#!/usr/bin/env python3
"""
Demo script for the new gem card functionality in PoE Leveling Planner

This script demonstrates:
1. Quest cards with same width as overlay
2. Clickable gems with selection state
3. Data persistence for gem selections
4. Responsive card layout
"""

import tkinter as tk
from tkinter import messagebox
from config_gui import ConfigGUI

def demo_gem_cards():
    """Demo the gem card functionality"""
    print("=== PoE Leveling Planner - Gem Cards Demo ===")
    print()
    print("New Features:")
    print("1. ✅ Quest cards with same width as overlay")
    print("2. ✅ Clickable gems with selection state")
    print("3. ✅ Grayed out non-selected gems when one is selected")
    print("4. ✅ Responsive card layout (multiple cards per row)")
    print("5. ✅ Data persistence for gem selections")
    print("6. ✅ Hover effects and improved styling")
    print()
    print("Instructions:")
    print("- Go to the 'Gems' tab")
    print("- Create or select a character")
    print("- Click on gems to select them")
    print("- Selected gems will be highlighted and others grayed out")
    print("- Selections are automatically saved")
    print()
    
    # Create and run the config GUI
    try:
        config_gui = ConfigGUI()
        config_gui.run()
    except Exception as e:
        print(f"Error running demo: {e}")
        messagebox.showerror("Error", f"Failed to run demo: {e}")

if __name__ == "__main__":
    demo_gem_cards() 