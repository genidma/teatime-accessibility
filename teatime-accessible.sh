#!/bin/bash
# Change to the script's directory. This makes sure that relative paths inside
# the Python script (like for sound files or icons) work correctly, no matter
# where the user runs the launcher from.

# Handle symlinks - get the real directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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

# Attempt to locate the AT-SPI bus address from the running dbus-daemon
# This fixes "Could not obtain desktop path or name" warnings by ensuring the app finds the accessibility bus
AT_SPI_BUS_ADDRESS=$(ps -ef | grep "at-spi/bus" | grep -v grep | grep -o "unix:path=[^ ]*" | head -n 1)

if [ -n "$AT_SPI_BUS_ADDRESS" ]; then
    export AT_SPI_BUS_ADDRESS
    
    # If DBUS_SESSION_BUS_ADDRESS is missing, use the AT-SPI bus as a fallback.
    # This ensures the app has *some* bus to talk to if launched in a restricted environment.
    if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
        export DBUS_SESSION_BUS_ADDRESS="$AT_SPI_BUS_ADDRESS"
    fi
    
    # Ensure the ATK bridge is loaded
    if [[ "$GTK_MODULES" != *"atk-bridge"* ]]; then
        export GTK_MODULES="${GTK_MODULES:+$GTK_MODULES:}gail:atk-bridge"
    fi
    
    # Ensure XDG_DATA_DIRS includes standard paths so the registry service can be found
    if [[ "$XDG_DATA_DIRS" != *"/usr/share"* ]]; then
        export XDG_DATA_DIRS="${XDG_DATA_DIRS:+$XDG_DATA_DIRS:}/usr/share:/usr/local/share"
    fi
fi

# Run the application, filtering out known noisy/harmless AT-SPI warnings from stderr
# We do not disable the bridge (NO_AT_BRIDGE is NOT set), so accessibility features remain active.
# We just clean up the terminal output for a better user experience.
python3 bin/teatime.py "$@" 2> >(grep -v -E "AT-SPI: Could not obtain desktop path|atk-bridge: get_device_events_reply|atk-bridge: GetRegisteredEvents" >&2)