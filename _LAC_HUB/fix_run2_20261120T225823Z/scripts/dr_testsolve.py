"""Phase D test solves for the Dominican Republic Stage 3 infeasibility (D7a search). Works on copies in
C:/clw_base_4ba69d6/_dr_test/ (outside the clone). Scales TotalTechnologyAnnualActivityLowerLimit of the listed technologies
in the listed years by a factor (0.98 / 0.999 puts a D7a band back) and solves with glpsol.
Usage: py -I scripts/dr_testsolve.py <scen> <label> <factor> <ymin> <ymax> TECH [TECH ...]
Prints the glpsol status. Log: logs/dr_testsolve.jsonl"""
import json, os, re, subprocess, sys, time

ROOT = 'C:/clw_fix/DominicanRepublic/RD_ENERGY'
JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
T = 'C:/clw_base_4ba69d6/_dr_test'
scen, label, fac, y0, y1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
techs = set(sys.argv[6:])
PARAM = 'TotalTechnologyAnnualActivityUpperLimit' if label.startswith('UP_') else ('TotalAnnualMaxCapacity' if label.startswith('MAXC_') else 'TotalTechnologyAnnualActivityLowerLimit')
os.makedirs(T, exist_ok=True)
src = f'{ROOT}/Executables/{scen}_FINAL_0/{scen}_FINAL_0.txt'
lines = open(src, encoding='utf-8').read().split('\n')
out, inblk, years, n = [], False, None, 0
for ln in lines:
    if ln.startswith('param ' + PARAM + ' '):
        inblk = True
        out.append(ln)
        continue
    if inblk:
        if ln.strip() == ';' or ln.startswith('param '):
            inblk = False
        elif ln.strip().endswith(':=') and re.match(r'^\s*\d{4}', ln):
            years = [int(x) for x in ln.replace(':=', '').split()]
        elif years and ln.split() and ln.split()[0] in techs:
            f = ln.split()
            vals = [float(x) for x in f[1:len(years) + 1]]
            vals = [v * fac if y0 <= y <= y1 else v for v, y in zip(vals, years)]
            ln = f[0] + ' ' + ' '.join(repr(v) for v in vals) + ' '
            n += 1
    out.append(ln)
dat = f'{T}/{scen}_{label}.txt'
open(dat, 'w', encoding='utf-8').write('\n'.join(out))
t0 = time.time()
r = subprocess.run(['C:/glpk-4.65/w64/glpsol.exe', '-m', f'{ROOT}/OSeMOSYS_Model.txt', '-d', dat, '-o', f'{T}/{scen}_{label}_out.txt'],
                   capture_output=True, text=True)
status = 'no output'
if os.path.exists(f'{T}/{scen}_{label}_out.txt'):
    for l in open(f'{T}/{scen}_{label}_out.txt', errors='replace').readlines()[:12]:
        if l.startswith('Status:'):
            status = l.split(':', 1)[1].strip()
    os.remove(f'{T}/{scen}_{label}_out.txt')
os.remove(dat)
tail = [l for l in r.stdout.splitlines() if 'PRIMAL' in l or 'INFEAS' in l.upper() or 'error' in l.lower()][-3:]
rec = dict(scen=scen, label=label, factor=fac, years=f'{y0}-{y1}', techs=sorted(techs), rows_changed=n, status=status,
           seconds=round(time.time() - t0), notes=tail)
open(JOB + '/logs/dr_testsolve.jsonl', 'a').write(json.dumps(rec) + '\n')
print(json.dumps(rec))
