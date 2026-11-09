#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 1 CLEANUP: Remove all _STAGE1_OUTPUT artifacts
======================================================
Removes everything Stage 1 v10 created. Stage 0 outputs untouched.

Usage:
  py stage1_clean.py              (preview — shows what would be deleted)
  py stage1_clean.py --confirm    (actually deletes)
"""

import sys, shutil, argparse
from pathlib import Path

MODELS_LAC_ROOT = "./"
OUTPUT_DIR = "_STAGE1_OUTPUT"


def main():
    parser = argparse.ArgumentParser(description="Remove all Stage 1 artifacts")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually delete (without this flag, just previews)")
    args = parser.parse_args()

    root = Path(MODELS_LAC_ROOT).resolve()
    to_delete = []

    # _STAGE1_OUTPUT/ directory
    stage1_out = root / OUTPUT_DIR
    if stage1_out.exists():
        to_delete.append(stage1_out)

    if not to_delete:
        print("Nothing to clean. Stage 1 has not been run.")
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
        print(f"\nDry run. To delete, run:  py stage1_clean.py --confirm")
        return

    for p in to_delete:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print(f"  Deleted: {p.relative_to(root)}")

    print(f"\nClean. Ready to re-run stage1_test_v10.py.")


if __name__ == "__main__":
    main()
