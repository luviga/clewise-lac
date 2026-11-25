"""Step 6, Guatemala distance case: the heavy freight distance Ref.km.BY that LAC_ALIGN reverted (9000 -> 50400,
register_distance_revert.csv) is put back in a copy of the model folder in the temporary folder, the model is
recompiled there with its own A2 compiler and B1 runner (glpsol wrapper in check mode, no solve), Stage 3 is built
there with scenario_rules.py and stage3_apply.py on the tracked controller, and the suite runs on the copy.
Appends its row to replay_check.csv. Usage: py -I replay_gua_distance.py"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT, JOB = M.ROOT, M.JOB
R = M.GATES_TMP / "replay" / "gua_distance_root"
MODEL = "Guatemala/GUA_ENERGY"
if R.exists():
    shutil.rmtree(R)
R.mkdir(parents=True)
for f in ("lac_tables.py", "scenario_rules.py", "stage3_apply.py", "ao_safe_save.py"):
    shutil.copy2(ROOT / f, R / f)
for d in ("config", "inputs", "_STAGE2_OUTPUT"):
    shutil.copytree(ROOT / d, R / d)
shutil.copytree(ROOT / MODEL, R / MODEL, ignore=shutil.ignore_patterns("Executables"))
(R / MODEL / "Executables").mkdir()

# put the distance back (Excel recalculates the workbook's formulas through the repository's safe save)
sys.path.insert(0, str(ROOT))
import openpyxl  # noqa: E402
import ao_safe_save  # noqa: E402
wbp = R / MODEL / "A1_Outputs" / "A-O_Demand.xlsx"
wb = openpyxl.load_workbook(wbp)
ws = wb["Demand_Projection"]
assert ws["B41"].value == "Techs_He_Freight", ws["B41"].value
before = ws["F41"].value
ws["F41"] = 9000
ao_safe_save.save_ao_safely(wb, wbp)
print("F41", before, "-> 9000")

LOG = R / "logs"
LOG.mkdir()
env = dict(os.environ, PATH=str(JOB / "scripts" / "glpsol_wrap") + os.pathsep + os.environ["PATH"], GLPSOL_CHECK="1",
           GLPSOL_CHECK_LOG=str(LOG / "check_log.jsonl"), PYTHONIOENCODING="utf-8")
shim = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z" / "scripts" / "run_with_append_shim.py"
for name, cmd, cwd in (("a2", [M.ANACONDA, str(shim), "A2_Compiler_Guatemala.py"], R / MODEL),
                       ("b1", [M.ANACONDA, "B1_Base_Scenarios_Adj_Parallel_Guatemala.py"], R / MODEL),
                       ("rules", [M.ANACONDA, "scenario_rules.py", "--root", ".", "--countries", "Guatemala"], R),
                       ("stage3", [M.ANACONDA, "stage3_apply.py", "--root", ".", "--clean", "--uncap-pp-maxcap",
                                   "--countries", "Guatemala"], R)):
    with open(LOG / f"{name}.log", "w", encoding="utf-8") as fh:
        rc = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, env=env).returncode
    print(name, "exit", rc, flush=True)

sys.path.insert(0, str(ROOT))
from gates import run as GR  # noqa: E402
res = {}
for point in ("b1", "final"):
    out = R / f"out_{point}"
    GR.main(["--point", point, "--models", "GUA_ENERGY", "--scenarios", "NDC", "LTS", "--data-dir", str(R),
             "--b1-data-dir", str(R), "--out", str(out), "--jobs", "1"])
    res[point] = list(csv.DictReader(open(out / "gate_results.csv", encoding="utf-8")))
hit = None
for point in ("final", "b1"):
    for r in res[point]:
        if r["check"] in ("P1", "B8", "B5", "S1", "S4") and r["class"] == "FAIL":
            hit = r
            break
    if hit:
        break
line = ",".join(hit[k] for k in ("check", "class", "model", "scenario", "point", "parameter", "technology", "fuel",
                                 "emission", "year", "timeslice", "values", "message")) if hit else ""
row = dict(defect="Guatemala NDC and LTS infeasible after the heavy freight distance rescaled transport demand",
           model="GUA_ENERGY", scenario="NDC|LTS",
           how_put_back=f"A-O_Demand.xlsx Demand_Projection F41 (Techs_He_Freight Ref.km.BY) {before} -> 9000 in a copy; "
                        "model recompiled there (A2, B1 in check mode), scenario_rules.py and stage3_apply.py run there",
           expected_check="P1|B8|B5|S1|S4", flagged="yes" if hit else "no", gate_results_line=line)
print(row)
out = JOB / "replay_check.csv"
exists = out.exists()
with open(out, "a", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(row), lineterminator="\n")
    if not exists:
        w.writeheader()
    w.writerow(row)
