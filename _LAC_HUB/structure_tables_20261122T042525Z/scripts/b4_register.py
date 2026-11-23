"""B4: tables_register.csv (one row per value or name moved out of the 26 code files) and
script_constants_accepted_job.csv (the constants that stay, each with its reason).

Inputs: work/fold/*.csv (written by b2_fold_check.py on the final files: old line, old literal, loader read),
work/sites.csv (flagged sites of the baseline scan; used for the batch and shell files, which were rewritten
whole), scan_after/gate1_rows.csv (rows of the scan of the branch, each with its reason).
Usage: py -I b4_register.py
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import glob
import os
import re
import sys

import yaml

ROOT = M.ROOT_S
JOB = ROOT + '/_LAC_HUB/structure_tables_20261122T042525Z'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b2_accept_rules import reason  # noqa: E402

EXE = yaml.safe_load(open(ROOT + '/config/execution/Config_MOMF_T1_AB.yaml', encoding='utf-8'))
CMP = yaml.safe_load(open(ROOT + '/config/compilation/Config_MOMF_T1_A.yaml', encoding='utf-8'))
COUNTRY_OF_DIR = {'CostaRica': 'CostaRica', 'DominicanRepublic': 'DominicanRepublic', 'Ecuador': 'Ecuador',
                  'Guatemala': 'Guatemala', 'Honduras': 'Honduras', 'Jamaica': 'Jamaica'}
T = {'controller': 'config/scenarios/rules/stage_controller.csv',
     'scenario': 'config/scenarios/scenario_catalogue.csv',
     'country': 'config/preparation/Config_country_codes.yaml',
     'tech': 'config/scenarios/technology_types.csv',
     'fuel': 'config/scenarios/fuel_types.csv',
     'emission': 'config/scenarios/emission_labels.csv',
     'values': 'inputs/scenarios/scenario_values.csv',
     'exe': 'config/execution/Config_MOMF_T1_AB.yaml',
     'cmp': 'config/compilation/Config_MOMF_T1_A.yaml'}
STR = r"""['"]([^'"]*)['"]"""


def args_of(expr):
    return re.findall(STR, expr)


def classify(expr, country):
    e = expr.split(' + ')[0] if ' + ' in expr and 'LT.scenario' not in expr.split(' + ')[0] else expr
    for part in expr.split(' + '):
        if 'LT.' in part or '_TB1' in part or '_TA2' in part:
            e = part
            break
    a = args_of(e)
    if '_TB1[' in e or '_TA2[' in e:
        k = a[0] if a else ''
        doc = EXE if '_TB1[' in e else CMP
        sec = f'countries.{country}.{k}' if k in ((doc.get('countries') or {}).get(country) or {}) else f'general.{k}'
        return T['exe' if '_TB1[' in e else 'cmp'], sec, 'system value'
    if 'LT.controller' in e:
        return T['controller'], 'name=' + (a[0] if a else '') + (f'; stage={a[1]}' if len(a) > 1 else ''), 'controller setting'
    if 'LT.scenario_value' in e:
        return T['values'], 'lever=' + (a[0] if a else ''), 'system value'
    if 'LT.scenario' in e:
        return T['scenario'], ('role=' if 'LT.scenario(' in e else 'group=') + (a[0] if a else 'in_use'), 'name'
    if 'LT.country' in e:
        return T['country'], 'country_data: ' + ', '.join(a), 'name'
    if 'LT.tech' in e:
        return T['tech'], 'group=' + (a[0] if a else ''), 'name' if 'tech_map' not in e else 'system value and name'
    if 'LT.fuel' in e:
        return T['fuel'], 'group=' + (a[0] if a else ''), 'name'
    if 'LT.emission' in e:
        return T['emission'], 'group=' + (a[0] if a else ''), 'name'
    return 'unclassified', expr, ''


rows = []
for path in sorted(glob.glob(JOB + '/work/fold/*.csv')):
    rel = os.path.basename(path)[:-4].replace('__', '/')
    country = COUNTRY_OF_DIR.get(rel.split('/')[0], 'all')
    for r in csv.DictReader(open(path, encoding='utf-8')):
        table, key, kind = classify(r['loader_read'], country)
        val = r['value']
        if kind == 'controller setting' and re.fullmatch(r'-?\d+(\.\d+)?(e-?\d+)?', str(val)) is None:
            kind = 'name'
        rows.append(dict(table=table, key=key, value=val, old_file=rel, old_line=r['old_line'], kind=kind,
                         loader_read=r['loader_read']))
# batch and shell files: rewritten whole; their run list now comes from lac_tables.solver_runs
for s in csv.DictReader(open(JOB + '/work/sites.csv', encoding='utf-8')):
    if s['file'] in ('stage0_run_all.bat', 'stage0_run_all.sh', 'stage3_run_all.bat'):
        k = s['kind']
        table = {'scenario': T['scenario'], 'country': T['country'], 'country code': T['country']}.get(k, '(removed)')
        rows.append(dict(table=table, key='lac_tables.solver_runs: countries, model folders and scenarios',
                         value=s['token'], old_file=s['file'], old_line=s['line'],
                         kind='name' if k != 'number' else 'removed (date or count in a comment or echo line)',
                         loader_read='py lac_tables.py solver-runs'))
cols = ['table', 'key', 'value', 'old_file', 'old_line', 'kind', 'loader_read']
with open(JOB + '/tables_register.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print('register rows', len(rows), 'unclassified', sum(1 for r in rows if r['table'] == 'unclassified'))
from collections import Counter  # noqa: E402
for (t, k), n in sorted(Counter((r['table'], r['kind']) for r in rows).items()):
    print(f'  {n:5d}  {t}  ({k})')

# accepted list of the job: the rows of the scan of the branch that stay, with their reason
g = JOB + '/scan_after/gate1_rows.csv'
if os.path.exists(g):
    acc = [r for r in csv.DictReader(open(g, encoding='utf-8')) if r['reason'] != 'NOT ACCEPTED']
    with open(JOB + '/script_constants_accepted_job.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['file', 'line', 'kind', 'value', 'reason'], extrasaction='ignore',
                           lineterminator='\n')
        w.writeheader()
        w.writerows(acc)
    print('accepted list rows', len(acc))
