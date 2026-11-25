"""Step 7.8 table: value_register.csv of the job folder, every register of work/ in one table with the step that
wrote it. Rows of a later register on the same cell come after the earlier rows (the last row of a cell is the
value in the workbook). Write logs are not merged.
Usage: python -I build_value_register.py"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high', 'step']
ORDER = [
    ('register_transport.csv', '2.5 transport targets'),
    ('register_hydrogen.csv', '3 hydrogen adoption rows'),
    ('register_history.csv', '5.1 history'),
    ('register_history_fix1.csv', '5.1 history, after the solves (fix 1)'),
    ('register_history_fix2.csv', '5.1 history, after the solves (fix 2)'),
    ('register_history_fix3.csv', '5.1 history, after the solves (fix 3)'),
    ('register_history_fix4.csv', '5.1 history, after the solves (fix 4)'),
    ('register_history_fix5.csv', '5.1 history, after the solves (fix 5)'),
    ('register_history_fix6.csv', '5.1 history, after the solves (fix 6)'),
    ('register_policy_history_dr1.csv', '5.3 policy history rows (DR), pass 1'),
    ('register_policy_history_dr2.csv', '5.3 policy plant caps (DR), pass 2'),
    ('register_policy_history_dr3.csv', '5.3 policy plant limits (DR), pass 3'),
    ('register_policy_history_dr4.csv', '5.3 policy-only plant caps opened (DR), pass 4'),
    ('register_policy_history_cr.csv', '5.3 policy plant limits (CR)'),
    ('register_imports.csv', '6.1-6.2 imports'),
    ('register_ear.csv', '6.3 emission factors'),
    ('register_ear_jam.csv', '6.3 emission factors (Jamaica road fuels)'),
    ('value_register_vehicles.csv', '7.1-7.4 vehicles'),
    ('register_distance_revert.csv', '7.4 distances reverted'),
    ('register_sector.csv', '7.5 sector costs'),
    ('register_penalties.csv', '7.6 penalties and 5.2 PPBIM'),
    ('register_discount.csv', '7.7 discount rate'),
    ('register_jam_transport.csv', '8 labels'),
]
rows = []
for name, step in ORDER:
    p = M.JOB / 'work' / name
    if not p.exists():
        print('missing', name)
        continue
    for r in csv.DictReader(open(p, encoding='utf-8')):
        if 'model' not in r:   # label register of step 8: sheet, cell, column, before, after
            r = {'model': 'Jamaica/JAM_TRANSPORT', 'file': 'B1_Scenario_Config.xlsx', 'sheet': r['sheet'],
                 'tech': r['cell'], 'parameter': r['column'], 'before': r['before'], 'after': r['after'],
                 'derivation': 'scenario label (step 8)'}
        rows.append({k: r.get(k, '') for k in FIELDS[:-1]} | {'step': step})
with open(M.JOB / 'value_register.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows')
