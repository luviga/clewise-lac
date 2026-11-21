"""Read-only queries on stage3_results.xlsx for Costa Rica. Usage: python -I query_stage3.py <stage3_results.xlsx>"""
import sys

import pandas as pd

s3 = pd.read_excel(sys.argv[1], sheet_name=["TotalCapacityAnnual", "AnnualEmissions", "ProductionByTechnologyAnnual"])
cty = "CostaRica"
c = s3["TotalCapacityAnnual"]
c = c[c["Country"] == cty]
print("columns:", list(c.columns))
print("years:", sorted(c["Year"].unique())[:3], "...", sorted(c["Year"].unique())[-2:])
pw = c[c["Technology"].astype(str).str.startswith("PWR")]
print("plant techs in capacity:", sorted(pw["Technology"].unique()))
for t in ["PWRSPVDTR", "PWRSUG"]:
    d = pw[(pw["Technology"] == t) & pw["Year"].isin([2025, 2030, 2035, 2050])]
    print(t, d.groupby(["Scenario", "Year"])["Value"].sum().to_dict())
e = s3["AnnualEmissions"]
e = e[e["Country"] == cty]
for lab in ["BC_TRN", "CO2e_TRN", "CO2e_PWR", "CO2e_DE"]:
    d = e[(e["Emission"] == lab) & e["Year"].isin([2021, 2025, 2030, 2035, 2050])]
    print(lab, d.groupby(["Scenario", "Year"])["Value"].sum().round(6).to_dict())
p = s3["ProductionByTechnologyAnnual"]
p = p[p["Country"] == cty]
d = p[(p["Technology"].astype(str) == "PWRSUG")]
print("PWRSUG production rows:", len(d))
d = p[p["Technology"].astype(str).str.startswith("PWR") & p["Fuel"].astype(str).str.contains("ELE") & (p["Year"] == 2021)]
print("2021 generation by plant:", d.groupby(["Scenario", "Technology"])["Value"].sum().round(4).to_dict())
