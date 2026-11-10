"""Step 6: electricity import row IMP_ELE (rule E1). Appends its rows to plant_costs.csv.

Years with a positive activity lower limit: 2018 to 2024. The price is the average cost of ENEE's purchases in the
regional electricity market (MER), contract plus spot, energy plus capacity charges, summed over 12 months from the
CREE quarterly tariff reports (cree_mer_monthly.csv, parse_cree_mer.py). Both VariableCost and FixedCost carry the
price in the workbook, so the price goes to VariableCost and FixedCost is proposed at 0 (brief, section 5).
The 99999 years from 2025 are left as they are (not proposed).
"""
import csv, json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
BAU = HERE.parents[1] / "Honduras" / "HON_ENERGY" / "A2_Output_Params" / "BAU"
FILE2SID = {
    "cree_Informe-de-1er-Ajuste-Tarifario-2024_Final.pdf": "HON-009", "cree_Informe-de-2do-Ajuste-Tarifario-2024.pdf": "HON-010",
    "cree_Informe-de-3er-Ajuste-Tarifario-2024.pdf": "HON-011", "cree_Informe-de-4to-Ajuste-Tarifario-2024_VF.pdf": "HON-012",
    "cree_Informe-de-1er-Ajuste-Tarifario-2025.pdf": "HON-013", "cree_Informe-de-2do-Ajuste-Tarifario-2025.pdf": "HON-014",
    "cree_Informe-de-Ajuste-Tarifario-Abr-Jun-2022.pdf": "CSH-020", "cree_Informe-de-Ajuste-Tarifario-Jul-Sep-2022.pdf": "CSH-021",
    "cree_Informe-de-Ajuste-Tarifario-Oct-Dic-2022-.pdf": "CSH-022", "cree_Informe-de-1er-Ajuste-Tarifario-2023_CREE_F.pdf": "CSH-023",
    "cree_Informe-de-2do-Ajuste-Tarifario-2023.pdf": "CSH-024", "cree_Informe-de-3er-Ajuste-Tarifario-2023-Final.pdf": "CSH-025",
    "cree_Informe-de-4to-Ajuste-Tarifario-2023-Final.pdf": "CSH-026",
}
fc = pd.read_csv(HERE / "fuel_constants.csv").set_index("name")
CPI = {y: float(fc.loc[f"CPIU_{y}", "value"]) for y in range(2018, 2026)}
m = pd.read_csv(HERE / "cree_mer_monthly.csv")
obs = {}
for y, g in m.groupby("year"):
    if g.month.nunique() == 12 and len(g) == 24:
        usd, gwh = g.total_usd.sum(), g.gwh.sum()
        sids = ";".join(sorted({FILE2SID[f] for f in g.file}))
        nominal = usd / gwh / 1000
        obs[y] = dict(nominal=nominal, real=nominal * CPI[2024] / CPI[y], usd=usd, gwh=gwh, sids=sids)
cur = {}
for p in ["FixedCost", "VariableCost"]:
    for r in pd.read_csv(BAU / f"{p}.csv").itertuples():
        if r.TECHNOLOGY == "IMP_ELE":
            cur[(p, int(r.YEAR))] = float(r.Value)
P24 = obs[2024]["real"] / 3.6
lo = min(o["real"] for o in obs.values()) / 3.6; hi = max(o["real"] for o in obs.values()) / 3.6
SENT = (f"ASSUMPTION: the price of electricity imported by Honduras from the regional electricity market in 2018 to 2021 is {P24:.2f} USD/GJ "
        f"({obs[2024]['real']:.2f} USD/MWh, real 2024 USD), the 2024 average price of ENEE's contract and spot purchases including capacity charges. "
        f"Reason: the price paid stayed between {obs[2024]['real']:.0f} and {max(o['real'] for o in obs.values()):.0f} USD/MWh in real 2024 USD over 2022 to 2024, "
        f"most of it under contracts priced near 120 to 124 USD/MWh, so the 2024 level stands for the earlier years. "
        f"Check: the December 2021 average of the same purchases was 113.2 USD/MWh nominal (CREE), and the 2022 and 2023 averages were "
        f"{obs[2022]['real']:.1f} and {obs[2023]['real']:.1f} USD/MWh in real 2024 USD. Range: {lo:.1f} to {hi:.1f} USD/GJ.")
rows = []
for y in range(2018, 2025):
    for p in ["VariableCost", "FixedCost"]:
        c = cur.get((p, y))
        rec = dict(technology="IMP_ELE", parameter=p, year=y, current_value="" if c is None else c)
        if p == "FixedCost":
            sid = obs[2024]["sids"]
            rec.update(proposed_value=0.0, p2_class="replace", change_class="replace", basis_class="replace", source_ids=sid,
                       derivation="Both FixedCost and VariableCost carry the import price in the workbook; the price paid per MWh, capacity charges included, goes to VariableCost and FixedCost is set to 0",
                       assumption_sentence="")
        elif y in obs:
            o = obs[y]
            rec.update(proposed_value=round(o["real"] / 3.6, 4), p2_class="replace", change_class="replace", basis_class="observed",
                       source_ids=o["sids"] + ";CSH-005",
                       derivation=(f"CREE Informe de Ajuste Tarifario, Tabla 'Costos reales de generacion', rows MER under Contratos and Oportunidad, 12 months of {y}: "
                                   f"{o['usd']:,.2f} USD / {o['gwh']:.2f} GWh = {o['nominal']:.3f} USD/MWh nominal; x CPIU_2024 {CPI[2024]} / CPIU_{y} {CPI[y]} "
                                   f"= {o['real']:.3f} USD/MWh; / 3.6 = {o['real']/3.6:.4f} USD/GJ"),
                       assumption_sentence="")
        else:
            rec.update(proposed_value=round(P24, 4), p2_class="ASSUMPTION", change_class="replace", basis_class="ASSUMPTION",
                       source_ids=obs[2024]["sids"] + ";" + obs[2023]["sids"] + ";" + obs[2022]["sids"] + ";CSH-005",
                       derivation=f"2024 price held for {y}: {P24:.4f} USD/GJ", assumption_sentence=SENT)
        rows.append(rec)
pc = pd.read_csv(HERE / "plant_costs.csv", keep_default_na=False)
pc = pc[pc.technology != "IMP_ELE"]
allrows = pc.to_dict("records") + rows
with open(HERE / "plant_costs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(pc.columns)); w.writeheader(); w.writerows(allrows)
for y, o in obs.items():
    print(y, round(o["gwh"], 2), round(o["usd"], 2), round(o["nominal"], 3), round(o["real"], 3), round(o["real"] / 3.6, 4), o["sids"])
print(SENT)
