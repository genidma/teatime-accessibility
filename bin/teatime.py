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
from gi.repository import Gtk, GLib, Gio, Gdk, Pango, GdkPixbuf

import argparse

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

# Feature flag for photosensitive mode
PHOTOSENSITIVE_MODE_DEFAULT = False # default value for photosensitive mode
PHOTOSENSITIVE_MODE_ENV_VAR = "TEATIME_PHOTOSENSITIVE_MODE"
# How often to update the time display visually in photosensitive mode (in seconds)
PHOTOSENSITIVE_DISPLAY_UPDATE_INTERVAL_SECONDS = 5


class TeaTimerApp(Gtk.Application):
    def __init__(self, duration=5):
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.current_timer_duration = 0
        self.font_scale_factor = DEFAULT_FONT_SCALE
        self.last_duration = duration  # Default duration from config or CLI
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
        self._load_config()  # Load settings from file

        # Initialize photosensitive mode
        self.photosensitive_mode = self._load_photosensitive_mode()
        self._last_photosensitive_display_update_time = None # For incremental timer updates

        # Set up keyboard shortcuts
        self._setup_actions()

    def _load_photosensitive_mode(self):
        """
        Loads the photosensitive mode flag from the environment variable.
        Returns True if the environment variable is set to 'true' (case-insensitive),
        False otherwise, defaulting to PHOTOSENSITIVE_MODE_DEFAULT.
        """
        env_value = os.environ.get(PHOTOSENSITIVE_MODE_ENV_VAR)
        if env_value is not None:
            return env_value.lower() == 'true'
        return PHOTOSENSITIVE_MODE_DEFAULT # Return default value if not set

    def set_main_window_background_color(self, hex_color=None):
        """
        Applies a background color to the main window using CSS.
        If hex_color is None, clears the custom background.
        """
        css_data = b""
        if hex_color:
            css_data = f"window {{ background-color: {hex_color}; }}".encode('utf-8')
        self.css_provider.load_from_data(css_data)

    def _start_rainbow_glow(self):
        """Starts the rainbow glow effect on the window background."""
        if self.photosensitive_mode:
            self._stop_rainbow_glow() # Ensure it's off and static color is set
            return

        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
        # Immediately set a color so it's not blank before the first update
        r, g, b = colorsys.hsv_to_rgb(self.rainbow_hue / 360.0, 0.7, 0.9)
        hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        self.set_main_window_background_color(hex_color)
        self.rainbow_timer_id = GLib.timeout_add(50, self._update_rainbow_glow_color)

    def _update_rainbow_glow_color(self):
        """Updates the rainbow glow color."""
        if self.photosensitive_mode: # This should not be called if properly guarded
            return False # Stop the callback

        self.rainbow_hue = (self.rainbow_hue + 1) % 360
        # Adjust saturation and value for a softer, less intense glow
        r, g, b = colorsys.hsv_to_rgb(self.rainbow_hue / 360.0, 0.7, 0.9)
        hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        self.set_main_window_background_color(hex_color)
        return True

    def _stop_rainbow_glow(self):
        """Stops the rainbow glow effect."""
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
            self.rainbow_timer_id = None
        # When stopping, revert to a default/static background color based on mode
        if self.photosensitive_mode:
            self.set_main_window_background_color("#616161") # Static grey in photosensitive mode
        else:
            self.set_main_window_background_color(None) # Clear custom background CSS

    def _start_focus_glow(self):
        """Starts a subtle color glow effect on the focused widget."""
        if self.photosensitive_mode:
            self._stop_focus_glow() # Ensure it's off
            return

        if self.focus_timer_id:
            GLib.source_remove(self.focus_timer_id)
        self.focus_timer_id = GLib.timeout_add(100, self._update_focus_glow)

    def _update_focus_glow(self):
        """Updates the focus glow color."""
        if self.photosensitive_mode: # Should not happen if properly guarded
            return False

        focused_widget = self.window.get_focus()
        if focused_widget:
            self.focus_hue = (self.focus_hue + 5) % 360  # Cycle hue more slowly than rainbow
            r, g, b = colorsys.hsv_to_rgb(self.focus_hue / 360.0, 0.8, 0.8)
            hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            css = f"*{ border: 2px solid {hex_color}; box-shadow: 0 0 5px {hex_color}; }"
            self.css_provider.load_from_data(css.encode('utf-8'))
        return True

    def _stop_focus_glow(self):
        """Stops the focus glow effect."""
        if self.focus_timer_id:
            GLib.source_remove(self.focus_timer_id)
            self.focus_timer_id = None
        # Clear any applied focus glow CSS
        self.css_provider.load_from_data(b"") # Load empty CSS to clear previous rules

    # Placeholder for sprite animation methods, to be disabled in photosensitive mode
    def _load_sprite_frames(self):
        # In a real app, this would load images. For now, it's a no-op.
        pass

    def _start_sprite_animation(self):
        """Starts the sprite animation."""
        if self.photosensitive_mode:
            self._stop_sprite_animation()
            return

        # Placeholder: In a real app, this would create/show a sprite window
        # For this exercise, we just manage the timer.
        if self.sprite_timer_id:
            GLib.source_remove(self.sprite_timer_id)
        # self.sprite_timer_id = GLib.timeout_add(100, self._update_sprite_frame)
        print("Sprite animation started (placeholder)")

    def _update_sprite_frame(self):
        """Updates the current sprite frame."""
        if self.photosensitive_mode:
            return False # Stop callback

        # Placeholder: In a real app, this would update the sprite image
        self.current_sprite_frame = (self.current_sprite_frame + 1) % len(self.sprite_frames)
        print(f"Updating sprite frame {self.current_sprite_frame} (placeholder)")
        return True

    def _stop_sprite_animation(self):
        """Stops the sprite animation."""
        if self.sprite_timer_id:
            GLib.source_remove(self.sprite_timer_id)
            self.sprite_timer_id = None
        if self.sprite_window:
            self.sprite_window.hide()
        print("Sprite animation stopped (placeholder)")

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
            stats_item = Gtk.MenuItem(label="_Statistics")
            stats_item.set_use_underline(True)
            stats_item.connect("activate", self.on_stats_activated)
            about_menu.append(stats_item)

            about_item = Gtk.MenuItem(label="_About")
            about_item.set_use_underline(True)
            about_item.connect("activate", self.on_about_activated)
            about_menu.append(about_item)
            about_menu.show_all()

            # Add an accelerator for the statistics menu item.
            accel_group = Gtk.AccelGroup()
            self.window.add_accel_group(accel_group)
            stats_item.add_accelerator("activate", accel_group, Gdk.keyval_from_name("i"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)


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
            self.start_button = Gtk.Button(label="_Start")
            self.start_button.set_use_underline(True)
            self.stop_button = Gtk.Button(label="_Stop")
            self.stop_button.set_use_underline(True)
            grid.attach(self.start_button, 0, 1, 1, 1)
            grid.attach(self.stop_button, 1, 1, 1, 1)

            # Row 2: Font size controls
            self.decrease_font_button = Gtk.Button(label="A-")
            self.increase_font_button = Gtk.Button(label="A+")
            grid.attach(self.decrease_font_button, 0, 2, 1, 1)
            grid.attach(self.increase_font_button, 1, 2, 1, 1)

            # Row 3: Sound toggle (spans both columns)
            self.sound_toggle = Gtk.CheckButton(label="_Enable Sound")
            self.sound_toggle.set_use_underline(True)
            self.sound_toggle.set_active(self.sound_enabled)
            grid.attach(self.sound_toggle, 0, 3, 2, 1)

            # Row 4: Photosensitive Mode Toggle - NEW UI ELEMENT
            self.photosensitive_toggle = Gtk.CheckButton(label="_Photosensitive Mode")
            self.photosensitive_toggle.set_use_underline(True)
            self.photosensitive_toggle.set_active(self.photosensitive_mode)
            grid.attach(self.photosensitive_toggle, 0, 4, 2, 1)


            # --- Presets Box (RIGHT SIDE) ---
            presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            presets_box.set_valign(Gtk.Align.CENTER)
            content_box.pack_start(presets_box, False, False, 0)

            presets_label = Gtk.Label(label="<span size='large'><b>Session Presets</b></span>")
            presets_label.set_use_markup(True)
            presets_box.pack_start(presets_label, False, False, 0)

            preset_45_button = Gtk.Button(label="_45 Minutes")
            preset_45_button.set_use_underline(True)
            preset_45_button.connect("clicked", self.on_preset_clicked, 45)
            presets_box.pack_start(preset_45_button, False, False, 0)

            preset_1_hour_button = Gtk.Button(label="_1 Hour")
            preset_1_hour_button.set_use_underline(True)
            preset_1_hour_button.connect("clicked", self.on_preset_clicked, 60)
            presets_box.pack_start(preset_1_hour_button, False, False, 0)

            self.window.add(main_box)

            # Connect signals
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            self.increase_font_button.connect("clicked", self.on_increase_font_clicked)
            self.decrease_font_button.connect("clicked", self.on_decrease_font_clicked)
            self.sound_toggle.connect("toggled", self.on_sound_toggled)
            self.photosensitive_toggle.connect("toggled", self.on_photosensitive_toggled) # NEW: Connect toggle

            # Add the single CSS provider to the screen. We will update this provider
            # later instead of adding new ones.
            screen = Gdk.Screen.get_default()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(
                    screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            else:
                print("Warning: No default screen found, CSS styling may not apply correctly.")

            # Apply initial photosensitive mode settings
            if self.photosensitive_mode:
                self.set_main_window_background_color("#616161") # Static grey
                self._stop_focus_glow() # Ensure focus glow is off initially
                self._stop_sprite_animation() # Ensure sprite animation is off initially

            self.window.show_all()

    def _on_window_destroy(self, widget):
        """Called when the main window is closed."""
        self._save_config() # Save settings before exit
        self._stop_timer()  # Ensure timer and any active glows are stopped
        # Clean up any sprite windows if they exist
        if self.sprite_window:
            self.sprite_window.destroy()
        Gtk.main_quit()

    def _on_focus_changed(self, widget, focused_child):
        """Called when the focus changes within the window."""
        if self.photosensitive_mode: # NEW: Disable focus glow in photosensitive mode
            self._stop_focus_glow()
            return

        if focused_child:
            self._start_focus_glow()
        else:
            self._stop_focus_glow()

    def _update_timer_display(self):
        """
        Updates the timer display label. In photosensitive mode,
        updates the visual label less frequently.
        """
        if self.timer_id is None: # Timer is not running, stop this callback
            return False

        if self.time_left <= 0:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
            self._timer_finished()
            return False

        minutes = self.time_left // 60
        seconds = self.time_left % 60
        formatted_time = f"{minutes:02}:{seconds:02}"

        # Apply font scaling
        font_size_px = 36 * self.font_scale_factor # Base font size is 36px

        # Conditional visual update for photosensitive mode
        update_label_now = True
        if self.photosensitive_mode:
            current_monotonic_time = time.monotonic()
            if self._last_photosensitive_display_update_time is None:
                self._last_photosensitive_display_update_time = current_monotonic_time
            elif (current_monotonic_time - self._last_photosensitive_display_update_time) < PHOTOSENSITIVE_DISPLAY_UPDATE_INTERVAL_SECONDS:
                update_label_now = False # Don't update the label visually yet

        if update_label_now:
            self.time_label.set_markup(f"<span font_desc='Sans Bold {int(font_size_px)}'>{formatted_time}</span>")
            if self.photosensitive_mode: # Only update _last_photosensitive_display_update_time when actually updating
                self._last_photosensitive_display_update_time = current_monotonic_time


        self.time_left -= 1
        return True

    def _start_timer(self):
        """Starts the countdown timer."""
        if self.timer_id:
            GLib.source_remove(self.timer_id)

        self.time_left = self.duration_spin.get_value_as_int() * 60
        self.current_timer_duration = self.time_left # Store for logging
        self._last_duration = self.time_left // 60 # Save last duration for config

        if self.time_left <= 0:
            print("Please set a duration greater than 0.")
            return

        self._update_timer_display() # Update immediately to show initial time
        self.timer_id = GLib.timeout_add(1000, self._update_timer_display) # Update every 1 second

        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self._set_preset_buttons_sensitive(False) # Disable presets when timer is active

        # Conditionally start visual effects
        if not self.photosensitive_mode:
            self._start_rainbow_glow()
            self._start_sprite_animation() # Placeholder

    def _stop_timer(self):
        """Stops the countdown timer."""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        
        # Always stop visual effects when the timer stops
        self._stop_rainbow_glow()
        self._stop_sprite_animation()
        self._stop_focus_glow() # Stop focus glow when timer stops

        self.time_left = 0 # Reset time
        self._update_timer_display() # Update display to 00:00
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self._set_preset_buttons_sensitive(True)

    def _timer_finished(self):
        """Called when the timer reaches zero."""
        # Stop any active glows/animations
        self._stop_rainbow_glow()
        self._stop_sprite_animation()
        self._stop_focus_glow() # In case focus was still active

        # Log the session
        self._log_session()

        # Update display to show 00:00 and enable start button
        self.time_left = 0
        self._update_timer_display() # Ensure it shows 00:00 immediately
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        # NEW: Conditionally play sound and show dialog based on photosensitive mode
        if not self.photosensitive_mode:
            if self.sound_enabled:
                # Play a sound notification
                try:
                    subprocess.run(["canberra-gtk-play", "--id=dialog-information", "--description='Tea Timer finished'"], check=False)
                except FileNotFoundError:
                    print("Warning: canberra-gtk-play not found. Please install libcanberra-gtk-module.")

            # Display a dialog
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                message_format="Session Completed!"
            )
            dialog.run()
            dialog.destroy()
        else:
            print("Session Completed (sound and dialog suppressed due to Photosensitive Mode).")


        # Re-enable the preset buttons
        self._set_preset_buttons_sensitive(True)


    def _set_preset_buttons_sensitive(self, sensitive):
        """Helper to enable/disable preset buttons."""
        # Iterate over children of presets_box if needed, or target specific buttons.
        # For this example, assuming presets_box only contains buttons directly.
        for child in self.window.get_children()[0].get_children()[0].get_children()[1].get_children():
            if isinstance(child, Gtk.Button):
                child.set_sensitive(sensitive)

    def _apply_font_size(self):
        """Applies the current font scale factor to the time label."""
        font_size_px = 36 * self.font_scale_factor
        self.time_label.set_markup(f"<span font_desc='Sans Bold {int(font_size_px)}'>{self.time_label.get_text()}</span>")

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
        is_new_file = not STATS_LOG_FILE.exists()
        with open(STATS_LOG_FILE, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'duration_minutes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if is_new_file:
                writer.writeheader() # Write header only if file is new

            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'duration_minutes': self.current_timer_duration // 60
            })

    def _setup_actions(self):
        """Sets up Gtk.Application actions for keyboard shortcuts."""
        action_quit = Gio.SimpleAction.new("quit", None)
        action_quit.connect("activate", self.on_quit)
        self.add_action(action_quit)

        # Example: Add an accelerator for "quit" (Ctrl+Q)
        self.set_accels_for_action("app.quit", ["<Primary>q"])

    # --- Signal Handlers ---
    def on_start_clicked(self, widget):
        self._start_timer()

    def on_stop_clicked(self, widget):
        self._stop_timer()

    def on_increase_font_clicked(self, widget):
        if self.font_scale_factor < MAX_FONT_SCALE:
            self.font_scale_factor += FONT_SCALE_INCREMENT
            self._apply_font_size()

    def on_decrease_font_clicked(self, widget):
        if self.font_scale_factor > MIN_FONT_SCALE:
            self.font_scale_factor -= FONT_SCALE_INCREMENT
            self._apply_font_size()

    def on_sound_toggled(self, widget):
        self.sound_enabled = widget.get_active()
        self._save_config() # Save the new sound setting

    def on_photosensitive_toggled(self, widget):
        """
        Handles toggling photosensitive mode.
        Disables/enables visual and auditory effects accordingly.
        """
        self.photosensitive_mode = widget.get_active()
        print(f"Photosensitive mode toggled: {self.photosensitive_mode}")

        if self.photosensitive_mode:
            # Disable visual effects immediately
            self._stop_rainbow_glow() # This will set a static grey background
            self._stop_focus_glow()
            self._stop_sprite_animation()
            # Reset the display update time to force an immediate update if needed
            self._last_photosensitive_display_update_time = None
            # Ensure static background is applied consistently
            self.set_main_window_background_color("#616161")
        else:
            # Clear custom background (revert to default GTK theme)
            self.set_main_window_background_color(None)
            # If a timer is running, restart dynamic effects
            if self.timer_id:
                self._start_rainbow_glow()
                self._start_sprite_animation()
            # Reset the last update time so the label updates immediately upon disabling photosensitive mode
            self._last_photosensitive_display_update_time = None

        self._update_timer_display() # Force an update to reflect potential new update interval

    def on_preset_clicked(self, widget, minutes):
        """Sets the duration spin button value and starts the timer."""
        self.duration_spin.set_value(minutes)
        self.on_start_clicked(widget) # Reuse the start button handler

    def on_about_activated(self, widget):
        """Displays the About dialog."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name(APP_NAME)
        about_dialog.set_version(APP_VERSION)
        about_dialog.set_copyright("© 2023 Your Name/Organization")
        about_dialog.set_comments("An accessible tea timer with customizable font sizes and visual/audio cues.")
        about_dialog.set_website("https://example.com/teatime") # Replace with actual website
        about_dialog.set_license_type(Gtk.License.MIT_X11)
        about_dialog.set_logo_icon_name("timer") # Use a suitable icon
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

            scroll_window = Gtk.ScrolledWindow()
            scroll_window.set_vexpand(True)
            scroll_window.set_hexpand(True)

            list_store = Gtk.ListStore(str, int) # (timestamp, duration_minutes)

            # Load stats from file
            if STATS_LOG_FILE.exists():
                try:
                    with open(STATS_LOG_FILE, 'r') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            list_store.append([row['timestamp'], int(row['duration_minutes'])])
                except (IOError, KeyError, ValueError) as e:
                    print(f"Error loading stats file: {e}")

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
            self._stats_window.add(scroll_window)
            self._stats_window.show_all()
        else:
            self._stats_window.present() # Bring existing window to front

    def on_stats_window_destroy(self, widget):
        """Callback for when the statistics window is destroyed."""
        self._stats_window = None # Clear the reference

    def on_quit(self, action, param):
        """Handles the 'quit' action."""
        self.window.destroy()


def main():
    parser = argparse.ArgumentParser(description="Accessible Tea Timer")
    parser.add_argument("-d", "--duration", type=int, default=5,
                        help="Initial timer duration in minutes (default: 5)")
    parser.add_argument("--photosensitive-mode", action="store_true",
                        help="Enable photosensitive mode, disabling flashing/dynamic elements.")
    args = parser.parse_args()

    app = TeaTimerApp(duration=args.duration)

    # If --photosensitive-mode CLI arg is used, it overrides the environment variable
    # for the initial launch. The UI toggle will then control runtime behavior.
    if args.photosensitive_mode:
        app.photosensitive_mode = True

    app.run(None)

if __name__ == "__main__":
    # Ensure locale is set for potential i18n or number formatting
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("Warning: Could not set locale.")
    main()