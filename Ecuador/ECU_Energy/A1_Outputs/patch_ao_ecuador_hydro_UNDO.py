#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
patch_ao_ecuador_hydro_UNDO.py — Revert A-O to pre-patch backup
=================================================================
Finds the most recent _BACKUP_ file and restores it over the current A-O.

Run from the Ecuador model directory:
  py patch_ao_ecuador_hydro_UNDO.py [--dry-run]
"""

import sys
import shutil
import argparse
from pathlib import Path

AO_FILE = "A-O_Parametrization.xlsx"
BACKUP_PATTERN = "A-O_Parametrization_BACKUP_*.xlsx"


def main():
    parser = argparse.ArgumentParser(description="Revert A-O to pre-patch backup")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--file", default=AO_FILE)
    args = parser.parse_args()

    ao_path = Path(args.file)
    backups = sorted(ao_path.parent.glob(BACKUP_PATTERN))

    if not backups:
        print(f"[ERROR] No backup files matching {BACKUP_PATTERN} found")
        sys.exit(1)

    latest = backups[-1]
    print(f"Found {len(backups)} backup(s):")
    for b in backups:
        tag = " ← latest" if b == latest else ""
        print(f"  {b.name}  ({b.stat().st_size:,} bytes){tag}")

    if not ao_path.exists():
        print(f"\n[WARN] {ao_path} not found — restoring from backup anyway")

    if args.dry_run:
        print(f"\n[DRY RUN] Would restore {latest.name} → {ao_path.name}")
    else:
        shutil.copy2(latest, ao_path)
        print(f"\n[RESTORED] {latest.name} → {ao_path.name}")
        print(f"[OK] A-O reverted to pre-patch state")
        print(f"\nTo re-run pipeline with original (broken) A-O:")
        print(f"  py A2_compiler.py --countries Ecuador")
        print(f"  py B1_scenario_config.py --countries Ecuador")


if __name__ == "__main__":
    main()
