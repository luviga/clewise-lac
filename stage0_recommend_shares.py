#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 0: Recommended Shares (D) for Stage 1
=============================================
For BAU ≤2024, classifies each tech and computes a recommended share D
that sums to 100%, based on the relationship between:

  A = LowerLimit / Total_Gen          (what the encoding demands)
  B'= ResidualCap × CF × AF × 31.536 / Total_Gen  (existing plant ceiling)
  B = (ResidualCap + cumul. MinCapInvest) × CF × AF × 31.536 / Total_Gen  (full ceiling)
  C = ActualProduction / Total_Gen    (what the optimizer chose)

Classification:
  CONSTRAINED : C ≈ A  →  D = A   (floor is binding)
  PUSH_UP     : C << B →  D = B   (unused capacity, increase lower limit)
  FILLER      : else   →  D adjusts proportionally so sum = 100%

Run from: MODELS_LAC_4/
Usage:
  python stage0_recommend_shares.py [--countries Honduras Jamaica]

Reads:
  _STAGE0_OUTPUT/STAGE0_CAPACITY_CEILING.csv
  B1_Output_Params/{scenario}/TotalAnnualMinCapacityInvestment.csv
  B1_Output_Params/{scenario}/ResidualCapacity.csv
  B1_Output_Params/{scenario}/CapacityFactor.csv
  B1_Output_Params/{scenario}/AvailabilityFactor.csv

Writes:
  _STAGE0_OUTPUT/STAGE0_RECOMMENDED_SHARES.csv
"""

import os, sys, argparse
from pathlib import Path
import pandas as pd
import numpy as np

MODELS_LAC_ROOT = "./"
STAGE0_OUTPUT_DIR = "./_STAGE0_OUTPUT"
CAU = 31.536
MAX_YEAR = 2024  # Only historical years

# Classification thresholds
CLOSE_THRESHOLD = 0.10    # C is "close to" A if |C-A|/max(C,A) < 10%
UNDERUTIL_THRESHOLD = 0.50  # C is "much smaller than" B if C/B < 50%

COUNTRY_CONFIG = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}

PP_PREFIXES = ("PP", "PWR")


def is_pp(t):
    return str(t).strip().upper().startswith(PP_PREFIXES)


def read_b1_csv(b1_dir, scenario, filename):
    p = b1_dir / scenario / filename
    if not p.exists():
        return None
    df = pd.read_csv(p)
    for col in ["YEAR", "Value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_cumulative_capacity(b1_dir, scenario):
    """
    Compute accumulated capacity per tech per year:
    AccumCap[tech, year] = ResidualCapacity[tech, year]
                         + sum(MinCapacityInvestment[tech, y] for y <= year)
    """
    df_rc = read_b1_csv(b1_dir, scenario, "ResidualCapacity.csv")
    df_mci = read_b1_csv(b1_dir, scenario, "TotalAnnualMinCapacityInvestment.csv")

    if df_rc is None or df_rc.empty:
        return {}

    # Pivot residual capacity
    rc = df_rc.pivot_table(index="TECHNOLOGY", columns="YEAR",
                           values="Value", aggfunc="sum").fillna(0)

    # Pivot min capacity investment (may not exist for all techs)
    if df_mci is not None and not df_mci.empty:
        mci = df_mci.pivot_table(index="TECHNOLOGY", columns="YEAR",
                                 values="Value", aggfunc="sum").fillna(0)
    else:
        mci = pd.DataFrame()

    result = {}
    all_techs = sorted(set(rc.index) | (set(mci.index) if not mci.empty else set()))

    for tech in all_techs:
        if not is_pp(tech):
            continue
        for yr in sorted(rc.columns):
            if yr > MAX_YEAR:
                continue
            # Residual capacity at year
            res = float(rc.loc[tech, yr]) if tech in rc.index and yr in rc.columns else 0.0

            # Cumulative min capacity investment up to year
            cum_invest = 0.0
            if not mci.empty and tech in mci.index:
                for y in sorted(mci.columns):
                    if y <= yr:
                        cum_invest += float(mci.loc[tech, y]) if y in mci.columns else 0.0

            result[(tech, int(yr))] = res + cum_invest

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Stage 0: Compute recommended D shares for Stage 1")
    parser.add_argument("--countries", nargs="*", default=[])
    parser.add_argument("--close-threshold", type=float, default=CLOSE_THRESHOLD,
                        help=f"C≈A threshold (default {CLOSE_THRESHOLD})")
    parser.add_argument("--underutil-threshold", type=float, default=UNDERUTIL_THRESHOLD,
                        help=f"C<<B threshold (default {UNDERUTIL_THRESHOLD})")
    args = parser.parse_args()

    root = Path(MODELS_LAC_ROOT).resolve()
    s0_dir = Path(STAGE0_OUTPUT_DIR)

    # Read existing ceiling data (has A, B', C for all scenarios/years)
    ceil_path = s0_dir / "STAGE0_CAPACITY_CEILING.csv"
    if not ceil_path.exists():
        print("[ERROR] Run stage0_capacity_check.py first.")
        sys.exit(1)

    df_ceil = pd.read_csv(ceil_path)

    print("=" * 70)
    print("STAGE 0: Recommended Shares (D) for Stage 1")
    print("=" * 70)
    print(f"Thresholds: C≈A if ratio < {args.close_threshold:.0%}, "
          f"C<<B if ratio < {args.underutil_threshold:.0%}")

    all_rows = []

    for country, model_dir in COUNTRY_CONFIG.items():
        if args.countries and country not in args.countries:
            continue

        b1_dir = root / country / model_dir / "B1_Output_Params"
        if not b1_dir.exists():
            print(f"\n  [SKIP] {country}: B1_Output_Params not found")
            continue

        print(f"\n{'='*60}\n{country}")

        # Get BAU ceiling data, ≤2024 only
        mask = (
            (df_ceil["Country"] == country) &
            (df_ceil["Scenario"] == "BAU") &
            (df_ceil["Year"] <= MAX_YEAR)
        )
        bau = df_ceil[mask].copy()

        if bau.empty:
            print(f"  [SKIP] No BAU ceiling data for ≤{MAX_YEAR}")
            continue

        # Get CF and AF for full-B computation
        df_cf = read_b1_csv(b1_dir, "BAU", "CapacityFactor.csv")
        df_af = read_b1_csv(b1_dir, "BAU", "AvailabilityFactor.csv")
        cf_pivot = pd.DataFrame()
        af_pivot = pd.DataFrame()
        if df_cf is not None and not df_cf.empty:
            cf_pivot = df_cf.pivot_table(index="TECHNOLOGY", columns="YEAR",
                                         values="Value", aggfunc="sum").fillna(0)
        if df_af is not None and not df_af.empty:
            af_pivot = df_af.pivot_table(index="TECHNOLOGY", columns="YEAR",
                                         values="Value", aggfunc="sum").fillna(0)

        # Compute accumulated capacity (residual + cumulative investment)
        accum_cap = get_cumulative_capacity(b1_dir, "BAU")

        # Process each year
        for yr in sorted(bau["Year"].unique()):
            yr_data = bau[bau["Year"] == yr].copy()
            total_gen = yr_data["Total_Gen_PJ"].iloc[0]

            techs = []
            for _, row in yr_data.iterrows():
                tech = row["Technology"]
                a = row["Share_A_LowerLimit_Pct"]
                b_prime = row["Share_B_Ceiling_Pct"]  # residual only
                c = row["Share_C_Actual_Pct"]

                # Compute full B (with investment)
                ac = accum_cap.get((tech, int(yr)), 0.0)
                cf_val = float(cf_pivot.loc[tech, yr]) if (
                    not cf_pivot.empty and tech in cf_pivot.index and yr in cf_pivot.columns
                ) else 0.0
                af_val = float(af_pivot.loc[tech, yr]) if (
                    not af_pivot.empty and tech in af_pivot.index and yr in af_pivot.columns
                ) else 1.0
                if af_val == 0:
                    af_val = 1.0

                full_potential = ac * cf_val * af_val * CAU
                b_full = full_potential / total_gen * 100 if total_gen > 0 else 0.0

                techs.append({
                    "tech": tech, "a": a, "b_prime": b_prime,
                    "b_full": round(b_full, 2), "c": c,
                    "full_potential_pj": round(full_potential, 4),
                    "accum_cap_gw": round(ac, 4),
                })

            # Classify
            for t in techs:
                a, b, c = t["a"], t["b_full"], t["c"]

                # C ≈ A? (close to floor — floor is binding)
                denom = max(c, a, 0.01)
                if abs(c - a) / denom < args.close_threshold:
                    t["category"] = "CONSTRAINED"
                    t["d_raw"] = a
                # C > A and C > B? (optimizer exceeded both floor and ceiling)
                elif c > a and c > b:
                    t["category"] = "OPTIMIZER"
                    t["d_raw"] = c
                # B > C and B > A? (capacity above both actual and floor — push up)
                elif b > c and b > a and b > 0.01:
                    t["category"] = "PUSH_UP"
                    t["d_raw"] = b
                # Everything else — filler
                else:
                    t["category"] = "FILLER"
                    t["d_raw"] = c

            # --- Column D: adjust only FILLERs so D sums to 100% ---
            locked_sum = sum(t["d_raw"] for t in techs if t["category"] != "FILLER")
            filler_techs = [t for t in techs if t["category"] == "FILLER"]
            filler_c_sum = sum(t["c"] for t in filler_techs)
            target_filler = 100.0 - locked_sum

            for t in techs:
                t["d"] = t["d_raw"]  # start from raw

            if filler_c_sum > 0.01 and filler_techs:
                scale = target_filler / filler_c_sum
                for t in filler_techs:
                    t["d"] = round(t["c"] * scale, 2)
            elif filler_techs:
                per = target_filler / len(filler_techs)
                for t in filler_techs:
                    t["d"] = round(per, 2)

            # Edge case: if locked_sum > 100, scale D proportionally
            total_d = sum(t["d"] for t in techs)
            if abs(total_d - 100.0) > 0.1:
                scale = 100.0 / total_d if total_d > 0 else 1.0
                for t in techs:
                    t["d"] = round(t["d"] * scale, 2)

            # --- Column E: balanced recommendation based on max(A, B) ---
            # Start from max(A, B) per tech — respect the stronger constraint
            # Then scale ALL techs proportionally to sum to 100%
            for t in techs:
                t["e_raw"] = max(t["a"], t["b_full"])

            e_raw_sum = sum(t["e_raw"] for t in techs)
            if e_raw_sum > 0.01:
                e_scale = 100.0 / e_raw_sum
                for t in techs:
                    t["e"] = round(t["e_raw"] * e_scale, 2)
            else:
                for t in techs:
                    t["e"] = 0.0

            # Record
            for t in techs:
                all_rows.append({
                    "Country": country,
                    "Year": int(yr),
                    "Technology": t["tech"],
                    "Share_A_LowerLimit_Pct": t["a"],
                    "Share_Bprime_Residual_Pct": t["b_prime"],
                    "Share_B_FullCeiling_Pct": t["b_full"],
                    "Share_C_Actual_Pct": t["c"],
                    "Share_D_Recommended_Pct": round(t["d"], 2),
                    "Share_E_Proportional_Pct": round(t["e"], 2),
                    "Category": t["category"],
                    "AccumCap_GW": t["accum_cap_gw"],
                    "FullPotential_PJ": t["full_potential_pj"],
                    "Total_Gen_PJ": round(total_gen, 4),
                })

            # Print summary for this year
            n_con = sum(1 for t in techs if t["category"] == "CONSTRAINED")
            n_push = sum(1 for t in techs if t["category"] == "PUSH_UP")
            n_opt = sum(1 for t in techs if t["category"] == "OPTIMIZER")
            n_fill = sum(1 for t in techs if t["category"] == "FILLER")
            d_sum = sum(t["d"] for t in techs)
            e_sum = sum(t["e"] for t in techs)
            print(f"  {yr}: {n_con} constrained, {n_push} push_up, {n_opt} optimizer, "
                  f"{n_fill} filler | D={d_sum:.1f}% E={e_sum:.1f}%")

    # Write
    if not all_rows:
        print("\n[WARN] No data.")
        return

    df = pd.DataFrame(all_rows)
    out_path = s0_dir / "STAGE0_RECOMMENDED_SHARES.csv"
    df.to_csv(out_path, index=False)
    print(f"\n[Wrote] {out_path} ({len(df)} rows)")

    # Print 2024 summary per country
    print(f"\n{'='*70}")
    print("2024 RECOMMENDED SHARES — BAU")
    print(f"{'='*70}")
    d2024 = df[df["Year"] == 2024]
    for country in sorted(d2024["Country"].unique()):
        sub = d2024[d2024["Country"] == country].sort_values(
            "Share_D_Recommended_Pct", ascending=False)
        total_gen = sub["Total_Gen_PJ"].iloc[0]
        d_sum = sub["Share_D_Recommended_Pct"].sum()
        e_sum = sub["Share_E_Proportional_Pct"].sum()
        print(f"\n{country} (Total={total_gen:.1f} PJ, D={d_sum:.1f}%, E={e_sum:.1f}%)")
        print(f"  {'Tech':15s} {'A':>6s} {'B\'':>6s} {'B':>6s} {'C':>6s} {'D':>6s} {'E':>6s}  Cat")
        for _, r in sub.iterrows():
            print(f"  {r['Technology']:15s} {r['Share_A_LowerLimit_Pct']:5.1f}% "
                  f"{r['Share_Bprime_Residual_Pct']:5.1f}% "
                  f"{r['Share_B_FullCeiling_Pct']:5.1f}% "
                  f"{r['Share_C_Actual_Pct']:5.1f}% "
                  f"{r['Share_D_Recommended_Pct']:5.1f}% "
                  f"{r['Share_E_Proportional_Pct']:5.1f}%  "
                  f"{r['Category']}")

    print(f"\n{'='*70}\nDONE.")
    print("Stage 1 reads: STAGE0_RECOMMENDED_SHARES.csv (D column = starting shares)")


if __name__ == "__main__":
    main()
