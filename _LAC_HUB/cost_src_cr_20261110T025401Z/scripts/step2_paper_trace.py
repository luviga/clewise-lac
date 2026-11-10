"""Step 2: paper trail rows for Costa Rica costs and fuel prices; writes paper_trace.csv.

Reads text extracted (extract_paper.py) from local copies of the CLEWISE papers in downloads/paper.
"""
import csv, os, re, sys
JOB = sys.argv[1]
P = os.path.join(JOB, 'downloads', 'paper')


def lines(name):
    return open(os.path.join(P, name), encoding='utf-8').read().split('\n')


def first8(text):
    t = re.sub(r'^\[P [^\]]*\]\s*', '', text).strip()
    return ' '.join(t.split()[:8])


dib = lines('CLEWISE_DataInBrief.txt')
mx = lines('CLEWISE_MethodsX_v02.txt')
jc = lines('CLEWISE_JCLP_draft_v2.txt')
rows = []


def add(doc, sec, tab, line, statement, model_rows, needs):
    rows.append(dict(document=doc, section_heading=sec, table_or_figure=tab, first_eight_words=first8(line) if line else '',
                     statement_as_written=statement, model_rows=model_rows, needs_to_say=needs))


# Data in Brief
p48 = [l for l in dib if l.startswith('[P ] Technology cost data include')]
add('CLEWISE_DataInBrief.docx', 'Specifications table, Data collection', '', [l for l in dib if l.startswith('Data collection')][0].replace('Data collection |', ''),
    'Compiled from ... international databases (World Bank WDI, FAO FAOSTAT, IRENA, OLADE SIER, UN Population Division).',
    'all cost rows', 'Add the fuel price and cost sources used: ARESEP and PROCOMER for Costa Rica 2024 prices, EIA Brent and Henry Hub, World Bank Pink Sheet, IEA WEO 2025, BLS CPI-U, and the plant cost sources in proposals.csv.')
add('CLEWISE_DataInBrief.docx', '4.8 Technology costs', '', p48[-1],
    'Cost projections incorporate learning curves based on IRENA Renewable Power Generation Costs database and IEA World Energy Outlook assumptions. Country-specific adjustments were applied where national feasibility studies or competitive auction results provided local cost benchmarks.',
    'PP_SPV_DG; PWRBMS; PWRDSL; PWRFOI; PWRGEO; PWRHYDDAM; PWRHYDROR; PWRSPVDTR; PWRSPVTRN; PWRWNONS',
    'Name, per technology, the edition and table each cost and its decline path come from (as in proposals.csv), including the national sources where used.')
add('CLEWISE_DataInBrief.docx', '4.8 Technology costs', 'Tables 49 to 71', p48[-1],
    'Costs in Tables 49-71 are reported as static base-year values in current USD without deflation; time-varying behaviour ... is parameterised separately',
    'all cost rows', 'State that fuel prices are pre-tax import or wholesale prices in real 2024 USD per GJ (net), and give the currency year of each plant cost.')
if len(p48) > 1:
    add('CLEWISE_DataInBrief.docx', 'section 4.7 tail, after Table 23 (duplicate of the 4.8 paragraph placed before the Ecuador emission factor tables)', '', p48[0],
        'Same paragraph as 4.8, truncated after "Cost projections".', 'all cost rows', 'Remove the duplicate or align it with the revised 4.8 text.')
# Table 49 rows
t49 = dib.index('[P ] Table 49. Costs of Energy Sector technologies for Costa Rica')
MAP = {'Import/Distribution - AV Gas': 'IMPAVG', 'Import/Distribution - Coal': 'IMPCOA', 'Import/Distribution - Fuel Oil': 'IMPFOI',
       'Import/Distribution - Kerosene and Jet Fuel': 'IMPKJF', 'Import/Distribution - LPG': 'IMPLPG', 'Import/Distribution - Pure Diesel': 'IMPPURDSL',
       'Import/Distribution - Pure Gasoline': 'IMPPURGSL', 'Solar PV Distributed Generation': 'PP_SPV_DG', 'Geothermal Power Plant': 'PWRGEO',
       'Hydroelectric Dam': 'PWRHYDDAM', 'Hydroelectric Run-of-the-river': 'PWRHYDROR', 'Solar PV in Distribution': 'PWRSPVDTR',
       'Solar PV in Transmission': 'PWRSPVTRN', 'Onshore Wind Power Plant': 'PWRWNONS', 'Power Distribution': 'ELE_DTR', 'Power Transmission': 'ELE_TRN',
       'Green Hydrogen Production - Electrolysis Grid': 'HYDPROELEGRI', 'Hydrogen Distribution': 'HYD_DISTR', 'Biomass Power Plant - Steam Turbine': 'PWRBMS',
       'Diesel Power Plant': 'PWRDSL', 'Fuel Oil Power Plant': 'PWRFOI'}
i = t49 + 3
while not dib[i].startswith('[END TABLE]'):
    cells = [c.strip() for c in dib[i].split('|')]
    tech = MAP.get(cells[0], '?')
    if tech.startswith('IMP'):
        need = ('Replace the 2021 variable cost with the 2024 pre-tax import or wholesale price in real 2024 USD/GJ from proposals.csv (STEPS), and say the path follows the WEO 2025 price ratio.')
        if cells[5] not in ('-', ''):
            need += ' The fixed cost on this supply row is not revised by this job (see GAPS).'
    elif tech.startswith('PWR') or tech.startswith('PP_'):
        need = 'Show the 2024 capital, fixed and variable costs from proposals.csv with their currency year and source (the table prints 2021 values).'
    else:
        need = 'Outside this job\'s scope; no change from this job.'
    add('CLEWISE_DataInBrief.docx', '4.8 Technology costs', 'Table 49. Costs of Energy Sector technologies for Costa Rica', '',
        '%s: capital %s %s; variable %s %s; fixed %s %s' % tuple(cells[:7]), tech, need)
    i += 1
for l in dib:
    if l.startswith('[P ] Data sources were identified through a systematic review'):
        add('CLEWISE_DataInBrief.docx', '5.1 Data source identification', '', l,
            '(4) peer-reviewed literature and grey literature (national energy plans, technology feasibility studies, IDB/UNDP/GIZ project reports) for technology costs',
            'all plant cost rows', 'Add the international cost series used (IRENA, IEA WEO, NREL ATB) and, for fuels, the regulator, customs and benchmark price series.')
    if l.startswith('[P ] For each variable in the dataset, the source was documented'):
        add('CLEWISE_DataInBrief.docx', '5.1 Data source identification', '', l,
            'This source registry is maintained in the data repository as a machine-readable metadata file accompanying the data tables.',
            'all cost rows', 'Point to the source registry that carries each cost value (sources.csv with URL, table and retrieval date).')
    if l.startswith('[P ] The six countries use varying conventions for units'):
        add('CLEWISE_DataInBrief.docx', '5.2 Harmonization and gap-filling', '', l,
            '(a) SI-derived units ... MUSD for costs ... (b) a common base year of 2021 for the projection starting point',
            'all cost rows', 'Add the currency basis (real 2024 USD, deflated with US CPI-U) and that fuel prices use net calorific values.')
for l in dib:
    if l.startswith('[P ] [13] IRENA') or l.startswith('[P ] [14] IEA'):
        add('CLEWISE_DataInBrief.docx', 'References', '', l, re.sub(r'^\[P [^\]]*\]\s*', '', l), 'plant cost rows',
            'Keep, and add IEA WEO 2025, IRENA Renewable Power Generation Costs in 2024, NREL ATB 2024 if used, EIA price series, World Bank Pink Sheet, BLS CPI-U, ARESEP and PROCOMER sources.')
# MethodsX
for l in mx:
    if l.startswith('[P ] The energy and transport template follows standard OSeMOSYS practice'):
        add('CLEWISE_MethodsX_v02.docx', 'Energy and transport template', '', l,
            'Technology lists are populated with country-specific power plants (type, nameplate capacity, efficiency, commissioning and retirement years, capital and operating costs) ... Fuel supply chains are represented from primary resource extraction through transformation',
            'all plant and supply rows', 'Add one sentence on the fuel price method: pre-tax import or wholesale price per country in real 2024 USD/GJ, projected with a multi-year ratio to Brent, Henry Hub or coal times the WEO 2025 scenario price path.')
    if l.startswith('[P ] Additional validation avenues include cross-checking'):
        add('CLEWISE_MethodsX_v02.docx', 'Method validation', '', l,
            'sensitivity analysis on key parameters (land-use transition rates, waste growth, technology costs)', 'all cost rows',
            'Mention the WEO 2025 CPS (high) and NZE (low) fuel price cases as the fuel price sensitivity.')
# JCLP
for l in jc:
    if l.startswith('[P ] CLEWISE is implemented as a linear, least-cost optimization model'):
        add('CLEWISE_JCLP_draft_v2.docx', 'Methods, model formulation', '', l,
            'The model minimizes the discounted sum of investment, operation and maintenance, and fuel costs', 'all cost rows',
            'State that fuel costs are pre-tax import parity prices in real 2024 USD with WEO 2025 STEPS as the central path.')
    if l.startswith('[P ] In addition to the three harmonized scenarios'):
        add('CLEWISE_JCLP_draft_v2.docx', 'Scenario design', '', l,
            'we also compute a least-cost optimization case ... a reference point to interpret how far policy-constrained pathways deviate', 'all cost rows',
            'Results of the least-cost case will change with the revised costs; rerun before reporting.')
    if l.startswith('[P ] In countries like the Dominican Republic, Guatemala, and Jamaica, the ratio'):
        add('CLEWISE_JCLP_draft_v2.docx', 'Results, Delta CAPEX/GDP', 'Figure (Delta CAPEX/GDP)', l,
            'Costa Rica and Ecuador show a similar pattern where the additional capital requirements are negligible or slightly negative relative to GDP.', 'plant CapitalCost rows',
            'Recheck the Costa Rica statement after the model is rerun with the revised costs.')
    if l.startswith('[P ] The ΔOPEX/GDP indicator captures'):
        add('CLEWISE_JCLP_draft_v2.docx', 'Results, Delta OPEX/GDP', 'Figure (Delta OPEX/GDP)', l,
            'Costa Rica shows a marginal increase, suggesting that operational requirements may increase slightly under the mitigation scenarios', 'plant FixedCost and VariableCost rows; supply VariableCost rows',
            'Recheck after rerun: fuel prices rise for most rows, which changes the OPEX difference between BAU and the mitigation scenarios.')
    if l.startswith('[P ] The change in accumulated investment indicator'):
        add('CLEWISE_JCLP_draft_v2.docx', 'Results, accumulated investment', '', l,
            'For Costa Rica and the Dominican Republic, the accumulated investment ratio remains near the zero line', 'plant CapitalCost rows',
            'Recheck after rerun with the revised capital costs.')
# Spreadsheets
add('Suplementary.xlsx', 'sheet Costos_CR', 'cells F1:L23 (Energy block)', '', 'Same 21 rows and values as Data in Brief Table 49 (for example Fuel Oil Power Plant 4650.33 M USD/GW).',
    'as Table 49', 'Update together with Table 49.')
add('Data_v2.xlsx', 'sheet 5.CR_Costos', 'blocks Capex2025 (row 2), Opex2025 (row 28), CapitalInvestment (row 54), Discounted and Not Discounted Net fossil fuel import expenditure (rows 88 and 94)', '',
    'Model results in MUSD by year for Costa Rica, used for the JCLP cost indicators.', 'all cost rows', 'Regenerate from the rerun model; the net fossil fuel import expenditure changes directly with the supply row prices.')
cols = ['document', 'section_heading', 'table_or_figure', 'first_eight_words', 'statement_as_written', 'model_rows', 'needs_to_say']
with open(os.path.join(JOB, 'paper_trace.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print(len(rows), Counter(r['document'] for r in rows))
