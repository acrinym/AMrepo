import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# --- ARGUMENTS ---
parser = argparse.ArgumentParser(description="Enhanced Extract AmandaMap/Phoenix Codex entries with 'Would you like me to log' patterns")
parser.add_argument("--dry-run", action="store_true", help="simulate actions without writing files")
args = parser.parse_args()
DRY_RUN = args.dry_run

# --- CONFIG ---
BASE_DIR = Path(__file__).resolve().parent
SEARCH_DIR = BASE_DIR / "Chats"
OUTPUT_DIR_AM = BASE_DIR / "am"
OUTPUT_DIR_PC = BASE_DIR / "pc"
COMBINED_DIR = BASE_DIR / "Combined"
GRIMOIRE_DIR = BASE_DIR / "grimoire"

# Ensure output directories exist
for dir_path in [OUTPUT_DIR_AM, OUTPUT_DIR_PC, COMBINED_DIR, GRIMOIRE_DIR]:
    if not DRY_RUN:
        dir_path.mkdir(exist_ok=True)

# --- ENHANCED PATTERNS ---
# Pattern 1: Direct entry patterns (existing)
ENTRY_PATTERNS = [
    r'^\s*(?:[#>*-]\s*)?(?:\\*\\*)?(AmandaMap|Phoenix Codex)\\b.*',
    r'^\s*(?:[#>*-]\s*)?(?:\\*\\*)?(Threshold|Entry|Echo|Field|Ritual|Directive|Anchor|Marker|Flame|Codex|Grimoire)\\b.*'
]

# Pattern 2: "Would you like me to log" patterns
LOG_REQUEST_PATTERNS = [
    r'Would you like me to log.*?(?:as|into|in|under|for|this|that).*?(AmandaMap|Phoenix Codex|Grimoire|RitualOS)',
    r'Would you like me to log.*?(?:as|into|in|under|for|this|that).*?(Threshold|Entry|Echo|Field|Ritual|Directive|Anchor|Marker|Flame|Codex)',
    r'Would you like me to log.*?(?:as|into|in|under|for|this|that).*?(Amanda|Phoenix|Grimoire|Ritual)'
]

# Pattern 3: User responses that indicate entry type
USER_RESPONSE_PATTERNS = [
    r'(?:yeah|yes|yep|sure|ok|okay|log it|log that|log this).*?(?:in|to|as|under).*?(AmandaMap|Phoenix Codex|Grimoire|RitualOS)',
    r'(?:yeah|yes|yep|sure|ok|okay|log it|log that|log this).*?(?:in|to|as|under).*?(Threshold|Entry|Echo|Field|Ritual|Directive|Anchor|Marker|Flame|Codex)',
    r'(?:yeah|yes|yep|sure|ok|okay|log it|log that|log this).*?(?:in|to|as|under).*?(Amanda|Phoenix|Grimoire|Ritual)'
]

# Pattern 4: Entry type keywords
ENTRY_TYPE_KEYWORDS = [
    'Threshold', 'Entry', 'Echo', 'Field', 'Ritual', 'Directive', 'Anchor', 'Marker', 
    'Flame', 'Codex', 'Grimoire', 'Phoenix', 'Amanda', 'SilentAct', 'Whispered', 
    'Field Pulse', 'Field Message', 'Field Transmission', 'Flame Entry', 'Flame Scroll',
    'Ritual Protocol', 'Hypothesis', 'Working', 'Tasking Template', 'Lionsgate Working'
]

def detect_entry_type(text):
    """Enhanced entry type detection"""
    text_lower = text.lower()
    
    # Check for specific entry types
    for keyword in ENTRY_TYPE_KEYWORDS:
        if keyword.lower() in text_lower:
            if 'threshold' in text_lower:
                return 'Threshold'
            elif 'entry' in text_lower:
                return 'Entry'
            elif 'echo' in text_lower:
                return 'Echo'
            elif 'field' in text_lower:
                return 'Field'
            elif 'ritual' in text_lower:
                return 'Ritual'
            elif 'directive' in text_lower:
                return 'Directive'
            elif 'anchor' in text_lower:
                return 'Anchor'
            elif 'marker' in text_lower:
                return 'Marker'
            elif 'flame' in text_lower:
                return 'Flame'
            elif 'codex' in text_lower:
                return 'Codex'
            elif 'grimoire' in text_lower:
                return 'Grimoire'
    
    return 'Unknown'

def find_log_requests_and_responses(content):
    """Find 'Would you like me to log' patterns and their responses"""
    entries = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Check for log request patterns
        for pattern in LOG_REQUEST_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Look ahead for the response and entry content
                entry_content = []
                entry_start = i
                
                # Look for the actual entry that follows
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j]
                    
                    # Check if this line contains entry content
                    if any(keyword.lower() in next_line.lower() for keyword in ENTRY_TYPE_KEYWORDS):
                        # Found entry content, collect it
                        entry_content.append(next_line)
                        
                        # Continue collecting until we hit a separator or new section
                        for k in range(j + 1, min(j + 50, len(lines))):
                            if k < len(lines):
                                content_line = lines[k]
                                if (content_line.strip().startswith('---') or 
                                    content_line.strip().startswith('##') or
                                    content_line.strip().startswith('###') or
                                    'Would you like me to log' in content_line or
                                    'Status:' in content_line):
                                    break
                                entry_content.append(content_line)
                        
                        # Determine entry type and system
                        entry_text = '\n'.join(entry_content)
                        entry_type = detect_entry_type(entry_text)
                        
                        # Determine if it's AmandaMap or Phoenix Codex
                        if 'phoenix' in entry_text.lower() or 'codex' in entry_text.lower():
                            system = 'Phoenix Codex'
                        elif 'amanda' in entry_text.lower() or 'map' in entry_text.lower():
                            system = 'AmandaMap'
                        else:
                            system = 'Unknown'
                        
                        entries.append({
                            'type': entry_type,
                            'system': system,
                            'content': entry_text,
                            'source': 'log_request',
                            'line_number': entry_start
                        })
                        break
                
                break
    
    return entries

def extract_entries_from_file(file_path):
    """Extract entries from a single file using enhanced patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    entries = []
    
    # Method 1: Direct entry patterns (existing logic)
    lines = content.split('\n')
    current_entry = None
    
    for i, line in enumerate(lines):
        # Check for entry start patterns
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in ENTRY_PATTERNS):
            if current_entry:
                entries.append(current_entry)
            
            # Determine entry type and system
            entry_type = detect_entry_type(line)
            if 'phoenix' in line.lower():
                system = 'Phoenix Codex'
            elif 'amanda' in line.lower():
                system = 'AmandaMap'
            else:
                system = 'Unknown'
            
            current_entry = {
                'type': entry_type,
                'system': system,
                'content': line,
                'source': 'direct_pattern',
                'line_number': i
            }
        
        elif current_entry:
            # Check for entry end
            if (line.strip().startswith('---') or 
                line.strip().startswith('##') or
                line.strip().startswith('###') or
                'Status:' in line or
                (i < len(lines) - 1 and any(re.search(pattern, lines[i + 1], re.IGNORECASE) for pattern in ENTRY_PATTERNS))):
                
                entries.append(current_entry)
                current_entry = None
            else:
                current_entry['content'] += '\n' + line
    
    if current_entry:
        entries.append(current_entry)
    
    # Method 2: Log request patterns
    log_entries = find_log_requests_and_responses(content)
    entries.extend(log_entries)
    
    return entries

def main():
    """Main extraction function"""
    if not SEARCH_DIR.exists():
        print(f"Search directory {SEARCH_DIR} not found!")
        return
    
    all_entries = []
    file_count = 0
    
    # Process all markdown files
    for file_path in SEARCH_DIR.rglob("*.md"):
        if file_path.is_file():
            print(f"Processing: {file_path.name}")
            entries = extract_entries_from_file(file_path)
            all_entries.extend(entries)
            file_count += 1
    
    print(f"\nProcessed {file_count} files")
    print(f"Found {len(all_entries)} total entries")
    
    # Group entries by system and type
    grouped_entries = defaultdict(lambda: defaultdict(list))
    for entry in all_entries:
        grouped_entries[entry['system']][entry['type']].append(entry)
    
    # Generate summary
    summary_lines = []
    summary_lines.append("# Enhanced Extraction Summary")
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"Files processed: {file_count}")
    summary_lines.append(f"Total entries found: {len(all_entries)}")
    summary_lines.append("")
    
    for system in sorted(grouped_entries.keys()):
        summary_lines.append(f"## {system}")
        system_entries = grouped_entries[system]
        
        for entry_type in sorted(system_entries.keys()):
            entries = system_entries[entry_type]
            summary_lines.append(f"### {entry_type}: {len(entries)} entries")
            
            for entry in entries[:5]:  # Show first 5 as examples
                content_preview = entry['content'][:100].replace('\n', ' ').strip()
                summary_lines.append(f"- {content_preview}... (line {entry['line_number']})")
            
            if len(entries) > 5:
                summary_lines.append(f"- ... and {len(entries) - 5} more")
            summary_lines.append("")
    
    # Write summary
    summary_file = BASE_DIR / "extraction_summary_enhanced_v2.md"
    if not DRY_RUN:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        print(f"Summary written to: {summary_file}")
    else:
        print("\n=== DRY RUN SUMMARY ===")
        print('\n'.join(summary_lines))
        print("\n=== END DRY RUN ===")

if __name__ == "__main__":
    main()