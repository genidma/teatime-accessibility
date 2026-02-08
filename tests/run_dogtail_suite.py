#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

DEFAULT_ESTIMATE_SEC = 15.0
LOCK_FILENAME = "dogtail_run.lock"


def lock_path(report_dir):
    return os.path.join(report_dir, LOCK_FILENAME)


def pid_is_running(pid):
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def check_active_lock(report_dir):
    path = lock_path(report_dir)
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return False
    pid = int(data.get("pid", 0))
    if pid and pid != os.getpid() and pid_is_running(pid):
        return True
    return False


def write_lock(report_dir):
    path = lock_path(report_dir)
    payload = {
        "pid": os.getpid(),
        "start_utc": datetime.datetime.utcnow().isoformat() + "Z",
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def remove_lock(report_dir):
    path = lock_path(report_dir)
    if os.path.exists(path):
        os.remove(path)


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if "groups" not in manifest or not isinstance(manifest["groups"], dict):
        raise ValueError("manifest must include a 'groups' object")
    return manifest


def list_tests(manifest, groups):
    if not groups:
        groups = list(manifest["groups"].keys())
    tests = []
    missing = []
    for group in groups:
        if group not in manifest["groups"]:
            missing.append(group)
            continue
        tests.extend(manifest["groups"][group])
    if missing:
        raise ValueError(f"unknown group(s): {', '.join(missing)}")
    # Preserve order while de-duplicating
    seen = set()
    ordered = []
    for test_id in tests:
        if test_id not in seen:
            seen.add(test_id)
            ordered.append(test_id)
    return ordered


def load_history(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return []


def durations_from_history(history):
    durations = {}
    for entry in history:
        for test in entry.get("tests", []):
            test_id = test.get("id")
            duration = test.get("duration_sec")
            if test_id and isinstance(duration, (int, float)):
                durations[test_id] = float(duration)
    return durations


def estimate_total(test_ids, durations):
    return sum(durations.get(test_id, DEFAULT_ESTIMATE_SEC) for test_id in test_ids)


def get_machine_profile():
    cpu_count = os.cpu_count() or 1
    load1 = None
    load5 = None
    load15 = None
    if hasattr(os, "getloadavg"):
        load1, load5, load15 = os.getloadavg()
    mem_total_kb = None
    mem_available_kb = None
    meminfo = "/proc/meminfo"
    if os.path.exists(meminfo):
        with open(meminfo, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    mem_total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_available_kb = int(line.split()[1])
    return {
        "cpu_count": cpu_count,
        "loadavg_1": load1,
        "loadavg_5": load5,
        "loadavg_15": load15,
        "mem_total_kb": mem_total_kb,
        "mem_available_kb": mem_available_kb,
    }


def recommend_max_procs(profile):
    cpu_count = profile.get("cpu_count") or 1
    baseline = max(1, cpu_count // 2)
    load1 = profile.get("loadavg_1")
    if load1 is not None and load1 > cpu_count * 0.7:
        baseline = max(1, baseline - 1)
    return baseline


def nodeid_to_junit_class(nodeid):
    parts = nodeid.split("::")
    if len(parts) < 2:
        return None
    path = parts[0]
    class_name = parts[1]
    module = path.replace("/", ".").replace("\\", ".")
    if module.endswith(".py"):
        module = module[:-3]
    return f"{module}.{class_name}"


def junit_class_to_nodeid(classname):
    if not classname:
        return None
    parts = classname.split(".")
    if len(parts) < 2:
        return None
    class_name = parts[-1]
    module = ".".join(parts[:-1])
    path = module.replace(".", "/") + ".py"
    return f"{path}::{class_name}"


def parse_junit_files(paths):
    totals = {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}
    results = []

    for path in paths:
        if not os.path.exists(path):
            continue
        tree = ET.parse(path)
        root = tree.getroot()
        suites = []
        if root.tag == "testsuite":
            suites = [root]
        else:
            suites = root.findall("testsuite")

        for suite in suites:
            for case in suite.findall("testcase"):
                classname = case.attrib.get("classname", "")
                name = case.attrib.get("name", "")
                duration = float(case.attrib.get("time", "0") or 0)

                status = "passed"
                message = None
                if case.find("failure") is not None:
                    status = "failed"
                    message = case.find("failure").attrib.get("message")
                elif case.find("error") is not None:
                    status = "error"
                    message = case.find("error").attrib.get("message")
                elif case.find("skipped") is not None:
                    status = "skipped"
                    message = case.find("skipped").attrib.get("message")

                base = junit_class_to_nodeid(classname)
                test_id = f"{base}::{name}" if base else f"{classname}::{name}"

                totals["total"] += 1
                totals[status] += 1
                results.append(
                    {
                        "id": test_id,
                        "status": status,
                        "duration_sec": duration,
                        "message": message,
                    }
                )

    return totals, results


def build_shards(test_ids, durations, shard_count):
    shard_count = max(1, shard_count)
    shards = [[] for _ in range(shard_count)]
    weights = [0.0 for _ in range(shard_count)]
    ordered = sorted(test_ids, key=lambda t: durations.get(t, DEFAULT_ESTIMATE_SEC), reverse=True)
    for test_id in ordered:
        idx = weights.index(min(weights))
        shards[idx].append(test_id)
        weights[idx] += durations.get(test_id, DEFAULT_ESTIMATE_SEC)
    return [shard for shard in shards if shard]


def build_pytest_command(test_ids, report_base, html_enabled):
    cmd = ["pytest"] + test_ids + ["-v", f"--junitxml={report_base}.xml"]
    if html_enabled:
        cmd += [f"--html={report_base}.html", "--self-contained-html"]
    dbus = shutil.which("dbus-run-session")
    if dbus:
        cmd = [dbus, "--"] + cmd
    return cmd


def detect_active_pytest(repo_root):
    if os.name != "posix":
        return False
    try:
        output = subprocess.check_output(["ps", "-aef"], text=True)
    except Exception:
        return False
    for line in output.splitlines():
        if "pytest" in line and "tests/test_ui_dogtail.py" in line and repo_root in line:
            return True
    return False


def find_stale_processes(repo_root):
    if os.name != "posix":
        return []
    try:
        output = subprocess.check_output(["ps", "-aef"], text=True)
    except Exception:
        return []
    candidates = []
    for line in output.splitlines():
        if repo_root not in line:
            continue
        if "python3 bin/teatime.py" in line or "teatime-accessible.sh" in line:
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                pid = int(parts[1])
            except ValueError:
                continue
            candidates.append((pid, line.strip()))
    return candidates


def cleanup_processes(repo_root, dry_run):
    if detect_active_pytest(repo_root):
        print("Active pytest run detected. Skipping cleanup.")
        return
    candidates = find_stale_processes(repo_root)
    if not candidates:
        print("No stale TeaTime app instances found.")
        return
    for pid, cmdline in candidates:
        if dry_run:
            print(f"DRY RUN: would terminate pid={pid} cmd={cmdline}")
            continue
        try:
            os.kill(pid, 15)
            print(f"Terminated pid={pid} cmd={cmdline}")
        except OSError as exc:
            print(f"Failed to terminate pid={pid}: {exc}")


def run_shards(shards, report_dir, nice_level, stagger_seconds, html_enabled):
    procs = []
    results = []

    for idx, shard in enumerate(shards, start=1):
        report_base = os.path.join(report_dir, f"dogtail_report_shard{idx}")
        cmd = build_pytest_command(shard, report_base, html_enabled)

        def preexec():
            if hasattr(os, "nice"):
                os.nice(nice_level)

        popen_kwargs = {
            "env": os.environ.copy(),
        }
        if os.name == "posix" and nice_level != 0:
            popen_kwargs["preexec_fn"] = preexec

        proc = subprocess.Popen(cmd, **popen_kwargs)
        procs.append((proc, report_base + ".xml"))

        if stagger_seconds > 0:
            time.sleep(stagger_seconds)

    for proc, junit_path in procs:
        exit_code = proc.wait()
        results.append((exit_code, junit_path))

    return results


def main():
    parser = argparse.ArgumentParser(description="Run Dogtail UI tests with dashboard updates.")
    parser.add_argument("--manifest", default="tests/ui_test_manifest.json")
    parser.add_argument("--group", action="append", dest="groups")
    parser.add_argument("--estimate", action="store_true")
    parser.add_argument("--profile-machine", action="store_true")
    parser.add_argument("--max-procs", type=int, default=1)
    parser.add_argument("--stagger-seconds", type=float, default=0.0)
    parser.add_argument("--nice", type=int, default=0)
    parser.add_argument("--no-dashboard", action="store_true")
    parser.add_argument("--clean", action="store_true", help="Terminate stale TeaTime app instances before running.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without running tests.")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_root)

    report_dir = os.path.join("tests", "reports")
    os.makedirs(report_dir, exist_ok=True)

    manifest = load_manifest(args.manifest)
    history_path = os.path.join(report_dir, "dogtail_history.json")
    history = load_history(history_path)
    durations = durations_from_history(history)

    test_ids = list_tests(manifest, args.groups)

    if args.profile_machine:
        profile = get_machine_profile()
        recommended = recommend_max_procs(profile)
        print(json.dumps({"profile": profile, "recommended_max_procs": recommended}, indent=2))

    if args.estimate:
        total = estimate_total(test_ids, durations)
        print(f"Estimated run time for {len(test_ids)} tests: {int(total)}s")
        return 0

    if args.max_procs < 1:
        raise ValueError("--max-procs must be >= 1")

    if check_active_lock(report_dir):
        print("Another Dogtail test run is already active (lock file present). Exiting.")
        return 1

    if args.clean:
        cleanup_processes(repo_root, args.dry_run)

    if args.dry_run:
        print("DRY RUN: no tests will be executed.")
        print(f"Selected tests: {len(test_ids)}")
        return 0

    html_enabled = args.max_procs == 1

    shards = build_shards(test_ids, durations, args.max_procs)
    if args.max_procs > 1:
        print("WARNING: Parallel Dogtail runs can conflict unless each shard has its own display session.")

    env = os.environ.copy()
    env["XDG_SESSION_TYPE"] = "x11"
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + os.pathsep + os.path.join(repo_root, "bin")
    os.environ.update(env)

    write_lock(report_dir)
    try:
        results = run_shards(shards, report_dir, args.nice, args.stagger_seconds, html_enabled)
    finally:
        remove_lock(report_dir)
    junit_paths = [path for _, path in results if os.path.exists(path)]

    exit_code = 0 if all(code == 0 for code, _ in results) else 1

    if not args.no_dashboard:
        totals, tests = parse_junit_files(junit_paths)
        profile = get_machine_profile()
        run_entry = {
            "run_id": datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
            "totals": totals,
            "tests": tests,
            "machine": profile,
            "params": {
                "groups": args.groups or list(manifest["groups"].keys()),
                "max_procs": args.max_procs,
                "stagger_seconds": args.stagger_seconds,
                "nice": args.nice,
                "clean": args.clean,
            },
        }
        dashboard_path = os.path.join(report_dir, "dogtail_dashboard.json")
        with open(dashboard_path, "w", encoding="utf-8") as handle:
            json.dump(run_entry, handle, indent=2)

        history.append(run_entry)
        with open(history_path, "w", encoding="utf-8") as handle:
            json.dump(history, handle, indent=2)

        print(f"Dashboard updated at {dashboard_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
