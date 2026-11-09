"""
Clean up scenario subfolders that aren't BAU / NDCNEW / LTSNEW / Default.

Targets the A2_Output_Params, B1_Output_Params, and Executables directories
for all six countries:

  CostaRica         CR_ENERGY/t1_confection/{A2,B1}_Output_Params, Executables
  DominicanRepublic RD_ENERGY/{A2,B1}_Output_Params, Executables
  Ecuador           ECU_Energy/{A2,B1}_Output_Params, Executables    (note: lowercase 'Energy')
  Guatemala         GUA_ENERGY/{A2,B1}_Output_Params, Executables
  Honduras          HON_ENERGY/{A2,B1}_Output_Params, Executables
  Jamaica           JAM_ENERGY/{A2,B1}_Output_Params, Executables

In each, looks at the immediate subdirectories. A subdirectory's name is
considered "allowed" if, after stripping an optional `_0` suffix, it
matches (case-insensitively) one of BAU / NDCNEW / LTSNEW / Default.
Allowed subdirs stay; everything else moves.

The `_0` tolerance is there because Executables/ folders use names like
`BAU_0`, `LTSNEW_0` — these are kept exactly as-is, not renamed.

Files (as opposed to subdirectories) at the top level of each target dir
are left alone.

Moves go to:
    _deprecate_scenarios/<timestamp>/<original_relative_path>

Usage:
    py clean_repo_scenarios.py --dry-run    # preview only
    py clean_repo_scenarios.py              # interactive
    py clean_repo_scenarios.py --yes        # skip confirmation prompt

Target directories that don't exist are skipped with a notice (e.g., if a
country hasn't been set up yet in this working copy).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEPRECATE_DIR = "_deprecate_scenarios"

# Directories whose immediate subdirectories will be inspected.
# Note the path quirks:
#   - Costa Rica has an extra `t1_confection` level
#   - Ecuador uses `ECU_Energy` (lowercase 'e'), all others use uppercase `_ENERGY`
TARGET_DIRS = [
    # Costa Rica (t1_confection nesting)
    "CostaRica/CR_ENERGY/t1_confection/A2_Output_Params",
    "CostaRica/CR_ENERGY/t1_confection/B1_Output_Params",
    "CostaRica/CR_ENERGY/t1_confection/Executables",

    # Dominican Republic
    "DominicanRepublic/RD_ENERGY/A2_Output_Params",
    "DominicanRepublic/RD_ENERGY/B1_Output_Params",
    "DominicanRepublic/RD_ENERGY/Executables",

    # Ecuador (lowercase 'Energy')
    "Ecuador/ECU_Energy/A2_Output_Params",
    "Ecuador/ECU_Energy/B1_Output_Params",
    "Ecuador/ECU_Energy/Executables",

    # Guatemala
    "Guatemala/GUA_ENERGY/A2_Output_Params",
    "Guatemala/GUA_ENERGY/B1_Output_Params",
    "Guatemala/GUA_ENERGY/Executables",

    # Honduras
    "Honduras/HON_ENERGY/A2_Output_Params",
    "Honduras/HON_ENERGY/B1_Output_Params",
    "Honduras/HON_ENERGY/Executables",

    # Jamaica
    "Jamaica/JAM_ENERGY/A2_Output_Params",
    "Jamaica/JAM_ENERGY/B1_Output_Params",
    "Jamaica/JAM_ENERGY/Executables",
]

# Scenario names that should stay. Matched case-insensitively.
# A trailing `_0` on a folder name is stripped before comparison.
ALLOWED_SCENARIOS = {"BAU", "NDCNEW", "LTSNEW", "Default"}


def normalize_scenario(folder_name: str) -> str:
    """Strip an optional `_0` suffix; return the base scenario name."""
    if folder_name.endswith("_0"):
        return folder_name[:-2]
    return folder_name


def is_allowed(folder_name: str) -> bool:
    """True if a folder name (with or without _0) matches an allowed scenario."""
    base = normalize_scenario(folder_name).upper()
    allowed_upper = {name.upper() for name in ALLOWED_SCENARIOS}
    return base in allowed_upper


def find_subdirs_to_move(root: Path) -> list[tuple[str, Path]]:
    """For each TARGET_DIR, find immediate subdirs whose names aren't allowed.

    Returns a list of (target_dir_label, full_subdir_path).
    """
    out: list[tuple[str, Path]] = []
    for target_rel in TARGET_DIRS:
        target = root / target_rel
        if not target.exists():
            print(f"  (skip) target does not exist: {target_rel}")
            continue
        if not target.is_dir():
            print(f"  (skip) target is not a directory: {target_rel}")
            continue

        for entry in sorted(target.iterdir()):
            if not entry.is_dir():
                continue
            if is_allowed(entry.name):
                continue
            out.append((target_rel, entry))
    return out


def folder_size_bytes(path: Path) -> int:
    """Sum of file sizes under path; ignore errors on individual files."""
    total = 0
    for sub in path.rglob("*"):
        try:
            if sub.is_file():
                total += sub.stat().st_size
        except OSError:
            continue
    return total


def choose_move_path(dest_root: Path, rel_path: Path) -> Path:
    """Pick a destination, appending an incrementing suffix on collision."""
    target = dest_root / rel_path
    if not target.exists():
        return target
    stem = target.name
    parent = target.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}__{counter}"
        if not candidate.exists():
            return candidate
        counter += 1


def print_plan(
    root: Path, subdirs: list[tuple[str, Path]]
) -> tuple[int, int]:
    """Show the move plan. Returns (folder_count, total_bytes)."""
    print()
    print("Plan")
    print("----")

    if not subdirs:
        print("  (nothing to move)")
        return 0, 0

    by_target: dict[str, list[Path]] = {}
    for target_rel, path in subdirs:
        by_target.setdefault(target_rel, []).append(path)

    total_folders = 0
    total_bytes = 0
    for target_rel in sorted(by_target):
        paths = by_target[target_rel]
        print(f"  in {target_rel}")
        for p in paths:
            size = folder_size_bytes(p)
            total_folders += 1
            total_bytes += size
            print(f"      {p.name:30}  {size/(1024*1024):8.2f} MB")

    print(f"  TOTAL  {total_folders} folders  {total_bytes/(1024*1024):.2f} MB")
    return total_folders, total_bytes


def confirm(prompt: str) -> bool:
    try:
        reply = input(prompt + " [y/N]: ").strip().lower()
    except EOFError:
        return False
    return reply in {"y", "yes"}


def execute_moves(
    subdirs: list[tuple[str, Path]], dest_root: Path, root: Path
) -> tuple[int, int]:
    """Move each subdir into dest_root preserving relative structure."""
    moved = 0
    total_bytes = 0
    for _, source in subdirs:
        try:
            rel = source.relative_to(root)
        except ValueError:
            print(f"  ! skip (outside root): {source}", file=sys.stderr)
            continue
        if not source.exists():
            continue
        size = folder_size_bytes(source)
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
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root. Default: current directory.",
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
    print(f"Allowed scenarios: {', '.join(sorted(ALLOWED_SCENARIOS))} (with optional _0 suffix)")
    print(f"Target directories ({len(TARGET_DIRS)}):")
    for t in TARGET_DIRS:
        print(f"  - {t}")

    subdirs = find_subdirs_to_move(root)
    total_folders, total_bytes = print_plan(root, subdirs)

    if args.dry_run:
        print()
        print("--dry-run: nothing moved.")
        return 0

    if total_folders == 0:
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

    moved, moved_bytes = execute_moves(subdirs, dest_root, root)

    print()
    print("Done.")
    print(f"  Moved:        {moved} folders  ({moved_bytes/(1024*1024):.2f} MB)")
    print(f"  Destination:  {dest_root.relative_to(root)}")
    print()
    print("The destination tree mirrors the original relative paths, so it's")
    print("the record of what moved. Restore is a manual `Move-Item` away.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
