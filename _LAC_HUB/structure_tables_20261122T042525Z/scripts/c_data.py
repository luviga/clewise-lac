"""Phase C data edits (workbooks, CSV tables), with checks; results appended to workbook_checks.csv.

  py -I c_data.py retire   C2: rows of retired scenario names in the six B1_Scenario_Config.xlsx are deleted
                           (Excel row deletion, check by row content); the 'Other_Scenarios' row of the five
                           A-Xtra_Scenarios.xlsx is kept until C3 (the compilers still read it in C2).
  py -I c_data.py rename   C3: cells NDCNEW -> NDC and LTSNEW -> LTS in the six B1_Scenario_Config.xlsx and the
                           Stage 2 override workbooks; Scenario column of the Stage 2 override CSV files and of
                           inputs/scenarios/scenario_values.csv; the A-Xtra 'Other_Scenarios' rows deleted.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c_wb_edit as W  # noqa: E402

ROOT = M.ROOT
JOB = ROOT / '_LAC_HUB' / 'structure_tables_20261122T042525Z'
MODELS = ['CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic/RD_ENERGY', 'Ecuador/ECU_Energy',
          'Guatemala/GUA_ENERGY', 'Honduras/HON_ENERGY', 'Jamaica/JAM_ENERGY']
RETIRED = {'NDCcond', 'NDCincond', 'NDP', 'NDPAMB', 'NDCINC', 'LTS', 'NDC'}
RENAME = {'NDCNEW': 'NDC', 'LTSNEW': 'LTS'}
LOG = JOB / 'workbook_checks.csv'


def log(step, file, action, result):
    new = not LOG.exists()
    with open(LOG, 'a', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        if new:
            w.writerow(['step', 'file', 'action', 'result'])
        w.writerow([step, file, action, json.dumps(result, default=str)])
    print(step, file, action, result.get('check', ''), {k: v for k, v in result.items() if k not in ('examples',)})


def rename_csv(path, col='Scenario'):
    raw = path.read_bytes().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    rows = list(csv.reader(io.StringIO(raw, newline='')))
    j = rows[0].index(col)
    n = 0
    for r in rows[1:]:
        if j < len(r) and r[j] in RENAME:
            r[j] = RENAME[r[j]]
            n += 1
    out = io.StringIO()
    csv.writer(out, lineterminator=nl).writerows(rows)
    new = out.getvalue()
    # check: only the Scenario field of renamed rows changed
    a = list(csv.reader(io.StringIO(raw, newline='')))
    b = list(csv.reader(io.StringIO(new, newline='')))
    bad = sum(1 for x, y in zip(a, b) for k, (u, v) in enumerate(zip(x, y)) if u != v and not (k == j and RENAME.get(u) == v))
    if len(a) != len(b):
        bad += 1
    if not raw.endswith(nl):
        new = new[:-len(nl)]
    path.write_bytes(new.encode('utf-8'))
    return {'renamed': n, 'other_fields_differing': bad, 'check': 'PASS' if bad == 0 else 'FAIL'}


def main(step):
    if step == 'retire':
        for m in MODELS:
            p = ROOT / m / 'B1_Scenario_Config.xlsx'
            rows = W.find_rows(p, RETIRED)
            if rows:
                log('C2', str(p.relative_to(ROOT)), 'delete rows ' + json.dumps({k: len(v) for k, v in rows.items()}),
                    W.delete_rows(p, rows))
    elif step == 'rename':
        for m in MODELS:
            p = ROOT / m / 'B1_Scenario_Config.xlsx'
            log('C3', str(p.relative_to(ROOT)), 'rename cells', W.rename(p, RENAME))
        for p in sorted((ROOT / '_STAGE2_INPUTS').glob('*.xlsx')):
            log('C3', str(p.relative_to(ROOT)), 'rename cells', W.rename(p, RENAME))
        for p in sorted((ROOT / '_STAGE2_INPUTS').glob('*.csv')):
            log('C3', str(p.relative_to(ROOT)), 'rename Scenario column', rename_csv(p))
        log('C3', 'inputs/scenarios/scenario_values.csv', 'rename scenario column',
            rename_csv(ROOT / 'inputs/scenarios/scenario_values.csv', 'scenario'))
        for m in MODELS[1:]:
            p = ROOT / m / 'A2_Extra_Inputs' / 'A-Xtra_Scenarios.xlsx'
            rows = W.find_rows(p, {'Other_Scenarios'})
            if rows:
                log('C3', str(p.relative_to(ROOT)), 'delete Other_Scenarios row', W.delete_rows(p, rows))


if __name__ == '__main__':
    main(sys.argv[1])
