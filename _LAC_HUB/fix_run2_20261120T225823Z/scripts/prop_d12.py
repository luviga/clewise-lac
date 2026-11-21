"""D1 and D12: Ecuador Fixed Horizon Parameters. OperationalLife for the 36 technologies with CapitalCost > 0 (sourced, by
class, research/d12_lives.md checked against the files), and new row pairs for PPHD (CapacityToActivityUnit 31.536, D1) and
PRONGS (CapacityToActivityUnit 1, keeps the pair layout). Reads the base snapshot. Writes proposals_parts/d12.csv.
Kinds: ao_cell (existing Value cell, by Tech and Parameter), fhp_newrow (new row; new_value = JSON of the row)."""
import os, sys, json
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_props import BASEDIR, write_part

AO = 'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx'
S = {  # source ids (sources.csv)
    'ARC': 'FR2-D12-01',   # ARCONEL-004/24 Codificada, PDF p.40, Anexo 1 Tablas 2 and 3
    'MCI': 'FR2-D12-02',   # ARCERNNR cost of service 2021, PDF p.18, Cuadro 1
    'MCID': 'FR2-D12-03',  # Regulacion ARCERNNR 001/23, PDF p.59 Anexo D, definition of vida util
    'LEY': 'FR2-D12-04',   # Ley de Hidrocarburos Art. 23, PDF p.15-16
    'KIT': 'CCG-002',      # CCG starter kit Ecuador Base SAND.xlsm
    'DIB': 'CCG-014',      # data article doi 10.1016/j.dib.2022.108021
    'PLM': 'FR2-D12-06',   # PLANMICC OperationalLife.csv at 7483e67
    'ATB': 'FR2-D12-08',   # NREL ATB 2024 definitions, Technical Lifetimes
    'H2': 'FR2-D12-09',    # IRENA Green hydrogen cost reduction 2020, PDF p.43
}
L = {}
for t in ['ELE_TRANS']:
    L[t] = (45, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 3 (PDF p.40): Lineas de Transmision 45 years')
for t in ['ELE_DIST']:
    L[t] = (35, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 3 (PDF p.40): Alimentadores Primarios 35 and Redes Secundarias 35 years')
for t in ['PPPVT', 'PPPVTS', 'PPPVD', 'PPPVDS']:
    L[t] = (25, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 legend (PDF p.40): Fotovoltaica (25 anos)')
for t in ['PPWNDON', 'PPWNDD']:
    L[t] = (25, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 legend (PDF p.40): Eolica (25 anos)')
for t in ['PPHDAMAB', 'PPHDAMAM', 'PPHDAMPM', 'PPHRORAB', 'PPHRORAM', 'PPHRORPM']:
    L[t] = (50, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 (PDF p.40), Hidraulica > 50MW, Infraestructura Civil-Obras Hidraulicas 50 years')
for t in ['PPHDAMAS', 'PPHDAMPS', 'PPHRORAS', 'PPHRORPS']:
    L[t] = (40, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 (PDF p.40), Hidraulica 5 - 50MW, Infraestructura Civil-Obras Hidraulicas 40 years')
for t in ['PPHD', 'PPIHD']:
    L[t] = (33, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 (PDF p.40), Hidraulica 0,5 - 5MW, Infraestructura Civil-Obras Hidraulicas 33 years')
for t in ['PPCRU', 'PPDSL', 'PPRDSL', 'PPDDSL', 'PPFOI', 'PPDFOI', 'PPILPG', 'PPBGS']:
    L[t] = (25, S['MCI'] + ';' + S['MCID'], 'ARCERNNR cost of service 2021 (PDF p.18, Cuadro 1), reference internal-combustion engine '
                                         'plant: Vida Util (n) 25 years')
for t in ['PPBIM', 'PPIBIM']:
    L[t] = (30, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 (PDF p.40), Termica de Vapor, Equipos e Instalaciones Electromecanicas 30 years')
for t in ['PPNGS', 'PPRNGS']:
    L[t] = (20, S['ARC'], 'ARCONEL-004/24 Anexo 1 Tabla 2 (PDF p.40), Termica Gas Industrial, Equipos e Instalaciones Electromecanicas 20 years')
L['PPGEO'] = (20, S['KIT'] + ';' + S['DIB'], 'CCG starter kit Ecuador, Parameters!J31144 (PWRGEO) 20 years; data article Table 10 (PDF p.16) 20')
L['HYD_G_PROD'] = (30, S['PLM'] + ';' + S['H2'], 'PLANMICC OperationalLife.csv at 7483e67, line 152 (HYDPROELEGRI) 30 years; IRENA 2020 '
                                                'PDF p.43: alkaline electrolysers have proven lifetimes of over 30 years')
L['STOELE'] = (15, S['ATB'], 'NREL ATB 2024 Definitions, Technical Lifetimes: Utility-scale battery storage 15 years')
L['PRONGS'] = (25, S['LEY'] + ';FR2-D12-10', 'Ley de Hidrocarburos Art. 23 (PDF p.15-16): natural gas exploitation period up to 25 years')
A_PRONGS = ('ASSUMPTION: the natural gas production assets have an operational life of 25 years (2018-2050), the maximum '
            'exploitation period of an Ecuador natural gas contract (Ley de Hidrocarburos, Art. 23); the contract term stands in for '
            'an asset life because no Ecuador or international document consulted states a gas-field asset life; the US tax class '
            'life for gas production assets (IRS Publication 946, class 13.2) is 14 years, so the range is 14 to 25 years.')
assert len(L) == 36, len(L)

wb = openpyxl.load_workbook(f'{BASEDIR}/{AO}')
ws = wb['Fixed Horizon Parameters']
hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
idx = {}
for r in range(2, ws.max_row + 1):
    t, p = ws.cell(r, hdr['Tech']).value, ws.cell(r, hdr['Parameter']).value
    if t:
        idx[(t, p)] = r
rows = []
vc = openpyxl.utils.get_column_letter(hdr['Value'])
for t, (life, src, der) in sorted(L.items()):
    a = A_PRONGS if t == 'PRONGS' else ''
    if (t, 'OperationalLife') in idx:
        r = idx[(t, 'OperationalLife')]
        rows.append(dict(country='Ecuador', workbook=AO, sheet='Fixed Horizon Parameters', row=r, column=vc, year='', Tech=t,
                         Parameter='OperationalLife', scenario='ALL', current_value=ws.cell(r, hdr['Value']).value,
                         new_value=repr(float(life)), kind='ao_cell', decision='D12', source_ids=src, derivation=der, assumption=a))
    else:
        assert t in ('PPHD', 'PRONGS'), t
# new row pairs: PPHD after the Primary block, PRONGS after the Secondary block (positions resolved by the writer)
names = {}
for sh in ['Primary Techs', 'Secondary Techs']:
    w2 = wb[sh]
    for r in range(2, w2.max_row + 1):
        names.setdefault(w2.cell(r, 2).value, (sh, w2.cell(r, 3).value))
for t, ttype, cau, cau_der, cau_src in [
        ('PPHD', 'Primary', 31.536, 'unit conversion: 8,760 h x 0.0036 PJ per GWh = 31.536 PJ per GW-year (decision D1)', ''),
        ('PRONGS', 'Secondary', 1.0, 'equal to the A2 default of 1 for a missing row; added only to keep the row-pair layout', '')]:
    tname = names[t][1]
    for pid, par, unit, val, der, src in [(1, 'CapacityToActivityUnit', 'PJ/PJ', cau, cau_der, cau_src),
                                          (2, 'OperationalLife', 'Years', float(L[t][0]), L[t][2], L[t][1])]:
        rec = {'Tech.Type': ttype, 'Tech': t, 'Tech.Name': tname, 'Parameter.ID': pid, 'Parameter': par, 'Unit': unit, 'Value': val}
        rows.append(dict(country='Ecuador', workbook=AO, sheet='Fixed Horizon Parameters', row='new', column='', year='', Tech=t,
                         Parameter=par, scenario='ALL', current_value='no row', new_value=json.dumps(rec), kind='fhp_newrow',
                         decision='D1' if (t == 'PPHD' and par == 'CapacityToActivityUnit') else 'D12', source_ids=src,
                         derivation=der + ('; insert after the last row of the ' + ttype + ' block, Tech.ID chain rebuilt'),
                         assumption=A_PRONGS if (t == 'PRONGS' and par == 'OperationalLife') else ''))
write_part('d12', rows)
print(len(rows), sorted(set((r['Tech'], r['current_value'], r['new_value'][:12]) for r in rows if r['kind'] == 'ao_cell'))[:6])
