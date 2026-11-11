import csv, re, sys, os
from collections import Counter
J = sys.argv[1]
T = os.path.join(J, 'downloads', 'paper', 'paper_txt')


def load(n):
    return open(os.path.join(T, n), encoding='utf-8').read().splitlines()


DIB = load('CLEWISE_DataInBrief.txt')
MX = load('CLEWISE_MethodsX_v02.txt')
JC = load('CLEWISE_JCLP_draft_v2.txt')


def clean(s):
    return s.replace(chr(0x2014), ', ').replace(chr(0x2013), ' to ').replace(chr(0xFFFD), '')


def para(lines, prefix, nth=0):
    hits = [l for l in lines if l.startswith('[P|') and l.split('] ', 1)[1].startswith(prefix)]
    return hits[nth].split('] ', 1)[1]


def f8(s):
    return clean(' '.join(s.split()[:8]))


def trim(s, n=700):
    s = clean(s)
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + ' [...]'


rows = []


def add(doc, sec, tab, first, stmt, model, chg):
    r = [clean(x) for x in (doc, sec, tab, first, stmt, model, chg)]
    rows.append(r)


D = 'CLEWISE_DataInBrief.docx'
M = 'CLEWISE_MethodsX_v02.docx'
JD = 'CLEWISE_JCLP_draft_v2.docx'
S = 'Suplementary.xlsx'
DV = 'Data_v2.xlsx'
FUELNOTE = 'real 2024 USD per GJ net'

# ---------- Data in Brief prose ----------
p = para(DIB, 'This article documents a multi-country')
add(D, 'Abstract', '', f8(p),
    '[...] technology cost assumptions covering more than 50 energy, transport, AFOLU, IPPU, and waste technologies [...] Data were compiled from national statistics institutes, national GHG inventories [...] and international databases (World Bank, FAO, IRENA, OLADE SIER, UN Population Division)',
    'ALL',
    'Add that Guatemala fuel prices come from MEM price structures and Banco de Guatemala customs CIF data and that plant costs cite IRENA, IEA WEO, national plan and NREL ATB documents.')
add(D, 'Specifications Table', 'Specifications Table, row Data collection',
    'Data collection | Compiled from national statistics institutes, national',
    'Compiled from national statistics institutes, national GHG inventories (BURs, BTRs, NIRs submitted to the UNFCCC), national energy balances, agricultural censuses, and international databases (World Bank WDI, FAO FAOSTAT, IRENA, OLADE SIER, UN Population Division). [...] Compilation period: 2023 to 2025.',
    'ALL',
    'Add MEM fuel price structures, Banco de Guatemala customs CIF, IEA World Energy Outlook 2025 and NREL ATB to the list of sources and extend the compilation period to cover the 2024 price data.')
p = para(DIB, 'The CLEWISE input dataset is organized into nine')
add(D, '4. Data Description', '', f8(p),
    'Tables in this section present base-year (2021) values [...] Emission factors (Section 4.7) and technology costs (Section 4.8) are reported as static base-year values, with time-varying behaviour (e.g. cost learning curves) handled through the parameters documented in the companion MethodsX article.',
    'ALL',
    'Say that technology costs and fuel prices are in real 2024 USD, with fuel price trajectories built from observed national series and IEA WEO 2025 scenario ratios rather than a static base-year value.')
p = para(DIB, 'Technology cost data include capital costs', 0)
add(D, '4.8 Technology costs', '', f8(p), trim(p, 1400), 'ALL',
    'Replace "current USD without deflation" with real 2024 USD, name the IRENA, IEA WEO, national plan and NREL ATB editions behind each plant cost (with newer editions beside), state that plant variable costs are in M USD/PJ (USD/GJ), and add a sentence that fuel prices are pre-tax import or wholesale 2024 prices projected with IEA WEO 2025 STEPS, CPS and NZE benchmark ratios.')
add(D, '4.7.4 Country-specific emission factors (stray copy after Table 23)', '', f8(p),
    'Duplicate of the Section 4.8 paragraph ("Technology cost data include capital costs [...] Costs in Tables 49 to 71 are reported as static base-year values in current USD without deflation [...]") placed after Table 23 and before the Ecuador appendix heading.',
    'ALL', 'Delete this stray copy or make it identical to the revised Section 4.8 paragraph.')
add(D, '4.8 Technology costs', 'Author comment anchored on heading 4.8', '4.8 Technology costs (Word comment)',
    'Comment: "Aca algunos sectores no tienen costos establecidos en BAU, solo en escenarios de mitigacion" (some sectors have no costs set in BAU, only in mitigation scenarios).',
    'ALL', 'No change needed for plant and fuel rows, since the proposed costs and prices apply to all scenarios including BAU.')

# ---------- Table 57 ----------
add(D, '4.8 Technology costs', 'Table 57', 'Table 57. Costs of Energy Sector technologies for Guatemala',
    'Columns: Technology | Capital Cost | Unit | Variable Cost | Variable Cost Unit | Fixed Cost | Unit. 26 rows (7 Import/Distribution, 15 Power Plant, 4 network and hydrogen). No source column. No rows for Import - Electricity, Kerosene, Coke or Crude. Plant variable costs labelled M USD/GWh; fuel variable costs labelled M USD/PJ.',
    'ALL (Guatemala)',
    'Add a source column naming the document and edition for every value, state real 2024 USD, relabel plant variable costs as M USD/PJ after the x277.78 correction, and add rows for Import - Electricity (IMP_ELE, published 2024 regional market price instead of 0), Kerosene (DIST_KER), Coke (DIST_COK) and Crude (EXTT_CRU).')
fuel = {'Coal': ('DIST_COA', 'steam coal'), 'Diesel': ('DIST_DSL', 'Brent'), 'Fuel Oil': ('DIST_FOI', 'Brent'),
        'Gasoline': ('DIST_GSL', 'Brent'), 'LPG': ('DIST_LPG', 'Brent'), 'Natural Gas': ('DIST_NGS', 'Henry Hub')}
plants = {'Biogas': 'PPBGS', 'Biomass': 'PPBIM', 'Coal': 'PPCOA', 'Diesel': 'PPDSL', 'Fuel Oil': 'PPFOI',
          'Geothermal': 'PPGEO', 'Hydro Dam': 'PPHDAM', 'Hydro Run-of-River': 'PPHROR', 'Natural Gas': 'PPNGS',
          'Distributed Solar': 'PPPVD', 'Distributed Solar with Battery Storage': 'PPPVDS',
          'Transmission Solar': 'PPPVT', 'Transmission Solar 2': 'PPPVT2',
          'Transmission Solar with Battery Storage': 'PPPVTS', 'Wind Onshore': 'PPWNDON'}
other = {'Power Distribution': 'ELE_DIST', 'Power Transmission': 'ELE_TRANS', 'Hydrogen Distribution': 'HYD_DIST',
         'Green Hydrogen Production': 'HYD_G_PROD'}
DR_SAME = {'Diesel', 'Gasoline', 'LPG'}
i = DIB.index('[TABLE 37]')
tab = []
for l in DIB[i + 2:]:
    if l.startswith('[/TABLE'):
        break
    tab.append([c.strip() for c in l.strip().lstrip('|').split('|')])
assert len(tab) == 26, len(tab)


def tech_rows(doc, sec, tabname, xlsx=False):
    for k, c in enumerate(tab):
        name, cap, capu, var, varu, fix, fixu = c
        def u(x):
            return '' if x == '-' else ' ' + x
        stmt = f'{name}: Capital Cost {cap}{u(capu)}; Variable Cost {var}{u(varu)}; Fixed Cost {fix}{u(fixu)}'
        first = f'Costos_GUA!F{k + 3}:L{k + 3} {name}' if xlsx else name
        if name.startswith('Import/Distribution'):
            f = name.split(' - ', 1)[1]
            if f == 'Flex Fuel':
                code = 'DIST_FLEXFUEL'
                chg = 'No change proposed by this job (flex fuel is outside the listed supply rows), but the row should still name its source.'
            else:
                code, bm = fuel[f]
                if f == 'Natural Gas':
                    chg = (f'Replace {var} M USD/PJ with the 2024 pre-tax import price for Guatemala (MEM, Banco de Guatemala customs CIF), '
                           f'quoted per MMBtu, treated as gross and divided by 0.9, in {FUELNOTE}, projected with a multi-year average ratio to '
                           f'the IEA WEO 2025 Henry Hub price (STEPS central, CPS high, NZE low), and cite the source.')
                else:
                    chg = (f'Replace {var} M USD/PJ with the 2024 pre-tax import or wholesale price from MEM price structures and Banco de Guatemala '
                           f'customs CIF in {FUELNOTE}, projected with a multi-year average ratio to the IEA WEO 2025 {bm} price '
                           f'(STEPS central, CPS high, NZE low), and cite the source.')
                if f in DR_SAME:
                    chg += f' Note that {var} equals the Dominican Republic value in Table 53, so it looks like a regional proxy.'
        elif name.startswith('Power Plant'):
            t = name.split(' - ', 1)[1]
            code = plants[t]
            if var != '-':
                v = float(var)
                chg = (f'Keep Capital {cap} and Fixed {fix} but cite the IRENA, IEA WEO, national plan or NREL ATB document they come from, '
                       f'with the newer edition beside, and correct Variable Cost {var} M USD/GWh (equal to USD/kWh) by x277.78 to '
                       f'{v * 277.78:.3f} M USD/PJ (USD/GJ).')
            else:
                chg = (f'Keep Capital {cap} and Fixed {fix} but cite the IRENA, IEA WEO, national plan or NREL ATB document they come from, '
                       f'with the newer edition proposed beside; no variable cost to correct.')
        else:
            code = other[name]
            chg = "No change needed (network or hydrogen row, outside this job's plant and fuel proposals)."
        add(doc, sec, tabname, first, stmt, code, chg)


tech_rows(D, '4.8 Technology costs', 'Table 57')

# ---------- Data in Brief section 5 ----------
p = para(DIB, 'Data sources were identified through a systematic review')
add(D, '5.1 Data source identification', '', f8(p),
    '[...] (3) international databases (World Bank WDI, FAO FAOSTAT, IRENA, OLADE SIER, UN Population Division), which provide standardized cross-country data for gap-filling and cross-validation; and (4) peer-reviewed literature and grey literature (national energy plans, technology feasibility studies, IDB/UNDP/GIZ project reports) for technology costs and sector-specific parameters not available in statistical databases.',
    'ALL',
    'Add that fuel prices come from national published 2024 price data (for Guatemala MEM and Banco de Guatemala customs CIF) and IEA WEO 2025 projections, and that plant costs cite IRENA, IEA WEO, national plans and NREL ATB.')
p = para(DIB, 'For each variable in the dataset, the source was documented')
add(D, '5.1 Data source identification', '', f8(p), trim(p), 'ALL',
    'The source registry must list the new fuel price and plant cost documents with edition, table, access date and URL for each Guatemala cost row.')
p = para(DIB, 'The six countries use varying conventions for units')
add(D, '5.2 Harmonization and gap-filling', '', f8(p),
    '[...] (a) SI-derived units consistent with OSeMOSYS conventions (PJ for energy, MW for capacity, MUSD for costs, Gg for emissions, hectares for land area); (b) a common base year of 2021 for the projection starting point [...]',
    'ALL', 'Add that costs and fuel prices are expressed in real 2024 USD, fuel prices per GJ net (M USD/PJ), and plant variable costs in M USD/PJ.')
p = para(DIB, 'Gap-filling was required for countries and variables')
add(D, '5.2 Harmonization and gap-filling', '', f8(p),
    '[...] (iii) use of regional proxies, i.e., applying data from a neighboring LAC country with a similar economic structure and adjusting for population or GDP, for variables with no national data [...] Each gap-filling instance is flagged in the dataset metadata',
    'DIST_DSL; DIST_GSL; DIST_LPG',
    'Guatemala diesel, gasoline and LPG prices will no longer be regional proxies (they match the Dominican Republic values), so the metadata flag should be replaced by the national MEM and Banco de Guatemala source.')
p = para(DIB, 'The CLEWISE framework uses OSeMOSYS as its optimization engine')
add(D, '5.4 Mapping to OSeMOSYS parameters', '', f8(p),
    '[...] technology costs map directly to CapitalCost, FixedCost, and VariableCost [...]', 'ALL',
    'Add that fuel prices map to VariableCost of the import/distribution rows and that plant VariableCost is per PJ of activity (USD/GJ).')
refs = [('[12] OLADE.', 'DIST_COA; DIST_DSL; DIST_FOI; DIST_GSL; DIST_LPG; DIST_NGS',
         ' (cited in 4.2 and 5.1 for energy data and cross-validation, not explicitly for prices)',
         'Keep for energy statistics cross-checks; Guatemala fuel prices will cite MEM price structures and Banco de Guatemala customs CIF instead.'),
        ('[13] IRENA.', 'PPBGS; PPBIM; PPGEO; PPHDAM; PPHROR; PPPVD; PPPVDS; PPPVT; PPPVT2; PPPVTS; PPWNDON',
         ' (no in-text number; Section 4.8 says "learning curves based on IRENA\'s Renewable Power Generation Costs database")',
         'Keep as the source for the renewable plant costs it actually supports, add the newer IRENA Renewable Power Generation Costs edition beside it, and cite it by number in Section 4.8 and Table 57.'),
        ('[14] IEA.', 'ALL',
         ' (no in-text number; Section 4.8 says "IEA World Energy Outlook assumptions")',
         'Add IEA World Energy Outlook 2025 (STEPS, CPS, NZE) as the fuel price projection source, keep WEO 2023 only for any plant costs taken from it, and cite both by number in Section 4.8.')]
for pre, mr, note, chg in refs:
    p = para(DIB, pre)
    add(D, 'References', 'Reference list', f8(p), trim(p) + note, mr, chg)

# ---------- MethodsX ----------
p = para(MX, 'Inputs. Official GHG inventory tables')
add(M, '1.3 Step 1, Data Assembly and Harmonisation', '', f8(p), trim(p), 'ALL',
    'Add fuel price data (national 2024 pre-tax import or wholesale prices and IEA WEO 2025 benchmark projections) and plant cost references to the list of Step 1 inputs.')
add(M, '1.3 Step 1, Data Assembly and Harmonisation', 'Table 1. Step 1 summary', 'Table 1. Step 1 summary.',
    'Inputs: GHG inventory tables (IPCC-coded) / Energy balances / Sectoral statistics (agriculture, waste, industry) / NDC/LTS documents / Socioeconomic projections; Processing: Extract to CSV / Harmonise units, base years, time horizon / Fill gaps with IPCC defaults / Document metadata.',
    'ALL', 'Add "fuel prices and technology costs" to Inputs and "convert costs to real 2024 USD and USD/GJ net" to Processing.')
p = para(MX, 'The energy and transport template follows standard')
add(M, '1.4.1 Energy and Transport', '', f8(p), trim(p), 'ALL',
    'Add that power plant costs are sourced to named IRENA, IEA WEO, national plan and NREL ATB editions in real 2024 USD, plant variable costs are in USD/GJ, and fuel supply rows carry pre-tax import or wholesale prices projected with IEA WEO 2025 scenarios.')
p = para(MX, 'Indicators. From each scenario')
add(M, '1.7 Step 5, Encoding NDC and LTS Constraints and Generating Indicators', '', f8(p), trim(p), 'ALL',
    'No change to the wording is needed, but the fuel-import exposure index will change once fuel prices and the IMP_ELE price are updated, so results must be regenerated.')
p = para(MX, 'Additional validation avenues include')
add(M, '2. Method Validation', '', f8(p), trim(p), 'ALL',
    'Add that fuel price sensitivity uses the IEA WEO 2025 CPS (high) and NZE (low) cases around the STEPS central case.')
add(M, 'References', 'Reference list', '[1] F. Gardumi, A. Shivakumar, R. Morrison, C.',
    'Reference list [1] to [11] contains no cost or fuel price source (OSeMOSYS, CLEWs, IPCC 2006 and placeholder items only).', 'ALL',
    'Add the plant cost (IRENA, IEA WEO, NREL ATB, national plan) and fuel price (national price publications, IEA WEO 2025) references if Section 1.4.1 is expanded.')

# ---------- JCLP ----------
p = para(JC, 'CLEWISE is implemented as a linear')
add(JD, '2.2 CLEWISE model architecture and sector modules', '', f8(p), trim(p), 'ALL',
    'Add that costs are in real 2024 USD and fuel costs are pre-tax import or wholesale prices projected from IEA WEO 2025, and state the discount rate, which the draft does not give.')
p = para(JC, 'The primary indicators are:')
add(JD, '2.4.3 Normalized indicators', '', f8(p), trim(p), 'ALL',
    'No change to the definitions is needed, but the indicator values must be recomputed after the fuel price, variable O&M and IMP_ELE changes.')
for pre in ['In countries like the Dominican Republic, Guatemala, and Jamaica, the ratio',
            'The ΔOPEX/GDP indicator captures', 'The change in accumulated investment indicator']:
    p = para(JC, pre)
    add(JD, '3.5 Normalised indicators for cross-country comparison', '', f8(p), trim(p, 500), 'ALL',
        'Re-check the Guatemala statement after re-running with the new fuel prices and the x277.78 variable O&M correction, since OPEX and fuel-import results may change.')
p = para(JC, 'The economic and efficiency indices further')
add(JD, '4.2 Why NDC scenarios are not enough', '', f8(p), trim(p, 500), 'ALL',
    'Re-check the Guatemala capital and operating cost statements after the model is re-run with the updated costs.')
add(JD, 'References', 'Reference list', '10. IRENA. Long-term energy scenarios and low-emission development',
    '10. IRENA. Long-term energy scenarios and low-emission development strategies: Stocktaking and alignment. (2023). (Only IRENA item; not a cost source. No IEA WEO, NREL ATB or OLADE price reference in the JCLP list.)',
    'ALL', 'Add references for the plant cost documents (IRENA, IEA WEO, NREL ATB, national plan) and for fuel prices (MEM, Banco de Guatemala, IEA WEO 2025).')

# ---------- Suplementary.xlsx ----------
add(S, 'Costos_GUA', 'Costos_GUA!F1:L28 (Energy block)', 'Costos_GUA!F1:L28',
    'Energy block header: Technology | Capital Cost | Unit | Variable Cost | Variable Cost Unit | Fixed Cost | Unit; 26 rows identical to Data in Brief Table 57; no source column.',
    'ALL (Guatemala)',
    'Update together with Table 57: add a source column, real 2024 USD label, corrected plant variable costs in M USD/PJ, new fuel prices, and an Import - Electricity row.')
tech_rows(S, 'Costos_GUA', 'Costos_GUA!F1:L28 (Energy block)', xlsx=True)

# ---------- Data_v2.xlsx ----------
add(DV, '9.Guatemala_Costos', '9.Guatemala_Costos!A2:AH78', '9.Guatemala_Costos!A2:AH78',
    'Model results Capex2025 [MUSD], Opex2025 [MUSD], CapitalInvestment [MUSD] by scenario (BAU, NDC, LTS) and sector, 2018 to 2050; Energy rows blank for BAU and NDC Capex/Opex; LTS Energy Capex and Opex e.g. 1562.776 (2030), 1854.294 (2035), 577.1958 (2050); NDC Energy CapitalInvestment 2296.23 (2030), 4003.282 (2035).',
    'ALL', 'Regenerate after the model is re-run with the new fuel prices, corrected variable O&M and IMP_ELE price, and fill the blank Energy rows.')
add(DV, '9.Guatemala_Costos', '9.Guatemala_Costos!A88:AH98', '9.Guatemala_Costos!A88:AH98',
    'Discounted Net fossil fuel import expenditure [MUSD] and Not Discounted Net fossil fuel import expenditure [MUSD], rows BAU/NDC/LTS: all value cells empty for Guatemala.',
    'DIST_COA; DIST_COK; DIST_DSL; DIST_FOI; DIST_GSL; DIST_KER; DIST_LPG; DIST_NGS; EXTT_CRU; IMP_ELE',
    'Fill from the re-run model using the new pre-tax import prices in real 2024 USD per GJ net.')
add(DV, 'Indice', 'Indice!B11:C11', 'Indice!B11:C11',
    '9. Guatemala_Costos: Datos de costos CAPEX, OPEX, Investment, Energy Demand, Net Fossil fuel para Guatemala', 'ALL',
    'No change needed.')

for r in rows:
    for x in r:
        assert chr(0x2014) not in x, x
out = os.path.join(J, 'paper_trace.csv')
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
    w.writerow(['document', 'section_heading', 'table_or_figure', 'first_eight_words', 'statement_as_written', 'model_rows', 'needed_change'])
    w.writerows(rows)
print(Counter(r[0] for r in rows), len(rows))
