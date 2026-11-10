"""Step 3: list every CapitalCost/FixedCost/VariableCost row of Primary and Secondary Techs
with cached values, add scope, and recompute the section 5 table from the BAU CSVs."""
import openpyxl, csv, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from common import *
sys.stdout.reconfigure(encoding="utf-8")
wb = openpyxl.load_workbook(WB, data_only=True, read_only=True)
rows = []; years = None
for sn in ["Primary Techs", "Secondary Techs"]:
    ws = wb[sn]
    it = ws.iter_rows(values_only=True)
    hdr = list(next(it))
    yc = [i for i, h in enumerate(hdr) if isinstance(h, int)]
    if years is None: years = [hdr[i] for i in yc]
    assert [hdr[i] for i in yc] == years
    ref_i = hdr.index("Referencia") if "Referencia" in hdr else hdr.index("Reference")
    for r in it:
        if r[4] in COST_PARAMS:
            rows.append(dict(sheet=sn, **{"Tech.ID": r[0], "Tech": r[1], "Tech.Name": r[2],
                        "Parameter": r[4], "Unit": r[5], "Projection.Mode": r[6],
                        "Reference": r[ref_i], "Projection.Parameter": r[8]},
                        **{str(y): r[i] for y, i in zip(years, yc)}, scope=scope_of(r[1])))
cols = ["sheet","Tech.ID","Tech","Tech.Name","Parameter","Unit","Projection.Mode","Reference","Projection.Parameter"] + [str(y) for y in years] + ["scope"]
with open(os.path.join(JOB, "cost_rows_current.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print("rows", len(rows), "years", years[0], "-", years[-1])
print(pd.Series([r["scope"] for r in rows]).value_counts().to_dict())

# Section 5 recheck from BAU CSVs
def load(n):
    p = os.path.join(BAU, n + ".csv")
    d = pd.read_csv(p); return d
cc, fc, vc = load("CapitalCost"), load("FixedCost"), load("VariableCost")
rc, tmc, tmci = load("ResidualCapacity"), load("TotalAnnualMaxCapacity"), load("TotalAnnualMaxCapacityInvestment")
ul = load("TotalTechnologyAnnualActivityUpperLimit")
def v(d, t, y=2024):
    s = d[(d.TECHNOLOGY == t) & (d.YEAR == y)].Value
    return float(s.iloc[0]) if len(s) else None
out = []
for t in PLANTS + SUPPLY + IMPORT:
    resid = v(rc, t) or 0.0
    can = False
    for y in range(2025, 2051):
        m = v(tmc, t, y); r_ = v(rc, t, y) or 0.0
        room = (m is None) or (m > r_ + 1e-9)
        if room: can = True; break
    inv = tmci[tmci.TECHNOLOGY == t].Value
    if len(inv) and (inv == 0).all(): can = False
    ulv = ul[ul.TECHNOLOGY == t]
    out.append(dict(tech=t, resid2024=resid, can_build=can, CapitalCost=v(cc, t), FixedCost=v(fc, t),
                    VariableCost=v(vc, t), ActUpper2024=v(ul, t),
                    ActUpper_max=float(ulv.Value.max()) if len(ulv) else None,
                    TMC2030=v(tmc, t, 2030)))
o = pd.DataFrame(out)
o.to_csv(os.path.join(JOB, "section5_recheck.csv"), index=False)
print(o.to_string())
