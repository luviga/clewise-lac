"""Step 8: proposals.csv (the only file LAC_COST_WRITE reads) and proposals_summary.csv.

change_class: keep (proposed equals current within 2 percent), upgrade (newer edition), replace,
fill_placeholder (current 0 replaced by a sourced value), fill_empty (the workbook cell is empty today; the
current value shown is the BAU compiled value produced by the row's projection mode). Extra columns after
assumption_sentence: projection_mode, workbook_cell, needs_user_defined_mode (yes when the proposal varies
by year or fills empty cells while the row's projection mode is not User defined).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

YEARS = list(range(2018, 2051))
cur = pd.read_csv(os.path.join(JOB, "cost_rows_current.csv"))
vc_bau = pd.read_csv(os.path.join(BAU, "VariableCost.csv"))
FP = pd.read_csv(os.path.join(JOB, "fuel_prices.csv"))
PC = pd.read_csv(os.path.join(JOB, "plant_costs.csv"))

def meta(tech, par):
    r = cur[(cur.Tech == tech) & (cur.Parameter == par)].iloc[0]
    return r
def close(a, b): return abs(a - b) <= 0.02 * abs(b) if b else abs(a) < 1e-9

out = []
for tech, g in FP.groupby("row", sort=False):
    m = meta(tech, "VariableCost")
    for r in g.itertuples():
        cv = vc_bau[(vc_bau.TECHNOLOGY == tech) & (vc_bau.YEAR == r.year)].Value
        curv = float(cv.iloc[0]) if len(cv) else 0.0
        wc = m[str(r.year)]
        empty = pd.isna(wc)
        if empty: ch = "fill_empty"
        elif curv == 0: ch = "fill_placeholder"
        elif close(r.value_usd_per_gj, curv): ch = "keep"
        else: ch = "replace"
        out.append(dict(country="DominicanRepublic", sheet=m["sheet"], **{"Tech.ID": int(m["Tech.ID"]), "Tech": tech},
                        Parameter="VariableCost", fuel_scenario=r.scenario, year=r.year, current_value=round(curv, 6),
                        proposed_value=round(r.value_usd_per_gj, 6), unit="MUSD/PJ (USD/GJ), net calorific basis, real 2024 USD",
                        change_class=ch, basis_class=r.case, source_ids=r.source_ids, derivation=r.derivation,
                        assumption_sentence=("" if pd.isna(r.assumption_sentence) else r.assumption_sentence),
                        projection_mode=m["Projection.Mode"], workbook_cell=("" if empty else wc),
                        needs_user_defined_mode=("yes" if m["Projection.Mode"] != "User defined" else "no")))
for (tech, par), g in PC.groupby(["technology", "parameter"], sort=False):
    m = meta(tech, par)
    varies = g.proposed_value.nunique() > 1
    for r in g.itertuples():
        wc = m[str(r.year)]; empty = pd.isna(wc)
        ch = r.change_class
        if empty and ch in ("keep", "replace", "upgrade", "fill_placeholder"): ch = "fill_empty"
        needs = "yes" if (m["Projection.Mode"] != "User defined" and (varies or g.workbook_cell.isna().any() or (g.workbook_cell.astype(str) == "").any())) else "no"
        out.append(dict(country="DominicanRepublic", sheet=m["sheet"], **{"Tech.ID": int(m["Tech.ID"]), "Tech": tech},
                        Parameter=par, fuel_scenario="ALL", year=r.year, current_value=r.current_value,
                        proposed_value=r.proposed_value, unit=r.unit, change_class=ch, basis_class=r.p2_class,
                        source_ids=r.source_ids, derivation=r.derivation,
                        assumption_sentence=("" if pd.isna(r.assumption_sentence) else r.assumption_sentence),
                        projection_mode=m["Projection.Mode"], workbook_cell=("" if empty else wc), needs_user_defined_mode=needs))
P = pd.DataFrame(out)
P.to_csv(os.path.join(JOB, "proposals.csv"), index=False)

summ = []
for (tech, par, sc), g in P.groupby(["Tech", "Parameter", "fuel_scenario"], sort=False):
    g = g.set_index("year")
    def pct(y):
        c, p = g.current_value[y], g.proposed_value[y]
        return round((p / c - 1) * 100, 2) if c else ""
    summ.append(dict(Tech=tech, Parameter=par, fuel_scenario=sc,
                     current_2024=g.current_value[2024], proposed_2024=g.proposed_value[2024], change_pct_2024=pct(2024),
                     current_2030=g.current_value[2030], proposed_2030=g.proposed_value[2030], change_pct_2030=pct(2030),
                     current_2050=g.current_value[2050], proposed_2050=g.proposed_value[2050], change_pct_2050=pct(2050),
                     basis_classes=";".join(sorted(g.basis_class.unique())), change_classes=";".join(sorted(g.change_class.unique()))))
S = pd.DataFrame(summ); S.to_csv(os.path.join(JOB, "proposals_summary.csv"), index=False)
print("proposals rows", len(P)); print(P.change_class.value_counts().to_dict()); print(P.basis_class.value_counts().to_dict())
print("techs", P.Tech.nunique())
