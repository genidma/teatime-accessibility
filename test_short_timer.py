#!/usr/bin/env python3
"""
Test script for the Tea Timer application with a short timer duration.

This script is designed for quick testing of the Tea Timer functionality
without waiting for a full-length timer. It automatically:
1. Launches the Tea Timer application
2. Sets a 10-second timer (displayed as 0.17 minutes)
3. Starts the timer automatically
4. Closes the application after 15 seconds total

Author: Lingma
Date: 2025
"""

import sys
import os
from pathlib import Path

# Add the bin directory to the path so we can import the TeaTimerApp
sys.path.insert(0, str(Path(__file__).parent / "bin"))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

# Import the application
from teatime import TeaTimerApp

def main():
    # Create the application
    app = TeaTimerApp()
    
    # Connect to the activate signal to set up our test
    def on_activate(app):
        # Set a very short timer (10 seconds)
        app.duration_spin.set_value(10/60)  # 10 seconds in minutes
        # Start the timer
        app.on_start_clicked()
        
        # Close the app after 15 seconds
        GLib.timeout_add_seconds(15, Gtk.main_quit)
    
    app.connect('activate', on_activate)
    
    # Run the application
    app.run(sys.argv)
    
    return 0

if __name__ == "__main__":
    main()