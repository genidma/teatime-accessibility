import unittest
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add bin to path so we can import teatime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

# Create specific mock classes that can be inherited from
class MockGtkApplication:
    def __init__(self, *args, **kwargs): pass
    def add_action(self, *args, **kwargs): pass
    def set_accels_for_action(self, *args, **kwargs): pass
    def add_main_option(self, *args, **kwargs): pass
    def connect(self, *args, **kwargs): pass
    def run(self, *args, **kwargs): pass

class MockGtkWindow:
    def __init__(self, *args, **kwargs): pass
    def set_default_size(self, *args, **kwargs): pass
    def set_modal(self, *args, **kwargs): pass
    def set_resizable(self, *args, **kwargs): pass
    def set_type_hint(self, *args, **kwargs): pass
    def set_decorated(self, *args, **kwargs): pass
    def set_role(self, *args, **kwargs): pass
    def connect(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): pass
    def show_all(self, *args, **kwargs): pass
    def hide(self, *args, **kwargs): pass

# Mock GI dependencies
mock_gtk = MagicMock()
mock_gtk.Application = MockGtkApplication
mock_gtk.Window = MockGtkWindow
mock_gtk.Box = MagicMock
mock_gtk.Grid = MagicMock
mock_gtk.Label = MagicMock
mock_gtk.ScrolledWindow = MagicMock
mock_gtk.Button = MagicMock
mock_gtk.TreeView = MagicMock
mock_gtk.ListStore = MagicMock
mock_gtk.Orientation = MagicMock()
mock_gtk.Align = MagicMock()
mock_gtk.PolicyType = MagicMock()
mock_gtk.MessageDialog = MagicMock()
mock_gtk.MessageType = MagicMock()
mock_gtk.ButtonsType = MagicMock()
mock_gtk.FileChooserDialog = MagicMock()
mock_gtk.FileChooserAction = MagicMock()
mock_gtk.ResponseType = MagicMock()
mock_gtk.CssProvider = MagicMock()
mock_gtk.STYLE_PROVIDER_PRIORITY_APPLICATION = 1

mock_glib = MagicMock()
mock_gio = MagicMock()
mock_gdk = MagicMock()

sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()
sys.modules['gi.repository.Gtk'] = mock_gtk
sys.modules['gi.repository.GLib'] = mock_glib
sys.modules['gi.repository.Gio'] = mock_gio
sys.modules['gi.repository.Gdk'] = mock_gdk

# Now import the actual classes from teatime
import teatime
from teatime import TeaTimerApp, StatisticsWindow

class TestCompatibility(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests")
        self.tmp_config = self.test_dir / "tmp_config.json"
        self.tmp_stats = self.test_dir / "tmp_stats.json"
        
        if self.tmp_config.exists():
            self.tmp_config.unlink()
        if self.tmp_stats.exists():
            self.tmp_stats.unlink()

    def tearDown(self):
        if self.tmp_config.exists():
            self.tmp_config.unlink()
        if self.tmp_stats.exists():
            self.tmp_stats.unlink()

    def test_load_legacy_config(self):
        """Test loading a config file that is missing newer fields."""
        legacy_data = {
            "font_scale_factor": 2.0,
            "last_duration": 10,
            "preferred_animation": "test_animation"
        }
        with open(self.tmp_config, 'w') as f:
            json.dump(legacy_data, f)
            
        # We need to mock some properties that TeaTimerApp expects to exist after __init__
        # to avoid crashes during _load_config or other calls
        app = TeaTimerApp()
        app.window = None # Ensure it doesn't try to save
        
        # Call the refactored method
        app._load_config(config_path=self.tmp_config)
        
        self.assertEqual(app.font_scale_factor, 2.0)
        self.assertEqual(app.last_duration, 10)
        self.assertEqual(app.preferred_animation, "test_animation")
        self.assertEqual(app.preferred_skin, "default")
        self.assertFalse(app.mini_mode)
        self.assertFalse(app.nano_mode)

    def test_load_corrupted_config(self):
        """Test handling of malformed JSON in config."""
        with open(self.tmp_config, 'w') as f:
            f.write("{ invalid json")
            
        app = TeaTimerApp()
        app._load_config(config_path=self.tmp_config)
        
        # Should reset to defaults
        self.assertEqual(app.preferred_skin, "default")
        self.assertEqual(app.preferred_animation, "puppy_animation")

    def test_load_legacy_stats(self):
        """Test loading stats file missing the category field."""
        legacy_stats_data = [
            {"timestamp": "2025-01-01T12:00:00", "duration": 25},
            {"timestamp": "2025-01-01T13:00:00", "duration": 5}
        ]
        with open(self.tmp_stats, 'w') as f:
            json.dump(legacy_stats_data, f)
            
        mock_app = MagicMock()
        mock_parent = MagicMock()
        
        # StatisticsWindow calls _load_stats in __init__
        # We need to make sure the TreeView store is usable
        stats_win = StatisticsWindow(mock_app, mock_parent)
        stats_win.store = MagicMock()
        
        stats_win._load_stats(stats_path=self.tmp_stats)
        
        # Verify 2 items were appended (legacy data handled)
        self.assertEqual(stats_win.store.append.call_count, 2)

if __name__ == '__main__':
    unittest.main()