import unittest
import os
import sys
from datetime import datetime, date
from unittest.mock import MagicMock

# Allow importing the local package from bin/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# Mock GTK imports used by teatime modules
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()

from teatime.stats import (
    _clip_interval_to_day,
    _flow_available_months,
    _flow_available_weeks,
    _flow_available_years,
    _flow_canvas_geometry,
    _flow_filter_points,
    _flow_label_x,
    _flow_scope_label,
    _parse_iso_ts,
)


class TestFlowLogic(unittest.TestCase):
    def test_parse_iso_valid(self):
        ts = _parse_iso_ts("2026-02-15T10:30:00")
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2026)

    def test_parse_iso_invalid(self):
        self.assertIsNone(_parse_iso_ts("not-a-timestamp"))

    def test_clip_inside_day(self):
        day_start = datetime(2026, 2, 15, 0, 0, 0)
        day_end = datetime(2026, 2, 15, 23, 59, 59)
        start = datetime(2026, 2, 15, 9, 0, 0)
        end = datetime(2026, 2, 15, 9, 25, 0)

        clipped = _clip_interval_to_day(start, end, day_start, day_end)
        self.assertEqual(clipped, (start, end))

    def test_clip_across_midnight_into_day(self):
        day_start = datetime(2026, 2, 15, 0, 0, 0)
        day_end = datetime(2026, 2, 15, 23, 59, 59)
        start = datetime(2026, 2, 14, 23, 50, 0)
        end = datetime(2026, 2, 15, 0, 10, 0)

        clipped = _clip_interval_to_day(start, end, day_start, day_end)
        self.assertEqual(clipped, (day_start, end))

    def test_clip_no_overlap(self):
        day_start = datetime(2026, 2, 15, 0, 0, 0)
        day_end = datetime(2026, 2, 15, 23, 59, 59)
        start = datetime(2026, 2, 14, 22, 0, 0)
        end = datetime(2026, 2, 14, 23, 0, 0)

        self.assertIsNone(_clip_interval_to_day(start, end, day_start, day_end))

    def test_flow_label_x_prefers_right_side_when_it_fits(self):
        x = _flow_label_x(point_x=120, label_width=30, canvas_width=560, pad=24, gap=6)
        self.assertEqual(x, 126.0)

    def test_flow_label_x_flips_left_near_right_edge(self):
        x = _flow_label_x(point_x=536, label_width=40, canvas_width=560, pad=24, gap=6)
        self.assertEqual(x, 490.0)

    def test_flow_available_calendar_filters(self):
        points = [
            ("2024-12-31", 10),
            ("2025-03-05", 20),
            ("2026-03-06", 30),
            ("2026-04-14", 40),
        ]

        self.assertEqual(_flow_available_years(points), [2024, 2025, 2026])
        self.assertEqual(_flow_available_months(points), [3, 4, 12])
        self.assertEqual(_flow_available_months(points, 2026), [3, 4])

        weeks_2026_march = _flow_available_weeks(points, 2026, 3)
        self.assertEqual(weeks_2026_march, [date(2026, 3, 2)])

    def test_flow_filter_points_combines_range_and_calendar_filters(self):
        points = [
            ("2025-03-10", 10),
            ("2026-02-25", 20),
            ("2026-03-06", 30),
            ("2026-03-25", 35),
            ("2026-04-14", 40),
        ]
        now = datetime(2026, 4, 20, 12, 0, 0)

        self.assertEqual(
            _flow_filter_points(points, now, range_days=30),
            [("2026-03-25", 35), ("2026-04-14", 40)],
        )
        self.assertEqual(
            _flow_filter_points(points, now, range_days=30, selected_year=2025),
            [],
        )
        self.assertEqual(
            _flow_filter_points(points, now, range_days=30, selected_year=2026),
            [("2026-03-25", 35), ("2026-04-14", 40)],
        )
        self.assertEqual(
            _flow_filter_points(points, now, range_days=30, selected_year=2026, selected_month=3),
            [("2026-03-25", 35)],
        )
        self.assertEqual(
            _flow_filter_points(points, now, range_days=30, selected_week_start="2026-04-13"),
            [("2026-04-14", 40)],
        )
        self.assertEqual(
            _flow_filter_points(points, now, range_days=-1, selected_year=2025),
            [("2025-03-10", 10)],
        )

    def test_flow_scope_label_formats_calendar_scope(self):
        self.assertEqual(_flow_scope_label("30d"), "30d")
        self.assertEqual(_flow_scope_label("All"), "All Time")
        self.assertEqual(_flow_scope_label("30d", selected_year=2026), "30d + 2026")
        self.assertEqual(
            _flow_scope_label("30d", selected_year=2026, selected_month=3),
            "30d + Mar 2026",
        )
        self.assertEqual(
            _flow_scope_label("30d", selected_week_start="2026-03-02"),
            "30d + Week of 2026-03-02",
        )

    def test_flow_canvas_geometry_switches_between_fit_and_scroll(self):
        fit_geometry = _flow_canvas_geometry(True, 90, viewport_width=900, viewport_height=240)
        self.assertEqual(fit_geometry, {"width_px": 900, "height_px": 240})

        scroll_geometry = _flow_canvas_geometry(False, 40, viewport_width=900, viewport_height=240)
        self.assertEqual(scroll_geometry, {"width_px": 1876, "height_px": 240})


if __name__ == "__main__":
    unittest.main()
