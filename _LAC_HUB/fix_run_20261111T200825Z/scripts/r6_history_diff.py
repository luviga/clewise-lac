"""R6: find by values where NDCNEW and LTSNEW differ from BAU in history years (<= 2024).

Compares the tracked A2_Output_Params and B1_Output_Params CSVs of the three scenarios,
keyed on every column except Scenario and Value. Writes r6_history_diff.csv (one row per
differing key) and prints a summary per country, stage, parameter.
Run: py -I scripts/r6_history_diff.py <root> <out_csv>
"""
import sys, os, glob
import pandas as pd

ROOT = sys.argv[1]
OUT = sys.argv[2]
MODELS = {
    'CostaRica': 'CostaRica/CR_ENERGY/t1_confection',
    'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
    'Ecuador': 'Ecuador/ECU_Energy',
    'Guatemala': 'Guatemala/GUA_ENERGY',
    'Honduras': 'Honduras/HON_ENERGY',
    'Jamaica': 'Jamaica/JAM_ENERGY',
}
KEYS = ['PARAMETER', 'REGION', 'TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE', 'SEASON',
        'DAYTYPE', 'DAILYTIMEBRACKET', 'STORAGE']


def load(folder):
    frames = []
    for f in sorted(glob.glob(os.path.join(folder, '*.csv'))):
        try:
            d = pd.read_csv(f, dtype=str, keep_default_na=False)
        except Exception:
            continue
        if 'Value' not in d.columns or 'PARAMETER' not in d.columns or len(d) == 0:
            continue
        for k in KEYS:
            if k not in d.columns:
                d[k] = ''
        d['file'] = os.path.basename(f)
        frames.append(d[KEYS + ['Value', 'file']])
    if not frames:
        return pd.DataFrame(columns=KEYS + ['Value', 'file'])
    x = pd.concat(frames, ignore_index=True)
    x['v'] = pd.to_numeric(x.Value, errors='coerce')
    return x


rows = []
for c, m in MODELS.items():
    for stage in ['A2_Output_Params', 'B1_Output_Params']:
        base = load(os.path.join(ROOT, m, stage, 'BAU'))
        for sc in ['NDCNEW', 'LTSNEW']:
            other = load(os.path.join(ROOT, m, stage, sc))
            mrg = base.merge(other, on=KEYS, how='outer', suffixes=('_bau', '_sc'), indicator=True)
            mrg['yr'] = pd.to_numeric(mrg.YEAR, errors='coerce')
            hist = mrg[(mrg.yr <= 2024) | mrg.yr.isna()]
            diff = hist[(hist._merge != 'both') | ((hist.v_bau - hist.v_sc).abs() > 1e-9 * hist[['v_bau', 'v_sc']].abs().max(axis=1).clip(lower=1))]
            for _, r in diff.iterrows():
                rows.append(dict(country=c, stage=stage, scenario=sc, parameter=r.PARAMETER, technology=r.TECHNOLOGY, fuel=r.FUEL,
                                 emission=r.EMISSION, mode=r.MODE_OF_OPERATION, year=r.YEAR, timeslice=r.TIMESLICE,
                                 bau=r.v_bau, scen=r.v_sc, presence=r._merge))
o = pd.DataFrame(rows)
o.to_csv(OUT, index=False)
if len(o):
    s = o.groupby(['country', 'stage', 'scenario', 'parameter']).agg(n=('year', 'size'), techs=('technology', lambda x: ','.join(sorted(set(x))[:8])),
                                                                     years=('year', lambda x: f'{min(x)}-{max(x)}'))
    pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90); pd.set_option('display.max_rows', 500)
    print(s.to_string())
else:
    print('no differences')
