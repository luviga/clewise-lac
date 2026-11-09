"""Append World Bank CMO October 2026 short-term forecasts (nominal USD), transcribed from the downloaded PDF page 1 (report page 12),
to projections.csv as a separate block. Values checked against downloads/CMO-October-2026-Forecasts.pdf."""
import sys, os, pandas as pd
OUT = sys.argv[1]
URL = "https://thedocs.worldbank.org/en/doc/2ac43f46629cf90c2ea5b8929a343593-0050012026/related/CMO-October-2026-Forecasts.pdf"
vals = {("Brent spot", "nominal USD/bbl"): {2024: 80.7, 2025: 69.0, 2026: 91.0, 2027: 79.0, 2028: 70.0},
        ("Henry Hub spot (Natural gas, United States)", "nominal USD/MMBtu"): {2024: 2.2, 2025: 3.5, 2026: 3.5, 2027: 3.7, 2028: 3.9},
        ("Coal, Australia (fob Newcastle)", "nominal USD/t"): {2024: 136.1, 2025: 108.4, 2026: 135.0, 2027: 130.0, 2028: 125.0},
        ("Liquefied natural gas, Japan", "nominal USD/MMBtu"): {2024: 12.8, 2025: 12.0, 2026: 20.0, 2027: 18.0, 2028: 13.0}}
rows = []
for (drv, unit), d in vals.items():
    for y, v in d.items():
        rows.append(dict(case="WB_baseline", aeo_case="World Bank CMO baseline forecast (2024-2025 actual)", publisher="World Bank",
                         edition="Commodity Markets Outlook, October 2026", table="Commodity price forecasts, report page 12",
                         row_key="", driver=drv, year=y, value=v, unit=unit, basis="nominal", source_url=URL))
p = pd.read_csv(os.path.join(OUT, "projections.csv"))
p = p[p.case != "WB_baseline"]
pd.concat([p, pd.DataFrame(rows)]).to_csv(os.path.join(OUT, "projections.csv"), index=False)
print(len(rows), "rows appended")
