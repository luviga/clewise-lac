"""Steps 0.3 and 9.3: compile and solve the sector models and JAM_TRANSPORT with their own scripts (A2 compiler, then
the B1 runner, then the B2 results creator where the model has one), and record the solve status and objective of
every scenario. The tracked side files the A2 compilers rewrite (A1_Outputs, A2_Extra_Inputs, A2_Structure_Lists)
are restored from the git index afterwards. Writes <out>.csv (model, scenario, status, objective, seconds).
Usage: python -I sector_run.py <root> <out.csv> [model ...]
       python -I sector_run.py --from-logs <logdir> <out.csv>   (statuses from the logs of an earlier run)"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import os
import re
import subprocess
import sys
import time
from pathlib import Path

if sys.argv[1] != '--from-logs':
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
else:
    root, out = M.ROOT, Path(sys.argv[3])
MODELS = {'CostaRica/CR_AFOLU/t1_confection': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel.py', 'B2_Results_Creator_f0.py'),
          'CostaRica/CR_WASTE': ('A2_Compiler_Waste.py', 'B1_Base_Scenarios_Adj_Parallel_Waste.py', 'B2_Results_Creator_f0_Waste.py'),
          'DominicanRepublic/RD_AFOLU': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel.py', 'B2_Results_Creator_f0.py'),
          'DominicanRepublic/RD_WASTE': ('A2_Compiler_Waste.py', 'B1_Base_Scenarios_Adj_Parallel_Waste.py', 'B2_Results_Creator_f0_Waste.py'),
          'Ecuador/ECU_WASTE': ('A2_Compiler_Waste.py', 'B1_Base_Scenarios_Adj_Parallel_Waste.py', 'B2_Results_Creator_f0_Waste.py'),
          'Ecuador/ECU_USCUSS': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel_SIMPLE.py', 'B2_Results_Creator_f0.py'),
          'Guatemala/GUA_WASTE': ('A2_Compiler_Waste.py', 'B1_Base_Scenarios_Adj_Parallel_Waste.py', 'B2_Results_Creator_f0_Waste.py'),
          'Honduras/HON_AFOLU/HON_AFOLU': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel.py', 'B2_Results_Creator_f0.py'),
          'Honduras/HON_WASTE': ('A2_Compiler_Waste.py', 'B1_Base_Scenarios_Adj_Parallel_Waste.py', 'B2_Results_Creator_f0_Waste.py'),
          'Jamaica/JAM_AFOLU': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel.py', 'B2_Results_Creator_f0.py'),
          'Jamaica/JAM_WASTE': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel.py', 'B2_Results_Creator_f0.py'),
          'Jamaica/JAM_TRANSPORT': ('A2_Compiler.py', 'B1_Base_Scenarios_Adj_Parallel.py', 'B2_Results_Creator_f0.py')}
only = sys.argv[3:]
env = dict(os.environ)
env['PATH'] = str(Path(M.GLPSOL).parent) + os.pathsep + env['PATH']
env['PYTHONIOENCODING'] = 'utf-8'
logdir = out.with_suffix('')
logdir.mkdir(parents=True, exist_ok=True)


def from_log(m, lf, secs, steps):
    """Status and objective of each solve from the solver messages of the B1 log (runners that delete outputs)."""
    out, st, obj = [], '', ''
    if not lf.exists():
        return [[m, '', 'no log', '', secs, steps]]
    for line in open(lf, encoding='utf-8', errors='replace'):
        if 'SOLUTION FOUND' in line or 'NO PRIMAL FEASIBLE' in line or 'NO DUAL FEASIBLE' in line or 'UNDEFINED' in line:
            st = 'OPTIMAL' if 'OPTIMAL' in line else line.strip()
        mm = re.search(r'obj =\s+([-0-9.eE+]+)', line)
        if mm:
            obj = mm.group(1)
        mw = re.search(r"Writing basic solution to '(.*)'", line)
        if mw:
            scen = re.split(r'[\\/]', mw.group(1))[-1].replace('_0_output.txt', '')
            out.append([m, scen, st or 'unknown', obj, secs, steps])
            st, obj = '', ''
    return out or [[m, '', 'no solver output', '', secs, steps]]


if sys.argv[1] == '--from-logs':
    ld, out = Path(sys.argv[2]), Path(sys.argv[3])
    rr = []
    for f in sorted(ld.glob('*_b1.log')):
        rr += from_log(f.stem[:-3].replace('_', '/', 1), f, '', '')
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['model', 'scenario', 'status', 'objective', 'seconds_model', 'steps'])
        w.writerows(rr)
    sys.exit(0)
rows = []
for m, (a2, b1, b2) in MODELS.items():
    if only and m not in only:
        continue
    d = root / m
    (d / 'Executables').mkdir(exist_ok=True)   # gitignored folder the B1 runners expect
    t0 = time.time()
    steps = []
    for name, script in (('a2', a2), ('b1', b1), ('b2', b2)):
        if not (d / script).exists():
            steps.append(f'{name}: no script')
            continue
        lf = logdir / (m.replace('/', '_') + f'_{name}.log')
        with open(lf, 'w', encoding='utf-8', newline='\n') as fh:
            r = subprocess.run([M.ANACONDA, script], cwd=d, stdout=fh, stderr=subprocess.STDOUT, env=env, timeout=5400)
        steps.append(f'{name}: exit {r.returncode}')
        if name == 'a2':
            sides = [s for s in ('A1_Outputs', 'A2_Extra_Inputs', 'A2_Structure_Lists.xlsx') if (d / s).exists()]
            subprocess.run(['git', 'checkout', '--', *sides], cwd=d, capture_output=True)
        if r.returncode != 0 and name != 'b2':
            break
    for o in sorted((d / 'Executables').glob('*_0/*_output.txt')) if (d / 'Executables').exists() else []:
        st, obj = '', ''
        with open(o, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if line.startswith('Status:'):
                    st = line.split(':', 1)[1].strip()
                if line.startswith('Objective:'):
                    mm = re.search(r'=\s*([-0-9.eE+]+)', line)
                    obj = mm.group(1) if mm else ''
                if st and obj:
                    break
        rows.append([m, o.parent.name.replace('_0', ''), st, obj, round(time.time() - t0), '; '.join(steps)])
    if not rows or rows[-1][0] != m:
        rows += from_log(m, logdir / (m.replace('/', '_') + '_b1.log'), round(time.time() - t0), '; '.join(steps))
    print(m, '; '.join(steps), flush=True)
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['model', 'scenario', 'status', 'objective', 'seconds_model', 'steps'])
    w.writerows(rows)
print(len(rows), 'rows ->', out)
