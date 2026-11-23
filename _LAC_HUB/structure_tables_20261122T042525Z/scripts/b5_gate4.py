"""Gate 4 of Phase B: the paths that differ from origin/main (committed, staged or in the working tree) are only
the code files of F2, the new tables, the loader, test files and the job folder; no workbook differs.
Usage: py -I b5_gate4.py   (prints every path with its class and FAIL for any other path)"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import subprocess
import sys

ROOT = M.ROOT_S
CODE = {'stage0_run.py', 'stage0_recommend_shares.py', 'stage0_collect_outputs.py', 'stage0_capacity_check.py',
        'stage1_share_analyzer_v16.py', 'stage2_apply_v2.py', 'stage3_apply.py', 'stage3_results.py',
        'stage0_run_all.bat', 'stage0_run_all.sh', 'stage3_run_all.bat', 'stage2_post_clean.py', 'stage0_clean.py',
        'ao_safe_save.py'}
MODEL_CODE = {'CostaRica/CR_ENERGY/t1_confection/A2_Compiler_CostaRica.py',
              'DominicanRepublic/RD_ENERGY/A2_Compiler_DominicanRepublic.py', 'Ecuador/ECU_Energy/A2_Compiler_Ecuador.py',
              'Guatemala/GUA_ENERGY/A2_Compiler_Guatemala.py', 'Honduras/HON_ENERGY/A2_Compiler_Honduras.py',
              'Jamaica/JAM_ENERGY/A2_Compiler_Jamaica.py',
              'CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py',
              'DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py',
              'Ecuador/ECU_Energy/B1_Base_Scenarios_Adj_Parallel.py',
              'Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py',
              'Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel_Honduras.py',
              'Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel_Jamaica.py'}
TABLES = ('config/', 'inputs/')


def cls(p):
    if p in CODE or p in MODEL_CODE:
        return 'code file of F2'
    if p.startswith(TABLES):
        return 'new table'
    if p == 'lac_tables.py':
        return 'loader'
    if p.startswith('_LAC_HUB/structure_tables_20261122T042525Z/'):
        return 'job folder'
    if 'test' in p.split('/')[-1] and p.endswith('.py'):
        return 'test file'
    return None


out = set()
for args in (['diff', '--name-only', 'origin/main'], ['diff', '--name-only', '--cached', 'origin/main'],
             ['ls-files', '--others', '--exclude-standard']):
    out |= set(subprocess.run(['git', '-C', ROOT, *args], capture_output=True, text=True).stdout.split())
bad = 0
counts = {}
for p in sorted(out):
    c = cls(p)
    if c is None or p.lower().endswith(('.xlsx', '.xlsm')):
        bad += 1
        print('FAIL', p)
    else:
        counts[c] = counts.get(c, 0) + 1
print(counts, 'other paths:', bad)
sys.exit(1 if bad else 0)
