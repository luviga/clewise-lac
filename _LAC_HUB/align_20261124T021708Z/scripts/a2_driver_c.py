"""Phase C A2 driver: run one country's A2 compiler with scenario names from the catalogue (lac_tables).

After C2 the compilers no longer write folders under older scenario names:
  direct     (Dominican Republic, Guatemala, Honduras, Jamaica): the compiler writes the base folder and each
             policy folder itself;
  copy_base  (Costa Rica, Ecuador): the policy scenarios take the base files, so the files the compiler writes
             to the base folder are copied over each policy folder (files it does not write stay), as the
             pipeline step of pipeline_commands.csv did.
Then the tracked side files the compiler rewrites (A1_Outputs, A2_Structure_Lists.xlsx, A2_Extra_Inputs) are
restored with git checkout, and the installed folders are saved to <logdir>/installed.
Usage: py -I a2_driver_c.py <Country> --logdir <dir> [--shim]
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import argparse
import importlib.util
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = M.ROOT
SHIM = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z" / "scripts" / "run_with_append_shim.py"
ANACONDA = M.ANACONDA
spec = importlib.util.spec_from_file_location('lac_tables', str(ROOT / 'lac_tables.py'))
LT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LT)
MODE = {"CostaRica": "copy_base", "Ecuador": "copy_base", "DominicanRepublic": "direct", "Guatemala": "direct",
        "Honduras": "direct", "Jamaica": "direct"}
SIDE_FILES = ["A1_Outputs", "A2_Structure_Lists.xlsx", "A2_Extra_Inputs"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("country")
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--shim", action="store_true")
    a = ap.parse_args()
    rel = LT.model_path(a.country)
    folder = ROOT / rel
    script = LT.country_value(a.country, 'a2_script')
    a2 = folder / "A2_Output_Params"
    base, policy = LT.scenario('base'), LT.scenarios('policy')
    logdir = Path(a.logdir)
    if logdir.exists():
        shutil.rmtree(logdir)
    logdir.mkdir(parents=True)
    before = {}
    for name in [base] + policy:
        for f in (a2 / name).glob("*.csv"):
            before[(name, f.name)] = f.stat().st_mtime_ns
    time.sleep(1.0)
    cmd = [ANACONDA] + ([str(SHIM)] if a.shim else []) + [script]
    t0 = time.time()
    with open(logdir / "run.log", "w", newline="\n") as fh:
        proc = subprocess.run(cmd, cwd=folder, stdout=fh, stderr=subprocess.STDOUT)
    summary = {"country": a.country, "mode": MODE[a.country], "exit": proc.returncode, "seconds": round(time.time() - t0, 1),
               "command": " ".join(["python(anaconda)"] + (["run_with_append_shim.py"] if a.shim else []) + [script])}
    written = {}
    for name in [base] + policy:
        written[name] = [f for f in (a2 / name).glob("*.csv") if before.get((name, f.name)) != f.stat().st_mtime_ns]
    summary["produced"] = {n: len(v) for n, v in written.items()}
    if proc.returncode == 0 and MODE[a.country] == "copy_base":
        for scen in policy:
            for f in written[base]:
                shutil.copy2(f, a2 / scen / f.name)
        summary["copied_base_files_to_policy"] = len(written[base])
    for scen in [base] + policy:
        shutil.copytree(a2 / scen, logdir / "installed" / scen)
    sides = [f"{rel}/{s}" for s in SIDE_FILES if (folder / s).exists()]
    subprocess.run(["git", "checkout", "--", *sides], cwd=ROOT)
    subprocess.run(["git", "clean", "-f", "-q", "--", *sides], cwd=ROOT)
    (logdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
