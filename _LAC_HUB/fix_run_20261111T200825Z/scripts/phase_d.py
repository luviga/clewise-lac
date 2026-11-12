"""Phase D (LAC_OVERNIGHT_COST_RUN): recompile A2 and B1 with the Phase B commands and
compare keyed with the Phase B baseline outputs.

  py -I phase_d.py run <Country>      A2 (a2_driver, fixed overlay source) then B1 (b1_driver)
  py -I phase_d.py compare            writes recompile_diff_summary.csv and recompile_diff_rows.csv

Allowed differences (brief D2): CapitalCost, FixedCost and VariableCost of written cells
(technology and year of a write_set.csv row of that country); Costa Rica SpecifiedAnnualDemand
of E5INDCOA in 2021 and any parameter B1 derives directly from it.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dat_compare import compare_dat  # noqa: E402
from keyed_compare import compare_dirs  # noqa: E402

ROOT = Path(r"C:\clw_fix")
JOB = ROOT / "_LAC_HUB" / "fix_run_20261111T200825Z"
SCENS = ["BAU", "NDCNEW", "LTSNEW"]
SRC = {"CostaRica": "BAU", "DominicanRepublic": "NDCcond", "Ecuador": "BAU", "Guatemala": "NDP",
       "Honduras": "NDP", "Jamaica": "LTSNEW"}
A2_BASE = "cand2_anaconda_pandas2"
B1_BASE = "cand1_anaconda"
COST = {"CapitalCost", "FixedCost", "VariableCost"}


def run(country):
    py = sys.executable
    a2 = [py, "-I", str(HERE / "a2_driver.py"), country, "--source", SRC[country],
          "--logdir", str(JOB / "recompile" / country / "A2")]
    if country == "Guatemala":
        a2.append("--shim")
    p = subprocess.run(a2, cwd=ROOT)
    if p.returncode != 0:
        print(f"A2 failed for {country}", flush=True)
    b1 = [py, "-I", str(HERE / "b1_driver.py"), country, "--logdir", str(JOB / "recompile" / country / "B1")]
    if country == "CostaRica":
        b1 += ["--temp-a2", "LTSOPT=LTSNEW"]
    p2 = subprocess.run(b1, cwd=ROOT)
    for big in (ROOT).glob(f"{country}/**/Executables/*/*_output.txt"):
        if big.stat().st_size > 500 * 1024 * 1024:
            big.unlink()
    return p.returncode, p2.returncode


def _key_parts(key_columns, key):
    return dict(zip(key_columns.split("|"), key.split("|")))


def compare():
    W = pd.read_csv(JOB / "write_set.csv", dtype=str, keep_default_na=False)
    written = {(r.country, r.tech, int(r.year), r.parameter) for r in W.itertuples()}
    rows, summary = [], Counter()
    for country in SRC:
        for stage in ("A2", "B1"):
            for scen in SCENS:
                if stage == "A2":
                    base = JOB / "baseline" / country / "A2" / A2_BASE / "installed" / scen
                    new = JOB / "recompile" / country / "A2" / "installed" / scen
                else:
                    base = JOB / "baseline" / country / "B1" / B1_BASE / "B1_Output_Params" / scen
                    new = JOB / "recompile" / country / "B1" / "B1_Output_Params" / scen
                if not new.exists():
                    rows.append(dict(country=country, stage=stage, scenario=scen, parameter="(missing output)",
                                     key="", kind="missing", baseline="", recompiled="", allowed="no",
                                     reason="no recompiled output"))
                    summary[(country, stage, scen, "(missing output)", "no")] += 1
                    continue
                for d in compare_dirs(base, new):
                    param = d["file"].replace(".csv", "")
                    kp = _key_parts(d.get("key_columns", ""), d["key"]) if d["key"] else {}
                    tech, fuel, year = kp.get("TECHNOLOGY", ""), kp.get("FUEL", ""), kp.get("YEAR", "")
                    allowed, reason = "no", ""
                    if param in COST and year and (country, tech, int(year), param) in written:
                        allowed, reason = "yes", "written cost cell"
                    elif country == "CostaRica" and fuel == "E5INDCOA" and year == "2021":
                        allowed, reason = "yes", "D9 E5INDCOA 2021 (or derived)"
                    rows.append(dict(country=country, stage=stage, scenario=scen, parameter=param, key=d["key"],
                                     kind=d["kind"], baseline=d["a"], recompiled=d["b"], allowed=allowed,
                                     reason=reason))
                    summary[(country, stage, scen, param, allowed)] += 1
            if stage == "B1":
                for scen in SCENS:
                    bd = JOB / "baseline" / country / "B1" / B1_BASE / "data_files" / f"{scen}_0.txt"
                    nd = JOB / "recompile" / country / "B1" / "data_files" / f"{scen}_0.txt"
                    if not (bd.exists() and nd.exists()):
                        continue
                    for d in compare_dat(bd, nd):
                        parts = d["key"].split("|") if d["kind"] == "value" else []
                        param = d["param"]
                        allowed, reason = "no", ""
                        if param in COST and len(parts) >= 3:
                            tech, year = parts[1], parts[-1]
                            if year.isdigit() and (country, tech, int(year), param) in written:
                                allowed, reason = "yes", "written cost cell"
                        if country == "CostaRica" and "E5INDCOA" in parts and parts[-1] == "2021":
                            allowed, reason = "yes", "D9 E5INDCOA 2021 (or derived)"
                        rows.append(dict(country=country, stage="B1 data file", scenario=scen, parameter=param,
                                         key=d["key"], kind=d["kind"], baseline=d["a"], recompiled=d["b"],
                                         allowed=allowed, reason=reason))
                        summary[(country, "B1 data file", scen, param, allowed)] += 1
    with open(JOB / "recompile_diff_rows.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["country", "stage", "scenario", "parameter", "key", "kind", "baseline",
                                           "recompiled", "allowed", "reason"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(JOB / "recompile_diff_summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["country", "stage", "scenario", "parameter", "values_changed", "allowed"])
        for (c, st, sc, p, a), n in sorted(summary.items()):
            w.writerow([c, st, sc, p, n, a])
    bad = sum(n for k, n in summary.items() if k[4] == "no")
    print("difference rows:", len(rows), "not allowed:", bad)
    for k, n in sorted(summary.items()):
        if k[4] == "no":
            print("  NOT ALLOWED", k, n)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        for c in sys.argv[2:]:
            print(c, run(c), flush=True)
    elif sys.argv[1] == "compare":
        compare()
