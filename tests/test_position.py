#!/usr/bin/env python3
"""
Test script to find the best overlay position for multi-monitor setups
"""

import tkinter as tk
import time

def create_test_overlay(x, y, label_text):
    """Create a test overlay at specific coordinates"""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.8)  # More opaque for testing
    
    # Set window size
    window_width = 300
    window_height = 120
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg='#ff0000')  # Red background for visibility
    
    # Main frame
    main_frame = tk.Frame(root, bg='#ff0000', padx=10, pady=10)
    main_frame.pack(fill='both', expand=True)
    
    # Text label
    text_label = tk.Label(
        main_frame,
        text=f"TEST OVERLAY\n{label_text}\nPosition: {x}, {y}",
        bg='#ff0000',
        fg='white',
        font=('Arial', 12, 'bold'),
        justify='center'
    )
    text_label.pack(expand=True)
    
    return root

def main():
    screen_width = 4054  # Your detected screen width
    screen_height = 1366  # Your detected screen height
    
    print(f"Screen dimensions: {screen_width} x {screen_height}")
    print("Creating test overlays in different positions...")
    print("Look for RED overlays on your screen(s)")
    print("Press Ctrl+C to stop")
    
    # Test different positions
    positions = [
        (100, 100, "Top-Left"),
        (screen_width//2 - 150, 100, "Top-Center"),
        (screen_width - 320, 100, "Top-Right (Original)"),
        (1920 - 320, 100, "Monitor 1 Top-Right"),
        (100, screen_height//2, "Middle-Left"),
        (100, screen_height - 140, "Bottom-Left")
    ]
    
    overlays = []
    
    try:
        for x, y, label in positions:
            if x >= 0 and y >= 0:  # Only create if coordinates are positive
                overlay = create_test_overlay(x, y, label)
                overlays.append(overlay)
                print(f"Created overlay: {label} at ({x}, {y})")
        
        print(f"\nCreated {len(overlays)} test overlays")
        print("Check all your monitors for RED test overlays")
        
        # Keep the overlays visible
        if overlays:
            overlays[0].mainloop()
            
    except KeyboardInterrupt:
        print("\nStopping test overlays...")
        for overlay in overlays:
            try:
                overlay.destroy()
            except:
                pass

if __name__ == "__main__":
    main() 