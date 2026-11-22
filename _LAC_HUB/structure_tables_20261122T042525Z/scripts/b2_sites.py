"""List every flagged literal (stage0_3_results_depend = yes) of the 26 code files with its source line, column and
the stripped line text, so that identical code sites in the six country copies can be decided once.

Writes work/sites.csv. Run on the untouched code (b51f24b). Usage: py -I b2_sites.py
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast
import csv
import os
import re
import sys

ROOT = M.ROOT_S
JOB = ROOT + '/_LAC_HUB/structure_tables_20261122T042525Z'
SCAN = JOB + '/scan_before/script_constants.csv'
OUT = JOB + '/work'
os.makedirs(OUT, exist_ok=True)

rows = [r for r in csv.DictReader(open(SCAN, encoding='utf-8')) if r['stage0_3_results_depend'] == 'yes'
        and not r['file'].endswith('OSeMOSYS_Model.txt')]


def norm_val(r):
    v = r['value']
    m = re.match(r"^(.*) \(in '", v)
    return m.group(1) if m else v


out = []
cache = {}
for r in rows:
    f = r['file']
    if f not in cache:
        cache[f] = open(os.path.join(ROOT, f), encoding='utf-8', errors='replace').read().splitlines()
    ln = int(r['line'])
    text = cache[f][ln - 1]
    out.append(dict(file=f, line=ln, kind=r['kind'], token=norm_val(r), value=r['value'], ctx=r['name'],
                    text=text.strip()[:200]))
with open(OUT + '/sites.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(out)
print(len(out))
b1 = [o for o in out if '/B1_' in o['file']]
a2 = [o for o in out if '/A2_' in o['file']]
print('B1 sites', len(b1), 'unique (text, token)', len({(o['text'], o['token']) for o in b1}))
print('A2 sites', len(a2), 'unique (text, token)', len({(o['text'], o['token']) for o in a2}))
