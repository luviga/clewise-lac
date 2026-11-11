"""Phase B: back up and write every cell of proposals.csv.

- A-O_Parametrization cells and mode cells: ao_cost_repair_manager.py manifests (apply, then verify),
  saved through save_ao_safely. Formula cells (R1) go in a separate manifest with --ignore-old-value-mismatch.
- New A-O rows (kind ao_newrow), A-O_Demand cells (demand_cell) and B1_Scenario_Config cells (config_cell):
  openpyxl + save_ao_safely.
- Stage input CSV lines (csv_line): text replacement keeping each line's ending.
Run: py -I scripts/phaseB_write.py [--dry-run]
"""
import csv, hashlib, json, os, shutil, subprocess, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.utils import column_index_from_string

ROOT = Path(r'C:\clw_fix')
JOB = ROOT / '_LAC_HUB' / 'fix_run_20261111T200825Z'
sys.path.insert(0, str(ROOT))
from ao_safe_save import save_ao_safely  # noqa: E402

DRY = '--dry-run' in sys.argv
P = pd.read_csv(JOB / 'proposals.csv', dtype=str, keep_default_na=False)
files = sorted(set(P.workbook))
log = open(JOB / 'logs' / 'phaseB_write.log', 'a', encoding='utf-8', newline='\n')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s); log.write(s + '\n'); log.flush()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---------- B1 backups ----------
if not DRY:
    rows = []
    for f in files:
        src = ROOT / f
        dst = JOB / 'backups' / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
        rows.append(dict(file=f, sha256_before=sha(src), backup=str(dst.relative_to(JOB)).replace('\\', '/'), sha256_backup=sha(dst)))
    with open(JOB / 'backups' / 'backup_manifest.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    say('backups', len(rows))

# ---------- A-O cells through the manager ----------
ao = P[P.kind.isin(['ao_cell', 'ao_mode'])]
fields = ['manifest_id', 'approved', 'decision', 'country', 'model_label', 'ao_path', 'sheet', 'row_index', 'tech', 'tech_name', 'parameter',
          'unit', 'year', 'old_value', 'new_value', 'source_kind', 'source_path', 'source_sheet', 'source_row_index', 'source_tech',
          'source_tech_name', 'source_unit', 'source_projection_mode', 'fuel_code', 'scenario', 'score', 'reason', 'row_fingerprint',
          'projection_mode_old', 'projection_mode_new', 'unit_conversion', 'generated_at']
for wbpath, g in ao.groupby('workbook'):
    wb = openpyxl.load_workbook(ROOT / wbpath, data_only=False)
    modes = {(r.sheet, int(r.row)): r.new_value for r in g[g.kind == 'ao_mode'].itertuples()}
    plain, formula = [], []
    for r in g[g.kind == 'ao_cell'].itertuples():
        ws = wb[r.sheet]
        cell = ws[f'{r.column}{int(r.row)}']
        cur = cell.value
        tech = ws.cell(int(r.row), 2).value
        assert str(tech).strip() == r.Tech, (wbpath, r.sheet, r.row, tech, r.Tech)
        is_f = isinstance(cur, str) and cur.startswith('=')
        if not is_f and r.current_value not in ('', 'nan') and cur is not None:
            assert abs(float(cur) - float(r.current_value)) <= 1e-6 * max(1, abs(float(cur))), (wbpath, r.sheet, r.row, r.column, cur, r.current_value)
        m = {k: '' for k in fields}
        m.update(manifest_id=f'{r.country}-{r.rule}-{r.sheet}-{r.row}-{r.year}', approved='YES', decision='APPLY', country=r.country,
                 model_label=r.country, ao_path=wbpath, sheet=r.sheet, row_index=str(int(r.row)), tech=r.Tech, parameter=r.Parameter,
                 year=str(r.year), old_value='' if cur is None else (cur if is_f else repr(float(cur))), new_value=repr(float(r.new_value)),
                 source_kind='LAC_FIX_RUN proposals', source_path='_LAC_HUB/fix_run_20261111T200825Z/proposals.csv', scenario='ALL',
                 reason=r.rule, row_fingerprint=f'{r.Tech}|{r.Parameter}',
                 projection_mode_new=modes.pop((r.sheet, int(r.row)), ''), generated_at='2026-11-11')
        (formula if is_f else plain).append(m)
    assert not modes, ('mode rows without a cell row', modes)
    wb.close()
    tag = Path(wbpath).parts[0]
    for name, rows, extra in [('plain', plain, []), ('formula', formula, ['--ignore-old-value-mismatch'])]:
        if not rows: continue
        mp = JOB / 'manifests' / f'manifest_{tag}_{name}.csv'
        mp.parent.mkdir(exist_ok=True)
        with open(mp, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)
        cmd = [sys.executable, '-I', str(ROOT / 'ao_cost_repair_manager.py'), '--root', str(ROOT), 'apply', '--manifest', str(mp),
               '--output-dir', str(JOB / 'manifests'), '--dry-run' if DRY else '--apply'] + extra
        say('$', ' '.join(cmd[2:]))
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        say(out.stdout.strip(), out.stderr.strip())
        if out.returncode != 0: raise SystemExit('manager apply failed')
        if not DRY:
            v = subprocess.run([sys.executable, '-I', str(ROOT / 'ao_cost_repair_manager.py'), '--root', str(ROOT), 'verify', '--manifest',
                                str(mp), '--expect', 'applied'], cwd=ROOT, capture_output=True, text=True)
            say('verify', mp.name, v.returncode, v.stdout.strip()[-300:])
            if v.returncode != 0: raise SystemExit('verify failed')

# ---------- other workbook cells and new rows ----------
def _val(x):
    if x is None or x == '':
        return None
    if isinstance(x, str) and x.startswith('='):
        return x
    try:
        return float(x)
    except (TypeError, ValueError):
        return x


other = P[P.kind.isin(['config_cell', 'demand_cell', 'ao_newrow'])]
for wbpath, g in other.groupby('workbook'):
    wb = openpyxl.load_workbook(ROOT / wbpath, data_only=False)
    n = 0
    for r in g.itertuples():
        ws = wb[r.sheet]
        rr = int(r.row)
        cell = ws[f'{r.column}{rr}']
        cur = cell.value
        if r.kind == 'ao_newrow':
            if cur is not None:
                raise SystemExit(f'new row cell {r.column}{rr} not empty in {wbpath}: {cur!r}')
        elif r.current_value not in ('', 'nan'):
            cv = _val(r.current_value)
            if isinstance(cv, float) and not isinstance(cur, str):
                assert cur is not None and abs(float(cur) - cv) <= 1e-9 * max(1.0, abs(cv)), (wbpath, r.sheet, rr, r.column, cur, cv)
            else:
                assert str(cur).replace(' ', '') == str(r.current_value).replace(' ', ''), (wbpath, r.sheet, rr, r.column, str(cur)[:80], r.current_value[:80])
        nv = _val(r.new_value)
        if r.kind == 'config_cell' and r.Parameter and r.year in ('Exact_Years', 'Exact_Values', '2018-2024'):
            nv = str(r.new_value)  # exact-year lists stay text, as B1 reads them with astype(str)
        cell.value = nv
        n += 1
    if not DRY:
        save_ao_safely(wb, ROOT / wbpath)
    wb.close()
    say('wrote', n, 'cells in', wbpath, '(dry run)' if DRY else '')

CRLF = chr(13) + chr(10)
# ---------- stage input CSV lines ----------
for f, g in P[P.kind == 'csv_line'].groupby('workbook'):
    raw = open(ROOT / f, 'rb').read().decode('utf-8')
    lines = raw.splitlines(keepends=True)
    for r in g.itertuples():
        i = int(r.row) - 1
        body = lines[i].rstrip(CRLF)
        end = lines[i][len(body):]
        old = r.derivation.split("' -> '")[0].split("'", 1)[1]
        new = r.derivation.split("' -> '")[1].rstrip("'")
        assert body == old, (f, r.row, body, old)
        lines[i] = new + end
    if not DRY:
        open(ROOT / f, 'wb').write(''.join(lines).encode('utf-8'))
    say('wrote', len(g), 'lines in', f, '(dry run)' if DRY else '')
log.close()
