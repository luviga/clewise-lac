"""Layer R: the standard and nothing invisible. Per scenario (R2, R3 data part, R8) and per model across its
scenarios (R1, R4, R5, R6, R7), plus the pipeline rule outputs (R3)."""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from . import config as C
from .findings import row

FAIL, WARN = "FAIL", "WARN"
_SKIP_IDX = {"REGION"}


def _yr(s):
    return s if re.fullmatch(r"\d{4}", str(s)) else ""


def _key_parts(dims, key):
    """(technology, fuel, emission, year, timeslice, other) of an index tuple."""
    out = {"TECHNOLOGY": "", "FUEL": "", "EMISSION": "", "YEAR": "", "TIMESLICE": ""}
    other = []
    for s, k in zip(dims, key):
        if s in out:
            out[s] = k
        elif s not in _SKIP_IDX:
            other.append(f"{s}={k}")
    return out["TECHNOLOGY"], out["FUEL"], out["EMISSION"], out["YEAR"], out["TIMESLICE"], ";".join(other)


def _years_text(ys):
    ys = sorted(set(ys), key=lambda x: int(x) if x else 0)
    if not ys or ys == [""]:
        return ""
    return ys[0] if len(ys) == 1 else f"{ys[0]}-{ys[-1]} ({len(ys)} years)"


# ---------------------------------------------------------------------------------------------- per scenario
def layer_r_scenario(v, ctx):
    thr = ctx["thr"]
    allowed = [m for m in str(thr.get("penalty_allowed_models", "") or "").split("|") if m]
    # R2
    if ctx["model"] not in allowed:
        nz = defaultdict(list)
        for (e, y), val in v.explicit("EmissionsPenalty").items():
            if val != 0:
                nz[e].append((y, val))
        dflt = v.default("EmissionsPenalty") or 0.0
        if dflt != 0:
            yield row(ctx, "R2", FAIL, parameter="EmissionsPenalty", values=f"default {dflt:g}",
                      message="the declared default of EmissionsPenalty is not 0")
        for e, items in nz.items():
            yield row(ctx, "R2", FAIL, parameter="EmissionsPenalty", emission=e, year=sorted(items)[0][0],
                      values=f"{len(items)} non-zero cells, first {sorted(items)[0][1]:g}",
                      message=f"non-zero emission penalty in {_years_text([i[0] for i in items])}")
    # R3, data part: REMinProductionTarget in [0, 1]
    for (y,), val in v.explicit("REMinProductionTarget").items():
        if val < 0 or val > 1:
            yield row(ctx, "R3", FAIL, parameter="REMinProductionTarget", year=y, values=f"{val:g}",
                      message="renewable target outside [0, 1] in the data file")
    # R8
    nolim = thr["no_limit_at_or_above"]
    has_input = {t for (t, y), by in v.iar.items() if any(any(x > 0 for x in m.values()) for m in by.values())}
    has_output = {t for (t, y), by in v.oar.items() if any(any(x > 0 for x in m.values()) for m in by.values())}
    for t in v.techs:
        if t in has_input or t not in has_output:
            continue
        limited = False
        for y in v.years:
            for name in ("TotalAnnualMaxCapacity", "TotalAnnualMaxCapacityInvestment",
                         "TotalTechnologyAnnualActivityUpperLimit"):
                x = v.val(name, t, y)
                if x is not None and x < nolim:
                    limited = True
            if limited:
                break
        mpu = v.val("TotalTechnologyModelPeriodActivityUpperLimit", t)
        if limited or (mpu is not None and mpu < nolim):
            continue
        cc = any((v.val("CapitalCost", t, y) or 0) != 0 for y in v.years)
        vc = any(val != 0 for (tt, m, y), val in v.explicit("VariableCost").items() if tt == t)
        if (v.default("VariableCost") or 0) != 0:
            vc = True
        if cc or vc:
            continue
        yield row(ctx, "R8", WARN, technology=t, fuel="|".join(sorted({f for y in v.years for f in v.outputs(t, y)})),
                  message="technology without input fuel, without a limit on activity or capacity, and with zero "
                          "capital and variable cost (a free unlimited source)")


# ---------------------------------------------------------------------------------------------- per model
def history_identity(model, views, ctx, stage3_model):
    """R4: inputs of years up to the history cut-off identical across the scenarios of a model."""
    thr = ctx["thr"]
    last = int(C.controller(ctx["root"], thr["history_end_year_key"]))
    nolim = thr["no_limit_at_or_above"]
    scen = list(views)
    if len(scen) < 2:
        return
    base = ctx["base"] if ctx["base"] in views else scen[0]
    vb = views[base]
    dims = vb.d.dims
    cls = WARN if (ctx["point"] == "b1" and stage3_model) else FAIL
    note = (" (the pipeline equalises history later with the scenario_rules.py history rule; checked as FAIL at "
            "the final point)") if cls == WARN else ""
    for name, sets in dims.items():
        if "YEAR" not in sets:
            continue
        yi = sets.index("YEAR")
        for sc in scen:
            if sc == base:
                continue
            vs = views[sc]
            pb, ps = vb.d.params.get(name), vs.d.params.get(name)
            if pb is None and ps is None:
                continue
            keys = set(pb.values if pb else {}) | set(ps.values if ps else {})
            grp = defaultdict(list)
            for k in keys:
                if int(k[yi]) > last:
                    continue
                a = pb.get(k, 0.0) if pb else 0.0
                b = ps.get(k, 0.0) if ps else 0.0
                if a >= nolim and b >= nolim:
                    continue  # two "no limit" sentinels
                if abs(a - b) > thr["rel_tol"] * max(abs(a), abs(b)) + thr["abs_tol"]:
                    grp[k[:yi] + k[yi + 1:]].append((k[yi], a, b))
            for k, items in grp.items():
                items.sort()
                full = k[:yi] + (items[0][0],) + k[yi:]
                t, f, e, y, l, other = _key_parts(sets, full)
                c2 = dict(ctx, scenario=sc)
                yield row(c2, "R4", cls, parameter=name, technology=t, fuel=f, emission=e, year=items[0][0], timeslice=l,
                          values=f"{base} {items[0][1]:.6g} vs {sc} {items[0][2]:.6g}" + (f" [{other}]" if other else ""),
                          message=f"history input differs from {base} in {_years_text([i[0] for i in items])}{note}")


def load_difference_register(root, thr):
    f = C.latest_job_file(root, thr["register_scenario_difference"])
    reg = defaultdict(list)
    if f is None:
        return reg, None
    for r in C.read_csv(f):
        reg[(r["model"], r["parameter"], r["scenario"], r.get("technology", ""), r.get("fuel", ""),
             r.get("emission", ""))].append((int(r["first_year"]) if r["first_year"] else 0,
                                            int(r["last_year"]) if r["last_year"] else 9999))
    return reg, f


def bau_differences(model_path, views, ctx, reg):
    """R5: every input of a policy scenario that differs from the base scenario has a register row."""
    thr = ctx["thr"]
    nolim = thr["no_limit_at_or_above"]
    base = ctx["base"]
    if base not in views:
        return
    vb = views[base]
    for sc, vs in views.items():
        if sc == base:
            continue
        for name, sets in vb.d.dims.items():
            pb, ps = vb.d.params.get(name), vs.d.params.get(name)
            if pb is None and ps is None:
                continue
            keys = set(pb.values if pb else {}) | set(ps.values if ps else {})
            yi = sets.index("YEAR") if "YEAR" in sets else None
            grp = defaultdict(list)
            for k in keys:
                a = pb.get(k, 0.0) if pb else 0.0
                b = ps.get(k, 0.0) if ps else 0.0
                if a >= nolim and b >= nolim:
                    continue  # two "no limit" sentinels
                if abs(a - b) > thr["rel_tol"] * max(abs(a), abs(b)) + thr["abs_tol"]:
                    gk = k[:yi] + k[yi + 1:] if yi is not None else k
                    grp[gk].append((k[yi] if yi is not None else "", a, b, k))
            for gk, items in grp.items():
                items.sort()
                t, f, e, y, l, other = _key_parts(sets, items[0][3])
                spans = reg.get((model_path, name, sc, t, f, e), [])
                missing = [i for i in items if not any(a <= int(i[0] or 0) <= b or not i[0] for a, b in spans)]
                if not missing:
                    continue
                c2 = dict(ctx, scenario=sc)
                yield row(c2, "R5", FAIL, parameter=name, technology=t, fuel=f, emission=e, year=missing[0][0],
                          timeslice=l, values=f"{base} {missing[0][1]:.6g} vs {sc} {missing[0][2]:.6g}"
                          + (f" [{other}]" if other else ""),
                          message=f"input differs from {base} with no row in the scenario difference register "
                                  f"({len(missing)} cells, {_years_text([i[0] for i in missing])})")


def published_as_maximum(model_row, views, ctx, root):
    """R6: a published target loaded into a Tech_Adoption row must not carry a maximum restriction."""
    thr = ctx["thr"]
    f = C.latest_job_file(root, thr["register_published"])
    if f is None:
        return
    path = model_row["path"]
    want = defaultdict(set)
    for r in C.read_csv(f):
        if r.get("result") != "loaded":
            continue
        mi = r.get("model_input", "")
        if not mi.startswith(path + "/"):
            continue
        parts = mi[len(path) + 1:].split()
        if len(parts) >= 4 and parts[1] == "Tech_Adoption":
            want[(parts[2], parts[3])].add(r["value_id"])
    if not want:
        return
    import pandas as pd
    wb = root / path / "B1_Scenario_Config.xlsx"
    ta = pd.read_excel(wb, sheet_name="Tech_Adoption")
    for (sc, tech), ids in sorted(want.items()):
        sel = ta[(ta["Scenario"].astype(str) == sc) & (ta["Tech_Set"].astype(str) == tech)]
        if sel.empty:
            continue
        rt = str(sel.iloc[0].get("Restriction_Type", ""))
        if "max" not in rt.lower():
            continue
        up = ""
        if sc in views:
            nolim = thr["no_limit_at_or_above"]
            for pname in ("TotalAnnualMaxCapacity", "TotalTechnologyAnnualActivityUpperLimit"):
                ex = views[sc].explicit(pname)
                ys = sorted(y for (t, y), val in ex.items() if t == tech and val < nolim)
                if ys:
                    up += f"; the data file carries {pname} for {tech} in {_years_text(ys)}"
        c2 = dict(ctx, scenario=sc)
        yield row(c2, "R6", FAIL, parameter="Tech_Adoption Restriction_Type", technology=tech,
                  values=f"Restriction_Type {rt}", message=f"published target ({', '.join(sorted(ids))}) is written "
                  f"with a maximum (B1_Scenario_Config.xlsx Tech_Adoption, row {sel.index[0] + 2}){up}")


def renewable_rule_outputs(root, ctx):
    """R3: rule outputs read by the pipeline lie in [0, 1]."""
    f = root / "_STAGE1_OUTPUT" / "RENEWABLE_TARGETS.csv"
    if f.exists():
        for r in C.read_csv(f):
            v = float(r["value"])
            if v < 0 or v > 1:
                c2 = dict(ctx, model=r["country"], scenario=r["scenario"])
                yield row(c2, "R3", FAIL, parameter="REMinProductionTarget", year=r["year"], values=f"{v:g}",
                          message=f"_STAGE1_OUTPUT/RENEWABLE_TARGETS.csv value outside [0, 1] ({r.get('derivation', '')})")
    import pandas as pd
    for ctl in ("_STAGE1_OUTPUT", "_STAGE2_OUTPUT"):
        p = root / ctl / "CONTROLLER_NEW_SCENARIOS.xlsx"
        if not p.exists():
            continue
        for sheet in ("CURRENT_SHARES", "TARGET_SHARES"):
            try:
                df = pd.read_excel(p, sheet_name=sheet)
            except ValueError:
                continue
            ycols = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
            for _, r in df.iterrows():
                bad = [(c, r[c]) for c in ycols if pd.notna(r[c]) and (r[c] < 0 or r[c] > 1)]
                if bad:
                    c2 = dict(ctx, model=r["Country"], scenario=r["Scenario"])
                    yield row(c2, "R3", FAIL, parameter=sheet, technology=r["Tech"], year=str(bad[0][0]),
                              values=f"{bad[0][1]:g}", message=f"{ctl}/CONTROLLER_NEW_SCENARIOS.xlsx {sheet} share outside "
                              f"[0, 1] in {len(bad)} years")


# ---------------------------------------------------------------------------------------------- value registers
def load_value_registers(root, thr):
    rows = []
    for f in C.job_files(root, thr["register_value"]):
        for i, r in enumerate(C.read_csv(f), start=2):
            r["_where"] = f"{f.parent.name}/{f.name} line {i}"
            rows.append(r)
    return rows


def _register_items(r, v, scenarios):
    """(scenarios, technology, emission, fuel, years) a register row names, or None when it names no model cell."""
    raw = str(r.get("tech", ""))
    toks = [x.strip() for x in re.split(r"[|;]", raw) if x.strip() and x.strip() != "nan"]
    sc = [x for x in toks if x in scenarios]
    tech = [x for x in toks if x in v.techs]
    emi = [x for x in toks if x in v.emissions]
    fuel = [x for x in toks if x in v.fuels]
    if len(sc) + len(tech) + len(emi) + len(fuel) < len(toks):
        return None  # the row names something that is not a set member of this model (a group or a label)
    y = str(r.get("year", ""))
    m = re.fullmatch(r"(?:v_)?(\d{4})", y)
    if m:
        years = [m.group(1)]
    elif y in ("", "nan"):
        years = list(v.years)
    else:
        return None
    return (sc or list(scenarios)), (tech[0] if tech else ""), (emi[0] if emi else ""), (fuel[0] if fuel else ""), years


def _index(v, name):
    """{(technology, emission, fuel, year): [values]} of one parameter of one region, with every partial key."""
    key = ("_idx", name)
    if key in v._cache:
        return v._cache[key]
    p = v.d.params.get(name)
    dims = v.d.dims.get(name, [])
    idx = defaultdict(list)
    if p is not None:
        for k, val in p.values.items():
            parts = dict(zip(dims, k))
            if parts.get("REGION", v.r) != v.r:
                continue
            t, e, f, y = parts.get("TECHNOLOGY", ""), parts.get("EMISSION", ""), parts.get("FUEL", ""), parts.get("YEAR", "")
            for tt in {t, ""}:
                for ee in {e, ""}:
                    for ff in {f, ""}:
                        idx[(tt, ee, ff, y)].append(val)
    v._cache[key] = idx
    return idx


def value_register_check(model_row, views, ctx, regs, diffreg):
    """R1: a register value that a merged job wrote (before -> after) is in the compiled file of every scenario that
    should carry it. The test is for staleness and stays sound when the compiler changes units: a cell FAILs when
    the compiled file still holds the register's `before` value (and before differs from after); a cell holding
    `after` passes; any other value (a unit conversion or interpolation of the compiler) is counted as unchecked.
    A row without a scenario belongs to every scenario, except a scenario whose difference from the base is in the
    scenario difference register (a policy measure that replaces it)."""
    thr = ctx["thr"]
    tol = thr.get("r1_value_tol", 1e-3)
    path = model_row["path"]
    scen = list(views)
    out = defaultdict(list)
    unchecked = 0

    def near(x, a):
        return abs(x - a) <= tol * max(abs(a), abs(x)) + thr["abs_tol"]

    for r in regs:
        if r.get("model") != path:
            continue
        name = r.get("parameter", "")
        any_v = views[scen[0]]
        if name not in any_v.d.dims:
            continue
        try:
            after = float(r.get("after", ""))
            before = float(r.get("before", ""))
        except ValueError:
            unchecked += 1
            continue
        if near(before, after):
            continue
        marker = str(thr.get("r1_conversion_marker", "") or "")
        if marker and marker in str(r.get("unit", "")):
            unchecked += 1  # the compiler converts the workbook unit: compiled and register values differ by design
            continue
        it = _register_items(r, any_v, scen)
        if it is None:
            unchecked += 1
            continue
        scs, tech, emi, fuel, years = it
        named_scen = any(x in scen for x in str(r.get("tech", "")).split("|"))
        dims = any_v.d.dims[name]
        for sc in scs:
            if sc not in views:
                continue
            if not named_scen and sc != ctx["base"] and diffreg.get((path, name, sc, tech, fuel, emi)):
                continue
            v = views[sc]
            p = v.d.params.get(name)
            if p is None:
                continue
            idx = _index(v, name)
            for y in years:
                vals = idx.get((tech, emi, fuel, y if "YEAR" in dims else ""), [])
                if not vals and p.default is not None:
                    vals = [p.default]
                if any(near(x, after) for x in vals):
                    continue
                if any(near(x, before) for x in vals):
                    out[(sc, name, tech, emi, fuel)].append((y, before, after, r["_where"]))
                else:
                    unchecked += 1
    for (sc, name, tech, emi, fuel), items in out.items():
        items.sort()
        c2 = dict(ctx, scenario=sc)
        y, b, a, where = items[0]
        yield row(c2, "R1", FAIL, parameter=name, technology=tech, emission=emi, fuel=fuel, year=y,
                  values=f"compiled {b:g} = register before; register after {a:g}",
                  message=f"compiled file still holds the value the register replaced, in "
                          f"{_years_text([i[0] for i in items])} ({where})")
    ctx.setdefault("_r1_unchecked", {})[path] = unchecked


# ---------------------------------------------------------------------------------------------- provenance
def provenance(model_row, views, ctx, regs, b1_views, root):
    """R7: origin of every limit value that differs from its default. Yields WARN rows for UNTRACED values and
    returns provenance rows through ctx['_prov']."""
    thr = ctx["thr"]
    params = str(thr["limit_parameters"]).split("|")
    patched = set(str(thr["stage3_patched_parameters"]).split("|"))
    nolim = thr["no_limit_at_or_above"]
    path = model_row["path"]
    last = int(C.controller(root, thr["history_end_year_key"]))
    hyd = {r["technology"] for r in C.read_csv(root / "config" / "scenarios" / "technology_types.csv")
           if r["group"] == "hydrogen"}
    reg_idx = defaultdict(list)
    for r in regs:
        if r.get("model") == path and r.get("parameter") in params:
            try:
                reg_idx[r["parameter"]].append(([x.strip() for x in re.split(r"[|;]", str(r.get("tech", "")))],
                                                str(r.get("year", "")),
                                                float(r["after"]), r["_where"]))
            except ValueError:
                pass
    wb = root / path / "B1_Scenario_Config.xlsx"
    # rows of B1_Scenario_Config.xlsx that name a technology, with the numbers they hold (cells and ';' lists)
    sheet_rows = defaultdict(list)
    try:
        import pandas as pd
        from openpyxl.utils import get_column_letter
        xl = pd.read_excel(wb, sheet_name=None, header=None)
        for s, df in xl.items():
            for i, rr in df.iterrows():
                names, nums = [], []
                for j, x in enumerate(rr.values):
                    if isinstance(x, str) and x.strip():
                        names.append(x.strip())
                        for part in x.split(";"):
                            try:
                                nums.append((float(part), j))
                            except ValueError:
                                pass
                    elif isinstance(x, (int, float)) and x == x:
                        nums.append((float(x), j))
                if nums:
                    for nm in names:
                        for tok in re.split(r"[|;]", nm):
                            sheet_rows[tok.strip()].append((s, i + 1, nums))
    except Exception:
        get_column_letter = None
    prov = ctx.setdefault("_prov", [])
    caps = root / "_STAGE3_RESULTS" / "EMISSION_CAPS.csv"
    for sc, v in views.items():
        a2 = {}
        for name in params:
            f = root / path / "A2_Output_Params" / sc / f"{name}.csv"
            if f.exists():
                for r in C.read_csv(f):
                    a2[(name, r.get("TECHNOLOGY", ""), r.get("EMISSION", ""), r.get("YEAR", ""))] = r.get("Value")
        bv = b1_views.get(sc) if b1_views else None
        bb = b1_views.get(ctx["base"]) if b1_views else None
        agg = defaultdict(list)
        for name in params:
            p = v.d.params.get(name)
            if p is None:
                continue
            dims = v.d.dims[name]
            for k, val in p.values.items():
                if p.default is not None and val == p.default:
                    continue
                if name.endswith(("Max", "MaxCapacity", "MaxCapacityInvestment", "UpperLimit", "EmissionLimit")) \
                        and val >= nolim:
                    continue
                t, f, e, y, l, other = _key_parts(dims, k)
                kind, origin = "UNTRACED", ""
                if ctx["point"] == "final" and bv is not None:
                    pb = bv.d.params.get(name)
                    b1val = pb.get(k) if pb else None
                    if b1val is None or abs(b1val - val) > thr["rel_tol"] * abs(val) + thr["abs_tol"]:
                        if t in hyd and name.startswith("TotalTechnologyAnnualActivity"):
                            kind, origin = "rule", "scenario_rules.py hydrogen rule"
                        elif y and int(y) <= last and sc != ctx["base"] and bb is not None and \
                                bb.d.params.get(name) and abs((bb.d.params[name].get(k) or 0) - val) <= thr["abs_tol"]:
                            kind, origin = "rule", "scenario_rules.py history rule"
                        elif name == "AnnualEmissionLimit":
                            kind, origin = "rule", "stage3_emission_cap.py cap (_STAGE3_RESULTS/EMISSION_CAPS.csv)"
                        elif name in patched:
                            kind, origin = "rule", "stage3_apply.py controller rule (_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx)"
                if kind == "UNTRACED":
                    for toks, ry, after, where in reg_idx.get(name, []):
                        if t and t not in toks:
                            continue
                        if e and e not in toks:
                            continue
                        mm = re.fullmatch(r"(?:v_)?(\d{4})", ry)
                        if mm and mm.group(1) != y:
                            continue
                        if abs(after - val) <= 1e-3 * max(abs(val), abs(after)) + thr["abs_tol"]:
                            kind, origin = "register", where
                            break
                if kind == "UNTRACED":
                    a = a2.get((name, t, e, y))
                    try:
                        if a is not None and abs(float(a) - val) <= 1e-6 * max(abs(val), 1.0):
                            kind, origin = "A2 table", f"A2_Output_Params/{sc}/{name}.csv (compiled by "\
                                                       f"{model_row['a2_compiler']} from the A1 workbooks)"
                    except ValueError:
                        pass
                if kind == "UNTRACED" and t and t in sheet_rows:
                    for s_, i, nums in sheet_rows[t]:
                        hit = next((j for x, j in nums if abs(x - val) <= 1e-4 * max(abs(val), abs(x)) + thr["abs_tol"]),
                                   None)
                        if hit is not None:
                            kind = "workbook"
                            origin = (f"B1_Scenario_Config.xlsx sheet {s_} cell {get_column_letter(hit + 1)}{i} "
                                      f"(read by {model_row['b1_runner']})")
                            break
                agg[(name, t, f, e, kind, origin)].append((y, val))
        for (name, t, f, e, kind, origin), items in agg.items():
            items.sort()
            prov.append(dict(model=ctx["model"], scenario=sc, point=ctx["point"], parameter=name, technology=t,
                             fuel=f, emission=e, years=_years_text([i[0] for i in items]), cells=len(items),
                             first_value=items[0][1], origin_kind=kind, origin=origin))
            if kind == "UNTRACED":
                c2 = dict(ctx, scenario=sc)
                yield row(c2, "R7", WARN, parameter=name, technology=t, fuel=f, emission=e, year=items[0][0],
                          values=f"{items[0][1]:.6g}", message=f"UNTRACED: {len(items)} cells in "
                          f"{_years_text([i[0] for i in items])} with no workbook, rule or register origin")
