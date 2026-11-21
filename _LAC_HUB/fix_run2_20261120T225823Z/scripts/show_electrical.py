"""Show the Electrical sheet layout of each B1 config (header, method counts, one example per method). Read-only."""
import sys, collections
import openpyxl

BASE = 'C:/clw_base_4ba69d6/'
M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
     'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
     'Jamaica': 'Jamaica/JAM_ENERGY'}
for c, p in M.items():
    wb = openpyxl.load_workbook(BASE + p + '/B1_Scenario_Config.xlsx', read_only=True)
    rows = list(wb['Electrical'].iter_rows(values_only=True))
    h = rows[0]
    hi = {x: i for i, x in enumerate(h) if x is not None}
    print('==', c, 'rows', len(rows) - 1)
    print('  header', [x for x in h if x is not None])
    cnt = collections.Counter((r[hi['Scenario']], r[hi['Built-in Parameter-Set']], r[hi['Method']]) for r in rows[1:] if r[0])
    print('  counts', dict(cnt))
    seen = set()
    for i, r in enumerate(rows[1:], start=2):
        m = (r[hi['Built-in Parameter-Set']], r[hi['Method']])
        if m in seen or not r[0]:
            continue
        seen.add(m)
        print('  ex row', i, {k: (str(r[j])[:60] if r[j] is not None else None) for k, j in hi.items()})
