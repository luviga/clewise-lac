"""R4 (currency year of 109 groups) and R5 (304 matched cells in 53 mixed groups).

For every cell in scope: take the source value and the currency year of the source
the value comes from, convert to real 2024 USD with CPI-U annual averages
(BLS CUUR0000SA0, downloads/r4/bls_v2_cpiu_*.json) and compare with the workbook
value at the base commit. Writes scripts/r4r5_cells.csv.
Run: py -I scripts/r4r5_build.py <ao_index.pkl>
"""
import json, re, sys
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z/'
HUB = 'C:/clw_fix/_LAC_HUB/'

cpi = {}
for f in ['bls_v2_cpiu_2010_2019.json', 'bls_v2_cpiu_2016_2025.json']:
    d = json.load(open(JOB + 'downloads/r4/' + f))
    for x in d['Results']['series'][0]['data']:
        if x['period'] == 'M13':
            cpi[int(x['year'])] = float(x['value'])
assert cpi[2024] == 313.689 and cpi[2010] == 218.056 and cpi[2025] == 321.943


def fac(cy):
    return cpi[2024] / cpi[cy]


idx = pd.read_pickle(sys.argv[1])
p = pd.read_csv(HUB + 'cost_review_20261111T015203Z/proposals_all.csv', low_memory=False)
p = p[p.fuel_scenario.isin(['ALL', 'STEPS'])]
c = pd.read_csv(HUB + 'cost_write_run_20261111T071733Z/currency_conversion.csv')
m4 = c.left.fillna('').str.contains('not stated|mixed|ambiguous|2025 USD|2010|PEIG 2026-2050')
R4 = set(map(tuple, c[m4][['country', 'tech', 'parameter']].values))
r5 = pd.read_csv(JOB + 'scripts/r5_matched_scratch.csv')
R5 = set(map(tuple, r5[['country', 'Tech', 'Parameter']].drop_duplicates().values))
R5cells = set(map(tuple, r5[['country', 'Tech', 'Parameter', 'year']].values))

# Currency-year statements found in the source documents (sources.csv in the job folder).
ASSUME = {
    'PEN': ("PEN 2022-2036 (CSD-008) states no currency year for Tablas 220, 223 and 229 (only 'Fuente: Comision Nacional de Energia, 2021'); "
            "the PDF was created on 2022-08-05", 2021),
    'PEIG': ("PEIG 2026-2050 (NAT-001) states no currency year for Tabla 6 (the only year reference is the 2024 exchange rate); "
             "the PDF was created on 2026-01-12", 2025),
    'PLANMICC': ("PLANMICC compiled files and their cost workbook (PMC-001 to PMC-003, PMC-008) state no currency year; "
                 "the repository version used was committed on 2024-09-24", 2023),
}


def assumption_sentence(key, tech, par, val24):
    why, cy = ASSUME[key]
    return (f"ASSUMPTION: the currency year of {tech} {par} is {cy}, the year before the source was published, "
            f"so the value is converted to real 2024 USD with CPI-U 2024/{cy} = {fac(cy):.6f}. Reason: {why}; "
            f"costs in a plan are normally stated in the prices of the year the work was done, which is the year before publication.")


# Group-level currency years for the R4 groups (source of the value actually written; see GAPS).
G = {}
for t in ['PPADSL', 'PPAFOI', 'PPANGS', 'PPCCTNGS', 'PPDBGS', 'PPDBIM', 'PPDDSL', 'PPDFOI', 'PPDGLP', 'PPDGSL', 'PPDNGS', 'PPICEGASFOI']:
    for par in ['CapitalCost', 'FixedCost', 'VariableCost']:
        G[('DominicanRepublic', t, par)] = ('PEN', 2021)
for t in ['PPCCTDSL', 'PPICEFOI', 'PPCOA']:
    for par in ['CapitalCost', 'FixedCost', 'VariableCost']:
        G[('DominicanRepublic', t, par)] = ('PEN', 2021)
G[('DominicanRepublic', 'PPBIM', 'FixedCost')] = ('PEN', 2021)
G[('DominicanRepublic', 'PPBIM', 'VariableCost')] = ('PEN', 2021)
G[('DominicanRepublic', 'PPBGS', 'FixedCost')] = ('ATB2024', 2022)
G[('DominicanRepublic', 'PPBGS', 'VariableCost')] = ('IRENA2022', 2022)
G[('DominicanRepublic', 'PPDHYD', 'FixedCost')] = ('IRENA2022', 2022)
for t in ['PPPVT', 'PPPVTHYD', 'PPWNDON']:
    G[('DominicanRepublic', t, 'CapitalCost')] = ('IRENA2022xATB2024', 2022)
    G[('DominicanRepublic', t, 'FixedCost')] = ('ATB2024', 2022)
for t, par in [('PPHDAM', 'CapitalCost'), ('PPHDAM', 'FixedCost'), ('PPPVD', 'CapitalCost'), ('PPPVD', 'FixedCost')]:
    G[('DominicanRepublic', t, par)] = ('ROW', None)  # per row: ATB 2023 (2021$) or ATB 2024 (2022$)
for t in ['HYD_DIST', 'HYD_G_PROD', 'PROCRU', 'PRONGS']:
    for par in ['CapitalCost', 'FixedCost', 'VariableCost']:
        G[('Ecuador', t, par)] = ('PLANMICC', 2023)
G[('Guatemala', 'IMP_ELE', 'VariableCost')] = ('AMM2024', 2024)
G[('Guatemala', 'PPBGS', 'VariableCost')] = ('PEG2020', 2020)
G[('Guatemala', 'PPCOA', 'CapitalCost')] = ('WEO2025', 2024)
for t, par in [('PPBIM', 'CapitalCost'), ('PPBIM', 'FixedCost'), ('PPDSL', 'CapitalCost'), ('PPDSL', 'FixedCost'), ('PPDSL', 'VariableCost'),
               ('PPFOI', 'CapitalCost'), ('PPGEO', 'FixedCost'), ('PPGEO', 'VariableCost'), ('PPHDAM', 'FixedCost'), ('PPNGS', 'FixedCost'),
               ('PPNGS', 'VariableCost'), ('PPPVT', 'FixedCost'), ('PPWNDON', 'FixedCost')]:
    G[('Guatemala', t, par)] = ('PEIG', 2025)
for k in R4:
    if k[0] == 'Honduras':
        G[k] = ('PIEG2024T7', 2023)  # only rows whose derivation cites Tabla 7 without the 2026-2035 path
G[('Jamaica', 'PPBGS', 'VariableCost')] = ('IRENA2025', 2025)
G[('Jamaica', 'PPBIM', 'VariableCost')] = ('IRENA2025', 2025)
G[('Jamaica', 'PPGEO', 'FixedCost')] = ('IRENA2025', 2025)
G[('Jamaica', 'PPNGS', 'CapitalCost')] = ('OUR2010', 2010)
for t, par in [('PPPVDS', 'CapitalCost'), ('PPPVDS', 'FixedCost'), ('PPWNDONS', 'CapitalCost'), ('PPWNDONS', 'FixedCost')]:
    G[('Jamaica', t, par)] = ('MIXED', None)
missing = [k for k in R4 if k not in G]
assert not missing, missing

num = r'([0-9][0-9,]*\.?[0-9]*)'


def f(x):
    return float(x.replace(',', ''))


def row_source(country, tech, par, year, r):
    """Return (source_value, currency_year, note) for one proposals_all row."""
    der = str(r.derivation)
    bc = r.basis_class
    k = (country, tech, par)
    if k in R4:
        kind, cy = G[k]
        if kind == 'ROW':
            txt = der.split('newer edition', 1)[1] if 'newer edition' in der else der
            cy = 2022 if 'ATB 2024' in txt else 2021 if 'ATB 2023' in txt else None
            if bc == 'matched':
                mm = re.search(r'gives ' + num, der)
                return f(mm.group(1)), cy, 'matched cell: source value from the derivation'
            return float(r.proposed_value), cy, 'proposed value'
        if kind == 'MIXED':
            mm = re.search(r'(PPPVD|PPWNDON) proposed ' + num + r' \+ battery ' + num + r' x ATB 4Hr battery (CAPEX|Fixed O&M) ' + num + ' / ' + num + ' = ' + num, der)
            a, b, idxy, idx0 = f(mm.group(2)), f(mm.group(3)), f(mm.group(5)), f(mm.group(6))
            batt = b * idxy / idx0
            if mm.group(1) == 'PPPVD':
                cy_a = 2022
            else:
                cy_a = 2024 if par == 'CapitalCost' else 2018
            v24 = a * fac(cy_a) + batt * fac(2018)
            return v24, 2024, (f'mixed: {mm.group(1)} part {a} ({cy_a} USD) x {fac(cy_a):.6f} + battery part {b} x {idxy}/{idx0} = {batt:.4f} '
                               f'(2018 USD, 2018 IRP p.107) x {fac(2018):.6f}')
        if bc == 'matched':
            if kind == 'PEN':
                mm = re.search(r'gives ' + num, der)
                if mm:
                    return f(mm.group(1)), cy, 'matched cell: source value from the derivation'
            if kind == 'PEIG':
                mm = re.search(r'row [A-Za-z ]+ ' + num + r' USD/kW', der)
                return f(mm.group(1)), cy, 'matched cell: PEIG Tabla 6 value'
            if kind == 'OUR2010':
                mm = re.search(r'combined cycle ' + num + ' USD/kW', der)
                return f(mm.group(1)), cy, 'matched cell: OUR 2010 value'
            if kind == 'PEG2020':
                return float(r.proposed_value), cy, 'proposed value (PEG 5 USD/MWh / 3.6)'
            return float(r.proposed_value), cy, 'proposed value'
        if kind == 'PIEG2024T7':
            if 'Tabla 7' in der and ('2026-2035' not in der and 'HON-016' not in str(r.source_ids)):
                return float(r.proposed_value), 2023, 'PIEG 2024-2033 Tabla 7 value (2023 prices)'
            return float(r.proposed_value), 2024, 'already 2024 USD'
        return float(r.proposed_value), cy, 'proposed value'
    # R5-only groups: matched cells only
    mm = re.search(r'within 2 percent of the source value ' + num, der)
    if mm:
        return f(mm.group(1)), 2024, 'source value already in 2024 USD'
    mm = re.search(r'current ' + num + r' equals ATB (20\d\d) [^=]+= ' + num + r' \((20\d\d) USD\)', der)
    if mm:
        a, b = f(mm.group(1)), f(mm.group(3))
        if abs(a - b) <= 0.0051:  # printed to 2 decimals: the cell already holds the source value
            return float(r.current_value), int(mm.group(4)), f'ATB {mm.group(2)} value (equals the current value at full precision)'
        return b, int(mm.group(4)), f'ATB {mm.group(2)} value'
    mm = re.search(r'year (20\d\d) source value ' + num, der)
    if mm and int(mm.group(1)) == year:
        cyv = re.search(r'\((20\d\d) USD\)\s*x CPIU_(20\d\d)/CPIU_(20\d\d)', der)
        cy = int(cyv.group(2)) if cyv else int(re.search(r'\((20\d\d) USD\)', der).group(1))
        return f(mm.group(2)), cy, 'source value of the year'
    mm = re.search(r'within 2 percent of ' + num + r'\)', der)
    if mm and '2018 USD' in der:
        return f(mm.group(1)), 2018, '2018 IRP value'
    mm = re.search(r'wind ' + num + r' USD/kW \(2018 USD\)', der)
    if mm:
        return f(mm.group(1)), 2018, '2018 IRP value'
    mm = re.search(r': ' + num + r' USD/kW(-yr)? \((20\d\d) USD\)', der)
    if mm:
        return f(mm.group(1)), int(mm.group(3)), 'stated value'
    if 'Tabla 7' in der:
        return float(r.proposed_value), 2023, 'PIEG 2024-2033 Tabla 7 value (2023 prices)'
    return None, None, 'UNPARSED'


rows = []
keys = sorted(R4 | R5)
for k in keys:
    country, tech, par = k
    w = idx[(idx.country == country) & (idx.tech == tech) & (idx.parameter == par)]
    assert len(w) == 1, k
    w = w.iloc[0]
    d = p[(p.country == country) & (p.Tech == tech) & (p.Parameter == par)].set_index('year')
    years = [y for y in d.index]
    for y in years:
        r = d.loc[y]
        if isinstance(r, pd.DataFrame):
            r = r[r.fuel_scenario == 'STEPS'].iloc[0] if (r.fuel_scenario == 'STEPS').any() else r.iloc[0]
        in4 = k in R4
        in5 = (country, tech, par, y) in R5cells
        if not in4 and not in5:
            continue
        sv, cy, note = row_source(country, tech, par, y, r)
        if (country, tech, par, y) == ('Guatemala', 'PPPVD', 'FixedCost', 2021):
            sv, note = 17.854389, 'ATB 2021 CommPV Class5 Fixed O&M 2021 = 17.854389 (2019 USD), exact value read in NREL_ATB2021_ATBe.csv (the derivation prints 17.85)'
        wbv = w.get(y)
        if sv is None:
            rows.append(dict(country=country, sheet=w.sheet, row=w['row'], tech=tech, parameter=par, year=y, wb_value=wbv,
                             source_value=None, currency_year=None, factor=None, new_value=None, rule='R4' if in4 else 'R5',
                             basis_class=r.basis_class, note=note, derivation_src=str(r.derivation), source_ids=r.source_ids))
            continue
        nv = sv * fac(cy)
        rule = 'R4+R5' if (in4 and in5) else 'R4' if in4 else 'R5'
        rows.append(dict(country=country, sheet=w.sheet, row=w['row'], tech=tech, parameter=par, year=y, wb_value=wbv,
                         source_value=sv, currency_year=cy, factor=fac(cy), new_value=nv, rule=rule, basis_class=r.basis_class,
                         note=note, derivation_src=str(r.derivation), source_ids=r.source_ids, mode=w['mode']))
o = pd.DataFrame(rows)
ws = pd.read_csv(HUB + 'cost_write_run_20261111T071733Z/write_set.csv', low_memory=False)
reg = set(map(tuple, ws[ws.rule == 'regional'][['country', 'tech', 'parameter', 'year']].values))
o['regional_in_pr10'] = [ (a, b, c, d) in reg for a, b, c, d in o[['country', 'tech', 'parameter', 'year']].values ]
o.loc[o.regional_in_pr10 & (o.rule == 'R5'), 'new_value'] = o.loc[o.regional_in_pr10 & (o.rule == 'R5'), 'wb_value']
o.loc[o.regional_in_pr10 & (o.rule == 'R5'), 'note'] = 'not written: PR #10 already wrote a regional sourced value (regional_proposals) into this cell'
o['wb_num'] = pd.to_numeric(o.wb_value, errors='coerce')
o['changes'] = ~((o.new_value - o.wb_num).abs() <= 1e-9 * o.new_value.abs().clip(lower=1e-12))
o.to_csv(JOB + 'scripts/r4r5_cells.csv', index=False)
print('cells', len(o), 'unparsed', o.new_value.isna().sum(), 'changing', o.changes.sum())
print(o.groupby(['country', 'rule']).agg(n=('year', 'size'), changing=('changes', 'sum')))
s = o.groupby(['country', 'tech', 'parameter']).agg(cy=('currency_year', lambda x: ','.join(map(str, sorted(set(x.dropna().astype(int)))))),
                                                    n=('year', 'size'), ch=('changes', 'sum'),
                                                    wb0=('wb_num', 'first'), new0=('new_value', 'first'), wb1=('wb_num', 'last'), new1=('new_value', 'last'))
pd.set_option('display.width', 250)
print(s.to_string())
