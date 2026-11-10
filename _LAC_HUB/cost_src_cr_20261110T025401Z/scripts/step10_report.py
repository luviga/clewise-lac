"""Write REPORT_LAC_COST_SRC_CR_<stamp>.md from the job outputs.
Usage: py -I step10_report.py <job folder> <pr text> <branch> <commit text>"""
import os, sys
import pandas as pd

JOB, PR, BR, COMMIT = sys.argv[1:5]
ST = '20261110T025401Z'
fs = pd.read_csv(os.path.join(JOB, 'scripts', 'fuel_summary.csv'))
ps = pd.read_csv(os.path.join(JOB, 'proposals_summary.csv'))
pc = pd.read_csv(os.path.join(JOB, 'plant_costs.csv'))
prop = pd.read_csv(os.path.join(JOB, 'proposals.csv'))
pt = pd.read_csv(os.path.join(JOB, 'paper_trace.csv'))
gp = os.path.join(JOB, 'gate_results_post.txt')
gates = open(gp, encoding='utf-8').read() if os.path.exists(gp) else open(os.path.join(JOB, 'gate_results_pre.txt'), encoding='utf-8').read()


def f(v, d=2):
    return '' if pd.isna(v) else ('%.*f' % (d, v))


L = []
L.append('# REPORT LAC_COST_SRC_CR %s\n' % ST)
L.append('Costa Rica energy model: sourced cost proposals for power plants and fuel supply rows. No model file changed.\n')
L.append('- Pull request: %s' % PR)
L.append('- Branch: `%s`, from `2ddd560`' % BR)
L.append('- Commit: %s\n' % COMMIT)
L.append('## Gates\n')
for g in gates.strip().split('\n'):
    L.append('- ' + g)
L.append('\nCounts: `proposals.csv` has %d rows:' % len(prop))
L.append('- 810 fuel rows: 9 supply rows x 3 scenarios x 30 years;')
L.append('- 900 plant rows: 10 plants x 3 parameters x 30 years;')
L.append('- 30 rows for the import technology `IMPELE`.\n')
L.append('By change class: %s.\n' % ', '.join('%s %d' % kv for kv in prop.change_class.value_counts().items()))
L.append('By basis class: %s.\n' % ', '.join('%s %d' % kv for kv in prop.basis_class.value_counts().items()))
L.append('## Fuel supply rows\n')
L.append('Values in USD/GJ (= MUSD/PJ), net calorific basis, real 2024 USD. r cases:')
L.append('- A: the chosen point has history;')
L.append('- B: wholesale import parity, with r from the import CIF history times the 2024 ratio to CIF;')
L.append('- C: no history, so the 2024 ratio alone.\n')
L.append('The step at the join is STEPS 2026 minus 2025 (2025 = history from the observed 2025 benchmark).\n')
L.append('| Row | Chosen point | 2024 value | Current 2024 | r (case) | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join 2025 to 2026 |')
L.append('|---|---|---|---|---|---|---|---|---|---|')
for _, r in fs.iterrows():
    c = ps[(ps.Tech == r.row) & (ps.Parameter == 'VariableCost')].iloc[0].current_2024
    L.append('| %s | %s | %.3f | %s | %.4f (%s) | %.3f | %.3f | %.3f | %.3f | %+.3f (%+.1f%%) |' % (
        r.row, r.chosen_point, r.v2024, f(c, 3) if pd.notna(c) else 'empty', r.r, r.r_case, r.steps2030, r.steps2050, r.cps2050, r.nze2050, r.join_step, r.join_step_pct))
L.append('\nBenchmarks:')
L.append('- Oil products and petroleum coke: EIA Brent (RBRTE) with the WEO 2025 IEA crude oil price.')
L.append('- `IMPNGS`: Henry Hub with the WEO United States gas price.')
L.append('- `IMPCOA`: World Bank South African coal with the WEO European Union steam coal price.\n')
L.append('WEO 2025 fuel price table: Table 2.3, PDF page 109, USD (MER, 2024).\n')
L.append('## Power plants (2024)\n')
L.append('CapitalCost in USD/kW, FixedCost in USD/kW-yr, VariableCost in USD/GJ. These are 2024 column values, on the workbook basis of 2022 USD.\n')
L.append('| Technology | CapitalCost current to proposed | FixedCost current to proposed | VariableCost current to proposed | P2 class (Cap / Fix / Var) | Main source |')
L.append('|---|---|---|---|---|---|')
MAIN = {'PP_SPV_DG': 'NREL ATB 2024 ResPV', 'PWRBMS': 'IRENA RPGC 2022 and 2024; ICE PEG 2020-2035', 'PWRDSL': 'ICE PEG 2020-2035 (MMV engines)',
        'PWRFOI': 'ICE PEG 2020-2035 (MMV engines)', 'PWRGEO': 'ICE PEG 2020-2035; IRENA RPGC 2024', 'PWRHYDDAM': 'NREL ATB 2024 NSD2; ICE PEG 2020-2035',
        'PWRHYDROR': 'ICE PEG 2020-2035', 'PWRSPVDTR': 'IRENA RPGC 2024; ICE PEG 2020-2035', 'PWRSPVTRN': 'ICE PEG 2020-2035; IRENA RPGC 2024',
        'PWRWNONS': 'IRENA RPGC 2024'}
for t in ['PP_SPV_DG', 'PWRBMS', 'PWRDSL', 'PWRFOI', 'PWRGEO', 'PWRHYDDAM', 'PWRHYDROR', 'PWRSPVDTR', 'PWRSPVTRN', 'PWRWNONS']:
    cells, cls = [], []
    for p in ('CapitalCost', 'FixedCost', 'VariableCost'):
        r = pc[(pc.technology == t) & (pc.parameter == p) & (pc.year == 2024)].iloc[0]
        d = 4 if p == 'VariableCost' else 2
        cv = 'empty' if pd.isna(r.current_value) else f(r.current_value, d)
        pv = 'empty' if pd.isna(r.proposed_value) else f(r.proposed_value, d)
        cells.append('%s to %s' % (cv, pv))
        cls.append(r['class'])
    L.append('| %s | %s | %s | %s | %s | %s |' % (t, cells[0], cells[1], cells[2], ' / '.join(cls), MAIN[t]))
L.append('\nHow the workbook builds its plant cost paths: the 2021 value x 1.0800 (CPI-U 2022/2021) x the NREL ATB 2024 shape (y) / (2022), an exact match for `PWRGEO`, `PWRWNONS`, `PWRSPVTRN`, `PWRBMS`, `PWRHYDROR` and `PWRDSL`. Only the 2021 levels needed separate sources. `PWRFOI` CapitalCost 4,650.33 USD/kW has no source; the ICE medium-speed engine overnight cost is 1,300 USD/kW (Dec-2019 USD), 1,488 USD/kW in 2022 USD.\n')
L.append('## Electricity imports\n')
L.append('The brief said Costa Rica has no electricity import technology, but the BAU data has `IMPELE` (output `E1_ELE`). Its annual activity upper limit is 2.245 PJ in 2021, 3.846 PJ in 2024 and 2.827 PJ a year from 2025. It had no cost, so imports up to the limit were free.')
L.append("On Luis's instruction of 10 November 2026 (after the first push), rule E1 was applied:")
L.append('- 2024: observed. ICE DOCSE Informe Anual 2024, page 17: ICE imported 363,748.07 MWh from the regional market for 74,953,098.26 USD (contracts and spot, including the CMORC transmission charge). That is 206.06 USD/MWh = **57.239 USD/GJ**.')
L.append('- 2021 to 2023 and 2025 to 2050: the same value held flat, as an ASSUMPTION. Check: ICE projected 152.66 USD/MWh for 2025, as used by ARESEP; the 2024 price without CMORC is 149.35 USD/MWh.')
L.append('- 30 rows, change class `fill_empty`.')
L.append('- The report total import interchange of 1,068 GWh matches the model 2024 upper limit of 3.846 PJ.' + chr(10))
L.append('## Country task: coal or petroleum coke\n')
L.append('- The MINAE Balance Energetico Nacional 2022 (Tabla 3, PDF p.40) gives industry coal of 0.26 kt, 6.67 TJ, and petroleum coke of 138.6 kt, 3,713.16 TJ.')
L.append('- The model already uses these values: `E5INDCOA` is 0.00667 PJ and `E5INDCOK` is 3.713 PJ in 2022, and coal stays near 0.008 to 0.011 PJ after 2022.')
L.append('- The 0.675 PJ of industry coal appears only in 2021 (`A-O_Demand.xlsx`, `Demand_Projection`, cell M25).')
L.append('- Customs show 2.5 t of anthracite in 2021 and 124,327.9 t of petroleum coke. At the IPCC 32.5 GJ/t, the coke is 4.041 PJ, within 1.2 percent of the model 2021 coke of 4.091 PJ.')
L.append('- So the 0.675 PJ is not coke recorded as coal: coke is already counted.')
L.append('- `structure_proposals.csv` proposes the least change, setting 2021 `E5INDCOA` to 0.00667 PJ, and records the literal move to coke as a non-recommended alternative.')
L.append('- The 2021 balance could not be opened (Cloudflare check).\n')
L.append('## ASSUMPTION rows\n')
a = prop[prop.basis_class == 'ASSUMPTION']
L.append('%d rows: %s.' % (len(a), '; '.join('%s %s %d' % (k[0], k[1], v) for k, v in a.groupby(['Tech', 'Parameter']).size().items())))
L.append('- `IMPNGS`: Costa Rica imports no natural gas. The 2024 delivered small-scale LNG cost of 7.763 USD/GJ gross is the ASSUMPTION, together with the F5 gross-to-net sentence.')
L.append('- Engines: non-fuel variable O&M is unchanged at 4.70 USD/MWh, checked against EIA AEO2023 (6.40 USD/MWh).')
L.append('- `IMPELE`: the 2024 import price is held flat in the other 29 years.\n')
L.append('## Paper trail\n')
for d, g in pt.groupby('document'):
    L.append('- %s: %d statements.' % (d, len(g)))
L.append('\nWhat changes:')
L.append('- Data in Brief Table 49 (and `Suplementary.xlsx` `Costos_CR`) prints 2021 values. Its fuel rows need the 2024 pre-tax import or wholesale prices, and its plant rows need the 2024 values with currency year and source.')
L.append('- Data in Brief section 4.8 needs the editions and tables per technology and the fuel price method (pre-tax import parity, real 2024 USD, WEO 2025 scaling with CPS and NZE as high and low cases).')
L.append('- MethodsX needs one sentence on the fuel price method.')
L.append('- The JCLP draft cost indicators (Delta CAPEX, Delta OPEX, accumulated investment) and `Data_v2.xlsx` `5.CR_Costos` need a rerun after the proposals are written.')
open(os.path.join(JOB, 'REPORT_LAC_COST_SRC_CR_%s.md' % ST), 'w', encoding='utf-8', newline=chr(10)).write('\n'.join(L) + '\n')
print('\n'.join(L))
