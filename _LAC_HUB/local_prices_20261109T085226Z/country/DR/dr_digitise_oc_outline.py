"""Digitise outline-drawn line series (stroke converted to a filled outline) in OC-SENI Memoria 2024 Figure 44
(fuel oil, RD$/gal). Each month is a bin on the x axis; the series value in the bin is the mean y of the outline
vertices in that bin (mean of upper and lower edge = centre line), converted with a least-squares fit of the
y tick labels.

Usage: py -I dr_digitise_oc_outline.py <memoria_pdf> <page_index> <first_x_month_index_offset_ignored> <out_csv>
The x grid: x_end = max x of the outline minus half the stroke width (estimated as half the median vertical
thickness is not used for x); months are spaced by (x_max - x_min) / (n_months - 1) with n_months from Jul 2001
(first point) to Dec 2024, i.e. 282 months, the same span as Figure 45 digitised by dr_digitise_oc_chart.py.
"""
import sys, csv, re
import pdfplumber

pdf = pdfplumber.open(sys.argv[1])
p = pdf.pages[int(sys.argv[2])]
words = p.extract_words()
ticks = []
for w in words:
    t = w['text'].replace(',', '')
    if re.fullmatch(r'\d+(\.\d+)?', t) and w['x0'] < 125 and 300 < w['top'] < 580:
        ticks.append((float(t), (w['top'] + w['bottom']) / 2))
n = len(ticks)
mx = sum(v for v, _ in ticks) / n
my = sum(y for _, y in ticks) / n
b = sum((v - mx) * (y - my) for v, y in ticks) / sum((v - mx) ** 2 for v, _ in ticks)
a = my - b * mx
print('ticks', n, 'y = %.4f + %.6f * value' % (a, b))
rows = []
for si, c in enumerate([c for c in p.curves if len(c['pts']) > 50]):
    pts = c['pts']
    xs = [q[0] for q in pts]
    x0, x1 = min(xs), max(xs)
    for nm in (282, 283, 284):
        pass
    nmonths = 282
    step = (x1 - x0) / (nmonths - 1)
    vals = []
    for k in range(nmonths):
        xc = x0 + k * step
        ys = [q[1] for q in pts if abs(q[0] - xc) <= step / 2]
        v = round((sum(ys) / len(ys) - a) / b, 2) if ys else None
        vals.append(v)
        mback = nmonths - 1 - k
        yr = 2024 - mback // 12
        mo = 12 - mback % 12
        rows.append(dict(series=si, month_index=k, year=yr, month=mo, x_centre=round(xc, 3), n_vertices=len(ys), value=v))
    last = vals[-12:]
    ok = [v for v in last if v is not None]
    print('series', si, 'vertices', len(pts), 'x %.1f-%.1f step %.4f' % (x0, x1, step), '2024:', last, 'mean %.2f' % (sum(ok) / len(ok)))
with open(sys.argv[4], 'w', newline='', encoding='utf-8') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
