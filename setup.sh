--- a/home/yourusername/GitHub/teatime-accessibility/setup.sh
+++ b/home/yourusername/GitHub/teatime-accessibility/setup.sh
@@ -7,7 +7,7 @@
 echo "Setting up Accessible Tea Timer..."
 
 # Check if we're in the right directory
-if [ ! -f "src/teatime.py" ]; then
+if [ ! -f "bin/teatime.py" ]; then
     echo "Error: Please run this script from the teatime-accessibility directory"
     exit 1
 fi
@@ -36,7 +36,7 @@
 [Desktop Entry]
 Type=Application
 Name=Accessible Tea Timer
 Comment=A tea timer with accessibility features
-Exec=/home/$USER/GitHub/teatime-accessibility/venv/bin/python /home/$USER/GitHub/teatime-accessibility/src/teatime.py
+Exec=/home/$USER/GitHub/teatime-accessibility/venv/bin/python /home/$USER/GitHub/teatime-accessibility/bin/teatime.py
 Icon=preferences-system-time
 Terminal=false
 Categories=Utility;
@@ -51,41 +51,9 @@
 #!/bin/bash
 cd "$(dirname "$0")"
 source venv/bin/activate
-python3 src/teatime.py "$@"
+python3 bin/teatime.py "$@"
 EOF
 
 chmod +x teatime-accessible
 
-# Create README with accessibility features
-cat > README.md << 'EOF'
-# Accessible Tea Timer
-
-An improved version of the Tea Timer application with enhanced accessibility features.
-
-## Accessibility Features
-
-### Visual Accessibility
-- **Adjustable Font Size**: Use A+ and A- buttons or Ctrl++ and Ctrl+- to increase/decrease font size
-- **High Contrast Support**: Automatically adapts to system theme settings
-- **Clear Visual Feedback**: Button states and status messages provide clear feedback
-- **Tooltips**: Hover tooltips explain what each control does
-
-### Keyboard Accessibility
-- **Full Keyboard Navigation**: Tab through all controls
-- **Keyboard Shortcuts**:
-  - `Ctrl+S`: Start timer
-  - `Ctrl+T`: Stop timer
-  - `Ctrl++`: Increase font size
-  - `Ctrl+-`: Decrease font size
-- **Focus Management**: Proper focus order and visual focus indicators
-
-### Screen Reader Support
-- **Proper Labels**: All controls have descriptive labels
-- **Status Updates**: Status changes are announced to screen readers
-- **Role Definitions**: UI elements have proper ARIA roles
-- **Live Regions**: Timer updates are announced appropriately
-
-### Audio Accessibility
-- **Sound Notifications**: Audio feedback for start, stop, and completion
-- **Desktop Notifications**: System notifications for timer completion
-- **Fallback Sounds**: System bell if audio files aren't available
-
-## Usage
-
-### Running the Application
-```bash
-./teatime-accessible
-```
-EOF

