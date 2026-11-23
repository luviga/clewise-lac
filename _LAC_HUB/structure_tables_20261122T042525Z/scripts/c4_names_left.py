"""C4 gate 2: scenario names left after the rename.

Reads a scope scan and an outside scan (c_scan.py) and writes names_left.csv, one row per (name, file, place
kind) with a count and a class:
  in scope, pipeline file      a file the stage pipeline runs, reads or writes (gate 2 counts these)
  in scope, not pipeline       a file in the scope folders that the pipeline neither runs nor reads (older script
                               copies, backup and reference workbooks, plot and test inputs of other tools)
  in scope, other tool keys    keys of the Costa Rica experiment manager YAML that the B1 runner does not read
  outside scope                every other tracked file (not changed, as the brief asks)
Only names other than BAU, NDC, LTS, LTSOPT and the generic word Default are listed.

Usage: py -I c4_names_left.py <scope scan> <outside scan> <names_left.csv>
"""
import csv
import sys
from collections import Counter

import yaml

ALLOWED = {'BAU', 'NDC', 'LTS', 'LTSOPT', 'Default'}
STAGE_DIRS = ('_STAGE0_OUTPUT/', '_STAGE1_OUTPUT/', '_STAGE2_INPUTS/', '_STAGE2_OUTPUT/', '_STAGE3_RESULTS/', 'config/',
              'inputs/')
ROOT_FILES = {'stage0_run.py', 'stage0_recommend_shares.py', 'stage0_collect_outputs.py', 'stage0_capacity_check.py',
              'stage1_share_analyzer_v16.py', 'stage2_apply_v2.py', 'stage3_apply.py', 'stage3_results.py',
              'stage0_run_all.bat', 'stage0_run_all.sh', 'stage3_run_all.bat', 'stage2_post_clean.py', 'stage0_clean.py',
              'stage1_clean.py', 'ao_safe_save.py', 'lac_tables.py', 'stage0_test.py', 'stage1_test_v16.py',
              'stage2_test_v2.py', 'stage3_test.py', 'stage2_demand_verify.py', 'snapshot_stage.py'}
cc = yaml.safe_load(open('config/preparation/Config_country_codes.yaml', encoding='utf-8'))['country_data']


MODEL_FILES = {'B1_Scenario_Config.xlsx', 'A2_Extra_Inputs/A-Xtra_Scenarios.xlsx', 'MOMF_T1_A.yaml',
               'Blend_Shares_0.pickle', 'SelectedResults.csv'}
NOT_PIPELINE = {'_STAGE1_OUTPUT/CONTROLLER_NEW_SCENARIOS_BEFORE.xlsx'}  # static copy of an earlier job, not read or written
OTHER_TOOL = {'CostaRica/CR_ENERGY/config_main_files/MOMF_B1_exp_manager.yaml'}


def cls(f):
    if f in NOT_PIPELINE:
        return 'in scope, not pipeline'
    if f in ROOT_FILES or f.startswith(STAGE_DIRS):
        return 'in scope, pipeline file'
    if f in OTHER_TOOL:
        return 'in scope, other tool keys'
    for c in cc:
        d = c['country_folder'] + '/' + c['model_dir'].rstrip('/') + '/'
        if f.startswith(d):
            rest = f[len(d):]
            files = set(MODEL_FILES)
            if c['name'] == 'CostaRica':  # the Costa Rica A2 reads MOMF_T1_A.yaml, not A-Xtra_Scenarios.xlsx
                files.discard('A2_Extra_Inputs/A-Xtra_Scenarios.xlsx')
            if rest in (c['a2_script'], c['b1_script']) or rest in files or \
                    rest.startswith(('A2_Output_Params/', 'B1_Output_Params/')):
                return 'in scope, pipeline file'
    return 'in scope, not pipeline'


def reason(c, f):
    if c != 'in scope, pipeline file':
        return {'in scope, not pipeline': 'file the stage pipeline neither runs nor reads; left as it is',
                'in scope, other tool keys': 'keys read only by the Costa Rica experiment manager tools; left as it is',
                'outside scope': 'outside the scope of Phase C; not changed'}[c]
    if f.endswith('B1_Scenario_Config.xlsx'):
        return ('description text of a row (column D), or a variant scenario row not run (Costa Rica '
                'NDCNEW_stage_2, LTSNEW_stage_2); the scenario column of the rows run holds the new names')
    if f.startswith('_STAGE2_INPUTS/'):
        return 'Note or Rationale text of override rows (provenance prose); the Scenario column holds the new names'
    if f.endswith('TotalAnnualMinCapacity.csv'):
        return ('Scenario label of rows that come from the A1 parametrization workbook (A1_Outputs), not through '
                'the A2 relabel; values equal the baseline')
    if f.endswith('Blend_Shares_0.pickle'):
        return 'written by an earlier Costa Rica B1 run; the runs of this job did not rewrite it'
    return 'see GAPS'


rows = Counter()
for path, where in ((sys.argv[1], 'scope'), (sys.argv[2], 'outside')):
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['name'] in ALLOWED:
            continue
        c = cls(r['file']) if where == 'scope' else 'outside scope'
        rows[(c, r['name'], r['file'], r['place_kind'])] += int(r['count'] or 0)
with open(sys.argv[3], 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['class', 'name', 'file', 'place_kind', 'count', 'reason'])
    for k in sorted(rows):
        w.writerow([*k, rows[k], reason(k[0], k[2])])
tot = Counter()
files = Counter()
for (c, n, f, k), v in rows.items():
    tot[(c, n)] += v
for (c, n, f, k) in rows:
    files[c] += 1
for k in sorted(tot):
    print(k, tot[k])
print('rows per class', dict(files))
