#!/usr/bin/env python3
"""
Accessible Tea Timer

Description: A timer application with accessibility features for Ubuntu Desktop.
"""

import argparse
import csv
import json
import locale
import os
import sys
import time
import colorsys
from datetime import datetime
from pathlib import Path
from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
require_version('GLib', '2.0')
from gi.repository import Gtk, Gdk, GLib, Gio

APP_NAME = "TeaTime Accessibility - Photosensitive version"
APP_VERSION = "v1.3.6-photosensitive"

# Default font scale factor
DEFAULT_FONT_SCALE = 1.0

# Configuration and data file paths
CONFIG_DIR = Path.home() / ".config" / "teatime"
CONFIG_FILE = CONFIG_DIR / "settings.json"
DATA_DIR = Path.home() / ".local" / "share"
STATS_LOG_FILE = DATA_DIR / "teatime_stats.json"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Font scaling constants
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 6.0

class TeaTimerApp(Gtk.Application):
    def __init__(self, duration=5, auto_start=False):
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.timer_id = None
        self.duration = duration * 60  # Convert minutes to seconds
        self.remaining = self.duration
        self.last_duration = duration
        self.sound_enabled = True
        self.rainbow_timer_id = None
        self.css_provider = Gtk.CssProvider()
        self._stats_window = None
        self.rainbow_hue = 0
        self._stats_window = None
        self.focus_hue = 0 # Hue for the focus glow, 0-359
        self.focus_timer_id = None # ADDED: Initialize focus timer ID
        self.sprite_window = None  # Reference to sprite animation window
        self.sprite_frames = []    # Storage for sprite frames
        self.current_sprite_frame = 0
        self.sprite_timer_id = None
        self.auto_start = auto_start  # Flag to indicate if timer should start automatically
        self.initial_duration = duration * 60  # Store initial duration in seconds
        self.font_scale_factor = DEFAULT_FONT_SCALE  # Initialize font scale factor
        self._load_config()  # Load settings from file

        # Set up keyboard shortcuts
        self._setup_actions()
        
        # Initialize mini-mode (photosensitive version - no visual effects)
        self.mini_mode = False
        
        # Apply initial font scaling
        self._apply_font_size()

    def do_activate(self):
        """
        This method is called when the application is activated.
        """
        if not self.window:
            # Create window programmatically since UI file might not exist
            self.window = Gtk.ApplicationWindow(application=self, title=APP_NAME)
            self.window.set_default_size(300, 200)
            self.window.connect("destroy", self._on_window_destroy)
            # Use "set-focus-child" signal, which is more reliable for this purpose
            self.window.connect("set-focus-child", self._on_focus_changed)
            # Handle window state changes to prevent issues with maximization
            self.window.connect("window-state-event", self._on_window_state_changed)
            # Handle window resize events
            self.window.connect("configure-event", self._on_window_configure)

            # --- HeaderBar for a modern look ---
            header_bar = Gtk.HeaderBar()
            header_bar.set_show_close_button(True)
            header_bar.props.title = APP_NAME
            self.window.set_titlebar(header_bar)

            # Create a menu for the "About" option
            about_menu = Gtk.Menu()
            stats_item = Gtk.MenuItem(label="_Statistics")
            stats_item.set_use_underline(True)
            stats_item.connect("activate", self.on_stats_activated)
            about_menu.append(stats_item)

            about_item = Gtk.MenuItem(label="_About")
            about_item.set_use_underline(True)
            about_item.connect("activate", self.on_about_activated)
            about_menu.append(about_item)
            about_menu.show_all()

            

            # Create a menu button and add it to the header bar
            menu_button = Gtk.MenuButton(popup=about_menu)
            icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
            menu_button.add(icon)
            header_bar.pack_end(menu_button)

            # Create main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            
            # Accelerators are handled via application actions; no need to bind directly to buttons
            main_box.set_margin_top(20)
            main_box.set_margin_bottom(20)
            main_box.set_margin_start(20) # Use modern property for left margin
            main_box.set_margin_end(20)   # Use modern property for right margin

            # --- Create a horizontal box to hold main controls and presets ---
            content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            main_box.pack_start(content_box, True, True, 0)

            # Time display
            self.time_label = Gtk.Label(label="00:00")
            self.time_label.set_markup("<span>00:00</span>")
            main_box.pack_start(self.time_label, False, False, 0)

            # --- Use a Grid for a clean, aligned layout ---
            grid = Gtk.Grid()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)
            grid.set_halign(Gtk.Align.CENTER) # Center the grid horizontally
            content_box.pack_start(grid, True, True, 0)

            # Row 0: Duration selection
            duration_label = Gtk.Label(label="Minutes:")
            duration_label.get_style_context().add_class("input-label") # Add this line
            self.duration_spin = Gtk.SpinButton.new_with_range(1, 999, 1)
            self.duration_spin.get_style_context().add_class("duration-spinbutton") # Add this line
            self.duration_spin.set_width_chars(3) # Ensure it's wide enough for 3 digits
            self.duration_spin.set_value(self.last_duration)
            # Manually set a large, fixed font size for the spin button's input
            # This is independent of the CSS scaling for user preference.
            # Using CSS provider instead of deprecated override_font method
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(b"""
                spinbutton entry {
                    font-family: Sans;
                    font-weight: bold;
                    font-size: 24px;
                }
            """)
            context = self.duration_spin.get_style_context()
            context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            grid.attach(duration_label, 0, 0, 1, 1)
            grid.attach(self.duration_spin, 1, 0, 1, 1)

            # Row 1: Control buttons
            self.start_button = Gtk.Button(label="_Start Timer")
            self.start_button.set_use_underline(True)
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button = Gtk.Button(label="_Stop Timer")
            self.stop_button.set_use_underline(True)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            grid.attach(self.start_button, 0, 1, 1, 1)
            grid.attach(self.stop_button, 1, 1, 1, 1)

            # Row 2: Font size controls
            self.decrease_font_button = Gtk.Button(label="A-")
            self.decrease_font_button.connect("clicked", self.on_decrease_font_clicked)
            self.increase_font_button = Gtk.Button(label="A+")
            self.increase_font_button.connect("clicked", self.on_increase_font_clicked)
            grid.attach(self.decrease_font_button, 0, 2, 1, 1)
            grid.attach(self.increase_font_button, 1, 2, 1, 1)

            # Row 3: Sound toggle (spans both columns)
            self.sound_toggle = Gtk.CheckButton(label="E_nable Sound")
            self.sound_toggle.set_use_underline(True)
            self.sound_toggle.set_active(self.sound_enabled)
            grid.attach(self.sound_toggle, 0, 3, 2, 1)

            # Row 4: Mini-mode toggle (spans both columns)
            self.mini_mode_toggle = Gtk.CheckButton(label="_Mini Mode")
            self.mini_mode_toggle.set_use_underline(True)
            self.mini_mode_toggle.set_active(self.mini_mode)
            self.mini_mode_toggle.connect("toggled", self._on_mini_mode_toggled)
            grid.attach(self.mini_mode_toggle, 0, 4, 2, 1)

            # --- Presets Box (RIGHT SIDE) ---
            presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            presets_box.set_valign(Gtk.Align.CENTER)
            content_box.pack_start(presets_box, False, False, 0)

            presets_label = Gtk.Label(label="<span size='large'><b>Session Presets</b></span>")
            presets_label.set_use_markup(True)
            presets_box.pack_start(presets_label, False, False, 0)

            preset_5_button = Gtk.Button(label="_5 Minutes")
            preset_5_button.set_use_underline(True)
            preset_5_button.connect("clicked", self.on_preset_clicked, 5)
            presets_box.pack_start(preset_5_button, False, False, 0)

            preset_10_button = Gtk.Button(label="_10 Minutes")
            preset_10_button.set_use_underline(True)
            preset_10_button.connect("clicked", self.on_preset_clicked, 10)
            presets_box.pack_start(preset_10_button, False, False, 0)

            preset_45_button = Gtk.Button(label="_45 Minutes")
            preset_45_button.set_use_underline(True)
            preset_45_button.connect("clicked", self.on_preset_clicked, 45)
            presets_box.pack_start(preset_45_button, False, False, 0)

            preset_1_hour_button = Gtk.Button(label="_1 Hour")
            preset_1_hour_button.set_use_underline(True)
            preset_1_hour_button.connect("clicked", self.on_preset_clicked, 60)
            presets_box.pack_start(preset_1_hour_button, False, False, 0)

            self.window.add(main_box)
            
            # Set GTK 3 accessibility properties (after all widgets are created)
            self._set_accessibility_properties()

        self.window.show_all()

    def _on_window_destroy(self, widget):
        """Called when the main window is closed."""
        self._save_config() # Save settings before exit
        self._stop_timer()  # Ensure timer and any active glows are stopped
        # Clean up any sprite windows if they exist
        if self.sprite_window:
            self.sprite_window.destroy()
        Gtk.main_quit()

    def _on_focus_changed(self, window, widget):
        """Callback for when the focus changes in the window."""
        # Disabled visual effects - do not start/stop focus glow
        pass

    def _on_window_state_changed(self, window, event):
        """Handle window state changes to ensure proper behavior when maximizing/restoring."""
        # If the window was maximized or restored, and we have an active timer,
        # ensure the timer display is still updating
        if self.timer_id is not None:
            # Force an immediate update to ensure display is refreshed
            self._update_timer_display()
            # Add a one-time check to ensure timer is still running properly
            GLib.timeout_add(100, self._ensure_timer_update)
        # No specific action needed, but having this handler prevents some GTK issues
        pass

    def _on_window_configure(self, window, event):
        """Handle window configure events (resize, move) to ensure proper behavior."""
        # This handler ensures that window configuration changes don't interfere 
        # with timer functionality
        # No specific action needed, but having this handler prevents some GTK issues
        pass

    def _ensure_timer_update(self):
        """Ensure the timer update mechanism is still working after window state changes."""
        # If we have an active timer but it's not updating, restart it
        if self.timer_id is not None and self.remaining > 0:
            # Check if timer is actually updating by comparing with a stored value
            # For now, just ensure the display is refreshed
            self._update_timer_display()
        return False  # Don't repeat this check automatically

    def _update_timer_display(self):
        """
        Updates the timer display label.
        """
        # If timer is not running, just update the display with current remaining time
        if self.timer_id is None:
            minutes = self.remaining // 60
            seconds = self.remaining % 60
            formatted_time = f"{minutes:02}:{seconds:02}"
            
            # Apply font scaling
            font_size_px = 36 * self.font_scale_factor # Base font size is 36px
            self.time_label.set_markup(f"<span font_desc='Sans Bold {int(font_size_px)}'>{formatted_time}</span>")
            return False

        if self.remaining <= 0:
            # Ensure we display 00:00 when timer finishes
            self.time_label.set_markup(f"<span font_desc='Sans Bold {int(36 * self.font_scale_factor)}'>00:00</span>")
            
            GLib.source_remove(self.timer_id)
            self.timer_id = None
            self._timer_finished()
            return False

        minutes = self.remaining // 60
        seconds = self.remaining % 60
        formatted_time = f"{minutes:02}:{seconds:02}"

        # Apply font scaling
        font_size_px = 36 * self.font_scale_factor # Base font size is 36px

        self.time_label.set_markup(f"<span font_desc='Sans Bold {int(font_size_px)}'>{formatted_time}</span>")

        # Decrement by 5 seconds since we update every 5 seconds
        self.remaining -= 5
        
        # Continue calling this function
        return True

    def _start_timer(self):
        """Starts the countdown timer."""
        if self.timer_id:
            GLib.source_remove(self.timer_id)

        # Set both duration and remaining based on the spin button value
        self.duration = self.duration_spin.get_value_as_int() * 60
        self.remaining = self.duration
        self.last_duration = self.duration // 60 # Save last duration for config

        if self.remaining <= 0:
            print("Please set a duration greater than 0.")
            return

        # Immediately update the display with the new time
        self._update_timer_display()
        # Use GLib.PRIORITY_DEFAULT instead of default priority to ensure consistent updates
        # Update every 5 seconds (5000ms) for the photosensitive version
        self.timer_id = GLib.timeout_add(5000, self._update_timer_display, priority=GLib.PRIORITY_DEFAULT)

        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        # Preset buttons remain enabled during active timer

        # Start visual effects - DISABLED
        # self._start_rainbow_glow()  # Removed for accessibility
        # self._start_sprite_animation()  # Removed for accessibility

    def _stop_timer(self):
        """Stops the countdown timer."""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

        # Disabled visual effects - do not stop any visual effects

        self.remaining = 0 # Reset time
        self._update_timer_display() # Update display to 00:00
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        # Ensure preset buttons are enabled when timer stops

    def _timer_finished(self):
        """Called when the timer reaches zero."""
        # Record stats
        self._log_session()

        # Play sound if enabled
        if self.sound_enabled:
            sound_played = False
            
            # Get the path to the sound file
            sound_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sounds", "service-bell_daniel_simion.wav")
            
            # Try different methods to play sound, prioritizing our custom bell
            sound_commands = [
                ["aplay", sound_file_path],
                ["paplay", sound_file_path],
                ["canberra-gtk-play", "-f", sound_file_path],
                ["canberra-gtk-play", "-i", "complete"],
                ["canberra-gtk-play", "-i", "dialog-information"],
                ["canberra-gtk-play", "-i", "bell"],
                ["paplay", "/usr/share/sounds/Yaru/stereo/bell.oga"],
                ["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
                ["aplay", "/usr/share/sounds/Yaru/stereo/bell.oga"],
                ["aplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"]
            ]
            
            for cmd in sound_commands:
                try:
                    import subprocess
                    subprocess.run(cmd, check=True, timeout=5)
                    sound_played = True
                    break  # If successful, break out of the loop
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue  # Try the next method
            
            if not sound_played:
                print("Warning: Could not play sound. Please check your sound system configuration.")

        # Update button states - enable Start, disable Stop
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        # Display a dialog
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Session Completed!"
        )
        dialog.run()
        dialog.destroy()

    def _set_preset_buttons_sensitive(self, sensitive):
        """Helper to enable/disable preset buttons."""
        # Get the main box (window -> main_box -> content_box -> presets_box)
        main_box = self.window.get_children()[0]
        content_box = main_box.get_children()[0]
        presets_box = content_box.get_children()[1]  # Presets box is the second child
        
        # Iterate over children of presets_box and set sensitivity for all buttons
        for child in presets_box.get_children():
            if isinstance(child, Gtk.Button):
                child.set_sensitive(sensitive)

    def _apply_font_size(self):
        """Applies the current font scale factor to all UI elements."""
        # Apply to the main time label if it exists
        if hasattr(self, 'time_label') and self.time_label:
            font_size_px = 36 * self.font_scale_factor
            self.time_label.set_markup(f"<span font_desc='Sans Bold {int(font_size_px)}'>{self.time_label.get_text()}</span>")
        
        # Apply font scaling to all UI elements via CSS
        css = f"""
            window, dialog {{
                font-size: {int(12 * self.font_scale_factor)}px;
            }}
            button, label, checkbutton {{
                font-size: {int(12 * self.font_scale_factor)}px;
            }}
            spinbutton entry {{
                font-family: Sans;
                font-weight: bold;
                font-size: {int(24 * self.font_scale_factor)}px;
            }}
            .input-label {{
                font-size: {int(12 * self.font_scale_factor)}px;
            }}
        """
        
        # Apply the CSS
        self.css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _load_config(self):
        """Loads font scale factor and last duration from config file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.font_scale_factor = config.get("font_scale_factor", DEFAULT_FONT_SCALE)
                    self.last_duration = config.get("last_duration", 5) # Default to 5 mins if not found
                    self.sound_enabled = config.get("sound_enabled", True)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}")
                # Reset to defaults on error
                self.font_scale_factor = DEFAULT_FONT_SCALE
                self.last_duration = 5
                self.sound_enabled = True
        else:
            # Ensure the directory exists if creating for the first time
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


    def _save_config(self):
        """Saves current font scale factor, last duration, and sound setting to config file."""
        config = {
            "font_scale_factor": self.font_scale_factor,
            "last_duration": self.duration_spin.get_value_as_int(),
            "sound_enabled": self.sound_toggle.get_active()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print(f"Error saving config file: {e}")

    def _log_session(self):
        """Logs completed session duration and timestamp to a CSV file."""
        STATS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if this is a new file
        is_new_file = not STATS_LOG_FILE.exists()
        
        try:
            # Append to the CSV file
            with open(STATS_LOG_FILE, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'duration_minutes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header if this is a new file
                if is_new_file:
                    writer.writeheader()

                # Calculate the actual duration of the session
                # When timer completes, remaining should be 0, so duration is the full session time
                actual_duration_minutes = self.duration // 60
                
                # Write the session data with simplified timestamp (no microseconds)
                writer.writerow({
                    'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    'duration_minutes': actual_duration_minutes
                })
        except Exception as e:
            print(f"Error logging session: {e}")

    def _setup_actions(self):
        """Sets up Gtk.Application actions for keyboard shortcuts."""
        # Quit action
        action_quit = Gio.SimpleAction.new("quit", None)
        action_quit.connect("activate", self.on_quit)
        self.add_action(action_quit)
        self.set_accels_for_action("app.quit", ["<Primary>q"])
        
        # Start timer action
        action_start = Gio.SimpleAction.new("start", None)
        action_start.connect("activate", self._on_start_action)
        self.add_action(action_start)
        self.set_accels_for_action("app.start", ["<Primary>s"])
        
        # Stop timer action
        action_stop = Gio.SimpleAction.new("stop", None)
        action_stop.connect("activate", self._on_stop_action)
        self.add_action(action_stop)
        self.set_accels_for_action("app.stop", ["<Primary>t"])
        
        # Toggle sound action
        action_toggle_sound = Gio.SimpleAction.new("toggle_sound", None)
        action_toggle_sound.connect("activate", self._on_toggle_sound_action)
        self.add_action(action_toggle_sound)
        self.set_accels_for_action("app.toggle_sound", ["<Primary>m"])
        
        # Increase font size action
        action_increase_font = Gio.SimpleAction.new("increase_font", None)
        action_increase_font.connect("activate", self.on_increase_font_clicked)
        self.add_action(action_increase_font)
        self.set_accels_for_action("app.increase_font", ["<Ctrl>plus", "<Ctrl>equal", "<Ctrl>KP_Add"])
        
        # Decrease font size action
        action_decrease_font = Gio.SimpleAction.new("decrease_font", None)
        action_decrease_font.connect("activate", self.on_decrease_font_clicked)
        self.add_action(action_decrease_font)
        self.set_accels_for_action("app.decrease_font", ["<Ctrl>minus", "<Ctrl>KP_Subtract"])
        
        # Toggle mini-mode action (photosensitive version - no visual effects)
        action_toggle_mini_mode = Gio.SimpleAction.new("toggle_mini_mode", None)
        action_toggle_mini_mode.connect("activate", self._on_toggle_mini_mode_action)
        self.add_action(action_toggle_mini_mode)
        self.set_accels_for_action("app.toggle_mini_mode", ["<Primary>d"])


    # --- Action Handlers ---


    def _on_start_action(self, action, param):
        """Handler for start timer action."""
        self.on_start_clicked(None)
        
    def _on_stop_action(self, action, param):
        """Handler for stop timer action."""
        self.on_stop_clicked(None)
        
    def _on_toggle_sound_action(self, action, param):
        """Handler for toggle sound action."""
        self.sound_toggle.set_active(not self.sound_toggle.get_active())
        
    def _on_toggle_mini_mode_action(self, action, param):
        """Handler for toggle mini-mode action."""
        self.mini_mode = not self.mini_mode
        # Update the UI toggle button to match the new state
        self.mini_mode_toggle.set_active(self.mini_mode)
        self._apply_mini_mode()

    # --- Signal Handlers ---
    def on_start_clicked(self, widget):
        self._start_timer()

    def on_stop_clicked(self, widget):
        self._stop_timer()

    def on_increase_font_clicked(self, *args):
        if self.font_scale_factor < MAX_FONT_SCALE:
            self.font_scale_factor += FONT_SCALE_INCREMENT
            self._apply_font_size()

    def on_decrease_font_clicked(self, *args):
        if self.font_scale_factor > MIN_FONT_SCALE:
            self.font_scale_factor -= FONT_SCALE_INCREMENT
            self._apply_font_size()

    def on_sound_toggled(self, widget):
        """Handles toggling the sound setting."""
        self.sound_enabled = widget.get_active()
        self._save_config()

    def on_preset_clicked(self, widget, minutes):
        """Sets the duration spin button value and starts the timer."""
        # If timer is currently running, stop it first
        if self.timer_id is not None:
            self._stop_timer()
        
        self.duration_spin.set_value(minutes)
        self.on_start_clicked(widget) # Reuse the start button handler

    def on_about_activated(self, widget):
        """Displays the About dialog."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name(APP_NAME)
        about_dialog.set_version(APP_VERSION)
        about_dialog.set_copyright("© 2025 ")
        about_dialog.set_comments("An accessible timer with customizable font sizes and visual/audio cues.")
        about_dialog.set_website("https://github.com/genidma/teatime-accessibility/releases/tag/v1.3.3-photosensitive")
        about_dialog.set_license_type(Gtk.License.MIT_X11)
        about_dialog.set_logo_icon_name("timer") 
        about_dialog.set_transient_for(self.window)
        about_dialog.set_modal(True)
        about_dialog.run()
        about_dialog.destroy()

    def on_stats_activated(self, widget):
        """Displays the Statistics window."""
        if not self._stats_window:
            self._stats_window = Gtk.Window(title="Session Statistics")
            self._stats_window.set_default_size(400, 300)
            self._stats_window.set_transient_for(self.window)
            self._stats_window.set_modal(False) # Non-modal for stats
            self._stats_window.connect("destroy", self.on_stats_window_destroy)

            # Create a vertical box container
            vbox = Gtk.VBox()
            
            scroll_window = Gtk.ScrolledWindow()
            scroll_window.set_vexpand(True)
            scroll_window.set_hexpand(True)

            list_store = Gtk.ListStore(str, int) # (timestamp, duration_minutes)
            self.stats_list_store = list_store  # Store reference for refresh functionality

            # Load stats from file
            if STATS_LOG_FILE.exists():
                try:
                    with open(STATS_LOG_FILE, 'r') as csvfile:
                        reader = csv.DictReader(csvfile)
                        rows = list(reader)
                        # Display in reverse order (most recent first)
                        for row in reversed(rows):
                            # Check if required fields exist
                            if 'timestamp' in row and 'duration_minutes' in row:
                                list_store.append([row['timestamp'], int(row['duration_minutes'])])
                            else:
                                pass  # Skip invalid rows silently
                except (IOError, KeyError, ValueError) as e:
                    pass  # Silently handle errors for cleaner UI

            tree_view = Gtk.TreeView(model=list_store)

            # Column 1: Timestamp
            renderer_timestamp = Gtk.CellRendererText()
            column_timestamp = Gtk.TreeViewColumn("Timestamp", renderer_timestamp, text=0)
            tree_view.append_column(column_timestamp)

            # Column 2: Duration
            renderer_duration = Gtk.CellRendererText()
            column_duration = Gtk.TreeViewColumn("Duration (minutes)", renderer_duration, text=1)
            tree_view.append_column(column_duration)

            scroll_window.add(tree_view)
            vbox.pack_start(scroll_window, True, True, 0)
            
            # Create button box
            button_box = Gtk.HBox()
            button_box.set_spacing(10)
            button_box.set_margin_top(10)
            button_box.set_margin_bottom(10)
            button_box.set_margin_start(10)
            button_box.set_margin_end(10)
            
            # Refresh button
            refresh_button = Gtk.Button(label="_Refresh Statistics")
            refresh_button.set_use_underline(True)
            refresh_button.connect("clicked", self._on_refresh_clicked)
            button_box.pack_start(refresh_button, False, False, 0)

            # Export to CSV button
            export_button = Gtk.Button(label="_Export to CSV")
            export_button.set_use_underline(True)
            export_button.connect("clicked", self._on_export_clicked)
            button_box.pack_start(export_button, False, False, 0)
            
            # Clear History button
            clear_button = Gtk.Button(label="_Clear History")
            clear_button.set_use_underline(True)
            clear_button.get_style_context().add_class("destructive-action") # Makes it red in many themes
            clear_button.connect("clicked", self._on_clear_history_clicked)
            button_box.pack_start(clear_button, False, False, 0)
            
            vbox.pack_start(button_box, False, False, 0)
            self._stats_window.add(vbox)
            self._stats_window.show_all()
        else:
            self._stats_window.present() # Bring existing window to front

    def on_stats_window_destroy(self, widget):
        """Callback for when the statistics window is destroyed."""
        self._stats_window = None # Clear the reference
        self.stats_list_store = None # Clear the reference

    def _on_refresh_clicked(self, widget):
        """Refresh the statistics display."""
        if self.stats_list_store and STATS_LOG_FILE.exists():
            # Clear the existing data
            self.stats_list_store.clear()
            
            # Reload stats from file
            try:
                with open(STATS_LOG_FILE, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    rows = list(reader)
                    # Display in reverse order (most recent first)
                    for row in reversed(rows):
                        # Check if required fields exist
                        if 'timestamp' in row and 'duration_minutes' in row:
                            self.stats_list_store.append([row['timestamp'], int(row['duration_minutes'])])
                        else:
                            print(f"Skipping invalid row during refresh: {row}")
            except (IOError, KeyError, ValueError) as e:
                print(f"Error loading stats file: {e}")

    def _on_export_clicked(self, widget):
        """Export statistics to a user-selected CSV file."""
        if not STATS_LOG_FILE.exists():
            dialog = Gtk.MessageDialog(
                transient_for=self._stats_window,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No statistics data to export."
            )
            dialog.run()
            dialog.destroy()
            return
            
        # Create a file chooser dialog
        dialog = Gtk.FileChooserDialog(
            title="Export Statistics to CSV",
            parent=self._stats_window,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT
        )
        dialog.set_current_name("teatime_statistics.csv")
        
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            try:
                # Copy the stats file to the selected location
                import shutil
                shutil.copy(STATS_LOG_FILE, filename)
                
                # Show success message
                success_dialog = Gtk.MessageDialog(
                    transient_for=self._stats_window,
                    modal=True,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Statistics successfully exported to {filename}"
                )
                success_dialog.run()
                success_dialog.destroy()
            except Exception as e:
                # Show error message
                error_dialog = Gtk.MessageDialog(
                    transient_for=self._stats_window,
                    modal=True,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error exporting statistics: {e}"
                )
                error_dialog.run()
                error_dialog.destroy()
        
        dialog.destroy()

    def _on_clear_history_clicked(self, widget):
        """Clear all statistics history."""
        # First confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self._stats_window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Are you sure you want to clear all statistics history?"
        )
        dialog.format_secondary_text("This action cannot be undone.")
        response = dialog.run()
        dialog.destroy()
        
        # If user confirmed the first time, show a second confirmation
        if response == Gtk.ResponseType.YES:
            # Second confirmation dialog
            dialog = Gtk.MessageDialog(
                transient_for=self._stats_window,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Are you absolutely sure? This will permanently delete all statistics."
            )
            dialog.format_secondary_text("Click Yes to confirm or No to cancel.")
            response = dialog.run()
            dialog.destroy()
            
            # If user confirmed the second time, proceed with clearing
            if response == Gtk.ResponseType.YES:
                # Clear the stats file
                try:
                    if STATS_LOG_FILE.exists():
                        STATS_LOG_FILE.unlink()
                    
                    # Clear the list store if it exists
                    if self.stats_list_store:
                        self.stats_list_store.clear()
                        
                    # Show success message
                    success_dialog = Gtk.MessageDialog(
                        transient_for=self._stats_window,
                        modal=True,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text="Statistics history cleared successfully."
                    )
                    success_dialog.run()
                    success_dialog.destroy()
                except Exception as e:
                    # Show error message
                    error_dialog = Gtk.MessageDialog(
                        transient_for=self._stats_window,
                        modal=True,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Error clearing statistics history: {e}"
                    )
                    error_dialog.run()
                    error_dialog.destroy()

    def _on_mini_mode_toggled(self, widget):
        """Handler for mini-mode toggle button."""
        self.mini_mode = self.mini_mode_toggle.get_active()
        self._apply_mini_mode()
        
    def _apply_mini_mode(self):
        """Apply mini-mode UI changes (photosensitive version - no visual effects)."""
        if not self.window:
            return
            
        if self.mini_mode:
            # Apply mini-mode - compact window size
            self.window.set_default_size(200, 100)
            self.window.resize(200, 100)
        else:
            # Apply normal mode
            self.window.set_default_size(300, 200)
            self.window.resize(300, 200)

    def _set_accessibility_properties(self):
        """
        Sets GTK 3 accessibility properties for better screen reader support.
        """
        # Removed set_role calls as they don't exist on these widgets
        pass

    def on_quit(self, action, param):
        """Handles the 'quit' action."""
        self.window.destroy()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Accessible Tea Timer")
    parser.add_argument("-d", "--duration", type=int, default=5,
                        help="Initial timer duration in minutes (default: 5)")
    args = parser.parse_args()

    app = TeaTimerApp(duration=args.duration)
    app.run(None)

if __name__ == "__main__":
    # Ensure locale is set for potential i18n or number formatting
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("Warning: Could not set locale.")
    main()