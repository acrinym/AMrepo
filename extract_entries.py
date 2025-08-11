import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# --- ARGUMENTS ---
parser = argparse.ArgumentParser(description="Extract AmandaMap/Phoenix Codex entries")
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

# Ensure dirs exist unless it's a dry-run
if not DRY_RUN:
    print("[+] Creating output directories...")
    for base in [OUTPUT_DIR_AM, OUTPUT_DIR_PC, COMBINED_DIR, GRIMOIRE_DIR]:
        base.mkdir(parents=True, exist_ok=True)
else:
    print("[+] Dry-run mode enabled. No files or directories will be created.")

# Patterns for AmandaMap/Phoenix Codex entries
start_pattern = re.compile(
    r"^(AmandaMap|Phoenix Codex)\s+[A-Za-z]+\s*(#?\d+|Threshold\s+\d+)?[^\n]*",
    re.IGNORECASE,
)
end_pattern = re.compile(r"^Status:\s?.*", re.IGNORECASE)

# Data structures to hold entries
# Dict: { "Type" : { num: [entries...] } }
entries_am = defaultdict(lambda: defaultdict(list))
entries_pc = defaultdict(lambda: defaultdict(list))
seen_hashes = set()

# Ritual detection patterns and tracking
ritual_start = re.compile(r"^Ritual(?:\s+Name)?[:\-]\s*(.+)", re.IGNORECASE)
ritual_section = re.compile(
    r"^(Ingredients|Steps|Spirits|Directions|Invocations)[:\-]\s*(.*)",
    re.IGNORECASE,
)
seen_rituals = set()

# Log of (relative_path, first_line) for quick summary after extraction
SUMMARY_LOG = []


def safe_filename(text: str) -> str:
    """Create a filesystem-safe filename from a string."""
    return re.sub(r"[^a-zA-Z0-9_\-]+", "_", text).strip("_")


def detect_type_and_num(line: str):
    """Detect the entry type and number from the first line of a block."""
    m = re.match(r"^(AmandaMap|Phoenix Codex)\s+([A-Za-z]+)\s*#?(\d+)?", line, re.IGNORECASE)
    if not m:
        return None, None
    entry_type = m.group(2).capitalize()
    num = int(m.group(3)) if m.group(3) else 99999  # Use a large number for entries without a number
    return entry_type, num


def extract_ritual_fields(text: str):
    """Extract structured fields (like Ingredients, Steps) from a ritual text block."""
    fields = {}
    current_section = None
    for line in text.splitlines():
        m = ritual_section.match(line)
        if m:
            current_section = m.group(1).lower()
            initial_content = m.group(2).strip()
            fields[current_section] = [initial_content] if initial_content else []
        elif current_section and line.strip():
            fields[current_section].append(line.strip())
        elif not line.strip():
            # Reset current section on a blank line
            current_section = None
            
    # Join the lines for each section
    for key, value_list in fields.items():
        fields[key] = "\n".join(value_list).strip()
    return fields


# --- MAIN SCANNING LOGIC ---
print(f"[+] Scanning for markdown files in: {SEARCH_DIR}")
for root, _, files in os.walk(SEARCH_DIR):
    for file in files:
        if file.lower().endswith(".md"):
            path = Path(root) / file
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # --- Process AmandaMap / Phoenix Codex entries ---
            i = 0
            while i < len(lines):
                if start_pattern.search(lines[i]):
                    block = []
                    j = 0
                    # Capture the entire block until the end pattern or a new start pattern
                    while i + j < len(lines):
                        current_line = lines[i + j]
                        # Stop if a new entry starts, but don't include it in the current block
                        if j > 0 and start_pattern.search(current_line):
                            break
                        
                        block.append(current_line.rstrip("\n"))
                        
                        # Stop after including the line with the end pattern
                        if end_pattern.search(current_line):
                            break
                        j += 1
                        
                    entry_text = "\n".join(block).strip()
                    entry_hash = hash(entry_text)

                    if entry_hash not in seen_hashes:
                        seen_hashes.add(entry_hash)

                        is_am = entry_text.lower().startswith("amandamap")
                        target_dir = OUTPUT_DIR_AM if is_am else OUTPUT_DIR_PC
                        entries_dict = entries_am if is_am else entries_pc
                        label = "AmandaMap" if is_am else "Phoenix Codex"

                        entry_type, num = detect_type_and_num(lines[i])
                        if not entry_type:
                            entry_type = "Unknown"

                        # Find date in text, otherwise use file modification time
                        date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", entry_text)
                        if date_match:
                            date_str = date_match.group(1)
                        else:
                            mtime = path.stat().st_mtime
                            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

                        type_folder = target_dir / entry_type
                        if not DRY_RUN:
                            type_folder.mkdir(parents=True, exist_ok=True)

                        fname = (
                            f"{entry_type.lower()}-{num}_{date_str}.md"
                            if num != 99999
                            else f"{entry_type.lower()}_{date_str}.md"
                        )
                        
                        # ** RESOLVED CONFLICT 1 **
                        file_path = type_folder / fname
                        if DRY_RUN:
                            print(f"[dry-run] Would write entry to: {file_path}")
                        else:
                            with file_path.open("w", encoding="utf-8") as out:
                                out.write(entry_text)

                        # Track the file and its first line for the summary log
                        SUMMARY_LOG.append(
                            (
                                file_path.relative_to(BASE_DIR),
                                entry_text.splitlines()[0],
                            )
                        )

                        entries_dict[entry_type][num].append(entry_text)

                        # If this is a ritual, also export to grimoire
                        if entry_type.lower() == "ritual":
                            first_line = lines[i].strip()
                            ritual_name_match = ritual_start.match(first_line) or re.match(r"^(?:AmandaMap|Phoenix Codex)\s+Ritual\s*#?\d*\s*[:\-]?\s*(.+)", first_line, re.IGNORECASE)
                            ritual_name = ritual_name_match.group(1).strip() if ritual_name_match else "Unnamed Ritual"
                            ritual_fields = extract_ritual_fields(entry_text)
                            ritual_filename = safe_filename(ritual_name)
                            ritual_path = GRIMOIRE_DIR / f"{ritual_filename}.ritual"
                            
                            # ** RESOLVED CONFLICT 2 **
                            if DRY_RUN:
                                print(f"[dry-run] Would write ritual to: {ritual_path}")
                            else:
                                with ritual_path.open("w", encoding="utf-8") as rfile:
                                    rfile.write(f"name: {ritual_name}\n")
                                    for key, val in ritual_fields.items():
                                        rfile.write(f"{key}: |\n")
                                        for l in val.splitlines():
                                            rfile.write(f"  {l}\n")

                            # Log ritual file creation with the first line of the entry
                            SUMMARY_LOG.append(
                                (
                                    ritual_path.relative_to(BASE_DIR),
                                    entry_text.splitlines()[0],
                                )
                            )
                    i += j
                else:
                    i += 1

            # --- Process Standalone ritual sections ---
            i = 0
            while i < len(lines):
                m = ritual_start.match(lines[i])
                if m:
                    ritual_name = m.group(1).strip()
                    block = [lines[i].rstrip("\n")]
                    j = 1
                    while i + j < len(lines):
                        if ritual_start.match(lines[i + j]):
                            break
                        block.append(lines[i + j].rstrip("\n"))
                        j += 1
                    ritual_text = "\n".join(block).strip()
                    ritual_hash = hash(ritual_text)
                    if ritual_hash not in seen_rituals:
                        seen_rituals.add(ritual_hash)
                        fields = extract_ritual_fields(ritual_text)
                        filename = safe_filename(ritual_name) or "ritual"
                        ritual_file = GRIMOIRE_DIR / f"{filename}.ritual"
                        
                        # ** RESOLVED CONFLICT 3 **
                        if DRY_RUN:
                            print(f"[dry-run] Would write standalone ritual to: {ritual_file}")
                        else:
                            with ritual_file.open("w", encoding="utf-8") as rf:
                                rf.write(f"name: {ritual_name}\n")
                                for key, val in fields.items():
                                    rf.write(f"{key}: |\n")
                                    for l in val.splitlines():
                                        rf.write(f"  {l}\n")

                        # Record standalone ritual output for the summary
                        SUMMARY_LOG.append(
                            (
                                ritual_file.relative_to(BASE_DIR),
                                ritual_text.splitlines()[0],
                            )
                        )
                    i += j
                else:
                    i += 1


def write_combined(entries_dict, out_path: Path, label: str):
    """Writes all found entries of a given type to a single combined markdown file."""
    if not entries_dict:
        print(f"[-] No entries found for {label}. Skipping combined file.")
        return

    output_lines = [f"# {label} – Full Extract\n"]
    for entry_type in sorted(entries_dict.keys()):
        output_lines.append(f"## {entry_type}\n")
        for num in sorted(entries_dict[entry_type].keys()):
            # Use enumerate to handle multiple entries with the same number
            for idx, text in enumerate(entries_dict[entry_type][num], start=1):
                suffix = f" (Part {idx})" if len(entries_dict[entry_type][num]) > 1 else ""
                if num != 99999:
                    title = f"### {label} {entry_type} #{num}{suffix}"
                else:
                    title = f"### {label} {entry_type}{suffix}"
                output_lines.append(title)
                output_lines.append(text)
                output_lines.append("\n---\n") # Separator for clarity
    
    # ** RESOLVED CONFLICT 4 **
    if DRY_RUN:
        print(f"[dry-run] Would write combined file to: {out_path}")
    else:
        print(f"[+] Writing combined file to: {out_path}")
        with out_path.open("w", encoding="utf-8") as out:
            out.write("\n".join(output_lines))


def main():
    """Main function to run the extraction and file writing process."""
    write_combined(entries_am, COMBINED_DIR / "amandamap.md", "AmandaMap")
    write_combined(entries_pc, COMBINED_DIR / "phoenixcodex.md", "Phoenix Codex")
    summary_path = BASE_DIR / "extraction_summary.md"
    with summary_path.open("w", encoding="utf-8") as sfile:
        for rel_path, first_line in SUMMARY_LOG:
            sfile.write(f"{rel_path} | {first_line}\n")
    print(f"[+] Summary written to: {summary_path}")
    print("\n[+] Extraction complete.")


if __name__ == "__main__":
    main()