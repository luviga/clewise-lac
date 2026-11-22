"""Line-targeted rewrites of the draft A2 and B1 scripts, driven by the flagged sites of the baseline scan.

For every flagged site (file, line, token) that a rule covers, the rule's regex is applied to that line of the
draft (line numbers of the untouched file: run before any edit that adds or removes lines). The regex must
match exactly as many times as there are flagged sites of that rule on the line; otherwise the line is left
and listed in work/linefix_unmatched.csv for a hand edit.

Usage: py -I b2_linefix.py <rules.py> <file> [...]   rules.py defines RULES = [(name, predicate, regex, repl)]
predicate(site) gets a dict with file, line, kind, token, text.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import re
import runpy
import sys
from collections import defaultdict
from pathlib import Path

ROOT = M.ROOT
JOB = ROOT / '_LAC_HUB' / 'structure_tables_20261122T042525Z'
rules = runpy.run_path(sys.argv[1])['RULES']
files = sys.argv[2:]
sites = [r for r in csv.DictReader(open(JOB / 'work' / 'sites.csv', encoding='utf-8')) if r['file'] in files]
unmatched = []
done = 0
for f in files:
    p = JOB / 'draft' / f
    raw = p.read_bytes().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.split(nl)
    by_line = defaultdict(list)
    for s in sites:
        if s['file'] == f:
            by_line[int(s['line'])].append(s)
    for ln, ss in sorted(by_line.items()):
        for name, pred, rx, repl in rules:
            n = sum(1 for s in ss if pred(s))
            if not n:
                continue
            text = lines[ln - 1]
            k = len(re.findall(rx, text))
            if k != n:
                unmatched.append(dict(file=f, line=ln, rule=name, sites=n, matches=k, text=text.strip()[:200]))
                continue
            lines[ln - 1] = re.sub(rx, repl, text)
            done += n
    p.write_bytes(nl.join(lines).encode('utf-8'))
with open(JOB / 'work' / 'linefix_unmatched.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['file', 'line', 'rule', 'sites', 'matches', 'text'], lineterminator='\n')
    w.writeheader()
    w.writerows(unmatched)
print('sites rewritten', done, 'lines left for hand edits', len(unmatched))
