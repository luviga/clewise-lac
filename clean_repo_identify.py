"""
Classify likely useful vs. noisy files in this MODELS_LAC working copy.

This is a READ-ONLY classifier: it produces a CSV report only. To actually
move anything, run clean_repo_apply.py against the report.

    py clean_repo_identify.py
    py clean_repo_identify.py --hash      # add SHA-256 + duplicate detection

Changes vs. v1 (the ChatGPT version):
  1. ACTIVE_ROOT_FILES now points at stage3_target_shares_v14.py and includes
     cleanup_audit_models_lac_4.py.
  2. is_old_root_stage_script() compares against v14, not v13. v13 is now
     correctly classified as superseded.
  3. is_stale_script_variant() respects an ACTIVE_DESPITE_MARKERS allowlist.
     This is what protects DR's active runner
     (B1_Base_Scenarios_Adj_Parallel_ADJ_TESTEOS.py) from a false positive
     caused by the substring "_TEST" matching inside "_TESTEOS".
  4. is_stale_b1_variant() no longer ends with `or True`. It now genuinely
     filters by markers, which is what the function name claims.
  5. The --move flag has been removed. Moves are now handled by the separate
     apply_deprecation_moves.py script, which reads this report.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


REPORT_DEFAULT = "deprecation_candidates_report.csv"
DEPRECATE_DIR = "_deprecate"


# --- Active files at the root of the working copy ---------------------------

ACTIVE_ROOT_FILES = {
    # audit & doc tooling (current names)
    "clean_repo_identify.py",
    "clean_repo_apply.py",
    # tolerate prior names if either script is still present from earlier work
    "identify_deprecation_candidates_v2.py",
    "identify_deprecation_candidates.py",
    "apply_deprecation_moves.py",
    "cleanup_audit_models_lac_4.py",
    "STAGE_SCRIPTS_EXPLAINED.md",
    "HANDOVER_PROMPT_ENERGY_ADJUSTMENTS.md",

    # current stage scripts
    "stage3_target_shares_v14.py",               # was v13 — bumped
    "stage4_generate_opt.py",
    "stage5_bau_constrained_v7.py",
}

ACTIVE_STAGE_FILES = {
    "_STAGE1_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx",
    "_STAGE3_OUTPUT/STAGE3_SUMMARY.csv",
    "_STAGE4_OUTPUT/STAGE4_SUMMARY.csv",
    "_STAGE5_OUTPUT/STAGE5_SUMMARY.csv",
}

ACTIVE_MODEL_FILENAMES = {
    "B1_Scenario_Config.xlsx",
    "B1_Default_Param.xlsx",
    "B1_Model_Structure.xlsx",
    "A2_Structure_Lists.xlsx",
    "OSeMOSYS_Model.txt",
    "requirements.txt",
    "setup_utils.py",
    "status_of_each_future.txt",
    "_GDP_Ref.xlsx",
}

ACTIVE_SCRIPT_PREFIXES = (
    "A1_Model_Structure",
    "A2_Compiler",
    "B1_Base_Scenarios_Adj_Parallel",
    "B2_Results_Creator_f0",
)


# --- Allowlists -------------------------------------------------------------

# Filenames that LOOK stale by substring rules but are actually active.
# Add new ones here; do NOT loosen STALE_SCRIPT_MARKERS instead — the markers
# are correct, they just have collateral damage on names that legitimately
# contain those substrings.
ACTIVE_DESPITE_MARKERS = {
    # DR uses this as its production runner (per HANDOVER_PROMPT). The "_TEST"
    # marker matches inside "_TESTEOS" but this file is NOT a test variant.
    "B1_Base_Scenarios_Adj_Parallel_ADJ_TESTEOS.py",
}


# --- Stale-marker substring lists -------------------------------------------

STALE_SCRIPT_MARKERS = (
    "_TEST",
    "_TESTS",
    "_OG",
    "_OLD",
    "_FREEZE",
    "_Susana",
    "_ignacio",
    "_Escenario",
    "_Win",
    "_2024",
)

STALE_WORKBOOK_MARKERS = (
    " FIX ",
    "FIX_",
    "FIXED",
    "FIX_LATER",
    "FREEZE",
    "UPDATED",
    "UPDATE",
    "STAGE_2",
    "STAGE_3",
    "BROKEN",
    "FAILS",
    "NEEDS_IMPROVEMENT",
    "PRE_ALIGNMENT_BACKUP",
    "COSTARICA",
    "ENERGY_AFTER_TRANSPORT",
    "_OG",
    "_ECU",
    "_MAIN",
    "_REF",
    "_CALC",
    "_INFEASIBLE",
    "_EDIT",
)

GENERATED_DIR_NAMES = {
    "Executables",
    "A2_Output_Params",
    "B1_Output_Params",
}

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".txt",
    ".json",
    ".toml",
    ".ini",
}


@dataclass(frozen=True)
class Classification:
    action: str
    confidence: str
    category: str
    reason: str
    rule: str


def norm(path: Path) -> str:
    return path.as_posix()


def has_part(rel: Path, names: Iterable[str]) -> bool:
    wanted = {name.lower() for name in names}
    return any(part.lower() in wanted for part in rel.parts)


def is_energy_path(rel: Path) -> bool:
    return any("energy" in part.lower() for part in rel.parts)


def is_stage_output_workbook(rel_s: str, name: str) -> bool:
    return (
        name.startswith("B1_Scenario_Config__")
        and name.endswith(("__Stage3.xlsx", "__Stage4.xlsx", "__Stage5.xlsx"))
        and rel_s.startswith(("_STAGE3_OUTPUT/", "_STAGE4_OUTPUT/", "_STAGE5_OUTPUT/"))
    )


def is_versioned_controller(rel_s: str, name: str) -> bool:
    return (
        rel_s.startswith("_STAGE1_OUTPUT/")
        and name.startswith("CONTROLLER_NEW_SCENARIOS_v")
        and name.endswith(".xlsx")
    )


def is_old_root_stage_script(name: str) -> bool:
    """Older versions of the staged scripts. Current versions live in ACTIVE_ROOT_FILES."""
    if name == "stage3_recalibrate_limits_v3.py":
        return True
    # PATCH: was v13 — bumped to v14 to match current active stage 3 script.
    # This means v13 is now correctly classified as superseded.
    if name.startswith("stage3_target_shares_v") and name != "stage3_target_shares_v14.py":
        return True
    if name.startswith("stage5_bau_constrained_v") and name != "stage5_bau_constrained_v7.py":
        return True
    return False


def is_stale_script_variant(name: str) -> bool:
    if not name.endswith(".py"):
        return False

    # PATCH: explicit allowlist for files whose names contain a stale marker
    # by accident but are actually active. This is what protects DR's
    # B1_Base_Scenarios_Adj_Parallel_ADJ_TESTEOS.py.
    if name in ACTIVE_DESPITE_MARKERS:
        return False

    lower_name = name.lower()
    if name in ACTIVE_ROOT_FILES:
        return False
    script_family = (
        lower_name.startswith("a1_model_structure")
        or lower_name.startswith("a2_compiler")
        or lower_name.startswith("b1_base_scenarios")
        or lower_name.startswith("b1_energy_base_scenarios")
        or lower_name.startswith("b2_results_creator")
    )
    if not script_family:
        return False
    return any(marker.lower() in lower_name for marker in STALE_SCRIPT_MARKERS)


def is_clean_model_input(name: str) -> bool:
    if name in ACTIVE_MODEL_FILENAMES:
        return True
    if name.startswith("MOMF_") and name.endswith((".yaml", ".yml")):
        return True
    if name.startswith(ACTIVE_SCRIPT_PREFIXES) and name.endswith(".py"):
        if any(marker.lower() in name.lower() for marker in STALE_SCRIPT_MARKERS):
            # ...unless it's allowlisted
            if name in ACTIVE_DESPITE_MARKERS:
                return True
            return False
        return True
    return False


def is_stale_b1_variant(name: str) -> bool:
    """A B1_Scenario_Config workbook variant that matches one of the stale markers.

    PATCH: removed the `or True` that made the marker filter inert. The
    function now genuinely filters by markers, which is what the name claims.
    Variants that don't match any marker fall through to the lower-priority
    'review' classification rather than auto-move.
    """
    if not (name.startswith("B1_Scenario_Config") and name.endswith(".xlsx")):
        return False
    if name == "B1_Scenario_Config.xlsx":
        return False
    name_upper = name.upper()
    return any(marker in name_upper for marker in STALE_WORKBOOK_MARKERS)


def is_generated_result(rel: Path, name: str) -> bool:
    if has_part(rel, GENERATED_DIR_NAMES):
        return True
    lower = name.lower()
    if lower.endswith(("_input.csv", "_output.csv")):
        return True
    if lower in {"selectedresults.csv", "output_dataset_0.csv", "input_dataset_0.csv"}:
        return True
    if lower.startswith("debug_") and lower.endswith(".csv"):
        return True
    if lower.endswith((".pickle", ".pkl")):
        return True
    return False


def classify(rel: Path, file_path: Path) -> Classification:
    rel_s = norm(rel)
    name = file_path.name
    lower_name = name.lower()
    suffix = file_path.suffix.lower()

    if rel.parts and rel.parts[0] == DEPRECATE_DIR:
        return Classification("ignore", "high", "already_deprecated", "Already under _deprecate.", "skip_deprecate_dir")

    if "__pycache__" in rel.parts or suffix == ".pyc":
        return Classification("move_safe", "high", "python_cache", "Python cache file; reproducible and never a source input.", "pycache")

    if lower_name.startswith("~$") or lower_name.endswith((".tmp", ".temp", ".bak")):
        return Classification("move_safe", "high", "temporary_file", "Temporary or editor/Office lock file.", "temp_file")

    if rel_s in ACTIVE_STAGE_FILES:
        return Classification("keep", "high", "stage_flow_input", "Named directly by the current stage workflow or summary output.", "active_stage_file")

    if rel.parent == Path(".") and name in ACTIVE_ROOT_FILES:
        return Classification("keep", "high", "active_root_script_or_doc", "Current stage script or handover documentation.", "active_root_file")

    if rel.parent == Path(".") and is_old_root_stage_script(name):
        return Classification("move_candidate", "high", "superseded_stage_script", "Older root-level stage script; current versions are v14/v7 plus stage4_generate_opt.py.", "old_root_stage_script")

    if rel.parent == Path(".") and name in {"folder_analysis.csv", REPORT_DEFAULT}:
        return Classification("review_generated", "medium", "generated_folder_report", "Generated audit/report file; useful as a snapshot, reproducible if needed.", "folder_analysis")

    if is_versioned_controller(rel_s, name):
        return Classification("move_candidate", "high", "superseded_controller_copy", "Versioned controller copy; scripts read CONTROLLER_NEW_SCENARIOS.xlsx.", "versioned_controller")

    if rel_s.startswith("_STAGE3_SCENARIOS/"):
        return Classification("move_candidate", "medium", "manual_stage3_snapshot", "Manual/intermediate Stage 3 scenario workbook folder; current scripts use _STAGE3_OUTPUT.", "stage3_scenarios")

    if is_stage_output_workbook(rel_s, name):
        return Classification("keep", "medium", "stage_flow_workbook", "Stage workbook used as an intermediate or final artifact in the staged Energy flow.", "stage_output_workbook")

    if rel_s.startswith(("_STAGE3_OUTPUT/", "_STAGE4_OUTPUT/", "_STAGE5_OUTPUT/")):
        return Classification("review_generated", "medium", "stage_generated_output", "Generated stage output or debug file; useful for audit, reproducible from scripts.", "stage_generated")

    if is_clean_model_input(name):
        return Classification("keep", "high", "clean_model_input", "Clean model input/script name used by active model runs.", "clean_model_input")

    if is_stale_b1_variant(name):
        return Classification("move_candidate", "high", "stale_scenario_config_variant", "Suffixed B1 scenario workbook matching a known stale marker; active scripts read the clean B1_Scenario_Config.xlsx name.", "stale_b1_variant")

    if is_stale_script_variant(name):
        return Classification("move_candidate", "medium", "stale_script_variant", "Script variant with TEST/OG/FREEZE/etc. marker; active runs use the clean current script names.", "stale_script_variant")

    if is_energy_path(rel) and name.startswith("_") and suffix == ".xlsx":
        return Classification("move_candidate", "medium", "energy_underscore_workbook", "Underscore-prefixed Energy workbook not part of the clean B1 scenario flow.", "energy_underscore_xlsx")

    if is_generated_result(rel, name):
        return Classification("review_generated", "medium", "generated_model_artifact", "Generated output or solver artifact; useful for verification but reproducible.", "generated_result")

    if suffix in {".twbx", ".twbr"}:
        return Classification("review", "medium", "tableau_or_visualization", "Visualization artifact; usually not needed to rerun the model but may be useful for reporting.", "visualization")

    if lower_name in {"dummy.txt"}:
        return Classification("move_candidate", "medium", "scratch_file", "Scratch placeholder file.", "scratch_file")

    if "backup" in [part.lower() for part in rel.parts]:
        return Classification("move_candidate", "medium", "backup_folder_file", "File inside a backup folder; not part of the active clean path.", "backup_folder")

    if suffix in TEXT_EXTENSIONS:
        return Classification("review", "low", "text_or_code", "Text/code file outside the known active script set; inspect before moving.", "text_or_code")

    return Classification("review", "low", "unclassified", "No strong rule matched; keep for manual review.", "unclassified")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] == DEPRECATE_DIR:
            continue
        yield path


def build_report(root: Path, include_hash: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    hashes: dict[str, str] = {}

    files = sorted(iter_files(root), key=lambda p: norm(p.relative_to(root)).lower())
    for file_path in files:
        rel = file_path.relative_to(root)
        cls = classify(rel, file_path)
        stat = file_path.stat()
        digest = ""
        if include_hash:
            digest = sha256_file(file_path)
            hashes.setdefault(digest, norm(rel))

        duplicate_of = ""
        if include_hash and digest:
            first = hashes[digest]
            if first != norm(rel):
                duplicate_of = first

        rows.append(
            {
                "action": cls.action,
                "confidence": cls.confidence,
                "category": cls.category,
                "path": norm(rel),
                "size_bytes": str(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "reason": cls.reason,
                "rule": cls.rule,
                "sha256": digest,
                "duplicate_of": duplicate_of,
                "moved_to": "",
            }
        )

    return rows


def write_report(report_path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "action",
        "confidence",
        "category",
        "path",
        "size_bytes",
        "modified",
        "reason",
        "rule",
        "sha256",
        "duplicate_of",
        "moved_to",
    ]
    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows: list[dict[str, str]], report_path: Path) -> None:
    counts: dict[str, int] = {}
    sizes: dict[str, int] = {}
    for row in rows:
        action = row["action"]
        counts[action] = counts.get(action, 0) + 1
        sizes[action] = sizes.get(action, 0) + int(row["size_bytes"])

    print()
    print("Classification summary")
    print("----------------------")
    for action in sorted(counts):
        mb = sizes[action] / (1024 * 1024)
        print(f"{action:18} {counts[action]:6d} files  {mb:10.2f} MB")
    print()
    print(f"Report: {report_path}")
    print()
    print("Next step: review the report, then run clean_repo_apply.py to actually move files.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root to scan. Default: current directory.",
    )
    parser.add_argument(
        "--report",
        default=REPORT_DEFAULT,
        help=f"CSV report path. Default: {REPORT_DEFAULT}",
    )
    parser.add_argument(
        "--hash",
        action="store_true",
        help="Compute SHA-256 hashes and populate duplicate_of. Slower on large folders.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path

    rows = build_report(root, include_hash=args.hash)
    write_report(report_path, rows)
    print_summary(rows, report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
