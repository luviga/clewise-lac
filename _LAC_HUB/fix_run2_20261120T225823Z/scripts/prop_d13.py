"""D13: CapacityToActivityUnit 31.536 for every power plant whose value is 31.356, 31.4 or 31.54 (Fixed Horizon Parameters
of each A-O workbook). Reads the base snapshot. Writes proposals_parts/d13.csv and logs/d13_scan.csv (every CAU row seen)."""
import os, sys, collections, csv
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB
from common_props import BASEDIR, write_part

AO = {
    'CostaRica': 'CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx',
    'DominicanRepublic': 'DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
    'Ecuador': 'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx',
    'Guatemala': 'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
    'Honduras': 'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
    'Jamaica': 'Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
}
TARGETS = (31.356, 31.4, 31.54)
rows, scan, excluded = [], [], []
for c, path in AO.items():
    wbf = openpyxl.load_workbook(f'{BASEDIR}/{path}')
    wbv = openpyxl.load_workbook(f'{BASEDIR}/{path}', data_only=True)
    ws, wv = wbf['Fixed Horizon Parameters'], wbv['Fixed Horizon Parameters']
    hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
    for r in range(2, ws.max_row + 1):
        t = ws.cell(r, hdr['Tech']).value
        p = ws.cell(r, hdr['Parameter']).value
        if p != 'CapacityToActivityUnit' or t is None:
            continue
        f = ws.cell(r, hdr['Value']).value
        v = wv.cell(r, hdr['Value']).value
        scan.append(dict(country=c, row=r, tech=t, value=v, formula=f if isinstance(f, str) else ''))
        if isinstance(f, str):
            print('FORMULA', c, r, t, f)
        is_plant = str(t).startswith('PP') or str(t).startswith('PWR')   # power plants only (F16); IMP_ELE, STOELE, DIST_* stay
        if v is not None and any(abs(float(v) - x) < 1e-9 for x in TARGETS) and not is_plant:
            excluded.append(dict(country=c, row=r, tech=t, value=v, formula=''))
        if v is not None and any(abs(float(v) - x) < 1e-9 for x in TARGETS) and is_plant:
            rows.append(dict(country=c, workbook=path, sheet='Fixed Horizon Parameters', row=r,
                             column=openpyxl.utils.get_column_letter(hdr['Value']), year='', Tech=t,
                             Parameter='CapacityToActivityUnit', scenario='ALL', current_value=v, new_value='31.536',
                             kind='ao_cell', decision='D13', source_ids='',
                             derivation='unit conversion: 8,760 h per year x 0.0036 PJ per GWh = 31.536 PJ per GW-year',
                             assumption=''))
with open(f'{JOB}/logs/d13_scan.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['country', 'row', 'tech', 'value', 'formula'], lineterminator='\n')
    w.writeheader(); w.writerows(scan)
with open(f'{JOB}/logs/d13_not_plants.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['country', 'row', 'tech', 'value', 'formula'], lineterminator='\n')
    w.writeheader(); w.writerows(excluded)
write_part('d13', rows)
print(collections.Counter((r['country'], r['current_value']) for r in rows))
vals = collections.Counter((s['country'], s['value']) for s in scan)
print(sorted(vals.items(), key=lambda x: (x[0][0], str(x[0][1]))))
