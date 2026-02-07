#!/usr/bin/env python3
"""Run a minimal set of tests based on changed files."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from fnmatch import fnmatch


def _git_diff_names(base: str, head: str):
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..{head}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr.strip())
        sys.exit(result.returncode)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _match_paths(paths, patterns):
    for p in paths:
        for pattern in patterns:
            if fnmatch(p, pattern):
                return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Run tests mapped to changed files.")
    parser.add_argument("--map", default="test_map.json", help="Path to test map JSON")
    parser.add_argument("--base", default="HEAD~1", help="Git base ref")
    parser.add_argument("--head", default="HEAD", help="Git head ref")
    parser.add_argument("--paths", nargs="*", help="Explicit file paths (skip git diff)")
    parser.add_argument("--dry-run", action="store_true", help="Print tests without running")
    args = parser.parse_args()

    map_path = Path(args.map)
    if not map_path.exists():
        print(f"Test map not found: {map_path}")
        return 2

    data = json.loads(map_path.read_text(encoding="utf-8"))
    rules = data.get("rules", [])
    default_tests = data.get("default_tests", [])
    test_command = data.get("test_command", ["python", "-m", "unittest"])

    paths = args.paths if args.paths else _git_diff_names(args.base, args.head)
    if not paths:
        print("No changed files detected.")
        return 0

    selected = []
    notes = []
    for rule in rules:
        rule_paths = rule.get("paths", [])
        if rule_paths and _match_paths(paths, rule_paths):
            selected.extend(rule.get("tests", []))
            note = rule.get("note")
            if note:
                notes.append(note)

    # De-duplicate while preserving order
    seen = set()
    selected = [t for t in selected if not (t in seen or seen.add(t))]

    if not selected:
        selected = list(default_tests)

    if notes:
        print("Matched rules:")
        for n in sorted(set(notes)):
            print(f"- {n}")

    if not selected:
        print("No tests to run (mapped rules and default_tests are empty).")
        return 0

    cmd = list(test_command) + selected
    print("Running:", " ".join(cmd))
    if args.dry_run:
        return 0

    proc = subprocess.run(cmd)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
