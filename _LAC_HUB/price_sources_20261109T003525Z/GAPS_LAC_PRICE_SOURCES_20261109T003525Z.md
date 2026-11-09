# GAPS LAC_PRICE_SOURCES 20261109T003525Z

## 1. Judgement calls and reasons

1. Oil product benchmarks are the EIA US Gulf Coast spot series (gasoline, ULSD, jet) and Mont Belvieu propane. This uses one free publisher for all oil products, and the US Gulf is the main supply point for the region. Some countries buy higher-sulfur diesel or regular gasoline grades that trade below these series.
2. Kerosene uses the USGC jet series on the kerosene net calorific value (43.8 GJ/t). No free USGC household kerosene series exists.
3. Fuel oil benchmark: Brent x 0.814. The ratio comes from the ARESEP 2024 "Precio FOB estimado" for bunker over 2024 Brent. It is one year from one regulator, but it agrees with the Platts No. 6 FOB quote in the Dominican MEM bulletins. The EIA US residual resale series (ratio 0.946, 2018-2021) was rejected as the main proxy because it is a domestic refiner resale price, mixes sulfur grades and ended in March 2022. It is kept as an upper alternative.
4. Aviation gasoline benchmark: USGC gasoline x 1.579 (EIA PADD 3 avgas resale, 2018-2021, full years only; 2022 has 3 months and was excluded). The Costa Rica COA is 7.29 USD/GJ above this proxy, which suggests the proxy is low for small Caribbean cargoes.
5. Coal benchmark: World Bank South African (fob Richards Bay, NAR 6000 kcal/kg). It is an Atlantic-basin coal on a stated net basis. The Colombian series is not in the current Pink Sheet monthly file. Australian Newcastle is the alternative.
6. Petroleum coke proxy: EIA average cost delivered to US power plants (Electric Power Monthly Table 4.1). It is a US delivered price, not a cargo price.
7. LPG density: the UN generic LPG factor (489 gal/t) is applied to Mont Belvieu propane. Pure propane is lighter per gallon (about 520 gal/t), so the propane benchmark in USD/GJ would be about 6 percent higher with a propane-specific density.
8. Natural gas values (Henry Hub, EIA LNG export prices, DR importer price, OUR plant prices) are kept on the gross calorific basis in which they are published.
9. Exchange rates: the 2024 average selling rate where both are published (BCCR, BCRD, BOJ), because importers buy dollars. Banguat publishes one reference rate. The Costa Rica and Guatemala annual figures are means of daily official rates computed in this session; no published annual average table could be retrieved.
10. Margin scope: the importer or terminal and wholesale margin is included; retail margins, bottler margins and inland freight to stations are excluded.
11. Dominican Republic diesel uses the generator (EGP-C) gasoil row, the only market-tracking diesel parity in 2024. Gasoline and LPG parities were administrative under a retail price freeze, but they are kept as observed and flagged.
12. Honduras diesel, gasoline and kerosene import costs use the SEN annual report CIF unit values (109.83, 94.48 and 106.16 USD/bbl). The SEN monthly reports give lower volume-weighted values (96.24, 83.94, 92.00) with large monthly swings, and their monthly CIF sums do not add up to the annual report. The annual report was judged more reliable because its volumes match.
13. Honduras and Jamaica fuel oil, and Jamaica and Dominican Republic natural gas, use regulator-published delivered prices. These already include margins, so the margin is set to 0.
14. Built adders (Jamaica liquids; kerosene in Guatemala and Ecuador; Ecuador fuel oil) use the median of the observed import adder and the median of the observed margin, taken separately across the regulator price structures (Costa Rica, Dominican Republic, Guatemala). For kerosene and jet only two observations exist.
15. Ecuador fuel oil uses import parity built from regional data. The export-parity alternative is given in REPORT.
16. AEO2025 is used instead of AEO2026 because only AEO2025 has High and Low Oil Price cases.
17. Product-to-Brent ratios use the 2018-2025 mean.
18. Jamaica 2051 to 2055: hold 2050 real values (the least change).
19. Model 2025 values in "percent growth of incomplete years" mode are shown as the last stored value held; the A-O tool may compute a different 2025 value.

## 2. Sources not opened, blocked or paywalled

- Platts, Argus and S&P Global (USGC No. 6 / HSFO, avgas and petcoke spot, Colombian coal): paywalled, not retrievable. They are the only origin of free-of-proxy benchmarks for fuel oil, aviation gasoline and petroleum coke.
- Energy Institute Statistical Review download page: HTTP 403; UN Statistics Division conversion factors were used instead.
- IEA World Energy Outlook 2025: not opened (time). It would offer scenario prices but no High/Low oil price cases.
- Petrojam (petrojam.com): HTTP 403 to automated tools; Wayback copies blocked; pcj.com connection failed. Jamaica ex-refinery prices therefore not retrieved.
- Honduras: the system operator portal (appcnd.enee.hn:3200) refused connection; the official gazette (gaceta.iaip.gob.hn) did not respond; portalunico.iaip.gob.hn returned 403. SEN weekly bulletins 9, 14 and 22 are missing, bulletins 30 and 31 are image-only, and none were found after early August 2024.
- Dominican Republic: OC-SENI (oc.do) generator fuel costs not opened (time); the MICM open-data workbook 2010-2025 returned 403.
- Guatemala: AMM dynamic reports (wl12.amm.org.gt, reportesbi.amm.org.gt) and CNEE not searched.
- Costa Rica: BCCR's annual average exchange rate table (gee.bccr.fi.cr) no longer returns data.
- Ecuador: Ministry of Energy and ARCERNNR not searched in depth; no 2024 "precio de paridad" per gallon found.

## 3. Values without a retrievable source (ASSUMPTION candidates)

- Coal delivered adder, all six countries (1.0 USD/GJ, range 0.6-1.6).
- Petroleum coke delivered adder, all six countries (0.8 USD/GJ, range 0.5-1.2).
- Crude oil delivered adder, Dominican Republic and Ecuador (0.35 USD/GJ, range 0.17-0.52).
- Terminal and wholesale margins for Honduras diesel, gasoline and kerosene; Ecuador diesel, gasoline, jet and LPG; Jamaica LPG.
- A gross-to-net calorific factor for natural gas, if the models are on a net basis.
- A published heat content basis for the OUR Jamaica HFO price (USD/MMBtu, basis not stated).

## 4. Known-limitation candidates

- Adders are held constant in real terms across REF, HIGH and LOW, as the brief specifies. In reality freight and insurance rise with oil prices.
- The fuel oil and aviation gasoline proxies rest on one year (fuel oil) or on a discontinued series (avgas).
- LNG adders mix observed totals that include importer margins (Dominican Republic 9.33, Jamaica 7.77 USD/GJ) with a built value for countries without LNG imports (5.68 USD/GJ). The built value uses a 2017 small-scale cost range.
- AEO Henry Hub and coal hardly respond to the oil price cases, so HIGH and LOW do not move gas or coal costs.
- The AEO coal export price describes US coal, not Colombian or South African coal.
- 2024 regulator data have uneven coverage: Guatemala 31 of 52 weeks, Honduras weekly bulletins January to July only, Jamaica generator prices June and July only.
- Dominican Republic gasoline and LPG import parity in 2024 was administrative under a price freeze.
- Costa Rica bunker and LPG pre-tax prices were subsidised below cost plus margin; the adder uses cost plus margin.
- The South African coal values for January to May 2024 are World Bank estimates.

## 5. Left unchecked or with doubts

- Only one value per country was re-checked in the main session against the downloaded document. All other extracted values rely on the country sub-tasks' parsing (each sub-task reported internal checks: structures summing to published totals, cross-checks between two sources).
- Dominican Republic: 22 weeks were read from scanned resolutions and accepted only when an independent check matched; 17 product-weeks were left out. December 14-20 has no resolution. The MEM bulletin values for December repeat November.
- Guatemala: the MEM bunker CIF is below the MEM daily FOB table, so the two tables probably cover different grades. The MEM petcoke unit value is reported per barrel, and that unit is doubtful. Kerosene was imported in one month only. One ex-rack file has an uncertain period, and one weekly report could not be parsed.
- Honduras: the annual report's CIF column is labelled millions of USD but the values are thousands. Pre-tax values are before the 2024 fuel subsidy.
- Jamaica: the Comtrade gasoline CIF (17.14 USD/GJ) is below the USGC benchmark, so it was not used. The Comtrade coal value has no weight. The derived E10 87 pre-tax price assumes the 2022 SCT rate and was not used.
- Ecuador: the December 2024 figures are provisional and the December total value prints as "##########". The jet unit value covers 7 months.
- Costa Rica: the IFO 380 and propane-rich LPG costs are stale (no purchases in 2024). The July FOB table was read from an image. August LPG prices come from a section table.
- The A-O model values in "percent growth of incomplete years" mode were not run through the A-O tool.

## 6. Process deviations in this session

- Gate 2: the country sub-tasks wrote 7 scratch files (HTML pages and PNG renders) to Claude's session temp scratchpad, outside MODELS_LAC_5. One fetch tool cached a PDF in its own temp folder. No file outside `price_sources_20261109T003525Z/` inside MODELS_LAC_5 was written by this job. The only other new files in MODELS_LAC_5 belong to the parallel formula job (`_LAC_HUB/formula_check_20261109T003529Z/`).
- The Costa Rica sub-task reported stopping one bash process (pid 8332) that may have belonged to another parallel sub-task, after its download had finished. No missing download was found.
- The Guatemala sub-task opened and then deleted the AMM 2024 annual statistical report (no fuel prices). The Costa Rica sub-task opened and deleted Imprenta Nacional Alcances 104 to 107 (not relevant).
- An empty file from a failed EIA download (HTTP 404) was deleted.
