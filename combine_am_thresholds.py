#!/usr/bin/env python3
"""Combine AmandaMap entries with the same leading threshold number.

Usage:
    python combine_am_thresholds.py SOURCE_DIR DEST_DIR
The script scans SOURCE_DIR for Markdown files whose names begin with
an integer followed by a hyphen (e.g., ``12-2025-05-02-Threshold 12.md``).
All files sharing the same leading number are concatenated into a single
Markdown file inside DEST_DIR named ``<number>-combined.md``. Each source
file's content is separated by a divider and prefixed with its original
filename for traceability.
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

def combine_thresholds(src: Path, dest: Path) -> int:
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in src.glob('*.md'):
        match = re.match(r'(\d+)-', path.name)
        if match:
            groups[match.group(1)].append(path)
    dest.mkdir(parents=True, exist_ok=True)
    for key, paths in groups.items():
        paths.sort()
        out_path = dest / f"{key}-combined.md"
        with out_path.open('w', encoding='utf-8') as out_file:
            for p in paths:
                out_file.write(f"## {p.name}\n\n")
                out_file.write(p.read_text(encoding='utf-8').strip())
                out_file.write("\n\n---\n\n")
    return len(groups)

def main() -> None:
    parser = argparse.ArgumentParser(description='Combine AmandaMap threshold files by number')
    parser.add_argument('source', type=Path, help='Directory containing AmandaMap files')
    parser.add_argument('dest', type=Path, help='Directory to write combined files')
    args = parser.parse_args()
    count = combine_thresholds(args.source, args.dest)
    print(f'Combined {count} threshold groups.')

if __name__ == '__main__':
    main()
