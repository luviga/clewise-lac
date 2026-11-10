"""Step 2: paper_trace.csv. Statements on costs, cost sources and fuel prices relevant to Honduras or to all
countries, read from the copies of the CLEWISE paper files (downloads/paper/, not tracked).
Table 62 cells are read from the dump of the Data in Brief; Costos_HON from Suplementary.xlsx."""
import csv
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
DIB, MX, JC = "CLEWISE_DataInBrief.docx", "CLEWISE_MethodsX_v02.docx", "CLEWISE_JCLP_draft_v2.docx"
P = pd.read_csv(HERE / "proposals_summary.csv", keep_default_na=False).set_index(["Tech", "Parameter"])
def prop(t, p):
    try:
        r = P.loc[(t, p)]
    except KeyError:
        return ""
    return f"{r.proposed_2024} in 2024 ({r.basis_classes})"

rows = []
def add(doc, sec, tab, first8, stmt, model_rows, need):
    rows.append(dict(document=doc, section_heading=sec, table_or_figure=tab, first_eight_words=first8,
                     statement_as_written=stmt, model_rows=model_rows, what_it_will_need_to_say=need))

add(DIB, "Specifications Table, Data collection", "Specifications Table", "Compiled from national statistics institutes, national GHG",
    "Compiled from national statistics institutes, ... and international databases (World Bank WDI, FAO FAOSTAT, IRENA, OLADE SIER, UN Population Division).",
    "all Honduras cost rows",
    "Add the cost sources used for Honduras: the ODS/CND expansion plans (PIEG 2024-2033 and 2026-2035), NREL ATB 2024, IEA WEO 2025, EIA, World Bank Pink Sheet, BLS CPI-U, UN Comtrade, BCH, SEN and CCHAC.")
for sec, first8 in [("4.8 Technology costs", "Technology cost data include capital costs (CAPEX in"),
                    ("Appendix (country-specific emission factors), duplicate paragraph", "Technology cost data include capital costs (CAPEX in")]:
    add(DIB, sec, "", first8,
        "Cost projections incorporate learning curves based on IRENA's Renewable Power Generation Costs database and IEA World Energy Outlook assumptions. Country-specific adjustments were applied where national feasibility studies or competitive auction results provided local cost benchmarks.",
        "all Honduras PP rows",
        "Say that Honduras plant costs come from the system operator's expansion plans (ODS/CND PIEG 2024-2033 Tabla 7 and Anexos B; PIEG 2026-2035 Tabla 19) with NREL ATB 2024 Moderate paths for wind, PV and hybrids, and IRENA 2022 for bioenergy.")
    add(DIB, sec, "", first8,
        "Costs in Tables 49-71 are reported as static base-year values in current USD without deflation; time-varying behaviour (technology learning, capital cost decline) is parameterised separately within the OSeMOSYS configuration described in the companion MethodsX article.",
        "all Honduras cost rows",
        "State that fuel supply prices are pre-tax import or wholesale prices in real 2024 USD per GJ on a net calorific basis (WEO 2025 STEPS central, CPS high, NZE low) and give the currency year of each plant cost source (2023 USD to 2023, 2024 USD from 2024 for ODS values; 2022 USD for IRENA 2022 and ATB 2024).")
add(DIB, "4.8 Technology costs", "Table 62", "Table 62. Costs of Energy Sector technologies for", "Table 62. Costs of Energy Sector technologies for Honduras",
    "all Honduras rows in Table 62", "Caption should state the year and currency basis of the values shown (the table prints the first model year values, 2018 for fuel rows).")
T62 = [  # label, values as printed, model row(s), parameters
    ("Import/Distribution - Coal", "Variable Cost 2.49 M USD/PJ", "DIST_COA", ["VariableCost"]),
    ("Import/Distribution - Coke", "Variable Cost 5.59 M USD/PJ", "DIST_COK", ["VariableCost"]),
    ("Import/Distribution - Diesel", "Variable Cost 15.28 M USD/PJ", "DIST_DSL", ["VariableCost"]),
    ("Import/Distribution - Fuel Oil", "Variable Cost 11.02 M USD/PJ", "DIST_FOI", ["VariableCost"]),
    ("Import/Distribution - Gasoline", "Variable Cost 16.94 M USD/PJ", "DIST_GSL", ["VariableCost"]),
    ("Import/Distribution - Kerosene", "Variable Cost 16.26 M USD/PJ", "DIST_KER", ["VariableCost"]),
    ("Import/Distribution - LPG", "Variable Cost 14.1 M USD/PJ", "DIST_LPG", ["VariableCost"]),
    ("Import/Distribution - Natural Gas", "Variable Cost 9.15 M USD/PJ", "DIST_NGS", ["VariableCost"]),
    ("Import - Electricity", "Variable Cost 500 M USD/PJ; Fixed Cost 500 M USD/PJ", "IMP_ELE", ["VariableCost", "FixedCost"]),
    ("Power Plant - Geothermal", "Capital 5900 M USD/GW; Variable 0.36 M USD/PJ; Fixed 153.98 M USD/GW", "PPGEO", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Hydro Dam", "Capital 3576 M USD/GW; Variable 0.44 M USD/PJ; Fixed 47.06 M USD/GW", "PPHDAM", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Hydro Run-of-River", "Capital 2000 M USD/GW; Variable 0.44 M USD/PJ; Fixed 47.06 M USD/GW", "PPHROR", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Distributed Solar", "Capital 871.8 M USD/GW; Variable -; Fixed 25.85 M USD/GW", "PPPVD", ["CapitalCost", "FixedCost"]),
    ("Power Plant - Transmission Solar", "Capital 1254.72 M USD/GW; Variable -; Fixed 25.36 M USD/GW", "PPPVT", ["CapitalCost", "FixedCost"]),
    ("Power Plant - Wind Onshore", "Capital 1716.52 M USD/GW; Variable -; Fixed 36.37 M USD/GW", "PPWNDON", ["CapitalCost", "FixedCost"]),
    ("Power Plant - Biomass", "Capital 5391 M USD/GW; Variable 0.08 M USD/GWh; Fixed 157 M USD/GW", "PPBIM", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Coke", "Capital 4769.52 M USD/GW; Variable 1.41 M USD/PJ; Fixed 45.68 M USD/GW", "PPCOK", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Fuel Oil", "Capital 984.08 M USD/GW; Variable 1.78 M USD/PJ; Fixed 39.57 M USD/GW", "PPFOI", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Gas Turbine Diesel", "Capital 1204.83 M USD/GW; Variable 0.58 M USD/PJ; Fixed 13.73 M USD/GW", "PPGTDSL", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Gas Turbine LPG", "Capital 1204.83 M USD/GW; Variable 1.47 M USD/PJ; Fixed 18.35 M USD/GW", "PPGTGLP", ["CapitalCost", "VariableCost", "FixedCost"]),
    ("Power Plant - Internal Combustion Engine Diesel", "Capital 966.72 M USD/GW; Variable 1.78 M USD/PJ; Fixed 39.57 M USD/GW", "PPICEDSL", ["CapitalCost", "VariableCost", "FixedCost"]),
]
for label, printed, t, params in T62:
    props = "; ".join(f"{p} {prop(t, p)}" for p in params if prop(t, p))
    need = f"Replace with the proposed values and cite their sources: {props}." if props else "No proposal in scope."
    if t == "PPBIM":
        need += " The variable cost unit M USD/GWh is a label slip (the model applies the value per PJ)."
    if t.startswith("DIST_"):
        need += " Fuel values are real 2024 USD per GJ (net), pre-tax; the 2018 value printed today is a nominal 2018 model value."
    add(DIB, "4.8 Technology costs", "Table 62", label + " |", f"{label}: {printed}", t, need)
add(DIB, "4.8 Technology costs", "Table 62", "Power Plant - Coal |", "Power Plant - Coal: Capital 4769.52 M USD/GW; Variable 1.41 M USD/GWh; Fixed 13.73 M USD/GW",
    "PPCOA (out of scope)", "Out of scope here; the variable cost unit M USD/GWh and the fixed cost 13.73 (the combined cycle value) differ from the coke plant row; listed as a known-limitation candidate.")
add(DIB, "4.8 Technology costs", "Table 62", "Power Plant - Natural Gas |", "Power Plant - Natural Gas: Capital 1204.83 M USD/GW; Variable 0.58 M USD/PJ; Fixed 13.73 M USD/GW",
    "PPNGS (out of scope: no residual capacity, cannot be built in BAU)", "If PPNGS is kept, the same ODS CCGN row of PIEG 2026-2035 (1,437.59 USD/kW, 16 USD/kW-yr, 3.5 USD/MWh) is the newer edition.")
add(DIB, "5.1 Data source identification", "", "Data sources were identified through a systematic review",
    "(4) peer-reviewed literature and grey literature (national energy plans, technology feasibility studies, IDB/UNDP/GIZ project reports) for technology costs and sector-specific parameters not available in statistical databases.",
    "all Honduras PP rows", "Consistent with the proposals; name the national plan used for Honduras (ODS/CND PIEG) and its edition.")
add(DIB, "5.1 Data source identification", "", "For each variable in the dataset, the source",
    "For each variable in the dataset, the source was documented with the specific publication, database table, access date, and URL where applicable.",
    "all Honduras cost rows", "The proposals' source list (URL, table, retrieval date) can serve as this registry for Honduras costs.")
add(DIB, "5.2 Harmonization and gap-filling", "", "The six countries use varying conventions for units,",
    "(b) a common base year of 2021 for the projection starting point, with historical data retained for calibration",
    "all Honduras cost rows", "Add that fuel prices use 2024 as the observed anchor year (real 2024 USD) and are projected from 2025 or 2026 with WEO 2025.")
add(DIB, "References", "[13], [14]", "[13] IRENA. (2023). Renewable Power Generation Costs in", "[13] IRENA (2023) Renewable Power Generation Costs in 2022; [14] IEA (2023) World Energy Outlook 2023.",
    "PPBIM; all PP rows", "Keep [13] (bioenergy); add ODS/CND PIEG 2024-2033 and 2026-2035, NREL ATB 2024, IEA WEO 2025 and the fuel price sources; [14] is no longer the source of any Honduras value.")
add(MX, "Energy and transport template", "", "The energy and transport template follows standard OSeMOSYS",
    "Technology lists are populated with country-specific power plants (type, nameplate capacity, efficiency, commissioning and retirement years, capital and operating costs), refineries, and end-use technologies.",
    "all Honduras PP and DIST rows", "Add that fuels reach plants and demand only through supply rows priced at pre-tax import or wholesale level (real 2024 USD per GJ, net), projected with WEO 2025 scenarios.")
add(MX, "Validation", "", "Additional validation avenues include cross-checking model outputs against",
    "sensitivity analysis on key parameters (land-use transition rates, waste growth, technology costs)",
    "DIST rows", "Fuel price sensitivity is now available as the WEO 2025 CPS (high) and NZE (low) price paths.")
add(MX, "Worked example", "", "[WORKED EXAMPLE: A minimal demonstration using one country",
    "A minimal demonstration using one country (Honduras or Costa Rica, to be selected based on repository readiness).",
    "all Honduras cost rows", "If Honduras is chosen, the example inputs will carry the new cost values and their source list.")
add(JC, "Methods, least-cost case", "", "In addition to the three harmonized scenarios reported",
    "we also compute a least-cost optimization case. This run serves as a technical benchmark", "all Honduras cost rows",
    "State the cost basis of the least-cost run: sourced plant costs (ODS plans) and pre-tax fuel prices in real 2024 USD.")
add(JC, "Methods, model formulation", "", "CLEWISE is implemented as a linear, least-cost optimization",
    "The model minimizes the discounted sum of investment, operation and maintenance, and fuel costs", "all Honduras cost rows",
    "Name the fuel price basis (pre-tax import parity, WEO 2025 STEPS) and the plant cost sources.")
add(JC, "Indicators", "", "The primary indicators are: Emission-Intensity Index: total",
    "Delta CAPEX/GDP and Delta OPEX/GDP ... Change in accumulated investment ... Fuel-Import Exposure: net fossil fuel import expenditure as a share of GDP, normalized to BAU.",
    "all Honduras cost rows", "After a re-run with the new costs, recompute the Honduras indicators; Fuel-Import Exposure moves directly with the new fuel prices (diesel -29%, LNG -40%, coal +51% in 2024).")
add(JC, "Results, Delta CAPEX/GDP", "Figure 10", "In countries like the Dominican Republic, Guatemala, and",
    "Honduras presents the most dynamic capital expenditure profile in the region, with a more pronounced curve that reaches its peak relative efficiency around 2040.",
    "PP rows (capital costs)", "Re-check after the re-run: hydro capital (+43% dam, +89% run-of-river from 2024) and lower bioenergy capital change the Honduras CAPEX profile.")
add(JC, "Results, Delta OPEX/GDP", "Figure 11", "The Delta OPEX/GDP indicator captures the long-term",
    "Honduras demonstrates a highly dynamic operational profile, with the LTS scenario showing a distinct upward trend after 2035.",
    "DIST rows; PP fixed and variable costs", "Re-check after the re-run: lower oil product and LNG prices and lower engine fixed O&M reduce BAU OPEX.")
add(JC, "Results, accumulated investment", "", "The change in accumulated investment indicator captures the",
    "In countries such as Guatemala, Honduras, and Jamaica, the accumulated investment index trends sharply downward into negative values",
    "PP rows (capital costs)", "Re-check the Honduras statement after the re-run.")
add("Suplementary.xlsx", "Sheet Costos_HON", "range E1:K38", "Technology | Capital Cost | Unit | Variable Cost",
    "Energy cost table for Honduras, same values as Data in Brief Table 62", "all Honduras rows in Table 62",
    "Update together with Table 62.")
add("Data_v2.xlsx", "Sheet 11.Honduras_Costos", "range A1:BG200", "Capex2025 [MUSD] BAU Energy IPPU AFOLU Waste",
    "Yearly CAPEX and OPEX results by sector and scenario for Honduras (model outputs)", "all Honduras cost rows",
    "Recompute from the re-run model.")
with open(HERE / "paper_trace.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), pd.DataFrame(rows).document.value_counts().to_dict())
