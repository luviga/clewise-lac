"""Print the Stage 1 and Stage 2 shares and lower limits of one country and scenario around chosen years.
Usage: python gua_look.py <stage1.xlsx> <stage2.xlsx> <Country> <Scenario> <year,year,...>"""
import sys
import warnings

import pandas as pd

warnings.filterwarnings('ignore')
s1, s2, c, s, yrs = sys.argv[1:6]
yrs = [int(y) for y in yrs.split(',')]
pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 200)
out = {}
for tag, path in (('S1', s1), ('S2', s2)):
    for sheet in ('CURRENT_SHARES', 'CURRENT_LOWER'):
        d = pd.read_excel(path, sheet_name=sheet)
        d.columns = [int(x) if str(x).isdigit() else x for x in d.columns]
        g = d[(d['Country'] == c) & (d['Scenario'] == s)].set_index('Tech')
        out[(tag, sheet)] = g
grp = out[('S2', 'CURRENT_SHARES')][['Group', 'Sub_Group']] if 'Sub_Group' in out[('S2', 'CURRENT_SHARES')] else None
for sheet in ('CURRENT_SHARES', 'CURRENT_LOWER'):
    t = pd.DataFrame(index=out[('S2', sheet)].index)
    if grp is not None:
        t['Group'] = grp['Group']
    for y in yrs:
        t[f'S1_{y}'] = out[('S1', sheet)][y]
        t[f'S2_{y}'] = out[('S2', sheet)][y]
    print('==', sheet)
    print(t.round(4).to_string())
    print('sum', t.drop(columns=[c for c in t.columns if c == 'Group']).sum().round(4).to_dict())
