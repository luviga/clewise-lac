"""Run one country's A2 compiler and build A2_Output_Params/{BAU,NDCNEW,LTSNEW}.

The compilers write BAU plus one or more 'other scenario' folders whose names
predate NDCNEW and LTSNEW (NDCincond, NDCcond, NDP, LTSNEW ...). The tracked
NDCNEW and LTSNEW folders hold the files one compiler folder produces, plus
files the compiler does not write (header-only or static). The canonical step
copies the produced files of the chosen folder over the existing NDCNEW and
LTSNEW folders and leaves the other files as they are. This driver:

  1. empties every folder the compiler writes to (so only fresh output is
     read), creating the ones that do not exist;
  2. runs the compiler from the model folder with the given interpreter
     (optionally through run_with_append_shim.py);
  3. saves every produced folder to <logdir>/produced/<name>/;
  4. for NDCNEW and LTSNEW builds each candidate "BAU overlaid by <folder>"
     and, with --tracked-ref, compares it keyed with the tracked folder;
  5. installs the chosen candidate into A2_Output_Params/NDCNEW and LTSNEW
     and saves the installed BAU/NDCNEW/LTSNEW to <logdir>/installed/;
  6. removes the folders it created and restores the tracked side files the
     compiler rewrites (A1_Outputs, A2_Structure_Lists.xlsx, A2_Extra_Inputs).
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keyed_compare import compare_dirs  # noqa: E402

ROOT = Path(r"C:\clw_overnight")
JOB = ROOT / "_LAC_HUB" / "cost_write_run_20261111T071733Z"
SHIM = JOB / "scripts" / "run_with_append_shim.py"
ANACONDA = r"C:\Users\luisfernando\anaconda3\python.exe"

COUNTRIES = {
    "CostaRica": dict(folder="CostaRica/CR_ENERGY/t1_confection", script="A2_Compiler_CostaRica.py",
                      other=["NDCincond", "NDCcond"]),
    "DominicanRepublic": dict(folder="DominicanRepublic/RD_ENERGY", script="A2_Compiler_DominicanRepublic.py",
                              other=["NDCincond", "NDCcond"]),
    "Ecuador": dict(folder="Ecuador/ECU_Energy", script="A2_Compiler_Ecuador.py", other=["NDCINC"]),
    "Guatemala": dict(folder="Guatemala/GUA_ENERGY", script="A2_Compiler_Guatemala.py", other=["NDP"]),
    "Honduras": dict(folder="Honduras/HON_ENERGY", script="A2_Compiler_Honduras.py",
                     other=["NDP", "NDPAMB", "NDCincond", "NDCcond"]),
    "Jamaica": dict(folder="Jamaica/JAM_ENERGY", script="A2_Compiler_Jamaica.py", other=["LTSNEW"]),
}
SIDE_FILES = ["A1_Outputs", "A2_Structure_Lists.xlsx", "A2_Extra_Inputs"]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def build_candidate(a2_bau: Path, src, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in a2_bau.glob("*.csv"):
        shutil.copy2(f, dst / f.name)
    if src is not None:
        for f in src.glob("*.csv"):
            shutil.copy2(f, dst / f.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("country")
    ap.add_argument("--python", default=ANACONDA)
    ap.add_argument("--shim", action="store_true")
    ap.add_argument("--script", default="")
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--tracked-ref", default="")
    ap.add_argument("--source", default="", help="force the NDCNEW/LTSNEW overlay folder ('BAU' = plain copy)")
    a = ap.parse_args()

    cfg = COUNTRIES[a.country]
    script = a.script or cfg["script"]
    folder = ROOT / cfg["folder"]
    a2 = folder / "A2_Output_Params"
    logdir = Path(a.logdir)
    if logdir.exists():
        shutil.rmtree(logdir)
    logdir.mkdir(parents=True)

    # snapshot of NDCNEW and LTSNEW before the run (Jamaica's compiler writes LTSNEW)
    for scen in ["NDCNEW", "LTSNEW"]:
        shutil.copytree(a2 / scen, logdir / f"pre_{scen}")
    created = []
    before = {}
    for name in ["BAU"] + cfg["other"]:
        p = a2 / name
        if p.exists():
            for f in p.glob("*.csv"):
                before[(name, f.name)] = f.stat().st_mtime_ns
        else:
            p.mkdir(parents=True)
            created.append(p)
    time.sleep(1.0)

    cmd = [a.python] + ([str(SHIM)] if a.shim else []) + [script]
    t0 = time.time()
    with open(logdir / "run.log", "w", newline="\n") as fh:
        proc = subprocess.run(cmd, cwd=folder, stdout=fh, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    shown = ["python(anaconda)" if "anaconda3" in a.python else Path(a.python).name]
    shown += (["run_with_append_shim.py"] if a.shim else []) + [script]
    summary = {"country": a.country, "command": " ".join(shown), "exit": proc.returncode, "seconds": round(dt, 1)}
    print(f"{a.country}: exit {proc.returncode} in {dt:.1f}s")

    # a file counts as produced when it is new or its modification time changed
    written = {}
    for name in ["BAU"] + cfg["other"]:
        files = [f for f in (a2 / name).glob("*.csv")
                 if before.get((name, f.name)) != f.stat().st_mtime_ns]
        if files:
            written[name] = files
    produced = list(written)
    summary["produced"] = {n: len(written[n]) for n in produced}
    summary["static_files_in_BAU"] = sorted(f.name for f in (a2 / "BAU").glob("*.csv")
                                            if f not in written.get("BAU", []))
    for n in produced:
        (logdir / "produced" / n).mkdir(parents=True)
        for f in written[n]:
            shutil.copy2(f, logdir / "produced" / n / f.name)
    # candidates start from the full BAU folder (produced files plus the static ones)
    full_bau = logdir / "full_BAU"
    shutil.copytree(a2 / "BAU", full_bau)

    diff_rows = []
    choice = {}
    if "BAU" in produced and proc.returncode == 0:
        cand_dir = logdir / "candidates"
        options = [None] + [n for n in produced if n != "BAU"]
        for scen in ["NDCNEW", "LTSNEW"]:
            results = []
            for src in options:
                label = src or "BAU"
                if a.source and label != a.source:
                    continue
                d = cand_dir / f"{scen}__{label}"
                # the existing folder, with the produced files of <src> copied over it
                build_candidate(logdir / f"pre_{scen}", logdir / "produced" / (src or "BAU"), d)
                if a.tracked_ref:
                    rows = compare_dirs(Path(a.tracked_ref) / cfg["folder"] / "A2_Output_Params" / scen, d)
                    results.append((len(rows), label, rows))
                    print(f"  {scen}: BAU overlaid by {label}: {len(rows)} differing rows")
                else:
                    results.append((0, label, []))
            results.sort(key=lambda t: t[0])
            n, label, rows = results[0]
            choice[scen] = {"source": label, "differing_rows": n}
            for r in rows:
                r.update(scenario=scen, source=label)
            diff_rows += rows
        if a.tracked_ref:
            rows = compare_dirs(Path(a.tracked_ref) / cfg["folder"] / "A2_Output_Params" / "BAU", full_bau)
            for r in rows:
                r.update(scenario="BAU", source="BAU")
            diff_rows = rows + diff_rows
            choice["BAU"] = {"source": "BAU", "differing_rows": len(rows)}
        for scen in ["NDCNEW", "LTSNEW"]:
            src_dir = cand_dir / f"{scen}__{choice[scen]['source']}"
            dst = a2 / scen
            for f in dst.glob("*.csv"):
                f.unlink()
            for f in src_dir.glob("*.csv"):
                shutil.copy2(f, dst / f.name)
        for scen in ["BAU", "NDCNEW", "LTSNEW"]:
            shutil.copytree(a2 / scen, logdir / "installed" / scen)
        shutil.rmtree(cand_dir)
    shutil.rmtree(full_bau)
    for scen in ["NDCNEW", "LTSNEW"]:
        shutil.rmtree(logdir / f"pre_{scen}")
    summary["choice"] = choice

    for p in created:
        shutil.rmtree(p)
    rel = cfg["folder"]
    sides = [f"{rel}/{s}" for s in SIDE_FILES if (folder / s).exists()]
    git("checkout", "--", *sides)
    git("clean", "-f", "-q", "--", *sides)

    with open(logdir / "diff_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["scenario", "source", "file", "key_columns", "key", "kind", "a", "b"],
                           extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in diff_rows:
            w.writerow(r)
    (logdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
