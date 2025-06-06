#!/usr/bin/env python3
"""
Language Manager for PoE Leveling Planner
Handles loading and managing different language files for internationalization.
"""

import json
import os
from typing import Dict, Any, Optional


class LanguageManager:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.current_language = "en_US"  # Default language
        self.languages = {}
        self.available_languages = {
            "en_US": "English (US)",
            "pt_BR": "Português (Brasil)"
        }
        
        # Load current language from config if available
        if config_manager:
            self.current_language = config_manager.get_setting("language", "current", "en_US")
        
        self.load_language(self.current_language)
    
    def load_language(self, language_code: str) -> bool:
        """Load a specific language file"""
        try:
            lang_file = os.path.join("lang", f"{language_code}.json")
            if not os.path.exists(lang_file):
                print(f"Warning: Language file {lang_file} not found, falling back to en_US")
                language_code = "en_US"
                lang_file = os.path.join("lang", f"{language_code}.json")
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.languages[language_code] = json.load(f)
            
            self.current_language = language_code
            return True
            
        except Exception as e:
            print(f"Error loading language file {language_code}: {e}")
            # Fallback to English if current language fails
            if language_code != "en_US":
                return self.load_language("en_US")
            return False
    
    def get_text(self, category: str, key: str, default: str = None) -> str:
        """Get translated text for a specific category and key"""
        try:
            if self.current_language in self.languages:
                lang_data = self.languages[self.current_language]
                if category in lang_data and key in lang_data[category]:
                    return lang_data[category][key]
            
            # Fallback to default if provided
            if default is not None:
                return default
            
            # Fallback to English if current language doesn't have the text
            if self.current_language != "en_US" and "en_US" in self.languages:
                lang_data = self.languages["en_US"]
                if category in lang_data and key in lang_data[category]:
                    return lang_data[category][key]
            
            # Last resort: return the key itself
            return f"{category}.{key}"
            
        except Exception as e:
            print(f"Error getting text for {category}.{key}: {e}")
            return default if default else f"{category}.{key}"
    
    def get_ui_text(self, key: str, default: str = None) -> str:
        """Convenience method to get UI text"""
        return self.get_text("ui", key, default)
    
    def get_message(self, key: str, default: str = None) -> str:
        """Convenience method to get message text"""
        return self.get_text("messages", key, default)
    
    def get_content(self, key: str, default: str = None) -> str:
        """Convenience method to get content text"""
        return self.get_text("content", key, default)
    
    def set_language(self, language_code: str) -> bool:
        """Set the current language and update config"""
        if language_code in self.available_languages:
            if self.load_language(language_code):
                if self.config_manager:
                    self.config_manager.update_setting("language", "current", language_code)
                    self.config_manager.save_config()
                return True
        return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get dictionary of available languages"""
        return self.available_languages.copy()
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language
    
    def get_current_language_name(self) -> str:
        """Get current language display name"""
        return self.available_languages.get(self.current_language, self.current_language) 