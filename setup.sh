#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Setting up Accessible Tea Timer..."

# Check if we're in the right directory
if [ ! -f "bin/teatime.py" ]; then
    echo "Error: Please run this script from the teatime-accessibility directory"
    exit 1
fi

# --- Create Python Virtual Environment and Install Dependencies ---
# We use --system-site-packages to give the venv access to the system-installed
# PyGObject (which provides the 'gi' module).
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment in 'venv/'..."
    python3 -m venv --system-site-packages venv
fi

echo "Activating virtual environment and installing 'playsound'..."
source venv/bin/activate

# Install playsound for audio notifications
pip install playsound

# Deactivate after installation
deactivate

echo "Dependencies set up."

# --- Create Launcher Script ---
# This script will activate the venv and run the python app
LAUNCHER_SCRIPT="teatime-accessible"
echo "Creating launcher script: ${LAUNCHER_SCRIPT}"

# Use a 'here document' to write the script content to the file
cat > "${LAUNCHER_SCRIPT}" << 'EOF'
#!/bin/bash
# Change to the script's directory to ensure relative paths work
cd "$(dirname "$0")"
# Activate the virtual environment
source venv/bin/activate
# Run the Python application, passing along any command-line arguments
python3 bin/teatime.py "$@"
EOF

# Make the launcher script executable
chmod +x "${LAUNCHER_SCRIPT}"
echo "Launcher script created and made executable."

# --- Create Desktop Shortcut ---
# This .desktop file allows the app to appear in application menus
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "${DESKTOP_DIR}"
DESKTOP_FILE="${DESKTOP_DIR}/teatime-accessible.desktop"
APP_PATH="$(pwd)" # Get the absolute path to the project directory

echo "Creating desktop shortcut: ${DESKTOP_FILE}"

# Use a 'here document' to write the .desktop file content
cat > "${DESKTOP_FILE}" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Accessible Tea Timer
Comment=A tea timer with accessibility features
# The Exec path must be absolute and should point to our launcher
Exec=${APP_PATH}/${LAUNCHER_SCRIPT}
Icon=preferences-system-time
Terminal=false
Categories=Utility;
StartupNotify=true
Path=${APP_PATH}
EOF

echo ""
echo "Setup complete!"
echo "You can now run the application using:"
echo "  ./${LAUNCHER_SCRIPT}"
echo "Or find 'Accessible Tea Timer' in your application menu (you may need to log out and back in)."
