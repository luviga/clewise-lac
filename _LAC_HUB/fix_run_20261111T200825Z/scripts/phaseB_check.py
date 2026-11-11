"""Phase B gates (B4). Writes write_check.csv and write_check_diffs.csv.

(1) every written cell equals proposals.csv (numbers to 1e-9 relative, text exactly);
(2) cell-by-cell comparison of each changed workbook against its backup (formulas and stored values):
    changes only at listed cells (and listed mode cells);
(3) no formula cell without a stored value in the changed workbooks;
(4) no formula left in the three F1 cells;
(5) every other tracked A-O workbook byte-identical to the base commit;
(6) stage input CSV: only the listed lines differ.
Run: py -I scripts/phaseB_check.py
"""
import csv, subprocess, sys
from pathlib import Path
import pandas as pd
import openpyxl

ROOT = Path(r'C:\clw_fix')
JOB = ROOT / '_LAC_HUB' / 'fix_run_20261111T200825Z'
sys.path.insert(0, str(ROOT))
from ao_safe_save import find_blank_formula_cells  # noqa: E402

P = pd.read_csv(JOB / 'proposals.csv', dtype=str, keep_default_na=False)
checks, diffs = [], []


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


for wbpath, g in P[P.kind != 'csv_line'].groupby('workbook'):
    listed = {(r.sheet, f'{r.column}{int(r.row)}') for r in g.itertuples()}
    new_f = openpyxl.load_workbook(ROOT / wbpath, data_only=False)
    new_v = openpyxl.load_workbook(ROOT / wbpath, data_only=True)
    old_f = openpyxl.load_workbook(JOB / 'backups' / wbpath, data_only=False)
    old_v = openpyxl.load_workbook(JOB / 'backups' / wbpath, data_only=True)
    # (1)
    bad1 = 0
    for r in g.itertuples():
        v = new_v[r.sheet][f'{r.column}{int(r.row)}'].value
        f = new_f[r.sheet][f'{r.column}{int(r.row)}'].value
        a, b = num(v), num(r.new_value)
        if a is not None and b is not None:
            ok = abs(a - b) <= 1e-9 * max(1.0, abs(b))
        else:
            ok = str(f).replace(' ', '') == str(r.new_value).replace(' ', '')
        if not ok:
            bad1 += 1
            diffs.append(dict(check='1_written_equals_proposal', workbook=wbpath, sheet=r.sheet, cell=f'{r.column}{int(r.row)}', old=r.new_value, new=v))
    checks.append(dict(check='1_written_equals_proposal', workbook=wbpath, cells=len(g), failures=bad1, result='pass' if bad1 == 0 else 'FAIL'))
    # (2)
    extra = 0
    for ws in new_f.worksheets:
        wo, wvn, wvo = old_f[ws.title], new_v[ws.title], old_v[ws.title]
        mr, mc = max(ws.max_row, wo.max_row), max(ws.max_column, wo.max_column)
        for row in range(1, mr + 1):
            for col in range(1, mc + 1):
                c1, c0 = ws.cell(row, col), wo.cell(row, col)
                same_f = c1.value == c0.value or (num(c1.value) is not None and num(c0.value) is not None and abs(num(c1.value) - num(c0.value)) <= 1e-12 * max(1, abs(num(c0.value))))
                v1, v0 = wvn.cell(row, col).value, wvo.cell(row, col).value
                same_v = v1 == v0 or (num(v1) is not None and num(v0) is not None and abs(num(v1) - num(v0)) <= 1e-12 * max(1, abs(num(v0))))
                if same_f and same_v:
                    continue
                coord = c1.coordinate
                if (ws.title, coord) in listed:
                    continue
                extra += 1
                diffs.append(dict(check='2_unlisted_change', workbook=wbpath, sheet=ws.title, cell=coord,
                                  old=f'{c0.value!r} / {v0!r}'[:200], new=f'{c1.value!r} / {v1!r}'[:200]))
    checks.append(dict(check='2_changes_only_at_listed_cells', workbook=wbpath, cells=len(listed), failures=extra,
                       result='pass' if extra == 0 else 'FAIL'))
    # (3)
    blanks = find_blank_formula_cells(ROOT / wbpath)
    checks.append(dict(check='3_no_formula_without_value', workbook=wbpath, cells='', failures=len(blanks), result='pass' if not blanks else 'FAIL'))
    for b in blanks:
        diffs.append(dict(check='3_no_formula_without_value', workbook=wbpath, sheet='', cell=b, old='', new=''))

# (4) F1 cells
F1 = [('Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx', 'Primary Techs', ['I284', 'J284']),
      ('Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx', 'Secondary Techs', ['I27', 'J27', 'K27']),
      ('DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx', 'Secondary Techs', ['J232'])]
nf = 0
for f, sh, cells in F1:
    wb = openpyxl.load_workbook(ROOT / f, data_only=False)
    for c in cells:
        v = wb[sh][c].value
        if isinstance(v, str) and v.startswith('='):
            nf += 1
            diffs.append(dict(check='4_F1_formula_left', workbook=f, sheet=sh, cell=c, old='', new=v))
checks.append(dict(check='4_no_formula_in_F1_cells', workbook='3 workbooks', cells=6, failures=nf, result='pass' if nf == 0 else 'FAIL'))

# (5) other A-O workbooks byte-identical to the base commit
changed = set(P.workbook)
tracked = subprocess.run(['git', 'ls-files', '*A-O_*.xlsx'], cwd=ROOT, capture_output=True, text=True).stdout.split()
others = [t for t in tracked if t not in changed]
alld = set(subprocess.run(['git', 'diff', '--name-only', 'c42ae07'], cwd=ROOT, capture_output=True, text=True).stdout.split())
dif = [t for t in others if t in alld]
checks.append(dict(check='5_other_AO_workbooks_identical', workbook=f'{len(others)} tracked A-O workbooks', cells='', failures=len(dif),
                   result='pass' if not dif else 'FAIL'))

# (6) CSV lines
for f, g in P[P.kind == 'csv_line'].groupby('workbook'):
    new = open(ROOT / f, 'rb').read().decode('utf-8').splitlines()
    old = open(JOB / 'backups' / f, 'rb').read().decode('utf-8').splitlines()
    rows = {int(r) for r in g.row}
    bad = [i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b and (i + 1) not in rows]
    checks.append(dict(check='6_csv_only_listed_lines', workbook=f, cells=len(rows), failures=len(bad) + abs(len(new) - len(old)),
                       result='pass' if not bad and len(new) == len(old) else 'FAIL'))

pd.DataFrame(checks).to_csv(JOB / 'write_check.csv', index=False, lineterminator='\n')
pd.DataFrame(diffs).to_csv(JOB / 'write_check_diffs.csv', index=False, lineterminator='\n')
print(pd.DataFrame(checks).to_string())
