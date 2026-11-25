"""Step 9.5 table: objectives.csv, status and objective of every solve before this job (baseline) and after it.
Energy models: Stage 3 solves (stage_logs/<run>/solves_stage3.jsonl). Sector models and JAM_TRANSPORT:
sector_baseline.csv and work/sector_after.csv. Scenario names of JAM_TRANSPORT changed in step 8 (LTS of the
baseline is NDP after, NDCNEW is NDC, LTSNEW is LTS); the rows are matched on those names.
Usage: python -I objectives_csv.py <baseline run> <after run>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import json
import re
import sys

base_run, after_run = sys.argv[1], sys.argv[2]
ENERGY = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
          'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
          'Jamaica': 'Jamaica/JAM_ENERGY'}
JT_MAP = {'LTS': 'NDP', 'NDCNEW': 'NDC', 'LTSNEW': 'LTS'}


def energy(run):
    out = {}
    for ln in (M.JOB / 'stage_logs' / run / 'solves_stage3.jsonl').read_text(encoding='utf-8').splitlines():
        r = json.loads(ln)
        m = re.search(r'=\s*([-0-9.eE+]+)', r.get('objective', ''))
        out[(ENERGY[r['country']], r['scenario'])] = (r['status'], m.group(1) if m else '')
    return out


def sector(path, rename):
    out = {}
    for r in csv.DictReader(open(path, encoding='utf-8')):
        sc = r['scenario']
        if rename and r['model'] == 'Jamaica/JAM_TRANSPORT':
            sc = JT_MAP.get(sc, sc)
        out[(r['model'], sc)] = (r['status'], r['objective'])
    return out


b = energy(base_run) | sector(M.JOB / 'sector_baseline.csv', True)
a = energy(after_run) | sector(M.JOB / 'work' / 'sector_after.csv', False)
rows = []
for k in list(dict.fromkeys(list(b) + list(a))):
    sb, ob = b.get(k, ('not run', ''))
    sa, oa = a.get(k, ('not run', ''))
    ch = ''
    try:
        ch = f'{(float(oa) - float(ob)) / abs(float(ob)) * 100:.2f}' if float(ob) else ''
    except ValueError:
        pass
    rows.append([k[0], k[1], sb, ob, sa, oa, ch])
with open(M.JOB / 'objectives.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['model', 'scenario', 'status_baseline', 'objective_baseline', 'status_after', 'objective_after',
                'change_percent'])
    w.writerows(rows)
print(len(rows), 'rows')
