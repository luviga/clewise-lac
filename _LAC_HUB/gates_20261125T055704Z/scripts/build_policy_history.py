"""Step 5.3 at the source: the policy rows (NDC, LTS) of the B1 workbook sheet Electrical take, for every year up to
history_end_year in their Exact_Years, the compiled BAU value of the same parameter and technology
(B1_Output_Params/BAU of the latest compile), divided by the row's Security_Multiplier (the runner multiplies the
written values by it). Writes work/register_policy_history.csv.
With --caps, the power plant capacity and activity limit rows of the policy scenarios take the BAU value in every year.
Usage: python -I build_policy_history.py <model> [<model> ...] [--caps]"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import io
import sys

import openpyxl
import pandas as pd

LAST = 2024
OPEN_CAP = 9999.0     # the open capacity value the B1 workbooks use (TotalAnnualMaxCapacity)
FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
rows = []
for model in [m for m in sys.argv[1:] if not m.startswith('--')]:
    p = M.ROOT / model / 'B1_Scenario_Config.xlsx'
    wb = openpyxl.load_workbook(io.BytesIO(p.read_bytes()), read_only=True)
    data = list(wb['Electrical'].iter_rows(values_only=True))
    hdr = [str(h) for h in data[0]]
    cache = {}
    seen = set()
    for r in data[1:]:
        d = dict(zip(hdr, r))
        if d.get('Scenario') not in ('NDC', 'LTS') or not d.get('Exact_Years') or not d.get('Exact_Values'):
            continue
        key = (d['Scenario'], d['Parameter'], d['Tech_Set'])
        if key in seen:
            continue          # the runner reads the first row of a scenario, technology and parameter
        seen.add(key)
        par, tech = d['Parameter'], d['Tech_Set']
        ys = [y.strip() for y in str(d['Exact_Years']).split(';')]
        vs = [v.strip() for v in str(d['Exact_Values']).split(';')]
        if len(ys) != len(vs) or not any(y.isdigit() and int(y) <= LAST for y in ys):
            continue
        if par not in cache:
            f = M.ROOT / model / 'B1_Output_Params' / 'BAU' / f'{par}.csv'
            cache[par] = pd.read_csv(f) if f.exists() else pd.DataFrame()
        b = cache[par]
        if b.empty and not ('--caps' in sys.argv and par == 'TotalAnnualMaxCapacity'):
            continue
        sub = b[b['TECHNOLOGY'] == tech] if not b.empty else b
        bau = dict(zip(sub['YEAR'].astype(int), sub['Value'])) if not b.empty else {}
        mult = float(d.get('Security_Multiplier') or 1)
        new = list(vs)
        allyears = '--caps' in sys.argv and par in ('TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityLowerLimit', 'TotalTechnologyAnnualActivityUpperLimit') and str(tech).startswith(('PP', 'PWR'))
        for i, y in enumerate(ys):
            if allyears and y.isdigit() and int(y) not in bau and par == 'TotalAnnualMaxCapacity':
                v = OPEN_CAP / mult     # BAU has no cap for this plant: the cap is open
                new[i] = f'{v:.6f}'.rstrip('0').rstrip('.')
                continue
            if y.isdigit() and (int(y) <= LAST or allyears) and int(y) in bau:
                v = bau[int(y)] / mult
                new[i] = f'{v:.6f}'.rstrip('0').rstrip('.') if v else '0'
        if new != vs:
            rows.append(dict(model=model, file='B1_Scenario_Config.xlsx', sheet='Electrical',
                             tech=f"{d['Scenario']}|{tech}", parameter=par, year='Exact_Values',
                             before=d['Exact_Values'], after=' ; '.join(new), unit='',
                             source_id='', page='',
                             derivation=(f'every year takes the compiled BAU value divided by the Security_Multiplier {mult}: the policy limit of this plant (from an earlier stylised target) is not a published policy measure (Stage 3 replaces plant limits from 2025 with the controller of the published targets)' if allyears else
                                         f'history years up to {LAST} take the compiled BAU value divided by the Security_Multiplier {mult} (history is the same in every scenario)'),
                             assumption_sentence='', range_low='', range_high=''))
with open(M.JOB / 'work' / 'register_policy_history.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows')
