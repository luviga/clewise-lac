"""Append rows to a table (CSV) of the repository, with csv quoting, keeping its column order.
Usage: py -I b2_add_rows.py <spec.py>   where spec defines ROWS = {table path: [dict, ...]}
A row whose key columns (all columns except value, unit, used_by and description) already exist is reported and skipped."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import runpy
import sys
from pathlib import Path

ROOT = M.ROOT
spec = runpy.run_path(sys.argv[1])
for table, rows in spec['ROWS'].items():
    p = ROOT / table
    with open(p, encoding='utf-8', newline='') as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        have = list(rd)
    keycols = [c for c in cols if c not in ('value', 'used_by', 'description', 'unit')]
    keys = {tuple(r[c] for c in keycols) for r in have}
    added = 0
    for r in rows:
        r = {c: str(r.get(c, '')) for c in cols}
        k = tuple(r[c] for c in keycols)
        if k in keys:
            print('exists', table, k)
            continue
        have.append(r)
        keys.add(k)
        added += 1
    with open(p, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        w.writerows(have)
    print(table, 'added', added, 'rows', len(have))
