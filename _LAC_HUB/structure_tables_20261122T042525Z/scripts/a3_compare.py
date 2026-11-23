"""Compare two snapshot trees cell by cell: compiled inputs (A2_Output_Params, B1_Output_Params) keyed by every
index column (parameter file, region, technology, fuel, emission, mode, timeslice, year ...), stage outputs
(CSV rows as text, XLSX sheets cell by cell, TXT line by line). Values are equal only when their text is equal
or their numbers are exactly equal; there is no tolerance.

Skipped as run stamps (counted, not compared): XLSX cells and TXT lines that hold the run time (ISO timestamps
written by the stage scripts, rows labelled Generated).

Usage: py -I a3_compare.py <tree A> <tree B> <out.csv> [--map NEW=OLD,...]
  --map: names of tree B written back to the names of tree A before comparing (folder names, sheet names, cell
  text), for the scenario rename of Phase C; a mapped difference is then no difference.
Prints a summary per area and writes every difference with both values.
"""
import csv
import math
import re
import sys
from collections import Counter
from pathlib import Path

import openpyxl
import pandas as pd

A, B, OUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
MAP = {}
if '--map' in sys.argv:
    for pair in sys.argv[sys.argv.index('--map') + 1].split(','):
        new, old = pair.split('=')
        MAP[new] = old
TS = re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?$')


def m(s):
    if not MAP or not isinstance(s, str):
        return s
    for new, old in MAP.items():
        s = re.sub(r'(?<![A-Za-z0-9])' + re.escape(new) + r'(?![A-Za-z0-9])', old, s)
    return s


def num(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def equal(a, b):
    if a == b:
        return True
    if a is None or b is None or a == '' or b == '':
        return (a in (None, '')) and (b in (None, ''))
    fa, fb = num(a), num(b)
    if fa is not None and fb is not None:
        return fa == fb
    return str(a) == str(b)


def norm_key(v):
    f = num(v)
    if f is not None and f.is_integer() and re.fullmatch(r'-?\d+(\.0+)?', str(v).strip()):
        return str(int(f))
    return str(v).strip()


rows = []
skipped = Counter()


def diff(area, file, loc, kind, a='', b=''):
    rows.append(dict(area=area, file=file, location=loc, kind=kind, a=a, b=b))


def area_of(rel):
    for k in ('A2_Output_Params', 'B1_Output_Params'):
        if k in rel:
            return 'compiled ' + k.split('_')[0]
    return rel.split('/')[0]


def cmp_param_csv(rel, pa, pb):
    da = pd.read_csv(pa, dtype=str, keep_default_na=False)
    db = pd.read_csv(pb, dtype=str, keep_default_na=False).map(m)
    area = area_of(rel)
    if list(da.columns) != list(db.columns):
        diff(area, rel, '', 'columns', '|'.join(da.columns), '|'.join(db.columns))
        return
    vc = 'Value' if 'Value' in da.columns else None
    keys = [c for c in da.columns if c != vc]

    def keyed(df):
        out = {}
        for r in df.itertuples(index=False):
            d = r._asdict() if hasattr(r, '_asdict') else dict(zip(df.columns, r))
            rec = dict(zip(df.columns, r))
            k = tuple(norm_key(rec[c]) for c in keys)
            out.setdefault(k, []).append(rec[vc] if vc else '')
        return out
    ka, kb = keyed(da), keyed(db)
    for k in sorted(set(ka) | set(kb)):
        va, vb = ka.get(k), kb.get(k)
        loc = '|'.join(f'{c}={x}' for c, x in zip(keys, k))
        if va is None or vb is None:
            diff(area, rel, loc, 'row only in ' + ('B' if va is None else 'A'), ';'.join(va or []), ';'.join(vb or []))
        elif len(va) != len(vb) or not all(equal(x, y) for x, y in zip(sorted(va, key=str), sorted(vb, key=str))):
            diff(area, rel, loc, 'value', ';'.join(va), ';'.join(vb))


def cmp_csv(rel, pa, pb):
    da = pd.read_csv(pa, dtype=str, keep_default_na=False)
    db = pd.read_csv(pb, dtype=str, keep_default_na=False).map(m)
    db.columns = [m(c) for c in db.columns]
    area = area_of(rel)
    if list(da.columns) != list(db.columns):
        diff(area, rel, '', 'columns', '|'.join(da.columns), '|'.join(db.columns))
        return
    if da.shape == db.shape:
        bad = [(i, c) for c in da.columns for i in range(len(da)) if not equal(da.at[i, c], db.at[i, c])]
        if not bad:
            return
    # row order may differ: compare as multisets of rows
    ra = Counter(tuple(norm_key(x) for x in r) for r in da.itertuples(index=False))
    rb = Counter(tuple(norm_key(x) for x in r) for r in db.itertuples(index=False))
    if ra == rb:
        return
    for r in (ra - rb):
        diff(area, rel, '|'.join(r)[:300], 'row only in A', '', '')
    for r in (rb - ra):
        diff(area, rel, '|'.join(r)[:300], 'row only in B', '', '')


def cmp_xlsx(rel, pa, pb):
    area = area_of(rel)
    wa = openpyxl.load_workbook(pa, read_only=True, data_only=True)
    wb = openpyxl.load_workbook(pb, read_only=True, data_only=True)
    sa = wa.sheetnames
    sb = [m(s) for s in wb.sheetnames]
    if sa != sb:
        diff(area, rel, '', 'sheet names', '|'.join(sa), '|'.join(sb))
    for name in sa:
        if name not in sb:
            continue
        ga = [list(r) for r in wa[name].iter_rows(values_only=True)]
        gb = [[m(x) for x in r] for r in wb[wb.sheetnames[sb.index(name)]].iter_rows(values_only=True)]
        nr = max(len(ga), len(gb))
        for i in range(nr):
            ra = ga[i] if i < len(ga) else []
            rb = gb[i] if i < len(gb) else []
            label = str(ra[0]) if ra else ''
            for j in range(max(len(ra), len(rb))):
                x = ra[j] if j < len(ra) else None
                y = rb[j] if j < len(rb) else None
                if equal(x, y):
                    continue
                if (isinstance(x, str) and TS.match(x) and isinstance(y, str) and TS.match(y)) or label == 'Generated':
                    skipped[rel] += 1
                    continue
                diff(area, rel, f'{name}!R{i + 1}C{j + 1}', 'cell', x, y)
    wa.close()
    wb.close()


def cmp_txt(rel, pa, pb):
    la = pa.read_text(encoding='utf-8', errors='replace').splitlines()
    lb = [m(x) for x in pb.read_text(encoding='utf-8', errors='replace').splitlines()]
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else ''
        y = lb[i] if i < len(lb) else ''
        if x == y:
            continue
        if x.startswith('Generated:') and y.startswith('Generated:'):
            skipped[rel] += 1
            continue
        diff(area_of(rel), rel, f'line {i + 1}', 'line', x, y)


fa = {p.relative_to(A).as_posix(): p for p in A.rglob('*') if p.is_file()}
fb = {m(p.relative_to(B).as_posix()): p for p in B.rglob('*') if p.is_file()}
for rel in sorted(set(fa) | set(fb)):
    if rel not in fb:
        diff(area_of(rel), rel, '', 'file only in A')
        continue
    if rel not in fa:
        diff(area_of(rel), rel, '', 'file only in B')
        continue
    pa, pb = fa[rel], fb[rel]
    if pa.read_bytes() == pb.read_bytes() and not MAP:
        continue
    if rel.endswith('.csv'):
        (cmp_param_csv if ('A2_Output_Params' in rel or 'B1_Output_Params' in rel) else cmp_csv)(rel, pa, pb)
    elif rel.endswith('.xlsx'):
        cmp_xlsx(rel, pa, pb)
    elif rel.endswith('.txt'):
        cmp_txt(rel, pa, pb)
    elif pa.read_bytes() != pb.read_bytes():
        diff(area_of(rel), rel, '', 'bytes differ')
with open(OUT, 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['area', 'file', 'location', 'kind', 'a', 'b'], lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(f'files A {len(fa)}, B {len(fb)}; differences {len(rows)}; run-stamp cells or lines skipped {sum(skipped.values())}')
by = Counter((r['area'], r['kind']) for r in rows)
for (a, k), n in sorted(by.items()):
    print(f'  {a}: {k}: {n}')
for f, n in skipped.items():
    print(f'  skipped stamps in {f}: {n}')
