"""Gate 1 of Phase B: rows of a scan with stage0_3_results_depend = yes outside the six model files must all be
constants of the mathematics, of a file layout or of presentation, each with its reason (b2_accept_rules).

Usage: py -I b5_gate1.py <scan folder> [--draft]   (--draft: read line texts from the draft copies)
Writes <scan folder>/gate1_rows.csv (every yes row with its reason or 'NOT ACCEPTED') and prints the counts.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b2_accept_rules import reason  # noqa: E402

ROOT = M.ROOT_S
JOB = ROOT + '/_LAC_HUB/structure_tables_20261122T042525Z'
scan = sys.argv[1]
draft = '--draft' in sys.argv
sys.stdout.reconfigure(encoding='utf-8')
cache = {}
out = []
model_rows = 0
for r in csv.DictReader(open(os.path.join(scan, 'script_constants.csv'), encoding='utf-8')):
    if r['stage0_3_results_depend'] != 'yes':
        continue
    if r['file'].endswith('OSeMOSYS_Model.txt'):
        model_rows += 1
        continue
    f = r['file']
    if f not in cache:
        p = os.path.join(JOB, 'draft', f) if draft and os.path.exists(os.path.join(JOB, 'draft', f)) else os.path.join(ROOT, f)
        cache[f] = open(p, encoding='utf-8', errors='replace').read().splitlines()
    m = re.match(r"^(.*) \(in '", r['value'])
    site = dict(file=f, line=r['line'], kind=r['kind'], token=m.group(1) if m else r['value'],
                text=cache[f][int(r['line']) - 1].strip())
    why = reason(site)
    out.append(dict(file=f, line=r['line'], kind=r['kind'], value=r['value'], name=r['name'],
                    reason=why or 'NOT ACCEPTED', text=site['text'][:200]))
with open(os.path.join(scan, 'gate1_rows.csv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]) if out else ['file'], lineterminator='\n')
    w.writeheader()
    w.writerows(out)
bad = [o for o in out if o['reason'] == 'NOT ACCEPTED']
print(f'yes rows outside the model files: {len(out)}; accepted with reason: {len(out) - len(bad)}; '
      f'not accepted: {len(bad)}; model file rows (kept, reported): {model_rows}')
for o in bad:
    print('  NOT ACCEPTED', o['file'], o['line'], o['kind'], o['value'][:60], '|', o['text'][:120])
