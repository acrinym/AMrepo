#!/usr/bin/env python3
"""
fix_encoding.py — Fix encoding issues in problematic chat files.
"""

import os
import chardet

def detect_and_fix_encoding(filepath):
    """Detect and fix encoding issues in a file."""
    try:
        # Read the file as bytes to detect encoding
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        # Detect encoding
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']
        confidence = result['confidence']
        
        print(f"File: {filepath}")
        print(f"Detected encoding: {detected_encoding} (confidence: {confidence:.2f})")
        
        if detected_encoding and confidence > 0.7:
            try:
                # Try to decode with detected encoding
                content = raw_data.decode(detected_encoding)
                
                # Write back as UTF-8
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Successfully converted {filepath} to UTF-8")
                return True
                
            except Exception as e:
                print(f"Error converting {filepath}: {e}")
                return False
        else:
            print(f"Could not reliably detect encoding for {filepath}")
            return False
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def fix_chat_files():
    """Fix encoding issues in all chat files."""
    chat_dir = "Chats"
    if not os.path.exists(chat_dir):
        print(f"Chat directory {chat_dir} not found")
        return
    
    fixed_count = 0
    total_count = 0
    
    for filename in os.listdir(chat_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(chat_dir, filename)
            total_count += 1
            
            if detect_and_fix_encoding(filepath):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} out of {total_count} chat files")

if __name__ == "__main__":
    try:
        import chardet
        fix_chat_files()
    except ImportError:
        print("chardet library not found. Install with: pip install chardet")
        print("Or manually fix the problematic file: Chats\\ChatGPT-Chakra_2_Clearing_Ritual.md")
