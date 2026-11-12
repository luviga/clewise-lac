"""R6: list B1_Scenario_Config rows of NDCNEW / LTSNEW that write history years (<= 2024).

For year-column sheets: rows whose Method writes year columns and that have a value in a history column.
For the Electrical sheet: rows whose Exact_Years include a history year, or whose y_ini is before 2024.
Run: py -I scripts/r6_config_scan.py <root> <out_csv>
"""
import sys, os
import pandas as pd
import openpyxl

ROOT, OUT = sys.argv[1], sys.argv[2]
CFG = {
    'CostaRica': 'CostaRica/CR_ENERGY/t1_confection/B1_Scenario_Config.xlsx',
    'DominicanRepublic': 'DominicanRepublic/RD_ENERGY/B1_Scenario_Config.xlsx',
    'Ecuador': 'Ecuador/ECU_Energy/B1_Scenario_Config.xlsx',
    'Guatemala': 'Guatemala/GUA_ENERGY/B1_Scenario_Config.xlsx',
    'Honduras': 'Honduras/HON_ENERGY/B1_Scenario_Config.xlsx',
    'Jamaica': 'Jamaica/JAM_ENERGY/B1_Scenario_Config.xlsx',
}
SC = ['NDCNEW', 'LTSNEW']
rows = []
for c, f in CFG.items():
    wb = openpyxl.load_workbook(os.path.join(ROOT, f), data_only=True, read_only=True)
    act = {}
    for r in wb['Scenarios'].iter_rows(min_row=2, values_only=True):
        if r[0]: act[r[0]] = r[1]
    for ws in wb.worksheets:
        data = list(ws.iter_rows(values_only=True))
        if not data: continue
        hdr = list(data[0])
        if 'Scenario' not in hdr: continue
        ic = {h: i for i, h in enumerate(hdr) if h is not None}
        ycols = {int(h): i for h, i in ic.items() if isinstance(h, (int, float)) and 2015 <= int(h) <= 2060}
        for k, r in enumerate(data[1:], start=2):
            sc = r[ic['Scenario']]
            if sc is None: continue
            par = r[ic['Parameter']] if 'Parameter' in ic else None
            st = r[ic.get('Set', ic.get('Tech_Set', ic.get('Group_Set', 0)))]
            meth = r[ic['Method']] if 'Method' in ic else None
            hist = []
            if ycols:
                hist = [y for y, i in ycols.items() if y <= 2024 and r[i] is not None]
            ey = r[ic['Exact_Years']] if 'Exact_Years' in ic else None
            yini = r[ic['y_ini']] if 'y_ini' in ic else None
            if ey is not None and str(ey).strip() != 'intact':
                try:
                    hist = [int(float(x)) for x in str(ey).replace(' ', '').split(';') if x and int(float(x)) <= 2024]
                except ValueError:
                    pass
            rows.append(dict(country=c, sheet=ws.title, row=k, scenario=sc, active=act.get(sc), parameter=par, set=st, method=meth,
                             exact_years=ey, y_ini=yini, hist_years=';'.join(map(str, hist)), n_hist=len(hist)))
o = pd.DataFrame(rows)
o.to_csv(OUT, index=False)
x = o[o.scenario.isin(SC + ['All', 'BAU'])]
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 400); pd.set_option('display.max_colwidth', 60)
print(x.groupby(['country', 'sheet', 'scenario']).agg(rows=('row', 'size'), with_hist=('n_hist', lambda s: (s > 0).sum())).to_string())
