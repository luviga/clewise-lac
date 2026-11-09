"""
Clean regenerable CSV and Tableau files from country energy folders.

This is a side-quest cleaner, separate from clean_repo_apply.py. It targets
exactly two file kinds that bloat country energy folders without being part
of the active source tree:

  1. CSV files inside each country's energy folder. These are consolidated
     OSeMOSYS inputs/outputs (*Input.csv, *Output.csv, etc.) regenerated on
     every solve. By default only the immediate folder level is cleaned; pass
     --recursive to also clean CSVs under Executables/ and similar nested
     dirs. The protected subdirs (B1_Output_Params, A2_Output_Params) are
     ALWAYS skipped because they hold stable processed parameters that are
     expensive to regenerate.

  2. .twbx / .twbr files anywhere in the project. Tableau packaged workbooks
     used for visualization, not part of the model run.

Files moved to:
    _deprecate_csv/<timestamp>/<original_relative_path>

This is a separate destination from clean_repo_apply.py's _deprecate/ so the
two audit trails stay readable.

Usage:
    py clean_repo_csvs.py --dry-run                 # preview only
    py clean_repo_csvs.py                           # immediate folder level only
    py clean_repo_csvs.py --recursive               # also Executables/ etc.
    py clean_repo_csvs.py --recursive --yes         # skip confirmation prompt

Like the other cleaners, defaults are cautious: interactive confirmation on,
and no CSV is mutated. The destination tree IS the audit trail.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEPRECATE_DIR = "_deprecate_csv"

# Each country's energy folder, relative to the project root.
COUNTRY_ENERGY_DIRS = [
    "DominicanRepublic/RD_ENERGY",
    "Ecuador/ECU_Energy",
    "Guatemala/GUA_ENERGY",
    "Honduras/HON_ENERGY",
    "Jamaica/JAM_ENERGY",
    "CostaRica/CR_ENERGY/t1_confection",
]

# Subdirs inside a country energy folder that must never be touched even in
# --recursive mode. These are the stable processed parameter folders; the
# CSVs in them are NOT regenerated each solve and are expensive to rebuild.
PROTECTED_SUBDIRS = {
    "B1_Output_Params",
    "A2_Output_Params",
}

# Tableau extensions to sweep across the whole project tree.
TABLEAU_SUFFIXES = (".twbx", ".twbr")


def find_country_csvs(root: Path, recursive: bool) -> list[tuple[str, Path]]:
    """Return [(country_label, full_path)] for CSVs to move."""
    out: list[tuple[str, Path]] = []
    for energy_dir in COUNTRY_ENERGY_DIRS:
        base = root / energy_dir
        if not base.exists() or not base.is_dir():
            continue
        country_label = energy_dir.split("/")[0]

        if recursive:
            for path in sorted(base.rglob("*.csv")):
                rel_to_base = path.relative_to(base)
                if any(part in PROTECTED_SUBDIRS for part in rel_to_base.parts):
                    continue
                rel_to_root = path.relative_to(root)
                if rel_to_root.parts and rel_to_root.parts[0].startswith("_deprecate"):
                    continue
                out.append((country_label, path))
        else:
            for path in sorted(base.glob("*.csv")):
                out.append((country_label, path))

    return out


def find_tableau_files(root: Path) -> list[Path]:
    """Return all .twbx/.twbr files in the project, excluding _deprecate*."""
    out: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TABLEAU_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0].startswith("_deprecate"):
            continue
        out.append(path)
    return out


def choose_move_path(dest_root: Path, rel_path: Path) -> Path:
    """Pick a destination, appending an incrementing suffix on collision."""
    target = dest_root / rel_path
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}__{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def print_plan(
    root: Path,
    country_csvs: list[tuple[str, Path]],
    tableau_files: list[Path],
    recursive: bool,
) -> tuple[int, int]:
    """Print the plan grouped by country and Tableau bucket. Return (count, bytes)."""
    print()
    print("Plan")
    print("----")

    if not country_csvs and not tableau_files:
        print("  (nothing to move)")
        return 0, 0

    # CSVs grouped by country
    by_country: dict[str, list[Path]] = {}
    for country, path in country_csvs:
        by_country.setdefault(country, []).append(path)

    total_files = 0
    total_bytes = 0

    for country in sorted(by_country):
        paths = by_country[country]
        n = len(paths)
        size = sum(p.stat().st_size for p in paths if p.exists())
        total_files += n
        total_bytes += size
        scope = "recursive" if recursive else "top-level"
        print(f"  CSVs  {country:24}  {scope:9}  {n:5d} files  {size/(1024*1024):8.2f} MB")

    if tableau_files:
        size = sum(p.stat().st_size for p in tableau_files if p.exists())
        total_files += len(tableau_files)
        total_bytes += size
        print(f"  TWBX  {'(project-wide)':24}  {'':9}  {len(tableau_files):5d} files  {size/(1024*1024):8.2f} MB")

    print(f"  {'TOTAL':6} {'':24}  {'':9}  {total_files:5d} files  {total_bytes/(1024*1024):8.2f} MB")
    return total_files, total_bytes


def confirm(prompt: str) -> bool:
    try:
        reply = input(prompt + " [y/N]: ").strip().lower()
    except EOFError:
        return False
    return reply in {"y", "yes"}


def execute_moves(
    paths: list[Path], dest_root: Path, root: Path
) -> tuple[int, int]:
    """Move each path into dest_root preserving relative structure."""
    moved = 0
    total_bytes = 0
    for source in paths:
        try:
            rel = source.relative_to(root)
        except ValueError:
            print(f"  ! skip (outside root): {source}", file=sys.stderr)
            continue
        if not source.exists():
            continue
        size = source.stat().st_size
        target = choose_move_path(dest_root, rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(source), str(target))
        except OSError as exc:
            print(f"  ! failed: {rel}  ({exc})", file=sys.stderr)
            continue
        moved += 1
        total_bytes += size
    return moved, total_bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--root",
        default=".",
        help="Project root. Default: current directory.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Also clean CSVs in subdirs of each country energy folder (e.g. Executables/). Always skips B1_Output_Params and A2_Output_Params.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be moved without touching anything.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    print(f"Workspace root: {root}")
    print(f"Mode:           {'recursive' if args.recursive else 'top-level only'} CSV cleanup + project-wide Tableau sweep")

    country_csvs = find_country_csvs(root, recursive=args.recursive)
    tableau_files = find_tableau_files(root)

    total_files, total_bytes = print_plan(root, country_csvs, tableau_files, args.recursive)

    if args.dry_run:
        print()
        print("--dry-run: no files moved.")
        return 0

    if total_files == 0:
        print()
        print("Nothing to do.")
        return 0

    if not args.yes:
        print()
        if not confirm("Proceed with these moves?"):
            print("Aborted.")
            return 0

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_root = root / DEPRECATE_DIR / timestamp

    all_paths = [p for _, p in country_csvs] + tableau_files
    moved, moved_bytes = execute_moves(all_paths, dest_root, root)

    print()
    print("Done.")
    print(f"  Moved:        {moved} files  ({moved_bytes/(1024*1024):.2f} MB)")
    print(f"  Destination:  {dest_root.relative_to(root)}")
    print()
    print("The destination tree mirrors the original relative paths, so it's")
    print("the record of what moved. Restore is a manual `Move-Item` away.")
    print()
    print("Note: CSVs in B1_Output_Params/ and A2_Output_Params/ were never")
    print("touched — those hold stable processed parameters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
