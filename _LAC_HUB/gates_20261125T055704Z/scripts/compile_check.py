"""Step 2.1: compile every model with its own A2 compiler and B1 runner, with the glpsol wrapper in check mode first
on PATH, so every Executables/<scenario>_0/<scenario>_0.txt is written and translated (glpsol --check) and nothing is
solved. Models come from config/gates/models.csv.

  energy models: phaseC_run_c.py <Country> (a2_driver_c.py, then b1_driver.py) as LAC_ALIGN ran them;
  other models:  the model's A2 compiler, then its B1 runner, from the model folder. The tracked side files the A2
                 compilers rewrite (A1_Outputs, A2_Extra_Inputs, A2_Structure_Lists.xlsx) are listed, then restored
                 from the index, as LAC_ALIGN's sector_run.py did. A runner that fails on a removed pandas method
                 (DataFrame.append) is run again through the append shim of the cost_write_run job.

Per model and scenario: data file written (yes or no, size, time), translation status from check_log.jsonl.
Usage: py -I compile_check.py <energy|other|all> [model ...]
Writes stage_logs/compile/<model>_{a2,b1}.log and compile_<group>.csv in the job folder."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT, JOB = M.ROOT, M.JOB
S = JOB / 'scripts'
LOG = JOB / 'stage_logs' / 'compile'
LOG.mkdir(parents=True, exist_ok=True)
CHECKLOG = JOB / 'check_log.jsonl'
SHIM = ROOT / '_LAC_HUB' / 'cost_write_run_20261111T071733Z' / 'scripts' / 'run_with_append_shim.py'
WRAP = S / 'glpsol_wrap'
WRAP.mkdir(exist_ok=True)
(WRAP / 'glpsol.bat').write_text('@echo off\r\n"' + M.ANACONDA + '" -I "' + str(S / 'glpsol_wrap.py')
                                 + '" %*\r\nexit /b %ERRORLEVEL%\r\n', encoding='utf-8')
SIDES = ('A1_Outputs', 'A2_Extra_Inputs', 'A2_Structure_Lists.xlsx')
COUNTRY = {'CR_ENERGY': 'CostaRica', 'RD_ENERGY': 'DominicanRepublic', 'ECU_Energy': 'Ecuador',
           'GUA_ENERGY': 'Guatemala', 'HON_ENERGY': 'Honduras', 'JAM_ENERGY': 'Jamaica'}

env = dict(os.environ)
env['PATH'] = str(WRAP) + os.pathsep + env.get('PATH', '')
env['GLPSOL_CHECK'] = '1'
env['GLPSOL_CHECK_LOG'] = str(CHECKLOG)
env['PYTHONIOENCODING'] = 'utf-8'
env['LAC_RUN'] = 'compile'
if M.TMP:
    env['TMP'] = env['TEMP'] = str(M.GATES_TMP)

group = sys.argv[1]
only = sys.argv[2:]
models = list(csv.DictReader(open(ROOT / 'config' / 'gates' / 'models.csv', encoding='utf-8')))


def run(cmd, cwd, logname, timeout=5400):
    t0 = time.time()
    with open(LOG / logname, 'w', encoding='utf-8', newline='\n') as fh:
        try:
            r = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, env=env, timeout=timeout)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = 'timeout'
    return rc, round(time.time() - t0, 1)


def needs_shim(logname):
    t = (LOG / logname).read_text(encoding='utf-8', errors='replace')
    return "has no attribute 'append'" in t or "has no attribute 'iteritems'" in t


rows = []
for m in models:
    if only and m['model'] not in only:
        continue
    if group == 'energy' and m['kind'] != 'energy' or group == 'other' and m['kind'] == 'energy':
        continue
    d = ROOT / m['path']
    (d / 'Executables').mkdir(exist_ok=True)
    t_start = time.time()
    steps = []
    if m['kind'] == 'energy':
        c = COUNTRY[m['model']]
        rc, sec = run([sys.executable, '-I', str(S / 'phaseC_run_c.py'), c], ROOT, f"{m['model']}_a2b1.log", 10800)
        steps.append(f'a2+b1 exit {rc} ({sec}s)')
    else:
        a2log, b1log = f"{m['model']}_a2.log", f"{m['model']}_b1.log"
        rc, sec = run([M.ANACONDA, m['a2_compiler']], d, a2log)
        if rc != 0 and needs_shim(a2log):
            rc, sec = run([M.ANACONDA, str(SHIM), m['a2_compiler']], d, a2log)
            steps.append('a2 via append shim')
        steps.append(f'a2 exit {rc} ({sec}s)')
        st = subprocess.run(['git', 'status', '--porcelain', '--', m['path']], cwd=ROOT, capture_output=True, text=True)
        (LOG / f"{m['model']}_a2_changed.txt").write_text(st.stdout, encoding='utf-8')
        sides = [s for s in SIDES if (d / s).exists()]
        subprocess.run(['git', 'checkout', '--', *sides], cwd=d, capture_output=True)
        subprocess.run(['git', 'clean', '-f', '-q', '--', *sides], cwd=d, capture_output=True)
        if rc == 0:
            rc, sec = run([M.ANACONDA, m['b1_runner']], d, b1log)
            if rc != 0 and needs_shim(b1log):
                rc, sec = run([M.ANACONDA, str(SHIM), m['b1_runner']], d, b1log)
                steps.append('b1 via append shim')
            steps.append(f'b1 exit {rc} ({sec}s)')
    total = round(time.time() - t_start, 1)
    checks = {}
    if CHECKLOG.exists():
        for ln in CHECKLOG.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                checks[os.path.normcase(os.path.abspath(r['data']))] = r
    for scen in m['scenarios'].split('|'):
        dat = d / 'Executables' / f'{scen}_0' / f'{scen}_0.txt'
        ck = checks.get(os.path.normcase(str(dat.resolve())), {})
        rows.append(dict(model=m['model'], scenario=scen, data_file_written='yes' if dat.exists() else 'no',
                         data_file_mb=round(dat.stat().st_size / 1e6, 2) if dat.exists() else '',
                         written_after_start='yes' if dat.exists() and dat.stat().st_mtime >= t_start else 'no',
                         translation=ck.get('status', 'not translated'), rows=ck.get('rows', ''),
                         columns=ck.get('columns', ''), check_seconds=ck.get('seconds', ''),
                         model_seconds=total, steps='; '.join(steps)))
        print(json.dumps(rows[-1]), flush=True)
out = JOB / f'compile_{group}{"_" + "_".join(only) if only else ""}.csv'
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
