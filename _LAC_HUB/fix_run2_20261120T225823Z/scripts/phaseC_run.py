"""Phase C1: A2 then B1 for one country, with the canonical commands (pipeline_commands.csv of the cost write run).
Usage: py -I scripts/phaseC_run.py <Country> [--tag N]
Logs in logs/phaseC/<Country>[_N]/{a2,b1}; prints the solve statuses of the three base scenarios."""
import json, subprocess, sys, time
from pathlib import Path

JOB = Path('C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z')
S = JOB / 'scripts'
SOURCE = {'CostaRica': 'BAU', 'DominicanRepublic': 'NDCcond', 'Ecuador': 'BAU', 'Guatemala': 'NDP', 'Honduras': 'NDP',
          'Jamaica': 'LTSNEW'}
c = sys.argv[1]
tag = ('_' + sys.argv[sys.argv.index('--tag') + 1]) if '--tag' in sys.argv else ''
skip_a2 = '--skip-a2' in sys.argv
L = JOB / 'logs' / 'phaseC' / (c + tag)
L.mkdir(parents=True, exist_ok=True)
t0 = time.time()
if not skip_a2:
    cmd = [sys.executable, '-I', str(S / 'a2_driver.py'), c, '--logdir', str(L / 'a2'), '--source', SOURCE[c]]
    if c == 'Guatemala':
        cmd.append('--shim')
    r = subprocess.run(cmd, capture_output=True, text=True)
    (L / 'a2_stdout.txt').write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    print(c, 'A2 exit', r.returncode, round(time.time() - t0), 's')
    if r.returncode != 0:
        sys.exit('A2 failed')
cmd = [sys.executable, '-I', str(S / 'b1_driver.py'), c, '--logdir', str(L / 'b1')]
if c == 'CostaRica':
    cmd += ['--temp-a2', 'LTSOPT=LTSNEW']
t1 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True)
(L / 'b1_stdout.txt').write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
print(c, 'B1 exit', r.returncode, round(time.time() - t1), 's')
sl = L / 'b1' / 'solve_log.jsonl'
if sl.exists():
    for line in sl.read_text(encoding='utf-8').splitlines():
        d = json.loads(line)
        print('  ', d.get('data', '')[-40:], d.get('status'), d.get('objective'))
