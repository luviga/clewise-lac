#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stage2_post_clean.py — Remove large GLPK output files from Executables/.
=========================================================================

Finds and removes output*.txt files from Stage 0 run folders that
saturate Dropbox. Dry-run by default.

Usage (from MODELS_LAC_4):
  py stage2_post_clean.py                    (dry run — shows what would be deleted)
  py stage2_post_clean.py --yes              (actually delete)
  py stage2_post_clean.py --pattern "*_S0_*" (only Stage 0 folders)
"""

import argparse
import sys
from pathlib import Path

COUNTRY_CONFIG = {
    "CostaRica": "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador": "ECU_Energy",
    "Guatemala": "GUA_ENERGY",
    "Honduras": "HON_ENERGY",
    "Jamaica": "JAM_ENERGY",
}


def find_output_files(root, folder_pattern="*_S0_*"):
    """Find solver output files in Executables subfolders."""
    targets = []
    for country, model_dir in sorted(COUNTRY_CONFIG.items()):
        exec_dir = root / country / model_dir / "Executables"
        if not exec_dir.exists():
            continue
        for folder in exec_dir.glob(folder_pattern):
            if not folder.is_dir():
                continue
            for f in folder.iterdir():
                name_lower = f.name.lower()
                if ("output" in name_lower and name_lower.endswith(".txt")) or \
                   name_lower.endswith(".sol") or \
                   name_lower.endswith(".log"):
                    targets.append(f)
    return targets


def fmt_size(nbytes):
    if nbytes >= 1_073_741_824:
        return f"{nbytes / 1_073_741_824:.1f} GB"
    if nbytes >= 1_048_576:
        return f"{nbytes / 1_048_576:.1f} MB"
    if nbytes >= 1024:
        return f"{nbytes / 1024:.1f} KB"
    return f"{nbytes} B"


def main():
    p = argparse.ArgumentParser(description="Stage 2 Post-Cleaner")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--yes", action="store_true", help="Actually delete (default: dry run)")
    p.add_argument("--pattern", default="*_S0_*",
                   help="Folder glob pattern (default: *_S0_* for Stage 0 runs)")
    p.add_argument("--all-runs", action="store_true",
                   help="Clean ALL Executables subfolders, not just S0")
    args = p.parse_args()

    root = args.root.resolve()
    pattern = "*" if args.all_runs else args.pattern

    print("=" * 60)
    print("STAGE 2 POST-CLEANER")
    print(f"  Root: {root}")
    print(f"  Pattern: {pattern}")
    print(f"  Mode: {'DELETE' if args.yes else 'DRY RUN'}")
    print("=" * 60)

    targets = find_output_files(root, pattern)

    if not targets:
        print("\nNo output files found. Nothing to clean.")
        return

    # Group by country
    by_country = {}
    total_bytes = 0
    for f in targets:
        size = f.stat().st_size
        total_bytes += size
        # Extract country from path
        parts = f.parts
        for c in COUNTRY_CONFIG:
            if c in parts:
                by_country.setdefault(c, []).append((f, size))
                break
        else:
            by_country.setdefault("Unknown", []).append((f, size))

    print(f"\nFound {len(targets)} files, total {fmt_size(total_bytes)}:\n")
    for country in sorted(by_country):
        files = by_country[country]
        country_bytes = sum(s for _, s in files)
        print(f"  {country}: {len(files)} files, {fmt_size(country_bytes)}")
        for f, size in sorted(files, key=lambda x: -x[1])[:3]:
            print(f"    {f.parent.name}/{f.name}: {fmt_size(size)}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")

    if not args.yes:
        print(f"\n[DRY RUN] Would delete {len(targets)} files ({fmt_size(total_bytes)})")
        print(f"Run with --yes to delete.")
        return

    # Delete
    deleted = 0
    freed = 0
    for f in targets:
        size = f.stat().st_size
        try:
            f.unlink()
            deleted += 1
            freed += size
        except Exception as e:
            print(f"  [ERR] {f}: {e}")

    print(f"\n[DONE] Deleted {deleted}/{len(targets)} files, freed {fmt_size(freed)}")


if __name__ == "__main__":
    main()
