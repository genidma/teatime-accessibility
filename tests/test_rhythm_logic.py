import unittest
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()

from teatime.stats import (
    _build_stats_fallback_rhythm_segments,
    _collect_rhythm_plot_data,
    _collect_rhythm_segments,
    _merge_missing_rhythm_days,
    _resolve_rhythm_window,
)


class TestRhythmLogic(unittest.TestCase):
    def test_collect_all_categories(self):
        events = [
            {
                "ts_start": "2026-02-16T09:00:00",
                "ts_end": "2026-02-16T09:30:00",
                "categories": ["breaks"],
            },
            {
                "ts_start": "2026-02-16T11:00:00",
                "ts_end": "2026-02-16T11:25:00",
                "categories": ["rdp"],
            },
        ]
        start_window = datetime(2026, 2, 16, 0, 0, 0)
        end_window = datetime(2026, 2, 16, 23, 59, 59)

        by_day = _collect_rhythm_segments(events, start_window, end_window, "All")

        self.assertIn("2026-02-16", by_day)
        self.assertEqual(len(by_day["2026-02-16"]), 2)

    def test_collect_filtered_category(self):
        events = [
            {
                "ts_start": "2026-02-16T09:00:00",
                "ts_end": "2026-02-16T09:30:00",
                "categories": ["breaks"],
            },
            {
                "ts_start": "2026-02-16T11:00:00",
                "ts_end": "2026-02-16T11:25:00",
                "categories": ["rdp"],
            },
        ]
        start_window = datetime(2026, 2, 16, 0, 0, 0)
        end_window = datetime(2026, 2, 16, 23, 59, 59)

        by_day = _collect_rhythm_segments(events, start_window, end_window, "breaks")

        self.assertIn("2026-02-16", by_day)
        self.assertEqual(len(by_day["2026-02-16"]), 1)

    def test_collect_category_string_single_value(self):
        events = [
            {
                "ts_start": "2026-02-16T09:00:00",
                "ts_end": "2026-02-16T09:30:00",
                "categories": "breaks",
            },
        ]
        start_window = datetime(2026, 2, 16, 0, 0, 0)
        end_window = datetime(2026, 2, 16, 23, 59, 59)

        by_day = _collect_rhythm_segments(events, start_window, end_window, "breaks")

        self.assertIn("2026-02-16", by_day)
        self.assertEqual(len(by_day["2026-02-16"]), 1)

    def test_collect_duration_min_fallback(self):
        events = [
            {
                "ts_start": "2026-02-16T10:00:00",
                "duration_min": 20,
                "categories": ["breaks"],
            },
        ]
        start_window = datetime(2026, 2, 16, 0, 0, 0)
        end_window = datetime(2026, 2, 16, 23, 59, 59)

        by_day = _collect_rhythm_segments(events, start_window, end_window, "breaks")

        self.assertIn("2026-02-16", by_day)
        self.assertAlmostEqual(by_day["2026-02-16"][0][0], 10 * 60)
        self.assertAlmostEqual(by_day["2026-02-16"][0][1], 10 * 60 + 20)

    def test_collect_clips_cross_midnight(self):
        events = [
            {
                "ts_start": "2026-02-15T23:50:00",
                "ts_end": "2026-02-16T00:10:00",
                "categories": ["breaks"],
            },
        ]
        start_window = datetime(2026, 2, 16, 0, 0, 0)
        end_window = datetime(2026, 2, 16, 23, 59, 59)

        by_day = _collect_rhythm_segments(events, start_window, end_window, "breaks")

        self.assertIn("2026-02-16", by_day)
        seg_start, seg_end = by_day["2026-02-16"][0]
        self.assertEqual(seg_start, 0)
        self.assertAlmostEqual(seg_end, 10, places=4)

    def test_collect_supports_legacy_start_end_keys(self):
        events = [
            {
                "start": "2026-02-16T09:00:00",
                "end": "2026-02-16T09:30:00",
                "categories": ["breaks"],
            },
        ]
        start_window = datetime(2026, 2, 16, 0, 0, 0)
        end_window = datetime(2026, 2, 16, 23, 59, 59)

        by_day = _collect_rhythm_segments(events, start_window, end_window, "breaks")

        self.assertIn("2026-02-16", by_day)
        self.assertEqual(len(by_day["2026-02-16"]), 1)
        self.assertAlmostEqual(by_day["2026-02-16"][0][0], 9 * 60)
        self.assertAlmostEqual(by_day["2026-02-16"][0][1], 9 * 60 + 30)

    def test_resolve_rhythm_window_for_all_supported_ranges(self):
        now = datetime(2026, 4, 4, 15, 30, 0)
        cases = [
            ("4h", 4, datetime(2026, 4, 4, 11, 30, 0), now, 4),
            ("12h", 12, datetime(2026, 4, 4, 3, 30, 0), now, 12),
            ("24h", 24, datetime(2026, 4, 3, 15, 30, 0), now, 24),
            ("3d", 72, datetime(2026, 4, 1, 15, 30, 0), now, 24),
            ("7d", 168, datetime(2026, 3, 28, 15, 30, 0), now, 24),
            ("30d", 720, datetime(2026, 3, 5, 15, 30, 0), now, 24),
            ("90d", 2160, datetime(2026, 1, 4, 15, 30, 0), now, 24),
            ("180d", 4320, datetime(2025, 10, 6, 15, 30, 0), now, 24),
        ]

        for label, span_hours, expected_start, expected_end, expected_hours in cases:
            with self.subTest(label=label):
                start_window, end_window, hours = _resolve_rhythm_window(now, span_hours)
                self.assertEqual(start_window, expected_start)
                self.assertEqual(end_window, expected_end)
                self.assertEqual(hours, expected_hours)

        start_window, end_window, hours = _resolve_rhythm_window(now, -1)
        self.assertEqual(start_window, datetime.min)
        self.assertEqual(end_window, datetime.max)
        self.assertEqual(hours, 24)

    def test_stats_fallback_includes_days_that_overlap_window(self):
        daily_minutes = [
            ("2026-01-05", 25),
            ("2026-01-06", 30),
            ("2026-01-07", 35),
        ]
        start_window = datetime(2026, 1, 5, 12, 0, 0)
        end_window = datetime(2026, 1, 6, 12, 0, 0)

        by_day = _build_stats_fallback_rhythm_segments(
            daily_minutes, start_window, end_window
        )

        self.assertEqual(sorted(by_day.keys()), ["2026-01-05", "2026-01-06"])

    def test_merge_missing_rhythm_days_preserves_event_days(self):
        primary = {"2026-04-03": [(540.0, 580.0)]}
        fallback = {
            "2026-01-10": [(720.0, 745.0)],
            "2026-04-03": [(720.0, 760.0)],
        }

        merged = _merge_missing_rhythm_days(primary, fallback)

        self.assertEqual(sorted(merged.keys()), ["2026-01-10", "2026-04-03"])
        self.assertEqual(merged["2026-04-03"], primary["2026-04-03"])
        self.assertEqual(merged["2026-01-10"], fallback["2026-01-10"])

    def test_collect_rhythm_plot_data_keeps_stats_only_history_days(self):
        events = [
            {
                "ts_start": "2026-04-03T09:00:00",
                "ts_end": "2026-04-03T09:40:00",
                "categories": ["breaks"],
            }
        ]
        daily_minutes = [
            ("2026-01-10", 25),
            ("2026-04-03", 40),
        ]
        start_window = datetime(2026, 1, 1, 0, 0, 0)
        end_window = datetime(2026, 4, 4, 23, 59, 59)

        by_day_detailed, by_day = _collect_rhythm_plot_data(
            events, daily_minutes, start_window, end_window, "All"
        )

        self.assertEqual(sorted(by_day_detailed.keys()), ["2026-04-03"])
        self.assertEqual(sorted(by_day.keys()), ["2026-01-10", "2026-04-03"])
        self.assertEqual(by_day["2026-04-03"], [(540.0, 580.0)])


if __name__ == "__main__":
    unittest.main()
