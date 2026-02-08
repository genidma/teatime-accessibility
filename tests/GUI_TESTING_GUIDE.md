# GUI Testing Guide (Dogtail)

This document describes the automated GUI testing infrastructure for TeaTime Accessibility using Dogtail and AT-SPI.

## Overview

Automated tests ensure that the TeaTime interface remains accessible and functional. We use the **`dogtail` Python package** (available via `pip install dogtail`) for its deep integration with AT-SPI, allowing us to interact with GTK widgets directly.

> [!NOTE]
> This guide refers to the **Dogtail testing library**, not the dog tail wagging animation feature within the application!

## Dashboard-to-Doc Mapping

If you see issues in the **Test Dashboard**, follow these cogent instructions:

| Dashboard Signal | Likely Cause | Recommended Command |
| :--- | :--- | :--- |
| `SearchError` | Element renamed or hidden | `pytest tests/test_ui_dogtail.py -k <test_name> -v` |
| `AttributeError` | App failed to launch/register | `atspi-registry --list-apps | grep teatime` |
| `Timeout` | System lag or DBus stall | `./tests/run_dogtail_tests.sh --triage <failed_test>` |
| `CheckedState Error` | Animation blocking click | `export DOGTAIL_SLEEP_DELAY=2.0 && ./tests/run_dogtail_tests.sh` |

## Enhanced Features

### 1. Fuzzy Matching
Selectors now use `find_child_fuzzy` which handles partial name matches and role-based filtering, making tests resilient to minor label changes (e.g., "Start" vs "Start Timer").

### 2. UI State Capture
On failure, the test suite automatically dumps the UI tree via `capture_ui_state()`. This is logged in the `pytest` output and the HTML report.

## How to Run Tests

### Standard Run
```bash
./tests/run_dogtail_tests.sh
```

### Staggered/Triaged Run
To prioritize system resources or debug a specific area:
```bash
# Run only settings tests with lower priority
nice -n 19 ./tests/run_dogtail_tests.sh --triage settings
```

### Time Estimation
To estimate how long the full suite will take:
```bash
./tests/run_dogtail_tests.sh --estimate
```

## Logs
Detailed search logs are available at `/tmp/dogtail-$USER/logs/`.
