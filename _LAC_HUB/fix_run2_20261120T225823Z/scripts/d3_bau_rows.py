"""Dump the 39 BAU emission-factor rows that the earlier run copied into NDCNEW and LTSNEW (F6), from the base snapshot.
Output: research/d3_bau_rows.csv (country, sheet, row, tech, emission, method, values 2018-2025).
"""
import os
import openpyxl
import pandas as pd

BASE = os.environ.get('LAC_BASE', 'C:/clw_base_4ba69d6')
JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
EARLIER = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z'
PATHS = {'Honduras': 'Honduras/HON_ENERGY', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
         'Ecuador': 'Ecuador/ECU_Energy'}
SHEET = {'Honduras': 'EmissionsActivityRatio', 'DominicanRepublic': 'EmissionsActivityRatio', 'Ecuador': 'SmartGrid'}

d = pd.read_csv(EARLIER + '/scripts/r6_ear_rows_Honduras_DominicanRepublic_Ecuador_Jamaica.csv')
g = d[['country', 'tech', 'emission', 'bau_row']].drop_duplicates()
out = []
for c in PATHS:
    wb = openpyxl.load_workbook(os.path.join(BASE, PATHS[c], 'B1_Scenario_Config.xlsx'), data_only=True, read_only=True)
    ws = wb[SHEET[c]]
    rows = list(ws.iter_rows(values_only=True))
    h = rows[0]
    yc = {int(x): i for i, x in enumerate(h) if str(x).isdigit() and 2018 <= int(x) <= 2025}
    for _, r in g[g.country == c].iterrows():
        v = rows[int(r.bau_row) - 1]
        assert v[0] == 'BAU', (c, r.bau_row, v[:4])
        rec = {'country': c, 'sheet': SHEET[c], 'row': int(r.bau_row), 'tech': r.tech, 'emission': r.emission,
               'cells_a_to_j': ' | '.join(str(x) for x in v[:10])}
        for y in range(2018, 2026):
            rec[str(y)] = v[yc[y]] if y in yc else None
        out.append(rec)
o = pd.DataFrame(out)
o.to_csv(JOB + '/research/d3_bau_rows.csv', index=False, lineterminator='\n')
print(len(o))
print(o[['country', 'row', 'tech', 'emission', '2018', '2021', '2024']].to_string())
