"""Stream the FAOSTAT bulk zips and keep the six countries, years 2019-2023.

Writes raw subsets next to the zips in downloads/GEN_sector/ (gitignored).
"""
import os
import zipfile
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
DL = os.path.join(JOB, "downloads", "GEN_sector")
AREAS = {48: "CR", 56: "DR", 58: "ECU", 89: "GUA", 95: "HON", 109: "JAM"}
YEARS = range(2019, 2024)

BULKS = {
    "trade": "Trade_CropsLivestock_E_All_Data_(Normalized)",
    "prices": "Prices_E_All_Data_(Normalized)",
    "production": "Production_Crops_Livestock_E_All_Data_(Normalized)",
}

for key, stem in BULKS.items():
    out = os.path.join(DL, f"subset_{key}_6countries_2019_2023.csv")
    zp = os.path.join(DL, stem + ".zip")
    parts = []
    with zipfile.ZipFile(zp) as z:
        with z.open(stem + ".csv") as fh:
            for ch in pd.read_csv(fh, chunksize=2_000_000, encoding="latin-1", low_memory=False):
                ch = ch[ch["Area Code"].isin(AREAS) & ch["Year"].isin(YEARS)]
                if len(ch):
                    parts.append(ch)
    df = pd.concat(parts)
    df.to_csv(out, index=False, lineterminator="\n")
    print(key, len(df), sorted(df["Element"].unique()))
