# TeaTime Accessibility

- a GUI (graphical user interface) based timer application (app) for the Ubuntu (Desktop) environment.
- ability to make the buttons inside larger and more visible
- presets for time, reminders (  including audible bell(s)  ), basic statistics
- visual effects (gifs): animations upon completion of a Session and dynamic skins

> [!NOTE]
> the main branch holds the code for the regular (non-photosensitive version). You can clone from the main page directly or from the releases page.

> [!IMPORTANT]
> separately, a **photosensitive version** of the app is also available from the releases section, please see below [link](https://github.com/genidma/teatime-accessibility/tree/main-dev?tab=readme-ov-file#photosensitive-epilepsy-safe-version)
- - code submission for the initial photosensitive version by @shanaya-gupta


_New features are added regularly_. To request or suggest additional features and/or to join, please see a link to the discussions/[feedback](https://github.com/genidma/teatime-accessibility?tab=readme-ov-file#feedback) section towards the end of this Readme. 

## Features

- **Simple Timer**: Easy-to-use interface with start/stop controls
- **Visual Notifications**: Fullscreen alerts, for you to go and enjoy your cuppa tea
- **Sound Notifications**: Audible sounds to complement visual notifications (if you choose to enable this option)
- **Customizable Animations**: Choose from multiple animated sprites to display when timer completes
- **Accessibility Features**:
  - Large, clear display
  - High contrast mode
  - Font scaling options
  - Keyboard shortcuts
- **Statistics Tracking**: Automatic logging and viewing of tea sessions w/ the ability to export to CSV
- **Settings Dialog**: Configure animation preferences through a user-friendly interface
- **Mini-Mode**: Compact display mode for a smaller window footprint
- **Nano-Mode**: Ultra-compact mode with transparent background that shows only the timer digits
- **Custom Skins**: Personalize the appearance with different visual themes
- **Preset Durations**: Quick access to 45 minute and 60 minute presets

# Demo(s) (in gif format)

### open app & start/stop the timer

in the first demo:
- app is opened using the icon on the desktop
- the timer is started using the buttons on the gui (graphical user interface)
- notice how the **timer increments in 5 seconds intervals** 
- the timer is then stopped. As this is just a demo
- fyi: If you are new to Github, then the .gif file below (and in subsequent demos) are looping through and they are typically of a shorter duration. 
![Demo - gif format](./screenshots_demo_clones/new_demos_49/open_app_start_stop.gif)

### session presets & manual durations

in this next demo, let's:
- invoke the timer using the 'Session Presets', currently located on the right-hand side of the gui
- demo how the timer can be started by clicking on the 'Session Presets' buttons, or by manually entering a value in the 'Minutes' field and clicking 'Start' 
- to stop the timer: Simply use the 'Stop' button or use the keyboard shortcuts (below in this Readme)
- how to decrease or increase the values for the 'Minutes' field by clicking on the - or + buttons
![Demo - gif format](./screenshots_demo_clones/new_demos_49/session-presets_and_manual-durations.gif)

### resizing

here
- let's resize the gui and the buttons inside of it using the A- and A+ buttons
- this function can also be performed leveraging the keyboard shortcuts (see in the correspondiong sections)

![Demo - gif format](./screenshots_demo_clones/new_demos_49/resizing.gif)

### enable or disable sound and animations

> [!NOTE]
> in addition to the demo directly below, there's more info about the customizable animations feature in one of the following sections, via: [link](https://github.com/genidma/teatime-accessibility/tree/main-dev?tab=readme-ov-file#customizable-animations)

- the 'Enable Sound' _checkbox_ can be used to enable or disable sound
- if selected, a .wav file will be played automatically, upon the completion of the timer
- _note_: if you uncheck this feature, then you will still get a visual (animation based) reminder, regardless of whether the 'Enable Sound' checkbox is checked or not
- because this is a .gif format being displayed, unfortunately the sound is not going to come through in this demo. But it definitely works when you install the app!
- in this demo, we also go into the Settings section to show you the section where you can select different animations

![Demo - gif format](./screenshots_demo_clones/new_demos_49/sound.gif)

### mini mode and nano mode

> [!NOTE]
> in addition to the demo (directly below), there is more information about these modes in one of the following sections below [link](https://github.com/genidma/teatime-accessibility/tree/main-dev?tab=readme-ov-file#display-modes)

- **mini mode**: suppose you only have one monitor and you don't want the app to take up the whole screen or most of the screen. this is where **mini mode** comes in handy
- upon choosing this option, the 'Session Presets' are hidden from view (they are still there, just temporarily hidden) and the size for the GUI is scaled down
- to get out of this mode, you simply uncheck the dialog box for 'mini mode'. Next you close the app and reopen it

![Demo - gif format](./screenshots_demo_clones/new_demos_49/minimode.gif)

- **nano mode**: this mode provides an absolute bare minimum timer. Once the timer is initiated in nano mode, it can only be controlled with keyboard shortcuts (see below)
- this feature was developed for individuals who are doing [deep work](https://www.amazon.com/Deep-Work-Focused-Success-Distracted/dp/1455586692) (via [Cal Newport](https://calnewport.com/)). When in a deep-work focused flow state, individuals would only want to occasionally glance at the timer in nano mode.
- all other features work and as expected in all modes. including the nano mode (animations after a session has concluded, sound and if you chose the option e.t.c)
- to get out of this mode. You would either wait for the timer to complete or use the keyboard shortcuts to stop the timer. next, you simply uncheck the dialog box for 'nano mode'. next, closing and reopening the app will get you back in the mode selected
- fyi: if for some reason, you choose the both mini-mode and nano-mode dialog box(es), here the nano-mode will be triggered
- fyi: the color for the numbers in nano-mode is Vanta Black. In the situation that your Desktop Background also happens to be Vanta Black! 
- overall, if you _do not_ select mini-mode or nano-mode, you will be in the normal mode.

- below, two demos are shown. 
- - 1. in this demo. The timer in started nano-mode. Then we use the meta key to move the timer on the screen. Then use the keyboard shortcuts to increase or decrease the timer, while it is in nano-mode. Finally we stop the timer, using the keyboard shortcut. 

![Demo - gif format](./screenshots_demo_clones/new_demos_49/nanomode1.gif)

- - 2. in this second demo, with nano mode _engaged_. You will notice that the timer is about to conclude. Once, concluded the app displays a full-screen animation.  
- - - once the timer has concluded, the app will return back to the main GUI and here you can simply uncheck the checkbox for nano mode

![Demo - gif format](./screenshots_demo_clones/new_demos_49/nanomode2.gif)

### Settings and customization options

as of 2025-11-06, there are two options under the 'Settings' area from the dialog box and here is more information about each option.

#### Animations
- this is where you choose which animation you want to see, once the timer has concluded. Currently there are two options in there. You must have noticed one of the demo from one of the previous section (above), so no point in repeating this demo. Changing this setting is easy, just click on the dropdown menu and select the option you want

#### Custom Skins

> [!NOTE]
> There is more information about the custom skins in one of the following sections. Here's the [link](https://github.com/genidma/teatime-accessibility/tree/main-dev?tab=readme-ov-file#custom-skins-1)

- there are currently two options under the _Settings_ for the **'Skins for Main UI (User Interface):**' section. **1. Default - No Skin** and **2. Lava Lamp** 
- - note: a change in this (Settings) section requires that the app is closed and opened again  
- in the demo below, the app will be opened in the 'Default - No Skin'. Next, the settings will be changed to 'Lava Lamp' and the app will be reopened.
- - note: the 'Lava Lamp' skin feature makes use of css (cascading style sheets), in order to dynamically change the app's skin. 

![Demo - gif format](./screenshots_demo_clones/new_demos_49/skins.gif)

#### Statistics
- the statistics section (engine) is powered by a local database in the form of a .json file

> [!IMPORTANT]
> as with every other file related to this app, all of the data sits on your machine and no data is ever sent anywhere. period!
- coming back to the statistics (stats) section (invoked from the dialog box or keyboard shortcut option): each time a timer concludes it's full cycle, an entry is logged in the engine
- - A full-cycle is a successful completion of the duration specified for timer. Meaning, that the cycle has not been stopped/interrupted by the user
- as you will notice in the demo, the user has to refresh the ui in the  statistics section to see the updated data

![Demo - gif format](./screenshots_demo_clones/new_demos_49/statistics.gif)

#### Export to CSV
- this feature allows the user to export the data stored in the Statistics view to a CSV file
- you can then load the data from the CSV file into an application of your choosing (that is designed to handle CSV files)

> [!NOTE]
> exporting data **does not** delete the data from the Statistics view 

![Demo - gif format](./screenshots_demo_clones/new_demos_49/export2csv.gif)


#### Clear History
- the 'Clear History' feature is a simple way to clear all the data stored the Statistics view
- this is **not** an **'Export'** (like above)
- the color of this button has been deliberately set to red to make it stand out
- - in addition to: the user is presented with not one, but _two reminders_ that they are about to wipe out the data logged (to date)
- this is like browser history. once you clean it and start using the browser again, your browser automatically starts recording the history again
- the amount of rows populated inside of the .json file should have absolutely any bearing on the functioning of the app
- - in the off situation where the .json file is populated with a large amount of rows (say a thousand rows or more) **and** this is leading to the app taking up more than 700 MB (Megabytes. I mean, it shouldn't take more than 500 MB of Memory Usage anyways [link](https://github.com/genidma/teatime-accessibility/issues/37)) of RAM (Random Access Memory or Physical Memory) on your machine. -> In such a situation, please look into creating a new issue by following the links from the 'Feedack' section [below](https://github.com/genidma/teatime-accessibility/tree/main-dev?tab=readme-ov-file#feedback)
- - - by the way, if you missed the url for the recorded session from the links directly above. the proof is definitive that memory_usage for this app is very stable. here's the link again [https://www.youtube.com/watch?v=m4BbTRmpyaA](https://www.youtube.com/watch?v=m4BbTRmpyaA)

![Demo - gif format](./screenshots_demo_clones/new_demos_49/chistory.gif)



## Keyboard Shortcuts

- **Space**: Start/stop timer
- **Ctrl+S**: Start timer
- **Ctrl+T**: Stop timer
- **Ctrl+I**: Open statistics window
- **Ctrl+M**: Toggle sound on/off
- **Ctrl+,**: Open settings dialog
- **Ctrl++**: Increase font size
- **Ctrl+-**: Decrease font size
- **Ctrl+D**: Toggle mini-mode
- **Ctrl+N**: Toggle nano-mode
- **Ctrl+Q**: Quit application

## Mnemonics (Alt Keys)

Activate buttons and menu items by pressing Alt plus the underlined letter.

**Main Window:**
- **Alt+S**: Start
- **Alt+T**: Stop
- **Alt+E**: Enable Sound
- **Alt+M**: Mini Mode
- **Alt+N**: Nano Mode
- **Alt+4**: 45 Minutes
- **Alt+1**: 1 Hour

**Statistics Window:**
- **Alt+R**: Refresh Statistics
- **Alt+E**: Export to CSV
- **Alt+C**: Clear History

## Display Modes

TeaTime Accessibility offers multiple display modes to suit different preferences and use cases.

### Mini-Mode

Mini-Mode provides a compact interface that reduces the overall window size while keeping all controls visible. This mode is ideal for when you want a smaller footprint on your desktop but still need access to all controls.

Features of Mini-Mode:
- Reduced window size
- Smaller controls and text
- All interface elements remain visible
- Can be toggled on/off with Ctrl+M or via the Settings dialog

### Nano-Mode

Nano-Mode is an ultra-compact display mode that shows only the timer digits and colon with a transparent background. This mode automatically activates when a timer starts (if enabled in settings) and provides an unobtrusive timer that floats on your desktop.

Features of Nano-Mode:
- Transparent background with no window decorations (title bar, borders)
- Only the timer digits and colon are visible
- Can be moved by clicking and dragging anywhere on the display. Press and hold the Meta key (usually the Windows key) on your keyboard and then click and drag anywhere on the window with the left mouse button
- Font size can still be adjusted using Ctrl++ and Ctrl+- even though the buttons are hidden
- Keyboard shortcuts still work. So to stop the timer in nano mode, you will do a ctrl+T. See the Keyboard Shortcuts section below for additional keyboard shortcuts.

To enable Nano-Mode:
- Use the "Nano Mode" checkbox in the Settings dialog (accessed via Ctrl+,)
- When enabled, the timer will automatically switch to nano display when started

When a timer is started with Nano-Mode enabled:
- The window automatically switches to the ultra-compact display
- All interface elements except the timer are hidden
- The window decorations are removed
- The background becomes transparent while preserving skin effects

When the timer completes or is stopped:
- The interface returns to its previous state (normal or mini mode)
- Window decorations are restored
- All interface elements become visible again

## Custom Skins

TeaTime Accessibility supports customizable visual themes:

- **Default Skin**: Standard grey background
- **Lava Lamp Skin**: Animated gradient background that flows like a lava lamp with dynamic colors

To select a skin:
1. Open the Settings dialog (Ctrl+, or from the menu)
2. Choose your preferred skin from the dropdown
3. Click OK to save your preference

Skins are preserved even in Nano-Mode, appearing as semi-transparent overlays behind the timer digits.

## Customizable Animations

The application supports multiple animated sprites that can be displayed when a timer completes. 
Currently included animations:
- Test animation (default)
- Puppy animation

To select which animation to display:
1. Open the Settings dialog (Ctrl+, or from the menu)
2. Choose your preferred animation from the dropdown
3. Click OK to save your preference

New animations can be added by creating a subdirectory in `assets/sprites/` with PNG frames 
following the naming pattern `*sprite_frame_*.png`.


## Demos on Youtube
* [Shorter demo video on YT](https://youtu.be/gsrPCAagAtw?t=137)
* [40 + minute demo " " ](https://youtu.be/cgc0qMRA638)


## Distinct Branch

### Photosensitive Epilepsy Safe Version
* a photosensitive version of the app was created by @shanaya-gupta with further code modifications led by @genidma
* it does not have any visual effects or sudden screen changes
* the latest stable photosensitive version of the app can be [downloaded via the releases section](https://github.com/genidma/teatime-accessibility/releases)


## Features

### Visual and Audio Accessibility
- **Rainbow 🌈 Glow**: Use tab on the keyboard ⌨️. As you cycle through the buttons they glow with a different color, each time the app is launched 
- **Live Regions**: Timer updates are announced visually and through the audio prompt (Simion's bell)

### Keyboard Accessibility
- **Full Keyboard Navigation**: Tab through all controls
- **Keyboard Shortcuts**:
  - `Ctrl+S`: Start timer
  - `Ctrl+T`: Stop timer
  - `Ctrl+I`: Show Statistics window
  - `Ctrl+M`: Toggle sound on/off
  - `Ctrl+,`: Open settings dialog
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

## Installation

### Prerequisites
Before running the install script, please install the required system dependencies. Note: See [instructions](https://ubuntu.com/tutorials/command-line-for-beginners#3-opening-a-terminal) on how to open and use a terminal and if you are new to Linux:

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
3. Create a desktop shortcut/icon for quick access (if you choose this option during the install)
4. Make the launcher script executable

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

### Snap Installation
TeaTime Accessibility is available as a Snap package for easy installation on Ubuntu and other Linux distributions.

#### Standard Version (main branch)
```bash
sudo snap install teatime-accessibility --channel=latest/stable
```

#### Photosensitive Version (photosensitive-version branch)
```bash
sudo snap install teatime-accessibility --channel=photosensitive/stable
```

### Flatpak Installation
TeaTime Accessibility is also available as a Flatpak for sandboxed installation.

#### Standard Version (main branch)
```bash
flatpak install flathub org.genidma.TeatimeAccessibility
```

#### Photosensitive Version (photosensitive-version branch)
```bash
flatpak install flathub org.genidma.TeatimeAccessibility.Photosensitive
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

### Option 1: Main 'Activities Menu'
1. Click on the 'Activities Menu' in Ubuntu Desktop. Highlighted with a Green Rectangle (with circular edges in the screenshot below)

   ![Activities Menu](screenshots_demo_clones/2025-10-16-Start-or-Activities-menu.png)
   
2. Depending on how many apps you have installed on your computer, you might have to scroll to the following views. 

In the illustration below: The icon for the app appears on the second page (or view). You either scroll to this location or you can click on the dots that you see at the bottom of the screen.

Screenshot below for visual representation:
Where (the same Green Rectangle with circular edges as in the previous screenshot) represents:

    1.  (within the screenshot directly) the mechanism via which you can scroll through the views. 

    And

    2.icon for the app itself
   ![Activities Menu Scroll](screenshots_demo_clones/2025-10-16-Start-or-Activities-menu-scroll.png)
3. Click on the application icon to launch it

### Option 2: Desktop Shortcut
If you chose to create a desktop shortcut during installation:
1. Navigate to your desktop
2. Right-click on the "TeaTime Accessibility" icon
3. Select "Allow Launching" from the context menu
5. Double-click the icon to launch the application
4. As of 2025-10-16, the icon looks like this. 

   <img src="./assets/icon.png" width="48" height="52" alt="Application Icon">

On Ubuntu Desktop, the icon will look like this (below):

   <img src="./screenshots_demo_clones/2025-10-16-icon-for-Readme.png" alt="Application Icon">

Fyi only: The icon looks larger in the illustrations here. The icons on your computer will be the same size as any other icon on your Ubuntu Desktop. 

The application will appear in your system tray (notification area) and can be controlled from there.

Note: The virtual environment is created in the project directory and persists between sessions. It only needs to be recreated if you manually delete it or run the uninstall script. For the desktop shortcut, you must first right-click on the icon and select "Allow Launching" from the context menu before you can use it to start the application.

### Option 3: Command Line
1. Navigate to the project directory (the location on your computer, where you originally cloned the repository)
2. Activate the existing virtual environment:
   ```bash
   source teatime-venv/bin/activate
   ```
3. Run the application:
   ```bash
   ./teatime-accessible.sh
   ```

### Command Line Options for Duration
A custom duration can be specified via the GUI and also via the command line. As a note on the aside, durations are always in minutes.

To do this on the command line:

1. Open a [terminal](https://ubuntu.com/tutorials/command-line-for-beginners#3-opening-a-terminal) and navigate to the project directory
2. In the example directly below, a 5 minute range has been specified for the duration. You still have to click on Start manually: 

```bash
# Range for duration (1-999 minutes)
# Example below
./teatime-accessible.sh --duration 5
```

When you launch the application with the `--duration` parameter, the specified value will be pre-filled in the minutes input field within the GUI. And you can choose any value specified in the 'range' above

As another example, if you frequently use a 30-minute timer. You could simply change/specify the duration like this:
```bash
./teatime-accessible.sh --duration 30
```

This eliminates the need to manually adjust the timer duration, each time you start the application.

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

2. To remove the desktop shortcut:
   ```bash
   rm ~/Desktop/teatime-accessibility.desktop
   ```

3. To remove the virtual environment:
   ```bash
   rm -rf teatime-venv
   ```

4. To remove configuration and statistics:
   ```bash
   rm ~/.config/teatime_config.json
   rm ~/.local/share/teatime_stats.json
   ```

## Development
The application consists of several scripts, each with a specific purpose:

- `bin/teatime.py`: The main Python application script, which programmatically builds the GTK3 user interface.

- `teatime-accessible.sh`: The launcher script that activates the virtual environment (if available) and starts the application. This is the recommended way to run the application as it ensures proper environment setup.

- `install.sh`: The installation script that:
  - Creates a Python virtual environment with system site packages access
  - Installs all required dependencies from requirements.txt
  - Sets up desktop integration by creating a .desktop file
  - Makes the launcher script executable
  - Optionally creates a desktop shortcut

- `uninstall.sh`: The removal script that:
  - Removes the desktop entry from the applications menu
  - Optionally removes the virtual environment
  - Preserves user configuration and statistics by default

- `teatime-accessibility.desktop`: The desktop entry file that integrates the application with the system's application menu and desktop environment.

- `requirements.txt`: Lists all Python package dependencies required for the application to run.

- `test_short_timer.py`: Test script used during development to verify timer functionality.

The application stores user configuration in `~/.config/teatime_config.json` and session statistics in `~/.local/share/teatime_stats.json`.

## Testing Tools

Script designed to verify application functionality (without having to wait for the timer to go off):

### test_short_timer.py
- Launches the app with a 1 second timer (see Usage below)
- Automatically starts the timer without manual intervention

**Usage:** git checkout main

####  Run with duration in seconds instead of minutes
```
python3 test_short_timer.py --duration 1 --use-seconds
```

### bin/teatime-tasks-priority-test.py
Script for project management that:
- Fetches open issues from the GitHub repository
- Categorizes them by type (bug, feature, enhancement, documentation)
- Prioritizes them by priority level (high, medium, low)
- Classifies them by complexity (simple, medium, complex)
- Generates recommended task order for development

**Usage:**
```bash
python3 bin/teatime-tasks-priority-test.py
```

Note: For authenticated requests (to avoid rate limiting), you can set a GITHUB_TOKEN environment variable with a GitHub personal access token.

## Feedback
Here's how you can reach out:

- **[Create an issue](https://github.com/genidma/teatime-accessibility/issues)** if you:
  - Found a bug or something isn't working as expected
  
- **[Start a discussion](https://github.com/genidma/teatime-accessibility/discussions)** if you:
  - Have ideas :bulb: or suggestions for improvements
  - Want to propose a new feature
  - Need help using the application
  - Want to share your experience or ask general questions

Issues are best for reporting problems that need to be fixed, while discussions are perfect for ideas, suggestions, and questions. 

## License
Originally inspired by the Tea Timer application from the Ubuntu snap store [link](https://snapcraft.io/install/teatime/ubuntu). By now, the code is entirely different and keeps evolving. The release(s) are also with with a different licensing policy.

## Credits
* For a complete list of credits, please see [CREDITS.md](CREDITS.md)