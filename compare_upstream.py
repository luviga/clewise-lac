#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compare Upstream: MODELS_LAC vs MODELS_LAC_4
============================================
Compares B1_Output_Params CSVs between the upstream MODELS_LAC directory
(where Stages 1-2 originally live) and your working MODELS_LAC_4 directory.

Purpose: before running Stage 1 in MODELS_LAC_4, know whether the upstream
has been regenerated with newer/different data that you should pull forward.

Run from MODELS_LAC_4 in Spyder:
  1. Set MODELS_LAC_PATH below to your actual MODELS_LAC location
  2. Hit Run (F5 in Spyder)
  3. Read the console output and the generated CSV report

This script is READ-ONLY. Compares only — does not modify or copy files.
"""

import csv
from pathlib import Path
from datetime import datetime


# =============================================================================
# CONFIGURATION — EDIT THESE TWO PATHS
# =============================================================================

# Path to the original upstream directory (where Stages 1-2 live).
# This is the "source of truth" you might want to pull from.
MODELS_LAC_PATH = r"C:\Users\luisfernando\Dropbox\2_WORK\MODELS_LAC"

# Path to your working directory. If this script lives inside MODELS_LAC_4,
# leave as "." and Spyder will resolve to wherever the script sits.
MODELS_LAC_4_PATH = r"."

# =============================================================================
# What to compare
# =============================================================================

COUNTRY_FOLDERS = {
    "DominicanRepublic":  "DominicanRepublic/RD_ENERGY",
    "Ecuador":            "Ecuador/ECU_Energy",
    "Guatemala":          "Guatemala/GUA_ENERGY",
    "Honduras":           "Honduras/HON_ENERGY",
    "Jamaica":            "Jamaica/JAM_ENERGY",
    "CostaRica":          "CostaRica/CR_ENERGY/t1_confection",
}

SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]

# Files inside B1_Output_Params/<scenario>/ that matter most for Stage 1
CRITICAL_FILES = [
    "TotalTechnologyAnnualActivityLowerLimit.csv",
    "TotalTechnologyAnnualActivityUpperLimit.csv",
    "TotalAnnualMaxCapacity.csv",
    "CapacityFactor.csv",
    "AvailabilityFactor.csv",
    "ResidualCapacity.csv",
    "SpecifiedAnnualDemand.csv",
    "InputActivityRatio.csv",
    "OutputActivityRatio.csv",
]


# =============================================================================
# Helpers
# =============================================================================

def fmt_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def file_fingerprint(path: Path):
    """Return (size, mtime, line_count_if_csv) for quick comparison."""
    if not path.exists():
        return None
    stat = path.stat()
    line_count = None
    if path.suffix.lower() == ".csv":
        try:
            with open(path, "rb") as f:
                line_count = sum(1 for _ in f)
        except Exception:
            line_count = None
    return {
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "lines": line_count,
    }


def compare_one_file(upstream_path: Path, working_path: Path):
    """Compare a single file's fingerprint between upstream and working."""
    up_fp = file_fingerprint(upstream_path)
    wo_fp = file_fingerprint(working_path)
    if up_fp is None and wo_fp is None:
        status = "BOTH_MISSING"
    elif up_fp is None:
        status = "UPSTREAM_MISSING"   # working has it, upstream doesn't
    elif wo_fp is None:
        status = "WORKING_MISSING"    # upstream has it, working doesn't
    elif up_fp["size"] == wo_fp["size"] and up_fp["lines"] == wo_fp["lines"]:
        status = "MATCH"              # same size and line count
    else:
        # Different size or line count = real content difference
        status = "DIFFER"
    return status, up_fp, wo_fp


# =============================================================================
# Main
# =============================================================================

def main():
    # Resolve paths
    upstream_root = Path(MODELS_LAC_PATH).resolve()
    working_root = Path(MODELS_LAC_4_PATH).resolve()

    print("=" * 78)
    print("UPSTREAM COMPARISON: MODELS_LAC vs MODELS_LAC_4")
    print("=" * 78)
    print(f"Upstream:  {upstream_root}")
    print(f"Working:   {working_root}")
    print(f"Run:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Validate paths
    if not upstream_root.exists():
        print(f"ERROR: upstream path does not exist: {upstream_root}")
        print(f"  Edit MODELS_LAC_PATH at the top of this script.")
        return
    if not working_root.exists():
        print(f"ERROR: working path does not exist: {working_root}")
        return

    # Collect all comparisons
    all_results = []
    summary_by_status = {"MATCH": 0, "DIFFER": 0, "WORKING_MISSING": 0,
                         "UPSTREAM_MISSING": 0, "BOTH_MISSING": 0}

    for country, rel_country_path in COUNTRY_FOLDERS.items():
        print(f"--- {country} ---")
        for scenario in SCENARIOS:
            print(f"  Scenario: {scenario}")
            for filename in CRITICAL_FILES:
                upstream_file = upstream_root / rel_country_path / "B1_Output_Params" / scenario / filename
                working_file = working_root / rel_country_path / "B1_Output_Params" / scenario / filename

                status, up_fp, wo_fp = compare_one_file(upstream_file, working_file)
                summary_by_status[status] += 1

                # Only print interesting cases to keep output readable
                if status == "MATCH":
                    continue
                if status == "BOTH_MISSING":
                    continue  # not interesting — file doesn't exist anywhere

                # Format details
                up_str = f"{fmt_size(up_fp['size'])} {up_fp['mtime']}" if up_fp else "—"
                wo_str = f"{fmt_size(wo_fp['size'])} {wo_fp['mtime']}" if wo_fp else "—"
                marker = {"DIFFER": "DIFFER", "WORKING_MISSING": "MISSING in MODELS_LAC_4",
                          "UPSTREAM_MISSING": "MISSING in MODELS_LAC"}[status]
                print(f"    [{marker}] {filename}")
                print(f"             upstream: {up_str}")
                print(f"             working:  {wo_str}")

                all_results.append({
                    "country": country,
                    "scenario": scenario,
                    "filename": filename,
                    "status": status,
                    "upstream_size": up_fp["size"] if up_fp else "",
                    "upstream_mtime": up_fp["mtime"] if up_fp else "",
                    "upstream_lines": up_fp["lines"] if up_fp else "",
                    "working_size": wo_fp["size"] if wo_fp else "",
                    "working_mtime": wo_fp["mtime"] if wo_fp else "",
                    "working_lines": wo_fp["lines"] if wo_fp else "",
                })

        print()

    # Summary
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    total = sum(summary_by_status.values())
    print(f"Total file comparisons: {total}")
    for status, count in summary_by_status.items():
        print(f"  {status:<20} {count}")
    print()

    if summary_by_status["DIFFER"] == 0 and summary_by_status["WORKING_MISSING"] == 0:
        print(">> MODELS_LAC_4 is in sync with MODELS_LAC for the critical files.")
        print(">> Safe to run Stage 1 against your MODELS_LAC_4 data.")
    elif summary_by_status["DIFFER"] > 0:
        print(f">> {summary_by_status['DIFFER']} files differ between the two directories.")
        print(">> Review the report and decide which version is authoritative")
        print("   BEFORE running Stage 1, or you'll calibrate against stale data.")
    if summary_by_status["WORKING_MISSING"] > 0:
        print(f">> {summary_by_status['WORKING_MISSING']} files exist in MODELS_LAC but are missing from MODELS_LAC_4.")
        print(">> These might be inputs you need to copy over.")
    if summary_by_status["UPSTREAM_MISSING"] > 0:
        print(f">> {summary_by_status['UPSTREAM_MISSING']} files exist in MODELS_LAC_4 but not in MODELS_LAC.")
        print(f"   (Probably fine — these are files you've created in your working dir.)")

    # Write CSV report
    report_path = working_root / "upstream_comparison_report.csv"
    if all_results:
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nReport (only interesting cases): {report_path}")
    else:
        print(f"\n(Everything matched — no report written.)")


# Spyder runs this when you hit F5
if __name__ == "__main__":
    main()
