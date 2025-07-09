#!/usr/bin/env python3

import time
import json
import locale
import subprocess
import os
from pathlib import Path

import gi
# Ensure GTK 4 is required. If your existing app is GTK 3, change "4.0" to "3.0"
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1") # Adwaita is commonly used with GTK 4
from gi.repository import Gtk, GLib, Gio, Adw, Gdk

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
DEFAULT_FONT_SCALE = 1.0
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 2.0

class TeaTimerApp(Adw.Application):
    def __init__(self):
        # Set Gio.ApplicationFlags.HANDLES_COMMAND_LINE to indicate we handle command line arguments
        # This is important for desktop integration and proper application lifecycle management
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.font_scale_factor = self._load_font_scale()

    def do_activate(self):
        """
        This method is called when the application is activated (e.g., launched without specific command line arguments).
        It ensures the main window is created and presented.
        """
        if not self.window:
            # Load the UI from the .ui file
            builder = Gtk.Builder()
            # Construct the path to window.ui relative to the current script
            ui_file_path = Path(__file__).parent / "window.ui"
            try:
                builder.add_from_file(str(ui_file_path))
            except GLib.Error as e:
                print(f"Error loading UI file '{ui_file_path}': {e}")
                # Fallback or exit if UI file cannot be loaded
                self.quit()
                return

            self.window = builder.get_object("main_window")
            if not self.window:
                print("Error: 'main_window' object not found in window.ui. Please check your UI file.")
                self.quit()
                return

            self.window.set_application(self) # Set application for the window

            # Get references to widgets defined in window.ui
            self.time_label = builder.get_object("time_label")
            self.start_button = builder.get_object("start_button")
            self.stop_button = builder.get_object("stop_button")
            self.duration_spin = builder.get_object("duration_spin")
            self.increase_font_button = builder.get_object("increase_font_button")
            self.decrease_font_button = builder.get_object("decrease_font_button")

            # Basic error checking for widgets
            if not all([self.time_label, self.start_button, self.stop_button,
                        self.duration_spin, self.increase_font_button, self.decrease_font_button]):
                print("Error: One or more required widgets not found in window.ui. Please check IDs.")
                self.quit()
                return

            # Connect signals
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            self.increase_font_button.connect("clicked", self.on_increase_font_clicked)
            self.decrease_font_button.connect("clicked", self.on_decrease_font_clicked)

            # Initial state for buttons
            self.stop_button.set_sensitive(False)

            # Apply initial font size
            self._apply_font_size()

            # Set accessible properties for existing elements (if not already in .ui)
            # These provide information to screen readers (e.g., Orca)
            self.time_label.set_accessible_role(Gtk.AccessibleRole.STATUS)
            self.time_label.set_accessible_description("Displays the remaining time for the tea timer.")
            self.start_button.set_accessible_name("Start Tea Timer")
            self.stop_button.set_accessible_name("Stop Tea Timer")
            self.duration_spin.set_accessible_name("Tea brewing duration in minutes")
            self.increase_font_button.set_accessible_name("Increase Font Size")
            self.decrease_font_button.set_accessible_name("Decrease Font Size")

        self.window.present()

    def do_command_line(self, command_line):
        """
        This method is called when the application is launched with command line arguments.
        It's required because Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        For this simple app, we just activate the application normally.
        """
        # You can process command_line arguments here if needed
        # For a simple app, we just activate the application
        self.activate()
        return 0 # Return 0 for success

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
        # Apply font size to all labels and buttons, and other text elements
        # This uses CSS to scale all fonts relative to their default size
        css = f"""
        * {{
            font-size: {self.font_scale_factor * 100}%;
        }}
        """
        css_provider.load_from_string(css)

        # Get the default display and add the CSS provider
        # This needs a graphical display to be available
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        else:
            print("Warning: No default display found to apply CSS. Are you running in a graphical environment?")

    def _update_font_size_announcement(self):
        """Updates the accessible description for the font size buttons."""
        description = f"Font size is now {int(self.font_scale_factor * 100)} percent of normal."
        self.increase_font_button.set_accessible_description(description)
        self.decrease_font_button.set_accessible_description(description)

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

    def on_start_clicked(self, button):
        self.time_left = int(self.duration_spin.get_value()) * 60
        self.start_timer()
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        # Update accessibility state for buttons
        self.start_button.set_accessible_state(Gtk.AccessibleState.DISABLED, True)
        self.stop_button.set_accessible_state(Gtk.AccessibleState.DISABLED, False)
        print("Timer started")
        # Announce to screen reader
        self.time_label.set_label(f"{self.time_left // 60:02d}:{self.time_left % 60:02d}")
        self.time_label.set_accessible_description(f"Tea timer started for {self.duration_spin.get_value()} minutes.")

    def on_stop_clicked(self, button):
        self.stop_timer()
        self.time_left = 0 # Reset time on stop
        self.time_label.set_label("00:00") # Reset label
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        # Update accessibility state for buttons
        self.start_button.set_accessible_state(Gtk.AccessibleState.DISABLED, False)
        self.stop_button.set_accessible_state(Gtk.AccessibleState.DISABLED, True)
        print("Timer stopped")
        # Announce to screen reader
        self.time_label.set_accessible_description("Tea timer stopped and reset.")

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
        self.time_label.set_label(f"{minutes:02d}:{seconds:02d}")
        # Only update accessible description if time changes significantly or for critical moments
        if self.time_left % 10 == 0 or self.time_left <= 5: # Update every 10 seconds or last 5
            self.time_label.set_accessible_description(f"Time remaining: {minutes} minutes and {seconds} seconds.")

        if self.time_left <= 0:
            self.stop_timer()
            self.time_label.set_label("Tea Ready!")
            self.time_label.set_accessible_description("Tea is ready! The timer has finished.")
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            # You would also play a sound and/or send a desktop notification here
            print("Tea is ready!")
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

import sys

if __name__ == "__main__":
    app = TeaTimerApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)