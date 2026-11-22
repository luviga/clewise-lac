"""C1: rename_plan.csv from the scope scan (c_scan.py scope), one action per row.
Usage: py -I c1_plan.py <scope scan csv> <rename_plan.csv>"""
import csv
import sys

RENAME = {'NDCNEW': 'NDC', 'LTSNEW': 'LTS'}
RETIRE = {'NDC', 'LTS', 'NDCcond', 'NDCincond', 'NDP', 'NDPAMB', 'NDCINC'}
KEEP = {'BAU', 'LTSOPT', 'Default'}
# compiled files of a scenario in use whose Scenario label holds an older name (the feed of F4)
FEEDS = {('DominicanRepublic/', 'NDCcond'), ('Guatemala/', 'NDP'), ('Honduras/', 'NDP'), ('Jamaica/', 'LTS')}
IN_USE_DIRS = ('/BAU/', '/NDCNEW/', '/LTSNEW/')

rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
out = []
for r in rows:
    n, f = r['name'], r['file']
    if n in RENAME:
        act, note = 'rename', f'{n} becomes {RENAME[n]}'
    elif n in RETIRE:
        feed = any(f.startswith(c) and n == old for c, old in FEEDS) and any(d in f for d in IN_USE_DIRS)
        if feed:
            act, note = 'retire', 'label of data that feeds a scenario in use: label replaced by the scenario in use, values kept'
        else:
            act, note = 'retire', 'older scenario: folder, rows, sheet cells or code branch removed'
    elif n in KEEP:
        act, note = 'keep', 'scenario in use' if n == 'BAU' else (
            'Costa Rica B1 optimal LTS run' if n == 'LTSOPT' else 'generic word Default')
    else:
        act, note = 'check', 'not one of the 12 names'
    out.append([n, r['place_kind'], f, r['place'], r['count'], act, note])
with open(sys.argv[2], 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['name', 'place_kind', 'file', 'place', 'count', 'action', 'note'])
    w.writerows(out)
cnt = {}
for o in out:
    cnt[(o[0], o[5])] = cnt.get((o[0], o[5]), 0) + int(o[4] or 0)
for k in sorted(cnt):
    print(k, cnt[k])
