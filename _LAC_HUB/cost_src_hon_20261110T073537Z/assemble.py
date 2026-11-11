"""Step 8: write proposals.csv (the file LAC_COST_WRITE reads) and proposals_summary.csv
from fuel_prices.csv (fuel supply rows, three scenarios) and plant_costs.csv (plants and the electricity import row)."""
import csv, json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
BAU = HERE.parents[1] / "Honduras" / "HON_ENERGY" / "A2_Output_Params" / "BAU"
cr = pd.read_csv(HERE / "cost_rows_current.csv", keep_default_na=False)
meta = {(r.Tech, r.Parameter): (r.sheet, r._2) for r in cr.itertuples()}  # _2 = Tech.ID
cur = {}
for p in ["CapitalCost", "FixedCost", "VariableCost"]:
    for r in pd.read_csv(BAU / f"{p}.csv").itertuples():
        cur[(r.TECHNOLOGY, p, int(r.YEAR))] = float(r.Value)
UNIT = {"CapitalCost": "MUSD/GW (USD/kW)", "FixedCost": "MUSD/GW per year (USD/kW-yr)", "VariableCost": "MUSD/PJ (USD/GJ)"}
GAS = json.loads((HERE / "fuel_assumptions.txt").read_text(encoding="utf-8"))["GAS"]

out = []
fp = pd.read_csv(HERE / "fuel_prices.csv", keep_default_na=False)
for r in fp.itertuples():
    sheet, tid = meta[(r.row, "VariableCost")]
    c = cur.get((r.row, "VariableCost", r.year))
    out.append(dict(country="Honduras", sheet=sheet, **{"Tech.ID": tid}, Tech=r.row, Parameter="VariableCost", fuel_scenario=r.scenario,
                    year=r.year, current_value="" if c is None else round(c, 6), proposed_value=r.value_usd_per_gj, unit=UNIT["VariableCost"],
                    change_class="replace" if c is not None else "fill_empty", basis_class=r.case, source_ids=r.source_ids,
                    derivation=f"{r.chosen_point}; r {r.r} ({r.r_case}); benchmark {r.benchmark}; WEO series {r.weo_series}. {r.derivation}",
                    assumption_sentence=GAS if r.row == "DIST_NGS" else ""))
pc = pd.read_csv(HERE / "plant_costs.csv", keep_default_na=False)
for r in pc.itertuples():
    sheet, tid = meta[(r.technology, r.parameter)]
    out.append(dict(country="Honduras", sheet=sheet, **{"Tech.ID": tid}, Tech=r.technology, Parameter=r.parameter, fuel_scenario="ALL",
                    year=r.year, current_value=r.current_value, proposed_value=r.proposed_value, unit=UNIT[r.parameter],
                    change_class=r.change_class, basis_class=r.basis_class, source_ids=r.source_ids, derivation=r.derivation,
                    assumption_sentence=r.assumption_sentence))
cols = list(out[0].keys())
with open(HERE / "proposals.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)

d = pd.DataFrame(out)
summ = []
for (t, p), g in d.groupby(["Tech", "Parameter"], sort=False):
    base = g[g.fuel_scenario.isin(["ALL", "STEPS"])].set_index("year")
    def v(col, y, gg=base):
        if y not in gg.index: return ""
        x = gg.loc[y, col]
        return "" if x == "" else float(x)
    rec = dict(Tech=t, Parameter=p, unit=g.unit.iloc[0], scenario_shown="STEPS" if (g.fuel_scenario == "STEPS").any() else "ALL")
    for y in (2024, 2030, 2050):
        c, q = v("current_value", y), v("proposed_value", y)
        rec[f"current_{y}"] = "" if c == "" else round(c, 4)
        rec[f"proposed_{y}"] = "" if q == "" else round(q, 4)
        rec[f"change_pct_{y}"] = "" if (c == "" or q == "" or c == 0) else round(100 * (q / c - 1), 1)
    for sc in ("CPS", "NZE"):
        gs = g[g.fuel_scenario == sc].set_index("year")
        rec[f"proposed_2050_{sc}"] = "" if gs.empty else round(float(gs.loc[2050, "proposed_value"]), 4)
    rec["change_classes"] = ";".join(sorted(set(g.change_class)))
    rec["basis_classes"] = ";".join(sorted(set(g.basis_class)))
    summ.append(rec)
pd.DataFrame(summ).to_csv(HERE / "proposals_summary.csv", index=False)
print(len(out), "proposal rows;", d.groupby("basis_class").size().to_dict(), d.groupby("change_class").size().to_dict())
print(pd.DataFrame(summ)[["Tech", "Parameter", "current_2024", "proposed_2024", "change_pct_2024", "proposed_2050"]].to_string())
