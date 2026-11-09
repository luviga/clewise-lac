"""Parse MEM weekly 'Estructuras de Precios referenciales' slide PDFs.

Usage: py -I gua_estructuras.py <folder with PDFs> <output csv>
For each slide (gasoline superior, gasoline regular, diesel, LPG 25 lb cylinder,
automotive LPG, bunker) it reads the component labels and the values in the
'Quetzales' column, pairs them by vertical order, and checks that the components
add up to the published total. Writes one row per file, slide and component.
"""
import csv
import glob
import os
import re
import sys

import pdfplumber

MESES = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7,
         'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}

LABELS = [
    ('PRECIO A EXPENDEDOR EN PLANTA', 'subtotal_planta'),
    ('PRECIO A CONSUMIDOR', None),
    ('PRECIO CONSUMIDOR', None),
    ('PRECIO EX RACK', None),
    ('PRECIO CIF', 'cif'),
    ('IMPUESTO A LA DISTRIBU', 'idp'),
    ('IMPUESTO DISTRIBU', 'idp'),
    ('IMPUESTO AL VALOR', 'iva'),
    ('IMPUESTO VALOR', 'iva'),
    ('FLETE TERRESTRE', 'inland_freight'),
    ('OTROS GASTOS', 'other_costs'),
    ('GASTOS DE TERMINAL', 'terminal'),
    ('CARGOS PORTUARIOS', 'port'),
    ('MARGEN BRUTO DEL IMPORTADOR', 'importer_margin'),
    ('MARGEN DEL IMPORTADOR', 'importer_margin'),
    ('MARGEN IMPORTADOR', 'importer_margin'),
    ('MARGEN DEL ENVASADOR', 'bottler_margin'),
    ('MARGEN DEL EXPENDEDOR', 'retail_margin'),
    ('MARGEN EXPENDEDOR', 'retail_margin'),
]
NUM = re.compile(r'^Q?\.?\s?(\d{1,3}(?:,\d{3})*\.\d{1,4})$')


def fuel_of(text):
    t = text.upper()
    if 'GASOLINA SUPERIOR' in t:
        return 'GSL_superior'
    if 'GASOLINA REGULAR' in t:
        return 'GSL_regular'
    if 'DIESEL' in t and 'ESTRUCTURA' in t:
        return 'DSL'
    if 'GLP AUTOMOTRIZ' in t:
        return 'LPG_automotive_gal'
    if '25 LIBRAS' in t:
        return 'LPG_cylinder_25lb'
    if 'BUNKER' in t:
        return 'FOI_bunker'
    return None


def slide_date(text):
    m = re.search(r'(\d{1,2})\s+(?:de\s+)?([a-záéíóú]+)\s+de\s+(\d{4})', text, re.I)
    if m and m.group(2).lower() in MESES:
        return '%s-%02d-%02d' % (m.group(3), MESES[m.group(2).lower()], int(m.group(1)))
    return ''


def parse_page(page):
    text = page.extract_text() or ''
    fuel = fuel_of(text)
    if not fuel:
        return None
    words = page.extract_words(keep_blank_chars=True, x_tolerance=2)
    for w in words:
        w['yc'] = (w['top'] + w['bottom']) / 2
        w['t'] = w['text'].strip()
    hdr = [w for w in words if w['t'].upper().startswith('QUETZALES')]
    labels = []
    for w in words:
        tu = w['t'].upper()
        for key, code in LABELS:
            if tu.startswith(key):
                labels.append((w['yc'], code, w['t'], w))
                break
    nums = []
    for w in words:
        m = NUM.match(w['t'].replace(' ', ''))
        if m:
            nums.append((w, float(m.group(1).replace(',', ''))))
    if not hdr:
        return fuel, slide_date(text), None, 'no Quetzales header'
    hx0, hx1 = hdr[0]['x0'] - 15, hdr[0]['x1'] + 15
    # rebuild the numbers of the Quetzales column from single characters
    chars = [c for c in page.chars if c['x0'] >= hx0 and c['x1'] <= hx1 and c['top'] > hdr[0]['bottom'] - 2
             and c['text'] in '0123456789.,Q']
    lines = []
    for c in sorted(chars, key=lambda c: ((c['top'] + c['bottom']) / 2, c['x0'])):
        yc = (c['top'] + c['bottom']) / 2
        if lines and abs(lines[-1][0] - yc) < 3:
            lines[-1][1].append(c)
        else:
            lines.append([yc, [c]])
    qcol = []
    for yc, cs in lines:
        t = ''.join(c['text'] for c in sorted(cs, key=lambda c: c['x0'])).replace(' ', '')
        m = NUM.match(t)
        if m:
            qcol.append((yc, float(m.group(1).replace(',', '')), t))
    labels.sort(key=lambda r: r[0])
    used = set()
    comps = []
    total = None
    for y, code, lt, lw in labels:
        cands = [(abs(q[0] - y), k) for k, q in enumerate(qcol) if k not in used and abs(q[0] - y) < 12]
        if not cands:
            if code is not None:
                comps.append((code, lt, None))
            continue
        k = min(cands)[1]
        used.add(k)
        if code is None:
            total = qcol[k][1]
        else:
            comps.append((code, lt, qcol[k][1]))
    if total is None:
        outside = [v for w, v in nums if w['t'].startswith('Q')]
        total = max(outside) if outside else None
    return fuel, slide_date(text), (comps, total), ''


def main(folder, out):
    rows = []
    for fn in sorted(glob.glob(os.path.join(folder, '*.pdf'))):
        with pdfplumber.open(fn) as pdf:
            for i, p in enumerate(pdf.pages):
                r = parse_page(p)
                if not r:
                    continue
                fuel, sdate, res, err = r
                base = os.path.basename(fn)
                if res is None:
                    rows.append(dict(file=base, page=i + 1, fuel=fuel, slide_date=sdate, component='ERROR',
                                     label=err, value='', total='', check=''))
                    continue
                comps, total = res
                s = sum(v for c, lt, v in comps if c != 'subtotal_planta' and v is not None)
                chk = '' if total is None else round(s - total, 3)
                for c, lt, v in comps:
                    rows.append(dict(file=base, page=i + 1, fuel=fuel, slide_date=sdate, component=c,
                                     label=lt, value=v, total=total, check=chk))
    with open(out, 'w', newline='', encoding='utf-8') as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print('rows', len(rows))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
