"""Register rows of step 7.7: each country's social discount rate of its public investment system in
B1_Default_Param.xlsx (DiscountRate) and in the output discounting of config/execution/Config_MOMF_T1_AB.yaml.
Rates read in the downloaded documents (work/research_R1.csv, topic A); Jamaica publishes none: mean of the five.
Writes work/register_discount.csv (workbook rows) and edits the YAML lines in place (logged in the same table)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import re

import openpyxl

FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
RATE = {'CostaRica': (0.0831, 'ALN-UNA-2024', 'PDF p.10 and p.18', 'MIDEPLAN social discount rate set in 2019 (8.31 percent), as tabulated by the source'),
        'DominicanRepublic': (0.12, 'ALN-UNA-2024', 'PDF p.18, Table 1.1', 'MEPyD 2017 social discount rate, status in force (12 percent)'),
        'Ecuador': (0.12, 'ALN-CEPAL-ECU-2021', 'PDF p.1 and p.2', 'standard social discount rate applied by the planning institutions (12 percent)'),
        'Guatemala': (0.07, 'ALN-UNA-2024', 'PDF p.18, Table 1.1', 'SEGEPLAN social discount rate updated in 2022 to 7 percent (12 percent in 2019)'),
        'Honduras': (0.12, 'ALN-UNA-2024', 'PDF p.18, Table 1.1', 'DGIP general methodology guide 2015, status in force (12 percent)')}
mean5 = round(sum(v[0] for v in RATE.values()) / len(RATE), 5)
RATE['Jamaica'] = (mean5, '', '', '')
JAM_ASSUM = (f"ASSUMPTION: Jamaica's discount rate is {mean5 * 100:.3f} percent a year, the mean of the social discount "
             "rates of the five other countries (Costa Rica 8.31, Dominican Republic 12, Ecuador 12, Guatemala 7, "
             "Honduras 12 percent); the Jamaican public investment guidelines (2016) and handbook (2024) state no rate. "
             "Range 7 to 12 percent.")
MODEL = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
         'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
         'Jamaica': 'Jamaica/JAM_ENERGY'}
rows = []
for c, (r, sid, page, what) in RATE.items():
    wb = openpyxl.load_workbook(M.ROOT / MODEL[c] / 'B1_Default_Param.xlsx', read_only=True)
    cur = next(row[1] for row in wb.worksheets[0].iter_rows(values_only=True) if row[0] == 'DiscountRate')
    rows.append(dict(model=MODEL[c], file='B1_Default_Param.xlsx', sheet='Default_Values', tech='', parameter='DiscountRate',
                     year='', before=cur, after=r, unit='fraction per year', source_id=sid, page=page,
                     derivation=what if sid else 'mean of the five other rates',
                     assumption_sentence='' if sid else JAM_ASSUM, range_low=0.07, range_high=0.12))
# YAML: output discounting of each country block that has one
yp = M.ROOT / 'config' / 'execution' / 'Config_MOMF_T1_AB.yaml'
lines = yp.read_text(encoding='utf-8').split('\n')
country = None
for i, ln in enumerate(lines):
    m = re.match(r'^  (\w+):\s*$', ln)
    if m:
        country = m.group(1)
        continue
    m = re.match(r'^(    (output_discount_rate|discount_rate): )([0-9.]+)(.*)$', ln)
    if m and country in RATE:
        new = RATE[country][0]
        if float(m.group(3)) != new:
            rows.append(dict(model='config/execution', file='Config_MOMF_T1_AB.yaml', sheet='countries', tech=country,
                             parameter=m.group(2), year='', before=m.group(3), after=new, unit='fraction per year',
                             source_id=RATE[country][1], page=RATE[country][2],
                             derivation='same rate as DiscountRate of the B1 defaults', assumption_sentence='' if RATE[country][1] else JAM_ASSUM,
                             range_low=0.07, range_high=0.12))
            lines[i] = f'{m.group(1)}{new}{m.group(4)}'
with open(yp, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(lines))
out = M.JOB / 'work' / 'register_discount.csv'
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows; Jamaica mean', mean5)
