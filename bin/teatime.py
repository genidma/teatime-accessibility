#!/usr/bin/python3

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
APP_NAME = "Karma Conscience Resonance"
APP_VERSION = "1.3.6"

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
STATS_LOG_FILE = Path.home() / ".local/share/teatime_stats.json"
DEFAULT_FONT_SCALE = 1.5
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 6.0

KC_CATEGORIES = ["rdp", "fc", "g", "m", "sii", "v", "r", "b", "t", "c", "MWHH", "yss", "we", "gotb", "rf", "breaks"]

class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else CONFIG_FILE

    def load(self):
        """Loads configuration from the config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error decoding config file: {self.config_path}. Error: {e}")
                return {}
            except Exception as e:
                print(f"An unexpected error occurred while loading config: {e}.")
                return {}
        return {}

    def save(self, config_data):
        """Saves the configuration to the config file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config file: {e}")
            return False

class StatsManager:
    def __init__(self, stats_path=None):
        self.stats_path = Path(stats_path) if stats_path else STATS_LOG_FILE

    def load(self):
        """Load statistics from the log file."""
        if not self.stats_path.exists():
            return []
        try:
            with open(self.stats_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading stats file: {e}")
            return []

class StatisticsWindow(Gtk.Window):
    def __init__(self, application, parent):
        super().__init__(title="Timer Statistics", application=application)
        self.set_default_size(800, 600)
        self.stats_manager = StatsManager()
        self.set_modal(False)
        self.set_resizable(True)
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
        self.summary_grid = Gtk.Grid(column_spacing=20, row_spacing=5, margin=10)
        self.total_sessions_label = Gtk.Label(label="Total Sessions: 0")
        self.total_time_label = Gtk.Label(label="Total Time: 0 minutes")
        self.avg_duration_label = Gtk.Label(label="Average Duration: 0 minutes")
        self.summary_grid.attach(self.total_sessions_label, 0, 0, 1, 1)
        self.summary_grid.attach(self.total_time_label, 1, 0, 1, 1)
        self.summary_grid.attach(self.avg_duration_label, 2, 0, 1, 1)
        main_box.pack_start(self.summary_grid, False, False, 0)

        # TreeView for detailed logs
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scrolled_window, True, True, 0)
        
        # Model: Date (str), 16 categories (str), Comments (str)
        types = [str] * (len(KC_CATEGORIES) + 2)
        self.store = Gtk.ListStore(*types)
        self.treeview = Gtk.TreeView(model=self.store)

        # Date Column
        renderer_text = Gtk.CellRendererText()
        column_date = Gtk.TreeViewColumn("Date", renderer_text, text=0)
        column_date.set_sort_column_id(0)
        column_date.set_resizable(True)
        self.treeview.append_column(column_date)

        # Category Columns
        for i, cat in enumerate(KC_CATEGORIES):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(cat, renderer, text=i+1)
            column.set_resizable(True)
            self.treeview.append_column(column)
        
        # We don't show comments in the treeview to save space
        
        scrolled_window.add(self.treeview)

        # --- Button Box ---
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        main_box.pack_start(button_box, False, False, 0)

        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        button_box.pack_start(refresh_button, False, False, 0)

        export_button = Gtk.Button(label="Export to CSV")
        export_button.connect("clicked", self._on_export_clicked)
        button_box.pack_start(export_button, False, False, 0)

        clear_button = Gtk.Button(label="Clear History")
        clear_button.get_style_context().add_class("destructive-action")
        clear_button.connect("clicked", self._on_clear_history_clicked)
        button_box.pack_start(clear_button, False, False, 0)

        # Comments Editor
        comments_label = Gtk.Label(label="<b>Comments for Selected Date</b>")
        comments_label.set_use_markup(True)
        main_box.pack_start(comments_label, False, False, 0)
        
        self.comments_view = Gtk.TextView()
        self.comments_view.set_wrap_mode(Gtk.WrapMode.WORD)
        comments_scrolled = Gtk.ScrolledWindow()
        comments_scrolled.set_min_content_height(100)
        comments_scrolled.add(self.comments_view)
        main_box.pack_start(comments_scrolled, False, False, 0)
        
        save_comments_button = Gtk.Button(label="Save Comments")
        save_comments_button.connect("clicked", self._on_save_comments_clicked)
        main_box.pack_start(save_comments_button, False, False, 0)
        
        # Connect selection change
        self.treeview.get_selection().connect("changed", self._on_selection_changed)
        
        self._load_stats()
        self.show_all()

    def _on_delete_event(self, widget, event):
        self.hide()
        return True

    def _on_selection_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is not None:
            # Comments is at the last index
            comments_idx = len(KC_CATEGORIES) + 1
            comments = model.get_value(iter, comments_idx)
            buffer = self.comments_view.get_buffer()
            buffer.set_text(comments if comments else "")

    def _on_save_comments_clicked(self, button):
        selection = self.treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is not None:
            date = model.get_value(iter, 0)
            buffer = self.comments_view.get_buffer()
            comments = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
            
            logs = self.stats_manager.load()
            for entry in logs:
                if entry.get("date") == date:
                    entry["comments"] = comments
                    break
            
            with open(STATS_LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
            
            comments_idx = len(KC_CATEGORIES) + 1
            model.set_value(iter, comments_idx, comments)
            print(f"Comments saved for {date}")

    def _on_refresh_clicked(self, button):
        self._load_stats()

    def _on_export_clicked(self, button):
        # Implementation similar to previous but handles multi-columns
        dialog = Gtk.FileChooserDialog(title="Export CSV", parent=self, action=Gtk.FileChooserAction.SAVE, modal=True)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT)
        dialog.set_current_name(f"teatime_stats_{datetime.now().strftime('%Y-%m-%d')}.csv")
        
        try:
            response = dialog.run()
            if response == Gtk.ResponseType.ACCEPT:
                filename = dialog.get_filename()
                if not filename.endswith(".csv"): filename += ".csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    header = ["Date"] + KC_CATEGORIES + ["Comments"]
                    writer.writerow(header)
                    for row in self.store:
                        writer.writerow([row[i] for i in range(len(row))])
                print(f"Exported stats to {filename}")
        finally:
            dialog.destroy()

    def _on_clear_history_clicked(self, button):
        dialog = Gtk.MessageDialog(parent=self, modal=True, message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO, text="Clear all history?")
        if dialog.run() == Gtk.ResponseType.YES:
            if STATS_LOG_FILE.exists(): STATS_LOG_FILE.unlink()
            self.store.clear()
            self._reset_summary_labels()
        dialog.destroy()

    def _reset_summary_labels(self):
        self.total_sessions_label.set_text("Total Sessions: 0")
        self.total_time_label.set_text("Total Time: 0 minutes")
        self.avg_duration_label.set_text("Average Duration: 0 minutes")

    def _load_stats(self):
        self.store.clear()
        logs = self.stats_manager.load()
        if not logs:
            self._reset_summary_labels()
            return

        total_duration = 0
        total_sessions = 0
        
        # Sort logs by date newest first
        sorted_logs = sorted(logs, key=lambda x: x.get("date", ""), reverse=True)
        
        for entry in sorted_logs:
            row = [entry.get("date", "Unknown")]
            day_sum = 0
            for cat in KC_CATEGORIES:
                val = entry.get(cat, 0)
                row.append(str(val))
                # Calculate numeric sum for this entry
                if isinstance(val, str) and "+" in val:
                    try:
                        day_sum += sum(int(x) for x in val.split("+") if x.isdigit())
                    except: pass
                elif str(val).isdigit():
                    day_sum += int(val)
            
            row.append(entry.get("comments", ""))
            self.store.append(row)
            total_duration += day_sum
            total_sessions += 1 # This is per-day sessions in this logic, or we can count entries

        self.total_sessions_label.set_text(f"Total Days Tracked: {len(sorted_logs)}")
        self.total_time_label.set_text(f"Total Time: {total_duration} minutes")
        if sorted_logs:
            self.avg_duration_label.set_text(f"Avg Time/Day: {total_duration/len(sorted_logs):.1f} min")

class TeaTimerApp(Gtk.Application):
    def __init__(self, duration=5, auto_start=False):
        super().__init__(application_id="org.genidma.KCResonance",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.window = None
        self.timer_id = None
        self.time_left = 0
        self.current_timer_duration = 0
        self.font_scale_factor = DEFAULT_FONT_SCALE
        self.last_duration = duration
        self.sound_enabled = True
        self.rainbow_timer_id = None
        self.css_provider = Gtk.CssProvider()
        self._stats_window = None
        self.rainbow_hue = 0
        self.focus_hue = 0
        self.sprite_frames = []
        self.current_sprite_frame = 0
        self.sprite_timer_id = None
        self.auto_start = auto_start
        self.mini_mode = False
        self.nano_mode = False
        self.pre_timer_mode = None
        self.selected_categories = [] 
        self.preferred_skin = "default"
        self.preferred_animation = "test_animation"
        self.rainbow_hue = 0
        self.rainbow_timer_id = None
        
        self._load_config()
        self._setup_actions()

    def _setup_actions(self):
        actions = [
            ("start", self.on_start_clicked, ["<Control>s"]),
            ("stop", self.on_stop_clicked, ["<Control>t"]),
            ("increase-font", self.on_increase_font_clicked, ["<Control>plus", "<Control>equal"]),
            ("decrease-font", self.on_decrease_font_clicked, ["<Control>minus"]),
            ("toggle-sound", self.on_toggle_sound_activated, ["<Control>m"]),
            ("toggle-mini-mode", self.on_toggle_mini_mode_activated, ["<Control>d"]),
            ("quit", lambda a, p: self.quit(), ["<Control>q"])
        ]
        for name, callback, accels in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            self.set_accels_for_action(f"app.{name}", accels)

    def do_activate(self):
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self, title=APP_NAME)
            self.window.set_default_size(400, 300)
            self.window.connect("destroy", self._on_window_destroy)
            self.window.connect("set-focus-child", self._on_focus_changed)

            header_bar = Gtk.HeaderBar(show_close_button=True, title=APP_NAME)
            self.window.set_titlebar(header_bar)

            menu = Gtk.Menu()
            items = [("_Statistics", self.on_stats_activated), ("S_ettings", self.on_settings_activated), ("_About", self.on_about_activated)]
            for label, callback in items:
                item = Gtk.MenuItem(label=label, use_underline=True)
                item.connect("activate", callback)
                menu.append(item)
            menu.show_all()
            
            menu_btn = Gtk.MenuButton(popup=menu)
            menu_btn.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
            header_bar.pack_end(menu_btn)

            self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=20)
            self.window.add(self.main_box)

            content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            self.main_box.pack_start(content_box, True, True, 0)
            self.content_box = content_box

            self.time_label = Gtk.Label(label="00:00")
            self.time_label.get_style_context().add_class("time-display")
            self.main_box.pack_start(self.time_label, False, False, 0)

            self.control_grid = Gtk.Grid(column_spacing=10, row_spacing=10, halign=Gtk.Align.CENTER)
            content_box.pack_start(self.control_grid, True, True, 0)

            # Row 0: Duration
            self.control_grid.attach(Gtk.Label(label="Minutes:"), 0, 0, 1, 1)
            self.duration_spin = Gtk.SpinButton.new_with_range(1, 999, 1)
            self.duration_spin.set_value(self.last_duration)
            self.control_grid.attach(self.duration_spin, 1, 0, 1, 1)

            # Row 1: CATEGORY GRID (REDESIGN)
            cat_frame = Gtk.Frame(label="Categories")
            cat_grid = Gtk.Grid(column_spacing=10, row_spacing=5, margin=10)
            self.category_checkboxes = {}
            for i, cat in enumerate(KC_CATEGORIES):
                cb = Gtk.CheckButton(label=cat)
                cat_grid.attach(cb, i % 4, i // 4, 1, 1)
                self.category_checkboxes[cat] = cb
            cat_frame.add(cat_grid)
            self.category_ui = cat_frame
            self.control_grid.attach(cat_frame, 0, 1, 2, 1)

            # Row 2: Controls
            self.start_button = Gtk.Button(label="Start")
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button = Gtk.Button(label="Stop", sensitive=False)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            self.control_grid.attach(self.start_button, 0, 2, 1, 1)
            self.control_grid.attach(self.stop_button, 1, 2, 1, 1)

            # Row 3: Font
            btn_minus = Gtk.Button(label="A-")
            btn_minus.connect("clicked", self.on_decrease_font_clicked)
            btn_plus = Gtk.Button(label="A+")
            btn_plus.connect("clicked", self.on_increase_font_clicked)
            self.control_grid.attach(btn_minus, 0, 3, 1, 1)
            self.control_grid.attach(btn_plus, 1, 3, 1, 1)

            # Row 4: Sound Toggle
            self.sound_toggle = Gtk.CheckButton(label="Enable Sound", active=self.sound_enabled)
            self.sound_toggle.connect("toggled", self.on_sound_toggled)
            self.control_grid.attach(self.sound_toggle, 0, 4, 2, 1)

            # Row 5: Mini Mode Toggle (FIXED OVERLAP)
            self.mini_mode_toggle = Gtk.CheckButton(label="Mini Mode", active=self.mini_mode)
            self.mini_mode_toggle.connect("toggled", self.on_mini_mode_toggled)
            self.control_grid.attach(self.mini_mode_toggle, 0, 5, 2, 1)

            # Row 6: Nano Mode Toggle
            self.nano_mode_toggle = Gtk.CheckButton(label="Nano Mode (auto)", active=self.nano_mode)
            self.nano_mode_toggle.connect("toggled", self.on_nano_mode_toggled)
            self.control_grid.attach(self.nano_mode_toggle, 0, 6, 2, 1)

            # Presets
            self.presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, halign=Gtk.Align.CENTER)
            content_box.pack_start(self.presets_box, False, False, 0)
            self.presets_box.add(Gtk.Label(label="<b>Presets</b>", use_markup=True))
            for mins in [15, 30, 45, 60]:
                btn = Gtk.Button(label=f"{mins}m")
                btn.connect("clicked", lambda b, m=mins: self.on_preset_clicked(b, m))
                self.presets_box.add(btn)

            screen = Gdk.Screen.get_default()
            if screen: Gtk.StyleContext.add_provider_for_screen(screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

            self._apply_font_size()
            self._apply_skin()

        self.window.show_all()
        self._apply_mini_mode()
        self._start_rainbow_timer()
        if self.auto_start: GLib.idle_add(self.on_start_clicked)

    def on_stats_activated(self, *args):
        if not self._stats_window:
            self._stats_window = StatisticsWindow(self, self.window)
        else:
            self._stats_window.present()

    def on_about_activated(self, *args):
        dialog = Gtk.AboutDialog(transient_for=self.window, modal=True, program_name=APP_NAME, version=APP_VERSION, copyright="Copyright 2026", license_type=Gtk.License.MIT_X11)
        dialog.run(); dialog.destroy()

    def on_start_clicked(self, *args):
        if self.nano_mode:
            self.pre_timer_mode = 'mini' if self.mini_mode else 'normal'
            self._activate_nano_mode()
        
        self._stop_rainbow_timer()
        duration = int(self.duration_spin.get_value())
        self.time_left = duration * 60
        self.current_timer_duration = duration
        self._update_label()
        
        self.timer_id = GLib.timeout_add_seconds(5, self.update_timer)
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)

    def on_stop_clicked(self, *args):
        self.stop_timer()
        self._restore_pre_timer_mode()
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self.time_label.set_text("00:00")

    def stop_timer(self):
        if self.timer_id: GLib.source_remove(self.timer_id); self.timer_id = None

    def update_timer(self):
        self.time_left -= 5
        self._update_label()
        if self.time_left <= 0:
            self.on_timer_complete()
            return False
        return True

    def _update_label(self):
        m, s = divmod(self.time_left, 60)
        self.time_label.set_markup(f"<span font_desc='Bold 32'>{m:02d}:{s:02d}</span>")

    def on_timer_complete(self):
        self.stop_timer()
        self.time_label.set_markup("<span foreground='green'>Done!</span>")
        self._play_notification_sound()
        self._log_timer_completion()
        self._show_fullscreen_notification()
        self._restore_pre_timer_mode()
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self._start_rainbow_timer()

    def _show_fullscreen_notification(self):
        win = Gtk.Window(type=Gtk.WindowType.POPUP)
        win.set_keep_above(True); win.fullscreen()
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, valign=Gtk.Align.CENTER)
        win.add(box)
        
        label = Gtk.Label()
        label.set_markup("<span font_desc='Sans Bold 60' foreground='white'>Session Complete</span>")
        box.pack_start(label, False, False, 0)
        
        # Sprite Animation
        frames = self._load_sprite_frames()
        if frames:
            da = Gtk.DrawingArea(); da.set_size_request(400, 400)
            da.connect("draw", self._on_sprite_draw, frames)
            box.pack_start(da, False, False, 0)
            GLib.timeout_add(100, lambda: (da.queue_draw(), True)[1])

        win.get_style_context().add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        win.connect("button-press-event", lambda w, e: win.destroy())
        GLib.timeout_add_seconds(10, win.destroy)
        win.show_all()

    def _load_sprite_frames(self):
        frames = []
        anim = getattr(self, 'preferred_animation', 'test_animation')
        path = Path(__file__).parent.parent / "assets" / "sprites" / anim
        if not path.exists():
            path = Path(__file__).parent.parent / "assets" / "sprites" / "test_animation"
            
        if path.exists():
            files = sorted(list(path.glob("*.png")))
            for f in files:
                try: 
                    pix = GdkPixbuf.Pixbuf.new_from_file(str(f))
                    if pix: frames.append(pix)
                except Exception as e:
                    print(f"Error loading frame {f}: {e}")
        return frames

    def _on_sprite_draw(self, widget, cr, frames):
        if not frames: return False
        cur = (int(time.time() * 10)) % len(frames)
        pix = frames[cur]
        
        alloc = widget.get_allocation()
        pw, ph = pix.get_width(), pix.get_height()
        scale = min(alloc.width / pw, alloc.height / ph)
        
        sw, sh = int(pw * scale), int(ph * scale)
        scaled = pix.scale_simple(sw, sh, GdkPixbuf.InterpType.BILINEAR)
        
        Gdk.cairo_set_source_pixbuf(cr, scaled, (alloc.width - sw) // 2, (alloc.height - sh) // 2)
        cr.paint(); return False

    def _log_timer_completion(self):
        today = datetime.now().strftime("%Y-%m-%d")
        logs = StatsManager().load()
        
        selected_data = {}
        for cat, cb in self.category_checkboxes.items():
            if cb.get_active():
                selected_data[cat] = self.current_timer_duration
        
        if not selected_data:
            selected_data = {"General": self.current_timer_duration}

        entry = next((e for e in logs if e.get("date") == today), None)
        if not entry:
            entry = {"date": today, "comments": ""}
            for cat in KC_CATEGORIES: entry[cat] = 0
            logs.append(entry)
        
        for cat, duration in selected_data.items():
            if cat not in entry: entry[cat] = 0
            
            curr = entry.get(cat, 0)
            if str(curr) == "0": 
                entry[cat] = duration
            else: 
                entry[cat] = f"{curr}+{duration}"
            
        with open(STATS_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

    def _play_notification_sound(self):
        if self.sound_enabled:
            # Fallback beep or simple sound command
            subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], stderr=subprocess.DEVNULL)
            print("\a") # terminal beep

    def on_mini_mode_toggled(self, widget):
        self.mini_mode = widget.get_active()
        self._apply_mini_mode()

    def on_nano_mode_toggled(self, widget):
        self.nano_mode = widget.get_active()

    def _activate_nano_mode(self):
        self.window.set_decorated(False)
        self.content_box.set_visible(False)
        self.category_ui.set_visible(False)
        self.window.resize(100, 50)

    def _restore_pre_timer_mode(self):
        self.window.set_decorated(True)
        self.content_box.set_visible(True)
        self.category_ui.set_visible(True)
        self._apply_mini_mode()

    def _apply_mini_mode(self):
        if self.mini_mode:
            self.presets_box.set_visible(False)
            self.window.resize(200, 150)
        else:
            self.presets_box.set_visible(True)
            self.window.resize(400, 300)

    def on_increase_font_clicked(self, *args):
        self.font_scale_factor = min(MAX_FONT_SCALE, self.font_scale_factor + 0.1)
        self._apply_font_size()

    def on_decrease_font_clicked(self, *args):
        self.font_scale_factor = max(MIN_FONT_SCALE, self.font_scale_factor - 0.1)
        self._apply_font_size()

    def _apply_font_size(self):
        scale = self.font_scale_factor * 100
        css = f".time-display {{ font-size: {scale*2}%; }} label, button {{ font-size: {scale}%; }}"
        self.css_provider.load_from_data(css.encode())

    def _apply_skin(self):
        skin = self.preferred_skin
        if skin == 'lava':
            h1 = self.rainbow_hue
            h2 = (self.rainbow_hue + 120) % 360
            h3 = (self.rainbow_hue + 240) % 360
            r1, g1, b1 = colorsys.hsv_to_rgb(h1 / 360.0, 0.8, 0.7)
            r2, g2, b2 = colorsys.hsv_to_rgb(h2 / 360.0, 0.8, 0.7)
            r3, g3, b3 = colorsys.hsv_to_rgb(h3 / 360.0, 0.8, 0.7)
            c1 = f"rgb({int(r1*255)}, {int(g1*255)}, {int(b1*255)})"
            c2 = f"rgb({int(r2*255)}, {int(g2*255)}, {int(b2*255)})"
            c3 = f"rgb({int(r3*255)}, {int(g3*255)}, {int(b3*255)})"
            
            css = f"""
            window {{
                background: linear-gradient(45deg, {c1}, {c2}, {c3});
                background-size: 300% 300%;
                animation: lavaFlow 20s ease infinite;
            }}
            @keyframes lavaFlow {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            """
            provider = Gtk.CssProvider()
            provider.load_from_data(css.encode())
            self.window.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
        else:
            # Default or reset
            self.window.get_style_context().remove_class("lava-skin") # Just in case

    def _start_rainbow_timer(self):
        if self.rainbow_timer_id: GLib.source_remove(self.rainbow_timer_id)
        self.rainbow_timer_id = GLib.timeout_add(1000, self._update_rainbow)

    def _stop_rainbow_timer(self):
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
            self.rainbow_timer_id = None

    def _update_rainbow(self):
        self.rainbow_hue = (self.rainbow_hue + 1) % 360
        self._apply_skin()
        return True

    def on_sound_toggled(self, btn):
        self.sound_enabled = btn.get_active()

    def _on_window_destroy(self, *args):
        self._save_config()
        self.quit()

    def _save_config(self):
        config = {
            "font_scale_factor": self.font_scale_factor,
            "last_duration": int(self.duration_spin.get_value()),
            "mini_mode": self.mini_mode,
            "nano_mode": self.nano_mode,
            "sound_enabled": self.sound_enabled,
            "preferred_skin": self.preferred_skin,
            "preferred_animation": self.preferred_animation
        }
        with open(CONFIG_FILE, 'w') as f: json.dump(config, f, indent=2)

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    c = json.load(f)
                    self.font_scale_factor = c.get("font_scale_factor", DEFAULT_FONT_SCALE)
                    self.last_duration = c.get("last_duration", 5)
                    self.mini_mode = c.get("mini_mode", False)
                    self.nano_mode = c.get("nano_mode", False)
                    self.sound_enabled = c.get("sound_enabled", True)
                    self.preferred_skin = c.get("preferred_skin", "default")
                    self.preferred_animation = c.get("preferred_animation", "test_animation")
            except: pass

    def on_preset_clicked(self, btn, mins):
        self.duration_spin.set_value(mins)
        self.on_start_clicked()

    def on_settings_activated(self, *args):
        self.show_settings_dialog()

    def show_settings_dialog(self):
        dialog = Gtk.Dialog(title="Settings", parent=self.window, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_default_size(300, 200)
        content = dialog.get_content_area()
        grid = Gtk.Grid(row_spacing=10, column_spacing=10, margin=15)
        content.add(grid)
        
        # Skin selection
        grid.attach(Gtk.Label(label="Skin:"), 0, 0, 1, 1)
        skin_combo = Gtk.ComboBoxText()
        skin_combo.append("default", "Default")
        skin_combo.append("lava", "Lava Lamp")
        skin_combo.set_active_id(self.preferred_skin)
        grid.attach(skin_combo, 1, 0, 1, 1)
        
        # Animation selection
        grid.attach(Gtk.Label(label="Animation:"), 0, 1, 1, 1)
        anim_combo = Gtk.ComboBoxText()
        # Find animations in assets/sprites/
        sprites_path = Path(__file__).parent.parent / "assets" / "sprites"
        if sprites_path.exists():
            for d in sprites_path.iterdir():
                if d.is_dir(): anim_combo.append(d.name, d.name.replace("_", " ").title())
        anim_combo.set_active_id(self.preferred_animation)
        grid.attach(anim_combo, 1, 1, 1, 1)
        
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            self.preferred_skin = skin_combo.get_active_id()
            self.preferred_animation = anim_combo.get_active_id()
            self._save_config()
            self._apply_skin()
        dialog.destroy()

    def on_toggle_sound_activated(self, *args):
        self.sound_toggle.set_active(not self.sound_toggle.get_active())

    def on_toggle_mini_mode_activated(self, *args):
        self.mini_mode_toggle.set_active(not self.mini_mode_toggle.get_active())

    def _on_focus_changed(self, *args):
        pass


if __name__ == "__main__":
    app = TeaTimerApp()
    app.run(sys.argv)
