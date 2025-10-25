# TeaTime Accessibility - Release Notes

## v1.3.7 (October 24, 2025)

### New Features

#### Nano Mode
- Introduced a new ultra-compact display mode called "Nano-Mode"
- Displays only the timer digits and colon with a transparent background
- Removes window decorations (title bar, borders) for a minimal appearance
- Perfect for an unobtrusive timer that floats on your desktop
- Accessible via Ctrl+N keyboard shortcut or Nano Mode checkbox in Settings
- Font size can still be adjusted using Ctrl++ and Ctrl+- even though the buttons are hidden

#### Custom Skins
- Added support for customizable visual themes
- Default Skin: Standard grey background
- Lava Lamp Skin: Animated gradient background that flows like a lava lamp with dynamic colors
- Skins are preserved even in Nano-Mode, appearing as semi-transparent overlays behind the timer digits
- Select skins through the Settings dialog

#### Enhanced Accessibility
- Improved font size adjustment functionality
- Better keyboard navigation and shortcuts
- Enhanced screen reader support with updated accessibility descriptions

### Improvements

#### UI/UX Enhancements
- Fixed issues with duplicate UI elements that were causing unexpected behavior
- Improved mode switching between normal, mini, and nano modes
- Enhanced visual consistency across different display modes
- Better handling of window decorations and transparency effects

#### Bug Fixes
- Fixed font button behavior in nano mode where clicking A+ or A- would accidentally start the timer
- Resolved issues with duplicate signal connections that were causing multiple callbacks
- Fixed transparency handling in nano mode to properly show skin effects
- Corrected state management when entering and exiting nano mode
- Fixed skin application in nano mode to preserve visual effects while maintaining transparency

#### Code Quality
- Removed duplicate UI creation code that was causing conflicts
- Improved state management for mode switching
- Enhanced debug logging for better troubleshooting
- Cleaned up signal connection logic to prevent duplicate callbacks

### Technical Updates

#### Dependencies
- Updated requirements.txt with latest compatible package versions
- Improved virtual environment handling in installation scripts

#### Documentation
- Updated README.md with comprehensive information about nano mode
- Added documentation for custom skins feature
- Improved keyboard shortcuts and mnemonics documentation
- Enhanced installation and usage instructions

### Known Issues
- Some keyboard shortcuts may not work properly when in Mini-Mode due to the reduced interface size and focus handling
- In rare cases, window transparency effects may not display correctly on all desktop environments

### Upgrading
To upgrade to v1.3.7, simply run the install.sh script again or pull the latest changes from the repository and restart the application. Existing settings and statistics will be preserved.