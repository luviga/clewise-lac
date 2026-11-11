"""Write search_log.csv and paper_trace.csv."""
import os, sys, csv, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

D = RETRIEVED
L = []
def log(row, lead, where, result): L.append(dict(row=row, lead=lead, url_or_query=where, date=D, result=result))
ALLP = "all plants in scope"
# paper leads
log(ALLP, "CLEWISE Data in Brief section 4.8 and Table 53 (lead only)", "paper copy, Table 53", "Table 53 prints the 2021 workbook values; section 4.8 names IRENA Renewable Power Generation Costs and IEA World Energy Outlook as the basis of cost projections; references [13] IRENA 2023 and [14] IEA 2023")
log(ALLP, "CLEWISE MethodsX and JCLP draft (lead only)", "paper copies", "no cost source named beyond the general OSeMOSYS practice; no DR-specific cost value")
log(ALLP, "workbook Reference column (lead only)", "A-O_Parametrization.xlsx Reference column", "names PEN Tabla 220 and 229, PEN 2022, 2023 ATB, SIE-064-2022-TF with ATB trajectory and ATB battery costs, OC weekly reports, a personal communication (PPBIM capital) and a CNE study (PPBIM variable)")
# IRENA
log(ALLP, "IRENA Renewable Power Generation Costs in 2022", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf", "downloaded; Table H.1 page 15: bioenergy 2,162, hydropower 2,881, solar PV 876, onshore wind 1,274 USD/kW (2022 USD); O&M shares pages 162 and 183; no DR-specific table; no projection")
log(ALLP, "IRENA Renewable Power Generation Costs in 2024 (newest edition)", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_TEC_RPGC_in_2024_2025.pdf", "downloaded; Table S1 page 15: bioenergy 3,242, hydropower 2,267, solar PV 691, onshore wind 1,041 USD/kW (2024 USD)")
log(ALLP, "IEA World Energy Outlook 2023 power generation technology costs", "https://iea.blob.core.windows.net/assets/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf", "downloaded; Table B.4a page 301 gives capital costs for United States, European Union, China and India only (no hydropower, biomass or engines; O&M combined with fuel and CO2); no model value matches within 2 percent (US gas CCGT 1,000 against 1,084)")
log(ALLP, "IEA World Energy Outlook 2025 power generation technology costs", "https://www.iea.org/reports/world-energy-outlook-2025", "copied from LAC_LOCAL_PRICES manual download; Table B.4b page 455 has the same regional structure as WEO 2023; no DR or Latin America values")
log(ALLP, "CNE Plan Energetico Nacional 2022-2036 (national plan)", "https://cne.gob.do/documentos/tecnicos/pen/", "page lists files through a Dropbox plugin; PEN2022-2037.pdf downloaded through the listed download link; Tablas 220, 223, 226, 229 give generic project costs")
log(ALLP, "PEN copies elsewhere", "https://bvearmb.do/handle/123456789/1855; https://www.energiaestrategica.com/wp-content/uploads/2021/12/Borrador-Plan-Energetico-Nacional-2022-2036-CNE.pdf", "HTTP 403 for both; not needed after the CNE file was obtained")
log(ALLP, "NREL ATB 2023 electricity data", "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2023/ATBe.parquet", "downloaded; matches PPHDAM (Hydropower NPD1), PPPVD (CommPV Class1 Moderate), the 2025 storage adder (4Hr battery OCC Conservative 2025, 1,836.85) and the adder in fixed O&M (4Hr battery Fixed O&M Moderate 2025, 35.90)")
log(ALLP, "NREL ATB 2024 v3.0.0 electricity data", "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2024/v3.0.0/ATBe.parquet", "downloaded; newer edition for PPHDAM and PPPVD; trajectories for NG CC, UtilityPV, LandbasedWind and 4Hr battery; Biopower Dedicated Fixed O&M 163.67 USD/kW-yr")
for t in ["PPPVT", "PPPVTHYD", "PPWNDON"]:
    log(t, "SIE-064-2022-TF (workbook reference for the 2018 level)", "web search: SIE-064-2022-TF Superintendencia de Electricidad resolucion tarifa energia renovable solar eolica costo inversion", "resolution not found in a short search; values 1,170.46 and 1,749.26 USD/kW not found in ATB 2023, IRENA 2022 or the PEN")
    log(t, "ATB 2023 UtilityPV and LandbasedWind paths", "ATBe_2023.parquet", "current path is piecewise linear between 2018, 2024, 2025, 2030 and 2050; no ATB 2023 path matches within 2 percent apart from single years")
for t in ["PPADSL","PPAFOI","PPANGS","PPDBGS","PPDBIM","PPDDSL","PPDFOI","PPDGLP","PPDGSL","PPDNGS","PPCCTNGS","PPICEGASFOI"]:
    log(t, "PEN Tabla 220 and ATB 2023 NG combined cycle path", "PEN2022-2037.pdf page 345; ATBe_2023.parquet NaturalGas_FE", "level 1,084 USD/kW and fixed O&M 14,100 USD/MW-yr match; variable O&M 2.55 USD/MWh (0.7083 USD/GJ) does not match 0.3751; the current capital cost decline after 2018 matches no ATB 2023 path")
log("PPCOA", "OC-SENI weekly operating cost reports (workbook reference for fixed and variable O&M)", "https://www.oc.do (Memoria Anual 2024 already copied as DR-007)", "the Memoria gives fuel costs, not plant O&M; PEN Tabla 223 gives 40,580 USD/MW-yr and 4.50 USD/MWh")
log("PPBIM", "personal communication with the Barahona project (workbook reference for capital 38.46)", "not an external source", "no external document gives 38.46 USD/kW; IRENA 2022 bioenergy 2,162 USD/kW used")
log("PPBGS", "workbook (zero placeholder, no reference); Data in Brief Table 53 (no row)", "paper copy", "no value")
log("PPBGS", "IRENA 2022 bioenergy (capital, O&M)", "IRENA 2022 pages 15 and 183", "capital 2,162 USD/kW; fixed O&M only as a range (2 to 6 percent of capital per year); variable O&M 0.005 USD/kWh")
log("PPBGS", "ATB 2024 Biopower Dedicated", "ATBe_2024_v3.0.0.parquet", "Fixed O&M 163.67 USD/kW-yr, Variable O&M 5.25 USD/MWh (US dedicated biomass)")
log("PPDHYD", "ATB 2023 Hydropower (all NPD and NSD classes)", "ATBe_2023.parquet", "1,980 USD/kW and 20 USD/kW-yr not found within 2 percent in a consistent scenario")
log("PPDHYD", "IRENA 2022 hydropower", "IRENA 2022 Table H.1 and page 162", "2,881 USD/kW; O&M 1 to 4 percent of investment, IEA average 2.5 percent")
# fuel leads
log("DIST_NGS", "LNG origin and indexation for the benchmark (F4)", "https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_A.xls", "US exports of LNG to the DR 2024: 90,594 MMcf, against DR customs imports of 1,842,142 t (about 89,798 MMcf gross): the US supplied about all 2024 LNG")
log("DIST_NGS", "LNG contract indexation", "https://totalenergies.com/node/26486", "HTTP 410")
log("DIST_NGS", "LNG contract indexation", "https://www.businesswire.com/news/home/20250415382375/en/", "HTTP 403")
log("DIST_NGS", "LNG contract indexation", "https://totalenergies.com/newsroom/liquefied-natural-gas-totalenergies-will-supply-400000-tons-lng-year-15-years/?lang=eng", "downloaded; heads of agreement with ENADOM, price indexed to Henry Hub, start mid-2027")
log("DIST_NGS", "AES Corporation Form 10-K (FY2013) LNG contract linked to NYMEX Henry Hub", "web search result https://www.sec.gov/Archives/edgar/data/0000874761/000087476114000011/a2013form10-k.htm", "not opened (SEC asks automated clients for a contact address); not cited")
log("DIST_COA", "coal index for the WEO series (F4)", "DR-006 MEM Boletin anual 2024", "reference is Platts coal FOB Puerto Bolivar (Colombia), an Atlantic-basin export price; WEO 2025 European Union steam coal (imports) chosen")
log("DIST_COA", "observed Colombian coal benchmark", "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx", "the annual file has no Colombian coal price column (only its description); Coal South African fob Richards Bay NAR 6000 used")
log("DIST_KER", "market value for kerosene", "LAC_LOCAL_PRICES local_prices_2024.csv rows 54 to 57", "only MICM parities (kerosene, frozen retail; avtur, unfrozen); no customs unit value for kerosene")
log("all supply rows", "IEA WEO 2025 fuel price table", "WorldEnergyOutlook2025.pdf page 109", "Table 2.3 (not 2.32): USD (MER, 2024), 2024, 2035 and 2050 for CPS, STEPS and NZE; gas on gross basis; coal adjusted to 6,000 kcal/kg")
log("all supply rows", "US CPI-U annual average", "https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2016&endyear=2025&annualaverage=true", "downloaded 2016 to 2025")
log("all supply rows", "EIA Brent and Henry Hub annual", "https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls; https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls", "downloaded to 2025")
log("IMP_ELE", "activity limit", "BAU TotalTechnologyAnnualActivityUpperLimit.csv", "0 in every year: rule E1 does not apply")
log("EXTT_CRU; EXTT_NGS; PRO_COA", "activity limits", "BAU TotalTechnologyAnnualActivityUpperLimit.csv, ResidualCapacity.csv, TotalAnnualMaxCapacity.csv", "EXTT_NGS upper limit 0 in all years; EXTT_CRU 43.2 PJ and PRO_COA 3.1 PJ in 2024 with no capacity limit and VariableCost 0")
pd.DataFrame(L).to_csv(os.path.join(JOB, "search_log.csv"), index=False)
print("search_log", len(L))

# ---------- paper trace ----------
P = os.path.join(DL, "paper")
def lines(name): return open(os.path.join(P, name + ".txt"), encoding="utf-8").read().split("\n")
docs = {"CLEWISE_DataInBrief.docx": lines("CLEWISE_DataInBrief"), "CLEWISE_MethodsX_v02.docx": lines("CLEWISE_MethodsX_v02"),
        "CLEWISE_JCLP_draft_v2.docx": lines("CLEWISE_JCLP_draft_v2")}
def heading(doc, n):
    ls = docs[doc]
    for i in range(n - 1, -1, -1):
        m = re.match(r"\[P (T[ií]tulo\d|Ttulo\d|Heading\d)\] (.*)", ls[i])
        if m: return m.group(2)
    return ""
def first8(doc, n):
    t = re.sub(r"^\[P[^\]]*\] ", "", docs[doc][n - 1])
    return " ".join(t.split()[:8])
summ = pd.read_csv(os.path.join(JOB, "proposals_summary.csv"))
def prop(tech, par, sc="ALL"):
    r = summ[(summ.Tech == tech) & (summ.Parameter == par) & (summ.fuel_scenario == sc)]
    return None if not len(r) else r.iloc[0]
T = []
def tr(doc, n, table, stmt, rows, needs):
    T.append(dict(document=doc, section_heading=(heading(doc, n) or "Abstract") if n else "", table_or_figure=table,
                  first_eight_words=first8(doc, n) if n else "", statement_as_written=stmt, model_rows=rows, needs_to_say=needs))
DIB = "CLEWISE_DataInBrief.docx"; MX = "CLEWISE_MethodsX_v02.docx"; JC = "CLEWISE_JCLP_draft_v2.docx"
tr(DIB, 7, "", "Data were compiled from ... international databases (World Bank, FAO, IRENA, OLADE SIER, UN Population Division)", "all cost rows",
   "Add the cost sources now used for the DR: CNE PEN 2022-2036, NREL ATB 2023 and 2024, IEA WEO 2025, UN Comtrade, MICM, EIA, World Bank Pink Sheet and BLS CPI-U.")
tr(DIB, 35, "", "Emission factors (Section 4.7) and technology costs (Section 4.8) are reported as static base-year values", "all cost rows",
   "Say that fuel supply prices vary by year and by fuel price scenario (STEPS central, CPS high, NZE low) and that plant cost paths are given by year.")
tr(DIB, 644, "", "duplicate of the section 4.8 paragraph placed before the Dominican Republic AFOLU tables (section 4.7)", "all cost rows",
   "Remove the duplicate or keep one copy, then apply the section 4.8 changes below.")
tr(DIB, 819, "Tables 49-71", "Cost projections incorporate learning curves based on IRENA's Renewable Power Generation Costs database and IEA World Energy Outlook assumptions", "DR plants",
   "For the DR say that plant cost paths follow NREL ATB 2023 or 2024 (hydro dam, distributed PV, PV and wind trajectories, gas combined cycle path, storage adder) and that IRENA 2022 gives the PV, wind, hydro and bioenergy levels.")
tr(DIB, 819, "Tables 49-71", "Country-specific adjustments were applied where national feasibility studies or competitive auction results provided local cost benchmarks", "DR thermal plants",
   "Name the CNE Plan Energetico Nacional 2022-2036 generic project tables (Tablas 220, 223 and 229) as the DR source for thermal plant capital, fixed and variable O&M.")
tr(DIB, 819, "Tables 49-71", "Costs in Tables 49-71 are reported as static base-year values in current USD without deflation", "DR fuel supply rows",
   "Say that DR fuel supply prices are pre-tax import or wholesale prices in real 2024 USD per GJ (net calorific basis), deflated with US CPI-U, projected with IEA WEO 2025 price ratios.")
tr(DIB, 1446, "", "(4) peer-reviewed literature and grey literature (national energy plans, technology feasibility studies ...) for technology costs", "all cost rows",
   "Add customs statistics (UN Comtrade), the regulator's weekly import parity (MICM) and NREL ATB to the hierarchy for costs and prices.")
tr(DIB, 1449, "", "(a) SI-derived units ... MUSD for costs ... (b) a common base year of 2021", "all cost rows",
   "State that DR fuel prices are in real 2024 USD while plant costs keep their source currency year.")
tr(DIB, 1455, "", "technology costs map directly to CapitalCost, FixedCost, and VariableCost", "fuel supply rows",
   "Add that fuel supply VariableCost carries one price series per fuel price scenario.")
tr(DIB, 1479, "Reference [13]", "IRENA. (2023). Renewable Power Generation Costs in 2022.", "PV, wind, hydro, bioenergy", "Keep, and add IRENA (2025) Renewable Power Generation Costs in 2024 where the newer values are cited.")
tr(DIB, 1480, "Reference [14]", "IEA. (2023). World Energy Outlook 2023.", "fuel supply rows", "Replace or add IEA (2025) World Energy Outlook 2025 for fuel prices; add NREL ATB 2023 and 2024 and CNE PEN 2022-2036.")
TAB = {"Import/Distribution - Biomass": None, "Import/Distribution - Coal": "DIST_COA", "Import/Distribution - Coke": "DIST_COK", "Import/Distribution - Crude": "DIST_CRU",
       "Import/Distribution - Diesel": "DIST_DSL", "Import/Distribution - Fuel Oil": "DIST_FOI", "Import/Distribution - Gasoline": "DIST_GSL", "Import/Distribution - LPG": "DIST_LPG",
       "Import/Distribution - Natural Gas": "DIST_NGS", "Import - Electricity": "IMP_ELE", "Selfproducer Power Plant - Hydro": "PPDHYD", "Power Plant - Geothermal": None,
       "Power Plant - Hydro Dam": "PPHDAM", "Power Plant - Hydro Run-of-River": None, "Power Plant - Distributed Solar": "PPPVD", "Power Plant - Transmission Solar": "PPPVT",
       "Power Plant - Transmission Solar (Hydrogen)": "PPPVTHYD", "Power Plant - Transmission Solar with Battery Storage": None, "Power Plant - Wind Offshore": None,
       "Power Plant - Wind Onshore": "PPWNDON", "Power Distribution": None, "Power Transmission": None, "Hydrogen Distribution": None, "Green Hydrogen Production": None,
       "Isolated Power Plant - Diesel": "PPADSL", "Isolated Power Plant - Fuel Oil": "PPAFOI", "Isolated Power Plant - Natural Gas": "PPANGS", "Power Plant - Biomass": "PPBIM",
       "Power Plant - Combined Cycle Fuel Oil and Diesel": None, "Power Plant - Combined Cycle Gas Turbine Diesel": "PPCCTDSL",
       "Power Plant - Combined Cycle Gas Turbine Natural Gas": "PPCCTNGS", "Power Plant - Combined Cycle Gas Turbine Natural Gas and Diesel": None, "Power Plant - Coal": "PPCOA",
       "Selfproducer Power Plant - Biogas": "PPDBGS", "Selfproducer Power Plant - Biomass": "PPDBIM", "Selfproducer Power Plant - Diesel": "PPDDSL",
       "Selfproducer Power Plant - Fuel Oil": "PPDFOI", "Selfproducer Power Plant - LPG": "PPDGLP", "Selfproducer Power Plant - Gasoline": "PPDGSL",
       "Selfproducer Power Plant - Natural Gas": "PPDNGS", "Power Plant - Internal Combustion Engine Fuel Oil": "PPICEFOI",
       "Power Plant - Internal Combustion Engine Natural Gas and Fuel Oil": "PPICEGASFOI"}
dib = docs[DIB]; start = [i for i, l in enumerate(dib) if l.startswith("[P ] Table 53.")][0] + 1
tline = start + 1
for l in dib[start + 2:]:
    if l.startswith("[END TABLE"): break
    cells = [c.strip() for c in l.strip()[2:].split(" | ")]
    name = cells[0]; tech = TAB.get(name)
    stmt = f"{name}: capital {cells[1]}, variable {cells[2]} {cells[3]}, fixed {cells[4]} {cells[5]}"
    if tech is None:
        needs = "No change from this job (technology outside the section 5 scope)."
    elif tech == "IMP_ELE":
        needs = "No change: the import technology has an activity limit of 0 in every year and is not priced by this job."
    elif tech.startswith("DIST_"):
        r = prop(tech, "VariableCost", "STEPS")
        needs = (f"Variable cost becomes a series: 2024 {r.proposed_2024:.2f} USD/GJ (real 2024, net), STEPS 2030 {r.proposed_2030:.2f}, STEPS 2050 {r.proposed_2050:.2f}, "
                 f"with CPS and NZE variants; cite the chosen local price point and WEO 2025.")
    else:
        parts = []
        for par, lab in (("CapitalCost", "capital"), ("FixedCost", "fixed"), ("VariableCost", "variable")):
            r = prop(tech, par)
            parts.append(f"{lab} {r.proposed_2024:.4g} ({r.basis_classes})")
        needs = "2024 values become " + ", ".join(parts) + " in USD/kW, USD/kW-yr and USD/GJ; cite the sources in proposals.csv."
    T.append(dict(document=DIB, section_heading="4.8 Technology costs", table_or_figure="Table 53", first_eight_words="Table 53. Costs of Energy Sector technologies for",
                  statement_as_written=stmt, model_rows=tech or "", needs_to_say=needs))
T.append(dict(document=DIB, section_heading="4.8 Technology costs", table_or_figure="Table 53", first_eight_words="Table 53. Costs of Energy Sector technologies for",
              statement_as_written="no row for Power Plant - Biogas (PPBGS) or for Import/Distribution - Kerosene (DIST_KER)", model_rows="PPBGS; DIST_KER",
              needs_to_say="Add rows: PPBGS capital 2,162 USD/kW, fixed 163.67 USD/kW-yr, variable 1.39 USD/GJ; DIST_KER 2024 19.89 USD/GJ (MICM kerosene import parity) with WEO 2025 projection."))
tr(MX, 44, "", "Technology lists are populated with country-specific power plants (type, nameplate capacity, efficiency, commissioning and retirement years, capital and operating costs)", "all plants",
   "Add one sentence on the cost hierarchy (national plan, IRENA, NREL ATB) and on fuel prices as pre-tax import parity in real 2024 USD with WEO scenario ratios.")
tr(MX, 92, "", "(c) fuel-import exposure indices", "fuel supply rows", "No wording change; values must be recomputed with the new fuel prices.")
tr(MX, 103, "", "sensitivity analysis on key parameters (land-use transition rates, waste growth, technology costs)", "fuel supply rows",
   "Mention that fuel price sensitivity is available through the CPS (high) and NZE (low) price series.")
tr(JC, 34, "", "least-cost optimization case ... technical benchmark", "all cost rows", "No wording change; the benchmark must be rerun with the new costs.")
tr(JC, 36, "2.2", "The model minimizes the discounted sum of investment, operation and maintenance, and fuel costs", "all cost rows", "No wording change.")
tr(JC, 69, "2.4.3", "Fuel-Import Exposure: net fossil fuel import expenditure as a share of GDP, normalized to BAU", "fuel supply rows", "No wording change; recompute with the new fuel prices.")
tr(JC, 80, "3.2", "In the Dominican Republic, for example, emissions drop from 56,483 Gg CO2e in the BAU scenario to approximately 28,300", "all cost rows", "Check the figures after the rerun; plant generation is held by Stage 3 limits, so changes come from capacity and demand-side fuel choices.")
tr(JC, 102, "3.5, Figure 10", "In countries like the Dominican Republic, Guatemala, and Jamaica, the ratio remains consistently below the BAU line", "all plants", "Recompute DCAPEX/GDP for the DR and revise the sentence if the sign changes.")
tr(JC, 105, "3.5, Figure 11", "In countries like the Dominican Republic, Guatemala, and Jamaica, the indicator remains consistently negative or near the zero line", "fuel supply rows; plants", "Recompute DOPEX/GDP for the DR; fuel price levels change (for example coal and LPG fall, natural gas rises).")
tr(JC, 108, "3.5, Figure 12", "For Costa Rica and the Dominican Republic, the accumulated investment ratio remains near the zero line", "all plants", "Recompute the accumulated investment ratio for the DR.")
T.append(dict(document="Suplementary.xlsx", section_heading="sheet Costos_RD", table_or_figure="cells F2:K44 (Energy block)", first_eight_words="",
              statement_as_written="same 41 rows and values as Data in Brief Table 53", model_rows="as Table 53", needs_to_say="Apply the Table 53 changes to the same cells."))
for cellref, txt in [("A2 and rows 4 to 26", "Capex2025 [MUSD] by scenario and sector"), ("A28 and rows 30 to 52", "Opex2025 [MUSD] by scenario and sector"),
                     ("A54 and rows 56 to 78", "CapitalInvestment [MUSD] by scenario and sector"), ("A88 and A94", "Discounted and not discounted net fossil fuel import expenditure [MUSD]"),
                     ("row 101, columns E to L", "CAPEX, DCAPEX, CUMDCAPEX, DCAPEX/GDP, OPEX, DOPEX, CUMDOPEX, DOPEX/GDP")]:
    T.append(dict(document="Data_v2.xlsx", section_heading="sheet 13.RD_Costos", table_or_figure=cellref, first_eight_words="", statement_as_written=txt,
                  model_rows="all cost rows", needs_to_say="Recompute from the rerun model results."))
pd.DataFrame(T).to_csv(os.path.join(JOB, "paper_trace.csv"), index=False)
print("paper_trace", len(T), pd.DataFrame(T).document.value_counts().to_dict())
