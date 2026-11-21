"""D2c/D2d repair (Phase C, recorded in GAPS): Dominican Republic PPDBGS CapacityFactor (Secondary Techs row 170) from IRENA
Renewable Energy Statistics 2025, Dominican Republic biogas: CF(y) = generation GWh (PDF p.91) / (capacity MW (PDF p.89) x 8.76).
2018-2023 written; 2024 onward keep the row's formula chain (=O170 ...), which holds the 2023 value.
The row copied the distributed-diesel capacity factor (about 0.08), which made the sourced biogas history unreachable with the
2.4 MW residual and forced new capacity in NDCNEW and LTSNEW. Writes proposals_parts/d2c.csv."""
import os, sys
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_props import BASEDIR, write_part

AO = 'DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx'
CAP = {2018: 2, 2019: 2, 2020: 2, 2021: 2, 2022: 4, 2023: 4}          # MW, IRENA25 PDF p.89 (Biogas, Dominican Rep)
GEN = {2018: 16, 2019: 14, 2020: 14, 2021: 14, 2022: 22, 2023: 30}      # GWh, IRENA25 PDF p.91
wb = openpyxl.load_workbook(f'{BASEDIR}/{AO}', data_only=True)
ws = wb['Secondary Techs']
hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
assert ws.cell(170, 2).value == 'PPDBGS' and ws.cell(170, 5).value == 'CapacityFactor'
A = ('ASSUMPTION: the capacity factor of self-producer biogas plants from 2024 to 2050 holds the 2023 value of 0.856, '
     'generation of 30 GWh on 4 MW (IRENA Renewable Energy Statistics 2025); the 2018-2023 published values range from 0.63 '
     'to 0.91, so the range of the held value is 0.63 to 0.91.')
rows = []
for y in range(2018, 2024):
    cf = GEN[y] / (CAP[y] * 8.76)
    rows.append(dict(country='DominicanRepublic', workbook=AO, sheet='Secondary Techs', row=170,
                     column=openpyxl.utils.get_column_letter(hdr[y]), year=y, Tech='PPDBGS', Parameter='CapacityFactor',
                     scenario='ALL', current_value=ws.cell(170, hdr[y]).value, new_value=repr(cf), kind='ao_cell',
                     decision='D2c;D2d', source_ids='FR2-D2-IRENA25',
                     derivation=f'IRENA RE Statistics 2025, Dominican Rep biogas: {GEN[y]} GWh (PDF p.91) / ({CAP[y]} MW (PDF p.89) '
                                f'x 8.76) = {cf:.6f}; 2024-2050 follow the row formula chain (hold 2023)',
                     assumption=A if y == 2023 else ''))
# Dominican Republic PPDHYD (D2f follow-up, Phase D repair): after the 0.0036 conversion the capacity factor of the row's
# own formula is 4.22, because the activity upper limit (0.2328 PJ = 64.7 GWh) is 6.5 times the published self-producer hydro
# generation; Stage 0 then ran PPDHYD at 74 to 193 PJ. The limit is written from UN energy statistics (Electricity, hydro
# autoproducer, Dominican Republic, million kWh): 7 (2018), 9 (2019-2022), 10 (2023); 2024-2050 hold 2023.
UN = {2018: 7, 2019: 9, 2020: 9, 2021: 9, 2022: 9, 2023: 10}
wf = openpyxl.load_workbook(f'{BASEDIR}/{AO}')
wp = wf['Primary Techs']
hp = {wp.cell(1, j).value: j for j in range(1, wp.max_column + 1)}
assert wp.cell(227, hp['Tech']).value == 'PPDHYD' and wp.cell(227, hp['Parameter']).value == 'TotalTechnologyAnnualActivityUpperLimit'
assert wp.cell(227, hp['Projection.Mode']).value == 'Flat'
AH = ('ASSUMPTION: the activity upper limit of self-producer hydro from 2024 to 2050 holds the 2023 generation of 10 GWh '
      '(0.036 PJ) published by the UN energy statistics, the last year printed; published generation grew from 7 to 10 GWh over '
      '2018-2023 on 1.5 to 1.9 MW, so a range of 0.025 to 0.036 PJ covers the observed years.')
rows.append(dict(country='DominicanRepublic', workbook=AO, sheet='Primary Techs', row=227,
                 column=openpyxl.utils.get_column_letter(hp['Projection.Mode']), year='', Tech='PPDHYD',
                 Parameter='TotalTechnologyAnnualActivityUpperLimit (Projection.Mode)', scenario='ALL', current_value='Flat',
                 new_value='User defined', kind='config_cell', decision='D2f;D2c', source_ids='FR2-D2-UNHYD',
                 derivation='mode switched so the limit can vary by year'))
for y in range(2018, 2051):
    gwh = UN[min(y, 2023)]
    cur = wp.cell(227, hp[y]).value
    rows.append(dict(country='DominicanRepublic', workbook=AO, sheet='Primary Techs', row=227,
                     column=openpyxl.utils.get_column_letter(hp[y]), year=y, Tech='PPDHYD',
                     Parameter='TotalTechnologyAnnualActivityUpperLimit', scenario='ALL', current_value=cur,
                     new_value=repr(gwh * 0.0036), kind='ao_cell', decision='D2f;D2c', source_ids='FR2-D2-UNHYD',
                     derivation=f'UN energy statistics, hydro autoproducer, Dominican Republic, {min(y, 2023)}: {gwh} million kWh x '
                                f'0.0036 PJ/GWh = {gwh * 0.0036:.4f} PJ' + ('' if y <= 2023 else '; 2023 held'),
                     assumption=AH if y >= 2024 else ''))
# policy history elements of PPDHYD = new BAU: lower (Flat row 228 = J227 x 0.999) and upper (row 227 by year), 4 decimals
CFG = 'DominicanRepublic/RD_ENERGY/B1_Scenario_Config.xlsx'
cw = openpyxl.load_workbook('C:/clw_fix/' + CFG, read_only=True)['Electrical']
CR = list(cw.iter_rows(values_only=True))
newlow = round(UN[2018] * 0.0036 * 0.999, 4)
for r, par, scen in [(25, 'Lower', 'LTSNEW'), (83, 'Lower', 'NDCNEW'), (181, 'Upper', 'LTSNEW'), (193, 'Upper', 'NDCNEW')]:
    v = CR[r - 1]
    assert v[0] == scen and v[2] == 'PPDHYD' and par in v[1], (r, v[:3])
    ys = [int(x) for x in str(v[6]).split(';')]
    xs = [x.strip() for x in str(v[7]).split(';')]
    while xs and xs[-1] == '':
        xs.pop()
    old = ' ; '.join(xs)
    for i, y in enumerate(ys):
        if y <= 2024:
            xs[i] = f'{newlow:.10g}' if par == 'Lower' else f'{round(UN[min(y, 2023)] * 0.0036, 4):.10g}'
    rows.append(dict(country='DominicanRepublic', workbook=CFG, sheet='Electrical', row=r, column='H', year='2018-2024',
                     Tech='PPDHYD', Parameter=f'TotalTechnologyAnnualActivity{par}Limit', scenario=scen, current_value=str(v[7]),
                     new_value=' ; '.join(xs), kind='config_cell', decision='D2a;D2f', source_ids='',
                     derivation='history elements 2018-2024 take the new BAU value (A-O row 227 by year; lower = row 227 2018 x 0.999, '
                                'Flat), rounded to 4 decimals as A2 rounds'))
write_part('d2c', rows)
print(len(rows))
