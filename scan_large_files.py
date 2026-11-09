"""
scan_large_files.py — Find all files above a size threshold.
Read-only, touches nothing.

Usage:
  python scan_large_files.py --root . --mb 50
  python scan_large_files.py --root . --mb 10
"""

import argparse
import os


def fmt_size(nbytes):
    if nbytes >= 1 << 30:
        return f"{nbytes / (1 << 30):.2f} GB"
    if nbytes >= 1 << 20:
        return f"{nbytes / (1 << 20):.1f} MB"
    return f"{nbytes / (1 << 10):.0f} KB"


def main():
    parser = argparse.ArgumentParser(description="Find all files above a size threshold.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--mb", type=int, default=50, help="Size threshold in MB (default: 50)")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    threshold = args.mb * 1024 * 1024

    print(f"Scanning {root} for files > {args.mb} MB ...\n")

    hits = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            fp = os.path.join(dirpath, f)
            try:
                sz = os.path.getsize(fp)
            except OSError:
                continue
            if sz >= threshold:
                hits.append((fp, sz))

    if not hits:
        print("None found.")
        return

    # Group by extension
    by_ext = {}
    for fp, sz in hits:
        ext = os.path.splitext(fp)[1].lower() or "(no ext)"
        by_ext.setdefault(ext, []).append((fp, sz))

    total = sum(sz for _, sz in hits)
    print(f"Found {len(hits)} files, {fmt_size(total)} total\n")

    for ext in sorted(by_ext.keys()):
        items = sorted(by_ext[ext], key=lambda x: x[0])
        ext_total = sum(sz for _, sz in items)
        print(f"--- {ext} ({len(items)} files, {fmt_size(ext_total)}) ---")
        for fp, sz in items:
            print(f"  {fmt_size(sz):>10s}  {os.path.relpath(fp, root)}")
        print()


if __name__ == "__main__":
    main()
