"""Checks of layers S (structure), B (pairs of limits) and P (limits pushed along the chain) on one region of one
parsed data file. Each function yields finding dicts (see findings.row). FAIL findings use only bounds that the
model's constraints imply (view.py); everything else is a WARN."""
from __future__ import annotations

from collections import defaultdict

from .findings import row

FAIL, WARN = "FAIL", "WARN"


def _years_text(years):
    ys = sorted(years, key=int)
    return ys[0] if len(ys) == 1 else f"{ys[0]}-{ys[-1]} ({len(ys)} years)"


# ====================================================================== layer S
def reachable(v, y, use_limits=False, act=None):
    """Fuels the system can deliver in year y, built up from technology modes with no input fuel (least fixed
    point). With use_limits, a mode counts only when its technology may run (largest activity above 0)."""
    avail = set()
    alive = set()
    changed = True
    while changed:
        changed = False
        for t in v.techs:
            if use_limits and act[(t, y)][1] <= 0:
                continue
            for m in v.modes or ["1"]:
                if (t, m) in alive:
                    continue
                if all(f in avail for f in v.mode_inputs(t, m, y)):
                    alive.add((t, m))
                    for f in v.mode_outputs(t, m, y):
                        if f not in avail:
                            avail.add(f)
                            changed = True
                    changed = True
    return avail, alive


def _on_cycle(v, y, dead_fuels):
    """Fuels among dead_fuels that lie on or below a cycle of dead fuels (a cycle with gains could in principle
    produce a fuel from nothing, so a FAIL there would not be sound)."""
    g = defaultdict(set)
    for t in v.techs:
        for m in v.modes or ["1"]:
            ins = [f for f in v.mode_inputs(t, m, y) if f in dead_fuels]
            outs = [f for f in v.mode_outputs(t, m, y) if f in dead_fuels]
            for a in ins:
                g[a].update(outs)
    on = set()
    color = {}

    def dfs(n, stack):
        color[n] = 1
        stack.append(n)
        for nb in g[n]:
            if color.get(nb) == 1:
                on.update(stack[stack.index(nb):])
            elif color.get(nb) is None:
                dfs(nb, stack)
        stack.pop()
        color[n] = 2

    for n in list(g):
        if color.get(n) is None:
            dfs(n, [])
    # everything reachable from a cycle fuel
    out = set(on)
    todo = list(on)
    while todo:
        n = todo.pop()
        for nb in g[n]:
            if nb not in out:
                out.add(nb)
                todo.append(nb)
    return out


def layer_s(v, ctx):
    act = v.own_activity_bounds()
    s1, s2, s3, s4 = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    for y in v.years:
        demanded = {f for f in v.fuels if v.demand(f, y) > 0}
        avail, _ = reachable(v, y)
        dead = set(v.fuels) - avail
        cyc = _on_cycle(v, y, dead) if dead & demanded else set()
        for f in demanded - avail:
            s1[(f, FAIL if f not in cyc else WARN)].append(y)
        producers = defaultdict(set)
        users = defaultdict(set)
        for t in v.techs:
            for f in v.outputs(t, y):
                producers[f].add(t)
            for f in v.inputs(t, y):
                users[f].add(t)
        for f, us in users.items():
            if producers.get(f):
                continue
            for t in us:
                lo = act[(t, y)][0]
                forced_act = lo > 0 and v.min_ratio(v.iar, t, f, y) > 0
                forced_cap = (v.val("TotalAnnualMinCapacity", t, y) or 0) > 0 or \
                             (v.val("TotalAnnualMinCapacityInvestment", t, y) or 0) > 0
                cls = FAIL if forced_act else WARN
                s2[(t, f, cls, "activity lower limit" if forced_act else
                    ("minimum capacity or investment" if forced_cap else "not forced"))].append(y)
        rtag = {f for f in v.fuels if (v.val("RETagFuel", f, y) or 0) > 0}
        mtag = {f for f in v.fuels if (v.val("ReserveMarginTagFuel", f, y) or 0) > 0}
        for f in producers:
            if f not in demanded and f not in users and f not in rtag and f not in mtag:
                s3[f].append(y)
        # S4: forced technology whose whole upstream chain may not run
        alive_fuels, alive = reachable(v, y, use_limits=True, act=act)
        dead2 = set(v.fuels) - alive_fuels
        cyc2 = None
        for t in v.techs:
            if act[(t, y)][0] <= 0:
                continue
            if any((t, m) in alive for m in v.modes or ["1"]):
                continue
            if act[(t, y)][1] <= 0:
                continue  # its own limits already say 0; that is B3 or B8
            if cyc2 is None:
                cyc2 = _on_cycle(v, y, dead2)
            missing = [f for f in v.inputs(t, y) if f in dead2]
            cls = WARN if any(f in cyc2 for f in missing) else FAIL
            s4[(t, "|".join(sorted(missing)), cls)].append(y)
    for (f, cls), ys in s1.items():
        yield row(ctx, "S1", cls, fuel=f, year=ys[0], values=f"demand {v.demand(f, ys[0]):.6g}",
                  message=f"fuel with demand is not reachable from any technology without input fuel in "
                          f"{_years_text(ys)}" + ("" if cls == FAIL else " (a cycle of unreachable fuels lies upstream)"))
    for (t, f, cls, why), ys in s2.items():
        yield row(ctx, "S2", cls, technology=t, fuel=f, year=ys[0], parameter="InputActivityRatio",
                  message=f"input fuel has no producer in {_years_text(ys)}; consumer {why}")
    for f, ys in s3.items():
        yield row(ctx, "S3", WARN, fuel=f, year=ys[0], parameter="OutputActivityRatio",
                  message=f"fuel produced but neither demanded, used nor tagged in {_years_text(ys)}")
    for (t, fs, cls), ys in s4.items():
        lo = act[(t, ys[0])][0]
        yield row(ctx, "S4", cls, technology=t, fuel=fs, year=ys[0], parameter="TotalTechnologyAnnualActivityLowerLimit",
                  values=f"lower {lo:.6g}",
                  message=f"forced technology whose input chain has largest activity 0 upstream in {_years_text(ys)}")
    # S5
    for code, name, key, msg in v.d.problems:
        if key and v.d.dims.get(name, [""])[0] == "REGION" and key[0] != v.r:
            continue
        yield row(ctx, "S5", FAIL, parameter=name, message=f"{msg} {key if key else ''}".strip())
    # S6
    thr = ctx["thr"]
    used = {t for (t, y) in list(v.iar) + list(v.oar)}
    for name in ("OperationalLife", "CapacityToActivityUnit"):
        ex = v.explicit(name)
        dflt = v.default(name)
        miss = [t for t in v.techs if (t,) not in ex]
        for t in miss:
            if dflt is None:
                yield row(ctx, "S6", FAIL, parameter=name, technology=t, message="no value and no declared default")
            elif t in used:
                yield row(ctx, "S6", WARN, parameter=name, technology=t, values=f"default {dflt:g}",
                          message="no explicit value; the declared default applies")
    for name in ("CapacityFactor", "AvailabilityFactor"):
        bad = defaultdict(list)
        for k, val in v.explicit(name).items():
            if val < 0 or val > 1:
                bad[(k[0], round(val, 6))].append(k[-1])
        for (t, val), ys in bad.items():
            yield row(ctx, "S6", FAIL, parameter=name, technology=t, year=ys[0], values=f"{val:g}",
                      message=f"outside [0, 1] in {_years_text(ys)}")
    for y in v.years:
        tot = sum(v.ys[(l, y)] for l in v.slices)
        if abs(tot - 1) > thr["sum_tol"]:
            yield row(ctx, "S6", FAIL, parameter="YearSplit", year=y, values=f"sum {tot:.6g}",
                      message="YearSplit does not sum to 1")
    bad = defaultdict(list)
    for f in v.fuels:
        for y in v.years:
            if (v.val("SpecifiedAnnualDemand", f, y) or 0) > 0:
                tot = sum(v.val("SpecifiedDemandProfile", f, l, y) or 0.0 for l in v.slices)
                if abs(tot - 1) > thr["sum_tol"]:
                    bad[(f, round(tot, 6))].append(y)
    for (f, tot), ys in bad.items():
        yield row(ctx, "S6", FAIL, parameter="SpecifiedDemandProfile", fuel=f, year=ys[0], values=f"sum {tot:g}",
                  message=f"profile of a demanded fuel does not sum to 1 in {_years_text(ys)}")


# ====================================================================== layer B
def layer_b(v, ctx):
    cap = v.cap_bounds()
    act = v.own_activity_bounds()
    grp = defaultdict(list)

    def add(check, t, y, a, b, what, param):
        grp[(check, t, param, what)].append((y, a, b))

    for t in v.techs:
        mpl = v.val("TotalTechnologyModelPeriodActivityLowerLimit", t) or 0.0
        mpu = v.val("TotalTechnologyModelPeriodActivityUpperLimit", t)
        if mpu is not None:
            if mpl > 0 and v.exceeds(mpl, mpu):
                add("B4", t, "", mpl, mpu, "model period lower limit above model period upper limit",
                    "TotalTechnologyModelPeriodActivityLowerLimit")
            sl = sum(v.val("TotalTechnologyAnnualActivityLowerLimit", t, y) or 0.0 for y in v.years)
            if v.exceeds(sl, mpu):
                add("B4", t, "", sl, mpu, "sum of annual lower limits above model period upper limit",
                    "TotalTechnologyAnnualActivityLowerLimit")
        if mpl > 0:
            hi = sum(act[(t, y)][1] for y in v.years)
            if v.exceeds(mpl, hi):
                add("B8", t, "", mpl, hi, "model period lower limit above the most activity capacity allows over the period",
                    "TotalTechnologyModelPeriodActivityLowerLimit")
        cau = v.val("CapacityToActivityUnit", t) or 0.0
        for y in v.years:
            mn = v.val("TotalAnnualMinCapacity", t, y) or 0.0
            mx = v.val("TotalAnnualMaxCapacity", t, y)
            res = v.val("ResidualCapacity", t, y) or 0.0
            mni = v.val("TotalAnnualMinCapacityInvestment", t, y) or 0.0
            mxi = v.val("TotalAnnualMaxCapacityInvestment", t, y)
            lo = v.val("TotalTechnologyAnnualActivityLowerLimit", t, y) or 0.0
            up = v.val("TotalTechnologyAnnualActivityUpperLimit", t, y)
            if mx is not None and mn > 0 and v.exceeds(mn, mx):
                add("B1", t, y, mn, mx, "minimum capacity above maximum capacity", "TotalAnnualMinCapacity")
            if mxi is not None and mni > 0 and v.exceeds(mni, mxi):
                add("B2", t, y, mni, mxi, "minimum investment above maximum investment", "TotalAnnualMinCapacityInvestment")
            if up is not None and lo > 0 and v.exceeds(lo, up):
                add("B3", t, y, lo, up, "activity lower limit above activity upper limit",
                    "TotalTechnologyAnnualActivityLowerLimit")
            if mx is not None and v.exceeds(res, mx):
                add("B5", t, y, res, mx, "residual capacity above maximum capacity", "ResidualCapacity")
            elif mx is not None:
                win = v.window(t, y)
                mi = sum(max(v.val("TotalAnnualMinCapacityInvestment", t, yy) or 0.0, 0.0) for yy in win)
                if mi > 0 and v.exceeds(res + mi, mx):
                    add("B6", t, y, res + mi, mx,
                        "residual capacity plus minimum investments within their life above maximum capacity",
                        "TotalAnnualMinCapacityInvestment")
            if mn > 0:
                win = v.window(t, y)
                reach = res + sum(v.val("TotalAnnualMaxCapacityInvestment", t, yy) or 0.0 for yy in win)
                if v.exceeds(mn, reach):
                    add("B7", t, y, mn, reach,
                        "minimum capacity above residual capacity plus the maximum investments within their life",
                        "TotalAnnualMinCapacity")
            if lo > 0:
                af = v.val("AvailabilityFactor", t, y)
                af = 1.0 if af is None else af
                most = cap[(t, y)][1] * cau * v.cfys(t, y) * min(max(af, 0.0), 1.0)
                if v.exceeds(lo, most):
                    add("B8", t, y, lo, most,
                        "activity lower limit above the most activity the reachable capacity allows "
                        f"(capacity {cap[(t, y)][1]:.6g} x CF.YearSplit {v.cfys(t, y):.6g} x AF {af:.6g} x CAU {cau:.6g})",
                        "TotalTechnologyAnnualActivityLowerLimit")
    for (check, t, param, what), items in grp.items():
        ys = [i[0] for i in items if i[0] != ""]
        y0, a, b = items[0]
        worst = max(items, key=lambda i: i[1] - i[2])
        yield row(ctx, check, v.cls(worst[1], worst[2]), parameter=param, technology=t, year=y0,
                  values=f"{a:.6g} > {b:.6g}",
                  message=what + (f" in {_years_text(ys)}" if ys else ""))


# ====================================================================== layer P
def propagate(v, y, act0):
    """Tightened (least, largest) yearly activity of every technology in year y, with the least requirement and the
    most supply of every fuel. Both directions use only valid bounds."""
    lo = {t: act0[(t, y)][0] for t in v.techs}
    hi = {t: act0[(t, y)][1] for t in v.techs}
    prod = defaultdict(list)   # f -> [(t, max output ratio)]
    use = defaultdict(list)    # f -> [(t, min input ratio)]
    for t in v.techs:
        for f in v.outputs(t, y):
            r = v.max_ratio(v.oar, t, f, y)
            if r > 0:
                prod[f].append((t, r))
        for f in v.inputs(t, y):
            r = v.min_ratio(v.iar, t, f, y)
            if r > 0:
                use[f].append((t, r))
    dem = {f: v.demand(f, y) for f in v.fuels}
    thr = v.thr
    fuels = set(prod) | set(use) | {f for f in dem if dem[f] > 0}

    def req(f):
        return dem.get(f, 0.0) + sum(lo[t] * r for t, r in use.get(f, []))

    def sup(f):
        return sum(hi[t] * r for t, r in prod.get(f, []))

    for _ in range(int(thr["propagation_max_rounds"])):
        moved = 0.0
        for f in fuels:
            R = req(f)
            P = prod.get(f, [])
            # a producer's least activity rises when the others at their largest cannot cover the requirement
            if R > 0:
                for i, (q, rq) in enumerate(P):
                    others = sum(hi[t] * r for j, (t, r) in enumerate(P) if j != i)
                    need = (R - others) / rq
                    if need > lo[q] * (1 + thr["propagation_change"]) + thr["abs_tol"]:
                        moved = max(moved, (need - lo[q]) / max(abs(need), 1e-12))
                        lo[q] = need
            # a user's largest activity falls to what the fuel can deliver after the other least uses
            Sp = sup(f)
            for t, r in use.get(f, []):
                rest = dem.get(f, 0.0) + sum(lo[u] * ru for u, ru in use[f] if u != t)
                cap_ = (Sp - rest) / r
                if cap_ < hi[t] * (1 - thr["propagation_change"]) - thr["abs_tol"]:
                    moved = max(moved, (hi[t] - cap_) / max(abs(hi[t]), 1e-12))
                    hi[t] = max(cap_, 0.0)  # below the least use the fuel already fails P1
        if moved <= thr["propagation_change"]:
            break
    return lo, hi, {f: req(f) for f in fuels}, {f: sup(f) for f in fuels}, prod, use


def layer_p(v, ctx):
    act0 = v.own_activity_bounds()
    cap = v.cap_bounds()
    p1, p1w, p2, p3, p4 = [], [], [], [], []
    ctx["_prop"] = {}
    for y in v.years:
        lo, hi, R, S, prod, use = propagate(v, y, act0)
        ctx["_prop"][y] = (lo, hi)
        sto = v.storage_fuels(y)
        # P1 per year
        for f in R:
            if v.exceeds(R[f], S[f]):
                p1.append((f, y, "", R[f], S[f]))
        # P1 per time slice, for fuels with a demand profile
        if len(v.slices) > 1:
            for f in v.fuels:
                sad = v.val("SpecifiedAnnualDemand", f, y) or 0.0
                if sad <= 0:
                    continue
                for l in v.slices:
                    need = sad * (v.val("SpecifiedDemandProfile", f, l, y) or 0.0)
                    if need <= 0:
                        continue
                    most = 0.0
                    for t, r in prod.get(f, []):
                        cau = v.val("CapacityToActivityUnit", t) or 0.0
                        a = cap[(t, y)][1] * (v.val("CapacityFactor", t, l, y) or 0.0) * cau * v.ys[(l, y)]
                        most += min(a, hi[t]) * r
                    if v.exceeds(need, most):
                        (p1w if f in sto else p1).append((f, y, l, need, most))
        # P2 emissions
        lim = v.explicit("AnnualEmissionLimit")
        nolim = ctx["thr"]["no_limit_at_or_above"]
        for (e, yy), L in lim.items():
            if yy != y or L >= nolim:
                continue
            least = v.val("AnnualExogenousEmission", e, y) or 0.0
            least += least_emissions(v, y, e, lo, hi, R, prod)
            if v.exceeds(least, L):
                p2.append((e, y, least, L))
        # P3 renewable target
        tgt = v.val("REMinProductionTarget", y) or 0.0
        if tgt > 0:
            tagged = sum((v.val("RETagFuel", f, y) or 0.0) * R.get(f, 0.0) for f in v.fuels)
            most = 0.0
            for t in v.techs:
                tag = v.val("RETagTechnology", t, y) or 0.0
                if tag > 0:
                    by_mode = max([sum(v.oar.get((t, y), {}).get(f, {}).get(m, 0.0) for f in v.outputs(t, y))
                                   for m in (v.modes or ["1"])] or [0.0])
                    most += tag * hi[t] * by_mode
            if v.exceeds(tgt * tagged, most):
                p3.append((y, tgt, tgt * tagged, most))
        # P4 reserve margin
        rm = v.val("ReserveMargin", y) or 0.0
        if rm > 0:
            capm = sum((v.val("ReserveMarginTagTechnology", t, y) or 0.0) * cap[(t, y)][1] *
                       (v.val("CapacityToActivityUnit", t) or 0.0) for t in v.techs)
            for l in v.slices:
                ysl = v.ys[(l, y)]
                if ysl <= 0:
                    continue
                rate = sum((v.val("ReserveMarginTagFuel", f, y) or 0.0) * (v.val("SpecifiedAnnualDemand", f, y) or 0.0)
                           * (v.val("SpecifiedDemandProfile", f, l, y) or 0.0) / ysl for f in v.fuels)
                if v.exceeds(rm * rate, capm):
                    p4.append((y, l, rm * rate, capm))
    for f, y, l, a, b in p1:
        yield row(ctx, "P1", v.cls(a, b), fuel=f, year=y, timeslice=l, values=f"least {a:.6g} > most {b:.6g}",
                  message="least requirement of the fuel exceeds the most supply its producers can give" +
                          (" in the time slice" if l else " in the year"))
    for f, y, l, a, b in p1w:
        yield row(ctx, "P1", WARN, fuel=f, year=y, timeslice=l, values=f"least {a:.6g} > most {b:.6g}",
                  message="time slice shortage on a fuel linked to a storage (storage may shift supply)")
    for e, y, a, b in p2:
        yield row(ctx, "P2", v.cls(a, b), emission=e, year=y, parameter="AnnualEmissionLimit", values=f"least {a:.6g} > limit {b:.6g}",
                  message="least emissions the tightened activities allow exceed the annual emission limit")
    for y, t, a, b in p3:
        yield row(ctx, "P3", v.cls(a, b), year=y, parameter="REMinProductionTarget",
                  values=f"target {t:.6g}: needed {a:.6g} > most renewable {b:.6g}",
                  message="largest tagged production cannot reach the target share of the least tagged-fuel production")
    for y, l, a, b in p4:
        yield row(ctx, "P4", v.cls(a, b), year=y, timeslice=l, parameter="ReserveMargin", values=f"needed {a:.6g} > most {b:.6g}",
                  message="largest tagged capacity cannot cover the reserve margin on the least tagged production rate")


def least_emissions(v, y, e, lo, hi, R, prod):
    """Lower bound of the emissions of label e in year y, by weak LP duality (the bound of an emission minimisation
    over the yearly fuel balances and the tightened activity bounds).

    c(t) = smallest emission ratio of t over the mode set (a negative ratio counts at the largest activity, and t
    then enters the rest with c = 0). e(f) = least embodied emission per unit of fuel f: the smallest
    (c(p) + sum of the smallest input ratios times e(input)) / largest output ratio over the producers p of f that
    give f alone; 0 for a fuel that a producer gives together with other fuels, or that nothing can deliver. Every
    technology then has a reduced cost rc(t) = c(t) + sum of input ratios times e(input) - output ratio times e(f)
    >= 0, and for every feasible activity
        emissions >= sum over fuels of e(f) x demand(f) + sum over technologies of rc(t) x activity(t).
    The second sum is bounded below per fuel: its single-output producers must deliver the fuel's least
    requirement, filled at the lowest rc per unit of output first between their least and largest activity
    (producers that give several fuels count at their largest output); every other technology adds rc x least
    activity."""
    c = {}
    base = 0.0
    for t in v.techs:
        if v.ear.get((t, y), {}).get(e):
            r = v.min_ratio(v.ear, t, e, y)
            if r < 0:
                base += r * hi[t]
                r = 0.0
            c[t] = r
        else:
            c[t] = 0.0
    outs = {t: v.outputs(t, y) for t in v.techs}
    ins = {t: [(g, v.min_ratio(v.iar, t, g, y)) for g in v.inputs(t, y)] for t in v.techs}
    ins = {t: [(g, r) for g, r in gs if r > 0] for t, gs in ins.items()}
    single = {t: o[0] for t, o in outs.items() if len(o) == 1}
    oar = {t: v.max_ratio(v.oar, t, single[t], y) for t in single}
    multi_out = {f for t, o in outs.items() if len(o) > 1 for f in o}
    INF = float("inf")
    ef = {f: (0.0 if f in multi_out else INF) for f in v.fuels}

    def relax(ef):
        for _ in range(len(v.fuels) + 2):
            moved = False
            for t, f in single.items():
                if f in multi_out or oar[t] <= 0:
                    continue
                cost = c[t] + sum(r * ef.get(g, 0.0) for g, r in ins[t])
                if cost < INF:
                    cand = cost / oar[t]
                    if cand < ef[f] - 1e-15:
                        ef[f] = cand
                        moved = True
            if not moved:
                break

    relax(ef)
    for f in ef:  # fuels nothing can deliver: 0, then relax again so every producer's reduced cost stays >= 0
        if ef[f] == INF:
            ef[f] = 0.0
    relax(ef)
    rc = {}
    for t in v.techs:
        val = c[t] + sum(r * ef.get(g, 0.0) for g, r in ins[t])
        if t in single:
            val -= oar[t] * ef[single[t]]
        rc[t] = 0.0 if -1e-12 < val < 0 else val
    total = base + sum(ef[f] * v.demand(f, y) for f in v.fuels)
    grouped = defaultdict(list)
    for t, f in single.items():
        grouped[f].append(t)
    for t in v.techs:
        if t not in single:
            total += rc[t] * (lo[t] if rc[t] >= 0 else hi[t])
    for f, ts in grouped.items():
        req = R.get(f, 0.0)
        free = sum(hi[t] * r for t, r in prod.get(f, []) if t not in single)
        items, out_lo = [], 0.0
        for t in ts:
            total += rc[t] * lo[t]
            if oar[t] <= 0:
                if rc[t] < 0:
                    total += rc[t] * (hi[t] - lo[t])
                continue
            out_lo += lo[t] * oar[t]
            items.append((rc[t] / oar[t], (hi[t] - lo[t]) * oar[t]))
        need = req - free - out_lo
        for per, room in sorted(items):
            if per < 0:  # a negative reduced cost lowers the bound most at the largest activity
                total += room * per
                need -= room
                continue
            if need <= 0:
                break
            take = min(room, need)
            total += take * per
            need -= take
    return total
