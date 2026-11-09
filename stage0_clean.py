#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 0 CLEANUP: Remove all _S0 artifacts
===========================================
Removes everything Stage 0 created. Original repo files untouched.

Usage:
  python stage0_clean.py              (preview — shows what would be deleted)
  python stage0_clean.py --confirm    (actually deletes)
"""

import os, sys, shutil, argparse
from pathlib import Path

MODELS_LAC_ROOT = "./"
SUFFIX = "_S0"
OUTPUT_DIR = "_STAGE0_OUTPUT"

COUNTRY_CONFIG = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}

def main():
    parser = argparse.ArgumentParser(description="Remove all Stage 0 artifacts")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually delete (without this flag, just previews)")
    args = parser.parse_args()

    root = Path(MODELS_LAC_ROOT).resolve()
    to_delete = []

    # 1. Executables/{scenario}_S0_0/ folders
    for country, model_dir in COUNTRY_CONFIG.items():
        exec_dir = root / country / model_dir / "Executables"
        if exec_dir.exists():
            for d in exec_dir.iterdir():
                if d.is_dir() and SUFFIX in d.name:
                    to_delete.append(d)

    # 2. _STAGE0_OUTPUT/ directory
    stage0_out = root / OUTPUT_DIR
    if stage0_out.exists():
        to_delete.append(stage0_out)

    # 3. Generated batch/shell scripts
    for fname in ["stage0_run_all.bat", "stage0_run_all.sh"]:
        p = root / fname
        if p.exists():
            to_delete.append(p)

    if not to_delete:
        print("Nothing to clean. Stage 0 has not been run.")
        return

    print(f"{'PREVIEW' if not args.confirm else 'DELETING'} — {len(to_delete)} items:\n")
    total_size = 0
    for p in sorted(to_delete):
        if p.is_dir():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            total_size += size
            print(f"  [DIR]  {p.relative_to(root)}  ({size/1e6:.1f} MB)")
        else:
            size = p.stat().st_size
            total_size += size
            print(f"  [FILE] {p.relative_to(root)}  ({size/1e3:.1f} KB)")

    print(f"\nTotal: {total_size/1e6:.1f} MB")

    if not args.confirm:
        print(f"\nDry run. To delete, run:  python stage0_clean.py --confirm")
        return

    for p in to_delete:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print(f"  Deleted: {p.relative_to(root)}")

    print(f"\nClean. Ready to re-run stage0_run.py.")

if __name__ == "__main__":
    main()
