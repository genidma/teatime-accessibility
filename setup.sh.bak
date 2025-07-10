#!/bin/bash

# Setup script for Accessible Tea Timer
# This script sets up the improved tea timer with accessibility features

set -e

echo "Setting up Accessible Tea Timer..."

# Check if we're in the right directory
if [ ! -f "src/teatime.py" ]; then
    echo "Error: Please run this script from the teatime-accessibility directory"
    exit 1
fi

# Install required system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y \
    python3-gi \
    python3-gi-dev \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1 \
    libgtk-4-dev \
    libadwaita-1-dev \
    pulseaudio-utils \
    libnotify-bin \
    xvfb

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install PyGObject

# Create requirements.txt
cat > requirements.txt << 'EOF'
PyGObject>=3.42.0
EOF

# Create desktop entry for the application
echo "Creating desktop entry..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/teatime-accessible.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Accessible Tea Timer
Comment=A tea timer with accessibility features
Exec=/home/$USER/GitHub/teatime-accessibility/venv/bin/python /home/$USER/GitHub/teatime-accessibility/src/teatime.py
Icon=preferences-system-time
Terminal=false
Categories=Utility;
Keywords=timer;tea;accessibility;
EOF

# Replace $USER with actual username
sed -i "s/\$USER/$USER/g" ~/.local/share/applications/teatime-accessible.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications/

# Create a launcher script
cat > teatime-accessible << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 src/teatime.py "$@"
EOF

chmod +x teatime-accessible

# Create README with accessibility features
cat > README.md << 'EOF'
# Accessible Tea Timer

An improved version of the Tea Timer application with enhanced accessibility features.

## Accessibility Features

### Visual Accessibility
- **Adjustable Font Size**: Use A+ and A- buttons or Ctrl++ and Ctrl+- to increase/decrease font size
- **High Contrast Support**: Automatically adapts to system theme settings
- **Clear Visual Feedback**: Button states and status messages provide clear feedback
- **Tooltips**: Hover tooltips explain what each control does

### Keyboard Accessibility
- **Full Keyboard Navigation**: Tab through all controls
- **Keyboard Shortcuts**:
  - `Ctrl+S`: Start timer
  - `Ctrl+T`: Stop timer
  - `Ctrl++`: Increase font size
  - `Ctrl+-`: Decrease font size
- **Focus Management**: Proper focus order and visual focus indicators

### Screen Reader Support
- **Proper Labels**: All controls have descriptive labels
- **Status Updates**: Status changes are announced to screen readers
- **Role Definitions**: UI elements have proper ARIA roles
- **Live Regions**: Timer updates are announced appropriately

### Audio Accessibility
- **Sound Notifications**: Audio feedback for start, stop, and completion
- **Desktop Notifications**: System notifications for timer completion
- **Fallback Sounds**: System bell if audio files aren't available

## Usage

### Running the Application
```bash
./teatime-accessible