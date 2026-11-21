"""Extra Phase D check: every written cost cell reaches the recompiled A2 output.

For each write_set.csv cell, the A2 value of the same parameter, technology and year in
A2_Output_Params/{BAU,NDCNEW,LTSNEW} must equal the written value rounded to 4 decimals (A2 rounds
every Flat and User defined value with round(x, 4)). A zero written value may also be absent from the
output (A2 drops nothing, but OSeMOSYS reads a missing cost as 0). Writes compiled_check.csv.
"""
import csv
from pathlib import Path

import pandas as pd

ROOT = Path(r"C:\clw_fix")
JOB = ROOT / "_LAC_HUB" / "fix_run_20261111T200825Z"
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}

W = pd.read_csv(JOB / "write_set.csv", keep_default_na=False)
rows, bad = [], 0
for c, d in MODEL.items():
    for scen in ("BAU", "NDCNEW", "LTSNEW"):
        cache = {}
        for p in ("CapitalCost", "FixedCost", "VariableCost"):
            df = pd.read_csv(ROOT / d / "A2_Output_Params" / scen / f"{p}.csv")
            g = df.groupby(["TECHNOLOGY", "YEAR"])["Value"].apply(list).to_dict()
            cache[p] = g
        for w in W[W.country == c].itertuples():
            vals = cache[w.parameter].get((w.tech, int(w.year)))
            want = round(float(w.value_to_write), 4)
            if vals is None:
                ok = want == 0
                got = "absent"
            else:
                ok = all(abs(v - want) <= 1e-9 * max(1, abs(want)) for v in vals)
                got = ";".join(repr(v) for v in vals)
            bad += not ok
            if not ok:
                rows.append(dict(country=c, scenario=scen, sheet=w.sheet, tech=w.tech, parameter=w.parameter,
                                 year=w.year, written=w.value_to_write, expected_a2=want, a2=got))
with open(JOB / "compiled_check.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=["country", "scenario", "sheet", "tech", "parameter", "year", "written",
                                        "expected_a2", "a2"], lineterminator="\n")
    wr.writeheader()
    for r in rows:
        wr.writerow(r)
print("cells checked:", len(W) * 3, "mismatches:", bad)
