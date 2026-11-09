"""Average the parsed MEM weekly price structures over 2024.

Usage: py -I gua_aggregate.py <estructuras_parsed.csv>
Equal weight per published week. Duplicate uploads of the same week (file name
ending in -1 with identical values) are dropped. Prints, per slide, the number of
weeks, the weeks used, the mean of each component (GTQ per published unit) and the
mean published total, plus derived means: pre-tax price (total minus IDP minus IVA),
wholesale before retail (CIF plus freight, other costs, terminal, port, importer margin).
"""
import csv
import re
import sys
from collections import defaultdict

MESES = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7,
         'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}


def file_date(fn):
    m = re.search(r'al-(\d{2})-([a-z]+)-(\d{4})', fn)
    return '%s-%02d-%s' % (m.group(3), MESES[m.group(2)], m.group(1))


def main(path):
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    by = defaultdict(lambda: defaultdict(dict))  # fuel -> week -> comp -> value
    files = defaultdict(dict)
    for r in rows:
        if r['component'] == 'ERROR' or r['value'] == '':
            continue
        wk = file_date(r['file'])
        if wk[:4] != '2024':
            continue
        if wk in files[r['fuel']] and files[r['fuel']][wk] != r['file']:
            continue  # duplicate upload of the same week
        files[r['fuel']][wk] = r['file']
        comp = r['component']
        d = by[r['fuel']][wk]
        if comp in d and comp == 'importer_margin':
            comp = 'importer_margin_2'
        d[comp] = float(r['value'])
        if r['total']:
            d['_total'] = float(r['total'])
    for fuel in sorted(by):
        weeks = sorted(by[fuel])
        print('\n### %s weeks=%d' % (fuel, len(weeks)))
        print('weeks:', ';'.join(weeks))
        months = sorted({int(w[5:7]) for w in weeks})
        print('months:', ';'.join(str(m) for m in months))
        comps = sorted({c for w in weeks for c in by[fuel][w]})
        for c in comps:
            vals = [by[fuel][w][c] for w in weeks if c in by[fuel][w]]
            print('mean\t%s\t%s\tn=%d\t%.4f\tmin=%.4f\tmax=%.4f' % (fuel, c, len(vals), sum(vals) / len(vals), min(vals), max(vals)))
        # derived
        pt, wh = [], []
        for w in weeks:
            d = by[fuel][w]
            tot = d.get('_total')
            if fuel == 'LPG_automotive_gal':
                tot = sum(v for k, v in d.items() if k not in ('_total', 'subtotal_planta'))
            if tot is None:
                continue
            pt.append(tot - d.get('idp', 0.0) - d.get('iva', 0.0))
            wh.append(sum(d.get(k, 0.0) for k in ('cif', 'inland_freight', 'other_costs', 'terminal', 'port',
                                                  'importer_margin', 'importer_margin_2')))
        print('derived\t%s\tpre_tax_total\tn=%d\t%.4f' % (fuel, len(pt), sum(pt) / len(pt)))
        print('derived\t%s\twholesale_before_retail\tn=%d\t%.4f' % (fuel, len(wh), sum(wh) / len(wh)))
        print('weekly\t%s\t' % fuel + ' '.join('%s:cif=%.3f' % (w, by[fuel][w].get('cif', float('nan'))) for w in weeks))


if __name__ == '__main__':
    main(sys.argv[1])
