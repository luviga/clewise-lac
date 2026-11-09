"""
Stage 3E — Extract results from GLPK _FINAL_0_output.txt files.

Parses the GLPK solution output (same logic as B1 data_processor) and
extracts key variables into a single summary Excel:
  - TotalTechnologyAnnualActivity  (generation by tech/year)
  - AnnualEmissions                (total emissions by emission/year)
  - AnnualTechnologyEmission       (emissions by tech/emission/year)
  - NewCapacity                    (new capacity by tech/year)
  - TotalCapacityAnnual            (total capacity by tech/year)
  - ProductionByTechnologyAnnual   (production by tech/fuel/year)

Usage (Windows Anaconda cmd):
    py stage3_results.py --root C:/path/to/MODELS_LAC_4
    py stage3_results.py --root . --countries CostaRica
    py stage3_results.py --root . --countries CostaRica --variables AnnualEmissions TotalTechnologyAnnualActivity
"""

import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd

# =====================================================================
# CONFIGURATION
# =====================================================================

SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection", "region": "CR"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY",              "region": "RD"},
    "Ecuador":           {"model_dir": "ECU_Energy",             "region": "ECU"},
    "Guatemala":         {"model_dir": "GUA_ENERGY",             "region": "GUA"},
    "Honduras":          {"model_dir": "HON_ENERGY",             "region": "HON"},
    "Jamaica":           {"model_dir": "JAM_ENERGY",             "region": "JAM"},
}

# Variables to extract and their index structure (from B1_Model_Structure)
# Format: {variable_name: [index_names]}
VARIABLES = {
    "TotalTechnologyAnnualActivity": ["r", "t", "y"],
    "AnnualEmissions":               ["r", "e", "y"],
    "AnnualTechnologyEmission":      ["r", "t", "e", "y"],
    "NewCapacity":                   ["r", "t", "y"],
    "TotalCapacityAnnual":           ["r", "t", "y"],
    "ProductionByTechnologyAnnual":  ["r", "t", "f", "y"],
}

# Column name mapping for index letters
INDEX_NAMES = {
    "r": "Region",
    "t": "Technology",
    "y": "Year",
    "e": "Emission",
    "f": "Fuel",
    "l": "Timeslice",
}


def parse_glpk_output(filepath, target_vars):
    """
    Parse a GLPK -o output file, extracting specified variables.
    
    Uses the same line-by-line pattern as B1 data_processor:
    - Find header "No. Column name  St   Activity..."
    - Read pairs of lines: line 1 = var name + indices, line 2 = values
    
    Returns dict: {var_name: list of (indices_tuple, value)}
    """
    results = {v: [] for v in target_vars}
    target_set = set(target_vars)
    
    ini_line = None
    end_line = None
    
    print(f"    Scanning {filepath.name} ...", end="", flush=True)
    t0 = time.time()
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        line_num = 0
        in_columns = False
        prev_line = None
        
        for raw_line in f:
            line_num += 1
            
            # Find the start of the columns section
            if not in_columns:
                if "No. Column name" in raw_line and "Activity" in raw_line:
                    in_columns = True
                    prev_line = None
                    skip_next = True  # skip the separator line
                continue
            
            # Check for end of columns section
            if "End of output" in raw_line or raw_line.strip().startswith("KKT") or "Karush-Kuhn-Tucker" in raw_line:
                break
            
            # Skip separator line after header
            if skip_next:
                skip_next = False
                prev_line = None
                continue
            
            # GLPK output alternates: odd lines have var name, even lines have values
            if prev_line is None:
                prev_line = raw_line
                continue
            
            # prev_line has the variable info, raw_line has the data
            var_line = prev_line
            data_line = raw_line
            prev_line = None
            
            # Parse variable line
            parts = [p for p in var_line.split() if p]
            if len(parts) < 2:
                continue
            
            var_with_idx = parts[1]  # e.g., "TotalTechnologyAnnualActivity[CR,PWRHYDDAM,2025]"
            
            if "[" not in var_with_idx:
                continue
            
            bracket_pos = var_with_idx.index("[")
            var_name = var_with_idx[:bracket_pos]
            
            if var_name not in target_set:
                continue
            
            idx_str = var_with_idx[bracket_pos+1:].rstrip("]").strip()
            indices = tuple(idx_str.split(","))
            
            # Parse data line for activity value
            data_parts = [p for p in data_line.split() if p]
            if len(data_parts) < 2:
                continue
            
            try:
                value = float(data_parts[1])
            except (ValueError, IndexError):
                continue
            
            if abs(value) > 1e-10:  # skip zeros
                results[var_name].append((indices, value))
    
    elapsed = time.time() - t0
    total = sum(len(v) for v in results.values())
    print(f" {total} values in {elapsed:.1f}s")
    
    return results


def results_to_dataframes(results, var_indices, country, scenario):
    """
    Convert parsed results into DataFrames with proper column names.
    Returns dict: {var_name: DataFrame}
    """
    dfs = {}
    for var_name, records in results.items():
        if not records:
            continue
        idx_names = var_indices[var_name]
        col_names = [INDEX_NAMES.get(i, i) for i in idx_names] + ["Value"]
        
        rows = []
        for indices, value in records:
            if len(indices) == len(idx_names):
                rows.append(list(indices) + [value])
        
        if rows:
            df = pd.DataFrame(rows, columns=col_names)
            df["Country"] = country
            df["Scenario"] = scenario
            # Convert Year to int where present
            if "Year" in df.columns:
                df["Year"] = df["Year"].astype(int)
            dfs[var_name] = df
    
    return dfs


def main():
    parser = argparse.ArgumentParser(description="Stage 3E: Extract GLPK results")
    parser.add_argument("--root", required=True, help="MODELS_LAC_4 root directory")
    parser.add_argument("--countries", nargs="*", default=[])
    parser.add_argument("--scenarios", nargs="*", default=SCENARIOS)
    parser.add_argument("--variables", nargs="*", default=list(VARIABLES.keys()),
                        help="Variables to extract")
    parser.add_argument("--output", default="_STAGE3_RESULTS/stage3_results.xlsx",
                        help="Output Excel path (relative to root)")
    parser.add_argument("--controller", default=None,
                        help="Path to controller xlsx (default: {root}/_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    countries = args.countries if args.countries else list(COUNTRY_CONFIG.keys())
    scenarios = args.scenarios
    target_vars = [v for v in args.variables if v in VARIABLES]

    print(f"Stage 3E Results Extractor")
    print(f"  Root:       {root}")
    print(f"  Countries:  {countries}")
    print(f"  Scenarios:  {scenarios}")
    print(f"  Variables:  {target_vars}")
    print()

    # Collect all DataFrames per variable
    all_dfs = {v: [] for v in target_vars}
    missing = []

    for country in countries:
        cfg = COUNTRY_CONFIG.get(country)
        if not cfg:
            print(f"[SKIP] Unknown country: {country}")
            continue

        for scenario in scenarios:
            exe_dir = root / country / cfg["model_dir"] / "Executables" / f"{scenario}_FINAL_0"
            output_file = exe_dir / f"{scenario}_FINAL_0_output.txt"

            if not output_file.exists():
                print(f"  [MISS] {country}/{scenario}: {output_file.name} not found")
                missing.append(f"{country}/{scenario}")
                continue

            print(f"  {country}/{scenario}:")
            results = parse_glpk_output(output_file, target_vars)
            dfs = results_to_dataframes(results, VARIABLES, country, scenario)

            for var_name, df in dfs.items():
                all_dfs[var_name].append(df)

    # Combine and write output
    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build share comparison data before writing Excel (so we can include it)
    share_comparison_df = None
    ctrl_path = Path(args.controller) if args.controller else root / "_STAGE2_OUTPUT" / "CONTROLLER_NEW_SCENARIOS.xlsx"
    if ctrl_path.exists() and all_dfs.get("TotalTechnologyAnnualActivity"):
        ctrl_shares = pd.read_excel(ctrl_path, sheet_name="CURRENT_SHARES")
        yr_cols = [c for c in ctrl_shares.columns if isinstance(c, (int, float))]

        act = pd.concat(all_dfs["TotalTechnologyAnnualActivity"], ignore_index=True)
        pp_act = act[act["Technology"].str.upper().str.startswith(("PP", "PWR"))].copy()
        totals = pp_act.groupby(["Country", "Scenario", "Year"])["Value"].sum().reset_index()
        totals = totals.rename(columns={"Value": "Total"})
        pp_act = pp_act.merge(totals, on=["Country", "Scenario", "Year"])
        pp_act["SolverShare"] = pp_act["Value"] / pp_act["Total"]

        share_rows = []
        # Find max year per country/scenario in solver output to skip beyond-horizon years
        solver_max_year = pp_act.groupby(["Country", "Scenario"])["Year"].max().to_dict()

        for _, crow in ctrl_shares.iterrows():
            c, s, tech = crow["Country"], crow["Scenario"], crow["Tech"]
            if c not in countries:
                continue
            max_yr = solver_max_year.get((c, s), 2050)
            for y in yr_cols:
                yi = int(y)
                if yi < 2025 or yi > max_yr:
                    continue
                ctrl_s = float(crow[y])
                solver_row = pp_act[
                    (pp_act["Country"] == c) & (pp_act["Scenario"] == s) &
                    (pp_act["Technology"] == tech) & (pp_act["Year"] == yi)
                ]
                if solver_row.empty:
                    # Zero controller share + zero solver output = PASS (tech inactive)
                    if ctrl_s < 1e-6:
                        solver_s = 0.0
                        dev = 0.0
                        status = "PASS"
                    else:
                        solver_s = 0.0
                        dev = -ctrl_s
                        abs_dev = abs(dev)
                        if abs_dev > 0.01:
                            status = "FAIL"
                        elif abs_dev > 0.003:
                            status = "WARN"
                        else:
                            status = "PASS"
                else:
                    solver_s = solver_row["SolverShare"].iloc[0]
                    dev = solver_s - ctrl_s
                    abs_dev = abs(dev)
                    if abs_dev > 0.01:
                        status = "FAIL"
                    elif abs_dev > 0.003:
                        status = "WARN"
                    else:
                        status = "PASS"
                share_rows.append({
                    "Country": c, "Scenario": s, "Technology": tech, "Year": yi,
                    "Ctrl_Share": ctrl_s, "Solver_Share": solver_s,
                    "Deviation": dev, "Status": status
                })
        share_comparison_df = pd.DataFrame(share_rows)

    print(f"\nWriting results to {out_path}")
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for var_name in target_vars:
            frames = all_dfs[var_name]
            if frames:
                combined = pd.concat(frames, ignore_index=True)
                cols = ["Country", "Scenario"] + [c for c in combined.columns 
                        if c not in ("Country", "Scenario")]
                combined = combined[cols]
                sheet = var_name[:31]
                combined.to_excel(writer, sheet_name=sheet, index=False)
                print(f"  {sheet}: {len(combined)} rows")
            else:
                print(f"  {var_name}: no data")

        if share_comparison_df is not None and len(share_comparison_df) > 0:
            share_comparison_df.to_excel(writer, sheet_name="ShareValidation", index=False)
            print(f"  ShareValidation: {len(share_comparison_df)} rows")

    # Quick summary: emissions divergence check
    print("\n" + "=" * 60)
    print("EMISSIONS DIVERGENCE CHECK")
    print("=" * 60)
    if all_dfs.get("AnnualEmissions"):
        em = pd.concat(all_dfs["AnnualEmissions"], ignore_index=True)
        for country in countries:
            cem = em[em["Country"] == country]
            if cem.empty:
                continue
            print(f"\n  {country}:")
            for year in [2025, 2030, 2035, 2040, 2050]:
                row = cem[cem["Year"] == year].groupby("Scenario")["Value"].sum()
                if not row.empty:
                    vals = "  ".join(f"{s}={v:.2f}" for s, v in row.items())
                    print(f"    {year}: {vals}")

    if missing:
        print(f"\n[WARN] Missing outputs: {missing}")

    # Share validation against controller
    if share_comparison_df is not None and len(share_comparison_df) > 0:
        print("\n" + "=" * 60)
        print("SHARE VALIDATION vs CONTROLLER")
        print("=" * 60)

        sv = share_comparison_df
        share_pass = len(sv[sv["Status"] == "PASS"])
        share_warn = len(sv[sv["Status"] == "WARN"])
        share_fail = len(sv[sv["Status"] == "FAIL"])

        status = "PASS" if share_fail == 0 else "FAIL"
        print(f"\n  Share match: {status}  ({share_pass} pass, {share_warn} warnings >0.3pp, {share_fail} failures >1pp)")

        # Max deviation per country/scenario
        print(f"\n  Max deviation per country/scenario:")
        for (c, s), g in sv.dropna(subset=["Deviation"]).groupby(["Country", "Scenario"]):
            worst = g.loc[g["Deviation"].abs().idxmax()]
            dev = abs(worst["Deviation"])
            print(f"    {c}/{s:<15} {dev:.4f}pp  ({worst['Technology']}/{worst['Year']}: ctrl={worst['Ctrl_Share']:.4f} solver={worst['Solver_Share']:.4f})")

        # Show failures
        fails = sv[sv["Status"] == "FAIL"].sort_values("Deviation", key=abs, ascending=False)
        if len(fails):
            print(f"\n  Top failures (>1pp):")
            for _, r in fails.head(20).iterrows():
                print(f"    FAIL {r['Country']}/{r['Scenario']}/{r['Technology']}/{r['Year']}: ctrl={r['Ctrl_Share']:.4f} solver={r['Solver_Share']:.4f} diff={r['Deviation']:.4f}")
            if len(fails) > 20:
                print(f"    ... and {len(fails)-20} more (see ShareValidation sheet)")

        print(f"\n  Full details in ShareValidation sheet — filter by Status column")
    elif not ctrl_path.exists():
        print(f"\n[SKIP] Controller not found at {ctrl_path} — share validation skipped")

    # RE TARGET VALIDATION — total renewable share vs policy milestones
    if ctrl_path.exists() and all_dfs.get("TotalTechnologyAnnualActivity"):
        print("\n" + "=" * 60)
        print("RE TARGET VALIDATION (total renewable share vs policy)")
        print("=" * 60)

        try:
            tech_map = pd.read_excel(ctrl_path, sheet_name="TECH_MAP")
            re_techs = set(tech_map[tech_map["Is_Renewable"] == 1.0]["Tech"])
        except Exception:
            re_techs = None
            print("  [SKIP] No TECH_MAP sheet in controller — cannot classify RE techs")

        if re_techs:
            act = pd.concat(all_dfs["TotalTechnologyAnnualActivity"], ignore_index=True)
            pp = act[act["Technology"].str.upper().str.startswith(("PP", "PWR"))].copy()
            pp["Is_RE"] = pp["Technology"].isin(re_techs).astype(int)

            totals = pp.groupby(["Country", "Scenario", "Year"])["Value"].sum().reset_index()
            totals = totals.rename(columns={"Value": "Total"})
            re_gen = pp[pp["Is_RE"] == 1].groupby(["Country", "Scenario", "Year"])["Value"].sum().reset_index()
            re_gen = re_gen.rename(columns={"Value": "RE"})
            merged = totals.merge(re_gen, on=["Country", "Scenario", "Year"], how="left").fillna(0)
            merged["RE_Share"] = merged["RE"] / merged["Total"]

            # Policy targets: {scenario: {year: target_share}}
            RE_TARGETS = {
                "NDCNEW": {2035: 0.75, 2050: 0.75},
                "LTSNEW": {2035: 0.75, 2050: 0.99},
            }
            RE_TOLERANCE = 0.02  # 2pp tolerance

            re_pass = 0
            re_fail = 0
            re_rows = []

            for country in countries:
                for scen, year_targets in RE_TARGETS.items():
                    for year, target in year_targets.items():
                        row = merged[(merged["Country"] == country) &
                                     (merged["Scenario"] == scen) &
                                     (merged["Year"] == year)]
                        if row.empty:
                            continue
                        actual = row["RE_Share"].iloc[0]
                        diff = actual - target
                        # Pass if actual >= target - tolerance (allow slight undershoot)
                        ok = actual >= target - RE_TOLERANCE
                        status = "PASS" if ok else "FAIL"
                        if ok:
                            re_pass += 1
                        else:
                            re_fail += 1
                        re_rows.append({
                            "Country": country, "Scenario": scen, "Year": year,
                            "Target": target, "Actual": actual,
                            "Diff": diff, "Status": status
                        })

            re_status = "PASS" if re_fail == 0 else "FAIL"
            print(f"\n  RE targets: {re_status}  ({re_pass} pass, {re_fail} fail, tolerance={RE_TOLERANCE*100:.0f}pp)")

            print(f"\n  {'Country':<22} {'Scenario':<10} {'Year':>5} {'Target':>8} {'Actual':>8} {'Diff':>8} {'Status'}")
            print(f"  {'-'*22} {'-'*10} {'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*6}")
            for r in re_rows:
                flag = " <--" if r["Status"] == "FAIL" else ""
                print(f"  {r['Country']:<22} {r['Scenario']:<10} {r['Year']:>5} "
                      f"{r['Target']*100:>7.1f}% {r['Actual']*100:>7.1f}% {r['Diff']*100:>+7.1f}pp {r['Status']}{flag}")

            # Also show BAU RE share for context
            print(f"\n  BAU renewable share (no target — context only):")
            for country in countries:
                bau = merged[(merged["Country"] == country) & (merged["Scenario"] == "BAU")]
                vals = []
                for y in [2025, 2030, 2035, 2050]:
                    r = bau[bau["Year"] == y]
                    if not r.empty:
                        vals.append(f"{y}={r['RE_Share'].iloc[0]*100:.1f}%")
                print(f"    {country:<22} {', '.join(vals)}")

    print(f"\nDone. Results saved to {out_path}")


if __name__ == "__main__":
    main()
