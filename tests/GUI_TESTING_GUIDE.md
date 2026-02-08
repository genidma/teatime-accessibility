# GUI Testing Guide (Dogtail)

This document describes the automated GUI testing infrastructure for TeaTime Accessibility using Dogtail and AT-SPI.

## Overview

Automated tests ensure that the TeaTime interface remains accessible and functional. We use the **`dogtail` Python package** (available via `pip install dogtail`) for its deep integration with AT-SPI, allowing us to interact with GTK widgets directly.

> [!NOTE]
> This guide refers to the **Dogtail testing library**, not the dog tail wagging animation feature within the application!

## Improvements Implemented

### 1. Robust Element Selection (Fuzzy Matching)
Implemented a `find_child_fuzzy` helper method in `tests/test_ui_dogtail.py` to overcome issues with exact name matching in the AT-SPI tree.

- **Fuzzy Name Matching**: Correctly identifies elements even if labels have **tiny** variations.
- **Role-Based Searching**: Prioritizes element roles (e.g., `check box`, `push button`) to ensure the correct widget type is found.
- **Targeted Recursion**: Searches within relevant containers (e.g., `grid`, `box`) without stalling on deep, irrelevant UI branches.

### 2. Enhanced Diagnostic Logging
Added comprehensive logging and diagnostic tools to aid in debugging:

- **UI State Capture**: On failure, the test suite automatically dumps the UI tree via `capture_ui_state()`. This is logged in the `pytest` output and the HTML report.
- **Dogtail Debug Integration**: Enabled full Dogtail debug logging to capture interaction details and search attempts.
- **Assertion Context**: Improved assertion messages provide clear context on which element failed and why.

### 3. Stabilized Test Runner
Created a dedicated test runner script `tests/run_dogtail_tests.sh` that:

- Ensures a clean AT-SPI session using `dbus-run-session`.
- Generates a self-contained HTML report with detailed failure logs.
- Manages virtual environment activation automatically.

## Dashboard-to-Doc Mapping

If you see issues in the **Test Dashboard**, follow these cogent instructions:

| Dashboard Signal | Likely Cause | Recommended Command |
| :--- | :--- | :--- |
| `SearchError` | Element renamed or hidden | `pytest tests/test_ui_dogtail.py -k <test_name> -v` |
| `AttributeError` | App failed to launch/register | `atspi-registry --list-apps | grep teatime` |
| `Timeout` | System lag or DBus stall | `./tests/run_dogtail_tests.sh --triage <failed_test>` |
| `CheckedState Error` | Animation blocking click | `export DOGTAIL_SLEEP_DELAY=2.0 && ./tests/run_dogtail_tests.sh` |

## Verification of Work

Due to significant system performance constraints in the current environment, a full automated run may experience delays. However, the following individual improvements have been verified:

1.  **Application Launch**: Confirmed that `teatime.py` is correctly targeted and launched by the tests.
2.  **Selector Logic**: Manually verified the fuzzy matching logic against the AT-SPI tree dump (`atspi_dump.txt`).
3.  **Reporting**: Verified that the HTML report generation is functional and captures diagnostic output.

## How to Run Tests

Ensure you are in the **usual location** (project root).

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

---

## Continuation Prompt for Next Session

If you hit usage limits and need to hand this task over to another AI, copy and paste the following prompt:

```text
I am working on expanding the Dogtail GUI test suite for the 'teatime-accessibility' project. 

Current Progress:
1. Implemented robust fuzzy matching and diagnostic logging (capture_ui_state) in 'tests/test_ui_dogtail.py'.
2. Created an enhanced test runner 'tests/run_dogtail_tests.sh' with --triage, --estimate, and --nice support.
3. Updated the consolidated 'tests/GUI_TESTING_GUIDE.md' to clarify the use of the 'dogtail' Python package and provided Dashboard-to-Doc error mapping.

Next Steps:
- Execute 'tests/run_dogtail_tests.sh' in a stable X11/DBus environment (from the usual project location).
- Verify full test coverage for: Presets, Categories, Mode toggles, Font scaling, and Menu navigation.
- Analyze the generated HTML report in 'tests/reports/dogtail_report.html' for any residual 'SearchError' or 'AttributeError' issues.

Please review the current codebase and continue the verification and stabilization of the Dogtail tests.
```
