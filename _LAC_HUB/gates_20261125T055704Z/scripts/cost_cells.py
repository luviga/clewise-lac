"""Count, per model and policy scenario, the cost cells (CapitalCost, FixedCost, VariableCost) that are 0 in the base
scenario and non-zero in the policy scenario, in the compiled data files (b1 point), and whether R5 of the run on
main flagged each of those parameters and technologies. Writes cost_cells.csv in the job folder.
Usage: py -I cost_cells.py <gate_results.csv of the b1 run>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import sys
from collections import defaultdict

ROOT, JOB = M.ROOT, M.JOB
sys.path.insert(0, str(ROOT))
from gates import gmpl  # noqa: E402

COST = ("CapitalCost", "FixedCost", "VariableCost")
flag = defaultdict(set)
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    if r["check"] == "R5":
        flag[(r["model"], r["scenario"], r["parameter"])].add(r["technology"])
out = []
for m in csv.DictReader(open(ROOT / "config" / "gates" / "models.csv", encoding="utf-8")):
    dims = gmpl.model_dims(str(ROOT / m["path"] / "OSeMOSYS_Model.txt"))
    scen = m["scenarios"].split("|")
    base = m["base_scenario"]
    data = {}
    for s in scen:
        f = ROOT / m["path"] / "Executables" / f"{s}_0" / f"{s}_0.txt"
        if f.exists():
            data[s] = gmpl.read_data(str(f), dims)
    if base not in data:
        continue
    for s in scen:
        if s == base or s not in data:
            continue
        n, techs, unflagged = 0, set(), set()
        for p in COST:
            pb, ps = data[base].params.get(p), data[s].params.get(p)
            if ps is None:
                continue
            for k, v in ps.values.items():
                b = pb.get(k, 0.0) if pb else 0.0
                if b == 0 and v != 0:
                    n += 1
                    t = k[dims[p].index("TECHNOLOGY")]
                    techs.add(t)
                    if t not in flag[(m["model"], s, p)]:
                        unflagged.add(f"{p}:{t}")
        if n:
            out.append(dict(model=m["model"], scenario=s, cells_bau_zero_policy_nonzero=n, technologies=len(techs),
                            flagged_by_R5="yes" if not unflagged else f"no: {';'.join(sorted(unflagged))[:200]}"))
with open(JOB / "cost_cells.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["model", "scenario", "cells_bau_zero_policy_nonzero", "technologies",
                                       "flagged_by_R5"], lineterminator="\n")
    w.writeheader()
    w.writerows(out)
for r in out:
    print(r)
