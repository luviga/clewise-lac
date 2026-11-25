"""Step 7: run the suite on the compiled main at the b1 and final points over every model and scenario, and at the
results point on the tracked #19 results; merge the three outputs into the job folder (gate_results.csv,
gate_summary.csv, provenance.csv) and record the run time of each point in run_times.json.
Usage: py -I run_main.py"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import json
import shutil
import subprocess
import time
from collections import Counter
from pathlib import Path

ROOT, JOB = M.ROOT, M.JOB
TMP = M.GATES_TMP / "main_run"
if TMP.exists():
    shutil.rmtree(TMP)
times, rows, prov = {}, [], []
for point in ("b1", "final", "results"):
    out = TMP / point
    t0 = time.time()
    r = subprocess.run([M.ANACONDA, "-I", "gates", "--point", point, "--out", str(out), "--jobs", "3"], cwd=ROOT,
                       capture_output=True, text=True)
    times[point] = dict(seconds=round(time.time() - t0, 1), exit=r.returncode, last_line=r.stdout.strip().splitlines()[-1])
    (JOB / "stage_logs").mkdir(exist_ok=True)
    (JOB / "stage_logs" / f"gates_{point}.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    g = list(csv.DictReader(open(out / "gate_results.csv", encoding="utf-8")))
    rows += g
    shutil.copy2(out / "gate_results.csv", JOB / f"gate_results_{point}.csv")
    if (out / "provenance.csv").exists():
        prov += list(csv.DictReader(open(out / "provenance.csv", encoding="utf-8")))
    print(point, times[point], flush=True)
fields = list(rows[0]) if rows else []
with open(JOB / "gate_results.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
c = Counter((r["check"], r["class"], r["model"], r["point"]) for r in rows)
with open(JOB / "gate_summary.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["check", "class", "model", "point", "count"])
    for k in sorted(c):
        w.writerow(list(k) + [c[k]])
if prov:
    with open(JOB / "provenance.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(prov[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(prov)
(JOB / "run_times.json").write_text(json.dumps(times, indent=2), encoding="utf-8")
print(json.dumps(times, indent=2))
