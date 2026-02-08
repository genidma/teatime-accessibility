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

# Default values
TRIAGE=""
ESTIMATE=false
PRIORITY=0

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --triage) TRIAGE="$2"; shift ;;
        --estimate) ESTIMATE=true ;;
        --nice) PRIORITY="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Estimation logic
if [ "$ESTIMATE" = true ]; then
    NUM_TESTS=$(grep -c "def test_" tests/test_ui_dogtail.py)
    # Estimate ~15s per test + 10s overhead
    TOTAL_ESTIMATE=$(($NUM_TESTS * 15 + 10))
    echo "Estimated run time for $NUM_TESTS tests: ${TOTAL_ESTIMATE}s"
    exit 0
fi

# Select tests to run
PYTEST_ARGS="tests/test_ui_dogtail.py -v --html=tests/reports/dogtail_report.html --self-contained-html"
if [ -n "$TRIAGE" ]; then
    PYTEST_ARGS="$PYTEST_ARGS -k $TRIAGE"
fi

echo "Running tests with priority $PRIORITY..."
source teatime-venv/bin/activate
nice -n $PRIORITY dbus-run-session -- pytest $PYTEST_ARGS

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
