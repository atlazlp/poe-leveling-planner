#!/usr/bin/env python3
"""
Vendor Reward Crawler for PoE Leveling Planner
Fetches vendor reward data from PoE Wiki and enriches it with gem color information from PoEDB.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from typing import Dict, List, Any, Optional
import time
from html_parser_utils import get_soup


class VendorRewardCrawler:
    def __init__(self):
        self.vendor_urls = {
            "en_US": "https://www.poewiki.net/wiki/List_of_vendor_rewards"
        }
        self.gem_urls = {
            "en_US": "https://poedb.tw/us/Gem",
            "pt_BR": "https://poedb.tw/pt/Gem"
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Class name mappings for different languages
        self.class_mappings = {
            "en_US": {
                "Witch": "Witch",
                "Shadow": "Shadow", 
                "Ranger": "Ranger",
                "Duelist": "Duelist",
                "Marauder": "Marauder",
                "Templar": "Templar",
                "Scion": "Scion"
            },
            "pt_BR": {
                "Witch": "Bruxa",
                "Shadow": "Sombra",
                "Ranger": "Ranger", 
                "Duelist": "Duelista",
                "Marauder": "Marauder",
                "Templar": "Templário",
                "Scion": "Scion"
            }
        }
        
        # Cache for gem color information
        self.gem_colors = {}
        
    def get_gem_color_from_name(self, gem_name: str) -> str:
        """Determine gem color based on gem name patterns (fallback method)"""
        # Common red gems (strength-based)
        red_patterns = [
            'strike', 'slam', 'smite', 'cleave', 'sweep', 'molten', 'burning', 'infernal',
            'heavy', 'ground', 'shield', 'perforate', 'ruthless', 'melee', 'fortify',
            'multistrike', 'ancestral', 'rage', 'berserk', 'intimidating', 'brutality',
            'fire', 'ignite', 'combustion', 'immolate', 'concentrated',
            'added fire', 'weapon elemental', 'avatar of fire', 'anger', 'hatred'
        ]
        
        # Common green gems (dexterity-based)
        green_patterns = [
            'arrow', 'shot', 'bow', 'projectile', 'pierce', 'fork', 'chain', 'split',
            'barrage', 'rain', 'tornado', 'whirling', 'flicker', 'viper', 'cobra',
            'poison', 'toxic', 'caustic', 'puncture', 'bleed', 'lacerate', 'blade',
            'spectral', 'ethereal', 'frost', 'ice', 'cold', 'hypothermia',
            'trap', 'mine', 'explosive', 'bear', 'cluster', 'multiple', 'lesser multiple',
            'greater multiple', 'faster attacks', 'faster projectiles', 'point blank',
            'far shot', 'iron grip', 'ballista', 'mirage', 'clone', 'grace'
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
            'discipline', 'purity', 'wrath'
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
    
    def fetch_gem_colors_from_poedb(self, language: str) -> Dict[str, str]:
        """Fetch gem color information from PoEDB"""
        if language in self.gem_colors:
            return self.gem_colors[language]
            
        print(f"Fetching gem color data from PoEDB ({language})...")
        
        try:
            url = self.gem_urls.get(language, self.gem_urls["en_US"])
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = get_soup(response.content)
            gem_colors = {}
            
            # Find all gem entries in the page
            # PoEDB uses specific patterns for gem listings
            gem_links = soup.find_all('a', href=True)
            
            for link in gem_links:
                href = link.get('href', '')
                # Look for gem detail page links
                if '/Gem/' in href or '/gem/' in href:
                    gem_name = link.get_text(strip=True)
                    if gem_name and len(gem_name) > 2:  # Filter out very short names
                        # Try to determine color from the link context or surrounding elements
                        parent = link.find_parent()
                        if parent:
                            parent_text = parent.get_text().lower()
                            parent_html = str(parent).lower()
                            
                            # Look for color indicators in the surrounding HTML
                            if any(indicator in parent_html for indicator in ['red', 'strength', 'str']):
                                gem_colors[gem_name] = "gem_red"
                            elif any(indicator in parent_html for indicator in ['green', 'dexterity', 'dex']):
                                gem_colors[gem_name] = "gem_green"
                            elif any(indicator in parent_html for indicator in ['blue', 'intelligence', 'int']):
                                gem_colors[gem_name] = "gem_blue"
                            else:
                                # Use pattern matching as fallback
                                gem_colors[gem_name] = self.get_gem_color_from_name(gem_name)
            
            # Also look for gems in table structures
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 1:
                        first_cell = cells[0]
                        gem_link = first_cell.find('a')
                        
                        if gem_link:
                            gem_name = gem_link.get_text(strip=True)
                            if gem_name and len(gem_name) > 2:
                                # Look for color indicators in the row
                                row_html = str(row).lower()
                                if any(indicator in row_html for indicator in ['red', 'strength', 'str']):
                                    gem_colors[gem_name] = "gem_red"
                                elif any(indicator in row_html for indicator in ['green', 'dexterity', 'dex']):
                                    gem_colors[gem_name] = "gem_green"
                                elif any(indicator in row_html for indicator in ['blue', 'intelligence', 'int']):
                                    gem_colors[gem_name] = "gem_blue"
                                else:
                                    # Use pattern matching as fallback
                                    gem_colors[gem_name] = self.get_gem_color_from_name(gem_name)
            
            self.gem_colors[language] = gem_colors
            print(f"Fetched {len(gem_colors)} gem colors from PoEDB ({language})")
            return gem_colors
            
        except Exception as e:
            print(f"Error fetching gem colors from PoEDB ({language}): {e}")
            return {}
    
    def parse_vendor_rewards(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse the HTML content to extract vendor reward information"""
        soup = get_soup(html_content)
        
        try:
            # Find the main vendor reward table
            tables = soup.find_all('table')
            if not tables:
                print("No tables found in vendor rewards page")
                return []
            
            # Look for the table with vendor rewards - it should have class columns
            vendor_table = None
            for table in tables:
                first_row = table.find('tr')
                if first_row:
                    cells = first_row.find_all(['th', 'td'])
                    if len(cells) >= 7:  # Should have at least 7 columns for all classes
                        # Check if we have class names in the header
                        header_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                        if any(class_name in header_text for class_name in ['Witch', 'Shadow', 'Ranger', 'Duelist', 'Marauder', 'Templar', 'Scion']):
                            vendor_table = table
                            break
            
            if not vendor_table:
                print("Vendor reward table not found")
                return []
            
            rows = vendor_table.find_all('tr')
            print(f"Found vendor table with {len(rows)} rows")
            
            # Parse header to get class column indices
            header_row = rows[0]
            header_cells = header_row.find_all(['th', 'td'])
            
            class_indices = {}
            for i, cell in enumerate(header_cells):
                cell_text = cell.get_text(strip=True)
                if cell_text in ['Witch', 'Shadow', 'Ranger', 'Duelist', 'Marauder', 'Templar', 'Scion']:
                    class_indices[cell_text] = i
            
            print(f"Found class columns: {class_indices}")
            
            # Parse data rows
            vendor_rewards = []
            current_quest = None
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if not cells or len(cells) < max(class_indices.values()) + 1:
                    continue
                
                # Check if this row contains a quest name
                first_cell = cells[0]
                quest_link = first_cell.find('a')
                
                if quest_link:
                    quest_name = quest_link.get_text(strip=True)
                    if quest_name:
                        current_quest = quest_name
                        print(f"Processing quest: {current_quest}")
                
                if not current_quest:
                    continue
                
                # Extract gems for each class
                for class_name, col_index in class_indices.items():
                    if col_index < len(cells):
                        cell = cells[col_index]
                        
                        # Find all gem links in this cell
                        gem_links = cell.find_all('a')
                        for gem_link in gem_links:
                            gem_name = gem_link.get_text(strip=True)
                            if gem_name and gem_name not in ['Witch', 'Shadow', 'Ranger', 'Duelist', 'Marauder', 'Templar', 'Scion']:
                                vendor_rewards.append({
                                    'quest': current_quest,
                                    'class': class_name,
                                    'gem': gem_name
                                })
            
            print(f"Parsed {len(vendor_rewards)} vendor reward entries")
            return vendor_rewards
            
        except Exception as e:
            print(f"Error parsing vendor rewards: {e}")
            return []
    
    def fetch_vendor_data(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch vendor reward data from PoE Wiki"""
        try:
            url = self.vendor_urls["en_US"]
            print(f"Fetching vendor data from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            vendor_rewards = self.parse_vendor_rewards(response.text)
            return vendor_rewards
            
        except Exception as e:
            print(f"Error fetching vendor data: {e}")
            return None
    
    def enrich_with_gem_colors(self, vendor_rewards: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Enrich vendor rewards with gem color information"""
        gem_colors = self.fetch_gem_colors_from_poedb(language)
        
        for reward in vendor_rewards:
            gem_name = reward['gem']
            if gem_name in gem_colors:
                reward['color'] = gem_colors[gem_name]
            else:
                # Use pattern matching as fallback
                reward['color'] = self.get_gem_color_from_name(gem_name)
        
        return vendor_rewards
    
    def organize_by_quest_and_class(self, vendor_rewards: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Organize vendor rewards by quest and class"""
        organized = {}
        
        for reward in vendor_rewards:
            quest = reward['quest']
            class_name = reward['class']
            
            if quest not in organized:
                organized[quest] = {}
            
            if class_name not in organized[quest]:
                organized[quest][class_name] = []
            
            organized[quest][class_name].append({
                'name': reward['gem'],
                'color': reward['color']
            })
        
        return organized
    
    def create_gem_translation_map(self, english_gems: Dict[str, str], portuguese_gems: Dict[str, str]) -> Dict[str, str]:
        """Create a translation map from English to Portuguese gem names"""
        translation_map = {}
        
        # First, try exact matches by removing common prefixes/suffixes
        def normalize_name(name):
            # Remove common prefixes and suffixes for better matching
            normalized = name.lower()
            # Remove "support" and "suporte" 
            normalized = normalized.replace(" support", "").replace(" suporte:", "").replace("suporte: ", "")
            # Remove common articles
            normalized = normalized.replace("the ", "").replace("a ", "").replace("an ", "")
            return normalized.strip()
        
        # Create normalized lookup for Portuguese gems
        pt_normalized = {}
        for pt_name, color in portuguese_gems.items():
            normalized = normalize_name(pt_name)
            if normalized not in pt_normalized:
                pt_normalized[normalized] = []
            pt_normalized[normalized].append((pt_name, color))
        
        # Try to match English gems to Portuguese gems
        for en_name, en_color in english_gems.items():
            en_normalized = normalize_name(en_name)
            
            # Look for exact normalized match with same color
            if en_normalized in pt_normalized:
                for pt_name, pt_color in pt_normalized[en_normalized]:
                    if en_color == pt_color:
                        translation_map[en_name] = pt_name
                        break
            
            # If no exact match, try partial matches with same color
            if en_name not in translation_map:
                en_words = set(en_normalized.split())
                best_match = None
                best_score = 0
                
                for pt_name, pt_color in portuguese_gems.items():
                    if en_color == pt_color:  # Only consider gems of the same color
                        pt_normalized_name = normalize_name(pt_name)
                        pt_words = set(pt_normalized_name.split())
                        
                        # Calculate similarity score
                        common_words = en_words & pt_words
                        if common_words:
                            score = len(common_words) / max(len(en_words), len(pt_words))
                            if score > best_score and score > 0.3:  # Minimum similarity threshold
                                best_score = score
                                best_match = pt_name
                
                if best_match:
                    translation_map[en_name] = best_match
        
        return translation_map

    def translate_gem_names(self, vendor_rewards: List[Dict[str, Any]], target_language: str) -> List[Dict[str, Any]]:
        """Translate gem names using PoEDB data"""
        if target_language == "en_US":
            return vendor_rewards
        
        # Fetch gem data from both languages
        english_gems = self.fetch_gem_colors_from_poedb("en_US")
        target_gems = self.fetch_gem_colors_from_poedb(target_language)
        
        if not english_gems or not target_gems:
            print(f"Warning: Could not fetch gem data for translation to {target_language}")
            return vendor_rewards
        
        # Create translation mapping
        translation_map = self.create_gem_translation_map(english_gems, target_gems)
        
        print(f"Created translation map with {len(translation_map)} entries for {target_language}")
        
        # Apply translations
        translated_rewards = []
        for reward in vendor_rewards:
            translated_reward = reward.copy()
            gem_name = reward['gem']
            
            if gem_name in translation_map:
                translated_reward['gem'] = translation_map[gem_name]
                print(f"Translated: {gem_name} -> {translation_map[gem_name]}")
            else:
                print(f"No translation found for: {gem_name}")
            
            translated_rewards.append(translated_reward)
        
        return translated_rewards
    
    def save_vendor_data(self, language: str, vendor_rewards: List[Dict[str, Any]]) -> bool:
        """Save vendor reward data to JSON file"""
        try:
            # Organize data by quest and class
            organized_data = self.organize_by_quest_and_class(vendor_rewards)
            
            # Convert to the format expected by the UI - separate data by class
            formatted_data = []
            for quest_name, class_data in organized_data.items():
                # Create separate quest entries for each class that has gems
                for class_name in ['Witch', 'Shadow', 'Ranger', 'Duelist', 'Marauder', 'Templar', 'Scion']:
                    if class_name in class_data and class_data[class_name]:
                        # Remove duplicates while preserving order
                        seen_gems = set()
                        unique_gems = []
                        for gem in class_data[class_name]:
                            gem_name = gem['name']
                            if gem_name not in seen_gems:
                                seen_gems.add(gem_name)
                                unique_gems.append(gem)
                        
                        if unique_gems:  # Only add if there are unique gems
                            quest_entry = {
                                'name': f"{quest_name} ({class_name})",  # Include class name for clarity
                                'act': 'Vendor',
                                'class_rewards': unique_gems
                            }
                            formatted_data.append(quest_entry)
            
            # Save to file
            filename = f"data/vendor_rewards_{language}.json"
            os.makedirs("data", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(formatted_data)} vendor reward entries to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving vendor data for {language}: {e}")
            return False
    
    def load_vendor_data(self, language: str) -> Optional[List[Dict[str, Any]]]:
        """Load vendor reward data from JSON file"""
        try:
            filename = f"data/vendor_rewards_{language}.json"
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"Error loading vendor data for {language}: {e}")
            return None
    
    def is_data_outdated(self, language: str, max_age_hours: int = 168) -> bool:  # 1 week default
        """Check if vendor data is outdated"""
        try:
            filename = f"data/vendor_rewards_{language}.json"
            if not os.path.exists(filename):
                return True
            
            file_age = time.time() - os.path.getmtime(filename)
            max_age_seconds = max_age_hours * 3600
            
            return file_age > max_age_seconds
            
        except Exception as e:
            print(f"Error checking data age for {language}: {e}")
            return True
    
    def update_vendor_data(self, language: str, force_update: bool = False) -> bool:
        """Update vendor reward data for a specific language"""
        try:
            if not force_update and not self.is_data_outdated(language):
                print(f"Vendor data for {language} is up to date")
                return True
            
            print(f"Updating vendor data for {language}...")
            
            # Fetch vendor rewards from English PoE Wiki
            vendor_rewards = self.fetch_vendor_data()
            if not vendor_rewards:
                print(f"Failed to fetch vendor data")
                return False
            
            # Enrich with gem colors
            vendor_rewards = self.enrich_with_gem_colors(vendor_rewards, "en_US")
            
            # Translate if needed
            if language != "en_US":
                vendor_rewards = self.translate_gem_names(vendor_rewards, language)
            
            # Save data
            success = self.save_vendor_data(language, vendor_rewards)
            
            if success:
                print(f"Successfully updated vendor data for {language}")
            else:
                print(f"Failed to save vendor data for {language}")
            
            return success
            
        except Exception as e:
            print(f"Error updating vendor data for {language}: {e}")
            return False
    
    def update_all_languages(self, force_update: bool = False) -> Dict[str, bool]:
        """Update vendor reward data for all supported languages"""
        results = {}
        
        for language in ["en_US", "pt_BR"]:
            print(f"\n--- Updating {language} ---")
            results[language] = self.update_vendor_data(language, force_update)
            
            # Add delay between requests to be respectful
            if language != "pt_BR":  # Don't delay after the last one
                time.sleep(2)
        
        return results
    
    def get_vendor_rewards_for_class(self, language: str, character_class: str) -> List[Dict[str, Any]]:
        """Get vendor rewards for a specific character class"""
        try:
            vendor_data = self.load_vendor_data(language)
            if not vendor_data:
                return []
            
            # Filter rewards for the specific class
            class_rewards = []
            for quest in vendor_data:
                # Check if this quest entry is for the specified class
                quest_name = quest['name']
                if f"({character_class})" in quest_name:
                    # Remove the class suffix from the name for display
                    display_name = quest_name.replace(f" ({character_class})", "")
                    
                    quest_rewards = quest.get('class_rewards', [])
                    if quest_rewards:
                        class_rewards.append({
                            'name': display_name,
                            'act': quest['act'],
                            'class_rewards': quest_rewards
                        })
            
            return class_rewards
            
        except Exception as e:
            print(f"Error getting vendor rewards for {character_class} in {language}: {e}")
            return []


def main():
    """Test the vendor reward crawler"""
    crawler = VendorRewardCrawler()
    
    # Update data for all languages
    results = crawler.update_all_languages(force_update=True)
    
    print("\n--- Update Results ---")
    for language, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {language}: {'Success' if success else 'Failed'}")
    
    # Test loading data
    print("\n--- Testing Data Loading ---")
    for language in ["en_US", "pt_BR"]:
        data = crawler.load_vendor_data(language)
        if data:
            print(f"{language}: Loaded {len(data)} vendor reward quests")
            
            # Test class-specific data
            class_data = crawler.get_vendor_rewards_for_class(language, "Witch")
            print(f"  Witch rewards: {len(class_data)} quests")
        else:
            print(f"{language}: No data loaded")


if __name__ == "__main__":
    main() 