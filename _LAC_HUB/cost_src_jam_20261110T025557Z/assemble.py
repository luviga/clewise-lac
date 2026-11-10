"""Step 8: write proposals.csv and proposals_summary.csv from fuel_prices.csv and plant_costs.csv."""
import csv, json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
YEARS = list(range(2021, 2056))
cur = pd.read_csv(HERE / "cost_rows_current.csv")
ycols = [str(y) for y in YEARS]

def effective(row):
    """Current value per year as the model uses it: Flat repeats the first year; Zero is 0; EMPTY is empty."""
    vals = {}
    mode = row["Projection.Mode"]
    first = row["2021"]
    for y in YEARS:
        v = row[str(y)]
        if mode == "Flat":
            v = first
        elif mode == "Zero":
            v = 0.0
        vals[y] = None if pd.isna(v) else float(v)
    return vals

def cur_row(tech, param):
    d = cur[(cur.Tech == tech) & (cur.Parameter == param)]
    assert len(d) == 1, (tech, param)
    return d.iloc[0]

UNITS = {"CapitalCost": "MUSD/GW", "FixedCost": "MUSD/GW per year", "VariableCost": "MUSD/PJ"}
props = []

def change_class(cv, pv, basis):
    if cv is None:
        return "fill_empty"
    if cv == 0 and pv != 0:
        return "fill_placeholder"
    if abs(pv - cv) <= 0.0005 * max(abs(cv), 1e-9) or round(pv, 4) == round(cv, 4):
        return "keep"
    if basis == "matched, newer edition":
        return "upgrade"
    return "replace"

# ---------------- fuel rows ----------------
fp = pd.read_csv(HERE / "fuel_prices.csv")
fa = json.load(open(HERE / "fuel_assumptions.txt", encoding="utf-8"))
for (row, sc), g in fp.groupby(["row", "scenario"]):
    cr = cur_row(row, "VariableCost"); eff = effective(cr)
    for r in g.itertuples():
        cv = eff[r.year]; pv = round(float(r.value_usd_per_gj), 4)
        sentence = ""
        sids = r.source_ids
        basis = r.case
        if row in ("DIST_KER", "DIST_JET") and (r.year == 2024 or r.case != "observed"):
            sentence = fa["ASSUME_KERJET"][row]
            if r.year == 2024:
                basis = "ASSUMPTION"
                sids = "CSJ-004;JAM-013;GEN-001;GEN-002"
        if row == "DIST_NGS":
            sentence = fa["GAS"]
        props.append(dict(country="Jamaica", sheet=cr.sheet, **{"Tech.ID": int(cr["Tech.ID"]), "Tech": row, "Parameter": "VariableCost"},
                          fuel_scenario=sc, year=r.year, current_value="" if cv is None else round(cv, 6), proposed_value=pv,
                          unit=UNITS["VariableCost"], change_class=change_class(cv, pv, basis), basis_class=basis,
                          source_ids=sids, derivation=r.derivation, assumption_sentence=sentence))

# ---------------- plant rows ----------------
pc = pd.read_csv(HERE / "plant_costs.csv", keep_default_na=False)
for r in pc.itertuples():
    cr = cur_row(r.technology, r.parameter)
    cv = None if r.current_value == "" else float(r.current_value)
    pv = None if r.proposed_value == "" else float(r.proposed_value)
    if pv is None:
        continue
    props.append(dict(country="Jamaica", sheet=cr.sheet, **{"Tech.ID": int(cr["Tech.ID"]), "Tech": r.technology, "Parameter": r.parameter},
                      fuel_scenario="ALL", year=int(r.year), current_value="" if cv is None else round(cv, 6), proposed_value=round(pv, 4),
                      unit=UNITS[r.parameter], change_class=r.change_class, basis_class=r.basis_class,
                      source_ids=r.source_ids, derivation=r.derivation, assumption_sentence=r.assumption_sentence))

import re
for p_ in props:
    p_["source_ids"] = ";".join(dict.fromkeys(re.findall(r"[A-Z]{2,4}-\d{3}", str(p_["source_ids"]))))
cols = ["country", "sheet", "Tech.ID", "Tech", "Parameter", "fuel_scenario", "year", "current_value", "proposed_value", "unit",
        "change_class", "basis_class", "source_ids", "derivation", "assumption_sentence"]
with open(HERE / "proposals.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(props)

# ---------------- summary ----------------
P = pd.DataFrame(props)
summ = []
for (tech, param, sc), g in P.groupby(["Tech", "Parameter", "fuel_scenario"]):
    rec = dict(technology=tech, parameter=param, fuel_scenario=sc)
    for y in (2024, 2030, 2050):
        x = g[g.year == y].iloc[0]
        c = x.current_value; p = x.proposed_value
        rec[f"current_{y}"] = c; rec[f"proposed_{y}"] = p
        rec[f"change_pct_{y}"] = "" if c in ("", None) or float(c) == 0 else round(100 * (float(p) / float(c) - 1), 1)
    rec["change_classes"] = ";".join(sorted(g.change_class.unique()))
    rec["basis_classes"] = ";".join(sorted(g.basis_class.unique()))
    summ.append(rec)
pd.DataFrame(summ).to_csv(HERE / "proposals_summary.csv", index=False)
print(len(props), "proposal rows;", len(summ), "summary rows")
print(P.groupby(["change_class"]).size()); print(P.groupby(["basis_class"]).size())
