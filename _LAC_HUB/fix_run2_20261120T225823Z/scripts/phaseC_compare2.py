"""C2: keyed comparison of the recompiled A2_Output_Params and B1_Output_Params (working tree) against the base snapshot
(4ba69d6). Every differing (country, stage, scenario, parameter, technology, year-range) is classified as allowed by a decision
or 'unexplained'. Writes recompile_diff_summary.csv and logs/recompile_diff_unexplained.csv.
Usage: py -I scripts/phaseC_compare2.py [Country ...]"""
import glob, os, sys
import pandas as pd

ROOT = 'C:/clw_fix/'
BASE = 'C:/clw_base_4ba69d6/'
JOB = ROOT + '_LAC_HUB/fix_run2_20261120T225823Z'
M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
     'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
     'Jamaica': 'Jamaica/JAM_ENERGY'}
KEYS = ['PARAMETER', 'REGION', 'TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE', 'SEASON', 'DAYTYPE',
        'DAILYTIMEBRACKET', 'STORAGE']
P = pd.read_csv(JOB + '/proposals.csv', dtype=str, keep_default_na=False)
d13 = set(zip(P[P.decision == 'D13'].country, P[P.decision == 'D13'].Tech))
d7a = set(zip(P[P.decision.str.contains('D7a')].country, P[P.decision.str.contains('D7a')].Tech))
d3 = set(zip(P[P.decision == 'D3'].country, P[P.decision == 'D3'].Tech))
d2rows = set(zip(P[P.decision.str.startswith('D2')].country, P[P.decision.str.startswith('D2')].Tech))
ECU = {'EXTT_CRU', 'DIST_CRU', 'PROCRU', 'REF_DSL', 'REF_GSL', 'REF_LPG', 'REF_FOI', 'REF_JET', 'PPHD', 'E5EXPCRU', 'T5CRUEXP'}


def load(folder):
    fr = []
    for f in glob.glob(folder + '/*.csv'):
        try:
            d = pd.read_csv(f, dtype=str, keep_default_na=False)
        except Exception:
            continue
        if 'PARAMETER' not in d.columns or 'Value' not in d.columns:
            continue
        for k in KEYS:
            if k not in d.columns:
                d[k] = ''
        fr.append(d[KEYS + ['Value']])
    if not fr:
        return pd.DataFrame(columns=KEYS + ['v'])
    x = pd.concat(fr, ignore_index=True)
    x['v'] = pd.to_numeric(x.Value, errors='coerce')
    return x.drop(columns='Value').groupby(KEYS, as_index=False).v.first()


def reason(c, stage, s, par, tech, y0, y1, maxabs):
    if maxabs <= 0.00005 + 1e-12:
        return 'rounding (at most 0.00005)'
    if c == 'Ecuador' and tech == 'PRONGS' and par == 'CapacityToActivityUnit':
        return 'D12 layout row (value 1 = default)'
    if par == 'CapacityToActivityUnit' and (c, tech) in d13:
        return 'D13'
    if c == 'Ecuador' and (tech in ECU or par == 'OperationalLife' or (par == 'CapacityToActivityUnit' and tech == 'PPHD')):
        return 'D-ECU / D1 / D12'
    if par == 'SpecifiedAnnualDemand' and c == 'Ecuador':
        return 'D-ECU1 (E5EXPCRU)'
    if (c, tech) in d7a and 'ActivityLowerLimit' in par:
        return 'D7a band'
    if c == 'Jamaica' and tech == 'REF_FOI' and 'UpperLimit' in par:
        return 'D7a dependent (upper = lower band x 1.01 from 2024)'
    if c == 'Honduras' and tech == 'PPBGS' and par == 'CapitalCost':
        return 'D5'
    if c == 'Guatemala' and tech == 'DIST_FLEXFUEL' and par == 'VariableCost':
        return 'D6'
    if c == 'DominicanRepublic' and tech in ('PPDHYD', 'PPDBGS') and par == 'CapacityFactor':
        return 'D2f / D2c capacity factor'
    if par == 'EmissionActivityRatio' and (c, tech) in d3 and y1 <= 2024:
        return 'D3 history factor'
    if s in ('NDCNEW', 'LTSNEW') and y1 <= 2024:
        return 'D2 history 2018-2024'
    if (c, tech) in d2rows and s in ('NDCNEW', 'LTSNEW'):
        return 'D2 row (check from 2025)'
    return 'unexplained'


out, unex = [], []
countries = sys.argv[1:] or list(M)
for c in countries:
    for stage in ('A2_Output_Params', 'B1_Output_Params'):
        for s in ('BAU', 'NDCNEW', 'LTSNEW'):
            a = load(f'{BASE}{M[c]}/{stage}/{s}')
            b = load(f'{ROOT}{M[c]}/{stage}/{s}')
            m = a.merge(b, on=KEYS, how='outer', suffixes=('_a', '_b'), indicator=True)
            m['d'] = (m.v_a.fillna(-9e99) - m.v_b.fillna(-9e99)).abs()
            m = m[(m._merge != 'both') | (m.d > 1e-9 * m[['v_a', 'v_b']].abs().max(axis=1).clip(lower=1))]
            if not len(m):
                continue
            m['y'] = pd.to_numeric(m.YEAR, errors='coerce').fillna(0).astype(int)
            for (par, tech), g in m.groupby(['PARAMETER', 'TECHNOLOGY']):
                ys = g.y[g.y > 0]
                y0, y1 = (int(ys.min()), int(ys.max())) if len(ys) else (0, 0)
                mx = float(g.d[g._merge == 'both'].max()) if (g._merge == 'both').any() else 1e9
                onesided = int((g._merge != 'both').sum())
                rs = reason(c, stage, s, par, tech, y0, y1, mx if not onesided else 1e9)
                # split a policy key that differs both in history and later years
                if s != 'BAU' and rs == 'D2 history 2018-2024' and y1 > 2024:
                    rs = 'D2 history; also from 2025'
                rec = dict(country=c, stage=stage[:2], scenario=s, parameter=par, technology=tech, years=f'{y0}-{y1}',
                           n=len(g), one_sided=onesided, max_abs=mx, reason=rs)
                out.append(rec)
                if rs in ('unexplained', 'D2 history; also from 2025', 'D2 row (check from 2025)'):
                    unex.append(rec)
O = pd.DataFrame(out)
old = pd.read_csv(JOB + '/recompile_diff_summary.csv') if os.path.exists(JOB + '/recompile_diff_summary.csv') else pd.DataFrame()
if len(old):
    old = old[~old.country.isin(countries)]
O = pd.concat([old, O], ignore_index=True)
O.to_csv(JOB + '/recompile_diff_summary.csv', index=False, lineterminator='\n')
U = O[O.reason.isin(['unexplained', 'D2 history; also from 2025', 'D2 row (check from 2025)'])]
U.to_csv(JOB + '/logs/recompile_diff_unexplained.csv', index=False, lineterminator='\n')
print(O[O.country.isin(countries)].groupby(['country', 'reason']).size().to_string())
pd.set_option('display.width', 250)
print(U[U.country.isin(countries)].head(60).to_string())
