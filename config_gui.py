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
from quest_reward_crawler import QuestRewardCrawler
import threading


class ConfigGUI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager(self.config_manager)
        self.quest_crawler = QuestRewardCrawler()
        self.root = tk.Tk()
        self.test_window = None  # For live testing
        self.debounce_timer = None  # For debouncing slider updates
        self.drag_start_x = None  # For window dragging
        self.drag_start_y = None  # For window dragging
        self.quest_data_loading = False  # Track if quest data is being loaded
        self.setup_window()
        self.setup_ui()
        self.load_current_settings()
        self.start_live_testing()
        
        # Initialize quest data in background
        self.initialize_quest_data()
        
    def initialize_quest_data(self):
        """Initialize quest data in background thread"""
        def update_quest_data():
            try:
                self.quest_data_loading = True
                self.update_gem_info_loading()
                
                # Update quest data for current language
                current_lang = self.language_manager.get_current_language()
                success = self.quest_crawler.update_quest_data(current_lang)
                
                if success:
                    # Update UI on main thread
                    self.root.after(0, self.refresh_gem_info)
                else:
                    self.root.after(0, lambda: self.update_gem_info_error("Failed to load quest data"))
                    
            except Exception as e:
                print(f"Error initializing quest data: {e}")
                self.root.after(0, lambda: self.update_gem_info_error(f"Error: {e}"))
            finally:
                self.quest_data_loading = False
        
        # Start background thread
        thread = threading.Thread(target=update_quest_data, daemon=True)
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
        
        # Minimize/Restore button for config window
        minimize_frame = ttk.Frame(preview_frame)
        minimize_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.minimize_btn = ttk.Button(minimize_frame, text=self.language_manager.get_ui_text("hide_config_window", "Hide Config Window"), command=self.toggle_config_window)
        self.minimize_btn.pack(side=tk.LEFT)
        
        self.config_hidden = False
        
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
        
        # Hotkeys Section
        hotkey_frame = ttk.LabelFrame(general_frame, text=self.language_manager.get_ui_text("hotkeys", "Hotkeys"), padding="10")
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
        content_frame = ttk.LabelFrame(general_frame, text=self.language_manager.get_ui_text("text_content", "Text Content"), padding="10")
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
        
        # Position is now hidden and always set to "center"
        self.position_var = tk.StringVar(value="center")
        
        monitor_frame.columnconfigure(1, weight=1)
        
        # Position Offset Section
        offset_frame = ttk.LabelFrame(appearance_frame, text=self.language_manager.get_ui_text("position_offset", "Position Offset"), padding="10")
        offset_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # X Offset
        ttk.Label(offset_frame, text=self.language_manager.get_ui_text("x_offset", "X Offset:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_offset_var = tk.IntVar()
        x_offset_scale = ttk.Scale(offset_frame, from_=-3000, to=3000, variable=self.x_offset_var,
                                  orient=tk.HORIZONTAL, length=200)
        x_offset_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self.x_offset_entry = ttk.Entry(offset_frame, textvariable=self.x_offset_var, width=8)
        self.x_offset_entry.grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Y Offset
        ttk.Label(offset_frame, text=self.language_manager.get_ui_text("y_offset", "Y Offset:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_offset_var = tk.IntVar()
        y_offset_scale = ttk.Scale(offset_frame, from_=-3000, to=3000, variable=self.y_offset_var,
                                  orient=tk.HORIZONTAL, length=200)
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
        opacity_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, length=200)
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
        for var in [self.monitor_var, self.position_var]:
            var.trace('w', self.update_live_preview)
        
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
        """Setup the Gems tab with character management and quest rewards"""
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
        
        # Quest rewards section - no vertical scrolling needed
        quest_frame = ttk.LabelFrame(gems_frame, text="Quest Gem Rewards", padding="10")
        quest_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create simple frame for quest rewards (no vertical scrolling)
        self.scrollable_frame = ttk.Frame(quest_frame)
        self.scrollable_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial gem info label
        self.gem_info_label = ttk.Label(self.scrollable_frame, 
                                       text="Loading quest reward data...", 
                                       font=('Arial', 10), foreground='gray')
        self.gem_info_label.grid(row=0, column=0, pady=20)
        
        # Refresh button
        refresh_frame = ttk.Frame(quest_frame)
        refresh_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.refresh_quest_btn = ttk.Button(refresh_frame, text="Refresh Quest Data", 
                                           command=self.refresh_quest_data)
        self.refresh_quest_btn.pack(side=tk.LEFT)
        
        char_frame.columnconfigure(1, weight=1)
        quest_frame.columnconfigure(0, weight=1)
        quest_frame.rowconfigure(0, weight=1)
        gems_frame.columnconfigure(0, weight=1)
        gems_frame.rowconfigure(2, weight=1)
        
        # Load character data
        self.load_character_data()
    
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
            "class": char_class
        }
        
        characters.append(new_character)
        self.config_manager.update_setting("characters", "profiles", characters)
        self.config_manager.update_setting("characters", "selected", name)
        
        # Clear input fields
        self.new_char_name_var.set("")
        self.new_char_class_var.set("")
        
        # Reload character data
        self.load_character_data()
        
        messagebox.showinfo("Success", f"Character '{name}' ({char_class}) created successfully!")
    
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
            
            messagebox.showinfo("Success", f"Character '{selected_name}' deleted successfully!")
    
    def on_character_select(self, event=None):
        """Handle character selection change"""
        selected_name = self.selected_char_var.get()
        if selected_name:
            self.config_manager.update_setting("characters", "selected", selected_name)
            self.update_character_info(selected_name)
            self.refresh_gem_info()
    
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
        """Show placeholder text when no character is selected"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.gem_info_label = ttk.Label(self.scrollable_frame, 
                                       text="Select a character to view quest gem rewards.", 
                                       font=('Arial', 10), foreground='gray')
        self.gem_info_label.grid(row=0, column=0, pady=20)
    
    def update_gem_info_loading(self):
        """Show loading message"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.gem_info_label = ttk.Label(self.scrollable_frame, 
                                       text="Loading quest reward data...", 
                                       font=('Arial', 10), foreground='blue')
        self.gem_info_label.grid(row=0, column=0, pady=20)
    
    def update_gem_info_error(self, error_message):
        """Show error message"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.gem_info_label = ttk.Label(self.scrollable_frame, 
                                       text=f"Error loading quest data:\n{error_message}", 
                                       font=('Arial', 10), foreground='red')
        self.gem_info_label.grid(row=0, column=0, pady=20)
    
    def refresh_gem_info(self):
        """Refresh the gem information display based on selected character"""
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
        quest_rewards = self.quest_crawler.get_quest_rewards_for_class(current_language, character_class)
        
        # Preserve horizontal scroll position if canvas exists
        scroll_position = None
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, tk.Canvas) and hasattr(widget, 'xview'):
                scroll_position = widget.xview()
                break
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not quest_rewards:
            self.gem_info_label = ttk.Label(self.scrollable_frame, 
                                           text=f"No quest reward data available for {character_class}.\nTry refreshing the quest data.", 
                                           font=('Arial', 10), foreground='orange')
            self.gem_info_label.grid(row=0, column=0, pady=20)
            return
        
        # Get overlay width for card sizing
        overlay_width = self.config_manager.get_setting("appearance", "width", 250)
        card_width = max(200, min(overlay_width, 250))  # Cap at 250px, minimum 200px
        
        # Get or initialize gem selections for this character
        if 'gem_selections' not in character:
            character['gem_selections'] = {}
        
        # Create horizontal scrollable container
        horizontal_canvas = tk.Canvas(self.scrollable_frame, height=400)  # Increased height for more gems
        horizontal_scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="horizontal", command=horizontal_canvas.xview)
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
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        
        # Update scroll region
        self.scrollable_frame.update_idletasks()
        
        # Restore horizontal scroll position if it was preserved
        if scroll_position is not None:
            # Find the horizontal canvas and restore its position
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, tk.Canvas) and hasattr(widget, 'xview_moveto'):
                    # Use a small delay to ensure the canvas is fully rendered
                    self.root.after(10, lambda: widget.xview_moveto(scroll_position[0]))
                    break
    
    def on_gem_click(self, gem, quest_key, character):
        """Handle gem selection click"""
        gem_name = gem['name']
        
        # Toggle selection: if already selected, deselect; otherwise select
        current_selection = character['gem_selections'].get(quest_key, None)
        if current_selection == gem_name:
            # Deselect
            character['gem_selections'][quest_key] = None
        else:
            # Select this gem
            character['gem_selections'][quest_key] = gem_name
        
        # Save the updated character data immediately
        self.save_character_gem_selections(character)
        
        # Refresh the display to show updated selection states
        self.refresh_gem_info()
    
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
        
        if not character or 'gem_selections' not in character:
            return "No gem selections"
        
        selections = character['gem_selections']
        selected_count = sum(1 for selection in selections.values() if selection is not None)
        total_quests = len(selections)
        
        return f"Selected gems: {selected_count}/{total_quests} quests"
    
    def refresh_quest_data(self):
        """Refresh quest data from PoEDB"""
        if self.quest_data_loading:
            messagebox.showinfo("Info", "Quest data is already being updated. Please wait.")
            return
        
        def update_data():
            try:
                self.quest_data_loading = True
                self.root.after(0, self.update_gem_info_loading)
                
                current_language = self.language_manager.get_current_language()
                success = self.quest_crawler.update_quest_data(current_language, force_update=True)
                
                if success:
                    self.root.after(0, lambda: [
                        self.refresh_gem_info(),
                        messagebox.showinfo("Success", "Quest data updated successfully!")
                    ])
                else:
                    self.root.after(0, lambda: [
                        self.update_gem_info_error("Failed to update quest data"),
                        messagebox.showerror("Error", "Failed to update quest data. Please check your internet connection.")
                    ])
                    
            except Exception as e:
                print(f"Error updating quest data: {e}")
                self.root.after(0, lambda: [
                    self.update_gem_info_error(f"Error: {e}"),
                    messagebox.showerror("Error", f"Error updating quest data: {e}")
                ])
            finally:
                self.quest_data_loading = False
        
        # Start background thread
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
    
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
                self.refresh_ui_text()
                self.update_content_for_language()
                
                # Update quest data for new language
                self.initialize_quest_data()
                
                messagebox.showinfo(
                    self.language_manager.get_ui_text("language_changed", "Language Changed"),
                    self.language_manager.get_ui_text("language_changed_message", "Language has been changed. Some changes may require a restart to take full effect.")
                )
    
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