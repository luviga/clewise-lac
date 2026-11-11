"""E2: compare the base re-runs with the 16 May results (LAC_OVERNIGHT_COST_RUN).

Inputs: the 16 May workbooks taken from the base commit (git show 4124868:...), the new
_STAGE3_RESULTS/stage3_results.xlsx and _STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx, and the solve
logs (new: stage_logs/solves_stage3.jsonl; 16 May: resolve_16may.jsonl, the main copy's 16 May
*_FINAL_0 data files solved again with the same model and glpsol).

Definitions follow stage3_results.py: RE share = activity of PP/PWR technologies flagged
Is_Renewable in the controller TECH_MAP over all PP/PWR activity; RE targets NDCNEW 2035 and 2050
75 percent, LTSNEW 2035 75 and 2050 99 percent, 2 pp tolerance; emissions = AnnualEmissions summed
over every emission; new capacity = NewCapacity of PP/PWR technologies summed over the horizon.
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"C:\clw_fix")
JOB = ROOT / "_LAC_HUB" / "fix_run_20261111T200825Z"
BASE = "4124868"
COUNTRIES = ["CostaRica", "DominicanRepublic", "Ecuador", "Guatemala", "Honduras", "Jamaica"]
SCENS = ["BAU", "NDCNEW", "LTSNEW"]
RE_TARGETS = {"NDCNEW": {2035: 0.75, 2050: 0.75}, "LTSNEW": {2035: 0.75, 2050: 0.99}}


def git_bytes(path):
    return subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=ROOT, capture_output=True).stdout


def load(xlsx_bytes_or_path):
    src = io.BytesIO(xlsx_bytes_or_path) if isinstance(xlsx_bytes_or_path, bytes) else xlsx_bytes_or_path
    return pd.read_excel(src, sheet_name=None)


def re_shares(res, ctrl):
    tm = ctrl["TECH_MAP"]
    re_t = set(tm[tm["Is_Renewable"] == 1.0]["Tech"])
    act = res["TotalTechnologyAnnualActivity"]
    pp = act[act["Technology"].str.upper().str.startswith(("PP", "PWR"))].copy()
    pp["RE"] = pp["Technology"].isin(re_t)
    tot = pp.groupby(["Country", "Scenario", "Year"])["Value"].sum()
    re = pp[pp["RE"]].groupby(["Country", "Scenario", "Year"])["Value"].sum()
    return (re / tot).fillna(0.0)


def solves(path):
    out = {}
    if not Path(path).exists():
        return out
    for ln in Path(path).read_text().splitlines():
        if not ln.strip():
            continue
        d = json.loads(ln)
        m = re.search(r"(CostaRica|DominicanRepublic|Ecuador|Guatemala|Honduras|Jamaica).*?(BAU|NDCNEW|LTSNEW)_FINAL_0",
                      (d.get("data") or "").replace("\\\\", "\\"))
        if m:
            obj = None
            if d.get("objective"):
                mm = re.search(r"=\s*([-0-9.eE+]+)", d["objective"])
                obj = float(mm.group(1)) if mm else None
            out[(m.group(1), m.group(2))] = (d.get("status"), obj)
    return out


def main():
    old = load(git_bytes("_STAGE3_RESULTS/stage3_results.xlsx"))
    oldc = load(git_bytes("_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx"))
    new = load(ROOT / "_STAGE3_RESULTS" / "stage3_results.xlsx")
    newc = load(ROOT / "_STAGE2_OUTPUT" / "CONTROLLER_NEW_SCENARIOS.xlsx")
    so, sn = solves(JOB / "resolve_16may.jsonl"), solves(JOB / "stage_logs" / "solves_stage3.jsonl")
    rso, rsn = re_shares(old, oldc), re_shares(new, newc)
    rows = []

    def add(c, s, metric, item, a, b):
        ch = ""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and a == a and b == b:
            ch = b - a
        rows.append(dict(country=c, scenario=s, metric=metric, item=item, value_16may=a, value_new=b, change=ch))

    for c in COUNTRIES:
        for s in SCENS:
            o, n = so.get((c, s), (None, None)), sn.get((c, s), (None, None))
            add(c, s, "solve status", "", o[0] or "not available", n[0] or "not available")
            add(c, s, "objective", "OFL_Cost / cost", o[1] if o[1] is not None else "not available",
                n[1] if n[1] is not None else "not available")
            for y in (2030, 2035, 2050):
                a = rso.get((c, s, y), float("nan"))
                b = rsn.get((c, s, y), float("nan"))
                add(c, s, "RE share", str(y), round(float(a), 6), round(float(b), 6))
                t = RE_TARGETS.get(s, {}).get(y)
                if t is not None:
                    add(c, s, "RE target met (2 pp tolerance)", f"{y} target {t:.2f}",
                        "yes" if a >= t - 0.02 else "no", "yes" if b >= t - 0.02 else "no")
            for res, lab in ((old, "16may"), (new, "new")):
                pass
            sv_o = old["ShareValidation"]; sv_n = new["ShareValidation"]
            for st in ("PASS", "WARN", "FAIL"):
                add(c, s, "share validation", st,
                    int(((sv_o.Country == c) & (sv_o.Scenario == s) & (sv_o.Status == st)).sum()),
                    int(((sv_n.Country == c) & (sv_n.Scenario == s) & (sv_n.Status == st)).sum()))
            for y in (2030, 2050):
                eo, en = old["AnnualEmissions"], new["AnnualEmissions"]
                add(c, s, "emissions (sum of AnnualEmissions)", str(y),
                    float(eo[(eo.Country == c) & (eo.Scenario == s) & (eo.Year == y)].Value.sum()),
                    float(en[(en.Country == c) & (en.Scenario == s) & (en.Year == y)].Value.sum()))
            nco, ncn = old["NewCapacity"], new["NewCapacity"]
            f = lambda d: d[(d.Country == c) & (d.Scenario == s) & d.Technology.str.upper().str.startswith(("PP", "PWR"))]
            go = f(nco).groupby("Technology").Value.sum()
            gn = f(ncn).groupby("Technology").Value.sum()
            for t in sorted(set(go.index) | set(gn.index)):
                add(c, s, "new capacity summed over the horizon (GW)", t, float(go.get(t, 0.0)), float(gn.get(t, 0.0)))
    with open(JOB / "results_compare.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["country", "scenario", "metric", "item", "value_16may", "value_new",
                                           "change"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    df = pd.DataFrame(rows)
    # top five new capacity changes per country
    nc = df[df.metric.str.startswith("new capacity")].copy()
    nc["abs"] = pd.to_numeric(nc.change, errors="coerce").abs()
    top = nc.sort_values("abs", ascending=False).groupby("country").head(5).sort_values(["country", "abs"],
                                                                                         ascending=[True, False])
    top.drop(columns="abs").to_csv(JOB / "results_compare_top_newcap.csv", index=False, lineterminator="\n")
    print("rows", len(df))


if __name__ == "__main__":
    main()
