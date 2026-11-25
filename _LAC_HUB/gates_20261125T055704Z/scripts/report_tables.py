"""Tables for REPORT_LAC_INPUT_GATES from the job outputs (markdown on stdout).
Usage: py -I report_tables.py"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import json
import os
from collections import Counter, defaultdict

JOB = M.JOB
ROOT = M.ROOT


def rd(name):
    p = JOB / name
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def md(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols) + " |")
    return "\n".join(out)


# compile and translation per model and scenario
checks = [json.loads(x) for x in open(JOB / "check_log.jsonl", encoding="utf-8") if x.strip()]
by_data = {}
for c in checks:
    by_data[c["data"]] = c
models = list(csv.DictReader(open(ROOT / "config" / "gates" / "models.csv", encoding="utf-8")))
cat = {r["scenario"]: r["stage3_folder"] for r in csv.DictReader(open(ROOT / "config" / "scenarios" / "scenario_catalogue.csv",
                                                                       encoding="utf-8")) if r["stage3_folder"]}
rows = []
for m in models:
    for s in m["scenarios"].split("|"):
        f0 = ROOT / m["path"] / "Executables" / f"{s}_0" / f"{s}_0.txt"
        c0 = by_data.get(f0.relative_to(ROOT).as_posix(), {})
        r = dict(model=m["model"], scenario=s, written="yes" if f0.exists() else "no",
                 translation_0=c0.get("status", "not translated"), rows_0=c0.get("rows", ""),
                 seconds_0=c0.get("seconds", ""))
        if m["stage3"] == "yes" and s in cat:
            ff = ROOT / m["path"] / "Executables" / cat[s] / f"{cat[s]}.txt"
            cf = by_data.get(ff.relative_to(ROOT).as_posix(), {})
            r.update(final="yes" if ff.exists() else "no", translation_final=cf.get("status", "not translated"),
                     seconds_final=cf.get("seconds", ""))
        rows.append(r)
print("## Compile and translation\n")
print(md(rows, ["model", "scenario", "written", "translation_0", "rows_0", "seconds_0", "final", "translation_final",
                "seconds_final"]))
print(f"\nTranslations logged: {len(checks)}; T0 failures: {sum(1 for c in checks if c['status'] != 'translated')}\n")

for name in ("gate_results_b1.csv", "gate_results_final.csv", "gate_results_results.csv"):
    g = rd(name)
    if not g:
        continue
    print(f"## {name}\n")
    cnt = Counter((r["check"], r["class"]) for r in g)
    per = defaultdict(Counter)
    for r in g:
        per[(r["check"], r["class"])][r["model"]] += 1
    out = [dict(check=k[0], cls=k[1], count=v, models="; ".join(f"{m} {n}" for m, n in sorted(per[k].items())))
           for k, v in sorted(cnt.items())]
    print(md(out, ["check", "cls", "count", "models"]))
    print()

prov = rd("provenance.csv")
if prov:
    tot = Counter()
    for p in prov:
        tot[(p["point"], p["origin_kind"])] += int(p["cells"])
    print("## Provenance (cells)\n")
    for pt in sorted({k[0] for k in tot}):
        allc = sum(v for k, v in tot.items() if k[0] == pt)
        un = tot.get((pt, "UNTRACED"), 0)
        parts = ", ".join(f"{k[1]} {v}" for k, v in sorted(tot.items()) if k[0] == pt)
        print(f"- {pt}: {allc} cells; {parts}; traced share {100 * (allc - un) / allc:.1f} percent")
