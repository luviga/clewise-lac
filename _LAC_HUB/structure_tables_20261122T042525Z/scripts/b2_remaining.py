"""List flagged sites of the given files that are neither accepted (b2_accept_rules) nor already rewritten
(the draft line no longer holds the literal). Line numbers are those of the untouched file; the draft text is
found by searching for the untouched line text.  Usage: py -I b2_remaining.py <file> [...]"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b2_accept_rules import reason  # noqa: E402

JOB = M.JOB_S
sys.stdout.reconfigure(encoding='utf-8')
files = sys.argv[1:]
n = 0
for s in csv.DictReader(open(JOB + '/work/sites.csv', encoding='utf-8')):
    if s['file'] not in files or reason(s):
        continue
    draft = open(os.path.join(JOB, 'draft', s['file']), encoding='utf-8').read()
    if s['text'] not in draft:
        continue  # line was rewritten
    n += 1
    print(f"{s['file'].split('/')[0][:3]} {s['line']} {s['kind'][:5]} {s['token']} | {s['text'][:150]}")
print('remaining', n)
