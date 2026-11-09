#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 0: Capacity Ceiling Check
=================================
Compares two shares per (country, scenario, tech, year):

  Share_A = LowerLimit / Total_Gen          (what the encoding demands)
  Share_B = ProductionPotential / Total_Gen  (what the plant can deliver)

Where ProductionPotential = ResidualCapacity × CapacityFactor × AvailabilityFactor × 31.536

If Share_A > Share_B, Stage 1 must cap and redistribute.

Run from: MODELS_LAC_4/
Usage:
  python stage0_capacity_check.py [--countries Ecuador Honduras]

Reads:
  B1_Output_Params/{scenario}/ResidualCapacity.csv
  B1_Output_Params/{scenario}/CapacityFactor.csv
  B1_Output_Params/{scenario}/AvailabilityFactor.csv
  B1_Output_Params/{scenario}/TotalTechnologyAnnualActivityLowerLimit.csv
  _STAGE0_OUTPUT/{Country}/EMPIRICAL_GEN__{Country}__{Scenario}_S0.csv

Writes:
  _STAGE0_OUTPUT/STAGE0_CAPACITY_CEILING.csv
  _STAGE0_OUTPUT/STAGE0_CEILING_VIOLATIONS.csv  (only rows where Share_A > Share_B)
"""

import os, sys, argparse
from pathlib import Path
import pandas as pd
import numpy as np

MODELS_LAC_ROOT = "./"
STAGE0_OUTPUT_DIR = "./_STAGE0_OUTPUT"
CAU = 31.536  # CapacityToActivityUnit (PJ/GW/yr)

SOURCE_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
PP_PREFIXES = ("PP", "PWR")

COUNTRY_CONFIG = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}


def is_pp(t):
    return str(t).strip().upper().startswith(PP_PREFIXES)


def read_b1_csv(b1_dir, scenario, filename):
    """Read a CSV from B1_Output_Params/{scenario}/"""
    p = b1_dir / scenario / filename
    if not p.exists():
        return None
    df = pd.read_csv(p)
    # Standardize columns
    for col in ["YEAR", "Value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def pivot_tech_year(df, value_col="Value"):
    """Pivot a B1 CSV into tech × year matrix."""
    if df is None or df.empty:
        return pd.DataFrame()
    if "TECHNOLOGY" not in df.columns or "YEAR" not in df.columns:
        return pd.DataFrame()
    return df.pivot_table(
        index="TECHNOLOGY", columns="YEAR",
        values=value_col, aggfunc="sum"
    ).fillna(0)


def read_empirical_gen(stage0_dir, country, scenario):
    """Read empirical generation from Stage 0 output."""
    s0_scen = f"{scenario}_S0"
    p = Path(stage0_dir) / country / f"EMPIRICAL_GEN__{country}__{s0_scen}.csv"
    if not p.exists():
        return pd.Series(dtype=float)
    df = pd.read_csv(p)
    return pd.Series(df["Empirical_Gen_PJ"].values, index=df["Year"].values)


def main():
    parser = argparse.ArgumentParser(
        description="Stage 0: Capacity ceiling check")
    parser.add_argument("--countries", nargs="*", default=[])
    args = parser.parse_args()

    root = Path(MODELS_LAC_ROOT).resolve()
    s0_dir = Path(STAGE0_OUTPUT_DIR)

    print("=" * 70)
    print("STAGE 0: Capacity Ceiling Check")
    print("=" * 70)

    # Load actual production from Stage 0 headroom decomposition
    hr_path = Path(STAGE0_OUTPUT_DIR) / "STAGE0_HEADROOM_DECOMPOSITION.csv"
    if hr_path.exists():
        df_hr = pd.read_csv(hr_path)
        df_hr["Year"] = pd.to_numeric(df_hr["Year"], errors="coerce").astype(int)
        print(f"Loaded HEADROOM_DECOMPOSITION: {len(df_hr)} rows")
    else:
        df_hr = pd.DataFrame()
        print("[WARN] STAGE0_HEADROOM_DECOMPOSITION.csv not found — Share_C will be empty")

    all_rows = []

    for country, model_dir in COUNTRY_CONFIG.items():
        if args.countries and country not in args.countries:
            continue

        b1_dir = root / country / model_dir / "B1_Output_Params"
        if not b1_dir.exists():
            print(f"  [SKIP] {country}: B1_Output_Params not found")
            continue

        print(f"\n{'='*60}\n{country}")

        for scenario in SOURCE_SCENARIOS:
            print(f"\n  {scenario}:")

            # Read B1 data
            df_rescap = read_b1_csv(b1_dir, scenario, "ResidualCapacity.csv")
            df_cf = read_b1_csv(b1_dir, scenario, "CapacityFactor.csv")
            df_af = read_b1_csv(b1_dir, scenario, "AvailabilityFactor.csv")
            df_ll = read_b1_csv(b1_dir, scenario,
                                "TotalTechnologyAnnualActivityLowerLimit.csv")

            # Pivot to tech × year
            rescap = pivot_tech_year(df_rescap)
            cf = pivot_tech_year(df_cf)
            af = pivot_tech_year(df_af)
            ll = pivot_tech_year(df_ll)

            if rescap.empty:
                print(f"    [WARN] No ResidualCapacity data")
                continue

            # Read empirical generation (denominator)
            emp_gen = read_empirical_gen(s0_dir, country, scenario)
            if emp_gen.empty:
                print(f"    [WARN] No empirical gen for {scenario}_S0")
                continue

            # Get PP-prefix techs present in lower limits
            pp_techs = sorted(
                set(t for t in ll.index if is_pp(t)) |
                set(t for t in rescap.index if is_pp(t))
            )

            # Common years
            years = sorted(
                set(ll.columns) &
                set(rescap.columns) &
                set(emp_gen.index)
            )

            n_violations = 0

            # Build actual production lookup from headroom data
            actual_lookup = {}
            if not df_hr.empty:
                scen_hr = df_hr[
                    (df_hr["Country"] == country) &
                    (df_hr["Scenario"] == f"{scenario}_S0")
                ]
                for _, row in scen_hr.iterrows():
                    actual_lookup[(row["Technology"], int(row["Year"]))] = row["Actual_PJ"]

            for tech in pp_techs:
                for yr in years:
                    # Lower limit
                    lower = float(ll.loc[tech, yr]) if tech in ll.index and yr in ll.columns else 0.0

                    # Production potential
                    rc = float(rescap.loc[tech, yr]) if tech in rescap.index and yr in rescap.columns else 0.0
                    c = float(cf.loc[tech, yr]) if tech in cf.index and yr in cf.columns else 0.0
                    a = float(af.loc[tech, yr]) if tech in af.index and yr in af.columns else 1.0
                    if a == 0:
                        a = 1.0  # default if not specified

                    prod_potential = rc * c * a * CAU

                    # Actual production from S0 run
                    actual = actual_lookup.get((tech, int(yr)), 0.0)

                    # Total generation (denominator)
                    total_gen = emp_gen.get(yr, 0)
                    if total_gen < 0.001:
                        continue

                    # Share A: lower limit as share of total
                    share_a = lower / total_gen * 100

                    # Share B: production potential as share of total
                    share_b = prod_potential / total_gen * 100 if prod_potential > 0 else 0.0

                    # Share C: actual production as share of total
                    share_c = actual / total_gen * 100

                    # Only record rows where at least one value > 0
                    if share_a < 0.001 and share_b < 0.001 and share_c < 0.001:
                        continue

                    violation = share_a > share_b and share_b > 0

                    if violation:
                        n_violations += 1

                    all_rows.append({
                        "Country": country,
                        "Scenario": scenario,
                        "Technology": tech,
                        "Year": int(yr),
                        "LowerLimit_PJ": round(lower, 4),
                        "ProdPotential_PJ": round(prod_potential, 4),
                        "Actual_PJ": round(actual, 4),
                        "Total_Gen_PJ": round(total_gen, 4),
                        "Share_A_LowerLimit_Pct": round(share_a, 2),
                        "Share_B_Ceiling_Pct": round(share_b, 2),
                        "Share_C_Actual_Pct": round(share_c, 2),
                        "Violation": violation,
                    })

            print(f"    {len(pp_techs)} PP techs × {len(years)} years | "
                  f"{n_violations} violations (Share_A > Share_B)")

    # Write outputs
    if not all_rows:
        print("\n[WARN] No data collected.")
        return

    df = pd.DataFrame(all_rows)
    out_dir = Path(STAGE0_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Full ceiling data
    df.to_csv(out_dir / "STAGE0_CAPACITY_CEILING.csv", index=False)
    print(f"\n[Wrote] STAGE0_CAPACITY_CEILING.csv ({len(df)} rows)")

    # Violations only
    violations = df[df["Violation"]].copy()
    violations.to_csv(out_dir / "STAGE0_CEILING_VIOLATIONS.csv", index=False)
    print(f"[Wrote] STAGE0_CEILING_VIOLATIONS.csv ({len(violations)} rows)")

    if len(violations) > 0:
        print(f"\n{'='*70}")
        print(f"VIOLATIONS SUMMARY: {len(violations)} cases where LowerLimit > ProductionPotential")
        print(f"{'='*70}")
        by_country = violations.groupby(["Country", "Scenario"]).size().reset_index(name="N")
        print(by_country.to_string(index=False))

        print(f"\nWorst violations (largest Share_A - Share_B):")
        violations["Gap_Pct"] = violations["Share_A_LowerLimit_Pct"] - violations["Share_B_Ceiling_Pct"]
        worst = violations.nlargest(10, "Gap_Pct")
        for _, r in worst.iterrows():
            print(f"  {r['Country']}/{r['Scenario']} {r['Technology']} {r['Year']}: "
                  f"LL={r['LowerLimit_PJ']:.2f} PJ > Ceiling={r['ProdPotential_PJ']:.2f} PJ "
                  f"(Share {r['Share_A_LowerLimit_Pct']:.1f}% > {r['Share_B_Ceiling_Pct']:.1f}%)")
    else:
        print(f"\n[OK] No violations — all lower limits are within production potential.")

    print(f"\n{'='*70}\nDONE.")
    print("Stage 1 reads STAGE0_CAPACITY_CEILING.csv as a cap per tech/year.")


if __name__ == "__main__":
    main()
