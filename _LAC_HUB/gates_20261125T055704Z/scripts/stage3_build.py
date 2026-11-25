"""Step 2.3: build the Stage 3 data files without solving.

  1. keep a copy of every compiled energy data file Executables/<scenario>_0/<scenario>_0.txt (the b1 point) in
     <tmp>/pristine_b1/<model path>/Executables/...;
  2. scenario_rules.py --root . (the pipeline step that rewrites the _0 files before Stage 0 and Stage 3:
     hydrogen and history rules), as PIPELINE_WORKFLOW.md runs it;
  3. stage3_apply.py --root . --clean --uncap-pp-maxcap with the tracked Stage 2 controller
     (_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx);
  4. the tracked caps of _STAGE3_RESULTS/EMISSION_CAPS.csv written into the capped FINAL data files by the
     pipeline's own writing function (scenario_rules.set_rows, the function stage3_emission_cap.py calls);
  5. every FINAL data file translated with glpsol --check through the wrapper in check mode (check_log.jsonl);
  6. the rule-applied _0 files saved to <tmp>/rules_b1 and the compiled _0 files put back, so the b1 point
     reads what the compile wrote;
  7. the tracked files these steps changed listed in stage_logs/stage3/changed.txt.
Usage: py -I stage3_build.py
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT, JOB = M.ROOT, M.JOB
TMP = M.GATES_TMP
LOG = JOB / "stage_logs" / "stage3"
LOG.mkdir(parents=True, exist_ok=True)
models = [m for m in csv.DictReader(open(ROOT / "config" / "gates" / "models.csv", encoding="utf-8"))
          if m["stage3"] == "yes"]
times = {}
CAT = {r["scenario"]: r["stage3_folder"] for r in csv.DictReader(
    open(ROOT / "config" / "scenarios" / "scenario_catalogue.csv", encoding="utf-8")) if r["stage3_folder"]}


def run(name, cmd):
    t0 = time.time()
    with open(LOG / f"{name}.log", "w", encoding="utf-8", newline="\n") as fh:
        r = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    times[name] = round(time.time() - t0, 1)
    print(name, "exit", r.returncode, times[name], "s", flush=True)
    return r.returncode


def copy_zero(src_root, dst_root):
    n = 0
    for m in models:
        for s in m["scenarios"].split("|"):
            f = src_root / m["path"] / "Executables" / f"{s}_0" / f"{s}_0.txt"
            if f.exists():
                d = dst_root / m["path"] / "Executables" / f"{s}_0" / f"{s}_0.txt"
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, d)
                n += 1
    return n


print("pristine copies:", copy_zero(ROOT, TMP / "pristine_b1"))
run("scenario_rules", [M.ANACONDA, "scenario_rules.py", "--root", "."])
run("stage3_apply", [M.ANACONDA, "stage3_apply.py", "--root", ".", "--clean", "--uncap-pp-maxcap"])

# caps through the pipeline's own writing function
t0 = time.time()
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import lac_tables as LT  # noqa: E402
import scenario_rules as SR  # noqa: E402
caps = defaultdict(lambda: defaultdict(dict))
for r in csv.DictReader(open(ROOT / "_STAGE3_RESULTS" / "EMISSION_CAPS.csv", encoding="utf-8")):
    caps[(r["country"], r["scenario"])][r["emission"]][int(r["year"])] = float(r["cap"])
cap_log = []
for (c, sc), cp in caps.items():
    folder = CAT[sc]
    data = ROOT / LT.model_path(c) / "Executables" / folder / f"{folder}.txt"
    with open(data, "r", encoding="utf-8", errors="replace", newline="") as fh:
        content = fh.read()
    crlf = "\r\n" in content
    content = content.replace("\r\n", "\n")
    yrs = SR.years_of(content)
    content, n = SR.set_rows(content, "AnnualEmissionLimit", cp, yrs, SR.region_of(content))
    if crlf:
        content = content.replace("\n", "\r\n")
    with open(data, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    cap_log.append(dict(country=c, scenario=sc, values=n, labels="|".join(cp), file=f"{folder}/{folder}.txt"))
    print(f"cap {c} {sc}: {n} values", flush=True)
times["emission_cap_write"] = round(time.time() - t0, 1)

# translate every FINAL data file
env = dict(os.environ, GLPSOL_CHECK="1", GLPSOL_CHECK_LOG=str(JOB / "check_log.jsonl"))
t0 = time.time()
cat = CAT
final_rows = []
for m in models:
    for s in m["scenarios"].split("|"):
        if s not in cat:
            continue
        f = ROOT / m["path"] / "Executables" / cat[s] / f"{cat[s]}.txt"
        if not f.exists():
            final_rows.append(dict(model=m["model"], scenario=s, data_file_written="no", translation="no file"))
            continue
        r = subprocess.run([M.ANACONDA, "-I", str(JOB / "scripts" / "glpsol_wrap.py"), "-m",
                            str(ROOT / m["path"] / "OSeMOSYS_Model.txt"), "-d", str(f)], env=env,
                           capture_output=True, text=True)
        final_rows.append(dict(model=m["model"], scenario=s, data_file_written="yes",
                               translation="translated" if r.returncode == 0 else "T0", output=r.stdout.strip()[-200:]))
        print(final_rows[-1], flush=True)
times["final_translation"] = round(time.time() - t0, 1)

print("rules copies:", copy_zero(ROOT, TMP / "rules_b1"))
print("restored pristine:", copy_zero(TMP / "pristine_b1", ROOT))
st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
(LOG / "changed.txt").write_text(st, encoding="utf-8")
with open(JOB / "compile_final.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["model", "scenario", "data_file_written", "translation", "output"],
                       lineterminator="\n")
    w.writeheader()
    w.writerows(final_rows)
(LOG / "times.json").write_text(json.dumps(dict(times=times, caps=cap_log), indent=2), encoding="utf-8")
print(json.dumps(times))
