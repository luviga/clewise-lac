"""Parse ARESEP (Intendencia de Energia) monthly RECOPE price resolutions for 2024.

Usage: py -I parse_aresep_cr.py <txt_dir> <out_csv>
<txt_dir> holds the PyMuPDF text files written by extract_text.py.
Writes one long CSV: period,resolution,file,product,component,value,unit,pdf_page.

Components:
  fx            CRC/USD used by ARESEP to convert RECOPE invoices (BCCR sell rate, 15-day mean)
  coa           costo de adquisicion, CRC/L (Cuadro 'Determinacion del Costo de Adquisicion (COA)')
  mo, rsbt      margen de operacion and redito sobre base tarifaria, CRC/L
  fob_est, term_nosub, term_sub   subsidy table (Bunker, Bunker Termico ICE, ICE 2, LPG), CRC/L
  tax           impuesto unico, CRC/L
  plantel_sin, plantel_con        Por Tanto I.a plantel price without / with impuesto unico, CRC/L
  station_sin_iva                 Por Tanto I.d station price without VAT on transport (includes impuesto unico), CRC/L
"""
import re, sys, os, csv, unicodedata

DOCS = [
    ('2024-01', 'RE-0002-IE-2024', 'RE-0002-IE-2024', None),
    ('2024-02', 'RE-0013-IE-2024', 'RE-0013-IE-2024', None),
    ('2024-03', 'RE-0021-IE-2024', 'RE-0021-IE-2024', None),
    ('2024-04', 'RE-0034-IE-2024', 'RE-0034-IE-2024', None),
    ('2024-05', 'RE-0040-IE-2024', 'RE-0040-IE-2024', None),
    ('2024-06', 'RE-0043-IE-2024', 'ALCA108_10_06_2024', r'^RE-0043-IE-2024\s*$'),
    ('2024-07', 'RE-0050-IE-2024', 'RE-0050-IE-2024', None),
    ('2024-08', 'RE-0059-IE-2024', 'RE-0059-IE-2024', None),
    ('2024-09', 'RE-0062-IE-2024', 'RE-0062-IE-2024', None),
    ('2024-10', 'RE-0068-IE-2024', 'RE-0068-IE-2024', None),
    ('2024-11', 'RE-0076-IE-2024', 'RE-0076-IE-2024', None),
    ('2024-12', 'RE-0083-IE-2024', 'RE-0083-IE-2024', None),
    ('2025-01', 'RE-004-IE-2025', 'RE-004-IE-2025', None),
]

NUM = re.compile(r'^-?\s*\d{1,3}(?:[   ]\d{3})*(?:,\d+)?%?$')


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', s).strip()


def tonum(t):
    t = t.replace(' ', '').replace(' ', '').replace(' ', '').replace('%', '').replace(',', '.')
    return float(t)


def tokens(lines):
    out = []
    for ln in lines:
        ln = ln.replace(' ', ' ').strip()
        if not ln or ln.startswith('=====PAGE'):
            continue
        for p in re.split(r'\s{2,}|\|', ln):
            p = p.strip()
            if not p:
                continue
            if p in ('-', '- -'):
                out.append(('num', 0.0))
            elif NUM.match(p):
                out.append(('num', tonum(p)))
            else:
                out.append(('txt', p))
    return out


def records(lines):
    recs, name, nums = [], [], []
    for k, v in tokens(lines):
        if k == 'txt':
            if nums:
                recs.append((' '.join(name), nums))
                name, nums = [], []
            name.append(v)
        else:
            nums.append(v)
    if nums:
        recs.append((' '.join(name), nums))
    return recs


# order matters: more specific first
PRODUCTS = [
    ('FOI_ICE2', lambda n: 'termico ice 2' in n),
    ('FOI_ICE', lambda n: 'termico ice' in n),
    ('GSL95', lambda n: 'gasolina ron 95' in n and 'pescador' not in n),
    ('GSL91', lambda n: 'gasolina ron 91' in n and 'pescador' not in n),
    ('DSL', lambda n: 'diesel' in n and 'automotriz' in n and 'pescador' not in n),
    ('KER', lambda n: 'keroseno' in n),
    ('JET', lambda n: re.search(r'jet fuel a-?1', n) is not None),
    ('AVG', lambda n: 'av-gas' in n or 'avgas' in n),
    ('FOI', lambda n: re.search(r'\bbunker\b', n) is not None and 'termico' not in n),
    ('IFO380', lambda n: 'ifo 380' in n),
    ('LPG', lambda n: 'lpg' in n and '70-30' in n),
    ('LPG_PROP', lambda n: 'lpg' in n and 'propano' in n),
]


def prod_of(name):
    n = norm(re.sub(r'\(\d\)', '', name))
    # keep the tail of the name after the last header-like word
    for key, fn in PRODUCTS:
        if fn(n):
            return key
    return None


def find(L, pat, start=0):
    rx = re.compile(pat)
    for i in range(start, len(L)):
        if rx.search(L[i]):
            return i
    return -1


def page_of(L, i):
    for k in range(i, -1, -1):
        m = re.match(r'=====PAGE (\d+)=====', L[k])
        if m:
            return int(m.group(1))
    return None


def seg(L, i, endpat, maxlen=250):
    j = find(L, endpat, i + 1)
    return L[i + 1:(j if 0 < j < i + maxlen else i + maxlen)]


def tail(name, cut):
    parts = re.split(cut, name)
    return parts[-1]


def parse(path, start_pat=None):
    L = [x.rstrip('\r') for x in open(path, encoding='utf-8').read().split('\n')]
    off = 0
    if start_pat:
        off = find(L, start_pat)
    out = []

    def add(prod, comp, val, unit, i):
        out.append((prod, comp, val, unit, page_of(L, i)))

    # exchange rate
    i = find(L, r'por d[oó]lar, el cual se obtuvo', off)
    txt = ' '.join(L[i - 2:i + 1])
    m = re.findall(r'(\d{3},\d{2})\s*por d', txt)
    if m:
        add('all', 'fx', tonum(m[-1]), 'CRC/USD', i)
    # COA
    i = find(L, r'Determinaci[oó]n del Costo de Adquisici[oó]n \(COA\)', off)
    if i < 0:
        i = find(L, r'costo de adquisici[oó]n final por barril', off)
    seen = set()
    for nm, nums in records(seg(L, i, r'^Fuente')):
        p = prod_of(tail(nm, r'litro'))
        if p and p not in seen and len(nums) >= 2:
            seen.add(p)
            add(p, 'coa', nums[-1], 'CRC/L', i)
            add(p, 'coa_bbl', nums[-2], 'CRC/bbl', i)
    # MO / RSBT
    i = find(L, r'C[aá]lculo de componentes de margen de operaci[oó]n', off)
    seen = set()
    for nm, nums in records(seg(L, i, r'^Fuente')):
        p = prod_of(tail(nm, r'RSBT'))
        if p and p not in seen and len(nums) >= 2:
            seen.add(p)
            add(p, 'mo', nums[-2], 'CRC/L', i)
            add(p, 'rsbt', nums[-1], 'CRC/L', i)
    # subsidy table with Precio FOB estimado
    i = find(L, r'^\s*Precio FOB\s*$', off)
    if i > 0:
        for nm, nums in records(seg(L, i, r'Total del subsidio')):
            p = prod_of(tail(nm, r'millones\)'))
            if p == 'FOI_ICE' and len(nums) >= 8 and nums[0] == 2:
                p, nums = 'FOI_ICE2', nums[1:]
            if p and len(nums) >= 7:
                add(p, 'fob_est', nums[2], 'CRC/L', i)
                add(p, 'term_nosub', nums[3], 'CRC/L', i)
                add(p, 'term_sub', nums[4], 'CRC/L', i)
    # impuesto unico
    i = find(L, r'^\s*Impuesto [uú]nico a los combustibles\s*$', off)
    seen = set()
    for nm, nums in records(seg(L, i, r'^Fuente|^\s*Fuente|Precio ICE|^\d+\.\s')):
        if 'pescador' in norm(nm):
            continue
        p = prod_of(tail(nm, r'litro'))
        if p and p not in seen and nums:
            seen.add(p)
            add(p, 'tax', nums[-1], 'CRC/L', i)
    # Por Tanto I.a plantel prices
    i = find(L, r'a\.\s*Precios en planteles de abasto:', off)
    seen = set()
    for nm, nums in records(seg(L, i, r'^\(1\) Para efecto')):
        p = prod_of(tail(nm, r'\(3\)'))
        if p and p not in seen and len(nums) >= 2:
            seen.add(p)
            add(p, 'plantel_sin', nums[-2], 'CRC/L', i)
            add(p, 'plantel_con', nums[-1], 'CRC/L', i)
    # Por Tanto I.b prices by mass (price with tax per litre, reference density kg/m3)
    i = find(L, r'^\s*b\.\s*Precios en planteles de abasto por masa', off)
    seen = set()
    for nm, nums in records(seg(L, i, r'^\(1\) Para efecto')):
        p = prod_of(tail(nm, r'masa'))
        if p and p not in seen and len(nums) >= 3:
            seen.add(p)
            add(p, 'masa_con_l', nums[-3], 'CRC/L', i)
            add(p, 'dens_ref', nums[-2], 'kg/m3', i)
            add(p, 'masa_con_kg', nums[-1], 'CRC/kg', i)
    # Por Tanto I.d station prices
    i = find(L, r'^\s*d\.\s*Precios al consumidor final en estaci[oó]n de servicio', off)
    seen = set()
    for nm, nums in records(seg(L, i, r'^\(1\) El precio final')):
        p = prod_of(tail(nm, r'\(4\)'))
        if p and p not in seen and len(nums) >= 3:
            seen.add(p)
            add(p, 'station_sin_iva', nums[0], 'CRC/L', i)
            add(p, 'station_con_iva', nums[-1], 'CRC/L', i)
    # June: rectification RE-0044-IE-2024 replaces station prices for Av-Gas and Jet fuel
    if start_pat:
        r = find(L, r'RECTIFICACI[OÓ]N DE LA RESOLUCI[OÓ]N RE-0043-IE-2024', 0)
        if r > 0:
            i = find(L, r'^\s*d\.\s*Precios al consumidor final en estaci[oó]n de servicio', r)
            fix = {}
            for nm, nums in records(seg(L, i, r'^\(1\) El precio final')):
                p = prod_of(tail(nm, r'\(4\)'))
                if p in ('AVG', 'JET') and p not in fix and len(nums) >= 3:
                    fix[p] = (nums[0], nums[-1])
            out2 = []
            for row in out:
                if row[0] in fix and row[1] in ('station_sin_iva', 'station_con_iva'):
                    continue
                out2.append(row)
            out = out2
            for p, (a, b) in fix.items():
                add(p, 'station_sin_iva', a, 'CRC/L', i)
                add(p, 'station_con_iva', b, 'CRC/L', i)
    return out


if __name__ == '__main__':
    txt_dir, out_csv = sys.argv[1], sys.argv[2]
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['period', 'resolution', 'file', 'product', 'component', 'value', 'unit', 'pdf_page'])
        for per, res, stem, sp in DOCS:
            rows = parse(os.path.join(txt_dir, stem + '.txt'), sp)
            for prod, comp, val, unit, pg in rows:
                w.writerow([per, res, stem + '.pdf', prod, comp, val, unit, pg])
            print(per, res, len(rows))
