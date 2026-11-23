"""Phase C: A2 (a2_driver_c.py) then B1 (b1_driver.py) for one country, scenario names from the catalogue.
Usage: py -I phaseC_run_c.py <Country> [--skip-a2]
Logs in stage_logs/<LAC_RUN>/a2b1/<Country>/{a2,b1}; prints the solve statuses."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import importlib.util

ROOT = M.ROOT
JOB = ROOT / '_LAC_HUB' / 'structure_tables_20261122T042525Z'
S = JOB / 'scripts'
spec = importlib.util.spec_from_file_location('lac_tables', str(ROOT / 'lac_tables.py'))
LT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LT)
c = sys.argv[1]
L = JOB / 'stage_logs' / os.environ.get('LAC_RUN', 'phaseC') / 'a2b1' / c
L.mkdir(parents=True, exist_ok=True)
if '--skip-a2' not in sys.argv:
    t0 = time.time()
    cmd = [sys.executable, '-I', str(S / 'a2_driver_c.py'), c, '--logdir', str(L / 'a2')]
    if c == 'Guatemala':
        cmd.append('--shim')
    r = subprocess.run(cmd, capture_output=True, text=True)
    (L / 'a2_stdout.txt').write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    print(c, 'A2 exit', r.returncode, round(time.time() - t0), 's')
    if r.returncode != 0:
        sys.exit('A2 failed')
cmd = [sys.executable, '-I', str(S / 'b1_driver.py'), c, '--logdir', str(L / 'b1')]
if c == 'CostaRica':
    cmd += ['--temp-a2', LT.scenario('lts_optimal') + '=' + LT.scenario('lts')]
t1 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True)
(L / 'b1_stdout.txt').write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
print(c, 'B1 exit', r.returncode, round(time.time() - t1), 's')
sl = L / 'b1' / 'solve_log.jsonl'
if sl.exists():
    for line in sl.read_text(encoding='utf-8').splitlines():
        d = json.loads(line)
        print('  ', d.get('data', '')[-40:], d.get('status'), d.get('objective'))
