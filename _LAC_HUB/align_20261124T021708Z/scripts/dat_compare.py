"""Parse GLPK MathProg data files written by B1 / Stage 3 and compare them by
parameter and index (never as text).

Handles the three layouts these files use:
  param P default d :=  [r,t,*,*]: <cols> :=  <row> v v ...   (slices)
  param P default d :   <cols> :=  <row> v v ...               (2-D table)
  param P default d :=  r t y v                                 (plain tuples)
A missing index takes the parameter default, so a value written explicitly
equal to the default is not a difference.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

REL_TOL = 1e-9


def _f(x):
    try:
        return float(x)
    except ValueError:
        return x


def parse_dat(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    sets, params, defaults = {}, {}, {}
    for stmt in text.split(";"):
        lines = [ln.strip() for ln in stmt.strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]
        if not lines:
            continue
        head = lines[0]
        if head.startswith("set "):
            m = re.match(r"set\s+(\S+)\s*:=\s*(.*)$", " ".join(lines))
            if m:
                sets[m.group(1)] = set(m.group(2).split())
            continue
        if not head.startswith("param "):
            continue
        m = re.match(r"param\s+(\S+)(?:\s+default\s+(\S+))?\s*(:=|:)?\s*(.*)$", head)
        if not m:
            continue
        name, dflt, opener, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        defaults[name] = _f(dflt) if dflt is not None else None
        vals = params.setdefault(name, {})
        body = ([rest] if rest else []) + lines[1:]
        slice_spec, cols = None, None
        for ln in body:
            if ln.startswith("[") and ln.endswith(":"):
                slice_spec = [p.strip() for p in ln[1:ln.index("]")].split(",")]
                cols = None
                continue
            if ln.endswith(":="):
                cols = ln[:-2].split()
                continue
            toks = ln.split()
            if cols is not None:
                row, data = toks[0], toks[1:]
                for c, v in zip(cols, data):
                    if v == ".":
                        continue
                    if slice_spec is not None:
                        free = iter([row, c])
                        key = tuple(next(free) if p == "*" else p for p in slice_spec)
                    else:
                        key = (row, c)
                    vals[key] = _f(v)
            else:
                if len(toks) >= 2:
                    vals[tuple(toks[:-1])] = _f(toks[-1])
    return sets, params, defaults


def _eq(a, b):
    if isinstance(a, float) and isinstance(b, float):
        if a == b:
            return True
        if math.isinf(a) or math.isinf(b):
            return False
        return abs(a - b) <= REL_TOL * max(abs(a), abs(b))
    return a == b


def compare_dat(path_a, path_b):
    """Return list of diff dicts: kind in set_only_a/set_only_b/param_only_a/
    param_only_b/default/value."""
    sa, pa, da = parse_dat(path_a)
    sb, pb, db = parse_dat(path_b)
    rows = []
    for s in sorted(set(sa) | set(sb)):
        A, B = sa.get(s, set()), sb.get(s, set())
        for x in sorted(A - B):
            rows.append(dict(param=s, key=x, kind="set_only_a", a=x, b=""))
        for x in sorted(B - A):
            rows.append(dict(param=s, key=x, kind="set_only_b", a="", b=x))
    for p in sorted(set(pa) | set(pb)):
        if p not in pa or p not in pb:
            rows.append(dict(param=p, key="", kind="param_only_a" if p in pa else "param_only_b", a="", b=""))
            continue
        dfa, dfb = da.get(p), db.get(p)
        if not _eq(dfa, dfb):
            rows.append(dict(param=p, key="(default)", kind="default", a=dfa, b=dfb))
        A, B = pa[p], pb[p]
        for k in set(A) | set(B):
            va = A.get(k, dfa)
            vb = B.get(k, dfb)
            if not _eq(va, vb):
                rows.append(dict(param=p, key="|".join(k), kind="value", a=va, b=vb))
    return rows


if __name__ == "__main__":
    rows = compare_dat(sys.argv[1], sys.argv[2])
    print(len(rows), "differences")
    for r in rows[:50]:
        print(r)
