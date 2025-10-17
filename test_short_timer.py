#!/usr/bin/env python3
"""
Test script for the Tea Timer application with a short timer duration.

This script is designed for quick testing of the Tea Timer functionality
without waiting for a full-length timer. It automatically:
1. Launches the Tea Timer application
2. Sets a configurable timer duration (default 10 seconds)
3. Starts the timer automatically
4. Closes the application after the timer duration plus 5 seconds

Difference from test_sprite.py: This is a basic functionality test that 
runs a short timer and automatically closes, while test_sprite.py specifically 
tests the sprite animation features.

Author: Lingma from Alibaba Cloud
Co-author: genidma on Github
Date of creation: October 2025
"""

import sys
import os
import argparse
from pathlib import Path

# Parse command line arguments before GTK processes them
parser = argparse.ArgumentParser(description='Test Tea Timer with custom duration')
parser.add_argument('--duration', type=int, default=10, help='Timer duration in seconds (default: 10)')
parser.add_argument('--exit-delay', type=int, default=5, help='Delay in seconds before exiting after timer finishes (default: 5)')

# Parse known args to avoid conflicts with GTK arguments
args, unknown = parser.parse_known_args()

# Reconstruct sys.argv without our custom arguments for GTK
new_argv = [sys.argv[0]] + unknown
sys.argv = new_argv

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
    def on_activate(application):
        # UI elements are now created, set the timer duration (convert seconds to minutes)
        app.duration_spin.set_value(args.duration/60)
        # Start the timer
        app.on_start_clicked()
        
        # Close the app after timer duration plus exit delay
        GLib.timeout_add_seconds(args.duration + args.exit_delay, Gtk.main_quit)
    
    app.connect('activate', on_activate)
    
    # Run the application
    app.run(sys.argv)
    
    return 0

if __name__ == "__main__":
    main()