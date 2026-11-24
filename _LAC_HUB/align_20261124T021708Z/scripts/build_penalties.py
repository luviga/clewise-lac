"""Register rows of step 7.6: every EmissionsPenalty of the energy and sector models set to 0 in the input data
(external costs are reported after the solve, not paid inside the objective). Sources of the penalties:
A2_Extra_Inputs/A-Xtra_Emissions.xlsx sheet Externalities (column EmissionsPenalty) and B1_Scenario_Config.xlsx
rows whose Parameter is EmissionsPenalty (every value column). Left out: Ecuador ECU_AGR (unchanged by rule) and
Guatemala GUA_AFOLU (its penalties are crop and livestock incomes kept in its own parameter files).
Also step 5.2: Jamaica PPBIM residual capacity 0.005 GW set to 0 (the activity lower limit follows from it).
Writes work/register_penalties.csv."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

import openpyxl

FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
SKIP = {'Ecuador/ECU_AGR', 'Guatemala/GUA_AFOLU'}
DER = 'externalities out of the objective: penalty 0; external costs are reported after the solve in external_costs.csv'
rows = []
for f in sorted(M.ROOT.glob('*/*/A2_Extra_Inputs/A-Xtra_Emissions.xlsx')) + sorted(M.ROOT.glob('*/*/*/A2_Extra_Inputs/A-Xtra_Emissions.xlsx')):
    model = f.parent.parent.relative_to(M.ROOT).as_posix()
    if model in SKIP:
        continue
    wb = openpyxl.load_workbook(f, read_only=True)
    if 'Externalities' not in wb.sheetnames:
        continue
    data = list(wb['Externalities'].iter_rows(values_only=True))
    hdr = [str(h).strip() if h is not None else '' for h in data[0]]
    if 'EmissionsPenalty' not in hdr or 'Tech' not in hdr:
        continue
    t, e, p = hdr.index('Tech'), hdr.index('Tech') + 1, hdr.index('EmissionsPenalty')
    seen = {}
    for r in data[1:]:
        if r[t] is None:
            continue
        k = f'{r[t]}|{r[e]}'
        seen[k] = seen.get(k, 0) + 1
    for r in data[1:]:
        if r[t] is None or r[p] in (None, 0, 0.0):
            continue
        k = f'{r[t]}|{r[e]}'
        rows.append(dict(model=model, file='A2_Extra_Inputs/A-Xtra_Emissions.xlsx', sheet='Externalities', tech=k,
                         parameter='EmissionsPenalty', year='', before=r[p], after=0, unit=data[0][4] if len(data[0]) > 4 else '',
                         source_id='', page='', derivation=DER + ('' if seen[k] == 1 else ' (duplicate key row)'),
                         assumption_sentence='', range_low='', range_high=''))
for f in sorted(M.ROOT.glob('*/*/B1_Scenario_Config.xlsx')):
    model = f.parent.relative_to(M.ROOT).as_posix()
    if model in SKIP:
        continue
    wb = openpyxl.load_workbook(f, read_only=True)
    for ws in wb.worksheets:
        data = list(ws.iter_rows(values_only=True))
        if not data:
            continue
        hdr = [str(h).strip() if h is not None else '' for h in data[0]]
        if 'Parameter' not in hdr or 'Scenario' not in hdr or 'Set' not in hdr:
            continue
        pi, si, ki = hdr.index('Parameter'), hdr.index('Scenario'), hdr.index('Set')
        ycols = [k for k, h in enumerate(hdr) if h.isdigit()]
        for r in data[1:]:
            if r[pi] != 'EmissionsPenalty':
                continue
            for k in ycols:
                if r[k] in (None, 0, 0.0) or isinstance(r[k], str):
                    continue
                rows.append(dict(model=model, file='B1_Scenario_Config.xlsx', sheet=ws.title, tech=f'{r[si]}|{r[ki]}',
                                 parameter='EmissionsPenalty', year=hdr[k], before=r[k], after=0, unit='', source_id='',
                                 page='', derivation=DER, assumption_sentence='', range_low='', range_high=''))
rows.append(dict(model='Jamaica/JAM_ENERGY', file='A1_Outputs/A-O_Parametrization.xlsx', sheet='Secondary Techs', tech='PPBIM',
                 parameter='ResidualCapacity', year=2021, before=0.005, after=0, unit='GW', source_id='JAM-GLEANER-2022-10-01',
                 page='news article, 1 October 2022',
                 derivation='no grid biomass plant: the Frome and Monymusk bagasse cogeneration project was shelved; residual capacity 0, so the activity lower limit (formula from the residual capacity) is 0',
                 assumption_sentence='', range_low='', range_high=''))
out = M.JOB / 'work' / 'register_penalties.csv'
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
from collections import Counter  # noqa: E402
print(len(rows), 'rows ->', out)
for k, v in sorted(Counter((r['model'], r['sheet']) for r in rows).items()):
    print(' ', k, v)
