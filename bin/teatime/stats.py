from datetime import datetime
import csv
import json

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, Pango, GdkPixbuf

from .core import STATS_LOG_FILE, StatsManager

class StatisticsWindow(Gtk.Window):
    def __init__(self, application, parent):
        super().__init__(title="Timer Statistics", application=application)
        self.set_default_size(400, 300); self.stats_manager = StatsManager(); self.set_modal(False)
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

            self.window.add(main_box)

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



