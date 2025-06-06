#!/usr/bin/env python3
"""
Test script for PoE Leveling Planner Overlay
This script helps test the overlay functionality and hotkeys.
"""

import time
import subprocess
import sys

def test_overlay():
    """Test the overlay application"""
    print("PoE Leveling Planner - Test Script")
    print("=" * 40)
    print()
    print("This script will help you test the overlay application.")
    print()
    print("Instructions:")
    print("1. The overlay should appear in the top-right corner of your screen")
    print("2. It should be semi-transparent (50% opacity) with dark background")
    print("3. Test the hotkeys:")
    print("   - Press Ctrl+X to change the text")
    print("   - Press Ctrl+Z to return to original text")
    print("4. The overlay should stay on top of all windows")
    print()
    
    # Check if main.py is running
    try:
        result = subprocess.run(['pgrep', '-f', 'python3 main.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Overlay application is running (PID: {})".format(result.stdout.strip()))
        else:
            print("✗ Overlay application is not running")
            print("  Run: python3 main.py")
            return
    except Exception as e:
        print(f"Error checking process: {e}")
        return
    
    print()
    print("Testing hotkeys...")
    print("Please test the following:")
    print("1. Press Ctrl+X - text should change to 'Hotkey Activated!'")
    print("2. Press Ctrl+Z - text should return to 'PoE Leveling Planner'")
    print()
    print("If the hotkeys work correctly, the overlay is functioning properly!")
    print()
    print("To stop the overlay, press Ctrl+C in the terminal where main.py is running")

if __name__ == "__main__":
    test_overlay() 