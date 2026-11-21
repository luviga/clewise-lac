"""B3 gates. For every workbook in proposals.csv:
  (1) every proposed cell holds its target (value within relative 1e-9, or the formula text; config text exact; new rows present);
  (2) cell-by-cell comparison (stored values and formulas) against the base snapshot: differences only at listed cells, at formula
      cells that depend on them (dependency closure computed from the base formulas, same sheet), and in appended / inserted rows;
      Fixed Horizon Parameters is compared by (Tech, Parameter);
  (3) no formula cell without a stored value;
  (4) every other A-O workbook of the six models byte-identical to the base;
  (5) Stage 2 CSVs changed only on listed lines.
Writes write_check.csv (one line per check) and logs/write_check_detail.csv."""
import glob, hashlib, json, os, re
import openpyxl
import pandas as pd
from openpyxl.utils import column_index_from_string, get_column_letter

ROOT = 'C:/clw_fix/'
BASE = 'C:/clw_base_4ba69d6/'
JOB = ROOT + '_LAC_HUB/fix_run2_20261120T225823Z'
P = pd.read_csv(JOB + '/proposals.csv', dtype=str, keep_default_na=False)
P = P[~P.kind.isin(['d8_target', 'doc'])]
checks, detail = [], []
REF = re.compile(r"(?<![A-Za-z!'])\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?")


def close(a, b):
    try:
        return abs(float(a) - float(b)) <= 1e-9 * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


def deps(wsf):
    """reverse dependency map: cell -> formula cells that reference it (same sheet, no sheet-qualified refs)."""
    rev = {}
    for row in wsf.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                f = re.sub(r"'[^']*'![$A-Z0-9:]+|[A-Za-z_]+![$A-Z0-9:]+", '', c.value)
                for m in REF.finditer(f):
                    c1, r1 = column_index_from_string(m.group(1)), int(m.group(2))
                    c2 = column_index_from_string(m.group(3)) if m.group(3) else c1
                    r2 = int(m.group(4)) if m.group(4) else r1
                    for rr in range(min(r1, r2), max(r1, r2) + 1):
                        for cc in range(min(c1, c2), max(c1, c2) + 1):
                            rev.setdefault((rr, cc), set()).add((c.row, c.column))
    return rev


for wbpath, g in P.groupby('workbook'):
    if wbpath.endswith('.csv'):
        continue
    nf = openpyxl.load_workbook(ROOT + wbpath, data_only=False)
    nv = openpyxl.load_workbook(ROOT + wbpath, data_only=True)
    bf = openpyxl.load_workbook(BASE + wbpath, data_only=False)
    bv = openpyxl.load_workbook(BASE + wbpath, data_only=True)
    ok1 = bad1 = 0
    listed = {}
    for r in g.itertuples():
        if r.kind in ('config_row', 'fhp_newrow'):
            continue
        listed.setdefault(r.sheet, set()).add((int(r.row), column_index_from_string(r.column)))
        cf, cv = nf[r.sheet][f'{r.column}{r.row}'].value, nv[r.sheet][f'{r.column}{r.row}'].value
        if r.kind in ('ao_cell', 'demand_cell', 'cfg_num'):
            good = close(cv, r.new_value) and not (isinstance(cf, str) and cf.startswith('='))
        elif r.kind == 'ao_formula':
            good = cf == r.new_formula and cv is not None
            if r.new_value:
                good = good and close(cv, r.new_value)
        else:
            good = str(cf) == r.new_value
        ok1 += good
        bad1 += not good
        if not good:
            detail.append(dict(check='target', workbook=wbpath, sheet=r.sheet, cell=f'{r.column}{r.row}', expected=r.new_formula or r.new_value,
                               found=f'{cf!r} / {cv!r}'))
    # new rows present
    for r in g[g.kind.isin(['config_row', 'fhp_newrow'])].itertuples():
        rec = json.loads(r.new_value)
        ws = nf[r.sheet]
        h = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
        tk = 'Tech_Set' if 'Tech_Set' in h else 'Tech'
        found = False
        for rr in range(2, ws.max_row + 1):
            if r.kind == 'fhp_newrow':
                if ws.cell(rr, h['Tech']).value == rec['Tech'] and ws.cell(rr, h['Parameter']).value == rec['Parameter']:
                    found = close(nv[r.sheet].cell(rr, h['Value']).value, rec['Value'])
            elif all(str(ws.cell(rr, h[k]).value) == str(rec[k]) for k in ('Scenario', 'Parameter', tk)) and \
                    (r.sheet != 'Electrical' or str(ws.cell(rr, h['Exact_Values']).value) == rec['Exact_Values']):
                found = True
        ok1 += found
        bad1 += not found
        if not found:
            detail.append(dict(check='new row', workbook=wbpath, sheet=r.sheet, cell=r.row, expected=r.new_value[:80], found='absent'))
    checks.append(dict(check='1 targets written', workbook=wbpath, ok=ok1, bad=bad1))
    # (2) differences against base
    unexpected = expected_dep = 0
    for ws in bf.worksheets:
        name = ws.title
        if name == 'Fixed Horizon Parameters' and any(g.kind == 'fhp_newrow'):
            def keyed(wf, wv):
                h = {wf.cell(1, j).value: j for j in range(1, wf.max_column + 1)}
                return {(wf.cell(r, h['Tech']).value, wf.cell(r, h['Parameter']).value): wv.cell(r, h['Value']).value
                        for r in range(2, wf.max_row + 1) if wf.cell(r, h['Tech']).value}
            kb, kn = keyed(ws, bv[name]), keyed(nf[name], nv[name])
            lt = {(r.Tech, r.Parameter) for r in g.itertuples() if r.sheet == name}
            for k in set(kb) | set(kn):
                if not close(kb.get(k), kn.get(k)) and k not in lt:
                    unexpected += 1
                    detail.append(dict(check='unexpected', workbook=wbpath, sheet=name, cell=str(k), expected=kb.get(k), found=kn.get(k)))
            continue
        rev = deps(ws)
        L = listed.get(name, set())
        closure, stack = set(L), list(L)
        while stack:
            x = stack.pop()
            for y in rev.get(x, ()):
                if y not in closure:
                    closure.add(y)
                    stack.append(y)
        wn, wnv, wbv = nf[name], nv[name], bv[name]
        base_rows = ws.max_row
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                a, b = ws.cell(r, c).value, wn.cell(r, c).value
                av, bvv = wbv.cell(r, c).value, wnv.cell(r, c).value
                same = (a == b or close(a, b)) and (av == bvv or close(av, bvv))
                if same:
                    continue
                if (r, c) in closure:
                    expected_dep += (r, c) not in L
                    continue
                if r > base_rows and a is None:
                    continue      # appended row
                unexpected += 1
                detail.append(dict(check='unexpected', workbook=wbpath, sheet=name, cell=f'{get_column_letter(c)}{r}',
                                   expected=f'{a!r} / {av!r}', found=f'{b!r} / {bvv!r}'))
    checks.append(dict(check='2 changes only at listed and dependent cells', workbook=wbpath, ok=expected_dep, bad=unexpected))
    # (3) blank formula cells
    blanks = 0
    for ws in nf.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.data_type == 'f' and nv[ws.title][c.coordinate].value is None:
                    blanks += 1
    checks.append(dict(check='3 no formula without stored value', workbook=wbpath, ok=0, bad=blanks))
# (4) other A-O workbooks byte-identical
changed = set(P.workbook)
for f in sorted(glob.glob(BASE + '**/A1_Outputs/*.xlsx', recursive=True)) + sorted(glob.glob(BASE + '**/B1_Scenario_Config.xlsx', recursive=True)):
    rel = f[len(BASE):].replace('\\', '/')
    if rel in changed:
        continue
    same = hashlib.sha256(open(f, 'rb').read()).hexdigest() == hashlib.sha256(open(ROOT + rel, 'rb').read()).hexdigest()
    checks.append(dict(check='4 unchanged workbook byte-identical', workbook=rel, ok=int(same), bad=int(not same)))
# (5) Stage 2 CSVs
for f in sorted(glob.glob(ROOT + '_STAGE2_INPUTS/*.csv')):
    rel = f[len(ROOT):].replace('\\', '/')
    a = open(BASE + rel, 'rb').read().decode('utf-8').splitlines()
    b = open(f, 'rb').read().decode('utf-8').splitlines()
    listed_lines = set(P[(P.workbook == rel) & (P.kind == 'csv_line')].new_value)
    extra = [x for x in b if x not in a and x not in listed_lines]
    missing = [x for x in a if x not in b]
    checks.append(dict(check='5 stage 2 csv only listed lines', workbook=rel, ok=len(b) - len(extra), bad=len(extra) + len(missing)))
C = pd.DataFrame(checks)
C.to_csv(JOB + '/write_check.csv', index=False, lineterminator='\n')
pd.DataFrame(detail).to_csv(JOB + '/logs/write_check_detail.csv', index=False, lineterminator='\n')
print(C.to_string())
print('WRITE CHECK', 'PASS' if C.bad.sum() == 0 else f'FAIL ({int(C.bad.sum())})')
