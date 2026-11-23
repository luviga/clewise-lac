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

## 3. Manual downloads

(Added at the end.)

## 4. Gates

(Added at the end.)
