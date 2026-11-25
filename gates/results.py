"""Layer X: checks on extracted results (results_summary.csv format of the solved runs)."""
from __future__ import annotations

from collections import defaultdict

from . import config as C
from .findings import row

FAIL, WARN = "FAIL", "WARN"


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def layer_x(root, results_file, ctx, models=None, scenarios=None):
    thr = ctx["thr"]
    rows = C.read_csv(results_file)
    by = defaultdict(dict)
    for r in rows:
        if models and r["country"] not in models:
            continue
        if scenarios and r["scenario"] not in scenarios:
            continue
        by[(r["country"], r["scenario"])][int(r["year"])] = r
    cols = rows[0].keys() if rows else []
    emi_cols = [c for c in str(thr["x1_emissions_columns"]).split("|") if c in cols]
    gen_cols = [c for c in cols if c.startswith(str(thr["x1_generation_prefix"]))]
    cap_cols = [c for c in cols if c.startswith(str(thr["x1_capacity_prefix"]))]
    # X1
    for (c, sc), yrs in sorted(by.items()):
        ys = sorted(yrs)
        c2 = dict(ctx, model=c, scenario=sc)
        for a, b in zip(ys, ys[1:]):
            for col in emi_cols:
                x, y = _f(yrs[a][col]), _f(yrs[b][col])
                if x and y is not None and abs(y - x) > thr["x1_emissions_jump"] * abs(x):
                    yield row(c2, "X1", WARN, parameter=col, year=str(b), values=f"{a} {x:g} -> {b} {y:g}",
                              message=f"energy emissions change by {100 * (y - x) / x:.1f} percent in one year")
            for col in gen_cols:
                x, y = _f(yrs[a][col]) or 0.0, _f(yrs[b][col]) or 0.0
                if max(x, y) >= thr["x1_generation_floor"] and abs(y - x) > thr["x1_generation_jump"] * max(x, 1e-12):
                    yield row(c2, "X1", WARN, parameter=col, year=str(b), values=f"{a} {x:g} -> {b} {y:g}",
                              message="generation of the group changes by more than the threshold in one year")
            for col in cap_cols:
                x, y = _f(yrs[a][col]) or 0.0, _f(yrs[b][col]) or 0.0
                if abs(y - x) > thr["x1_capacity_jump"]:
                    yield row(c2, "X1", WARN, parameter=col, year=str(b), values=f"{a} {x:g} -> {b} {y:g}",
                              message="new capacity of the group changes by more than the threshold in one year")
    # X2: loaded targets met (renewable share and energy emission reduction levers of scenario_values.csv)
    tol = thr["x2_tolerance"]
    targets = defaultdict(list)
    for r in C.read_csv(root / "inputs" / "scenarios" / "scenario_values.csv"):
        targets[(r["country"], r["scenario"], r["lever"])].append((int(r["year"]), float(r["value"]), r.get("value_id", "")))
    for (c, sc, lever), ts in targets.items():
        if (c, sc) not in by:
            continue
        ts.sort()
        yrs = by[(c, sc)]
        c2 = dict(ctx, model=c, scenario=sc)
        if lever == "renewable_share":
            for y in sorted(yrs):
                held = [t for t in ts if t[0] <= y]
                if not held:
                    continue
                ty, tv, vid = held[-1]
                got = _f(yrs[y].get("renewable_share"))
                if got is not None and got < tv - tol:
                    yield row(c2, "X2", FAIL, parameter="renewable_share", year=str(y),
                              values=f"result {got:g} < target {tv:g}",
                              message=f"renewable share target {vid or ''} (from {ty}, held after) not met")
        elif lever == "energy_emission_reduction_vs_bau":
            base = by.get((c, "BAU"), {})
            for ty, r_, vid in ts:
                e = _f(yrs.get(ty, {}).get(emi_cols[0])) if emi_cols else None
                b = _f(base.get(ty, {}).get(emi_cols[0])) if emi_cols else None
                if e is None or b is None:
                    continue
                cap = b * (1 - r_)
                if e > cap + tol * abs(cap):
                    yield row(c2, "X2", FAIL, parameter=emi_cols[0], year=str(ty),
                              values=f"result {e:g} > BAU {b:g} x (1 - {r_:g}) = {cap:g}",
                              message="energy emission reduction against BAU not met")
    # X3: history identical across scenarios
    last = int(C.controller(root, thr["history_end_year_key"]))
    xcols = [c for c in str(thr["x3_columns"]).split("|") if c in cols]
    countries = sorted({c for c, _ in by})
    for c in countries:
        base = by.get((c, "BAU"))
        if not base:
            continue
        for (cc, sc), yrs in sorted(by.items()):
            if cc != c or sc == "BAU":
                continue
            c2 = dict(ctx, model=c, scenario=sc)
            for y in sorted(yrs):
                if y > last or y not in base:
                    continue
                for col in xcols:
                    a, b = _f(base[y].get(col)), _f(yrs[y].get(col))
                    if a is None or b is None:
                        continue
                    scale = 100.0 if col.endswith("share") and max(abs(a), abs(b)) <= 1 else 1.0
                    if abs(a - b) * scale > thr["x3_tolerance"]:
                        yield row(c2, "X3", WARN, parameter=col, year=str(y), values=f"BAU {a:g} vs {sc} {b:g}",
                                  message="solved history differs from BAU although history inputs are identical")
