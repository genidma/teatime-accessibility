import unittest
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add bin to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# Mock GI dependencies minimally to allow module import
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()
import teatime

class TestCompatibility(unittest.TestCase):
    def setUp(self):
        self.tmp_config = Path("tests/tmp_config.json")
        self.tmp_stats = Path("tests/tmp_stats.json")
        for p in [self.tmp_config, self.tmp_stats]:
            if p.exists(): p.unlink()

    def tearDown(self):
        for p in [self.tmp_config, self.tmp_stats]:
            if p.exists(): p.unlink()

    def test_load_legacy_config_logic(self):
        """Test the logic of _load_config using an unbound method."""
        legacy_data = {
            "font_scale_factor": 1.75,
            "last_duration": 12,
            "preferred_animation": "legacy_ani"
        }
        with open(self.tmp_config, 'w') as f:
            json.dump(legacy_data, f)
            
        # Create a mock object to act as 'self'
        mock_self = MagicMock()
        mock_self.window = None
        
        # Call the method from the class, passing our mock
        teatime.TeaTimerApp._load_config(mock_self, config_path=self.tmp_config)
        
        # Verify attributes were set on mock_self
        self.assertEqual(mock_self.font_scale_factor, 1.75)
        self.assertEqual(mock_self.last_duration, 12)
        self.assertEqual(mock_self.preferred_animation, "legacy_ani")
        self.assertEqual(mock_self.preferred_skin, "default") 
        self.assertFalse(mock_self.mini_mode)

    def test_load_corrupted_config_logic(self):
        with open(self.tmp_config, 'w') as f:
            f.write("{ invalid json")
            
        mock_self = MagicMock()
        teatime.TeaTimerApp._load_config(mock_self, config_path=self.tmp_config)
        
        # Should fall back to defaults
        self.assertEqual(mock_self.preferred_skin, "default")
        self.assertEqual(mock_self.preferred_animation, "puppy_animation")

    def test_load_legacy_stats_logic(self):
        legacy_stats = [
            {"timestamp": "2025-01-01T10:00:00", "duration": 10},
            {"timestamp": "2025-01-01T11:00:00", "duration": 20}
        ]
        with open(self.tmp_stats, 'w') as f:
            json.dump(legacy_stats, f)
            
        mock_self = MagicMock()
        mock_self.store = MagicMock()
        
        # Call StatisticsWindow method unbound
        teatime.StatisticsWindow._load_stats(mock_self, stats_path=self.tmp_stats)
        
        # Check if 2 entries were added to the store
        # and that the logic didn't crash because of missing 'category'
        self.assertEqual(mock_self.store.append.call_count, 2)
        
        # Verify first call args (it sorts reverse timestamp, so newest first)
        # 11:00 should be first, 10:00 second.
        # stats_win.store.append([friendly_date, duration])
        calls = mock_self.store.append.call_args_list
        self.assertEqual(calls[0][0][0][1], 20) # Newest duration
        self.assertEqual(calls[1][0][0][1], 10) # Oldest duration

if __name__ == "__main__":
    unittest.main()