#!/usr/bin/env python3
"""
Targeted search to find actual entry patterns and formats in conversations.json
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def find_actual_patterns():
    """Find the actual patterns used for entries in conversations.json."""
    
    json_file = Path("Chats/conversations.json")
    if not json_file.exists():
        print("conversations.json not found!")
        return
    
    print("Finding actual entry patterns in conversations.json...")
    
    # Look for actual entry headers and patterns
    entry_headers = defaultdict(int)
    entry_examples = defaultdict(list)
    
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
                        
                        # Look for actual entry headers (lines starting with # or specific patterns)
                        lines = content_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            
                            # Check for markdown headers that might be entries
                            if re.match(r'^#{1,6}\s+', line):
                                # Look for entry-like headers
                                if any(keyword in line.lower() for keyword in [
                                    'threshold', 'entry', 'whispered flame', 'field pulse', 
                                    'flame vow', 'anchor site', 'protocol', 'ritual', 'silent act',
                                    'amandamap', 'phoenix codex'
                                ]):
                                    entry_headers[line] += 1
                                    if len(entry_examples[line]) < 3:  # Keep first 3 examples
                                        entry_examples[line].append({
                                            'conversation': conv_idx,
                                            'context': content_text[:200] + "..." if len(content_text) > 200 else content_text
                                        })
                            
                            # Check for non-markdown entry patterns
                            elif any(keyword in line.lower() for keyword in [
                                'threshold', 'entry', 'whispered flame', 'field pulse',
                                'flame vow', 'anchor site', 'protocol', 'ritual', 'silent act'
                            ]):
                                if re.search(r'\d+', line):  # Has a number (likely an entry)
                                    entry_headers[line] += 1
                                    if len(entry_examples[line]) < 3:
                                        entry_examples[line].append({
                                            'conversation': conv_idx,
                                            'context': content_text[:200] + "..." if len(content_text) > 200 else content_text
                                        })
        
        # Print results
        print(f"\n{'='*60}")
        print("ACTUAL ENTRY PATTERNS FOUND")
        print(f"{'='*60}")
        print(f"Total unique entry headers: {len(entry_headers)}")
        print()
        
        # Sort by frequency
        sorted_headers = sorted(entry_headers.items(), key=lambda x: x[1], reverse=True)
        
        for header, count in sorted_headers[:50]:  # Show top 50
            print(f"{count:4d}x: {header}")
            if entry_examples[header]:
                print(f"      Example from conversation {entry_examples[header][0]['conversation']}: {entry_examples[header][0]['context'][:100]}...")
            print()
        
        # Save to file
        with open("actual_entry_patterns.txt", "w", encoding="utf-8") as f:
            f.write("ACTUAL ENTRY PATTERNS FOUND\n")
            f.write("="*60 + "\n\n")
            f.write(f"Total unique entry headers: {len(entry_headers)}\n\n")
            
            for header, count in sorted_headers:
                f.write(f"{count:4d}x: {header}\n")
                if entry_examples[header]:
                    f.write(f"      Example from conversation {entry_examples[header][0]['conversation']}: {entry_examples[header][0]['context']}\n")
                f.write("\n")
        
        print(f"\nDetailed patterns saved to: actual_entry_patterns.txt")
        
    except Exception as e:
        print(f"Error processing conversations.json: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_actual_patterns()
