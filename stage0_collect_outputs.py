#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 0: Collect Outputs and Compute Empirical Denominators
=============================================================
Run from: MODELS_LAC_4/   (after stage0_run_all.bat completes)

Usage:
  python stage0_collect_outputs.py [--countries Ecuador Jamaica]
"""

import os, sys, argparse, re
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

MODELS_LAC_ROOT = "./"
OUTPUT_DIR = "./_STAGE0_OUTPUT"
SUFFIX = "_S0"
SOURCE_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
PP_PREFIXES = ("PP", "PWR")  # Must match Stage 1's PWR_PREFIXES
ELEC_FUEL_PATTERNS = ["ELE"]
TD_PATTERNS = ["ELE_TRN","ELE_TRANS","ELETTRN","TDELE","TD_ELE","TRANS_ELE",
               "ELE_DTR","ELE_DIST","ELEDTR","ELEDIST","TD_DIST","DIST_ELE"]

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY"},
    "Ecuador":           {"model_dir": "ECU_Energy"},
    "Guatemala":         {"model_dir": "GUA_ENERGY"},
    "Honduras":          {"model_dir": "HON_ENERGY"},
    "Jamaica":           {"model_dir": "JAM_ENERGY"},
}

def is_pp(t): return str(t).upper().startswith(PP_PREFIXES)
def read_csv(d, f):
    p = d / f
    return pd.read_csv(p) if p.exists() else None


def parse_glpk_output(path):
    """
    Parse GLPK old-style -o output. Format is pairs of lines:
      Line N:    <num> <VarName>[<idx1>,<idx2>,...]\n
      Line N+1:                     <status>  <activity>  <lower>  <upper>
    B1's data_processor reads these with step=2, extracting the variable
    name from line N and the activity value from line N+1.

    TotalTechnologyAnnualActivity indices: [region, tech, year]
    or sometimes [region, mode, tech, year] — we handle both.
    """
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Find the column section
    col_start = None
    col_end = None
    for i, line in enumerate(lines):
        if "No. Column name" in line and "Activity" in line:
            col_start = i + 2  # skip header + separator line
        if col_start and i > col_start and line.strip().startswith("End of output"):
            col_end = i
            break

    if col_start is None:
        # Try alternate: just scan all lines
        col_start = 0
        col_end = len(lines)

    # Parse pairs of lines
    i = col_start
    while i < (col_end or len(lines)) - 1:
        line1 = lines[i]
        line2 = lines[i + 1] if i + 1 < len(lines) else ""

        # Check if line1 contains a variable with brackets
        if "TotalTechnologyAnnualActivity[" in line1:
            # Extract variable and indices from line1
            bracket_match = re.search(r"TotalTechnologyAnnualActivity\[([^\]]+)\]", line1)
            if bracket_match:
                indices = bracket_match.group(1).split(",")

                # Extract activity value from line2
                parts2 = line2.split()
                activity = None
                if len(parts2) >= 2:
                    # parts2 looks like: ['BS', '0.75291', '0', ''] or ['*', '5.123', '0']
                    # The activity is typically the second non-empty element
                    for p in parts2:
                        try:
                            val = float(p)
                            if activity is None:
                                activity = val
                                break
                        except ValueError:
                            continue

                if activity is not None and activity != 0:
                    # Parse indices: [region, tech, year] or [region, mode, tech, year]
                    if len(indices) == 3:
                        region, tech, year = indices[0].strip(), indices[1].strip(), indices[2].strip()
                    elif len(indices) == 4:
                        region, _mode, tech, year = [x.strip() for x in indices]
                    else:
                        i += 2
                        continue

                    try:
                        rows.append({
                            "REGION": region,
                            "TECHNOLOGY": tech,
                            "YEAR": int(year),
                            "Value": float(activity),
                        })
                    except ValueError:
                        pass

            i += 2
            continue

        # Also capture ProductionByTechnologyAnnual as fallback
        if "ProductionByTechnologyAnnual[" in line1:
            bracket_match = re.search(r"ProductionByTechnologyAnnual\[([^\]]+)\]", line1)
            if bracket_match:
                indices = bracket_match.group(1).split(",")
                parts2 = line2.split()
                activity = None
                for p in parts2:
                    try:
                        activity = float(p)
                        break
                    except ValueError:
                        continue
                # indices: [region, tech, fuel, year] typically
                # We'll skip this for now, TotalTechnologyAnnualActivity is primary

        i += 2  # Always step by 2 in the column section

    return pd.DataFrame(rows)


def get_elec_demand(b1_dir, scenario):
    df = read_csv(b1_dir / scenario, "SpecifiedAnnualDemand.csv")
    if df is None or "FUEL" not in df.columns: return pd.Series(dtype=float)
    d = df[df["FUEL"].astype(str).str.contains("|".join(ELEC_FUEL_PATTERNS), case=False, na=False)].copy()
    if d.empty: return pd.Series(dtype=float)
    d["YEAR"] = pd.to_numeric(d["YEAR"], errors="coerce").astype(int)
    return d.groupby("YEAR")["Value"].sum().sort_index()

def get_loss(b1_dir, scenario, years):
    result = pd.Series(1.0, index=years, dtype=float)
    iar = read_csv(b1_dir / scenario, "InputActivityRatio.csv")
    oar = read_csv(b1_dir / scenario, "OutputActivityRatio.csv")
    if iar is None or oar is None: return result
    all_t = set(iar["TECHNOLOGY"].astype(str).unique()) if "TECHNOLOGY" in iar.columns else set()
    td = [t for t in all_t if any(p.upper() in t.upper() for p in TD_PATTERNS)]
    for tech in td:
        i = iar[iar["TECHNOLOGY"].astype(str)==tech].copy()
        o = oar[oar["TECHNOLOGY"].astype(str)==tech].copy()
        if i.empty or o.empty: continue
        i["YEAR"]=pd.to_numeric(i["YEAR"],errors="coerce").astype(int)
        o["YEAR"]=pd.to_numeric(o["YEAR"],errors="coerce").astype(int)
        iby=i.groupby("YEAR")["Value"].mean(); oby=o.groupby("YEAR")["Value"].mean()
        for y in years:
            iv=iby.get(y,1.0); ov=oby.get(y,1.0)
            if ov>0: result.loc[y]*=(iv/ov)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", nargs="*", default=[])
    args = parser.parse_args()

    root = Path(MODELS_LAC_ROOT).resolve()
    out_dir = Path(OUTPUT_DIR); out_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("STAGE 0: Collect Outputs")
    print("="*70)

    all_denom, all_hr, all_shares = [], [], []
    status_rows = []

    for cname, cfg in COUNTRY_CONFIG.items():
        if args.countries and cname not in args.countries: continue
        cdir = root / cname
        if not cdir.exists(): continue
        mdir = cdir / cfg["model_dir"]
        exec_dir = mdir / "Executables"
        b1_dir = mdir / "B1_Output_Params"

        print(f"\n{'='*60}\n{cname}")

        for sc_base in SOURCE_SCENARIOS:
            sc_s0 = f"{sc_base}{SUFFIX}"
            folder = exec_dir / f"{sc_s0}_0"
            if not folder.exists():
                print(f"  [SKIP] {sc_s0}: folder not found")
                status_rows.append({"Country":cname,"Scenario":sc_s0,"Status":"SKIP"})
                continue

            # Find output
            out_files = list(folder.glob("*_output.txt"))
            if not out_files:
                print(f"  [WARN] {sc_s0}: no output file")
                status_rows.append({"Country":cname,"Scenario":sc_s0,"Status":"NO_OUTPUT"})
                continue

            op = out_files[0]

            # Check if OPTIMAL or INFEASIBLE
            with open(op, "r", encoding="utf-8", errors="replace") as f:
                header = f.read(5000)  # first 5KB
            if "PROBLEM HAS NO" in header or "INFEASIBLE" in header.upper():
                print(f"  [INFEASIBLE] {sc_s0}")
                status_rows.append({"Country":cname,"Scenario":sc_s0,"Status":"INFEASIBLE"})
                continue

            if "OPTIMAL" not in header.upper():
                print(f"  [WARN] {sc_s0}: status unclear in output")

            print(f"\n  {sc_s0}: parsing {op.name}...")
            activity = parse_glpk_output(op)

            if activity.empty:
                print(f"    No TotalTechnologyAnnualActivity data found")
                status_rows.append({"Country":cname,"Scenario":sc_s0,"Status":"NO_DATA"})
                continue

            # Filter to PP techs
            pp = activity[activity["TECHNOLOGY"].apply(is_pp)].copy()
            all_techs = activity["TECHNOLOGY"].nunique()
            pp_techs = pp["TECHNOLOGY"].nunique()

            if pp.empty:
                print(f"    {all_techs} techs found but 0 PP-prefix")
                status_rows.append({"Country":cname,"Scenario":sc_s0,"Status":"NO_PP"})
                continue

            emp_gen = pp.groupby("YEAR")["Value"].sum().sort_index()
            by_tech = pp.pivot_table(index="TECHNOLOGY", columns="YEAR",
                                     values="Value", aggfunc="sum").fillna(0)

            print(f"    {pp_techs} PP techs | {all_techs} total techs | "
                  f"{emp_gen.min():.1f}-{emp_gen.max():.1f} PJ")
            status_rows.append({"Country":cname,"Scenario":sc_s0,"Status":"OK",
                               "PP_Techs":pp_techs,"Total_Techs":all_techs,
                               "Min_PJ":round(emp_gen.min(),2),"Max_PJ":round(emp_gen.max(),2)})

            # Save
            co = out_dir / cname; co.mkdir(exist_ok=True)
            emp_gen.reset_index().rename(columns={"YEAR":"Year","Value":"Empirical_Gen_PJ"}).to_csv(
                co / f"EMPIRICAL_GEN__{cname}__{sc_s0}.csv", index=False)
            by_tech.to_csv(co / f"PRODUCTION_BY_TECH__{cname}__{sc_s0}.csv")

            # Shares: each tech as % of total generation per year
            # Only historical years (<=2024) — Stage 1 handles 2025+ composition
            for yr in sorted(by_tech.columns):
                if yr > 2024:
                    continue
                total = emp_gen.get(yr, 0)
                if total < 0.001:
                    continue
                for tech in sorted(by_tech.index):
                    gen = float(by_tech.loc[tech, yr])
                    if gen > 0.0001:
                        all_shares.append({
                            "Country": cname, "Scenario": sc_s0, "Year": yr,
                            "Technology": tech,
                            "Gen_PJ": round(gen, 4),
                            "Total_Gen_PJ": round(total, 4),
                            "Share_Pct": round(gen / total * 100, 2),
                        })

            # Analytical comparison
            if b1_dir.exists():
                demand = get_elec_demand(b1_dir, sc_base)
                years = sorted(emp_gen.index)
                loss = get_loss(b1_dir, sc_base, years)
                for y in years:
                    d=demand.get(y,0); l=loss.get(y,1); analytical=d*l
                    empirical=emp_gen.get(y,0)
                    delta=empirical-analytical
                    dpct=(delta/analytical*100) if analytical>0 else 0
                    all_denom.append({"Country":cname,"Scenario":sc_s0,"Year":y,
                        "Empirical_Gen_PJ":round(empirical,4),
                        "Analytical_RequiredGen_PJ":round(analytical,4),
                        "Delta_PJ":round(delta,4),"Delta_Pct":round(dpct,1)})

                # Headroom
                ll = read_csv(b1_dir / sc_base, "TotalTechnologyAnnualActivityLowerLimit.csv")
                if ll is not None and not ll.empty:
                    ll["YEAR"]=pd.to_numeric(ll["YEAR"],errors="coerce").astype(int)
                    ll["Value"]=pd.to_numeric(ll["Value"],errors="coerce").fillna(0)
                    ups = ll.pivot_table(index="TECHNOLOGY",columns="YEAR",values="Value",aggfunc="sum")
                    for t in sorted(set(by_tech.index)&set(ups.index)):
                        for yr in sorted(set(by_tech.columns)&set(ups.columns)):
                            a=float(by_tech.loc[t,yr]); f=float(ups.loc[t,yr])
                            if a>0.001 or f>0.001:
                                all_hr.append({"Country":cname,"Scenario":sc_s0,
                                    "Technology":t,"Year":yr,
                                    "Actual_PJ":round(a,4),"Floor_PJ":round(f,4),
                                    "Headroom_PJ":round(a-f,4)})

    # Write
    print(f"\n{'='*70}\nWriting outputs...")

    # Status summary
    df_status = pd.DataFrame(status_rows)
    df_status.to_csv(out_dir / "STAGE0_RUN_STATUS.csv", index=False)
    print(f"  [Wrote] STAGE0_RUN_STATUS.csv")
    ok = len(df_status[df_status.get("Status","")=="OK"]) if "Status" in df_status.columns else 0
    inf = len(df_status[df_status.get("Status","")=="INFEASIBLE"]) if "Status" in df_status.columns else 0
    print(f"  Results: {ok} OK, {inf} INFEASIBLE, {len(df_status)-ok-inf} other")

    if all_denom:
        dd = pd.DataFrame(all_denom)
        with pd.ExcelWriter(out_dir/"STAGE0_DENOMINATORS.xlsx", engine="openpyxl") as w:
            for sc in SOURCE_SCENARIOS:
                sub=dd[dd["Scenario"]==f"{sc}{SUFFIX}"]
                if not sub.empty: sub.to_excel(w, sheet_name=f"{sc}{SUFFIX}", index=False)
            dd.to_excel(w, sheet_name="ALL", index=False)
        print(f"  [Wrote] STAGE0_DENOMINATORS.xlsx")
        big=dd[abs(dd["Delta_Pct"])>5]
        if not big.empty:
            print(f"\n  {len(big)} rows with >5% delta:")
            for _,r in big.head(8).iterrows():
                print(f"    {r['Country']}/{r['Scenario']}/{r['Year']}: {r['Delta_Pct']:.1f}%")

    if all_hr:
        pd.DataFrame(all_hr).to_csv(out_dir/"STAGE0_HEADROOM_DECOMPOSITION.csv", index=False)
        print(f"  [Wrote] STAGE0_HEADROOM_DECOMPOSITION.csv ({len(all_hr)} rows)")

    if all_shares:
        df_shares = pd.DataFrame(all_shares)
        df_shares.to_csv(out_dir/"STAGE0_SHARES.csv", index=False)
        print(f"  [Wrote] STAGE0_SHARES.csv ({len(df_shares)} rows)")

        # Quick sanity: check share sums per country/scenario/year
        sums = df_shares.groupby(["Country","Scenario","Year"])["Share_Pct"].sum()
        bad = sums[(sums - 100.0).abs() > 0.1]
        if len(bad) > 0:
            print(f"\n  [WARN] {len(bad)} country/scenario/year combos where shares don't sum to 100%:")
            for idx, val in bad.head(5).items():
                print(f"    {idx}: {val:.2f}%")
        else:
            print(f"  [OK] All share sums = 100.0% (+/- 0.1%)")

    print(f"\n{'='*70}\nDONE.")
    print("Stage 1 reads:")
    print("  shares = pd.read_csv('_STAGE0_OUTPUT/STAGE0_SHARES.csv')")
    print("  denoms = pd.read_csv('_STAGE0_OUTPUT/{country}/EMPIRICAL_GEN__{country}__BAU_S0.csv')")

if __name__ == "__main__":
    main()
