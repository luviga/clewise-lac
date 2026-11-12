"""Phase C correction: write the cells of proposals.csv whose stored value differs from new_value.

Found at the Phase C recompile (see GAPS, incidents):
- R6, Costa Rica and Honduras: their B1 scripts only round 'Overwrite' rows (no Security_Multiplier), so the
  history values written in Phase B (BAU divided by the multiplier) were too low; proposals.csv now holds the
  corrected values.
- R3, Ecuador: DIST_CRU activity upper limit 2021 and 2022 from 0 to 999,999 PJ.
Config cells: openpyxl + save_ao_safely. A-O_Parametrization cells: ao_cost_repair_manager manifest (apply, verify).
Run: py -I scripts/phaseC_fix_write.py [--dry-run]
"""
import csv, subprocess, sys
from pathlib import Path
import pandas as pd
import openpyxl

ROOT = Path(r'C:\clw_fix')
JOB = ROOT / '_LAC_HUB' / 'fix_run_20261111T200825Z'
sys.path.insert(0, str(ROOT))
from ao_safe_save import save_ao_safely  # noqa: E402

DRY = '--dry-run' in sys.argv
P = pd.read_csv(JOB / 'proposals.csv', dtype=str, keep_default_na=False)
log = open(JOB / 'logs' / 'phaseC_fix_write.log', 'a', encoding='utf-8', newline='\n')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s); log.write(s + '\n'); log.flush()


def same(stored, new):
    try:
        return abs(float(stored) - float(new)) <= 1e-9 * max(1.0, abs(float(new)))
    except (TypeError, ValueError):
        return str(stored).replace(' ', '') == str(new).replace(' ', '')


todo = []
for wbpath, g in P[P.kind.isin(['config_cell', 'ao_cell'])].groupby('workbook'):
    wb = openpyxl.load_workbook(ROOT / wbpath, data_only=False, read_only=True)
    for r in g.itertuples():
        v = wb[r.sheet][f'{r.column}{int(r.row)}'].value
        if not same(v, r.new_value):
            todo.append((wbpath, r, v))
    wb.close()
say('cells to write', len(todo), pd.Series([f'{t[1].country} {t[1].rule} {t[1].kind}' for t in todo]).value_counts().to_dict())

# config cells
cfg = [t for t in todo if t[1].kind == 'config_cell']
for wbpath in sorted({t[0] for t in cfg}):
    wb = openpyxl.load_workbook(ROOT / wbpath, data_only=False)
    n = 0
    for _, r, old in [t for t in cfg if t[0] == wbpath]:
        cell = wb[r.sheet][f'{r.column}{int(r.row)}']
        assert cell.value == old
        cell.value = str(r.new_value) if r.year in ('Exact_Years', 'Exact_Values', '2018-2024') else float(r.new_value)
        n += 1
    if not DRY:
        save_ao_safely(wb, ROOT / wbpath)
    wb.close()
    say('wrote', n, 'cells in', wbpath, '(dry run)' if DRY else '')

# A-O cells through the manager
fields = ['manifest_id', 'approved', 'decision', 'country', 'model_label', 'ao_path', 'sheet', 'row_index', 'tech', 'tech_name', 'parameter',
          'unit', 'year', 'old_value', 'new_value', 'source_kind', 'source_path', 'source_sheet', 'source_row_index', 'source_tech',
          'source_tech_name', 'source_unit', 'source_projection_mode', 'fuel_code', 'scenario', 'score', 'reason', 'row_fingerprint',
          'projection_mode_old', 'projection_mode_new', 'unit_conversion', 'generated_at']
ao = [t for t in todo if t[1].kind == 'ao_cell']
for wbpath in sorted({t[0] for t in ao}):
    rows = []
    for _, r, old in [t for t in ao if t[0] == wbpath]:
        m = {k: '' for k in fields}
        m.update(manifest_id=f'{r.country}-{r.rule}-{r.sheet}-{r.row}-{r.year}-phaseC', approved='YES', decision='APPLY', country=r.country,
                 model_label=r.country, ao_path=wbpath, sheet=r.sheet, row_index=str(int(r.row)), tech=r.Tech, parameter=r.Parameter,
                 year=str(r.year), old_value=repr(float(old)), new_value=repr(float(r.new_value)), source_kind='LAC_FIX_RUN proposals',
                 source_path='_LAC_HUB/fix_run_20261111T200825Z/proposals.csv', scenario='ALL', reason=r.rule,
                 row_fingerprint=f'{r.Tech}|{r.Parameter}', generated_at='2026-11-11')
        rows.append(m)
    tag = Path(wbpath).parts[0]
    mp = JOB / 'manifests' / f'manifest_{tag}_phaseC_fix.csv'
    with open(mp, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)
    cmd = [sys.executable, '-I', str(ROOT / 'ao_cost_repair_manager.py'), '--root', str(ROOT), 'apply', '--manifest', str(mp),
           '--output-dir', str(JOB / 'manifests'), '--dry-run' if DRY else '--apply']
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    say('$', ' '.join(cmd[2:])); say(out.stdout.strip()[-600:], out.stderr.strip()[-300:])
    if out.returncode != 0: raise SystemExit('manager apply failed')
    if not DRY:
        v = subprocess.run([sys.executable, '-I', str(ROOT / 'ao_cost_repair_manager.py'), '--root', str(ROOT), 'verify', '--manifest',
                            str(mp), '--expect', 'applied'], cwd=ROOT, capture_output=True, text=True)
        say('verify', mp.name, v.returncode, v.stdout.strip()[-300:])
        if v.returncode != 0: raise SystemExit('verify failed')
log.close()
