"""Step 3: read CapitalCost, FixedCost and VariableCost rows from the Honduras A-O workbook (cached values),
and recompute the section 5 facts from the BAU compiled CSVs."""
import csv, openpyxl
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / "Honduras" / "HON_ENERGY"
AO = ROOT / "A1_Outputs" / "A-O_Parametrization.xlsx"
BAU = ROOT / "A2_Output_Params" / "BAU"
OUT = Path(__file__).parent
PLANTS = ["PPBIM","PPCOK","PPFOI","PPGEO","PPGTDSL","PPGTGLP","PPHDAM","PPHROR","PPICEDSL","PPPVD","PPPVT","PPWNDON"]
SUPPLY = ["DIST_COA","DIST_COK","DIST_DSL","DIST_FOI","DIST_GSL","DIST_KER","DIST_LPG","DIST_NGS"]
IMPORT = ["IMP_ELE"]
COSTS = {"CapitalCost","FixedCost","VariableCost"}
wb = openpyxl.load_workbook(AO, data_only=True, read_only=True)
allrows = []; other = []
for s in ["Primary Techs", "Secondary Techs"]:
    rows = list(wb[s].iter_rows(values_only=True))
    hdr = rows[0]
    ycols = [(i, int(h)) for i, h in enumerate(hdr) if isinstance(h, (int, float)) and 1900 < h < 2200]
    YEARS = [y for _, y in ycols]
    for r in rows[1:]:
        if r[1] is None: continue
        rec = dict(sheet=s, tech_id=r[0], tech=r[1], tech_name=r[2], parameter=r[4], unit=r[5],
                   mode=r[6], mode_param=r[7], values={y: r[i] for i, y in ycols})
        if rec["parameter"] in COSTS: allrows.append(rec)
        else: other.append(rec)
def scope(t):
    return "plant in scope" if t in PLANTS else "supply row" if t in SUPPLY else "electricity import" if t in IMPORT else "other"
with open(OUT / "cost_rows_current.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sheet","Tech.ID","Tech","Tech.Name","Parameter","Unit","Projection.Mode","Projection.Parameter","scope"] + YEARS)
    for r in allrows:
        w.writerow([r["sheet"], r["tech_id"], r["tech"], r["tech_name"], r["parameter"], r["unit"], r["mode"], r["mode_param"], scope(r["tech"])]
                   + ["" if r["values"].get(y) is None else r["values"][y] for y in YEARS])
with open(OUT / "capacity_rows_current.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sheet","Tech","Parameter","Unit","Projection.Mode","Projection.Parameter"] + YEARS)
    for r in other:
        if r["tech"] in PLANTS + IMPORT + SUPPLY and r["parameter"] in ("ResidualCapacity","TotalAnnualMaxCapacity","TotalAnnualMaxCapacityInvestment",
                "TotalTechnologyAnnualActivityLowerLimit","TotalTechnologyAnnualActivityUpperLimit"):
            w.writerow([r["sheet"], r["tech"], r["parameter"], r["unit"], r["mode"], r["mode_param"]] + ["" if r["values"].get(y) is None else r["values"][y] for y in YEARS])
# section 5 check from BAU CSVs
def bau(p):
    d = pd.read_csv(BAU / f"{p}.csv")
    return d
res = bau("ResidualCapacity"); mx = bau("TotalAnnualMaxCapacity"); mxi = bau("TotalAnnualMaxCapacityInvestment")
cc = bau("CapitalCost"); fc = bau("FixedCost"); vc = bau("VariableCost")
def v(d, t, y, mode=None):
    q = d[(d.TECHNOLOGY == t) & (d.YEAR == y)]
    return None if q.empty else round(float(q.Value.iloc[0]), 6)
lines = ["tech,residual_2024,can_build_more,capital_2024,fixed_2024,variable_2024"]
for t in PLANTS + SUPPLY + IMPORT:
    can = "no"
    rq = res[res.TECHNOLOGY == t].set_index("YEAR").Value
    mq = mx[mx.TECHNOLOGY == t].set_index("YEAR").Value
    iq = mxi[mxi.TECHNOLOGY == t].set_index("YEAR").Value
    room = any((mq.get(y, 1e9) > rq.get(y, 0) + 1e-9) for y in range(2025, 2051))
    inv_open = iq.empty or any(iq.get(y, 1) != 0 for y in range(2025, 2051))
    if room and inv_open: can = "yes"
    lines.append(f"{t},{v(res,t,2024)},{can},{v(cc,t,2024)},{v(fc,t,2024)},{v(vc,t,2024)}")
(OUT / "section5_check.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines)); print(YEARS[0], YEARS[-1], len(allrows))
