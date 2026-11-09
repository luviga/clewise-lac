"""Sourcing check for the Costa Rica outputs.
Usage: py -I check_cr.py <country_CR_dir> <downloads_dir>
Checks: every non-ASSUMPTION row of prices, history, constants and calorific names source ids that exist in
sources_CR.csv; every source has an http(s) URL, page_or_table, retrieval_date and a downloaded file that exists;
no field holds a local path; no em dash anywhere."""
import csv, os, sys, re
D, DL = sys.argv[1], sys.argv[2]
src = {r['id']: r for r in csv.DictReader(open(os.path.join(D, 'sources_CR.csv'), encoding='utf-8'))}
bad = []
for sid, r in src.items():
    if not r['url'].startswith(('http://', 'https://')): bad.append(('url', sid))
    if not r['page_or_table'] or not r['retrieval_date']: bad.append(('page/date', sid))
    for f in r['downloaded_file'].split(';'):
        if not os.path.exists(os.path.join(DL, f)): bad.append(('file', sid, f))
n = {}
for name, col in [('prices_CR.csv', 'source_id'), ('history_CR.csv', 'source_id'), ('constants_CR.csv', 'source_id'), ('calorific_CR.csv', 'source_id')]:
    rows = list(csv.DictReader(open(os.path.join(D, name), encoding='utf-8')))
    ok = 0
    for r in rows:
        if r.get('evidence_class') == 'ASSUMPTION candidate':
            continue
        ids = [x for x in r[col].split(';') if x]
        if not ids or any(i not in src for i in ids):
            bad.append((name, 'missing source', r.get('fuel', r.get('name', r.get('balance'))), r[col]))
        else:
            ok += 1
        for f in r.get('downloaded_file', '').split(';'):
            if f and not os.path.exists(os.path.join(DL, f)): bad.append((name, 'file', f))
    n[name] = (len(rows), ok)
for fn in os.listdir(D):
    if fn.endswith(('.csv', '.md')):
        t = open(os.path.join(D, fn), encoding='utf-8').read()
        if chr(0x2014) in t: bad.append(('em dash', fn))
        if re.search(r'[A-Za-z]:\\|/c/|Users\\|Users/', t): bad.append(('path', fn))
print('rows (total, sourced):', n)
print('sources:', len(src))
print('failures:', len(bad))
for b in bad: print(b)
