"""D2b: history lower limits against reachable output, per power technology and year, from B1_Output_Params.
reachable = ResidualCapacity x sum_l(CapacityFactor x YearSplit) x AvailabilityFactor x CapacityToActivityUnit
Run: py -I scripts/reach.py <root> <out_csv> [scenario]"""
import sys, os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MODELS, load_params, defaults

ROOT, OUT = sys.argv[1], sys.argv[2]
SC = sys.argv[3] if len(sys.argv) > 3 else 'BAU'
rows = []
for c, m in MODELS.items():
    d = load_params(os.path.join(ROOT, m, 'B1_Output_Params', SC))
    dflt = defaults(m, ROOT)
    d['y'] = pd.to_numeric(d.YEAR, errors='coerce')
    def get(par):
        return d[d.PARAMETER == par]
    cau = get('CapacityToActivityUnit').set_index('TECHNOLOGY').v.to_dict()
    ys = get('YearSplit')
    cf = get('CapacityFactor')
    af = get('AvailabilityFactor').set_index(['TECHNOLOGY', 'y']).v.to_dict()
    res = get('ResidualCapacity').set_index(['TECHNOLOGY', 'y']).v.to_dict()
    ll = get('TotalTechnologyAnnualActivityLowerLimit').set_index(['TECHNOLOGY', 'y']).v.to_dict()
    ul = get('TotalTechnologyAnnualActivityUpperLimit').set_index(['TECHNOLOGY', 'y']).v.to_dict()
    mxc = get('TotalAnnualMaxCapacity').set_index(['TECHNOLOGY', 'y']).v.to_dict()
    mnc = get('TotalAnnualMinCapacityInvestment').set_index(['TECHNOLOGY', 'y']).v.to_dict()
    cfm = cf.merge(ys[['TIMESLICE', 'y', 'v']].rename(columns={'v': 'ys'}), on=['TIMESLICE', 'y'], how='left')
    cfm['w'] = cfm.v * cfm.ys
    cfa = cfm.groupby(['TECHNOLOGY', 'y']).w.sum().to_dict()
    techs = sorted(t for t in set(d.TECHNOLOGY) if t.startswith('PP') or t.startswith('PWR'))
    for t in techs:
        for y in range(2018, 2025):
            if (t, y) not in ll and (t, y) not in res and (t, y) not in cfa:
                continue
            r = res.get((t, y), dflt.get('ResidualCapacity', 0))
            f = cfa.get((t, y), dflt.get('CapacityFactor', 1))
            a = af.get((t, y), dflt.get('AvailabilityFactor', 1))
            u = cau.get(t, dflt.get('CapacityToActivityUnit', 1))
            lo = ll.get((t, y), 0.0)
            reach = r * f * a * u
            rows.append(dict(country=c, scenario=SC, tech=t, year=y, residual_gw=r, cf=f, af=a, cau=u, reachable_pj=reach,
                             lower_pj=lo, upper_pj=ul.get((t, y)), maxcap_gw=mxc.get((t, y)), mincapinv_gw=mnc.get((t, y)),
                             excess_pj=lo - reach, need_gw=(lo - reach) / (f * a * u) if f * a * u > 0 else float('nan')))
o = pd.DataFrame(rows)
o.to_csv(OUT, index=False, lineterminator='\n')
v = o[o.excess_pj > 1e-6]
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 600)
print(v.round(5).to_string())
print(len(o), len(v))
