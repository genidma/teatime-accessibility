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
import sys

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, Pango, GdkPixbuf

import argparse

# Application metadata
APP_NAME = "Accessible Tea Timer"
APP_VERSION = "1.3.6"

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
STATS_LOG_FILE = Path.home() / ".local/share/teatime_stats.json"
DEFAULT_FONT_SCALE = 1.5
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 6.0

class TeaTimerApp(Gtk.Application):
    def __init__(self, duration=5, auto_start=False):
        super().__init__(application_id="org.example.TeaTimer",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.current_timer_duration = 0
        self.font_scale_factor = DEFAULT_FONT_SCALE
        # Check if duration was set via environment variable
        import os
        env_duration = os.environ.get('TEATIME_DURATION')
        # If seconds mode is active (developer/test), use duration as-is
        if getattr(self, 'use_seconds', False):
            self.last_duration = duration  # already in seconds
        else:
            # Normal behavior: use environment variable if set, else duration (in minutes)
            env_duration = os.environ.get('TEATIME_DURATION')
            if env_duration is not None:
                self.last_duration = int(env_duration)
            else:
                self.last_duration = duration
        self.sound_enabled = True
        self.rainbow_timer_id = None
        self.css_provider = Gtk.CssProvider()
        self._stats_window = None
        self.rainbow_hue = 0
        self._stats_window = None
        self.focus_hue = 0 # Hue for the focus glow, 0-359
        self.sprite_window = None  # Reference to sprite animation window
        self.sprite_frames = []    # Storage for sprite frames
        self.current_sprite_frame = 0
        self.sprite_timer_id = None
        self.auto_start = auto_start  # Flag to indicate if timer should start automatically
        self.mini_mode = False  # Mini-mode flag
        self.nano_mode = False  # Nano-mode flag (active only during timer)
        self.pre_timer_mode = None  # Store the mode before timer starts
        self._load_config()  # Load settings from file

        # Set up keyboard shortcuts
        self._setup_actions()
        
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

            # Add Settings menu item
            settings_item = Gtk.MenuItem(label="_Settings")
            settings_item.set_use_underline(True)
            settings_item.connect("activate", self.on_settings_activated)
            about_menu.append(settings_item)

            about_item = Gtk.MenuItem(label="_About")
            about_item.set_use_underline(True)
            about_item.connect("activate", self.on_about_activated)
            about_menu.append(about_item)
            about_menu.show_all()

            # Add accelerators for menu items
            accel_group = Gtk.AccelGroup()
            self.window.add_accel_group(accel_group)
            stats_item.add_accelerator("activate", accel_group, Gdk.keyval_from_name("i"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
            settings_item.add_accelerator("activate", accel_group, Gdk.keyval_from_name("comma"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)

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
            self.main_box = main_box  # Store reference for mini-mode

            # --- Create a horizontal box to hold main controls and presets ---
            content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            main_box.pack_start(content_box, True, True, 0)
            self.content_box = content_box  # Store reference for mini-mode

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
            self.control_grid = grid  # Store reference for mini-mode

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
            self.stop_button = Gtk.Button(label="S_top")
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

            # Row 4: Mini-mode toggle (spans both columns)
            self.mini_mode_toggle = Gtk.CheckButton(label="_Mini Mode")
            self.mini_mode_toggle.set_use_underline(True)
            self.mini_mode_toggle.set_active(getattr(self, 'mini_mode', False))
            self.mini_mode_toggle.connect("toggled", self.on_mini_mode_toggled)
            grid.attach(self.mini_mode_toggle, 0, 4, 2, 1)

            # Row 5: Nano-mode toggle (spans both columns)
            self.nano_mode_toggle = Gtk.CheckButton(label="_Nano Mode (auto-activate during timer)")
            self.nano_mode_toggle.set_use_underline(True)
            self.nano_mode_toggle.set_active(getattr(self, 'nano_mode', False))
            self.nano_mode_toggle.connect("toggled", self.on_nano_mode_toggled)
            grid.attach(self.nano_mode_toggle, 0, 5, 2, 1)

            # --- Presets Box (RIGHT SIDE) ---
            presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            presets_box.set_valign(Gtk.Align.CENTER)
            content_box.pack_start(presets_box, False, False, 0)
            self.presets_box = presets_box  # Store reference for mini-mode

            presets_label = Gtk.Label(label="<span size='large'><b>Session Presets</b></span>")
            presets_label.set_use_markup(True)
            presets_box.pack_start(presets_label, False, False, 0)
            self.presets_label = presets_label  # Store reference for mini-mode

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
        
        # Apply mini-mode settings
        self._apply_mini_mode()
        
        # Apply the selected skin
        self._apply_skin()
        
        # Start the rainbow timer for background glow effect
        self._start_rainbow_timer()
        
        # Automatically start the timer if auto_start flag is set
        if self.auto_start:
            # Use idle_add to ensure the UI is fully initialized before starting
            GLib.idle_add(self._auto_start_timer)

    def _auto_start_timer(self):
        """Helper method to automatically start the timer after UI is shown."""
        # Set the duration and start the timer
        self.on_start_clicked()
        return False  # Don't repeat this callback

    def _on_window_destroy(self, widget):
        """Handle window destruction properly."""
        self._save_config()

    def toggle_mini_mode(self):
        """Toggle mini-mode and apply UI changes."""
        self.mini_mode = not self.mini_mode
        if hasattr(self, 'mini_mode_toggle'):
            self.mini_mode_toggle.set_active(self.mini_mode)
        self._apply_mini_mode()
        self._save_config()

    def _apply_mini_mode(self):
        """Apply mini-mode UI changes."""
        if not self.window:
            return
            
        # Check if UI elements exist
        if hasattr(self, 'content_box') and hasattr(self, 'presets_box') and hasattr(self, 'presets_label') and hasattr(self, 'main_box') and hasattr(self, 'time_label') and hasattr(self, 'control_grid'):
            if self.mini_mode:
                # Apply mini-mode - compact window size
                self.window.set_default_size(200, 100)
                self.window.resize(200, 100)
                
                # Hide the presets section in mini-mode
                self.presets_box.set_visible(False)
                self.presets_label.set_visible(False)
                
                # Make the control grid more compact
                self.control_grid.set_column_spacing(5)
                self.control_grid.set_row_spacing(5)
                
                # Make the duration spin button smaller
                self.duration_spin.set_width_chars(2)
                
                # Make buttons smaller by changing their style
                css_provider = Gtk.CssProvider()
                css_provider.load_from_data(b"""
                    button, checkbutton {
                        padding: 2px 4px;
                        font-size: 10px;
                    }
                    spinbutton entry {
                        font-size: 14px;
                        padding: 2px;
                    }
                    label:not(.time-display) {
                        font-size: 10px;
                    }
                """)
                # Apply to the main window
                screen = Gdk.Screen.get_default()
                if screen:
                    Gtk.StyleContext.add_provider_for_screen(
                        screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 2
                    )
                
                # Adjust main box margins
                self.main_box.set_margin_top(10)
                self.main_box.set_margin_bottom(10)
                self.main_box.set_margin_start(10)
                self.main_box.set_margin_end(10)
                
                # Center the time label
                self.time_label.set_halign(Gtk.Align.CENTER)
            else:
                # Apply normal mode
                self.window.set_default_size(300, 200)
                self.window.resize(300, 200)
                
                # Show all elements
                self.presets_box.set_visible(True)
                self.presets_label.set_visible(True)
                
                # Reset the control grid spacing
                self.control_grid.set_column_spacing(10)
                self.control_grid.set_row_spacing(10)
                
                # Reset the duration spin button
                self.duration_spin.set_width_chars(3)
                
                # Remove the mini-mode CSS provider by creating a new one with empty CSS
                css_provider = Gtk.CssProvider()
                css_provider.load_from_data(b"")
                screen = Gdk.Screen.get_default()
                if screen:
                    Gtk.StyleContext.add_provider_for_screen(
                        screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 2
                    )
                
                # Remove the time label CSS provider
                time_css_provider = Gtk.CssProvider()
                time_css_provider.load_from_data(b"")
                self.time_label.get_style_context().add_provider(
                    time_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 3
                )
                
                # Reset main box margins
                self.main_box.set_margin_top(20)
                self.main_box.set_margin_bottom(20)
                self.main_box.set_margin_start(20)
                self.main_box.set_margin_end(20)
                
                # Reset time label alignment
                self.time_label.set_halign(Gtk.Align.FILL)
        else:
            print("Some UI elements are missing, skipping mini-mode application")

    def _activate_nano_mode(self):
        """Activate nano mode - hide all controls except timer display."""
        if not self.window:
            return
            
        # Apply nano-mode - ultra compact window size
        self.window.set_default_size(150, 80)
        self.window.resize(150, 80)
        
        # Hide all elements except the time label
        if hasattr(self, 'content_box'):
            self.content_box.set_visible(False)
        
        if hasattr(self, 'control_grid'):
            self.control_grid.set_visible(False)
            
        # Make sure time label is visible and centered
        self.time_label.set_halign(Gtk.Align.CENTER)
        self.time_label.set_valign(Gtk.Align.CENTER)
        
        # Add CSS to make the timer even more prominent (200% larger than current size)
        # Calculate a larger font size based on current font scale factor
        timer_font_percentage = self.font_scale_factor * 4.0 * 100  # 4x = 200% larger than 2x
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(f"""
            .time-display {{
                font-size: {timer_font_percentage}%;
                margin: 0;
                padding: 0;
            }}
        """.encode())
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 3
            )

    def _restore_pre_timer_mode(self):
        """Restore the mode that was active before the timer started."""
        if not self.window or not self.pre_timer_mode:
            return
            
        # Remove nano mode CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"")
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 3
            )
            
        # Show all UI elements that were hidden during nano mode
        if hasattr(self, 'content_box'):
            self.content_box.set_visible(True)
        
        if hasattr(self, 'control_grid'):
            self.control_grid.set_visible(True)
            
        # Restore window size
        if self.pre_timer_mode == 'mini':
            # Restore mini mode
            self.mini_mode = True
            self._apply_mini_mode()
        else:
            # Restore normal mode
            self.mini_mode = False
            self._apply_mini_mode()


    def _on_focus_changed(self, container, widget):
        """Cycles the focus glow color when the focused widget changes."""
        # This signal reliably fires when a new child widget gets focus.
        self.focus_hue = (self.focus_hue + 40) % 360 # Cycle through the hue spectrum
        self._apply_font_size() # Re-apply CSS with the new color

    def on_stats_activated(self, *args):
        """Handles the activation of the statistics action."""
        self.show_statistics_window()

    def on_settings_activated(self, *args):
        """Handles the activation of the settings action."""
        self.show_settings_dialog()

    def on_about_activated(self, *args):
        """Handles the activation of the about action."""
        self.show_about_dialog()

    def on_toggle_sound_activated(self, action, parameter):
        """Callback for sound toggle action."""
        self.toggle_sound()

    def on_mini_mode_toggled(self, widget):
        """Callback for mini-mode toggle."""
        self.mini_mode = self.mini_mode_toggle.get_active()
        self._apply_mini_mode()
        self._save_config()

    def on_nano_mode_toggled(self, widget):
        """Callback for nano-mode toggle."""
        self.nano_mode = self.nano_mode_toggle.get_active()
        self._save_config()

    def on_toggle_mini_mode_activated(self, action, parameter):
        """Callback for mini-mode toggle action."""
        self.toggle_mini_mode()

    def _on_window_destroy(self, widget):
        """Handles window destruction."""
        self.quit()

    def show_statistics_window(self):
        """Show the statistics window."""
        # Create statistics window if it doesn't exist
        if not hasattr(self, 'stats_window') or self.stats_window is None:
            self.stats_window = StatisticsWindow(self, self.window)
        else:
            # If it exists, just present it
            self.stats_window.present()

    def show_settings_dialog(self):
        """Displays the settings dialog."""
        # Create the settings dialog
        dialog = Gtk.Dialog(
            title="Settings",
            parent=self.window,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        
        dialog.set_default_size(400, 300)
        dialog.set_border_width(10)
        
        # Get content area
        content_area = dialog.get_content_area()
        content_area.set_spacing(15)
        
        # Create a grid for layout
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        content_area.add(grid)
        
        # Add animation selection with more descriptive label
        animation_label = Gtk.Label(label="Animation (For Session Complete):")
        animation_label.set_halign(Gtk.Align.START)
        grid.attach(animation_label, 0, 0, 1, 1)
        
        # Get available animations
        assets_dir = Path(__file__).parent.parent / "assets"
        sprites_dir = assets_dir / "sprites"
        animations = []
        
        if sprites_dir.exists():
            for item in sprites_dir.iterdir():
                if item.is_dir():
                    animations.append(item.name)
        
        # Create combobox for animation selection
        self.animation_combo = Gtk.ComboBoxText()
        for animation in animations:
            # Remove underscores and convert to title case
            display_name = animation.replace("_", " ").title()
            # Remove the redundant "Animation" word from the display name
            display_name = display_name.replace("Animation", "").strip()
            # Special case: change "Test" to "Bouncing Balls"
            if display_name == "Test":
                display_name = "Bouncing Balls"
            self.animation_combo.append(animation, display_name)
        
        # Set the current selection
        current_animation = getattr(self, 'preferred_animation', 'test_animation')
        self.animation_combo.set_active_id(current_animation)
        
        grid.attach(self.animation_combo, 1, 0, 1, 1)
        
        # Add skin selection with more descriptive label
        skin_label = Gtk.Label(label="Skins for Main UI (User Interface):")
        skin_label.set_halign(Gtk.Align.START)
        grid.attach(skin_label, 0, 1, 1, 1)
        
        # Define available skins
        skins = [
            ("default", "Default - No Skin"),
            ("lava", "Lava Lamp")
        ]
        
        # Create combobox for skin selection
        self.skin_combo = Gtk.ComboBoxText()
        for skin_id, skin_name in skins:
            self.skin_combo.append(skin_id, skin_name)
        
        # Set the current selection
        current_skin = getattr(self, 'preferred_skin', 'default')
        self.skin_combo.set_active_id(current_skin)
        
        grid.attach(self.skin_combo, 1, 1, 1, 1)
        
        
        # Show the dialog
        dialog.show_all()
        
        # Run the dialog and handle response
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Save the selected animation
            selected_animation = self.animation_combo.get_active_id()
            if selected_animation:
                self.preferred_animation = selected_animation
                print(f"Animation preference updated to: {selected_animation}")
                
            # Save the selected skin
            selected_skin = self.skin_combo.get_active_id()
            if selected_skin:
                self.preferred_skin = selected_skin
                print(f"Skin preference updated to: {selected_skin}")
                
            # Save nano mode preference
            self.nano_mode = self.nano_mode_toggle.get_active()
            print(f"Nano mode preference updated to: {self.nano_mode}")
                
            self._save_config()
            
        dialog.destroy()

    def show_about_dialog(self):
        """Displays the about dialog."""
        # Create about dialog
        dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        dialog.set_program_name(APP_NAME)
        dialog.set_version(APP_VERSION)
        dialog.set_comments("An accessible tea timer application with customizable animations.")
        dialog.set_website("https://github.com/harmonoid/teatime-accessibility")
        dialog.set_website_label("GitHub Repository")
        dialog.set_authors(["Lingma from Alibaba Cloud", "Gemini by Google", "genidma on Github"])
        dialog.set_copyright("Copyright 2025 TeaTime Accessibility Team")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_logo_icon_name("timer")
        
        # Show the dialog
        dialog.run()
        dialog.destroy()

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
                    print("", end="", flush=True)
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

        # Sound toggle action
        sound_action = Gio.SimpleAction.new("toggle-sound", None)
        sound_action.connect("activate", self.on_toggle_sound_activated)
        self.add_action(sound_action)
        self.set_accels_for_action("app.toggle-sound", ["<Control>m"])

        # Mini-mode toggle action
        mini_mode_action = Gio.SimpleAction.new("toggle-mini-mode", None)
        mini_mode_action.connect("activate", self.on_toggle_mini_mode_activated)
        self.add_action(mini_mode_action)
        self.set_accels_for_action("app.toggle-mini-mode", ["<Control>d"])  # 'd' for compact display

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
                    # Only load last_duration from config if not set via command line
                    env_duration = os.environ.get('TEATIME_DURATION')
                    if env_duration is None:
                        self.last_duration = config.get("last_duration", 5)
                    # Load preferred animation
                    self.preferred_animation = config.get("preferred_animation", "puppy_animation")
                    # Load preferred skin
                    self.preferred_skin = config.get("preferred_skin", "default")
                    # Load mini-mode preference
                    self.mini_mode = config.get("mini_mode", False)
                    # Load nano-mode preference
                    self.nano_mode = config.get("nano_mode", False)
                    # Initialize nano mode tracking (not persisted)
                    self.pre_timer_mode = None
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error decoding config file: {CONFIG_FILE}. Using defaults. Error: {e}")
                self.preferred_animation = "puppy_animation"
                self.preferred_skin = "default"
                self.mini_mode = False
                self.nano_mode = False
                self.pre_timer_mode = None
            except Exception as e:
                print(f"An unexpected error occurred while loading config: {e}. Using defaults.")
                self.preferred_animation = "puppy_animation"
                self.preferred_skin = "default"
                self.mini_mode = False
                self.nano_mode = False
                self.pre_timer_mode = None
        else:
            # Default animation if no config file exists
            self.preferred_animation = "puppy_animation"
            self.preferred_skin = "default"
            self.mini_mode = False
            self.nano_mode = False
            self.pre_timer_mode = None

    def _save_config(self):
        """Saves the current configuration to the config file."""
        if not self.window:  # Don't save if window wasn't created
            return
        try:
            config_data = {
                "font_scale_factor": self.font_scale_factor,
                "last_duration": self.duration_spin.get_value_as_int(),
                "preferred_animation": getattr(self, 'preferred_animation', 'test_animation'),
                "preferred_skin": getattr(self, 'preferred_skin', 'default'),
                "mini_mode": getattr(self, 'mini_mode', False),
                "nano_mode": getattr(self, 'nano_mode', False)
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

    def _apply_skin(self):
        """Applies the selected skin to the main window."""
        skin = getattr(self, 'preferred_skin', 'default')
        
        if skin == 'default':
            # Remove any custom background styling
            css = """
            window {
                background-color: #f0f0f0;
                background-image: none;
            }
            """
        elif skin == 'lava':
            # Apply lava lamp effect using gradients
            # We'll create a dynamic gradient that changes with the rainbow hue
            h1 = self.rainbow_hue
            h2 = (self.rainbow_hue + 120) % 360
            h3 = (self.rainbow_hue + 240) % 360
            
            r1, g1, b1 = colorsys.hsv_to_rgb(h1 / 360.0, 0.8, 0.7)
            r2, g2, b2 = colorsys.hsv_to_rgb(h2 / 360.0, 0.8, 0.7)
            r3, g3, b3 = colorsys.hsv_to_rgb(h3 / 360.0, 0.8, 0.7)
            
            color1 = f"rgb({int(r1*255)}, {int(g1*255)}, {int(b1*255)})"
            color2 = f"rgb({int(r2*255)}, {int(g2*255)}, {int(b2*255)})"
            color3 = f"rgb({int(r3*255)}, {int(g3*255)}, {int(b3*255)})"
            
            css = f"""
            window {{
                background: linear-gradient(45deg, {color1}, {color2}, {color3});
                background-size: 300% 300%;
                animation: lavaFlow 60s ease infinite;
            }}
            
            @keyframes lavaFlow {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            """
        else:
            # Default fallback
            css = """
            window {
                background-color: #f0f0f0;
                background-image: none;
            }
            """
        
        # Apply the skin CSS
        try:
            skin_provider = Gtk.CssProvider()
            skin_provider.load_from_data(css.encode())
            
            # Add the skin provider with higher priority than the main one
            screen = Gdk.Screen.get_default()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(
                    screen, skin_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
                )
        except Exception as e:
            print(f"Error applying skin: {e}")

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
        print("DEBUG: on_increase_font_clicked called")
        print(f"DEBUG: Attempting to increase font size. Current: {self.font_scale_factor:.1f}, Max: {MAX_FONT_SCALE:.1f}")
        if self.font_scale_factor < MAX_FONT_SCALE:
            self.font_scale_factor = min(MAX_FONT_SCALE, self.font_scale_factor + FONT_SCALE_INCREMENT)
            print(f"New font scale factor: {self.font_scale_factor:.1f}")
            self._apply_font_size()
            # If we're in nano mode, also update the nano mode font size
            if hasattr(self, 'nano_mode') and self.nano_mode and hasattr(self, 'pre_timer_mode') and self.pre_timer_mode:
                self._activate_nano_mode()
            self._save_config()
            print(f"Increased font to: {self.font_scale_factor:.1f}x")
            self._update_font_size_announcement()
        else:
            print("Font size is already at maximum")

    def on_decrease_font_clicked(self, *args):
        """Decreases the font size."""
        print("DEBUG: on_decrease_font_clicked called")
        print(f"DEBUG: Attempting to decrease font size. Current: {self.font_scale_factor:.1f}, Min: {MIN_FONT_SCALE:.1f}")
        if self.font_scale_factor > MIN_FONT_SCALE:
            self.font_scale_factor = max(MIN_FONT_SCALE, self.font_scale_factor - FONT_SCALE_INCREMENT)
            print(f"New font scale factor: {self.font_scale_factor:.1f}")
            self._apply_font_size()
            # If we're in nano mode, also update the nano mode font size
            if hasattr(self, 'nano_mode') and self.nano_mode and hasattr(self, 'pre_timer_mode') and self.pre_timer_mode:
                self._activate_nano_mode()
            self._save_config()
            print(f"Decreased font to: {self.font_scale_factor:.1f}x")
            self._update_font_size_announcement()
        else:
            print("Font size is already at minimum")

    def on_toggle_sound_activated(self, *args):
        """Handles the activation of the toggle-sound action, and toggles the sound_toggle button."""
        if self.sound_toggle:
            self.sound_toggle.set_active(not self.sound_toggle.get_active())

    def on_sound_toggled(self, button):
        """Toggle sound notifications on/off."""
        self.sound_enabled = button.get_active()
        status = "enabled" if self.sound_enabled else "disabled"
        print(f"Sound notifications {status}")

    def _start_rainbow_timer(self):
        """Start the rainbow color cycling timer."""
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
        self.rainbow_timer_id = GLib.timeout_add(500, self._update_rainbow)

    def _stop_rainbow_timer(self):
        """Stop the rainbow color cycling timer."""
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
            self.rainbow_timer_id = None

    def _update_rainbow(self):
        """Update the rainbow color effect."""
        self.rainbow_hue = (self.rainbow_hue + 1) % 360
        self._apply_font_size()
        self._apply_skin()  # Also update the skin if it uses rainbow colors
        return GLib.SOURCE_CONTINUE

    def on_start_clicked(self, *args):
        # Store the current mode before starting timer if nano mode is enabled
        if getattr(self, 'nano_mode', False):
            self.pre_timer_mode = 'mini' if self.mini_mode else 'normal'
            
            # Activate nano mode when timer starts
            self._activate_nano_mode()
        
        # Stop any previous rainbow effect
        self._stop_rainbow_timer()
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size() # Reset color

        # Get the current value from the spin button
        current_duration = int(self.duration_spin.get_value())
        print(f"DEBUG: Starting timer with duration: {current_duration}")
        
        # 2025-10-17 Chatgpt recommended change so that the 'test_short_timer.py' script can pass second based variables for durtion to this main teatime.py script
        if getattr(self, 'use_seconds', False):
            self.time_left = current_duration  # already in seconds
        else:
            self.time_left = current_duration * 60  # minutes → seconds
        # DEBUG: show the exact countdown in seconds
        print(f"DEBUG: time_left = {self.time_left} seconds")    
        self.current_timer_duration = current_duration
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
                accessible.set_description(f"Tea timer started for {current_duration} minutes.")
        except Exception as e:
            print(f"Warning: Could not update accessibility description: {e}")

    def on_stop_clicked(self, *args):
        # Stop any previous rainbow effect
        self._stop_rainbow_timer()
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size() # Reset color

        self.stop_timer()
        self.time_left = 0
        self.time_label.set_markup("<span>00:00</span>")
        
        # Restore the mode that was active before timer started
        self._restore_pre_timer_mode()
        
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
        self.timer_id = GLib.timeout_add_seconds(5, self.update_timer)

    def stop_timer(self):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        self.time_left -= 5
        minutes = int(self.time_left // 60)
        seconds = int(self.time_left % 60)
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
            
            # Restore the mode that was active before timer started
            self._restore_pre_timer_mode()
            
            # Start the celebratory rainbow effect!
            self.time_label.get_style_context().add_class("rainbow-text")
            self._start_rainbow_timer()

            # Play notification sound
            self._play_notification_sound()

            # Show fullscreen notification with embedded sprite animation
            self._show_fullscreen_notification()
            
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
            
            # Reset the time display after a delay to match the notification duration
            GLib.timeout_add_seconds(5, self._reset_time_display)
            
            print("Tea is ready!")
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _reset_time_display(self):
        """Reset the time display after timer completion."""
        self.time_label.set_markup("<span>00:00</span>")
        self.time_label.get_style_context().remove_class("rainbow-text")
        self._apply_font_size()  # Reset color
        return GLib.SOURCE_REMOVE

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

    def _show_fullscreen_notification(self):
        """Displays a temporary, fullscreen notification on the same monitor as the main window."""
        notification_window = Gtk.Window(type=Gtk.WindowType.POPUP)
        notification_window.set_decorated(False)
        notification_window.set_keep_above(True)
        
        # Get the monitor where the main window is located
        if self.window and self.window.get_window():
            display = self.window.get_window().get_display()
            monitor = display.get_monitor_at_window(self.window.get_window())
            
            # Get the geometry of the monitor
            geometry = monitor.get_geometry()
            
            # Set the window to cover the entire monitor
            notification_window.move(geometry.x, geometry.y)
            notification_window.set_size_request(geometry.width, geometry.height)
        else:
            # Fallback to fullscreen if we can't determine the monitor
            notification_window.fullscreen()

        # A box to center the content vertically
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_valign(Gtk.Align.CENTER)
        notification_window.add(main_box)

        # The message label
        label = Gtk.Label()
        label.set_markup("<span font_desc='Sans Bold 60px' foreground='white'>Session Complete</span>")
        main_box.pack_start(label, False, False, 0)
        
        # Load sprite frames if not already loaded
        if not self.sprite_frames:
            self.sprite_frames = self._load_sprite_frames()
        
        # Add sprite animation if frames are available
        if self.sprite_frames:
            self.current_sprite_frame = 0  # Reset to first frame
            self.sprite_drawing_area = Gtk.DrawingArea()
            self.sprite_drawing_area.set_size_request(300, 300)  # Set a fixed size
            self.sprite_drawing_area.connect("draw", self._on_sprite_draw)
            main_box.pack_start(self.sprite_drawing_area, False, False, 0)
            
            # Start animation timer (adjust speed as needed)
            if self.sprite_timer_id:
                GLib.source_remove(self.sprite_timer_id)
            
            self.sprite_timer_id = GLib.timeout_add(100, self._update_sprite_frame_notification)  # 10 FPS

        # Set a dark, semi-transparent background for the window
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: rgba(0, 0, 0, 0.75);
        }
        """
        css_provider.load_from_data(css)
        context = notification_window.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        notification_window.show_all()

        # Connect click event to close the window
        notification_window.connect("button-press-event", self._on_notification_clicked)

        # Automatically close the window after 5 seconds
        GLib.timeout_add_seconds(5, self._close_fullscreen_notification, notification_window)
        
    def _update_sprite_frame_notification(self):
        """Update sprite frame for the notification window."""
        if self.sprite_frames and self.sprite_drawing_area:
            self.current_sprite_frame = (self.current_sprite_frame + 1) % len(self.sprite_frames)
            self.sprite_drawing_area.queue_draw()
            return GLib.SOURCE_CONTINUE
        return GLib.SOURCE_REMOVE

    def _load_sprite_frames(self):
        """
        Load sprite frames from the assets directory.
        Looks for files with pattern 'sprite_frame_*.png' or converts GIF to frames.
        """
        sprite_frames = []
        assets_dir = Path(__file__).parent.parent / "assets"
        
        # Check if there's a preferred animation in the config
        preferred_animation = getattr(self, 'preferred_animation', 'test_animation')
        
        # Try to load from the preferred animation directory first
        sprites_dir = assets_dir / "sprites" / preferred_animation
        
        # If preferred animation doesn't exist, try test_animation as fallback
        if not sprites_dir.exists():
            sprites_dir = assets_dir / "sprites" / "test_animation"
        
        print(f"Looking for sprites in: {sprites_dir}")
        
        # Look for individual frame files with "sprite_frame" pattern
        frame_files = list(sprites_dir.glob("*sprite_frame_*.png"))
        print(f"Found {len(frame_files)} frame files: {frame_files}")
        
        if frame_files:
            # Sort frames by number, handling cases where there might not be digits
            def extract_number(filename):
                # Extract all digits from the filename
                digits = ''.join(filter(str.isdigit, filename.name))
                # Return 0 if no digits found, otherwise convert to int
                return int(digits) if digits else 0
                
            frame_files.sort(key=extract_number)
            print(f"Sorted frame files: {frame_files}")
            for frame_file in frame_files:
                try:
                    print(f"Loading sprite frame: {frame_file}")
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(frame_file))
                    sprite_frames.append(pixbuf)
                except Exception as e:
                    print(f"Could not load sprite frame {frame_file}: {e}")
        else:
            # Try to find a GIF file and split it into frames
            gif_files = list(assets_dir.glob("*.gif"))
            print(f"Found {len(gif_files)} GIF files: {gif_files}")
            
            if gif_files:
                # Try to load frames from the first GIF file found
                try:
                    gif_path = str(gif_files[0])
                    print(f"Loading sprite from GIF: {gif_path}")
                    # Load the GIF as an animation
                    animation = GdkPixbuf.PixbufAnimation.new_from_file(gif_path)
                    # For simplicity, we'll just use the first frame for now
                    # A full implementation would extract all frames
                    iter = animation.get_iter(None)
                    pixbuf = iter.get_pixbuf()
                    if pixbuf:
                        sprite_frames.append(pixbuf)
                        print(f"Loaded sprite from GIF: {gif_files[0].name}")
                except Exception as e:
                    print(f"Could not load GIF file {gif_files[0]}: {e}")
                    print("To use sprite animations, please convert GIF to PNG frames named sprite_frame_00.png, sprite_frame_01.png, etc.")
        
        # Also check for the sample image in assets
        image_files = list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.jpg"))
        # Filter out the sprite frames we already processed
        image_files = [f for f in image_files if not "sprite_frame" in f.name]
        print(f"Found {len(image_files)} other image files: {image_files}")
        
        if image_files and not sprite_frames:
            # If we have an image but no sprite frames, use the image as a static sprite
            try:
                # Sort to get a consistent result
                image_files.sort()
                print(f"Using {image_files[0]} as static sprite")
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    str(image_files[0]), 200, 200, True)
                sprite_frames.append(pixbuf)
                print(f"Using {image_files[0].name} as static sprite")
            except Exception as e:
                print(f"Could not load image {image_files[0]}: {e}")
        
        if sprite_frames:
            print(f"Loaded {len(sprite_frames)} sprite frames")
        else:
            print("No sprite frames loaded")
        
        return sprite_frames

    def _show_sprite_animation(self):
        """Display sprite animation when timer completes."""
        # Sprite animation is now embedded in the fullscreen notification
        pass

    def _create_sprite_window(self):
        """Create a window to display the sprite animation."""
        # Sprite animation is now embedded in the fullscreen notification
        pass

    def _on_sprite_draw(self, widget, cr):
        """Draw the current sprite frame."""
        print(f"Drawing sprite frame {self.current_sprite_frame}")
        if self.sprite_frames and 0 <= self.current_sprite_frame < len(self.sprite_frames):
            alloc = widget.get_allocation()
            # Draw the actual sprite frame
            pixbuf = self.sprite_frames[self.current_sprite_frame]
            # Scale the pixbuf to fit the drawing area while maintaining aspect ratio
            pixbuf_width = pixbuf.get_width()
            pixbuf_height = pixbuf.get_height()
            
            scale_x = alloc.width / pixbuf_width
            scale_y = alloc.height / pixbuf_height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            scaled_width = int(pixbuf_width * scale)
            scaled_height = int(pixbuf_height * scale)
            
            # Center the image
            x = (alloc.width - scaled_width) // 2
            y = (alloc.height - scaled_height) // 2
            
            scaled_pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)
            Gdk.cairo_set_source_pixbuf(cr, scaled_pixbuf, x, y)
            cr.paint()
            print(f"Sprite frame {self.current_sprite_frame} drawn")
        else:
            print(f"Skipping draw - no valid sprite frame (current: {self.current_sprite_frame}, total: {len(self.sprite_frames) if self.sprite_frames else 0})")
        
        return False

    def _start_sprite_animation(self):
        """Start the sprite animation loop."""
        # Sprite animation is now embedded in the fullscreen notification
        pass

    def _update_sprite_frame(self):
        """Update to the next sprite frame."""
        if self.sprite_frames:
            self.current_sprite_frame = (self.current_sprite_frame + 1) % len(self.sprite_frames)
            print(f"Updated to sprite frame {self.current_sprite_frame}")
            if hasattr(self, 'sprite_drawing_area'):
                self.sprite_drawing_area.queue_draw()
            return GLib.SOURCE_CONTINUE
        return GLib.SOURCE_REMOVE

    def _close_sprite_animation(self):
        """Close the sprite animation window."""
        # Sprite animation is now embedded in the fullscreen notification
        return GLib.SOURCE_REMOVE

    def _on_notification_clicked(self, widget, event):
        """Close the notification window on click."""
        print("Notification clicked, closing.")
        self._close_fullscreen_notification(widget)
        # Clean up sprite timer if it exists
        if self.sprite_timer_id:
            GLib.source_remove(self.sprite_timer_id)
            self.sprite_timer_id = None

    def _close_fullscreen_notification(self, notification_window):
        """Callback to close the notification window."""
        # Clean up sprite timer if it exists
        if self.sprite_timer_id:
            GLib.source_remove(self.sprite_timer_id)
            self.sprite_timer_id = None
            
        if notification_window:
            notification_window.destroy()
        return GLib.SOURCE_REMOVE

    def do_command_line(self, command_line):
        """Handle command line arguments before activating the application."""
        options = command_line.get_options_dict()
        
        # Get the duration from command line if provided
        duration_variant = options.lookup_value("duration", None)
        if duration_variant is not None:
            self.last_duration = duration_variant.get_int32()
        
        # Activate the application
        self.activate()
        return 0

    def do_startup(self):
        """Set up command line options during application startup."""
        Gtk.Application.do_startup(self)
        
        # Add command line option for duration
        action = Gio.SimpleAction.new("duration", GLib.VariantType.new("i"))
        action.connect("activate", lambda a, p: None)  # No action needed, handled in do_command_line
        self.add_action(action)
        
        # Add the option to the application
        self.add_main_option(
            "duration",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.INT,
            "Timer duration in minutes (1-999)",
            "DURATION"
        )

class StatisticsWindow(Gtk.Window):
    def __init__(self, application, parent):
        super().__init__(title="Timer Statistics", application=application)
        self.set_default_size(400, 300)
        self.set_modal(False)
        self.set_resizable(True)
        # Ensure window decorations including maximize button are displayed
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_decorated(True)
        self.set_role("statistics-window")
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
        self.total_sessions_label = Gtk.Label(label="Total Sessions: 0")
        self.total_time_label = Gtk.Label(label="Total Time: 0 minutes")
        self.avg_duration_label = Gtk.Label(label="Average Duration: 0 minutes")
        self.summary_grid.attach(self.total_sessions_label, 0, 0, 1, 1)
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
                    transient_for=self,
                    modal=True,
                    message_type=Gtk.MessageType.ERROR,
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
        self._load_stats()

    def _reset_summary_labels(self):
        """Resets the summary labels to their default state."""
        self.total_sessions_label.set_text("Total Sessions: 0")
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
        self.total_sessions_label.set_text(f"Total Sessions: {len(sorted_logs)}")
        self.total_time_label.set_text(f"Total Time: {total_duration} minutes")
        if sorted_logs:
            avg_duration = total_duration / len(sorted_logs)
            self.avg_duration_label.set_text(f"Average Duration: {avg_duration:.1f} minutes")
        else:
            self._reset_summary_labels()

    def do_command_line(self, command_line):
        """Handle command line arguments."""
        # Get the command line arguments
        args = command_line.get_arguments()
        
        # Simple argument parsing - look for --duration
        duration = self.default_duration
        i = 1
        while i < len(args):
            if args[i] == "--duration" and i + 1 < len(args):
                try:
                    duration = int(args[i + 1])
                    if duration < 1:
                        duration = 1
                    elif duration > 999:
                        duration = 999
                    i += 2
                except ValueError:
                    i += 2
            else:
                # Skip unknown arguments
                i += 1
        
        # Store the duration and activate the application
        self.last_duration = duration
        self.activate()
        return 0

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
            self.main_box = main_box  # Store reference for mini-mode

            # --- Create a horizontal box to hold main controls and presets ---
            content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            main_box.pack_start(content_box, True, True, 0)
            self.content_box = content_box  # Store reference for mini-mode

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
            self.control_grid = grid  # Store reference for mini-mode

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
            self.stop_button = Gtk.Button(label="S_top")
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

            # --- Presets Box (RIGHT SIDE) ---
            presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            presets_box.set_valign(Gtk.Align.CENTER)
            content_box.pack_start(presets_box, False, False, 0)
            self.presets_box = presets_box  # Store reference for mini-mode

            presets_label = Gtk.Label(label="<span size='large'><b>Session Presets</b></span>")
            presets_label.set_use_markup(True)
            presets_box.pack_start(presets_label, False, False, 0)
            self.presets_label = presets_label  # Store reference for mini-mode

            preset_45_button = Gtk.Button(label="_45 Minutes")
            preset_45_button.set_use_underline(True)
            preset_45_button.connect("clicked", self.on_preset_clicked, 45)
            presets_box.pack_start(preset_45_button, False, False, 0)

            preset_1_hour_button = Gtk.Button(label="_1 Hour")
            preset_1_hour_button.set_use_underline(True)
            preset_1_hour_button.connect("clicked", self.on_preset_clicked, 60)
            presets_box.pack_start(preset_1_hour_button, False, False, 0)

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
        
        # Apply mini-mode settings
        self._apply_mini_mode()
        
        # Apply the selected skin
        self._apply_skin()
        
        # Start the rainbow timer for background glow effect
        self._start_rainbow_timer()
        
        # Automatically start the timer if auto_start flag is set
        if self.auto_start:
            # Use idle_add to ensure the UI is fully initialized before starting
            GLib.idle_add(self._auto_start_timer)

            self.window.add(main_box)

        self.window.show_all()


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Accessible Tea Timer')
    parser.add_argument('--duration', type=int, default=5, help='Timer duration in minutes (1-999)')
    
    # Parse known args to avoid conflicts with GTK arguments
    args, unknown = parser.parse_known_args()
    
    # Store duration for use in the app
    import os
    os.environ['TEATIME_DURATION'] = str(args.duration)
    
    # Determine if we should auto-start the timer (when duration is explicitly provided)
    auto_start = '--duration' in sys.argv
    
    # Reconstruct sys.argv without our custom arguments for GTK
    new_argv = [sys.argv[0]] + unknown
    sys.argv = new_argv
    
    # Create a new Gio.Application
    app = TeaTimerApp(duration=args.duration, auto_start=auto_start)
    
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
