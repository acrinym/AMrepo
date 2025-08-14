#!/usr/bin/env python3
"""
FULL CONVERSATION RITUAL EXTRACTION SCRIPT
Extracts COMPLETE ritual conversations, not just individual message parts
NO SUMMARIZATION - FULL DETAILS ONLY
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import hashlib
from collections import defaultdict

class FullConversationRitualExtractor:
    def __init__(self):
        self.ritual_conversations = []
        
    def extract_full_conversation_rituals(self, json_file_path: Path):
        """Extract COMPLETE ritual conversations, not just message parts."""
        print(f"Extracting FULL CONVERSATION ritual content from {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return
            
        print(f"Processing {len(data)} conversations...")
        
        for conv_idx, conversation in enumerate(data):
            if conv_idx % 100 == 0:
                print(f"Processing conversation {conv_idx + 1}/{len(data)}")
                
            # Check if this conversation contains ritual content
            if self._conversation_has_ritual_content(conversation):
                # Extract the ENTIRE conversation content
                full_content = self._extract_full_conversation_content(conversation)
                if full_content:
                    self.ritual_conversations.append({
                        'conversation_id': conversation.get('conversation_id', f'conv_{conv_idx}'),
                        'full_content': full_content,
                        'message_count': len(conversation.get('mapping', {})),
                        'ritual_keywords_found': self._count_ritual_keywords(full_content)
                    })
        
        print(f"\nFound {len(self.ritual_conversations)} conversations with ritual content")
        
    def _conversation_has_ritual_content(self, conversation: Dict) -> bool:
        """Check if conversation contains ACTUAL ritual instructions, not just magical words."""
        mapping = conversation.get('mapping', {})
        
        # Track magical content with scoring system
        magical_score = 0
        required_score = 8  # Must have significant magical content
        
        for msg_data in mapping.values():
            if not msg_data or not msg_data.get('message') or not msg_data['message'].get('content'):
                continue
                
            content = msg_data['message']['content']
            if 'parts' not in content:
                continue
                
            for part in content['parts']:
                if isinstance(part, str):
                    part_lower = part.lower()
                    
                    # HIGH CONFIDENCE MAGICAL PATTERNS (3 points each)
                    high_confidence_patterns = [
                        r'\b(?:ritual|spell|working|ceremony|rite)\b',
                        r'\b(?:invocation|evocation|conjuration)\b',
                        r'\b(?:magic|magical|witchcraft|occult)\b'
                    ]
                    
                    for pattern in high_confidence_patterns:
                        if re.search(pattern, part_lower):
                            magical_score += 3
                    
                    # MEDIUM CONFIDENCE PATTERNS (2 points each) - must be in magical context
                    if magical_score >= 3:  # Only check these if we already have magical language
                        medium_patterns = [
                            # Spirits/entities (explicitly magical)
                            r'\b(?:spirits?|entities?|servitors?|demons?|angels?|gods?|zepar|vassago|lucifer|seere|balam|foras|sitri)\b',
                            # Magical tools (explicitly magical)
                            r'\b(?:altar|circle|temple|sacred space|sanctuary)\b',
                            # Magical actions (explicitly magical)
                            r'\b(?:invoke|evoke|summon|banish|bind|cleanse|purify|consecrate)\b',
                            # Magical timing (explicitly magical)
                            r'\b(?:new moon|full moon|waxing|waning|dawn|dusk|midnight|noon)\b',
                            # Magical protection (explicitly magical)
                            r'\b(?:banishment|protection|warding|shielding|lbrp|lesser banishing ritual)\b'
                        ]
                        
                        for pattern in medium_patterns:
                            if re.search(pattern, part_lower):
                                magical_score += 2
                    
                    # LOW CONFIDENCE PATTERNS (1 point each) - only if we have strong magical context
                    if magical_score >= 6:  # Only check these if we already have strong magical content
                        low_patterns = [
                            # Step-by-step instructions
                            r'\b(?:step \d+|first|second|third|finally|next|then)\b',
                            # Materials (only in magical context)
                            r'\b(?:candles?|herbs?|crystals?|oils?|powders?|stones?|salt|thread|photo|mirror)\b',
                            # Actions (only in magical context)
                            r'\b(?:burn|light|bury|dispose|anoint|mix|combine|place|position|hold)\b',
                            # Visualization (only in magical context)
                            r'\b(?:visualize|focus|intend|declare|vow|promise)\b'
                        ]
                        
                        for pattern in low_patterns:
                            if re.search(pattern, part_lower):
                                magical_score += 1
                    
                    # If we've reached the required score, we can stop checking
                    if magical_score >= required_score:
                        break
        
        # Only return True if we have significant magical content
        return magical_score >= required_score
    
    def _extract_full_conversation_content(self, conversation: Dict) -> str:
        """Extract the COMPLETE conversation content, not just individual messages."""
        mapping = conversation.get('mapping', {})
        if not mapping:
            return ""
            
        # Sort messages by their order in the conversation
        sorted_messages = []
        for msg_id, msg_data in mapping.items():
            if msg_data and msg_data.get('message'):
                msg = msg_data['message']
                if 'content' in msg and 'parts' in msg['content']:
                    # Get the timestamp for ordering - handle None values
                    timestamp = msg.get('create_time')
                    if timestamp is None:
                        timestamp = 0.0  # Default timestamp for messages without time
                    sorted_messages.append((timestamp, msg_id, msg))
        
        # Sort by timestamp
        sorted_messages.sort(key=lambda x: x[0])
        
        # Build the full conversation content
        full_content = []
        for timestamp, msg_id, msg in sorted_messages:
            role = msg.get('author', {}).get('role', 'unknown')
            content = msg.get('content', {})
            
            if 'parts' in content:
                for part in content['parts']:
                    if isinstance(part, str) and part.strip():
                        full_content.append(f"**{role.upper()}**: {part.strip()}")
        
        return "\n\n".join(full_content)
    
    def _count_ritual_keywords(self, content: str) -> int:
        """Count ritual keywords in the content."""
        ritual_keywords = [
            'ingredients', 'materials', 'tools', 'supplies', 'step', 'first', 'second', 'third',
            'burn', 'light', 'bury', 'dispose', 'anoint', 'consecrate', 'mix', 'combine',
            'visualize', 'focus', 'intend', 'declare', 'vow', 'promise', 'moon', 'dawn', 'dusk',
            'spirits', 'entities', 'servitors', 'demons', 'angels', 'gods', 'candles', 'herbs',
            'crystals', 'oils', 'powders', 'stones', 'banishment', 'protection', 'summoning',
            'binding', 'cleansing', 'purification', 'altar', 'circle', 'sacred', 'space', 'temple'
        ]
        
        count = 0
        content_lower = content.lower()
        for keyword in ritual_keywords:
            if keyword in content_lower:
                count += 1
                
        return count
    
    def save_full_conversation_rituals(self, output_dir: Path):
        """Save COMPLETE ritual conversations with NO summarization."""
        output_dir.mkdir(exist_ok=True)
        
        # Create index file
        index_content = "# FULL CONVERSATION RITUAL EXTRACTION INDEX\n\n"
        index_content += f"**Total Ritual Conversations**: {len(self.ritual_conversations)}\n"
        index_content += f"**Extraction Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        index_content += "## Complete Ritual Conversations\n\n"
        index_content += "**These contain the FULL conversation content - NO SUMMARIZATION**\n\n"
        
        for i, ritual in enumerate(self.ritual_conversations, 1):
            # Generate filename - much more aggressive sanitization
            content_preview = ritual['full_content'][:100].replace('\n', ' ').replace('**', '')
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', content_preview)
            safe_filename = re.sub(r'_+', '_', safe_filename)
            safe_filename = safe_filename[:100]  # Limit length
            
            filename = f"ritual_{i:03d}_{datetime.now().strftime('%Y-%m-%d')}_{safe_filename}.md"
            
            # Create the ritual file
            ritual_content = f"# Complete Ritual Conversation {i}\n\n"
            ritual_content += f"**Conversation ID**: {ritual['conversation_id']}\n"
            ritual_content += f"**Total Messages**: {ritual['message_count']}\n"
            ritual_content += f"**Ritual Keywords Found**: {ritual['ritual_keywords_found']}\n"
            ritual_content += f"**Extraction Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            ritual_content += "---\n\n"
            ritual_content += "## FULL CONVERSATION CONTENT\n\n"
            ritual_content += "**NO SUMMARIZATION - COMPLETE DETAILS BELOW**\n\n"
            ritual_content += ritual['full_content']
            
            # Save the file
            file_path = output_dir / filename
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(ritual_content)
                print(f"Saved: {filename}")
            except Exception as e:
                print(f"Error saving {filename}: {e}")
        
        # Save the index
        index_path = output_dir / "00_RITUAL_CONVERSATIONS_INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"\nSaved {len(self.ritual_conversations)} ritual conversation files")
        print(f"Index saved to: {index_path}")

def main():
    extractor = FullConversationRitualExtractor()
    
    # Extract from conversations.json
    json_path = Path("Chats/conversations.json")
    if not json_path.exists():
        print("Error: conversations.json not found!")
        return
        
    extractor.extract_full_conversation_rituals(json_path)
    
    # Save the results
    output_dir = Path("full_ritual_conversations")
    extractor.save_full_conversation_rituals(output_dir)

if __name__ == "__main__":
    main()
