# REPORT LAC_LOCAL_PRICES 20261109T085226Z

Per-country published fuel prices for the six LAC energy models, 2024 first, history 2018 to 2025 where one publisher gives a consistent series. No model file changed and no final price series was built.

- Pull request: https://github.com/luviga/clewise-lac/pull/1 (draft, number 1)
- Branch: `job/local-prices`, from `c5ca4ee`
- Commits: `0a6a9b92d76493cec6eb73cd6f5420380d49bbb1` adds this folder; a second commit fills in this header only (the pull request number and the first hash could not be written inside the first commit, and amending it was not permitted in this run)
- Brief: `BRIEF_LAC_LOCAL_PRICES.md`; steer: `STEER_1.md` (applied from the moment it arrived; see GAPS for what was redone)

## Gate results

No gate failure is open. Sourcing check output: `gate_check_sourcing.txt`; text scan output: `scan_gate7.txt`.

| Gate | Result | Counts |
|---|---|---|
| 1. Read-only hashes | PASS | 18 of 18 hashes in `baseline_after.csv` equal `baseline_before.csv` (6 A-O workbooks, 6 BAU InputActivityRatio, 6 BAU OutputActivityRatio) |
| 2. Diff limited to the job folder | PASS | `git diff --name-only c5ca4ee HEAD`: 136 files, all under `_LAC_HUB/local_prices_20261109T085226Z/`; 0 outside |
| 3. Tracked file types; nothing under `downloads/` tracked | PASS | 136 tracked files: 64 `.csv`, 12 `.md`, 56 `.py`, 4 `.txt`; `git ls-files .../downloads` prints nothing |
| 4. Sourcing check (as replaced by STEER_1), script `scripts/check_sourcing.py` | PASS | Rows naming an existing source id: `local_prices_2024.csv` 172 of 172 non-ASSUMPTION rows; `local_history.csv` 330 of 330; `calorific_basis.csv` 9 of 9; `constants.csv` 90 of 90. Sources complete (http(s) URL, page or table, retrieval date, file present in `downloads/`, no local or internal reference): 352 of 352. Duplicate ids: 0. Price rows whose `downloaded_file` exists: 172 of 172 (2024), 330 of 330 (history) |
| 5. Every ASSUMPTION candidate has every lead logged | PASS | 4 ASSUMPTION rows (country, fuel), 4 pass, 0 fail |
| 6. Every number in REPORT traces to a CSV in the job folder | PASS | each table names its CSV; values are as printed in those files |
| 7. `git diff --check`; no em dash; no machine path outside URLs | PASS with documented exceptions | `git diff --check` clean (after converting Windows line endings to LF with `scripts/normalize_eol.py`). 0 em dashes. 8 path-like lines, all expected: 6 in `BRIEF_LAC_LOCAL_PRICES.md` (the brief, copied verbatim as Step 6 requires) and 2 regular-expression patterns that look for paths in the sub-task check scripts `country/DR/dr_check_sources.py` line 34 and `country/JAM/check_jam.py` line 31 |

Two earlier runs of the gate 4 script reported false failures, caused by its own path pattern (it matched `https:/`, then a SharePoint `/:b:/` link). The pattern was corrected and tested; see GAPS, incidents.

## Coverage, country by fuel, before and after

Source: `coverage_before.csv`, `coverage_after.csv`. Cell = status before > best evidence class found now for any 2024 price point of that row. Before: O observed; O+M observed import cost with assumed margin; Bx built from other countries; Br built from published rates; A ASSUMPTION candidate. After: R local regulator or operator; C local customs or statistics; T international customs (Comtrade); B built from published components; A ASSUMPTION candidate. n/m no model row.

| Fuel | Costa Rica | Dominican Rep. | Ecuador | Guatemala | Honduras | Jamaica |
|---|---|---|---|---|---|---|
| Coal | A > C | A > R (chart) and T | A > T | A > C | A > B (and T) | A > T |
| Petroleum coke | A > C | A > T | A > T | A > C | A > T | A > C (and T) |
| Natural gas | Br > A | O > R | Br > R | Br > A | Br > B | O > R (12 months) |
| Fuel oil | O > R | O > R | Bx > R | O > R | O > R | O > R (12 months) |
| Diesel | O > R | O > R | O+M > R | O > R | O+M > R | Bx > R (tax-inclusive) and B |
| Gasoline | O > R | O > R | O+M > R | O > R | O+M > R | Bx > R (tax-inclusive) and T |
| LPG | O > R | O > R | O+M > R | O > R | O > R | O+M > T |
| Kerosene | O > R | O > R | Bx > R | Bx > R | O+M > R | Bx > A |
| Jet fuel | O > R | O > R | O+M > R | n/m | n/m | Bx > A |
| Crude oil | n/m | A > T | A > R | n/m | n/m | n/m |
| Aviation gasoline | O > R | n/m | n/m | n/m | n/m | n/m |

Totals over the 55 rows (`coverage_after.csv`, `new_evidence_class`): local regulator or operator 37, local customs or statistics 5, international customs (Comtrade) 7, built from published components 2, ASSUMPTION candidate 4. Of the 33 rows open before, 29 now rest on a published source for that country. The 4 rows still ASSUMPTION candidates: natural gas in Costa Rica and Guatemala (no imports in 2024, no published price), kerosene and jet fuel in Jamaica.

A best class of R does not always mean a pre-tax wholesale price: Jamaica's diesel and gasoline R rows are Petrojam billing prices that include the special consumption tax, and Ecuador's and Costa Rica's generator rows are regulated or subsidised prices. Every price point is a separate row in `local_prices_2024.csv` (176 rows: 118 R, 18 C, 21 T, 15 B, 4 A).

## Values by country (2024)

Source for every value: `local_prices_2024.csv` (columns `price_as_published`, `derivation`, `source_id`, `page_or_table`). Constants: `constants.csv`. USD/GJ on the net calorific basis of the factor used (IPCC 2006 Table 1.2 or the source's own factor), except natural gas per MMBtu, kept on its published basis (gross where stated or by convention).

### Costa Rica

- Coal (`IMPCOA`, industry): PROCOMER customs open data, HS 270111 anthracite, 131,404.79 USD / 233,468 kg = 562.84 USD/t; / 26.7 GJ/t (IPCC anthracite) = 21.080 USD/GJ (CR-017, CR-018; Comtrade CR-022 identical). Only 233 t in 3 months: specialty lots, not steam coal. No HS 270112 imports in 2024.
- Petroleum coke (`IMPCOK`, industry): PROCOMER HS 271311, 10,063,119.59 USD / 98,974,100 kg = 101.67 USD/t; / 32.5 GJ/t = 3.128 USD/GJ (CR-016; Comtrade CR-022 identical).
- Natural gas (`IMPNGS`): no imports in 2024 (PROCOMER and Comtrade: no HS 271111; 3 kg under 271121). ASSUMPTION candidate 7.763 USD/GJ gross (sentence in the row).
- Fuel oil: RECOPE purchase invoices (ARESEP open data), 13 cargoes, CIF 49,754,201.88 USD / 102,005,269 L = 0.4878 USD/L; / (0.9882 kg/L x 40.4 GJ/t / 1000) = 12.218 USD/GJ (CR-013). Wholesale import parity (COA 254.30 + RECOPE margin K 63.58 CRC/L) = 317.88 CRC/L / 515.1098 CRC/USD = 15.458 USD/GJ. Generator delivered (Bunker Termico ICE 2, plantel price without tax 273.445 + freight 7.045 CRC/L) = 280.49 CRC/L = 13.929 USD/GJ (built from ARESEP CVG resolution RE-0164-IE-2023 and the monthly resolutions); the tax-inclusive ARESEP figure is 16.375 USD/GJ.
- Liquids components found: FOB, freight and insurance per cargo (AVG, DSL, FOI, GSL, JET, LPG); RECOPE margin K (importer and terminal); station freight and station margin (DSL, GSL, KER, AVG, JET). Diesel: CIF 17.593, wholesale parity 19.966, plantel pre-tax 20.489, station pre-tax 24.241, generator delivered 20.824 USD/GJ.

### Dominican Republic

- Coal (`DIST_COA`, power and industry): Comtrade (DR reporter) HS 270112 CIF 297,969,626.78 USD / 2,905,655,625 kg = 102.55 USD/t; / 25.8 GJ/t = 3.975 USD/GJ (DR-003). Generator delivered: OC-SENI Memoria 2024, Figure 45 (average cost declared by agents), 12 monthly values digitised from the chart, mean 5,865.17 DOP/t / 59.5665 = 98.46 USD/t = 3.816 USD/GJ (DR-007).
- Petroleum coke (`DIST_COK`): Comtrade HS 271311, 29,175,032.45 USD / 342,338,030 kg = 85.22 USD/t = 2.622 USD/GJ (DR-003).
- Natural gas (`DIST_NGS`): MICM weekly import parity (PPI), 50 weeks, mean 9.1435 USD/MMBtu / 1.055056 = 8.666 USD/GJ (DR-046 and others). Generator delivered, OC-SENI Figure 46, mean 513.93 DOP/MMBtu = 8.178 USD/GJ (chart). Comtrade LNG CIF 428.92 USD/t / 48.0 GJ/t = 8.936 USD/GJ net.
- Fuel oil: MICM Fuel Oil No. 6 EGP-C (generators), PPI 113.55 + distributor margin 1.35 + transport commission 5.68 = 120.58 DOP/gal; / 59.5665 / 0.145324 GJ/gal = 13.929 USD/GJ generator delivered. Import parity No. 6, 115.58 DOP/gal = 13.352 USD/GJ. The 1 percent sulphur grade: 15.527 delivered, 14.950 parity.
- Crude (`DIST_CRU`): Comtrade HS 2709 CIF 647.16 USD/t = 15.299 USD/GJ (DR-003).
- Liquids components found: distributor (wholesale) margin, transport commission (inland freight) and retailer margin for DSL, GSL, KER, JET, LPG, FOI. No FOB, freight or insurance split of the MICM parity is published.

### Ecuador

- Coal (`DIST_COA`, industry): Comtrade HS 2701 CIF 3,506,260.77 USD / 14,734,330 kg = 237.97 USD/t; 99.6 percent anthracite, / 26.7 GJ/t = 8.913 USD/GJ (ECU-017, ECU-018).
- Petroleum coke (`DIST_COK`): Comtrade HS 271311 CIF 30,287,760.08 USD / 245,618,130 kg = 123.31 USD/t = 3.794 USD/GJ (ECU-018, ECU-023).
- Natural gas (`DIST_NGS`, domestic Amistad gas): EP Petroecuador 2024 dispatch value 20,061,024.56 USD including VAT, VAT removed month by month = 17,547,799.73 USD / 5,773,789 MMBtu = 3.0392 USD/MMBtu = 2.881 USD/GJ to generators (ECU-001). Industrial terminal price 3.7705 USD/MMBtu excluding VAT = 3.574 USD/GJ; LNG from Bajo Alto 7.0423 USD/MMBtu = 6.675 USD/GJ.
- Fuel oil: see the open question below.
- Crude (`DIST_CRU`): EP Petroecuador export FOB 68.56 USD/bbl = 11.86 USD/GJ (ECU-001); BCE, all exporters, 68.45 USD/bbl.
- Liquids components found: published retail margins excluding VAT (diesel 0.128438 USD/gal, Extra 0.160313 USD/gal, LPG for taxis 0.13 USD/kg; Registro Oficial 529, ECU-016). Import unit values (freight included, insurance excluded) as in the earlier job. Terminal and wholesale margins are not published separately; industrial terminal prices are recorded as the wholesale point (diesel 2 industrial 17.405 USD/GJ). Kerosene (Diesel 1 in the national balance) 2.4619 USD/gal excluding VAT = 18.324 USD/GJ.

### Guatemala

- Coal (`DIST_COA`, power only): Banguat customs, line 2701120000, 207,199,655 USD / 1,458,913,000 kg = 142.02 USD/t; / (23.81 MMBtu/t net as received, PEG-5 tender bases, x 1.055056) = 25.1209 GJ/t = 5.654 USD/GJ (GUA-002 to GUA-004, GUA-006). Comtrade agrees within 0.01 percent.
- Petroleum coke (`DIST_COK`, industry and cement): Banguat 91,719,961 USD / 914,167,966 kg = 100.33 USD/t; / 31.3985 GJ/t (29.76 MMBtu/t, PEG-5) = 3.195 USD/GJ.
- Natural gas (`DIST_NGS`, power only): no imports in 2024. ASSUMPTION candidate 7.763 USD/GJ gross, checked against the PEG-5 contract gas formula (Henry Hub plus a bidder adder plus a supply guarantee factor).
- Fuel oil: MEM weekly structures (35 of 52 weeks) CIF 11.709 GTQ/gal / 7.7596 / 0.145324 = 10.384 USD/GJ; ex-rack Puerto San Jose before taxes 16.700 GTQ/gal (CIF + terminal 0.24 + port 0.1436 + importer margin 4.6077) = 14.810 USD/GJ. Banguat CIF 449.80 USD/t = 11.134 USD/GJ. No generator-delivered price is published (AMM gives US$/MWh only).
- Liquids components found: importer and terminal margin, inland freight, retail margin (DSL, GSL, LPG), bottler margin (LPG cylinder), port (FOI). Kerosene: MEM Guatemala City consumer price 37.00 GTQ/gal, pre-tax 31.259 USD/GJ.

### Honduras

- Coal (`DIST_COA`, power only): Comtrade HS 270112 CIF 3,685,000 USD / 27,500,000 kg = 134.00 USD/t = 5.194 USD/GJ (HON-019). Generator delivered, built: x (1 + 0.05 local cost share, ODS Plan Indicativo de Expansion 2026-2035, 5.3.4) = 140.70 USD/t = 5.453 USD/GJ (HON-016).
- Petroleum coke (`DIST_COK`, power and industry): Comtrade HS 271311 CIF 15,104,108.97 USD / 185,197,337.35 kg = 81.56 USD/t = 2.509 USD/GJ.
- Natural gas (`DIST_NGS`, power only): no imports in 2024. Built from the ODS published LNG chain: Henry Hub 2024 2.19 USD/MMBtu (EIA, HON-027) x 1.15 + 2.0 liquefaction + 0.3 shipping + 1.0 regasification = 5.8185 USD/MMBtu = 5.515 USD/GJ gross.
- Fuel oil: CREE real bunker price for generation, 12 monthly values, mean 73.5608 USD/bbl / 42 x 278 / 40.4 = 12.052 USD/GJ (HON-010 to HON-012). Import CIF BCH 76.36 USD/bbl (12.510 USD/GJ), SEN 76.46 (12.528).
- Liquids components found: one full SEN weekly structure (27 May to 2 June 2024, as printed by two newspapers) with import parity, wholesale margin, freight and retail margin for DSL, GSL, KER; LPG cylinder chain with every component (25 weeks); CCHAC pre-tax prices for DSL and GSL (28 weeks). BCH import CIF for every liquid.

### Jamaica

- Coal (`DIST_COA`, industry): Comtrade HS 2701 CIF 3,085,157.70 USD / 20,806,276.75 kg (weight estimated by Comtrade) = 148.28 USD/t = 5.747 USD/GJ (JAM-002). USA mirror export FOB 80.00 USD/t.
- Petroleum coke (`DIST_COK`, industry): Comtrade HS 2713 CIF 3,319,979.75 USD / 33,095,360.52 kg = 100.32 USD/t = 3.087 USD/GJ. MSET reports the cement company's petcoke at 23.724 USD per barrel, with no energy factor.
- Natural gas: OUR Annual Report 2024-2025, Table 24 (read from page image, re-checked in the main session): NG to JPS plants 13.54 USD/MMBtu, 12 months = 12.833 USD/GJ (basis not stated, taken as gross). IPP plants June and July: 8.66 and 10.48 USD/MMBtu. Comtrade LNG 668.31 USD/t = 13.923 USD/GJ net.
- Fuel oil: OUR Table 24, HFO to JPS 12.97 USD/MMBtu (81.87 USD/bbl), 12 months = 12.293 USD/GJ. MSET Bunker C imports (alumina companies) 80.949 USD/bbl = 13.262 USD/GJ.
- Liquids components found: none published. Diesel to JPS without the special consumption tax, built from OUR's ADO price and OUR's stated SCT rate: 19.948 USD/GJ. Petrojam billing prices (ADO, ULSD, E10-87, E10-90) include SCT.

## The two open questions

Source: `local_prices_2024.csv`; earlier values from `coverage_before.csv`.

Dominican Republic gasoline and LPG (2024, USD/GJ):

| Fuel | MICM administrative import parity | Market-tracking import cost | Earlier job (pre-tax, administrative parity plus distributor margin) |
|---|---|---|---|
| Gasoline | 19.490 (PPI 144.06 DOP/gal, 51 weeks) | 19.614 (built: US-reported export FOB to DR 98.02 USD/bbl x DR CIF/FOB ratio 1.0429 for HS 271012) | 21.660 |
| LPG | 15.253 (PPI 85.24 DOP/gal at MICM's 504.15 gal/t) | 11.042 (Comtrade DR, HS 271112 + 271113, 522.26 USD/t) | 16.719 |

Gasoline: the two sides agree within 1 percent on the annual mean, although the weekly PPI hardly moved while the market did. LPG: the administrative parity is 38 percent above customs CIF; the PPI is the residual of a frozen retail price (on 25 May 2024 margins rose by 3.50 DOP/gal and PPI plus tax fell by exactly 3.50).

Ecuador fuel oil (2024): EP Petroecuador imported no fuel oil.

| Price point | Value | USD/GJ |
|---|---|---|
| Export FOB, Fuel Oil No. 6 (EP Petroecuador, 6,253,273 bbl) | 61.68 USD/bbl | 10.106 |
| Generator delivered, Fuel Oil No. 4 from La Libertad (Decreto 215, RO 529) | 0.48 USD/gal excl. VAT | 3.303 |
| Generator delivered, Fuel Oil No. 4 other points | 0.62 USD/gal excl. VAT | 4.266 |
| Generator delivered, Fuel Oil No. 4, actual 2024 dispatch value | 20.19 USD/bbl excl. VAT | 3.308 |
| Generator delivered, Fuel Oil No. 6 electric (July to December) | 0.3634 USD/gal excl. VAT | 2.500 |
| Industrial terminal price, Fuel Oil No. 6 | 1.6355 USD/gal excl. VAT | 11.254 |
| Earlier job, built import parity | | 15.978 |

The generator prices are administered subsidised prices, far below export parity.

## Calorific basis by country

Source: `calorific_basis.csv` (9 sourced rows) and `calorific_not_retrieved.csv` (2 rows). Model fuel quantities: the tracked model workbooks cite the OLADE balance (Dominican Republic, "Balance Energetico de OLADE"; CNE BNEN 2018 annex) and the Balance Energetico Nacional 2021 (Ecuador); no tracked file names a balance for Costa Rica, Guatemala, Honduras or Jamaica (`scripts/find_balance_hits.txt`).

| Country | Balance opened | Net or gross | Factors published |
|---|---|---|---|
| Costa Rica | none (MINAE BEN: Cloudflare 403; OLADE: 403) | not retrieved | none |
| Dominican Rep. | Balance Energetico Nacional (SIEN, OLADE method), DR-009 | not stated | natural gas 0.83 toe per thousand Nm3 (34.75 MJ/Nm3, a net-level value) |
| Ecuador | BEN 2024, ECU-021 | not stated (cites OLADE manual 2017) | NGS 5.9806 BEP per thousand m3; coal 5.0439 kBEP/kt; fuel oil 1.0304 kBEP/kbbl; no petcoke factor; BEP not defined in GJ |
| Guatemala | BE 2024 (GUA-013), BE 2010 factor table (GUA-012) | not stated | 2010: coal 5.0439, coke 4.8998 BEP/t, fuel oil 1.0685 BEP/bbl. PEG-5 tender bases (GUA-006): coal 23.81 and petcoke 29.76 MMBtu/t, net as received |
| Honduras | BEN 2024, HON-028 | not stated | implied petcoke 5.549 kBEP/kt, fuel oil 1.0463 kBEP/kbbl; no gas or coal. ODS plan (HON-016) converts to lower heating value |
| Jamaica | National Energy Balance 2024, JAM-021; Energy Statistics 2025, JAM-015 | not stated | none; implied coal 5.16 BOE/t |

No national balance states its basis in the documents retrieved. The UN Energy Statistics Yearbook 2023 (GEN-006, p. xxv) converts natural gas from gross to net by x 0.9 (`UN_NGS_NET_PER_GROSS`), and IRES (GEN-008, para. 4.34) recommends net values for balances. Basis of the prices collected: IPCC 2006 factors (GEN-002) are net; Henry Hub, the EIA heat content (GEN-005) and the OUR, MICM, OC-SENI and EP Petroecuador per-MMBtu gas prices are gross or not stated and were kept as published; Comtrade LNG per tonne converted with IPCC 48.0 GJ/t is net.

## Manual download list

Source: `manual_downloads.csv`: 43 entries (40 distinct URLs; the OLADE manual appears once per country that needed it), sorted by weight.

| Weight rank | Entries | What they would close |
|---|---|---|
| 1 | 11 | tabulated generator-delivered coal, gas, fuel oil and diesel prices: OC-SENI Memoria tables, weekly programmes and monthly economic transaction reports (DR); CND planning database and annual market report, ENEE statistical bulletin (Honduras); AMM participant fuel declarations (Guatemala); Honduras customs CIF for coal and petcoke; calorific basis for DR and Guatemala (CNE balance, OLADE) |
| 2 | 8 | national customs CIF for coal and petcoke (ONE and DGA in DR, SIECA for Honduras, STATIN in Jamaica, SENAE in Ecuador); Costa Rica national balance and OLADE manual (calorific basis) |
| 3 | 10 | SIE generation cost publications (DR); JPS annual report and fuel filings, full-resolution OUR annual report (Jamaica); Ecuador price regulation text; La Gaceta margins (Honduras); OLADE manuals (calorific basis, five entries) |
| 4 | 8 | MEM Guatemala index pages for the 17 missing weekly structures; Petrojam weekly price index; Registro Oficial 589 (Ecuador, July to December prices); MICM weekly notices page and 2010-2025 workbook; BCCR daily exchange rates |
| 5 | 3 | Petrojam annual reports; CCHAC bulletins 9, 14, 22 and 32 to 52; SEN Honduras weekly price structures |
| 6 | 3 | REFIDOMSA annual report (crude); Jamaica Consumer Affairs Commission price tool; CEPAL hydrocarbon statistics (cross-check) |

The ranks are those each sub-task assigned; calorific-basis items were ranked by the rows whose conversion they would confirm.

Luis saves these in `downloads/manual/` of this job folder for a follow-up job.

## Values not sourced externally

Listed in GAPS, section 3, with the rows they affect. In short: 4 ASSUMPTION candidate rows; calorific basis for Costa Rica and the net or gross statement for every national balance; Costa Rica BCCR daily rates (WDI annual average used instead); no published margins for Jamaica; generator-delivered coal and fuel oil prices in Guatemala and Honduras (coal delivered in Honduras is built); FOB, freight and insurance splits outside Costa Rica.
