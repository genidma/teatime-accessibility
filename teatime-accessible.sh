#!/bin/bash
# Change to the script's directory. This makes sure that relative paths inside
# the Python script (like for sound files or icons) work correctly, no matter
# where the user runs the launcher from.
cd "$(dirname "$0")"
# Activate the virtual environment if it exists
if [ -f "teatime-venv/bin/activate" ]; then
    source teatime-venv/bin/activate
else
    echo "Virtual environment not found. Using system Python."
fi
# Execute the Python script. "$@" passes along any command-line arguments
# from the launcher to the Python application.
python3 bin/teatime.py "$@"