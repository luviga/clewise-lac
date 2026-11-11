"""Steps 5 to 7: plant, other-row and electricity import cost proposals for Ecuador.

Usage: py -I step5_plant_costs.py <job_folder>
Inputs (job folder): cost_rows_current.csv, fuel_prices.csv,
  downloads/_extract/ccg_costs_ECU.csv (CCG kit workbook values), pmc_compiled_costs.csv (PLANMICC compiled BAU),
  ben_cpi_annual.csv, atb_values.csv (NREL ATB 2024, optional)
Outputs: plant_costs.csv, mapping_ECU.csv, downloads/_extract/constants_plant.csv
"""
import sys, os
import pandas as pd

job = sys.argv[1]
X = os.path.join(job, 'downloads', '_extract')
YEARS = list(range(2021, 2051))
cur = pd.read_csv(os.path.join(job, 'cost_rows_current.csv'))
ccg = pd.read_csv(os.path.join(X, 'ccg_costs_ECU.csv'))
ccg = ccg[ccg.file_in_kit == 'Ecuador Base SAND.xlsm']
pmc = pd.read_csv(os.path.join(X, 'pmc_compiled_costs.csv'))
cpi = pd.read_csv(os.path.join(X, 'ben_cpi_annual.csv')).set_index('year')['annual_average'].to_dict()
F20 = cpi[2024] / cpi[2020]
F22 = cpi[2024] / cpi[2022]
C2A = 31.536  # PJ per GW-year
const = [('CPI_FACTOR_2020_TO_2024', round(F20, 6), 'ratio', 'BEN-004', 'CPI-U annual averages 2024 / 2020', '313.689 / 258.811'),
         ('CPI_FACTOR_2022_TO_2024', round(F22, 6), 'ratio', 'BEN-004', 'CPI-U annual averages 2024 / 2022', '313.689 / 292.655'),
         ('PJ_PER_GW_YEAR', C2A, 'PJ per GW-year', 'GEN-003', 'Appendix B.8, page 45', '8760 h x 3600 s / 1e6 x 1 GW = 31.536 PJ')]

fp = pd.read_csv(os.path.join(job, 'fuel_prices.csv'))
atb_path = os.path.join(X, 'atb_values.csv')
atb = pd.read_csv(atb_path) if os.path.exists(atb_path) else None


def ccg_val(code, par, y):
    s = ccg[(ccg.technology_code == code) & (ccg.parameter == par) & (ccg.year == y)]
    return float(s.value.iloc[0]), s.locator.iloc[0]


def pmc_val(code, par, y):
    if not code:
        return None
    s = pmc[(pmc.technology == code) & (pmc.parameter == par) & (pmc.year == y)]
    return float(s.value.iloc[0]) if len(s) else None


# Our plant -> CCG code, PLANMICC code, PLANMICC v2 source codes (capital/fixed/variable)
PLANT_MAP = {
    'PPBGS': ('PWRBIO001', 'PP_BGSICE', '4/4/none'),
    'PPBIM': ('PWRBIO001', 'PP_SUG', '1,4/4/none'),
    'PPIBIM': ('PWRBIO001', 'PP_SUG', '1,4/4/none'),
    'PPCRU': ('PWROHC001', 'PP_CRU', '4/4/4 (as PP_FOITST)'),
    'PPDDSL': ('PWROHC001', 'PP_DSLICE', '1/4/2'),
    'PPDFOI': ('PWROHC001', 'PP_FOIICE', '4/4/2'),
    'PPDSL': ('PWROHC001', 'PP_DSLICE', '1/4/2'),
    'PPFOI': ('PWROHC001', 'PP_FOIICE', '4/4/2'),
    'PPRDSL': ('PWROHC001', 'PPIDSLPETICE', '1/4/2'),
    'PPILPG': ('PWROHC001', None, 'none'),
    'PPNGS': ('PWRNGS002', 'PP_NGSTGS', '4/4/4'),
    'PPRNGS': ('PWRNGS002', 'PPINGSPETTGS', '4/4/4'),
    'PPHDAMAB': ('PWRHYD001', 'PP_HYDAMADAMLAR', '1/4/2'),
    'PPHDAMAM': ('PWRHYD001', 'PP_HYDAMADAMMED', '1/4/2'),
    'PPHDAMAS': ('PWRHYD002', 'PP_HYDAMADAMSMA', '1/4/2'),
    'PPHDAMPM': ('PWRHYD001', 'PP_HYDPACDAMMED', '1/4/2'),
    'PPHDAMPS': ('PWRHYD002', 'PP_HYDPACDAMSMA', '1/4/2'),
    'PPHRORAB': ('PWRHYD001', 'PP_HYDAMARORLAR', '1/4/2'),
    'PPHRORAM': ('PWRHYD001', 'PP_HYDAMARORMED', '1/4/2'),
    'PPHRORAS': ('PWRHYD002', 'PP_HYDAMARORSMA', '1/4/2'),
    'PPHRORPM': ('PWRHYD001', 'PP_HYDPACRORMED', '1/4/2'),
    'PPHRORPS': ('PWRHYD002', 'PP_HYDPACRORSMA', '1/4/2'),
    'PPHD': ('PWRHYD003', 'PP_HYDAMARORSMA', '1/4/2'),
    'PPIHD': ('PWRHYD004', 'PPIHYDAMAELR', '1/4/2'),
    'PPPVT': ('PWRSOL001', 'PP_SPV_US', '3/4/none'),
    'PPPVTS': ('PWRSOL001S', None, 'none'),
    'PPWNDON': ('PWRWND001', 'PP_WND_US', '1/4/none'),
    'PPPVD': (None, 'PP_SPV_DG', 'no code'),
    'PPWNDD': (None, None, 'none'),
}
CCG_DESC = {r.technology_code: r.technology_description for r in ccg.drop_duplicates('technology_code').itertuples()}
MAP_NOTE = {
    'PPBGS': 'biogas engines: CCG has one biomass plant class',
    'PPBIM': 'bagasse and residue plants: CCG biomass plant',
    'PPIBIM': 'isolated biomass plants: CCG biomass plant',
    'PPCRU': 'crude-fired engines and boilers: CCG light fuel oil plant is its only liquid-fuel plant above 1 kW',
    'PPDDSL': 'distributed diesel plants (MW scale): CCG light fuel oil plant; its 1 kW standalone generator class is too small',
    'PPDFOI': 'distributed fuel oil plants: CCG light fuel oil plant',
    'PPDSL': 'diesel engines and turbines: CCG light fuel oil plant',
    'PPFOI': 'fuel oil engines and steam plants: CCG light fuel oil plant',
    'PPRDSL': 'isolated refinery and oilfield diesel plants: CCG light fuel oil plant',
    'PPILPG': 'isolated LPG engines: CCG light fuel oil plant',
    'PPNGS': 'Ecuador gas plants are open-cycle turbines (Termogas Machala): CCG gas SCGT',
    'PPRNGS': 'isolated refinery and oilfield gas turbines: CCG gas SCGT',
    'PPHD': 'distributed hydro: CCG small hydro (<10 MW)',
    'PPIHD': 'isolated hydro: CCG off-grid hydro',
    'PPPVT': 'utility PV: CCG utility PV',
    'PPPVTS': 'utility PV with storage: CCG utility PV with 2 hour storage',
    'PPWNDON': 'onshore wind: CCG onshore wind',
    'PPPVD': 'distributed PV without storage: CCG has only distributed PV with storage (PWRSOL002), not equivalent',
    'PPWNDD': 'distributed wind: no CCG or PLANMICC class',
}
for t in [k for k in PLANT_MAP if k.startswith(('PPHDAM', 'PPHROR'))]:
    kind = 'dam' if 'HDAM' in t else 'run-of-river'
    basin = 'Amazon' if t[5] == 'A' else 'Pacific'
    size = {'B': 'big (450 MW and above)', 'M': 'medium (50 to 450 MW)', 'S': 'small (below 50 MW)'}[t[-1]]
    cc = PLANT_MAP[t][0]
    MAP_NOTE[t] = f'hydro {kind}, {basin}, {size}: CCG {CCG_DESC[cc]}; PLANMICC same basin, kind and size class'

mapping = []
for t, (cc, pm, codes) in PLANT_MAP.items():
    mapping.append(dict(technology=t, ccg_code=cc or 'none', ccg_description=CCG_DESC.get(cc, 'none'),
                        planmicc_code=pm or 'none', planmicc_v2_source_codes_cap_fix_var=codes, note=MAP_NOTE.get(t, '')))

rows = []


def curval(t, par, y):
    s = cur[(cur.Tech == t) & (cur.Parameter == par)]
    if not len(s):
        return None
    v = s[str(y)].iloc[0]
    if pd.isna(v):
        v0 = s['2021'].iloc[0]  # Flat mode: value in the first year column applies to all years
        return None if pd.isna(v0) else float(v0)
    return float(v)


def cls(current, proposed, basis):
    if basis == 'ASSUMPTION':
        b = 'ASSUMPTION'
    else:
        b = basis
    if current is None:
        return 'fill_empty', b
    if current in (1.0, 2.0) and abs(proposed - current) > 1e-9:
        return 'fill_placeholder', b
    if current != 0 and abs(proposed - current) / abs(current) <= 0.02:
        return 'keep', 'matched'
    if current == 0 and proposed == 0:
        return 'keep', 'matched'
    return 'replace', b


def add(t, par, y, prop, src, deriv, basis='replace', assumption='', pmcv=None, pmcode='', pmsrc='', scen='ALL', unit=''):
    c = curval(t, par, y)
    ch, b = cls(c, prop, basis)
    flag = ''
    if pmcv is not None and pmcv != 0:
        d = 100 * (prop - pmcv) / pmcv
        flag = 'yes' if abs(d) > 25 else 'no'
        pmd = round(d, 1)
    else:
        pmd = ''
    if ch == 'keep' and c is not None:
        deriv = f'current value {c:g} is within 2 percent of the source value {prop:.4f}; kept. Source value: ' + deriv
        prop = c
    rows.append(dict(technology=t, parameter=par, fuel_scenario=scen, year=y, current_value=c, proposed_value=round(prop, 6),
                     unit=unit, change_class=ch, basis_class=b, source_ids=src, derivation=deriv, assumption_sentence=assumption,
                     planmicc_code=pmcode, planmicc_value=pmcv, planmicc_source_code=pmsrc, diff_vs_planmicc_pct=pmd,
                     flag_over_25pct=flag))


UNITS = {'CapitalCost': 'MUSD/GW (= USD/kW)', 'FixedCost': 'MUSD/GW per year (= USD/kW-yr)', 'VariableCost': 'MUSD/PJ (= USD/GJ)'}

# ---------- power plants ----------
for t, (cc, pm, codes) in PLANT_MAP.items():
    cap_code, fix_code, var_code = (codes.split('/') + ['', '', ''])[:3] if '/' in codes else (codes, codes, codes)
    for y in YEARS:
        if cc:
            for par in ('CapitalCost', 'FixedCost'):
                v, loc = ccg_val(cc, par, y)
                add(t, par, y, v * F20, 'CCG-002;CCG-014;BEN-004',
                    f'CCG Ecuador kit {cc} ({CCG_DESC[cc]}) {par} {y} = {v:g} (2020 USD; {loc}) x CPI 2024/2020 {F20:.6f} = {v * F20:.4f}'
                    + ('' if par == 'FixedCost' else '; path as in the kit workbook (fossil and hydro flat, renewables declining)'),
                    pmcv=pmc_val(pm, par, y), pmcode=pm or '', pmsrc=(cap_code if par == 'CapitalCost' else fix_code),
                    unit=UNITS[par])
            add(t, 'VariableCost', y, 0.0, 'CCG-002;CCG-014',
                'CCG fixed costs include variable O&M (Allington et al. 2022, p.17), so non-fuel variable cost is 0; the kit workbook carries 0.0001 as a solver placeholder',
                pmcv=pmc_val(pm, 'VariableCost', y), pmcode=pm or '', pmsrc=var_code, unit=UNITS['VariableCost'])
        elif t == 'PPPVD' and atb is not None:
            pass  # filled below from ATB
        elif t == 'PPWNDD' and atb is not None:
            pass

# ATB-based rows (PPPVD, PPWNDD, STOELE): filled when atb_values.csv is present
ATB_ROWS = {'PPPVD': ('Commercial PV', None), 'PPWNDD': ('Distributed Wind', 'Midsize'),
            'STOELE': ('Utility-Scale Battery Storage', '4 Hr')}


def atb_get(tech, klass, par, y):
    a = atb[(atb.source_id == 'ATB-001') & (atb.technology.str.contains(tech, case=False, regex=False)) & (atb.parameter.str.upper() == par.upper())]
    if klass:
        a = a[a['class'].astype(str).str.contains(klass, case=False, regex=False)]
    if not len(a):
        return None, None, None
    pts = {int(r.year): float(r.value) for r in a.itertuples()}
    ys = sorted(pts)
    if y <= ys[0]:
        v = pts[ys[0]] if y >= 2024 else pts[ys[0]]
    elif y >= ys[-1]:
        v = pts[ys[-1]]
    elif y in pts:
        v = pts[y]
    else:
        lo = max(k for k in ys if k < y); hi = min(k for k in ys if k > y)
        v = pts[lo] + (pts[hi] - pts[lo]) * (y - lo) / (hi - lo)
    return v, a.source_id.iloc[0], a.dollar_year.iloc[0]


if atb is not None:
    for t, (tech, klass) in ATB_ROWS.items():
        for y in YEARS:
            for par, key in (('CapitalCost', 'OCC'), ('FixedCost', 'Fixed O&M')):
                v, sid, dy = atb_get(tech, klass, key, y)
                if v is None:
                    continue
                f = cpi[2024] / cpi[int(dy)]
                if t == 'STOELE':
                    prop = v * f / C2A
                    der = (f'NREL ATB 2024 {tech} {klass} Moderate {key} {y} = {v:.2f} USD/kW ({int(dy)} USD; values before 2024 take 2024, '
                           f'between published years linear) x CPI 2024/{int(dy)} {f:.6f} / 31.536 PJ per GW-year (STOELE capacity is in PJ/yr) = {prop:.4f}')
                    unit = 'MUSD per PJ/yr' if par == 'CapitalCost' else 'MUSD per PJ/yr per year'
                else:
                    prop = v * f
                    der = f'NREL ATB 2024 {tech}{" " + klass if klass else ""} Moderate {key} {y} = {v:.2f} ({int(dy)} USD) x CPI 2024/{int(dy)} {f:.6f} = {prop:.4f}'
                    unit = UNITS[par]
                pm = PLANT_MAP.get(t, (None, None, ''))[1]
                add(t, par, y, prop, f'{sid};BEN-004', der, pmcv=pmc_val(pm, par, y), pmcode=pm or '', pmsrc='no code' if pm else '', unit=unit)
            add(t, 'VariableCost', y, 0.0, f'{sid}',
                f'NREL ATB 2024 {tech} has no variable O&M (fixed O&M covers O&M)', unit=UNITS['VariableCost'] if t != 'STOELE' else 'MUSD/PJ')

# ---------- other rows ----------
A_DIST_CF = ('ASSUMPTION: {t} ({name}) has capital cost 0 and fixed cost 0 in every year from 2021 to 2050. '
             'Reason: this row carries the delivered fuel price per GJ as its variable cost, and that price already covers the terminals, storage and transport behind it, so a capacity cost would count them twice. '
             'Check: EP Petroecuador terminal price structures for 2024 list the storage, transport and marketing margins inside the published terminal price (Estructura de precios, January 2024). '
             'Range: 0; any separate infrastructure charge belongs in the variable cost.')
NAMES = dict(zip(cur.Tech, cur['Tech.Name']))

DIST_ROWS = ['DIST_COA', 'DIST_COK', 'DIST_CRU', 'DIST_DSL', 'DIST_FOI', 'DIST_GSL', 'DIST_JET', 'DIST_KER', 'DIST_LPG',
             'DIST_NGS', 'DIST_OPE', 'DIST_BGS', 'DIST_BIM', 'DIST_CHA', 'DIST_FIR', 'DIST_OID', 'DIST_RDF']
for t in DIST_ROWS:
    for y in YEARS:
        for par in ('CapitalCost', 'FixedCost'):
            add(t, par, y, 0.0, 'ECU-004', 'set to 0: see ASSUMPTION', basis='ASSUMPTION',
                assumption=A_DIST_CF.format(t=t, name=NAMES.get(t, '')), unit='MUSD per unit of capacity')

# Fuel supply VariableCost rows from fuel_prices.csv
OPE_A = None
foi24 = fp[(fp.row == 'DIST_FOI') & (fp.year == 2024) & (fp.scenario == 'STEPS')].value_usd_per_gj.iloc[0]
RES_GAL = 0.894  # EP Petroecuador industrial residue terminal price 2024, USD/gal excl. VAT (day-weighted)
res_gj = RES_GAL * 278 / 40.4  # 278 gal/t (UN, GEN-001), 40.4 GJ/t NCV residual fuel oil (IPCC, GEN-002)
const.append(('ECU_RESIDUE_TERMINAL_2024', RES_GAL, 'USD/gal excl. VAT, day-weighted 2024', 'ECU-003;ECU-004;ECU-005;ECU-006;ECU-007;ECU-008;ECU-009;ECU-010;ECU-011;ECU-012;ECU-013;ECU-014;ECU-015', 'Residuo industrial row, monthly terminal price lists', 'day-weighted mean of monthly prices excluding VAT'))
const.append(('UN_GAL_PER_T_FOI', 278, 'US gallons per metric ton (fuel oil)', 'GEN-001', 'Table II, page xxvii', 'as published'))
const.append(('IPCC_NCV_FOI', 40.4, 'GJ per t (net)', 'GEN-002', 'Table 1.2, page 1.18', 'Residual Fuel Oil'))
OPE_A = (f'ASSUMPTION: other petroleum products (DIST_OPE: asphalts, solvents, lubricants, sulphur, spray oil) are priced at the fuel oil export value, '
         f'{foi24:.2f} USD/GJ net in 2024 in real 2024 USD, and follow the fuel oil path in every year and fuel scenario (STEPS, CPS, NZE). '
         f'Reason: Ecuador\'s national energy balance defines these products as made from heavy refinery residues, and the market value of those residues to Ecuador is the fuel oil No. 6 export price. '
         f'Check: EP Petroecuador\'s 2024 terminal price for industrial residue, 0.894 USD/gal excluding VAT, equals {res_gj:.2f} USD/GJ at 278 gal/t and 40.4 GJ/t. '
         f'Range: {res_gj:.1f} to {foi24:.1f} USD/GJ in 2024.')
for r in fp.itertuples():
    if r.row == 'DIST_OPE':
        add(r.row, 'VariableCost', r.year, r.value_usd_per_gj, 'ECU-001;ECU-002;ECU-021;ECU-003;ECU-004;ECU-015;GEN-001;GEN-002;BEN-001;BEN-004;BEN-005',
            f'equal to DIST_FOI {r.scenario} {r.year} ({r.case.split(" (")[0]} path of the fuel oil export series)', basis='ASSUMPTION',
            assumption=OPE_A, scen=r.scenario, unit='MUSD/PJ (= USD/GJ)')
    else:
        deriv = f'{r.case}; r = {r.r} ({r.r_case}); benchmark {r.benchmark}; {r.weo_series}' if r.case != 'observed' else \
            'observed chosen point, real 2024 USD per GJ net (nominal x CPI 2024 / CPI year' + ('; gas gross / 0.9' if r.row == 'DIST_NGS' else '') + ')'
        basis = r.case if r.case in ('observed', 'history from ratio', 'projected') else 'projected'
        asent = ''
        if r.row == 'DIST_NGS':
            asent = ('ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the models\' net basis by dividing by 0.9 '
                     '(net = 0.9 x gross for natural gas, UN Statistics Division), for all six countries and all years. Reason: natural gas in the Americas, Henry Hub included, '
                     'is priced on a gross basis, and the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). '
                     'Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net basis would be overstated by about 11 percent.')
            if r.case == 'projected':
                asent += (' ASSUMPTION: Ecuador\'s natural gas price to generators is held flat in real terms from 2026 to 2050 at 3.44 USD/GJ net (real 2024 USD), '
                          'the mean of its observed real values for 2018 to 2025, in all three fuel scenarios. Reason: the price is set administratively for domestic gas from the Amistad field and does not follow an import benchmark. '
                          'Check: the observed real net values ranged from 3.15 USD/GJ (2023) to 3.87 USD/GJ (2025) (EP Petroecuador Informes Estadisticos 2018 to 2025). '
                          'Range: 3.1 to 3.9 USD/GJ.')
                basis = 'ASSUMPTION'
        add(r.row, 'VariableCost', r.year, r.value_usd_per_gj, r.source_ids, deriv, basis=basis, assumption=asent,
            scen=r.scenario, unit='MUSD/PJ (= USD/GJ)')

# EXTT rows: CCG extraction costs (variable), no capital or fixed in the kit
for t, cc, pmc_code in (('EXTT_CRU', 'MINOIL', None), ('EXTT_NGS', 'MINNGS', None)):
    for y in YEARS:
        for par in ('CapitalCost', 'FixedCost'):
            v, loc = ccg_val(cc, par, y)
            add(t, par, y, 0.0, 'CCG-002', f'CCG kit {cc} {par} {y} = {v:g} ({loc}), a solver placeholder for zero; proposed 0', unit='MUSD per unit of capacity')
        v, loc = ccg_val(cc, 'VariableCost', y)
        for s in ('STEPS', 'CPS', 'NZE'):
            add(t, 'VariableCost', y, v * F20, 'CCG-002;CCG-008;CCG-014;BEN-004',
                f'CCG Ecuador kit {cc} ({CCG_DESC[cc]}) VariableCost {y} = {v:g} USD/GJ (2020 USD; {loc}) x CPI 2024/2020 {F20:.6f}; same in all fuel scenarios',
                scen=s, unit='MUSD/PJ (= USD/GJ)')

# Other DIST VariableCost rows
for t in ('DIST_BIM', 'DIST_FIR'):
    for y in YEARS:
        v, loc = ccg_val('MINBIO', 'VariableCost', y)
        pm = 'PROSUG' if t == 'DIST_BIM' else 'PROFIR'
        add(t, 'VariableCost', y, v * F20, 'CCG-002;CCG-008;BEN-004',
            f'CCG Ecuador kit MINBIO (Biomass Extraction) VariableCost {y} = {v:g} USD/GJ (2020 USD; {loc}) x CPI 2024/2020 {F20:.6f}',
            pmcv=pmc_val(pm, 'VariableCost', y), pmcode=pm, pmsrc='8' if pm == 'PROSUG' else 'none', unit='MUSD/PJ (= USD/GJ)')
minbio = ccg_val('MINBIO', 'VariableCost', 2024)[0] * F20
A_CHA = (f'ASSUMPTION: charcoal (DIST_CHA) costs {2 * minbio:.2f} USD/GJ in real 2024 USD in every year from 2021 to 2050. '
         f'Reason: charcoal is made from wood, traditional kilns keep about half of the wood energy in the charcoal, so the wood cost per GJ of charcoal is twice the wood supply cost of {minbio:.2f} USD/GJ (CCG Ecuador kit biomass supply cost 5.6 USD/GJ in 2020 USD, times 1.2120 for US consumer prices to 2024). '
         f'Check: the CCG Ecuador kit biomass supply cost is 5.6 USD/GJ (2020 USD) in every year. '
         f'Range: {minbio:.1f} USD/GJ (wood cost alone) to {2 * minbio:.1f} USD/GJ.')
A_ZERO = {
    'DIST_BGS': ('ASSUMPTION: biogas (DIST_BGS) has a supply cost of 0 USD/GJ in every year from 2021 to 2050. '
                 'Reason: the biogas is landfill or digester gas collected at the generating site, and its collection and cleaning are part of the biogas plant\'s own capital and fixed costs (PPBGS, CCG biomass plant values). '
                 'Check: PLANMICC\'s Ecuador biogas engine row carries all its costs as capital and fixed costs and has no fuel cost (PP_BGSICE, compiled FixedCost and VariableCost). '
                 'Range: 0 to 3.4 USD/GJ, the domestic natural gas price, if the gas were bought from a third party.'),
    'DIST_OID': ('ASSUMPTION: waste oils (DIST_OID) have a supply cost of 0 USD/GJ in every year from 2021 to 2050. '
                 'Reason: waste oils are a by-product of lubricant and fuel use, collected as waste, and carry no extraction or import cost. '
                 'Check: EP Petroecuador\'s 2024 terminal price for industrial residue, the nearest priced heavy oil stream, is 0.894 USD/gal excluding VAT (about 6.2 USD/GJ). '
                 'Range: 0 to 6.2 USD/GJ.'),
    'DIST_RDF': ('ASSUMPTION: non-biomass municipal waste (DIST_RDF) has a supply cost of 0 USD/GJ in every year from 2021 to 2050. '
                 'Reason: municipalities collect this waste whether or not it is used for energy, so its energy use adds no fuel cost. '
                 'Check: the CCG Ecuador kit has no waste fuel cost and prices only biomass, at 5.6 USD/GJ in 2020 USD. '
                 'Range: 0 to 6.8 USD/GJ, the biomass supply cost in 2024 USD.'),
}
for y in YEARS:
    add('DIST_CHA', 'VariableCost', y, 2 * minbio, 'CCG-002;CCG-008;BEN-004', f'2 x CCG MINBIO 5.6 USD/GJ (2020 USD) x {F20:.6f}', basis='ASSUMPTION', assumption=A_CHA, unit='MUSD/PJ (= USD/GJ)')
    for t, a in A_ZERO.items():
        add(t, 'VariableCost', y, 0.0, 'CCG-002;ECU-004;PMC-002;PMC-003' if t != 'DIST_RDF' else 'CCG-002;CCG-008', 'set to 0: see ASSUMPTION', basis='ASSUMPTION', assumption=a, unit='MUSD/PJ (= USD/GJ)')

A_GRE = ('ASSUMPTION: refinery gas (ADD_GRE) has capital, fixed and variable costs of 0 in every year from 2021 to 2050. '
         'Reason: refinery gas is a by-product of crude refining, and its cost is already carried by the crude supply and refinery rows. '
         'Check: the CCG Ecuador kit puts refinery costs on the refinery technology only and has no separate refinery gas cost (UPSREF001, UPSREF002). '
         'Range: 0 to 3.4 USD/GJ, the domestic natural gas price, if it were valued as a gas substitute.')
for y in YEARS:
    for par in ('CapitalCost', 'FixedCost', 'VariableCost'):
        add('ADD_GRE', par, y, 0.0, 'CCG-002', 'set to 0: see ASSUMPTION', basis='ASSUMPTION', assumption=A_GRE, unit='MUSD per unit of capacity' if par != 'VariableCost' else 'MUSD/PJ')

# Transmission and distribution: CCG, capacity in PJ/yr in our model (CapacityToActivityUnit 1)
for t, cc, pm in (('ELE_TRANS', 'PWRTRN', 'ELE_TRANS'), ('ELE_DIST', 'PWRDIST', 'ELE_DISTR')):
    for y in YEARS:
        v, loc = ccg_val(cc, 'CapitalCost', y)
        pv = pmc_val(pm, 'CapitalCost', y)
        add(t, 'CapitalCost', y, v * F20 / C2A, 'CCG-002;BEN-004;GEN-003',
            f'CCG kit {cc} CapitalCost {y} = {v:g} USD/kW (2020 USD; {loc}) x CPI {F20:.6f} / 31.536 PJ per GW-year (our capacity unit is PJ/yr) = {v * F20 / C2A:.4f} MUSD per PJ/yr',
            pmcv=(pv / C2A if pv is not None else None), pmcode=pm + ' (converted /31.536)', pmsrc='no code', unit='MUSD per PJ/yr')
        for par in ('FixedCost', 'VariableCost'):
            v2, loc2 = ccg_val(cc, par, y)
            add(t, par, y, 0.0, 'CCG-002', f'CCG kit {cc} {par} {y} = {v2:g} ({loc2}), a solver placeholder for zero; proposed 0', pmcv=None, pmcode=pm, unit='MUSD per PJ/yr per year' if par == 'FixedCost' else 'MUSD/PJ')

# Refinery rows: VariableCost only (capital and fixed are EMPTY in the workbook; not proposed)
for t in ('REF_DSL', 'REF_FOI', 'REF_GSL', 'REF_JET', 'REF_LPG', 'REF_OPE'):
    pm = {'REF_DSL': 'REFCRUDSL', 'REF_FOI': 'REFCRUFOI', 'REF_GSL': 'REFCRUGSL', 'REF_JET': 'REFCRUKJF', 'REF_LPG': 'REFCRULPG', 'REF_OPE': None}[t]
    for y in YEARS:
        v, loc = ccg_val('UPSREF001', 'VariableCost', y)
        add(t, 'VariableCost', y, v * F20, 'CCG-002;CCG-006;CCG-014;BEN-004',
            f'CCG kit UPSREF001 (Crude Oil Refinery Option 1, article Table 23) VariableCost {y} = {v:g} USD/GJ of output (2020 USD; {loc}) x CPI {F20:.6f}',
            pmcv=pmc_val(pm, 'VariableCost', y), pmcode=pm or '', pmsrc='none', unit='MUSD/PJ (= USD/GJ)')

# PLANMICC rows without a CCG counterpart
for t, pm, conv, note in (('PROCRU', 'PROCRU', C2A, 'our PROCRU capacity unit is 31.536 PJ per unit (CapacityToActivityUnit 31.536), PLANMICC uses 1'),
                          ('PRONGS', 'PRONGS', 1.0, 'both models use 1 PJ/yr per unit of capacity'),
                          ('HYD_G_PROD', 'HYDPROELEGRI', 1.0, 'both models use 1 PJ/yr per unit of capacity'),
                          ('HYD_DIST', 'HYD_DISTR', 1.0, 'both models use 1 PJ/yr per unit of capacity')):
    for y in YEARS:
        for par in ('CapitalCost', 'FixedCost', 'VariableCost'):
            pv = pmc_val(pm, par, y)
            f = conv if par != 'VariableCost' else 1.0
            prop = (pv or 0.0) * f
            der = (f'PLANMICC compiled {pm} {par} {y} = {pv:g} x {f:g} ({note if f != 1 else "no unit change"}) = {prop:.4f}; currency year not stated by PLANMICC, used as published'
                   if pv is not None else f'PLANMICC compiled BAU has no {par} for {pm}; proposed 0')
            src = {'CapitalCost': 'PMC-001', 'FixedCost': 'PMC-002', 'VariableCost': 'PMC-003'}[par] + ';PMC-007;PMC-008'
            add(t, par, y, prop, src, der, pmcv=(pv * f if pv is not None else None), pmcode=pm + (f' (x{f:g})' if f != 1 else ''), pmsrc={'PROCRU': '6 (petroleum sheet)', 'PRONGS': '10 (petroleum sheet)', 'HYDPROELEGRI': '4 (petroleum sheet)', 'HYD_DISTR': 'none'}[pm],
                unit='MUSD per unit of capacity' if par != 'VariableCost' else 'MUSD/PJ')

# Electricity imports (Step 6)
IMP = {2021: (9.28, 363.80), 2022: (27.69 + 0.0266, 465.30 + 0.53), 2023: (281.31 + 4.57, 1296.58 + 24.37), 2024: (334.501312880, 1269.56411)}
imp_obs = {y: (m / g) * 1000 * 0.27778 * cpi[2024] / cpi[y] for y, (m, g) in IMP.items()}  # MUSD/GWh -> USD/MWh -> USD/GJ, real
for y, (m, g) in IMP.items():
    const.append((f'ECU_IMPELE_{y}', round(m / g * 1000, 2), 'USD/MWh nominal (total paid / energy imported, Colombia and Peru)',
                  'ECU-020;ECX-001', 'ARCONEL Estadistica 2024 Tablas 145 to 148, PDF p.138-139; CENACE Informe Anual 2024 Tabla 2.4', f'{m:.4f} MUSD / {g:.2f} GWh'))
A_IMP = (f'ASSUMPTION: electricity imports (IMPELE, from Colombia and Peru) cost {imp_obs[2024]:.2f} USD/GJ ({imp_obs[2024] / 0.27778:.1f} USD/MWh) in real 2024 USD in every year from 2025 to 2050, the price Ecuador paid on average in 2024. '
         'Reason: the latest full year paid is used as the level for all later years. '
         f'Check: Ecuador paid {IMP[2021][0] / IMP[2021][1] * 1000:.1f} USD/MWh in 2021, {IMP[2022][0] / IMP[2022][1] * 1000:.1f} in 2022 and {IMP[2023][0] / IMP[2023][1] * 1000:.1f} in 2023 (ARCONEL, Estadistica Anual y Multianual del Sector Electrico 2024, Tablas 145 to 148), so the 2024 level reflects the 2023-2024 drought. '
         f'Range: {imp_obs[2021]:.1f} to {imp_obs[2024]:.1f} USD/GJ (2021 to 2024, real 2024 USD).')
A_IMP_CF = ('ASSUMPTION: IMPELE (electricity imports) has capital cost 0 and fixed cost 0 in every year from 2021 to 2050. '
            'Reason: the import row carries the price paid per unit of energy, which settles the cross-border exchange; the interconnection lines are not part of this row. '
            'Check: ARCONEL reports imports as energy and a total amount paid, with no capacity charge (Estadistica 2024, Tabla 148). Range: 0.')
for y in YEARS:
    if y in imp_obs:
        add('IMPELE', 'VariableCost', y, imp_obs[y], 'ECU-020;ECX-001;BEN-004;GEN-003',
            f'{IMP[y][0]:.4f} MUSD / {IMP[y][1]:.2f} GWh = {IMP[y][0] / IMP[y][1] * 1000:.2f} USD/MWh x 0.27778 x CPI 2024/{y}', basis='observed', unit='MUSD/PJ (= USD/GJ)',
            pmcv=pmc_val('IMPELE', 'VariableCost', y), pmcode='IMPELE', pmsrc='none')
    else:
        add('IMPELE', 'VariableCost', y, imp_obs[2024], 'ECU-020;ECX-001;BEN-004;GEN-003', 'held at the 2024 value: see ASSUMPTION', basis='ASSUMPTION',
            assumption=A_IMP, unit='MUSD/PJ (= USD/GJ)', pmcv=pmc_val('IMPELE', 'VariableCost', y), pmcode='IMPELE', pmsrc='none')
    for par in ('CapitalCost', 'FixedCost'):
        add('IMPELE', par, y, 0.0, 'ECU-020', 'set to 0: see ASSUMPTION', basis='ASSUMPTION', assumption=A_IMP_CF, unit='MUSD per unit of capacity')

pc = pd.DataFrame(rows)
pc.to_csv(os.path.join(job, 'plant_costs.csv'), index=False)
pd.DataFrame(mapping).to_csv(os.path.join(job, 'mapping_ECU.csv'), index=False)
pd.DataFrame(const, columns=['name', 'value', 'unit', 'source_id', 'page_or_table', 'derivation']).to_csv(os.path.join(X, 'constants_plant.csv'), index=False)
print(len(pc), pc.groupby(['change_class', 'basis_class']).size())
print('techs', pc.technology.nunique())
