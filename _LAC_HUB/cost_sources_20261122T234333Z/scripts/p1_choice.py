"""Phase 1, step 1.2: choice sets from the compiled BAU files (2030) and a class for every
inventory row. Writes choice_sets.csv, tech_status.csv and adds `class` to cost_inventory.csv."""
import os, sys, csv
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS

Y = 2030
LIM = {
    "lower": "TotalTechnologyAnnualActivityLowerLimit",
    "upper": "TotalTechnologyAnnualActivityUpperLimit",
    "maxcap": "TotalAnnualMaxCapacity",
    "maxinv": "TotalAnnualMaxCapacityInvestment",
    "resid": "ResidualCapacity",
}
COSTP = ["CapitalCost", "FixedCost", "VariableCost"]


def read(folder, param):
    p = os.path.join(ROOT, folder, param + ".csv")
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def series(folder, param):
    d = defaultdict(dict)
    for r in read(folder, param):
        try:
            d[r["TECHNOLOGY"]][int(float(r["YEAR"]))] = float(r["Value"])
        except ValueError:
            pass
    return d


def possible(t, y, L):
    """False when the tech cannot operate in year y: capacity capped at zero, activity capped
    at zero, or no new capacity allowed and no residual capacity."""
    mc = L["maxcap"].get(t, {}).get(y)
    up = L["upper"].get(t, {}).get(y)
    mi = L["maxinv"].get(t, {}).get(y)
    rc = L["resid"].get(t, {}).get(y, 0.0)
    if mc is not None and mc == 0:
        return False
    if up is not None and up == 0:
        return False
    return True


def free(t, y, L):
    lo = L["lower"].get(t, {}).get(y)
    up = L["upper"].get(t, {}).get(y)
    if lo is not None and up is not None and abs(lo - up) <= 1e-9 * max(1.0, abs(up)):
        return False, "activity fixed (lower = upper)"
    if not possible(t, y, L):
        return False, "capacity or activity capped at zero"
    return True, ""


choice_rows, status_rows = [], []
tech_class = {}  # (model, tech) -> class
veh_count = {}
for m in MODELS:
    f = m["bau"]
    oar = read(f, "OutputActivityRatio")
    L = {k: series(f, v) for k, v in LIM.items()}
    costs = {p: series(f, p) for p in COSTP}
    prod_y = defaultdict(set)      # fuel -> techs in year Y
    out_years = defaultdict(set)   # tech -> years with output
    for r in oar:
        try:
            v = float(r["Value"]); y = int(float(r["YEAR"]))
        except ValueError:
            continue
        if v <= 0:
            continue
        out_years[r["TECHNOLOGY"]].add(y)
        if y == Y:
            prod_y[r["FUEL"]].add(r["TECHNOLOGY"])
    choice_free = set()
    for fuel, techs in sorted(prod_y.items()):
        if len(techs) < 2:
            continue
        fr = {}
        for t in sorted(techs):
            ok, why = free(t, Y, L)
            fr[t] = (ok, why)
        frees = [t for t in sorted(techs) if fr[t][0]]
        ch = len(frees) >= 2
        if ch:
            choice_free.update(frees)
        carry = {p: ";".join(t for t in frees if any(v != 0 for v in costs[p].get(t, {}).values())) for p in COSTP}
        pinned = []
        for t in frees:
            lo = L["lower"].get(t, {}).get(Y); mc = L["maxcap"].get(t, {}).get(Y)
            if lo and mc and abs(mc - lo) <= 0.01 * lo:
                pinned.append(t)
        choice_rows.append(dict(country=m["cc"], model=m["model"], fuel=fuel, year=Y,
                                producers=";".join(sorted(techs)), n_producers=len(techs),
                                free_producers=";".join(frees), n_free=len(frees), choice="yes" if ch else "no",
                                not_free_reasons=";".join("%s: %s" % (t, fr[t][1]) for t in sorted(techs) if not fr[t][0]),
                                free_with_CapitalCost=carry["CapitalCost"], free_with_FixedCost=carry["FixedCost"],
                                free_with_VariableCost=carry["VariableCost"],
                                free_but_capacity_equals_activity_lower_limit=";".join(pinned)))
    # classes per tech
    alltechs = set(out_years) | {t for p in COSTP for t in costs[p]}
    for t in sorted(alltechs):
        yrs = out_years.get(t, set())
        can = [y for y in yrs if possible(t, y, L)]
        if not yrs:
            lo_any = any(v > 0 for v in L["lower"].get(t, {}).values())
            cls = "total_only" if lo_any else "inactive"
            why = "no output fuel; " + ("activity lower limit > 0" if lo_any else "no forced activity")
        elif not can:
            cls, why = "inactive", "capacity or activity capped at zero in every year"
        elif t in choice_free:
            cls, why = "choice", "free producer in a %d choice set" % Y
        else:
            cls, why = "total_only", "not a free producer in any %d choice set" % Y
        tech_class[(m["model"], t)] = (cls, why)
        status_rows.append(dict(country=m["cc"], model=m["model"], tech=t, cls=cls, reason=why))
    # hub 12 style count for energy vehicles
    if m["kind"] == "energy" or m["model"] == "JAM_TRANSPORT":
        veh_count[m["model"]] = (sum(1 for fu, ts in prod_y.items() if len(ts) >= 2 and fu.startswith("E5")),
                                 sum(1 for r in choice_rows if r["model"] == m["model"] and r["choice"] == "yes" and r["fuel"].startswith("E5")),
                                 sum(1 for fu, ts in prod_y.items() if len(ts) >= 2))

with open(os.path.join(JOB, "choice_sets.csv"), "w", newline="", encoding="utf-8") as fo:
    w = csv.DictWriter(fo, fieldnames=list(choice_rows[0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(choice_rows)
with open(os.path.join(JOB, "tech_status.csv"), "w", newline="", encoding="utf-8") as fo:
    w = csv.DictWriter(fo, fieldnames=list(status_rows[0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(status_rows)

# add class to inventory
inv = os.path.join(JOB, "cost_inventory.csv")
with open(inv, newline="", encoding="utf-8") as fi:
    rows = list(csv.DictReader(fi))
for r in rows:
    if r["parameter"] == "EmissionsPenalty":
        continue
    c, why = tech_class.get((r["model"], r["tech"]), ("inactive", "technology not in the compiled BAU model"))
    r["class"] = c
    r["class_reason"] = why
fields = [k for k in rows[0].keys() if k not in ("class", "class_reason")] + ["class", "class_reason"]
with open(inv, "w", newline="", encoding="utf-8") as fo:
    w = csv.DictWriter(fo, fieldnames=fields, lineterminator="\n")
    w.writeheader(); w.writerows(rows)

print("choice sets:", sum(1 for r in choice_rows if r["choice"] == "yes"), "of", len(choice_rows), "multi-producer fuels")
for k, v in veh_count.items():
    print("  vehicles", k, "E5 fuels >=2 producers:", v[0], " E5 choice yes:", v[1], " all fuels >=2 producers:", v[2])
from collections import Counter
c = Counter((r["model"], r["class"], r["any_nonzero"]) for r in rows)
for k in sorted(c):
    print(" ", k, c[k])
