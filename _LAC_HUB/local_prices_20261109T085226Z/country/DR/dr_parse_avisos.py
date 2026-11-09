"""Parse MICM weekly fuel price notices (avisos, digital PDFs) into a long CSV.
Usage: py -I dr_parse_avisos.py <aviso_dir> <out_csv>
Columns per product row: PPI, Ley 112-00, Ley 495-06 ad valorem, distributor margin,
retailer margin, transport commission, official price, adjustment, price paid by public.
Also extracts the exchange rate applied and the LPG gallons per tonne factor."""
import sys, os, re, csv, pdfplumber

NUM = re.compile(r'^\(?-?[0-9,]+\.[0-9]+\)?$')
def val(t):
    neg = t.startswith('(')
    v = float(t.strip('()').replace(',', ''))
    return -v if neg else v

def parse(path):
    pdf = pdfplumber.open(path)
    rows, meta = [], {}
    text = '\n'.join((p.extract_text() or '') for p in pdf.pages)
    m = re.search(r'Tasa de Cambio[^\n]*?RD\$\s*([0-9.]+)', text)
    meta['fx'] = m.group(1) if m else ''
    m = re.search(r'Metric\.\)\s*=\s*([0-9.]+)', text)
    meta['lpg_gal_per_t'] = m.group(1) if m else ''
    for pno, page in enumerate(pdf.pages):
        words = page.extract_words()
        lines = {}
        for w in words:
            key = None
            for k in lines:
                if abs(k - w['top']) < 2.0:
                    key = k; break
            if key is None:
                key = w['top']; lines[key] = []
            lines[key].append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w['x0'])
            nums = [w for w in ws if NUM.match(w['text']) and w['x0'] > 195]
            label = ' '.join(w['text'] for w in ws if w['x0'] < 200)
            if len(nums) >= 9 and label:
                rows.append((pno + 1, label, [val(w['text']) for w in nums]))
    return rows, meta

out = []
for f in sorted(os.listdir(sys.argv[1])):
    if not f.lower().endswith('.pdf'):
        continue
    rows, meta = parse(os.path.join(sys.argv[1], f))
    for pno, label, v in rows:
        rec = dict(file=f, page=pno, product=label, fx=meta['fx'], lpg_gal_per_t=meta['lpg_gal_per_t'])
        if 'GLP' in label or 'Licuado' in label:
            names = ['ppi', 'ley112', 'ley495', 'dist', 'det', 'transp', 'oficial', 'ajuste', 'bonogas', 'final']
        else:
            names = ['ppi', 'ley112', 'ley495', 'dist', 'det', 'transp', 'oficial', 'ajuste', 'final', 'variacion']
        for n, x in zip(names, v):
            rec[n] = x
        s = sum(rec.get(n, 0) for n in ['ppi', 'ley112', 'ley495', 'dist', 'det', 'transp'])
        rec['check_sum_minus_oficial'] = round(s - rec.get('oficial', 0), 2)
        out.append(rec)
cols = ['file', 'page', 'product', 'ppi', 'ley112', 'ley495', 'dist', 'det', 'transp', 'oficial', 'ajuste', 'bonogas', 'final', 'variacion', 'fx', 'lpg_gal_per_t', 'check_sum_minus_oficial']
with open(sys.argv[2], 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in out:
        w.writerow({c: r.get(c, '') for c in cols})
print(len(out), 'rows')
