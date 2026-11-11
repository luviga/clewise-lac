"""Write search_log.csv: every lead tried for the fuel rows, the plants and the electricity import row (date 2026-11-10).
Import leads come from imp_leads.csv when present (written from the import research step)."""
import csv
from pathlib import Path
HERE = Path(__file__).parent
D = "2026-11-10"
ODS23 = "https://cnd.enee.hn/wp-content/uploads/2024/07/G01-PIEG-2024-2033-Aprobado.pdf"
ODS23A = "https://cnd.enee.hn/wp-content/uploads/2024/07/G02-Anexos-PIEG-2024-2033-Aprobado.pdf"
ODS26 = "https://cnd.enee.hn/wp-content/uploads/2026/09/Informe-PIEG-2026-2035.pdf"
ODS26A = "https://cnd.enee.hn/wp-content/uploads/2026/09/Anexos-PIEG-2026-2035.pdf"
IR22 = "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf"
IR25 = "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf"
WEO23 = "https://www.iea.org/files/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf"
ATB = "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2024/v4.0.0/ATBe.csv"
L = []
def add(row, lead, url, result):
    L.append(dict(row=row, lead=lead, url_or_query=url, date=D, result=result))

# ---- fuel rows ----
add("DIST_COA;DIST_COK;DIST_DSL;DIST_FOI;DIST_GSL;DIST_KER;DIST_LPG;DIST_NGS", "Published 2024 price points and 2018 to 2025 history for Honduras", "LAC_LOCAL_PRICES local_prices_2024.csv and local_history.csv (reused source ids HON-001 to HON-067)", "Chosen points by rule F2: wholesale import parity for DSL, GSL, KER, LPG; import CIF for COA, COK, FOI; generator delivered (ODS LNG chain) for NGS")
add("DIST_COA", "Origin of Honduras coal imports (Comtrade mirror, exports to Honduras 2024)", "https://comtradeapi.un.org/public/v1/preview/C/A/HS?period=2024&partnerCode=340&flowCode=X&cmdCode=270112,271311", "Colombia reports 27.5 kt of HS 270112 to Honduras at 99.4 USD/t FOB, equal to the 27.5 kt Honduras imported; USA reports 66 kt coal and 530 kt petroleum coke. Coal origin confirmed as Colombia")
add("DIST_COA", "ODS coal price method", ODS26, "Section 5.3.4 (page 56): FOB Colombia (Platts) for the monthly path, EIA AEO for the long term, freight 0.549 USD/MMBtu, 5 percent local cost")
add("DIST_COA;DIST_COK", "Free observed Colombian coal FOB benchmark", "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx", "Monthly Pink Sheet lists Coal Australian and Coal South African only; no Colombian series. South African (fob Richards Bay, NAR 6000) used as the observed Atlantic benchmark; WEO European Union steam coal (imports) as the projection series")
add("DIST_COA;DIST_COK", "Comtrade 2025 Honduras imports of HS 270112 and 271311", "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=340&period=2025&partnerCode=0&flowCode=M&cmdCode=270112,271311", "count 0, no 2025 data; 2025 projected")
add("DIST_COK", "Free petroleum coke price benchmark", "World Bank Pink Sheet annual and monthly; EIA spot price tables", "No free petroleum coke benchmark; the coal benchmark and WEO steam coal series are used")
add("DIST_NGS", "Index of the Honduras LNG price", ODS26, "Section 5.3.5 (pages 56 to 57): LNG chain referenced to Henry Hub plus 15 percent, liquefaction 2.0, shipping 0.3, regasification 1.0 USD/MMBtu; confirms Henry Hub benchmark and WEO United States gas series")
add("DIST_DSL;DIST_GSL;DIST_KER", "Full-year 2024 weekly import parity structure", "SEN/DGHB weekly structures (LAC_LOCAL_PRICES search log)", "Only one week (27 May to 2 June 2024) is public; used as published")
add("ALL fuel rows", "IEA WEO 2025 fuel price table", "https://www.iea.org/reports/world-energy-outlook-2025", "Table 2.3 (PDF page 109), not 2.32: USD (MER, 2024), years 2024, 2035, 2050, scenarios CPS, STEPS, NZE")
add("ALL fuel rows", "US CPI-U annual averages (CUUR0000SA0)", "https://api.bls.gov/publicAPI/v1/timeseries/data/ POST seriesid CUUR0000SA0 2016 to 2025", "200; monthly values 2016 to 2025; October 2025 not published, 2025 mean over 11 months")
add("ALL fuel rows", "EIA Brent and Henry Hub annual spot series", "https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls; https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls", "200; annual averages 2018 to 2025")

# ---- plants ----
add("ALL plants", "CLEWISE Data in Brief, section 4.8 and Table 62", "copies of the paper files (leads only)", "Names IRENA Renewable Power Generation Costs 2022 [13] and IEA WEO 2023 [14]; Table 62 prints the 2018 to 2021 workbook values")
add("ALL plants", "IRENA Renewable Power Generation Costs in 2022 (edition cited)", IR22, "200, 48.2 MB, saved. Table H.1 (page 15): bioenergy 2,162, geothermal 3,478, hydropower 2,881, solar PV 876, onshore wind 1,274 USD/kW (2022). None of the current Honduras values appear")
add("ALL plants", "IRENA Renewable Power Generation Costs in 2025 (newest edition)", IR25, "200, 73.4 MB, saved. Figure S1 (page 14): bioenergy 3,606, geothermal 5,997, hydropower 2,079, solar PV 667, onshore wind 976 USD/kW (2025); bioenergy variable O&M 0.004 USD/kWh. No current Honduras value appears")
add("ALL plants", "IEA WEO 2023 Annex B power generation technology costs (edition cited)", WEO23, "200, 16.0 MB, saved. Table B.4a (PDF page 301) covers nuclear, coal, gas CCGT, solar PV, wind on and offshore for the US, EU, China and India only; no hydro, bioenergy, geothermal, engines or gas turbines; no current Honduras value appears")
add("ALL plants", "IEA WEO 2025 Annex B (same table, newer edition)", "https://www.iea.org/reports/world-energy-outlook-2025", "Tables B.4a and B.4b cover the same technologies and regions; no Central America values")
add("ALL plants", "ODS/CND Plan Indicativo de Expansion de la Generacion 2024-2033 (national plan)", ODS23, "200, saved. Tabla 7 (PDF page 42, 2023 USD) gives every current value except bioenergy and distributed PV fixed O&M: 871.80, 1,254.72, 1,716.52, 5,900, 984.08, 966.72, 1,024.63, 1,204.83, 4,769.52, 2,000, 3,576 USD/kW and the fixed and variable O&M values")
add("PPPVT;PPWNDON", "ODS PIEG 2024-2033 Anexos, cost projections", ODS23A, "200, saved. Tabla B-2 (PDF page 18) and Tabla B-3 (PDF page 19) give the yearly 2023 to 2042 capital and fixed O&M paths that the model carries for PPPVT and PPWNDON")
add("ALL plants", "ODS/CND PIEG 2026-2035 (newer edition of the same table)", ODS26, "Tabla 19 (PDF page 46, 2024 USD): newer values for every row except coal (no coal candidate) and bioenergy; Anexos A.2 (page 22) projects wind, PV and hybrid costs with NREL ATB 2024 Moderate rates from 2024")
add("ALL plants", "NREL ATB 2024 electricity CSV", ATB, "200, 102.7 MB, saved. Moderate, Market, 30-year rows extracted for UtilityPV, ResPV, LandbasedWind, PV-Plus-Battery and Biopower (atb2024_series.csv)")
add("PPBIM", "Bioenergy capital, fixed and variable cost in the ODS plans", ODS23 + "; " + ODS26, "No bioenergy candidate cost in either edition")
add("PPBIM", "Source of 5,391 to 3,871 USD/kW, 157 USD/kW-yr and 0.08", IR22 + "; " + WEO23 + "; " + ATB, "Not in IRENA 2022, WEO 2023 or ATB 2024 (ATB 2024 Biopower OCC 4,830 in 2022 and 4,497 in 2024; CAPEX 5,528 and 5,154; fixed O&M 163.67; variable O&M 5.25 USD/MWh). Replaced: IRENA 2022 capital 2,162 USD/kW and variable O&M 0.005 USD/kWh; IRENA gives fixed O&M only as 2 to 6 percent of capital, so ATB fixed O&M is used")
add("PPBIM", "IRENA 2022 regional bioenergy installed cost (Central America)", IR22, "Regional values only in figures (Figure 8.2, page 181); no Central America number in text or tables; global weighted average used")
add("PPPVD", "Distributed PV fixed O&M path 25.85 to 11.40 USD/kW-yr", IR22 + "; " + IR25 + "; " + WEO23 + "; " + ODS23 + "; " + ODS26, "No source gives the path; IRENA and WEO publish no residential or commercial PV O&M; ODS plans cover utility PV only. Replaced with NREL ATB 2024 ResPV Moderate fixed O&M")
add("PPGTDSL;PPGTGLP", "Gas turbine rows in ODS Tabla 7", ODS23, "PPGTDSL carries the CCGN 250 MW row (1,204.83, 13.73, 2.10); PPGTGLP carries the CCGN capital cost and the LPG 30 MW fixed and variable O&M (18.35, 5.29); LPG row capital is 1,024.63")
add("PPCOK", "Coal or petroleum coke plant in ODS PIEG 2026-2035", ODS26, "No new coal candidate in Tabla 19; Tabla 20 (page 47) lists a Becosa-like 105 MW steam unit valued at the capacity reference price (1,537.12 USD/kW), not a cost estimate; the 2024-2033 values are kept")
add("PPHDAM;PPHROR", "Hydro variable O&M", ODS23 + "; " + ODS26, "2024-2033 Tabla 7 gives 1.57 USD/MWh; 2026-2035 Tabla 19 gives 0.00 USD/MWh, equal to the model's empty value")

imp = HERE / "imp_leads.csv"
if imp.exists():
    import pandas as pd
    for r in pd.read_csv(imp, keep_default_na=False).itertuples():
        add("IMP_ELE", r.lead, r.url_or_query, r.result)
with open(HERE / "search_log.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["row", "lead", "url_or_query", "date", "result"]); w.writeheader(); w.writerows(L)
print(len(L), "leads")
