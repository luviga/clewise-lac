"""Step 2 follow-up: rewrite the needed_change column of paper_trace.csv from the final proposals
(the first pass was written before the plant and import results existed).
Usage: py -I s2b_update_paper_trace.py <job folder>"""
import os, sys
import pandas as pd

J = sys.argv[1]
pt = pd.read_csv(os.path.join(J, 'paper_trace.csv'), dtype=str).fillna('')
s = pd.read_csv(os.path.join(J, 'proposals_summary.csv'))
fs = pd.read_csv(os.path.join(J, 'work', 'fuel_summary.csv')).set_index('row')
pc = pd.read_csv(os.path.join(J, 'plant_costs.csv'))

POINT = {'DIST_COA': 'Banco de Guatemala customs import CIF', 'DIST_COK': 'Banco de Guatemala customs import CIF',
         'DIST_DSL': 'MEM price structure wholesale import parity (pre-tax)', 'DIST_FOI': 'MEM bunker structure ex-rack price (pre-tax)',
         'DIST_GSL': 'MEM price structure wholesale import parity for regular gasoline (pre-tax)',
         'DIST_LPG': 'MEM 25 lb cylinder structure wholesale import parity (pre-tax)', 'DIST_KER': 'MEM Guatemala City consumer price net of taxes',
         'EXTT_CRU': 'Banco de Guatemala customs export FOB'}
BENCH = {'coal': 'Atlantic steam coal (World Bank) and the WEO 2025 European Union steam coal price', 'brent': 'Brent and the WEO 2025 IEA crude oil price',
         'hh': 'Henry Hub and the WEO 2025 United States gas price'}

def fuel_text(code, old):
    r = fs.loc[code]
    if code == 'DIST_NGS':
        head = (f'Replace {old} M USD/PJ with an ASSUMPTION of 7.763 USD/GJ gross (8.626 USD/GJ net after dividing by 0.9) for 2024, '
                f'Henry Hub plus liquefaction, shipping and regasification, since Guatemala imports no natural gas')
    else:
        head = f'Replace {old} M USD/PJ with the 2024 {POINT[code]}, {r.value_2024:.2f} USD/GJ net in real 2024 USD'
    return (f'{head}, with observed or ratio-based history to 2025 and projections scaled by {BENCH[r.benchmark]} '
            f'(STEPS {r.STEPS_2030:.2f} in 2030 and {r.STEPS_2050:.2f} in 2050; CPS {r.CPS_2050:.2f}, NZE {r.NZE_2050:.2f} in 2050), and cite the sources.')

def short_src(t, p):
    g = pc[(pc.technology == t) & (pc.parameter == p) & (pc.year == 2024)].iloc[0]
    return g['class']

def plant_text(t):
    parts = []
    for p, lab in (('CapitalCost', 'Capital'), ('FixedCost', 'Fixed'), ('VariableCost', 'Variable Cost')):
        g = s[(s.Tech == t) & (s.Parameter == p)].iloc[0]
        cls = short_src(t, p)
        cur, new = g.current_2024, g.proposed_2024
        unit = ' M USD/PJ (USD/GJ)' if p == 'VariableCost' else ''
        if p == 'VariableCost' and cur not in (0,) and not pd.isna(cur):
            parts.append(f'{lab} {cur:g} M USD/GWh (USD/kWh) becomes {new:.3f}{unit} ({cls})')
        elif abs((new or 0) - (cur if not pd.isna(cur) else 0)) < 1e-6:
            parts.append(f'{lab} {new:g}{unit} kept ({cls})')
        else:
            parts.append(f'{lab} {cur if not pd.isna(cur) else 0:g} becomes {new:g}{unit} in 2024 ({cls})')
        if t in ('PPPVT2', 'PPPVTS', 'PPPVD', 'PPPVDS') and p != 'VariableCost':
            parts[-1] += f', path to {g.proposed_2050:g} in 2050'
    src = ';'.join(sorted({x for x in pc[pc.technology == t].source_ids.str.split(';').sum()}))
    return '2024 values: ' + '; '.join(parts) + f'. Name the source documents and editions (source ids {src}) and the dollar year of each value.'

GEN = {
    2: 'Say that fuel prices are in real 2024 USD per GJ net with trajectories from observed national series and IEA WEO 2025 scenario ratios, and that plant costs are given in the dollar year of each cited source.',
    3: 'Replace "current USD without deflation" with: fuel prices in real 2024 USD; plant costs as published by each cited IRENA, IEA WEO, national plan, EIA or NREL ATB edition, in that edition\'s dollar year; plant variable costs in M USD/PJ (USD/GJ).',
    35: 'Add that fuel prices are in real 2024 USD per GJ net (M USD/PJ), plant costs are in the dollar year of each cited source, and plant variable costs are in M USD/PJ.',
    42: 'Add "fuel prices and technology costs" to Inputs and "convert fuel prices to real 2024 USD per GJ net and plant variable costs to USD/GJ" to Processing.',
    43: 'Add that power plant costs are sourced to named IRENA, IEA WEO, Guatemalan national plan, EIA and NREL ATB editions, plant variable costs are in USD/GJ, and fuel supply rows carry pre-tax import or wholesale prices projected with IEA WEO 2025 scenarios.',
    47: 'Add that fuel costs are pre-tax import or wholesale prices in real 2024 USD projected from IEA WEO 2025, that plant costs carry the dollar year of each source, and state the discount rate, which the draft does not give.',
    54: 'Update together with Table 57: add a source column, the dollar year of each plant value, corrected plant variable costs in M USD/PJ, the new fuel prices, and rows for Import - Electricity, Kerosene, Petroleum coke and Crude oil export.',
}
n = 0
for i, r in pt.iterrows():
    code = r.model_rows.strip()
    if r.table_or_figure == 'Table 57' and code == 'ALL' or ('Costos_GUA' in r.table_or_figure and code.startswith('ALL')):
        pt.at[i, 'needed_change'] = GEN[54]; n += 1
    elif code in fs.index:
        old = [w for w in r.statement_as_written.replace('|', ' ').split() if w.replace('.', '', 1).isdigit()]
        pt.at[i, 'needed_change'] = fuel_text(code, old[0] if old else 'the current value'); n += 1
    elif code in set(s.Tech) and code.startswith('PP'):
        pt.at[i, 'needed_change'] = plant_text(code); n += 1
    elif i in GEN:
        pt.at[i, 'needed_change'] = GEN[i]; n += 1
pt.loc[pt.needed_change.str.contains('IMP_ELE, published 2024 region', regex=False), 'needed_change'] = GEN[54]
pt.to_csv(os.path.join(J, 'paper_trace.csv'), index=False)
print('rewritten', n)
