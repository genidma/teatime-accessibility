#!/usr/bin/env python3

import time
import json
import locale
import subprocess
import os
from pathlib import Path
import threading

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
DEFAULT_FONT_SCALE = 1.0
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 2.0

class TeaTimerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.font_scale_factor = self._load_font_scale()
        self.sound_enabled = True

    def do_activate(self):
        """
        This method is called when the application is activated.
        """
        if not self.window:
            # Create window programmatically since UI file might not exist
            self.window = Gtk.ApplicationWindow(application=self)
            self.window.set_title("Tea Timer")
            self.window.set_default_size(300, 200)

            # Create main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            main_box.set_margin_top(20)
            main_box.set_margin_bottom(20)
            main_box.set_margin_left(20)
            main_box.set_margin_right(20)

            # Time display
            self.time_label = Gtk.Label(label="00:00")
            self.time_label.set_markup("<span size='xx-large'>00:00</span>")
            main_box.pack_start(self.time_label, False, False, 0)

            # Duration selection
            duration_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            duration_label = Gtk.Label(label="Minutes:")
            self.duration_spin = Gtk.SpinButton.new_with_range(1, 60, 1)
            self.duration_spin.set_value(5)
            duration_box.pack_start(duration_label, False, False, 0)
            duration_box.pack_start(self.duration_spin, False, False, 0)
            main_box.pack_start(duration_box, False, False, 0)

            # Control buttons
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.start_button = Gtk.Button(label="Start")
            self.stop_button = Gtk.Button(label="Stop")
            button_box.pack_start(self.start_button, True, True, 0)
            button_box.pack_start(self.stop_button, True, True, 0)
            main_box.pack_start(button_box, False, False, 0)

            # Font size controls
            font_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.decrease_font_button = Gtk.Button(label="A-")
            self.increase_font_button = Gtk.Button(label="A+")
            font_box.pack_start(self.decrease_font_button, True, True, 0)
            font_box.pack_start(self.increase_font_button, True, True, 0)
            main_box.pack_start(font_box, False, False, 0)

            # Sound toggle
            sound_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.sound_toggle = Gtk.CheckButton(label="Enable Sound")
            self.sound_toggle.set_active(self.sound_enabled)
            sound_box.pack_start(self.sound_toggle, False, False, 0)
            main_box.pack_start(sound_box, False, False, 0)

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

            # Set GTK 3 accessibility properties
            self._set_accessibility_properties()

        self.window.show_all()

    def _play_notification_sound(self):
        """Play a sound notification when timer finishes."""
        if not self.sound_enabled:
            return
            
        def play_sound():
            try:
                # Method 1: Try playsound (install with: pip install playsound)
                try:
                    from playsound import playsound
                    # You can replace this with your own sound file
                    sound_file = "/usr/share/sounds/alsa/Front_Right.wav"  # Common system sound
                    if os.path.exists(sound_file):
                        playsound(sound_file)
                    else:
                        # Fallback to system beep
                        subprocess.run(["paplay", "/usr/share/sounds/alsa/Front_Left.wav"], 
                                     check=False, capture_output=True)
                except ImportError:
                    # Method 2: Use system commands
                    # Try different system sound commands
                    commands = [
                        ["paplay", "/usr/share/sounds/alsa/Front_Right.wav"],
                        ["aplay", "/usr/share/sounds/alsa/Front_Right.wav"],
                        ["speaker-test", "-t", "sine", "-f", "1000", "-l", "1"],
                        ["beep"],
                        ["echo", "-e", "\\a"]  # Terminal bell
                    ]
                    
                    for cmd in commands:
                        try:
                            result = subprocess.run(cmd, check=False, capture_output=True, timeout=3)
                            if result.returncode == 0:
                                break
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            continue
                            
            except Exception as e:
                print(f"Could not play sound: {e}")
        
        # Play sound in separate thread to avoid blocking UI
        threading.Thread(target=play_sound, daemon=True).start()
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

    def do_command_line(self, command_line):
        """Handle command line arguments."""
        self.activate()
        return 0

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
        css = f"""
        * {{
            font-size: {self.font_scale_factor * 100}%;
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

    def on_increase_font_clicked(self, button):
        """Increases the font size."""
        if self.font_scale_factor < MAX_FONT_SCALE:
            self.font_scale_factor += FONT_SCALE_INCREMENT
            self._apply_font_size()
            self._save_font_scale()
            print(f"Increased font to: {self.font_scale_factor:.1f}x")
            self._update_font_size_announcement()

    def on_decrease_font_clicked(self, button):
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

    def on_start_clicked(self, button):
        self.time_left = int(self.duration_spin.get_value()) * 60
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

    def on_stop_clicked(self, button):
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
            
            # Play notification sound
            self._play_notification_sound()
            
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_description("Tea is ready! The timer has finished.")
            
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            print("Tea is ready!")
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

import sys

if __name__ == "__main__":
    app = TeaTimerApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)