"""Step G gates. Writes parts/gate_results.csv."""
import os
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, read_csv, write_csv, sha256

REPO = os.path.dirname(os.path.dirname(JOB))
REL = "_LAC_HUB/" + os.path.basename(JOB) + "/"
res = []


def gate(n, name, ok, detail):
    res.append({"gate": n, "name": name, "result": "pass" if ok else "fail", "detail": detail})
    print(n, "pass" if ok else "FAIL", detail)


# 1
d = subprocess.run(["git", "-C", REPO, "diff", "--name-only", "origin/main"], capture_output=True, text=True).stdout.split()
u = subprocess.run(["git", "-C", REPO, "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.split()
bad = [f for f in d + u if not f.startswith(REL)]
gate(1, "changes only under the job folder", not bad, f"{len(d)} changed, {len(u)} untracked; outside: {bad[:5]}")

# 2
src = {r["id"]: r for r in read_csv(os.path.join(JOB, "sources.csv"))}
missing, nopage, lead = [], [], []
for code in CODES:
    for fn in [f"verification_{code}.csv", f"analyses_{code}.csv"]:
        p = os.path.join(JOB, fn)
        if not os.path.exists(p):
            missing.append(f"{fn} absent")
            continue
        for r in read_csv(p):
            if r["source_id"] not in src:
                missing.append(f"{fn}:{r['source_id']}")
            pg = r.get("check1_page") or r.get("page")
            if not pg:
                nopage.append(f"{fn}:{r.get('value_id', r['source_id'])}")
for r in read_csv(os.path.join(JOB, "scenario_values.csv")):
    if r["source_id"] not in src:
        missing.append(f"scenario_values:{r['source_id']}")
    elif src[r["source_id"]]["class"] == "lead":
        lead.append(r["value_id"])
    if not r["page"]:
        nopage.append(f"scenario_values:{r['value_id']}")
gate(2, "source ids exist, pages given, no lead in scenario_values", not (missing or nopage or lead),
     f"missing ids {len(missing)} {missing[:5]}; no page {len(nopage)} {nopage[:5]}; lead rows {len(lead)}")

# 3
ver = set()
for code in CODES:
    ver |= {r["value_id"] for r in read_csv(os.path.join(JOB, f"verification_{code}.csv"))}
vv = [r["value_id"] for r in read_csv(os.path.join(JOB, "values_to_verify.csv"))]
nov = [v for v in vv if v not in ver]
gate(3, "every value to verify has a verification row", not nov, f"{len(vv)} values, {len(nov)} without row {nov[:5]}")

# 4
units = read_csv(os.path.join(JOB, "units.csv"))
std = {r["standard_unit"] for r in units} | {r["unit"] for r in units}
badu = [r["value_id"] for r in read_csv(os.path.join(JOB, "scenario_values.csv")) if r["unit_standard"] and r["unit_standard"] not in std]
empty = [r["value_id"] for r in read_csv(os.path.join(JOB, "scenario_values.csv")) if not r["unit_standard"] and r["value_id"]]
gate(4, "standard units listed in units.csv", not badu and not empty, f"not listed {badu[:5]}; empty {empty[:5]}")

# 5
badf = []
for r in src.values():
    f = os.path.normpath(os.path.join(JOB, r["file"]))
    if not os.path.exists(f) or sha256(f) != r["SHA-256"].strip().lower():
        badf.append(r["id"])
gate(5, "source files exist with matching SHA-256", not badf, f"{len(src)} sources; bad {badf}")

# 6
s = subprocess.run(["git", "-C", "C:/clw_scout_model", "status", "--short"], capture_output=True, text=True).stdout.strip()
gate(6, "model worktree clean", s == "", s[:200] or "empty")

write_csv(os.path.join(JOB, "parts", "gate_results.csv"), res)
