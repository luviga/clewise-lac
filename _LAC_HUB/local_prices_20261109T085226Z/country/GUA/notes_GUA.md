# Guatemala (GUA) notes, job LAC_LOCAL_PRICES 20261109T085226Z

## Summary

Closed with a published Guatemalan source:

- Coal, DIST_COA (was ASSUMPTION candidate): import CIF 2024 from Banco de Guatemala customs statistics (SAC 2701.12, all from Colombia), 142.02 USD/t, 5.6536 USD/GJ with the PEG-5 tender value of 23.81 MMBtu/t net as received. UN Comtrade gives the same value (142.03 USD/t). No generator-delivered coal price is published.
- Petroleum coke, DIST_COK (was ASSUMPTION candidate): import CIF 2024 from Banguat (SAC 2713.11, United States and Mexico), 100.33 USD/t, 3.1954 USD/GJ with the PEG-5 value of 29.76 MMBtu/t net as received. Comtrade agrees. No delivered price to cement or industry is published.
- Kerosene, DIST_KER (was built from other countries' data): MEM consumer price in Guatemala City, 37.00 GTQ/gal in every month January to October 2024, 31.2593 USD/GJ pre-tax. The Banguat import line for kerosene (14.8 t in 2024) is recorded but is not a usable price.
- Diesel, gasoline, LPG and bunker: MEM weekly price structures extended from 31 to 35 of 52 weeks (four new files: 30 Sep, 7, 14, 21 Oct 2024). Each component (CIF, inland freight, other costs, terminal, port, importer margin, bottler margin, retail margin, IDP, IVA) is recorded as a mean of the 35 weeks. Banguat customs CIF per tonne is recorded as a second import value for fuel oil, diesel, gasoline and LPG. Bunker consumer price (MEM, January to October) added.
- Exchange rate GUA_FX_2024 = 7.75960 GTQ/USD, mean of 366 Banguat daily reference rates (re-confirms the earlier 7.7596). Means for 2018 to 2023 and 2025 also computed for the history file.

Still open:

- Natural gas, DIST_NGS: Guatemala imported no natural gas in 2024 (Banguat and Comtrade have no 2711.11 or 2711.21 record) and no local delivered price exists. The row stays an ASSUMPTION candidate at 7.763 USD/GJ (gross), checked against the PEG-5 price formula (Henry Hub plus a bidder adder for liquefaction and transport).
- 17 of 52 weekly MEM structures (26 Feb to 18 Mar, 29 Apr, 29 Jul to 9 Sep, 4 Nov, 18 Nov to 9 Dec, 30 Dec) were not found by file name; the MEM index pages are behind a Cloudflare challenge (HTTP 403). Kerosene and bunker consumer prices for November and December 2024 also missing.
- No generator-delivered price for coal, bunker or diesel: AMM publishes variable costs in US$/MWh only; declared fuel costs sit behind the AMM participant login.

Counts: prices_GUA.csv 29 rows (19 local regulator or operator, 7 local customs or statistics, 2 international customs (Comtrade), 1 ASSUMPTION candidate), history_GUA.csv 62 rows, sources_GUA.csv 62 documents, constants_GUA.csv 15 constants, search_log_GUA.csv 178 rows, manual_GUA.csv 5 items.

## Judgement calls and reasons

- Coal and petcoke calorific values: customs publish none, so the PEG-5 tender bases (a Guatemalan document approved by CNEE) were used: Colombia 6000 kcal/kg NAR (23.81 MMBtu/t) and USGC petcoke 7500 kcal/kg NAR (29.76 MMBtu/t). These are net as received. The IPCC alternative is given in each row's notes (coal 5.5048, petcoke 3.0864 USD/GJ).
- Coal line: the main row uses SAC 2701.12 (bituminous, 88 percent of coal tonnage, all Colombian). SAC 2701.19 (other coal, from the United States, 133.06 USD/t) is mentioned in the notes; all 2701 lines together give 141.66 USD/t.
- Weekly structures are averaged with equal weight per published week; the annual mean exchange rate is applied to the mean. Months covered: 1 to 7 and 9 to 12 (no August structure).
- Gasoline: regular and superior are recorded as separate rows with the same model code; the build job chooses the mix (MEM 2024 import volumes: regular 10.45 million bbl, superior 8.37 million bbl).
- LPG: the residential 25 lb cylinder and the automotive per-gallon structures are both recorded. The cylinder price includes a large bottler margin (31.39 GTQ per cylinder), recorded in wholesale_margin; its wholesale row stops before bottling.
- Bunker: the MEM bunker structure ends at the ex-rack price at the Puerto San Jose terminal, which is where power plants and industry buy; it is recorded as wholesale import parity. importer_terminal_margin holds the terminal charges (0.2400 GTQ/gal) plus the gross importer margin (4.6077 GTQ/gal); both are listed separately in the notes. Port charges (0.1436) are in the port column.
- OTROS GASTOS (other costs, 0.25 GTQ/gal for diesel and gasoline, about 4.26 GTQ per LPG cylinder) has no column; it is included in the wholesale sum and listed in the notes.
- Pre-tax consumer prices remove IDP and IVA as published in each structure. IVA is 12 percent of the price net of IDP (checked on the 3 Jan 2024 superior slide).
- Kerosene IDP: the only published rate found is Q0.50 per gallon in Decreto 74-98 (1998). Later reforms changed the gasoline and fuel oil rates; no later kerosene rate was found. The effect on the pre-tax value is 1.4 percent.
- Banguat values are taken as CIF because Banguat's Cuadro 4 on the same imports is titled VALOR (CIF) and its January 2024 coal footnote equals the KF-103 coal line.
- MEM DGH monthly import cost and volume tables were read but not used for rows: they do not state CIF or FOB, the June 2024 bunker unit value (204 USD/bbl) is an outlier, and the petcoke series is inconsistent with customs.
- The duplicate upload Estructuras-de-Precios-referenciales-al-22-julio-2024-1.pdf (identical to the file without -1) was set aside.
- History: Banguat CIF unit values 2018 to 2025 for coal, petcoke, fuel oil, diesel, gasoline and propane (one publisher, same lines every year), and MEM Guatemala City consumer prices for kerosene and bunker 2018 to 2024 converted at each year's Banguat mean rate. For bunker in 2018 to 2023 the IDP was taken as zero (the 2024 structure value); earlier rates were not checked.

## Values that could not be sourced externally

- DIST_NGS 2024 delivered gas price: no import and no published local price; ASSUMPTION candidate kept at 7.763 USD/GJ (the hub's Henry Hub plus LNG spread build, whose components this sub-task did not re-source).
- Generator-delivered coal, bunker and diesel prices: not published (AMM participant login).
- Delivered petcoke price to cement and industry: not published.
- Freight and insurance separately from FOB for liquids: MEM publishes CIF only.

## Differences above 10 percent from adders_2024.csv

- COK: 3.1954 against 3.606 USD/GJ (minus 11.4 percent). The earlier value was a US petcoke delivered price plus an assumed 0.8 adder; the new one is the Guatemalan customs CIF with a net calorific value of 31.40 GJ/t.
- GSL superior final consumer pre-tax: 25.1613 against 21.938 (plus 14.7 percent). The earlier pre-tax value was import cost plus a margin, not the station price net of taxes; regular is plus 8.8 percent.
- LPG: cylinder final consumer pre-tax 24.1883 and automotive 20.3062 against 12.874 (plus 88 and 58 percent). The earlier value was import parity plus a 0.78 margin; the consumer prices include bottling, distribution and retail margins. The cylinder wholesale value (13.7735) is within 7 percent. Banguat propane CIF 14.0198 is 15.9 percent above the earlier observed 12.098 (MEM CIF is 1 percent below).
- KER: 31.2593 against 20.844 (plus 50 percent). The new value is a small-volume retail price in Guatemala City that MEM shows fixed at 37.00 GTQ/gal; the earlier value was built from the US Gulf jet price and other countries' margins. The Banguat kerosene line (51.23 USD/GJ) covers 14.8 t only.
- Other rows are within 10 percent: coal plus 8.5, diesel CIF minus 1.4, bunker CIF plus 0.8, bunker ex-rack minus 0.4.

## Known-limitation candidates

- AMM weekly dispatch workbooks (sheet CVG): plant variable costs in US$/MWh and efficiencies in kWh/t could give an implied coal cost per tonne if O&M were known; not a fuel price.
- PEG-5 bases numeral 5.3.3: local internment and transport for coal (23.33 US$/MWh) and petcoke (18.76 US$/MWh) per MWh of output, a possible delivered adder once a heat rate is chosen.
- MEM Revista Hidrocarburos 2024-03T: national crude price (feeds the EXTT_CRU export row, not in this sub-task).
- AMM workbooks and EOR planning report list a small natural gas plant (Actun Can, 2.6 MW) burning domestic associated gas in Peten; no gas price is published.
- MEM ex-rack weekly terminal prices for gasoline, diesel and bunker (not downloaded; the bunker structure already ends at ex-rack).

## Left unchecked

- MEM weekly statistical reports (Informe Estadistico Semanal) with daily US Gulf FOB prices: an international benchmark, not a local price.
- MEM ex-rack weekly price files for 2024.
- AMM weekly dispatch workbooks for 2024 (the 2026 file shows they carry no fuel prices).
- IDP rate on bunker for 2018 to 2023.

## Incidents

- An early parallel probe of mem.gob.gt file names drew HTTP 429 (rate limit). It was stopped and all later probing ran one request per second with a 30 second back-off on 429. A second probe run returned HTTP 000 for every URL because the candidate list had Windows line endings; it was rerun with the line endings removed.
- Mid-task rule change: no user-agent spoofing. All downloads in this sub-task used curl's default agent; MEM index pages that return 403 to it were put on the manual list.
- The AMM 2024 statistical report (80 MB) and the CNEE PEG 2024-2054 plan (32 MB) were opened, found to carry no fuel prices, and deleted from downloads; they are logged in the search log.
