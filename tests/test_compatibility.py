import unittest
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Add bin to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# 1. Define base classes that don't depend on GTK
class MockBase:
    def __init__(self, *args, **kwargs): pass
    def connect(self, *args, **kwargs): pass
    def add_action(self, *args, **kwargs): pass
    def set_accels_for_action(self, *args, **kwargs): pass
    def get_style_context(self, *args, **kwargs):
        m = MagicMock()
        m.add_provider.return_value = None
        return m

# 2. Mock GI modules
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()

import gi.repository
gi.repository.Gtk = MagicMock()
gi.repository.Gtk.Application = MockBase
gi.repository.Gtk.Window = MockBase
gi.repository.GObject = MagicMock()
gi.repository.Gio = MagicMock()
gi.repository.Gdk = MagicMock()

# 3. Now import teatime
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

    def test_load_legacy_config(self):
        legacy_data = {
            "font_scale_factor": 1.5,
            "last_duration": 15,
            "preferred_animation": "old_ani"
        }
        with open(self.tmp_config, 'w') as f:
            json.dump(legacy_data, f)
            
        # Instantiate TeaTimerApp
        # We need to mock a few things it uses in __init__
        with patch('gi.repository.Gtk.CssProvider', MagicMock()):
            app = teatime.TeaTimerApp()
            app.window = None  # Prevent saving
            
            # Use refactored _load_config
            app._load_config(config_path=self.tmp_config)
            
            self.assertEqual(app.font_scale_factor, 1.5)
            self.assertEqual(app.last_duration, 15)
            self.assertEqual(app.preferred_animation, "old_ani")
            self.assertEqual(app.preferred_skin, "default") # Verified backward compat

    def test_load_腐った_stats(self): # (corrupted)
        legacy_stats = [{"timestamp": "2025-01-01T10:00:00", "duration": 10}]
        with open(self.tmp_stats, 'w') as f:
            json.dump(legacy_stats, f)
            
        mock_app = MagicMock()
        mock_parent = MagicMock()
        
        # We need to mock ListStore and Labels
        with patch('gi.repository.Gtk.ListStore', MagicMock()), \
             patch('gi.repository.Gtk.Label', MagicMock()), \
             patch('gi.repository.Gtk.Box', MagicMock()), \
             patch('gi.repository.Gtk.Grid', MagicMock()), \
             patch('gi.repository.Gtk.ScrolledWindow', MagicMock()), \
             patch('gi.repository.Gtk.TreeView', MagicMock()):
                
            stats_win = teatime.StatisticsWindow(mock_app, mock_parent)
            stats_win.store = MagicMock()
            
            stats_win._load_stats(stats_path=self.tmp_stats)
            self.assertEqual(stats_win.store.append.call_count, 1)

if __name__ == "__main__":
    unittest.main()