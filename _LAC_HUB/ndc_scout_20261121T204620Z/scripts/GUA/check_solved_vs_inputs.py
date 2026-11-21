"""Compare solved plant activity (stage3 TotalTechnologyAnnualActivity) with compiled
activity limits (TotalTechnologyAnnualActivityLowerLimit / UpperLimit) for Guatemala.

Usage: python -I check_solved_vs_inputs.py <model_root> <out_csv>
Read-only. Prints the sheet layout first, then writes one row per scenario, technology and
year 2025-2050 where solved activity is below the lower limit or above the upper limit
(tolerance 1e-3 PJ absolute and 0.5 percent relative).
"""
import csv
import os
import sys

import pandas as pd

ROOT = sys.argv[1]
OUT = sys.argv[2]
P = os.path.join(ROOT, "Guatemala", "GUA_ENERGY", "B1_Output_Params")
XL = os.path.join(ROOT, "_STAGE3_RESULTS", "stage3_results.xlsx")
SCEN = ["BAU", "NDCNEW", "LTSNEW"]


def limits(scen, name):
    df = pd.read_csv(os.path.join(P, scen, name + ".csv"))
    df = df[df["TECHNOLOGY"].astype(str).str.match(r"^(PP|IMP_ELE|TR|Techs_)")]
    return {(r.TECHNOLOGY, int(r.YEAR)): float(r.Value) for r in df.itertuples()}


def main():
    x = pd.read_excel(XL, sheet_name="TotalTechnologyAnnualActivity", engine="openpyxl")
    print("columns:", list(x.columns)[:20])
    print(x.head(3).to_string())
    ccol = [c for c in x.columns if str(c).lower() in ("country", "pais", "region_name")]
    print("country-like columns:", ccol)
    # find columns
    cols = {str(c).lower(): c for c in x.columns}
    country_col = None
    for c in x.columns:
        vals = x[c].astype(str).unique()[:50]
        if any("Guatemala" in v or v == "GUA" for v in vals):
            country_col = c
            break
    print("country column:", country_col)
    g = x[x[country_col].astype(str).isin(["Guatemala", "GUA"])]
    tech_col = [c for c in g.columns if "tech" in str(c).lower()][0]
    year_col = [c for c in g.columns if "year" in str(c).lower()][0]
    scen_col = [c for c in g.columns if "scen" in str(c).lower()][0]
    val_col = [c for c in g.columns if str(c).lower() in ("value", "valor", "val")][0]
    print("using", tech_col, year_col, scen_col, val_col)
    print("scenarios:", g[scen_col].unique())
    rows = []
    for s in SCEN:
        lo = limits(s, "TotalTechnologyAnnualActivityLowerLimit")
        up = limits(s, "TotalTechnologyAnnualActivityUpperLimit")
        gs = g[g[scen_col].astype(str) == s]
        sol = gs.groupby([tech_col, year_col])[val_col].sum().to_dict()
        techs = sorted({k[0] for k in list(lo) + list(up)
                        if str(k[0]).startswith("PP") or k[0] == "IMP_ELE"})
        for t in techs:
            for y in range(2025, 2051):
                v = float(sol.get((t, y), 0.0))
                l = lo.get((t, y))
                u = up.get((t, y))
                tol_l = max(1e-3, 0.005 * abs(l)) if l is not None else 0
                tol_u = max(1e-3, 0.005 * abs(u)) if u is not None else 0
                kind = ""
                if l is not None and v < l - tol_l:
                    kind = "below lower limit"
                if u is not None and v > u + tol_u:
                    kind = "above upper limit"
                if kind:
                    rows.append([s, t, y, round(v, 4), "" if l is None else round(l, 4),
                                 "" if u is None else round(u, 4), kind])
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["scenario", "technology", "year", "solved_activity_PJ", "lower_limit_PJ",
                    "upper_limit_PJ", "finding"])
        w.writerows(rows)
    print("rows written:", len(rows))


if __name__ == "__main__":
    main()
