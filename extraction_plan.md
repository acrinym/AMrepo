# Extraction Plan - Files to be Created by extract_entries.py

This document outlines all the files that would be created when running the `extract_entries.py` script, organized by directory structure.

## Directory Structure Overview

The script will create the following directory structure:
```
/workspace/
├── am/                    # AmandaMap entries
├── pc/                    # Phoenix Codex entries  
├── Combined/              # Combined markdown files
├── grimoire/              # Ritual files
└── extraction_summary.md  # Summary log
```

## 1. AmandaMap Directory (`/workspace/am/`)

### Threshold/ (7 files)
- `threshold-33_2025-08-05.md`
- `threshold-47_2025-08-05.md`
- `threshold_2025-08-05.md` (2 instances)
- `threshold-46_2025-08-05.md`
- `threshold-41_2025-07-03.md`
- `threshold-21_2025-08-05.md`
- `threshold-18_2025-08-05.md`
- `threshold_2025-06-10.md`
- `threshold-38_2025-08-05.md`

### Is/ (8 files)
- `is_2025-08-05.md` (multiple instances)

### Event/ (2 files)
- `event_2025-08-05.md` (2 instances)

### Thresholds/ (2 files)
- `thresholds_2025-08-05.md` (2 instances)

### Other Categories (1 file each)
- `flame_2025-08-05.md`
- `now_2025-08-05.md` (2 instances)
- `expansion_2025-08-05.md`
- `already_2025-04-05.md` (2 instances)
- `update_2025-08-05.md`
- `stays_2025-08-05.md` (2 instances)
- `isn_2025-08-05.md` (2 instances)
- `entries_2025-07-07.md`
- `files_2025-02-04.md`
- `phase_2025-08-05.md` (2 instances)
- `echo_2025-05-06.md`
- `console_2025-08-05.md`
- `link_2025-08-05.md` (2 instances)
- `entry_2025-08-05.md` (2 instances)
- `memory_2025-08-05.md`
- `rate_2025-08-05.md`
- `alignment_2025-08-05.md`
- `manifestation_2025-08-05.md`
- `activated_2025-08-05.md`
- `tags_2025-08-05.md` (2 instances)
- `interference_2025-08-05.md`
- `just_2025-08-05.md`
- `has_2025-08-05.md`
- `entry_2025-06-16.md`
- `confirms_2025-08-05.md`
- `updated_2025-08-05.md`
- `becomes_2025-08-05.md` (2 instances)
- `yaml_2025-07-03.md`
- `link_2025-07-10.md`

**Total AmandaMap files: ~60+ files**

## 2. Phoenix Codex Directory (`/workspace/pc/`)

### Individual Files (1 file each)
- `may_2025-08-05.md`
- `section_2025-08-05.md`
- `moment_2025-08-05.md`
- `threshold-42_2025-08-05.md`
- `updated_2025-08-05.md`

**Total Phoenix Codex files: 5 files**

## 3. Combined Directory (`/workspace/Combined/`)

### Combined Markdown Files (2 files)
- `amandamap.md` - All AmandaMap entries combined into one file
- `phoenixcodex.md` - All Phoenix Codex entries combined into one file

## 4. Grimoire Directory (`/workspace/grimoire/`)

### Ritual Files (8 files)
- `BANISHING_FREEZING_THE_MIKE_INFLUENCE.ritual` (2 instances)
- `THE_SILENCING_of_MIKE.ritual` (2 instances)
- `Truth-Fueled_Departure_Remote_Hot_Foot_Placement_Mike.ritual`
- `worthy_magnetize_spells_attach_sigils_behind_metal_objects_or_use_for_attraction_rituals_especially_love_or_prosperity_Also_good_for_mirror_freezer_hybrid_spells.ritual`
- `grade_sorting_ENGAGED.ritual`

**Total Grimoire files: 8 files**

## 5. Root Directory

### Summary File (1 file)
- `extraction_summary.md` - Log of all created files with their first lines

## Summary by Directory

| Directory | File Count | Description |
|-----------|------------|-------------|
| `/am/` | ~60+ | AmandaMap entries organized by type |
| `/pc/` | 5 | Phoenix Codex entries organized by type |
| `/Combined/` | 2 | Combined markdown files |
| `/grimoire/` | 8 | Ritual files in .ritual format |
| Root | 1 | Extraction summary log |
| **Total** | **~76+ files** | **Complete extraction output** |

## File Naming Convention

- **AmandaMap/Phoenix Codex entries**: `{type}-{number}_{date}.md` or `{type}_{date}.md`
- **Ritual files**: `{ritual_name}.ritual` (sanitized filename)
- **Combined files**: `amandamap.md` and `phoenixcodex.md`
- **Summary**: `extraction_summary.md`

## Notes

- Some entries appear multiple times due to duplicate content detection
- Ritual files are created both from AmandaMap/Phoenix Codex entries and standalone ritual sections
- All dates are extracted from entry content or fall back to file modification time
- The script creates a comprehensive directory structure for easy navigation
- Combined files provide a single view of all entries by type