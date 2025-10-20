#!/usr/bin/env python3
"""
Script to easily set the preferred animation for TeaTime Accessibility.

Usage:
    python3 set_animation.py puppy_animation    # Set puppy animation
    python3 set_animation.py test_animation     # Set default test animation
    python3 set_animation.py my_animation       # Set custom animation
"""

import json
import sys
from pathlib import Path

# Configuration file path
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"

def set_preferred_animation(animation_name):
    """Set the preferred animation in the config file."""
    config = {}
    
    # Load existing config if it exists
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing config file: {e}")
    
    # Update the preferred animation
    config["preferred_animation"] = animation_name
    
    # Save the config
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Successfully set preferred animation to: {animation_name}")
    except Exception as e:
        print(f"Error saving config file: {e}")
        return False
    
    return True

def list_available_animations():
    """List available animations in the assets/sprites directory."""
    import os
    sprites_dir = Path(__file__).parent / "assets" / "sprites"
    
    if sprites_dir.exists():
        animations = [d.name for d in sprites_dir.iterdir() if d.is_dir()]
        print("Available animations:")
        for animation in animations:
            print(f"  - {animation}")
    else:
        print("Could not find sprites directory")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 set_animation.py <animation_name>")
        list_available_animations()
        sys.exit(1)
    
    animation_name = sys.argv[1]
    set_preferred_animation(animation_name)