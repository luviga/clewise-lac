"""Model quantities for the Guatemala alignment (read-only, model state 481a7c0).

Usage: python -I model_numbers.py <model_root> <job_folder>
Prints:
- renewable installed capacity 2025 and 2035 (from model_levers_GUA.csv, solved part)
- solved emissions by label per year (stage3 AnnualEmissions) and cumulative reductions
- solved renewable share of generation in 2032 (stage3 TotalTechnologyAnnualActivity, PP techs)
- electric share of car output in 2032 (stage3)
"""
import os
import sys

import pandas as pd

ROOT, JOB = sys.argv[1], sys.argv[2]
XL = os.path.join(ROOT, "_STAGE3_RESULTS", "stage3_results.xlsx")
REN = {"PPBGS", "PPBIM", "PPGEO", "PPHDAM", "PPHROR", "PPPVD", "PPPVDS", "PPPVT", "PPPVT2",
       "PPPVTS", "PPWNDON"}

lev = pd.read_csv(os.path.join(JOB, "model_levers_GUA.csv"))
cap = lev[(lev.part == "solved") & (lev.quantity == "installed capacity by plant type")]
for s in ["BAU", "NDCNEW", "LTSNEW"]:
    out = {}
    for y in [2025, 2030, 2035, 2050]:
        col = f"{s}_{y}"
        r = cap[cap.technology.isin(REN)][col].fillna(0).sum()
        f = cap[~cap.technology.isin(REN)][col].fillna(0).sum()
        out[y] = (round(r, 6), round(f, 6))
    print(s, "renewable GW, fossil GW:", out,
          "increase RE 2025-2035 MW:", round((out[2035][0] - out[2025][0]) * 1000, 1),
          "increase RE 2025-2030 MW:", round((out[2030][0] - out[2025][0]) * 1000, 1))

em = pd.read_excel(XL, sheet_name="AnnualEmissions", engine="openpyxl")
print("AnnualEmissions columns:", list(em.columns))
g = em[em.Country.astype(str) == "Guatemala"]
print("labels:", sorted(g.Emission.astype(str).unique()) if "Emission" in g.columns else "?")
piv = g.pivot_table(index=["Emission", "Year"], columns="Scenario", values="Value", aggfunc="sum")
for lab in ["CO2e_sources", "CO2e"]:
    p = piv.loc[lab]
    for y in [2025, 2030, 2032, 2035, 2050]:
        if y in p.index:
            b, n, l = p.loc[y, "BAU"], p.loc[y, "NDCNEW"], p.loc[y, "LTSNEW"]
            print(lab, y, "BAU", round(b, 4), "NDCNEW", round(n, 4), "LTSNEW", round(l, 4),
                  "red NDC %", round(100 * (1 - n / b), 3), "red LTS %", round(100 * (1 - l / b), 3))
    yrs = [y for y in p.index if 2019 <= y <= 2050]
    print(lab, "years", min(yrs), max(yrs), len(yrs))
    cum_n = sum(p.loc[y, "BAU"] - p.loc[y, "NDCNEW"] for y in yrs)
    cum_l = sum(p.loc[y, "BAU"] - p.loc[y, "LTSNEW"] for y in yrs)
    print(lab, "cumulative reduction 2019-2050 Mt: NDCNEW", round(cum_n, 3), "LTSNEW", round(cum_l, 3))
    y26 = [y for y in yrs if 2026 <= y <= 2035]
    print(lab, "cumulative reduction 2026-2035 Mt: NDCNEW",
          round(sum(p.loc[y, "BAU"] - p.loc[y, "NDCNEW"] for y in y26), 3),
          "LTSNEW", round(sum(p.loc[y, "BAU"] - p.loc[y, "LTSNEW"] for y in y26), 3))

act = pd.read_excel(XL, sheet_name="TotalTechnologyAnnualActivity", engine="openpyxl")
a = act[act.Country.astype(str) == "Guatemala"]
for y in [2030, 2032, 2035]:
    for s in ["BAU", "NDCNEW", "LTSNEW"]:
        x = a[(a.Scenario == s) & (a.Year == y)]
        pp = x[x.Technology.astype(str).str.startswith("PP")]
        tot = pp.Value.sum()
        ren = pp[pp.Technology.isin(REN)].Value.sum()
        aut = x[x.Technology.astype(str).str.match(r"^TRAUT")]
        ele = aut[aut.Technology == "TRAUTELE"].Value.sum()
        print(y, s, "RE share", round(ren / tot, 4), "gen PJ", round(tot, 3),
              "car electric share", round(ele / aut.Value.sum(), 4) if aut.Value.sum() else None)
