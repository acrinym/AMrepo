#!/usr/bin/env python3
"""
Build a comprehensive list of magical phrases for ritual detection
"""
import json
import re
from pathlib import Path
from collections import defaultdict

def search_magical_phrases():
    """Search conversations.json for magical phrases and build a comprehensive list."""
    
    json_file = Path("Chats/conversations.json")
    if not json_file.exists():
        print("❌ conversations.json not found!")
        return
    
    print("🔍 Searching conversations.json for magical phrases...")
    
    # Load the JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Found {len(data)} conversations")
    
    # Define search patterns for different types of magical content
    search_patterns = {
        "EXPLICIT_RITUAL": [
            r'\b(?:ritual|spell|working|ceremony|rite|invocation|evocation|conjuration)\b',
            r'\b(?:magic|magical|witchcraft|occult|esoteric)\b'
        ],
        "SPIRIT_ENTITIES": [
            r'\b(?:spirit|entity|servitor|demon|angel|god|deity)\b',
            r'\b(?:zepar|vassago|lucifer|seere|balam|foras|sitri|andras|eligos|clauneck)\b'
        ],
        "MAGICAL_ACTIONS": [
            r'\b(?:invoke|evoke|summon|banish|bind|cleanse|purify|consecrate)\b',
            r'\b(?:cast|perform|execute|conduct|enact)\b'
        ],
        "MAGICAL_TOOLS": [
            r'\b(?:altar|circle|temple|sacred space|sanctuary)\b',
            r'\b(?:candle|herb|crystal|oil|powder|stone|salt|thread|photo|mirror)\b'
        ],
        "MAGICAL_TIMING": [
            r'\b(?:new moon|full moon|waxing|waning|dawn|dusk|midnight|noon)\b',
            r'\b(?:sabbath|esbat|equinox|solstice|planetary hour)\b'
        ],
        "MAGICAL_PROTECTION": [
            r'\b(?:banishment|protection|warding|shielding|defense)\b',
            r'\b(?:lbrp|lesser banishing ritual|greater banishing ritual)\b'
        ],
        "MAGICAL_VISUALIZATION": [
            r'\b(?:visualize|focus|intend|declare|vow|promise)\b',
            r'\b(?:energy|field|aura|chakra|meridian|qi|chi|prana)\b'
        ]
    }
    
    # Track findings
    findings = defaultdict(list)
    total_conversations = 0
    conversations_with_magic = 0
    
    # Search through conversations
    for i, conversation in enumerate(data):
        if i % 100 == 0:
            print(f"Processing conversation {i}/{len(data)}...")
        
        mapping = conversation.get('mapping', {})
        conversation_has_magic = False
        
        for msg_data in mapping.values():
            if not msg_data or not msg_data.get('message') or not msg_data['message'].get('content'):
                continue
                
            content = msg_data['message']['content']
            if 'parts' not in content:
                continue
                
            for part in content['parts']:
                if isinstance(part, str):
                    part_lower = part.lower()
                    
                    # Check each pattern category
                    for category, patterns in search_patterns.items():
                        for pattern in patterns:
                            matches = re.findall(pattern, part_lower)
                            if matches:
                                findings[category].extend(matches)
                                conversation_has_magic = True
        
        if conversation_has_magic:
            conversations_with_magic += 1
        total_conversations += 1
    
    # Analyze results
    print(f"\n📈 ANALYSIS RESULTS:")
    print(f"Total conversations: {total_conversations}")
    print(f"Conversations with magical content: {conversations_with_magic}")
    print(f"Percentage: {(conversations_with_magic/total_conversations)*100:.1f}%")
    
    print(f"\n🔮 MAGICAL PHRASES FOUND BY CATEGORY:")
    for category, matches in findings.items():
        unique_matches = list(set(matches))
        print(f"\n{category}:")
        for match in sorted(unique_matches):
            count = matches.count(match)
            print(f"  {match}: {count} times")
    
    # Build recommended detection phrases
    print(f"\n💡 RECOMMENDED DETECTION PHRASES:")
    print("Based on the analysis, here are the most reliable magical indicators:")
    
    # High-confidence phrases (appear frequently and are clearly magical)
    high_confidence = []
    for category, matches in findings.items():
        if category in ["EXPLICIT_RITUAL", "SPIRIT_ENTITIES", "MAGICAL_ACTIONS"]:
            for match in set(matches):
                if matches.count(match) >= 5:  # Appears at least 5 times
                    high_confidence.append(match)
    
    print(f"\nHIGH CONFIDENCE (appear 5+ times):")
    for phrase in sorted(high_confidence):
        print(f"  '{phrase}'")
    
    # Medium confidence (appear 2-4 times)
    medium_confidence = []
    for category, matches in findings.items():
        for match in set(matches):
            count = matches.count(match)
            if 2 <= count <= 4:
                medium_confidence.append((match, count))
    
    print(f"\nMEDIUM CONFIDENCE (appear 2-4 times):")
    for phrase, count in sorted(medium_confidence, key=lambda x: x[1], reverse=True):
        print(f"  '{phrase}': {count} times")
    
    # Build detection logic recommendations
    print(f"\n🎯 RECOMMENDED DETECTION LOGIC:")
    print("1. MUST have at least 1 HIGH CONFIDENCE phrase")
    print("2. PLUS at least 1 additional magical element from any category")
    print("3. This should eliminate false positives while catching real rituals")

if __name__ == "__main__":
    search_magical_phrases()
