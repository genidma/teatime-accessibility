#!/usr/bin/python3

import time
import math
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

from .core import (
    APP_NAME,
    APP_VERSION,
    CONFIG_FILE,
    STATS_LOG_FILE,
    DEFAULT_FONT_SCALE,
    FONT_SCALE_INCREMENT,
    MIN_FONT_SCALE,
    MAX_FONT_SCALE,
    KC_CATEGORIES,
    ConfigManager,
    StatsManager,
)
from .stats import StatisticsWindow

class FlipLabel(Gtk.Box):
    def __init__(self, text=""):
        super().__init__()
        self._effects_enabled = False
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)
        self._stack.set_transition_duration(200)

        self._label_a = Gtk.Label()
        self._label_b = Gtk.Label()
        self._label_a.set_use_markup(True)
        self._label_b.set_use_markup(True)
        self._label_a.get_style_context().add_class("time-display")
        self._label_b.get_style_context().add_class("time-display")

        self._stack.add_named(self._label_a, "a")
        self._stack.add_named(self._label_b, "b")
        self._current = "a"
        self._stack.set_visible_child_name("a")

        self.pack_start(self._stack, True, True, 0)
        if text:
            self.set_text(text)

    def set_effects_enabled(self, enabled: bool):
        self._effects_enabled = bool(enabled)
        self._stack.set_transition_duration(200 if self._effects_enabled else 0)

    def _set_label_value(self, label, value, markup: bool):
        if markup:
            label.set_markup(value)
        else:
            label.set_text(value)

    def _set_value(self, value, markup: bool):
        if not self._effects_enabled:
            self._set_label_value(self._label_a, value, markup)
            self._set_label_value(self._label_b, value, markup)
            self._stack.set_visible_child_name("a")
            self._current = "a"
            return

        next_name = "b" if self._current == "a" else "a"
        next_label = self._label_b if next_name == "b" else self._label_a
        self._set_label_value(next_label, value, markup)
        self._stack.set_visible_child_name(next_name)
        self._current = next_name

    def set_markup(self, markup: str):
        self._set_value(markup, True)

    def set_text(self, text: str):
        self._set_value(text, False)

    def get_text(self):
        active = self._label_a if self._current == "a" else self._label_b
        return active.get_text()

    def get_label(self):
        active = self._label_a if self._current == "a" else self._label_b
        return active.get_label()

    def get_label_widget(self):
        return self._label_a if self._current == "a" else self._label_b

class TargetCheckButton(Gtk.CheckButton):
    def __init__(self, label, pulse_ms=500):
        super().__init__(label=label)
        self._pulse_ms = pulse_ms
        self._pulse_progress = 0.0
        self._pulse_id = None
        self.connect("toggled", self._on_toggled)

    def _on_toggled(self, btn):
        if btn.get_active():
            self._start_pulse()

    def _start_pulse(self):
        if self._pulse_id:
            GLib.source_remove(self._pulse_id)
            self._pulse_id = None
        self._pulse_progress = 0.0
        steps = max(1, int(self._pulse_ms / 16))
        step = 1.0 / steps

        def tick():
            self._pulse_progress += step
            if self._pulse_progress >= 1.0:
                self._pulse_progress = 0.0
                self.queue_draw()
                self._pulse_id = None
                return False
            self.queue_draw()
            return True

        self._pulse_id = GLib.timeout_add(16, tick)

    def do_draw(self, cr):
        res = Gtk.CheckButton.do_draw(self, cr)
        if self._pulse_progress <= 0.0:
            return res

        alloc = self.get_allocation()
        w, h = alloc.width, alloc.height
        if w <= 0 or h <= 0:
            return res

        r = min(w, h) * 0.45
        cx, cy = w / 2, h / 2
        t = self._pulse_progress
        alpha = max(0.0, 0.9 - t)

        cr.set_source_rgba(1.0, 0.23, 0.19, alpha)
        cr.set_line_width(2.0)
        cr.arc(cx, cy, r * (0.85 + 0.15 * t), 0, 2 * math.pi)
        cr.stroke()
        cr.arc(cx, cy, r * 0.45, 0, 2 * math.pi)
        cr.stroke()
        return res


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
        self._sprite_frames_cache = {}
        self._sprite_scaled_cache = {}
        self._last_sprite_anim = None
        self.current_sprite_frame = 0
        self.sprite_timer_id = None
        self.auto_start = auto_start
        self.mini_mode = False
        self.nano_mode = False
        self.pre_timer_mode = None
        self.selected_categories = [] 
        self.preferred_skin = "default"
        self.preferred_animation = "test_animation"
        self.wall_clock_mode = False
        self.text_transition_effects = False
        self.rainbow_hue = 0
        self.rainbow_timer_id = None
        self._rainbow_deferred = False
        self._last_css = None
        
        self._load_config()
        self._setup_actions()
            
    def _setup_actions(self):
        actions = [
            ("start", self.on_start_clicked, ["<Control>s"]),
            ("stop", self.on_stop_clicked, ["<Control>t"]),
            ("toggle-timer", self._on_toggle_timer, ["space"]),
            ("statistics", self.on_stats_activated, ["<Control>i"]),
            ("settings", self.on_settings_activated, ["<Control>comma"]),
            ("increase-font", self.on_increase_font_clicked, ["<Control>plus", "<Control>equal"]),
            ("decrease-font", self.on_decrease_font_clicked, ["<Control>minus"]),
            ("toggle-sound", self.on_toggle_sound_activated, ["<Control>m"]),
            ("toggle-mini-mode", self.on_toggle_mini_mode_activated, ["<Control>d"]),
            ("toggle-nano-mode", self.on_toggle_nano_mode_activated, ["<Control>n"]),
            ("quit", lambda a, p: self.quit(), ["<Control>q"])
        ]
        for name, callback, accels in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            self.set_accels_for_action(f"app.{name}", accels)
            
    def _on_toggle_timer(self, *args):
        if self.timer_id:
            self.on_stop_clicked()
        else:
            self.on_start_clicked()

    def do_activate(self):
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self, title=APP_NAME)
            self.window.set_default_size(400, 300)
            self.window.connect("destroy", self._on_window_destroy)
            self.window.connect("set-focus-child", self._on_focus_changed)
            self.window.connect("focus-in-event", self._on_window_focus_in)
            self.window.connect("focus-out-event", self._on_window_focus_out)

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

            self.time_label = FlipLabel("00:00")
            self.time_label.set_effects_enabled(self.text_transition_effects)
            self.main_box.pack_start(self.time_label, False, False, 0)

            self.control_grid = Gtk.Grid(column_spacing=10, row_spacing=10, halign=Gtk.Align.CENTER)
            content_box.pack_start(self.control_grid, True, True, 0)

            # Row 0: Duration (spin + slider)
            self.control_grid.attach(Gtk.Label(label="Minutes:"), 0, 0, 1, 1)
            self.duration_spin = Gtk.SpinButton.new_with_range(1, 120, 1)
            self.duration_spin.set_value(self.last_duration)
            self.control_grid.attach(self.duration_spin, 1, 0, 1, 1)

            self.duration_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 120, 1)
            self.duration_scale.set_value(self.last_duration)
            self.duration_scale.set_digits(0)
            self.duration_scale.set_hexpand(True)
            self.duration_scale.set_draw_value(False)
            self.control_grid.attach(self.duration_scale, 0, 1, 2, 1)

            def on_spin_changed(spin):
                val = spin.get_value()
                if abs(self.duration_scale.get_value() - val) > 0.5:
                    self.duration_scale.set_value(val)

            def on_scale_changed(scale):
                val = int(scale.get_value())
                if int(self.duration_spin.get_value()) != val:
                    self.duration_spin.set_value(val)

            self.duration_spin.connect("value-changed", on_spin_changed)
            self.duration_scale.connect("value-changed", on_scale_changed)

            # Row 2: CATEGORY GRID (REDESIGN)
            cat_frame = Gtk.Frame(label="Categories")
            cat_grid = Gtk.Grid(column_spacing=10, row_spacing=5, margin=10)
            self.category_checkboxes = {}
            for i, cat in enumerate(KC_CATEGORIES):
                if cat.strip() == "":
                    continue
                cb = TargetCheckButton(label=cat, pulse_ms=500)
                cat_grid.attach(cb, i % 4, i // 4, 1, 1)
                self.category_checkboxes[cat] = cb
            cat_frame.add(cat_grid)
            self.category_ui = cat_frame
            self.control_grid.attach(cat_frame, 0, 2, 2, 1)

            # Row 3: Controls
            self.start_button = Gtk.Button(label="_Start", use_underline=True)
            self.start_button.connect("clicked", self.on_start_clicked)
            self.stop_button = Gtk.Button(label="_Stop", use_underline=True, sensitive=False)
            self.stop_button.connect("clicked", self.on_stop_clicked)
            self.control_grid.attach(self.start_button, 0, 3, 1, 1)
            self.control_grid.attach(self.stop_button, 1, 3, 1, 1)

            # Row 4: Font
            btn_minus = Gtk.Button(label="A-")
            btn_minus.connect("clicked", self.on_decrease_font_clicked)
            btn_plus = Gtk.Button(label="A+")
            btn_plus.connect("clicked", self.on_increase_font_clicked)
            self.control_grid.attach(btn_minus, 0, 4, 1, 1)
            self.control_grid.attach(btn_plus, 1, 4, 1, 1)

            # Row 5: Sound Toggle
            self.sound_toggle = Gtk.CheckButton(label="_Enable Sound", use_underline=True, active=self.sound_enabled)
            self.sound_toggle.connect("toggled", self.on_sound_toggled)
            self.control_grid.attach(self.sound_toggle, 0, 5, 2, 1)

            # Row 6: Mini Mode Toggle (FIXED OVERLAP)
            self.mini_mode_toggle = Gtk.CheckButton(label="_Mini Mode", use_underline=True, active=self.mini_mode)
            self.mini_mode_toggle.connect("toggled", self.on_mini_mode_toggled)
            self.control_grid.attach(self.mini_mode_toggle, 0, 6, 2, 1)

            # Row 7: Nano Mode Toggle
            self.nano_mode_toggle = Gtk.CheckButton(label="_Nano Mode (auto)", use_underline=True, active=self.nano_mode)
            self.nano_mode_toggle.connect("toggled", self.on_nano_mode_toggled)
            self.control_grid.attach(self.nano_mode_toggle, 0, 7, 2, 1)

            # Presets
            self.presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, halign=Gtk.Align.CENTER)
            content_box.pack_start(self.presets_box, False, False, 0)
            self.presets_box.add(Gtk.Label(label="<b>Presets</b>", use_markup=True))
            self.presets_box.add(Gtk.Label(label="<b>Presets</b>", use_markup=True))
            
            # Presets with mnemonics
            presets = [
                (15, "15m"), 
                (30, "30m"), 
                (45, "_45m"), 
                (60, "_1 Hour")
            ]
            for mins, label in presets:
                btn = Gtk.Button(label=label, use_underline=True)
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
        if self.timer_id: return
        
        if self.nano_mode:
            self.pre_timer_mode = 'mini' if self.mini_mode else 'normal'
            self._activate_nano_mode()
        elif self.wall_clock_mode:
            self._activate_wall_clock_mode()
        
        self._stop_rainbow_timer()
        duration = int(self.duration_spin.get_value())
        self.time_left = duration * 60
        self.current_timer_duration = duration
        self._update_label()
        
        # Update every 5 seconds
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
        win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        win.set_decorated(False)
        win.set_keep_above(True)
        win.set_skip_taskbar_hint(True)
        win.set_skip_pager_hint(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, valign=Gtk.Align.CENTER)
        win.add(box)
        
        label = FlipLabel()
        label.set_effects_enabled(self.text_transition_effects)
        label.set_markup("<span font_desc='Sans Bold 60' foreground='white'>Session Complete</span>")
        box.pack_start(label, False, False, 0)
        
        # Sprite Animation
        frames = self._load_sprite_frames()
        if frames:
            da = Gtk.DrawingArea(); da.set_size_request(400, 400)
            da.connect("draw", self._on_sprite_draw, frames)
            box.pack_start(da, False, False, 0)
            
            # Store reference to animation timeout to cancel it later
            animation_timeout_id = GLib.timeout_add(300, lambda: (da.queue_draw(), True)[1])
            
            # Clean up animation when window is destroyed
            def cleanup_animation(*args):
                if animation_timeout_id:
                    GLib.source_remove(animation_timeout_id)
                    
            win.connect("destroy", cleanup_animation)

        win.get_style_context().add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        win.connect("button-press-event", lambda w, e: win.destroy())
        GLib.timeout_add_seconds(10, win.destroy)
        win.show_all()
        win.fullscreen()
        win.present()

    def _load_sprite_frames(self):
        anim = getattr(self, 'preferred_animation', 'test_animation')
        if anim in self._sprite_frames_cache:
            self._last_sprite_anim = anim
            return self._sprite_frames_cache[anim]

        frames = []
        path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / anim
        if not path.exists():
            path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "test_animation"
            
        if path.exists():
            print(f"DEBUG: Animation path found: {path}")
            files = sorted(list(path.glob("*.png")))
            print(f"DEBUG: Found {len(files)} PNG frames")
            for f in files:
                try: 
                    pix = GdkPixbuf.Pixbuf.new_from_file(str(f))
                    if pix: frames.append(pix)
                except Exception as e:
                    print(f"Error loading frame {f}: {e}")
        else:
            print(f"DEBUG: Animation path NOT found: {path}")
        self._sprite_frames_cache[anim] = frames
        self._last_sprite_anim = anim
        return frames
    def _on_sprite_draw(self, widget, cr, frames):
        if not frames: return False
        alloc = widget.get_allocation()
        anim = self._last_sprite_anim or "unknown"
        size_key = (alloc.width, alloc.height)
        cache = self._sprite_scaled_cache.setdefault(anim, {})

        scaled_frames = cache.get(size_key)
        if scaled_frames is None:
            scaled_frames = []
            for pix in frames:
                pw, ph = pix.get_width(), pix.get_height()
                scale = min(alloc.width / pw, alloc.height / ph)
                sw, sh = max(1, int(pw * scale)), max(1, int(ph * scale))
                scaled_frames.append(pix.scale_simple(sw, sh, GdkPixbuf.InterpType.BILINEAR))
            cache[size_key] = scaled_frames

        cur = (int(time.time() * 10)) % len(scaled_frames)
        scaled = scaled_frames[cur]

        sw, sh = scaled.get_width(), scaled.get_height()
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
            for cat in KC_CATEGORIES:
                if cat.strip(): entry[cat] = 0
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
        self._apply_font_size()
        self._apply_skin() # Re-apply to ensure no background
        GLib.idle_add(self._resize_nano_window_to_label)

    def _resize_nano_window_to_label(self):
        if not self.window or not hasattr(self, 'time_label'):
            return False

        text = self.time_label.get_text() or self.time_label.get_label() or "00:00"
        label_widget = self.time_label.get_label_widget() if hasattr(self.time_label, "get_label_widget") else self.time_label
        layout = label_widget.create_pango_layout(text)
        context = label_widget.get_style_context()
        font_desc = context.get_font(Gtk.StateFlags.NORMAL)
        if font_desc:
            layout.set_font_description(font_desc)
        width, height = layout.get_pixel_size()

        target_w = max(120, width + 40)
        target_h = max(60, height + 30)
        self.window.set_default_size(target_w, target_h)
        self.window.resize(target_w, target_h)
        return False

    def _activate_wall_clock_mode(self):
        self.content_box.set_visible(False)
        self.time_label.set_margin_start(170)
        self.time_label.set_margin_end(170)
        self.time_label.set_margin_top(132)
        self.time_label.set_margin_bottom(132)

    def _restore_pre_timer_mode(self):
        self.window.set_decorated(True)
        self.content_box.set_visible(True)
        self.category_ui.set_visible(True)
        self.time_label.set_margin_start(0)
        self.time_label.set_margin_end(0)
        self.time_label.set_margin_top(0)
        self.time_label.set_margin_bottom(0)
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
        time_scale = scale * 2
        if self.nano_mode:
            time_scale *= 0.8
        self.font_css = f".time-display {{ font-size: {time_scale}%; }} label, button {{ font-size: {scale}%; }}"
        
        # Combine font CSS with skin CSS if applicable
        combined_css = self.font_css
        if not self.nano_mode and self.preferred_skin == 'lava':  # Only add skin CSS if in lava mode
            h1 = self.rainbow_hue
            h2 = (self.rainbow_hue + 120) % 360
            h3 = (self.rainbow_hue + 240) % 360
            r1, g1, b1 = colorsys.hsv_to_rgb(h1 / 360.0, 0.8, 0.7)
            r2, g2, b2 = colorsys.hsv_to_rgb(h2 / 360.0, 0.8, 0.7)
            r3, g3, b3 = colorsys.hsv_to_rgb(h3 / 360.0, 0.8, 0.7)
            c1 = f"rgb({int(r1*255)}, {int(g1*255)}, {int(b1*255)})"
            c2 = f"rgb({int(r2*255)}, {int(g2*255)}, {int(b2*255)})"
            c3 = f"rgb({int(r3*255)}, {int(g3*255)}, {int(b3*255)})"
            
            skin_css = f"""
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
            combined_css = skin_css + self.font_css  # Combine both CSS styles
        # If not in lava mode, just use font CSS only
        
        if combined_css == self._last_css:
            if self.nano_mode:
                GLib.idle_add(self._resize_nano_window_to_label)
            return
        self.css_provider.load_from_data(combined_css.encode())
        self._last_css = combined_css
        if self.nano_mode:
            GLib.idle_add(self._resize_nano_window_to_label)

    def _apply_skin(self):
        # Just trigger a re-render which will pick up the correct CSS
        # The actual CSS is now managed in _apply_font_size
        self._apply_font_size()

    def _start_rainbow_timer(self):
        if self.rainbow_timer_id: GLib.source_remove(self.rainbow_timer_id)
        if self.window and not self.window.is_active():
            self._rainbow_deferred = True
            return
        self.rainbow_timer_id = GLib.timeout_add(2000, self._update_rainbow)

    def _stop_rainbow_timer(self):
        if self.rainbow_timer_id:
            GLib.source_remove(self.rainbow_timer_id)
            self.rainbow_timer_id = None

    def _update_rainbow(self):
        if self.window and not self.window.is_active():
            self._stop_rainbow_timer()
            self._rainbow_deferred = True
            return False
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
            "wall_clock_mode": self.wall_clock_mode,
            "preferred_skin": self.preferred_skin,
            "preferred_animation": self.preferred_animation,
            "text_transition_effects": self.text_transition_effects
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
                    self.wall_clock_mode = c.get("wall_clock_mode", False)
                    self.preferred_skin = c.get("preferred_skin", "default")
                    self.preferred_animation = c.get("preferred_animation", "test_animation")
                    self.text_transition_effects = c.get("text_transition_effects", False)
            except: pass

    def on_preset_clicked(self, btn, mins):
        self.stop_timer()
        self.duration_spin.set_value(mins)
        # We need to manually call this because 'self.timer_id' was just cleared
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
        sprites_path = Path(__file__).resolve().parents[2] / "assets" / "sprites"
        if sprites_path.exists():
            for d in sprites_path.iterdir():
                if d.is_dir(): anim_combo.append(d.name, d.name.replace("_", " ").title())
        anim_combo.set_active_id(self.preferred_animation)
        grid.attach(anim_combo, 1, 1, 1, 1)
        
        # Wall Clock Mode
        wc_check = Gtk.CheckButton(label="Wall Clock Mode (active only during timer)")
        wc_check.set_active(self.wall_clock_mode)
        grid.attach(wc_check, 0, 2, 2, 1)

        # Text Transition Effects
        text_fx_check = Gtk.CheckButton(label="Text transition effects")
        text_fx_check.set_active(self.text_transition_effects)
        grid.attach(text_fx_check, 0, 3, 2, 1)
        
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            self.preferred_skin = skin_combo.get_active_id()
            self.preferred_animation = anim_combo.get_active_id()
            self.wall_clock_mode = wc_check.get_active()
            self.text_transition_effects = text_fx_check.get_active()
            if hasattr(self, "time_label") and hasattr(self.time_label, "set_effects_enabled"):
                self.time_label.set_effects_enabled(self.text_transition_effects)
            self._save_config()
            self._apply_skin()
        dialog.destroy()

    def on_toggle_sound_activated(self, *args):
        self.sound_toggle.set_active(not self.sound_toggle.get_active())

    def on_toggle_mini_mode_activated(self, *args):
        self.mini_mode_toggle.set_active(not self.mini_mode_toggle.get_active())

    def on_toggle_nano_mode_activated(self, *args):
        self.nano_mode_toggle.set_active(not self.nano_mode_toggle.get_active())

    def _on_focus_changed(self, *args):
        pass

    def _on_window_focus_in(self, *args):
        if self._rainbow_deferred and not self.rainbow_timer_id:
            self._rainbow_deferred = False
            self._start_rainbow_timer()
        return False

    def _on_window_focus_out(self, *args):
        self._stop_rainbow_timer()
        self._rainbow_deferred = True
        return False


def main(argv=None):
    if argv is None:
        argv = sys.argv
    app = TeaTimerApp()
    return app.run(argv)

if __name__ == "__main__":
    raise SystemExit(main())
