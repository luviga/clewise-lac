"""C2: keyed comparison of the recompiled A2 and B1 outputs (and B1 data files) with c42ae07.

Baseline: the tracked A2_Output_Params and B1_Output_Params at c42ae07 (copied before the recompile to
<base_dir>) and the c42ae07 B1 data files left by LAC_OVERNIGHT_COST_RUN in C:\\clw_overnight (read only).
Allowed differences (brief C2): parameters and technologies of proposals.csv; Costa Rica SpecifiedAnnualDemand
E5INDCOA 2021; Ecuador E5EXPCRU demand, EXTT_CRU and DIST_CRU limits and costs, T5CRUEXP VariableCost; Jamaica
PPHROR rows; the R6 history changes in 2018 to 2024 of NDCNEW and LTSNEW.
Writes recompile_diff_summary.csv and recompile_diff_rows.csv (not-allowed rows and a sample of allowed ones).
Run: py -I scripts/phaseC_compare.py <base_dir>
"""
import csv, sys
from collections import Counter
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dat_compare import compare_dat  # noqa: E402
from keyed_compare import compare_dirs  # noqa: E402

ROOT = Path(r'C:\clw_fix')
JOB = ROOT / '_LAC_HUB' / 'fix_run_20261111T200825Z'
BASE = Path(sys.argv[1])
OVR = Path(r'C:\clw_overnight')
M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY', 'Ecuador': 'Ecuador/ECU_Energy',
     'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY', 'Jamaica': 'Jamaica/JAM_ENERGY'}
SCENS = ['BAU', 'NDCNEW', 'LTSNEW']
COST = {'CapitalCost', 'FixedCost', 'VariableCost'}
P = pd.read_csv(JOB / 'proposals.csv', dtype=str, keep_default_na=False)
cost_keys = {(r.country, r.Tech, r.Parameter) for r in P.itertuples() if r.Parameter in COST}
r6 = P[P.rule == 'R6']
r6_keys = {(r.country, r.Parameter, r.Tech) for r in r6.itertuples()}
ECU_T = {'EXTT_CRU', 'DIST_CRU', 'T5CRUEXP'}
LIM = {'TotalTechnologyAnnualActivityUpperLimit', 'TotalTechnologyAnnualActivityLowerLimit'}


def allowed(country, scen, param, tech, fuel, year):
    y = int(year) if str(year).isdigit() else None
    if param in COST and (country, tech, param) in cost_keys:
        return 'proposal cost cell (R1, R3, R4, R5)'
    if country == 'DominicanRepublic' and param == 'FixedCost' and tech in ('ELE_TRANS', 'ELE_DIST'):
        return 'dependent formula of the R1 cell (Secondary Techs J233 and J253 = J232 x 0.5 percent)'
    if country == 'CostaRica' and param == 'SpecifiedAnnualDemand' and fuel == 'E5INDCOA' and y == 2021:
        return 'R2 E5INDCOA 2021'
    if country == 'Ecuador' and (fuel == 'E5EXPCRU' or (tech in ECU_T and (param in LIM or param in COST))):
        return 'R3 Ecuador crude'
    if country == 'Jamaica' and tech == 'PPHROR':
        return 'R7 Jamaica PPHROR'
    if scen in ('NDCNEW', 'LTSNEW') and y is not None and y <= 2024 and (country, param, tech or fuel) in r6_keys:
        return 'R6 history change'
    return ''


DFLT = {}
for c, m in M.items():
    x = pd.read_excel(ROOT / m / 'B1_Default_Param.xlsx')
    DFLT[c] = dict(zip(x.iloc[:, 0], x.iloc[:, 1]))


def allowed_r6_tail(country, scen, param, tech, year, kind, a, b):
    """R6 rows added in Phase C: from 2025 they carry the B1 default (no effect) or B1's 4-decimal rounding."""
    y = int(year) if str(year).isdigit() else None
    if scen not in ('NDCNEW', 'LTSNEW') or y is None or y < 2025 or (country, param, tech) not in r6_keys:
        return ''
    if kind == 'only_b':
        try:
            if abs(float(b) - float(DFLT[country].get(param))) < 1e-9:
                return 'R6 history-only row: B1 default from 2025 (no effect)'
        except (TypeError, ValueError):
            return ''
    if param == 'EmissionActivityRatio' and kind == 'value':
        if abs(float(a) - float(b)) <= 5e-5 + 1e-12:
            return 'R6 emission-factor row: B1 rounds the row to 4 decimals (change from 2025 at most 0.00005)'
    return ''


rows, summary = [], Counter()
for c, m in M.items():
    for stage in ('A2_Output_Params', 'B1_Output_Params'):
        for sc in SCENS:
            for d in compare_dirs(BASE / m / stage / sc, ROOT / m / stage / sc):
                param = d['file'].replace('.csv', '')
                kp = dict(zip(d.get('key_columns', '').split('|'), d['key'].split('|'))) if d['key'] else {}
                why = allowed(c, sc, param, kp.get('TECHNOLOGY', ''), kp.get('FUEL', ''), kp.get('YEAR', ''))
                if not why:
                    why = allowed_r6_tail(c, sc, param, kp.get('TECHNOLOGY', ''), kp.get('YEAR', ''), d['kind'], d['a'], d['b'])
                summary[(c, stage.split('_')[0], sc, param, why or 'NOT ALLOWED')] += 1
                if not why or summary[(c, stage.split('_')[0], sc, param, why)] <= 3:
                    rows.append(dict(country=c, stage=stage.split('_')[0], scenario=sc, parameter=param, key=d['key'], kind=d['kind'],
                                     c42ae07=d['a'], recompiled=d['b'], allowed=why or 'NOT ALLOWED'))
    for sc in SCENS:
        a = OVR / m / 'Executables' / f'{sc}_0' / f'{sc}_0.txt'
        b = ROOT / m / 'Executables' / f'{sc}_0' / f'{sc}_0.txt'
        if not (a.exists() and b.exists()):
            summary[(c, 'B1 data file', sc, '(missing)', 'NOT ALLOWED')] += 1
            continue
        for d in compare_dat(a, b):
            param = d['param']
            parts = d['key'].split('|') if d['kind'] == 'value' else []
            tech = fuel = year = ''
            if parts:
                year = parts[-1] if parts[-1].isdigit() else ''
                for p_ in parts[1:]:
                    if p_.startswith(('E', 'D')) and param == 'SpecifiedAnnualDemand':
                        fuel = p_
                tech = parts[1] if len(parts) > 1 else ''
                if param == 'SpecifiedAnnualDemand':
                    tech = ''
                    fuel = parts[1] if len(parts) > 1 else fuel
            why = allowed(c, sc, param, tech, fuel, year)
            if not why:
                why = allowed_r6_tail(c, sc, param, tech, year, d['kind'], d['a'], d['b'])
            summary[(c, 'B1 data file', sc, param, why or 'NOT ALLOWED')] += 1
            if not why or summary[(c, 'B1 data file', sc, param, why)] <= 3:
                rows.append(dict(country=c, stage='B1 data file', scenario=sc, parameter=param, key=d['key'], kind=d['kind'],
                                 c42ae07=d['a'], recompiled=d['b'], allowed=why or 'NOT ALLOWED'))
with open(JOB / 'recompile_diff_rows.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['country', 'stage', 'scenario', 'parameter', 'key', 'kind', 'c42ae07', 'recompiled', 'allowed'], lineterminator='\n')
    w.writeheader(); w.writerows(rows)
with open(JOB / 'recompile_diff_summary.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['country', 'stage', 'scenario', 'parameter', 'allowed_reason', 'values_changed'])
    for k, n in sorted(summary.items()):
        w.writerow(list(k) + [n])
bad = {k: n for k, n in summary.items() if k[4] == 'NOT ALLOWED'}
print('differing values', sum(summary.values()), 'not allowed', sum(bad.values()))
for k, n in sorted(bad.items()):
    print('  NOT ALLOWED', k, n)
