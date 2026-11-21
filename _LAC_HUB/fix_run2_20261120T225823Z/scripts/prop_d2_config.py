"""D2 (a, d, e): B1 config proposals that make NDCNEW and LTSNEW history (2018-2024) equal BAU while keeping each scenario's
4ba69d6 values from 2025. Reads the base snapshot and history_diff_before.csv. Writes proposals_parts/d2_config.csv.

Kinds:
  config_cell   : edit of an existing Electrical cell (Exact_Values string), new_value = full new string
  config_row    : new row appended to a sheet; new_value = JSON dict {header: value}
Rules:
  - transport keys (no year points in their own sheets): one Electrical Overwrite row per (scenario, parameter, tech), every
    year explicit: BAU compiled value to 2024, the scenario's own 4ba69d6 compiled value from 2025, Security_Multiplier 1.
  - BAU-only history caps (CR PWRSUG, HON TRBPUGSL): history-only Write row (BAU values to 2024, B1 default from 2025).
  - existing policy rows that hold history year points (CR PWRBMS / PWRHYDROR 2021; DR PPDBGS / PPDBIM / PPDHYD lower limits):
    their history elements take the BAU value (DR: BAU after D7a, upper x 0.999 rounded as A2 rounds, 4 decimals).
  - Jamaica T5DSLTRO / T5GSLTRO emission factors: SmartGrid Exact_Multiplier rows for NDCNEW and LTSNEW, BAU multipliers to 2024,
    1 from 2025 (the scenarios have no multiplier row at 4ba69d6).
"""
import os, sys, json, collections
import openpyxl
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB
from common_props import BASEDIR, write_part

M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
     'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
     'Jamaica': 'Jamaica/JAM_ENERGY'}
POL = ['NDCNEW', 'LTSNEW']
DEFAULT = {'TotalAnnualMaxCapacity': 99999.0, 'TotalTechnologyAnnualActivityLowerLimit': 0.0}
rows = []


def num(x):
    return f'{x:.10g}'


def compiled(c, scen, par):
    f = f'{BASEDIR}/{M[c]}/B1_Output_Params/{scen}/{par}.csv'
    d = pd.read_csv(f, dtype={'Value': float}, keep_default_na=False)
    return d


def series(d, tech):
    x = d[d.TECHNOLOGY == tech]
    assert x.YEAR.is_unique, ('not one block', tech, len(x))
    return dict(zip(x.YEAR.astype(int), x.Value.astype(float)))


def electrical_header(c):
    wb = openpyxl.load_workbook(f'{BASEDIR}/{M[c]}/B1_Scenario_Config.xlsx', read_only=True)
    ws = wb['Electrical']
    h = [x for x in next(ws.iter_rows(values_only=True))]
    n = sum(1 for r in ws.iter_rows(values_only=True) if r[0] is not None)
    return h, n


hd = pd.read_csv(JOB + '/history_diff_before.csv')
big = hd[(hd.absd > 0.00005) & (hd.presence == 'both')]
TRANSPORT = big[big.parameter.isin(['TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityLowerLimit']) &
                big.technology.str.match(r'^(TRN|TR|Techs_)')]
keys = TRANSPORT.groupby(['country', 'scenario', 'parameter', 'technology']).size().reset_index()
appended = collections.Counter()
for _, k in keys.iterrows():
    c, s, p, t = k.country, k.scenario, k.parameter, k.technology
    b = series(compiled(c, 'BAU', p), t)
    o = series(compiled(c, s, p), t)
    years = sorted(o)
    assert years == list(range(years[0], years[-1] + 1)), (c, s, p, t, years[:3])
    vals = [b[y] if y <= 2024 else o[y] for y in years]
    h, n = electrical_header(c)
    rec = {x: None for x in h if x is not None}
    rec.update({'Scenario': s, 'Parameter': p, 'Tech_Set': t,
                'Description Parameter-Set': 'History 2018-2024 equal to BAU (decision D2); own values from 2025',
                'Built-in Parameter-Set': 'YES', 'Linear': 'YES', 'Exact_Years': ' ; '.join(str(y) for y in years),
                'Exact_Values': ' ; '.join(num(v) for v in vals), 'y_ini': str(years[-1]), 'Milestone_Years': str(years[-1]),
                'Milestone_Value': num(vals[-1]), 'Unit': 'GW' if p == 'TotalAnnualMaxCapacity' else 'PJ',
                'Security_Multiplier': 1, 'Method': 'Overwrite ; Interpolate ; Fix_Last'})
    appended[c] += 1
    rows.append(dict(country=c, workbook=f'{M[c]}/B1_Scenario_Config.xlsx', sheet='Electrical', row=f'new {n + appended[c]}',
                     column='', year='2018-2050', Tech=t, Parameter=p, scenario=s, current_value='no row',
                     new_value=json.dumps(rec), kind='config_row', decision='D2a;D2e', source_ids='',
                     derivation=f'BAU compiled values (B1_Output_Params/BAU at 4ba69d6) for {years[0]}-2024, {s} compiled values '
                                f'at 4ba69d6 from 2025; Security_Multiplier 1 so B1 writes the values as given (rounded to 4 decimals)'))
# BAU-only history caps -> history-only Write rows
for c, t in [('CostaRica', 'PWRSUG'), ('Honduras', 'TRBPUGSL')]:
    p = 'TotalAnnualMaxCapacity'
    b = series(compiled(c, 'BAU', p), t)
    for s in POL:
        o = compiled(c, s, p)
        assert t not in set(o.TECHNOLOGY), (c, s, t)
        years = sorted(b)
        vals = [b[y] if y <= 2024 else DEFAULT[p] for y in years]
        h, n = electrical_header(c)
        rec = {x: None for x in h if x is not None}
        rec.update({'Scenario': s, 'Parameter': p, 'Tech_Set': t,
                    'Description Parameter-Set': 'History 2018-2024 cap equal to BAU (decision D2); B1 default from 2025',
                    'Built-in Parameter-Set': 'NO', 'Linear': 'YES', 'Exact_Years': ' ; '.join(str(y) for y in years),
                    'Exact_Values': ' ; '.join(num(v) for v in vals), 'y_ini': str(years[-1]), 'Milestone_Years': str(years[-1]),
                    'Milestone_Value': num(vals[-1]), 'Unit': 'GW', 'Security_Multiplier': 1,
                    'Method': 'Write ; Interpolate ; Fix_Last'})
        appended[c] += 1
        rows.append(dict(country=c, workbook=f'{M[c]}/B1_Scenario_Config.xlsx', sheet='Electrical', row=f'new {n + appended[c]}',
                         column='', year='2018-2050', Tech=t, Parameter=p, scenario=s, current_value='no row (B1 default 99999)',
                         new_value=json.dumps(rec), kind='config_row', decision='D2a;D2e', source_ids='',
                         derivation=f'BAU compiled cap {sorted(set(b[y] for y in years if y <= 2024))} for {years[0]}-2024; B1 default '
                                    f'99999 from 2025 (the scenario had no row, so its compiled value was the default)'))


def cfg_rows(c):
    wb = openpyxl.load_workbook(f'{BASEDIR}/{M[c]}/B1_Scenario_Config.xlsx', read_only=True)
    return list(wb['Electrical'].iter_rows(values_only=True))


def edit_history(c, r, tech, par, scen, newhist, note):
    R = cfg_rows(c)
    h = R[0]
    hi = {x: i for i, x in enumerate(h) if x is not None}
    v = R[r - 1]
    assert v[hi['Scenario']] == scen and v[hi['Tech_Set']] == tech and v[hi['Parameter']] == par, (c, r, v[:3])
    ys = [int(x) for x in str(v[hi['Exact_Years']]).split(';')]
    xs = [x.strip() for x in str(v[hi['Exact_Values']]).split(';')]
    while xs and xs[-1] == '':
        xs.pop()
    assert len(ys) == len(xs), (c, r, len(ys), len(xs))
    old = list(xs)
    for i, y in enumerate(ys):
        if y in newhist:
            xs[i] = num(newhist[y])
    if xs == old:
        return
    col = openpyxl.utils.get_column_letter(hi['Exact_Values'] + 1)
    rows.append(dict(country=c, workbook=f'{M[c]}/B1_Scenario_Config.xlsx', sheet='Electrical', row=r, column=col,
                     year=';'.join(str(y) for y in sorted(newhist)), Tech=tech, Parameter=par, scenario=scen,
                     current_value=str(v[hi['Exact_Values']]), new_value=' ; '.join(xs), kind='config_cell',
                     decision='D2a;D2d', source_ids='', derivation=note))


# Costa Rica 2021 elements (rows 47, 52, 56, 61)
for r, t, s in [(47, 'PWRBMS', 'NDCNEW'), (52, 'PWRHYDROR', 'NDCNEW'), (56, 'PWRBMS', 'LTSNEW'), (61, 'PWRHYDROR', 'LTSNEW')]:
    b = series(compiled('CostaRica', 'BAU', 'TotalTechnologyAnnualActivityLowerLimit'), t)
    edit_history('CostaRica', r, t, 'TotalTechnologyAnnualActivityLowerLimit', s, {2021: b[2021]},
                 f'2021 element takes the BAU compiled value {b[2021]} (2022-2024 already equal BAU); reachable after D13')
# Dominican Republic distributed lower limits: BAU after D7a = A-O upper x 0.999, rounded to 4 decimals as A2 rounds
wv = openpyxl.load_workbook(f'{BASEDIR}/{M["DominicanRepublic"]}/A1_Outputs/A-O_Parametrization.xlsx', data_only=True)


def ao_upper(sheet, r, tech):
    ws = wv[sheet]
    hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
    assert ws.cell(r, hdr['Tech']).value == tech and ws.cell(r, hdr['Parameter']).value == 'TotalTechnologyAnnualActivityUpperLimit'
    out, last = {}, None
    for y in range(2018, 2025):
        v = ws.cell(r, hdr[y]).value
        last = v if v is not None else last      # Flat rows hold only the first year
        out[y] = float(last)
    return out


DRU = {'PPDHYD': ao_upper('Primary Techs', 227, 'PPDHYD'), 'PPDBGS': ao_upper('Secondary Techs', 167, 'PPDBGS'),
       'PPDBIM': ao_upper('Secondary Techs', 227, 'PPDBIM')}
# PPDBIM (rows 24, 82) keeps its 4ba69d6 history: Phase C repair C1-1 (BAU history needs about 10.8 MW at the row's capacity
# factors, above the scenarios' 10.1 MW cap from 2025; no sourced value removes the conflict; see GAPS)
for r, t, s in [(23, 'PPDBGS', 'LTSNEW'), (25, 'PPDHYD', 'LTSNEW'),
                (81, 'PPDBGS', 'NDCNEW'), (83, 'PPDHYD', 'NDCNEW')]:
    nh = {y: round(DRU[t][y] * 0.999, 4) for y in range(2018, 2025)}
    edit_history('DominicanRepublic', r, t, 'TotalTechnologyAnnualActivityLowerLimit', s, nh,
                 'history elements 2018-2024 take the BAU value after D7a: A-O activity upper limit x 0.999, rounded to 4 decimals '
                 'as A2 rounds (to be checked against the recompiled BAU in Phase C)')
# Jamaica SmartGrid multiplier rows
wb = openpyxl.load_workbook(f'{BASEDIR}/{M["Jamaica"]}/B1_Scenario_Config.xlsx', read_only=True)
SG = list(wb['SmartGrid'].iter_rows(values_only=True))
nsg = sum(1 for r in SG if r[0] is not None)
hsg = SG[0]
add = 0
for rbau, t in [(13, 'T5DSLTRO'), (14, 'T5GSLTRO')]:
    v = SG[rbau - 1]
    assert v[0] == 'BAU' and v[2] == t, v[:3]
    for s in POL:
        rec = {}
        for i, x in enumerate(hsg):
            if x is None:
                continue
            rec[str(x)] = v[i]
        rec['Scenario'] = s
        for i, x in enumerate(hsg):
            if str(x).isdigit() and int(x) >= 2025:
                rec[str(x)] = 1
        add += 1
        rows.append(dict(country='Jamaica', workbook=f'{M["Jamaica"]}/B1_Scenario_Config.xlsx', sheet='SmartGrid',
                         row=f'new {nsg + add}', column='', year='2021-2050', Tech=t, Parameter='EmissionActivityRatio',
                         scenario=s, current_value='no row', new_value=json.dumps(rec, default=str), kind='config_row',
                         decision='D2a', source_ids='',
                         derivation=f'copy of BAU SmartGrid row {rbau} (Exact_Multiplier) with multiplier 1 from 2025, so 2021-2024 '
                                    f'equal BAU and later years keep the unmultiplied A2 value'))
write_part('d2_config', rows)
print(collections.Counter((r['country'], r['kind'], r['scenario']) for r in rows))
