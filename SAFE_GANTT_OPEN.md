# Safe ways to open the generated Gantt chart

This document collects safe commands and options for viewing `teatime-gantt-chart.html` on systems where GPU acceleration or snap confinement may crash the browser. Follow the method that matches your goal.

Repository root (example):
`/vms_and_github/Github/teatime-accessibility`

Paths used by the test script:
- Tasks output: `teatime-tasks-output.txt`
- Gantt HTML: `teatime-gantt-chart.html`

If you used the script with env vars, you can generate and attempt an auto-open with:

```bash
# use the project's virtualenv python so plotly/pandas are available
OPEN_GANTT=1 BROWSER_NAME=chromium OPEN_GANTT_SERVER=1 /vms_and_github/Github/teatime-accessibility/teatime-venv/bin/python3 -u bin/teatime-tasks-priority-test.py
```

This will:
- Create `teatime-gantt-chart.html` in the repository root.
- Copy it to `/tmp/tt-gantt/gantt-chart.html` and start a tiny HTTP server.
- Launch Chromium with a set of GPU-disabling flags.

If you prefer to do things manually or want to run a safe open yourself, use one of the options below.

## 1) Start a local HTTP server (safe for file access)

Serving over HTTP avoids file:// edge cases (snap confinement and file access bugs). It does not by itself disable GPU — you still have to start the browser with GPU-disabled flags.

```bash
# from the repository root
python3 -m http.server --directory /vms_and_github/Github/teatime-accessibility 8000
# then open in a browser (see Chromium flags below):
http://127.0.0.1:8000/teatime-gantt-chart.html
```

## 2) Open with Chromium and disable GPU (visual, interactive)

This is the recommended visual (non-headless) option when you want to inspect interactivity but avoid GPU crashes. Adjust the chromium executable path if needed.

```bash
/snap/bin/chromium \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-accelerated-2d-canvas \
  --disable-accelerated-jpeg-decoding \
  --disable-accelerated-mjpeg-decode \
  --disable-accelerated-video-decode \
  --disable-gpu-compositing \
  --disable-dev-shm-usage \
  --user-data-dir=/tmp/tt-gantt-userdata \
  --no-first-run \
  --no-default-browser-check \
  "http://127.0.0.1:8000/teatime-gantt-chart.html" &
```

Notes:
- Replace `/snap/bin/chromium` with the path returned by `which chromium` or `shutil.which('chromium')`.
- The `--user-data-dir` flag keeps browser state separated from your normal profile.

## 3) Headless Chromium (no GUI)

If you do not need to interact with the chart visually, use headless mode to render or screenshot the page with minimal GPU involvement:

```bash
/snap/bin/chromium \
  --headless=new \
  --disable-gpu \
  --screenshot=/tmp/teatime-gantt-screenshot.png \
  --window-size=1280,800 \
  "http://127.0.0.1:8000/teatime-gantt-chart.html"
```

Headless may disable some interactive features, but it's useful for automation or CI.

## 4) Force software GL (useful when GPU drivers are buggy)

```bash
export LIBGL_ALWAYS_SOFTWARE=1
/snap/bin/chromium --disable-gpu --user-data-dir=/tmp/tt-gantt-userdata "http://127.0.0.1:8000/teatime-gantt-chart.html" &
```

## 5) Use xvfb-run to create a virtual X server (isolated display)

If you want a headful browser but isolated from your main display, run:

```bash
xvfb-run -s "-screen 0 1280x800x24" /snap/bin/chromium --disable-gpu "http://127.0.0.1:8000/teatime-gantt-chart.html" &
```

## Viewing logs and stopping the server/browser

The test script writes debug info to temporary files when it auto-opens:

- `/tmp/tt-gantt-debug.log`  — script debug trace
- `/tmp/tt-gantt-chromium.log` — Chromium stdout/stderr from the launched process

Tail logs:

```bash
tail -n 200 -f /tmp/tt-gantt-debug.log
tail -n 200 -f /tmp/tt-gantt-chromium.log
```

Kill processes (replace PID with the actual PID from the logs or `ps`):

```bash
kill <CHROMIUM_PID>
kill <HTTP_SERVER_PID>
```

## Script env vars (used by `bin/teatime-tasks-priority-test.py`)

- `OPEN_GANTT=1` — enable auto-open behavior
- `BROWSER_NAME=chromium` — prefer Chromium and trigger GPU-disable flags
- `OPEN_GANTT_SERVER=1` — force the script to start an HTTP server fallback
- `ALLOW_NO_SANDBOX=1` — will add `--no-sandbox` (use only if you understand the security implications)

## Where this file lives

When created by this change, the script will reference this file at:

`SAFE_GANTT_OPEN.md`

Open this file in a text editor to copy any commands (it's intentionally self-contained).

---
Last updated: 2025-10-27
