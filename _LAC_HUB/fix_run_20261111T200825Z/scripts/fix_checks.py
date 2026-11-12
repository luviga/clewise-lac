"""Phase D gates by values (brief D2). Writes fix_checks.csv and fix_checks_detail.csv.

Reads _STAGE3_RESULTS/stage3_results.xlsx (activity, new capacity), the controller TECH_MAP (hydro group),
the Stage 2 test log (T9, T11a), the Stage 3 data files (*_FINAL_0) for Costa Rica E5INDCOA demand,
and the B1 InputActivityRatio of PROCRU and T5CRUEXP for the Ecuador crude balance.
Run: py -I scripts/fix_checks.py <stage2_test_log>
"""
import re, sys
from pathlib import Path
import pandas as pd
import openpyxl

ROOT = Path(r'C:\clw_fix')
JOB = ROOT / '_LAC_HUB' / 'fix_run_20261111T200825Z'
S2LOG = Path(sys.argv[1]) if len(sys.argv) > 1 else None
SC = ['BAU', 'NDCNEW', 'LTSNEW']
res = pd.read_excel(ROOT / '_STAGE3_RESULTS' / 'stage3_results.xlsx', sheet_name=None)
act, newcap = res['TotalTechnologyAnnualActivity'], res['NewCapacity']
wb = openpyxl.load_workbook(ROOT / '_STAGE2_OUTPUT' / 'CONTROLLER_NEW_SCENARIOS.xlsx', read_only=True)
tm = list(wb['TECH_MAP'].iter_rows(values_only=True))
hydro = {r[0] for r in tm[1:] if r[2] and str(r[2]).upper() == 'HYDRO'}
checks, detail = [], []

# 1. history: PP/PWR activity identical across scenarios through 2024
pp = act[act.Technology.str.upper().str.startswith(('PP', 'PWR'))]
for c, g in pp.groupby('Country'):
    h = g[g.Year <= 2024].pivot_table(index=['Technology', 'Year'], columns='Scenario', values='Value', aggfunc='sum').fillna(0.0)
    h['spread'] = h[[s for s in SC if s in h]].max(axis=1) - h[[s for s in SC if s in h]].min(axis=1)
    bad = h[h.spread > 0.05]
    for (t, y), r in bad.iterrows():
        detail.append(dict(check='history_pp_activity', country=c, item=t, year=y, value=round(r.spread, 4),
                           note=' / '.join(f'{s} {r.get(s, 0):.3f}' for s in SC)))
    tot = g[g.Year <= 2024].groupby(['Year', 'Scenario']).Value.sum().unstack()
    checks.append(dict(check='history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ', country=c,
                       result='pass' if bad.empty else 'FAIL', count=len(bad),
                       note=f'max spread {h.spread.max():.4f} PJ; total PP activity spread max {(tot.max(axis=1) - tot.min(axis=1)).max():.4f} PJ'))

# Stage 2 test log: T9 and T11a
if S2LOG and S2LOG.exists():
    txt = S2LOG.read_text(encoding='utf-8', errors='replace')
    for t in ['T9_hydro_pj_freeze', 'T11a_denom_alignment']:
        m = re.search(t + r'.*', txt)
        checks.append(dict(check=f'Stage 2 test {t}', country='all', result=('pass' if m and 'PASS' in m.group(0) else 'FAIL'), count='',
                           note=m.group(0)[:200] if m else 'not found in log'))
    t9j = len(re.findall(r'Jamaica/[A-Z]+ \d{4}: [0-9.]+ > boundary', txt))
    checks.append(dict(check='Stage 2 T9 violations printed for Jamaica (first lines of the log only)', country='Jamaica', result='info', count=t9j, note=''))

# 2. Ecuador crude balance
e = act[act.Country == 'Ecuador']
iar = {}
for sc in SC:
    d = pd.read_csv(ROOT / 'Ecuador/ECU_Energy/B1_Output_Params' / sc / 'InputActivityRatio.csv')
    d = d[(d.FUEL == 'E0CRU')]
    for t in ['PROCRU', 'T5CRUEXP']:
        x = d[d.TECHNOLOGY == t]
        iar[(sc, t)] = dict(zip(x.YEAR, x.Value)) if len(x) else {}
dem = {}
for sc in SC:
    d = pd.read_csv(ROOT / 'Ecuador/ECU_Energy/B1_Output_Params' / sc / 'SpecifiedAnnualDemand.csv')
    d = d[d.FUEL == 'E5EXPCRU']
    dem[sc] = dict(zip(d.YEAR.astype(int), d.Value))
worst = 0
for sc in SC:
    g = e[e.Scenario == sc].pivot_table(index='Year', columns='Technology', values='Value', aggfunc='sum').fillna(0.0)
    for y in g.index:
        ext = g.loc[y].get('EXTT_CRU', 0.0); imp = g.loc[y].get('DIST_CRU', 0.0)
        ref = g.loc[y].get('PROCRU', 0.0) * iar[(sc, 'PROCRU')].get(y, 1.0)
        exp_ = g.loc[y].get('T5CRUEXP', 0.0) * iar[(sc, 'T5CRUEXP')].get(y, 1.0)
        bal = ext + imp - ref - exp_
        worst = max(worst, bal)
        if bal > 0.5 or y in (2021, 2022, 2024, 2030, 2035, 2040, 2050):
            detail.append(dict(check='ecuador_crude_balance', country='Ecuador', item=sc, year=int(y), value=round(bal, 3),
                               note=f'extraction {ext:.2f}, imports {imp:.2f}, refinery {ref:.2f}, exports {exp_:.2f} PJ (export demand {dem[sc].get(int(y), 0.0):.2f})' + (' ABOVE 0.5' if bal > 0.5 else '')))
nbad = sum(1 for d in detail if d['check'] == 'ecuador_crude_balance' and d['value'] > 0.5)
checks.append(dict(check='Ecuador crude surplus (extraction + imports - refinery - exports) at most 0.5 PJ, every year and scenario', country='Ecuador',
                   result='pass' if nbad == 0 else 'FAIL', count=nbad, note=f'largest surplus {worst:.3f} PJ'))

# 3. Jamaica PPHROR
j = newcap[(newcap.Country == 'Jamaica') & (newcap.Technology == 'PPHROR')]
for sc in SC:
    s = j[j.Scenario == sc]
    tot = s.Value.sum(); early = s[s.Year.between(2024, 2026)].Value.sum()
    checks.append(dict(check='Jamaica PPHROR new capacity over the horizon at most 0.0343 GW, none in 2024 to 2026', country=f'Jamaica {sc}',
                       result='pass' if tot <= 0.0343 + 1e-4 and early <= 1e-6 else 'FAIL', count='',
                       note=f'total {tot*1000:.2f} MW; 2024-2026 {early*1000:.2f} MW; by year ' + ', '.join(f'{int(y)} {v*1000:.2f}' for y, v in zip(s.Year, s.Value) if v > 1e-7)))
jh = act[(act.Country == 'Jamaica') & (act.Technology.isin(hydro | {'PPHROR', 'PPHDAM'}))].groupby(['Scenario', 'Year']).Value.sum().unstack(0)
spread = (jh.max(axis=1) - jh.min(axis=1)).max()
checks.append(dict(check='Jamaica hydro output identical across scenarios (0.05 PJ)', country='Jamaica', result='pass' if spread <= 0.05 else 'FAIL',
                   count='', note=f'max spread {spread:.4f} PJ'))

# 4. Costa Rica E5INDCOA 2021 (config 0.00667; B1 rounds Efficiency rows to 4 decimals, so the data file holds 0.0067)
sys.path.insert(0, str(JOB / 'scripts'))
from dat_compare import parse_dat  # noqa: E402
for sc in SC:
    f = ROOT / 'CostaRica/CR_ENERGY/t1_confection/Executables' / f'{sc}_FINAL_0' / f'{sc}_FINAL_0.txt'
    val = None
    if f.exists():
        _, P_, _ = parse_dat(f)
        val = next((v for k, v in P_.get('SpecifiedAnnualDemand', {}).items() if 'E5INDCOA' in k and k[-1] == '2021'), None)
    ok = val is not None and abs(float(val) - 0.00667) <= 5e-5
    checks.append(dict(check='Costa Rica E5INDCOA 2021 demand 0.00667 PJ (config; B1 rounds to 4 decimals)', country=f'CostaRica {sc}',
                       result='pass' if ok else 'FAIL', count='', note=f'Stage 3 data file value {val}'))

# 5. hydro output by country and scenario
for c, g in act[act.Technology.isin(hydro)].groupby('Country'):
    t = g[g.Year.isin([2026, 2030, 2040, 2050])].groupby(['Scenario', 'Year']).Value.sum().unstack()
    for sc, r in t.iterrows():
        detail.append(dict(check='hydro_output_PJ', country=c, item=sc, year='2026/2030/2040/2050', value='',
                           note=' / '.join(f'{r.get(y, 0):.3f}' for y in [2026, 2030, 2040, 2050])))
pd.DataFrame(checks).to_csv(JOB / 'fix_checks.csv', index=False, lineterminator='\n')
pd.DataFrame(detail).to_csv(JOB / 'fix_checks_detail.csv', index=False, lineterminator='\n')
print(pd.DataFrame(checks).to_string())
