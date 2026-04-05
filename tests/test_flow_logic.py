import unittest
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

# Allow importing the local package from bin/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# Mock GTK imports used by teatime modules
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()

from teatime.stats import _clip_interval_to_day, _flow_label_x, _parse_iso_ts


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


if __name__ == "__main__":
    unittest.main()
