#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AmandaMap / Phoenix Codex Reflow
- Finds scattered fragments across exported chats
- Decides "same entry evolving" vs "different entry"
- Merges losslessly
- Renumbers deterministically
Outputs:
  - dist/{YEAR}/{ID}.md            (canonical entries)
  - dist/redirects.json            (cross-day renumbers)
  - dist/reflow_preview.csv        (what changed)
Usage:
  python amandamap_reflow.py --input extracted_entries/ --out dist/ --dry-run
Notes:
  * No external libs required.
  * Designed for plain text or markdown chat exports.
"""

import argparse, csv, json, hashlib, os, re, sys
from collections import defaultdict, namedtuple
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

# ---------- CONFIG ----------

ANCHOR_PHRASES = [
    "ONLY ALWAYS. ONLY AMANDA.",
    "I Wait. That's What I Do.",
    "Amanda is mine, and only mine. And I am hers, and only hers.",
    "Amanda is mine by Divine Right.",
    "The Hawk Descends, The Phoenix Rises",
    "The Icons Return. The Flame Reignites.",
]

TYPE_TOKENS = {
    "threshold": "Threshold",
    "thr": "Threshold",
    "whispered flame": "WhisperedFlame",
    "field pulse": "FieldPulse",
    "fp": "FieldPulse",
    "wf": "WhisperedFlame",
    "phoenix codex": "PhoenixCodex",
    "codex": "PhoenixCodex",
}

# Regex: keep human-readable; compile once.
RX_TYPE_NUM = re.compile(
    r"""(?ix)
    \b(?:
         (threshold|thr) \s* \#? \s* (?P<num_thr>\d{1,3}) |
         (whispered \s* flame|wf) \s* \#? \s* (?P<num_wf>\d{1,3}) |
         (field \s* pulse|fp) \s* \#? \s* (?P<num_fp>\d{1,3}) |
         (phoenix \s* codex|codex) (?!\s*\#?\d)        # usually unnumbered
       )
    \b
    """
)

RX_TITLE_LINE = re.compile(
    r"""(?imx)
    ^\s*
    (?P<title>
       (?:threshold\s*\d+|thr\s*\d+|
          whispered\s*flame(?:\s*\#?\d+)?|
          field\s*pulse(?:\s*\#?\d+)?|
          phoenix\s*codex
       ).*?
    )
    \s*(?:[-–:]\s*(?P<subtitle>.+))?\s*$
    """
)

RX_STATUS = re.compile(r"(?im)\bStatus\s*[:\-–]\s*(?P<status>[^\n]+)")
RX_DATE_INLINE = re.compile(r"(?i)\b(?:date|on)\s*[:\-–]\s*(\d{4}-\d{2}-\d{2})")
RX_DATE_BRACKET = re.compile(r"\[(\d{4}-\d{2}-\d{2})\]")
RX_TIMESTAMP = re.compile(r"\b(\d{2}:\d{2}:\d{2})\b")

# ---------- MODELS ----------

Fragment = namedtuple("Fragment", "type number title date time status anchors content src_chat src_idx raw_hash")

class CanonicalEntry:
    def __init__(self, etype, number, date_iso):
        self.etype = etype                  # Threshold / WhisperedFlame / FieldPulse / PhoenixCodex
        self.number = number                # int or None until final
        self.date = date_iso                # "YYYY-MM-DD"
        self.parts = []                     # list of (part_letter, Fragment)
        self.status = None
        self.anchors = set()
        self.prev_ids = []
        self.redirects_from = []            # list of dicts
        self.merge_log = []
        self.title = None                   # best derived
        self.id = None                      # stable id after assign
        self.year = self.date[:4]

    def to_markdown(self):
        parts_md = []
        for letter, frag in self.parts:
            header = f"## Part {letter}" if letter else "## Part"
            parts_md.append(
f"""{header}
**Source**: {frag.src_chat}#{frag.src_idx}  
**Time**: {frag.time or '—'}  
**Status (this part)**: {frag.status or '—'}

{frag.content.strip()}
""")
        anchors_md = "".join([f"- {a}\n" for a in sorted(self.anchors)]) if self.anchors else "—\n"
        redirects_md = ""
        if self.redirects_from:
            for r in self.redirects_from:
                redirects_md += f"- From #{r['number']} on {r['date']}: {r['reason']}\n"
        else:
            redirects_md = "—\n"
        mergelog_md = ""
        if self.merge_log:
            for m in self.merge_log:
                mergelog_md += f"- {m}\n"
        else:
            mergelog_md = "—\n"

        title_line = self.title or f"{self.etype} {self.number if self.number is not None else ''}".strip()
        return f"""# {title_line}
**Type**: {self.etype}  
**ID**: {self.id or 'unassigned'}  
**Number**: {self.number if self.number is not None else 'unassigned'}  
**Date**: {self.date}  
**Status (final)**: {self.status or '—'}  

### Anchors
{anchors_md}
### Redirects
{redirects_md}
### Merge Log
{mergelog_md}
### Parts
{''.join(parts_md)}
"""

# ---------- HELPERS ----------

def sha256_text(t:str)->str:
    return hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()

def normalize_text(t:str)->str:
    # Keep punctuation, emojis; collapse whitespace; lowercase except protected anchors
    lowered = t
    for a in ANCHOR_PHRASES:
        lowered = lowered.replace(a, f"[[ANCHOR::{a}]]")
    lowered = lowered.lower()
    for a in ANCHOR_PHRASES:
        lowered = lowered.replace(f"[[anchor::{a.lower()}]]", a)
    return re.sub(r"\s+", " ", lowered).strip()

def jaccard_3gram(a:str,b:str)->float:
    def grams(s):
        s=f"  {s}  "
        return {s[i:i+3] for i in range(len(s)-2)}
    A,B=grams(a),grams(b)
    if not A or not B: return 0.0
    return len(A&B)/len(A|B)

def text_sim(a:str,b:str)->float:
    # conservative max of difflib ratio and 3-gram Jaccard
    return max(SequenceMatcher(None,a,b).ratio(), jaccard_3gram(a,b))

def detect_type_number(text:str):
    m = RX_TYPE_NUM.search(text)
    if not m: return (None, None)
    raw = m.group(0).lower()
    etype = None
    for token, label in TYPE_TOKENS.items():
        if token in raw:
            etype = label
            break
    num = None
    for k in ("num_thr","num_wf","num_fp"):
        if m.groupdict().get(k):
            num = int(m.groupdict()[k])
            break
    return (etype, num)

def scan_status(text:str):
    mm = RX_STATUS.findall(text)
    return mm[-1].strip() if mm else None

def scan_date(text:str):
    for rx in (RX_DATE_INLINE, RX_DATE_BRACKET):
        m = rx.search(text)
        if m:
            for g in m.groups():
                if g: return g
    return None

def scan_time(text:str):
    m = RX_TIMESTAMP.search(text)
    return m.group(1) if m else None

def scan_title(text:str):
    m = RX_TITLE_LINE.search(text)
    if not m: return None
    t = m.group("title").strip()
    sub = m.group("subtitle")
    return f"{t} — {sub.strip()}" if sub else t

def scan_anchors(text:str):
    found = []
    for a in ANCHOR_PHRASES:
        if a in text:
            found.append(a)
    return found

def guess_date_from_filename(fname:str):
    # e.g., "0904T18:26 ..." → we only know month/day? If you embed YYYY in export, prefer real parser.
    # Fallback to today to avoid None; better: pass --default-year
    return None

# ---------- EXTRACTION ----------

def load_fragments(input_dir:Path, default_year:str=None):
    """
    Very simple splitter:
    - Treat each line block separated by blank lines as a potential fragment.
    - Real-world: you may want to split on message boundaries from your export.
    """
    frags = []
    for p in Path(input_dir).rglob("*"):
        if p.is_dir(): continue
        if p.suffix.lower() not in (".txt",".md",".markdown",".log"): continue
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            content_all = f.read()

        # Better splitting: treat each file as a single fragment if it contains our content
        # This preserves the full content of each file
        text = content_all.strip()
        if not text: continue
        
        etype, num = detect_type_number(text)
        if not etype:
            # Skip unless it looks strongly like our domain (title or anchors)
            if not scan_title(text) and not scan_anchors(text):
                continue
            # If it has title/anchors, treat as fragment with unknown type
            # Heuristic: infer from title if possible
            tit = scan_title(text) or ""
            t_low = tit.lower()
            for token,label in TYPE_TOKENS.items():
                if token in t_low:
                    etype = label; break
            if not etype:
                continue

        date = scan_date(text)
        if not date:
            # try filename inference or fallback
            date = guess_date_from_filename(p.name) or (default_year and f"{default_year}-01-01") or "1900-01-01"

        time = scan_time(text)
        status = scan_status(text)
        title = scan_title(text)
        anchors = scan_anchors(text)
        raw_hash = "sha256:"+sha256_text(text)
        frags.append(Fragment(
            type=etype, number=num, title=title, date=date, time=time,
            status=status, anchors=anchors, content=text,
            src_chat=p.name, src_idx=0, raw_hash=raw_hash
        ))
    return frags

# ---------- GROUPING / MERGE ----------

def same_day(d1,d2): return d1==d2

def decide_same_entry(fa:Fragment, fb:Fragment):
    """
    Returns one of: "same-day-part", "cross-day-merge-candidate", "different"
    """
    na, nb = normalize_text(fa.content), normalize_text(fb.content)
    sim = text_sim(na, nb)
    anchor_overlap = 0.0
    if fa.anchors or fb.anchors:
        sa, sb = set(fa.anchors), set(fb.anchors)
        anchor_overlap = len(sa & sb) / len(sa | sb)

    if same_day(fa.date, fb.date):
        if sim >= 0.60 or anchor_overlap >= 0.5:
            return "same-day-part"
        return "different"
    else:
        # cross-day
        if sim >= 0.80 and anchor_overlap >= 0.5:
            return "cross-day-merge-candidate"
        return "different"

def build_canonicals(fragments):
    # first pass: bucket by (type, explicit number if present else None)
    buckets = defaultdict(list)
    for fr in fragments:
        key = (fr.type, fr.number if fr.number is not None else None)
        buckets[key].append(fr)

    canon = []              # list of CanonicalEntry
    review_pairs = []        # (fa, fb) cross-day candidates for manual look (we'll auto-new-number by default)

    # Within each type bucket, cluster by date/title/sim
    for (etype, num_hint), frs in buckets.items():
        # pre-sort by date/time
        def ts(f):
            t = f.time or "00:00:00"
            return (f.date, t)
        frs.sort(key=ts)

        used = set()
        for i, f in enumerate(frs):
            if i in used: continue
            # Start a new canonical seed
            entry = CanonicalEntry(etype, f.number, f.date)
            entry.title = f.title
            # collect same-day parts
            same_day_group = [(None, f)]
            used.add(i)
            for j in range(i+1, len(frs)):
                if j in used: continue
                g = frs[j]
                decision = decide_same_entry(f, g)
                if decision == "same-day-part":
                    same_day_group.append((None, g))
                    used.add(j)
                elif decision == "cross-day-merge-candidate":
                    # Record for info; we'll default to new number later
                    review_pairs.append((f,g))
                # else different → ignore here

            # Assign parts letters by time
            same_day_group.sort(key=lambda x: (x[1].time or "00:00:00"))
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for idx_part, (_, frag) in enumerate(same_day_group):
                letter = letters[idx_part] if idx_part < len(letters) and len(same_day_group) > 1 else None
                entry.parts.append((letter, frag))
                if frag.status: entry.status = frag.status
                entry.anchors.update(frag.anchors)
                if not entry.title and frag.title: entry.title = frag.title

            canon.append(entry)

    return canon, review_pairs

def lossless_merge(entry:CanonicalEntry):
    """
    Build a canonical content out of parts without losing wording.
    Policy: keep parts intact; canonical 'Status' is from last part with a Status.
    We already store every part, so the Markdown shows all raw texts.
    """
    # nothing to do here beyond ensuring final status & merge log
    # If you want a single "content" block, you could build it here by sentence union.
    if not entry.status:
        # try last part's status
        for letter, frag in reversed(entry.parts):
            if frag.status:
                entry.status = frag.status
                break
    # Merge log sample
    srcs = [f"{frag.src_chat}#{frag.src_idx}" for _, frag in entry.parts]
    entry.merge_log.append(f"Merged {len(entry.parts)} parts from {', '.join(srcs)}")

def assign_stable_ids_and_numbers(entries, series_prefix_map=None):
    """
    Deterministic numbering:
      - Stable ID: PREFIX-year-seq (seq filled later)
      - Within type, sort by date/time; numbers rise over time
      - Cross-day same-number collisions -> new number + redirect record
    """
    # Map type -> prefix
    prefix_map = {"Threshold":"THR","WhisperedFlame":"WF","FieldPulse":"FP","PhoenixCodex":"PC"}
    if series_prefix_map: prefix_map.update(series_prefix_map)

    # By type, then by date/time (first part time if any)
    grouped = defaultdict(list)
    for e in entries:
        grouped[e.etype].append(e)

    redirects = []
    preview_rows = []

    for etype, lst in grouped.items():
        def first_time(e):
            return e.parts[0][1].time or "00:00:00" if e.parts else "00:00:00"
        lst.sort(key=lambda e: (e.date, first_time(e), (e.number if e.number is not None else 10**9)))

        # number assignment
        used_numbers = set()
        next_num = 1
        for e in lst:
            # pick target number:
            original = e.number
            # If original available and unused on this date, keep it.
            if original is not None and original not in used_numbers:
                e.number = original
                used_numbers.add(original)
                next_num = max(next_num, original+1)
            else:
                # assign next free number
                while next_num in used_numbers: next_num += 1
                e.number = next_num
                used_numbers.add(next_num)
                next_num += 1

            # Build ID
            prefix = prefix_map.get(etype, "XX")
            e.id = f"{prefix}-{e.date[:4]}-{e.number:04d}"

            # Redirect note if we changed number from a conflicting same-number-on-different-day scenario
            if original is not None and original != e.number:
                redirects.append({
                    "type": etype,
                    "from": {"number": original, "date": e.date},
                    "to": {"number": e.number, "id": e.id},
                    "reason": "cross-day collision; renumbered deterministically"
                })

            # Preview CSV row
            parts_count = len(e.parts)
            preview_rows.append({
                "etype": etype,
                "date": e.date,
                "id": e.id,
                "number": e.number,
                "parts": parts_count,
                "status": e.status or "",
                "title": e.title or ""
            })

    return redirects, preview_rows

# ---------- I/O ----------

def ensure_dir(p:Path): p.mkdir(parents=True, exist_ok=True)

def write_outputs(entries, redirects, preview_rows, out_dir:Path, dry_run:bool):
    if dry_run:
        # Show a concise console preview
        print("DRY RUN: would create the following entries:")
        for r in preview_rows[:50]:
            print(f"  {r['date']}  {r['etype']:<15} #{r['number']:>3}  {r['id']}  parts={r['parts']}  {r['title'][:60]}")
        if len(preview_rows) > 50:
            print(f"... and {len(preview_rows)-50} more")
        print("\nDRY RUN: would write redirects:", len(redirects))
        return

    # Write Markdown files
    for e in entries:
        ensure_dir(out_dir / e.year)
        path = out_dir / e.year / f"{e.id}.md"
        with path.open("w", encoding="utf-8") as f:
            f.write(e.to_markdown())

    # Write redirects.json
    with (out_dir / "redirects.json").open("w", encoding="utf-8") as f:
        json.dump({"redirects": redirects}, f, indent=2)

    # Write preview CSV
    with (out_dir / "reflow_preview.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["etype","date","id","number","parts","status","title"])
        w.writeheader()
        for r in preview_rows:
            w.writerow(r)

# ---------- MAIN ----------

def main():
    ap = argparse.ArgumentParser(description="AmandaMap/PhoenixCodex Reflow")
    ap.add_argument("--input", required=True, help="Directory with exported chats (.md/.txt)")
    ap.add_argument("--out", required=True, help="Output directory (will create dist)")
    ap.add_argument("--default-year", help="Fallback year if dates are missing (e.g., 2025)")
    ap.add_argument("--dry-run", action="store_true", help="Show preview only, write nothing")
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.out)

    frags = load_fragments(in_dir, default_year=args.default_year)
    if not frags:
        print("No fragments detected. Check input path or adjust split logic.", file=sys.stderr)
        sys.exit(1)

    canon, review_pairs = build_canonicals(frags)
    for e in canon:
        lossless_merge(e)

    redirects, preview_rows = assign_stable_ids_and_numbers(canon)

    ensure_dir(out_dir)
    write_outputs(canon, redirects, preview_rows, out_dir, dry_run=args.dry_run)

    # Optional: dump review hints (not blocking)
    if review_pairs:
        print(f"\nNote: {len(review_pairs)} cross-day continuation candidates detected (auto-new-number applied).")
        print("If you want, add a manual pass to convert specific ones into multi-day parts.")

if __name__ == "__main__":
    main()
