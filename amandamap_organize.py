#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AmandaMap / Phoenix Codex Organizer
- Simple file organization and renaming
- Preserves original content exactly
- Creates clean directory structure
- Generates index and metadata
"""

import argparse, json, os, re, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ---------- CONFIG ----------

TYPE_PATTERNS = {
    "Threshold": [
        r"threshold\s*#?\s*(\d+)",
        r"thr\s*#?\s*(\d+)",
        r"threshold\s+(\d+)",
    ],
    "FieldPulse": [
        r"field\s+pulse\s*#?\s*(\d+)",
        r"fp\s*#?\s*(\d+)",
        r"field\s+pulse\s+(\d+)",
    ],
    "WhisperedFlame": [
        r"whispered\s+flame\s*#?\s*(\d+)",
        r"wf\s*#?\s*(\d+)",
        r"whispered\s+flame\s+(\d+)",
    ],
    "PhoenixCodex": [
        r"phoenix\s+codex",
        r"codex",
    ],
    "AmandaMap": [
        r"amandamap",
        r"amanda\s+map",
    ]
}

DATE_PATTERNS = [
    r"(\d{4}-\d{2}-\d{2})",
    r"(\d{2}-\d{2}-\d{4})",
    r"(\d{1,2}-\d{1,2}-\d{4})",
]

# ---------- HELPERS ----------

def extract_type_and_number(content, filename):
    """Extract entry type and number from content and filename"""
    content_lower = content.lower()
    filename_lower = filename.lower()
    
    # Check content first
    for entry_type, patterns in TYPE_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, content_lower)
            if match:
                if entry_type in ["PhoenixCodex", "AmandaMap"]:
                    return entry_type, None
                else:
                    try:
                        number = int(match.group(1))
                        return entry_type, number
                    except (ValueError, IndexError):
                        continue
    
    # Check filename as fallback
    for entry_type, patterns in TYPE_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, filename_lower)
            if match:
                if entry_type in ["PhoenixCodex", "AmandaMap"]:
                    return entry_type, None
                else:
                    try:
                        number = int(match.group(1))
                        return entry_type, number
                    except (ValueError, IndexError):
                        continue
    
    return None, None

def extract_date(content, filename):
    """Extract date from content and filename"""
    # Check content first
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, content)
        if match:
            date_str = match.group(1)
            # Normalize date format
            if len(date_str.split('-')[0]) == 2:  # MM-DD-YYYY or MM-DD-YY
                parts = date_str.split('-')
                if len(parts[2]) == 2:
                    parts[2] = '20' + parts[2]
                return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            elif len(date_str.split('-')[0]) == 4:  # YYYY-MM-DD
                return date_str
            else:  # MM-DD-YYYY
                parts = date_str.split('-')
                return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    
    # Check filename
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, filename)
        if match:
            date_str = match.group(1)
            # Same normalization logic
            if len(date_str.split('-')[0]) == 2:
                parts = date_str.split('-')
                if len(parts[2]) == 2:
                    parts[2] = '20' + parts[2]
                return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            elif len(date_str.split('-')[0]) == 4:
                return date_str
            else:
                parts = date_str.split('-')
                return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    
    return "2025-01-01"  # Default fallback

def extract_title(content):
    """Extract title from content"""
    lines = content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('*') and not line.startswith('-'):
            # Clean up the title
            title = re.sub(r'^[#*\-]+', '', line).strip()
            if title and len(title) > 5:
                return title
    return "Untitled Entry"

def generate_id(entry_type, number, date, counter=None):
    """Generate stable ID"""
    year = date[:4]
    if number is not None:
        base_id = f"{entry_type}-{year}-{number:04d}"
    else:
        # For unnumbered entries, use date
        date_part = date.replace('-', '')
        base_id = f"{entry_type}-{year}-{date_part}"
    
    if counter is not None:
        return f"{base_id}-{counter:03d}"
    return base_id

# ---------- MAIN PROCESSING ----------

def process_files(input_dir, output_dir, dry_run=False):
    """Process all files and organize them"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        return
    
    # Create output directory
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Process all markdown files
    entries = []
    file_count = 0
    id_counters = {}  # Track counters for duplicate IDs
    
    for file_path in input_path.rglob("*.md"):
        if file_path.is_dir():
            continue
            
        print(f"Processing: {file_path.name.encode('utf-8', errors='replace').decode('utf-8')}")
        file_count += 1
        
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
            
            if not content:
                continue
            
            # Extract metadata
            entry_type, number = extract_type_and_number(content, file_path.name)
            if not entry_type:
                continue  # Skip files that don't match our patterns
            
            date = extract_date(content, file_path.name)
            title = extract_title(content)
            
            # Generate unique ID, handling duplicates
            base_id = generate_id(entry_type, number, date)
            if base_id in id_counters:
                id_counters[base_id] += 1
                entry_id = generate_id(entry_type, number, date, id_counters[base_id])
            else:
                id_counters[base_id] = 0
                entry_id = base_id
            
            # Create entry record
            entry = {
                'id': entry_id,
                'type': entry_type,
                'number': number,
                'date': date,
                'title': title,
                'source_file': str(file_path),
                'content': content
            }
            entries.append(entry)
            
            if not dry_run:
                # Create year directory
                year_dir = output_path / date[:4]
                year_dir.mkdir(exist_ok=True)
                
                # Write organized file
                output_file = year_dir / f"{entry_id}.md"
                with output_file.open('w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n")
                    f.write(f"**Type**: {entry_type}\n")
                    f.write(f"**ID**: {entry_id}\n")
                    if number is not None:
                        f.write(f"**Number**: {number}\n")
                    f.write(f"**Date**: {date}\n")
                    f.write(f"**Source**: {file_path.name}\n\n")
                    f.write("---\n\n")
                    f.write(content)
        
        except Exception as e:
            print(f"Error processing {file_path.name.encode('utf-8', errors='replace').decode('utf-8')}: {e}")
            continue
    
    # Sort entries
    entries.sort(key=lambda x: (x['type'], x['number'] if x['number'] is not None else 999, x['date']))
    
    # Generate index
    if not dry_run:
        generate_index(entries, output_path)
        generate_metadata(entries, output_path)
    
    print(f"\nProcessed {file_count} files, created {len(entries)} entries")
    if dry_run:
        print("\nDRY RUN - No files written")
        for entry in entries[:10]:  # Show first 10
            print(f"  {entry['id']}: {entry['title']}")
        if len(entries) > 10:
            print(f"  ... and {len(entries) - 10} more")
    else:
        print(f"Files written to: {output_path}")

def generate_index(entries, output_path):
    """Generate master index"""
    index_content = "# AmandaMap / Phoenix Codex - Master Index\n\n"
    index_content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    # Group by type
    by_type = defaultdict(list)
    for entry in entries:
        by_type[entry['type']].append(entry)
    
    for entry_type in sorted(by_type.keys()):
        index_content += f"## {entry_type}\n\n"
        for entry in by_type[entry_type]:
            number_str = f" #{entry['number']}" if entry['number'] is not None else ""
            index_content += f"- **{entry['id']}**{number_str}: {entry['title']} ({entry['date']})\n"
        index_content += "\n"
    
    # Write index
    with (output_path / "INDEX.md").open('w', encoding='utf-8') as f:
        f.write(index_content)

def generate_metadata(entries, output_path):
    """Generate metadata JSON"""
    metadata = {
        'generated': datetime.now().isoformat(),
        'total_entries': len(entries),
        'by_type': defaultdict(int),
        'by_year': defaultdict(int),
        'entries': []
    }
    
    for entry in entries:
        metadata['by_type'][entry['type']] += 1
        metadata['by_year'][entry['date'][:4]] += 1
        metadata['entries'].append({
            'id': entry['id'],
            'type': entry['type'],
            'number': entry['number'],
            'date': entry['date'],
            'title': entry['title']
        })
    
    # Convert defaultdict to regular dict for JSON serialization
    metadata['by_type'] = dict(metadata['by_type'])
    metadata['by_year'] = dict(metadata['by_year'])
    
    with (output_path / "metadata.json").open('w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

# ---------- MAIN ----------

def main():
    parser = argparse.ArgumentParser(description="AmandaMap/Phoenix Codex Organizer")
    parser.add_argument("--input", required=True, help="Input directory with markdown files")
    parser.add_argument("--output", required=True, help="Output directory for organized files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing files")
    
    args = parser.parse_args()
    
    process_files(args.input, args.output, args.dry_run)

if __name__ == "__main__":
    main()
