#!/bin/bash
# Change to the script's directory. This makes sure that relative paths inside
# the Python script (like for sound files or icons) work correctly, no matter
# where the user runs the launcher from.
cd "$(dirname "$0")"

# Function to check if we're in a virtual environment
is_venv_active() {
    [[ -n "$VIRTUAL_ENV" ]]
}

# Activate the virtual environment if it exists and is not already active
if [ -f "teatime-venv/bin/activate" ] && ! is_venv_active; then
    echo "Activating virtual environment..."
    source teatime-venv/bin/activate
    echo "Virtual environment activated"
elif is_venv_active; then
    echo "Virtual environment already active"
else
    echo "Virtual environment not found. Using system Python."
fi

# Execute the Python script. "$@" passes along any command-line arguments
# from the launcher to the Python application.
python3 bin/teatime.py "$@"