import unittest
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add bin to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# Create a mock for gi.repository and define dummy classes for Gtk base classes
gi_repository = MagicMock()

class DummyApplication:
    def __init__(self, *args, **kwargs):
        pass
    def add_action(self, *args):
        pass
    def set_accels_for_action(self, *args):
        pass

class DummyWindow:
    def __init__(self, *args, **kwargs):
        pass
    def connect(self, *args):
        pass
    def show_all(self, *args):
        pass

gi_repository.Gtk.Application = DummyApplication
gi_repository.Gtk.Window = DummyWindow

# Set in sys.modules before any imports of teatime
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = gi_repository

import teatime

class TestCompatibility(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests")
        self.tmp_config = self.test_dir / "tmp_config.json"
        self.tmp_stats = self.test_dir / "tmp_stats.json"
        for p in [self.tmp_config, self.tmp_stats]:
            if p.exists(): p.unlink()

        # Save original files paths to restore
        import teatime.app
        import teatime.stats
        self.orig_app_config = teatime.app.CONFIG_FILE
        self.orig_stats_file = teatime.stats.STATS_LOG_FILE
        
        teatime.app.CONFIG_FILE = self.tmp_config
        teatime.stats.STATS_LOG_FILE = self.tmp_stats

    def tearDown(self):
        for p in [self.tmp_config, self.tmp_stats]:
            if p.exists(): p.unlink()
            
        import teatime.app
        import teatime.stats
        teatime.app.CONFIG_FILE = self.orig_app_config
        teatime.stats.STATS_LOG_FILE = self.orig_stats_file

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

    def test_app_load_config_missing_and_null_fields(self):
        """Verify app._load_config handles null/missing fields gracefully."""
        bad_config = {
            "font_scale_factor": None,
            "last_duration": None,
            "preferred_animation": None,
            "preferred_skin": None,
            "mini_mode": None,
            "nano_mode": None
        }
        with open(self.tmp_config, 'w') as f:
            json.dump(bad_config, f)

        # Clear env variable if present to force reading last_duration from config
        with patch.dict(os.environ, {}, clear=True):
            app = teatime.app.TeaTimerApp()
            
            # Assert defaults are used instead of None values
            self.assertEqual(app.font_scale_factor, teatime.app.DEFAULT_FONT_SCALE)
            self.assertEqual(app.last_duration, 5)
            self.assertEqual(app.preferred_animation, "puppy_animation")
            self.assertEqual(app.preferred_skin, "default")
            self.assertEqual(app.mini_mode, False)
            self.assertEqual(app.nano_mode, False)

    def test_stats_window_load_stats_malformed_and_nulls(self):
        """Verify StatisticsWindow._load_stats handles malformed/null fields and missing categories gracefully."""
        bad_stats = [
            # Entry 1: Completely valid
            {"timestamp": "2025-01-01T10:00:00", "duration": 10, "category": "Work"},
            # Entry 2: Null/missing fields
            {"timestamp": None, "duration": None, "category": None},
            # Entry 3: Invalid types
            {"timestamp": "invalid_date", "duration": "not_an_int", "category": 123},
            # Entry 4: Missing fields altogether
            {"other_field": "val"}
        ]
        with open(self.tmp_stats, 'w') as f:
            json.dump(bad_stats, f)

        # Instantiate stats window (calls _load_stats in constructor)
        app_mock = MagicMock()
        parent_mock = MagicMock()
        window = teatime.stats.StatisticsWindow(app_mock, parent_mock)

        # Retrieve the appends made to the store
        append_calls = window.store.append.call_args_list
        # We expect 4 entries to be parsed (Entry 4 will be treated as an empty dict log, but still parsed)
        self.assertEqual(len(append_calls), 4)

        # Verify details of Entry 1 (valid)
        first_call_args = append_calls[0][0][0] # first call, first arg list
        self.assertEqual(first_call_args[0], "2025-01-01 10:00")
        self.assertEqual(first_call_args[1], 10)

        # Verify summary statistics labels were set correctly
        # Total sessions = 4
        # Total duration = 10 (since all invalid ones fallback to 0)
        window.total_sessions_label.set_text.assert_any_call("Total Sessions: 4")
        window.total_time_label.set_text.assert_any_call("Total Time: 10 minutes")

if __name__ == "__main__":
    unittest.main()