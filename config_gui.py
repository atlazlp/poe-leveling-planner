#!/usr/bin/env python3
"""
Visual Configuration GUI for PoE Leveling Planner
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from config_manager import ConfigManager
from language_manager import LanguageManager


class ConfigGUI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager(self.config_manager)
        self.root = tk.Tk()
        self.test_window = None  # For live testing
        self.debounce_timer = None  # For debouncing slider updates
        self.drag_start_x = None  # For window dragging
        self.drag_start_y = None  # For window dragging
        self.setup_window()
        self.setup_ui()
        self.load_current_settings()
        self.start_live_testing()
        
    def setup_window(self):
        """Setup the main configuration window"""
        self.root.title(self.language_manager.get_ui_text("window_title", "PoE Leveling Planner - Configuration"))
        self.root.geometry("500x750")  # Increased height for language section
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (750 // 2)
        self.root.geometry(f"500x750+{x}+{y}")
        
        # Make it stay on top initially
        self.root.attributes('-topmost', True)
        self.root.after(1000, lambda: self.root.attributes('-topmost', False))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Create the UI elements"""
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text=self.language_manager.get_ui_text("main_title", "PoE Leveling Planner Configuration"), 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        row = 1
        
        # Language Selection Section
        language_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("language_settings", "Language Settings"), padding="10")
        language_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(language_frame, text=self.language_manager.get_ui_text("language", "Language:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.language_var = tk.StringVar()
        language_options = list(self.language_manager.get_available_languages().values())
        self.language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                         values=language_options, state="readonly", width=30)
        self.language_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        language_frame.columnconfigure(1, weight=1)
        
        # Monitor Selection Section
        monitor_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("monitor_settings", "Monitor Settings"), padding="10")
        monitor_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(monitor_frame, text=self.language_manager.get_ui_text("monitor", "Monitor:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.monitor_var = tk.StringVar()
        self.monitor_combo = ttk.Combobox(monitor_frame, textvariable=self.monitor_var, 
                                         state="readonly", width=30)
        self.monitor_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Position is now hidden and always set to "center"
        self.position_var = tk.StringVar(value="center")
        
        monitor_frame.columnconfigure(1, weight=1)
        
        # Position Offset Section
        offset_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("position_offset", "Position Offset"), padding="10")
        offset_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # X Offset
        ttk.Label(offset_frame, text=self.language_manager.get_ui_text("x_offset", "X Offset:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_offset_var = tk.IntVar()
        x_offset_scale = ttk.Scale(offset_frame, from_=-1500, to=1500, variable=self.x_offset_var,
                                  orient=tk.HORIZONTAL, length=200)
        x_offset_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.x_offset_label = ttk.Label(offset_frame, text="0")
        self.x_offset_label.grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Y Offset
        ttk.Label(offset_frame, text=self.language_manager.get_ui_text("y_offset", "Y Offset:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_offset_var = tk.IntVar()
        y_offset_scale = ttk.Scale(offset_frame, from_=-1500, to=1500, variable=self.y_offset_var,
                                  orient=tk.HORIZONTAL, length=200)
        y_offset_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.y_offset_label = ttk.Label(offset_frame, text="0")
        self.y_offset_label.grid(row=1, column=2, padx=(10, 0), pady=2)
        
        # Update offset labels when scales change
        def update_x_offset_label(*args):
            self.x_offset_label.config(text=f"{self.x_offset_var.get()}")
        def update_y_offset_label(*args):
            self.y_offset_label.config(text=f"{self.y_offset_var.get()}")
        
        self.x_offset_var.trace('w', update_x_offset_label)
        self.y_offset_var.trace('w', update_y_offset_label)
        
        offset_frame.columnconfigure(1, weight=1)
        
        # Appearance Section
        appearance_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("appearance", "Appearance"), padding="10")
        appearance_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # Opacity
        ttk.Label(appearance_frame, text=self.language_manager.get_ui_text("opacity", "Opacity:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.opacity_var = tk.DoubleVar()
        opacity_scale = ttk.Scale(appearance_frame, from_=0.1, to=1.0, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, length=200)
        opacity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.opacity_label = ttk.Label(appearance_frame, text="0.8")
        self.opacity_label.grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Update opacity label when scale changes
        def update_opacity_label(*args):
            self.opacity_label.config(text=f"{self.opacity_var.get():.1f}")
        self.opacity_var.trace('w', update_opacity_label)
        
        # Size
        ttk.Label(appearance_frame, text=self.language_manager.get_ui_text("width", "Width:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.IntVar()
        width_spin = ttk.Spinbox(appearance_frame, from_=100, to=800, textvariable=self.width_var, width=10)
        width_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(appearance_frame, text=self.language_manager.get_ui_text("height", "Height:")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.height_var = tk.IntVar()
        height_spin = ttk.Spinbox(appearance_frame, from_=50, to=400, textvariable=self.height_var, width=10)
        height_spin.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        appearance_frame.columnconfigure(1, weight=1)
        
        # Hotkeys Section
        hotkey_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("hotkeys", "Hotkeys"), padding="10")
        hotkey_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(hotkey_frame, text=self.language_manager.get_ui_text("toggle_text", "Toggle Text:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.toggle_key_var = tk.StringVar()
        toggle_combo = ttk.Combobox(hotkey_frame, textvariable=self.toggle_key_var,
                                   values=["ctrl+1", "ctrl+x", "ctrl+t", "alt+x", "alt+t", "shift+x"],
                                   width=15)
        toggle_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(hotkey_frame, text=self.language_manager.get_ui_text("reset_text", "Reset Text:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.reset_key_var = tk.StringVar()
        reset_combo = ttk.Combobox(hotkey_frame, textvariable=self.reset_key_var,
                                  values=["ctrl+2", "ctrl+z", "ctrl+r", "alt+z", "alt+r", "shift+z"],
                                  width=15)
        reset_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Content Section
        content_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("text_content", "Text Content"), padding="10")
        content_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(content_frame, text=self.language_manager.get_ui_text("default_text", "Default Text:")).grid(row=0, column=0, sticky=(tk.W, tk.N), pady=2)
        self.default_text_var = tk.StringVar()
        default_text_entry = tk.Text(content_frame, height=3, width=40)
        default_text_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.default_text_widget = default_text_entry
        
        ttk.Label(content_frame, text=self.language_manager.get_ui_text("alternate_text", "Alternate Text:")).grid(row=1, column=0, sticky=(tk.W, tk.N), pady=2)
        self.alternate_text_var = tk.StringVar()
        alternate_text_entry = tk.Text(content_frame, height=3, width=40)
        alternate_text_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.alternate_text_widget = alternate_text_entry
        
        content_frame.columnconfigure(1, weight=1)
        
        # Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("live_preview", "Live Preview"), padding="10")
        preview_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        self.preview_label = ttk.Label(preview_frame, text="Position: (0, 0)\nMonitor: Primary", 
                                      font=('Arial', 9))
        self.preview_label.grid(row=0, column=0, sticky=tk.W)
        
        # Minimize/Restore button for config window
        minimize_frame = ttk.Frame(preview_frame)
        minimize_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.minimize_btn = ttk.Button(minimize_frame, text=self.language_manager.get_ui_text("hide_config_window", "Hide Config Window"), command=self.toggle_config_window)
        self.minimize_btn.pack(side=tk.LEFT)
        
        self.config_hidden = False
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text=self.language_manager.get_ui_text("save_restart", "Save & Restart"), command=self.save_and_restart).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.language_manager.get_ui_text("cancel", "Cancel"), command=self.cancel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.language_manager.get_ui_text("reset_to_default", "Reset to Default"), command=self.reset_defaults).pack(side=tk.LEFT)
        
        main_frame.columnconfigure(0, weight=1)
        
        # Update preview when settings change - with debouncing for sliders
        for var in [self.monitor_var, self.position_var]:
            var.trace('w', self.update_live_preview)
        
        # Add debounced updates for sliders to prevent lag
        for var in [self.x_offset_var, self.y_offset_var, self.width_var, self.height_var, self.opacity_var]:
            var.trace('w', self.debounced_update)
    
    def debounced_update(self, *args):
        """Debounced update for slider changes to prevent lag"""
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
        self.debounce_timer = self.root.after(100, self.update_live_preview)  # 100ms delay
    
    def load_current_settings(self):
        """Load current settings into the GUI"""
        # Load language setting
        current_language = self.config_manager.get_setting("language", "current", "en_US")
        language_name = self.language_manager.get_available_languages().get(current_language, "English (US)")
        self.language_var.set(language_name)
        
        # Load monitor options
        monitors = self.config_manager.get_monitor_info()
        monitor_options = [self.language_manager.get_ui_text("auto_primary", "Auto/Primary")]
        for i, monitor in enumerate(monitors):
            monitor_options.append(f"{monitor['name']} - {monitor['width']}x{monitor['height']}")
        
        self.monitor_combo['values'] = monitor_options
        
        # Set current values
        current_monitor = self.config_manager.get_setting("display", "monitor")
        if current_monitor == "auto":
            self.monitor_var.set(self.language_manager.get_ui_text("auto_primary", "Auto/Primary"))
        elif isinstance(current_monitor, int):
            if current_monitor < len(monitors):
                monitor_name = f"{monitors[current_monitor]['name']} - {monitors[current_monitor]['width']}x{monitors[current_monitor]['height']}"
                self.monitor_var.set(monitor_name)
            else:
                self.monitor_var.set(self.language_manager.get_ui_text("auto_primary", "Auto/Primary"))
        
        self.position_var.set(self.config_manager.get_setting("display", "position", "top-right"))
        self.x_offset_var.set(self.config_manager.get_setting("display", "x_offset", 0))
        self.y_offset_var.set(self.config_manager.get_setting("display", "y_offset", 0))
        self.opacity_var.set(self.config_manager.get_setting("display", "opacity", 0.8))
        self.width_var.set(self.config_manager.get_setting("appearance", "width", 250))
        self.height_var.set(self.config_manager.get_setting("appearance", "height", 100))
        self.toggle_key_var.set(self.config_manager.get_setting("hotkeys", "toggle_text", "ctrl+1"))
        self.reset_key_var.set(self.config_manager.get_setting("hotkeys", "reset_text", "ctrl+2"))
        
        # Load text content
        default_text = self.config_manager.get_setting("content", "default_text", self.language_manager.get_content("default_text", "PoE Leveling Planner\nReady to assist!"))
        alternate_text = self.config_manager.get_setting("content", "alternate_text", self.language_manager.get_content("alternate_text", "Hotkey Activated!\nCtrl+2 to return"))
        
        self.default_text_widget.delete(1.0, tk.END)
        self.default_text_widget.insert(1.0, default_text)
        
        self.alternate_text_widget.delete(1.0, tk.END)
        self.alternate_text_widget.insert(1.0, alternate_text)
    
    def start_live_testing(self):
        """Start the live testing overlay"""
        self.update_live_preview()
    
    def update_live_preview(self, *args):
        """Update the live preview overlay and information"""
        try:
            # Get selected monitor index
            monitor_selection = self.monitor_var.get()
            if monitor_selection == "Auto/Primary":
                monitor_index = 0
            else:
                # Extract index from selection
                monitors = self.config_manager.get_monitor_info()
                for i, monitor in enumerate(monitors):
                    if f"{monitor['name']} - {monitor['width']}x{monitor['height']}" == monitor_selection:
                        monitor_index = i
                        break
                else:
                    monitor_index = 0
            
            # Temporarily update config for preview
            old_monitor = self.config_manager.config["display"]["monitor"]
            old_position = self.config_manager.config["display"]["position"]
            old_x_offset = self.config_manager.config["display"].get("x_offset", 0)
            old_y_offset = self.config_manager.config["display"].get("y_offset", 0)
            
            self.config_manager.config["display"]["monitor"] = monitor_index
            self.config_manager.config["display"]["position"] = self.position_var.get()
            self.config_manager.config["display"]["x_offset"] = self.x_offset_var.get()
            self.config_manager.config["display"]["y_offset"] = self.y_offset_var.get()
            
            x, y = self.config_manager.calculate_position()
            
            # Restore original values
            self.config_manager.config["display"]["monitor"] = old_monitor
            self.config_manager.config["display"]["position"] = old_position
            self.config_manager.config["display"]["x_offset"] = old_x_offset
            self.config_manager.config["display"]["y_offset"] = old_y_offset
            
            monitors = self.config_manager.get_monitor_info()
            monitor_name = monitors[monitor_index]["name"] if monitor_index < len(monitors) else "Primary"
            
            self.preview_label.config(text=f"Position: ({x}, {y})\nMonitor: {monitor_name}")
            
            # Update live test overlay
            self.update_test_overlay(x, y)
            
        except Exception as e:
            self.preview_label.config(text="Position: (0, 0)\nMonitor: Primary")
            print(f"Error updating preview: {e}")
    
    def update_test_overlay(self, x, y):
        """Update or create the live test overlay"""
        try:
            if self.test_window is None:
                # Create test overlay
                self.test_window = tk.Toplevel(self.root)
                self.test_window.overrideredirect(True)
                self.test_window.attributes('-topmost', True)
                self.test_window.configure(bg='red')
                
                label = tk.Label(self.test_window, text="LIVE PREVIEW\nOverlay Position\nDrag to move", 
                               bg='red', fg='white', font=('Arial', 8, 'bold'), justify='center')
                label.pack(expand=True)
                
                # Add drag functionality
                label.bind('<Button-1>', self.start_drag)
                label.bind('<B1-Motion>', self.on_drag)
                label.bind('<ButtonRelease-1>', self.end_drag)
                
                # Don't let the test window be destroyed by user
                self.test_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Update position, size, and opacity
            width = self.width_var.get()
            height = self.height_var.get()
            opacity = self.opacity_var.get()
            
            self.test_window.geometry(f"{width}x{height}+{x}+{y}")
            self.test_window.attributes('-alpha', opacity * 0.7)  # Slightly more visible for preview
            
        except Exception as e:
            print(f"Error updating test overlay: {e}")
    
    def start_drag(self, event):
        """Start window drag operation"""
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.window_start_x = self.test_window.winfo_x()
        self.window_start_y = self.test_window.winfo_y()

    def on_drag(self, event):
        """Handle window dragging"""
        if self.drag_start_x is not None:
            # Calculate the distance moved
            dx = event.x_root - self.drag_start_x
            dy = event.y_root - self.drag_start_y
            
            # Calculate new position
            new_x = self.window_start_x + dx
            new_y = self.window_start_y + dy
            
            # Update window position
            self.test_window.geometry(f"+{new_x}+{new_y}")
            
            # Update offset values based on the center position
            monitor_selection = self.monitor_var.get()
            if monitor_selection == "Auto/Primary":
                monitor_index = 0
            else:
                monitors = self.config_manager.get_monitor_info()
                for i, monitor in enumerate(monitors):
                    if f"{monitor['name']} - {monitor['width']}x{monitor['height']}" == monitor_selection:
                        monitor_index = i
                        break
                else:
                    monitor_index = 0
            
            # Get monitor info
            monitors = self.config_manager.get_monitor_info()
            monitor = monitors[monitor_index]
            
            # Calculate center position of monitor
            center_x = monitor["x"] + (monitor["width"] - self.width_var.get()) // 2
            center_y = monitor["y"] + (monitor["height"] - self.height_var.get()) // 2
            
            # Calculate offsets from center
            x_offset = new_x - center_x
            y_offset = new_y - center_y
            
            # Update offset values
            self.x_offset_var.set(x_offset)
            self.y_offset_var.set(y_offset)

    def end_drag(self, event):
        """End window drag operation"""
        self.drag_start_x = None
        self.drag_start_y = None
    
    def save_and_restart(self):
        """Save configuration and restart the overlay"""
        if self.save_config():
            try:
                # Kill any existing overlay processes
                subprocess.run(["pkill", "-f", "main.py"], capture_output=True)
                
                # Start new overlay process
                subprocess.Popen([sys.executable, "main.py"], 
                               cwd=os.path.dirname(os.path.abspath(__file__)))
                
                messagebox.showinfo("Success", "Configuration saved and overlay restarted!")
                self.root.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not restart overlay: {e}")
    
    def save_config(self):
        """Save the current configuration"""
        try:
            # Get monitor index
            monitor_selection = self.monitor_var.get()
            auto_primary_text = self.language_manager.get_ui_text("auto_primary", "Auto/Primary")
            if monitor_selection == auto_primary_text:
                monitor_value = "auto"
            else:
                monitors = self.config_manager.get_monitor_info()
                for i, monitor in enumerate(monitors):
                    if f"{monitor['name']} - {monitor['width']}x{monitor['height']}" == monitor_selection:
                        monitor_value = i
                        break
                else:
                    monitor_value = "auto"
            
            # Get language code from selected language name
            selected_language_name = self.language_var.get()
            language_code = "en_US"  # Default
            for code, name in self.language_manager.get_available_languages().items():
                if name == selected_language_name:
                    language_code = code
                    break
            
            # Update all settings
            self.config_manager.update_setting("display", "monitor", monitor_value)
            self.config_manager.update_setting("display", "position", self.position_var.get())
            self.config_manager.update_setting("display", "x_offset", self.x_offset_var.get())
            self.config_manager.update_setting("display", "y_offset", self.y_offset_var.get())
            self.config_manager.update_setting("display", "opacity", self.opacity_var.get())
            self.config_manager.update_setting("appearance", "width", self.width_var.get())
            self.config_manager.update_setting("appearance", "height", self.height_var.get())
            self.config_manager.update_setting("hotkeys", "toggle_text", self.toggle_key_var.get())
            self.config_manager.update_setting("hotkeys", "reset_text", self.reset_key_var.get())
            self.config_manager.update_setting("language", "current", language_code)
            
            # Update text content
            default_text = self.default_text_widget.get(1.0, tk.END).strip()
            alternate_text = self.alternate_text_widget.get(1.0, tk.END).strip()
            self.config_manager.update_setting("content", "default_text", default_text)
            self.config_manager.update_setting("content", "alternate_text", alternate_text)
            
            # Force save to file
            self.config_manager.save_config()
            print(self.language_manager.get_message("config_saved", "Configuration saved to config.json"))
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"{self.language_manager.get_message('error_saving_config', 'Could not save configuration:')} {e}")
            return False
    
    def cancel(self):
        """Cancel without saving"""
        self.root.destroy()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno(self.language_manager.get_ui_text("reset_to_default", "Confirm Reset"), 
                              self.language_manager.get_message("confirm_reset", "Are you sure you want to reset all settings to defaults?")):
            self.config_manager.config = self.config_manager.get_default_config()
            self.config_manager.save_config()
            # Reload language manager with new config
            self.language_manager = LanguageManager(self.config_manager)
            self.load_current_settings()
            messagebox.showinfo("Success", self.language_manager.get_message("reset_success", "Settings reset to defaults!"))
    
    def on_closing(self):
        """Handle window closing"""
        if self.test_window:
            self.test_window.destroy()
        if hasattr(self, 'restore_window'):
            self.restore_window.destroy()
        self.root.destroy()
    
    def toggle_config_window(self):
        """Toggle visibility of the config window"""
        if self.config_hidden:
            self.root.deiconify()  # Show window
            self.minimize_btn.config(text=self.language_manager.get_ui_text("hide_config_window", "Hide Config Window"))
            self.config_hidden = False
        else:
            self.root.withdraw()  # Hide window
            self.minimize_btn.config(text=self.language_manager.get_ui_text("show_config_window", "Show Config Window"))
            self.config_hidden = True
            
            # Create a small restore button that stays visible
            if not hasattr(self, 'restore_window'):
                self.restore_window = tk.Toplevel(self.root)
                self.restore_window.title("Show Config")
                self.restore_window.geometry("120x40+50+50")
                self.restore_window.attributes('-topmost', True)
                self.restore_window.resizable(False, False)
                
                restore_btn = tk.Button(self.restore_window, text="Show Config", 
                                      command=self.show_config_window, font=('Arial', 8))
                restore_btn.pack(fill='both', expand=True)
                
                self.restore_window.protocol("WM_DELETE_WINDOW", self.show_config_window)

    def show_config_window(self):
        """Show the config window and destroy restore button"""
        if hasattr(self, 'restore_window'):
            self.restore_window.destroy()
            delattr(self, 'restore_window')
        
        self.root.deiconify()
        self.minimize_btn.config(text=self.language_manager.get_ui_text("hide_config_window", "Hide Config Window"))
        self.config_hidden = False
    
    def on_language_change(self, event=None):
        """Handle language selection change"""
        selected_language_name = self.language_var.get()
        # Find the language code for the selected name
        for code, name in self.language_manager.get_available_languages().items():
            if name == selected_language_name:
                if self.language_manager.set_language(code):
                    # Refresh the UI with new language
                    self.refresh_ui_text()
                    # Update content text fields with new language defaults
                    self.update_content_for_language()
                break
    
    def refresh_ui_text(self):
        """Refresh all UI text elements with current language"""
        # Update window title
        self.root.title(self.language_manager.get_ui_text("window_title", "PoE Leveling Planner - Configuration"))
        
        # Update button text
        self.minimize_btn.config(text=self.language_manager.get_ui_text("hide_config_window" if not self.config_hidden else "show_config_window", "Hide Config Window"))
        
        # Note: For a complete refresh, we would need to recreate the entire UI
        # For now, we'll just update the critical elements that can be changed
        # A full implementation would store references to all labels and update them
        
    def update_content_for_language(self):
        """Update content text fields with language-appropriate defaults"""
        # Get the default content for the current language
        default_text = self.language_manager.get_content("default_text", "PoE Leveling Planner\nReady to assist!")
        alternate_text = self.language_manager.get_content("alternate_text", "Hotkey Activated!\nCtrl+2 to return")
        
        # Update the text widgets with new language defaults
        self.default_text_widget.delete(1.0, tk.END)
        self.default_text_widget.insert(1.0, default_text)
        
        self.alternate_text_widget.delete(1.0, tk.END)
        self.alternate_text_widget.insert(1.0, alternate_text)
    
    def run(self):
        """Start the configuration GUI"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = ConfigGUI()
        app.run()
    except Exception as e:
        print(f"Error starting configuration GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 