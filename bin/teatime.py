#!/usr/bin/env python3

import time
import json
import locale
import subprocess
import os
from pathlib import Path
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
        self.rainbow_timer_id = None
        self.rainbow_hue = 0

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
            main_box.set_margin_left(20)
            main_box.set_margin_right(20)

            # Time display
            self.time_label = Gtk.Label(label="00:00")
            self.time_label.set_markup("<span size='xx-large'>00:00</span>")
            main_box.pack_start(self.time_label, False, False, 0)

            # Duration selection
            duration_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            duration_label = Gtk.Label(label="Minutes:")
            # Allow up to 3 digits for the timer
            self.duration_spin = Gtk.SpinButton.new_with_range(1, 999, 1)
            self.duration_spin.set_width_chars(3) # Ensure it's wide enough for 3 digits
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
        about_dialog.set_authors(["Adeel Khan (GitHub: genidma)", "Initial script by Claude AI", "Refinements by Gemini"])
        about_dialog.set_logo_icon_name("accessories-clock")
        about_dialog.run()
        about_dialog.destroy()

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

    def on_start_clicked(self, button):
        # Stop any previous rainbow effect
        self._stop_rainbow_timer()
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size() # Reset color

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
            
            accessible = self.time_label.get_accessible()
            if accessible:
                accessible.set_description("Tea is ready! The timer has finished.")
            
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            print("Tea is ready!")
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE


if __name__ == "__main__":
    import sys
    app = TeaTimerApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)