#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bin'))

# Import the main application class
from teatime import TeaTimerApp
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class TestApp(TeaTimerApp):
    def __init__(self):
        # Initialize without creating the full GUI
        self.current_timer_duration = 5  # 5 minutes
        
    def test_logging(self):
        print("Testing _log_timer_completion directly...")
        self._log_timer_completion()
        print("Test completed.")

if __name__ == "__main__":
    app = TestApp()
    app.test_logging()