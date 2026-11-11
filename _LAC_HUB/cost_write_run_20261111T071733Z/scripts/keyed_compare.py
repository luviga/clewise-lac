"""Keyed comparison of OSeMOSYS parameter CSV files (A2 and B1 outputs).

Each row is keyed by its parameter file name and every index column (all
columns except Value). Values are compared to 1e-9 relative. Row order and
file bytes are ignored. Duplicate keys are compared as sorted value lists.
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

REL_TOL = 1e-9


def _num(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    try:
        f = float(v)
        if math.isnan(f):
            return None
        return f
    except (TypeError, ValueError):
        s = str(v).strip()
        return s if s != "" else None


def values_equal(a, b) -> bool:
    a, b = _num(a), _num(b)
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) and isinstance(b, float):
        if a == b:
            return True
        return abs(a - b) <= REL_TOL * max(abs(a), abs(b))
    return str(a) == str(b)


def _norm_key_val(v):
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        if v.is_integer():
            return str(int(v))
        return repr(v)
    s = str(v).strip()
    try:
        f = float(s)
        if f.is_integer() and s.replace(".0", "").lstrip("-").isdigit():
            return str(int(f))
    except ValueError:
        pass
    return s


def load_keyed(path, ignore_cols=(), value_col="Value"):
    """Return dict key_tuple -> sorted list of values, plus the key columns."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    cols = [c for c in df.columns if c != value_col and c not in ignore_cols]
    out: dict = {}
    if value_col not in df.columns:
        # a file with no Value column: every row is a key
        for row in df[cols].itertuples(index=False):
            k = tuple(_norm_key_val(x) for x in row)
            out.setdefault(k, []).append("")
        return out, cols
    for row in df[cols + [value_col]].itertuples(index=False):
        k = tuple(_norm_key_val(x) for x in row[:-1])
        out.setdefault(k, []).append(row[-1])
    return out, cols


def compare_files(path_a, path_b, ignore_cols=()):
    """Yield dicts describing every differing value between two CSV files."""
    a, cols_a = load_keyed(path_a, ignore_cols)
    b, cols_b = load_keyed(path_b, ignore_cols)
    diffs = []
    if cols_a != cols_b:
        diffs.append({"key": "", "kind": "columns_differ", "a": "|".join(cols_a), "b": "|".join(cols_b)})
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k), b.get(k)
        if va is None:
            for v in vb:
                if _num(v) is None:
                    kind = "only_b_empty"
                else:
                    kind = "only_b"
                diffs.append({"key": "|".join(k), "kind": kind, "a": "", "b": v})
            continue
        if vb is None:
            for v in va:
                kind = "only_a_empty" if _num(v) is None else "only_a"
                diffs.append({"key": "|".join(k), "kind": kind, "a": v, "b": ""})
            continue
        if len(va) == 1 and len(vb) == 1:
            if not values_equal(va[0], vb[0]):
                diffs.append({"key": "|".join(k), "kind": "value", "a": va[0], "b": vb[0]})
            continue
        sa = sorted(va, key=lambda x: (str(type(_num(x))), str(_num(x))))
        sb = sorted(vb, key=lambda x: (str(type(_num(x))), str(_num(x))))
        if len(sa) != len(sb) or not all(values_equal(x, y) for x, y in zip(sa, sb)):
            diffs.append({"key": "|".join(k), "kind": "duplicate_key_values", "a": ";".join(sa), "b": ";".join(sb)})
    return diffs, cols_a


def compare_dirs(dir_a, dir_b, ignore_cols=(), pattern="*.csv"):
    """Compare every CSV in two folders. Returns list of diff dicts with 'file'."""
    dir_a, dir_b = Path(dir_a), Path(dir_b)
    names_a = {p.name for p in dir_a.glob(pattern)}
    names_b = {p.name for p in dir_b.glob(pattern)}
    rows = []
    for name in sorted(names_a | names_b):
        if name not in names_a:
            rows.append({"file": name, "key": "", "kind": "file_only_b", "a": "", "b": ""})
            continue
        if name not in names_b:
            rows.append({"file": name, "key": "", "kind": "file_only_a", "a": "", "b": ""})
            continue
        diffs, cols = compare_files(dir_a / name, dir_b / name, ignore_cols)
        for d in diffs:
            d["file"] = name
            d["key_columns"] = "|".join(cols)
            rows.append(d)
    return rows
