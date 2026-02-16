import unittest
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()

from teatime.stats import _collect_rhythm_segments


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


if __name__ == "__main__":
    unittest.main()
