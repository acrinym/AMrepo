#!/usr/bin/env python3
import json
from pathlib import Path

def debug_json_structure():
    json_file = Path("Chats/conversations.json")
    
    if not json_file.exists():
        print("conversations.json not found!")
        return
    
    print("Loading conversations.json...")
    with open(json_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Look at first conversation structure
    if conversations:
        first_conv = conversations[0]
        print(f"\nFirst conversation keys: {list(first_conv.keys())}")
        
        if 'mapping' in first_conv:
            mapping = first_conv['mapping']
            print(f"Mapping has {len(mapping)} entries")
            
            # Look at multiple messages to find one with data
            for i, (msg_id, msg) in enumerate(mapping.items()):
                if i >= 5:  # Only check first 5
                    break
                    
                print(f"\nMessage {i+1} keys: {list(msg.keys())}")
                
                if 'message' in msg:
                    message_data = msg['message']
                    if message_data:
                        print(f"  Message data keys: {list(message_data.keys())}")
                        
                        if 'create_time' in message_data:
                            print(f"  Message create_time: {message_data['create_time']}")
                        
                        if 'content' in message_data:
                            content = message_data['content']
                            print(f"  Content keys: {list(content.keys())}")
                            
                            if 'parts' in content:
                                parts = content['parts']
                                if parts and isinstance(parts[0], str):
                                    print(f"  First part (first 100 chars): {parts[0][:100]}")
                    else:
                        print("  Message data is None")
                
                if 'create_time' in msg:
                    print(f"  Message create_time: {msg['create_time']}")
        
        if 'create_time' in first_conv:
            print(f"\nConversation create_time: {first_conv['create_time']}")

if __name__ == "__main__":
    debug_json_structure()
