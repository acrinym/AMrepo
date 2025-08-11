import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# --- CONFIG ---
BASE_DIR = Path(__file__).resolve().parent
SEARCH_DIR = BASE_DIR / "Chats"
OUTPUT_DIR_AM = BASE_DIR / "am"
OUTPUT_DIR_PC = BASE_DIR / "pc"
COMBINED_DIR = BASE_DIR / "Combined"
GRIMOIRE_DIR = BASE_DIR / "grimoire"

# Ensure dirs exist
for base in [OUTPUT_DIR_AM, OUTPUT_DIR_PC, COMBINED_DIR, GRIMOIRE_DIR]:
    base.mkdir(parents=True, exist_ok=True)

# Patterns for AmandaMap/Phoenix Codex entries
start_pattern = re.compile(
    r"^(AmandaMap|Phoenix Codex)\s+[A-Za-z]+\s*(#?\d+|Threshold\s+\d+)?[^\n]*",
    re.IGNORECASE,
)
end_pattern = re.compile(r"^Status:\s?.*", re.IGNORECASE)

# Dict: { "Type" : { num: [entries...] } }
entries_am = defaultdict(lambda: defaultdict(list))
entries_pc = defaultdict(lambda: defaultdict(list))
seen_hashes = set()

# Ritual detection
ritual_start = re.compile(r"^Ritual(?:\s+Name)?[:\-]\s*(.+)", re.IGNORECASE)
ritual_section = re.compile(
    r"^(Ingredients|Steps|Spirits|Directions|Invocations)[:\-]\s*(.*)",
    re.IGNORECASE,
)
seen_rituals = set()


def safe_filename(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]+", "_", text).strip("_")


def detect_type_and_num(line: str):
    m = re.match(r"^(AmandaMap|Phoenix Codex)\s+([A-Za-z]+)\s*#?(\d+)?", line, re.IGNORECASE)
    if not m:
        return None, None
    entry_type = m.group(2).capitalize()
    num = int(m.group(3)) if m.group(3) else 99999
    return entry_type, num


def extract_ritual_fields(text: str):
    fields = {}
    current = None
    for line in text.splitlines():
        m = ritual_section.match(line)
        if m:
            current = m.group(1).lower()
            fields[current] = [m.group(2).strip()] if m.group(2).strip() else []
        elif current:
            if not line.strip():
                current = None
            else:
                fields[current].append(line.strip())
    for k in list(fields.keys()):
        fields[k] = "\n".join(fields[k]).strip()
    return fields


# --- SCAN ---
for root, _, files in os.walk(SEARCH_DIR):
    for file in files:
        if file.lower().endswith(".md"):
            path = Path(root) / file
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # AmandaMap / Phoenix Codex entries
            i = 0
            while i < len(lines):
                if start_pattern.search(lines[i]):
                    block = [lines[i].rstrip("\n")]
                    j = 1
                    while i + j < len(lines):
                        block.append(lines[i + j].rstrip("\n"))
                        if end_pattern.search(lines[i + j]):
                            break
                        # stop at new entry start
                        if start_pattern.search(lines[i + j]):
                            break
                        j += 1
                    entry_text = "\n".join(block).strip()

                    entry_hash = hash(entry_text)
                    if entry_hash in seen_hashes:
                        i += j
                        continue
                    seen_hashes.add(entry_hash)

                    is_am = entry_text.lower().startswith("amandamap")
                    target_dir = OUTPUT_DIR_AM if is_am else OUTPUT_DIR_PC
                    entries_dict = entries_am if is_am else entries_pc
                    label = "AmandaMap" if is_am else "Phoenix Codex"

                    entry_type, num = detect_type_and_num(lines[i])
                    if not entry_type:
                        entry_type = "Unknown"

                    date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", entry_text)
                    if date_match:
                        date_str = date_match.group(1)
                    else:
                        mtime = path.stat().st_mtime
                        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

                    type_folder = target_dir / entry_type
                    type_folder.mkdir(parents=True, exist_ok=True)

                    fname = (
                        f"{entry_type.lower()}-{num}_{date_str}.md"
                        if num != 99999
                        else f"{entry_type.lower()}_{date_str}.md"
                    )
                    with (type_folder / fname).open("w", encoding="utf-8") as out:
                        out.write(entry_text)

                    entries_dict[entry_type][num].append(entry_text)

                    # If this is a ritual, also export to grimoire
                    if entry_type.lower() == "ritual":
                        ritual_name = safe_filename(lines[i].strip())
                        ritual_fields = extract_ritual_fields(entry_text)
                        ritual_path = GRIMOIRE_DIR / f"{ritual_name}.ritual"
                        with ritual_path.open("w", encoding="utf-8") as rfile:
                            rfile.write(f"name: {lines[i].strip()}\n")
                            for key, val in ritual_fields.items():
                                rfile.write(f"{key}: |\n")
                                for l in val.splitlines():
                                    rfile.write(f"  {l}\n")

                    i += j
                else:
                    i += 1

            # Standalone ritual sections
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
                        with ritual_file.open("w", encoding="utf-8") as rf:
                            rf.write(f"name: {ritual_name}\n")
                            for key, val in fields.items():
                                rf.write(f"{key}: |\n")
                                for l in val.splitlines():
                                    rf.write(f"  {l}\n")
                    i += j
                else:
                    i += 1


def write_combined(entries_dict, out_path: Path, label: str):
    output_lines = [f"# {label} – Full Extract\n"]
    for entry_type in sorted(entries_dict.keys()):
        output_lines.append(f"<{entry_type}>")
        for num in sorted(entries_dict[entry_type].keys()):
            for idx, text in enumerate(entries_dict[entry_type][num], start=1):
                suffix = f" Part {idx}" if idx > 1 else ""
                if num != 99999:
                    title = f"### {label} {entry_type} #{num}{suffix}"
                else:
                    title = f"### {label} {entry_type}{suffix}"
                output_lines.append(title)
                output_lines.append(text)
                output_lines.append("")
        output_lines.append(f"</{entry_type}>")
        output_lines.append("")
    with out_path.open("w", encoding="utf-8") as out:
        out.write("\n".join(output_lines))


def main():
    write_combined(entries_am, COMBINED_DIR / "amandamap.md", "AmandaMap")
    write_combined(entries_pc, COMBINED_DIR / "phoenixcodex.md", "Phoenix Codex")
    print("[+] Extraction complete with type-based sections, part-labeling, and ritual export.")


if __name__ == "__main__":
    main()
