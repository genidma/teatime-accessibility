#!/bin/bash

# Uninstall script for TeaTime Accessibility
# This script removes the desktop entry and optionally the virtual environment

echo "TeaTime Accessibility Uninstall Script"
echo "====================================="

# Check if we're in the project directory
if [ ! -f "teatime-accessible.sh" ]; then
    echo "Error: This script must be run from the project root directory"
    echo "Please navigate to the teatime-accessibility directory and try again"
    exit 1
fi

# Remove desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/teatime-accessibility.desktop"
if [ -f "$DESKTOP_ENTRY" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_ENTRY"
    echo "Desktop entry removed"
else
    echo "No desktop entry found"
fi

# Ask user if they want to remove the virtual environment
echo ""
echo "Do you want to remove the virtual environment? This will remove all installed packages."
echo "Note: Your configuration and statistics will be preserved."
echo ""
read -p "Remove virtual environment? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "teatime-venv" ]; then
        echo "Removing virtual environment..."
        rm -rf "teatime-venv"
        echo "Virtual environment removed"
    else
        echo "No virtual environment found"
    fi
else
    echo "Virtual environment preserved"
fi

echo ""
echo "Uninstall completed!"
echo "====================================="
echo "The following have been preserved:"
echo "  - Configuration: ~/.config/teatime_config.json"
echo "  - Statistics: ~/.local/share/teatime_stats.json"
echo ""
echo "To completely remove all data, manually delete these files:"
echo "  rm ~/.config/teatime_config.json"
echo "  rm ~/.local/share/teatime_stats.json"