"""One region of one parsed data file, with the bounds the model's own constraints imply.

Constraint semantics used (OSeMOSYS_Model.txt of the 24 models):
  CAa1, CAa2  capacity(y) = residual(y) + sum of new capacity of the years yy with 0 <= y - yy < OperationalLife
  NCC1, NCC2  new capacity(y) <= TotalAnnualMaxCapacityInvestment(y) (every year, default applies);
              new capacity(y) >= TotalAnnualMinCapacityInvestment(y) where above 0
  TCC1, TCC2  capacity(y) <= TotalAnnualMaxCapacity(y) (every year); capacity(y) >= TotalAnnualMinCapacity(y) where above 0
  CAa4        rate of activity in a time slice <= capacity * CapacityFactor * CapacityToActivityUnit
  CAb1        yearly activity <= capacity * sum over slices (CapacityFactor * YearSplit) * AvailabilityFactor * CapacityToActivityUnit
  AAC2, AAC3  yearly activity <= upper limit (every year); >= lower limit where above 0
  TAC1..3     model period activity = sum of yearly activity, within its upper limit and its lower limit (above 0)
Every activity is the sum over all modes of the mode set, and a mode with no ratio for a fuel neither uses nor
gives that fuel, so ratios over modes are read conservatively: for a requirement the smallest ratio over every mode
of the set (0 when one mode has none), for an availability the largest.
"""
from __future__ import annotations

from collections import defaultdict


class View:
    def __init__(self, data, region, thr):
        self.d = data
        self.r = region
        self.thr = thr
        S = data.sets
        self.years = sorted(S.get("YEAR", []), key=int)
        self.techs = list(S.get("TECHNOLOGY", []))
        self.fuels = list(S.get("FUEL", []))
        self.emissions = list(S.get("EMISSION", []))
        self.modes = list(S.get("MODE_OF_OPERATION", []))
        self.slices = list(S.get("TIMESLICE", []))
        self._cache = {}
        # ratios: (t, y) -> {fuel or emission: {mode: value}}
        self.iar = self._ratio("InputActivityRatio")
        self.oar = self._ratio("OutputActivityRatio")
        self.ear = self._ratio("EmissionActivityRatio")
        ys = self.d.params.get("YearSplit")
        self.ys = {(l, y): ys.get((l, y), 0.0) if ys else 0.0 for l in self.slices for y in self.years}

    # ------------------------------------------------------------------ access
    def par(self, name):
        return self.d.params.get(name)

    def val(self, name, *idx):
        """Value with the declared default; region prepended when the parameter has a REGION index."""
        p = self.d.params.get(name)
        if p is None:
            return None
        dims = self.d.dims.get(name, [])
        key = ((self.r,) + idx) if dims and dims[0] == "REGION" else idx
        return p.get(key)

    def explicit(self, name):
        """{index without region: value} of the explicit values of this region."""
        if name in self._cache:
            return self._cache[name]
        p = self.d.params.get(name)
        out = {}
        if p is not None:
            dims = self.d.dims.get(name, [])
            if dims and dims[0] == "REGION":
                for k, v in p.values.items():
                    if k[0] == self.r:
                        out[k[1:]] = v
            else:
                out = dict(p.values)
        self._cache[name] = out
        return out

    def default(self, name):
        p = self.d.params.get(name)
        return p.default if p is not None else None

    def _ratio(self, name):
        out = defaultdict(lambda: defaultdict(dict))
        for (t, f, m, y), v in self.explicit(name).items():
            out[(t, y)][f][m] = v
        return out

    # ------------------------------------------------------------------ ratios over modes
    def min_ratio(self, table, t, x, y):
        """Smallest ratio of t for x over every mode of the mode set (0 when a mode has none)."""
        by = table.get((t, y), {}).get(x)
        if not by:
            return 0.0
        return min(by.get(m, 0.0) for m in self.modes) if self.modes else min(by.values())

    def max_ratio(self, table, t, x, y):
        by = table.get((t, y), {}).get(x)
        if not by:
            return 0.0
        return max([by.get(m, 0.0) for m in self.modes] or list(by.values()))

    def outputs(self, t, y):
        return [f for f, by in self.oar.get((t, y), {}).items() if any(v > 0 for v in by.values())]

    def inputs(self, t, y):
        return [f for f, by in self.iar.get((t, y), {}).items() if any(v > 0 for v in by.values())]

    def mode_inputs(self, t, m, y):
        return [f for f, by in self.iar.get((t, y), {}).items() if by.get(m, 0.0) > 0]

    def mode_outputs(self, t, m, y):
        return [f for f, by in self.oar.get((t, y), {}).items() if by.get(m, 0.0) > 0]

    # ------------------------------------------------------------------ capacity and activity bounds
    def cfys(self, t, y):
        """sum over slices of CapacityFactor * YearSplit."""
        return sum((self.val("CapacityFactor", t, l, y) or 0.0) * self.ys[(l, y)] for l in self.slices)

    def window(self, t, y):
        ol = self.val("OperationalLife", t) or 0.0
        yi = int(y)
        return [yy for yy in self.years if 0 <= yi - int(yy) < ol]

    def cap_bounds(self):
        """{(t, y): (least capacity, largest reachable capacity)}."""
        if "cap" in self._cache:
            return self._cache["cap"]
        out = {}
        for t in self.techs:
            for y in self.years:
                res = self.val("ResidualCapacity", t, y) or 0.0
                mx = self.val("TotalAnnualMaxCapacity", t, y)
                mn = self.val("TotalAnnualMinCapacity", t, y) or 0.0
                win = self.window(t, y)
                maxinv = sum(self.val("TotalAnnualMaxCapacityInvestment", t, yy) or 0.0 for yy in win)
                mininv = sum(max(self.val("TotalAnnualMinCapacityInvestment", t, yy) or 0.0, 0.0) for yy in win)
                reach = res + maxinv
                if mx is not None:
                    reach = min(reach, mx)
                least = max(mn if mn > 0 else 0.0, res + mininv)
                out[(t, y)] = (least, reach)
        self._cache["cap"] = out
        return out

    def own_activity_bounds(self):
        """{(t, y): (least, largest)} yearly activity from the technology's own limits."""
        if "act" in self._cache:
            return self._cache["act"]
        cap = self.cap_bounds()
        out = {}
        for t in self.techs:
            cau = self.val("CapacityToActivityUnit", t) or 0.0
            for y in self.years:
                af = self.val("AvailabilityFactor", t, y)
                af = 1.0 if af is None else af
                hi = cap[(t, y)][1] * cau * self.cfys(t, y) * min(max(af, 0.0), 1.0)
                up = self.val("TotalTechnologyAnnualActivityUpperLimit", t, y)
                if up is not None:
                    hi = min(hi, up)
                mpu = self.val("TotalTechnologyModelPeriodActivityUpperLimit", t)
                if mpu is not None:
                    hi = min(hi, mpu)
                lo = self.val("TotalTechnologyAnnualActivityLowerLimit", t, y) or 0.0
                out[(t, y)] = (max(lo, 0.0), max(hi, 0.0))
        # model period lower limit: least yearly activity = lower limit minus the most of the other years
        for t in self.techs:
            mpl = self.val("TotalTechnologyModelPeriodActivityLowerLimit", t) or 0.0
            if mpl > 0:
                tot = sum(out[(t, y)][1] for y in self.years)
                for y in self.years:
                    lo, hi = out[(t, y)]
                    need = mpl - (tot - hi)
                    if need > lo:
                        out[(t, y)] = (need, hi)
        self._cache["act"] = out
        return out

    def demand(self, f, y):
        return (self.val("SpecifiedAnnualDemand", f, y) or 0.0) + (self.val("AccumulatedAnnualDemand", f, y) or 0.0)

    def storage_fuels(self, y):
        """Fuels given or taken by a technology linked to a storage."""
        out = set()
        for name in ("TechnologyToStorage", "TechnologyFromStorage"):
            for (t, s, m), v in self.explicit(name).items():
                if v > 0:
                    out.update(self.mode_outputs(t, m, y))
                    out.update(self.mode_inputs(t, m, y))
        return out

    def exceeds(self, a, b):
        """a > b beyond the tolerances."""
        return a > b + self.thr["rel_tol"] * abs(b) + self.thr["abs_tol"]

    def cls(self, a, b):
        """FAIL when a exceeds b beyond the solver's feasibility tolerance, WARN when only beyond abs_tol."""
        return "FAIL" if a > b + self.thr["rel_tol"] * abs(b) + self.thr["solver_abs_tol"] else "WARN"
