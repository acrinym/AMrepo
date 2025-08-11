#!/usr/bin/env python3
"""
build_structured_markdown.py — Builds structured markdown files from extracted entries.
Organizes entries by date/sequence and entry type, with undated entries at the bottom.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def parse_filename_info(filename):
    """Parse filename to extract number, date, and entry type."""
    # Remove .md extension
    name = filename.replace('.md', '')
    
    # Extract number and date
    parts = name.split('-', 2)
    
    number = None
    date = None
    entry_type = None
    
    if len(parts) >= 2:
        # Check if first part is a number
        if parts[0].isdigit():
            number = int(parts[0])
            if len(parts) >= 3 and parts[1] != 'nodate':
                # Try to parse date
                try:
                    date = datetime.strptime(parts[1], '%Y-%m-%d')
                except ValueError:
                    pass
        elif parts[0] == 'x':
            number = None
            if len(parts) >= 3 and parts[1] != 'nodate':
                try:
                    date = datetime.strptime(parts[1], '%Y-%m-%d')
                except ValueError:
                    pass
    
    # Determine entry type from filename
    if 'threshold' in name.lower():
        entry_type = 'Threshold'
    elif 'whispered flame' in name.lower():
        entry_type = 'Whispered Flame'
    elif 'field pulse' in name.lower():
        entry_type = 'Field Pulse'
    elif 'flame vow' in name.lower():
        entry_type = 'Flame Vow'
    elif 'anchor site' in name.lower():
        entry_type = 'Anchor Site'
    elif 'protocol' in name.lower():
        entry_type = 'Protocol'
    elif 'entry' in name.lower():
        entry_type = 'Entry'
    else:
        entry_type = 'Other'
    
    return {
        'number': number,
        'date': date,
        'entry_type': entry_type,
        'filename': filename,
        'name': name
    }

def extract_date_from_content(filepath):
    """Try to extract date from file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for date patterns in content
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\w+ \d{1,2},? \d{4})',  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                date_str = match.group(1)
                try:
                    if '-' in date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    elif '/' in date_str:
                        return datetime.strptime(date_str, '%m/%d/%Y')
                    else:
                        # Try to parse month name format
                        return datetime.strptime(date_str, '%B %d, %Y')
                except ValueError:
                    continue
                    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return None

def build_structured_markdown(entries_dir, output_file, title):
    """Build structured markdown from entries directory."""
    
    entries = []
    
    # Read all entry files
    for filename in os.listdir(entries_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(entries_dir, filename)
            info = parse_filename_info(filename)
            
            # Try to get date from content if not in filename
            if info['date'] is None:
                content_date = extract_date_from_content(filepath)
                if content_date:
                    info['date'] = content_date
            
            # Read file content
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                info['content'] = content
                entries.append(info)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
    
    # Separate dated and undated entries
    dated_entries = [e for e in entries if e['date'] is not None]
    undated_entries = [e for e in entries if e['date'] is None]
    
    # Sort dated entries by date
    dated_entries.sort(key=lambda x: x['date'])
    
    # Sort undated entries by entry type and number
    def sort_undated(e):
        type_order = {
            'Threshold': 1,
            'Whispered Flame': 2,
            'Field Pulse': 3,
            'Flame Vow': 4,
            'Anchor Site': 5,
            'Protocol': 6,
            'Entry': 7,
            'Other': 8
        }
        return (type_order.get(e['entry_type'], 9), e['number'] or 999)
    
    undated_entries.sort(key=sort_undated)
    
    # Build markdown content
    md_content = f"# {title}\n\n"
    md_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    # Dated entries section
    if dated_entries:
        md_content += "## Chronological Entries\n\n"
        
        current_date = None
        for entry in dated_entries:
            entry_date = entry['date'].strftime('%Y-%m-%d')
            if entry_date != current_date:
                md_content += f"### {entry_date}\n\n"
                current_date = entry_date
            
            # Entry header
            if entry['number']:
                md_content += f"#### {entry['entry_type']} #{entry['number']}\n\n"
            else:
                md_content += f"#### {entry['entry_type']}\n\n"
            
            # Entry content
            md_content += f"{entry['content']}\n\n"
            md_content += "---\n\n"
    
    # Undated entries section
    if undated_entries:
        md_content += "## Undated Entries\n\n"
        
        current_type = None
        for entry in undated_entries:
            if entry['entry_type'] != current_type:
                md_content += f"### {entry['entry_type']}s\n\n"
                current_type = entry['entry_type']
            
            # Entry header
            if entry['number']:
                md_content += f"#### {entry['entry_type']} #{entry['number']}\n\n"
            else:
                md_content += f"#### {entry['entry_type']}\n\n"
            
            # Entry content
            md_content += f"{entry['content']}\n\n"
            md_content += "---\n\n"
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Created {output_file}")
    print(f"  - Dated entries: {len(dated_entries)}")
    print(f"  - Undated entries: {len(undated_entries)}")
    print(f"  - Total entries: {len(entries)}")

def main():
    """Main function to build both structured markdown files."""
    
    # Build AmandaMap structured markdown
    am_dir = "extracted_entries/am"
    if os.path.exists(am_dir):
        build_structured_markdown(
            am_dir, 
            "AMANDA_MAP_STRUCTURED.md", 
            "AmandaMap - Complete Structured Archive"
        )
    else:
        print(f"Directory {am_dir} not found")
    
    # Build Phoenix Codex structured markdown
    pc_dir = "extracted_entries/pc"
    if os.path.exists(pc_dir):
        build_structured_markdown(
            pc_dir, 
            "PHOENIX_CODEX_STRUCTURED.md", 
            "Phoenix Codex - Complete Structured Archive"
        )
    else:
        print(f"Directory {pc_dir} not found")

if __name__ == "__main__":
    main()
