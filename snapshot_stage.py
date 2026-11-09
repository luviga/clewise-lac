#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MODELS_LAC_4 Snapshot Helper (v2)
=================================
Archives both stage outputs AND country-folder state at key pipeline
checkpoints so you can roll back if a later step goes wrong.

The pipeline mutates state in two places:
  1. Stage output folders (_STAGE1_OUTPUT, _STAGE2_OUTPUT, etc.) — immutable
     once a stage finishes, easy to archive.
  2. Country folders (Country/Country_ENERGY/) — get OVERWRITTEN every time
     you deploy a Stage <N> output back as the active B1_Scenario_Config.xlsx,
     and *Output.csv + Executables/ get REGENERATED every OSeMOSYS solve.

v2 adds country-folder snapshotting at key checkpoints so re-running a stage
after a botched downstream step is actually possible.

Usage:
    py snapshot_stage.py --stage 1
    py snapshot_stage.py --stage controller
    py snapshot_stage.py --checkpoint post_solve_1
    py snapshot_stage.py --list
    py snapshot_stage.py --restore <name>
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime


STAGE_NAMES = {
    "1": ("_STAGE1_OUTPUT",  "Baseline Characterization"),
    "2": ("_STAGE2_OUTPUT",  "Initial Scenario Construction"),
    "3": ("_STAGE3_OUTPUT",  "Target-Share Calibration"),
    "4": ("_STAGE4_OUTPUT",  "Sensitivity Generation"),
    "5": ("_STAGE5_OUTPUT",  "BAU Coherence Adjustment"),
}

CONTROLLER_PATH = "_STAGE1_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx"

COUNTRY_FOLDERS = {
    "DominicanRepublic":  "DominicanRepublic/RD_ENERGY",
    "Ecuador":            "Ecuador/ECU_Energy",
    "Guatemala":          "Guatemala/GUA_ENERGY",
    "Honduras":           "Honduras/HON_ENERGY",
    "Jamaica":            "Jamaica/JAM_ENERGY",
    "CostaRica":          "CostaRica/CR_ENERGY/t1_confection",
}

CHECKPOINT_DEFINITIONS = {
    "post_stage2_deploy": {
        "description": "After Stage 2 outputs deployed as active B1_Scenario_Config",
        "countries":   ["DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"],
        "patterns":    ["B1_Scenario_Config.xlsx"],
    },
    "post_solve_1": {
        "description": "After first OSeMOSYS solve (Stage 2 constraints)",
        "countries":   ["DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica", "CostaRica"],
        "patterns":    ["*Output.csv", "*Input.csv", "Executables/*_0/*.txt"],
    },
    "post_stage3_deploy": {
        "description": "After Stage 3 outputs deployed as active B1_Scenario_Config",
        "countries":   ["DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"],
        "patterns":    ["B1_Scenario_Config.xlsx"],
    },
    "post_solve_2": {
        "description": "After second OSeMOSYS solve (Stage 3 calibrated constraints)",
        "countries":   ["DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"],
        "patterns":    ["*Output.csv", "*Input.csv", "Executables/*_0/*.txt"],
    },
    "post_stage4_deploy": {
        "description": "After Stage 4 outputs deployed (LTSOPT scenario added)",
        "countries":   ["DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"],
        "patterns":    ["B1_Scenario_Config.xlsx"],
    },
    "post_solve_3": {
        "description": "After third OSeMOSYS solve (Stage 4 LTSOPT)",
        "countries":   ["DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"],
        "patterns":    ["*Output.csv", "*Input.csv", "Executables/*_0/*.txt"],
    },
    "post_stage5_deploy": {
        "description": "After Stage 5 output deployed (Costa Rica only)",
        "countries":   ["CostaRica"],
        "patterns":    ["B1_Scenario_Config.xlsx"],
    },
    "post_solve_cr": {
        "description": "After Costa Rica final OSeMOSYS solve (Stage 5 constraints)",
        "countries":   ["CostaRica"],
        "patterns":    ["*Output.csv", "*Input.csv", "Executables/*_0/*.txt"],
    },
}


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def fmt_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def snapshot_stage(root: Path, stage: str) -> None:
    if stage == "controller":
        snapshot_controller(root)
        return
    if stage not in STAGE_NAMES:
        print(f"ERROR: unknown stage '{stage}'. Valid: {list(STAGE_NAMES.keys())} or 'controller'")
        sys.exit(1)
    folder_name, stage_name = STAGE_NAMES[stage]
    source = root / folder_name
    if not source.exists():
        print(f"ERROR: source folder does not exist: {source}")
        sys.exit(1)
    archive_name = f"{folder_name}__archive_{timestamp()}"
    dest = root / archive_name
    print(f"Stage {stage}: {stage_name}")
    print(f"  Archiving: {source.name}  ->  {dest.name}")
    shutil.copytree(source, dest)
    print(f"  Done.")


def snapshot_controller(root: Path) -> None:
    source = root / CONTROLLER_PATH
    if not source.exists():
        print(f"ERROR: controller file does not exist: {source}")
        sys.exit(1)
    dest_name = f"CONTROLLER_NEW_SCENARIOS.policy_backup_{timestamp()}.xlsx"
    dest = source.parent / dest_name
    print(f"Controller backup: {source.name}  ->  {dest.name}")
    shutil.copy2(source, dest)
    print(f"  Done.")


def snapshot_checkpoint(root: Path, checkpoint: str) -> None:
    if checkpoint not in CHECKPOINT_DEFINITIONS:
        print(f"ERROR: unknown checkpoint '{checkpoint}'")
        print(f"  Valid: {list(CHECKPOINT_DEFINITIONS.keys())}")
        sys.exit(1)
    spec = CHECKPOINT_DEFINITIONS[checkpoint]
    snapshot_dir = root / "_SNAPSHOTS" / f"{checkpoint}__{timestamp()}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    manifest = snapshot_dir / "MANIFEST.txt"
    with open(manifest, "w", encoding="utf-8") as f:
        f.write(f"Snapshot: {checkpoint}\n")
        f.write(f"Description: {spec['description']}\n")
        f.write(f"Created: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Countries: {spec['countries']}\n")
        f.write(f"Patterns: {spec['patterns']}\n")
        f.write(f"\nFiles captured:\n")
    print(f"Checkpoint: {checkpoint}")
    print(f"  {spec['description']}")
    print(f"  Snapshot dir: {snapshot_dir.relative_to(root)}")
    print()
    total_files = 0
    total_size = 0
    for country in spec["countries"]:
        if country not in COUNTRY_FOLDERS:
            print(f"  [WARN] Country '{country}' not in COUNTRY_FOLDERS, skipping")
            continue
        country_path = root / COUNTRY_FOLDERS[country]
        if not country_path.exists():
            print(f"  [WARN] Country folder does not exist: {country_path}")
            continue
        captured = 0
        for pattern in spec["patterns"]:
            for source_file in country_path.glob(pattern):
                if not source_file.is_file():
                    continue
                rel = source_file.relative_to(root)
                dest = snapshot_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest)
                size = source_file.stat().st_size
                total_files += 1
                total_size += size
                captured += 1
                with open(manifest, "a", encoding="utf-8") as f:
                    f.write(f"  {rel}  ({fmt_size(size)})\n")
        print(f"  {country:<20} captured {captured} files")
    print()
    print(f"  Total: {total_files} files, {fmt_size(total_size)}")
    print(f"  Manifest: {manifest.relative_to(root)}")


def list_snapshots(root: Path) -> None:
    print(f"Snapshots in {root}:\n")
    print("=== Stage output archives ===")
    for stage, (folder_name, stage_name) in STAGE_NAMES.items():
        archives = sorted(root.glob(f"{folder_name}__archive_*"))
        active = root / folder_name
        active_marker = " [ACTIVE]" if active.exists() else " [no active output]"
        print(f"Stage {stage}: {stage_name}{active_marker}")
        if not archives:
            print(f"  (no snapshots)")
        for archive in archives:
            size = sum(f.stat().st_size for f in archive.rglob("*") if f.is_file())
            print(f"  {archive.name}  ({fmt_size(size)})")
        print()
    controller_dir = root / "_STAGE1_OUTPUT"
    if controller_dir.exists():
        backups = sorted(controller_dir.glob("CONTROLLER_NEW_SCENARIOS.policy_backup_*.xlsx"))
        print("=== Controller policy backups ===")
        if not backups:
            print("  (none)")
        for backup in backups:
            print(f"  {backup.name}  ({fmt_size(backup.stat().st_size)})")
        print()
    snapshots_dir = root / "_SNAPSHOTS"
    print("=== Country-folder checkpoint snapshots ===")
    if not snapshots_dir.exists():
        print("  (none — _SNAPSHOTS/ folder does not exist)")
        return
    by_checkpoint = {}
    for snap in sorted(snapshots_dir.iterdir()):
        if not snap.is_dir():
            continue
        cp_name = snap.name.split("__")[0]
        by_checkpoint.setdefault(cp_name, []).append(snap)
    if not by_checkpoint:
        print("  (none)")
        return
    for cp_name in CHECKPOINT_DEFINITIONS:
        snaps = by_checkpoint.get(cp_name, [])
        if not snaps:
            continue
        desc = CHECKPOINT_DEFINITIONS[cp_name]["description"]
        print(f"{cp_name}: {desc}")
        for snap in snaps:
            size = sum(f.stat().st_size for f in snap.rglob("*") if f.is_file())
            file_count = sum(1 for f in snap.rglob("*") if f.is_file())
            print(f"  {snap.name}  ({file_count} files, {fmt_size(size)})")
        print()


def restore_snapshot(root: Path, name: str) -> None:
    if name.startswith("_STAGE") and "__archive_" in name:
        source = root / name
        if not source.exists():
            print(f"ERROR: snapshot does not exist: {source}")
            sys.exit(1)
        target_folder = name.split("__archive_")[0]
        target = root / target_folder
        print(f"About to restore stage output:")
        print(f"  FROM: {source.name}")
        print(f"  TO:   {target.name}")
        if target.exists():
            print(f"  WARNING: this DELETES the current {target.name}")
        response = input("Type 'yes' to confirm: ").strip().lower()
        if response != "yes":
            print("Aborted.")
            return
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"Restored. {target.name} is now a copy of the archive.")
        return
    cp_dir = root / "_SNAPSHOTS" / name
    if cp_dir.exists() and cp_dir.is_dir():
        print(f"About to restore country-folder checkpoint:")
        print(f"  FROM: _SNAPSHOTS/{name}")
        print(f"  This OVERWRITES files in country folders with the snapshot's copies.")
        print()
        files_to_restore = []
        for f in cp_dir.rglob("*"):
            if f.is_file() and f.name != "MANIFEST.txt":
                rel = f.relative_to(cp_dir)
                target = root / rel
                files_to_restore.append((f, target))
        print(f"  {len(files_to_restore)} files will be overwritten.")
        response = input("Type 'yes' to confirm: ").strip().lower()
        if response != "yes":
            print("Aborted.")
            return
        for source_file, target_file in files_to_restore:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
        print(f"Restored {len(files_to_restore)} files from {name}.")
        return
    print(f"ERROR: cannot find snapshot '{name}'")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="MODELS_LAC_4 snapshot helper v2")
    parser.add_argument("--root", default=".", help="Path to MODELS_LAC_4 root")
    parser.add_argument("--stage", help="Stage to archive: 1, 2, 3, 4, 5, or 'controller'")
    parser.add_argument("--checkpoint", help="Country-folder checkpoint name")
    parser.add_argument("--list", action="store_true", help="List existing snapshots")
    parser.add_argument("--restore", help="Restore a snapshot by name")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}")
        sys.exit(1)
    if args.list:
        list_snapshots(root)
    elif args.restore:
        restore_snapshot(root, args.restore)
    elif args.stage:
        snapshot_stage(root, args.stage)
    elif args.checkpoint:
        snapshot_checkpoint(root, args.checkpoint)
    else:
        parser.print_help()
        print()
        print("Available checkpoints:")
        for cp, spec in CHECKPOINT_DEFINITIONS.items():
            print(f"  {cp:<25} {spec['description']}")


if __name__ == "__main__":
    main()
