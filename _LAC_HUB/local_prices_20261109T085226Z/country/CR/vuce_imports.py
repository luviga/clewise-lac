"""Summarise PROCOMER / VUCE open-data import records (OData) by year and tariff line.

Usage: py -I vuce_imports.py <pt_tiempo.json> <od_import json> [<od_import json> ...]
Each od_import file is the saved response of
  https://datos.vuce.cr/OpenData/EstadisticasOData.svc/od_import?$filter=startswith(partida,'<HS4>') eq true
(JSON, OData verbose). valor_tot is US dollars, peso_tot is kilograms (valor and peso are the same
in thousands of US dollars and tonnes). Prints, per year and 10-digit line: value USD, kg, USD/t.
"""
import json, sys, collections

t = json.load(open(sys.argv[1], encoding='utf-8'))['d']
t = t['results'] if isinstance(t, dict) else t
year = {r['id_tiempo']: int(r['anno'].strip('*')) for r in t}
month = {r['id_tiempo']: int(r['num_mes']) for r in t}
for path in sys.argv[2:]:
    d = json.load(open(path, encoding='utf-8'))['d']
    rows = d['results'] if isinstance(d, dict) else d
    nxt = d.get('__next') if isinstance(d, dict) else None
    agg = collections.defaultdict(lambda: [0.0, 0.0, set()])
    for r in rows:
        k = (year[r['id_tiempo']], r['partida'])
        agg[k][0] += float(r['valor_tot'])
        agg[k][1] += float(r['peso_tot'])
        agg[k][2].add(month[r['id_tiempo']])
    print('==', path, 'records', len(rows), 'next page:', nxt)
    for (y, p), (v, kg, ms) in sorted(agg.items()):
        if y >= 2017:
            print(f'{y} {p} value_usd={v:,.2f} kg={kg:,.0f} usd_per_t={v / kg * 1000 if kg else float("nan"):.2f} months={len(ms)}')
