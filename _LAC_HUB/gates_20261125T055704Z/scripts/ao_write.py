"""Write model input workbooks from the job's value_register.csv (the script holds no value).

Each register row names model, file, sheet, tech, parameter, year, before, after. The cell is found from the
header row (row 1) of the sheet:
  - a sheet with a 'Tech' column: the row whose Tech equals `tech` (a `tech` of the form 'A|B' also matches the
    next text column to B, e.g. Externalities: Tech|External Cost) and, if the sheet has a 'Parameter' column,
    whose Parameter equals `parameter`; the column is the year header `year`, or the header named `parameter`,
    or 'Value' when year is blank;
  - a two-column sheet without a Tech column (B1_Default_Param.xlsx Default_Values): the row whose first cell is
    `parameter`, value in the second column.
The current cell must equal `before` (number within 1e-9 relative, or the same formula text); otherwise the row
is refused and reported. A-O workbooks (A1_Outputs) and every workbook with formulas are saved through
ao_safe_save.save_ao_safely (Excel recalculates the copy before it replaces the file).
Usage: python -I ao_write.py <value_register.csv> [--dry-run]
Writes <register>_write_log.csv next to the register."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import gc
import io
import re
import sys
from collections import defaultdict

import openpyxl

sys.path.insert(0, str(M.ROOT))
import ao_safe_save  # noqa: E402

reg = sys.argv[1]
dry = '--dry-run' in sys.argv
rows = list(csv.DictReader(open(reg, encoding='utf-8')))
groups = defaultdict(list)
for i, r in enumerate(rows):
    groups[(r['model'], r['file'])].append((i, r))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def same(cell, before):
    if isinstance(cell, str) and cell.startswith('='):
        if cell.strip() == str(before).strip():
            return True
        expr = cell.strip()[1:]
        if num(before) is not None and re.fullmatch(r'[0-9.+\-*/() ]+', expr):
            v = eval(expr, {'__builtins__': {}}, {})   # plain arithmetic of numbers only
            return abs(v - float(before)) <= 1e-6 * max(1.0, abs(v))
        return False
    a, b = num(cell), num(before)
    if a is None or b is None:
        return (cell in (None, '') and str(before).strip() in ('', 'None')) or str(cell) == str(before)
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def locate(ws, tech, param, year):
    hdr = [c.value for c in ws[1]]
    names = [str(h).strip() if h is not None else '' for h in hdr]
    names = ['Tech' if n == 'Fuel/Tech' else n for n in names]   # A-O_Demand: row key column
    if 'Set' in names and 'Scenario' in names:
        # B1 sheet with Set (and Set2): tech = 'Scenario|Set|Set2', year = the column header
        sc_, s1_, s2_ = (tech.split('|') + ['', ''])[:3]
        sc, c1, pc = names.index('Scenario'), names.index('Set'), names.index('Parameter')
        c2 = names.index('Set2') if 'Set2' in names else None
        vc = names.index(str(year)) if str(year) in names else None
        hits = [row[vc] for row in ws.iter_rows(min_row=2) if vc is not None and
                str(row[sc].value).strip() == sc_ and str(row[c1].value).strip() == s1_ and
                (c2 is None or str(row[c2].value).strip() == s2_) and str(row[pc].value).strip() == param]
        return hits[0] if len(hits) == 1 else None
    if 'Tech_Set' in names and 'Scenario' in names:
        # B1 scenario sheet: tech = 'Scenario|Tech_Set', parameter = Parameter, year = the column header
        sc_, _, ts_ = tech.partition('|')
        sc, tc = names.index('Scenario'), names.index('Tech_Set')
        pc = names.index('Parameter') if 'Parameter' in names else None
        vc = names.index(str(year)) if str(year) in names else None
        hits = [row[vc] for row in ws.iter_rows(min_row=2) if vc is not None and
                str(row[sc].value).strip() == sc_ and str(row[tc].value).strip() == ts_ and
                (pc is None or str(row[pc].value).strip() == param)]
        return hits[0] if len(hits) == 1 else None
    if 'Tech' not in names:
        for row in ws.iter_rows(min_row=1):
            if str(row[0].value).strip() == param:
                return row[1]
        return None
    tc = names.index('Tech')
    pc = names.index('Parameter') if 'Parameter' in names else None
    t1, _, t2 = tech.partition('|')
    if year not in ('', None) and num(year) is None:
        vc = names.index(str(year)) if str(year) in names else None
    elif year not in ('', None):
        ys = str(int(float(year)))
        vc = next((k for k, n in enumerate(names) if n == ys or n == ys + '.0'), None)
    elif param in names:
        vc = names.index(param)
    else:
        vc = names.index('Value') if 'Value' in names else None
    if vc is None:
        return None
    hits = []
    for row in ws.iter_rows(min_row=2):
        if str(row[tc].value).strip() != t1:
            continue
        if t2 and str(row[tc + 1].value).strip() != t2:
            continue
        if pc is not None and str(row[pc].value).strip() != param:
            continue
        hits.append(row[vc])
    return hits[0] if len(hits) == 1 else None


log = []
for (model, file), items in groups.items():
    path = M.ROOT / model / file
    with open(path, 'rb') as fh:
        wb = openpyxl.load_workbook(io.BytesIO(fh.read()))
    n_ok = 0
    for i, r in items:
        ws = wb[r['sheet']]
        cell = locate(ws, r['tech'], r['parameter'], r['year'])
        if cell is None:
            log.append([i, model, file, r['sheet'], r['tech'], r['parameter'], r['year'], 'refused: cell not found', ''])
            continue
        if not same(cell.value, r['before']):
            log.append([i, model, file, r['sheet'], r['tech'], r['parameter'], r['year'],
                        'refused: before differs', cell.value])
            continue
        if same(cell.value, r['after']):
            log.append([i, model, file, r['sheet'], r['tech'], r['parameter'], r['year'], 'unchanged', cell.coordinate])
            continue
        a = r['after']
        if str(a).strip() in ('', 'None'):
            cell.value = None
        elif str(a).startswith('='):
            cell.value = a
        elif num(a) is not None and str(a).strip() != '':
            f = float(a)
            cell.value = int(f) if f == int(f) and abs(f) < 1e12 and '.' not in str(a) else f
        else:
            cell.value = a
        n_ok += 1
        log.append([i, model, file, r['sheet'], r['tech'], r['parameter'], r['year'], 'written', cell.coordinate])
    if n_ok and not dry:
        ao_safe_save.save_ao_safely(wb, path)
    wb.close()
    del wb
    gc.collect()
    print(model, file, n_ok, 'written' + (' (dry run)' if dry else ''))
out = reg.replace('.csv', '_write_log.csv')
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['row', 'model', 'file', 'sheet', 'tech', 'parameter', 'year', 'result', 'cell'])
    w.writerows(log)
bad = [l for l in log if l[7].startswith('refused')]
print(len(log), 'rows;', len(bad), 'refused ->', out)
sys.exit(1 if bad else 0)
