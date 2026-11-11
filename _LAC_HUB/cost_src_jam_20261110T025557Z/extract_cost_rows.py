"""Step 3: read CapitalCost, FixedCost and VariableCost rows from the Jamaica A-O workbook (cached values)."""
import csv, openpyxl
from pathlib import Path
AO = Path(__file__).resolve().parents[2] / "Jamaica" / "JAM_ENERGY" / "A1_Outputs" / "A-O_Parametrization.xlsx"
OUT = Path(__file__).parent
PLANTS = ["PPBGS","PPBIM","PPDSL","PPFOI","PPGEO","PPHDAM","PPHROR","PPNGS","PPPVD","PPPVDS","PPPVT","PPWNDON","PPWNDONS"]
SUPPLY = ["DIST_COA","DIST_COK","DIST_DSL","DIST_FOI","DIST_GSL","DIST_JET","DIST_KER","DIST_LPG","DIST_NGS","DIST_OPE","EXTT_CRU"]
COSTS = {"CapitalCost","FixedCost","VariableCost"}
wb = openpyxl.load_workbook(AO, data_only=True, read_only=True)
allrows = []; years_by_sheet = {}; resid = {}
for s in ["Primary Techs", "Secondary Techs"]:
    rows = list(wb[s].iter_rows(values_only=True))
    hdr = rows[0]
    ycols = [(i, int(h)) for i, h in enumerate(hdr) if isinstance(h, (int, float)) and 1900 < h < 2200]
    years_by_sheet[s] = [y for _, y in ycols]
    for r in rows[1:]:
        if r[1] is None: continue
        rec = dict(sheet=s, tech_id=r[0], tech=r[1], tech_name=r[2], parameter=r[4], unit=r[5],
                   mode=r[6], mode_param=r[7], values={y: r[i] for i, y in ycols})
        if rec["parameter"] in COSTS: allrows.append(rec)
        if rec["parameter"] in ("ResidualCapacity", "TotalAnnualMaxCapacity", "TotalAnnualMaxCapacityInvestment"):
            resid[(rec["tech"], rec["parameter"])] = rec
allyears = sorted(set(y for v in years_by_sheet.values() for y in v))
def scope(tech):
    if tech in PLANTS: return "plant in scope"
    if tech in SUPPLY: return "supply row"
    if tech.startswith("ELE_IMP") or "IMP" in tech and tech.startswith("ELE"): return "electricity import"
    return "other"
with open(OUT / "cost_rows_current.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sheet","Tech.ID","Tech","Tech.Name","Parameter","Unit","Projection.Mode","Projection.Parameter","scope"] + allyears)
    for r in allrows:
        w.writerow([r["sheet"], r["tech_id"], r["tech"], r["tech_name"], r["parameter"], r["unit"], r["mode"], r["mode_param"], scope(r["tech"])]
                   + ["" if r["values"].get(y) is None else r["values"][y] for y in allyears])
with open(OUT / "capacity_rows_current.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sheet","Tech","Parameter","Unit","Projection.Mode","Projection.Parameter"] + allyears)
    for (t, p), r in sorted(resid.items()):
        if t in PLANTS:
            w.writerow([r["sheet"], t, p, r["unit"], r["mode"], r["mode_param"]] + ["" if r["values"].get(y) is None else r["values"][y] for y in allyears])
print({k: (v[0], v[-1], len(v)) for k, v in years_by_sheet.items()}, len(allrows))
