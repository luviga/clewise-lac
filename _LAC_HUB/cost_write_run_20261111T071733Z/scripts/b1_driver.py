"""Run one country's B1 runner (writes B1_Output_Params and Executables/<scen>_0,
solves the three _0 scenarios with glpsol, processes outputs) and compare.

  1. creates Executables/ in the model folder if missing (gitignored);
  2. puts scripts/glpsol_wrap first on PATH so each solve's Status and
     Objective are logged to <logdir>/solve_log.jsonl (the solver is the real
     glpsol.exe, called with B1's own arguments);
  3. runs `python <runner>` from the model folder (optionally via the
     pandas compatibility shim);
  4. saves B1_Output_Params/{BAU,NDCNEW,LTSNEW} and the regenerated data files
     Executables/<scen>_0/<scen>_0.txt to <logdir>;
  5. with --tracked-ref compares B1_Output_Params keyed with the tracked files;
     with --main-copy compares each data file, parsed by parameter and index,
     with the main copy's Executables/<scen>_0/<scen>_0.txt;
  6. lists tracked files the run changed outside B1_Output_Params.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dat_compare import compare_dat  # noqa: E402
from keyed_compare import compare_dirs  # noqa: E402

ROOT = Path(r"C:\clw_overnight")
JOB = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z"
SHIM = JOB / "scripts" / "run_with_append_shim.py"
WRAP = JOB / "scripts" / "glpsol_wrap"
ANACONDA = r"C:\Users\luisfernando\anaconda3\python.exe"
SCENS = ["BAU", "NDCNEW", "LTSNEW"]

COUNTRIES = {
    "CostaRica": dict(folder="CostaRica/CR_ENERGY/t1_confection", script="B1_Base_Scenarios_Adj_Parallel_CostaRica.py"),
    "DominicanRepublic": dict(folder="DominicanRepublic/RD_ENERGY",
                              script="B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py"),
    "Ecuador": dict(folder="Ecuador/ECU_Energy", script="B1_Base_Scenarios_Adj_Parallel.py"),
    "Guatemala": dict(folder="Guatemala/GUA_ENERGY", script="B1_Base_Scenarios_Adj_Parallel_Guatemala.py"),
    "Honduras": dict(folder="Honduras/HON_ENERGY", script="B1_Base_Scenarios_Adj_Parallel_Honduras.py"),
    "Jamaica": dict(folder="Jamaica/JAM_ENERGY", script="B1_Base_Scenarios_Adj_Parallel_Jamaica.py"),
}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("country")
    ap.add_argument("--script", default="")
    ap.add_argument("--python", default=ANACONDA)
    ap.add_argument("--shim", action="store_true")
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--tracked-ref", default="")
    ap.add_argument("--main-copy", default="")
    ap.add_argument("--timeout", type=int, default=5400)
    ap.add_argument("--temp-a2", default="",
                    help="NAME=SRC: create A2_Output_Params/NAME as a copy of SRC for the run only, then remove "
                         "it and every B1 output of NAME (used for Costa Rica LTSOPT)")
    a = ap.parse_args()

    cfg = COUNTRIES[a.country]
    script = a.script or cfg["script"]
    folder = ROOT / cfg["folder"]
    logdir = Path(a.logdir).resolve()
    if logdir.exists():
        shutil.rmtree(logdir)
    logdir.mkdir(parents=True)
    (folder / "Executables").mkdir(exist_ok=True)

    status_before = set(git("status", "--porcelain", "--", cfg["folder"]).stdout.splitlines())
    temp_name = None
    if a.temp_a2:
        temp_name, temp_src = a.temp_a2.split("=")
        tdir = folder / "A2_Output_Params" / temp_name
        if tdir.exists():
            raise SystemExit(f"{tdir} exists already")
        shutil.copytree(folder / "A2_Output_Params" / temp_src, tdir)
        (folder / "B1_Output_Params" / temp_name).mkdir()
    before = {}
    for scen in SCENS:
        for f in (folder / "B1_Output_Params" / scen).glob("*.csv"):
            before[(scen, f.name)] = f.stat().st_mtime_ns
    time.sleep(1.0)

    env = os.environ.copy()
    env["PATH"] = str(WRAP) + os.pathsep + env.get("PATH", "")
    env["GLPSOL_WRAP_LOG"] = str(logdir / "solve_log.jsonl")
    cmd = [a.python] + ([str(SHIM)] if a.shim else []) + [script]
    t0 = time.time()
    with open(logdir / "run.log", "w", newline="\n") as fh:
        try:
            proc = subprocess.run(cmd, cwd=folder, stdout=fh, stderr=subprocess.STDOUT, env=env, timeout=a.timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
    dt = time.time() - t0
    shown = ["python(anaconda)" if "anaconda3" in a.python else Path(a.python).name]
    shown += (["run_with_append_shim.py"] if a.shim else []) + [script]
    summary = {"country": a.country, "command": " ".join(shown), "exit": rc, "seconds": round(dt, 1)}
    print(f"{a.country}: {script} exit {rc} in {dt:.1f}s")

    solves = []
    if (logdir / "solve_log.jsonl").exists():
        for ln in (logdir / "solve_log.jsonl").read_text().splitlines():
            if ln.strip():
                solves.append(json.loads(ln))
    summary["solves"] = [{k: s[k] for k in ("data", "status", "objective", "seconds", "returncode")} for s in solves]

    summary["b1_files_written"] = {
        scen: sum(1 for f in (folder / "B1_Output_Params" / scen).glob("*.csv")
                  if before.get((scen, f.name)) != f.stat().st_mtime_ns)
        for scen in SCENS}
    if temp_name:
        for p in [folder / "A2_Output_Params" / temp_name, folder / "B1_Output_Params" / temp_name,
                  folder / "Executables" / f"{temp_name}_0"]:
            if p.exists():
                shutil.rmtree(p)
        summary["temp_a2"] = a.temp_a2 + " (created for the run, removed after with its B1 outputs)"
    b1_rows, dat_rows = [], []
    for scen in SCENS:
        src = folder / "B1_Output_Params" / scen
        if src.exists():
            shutil.copytree(src, logdir / "B1_Output_Params" / scen)
        dat = folder / "Executables" / f"{scen}_0" / f"{scen}_0.txt"
        if dat.exists():
            (logdir / "data_files").mkdir(exist_ok=True)
            shutil.copy2(dat, logdir / "data_files" / dat.name)
        if a.tracked_ref and src.exists():
            rows = compare_dirs(Path(a.tracked_ref) / cfg["folder"] / "B1_Output_Params" / scen, src)
            for r in rows:
                r["scenario"] = scen
            b1_rows += rows
        if a.main_copy and dat.exists():
            ref = Path(a.main_copy) / cfg["folder"] / "Executables" / f"{scen}_0" / f"{scen}_0.txt"
            if ref.exists():
                rows = compare_dat(ref, dat)
                for r in rows:
                    r["scenario"] = scen
                dat_rows += rows
                summary.setdefault("datafile_diffs", {})[scen] = len(rows)
            else:
                summary.setdefault("datafile_diffs", {})[scen] = "no main-copy file"
    summary["b1_diffs"] = {s: sum(1 for r in b1_rows if r["scenario"] == s) for s in SCENS}

    status_after = set(git("status", "--porcelain", "--", cfg["folder"]).stdout.splitlines())
    changed = sorted(x for x in status_after - status_before if "B1_Output_Params" not in x)
    summary["other_changed_paths"] = changed
    # SelectedResults.csv is written by the runner in the model folder (last writer wins; ignored)
    sel = folder / "SelectedResults.csv"
    if sel.exists() and f"?? {cfg['folder']}/SelectedResults.csv" in changed:
        sel.unlink()
        summary["removed_untracked"] = "SelectedResults.csv"

    write_csv(logdir / "diff_rows.csv", b1_rows, ["scenario", "file", "key_columns", "key", "kind", "a", "b"])
    write_csv(logdir / "datafile_diff_rows.csv", dat_rows, ["scenario", "param", "key", "kind", "a", "b"])
    (logdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in summary if k not in ("solves",)}))
    for s in summary["solves"]:
        print("  solve:", s)
    sys.exit(0 if rc == 0 else 1)


if __name__ == "__main__":
    main()
