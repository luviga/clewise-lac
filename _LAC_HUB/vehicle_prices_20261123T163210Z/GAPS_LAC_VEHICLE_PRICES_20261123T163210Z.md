# GAPS LAC_VEHICLE_PRICES 20261123T163210Z

## Judgement calls

1. Pull request #16 (LAC_COST_SOURCES) was not merged into `main` at the start (the start check printed nothing). Its files were read from `origin/job/cost-sources` into a temporary folder, as the brief says. `scope_cells.csv` holds the 2,892 rows taken from them.
2. UN Comtrade quantities flagged as estimated by the UN (`isQtyEstimated`) are not counts of the government; they are derived from net weight. They never enter an average. This leaves Costa Rica, Guatemala and Honduras (all years), Jamaica 2022 and 2023 and the Dominican Republic 2023 without Comtrade counts.
3. The quantities the Dominican Republic reports to UN Comtrade for 2019 to 2022 are flagged as reported but are not vehicle counts: they add up to a few thousand a year (for example 373 cars above 3,000 cc worth US$ 249 million in 2019), against 120,189 vehicles counted by DGA for 2019. They are rejected through `parameters.csv` (`comtrade_units_rejected`).
4. The DGA vehicle bulletins give counts and FOB by vehicle type, not by tariff line. They are used as the Dominican Republic's own statistic for cars and taxis (Automoviles), SUVs and jeeps (Jeepetas) and buses and minibuses (Autobuses), for gasoline, diesel, LPG and natural gas vehicles, since the type has no fuel split (`national_type_map.csv`). Electric and hybrid vehicles have their own lines and are not priced from the type totals. "Vehiculos de carga" mixes light and heavy trucks and is not used; "Furgonetas y minivans", "Vehiculos de turismo" and "Otros" match no model class. No bulletin with annual figures exists for 2021 and 2022, so the Dominican average covers 2019, 2020 and 2023.
5. Rule 2 ("the same lines in the other four countries") is read literally: only tariff-line statistics enter it. The Dominican type counts do not, so rule 2 is in practice Jamaica's lines for every class.
6. Order of methods per technology: own tariff lines, then own customs counts by vehicle type, then rule 2, then rule 3. Rule 3 uses the class's diesel price found the same way.
7. LPG, natural gas and flex-fuel vehicles have spark-ignition engines and share the gasoline lines; HS has no fuel split. They take the statistic of those lines.
8. Fuel cell vehicles have only an electric motor for propulsion and fall in the electric lines, where battery electric vehicles make nearly all imports; they go to rule 3 (the brief's example). Heavy electric trucks also go to rule 3: the electric goods-vehicle line 8704.60 (HS 2022) has no weight split and holds mostly light vans.
9. Cars and SUVs are split by engine size, the only split HS gives: cars take spark-ignition lines up to 3,000 cc (870321 to 870323) and diesel lines up to 2,500 cc (870331, 870332); SUVs take spark-ignition lines above 1,500 cc (870323, 870324) and diesel lines above 1,500 cc (870332, 870333). The middle lines serve both.
10. The Honduran and Jamaican group "Pick Up and Jeep" (TRSUV) takes the SUV lines and the goods-vehicle lines up to 5 tonnes. Light trucks take goods vehicles up to 5 tonnes g.v.w.; heavy trucks take both bands above 5 tonnes.
11. Buses and minibuses share heading 8702: HS does not separate them by size, so both classes get the same statistic.
12. Hybrid and plug-in hybrid goods vehicles have their own lines only from HS 2022 (8704.41 to 8704.52); the HS 2017 line 8704.90 "Other" mixes them with other vehicles and is not used.
13. The base price is a 2019 to 2023 average in 2024 US$. It is entered where the model expects the 2024 price (base-year cell of trajectory rows; Costa Rica's 2024 cell), as the cost-sources proposals did.
14. Later-year multipliers of trajectory rows and the Costa Rica year ratios are those of the cost-sources proposals, unchanged (NREL ATB 2022 Mid path). Because the ATB is not a government statistic, these cells carry an ASSUMPTION sentence on the price path; gate 3 then checks only rows that rest on statistics alone. The Costa Rica ratio of each year is the cost-sources proposed price of that year divided by its 2024 price, which reproduces the ATB ratios exactly; motorcycles stay flat as before.
15. "Relative to" cells hold the ratio of the vehicle's statistic to the reference vehicle's statistic. Guatemala `TRAUTHG` and `TRAUTPHG` point at `TRAUTDSL` (column `unit_introduced_proposed`) for every year cell of the row. Dominican `TRYLFNGS` gets the ratio of the spark-ignition to the diesel light-truck statistic (both from Jamaica's lines).
16. `build_prices.py` reads, besides `downloads/` and `parameters.csv`, the two job maps (`vehicle_class_map.csv`, `national_type_map.csv`), which say which lines and types make each class. They hold definitions, not values.
17. The CPI, exchange-rate and ATB sources (GEN-001, WDI-001, GEN-101) are named in the derivations and listed in every sources file, but they are not put in `source_ids` of statistic rows; `source_ids` lists the statistics only (GEN-101 is listed on rows that use the ATB ratio or path, which are ASSUMPTION rows).
18. The 25 percent band is applied to every cell, multipliers included, as the cost-sources job did.
19. Manual files go to `downloads/manual/<CC>/` (one subfolder per country) so the reader knows the country and its currency.
20. The World Bank API call for the exchange rates timed out; the WDI bulk CSV of the same indicator was downloaded instead (WDI-001). No value used needed it: all statistics used are in US$.
21. The DGA report for 2024 also gives 2024 figures; they are outside the 2019 to 2023 window and are left out by `first_year` and `last_year`.
22. Costa Rica rail `TRNPASRAIELE` keeps its cost-sources row, as the brief says.
23. The units minimum of 10 is applied per line-year, so a small line drops in the years it falls short (for example Jamaica's electric buses, 870240, one vehicle in 2019).

## Known-limitation candidates

- Jamaica's lines carry mostly used vehicles from Japan; their CIF values are low for new vehicles (gasoline car 8,540 US$, electric car 14,221 US$). Rule 2 passes them to Costa Rica, Guatemala and Honduras until those countries' counts arrive. Where: `<CC>/class_prices_<CC>.csv`, method "other four countries".
- Motorcycles average 527 US$ per vehicle: Jamaica's 871120 line (50 to 250 cc, about 6,500 units a year at about 400 US$ CIF) dominates and probably holds scooters and kits. Where: every `TRMOT*GSL` and `TRNMOTGSL` row.
- Diesel hybrid buses (8702.20, 33 units in 2019 and 2020) average 15,358 US$, below diesel buses (34,139 US$); gasoline buses (8702.90) average 14,954 US$. The small lines hold vans and small vehicles. Where: `TRNBUSHYBDSL`, `TRNMICHYBDSL`, `TRBPRPHD`, `TRBPUPHD`, `TRMBSPHD`, `TRNBUSLPG`, `TRMBSGSL` and similar rows.
- Heavy diesel trucks (17,904 US$) average below light diesel trucks (18,953 US$) in Jamaica's imports, which are largely used trucks. Where: `TRYTKDSL`, `TRNFREHEADSL`.
- The Jamaican gasoline hybrid car (11,221 US$) is below the diesel car (22,091 US$), so Guatemala's `TRAUTHG` ratio to `TRAUTDSL` is 0.51. Diesel cars in Jamaica are mostly large vehicles.
- The bus price (34,139 US$ from Jamaica; 27,483 US$ FOB from DGA) reflects imports dominated by minibuses; a full-size bus cannot be separated in HS 8702.
- Dominican cars, SUVs and buses have one price for all fuels, so the "Relative to" cells of LPG and natural gas vehicles against diesel are 1.
- The DGA bulletins are marked preliminary.
- `CR_TICA_arancel_8702_8703_8704_8711.csv` was assembled from TICA query pages in a browser, not downloaded as one file.
- Costa Rica's PROCOMER open data, Guatemala's Banguat tables and the Dominican DGA transaction tables give CIF or FOB by national line with weight only; they are downloaded and listed in the sources files but enter no average.
- OperationalLife and distance per vehicle, which the cost-sources job flagged (one-year lives, 1 km placeholders), are untouched.

## Left unchecked

- The generic reader for manual tables was tested on a made-up table in a scratch copy only; real files from SAT, ONE, Hacienda, Honduran customs or STATIN may need a column name added.
- Whether SAT's vehicle import statistics are by tariff line or by vehicle type, and whether ONE's import database has a quantity field, could not be seen (Cloudflare).
- SIECA's SEC tool was reported by two country searches to offer value and weight only; it was not exported for Honduras because the hidden browser pane did not advance.
- The 2019 Costa Rica PROCOMER rows use some older 10-digit codes; not mapped, since the file is not used.
- Whether Jamaica's 2019 to 2021 Comtrade counts include CKD kits (lines for kits exist in the national tariff) was not checked.

## Incidents

- The first UN Comtrade probe asked for five years in one request and got HTTP 400 ("Maximum number of periods for preview is 1"); the logged download then ran one year per request. The probe requests (25, in a scratch folder) are not in the search logs.
- Three country searches ran at the same time as the Comtrade download, so the Comtrade rows sit between their rows in the search logs. One Dominican log row named DGA as the route for a ONE page; the label was corrected.
- While the Costa Rica search clicked through SIECA's SEC tool in the built-in browser, the page wrote to the clipboard. Nothing was pasted.
- The Dominican search downloaded, checked and deleted DGA magazines, yearbooks and monthly bulletins that held no vehicle counts by line.
- `pdfplumber` text extraction scrambled the 2020 DGA bulletin (characters placed one by one); the reader rebuilds lines from character positions instead.
