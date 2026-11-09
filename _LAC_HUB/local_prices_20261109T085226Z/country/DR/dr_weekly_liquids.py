"""Build the 2024 weekly MICM liquid-fuel import parity (PPI) series for the Dominican Republic.

Usage: py -I dr_weekly_liquids.py <downloads_DR_dir> <out_csv>

Sources inside <downloads_DR_dir>:
  avisos_parsed.csv     (from dr_parse_avisos.py; 28 digital weekly notices, Jan to Aug 2024)
  micm_hist2024/*Data_Cruda*.xlsx  (MICM quarterly weekly price history, price paid by public)
  micm_res2024/*.pdf    (MICM weekly price resolutions, scanned with OCR text layer)

Method per product and week (weeks starting Saturday 6 Jan 2024 to Saturday 28 Dec 2024):
  1. If a digital aviso exists, take the PPI from it (source 'aviso').
  2. Unfrozen products (gasoil EGP-C, avtur, fuel oil rows): PPI = (P - L112 - dist - det - transp) / (1 + adval),
     P = price in the MICM weekly history xlsx (no adjustment on these rows in any aviso week).
     Accepted only if the derived PPI (+-0.01) appears in the OCR text of that week's resolution
     (source 'xlsx_derived_ocr_confirmed'); else 'xlsx_derived_unconfirmed'.
  3. Frozen products (gasolines, gasoil regular, kerosene, LPG): candidate PPI p from OCR numbers is accepted
     when p + round(adval*p,2) + L112 + dist + det + transp equals an official price in the same OCR text (+-0.02)
     for one of the published margin sets, and exactly one p matches (source 'ocr_matched').
"""
import sys, os, re, csv, glob, datetime as dt
from collections import Counter
import openpyxl, pdfplumber

base, out_csv = sys.argv[1], sys.argv[2]
D = dt.date

MONTHS = {'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12}

# structure: ley112, ad valorem rate, margin sets (dist, det) seen in 2024 avisos, transport, xlsx column, aviso label
PROD = {
    'GSL_PREMIUM': dict(l112=71.85, av=0.16, m=[(15.09, 22.57), (16.59, 25.07)], tr=5.68, col=None, label='Gasolina Premium'),
    'GSL_REGULAR': dict(l112=63.83, av=0.16, m=[(15.09, 22.57), (16.59, 25.07)], tr=5.68, col=None, label='Gasolina Regular'),
    'DSL_REGULAR': dict(l112=28.06, av=0.16, m=[(12.78, 19.25), (14.28, 21.75)], tr=5.68, col=None, label='Gasoil Regular'),
    'DSL_EGPC': dict(l112=28.06, av=0.16, m=[(5.24, 0.0)], tr=5.68, col=5, label='Gasoil Regular EGP-C ( Inter. y No Interconectado)'),
    'AVTUR': dict(l112=6.30, av=0.065, m=[(15.53, 0.0)], tr=5.68, col=10, label='Avtur'),
    'KER': dict(l112=17.99, av=0.16, m=[(9.10, 15.01)], tr=5.68, col=None, label='Kerosene'),
    'FO6': dict(l112=17.99, av=0.16, m=[(1.54, 0.0)], tr=5.68, col=12, label='Fuel Oil'),
    'FO6_EGPC': dict(l112=17.99, av=0.16, m=[(1.35, 0.0)], tr=5.68, col=13, label='Fuel Oil EGP-C ( Inter. y No Interconectado)'),
    'FO6_1S': dict(l112=17.99, av=0.16, m=[(1.54, 0.0)], tr=5.68, col=17, label='Fuel Oil 1% Azufre (FO6, 1%S)'),
    'FO6_1S_EGPC': dict(l112=17.99, av=0.16, m=[(1.35, 0.0)], tr=5.68, col=18, label='Fuel Oil 1% Azufre (FO6, 1%S) EGP-C ( Inter. y No Interconectado)'),
    'LPG': dict(l112=0.0, av=0.16, m=[(10.21, 14.90), (11.71, 16.90)], tr=5.68, col=None, label='Gas Licuado de Petr'),
}
EXACT = {'DSL_REGULAR', 'FO6', 'FO6_1S', 'GSL_PREMIUM', 'GSL_REGULAR', 'AVTUR', 'KER'}

weeks = [D(2024, 1, 6) + dt.timedelta(days=7 * i) for i in range(52)]

# 1. avisos
avisos = {}
for r in csv.DictReader(open(os.path.join(base, 'avisos_parsed.csv'), encoding='utf-8')):
    m = re.search(r'CORTE-(\d{2})-(\d{2})-(?:DE-)?([A-Z]{3})', r['file'])
    d1, d2, mon = int(m.group(1)), int(m.group(2)), MONTHS[m.group(3)]
    start = D(2024, mon if d1 < d2 else mon - 1, d1)
    avisos.setdefault(start, {})[r['product']] = r

# 2. history xlsx: weeks consecutive from 30 Dec 2023
hist = {}
order = ['PRIMER', 'SEGUNDO', 'TERCER', 'CUARTO']
files = [f for f in glob.glob(os.path.join(base, 'micm_hist2024', '*.xlsx')) if 'CRUDA' in os.path.basename(f).upper()]
files.sort(key=lambda f: [i for i, o in enumerate(order) if o in os.path.basename(f).upper()][0])
wk = D(2023, 12, 30)
for f in files:
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0]
    for r in ws.iter_rows(values_only=True):
        if r and isinstance(r[0], (int, float)) and isinstance(r[1], str) and len(r) > 18 and isinstance(r[5], (int, float)) and r[5] > 0:
            if wk > D(2024, 12, 28):
                break
            hist[wk] = dict(period=r[1].strip(), row=r, file=os.path.basename(f))
            wk += dt.timedelta(days=7)

# 3. resolutions: liquids files sorted by number, mapped to weeks with known gaps (23 Mar, 14 Dec)
res_files = [f for f in os.listdir(os.path.join(base, 'micm_res2024')) if 'NATURAL' not in f.upper()]
res_files.sort(key=lambda f: int(re.search(r'NO\.(\d{3})', f).group(1)))
res_weeks = [w for w in weeks if w not in (D(2024, 3, 23), D(2024, 12, 14))]
assert len(res_files) == len(res_weeks) == 50, (len(res_files), len(res_weeks))
res = dict(zip(res_weeks, res_files))
ocr_nums = {}
for w, f in res.items():
    t = pdfplumber.open(os.path.join(base, 'micm_res2024', f))
    txt = ' '.join((p.extract_text() or '') for p in t.pages)
    txt = re.sub(r'(\d),(\d{3}\.)', r'\1\2', txt)
    toks = re.findall(r'\d{1,3}[.,\-] ?\d{2}(?!\d)', txt)
    nums = set()
    for tk in toks:
        try:
            nums.add(round(float(re.sub(r'[,\-] ?', '.', tk).replace(' ', '')), 2))
        except ValueError:
            pass
    ocr_nums[w] = nums


def official(p, s, dist, det):
    return round(p + round(s['av'] * p, 2) + s['l112'] + dist + det + s['tr'], 2)


def aviso_row(a, k, s):
    for lab, v in a.items():
        if k in EXACT:
            if lab.strip() == s['label']:
                return v
        elif lab.startswith(s['label']):
            return v
    return None


rows = []
for w in weeks:
    for k, s in PROD.items():
        rec = dict(week_start=w.isoformat(), product=k, ppi='', source='', dist='', det='', transp=s['tr'], l112=s['l112'], adval_rate=s['av'],
                   price_public_xlsx='', fx_micm='', aviso_file='', resolution_file=res.get(w, ''), hist_file=hist.get(w, {}).get('file', ''),
                   hist_period=hist.get(w, {}).get('period', ''), check='')
        ar = aviso_row(avisos.get(w, {}), k, s)
        h = hist.get(w)
        if h and s['col'] is not None:
            rec['price_public_xlsx'] = h['row'][s['col']]
        if ar:
            rec.update(ppi=float(ar['ppi']), source='aviso', dist=float(ar['dist']), det=float(ar['det']), fx_micm=ar['fx'], aviso_file=ar['file'])
            if s['col'] is not None and h:
                dist, det = s['m'][0]
                der = round((h['row'][s['col']] - s['l112'] - dist - det - s['tr']) / (1 + s['av']), 2)
                rec['check'] = 'xlsx-derived %.2f vs aviso %.2f' % (der, rec['ppi'])
        elif s['col'] is not None and h:
            dist, det = s['m'][0]
            der = round((h['row'][s['col']] - s['l112'] - dist - det - s['tr']) / (1 + s['av']), 2)
            ok = w in ocr_nums and any(abs(der - x) <= 0.011 for x in ocr_nums[w])
            rec.update(ppi=der, dist=dist, det=det, source='xlsx_derived_ocr_confirmed' if ok else 'xlsx_derived_unconfirmed')
        elif w in ocr_nums:
            nums = ocr_nums[w]
            lo, hi = (75, 100) if k == 'LPG' else (95, 200)
            hits = set()
            for p in nums:
                if not lo <= p <= hi:
                    continue
                for dist, det in s['m']:
                    o = official(p, s, dist, det)
                    if any(abs(o - x) <= 0.021 for x in nums):
                        hits.add((p, dist, det))
            ps = {x[0] for x in hits}
            if len(ps) == 1:
                p, dist, det = sorted(hits)[0]
                rec.update(ppi=p, dist=dist, det=det, source='ocr_matched')
            else:
                rec.update(source='unresolved', check='candidates %s' % sorted(ps))
        else:
            rec.update(source='no document')
        rows.append(rec)

cols = list(rows[0].keys())
with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
    wtr = csv.DictWriter(fh, fieldnames=cols)
    wtr.writeheader()
    wtr.writerows(rows)
for kv in sorted(Counter((r['product'], r['source']) for r in rows).items()):
    print(kv)
