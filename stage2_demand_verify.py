#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stage2_demand_verify.py — Check SpecifiedAnnualDemand consistency across scenarios.
====================================================================================

Reads .txt GMPL data files from Executables/ folders for each country/scenario.
Reports any differences in SpecifiedAnnualDemand across BAU/NDCNEW/LTSNEW.

Demands should be IDENTICAL across scenarios for all years — they represent
exogenous electricity demand, not model output.

Usage (from MODELS_LAC_4):
  py stage2_demand_verify.py
  py stage2_demand_verify.py --root .
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================

COUNTRY_CONFIG = {
    "CostaRica": "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador": "ECU_Energy",
    "Guatemala": "GUA_ENERGY",
    "Honduras": "HON_ENERGY",
    "Jamaica": "JAM_ENERGY",
}

SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
SUFFIXES_TO_TRY = ["_0", "_ADJ_TESTEOS", "_S0_0"]  # try original, then DR variant, then S0


def find_txt_file(exec_dir, scenario, suffix):
    """Find the .txt data file in an Executables subfolder."""
    folder_name = f"{scenario}{suffix}"
    folder = exec_dir / folder_name
    if not folder.exists():
        return None

    # Try exact name first
    expected = folder / f"{folder_name}.txt"
    if expected.exists():
        return expected

    # Glob for any .txt that's not output
    txts = [f for f in folder.glob("*.txt") if "output" not in f.name.lower()]
    return txts[0] if txts else None


def parse_specified_annual_demand(txt_path):
    """Parse SpecifiedAnnualDemand block from GMPL .txt file.

    Returns: dict[tech] -> dict[year] -> value
    """
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    pattern = r"param\s+SpecifiedAnnualDemand\s+default\s+[\d.\-]+\s*:"
    match = re.search(pattern, content)
    if not match:
        return {}

    block_start = match.start()
    semi_pos = content.find(";", block_start)
    if semi_pos == -1:
        return {}

    block = content[block_start:semi_pos]
    lines = block.split("\n")

    # Find year header line
    years = []
    data = {}
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        # Year header line: contains multiple integers
        if len(parts) > 5 and all(p.replace(":", "").isdigit() for p in parts[:5]):
            years = [int(p.replace(":", "")) for p in parts if p.replace(":", "").isdigit()]
            continue

        # Data line: TECH val val val ... or TECH val val val ... :=
        if years and len(parts) >= 2:
            tech = parts[0]
            if tech in (":=", ";", "["):
                continue
            # Try to parse as tech + values
            try:
                vals = []
                for v in parts[1:]:
                    v_clean = v.replace(":=", "").strip()
                    if v_clean:
                        vals.append(float(v_clean))
                if len(vals) == len(years):
                    data[tech] = dict(zip(years, vals))
            except ValueError:
                continue

    return data


def main():
    p = argparse.ArgumentParser(description="Stage 2 Demand Verifier")
    p.add_argument("--root", type=Path, default=Path("."))
    args = p.parse_args()

    root = args.root.resolve()

    print("=" * 70)
    print("STAGE 2 DEMAND VERIFIER")
    print(f"  Root: {root}")
    print("=" * 70)

    all_issues_hist = []
    total_checks = 0

    for country, model_dir in sorted(COUNTRY_CONFIG.items()):
        exec_dir = root / country / model_dir / "Executables"
        if not exec_dir.exists():
            print(f"\n[SKIP] {country}: no Executables/ at {exec_dir}")
            continue

        print(f"\n{'─'*60}")
        print(f"[{country}]")

        # Find and parse demands for each scenario
        demands = {}  # scenario -> {tech -> {year -> val}}
        sources = {}  # scenario -> (suffix, path)

        for sc in SCENARIOS:
            for suffix in SUFFIXES_TO_TRY:
                txt = find_txt_file(exec_dir, sc, suffix)
                if txt:
                    demands[sc] = parse_specified_annual_demand(txt)
                    sources[sc] = (suffix, txt)
                    break

        found = [sc for sc in SCENARIOS if sc in demands]
        missing = [sc for sc in SCENARIOS if sc not in demands]
        if missing:
            print(f"  [WARN] Missing scenarios: {missing}")
        if not found:
            print(f"  [SKIP] No data files found")
            continue

        for sc in found:
            suffix, path = sources[sc]
            n_techs = len(demands[sc])
            print(f"  {sc:8s} ({suffix}): {n_techs} demand techs from {path.name}")

        # Compare across scenarios
        if len(found) < 2:
            print(f"  [SKIP] Only {len(found)} scenario — nothing to compare")
            continue

        # Get all techs and years
        all_techs = set()
        all_years = set()
        for sc in found:
            for tech, yvals in demands[sc].items():
                all_techs.add(tech)
                all_years.update(yvals.keys())
        all_techs = sorted(all_techs)
        all_years = sorted(all_years)

        # Compare
        HISTORICAL_END = 2024  # demands must match through here
        country_issues_hist = []  # ≤2024: these are ERRORS
        country_issues_fwd = []   # 2025+: expected (policy measures)
        for tech in all_techs:
            for year in all_years:
                vals = {}
                for sc in found:
                    v = demands[sc].get(tech, {}).get(year)
                    if v is not None:
                        vals[sc] = v

                if len(vals) < 2:
                    continue
                total_checks += 1

                vlist = list(vals.values())
                spread = max(vlist) - min(vlist)
                if spread > 0.001:
                    issue = {
                        "country": country, "tech": tech, "year": year,
                        "vals": vals, "spread": spread,
                    }
                    if year <= HISTORICAL_END:
                        country_issues_hist.append(issue)
                        all_issues_hist.append(issue)
                    else:
                        country_issues_fwd.append(issue)

        if not country_issues_hist and not country_issues_fwd:
            print(f"  [OK] All demands identical across {found}")
        else:
            if country_issues_hist:
                print(f"  [!!!] {len(country_issues_hist)} ERRORS (≤{HISTORICAL_END} — should be identical):")
                by_tech = defaultdict(list)
                for iss in country_issues_hist:
                    by_tech[iss["tech"]].append(iss)
                for tech in sorted(by_tech):
                    issues = by_tech[tech]
                    years_affected = sorted(set(i["year"] for i in issues))
                    worst = max(i["spread"] for i in issues)
                    first = issues[0]
                    val_str = " ".join(f"{sc}={v:.2f}" for sc, v in first["vals"].items())
                    print(f"    {tech:12s}: {len(issues)} years ({min(years_affected)}-{max(years_affected)}), "
                          f"worst spread={worst:.3f} PJ")
                    print(f"      e.g. {first['year']}: {val_str}")
            else:
                print(f"  [OK] Historical demands (≤{HISTORICAL_END}) identical across scenarios")

            if country_issues_fwd:
                n_transport = sum(1 for i in country_issues_fwd if 'TRO' in i['tech'] or 'TRN' in i['tech'] or 'PAS' in i['tech'])
                n_efficiency = len(country_issues_fwd) - n_transport
                print(f"  [info] {len(country_issues_fwd)} post-{HISTORICAL_END} differences "
                      f"({n_transport} transport, {n_efficiency} efficiency) — expected from policy measures")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"  Total checks: {total_checks}")
    print(f"  Historical errors (≤2024): {len(all_issues_hist)}")
    if all_issues_hist:
        print(f"\n  Affected countries:")
        by_country = defaultdict(int)
        for iss in all_issues_hist:
            by_country[iss["country"]] += 1
        for c, n in sorted(by_country.items()):
            print(f"    {c}: {n} mismatches in historical years")
        print(f"\n  ACTION: historical demands must be identical across scenarios.")
        print(f"  Copy the BAU demand block to NDCNEW/LTSNEW for years ≤2024.")
        sys.exit(1)
    else:
        print(f"\n  All historical demands (≤2024) identical. Post-2024 differences are policy measures.")
        sys.exit(0)


if __name__ == "__main__":
    main()
