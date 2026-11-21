"""Model numbers for the Jamaica alignment (read-only on the model worktree).

Usage: python -I model_numbers.py <model_root> <out_txt>

Writes plain text with:
  1. solved generation, capacity and renewable share by year for PP techs
  2. emissions by label (never summed) and BAU-relative reductions
  3. electric share of road transport fuel delivered (E5TRO*)
  4. compiled B1_Output_Params plant limits versus solved activity versus Stage 2 controller
  5. grid loss factor (ELE_DIST InputActivityRatio)
"""
import os
import sys

import pandas as pd

ROOT, OUT = sys.argv[1], sys.argv[2]
XL = os.path.join(ROOT, "_STAGE3_RESULTS", "stage3_results.xlsx")
CTL = os.path.join(ROOT, "_STAGE2_OUTPUT", "CONTROLLER_NEW_SCENARIOS.xlsx")
B1 = os.path.join(ROOT, "Jamaica", "JAM_ENERGY", "B1_Output_Params")
SCEN = ["BAU", "NDCNEW", "LTSNEW"]
REN = ["PPBIM", "PPBGS", "PPGEO", "PPHDAM", "PPHROR", "PPPVT", "PPPVD", "PPPVDS", "PPPVTS",
       "PPWNDON", "PPWNDONS", "PPWNDOFF"]
YRS = [2025, 2027, 2028, 2030, 2032, 2035, 2037, 2040, 2045, 2050]

lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


act = pd.read_excel(XL, sheet_name="TotalTechnologyAnnualActivity", engine="openpyxl")
act = act[act.Country == "Jamaica"]
cap = pd.read_excel(XL, sheet_name="TotalCapacityAnnual", engine="openpyxl")
cap = cap[cap.Country == "Jamaica"]
emi = pd.read_excel(XL, sheet_name="AnnualEmissions", engine="openpyxl")
emi = emi[emi.Country == "Jamaica"]
prod = pd.read_excel(XL, sheet_name="ProductionByTechnologyAnnual", engine="openpyxl")
prod = prod[prod.Country == "Jamaica"]

pp = act[act.Technology.astype(str).str.startswith("PP")]
A = pp.groupby(["Scenario", "Technology", "Year"]).Value.sum()
C = cap[cap.Technology.astype(str).str.startswith("PP")].groupby(["Scenario", "Technology", "Year"]).Value.sum()

p("## 1. Solved generation (PJ), capacity (GW), renewable share")
for s in SCEN:
    for y in YRS:
        g = {t: float(A.get((s, t, y), 0.0)) for t in sorted(set(pp.Technology))}
        tot = sum(g.values())
        ren = sum(v for t, v in g.items() if t in REN)
        c = {t: float(C.get((s, t, y), 0.0)) for t in sorted(set(pp.Technology))}
        p(s, y, "total_gen_PJ", round(tot, 4), "GWh", round(tot / 0.0036, 1), "RE_share", round(ren / tot, 4) if tot else None)
        p("   gen", {t: round(v, 4) for t, v in g.items() if abs(v) > 1e-6})
        p("   cap_GW", {t: round(v, 4) for t, v in c.items() if abs(v) > 1e-6})
        p("   solar_MW", round(1000 * c.get("PPPVT", 0), 1), "wind_MW", round(1000 * c.get("PPWNDON", 0), 1),
          "hydro_MW", round(1000 * (c.get("PPHDAM", 0) + c.get("PPHROR", 0)), 1),
          "fossil_gen_PJ", round(sum(v for t, v in g.items() if t not in REN), 4))
    sto = cap[(cap.Scenario == s) & (cap.Technology == "STOELE")]
    p("   STOELE capacity GW by year", {int(r.Year): round(r.Value, 4) for r in sto.itertuples() if r.Year in YRS})

p("")
p("## 2. Emissions by label (model unit, Mt CO2e assumed) - never summed")
E = emi.groupby(["Scenario", "Emission", "Year"]).Value.sum()
labels = sorted(set(emi.Emission))
p("labels:", labels)
for lab in labels:
    for s in SCEN:
        p(lab, s, {y: round(float(E.get((s, lab, y), 0.0)), 5) for y in [2025, 2030, 2035, 2040, 2045, 2050]})
for lab in ["CO2e_sources", "CO2e_PP", "CO2e_DETRN", "CO2e_CEM"]:
    for s in ["NDCNEW", "LTSNEW"]:
        red = {}
        for y in [2030, 2035, 2040, 2050]:
            b = float(E.get(("BAU", lab, y), 0.0))
            v = float(E.get((s, lab, y), 0.0))
            red[y] = (round(100 * (b - v) / b, 3) if b else None, round(b - v, 5))
        p("reduction vs BAU (percent, absolute)", lab, s, red)
for s in SCEN:
    cum = sum(float(E.get((s, "CO2e_sources", y), 0.0)) for y in range(2026, 2036))
    p("cumulative CO2e_sources 2026-2035", s, round(cum, 4))

p("")
p("## 3. Road transport fuel delivered (E5TRO*) and electric share")
tro = prod[prod.Fuel.astype(str).str.startswith("E5TRO")]
T = tro.groupby(["Scenario", "Fuel", "Year"]).Value.sum()
for s in SCEN:
    for y in [2025, 2030, 2035, 2040, 2050]:
        f = {fu: round(float(T.get((s, fu, y), 0.0)), 4) for fu in sorted(set(tro.Fuel))}
        tot = sum(f.values())
        p(s, y, f, "ELE share", round(f.get("E5TROELE", 0) / tot, 4) if tot else None)

p("")
p("## 4. Compiled limits (B1_Output_Params) vs solved vs Stage 2 controller (PP techs)")
low_c = pd.read_excel(CTL, sheet_name="CURRENT_LOWER", engine="openpyxl")
low_c = low_c[low_c.Country == "Jamaica"]
viol = {}
detail = []
for s in SCEN:
    lo = pd.read_csv(os.path.join(B1, s, "TotalTechnologyAnnualActivityLowerLimit.csv"))
    up = pd.read_csv(os.path.join(B1, s, "TotalTechnologyAnnualActivityUpperLimit.csv"))
    lo = lo[lo.TECHNOLOGY.astype(str).str.startswith("PP")].set_index(["TECHNOLOGY", "YEAR"]).Value
    up = up[up.TECHNOLOGY.astype(str).str.startswith("PP")].set_index(["TECHNOLOGY", "YEAR"]).Value
    techs = sorted(set(t for t, _ in lo.index) | set(t for t, _ in up.index))
    for t in techs:
        for y in range(2025, 2051):
            v = float(A.get((s, t, y), 0.0))
            l = lo.get((t, y))
            u = up.get((t, y))
            if l is not None and v < float(l) - max(1e-3, 0.005 * float(l)):
                viol[(s, "below compiled lower")] = viol.get((s, "below compiled lower"), 0) + 1
                detail.append((s, t, y, round(v, 4), round(float(l), 4), None if u is None else round(float(u), 4), "below compiled lower"))
            if u is not None and v > float(u) + max(1e-3, 0.005 * float(u)):
                viol[(s, "above compiled upper")] = viol.get((s, "above compiled upper"), 0) + 1
                detail.append((s, t, y, round(v, 4), None if l is None else round(float(l), 4), round(float(u), 4), "above compiled upper"))
    # implied renewable share of compiled lower limits
    for y in [2030, 2035, 2050]:
        ls = {t: float(lo.get((t, y), 0.0)) for t in techs}
        tot = sum(ls.values())
        ren = sum(v for t, v in ls.items() if t in REN)
        p(s, y, "compiled lower-limit total", round(tot, 3), "RE share of compiled lowers", round(ren / tot, 4) if tot else None)
    # controller check
    cl = low_c[low_c.Scenario == s]
    for y in [2030, 2035, 2050]:
        tot = cl[y].sum()
        ren = cl[cl.Is_Renewable == 1][y].sum()
        p(s, y, "controller lower total", round(tot, 3), "controller RE share", round(ren / tot, 4))
    cv = 0
    for r in cl.itertuples(index=False):
        d = r._asdict()
        t = d["Tech"]
        for y in range(2025, 2051):
            key = [k for k in d.keys() if str(k).strip("_") == str(y)]
            lov = float(d[key[0]]) if key else float(cl.loc[cl.Tech == t, y].iloc[0])
            v = float(A.get((s, t, y), 0.0))
            if v < lov - max(1e-3, 0.005 * lov) or (lov > 0 and v > 1.05 * lov + max(1e-3, 0.005 * lov)):
                cv += 1
    p(s, "technology-years outside controller lower..lower x 1.05:", cv)
p("violations of compiled limits (count):", viol)
for d in detail:
    if d[2] in (2025, 2027, 2030, 2035, 2040, 2050):
        p("   ", d)

p("")
p("## 5. Grid losses: ELE_DIST InputActivityRatio")
for s in SCEN:
    iar = pd.read_csv(os.path.join(B1, s, "InputActivityRatio.csv"))
    iar = iar[iar.TECHNOLOGY.isin(["ELE_DIST", "ELE_TRANS"])]
    for t in ["ELE_TRANS", "ELE_DIST"]:
        x = iar[iar.TECHNOLOGY == t].set_index("YEAR").Value
        p(s, t, {y: float(x.get(y)) for y in [2025, 2030, 2035, 2050] if y in x.index})
for s in SCEN:
    for y in [2030, 2035]:
        a_in = float(act[(act.Scenario == s) & (act.Technology == "ELE_DIST") & (act.Year == y)].Value.sum())
        p(s, y, "ELE_DIST activity (output) PJ", round(a_in, 4))

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
print("written", OUT)
