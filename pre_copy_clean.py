"""
pre_copy_clean.py — Remove large GLPK solver output files (>100 MB) from
MODELS_LAC_4 before copying to MODELS_LAC_5.

Only targets: *_output.txt files greater than 100 MB.
Everything else is left untouched.

Usage:
  python pre_copy_clean.py --root . --dry-run
  python pre_copy_clean.py --root . --yes
"""

import argparse
import os
import shutil
import sys
from datetime import datetime


SIZE_THRESHOLD_MB = 100
SIZE_THRESHOLD_BYTES = SIZE_THRESHOLD_MB * 1024 * 1024


def fmt_size(nbytes):
    if nbytes >= 1 << 30:
        return f"{nbytes / (1 << 30):.2f} GB"
    if nbytes >= 1 << 20:
        return f"{nbytes / (1 << 20):.1f} MB"
    return f"{nbytes / (1 << 10):.0f} KB"


def main():
    parser = argparse.ArgumentParser(
        description="Remove *_output.txt files > 100 MB from MODELS_LAC_4."
    )
    parser.add_argument("--root", required=True, help="Root directory (e.g. '.')")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True)
    mode.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    apply_mode = args.yes

    if not os.path.isdir(root):
        print(f"ERROR: '{root}' is not a directory.")
        sys.exit(1)

    print("=" * 70)
    print("PRE-COPY CLEANUP — large *_output.txt only")
    print("=" * 70)
    print(f"Root:      {root}")
    print(f"Threshold: > {SIZE_THRESHOLD_MB} MB")
    print(f"Mode:      {'APPLY (--yes)' if apply_mode else 'DRY-RUN'}")
    print()

    # Scan
    hits = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if f.endswith("_output.txt"):
                fp = os.path.join(dirpath, f)
                try:
                    sz = os.path.getsize(fp)
                except OSError:
                    continue
                if sz >= SIZE_THRESHOLD_BYTES:
                    hits.append((fp, sz))

    if not hits:
        print("No *_output.txt files > 100 MB found. Nothing to do.")
        return

    total = sum(sz for _, sz in hits)
    print(f"Found {len(hits)} files, {fmt_size(total)} total:\n")
    for fp, sz in sorted(hits):
        print(f"  {fmt_size(sz):>10s}  {os.path.relpath(fp, root)}")
    print()

    if not apply_mode:
        print("DRY-RUN complete. No files moved.")
        print(f'To apply: python pre_copy_clean.py --root "{args.root}" --yes')
        return

    # Apply — move to timestamped destination
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_root = os.path.join(
        os.path.dirname(root),
        f"_PRE_COPY_CLEAN_{os.path.basename(root)}_{timestamp}"
    )

    print("!" * 70)
    print("REMINDER: Pause Dropbox sync before proceeding.")
    print("!" * 70)
    print(f"\nDestination: {dest_root}")
    print(f"Files: {len(hits)}, Size: {fmt_size(total)}\n")

    confirm = input("Type YES to proceed: ").strip()
    if confirm != "YES":
        print("Aborted.")
        return

    os.makedirs(dest_root, exist_ok=True)
    moved = 0
    errors = 0
    for fp, sz in hits:
        rel = os.path.relpath(fp, root)
        dest = os.path.join(dest_root, rel)
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(fp, dest)
            moved += 1
            print(f"  MOVED  {rel}")
        except Exception as e:
            errors += 1
            print(f"  ERROR  {rel}: {e}")

    print(f"\nDone. Moved {moved}, errors {errors}.")
    print(f"Destination: {dest_root}")


if __name__ == "__main__":
    main()
