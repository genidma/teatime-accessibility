# TeaTime Accessibility

TeaTime Accessibility is an accessibility focused timer application (app) for the Ubuntu (Desktop) environment. This app has timers with presets, reminders (audible vs to the contrary) and basic statistics for your sessions. It also has a fun rainbow-glow feature (see below)

## Features

- **Timer:** Set custom break intervals for better productivity.
- **Accessibility Integration:** Works seamlessly with screen readers and other assistive technologies.
- **Usage Statistics:** Tracks your session times and provides insights into your computer usage habits. The statistics are stored in `~/.local/share/teatime_stats.json`.
- **Custom Application Icon:** Features a distinctive teapot-themed icon for better recognition in your applications menu.

# Accessible Tea Timer

A simpler version of the Tea Timer application with enhanced accessibility features.

![Demo - gif format](./screenshots_demo_clones/demo-2025-07-15.gif)

Screenshot of the main GUI (graphical user interface) from version 1.3.3 of the app
![screenshot](./screenshots_demo_clones/2025-07-15-screenshot-for-README.png)

Screenshot of the Statistics engine that is built into the app. It automatically records the number of sessions by date. Including, breakdown for the Total number of sessions, Total Time for Sessions, Average Duration considering duration of all the Sessions
![screenshot for stats](./screenshots_demo_clones/2025-10-14-screenshot-for-README-STATS.png)

## Demos on Youtube
* [Shorter demo video on YT](https://youtu.be/gsrPCAagAtw?t=137)
* [40 + minute demo " " ](https://youtu.be/cgc0qMRA638)


## Accessibility Features

### Visual Accessibility
- **Adjustable Font Size**: Use A+ and A- buttons or Ctrl++ and Ctrl+- to increase/decrease font size
- **High Contrast Support**: Automatically adapts to system theme settings
- **Clear Visual Feedback**: Button states and status messages provide clear feedback
- **Rainbow 🌈 Glow**: Use tab on the keyboard ⌨️. As you cycle through the buttons they glow with a different color, each time the app is launched 

### Keyboard Accessibility
- **Full Keyboard Navigation**: Tab through all controls
- **Keyboard Shortcuts**:
  - `Ctrl+S`: Start timer
  - `Ctrl+T`: Stop timer
  - `Ctrl+I`: Show Statistics window
  - `Ctrl+M`: Toggle sound on/off
  - `Ctrl++`: Increase font size
  - `Ctrl+-`: Decrease font size
  - `Ctrl+Q`: Quit the application
- **Mnemonics (Alt Keys)**: Activate buttons and menu items by pressing `Alt` plus the underlined letter.
  - **Main Window:**
    - `Alt+S`: **S**tart
    - `Alt+T`: S**t**op
    - `Alt+E`: **E**nable Sound
    - `Alt+4`: **4**5 Minutes
    - `Alt+1`: **1** Hour
  - **Statistics Window:**
    - `Alt+R`: **R**efresh Statistics
    - `Alt+E`: **E**xport to CSV
    - `Alt+C`: **C**lear History
- **Focus Management**: Proper focus order and visual focus indicators

### Screen Reader Support
- **Proper Labels**: All controls have descriptive labels
- **Status Updates**: Status changes are announced to screen readers (I have to test this)
- **Live Regions**: Timer updates are announced visually and through the audio prompt (bell)

### Audio Accessibility
- **Sound Notifications**: Audio feedback (bell 🔔 )at the completion of each session 
- **Desktop Notifications**: System notifications for timer completion
- **Fallback Sounds**: System bell if audio files aren't available

## Installation

### Prerequisites
Before running the install script, install the required system dependencies:

```bash
sudo apt install python3-dev libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-venv gir1.2-gtk-3.0
```

For better compatibility, we also recommend installing the system-wide PyGObject packages:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Automatic Installation (Recommended)
First, clone the repository to a location of your choice, then run the install script:

```bash
git clone <repository-url>
cd teatime-accessibility
./install.sh
```

This script will:
1. Create a virtual environment with access to system packages (if one doesn't already exist)
2. Install all required dependencies
3. Create a desktop entry for easy access in the Utilities section of your application menu
4. Optionally create a desktop shortcut/icon for quick access
5. Make the launcher script executable

The install script will also prompt you to install system dependencies if needed.

### Manual Installation
If you prefer to install manually:

1. Create a virtual environment with access to system packages:
   ```bash
   python3 -m venv teatime-venv --system-site-packages
   source teatime-venv/bin/activate
   ```

2. Install dependencies (if needed):
   ```bash
   pip install -r requirements.txt
   ```

3. Create desktop entry (optional):
   ```bash
   mkdir -p ~/.local/share/applications
   cp teatime-accessibility.desktop ~/.local/share/applications/
   ```
   
   You can also create a desktop shortcut for direct access:
   ```bash
   cp teatime-accessibility.desktop ~/Desktop/
   ```

After running these commands, you'll find "TeaTime Accessibility" in the Utilities section of your application menu. The desktop entry will be created at `~/.local/share/applications/teatime-accessibility.desktop`. If you choose to create a desktop shortcut during the installation process, you can also launch the app directly from your desktop in future instances.

## Installation Locations

When you run the install script, here's exactly where each component is installed:

1. **Virtual Environment**: 
   - Location: Inside the project directory as `teatime-venv/`
   - This is a local virtual environment that stays within your project folder

2. **Desktop Entry**:
   - Location: `~/.local/share/applications/teatime-accessibility.desktop`
   - This allows the app to appear in your system's application menu under "Utilities"

3. **Desktop Shortcut** (if you choose to create one):
   - Location: On your desktop (e.g., `~/Desktop/teatime-accessibility.desktop`)
   - This provides a direct shortcut icon on your desktop

4. **Application Files**:
   - All application files remain in your project directory (wherever you cloned the repository)
   - This includes the main Python script, assets, and configuration files

5. **User Data**:
   - Configuration: `~/.config/teatime_config.json`
   - Statistics: `~/.local/share/teatime_stats.json`

The important thing to note is that the application itself is not moved or copied elsewhere - it runs directly from your project directory. The install script simply:
1. Sets up the virtual environment for isolated dependencies
2. Creates convenient access points (desktop entry and/or desktop shortcut)
3. Ensures all necessary components are properly configured

This approach keeps everything contained within your project directory while providing convenient access methods through the standard desktop environment interfaces.

## Usage

After installation, you can run the application in one of the following ways:

### Option 1: Applications Menu
1. Open your applications menu
2. Look for "TeaTime Accessibility" under the "Utilities" category
3. Click on the application icon to launch it

### Option 2: Desktop Shortcut
If you chose to create a desktop shortcut during installation:
1. Navigate to your desktop
2. Right-click on the "TeaTime Accessibility" icon
3. Select "Allow Launching" from the context menu
4. Once you have selected "Allow Launching" and as of 2025-10-16, your icon will look like this. 

   <img src="./assets/icon.png" width="48" height="52" alt="Application Icon">

On Ubuntu Desktop, the icon will look like this (below):

   <img src="./screenshots_demo_clones/2025-10-16-icon-for-Readme.png" alt="Application Icon">

Note: The icon will look like the same size as any other icon on your Ubuntu Desktop. It looks a bit bigger via the screenshot here. Fyi only.

5. Double-click the icon to launch the application

The application will appear in your system tray (notification area) and can be controlled from there.

Note: The virtual environment is created in the project directory and persists between sessions. It only needs to be recreated if you manually delete it or run the uninstall script. For the desktop shortcut, you must first right-click on the icon and select "Allow Launching" from the context menu before you can use it to start the application.

### Option 3: Command Line
1. Navigate to the project directory (wherever you originally cloned the repository)
2. Activate the existing virtual environment:
   ```bash
   source teatime-venv/bin/activate
   ```
3. Run the application:
   ```bash
   ./teatime-accessible.sh
   ```

### Command Line Options
The application supports command line arguments for setting the default timer duration. Including custom durations (Different from Session Presets in the GUI - Graphical User Iterface)

To use the command line option:

1. Open a terminal and navigate to the project directory
2. Next, you can specify different parameters for the duration:

```bash
# Set default duration (1-999 minutes)
./teatime-accessible.sh --duration 5
```

When you launch the application with the `--duration` parameter, the specified value will be pre-filled in the minutes input field within the GUI.

For example, if you frequently use a 30-minute timer. Because you want to check in with your loved one or check up on your puppy. Here, you could simply:
```bash
./teatime-accessible.sh --duration 30
```

This eliminates the need to manually adjust the timer duration each time you start the application.

### Configuration
Settings are automatically saved to `~/.config/teatime/settings.json` including:
- Font scale preference
- Default timer duration

## Dependencies
- GTK 3.0+
- Python 3.8+
- PyGObject
- PulseAudio (for sound notifications)

## Uninstalling the Application

### Automatic Uninstall (Recommended)
Run the uninstall script from the project directory:

```bash
./uninstall.sh
```

This script will:
1. Remove the desktop entry
2. Ask if you want to remove the virtual environment
3. Preserve your configuration and statistics

### Manual Uninstall
To manually uninstall:

1. Remove the desktop entry:
   ```bash
   rm ~/.local/share/applications/teatime-accessibility.desktop
   ```

2. Optionally remove the desktop shortcut:
   ```bash
   rm ~/Desktop/teatime-accessibility.desktop
   ```

3. Optionally remove the virtual environment:
   ```bash
   rm -rf teatime-venv
   ```

4. Optionally remove configuration and statistics:
   ```bash
   rm ~/.config/teatime_config.json
   rm ~/.local/share/teatime_stats.json
   ```

## Development
The application consists of:
- `bin/teatime.py`: The main Python application script, which programmatically builds the GTK3 user interface.

## License
Originally inspired by the Tea Timer application from the Ubuntu snap store [link](https://snapcraft.io/install/teatime/ubuntu). But the code is significantly different with a different licensing policy.
