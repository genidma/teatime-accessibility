#!/bin/bash
#
# setup.sh - Installation and setup script for Accessible Tea Timer
#
# This script automates the setup process by:
# 1. Initializing a Git repository if one doesn't exist.
# 2. Creating a Python virtual environment with access to system GTK libraries.
# 3. Installing the necessary Python dependencies (`playsound`).
# 4. Creating a robust launcher script (`teatime-accessible`).
# 5. Creating a standard Linux desktop shortcut (`.desktop` file).
#

# Exit immediately if a command exits with a non-zero status.
# This ensures that the script will stop if any step fails.
set -e

echo "Setting up Accessible Tea Timer..."

# --- Sanity Check ---
# Ensure the script is run from the project's root directory by checking for a key file.
if [ ! -f "bin/teatime.py" ]; then
    echo "Error: Please run this script from the teatime-accessibility directory"
    exit 1
fi

# --- Initialize Git Repository (if not already initialized) ---
# This makes it easy to start tracking changes right after setup.
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit of Accessible Tea Timer project"
    echo "Git repository initialized and initial commit created."
else
    echo "Git repository already exists. Skipping initialization."
fi

# --- Create Python Virtual Environment and Install Dependencies ---
# We check for an existing 'venv' directory to avoid re-creating it on subsequent runs.
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment in 'venv/'..."
    # The --system-site-packages flag is crucial. It allows the virtual environment
    # to access system-level libraries like PyGObject (for GTK), which are
    # best managed by the system's package manager (apt, dnf, etc.).
    python3 -m venv --system-site-packages venv
fi

echo "Activating virtual environment..."
# We must activate the environment to ensure 'pip' installs packages into it.
source venv/bin/activate

# Deactivate after installation
deactivate

echo "Virtual environment is set up."

# --- Create Launcher Script ---
# This script provides a simple, one-command way to run the application.
LAUNCHER_SCRIPT="teatime-accessible"
echo "Creating launcher script: ${LAUNCHER_SCRIPT}"

# A 'here document' (cat << 'EOF') is a reliable way to write multi-line
# text to a file. The quotes around 'EOF' prevent shell variable expansion.
cat > "${LAUNCHER_SCRIPT}" << 'EOF'
#!/bin/bash
# Change to the script's directory. This makes sure that relative paths inside
# the Python script (like for sound files or icons) work correctly, no matter
# where the user runs the launcher from.
cd "$(dirname "$0")"
# Activate the virtual environment
source venv/bin/activate
# Execute the Python script. "$@" passes along any command-line arguments
# from the launcher to the Python application.
python3 bin/teatime.py "$@"
EOF

# Make the launcher script executable
chmod +x "${LAUNCHER_SCRIPT}"
echo "Launcher script created and made executable."

# --- Create Desktop Shortcut ---
# This .desktop file allows the application to appear in the system's
# application menu (like GNOME Activities or the KDE Start Menu).
DESKTOP_DIR="$HOME/.local/share/applications"
# The -p flag ensures that the parent directories are created if they don't exist.
mkdir -p "${DESKTOP_DIR}"
DESKTOP_FILE="${DESKTOP_DIR}/teatime-accessible.desktop"
# We need the full, absolute path to the project for the .desktop file to work reliably.
APP_PATH="$(pwd)"

echo "Creating desktop shortcut: ${DESKTOP_FILE}"

# Write the contents of the .desktop file. Note that 'EOF' is *not* quoted
# here, which allows the shell to expand variables like ${APP_PATH}.
cat > "${DESKTOP_FILE}" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Accessible Tea Timer
Comment=A tea timer with accessibility features
# The 'Exec' path must be absolute and point to our launcher script.
Exec=${APP_PATH}/${LAUNCHER_SCRIPT}
Icon=preferences-system-time
Terminal=false
Categories=Utility;
StartupNotify=true
Path=${APP_PATH}
EOF

# --- Final Instructions ---
echo ""
echo "Setup complete!"
echo "You can now run the application using:"
echo "  ./${LAUNCHER_SCRIPT}"
echo "Or find 'Accessible Tea Timer' in your application menu (you may need to log out and back in)."
