from datetime import datetime
import csv
import json
from pathlib import Path

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, Pango, GdkPixbuf

from .core import STATS_LOG_FILE, EVENT_LOG_FILE, StatsManager, KC_CATEGORIES

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
        
        # Filtered categories for data operations
        self.data_categories = [c for c in KC_CATEGORIES if c.strip()]

        # Model: Date (str), N categories (str), Comments (str)
        types = [str] * (len(self.data_categories) + 2)
        self.store = Gtk.ListStore(*types)
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_headers_clickable(True)

        # Date Column
        renderer_text = Gtk.CellRendererText()
        column_date = Gtk.TreeViewColumn("Date", renderer_text, text=0)
        column_date.set_sort_column_id(0)
        column_date.set_resizable(True)
        self.treeview.append_column(column_date)

        # Category Columns
        for i, cat in enumerate(self.data_categories):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(cat, renderer, text=i+1)
            column.set_resizable(True)
            if cat.lower() == "breaks":
                column.set_clickable(True)
                header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                header_title = Gtk.Label(label="Breaks")
                self.flow_button = Gtk.Button(label="Flow")
                self.flow_button.set_tooltip_text("Show flow timeline")
                self.flow_button.connect("clicked", self._on_flow_clicked)
                self.breaks_today_label = Gtk.Label(label="Today: 0m")
                header_title.set_halign(Gtk.Align.CENTER)
                self.flow_button.set_halign(Gtk.Align.CENTER)
                self.breaks_today_label.set_halign(Gtk.Align.CENTER)
                header_box.pack_start(header_title, False, False, 0)
                header_box.pack_start(self.flow_button, False, False, 0)
                header_box.pack_start(self.breaks_today_label, False, False, 0)
                header_box.show_all()
                column.set_widget(header_box)
            self.treeview.append_column(column)
        
        # We don't show comments in the treeview to save space
        
        scrolled_window.add(self.treeview)

        # --- Button Box ---
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        main_box.pack_start(button_box, False, False, 0)

        refresh_button = Gtk.Button(label="_Refresh", use_underline=True)
        refresh_button.connect("clicked", self._on_refresh_clicked)
        button_box.pack_start(refresh_button, False, False, 0)

        export_button = Gtk.Button(label="_Export to CSV", use_underline=True)
        export_button.connect("clicked", self._on_export_clicked)
        button_box.pack_start(export_button, False, False, 0)

        clear_button = Gtk.Button(label="_Clear History", use_underline=True)
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
            comments_idx = len(self.data_categories) + 1
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
            
            comments_idx = len(self.data_categories) + 1
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
                    header = ["Date"] + self.data_categories + ["Comments"]
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

    def _load_events(self):
        if not EVENT_LOG_FILE.exists():
            return []
        events = []
        try:
            with open(EVENT_LOG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except:
                        pass
        except:
            return []
        return events

    def _on_flow_clicked(self, button):
        if hasattr(self, "_flow_popup") and self._flow_popup:
            self._flow_popup.destroy()
            self._flow_popup = None

        popup = Gtk.Window(type=Gtk.WindowType.POPUP)
        popup.set_transient_for(self)
        popup.set_decorated(False)
        popup.set_skip_taskbar_hint(True)
        popup.set_skip_pager_hint(True)
        popup.set_border_width(8)

        frame = Gtk.Frame(label="Flow Timeline (Today)")
        da = Gtk.DrawingArea()
        da.set_size_request(520, 140)
        frame.add(da)
        popup.add(frame)

        events = self._load_events()
        today = datetime.now().strftime("%Y-%m-%d")
        todays = []
        for e in events:
            ts_end = e.get("ts_end")
            if ts_end and ts_end.startswith(today):
                todays.append(e)

        def draw_timeline(widget, cr):
            alloc = widget.get_allocation()
            w, h = alloc.width, alloc.height
            if w <= 0 or h <= 0:
                return False

            pad = 20
            y = h / 2
            cr.set_source_rgba(0.6, 0.6, 0.6, 0.5)
            cr.set_line_width(2)
            cr.move_to(pad, y)
            cr.line_to(w - pad, y)
            cr.stroke()

            if not todays:
                return False

            def parse_ts(ts):
                try:
                    return datetime.fromisoformat(ts)
                except:
                    return None

            day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start.replace(hour=23, minute=59, second=59)
            span = (day_end - day_start).total_seconds()

            for e in todays:
                start = parse_ts(e.get("ts_start"))
                end = parse_ts(e.get("ts_end"))
                if not start or not end:
                    continue
                sx = pad + ((start - day_start).total_seconds() / span) * (w - pad * 2)
                ex = pad + ((end - day_start).total_seconds() / span) * (w - pad * 2)
                cats = e.get("categories", [])
                is_break = any(str(c).lower() == "breaks" for c in cats)

                cr.set_source_rgba(0.2, 0.7, 1.0, 0.9)
                cr.set_line_width(6)
                cr.move_to(sx, y)
                cr.line_to(ex, y)
                cr.stroke()

                if is_break:
                    cr.set_source_rgba(1.0, 0.6, 0.2, 0.95)
                    cr.arc(ex, y, 6, 0, 2 * 3.14159)
                    cr.fill()
                    cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
                    cr.select_font_face("Sans", 0, 0)
                    cr.set_font_size(12)
                    cr.move_to(ex + 8, y - 6)
                    cr.show_text("☕")

            return False

        da.connect("draw", draw_timeline)

        def close_popup(*args):
            popup.destroy()
            self._flow_popup = None
            return False

        popup.connect("button-press-event", close_popup)
        popup.connect("key-press-event", close_popup)

        popup.show_all()
        popup.grab_add()
        popup.grab_focus()
        popup.present()
        self._flow_popup = popup

    def _reset_summary_labels(self):
        self.total_sessions_label.set_text("Total Sessions: 0")
        self.total_time_label.set_text("Total Time: 0 minutes")
        self.avg_duration_label.set_text("Average Duration: 0 minutes")
        if hasattr(self, "breaks_today_label") and self.breaks_today_label:
            self.breaks_today_label.set_text("Today: 0m")

    def _load_stats(self):
        self.store.clear()
        logs = self.stats_manager.load()
        if not logs:
            self._reset_summary_labels()
            return

        def _parse_minutes(val):
            try:
                if isinstance(val, str):
                    nums = [int(x) for x in __import__("re").findall(r"\d+", val)]
                    return sum(nums) if nums else 0
                if str(val).isdigit():
                    return int(val)
            except:
                pass
            return 0

        total_duration = 0
        total_sessions = 0
        
        # Sort logs by date newest first
        sorted_logs = sorted(logs, key=lambda x: x.get("date", ""), reverse=True)
        
        for entry in sorted_logs:
            row = [entry.get("date", "Unknown")]
            day_sum = 0
            for cat in self.data_categories:
                val = entry.get(cat, 0)
                row.append(str(val))
                # Calculate numeric sum for this entry
                day_sum += _parse_minutes(val)
            
            row.append(entry.get("comments", ""))
            self.store.append(row)
            total_duration += day_sum
            total_sessions += 1 # This is per-day sessions in this logic, or we can count entries

        self.total_sessions_label.set_text(f"Total Days Tracked: {len(sorted_logs)}")
        self.total_time_label.set_text(f"Total Time: {total_duration} minutes")
        if sorted_logs:
            self.avg_duration_label.set_text(f"Avg Time/Day: {total_duration/len(sorted_logs):.1f} min")

        if hasattr(self, "breaks_today_label") and self.breaks_today_label:
            today = datetime.now().strftime("%Y-%m-%d")
            today_entry = next((e for e in logs if e.get("date") == today), None)
            breaks_total = 0
            if today_entry:
                for cat in self.data_categories:
                    if cat.lower() == "breaks":
                        breaks_total = _parse_minutes(today_entry.get(cat, 0))
                        break
            self.breaks_today_label.set_text(f"Today: {breaks_total}m")
