"""Summarise UN Comtrade preview JSON files: CIF value, net weight and unit value (USD/t).
Usage: py -I comtrade_summary.py <json> [<json> ...]"""
import json, sys
for f in sys.argv[1:]:
    d = json.load(open(f, encoding='utf-8'))
    for r in sorted(d.get('data', []), key=lambda r: r['cmdCode']):
        w = r.get('netWgt'); v = r.get('cifvalue') if r.get('cifvalue') is not None else r.get('primaryValue')
        uv = round(v / (w / 1000), 2) if w else None
        print(r['refYear'], r['reporterCode'], r['flowCode'], r['partnerCode'], r['cmdCode'],
              'cif=%s' % v, 'netWgt_kg=%s' % w, 'estW=%s' % r.get('isNetWgtEstimated'),
              'qtyUnit=%s' % r.get('qtyUnitAbbr'), 'USD_per_t=%s' % uv)
