# Dogtail UI Testing Documentation

This document describes the setup and execution of automated GUI tests for the TeaTime Accessibility application using Dogtail.

Reference: Issue #60

## Overview

Automated GUI tests are implemented using Dogtail to ensure the accessibility and functionality of the TeaTime Accessibility user interface. These tests verify that the application windows and controls are correctly registered with AT-SPI and behave as expected.

## Test Suite: `tests/test_ui_dogtail.py`

The test suite includes the following checks:
- **Main Window Presence**: Verifies the application window is correctly identified.
- **UI Control Detection**: Ensures "Start" and "Stop" buttons are visible and interactable.
- **Timer Functionality**: Verifies that clicking "Start" initiates the timer (changing button sensitivity) and "Stop" terminates it correctly.

## Practical Implementation Details

The tests use a robust search method to locate the application node in AT-SPI, typically searching for names like `teatime.py` or variant strings containing `teatime` to ensure compatibility across different launch environments.

## Dependencies

### Python Dependencies
- `dogtail`: The primary GUI testing framework.
- `pyatspi`: (Internal dependency of Dogtail)

### System Dependencies
- `python3-pyatspi`: Required for Dogtail to interact with the GTK application via AT-SPI.

To install the system dependency on Debian-based systems:
```bash
sudo apt update && sudo apt install -y python3-pyatspi
```

## How to Run Tests

To run the Dogtail tests, ensure you are in the project root and execute the following commands:

```bash
# Activate the virtual environment
source teatime-venv/bin/activate

# Force X11 session type (recommended for stability with Dogtail)
export XDG_SESSION_TYPE=x11

# Run the tests within a DBus session
dbus-run-session -- python3 tests/test_ui_dogtail.py
```

> [!NOTE]
> Forcing `XDG_SESSION_TYPE=x11` is currently the most stable way to run these tests, even on Wayland-based systems.
