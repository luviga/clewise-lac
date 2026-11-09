#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 0: Patch .txt Data Files and Prepare Solver Runs
========================================================
Run from: MODELS_LAC_4/

Copies existing Executables/{scenario}_0/ folders, patches the .txt GMPL
data files to relax electricity-sector lower limits, and generates a
batch script to run glpsol. Bypasses B1.py entirely — no config changes.

Usage:
  cd C:\\Users\\luisfernando\\Dropbox\\2_WORK\\MODELS_LAC_4
  python stage0_run.py [--dry-run] [--countries Ecuador Jamaica]
  stage0_run_all.bat
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

# =============================================================================
# CONFIGURATION
# =============================================================================

MODELS_LAC_ROOT = "./"

SOURCE_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
SUFFIX = "_S0"

ANCHOR_YEAR = 2024
PLATEAU_END = 2024  # 2025+ gets set to anchor value (was 2026)

PP_PREFIXES = ("PP", "PWR")  # Must match Stage 1's PWR_PREFIXES

# Bypass techs route generation to E3ELE directly, skipping T&D losses.
# In the relaxed Stage 0 run, the optimizer exploits this to avoid the
# ~18.5% IAR penalty, collapsing Empirical_Gen toward consumer demand
# instead of staying at the generation level. Cap these at their 2024
# activity (hold_at_anchor) so the optimizer can't game the bypass routes.
BYPASS_TECHS = {
    "PPWNDD", "PPPVD", "PPPVDS",           # distributed gen → E3ELE
    "PPHD", "PPIHD",                         # isolated/distributed hydro → E3ELE
    "PPCRU", "PPDDSL", "PPDFOI", "PPDGSL",  # autoproducers → E3ELE
    "PPDGLP", "PPDNGS", "PPRDSL", "PPRNGS", # refinery/distributed → E3ELE
    "PPILPG", "PPIBIM",                      # isolated → E3ELE
}

PARAMS_TO_PATCH = ["TotalTechnologyAnnualActivityLowerLimit"]
PATCH_UPPER_LIMITS = True  # Set PP-prefix upper limits to 9999 for 2025+
UPPER_LIMIT_SENTINEL = 9999.0

OUTPUT_DIR = "./_STAGE0_OUTPUT"

# Confirmed from Codex scan — model dir relative to country root,
# and path to OSeMOSYS_Model.txt relative to country root.
COUNTRY_CONFIG = {
    "CostaRica": {
        "model_dir": "CR_ENERGY/t1_confection",
        "osemosys":  "CR_ENERGY/t1_confection/OSeMOSYS_Model.txt",
    },
    "DominicanRepublic": {
        "model_dir": "RD_ENERGY",
        "osemosys":  "RD_ENERGY/OSeMOSYS_Model.txt",
    },
    "Ecuador": {
        "model_dir": "ECU_Energy",
        "osemosys":  "ECU_Energy/OSeMOSYS_Model.txt",
    },
    "Guatemala": {
        "model_dir": "GUA_ENERGY",
        "osemosys":  "GUA_ENERGY/OSeMOSYS_Model.txt",
    },
    "Honduras": {
        "model_dir": "HON_ENERGY",
        "osemosys":  "HON_ENERGY/OSeMOSYS_Model.txt",
    },
    "Jamaica": {
        "model_dir": "JAM_ENERGY",
        "osemosys":  "JAM_ENERGY/OSeMOSYS_Model.txt",
    },
}


# =============================================================================
# HELPERS
# =============================================================================

def is_pp_tech(tech_name: str) -> bool:
    return str(tech_name).strip().upper().startswith(PP_PREFIXES)


def read_param_block_data(txt_path: Path, param_name: str, anchor_year: int):
    """
    Parse a param block and return ({tech: anchor_year_value}, year_list)
    for all PP-prefix techs. Non-destructive read — does NOT modify the file.
    """
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    param_pattern = rf"param\s+{re.escape(param_name)}\s+default\s+[\d.\-]+\s*:"
    match = re.search(param_pattern, content)
    if not match:
        return {}, []

    block_start = match.start()
    semi_pos = content.find("\n;\n", block_start)
    if semi_pos == -1:
        semi_pos = content.find("\n;", block_start)
    if semi_pos == -1:
        return {}, []

    block = content[block_start:semi_pos]
    lines = block.split("\n")
    year_header = None
    anchor_col = None
    result = {}
    in_data = False

    for line in lines:
        stripped = line.strip()
        if ":=" in stripped and not stripped.startswith("param"):
            parts = stripped.replace(":=", "").strip().split()
            years = [int(p) for p in parts if p.isdigit()]
            if years and years[0] >= 2000:
                year_header = years
                anchor_col = {y: i for i, y in enumerate(years)}.get(anchor_year)
                in_data = True
            continue
        if stripped.startswith("[") and stripped.endswith(":"):
            in_data = False
            continue
        if in_data and year_header and stripped and not stripped.startswith(";"):
            parts = stripped.split()
            if len(parts) >= 2:
                tech = parts[0]
                values = parts[1:]
                if is_pp_tech(tech) and anchor_col is not None and len(values) == len(year_header):
                    try:
                        result[tech] = float(values[anchor_col])
                    except ValueError:
                        result[tech] = 0.0

    return result, (year_header or [])


def inject_upper_limit_rows(txt_path: Path, param_name: str,
                             techs_to_add: set, anchor_values: dict,
                             anchor_year: int, plateau_end: int,
                             log: list = None, change_rows: list = None) -> int:
    """
    Inject new rows into the upper-limit block for bypass techs that have
    no existing row (and therefore aren't reached by hold_at_anchor re-patch).

    Values for years <= plateau_end: 9999 (don't constrain historical).
    Values for years >  plateau_end: anchor value from lower-limit block,
    or 0.01 PJ if the tech wasn't in the LL block either.
    """
    if not techs_to_add:
        return 0
    if log is None:
        log = []
    if change_rows is None:
        change_rows = []

    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Find the upper-limit param block
    param_pattern = rf"param\s+{re.escape(param_name)}\s+default\s+[\d.\-]+\s*:"
    match = re.search(param_pattern, content)
    if not match:
        log.append(f"    [WARN] Cannot inject: '{param_name}' block not found")
        return 0

    block_start = match.start()
    semi_pos = content.find("\n;\n", block_start)
    if semi_pos == -1:
        semi_pos = content.find("\n;", block_start)
    if semi_pos == -1:
        log.append(f"    [WARN] Cannot inject: no semicolon end for '{param_name}'")
        return 0

    # Extract year header from the block
    block = content[block_start:semi_pos]
    year_header = None
    for line in block.split("\n"):
        stripped = line.strip()
        if ":=" in stripped and not stripped.startswith("param"):
            parts = stripped.replace(":=", "").strip().split()
            years = [int(p) for p in parts if p.isdigit()]
            if years and years[0] >= 2000:
                year_header = years
                break

    if not year_header:
        log.append(f"    [WARN] Cannot inject: no year header in '{param_name}'")
        return 0

    # Build injection lines
    injection_lines = []
    changes = 0
    for tech in sorted(techs_to_add):
        anchor_val = anchor_values.get(tech, 0.01)
        if anchor_val <= 0:
            anchor_val = 0.01  # Must be positive for UL to constrain

        values = []
        for year in year_header:
            if year <= plateau_end:
                values.append("9999")
            else:
                if anchor_val == int(anchor_val):
                    values.append(str(int(anchor_val)))
                else:
                    values.append(f"{anchor_val:.4f}".rstrip("0").rstrip("."))
                changes += 1
                change_rows.append({
                    "Parameter": param_name,
                    "Technology": tech,
                    "Year": year,
                    "Original": 0.0,
                    "Relaxed": round(anchor_val, 6),
                    "Delta": round(anchor_val, 6),
                })

        injection_lines.append(tech + " " + " ".join(values))
        log.append(f"    [INJECT] {tech} UL capped at {anchor_val:.4f} for {plateau_end + 1}+")

    # Insert before the semicolon line
    inject_text = "\n".join(injection_lines) + "\n"
    new_content = content[:semi_pos] + "\n" + inject_text + content[semi_pos:]

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    log.append(f"    Injected {len(techs_to_add)} bypass-tech UL rows: {changes} values")
    return changes


def patch_txt_data_file(txt_path: Path, param_name: str,
                         anchor_year: int, plateau_end: int,
                         mode: str = "hold_at_anchor",
                         log: list = None,
                         change_rows: list = None,
                         tech_filter: set = None,
                         anchor_overrides: dict = None) -> int:
    """
    Patch a GMPL .txt data file in place. Finds the block for `param_name`,
    then for each PP-prefix tech row, replaces projection-year values with
    the anchor-year value.

    If tech_filter is provided, only techs in that set are patched (they must
    still pass the PP-prefix check). Used to re-patch bypass techs with
    hold_at_anchor after a sentinel pass.

    If anchor_overrides is provided (dict of {tech: value}), techs in the dict
    use that value instead of the block's own anchor-year value. Used to force
    bypass techs whose UL anchor is unreasonably large to a realistic cap.

    Format (3-key param: REGION, TECHNOLOGY, YEAR):
        param TotalTechnologyAnnualActivityLowerLimit default 0 :
        [CR,*,*]:
        2018 2019 ... 2030 :=
        PPFOI01 5.0 5.0 ... 3.0
        ;

    Returns number of values changed.
    """
    if log is None:
        log = []
    if change_rows is None:
        change_rows = []

    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    param_pattern = rf"param\s+{re.escape(param_name)}\s+default\s+[\d.\-]+\s*:"
    match = re.search(param_pattern, content)
    if not match:
        log.append(f"    [WARN] '{param_name}' not found in {txt_path.name}")
        return 0

    block_start = match.start()
    semicolon_pos = content.find("\n;\n", block_start)
    if semicolon_pos == -1:
        semicolon_pos = content.find("\n;", block_start)
    if semicolon_pos == -1:
        log.append(f"    [WARN] Could not find end of '{param_name}' block")
        return 0

    block_end = semicolon_pos + 2
    block = content[block_start:block_end]

    lines = block.split("\n")
    new_lines = []
    year_header = None
    year_indices = {}
    anchor_col = None
    changes = 0
    in_data_section = False

    for line in lines:
        stripped = line.strip()

        if ":=" in stripped and not stripped.startswith("param"):
            parts = stripped.replace(":=", "").strip().split()
            try:
                years = [int(p) for p in parts if p.isdigit()]
                if years and years[0] >= 2000:
                    year_header = years
                    year_indices = {y: i for i, y in enumerate(years)}
                    anchor_col = year_indices.get(anchor_year)
                    in_data_section = True
            except ValueError:
                pass
            new_lines.append(line)
            continue

        if stripped.startswith("[") and stripped.endswith(":"):
            in_data_section = False
            new_lines.append(line)
            continue

        if in_data_section and year_header and stripped and not stripped.startswith(";"):
            parts = stripped.split()
            if len(parts) >= 2:
                tech_name = parts[0]
                values = parts[1:]

                if is_pp_tech(tech_name) and anchor_col is not None and len(values) == len(year_header):
                    # If tech_filter is set, only patch techs in that set
                    if tech_filter is not None and tech_name not in tech_filter:
                        new_lines.append(line)
                        continue
                    try:
                        anchor_val = float(values[anchor_col])
                    except (ValueError, IndexError):
                        anchor_val = 0.0
                    # Override if caller provided a forced cap for this tech
                    if anchor_overrides and tech_name in anchor_overrides:
                        anchor_val = anchor_overrides[tech_name]

                    new_values = list(values)
                    for i, year in enumerate(year_header):
                        if year > plateau_end:
                            try:
                                old_val = float(values[i])
                            except ValueError:
                                continue

                            if mode == "hold_at_anchor":
                                new_val = anchor_val
                            elif mode == "zero":
                                new_val = 0.0
                            elif mode == "upper_sentinel":
                                new_val = UPPER_LIMIT_SENTINEL
                            else:
                                new_val = anchor_val

                            if abs(new_val - old_val) > 1e-10:
                                if new_val == int(new_val):
                                    new_values[i] = str(int(new_val))
                                else:
                                    new_values[i] = f"{new_val:.4f}".rstrip("0").rstrip(".")
                                changes += 1

                                change_rows.append({
                                    "Parameter": param_name,
                                    "Technology": tech_name,
                                    "Year": year,
                                    "Original": round(old_val, 6),
                                    "Relaxed": round(new_val, 6),
                                    "Delta": round(new_val - old_val, 6),
                                })

                    new_line = tech_name + " " + " ".join(new_values)
                    new_lines.append(new_line)
                    continue

        new_lines.append(line)

    new_block = "\n".join(new_lines)
    new_content = content[:block_start] + new_block + content[block_end:]

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    log.append(f"    Patched {param_name}: {changes} values")
    return changes


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Stage 0: Patch .txt data files and prepare solver runs")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--countries", nargs="*", default=[])
    parser.add_argument("--patch-upper", action="store_true")
    parser.add_argument("--mode", choices=["hold_at_anchor", "zero"],
                        default="zero")
    args = parser.parse_args()

    global PATCH_UPPER_LIMITS
    if args.patch_upper:
        PATCH_UPPER_LIMITS = True

    root = Path(MODELS_LAC_ROOT).resolve()
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("STAGE 0: Patch .txt Data Files & Prepare Solver Runs")
    print("=" * 70)
    print(f"Root:        {root}")
    print(f"Mode:        {args.mode}")
    print(f"Anchor:      {ANCHOR_YEAR} | Plateau end: {PLATEAU_END}")
    print(f"Dry run:     {args.dry_run}")
    print()

    # Build country list from confirmed config
    countries_to_run = []
    for country_name, cfg in COUNTRY_CONFIG.items():
        if args.countries and country_name not in args.countries:
            continue
        country_dir = root / country_name
        if not country_dir.exists():
            print(f"  [SKIP] {country_name}: directory not found")
            continue
        exec_dir = country_dir / cfg["model_dir"] / "Executables"
        model_file = country_dir / cfg["osemosys"]
        if not exec_dir.exists():
            print(f"  [SKIP] {country_name}: Executables not found at {exec_dir}")
            continue
        if not model_file.exists():
            print(f"  [WARN] {country_name}: OSeMOSYS_Model.txt not found at {model_file}")
            model_file = None
        countries_to_run.append((country_name, country_dir, exec_dir, model_file))

    if not countries_to_run:
        print("[ERROR] No countries to process.")
        sys.exit(1)

    print(f"Processing {len(countries_to_run)} countries:")
    for name, _, ed, mf in countries_to_run:
        print(f"  {name}: {ed}")
    print()

    # Batch script header
    bat = ["@echo off",
           f"REM Stage 0 solver runs - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
           f"cd /d \"{root}\"", ""]
    sh = ["#!/bin/bash",
          f"# Stage 0 solver runs - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
          f"cd \"{root}\"", ""]

    global_log = []
    all_changes = []

    for country_name, country_dir, exec_dir, model_file in countries_to_run:
        print(f"\n{'='*60}")
        print(f"{country_name}")

        bat.append(f"REM === {country_name} ===")
        sh.append(f"# === {country_name} ===")

        for scenario in SOURCE_SCENARIOS:
            src_name = f"{scenario}_0"
            dst_name = f"{scenario}{SUFFIX}_0"
            src_dir = exec_dir / src_name
            dst_dir = exec_dir / dst_name

            if not src_dir.exists():
                print(f"  [SKIP] {src_name}: not found")
                global_log.append(f"{country_name}/{scenario}: SKIP")
                continue

            # Find the .txt data file (BAU_0/BAU_0.txt)
            expected_txt = src_dir / f"{src_name}.txt"
            if not expected_txt.exists():
                txt_files = [f for f in src_dir.glob("*.txt")
                             if "output" not in f.name.lower()]
                expected_txt = txt_files[0] if txt_files else None
            if expected_txt is None:
                print(f"  [SKIP] {src_name}: no .txt data file")
                continue

            print(f"\n  {src_name} -> {dst_name}")
            log = []
            change_rows = []

            # Copy
            if dst_dir.exists() and not args.dry_run:
                shutil.rmtree(dst_dir)
            if not args.dry_run:
                shutil.copytree(src_dir, dst_dir)
                log.append(f"    Copied")

            # Rename all files: BAU_0.txt -> BAU_S0_0.txt, etc.
            new_txt_name = f"{dst_name}.txt"
            new_txt_path = dst_dir / new_txt_name

            if not args.dry_run:
                for f in list(dst_dir.iterdir()):
                    if src_name in f.name:
                        new_name = f.name.replace(src_name, dst_name)
                        f.rename(dst_dir / new_name)

            # Patch
            total_changes = 0
            if not args.dry_run and new_txt_path.exists():
                # Pre-read: capture bypass-tech anchor values from LL block
                # BEFORE zeroing, so we know what cap to use for injection.
                ll_anchors, _ = read_param_block_data(
                    new_txt_path,
                    "TotalTechnologyAnnualActivityLowerLimit",
                    ANCHOR_YEAR)
                ul_anchors, _ = read_param_block_data(
                    new_txt_path,
                    "TotalTechnologyAnnualActivityUpperLimit",
                    ANCHOR_YEAR)
                # Also read ResidualCapacity to detect bypass techs that
                # exist in the model but have no LL or UL rows.
                rc_anchors, _ = read_param_block_data(
                    new_txt_path, "ResidualCapacity", ANCHOR_YEAR)

                bypass_missing_from_ul = set()
                C2A = 31.536
                # Build ideal caps for ALL bypass techs:
                # priority: LL anchor → RC × C2A → 0.01 PJ
                bypass_ideal_caps = {}
                for tech in BYPASS_TECHS:
                    if tech in ll_anchors and ll_anchors[tech] > 0:
                        bypass_ideal_caps[tech] = ll_anchors[tech]
                    elif tech in rc_anchors and rc_anchors[tech] > 0:
                        bypass_ideal_caps[tech] = rc_anchors[tech] * C2A
                    else:
                        bypass_ideal_caps[tech] = 0.01

                # Split bypass techs into missing (need injection) vs
                # oversized (have a UL row but anchor is way above ideal).
                bypass_overrides = {}
                for tech in BYPASS_TECHS:
                    if tech not in ul_anchors:
                        if tech in ll_anchors or tech in rc_anchors:
                            bypass_missing_from_ul.add(tech)
                    else:
                        ideal = bypass_ideal_caps.get(tech, 0.01)
                        if ul_anchors[tech] > ideal * 2:
                            bypass_overrides[tech] = ideal
                            log.append(
                                f"    [OVERRIDE] {tech} UL anchor "
                                f"{ul_anchors[tech]:.4f} -> {ideal:.4f}")

                for param in PARAMS_TO_PATCH:
                    n = patch_txt_data_file(
                        new_txt_path, param,
                        ANCHOR_YEAR, PLATEAU_END,
                        mode=args.mode, log=log, change_rows=change_rows)
                    total_changes += n

                if PATCH_UPPER_LIMITS:
                    n = patch_txt_data_file(
                        new_txt_path,
                        "TotalTechnologyAnnualActivityUpperLimit",
                        ANCHOR_YEAR, PLATEAU_END,
                        mode="upper_sentinel", log=log, change_rows=change_rows)
                    total_changes += n

                    # Re-patch bypass techs: hold upper at anchor (not 9999)
                    # so the optimizer can't shift generation off-grid to
                    # avoid T&D losses in the relaxed run.
                    # Pass anchor_overrides so techs with bloated UL anchors
                    # (e.g. PPPVD at 9999) get capped at the LL/RC ideal.
                    n = patch_txt_data_file(
                        new_txt_path,
                        "TotalTechnologyAnnualActivityUpperLimit",
                        ANCHOR_YEAR, PLATEAU_END,
                        mode="hold_at_anchor", log=log, change_rows=change_rows,
                        tech_filter=BYPASS_TECHS,
                        anchor_overrides=bypass_overrides)
                    total_changes += n

                    # Inject UL rows for bypass techs that had no row in the
                    # block (hold_at_anchor can't patch what doesn't exist).
                    if bypass_missing_from_ul:
                        n = inject_upper_limit_rows(
                            new_txt_path,
                            "TotalTechnologyAnnualActivityUpperLimit",
                            bypass_missing_from_ul, bypass_ideal_caps,
                            ANCHOR_YEAR, PLATEAU_END,
                            log=log, change_rows=change_rows)
                        total_changes += n

                for row in change_rows:
                    row["Country"] = country_name
                    row["Scenario"] = scenario
                all_changes.extend(change_rows)

            for l in log:
                print(l)
            print(f"    {total_changes} values patched")
            global_log.append(f"{country_name}/{scenario}: {total_changes} patched")

            # Solver command
            if model_file:
                model_rel = os.path.relpath(model_file, root)
                txt_rel = os.path.relpath(new_txt_path, root)
                output_rel = txt_rel.replace(".txt", "_output.txt")

                bat.append(f'echo Running {country_name} {scenario}{SUFFIX}...')
                bat.append(f'glpsol -m "{model_rel}" -d "{txt_rel}" -o "{output_rel}"')
                bat.append("")

                sh.append(f'echo "Running {country_name} {scenario}{SUFFIX}..."')
                sh.append(f'glpsol -m "{model_rel}" -d "{txt_rel}" -o "{output_rel}"')
                sh.append("")

    # Write batch scripts
    bat.extend(["echo.", "echo All Stage 0 runs complete!", "pause"])
    sh.extend(['echo ""', 'echo "All Stage 0 runs complete!"'])

    if not args.dry_run:
        bat_path = root / "stage0_run_all.bat"
        with open(bat_path, "w") as f:
            f.write("\n".join(bat))
        print(f"\n[Wrote] {bat_path}")

        sh_path = root / "stage0_run_all.sh"
        with open(sh_path, "w") as f:
            f.write("\n".join(sh))
        print(f"[Wrote] {sh_path}")

    # Change audit
    if all_changes:
        df = pd.DataFrame(all_changes)
        df.to_csv(out_dir / "STAGE0_CHANGES_DETAIL.csv", index=False)
        print(f"[Wrote] STAGE0_CHANGES_DETAIL.csv ({len(df)} rows)")

        summary = []
        for (c, s), g in df.groupby(["Country", "Scenario"]):
            summary.append({
                "Country": c, "Scenario": s,
                "PP_Techs": g["Technology"].nunique(),
                "Years": g["Year"].nunique(),
                "Values_Changed": len(g),
            })
        pd.DataFrame(summary).to_csv(out_dir / "STAGE0_CHANGES_SUMMARY.csv", index=False)

    with open(out_dir / "STAGE0_LOG.txt", "w") as f:
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Mode: {args.mode}\n\n")
        f.write("\n".join(global_log))

    print(f"\n{'='*70}")
    print("DONE. Next:")
    print("  stage0_run_all.bat")
    print("  python stage0_collect_outputs.py")


if __name__ == "__main__":
    main()
