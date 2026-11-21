"""Model quantities for the Honduras alignment (read-only, model state 481a7c0).

Usage: python -I model_numbers.py <model_root> <job_folder>
Prints the numbers used in alignment_HON.csv. Nothing is written.
"""
import os
import sys

import pandas as pd

ROOT, JOB = sys.argv[1], sys.argv[2]
XL = os.path.join(ROOT, "_STAGE3_RESULTS", "stage3_results.xlsx")
B1 = os.path.join(ROOT, "Honduras", "HON_ENERGY", "B1_Output_Params")
REN = {"PPBGS", "PPBIM", "PPGEO", "PPHDAM", "PPHROR", "PPPVD", "PPPVDS", "PPPVT", "PPPVT2",
       "PPPVTS", "PPWNDON", "PPWNDS"}
SC = ["BAU", "NDCNEW", "LTSNEW"]
C = "Honduras"

# ---------------- capacity (solved) ----------------
cap = pd.read_excel(XL, sheet_name="TotalCapacityAnnual", engine="openpyxl")
cap = cap[(cap.Country == C) & cap.Technology.astype(str).str.startswith("PP")]
for s in SC:
    x = cap[cap.Scenario == s]
    out = {}
    for y in [2025, 2026, 2030, 2035, 2050]:
        z = x[x.Year == y]
        out[y] = (round(z[z.Technology.isin(REN)].Value.sum() * 1000, 1),
                  round(z[~z.Technology.isin(REN)].Value.sum() * 1000, 1))
    print("CAP MW (ren, fossil)", s, out,
          "| RE incr 2025-2035", round(out[2035][0] - out[2025][0], 1),
          "| RE incr 2026-2035", round(out[2035][0] - out[2026][0], 1),
          "| fossil change 2025-2035", round(out[2035][1] - out[2025][1], 1))
    for t in ["PPNGS", "PPCOK", "PPFOI", "PPICEDSL", "PPGTDSL", "PPGTGLP", "PPCOA"]:
        print("   ", s, t, [round(x[(x.Technology == t) & (x.Year == y)].Value.sum() * 1000, 1)
                            for y in [2025, 2029, 2030, 2035, 2050]])

newcap = pd.read_excel(XL, sheet_name="NewCapacity", engine="openpyxl")
newcap = newcap[(newcap.Country == C) & newcap.Technology.astype(str).str.startswith("PP")]
for s in SC:
    x = newcap[(newcap.Scenario == s) & (newcap.Year >= 2026) & (newcap.Year <= 2035)]
    print("NEWCAP 2026-2035 MW", s, "ren", round(x[x.Technology.isin(REN)].Value.sum() * 1000, 1),
          "fossil", round(x[~x.Technology.isin(REN)].Value.sum() * 1000, 1),
          x.groupby("Technology").Value.sum().mul(1000).round(1).to_dict())

# ---------------- generation (solved) ----------------
act = pd.read_excel(XL, sheet_name="TotalTechnologyAnnualActivity", engine="openpyxl")
a = act[act.Country == C]
for s in SC:
    for y in [2025, 2030, 2031, 2035]:
        x = a[(a.Scenario == s) & (a.Year == y)]
        pp = x[x.Technology.astype(str).str.startswith("PP")]
        tot = pp.Value.sum()
        ren = pp[pp.Technology.isin(REN)].Value.sum()
        imp = x[x.Technology == "IMP_ELE"].Value.sum()
        print("GEN", s, y, "total PJ", round(tot, 4), "RE share", round(ren / tot, 4),
              "imports PJ", round(imp, 4))

# ---------------- road transport (solved activity) ----------------
groups = {"AUT": "TRAUT", "SUV": "TRSUV", "MOT": "TRMOT", "TAX": "TRTAX", "BPU": "TRBPU",
          "MBS": "TRMBS", "BTUR": "TRBTUR", "YLF": "TRYLF", "YTK": "TRYTK"}
tr = a[a.Technology.astype(str).str.match(r"^TR(AUT|SUV|MOT|TAX|BPU|MBS|BTUR|YLF|YTK)")]
print("transport techs:", sorted(tr.Technology.unique()))
for s in SC:
    for y in [2025, 2030, 2035]:
        x = tr[(tr.Scenario == s) & (tr.Year == y)]
        line = []
        tot_all = 0.0
        ele_all = 0.0
        for g, p in groups.items():
            z = x[x.Technology.astype(str).str.startswith(p)]
            t = z.Value.sum()
            e = z[z.Technology.astype(str).str.endswith("ELE")].Value.sum()
            h = z[z.Technology.astype(str).str.match(r".*(HG|HD|PHG)$")].Value.sum()
            tot_all += t
            ele_all += e
            line.append(f"{g}: ele {e / t:.4f} hyb {h / t:.4f}" if t else f"{g}: 0")
        print("ROAD", s, y, "; ".join(line), "| all groups ele", round(ele_all / tot_all, 4))

# ---------------- emissions (solved) ----------------
em = pd.read_excel(XL, sheet_name="AnnualEmissions", engine="openpyxl")
g = em[em.Country == C]
piv = g.pivot_table(index=["Emission", "Year"], columns="Scenario", values="Value", aggfunc="sum")
for lab in ["CO2e_sources", "CO2e_PP", "CO2_PP"]:
    p = piv.loc[lab]
    for y in [2025, 2030, 2035, 2050]:
        b, n, l = p.loc[y, "BAU"], p.loc[y, "NDCNEW"], p.loc[y, "LTSNEW"]
        print(lab, y, "BAU", round(b, 4), "NDCNEW", round(n, 4), "LTSNEW", round(l, 4),
              "red NDC %", round(100 * (1 - n / b), 3), "red LTS %", round(100 * (1 - l / b), 3))
    for s in SC:
        print(lab, s, "change vs own 2025 in 2030 %", round(100 * (p.loc[2030, s] / p.loc[2025, s] - 1), 2),
              "in 2035 %", round(100 * (p.loc[2035, s] / p.loc[2025, s] - 1), 2))
    for a0, a1 in [(2021, 2030), (2021, 2035)]:
        yrs = range(a0, a1 + 1)
        print(lab, f"cumulative reduction {a0}-{a1} Mt: NDCNEW",
              round(sum(p.loc[y, "BAU"] - p.loc[y, "NDCNEW"] for y in yrs), 4),
              "LTSNEW", round(sum(p.loc[y, "BAU"] - p.loc[y, "LTSNEW"] for y in yrs), 4))
print("CO2e_sources BAU 2018-2024:", [round(piv.loc["CO2e_sources"].loc[y, "BAU"], 4) for y in range(2018, 2025)])

# ---------------- compiled demand ----------------
for s in SC:
    d = pd.read_csv(os.path.join(B1, s, "SpecifiedAnnualDemand.csv"))
    d = d.set_index(["FUEL", "YEAR"]).Value
    for y in [2018, 2022, 2025, 2030, 2035]:
        tot = 0.0
        ele = 0.0
        for f, v in d.xs(y, level="YEAR").items():
            if str(f)[:5] in ("E5RES", "E5COM", "E5IND"):
                tot += v
                if str(f).endswith("ELE"):
                    ele += v
        print("DEMAND", s, y, "RES+COM+IND total PJ", round(tot, 4), "electric share", round(ele / tot, 4),
              "| E5RESFIR", round(d.get(("E5RESFIR", y), float("nan")), 4),
              "| E5EXPLPG", round(d.get(("E5EXPLPG", y), float("nan")), 4))

# ---------------- transport fuel and ethanol ----------------
prod = pd.read_excel(XL, sheet_name="ProductionByTechnologyAnnual", engine="openpyxl")
pr = prod[prod.Country == C]
t4 = pr[pr.Technology.astype(str).str.startswith("T4")]
print("T4 techs:", sorted(t4.Technology.unique()))
for s in SC:
    for y in [2030, 2035]:
        x = t4[(t4.Scenario == s) & (t4.Year == y)]
        tot = x.Value.sum()
        gsl = x[x.Technology.astype(str).str.startswith("T4GSL")].Value.sum()
        print("TRANSPORT FUEL", s, y, "T4 total PJ", round(tot, 4), "gasoline PJ", round(gsl, 4),
              "ethanol share of transport energy at 4.99/5 pct blend",
              round((0.0499 if y == 2030 else 0.05) * gsl / tot, 4))
