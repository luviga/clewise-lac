"""Register rows of step 6.1 and 6.2 (electricity imports of Guatemala and Honduras): the same IMP_ELE activity
limits in every scenario; history from sourced import records where they exist; from 2025 the lower limit is 0 and
the upper limit is the sourced interconnection import capacity. Reads the current cells (before) and writes
work/register_imports.csv in the value_register columns."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

import openpyxl

PJ_PER_GWH = 0.0036          # 1 GWh = 3.6 TJ
PJ_PER_MW_YEAR = 0.031536    # 1 MW for 8760 hours = 8.76 GWh = 0.031536 PJ
YEARS = list(range(2018, 2051))
FIELDS = ['model', 'file', 'sheet', 'tech', 'parameter', 'year', 'before', 'after', 'unit', 'source_id', 'page',
          'derivation', 'assumption_sentence', 'range_low', 'range_high']
rows = []

# ---------------- Guatemala
gua_hist = {2019: 1113, 2020: 1008, 2021: 1141, 2022: 1413, 2023: 1900}     # GWh, CNEE Compendio 2024 p.12
gua_cap_mw = 240 + 300   # Mexico-SER transfer limit (EOR 2021 p.20) + SIEPAC import limit (EOR Nov 2025 Table 12)
cap = round(gua_cap_mw * PJ_PER_MW_YEAR, 4)
cur_up = {2018: 2.2895, 2024: 6.175}     # compiled current values of the years without a record
cur_lo = {2018: 0.0, 2024: 6.175}
up = [cur_up[y] if y in cur_up else round(gua_hist[y] * PJ_PER_GWH, 4) if y in gua_hist else cap for y in YEARS]
lo = [cur_lo[y] if y in cur_lo else round(gua_hist[y] * PJ_PER_GWH, 4) if y in gua_hist else 0.0 for y in YEARS]
model, f, sh = 'Guatemala/GUA_ENERGY', 'B1_Scenario_Config.xlsx', 'Electrical'
wb = openpyxl.load_workbook(M.ROOT / model / f, read_only=True)
ws = wb[sh]
hdr = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
cur = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[2] == 'IMP_ELE':
        cur[(r[0], r[1])] = dict(zip(hdr, r))
der_up = (f"2019-2023 imports (CNEE Compendio Estadistico 2024 p.12, GWh) x {PJ_PER_GWH} PJ per GWh; from 2025 the "
          f"import capacity {gua_cap_mw} MW (Mexico-SER limit 240 MW, EOR 2021 p.20, plus SIEPAC import limit 300 MW, "
          f"EOR November 2025 Table 12) x {PJ_PER_MW_YEAR} PJ per MW-year = {cap} PJ; written without multiplier")
assum = ("ASSUMPTION: Guatemala imports in 2018 (2.2895 PJ upper limit, no lower limit) and 2024 (6.175 PJ) hold "
         "their values; CNEE records 1,113 to 1,900 GWh (4.0 to 6.8 PJ) in 2019 to 2023, so the 2024 value sits "
         "10 percent below the 2023 record.")
for sc in ['BAU', 'NDC', 'LTS']:
    for par, vec in [('TotalTechnologyAnnualActivityUpperLimit', up), ('TotalTechnologyAnnualActivityLowerLimit', lo)]:
        c = cur[(sc, par)]
        new = {'Description Parameter-Set': 'Electricity imports: sourced history; from 2025 open up to the import capacity, same in every scenario',
               'Built-in Parameter-Set': 'NO', 'Linear': 'NO',
               'Exact_Years': ' ; '.join(str(y) for y in YEARS), 'Exact_Values': ' ; '.join(f'{v:g}' for v in vec),
               'y_ini': 2050, 'Milestone_Years': 2050, 'Milestone_Value': vec[-1], 'Security_Multiplier': 1,
               'Method': 'Write ; Interpolate ; Fix_Last'}
        for col, val in new.items():
            if str(c[col]) == str(val):
                continue
            rows.append(dict(model=model, file=f, sheet=sh, tech=f'{sc}|IMP_ELE', parameter=par, year=col,
                             before=c[col], after=val, unit='PJ' if col in ('Exact_Values', 'Milestone_Value') else '',
                             source_id='ALN-CNEE-2024|ALN-EOR-MEX-2021|ALN-EOR-MCTP-2025', page='p.12; p.20; Table 12',
                             derivation=der_up if 'Upper' in par else der_up.replace('from 2025 the import capacity', 'from 2025 lower limit 0 (open to least cost); upper limit at the import capacity'),
                             assumption_sentence=assum, range_low='', range_high=''))

# ---------------- Honduras
hon_cap_mw = 280 + 140   # import from Guatemala or El Salvador (most restrictive 280 MW) + import South-North (140 MW)
hcap = round(hon_cap_mw * PJ_PER_MW_YEAR, 4)
model, f = 'Honduras/HON_ENERGY', 'A1_Outputs/A-O_Parametrization.xlsx'
wb = openpyxl.load_workbook(M.ROOT / model / f)
ws = wb['Primary Techs']
names = [str(c.value).strip() if c.value is not None else '' for c in ws[1]]
tc, pc = names.index('Tech'), names.index('Parameter')
hassum = ("ASSUMPTION: Honduras imports are limited from 2025 to 420 MW (13.2451 PJ a year): the most restrictive "
          "SIEPAC import limit from the north (280 MW from Guatemala or El Salvador; the links of one corridor do not add, as "
          "the Guatemala simultaneous export limit of 300 MW equals each single limit) plus the South-North import "
          "limit of 140 MW (EOR November 2025 Table 12). Range 280 to 700 MW.")
hist_vals = {}
for row in ws.iter_rows(min_row=2):
    if row[tc].value == 'IMP_ELE' and row[pc].value == 'TotalTechnologyAnnualActivityUpperLimit':
        for k, n in enumerate(names):
            if n.isdigit():
                y = int(n)
                v = row[k].value
                if y <= 2024:
                    hist_vals[y] = v
                elif y <= 2050 and v not in (None,) and str(v) != str(hcap):
                    rows.append(dict(model=model, file=f, sheet='Primary Techs', tech='IMP_ELE',
                                     parameter='TotalTechnologyAnnualActivityUpperLimit', year=y, before=v, after=hcap,
                                     unit='PJ', source_id='ALN-EOR-MCTP-2025', page='Table 12',
                                     derivation=f'{hon_cap_mw} MW x {PJ_PER_MW_YEAR} PJ per MW-year', assumption_sentence=hassum,
                                     range_low=round(280 * PJ_PER_MW_YEAR, 4), range_high=round(700 * PJ_PER_MW_YEAR, 4)))
wb2 = openpyxl.load_workbook(M.ROOT / model / 'B1_Scenario_Config.xlsx', read_only=True)
ws2 = wb2['Electrical']
hdr2 = [c.value for c in next(ws2.iter_rows(min_row=1, max_row=1))]
hvec = [float(hist_vals[y]) if y <= 2024 else hcap for y in YEARS]
for r in ws2.iter_rows(min_row=2, values_only=True):
    if r[2] == 'IMP_ELE':
        c = dict(zip(hdr2, r))
        new = {'Description Parameter-Set': 'Electricity imports: same limits as BAU; from 2025 the import capacity',
               'Exact_Values': ' ; '.join(f'{v:.4f}'.rstrip('0').rstrip('.') for v in hvec),
               'Milestone_Value': hcap, 'Security_Multiplier': 1}
        for col, val in new.items():
            if str(c[col]) == str(val):
                continue
            rows.append(dict(model=model, file='B1_Scenario_Config.xlsx', sheet='Electrical', tech=f'{c["Scenario"]}|IMP_ELE',
                             parameter=c['Parameter'], year=col, before=c[col], after=val,
                             unit='PJ' if col in ('Exact_Values', 'Milestone_Value') else '', source_id='ALN-EOR-MCTP-2025',
                             page='Table 12', derivation=f'history as in BAU; from 2025 {hon_cap_mw} MW x {PJ_PER_MW_YEAR} PJ per MW-year',
                             assumption_sentence=hassum, range_low='', range_high=''))
out = M.JOB / 'work' / 'register_imports.csv'
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows ->', out, '; GUA cap', cap, 'HON cap', hcap)
