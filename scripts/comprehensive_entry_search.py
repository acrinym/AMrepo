#!/usr/bin/env python3
"""
Comprehensive search script to find ALL AmandaMap and Phoenix Codex entry types
in the conversations.json file.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def search_conversations_json():
    """Search conversations.json for all entry types."""
    
    json_file = Path("Chats/conversations.json")
    if not json_file.exists():
        print("conversations.json not found!")
        return
    
    print("Searching conversations.json for all entry types...")
    
    # Entry type patterns to search for
    entry_patterns = {
        # AmandaMap patterns
        'amandamap_threshold': [
            r'AmandaMap\s+Threshold\s+#?\d+',
            r'Threshold\s+#?\d+.*AmandaMap',
            r'#{1,3}\s*AmandaMap\s+Threshold\s+#?\d+',
        ],
        'amandamap_entry': [
            r'AmandaMap\s+Entry\s+#?\d+',
            r'Entry\s+#?\d+.*AmandaMap',
            r'#{1,3}\s*AmandaMap\s+Entry\s+#?\d+',
        ],
        'whispered_flame': [
            r'Whispered\s+Flame\s+#?\d+',
            r'#{1,3}\s*Whispered\s+Flame\s+#?\d+',
        ],
        'field_pulse': [
            r'Field\s+Pulse\s+#?\d+',
            r'#{1,3}\s*Field\s+Pulse\s+#?\d+',
        ],
        'flame_vow': [
            r'Flame\s+Vow',
            r'#{1,3}\s*Flame\s+Vow',
        ],
        'anchor_site': [
            r'Anchor\s+Site',
            r'#{1,3}\s*Anchor\s+Site',
        ],
        'protocol': [
            r'Protocol',
            r'#{1,3}\s*Protocol',
        ],
        'ritual': [
            r'Ritual',
            r'#{1,3}\s*Ritual',
        ],
        'silent_act': [
            r'Silent\s+Act',
            r'#{1,3}\s*Silent\s+Act',
        ],
        
        # Phoenix Codex patterns
        'phoenix_codex_threshold': [
            r'Phoenix\s+Codex\s+Threshold\s+#?\d+',
            r'#{1,3}\s*Phoenix\s+Codex\s+Threshold\s+#?\d+',
        ],
        'phoenix_codex_entry': [
            r'Phoenix\s+Codex\s+Entry\s+#?\d+',
            r'#{1,3}\s*Phoenix\s+Codex\s+Entry\s+#?\d+',
        ],
        
        # "Would you like me to" patterns
        'would_you_like': [
            r'Would you like me to.*log.*as.*AmandaMap',
            r'Would you like me to.*log.*as.*Phoenix Codex',
            r'Would you like me to.*log.*as.*Threshold',
            r'Would you like me to.*log.*as.*Entry',
            r'Would you like me to.*log.*as.*Whispered Flame',
            r'Would you like me to.*log.*as.*Field Pulse',
            r'Would you like me to.*log.*as.*Flame Vow',
            r'Would you like me to.*log.*as.*Anchor Site',
            r'Would you like me to.*log.*as.*Protocol',
            r'Would you like me to.*log.*as.*Ritual',
            r'Would you like me to.*log.*as.*Silent Act',
        ],
        
        # Other variations
        'shall_i_log': [
            r'Shall I log.*as.*AmandaMap',
            r'Shall I log.*as.*Phoenix Codex',
        ],
        'do_you_want_me_to': [
            r'Do you want me to.*log.*as.*AmandaMap',
            r'Do you want me to.*log.*as.*Phoenix Codex',
        ],
    }
    
    # Results storage
    results = defaultdict(list)
    total_entries = 0
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        print(f"Loaded {len(conversations)} conversations")
        
        for conv_idx, conversation in enumerate(conversations):
            mapping = conversation.get('mapping', {})
            
            for message_id, message_data in mapping.items():
                if not message_data or not isinstance(message_data, dict):
                    continue
                    
                actual_message = message_data.get('message')
                if not actual_message:
                    continue
                    
                content = actual_message.get('content', {})
                if not content or not isinstance(content, dict):
                    continue
                    
                parts = content.get('parts', [])
                for part in parts:
                    if isinstance(part, str) and part.strip():
                        content_text = part.strip()
                        
                        # Search for each pattern type
                        for entry_type, patterns in entry_patterns.items():
                            for pattern in patterns:
                                matches = re.finditer(pattern, content_text, re.IGNORECASE)
                                for match in matches:
                                    # Get context around the match
                                    start = max(0, match.start() - 100)
                                    end = min(len(content_text), match.end() + 100)
                                    context = content_text[start:end]
                                    
                                    results[entry_type].append({
                                        'conversation': conv_idx,
                                        'message_id': message_id,
                                        'match': match.group(0),
                                        'context': context,
                                        'full_content': content_text[:500] + "..." if len(content_text) > 500 else content_text
                                    })
                                    total_entries += 1
        
        # Print results summary
        print(f"\n{'='*60}")
        print("COMPREHENSIVE ENTRY SEARCH RESULTS")
        print(f"{'='*60}")
        print(f"Total entries found: {total_entries}")
        print()
        
        for entry_type, entries in results.items():
            print(f"{entry_type.upper().replace('_', ' ')}: {len(entries)} entries")
            if entries:
                print("  Examples:")
                for i, entry in enumerate(entries[:3]):  # Show first 3 examples
                    print(f"    {i+1}. {entry['match']}")
                    print(f"       Context: {entry['context'][:100]}...")
                if len(entries) > 3:
                    print(f"    ... and {len(entries) - 3} more")
                print()
        
        # Save detailed results to file
        with open("comprehensive_entry_search_results.txt", "w", encoding="utf-8") as f:
            f.write("COMPREHENSIVE ENTRY SEARCH RESULTS\n")
            f.write("="*60 + "\n\n")
            f.write(f"Total entries found: {total_entries}\n\n")
            
            for entry_type, entries in results.items():
                f.write(f"{entry_type.upper().replace('_', ' ')}: {len(entries)} entries\n")
                f.write("-" * 40 + "\n")
                
                for i, entry in enumerate(entries):
                    f.write(f"\n{i+1}. Match: {entry['match']}\n")
                    f.write(f"   Conversation: {entry['conversation']}\n")
                    f.write(f"   Message ID: {entry['message_id']}\n")
                    f.write(f"   Context: {entry['context']}\n")
                    f.write(f"   Full Content: {entry['full_content']}\n")
                    f.write("-" * 40 + "\n")
        
        print(f"\nDetailed results saved to: comprehensive_entry_search_results.txt")
        
    except Exception as e:
        print(f"Error processing conversations.json: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_conversations_json()
