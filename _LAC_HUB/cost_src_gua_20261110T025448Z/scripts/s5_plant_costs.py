"""Steps 5 and 6: plant cost proposals (rules P1 to P3) and the electricity import price (rule E1).
Values are proposed as published by each source, in that source's dollar year (no deflation), so that a
kept value and its source read the same number; the dollar year is recorded in each row.
Usage: py -I s5_plant_costs.py <clone root> <job folder>"""
import os, sys
import pandas as pd

ROOT, J = sys.argv[1], sys.argv[2]
YEARS = list(range(2018, 2051))
cur = pd.read_csv(os.path.join(J, 'cost_rows_current.csv'))
bau = {}
for p in ['CapitalCost', 'FixedCost', 'VariableCost']:
    x = pd.read_csv(os.path.join(ROOT, 'Guatemala/GUA_ENERGY/A2_Output_Params/BAU', p + '.csv'))
    for _, r in x.iterrows():
        bau[(r.TECHNOLOGY, p, int(r.YEAR))] = float(r.Value)

def current(t, p, y):
    if (t, p, y) in bau:
        return bau[(t, p, y)]
    row = cur[(cur.Tech == t) & (cur.Parameter == p)].iloc[0]
    v = row[str(y)]
    if pd.isna(v):
        v = row['2018'] if row['Projection.Mode'] in ('Flat', 'Zero') else None
    return 0.0 if v is None or pd.isna(v) else float(v)

atb = pd.read_csv(os.path.join(J, 'work', 'atb_paths.csv'))
def A(ed, tech, param, y, cls='Class5'):
    d = atb[(atb.edition == f'ATB {ed}') & (atb.technology == tech) & (atb.parameter == param) & (atb.year == y)]
    if tech in ('UtilityPV', 'CommPV', 'ResPV', 'Utility-Scale PV-Plus-Battery'):
        d = d[d.techdetail == cls]
    return float(d.value.iloc[0]) if len(d) else None
ATB_SRC = {2024: 'INT-003;INT-004', 2023: 'INT-005;INT-006', 2021: 'INT-007;INT-008'}
ATB_DY = {2024: '2022 USD', 2023: '2021 USD', 2021: '2019 USD'}
ATB_LOC = 'ATBe.csv rows scenario Moderate, core_metric_case Market, technology {t} {c}, core_metric_parameter {p}, core_metric_variable {y}'

U = {'CapitalCost': 'M US$ / GW (= USD/kW)', 'FixedCost': 'M US$ / GW per year (= USD/kW-yr)', 'VariableCost': 'M US$ / PJ (= USD/GJ)'}
MWH = 3.6  # 1 USD/GJ = 3.6 USD/MWh; USD/MWh / 3.6 = USD/GJ
rows = []

def add(t, p, y, prop, cls, chg, src, der, dy, sent=''):
    rows.append({'technology': t, 'parameter': p, 'year': y, 'current_value': round(current(t, p, y), 6), 'proposed_value': round(prop, 6),
                 'unit': U[p], 'class': cls, 'change_class': chg, 'source_ids': src, 'derivation': der, 'source_dollar_year': dy,
                 'assumption_sentence': sent})

def within(a, b, tol=0.02):
    return b not in (None, 0) and abs(a / b - 1) <= tol

def flat(t, p, prop, cls, chg, src, der, dy, sent=''):
    for y in YEARS:
        add(t, p, y, prop, cls, chg, src, der, dy, sent)

# ---------------- source values (published) ----------------
PEIG = 'NAT-001'   # MEM PEIG 2026-2050, Tabla 6 p35 (newest MEM generation plan edition)
PEG20 = 'NAT-002'  # MEM PEG 2020-2050, Tablas 4 and 5 pp41-42, 2020 USD
PEG22 = 'NAT-004'  # MEM PEIG 2022-2052, Tabla 11 pp124-125
L_PEIG = 'PEIG 2026-2050 Tabla 6 (PDF p.35), row {r}'
L_PEG20 = 'PEG 2020-2050 Tabla 4/5 (PDF pp.41-42), row {r}'
L_PEG22 = 'PEIG 2022-2052 Tabla 11 (PDF pp.124-125), row {r}'

# ---- PPBGS biogas
flat('PPBGS', 'CapitalCost', 2600, 'matched, newer edition', 'upgrade', f'{PEG20};{PEG22}',
     'current 5000 USD/kW equals ' + L_PEG20.format(r='biogas') + ' 5000 USD/kW (2020 USD); the newer edition of the same MEM plan table, '
     + L_PEG22.format(r='biogas') + ', gives 2600 USD/kW; the newest edition (PEIG 2026-2050) has no biogas candidate', '2020 USD (old); not stated (new)')
flat('PPBGS', 'FixedCost', 7.11, 'matched', 'keep', f'{PEG20};{PEG22}',
     L_PEG20.format(r='biogas') + ' 7.11 USD/kW-yr; same value in ' + L_PEG22.format(r='biogas'), '2020 USD')
flat('PPBGS', 'VariableCost', 5 / MWH, 'matched', 'unit_fix', f'{PEG20};{PEG22};INT-001',
     'current 0.005 is USD/kWh (MUSD/GWh, the unit label of the cell); ' + L_PEG20.format(r='biogas') + ' 5 USD/MWh (also IRENA 2022 p183, bioenergy 0.005 USD/kWh); 5 / 3.6 = 1.388889 USD/GJ (equal to 0.005 x 277.78)', '2020 USD')
# ---- PPBIM biomass (bagasse cogeneration)
flat('PPBIM', 'CapitalCost', 1929, 'matched', 'keep', PEIG, L_PEIG.format(r='Cogeneracion') + ' 1929 USD/kW (exact)', 'not stated (plan dated January 2026)')
flat('PPBIM', 'FixedCost', 77.16, 'matched', 'keep', PEIG, L_PEIG.format(r='Cogeneracion') + ' 77 USD/kW-yr (0.2 percent from 77.16)', 'not stated (plan dated January 2026)')
flat('PPBIM', 'VariableCost', 4 / MWH, 'replace', 'replace', 'INT-002;INT-001',
     'current 0.00965 USD/kWh (9.65 USD/MWh) matches no source within 2 percent (PEIG Cogeneracion 10 USD/MWh is 3.6 percent off); first source in P1 order: IRENA Renewable Power Generation Costs, bioenergy variable O&M 0.005 USD/kWh (2022 edition p183), newest edition 0.004 USD/kWh (2024 edition p171, 2024 USD); 4 / 3.6 = 1.111111 USD/GJ', '2024 USD')
# ---- PPCOA coal
for y in YEARS:
    add('PPCOA', 'CapitalCost', y, 2100, 'replace', 'replace', 'INT-013',
        'current 2562 USD/kW matches no source; IRENA does not cover coal and the WEO 2023 cost table needs a sign-in; WEO 2025 Annex B Table B.4b (Stated Policies, p.455), United States, Coal capital cost 2100 USD/kW in 2024, 2035 and 2050 (held flat before 2024)', '2024 USD')
flat('PPCOA', 'FixedCost', 31.6, 'replace', 'replace', PEG20,
     'current 61.4 USD/kW-yr matches no source; IRENA and WEO 2025 publish no separate fixed O&M for coal; national plan: ' + L_PEG20.format(r='carbon') + ' 31.6 USD/kW-yr (later MEM editions have no coal candidate)', '2020 USD')
flat('PPCOA', 'VariableCost', 6 / MWH, 'replace', 'replace', PEG20,
     'current 0.0064 USD/kWh (6.4 USD/MWh) matches no source within 2 percent; ' + L_PEG20.format(r='carbon') + ' 6 USD/MWh; 6 / 3.6 = 1.666667 USD/GJ', '2020 USD')
# ---- PPDSL diesel and PPFOI fuel oil (reciprocating engines)
flat('PPDSL', 'CapitalCost', 1400, 'replace', 'replace', PEIG,
     'current 448 USD/kW matches no source; IRENA and WEO 2025 do not cover oil-fired engines; national plan: ' + L_PEIG.format(r='Combustion interna') + ' 1400 USD/kW (internal combustion engine candidate, listed for gas; used for diesel engines)', 'not stated (plan dated January 2026)')
flat('PPDSL', 'FixedCost', 20, 'replace', 'replace', PEIG,
     'current 31.6 USD/kW-yr equals the coal row of PEG 2020-2050, not a diesel source; ' + L_PEIG.format(r='Combustion interna') + ' 20 USD/kW-yr', 'not stated (plan dated January 2026)')
flat('PPDSL', 'VariableCost', 5 / MWH, 'replace', 'replace', PEIG,
     'current 0.006 USD/kWh equals the coal row of PEG 2020-2050 (6 USD/MWh), not a diesel source; ' + L_PEIG.format(r='Combustion interna') + ' 5 USD/MWh; 5 / 3.6 = 1.388889 USD/GJ', 'not stated (plan dated January 2026)')
flat('PPFOI', 'CapitalCost', 1400, 'replace', 'replace', PEIG,
     'current 1908 USD/kW matches no source (EIA 2020 cost study internal combustion engines 1810, 5.4 percent off); IRENA and WEO 2025 do not cover oil-fired engines; ' + L_PEIG.format(r='Combustion interna') + ' 1400 USD/kW', 'not stated (plan dated January 2026)')
flat('PPFOI', 'FixedCost', 35.16, 'matched', 'keep', 'INT-009',
     'EIA Capital Cost and Performance Characteristic Estimates (Sargent and Lundy, February 2020), Table 2 p.28, Case 4 Internal Combustion Engines 4 x 5.6 MW, fixed O&M 35.16 USD/kW-year (2019 USD)', '2019 USD')
flat('PPFOI', 'VariableCost', 5.69 / MWH, 'matched', 'unit_fix', 'INT-009',
     'current 0.00569 is USD/kWh; EIA 2020 cost study Table 2 p.28, Case 4 Internal Combustion Engines, variable O&M 5.69 USD/MWh (2019 USD); 5.69 / 3.6 = 1.580556 USD/GJ', '2019 USD')
# ---- PPGEO geothermal
flat('PPGEO', 'CapitalCost', 4015, 'replace', 'replace', 'INT-002;INT-001',
     'current 3900 USD/kW matches no geothermal source; IRENA Renewable Power Generation Costs global weighted average total installed cost for geothermal: 3478 USD/kW (2022 edition Table H.1 p15, 2022 USD), newest edition 4015 USD/kW (2024 edition Table S1 p15, 2024 USD)', '2024 USD')
flat('PPGEO', 'FixedCost', 150.6, 'matched', 'keep', PEIG, L_PEIG.format(r='Geotermica') + ' 151 USD/kW-yr (0.3 percent from 150.6)', 'not stated (plan dated January 2026)')
flat('PPGEO', 'VariableCost', 5 / MWH, 'replace', 'replace', PEIG,
     'current 0 matches no geothermal source (EIA 2020 cost study 1.16 USD/MWh, PEIG 5 USD/MWh); IRENA states geothermal O&M as a fixed amount only and WEO 2025 combines fuel and O&M; national plan: ' + L_PEIG.format(r='Geotermica') + ' 5 USD/MWh, the same table as the matched fixed O&M; 5 / 3.6 = 1.388889 USD/GJ', 'not stated (plan dated January 2026)')
# ---- PPHDAM hydro reservoir
flat('PPHDAM', 'CapitalCost', 3500, 'matched, newer edition', 'upgrade', f'{PEG20};{PEG22};{PEIG}',
     'current 2619 USD/kW is 0.7 percent from the large hydro candidates of 2600 USD/kW in ' + L_PEG20.format(r='hidro grande') + ' and ' + L_PEG22.format(r='hidro grande')
     + '; the newest edition of the MEM plan, ' + L_PEIG.format(r='Hidro de embalse') + ', gives 3500 USD/kW (IRENA 2024 Table 6.3 p149, Central America large hydro 2018-2024: 3058 USD/kW)', 'not stated (new); 2020 USD (old)')
flat('PPHDAM', 'FixedCost', 50, 'replace', 'replace', f'{PEIG};INT-001',
     'current 33.54 USD/kW-yr matches no reservoir hydro source; IRENA gives hydropower O&M only as 2 to 2.5 percent of capital cost, regional averages 20 to 60 USD/kW-yr (2022 edition p162), not a single value; WEO 2025 has no separate O&M; national plan: '
     + L_PEIG.format(r='Hidro de embalse') + ' 50 USD/kW-yr, inside the IRENA range', 'not stated (plan dated January 2026)')
flat('PPHDAM', 'VariableCost', 0, 'matched', 'keep', 'INT-009',
     'EIA 2020 cost study Table 2 p.29, Case 17 Hydroelectric Power Plant, variable O&M 0 USD/MWh', '2019 USD')
# ---- PPHROR hydro run of river
flat('PPHROR', 'CapitalCost', 3444, 'replace', 'replace', 'INT-002;INT-001',
     'current 1870 USD/kW matches no source; IRENA Central America small hydropower weighted average total installed cost: 3244 USD/kW for 2010-2015 (2022 edition p159, 2022 USD), newest edition 3444 USD/kW for 2010-2017 (2024 edition Table 6.3 p149, 2024 USD)', '2024 USD')
flat('PPHROR', 'FixedCost', 34, 'matched, newer edition', 'upgrade', f'{PEG20};{PEG22};{PEIG}',
     'current 54 USD/kW-yr equals the small hydro (GDR) fixed O&M of ' + L_PEG20.format(r='GDR hidro') + ' and ' + L_PEG22.format(r='GDR hidro')
     + '; the newest edition, ' + L_PEIG.format(r='Hidro de pasada') + ', gives 34 USD/kW-yr', 'not stated (new); 2020 USD (old)')
flat('PPHROR', 'VariableCost', 0, 'matched', 'keep', 'INT-009',
     'EIA 2020 cost study Table 2 p.29, Case 17 Hydroelectric Power Plant, variable O&M 0 USD/MWh', '2019 USD')
# ---- PPNGS natural gas combined cycle
for y in YEARS:
    v = 1000 if y <= 2024 else (1000 + 100 * (y - 2024) / 11 if y <= 2035 else 1100)
    add('PPNGS', 'CapitalCost', y, v, 'replace', 'replace', 'INT-013',
        'current 1156 USD/kW matches no source (PEG 2020-2050 gas 1100, 4.8 percent off); IRENA does not cover gas and the WEO 2023 cost table needs a sign-in; WEO 2025 Annex B Table B.4b (Stated Policies, p.455), United States, Gas CCGT capital cost 1000 USD/kW in 2024 and 1100 in 2035 and 2050, linear between, flat before 2024', '2024 USD')
flat('PPNGS', 'FixedCost', 12.12, 'matched', 'keep', PEIG, L_PEIG.format(r='Ciclo combinado') + ' 12 USD/kW-yr (1.0 percent from 12.12)', 'not stated (plan dated January 2026)')
flat('PPNGS', 'VariableCost', 5 / MWH, 'replace', 'replace', PEIG,
     'current 0.00453 USD/kWh (4.53 USD/MWh) matches no source within 2 percent; IRENA and WEO 2025 give no separate variable O&M for gas; ' + L_PEIG.format(r='Ciclo combinado') + ' 5 USD/MWh; 5 / 3.6 = 1.388889 USD/GJ', 'not stated (plan dated January 2026)')
# ---- PPPVT utility PV (existing)
flat('PPPVT', 'CapitalCost', 1375, 'replace', 'replace', 'INT-002;INT-001',
     'current 949 USD/kW matches no source; IRENA utility-scale PV: global weighted average 876 USD/kW (2022 edition Table H.1 p15); newest edition gives Central America and the Caribbean 1375 USD/kW (2024 edition Table 3.1 p95, 2024 USD), the regional value used', '2024 USD')
flat('PPPVT', 'FixedCost', 20.23, 'matched', 'keep', PEIG, L_PEIG.format(r='Fotovoltaica') + ' 20 USD/kW-yr (1.2 percent from 20.23)', 'not stated (plan dated January 2026)')
flat('PPPVT', 'VariableCost', 0, 'matched', 'keep', 'INT-009', 'EIA 2020 cost study Table 2 p.29, Case 24 Solar PV with single axis tracking, variable O&M 0 USD/MWh', '2019 USD')
# ---- PPWNDON onshore wind
flat('PPWNDON', 'CapitalCost', 1600, 'matched, newer edition', 'upgrade', f'{PEG20};{PEIG};INT-010',
     'current 1518 USD/kW equals EIA AEO2019 electricity assumptions Table 2 p.5 wind base overnight cost 1518 (2018 USD) and is 1.2 percent from ' + L_PEG20.format(r='eolico') + ' 1500 USD/kW; the newest edition of the MEM plan, '
     + L_PEIG.format(r='Eolica') + ', gives 1600 USD/kW', 'not stated (new); 2018 USD (old)')
flat('PPWNDON', 'FixedCost', 28.08, 'matched', 'keep', PEIG, L_PEIG.format(r='Eolica') + ' 28 USD/kW-yr (0.3 percent from 28.08)', 'not stated (plan dated January 2026)')
flat('PPWNDON', 'VariableCost', 0, 'matched', 'keep', 'INT-009', 'EIA 2020 cost study Table 2 p.29, Cases 20 and 21 Onshore Wind, variable O&M 0 USD/MWh', '2019 USD')

# ---- ATB paths: PPPVT2 (UtilityPV), PPPVTS (PV-plus-battery), PPPVD (CommPV)
MAP = {'PPPVT2': 'UtilityPV', 'PPPVTS': 'Utility-Scale PV-Plus-Battery', 'PPPVD': 'CommPV'}
prop_pvd = {}
for t, tech in MAP.items():
    for p, ap in (('CapitalCost', 'CAPEX'), ('FixedCost', 'Fixed O&M')):
        for y in YEARS:
            c = current(t, p, y)
            if y >= 2022:
                new = A(2024, tech, ap, y)
                old = A(2023, tech, ap, y)
                if within(c, old):
                    cls, chg = 'matched, newer edition', 'upgrade'
                    der = (f'current {c:.2f} equals ATB 2023 {tech} {ap} {y} = {old:.2f} (2021 USD); newer edition ATB 2024 gives {new:.2f} (2022 USD); '
                           + ATB_LOC.format(t=tech, c='Class5', p=ap, y=y))
                    src = f"{ATB_SRC[2024]};{ATB_SRC[2023]}"
                else:
                    cls, chg = 'replace', 'replace'
                    der = (f'current {c:.2f} matches no ATB edition for {y}; ATB 2024 {tech} {ap} {y} = {new:.2f} (2022 USD), the path source for this row; '
                           + ATB_LOC.format(t=tech, c='Class5', p=ap, y=y))
                    src = ATB_SRC[2024]
                add(t, p, y, new, cls, chg, src, der, ATB_DY[2024])
            else:
                yy = max(y, 2019)
                ref = A(2021, tech, ap, yy)
                ref23 = A(2023, tech, ap, y) if y >= 2021 else None
                if within(c, ref) or within(c, ref23):
                    ed = 2021 if within(c, ref) else 2023
                    v = ref if ed == 2021 else ref23
                    add(t, p, y, c, 'matched', 'keep', ATB_SRC[ed],
                        f'current {c:.2f} equals ATB {ed} {tech} {ap} {y if ed == 2023 else yy} = {v:.2f} ({ATB_DY[ed]}); ATB 2024 starts in 2022; ' + ATB_LOC.format(t=tech, c='Class5', p=ap, y=y if ed == 2023 else yy), ATB_DY[ed])
                    new = c
                else:
                    new = ref
                    add(t, p, y, ref, 'replace', 'replace', ATB_SRC[2021],
                        f'current {c:.2f} matches no ATB value for {y}; ATB 2024 starts in 2022, so the ATB 2021 value for {yy} is used ({ref:.2f}, 2019 USD; years before 2019 held at 2019); '
                        + ATB_LOC.format(t=tech, c='Class5', p=ap, y=yy), ATB_DY[2021])
            if t == 'PPPVD':
                prop_pvd[(p, y)] = new

# ---- PPPVDS distributed PV with storage: ASSUMPTION built from ATB ratios
r24c = A(2024, 'Utility-Scale PV-Plus-Battery', 'CAPEX', 2024) / A(2024, 'UtilityPV', 'CAPEX', 2024)
r24f = A(2024, 'Utility-Scale PV-Plus-Battery', 'Fixed O&M', 2024) / A(2024, 'UtilityPV', 'Fixed O&M', 2024)
pvds = {}
for p, ap in (('CapitalCost', 'CAPEX'), ('FixedCost', 'Fixed O&M')):
    for y in YEARS:
        ed, yy = (2024, y) if y >= 2022 else (2021, max(y, 2019))
        ratio = A(ed, 'Utility-Scale PV-Plus-Battery', ap, yy) / A(ed, 'UtilityPV', ap, yy)
        pvds[(p, y)] = (prop_pvd[(p, y)] * ratio, ratio, ed, yy)
c50 = pvds[('CapitalCost', 2050)][0]; f50 = pvds[('FixedCost', 2050)][0]
c24 = pvds[('CapitalCost', 2024)][0]; f24 = pvds[('FixedCost', 2024)][0]
SENT_PVDS = (f'ASSUMPTION: distributed solar PV with battery storage in Guatemala costs the distributed (commercial rooftop) PV cost of each year multiplied by the ratio of '
             f'utility-scale PV-plus-battery to utility-scale PV cost in the same year of the NREL Annual Technology Baseline (Moderate scenario, Market case): '
             f'in 2024 capital {prop_pvd[("CapitalCost", 2024)]:.2f} x {r24c:.4f} = {c24:.1f} USD/kW and fixed O&M {prop_pvd[("FixedCost", 2024)]:.2f} x {r24f:.4f} = {f24:.2f} USD/kW-yr, '
             f'and in 2050 {c50:.1f} USD/kW and {f50:.2f} USD/kW-yr, for all model years (ATB 2021 ratios before 2022). Reason: a battery adds the same share of cost to a rooftop PV system as it adds to a '
             f'utility-scale PV plant, so the utility-scale ratio carries over to distributed systems. Check: the EIA 2020 cost study prices utility-scale PV with storage at 1755 against '
             f'1313 USD/kW for PV alone (ratio 1.34) and fixed O&M at 31.27 against 15.25 USD/kW-yr (ratio 2.05). Range: capital ratio 1.34 to {r24c:.2f}, about '
             f'{prop_pvd[("CapitalCost", 2024)] * 1.34:.0f} to {c24:.0f} USD/kW in 2024.')
for p in ('CapitalCost', 'FixedCost'):
    for y in YEARS:
        v, ratio, ed, yy = pvds[(p, y)]
        add('PPPVDS', p, y, v, 'ASSUMPTION', 'replace', f"{ATB_SRC[ed]};INT-009",
            f'PPPVD proposed {p} {y} {prop_pvd[(p, y)]:.2f} x ATB {ed} ratio PV-plus-battery / UtilityPV ({yy}) {ratio:.4f} = {v:.2f}', ATB_DY[ed], SENT_PVDS)
for t in ('PPPVT2', 'PPPVTS', 'PPPVD', 'PPPVDS'):
    flat(t, 'VariableCost', 0, 'matched', 'keep', 'INT-009', 'EIA 2020 cost study Table 2 p.29, Cases 24 and 25 Solar PV and Solar PV with battery storage, variable O&M 0 USD/MWh', '2019 USD')

# ---- IMP_ELE electricity imports (rule E1)
P_MWH = 62.02
v = P_MWH / MWH
SRC_IMP = 'NAT-006;' + ';'.join(f'NAT-0{i}' for i in range(10, 22))
SENT_IMP = ('ASSUMPTION: electricity imported into Guatemala costs 17.23 USD/GJ (62.02 USD/MWh, real 2024 USD) in every model year, equal to the 2024 '
            'volume-weighted import price. Reason: the model fixes the import quantity each year, so the price only adds a fixed amount to total cost, and holding '
            'the 2024 price constant in real terms is the neutral path for a price set month by month on the Mexican and regional spot markets. Check: UN Comtrade records '
            "Mexico's 2024 electricity exports to Guatemala at 1,285,713 MWh for 101.13 million USD FOB (78.66 USD/MWh), and the AMM 2024 statistical report gives the "
            'regional market (MER) average price as 158.35 USD/MWh. Range: 55.75 USD/MWh (Mexico supply alone, 2024 weighted) to 78.66 USD/MWh (customs value), '
            '15.5 to 21.9 USD/GJ.')
for y in YEARS:
    if y == 2024:
        add('IMP_ELE', 'VariableCost', y, v, 'observed', 'fill_placeholder', SRC_IMP,
            'AMM monthly market analyses 2024 (section 5 prices and section 7 import energy): Mexico 55.75 USD/MWh on 1,623.39 GWh and MER 121.68 USD/MWh on 170.57 GWh, '
            'volume-weighted 62.02 USD/MWh on 1,793.96 GWh (AMM Informe Estadistico 2024 p.4: 1,793.97 GWh); 62.02 x 0.27778 = 17.2278 USD/GJ (62.02 / 3.6)', '2024 USD')
    else:
        add('IMP_ELE', 'VariableCost', y, v, 'ASSUMPTION', 'fill_placeholder', SRC_IMP + ';NAT-031;NAT-032',
            'held at the 2024 volume-weighted import price 62.02 USD/MWh = 17.2278 USD/GJ', '2024 USD', SENT_IMP)

pc = pd.DataFrame(rows)
pc.to_csv(os.path.join(J, 'plant_costs.csv'), index=False)
print(len(pc)); print(pc.groupby(['class', 'change_class']).size().to_string())
s = pc[pc.year.isin([2024, 2050])].pivot_table(index=['technology', 'parameter'], columns='year', values=['current_value', 'proposed_value'], aggfunc='first')
print(s.round(3).to_string())
