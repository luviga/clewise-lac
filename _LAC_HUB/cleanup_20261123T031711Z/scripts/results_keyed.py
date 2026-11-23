"""Keyed comparison of the Stage 3 results workbook of two snapshots: each sheet is keyed on every column but the
value (Value, or Solver_Share, Deviation and Status of ShareValidation), so added or removed rows do not shift the
comparison. Prints and writes the count of changed keys by sheet, country and scenario, and the largest change.
Usage: python results_keyed.py <snapA> <snapB> <out.csv> [tolerance]
"""
import csv
import sys
from pathlib import Path

import openpyxl

snap_a, snap_b, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
tol = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
VALUE_COLS = {'Value', 'Solver_Share', 'Deviation', 'Status'}


def load(snap):
    wb = openpyxl.load_workbook(snap / 'tree' / '_STAGE3_RESULTS' / 'stage3_results.xlsx', read_only=True)
    data = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        head = next(it)
        kcols = [i for i, h in enumerate(head) if h not in VALUE_COLS]
        vcols = [i for i, h in enumerate(head) if h in VALUE_COLS]
        d = data.setdefault(ws.title, {})
        for r in it:
            d[tuple(r[i] for i in kcols)] = tuple(r[i] for i in vcols)
    wb.close()
    return data


def differs(x, y):
    for p, q in zip(x, y):
        if isinstance(p, (int, float)) and isinstance(q, (int, float)):
            if abs(p - q) > tol:
                return True
        elif p != q:
            return True
    return False


a, b = load(snap_a), load(snap_b)
agg = {}
for sheet in sorted(set(a) | set(b)):
    da, db = a.get(sheet, {}), b.get(sheet, {})
    for k in set(da) | set(db):
        va, vb = da.get(k), db.get(k)
        if va is not None and vb is not None and not differs(va, vb):
            continue
        kind = 'only_a' if vb is None else 'only_b' if va is None else 'changed'
        g = agg.setdefault((sheet, k[0], k[1], kind), [0, 0.0])
        g[0] += 1
        if kind == 'changed' and isinstance(va[0], (int, float)) and isinstance(vb[0], (int, float)):
            g[1] = max(g[1], abs(vb[0] - va[0]))
rows = [dict(sheet=s, country=c, scenario=sc, kind=k, keys=n, max_abs_change=round(m, 6))
        for (s, c, sc, k), (n, m) in sorted(agg.items())]
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['sheet', 'country', 'scenario', 'kind', 'keys', 'max_abs_change'],
                       lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r)
print('groups', len(rows))
