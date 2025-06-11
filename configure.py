#!/usr/bin/env python3
"""
Configuration Utility for PoE Leveling Planner
Interactive script to configure overlay settings.
"""

import sys
from config_manager import ConfigManager


def main():
    config_manager = ConfigManager()
    
    print("PoE Leveling Planner - Configuration Utility")
    print("=" * 50)
    
    while True:
        print("\nCurrent Configuration:")
        config_manager.print_monitor_info()
        
        print(f"\nDisplay Settings:")
        print(f"  Monitor: {config_manager.get_setting('display', 'monitor')}")
        print(f"  Opacity: {config_manager.get_setting('display', 'opacity')}")
        
        print(f"\nAppearance:")
        print(f"  Size: {config_manager.get_setting('appearance', 'width')}x{config_manager.get_setting('appearance', 'height')}")
        print(f"  Background: {config_manager.get_setting('appearance', 'background_color')}")
        
        print(f"\nHotkeys:")
        print(f"  Previous Quest: {config_manager.get_setting('hotkeys', 'previous_quest')}")
        print(f"  Next Quest: {config_manager.get_setting('hotkeys', 'next_quest')}")
        
        print("\nOptions:")
        print("1. Change monitor")
        print("2. Change opacity")
        print("3. Change size")
        print("4. Test current settings")
        print("5. Reset to defaults")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "0":
            print("Configuration saved. Restart the overlay to apply changes.")
            break
        elif choice == "1":
            change_monitor(config_manager)
        elif choice == "2":
            change_opacity(config_manager)
        elif choice == "3":
            change_size(config_manager)
        elif choice == "4":
            test_settings(config_manager)
        elif choice == "5":
            reset_defaults(config_manager)
        else:
            print("Invalid choice. Please try again.")


def change_monitor(config_manager):
    """Change monitor setting"""
    monitors = config_manager.get_monitor_info()
    
    print("\nAvailable monitors:")
    print("0. Auto/Primary")
    for i, monitor in enumerate(monitors):
        print(f"{i+1}. {monitor['name']} - {monitor['width']}x{monitor['height']}")
    
    try:
        choice = input(f"\nSelect monitor (0-{len(monitors)}): ").strip()
        
        if choice == "0":
            config_manager.update_setting("display", "monitor", "auto")
            print("Monitor set to: Auto/Primary")
        else:
            monitor_index = int(choice) - 1
            if 0 <= monitor_index < len(monitors):
                config_manager.update_setting("display", "monitor", monitor_index)
                print(f"Monitor set to: {monitors[monitor_index]['name']}")
            else:
                print("Invalid monitor selection.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def change_opacity(config_manager):
    """Change opacity setting"""
    print("\nCurrent opacity:", config_manager.get_setting("display", "opacity"))
    
    try:
        opacity = float(input("Enter new opacity (0.1-1.0): ").strip())
        
        if 0.1 <= opacity <= 1.0:
            config_manager.update_setting("display", "opacity", opacity)
            print(f"Opacity set to: {opacity}")
        else:
            print("Opacity must be between 0.1 and 1.0")
    except ValueError:
        print("Invalid input. Please enter a decimal number.")


def change_size(config_manager):
    """Change overlay size"""
    current_width = config_manager.get_setting("appearance", "width")
    current_height = config_manager.get_setting("appearance", "height")
    
    print(f"\nCurrent size: {current_width}x{current_height}")
    
    try:
        width = int(input("Enter new width (100-800): ").strip())
        height = int(input("Enter new height (50-400): ").strip())
        
        if 100 <= width <= 800 and 50 <= height <= 400:
            config_manager.update_setting("appearance", "width", width)
            config_manager.update_setting("appearance", "height", height)
            print(f"Size set to: {width}x{height}")
        else:
            print("Width must be 100-800, height must be 50-400")
    except ValueError:
        print("Invalid input. Please enter numbers.")


def test_settings(config_manager):
    """Test current settings by showing calculated position"""
    print("\nTesting current settings...")
    x, y = config_manager.calculate_position()
    
    monitors = config_manager.get_monitor_info()
    monitor_setting = config_manager.get_setting("display", "monitor")
    
    print(f"Overlay will appear at position: ({x}, {y})")
    print(f"Monitor setting: {monitor_setting}")
    print("Position setting: Always centered")
    
    # Determine which monitor this position is on
    for i, monitor in enumerate(monitors):
        if (monitor["x"] <= x < monitor["x"] + monitor["width"] and 
            monitor["y"] <= y < monitor["y"] + monitor["height"]):
            print(f"This will place the overlay on: {monitor['name']}")
            break
    else:
        print("Warning: Calculated position may be off-screen!")


def reset_defaults(config_manager):
    """Reset configuration to defaults"""
    confirm = input("\nAre you sure you want to reset all settings to defaults? (y/N): ").strip().lower()
    
    if confirm == 'y' or confirm == 'yes':
        config_manager.config = config_manager.get_default_config()
        config_manager.save_config()
        print("Configuration reset to defaults.")
    else:
        print("Reset cancelled.")


if __name__ == "__main__":
    main() 