# Ecuador (ECU): local fuel prices 2024, job LAC_LOCAL_PRICES 20261109T085226Z

## Summary

All ten open Ecuador rows now have at least one 2024 value from an Ecuador publisher or from UN Comtrade. No row needs an ASSUMPTION candidate.

prices_ECU.csv has 32 rows: 25 `local regulator or operator`, 1 `local customs or statistics`, 3 `international customs (Comtrade)` and 3 `built from published components`. All values are in USD (Ecuador uses the US dollar).

- Coal `DIST_COA`: import CIF from Comtrade, 237.97 USD/t. Ecuador's 2024 coal imports are 99.6 percent anthracite (HS 270111), 14.7 kt in total. At the IPCC anthracite NCV this is 8.91 USD/GJ. Evidence class: Comtrade.
- Petroleum coke `DIST_COK`: import CIF from Comtrade (HS 271311), 123.31 USD/t or 3.79 USD/GJ. The BCE publishes only the FOB value (21.6 million USD), with no quantity. Evidence class: Comtrade.
- Natural gas `DIST_NGS`, three values:
  - To generators: 3.04 USD/MMBTU excluding VAT, or 2.88 USD/GJ. This is EP Petroecuador's 2024 dispatch value of domestic Amistad gas, 99.7 percent of which went to Termogas Machala.
  - To industry, piped: 3.7705 USD/MMBTU (3.57 USD/GJ), from the EP Petroecuador terminal price structures.
  - To industry, LNG from Bajo Alto: 7.04 USD/MMBTU (6.67 USD/GJ).
- Fuel oil `DIST_FOI`, both sides of the open question:
  - Export: Fuel Oil No. 6 FOB 61.68 USD/bbl (10.11 USD/GJ). No fuel oil was imported by EP Petroecuador in 2024.
  - Delivered to generators: the regulated prices are 0.48 USD/gal for fuel oil No. 4 from La Libertad (3.30 USD/GJ) and 0.62 USD/gal at other dispatch points (4.27 USD/GJ). Fuel oil No. 6 for power cost 0.3634 USD/gal (2.50 USD/GJ, July to December). The actual average paid for fuel oil No. 4 dispatched to power was 0.4807 USD/gal.
  - To industry: fuel oil No. 6 cost 1.6355 USD/gal (11.25 USD/GJ) and residuo 0.894 USD/gal (6.15 USD/GJ).
- Diesel, gasoline, jet fuel and LPG:
  - The import DPU values match the earlier job exactly (both jobs read the same EP Petroecuador table).
  - Each fuel now also has the EP Petroecuador terminal price to unsubsidised industrial buyers. This is a published price, not a margin: the price structures do not split terminal price into import cost and margin.
  - The regulated retail margins (margenes de comercializacion, excluding VAT) are published in Registro Oficial 529: diesel 0.128438 USD/gal, Extra and Ecopais 0.160313 USD/gal, and LPG for taxis and grain drying 0.13 USD/kg.
  - From these, the pre-tax final consumer prices for the subsidised automotive segments are built from published components: diesel 1.5626 USD/gal and Extra 2.2263 USD/gal.
  - Diesel delivered to generators is regulated at 0.8042 USD/gal (5.69 USD/GJ).
- Kerosene `DIST_KER`: Ecuador's own value is now used. Diesel 1 is labelled kerosene in the national energy balance, and its 2024 industrial terminal price was 2.4619 USD/gal excluding VAT (18.32 USD/GJ).
- Crude `DIST_CRU`: EP Petroecuador export FOB 68.56 USD/bbl (11.86 USD/GJ). The BCE figure for all exporters is 68.45 USD/bbl, and Comtrade gives 458.40 USD/t. No price for crude transferred to the refineries is published.
- history_ECU.csv: 2018 to 2025 BCE annual series (40 rows) for crude export, fuel oil No. 6 export, and diesel, naphtha and LPG import costs.
- Still open: none as ASSUMPTION. The manual list has 4 items. They would refine, not open, rows: the Decreto 308 text, the base text of the price regulation, the OLADE manual for calorific basis, and the SENAE customs export for coal and coke.

## Judgement calls and reasons

1. **Terminal price averages.** EP Petroecuador terminal prices are averaged day-weighted over calendar 2024, using the 13 structures in force from 12 December 2023 to 11 January 2025. Each structure holds from the 12th to the 11th, so averaging by month would misplace 11 days in each month.
2. **VAT.** Structure prices include VAT: 12 percent to March 2024, 15 percent from April 2024, and 5 percent for residuo cementero from June. VAT was removed day by day at the rate printed in the file in force.
3. **Dispatch values.** EP Petroecuador's "despachos valorados" (Informe Estadistico p.53) are taken to include VAT. The electric-sector diesel and fuel oil unit values match the VAT-inclusive regulated prices: for example, diesel in January works out to 0.9023 USD/gal against 0.900704 including VAT. The natural gas generator price is derived from these values on that basis.
4. **Natural gas basis.** Natural gas prices per MMBTU are kept on their published basis, which is not stated. Following the coordinator rule, they are not converted to net.
5. **Industrial terminal prices as wholesale.** Industrial-segment terminal prices are recorded as `wholesale import parity`. They are EP Petroecuador's monthly unsubsidised sale prices, set by the price regulation, and are the closest published local price to import parity. The automotive, electric and household prices are administered (subsidised) and are recorded separately under their own price points.
6. **Margins outside the April to June text.** The margins from Decreto 215 (Registro Oficial 529, in force 1 April 2024) are applied to the whole year. The automotive diesel terminal price excluding VAT barely moved all year (1.434063 to 1.434171), which suggests the same regime. The Decreto 308 text in force from 28 June is on the manual list.
7. **Coal conversion factor.** The IPCC anthracite NCV (26.7 GJ/t, sourced as ECU_IPCC_NCV_ANTHRACITE) is used because 99.6 percent of the tonnage is HS 270111. The other-bituminous alternative is given in the row notes.
8. **Petroleum coke quantity.** For petroleum coke the Comtrade `netWgt` field is used, as the brief requires. Comtrade's `qty` field is 28 percent higher; the alternative value is in the notes.
9. **Crude per barrel.** Crude per barrel is converted with the shared UN 7.32 bbl/t. Ecuador's crudes are heavier, so a per-tonne Comtrade row is also given.
10. **Kerosene.** Kerosene is taken as Diesel 1 because the BEN 2024 (p.37) labels it that way. No separate household kerosene price exists.

## Values that could not be sourced externally

- Refinery transfer price of crude: not published by EP Petroecuador, BCE or the financial statements.
- Import margins as published components: FOB, freight and insurance are not published separately for EP Petroecuador imports. The import value is DPU (freight included, insurance excluded). The terminal and wholesale margins inside the industrial terminal prices are not published either.
- Unit price of private fuel oil imports: BCE lists 61.7 million USD FOB under subpartida 2710192200 in 2024 but gives no quantity, and Comtrade 271019 mixes products.
- Inland freight: not published as a separate component; it sits inside the regulated margin.

## Differences above 10 percent from the earlier job (adders_2024.csv)

Differences are against `pre_tax_price_2024_usd_per_gj`, or `observed_import_cost_usd_per_gj` where noted.

| Fuel | Value in this job | Earlier job | Difference | Likely cause |
|---|---|---|---|---|
| COA | 8.91 USD/GJ | 5.211 USD/GJ | +71 percent | Ecuador imports anthracite in small lots at 238 USD/t CIF. The earlier value was South African steam coal plus an assumed adder. |
| NGS, generator | 2.88 USD/GJ | 7.763 USD/GJ | -63 percent | Domestic Amistad gas at an administered price, against the earlier imported-LNG build. |
| NGS, industrial piped | 3.57 USD/GJ | 7.763 USD/GJ | -54 percent | Same cause as the generator row. |
| NGS, LNG | 6.67 USD/GJ | 7.763 USD/GJ | -14 percent | Same cause as the generator row. |
| FOI, export FOB | 10.11 USD/GJ | 15.978 USD/GJ | -37 percent | Export parity, against the earlier import parity built from other countries. |
| FOI, industrial | 11.25 USD/GJ | 15.978 USD/GJ | -30 percent | Same cause as the export row. |
| FOI, regulated to generators | 2.50 to 4.27 USD/GJ | 15.978 USD/GJ | -73 to -84 percent | Subsidised administered prices. |
| CRU | 11.86 USD/GJ | 14.285 USD/GJ | -17 percent | Oriente and Napo trade at a discount to Brent (68.56 against about 80 USD/bbl). The earlier value was Brent plus an adder. |
| KER | 18.32 USD/GJ | 20.844 USD/GJ | -12 percent | Ecuador's own Diesel 1 price, against the earlier jet-based build. |
| JET, terminal | 18.77 USD/GJ | 25.989 USD/GJ | -28 percent | Jet imports were 7 small cargoes at high unit cost. Most supply was refined locally and priced off international reference. |
| LPG, industrial | 16.28 USD/GJ | 13.123 USD/GJ | +24 percent | The industrial LPG terminal price is set well above import cost (0.77 against 0.557 USD/kg). |
| LPG, household | 2.02 USD/GJ | 13.123 USD/GJ | -85 percent | Subsidised price. |
| LPG, taxis and drying | 6.31 USD/GJ | 13.123 USD/GJ | -52 percent | Subsidised price. |
| DSL, automotive | 11.05 USD/GJ | 19.676 USD/GJ | -44 percent | Subsidised price. |
| DSL, generator | 5.69 USD/GJ | 19.676 USD/GJ | -71 percent | Subsidised price. |
| DSL, Diesel 2 industrial terminal | 17.41 USD/GJ | 19.676 USD/GJ | -12 percent | The Diesel 2 industrial terminal price sat below its 2024 import DPU value. |
| GSL, Extra automotive | 17.94 USD/GJ | 22.351 USD/GJ | -20 percent | Subsidised until 27 June 2024, then a price band. |

The import DPU values for DSL, GSL, JET and LPG equal the earlier `observed_import_cost_usd_per_gj` (difference 0.0 percent). The Diesel Premium, Extra and Super industrial terminal prices are within 10 percent of the earlier pre-tax values.

## Known-limitation candidates

- prices_ECU.csv, NGS generator row: the electric gas price rose in November 2024 from about 2.91 to 3.63 USD/MMBTU excluding VAT, reaching the industrial price. The 2024 mean understates the late-2024 level.
- prices_ECU.csv, GSL Extra automotive row: the structure in force 12 June to 11 July 2024 shows the pre-28 June price, so 14 days carry the subsidised price.
- prices_ECU.csv, FOI generator rows: these are administered prices far below export parity. Using them as the model's supply cost would value fuel oil for power at a fraction of its opportunity cost.
- prices_ECU.csv, COK row: Comtrade's two quantity fields differ by 28 percent for HS 271311 (netWgt 245.6 kt, qty 315.1 kt).
- prices_ECU.csv, CRU rows: Comtrade crude export value is 9 percent below the BCE income figure for 2024.
- calorific_ECU.csv: the BEN 2024 states its factors in BEP without defining BEP in energy units or stating net or gross.

## Left unchecked

- The Decreto 308 text, and whether the 28 June 2024 regime changed the diesel margin or the electric fuel prices. This is on the manual list. The structures show no change in the excluding-VAT electric prices.
- Monthly ARCH notices of retail (surtidor) prices for 2024. No official file was located.
- Private-importer prices for diesel, gasoline and fuel oil. BCE gives FOB values without quantities.
- Avgas was not processed (no open AVG row for Ecuador). Its import DPU value is 265.29 USD/bbl (Informe Estadistico p.62).

## Incidents

- The Git Bash curl (mingw64) crashed with a segmentation fault on the BCE download. Windows curl.exe was used with the same options and no user agent.
- Several EP Petroecuador requests failed to connect (curl error 28) and succeeded on retry.
- After the coordinator's rule change, no user-agent override was used anywhere. Blocked pages (OLADE HTTP 403, gob.ec connection reset, SIMEM certificate login) were logged and listed, not worked around.
- Two OLADE responses were HTML error pages saved under a .pdf name. They were deleted and are not cited.
