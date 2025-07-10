#!/bin/bash
#
# uninstall.sh - Uninstallation script for Accessible Tea Timer
#
# This script removes the components installed by setup.sh.
# In order to make this script executable, please run the command directly below in your terminal (without the ## pound signs)
## chmod +x uninstall.sh


# Exit immediately if a command exits with a non-zero status.
set -e

echo "Uninstalling Accessible Tea Timer..."

# --- Sanity Check ---
# Ensure the script is run from the project's root directory.
if [ ! -f "bin/teatime.py" ]; then
    echo "Error: Please run this script from the teatime-accessibility directory"
    exit 1
fi

# --- Remove Desktop Shortcut ---
DESKTOP_FILE="$HOME/.local/share/applications/teatime-accessible.desktop"
if [ -f "${DESKTOP_FILE}" ]; then
    echo "Removing desktop shortcut: ${DESKTOP_FILE}"
    rm -f "${DESKTOP_FILE}"
    # Update the desktop database to reflect the change immediately
    echo "Updating desktop database..."
    update-desktop-database -q "$HOME/.local/share/applications"
fi

# --- Remove Launcher Script ---
LAUNCHER_SCRIPT="teatime-accessible"
if [ -f "${LAUNCHER_SCRIPT}" ]; then
    echo "Removing launcher script: ${LAUNCHER_SCRIPT}"
    rm -f "${LAUNCHER_SCRIPT}"
fi

# --- Ask to Remove Optional Components ---
echo ""
read -p "Do you want to remove the Python virtual environment (teatime-venv)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing virtual environment..."
    rm -rf "teatime-venv"
fi

read -p "Do you want to remove user configuration and statistics files? (This cannot be undone) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing user data..."
    rm -f "$HOME/.config/teatime_config.json"
    rm -f "$HOME/.local/share/teatime_stats.json"
fi

echo ""
echo "Uninstallation complete."