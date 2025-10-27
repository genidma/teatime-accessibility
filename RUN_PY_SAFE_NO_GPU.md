# Run the Python script safely and avoid launching a GPU-enabled browser

This document explains how to run the repository's text-based issue prioritization and how to safely generate/view the interactive Gantt chart without triggering GPU-accelerated browser rendering that may crash some systems.

WARNING: Do NOT open the generated `teatime-gantt-chart.html` directly via `file://` in a browser that uses GPU acceleration on systems with unstable drivers. Use the safe commands below instead.

----------------------------------------
SECTION A — Run the text-based prioritization (no browser)
----------------------------------------

These commands run the script and only produce the text-based prioritization output (no browser auto-open):

Recommended (use the virtualenv Python directly):

```bash
/vms_and_github/Github/teatime-accessibility/teatime-venv/bin/python3 bin/teatime-tasks-priority-test.py
```

Or activate the venv first, then run:

```bash
source teatime-venv/bin/activate
python3 bin/teatime-tasks-priority-test.py
```

Notes:
- Do NOT set `OPEN_GANTT=1` if you don't want the script to attempt an auto-open in a browser.
- The script writes text output to `teatime-tasks-output.txt` in the repository root. View it with `cat` or `less`:

```bash
cat teatime-tasks-output.txt
less teatime-tasks-output.txt
```

To show only the "Recommended Task Order" section:

```bash
sed -n '/=== RECOMMENDED TASK ORDER ===/,/$/p' teatime-tasks-output.txt
```

----------------------------------------
SECTION B — Safe Gantt generation and viewing (optional)
----------------------------------------

The script can generate a Gantt chart based on the live issues (priority-based). Use the safe server + browser flags below to view it interactively with GPU disabled.

Generate the Gantt and attempt an auto-open (the script will copy the file to `/tmp/tt-gantt/` and start a tiny HTTP server):

```bash
# use venv python so pandas/plotly are available; this will generate the chart
OPEN_GANTT=1 BROWSER_NAME=chromium OPEN_GANTT_SERVER=1 /vms_and_github/Github/teatime-accessibility/teatime-venv/bin/python3 -u bin/teatime-tasks-priority-test.py
```

By default, the Gantt generation will show a limited initial set of tasks to avoid overwhelming the chart. To show all tasks in the Gantt, set:

```bash
export OPEN_GANTT_ALL=1
# then re-run the same OPEN_GANTT=1 command above
```

Manual safe view options (if you prefer manual control):

1) Start a local HTTP server and open the Gantt in Chromium with GPU disabled:

```bash
# from the repository root
python3 -m http.server --directory /vms_and_github/Github/teatime-accessibility 8000

# then launch Chromium with GPU-disabled flags (adjust path as needed):
/snap/bin/chromium \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-accelerated-2d-canvas \
  --disable-accelerated-video-decode \
  --disable-gpu-compositing \
  --user-data-dir=/tmp/tt-gantt-userdata \
  --no-first-run \
  --no-default-browser-check \
  "http://127.0.0.1:8000/teatime-gantt-chart.html" &
```

2) Headless screenshot (no GUI):

```bash
/snap/bin/chromium \
  --headless=new \
  --disable-gpu \
  --screenshot=/tmp/teatime-gantt-screenshot.png \
  --window-size=1280,800 \
  "http://127.0.0.1:8000/teatime-gantt-chart.html"
```

3) Force software GL if GPU drivers are problematic:

```bash
export LIBGL_ALWAYS_SOFTWARE=1
/snap/bin/chromium --disable-gpu --user-data-dir=/tmp/tt-gantt-userdata "http://127.0.0.1:8000/teatime-gantt-chart.html" &
```

4) Use a virtual X server (isolated display):

```bash
xvfb-run -s "-screen 0 1280x800x24" /snap/bin/chromium --disable-gpu "http://127.0.0.1:8000/teatime-gantt-chart.html" &
```

Viewing logs and stopping processes

- `/tmp/tt-gantt-debug.log` — script debug trace
- `/tmp/tt-gantt-chromium.log` — Chromium stdout/stderr

Tail logs:

```bash
tail -n 200 -f /tmp/tt-gantt-debug.log
tail -n 200 -f /tmp/tt-gantt-chromium.log
```

Kill processes (replace PID with the actual PID):

```bash
kill <CHROMIUM_PID>
kill <HTTP_SERVER_PID>
```

----------------------------------------
ENV vars used by the script
----------------------------------------

- `OPEN_GANTT=1` — enable auto-open behavior
- `BROWSER_NAME=chromium` — prefer Chromium and trigger GPU-disable flags
- `OPEN_GANTT_SERVER=1` — force the script to start an HTTP server fallback
- `OPEN_GANTT_ALL=1` — show all tasks in the generated Gantt (default limits are applied otherwise)
- `ALLOW_NO_SANDBOX=1` — will add `--no-sandbox` (use only if you understand the security implications)

----------------------------------------
Where this file lives
----------------------------------------

`RUN_PY_SAFE_NO_GPU.md` — repository root

Open this file in a text editor to copy any commands.

Last updated: 2025-10-27
