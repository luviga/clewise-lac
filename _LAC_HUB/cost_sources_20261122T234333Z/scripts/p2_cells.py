"""Phase 2 setup: one row per A-O cell that Phase 2 proposes against, per country (<CC>/cells_<CC>.csv).
Rows of phase2_scope vehicle or sector_choice; Flat rows give the base-year cell only; trajectory rows
give the base-year price and each multiplier cell; User defined rows give every year cell.
Vehicle chain inputs (Ref.km.BY per group, OperationalLife per vehicle) are added as cells too.
EmissionsPenalty rows (compiled, no A-O cell) are given per year from the compiled BAU file with
their input location."""
import os, sys, csv
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS
import openpyxl

MBY = {m["model"]: m for m in MODELS}
inv = list(csv.DictReader(open(os.path.join(JOB, "cost_inventory.csv"), newline="", encoding="utf-8")))
scope = [r for r in inv if r["phase2_scope"] in ("vehicle", "sector_choice")]
by_model = defaultdict(list)
for r in scope:
    by_model[r["model"]].append(r)

out = defaultdict(list)
for model, rows in by_model.items():
    m = MBY[model]
    pen = [r for r in rows if r["parameter"] == "EmissionsPenalty"]
    ao_rows = [r for r in rows if r["parameter"] != "EmissionsPenalty"]
    if ao_rows:
        wb = openpyxl.load_workbook(os.path.join(ROOT, m["ao"]), read_only=True, data_only=True)
        cache = {}
        for r in ao_rows:
            sh = r["sheet"]
            if sh not in cache:
                it = wb[sh].iter_rows(values_only=True)
                hdr = list(next(it))
                cache[sh] = (hdr, [None, None] + [list(x) for x in it])
            hdr, data = cache[sh]
            row = data[int(r["ao_row"])]
            H = {h: i for i, h in enumerate(hdr) if h is not None}
            years = [h for h in hdr if isinstance(h, int)]
            mode = r["projection_mode"]
            if mode == "Flat":
                yrs = [years[0]]
                kind = "base-year cell (Flat: every year takes this cell)"
            elif mode == "User defined trajectory relative to BY":
                yrs = [y for y in years if row[H[y]] is not None]
                kind = "base-year price, later years multipliers on it"
            else:
                yrs = [y for y in years if row[H[y]] is not None]
                kind = "year cell"
            for y in yrs:
                v = row[H[y]]
                out[m["cc"]].append(dict(country=m["cc"], model=model, sheet=sh, tech=r["tech"], tech_name=r["tech_name"],
                                         parameter=r["parameter"], unit_introduced=r["unit_introduced"], unit=r["unit"],
                                         projection_mode=mode, year=y, current_value=v,
                                         cell_meaning=("ratio to the reference vehicle's base-year price" if "Relative" in r["unit_introduced"] and y == years[0] else
                                                       ("multiplier on the base-year value" if mode == "User defined trajectory relative to BY" and y != years[0] else kind)),
                                         class_=r["class"], phase2_scope=r["phase2_scope"],
                                         ao_row_at_b51f24b="%s/A1_Outputs/A-O_Parametrization.xlsx, sheet %s, row %s, column %s" % (m["folder"], sh, r["ao_row"], y)))
    for r in pen:
        p = os.path.join(ROOT, m["bau"], "EmissionsPenalty.csv")
        for c in csv.DictReader(open(p, newline="", encoding="utf-8-sig")):
            if c["EMISSION"] == r["tech"]:
                out[m["cc"]].append(dict(country=m["cc"], model=model, sheet="EmissionsPenalty (" + r["sheet"].split("(", 1)[-1].rstrip(")") + ")",
                                         tech=r["tech"], tech_name=r["tech_name"], parameter="EmissionsPenalty",
                                         unit_introduced="", unit=r["unit"], projection_mode="per year", year=int(float(c["YEAR"])),
                                         current_value=float(c["Value"]), cell_meaning="penalty per unit of emission in that year",
                                         class_=r["class"], phase2_scope=r["phase2_scope"],
                                         ao_row_at_b51f24b="%s/B1_Scenario_Config.xlsx or A2_Extra_Inputs/A-Xtra_Emissions.xlsx; compiled %s/EmissionsPenalty.csv" % (m["folder"], m["bau"])))

# vehicle chain inputs
VEH = {"CR_ENERGY", "RD_ENERGY", "GUA_ENERGY", "HON_ENERGY", "JAM_TRANSPORT"}
vci = list(csv.DictReader(open(os.path.join(JOB, "vehicle_chain_inputs.csv"), newline="", encoding="utf-8")))
vtech = {(r["model"], r["tech"]) for r in scope if r["phase2_scope"] == "vehicle"}
seen = set()
for r in vci:
    m = MBY[r["model"]]
    if r["input"].startswith("distance"):
        if (r["model"], r["group"]) in seen or not any((r["model"], t) in vtech for t in [r["tech"]]):
            continue
        seen.add((r["model"], r["group"]))
        out[m["cc"]].append(dict(country=m["cc"], model=r["model"], sheet="A-O_Demand.xlsx (first sheet)", tech=r["group"],
                                 tech_name="vehicle group", parameter="Ref.km.BY", unit_introduced="km per vehicle per year",
                                 unit="km per vehicle per year", projection_mode="base year, changed yearly by A-Xtra_Projections.xlsx",
                                 year="BY", current_value=r["value_base_year"], cell_meaning="distance per vehicle per year in the base year",
                                 class_="chain input", phase2_scope="vehicle_chain",
                                 ao_row_at_b51f24b="%s/A1_Outputs/A-O_Demand.xlsx, row of %s, column Ref.km.BY" % (m["folder"], r["group"])))
    elif r["input"] == "OperationalLife" and (r["model"], r["tech"]) in vtech:
        out[m["cc"]].append(dict(country=m["cc"], model=r["model"], sheet="Fixed Horizon Parameters", tech=r["tech"],
                                 tech_name="", parameter="OperationalLife", unit_introduced="Years", unit="Years",
                                 projection_mode="fixed", year="", current_value=r["value_base_year"],
                                 cell_meaning="operational life", class_="chain input", phase2_scope="vehicle_chain",
                                 ao_row_at_b51f24b="%s/A1_Outputs/A-O_Parametrization.xlsx, sheet Fixed Horizon Parameters, row of %s OperationalLife" % (m["folder"], r["tech"])))

for cc, rows in out.items():
    os.makedirs(os.path.join(JOB, cc), exist_ok=True)
    with open(os.path.join(JOB, cc, "cells_%s.csv" % cc), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(cc, len(rows), dict(Counter((r["model"], r["phase2_scope"]) for r in rows)))
