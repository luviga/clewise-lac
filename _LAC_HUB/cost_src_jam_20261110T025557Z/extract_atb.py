"""Extract NREL ATB 2024 (v4.0.0) Moderate, Market case, 30-year cost recovery series used as plant cost leads and paths."""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).parent
d = pd.read_csv(HERE / "downloads" / "plant2" / "ATBe_2024_v4.0.0.csv", low_memory=False)
KEEP = [("UtilityPV", "Class1"), ("ResPV", "Class1"), ("LandbasedWind", "Class9"), ("LandbasedWind", "Class6"), ("Hydropower", "NPD1"),
        ("Hydropower", "NSD2"), ("Hydropower", "NSD3"), ("Geothermal", "HydroFlash"), ("Geothermal", "HydroBinary"), ("Biopower", "Dedicated"),
        ("NaturalGas_FE", "NG 2-on-1 Combined Cycle (F-Frame)"), ("NaturalGas_FE", "NG Combustion Turbine (F-Frame)"),
        ("Residential Battery Storage", None), ("Utility-Scale Battery Storage", "4Hr Battery Storage")]
m = d[(d.scenario == "Moderate") & (d.core_metric_case == "Market") & (d.crpyears == 30)
      & d.core_metric_parameter.isin(["CAPEX", "OCC", "Fixed O&M", "Variable O&M"])]
parts = []
for t, td in KEEP:
    x = m[(m.technology == t) & ((m.techdetail == td) if td else True)]
    x = x.sort_values("tax_credit_case").drop_duplicates(["techdetail", "core_metric_parameter", "core_metric_variable"])
    parts.append(x)
o = pd.concat(parts)[["technology", "techdetail", "core_metric_parameter", "core_metric_variable", "units", "value", "tax_credit_case"]]
o = o.rename(columns={"core_metric_variable": "year"}); o["year"] = pd.to_numeric(o.year, errors="coerce"); o["value"] = pd.to_numeric(o.value, errors="coerce"); o = o.dropna(subset=["year"]); o["year"] = o.year.astype(int)
o.to_csv(HERE / "atb2024_series.csv", index=False)
p = o.pivot_table(index=["technology", "techdetail", "core_metric_parameter"], columns="year", values="value")
print(p[[2022, 2023, 2024, 2025, 2030, 2040, 2050]].round(1).to_string())
