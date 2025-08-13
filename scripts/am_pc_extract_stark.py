def is_duplicate_entry(new_entry, existing_entries):
    """
    Check if a new entry is a duplicate of an existing one.
    Allows same titles with different content from different chats.
    
    Args:
        new_entry: The new entry to check
        existing_entries: List of existing entries
    
    Returns:
        bool: True if duplicate found
    """
    if not existing_entries:
        return False
    
    new_content = new_entry.get('content', '').strip()
    new_title = new_entry.get('title', '').strip()
    new_source = new_entry.get('source_file', '')
    
    for existing in existing_entries:
        existing_content = existing.get('content', '').strip()
        existing_title = existing.get('title', '').strip()
        existing_source = existing.get('source_file', '')
        
        # Check for exact content match (always a duplicate)
        if new_content == existing_content and new_content:
            return True
        
        # Check for same title + same source file (likely duplicate)
        if new_title == existing_title and new_source == existing_source:
            return True
        
        # Check for very similar content from same source (90% similarity)
        if (new_source == existing_source and 
            len(new_content) > 50 and len(existing_content) > 50):
            
            # Simple similarity check - count common words
            new_words = set(new_content.lower().split())
            existing_words = set(existing_content.lower().split())
            
            if len(new_words) > 0 and len(existing_words) > 0:
                similarity = len(new_words.intersection(existing_words)) / len(new_words.union(existing_words))
                if similarity > 0.9:  # 90% similarity threshold
                    return True
    
    return False
