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
write_part('d2c', rows)
print([round(float(r['new_value']), 4) for r in rows])
