"""Register rows of step 6.3: one emission factor (EmissionActivityRatio) per plant type and emission in every
scenario. The NDC and LTS rows of the scenario workbooks take, year by year, the value of the BAU row of the same
plant and emission (Dominican Republic and Honduras: sheet EmissionsActivityRatio; Ecuador: sheet SmartGrid).
Each BAU factor is checked against the IPCC 2006 default of its fuel (Vol. 2 Ch. 2 Table 2.2, energy industries)
times the plant's fuel input per unit of output (InputActivityRatio of the compiled BAU inputs, 2030):
work/ear_ipcc_check.csv. Writes work/register_ear.csv."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

import openpyxl
import pandas as pd

FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
# IPCC 2006 Vol. 2 Ch. 2 Table 2.2 (energy industries), CO2 kg per TJ (pdf p.16-17), read from the downloaded file
IPCC_CO2 = {'NGS': 56100, 'GAS': 56100, 'DSL': 74100, 'FOI': 77400, 'CRU': 73300, 'GLP': 63100, 'LPG': 63100,
            'COK': 97500, 'COA': 94600}
SPECS = [('DominicanRepublic/RD_ENERGY', 'EmissionsActivityRatio', ('Set', 'Set2')),
         ('Honduras/HON_ENERGY', 'EmissionsActivityRatio', ('Set', 'Set2')),
         ('Ecuador/ECU_Energy', 'SmartGrid', ('Tech_Set',))]
rows, checks = [], []
# IPCC 2006 Table 2.2 CH4 and N2O kg per TJ, and the AR5 global warming potentials the Ecuador inventory uses
# (Documento del Inventario Nacional 2024, ECU-05, p.50: CH4 28, N2O 265)
IPCC_CH4 = {'NGS': 1, 'DSL': 3, 'FOI': 3, 'CRU': 3}
IPCC_N2O = {'NGS': 0.1, 'DSL': 0.6, 'FOI': 0.6, 'CRU': 0.6}
GWP = {'CH4': 28, 'N2O': 265}
# Ecuador: plant factors far from the IPCC default (ear_ipcc_check.csv: -28 to +57 percent) take the IPCC default
# times the plant's fuel input per unit of output in every scenario and year
ECU_IPCC = {'PPDSL', 'PPFOI', 'PPNGS', 'PPCRU', 'PPRNGS', 'PPRDSL'}


def ecu_factor(plant, emission, fin):
    tok = next(t for t in IPCC_CH4 if t in plant)
    gas = emission.split('_')[0]
    kg = {'CO2': IPCC_CO2[tok], 'CH4': IPCC_CH4[tok], 'N2O': IPCC_N2O[tok],
          'CO2e': IPCC_CO2[tok] + GWP['CH4'] * IPCC_CH4[tok] + GWP['N2O'] * IPCC_N2O[tok]}[gas]
    return kg * 1e-6 * fin, kg


for model, sheet, keys in SPECS:
    wb = openpyxl.load_workbook(M.ROOT / model / 'B1_Scenario_Config.xlsx', read_only=True)
    data = list(wb[sheet].iter_rows(values_only=True))
    hdr = [str(h).strip() if h is not None else '' for h in data[0]]
    ycols = [k for k, h in enumerate(hdr) if h.isdigit()]
    ki = [hdr.index(k) for k in keys]
    pi, si = hdr.index('Parameter'), hdr.index('Scenario')
    bau = {}
    for r in data[1:]:
        if r[si] == 'BAU' and r[pi] == 'EmissionActivityRatio':
            bau[tuple(str(r[k]).strip() for k in ki)] = r
    iar = pd.read_csv(M.ROOT / model / 'A2_Output_Params' / 'BAU' / 'InputActivityRatio.csv')
    if model.startswith('Ecuador'):
        for r in data[1:]:
            if r[si] not in ('BAU', 'NDC', 'LTS') or r[pi] != 'EmissionActivityRatio':
                continue
            plant, em = [x.strip() for x in str(r[hdr.index('Tech_Set')]).split(';')]
            if plant not in ECU_IPCC:
                continue
            for k in ycols:
                y = int(hdr[k])
                sub = iar[(iar['TECHNOLOGY'] == plant) & (iar['YEAR'] == y)]
                fin = float(sub['Value'].sum())
                v, kg = ecu_factor(plant, em, fin)
                v = round(v, 10)
                if r[k] is not None and abs(float(r[k]) - v) <= 1e-12:
                    continue
                rows.append(dict(model=model, file='B1_Scenario_Config.xlsx', sheet=sheet,
                                 tech=r[si] + '|' + str(r[hdr.index('Tech_Set')]).strip(), parameter='EmissionActivityRatio',
                                 year=hdr[k], before=r[k], after=v, unit='Mt per PJ of output',
                                 source_id='ALN-IPCC2006-V2C2|ECU-05', page='Table 2.2 (pdf p.16-17); ECU-05 p.50',
                                 derivation=f'{kg:g} kg per TJ of fuel ({em.split("_")[0]}; CO2e with AR5 GWP CH4 28, N2O 265) x 1e-6 x fuel input {fin:.4f} PJ per PJ of output ({y})',
                                 assumption_sentence='', range_low='', range_high=''))
    for r in data[1:]:
        if r[si] not in ('NDC', 'LTS') or r[pi] != 'EmissionActivityRatio':
            continue
        key = tuple(str(r[k]).strip() for k in ki)
        b = bau.get(key)
        if b is None or (model.startswith('Ecuador') and key[0].split(';')[0].strip() in ECU_IPCC):
            continue
        tech = r[si] + '|' + '|'.join(key)
        for k in ycols:
            if b[k] is None or (r[k] is not None and abs(float(r[k]) - float(b[k])) <= 1e-12):
                continue
            rows.append(dict(model=model, file='B1_Scenario_Config.xlsx', sheet=sheet, tech=tech,
                             parameter='EmissionActivityRatio', year=hdr[k], before=r[k], after=b[k],
                             unit='Mt CO2 eq per PJ of output', source_id='ALN-IPCC2006-V2C2', page='Table 2.2 (pdf p.16-17)',
                             derivation='value of the BAU row of the same plant and emission in that year (one factor per plant and emission in every scenario); checked in ear_ipcc_check.csv',
                             assumption_sentence='', range_low='', range_high=''))
    for key, b in bau.items():
        name = key[0].split(';')[0].strip()
        em = key[-1].split(';')[-1].strip() if len(key) > 1 else key[0].split(';')[1].strip()
        tok = next((t for t in IPCC_CO2 if t in name), None)
        if tok is None or not (em.startswith('CO2')):
            continue
        y = hdr.index('2030')
        sub = iar[(iar['TECHNOLOGY'] == name) & (iar['YEAR'] == 2030)]
        fin = float(sub['Value'].sum()) if len(sub) else float('nan')
        ipcc = IPCC_CO2[tok] / 1e6 * fin   # kg/TJ -> Mt/PJ is x 1e-6; times PJ of fuel per PJ of output
        cur = float(b[y]) if b[y] is not None else float('nan')
        checks.append(dict(model=model, plant=name, emission=em, fuel_token=tok, bau_factor_2030=cur,
                           fuel_input_per_output_2030=round(fin, 4), ipcc_co2_kg_per_tj=IPCC_CO2[tok],
                           ipcc_factor=round(ipcc, 6), deviation_pct=round(100 * (cur / ipcc - 1), 1) if ipcc else ''))
out = M.JOB / 'work' / 'register_ear.csv'
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
with open(M.JOB / 'work' / 'ear_ipcc_check.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(checks[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(checks)
print(len(rows), 'rows ->', out, ';', len(checks), 'checks')
