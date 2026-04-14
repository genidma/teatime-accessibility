#!/usr/bin/env python3

import json
import os
from pathlib import Path
from datetime import datetime

# Test script to check stats file writing
STATS_LOG_FILE = Path.home() / ".local/share/teatime_stats.json"

def test_stats_writing():
    print(f"Home directory: {Path.home()}")
    print(f"Stats file path: {STATS_LOG_FILE}")
    print(f"Stats file exists: {STATS_LOG_FILE.exists()}")
    
    # Test directory
    stats_dir = STATS_LOG_FILE.parent
    print(f"Stats directory: {stats_dir}")
    print(f"Stats directory exists: {stats_dir.exists()}")
    
    if not stats_dir.exists():
        print("Creating stats directory...")
        try:
            stats_dir.mkdir(parents=True, exist_ok=True)
            print("Directory created successfully")
        except Exception as e:
            print(f"Failed to create directory: {e}")
            return
    
    # Test writing a simple file
    test_file = stats_dir / "test_write.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test successful")
        print("Basic file write test: PASSED")
        test_file.unlink()  # Remove test file
    except Exception as e:
        print(f"Basic file write test: FAILED - {e}")
        return
    
    # Test JSON writing
    test_entry = {
        "timestamp": datetime.now().isoformat(),
        "duration": 5
    }
    
    try:
        with open(STATS_LOG_FILE, 'w') as f:
            json.dump([test_entry], f, indent=2)
        print("JSON write test: PASSED")
        
        # Test reading
        with open(STATS_LOG_FILE, 'r') as f:
            data = json.load(f)
        print(f"JSON read test: PASSED - Read {len(data)} entries")
        
        # Clean up
        STATS_LOG_FILE.unlink()
        
    except Exception as e:
        print(f"JSON write/read test: FAILED - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stats_writing()