"""Command line of the check suite.

    py -I -m gates --point <b1|final|results> [--models ...] [--scenarios ...] [--out DIR]
                   [--data-dir DIR] [--b1-data-dir DIR] [--results-file FILE] [--jobs N]

b1       every Executables/<scenario>_0/<scenario>_0.txt the A2 and B1 compile wrote (the scenarios each model's
         configuration lists); the parsed values are also compared with B1_Output_Params/<scenario>.
final    every Executables/<stage3 folder>/<stage3 folder>.txt that stage3_apply.py and the emission cap wrote
         (models that Stage 3 patches, scenarios with a Stage 3 folder in the scenario catalogue).
results  the extracted results of a solved run (results_summary.csv format).
--data-dir reads the data files from a copy of the model folders (same relative paths) instead of the repository;
--b1-data-dir names where the compiled _0 files are, for the provenance of FINAL values (default: the data dir).
Writes gate_results.csv, gate_summary.csv and provenance.csv in --out and exits with 1 when any FAIL is found.
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from . import config as C
from . import gmpl
from .findings import row, write
from .layers import layer_b, layer_p, layer_s
from .results import layer_x
from .standard import (bau_differences, history_identity, layer_r_scenario, load_difference_register,
                       load_value_registers, provenance, published_as_maximum, renewable_rule_outputs,
                       value_register_check)
from .view import View

ROOT = Path(__file__).resolve().parents[1]


def data_file(base: Path, m, scen, point, finals):
    d = base / m["path"] / "Executables"
    if point == "b1":
        return d / f"{scen}_0" / f"{scen}_0.txt"
    f = finals[scen]
    return d / f / f"{f}.txt"


def b1_consistency(m, scen, data, ctx, root, thr):
    """S0: the parsed data file holds the values of B1_Output_Params/<scenario> (the runner's own tables)."""
    folder = root / m["path"] / "B1_Output_Params" / scen
    if not folder.exists():
        return
    tol = thr["b1_compare_tol"]
    for f in sorted(folder.glob("*.csv")):
        name = f.stem
        if name not in data.dims:
            continue
        p = data.params.get(name)
        dims = data.dims[name]
        bad, first, n = 0, None, 0
        seen = set()
        for r in C.read_csv(f):
            key = tuple(str(r.get(s, "")).strip() for s in dims)
            key = tuple(k[:-2] if k.endswith(".0") and k[:-2].isdigit() else k for k in key)
            try:
                want = float(r["Value"])
            except (KeyError, ValueError):
                continue
            n += 1
            seen.add(key)
            got = p.get(key) if p is not None else None
            if got is None or abs(got - want) > tol * max(abs(want), abs(got)) + thr["abs_tol"]:
                bad += 1
                first = first or (key, want, got)
        extra = 0
        if p is not None:
            for k, val in p.values.items():
                if k not in seen and (p.default is None or val != p.default):
                    extra += 1
                    first = first or (k, None, val)
        if bad or extra:
            k, want, got = first
            yield row(ctx, "S0", "FAIL", parameter=name, values=f"B1_Output_Params {want} vs data file {got} at {k}",
                      message=f"data file differs from B1_Output_Params/{scen}/{name}.csv: {bad} of {n} table rows "
                              f"differ, {extra} data values not in the table")


def check_model(args):
    m, point, scen_filter, data_dir, b1_dir, root = args
    thr = C.thresholds(root)
    finals = C.final_folder(root)
    base = m.get("base_scenario") or "BAU"
    out, prov, info = [], [], {}
    ctx0 = dict(model=m["model"], point=point, thr=thr, root=root, base=base)
    scen = [s for s in m["scenarios"].split("|") if s]
    if point == "final":
        if m["stage3"] != "yes":
            return out, prov, info
        scen = [s for s in scen if s in finals]
    if scen_filter:
        scen = [s for s in scen if s in scen_filter]
    dims = gmpl.model_dims(str(root / m["path"] / "OSeMOSYS_Model.txt"))
    datas, views = {}, {}
    t0 = time.time()
    for s in scen:
        ctx = dict(ctx0, scenario=s)
        f = data_file(data_dir, m, s, point, finals)
        if point == "b1" and not (root / m["path"] / "B1_Output_Params" / s).exists():
            out.append(row(ctx, "S7", "FAIL", message=f"scenario listed by the model configuration has no compiled "
                                                      f"folder B1_Output_Params/{s}"))
        if not f.exists():
            out.append(row(ctx, "S7", "FAIL", message=f"scenario listed by the model configuration has no data file "
                                                      f"{f.parent.name}/{f.name}"))
            continue
        try:
            d = gmpl.read_data(str(f), dims)
        except Exception as exc:  # a file the parser cannot read is a structural failure
            out.append(row(ctx, "S5", "FAIL", message=f"data file cannot be parsed: {exc}"))
            continue
        datas[s] = d
        for r in d.sets.get("REGION", []) or [""]:
            v = View(d, r, thr)
            views.setdefault(s, v)
            for layer in (layer_s, layer_b, layer_p, layer_r_scenario):
                out.extend(layer(v, ctx))
        if point == "b1":
            out.extend(b1_consistency(m, s, d, ctx, root, thr))
    info["parse_and_scenario_seconds"] = round(time.time() - t0, 1)
    if views:
        regs = load_value_registers(root, thr)
        diffreg, _ = load_difference_register(root, thr)
        out.extend(history_identity(m, views, dict(ctx0), m["stage3"] == "yes"))
        out.extend(bau_differences(m["path"], views, dict(ctx0), diffreg))
        if point == "b1":
            c = dict(ctx0)
            out.extend(value_register_check(m, views, c, regs, diffreg))
            info["r1_unchecked"] = c.get("_r1_unchecked", {}).get(m["path"], 0)
            out.extend(published_as_maximum(m, views, dict(ctx0), root))
        b1_views = None
        if point == "final":
            b1_views = {}
            for s in views:
                f = data_file(b1_dir, m, s, "b1", finals)
                if f.exists():
                    b1_views[s] = View(gmpl.read_data(str(f), dims), views[s].r, thr)
        c = dict(ctx0)
        out.extend(provenance(m, views, c, regs, b1_views, root))
        prov = c.get("_prov", [])
    info["seconds"] = round(time.time() - t0, 1)
    return out, prov, info


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gates")
    ap.add_argument("--point", required=True, choices=["b1", "final", "results"])
    ap.add_argument("--models", nargs="*", default=[])
    ap.add_argument("--scenarios", nargs="*", default=[])
    ap.add_argument("--out", default=".")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--data-dir", default="")
    ap.add_argument("--b1-data-dir", default="")
    ap.add_argument("--results-file", default="")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    thr = C.thresholds(root)
    t0 = time.time()
    rows, prov = [], []
    if a.point == "results":
        f = Path(a.results_file) if a.results_file else C.latest_job_file(root, thr["results_file"])
        ctx = dict(point="results", thr=thr, root=root)
        rows = list(layer_x(root, f, ctx, a.models, a.scenarios))
        print(f"results point: {f}")
    else:
        data_dir = Path(a.data_dir) if a.data_dir else root
        b1_dir = Path(a.b1_data_dir) if a.b1_data_dir else data_dir
        ms = [m for m in C.models(root) if not a.models or m["model"] in a.models]
        jobs = [(m, a.point, a.scenarios, data_dir, b1_dir, root) for m in ms]
        if a.jobs > 1:
            with ProcessPoolExecutor(max_workers=a.jobs) as ex:
                results = list(ex.map(check_model, jobs))
        else:
            results = [check_model(j) for j in jobs]
        for m, (r, p, info) in zip(ms, results):
            rows.extend(r)
            prov.extend(p)
            if info:
                print(f"{m['model']}: {info}", flush=True)
        if a.point == "final":
            rows.extend(renewable_rule_outputs(root, dict(point="final", thr=thr, root=root)))
    write(rows, out / "gate_results.csv", out / "gate_summary.csv")
    if prov:
        import csv
        with open(out / "provenance.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(prov[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(prov)
    nf = sum(1 for r in rows if r["class"] == "FAIL")
    nw = sum(1 for r in rows if r["class"] == "WARN")
    print(f"point {a.point}: {nf} FAIL, {nw} WARN in {time.time() - t0:.1f}s -> {out / 'gate_results.csv'}")
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
