#!/bin/bash

# run_dogtail_tests.sh
# This script runs the comprehensive Dogtail UI tests and generates a report.

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Set up environment
export XDG_SESSION_TYPE=x11
export PYTHONPATH=$PYTHONPATH:$(pwd)/bin

# Create report directory if it doesn't exist
mkdir -p tests/reports

# Run tests with pytest
# -v: verbose
# --html: generate HTML report
# --self-contained-html: embed CSS into the HTML file
echo "Starting Dogtail UI Tests..."
source teatime-venv/bin/activate
dbus-run-session -- pytest tests/test_ui_dogtail.py -v --html=tests/reports/dogtail_report.html --self-contained-html

# Check exit status
if [ $? -eq 0 ]; then
    echo "------------------------------------------------"
    echo "TESTS PASSED"
    echo "------------------------------------------------"
else
    echo "------------------------------------------------"
    echo "TESTS FAILED (see report at tests/reports/dogtail_report.html)"
    echo "------------------------------------------------"
fi

echo "Summary report generated at tests/reports/dogtail_report.html"
