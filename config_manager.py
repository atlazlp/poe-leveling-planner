#!/usr/bin/env python3
"""
Configuration Manager for PoE Leveling Planner
Handles loading, saving, and managing overlay settings.
"""

import json
import os
import tkinter as tk
from typing import Dict, Any, Tuple, List


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.get_default_config()
        else:
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "display": {
                "monitor": "auto",
                "position": "center",
                "x_offset": 0,
                "y_offset": 0,
                "custom_x": None,
                "custom_y": None,
                "opacity": 0.8,
                "always_on_top": True
            },
            "appearance": {
                "width": 250,
                "height": 100,
                "background_color": "#2b2b2b",
                "text_color": "#ffffff",
                "font_family": "Arial",
                "font_size": 10,
                "font_weight": "bold"
            },
            "hotkeys": {
                "toggle_text": "ctrl+1",
                "reset_text": "ctrl+2"
            },
            "content": {
                "default_text": "PoE Leveling Planner\nReady to assist!",
                "alternate_text": "Hotkey Activated!\nCtrl+Z to return"
            },
            "characters": {
                "profiles": [],
                "selected": ""
            },
            "language": {
                "current": "en_US"
            },
            "behavior": {
                "auto_hide_when_poe_not_running": False,
                "fade_in_duration": 0,
                "fade_out_duration": 0
            }
        }
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Get information about available monitors"""
        try:
            # Create a temporary root to get screen info
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
            
            total_width = temp_root.winfo_screenwidth()
            total_height = temp_root.winfo_screenheight()
            
            temp_root.destroy()
            
            # For now, we'll estimate monitor layout based on total width
            # This is a simplified approach - more advanced detection would require platform-specific code
            monitors = []
            
            if total_width > 3000:  # Likely multi-monitor or ultra-wide
                # Assume dual 1920x1080 monitors
                monitors = [
                    {"id": 0, "name": "Primary Monitor", "x": 0, "y": 0, "width": 1920, "height": 1080},
                    {"id": 1, "name": "Secondary Monitor", "x": 1920, "y": 0, "width": total_width - 1920, "height": total_height}
                ]
            else:
                # Single monitor
                monitors = [
                    {"id": 0, "name": "Primary Monitor", "x": 0, "y": 0, "width": total_width, "height": total_height}
                ]
            
            return monitors
            
        except Exception as e:
            print(f"Error detecting monitors: {e}")
            return [{"id": 0, "name": "Default Monitor", "x": 0, "y": 0, "width": 1920, "height": 1080}]
    
    def calculate_position(self) -> Tuple[int, int]:
        """Calculate overlay position based on configuration"""
        monitors = self.get_monitor_info()
        display_config = self.config["display"]
        appearance_config = self.config["appearance"]
        
        # Use custom position if specified
        if display_config["custom_x"] is not None and display_config["custom_y"] is not None:
            return display_config["custom_x"], display_config["custom_y"]
        
        # Determine target monitor
        monitor_setting = display_config["monitor"]
        if monitor_setting == "auto" or monitor_setting == "primary":
            target_monitor = monitors[0]
        elif monitor_setting == "secondary" and len(monitors) > 1:
            target_monitor = monitors[1]
        elif isinstance(monitor_setting, int) and 0 <= monitor_setting < len(monitors):
            target_monitor = monitors[monitor_setting]
        else:
            target_monitor = monitors[0]  # Fallback to primary
        
        # Always calculate center position
        width = appearance_config["width"]
        height = appearance_config["height"]
        
        monitor_x = target_monitor["x"]
        monitor_y = target_monitor["y"]
        monitor_width = target_monitor["width"]
        monitor_height = target_monitor["height"]
        
        # Calculate center position
        x = monitor_x + (monitor_width - width) // 2
        y = monitor_y + (monitor_height - height) // 2
        
        # Apply X/Y offsets
        x_offset = display_config.get("x_offset", 0)
        y_offset = display_config.get("y_offset", 0)
        x += x_offset
        y += y_offset
        
        return x, y
    
    def update_setting(self, section: str, key: str, value: Any) -> None:
        """Update a specific setting"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config()
        print(f"Updated {section}.{key} = {value} and saved to file")
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self.config.get(section, {}).get(key, default)
    
    def print_monitor_info(self) -> None:
        """Print detected monitor information"""
        monitors = self.get_monitor_info()
        print("Detected Monitors:")
        for i, monitor in enumerate(monitors):
            print(f"  {i}: {monitor['name']} - {monitor['width']}x{monitor['height']} at ({monitor['x']}, {monitor['y']})")
        print(f"\nCurrent monitor setting: {self.config['display']['monitor']}")
        print(f"Current position: {self.config['display']['position']}")
        
        x, y = self.calculate_position()
        print(f"Calculated overlay position: ({x}, {y})") 