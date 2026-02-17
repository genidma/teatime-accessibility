from datetime import datetime, timedelta
import csv
import json
import traceback

import gi
# Use GTK 3 for better compatibility
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, Pango, GdkPixbuf

from .core import (
    STATS_LOG_FILE,
    EVENT_LOG_FILE,
    StatsManager,
    KC_CATEGORIES,
    format_category_label,
    get_category_icon_path,
)

def _set_checkbutton_icon_label(button, category):
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
    icon_path = get_category_icon_path(category)
    if icon_path:
        img = Gtk.Image.new_from_file(icon_path)
        row.pack_start(img, False, False, 0)
    txt = Gtk.Label(label=format_category_label(category))
    txt.set_xalign(0.0)
    row.pack_start(txt, False, False, 0)
    button.add(row)

def _parse_iso_ts(ts):
    try:
        return datetime.fromisoformat(ts)
    except:
        return None

def _parse_minutes_value(val):
    try:
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            nums = [int(x) for x in __import__("re").findall(r"\d+", val)]
            return sum(nums) if nums else 0
    except Exception:
        pass
    return 0

def _clip_interval_to_day(start, end, day_start, day_end):
    if not start or not end:
        return None
    if end < day_start or start > day_end:
        return None
    return max(start, day_start), min(end, day_end)

def _event_matches_category(event, category_filter):
    if not category_filter or category_filter == "All":
        return True
    if isinstance(category_filter, (list, tuple, set)):
        wanted = {str(c).strip().lower() for c in category_filter if str(c).strip()}
        if not wanted:
            return True
        cats = event.get("categories", []) or event.get("category", [])
        return any(str(c).strip().lower() in wanted for c in cats)
    cats = event.get("categories", []) or event.get("category", [])
    return any(str(c).lower() == category_filter.lower() for c in cats)

def _collect_rhythm_segments(events, start_window, end_window, category_filter="All"):
    by_day = {}
    for e in events:
        if not _event_matches_category(e, category_filter):
            continue
        start = _parse_iso_ts(e.get("ts_start"))
        end = _parse_iso_ts(e.get("ts_end"))
        clipped = _clip_interval_to_day(start, end, start_window, end_window)
        if not clipped:
            continue

        seg_start, seg_end = clipped
        if seg_end <= seg_start:
            continue

        day_key = seg_start.strftime("%Y-%m-%d")
        start_min = seg_start.hour * 60 + seg_start.minute + seg_start.second / 60.0
        end_min = seg_end.hour * 60 + seg_end.minute + seg_end.second / 60.0
        by_day.setdefault(day_key, []).append((start_min, end_min))

    for day in by_day:
        by_day[day].sort(key=lambda x: x[0])

    return by_day

def _collect_rhythm_segments_detailed(events, start_window, end_window, category_filter="All"):
    by_day = {}
    for e in events:
        if not _event_matches_category(e, category_filter):
            continue
        start = _parse_iso_ts(e.get("ts_start")) or _parse_iso_ts(e.get("start")) or _parse_iso_ts(e.get("start_ts"))
        end = _parse_iso_ts(e.get("ts_end")) or _parse_iso_ts(e.get("end")) or _parse_iso_ts(e.get("end_ts"))
        if (not start or not end) and start:
            duration = _parse_minutes_value(e.get("duration_min", 0))
            if duration > 0:
                end = start + timedelta(minutes=duration)
        clipped = _clip_interval_to_day(start, end, start_window, end_window)
        if not clipped:
            continue

        seg_start, seg_end = clipped
        if seg_end <= seg_start:
            continue

        cats = e.get("categories", []) or e.get("category", [])
        if isinstance(cats, str):
            cats = [cats]
        if not isinstance(cats, list):
            cats = []

        day_key = seg_start.strftime("%Y-%m-%d")
        start_min = seg_start.hour * 60 + seg_start.minute + seg_start.second / 60.0
        end_min = seg_end.hour * 60 + seg_end.minute + seg_end.second / 60.0
        by_day.setdefault(day_key, []).append(
            {
                "start_min": start_min,
                "end_min": end_min,
                "cats": [str(c) for c in cats],
            }
        )

    for day in by_day:
        by_day[day].sort(key=lambda x: x["start_min"])

    return by_day

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
            column = Gtk.TreeViewColumn(format_category_label(cat), renderer, text=i+1)
            column.set_resizable(True)
            if cat.lower() == "breaks":
                column.set_clickable(True)
                header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                header_title = Gtk.Label(label="Breaks")
                self.breaks_today_label = Gtk.Label(label="Today: 0m")
                header_title.set_halign(Gtk.Align.CENTER)
                self.breaks_today_label.set_halign(Gtk.Align.CENTER)
                header_box.pack_start(header_title, False, False, 0)
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

        kcresonance_frame = Gtk.Frame(label="kcresonance")
        kcresonance_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            halign=Gtk.Align.CENTER,
            margin=8,
        )
        kcresonance_frame.add(kcresonance_row)
        main_box.pack_start(kcresonance_frame, False, False, 0)

        flow_quick_button = Gtk.Button(label="Flow")
        flow_quick_button.set_tooltip_text("Show flow timeline")
        flow_quick_button.connect("clicked", self._on_flow_clicked)
        kcresonance_row.pack_start(flow_quick_button, False, False, 0)

        rhythm_quick_button = Gtk.Button(label="Rhythm")
        rhythm_quick_button.set_tooltip_text("Show daily rhythm graph")
        rhythm_quick_button.connect("clicked", self._on_rhythm_clicked)
        kcresonance_row.pack_start(rhythm_quick_button, False, False, 0)

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
                        row_data = []
                        for i, val in enumerate(row):
                            # Indices: 0 is Date, last is Comments. Everything in between is data.
                            # len(row) = 1 (Date) + len(self.data_categories) + 1 (Comments)
                            is_data_category = 1 <= i <= len(self.data_categories)
                            
                            new_val = val
                            if is_data_category:
                                should_prepend = False
                                # Check if it's a digit > 1
                                if isinstance(val, str) and val.isdigit():
                                    try:
                                        if int(val) > 1:
                                            should_prepend = True
                                    except ValueError: pass
                                elif isinstance(val, int) and val > 1:
                                     should_prepend = True
                                
                                # Check if it contains '+' (formula)
                                if isinstance(val, str) and '+' in val:
                                    should_prepend = True
                                
                                if should_prepend:
                                    new_val = "=" + str(val)
                            
                            row_data.append(new_val)
                        writer.writerow(row_data)
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

    def _show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            parent=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def _load_events(self):
        events = []
        event_paths = [
            EVENT_LOG_FILE,
            EVENT_LOG_FILE.with_suffix(".json"),
            EVENT_LOG_FILE.with_name("teatime_events.json"),
        ]
        try:
            for path in event_paths:
                if not path.exists():
                    continue
                with open(path, "r") as f:
                    raw = f.read().strip()
                if not raw:
                    continue
                if raw.startswith("["):
                    try:
                        loaded = json.loads(raw)
                        if isinstance(loaded, list):
                            events.extend([e for e in loaded if isinstance(e, dict)])
                            continue
                    except Exception:
                        pass
                for line in raw.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                        if isinstance(row, dict):
                            events.append(row)
                    except Exception:
                        pass
        except:
            return []
        return events

    def _event_categories(self, event):
        cats = event.get("categories", [])
        if isinstance(cats, str):
            return [cats]
        if isinstance(cats, list):
            return cats
        cat = event.get("category")
        if isinstance(cat, list):
            return cat
        if isinstance(cat, str):
            return [cat]
        return []

    def _event_interval(self, event):
        start = (
            _parse_iso_ts(event.get("ts_start"))
            or _parse_iso_ts(event.get("start"))
            or _parse_iso_ts(event.get("start_ts"))
        )
        end = (
            _parse_iso_ts(event.get("ts_end"))
            or _parse_iso_ts(event.get("end"))
            or _parse_iso_ts(event.get("end_ts"))
        )
        if start and end and end > start:
            return start, end
        duration = _parse_minutes_value(event.get("duration_min", 0))
        if start and duration > 0:
            return start, start + timedelta(minutes=duration)
        return None

    def _daily_minutes_from_stats(self, selected_categories):
        logs = self.stats_manager.load() or []
        if not logs:
            return []
        wanted = [str(c).strip().lower() for c in selected_categories if str(c).strip()]
        out = []
        for row in logs:
            day = str(row.get("date", "")).strip()
            if not day:
                continue
            if wanted:
                cats = [c for c in self.data_categories if c.lower() in wanted]
            else:
                cats = list(self.data_categories)
            total = sum(_parse_minutes_value(row.get(cat, 0)) for cat in cats)
            if total > 0:
                out.append((day, total))
        out.sort(key=lambda x: x[0])
        return out

    def _daily_minutes_from_events(self, selected_categories):
        wanted = {str(c).strip().lower() for c in selected_categories if str(c).strip()}
        totals = {}
        for e in self._load_events():
            cats = [str(c).strip().lower() for c in self._event_categories(e)]
            if wanted and not any(c in wanted for c in cats):
                continue
            interval = self._event_interval(e)
            if not interval:
                continue
            start, end = interval
            day = start.strftime("%Y-%m-%d")
            mins = max(0.0, (end - start).total_seconds() / 60.0)
            totals[day] = totals.get(day, 0.0) + mins
        out = sorted([(d, int(round(v))) for d, v in totals.items() if v > 0], key=lambda x: x[0])
        return out

    def _collect_rhythm_segments_fallback(self, events, start_window, end_window, category_filter):
        by_day = _collect_rhythm_segments(events, start_window, end_window, category_filter)
        if by_day:
            return by_day
        if isinstance(category_filter, (list, tuple, set)):
            selected_categories = list(category_filter)
        elif isinstance(category_filter, str) and category_filter != "All":
            selected_categories = [category_filter]
        else:
            selected_categories = []
        daily = self._daily_minutes_from_stats(selected_categories)
        for day, total_min in daily:
            try:
                day_start = datetime.fromisoformat(day).replace(hour=0, minute=0, second=0, microsecond=0)
            except Exception:
                continue
            if day_start < start_window or day_start > end_window:
                continue
            start_min = 12 * 60
            end_min = min(24 * 60, start_min + float(total_min))
            by_day.setdefault(day, []).append((start_min, end_min))
        return by_day

    def _get_selected_categories_from_main(self):
        app = self.get_application()
        if not app:
            return []
        checkboxes = getattr(app, "category_checkboxes", {}) or {}
        selected = []
        for cat, cb in checkboxes.items():
            try:
                if cb.get_active():
                    selected.append(cat)
            except Exception:
                continue
        return selected


    def _on_flow_clicked(self, button):
        try:
            if hasattr(self, "_flow_popup") and self._flow_popup:
                self._flow_popup.destroy()
                self._flow_popup = None

            popup = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
            popup.set_transient_for(self)
            popup.set_modal(False)
            popup.set_title("Flow Timeline")
            popup.set_default_size(560, 180)
            popup.set_border_width(8)

            frame = Gtk.Frame(label="Flow Timeline")
            da = Gtk.DrawingArea()
            da.set_size_request(520, 140)
            frame.add(da)
            popup.add(frame)

            selected_categories = self._get_selected_categories_from_main()
            points = self._daily_minutes_from_stats(selected_categories)
            if not points:
                points = self._daily_minutes_from_events(selected_categories)
            points = points[-21:]
            flow_scope = (
                ", ".join(format_category_label(c) for c in selected_categories)
                if selected_categories
                else "All"
            )
            frame.set_label(f"Flow Timeline ({flow_scope})")

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

                if not points:
                    cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
                    cr.select_font_face("Sans", 0, 0)
                    cr.set_font_size(12)
                    cr.move_to(pad + 6, y - 10)
                    cr.show_text("No flow data for selected categories")
                    return False

                max_minutes = max(m for _, m in points) if points else 1
                span_x = max(1, len(points) - 1)
                dot_positions = []
                for idx, (day, mins) in enumerate(points):
                    x = pad + (idx / span_x) * (w - pad * 2)
                    y_off = (mins / max_minutes) * (h * 0.35)
                    py = y - y_off
                    dot_positions.append((x, py, day, mins))

                cr.set_source_rgba(0.2, 0.7, 1.0, 0.9)
                cr.set_line_width(2)
                for idx, (x, py, _, _) in enumerate(dot_positions):
                    if idx == 0:
                        cr.move_to(x, py)
                    else:
                        cr.line_to(x, py)
                cr.stroke()

                for x, py, day, mins in dot_positions:
                    cr.set_source_rgba(1.0, 0.6, 0.2, 0.95)
                    cr.arc(x, py, 4, 0, 2 * 3.14159)
                    cr.fill()
                    cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
                    cr.select_font_face("Sans", 0, 0)
                    cr.set_font_size(10)
                    cr.move_to(x + 5, py - 4)
                    cr.show_text(f"{mins}m")
                    cr.move_to(x + 5, py + 8)
                    cr.show_text(day[5:])

                return False

            da.connect("draw", draw_timeline)

            popup.connect("delete-event", lambda *args: setattr(self, "_flow_popup", None) or False)
            popup.show_all()
            popup.present()
            self._flow_popup = popup
        except Exception:
            self._show_error_dialog("Flow failed", traceback.format_exc())


    def _on_rhythm_clicked(self, button):
        try:
            if hasattr(self, "_rhythm_popup") and self._rhythm_popup:
                self._rhythm_popup.destroy()
                self._rhythm_popup = None

            popup = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
            popup.set_transient_for(self)
            popup.set_modal(False)
            popup.set_default_size(820, 460)
            popup.set_title("Rhythm Graph")
            popup.set_border_width(10)

            root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            popup.add(root)

            controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            root.pack_start(controls, False, False, 0)

            range_label = Gtk.Label(label="Range")
            range_label.set_halign(Gtk.Align.START)
            controls.pack_start(range_label, False, False, 0)

            range_combo = Gtk.ComboBoxText()
            range_combo.append_text("Last 12 Hours")
            range_combo.append_text("Last 7 Days")
            range_combo.append_text("Last 1 Hour")
            range_combo.append_text("Last 4 Hours")
            range_combo.append_text("Last 24 Hours")
            range_combo.append_text("Today")
            range_combo.append_text("Yesterday")
            range_combo.append_text("Last 3 Days")
            range_combo.append_text("Last 30 Days")
            range_combo.append_text("Last 90 Days")
            range_combo.append_text("Last 6 Months")
            range_combo.append_text("Last 1 Year")
            range_combo.append_text("All Time")
            range_combo.set_active(0)
            controls.pack_start(range_combo, False, False, 0)

            zoom_label = Gtk.Label(label="Zoom")
            zoom_label.set_halign(Gtk.Align.START)
            controls.pack_start(zoom_label, False, False, 0)

            zoom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            controls.pack_start(zoom_box, False, False, 0)
            zoom_hours = {"value": 24}

            categories_frame = Gtk.Frame(label="Categories")
            categories_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=10,
                margin=6,
            )
            categories_frame.add(categories_box)
            root.pack_start(categories_frame, False, False, 0)

            rhythm_category_checks = {}
            all_check = Gtk.CheckButton(label="All")
            all_label = all_check.get_child()
            if isinstance(all_label, Gtk.Label):
                all_label.set_use_markup(True)
                all_label.set_markup("<b>All</b>")
            all_check.set_active(True)
            rhythm_category_checks["All"] = all_check
            categories_box.pack_start(all_check, False, False, 0)

            for cat in self.data_categories:
                cb = Gtk.CheckButton()
                _set_checkbutton_icon_label(cb, cat)
                rhythm_category_checks[cat] = cb
                categories_box.pack_start(cb, False, False, 0)

            chart_host = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            chart_host.set_hexpand(True)
            chart_host.set_vexpand(True)
            root.pack_start(chart_host, True, True, 0)

            status = Gtk.Label(label="")
            status.set_halign(Gtk.Align.START)
            root.pack_start(status, False, False, 0)

            fig = None
            ax_micro = None
            ax_short = None
            ax_long = None
            canvas = None
            try:
                from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
                from matplotlib.figure import Figure
                fig = Figure(figsize=(8, 8), dpi=100)
                ax_micro = fig.add_subplot(311)
                ax_short = fig.add_subplot(312, sharex=ax_micro)
                ax_long = fig.add_subplot(313, sharex=ax_micro)
                canvas = FigureCanvas(fig)
                chart_host.pack_start(canvas, True, True, 0)
                try:
                    from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
                    toolbar = NavigationToolbar(canvas, popup)
                    root.pack_start(toolbar, False, False, 0)
                except Exception:
                    pass
            except Exception as e:
                status.set_text(
                    "Rhythm chart unavailable. Install/verify matplotlib GTK backend "
                    f"(error: {e})."
                )

            def _on_zoom_hours_clicked(_button, hours):
                zoom_hours["value"] = hours
                update_chart()

            for hours in (1, 4, 8, 12, 24):
                zbtn = Gtk.Button(label=f"{hours}h")
                zbtn.connect("clicked", _on_zoom_hours_clicked, hours)
                zoom_box.pack_start(zbtn, False, False, 0)

            def get_rhythm_selected_categories():
                if rhythm_category_checks["All"].get_active():
                    return []
                selected = []
                for cat in self.data_categories:
                    cb = rhythm_category_checks.get(cat)
                    if cb and cb.get_active():
                        selected.append(cat)
                # If none are selected, default back to "All"
                return selected

            def on_all_toggled(btn):
                if btn.get_active():
                    for cat in self.data_categories:
                        cb = rhythm_category_checks.get(cat)
                        if cb and cb.get_active():
                            cb.set_active(False)
                update_chart()

            def on_category_toggled(btn):
                if btn.get_active() and rhythm_category_checks["All"].get_active():
                    rhythm_category_checks["All"].set_active(False)
                if not rhythm_category_checks["All"].get_active():
                    any_selected = any(
                        rhythm_category_checks.get(cat).get_active()
                        for cat in self.data_categories
                        if rhythm_category_checks.get(cat)
                    )
                    if not any_selected:
                        rhythm_category_checks["All"].set_active(True)
                update_chart()

            def update_chart(*args):
                if not fig or not ax_micro or not ax_short or not ax_long or not canvas:
                    return
                mpimg = None
                OffsetImage = None
                AnnotationBbox = None
                text_effects = None
                try:
                    import matplotlib.image as _mpimg
                    from matplotlib.offsetbox import OffsetImage as _OffsetImage, AnnotationBbox as _AnnotationBbox
                    mpimg = _mpimg
                    OffsetImage = _OffsetImage
                    AnnotationBbox = _AnnotationBbox
                except Exception:
                    mpimg = None
                try:
                    import matplotlib.patheffects as pe
                    text_effects = [pe.withStroke(linewidth=1.5, foreground="black")]
                except Exception:
                    text_effects = None

                events = self._load_events()
                now = datetime.now()
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start.replace(hour=23, minute=59, second=59)

                range_name = range_combo.get_active_text() or "Last 12 Hours"
                if range_name == "Last 1 Hour":
                    start_window = now - timedelta(hours=1)
                    end_window = now
                elif range_name == "Last 4 Hours":
                    start_window = now - timedelta(hours=4)
                    end_window = now
                elif range_name == "Last 12 Hours":
                    start_window = now - timedelta(hours=12)
                    end_window = now
                elif range_name == "Last 24 Hours":
                    start_window = now - timedelta(hours=24)
                    end_window = now
                elif range_name == "Today":
                    start_window = today_start
                    end_window = today_end
                elif range_name == "Yesterday":
                    start_window = today_start - timedelta(days=1)
                    end_window = today_start - timedelta(seconds=1)
                elif range_name == "Last 3 Days":
                    start_window = today_start - timedelta(days=2)
                    end_window = today_end
                elif range_name == "Last 7 Days":
                    start_window = today_start - timedelta(days=6)
                    end_window = today_end
                elif range_name == "Last 30 Days":
                    start_window = today_start - timedelta(days=29)
                    end_window = today_end
                elif range_name == "Last 90 Days":
                    start_window = today_start - timedelta(days=89)
                    end_window = today_end
                elif range_name == "Last 6 Months":
                    start_window = today_start - timedelta(days=182)
                    end_window = today_end
                elif range_name == "Last 1 Year":
                    start_window = today_start - timedelta(days=365)
                    end_window = today_end
                elif range_name == "All Time":
                    start_window = datetime.min
                    end_window = datetime.max
                else:
                    start_window = now - timedelta(hours=12)
                    end_window = now

                selected_categories = get_rhythm_selected_categories()
                category_filter = selected_categories if selected_categories else "All"
                by_day_detailed = _collect_rhythm_segments_detailed(
                    events, start_window, end_window, category_filter
                )
                by_day = self._collect_rhythm_segments_fallback(
                    events, start_window, end_window, category_filter
                )

                if selected_categories:
                    status.set_text(
                        "Using selected Categories filter: "
                        + ", ".join(format_category_label(c) for c in selected_categories)
                    )
                else:
                    status.set_text("Using selected Categories filter: All")

                day_keys = sorted(by_day.keys())
                day_based_ranges = {
                    "Today",
                    "Yesterday",
                    "Last 3 Days",
                    "Last 7 Days",
                    "Last 30 Days",
                    "Last 90 Days",
                    "Last 6 Months",
                    "Last 1 Year",
                    "All Time",
                }
                hours = int(zoom_hours["value"])
                all_end_max = None
                for _day in day_keys:
                    for start_min, end_min in by_day.get(_day, []):
                        seg_end = float(end_min)
                        if all_end_max is None or seg_end > all_end_max:
                            all_end_max = seg_end
                if range_name in day_based_ranges:
                    end_min_global = min(24 * 60.0, all_end_max if all_end_max is not None else 24 * 60.0)
                else:
                    end_min_global = now.hour * 60 + now.minute + now.second / 60.0
                if hours >= 24:
                    x_start_global = 0.0
                    x_end_global = 24 * 60.0
                else:
                    span_minutes = float(hours * 60.0)
                    if end_min_global <= span_minutes:
                        x_start_global = 0.0
                        x_end_global = min(24 * 60.0, span_minutes)
                    else:
                        x_start_global = end_min_global - span_minutes
                        x_end_global = end_min_global
                span_global = x_end_global - x_start_global
                if span_global <= 60:
                    step = 10
                elif span_global <= 240:
                    step = 30
                elif span_global <= 480:
                    step = 60
                elif span_global <= 720:
                    step = 120
                else:
                    step = 240
                tick_start = int((x_start_global // step) * step)
                ticks_global = []
                t = tick_start
                while t <= x_end_global + 0.1:
                    if t >= x_start_global - 0.1:
                        ticks_global.append(float(t))
                    t += step
                if not ticks_global:
                    ticks_global = [x_start_global, x_end_global]
                tick_labels_global = [f"{int(v // 60):02d}:{int(v % 60):02d}" for v in ticks_global]

                def _render_axis(ax, title, color, duration_predicate):
                    ax.clear()
                    ax.set_title(title)
                    ax.grid(axis="x", alpha=0.25)

                    if not day_keys:
                        ax.set_yticks([])
                        ax.text(
                            0.5,
                            0.5,
                            "No sessions in selected range/category",
                            ha="center",
                            va="center",
                            color="black",
                            transform=ax.transAxes,
                        )
                        return

                    has_bars = False
                    ytick_positions = []
                    ytick_labels = []
                    y_cursor = 0.0
                    day_gap = 1.2
                    bar_height = 0.62
                    marker_fontsize = 11

                    for day in day_keys:
                        segments = by_day.get(day, [])
                        detailed_segments = by_day_detailed.get(day, [])
                        lane_entries = []

                        # Prefer detailed event segments (with categories) for marker fidelity.
                        if detailed_segments:
                            for d in detailed_segments:
                                start_min = float(d.get("start_min", 0.0))
                                end_min = float(d.get("end_min", 0.0))
                                dur_min = max(0.0, end_min - start_min)
                                if duration_predicate(dur_min):
                                    lane_entries.append(
                                        {
                                            "start": start_min,
                                            "width": max(0.5, dur_min),
                                            "cats": list(d.get("cats", [])),
                                        }
                                    )
                        else:
                            for start_min, end_min in segments:
                                dur_min = max(0.0, end_min - start_min)
                                if duration_predicate(dur_min):
                                    lane_entries.append(
                                        {
                                            "start": float(start_min),
                                            "width": max(0.5, dur_min),
                                            "cats": [],
                                        }
                                    )

                        if not lane_entries:
                            continue

                        # Assign overlap-aware lanes so dense events do not collapse on one row.
                        lane_entries.sort(key=lambda item: item["start"])
                        lane_ends = []
                        for item in lane_entries:
                            lane_idx = None
                            item_end = item["start"] + item["width"]
                            for i, end_pos in enumerate(lane_ends):
                                if item["start"] >= end_pos:
                                    lane_idx = i
                                    break
                            if lane_idx is None:
                                lane_idx = len(lane_ends)
                                lane_ends.append(item_end)
                            else:
                                lane_ends[lane_idx] = item_end
                            item["lane"] = lane_idx

                        lane_count = max(1, len(lane_ends))
                        ytick_positions.append(y_cursor + (lane_count - 1) / 2.0)
                        ytick_labels.append(day)

                        for item in lane_entries:
                            has_bars = True
                            y = y_cursor + item["lane"]
                            ax.broken_barh(
                                [(item["start"], item["width"])],
                                (y - (bar_height / 2.0), bar_height),
                                facecolors=color,
                            )

                            marker_cat = None
                            if item["cats"]:
                                marker_cat = str(item["cats"][0])
                            elif selected_categories:
                                marker_cat = str(selected_categories[0])

                            x_center = item["start"] + (item["width"] / 2.0)
                            if marker_cat and mpimg and OffsetImage and AnnotationBbox:
                                icon_path = get_category_icon_path(marker_cat)
                                if icon_path:
                                    try:
                                        icon_arr = mpimg.imread(icon_path)
                                        marker_img = OffsetImage(icon_arr, zoom=0.50)
                                        marker_ab = AnnotationBbox(
                                            marker_img,
                                            (x_center, y),
                                            frameon=False,
                                            pad=0.0,
                                            box_alignment=(0.5, 0.5),
                                        )
                                        ax.add_artist(marker_ab)
                                    except Exception:
                                        pass

                            code_label = marker_cat if marker_cat else "*"
                            label_x = min(24 * 60 - 5, x_center + 12)
                            txt = ax.text(
                                label_x,
                                y,
                                code_label,
                                ha="left",
                                va="center",
                                fontsize=max(marker_fontsize - 1, 9),
                                color="white",
                            )
                            if text_effects:
                                txt.set_path_effects(text_effects)

                        y_cursor += lane_count + day_gap

                    ax.set_yticks(ytick_positions)
                    ax.set_yticklabels(ytick_labels)
                    if y_cursor > 0:
                        ax.set_ylim(-0.8, y_cursor - 0.2)
                    ax.set_xlim(x_start_global, x_end_global)
                    ax.set_xticks(ticks_global)
                    ax.set_xticklabels(tick_labels_global)
                    if not has_bars:
                        ax.text(
                            0.5,
                            0.5,
                            "No sessions in this duration bucket",
                            ha="center",
                            va="center",
                            color="black",
                            transform=ax.transAxes,
                        )

                category_name = (
                    ", ".join(format_category_label(c) for c in selected_categories)
                    if selected_categories
                    else "All"
                )
                fig.suptitle(f"Daily Rhythm: {category_name} ({range_name})")
                _render_axis(ax_micro, "Graph #1: Sessions <= 1 minute", "#0ea5e9", lambda d: d <= 1.0)
                _render_axis(ax_short, "Graph #2: Sessions > 1 and < 5 minutes", "#2d7ff9", lambda d: d > 1.0 and d < 5.0)
                _render_axis(ax_long, "Graph #3: Sessions >= 5 minutes", "#f28c28", lambda d: d >= 5.0)
                ax_long.set_xlabel("Time of day")
                fig.tight_layout(rect=[0, 0, 1, 0.95])
                canvas.draw()

            def _on_range_changed(_combo):
                zoom_hours["value"] = 24
                update_chart()

            range_combo.connect("changed", _on_range_changed)
            rhythm_category_checks["All"].connect("toggled", on_all_toggled)
            for cat in self.data_categories:
                rhythm_category_checks[cat].connect("toggled", on_category_toggled)
            update_chart()

            popup.connect("delete-event", lambda *args: setattr(self, "_rhythm_popup", None) or False)
            popup.show_all()
            popup.present()
            self._rhythm_popup = popup
        except Exception:
            self._show_error_dialog("Rhythm failed", traceback.format_exc())

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
