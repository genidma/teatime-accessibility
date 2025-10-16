#!/bin/bash

# Install script for TeaTime Accessibility
# This script creates a virtual environment and installs required dependencies

set -e  # Exit on any error

echo "TeaTime Accessibility Install Script"
echo "==================================="

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
        python3 -m venv "$VENV_DIR" --system-site-packages
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

# Try to install required packages
if [ -f "requirements.txt" ]; then
    echo "Installing required packages from requirements.txt..."
    if ! pip install -r requirements.txt; then
        echo "Failed to install packages from requirements.txt"
        echo "Trying alternative installation method..."
        
        # Try installing system-wide PyGObject and then creating a virtual environment that can access it
        echo "Installing PyGObject system-wide..."
        sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
        
        echo "Creating virtual environment with system site packages..."
        # Deactivate current venv
        deactivate 2>/dev/null || true
        
        # Remove existing venv
        rm -rf "$VENV_DIR"
        
        # Create new venv with access to system packages
        python3 -m venv "$VENV_DIR" --system-site-packages
        source "$VENV_DIR/bin/activate"
        
        echo "Virtual environment with system packages created"
    fi
else
    echo "No requirements.txt found, installing PyGObject directly..."
    if ! pip install PyGObject; then
        echo "Failed to install PyGObject"
        echo "Installing system-wide PyGObject..."
        sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
        
        echo "Creating virtual environment with system site packages..."
        # Deactivate current venv
        deactivate 2>/dev/null || true
        
        # Remove existing venv
        rm -rf "$VENV_DIR"
        
        # Create new venv with access to system packages
        python3 -m venv "$VENV_DIR" --system-site-packages
        source "$VENV_DIR/bin/activate"
        
        echo "Virtual environment with system packages created"
    fi
fi

# Check if required packages are installed
echo "Verifying installation..."
if python3 -c "import gi; print('PyGObject is installed')" &> /dev/null; then
    echo "PyGObject installation verified"
else
    echo "Warning: PyGObject verification failed"
    echo "You might need to install system dependencies:"
    echo "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
fi

# Create icons directory if it doesn't exist
ICONS_DIR="$HOME/.local/share/icons/hicolor/48x48/apps"
mkdir -p "$ICONS_DIR"

# Copy the custom icon to the appropriate location
ICON_FILE="assets/icon.png"
if [ -f "$ICON_FILE" ]; then
    echo "Installing custom application icon..."
    cp "$ICON_FILE" "$ICONS_DIR/teatime-accessibility.png"
    # Update icon cache
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    fi
else
    echo "Warning: Custom PNG icon file not found. Using system default."
fi

# Also install PNG version for better compatibility
ICON_PNG_FILE="assets/icon.png"
if [ -f "$ICON_PNG_FILE" ]; then
    ICON_SIZES=("16x16" "22x22" "24x24" "32x32" "48x48" "64x64" "128x128" "256x256")
    for size in "${ICON_SIZES[@]}"; do
        ICON_SIZE_DIR="$HOME/.local/share/icons/hicolor/$size/apps"
        mkdir -p "$ICON_SIZE_DIR"
        cp "$ICON_PNG_FILE" "$ICON_SIZE_DIR/teatime-accessibility.png"
    done
    
    # Update icon cache
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    fi
else
    echo "Warning: Custom PNG icon file not found."
fi

# Create/update desktop entry
echo "Creating desktop entry..."
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

# Create a custom desktop entry with a relative path
cat > "$DESKTOP_DIR/teatime-accessibility.desktop" << EOF
[Desktop Entry]
Name=TeaTime Accessibility
Comment=Accessible tea timer with rainbow glow feature
Exec=$PWD/teatime-accessible.sh
Icon=teatime-accessibility
Terminal=false
Type=Application
Categories=Utility;Accessibility;
Keywords=timer;accessibility;tea;
EOF

echo "Desktop entry created at $DESKTOP_DIR/teatime-accessibility.desktop"

# Ask user if they want to create a desktop shortcut
echo ""
read -p "Do you want to create a desktop shortcut? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating desktop shortcut..."
    DESKTOP_SHORTCUT_DIR="$HOME/Desktop"
    # Check if Desktop directory exists, if not try other common locations
    if [ ! -d "$DESKTOP_SHORTCUT_DIR" ]; then
        DESKTOP_SHORTCUT_DIR="$HOME/desktop"
        if [ ! -d "$DESKTOP_SHORTCUT_DIR" ]; then
            DESKTOP_SHORTCUT_DIR="$HOME/Área de Trabalho"  # Portuguese
            if [ ! -d "$DESKTOP_SHORTCUT_DIR" ]; then
                DESKTOP_SHORTCUT_DIR="$HOME/سطح المكتب"  # Arabic
                if [ ! -d "$DESKTOP_SHORTCUT_DIR" ]; then
                    DESKTOP_SHORTCUT_DIR="$HOME/デスクトップ"  # Japanese
                    if [ ! -d "$DESKTOP_SHORTCUT_DIR" ]; then
                        DESKTOP_SHORTCUT_DIR="$HOME/Рабочий стол"  # Russian
                        if [ ! -d "$DESKTOP_SHORTCUT_DIR" ]; then
                            # If no desktop directory found, create one
                            DESKTOP_SHORTCUT_DIR="$HOME/Desktop"
                            mkdir -p "$DESKTOP_SHORTCUT_DIR"
                        fi
                    fi
                fi
            fi
        fi
    fi
    
    # Create desktop shortcut by copying the desktop entry
    cp "$DESKTOP_DIR/teatime-accessibility.desktop" "$DESKTOP_SHORTCUT_DIR/"
    echo "Desktop shortcut created at $DESKTOP_SHORTCUT_DIR/teatime-accessibility.desktop"
    echo ""
    echo "NOTE: To launch the application from the desktop shortcut:"
    echo "  1. Navigate to your desktop"
    echo "  2. Right-click on the 'TeaTime Accessibility' icon"
    echo "  3. Select 'Allow Launching' from the context menu"
    echo "  4. Double-click the icon to launch the application"
fi

# Make the launcher script executable
chmod +x teatime-accessible.sh

echo ""
echo "Install completed successfully!"
echo "=================================="
echo ""
echo "You can now run the application in one of the following ways:"
echo ""
echo "Option 1 - From your applications menu:"
echo "  1. Open your applications menu"
echo "  2. Look for 'TeaTime Accessibility' under the 'Utilities' category"
echo "  3. Click on the application icon to launch it"
echo ""
echo "Option 2 - From the command line:"
echo "  1. Navigate to this project directory"
echo "  2. Run: source teatime-venv/bin/activate"
echo "  3. Run: ./teatime-accessible.sh"
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
echo "Option 3 - From your desktop:"
echo "  1. Navigate to your desktop"
echo "  2. Right-click on the 'TeaTime Accessibility' icon"
echo "  3. Select 'Allow Launching' from the context menu"
echo "  4. Double-click the icon to launch the application"
echo ""
fi
echo "Note: The virtual environment has been created in this directory and does not need to be"
echo "      recreated unless you run the uninstall script."