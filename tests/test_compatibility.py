import unittest
import json
import os
import sys
from pathlib import Path

# Add bin to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# Mock GI dependencies minimally to allow module import even though we don't use them for manager tests
from unittest.mock import MagicMock
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()

import teatime

class TestCompatibility(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests")
        self.tmp_config = self.test_dir / "tmp_config.json"
        self.tmp_stats = self.test_dir / "tmp_stats.json"
        for p in [self.tmp_config, self.tmp_stats]:
            if p.exists(): p.unlink()

    def tearDown(self):
        for p in [self.tmp_config, self.tmp_stats]:
            if p.exists(): p.unlink()

    def test_config_manager_benchmarks(self):
        """Verify ConfigManager handles basic saving/loading."""
        cm = teatime.ConfigManager(config_path=self.tmp_config)
        data = {"test": "val"}
        cm.save(data)
        
        loaded = cm.load()
        self.assertEqual(loaded["test"], "val")

    def test_config_manager_backward_compat(self):
        """Test loading a config file that is missing newer fields."""
        legacy_data = {
            "font_scale_factor": 1.5,
            "last_duration": 15
        }
        with open(self.tmp_config, 'w') as f:
            json.dump(legacy_data, f)
            
        cm = teatime.ConfigManager(config_path=self.tmp_config)
        config = cm.load()
        
        # Verify it loads what is there
        self.assertEqual(config["font_scale_factor"], 1.5)
        self.assertEqual(config["last_duration"], 15)
        # Verify it doesn't crash on missing fields (it just returns the dict)
        self.assertNotIn("preferred_skin", config)

    def test_config_manager_corrupted(self):
        with open(self.tmp_config, 'w') as f:
            f.write("{ invalid json")
        cm = teatime.ConfigManager(config_path=self.tmp_config)
        config = cm.load()
        self.assertEqual(config, {}) # Returns empty dict on error

    def test_stats_manager_logic(self):
        legacy_stats = [
            {"timestamp": "2025-01-01T10:00:00", "duration": 10},
            {"timestamp": "2025-01-01T11:00:00", "duration": 20}
        ]
        with open(self.tmp_stats, 'w') as f:
            json.dump(legacy_stats, f)
            
        sm = teatime.StatsManager(stats_path=self.tmp_stats)
        logs = sm.load()
        
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["duration"], 10)
        self.assertNotIn("category", logs[0])

if __name__ == "__main__":
    unittest.main()