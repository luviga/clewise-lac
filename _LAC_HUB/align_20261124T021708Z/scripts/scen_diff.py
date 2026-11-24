"""Compiled inputs that differ between BAU and a policy scenario, per model (B1_Output_Params, or A2 with --a2).
Usage: python -I scen_diff.py <root> <out.csv> [--a2]
One row per (model, parameter, scenario, technology, fuel, emission, year group) with the number of cells, the
years and an example; year group: history (up to 2024) or projection (2025 on)."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import csv
import sys
from pathlib import Path

import pandas as pd

root = Path(sys.argv[1])
out = sys.argv[2]
folder = 'A2_Output_Params' if '--a2' in sys.argv else 'B1_Output_Params'
MODELS = ['CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic/RD_ENERGY', 'Ecuador/ECU_Energy',
          'Guatemala/GUA_ENERGY', 'Honduras/HON_ENERGY', 'Jamaica/JAM_ENERGY']
KEYS = ['REGION', 'TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE', 'SEASON', 'DAYTYPE',
        'DAILYTIMEBRACKET', 'STORAGE']
rows = []
for m in MODELS:
    base = root / m / folder / 'BAU'
    for pol in ['NDC', 'LTS']:
        pdir = root / m / folder / pol
        for f in sorted(base.glob('*.csv')):
            g = pdir / f.name
            if not g.exists():
                continue
            a = pd.read_csv(f, dtype=str, keep_default_na=False)
            b = pd.read_csv(g, dtype=str, keep_default_na=False)
            if 'Value' not in a.columns:
                continue
            k = [c for c in KEYS if c in a.columns]
            a = a.drop_duplicates(k, keep='last').set_index(k)['Value']
            b = b.drop_duplicates(k, keep='last').set_index(k)['Value']
            j = pd.concat([a.rename('bau'), b.rename('pol')], axis=1)
            j['bau_n'] = pd.to_numeric(j['bau'], errors='coerce')
            j['pol_n'] = pd.to_numeric(j['pol'], errors='coerce')
            d = j[~((j['bau_n'] - j['pol_n']).abs() <= 1e-9 * (1 + j['bau_n'].abs()))]
            d = d[~(d['bau'].isna() & d['pol'].isna())]
            if d.empty:
                continue
            d = d.reset_index()
            d['YEAR_i'] = pd.to_numeric(d.get('YEAR', ''), errors='coerce')
            d['grp'] = d['YEAR_i'].apply(lambda y: 'history' if y == y and y <= 2024 else 'projection')
            idx = [c for c in ['TECHNOLOGY', 'FUEL', 'EMISSION'] if c in d.columns]
            for key, sub in d.groupby(idx + ['grp'], dropna=False):
                key = key if isinstance(key, tuple) else (key,)
                kd = dict(zip(idx + ['grp'], key))
                ex = sub.iloc[0]
                yrs = sorted(int(y) for y in sub['YEAR_i'].dropna())
                rows.append(dict(model=m, parameter=f.stem, scenario=pol, technology=kd.get('TECHNOLOGY', ''),
                                 fuel=kd.get('FUEL', ''), emission=kd.get('EMISSION', ''), year_group=kd['grp'],
                                 cells=len(sub), first_year=yrs[0] if yrs else '', last_year=yrs[-1] if yrs else '',
                                 example_year=ex.get('YEAR', ''), bau_value=ex['bau'], policy_value=ex['pol']))
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ['model'], lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'groups ->', out)
