#!/bin/bash

# Setup script for TeaTime Accessibility
# This script creates a virtual environment and installs required dependencies

set -e  # Exit on any error

echo "TeaTime Accessibility Setup Script"
echo "=================================="

# Check if we're in the project directory
if [ ! -f "teatime-accessible.sh" ]; then
    echo "Error: This script must be run from the project root directory"
    echo "Please navigate to the teatime-accessibility directory and try again"
    exit 1
fi

# Define virtual environment directory
VENV_DIR="teatime-venv"

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists: $VENV_DIR"
    echo "Skipping virtual environment creation..."
else
    echo "Creating virtual environment..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Create virtual environment
    if python3 -m venv --help &> /dev/null; then
        python3 -m venv "$VENV_DIR"
        echo "Virtual environment created successfully"
    else
        echo "Error: venv module is not available"
        echo "Please install python3-venv package:"
        echo "  sudo apt install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install system dependencies message
echo ""
echo "Before installing Python packages, you may need to install system dependencies."
echo "Run the following command if you encounter installation errors:"
echo "  sudo apt install python3-dev libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-venv gir1.2-gtk-3.0"
echo ""

# Ask user if they want to install system dependencies
read -p "Do you want to install system dependencies now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing system dependencies..."
    sudo apt install python3-dev libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-venv gir1.2-gtk-3.0
fi

# Install required packages
if [ -f "requirements.txt" ]; then
    echo "Installing required packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found, installing PyGObject directly..."
    pip install PyGObject
fi

# Check if required packages are installed
echo "Verifying installation..."
if python3 -c "import gi; print('PyGObject is installed')" &> /dev/null; then
    echo "PyGObject installation verified"
else
    echo "Warning: PyGObject verification failed"
    echo "You might need to install system dependencies:"
    echo "  sudo apt install python3-dev libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-venv gir1.2-gtk-3.0"
fi

# Create/update desktop entry
echo "Creating desktop entry..."
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/teatime-accessibility.desktop" << EOF
[Desktop Entry]
Name=TeaTime Accessibility
Comment=Accessible tea timer with rainbow glow feature
Exec=$PWD/teatime-accessible.sh
Icon=accessories-clock
Terminal=false
Type=Application
Categories=Utility;Accessibility;
Keywords=timer;accessibility;tea;
EOF

echo "Desktop entry created at $DESKTOP_DIR/teatime-accessibility.desktop"

# Make the launcher script executable
chmod +x teatime-accessible.sh

echo ""
echo "Setup completed successfully!"
echo "=================================="
echo "You can now run the application using:"
echo "  ./teatime-accessible.sh"
echo ""
echo "Or launch it from your applications menu as 'TeaTime Accessibility'"
echo ""
echo "To manually activate the virtual environment in the future, run:"
echo "  source $VENV_DIR/bin/activate"