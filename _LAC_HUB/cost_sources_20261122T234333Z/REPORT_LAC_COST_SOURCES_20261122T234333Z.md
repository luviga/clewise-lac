# REPORT LAC_COST_SOURCES 20261122T234333Z

Branch `job/cost-sources` from `b51f24b`. Draft pull request: (number added after the first push).

## 1. Phase 1 summary

### 1.1 Cost rows by model and class

Rows are one per model, sheet, technology and cost parameter (`cost_inventory.csv`). Energy models contribute only their `Vehicle Techs` sheet; EmissionsPenalty rows come from the compiled BAU files (no A-O sheet holds them). Classes apply to rows with a non-zero value; "zero" rows hold no cost in any year. "Pairs" are distinct technology and parameter pairs that Phase 2 sources: `vehicle` (Vehicle Techs rows of technologies in a 2030 fuel with two or more producers), `sector_choice` (sector rows of class choice) and `energy_copy` (sector rows of class choice whose technology is an energy-model technology: plants, fuel supply and vehicles copied into RD_AFOLU and HON_AFOLU; not sourced again).

| Model | Rows | Non-zero choice | Non-zero total_only | Non-zero inactive | Zero rows | Technologies in class choice | Vehicle pairs | Sector pairs | Energy-copy pairs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CR_ENERGY (vehicles) | 92 | 48 | 2 | 32 | 10 | 24 | 82 | 0 | 0 |
| CR_AFOLU | 435 | 35 | 26 | 0 | 374 | 19 | 0 | 35 | 0 |
| CR_IPPU | 107 | 0 | 0 | 0 | 107 | 0 | 0 | 0 | 0 |
| CR_WASTE | 154 | 2 | 20 | 11 | 121 | 1 | 0 | 2 | 0 |
| RD_ENERGY (vehicles) | 91 | 83 | 0 | 0 | 8 | 42 | 82 | 0 | 0 |
| RD_AFOLU | 734 | 189 | 99 | 24 | 422 | 93 | 0 | 41 | 148 |
| RD_IPPU | 77 | 0 | 0 | 0 | 77 | 0 | 0 | 0 | 0 |
| RD_WASTE | 131 | 5 | 6 | 20 | 100 | 3 | 0 | 5 | 0 |
| ECU_Energy (vehicles) | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| ECU_AGR | 371 | 117 | 121 | 9 | 124 | 39 | 0 | 117 | 0 |
| ECU_USCUSS | 602 | 0 | 544 | 0 | 58 | 0 | 0 | 0 | 0 |
| ECU_IPPU | 102 | 0 | 2 | 0 | 100 | 0 | 0 | 0 | 0 |
| ECU_WASTE | 89 | 2 | 17 | 4 | 66 | 1 | 0 | 2 | 0 |
| GUA_ENERGY (vehicles) | 85 | 46 | 5 | 28 | 6 | 24 | 76 | 0 | 0 |
| GUA_AFOLU | 53 | 0 | 37 | 1 | 15 | 0 | 0 | 0 | 0 |
| GUA_IPPU | 82 | 0 | 0 | 0 | 82 | 0 | 0 | 0 | 0 |
| GUA_WASTE | 113 | 8 | 10 | 10 | 85 | 6 | 0 | 8 | 0 |
| HON_ENERGY (vehicles) | 61 | 50 | 1 | 10 | 0 | 25 | 60 | 0 | 0 |
| HON_AFOLU | 549 | 127 | 53 | 13 | 356 | 65 | 0 | 17 | 110 |
| HON_IPPU | 67 | 0 | 2 | 0 | 65 | 0 | 0 | 0 | 0 |
| HON_WASTE | 108 | 8 | 10 | 12 | 78 | 6 | 0 | 8 | 0 |
| JAM_ENERGY (vehicles) | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| JAM_AFOLU | 233 | 53 | 12 | 0 | 168 | 27 | 0 | 53 | 0 |
| JAM_TRANSPORT | 169 | 34 | 6 | 18 | 111 | 17 | 52 | 0 | 0 |
| JAM_WASTE | 112 | 13 | 11 | 12 | 76 | 9 | 0 | 13 | 0 |
| Total | 4,621 | 820 | 984 | 204 | 2,613 | 401 | 352 | 301 | 258 |

The section 3 recount of non-zero BAU rows per technology and year is replaced by this table, which counts A-O rows (one per technology and parameter), not technology-years. The vehicle counts of section 3 are confirmed: Costa Rica 46 vehicle technologies with 41 non-zero CapitalCost rows, Dominican Republic 45 and 41, Guatemala 41 and 38, Honduras 30 and 30, JAM_TRANSPORT 35 and 26; Ecuador and Jamaica energy hold one vehicle technology each with no CapitalCost.

### 1.2 Choice sets

`choice_sets.csv` lists every 2030 output fuel with two or more producers (277 in all models) and marks a choice where at least two producers are free (215). By model, choice sets of multi-producer fuels: CR_ENERGY 17 of 18, CR_AFOLU 13 of 14, CR_IPPU 0 of 1, CR_WASTE 3 of 14, RD_ENERGY 19 of 21, RD_AFOLU 33 of 44, RD_IPPU 1 of 1, RD_WASTE 4 of 8, ECU_Energy 9 of 10, ECU_AGR 20 of 25, ECU_IPPU 0 of 1, ECU_WASTE 2 of 5, GUA_ENERGY 9 of 12, GUA_IPPU 0 of 1, GUA_WASTE 3 of 5, HON_ENERGY 14 of 14, HON_AFOLU 23 of 27, HON_IPPU 0 of 1, HON_WASTE 3 of 5, JAM_ENERGY 9 of 11, JAM_AFOLU 15 of 18, JAM_TRANSPORT 12 of 13, JAM_WASTE 6 of 8. ECU_USCUSS and GUA_AFOLU have no output fuel with two producers.

Hub 12 vehicle count repeated: fuels with two or more vehicle or vehicle-group producers in 2030 are Costa Rica 13 (10 vehicle fuels plus 3 group fuels), Dominican Republic 12 (9 plus 3), Guatemala 10 (7 plus 3), Honduras 11 (9 plus 2), the same as hub 12. With the free-producer rule, Costa Rica has a choice in 9 of its 10 vehicle fuels (in `E5TRNBUS` only the diesel bus is free; the electric, hybrid, hydrogen and LPG buses are capped at zero in 2030), Guatemala 6 of 7 (in `E5TRYTK` only the diesel heavy truck is free), Dominican Republic 9 of 9, Honduras 9 of 9, JAM_TRANSPORT 10 of 11 vehicle fuels.

In BAU many electric and hybrid vehicles are not free: their 2030 capacity is capped at zero (for example Costa Rica `TRNBUSELE`, `TRNMICELE`, all Costa Rica hybrid diesel vehicles; Guatemala `TRYTKELE`), or capped at the level of their own activity lower limit (column `free_but_capacity_equals_activity_lower_limit`, for example Honduras `TRAUTELE`, `TRBPUELE`). Phase 2 sources every vehicle of a multi-producer vehicle fuel whatever its BAU class, because the optimised scenarios lift these caps (GAPS, judgement 3).

### 1.3 Vehicle cost chain

Described in `vehicle_cost_chain.md`. In short: `CapitalCost (M US$ per Gvkm) = 1000 x price (US$ per vehicle) / distance (km per vehicle per year)`, with the distance of the vehicle's group from `A-O_Demand.xlsx` (`Ref.km.BY`) changed yearly by `A-Xtra_Projections.xlsx`. "Relative to" rows multiply the reference vehicle's base-year cell; trajectory rows multiply the base-year price by the year's cell. The battery replacement workbook is read and never used. All compiled 2024, 2030 and 2050 CapitalCost values with a non-zero price were recomputed exactly (186 rows per year). Findings: Guatemala `TRAUTHG` and `TRAUTPHG` chain a ratio onto a ratio and compile to 0.0694 M US$ per Gvkm (1.33 US$ per vehicle); Costa Rica's values labelled "US$ / vehicle" behave like M US$ per Gvkm and are divided by distance a second time (section 2.1); the Dominican Republic's `TRYLFNGS` ratio cell holds a price and compiles to 33.9 million M US$ per Gvkm; OperationalLife is 1 year for Dominican Republic automobiles, motorcycles and taxis and for Costa Rica minibuses.

### 1.4 EmissionsPenalty

`penalty.csv` lists every emission with a non-zero penalty in each model's compiled BAU, its years, values, unit where the input states one, its emitters and whether an emitter is a free producer in a 2030 choice set. The eleven sector models of section 3 all hold non-zero penalties (recount confirms the list); three energy models also hold them (RD_ENERGY and HON_ENERGY `Health`, GUA_ENERGY `Accidents`, `Congestion`, `Health`), which are outside this job's scope.

- RD_AFOLU. Twelve penalised emissions, 2018 to 2050. Seven come from `A-Xtra_Emissions.xlsx` (Externalities): `Health` at 1000 M US$ per PJ, emitted by 19 power plants copied from the energy model, of which `PPCCTNGS`, `PPCCTNGSDSL` and `PPCOA` are free in the electricity choice set, so the penalty can change that choice; and six land co-benefit emissions (`CONHAB`, `CONHICK`, `CONTUR`, `CONVAR`, `DAPANI`, `RESHID`) at -1000 M US$ per PJ, each emitted by one technology outside any choice set. Five waste externalities come from `B1_Scenario_Config.xlsx`: `RM` -56, `FERT_ORG` -58.44, `contam_agua` 27.80, `salud_residuos` 67.51, `turismo_residuos` 101.26 (2030; no unit stated); the last three are emitted by `NO_CONTR_OD`, `SIT_CLAN` and `OPEN_BURN`, which are free producers in waste choice sets, so these penalties can change the waste route.
- ECU_AGR. `EXT_REGAIR` at 1.0 M USD per Mha, 2021 to 2050, emitted by one technology that is not in a choice set; it changes total cost only.
- ECU_USCUSS. `EXT_REGAIR` at -3.38 M USD per Mha, 2021 to 2050, one emitter, no choice set in the model; total cost only.
- ECU_WASTE. `FERT_ORG` -58.44, `contam_agua` 32.63, `salud_residuos` 79.24, `turismo_residuos` 118.86 (2030), from `B1_Scenario_Config.xlsx`. Emitters are not free in any choice set (the disposal set `NO_OSS` has only one free producer), so no penalty changes a choice in BAU.
- GUA_AFOLU. Ten penalties from the ModeloSuelo workbook: nine "income" emissions (`AG1a_income` -11.27 to `AG3_income` 371.62 in 2030), `dano_lena` 3,801.90 and `servicios_ecosistemicos` -4,037.43, each emitted by one land technology. The model has no output fuel with two producers, so none is in a choice set; the land technologies compete through activity limits and these penalties instead (GAPS, known-limitation candidates).
- GUA_WASTE. `FERT_ORG` -58.44, `RM` -56, `contam_agua` 57.82, `salud_residuos` 140.43, `turismo_residuos` 210.65 (2030). `NO_CONTR_OD` (uncontrolled disposal) emits the last three and is free in the `NO_OSS` choice set, so these penalties can change the disposal route.
- HON_AFOLU. Ten penalties at 1000 from `A-Xtra_Emissions.xlsx`: `Health` (M US$ per PJ, 12 power plants copied from the energy model, none free in a 2030 choice set) and nine land measures (`AGCOF`, `CONAG`, `CONHICK`, `CONSOIL`, `CONVAR`, `REFOR`, `RESTORMAN`, `SAF`, `SSP`, M US$ per Mha), each emitted by one technology outside any choice set. Total cost only. The sign is positive here and negative in RD_AFOLU and JAM_AFOLU for the same kind of co-benefit.
- HON_WASTE. Same five waste externalities as Guatemala but about 1000 times smaller and with the opposite sign for `FERT_ORG` and `RM` (0.05844 and 0.056 against -58.44 and -56 elsewhere). `NO_CONTR_OD` is free in `NO_OSS`, so `contam_agua`, `salud_residuos` and `turismo_residuos` can change the disposal route.
- JAM_AFOLU. `CON`, `CONAG`, `CONSOIL`, `HAB` at -1000 M USD per Mha, 2021 to 2055, each emitted by one technology outside any choice set. Total cost only.
- JAM_TRANSPORT. `Health` at 1000 M US$ per PJ, 2021 to 2055, seven emitters, none free in a 2030 choice set. Total cost only.
- JAM_WASTE. Six waste externalities from `B1_Scenario_Config.xlsx` (`FERT_ORG` -58.44, `RM` -56, `water_reuse` -1,500, `contam_agua` 32.25, `salud_residuos` 78.32, `turismo_residuos` 117.48 in 2030). The last three are emitted by `NO_CONTR_OD`, `SIT_CLAN` and `OPEN_BURN`, free in waste choice sets, so they can change the route.

### 1.5 The shared 11,525 value

`TRAUTDSL` 11,525 US$ per vehicle (Dominican Republic, Honduras, JAM_TRANSPORT) and `TRAUTGSL` 10,504.4963 (Dominican Republic, Honduras) have no confirmed external origin. The Dominican Republic and Honduras vehicle sheets share one template whose electric and bus prices come from the Dominican national electric mobility plan (GEN-104: electric car 30,000, electric bus 360,000, electric cargo vehicle 120,000, electric motorcycle 3,000 US$, cars 7,500 km per year); the electric-car multiplier 0.6667 in 2030 brings 30,000 to the plan's average new conventional vehicle price of 20,001 US$. The plan does not contain 11,525 or 10,504. The ratio 11,525 / 10,504.4963 = 1.097 is close to the diesel-to-gasoline ratio (1.099) of the Costa Rica model's light-duty costs, which the Costa Rica model documentation (a lead only) attributes to the Costa Rica Ministry of Finance vehicle valuation database; the version behind the number could not be identified, and that database is an online query with nothing to download. Neither value appears in any Dominican document checked (World Bank CCDR transport annex, DGII fleet report, the plan). The value is therefore treated as unsourced and replaced by sourced prices in the country proposals.

### 1.6 Sourcing work

Phase 2 sources 352 vehicle pairs (Costa Rica 82, Dominican Republic 82, Guatemala 76, Honduras 60, JAM_TRANSPORT 52) and 301 sector pairs (CR_AFOLU 35, CR_WASTE 2, RD_AFOLU 41, RD_WASTE 5, ECU_AGR 117, ECU_WASTE 2, GUA_WASTE 8, HON_AFOLU 17, HON_WASTE 8, JAM_AFOLU 53, JAM_WASTE 13), plus the vehicle chain inputs (distance per vehicle and OperationalLife, `vehicle_chain_inputs.csv`). Many pairs share one source value (for example a crop's production cost and its import price), so the number of distinct values to find is smaller.

## 2. Phase 2 by country

Shared sources (`sources_GEN.csv`): GEN-001 US CPI-U (BLS); GEN-101 to GEN-103 NREL ATB 2022 Transportation (purchase prices and price trajectories, scenario Mid; levelized maintenance; lifetimes and annual mileage); GEN-104 Dominican Republic national electric mobility plan (INTRANT and IDB, 2020); GEN-201 to GEN-203 FAOSTAT trade, producer prices and production bulk files; GEN-204 and GEN-205 World Bank What a Waste 2.0; GEN-206 CEPAL 2016 waste management guide (Latin American costs per tonne); GEN-207 World Bank WSP 2016 costs of the water and sanitation SDG targets. Every country uses the ATB 2022 Mid family for vehicle price trajectories and maintenance where no national value exists. ATB has no bus (Class 8 is the heavy-duty proxy for the trajectory only), no LPG vehicle and no motorcycle; those rows use stated proxies, national data or an ASSUMPTION.

### 2.1 Costa Rica

Files: `CR/proposals_CR.csv`, `CR/sources_CR.csv` (CR-001 to CR-013), `CR/search_log_CR.csv`, `CR/manual_downloads_CR.csv`.

Counts by class (cells; distinct technology-parameter pairs):

| Model | Confirmed | Replace | Assumption | Manual |
| --- | --- | --- | --- | --- |
| CR_ENERGY vehicles and chain inputs | 268 | 2,078 | 106 | 0 |
| CR_AFOLU | 18 | 9 | 8 | 0 |
| CR_WASTE | 0 | 2 | 0 | 0 |
| Cells, total 2,489 | 286 | 2,089 | 114 | 0 |
| Pairs, total 169 | 54 | 88 | 27 | 0 |

What the vehicle capital cost cells are. The CapitalCost cells of `Vehicle Techs` are plain numbers (except the hybrid taxi rows, which repeat the previous year by formula from 2023, and the rail rows, a constant divided by 0.7315286784). Multiplied back by the group distance and divided by 1000, the 2030 cells give plausible prices: diesel bus 96,016 US$, electric bus 134,886, diesel minibus 19,745, diesel heavy truck 60,045, diesel light truck 15,503, gasoline sedan 8,596, gasoline taxi 10,106, gasoline motorcycle 1,166. The ratio between cell and price equals the group distance over 1000 (59.0 for buses, 12.1 for sedans), so the cells most likely already hold M US$ per Gvkm and the compiler divides them by the distance a second time: compiled capital costs are 12 to 59 times too low (gasoline sedan 58.8 M US$ per Gvkm in 2030 instead of about 2,375). The implied light-duty prices are low against new-car prices, which fits depreciated fiscal values and a fleet that imports many used vehicles.

Proposals. Prices per vehicle in real 2024 USD: diesel bus 154,535 (ARESEP ceiling price CRC 74,087,835, USD 127,500 in 2020, CR-001), electric bus 484,816 base (BYD K9G, USD 400,000 in 2020, CR-001), hybrid and fuel cell buses as the national diesel price times the ATB Class 8 powertrain ratio, other classes from the ATB reference prices (United States prices before Costa Rica taxes), electric motorcycle 3,636 (GEN-104), gasoline motorcycle 2,000 (ASSUMPTION, range 1,200 to 3,500). Each year cell is the base price times the ATB ratio of that year. FixedCost from ATB maintenance (motorcycles ASSUMPTION: 25 M US$ per Gvkm gasoline, 15 electric). OperationalLife: minibuses 1 to 15 years (ATB Class 4 van life, equal to the 15-year legal life of Costa Rica public transport buses, CR-002), combustion taxis 9 to 15, gasoline motorcycles 7 to 10; heavy freight held at 20 years as an ASSUMPTION (inspected vehicles average 16 years, CR-003). Distance: bus 49,500 km (CR-001) and minibus 35,942 km (ATB) checked; the others are ASSUMPTIONs at their current values. Crops: SEPSA and MAG cost-of-production models 2025 (CR-004 to CR-013); imports: FAOSTAT unit values; collection: CEPAL 2016.

Ten largest changes, 2030 CapitalCost (cell in the A-O unit as entered; compiled M US$ per Gvkm now and with the proposal):

| Tech | Current cell | Proposed US$ per vehicle | Compiled now | Compiled with proposal |
| --- | --- | --- | --- | --- |
| TRNBUSELE | 2,286.2 | 387,557 | 38.8 | 6,568.9 |
| TRNFREHEAELE | 4,362.0 | 317,554 | 161.7 | 11,770.4 |
| TRNFREHEAHYD | 7,791.9 | 294,526 | 288.8 | 10,916.8 |
| TRNBUSHYD | 5,761.3 | 233,605 | 97.7 | 3,959.5 |
| TRNFREHEAHYBDSL | 3,288.0 | 209,683 | 121.9 | 7,772.1 |
| TRNFREHEADSL | 2,225.6 | 196,350 | 82.5 | 7,277.9 |
| TRNFREHEANGV | 3,116.0 | 196,350 | 115.5 | 7,277.9 |
| TRNFREHEALPG | 3,116.0 | 196,350 | 115.5 | 7,277.9 |
| TRNBUSHYBDSL | 1,930.6 | 166,311 | 32.7 | 2,818.9 |
| TRNBUSDSL | 1,627.4 | 155,737 | 27.6 | 2,639.6 |

Largest sector changes: pineapple fixed plus variable cost 6,919 to 18,849 US$ per ha per year (CR-007); orange establishment 2,924 to 6,339 US$ per ha and yearly cost 1,369 to 3,600 (CR-008); milk import 1,992 to 1,193 US$ per t and beef import 4,534 to 5,891 (FAOSTAT); waste collection 38.7 to 49.2 US$ per t (CEPAL 2016).

Decisions for Luis:
1. Unit of the vehicle capital cost cells. Option A (proposed): write prices per vehicle; compiled costs rise 12 to 170 times, are sourced and comparable with the other countries. Option B: relabel `Unit.Introduced` to "M US$ / Gvkm" and keep the cells; compiled costs rise 12 to 59 times with today's relative prices, but the values stay unsourced and partly reflect used vehicles.
2. Taxes. The ATB light-duty prices exclude Costa Rica import duty, selective consumption tax and VAT (above 50 percent for combustion cars, mostly exempted for electric vehicles). Adding them is a scenario-design choice.
3. Distances. Only bus and minibus distances are checked; replacing the others with the Dominican (7,500 km cars) or United States (19,108 km) references would change compiled costs 1.5 to 3 times.
4. Minibus OperationalLife 15 years instead of 1.

Judgement calls: the CEPAL bus prices are read as 2020 USD (the study's data year, converted at 581.02 CRC per USD); ATB prices are used for classes without a downloadable national price table; crop fixed plus variable cost is compared with the SEPSA total cost per hectare and replacements keep the model's split; crop capital cost is compared with the establishment year for coffee, oil palm and orange, and is an ASSUMPTION for annual crops; other vegetables are confirmed against the onion model (18,523 US$ per ha); banana rows are ASSUMPTIONs (the national model covers smallholder criollo banana only); pineapple imports are an ASSUMPTION (FAOSTAT volumes about 8 t per year).

### 2.2 Dominican Republic

Files: `DR/proposals_DR.csv`, `DR/sources_DR.csv` (DR-001 DGII fleet report 2023, DR-002 World Bank exchange rate, DR-003 and DR-004 Ministry of Agriculture production costs 2021 and 2019), `DR/search_log_DR.csv`, `DR/manual_downloads_DR.csv`.

Counts by class:

| Model | Confirmed | Replace | Assumption | Manual |
| --- | --- | --- | --- | --- |
| RD_ENERGY vehicles and chain inputs | 359 | 1,337 | 68 | 0 |
| RD_AFOLU | 3 | 276 | 306 | 0 |
| RD_WASTE | 0 | 5 | 0 | 0 |
| Cells, total 2,354 | 362 | 1,618 | 374 | 0 |
| Pairs, total 178 | 36 | 111 | 22 | 9 mixed (base cell confirmed, multipliers replaced) |

The 99 EmissionsPenalty cells (`contam_agua`, `salud_residuos`, `turismo_residuos`) are ASSUMPTIONs whose source is listed as a manual download (section 3).

Vehicle prices. Where the national plan (GEN-104) prices a class, that price anchors the class and ATB 2022 Mid powertrain ratios fill the other powertrains. Cars and taxis: gasoline and LPG 24,242 US$ (USD 20,001 in 2020), diesel 29,988 (ATB ratio 1.2370), electric 30,000 confirmed (sourced 36,361), hybrid ratio 1.02 confirmed (sourced 0.895). Buses: electric public bus 436,334 replaces 760,000, electric tourism bus 360,000 confirmed, diesel and gasoline 214,007 (ATB Class 8 diesel to electric ratio 0.4905). Heavy freight: electric 120,000 confirmed, diesel and gasoline 71,336. SUV, pickup and minibus use ATB United States prices. Motorcycles: electric 3,000 confirmed, gasoline 1,153.47 an ASSUMPTION (range 900 to 2,000). Multipliers follow ATB from 2024 and are 1.0 for 2019 to 2023. FixedCost uses ATB maintenance (motorcycles ASSUMPTIONs). OperationalLife: the 1-year rows become 15 years (cars, taxis) and 10 (motorcycles); buses and freight move from 14 to 17 years to 10 (plan), against DGII data showing 42 to 48 percent of the fleet built in 2000 or earlier. Public and tourism bus distance moves from 33,000 to 44,000 km (plan).

Ten largest changes (US$ per vehicle; compiled M US$ per Gvkm where stated):
1. TRYLFNGS: the ratio cell holds 17,466.62 (compiled 33,898,090); proposed ratio 1.0355 (51,609 US$, compiled 5,734).
2. TRBPUELE: 760,000 to 436,334 (compiled 23,030 to 9,917).
3. TRYTKHYD: 365,824 to 129,580.
4. TRBPULPG and TRBTURLPG: about +118,000, because their reference vehicle changes.
5. TRBPU and TRBTUR diesel and gasoline: 106,586 to 214,007.
6. TRYTKHD: 145,724 to 76,661.
7. TRYTKLPG: 138,109 to 71,336.
8. TRMBSELE: 38,632 to 103,126.
9. TRMBSDSL and TRMBSGSL: 27,594 to 73,662.
10. TRYLFDSL: 17,467 to 49,839.

Sector: IMPCARBOV 3,811 to 10,995 US$ per t; SEWERWW capital 1,194 to 6,164 and AERO_PTAR 900 to 4,646 M US$ per billion m3 per year; SEPT_SYST 210 to 2,802; IMPLEC 3,050 to 662 US$ per t; AG_COC FixedCost 3,297 to 1,242 US$ per ha; AG_CAF FixedCost 1,393 to 335.

Decisions for Luis:
1. Taxes: proposed prices exclude Dominican import taxes, which the plan puts at 40 percent of the landed cost.
2. Heavy freight anchor: diesel is anchored on the national electric truck price; the alternative, ATB Class 8 diesel at 194,835 US$, would leave electric trucks cheaper than diesel.
3. Minibus and pickup prices: ATB United States prices may overstate Dominican vehicles; replace them, or keep the current values until customs data (manual) arrive.
4. Bus distance 33,000 to 44,000 km lowers compiled bus capital cost by 25 percent.
5. Operational lives as above.
6. Wastewater capital costs scale linearly with the assumed 150 L per person per day (range 100 to 200).
7. Waste: collection rises to 66.5 US$ per t, disposal falls to 29.4, open dump to 12.5.
8. Crop costs: the sourced total cost per ha is split in the model's own proportion between fixed and variable cost.

Judgement calls: national anchor plus ATB ratios; ratio rows use the proposed price of the reference vehicle; where any multiplier of a row differs by more than 25 percent the whole ATB series is proposed (cells within 25 percent are marked replace with a note); one maintenance basis (ATB) for every powertrain; imports use FAOSTAT unit values; UN Comtrade was downloaded and rejected (the Dominican Republic does not report and mirror quantities are unusable).

### 2.3 Guatemala

Files: `GUA/proposals_GUA.csv`, `GUA/sources_GUA.csv` (GUA-001 and GUA-002, UN Comtrade Guatemala vehicle imports 2024 and 2018, partner-reported estimates), `GUA/search_log_GUA.csv`, `GUA/manual_downloads_GUA.csv`.

Counts by class:

| Block | Confirmed | Replace | Assumption | Manual |
| --- | --- | --- | --- | --- |
| GUA_ENERGY vehicle cells (556) | 145 | 407 | 4 | 0 |
| GUA_ENERGY chain inputs (45) | 28 | 16 | 1 | 0 |
| GUA_WASTE (104) | 0 | 5 | 99 | 0 |
| Cells, total 705 | 173 | 428 | 104 | 0 |
| Pairs: vehicles 76, chain inputs 45, waste 8 | 11, 28, 0 | 61, 16, 5 | 4, 1, 3 | 0 |

What was used. No Guatemalan document with vehicle prices, distances or lives was found: the SAT vehicle valuation tables and import statistics sit behind a bot check (manual), and the NDC 3.0, BTR1, national inventory report, the low-emission development strategy and the 2017 to 2032 energy plan hold none. Prices therefore follow the shared method: ATB 2022 Mid prices for light-duty classes; buses and heavy trucks anchored on the Dominican plan's electric bus (360,000 US$) and electric cargo vehicle (120,000 US$) with ATB Class 8 powertrain ratios; gasoline motorcycle confirmed against UN Comtrade (2,453 US$ CIF per unit, 2024); electric motorcycle 3,636 US$ (GEN-104). Multipliers are the ATB series (1.0 for 2019 to 2023). FixedCost from ATB maintenance (motorcycles ASSUMPTIONs). Distances are all confirmed against the shared references (cars 19,220 and light freight 20,600 km against ATB 19,108; buses 50,400 against the Dominican plan's 44,000; motorcycles 9,390 against 10,500), heavy freight 50,400 is an ASSUMPTION. OperationalLife: cars, light freight and microbuses 17 years confirmed (ATB 15), buses and heavy trucks 17 replaced by 10 (GEN-104), motorcycles 10 confirmed. Waste: CEPAL 2016 Latin American averages, What a Waste 2.0 for open dumps; the three externality penalties are ASSUMPTIONs (IDB origin listed as manual).

Ten largest changes (base-year price per vehicle and compiled CapitalCost):

| Tech | US$ per vehicle | M US$ per Gvkm | Note |
| --- | --- | --- | --- |
| TRBPUELE and TRBPRELE | 211,709 to 410,893 | 4,200.6 to 8,152.6 | ratio 1.92 confirmed; the diesel reference changes |
| TRBPUPHD and TRBPRPHD | 178,630 to 346,691 | 3,544.2 to 6,878.8 | ratio confirmed; the reference changes |
| TRBPUDSL and TRBPRDSL | 110,265 to 214,007 | 2,187.8 to 4,246.2 | |
| TRAUTPHG | 2.04 to 35,318.80 | 0.11 to 1,837.6 | ratio-chain fix |
| TRMBSPHD | 30,102 to 119,332 | 597.3 to 2,367.7 | |
| TRYLFDSL | 16,528 to 49,839 | 802.3 to 2,419.4 | |
| TRAUTHG | 2.04 to 31,028 | 0.11 to 1,614.4 | ratio-chain fix |
| TRYTKELE | 79,789 to 143,384 | 1,583.1 to 2,844.9 | |
| TRYLFGSL | 16,528 to 42,058 | 802.3 to 2,041.6 | |
| TRMBSELE | 35,676 to 95,781 | 707.9 to 1,900.4 | |

Also: TRAUTDSL 16,597 to 34,664 US$ and TRAUTGSL 16,597 to 28,022 US$. FixedCost: freight falls (TRYTKDSL 464.79 to 114.47 M US$ per Gvkm; light freight diesel, gasoline and LPG 236.83 to 92.64), cars rise (TRAUTDSL 61.65 to 93.39; TRAUTELE 20.34 to 63.11). Waste: collection 38.7 to 66.5 US$ per t, landfill 67.3 to 29.4, open dump 42.1 to 12.5.

Decisions for Luis:
1. `TRAUTHG` and `TRAUTPHG` ratio chain. Proposed cells 30,769.98 and 35,024.9 are the sourced prices divided by the proposed `TRAUTELE` ratio (1.00839), correct only if `TRAUTELE` is written as proposed. The cleaner fix is to change their `Unit.Introduced` to "Relative to TRAUTDSL"; the cells would then be 0.89511 and 1.01888.
2. Price basis. UN Comtrade 2024 CIF unit values, which mix new and used imports, are well below ATB: gasoline cars 22,250 against 28,022 US$; diesel cars 28,831 against 34,664; pickups up to 5 t 25,931 (diesel) and 17,508 (gasoline) against 49,839 and 42,058; diesel buses 87,521 against 214,007; hybrid cars 25,876 and electric cars 34,695 (no ATB counterpart used). The SAT valuation tables (manual) would settle this.
3. Bus and heavy-truck life 17 to 10 years (Dominican plan); Guatemalan buses are often imported used and run longer, so 17 may be kept as an ASSUMPTION.
4. Microbuses mapped to the ATB Class 4 step van (73,662 US$ against 18,581 today) may overstate a passenger van.
5. Waste externality penalties stay ASSUMPTIONs until the IDB documents can be opened.

Judgement calls: the shared method (ATB plus GEN-104 anchors) is followed instead of Comtrade unit values, which are partner estimates, CIF only and mixed with used vehicles; heavy trucks use the GEN-104-based diesel price (71,336 US$), not the ATB Class 8 tractor (194,835 US$); microbus distance is compared with the bus figure (44,000 km).

### 2.4 Honduras

Files: `HON/proposals_HON.csv`, `HON/sources_HON.csv` (HON-001 INE vehicle fleet 2017 to 2021; HON-002 UNDP, HEIFER and IHCAFE coffee value chain 2018; HON-003 INE agricultural census 2024 preliminary report, 1 manzana = 0.6993 ha; HON-004 World Bank exchange rate; HON-005 CIAT 2024 basic grains profile), `HON/search_log_HON.csv`, `HON/manual_downloads_HON.csv`.

Counts by class:

| Model | Confirmed | Replace | Assumption | Manual |
| --- | --- | --- | --- | --- |
| HON_ENERGY vehicles and chain inputs (1,379) | 222 | 1,089 | 68 | 0 |
| HON_AFOLU (49) | 2 | 6 | 41 | 0 |
| HON_WASTE (104) | 0 | 5 | 99 | 0 |
| Cells, total 1,532 | 224 | 1,100 | 208 | 0 |
| Pairs, total 124 | 28 | 80 | 16 | 0 |

What was used. No Honduran document publishes vehicle prices, distance per vehicle or vehicle life by type (no SAR or customs valuation table and no SAG or DICTA crop budget is online; the electric mobility strategy draft returns HTTP 403, manual). The vehicle sheet shares the Dominican template, so vehicles follow the same method as the Dominican Republic: GEN-104 prices treated as a regional price, ATB prices and powertrain ratios, the ATB 2022 Mid trajectory (multipliers 1.0 before 2024) and ATB maintenance.

Largest changes (real 2024 USD per vehicle; compiled M US$ per Gvkm at the proposed distance):
1. TRYTKHYD: 365,824 to 129,580 US$; 40,647 to 14,398.
2. TRBTURELE: 204,645 to 410,893 US$; 27,286 to 9,339 (distance 7,500 to 44,000 km).
3. TRBTURDSL and TRBTURGSL: 106,586 to 214,007 US$; 14,212 to 4,864.
4. TRYTKHD: 145,724 to 76,661 US$; 16,192 to 8,518.
5. TRBPUHYD: 399,698 to 388,741 US$; 15,373 to 8,835.
6. TRYTKELE: 198,340 to 143,434 US$; 22,038 to 15,937.
7. TRYLFDSL: 17,467 to 49,839 US$; 1,941 to 5,538.
8. TRSUVDSL: 19,681 to 43,270 US$; 2,624 to 5,769.
9. TRAUTDSL: 11,525 to 29,988 US$; 1,537 to 3,998.
10. AG_CAF VariableCost: 4,318.8 to 2,280.15 US$ per ha (HON-002).

Other sector changes: import prices that were 0 in the compiled model now carry a price (US$ per t: IMPCAF 1,503.4, IMPLEG 1,105.29, IMPRIC 656.61, IMPBAN 160.89; IMPMEL 610.13 as an ASSUMPTION); IMPFRI 725.9 to 1,209.25; waste collection 38.7 to 66.5 US$ per t, landfill 67.3 to 29.4, open dump 42.1 to 12.49.

Decisions for Luis:
1. Distances: buses, minibuses and tourism buses 44,000 km (now 26,000, 20,000 and 7,500), motorcycles 10,500 (now 7,327), all from the Dominican plan for lack of Honduran data; the tourism-bus change cuts that group's compiled capital cost by about two thirds.
2. Whether the Dominican plan's prices (GEN-104) may stand in for Honduras.
3. Vehicle lives: buses, heavy freight and motorcycles drop to 10 years (from 14 to 17); the hydrogen bus stays at 12 (within 25 percent), so bus lives become mixed; light vehicles keep 17, minibuses 14 or 16.
4. Coffee cost halves; the source excludes farm administration and interest, so the new value is a lower bound.
5. Rice stays an ASSUMPTION at 2,766.5 US$ per ha; the only Honduran budget (CIAT, 923 US$ per ha) is for low-input upland rice.
6. Five import prices that were 0 now carry a price, which changes how imports compete with domestic crops.
7. The open dump becomes cheaper than the landfill, as in What a Waste 2.0.

Judgement calls: banana import values use FAOSTAT years with official flags only (the 2022 FAO estimate of 35.56 US$ per t is left out); IMPLEG is read as vegetables (pulses differ by less than 10 percent); the CIAT bean budget (658.25 US$ per ha) is treated as national, so AG_FRI is confirmed; open dumping takes the top of the lower-middle-income range (10 US$ per t) for consistency with the Dominican Republic; waste penalties keep the current per-year values as ASSUMPTIONs in M US$ per kt.

### 2.5 Jamaica

Files: `JAM/proposals_JAM.csv`, `JAM/sources_JAM.csv` (JAM-001 Electric Vehicle Policy 2023, read and not cited; JAM-002 Office of Utilities Regulation EV consultation document 2021; JAM-003 Gleaner 2022 on the JUTC bus contract; JAM-004 UN Comtrade vehicle imports 2021, comparison only; JAM-005 World Bank exchange rate; JAM-006 Ministry of Agriculture and Fisheries Cost of Production Estimates 2022; JAM-007 Jamaica Information Service on JUTC buses, comparison only), `JAM/search_log_JAM.csv`, `JAM/manual_downloads_JAM.csv`.

Counts by class:

| Model | Confirmed | Replace | Assumption | Manual |
| --- | --- | --- | --- | --- |
| JAM_TRANSPORT vehicles and chain inputs (1,276) | 444 | 759 | 73 | 0 |
| JAM_AFOLU (53) | 6 | 18 | 29 | 0 |
| JAM_WASTE (455) | 0 | 280 | 175 | 0 |
| Cells, total 1,784 | 450 | 1,057 | 277 | 0 |
| Pairs, total 152 | 40 | 73 | 39 | 0 |

Departures from the shared method: ATB multipliers end in 2050 and JAM_TRANSPORT runs to 2055, so 2051 to 2055 hold the 2050 ratio; buses use the national JUTC contract (45 diesel buses for US$5.4 million and 5 electric buses for US$1.1 million, 2022) instead of the Dominican anchor; heavy-freight distance stays at 27,000 km as an ASSUMPTION (no shared distance fits).

Ten largest vehicle changes (compiled base-year M US$ per Gvkm at the proposed distance; real 2024 USD per vehicle in brackets):
1. TRYTKHYD: 13,549 to 4,799 (365,824 to 129,580); ratio 3.7086 to 1.8165.
2. TRBPUELE: 10,455 to 5,240 (470,474 to 235,812), national JUTC price.
3. TRYLFHD: 10,174 to 5,049 (101,743 to 50,494).
4. TRBPUHYD: 8,882 to 5,192 (399,698 to 233,645); ratio 3.75 to 2.19.
5. TRYTKHD: 5,397 to 2,839 (145,724 to 76,661).
6. TRYLFELE: 8,510 to 6,070 (85,103 to 60,699).
7. TRYTKELE: 7,346 to 5,312 (198,340 to 143,434); ratio confirmed, the diesel reference changes.
8. TRAUTDSL: 960 to 2,432 (11,525 to 48,634); price and distance both change.
9. TRYLFDSL: 3,606 to 4,984 (36,060 to 49,839).
10. TRMOTELE: 1,330 to 303 (15,955 to 3,636).

Largest sector changes (A-O unit): crop VariableCost in US$ per ha, AG_YAM 218 to 17,781, AG_FRT 685 to 12,124, AG_VEG 75 to 8,413, AG_POT 579 to 7,884, AG_PLA 148 to 6,682, AG_LEG 267 to 5,525 (Ministry budgets 2022); wastewater CapitalCost in M US$ per billion m3, SEWERWW 1,194 to 4,685 and AERO_PTAR 900 to 3,531; IMPCARPOL 3,542 to 1,120 US$ per t.

Decisions for Luis:
1. Light-duty prices include taxes. The only Jamaican car price (OUR 2021) includes import duty and taxes: petrol car 39,315 and Nissan Leaf 56,015 US$ in 2024 USD, against 15,553 and 23,066 today. SUV and pickup prices come from ATB (no Jamaican tax), so cars now cost more than SUVs. Choose tax-inclusive (proposed) or tax-exclusive prices (ATB: petrol car 28,022, electric 34,955).
2. Car and SUV distance from 12,000 to 20,000 km per year (OUR 2021), which lowers compiled M US$ per Gvkm by 40 percent at a given price.
3. Heavy trucks and motorcycles: OperationalLife from 15 to 10 years (Dominican plan, as for the Dominican Republic); Jamaica publishes no figure.
4. Crop cost unit and scale. The unit M US$ per Mha equals US$ per ha of harvested area (the activity is Mha). Current values are 12 to 106 times below the Ministry's 2022 operating costs per ha, with no single factor, so they are not one unit slip. Coffee CapitalCost 24.677 US$ per ha is a token value; livestock rows are per ha and similarly small. CapitalCost rows stay ASSUMPTIONs with ranges, because the Ministry budgets exclude establishment costs.
5. Waste externality penalties stay ASSUMPTIONs until the IDB documents are obtained.

Judgement calls: diesel bus confirmed at 106,586 US$ (sourced 128,625); the national electric-to-diesel bus price ratio is 1.83 against 2.04 for ATB Class 8; gasoline motorcycle 2,500 US$ as an ASSUMPTION (range 1,500 to 4,000); each crop's cost is the mean of the Ministry budgets for its mapped crops with one crop cycle per harvested ha (fruit uses pineapple only, legumes red peas only); imports use FAOSTAT 2019 to 2023 unit values (IMPCER uses the FAO cereal aggregate, which includes cereal preparations; maize alone, 316 US$ per t, is also within 25 percent). Not searched within the time: Jamaica Customs Agency, STATIN, Island Traffic Authority, Coffee Industry Regulation Division (GAPS).

### 2.6 Ecuador

Files: `ECU/proposals_ECU.csv`, `ECU/sources_ECU.csv` (ECU-001 Castillo 2013, Rimisp, with the MAGAP 2012 rice budget; ECU-002 Ibarra Velasquez et al. 2023, Polo del Conocimiento, quoting the MAG 2022 hard-maize cost; ECU-003 Castillo 2015, Rimisp working paper 144 on beef cattle; ECU-004 MAG SIPA palm-heart bulletin 2023), `ECU/search_log_ECU.csv`, `ECU/manual_downloads_ECU.csv` (none).

Scope and units. 119 sector cells, no vehicles: ECU_AGR 117 (CapitalCost, FixedCost and VariableCost of 11 crops, 9 livestock technologies and 19 imports, all Flat with the placeholder value 1) and ECU_WASTE 2 (collection). Read from the compiled BAU files: crops use cropland in Mha (output Mt at the model yield), so values are US$ per ha; livestock uses pasture in Mha (output million head; head per ha 1.638 for cattle, 0.5339 horses, 0.1068 camelids and mules, 0.0107 sheep, goats, pigs and poultry), so values are US$ per ha of pasture = cost per head x head per ha; imports produce Mt (crops, US$ per t) or million head (animals, US$ per head), so the A-O label "MUS$ / Mha" fits neither; waste is read as US$ per t.

Counts by class (cells equal pairs, all rows Flat): confirmed 0, replace 21, assumption 98, manual 0. Replace: 13 import VariableCost rows from FAOSTAT unit values plus IMPSUG as the cane equivalent of sugar; AG_ARR fixed and variable (MAGAP 2012); AG_MAI fixed and variable (MAG 2022); GA_BOV variable (Rimisp 2014); the 2 waste cells (CEPAL 2016). Assumption: other crop and livestock costs (value of production per ha used as total cost, split with the MAG maize fixed share 0.1725), capital costs, import capital and fixed costs (0), and IMPSOY, IMPOVE, IMPCBR, IMPCAM, IMPMUL.

Ten largest changes (every current value is 1; real 2024 USD in the unit stated):

| Rank | Row | Proposed value | Class and note |
| --- | --- | --- | --- |
| 1 | IMPCAB VariableCost | 8,181.68 US$ per head | replace; pedigree horses |
| 2 | IMPBOV VariableCost | 7,573.46 US$ per head | replace; breeding cattle, 52 head a year |
| 3 | AG_FRT VariableCost | 4,670.26 US$ per ha | assumption |
| 4 | IMPPAL VariableCost | 4,609.34 US$ per t | replace; FAO item 472, preserved product |
| 5 | AG_COF, AG_PAL, AG_FRT CapitalCost | 3,000 US$ per ha each | assumption |
| 6 | AG_VEG VariableCost | 2,989.03 US$ per ha | assumption |
| 7 | AG_TUB VariableCost | 2,487.64 US$ per ha | assumption |
| 8 | IMPCOF VariableCost | 2,473.98 US$ per t | replace |
| 9 | AG_SUG VariableCost | 2,281.00 US$ per ha | assumption |
| 10 | AG_SUG CapitalCost | 2,000 US$ per ha | assumption |

Also: AG_ARR variable 1,715.07 and fixed 363.44 US$ per ha; AG_MAI variable 1,562.86 and fixed 325.87; IMPPOR 1,902.42 US$ per head; collection capital 15.47 and variable 51.04 US$ per t (model total 38.7, sourced total 66.51).

Decisions for Luis:
1. Livestock imports supply the herds. In BAU 2021 the import technologies meet the whole herd demand for poultry (58.3 million head), pigs (3.26 million), sheep, goats, camelids, horses, mules and dairy cattle. FAOSTAT live-animal unit values are breeding-stock prices (pigs 1,902, cattle 7,573, horses 8,182 US$ per head); writing them would cost billions of US$ a year on herds that are raised in Ecuador. Decide whether import prices per head are written before the livestock structure is fixed.
2. Livestock per-ha values for sheep, goats, pigs and poultry are tiny (0.05 to 4 US$ per ha) because of the 0.0107 head per ha ratio; the per-head cost is in each derivation (pigs 370, poultry 5.82, sheep 29 US$ per head a year). Write them on the current ratios or wait for the ratios to be corrected.
3. IMPSUG ("Import Sugarcane") uses the sugar import unit value converted to cane with the national sugar-to-cane ratio 0.0575 (39.54 US$ per t); the alternative is to treat it as sugar (687.07).
4. IMPPAL: AG_PAL is palm hearts, not oil palm; FAO item 472 is a broad preserved-vegetables price (4,609 US$ per t), far above the farm-gate price of 340 US$ per t.
5. Cost split: where no national budget splits the cost, the MAG maize fixed share (17.25 percent) is used for every crop and animal (the MAGAP rice budget gives 17.5 percent). Capital costs are 0 for annual crops, livestock and imports, and ASSUMPTIONs for perennials.

Judgement calls: value of production per ha (FAOSTAT 2019 to 2023 producer price x yield, or the MAG bulletin for palm hearts) stands in for total cost where no national budget exists; on the two crops with budgets, maize value 1,708 against cost 1,889 and rice value 1,372 against cost 2,078 US$ per ha (real 2024). FAO yields are used, not the model yields; other cereals exclude rice and maize (FAO yield 1.51 t per ha, model 1.49); fruit excludes bananas and plantains. Beef cattle: Rimisp cost per head (mean 200.77 US$, 2014) x 1.638 head per ha = 435.78 US$ per ha (the direct Rimisp per-ha mean would be 285.97 in 2014 USD); land rent and herd value excluded. Waste: CEPAL collection plus transfer, split in the model's capital to variable proportion, as for the Dominican Republic and Honduras (Costa Rica used collection only). Rice: the MAGAP 2012 budget assumes about 7 t per ha, above the national yield, so the cost per ha is at the high end. Not found: SIPA has no cost-of-production section (404); 28 SIPA crop bulletins have no cost table; no national budget was downloadable for coffee, sugarcane, soy, pulses, other cereals, tubers, fruit, vegetables or dairy; the only Ecuadorian waste cost study shows values in box plots only.

## 3. Manual downloads

(Added at the end.)

## 4. Gates

(Added at the end.)
