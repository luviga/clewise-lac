"""Gates after the full run:
  frozen_output.csv     frozen plants of Stage 2 (sheet FROZEN) with the override row behind the value
  frozen_check.csv      solved generation of each frozen plant against its frozen value (Stage 2 FROZEN, PJ of the
                        boundary year), every country, scenario and year after the boundary; a row per shortfall
  history_builds_after.csv  the cases of the history builds table with the solved builds 2021-2024 of this run
  hydrogen_check.csv    solved activity of every hydrogen technology (must be 0)
Usage: python -I gates_after.py <root>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import sys
from pathlib import Path

import pandas as pd

root = Path(sys.argv[1]) if len(sys.argv) > 1 else M.ROOT
sys.path.insert(0, str(root))
import lac_tables as LT  # noqa: E402

ctrl = root / '_STAGE2_OUTPUT' / 'CONTROLLER_NEW_SCENARIOS.xlsx'
fr = pd.read_excel(ctrl, 'FROZEN')
fr = fr.replace({'\u2014': '-'}, regex=True)   # override notes are copied without em dashes
fr.to_csv(M.JOB / 'frozen_output.csv', index=False, lineterminator='\n')
fl = pd.read_excel(ctrl, 'FLOOR_LOWER')
x = pd.ExcelFile(root / '_STAGE3_RESULTS' / 'stage3_results.xlsx')
act = pd.read_excel(x, 'TotalTechnologyAnnualActivity')
nc = pd.read_excel(x, 'NewCapacity')
tol = 1e-3
rows = []
frozen = set(zip(fr.Country, fr.Scenario, fr.Tech))
years = [c for c in fl.columns if isinstance(c, (int, float))]
first = LT.controller('first_patch_year', '3')
last = LT.controller('max_year_default', '3')
n = 0
fpj = {(r.Country, r.Scenario, r.Tech): (float(r.Frozen_PJ), int(r.Boundary_Year)) for r in fr.itertuples()}
for _, d in fl.iterrows():
    k = (d['Country'], d['Scenario'], d['Tech'])
    if k not in frozen:
        continue
    a = act[(act.Country == d['Country']) & (act.Scenario == d['Scenario']) & (act.Technology == d['Tech'])]
    av = dict(zip(a.Year, a.Value))
    for y in years:
        if y <= fpj[k][1] or y < first or y > last:
            continue
        n += 1
        fv = fpj[k][0]
        sv = float(av.get(y, 0.0))
        if sv + tol < fv * 0.999:
            rows.append([d['Country'], d['Scenario'], d['Tech'], y, round(fv, 4), round(sv, 4)])
with open(M.JOB / 'frozen_check.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['country', 'scenario', 'tech', 'year', 'frozen_pj', 'solved_pj'])
    w.writerows(rows)
print('frozen check:', n, 'plant-years compared,', len(rows), 'below the frozen value')

# hydrogen
h2 = []
for c in LT.countries():
    try:
        ts = set(LT.techs('hydrogen', c))
    except KeyError:
        continue
    a = act[(act.Country == c) & act.Technology.isin(ts)]
    for r in a.itertuples():
        if abs(r.Value) > 1e-9:
            h2.append([c, r.Scenario, r.Technology, r.Year, r.Value])
with open(M.JOB / 'hydrogen_check.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['country', 'scenario', 'technology', 'year', 'activity_pj'])
    w.writerows(h2)
print('hydrogen check:', len(h2), 'non-zero activity values')

# history builds after
plan = pd.read_csv(M.JOB / 'work' / 'history_plan.csv')
hb = pd.read_csv(root / '_LAC_HUB' / 'fix_run2_20261120T225823Z' / 'history_builds.csv')
out = []
for r in hb.itertuples():
    sub = nc[(nc.Country == r.country) & (nc.Technology == r.tech) & (nc.Year.between(2021, 2024))]
    built = {s: round(float(sub[sub.Scenario == s].Value.sum()), 4) for s in LT.scenarios()}
    yrs = ';'.join(str(int(y)) for y in sorted(sub[sub.Value > 1e-6].Year.unique()))
    p = plan[(plan.country == r.country) & (plan.tech == r.tech)]
    st = p.status_expected.iloc[0] if len(p) else ''
    note = p.note.iloc[0] if len(p) and 'note' in p else ''
    src = r.sourced_commissioning_gw
    match = ''
    if pd.notna(src):
        match = 'matches sourced commissioning' if abs(built[LT.scenario('base')] - float(src)) <= max(0.005, 0.1 * float(src)) else 'does not match sourced commissioning'
    out.append(dict(country=r.country, tech=r.tech, build_years_after=yrs,
                    **{f'built_gw_2021_2024_{s}': v for s, v in built.items()},
                    sourced_commissioning_gw=src, plants_and_dates=r.plants_and_dates, source_locator=r.source_locator,
                    status_after=match or 'no sourced record', plan_status=st, note=note))
pd.DataFrame(out).to_csv(M.JOB / 'history_builds_after.csv', index=False, lineterminator='\n')
print('history builds:', pd.DataFrame(out).status_after.value_counts().to_dict())
