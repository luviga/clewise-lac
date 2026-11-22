"""Phase 1, step 1.5: add phase2_scope to cost_inventory.csv and print the per-model summary.
phase2_scope:
  vehicle        Vehicle Techs row (energy model with vehicles, or JAM_TRANSPORT) with a non-zero cost,
                 of a technology that produces a 2030 fuel with two or more producers
  sector_choice  sector-model row of class choice with a non-zero value, not an energy-model copy
  energy_copy    sector-model row of class choice whose technology also exists in the same
                 country's energy model (plants, fuel supply, vehicles): already sourced or sourced
                 under `vehicle`, not sourced again
  (blank)        not sourced in Phase 2 (total_only, inactive, or zero)"""
import os, sys, csv
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS

inv = os.path.join(JOB, "cost_inventory.csv")
rows = list(csv.DictReader(open(inv, newline="", encoding="utf-8")))
cs = list(csv.DictReader(open(os.path.join(JOB, "choice_sets.csv"), newline="", encoding="utf-8")))
multi = defaultdict(set)
for r in cs:
    for t in r["producers"].split(";"):
        multi[r["model"]].add(t)
energy_techs = defaultdict(set)
for r in rows:
    if r["model"].upper().endswith("ENERGY"):
        energy_techs[r["country"]].add(r["tech"])
# energy techs from the energy model's compiled BAU (all sheets, not only vehicles)
for m in MODELS:
    if m["kind"] == "energy":
        p = os.path.join(ROOT, m["bau"], "OutputActivityRatio.csv")
        for r in csv.DictReader(open(p, newline="", encoding="utf-8-sig")):
            energy_techs[m["cc"]].add(r["TECHNOLOGY"])
VEHM = {"CR_ENERGY", "RD_ENERGY", "GUA_ENERGY", "HON_ENERGY", "JAM_TRANSPORT"}
for r in rows:
    s = ""
    nz = r["any_nonzero"] == "yes"
    if r["sheet"] == "Vehicle Techs" and r["model"] in VEHM and nz and r["tech"] in multi[r["model"]]:
        s = "vehicle"
    elif r["model"] not in VEHM and not r["model"].upper().endswith("ENERGY") and r["class"] == "choice" and nz:
        s = "energy_copy" if r["tech"] in energy_techs[r["country"]] else "sector_choice"
    elif r["model"] == "JAM_TRANSPORT" and r["class"] == "choice" and nz:
        s = "sector_choice"
    r["phase2_scope"] = s
fields = [k for k in rows[0].keys() if k != "phase2_scope"] + ["phase2_scope"]
with open(inv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader(); w.writerows(rows)

print("model | rows | nonzero choice | nonzero total_only | nonzero inactive | zero rows | choice techs | vehicle pairs | sector pairs | energy_copy pairs")
tot = Counter()
for m in MODELS:
    g = [r for r in rows if r["model"] == m["model"]]
    nz = [r for r in g if r["any_nonzero"] == "yes"]
    c = Counter(r["class"] for r in nz)
    ch_t = len({r["tech"] for r in nz if r["class"] == "choice"})
    vp = len({(r["tech"], r["parameter"]) for r in g if r["phase2_scope"] == "vehicle"})
    sp = len({(r["tech"], r["parameter"]) for r in g if r["phase2_scope"] == "sector_choice"})
    ep = len({(r["tech"], r["parameter"]) for r in g if r["phase2_scope"] == "energy_copy"})
    line = (m["model"], len(g), c["choice"], c["total_only"], c["inactive"], len(g) - len(nz), ch_t, vp, sp, ep)
    for k, v in zip(["rows", "ch", "to", "in", "zero", "cht", "vp", "sp", "ep"], line[1:]):
        tot[k] += v
    print(" | ".join(str(x) for x in line))
print("TOTAL", dict(tot))
print(Counter(r["phase2_scope"] for r in rows))
