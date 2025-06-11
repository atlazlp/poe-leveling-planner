#!/usr/bin/env python3
"""
Data Manager for PoE Leveling Planner
Centralized data management with intelligent caching and update logic.
"""

import os
import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable
from quest_reward_crawler import QuestRewardCrawler
from vendor_reward_crawler import VendorRewardCrawler


class DataManager:
    def __init__(self):
        self.quest_crawler = QuestRewardCrawler()
        self.vendor_crawler = VendorRewardCrawler()
        
        # Cache update interval (1 week in seconds)
        self.UPDATE_INTERVAL = 7 * 24 * 3600  # 1 week
        
        # Path to data directory relative to src
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.metadata_file = os.path.join(self.data_dir, "data_metadata.json")
    
    def _get_data_path(self, filename: str) -> str:
        """Get the full path to a data file"""
        return os.path.join(self.data_dir, filename)
        
        # Initialize metadata
        self.metadata = self.load_metadata()
        
    def load_metadata(self) -> Dict[str, Any]:
        """Load metadata about data updates"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
        
        # Return default metadata
        return {
            "last_update_check": 0,
            "last_quest_update": {},
            "last_vendor_update": {},
            "first_run_completed": False
        }
    
    def save_metadata(self):
        """Save metadata about data updates"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def is_first_run(self) -> bool:
        """Check if this is the first time the app is running"""
        return not self.metadata.get("first_run_completed", False)
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for data updates"""
        if self.is_first_run():
            return True
        
        last_check = self.metadata.get("last_update_check", 0)
        current_time = time.time()
        
        return (current_time - last_check) >= self.UPDATE_INTERVAL
    
    def is_data_available(self, language: str) -> bool:
        """Check if data files exist for the given language"""
        quest_file = self._get_data_path(f"quest_rewards_{language}.json")
        vendor_file = self._get_data_path(f"vendor_rewards_{language}.json")
        
        return os.path.exists(quest_file) and os.path.exists(vendor_file)
    
    def get_data_age(self, language: str) -> Dict[str, float]:
        """Get the age of data files in hours"""
        ages = {}
        current_time = time.time()
        
        quest_file = self._get_data_path(f"quest_rewards_{language}.json")
        vendor_file = self._get_data_path(f"vendor_rewards_{language}.json")
        
        if os.path.exists(quest_file):
            file_time = os.path.getmtime(quest_file)
            ages["quest"] = (current_time - file_time) / 3600
        else:
            ages["quest"] = float('inf')
        
        if os.path.exists(vendor_file):
            file_time = os.path.getmtime(vendor_file)
            ages["vendor"] = (current_time - file_time) / 3600
        else:
            ages["vendor"] = float('inf')
        
        return ages
    
    def initialize_data(self, language: str, progress_callback: Optional[Callable[[str, int, int], None]] = None) -> bool:
        """Initialize all data for the given language"""
        print(f"Initializing data for {language}...")
        
        if progress_callback:
            progress_callback("Initializing data...", 0, 4)
        
        success = True
        
        # Update quest data
        if progress_callback:
            progress_callback("Downloading quest rewards...", 1, 4)
        
        quest_success = self.quest_crawler.update_quest_data(language, force_update=True)
        if quest_success:
            self.metadata["last_quest_update"][language] = time.time()
            print(f"Quest data updated successfully for {language}")
        else:
            print(f"Failed to update quest data for {language}")
            success = False
        
        # Update vendor data
        if progress_callback:
            progress_callback("Downloading vendor rewards...", 2, 4)
        
        vendor_success = self.vendor_crawler.update_vendor_data(language, force_update=True)
        if vendor_success:
            self.metadata["last_vendor_update"][language] = time.time()
            print(f"Vendor data updated successfully for {language}")
        else:
            print(f"Failed to update vendor data for {language}")
            success = False
        
        # Update metadata
        if progress_callback:
            progress_callback("Finalizing...", 3, 4)
        
        if success:
            self.metadata["last_update_check"] = time.time()
            if self.is_first_run():
                self.metadata["first_run_completed"] = True
        
        self.save_metadata()
        
        if progress_callback:
            progress_callback("Complete!" if success else "Failed!", 4, 4)
        
        return success
    
    def check_and_update_data(self, language: str, progress_callback: Optional[Callable[[str, int, int], None]] = None) -> bool:
        """Check if data needs updating and update if necessary"""
        if not self.should_check_for_updates():
            print("Data is up to date, no update check needed")
            return True
        
        print("Checking for data updates...")
        
        if progress_callback:
            progress_callback("Checking for updates...", 0, 4)
        
        # Check if data files exist
        if not self.is_data_available(language):
            print("Data files missing, performing full initialization")
            return self.initialize_data(language, progress_callback)
        
        # Check data age - convert UPDATE_INTERVAL from seconds to hours
        ages = self.get_data_age(language)
        update_threshold_hours = self.UPDATE_INTERVAL / 3600  # Convert seconds to hours (168 hours)
        quest_outdated = ages["quest"] > update_threshold_hours
        vendor_outdated = ages["vendor"] > update_threshold_hours
        
        print(f"Data age check: Quest={ages['quest']:.1f}h, Vendor={ages['vendor']:.1f}h, Threshold={update_threshold_hours:.1f}h")
        print(f"Quest outdated: {quest_outdated}, Vendor outdated: {vendor_outdated}")
        
        if not quest_outdated and not vendor_outdated:
            print("All data is up to date")
            self.metadata["last_update_check"] = time.time()
            self.save_metadata()
            if progress_callback:
                progress_callback("Data is up to date", 4, 4)
            return True
        
        success = True
        step = 1
        
        # Update quest data if needed
        if quest_outdated:
            if progress_callback:
                progress_callback("Updating quest rewards...", step, 4)
            step += 1
            
            quest_success = self.quest_crawler.update_quest_data(language, force_update=True)
            if quest_success:
                self.metadata["last_quest_update"][language] = time.time()
                print(f"Quest data updated successfully for {language}")
            else:
                print(f"Failed to update quest data for {language}")
                success = False
        
        # Update vendor data if needed
        if vendor_outdated:
            if progress_callback:
                progress_callback("Updating vendor rewards...", step, 4)
            step += 1
            
            vendor_success = self.vendor_crawler.update_vendor_data(language, force_update=True)
            if vendor_success:
                self.metadata["last_vendor_update"][language] = time.time()
                print(f"Vendor data updated successfully for {language}")
            else:
                print(f"Failed to update vendor data for {language}")
                success = False
        
        # Update metadata
        if progress_callback:
            progress_callback("Finalizing...", 4, 4)
        
        self.metadata["last_update_check"] = time.time()
        self.save_metadata()
        
        return success
    
    def initialize_data_async(self, language: str, callback: Optional[Callable[[bool], None]] = None, 
                            progress_callback: Optional[Callable[[str, int, int], None]] = None):
        """Initialize data asynchronously in a background thread"""
        def update_thread():
            try:
                success = self.check_and_update_data(language, progress_callback)
                if callback:
                    callback(success)
            except Exception as e:
                print(f"Error in data initialization thread: {e}")
                if callback:
                    callback(False)
        
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()
        return thread
    
    def get_quest_data(self, language: str) -> Optional[List[Dict[str, Any]]]:
        """Get quest data for the given language"""
        return self.quest_crawler.load_quest_data(language)
    
    def get_vendor_data(self, language: str) -> Optional[List[Dict[str, Any]]]:
        """Get vendor data for the given language"""
        return self.vendor_crawler.load_vendor_data(language)
    
    def get_data_status(self, language: str) -> Dict[str, Any]:
        """Get status information about the data"""
        ages = self.get_data_age(language)
        
        return {
            "data_available": self.is_data_available(language),
            "is_first_run": self.is_first_run(),
            "should_check_updates": self.should_check_for_updates(),
            "quest_age_hours": ages.get("quest", float('inf')),
            "vendor_age_hours": ages.get("vendor", float('inf')),
            "last_update_check": self.metadata.get("last_update_check", 0),
            "quest_outdated": ages.get("quest", float('inf')) > (self.UPDATE_INTERVAL / 3600),
            "vendor_outdated": ages.get("vendor", float('inf')) > (self.UPDATE_INTERVAL / 3600)
        }
    
    def get_quest_rewards_for_class(self, language: str, character_class: str) -> List[Dict[str, Any]]:
        """Get quest rewards filtered for a specific character class"""
        return self.quest_crawler.get_quest_rewards_for_class(language, character_class)
    
    def get_vendor_rewards_for_class(self, language: str, character_class: str) -> List[Dict[str, Any]]:
        """Get vendor rewards for a specific character class"""
        return self.vendor_crawler.get_vendor_rewards_for_class(language, character_class)
    
    def force_update_all(self, language: str, progress_callback: Optional[Callable[[str, int, int], None]] = None) -> bool:
        """Force update all data regardless of age"""
        return self.initialize_data(language, progress_callback) 