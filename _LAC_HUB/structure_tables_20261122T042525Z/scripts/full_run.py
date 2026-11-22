"""One full pipeline run: A2 and B1 for the six countries, Stages 0 to 3 with their tests, the two unit-test files.

Usage: py -I full_run.py <run_name> [--from-step NAME]
Logs in stage_logs/<run_name>/. One JSON line per step in stage_logs/<run_name>/run_steps.jsonl.
Solver output .txt files over 500 MB of a finished stage are deleted when free disk on C: is below 80 GB
(after solve_headers has read their headers and the stage's extraction step has finished).
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = M.ROOT
JOB = ROOT / '_LAC_HUB' / 'structure_tables_20261122T042525Z'
S = JOB / 'scripts'
PY = M.ANACONDA
COUNTRIES = ['CostaRica', 'DominicanRepublic', 'Ecuador', 'Guatemala', 'Honduras', 'Jamaica']
MODEL = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
         "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
         "Jamaica": "Jamaica/JAM_ENERGY"}

run = sys.argv[1]
start_from = sys.argv[sys.argv.index('--from-step') + 1] if '--from-step' in sys.argv else None
LOG = JOB / 'stage_logs' / run
LOG.mkdir(parents=True, exist_ok=True)
env = dict(os.environ)
env['LAC_RUN'] = run
env['PYTHONIOENCODING'] = 'utf-8'


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def record(**kw):
    kw['time_utc'] = now()
    with open(LOG / 'run_steps.jsonl', 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(kw) + '\n')
    print(json.dumps(kw), flush=True)


def free_gb():
    return shutil.disk_usage(M.DRIVE).free / 1e9


def prune(tag):
    """Delete solver output .txt files over 500 MB of stage <tag> (S0 or FINAL) when free disk is below 80 GB."""
    fg = free_gb()
    removed = []
    if fg < 80:
        for c, d in MODEL.items():
            ex = ROOT / d / 'Executables'
            if not ex.exists():
                continue
            for sub in ex.glob(f'*_{tag}_0'):
                for f in sub.glob('*.txt'):
                    if f.stat().st_size > 500e6 and f.name.endswith('_output.txt'):
                        removed.append((str(f.relative_to(ROOT)), f.stat().st_size))
                        f.unlink()
    record(step=f'prune_{tag}', free_gb_before=round(fg, 1), removed=len(removed),
           removed_gb=round(sum(s for _, s in removed) / 1e9, 2), free_gb_after=round(free_gb(), 1))


def step(name, cmd, cwd=None, logname=None):
    global start_from
    if start_from and name != start_from:
        record(step=name, skipped=True)
        return 0
    start_from = None
    t0 = time.time()
    lf = LOG / (logname or f'{name}.log')
    with open(lf, 'w', encoding='utf-8', newline='\n') as fh:
        r = subprocess.run(cmd, cwd=str(cwd or ROOT), stdout=fh, stderr=subprocess.STDOUT, env=env)
    record(step=name, exit=r.returncode, seconds=round(time.time() - t0, 1), free_gb=round(free_gb(), 1))
    return r.returncode


st = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, capture_output=True, text=True)
record(step='start', tracked_changes=len(st.stdout.splitlines()), free_gb=round(free_gb(), 1))
t_all = time.time()
A2B1 = 'phaseC_run_c.py' if '--phase-c' in sys.argv else 'phaseC_run.py'
for c in COUNTRIES:
    step(f'a2b1_{c}', [sys.executable, '-I', str(S / A2B1), c])
if '--a2b1-only' in sys.argv:
    record(step='end', seconds_total=round(time.time() - t_all, 1))
    sys.exit(0)
step('stage0', [sys.executable, '-I', str(S / 'stage_runner.py'), '0', '--from', '1'], logname='stage0_runner.log')
# stage_runner runs all 7 Stage 0 steps; headers are read after, then outputs pruned
step('solve_headers_S0', [sys.executable, '-I', str(S / 'solve_headers.py'), 'S0'])
prune('S0')
for s in ['1', '2', '3']:
    step(f'stage{s}', [sys.executable, '-I', str(S / 'stage_runner.py'), s], logname=f'stage{s}_runner.log')
step('solve_headers_FINAL', [sys.executable, '-I', str(S / 'solve_headers.py'), 'FINAL'])
prune('FINAL')
step('test_ao_cost_repair_manager', [PY, '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_ao_cost_repair_manager.py', '-v'])
step('test_ao_safe_save', [PY, 'test_ao_safe_save.py'])
record(step='end', seconds_total=round(time.time() - t_all, 1))
