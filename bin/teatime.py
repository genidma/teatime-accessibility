#!/usr/bin/env python3

import time
import json
import locale
import subprocess
import os
from pathlib import Path
from datetime import datetime
import colorsys
import csv
import threading

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, Pango  # MOVE THIS LINE HERE

import argparse

# Add after imports, before the class:
parser = argparse.ArgumentParser(description='Accessible Tea Timer')
parser.add_argument('--duration', type=int, default=5, help='Timer duration in minutes (1-999)')
args = parser.parse_args()

# Application metadata
APP_NAME = "Accessible Tea Timer"
APP_VERSION = "1.3.3"

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
STATS_LOG_FILE = Path.home() / ".local/share/teatime_stats.json"
DEFAULT_FONT_SCALE = 1.5
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 6.0

class TeaTimerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.current_timer_duration = 0
        self.font_scale_factor = DEFAULT_FONT_SCALE
        self.last_duration = args.duration  # Default duration from config
        self.sound_enabled = True
        self.rainbow_timer_id = None
        self.css_provider = Gtk.CssProvider()
        self.rainbow_hue = 0
        self._stats_window = None
        self.focus_hue = 0 # Hue for the focus glow, 0-359
        self._load_config()  # Load settings from file
        # Set up keyboard shortcuts
        self._setup_actions()

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

            # --- HeaderBar for a modern look ---
            header_bar = Gtk.HeaderBar()
            header_bar.set_show_close_button(True)
            header_bar.props.title = APP_NAME
            self.window.set_titlebar(header_bar)

            # Create a menu for the "About" option
            about_menu = Gtk.Menu()
            stats_item = Gtk.MenuItem(label="Statistics")
            stats_item.connect("activate", self.on_stats_activated)
            about_item = Gtk.MenuItem(label="About")
            about_item.connect("activate", self.on_about_activated)
            about_menu.append(stats_item)
            about_menu.append(about_item)
            about_menu.show_all()

            # Create a menu button and add it to the header bar
            menu_button = Gtk.MenuButton(popup=about_menu)
            icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
            menu_button.add(icon)
            header_bar.pack_end(menu_button)

            # Create main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
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
            font_desc = Pango.FontDescription("Sans Bold 24")
            self.duration_spin.override_font(font_desc)
            grid.attach(duration_label, 0, 0, 1, 1)
            grid.attach(self.duration_spin, 1, 0, 1, 1)

            # Row 1: Control buttons
            self.start_button = Gtk.Button(label="Start")
            self.stop_button = Gtk.Button(label="Stop")
            grid.attach(self.start_button, 0, 1, 1, 1)
            grid.attach(self.stop_button, 1, 1, 1, 1)

            # Row 2: Font size controls
            self.decrease_font_button = Gtk.Button(label="A-")
            self.increase_font_button = Gtk.Button(label="A+")
            grid.attach(self.decrease_font_button, 0, 2, 1, 1)
            grid.attach(self.increase_font_button, 1, 2, 1, 1)

            # Row 3: Sound toggle (spans both columns)
            self.sound_toggle = Gtk.CheckButton(label="Enable Sound")
            self.sound_toggle.set_active(self.sound_enabled)
            grid.attach(self.sound_toggle, 0, 3, 2, 1)

            # --- Presets Box (RIGHT SIDE) ---
            presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            presets_box.set_valign(Gtk.Align.CENTER)
            content_box.pack_start(presets_box, False, False, 0)

            presets_label = Gtk.Label(label="<span size='large'><b>Session Presets</b></span>")
            presets_label.set_use_markup(True)
            presets_box.pack_start(presets_label, False, False, 0)

            preset_45_button = Gtk.Button(label="45 Minutes")
            preset_45_button.connect("clicked", self.on_preset_clicked, 45)
            presets_box.pack_start(preset_45_button, False, False, 0)

            preset_1_hour_button = Gtk.Button(label="1 Hour")
            preset_1_hour_button.connect("clicked", self.on_preset_clicked, 60)
            presets_box.pack_start(preset_1_hour_button, False, False, 0)

            self.window.add(main_box)

            # Connect signals
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            self.increase_font_button.connect("clicked", self.on_increase_font_clicked)
            self.decrease_font_button.connect("clicked", self.on_decrease_font_clicked)
            self.sound_toggle.connect("toggled", self.on_sound_toggled)

            # Add the single CSS provider to the screen. We will update this provider
            # later instead of adding new ones.
            screen = Gdk.Screen.get_default()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(
                    screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            else:
                print("Warning: No default screen found to apply CSS.")

            # Initial state for buttons
            self.stop_button.set_sensitive(False)

            # Apply initial font size
            self._apply_font_size()

            # Add a style class to the time label for specific targeting
            self.time_label.get_style_context().add_class("time-display")

            # Set GTK 3 accessibility properties (after all widgets are created)
            self._set_accessibility_properties()

        self.window.show_all()

    def _on_window_destroy(self, widget):
        """Handle window destruction properly."""
        self._save_config() # Save settings on exit

        # Clean up timers
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
            self.rainbow_timer_id = None
        
        # Close stats window if open
        if self._stats_window:
            self._stats_window.destroy()
        
        # Quit the application
        self.quit()

    def _on_focus_changed(self, container, widget):
        """Cycles the focus glow color when the focused widget changes."""
        # This signal reliably fires when a new child widget gets focus.
        self.focus_hue = (self.focus_hue + 40) % 360 # Cycle through the hue spectrum
        self._apply_font_size() # Re-apply CSS with the new color

    def on_about_activated(self, widget):
        """Shows the About dialog."""
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.set_program_name(APP_NAME)
        about_dialog.set_version(APP_VERSION)
        about_dialog.set_copyright("Copyright © 2024 Adeel Khan")
        about_dialog.set_comments("A simple and accessible tea timer.")
        about_dialog.set_website("https://github.com/genidma/teatime-accessibility")
        # Giving credit where it's due!
        about_dialog.set_authors([
            "Adeel Khan (GitHub: genidma)",
            "Initial script by Claude AI",
            "Refinements by Gemini",
            "Sound by Daniel Simion, https://soundbible.com/2218-Service-Bell-Help.html"
        ])
        about_dialog.set_logo_icon_name("accessories-clock")
        about_dialog.run()
        about_dialog.destroy()

    def on_stats_activated(self, widget):
        """Shows the Statistics window."""
        # Create a new StatisticsWindow instance
        # if the window doesn't exist yet, create it.
        if self._stats_window is None:
            self._stats_window = StatisticsWindow(application=self, parent=self.window)

        # Present the window, which shows it and brings it to the front.
        self._stats_window.present()

    def _play_notification_sound(self):
        """Play a sound notification when timer finishes."""
        if not self.sound_enabled:
            return
            
        def play_sound_task():
            """Defines and tries different strategies to play a sound."""
            sound_files = [
                "service-bell_daniel_simion.wav",
            ]

            def strategy_paplay():
                for sound_file in sound_files:
                    if os.path.exists(sound_file):
                        try:
                            result = subprocess.run(["paplay", sound_file], 
                                                  capture_output=True, timeout=5)
                            if result.returncode == 0:
                                return True
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            continue
                return False

            def strategy_aplay():
                for sound_file in sound_files:
                    if os.path.exists(sound_file):
                        try:
                            result = subprocess.run(["aplay", sound_file], 
                                                  capture_output=True, timeout=5)
                            if result.returncode == 0:
                                return True
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            continue
                return False

            def strategy_system_beep():
                # A simple, reliable fallback
                try:
                    print("\a", end="", flush=True)
                    return True
                except:
                    return False

            strategies = [strategy_paplay, strategy_aplay, strategy_system_beep]

            for strategy in strategies:
                try:
                    if strategy():
                        print(f"Sound played using: {strategy.__name__}")
                        return
                except Exception as e:
                    print(f"Strategy {strategy.__name__} failed: {e}")
                    continue
            print("Could not play any notification sound.")
        
        # Play sound in separate thread to avoid blocking UI
        threading.Thread(target=play_sound_task, daemon=True).start()

    def _set_accessibility_properties(self):
        """Set accessibility properties using GTK 3 methods."""
        # Set accessible names and descriptions using GTK 3 methods
        try:
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_name("Timer Display")
                accessible.set_description("Displays the remaining time for the tea timer")

            accessible = self.start_button.get_accessible()
            if accessible:
                accessible.set_name("Start Tea Timer")
                accessible.set_description("Start the tea brewing timer")

            accessible = self.stop_button.get_accessible()
            if accessible:
                accessible.set_name("Stop Tea Timer")
                accessible.set_description("Stop the tea brewing timer")

            accessible = self.duration_spin.get_accessible()
            if accessible:
                accessible.set_name("Tea brewing duration")
                accessible.set_description("Set the tea brewing duration in minutes")

            accessible = self.increase_font_button.get_accessible()
            if accessible:
                accessible.set_name("Increase Font Size")
                accessible.set_description("Make the text larger")

            accessible = self.decrease_font_button.get_accessible()
            if accessible:
                accessible.set_name("Decrease Font Size")
                accessible.set_description("Make the text smaller")

            accessible = self.sound_toggle.get_accessible()
            if accessible:
                accessible.set_name("Sound Toggle")
                accessible.set_description("Enable or disable sound notifications")
        except Exception as e:
            print(f"Warning: Could not set accessibility properties: {e}")

    def _setup_actions(self):
        """Sets up application-level actions and keyboard shortcuts."""
        # Start action
        start_action = Gio.SimpleAction.new("start", None)
        start_action.connect("activate", self.on_start_clicked)
        self.add_action(start_action)
        self.set_accels_for_action("app.start", ["<Control>s"])

        # Stop action
        stop_action = Gio.SimpleAction.new("stop", None)
        stop_action.connect("activate", self.on_stop_clicked)
        self.add_action(stop_action)
        self.set_accels_for_action("app.stop", ["<Control>t"]) # 't' for sTop

        # Increase font action
        increase_action = Gio.SimpleAction.new("increase-font", None)
        increase_action.connect("activate", self.on_increase_font_clicked)
        self.add_action(increase_action)
        # 'plus' and 'equal' are often the same physical key
        self.set_accels_for_action("app.increase-font", ["<Control>plus", "<Control>equal"])

        # Decrease font action
        decrease_action = Gio.SimpleAction.new("decrease-font", None)
        decrease_action.connect("activate", self.on_decrease_font_clicked)
        self.add_action(decrease_action)
        self.set_accels_for_action("app.decrease-font", ["<Control>minus"])

        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda a, p: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

    def _load_config(self):
        """Loads configuration from the config file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Load font scale
                    scale = config.get("font_scale_factor", DEFAULT_FONT_SCALE)
                    self.font_scale_factor = max(MIN_FONT_SCALE, min(MAX_FONT_SCALE, scale))
                    # Load last duration
                    self.last_duration = config.get("last_duration", 5)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error decoding config file: {CONFIG_FILE}. Using defaults. Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while loading config: {e}. Using defaults.")

    def _save_config(self):
        """Saves the current configuration to the config file."""
        if not self.window:  # Don't save if window wasn't created
            return
        try:
            config_data = {
                "font_scale_factor": self.font_scale_factor,
                "last_duration": self.duration_spin.get_value_as_int()
            }
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def _apply_font_size(self):
        """Applies the current font scale factor using CSS."""
        try:
            # Define multipliers for a clear visual hierarchy
            timer_font_multiplier = 2.5   # 250% of the base scale
            control_font_multiplier = 1.2 # 120% for general controls like labels and buttons

            timer_font_percentage = self.font_scale_factor * timer_font_multiplier * 100
            control_font_percentage = self.font_scale_factor * control_font_multiplier * 100

            # Calculate focus glow color from the current hue
            fr, fg, fb = colorsys.hsv_to_rgb(self.focus_hue / 360.0, 0.9, 1.0)
            glow_rgba = f"rgba({int(fr*255)}, {int(fg*255)}, {int(fb*255)}, 0.8)"
            border_rgb = f"rgb({int(fr*255)}, {int(fg*255)}, {int(fb*255)})"

            css = f"""
            /* Target the main timer display to make it large and scalable */
            .time-display {{
                font-size: {timer_font_percentage}%;
                font-weight: bold;
            }}

            /* Apply a larger font to general controls for better readability */
            .input-label, button label, checkbutton label {{
                font-size: {control_font_percentage}%;
            }}

            /* Add a smooth transition to the focus glow */
            button,
            checkbutton,
            spinbutton {{
                transition: box-shadow 0.2s ease-in-out, border-color 0.2s ease-in-out;
            }}

            /* Add a glow effect to focused widgets for better keyboard navigation visibility */
            button:focus,
            checkbutton:focus,
            spinbutton:focus {{
                outline: none; /* Remove the default dotted outline */
                box-shadow: 0 0 8px 3px {glow_rgba}; /* A nice rainbow glow */
                border-color: {border_rgb}; /* A matching border color for consistency */
            }}
            """
            
            # Add rainbow effect (always calculated, but only applied if class is present)
            r, g, b = colorsys.hsv_to_rgb(self.rainbow_hue / 360.0, 1.0, 1.0)
            color = f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"
            css += f"""
                .rainbow-text {{
                    color: {color};
                }}
                """
            self.css_provider.load_from_data(css.encode())
        except Exception as e:
            print(f"Error applying font size: {e}")

    def _update_font_size_announcement(self):
        """Updates the accessible description for the font size buttons."""
        try:
            description = f"Font size is now {int(self.font_scale_factor * 100)} percent of normal."
            
            # Update accessibility description for GTK 3
            accessible = self.increase_font_button.get_accessible()
            if accessible:
                accessible.set_description(description)
            
            accessible = self.decrease_font_button.get_accessible()
            if accessible:
                accessible.set_description(description)
        except Exception as e:
            print(f"Warning: Could not update font size announcement: {e}")

    def on_increase_font_clicked(self, *args):
        """Increases the font size."""
        if self.font_scale_factor < MAX_FONT_SCALE:
            self.font_scale_factor = min(MAX_FONT_SCALE, self.font_scale_factor + FONT_SCALE_INCREMENT)
            self._apply_font_size()
            self._save_config()
            print(f"Increased font to: {self.font_scale_factor:.1f}x")
            self._update_font_size_announcement()

    def on_decrease_font_clicked(self, *args):
        """Decreases the font size."""
        if self.font_scale_factor > MIN_FONT_SCALE:
            self.font_scale_factor = max(MIN_FONT_SCALE, self.font_scale_factor - FONT_SCALE_INCREMENT)
            self._apply_font_size()
            self._save_config()
            print(f"Decreased font to: {self.font_scale_factor:.1f}x")
            self._update_font_size_announcement()

    def on_sound_toggled(self, button):
        """Toggle sound notifications on/off."""
        self.sound_enabled = button.get_active()
        status = "enabled" if self.sound_enabled else "disabled"
        print(f"Sound notifications {status}")

    def _start_rainbow_timer(self):
        """Start the rainbow color cycling timer."""
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
        self.rainbow_timer_id = GLib.timeout_add(100, self._update_rainbow)

    def _stop_rainbow_timer(self):
        """Stop the rainbow color cycling timer."""
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
            self.rainbow_timer_id = None

    def _update_rainbow(self):
        """Update the rainbow color effect."""
        self.rainbow_hue = (self.rainbow_hue + 5) % 360
        self._apply_font_size()
        return GLib.SOURCE_CONTINUE

    def on_start_clicked(self, *args):
        # Stop any previous rainbow effect
        self._stop_rainbow_timer()
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size() # Reset color

        self.time_left = int(self.duration_spin.get_value()) * 60
        self.current_timer_duration = self.duration_spin.get_value()
        self.start_timer()
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        print("Timer started")
        
        # Update time display
        self.time_label.set_markup(f"<span>{self.time_left // 60:02d}:{self.time_left % 60:02d}</span>")
        
        # Update accessibility description
        try:
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_description(f"Tea timer started for {self.duration_spin.get_value()} minutes.")
        except Exception as e:
            print(f"Warning: Could not update accessibility description: {e}")

    def on_stop_clicked(self, *args):
        # Stop any rainbow effect
        self._stop_rainbow_timer()
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size() # Reset color

        self.stop_timer()
        self.time_left = 0
        self.time_label.set_markup("<span>00:00</span>")
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        print("Timer stopped")
        
        # Update accessibility description
        try:
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_description("Tea timer stopped and reset.")
        except Exception as e:
            print(f"Warning: Could not update accessibility description: {e}")

    def start_timer(self):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
        self.timer_id = GLib.timeout_add_seconds(1, self.update_timer)

    def stop_timer(self):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        self.time_left -= 1
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.set_markup(f"<span>{minutes:02d}:{seconds:02d}</span>")
        
        # Update accessibility description at key moments
        if self.time_left % 10 == 0 or self.time_left <= 5:
            try:
                accessible = self.time_label.get_accessible()
                if accessible:
                    accessible.set_description(f"Time remaining: {minutes} minutes and {seconds} seconds.")
            except Exception as e:
                print(f"Warning: Could not update accessibility description: {e}")

        if self.time_left <= 0:
            self.stop_timer()
            self.time_label.set_markup("<span>Session Complete</span>")
            
            # Start the celebratory rainbow effect!
            self.time_label.get_style_context().add_class("rainbow-text")
            self._start_rainbow_timer()

            # Play notification sound
            self._play_notification_sound()
            
            # Log the completed timer
            self._log_timer_completion()
            
            try:
                accessible = self.time_label.get_accessible()
                if accessible:
                    accessible.set_description("Tea is ready! The timer has finished.")
            except Exception as e:
                print(f"Warning: Could not update accessibility description: {e}")
            
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            print("Tea is ready!")
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _log_timer_completion(self):
        """Logs a completed timer session to the stats file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "duration": self.current_timer_duration
        }
        
        try:
            STATS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            if STATS_LOG_FILE.exists():
                with open(STATS_LOG_FILE, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Remove duplicates based on timestamp
            unique_logs = {log['timestamp']: log for log in reversed(logs)}
            logs = list(unique_logs.values())
            
            logs.append(log_entry)
            
            with open(STATS_LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
            print(f"Logged timer: {log_entry['duration']} minutes.")
            
        except Exception as e:
            print(f"Error logging statistics: {e}")

    def on_preset_clicked(self, button, minutes):
        """Sets the duration spin button to a preset value and starts the timer."""
        self.duration_spin.set_value(minutes)
        print(f"Preset selected: {minutes} minutes. Starting timer automatically.")
        # Automatically start the timer
        self.on_start_clicked()


class StatisticsWindow(Gtk.Window):
    def __init__(self, application, parent):
        super().__init__(title="Timer Statistics", application=application)
        self.set_default_size(400, 300)
        self.set_transient_for(parent)
        self.set_modal(False)
        
        # Handle window close properly
        self.connect("delete-event", self._on_delete_event)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.add(main_box)

        # Summary Labels
        self.summary_grid = Gtk.Grid(column_spacing=10, row_spacing=5, margin=10)
        self.total_breaks_label = Gtk.Label(label="Total Breaks: 0")
        self.total_time_label = Gtk.Label(label="Total Time: 0 minutes")
        self.avg_duration_label = Gtk.Label(label="Average Duration: 0 minutes")
        self.summary_grid.attach(self.total_breaks_label, 0, 0, 1, 1)
        self.summary_grid.attach(self.total_time_label, 1, 0, 1, 1)
        self.summary_grid.attach(self.avg_duration_label, 0, 1, 2, 1)
        main_box.pack_start(self.summary_grid, False, False, 0)

        # TreeView for detailed logs
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scrolled_window, True, True, 0)
        
        # --- Button Box ---
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, halign=Gtk.Align.CENTER)
        main_box.pack_start(button_box, False, False, 0)

        # Refresh button
        refresh_button = Gtk.Button(label="Refresh Statistics")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        button_box.pack_start(refresh_button, False, False, 0)

        # Export to CSV button
        export_button = Gtk.Button(label="Export to CSV")
        export_button.connect("clicked", self._on_export_clicked)
        button_box.pack_start(export_button, False, False, 0)

        # Clear History button
        clear_button = Gtk.Button(label="Clear History")
        clear_button.get_style_context().add_class("destructive-action") # Makes it red in many themes
        clear_button.connect("clicked", self._on_clear_history_clicked)
        button_box.pack_start(clear_button, False, False, 0)

        button_box.set_margin_top(10)
        
        # Model: Date (string), Duration (int)
        self.store = Gtk.ListStore(str, int)
        self.treeview = Gtk.TreeView(model=self.store)

        # Date Column
        renderer_text = Gtk.CellRendererText()
        column_date = Gtk.TreeViewColumn("Date", renderer_text, text=0)
        column_date.set_sort_column_id(0)
        column_date.set_resizable(True)
        self.treeview.append_column(column_date)

        # Duration Column
        renderer_text = Gtk.CellRendererText()
        column_duration = Gtk.TreeViewColumn("Duration (minutes)", renderer_text, text=1)
        column_duration.set_sort_column_id(1)
        column_duration.set_resizable(True)
        self.treeview.append_column(column_duration)

        scrolled_window.add(self.treeview)
        self._load_stats()

        # Make all widgets inside the window visible
        self.show_all()

    def _on_delete_event(self, widget, event):
        """Handle window close event."""
        self.hide()
        return True  # Prevent actual destruction

    def _on_export_clicked(self, button):
        """Handles exporting the statistics to a CSV file."""
        if len(self.store) == 0:
            info_dialog = Gtk.MessageDialog(
                transient_for=self, modal=True, message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK, text="No Statistics to Export",
            )
            info_dialog.format_secondary_text("The statistics log is currently empty.")
            info_dialog.run()
            info_dialog.destroy()
            return

        dialog = Gtk.FileChooserDialog(
            title="Save Statistics as CSV",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT
        )

        # Suggest a filename
        today_str = datetime.now().strftime("%Y-%m-%d")
        dialog.set_current_name(f"teatime_stats_{today_str}.csv")

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            if not filename.lower().endswith(".csv"):
                filename += ".csv"
            
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(["Timestamp", "Duration (minutes)"])
                    # Write data from the ListStore
                    for row in self.store:
                        writer.writerow([row[0], row[1]])
                
                success_dialog = Gtk.MessageDialog(
                    transient_for=self, modal=True, message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK, text="Export Successful",
                )
                success_dialog.format_secondary_text(f"Statistics saved to:\n{filename}")
                success_dialog.run()
                success_dialog.destroy()

            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK, text="Export Failed",
                )
                error_dialog.format_secondary_text(f"Could not save the file.\nError: {e}")
                error_dialog.run()
                error_dialog.destroy()

        dialog.destroy()

    def _on_clear_history_clicked(self, button):
        """Handles the first confirmation dialog for clearing history."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear All Timer Statistics?",
        )
        dialog.format_secondary_text(
            "This will permanently delete all recorded timer sessions. This action cannot be undone."
        )
        
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self._show_second_confirmation()

    def _show_second_confirmation(self):
        """Handles the second, final confirmation dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING, # Use WARNING for more emphasis
            buttons=Gtk.ButtonsType.YES_NO,
            text="Are You Absolutely Sure?",
        )
        dialog.format_secondary_text(
            "This is the final confirmation. Pressing 'Yes' will erase all statistics forever."
        )
        
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self._perform_clear_history()

    def _perform_clear_history(self):
        """Deletes the stats file and clears the view."""
        try:
            if STATS_LOG_FILE.exists():
                STATS_LOG_FILE.unlink() # Use unlink() from pathlib
            
            # Clear the model which updates the TreeView
            self.store.clear()
            
            # Reset the summary labels
            self._reset_summary_labels()
            
            print("Statistics history has been cleared.")
            
        except Exception as e:
            print(f"Error clearing statistics: {e}")
            error_dialog = Gtk.MessageDialog(
                transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK, text="Failed to Clear History",
            )
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()

    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        print("Refreshing statistics...")
        self._load_stats()

    def _reset_summary_labels(self):
        """Resets the summary labels to their default state."""
        self.total_breaks_label.set_text("Total Breaks: 0")
        self.total_time_label.set_text("Total Time: 0 minutes")
        self.avg_duration_label.set_text("Average Duration: 0 minutes")

    def _load_stats(self):
        """Load statistics from the log file."""
        if not STATS_LOG_FILE.exists():
            self.store.clear()
            self._reset_summary_labels()
            return

        try:
            with open(STATS_LOG_FILE, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        # Clear existing data
        self.store.clear()
        
        total_duration = 0

        # Sort logs by timestamp correctly using datetime objects
        def get_datetime(log):
            """Helper function to convert log timestamp to datetime object."""
            timestamp_str = log.get("timestamp", "")
            try:
                return datetime.fromisoformat(timestamp_str)
            except ValueError:
                return datetime.min  # Use minimum datetime for invalid timestamps

        # Sort logs by timestamp (newest first) for display
        sorted_logs = sorted(logs, key=get_datetime, reverse=True)

        for log in sorted_logs:
            timestamp_str = log.get("timestamp", "")
            duration = log.get("duration", 0)

            try:
                dt_object = datetime.fromisoformat(timestamp_str)
                friendly_date = dt_object.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                friendly_date = timestamp_str  # Use raw string if parsing fails

            # Append to the store. This is more efficient than insert(0, ...)
            # and since we sorted newest-first, this will display newest-first.
            self.store.append([friendly_date, duration])
            total_duration += duration

        # Update summary
        self.total_breaks_label.set_text(f"Total Breaks: {len(sorted_logs)}")
        self.total_time_label.set_text(f"Total Time: {total_duration} minutes")
        if sorted_logs:
            avg_duration = total_duration / len(sorted_logs)
            self.avg_duration_label.set_text(f"Average Duration: {avg_duration:.1f} minutes")
        else:
            self._reset_summary_labels()

if __name__ == "__main__":
    import sys
    app = TeaTimerApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)