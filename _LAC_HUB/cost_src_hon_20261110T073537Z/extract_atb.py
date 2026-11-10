"""Extract the NREL ATB 2024 (v4.0.0) series used for plant cost paths: Moderate scenario, Market case, crpyears 30,
parameters OCC, CAPEX, Fixed O&M, Variable O&M; years 2022 to 2050. Writes atb2024_series.csv."""
import pandas as pd
from pathlib import Path
HERE = Path(__file__).parent
SEL = [("UtilityPV", "Class1"), ("UtilityPV", "Class4"), ("ResPV", "Class1"), ("ResPV", "Class4"),
       ("LandbasedWind", "Class4"), ("LandbasedWind", "Class7"), ("LandbasedWind", "Class9"),
       ("Utility-Scale PV-Plus-Battery", "Class1"), ("Biopower", "Dedicated")]
keep = []
for c in pd.read_csv(HERE / "downloads" / "plant" / "ATBe_2024_v4.0.0.csv", chunksize=500000, low_memory=False):
    c = c[(c.scenario == "Moderate") & (c.core_metric_case == "Market") & (c.crpyears.astype(str) == "30")
          & (c.core_metric_parameter.isin(["OCC", "CAPEX", "Fixed O&M", "Variable O&M"]))]
    c = c[[ (t, d) in SEL for t, d in zip(c.technology, c.techdetail)]]
    keep.append(c)
d = pd.concat(keep)
# values identical across tax_credit_case for these parameters; keep one and check
chk = d.groupby(["technology", "techdetail", "core_metric_parameter", "core_metric_variable"]).value.nunique()
print("max distinct values across tax credit cases:", chk.max())
d = d.drop_duplicates(["technology", "techdetail", "core_metric_parameter", "core_metric_variable"])
d = d[["technology", "techdetail", "core_metric_parameter", "core_metric_variable", "units", "value"]].rename(columns={"core_metric_variable": "year"})
d["value"] = d["value"].astype(float); d["year"] = d["year"].astype(int)
d.sort_values(["technology", "techdetail", "core_metric_parameter", "year"]).to_csv(HERE / "atb2024_series.csv", index=False)
d["value"] = d["value"].astype(float); d["year"] = d["year"].astype(int)
p = d.pivot_table(index=["technology", "techdetail", "core_metric_parameter"], columns="year", values="value")
print(p[[2022, 2024, 2030, 2040, 2050]].round(2).to_string())
