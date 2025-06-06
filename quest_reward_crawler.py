#!/usr/bin/env python3
"""
Quest Reward Crawler for PoE Leveling Planner
Fetches quest reward data from PoEDB and saves it in language-specific files.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from typing import Dict, List, Any, Optional
import time


class QuestRewardCrawler:
    def __init__(self):
        self.base_urls = {
            "en_US": "https://poedb.tw/us/QuestRewards",
            "pt_BR": "https://poedb.tw/pt/QuestRewards"
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Class name mappings for different languages
        self.class_mappings = {
            "en_US": {
                "Marauder": "Marauder",
                "Witch": "Witch", 
                "Scion": "Scion",
                "Ranger": "Ranger",
                "Duelist": "Duelist",
                "Shadow": "Shadow",
                "Templar": "Templar"
            },
            "pt_BR": {
                "Marauder": "Marauder",
                "Witch": "Bruxa",
                "Scion": "Scion", 
                "Ranger": "Ranger",
                "Duelist": "Duelista",
                "Shadow": "Sombra",
                "Templar": "Templário"
            }
        }
        
    def get_gem_color(self, gem_name: str) -> str:
        """Determine gem color based on gem name patterns"""
        # Common red gems (strength-based)
        red_patterns = [
            'strike', 'slam', 'smite', 'cleave', 'sweep', 'molten', 'burning', 'infernal',
            'heavy', 'ground', 'shield', 'perforate', 'ruthless', 'melee', 'fortify',
            'multistrike', 'ancestral', 'rage', 'berserk', 'intimidating', 'brutality',
            'fire', 'ignite', 'combustion', 'immolate', 'elemental focus', 'concentrated',
            'added fire', 'weapon elemental', 'avatar of fire'
        ]
        
        # Common green gems (dexterity-based)
        green_patterns = [
            'arrow', 'shot', 'bow', 'projectile', 'pierce', 'fork', 'chain', 'split',
            'barrage', 'rain', 'tornado', 'whirling', 'flicker', 'viper', 'cobra',
            'poison', 'toxic', 'caustic', 'puncture', 'bleed', 'lacerate', 'blade',
            'spectral', 'ethereal', 'frost', 'ice', 'cold', 'hypothermia', 'elemental',
            'trap', 'mine', 'explosive', 'bear', 'cluster', 'multiple', 'lesser multiple',
            'greater multiple', 'faster attacks', 'faster projectiles', 'point blank',
            'far shot', 'iron grip', 'ballista', 'mirage', 'clone'
        ]
        
        # Common blue gems (intelligence-based)  
        blue_patterns = [
            'bolt', 'pulse', 'orb', 'ball', 'wave', 'storm', 'lightning', 'shock',
            'spark', 'arc', 'tendrils', 'call', 'warp', 'teleport', 'blink', 'flame',
            'fireball', 'incinerate', 'flameblast', 'magma', 'rolling', 'spell',
            'cast', 'echo', 'cascade', 'controlled', 'elemental focus', 'penetration',
            'minion', 'zombie', 'skeleton', 'spectre', 'golem', 'animate', 'raise',
            'summon', 'convocation', 'offering', 'aura', 'herald', 'curse', 'hex',
            'mark', 'brand', 'sigil', 'void', 'chaos', 'contagion', 'essence',
            'wither', 'blight', 'despair', 'temporal', 'arcane', 'mana', 'clarity',
            'discipline', 'purity', 'grace', 'haste', 'anger', 'hatred', 'wrath'
        ]
        
        gem_lower = gem_name.lower()
        
        # Check for red gem patterns
        for pattern in red_patterns:
            if pattern in gem_lower:
                return "gem_red"
                
        # Check for green gem patterns  
        for pattern in green_patterns:
            if pattern in gem_lower:
                return "gem_green"
                
        # Check for blue gem patterns
        for pattern in blue_patterns:
            if pattern in gem_lower:
                return "gem_blue"
        
        # Default fallback - try to guess based on common words
        if any(word in gem_lower for word in ['support', 'aura', 'curse', 'spell', 'minion']):
            return "gem_blue"
        elif any(word in gem_lower for word in ['attack', 'weapon', 'melee', 'fire']):
            return "gem_red"
        elif any(word in gem_lower for word in ['bow', 'projectile', 'trap', 'mine', 'cold']):
            return "gem_green"
            
        # Final fallback
        return "gem_blue"
    
    def parse_quest_rewards(self, html_content: str, language: str) -> List[Dict[str, Any]]:
        """Parse the HTML content to extract quest reward information"""
        soup = BeautifulSoup(html_content, 'lxml')
        quests = []
        
        try:
            # Find the main quest reward table
            tables = soup.find_all('table')
            if not tables:
                print(f"No tables found in {language} page")
                return []
            
            # Look for the table with quest rewards - find the one with the most quest data
            quest_table = None
            max_quest_rows = 0
            
            for table in tables:
                # Check if this table contains quest reward data by looking for class names in headers
                first_row = table.find('tr')
                if first_row:
                    cells = first_row.find_all(['th', 'td'])
                    if len(cells) >= 7:  # Should have at least 7 columns for all classes
                        # Check if we have class names in the header
                        header_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                        if any(class_name in header_text for class_name in ['Marauder', 'Witch', 'Ranger', 'Shadow', 'Templar', 'Duelist', 'Scion']):
                            # Count how many rows have quest links (actual quest data)
                            rows = table.find_all('tr')
                            quest_row_count = 0
                            for row in rows:
                                row_cells = row.find_all(['td', 'th'])
                                if row_cells and len(row_cells) >= 7:
                                    first_cell = row_cells[0]
                                    quest_link = first_cell.find('a')
                                    if quest_link:
                                        quest_name = quest_link.get_text(strip=True)
                                        # Skip header-like entries
                                        if quest_name and quest_name not in ['Marauder', 'Witch', 'Scion', 'Ranger', 'Duelist', 'Shadow', 'Templar']:
                                            quest_row_count += 1
                            
                            print(f"Found table with {quest_row_count} quest rows")
                            if quest_row_count > max_quest_rows:
                                max_quest_rows = quest_row_count
                                quest_table = table
            
            if not quest_table:
                print(f"Quest reward table not found in {language} page")
                return []
            
            rows = quest_table.find_all('tr')
            print(f"Using table with {len(rows)} total rows, {max_quest_rows} quest rows")
            
            # Skip header row(s) and process data rows
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                if not cells or len(cells) < 7:  # Need at least 7 cells for all classes
                    continue
                
                # Check if this row contains a quest name (first cell should have a quest link)
                first_cell = cells[0]
                quest_link = first_cell.find('a')
                
                if quest_link:
                    quest_name = quest_link.get_text(strip=True)
                    
                    # Skip if quest name is empty or looks like a header
                    if not quest_name or quest_name in ['Marauder', 'Witch', 'Scion', 'Ranger', 'Duelist', 'Shadow', 'Templar']:
                        continue
                    
                    # Try to extract act information from the quest name or surrounding context
                    act = "Unknown"
                    
                    # Special case for tutorial quest
                    if quest_name == "The Twilight Strand":
                        act = "Act 0"
                    else:
                        # Look for act information in the quest name itself or first cell text
                        first_cell_text = first_cell.get_text(strip=True)
                        act_match = re.search(r'Act\s*(\d+)', first_cell_text, re.IGNORECASE)
                        if act_match:
                            act = f"Act {act_match.group(1)}"
                        else:
                            # Look for act information in previous rows or context
                            for prev_row_idx in range(max(0, i-5), i):
                                if prev_row_idx < len(rows):
                                    prev_row_text = rows[prev_row_idx].get_text()
                                    act_match = re.search(r'Act\s*(\d+)', prev_row_text, re.IGNORECASE)
                                    if act_match:
                                        act = f"Act {act_match.group(1)}"
                                        break
                            
                            # If still no act found, try to infer from quest name patterns
                            if act == "Unknown":
                                # Common Act 1 quests
                                if any(name in quest_name for name in ["Enemy at the Gate", "Breaking Some Eggs", "Caged Brute", "Siren's Cadence"]):
                                    act = "Act 1"
                                # Common Act 2 quests  
                                elif any(name in quest_name for name in ["Intruders in Black", "Sharp and Cruel", "Root of the Problem"]):
                                    act = "Act 2"
                                # Common Act 3 quests
                                elif any(name in quest_name for name in ["Lost in Love", "Sever the Right Hand", "Fixture of Fate"]):
                                    act = "Act 3"
                                # Common Act 4 quests
                                elif any(name in quest_name for name in ["Eternal Nightmare", "Breaking the Seal"]):
                                    act = "Act 4"
                                # And so on for other acts...
                    
                    # Check if this quest has gem rewards
                    has_gems = False
                    for cell in cells[1:]:  # Skip first cell (quest name)
                        if cell.find('a'):  # Has gem links
                            has_gems = True
                            break
                    
                    if not has_gems:
                        continue
                    
                    current_quest = {
                        "name": quest_name,
                        "act": act,
                        "rewards": {}
                    }
                    
                    # Map class rewards (standard order: Marauder, Witch, Scion, Ranger, Duelist, Shadow, Templar)
                    class_order = ["Marauder", "Witch", "Scion", "Ranger", "Duelist", "Shadow", "Templar"]
                    
                    for j, class_name in enumerate(class_order):
                        if j + 1 < len(cells):  # +1 to skip quest name cell
                            cell = cells[j + 1]
                            gems = []
                            
                            # Extract gem names from links
                            gem_links = cell.find_all('a')
                            for link in gem_links:
                                gem_name = link.get_text(strip=True)
                                if gem_name and gem_name not in ['', ' ']:
                                    gem_color = self.get_gem_color(gem_name)
                                    gems.append({
                                        "name": gem_name,
                                        "color": gem_color
                                    })
                            
                            if gems:  # Only add if there are gems
                                current_quest["rewards"][class_name] = gems
                    
                    if current_quest["rewards"]:  # Only add quest if it has gem rewards
                        quests.append(current_quest)
                        print(f"Added quest: {quest_name} ({act}) with {len(current_quest['rewards'])} class rewards")
            
            print(f"Parsed {len(quests)} quests with gem rewards for {language}")
            return quests
            
        except Exception as e:
            print(f"Error parsing quest rewards for {language}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_quest_data(self, language: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch quest reward data for a specific language"""
        if language not in self.base_urls:
            print(f"Language {language} not supported")
            return None
        
        url = self.base_urls[language]
        
        try:
            print(f"Fetching quest data from {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML content
            quests = self.parse_quest_rewards(response.text, language)
            return quests
            
        except requests.RequestException as e:
            print(f"Error fetching data for {language}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for {language}: {e}")
            return None
    
    def save_quest_data(self, language: str, quests: List[Dict[str, Any]]) -> bool:
        """Save quest data to a language-specific file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            filename = f"data/quest_rewards_{language}.json"
            
            # Add metadata
            data = {
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "language": language,
                "total_quests": len(quests),
                "quests": quests
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(quests)} quests to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving quest data for {language}: {e}")
            return False
    
    def load_quest_data(self, language: str) -> Optional[List[Dict[str, Any]]]:
        """Load quest data from a language-specific file"""
        try:
            filename = f"data/quest_rewards_{language}.json"
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get("quests", [])
            
        except Exception as e:
            print(f"Error loading quest data for {language}: {e}")
            return None
    
    def is_data_outdated(self, language: str, max_age_hours: int = 24) -> bool:
        """Check if the cached data is outdated"""
        try:
            filename = f"data/quest_rewards_{language}.json"
            
            if not os.path.exists(filename):
                return True
            
            # Check file modification time
            file_time = os.path.getmtime(filename)
            current_time = time.time()
            age_hours = (current_time - file_time) / 3600
            
            return age_hours > max_age_hours
            
        except Exception as e:
            print(f"Error checking data age for {language}: {e}")
            return True
    
    def update_quest_data(self, language: str, force_update: bool = False) -> bool:
        """Update quest data for a specific language if needed"""
        if not force_update and not self.is_data_outdated(language):
            print(f"Quest data for {language} is up to date")
            return True
        
        print(f"Updating quest data for {language}")
        quests = self.fetch_quest_data(language)
        
        if quests is not None:
            return self.save_quest_data(language, quests)
        
        return False
    
    def update_all_languages(self, force_update: bool = False) -> Dict[str, bool]:
        """Update quest data for all supported languages"""
        results = {}
        
        for language in self.base_urls.keys():
            print(f"\n--- Updating {language} ---")
            results[language] = self.update_quest_data(language, force_update)
            
            # Add delay between requests to be respectful
            if len(self.base_urls) > 1:
                time.sleep(2)
        
        return results
    
    def get_quest_rewards_for_class(self, language: str, character_class: str) -> List[Dict[str, Any]]:
        """Get quest rewards filtered for a specific character class"""
        quests = self.load_quest_data(language)
        if not quests:
            return []
        
        filtered_quests = []
        for quest in quests:
            if character_class in quest.get("rewards", {}):
                quest_copy = quest.copy()
                quest_copy["class_rewards"] = quest["rewards"][character_class]
                filtered_quests.append(quest_copy)
        
        return filtered_quests


def main():
    """Test the crawler functionality"""
    crawler = QuestRewardCrawler()
    
    print("Testing Quest Reward Crawler")
    print("=" * 40)
    
    # Update data for all languages
    results = crawler.update_all_languages(force_update=True)
    
    print("\nUpdate Results:")
    for language, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {language}: {status}")
    
    # Test loading data for a specific class
    print("\nTesting class-specific rewards (Marauder, en_US):")
    marauder_quests = crawler.get_quest_rewards_for_class("en_US", "Marauder")
    for quest in marauder_quests[:3]:  # Show first 3 quests
        print(f"  {quest['name']} ({quest['act']})")
        for gem in quest.get('class_rewards', []):
            print(f"    - {gem['name']} ({gem['color']})")


if __name__ == "__main__":
    main() 