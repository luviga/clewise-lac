import pandas as pd, re
W = 'cost_write_run_20261111T071733Z/'
c = pd.read_csv(W+'currency_conversion.csv')
m = c.left.fillna('').str.contains('not stated|mixed|ambiguous|2025 USD|2010|PEIG 2026-2050')
g = c[m].copy()
ws = pd.read_csv(W+'write_set.csv', low_memory=False)
p = pd.read_csv('cost_review_20261111T015203Z/proposals_all.csv', low_memory=False)
out = []
for _, r in g.iterrows():
    s = ws[(ws.country==r.country)&(ws.tech==r.tech)&(ws.parameter==r.parameter)]
    pp = p[(p.country==r.country)&(p.Tech==r.tech)&(p.Parameter==r.parameter)]
    src = ';'.join(sorted(set(';'.join(s.source_ids.dropna().astype(str)).split(';'))))
    der = pp.derivation.dropna().astype(str).unique()
    out.append(dict(country=r.country, tech=r.tech, parameter=r.parameter, n_ws=len(s), years=f"{s.year.min()}-{s.year.max()}" if len(s) else '',
        fuel=';'.join(sorted(s.fuel_scenario.dropna().astype(str).unique())), rules=';'.join(sorted(s.rule.dropna().unique())),
        src=src, left=r.left, ws_vals=f"{s.value_to_write.min():.4g}..{s.value_to_write.max():.4g}" if len(s) else '', n_der=len(der), der0=der[0][:400] if len(der) else ''))
o = pd.DataFrame(out)
o.to_csv('fix_run_20261111T200825Z/scripts/r4_groups_scratch.csv', index=False)
pd.set_option('display.width', 300); pd.set_option('display.max_colwidth', 400)
for k, gg in o.groupby('country'):
    print('=====', k)
    for _, r in gg.iterrows():
        print(r.tech, r.parameter, r.n_ws, r.years, r.fuel, r.rules, '|', r.src, '|', r.ws_vals, '| nder', r.n_der)
        print('    ', r.der0[:300])
        print('    LEFT:', r.left[:200])
