"""Merge image reads of scanned resolutions into the weekly PPI series and compute 2024 means.
Usage: py -I dr_merge_weekly.py <weekly_liquids_2024.csv> <dr_resolution_image_reads.csv> <out_final_csv>
Rules: where an image read exists for a week and product it confirms or fills the value.
A mismatch between an image read and an aviso or OCR-confirmed value is printed and the image value is not used.
"""
import sys, csv
from collections import defaultdict

w = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
img = {r['week_start']: r for r in csv.DictReader(open(sys.argv[2], encoding='utf-8'))}
for r in w:
    i = img.get(r['week_start'])
    if not i or r['product'] not in i:
        continue
    v = float(i[r['product']])
    if r['ppi'] in ('', None):
        r['ppi'] = v
        r['source'] = 'resolution_image_read'
        r['check'] = 'filled from image of resolution %s page %s' % (i['resolution_number'], i['page'])
    else:
        old = float(r['ppi'])
        if abs(old - v) > 0.011:
            print('MISMATCH', r['week_start'], r['product'], old, v, r['source'])
            if r['source'] == 'ocr_matched':
                r['ppi'] = v
                r['source'] = 'resolution_image_read'
                r['check'] = 'OCR pattern match %.2f rejected; image of resolution %s page %s reads %.2f' % (old, i['resolution_number'], i['page'], v)
        elif r['source'] == 'ocr_matched':
            r['source'] = 'resolution_image_read'
            r['check'] = 'image read %.2f agrees with OCR pattern match' % v
        else:
            if r['source'] == 'xlsx_derived_unconfirmed':
                r['source'] = 'xlsx_derived_image_confirmed'
            r['check'] = (r['check'] + '; ' if r['check'] else '') + 'image read %.2f agrees' % v
with open(sys.argv[3], 'w', newline='', encoding='utf-8') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(w[0].keys()))
    wr.writeheader()
    wr.writerows(w)
agg = defaultdict(list)
for r in w:
    if r['ppi'] not in ('', None):
        agg[r['product']].append((r['week_start'], float(r['ppi']), r['source'], float(r['dist']) if r['dist'] else None))
for k, v in agg.items():
    srcs = defaultdict(int)
    for x in v:
        srcs[x[2]] += 1
    dists = sorted({x[3] for x in v if x[3] is not None})
    print(k, 'weeks', len(v), 'mean PPI %.4f' % (sum(x[1] for x in v) / len(v)), 'min %.2f max %.2f' % (min(x[1] for x in v), max(x[1] for x in v)), dict(srcs), 'dist margins', dists)
    missing = sorted(set(r['week_start'] for r in w) - set(x[0] for x in v))
    print('   missing weeks', missing)
