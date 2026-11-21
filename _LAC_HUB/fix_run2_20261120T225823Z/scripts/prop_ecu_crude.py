"""D-ECU1, D-ECU2, D7a (EXTT_CRU band): proposals for the Ecuador crude chain, built from the base
snapshot and the downloaded BCE and MDEP files. Writes proposals_parts/ecu_crude.csv.
Before use: create the base snapshot (scripts/make_base_snapshot.sh), run, and check the printed T check against F1."""
import os, sys, collections
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EARLIER
from common_props import BASEDIR, write_part, col_letter

AO = 'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx'
DEM = 'Ecuador/ECU_Energy/A1_Outputs/A-O_Demand.xlsx'
NCV = 42.3 / 7.32            # GJ per bbl: IPCC crude NCV 42.3 GJ/t (GEN-002) over UNSD 7.32 bbl/t (GEN-001)
BAND = 0.999                 # D7a; revert to 0.98 only if a solve fails
YEARS = list(range(2021, 2051))

wb = openpyxl.load_workbook(EARLIER + '/downloads/ecu/SerieCifrasPetroleras.xlsx', data_only=True)
ws = wb[wb.sheetnames[0]]
yr = None
cols = []
for c in range(3, ws.max_column + 1):
    y = ws.cell(2, c).value
    m = ws.cell(3, c).value
    if isinstance(y, (int, float)):
        yr = int(y)
    if isinstance(m, str) and m.strip().lower()[:3] in ('ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'):
        cols.append((c, yr))


def annual(row):
    t = collections.defaultdict(float)
    n = collections.Counter()
    for c, y in cols:
        v = ws.cell(row, c).value
        if isinstance(v, (int, float)):
            t[y] += v
            n[y] += 1
    return {y: t[y] / 1000.0 for y in t if n[y] == 12}      # million bbl, full years only


prod_obs = annual(5)      # field production, sheet Petroleo row 5
proc_obs = annual(51)     # processed in refineries, row 51
PROD_OUT = {2026: 168.3, 2027: 169.0, 2028: 171.3, 2029: 173.9, 2030: 174.7}      # ECUF-03 Tabla 2
LOAD_OUT = {2026: 47.0, 2027: 54.0, 2028: 59.0, 2029: 59.0, 2030: 59.0}          # ECUF-06 Anexo 3 (PDF p.93)


def prod_pj(y):
    return (prod_obs[y] if y <= 2025 else PROD_OUT[min(y, 2030)]) * NCV


def target_pj(y):
    return (proc_obs[y] if y <= 2025 else LOAD_OUT[min(y, 2030)]) * NCV


A_HOLD = ('ASSUMPTION: crude production, crude exports and refinery runs from 2031 to 2050 hold their 2030 values (field '
          'production 174.7 million bbl, 1,009.5 PJ). The BCE Programacion Macroeconomica 2026-2030 ends in 2030 and no national '
          'outlook covers later years; holding 2030 keeps the 2030 balance of production, exports and refining.')
A_BAND = ('ASSUMPTION: the lower activity limit is 0.999 times the sourced output, a 0.1 percent band that keeps the solve '
          'feasible against rounding; a band of 2 percent would let output fall up to 2 percent below the sourced value.')

wf = openpyxl.load_workbook(f'{BASEDIR}/{AO}')
rows = []


def cell(sheet, r, y):
    return wf[sheet].cell(r, 9 + (y - 2021))


def add(sheet, r, y, tech, par, new, dec, src, der, assum=''):
    c = cell(sheet, r, y)
    cur = c.value
    assert wf[sheet].cell(r, 2).value == tech and wf[sheet].cell(r, 5).value == par, (sheet, r, tech, par)
    assert wf[sheet].cell(1, 9 + (y - 2021)).value == y
    if cur is not None and not isinstance(cur, str) and abs(float(cur) - new) <= 1e-9 * max(1.0, abs(new)):
        return
    rows.append(dict(country='Ecuador', workbook=AO, sheet=sheet, row=r, column=col_letter(9 + (y - 2021)), year=y, Tech=tech,
                     Parameter=par, scenario='ALL', current_value=cur, new_value=repr(float(new)), kind='ao_cell', decision=dec,
                     source_ids=src, derivation=der, assumption=assum))


UP, LO = 'TotalTechnologyAnnualActivityUpperLimit', 'TotalTechnologyAnnualActivityLowerLimit'
P, S = 'Primary Techs', 'Secondary Techs'
for y in YEARS:      # EXTT_CRU rows 387 / 388
    up = prod_pj(y)
    if y <= 2025:
        der = f'BCE field production {prod_obs[y]:.4f} million bbl ({y}, sum of 12 months, sheet Petroleo row 5) x {NCV:.6f} GJ/bbl'
        src, dec, a = 'ECUF-01;GEN-001;GEN-002', 'D-ECU2b', ''
    elif y <= 2030:
        der = f'BCE outlook field production {PROD_OUT[y]} million bbl ({y}, Tabla 2) x {NCV:.6f} GJ/bbl'
        src, dec, a = 'ECUF-03;GEN-001;GEN-002', 'D-ECU2b', ''
    else:
        der = f'2030 value held: 174.7 million bbl x {NCV:.6f} GJ/bbl'
        src, dec, a = 'ECUF-03;GEN-001;GEN-002', 'D-ECU1', A_HOLD
    add(P, 387, y, 'EXTT_CRU', UP, up, dec, src, der, a)
    add(P, 388, y, 'EXTT_CRU', LO, BAND * up, dec + ';D7a', src, f'{BAND} x upper limit ({der})', A_BAND + (' ' + a if a else ''))
for y in YEARS:      # DIST_CRU rows 137 / 138, PROCRU rows 177 / 178
    add(P, 137, y, 'DIST_CRU', UP, 999999.0, 'D-ECU2d', '', 'decision D-ECU2(d): upper limit 999,999 (not binding) in every year')
    add(P, 138, y, 'DIST_CRU', LO, 0.0, 'D-ECU2d', '', 'decision D-ECU2(d): lower limit 0 in every year')
    add(S, 177, y, 'PROCRU', UP, 999999.0, 'D-ECU2a', '', 'decision D-ECU2(a): upper limit 999,999 (not binding) in every year')
    add(S, 178, y, 'PROCRU', LO, 0.0, 'D-ECU2a', '', 'decision D-ECU2(a): lower limit 0 in every year')
REF = [('REF_DSL', 197, 198), ('REF_GSL', 207, 208), ('REF_LPG', 217, 218), ('REF_FOI', 227, 228), ('REF_JET', 237, 238)]
tcheck = []
for y in YEARS:
    cu = {t: float(cell(S, ru, y).value) for t, ru, rl in REF}
    cl = {t: float(cell(S, rl, y).value) for t, ru, rl in REF}
    tot = sum(cu.values())
    T = target_pj(y)
    k = T / tot
    tcheck.append((y, T, tot, k))
    if y <= 2025:
        tsrc, tder, dec, a = 'ECUF-01;GEN-001;GEN-002', f'BCE processed crude {proc_obs[y]:.4f} million bbl ({y}, sheet Petroleo row 51)', 'D-ECU2c', ''
    elif y <= 2030:
        tsrc, tder, dec, a = 'ECUF-06;GEN-001;GEN-002', f'MDEP-BCE Anexo 3 refinery load {LOAD_OUT[y]:.0f} million bbl ({y})', 'D-ECU2c', ''
    else:
        tsrc, tder, dec, a = 'ECUF-06;GEN-001;GEN-002', 'MDEP-BCE Anexo 3 refinery load 59 million bbl (2030), held', 'D-ECU1;D-ECU2c', A_HOLD
    for t, ru, rl in REF:
        nu = k * cu[t]
        ratio = cl[t] / cu[t]
        add(S, ru, y, t, UP, nu, dec, tsrc,
            f'T({y}) = {tder} x {NCV:.6f} GJ/bbl = {T:.4f} PJ; k = T / sum of the five REF upper limits ({tot:.4f} PJ) = {k:.6f}; new upper = k x {cu[t]:.6f}', a)
        add(S, rl, y, t, LO, nu * ratio, dec, tsrc,
            f'new upper {nu:.6f} x the lower-to-upper ratio of this row in {y} ({cl[t]:.6f} / {cu[t]:.6f} = {ratio:.6f})', a)
wd = openpyxl.load_workbook(f'{BASEDIR}/{DEM}')      # E5EXPCRU demand row 58, year columns from K (11)
wsd = wd['Demand_Projection']
assert wsd.cell(58, 2).value == 'E5EXPCRU' and wsd.cell(1, 11).value == 2021
v2030 = float(wsd.cell(58, 11 + 9).value)
for y in range(2031, 2051):
    cur = wsd.cell(58, 11 + (y - 2021)).value
    if cur is not None and abs(float(cur) - v2030) <= 1e-9 * v2030:
        continue
    rows.append(dict(country='Ecuador', workbook=DEM, sheet='Demand_Projection', row=58, column=col_letter(11 + (y - 2021)), year=y,
                     Tech='E5EXPCRU', Parameter='Demand', scenario='ALL', current_value=cur, new_value=repr(v2030), kind='demand_cell',
                     decision='D-ECU1', source_ids='ECUF-03;GEN-001;GEN-002',
                     derivation='2030 value held: BCE outlook crude exports 113.5 million bbl (Tabla 2) x 5.778689 GJ/bbl = 655.88 PJ',
                     assumption=A_HOLD))
write_part('ecu_crude', rows)
print(collections.Counter((r['Tech'], r['Parameter'][-10:]) for r in rows))
print('T check (year, T, current REF upper sum, k):')
for y, T, tot, k in tcheck:
    if y in (2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2030, 2031, 2050):
        print(y, round(T, 2), round(tot, 2), round(k, 5))
print('EXTT upper 2026-2030:', [round(prod_pj(y), 2) for y in range(2026, 2031)], 'E5EXPCRU 2030', v2030)
