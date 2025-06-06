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


class PoEOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        self.setup_hotkeys()
        
        # Text states
        self.original_text = "PoE Leveling Planner\nReady to assist!"
        self.alternate_text = "Hotkey Activated!\nCtrl+Z to return"
        self.current_state = "original"
        
        # Update initial text
        self.text_label.config(text=self.original_text)
        
    def setup_window(self):
        """Configure the overlay window properties"""
        # Remove window decorations and make it stay on top
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)  # 50% opacity
        
        # Set window size
        window_width = 250
        window_height = 100
        
        # Position in top-right corner with some margin
        screen_width = self.root.winfo_screenwidth()
        x_position = screen_width - window_width - 20
        y_position = 20
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Make window background dark
        self.root.configure(bg='#2b2b2b')
        
    def setup_ui(self):
        """Create the UI elements"""
        # Main frame with dark background
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Text label
        self.text_label = tk.Label(
            main_frame,
            text="",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10, 'bold'),
            justify='center'
        )
        self.text_label.pack(expand=True)
        
        # Instructions label
        instructions = tk.Label(
            main_frame,
            text="Ctrl+X | Ctrl+Z",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 8),
            justify='center'
        )
        instructions.pack(side='bottom')
        
    def setup_hotkeys(self):
        """Setup global hotkey listeners"""
        def on_hotkey_ctrl_x():
            self.toggle_to_alternate()
            
        def on_hotkey_ctrl_z():
            self.toggle_to_original()
            
        # Create hotkey combinations
        hotkey_ctrl_x = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+x'),
            on_hotkey_ctrl_x
        )
        
        hotkey_ctrl_z = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+z'),
            on_hotkey_ctrl_z
        )
        
        # Listener function
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
            
        # Start the keyboard listener in a separate thread
        def start_listener():
            with keyboard.Listener(
                on_press=for_canonical(lambda key: [
                    hotkey_ctrl_x.press(key),
                    hotkey_ctrl_z.press(key)
                ]),
                on_release=for_canonical(lambda key: [
                    hotkey_ctrl_x.release(key),
                    hotkey_ctrl_z.release(key)
                ])
            ) as listener:
                listener.join()
        
        # Start listener in background thread
        listener_thread = threading.Thread(target=start_listener, daemon=True)
        listener_thread.start()
        
    def toggle_to_alternate(self):
        """Switch to alternate text"""
        self.current_state = "alternate"
        self.text_label.config(text=self.alternate_text)
        print("Hotkey Ctrl+X pressed - switched to alternate text")
        
    def toggle_to_original(self):
        """Switch back to original text"""
        self.current_state = "original"
        self.text_label.config(text=self.original_text)
        print("Hotkey Ctrl+Z pressed - switched to original text")
        
    def run(self):
        """Start the application"""
        print("PoE Leveling Planner started!")
        print("Overlay visible in top-right corner")
        print("Hotkeys: Ctrl+X (change text), Ctrl+Z (original text)")
        print("Press Ctrl+C in terminal to exit")
        
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
        sys.exit(1)


if __name__ == "__main__":
    main() 