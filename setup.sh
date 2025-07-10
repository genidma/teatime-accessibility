echo "Setting up Accessible Tea Timer..."

# Check if we're in the right directory
if [ ! -f "bin/teatime.py" ]; then
    echo "Error: Please run this script from the teatime-accessibility directory"
    exit 1
fi
[Desktop Entry]
Type=Application
Name=Accessible Tea Timer
Comment=A tea timer with accessibility features
Exec=/home/$USER/GitHub/teatime-accessibility/venv/bin/python /home/$USER/GitHub/teatime-accessibility/bin/teatime.py
Icon=preferences-system-time
Terminal=false
Categories=Utility;
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 bin/teatime.py "$@"
EOF

chmod +x teatime-accessible


