"""Honduras: compare solved plant activity (stage3 TotalTechnologyAnnualActivity) with
(a) the compiled activity limits in HON_ENERGY/B1_Output_Params and
(b) the Stage 2 controller lower limits (_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx, CURRENT_LOWER).
Read-only.

Usage: python -I check_solved_vs_inputs.py <model_root> <out_csv>
Tolerance: 1e-3 PJ absolute and 0.5 percent relative.
"""
import csv
import os
import sys

import pandas as pd

ROOT, OUT = sys.argv[1], sys.argv[2]
C = "Honduras"
P = os.path.join(ROOT, C, "HON_ENERGY", "B1_Output_Params")
XL = os.path.join(ROOT, "_STAGE3_RESULTS", "stage3_results.xlsx")
CTL = os.path.join(ROOT, "_STAGE2_OUTPUT", "CONTROLLER_NEW_SCENARIOS.xlsx")
SCEN = ["BAU", "NDCNEW", "LTSNEW"]
YEARS = list(range(2025, 2051))


def limits(scen, name):
    df = pd.read_csv(os.path.join(P, scen, name + ".csv"))
    df = df[df["TECHNOLOGY"].astype(str).str.match(r"^(PP|IMP_ELE)")]
    return {(r.TECHNOLOGY, int(r.YEAR)): float(r.Value) for r in df.itertuples()}


act = pd.read_excel(XL, sheet_name="TotalTechnologyAnnualActivity", engine="openpyxl")
a = act[act.Country == C]
sol = a.groupby(["Scenario", "Technology", "Year"]).Value.sum().to_dict()

rows = []
count = {}
for s in SCEN:
    lo = limits(s, "TotalTechnologyAnnualActivityLowerLimit")
    up = limits(s, "TotalTechnologyAnnualActivityUpperLimit")
    techs = sorted({k[0] for k in list(lo) + list(up)})
    for t in techs:
        for y in YEARS:
            v = float(sol.get((s, t, y), 0.0))
            l = lo.get((t, y))
            u = up.get((t, y))
            kind = ""
            if l is not None and v < l - max(1e-3, 0.005 * abs(l)):
                kind = "below compiled lower limit"
            if u is not None and v > u + max(1e-3, 0.005 * abs(u)):
                kind = "above compiled upper limit"
            if kind:
                rows.append(["compiled", s, t, y, round(v, 4), "" if l is None else round(l, 4),
                             "" if u is None else round(u, 4), kind])
                count[("compiled", s)] = count.get(("compiled", s), 0) + 1

low = pd.read_excel(CTL, sheet_name="CURRENT_LOWER", engine="openpyxl")
low = low[low.Country == C]
print("controller columns:", list(low.columns)[:12])
for r in low.itertuples(index=False):
    d = r._asdict()
    s, t = d["Scenario"], d["Tech"]
    sub = low[(low.Scenario == s) & (low.Tech == t)]
    for y in YEARS:
        lov = float(sub[y].iloc[0])
        v = float(sol.get((s, t, y), 0.0))
        upv = lov * 1.05 if lov > 0 else None
        kind = ""
        if v < lov - max(1e-3, 0.005 * lov):
            kind = "below controller lower"
        elif upv is not None and v > upv + max(1e-3, 0.005 * upv):
            kind = "above controller lower x 1.05"
        if kind:
            rows.append(["controller", s, t, y, round(v, 4), round(lov, 4),
                         "" if upv is None else round(upv, 4), kind])
            count[("controller", s)] = count.get(("controller", s), 0) + 1

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["reference", "scenario", "technology", "year", "solved_PJ", "lower_PJ", "upper_PJ", "finding"])
    w.writerows(rows)
print("violations by reference and scenario:", count)

# examples and renewable share of the compiled and controller lower limits
REN = {"PPBGS", "PPBIM", "PPGEO", "PPHDAM", "PPHROR", "PPPVD", "PPPVDS", "PPPVT", "PPPVT2",
       "PPPVTS", "PPWNDON", "PPWNDS"}
for s in SCEN:
    lo = limits(s, "TotalTechnologyAnnualActivityLowerLimit")
    for y in [2030, 2035, 2050]:
        tot = sum(v for (t, yy), v in lo.items() if yy == y and t.startswith("PP"))
        ren = sum(v for (t, yy), v in lo.items() if yy == y and t in REN)
        l2 = low[low.Scenario == s]
        ctot = l2[y].sum()
        cren = l2[l2.Is_Renewable == 1][y].sum()
        print(s, y, "compiled lower total", round(tot, 3), "RE share", round(ren / tot, 4) if tot else None,
              "| controller lower total", round(ctot, 3), "RE share", round(cren / ctot, 4) if ctot else None)
for s in ["NDCNEW", "LTSNEW", "BAU"]:
    lo = limits(s, "TotalTechnologyAnnualActivityLowerLimit")
    up = limits(s, "TotalTechnologyAnnualActivityUpperLimit")
    for t in ["PPFOI", "PPCOK", "PPPVT", "PPWNDON", "PPHDAM", "PPNGS", "IMP_ELE"]:
        for y in [2030, 2035, 2050]:
            print("EX", s, t, y, "solved", round(float(sol.get((s, t, y), 0.0)), 4),
                  "compiled lower", lo.get((t, y)), "upper", up.get((t, y)))
