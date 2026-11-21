"""A3 / D8: sourced Guatemala hydro PJ for 2025 and 2026 (AMM monthly generation by plant, hydro block total, last full
observed year 2025, held in 2026). The overwrite shares are computed in Phase D step DS1 from the new Stage 0 denominators.
Writes proposals_parts/d8.csv (kind d8_target: no cell is written in Phase B)."""
import os, sys
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB
from common_props import write_part

F = JOB + '/downloads/d2_gua/AMM_GM20250101.xlsx'
ws = openpyxl.load_workbook(F, read_only=True, data_only=True)['Energia']
rows = list(ws.iter_rows(max_col=15, values_only=True))
assert rows[2][2] == 2025 and rows[7][1].startswith('PLANTAS HIDRO') and rows[4][14] == 'TOTAL'
gwh = float(rows[7][14])
months = [rows[7][c] for c in range(2, 14)]
assert all(isinstance(m, (int, float)) for m in months) and abs(sum(months) - gwh) < 1e-6
pj = gwh * 0.0036
out = []
for y in (2025, 2026):
    out.append(dict(country='Guatemala', workbook='_STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.csv', sheet='', row='', column='',
                    year=y, Tech='PPHDAM+PPHROR', Parameter='hydro generation target (PJ)', scenario='BAU;NDCNEW;LTSNEW',
                    current_value='share 40.31 + 2.84 percent of each scenario denominator', new_value=repr(pj), kind='d8_target',
                    decision='D8', source_ids='FR2-GUA-01',
                    derivation=f'AMM Generacion Mensual por Planta 2025, sheet Energia row 8 (PLANTAS HIDROELECTRICAS, includes the '
                               f'GDR hydro plants), TOTAL column O = {gwh:.6f} GWh (sum of the 12 months) x 0.0036 PJ/GWh = {pj:.6f} PJ'
                               + ('' if y == 2025 else '; 2025 is the last full observed year, held in 2026 (decision D8)') +
                               '; split PPHDAM : PPHROR by the 2024 overwrite shares 40.31 : 2.84; share(s, y) = PJ / Stage 0 '
                               'denominator(s, y), computed in DS1',
                    assumption=''))
write_part('d8', out)
print(gwh, pj)
