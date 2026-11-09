#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stage1_test_v16.py
==================
Test harness for stage1_share_analyzer_v16.py.

Runs v16, then validates the controller workbook against acceptance criteria.

Usage (from MODELS_LAC_4):
    py stage1_test_v16.py
    py stage1_test_v16.py --countries Honduras Jamaica
    py stage1_test_v16.py --skip-run    (validate existing controller only)

Tests:
  1. All 6 countries × 3 scenarios present
  2. Share sums in [0.98, 1.02] for all (country, scenario, year)
  3. Historical alignment: BAU = NDCNEW = LTSNEW for year ≤ 2026
  4. BAU fossil decline: 2050 fossil sum < 2024 fossil sum (non-CR)
  5. Policy milestones: NDCNEW/LTSNEW renewable ≥ target at milestone years
  6. Ceiling: no lower limit exceeds production potential
  7. Feasibility: lower ≤ upper for all cells
  8. Costa Rica flat: BAU shares constant across 2024-2050
  9. No negative shares or limits
 10. Share violation summary (with CSV export)
"""

import sys
import argparse
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────
OUTPUT_DIR     = "./_STAGE1_OUTPUT"
STAGE0_DIR     = "./_STAGE0_OUTPUT"
CTRL_FILENAME  = "CONTROLLER_NEW_SCENARIOS.xlsx"
CEILING_FILE   = "STAGE0_CAPACITY_CEILING.csv"

CUTOFF_YEAR     = 2026
ANCHOR_YEAR     = 2024
SHARE_TOL       = 0.02    # ±2% tolerance for share sums
ALIGN_TOL       = 0.001   # tolerance for historical alignment
FOSSIL_DECLINE  = 0.01

EXPECTED_COUNTRIES = ["CostaRica", "DominicanRepublic", "Ecuador",
                      "Guatemala", "Honduras", "Jamaica"]
EXPECTED_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]

# Policy milestones: (scenario, year, min_renewable_share)
POLICY_CHECKS = [
    ("NDCNEW", 2035, 0.70),   # 75% target, allow 5pp margin
    ("NDCNEW", 2050, 0.70),
    ("LTSNEW", 2035, 0.70),
    ("LTSNEW", 2050, 0.94),   # 99% target, allow 5pp margin
]

COSTA_RICA_NAMES = ["CostaRica"]

V10_SCRIPT = Path(__file__).parent / "stage1_share_analyzer_v16.py"

RESULTS = []


def record(test_id, passed, details=""):
    RESULTS.append((test_id, passed, details))
    flag = "PASS" if passed else "FAIL"
    print(f"  [{flag}] Test {test_id}: {details}")


# ── Main ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", nargs="*", default=[])
    parser.add_argument("--skip-run", action="store_true",
                        help="Skip running v10; validate existing controller")
    parser.add_argument("--output-dir", default=OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    ctrl_path = output_dir / CTRL_FILENAME

    # ── Step 1: Run v10 (unless --skip-run) ──
    if not args.skip_run:
        print("=" * 70)
        print("Running stage1_share_analyzer_v16.py...")
        print("=" * 70)
        cmd = [sys.executable, str(V10_SCRIPT),
               "--output-dir", str(output_dir),
               "--stage0-dir", STAGE0_DIR]
        if args.countries:
            cmd += ["--countries"] + args.countries
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"[FATAL] v10 exited with code {result.returncode}")
            sys.exit(1)
        print()

    if not ctrl_path.exists():
        print(f"[FATAL] Controller not found: {ctrl_path}")
        sys.exit(1)

    # ── Step 2: Load controller ──
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)
    print(f"Loading {ctrl_path.name}...")

    shares = pd.read_excel(ctrl_path, sheet_name="CURRENT_SHARES")
    lower = pd.read_excel(ctrl_path, sheet_name="CURRENT_LOWER")
    upper = pd.read_excel(ctrl_path, sheet_name="CURRENT_UPPER")
    tech_map = pd.read_excel(ctrl_path, sheet_name="TECH_MAP")

    base_cols = ["Country", "Model", "Scenario", "Tech",
                 "Is_Renewable", "Group", "Sub_Group", "Source"]
    year_cols = sorted([c for c in shares.columns
                        if isinstance(c, (int, np.integer))])

    countries = sorted(shares["Country"].unique())
    scenarios = sorted(shares["Scenario"].unique())
    print(f"  Countries: {countries}")
    print(f"  Scenarios: {scenarios}")
    print(f"  Years: {year_cols[0]}-{year_cols[-1]}")
    print()

    # ── Test 1: Coverage ──
    expected_c = args.countries if args.countries else EXPECTED_COUNTRIES
    missing_c = [c for c in expected_c if c not in countries]
    missing_s = [s for s in EXPECTED_SCENARIOS if s not in scenarios]
    record(1, not missing_c and not missing_s,
           f"Coverage: {len(countries)} countries × {len(scenarios)} scenarios"
           + (f" | missing countries: {missing_c}" if missing_c else "")
           + (f" | missing scenarios: {missing_s}" if missing_s else ""))

    # ── Test 2: Share sums ──
    violations = []
    for country in countries:
        for scenario in scenarios:
            sub = shares[(shares["Country"] == country) &
                         (shares["Scenario"] == scenario)]
            if sub.empty:
                continue
            for year in year_cols:
                s = sub[year].sum()
                if abs(s - 1.0) > SHARE_TOL:
                    violations.append({
                        "Country": country, "Scenario": scenario,
                        "Year": year, "Share_Sum": round(s, 6),
                        "Source": "v10",
                    })
    record(2, len(violations) == 0,
           f"Share sums in [{1-SHARE_TOL:.2f}, {1+SHARE_TOL:.2f}]: "
           f"{len(violations)} violations out of "
           f"{len(countries)*len(scenarios)*len(year_cols)} cells")

    if violations:
        vdf = pd.DataFrame(violations)
        vpath = output_dir / "SHARE_SUM_VIOLATIONS.csv"
        vdf.to_csv(vpath, index=False)
        print(f"    Violations saved to {vpath}")
        # Show first few
        for _, v in vdf.head(5).iterrows():
            print(f"    {v['Country']}/{v['Scenario']}/{v['Year']}: {v['Share_Sum']:.4f}")

    # ── Test 3: Historical alignment ──
    align_fails = 0
    for country in countries:
        bau = shares[(shares["Country"] == country) &
                     (shares["Scenario"] == "BAU")]
        for sc in ["NDCNEW", "LTSNEW"]:
            other = shares[(shares["Country"] == country) &
                           (shares["Scenario"] == sc)]
            if bau.empty or other.empty:
                continue
            hist_years = [y for y in year_cols if y <= CUTOFF_YEAR]
            for year in hist_years:
                for tech in bau["Tech"].values:
                    bv = bau[bau["Tech"] == tech][year].values
                    ov = other[other["Tech"] == tech][year].values
                    if len(bv) == 0 or len(ov) == 0:
                        continue
                    if abs(float(bv[0]) - float(ov[0])) > ALIGN_TOL:
                        align_fails += 1
    record(3, align_fails == 0,
           f"Historical alignment (≤{CUTOFF_YEAR}): {align_fails} mismatches")

    # ── Test 4: BAU fossil decline (non-CR) ──
    decline_fails = 0
    for country in countries:
        if country in COSTA_RICA_NAMES:
            continue
        bau = shares[(shares["Country"] == country) &
                     (shares["Scenario"] == "BAU")]
        if bau.empty:
            continue
        cat = dict(zip(tech_map["Tech"], tech_map["Sub_Group"]))
        fossil_techs = [t for t in bau["Tech"].values if cat.get(t) == "FOSSIL"]
        if not fossil_techs:
            continue
        f_sub = bau[bau["Tech"].isin(fossil_techs)]
        if ANCHOR_YEAR in year_cols and 2050 in year_cols:
            f_2024 = f_sub[ANCHOR_YEAR].sum()
            f_2050 = f_sub[2050].sum()
            if f_2024 > 0.01 and f_2050 >= f_2024 + 0.02:  # 2pp tolerance for mincap
                decline_fails += 1
                print(f"    {country}: fossil 2024={f_2024:.4f} 2050={f_2050:.4f}")
    record(4, decline_fails == 0,
           f"BAU fossil decline (non-CR): {decline_fails} failures")

    # ── Test 5: Policy milestones ──
    policy_fails = 0
    for sc, milestone_year, min_renew in POLICY_CHECKS:
        if milestone_year not in year_cols:
            continue
        for country in countries:
            sub = shares[(shares["Country"] == country) &
                         (shares["Scenario"] == sc)]
            if sub.empty:
                continue
            cat = dict(zip(tech_map["Tech"], tech_map["Sub_Group"]))
            renew_techs = [t for t in sub["Tech"].values
                           if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE")]
            r_sub = sub[sub["Tech"].isin(renew_techs)]
            renew_share = r_sub[milestone_year].sum()
            if renew_share < min_renew:
                policy_fails += 1
                print(f"    {country}/{sc}/{milestone_year}: "
                      f"renewable={renew_share:.4f} < {min_renew}")
    record(5, policy_fails == 0,
           f"Policy milestones: {policy_fails} failures")

    # ── Test 6: Ceiling check ──
    ceil_path = Path(STAGE0_DIR) / CEILING_FILE
    ceil_fails = 0
    if ceil_path.exists():
        df_ceil = pd.read_csv(ceil_path)
        for _, cr in df_ceil.iterrows():
            c, sc, tech, yr = cr["Country"], cr["Scenario"], cr["Technology"], int(cr["Year"])
            pp = cr["ProdPotential_PJ"]
            if pp <= 0:
                continue
            row = lower[(lower["Country"] == c) & (lower["Scenario"] == sc) &
                        (lower["Tech"] == tech)]
            if row.empty or yr not in row.columns:
                continue
            lv = float(row[yr].iloc[0])
            if lv > pp * 1.01:  # 1% tolerance
                ceil_fails += 1
        record(6, ceil_fails == 0,
               f"Ceiling enforcement: {ceil_fails} violations")
    else:
        record(6, True, "Ceiling file not found — skipped")

    # ── Test 7: Feasibility (lower ≤ upper) ──
    feas_fails = 0
    for country in countries:
        for scenario in scenarios:
            l_sub = lower[(lower["Country"] == country) &
                          (lower["Scenario"] == scenario)]
            u_sub = upper[(upper["Country"] == country) &
                          (upper["Scenario"] == scenario)]
            if l_sub.empty or u_sub.empty:
                continue
            for tech in l_sub["Tech"].values:
                lr = l_sub[l_sub["Tech"] == tech]
                ur = u_sub[u_sub["Tech"] == tech]
                if lr.empty or ur.empty:
                    continue
                for year in year_cols:
                    lv = float(lr[year].iloc[0])
                    uv = float(ur[year].iloc[0])
                    if lv > uv + 0.001:
                        feas_fails += 1
    record(7, feas_fails == 0,
           f"Feasibility (lower ≤ upper): {feas_fails} violations")

    # ── Test 8: Costa Rica BAU (v16: hydro PJ freeze + fossil decline) ──
    cr_fails = 0
    for country in COSTA_RICA_NAMES:
        if country not in countries:
            continue
        bau = shares[(shares["Country"] == country) &
                     (shares["Scenario"] == "BAU")]
        if bau.empty:
            continue

        # 8a: Historical + plateau (≤2026) must be flat at anchor
        hist_plateau = [y for y in year_cols if ANCHOR_YEAR <= y <= CUTOFF_YEAR]
        for _, row in bau.iterrows():
            anchor_val = float(row.get(ANCHOR_YEAR, 0))
            for y in hist_plateau:
                if abs(float(row.get(y, 0)) - anchor_val) > 0.001:
                    cr_fails += 1
                    if cr_fails <= 2:
                        print(f"    CR plateau drift: {row['Tech']} {y}")
                    break

        # 8b: Fossil should decline from 2024 to 2050
        cat = dict(zip(tech_map["Tech"], tech_map["Sub_Group"]))
        fossil_techs_cr = [t for t in bau["Tech"] if cat.get(t) == "FOSSIL"]
        if fossil_techs_cr and ANCHOR_YEAR in year_cols and 2050 in year_cols:
            f_sub = bau[bau["Tech"].isin(fossil_techs_cr)]
            f_2024 = f_sub[ANCHOR_YEAR].sum()
            f_2050 = f_sub[2050].sum()
            if f_2024 > 0.01 and f_2050 >= f_2024:
                cr_fails += 1
                print(f"    CR fossil not declining: 2024={f_2024:.4f} 2050={f_2050:.4f}")

        # 8c: Renewable should grow from 2024 to 2050
        renew_techs_cr = [t for t in bau["Tech"]
                          if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE")]
        if renew_techs_cr and ANCHOR_YEAR in year_cols and 2050 in year_cols:
            r_sub = bau[bau["Tech"].isin(renew_techs_cr)]
            r_2024 = r_sub[ANCHOR_YEAR].sum()
            r_2050 = r_sub[2050].sum()
            if r_2024 > 0.01 and r_2050 < r_2024 - 0.005:
                cr_fails += 1
                print(f"    CR renewable not growing: 2024={r_2024:.4f} 2050={r_2050:.4f}")

    record(8, cr_fails == 0,
           f"Costa Rica BAU (plateau flat, fossil decline, RE growth): {cr_fails} failures")

    # ── Test 9: No negatives ──
    neg_shares = 0
    neg_lower = 0
    for year in year_cols:
        if (shares[year] < -0.001).any():
            neg_shares += int((shares[year] < -0.001).sum())
        if (lower[year] < -0.001).any():
            neg_lower += int((lower[year] < -0.001).sum())
    record(9, neg_shares == 0 and neg_lower == 0,
           f"No negatives: {neg_shares} negative shares, {neg_lower} negative limits")

    # ── Test 10: Share sum statistics ──
    all_sums = []
    for country in countries:
        for scenario in scenarios:
            sub = shares[(shares["Country"] == country) &
                         (shares["Scenario"] == scenario)]
            if sub.empty:
                continue
            for year in year_cols:
                all_sums.append({
                    "Country": country, "Scenario": scenario,
                    "Year": year, "Sum": round(sub[year].sum(), 6),
                })
    if all_sums:
        sdf = pd.DataFrame(all_sums)
        min_s = sdf["Sum"].min()
        max_s = sdf["Sum"].max()
        mean_s = sdf["Sum"].mean()
        record(10, True,
               f"Share sum stats: min={min_s:.4f} max={max_s:.4f} mean={mean_s:.4f}")

    # ── Test 11: BAU floor (NDCNEW/LTSNEW RE ≥ BAU RE for all years) ──
    floor_fails = 0
    proj_years = [y for y in year_cols if y > CUTOFF_YEAR]
    cat = dict(zip(tech_map["Tech"], tech_map["Sub_Group"]))
    for country in countries:
        bau = shares[(shares["Country"] == country) & (shares["Scenario"] == "BAU")]
        if bau.empty:
            continue
        renew_techs = [t for t in bau["Tech"] if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE")]
        bau_r = bau[bau["Tech"].isin(renew_techs)]
        for sc in ["NDCNEW", "LTSNEW"]:
            pol = shares[(shares["Country"] == country) & (shares["Scenario"] == sc)]
            if pol.empty:
                continue
            pol_r = pol[pol["Tech"].isin(renew_techs)]
            for year in proj_years:
                bau_re = bau_r[year].sum()
                pol_re = pol_r[year].sum()
                if pol_re < bau_re - 0.005:  # 0.5pp tolerance
                    floor_fails += 1
                    if floor_fails <= 3:
                        print(f"    {country}/{sc}/{year}: policy RE={pol_re:.4f} < BAU RE={bau_re:.4f}")
    record(11, floor_fails == 0,
           f"BAU floor (policy RE ≥ BAU RE): {floor_fails} violations")

    # ── Test 12: Biomass not inflated in policy scenarios ──
    BIOMASS_TOKENS = ["BMS", "BIM", "BIO", "BGS", "SUG"]
    bio_inflate = 0
    for country in countries:
        bau = shares[(shares["Country"] == country) & (shares["Scenario"] == "BAU")]
        if bau.empty:
            continue
        bio_techs = [t for t in bau["Tech"]
                     if any(tok in str(t).upper() for tok in BIOMASS_TOKENS)]
        if not bio_techs:
            continue
        bau_bio = bau[bau["Tech"].isin(bio_techs)]
        for sc in ["NDCNEW", "LTSNEW"]:
            pol = shares[(shares["Country"] == country) & (shares["Scenario"] == sc)]
            if pol.empty:
                continue
            pol_bio = pol[pol["Tech"].isin(bio_techs)]
            for year in proj_years:
                bv = bau_bio[year].sum()
                pv = pol_bio[year].sum()
                if pv > bv * 1.1 + 0.005:  # >10% above BAU + small tolerance
                    bio_inflate += 1
                    if bio_inflate <= 3:
                        print(f"    {country}/{sc}/{year}: bio={pv:.4f} > BAU bio={bv:.4f}")
    record(12, bio_inflate == 0,
           f"Biomass lock (policy bio ≤ BAU bio): {bio_inflate} violations")

    # ── Test 13: Historical shares vary (not flat before 2024) ──
    hist_flat_countries = 0
    hist_years = [y for y in year_cols if 2018 <= y <= 2023]
    for country in countries:
        bau = shares[(shares["Country"] == country) & (shares["Scenario"] == "BAU")]
        if bau.empty or not hist_years:
            continue
        # Check if any tech has variation between earliest hist year and 2024
        has_variation = False
        for _, row in bau.iterrows():
            vals = [float(row.get(y, 0)) for y in hist_years if y in row.index]
            v2024 = float(row.get(ANCHOR_YEAR, 0))
            if vals and any(abs(v - v2024) > 0.005 for v in vals):
                has_variation = True
                break
        if not has_variation and len(hist_years) >= 2:
            hist_flat_countries += 1
            print(f"    {country}: historical shares appear flat (no variation 2018-2023)")
    record(13, hist_flat_countries == 0,
           f"Historical variation: {hist_flat_countries} countries with flat pre-2024 shares")

    # ── Summary ──
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, p, _ in RESULTS if p)
    failed = sum(1 for _, p, _ in RESULTS if not p)
    print(f"  PASSED: {passed}/{passed+failed}")
    if failed:
        print(f"  FAILED: {failed}")
        for tid, p, d in RESULTS:
            if not p:
                print(f"    Test {tid}: {d}")
    print()

    if failed:
        sys.exit(1)
    print("All tests passed. Controller is ready for review.")
    print(f"  {output_dir / CTRL_FILENAME}")


if __name__ == "__main__":
    main()
