"""R3 Ecuador crude: build scripts/r3_volumes.json (proposal rows) from scripts/r3_inputs.json.

r3_inputs.json holds the sourced annual volumes in barrels:
  {"production_bbl": {year: bbl}, "exports_bbl": {year: bbl}, "production_src": "...", "exports_src": "...",
   "production_ids": "...", "exports_ids": "...", "latest_observed_year": 2025, "pending": true/false}
Rules (brief R3): exports stay a demand (E5EXPCRU); EXTT_CRU upper = production path (never above the latest
observed year), lower = 0.98 x upper (the existing 2 percent band); DIST_CRU lower 0, upper unchanged;
EXTT_CRU VariableCost = the current DIST_CRU path; T5CRUEXP VariableCost = minus that path (new Demand Techs row);
DIST_CRU VariableCost = Brent real 2024 USD per GJ on the WEO 2025 STEPS path.
Run: py -I scripts/r3_build.py <ao_index.pkl>
"""
import json, sys
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

JOB = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z/'
ROOT = 'C:/clw_fix/'
idx = pd.read_pickle(sys.argv[1])
inp = json.load(open(JOB + 'scripts/r3_inputs.json', encoding='utf-8'))
ECU = 'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx'
DEM = 'Ecuador/ECU_Energy/A1_Outputs/A-O_Demand.xlsx'
GJ_BBL = 42.3 / 7.32
CPI = {2018: 251.107, 2019: 255.657, 2020: 258.811, 2021: 270.970, 2022: 292.655, 2023: 304.702, 2024: 313.689, 2025: 321.943}
BRENT = {2018: 71.34, 2019: 64.30, 2020: 41.96, 2021: 70.86, 2022: 100.93, 2023: 82.49, 2024: 80.52, 2025: 69.14}
YEARS = list(range(2021, 2051))


def weo(y):
    if y <= 2035:
        return 79 + (80 - 79) * (y - 2024) / 11
    return 80 + (76 - 80) * (y - 2035) / 15


def row(t, p):
    w = idx[(idx.country == 'Ecuador') & (idx.tech == t) & (idx.parameter == p)]
    assert len(w) == 1, (t, p)
    return w.iloc[0]


wb = openpyxl.load_workbook(ROOT + ECU, read_only=True)
hdr = {}
for sh in ['Primary Techs', 'Demand Techs']:
    r1 = next(wb[sh].iter_rows(min_row=1, max_row=1, values_only=True))
    hdr[sh] = {(int(v) if isinstance(v, float) else v): get_column_letter(i + 1) for i, v in enumerate(r1) if v is not None}
wb.close()
out = []


def add(**kw):
    base = dict(country='Ecuador', workbook=ECU, rule='R3', kind='ao_cell', assumption='')
    base.update(kw)
    out.append(base)


dc = row('DIST_CRU', 'VariableCost')
old_path = {y: float(dc[y]) for y in YEARS}
# DIST_CRU VariableCost = Brent
for y in YEARS:
    if y <= 2025:
        v = BRENT[y] * CPI[2024] / CPI[y] / GJ_BBL
        der = f"EIA Brent spot FOB annual {BRENT[y]} USD/bbl ({y} USD) x CPI-U 2024/{y} = {CPI[2024]/CPI[y]:.6f} / {GJ_BBL:.6f} GJ/bbl -> {v:.4f} real 2024 USD/GJ"
        ids = 'BEN-001;BEN-004;GEN-001;GEN-002'
    else:
        v = BRENT[2024] * weo(y) / 79 / GJ_BBL
        der = (f"Brent 2024 80.52 USD/bbl x WEO 2025 Table 2.3 STEPS IEA crude oil index {weo(y):.4f}/79 (79 in 2024, 80 in 2035, 76 in 2050, USD 2024, "
               f"linear between) / {GJ_BBL:.6f} GJ/bbl -> {v:.4f} real 2024 USD/GJ; no freight added (no freight source found)")
        ids = 'BEN-001;BEN-005;GEN-001;GEN-002'
    add(sheet='Primary Techs', row=int(dc['row']), column=hdr['Primary Techs'][y], Tech='DIST_CRU', Parameter='VariableCost', year=y,
        current_value=old_path[y], new_value=v, source_ids=ids, derivation=der + ' (IPCC crude NCV 42.3 GJ/t / UNSD 7.32 bbl/t)')
# EXTT_CRU VariableCost = old DIST_CRU path
ex = row('EXTT_CRU', 'VariableCost')
srcids = 'ECU-002;BEN-001;BEN-004;BEN-005'
for y in YEARS:
    add(sheet='Primary Techs', row=int(ex['row']), column=hdr['Primary Techs'][y], Tech='EXTT_CRU', Parameter='VariableCost', year=y,
        current_value=float(ex[y]), new_value=old_path[y], source_ids=srcids,
        derivation=(f"Ecuador crude export value (the DIST_CRU VariableCost path before this job: BCE observed export value 2021-2025, then 0.147247 x Brent on "
                    f"the WEO 2025 STEPS path) = {old_path[y]:.4f} real 2024 USD/GJ; replaces the CCG kit MINOIL value (see starter_kit_deviations.csv)"))
# T5CRUEXP VariableCost: new Demand Techs row (appended after the last row; Tech.ID formula points at the T5CRUEXP block)
NEWROW = 203
fixed = [('A', '=A95'), ('B', 'T5CRUEXP'), ('C', 'Demand Crude for Exports'), ('D', 4), ('E', 'VariableCost'), ('F', 'M US$ / PJ'),
         ('G', 'User defined'), ('H', 0)]
for col, v in fixed:
    add(sheet='Demand Techs', row=NEWROW, column=col, Tech='T5CRUEXP', Parameter='VariableCost', year='label', current_value='', new_value=v,
        source_ids='', kind='ao_newrow', derivation='new row label cell')
for y in YEARS:
    add(sheet='Demand Techs', row=NEWROW, column=hdr['Demand Techs'][y], Tech='T5CRUEXP', Parameter='VariableCost', year=y, current_value='',
        new_value=-old_path[y], source_ids=srcids, kind='ao_newrow',
        derivation=f"minus the Ecuador crude export value {old_path[y]:.4f} real 2024 USD/GJ: exports earn the export price (brief R3); row added because the Ecuador A2 compiler reads a Demand Techs VariableCost row (test compile)")
# DIST_CRU lower limit 0
lo = row('DIST_CRU', 'TotalTechnologyAnnualActivityLowerLimit')
for y in YEARS:
    if abs(float(lo[y])) > 0:
        add(sheet='Primary Techs', row=int(lo['row']), column=hdr['Primary Techs'][y], Tech='DIST_CRU', Parameter='TotalTechnologyAnnualActivityLowerLimit',
            year=y, current_value=float(lo[y]), new_value=0.0, source_ids='', derivation='crude imports lower limit 0 in every year: OSeMOSYS fills any shortfall (brief R3)')
# DIST_CRU upper limit: 0 in 2021 to 2023 in the workbook (no crude imports observed). With the sourced production
# and export volumes and the refinery's own crude input lower limit (PROCRU, 327.6 PJ in 2021 and 346.5 PJ in 2022),
# 2021 and 2022 cannot balance without imports (found at the Phase C recompile: every Ecuador solve infeasible).
# Least change: open imports in those two years only, at the 999,999 PJ the row has from 2024 (brief R3 "OSeMOSYS
# fills any shortfall"; the brief's F3 describes this row's upper limit as 999,999); 2023 balances and stays 0.
du = row('DIST_CRU', 'TotalTechnologyAnnualActivityUpperLimit')
for y in (2021, 2022):
    assert abs(float(du[y])) == 0.0, (y, du[y])
    add(sheet='Primary Techs', row=int(du['row']), column=hdr['Primary Techs'][y], Tech='DIST_CRU', Parameter='TotalTechnologyAnnualActivityUpperLimit',
        year=y, current_value=0.0, new_value=999999.0, source_ids='',
        derivation=(f"crude imports upper limit {y}: 0 -> 999,999 PJ, the value the row has from 2024, so OSeMOSYS can fill the shortfall (brief R3); "
                    f"with the sourced production upper limit and export demand, the refinery crude input lower limit (PROCRU) cannot be met in {y} "
                    f"without imports (all Ecuador solves infeasible at the Phase C recompile)"),
        assumption=(f"ASSUMPTION: crude imports may fill a shortfall in {y} because the refinery input lower limit of the model is about 9 PJ (2021) "
                    f"and 8 PJ (2022) above sourced production minus sourced exports; the refinery limit itself is outside the scope of this job."))
# volumes
if not inp.get('pending'):
    prod = {int(k): v for k, v in inp['production_bbl'].items()}
    exp_ = {int(k): v for k, v in inp['exports_bbl'].items()}
    last = inp['latest_observed_year']
    cap = prod[last]
    up, lw = row('EXTT_CRU', 'TotalTechnologyAnnualActivityUpperLimit'), row('EXTT_CRU', 'TotalTechnologyAnnualActivityLowerLimit')
    for y in sorted(prod):
        bbl = min(prod[y], cap) if y > last else prod[y]
        pj = bbl * GJ_BBL / 1e6
        d_up = f"Ecuador crude production {bbl:,.0f} bbl in {y} ({inp['production_note'].get(str(y), inp['production_src'])}) x {GJ_BBL:.6f} GJ/bbl = {pj:.4f} PJ"
        add(sheet='Primary Techs', row=int(up['row']), column=hdr['Primary Techs'][y], Tech='EXTT_CRU', Parameter='TotalTechnologyAnnualActivityUpperLimit',
            year=y, current_value=float(up[y]), new_value=pj, source_ids=inp['production_ids'] + ';GEN-001;GEN-002', derivation=d_up + '; never above the latest observed year')
        add(sheet='Primary Techs', row=int(lw['row']), column=hdr['Primary Techs'][y], Tech='EXTT_CRU', Parameter='TotalTechnologyAnnualActivityLowerLimit',
            year=y, current_value=float(lw[y]), new_value=0.98 * pj, source_ids=inp['production_ids'] + ';GEN-001;GEN-002',
            derivation=d_up + ' x 0.98 (the 2 percent band between the lower and upper limits the row already had)')
    dwb = openpyxl.load_workbook(ROOT + DEM, read_only=True, data_only=True)
    ws = dwb['Demand_Projection']
    r1 = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    dh = {(int(v) if isinstance(v, float) else v): get_column_letter(i + 1) for i, v in enumerate(r1) if v is not None}
    r58 = next(ws.iter_rows(min_row=58, max_row=58, values_only=True))
    assert r58[1] == 'E5EXPCRU'
    di = {(int(v) if isinstance(v, float) else v): i for i, v in enumerate(r1) if v is not None}
    for y in YEARS:
        if y not in exp_: continue
        pj = exp_[y] * GJ_BBL / 1e6
        add(workbook=DEM, sheet='Demand_Projection', row=58, column=dh[y], Tech='E5EXPCRU', Parameter='SpecifiedAnnualDemand', year=y,
            current_value=r58[di[y]], new_value=pj, source_ids=inp['exports_ids'] + ';GEN-001;GEN-002', kind='demand_cell',
            derivation=f"Ecuador crude exports {exp_[y]:,.0f} bbl in {y} ({inp['exports_note'].get(str(y), inp['exports_src'])}) x {GJ_BBL:.6f} GJ/bbl = {pj:.4f} PJ")
json.dump(out, open(JOB + 'scripts/r3_volumes.json', 'w', encoding='utf-8'), indent=1, default=float)
print(len(out), pd.DataFrame(out).groupby(['Tech', 'Parameter', 'kind']).size().to_string())
