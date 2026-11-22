"""Phase 1, step 1.3: recompute vehicle CapitalCost (M US$/Gvkm) from the A-O inputs and compare
with the compiled BAU CapitalCost; list the chain inputs (distance, OperationalLife, battery rows).
Writes vehicle_chain_check.csv and vehicle_chain_inputs.csv."""
import os, sys, csv, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS
import openpyxl

VEH = ["CR_ENERGY", "RD_ENERGY", "GUA_ENERGY", "HON_ENERGY", "JAM_TRANSPORT"]
TRAJ = "User defined trajectory relative to BY"


def sheet_rows(path, name):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    hdr = list(next(it))
    return hdr, [list(r) for r in it if r and any(v is not None for v in r)]


def compiled(folder, param):
    out = {}
    p = os.path.join(ROOT, folder, param + ".csv")
    with open(p, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[(r["TECHNOLOGY"], int(float(r["YEAR"])))] = float(r["Value"])
    return out


checks, inputs = [], []
for m in [x for x in MODELS if x["model"] in VEH]:
    base = os.path.join(ROOT, m["folder"])
    hdr, rows = sheet_rows(os.path.join(ROOT, m["ao"]), "Vehicle Techs")
    H = {h: i for i, h in enumerate(hdr)}
    years = [h for h in hdr if isinstance(h, int)]
    y0 = years[0]
    cap = {r[H["Tech"]]: r for r in rows if r[H["Parameter"]] == "CapitalCost"}
    dist = pickle.load(open(os.path.join(base, "A1_Outputs", "A-O_Fleet_Groups_Distance.pickle"), "rb"))
    groups = pickle.load(open(os.path.join(base, "A1_Outputs", "A-O_Fleet_Groups.pickle"), "rb"))
    comp = compiled(m["bau"], "CapitalCost")
    compF = compiled(m["bau"], "FixedCost")
    # demand Ref.km.BY per group
    dh, drows = sheet_rows(os.path.join(base, "A1_Outputs", "A-O_Demand.xlsx"),
                           openpyxl.load_workbook(os.path.join(base, "A1_Outputs", "A-O_Demand.xlsx"), read_only=True).sheetnames[0])
    DH = {h: i for i, h in enumerate(dh)}
    refkm = {r[DH["Fuel/Tech"]]: r[DH["Ref.km.BY"]] for r in drows}
    # Fixed Horizon OperationalLife
    fh, frows = sheet_rows(os.path.join(ROOT, m["ao"]), "Fixed Horizon Parameters")
    FH = {h: i for i, h in enumerate(fh)}
    oplife = {r[FH["Tech"]]: (r[FH["Value"]], r[FH["Source / Assumption"]] if "Source / Assumption" in FH and FH["Source / Assumption"] < len(r) else "")
              for r in frows if r[FH["Parameter"]] == "OperationalLife"}
    # battery replacement
    bp = os.path.join(base, "A2_Extra_Inputs", "A-Xtra_Battery_Replacement.xlsx")
    bh, brows = sheet_rows(bp, openpyxl.load_workbook(bp, read_only=True).sheetnames[0])
    tech2group = {t: g for g, ts in groups.items() for t in ts}

    def usd(tech, y):
        r = cap[tech]
        ui = str(r[H["Unit.Introduced"]] or "")
        mode = r[H["Projection.Mode"]]
        v = lambda yy: r[H[yy]] if r[H[yy]] is not None else float("nan")
        if "Relative" in ui:
            ref = ui.split(" ")[-1]
            refv = cap[ref][H[y0]]
            if mode == TRAJ:
                b = refv * v(y0)
                return b if y == y0 else b * v(y)
            return refv * v(y0)  # Flat
        if mode == TRAJ:
            return v(y0) if y == y0 else v(y0) * v(y)
        if mode == "Flat":
            return v(y0)
        return v(y)

    for t, r in cap.items():
        ui = str(r[H["Unit.Introduced"]] or "")
        if t not in dist:
            continue
        for y in (2024, 2030, 2050):
            if y not in years:
                continue
            u = usd(t, y)
            km = dist[t][years.index(y)]
            conv = ("vehicle" in ui or "Relative" in ui) and "Gvkm" in str(r[H["Unit"]] or "")
            calc = (round(1000 * u / km, 4) if km else float("nan")) if conv else round(u, 4)
            c = comp.get((t, y))
            checks.append(dict(model=m["model"], tech=t, year=y, unit_introduced=ui,
                               projection_mode=r[H["Projection.Mode"]], usd_per_vehicle=round(u, 4),
                               km_per_vehicle_year=km, recomputed_MUSD_per_Gvkm=calc,
                               compiled_bau=c if c is not None else "",
                               match="yes" if (c is not None and abs(calc - c) <= 1e-3 * max(1, abs(c))) else ("no compiled value" if c is None else "no")))
    for t in sorted(tech2group):
        g = tech2group[t]
        km = dist.get(t)
        b = [x for x in brows if x[0] == t]
        inputs.append(dict(model=m["model"], tech=t, group=g, input="distance per vehicle (Ref.km.BY of group)",
                           unit="km per vehicle per year", value_base_year=refkm.get(g, ""),
                           value_2030=km[years.index(2030)] if km else "", value_2050=km[years.index(2050)] if km else "",
                           where="A-O_Demand.xlsx column Ref.km.BY; yearly change from A-Xtra_Projections.xlsx Variation_km_Passenger or Variation_km_Freight",
                           used_by_compiler="yes", note=""))
        ol = oplife.get(t)
        inputs.append(dict(model=m["model"], tech=t, group=g, input="OperationalLife", unit="years",
                           value_base_year=ol[0] if ol else "", value_2030="", value_2050="",
                           where="A-O_Parametrization.xlsx sheet Fixed Horizon Parameters", used_by_compiler="yes",
                           note=("source text: " + str(ol[1])) if ol and ol[1] else ""))
    bt = set()
    for x in brows:
        bt.add(x[0])
        inputs.append(dict(model=m["model"], tech=x[0], group=tech2group.get(x[0], "(not a model technology)"),
                           input="battery replacement row", unit="Lifetime yr; Replacements; CIF US$/vehicle; Battery.Per.CIF share",
                           value_base_year="Lifetime=%s; Hybrid.Factor=%s; Replacements=%s; CIF=%s; Battery.Per.CIF=%s" % tuple(x[i] for i in (2, 4, 5, 6, 7)),
                           value_2030="", value_2050="", where="A2_Extra_Inputs/A-Xtra_Battery_Replacement.xlsx",
                           used_by_compiler="no (read into a table and never used)", note=str(x[3] or "")))

for name, rows in (("vehicle_chain_check.csv", checks), ("vehicle_chain_inputs.csv", inputs)):
    with open(os.path.join(JOB, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter((c["model"], c["year"], c["match"]) for c in checks))
for c in checks:
    if c["match"] == "no":
        print("MISMATCH", c)
