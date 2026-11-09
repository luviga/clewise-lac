"""Step 3: extract driver projections as published from EIA AEO2025 tables 12, 13, 15 (Reference, High Oil Price, Low Oil Price).
Writes projections.csv (as published) and projections_usd_per_gj.csv (converted, real 2024 USD).
Run: py -I projections.py <output_folder>
"""
import sys, os
import pandas as pd

OUT = sys.argv[1]
DL = os.path.join(OUT, "downloads", "aeo2025")
CASES = {"ref": ("REF", "Reference (ref2025)", "https://www.eia.gov/outlooks/archive/aeo25/excel/aeotab{t}.xlsx"),
         "highprice": ("HIGH", "High Oil Price (highprice)", "https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/highprice/aeotab{t}.xlsx"),
         "lowprice": ("LOW", "Low Oil Price (lowprice)", "https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/lowprice/aeotab{t}.xlsx")}
# (table, row key in column 0, driver name, unit, basis)
ITEMS = [
    ("12", "PPP000:ba_WorldOilPrice", "Brent spot", "2024 USD/bbl", "real 2024"),
    ("12", "PPP000:nom_WorldOilPric", "Brent spot", "nominal USD/bbl", "nominal"),
    ("13", "NGS000:ia_HenryHub", "Henry Hub spot", "2024 USD/MMBtu", "real 2024"),
    ("13", "NGS000:nom_HenryHub", "Henry Hub spot", "nominal USD/MMBtu", "nominal"),
    ("15", "CSD000:ja_Exports", "US coal exports, free alongside ship at US port of exit", "2024 USD/short ton", "real 2024"),
    ("15", "CSD000:nom_Exports", "US coal exports, free alongside ship at US port of exit", "nominal USD/short ton", "nominal"),
    ("12", "PPP000:ha_ResidualFuel(", "US residual fuel oil, electric power sector delivered", "2024 USD/bbl", "real 2024"),
]
rows = []
for c, (case, cname, urlt) in CASES.items():
    for t, key, name, unit, basis in ITEMS:
        d = pd.read_excel(os.path.join(DL, f"{c}_aeotab{t}.xlsx"), header=None)
        hdr = [i for i in range(len(d)) if str(d.iloc[i, 1]).strip() in ("Sector and Fuel", "Supply, Disposition, and Prices", "Supply, Disposition, and Prices ") or d.iloc[i, 2] == 2024][0]
        years = d.iloc[hdr, :].tolist()
        r = [i for i in range(len(d)) if str(d.iloc[i, 0]).startswith(key)][0]
        for j, y in enumerate(years):
            try:
                yi = int(float(y))
            except (TypeError, ValueError):
                continue
            if 2024 <= yi <= 2050:
                rows.append(dict(case=case, aeo_case=cname, publisher="U.S. Energy Information Administration",
                                 edition="Annual Energy Outlook 2025 (released April 15, 2025)", table=f"Table {t}",
                                 row_key=str(d.iloc[r, 0]), driver=name, year=yi, value=float(d.iloc[r, j]),
                                 unit=unit, basis=basis, source_url=urlt.format(t=t)))
p = pd.DataFrame(rows)
p.to_csv(os.path.join(OUT, "projections.csv"), index=False)

# converted, real 2024 USD per GJ
conv = {"Brent spot": (7.32 / 42.3, "x 7.32 bbl/t / 42.3 GJ/t"),
        "Henry Hub spot": (1 / 1.055056, "/ 1.055056 GJ/MMBtu, gross basis"),
        "US coal exports, free alongside ship at US port of exit": (None, "not converted: heat content of exported coal not given in Table 15")}
r = p[(p.basis == "real 2024") & p.driver.isin(["Brent spot", "Henry Hub spot"])].copy()
r["usd2024_per_gj"] = [v * conv[d][0] for v, d in zip(r.value, r.driver)]
r["conversion"] = [conv[d][1] for d in r.driver]
r[["case", "driver", "year", "value", "unit", "usd2024_per_gj", "conversion"]].to_csv(os.path.join(OUT, "projections_usd_per_gj.csv"), index=False)
piv = p[p.basis == "real 2024"].pivot_table(index="year", columns=["driver", "case"], values="value")
print(piv.loc[[2024, 2025, 2026, 2030, 2035, 2040, 2045, 2050]].round(2).to_string())
