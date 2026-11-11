"""Step 2: paper_trace.csv. Statements about costs and fuel prices in the CLEWISE paper copies, and what each will need to say."""
import csv
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
S = pd.read_csv(HERE / "proposals_summary.csv", keep_default_na=False)
def sv(tech, param, sc="ALL"):
    g = S[(S.technology == tech) & (S.parameter == param) & (S.fuel_scenario == sc)]
    return None if g.empty else g.iloc[0]

rows = []
def add(doc, sec, tab, first8, stmt, model_rows, need):
    rows.append([doc, sec, tab, first8, stmt, model_rows, need])

DIB = "CLEWISE_DataInBrief.docx"; MX = "CLEWISE_MethodsX_v02.docx"; JC = "CLEWISE_JCLP_draft_v2.docx"
P49 = "Technology cost data include capital costs (CAPEX in"
add(DIB, "4.8 Technology costs", "", P49,
    "Cost projections incorporate learning curves based on IRENA's Renewable Power Generation Costs database and IEA World Energy Outlook assumptions. Country-specific adjustments were applied where national feasibility studies or competitive auction results provided local cost benchmarks.",
    "all PP* plant rows", "Name the source of each Jamaica plant cost as recorded in proposals.csv (IRENA 2022, IEA WEO 2023, NREL ATB 2024 or a stated assumption) instead of a general reference to IRENA and the WEO.")
add(DIB, "4.8 Technology costs", "", P49,
    "Costs in Tables 49-71 are reported as static base-year values in current USD without deflation; time-varying behaviour (technology learning, capital cost decline) is parameterised separately within the OSeMOSYS configuration described in the companion MethodsX article.",
    "all cost rows", "State that fuel supply prices are pre-tax import or wholesale prices in real 2024 USD per GJ (net calorific basis) with 2024 as the observed year, and give the currency year of each plant cost source.")
add(DIB, "Section 4 (paragraph placed before Appendix tables, duplicate of 4.8)", "", P49,
    "Same text as the 4.8 Technology costs paragraph (duplicated in the document body).", "all cost rows",
    "Remove the duplicate or keep it identical to the revised 4.8 paragraph.")
add(DIB, "Specifications table", "Data collection row", "Compiled from national statistics institutes, national GHG inventories",
    "international databases (World Bank WDI, FAO FAOSTAT, IRENA, OLADE SIER, UN Population Division)", "fuel supply rows; plant rows",
    "Add the sources now used for costs: IEA WEO 2025, EIA spot prices, World Bank Pink Sheet, UN Comtrade, MSET Energy Statistics, OUR, BLS CPI-U and NREL ATB 2024 where cited.")
add(DIB, "4.2 Electricity demand and installed capacity", "", "For Jamaica, electricity demand growth followed 2018 Jamaica",
    "For Jamaica, electricity demand growth followed 2018 Jamaica Integrated Resource Plan [13]", "none (demand); reference list",
    "Reference [13] in the list is IRENA Renewable Power Generation Costs in 2022, not the Jamaica IRP; the IRP needs its own reference entry, and IRENA [13] keeps its number for costs.")
add(DIB, "5.2 Harmonization and gap-filling", "", "The six countries use varying conventions for units,",
    "standardized all data to: (a) SI-derived units ... MUSD for costs ...; (b) a common base year of 2021", "all cost rows",
    "Say that cost inputs are in real 2024 USD (fuel prices deflated with US CPI-U) although the model's first year is 2021.")
add(DIB, "References", "[13]", "IRENA. (2023). Renewable Power Generation Costs in 2022.",
    "IRENA (2023) Renewable Power Generation Costs in 2022", "PPPVT, PPPVD, PPWNDON, PPHDAM, PPHROR, PPGEO, PPBIM, PPBGS",
    "Keep, with URL; add the newest IRENA edition where proposals use it as a newer-edition value.")
add(DIB, "References", "[14]", "IEA. (2023). World Energy Outlook 2023. International",
    "IEA (2023) World Energy Outlook 2023", "plant rows", "Keep for plant costs where cited; add IEA (2025) World Energy Outlook 2025 for fuel price projections (Table 2.3).")

# Table 67 rows
T67 = [("Import/Distribution - Coal", "DIST_COA", "VariableCost", "1.51"), ("Import/Distribution - Coke", "DIST_COK", "VariableCost", "4.62"),
       ("Import/Distribution - Diesel", "DIST_DSL", "VariableCost", "18.92"), ("Import/Distribution - Fuel Oil", "DIST_FOI", "VariableCost", "12.46"),
       ("Import/Distribution - Gasoline", "DIST_GSL", "VariableCost", "24.28"), ("Import/Distribution - Jet Fuel", "DIST_JET", "VariableCost", "16.66"),
       ("Import/Distribution - Kerosene", "DIST_KER", "VariableCost", "16.66"), ("Import/Distribution - LPG", "DIST_LPG", "VariableCost", "21.65"),
       ("Import/Distribution - Natural Gas", "DIST_NGS", "VariableCost", "7.06"),
       ("Power Plant - Geothermal", "PPGEO", "CapitalCost", "6750.07"), ("Power Plant - Geothermal", "PPGEO", "FixedCost", "113.62"),
       ("Power Plant - Hydro Dam", "PPHDAM", "CapitalCost", "3007.71"), ("Power Plant - Hydro Dam", "PPHDAM", "FixedCost", "85"),
       ("Power Plant - Hydro Run-of-River", "PPHROR", "CapitalCost", "7436.08"), ("Power Plant - Hydro Run-of-River", "PPHROR", "FixedCost", "120"),
       ("Power Plant - Distributed Solar", "PPPVD", "CapitalCost", "2858.73"), ("Power Plant - Distributed Solar", "PPPVD", "FixedCost", "30.33"),
       ("Power Plant - Distributed Solar with Battery Storage", "PPPVDS", "CapitalCost", "3682.89"), ("Power Plant - Distributed Solar with Battery Storage", "PPPVDS", "FixedCost", "66.13"),
       ("Power Plant - Transmission Solar", "PPPVT", "CapitalCost", "1350"), ("Power Plant - Transmission Solar", "PPPVT", "FixedCost", "31.2"),
       ("Power Plant - Wind Onshore", "PPWNDON", "CapitalCost", "1870"), ("Power Plant - Wind Onshore", "PPWNDON", "VariableCost", "0.69"), ("Power Plant - Wind Onshore", "PPWNDON", "FixedCost", "36"),
       ("Power Plant - Wind Onshore with Battery Storage", "PPWNDONS", "CapitalCost", "3457.25"), ("Power Plant - Wind Onshore with Battery Storage", "PPWNDONS", "FixedCost", "75.68"),
       ("Power Plant - Biogas", "PPBGS", "CapitalCost", "5391"), ("Power Plant - Biogas", "PPBGS", "VariableCost", "1.4"), ("Power Plant - Biogas", "PPBGS", "FixedCost", "157"),
       ("Power Plant - Biomass", "PPBIM", "CapitalCost", "5391"), ("Power Plant - Biomass", "PPBIM", "VariableCost", "1.4"), ("Power Plant - Biomass", "PPBIM", "FixedCost", "157"),
       ("Power Plant - Diesel", "PPDSL", "CapitalCost", "5391"), ("Power Plant - Diesel", "PPDSL", "VariableCost", "0.9"), ("Power Plant - Diesel", "PPDSL", "FixedCost", "2.99"),
       ("Power Plant - Fuel Oil", "PPFOI", "CapitalCost", "5391"), ("Power Plant - Fuel Oil", "PPFOI", "VariableCost", "6.34"), ("Power Plant - Fuel Oil", "PPFOI", "FixedCost", "2.99"),
       ("Power Plant - Natural Gas", "PPNGS", "CapitalCost", "1300"), ("Power Plant - Natural Gas", "PPNGS", "VariableCost", "1.15"), ("Power Plant - Natural Gas", "PPNGS", "FixedCost", "22.77")]
for name, tech, param, val in T67:
    sc = "STEPS" if tech.startswith("DIST") else "ALL"
    s = sv(tech, param, sc)
    if s is None:
        need = "No proposal for this cell."
    else:
        p24 = s["proposed_2024"]
        basis = s["basis_classes"]
        if tech.startswith("DIST"):
            need = (f"Report {float(p24):.2f} MUSD/PJ for 2024 (pre-tax import or wholesale price, real 2024 USD, net basis; the table shows the 2021 workbook value) "
                    f"and state that later years follow WEO 2025 STEPS ({float(s['proposed_2030']):.2f} in 2030, {float(s['proposed_2050']):.2f} in 2050).")
        else:
            if "keep" in s["change_classes"] and s["change_classes"] == "keep":
                need = f"Value stays ({float(p24):.2f} in 2024); add its source ({basis})."
            else:
                need = f"Report {float(p24):.2f} for 2024 ({basis}); the table value is the 2021 workbook value; add the source."
    add(DIB, "4.8 Technology costs", "Table 67. Costs of Energy Sector technologies for Jamaica", "Technology | Capital Cost | Capital Cost Unit",
        f"{name}: {param} {val}", f"{tech} {param}", need)
add(DIB, "4.8 Technology costs", "Table 67", "Technology | Capital Cost | Capital Cost Unit",
    "Table 67 has no rows for crude oil to the refinery (EXTT_CRU) or other petroleum products (DIST_OPE).", "EXTT_CRU; DIST_OPE VariableCost",
    "Add both rows if the proposals are applied: crude at the MSET import value and other petroleum products at the petroleum coke import price.")
add(DIB, "4.8 Technology costs", "Table 67", "Technology | Capital Cost | Capital Cost Unit",
    "Diesel Refinery 10.77; Fuel Oil Refinery 10.88; Gasoline Refinery 12.03; Jet Fuel Refinery 10.39; LPG Refinery 11.15 (Variable Cost MUSD/PJ)", "REF_* VariableCost (other rows, not in scope)",
    "No change proposed by this job; once crude is priced these refinery costs sit on top of the crude price, which the text should explain or the values should be reviewed.")
add("Suplementary.xlsx", "sheet Costos_JAM", "cells L1:Q36 (Energy)", "Import/Distribution - Coal",
    "Source table of Data in Brief Table 67 (same values).", "all Table 67 rows", "Update together with Table 67.")
add(MX, "Step 2 Sector templates, Energy and transport", "", "The energy and transport template follows standard OSeMOSYS",
    "Technology lists are populated with country-specific power plants (type, nameplate capacity, efficiency, commissioning and retirement years, capital and operating costs), refineries, and end-use technologies.",
    "all PP* and DIST_* rows", "Add that fuel enters plants only through supply rows priced at pre-tax import parity in real 2024 USD, projected with IEA WEO 2025 scenarios (STEPS central, CPS high, NZE low), and that plant variable cost is non-fuel O&M.")
add(MX, "Validation", "", "Additional validation avenues include cross-checking model outputs against",
    "sensitivity analysis on key parameters (land-use transition rates, waste growth, technology costs)", "DIST_* VariableCost (CPS, NZE)",
    "Mention the fuel price sensitivity runs that the CPS (high) and NZE (low) fuel price series allow.")
add(JC, "2.2 CLEWISE model architecture and sector modules", "", "CLEWISE is implemented as a linear, least-cost optimization",
    "The model minimizes the discounted sum of investment, operation and maintenance, and fuel costs", "all cost rows",
    "State the fuel cost basis (pre-tax import parity, real 2024 USD, WEO 2025 STEPS) so the least-cost claim rests on sourced prices.")
add(JC, "2.1.1 NDC plateaus and LTS-consistent pathways", "", "In addition to the three harmonized scenarios reported",
    "we also compute a least-cost optimization case", "all cost rows", "Needs re-running after the proposals are written; the least-cost benchmark depends on these costs.")
add(JC, "2.4.3 Normalized indicators", "", "The primary indicators are: Emission-Intensity Index: total",
    "Fuel-Import Exposure: net fossil fuel import expenditure as a share of GDP, normalized to BAU", "DIST_* VariableCost",
    "Values change with the new fuel prices (diesel, gasoline, LPG and natural gas move most); recompute.")
add(JC, "3.5 Normalised indicators for cross-country comparison", "", "In countries like the Dominican Republic, Guatemala, and",
    "In countries like the Dominican Republic, Guatemala, and Jamaica, the ratio remains consistently below the BAU line, indicating that NDC and LTS pathways are more capital-efficient", "PP* CapitalCost",
    "Re-check for Jamaica after re-running with the proposed plant capital costs.")
add(JC, "3.5 Normalised indicators for cross-country comparison", "", "The ΔOPEX/GDP indicator captures the long-term economic burden",
    "In countries like the Dominican Republic, Guatemala, and Jamaica, the indicator remains consistently negative or near the zero line", "DIST_* VariableCost; PP* FixedCost",
    "Re-check for Jamaica after re-running; OPEX includes fuel, which changes.")
add(JC, "3.5 Normalised indicators for cross-country comparison", "", "The change in accumulated investment indicator captures the",
    "In countries such as Guatemala, Honduras, and Jamaica, the accumulated investment index trends sharply downward into negative values", "PP* CapitalCost",
    "Re-check for Jamaica after re-running.")
add("Data_v2.xlsx", "sheet 15. Jamaica_Costos", "Capex2025, Opex2025, CapitalInvestment, Net fossil fuel import expenditure blocks", "Datos de costos CAPEX, OPEX, Investment, Energy Demand",
    "Model results for Jamaica (CAPEX, OPEX, investment, discounted and undiscounted net fossil fuel import expenditure)", "all cost rows",
    "Recompute from the re-run model.")

with open(HERE / "paper_trace.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["document", "section_heading", "table_or_figure", "first_eight_words", "statement_as_written", "model_rows", "what_it_will_need_to_say"])
    w.writerows(rows)
print(len(rows), "paper trace rows")
