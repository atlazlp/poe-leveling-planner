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
from data_manager import DataManager
import threading


class ConfigGUI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager(self.config_manager)
        self.data_manager = DataManager()
        self.root = tk.Tk()
        self.test_window = None  # For live testing
        self.debounce_timer = None  # For debouncing slider updates
        self.data_loading = False  # Track if data is being loaded
        
        # Don't kill existing overlay processes when config opens
        # Only kill them when explicitly restarting
        
        self.setup_window()
        self.setup_ui()
        self.load_current_settings()
        self.start_live_testing()
        
        # Initialize data in background
        self.initialize_data()
        
    def initialize_data(self):
        """Initialize data in background thread"""
        def update_data():
            try:
                self.data_loading = True
                self.update_gem_info_loading()
                self.update_vendor_info_loading()
                
                # Update data for current language
                current_lang = self.language_manager.get_current_language()
                success = self.data_manager.check_and_update_data(current_lang)
                
                if success:
                    # Update UI on main thread
                    self.root.after(0, self.refresh_gem_info)
                    self.root.after(0, self.refresh_vendor_info)
                else:
                    self.root.after(0, lambda: self.update_gem_info_error("Failed to load data"))
                    self.root.after(0, lambda: self.update_vendor_info_error("Failed to load data"))
                    
            except Exception as e:
                print(f"Error initializing data: {e}")
                self.root.after(0, lambda: self.update_gem_info_error(f"Error: {e}"))
                self.root.after(0, lambda: self.update_vendor_info_error(f"Error: {e}"))
            finally:
                self.data_loading = False
        
        # Start background thread
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
        
    def setup_window(self):
        """Setup the main configuration window"""
        self.root.title(self.language_manager.get_ui_text("window_title", "PoE Leveling Planner - Configuration"))
        self.root.geometry("600x800")  # Increased width and height for gem info
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"600x800+{x}+{y}")
        
        # Make it stay on top initially
        self.root.attributes('-topmost', True)
        self.root.after(1000, lambda: self.root.attributes('-topmost', False))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Create the UI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text=self.language_manager.get_ui_text("main_title", "PoE Leveling Planner Configuration"), 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Create tabs
        self.setup_general_tab()
        self.setup_appearance_tab()
        self.setup_gems_tab()
        
        # Preview Section (outside tabs)
        preview_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_ui_text("live_preview", "Live Preview"), padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.preview_label = ttk.Label(preview_frame, text="Position: (0, 0)\nMonitor: Primary", 
                                      font=('Arial', 9))
        self.preview_label.grid(row=0, column=0, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Save and Cancel buttons (always visible)
        ttk.Button(button_frame, text=self.language_manager.get_ui_text("save_restart", "Save & Restart"), command=self.save_and_restart).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=self.language_manager.get_ui_text("cancel", "Cancel"), command=self.cancel).pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset to Default button (will be shown/hidden based on tab)
        self.reset_btn = ttk.Button(button_frame, text=self.language_manager.get_ui_text("reset_to_default", "Reset to Default"), command=self.reset_defaults)
        
        # Bind tab change event to show/hide reset button
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def setup_general_tab(self):
        """Setup the General tab"""
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="General")
        
        row = 0
        
        # Language Selection Section
        language_frame = ttk.LabelFrame(general_frame, text=self.language_manager.get_ui_text("language_settings", "Language Settings"), padding="10")
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
        
        # Hotkeys Section - Updated for quest navigation
        hotkey_frame = ttk.LabelFrame(general_frame, text=self.language_manager.get_ui_text("hotkeys", "Hotkeys"), padding="10")
        hotkey_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(hotkey_frame, text="Previous Quest:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.previous_quest_var = tk.StringVar()
        previous_combo = ttk.Combobox(hotkey_frame, textvariable=self.previous_quest_var,
                                   values=["ctrl+1", "ctrl+x", "ctrl+t", "alt+x", "alt+t", "shift+x"],
                                   width=15)
        previous_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(hotkey_frame, text="Next Quest:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.next_quest_var = tk.StringVar()
        next_combo = ttk.Combobox(hotkey_frame, textvariable=self.next_quest_var,
                                  values=["ctrl+2", "ctrl+z", "ctrl+r", "alt+z", "alt+r", "shift+z"],
                                  width=15)
        next_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(hotkey_frame, text="Copy Regex:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.copy_regex_var = tk.StringVar()
        copy_regex_combo = ttk.Combobox(hotkey_frame, textvariable=self.copy_regex_var,
                                       values=["ctrl+3", "ctrl+c", "ctrl+v", "alt+c", "alt+v", "shift+c"],
                                       width=15)
        copy_regex_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Regex Management Section
        regex_frame = ttk.LabelFrame(general_frame, text="Regex Management", padding="10")
        regex_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # Add regex button and status
        regex_button_frame = ttk.Frame(regex_frame)
        regex_button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.add_regex_btn = ttk.Button(regex_button_frame, text="Add Regex", command=self.add_regex)
        self.add_regex_btn.pack(side=tk.LEFT)
        
        self.regex_status_label = ttk.Label(regex_button_frame, text="", foreground='gray')
        self.regex_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Regex list frame
        self.regex_list_frame = ttk.Frame(regex_frame)
        self.regex_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        regex_frame.columnconfigure(0, weight=1)
        regex_frame.rowconfigure(1, weight=1)
        
        general_frame.columnconfigure(0, weight=1)
        
    def setup_appearance_tab(self):
        """Setup the Appearance tab"""
        appearance_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(appearance_frame, text="Appearance")
        
        row = 0
        
        # Monitor Selection Section
        monitor_frame = ttk.LabelFrame(appearance_frame, text=self.language_manager.get_ui_text("monitor_settings", "Monitor Settings"), padding="10")
        monitor_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(monitor_frame, text=self.language_manager.get_ui_text("monitor", "Monitor:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.monitor_var = tk.StringVar()
        self.monitor_combo = ttk.Combobox(monitor_frame, textvariable=self.monitor_var, 
                                         state="readonly", width=30)
        self.monitor_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Position is always center - no UI control needed
        
        monitor_frame.columnconfigure(1, weight=1)
        
        # Position Offset Section
        offset_frame = ttk.LabelFrame(appearance_frame, text=self.language_manager.get_ui_text("position_offset", "Position Offset"), padding="10")
        offset_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # X Offset
        ttk.Label(offset_frame, text=self.language_manager.get_ui_text("x_offset", "X Offset:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_offset_var = tk.IntVar()
        x_offset_scale = tk.Scale(offset_frame, from_=-3000, to=3000, variable=self.x_offset_var,
                                  orient=tk.HORIZONTAL, length=200, resolution=1)
        x_offset_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.x_offset_entry = ttk.Entry(offset_frame, textvariable=self.x_offset_var, width=8)
        self.x_offset_entry.grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Y Offset
        ttk.Label(offset_frame, text=self.language_manager.get_ui_text("y_offset", "Y Offset:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_offset_var = tk.IntVar()
        y_offset_scale = tk.Scale(offset_frame, from_=-3000, to=3000, variable=self.y_offset_var,
                                  orient=tk.HORIZONTAL, length=200, resolution=1)
        y_offset_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.y_offset_entry = ttk.Entry(offset_frame, textvariable=self.y_offset_var, width=8)
        self.y_offset_entry.grid(row=1, column=2, padx=(10, 0), pady=2)
        
        offset_frame.columnconfigure(1, weight=1)
        
        # Appearance Settings Section
        settings_frame = ttk.LabelFrame(appearance_frame, text=self.language_manager.get_ui_text("appearance", "Appearance"), padding="10")
        settings_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        ttk.Label(settings_frame, text=self.language_manager.get_ui_text("opacity", "Opacity:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.opacity_var = tk.DoubleVar()
        opacity_scale = tk.Scale(settings_frame, from_=0.1, to=1.0, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, length=200, resolution=0.1)
        opacity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.opacity_label = ttk.Label(settings_frame, text="0.8")
        self.opacity_label.grid(row=0, column=2, padx=(10, 0), pady=2)
        
        ttk.Label(settings_frame, text=self.language_manager.get_ui_text("width", "Width:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.IntVar()
        width_spin = ttk.Spinbox(settings_frame, from_=100, to=800, textvariable=self.width_var, width=10)
        width_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(settings_frame, text=self.language_manager.get_ui_text("height", "Height:")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.height_var = tk.IntVar()
        height_spin = ttk.Spinbox(settings_frame, from_=50, to=400, textvariable=self.height_var, width=10)
        height_spin.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
        appearance_frame.columnconfigure(0, weight=1)
        
        # Update preview when settings change - with debouncing for sliders
        self.monitor_var.trace('w', self.update_live_preview)
        
        # Add debounced updates for sliders to prevent lag
        for var in [self.x_offset_var, self.y_offset_var, self.width_var, self.height_var, self.opacity_var]:
            var.trace('w', self.debounced_update)
            
        # Update labels when scales change
        def update_x_offset_label(*args):
            pass  # Entry widget automatically updates with IntVar
        def update_y_offset_label(*args):
            pass  # Entry widget automatically updates with IntVar
        def update_opacity_label(*args):
            self.opacity_label.config(text=f"{self.opacity_var.get():.1f}")
        
        # Add validation for offset entries
        def validate_offset_entry(value, min_val=-3000, max_val=3000):
            if value == "" or value == "-":
                return True  # Allow empty or just minus sign during typing
            try:
                val = int(value)
                return min_val <= val <= max_val
            except ValueError:
                return False
        
        # Register validation functions
        vcmd = (self.root.register(validate_offset_entry), '%P')
        self.x_offset_entry.config(validate='key', validatecommand=vcmd)
        self.y_offset_entry.config(validate='key', validatecommand=vcmd)
        
        # Update opacity label when scale changes
        self.opacity_var.trace('w', update_opacity_label)
            
    def setup_gems_tab(self):
        """Setup the Gems tab with character management and sub-tabs for quests and vendors"""
        gems_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(gems_frame, text="Gems")
        
        # Character Management Section
        char_frame = ttk.LabelFrame(gems_frame, text="Character Management", padding="10")
        char_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Character selection
        ttk.Label(char_frame, text="Selected Character:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.selected_char_var = tk.StringVar()
        self.char_combo = ttk.Combobox(char_frame, textvariable=self.selected_char_var, 
                                      state="readonly", width=25)
        self.char_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.char_combo.bind('<<ComboboxSelected>>', self.on_character_select)
        
        # Delete character button
        self.delete_char_btn = ttk.Button(char_frame, text="Delete Character", 
                                         command=self.delete_character)
        self.delete_char_btn.grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # New character section
        new_char_frame = ttk.LabelFrame(char_frame, text="Create New Character", padding="5")
        new_char_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(new_char_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.new_char_name_var = tk.StringVar()
        self.new_char_name_entry = ttk.Entry(new_char_frame, textvariable=self.new_char_name_var, width=20)
        self.new_char_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(new_char_frame, text="Class:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.new_char_class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(new_char_frame, textvariable=self.new_char_class_var,
                                       values=["Marauder", "Templar", "Duelist", "Shadow", "Witch", "Ranger", "Scion"],
                                       state="readonly", width=15)
        self.class_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        self.create_char_btn = ttk.Button(new_char_frame, text="Create Character", 
                                         command=self.create_character)
        self.create_char_btn.grid(row=0, column=4, padx=(10, 0), pady=2)
        
        new_char_frame.columnconfigure(1, weight=1)
        new_char_frame.columnconfigure(3, weight=1)
        
        # Character info display
        info_frame = ttk.LabelFrame(gems_frame, text="Character Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.char_info_label = ttk.Label(info_frame, text="No character selected", 
                                        font=('Arial', 10))
        self.char_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Create sub-tabs for Quests and Vendors
        self.gems_notebook = ttk.Notebook(gems_frame)
        self.gems_notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup Quests tab
        self.setup_quests_subtab()
        
        # Setup Vendors tab
        self.setup_vendors_subtab()
        
        char_frame.columnconfigure(1, weight=1)
        gems_frame.columnconfigure(0, weight=1)
        gems_frame.rowconfigure(2, weight=1)
        
        # Load character data
        self.load_character_data()
    
    def setup_quests_subtab(self):
        """Setup the Quests sub-tab"""
        quests_frame = ttk.Frame(self.gems_notebook, padding="10")
        self.gems_notebook.add(quests_frame, text="Quests")
        
        # Quest rewards section
        quest_frame = ttk.LabelFrame(quests_frame, text="Quest Gem Rewards", padding="10")
        quest_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create simple frame for quest rewards
        self.quest_scrollable_frame = ttk.Frame(quest_frame)
        self.quest_scrollable_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial gem info label
        self.quest_gem_info_label = ttk.Label(self.quest_scrollable_frame, 
                                             text="Loading quest reward data...", 
                                             font=('Arial', 10), foreground='gray')
        self.quest_gem_info_label.grid(row=0, column=0, pady=20)
        
        # Refresh button
        refresh_frame = ttk.Frame(quest_frame)
        refresh_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.refresh_quest_btn = ttk.Button(refresh_frame, text="Refresh Quest Data", 
                                           command=self.refresh_quest_data)
        self.refresh_quest_btn.pack(side=tk.LEFT)
        
        quest_frame.columnconfigure(0, weight=1)
        quest_frame.rowconfigure(0, weight=1)
        quests_frame.columnconfigure(0, weight=1)
        quests_frame.rowconfigure(0, weight=1)
    
    def setup_vendors_subtab(self):
        """Setup the Vendors sub-tab"""
        vendors_frame = ttk.Frame(self.gems_notebook, padding="10")
        self.gems_notebook.add(vendors_frame, text="Vendors")
        
        # Vendor rewards section
        vendor_frame = ttk.LabelFrame(vendors_frame, text="Vendor Gem Rewards", padding="10")
        vendor_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create simple frame for vendor rewards
        self.vendor_scrollable_frame = ttk.Frame(vendor_frame)
        self.vendor_scrollable_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial vendor info label
        self.vendor_gem_info_label = ttk.Label(self.vendor_scrollable_frame, 
                                              text="Loading vendor reward data...", 
                                              font=('Arial', 10), foreground='gray')
        self.vendor_gem_info_label.grid(row=0, column=0, pady=20)
        
        # Refresh button
        refresh_frame = ttk.Frame(vendor_frame)
        refresh_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.refresh_vendor_btn = ttk.Button(refresh_frame, text="Refresh Vendor Data", 
                                            command=self.refresh_vendor_data)
        self.refresh_vendor_btn.pack(side=tk.LEFT)
        
        vendor_frame.columnconfigure(0, weight=1)
        vendor_frame.rowconfigure(0, weight=1)
        vendors_frame.columnconfigure(0, weight=1)
        vendors_frame.rowconfigure(0, weight=1)
    
    def load_character_data(self):
        """Load character data from config and populate the UI"""
        try:
            characters = self.config_manager.get_setting("characters", "profiles", [])
            selected_char = self.config_manager.get_setting("characters", "selected", "")
            
            # Update character combo box
            char_names = [char["name"] for char in characters]
            self.char_combo['values'] = char_names
            
            if selected_char and selected_char in char_names:
                self.selected_char_var.set(selected_char)
                self.update_character_info(selected_char)
            elif char_names:
                # Select first character if no valid selection
                self.selected_char_var.set(char_names[0])
                self.update_character_info(char_names[0])
                self.config_manager.update_setting("characters", "selected", char_names[0])
            else:
                self.selected_char_var.set("")
                self.update_character_info("")
                
            # Enable/disable delete button
            self.delete_char_btn.config(state="normal" if char_names else "disabled")
            
        except Exception as e:
            print(f"Error loading character data: {e}")
            self.char_combo['values'] = []
            self.selected_char_var.set("")
            self.update_character_info("")
            self.delete_char_btn.config(state="disabled")
    
    def create_character(self):
        """Create a new character"""
        name = self.new_char_name_var.get().strip()
        char_class = self.new_char_class_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a character name.")
            return
            
        if not char_class:
            messagebox.showerror("Error", "Please select a character class.")
            return
        
        # Check if character name already exists
        characters = self.config_manager.get_setting("characters", "profiles", [])
        if any(char["name"] == name for char in characters):
            messagebox.showerror("Error", f"A character named '{name}' already exists.")
            return
        
        # Create new character
        new_character = {
            "name": name,
            "class": char_class,
            "gem_selections": {},
            "vendor_gem_selections": {},
            "regex_patterns": []
        }
        
        characters.append(new_character)
        self.config_manager.update_setting("characters", "profiles", characters)
        self.config_manager.update_setting("characters", "selected", name)
        
        # Clear input fields
        self.new_char_name_var.set("")
        self.new_char_class_var.set("")
        
        # Reload character data and select the new character
        self.load_character_data()
        
        # Ensure the new character is selected in the combobox
        self.selected_char_var.set(name)
        
        # Update character info and gem displays
        self.update_character_info(name)
        self.refresh_gem_info()
        self.refresh_vendor_info()
        
        # Update regex management
        self.update_regex_button_state()
        self.refresh_regex_list()
        
        messagebox.showinfo("Success", f"Character '{name}' ({char_class}) created and selected successfully!")
    
    def delete_character(self):
        """Delete the selected character"""
        selected_name = self.selected_char_var.get()
        if not selected_name:
            return
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete character '{selected_name}'?"):
            characters = self.config_manager.get_setting("characters", "profiles", [])
            characters = [char for char in characters if char["name"] != selected_name]
            
            self.config_manager.update_setting("characters", "profiles", characters)
            
            # Update selected character
            if characters:
                new_selected = characters[0]["name"]
                self.config_manager.update_setting("characters", "selected", new_selected)
            else:
                self.config_manager.update_setting("characters", "selected", "")
            
            # Reload character data
            self.load_character_data()
            
            # Update regex management
            self.update_regex_button_state()
            self.refresh_regex_list()
            
            messagebox.showinfo("Success", f"Character '{selected_name}' deleted successfully!")
    
    def on_character_select(self, event=None):
        """Handle character selection change"""
        selected_name = self.selected_char_var.get()
        if selected_name:
            self.config_manager.update_setting("characters", "selected", selected_name)
            self.update_character_info(selected_name)
            self.refresh_gem_info()
            self.refresh_vendor_info()
            # Update regex management
            self.update_regex_button_state()
            self.refresh_regex_list()
    
    def update_character_info(self, character_name):
        """Update the character information display"""
        if not character_name:
            self.char_info_label.config(text="No character selected")
            self.update_gem_info_placeholder()
            return
            
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == character_name), None)
        
        if character:
            gem_summary = self.get_character_gem_summary(character_name)
            info_text = f"Name: {character['name']}\nClass: {character['class']}\n{gem_summary}"
            self.char_info_label.config(text=info_text)
            
            # Update gem info for this character's class
            self.refresh_gem_info()
        else:
            self.char_info_label.config(text="Character not found")
            self.update_gem_info_placeholder()
    
    def update_gem_info_placeholder(self):
        """Update gem info display with placeholder text"""
        # Clear existing widgets in quest tab
        for widget in self.quest_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.quest_gem_info_label = ttk.Label(self.quest_scrollable_frame, 
                                             text="Select a character to view quest gem rewards", 
                                             font=('Arial', 10), foreground='gray')
        self.quest_gem_info_label.grid(row=0, column=0, pady=20)
        
        # Clear existing widgets in vendor tab
        for widget in self.vendor_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.vendor_gem_info_label = ttk.Label(self.vendor_scrollable_frame, 
                                              text="Select a character to view vendor gem rewards", 
                                              font=('Arial', 10), foreground='gray')
        self.vendor_gem_info_label.grid(row=0, column=0, pady=20)
    
    def update_gem_info_loading(self):
        """Update gem info display with loading text"""
        # Clear existing widgets in quest tab
        for widget in self.quest_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.quest_gem_info_label = ttk.Label(self.quest_scrollable_frame, 
                                             text="Loading quest reward data...", 
                                             font=('Arial', 10), foreground='gray')
        self.quest_gem_info_label.grid(row=0, column=0, pady=20)
    
    def update_vendor_info_loading(self):
        """Update vendor info display with loading text"""
        # Clear existing widgets in vendor tab
        for widget in self.vendor_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.vendor_gem_info_label = ttk.Label(self.vendor_scrollable_frame, 
                                              text="Loading vendor reward data...", 
                                              font=('Arial', 10), foreground='gray')
        self.vendor_gem_info_label.grid(row=0, column=0, pady=20)
    
    def update_gem_info_error(self, error_message):
        """Update gem info display with error message"""
        # Clear existing widgets in quest tab
        for widget in self.quest_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.quest_gem_info_label = ttk.Label(self.quest_scrollable_frame, 
                                             text=f"Error loading quest data:\n{error_message}", 
                                             font=('Arial', 10), foreground='red')
        self.quest_gem_info_label.grid(row=0, column=0, pady=20)
    
    def update_vendor_info_error(self, error_message):
        """Update vendor info display with error message"""
        # Clear existing widgets in vendor tab
        for widget in self.vendor_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.vendor_gem_info_label = ttk.Label(self.vendor_scrollable_frame, 
                                              text=f"Error loading vendor data:\n{error_message}", 
                                              font=('Arial', 10), foreground='red')
        self.vendor_gem_info_label.grid(row=0, column=0, pady=20)
    
    def refresh_gem_info(self):
        """Refresh the quest gem information display based on selected character"""
        selected_name = self.selected_char_var.get()
        if not selected_name:
            self.update_gem_info_placeholder()
            return
        
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == selected_name), None)
        
        if not character:
            self.update_gem_info_placeholder()
            return
        
        character_class = character['class']
        current_language = self.language_manager.get_current_language()
        
        # Get quest rewards for this character class
        quest_rewards = self.data_manager.get_quest_rewards_for_class(current_language, character_class)
        
        # Preserve horizontal scroll position if canvas exists
        scroll_position = None
        for widget in self.quest_scrollable_frame.winfo_children():
            if isinstance(widget, tk.Canvas) and hasattr(widget, 'xview'):
                scroll_position = widget.xview()
                break
        
        # Clear existing widgets
        for widget in self.quest_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not quest_rewards:
            self.quest_gem_info_label = ttk.Label(self.quest_scrollable_frame, 
                                                 text=f"No quest reward data available for {character_class}.\nTry refreshing the quest data.", 
                                                 font=('Arial', 10), foreground='orange')
            self.quest_gem_info_label.grid(row=0, column=0, pady=20)
            return
        
        # Get overlay width for card sizing
        overlay_width = self.config_manager.get_setting("appearance", "width", 250)
        card_width = max(200, min(overlay_width, 250))  # Cap at 250px, minimum 200px
        
        # Get or initialize gem selections for this character
        if 'gem_selections' not in character:
            character['gem_selections'] = {}
        
        # Create horizontal scrollable container
        horizontal_canvas = tk.Canvas(self.quest_scrollable_frame, height=400)  # Increased height for more gems
        horizontal_scrollbar = ttk.Scrollbar(self.quest_scrollable_frame, orient="horizontal", command=horizontal_canvas.xview)
        cards_frame = ttk.Frame(horizontal_canvas)
        
        cards_frame.bind(
            "<Configure>",
            lambda e: horizontal_canvas.configure(scrollregion=horizontal_canvas.bbox("all"))
        )
        
        horizontal_canvas.create_window((0, 0), window=cards_frame, anchor="nw")
        horizontal_canvas.configure(xscrollcommand=horizontal_scrollbar.set)
        
        # Pack the horizontal scroll components to use full width
        horizontal_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        horizontal_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Display quest rewards as cards in a single horizontal row
        for quest_idx, quest in enumerate(quest_rewards):
            # Get gem rewards for this class first (needed for height calculation)
            gems = quest.get('class_rewards', [])
            
            # Create quest card frame with border
            quest_card = ttk.LabelFrame(cards_frame, text="", padding="10", relief="raised", borderwidth=2)
            quest_card.grid(row=0, column=quest_idx, sticky=(tk.W, tk.E, tk.N, tk.S), 
                           padx=(0 if quest_idx == 0 else 10, 0), pady=0)
            
            # Set fixed width but allow height to be dynamic based on content
            quest_card.grid_propagate(False)
            
            # Calculate dynamic height based on number of gems (more compact)
            base_height = 80   # Reduced height for title and padding
            gem_height = 28    # Reduced height per gem button (including padding)
            min_height = 160   # Reduced minimum height
            max_height = 350   # Maximum height before we need vertical scroll
            calculated_height = min(max_height, max(min_height, base_height + (len(gems) * gem_height)))
            
            quest_card.configure(width=card_width, height=calculated_height)
            
            # Quest title and act
            title_frame = ttk.Frame(quest_card)
            title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            quest_title = ttk.Label(title_frame, text=quest['name'], 
                                   font=('Arial', 12, 'bold'), anchor='center')
            quest_title.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            quest_act = ttk.Label(title_frame, text=quest['act'], 
                                 font=('Arial', 10), foreground='#666666', anchor='center')
            quest_act.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            title_frame.columnconfigure(0, weight=1)
            
            # Gem rewards for this class
            if gems:
                # Check if we need vertical scrolling
                needs_scroll = calculated_height >= max_height and len(gems) > 8
                
                if needs_scroll:
                    # Create scrollable frame for gems when there are many
                    gems_canvas = tk.Canvas(quest_card, height=max_height-base_height)
                    gems_scrollbar = ttk.Scrollbar(quest_card, orient="vertical", command=gems_canvas.yview)
                    gems_scrollable_frame = ttk.Frame(gems_canvas)
                    
                    gems_scrollable_frame.bind(
                        "<Configure>",
                        lambda e: gems_canvas.configure(scrollregion=gems_canvas.bbox("all"))
                    )
                    
                    gems_canvas.create_window((0, 0), window=gems_scrollable_frame, anchor="nw")
                    gems_canvas.configure(yscrollcommand=gems_scrollbar.set)
                    
                    gems_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                    gems_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
                    
                    gems_frame = gems_scrollable_frame
                else:
                    # Create simple frame for gems when scrolling is not needed
                    gems_container = ttk.Frame(quest_card)
                    gems_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                    
                    gems_frame = ttk.Frame(gems_container)
                    gems_frame.pack(expand=True, fill='both')
                
                quest_key = f"{quest['name']}_{quest['act']}"
                selected_gem = character['gem_selections'].get(quest_key, None)
                
                for gem_idx, gem in enumerate(gems):
                    # Create clickable gem button
                    gem_color = gem['color']
                    if gem_color == 'gem_red':
                        color = '#ff6b6b'  # Red
                        bg_color = '#ffebee'  # Light red background
                    elif gem_color == 'gem_green':
                        color = '#51cf66'  # Green
                        bg_color = '#e8f5e8'  # Light green background
                    elif gem_color == 'gem_blue':
                        color = '#339af0'  # Blue
                        bg_color = '#e3f2fd'  # Light blue background
                    else:
                        color = '#868e96'  # Gray fallback
                        bg_color = '#f5f5f5'  # Light gray background
                    
                    # Determine if this gem is selected or grayed out
                    is_selected = selected_gem == gem['name']
                    is_grayed_out = selected_gem is not None and not is_selected
                    
                    if is_grayed_out:
                        display_color = '#cccccc'
                        display_bg = '#f0f0f0'
                        relief = 'flat'
                        border_width = 1
                    elif is_selected:
                        display_color = color
                        display_bg = bg_color
                        relief = 'solid'
                        border_width = 3
                    else:
                        display_color = color
                        display_bg = self.root.cget('bg')
                        relief = 'raised'
                        border_width = 1
                    
                    def make_gem_click_handler(gem_data, quest_key_data, character_data):
                        return lambda: self.on_gem_click(gem_data, quest_key_data, character_data)
                    
                    gem_button = tk.Button(gems_frame, text=gem['name'], 
                                         font=('Arial', 9, 'bold' if is_selected else 'normal'), 
                                         fg=display_color,
                                         bg=display_bg,
                                         activebackground=bg_color if not is_grayed_out else display_bg,
                                         relief=relief,
                                         borderwidth=border_width,
                                         cursor='hand2',
                                         wraplength=card_width-40,  # Wrap text if too long
                                         justify='center',
                                         padx=3,
                                         pady=2,
                                         command=make_gem_click_handler(gem, quest_key, character))
                    gem_button.pack(fill='x', pady=1, padx=3)
                
            else:
                no_gems_label = ttk.Label(quest_card, 
                                        text="No gems available", 
                                        font=('Arial', 10, 'italic'), foreground='#999999',
                                        anchor='center')
                no_gems_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=20)
            
            quest_card.columnconfigure(0, weight=1)
            quest_card.rowconfigure(1, weight=1)
        
        # Configure grid weights for the scrollable frame
        self.quest_scrollable_frame.columnconfigure(0, weight=1)
        self.quest_scrollable_frame.rowconfigure(0, weight=1)
        
        # Update scroll region
        self.quest_scrollable_frame.update_idletasks()
        
        # Restore horizontal scroll position if it was preserved
        if scroll_position is not None:
            # Find the horizontal canvas and restore its position
            for widget in self.quest_scrollable_frame.winfo_children():
                if isinstance(widget, tk.Canvas) and hasattr(widget, 'xview_moveto'):
                    # Use a small delay to ensure the canvas is fully rendered
                    # Add error handling to prevent TclError if widget is destroyed
                    def safe_restore_scroll():
                        try:
                            if widget.winfo_exists():
                                widget.xview_moveto(scroll_position[0])
                        except tk.TclError:
                            pass  # Widget was destroyed, ignore
                    
                    self.root.after(10, safe_restore_scroll)
                    break
    
    def refresh_vendor_info(self):
        """Refresh the vendor gem information display based on selected character"""
        selected_name = self.selected_char_var.get()
        if not selected_name:
            return
        
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == selected_name), None)
        
        if not character:
            return
        
        character_class = character['class']
        current_language = self.language_manager.get_current_language()
        
        # Get vendor rewards for this character class
        vendor_rewards = self.data_manager.get_vendor_rewards_for_class(current_language, character_class)
        
        # Clear existing widgets
        for widget in self.vendor_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not vendor_rewards:
            self.vendor_gem_info_label = ttk.Label(self.vendor_scrollable_frame, 
                                                  text=f"No vendor reward data available for {character_class}.\nTry refreshing the vendor data.", 
                                                  font=('Arial', 10), foreground='orange')
            self.vendor_gem_info_label.grid(row=0, column=0, pady=20)
            return
        
        # Get or initialize vendor gem selections for this character
        if 'vendor_gem_selections' not in character:
            character['vendor_gem_selections'] = {}
        
        # Create vertical scrollable container
        canvas = tk.Canvas(self.vendor_scrollable_frame)
        scrollbar = ttk.Scrollbar(self.vendor_scrollable_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scroll components
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Display vendor rewards as full-width rows
        for vendor_idx, vendor_quest in enumerate(vendor_rewards):
            gems = vendor_quest.get('class_rewards', [])
            
            # Create vendor row frame - use full width
            vendor_row = ttk.LabelFrame(scrollable_frame, text=f"{vendor_quest['name']} ({vendor_quest['act']})", 
                                       padding="10", relief="raised", borderwidth=1)
            vendor_row.grid(row=vendor_idx, column=0, sticky=(tk.W, tk.E), pady=(0 if vendor_idx == 0 else 10, 0))
            
            if gems:
                vendor_key = f"{vendor_quest['name']}_{vendor_quest['act']}"
                selected_gems = character['vendor_gem_selections'].get(vendor_key, [])
                
                # Ensure selected_gems is a list (handle old single selection format)
                if not isinstance(selected_gems, list):
                    selected_gems = [selected_gems] if selected_gems else []
                
                # Create gems grid with 4 columns
                gems_per_row = 4
                for gem_idx, gem in enumerate(gems):
                    row = gem_idx // gems_per_row
                    col = gem_idx % gems_per_row
                    
                    # Create clickable gem button
                    gem_color = gem['color']
                    if gem_color == 'gem_red':
                        color = '#ff6b6b'  # Red
                        bg_color = '#ffebee'  # Light red background
                    elif gem_color == 'gem_green':
                        color = '#51cf66'  # Green
                        bg_color = '#e8f5e8'  # Light green background
                    elif gem_color == 'gem_blue':
                        color = '#339af0'  # Blue
                        bg_color = '#e3f2fd'  # Light blue background
                    else:
                        color = '#868e96'  # Gray fallback
                        bg_color = '#f5f5f5'  # Light gray background
                    
                    # Determine if this gem is selected (multiple selections allowed)
                    is_selected = gem['name'] in selected_gems
                    
                    if is_selected:
                        display_color = color
                        display_bg = bg_color
                        relief = 'solid'
                        border_width = 3
                    else:
                        display_color = color
                        display_bg = self.root.cget('bg')
                        relief = 'raised'
                        border_width = 1
                    
                    def make_vendor_gem_click_handler(gem_data, vendor_key_data, character_data):
                        return lambda: self.on_vendor_gem_click(gem_data, vendor_key_data, character_data)
                    
                    gem_button = tk.Button(vendor_row, text=gem['name'], 
                                         font=('Arial', 9, 'bold' if is_selected else 'normal'), 
                                         fg=display_color,
                                         bg=display_bg,
                                         activebackground=bg_color,
                                         relief=relief,
                                         borderwidth=border_width,
                                         cursor='hand2',
                                         wraplength=120,  # Wrap text for better fit in grid
                                         justify='center',
                                         padx=5,
                                         pady=3,
                                         width=15,  # Fixed width for consistent grid
                                         command=make_vendor_gem_click_handler(gem, vendor_key, character))
                    gem_button.grid(row=row, column=col, sticky=(tk.W, tk.E), pady=2, padx=2)
                
                # Configure column weights for even distribution across full width
                for col in range(gems_per_row):
                    vendor_row.columnconfigure(col, weight=1)
                
            else:
                no_gems_label = ttk.Label(vendor_row, 
                                        text="No gems available", 
                                        font=('Arial', 10, 'italic'), foreground='#999999',
                                        anchor='center')
                no_gems_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
                vendor_row.columnconfigure(0, weight=1)
        
        # Configure grid weights for the scrollable frame
        scrollable_frame.columnconfigure(0, weight=1)
        self.vendor_scrollable_frame.columnconfigure(0, weight=1)
        self.vendor_scrollable_frame.rowconfigure(0, weight=1)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Update scroll region
        self.vendor_scrollable_frame.update_idletasks()
    
    def on_gem_click(self, gem, quest_key, character):
        """Handle gem selection for quest rewards"""
        # Toggle gem selection
        if 'gem_selections' not in character:
            character['gem_selections'] = {}
        
        current_selection = character['gem_selections'].get(quest_key, None)
        
        if current_selection == gem['name']:
            # Deselect if clicking the same gem
            character['gem_selections'][quest_key] = None
        else:
            # Select the new gem
            character['gem_selections'][quest_key] = gem['name']
        
        # Save character data
        self.save_character_gem_selections(character)
        
        # Refresh the display
        self.refresh_gem_info()
        
        # Update character info
        self.update_character_info(character['name'])
    
    def on_vendor_gem_click(self, gem, vendor_key, character):
        """Handle gem selection for vendor rewards - allows multiple selections"""
        # Initialize vendor gem selections as lists for multiple selections
        if 'vendor_gem_selections' not in character:
            character['vendor_gem_selections'] = {}
        
        # Get current selections for this vendor (as a list)
        current_selections = character['vendor_gem_selections'].get(vendor_key, [])
        if not isinstance(current_selections, list):
            # Convert old single selection format to list format
            current_selections = [current_selections] if current_selections else []
        
        if gem['name'] in current_selections:
            # Deselect if clicking a selected gem
            current_selections.remove(gem['name'])
        else:
            # Add the new gem to selections
            current_selections.append(gem['name'])
        
        # Update the selections (remove empty lists to keep data clean)
        if current_selections:
            character['vendor_gem_selections'][vendor_key] = current_selections
        else:
            character['vendor_gem_selections'][vendor_key] = []
        
        # Save character data
        self.save_character_gem_selections(character)
        
        # Refresh the display
        self.refresh_vendor_info()
        
        # Update character info
        self.update_character_info(character['name'])
    
    def save_character_gem_selections(self, character):
        """Save character gem selections to config"""
        try:
            characters = self.config_manager.get_setting("characters", "profiles", [])
            for i, char in enumerate(characters):
                if char["name"] == character["name"]:
                    characters[i] = character
                    break
            
            self.config_manager.update_setting("characters", "profiles", characters)
            
            # Force save to file
            self.config_manager.save_config()
            
            print(f"Saved gem selections for character: {character['name']}")
            
        except Exception as e:
            print(f"Error saving gem selections: {e}")
    
    def get_character_gem_summary(self, character_name):
        """Get a summary of selected gems for a character"""
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == character_name), None)
        
        if not character:
            return "No character data found"
        
        quest_selections = character.get('gem_selections', {})
        vendor_selections = character.get('vendor_gem_selections', {})
        
        quest_count = len([v for v in quest_selections.values() if v is not None])
        
        # Count vendor gems (handle both old single selection and new list format)
        vendor_count = 0
        for vendor_key, selections in vendor_selections.items():
            if isinstance(selections, list):
                vendor_count += len([gem for gem in selections if gem])
            elif selections:  # Old single selection format
                vendor_count += 1
        
        total_count = quest_count + vendor_count
        
        if total_count == 0:
            return "No gems selected"
        
        summary_parts = []
        if quest_count > 0:
            summary_parts.append(f"{quest_count} quest gems")
        if vendor_count > 0:
            summary_parts.append(f"{vendor_count} vendor gems")
        
        return f"Selected: {', '.join(summary_parts)} ({total_count} total)"
    
    def refresh_quest_data(self):
        """Refresh quest data from PoEDB"""
        if self.data_loading:
            messagebox.showinfo("Info", "Data is already being updated. Please wait.")
            return
        
        def update_data():
            try:
                self.data_loading = True
                self.root.after(0, self.update_gem_info_loading)
                self.root.after(0, self.update_vendor_info_loading)
                
                current_language = self.language_manager.get_current_language()
                success = self.data_manager.force_update_all(current_language)
                
                if success:
                    self.root.after(0, lambda: [
                        self.refresh_gem_info(),
                        self.refresh_vendor_info(),
                        messagebox.showinfo("Success", "Data updated successfully!")
                    ])
                else:
                    self.root.after(0, lambda: [
                        self.update_gem_info_error("Failed to update data"),
                        self.update_vendor_info_error("Failed to update data"),
                        messagebox.showerror("Error", "Failed to update data. Please check your internet connection.")
                    ])
                    
            except Exception as e:
                print(f"Error updating data: {e}")
                self.root.after(0, lambda: [
                    self.update_gem_info_error(f"Error: {e}"),
                    self.update_vendor_info_error(f"Error: {e}"),
                    messagebox.showerror("Error", f"Error updating data: {e}")
                ])
            finally:
                self.data_loading = False
        
        # Start background thread
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
    
    def refresh_vendor_data(self):
        """Refresh vendor data - now uses the same method as quest data"""
        self.refresh_quest_data()  # Both quest and vendor data are updated together now
    
    def on_tab_changed(self, event):
        """Handle tab change to show/hide reset button"""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Appearance":
            self.reset_btn.pack(side=tk.LEFT)
        else:
            self.reset_btn.pack_forget()
    
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
        
        # Load display settings
        self.x_offset_var.set(self.config_manager.get_setting("display", "x_offset", 0))
        self.y_offset_var.set(self.config_manager.get_setting("display", "y_offset", 0))
        self.opacity_var.set(self.config_manager.get_setting("display", "opacity", 0.8))
        
        # Load appearance settings
        self.width_var.set(self.config_manager.get_setting("appearance", "width", 350))
        self.height_var.set(self.config_manager.get_setting("appearance", "height", 250))
        
        # Load color settings if they exist
        if hasattr(self, 'bg_color_var'):
            self.bg_color_var.set(self.config_manager.get_setting("appearance", "background_color", "#2b2b2b"))
        if hasattr(self, 'text_color_var'):
            self.text_color_var.set(self.config_manager.get_setting("appearance", "text_color", "#ffffff"))
        
        # Load font settings if they exist
        if hasattr(self, 'font_family_var'):
            self.font_family_var.set(self.config_manager.get_setting("appearance", "font_family", "Arial"))
        if hasattr(self, 'font_size_var'):
            self.font_size_var.set(self.config_manager.get_setting("appearance", "font_size", 10))
        if hasattr(self, 'font_weight_var'):
            self.font_weight_var.set(self.config_manager.get_setting("appearance", "font_weight", "bold"))
        
        # Load behavior settings if they exist
        if hasattr(self, 'always_on_top_var'):
            self.always_on_top_var.set(self.config_manager.get_setting("display", "always_on_top", True))
        if hasattr(self, 'auto_hide_var'):
            self.auto_hide_var.set(self.config_manager.get_setting("behavior", "auto_hide_when_poe_not_running", False))
        
        # Load hotkey settings
        self.previous_quest_var.set(self.config_manager.get_setting("hotkeys", "previous_quest", "ctrl+1"))
        self.next_quest_var.set(self.config_manager.get_setting("hotkeys", "next_quest", "ctrl+2"))
        self.copy_regex_var.set(self.config_manager.get_setting("hotkeys", "copy_regex", "ctrl+3"))
        
        # Load regex management
        self.load_regex_management()
        
        # Trigger initial live preview update
        self.root.after(100, self.update_live_preview)
    
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
            old_x_offset = self.config_manager.config["display"].get("x_offset", 0)
            old_y_offset = self.config_manager.config["display"].get("y_offset", 0)
            
            self.config_manager.config["display"]["monitor"] = monitor_index
            self.config_manager.config["display"]["x_offset"] = self.x_offset_var.get()
            self.config_manager.config["display"]["y_offset"] = self.y_offset_var.get()
            
            x, y = self.config_manager.calculate_position()
            
            # Restore original values
            self.config_manager.config["display"]["monitor"] = old_monitor
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
                
                label = tk.Label(self.test_window, text="LIVE PREVIEW\nOverlay Position", 
                               bg='red', fg='white', font=('Arial', 8, 'bold'), justify='center')
                label.pack(expand=True)
                
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
    
    def save_and_restart(self):
        """Save configuration and restart the overlay"""
        if self.save_config():
            try:
                # Kill any existing overlay processes
                self.kill_existing_overlay()
                
                # Wait a moment for processes to fully terminate
                import time
                time.sleep(0.5)
                
                # Start new overlay process
                # Check if we're running from a packaged executable
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    # We're running from PyInstaller package
                    # Get the executable path (remove --config flag by running without args)
                    exe_path = sys.executable
                    subprocess.Popen([exe_path], 
                                   cwd=os.path.dirname(os.path.abspath(exe_path)))
                else:
                    # We're running from source
                    subprocess.Popen([sys.executable, "main.py"], 
                                   cwd=os.path.dirname(os.path.abspath(__file__)))
                
                messagebox.showinfo("Success", "Configuration saved and overlay restarted!")
                self.root.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not restart overlay: {e}")
    
    def kill_existing_overlay(self):
        """Kill any existing overlay processes"""
        import os
        import signal
        import psutil
        
        try:
            # Windows-compatible process killing
            current_pid = os.getpid()
            processes_killed = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['pid'] == current_pid:
                        continue  # Don't kill the config process itself
                    
                    if proc.info['cmdline'] and any('main.py' in str(arg) for arg in proc.info['cmdline']):
                        print(f"Terminating overlay process PID: {proc.info['pid']}")
                        proc.terminate()
                        processes_killed += 1
                        
                        # Wait for process to terminate, then force kill if needed
                        try:
                            proc.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            proc.kill()
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            if processes_killed > 0:
                print(f"Terminated {processes_killed} overlay processes")
            else:
                print("No overlay processes found to terminate")
                
        except Exception as e:
            print(f"Note: Could not kill existing overlay processes: {e}")
    
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
            self.config_manager.update_setting("display", "x_offset", self.x_offset_var.get())
            self.config_manager.update_setting("display", "y_offset", self.y_offset_var.get())
            self.config_manager.update_setting("display", "opacity", self.opacity_var.get())
            self.config_manager.update_setting("appearance", "width", self.width_var.get())
            self.config_manager.update_setting("appearance", "height", self.height_var.get())
            self.config_manager.update_setting("language", "current", language_code)
            
            # Update hotkey settings
            self.config_manager.update_setting("hotkeys", "previous_quest", self.previous_quest_var.get())
            self.config_manager.update_setting("hotkeys", "next_quest", self.next_quest_var.get())
            self.config_manager.update_setting("hotkeys", "copy_regex", self.copy_regex_var.get())
            
            # Force save to file
            self.config_manager.save_config()
            print(self.language_manager.get_message("config_saved", "Configuration saved to config.json"))
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"{self.language_manager.get_message('error_saving_config', 'Could not save configuration:')} {e}")
            return False
    
    def cancel(self):
        """Cancel without saving"""
        # Since we no longer kill the overlay when config opens,
        # we don't need to restart it when canceling
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
        self.root.destroy()
    
    def on_language_change(self, event=None):
        """Handle language change"""
        if not hasattr(self, 'language_combo'):
            return
            
        selected_display_name = self.language_var.get()
        
        # Find the language code for the selected display name
        available_languages = self.language_manager.get_available_languages()
        selected_language = None
        for code, display_name in available_languages.items():
            if display_name == selected_display_name:
                selected_language = code
                break
        
        if selected_language and selected_language != self.language_manager.get_current_language():
            # Update language
            if self.language_manager.set_language(selected_language):
                # Update window title
                self.root.title(self.language_manager.get_ui_text("window_title", "PoE Leveling Planner - Configuration"))
                
                # Update data for new language
                self.initialize_data()
                
                messagebox.showinfo(
                    self.language_manager.get_ui_text("language_changed", "Language Changed"),
                    self.language_manager.get_ui_text("language_changed_message", "Language has been changed. Some changes may require a restart to take full effect.")
                )
    
    def load_regex_management(self):
        """Load and display regex management UI"""
        self.update_regex_button_state()
        self.refresh_regex_list()
    
    def update_regex_button_state(self):
        """Update the add regex button state and status label"""
        selected_char = self.selected_char_var.get() if hasattr(self, 'selected_char_var') else ""
        
        if not selected_char:
            self.add_regex_btn.config(state="disabled")
            self.regex_status_label.config(text="Create a character in the Gems section first", foreground='orange')
            return
        
        # Get character's regex list
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == selected_char), None)
        
        if not character:
            self.add_regex_btn.config(state="disabled")
            self.regex_status_label.config(text="Character not found", foreground='red')
            return
        
        regex_list = character.get('regex_patterns', [])
        used_acts = set()
        has_all_acts = False
        
        for regex_item in regex_list:
            if regex_item.get('act') == 'all_acts':
                has_all_acts = True
            else:
                used_acts.add(regex_item.get('act'))
        
        # Check if we can add more regex patterns
        max_regexes = 11  # 10 acts + 1 "all acts"
        can_add = len(regex_list) < max_regexes and not (has_all_acts and len(used_acts) >= 10)
        
        if can_add:
            self.add_regex_btn.config(state="normal")
            remaining = max_regexes - len(regex_list)
            self.regex_status_label.config(text=f"{len(regex_list)}/{max_regexes} regex patterns", foreground='gray')
        else:
            self.add_regex_btn.config(state="disabled")
            self.regex_status_label.config(text="Maximum regex patterns reached (11/11)", foreground='red')
    
    def refresh_regex_list(self):
        """Refresh the regex list display"""
        # Clear existing widgets
        for widget in self.regex_list_frame.winfo_children():
            widget.destroy()
        
        selected_char = self.selected_char_var.get() if hasattr(self, 'selected_char_var') else ""
        if not selected_char:
            return
        
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == selected_char), None)
        
        if not character:
            return
        
        regex_list = character.get('regex_patterns', [])
        
        if not regex_list:
            no_regex_label = ttk.Label(self.regex_list_frame, text="No regex patterns added yet", 
                                      font=('Arial', 10, 'italic'), foreground='gray')
            no_regex_label.grid(row=0, column=0, pady=10)
            return
        
        # Sort regex patterns: "all_acts" first, then by act number
        def sort_key(regex_item):
            act = regex_item.get('act', '')
            if act == 'all_acts':
                return (0, 0)  # First priority
            elif act.startswith('act_'):
                try:
                    act_num = int(act.split('_')[1])
                    return (1, act_num)  # Second priority, sorted by act number
                except (IndexError, ValueError):
                    return (2, 0)  # Unknown acts last
            else:
                return (2, 0)  # Unknown acts last
        
        sorted_regex_list = sorted(regex_list, key=sort_key)
        
        # Create scrollable frame for regex list
        canvas = tk.Canvas(self.regex_list_frame, height=200)
        scrollbar = ttk.Scrollbar(self.regex_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Display regex patterns
        for idx, regex_item in enumerate(sorted_regex_list):
            act = regex_item.get('act', '')
            pattern = regex_item.get('pattern', '')
            
            # Create frame for each regex item
            item_frame = ttk.Frame(scrollable_frame, relief="raised", borderwidth=1, padding="5")
            item_frame.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=2, padx=2)
            
            # Act label
            act_display = "All Acts" if act == 'all_acts' else f"Act {act.split('_')[1]}" if act.startswith('act_') else act
            act_label = ttk.Label(item_frame, text=act_display, font=('Arial', 10, 'bold'))
            act_label.grid(row=0, column=0, sticky=tk.W)
            
            # Pattern text (truncated if too long)
            display_pattern = pattern if len(pattern) <= 50 else pattern[:47] + "..."
            pattern_label = ttk.Label(item_frame, text=display_pattern, font=('Arial', 9), foreground='#666666')
            pattern_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
            
            # Delete button
            def make_delete_handler(regex_idx, char_data):
                return lambda: self.delete_regex(regex_idx, char_data)
            
            delete_btn = ttk.Button(item_frame, text="Delete", 
                                   command=make_delete_handler(idx, character))
            delete_btn.grid(row=0, column=1, rowspan=2, sticky=tk.E, padx=(10, 0))
            
            item_frame.columnconfigure(0, weight=1)
        
        self.regex_list_frame.columnconfigure(0, weight=1)
        self.regex_list_frame.rowconfigure(0, weight=1)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def add_regex(self):
        """Add a new regex pattern"""
        selected_char = self.selected_char_var.get() if hasattr(self, 'selected_char_var') else ""
        if not selected_char:
            return
        
        characters = self.config_manager.get_setting("characters", "profiles", [])
        character = next((char for char in characters if char["name"] == selected_char), None)
        
        if not character:
            return
        
        # Initialize regex_patterns if not exists
        if 'regex_patterns' not in character:
            character['regex_patterns'] = []
        
        regex_list = character['regex_patterns']
        
        # Get available acts
        used_acts = set()
        has_all_acts = False
        
        for regex_item in regex_list:
            if regex_item.get('act') == 'all_acts':
                has_all_acts = True
            else:
                used_acts.add(regex_item.get('act'))
        
        available_acts = []
        if not has_all_acts:
            available_acts.append(('all_acts', 'All Acts'))
        
        for i in range(1, 11):
            act_key = f'act_{i}'
            if act_key not in used_acts:
                available_acts.append((act_key, f'Act {i}'))
        
        if not available_acts:
            messagebox.showwarning("No Acts Available", "All acts have been assigned regex patterns.")
            return
        
        # Create dialog for adding regex
        self.show_add_regex_dialog(character, available_acts)
    
    def show_add_regex_dialog(self, character, available_acts):
        """Show dialog for adding a new regex pattern"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Regex Pattern")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Act selection
        ttk.Label(main_frame, text="Select Act:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        act_var = tk.StringVar()
        act_combo = ttk.Combobox(main_frame, textvariable=act_var, 
                                values=[display for _, display in available_acts], 
                                state="readonly", width=30)
        act_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # Regex pattern input
        ttk.Label(main_frame, text="Regex Pattern:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        pattern_var = tk.StringVar()
        pattern_entry = ttk.Entry(main_frame, textvariable=pattern_var, width=40)
        pattern_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 5))
        
        # Character limit label
        char_count_label = ttk.Label(main_frame, text="0/250 characters", foreground='gray')
        char_count_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        def update_char_count(*args):
            count = len(pattern_var.get())
            char_count_label.config(text=f"{count}/250 characters", 
                                   foreground='red' if count > 250 else 'gray')
        
        pattern_var.trace('w', update_char_count)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        def save_regex():
            act_display = act_var.get()
            pattern = pattern_var.get().strip()
            
            if not act_display:
                messagebox.showerror("Error", "Please select an act.")
                return
            
            if not pattern:
                messagebox.showerror("Error", "Please enter a regex pattern.")
                return
            
            if len(pattern) > 250:
                messagebox.showerror("Error", "Regex pattern must be 250 characters or less.")
                return
            
            # Find the act key
            act_key = None
            for key, display in available_acts:
                if display == act_display:
                    act_key = key
                    break
            
            if not act_key:
                messagebox.showerror("Error", "Invalid act selection.")
                return
            
            # Add regex to character
            regex_item = {
                'act': act_key,
                'pattern': pattern
            }
            
            character['regex_patterns'].append(regex_item)
            
            # Save character data
            self.save_character_data(character)
            
            # Refresh UI
            self.update_regex_button_state()
            self.refresh_regex_list()
            
            dialog.destroy()
            messagebox.showinfo("Success", f"Regex pattern added for {act_display}!")
        
        ttk.Button(button_frame, text="Save", command=save_regex).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        main_frame.columnconfigure(1, weight=1)
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        
        # Focus on pattern entry
        pattern_entry.focus()
    
    def delete_regex(self, regex_idx, character):
        """Delete a regex pattern"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this regex pattern?"):
            if 'regex_patterns' in character and 0 <= regex_idx < len(character['regex_patterns']):
                deleted_item = character['regex_patterns'].pop(regex_idx)
                act_display = "All Acts" if deleted_item.get('act') == 'all_acts' else f"Act {deleted_item.get('act', '').split('_')[1]}" if deleted_item.get('act', '').startswith('act_') else deleted_item.get('act', '')
                
                # Save character data
                self.save_character_data(character)
                
                # Refresh UI
                self.update_regex_button_state()
                self.refresh_regex_list()
                
                messagebox.showinfo("Success", f"Regex pattern for {act_display} deleted!")
    
    def save_character_data(self, character):
        """Save character data to config"""
        try:
            characters = self.config_manager.get_setting("characters", "profiles", [])
            for i, char in enumerate(characters):
                if char["name"] == character["name"]:
                    characters[i] = character
                    break
            
            self.config_manager.update_setting("characters", "profiles", characters)
            self.config_manager.save_config()
            
        except Exception as e:
            print(f"Error saving character data: {e}")
    
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