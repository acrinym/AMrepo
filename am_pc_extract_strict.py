#!/usr/bin/env python3
"""
am_pc_extract_strict.py — Enhanced extractor for AmandaMap / Phoenix Codex entries.
- Original title-based detection
- NEW: "Would you like" pattern detection for AmandaMap entries
- Captures full content blocks when affirmative responses are given
- Outputs JSONL + per-entry Markdown under ./out by default.

Usage:
  python am_pc_extract_strict.py <root_folder> [--out OUTDIR] [--no-files] [--require-meta]
"""

import sys, json, re
from pathlib import Path
from datetime import datetime

SEPARATORS = [":", " – ", " — ", " - "]
HARD_STOPS = ["### ", "## ", "# ", "----", "---", "***"]
MAX_BLANK_STREAK = 2
MIN_BLOCK_LINES = 3  # if fewer lines, require early Date/Status to accept

# New: Affirmative response patterns
AFFIRMATIVE_PATTERNS = [
    r'\b(yes|yeah|yep|sure|absolutely|definitely|please|ok|okay|do it|log it|save it|mark it)\b',
    r'\b(that sounds good|that works|go ahead|proceed|continue|start|begin)\b',
    r'\b(i would|i do|i want|i need|i\'d like|i\'d love)\b'
]

# New: AmandaMap reference patterns (case insensitive)
AMANDAMAP_PATTERNS = [
    r'\bamandamap\b',
    r'\bamanda map\b',
    r'\bthe amandamap\b',
    r'\bin the amandamap\b',
    r'\bin amandamap\b',
    r'\bthreshold\b',
    r'\bentry\b',
    r'\bflame\b',
    r'\bcodex\b'
]

def normalize_line(s: str) -> str:
    t = s.strip().lower()
    for d in ["**","__","*","`",">","|"]:
        t = t.replace(d,"")
    for e in ["🔊","🧬","📡","🌀","🌙","🦅","📱","🗺️","🐦‍🔥","❤️","♥️"]:
        t = t.replace(e,"")
    return t.strip()

def strip_heading_prefix(raw: str) -> str:
    s = raw.lstrip()
    while s.startswith(("#", "-", "*", "•")):
        s = s[1:].lstrip()
    return s

def looks_like_title(raw: str) -> bool:
    body = strip_heading_prefix(raw)
    return (len(body) <= 160) and any(sep in body for sep in SEPARATORS)

def scan_number_from_text(text: str) -> str:
    # first contiguous digits
    buf = []
    for ch in text:
        if ch.isdigit():
            buf.append(ch)
        elif buf:
            break
    return "".join(buf) if buf else ""

def scan_date_from_block(lines: list[str]) -> str:
    months = ["january","february","march","april","may","june","july","august",
              "september","october","november","december"]
    for raw in lines[:6]:
        n = normalize_line(raw).replace(",", "")
        # YYYY-MM-DD
        for token in n.split():
            if len(token)==10 and token[4]=="-" and token[7]=="-" and \
               token[:4].isdigit() and token[5:7].isdigit() and token[8:].isdigit():
                return token
        # Month DD YYYY
        words = n.split()
        for m in months:
            if m in words:
                i = words.index(m)
                day = words[i+1] if i+1 < len(words) else ""
                year = words[i+2] if i+2 < len(words) else ""
                if day.isdigit() and len(year)==4 and year.isdigit():
                    mm = str(months.index(m)+1).zfill(2)
                    dd = day.zfill(2)
                    return f"{year}-{mm}-{dd}"
    return ""

def is_affirmative_response(text: str) -> bool:
    """Check if text contains an affirmative response"""
    text_lower = text.lower()
    for pattern in AFFIRMATIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def contains_amandamap_reference(text: str) -> bool:
    """Check if text contains AmandaMap-related references"""
    text_lower = text.lower()
    for pattern in AMANDAMAP_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def detect_would_you_like_pattern(lines: list[str], start_idx: int) -> tuple[bool, int, int]:
    """
    Detect "Would you like" patterns and find the complete block.
    Returns (is_would_you_like, start_line, end_line)
    """
    if start_idx >= len(lines):
        return False, start_idx, start_idx
    
    current_line = lines[start_idx].lower()
    
    # Check if current line contains "would you like"
    if "would you like" not in current_line:
        return False, start_idx, start_idx
    
    # Check if it's about logging/marking/saving something
    if not any(word in current_line for word in ["log", "mark", "save", "record", "add", "create"]):
        return False, start_idx, start_idx
    
    # Look ahead for affirmative response (within next 10 lines)
    end_idx = start_idx
    affirmative_found = False
    amandamap_reference_found = False
    
    # First, check if the question itself contains AmandaMap reference
    if contains_amandamap_reference(lines[start_idx]):
        amandamap_reference_found = True
    
    # Look for affirmative response and AmandaMap references
    for i in range(start_idx + 1, min(start_idx + 10, len(lines))):
        line = lines[i]
        if not line.strip():  # Skip empty lines
            continue
            
        # Check for affirmative response
        if not affirmative_found and is_affirmative_response(line):
            affirmative_found = True
        
        # Check for AmandaMap references
        if not amandamap_reference_found and contains_amandamap_reference(line):
            amandamap_reference_found = True
        
        # If we found both, we can stop looking
        if affirmative_found and amandamap_reference_found:
            end_idx = i
            break
    
    # If we found both conditions, this is a valid "Would you like" pattern
    if affirmative_found and amandamap_reference_found:
        # Look for the end of the block (next hard stop or significant content break)
        for i in range(end_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            
            # Check for hard stops
            if any(line.strip().startswith(stop) for stop in ["###", "##", "#", "----", "---", "***"]):
                break
            
            # Check if this looks like the start of a new entry
            if detect_start(line)[0]:
                break
            
            # Check if we've hit another "Would you like" pattern
            if "would you like" in line.lower():
                break
            
            end_idx = i
        
        return True, start_idx, end_idx
    
    return False, start_idx, start_idx

def detect_start(raw: str, require_meta: bool=False):
    """
    Return (True, scope, subtype) if this raw line should start a block.
    scope in {"AmandaMap","PhoenixCodex"}, subtype in {"threshold","whisperedflame","fieldpulse","entry","flamevow","anchorsite","protocol"}.
    """
    body = strip_heading_prefix(raw)
    norm = normalize_line(body)
    if not looks_like_title(raw):
        return False, "", ""
    # exact starts only
    def starts(prefix): return norm.startswith(prefix)

    # Threshold (must include a number)
    if starts("amandamap threshold") or starts("threshold "):
        if scan_number_from_text(norm):
            return True, "AmandaMap", "threshold"
    if starts("phoenix codex threshold"):
        if scan_number_from_text(norm):
            return True, "PhoenixCodex", "threshold"

    # Whispered Flame (numbered)
    if starts("whispered flame"):
        if scan_number_from_text(norm):
            return True, "AmandaMap", "whisperedflame"

    # Field Pulse (numbered)
    if starts("field pulse"):
        if scan_number_from_text(norm):
            return True, "AmandaMap", "fieldpulse"

    # Flame Vow / Anchor Site / Protocol (not necessarily numbered)
    if starts("flame vow "):
        return True, "AmandaMap", "flamevow"
    if starts("anchor site "):
        return True, "AmandaMap", "anchorsite"
    if starts("protocol "):
        return True, "AmandaMap", "protocol"

    # Generic entry lines: must begin with exact tokens
    if starts("amandamap entry") or starts("amandamap:"):
        return True, "AmandaMap", "entry"
    if starts("phoenix codex "):  # e.g., "phoenix codex entry: ..."
        return True, "PhoenixCodex", "entry"

    return False, "", ""

def is_hard_stop(norm: str) -> bool:
    if not norm: return False
    for h in HARD_STOPS:
        if norm.startswith(h.strip().lower()):
            return True
    return False

def block_is_valid(lines: list[str], require_meta: bool=False) -> bool:
    if len(lines) >= MIN_BLOCK_LINES:
        return True
    # else check for early meta
    meta_found = False
    for raw in lines[1:4]:
        n = normalize_line(raw)
        if n.startswith("date:") or n.startswith("status:"):
            meta_found = True
            break
    return meta_found if require_meta else meta_found or len(lines) >= 2

def safe_filename(s: str) -> str:
    bad = '<>:"/\\|?*'
    return "".join("_" if ch in bad else ch for ch in s)[:140]

def walk_files(root: Path):
    files = []
    # Only search in the Chats directory for original chat files
    chats_dir = root / "Chats"
    if chats_dir.exists():
        for ext in (".md", ".txt"):
            files.extend(chats_dir.rglob(f"*{ext}"))
    
    # Also search in the root directory for structured files like AMANDA_MAP_STRUCTURED.md
    for ext in (".md", ".txt"):
        files.extend([f for f in root.glob(f"*{ext}") if f.name.startswith(("AMANDA_MAP_STRUCTURED", "PHOENIX_CODEX_STRUCTURED"))])
    
    # Filter out any files from extracted_entries or output directories
    files = [f for f in files if "extracted_entries" not in str(f) and "out" not in str(f) and "test_output" not in str(f)]
    
    return files

def find_resume_point(entries, files_processed):
    """
    Find the resume point for the next extraction run.
    Returns (file_index, line_number) where to resume.
    """
    if not entries:
        return 0, 0
    
    # Get the last entry's source file
    last_entry = entries[-1]
    last_source = last_entry["source_file"]
    
    # Find the file index
    for i, file_path in enumerate(files_processed):
        if str(file_path) == last_source:
            # For now, resume from the beginning of the next file
            # In a more sophisticated version, we could track the exact line
            if i + 1 < len(files_processed):
                return i + 1, 0
            else:
                return i, 0
    
    return 0, 0

def extract_blocks_with_restart(paths, require_meta=False, verbose=False, max_entries_per_run=2000):
    """
    Extract blocks with automatic restart when hitting entry limits.
    Returns all entries found across multiple runs.
    """
    all_entries = []
    current_run = 0
    
    while True:
        current_run += 1
        print(f"\n=== EXTRACTION RUN #{current_run} ===")
        
        # Determine which files to process in this run
        if current_run == 1:
            # First run: process all files
            files_to_process = paths
            start_line = 0
        else:
            # Subsequent runs: resume from last processed file/line
            files_to_process = paths[resume_file_index:]
            start_line = resume_line
            print(f"Resuming from file {resume_file_index}/{len(paths)} at line {resume_line}")
        
        # Extract blocks for this run
        run_entries = extract_blocks_single_run(files_to_process, require_meta, verbose, start_line, max_entries_per_run)
        
        print(f"Run #{current_run} found {len(run_entries)} entries")
        
        # Add to total entries
        all_entries.extend(run_entries)
        print(f"Total entries so far: {len(all_entries)}")
        
        # Check if we hit the limit and need to restart
        if len(run_entries) == max_entries_per_run:
            print(f"\n*** HIT {max_entries_per_run} LIMIT - PREPARING TO RESTART ***")
            
            # Find the resume point for next run
            resume_file_index, resume_line = find_resume_point(run_entries, files_to_process)
            
            print(f"Next run will resume from file {resume_file_index}/{len(paths)} at line {resume_line}")
            
            # Check if we have more files to process
            if resume_file_index >= len(paths):
                print("No more files to process - extraction complete!")
                break
        else:
            print("Extraction completed without hitting limit")
            break
    
    return all_entries

def extract_blocks_single_run(paths, require_meta=False, verbose=False, start_line=0, max_entries=2000):
    """
    Extract blocks for a single run, stopping when hitting max_entries limit.
    Returns entries found and resume point information.
    """
    entries = []
    file_count = 0
    
    for p in paths:
        file_count += 1
        if file_count % 100 == 0:
            print(f"Processing file {file_count}/{len(paths)}...")
        
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
            
        lines = text.splitlines()
        current = None
        blank_streak = 0
        
        # Start from specified line if this is a resume
        i = start_line if file_count == 1 and start_line > 0 else 0
        
        def close():
            nonlocal current
            if current and current["lines"]:
                if not block_is_valid(current["lines"], require_meta):
                    current = None
                    return
                raw_lines = current["lines"]
                title = strip_heading_prefix(raw_lines[0]) if raw_lines else ""
                number = scan_number_from_text(normalize_line(title))
                date = scan_date_from_block(raw_lines)
                
                # For "Would you like" patterns, generate a title if none exists
                if current["subtype"] == "would_you_like" and not title.strip():
                    title = f"Would You Like Entry - {date or 'nodate'}"
                
                entries.append({
                    "source_file": str(current["source"]),
                    "scope": current["scope"],
                    "subtype": current["subtype"],
                    "title": title.strip(),
                    "number": number,
                    "date": date,
                    "content": "\n".join(raw_lines).strip()
                })
                
                # Check if we've hit the limit
                if len(entries) >= max_entries:
                    print(f"*** HIT {max_entries} LIMIT IN THIS RUN ***")
                    return True  # Signal to stop
                
            current = None
            return False
        
        while i < len(lines):
            raw = lines[i]
            n = normalize_line(raw)
            
            # Check for "Would you like" patterns first
            is_would_you_like, start_line, end_line = detect_would_you_like_pattern(lines, i)
            if is_would_you_like:
                if close():  # Check if we hit the limit
                    return entries
                # Extract the complete block
                block_lines = lines[start_line:end_line + 1]
                current = {
                    "source": p, 
                    "scope": "AmandaMap", 
                    "subtype": "would_you_like", 
                    "lines": block_lines
                }
                i = end_line + 1  # Move to after the block
                continue
            
            # Original title-based detection
            start, scope, subtype = detect_start(raw, require_meta=require_meta)
            if start:
                if close():  # Check if we hit the limit
                    return entries
                current = {"source": p, "scope": scope, "subtype": subtype, "lines": [raw]}
                blank_streak = 0
                i += 1
                continue
                
            if current:
                if is_hard_stop(n):
                    if close():  # Check if we hit the limit
                        return entries
                    i += 1
                    continue
                if not n:
                    blank_streak += 1
                    if blank_streak >= MAX_BLANK_STREAK:
                        if close():  # Check if we hit the limit
                            return entries
                        i += 1
                        continue
                else:
                    blank_streak = 0
                # stop if next line begins a new block
                nxt = lines[i] if i < len(lines) else ""
                if nxt:
                    s2,_,_ = detect_start(nxt, require_meta=require_meta)
                    if s2:
                        if close():  # Check if we hit the limit
                            return entries
                        i += 1
                        continue
                current["lines"].append(raw)
            i += 1
        close()
        
        # Reset start_line for subsequent files
        start_line = 0
        
    return entries

def write_outputs(entries, out_dir: Path, write_files=True):
    am = [e for e in entries if e["scope"] == "AmandaMap"]
    pc = [e for e in entries if e["scope"] == "PhoenixCodex"]
    (out_dir / "combined").mkdir(parents=True, exist_ok=True)
    with (out_dir / "combined" / "amandamap.jsonl").open("w", encoding="utf-8") as f:
        for e in am: f.write(json.dumps(e, ensure_ascii=False) + "\n")
    with (out_dir / "combined" / "phoenixcodex.jsonl").open("w", encoding="utf-8") as f:
        for e in pc: f.write(json.dumps(e, ensure_ascii=False) + "\n")
    if write_files:
        (out_dir / "am").mkdir(parents=True, exist_ok=True)
        (out_dir / "pc").mkdir(parents=True, exist_ok=True)
        def write_group(group, folder):
            for e in group:
                n = e["number"] or "x"
                d = e["date"] or "nodate"
                t = e["title"] or e["subtype"]
                fn = f"{n}-{d}-{safe_filename(t)}.md"
                (out_dir / folder / fn).write_text(e["content"], encoding="utf-8")
        write_group(am, "am"); write_group(pc, "pc")

def main():
    if len(sys.argv) < 2:
        print("Usage: python am_pc_extract_strict.py <root> [--out OUTDIR] [--no-files] [--require-meta]")
        sys.exit(1)
    root = Path(sys.argv[1]).expanduser().resolve()
    out_dir = Path("./out")
    write_files = True
    require_meta = False
    if "--out" in sys.argv:
        out_dir = Path(sys.argv[sys.argv.index("--out")+1]).expanduser().resolve()
    if "--no-files" in sys.argv:
        write_files = False
    if "--require-meta" in sys.argv:
        require_meta = True

    files = walk_files(root)
    entries = extract_blocks_with_restart(files, require_meta=require_meta)
    
    # Debug: Test if we can add more entries manually
    print(f"After extraction: {len(entries)} entries")
    if len(entries) == 2000:
        print("*** TESTING: Adding a manual entry to see if we can go beyond 2000 ***")
        entries.append({
            "source_file": "TEST",
            "scope": "AmandaMap",
            "subtype": "test",
            "title": "Test Entry Beyond 2000",
            "number": "9999",
            "date": "test",
            "content": "This is a test entry to see if we can go beyond 2000"
        })
        print(f"After manual addition: {len(entries)} entries")
    
    write_outputs(entries, out_dir, write_files)
    print(f"Scanned {len(files)} files → found {len(entries)} entries.")
    print(f"Wrote JSONL to {out_dir/'combined'}; per-entry MD: {write_files}")

if __name__ == "__main__":
    main()
