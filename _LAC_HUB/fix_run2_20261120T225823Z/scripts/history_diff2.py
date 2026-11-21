"""History differences (years <= 2024) between BAU and NDCNEW/LTSNEW in B1_Output_Params, with a missing key
read as the model default of that parameter. Relative tolerance 1e-4.
Run: py -I scripts/history_diff2.py <root> <out_csv>"""
import sys, os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MODELS, KEYS, load_params, defaults

ROOT, OUT = sys.argv[1], sys.argv[2]
rows = []
for c, m in MODELS.items():
    dflt = defaults(m, ROOT)
    base = load_params(os.path.join(ROOT, m, 'B1_Output_Params', 'BAU'))
    for sc in ['NDCNEW', 'LTSNEW']:
        other = load_params(os.path.join(ROOT, m, 'B1_Output_Params', sc))
        mrg = base.merge(other, on=KEYS, how='outer', suffixes=('_bau', '_sc'), indicator=True)
        mrg['yr'] = pd.to_numeric(mrg.YEAR, errors='coerce')
        h = mrg[mrg.yr <= 2024].copy()
        dv = h.PARAMETER.map(lambda p: dflt.get(p, float('nan')))
        h['b'] = h.v_bau.where(h._merge != 'right_only', dv)
        h['s'] = h.v_sc.where(h._merge != 'left_only', dv)
        h['absd'] = (h.b - h.s).abs()
        h['reld'] = h.absd / h[['b', 's']].abs().max(axis=1).where(lambda x: x > 0, 1)
        d = h[(h.reld > 1e-4) | h.b.isna() | h.s.isna()]
        for _, r in d.iterrows():
            rows.append(dict(country=c, scenario=sc, parameter=r.PARAMETER, technology=r.TECHNOLOGY, fuel=r.FUEL,
                             emission=r.EMISSION, mode=r.MODE_OF_OPERATION, timeslice=r.TIMESLICE, year=int(r.yr),
                             bau=r.b, scen=r.s, presence=r._merge, absd=r.absd, reld=r.reld))
o = pd.DataFrame(rows)
o.to_csv(OUT, index=False, lineterminator='\n')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 80); pd.set_option('display.max_rows', 500)
if len(o):
    s = o.groupby(['country', 'scenario', 'parameter', 'presence']).agg(
        n=('year', 'size'), ntech=('technology', 'nunique'),
        techs=('technology', lambda x: ','.join(sorted(set(x))[:7])), fuels=('fuel', lambda x: ','.join(sorted(set(x))[:3])),
        maxabs=('absd', 'max'), maxrel=('reld', 'max'))
    print(s.to_string())
print('rows', len(o))
