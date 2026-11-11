"""Merge the fuel and plant search logs into search_log.csv; merge constants into constants.csv."""
import csv
from pathlib import Path
import pandas as pd
HERE = Path(__file__).parent
rows = []
f = pd.read_csv(HERE / "search_log_fuel.csv", keep_default_na=False, dtype=str)
rows += f.to_dict("records")
for p in ["downloads/plant/search_log_irena_iea.csv", "downloads/plant2/search_log_atb_jam.csv"]:
    d = pd.read_csv(HERE / p, keep_default_na=False, dtype=str)
    for r in d.itertuples(index=False):
        r = r._asdict()
        rows.append(dict(row=r.get("tech_or_row", ""), lead=r.get("lead", ""), url_or_query=r.get("url_or_query", ""), date=r.get("date", ""), result=r.get("result", "")))
extra = [
    ("PPPVDS;PPWNDONS", "IRENA Renewable Power Generation Costs in 2022 and in 2025: combined PV or wind with battery systems", "https://www.irena.org/Publications/2023/Aug/Renewable-Power-Generation-Costs-in-2022", "2026-11-10", "No combined system cost; IRENA 2022 has no battery cost; IRENA 2025 gives a stand-alone battery cost per kWh only."),
    ("PPPVDS;PPWNDONS", "IEA WEO 2023 Annex B Table B.4a and WEO 2025 Table B.4b", "https://www.iea.org/reports/world-energy-outlook-2023", "2026-11-10", "Battery storage per kWh and PV and wind separately; no combined system and no buildings PV with battery."),
    ("PPPVDS;PPWNDONS", "2018 Jamaica IRP and IRP-2 (2023)", "https://www.mset.gov.jm/wp-content/uploads/2020/03/2018-Jamaica-Integrated-Resource-Feb-21-2020.pdf", "2026-11-10", "Stand-alone transmission-sited BESS only (816 USD/kW, 50 USD/kW-yr, 2018 USD, 15-minute duration, PDF p.107); no combined plant."),
    ("PPPVDS;PPWNDONS", "NREL ATB 2024 (ATBe.csv v4.0.0)", "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2024/v4.0.0/ATBe.csv", "2026-11-10", "Utility-scale PV-plus-battery exists; no residential PV-plus-battery and no wind-plus-battery. Stand-alone residential and utility battery rows exist."),
    ("PPHDAM;PPGEO", "Variable O&M for dam hydro and geothermal", "ATBe.csv v4.0.0 (Variable O&M rows); 2018 IRP Appendix C", "2026-11-10", "ATB 2024 has no Variable O&M rows for Hydropower or Geothermal; the IRP has no dam hydro or geothermal candidates. Empty cells proposed at 0 with an ASSUMPTION sentence."),
]
for r in extra:
    rows.append(dict(zip(["row", "lead", "url_or_query", "date", "result"], r)))
with open(HERE / "search_log.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["row", "lead", "url_or_query", "date", "result"]); w.writeheader(); w.writerows(rows)
c = pd.read_csv(HERE / "fuel_constants.csv", dtype=str, keep_default_na=False)
c = pd.concat([c, pd.DataFrame([dict(name="CPIU_2021_PER_2022", value=None, unit="ratio", source_id="CSJ-006", page_or_table="series CUUR0000SA0", derivation="CPIU_2021 / CPIU_2022, used to express ATB 2022 USD in 2021 USD")])])
fc = pd.read_csv(HERE / "fuel_constants.csv").set_index("name")
c.loc[c.name == "CPIU_2021_PER_2022", "value"] = round(float(fc.loc["CPIU_2021", "value"]) / float(fc.loc["CPIU_2022", "value"]), 6)
plant_consts = [("GJ_PER_MWH", 3.6, "GJ per MWh", "GEN-003", "Appendix B.8 (1 kWh = 3.6 MJ)", "exact"),
                ("MONTHS_PER_YEAR", 12, "months per year", "GEN-003", "definition", "USD/kW-month x 12 = USD/kW-yr")]
c = pd.concat([c, pd.DataFrame(plant_consts, columns=["name", "value", "unit", "source_id", "page_or_table", "derivation"])])
c.to_csv(HERE / "constants.csv", index=False)
print(len(rows), "search log rows;", len(c), "constants")
