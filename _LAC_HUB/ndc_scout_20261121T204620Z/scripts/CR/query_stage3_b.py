"""Renewable share of generation for Costa Rica in given years, read-only. Usage: python -I query_stage3_b.py <stage3_results.xlsx>
Renewable plant types as in c1_model_levers.py notes: PWRBMS PWRGEO PWRHYDDAM PWRHYDROR PWRSPVTRN PWRWNONS."""
import sys

import pandas as pd

REN = {"PWRBMS", "PWRGEO", "PWRHYDDAM", "PWRHYDROR", "PWRSPVTRN", "PWRWNONS"}
p = pd.read_excel(sys.argv[1], sheet_name="ProductionByTechnologyAnnual")
p = p[(p["Country"] == "CostaRica") & p["Technology"].astype(str).str.startswith("PWR") & p["Fuel"].astype(str).str.contains("ELE")]
for y in [2021, 2024, 2025, 2027, 2030, 2035]:
    for s in ["BAU", "NDCNEW", "LTSNEW"]:
        d = p[(p["Year"] == y) & (p["Scenario"] == s)]
        tot = d["Value"].sum()
        ren = d[d["Technology"].isin(REN)]["Value"].sum()
        print(y, s, round(tot, 4), round(ren / tot, 6) if tot else None)
