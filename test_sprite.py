#!/usr/bin/env python3
"""
Test script for the Tea Timer application's sprite functionality.

This script is designed to test the sprite animation features of the Tea Timer.
It automatically:
1. Launches the Tea Timer application
2. Sets a 5-second timer (displayed as 0.083 minutes)
3. Starts the timer automatically
4. Displays any sprite animations associated with the timer

Difference from test_short_timer.py: This specifically tests the sprite 
animation features of the application, while test_short_timer.py is a 
general functionality test with automatic closing.

Author: Lingma from Alibaba Cloud
Co-author: genidma on Github
Date of creation: October 2025
"""

import sys
import os
from pathlib import Path

# Add the bin directory to the path so we can import the TeaTimerApp
sys.path.insert(0, str(Path(__file__).parent / "bin"))

from teatime import TeaTimerApp
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class TestSpriteApp:
    def __init__(self):
        self.app = TeaTimerApp()
        
    def run_test(self):
        # Connect to the activate signal to set up our test
        def on_activate(application):
            # UI elements are now created, set a 5-second timer for testing
            self.app.duration_spin.set_value(5/60)  # 5 seconds in minutes
            self.app.on_start_clicked()
            
            # Start the GTK main loop
            Gtk.main()
        
        self.app.connect('activate', on_activate)
        self.app.run(sys.argv)

if __name__ == "__main__":
    test_app = TestSpriteApp()
    test_app.run_test()