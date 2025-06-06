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


class PoEOverlay:
    def __init__(self):
        self.config_manager = ConfigManager()
        
        # Create a hidden root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        
        # Create the actual overlay as a Toplevel window (like the working preview)
        self.overlay = tk.Toplevel(self.root)
        
        self.setup_window()
        self.setup_ui()
        self.setup_hotkeys()
        
        # Text states from config
        self.original_text = self.config_manager.get_setting("content", "default_text")
        self.alternate_text = self.config_manager.get_setting("content", "alternate_text")
        self.current_state = "original"
        
        # Update initial text
        self.text_label.config(text=self.original_text)
        
    def setup_window(self):
        """Configure the overlay window properties"""
        # Remove window decorations and make it stay on top
        self.overlay.overrideredirect(True)
        
        # Get settings from config
        always_on_top = self.config_manager.get_setting("display", "always_on_top", True)
        opacity = self.config_manager.get_setting("display", "opacity", 0.8)
        width = self.config_manager.get_setting("appearance", "width", 250)
        height = self.config_manager.get_setting("appearance", "height", 100)
        bg_color = self.config_manager.get_setting("appearance", "background_color", "#2b2b2b")
        
        # Calculate position based on config
        x_position, y_position = self.config_manager.calculate_position()
        
        # Set geometry first
        self.overlay.geometry(f"{width}x{height}+{x_position}+{y_position}")
        
        # Set window background color
        self.overlay.configure(bg=bg_color)
        
        # Set always on top
        if always_on_top:
            self.overlay.attributes('-topmost', True)
        
        # Set opacity (alpha) - this should now work like the preview window
        try:
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
        main_frame = tk.Frame(self.overlay, bg=bg_color, padx=5, pady=5)
        main_frame.pack(fill='both', expand=True)
        
        # Button frame in top-right corner
        button_frame = tk.Frame(main_frame, bg=bg_color)
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
            main_frame,
            text="",
            bg=bg_color,
            fg=text_color,
            font=(font_family, font_size, font_weight),
            justify='center'
        )
        self.text_label.pack(expand=True, fill='both')
        
        # Get hotkey settings for display
        toggle_key = self.config_manager.get_setting("hotkeys", "toggle_text", "ctrl+1").upper()
        reset_key = self.config_manager.get_setting("hotkeys", "reset_text", "ctrl+2").upper()
        
        # Instructions label
        instructions = tk.Label(
            main_frame,
            text=f"{toggle_key} | {reset_key}",
            bg=bg_color,
            fg='#888888',
            font=(font_family, 7),
            justify='center'
        )
        instructions.pack(side='bottom')
        
    def setup_hotkeys(self):
        """Setup global hotkey listeners"""
        def on_hotkey_toggle():
            self.toggle_to_alternate()
            
        def on_hotkey_reset():
            self.toggle_to_original()
        
        # Get hotkey settings from config
        toggle_hotkey = self.config_manager.get_setting("hotkeys", "toggle_text", "ctrl+1")
        reset_hotkey = self.config_manager.get_setting("hotkeys", "reset_text", "ctrl+2")
        
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
            parsed_toggle = parse_hotkey_safe(toggle_hotkey)
            parsed_reset = parse_hotkey_safe(reset_hotkey)
            
            if not parsed_toggle or not parsed_reset:
                print("Could not parse hotkeys, using defaults")
                parsed_toggle = "<ctrl>+1"
                parsed_reset = "<ctrl>+2"
            
            print(f"Parsed hotkeys: {parsed_toggle}, {parsed_reset}")
            
            # Create hotkey combinations
            hotkey_toggle = keyboard.HotKey(
                keyboard.HotKey.parse(parsed_toggle),
                on_hotkey_toggle
            )
            
            hotkey_reset = keyboard.HotKey(
                keyboard.HotKey.parse(parsed_reset),
                on_hotkey_reset
            )
            
            # Start the keyboard listener in a separate thread
            def start_listener():
                def on_press(key):
                    try:
                        hotkey_toggle.press(key)
                        hotkey_reset.press(key)
                    except Exception as e:
                        pass  # Ignore individual key press errors
                    
                def on_release(key):
                    try:
                        hotkey_toggle.release(key)
                        hotkey_reset.release(key)
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
            
            print(f"Hotkeys registered: {toggle_hotkey.upper()}, {reset_hotkey.upper()}")
            
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
            print("Hotkeys may not work properly")
        
    def toggle_to_alternate(self):
        """Switch to alternate text"""
        self.current_state = "alternate"
        self.text_label.config(text=self.alternate_text)
        toggle_key = self.config_manager.get_setting("hotkeys", "toggle_text", "ctrl+1")
        print(f"Hotkey {toggle_key.upper()} pressed - switched to alternate text")
        
    def toggle_to_original(self):
        """Switch back to original text"""
        self.current_state = "original"
        self.text_label.config(text=self.original_text)
        reset_key = self.config_manager.get_setting("hotkeys", "reset_text", "ctrl+2")
        print(f"Hotkey {reset_key.upper()} pressed - switched to original text")
        
    def open_config(self):
        """Open the configuration window"""
        try:
            print("Opening configuration window...")
            subprocess.Popen([sys.executable, "config_gui.py"], 
                           cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            print(f"Error opening config window: {e}")
    
    def close_application(self):
        """Close the application"""
        print("Closing application...")
        self.overlay.destroy()
        self.root.quit()
        
    def run(self):
        """Start the application"""
        print("PoE Leveling Planner started!")
        print("Configuration loaded from config.json")
        
        # Display current settings
        monitor_setting = self.config_manager.get_setting("display", "monitor", "auto")
        position_setting = self.config_manager.get_setting("display", "position", "top-right")
        opacity = self.config_manager.get_setting("display", "opacity", 0.8)
        
        print(f"Monitor: {monitor_setting}, Position: {position_setting}, Opacity: {opacity}")
        
        toggle_key = self.config_manager.get_setting("hotkeys", "toggle_text", "ctrl+1")
        reset_key = self.config_manager.get_setting("hotkeys", "reset_text", "ctrl+2")
        print(f"Hotkeys: {toggle_key.upper()} (change text), {reset_key.upper()} (original text)")
        print("Use overlay buttons or press Ctrl+C in terminal to exit")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.root.quit()


def main():
    """Main entry point"""
    try:
        app = PoEOverlay()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 