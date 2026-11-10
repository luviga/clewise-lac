# GAPS LAC_COST_SRC_DR 20261110T025405Z

## Judgement calls

- Natural gas chosen point: the import CIF (DR customs, LNG, 8.936 USD/GJ net) instead of the first point in F2 order (MICM wholesale import parity, 8.666 USD/GJ gross, 9.629 net). Reason: rule F2 says market over administrative, and the MICM natural gas PPI is fixed in pesos and changes twice a year. It is also the option that changes the current value least (+17 percent against +26 percent).
- Kerosene chosen point: the MICM kerosene import parity (19.889 USD/GJ), although that row follows a frozen retail price. No market value for kerosene is published; the market-tracking jet fuel parity (20.015) differs by 0.6 percent and is recorded beside it.
- Fuel oil: the MICM Fuel Oil No. 6 parity (13.352) is chosen; the FO 1%S grade (14.950) is recorded beside it.
- Petroleum coke and LPG are benchmarked to Brent and the WEO crude oil price, as rule F4 says for oil products, although petroleum coke trades against coal and LPG against Mont Belvieu propane. With the multi-year r, petroleum coke rises from 2.62 USD/GJ in 2024 to 3.69 in 2026 (step 35 percent) because the 2024 ratio to Brent (0.19) is below the 2019 to 2025 average (0.26).
- Coal: the WEO 2025 European Union steam coal series is used for the projection (DR coal reference Platts FOB Puerto Bolivar, Atlantic basin) and the World Bank Coal South African series (fob Richards Bay NAR 6000) as observed benchmark for r, because the Pink Sheet annual file has no Colombian coal column.
- Year 2025: treated as a history year (benchmark observed in 2025) for every row; where the chosen point has no 2025 observation the value is r times the 2025 benchmark. Projected years start in 2026 for all rows.
- History before the first observation (2018 for every row, and 2020 and 2021 for some) uses r times the benchmark, per F3. Comtrade weights flagged as estimated (2019, 2022 and 2023 coal; 2022 petroleum coke; 2019 LPG; 2023 crude) are used as published.
- Plant costs are left in their source currency year (PEN 2021 USD, IRENA 2022 USD, ATB 2022 or 2023 USD); the brief asks for real 2024 USD only for fuel prices.
- IEA WEO 2023 and 2025 technology cost tables cover only the United States, the European Union, China and India and combine O&M with fuel; they were checked for matches and not used as the replacement source. The national plan (PEN) is the first covering source for thermal plants; IRENA for PV, wind, hydropower and bioenergy levels; NREL ATB for paths.
- IRENA values are matched only against the year they report (2022). Where no source matches, a replacement takes the IRENA 2022 level (cited edition) and, for PV and wind, the ATB 2024 Moderate trajectory from 2022 on; the newer IRENA 2024 values are written in the derivation, not proposed.
- Matched rows whose cited table has a newer edition (ATB 2023 to ATB 2024 for PPHDAM and PPPVD) take the newer value as `matched, newer edition` (change class upgrade), and the cited value is kept in `plant_costs.csv` column cited_edition_value.
- Generic thermal plants (12 technologies) share the PEN Tabla 220 combined cycle figures. The capital cost path after 2022 follows the ATB 2024 NG 2-on-1 Combined Cycle (F-Frame) trajectory scaled to 1,084 USD/kW, because the current decline matches no source.
- `PPCCTDSL` variable O&M takes PEN Tabla 220 (combined cycle), although its capital and fixed values match Tabla 229 (engines) by number.
- PV and wind keep the storage adder the current rows apply from 2025 (the 2025 adder equals ATB 2023 4Hr battery OCC Conservative 2025, 1,836.85 USD/kW, and 35.90 USD/kW-yr fixed O&M). The proposal uses the ATB 2024 4Hr battery CAPEX and fixed O&M (Moderate) for the adder.
- `PPBGS` fixed O&M uses ATB 2024 Biopower Dedicated (163.67 USD/kW-yr) because IRENA 2022 gives only a range (2 to 6 percent of capital per year). This avoids an ASSUMPTION row.
- `PPDHYD` fixed O&M = 2.5 percent of 2,881 USD/kW (IEA average quoted by IRENA 2022 page 162).
- Current values: the A-O workbook fills only the 2018 cell for most rows; the current value in the proposals is the BAU compiled value, and rows writing an empty cell are `fill_empty`.
- PR number and commit hash are not written in REPORT because the brief allows one commit; they are in the pull request and the final summary.

## ASSUMPTION rows

None with basis ASSUMPTION. The `DIST_NGS` rows that use Henry Hub carry the brief's gas gross-to-net sentence; leads for `DIST_NGS` are in `search_log.csv` (EIA LNG exports by country, TotalEnergies release, AES 10-K not opened).

## Proposed changes above 25 percent

Source: `proposals_summary.csv` (STEPS for fuel rows).

| Technology | Parameter | Year | Current | Proposed | Change | Likely cause |
|---|---|---|---|---|---|---|
| `DIST_COA` | VariableCost | 2024 | 9.6054 | 3.9747 | -59% | current values are about 2.4 times the 2024 customs CIF (3.97 USD/GJ); the current 2024 value tracks the 2022 price spike |
| `DIST_COK` | VariableCost | 2024 | 4.9447 | 2.6222 | -47% | current values grow by a percent rule; the customs CIF of petroleum coke is 2.62 USD/GJ and the projection follows Brent through WEO |
| `DIST_COK` | VariableCost | 2030 | 5.5358 | 3.7072 | -33% | current values grow by a percent rule; the customs CIF of petroleum coke is 2.62 USD/GJ and the projection follows Brent through WEO |
| `DIST_COK` | VariableCost | 2050 | 8.0662 | 3.5420 | -56% | current values grow by a percent rule; the customs CIF of petroleum coke is 2.62 USD/GJ and the projection follows Brent through WEO |
| `DIST_DSL` | VariableCost | 2050 | 33.4306 | 17.2275 | -48% | the current row grows by a percent rule to 33.4 USD/GJ in 2050; the WEO 2025 STEPS crude path is flat to falling |
| `DIST_GSL` | VariableCost | 2030 | 28.0535 | 19.7491 | -30% | same percent growth rule in the current row; the market import cost is 19.61 USD/GJ |
| `DIST_GSL` | VariableCost | 2050 | 40.8762 | 18.8689 | -54% | same percent growth rule in the current row; the market import cost is 19.61 USD/GJ |
| `DIST_LPG` | VariableCost | 2024 | 29.4676 | 11.0415 | -63% | current 29.47 USD/GJ is a retail-type value; the DR customs CIF is 11.04 USD/GJ and the MICM parity 15.25 |
| `DIST_LPG` | VariableCost | 2030 | 32.9906 | 11.1484 | -66% | current 29.47 USD/GJ is a retail-type value; the DR customs CIF is 11.04 USD/GJ and the MICM parity 15.25 |
| `DIST_LPG` | VariableCost | 2050 | 48.0700 | 10.6515 | -78% | current 29.47 USD/GJ is a retail-type value; the DR customs CIF is 11.04 USD/GJ and the MICM parity 15.25 |
| `DIST_NGS` | VariableCost | 2030 | 2.9863 | 8.7926 | 194% | the current row falls to 3.2 USD/GJ by 2050; the WEO 2025 US gas price rises from 2.2 to 4.6 USD/MBtu in STEPS and r is 2.68 (LNG over Henry Hub) |
| `DIST_NGS` | VariableCost | 2050 | 3.1850 | 12.9334 | 306% | the current row falls to 3.2 USD/GJ by 2050; the WEO 2025 US gas price rises from 2.2 to 4.6 USD/MBtu in STEPS and r is 2.68 (LNG over Henry Hub) |
| `PPADSL` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPADSL` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPADSL` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPAFOI` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPAFOI` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPAFOI` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPANGS` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPANGS` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPANGS` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPBIM` | CapitalCost | 2024 | 38.4600 | 2,162.0000 | 5,521% | current 38.46 USD/kW has no external source; IRENA 2022 bioenergy is 2,162 |
| `PPBIM` | CapitalCost | 2030 | 38.4600 | 2,162.0000 | 5,521% | current 38.46 USD/kW has no external source; IRENA 2022 bioenergy is 2,162 |
| `PPBIM` | CapitalCost | 2050 | 38.4600 | 2,162.0000 | 5,521% | current 38.46 USD/kW has no external source; IRENA 2022 bioenergy is 2,162 |
| `PPCCTDSL` | VariableCost | 2024 | 3.1767 | 0.7083 | -78% | current 3.18 USD/GJ (11.4 USD/MWh) has no source; PEN Tabla 220 combined cycle 2.55 USD/MWh |
| `PPCCTDSL` | VariableCost | 2030 | 3.1767 | 0.7083 | -78% | current 3.18 USD/GJ (11.4 USD/MWh) has no source; PEN Tabla 220 combined cycle 2.55 USD/MWh |
| `PPCCTDSL` | VariableCost | 2050 | 3.1767 | 0.7083 | -78% | current 3.18 USD/GJ (11.4 USD/MWh) has no source; PEN Tabla 220 combined cycle 2.55 USD/MWh |
| `PPCCTNGS` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPCCTNGS` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPCCTNGS` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPCOA` | FixedCost | 2024 | 82.0000 | 40.5800 | -51% | PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh) |
| `PPCOA` | FixedCost | 2030 | 82.0000 | 40.5800 | -51% | PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh) |
| `PPCOA` | FixedCost | 2050 | 82.0000 | 40.5800 | -51% | PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh) |
| `PPCOA` | VariableCost | 2024 | 0.7056 | 1.2500 | 77% | PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh) |
| `PPCOA` | VariableCost | 2030 | 0.7056 | 1.2500 | 77% | PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh) |
| `PPCOA` | VariableCost | 2050 | 0.7056 | 1.2500 | 77% | PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh) |
| `PPDBGS` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDBGS` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDBGS` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDBIM` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDBIM` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDBIM` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDDSL` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDDSL` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDDSL` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDFOI` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDFOI` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDFOI` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDGLP` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDGLP` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDGLP` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDGSL` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDGSL` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDGSL` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDHYD` | CapitalCost | 2024 | 1,980.0000 | 2,881.0000 | 46% | current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M |
| `PPDHYD` | CapitalCost | 2030 | 1,980.0000 | 2,881.0000 | 46% | current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M |
| `PPDHYD` | CapitalCost | 2050 | 1,980.0000 | 2,881.0000 | 46% | current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M |
| `PPDHYD` | FixedCost | 2024 | 20.0000 | 72.0250 | 260% | current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M |
| `PPDHYD` | FixedCost | 2030 | 20.0000 | 72.0250 | 260% | current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M |
| `PPDHYD` | FixedCost | 2050 | 20.0000 | 72.0250 | 260% | current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M |
| `PPDNGS` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDNGS` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPDNGS` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPICEFOI` | VariableCost | 2024 | 1.0410 | 1.5806 | 52% | current 1.04 USD/GJ (3.75 USD/MWh) has no source; PEN Tabla 229 engines 5.69 USD/MWh |
| `PPICEFOI` | VariableCost | 2030 | 1.0410 | 1.5806 | 52% | current 1.04 USD/GJ (3.75 USD/MWh) has no source; PEN Tabla 229 engines 5.69 USD/MWh |
| `PPICEFOI` | VariableCost | 2050 | 1.0410 | 1.5806 | 52% | current 1.04 USD/GJ (3.75 USD/MWh) has no source; PEN Tabla 229 engines 5.69 USD/MWh |
| `PPICEGASFOI` | VariableCost | 2024 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPICEGASFOI` | VariableCost | 2030 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPICEGASFOI` | VariableCost | 2050 | 0.3751 | 0.7083 | 89% | PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ |
| `PPPVD` | FixedCost | 2050 | 18.0000 | 11.1240 | -38% | ATB 2024 CommPV fixed O&M falls over time while the current value is flat at 18 |
| `PPPVT` | FixedCost | 2024 | 13.5466 | 21.6089 | 60% | ATB 2024 UtilityPV fixed O&M (21.6 USD/kW-yr in 2024) is above the current 13.5 |
| `PPPVTHYD` | FixedCost | 2024 | 13.5466 | 21.6089 | 60% | same as PPPVT |

## Sources blocked or paywalled

- SIE resolution SIE-064-2022-TF (workbook reference for PV and wind 2018 levels): not found in a short search.
- bvearmb.do repository copy of the PEN and the energiaestrategica.com PEN draft: HTTP 403.
- totalenergies.com/node/26486: HTTP 410; Business Wire copy of the release: HTTP 403 (the TotalEnergies newsroom page was used).
- AES Corporation Form 10-K on sec.gov: not opened, because the SEC asks automated clients for a contact address.
- CNE documents page loads its file list through a script; the PEN file was reached in a browser and downloaded through the listed link, which carries a list token that may expire.

## Known-limitation candidates

- `EXTT_CRU` (Primary Techs): domestic crude extraction with VariableCost 0 and an activity upper limit of 43.2 PJ in 2024 (51.5 PJ maximum), producing the same fuel E1CRU as `DIST_CRU`; the DR produces no crude.
- `PRO_COA` (Primary Techs): domestic coal production with VariableCost 0 and an activity upper limit of 3.1 PJ in 2024 (3.6 PJ maximum), producing E1COA like `DIST_COA`; the DR produces no coal.
- Generic thermal plants: twelve technologies (isolated, self-producer, engines and combined cycle) share the PEN combined cycle cost figures (Secondary Techs).
- `PPPVT`, `PPPVTHYD`, `PPWNDON`: a battery storage cost is added to the plant cost from 2025 (Primary Techs); whether the model also represents the storage service is not checked.
- Unit labels: plant VariableCost rows are labelled M US$ / GWh for some technologies (for example PPHDAM, PPPVT, PPWNDON) and M US$ / PJ for others; all affected values are 0.
- Supply rows use the projection mode Percent growth of incomplete years, with only the 2018 cell filled (Primary Techs).
- MICM kerosene, gasoline and LPG parities are residuals of frozen retail prices (from LAC_LOCAL_PRICES notes).
- Plant costs mix currency years (2021 to 2024 USD) while fuel prices are real 2024 USD.
- PPPVT FixedCost 2024 is 13.5466 (section 5 of the brief shows 13.6).

## Left unchecked

- Whether the PEN 2025-2038 (reported to be in consultation) has newer generic project tables.
- The SIE-064-2022-TF resolution text.
- Country-level IRENA data for the DR (IRENA charts list the DR for onshore wind and PV installed costs; values not read from charts).
- Plant rows outside section 5 (other technologies are listed in `cost_rows_current.csv` only).
- Whether LAC_COST_WRITE changes projection modes when it writes year cells.

## Incidents

- The session was interrupted once at the start of Step 2 (paper file search); the step was restarted with a time limit and completed.
- First fuel summary read the workbook 2024 cell (empty for most rows); corrected to the BAU compiled value.
- IRENA single-year values were first matched against every year; corrected to match only 2022.
- Gate 7a first flagged URLs as machine paths (the pattern matched the scheme separator of https links); the pattern was corrected.
- One patch to `gates.py` by text replacement did not apply because of escaping; the line was edited directly.
