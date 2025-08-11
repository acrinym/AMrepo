#!/usr/bin/env python3
"""
am_pc_extract_strict.py — Deterministic extractor for AmandaMap / Phoenix Codex entries.
- No regex (pattern-free, title-only detection).
- Start-of-line markers only (after stripping heading/bullets).
- Threshold / Whispered Flame / Field Pulse must include a number.
- Blocks must look like real entries (min length or early Date/Status).
- Outputs JSONL + per-entry Markdown under ./out by default.

Usage:
  python am_pc_extract_strict.py <root_folder> [--out OUTDIR] [--no-files] [--require-meta]
"""

import sys, json
from pathlib import Path
from datetime import datetime

SEPARATORS = [":", " – ", " — ", " - "]
HARD_STOPS = ["### ", "## ", "# ", "----", "---", "***"]
MAX_BLANK_STREAK = 2
MIN_BLOCK_LINES = 3  # if fewer lines, require early Date/Status to accept

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
    for ext in (".md", ".txt"):
        files.extend(root.rglob(f"*{ext}"))
    return files

def extract_blocks(paths, require_meta=False, verbose=False):
    entries = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = text.splitlines()
        current = None
        blank_streak = 0

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
                entries.append({
                    "source_file": str(current["source"]),
                    "scope": current["scope"],
                    "subtype": current["subtype"],
                    "title": title.strip(),
                    "number": number,
                    "date": date,
                    "content": "\n".join(raw_lines).strip()
                })
            current = None

        i = 0
        while i < len(lines):
            raw = lines[i]
            n = normalize_line(raw)
            start, scope, subtype = detect_start(raw, require_meta=require_meta)
            if start:
                close()
                current = {"source": p, "scope": scope, "subtype": subtype, "lines": [raw]}
                blank_streak = 0
                i += 1
                continue
            if current:
                if is_hard_stop(n):
                    close(); i += 1; continue
                if not n:
                    blank_streak += 1
                    if blank_streak >= MAX_BLANK_STREAK:
                        close(); i += 1; continue
                else:
                    blank_streak = 0
                # stop if next line begins a new block
                nxt = lines[i] if i < len(lines) else ""
                if nxt:
                    s2,_,_ = detect_start(nxt, require_meta=require_meta)
                    if s2:
                        close(); i += 1; continue
                current["lines"].append(raw)
            i += 1
        close()
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
    entries = extract_blocks(files, require_meta=require_meta)
    write_outputs(entries, out_dir, write_files)
    print(f"Scanned {len(files)} files → found {len(entries)} entries.")
    print(f"Wrote JSONL to {out_dir/'combined'}; per-entry MD: {write_files}")

if __name__ == "__main__":
    main()
