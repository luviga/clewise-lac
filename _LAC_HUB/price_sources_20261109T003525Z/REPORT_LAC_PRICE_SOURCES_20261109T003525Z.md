# REPORT LAC_PRICE_SOURCES 20261109T003525Z

Source plan for pre-tax import parity fuel prices in Costa Rica, the Dominican Republic, Ecuador, Guatemala, Honduras and Jamaica.
Run stamp 20261109T003525Z (UTC). All files are in `_LAC_HUB/price_sources_20261109T003525Z/`. No model file was changed and no final price series was built.

## Gate results

| Gate | Result |
|---|---|
| 1. Read-only: SHA-256 of the six A-O energy workbooks and `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx`, before Step 1 and after Step 5 | PASS. All 7 hashes match (`baseline_before.csv`, `baseline_after.csv`). |
| 2. Nothing written outside the output folder | PASS inside MODELS_LAC_5: the only other new files are in `_LAC_HUB/formula_check_20261109T003529Z/`, which belongs to the parallel formula job. One deviation outside MODELS_LAC_5: the country sub-tasks left 7 scratch files (HTML pages and PNG renders) in Claude's session temp scratchpad, and one fetch tool cached a PDF in its own temp folder. None of these is a model file, but they are outside the output folder (see GAPS). |
| 3. Every source opened in this session; `sources.csv` lists each | PASS with one note. `sources.csv` has 388 rows: 32 opened in the main session and 356 opened and downloaded by the six country sub-tasks run in this session. One value per country was re-checked against the downloaded document in the main session (see Step 4). |
| 4. Every number in REPORT traces to a CSV or downloaded file | PASS. Each table names its CSV. |

## Short answer

### Proposed benchmark set (one set for all six countries)

| Fuel | Benchmark | Publisher | 2024 value, USD/GJ |
|---|---|---|---|
| Crude oil | Brent spot FOB | EIA | 13.94 |
| Gasoline | US Gulf Coast conventional regular gasoline spot FOB | EIA | 18.02 |
| Diesel | US Gulf Coast ULSD spot | EIA | 16.72 |
| Jet fuel | US Gulf Coast kerosene-type jet fuel spot FOB | EIA | 17.28 |
| Kerosene | Same jet series, on the kerosene net calorific value | EIA | 17.40 |
| LPG | Mont Belvieu propane spot FOB | EIA | 8.06 |
| Fuel oil | PROXY: Brent x 0.814 (ratio of ARESEP 2024 FOB bunker to Brent) | EIA and ARESEP | 11.34 |
| Aviation gasoline | PROXY: USGC gasoline x 1.579 (EIA PADD 3 avgas resale ratio, 2018-2021) | EIA | 28.46 |
| Natural gas (LNG) | Henry Hub spot (gross calorific basis) | EIA | 2.08 |
| Coal | South African coal fob Richards Bay, NAR 6000 kcal/kg | World Bank Pink Sheet | 4.21 |
| Petroleum coke | PROXY: average cost of petroleum coke delivered to US power plants | EIA Electric Power Monthly | 2.81 |

Sources: `benchmarks.csv`, `history_usd_per_gj.csv`. All oil products come from one publisher (EIA), so the six countries share one base.

### Projection source and cases

EIA Annual Energy Outlook 2025 (15 April 2025): Reference (REF), High Oil Price (HIGH) and Low Oil Price (LOW), 2024 to 2050, published in real 2024 dollars and in nominal dollars. Drivers are Brent (Table 12), Henry Hub (Table 13) and the US coal export price (Table 15). AEO2026 (8 April 2026) is newer but has no oil price cases. Products follow Brent by a constant ratio. LNG is Henry Hub plus a fixed adder. Coal follows the AEO coal export price index. Petcoke follows coal. See `projections.csv` and `projection_method.md`.

Brent, 2024 USD/bbl: REF 81.45 (2026), 79.80 (2030), 91.46 (2050); HIGH 123.91, 124.23, 157.11; LOW 38.53, 41.34, 48.10 (`projections.csv`).

### Adder status by country and fuel (2024, USD/GJ)

O = observed from a regulator price structure or a regulator-published delivered price. O+M = observed import cost, with the margin as an ASSUMPTION candidate (median of published margins). B = built from published rates or regional regulator data. A = ASSUMPTION candidate. "n/m" = no model row. Values are the total adder from `adders_2024.csv`.

| Fuel | Costa Rica | Dominican Rep. | Guatemala | Honduras | Jamaica | Ecuador |
|---|---|---|---|---|---|---|
| Diesel | O 2.36 | O 1.87 | O 3.42 | O+M 3.73 | B 3.21 | O+M 2.96 |
| Gasoline | O 1.85 | O 3.64 (administrative parity) | O 3.92 | O+M 2.33 | B 3.62 | O+M 4.33 |
| LPG | O 5.15 | O 8.66 (administrative parity) | O 4.82 | O 4.27 | O+M 2.34 | O+M 5.07 |
| Kerosene | O 3.18 | O 3.71 | B 3.45 | O+M 2.95 | B 3.45 | B 3.45 |
| Jet fuel | O 4.93 (row IMPKJF) | n/m (O 4.69) | n/m | n/m | B 4.81 | O+M 8.71 |
| Fuel oil | O 4.64 | O 2.19 | O 3.52 | O 0.71 (delivered) | O 1.43 (delivered, Jun-Jul) | B 4.64 |
| Natural gas (LNG) | B 5.68 | O 9.33 | B 5.68 | B 5.68 | O 7.77 (delivered, Jun-Jul) | B 5.68 |
| Coal | A 1.00 | A 1.00 | A 1.00 | A 1.00 | A 1.00 | A 1.00 |
| Petroleum coke | A 0.80 | A 0.80 | A 0.80 | A 0.80 | A 0.80 | A 0.80 |
| Crude oil | n/m | A 0.35 | n/m | n/m | n/m | A 0.35 |
| Aviation gasoline | O 12.22 | n/m | n/m | n/m | n/m | n/m |

### What cannot be sourced

- No free international benchmark for fuel oil, aviation gasoline or petroleum coke. Platts and Argus are the only origin of USGC HSFO, avgas and petcoke spot quotes and are paywalled; proxies are used.
- No published delivered coal or petroleum coke price was retrieved for any of the six countries, so those adders are ASSUMPTION candidates.
- No published crude import cost for the Dominican Republic or Ecuador.
- Jamaica: no published pre-tax product price. Petrojam's website refused automated access, and press reports give tax-inclusive prices.
- Honduras: no published import parity structure for liquid fuels except LPG, so margins are not published.
- Ecuador: import costs are published, margins are not.
- No LNG price for Costa Rica, Guatemala, Honduras or Ecuador (none import LNG at scale in 2024).

### Decisions Luis must take before a build job

1. Real or nominal. Proposed: real 2024 USD, from the AEO2025 real series.
2. Projection edition. Proposed: AEO2025, the latest edition with High and Low Oil Price cases. The alternative is AEO2026 Reference with no matching HIGH and LOW.
3. How to treat 2026. Observed Brent averaged 96.3 USD/bbl over January to October 2026 (`monthly_benchmarks.csv`), against 81.45 (2024 USD) in AEO2025 REF. Options: (a) use AEO2025 from 2026; (b) use observed 2026 and the World Bank CMO October 2026 forecast for 2027 and 2028 (79 and 70 USD/bbl, nominal), then AEO2025; (c) start the projection in 2027.
4. Product ratio period. Proposed: 2018-2025 mean (diesel 1.249, gasoline 1.310, jet 1.260, LPG 0.648). The 2021-2025 alternative is about 3 percent higher.
5. Fuel oil proxy. Proposed: Brent x 0.814 (ARESEP 2024 FOB bunker, one year). Alternative: 0.946 from the discontinued EIA US residual resale price (2018-2021), which gives a fuel oil benchmark 16 percent higher.
6. Calorific basis for natural gas. Henry Hub and the LNG observations are on a gross basis; oil benchmarks use net calorific values. If the models are on a net basis, the gas prices need a gross-to-net factor that this job did not source.
7. Margin scope. Proposed: include the importer or terminal and wholesale margin; exclude retail margin and inland freight to stations. Costa Rica's RECOPE margin K is large for jet (3.68), fuel oil (3.20) and avgas (4.93 USD/GJ).
8. Dominican Republic gasoline and LPG. Their 2024 import parity was an administrative figure under a retail price freeze. Accept it, or use a built adder from the other countries.
9. Ecuador fuel oil. Import parity (built 4.64) or export parity (EP Petroecuador export FOB 61.68 USD/bbl = 10.11 USD/GJ, 1.24 below the benchmark).
10. Coal benchmark: South African (proposed, Atlantic basin, net basis stated) or Australian Newcastle (5.42 USD/GJ in 2024).
11. Whether ASSUMPTION candidates for coal (1.0, range 0.6-1.6), petcoke (0.8, range 0.5-1.2), crude (0.35, range 0.17-0.52) and built LNG (5.68, range 4.73-8.53 USD/GJ) are acceptable.

## Step 1. Benchmarks

Full list with series codes, URLs, frequency and coverage: `benchmarks.csv`. Downloaded data files: `downloads/PET_PRI_SPT_S1_M.xls` (EIA spot prices, data to 2026-10), `downloads/eia_ng/NG_PRI_FUT_S1_M.xls` (Henry Hub), `downloads/eia_ng/NG_MOVE_EXPC_S1_M.xls` (US LNG export prices by destination), `downloads/CMO-Historical-Data-Monthly.xlsx` (World Bank, updated 3 November 2026), `downloads/eia_epm/table_4_01continued.xlsx` (petroleum coke), `downloads/PET_PRI_REFOTH_A_EPPV_PWG_DPGAL_M.xls` and `downloads/PET_PRI_REFOTH_A_EPPR_PWG_DPGAL_M.xls` (EIA refiner avgas and residual, both ending March 2022).

Proxies:

- Fuel oil: Brent x 0.814. The ratio is the ARESEP "Precio FOB estimado" for bunker in the 12 monthly 2024 resolutions (mean 69.25 USD/bbl, 11.35 USD/GJ) over 2024 Brent (13.94 USD/GJ). It agrees with the Platts fuel oil No. 6 FOB quote of 11.27 USD/MMBtu in the Dominican Ministry of Energy and Mines bulletins (5 months of 2024, `downloads/DR/DR_regulator_2024.csv`).
- Aviation gasoline: USGC gasoline x 1.579, the 2018-2021 mean of the EIA PADD 3 avgas wholesale/resale price over USGC gasoline (`history_ratios.csv`).
- Petroleum coke: EIA average cost delivered to US power plants, 2.96 USD/MMBtu in 2024. Its ratio to the South African coal benchmark averaged 0.638 over 2018-2025.
- Kerosene uses the jet series, because no free USGC household kerosene series exists.

Conversion factors (`history.py`): US gallons per tonne from the 2023 UN Energy Statistics Yearbook, Table II (gasoline 357, diesel 304, jet and kerosene 326, fuel oil 278, LPG 489, avgas 362; crude 7.32 bbl/t). Net calorific values from the 2006 IPCC Guidelines, Vol. 2, Table 1.2 (gasoline 44.3, diesel 43.0, jet 44.1, other kerosene 43.8, residual fuel oil 40.4, LPG 47.3, avgas 44.3, crude 42.3, petcoke 32.5 GJ/t). Coal: 6000 kcal/kg NAR x 4.1868 = 25.12 GJ/t. Gas: 1.055056 GJ/MMBtu and 1.037 MMBtu/Mcf (EIA FAQ, 2025 average).

## Step 2. History, 2018 to 2025

USD/GJ, annual means of monthly data. 2025 has 12 months for every benchmark. Source: `history_usd_per_gj.csv` (each row carries its source URL and conversion).

| Year | Brent | Gasoline | Diesel | Jet | LPG | Fuel oil (proxy) | Avgas (proxy) | Henry Hub | Coal (S. Africa) | Petcoke (proxy) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 12.30 | 15.12 | 14.40 | 14.92 | 9.04 | 10.01 | 23.87 | 3.00 | 3.89 | 2.41 |
| 2019 | 11.14 | 13.69 | 13.31 | 13.88 | 5.61 | 9.07 | 21.62 | 2.43 | 2.86 | 1.81 |
| 2020 | 7.23 | 9.07 | 8.46 | 8.14 | 4.80 | 5.88 | 14.32 | 1.93 | 2.61 | 1.61 |
| 2021 | 12.23 | 16.59 | 14.23 | 13.71 | 10.79 | 9.96 | 26.19 | 3.70 | 4.77 | 3.00 |
| 2022 | 17.44 | 23.72 | 24.75 | 24.89 | 11.44 | 14.20 | 37.46 | 6.08 | 9.58 | 4.12 |
| 2023 | 14.27 | 20.01 | 19.33 | 19.96 | 7.37 | 11.62 | 31.59 | 2.40 | 4.74 | 3.84 |
| 2024 | 13.94 | 18.02 | 16.72 | 17.28 | 8.06 | 11.34 | 28.46 | 2.08 | 4.21 | 2.81 |
| 2025 | 11.96 | 16.26 | 15.74 | 15.65 | 7.76 | 9.73 | 25.68 | 3.34 | 3.78 | 2.65 |

The file also holds the World Bank Brent and Henry Hub series (they match EIA within 1 percent), Australian coal, Japan LNG, and the EIA FOB prices of US LNG exports to the Dominican Republic and Jamaica. The World Bank notes that South African coal values for January to May 2024 are estimates.

## Step 3. Projections, REF, HIGH and LOW, to 2050

Publisher EIA, AEO2025, Tables 12, 13 and 15, cases `ref2025`, `highprice` and `lowprice`, years 2024 to 2050, real 2024 dollars and nominal (`projections.csv`, `projections_usd_per_gj.csv`). Values as published, 2024 dollars:

| Year | Brent REF | Brent HIGH | Brent LOW | HH REF | HH HIGH | HH LOW | Coal exports REF (USD/short ton) | HIGH | LOW |
|---|---|---|---|---|---|---|---|---|---|
| 2024 | 80.49 | 80.49 | 80.49 | 2.19 | 2.19 | 2.19 | 166.67 | 166.68 | 166.70 |
| 2026 | 81.45 | 123.91 | 38.53 | 2.74 | 2.67 | 2.96 | 161.73 | 168.98 | 159.46 |
| 2030 | 79.80 | 124.23 | 41.34 | 3.08 | 2.84 | 3.71 | 160.86 | 167.32 | 158.56 |
| 2040 | 84.66 | 144.93 | 44.91 | 4.27 | 4.65 | 4.94 | 166.96 | 169.80 | 165.65 |
| 2050 | 91.46 | 157.11 | 48.10 | 4.80 | 5.42 | 4.53 | 165.56 | 169.11 | 161.84 |

In these cases Henry Hub and coal hardly move with the oil price, so HIGH and LOW act mainly on oil products. Rules for each fuel, the ratio periods and the bridge from 2025 are in `projection_method.md`. `projections.csv` also holds the World Bank CMO October 2026 short-term forecast (case `WB_baseline`) as a single-case alternative for 2026 to 2028. Jamaica 2051 to 2055: hold 2050 real values.

## Step 4. Freight, insurance and margins (2024)

Full table: `adders_2024.csv` (55 rows, with components and sources). Working lines: `adders_working.txt`. Exchange rates (2024 averages, selling rate where both are published): CRC 518.23 (BCCR daily reference rates), DOP 59.5665 (BCRD annual average), GTQ 7.7596 (Banguat daily reference rates), JMD 157.22 (Bank of Jamaica annual average). Ecuador uses USD; Honduras values used are already in USD.

Each country's extraction is in `downloads/<CC>/<CC>_regulator_2024.csv` with its notes file. In the main session one value per country was re-read from the downloaded document and matched:
- Costa Rica: diesel COA 358.06 CRC/L, January resolution, p.16.
- Honduras: diesel CIF 916,315.08 (thousand USD) over 8,343,045.76 bbl, annual report p.10.
- Guatemala: superior gasoline CIF Q20.82/gal, 3 June structure.
- Dominican Republic: gasoil EGP-C import parity 151.30 DOP/gal, 1-7 June aviso.
- Jamaica: Comtrade HS 271012, 350.5 million USD over 461.6 kt.
- Ecuador: Diesel 2 imports of 9,347,912 bbl and 983,330,632 USD, p.63.

Method: adder = (observed pre-tax import cost minus the 2024 benchmark) plus the published terminal and wholesale margin. Retail margins and inland freight to stations are excluded.

### Full working, diesel

| Country | Observed import cost | Conversion | Import cost USD/GJ | Benchmark | Import adder | Margin | Adder |
|---|---|---|---|---|---|---|---|
| Costa Rica | ARESEP COA 331.11 CRC/L (12 monthly resolutions); RECOPE margin K 38.42 CRC/L | / 518.23 x 3.7854 L/gal x 7.070 gal/GJ | 17.10 | 16.72 | 0.38 | 1.98 | 2.36 |
| Dominican Rep. | MICM import parity, gasoil for generators (EGP-C), 151.38 DOP/gal (50 weeks); distributor margin 5.24 | / 59.5665 x 7.070 | 17.97 | 16.72 | 1.25 | 0.62 | 1.87 |
| Guatemala | MEM Precio CIF 19.96 GTQ/gal (31 weeks); importer margin 1.90 plus other costs 0.25 | / 7.7596 x 7.070 | 18.18 | 16.72 | 1.47 | 1.96 | 3.42 |
| Honduras | SEN annual report CIF unit value 109.83 USD/bbl | / 42 x 7.070 | 18.49 | 16.72 | 1.77 | 1.96 (ASSUMPTION: median of CR, DR, GUA margins, range 0.62-1.98) | 3.73 |
| Jamaica | none published | built: median of observed import adders (1.25) and margins (1.96) | n/a | 16.72 | 1.25 | 1.96 | 3.21 |
| Ecuador | EP Petroecuador 2024 import unit value, all diesel, 105.26 USD/bbl (freight included, insurance excluded) | / 42 x 7.070 | 17.72 | 16.72 | 1.00 | 1.96 (ASSUMPTION, as Honduras) | 2.96 |

Checks: Guatemala's MEM publishes its own daily FOB US Gulf diesel at 17.77 GTQ/gal (2.29 USD/gal), 3 percent below the EIA ULSD average of 2.36 USD/gal, and its CIF minus FOB is 1.99 USD/GJ. In the Dominican Republic the public gasoil import parity (134.44 DOP/gal) was administrative in 2024; the EGP-C row tracks the market.

### Full working, fuel oil

| Country | Observed import cost | Conversion | Import cost USD/GJ | Benchmark (proxy) | Import adder | Margin | Adder |
|---|---|---|---|---|---|---|---|
| Costa Rica | ARESEP COA bunker 254.30 CRC/L (FOB 11.39 plus freight, insurance and port 1.40 USD/GJ); RECOPE margin K 63.58 CRC/L | / 518.23 x 3.7854 x 6.881 gal/GJ | 12.78 | 11.34 | 1.44 | 3.20 | 4.64 |
| Dominican Rep. | MICM import parity fuel oil No. 6, 115.62 DOP/gal (50 weeks); distributor margin 1.54 | / 59.5665 x 6.881 | 13.36 | 11.34 | 2.01 | 0.18 | 2.19 |
| Guatemala | MEM ex-rack Puerto San Jose: CIF 11.61 GTQ/gal (31 weeks); importer margin 4.76, terminal 0.24, port 0.14 | / 7.7596 x 6.881 | 10.30 | 11.34 | -1.04 | 4.56 | 3.52 |
| Honduras | CREE actual bunker price for generation, 73.56 USD/bbl (12 months), delivered | / 42 x 6.881 | 12.05 | 11.34 | 0.71 | included | 0.71 |
| Jamaica | OUR report: HFO to JPS and IPP plants 13.48 USD/MMBtu (8 plant-months, June-July 2024), delivered | / 1.055056 | 12.77 | 11.34 | 1.43 | included | 1.43 |
| Ecuador | none (no imports in 2024; exports at 61.68 USD/bbl FOB) | built: median observed import adder (1.44) and margin (3.20) | n/a | 11.34 | 1.44 | 3.20 | 4.64 |

Checks: Guatemala's monthly unit import value for bunker is 78.14 USD/bbl (12.80 USD/GJ), above the structure CIF, so the structure CIF looks low. Honduras SEN's annual CIF for fuel oil is 76.46 USD/bbl (12.53 USD/GJ). The Jamaica value is on an unstated, probably gross, basis.

### Other fuels, observed values worth noting

- LNG: the EIA FOB price of US LNG to the Dominican Republic averaged 6.34 USD/GJ in 2024, 4.26 above Henry Hub. The MICM importer price to wholesalers (716.72 DOP/MMBtu, 49 weeks) gives an observed DR adder of 9.33 USD/GJ. OUR's Jamaica plant prices give 7.77 USD/GJ (June and July only). The built adder for the other four countries is 4.26 plus small-scale shipping and regasification of 1.5 USD/MMBtu (1.42 USD/GJ), from LNG Industry (2017): 5.68 USD/GJ, range 4.73-8.53.
- LPG: published FOB values agree with Mont Belvieu (Costa Rica 70-30 mix FOB 8.36 USD/GJ; Honduras FOB 8.53 USD/GJ against 8.06). Adders are high because of ocean freight and terminal costs for pressurised cargo (Costa Rica freight, insurance and port 2.38 USD/GJ).
- Aviation gasoline: Costa Rica's COA of 598.89 CRC/L gives 35.75 USD/GJ, 7.29 above the proxy benchmark, so the proxy is weak.

### ASSUMPTION candidates

- Coal: Imported steam coal delivered to the plant or industrial user costs about 1.0 USD/GJ (range 0.6 to 1.6 USD/GJ, equal to 15 to 40 USD/t at 25.1 GJ/t) above the World Bank South African fob Richards Bay benchmark. This covers ocean freight from Colombia or the US Gulf, insurance, port handling and inland transport, held constant in real terms, and applies to all six countries. Check: the Dominican Ministry of Energy and Mines quotes coal fob Puerto Bolivar at 3.58 USD/MMBtu (3.39 USD/GJ) in 2024 months, so the benchmark already sits about 0.8 USD/GJ above the Colombian origin price.
- Petroleum coke: Imported petroleum coke delivered to the cement or power plant costs about 0.8 USD/GJ (range 0.5 to 1.2 USD/GJ, equal to 15 to 40 USD/t at 32.5 GJ/t) above the EIA US delivered petroleum coke proxy. This covers ocean freight from the US Gulf, insurance and port handling, held constant in real terms, and applies to all six countries.
- Crude oil: Imported crude oil delivered to the refinery costs about 0.35 USD/GJ (range 0.17 to 0.52 USD/GJ, equal to 1 to 3 USD/bbl) above Brent. This covers tanker freight in the Caribbean basin and insurance, held constant in real terms, and applies to the Dominican Republic and Ecuador. Check: UN Comtrade puts Jamaica's 2024 crude imports at 586.37 USD/t CIF (13.86 USD/GJ), close to 2024 Brent at 13.94 USD/GJ.
- Margins in Honduras (diesel, gasoline, kerosene), Ecuador (diesel, gasoline, jet, LPG) and Jamaica (LPG): The terminal and wholesale margin equals the median of the margins published in Costa Rica, the Dominican Republic and Guatemala for the same fuel. For diesel this is 1.96 USD/GJ, range 0.62 to 1.98, held constant in real terms.

## Step 5. Sanity check against the models

Model values were read without saving from `Primary Techs` in each `A1_Outputs/A-O_Parametrization.xlsx` (`ao_dsl_foi_2025.csv`). The comparison is with benchmark 2024 plus the Step 4 adder (`sanity_check_2025.csv`). Model units are MUSD/PJ, equal to USD/GJ.

| Country | Fuel | Model 2025 | How the 2025 value is stored | Benchmark 2024 + adder | Ratio model / parity |
|---|---|---|---|---|---|
| Costa Rica | Diesel (IMPPURDSL) | 12.85 | stored | 19.08 | 0.67 |
| Costa Rica | Fuel oil (IMPFOI) | 9.86 | stored | 15.98 | 0.62 |
| Dominican Rep. | Diesel | 18.65 | 2019 value held ("percent growth of incomplete years" mode) | 18.59 | 1.00 |
| Dominican Rep. | Fuel oil | 12.95 | stored | 13.54 | 0.96 |
| Guatemala | Diesel | 18.65 | 2019 value held (same mode) | 20.14 | 0.93 |
| Guatemala | Fuel oil | 12.59 | 2019 value held (same mode) | 14.86 | 0.85 |
| Honduras | Diesel | 25.50 | 2022 value held (same mode) | 20.45 | 1.25 |
| Honduras | Fuel oil | 14.51 | 2022 value held (same mode) | 12.05 | 1.20 |
| Jamaica | Diesel | 19.90 | stored | 19.93 | 1.00 |
| Jamaica | Fuel oil | 12.89 | stored | 12.77 | 1.01 |
| Ecuador | Diesel, fuel oil | 1 | placeholder | 19.68, 15.98 | skipped |

Costa Rica's current values are about one third below 2024 import parity. Honduras holds 2022 crisis-year prices and sits about 20 to 25 percent above. For the three rows in "percent growth of incomplete years" mode, the A-O tool may extend the last stored value differently from the "held" value shown. Ecuador holds placeholders of 1 and was skipped.
