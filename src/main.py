#!/usr/bin/env python3
"""
PoE Leveling Planner - Desktop Overlay Application
A transparent overlay for Path of Exile with global hotkey support.
"""

import tkinter as tk
from tkinter import ttk
import threading
from pynput import keyboard
import sys
import os
import subprocess
from config_manager import ConfigManager
from language_manager import LanguageManager
from data_manager import DataManager
import json
import argparse


class PoEOverlay:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager(self.config_manager)
        self.data_manager = DataManager()
        
        # Create a hidden root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        
        # Create the actual overlay as a Toplevel window (like the working preview)
        self.overlay = tk.Toplevel(self.root)
        
        # Quest navigation state
        self.current_quest_index = 0
        self.available_quests = []
        
        # Data loading state
        self.data_loading = False
        self.data_loaded = False
        
        self.setup_window()
        self.setup_ui()
        self.setup_hotkeys()
        
        # Initialize data with the new data manager
        self.initialize_data()
        
    def initialize_data(self):
        """Initialize data using the centralized data manager"""
        if self.data_loading:
            return
            
        self.data_loading = True
        current_lang = self.language_manager.get_current_language()
        
        # Show loading status without destroying the main UI structure
        self.show_loading_message("Checking data...")
        
        def on_data_ready(success):
            """Callback when data initialization is complete"""
            self.data_loading = False
            self.data_loaded = success
            
            if success:
                print("Data initialization completed successfully")
                # Load available quests after data is ready
                self.root.after(0, self.load_available_quests)
            else:
                print("Data initialization failed")
                self.root.after(0, lambda: self.show_error_message("Failed to load data"))
        
        def progress_callback(message, current, total):
            """Progress callback for data loading"""
            self.root.after(0, lambda: self.show_loading_message(f"{message} ({current}/{total})"))
        
        # Start data initialization in background
        self.data_manager.initialize_data_async(
            current_lang, 
            callback=on_data_ready,
            progress_callback=progress_callback
        )
        
    def load_available_quests(self):
        """Load quests that have selected gems from the current character profile"""
        try:
            # Get current character profile
            characters = self.config_manager.get_setting("characters", "profiles")
            selected_profile = self.config_manager.get_setting("characters", "selected")
            
            if not characters or not selected_profile:
                print("No character profile selected")
                self.available_quests = []
                self.update_overlay_display()
                return
            
            current_profile = None
            for profile in characters:
                if profile.get("name") == selected_profile:
                    current_profile = profile
                    break
            
            if not current_profile:
                print("Selected character profile not found")
                self.available_quests = []
                self.update_overlay_display()
                return
            
            # Load data using the data manager
            current_lang = self.language_manager.get_current_language()
            quest_data = self.data_manager.get_quest_data(current_lang)
            vendor_data = self.data_manager.get_vendor_data(current_lang)
            
            if not quest_data:
                print("No quest data available")
                self.available_quests = []
                self.update_overlay_display()
                return
            
            # Get selected gems and vendor gems
            gem_selections = current_profile.get("gem_selections", {})
            vendor_gem_selections = current_profile.get("vendor_gem_selections", {})
            
            # Build list of available quests
            self.available_quests = []
            
            # Process quest rewards
            for quest in quest_data:
                quest_name = quest.get("name", "")
                quest_key = f"{quest_name}_{quest.get('act', '')}"
                
                # Check if this quest has selected gems
                selected_gem = gem_selections.get(quest_key)
                if selected_gem:
                    quest_info = {
                        "name": quest_name,
                        "act": quest.get("act", ""),
                        "type": "quest",
                        "selected_gem": selected_gem,
                        "vendor_gems": []
                    }
                    
                    # Find corresponding vendor gems
                    vendor_key = f"{quest_name}_Vendor"
                    if vendor_key in vendor_gem_selections:
                        vendor_gems = vendor_gem_selections[vendor_key]
                        if isinstance(vendor_gems, list):
                            quest_info["vendor_gems"] = vendor_gems
                    
                    self.available_quests.append(quest_info)
            
            # Process vendor-only quests (quests that only have vendor gems selected)
            for vendor_key, selected_vendor_gems in vendor_gem_selections.items():
                if selected_vendor_gems and isinstance(selected_vendor_gems, list) and vendor_key.endswith("_Vendor"):
                    quest_name = vendor_key.replace("_Vendor", "")
                    
                    # Check if we already added this quest
                    already_added = any(q["name"] == quest_name for q in self.available_quests)
                    if not already_added:
                        # Find quest info from vendor data
                        quest_act = "Unknown"
                        if vendor_data:
                            for vendor_quest in vendor_data:
                                if quest_name in vendor_quest.get("name", ""):
                                    quest_act = vendor_quest.get("act", "Unknown")
                                    break
                        
                        quest_info = {
                            "name": quest_name,
                            "act": quest_act,
                            "type": "vendor_only",
                            "selected_gem": None,
                            "vendor_gems": selected_vendor_gems
                        }
                        self.available_quests.append(quest_info)
            
            # Sort quests by act and name
            def sort_key(quest):
                act = quest.get("act", "Unknown")
                if act.startswith("Act "):
                    try:
                        act_num = int(act.split(" ")[1])
                        return (act_num, quest.get("name", ""))
                    except:
                        return (999, quest.get("name", ""))
                return (999, quest.get("name", ""))
            
            self.available_quests.sort(key=sort_key)
            
            print(f"Loaded {len(self.available_quests)} available quests")
            
            # Reset to first quest
            self.current_quest_index = 0
            self.update_overlay_display()
            
        except Exception as e:
            print(f"Error loading available quests: {e}")
            import traceback
            traceback.print_exc()
            self.available_quests = []
            # Use the safer error display method instead of update_overlay_display
            self.show_error_message("Failed to load quest data")
    
    def get_gem_color_hex(self, color):
        """Get hex color code for gem color"""
        color_hex = {
            "gem_red": "#ff4444",
            "gem_green": "#44ff44", 
            "gem_blue": "#4444ff"
        }
        return color_hex.get(color, "#ffffff")
    
    def update_overlay_display(self):
        """Update the overlay display with current quest information"""
        # Check if overlay still exists
        if not self.overlay or not self.overlay.winfo_exists():
            return
            
        if not self.available_quests:
            # Check if we have any character profiles at all
            characters = self.config_manager.get_setting("characters", "profiles", [])
            selected_profile = self.config_manager.get_setting("characters", "selected")
            
            if not characters:
                display_text = "Welcome to PoE Leveling Planner!\n\nClick the gear button above to:\n• Create your first character\n• Configure gem selections\n• Set up your preferences"
            elif not selected_profile:
                display_text = f"No character selected\n\nYou have {len(characters)} character(s) created.\nClick the gear button to select one\nand configure gem selections."
            else:
                display_text = "No quests with selected gems\n\nClick the gear button to:\n• Configure gem selections\n• Add more characters\n• Adjust settings"
            
            # Check if text_label still exists before updating
            if hasattr(self, 'text_label') and self.text_label and self.text_label.winfo_exists():
                self.text_label.config(text=display_text)
            return
        
        if self.current_quest_index >= len(self.available_quests):
            self.current_quest_index = 0
        
        current_quest = self.available_quests[self.current_quest_index]
        
        # Clear the current label and create a new frame for colored text
        if hasattr(self, 'text_label') and self.text_label and self.text_label.winfo_exists():
            self.text_label.destroy()
        
        # Check if main_frame still exists
        if not hasattr(self, 'main_frame') or not self.main_frame or not self.main_frame.winfo_exists():
            return
        
        # Get appearance settings
        bg_color = self.config_manager.get_setting("appearance", "background_color", "#2b2b2b")
        text_color = self.config_manager.get_setting("appearance", "text_color", "#ffffff")
        font_family = self.config_manager.get_setting("appearance", "font_family", "Arial")
        font_size = self.config_manager.get_setting("appearance", "font_size", 10)
        font_weight = self.config_manager.get_setting("appearance", "font_weight", "bold")
        
        # Create a frame to hold the text
        text_frame = tk.Frame(self.main_frame, bg=bg_color)
        text_frame.pack(expand=True, fill='both')
        
        # Quest name and act
        quest_title = f"{current_quest['name']}"
        if current_quest['act'] != "Unknown":
            quest_title += f" ({current_quest['act']})"
        
        title_label = tk.Label(
            text_frame,
            text=quest_title,
            bg=bg_color,
            fg=text_color,
            font=(font_family, font_size, font_weight),
            justify='left'
        )
        title_label.pack(anchor='w')
        
        # Empty line
        tk.Label(text_frame, text="", bg=bg_color).pack()
        
        # Selected quest gem
        if current_quest.get('selected_gem'):
            gem_name = current_quest['selected_gem']
            gem_color = self.get_gem_color_from_data(current_quest['name'], gem_name)
            gem_hex_color = self.get_gem_color_hex(gem_color)
            
            quest_gem_frame = tk.Frame(text_frame, bg=bg_color)
            quest_gem_frame.pack(anchor='w')
            
            tk.Label(
                quest_gem_frame,
                text="Quest Gem: ",
                bg=bg_color,
                fg=text_color,
                font=(font_family, font_size-1, "normal"),
                justify='left'
            ).pack(side='left')
            
            tk.Label(
                quest_gem_frame,
                text=gem_name,
                bg=bg_color,
                fg=gem_hex_color,
                font=(font_family, font_size-1, font_weight),
                justify='left'
            ).pack(side='left')
        
        # Vendor gems
        if current_quest.get('vendor_gems'):
            # Empty line
            tk.Label(text_frame, text="", bg=bg_color).pack()
            
            vendor_title_label = tk.Label(
                text_frame,
                text="Vendor Gems:",
                bg=bg_color,
                fg=text_color,
                font=(font_family, font_size-1, "normal"),
                justify='left'
            )
            vendor_title_label.pack(anchor='w')
            
            for vendor_gem in current_quest['vendor_gems']:
                gem_color = self.get_gem_color_from_vendor_data(current_quest['name'], vendor_gem)
                gem_hex_color = self.get_gem_color_hex(gem_color)
                
                vendor_gem_label = tk.Label(
                    text_frame,
                    text=f"  • {vendor_gem}",
                    bg=bg_color,
                    fg=gem_hex_color,
                    font=(font_family, font_size-2, "normal"),
                    justify='left'
                )
                vendor_gem_label.pack(anchor='w')
        
        # Quest counter
        if len(self.available_quests) > 1:
            # Empty line
            tk.Label(text_frame, text="", bg=bg_color).pack()
            
            counter_text = f"Quest {self.current_quest_index + 1} of {len(self.available_quests)}"
            counter_label = tk.Label(
                text_frame,
                text=counter_text,
                bg=bg_color,
                fg="#888888",
                font=(font_family, font_size-2, "normal"),
                justify='center'
            )
            counter_label.pack()
        
        # Store reference to the text frame for future updates
        self.text_label = text_frame
    
    def get_gem_color_from_data(self, quest_name, gem_name):
        """Get gem color from quest data"""
        try:
            current_lang = self.language_manager.get_current_language()
            quest_data = self.data_manager.get_quest_data(current_lang)
            
            if quest_data:
                for quest in quest_data:
                    if quest.get("name") == quest_name:
                        # Look through all class rewards for this gem
                        for class_name, rewards in quest.get("rewards", {}).items():
                            for gem in rewards:
                                if gem.get("name") == gem_name:
                                    return gem.get("color", "gem_red")
        except Exception as e:
            print(f"Error getting gem color from data: {e}")
        
        # Fallback to crawler's color detection
        return self.data_manager.quest_crawler.get_gem_color(gem_name)
    
    def get_gem_color_from_vendor_data(self, quest_name, gem_name):
        """Get gem color from vendor data"""
        try:
            current_lang = self.language_manager.get_current_language()
            vendor_data = self.data_manager.get_vendor_data(current_lang)
            
            if vendor_data:
                for quest in vendor_data:
                    if quest_name in quest.get("name", ""):
                        for gem in quest.get("class_rewards", []):
                            if gem.get("name") == gem_name:
                                return gem.get("color", "gem_red")
        except Exception as e:
            print(f"Error getting gem color from vendor data: {e}")
        
        # Fallback to crawler's color detection
        return self.data_manager.quest_crawler.get_gem_color(gem_name)
        
    def setup_window(self):
        """Configure the overlay window properties"""
        # Get settings from config first
        always_on_top = self.config_manager.get_setting("display", "always_on_top", True)
        opacity = self.config_manager.get_setting("display", "opacity", 0.8)
        width = self.config_manager.get_setting("appearance", "width", 350)
        height = self.config_manager.get_setting("appearance", "height", 250)
        bg_color = self.config_manager.get_setting("appearance", "background_color", "#2b2b2b")
        
        # Calculate position based on config
        x_position, y_position = self.config_manager.calculate_position()
        
        # Remove window decorations first
        self.overlay.overrideredirect(True)
        
        # Set geometry
        self.overlay.geometry(f"{width}x{height}+{x_position}+{y_position}")
        
        # Set window background color
        self.overlay.configure(bg=bg_color)
        
        # Update the window to ensure it's fully created
        self.overlay.update_idletasks()
        
        # Set always on top
        if always_on_top:
            self.overlay.attributes('-topmost', True)
        
        # Set opacity (alpha) - ensure this is done after window is fully configured
        try:
            # Force the window to be displayed first
            self.overlay.attributes('-alpha', 1.0)  # Start fully opaque
            self.overlay.update()  # Force update
            
            # Now set the desired opacity
            self.overlay.attributes('-alpha', opacity)
            print(f"Transparency set to: {opacity}")
            if opacity < 1.0:
                print("Window should appear semi-transparent")
            else:
                print("Window is fully opaque")
        except tk.TclError as e:
            print(f"Warning: Could not set transparency: {e}")
            print("Transparency may not be supported on this system")
        
        # Print position info for debugging
        print(f"Overlay positioned at: ({x_position}, {y_position})")
        self.config_manager.print_monitor_info()
        
    def setup_ui(self):
        """Create the UI elements"""
        # Get appearance settings from config
        bg_color = self.config_manager.get_setting("appearance", "background_color", "#2b2b2b")
        text_color = self.config_manager.get_setting("appearance", "text_color", "#ffffff")
        font_family = self.config_manager.get_setting("appearance", "font_family", "Arial")
        font_size = self.config_manager.get_setting("appearance", "font_size", 10)
        font_weight = self.config_manager.get_setting("appearance", "font_weight", "bold")
        
        # Main frame with configured background
        self.main_frame = tk.Frame(self.overlay, bg=bg_color, padx=5, pady=5)
        self.main_frame.pack(fill='both', expand=True)
        
        # Button frame in top-right corner
        button_frame = tk.Frame(self.main_frame, bg=bg_color)
        button_frame.pack(side='top', anchor='ne')
        
        # Config button (gear icon)
        config_btn = tk.Button(
            button_frame,
            text="⚙",
            font=('Arial', 8),
            bg=bg_color,
            fg=text_color,
            bd=0,
            padx=2,
            pady=0,
            command=self.open_config,
            relief='flat'
        )
        config_btn.pack(side='left', padx=(0, 2))
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="✕",
            font=('Arial', 8),
            bg=bg_color,
            fg='#ff6b6b',
            bd=0,
            padx=2,
            pady=0,
            command=self.close_application,
            relief='flat'
        )
        close_btn.pack(side='left')
        
        # Text label
        self.text_label = tk.Label(
            self.main_frame,
            text="Loading quest data...",
            bg=bg_color,
            fg=text_color,
            font=(font_family, font_size, font_weight),
            justify='left',
            anchor='nw'
        )
        self.text_label.pack(expand=True, fill='both')
        
        # Get hotkey settings for display
        prev_key = self.config_manager.get_setting("hotkeys", "previous_quest", "ctrl+1").upper()
        next_key = self.config_manager.get_setting("hotkeys", "next_quest", "ctrl+2").upper()
        copy_key = self.config_manager.get_setting("hotkeys", "copy_regex", "ctrl+3").upper()
        
        # Instructions label
        instructions = tk.Label(
            self.main_frame,
            text=f"{prev_key} Previous | {next_key} Next | {copy_key} Copy Regex",
            bg=bg_color,
            fg='#888888',
            font=(font_family, 7),
            justify='center'
        )
        instructions.pack(side='bottom')
        
    def setup_hotkeys(self):
        """Setup global hotkey listeners"""
        def on_hotkey_previous():
            self.previous_quest()
            
        def on_hotkey_next():
            self.next_quest()
            
        def on_hotkey_copy_regex():
            self.copy_regex()
        
        # Get hotkey settings from config with new names
        prev_hotkey = self.config_manager.get_setting("hotkeys", "previous_quest", "ctrl+1")
        next_hotkey = self.config_manager.get_setting("hotkeys", "next_quest", "ctrl+2")
        copy_regex_hotkey = self.config_manager.get_setting("hotkeys", "copy_regex", "ctrl+3")
        
        try:
            # Parse hotkeys more carefully
            def parse_hotkey_safe(hotkey_str):
                """Safely parse hotkey string"""
                try:
                    # Clean the string and handle common formats
                    hotkey_str = hotkey_str.lower().strip()
                    if '+' in hotkey_str:
                        parts = [part.strip() for part in hotkey_str.split('+')]
                        # Convert to pynput format
                        if len(parts) == 2:
                            modifier, key = parts
                            if modifier == 'ctrl':
                                return f'<ctrl>+{key}'
                            elif modifier == 'alt':
                                return f'<alt>+{key}'
                            elif modifier == 'shift':
                                return f'<shift>+{key}'
                    return hotkey_str
                except Exception as e:
                    print(f"Error parsing hotkey '{hotkey_str}': {e}")
                    return None
            
            # Parse hotkeys
            parsed_prev = parse_hotkey_safe(prev_hotkey)
            parsed_next = parse_hotkey_safe(next_hotkey)
            parsed_copy_regex = parse_hotkey_safe(copy_regex_hotkey)
            
            if not parsed_prev or not parsed_next or not parsed_copy_regex:
                print("Could not parse hotkeys, using defaults")
                parsed_prev = "<ctrl>+1"
                parsed_next = "<ctrl>+2"
                parsed_copy_regex = "<ctrl>+3"
            
            print(f"Parsed hotkeys: {parsed_prev}, {parsed_next}, {parsed_copy_regex}")
            
            # Create hotkey combinations
            hotkey_prev = keyboard.HotKey(
                keyboard.HotKey.parse(parsed_prev),
                on_hotkey_previous
            )
            
            hotkey_next = keyboard.HotKey(
                keyboard.HotKey.parse(parsed_next),
                on_hotkey_next
            )
            
            hotkey_copy_regex = keyboard.HotKey(
                keyboard.HotKey.parse(parsed_copy_regex),
                on_hotkey_copy_regex
            )
            
            # Start the keyboard listener in a separate thread
            def start_listener():
                def on_press(key):
                    try:
                        hotkey_prev.press(key)
                        hotkey_next.press(key)
                        hotkey_copy_regex.press(key)
                    except Exception as e:
                        pass  # Ignore individual key press errors
                    
                def on_release(key):
                    try:
                        hotkey_prev.release(key)
                        hotkey_next.release(key)
                        hotkey_copy_regex.release(key)
                    except Exception as e:
                        pass  # Ignore individual key release errors
                
                try:
                    with keyboard.Listener(
                        on_press=on_press,
                        on_release=on_release
                    ) as listener:
                        listener.join()
                except Exception as e:
                    print(f"Error starting keyboard listener: {e}")
            
            # Start listener in background thread
            listener_thread = threading.Thread(target=start_listener, daemon=True)
            listener_thread.start()
            
            print(f"Hotkeys registered: {prev_hotkey.upper()}, {next_hotkey.upper()}, {copy_regex_hotkey.upper()}")
            
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
            print("Hotkeys may not work properly")
        
    def previous_quest(self):
        """Navigate to previous quest"""
        if not self.available_quests:
            return
            
        self.current_quest_index = (self.current_quest_index - 1) % len(self.available_quests)
        self.update_overlay_display()
        prev_key = self.config_manager.get_setting("hotkeys", "previous_quest", "ctrl+1")
        print(f"Hotkey {prev_key.upper()} pressed - previous quest")
        
    def next_quest(self):
        """Navigate to next quest"""
        if not self.available_quests:
            return
            
        self.current_quest_index = (self.current_quest_index + 1) % len(self.available_quests)
        self.update_overlay_display()
        next_key = self.config_manager.get_setting("hotkeys", "next_quest", "ctrl+2")
        print(f"Hotkey {next_key.upper()} pressed - next quest")
    
    def copy_regex(self):
        """Copy regex pattern to clipboard based on current quest and selected character"""
        try:
            # Get selected character
            selected_char = self.config_manager.get_setting("characters", "selected", "")
            if not selected_char:
                print("No character selected - cannot copy regex")
                return
            
            # Get character data
            characters = self.config_manager.get_setting("characters", "profiles", [])
            character = next((char for char in characters if char["name"] == selected_char), None)
            
            if not character:
                print(f"Character '{selected_char}' not found - cannot copy regex")
                return
            
            regex_patterns = character.get('regex_patterns', [])
            if not regex_patterns:
                print(f"No regex patterns defined for character '{selected_char}'")
                return
            
            # Determine current act from quest data
            current_act = None
            if self.available_quests and 0 <= self.current_quest_index < len(self.available_quests):
                current_quest = self.available_quests[self.current_quest_index]
                act_text = current_quest.get('act', '')
                # Extract act number from text like "Act 1", "Act 2", etc.
                if act_text.startswith('Act '):
                    try:
                        act_num = int(act_text.split()[1])
                        current_act = f'act_{act_num}'
                    except (IndexError, ValueError):
                        pass
            
            # Find matching regex pattern
            regex_to_copy = None
            
            # First, try to find exact act match
            if current_act:
                for regex_item in regex_patterns:
                    if regex_item.get('act') == current_act:
                        regex_to_copy = regex_item.get('pattern', '')
                        break
            
            # If no exact match, try "all_acts" pattern
            if not regex_to_copy:
                for regex_item in regex_patterns:
                    if regex_item.get('act') == 'all_acts':
                        regex_to_copy = regex_item.get('pattern', '')
                        break
            
            if regex_to_copy:
                # Copy to clipboard
                import pyperclip
                pyperclip.copy(regex_to_copy)
                
                copy_key = self.config_manager.get_setting("hotkeys", "copy_regex", "ctrl+3")
                act_display = f"Act {current_act.split('_')[1]}" if current_act and current_act.startswith('act_') else "All Acts"
                print(f"Hotkey {copy_key.upper()} pressed - copied regex for {act_display} to clipboard")
                
                # Show brief feedback in overlay
                if hasattr(self, 'text_label') and self.text_label and self.text_label.winfo_exists():
                    original_text = self.text_label.cget('text')
                    self.text_label.config(text="Regex copied to clipboard!")
                    # Restore original text after 2 seconds
                    self.overlay.after(2000, lambda: self.text_label.config(text=original_text) if self.text_label.winfo_exists() else None)
            else:
                print(f"No regex pattern found for current context (character: {selected_char}, act: {current_act or 'unknown'})")
                
        except ImportError:
            print("pyperclip module not available - cannot copy to clipboard")
            print("Install with: pip install pyperclip")
        except Exception as e:
            print(f"Error copying regex: {e}")
        
    def open_config(self):
        """Open the configuration window"""
        try:
            print(self.language_manager.get_message("opening_config", "Opening configuration window..."))
            
            # Hide the overlay while config is open
            if self.overlay and self.overlay.winfo_exists():
                self.overlay.withdraw()
            
            # Check if we're running from a packaged executable
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # We're running from PyInstaller package
                # The config GUI is embedded in the same executable
                # We need to run it as a separate instance with a special flag
                import os
                exe_path = sys.executable
                subprocess.Popen([exe_path, "--config"], 
                               cwd=os.path.dirname(os.path.abspath(exe_path)))
            else:
                # We're running from source - use the original method
                subprocess.Popen([sys.executable, "config_gui.py"], 
                               cwd=os.path.dirname(os.path.abspath(__file__)))
            
            # Set up a timer to check when config window closes and restore overlay
            self.check_config_window()
                
        except Exception as e:
            print(f"{self.language_manager.get_message('error_opening_config', 'Error opening config window:')} {e}")
            # Restore overlay if there was an error
            if self.overlay and self.overlay.winfo_exists():
                self.overlay.deiconify()
    
    def check_config_window(self):
        """Check if config window is still open and restore overlay when it closes"""
        try:
            # Check if any config processes are running
            import psutil
            config_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline_str = ' '.join(proc.info['cmdline'])
                        # Check for both source mode and packaged mode
                        if ('config_gui.py' in cmdline_str or 
                            '--config' in cmdline_str):
                            config_running = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if config_running:
                # Config is still running, check again in 1 second
                self.overlay.after(1000, self.check_config_window)
            else:
                # Config closed, restore overlay and reload settings
                if self.overlay and self.overlay.winfo_exists():
                    self.overlay.deiconify()
                    # Reload configuration in case settings changed
                    self.reload_configuration()
                    
        except ImportError:
            # psutil not available, just restore overlay after 5 seconds
            self.overlay.after(5000, lambda: self.overlay.deiconify() if self.overlay and self.overlay.winfo_exists() else None)
        except Exception as e:
            print(f"Error checking config window: {e}")
            # Restore overlay on error
            if self.overlay and self.overlay.winfo_exists():
                self.overlay.deiconify()
    
    def reload_configuration(self):
        """Reload configuration after config window closes"""
        try:
            # Reload config manager
            self.config_manager = ConfigManager()
            self.language_manager = LanguageManager(self.config_manager)
            
            # Reload available quests in case character selection changed
            self.load_available_quests()
            
            # Update window properties
            self.update_window_properties()
            
            print("Configuration reloaded successfully")
        except Exception as e:
            print(f"Error reloading configuration: {e}")
    
    def update_window_properties(self):
        """Update window properties based on current configuration"""
        try:
            # Get updated settings
            always_on_top = self.config_manager.get_setting("display", "always_on_top", True)
            opacity = self.config_manager.get_setting("display", "opacity", 0.8)
            width = self.config_manager.get_setting("appearance", "width", 350)
            height = self.config_manager.get_setting("appearance", "height", 250)
            bg_color = self.config_manager.get_setting("appearance", "background_color", "#2b2b2b")
            
            # Calculate new position
            x_position, y_position = self.config_manager.calculate_position()
            
            # Update geometry
            self.overlay.geometry(f"{width}x{height}+{x_position}+{y_position}")
            
            # Update background color
            self.overlay.configure(bg=bg_color)
            if hasattr(self, 'main_frame') and self.main_frame:
                self.main_frame.configure(bg=bg_color)
            
            # Update always on top
            self.overlay.attributes('-topmost', always_on_top)
            
            # Update opacity
            self.overlay.attributes('-alpha', opacity)
            
            # Update display
            self.update_overlay_display()
            
        except Exception as e:
            print(f"Error updating window properties: {e}")
    
    def close_application(self):
        """Close the application"""
        print(self.language_manager.get_message("closing_app", "Closing application..."))
        self.overlay.destroy()
        self.root.quit()
        
    def run(self):
        """Start the application"""
        print(self.language_manager.get_message("app_started", "PoE Leveling Planner started!"))
        print(self.language_manager.get_message("config_loaded", "Configuration loaded from config.json"))
        
        # Display current settings
        monitor_setting = self.config_manager.get_setting("display", "monitor", "auto")
        position_setting = self.config_manager.get_setting("display", "position", "top-right")
        opacity = self.config_manager.get_setting("display", "opacity", 0.8)
        
        print(f"{self.language_manager.get_message('monitor_info', 'Monitor')}: {monitor_setting}, {self.language_manager.get_message('position_info', 'Position')}: {position_setting}, Opacity: {opacity}")
        
        prev_key = self.config_manager.get_setting("hotkeys", "previous_quest", "ctrl+1")
        next_key = self.config_manager.get_setting("hotkeys", "next_quest", "ctrl+2")
        copy_key = self.config_manager.get_setting("hotkeys", "copy_regex", "ctrl+3")
        print(f"Hotkeys: {prev_key.upper()} (previous quest), {next_key.upper()} (next quest), {copy_key.upper()} (copy regex)")
        print(self.language_manager.get_message("hotkey_instructions", "Use overlay buttons or press Ctrl+C in terminal to exit"))
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.root.quit()

    def show_loading_message(self, message):
        """Show loading message without destroying the main UI structure"""
        if hasattr(self, 'text_label') and self.text_label and self.text_label.winfo_exists():
            self.text_label.config(text=f"{message}\nPlease wait...")
    
    def show_error_message(self, error_message):
        """Show error message without destroying the main UI structure"""
        if hasattr(self, 'text_label') and self.text_label and self.text_label.winfo_exists():
            self.text_label.config(text=f"Error: {error_message}\n\nThe configuration is still accessible.\nClick the gear button to:\n• Check your settings\n• Create/select a character\n• Refresh data")


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PoE Leveling Planner')
    parser.add_argument('--config', action='store_true', help='Open configuration window')
    
    try:
        args = parser.parse_args()
        
        if args.config:
            # Launch config GUI
            from config_gui import ConfigGUI
            config_app = ConfigGUI()
            config_app.run()
        else:
            # Launch main overlay
            app = PoEOverlay()
            app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 