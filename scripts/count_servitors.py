#!/usr/bin/env python3
import json

def count_servitor_mentions():
    with open('Chats/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    servitor_count = 0
    servitor_messages = []
    
    for conv in data:
        mapping = conv.get('mapping', {})
        for msg_id, msg_data in mapping.items():
            if not msg_data or not isinstance(msg_data, dict):
                continue
                
            message = msg_data.get('message')
            if not message:
                continue
                
            content = message.get('content', {})
            parts = content.get('parts', [])
            
            for part in parts:
                if isinstance(part, str) and 'servitor' in part.lower():
                    servitor_count += 1
                    servitor_messages.append({
                        'content': part[:200] + '...' if len(part) > 200 else part,
                        'conv_id': conv.get('id', 'unknown')
                    })
    
    print(f"Found {servitor_count} messages mentioning 'servitor'")
    print("\nFirst 5 servitor mentions:")
    for i, msg in enumerate(servitor_messages[:5]):
        print(f"{i+1}. {msg['content']}")
        print(f"   Conversation: {msg['conv_id']}")
        print()

if __name__ == "__main__":
    count_servitor_mentions()
