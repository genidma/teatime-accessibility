#!/usr/bin/env python3

import time
import json
import locale
import subprocess
import os
from pathlib import Path
from datetime import datetime
import colorsys
import threading

# Attempt to import playsound, but don't fail if it's not installed
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk

# Application metadata
APP_NAME = "Accessible Tea Timer"
APP_VERSION = "1.3.0"

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
STATS_LOG_FILE = Path.home() / ".local/share/teatime_stats.json"
DEFAULT_FONT_SCALE = 1.0
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 2.0

class TeaTimerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE | Gio.ApplicationFlags.NON_UNIQUE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.current_timer_duration = 0
        self.font_scale_factor = self._load_font_scale()
        self.sound_enabled = True
        self.rainbow_timer_id = None
        self.rainbow_hue = 0
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

            # --- HeaderBar for a modern look ---
            header_bar = Gtk.HeaderBar()
            header_bar.set_show_close_button(True)
            header_bar.props.title = APP_NAME
            self.window.set_titlebar(header_bar)

            # Create a menu for the "About" option
            about_menu = Gtk.Menu()
            about_item = Gtk.MenuItem(label="About")
            about_item.connect("activate", self.on_about_activated)
            stats_item = Gtk.MenuItem(label="Statistics")
            stats_item.connect("activate", self.on_stats_activated)
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

            # Time display
            self.time_label = Gtk.Label(label="00:00")
            self.time_label.set_markup("<span size='xx-large'>00:00</span>")
            main_box.pack_start(self.time_label, False, False, 0)

            # --- Use a Grid for a clean, aligned layout ---
            grid = Gtk.Grid()
            grid.set_column_spacing(10)
            grid.set_row_spacing(10)
            grid.set_halign(Gtk.Align.CENTER) # Center the grid horizontally
            main_box.pack_start(grid, False, False, 0)

            # Row 0: Duration selection
            duration_label = Gtk.Label(label="Minutes:")
            self.duration_spin = Gtk.SpinButton.new_with_range(1, 999, 1)
            self.duration_spin.set_width_chars(3) # Ensure it's wide enough for 3 digits
            self.duration_spin.set_value(5)
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

            self.window.add(main_box)

            # Connect signals
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            self.increase_font_button.connect("clicked", self.on_increase_font_clicked)
            self.decrease_font_button.connect("clicked", self.on_decrease_font_clicked)
            self.sound_toggle.connect("toggled", self.on_sound_toggled)

            # Initial state for buttons
            self.stop_button.set_sensitive(False)

            # Apply initial font size
            self._apply_font_size()

            # Add a style class to the time label for specific targeting
            self.time_label.get_style_context().add_class("time-display")

            # Set GTK 3 accessibility properties (after all widgets are created)
            self._set_accessibility_properties()

        self.window.show_all()

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
            "Refinements by Gemini"
        ])
        about_dialog.set_logo_icon_name("accessories-clock")
        about_dialog.run()
        about_dialog.destroy()

    def on_stats_activated(self, widget):
        """Shows the Statistics dialog."""
        stats_dialog = StatisticsWindow(parent=self.window)
        stats_dialog.run()
        stats_dialog.destroy()
    def _play_notification_sound(self):
        """Play a sound notification when timer finishes."""
        if not self.sound_enabled:
            return
            
        def play_sound_task():
            """Defines and tries different strategies to play a sound."""
            sound_files = [
                "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "/usr/share/sounds/freedesktop/stereo/bell.oga",
                "/usr/share/sounds/ubuntu/stereo/notification.ogg",
            ]

            def strategy_playsound():
                if not PLAYSOUND_AVAILABLE:
                    return False
                for sound_file in sound_files:
                    if os.path.exists(sound_file):
                        playsound(sound_file)
                        return True
                return False

            def strategy_paplay():
                for sound_file in sound_files:
                    if os.path.exists(sound_file):
                        result = subprocess.run(["paplay", sound_file], capture_output=True)
                        if result.returncode == 0:
                            return True
                return False

            def strategy_system_beep():
                # A simple, reliable fallback
                print("\a", flush=True)
                return True

            strategies = [strategy_playsound, strategy_paplay, strategy_system_beep]

            for strategy in strategies:
                if strategy():
                    print(f"Sound played using: {strategy.__name__}")
                    return
            print("Could not play any notification sound.")
        
        # Play sound in separate thread to avoid blocking UI
        threading.Thread(target=play_sound_task, daemon=True).start()

    def _set_accessibility_properties(self):
        """Set accessibility properties using GTK 3 methods."""
        # Set accessible names and descriptions using GTK 3 methods
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

    def _load_font_scale(self):
        """Loads the font scale factor from the config file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get("font_scale_factor", DEFAULT_FONT_SCALE)
            except json.JSONDecodeError:
                print(f"Error decoding config file: {CONFIG_FILE}. Using default font scale.")
            except Exception as e:
                print(f"An unexpected error occurred while loading config: {e}. Using default font scale.")
        return DEFAULT_FONT_SCALE

    def _save_font_scale(self):
        """Saves the current font scale factor to the config file."""
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"font_scale_factor": self.font_scale_factor}, f)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def _apply_font_size(self):
        """Applies the current font scale factor using CSS."""
        css_provider = Gtk.CssProvider()
        
        # Base CSS for font size
        css = f"""
        * {{
            font-size: {self.font_scale_factor * 100}%;
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
        
        css_provider.load_from_data(css.encode())

        # Get the default screen and add the CSS provider
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        else:
            print("Warning: No default screen found to apply CSS.")

    def _update_font_size_announcement(self):
        """Updates the accessible description for the font size buttons."""
        description = f"Font size is now {int(self.font_scale_factor * 100)} percent of normal."
        
        # Update accessibility description for GTK 3
        accessible = self.increase_font_button.get_accessible()
        if accessible:
            accessible.set_description(description)
        
        accessible = self.decrease_font_button.get_accessible()
        if accessible:
            accessible.set_description(description)

    def on_increase_font_clicked(self, *args):
        """Increases the font size."""
        if self.font_scale_factor < MAX_FONT_SCALE:
            self.font_scale_factor += FONT_SCALE_INCREMENT
            self._apply_font_size()
            self._save_font_scale()
            print(f"Increased font to: {self.font_scale_factor:.1f}x")
            self._update_font_size_announcement()

    def on_decrease_font_clicked(self, *args):
        """Decreases the font size."""
        if self.font_scale_factor > MIN_FONT_SCALE:
            self.font_scale_factor -= FONT_SCALE_INCREMENT
            self._apply_font_size()
            self._save_font_scale()
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
        self.time_label.set_markup(f"<span size='xx-large'>{self.time_left // 60:02d}:{self.time_left % 60:02d}</span>")
        
        # Update accessibility description
        accessible = self.time_label.get_accessible()
        if accessible:
            accessible.set_description(f"Tea timer started for {self.duration_spin.get_value()} minutes.")

    def on_stop_clicked(self, *args):
        # Stop any rainbow effect
        self._stop_rainbow_timer()
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size() # Reset color

        self.stop_timer()
        self.time_left = 0
        self.time_label.set_markup("<span size='xx-large'>00:00</span>")
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        print("Timer stopped")
        
        # Update accessibility description
        accessible = self.time_label.get_accessible()
        if accessible:
            accessible.set_description("Tea timer stopped and reset.")

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
        self.time_label.set_markup(f"<span size='xx-large'>{minutes:02d}:{seconds:02d}</span>")
        
        # Update accessibility description at key moments
        if self.time_left % 10 == 0 or self.time_left <= 5:
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_description(f"Time remaining: {minutes} minutes and {seconds} seconds.")

        if self.time_left <= 0:
            self.stop_timer()
            self.time_label.set_markup("<span size='xx-large'>Tea Ready!</span>")
            
            # Start the celebratory rainbow effect!
            self.time_label.get_style_context().add_class("rainbow-text")
            self._start_rainbow_timer()

            # Play notification sound
            self._play_notification_sound()
            
            # Log the completed timer
            self._log_timer_completion()
            
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_description("Tea is ready! The timer has finished.")
            
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
            
            logs.append(log_entry)
            
            with open(STATS_LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
            
            print(f"Logged timer: {log_entry['duration']} minutes.")
            
        except Exception as e:
            print(f"Error logging statistics: {e}")


class StatisticsWindow(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Timer Statistics", transient_for=parent, flags=0)
        self.add_buttons("Close", Gtk.ResponseType.CLOSE)
        self.set_default_size(400, 300)

        box = self.get_content_area()
        
        # Summary Labels
        self.summary_grid = Gtk.Grid(column_spacing=10, row_spacing=5, margin=10)
        self.total_breaks_label = Gtk.Label(label="Total Breaks: 0")
        self.total_time_label = Gtk.Label(label="Total Time: 0 minutes")
        self.avg_duration_label = Gtk.Label(label="Average Duration: 0 minutes")
        self.summary_grid.attach(self.total_breaks_label, 0, 0, 1, 1)
        self.summary_grid.attach(self.total_time_label, 1, 0, 1, 1)
        self.summary_grid.attach(self.avg_duration_label, 0, 1, 2, 1)
        box.pack_start(self.summary_grid, False, False, 0)

        # TreeView for detailed logs
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        box.pack_start(scrolled_window, True, True, 0)

        # Model: Date (string), Duration (int)
        self.store = Gtk.ListStore(str, int)
        self.treeview = Gtk.TreeView(model=self.store)

        # Date Column
        renderer_text = Gtk.CellRendererText()
        column_date = Gtk.TreeViewColumn("Date", renderer_text, text=0)
        column_date.set_sort_column_id(0)
        self.treeview.append_column(column_date)

        # Duration Column
        renderer_text = Gtk.CellRendererText()
        column_duration = Gtk.TreeViewColumn("Duration (minutes)", renderer_text, text=1)
        column_duration.set_sort_column_id(1)
        self.treeview.append_column(column_duration)

        scrolled_window.add(self.treeview)
        self._load_stats()
        self.show_all()

    def _load_stats(self):
        if not STATS_LOG_FILE.exists():
            return

        try:
            with open(STATS_LOG_FILE, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not read statistics file: {e}")
            return

        total_duration = 0
        for log in logs:
            timestamp_str = log.get("timestamp")
            duration = log.get("duration", 0)
            dt_object = datetime.fromisoformat(timestamp_str)
            friendly_date = dt_object.strftime("%Y-%m-%d %H:%M")
            self.store.append([friendly_date, duration])
            total_duration += duration

        # Update summary
        self.total_breaks_label.set_text(f"Total Breaks: {len(logs)}")
        self.total_time_label.set_text(f"Total Time: {total_duration} minutes")
        if logs:
            avg_duration = total_duration / len(logs)
            self.avg_duration_label.set_text(f"Average Duration: {avg_duration:.1f} minutes")

if __name__ == "__main__":
    import sys
    app = TeaTimerApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)