"""Phase A: assemble proposals.csv (R1 to R7) from the per-rule calculations.

Inputs (job folder): scripts/r4r5_cells.csv, scripts/r6_changes.csv, scripts/r1_values.json,
scripts/r3_volumes.json, and the base A-O index pickle (argv[1]).
Output: proposals.csv (one row per cell or line to write).
Run: py -I scripts/phaseA_build.py <ao_index.pkl>
"""
import json, os, sys
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

JOB = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z/'
ROOT = 'C:/clw_fix/'
idx = pd.read_pickle(sys.argv[1])
AO = {
    'CostaRica': 'CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx',
    'DominicanRepublic': 'DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
    'Ecuador': 'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx',
    'Guatemala': 'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
    'Honduras': 'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
    'Jamaica': 'Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
}
CPI = {2010: 218.056, 2018: 251.107, 2019: 255.657, 2020: 258.811, 2021: 270.970, 2022: 292.655, 2023: 304.702,
       2024: 313.689, 2025: 321.943}
_hdr_cache = {}


def year_col(country, sheet, year):
    k = (country, sheet)
    if k not in _hdr_cache:
        wb = openpyxl.load_workbook(ROOT + AO[country], read_only=True)
        ws = wb[sheet]
        row1 = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
        _hdr_cache[k] = {(int(v) if isinstance(v, float) else v): i + 1 for i, v in enumerate(row1) if v is not None}
        wb.close()
    return get_column_letter(_hdr_cache[k][year])


def ao_row(country, tech, par):
    w = idx[(idx.country == country) & (idx.tech == tech) & (idx.parameter == par)]
    assert len(w) == 1, (country, tech, par, len(w))
    return w.iloc[0]


P = []


def add(**kw):
    base = dict(country='', workbook='', sheet='', row='', column='', Tech='', Parameter='', year='', current_value='',
                new_value='', rule='', source_ids='', derivation='', assumption='', kind='ao_cell')
    base.update(kw)
    P.append(base)


STATED = {
    2018: '2018 US dollars as stated in the 2018 Jamaica IRP (p.107 BESS costs; p.147 present worth in 2018 dollars)',
    2019: '2019 USD as stated for ATB 2021 values in the derivation',
    2020: '2020 USD (PEG 2020-2050 PDF p.8 "dolares de 2020"; CCG kit values in 2020 USD)',
    2021: '2021 USD',
    2022: '2022 USD',
    2023: '2023 prices',
    2024: '2024 USD',
    2025: '2025 USD',
    2010: 'January 1, 2010 price levels (OUR Generation Expansion Plan 2010); CPI-U annual average 2010 used',
}
WHERE = {
    'PEN': ('CSD-008', None), 'PEIG': ('NAT-001', None), 'PLANMICC': ('PMC-008', None),
}

# ---------------- R4 and R5 ----------------
c45 = pd.read_csv(JOB + 'scripts/r4r5_cells.csv')
c45 = c45[c45.changes == True]
ASSUME_KEYS = {
    ('DominicanRepublic', 2021): 'PEN', ('Guatemala', 2025): 'PEIG', ('Ecuador', 2023): 'PLANMICC',
}
ASSUME_TXT = {
    'PEN': ("PEN 2022-2036 (CSD-008) states no currency year for Tablas 220, 223 and 229 (the tables say only "
            "'Fuente: Comision Nacional de Energia, 2021'); the plan was published in 2022 (PDF created 2022-08-05)"),
    'PEIG': ("PEIG 2026-2050 (NAT-001) states no currency year for Tabla 6 (its only year reference is the 2024 exchange rate); "
             "the plan was published in January 2026 (PDF created 2026-01-12)"),
    'PLANMICC': ("the PLANMICC compiled cost files and cost workbook (PMC-001 to PMC-003, PMC-008) state no currency year; "
                 "the repository version used was published on 2024-09-24"),
}
for _, r in c45.iterrows():
    w = ao_row(r.country, r.tech, r.parameter)
    yr = int(r.year)
    first = min(y for y in w.index if isinstance(y, int) and pd.notna(w.get(y))) if w['mode'] == 'Flat' else None
    if w['mode'] == 'Flat' and pd.isna(r.wb_value) and yr != first:
        continue  # Flat row: A2 reads the first year column; empty cells stay empty
    cy = int(r.currency_year)
    key = None
    if r.rule.startswith('R4'):
        if r.country == 'DominicanRepublic' and 'PEN' in str(r.derivation_src) and cy == 2021:
            key = 'PEN'
        elif r.country == 'Guatemala' and cy == 2025:
            key = 'PEIG'
        elif r.country == 'Ecuador' and cy == 2023:
            key = 'PLANMICC'
    fac = CPI[2024] / CPI[cy]
    if str(r.note).startswith('mixed'):
        der = f"{r.note} = {r.new_value:.6f} (real 2024 USD); parts as in the original derivation: {str(r.derivation_src)[:220]}"
    elif cy == 2024:
        der = f"source value {r.source_value:.6f} already in 2024 USD; written over the old value kept inside the sourced path; {str(r.derivation_src)[:220]}"
    else:
        der = (f"source value {r.source_value:.6f} ({STATED.get(cy, str(cy) + ' USD')}) x CPI-U 2024/{cy} = {CPI[2024]}/{CPI[cy]} = {fac:.6f} "
               f"-> {r.new_value:.6f} real 2024 USD; {r.note}; value from: {str(r.derivation_src)[:220]}")
    ass = ''
    if key:
        why = ASSUME_TXT[key]
        ass = (f"ASSUMPTION: the values of {r.tech} {r.parameter} are in {cy} USD, the year before the source was published, "
               f"and are converted to real 2024 USD with CPI-U 2024/{cy} = {fac:.6f}. Reason: {why}; a plan normally states "
               f"costs in the prices of the year its work was done, which is the year before publication.")
    srcs = [s for s in str(r.source_ids).split(';') if s and s != 'nan'] + ['BEN-004']
    if 'ATB 2024' in str(r.derivation_src): srcs.append('FXR-002')
    if 'ATB 2023' in str(r.derivation_src): srcs.append('FXR-001')
    add(country=r.country, workbook=AO[r.country], sheet=r.sheet, row=int(r.row), column=year_col(r.country, r.sheet, yr),
        Tech=r.tech, Parameter=r.parameter, year=yr, current_value=r.wb_value, new_value=r.new_value, rule=r.rule,
        source_ids=';'.join(dict.fromkeys(srcs)), derivation=der, assumption=ass)

# R5: three Ecuador hydro rows matched to CCG large hydro (PWRHYD001) without currency conversion
v = 2939 * CPI[2024] / CPI[2020]
for t in ['PPHDAMAM', 'PPHDAMPM', 'PPHRORAB']:
    w = ao_row('Ecuador', t, 'CapitalCost')
    add(country='Ecuador', workbook=AO['Ecuador'], sheet=w.sheet, row=int(w['row']), column=year_col('Ecuador', w.sheet, 2021),
        Tech=t, Parameter='CapitalCost', year=2021, current_value=w[2021], new_value=v, rule='R5',
        source_ids='CCG-002;CCG-001;BEN-004',
        derivation=(f"CCG Ecuador kit v1.0 (doi:10.5281/zenodo.5498094) sheet Parameters row 19792 PWRHYD001 Large Hydropower Plant (Dam) (>100MW) "
                    f"CapitalCost 2939 (2020 USD, flat 2021 to 2050) x CPI-U 2024/2020 = {CPI[2024]}/{CPI[2020]} = {CPI[2024]/CPI[2020]:.6f} -> {v:.6f}; "
                    f"the Ecuador job maps big and medium hydro to CCG large hydro; the old 3500 equals CCG small hydro PWRHYD003 3499 (2020 USD, row 19794) "
                    f"without conversion. Flat row: A2 copies 2021 to every year."))

# ---------------- R2 ----------------
CRCFG = 'CostaRica/CR_ENERGY/t1_confection/B1_Scenario_Config.xlsx'
for rr, sc in [(47, 'BAU'), (48, 'LTSNEW'), (49, 'NDCNEW'), (119, 'LTSOPT')]:
    add(country='CostaRica', workbook=CRCFG, sheet='Efficiency', row=rr, column='M', Tech='E5INDCOA', Parameter='SpecifiedAnnualDemand',
        year=2021, current_value=0.675, new_value=0.00667, rule='R2', source_ids='CRC-006', kind='config_cell',
        derivation=(f"{sc} row, Method Exact: 2021 industry coal demand set to 0.00667 PJ, the value of the following years; MINAE Balance "
                    "Energetico Nacional 2022 PDF p.40 Tabla 3 Consumo por sector industrial de hidrocarburos: Carbon Mineral 6.67 TJ = 0.00667 PJ; "
                    "decision of 11 November 2026 (brief R2)."))

# ---------------- R6 ----------------
r6 = pd.read_csv(JOB + 'scripts/r6_changes.csv')
r6 = r6[~((r6.country == 'Jamaica') & (r6.set == 'PPHROR') & (r6.parameter == 'TotalAnnualMaxCapacity'))]
for _, r in r6.iterrows():
    if r.kind == 'electrical_list':
        der = (f"{r.scenario} row: history years up to 2024 set to what BAU ends up with in B1_Output_Params "
               f"(divided by the row's Security_Multiplier); years from 2025 on keep the values the row already gave them "
               f"(the crossing segment is anchored year by year)")
    else:
        der = f"{r.scenario} row, Method Exact: history year {r.header} set to the BAU value in B1_Output_Params"
    add(country=r.country, workbook=r.file, sheet=r.sheet, row=int(r.row), column=r.column, Tech=r.set, Parameter=r.parameter,
        year=r.header if r.kind == 'year_column' else '2018-2024', current_value=r.old, new_value=r.new, rule='R6',
        source_ids='', derivation=der, kind='config_cell')

# ---------------- R7 ----------------
JAM = AO['Jamaica']
sched = {2027: 0.0129, 2028: 0.0071, 2029: 0.0111, 2031: 0.0021, 2032: 0.0011}
w = ao_row('Jamaica', 'PPHROR', 'TotalAnnualMinCapacityInvestment')
for y in sorted(set(list(sched) + [y for y in range(2021, 2056) if isinstance(w.get(y), (int, float)) and pd.notna(w.get(y)) and w.get(y) != 0])):
    nv = sched.get(y, 0.0)
    if abs((w.get(y) or 0) - nv) < 1e-12: continue
    add(country='Jamaica', workbook=JAM, sheet=w.sheet, row=int(w['row']), column=year_col('Jamaica', w.sheet, y), Tech='PPHROR',
        Parameter='TotalAnnualMinCapacityInvestment', year=y, current_value=w.get(y), new_value=nv, rule='R7', source_ids='JAMF-01',
        derivation=("2022 Jamaica IRP (IRP-2): 34.3 MW of small hydro, 12 plants, 2027 to 2033 (Table ES-4 p15, Table 11-2 p62); period totals "
                    "Table ES-6 p19: 31.12 MW in 2026-2030 and 3.18 MW in 2031-2035; years from Table 11-5 p66 (2027 12.7, 2028 7, 2029 11, 2031 2, "
                    "2032 1 MW); each period total split in the Table 11-5 proportions on a 0.1 MW grid (A2 rounds to 0.0001 GW): "
                    "31.1 = 12.9 + 7.1 + 11.1, 3.2 = 2.1 + 1.1, total 34.3 MW"))
cum, run = {}, 0.0
for y in range(2021, 2056):
    run = round(run + sched.get(y, 0.0), 4)
    cum[y] = run
w = ao_row('Jamaica', 'PPHROR', 'TotalAnnualMaxCapacity')
add(country='Jamaica', workbook=JAM, sheet=w.sheet, row=int(w['row']), column='G', Tech='PPHROR', Parameter='TotalAnnualMaxCapacity',
    year='mode', current_value=w['mode'], new_value='User defined', rule='R7', source_ids='JAMF-01', kind='ao_mode',
    derivation='row switched from EMPTY to User defined so A2 writes the cap')
for y in range(2021, 2056):
    add(country='Jamaica', workbook=JAM, sheet=w.sheet, row=int(w['row']), column=year_col('Jamaica', w.sheet, y), Tech='PPHROR',
        Parameter='TotalAnnualMaxCapacity', year=y, current_value=w.get(y), new_value=cum[y], rule='R7', source_ids='JAMF-01;JAMF-06;JAMF-07;JAMF-09;JAMF-12',
        derivation=(f"cap = PPHROR residual capacity 0 + cumulative IRP-2 small hydro additions to {y} = {cum[y]:.4f} GW; no new hydro plant observed "
                    "in 2024 to 2026 (JPS Annual Reports 2024 and 2025, MSETT Jamaica Energy Statistics 2025, IRENA Renewable Capacity Statistics 2026: "
                    "hydro capacity about 29 to 30 MW every year)"))
JCFG = 'Jamaica/JAM_ENERGY/B1_Scenario_Config.xlsx'
years = list(range(2021, 2055))
ey = ' ; '.join(str(y) for y in years)
evs = ' ; '.join(repr(cum[y] / 1.01) for y in years)
for rr, sc in [(29, 'NDCNEW'), (59, 'LTSNEW')]:
    for col, hdr, old, new in [('G', 'Exact_Years', '2021', ey), ('H', 'Exact_Values', '99', evs), ('K', 'Milestone_Value', '99.1', repr(cum[2055] / 1.01))]:
        add(country='Jamaica', workbook=JCFG, sheet='Electrical', row=rr, column=col, Tech='PPHROR', Parameter='TotalAnnualMaxCapacity',
            year=hdr, current_value=old, new_value=new, rule='R7', source_ids='JAMF-01', kind='config_cell',
            derivation=(f"{sc} Write row for PPHROR TotalAnnualMaxCapacity (Security_Multiplier 1.01) set to the same IRP-2 cumulative cap as the "
                        "A-O row, divided by 1.01, so all three scenarios carry the cap (it was 99 GW x 1.01)"))
S2 = '_STAGE2_INPUTS/STAGE2_OVERWRITES_Jamaica.csv'
lines = open(ROOT + S2, encoding='utf-8', newline='').read().splitlines()
for i, ln in enumerate(lines, start=1):
    parts = ln.split(',')
    if len(parts) >= 5 and parts[0] == 'Jamaica' and parts[3] in ('2025', '2026') and parts[2] in ('PPHROR', 'PPHDAM'):
        if parts[2] == 'PPHROR':
            new = f"Jamaica,{parts[1]},PPHROR,{parts[3]},0.0,Existing run-of-river plants are held in PPHDAM residual capacity (29.1 MW); PPHROR has no residual capacity and the IRP-2 small hydro starts in 2027 (LAC_FIX_RUN R7)."
        else:
            new = (f"Jamaica,{parts[1]},PPHDAM,{parts[3]},{float(parts[4]) + 1.8:.1f},Frozen at 2024. Existing hydro fleet (Maggotty and the run-of-river plants, "
                   "29.1 MW residual capacity in PPHDAM): 0.7 Maggotty plus 1.8 run-of-river moved from PPHROR (LAC_FIX_RUN R7).")
        add(country='Jamaica', workbook=S2, sheet='', row=i, column='', Tech=parts[2], Parameter='New_Share_Pct', year=int(parts[3]),
            current_value=parts[4], new_value=new.split(',')[4], rule='R7', source_ids='JAMF-01;JAMF-04;JAMF-06', kind='csv_line',
            derivation=f"line {i} '{ln}' -> '{new}'")

# ---------------- R1 and R3 (from research results) ----------------
for fname in ['r1_values.json', 'r3_volumes.json']:
    p = JOB + 'scripts/' + fname
    if os.path.exists(p):
        for d in json.load(open(p, encoding='utf-8')):
            add(**d)
    else:
        print('missing', fname)

o = pd.DataFrame(P)
o.to_csv(JOB + 'proposals.csv', index=False, lineterminator='\n')
print(len(o)); print(o.groupby(['rule', 'country', 'kind']).size().to_string())
