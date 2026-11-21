"""Phase D: run the steps of one pipeline stage with Anaconda Python from C:/clw_fix (commands of PIPELINE_WORKFLOW.md),
one log per step in stage_logs/, one JSON line per step in stage_logs/stage_status.jsonl. Batch files by full path.
Usage: py -I scripts/stage_runner.py <0|1|2|3> [--from N] [--only N]"""
import datetime, json, os, subprocess, sys, time

ROOT = 'C:/clw_fix'
JOB = ROOT + '/_LAC_HUB/fix_run2_20261120T225823Z'
LOG = JOB + '/stage_logs'
PY = r'C:\Users\luisfernando\anaconda3\python.exe'
DEN = r'_STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx'
STEPS = {
    '0': [('stage0_clean', [PY, 'stage0_clean.py', '--confirm']), ('stage0_run', [PY, 'stage0_run.py']),
          ('stage0_run_all', ['cmd', '/c', r'C:\clw_fix\stage0_run_all.bat']), ('stage0_collect_outputs', [PY, 'stage0_collect_outputs.py']),
          ('stage0_capacity_check', [PY, 'stage0_capacity_check.py']), ('stage0_recommend_shares', [PY, 'stage0_recommend_shares.py']),
          ('stage0_test', [PY, 'stage0_test.py'])],
    '1': [('stage1_share_analyzer_v16', [PY, 'stage1_share_analyzer_v16.py']), ('stage1_test_v16', [PY, 'stage1_test_v16.py', '--skip-run'])],
    '2': [('stage2_apply_v2', [PY, 'stage2_apply_v2.py', '--root', '.', '--stage0-denom', DEN]),
          ('stage2_test_v2', [PY, 'stage2_test_v2.py', '--stage0-denom', DEN])],
    '3': [('stage3_apply', [PY, 'stage3_apply.py', '--root', '.', '--clean', '--uncap-pp-maxcap', '--skip-orphan-cap', 'Guatemala']),
          ('stage3_test', [PY, 'stage3_test.py', '--root', '.']), ('stage3_run_all', ['cmd', '/c', r'C:\clw_fix\stage3_run_all.bat']),
          ('stage3_results', [PY, 'stage3_results.py', '--root', '.'])],
}
st = sys.argv[1]
start = int(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 1
only = int(sys.argv[sys.argv.index('--only') + 1]) if '--only' in sys.argv else None
os.makedirs(LOG, exist_ok=True)
env = dict(os.environ)
env['PATH'] = os.pathsep.join(p for p in env['PATH'].split(os.pathsep) if 'glpsol_wrap' not in p)
env['PYTHONIOENCODING'] = 'utf-8'
for i, (name, cmd) in enumerate(STEPS[st], start=1):
    if i < start or (only and i != only):
        continue
    lf = f'{LOG}/s{st}_{i:02d}_{name}.log'
    t0 = time.time()
    su = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(lf, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('$ ' + ' '.join(os.path.basename(c) if c == PY else c for c in cmd) + '\n')
        fh.flush()
        r = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, env=env)
    rec = dict(stage=st, step=i, name=name, start_utc=su, seconds=round(time.time() - t0, 1), exit=r.returncode,
               log=os.path.basename(lf))
    with open(f'{LOG}/stage_status.jsonl', 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(rec) + '\n')
    print(json.dumps(rec), flush=True)
