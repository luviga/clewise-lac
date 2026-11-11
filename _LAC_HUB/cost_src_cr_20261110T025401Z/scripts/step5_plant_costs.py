"""Step 5: plant cost classification and proposals for Costa Rica (rules P1 to P3); writes plant_costs.csv.

Currency basis kept as in the model: the 2021 column in 2021 USD, 2022 to 2050 in 2022 USD (model rule:
2022 value = 2021 value x 1.0800, the CPI-U ratio 2022/2021). Source values are converted with BLS CPI-U annual averages (CRC-001).
Usage: py -I step5_plant_costs.py <job folder>
"""
import os, sys
import pandas as pd

JOB = sys.argv[1]
YEARS = list(range(2021, 2051))
CPI = {2019: 255.657, 2021: 270.970, 2022: 292.655, 2024: 313.689}
cur = pd.read_csv(os.path.join(JOB, 'cost_rows_current.csv'))
cur.columns = [str(c) for c in cur.columns]
atb = pd.read_csv(os.path.join(JOB, 'scripts', 'atb_extract.csv'))
atb['y'] = pd.to_numeric(atb.core_metric_variable, errors='coerce')
atb['value'] = pd.to_numeric(atb.value, errors='coerce')


def atb_series(tech, detail, par):
    s = atb[(atb.technology == tech) & (atb.techdetail == detail) & (atb.core_metric_parameter == par)]
    return {int(r.y): float(r.value) for _, r in s.iterrows() if 2022 <= r.y <= 2050}


def current(t, p):
    r = cur[(cur.Tech == t) & (cur.Parameter == p)].iloc[0]
    return {y: (None if pd.isna(r[str(y)]) else float(r[str(y)])) for y in YEARS}


def to22(v, yr):
    return v * CPI[2022] / CPI[yr]


ATB_SRC = 'CRC-013'
SHAPES = {
    'UPV_CAPEX': ('UtilityPV', 'Class5', 'CAPEX'), 'UPV_FOM': ('UtilityPV', 'Class5', 'Fixed O&M'),
    'RES_CAPEX': ('ResPV', 'Class5', 'CAPEX'), 'RES_FOM': ('ResPV', 'Class5', 'Fixed O&M'),
    'LBW_CAPEX': ('LandbasedWind', 'Class4', 'CAPEX'), 'LBW_FOM': ('LandbasedWind', 'Class4', 'Fixed O&M'),
    'NPD1_CAPEX': ('Hydropower', 'NPD1', 'CAPEX'), 'NPD1_FOM': ('Hydropower', 'NPD1', 'Fixed O&M'),
    'FLASH_CAPEX': ('Geothermal', 'HydroFlash', 'CAPEX'), 'FLASH_FOM': ('Geothermal', 'HydroFlash', 'Fixed O&M'),
    'BIO_CAPEX': ('Biopower', 'Dedicated', 'CAPEX'),
}
SHAPE_NAME = {k: 'NREL ATB 2024 %s %s %s, Market, Moderate' % v for k, v in SHAPES.items()}


def shaped(level24, shape):
    """level at 2024 in 2022 USD; returns values by year with the model's 2021 rule."""
    if shape == 'flat':
        vals = {y: level24 for y in range(2022, 2051)}
    elif shape.startswith('MODEL:'):
        t, p = shape[6:].split('|')
        c = current(t, p)
        vals = {y: level24 * c[y] / c[2024] for y in range(2022, 2051)}
    else:
        s = atb_series(*SHAPES[shape])
        vals = {y: level24 * s[y] / s[2024] for y in range(2022, 2051)}
    vals[2021] = vals[2022] * CPI[2021] / CPI[2022]
    return vals


A_ENGINE = ('ASSUMPTION: non-fuel variable operation and maintenance cost of diesel and fuel oil engine power plants in Costa Rica is 4.70 USD/MWh of '
            'electricity (1.3056 USD/GJ), in 2022 USD, for all years 2021 to 2050. Reason: the non-fuel variable cost of reciprocating engine plants comes '
            'from lubricating oil, consumables and maintenance scheduled by running hours, which add a few US dollars per MWh; fuel is charged separately '
            'through the fuel supply rows. Check: the US Energy Information Administration gives 6.40 USD/MWh (2022 USD) of variable O&M for a 21 MW internal '
            'combustion engine plant (Annual Energy Outlook 2023, Cost and Performance Characteristics of New Generating Technologies, Table 1). '
            'Range: 4 to 7 USD/MWh (1.1 to 1.9 USD/GJ).')

# (tech, parameter): spec
SPEC = {
    ('PP_SPV_DG', 'CapitalCost'): dict(cls='replace', level=2600.58, shape='RES_CAPEX', src='CRC-013',
        der='NREL ATB 2024 ResPV Class5 CAPEX 2024 = 2600.58 USD/kW (2022 USD, Market, Moderate); IRENA 2022 and 2024 editions, WEO 2023 and the ICE expansion plan publish no residential rooftop PV cost'),
    ('PP_SPV_DG', 'FixedCost'): dict(cls='replace', level=29.53, shape='RES_FOM', src='CRC-013',
        der='NREL ATB 2024 ResPV Class5 Fixed O&M 2024 = 29.53 USD/kW-yr (2022 USD)'),
    ('PWRBMS', 'CapitalCost'): dict(cls='matched, newer edition', level=to22(3242, 2024), shape='BIO_CAPEX', src='CRC-010;CRC-011;CRC-001;CRC-013',
        der=('matched: IRENA RPGC 2022 Table H.1 p.15 bioenergy global weighted average total installed cost 2022 = 2162 USD/kW (2022 USD) vs model 2024 2157.02 (2022 USD), +0.2 percent; '
             'newer edition: IRENA RPGC 2024 Table S1 p.15 bioenergy 2024 = 3242 USD/kW (2024 USD) x CPI 2022 292.655 / CPI 2024 313.689 = %.2f USD/kW (2022 USD)') % to22(3242, 2024)),
    ('PWRBMS', 'FixedCost'): dict(cls='replace', level=to22(37, 2019), shape='flat', src='CRC-012;CRC-001',
        der='ICE PEG 2020-2035 Tabla 10.7 (PDF p.110, printed p.100) Biomasa Generico Desc. 20 MW fixed O&M 37 USD/kW-yr (Dec-2019 USD) x CPI 2022 292.655 / CPI 2019 255.657 = %.2f; IRENA gives only a range (2 to 6 percent of installed cost); held flat as in ATB 2024 Biopower Fixed O&M' % to22(37, 2019)),
    ('PWRBMS', 'VariableCost'): dict(cls='replace', level=to22(4.0 / 3.6, 2024), shape='flat', src='CRC-011;CRC-001',
        der='IRENA RPGC 2024 p.171: bioenergy variable O&M around 0.004 USD/kWh (2024 USD) = 4.0 USD/MWh / 3.6 = 1.1111 USD/GJ x 292.655 / 313.689 = %.4f USD/GJ (2022 USD); flat' % to22(4.0 / 3.6, 2024)),
    ('PWRDSL', 'CapitalCost'): dict(cls='matched', src='CRC-012;CRC-001;CRC-013',
        der=('matched: ICE PEG 2020-2035 Tabla 10.8 (PDF p.111) MMV (motores de media velocidad) overnight 1300 USD/kW (Dec-2019 USD) x 292.655 / 255.657 = %.2f (2022 USD) vs model 2024 1488.67, 0.0 percent; '
             'path: model 2021 x 1.0800 x ATB 2024 NG 2-on-1 Combined Cycle (F-Frame) 95%% CCS CAPEX (y) / (2022), exact shape match') % to22(1300, 2019)),
    ('PWRDSL', 'FixedCost'): dict(cls='replace', level=to22(21, 2019), shape='MODEL:PWRDSL|FixedCost', src='CRC-012;CRC-001;CRC-013',
        der='ICE PEG 2020-2035 Tabla 10.7 (PDF p.110) MMV fixed O&M 21 USD/kW-yr (Dec-2019 USD) x 292.655 / 255.657 = %.2f at 2024; path keeps the model shape, ATB 2024 NG 2-on-1 Combined Cycle (F-Frame) 95%% CCS Fixed O&M' % to22(21, 2019)),
    ('PWRDSL', 'VariableCost'): dict(cls='ASSUMPTION', src='CRC-014', der='value unchanged at 1.3056 USD/GJ = 4.70 USD/MWh; check against EIA AEO2023 Table 1 internal combustion engine variable O&M 6.40 USD/MWh (2022 USD)', asm=A_ENGINE),
    ('PWRFOI', 'CapitalCost'): dict(cls='replace', level=to22(1300, 2019), shape='flat', src='CRC-012;CRC-001',
        der='ICE PEG 2020-2035 Tabla 10.8 (PDF p.111) MMV overnight 1300 USD/kW (Dec-2019 USD; Tabla 10.7 note d, medium-speed engines, the ICE bunker engine candidate) x 292.655 / 255.657 = %.2f (2022 USD); flat as the model; 2021 = %.2f (2021 USD)' % (to22(1300, 2019), 1300 * CPI[2021] / CPI[2019])),
    ('PWRFOI', 'FixedCost'): dict(cls='replace', level=to22(21, 2019), shape='flat', src='CRC-012;CRC-001',
        der='ICE PEG 2020-2035 Tabla 10.7 (PDF p.110) MMV fixed O&M 21 USD/kW-yr (Dec-2019 USD) x 292.655 / 255.657 = %.2f (2022 USD); flat' % to22(21, 2019)),
    ('PWRFOI', 'VariableCost'): dict(cls='ASSUMPTION', src='CRC-014', der='value unchanged at 1.3056 USD/GJ = 4.70 USD/MWh; check against EIA AEO2023 Table 1 internal combustion engine variable O&M 6.40 USD/MWh (2022 USD)', asm=A_ENGINE),
    ('PWRGEO', 'CapitalCost'): dict(cls='matched', src='CRC-012;CRC-001;CRC-013',
        der=('matched: ICE PEG 2020-2035 Tabla 10.8 (PDF p.111) Borinquen 2 and Geotermico Generico 12 MW overnight 5496 USD/kW (Dec-2019 USD) x 292.655 / 255.657 = %.2f (2022 USD) vs model 2024 6348.29, -0.9 percent; '
             'path: model 2021 x 1.0800 x ATB 2024 Geothermal HydroFlash CAPEX (y) / (2022), exact shape match') % to22(5496, 2019)),
    ('PWRGEO', 'FixedCost'): dict(cls='replace', level=to22(125, 2024), shape='FLASH_FOM', src='CRC-011;CRC-010;CRC-001;CRC-013',
        der='IRENA RPGC 2024 p.162: geothermal O&M assumption for 2024 projects 125 USD/kW-yr (2024 USD) x 292.655 / 313.689 = %.2f (2022 USD) at 2024 (IRENA RPGC 2022 p.173: 115 USD/kW-yr, 2022 USD); path ATB 2024 Geothermal HydroFlash Fixed O&M' % to22(125, 2024)),
    ('PWRHYDDAM', 'CapitalCost'): dict(cls='matched', src='CRC-013',
        der='matched: NREL ATB 2024 Hydropower NSD2 (new stream-reach) CAPEX 8140.07 USD/kW (2022 USD, flat 2022 to 2050) vs model 2022 to 2050 8079.14, +0.8 percent; model 2021 7480.5 vs 8140.07 x 270.970 / 292.655 = 7536.9, +0.8 percent; flat as in ATB'),
    ('PWRHYDDAM', 'FixedCost'): dict(cls='replace', level=to22(32, 2019), shape='flat', src='CRC-012;CRC-001;CRC-010',
        der='ICE PEG 2020-2035 Tabla 10.7 (PDF p.110) fixed O&M of the reservoir candidates Hidro 2 con regulacion 16 and Hidro 3 con regulacion 48 USD/kW-yr (Dec-2019 USD), mean 32 x 292.655 / 255.657 = %.2f (2022 USD); flat. IRENA RPGC 2022 p.162 gives only a range, 20 to 60 USD/kW-yr' % to22(32, 2019)),
    ('PWRHYDROR', 'CapitalCost'): dict(cls='matched', src='CRC-012;CRC-001;CRC-013',
        der=('matched: ICE PEG 2020-2035 Tabla 10.8 (PDF p.111) Hidro Generico 20 MW and 50 MW overnight 4013 USD/kW (Dec-2019 USD) x 270.970 / 255.657 = %.1f (2021 USD) vs model 2021 4248.5, +0.1 percent; x 292.655 / 255.657 = %.1f (2022 USD) vs model 2024 4588.50, +0.1 percent; '
             'path ATB 2024 Hydropower NPD1 CAPEX shape (flat to 2035, x 0.9599 from 2036)') % (4013 * CPI[2021] / CPI[2019], to22(4013, 2019))),
    ('PWRHYDROR', 'FixedCost'): dict(cls='replace', level=to22(48, 2019), shape='NPD1_FOM', src='CRC-012;CRC-001;CRC-013',
        der='ICE PEG 2020-2035 Tabla 10.7 (PDF p.110) Hidro Generico fixed O&M 48 USD/kW-yr (Dec-2019 USD) x 292.655 / 255.657 = %.2f (2022 USD); path ATB 2024 Hydropower NPD1 Fixed O&M (92, 88 in 2050)' % to22(48, 2019)),
    ('PWRSPVDTR', 'CapitalCost'): dict(cls='replace', level=to22(1375, 2024), shape='UPV_CAPEX', src='CRC-011;CRC-001;CRC-013',
        der='IRENA RPGC 2024 Table 3.1 (p.95) utility-scale solar PV, Central America and the Caribbean, weighted average total installed cost 2024 = 1375 USD/kW (2024 USD) x 292.655 / 313.689 = %.2f (2022 USD) at 2024; path ATB 2024 UtilityPV Class5 CAPEX (the current linear decline to 2030 then flat has no source)' % to22(1375, 2024)),
    ('PWRSPVDTR', 'FixedCost'): dict(cls='matched', src='CRC-012;CRC-001',
        der='matched: ICE PEG 2020-2035 Tabla 10.7 (PDF p.110) Valle Escondido 5 MW distribution-connected solar fixed O&M 19 USD/kW-yr (Dec-2019 USD) x 270.970 / 255.657 = 20.14 (2021 USD) vs model 2021 20.0, +0.7 percent; rule: held flat at 20 for all years'),
    ('PWRSPVTRN', 'CapitalCost'): dict(cls='matched', src='CRC-012;CRC-001;CRC-013',
        der='matched: ICE PEG 2020-2035 Tabla 10.8 (PDF p.111) Solar Generico 20 MW and 50 MW overnight 1105 USD/kW (Dec-2019 USD) x 270.970 / 255.657 = 1171.2 (2021 USD) vs model 2021 1163.75, +0.6 percent; path: model 2021 x 1.0800 x ATB 2024 UtilityPV Class5 CAPEX (y) / (2022), exact shape match'),
    ('PWRSPVTRN', 'FixedCost'): dict(cls='replace', level=to22(20.7, 2024), shape='UPV_FOM', src='CRC-011;CRC-010;CRC-001;CRC-013',
        der='IRENA RPGC 2024 Table A4 (p.210) solar PV O&M assumption, OECD (Costa Rica is an OECD member), 2024 = 20.7 USD/kW-yr (2024 USD) x 292.655 / 313.689 = %.2f (2022 USD) at 2024 (IRENA RPGC 2022 Table A1.3: OECD 2022 17.8, 2022 USD); path ATB 2024 UtilityPV Class5 Fixed O&M' % to22(20.7, 2024)),
    ('PWRWNONS', 'CapitalCost'): dict(cls='replace', level=to22(2108, 2024), shape='LBW_CAPEX', src='CRC-011;CRC-010;CRC-001;CRC-013',
        der='IRENA RPGC 2024 Table 2.1 (p.71) onshore wind, Central America and the Caribbean, weighted average total installed cost 2024 = 2108 USD/kW (2024 USD) x 292.655 / 313.689 = %.2f (2022 USD) at 2024 (IRENA RPGC 2022 Table 2.1 p.75: 1694 USD/kW, 2022 USD, 2021 data); path ATB 2024 LandbasedWind Class4 CAPEX' % to22(2108, 2024)),
    ('PWRWNONS', 'FixedCost'): dict(cls='replace', level=to22(45, 2024), shape='LBW_FOM', src='CRC-011;CRC-010;CRC-001;CRC-013',
        der='IRENA RPGC 2024 Table A3 (p.209) onshore wind O&M assumption, Other OECD = 45 USD/kW-yr (2024 USD) x 292.655 / 313.689 = %.2f (2022 USD) at 2024 (IRENA RPGC 2022 Table A1.2: Other OECD 36, 2022 USD); path ATB 2024 LandbasedWind Class4 Fixed O&M' % to22(45, 2024)),
}
EMPTY_OK = {'PP_SPV_DG': 'ResPV', 'PWRGEO': 'Geothermal', 'PWRHYDDAM': 'Hydropower', 'PWRHYDROR': 'Hydropower',
            'PWRSPVDTR': 'UtilityPV and CommPV', 'PWRSPVTRN': 'UtilityPV', 'PWRWNONS': 'LandbasedWind'}
PLANTS = ['PP_SPV_DG', 'PWRBMS', 'PWRDSL', 'PWRFOI', 'PWRGEO', 'PWRHYDDAM', 'PWRHYDROR', 'PWRSPVDTR', 'PWRSPVTRN', 'PWRWNONS']
rows = []
for t in PLANTS:
    for p in ('CapitalCost', 'FixedCost', 'VariableCost'):
        c = current(t, p)
        sp = SPEC.get((t, p))
        if sp is None:
            assert p == 'VariableCost' and all(v is None for v in c.values()), (t, p)
            sp = dict(cls='matched', src='CRC-013', der='current value empty (no non-fuel variable O&M); NREL ATB 2024 reports only fixed O&M for %s (no Variable O&M rows in the Market case), so the cell stays empty' % EMPTY_OK[t])
            prop = {y: None for y in YEARS}
        elif sp['cls'] in ('matched', 'ASSUMPTION'):
            prop = dict(c)
        else:
            prop = shaped(sp['level'], sp['shape'])
        shape_txt = SHAPE_NAME.get(sp.get('shape', ''), sp.get('shape', ''))
        for y in YEARS:
            rows.append(dict(technology=t, parameter=p, year=y, current_value=c[y], proposed_value=None if prop[y] is None else round(prop[y], 4),
                             **{'class': sp['cls']}, source_ids=sp['src'], derivation=sp['der'] + ('' if y != 2021 or sp['cls'] in ('matched', 'ASSUMPTION') else '; 2021 column = 2022 value x 270.970 / 292.655 (2021 USD, model convention)'),
                             assumption_sentence=sp.get('asm', '')))
# Electricity imports (rule E1): IMPELE VariableCost, real 2024 USD, held flat
IMP_MWH, IMP_USD = 363748.07, 74953098.26          # ICE DOCSE Informe Anual 2024 p.17, Total row
IMP_PRICE = IMP_USD / IMP_MWH                       # 206.06 USD/MWh
IMP_GJ = IMP_PRICE * 0.27778                        # USD/GJ (1 USD/MWh = 0.27778 USD/GJ)
A_IMP = ('ASSUMPTION: electricity imported by Costa Rica from the Central American regional electricity market costs %.2f USD/MWh (%.2f USD/GJ), '
         'real 2024 USD, in every model year from 2021 to 2050 other than 2024, equal to the 2024 average. Reason: regional market prices follow '
         'the hydrology and fuel costs of the Central American systems and have no long-term projection; the 2024 average covers contract and spot '
         'purchases and the regional transmission charge on contract imports, so it is the full cost of delivered imports. Check: for 2025 the Costa '
         'Rican regulator used an import price of 152.66 USD/MWh projected by ICE (ARESEP RE-0097-IE-2024, page 11), and the 2024 cost without the '
         'regional transmission charge was %.2f USD/MWh. Range: 150 to 210 USD/MWh (41.7 to 58.3 USD/GJ).') % (IMP_PRICE, IMP_GJ, (IMP_USD - 20629009.48) / IMP_MWH)
der_imp = ('ICE DOCSE Informe Anual 2024 p.17, Importacion del ICE al Mercado Regional 2024, Total row: 74,953,098.26 USD / 363,748.07 MWh = %.2f USD/MWh '
           '(contract south, contract north and regional spot market, including the CMORC transmission charge of 20,629,009.48 USD) x 0.27778 = %.4f USD/GJ (MWH_PER_GJ, GEN-003)') % (IMP_PRICE, IMP_GJ)
for y in YEARS:
    rows.append(dict(technology='IMPELE', parameter='VariableCost', year=y, current_value=None, proposed_value=round(IMP_GJ, 4),
                     **{'class': 'observed' if y == 2024 else 'ASSUMPTION'}, source_ids='CRC-015;GEN-003' + ('' if y == 2024 else ';CR-015'),
                     derivation=der_imp + ('' if y == 2024 else '; held at the 2024 value'), assumption_sentence='' if y == 2024 else A_IMP))
pc = pd.DataFrame(rows)
pc.to_csv(os.path.join(JOB, 'plant_costs.csv'), index=False)
s = pc[pc.year.isin([2021, 2024, 2030, 2050])].pivot_table(index=['technology', 'parameter', 'class'], columns='year', values=['current_value', 'proposed_value'], aggfunc='first')
print(s.round(2).to_string())
