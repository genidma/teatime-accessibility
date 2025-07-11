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
        super().__init__(application_id="org.example.TeaTimer")
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.current_timer_duration = 0  # Add this line
        self.cli_duration = None  # Store command line duration here
        self.font_scale_factor = DEFAULT_FONT_SCALE
        self.last_duration = 5  # Default duration from config
        self.sound_enabled = True
        self.rainbow_timer_id = None
        self.css_provider = Gtk.CssProvider()
        self.rainbow_hue = 0
        self._stats_window = None
        self.focus_hue = 0
        self._load_config()  # Load settings from file
        # Set up keyboard shortcuts
        self._setup_actions()


    def do_activate(self):
        """This method is called when the application is activated."""
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

            # --- Main grid layout ---
            grid = Gtk.Grid()
            grid.set_row_spacing(10)
            grid.set_column_spacing(10)
            grid.set_margin_top(10)
            grid.set_margin_bottom(10)
            grid.set_margin_start(10)
            grid.set_margin_end(10)
            self.window.add(grid)

            # Row 1: Duration selection
            duration_label = Gtk.Label(label="Minutes:")
            self.duration_spin = Gtk.SpinButton()
            self.duration_spin.set_range(1, 999)
            self.duration_spin.set_increments(1, 5)
            
            # Use last_duration from config
            self.duration_spin.set_value(self.last_duration)
            self.duration_spin.set_width_chars(3)  # Ensure enough width for 3 digits
            grid.attach(duration_label, 0, 1, 1, 1)
            grid.attach(self.duration_spin, 1, 1, 1, 1)

            # Row 2: Start button
            self.start_button = Gtk.Button(label="Start")
            self.start_button.connect("clicked", self._on_start_clicked)
            grid.attach(self.start_button, 0, 2, 2, 1)

            # Row 3: Time display
            self.time_label = Gtk.Label(label="00:00")
            self.time_label.modify_font(Pango.FontDescription(f"monospace {int(24 * self.font_scale_factor)}"))
            grid.attach(self.time_label, 0, 3, 2, 1)

            # Row 4: Font size controls
            font_size_label = Gtk.Label(label="Font Size:")
            self.font_size_spin = Gtk.SpinButton()
            self.font_size_spin.set_range(MIN_FONT_SCALE, MAX_FONT_SCALE)
            self.font_size_spin.set_increments(FONT_SCALE_INCREMENT, FONT_SCALE_INCREMENT)
            self.font_size_spin.set_value(self.font_scale_factor)
            self.font_size_spin.set_digits(1)
            self.font_size_spin.connect("value-changed", self._on_font_size_changed)
            grid.attach(font_size_label, 0, 4, 1, 1)
            grid.attach(self.font_size_spin, 1, 4, 1, 1)

            # Row 5: Sound toggle
            self.sound_toggle = Gtk.CheckButton(label="Sound Enabled")
            self.sound_toggle.set_active(self.sound_enabled)
            self.sound_toggle.connect("toggled", self._on_sound_toggled)
            grid.attach(self.sound_toggle, 0, 5, 2, 1)

            # Row 6: Stats button
            self.stats_button = Gtk.Button(label="View Stats")
            self.stats_button.connect("clicked", self._on_stats_clicked)
            grid.attach(self.stats_button, 0, 6, 2, 1)

            # Row 7: About button
            self.about_button = Gtk.Button(label="About")
            self.about_button.connect("clicked", self._on_about_clicked)
            grid.attach(self.about_button, 0, 7, 2, 1)

            # --- Apply CSS ---
            self._apply_css()

            # --- Show the window ---
            self.window.show_all()

    def _apply_css(self):
        css = """
        window {
            background-color: #f0f0f0;
        }
        label {
            color: #333333;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        button:hover {
            background-color: #45a049;
        }
        checkbutton {
            color: #333333;
        }
        """
        self.css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _on_start_clicked(self, button):
        self.current_timer_duration = self.duration_spin.get_value_as_int() * 60
        self.time_left = self.current_timer_duration
        self._update_time_label()
        self.start_button.set_sensitive(False)
        self.duration_spin.set_sensitive(False)
        self.timer_id = GLib.timeout_add(1000, self._on_timer_tick)

    def _on_timer_tick(self):
        self.time_left -= 1
        self._update_time_label()
        if self.time_left <= 0:
            self._on_timer_finished()
            return False
        return True

    def _on_timer_finished(self):
        self.start_button.set_sensitive(True)
        self.duration_spin.set_sensitive(True)
        self._play_sound()
        self._log_stats()

    def _update_time_label(self):
        minutes, seconds = divmod(self.time_left, 60)
        self.time_label.set_text(f"{minutes:02}:{seconds:02}")

    def _play_sound(self):
        if self.sound_enabled:
            subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"])

    def _log_stats(self):
        if not STATS_LOG_FILE.exists():
            STATS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATS_LOG_FILE.write_text(json.dumps([]))

        with open(STATS_LOG_FILE, "r+") as f:
            stats = json.load(f)
            stats.append({
                "duration": self.current_timer_duration,
                "timestamp": datetime.now().isoformat()
            })
            f.seek(0)
            f.write(json.dumps(stats))

    def _on_font_size_changed(self, spin_button):
        self.font_scale_factor = spin_button.get_value()
        self.time_label.modify_font(Pango.FontDescription(f"monospace {int(24 * self.font_scale_factor)}"))
        self._save_config()

    def _on_sound_toggled(self, toggle_button):
        self.sound_enabled = toggle_button.get_active()
        self._save_config()

    def _on_stats_clicked(self, button):
        if self._stats_window is None:
            self._stats_window = Gtk.Window(title="Tea Timer Stats")
            self._stats_window.set_default_size(400, 300)
            self._stats_window.connect("destroy", self._on_stats_window_destroy)

            # --- Main grid layout ---
            grid = Gtk.Grid()
            grid.set_row_spacing(10)
            grid.set_column_spacing(10)
            grid.set_margin_top(10)
            grid.set_margin_bottom(10)
            grid.set_margin_start(10)
            grid.set_margin_end(10)
            self._stats_window.add(grid)

            # Row 1: Stats label
            stats_label = Gtk.Label(label="Tea Timer Usage Stats")
            stats_label.modify_font(Pango.FontDescription("monospace 14"))
            grid.attach(stats_label, 0, 0, 2, 1)

            # Row 2: Stats text view
            self.stats_text_view = Gtk.TextView()
            self.stats_text_view.set_editable(False)
            self.stats_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
            grid.attach(self.stats_text_view, 0, 1, 2, 1)

            # Row 3: Close button
            close_button = Gtk.Button(label="Close")
            close_button.connect("clicked", self._on_stats_window_destroy)
            grid.attach(close_button, 0, 2, 2, 1)

            # --- Apply CSS ---
            self._apply_css()

            # --- Show the window ---
            self._stats_window.show_all()

        self._update_stats_window()

    def _on_stats_window_destroy(self, window):
        self._stats_window = None

    def _update_stats_window(self):
        if STATS_LOG_FILE.exists():
            with open(STATS_LOG_FILE, "r") as f:
                stats = json.load(f)
                stats_text = "\n".join([f"{entry['duration']} seconds at {entry['timestamp']}" for entry in stats])
                self.stats_text_view.get_buffer().set_text(stats_text, -1)

    def _on_about_clicked(self, button):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name(APP_NAME)
        about_dialog.set_version(APP_VERSION)
        about_dialog.set_copyright("© 2023 Your Name")
        about_dialog.set_comments("A simple tea timer application.")
        about_dialog.set_website("https://example.com")
        about_dialog.set_website_label("Visit Website")
        about_dialog.set_authors(["Your Name"])
        about_dialog.set_translator_credits("Your Name")
        about_dialog.set_logo_icon_name("org.example.TeaTimer")
        about_dialog.run()
        about_dialog.destroy()

    def _on_window_destroy(self, window):
        self.quit()

    def _on_focus_changed(self, window, widget):
        if widget:
            self.focus_hue = (self.focus_hue + 1) % 360
            self._apply_css()

    def _setup_actions(self):
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self._on_quit_action)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self._on_about_action)
        self.add_action(action)

        action = Gio.SimpleAction.new("stats", None)
        action.connect("activate", self._on_stats_action)
        self.add_action(action)

        action = Gio.SimpleAction.new("increase_font_size", None)
        action.connect("activate", self._on_increase_font_size_action)
        self.add_action(action)

        action = Gio.SimpleAction.new("decrease_font_size", None)
        action.connect("activate", self._on_decrease_font_size_action)
        self.add_action(action)

        action = Gio.SimpleAction.new("toggle_sound", None)
        action.connect("activate", self._on_toggle_sound_action)
        self.add_action(action)

        # Set up keyboard shortcuts
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])
        self.set_accels_for_action("app.about", ["<Ctrl>H"])
        self.set_accels_for_action("app.stats", ["<Ctrl>S"])
        self.set_accels_for_action("app.increase_font_size", ["<Ctrl>Up"])
        self.set_accels_for_action("app.decrease_font_size", ["<Ctrl>Down"])
        self.set_accels_for_action("app.toggle_sound", ["<Ctrl>T"])

    def _on_quit_action(self, action, param):
        self.quit()

    def _on_about_action(self, action, param):
        self._on_about_clicked(None)

    def _on_stats_action(self, action, param):
        self._on_stats_clicked(None)

    def _on_increase_font_size_action(self, action, param):
        self.font_size_spin.set_value(self.font_size_spin.get_value() + FONT_SCALE_INCREMENT)

    def _on_decrease_font_size_action(self, action, param):
        self.font_size_spin.set_value(self.font_size_spin.get_value() - FONT_SCALE_INCREMENT)

    def _on_toggle_sound_action(self, action, param):
        self.sound_toggle.set_active(not self.sound_toggle.get_active())

    def _load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.font_scale_factor = config.get("font_scale_factor", DEFAULT_FONT_SCALE)
                self.last_duration = config.get("last_duration", 5)
                self.sound_enabled = config.get("sound_enabled", True)

    def _save_config(self):
        config = {
            "font_scale_factor": self.font_scale_factor,
            "last_duration": self.duration_spin.get_value_as_int(),
            "sound_enabled": self.sound_enabled
        }
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

if __name__ == "__main__":
    import sys
    
    # Create a new Gio.Application
    app = TeaTimerApp()
    
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
