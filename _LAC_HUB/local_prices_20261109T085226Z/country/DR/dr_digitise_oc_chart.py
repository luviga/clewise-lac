"""Digitise the vector line charts in the OC-SENI Memoria Anual 2024 (Figures 44 to 46: monthly average fuel
costs declared by generating agents). The charts are vector drawings: each series is one polyline whose vertices
are the monthly points. The y axis is calibrated from the numeric tick labels on the same page (centre of label
text = gridline value), using a least-squares line through all tick labels.

Usage: py -I dr_digitise_oc_chart.py <memoria_pdf> <page_index_0_based> <out_csv>
Output: series_index, point_index, x, y, value (axis units), plus a guess of year-month assuming the last point is
December 2024 and points are consecutive months (checked against the year tick labels on the x axis).
"""
import sys, csv, re
import pdfplumber

pdf = pdfplumber.open(sys.argv[1])
p = pdf.pages[int(sys.argv[2])]
words = p.extract_words()
ticks = []
for w in words:
    t = w['text'].replace(',', '')
    if re.fullmatch(r'\d+(\.\d+)?', t) and w['x0'] < 125 and 150 < w['top'] < 520:
        ticks.append((float(t), (w['top'] + w['bottom']) / 2))
n = len(ticks)
mx = sum(v for v, _ in ticks) / n
my = sum(y for _, y in ticks) / n
b = sum((v - mx) * (y - my) for v, y in ticks) / sum((v - mx) ** 2 for v, _ in ticks)
a = my - b * mx
resid = max(abs(a + b * v - y) for v, y in ticks)
print('ticks', n, 'y = %.4f + %.6f * value' % (a, b), 'max tick residual %.3f pt' % resid)
series = [c for c in p.curves if len(c['pts']) > 50]
rows = []
for si, c in enumerate(series):
    pts = c['pts']
    print('series', si, 'points', len(pts), 'x from %.1f to %.1f' % (pts[0][0], pts[-1][0]))
    N = len(pts)
    for i, (x, y) in enumerate(pts):
        k = N - 1 - i  # months before Dec 2024
        yr = 2024 - (k // 12) - (1 if (12 - k % 12) <= 0 else 0)
        mo = 12 - (k % 12)
        rows.append(dict(series=si, point=i, x=round(x, 3), y=round(y, 3), value=round((y - a) / b, 2), assumed_year=yr, assumed_month=mo))
year_ticks = [(w['x0'], w['text']) for w in words if re.fullmatch(r'\d{4}', w['text']) and w['top'] > 460]
print('x-axis year labels (x0, text as extracted, may be reversed):', year_ticks[-4:])
with open(sys.argv[3], 'w', newline='', encoding='utf-8') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
for si in range(len(series)):
    last = [r for r in rows if r['series'] == si][-12:]
    print('series', si, 'last 12 points', [r['value'] for r in last], 'mean %.2f' % (sum(r['value'] for r in last) / 12))
