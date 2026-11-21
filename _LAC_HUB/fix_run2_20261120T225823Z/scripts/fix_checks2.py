"""DS2: Phase D gates by values (brief section 6, DS2). Writes fix_checks.csv and fix_checks_detail.csv, and fills the
'after' columns of history_builds.csv. Reads _STAGE3_RESULTS/stage3_results.xlsx (new) and the base snapshot's copy.
Run: py -I scripts/fix_checks2.py <stage2_test_log>"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import openpyxl
import pandas as pd

ROOT = 'C:/clw_fix/'
BASE = 'C:/clw_base_4ba69d6/'
JOB = ROOT + '_LAC_HUB/fix_run2_20261120T225823Z'
S2LOG = sys.argv[1] if len(sys.argv) > 1 else None
SC = ['BAU', 'NDCNEW', 'LTSNEW']
M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
     'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
     'Jamaica': 'Jamaica/JAM_ENERGY'}
new = pd.read_excel(ROOT + '_STAGE3_RESULTS/stage3_results.xlsx', sheet_name=None)
old = pd.read_excel(BASE + '_STAGE3_RESULTS/stage3_results.xlsx', sheet_name=None)
act, cap = new['TotalTechnologyAnnualActivity'], new['NewCapacity']
oact, ocap = old['TotalTechnologyAnnualActivity'], old['NewCapacity']
wb = openpyxl.load_workbook(ROOT + '_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx', read_only=True)
tm = list(wb['TECH_MAP'].iter_rows(values_only=True))
HY = {}
for r in tm[1:]:
    if r and r[3] and str(r[3]).upper() == 'HYDRO':
        HY.setdefault(r[1] if len(r) > 1 else None, set()).add(r[0])
hydro = set().union(*HY.values()) if HY else {'PPHDAM', 'PPHROR'}
checks, detail = [], []


def chk(name, country, ok, count='', note=''):
    checks.append(dict(check=name, country=country, result=ok if isinstance(ok, str) else ('pass' if ok else 'FAIL'),
                       count=count, note=note))


ispp = lambda s: s.astype(str).str.upper().str.match(r'^(PP|PWR)')
# 1 history: power-plant activity per tech identical through 2024
for c, g in act[ispp(act.Technology)].groupby('Country'):
    h = g[g.Year <= 2024].pivot_table(index=['Technology', 'Year'], columns='Scenario', values='Value', aggfunc='sum').fillna(0.0)
    cols = [s for s in SC if s in h]
    h['spread'] = h[cols].max(axis=1) - h[cols].min(axis=1)
    bad = h[h.spread > 0.05]
    for (t, y), r in bad.iterrows():
        detail.append(dict(check='history_pp_activity', country=c, item=t, year=y, value=round(r.spread, 4),
                           note=' / '.join(f'{s} {r.get(s, 0):.3f}' for s in SC)))
    chk('history: power-plant activity per technology through 2024 identical across scenarios (0.05 PJ)', c, bad.empty, len(bad),
        f'max spread {h.spread.max():.4f} PJ')
# 1b final demand per fuel through 2024 (B1 SpecifiedAnnualDemand)
for c, p in M.items():
    ds = {}
    for s in SC:
        d = pd.read_csv(f'{ROOT}{p}/B1_Output_Params/{s}/SpecifiedAnnualDemand.csv')
        d = d[d.YEAR <= 2024]
        ds[s] = d.groupby(['FUEL', 'YEAR']).Value.sum()
    D = pd.DataFrame(ds).fillna(0.0)
    sp = (D.max(axis=1) - D.min(axis=1))
    bad = sp[sp > 0.05]
    for (f, y), v in bad.items():
        detail.append(dict(check='history_final_demand', country=c, item=f, year=y, value=round(v, 4), note=''))
    chk('history: final demand per fuel through 2024 identical across scenarios (0.05 PJ)', c, bad.empty, len(bad),
        f'max spread {sp.max():.5f} PJ')
# Stage 2 log: T11a
if S2LOG:
    txt = open(S2LOG, encoding='utf-8', errors='replace').read()
    for t in ['T11a', 'T9', 'T8']:
        m = [x for x in txt.splitlines() if t in x][:3]
        chk(f'Stage 2 test {t} (log lines)', 'all', 'info', '', ' | '.join(m)[:400])
# 2 history builds
hb = pd.read_csv(JOB + '/history_builds.csv', dtype=str, keep_default_na=False)
nb = cap[ispp(cap.Technology) & cap.Year.between(2021, 2024)]
agg = nb.groupby(['Country', 'Technology', 'Scenario']).Value.sum()
seen = set()
rows = []
for (c, t), g in nb.groupby(['Country', 'Technology']):
    seen.add((c, t))
for _, r in hb.iterrows():
    seen.add((r.country, r.tech))
for c, t in sorted(seen):
    a = {s: float(agg.get((c, t, s), 0.0)) for s in SC}
    m = hb[(hb.country == c) & (hb.tech == t)]
    src = m.sourced_commissioning_gw.iloc[0] if len(m) else ''
    if src != '':
        tol = max(0.05 * float(src), 0.002)
        ok = all(abs(a[s] - float(src)) <= tol for s in SC)
        status = 'matches sourced commissioning' if ok else 'does not match sourced commissioning'
    else:
        ok = all(a[s] <= 0.002 for s in SC)
        status = 'no build above 2 MW' if ok else 'no sourced commissioning recorded'
    rows.append(dict(country=c, tech=t, after_BAU=round(a['BAU'], 4), after_NDCNEW=round(a['NDCNEW'], 4),
                     after_LTSNEW=round(a['LTSNEW'], 4), sourced=src, status_after=status, ok=ok))
R = pd.DataFrame(rows)
hb2 = hb.merge(R[['country', 'tech', 'after_BAU', 'after_NDCNEW', 'after_LTSNEW', 'status_after']], on=['country', 'tech'],
               how='outer', suffixes=('_x', ''))
for k in ('after_BAU', 'after_NDCNEW', 'after_LTSNEW'):
    if k + '_x' in hb2:
        hb2 = hb2.drop(columns=k + '_x')
hb2.to_csv(JOB + '/history_builds.csv', index=False, lineterminator='\n')
for c, g in R.groupby('country'):
    chk('history builds: power-plant new capacity 2021-2024 matches history_builds.csv (5 percent or 2 MW)', c, bool(g.ok.all()),
        int((~g.ok).sum()), '; '.join(f'{r.tech} {r.after_BAU}/{r.after_NDCNEW}/{r.after_LTSNEW}' for r in g[~g.ok].itertuples())[:600])
pphd = cap[(cap.Country == 'Ecuador') & (cap.Technology == 'PPHD')].Value.sum()
chk('Ecuador PPHD new capacity 0 in every year and scenario', 'Ecuador', pphd <= 1e-9, '', f'sum {pphd:.6f} GW')
# 3 Ecuador crude
e = act[act.Country == 'Ecuador']
iar, dem = {}, {}
for s in SC:
    d = pd.read_csv(f'{ROOT}Ecuador/ECU_Energy/B1_Output_Params/{s}/InputActivityRatio.csv')
    for t in ['PROCRU', 'T5CRUEXP', 'REF_DSL', 'REF_GSL', 'REF_LPG', 'REF_FOI', 'REF_JET', 'PPCRU']:
        x = d[(d.TECHNOLOGY == t) & (d.FUEL.isin(['E0CRU', 'E1CRU']))]
        iar[(s, t)] = x.groupby('YEAR').Value.max().to_dict()
props = pd.read_csv(JOB + '/proposals_parts/ecu_crude.csv')
T = {}
for _, r in props[props.Tech.str.startswith('REF_') & props.Parameter.str.contains('Upper')].iterrows():
    m = re.search(r'= ([0-9.]+) PJ; k', r.derivation)
    if m:
        T[int(r.year)] = float(m.group(1))
nbad, worst, impflag = 0, 0, 0
for s in SC:
    g = e[e.Scenario == s].pivot_table(index='Year', columns='Technology', values='Value', aggfunc='sum').fillna(0.0)
    for y in g.index:
        gy = g.loc[y]
        ext, imp = gy.get('EXTT_CRU', 0.0), gy.get('DIST_CRU', 0.0)
        ref_in = gy.get('PROCRU', 0.0) * iar[(s, 'PROCRU')].get(y, 1.0)
        exp_ = gy.get('T5CRUEXP', 0.0) * iar[(s, 'T5CRUEXP')].get(y, 1.0)
        refuse = sum(gy.get(t, 0.0) * iar[(s, t)].get(y, 1.0) for t in ['REF_DSL', 'REF_GSL', 'REF_LPG', 'REF_FOI', 'REF_JET'])
        bal = ext + imp - ref_in - exp_
        worst = max(worst, abs(bal))
        if abs(bal) > 0.5:
            nbad += 1
        if imp > 0.01 * ext:
            impflag += 1
        if abs(bal) > 0.5 or imp > 0.01 * ext or y in (2021, 2024, 2025, 2026, 2030, 2031, 2035, 2040, 2050):
            detail.append(dict(check='ecuador_crude', country='Ecuador', item=s, year=int(y), value=round(bal, 3),
                               note=f'extraction {ext:.2f}, imports {imp:.2f}{" (above 1 percent of production)" if imp > 0.01 * ext else ""}, '
                                    f'PROCRU input {ref_in:.2f}, exports {exp_:.2f}, REF crude use {refuse:.2f} vs T {T.get(int(y), float("nan")):.2f} PJ'))
chk('Ecuador crude: extraction + imports - (PROCRU input + exports) within 0.5 PJ, every year and scenario', 'Ecuador', nbad == 0, nbad,
    f'largest |imbalance| {worst:.3f} PJ')
chk('Ecuador crude imports above 1 percent of production (reported, flagged to GAPS)', 'Ecuador', 'info', impflag, '')
# 4 Jamaica
j = cap[(cap.Country == 'Jamaica') & (cap.Technology == 'PPHROR')]
for s in SC:
    x = j[j.Scenario == s]
    tot, early = x.Value.sum(), x[x.Year.between(2024, 2026)].Value.sum()
    chk('Jamaica PPHROR new capacity at most 34.4 MW over the horizon, none in 2024-2026', f'Jamaica {s}',
        tot <= 0.0344 + 1e-6 and early <= 1e-6, '', f'total {tot * 1000:.2f} MW; 2024-2026 {early * 1000:.2f} MW; ' +
        ', '.join(f'{int(y)} {v * 1000:.2f}' for y, v in zip(x.Year, x.Value) if v > 1e-7))
for c in ('Jamaica', 'Guatemala'):
    h = act[(act.Country == c) & act.Technology.isin(hydro)].groupby(['Scenario', 'Year']).Value.sum().unstack(0)
    sp = (h.max(axis=1) - h.min(axis=1))
    for y, v in sp[sp > 0.05].items():
        detail.append(dict(check=f'{c.lower()}_hydro_spread', country=c, item='hydro', year=int(y), value=round(v, 4),
                           note=' / '.join(f'{s} {h.loc[y].get(s, 0):.3f}' for s in SC)))
    chk(f'{c} hydro output identical across scenarios in every year (0.05 PJ)', c, sp.max() <= 0.05, int((sp > 0.05).sum()),
        f'max spread {sp.max():.4f} PJ')
# 5 D13: power-plant new capacity per country before and after
for c in M:
    a = cap[(cap.Country == c) & ispp(cap.Technology)].groupby('Scenario').Value.sum()
    b = ocap[(ocap.Country == c) & ispp(ocap.Technology)].groupby('Scenario').Value.sum()
    chk('D13: power-plant new capacity over the horizon, before -> after (GW)', c, 'info', '',
        '; '.join(f'{s} {b.get(s, 0):.3f} -> {a.get(s, 0):.3f} ({(a.get(s, 0) / b.get(s, 1) - 1) * 100:+.2f} percent)' for s in SC))
# 6 Ecuador grid new capacity and undiscounted capital
cc = {}
for s in SC:
    d = pd.read_csv(f'{ROOT}Ecuador/ECU_Energy/B1_Output_Params/{s}/CapitalCost.csv')
    od = pd.read_csv(f'{BASE}Ecuador/ECU_Energy/B1_Output_Params/{s}/CapitalCost.csv')
    for t in ('ELE_TRANS', 'ELE_DIST'):
        cc[('new', s, t)] = d[d.TECHNOLOGY == t].set_index('YEAR').Value.to_dict()
        cc[('old', s, t)] = od[od.TECHNOLOGY == t].set_index('YEAR').Value.to_dict()
for t in ('ELE_TRANS', 'ELE_DIST'):
    for s in SC:
        xn = cap[(cap.Country == 'Ecuador') & (cap.Technology == t) & (cap.Scenario == s)].set_index('Year').Value
        xo = ocap[(ocap.Country == 'Ecuador') & (ocap.Technology == t) & (ocap.Scenario == s)].set_index('Year').Value
        kn = sum(v * cc[('new', s, t)].get(y, 0) for y, v in xn.items())
        ko = sum(v * cc[('old', s, t)].get(y, 0) for y, v in xo.items())
        chk(f'Ecuador {t} new capacity 2021-2050 and undiscounted capital, before -> after', f'Ecuador {s}', 'info', '',
            f'capacity {xo.sum():.1f} -> {xn.sum():.1f}; capital {ko:,.0f} -> {kn:,.0f} MUSD')
        for y in sorted(set(xn.index) | set(xo.index)):
            detail.append(dict(check=f'ecuador_{t.lower()}_newcap', country='Ecuador', item=s, year=int(y),
                               value=round(float(xn.get(y, 0)), 4), note=f'before {float(xo.get(y, 0)):.4f}'))
# 7 hydro by country and scenario
for c, g in act[act.Technology.isin(hydro)].groupby('Country'):
    t = g[g.Year.isin([2026, 2030, 2040, 2050])].groupby(['Scenario', 'Year']).Value.sum().unstack()
    for s, r in t.iterrows():
        detail.append(dict(check='hydro_output_PJ', country=c, item=s, year='2026/2030/2040/2050', value='',
                           note=' / '.join(f'{r.get(y, 0):.3f}' for y in [2026, 2030, 2040, 2050])))
# 8 D7a
d7 = pd.read_csv(JOB + '/proposals_parts/d7a.csv')
rev = json.load(open(JOB + '/logs/d7a_reverted.json')) if __import__('os').path.exists(JOB + '/logs/d7a_reverted.json') else []
for (c, s, r, t), g in d7.groupby(['country', 'sheet', 'row', 'Tech']):
    detail.append(dict(check='d7a_rows', country=c, item=f'{s} row {r} {t}', year='', value='0.98' if [c, s, int(r)] in rev else '0.999',
                       note='put back to 0.98' if [c, s, int(r)] in rev else 'kept at 0.999'))
chk('D7a rows kept at 0.999 / put back to 0.98', 'DR, Jamaica, Ecuador', 'info', '',
    f'{d7.groupby(["country", "sheet", "row"]).ngroups + 1 - len(rev)} at 0.999 (incl. Ecuador EXTT_CRU), {len(rev)} put back')
pd.DataFrame(checks).to_csv(JOB + '/fix_checks.csv', index=False, lineterminator='\n')
pd.DataFrame(detail).to_csv(JOB + '/fix_checks_detail.csv', index=False, lineterminator='\n')
pd.set_option('display.width', 250)
pd.set_option('display.max_colwidth', 160)
print(pd.DataFrame(checks).to_string())
