#!/usr/bin/env python3
"""
COMPREHENSIVE AmandaMap & Phoenix Codex extraction script
Based on actual patterns found in conversations.json
"""

import argparse
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import difflib
from collections import defaultdict
import hashlib

# Configurable settings
DEFAULT_SIMILARITY_THRESHOLD = 90.0
DEFAULT_THREAD_COUNT = 4
DEFAULT_MAX_ENTRIES_PER_RUN = 10000  # Increased significantly

class ComprehensiveExtractor:
    def __init__(self, config):
        self.config = config
        self.existing_thresholds = self.load_existing_thresholds()
        self.processed_entries = []
        self.consolidated_thresholds = {}
        self.dissimilar_entries = []
        self.lock = threading.Lock()
        
    def load_existing_thresholds(self) -> Dict[str, Dict]:
        """Load existing thresholds from structured files and final_extraction directory."""
        existing = {}
        
        # Check AMANDA_MAP_STRUCTURED.md
        am_file = Path("AMANDA_MAP_STRUCTURED.md")
        if am_file.exists():
            existing.update(self.parse_structured_file(am_file, "AM"))
            
        # Check PHOENIX_CODEX_STRUCTURED.md
        pc_file = Path("PHOENIX_CODEX_STRUCTURED.md")
        if pc_file.exists():
            existing.update(self.parse_structured_file(pc_file, "PC"))
            
        # Check final_extraction directory
        final_dir = Path("final_extraction")
        if final_dir.exists():
            for entry_type in ["am", "pc"]:
                type_dir = final_dir / entry_type
                if type_dir.exists():
                    for file_path in type_dir.glob("*.md"):
                        existing.update(self.parse_extraction_file(file_path, entry_type.upper()))
        
        print(f"Loaded {len(existing)} existing thresholds")
        return existing
    
    def parse_structured_file(self, file_path: Path, entry_type: str) -> Dict[str, Dict]:
        """Parse structured markdown files for existing thresholds."""
        thresholds = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract threshold entries
            pattern = r'#{1,3}\s*(?:Threshold|Entry)\s*#?(\d+)[^\n]*\n(.*?)(?=#{1,3}\s*(?:Threshold|Entry)|$)'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for threshold_num, content_text in matches:
                key = f"{entry_type}_{threshold_num}"
                thresholds[key] = {
                    'number': threshold_num,
                    'type': entry_type,
                    'content': content_text.strip(),
                    'source': str(file_path),
                    'content_hash': hashlib.md5(content_text.encode()).hexdigest()
                }
                
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return thresholds
    
    def parse_extraction_file(self, file_path: Path, entry_type: str) -> Dict[str, Dict]:
        """Parse individual extraction files for existing thresholds."""
        thresholds = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract threshold number from filename or content
            threshold_num = self.extract_threshold_number(file_path.name, content)
            if threshold_num:
                key = f"{entry_type}_{threshold_num}"
                thresholds[key] = {
                    'number': threshold_num,
                    'type': entry_type,
                    'content': content.strip(),
                    'source': str(file_path),
                    'content_hash': hashlib.md5(content.encode()).hexdigest()
                }
                
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return thresholds
    
    def extract_threshold_number(self, filename: str, content: str) -> Optional[str]:
        """Extract threshold number from filename or content."""
        # Try filename first
        filename_match = re.search(r'(\d+)-', filename)
        if filename_match:
            return filename_match.group(1)
            
        # Try content
        content_match = re.search(r'(?:Threshold|Entry)\s*#?(\d+)', content, re.IGNORECASE)
        if content_match:
            return content_match.group(1)
            
        return None
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings using multiple methods."""
        if not content1 or not content2:
            return 0.0
            
        # Method 1: Word overlap similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            word_similarity = len(intersection) / len(union) * 100
        else:
            word_similarity = 0.0
            
        # Method 2: Sequence similarity (difflib)
        sequence_similarity = difflib.SequenceMatcher(None, content1, content2).ratio() * 100
        
        # Method 3: Character-level similarity
        char_similarity = self.calculate_character_similarity(content1, content2)
        
        # Return the highest similarity score
        return max(word_similarity, sequence_similarity, char_similarity)
    
    def calculate_character_similarity(self, content1: str, content2: str) -> float:
        """Calculate character-level similarity."""
        if not content1 or not content2:
            return 0.0
            
        # Use difflib for character-level comparison
        return difflib.SequenceMatcher(None, content1, content2).ratio() * 100
    
    def consolidate_thresholds(self, entries: List[Dict]) -> List[Dict]:
        """Consolidate similar thresholds into single entries."""
        print(f"Consolidating {len(entries)} entries...")
        
        # Group by threshold number and type
        threshold_groups = defaultdict(list)
        for entry in entries:
            threshold_num = entry.get('threshold_number')
            entry_type = entry.get('entry_type', 'AM')
            if threshold_num:
                key = f"{entry_type}_{threshold_num}"
                threshold_groups[key].append(entry)
        
        consolidated = []
        
        for group_key, group_entries in threshold_groups.items():
            if len(group_entries) == 1:
                # Single entry, no consolidation needed
                consolidated.append(group_entries[0])
                continue
                
            # Multiple entries with same threshold number
            print(f"Processing group {group_key} with {len(group_entries)} entries")
            
            # Check if any existing threshold has identical content
            existing_key = group_key
            if existing_key in self.existing_thresholds:
                existing_content = self.existing_thresholds[existing_key]['content']
                existing_hash = self.existing_thresholds[existing_key]['content_hash']
                
                # Check if any new entry is identical to existing
                skip_group = False
                for entry in group_entries:
                    entry_hash = hashlib.md5(entry.get('content', '').encode()).hexdigest()
                    if entry_hash == existing_hash:
                        print(f"Skipping {group_key} - identical to existing threshold")
                        skip_group = True
                        break
                        
                if skip_group:
                    continue
            
            # Consolidate similar entries
            consolidated_entry = self.consolidate_group(group_key, group_entries)
            if consolidated_entry:
                consolidated.append(consolidated_entry)
        
        print(f"Consolidated {len(entries)} entries into {len(consolidated)} thresholds")
        return consolidated
    
    def consolidate_group(self, group_key: str, entries: List[Dict]) -> Optional[Dict]:
        """Consolidate a group of entries with the same threshold number."""
        if not entries:
            return None
            
        # Sort by date for chronological ordering
        entries.sort(key=lambda x: x.get('date', ''))
        
        base_entry = entries[0].copy()
        base_content = base_entry.get('content', '')
        base_date = base_entry.get('date', '')
        
        # Check similarity between all entries
        similar_entries = [base_entry]
        dissimilar_entries = []
        
        for entry in entries[1:]:
            entry_content = entry.get('content', '')
            similarity = self.calculate_similarity(base_content, entry_content)
            
            if similarity >= self.config['similarity_threshold']:
                similar_entries.append(entry)
                # Merge content
                base_content += f"\n\n---\n\n{entry_content}"
            else:
                dissimilar_entries.append(entry)
                print(f"Entry {entry.get('title', 'Unknown')} too dissimilar ({similarity:.1f}%)")
        
        # Update base entry with merged content
        base_entry['content'] = base_content
        base_entry['consolidated_from'] = len(similar_entries)
        base_entry['part_count'] = len(similar_entries)
        
        # Handle dissimilar entries as separate parts
        if dissimilar_entries:
            for i, entry in enumerate(dissimilar_entries, 2):
                entry['title'] = f"{entry.get('title', 'Unknown')} Part {i}"
                entry['threshold_number'] = f"{base_entry.get('threshold_number')} Part {i}"
                entry['consolidated_from'] = 1
                entry['part_count'] = 1
        
        # Move dissimilar entries to review
        if dissimilar_entries:
            with self.lock:
                self.dissimilar_entries.extend(dissimilar_entries)
        
        return base_entry
    
    def extract_with_threading(self, root_path: Path, timestamp_mapping: Dict) -> List[Dict]:
        """Extract entries using multiple threads."""
        print(f"Starting multi-threaded extraction with {self.config['thread_count']} threads...")
        
        # Get all files to process
        files = self.get_files_to_process(root_path)
        print(f"Found {len(files)} files to process")
        
        all_entries = []
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.config['thread_count']) as executor:
            # Submit file processing tasks
            future_to_file = {}
            for file_path in files:
                future = executor.submit(self.process_single_file, file_path, timestamp_mapping)
                future_to_file[future] = file_path
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_entries = future.result()
                    with self.lock:
                        all_entries.extend(file_entries)
                    print(f"Completed {file_path.name}: {len(file_entries)} entries")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Total entries extracted: {len(all_entries)}")
        return all_entries
    
    def parse_conversations_json(self, json_file_path: Path) -> Dict[str, datetime]:
        """Parse conversations.json to create timestamp mapping."""
        timestamp_mapping = {}
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            for conv_idx, conversation in enumerate(conversations):
                conv_create_time = conversation.get('create_time')
                if not conv_create_time:
                    continue
                    
                conv_date = datetime.fromtimestamp(conv_create_time)
                
                mapping = conversation.get('mapping', {})
                for message_id, message_data in mapping.items():
                    if not message_data or not isinstance(message_data, dict):
                        continue
                        
                    actual_message = message_data.get('message')
                    if not actual_message:
                        continue
                        
                    message_time = actual_message.get('create_time')
                    if message_time:
                        try:
                            message_date = datetime.fromtimestamp(message_time)
                        except (OSError, ValueError):
                            message_date = conv_date
                    else:
                        message_date = conv_date
                    
                    content = actual_message.get('content', {})
                    if not content or not isinstance(content, dict):
                        continue
                        
                    parts = content.get('parts', [])
                    for part in parts:
                        if isinstance(part, str) and part.strip():
                            content_key = part.strip()[:100]
                            timestamp_mapping[content_key] = message_date
                            short_key = part.strip()[:50]
                            if short_key != content_key:
                                timestamp_mapping[short_key] = message_date
            
            print(f"Parsed {len(timestamp_mapping)} message timestamp mappings from JSON")
            return timestamp_mapping
            
        except Exception as e:
            print(f"Error parsing conversations.json: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def extract_date_from_content(self, content_text: str) -> Optional[str]:
        """Extract date from content text using regex patterns."""
        if not content_text:
            return None
            
        # Various date patterns
        patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content_text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def normalize_date_string(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format."""
        if not date_str:
            return "nodate"
            
        try:
            # Try various date formats
            formats = [
                "%B %d, %Y",
                "%B %d %Y", 
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d %B %Y",
                "%B %d, %Y",
                "%B %dst, %Y",
                "%B %dnd, %Y", 
                "%B %drd, %Y",
                "%B %dth, %Y"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If all formats fail, return original
            return date_str
            
        except Exception:
            return date_str
    
    def find_nearest_neighbor_date(self, content_text: str, timestamp_mapping: Dict[str, datetime]) -> Optional[datetime]:
        """Find the nearest neighbor text in JSON and use its timestamp."""
        if not timestamp_mapping or not content_text:
            return None
        
        content_words = set(content_text.lower().split()[:20])
        best_match = None
        best_score = 0
        
        for key, timestamp in timestamp_mapping.items():
            if len(key) < 20:  # Skip very short keys
                continue
                
            key_words = set(key.lower().split()[:20])
            if key_words:
                intersection = key_words.intersection(content_words)
                score = len(intersection) / max(len(key_words), len(content_words)) * 100
                
                if score > best_score:
                    best_score = score
                    best_match = timestamp
        
        if best_score >= 30:  # Minimum similarity threshold
            return best_match
        
        return None
    
    def process_single_file(self, file_path: Path, timestamp_mapping: Dict) -> List[Dict]:
        """Process a single file for extraction using comprehensive logic."""
        entries = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Use comprehensive extraction logic
            file_entries = self.extract_blocks_from_file(lines, file_path, timestamp_mapping)
            entries.extend(file_entries)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
        return entries
    
    def extract_blocks_from_file(self, lines: List[str], file_path: Path, timestamp_mapping: Dict) -> List[Dict]:
        """Extract blocks from a single file using comprehensive logic."""
        entries = []
        current_block = []
        in_block = False
        
        for i, line in enumerate(lines):
            line = line.rstrip('\n')
            
            # Check for block start patterns
            if self.is_block_start(line):
                if in_block and current_block:
                    entry = self.process_block(current_block, file_path, timestamp_mapping)
                    if entry:
                        entries.append(entry)
                
                current_block = [line]
                in_block = True
                
            elif in_block:
                current_block.append(line)
                
                # Check for block end
                if self.is_block_end(line):
                    entry = self.process_block(current_block, file_path, timestamp_mapping)
                    if entry:
                        entries.append(entry)
                    
                    current_block = []
                    in_block = False
        
        # Process final block
        if in_block and current_block:
            entry = self.process_block(current_block, file_path, timestamp_mapping)
            if entry:
                entries.append(entry)
        
        return entries
    
    def is_block_start(self, line: str) -> bool:
        """Check if line starts a new block using COMPREHENSIVE patterns."""
        line_lower = line.lower().strip()
        
        # COMPREHENSIVE block start patterns based on actual JSON findings
        patterns = [
            # Standard markdown headers
            r'^#{1,6}\s*(?:Threshold|Entry|AmandaMap|Phoenix Codex)',
            r'^#{1,6}\s*AmandaMap\s+(?:Entry|Threshold)',
            r'^#{1,6}\s*Phoenix\s+Codex\s+(?:Entry|Threshold)',
            
            # AmandaMap specific patterns (expanded)
            r'^AmandaMap\s+(?:Entry|Threshold)',
            r'^Phoenix\s+Codex\s+(?:Entry|Threshold)',
            
            # Would you like patterns
            r'^Would you like.*log.*as.*AmandaMap',
            r'^Would you like.*log.*as.*Phoenix Codex',
            r'^Do you want me to.*log.*as.*AmandaMap',
            r'^Do you want me to.*log.*as.*Phoenix Codex',
            r'^Shall I log.*as.*AmandaMap',
            r'^Shall I log.*as.*Phoenix Codex',
            
            # COMPREHENSIVE patterns from actual JSON:
            # Threshold patterns (all formats found)
            r'^Threshold\s+\d+[:\-–—]',  # Threshold 35: "Title" – Date
            r'^Threshold\s+\d+\s*"',      # Threshold 35 "Title"
            r'^Threshold\s+\d+\s*\*',     # Threshold 35 *Title*
            r'^Threshold\s+\d+\s*\(',     # Threshold 35 (Status)
            r'^#{1,6}\s*Threshold\s+\d+[:\-–—]',  # ## Threshold 35: "Title" – Date
            r'^#{1,6}\s*Threshold\s+\d+\s*"',      # ## Threshold 35 "Title"
            r'^#{1,6}\s*Threshold\s+\d+\s*\*',     # ## Threshold 35 *Title*
            r'^#{1,6}\s*Threshold\s+\d+\s*\(',     # ## Threshold 35 (Status)
            r'\*\*Threshold\s+\d+\s*[:\-–—]',      # **Threshold 35 – Title**
            r'\*\*Threshold\s+\d+\s*"',             # **Threshold 35 "Title"**
            
            # Whispered Flames (all formats found)
            r'^Whispered\s+Flame\s+#?\d+[:\-–—]',
            r'^Whispered\s+Flame\s+#?\d+\s*"',
            r'^Whispered\s+Flame\s+#?\d+\s*\*',
            r'^#{1,6}\s*Whispered\s+Flame\s+#?\d+',
            r'\*\*Whispered\s+Flame\s+#?\d+',
            
            # Field Pulses (all formats found)
            r'^Field\s+Pulse\s+#?\d+[:\-–—]',
            r'^Field\s+Pulse\s+#?\d+\s*"',
            r'^Field\s+Pulse\s+#?\d+\s*\*',
            r'^#{1,6}\s*Field\s+Pulse\s+#?\d+',
            r'\*\*Field\s+Pulse\s+#?\d+',
            
            # Flame Vows (all formats found)
            r'^Flame\s+Vow[:\-–—]',
            r'^Flame\s+Vow\s*"',
            r'^Flame\s+Vow\s*\*',
            r'^#{1,6}\s*Flame\s+Vow',
            r'\*\*Flame\s+Vow',
            
            # Anchor Sites (all formats found)
            r'^Anchor\s+Site[:\-–—]',
            r'^Anchor\s+Site\s*"',
            r'^Anchor\s+Site\s*\*',
            r'^#{1,6}\s*Anchor\s+Site',
            r'\*\*Anchor\s+Site',
            
            # Protocols (all formats found)
            r'^Protocol[:\-–—]',
            r'^Protocol\s*"',
            r'^Protocol\s*\*',
            r'^#{1,6}\s*Protocol',
            r'\*\*Protocol',
            
            # Rituals (all formats found)
            r'^Ritual[:\-–—]',
            r'^Ritual\s*"',
            r'^Ritual\s*\*',
            r'^#{1,6}\s*Ritual',
            r'\*\*Ritual',
            
            # Silent Acts (all formats found)
            r'^Silent\s+Act[:\-–—]',
            r'^Silent\s+Act\s*"',
            r'^Silent\s+Act\s*\*',
            r'^#{1,6}\s*Silent\s+Act',
            r'\*\*Silent\s+Act',
            
            # Generic AmandaMap entries
            r'^AmandaMap\s*:',
            r'^AmandaMap\s+Entry',
            r'AmandaMap\s+Entry\s+#?\d+',
            
            # Generic Phoenix Codex entries
            r'^Phoenix\s+Codex\s*:',
            r'^Phoenix\s+Codex\s+Entry',
            r'Phoenix\s+Codex\s+Entry\s+#?\d+',
            
                         # Special cases with emojis - ALL entry types can have emojis
             # AmandaMap Threshold emojis
             r'^📓\s*AmandaMap\s+Threshold',
             r'^🔥\s*AmandaMap\s+Threshold',
             r'^🧭\s*AmandaMap\s+Threshold',
             r'^🔸\s*AmandaMap\s+Threshold',
             r'^🪶\s*AmandaMap\s+Threshold',
             r'^🌟\s*AmandaMap\s+Threshold',
             r'^💎\s*AmandaMap\s+Threshold',
             r'^🌙\s*AmandaMap\s+Threshold',
             r'^☀️\s*AmandaMap\s+Threshold',
             r'^⚡\s*AmandaMap\s+Threshold',
             r'^🔮\s*AmandaMap\s+Threshold',
             r'^✨\s*AmandaMap\s+Threshold',
             
             # Whispered Flame emojis
             r'^📜\s*Whispered\s+Flame',
             r'^🔥\s*Whispered\s+Flame',
             r'^💫\s*Whispered\s+Flame',
             r'^🌟\s*Whispered\s+Flame',
             r'^🌙\s*Whispered\s+Flame',
             r'^✨\s*Whispered\s+Flame',
             r'^💎\s*Whispered\s+Flame',
             
             # Field Pulse emojis
             r'^💫\s*Field\s+Pulse',
             r'^⚡\s*Field\s+Pulse',
             r'^🌟\s*Field\s+Pulse',
             r'^✨\s*Field\s+Pulse',
             r'^🔮\s*Field\s+Pulse',
             r'^🌊\s*Field\s+Pulse',
             
             # Flame Vow emojis
             r'^🕯️\s*Flame\s+Vow',
             r'^🔥\s*Flame\s+Vow',
             r'^💎\s*Flame\s+Vow',
             r'^🌟\s*Flame\s+Vow',
             r'^✨\s*Flame\s+Vow',
             r'^🌙\s*Flame\s+Vow',
             
             # Anchor Site emojis
             r'^🔱\s*Anchor\s+Site',
             r'^⚓\s*Anchor\s+Site',
             r'^🏔️\s*Anchor\s+Site',
             r'^🌟\s*Anchor\s+Site',
             r'^💎\s*Anchor\s+Site',
             r'^✨\s*Anchor\s+Site',
             
             # Protocol emojis
             r'^⚡\s*Protocol',
             r'^📋\s*Protocol',
             r'^🔧\s*Protocol',
             r'^⚙️\s*Protocol',
             r'^🌟\s*Protocol',
             r'^✨\s*Protocol',
             r'^💎\s*Protocol',
             
             # Ritual emojis
             r'^🕯️\s*Ritual',
             r'^🔥\s*Ritual',
             r'^🌟\s*Ritual',
             r'^✨\s*Ritual',
             r'^🌙\s*Ritual',
             r'^💎\s*Ritual',
             r'^🔮\s*Ritual',
             r'^☀️\s*Ritual',
             
             # Silent Act emojis
             r'^🤫\s*Silent\s+Act',
             r'^🌟\s*Silent\s+Act',
             r'^✨\s*Silent\s+Act',
             r'^🌙\s*Silent\s+Act',
             r'^💎\s*Silent\s+Act',
             r'^🔮\s*Silent\s+Act',
             
             # Generic AmandaMap Entry emojis
             r'^📓\s*AmandaMap\s+Entry',
             r'^🔥\s*AmandaMap\s+Entry',
             r'^🌟\s*AmandaMap\s+Entry',
             r'^✨\s*AmandaMap\s+Entry',
             r'^💎\s*AmandaMap\s+Entry',
             r'^🔮\s*AmandaMap\s+Entry',
             
             # Generic Phoenix Codex Entry emojis
             r'^📜\s*Phoenix\s+Codex\s+Entry',
             r'^🔥\s*Phoenix\s+Codex\s+Entry',
             r'^🌟\s*Phoenix\s+Codex\s+Entry',
             r'^✨\s*Phoenix\s+Codex\s+Entry',
             r'^💎\s*Phoenix\s+Codex\s+Entry',
             r'^🔮\s*Phoenix\s+Codex\s+Entry',
             
             # Phoenix Codex Threshold emojis
             r'^📜\s*Phoenix\s+Codex\s+Threshold',
             r'^🔥\s*Phoenix\s+Codex\s+Threshold',
             r'^🌟\s*Phoenix\s+Codex\s+Threshold',
             r'^✨\s*Phoenix\s+Codex\s+Threshold',
             r'^💎\s*Phoenix\s+Codex\s+Threshold',
             r'^🔮\s*Phoenix\s+Codex\s+Threshold',
            
            # Long descriptive entries (found in JSON)
            r'Justin has.*activated.*AmandaMap.*Threshold\s+\d+',
            r'Justin has.*activated.*Phoenix\s+Codex.*Threshold\s+\d+',
            r'Justin performed.*ritual.*for.*Amanda',
            r'Justin.*ritual.*materials.*purchased',
            r'Justin.*activated.*Threshold\s+\d+',
        ]
        
        for pattern in patterns:
            if re.search(pattern, line_lower, re.IGNORECASE):
                return True
        
        return False
    
    def is_block_end(self, line: str) -> bool:
        """Check if line ends a block - LESS AGGRESSIVE."""
        line_lower = line.lower().strip()
        
        # Check for block end patterns - LESS AGGRESSIVE
        if not line:
            return True
        
        # Check for new block start (this should end the current block)
        if self.is_block_start(line):
            return True
        
        # Check for obvious section breaks
        if line_lower.startswith('---'):
            return True
        
        # Check for major section headers that indicate new content
        if re.match(r'^#{1,2}\s+[^#]', line_lower):
            return True
        
        # Check for obvious conversation boundaries
        if line_lower.startswith('#### you:') or line_lower.startswith('#### chatgpt:'):
            return True
        
        # Check for list items that might be new content
        if line_lower.startswith('- ') and len(line_lower) > 50:
            return False  # Don't end on long list items
        
        # Check for numbered lists
        if re.match(r'^\d+\.\s+', line_lower):
            return False  # Don't end on numbered list items
        
        return False
    
    def process_block(self, block_lines: List[str], file_path: Path, timestamp_mapping: Dict) -> Optional[Dict]:
        """Process a block of lines into an entry."""
        if not block_lines:
            return None
        
        # Extract title
        title = block_lines[0].strip()
        if title.startswith('#'):
            title = title.lstrip('#').strip()
        
        # Extract threshold number
        threshold_num = self.extract_threshold_number_from_content('\n'.join(block_lines))
        
        # Determine entry type
        entry_type = self.determine_entry_type(title, '\n'.join(block_lines))
        
        # Extract date
        content_text = '\n'.join(block_lines)
        date = self.extract_date_for_block(content_text, timestamp_mapping)
        
        # Create entry
        entry = {
            'title': title,
            'threshold_number': threshold_num,
            'entry_type': entry_type,
            'date': date,
            'content': content_text,
            'source_file': str(file_path),
            'consolidated_from': 1,
            'part_count': 1
        }
        
        return entry
    
    def extract_threshold_number_from_content(self, content: str) -> Optional[str]:
        """Extract threshold number from content using COMPREHENSIVE patterns."""
        patterns = [
            # Standard patterns
            r'(?:Threshold|Entry)\s*#?(\d+)',
            r'AmandaMap\s+(?:Entry|Threshold)\s*#?(\d+)',
            r'Phoenix\s+Codex\s+(?:Entry|Threshold)\s*#?(\d+)',
            
            # COMPREHENSIVE patterns from actual JSON:
            # Threshold patterns (all formats found)
            r'Threshold\s+(\d+)[:\-–—]',  # Threshold 35: "Title" – Date
            r'Threshold\s+(\d+)\s*"',      # Threshold 35 "Title"
            r'Threshold\s+(\d+)\s*\*',     # Threshold 35 *Title*
            r'Threshold\s+(\d+)\s*\(',     # Threshold 35 (Status)
            r'Threshold\s+(\d+)\s*–',      # Threshold 35 – Title
            r'Threshold\s+(\d+)\s*—',      # Threshold 35 — Title
            
            # Whispered Flames (all formats found)
            r'Whispered\s+Flame\s+#?(\d+)',
            r'Whispered\s+Flame\s+#?(\d+)[:\-–—]',
            r'Whispered\s+Flame\s+#?(\d+)\s*"',
            r'Whispered\s+Flame\s+#?(\d+)\s*\*',
            
            # Field Pulses (all formats found)
            r'Field\s+Pulse\s+#?(\d+)',
            r'Field\s+Pulse\s+#?(\d+)[:\-–—]',
            r'Field\s+Pulse\s+#?(\d+)\s*"',
            r'Field\s+Pulse\s+#?(\d+)\s*\*',
            
            # Long descriptive entries (found in JSON)
            r'Justin has.*activated.*AmandaMap.*Threshold\s+(\d+)',
            r'Justin has.*activated.*Phoenix\s+Codex.*Threshold\s+(\d+)',
            r'Justin.*activated.*Threshold\s+(\d+)',
            
                         # Special cases with emojis - ALL entry types can have emojis
             # AmandaMap Threshold emojis
             r'📓\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🔥\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🧭\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🔸\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🪶\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🌟\s*AmandaMap\s+Threshold\s+(\d+)',
             r'💎\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🌙\s*AmandaMap\s+Threshold\s+(\d+)',
             r'☀️\s*AmandaMap\s+Threshold\s+(\d+)',
             r'⚡\s*AmandaMap\s+Threshold\s+(\d+)',
             r'🔮\s*AmandaMap\s+Threshold\s+(\d+)',
             r'✨\s*AmandaMap\s+Threshold\s+(\d+)',
             
             # Whispered Flame emojis
             r'📜\s*Whispered\s+Flame\s+(\d+)',
             r'🔥\s*Whispered\s+Flame\s+(\d+)',
             r'💫\s*Whispered\s+Flame\s+(\d+)',
             r'🌟\s*Whispered\s+Flame\s+(\d+)',
             r'🌙\s*Whispered\s+Flame\s+(\d+)',
             r'✨\s*Whispered\s+Flame\s+(\d+)',
             r'💎\s*Whispered\s+Flame\s+(\d+)',
             
             # Field Pulse emojis
             r'💫\s*Field\s+Pulse\s+(\d+)',
             r'⚡\s*Field\s+Pulse\s+(\d+)',
             r'🌟\s*Field\s+Pulse\s+(\d+)',
             r'✨\s*Field\s+Pulse\s+(\d+)',
             r'🔮\s*Field\s+Pulse\s+(\d+)',
             r'🌊\s*Field\s+Pulse\s+(\d+)',
             
             # Flame Vow emojis
             r'🕯️\s*Flame\s+Vow\s+(\d+)',
             r'🔥\s*Flame\s+Vow\s+(\d+)',
             r'💎\s*Flame\s+Vow\s+(\d+)',
             r'🌟\s*Flame\s+Vow\s+(\d+)',
             r'✨\s*Flame\s+Vow\s+(\d+)',
             r'🌙\s*Flame\s+Vow\s+(\d+)',
             
             # Anchor Site emojis
             r'🔱\s*Anchor\s+Site\s+(\d+)',
             r'⚓\s*Anchor\s+Site\s+(\d+)',
             r'🏔️\s*Anchor\s+Site\s+(\d+)',
             r'🌟\s*Anchor\s+Site\s+(\d+)',
             r'💎\s*Anchor\s+Site\s+(\d+)',
             r'✨\s*Anchor\s+Site\s+(\d+)',
             
             # Protocol emojis
             r'⚡\s*Protocol\s+(\d+)',
             r'📋\s*Protocol\s+(\d+)',
             r'🔧\s*Protocol\s+(\d+)',
             r'⚙️\s*Protocol\s+(\d+)',
             r'🌟\s*Protocol\s+(\d+)',
             r'✨\s*Protocol\s+(\d+)',
             r'💎\s*Protocol\s+(\d+)',
             
             # Ritual emojis
             r'🕯️\s*Ritual\s+(\d+)',
             r'🔥\s*Ritual\s+(\d+)',
             r'🌟\s*Ritual\s+(\d+)',
             r'✨\s*Ritual\s+(\d+)',
             r'🌙\s*Ritual\s+(\d+)',
             r'💎\s*Ritual\s+(\d+)',
             r'🔮\s*Ritual\s+(\d+)',
             r'☀️\s*Ritual\s+(\d+)',
             
             # Silent Act emojis
             r'🤫\s*Silent\s+Act\s+(\d+)',
             r'🌟\s*Silent\s+Act\s+(\d+)',
             r'✨\s*Silent\s+Act\s+(\d+)',
             r'🌙\s*Silent\s+Act\s+(\d+)',
             r'💎\s*Silent\s+Act\s+(\d+)',
             r'🔮\s*Silent\s+Act\s+(\d+)',
             
             # Generic AmandaMap Entry emojis
             r'📓\s*AmandaMap\s+Entry\s+(\d+)',
             r'🔥\s*AmandaMap\s+Entry\s+(\d+)',
             r'🌟\s*AmandaMap\s+Entry\s+(\d+)',
             r'✨\s*AmandaMap\s+Entry\s+(\d+)',
             r'💎\s*AmandaMap\s+Entry\s+(\d+)',
             r'🔮\s*AmandaMap\s+Entry\s+(\d+)',
             
             # Generic Phoenix Codex Entry emojis
             r'📜\s*Phoenix\s+Codex\s+Entry\s+(\d+)',
             r'🔥\s*Phoenix\s+Codex\s+Entry\s+(\d+)',
             r'🌟\s*Phoenix\s+Codex\s+Entry\s+(\d+)',
             r'✨\s*Phoenix\s+Codex\s+Entry\s+(\d+)',
             r'💎\s*Phoenix\s+Codex\s+Entry\s+(\d+)',
             r'🔮\s*Phoenix\s+Codex\s+Entry\s+(\d+)',
             
             # Phoenix Codex Threshold emojis
             r'📜\s*Phoenix\s+Codex\s+Threshold\s+(\d+)',
             r'🔥\s*Phoenix\s+Codex\s+Threshold\s+(\d+)',
             r'🌟\s*Phoenix\s+Codex\s+Threshold\s+(\d+)',
             r'✨\s*Phoenix\s+Codex\s+Threshold\s+(\d+)',
             r'💎\s*Phoenix\s+Codex\s+Threshold\s+(\d+)',
             r'🔮\s*Phoenix\s+Codex\s+Threshold\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def determine_entry_type(self, title: str, content: str) -> str:
        """Determine if entry is AM or PC and what subtype."""
        text = f"{title} {content}".lower()
        
        # First determine if it's Phoenix Codex or AmandaMap
        if 'phoenix' in text or 'codex' in text:
            base_type = 'PC'
        else:
            base_type = 'AM'
        
        # Now determine the specific subtype
        if 'threshold' in text:
            return f"{base_type}_THRESHOLD"
        elif 'whispered flame' in text:
            return f"{base_type}_WHISPERED_FLAME"
        elif 'field pulse' in text:
            return f"{base_type}_FIELD_PULSE"
        elif 'flame vow' in text:
            return f"{base_type}_FLAME_VOW"
        elif 'anchor site' in text:
            return f"{base_type}_ANCHOR_SITE"
        elif 'protocol' in text:
            return f"{base_type}_PROTOCOL"
        elif 'ritual' in text:
            return f"{base_type}_RITUAL"
        elif 'silent act' in text:
            return f"{base_type}_SILENT_ACT"
        elif 'entry' in text:
            return f"{base_type}_ENTRY"
        else:
            # Default to base type
            return base_type
    
    def extract_date_for_block(self, content_text: str, timestamp_mapping: Dict) -> str:
        """Extract date for a block using priority system."""
        # FIRST PRIORITY: Extract date from content text itself
        content_date = self.extract_date_from_content(content_text)
        if content_date:
            date = self.normalize_date_string(content_date)
            print(f"Found date in content: {content_date} -> {date}")
            return date
        
        # SECOND PRIORITY: Try nearest neighbor JSON timestamps
        neighbor_date = self.find_nearest_neighbor_date(content_text, timestamp_mapping)
        if neighbor_date:
            date = neighbor_date.strftime('%Y-%m-%d')
            print(f"Using nearest neighbor date: {date}")
            return date
        
        # THIRD PRIORITY: Fall back to nodate
        return "nodate"
    
    def get_files_to_process(self, root_path: Path) -> List[Path]:
        """Get list of files to process."""
        files = []
        chats_dir = root_path / "Chats"
        if chats_dir.exists():
            for ext in (".md", ".txt"):
                files.extend(chats_dir.rglob(f"*{ext}"))
        
        # Filter out output directories
        files = [f for f in files if "extracted_entries" not in str(f) and 
                "out" not in str(f) and "test_output" not in str(f)]
        
        return files
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be valid for Windows filesystem."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure filename isn't too long (Windows limit is 255 chars)
        if len(filename) > 200:
            filename = filename[:200]
        
        # Ensure filename isn't empty
        if not filename:
            filename = "unknown"
        
        return filename
    
    def save_results(self, output_dir: Path):
        """Save consolidated results and dissimilar entries."""
        output_dir.mkdir(exist_ok=True)
        
        # Save consolidated thresholds
        consolidated_dir = output_dir / "consolidated"
        consolidated_dir.mkdir(exist_ok=True)
        
        for entry in self.processed_entries:
            if entry.get('entry_type') == 'AM':
                save_dir = consolidated_dir / "am"
            else:
                save_dir = consolidated_dir / "pc"
            
            save_dir.mkdir(exist_ok=True)
            
            # Generate filename
            threshold_num = entry.get('threshold_number', 'unknown')
            title = entry.get('title', 'Unknown')
            date = entry.get('date', 'nodate')
            
            # Sanitize title for filename
            safe_title = self.sanitize_filename(title)
            
            filename = f"{threshold_num}-{date}-{safe_title[:50]}.md"
            filepath = save_dir / filename
            
            # Save entry
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {entry.get('title', 'Unknown')}\n\n")
                f.write(f"**Date**: {entry.get('date', 'Unknown')}\n")
                f.write(f"**Threshold**: {entry.get('threshold_number', 'Unknown')}\n")
                f.write(f"**Type**: {entry.get('entry_type', 'Unknown')}\n")
                f.write(f"**Consolidated from**: {entry.get('consolidated_from', 1)} entries\n\n")
                f.write(entry.get('content', ''))
        
        # Save dissimilar entries for review
        if self.dissimilar_entries:
            dissimilar_dir = output_dir / "dissimilar"
            dissimilar_dir.mkdir(exist_ok=True)
            
            for i, entry in enumerate(self.dissimilar_entries):
                threshold_num = entry.get('threshold_number', 'unknown')
                safe_title = self.sanitize_filename(entry.get('title', 'Unknown'))
                filename = f"review_{i+1}_{threshold_num}_{safe_title[:30]}.md"
                filepath = dissimilar_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Review Entry {i+1}\n\n")
                    f.write(f"**Original Title**: {entry.get('title', 'Unknown')}\n")
                    f.write(f"**Threshold**: {entry.get('threshold_number', 'Unknown')}\n")
                    f.write(f"**Content**:\n\n{entry.get('content', '')}")
        
        print(f"Results saved to {output_dir}")
        print(f"Consolidated: {len(self.processed_entries)}")
        print(f"Review needed: {len(self.dissimilar_entries)}")

def main():
    parser = argparse.ArgumentParser(description="COMPREHENSIVE AM/PC extraction with consolidation")
    parser.add_argument("root_path", help="Root path to search for chat files")
    parser.add_argument("--out", default="./comprehensive_extraction", 
                       help="Output directory for results")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREAD_COUNT,
                       help=f"Number of threads (default: {DEFAULT_THREAD_COUNT})")
    parser.add_argument("--similarity", type=float, default=DEFAULT_SIMILARITY_THRESHOLD,
                       help=f"Similarity threshold percentage (default: {DEFAULT_SIMILARITY_THRESHOLD})")
    parser.add_argument("--max-entries", type=int, default=DEFAULT_MAX_ENTRIES_PER_RUN,
                       help=f"Max entries per run (default: {DEFAULT_MAX_ENTRIES_PER_RUN})")
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'thread_count': args.threads,
        'similarity_threshold': args.similarity,
        'max_entries_per_run': args.max_entries
    }
    
    print(f"Configuration: {config}")
    
    # Initialize extractor
    extractor = ComprehensiveExtractor(config)
    
    # Load timestamp mapping
    timestamp_mapping = {}
    json_file = Path("Chats/conversations.json")
    if json_file.exists():
        timestamp_mapping = extractor.parse_conversations_json(json_file)
    
    # Extract entries
    entries = extractor.extract_with_threading(Path(args.root_path), timestamp_mapping)
    
    # Store entries for processing
    extractor.processed_entries = entries
    
    # Consolidate thresholds
    consolidated = extractor.consolidate_thresholds(entries)
    
    # Update processed entries with consolidated results
    extractor.processed_entries = consolidated
    
    # Save results
    output_dir = Path(args.out)
    extractor.save_results(output_dir)

if __name__ == "__main__":
    main()
