"""D5 (Honduras PPBGS CapitalCost) and D2f (Dominican Republic PPDHYD CapacityFactor formula). Reads the base snapshot.
Writes proposals_parts/misc.csv."""
import os, sys
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_props import BASEDIR, write_part

rows = []
# D5
AO = 'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx'
wb = openpyxl.load_workbook(f'{BASEDIR}/{AO}')
ws = wb['Secondary Techs']
hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
assert ws.cell(27, hdr['Tech']).value == 'PPBGS' and ws.cell(27, hdr['Parameter']).value == 'CapitalCost'
v2018 = ws.cell(27, hdr[2018]).value
assert abs(v2018 - 7269.10) < 0.01, v2018
assert ws.cell(27, hdr['Projection.Mode']).value == 'User defined'
for y in range(2018, 2051):
    cur = ws.cell(27, hdr[y]).value
    if isinstance(cur, (int, float)) and abs(cur - v2018) <= 1e-9 * v2018:
        continue
    rows.append(dict(country='Honduras', workbook=AO, sheet='Secondary Techs', row=27,
                     column=openpyxl.utils.get_column_letter(hdr[y]), year=y, Tech='PPBGS', Parameter='CapitalCost', scenario='ALL',
                     current_value=cur, new_value=repr(float(v2018)), kind='ao_cell', decision='D5', source_ids='R1F-11;BEN-004',
                     derivation='IRENA 2012 biogas Case 10 capital cost converted to the model currency year with US CPI-U '
                                '(the 2018-2020 value of this row, 7,269.10 USD/kW), held in every year 2018-2050 (decision D5); '
                                'Projection.Mode stays User defined'))
# D2f
AO = 'DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx'
wb = openpyxl.load_workbook(f'{BASEDIR}/{AO}')
wv = openpyxl.load_workbook(f'{BASEDIR}/{AO}', data_only=True)
ws = wb['Primary Techs']
hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
assert ws.cell(230, hdr['Tech']).value == 'PPDHYD' and ws.cell(230, hdr['Parameter']).value == 'CapacityFactor'
j = hdr[2018]
f = ws.cell(230, j).value
assert f == '=J227/(J225*8760)', f
rows.append(dict(country='DominicanRepublic', workbook=AO, sheet='Primary Techs', row=230,
                 column=openpyxl.utils.get_column_letter(j), year=2018, Tech='PPDHYD', Parameter='CapacityFactor', scenario='ALL',
                 current_value=wv['Primary Techs'].cell(230, j).value, new_value='',
                 new_formula='=J227/(J225*8760*0.0036)', kind='ao_formula', decision='D2f', source_ids='',
                 derivation='unit conversion 0.0036 PJ per GWh added: capacity factor = activity upper limit (PJ) / (residual '
                            'capacity (GW) x 8,760 h x 0.0036 PJ per GWh); Flat row, so it applies in every year and scenario'))
write_part('misc', rows)
print(len(rows))
