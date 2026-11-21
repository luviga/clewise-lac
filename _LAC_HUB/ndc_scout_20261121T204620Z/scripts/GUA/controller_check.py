"""Compare the Stage 2 controller lower limits (which Stage 3 patched into the solved data files,
upper = lower x 1.05, zero-lower techs uncapped for Guatemala) with the solved plant activity
for Guatemala. Read-only.

Usage: python -I controller_check.py <model_root> <out_csv>
"""
import csv
import os
import sys

import pandas as pd

ROOT, OUT = sys.argv[1], sys.argv[2]
CTL = os.path.join(ROOT, "_STAGE2_OUTPUT", "CONTROLLER_NEW_SCENARIOS.xlsx")
XL = os.path.join(ROOT, "_STAGE3_RESULTS", "stage3_results.xlsx")
YEARS = list(range(2025, 2051))

low = pd.read_excel(CTL, sheet_name="CURRENT_LOWER", engine="openpyxl")
tgt = pd.read_excel(CTL, sheet_name="TARGET_SHARES", engine="openpyxl")
low = low[low.Country == "Guatemala"]
tgt = tgt[tgt.Country == "Guatemala"]
act = pd.read_excel(XL, sheet_name="TotalTechnologyAnnualActivity", engine="openpyxl")
a = act[(act.Country == "Guatemala") & act.Technology.astype(str).str.startswith("PP")]
sol = a.groupby(["Scenario", "Technology", "Year"]).Value.sum().to_dict()

rows = []
summary = {}
for r in low.itertuples(index=False):
    d = r._asdict()
    s, t = d["Scenario"], d["Tech"]
    for y in YEARS:
        lo = None
        for k, v in d.items():
            if str(k).strip("_") == str(y) or k == y:
                lo = v
        if lo is None:
            lo = low.loc[(low.Scenario == s) & (low.Tech == t), y].iloc[0]
        v = float(sol.get((s, t, y), 0.0))
        up = lo * 1.05 if lo > 0 else None
        kind = ""
        if v < lo - max(1e-3, 0.005 * lo):
            kind = "below controller lower"
        elif up is not None and v > up + max(1e-3, 0.005 * up):
            kind = "above lower x 1.05"
        if kind:
            rows.append([s, t, y, round(v, 4), round(lo, 4), "" if up is None else round(up, 4), kind])
            summary[(s, kind)] = summary.get((s, kind), 0) + 1

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["scenario", "technology", "year", "solved_PJ", "controller_lower_PJ", "upper_PJ", "finding"])
    w.writerows(rows)
print("violations:", summary)
print("controller techs:", sorted(low.Tech.unique()))

# controller renewable share and total vs solved
for s in ["BAU", "NDCNEW", "LTSNEW"]:
    for y in [2030, 2035, 2050]:
        l = low[low.Scenario == s]
        tot = l[y].sum()
        ren = l[l.Is_Renewable == 1][y].sum()
        x = a[(a.Scenario == s) & (a.Year == y)]
        print(s, y, "controller lower total", round(tot, 3), "RE share of lower", round(ren / tot, 4),
              "| solved total", round(x.Value.sum(), 3))
        fos = l[l.Is_Renewable == 0][["Tech", y]].values.tolist()
        print("   controller fossil lower:", [(t, round(v, 3)) for t, v in fos],
              "solved fossil:", [(t, round(float(sol.get((s, t, y), 0)), 3)) for t, _ in fos])
