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

Described in `vehicle_cost_chain.md`. In short: `CapitalCost (M US$ per Gvkm) = 1000 x price (US$ per vehicle) / distance (km per vehicle per year)`, with the distance of the vehicle's group from `A-O_Demand.xlsx` (`Ref.km.BY`) changed yearly by `A-Xtra_Projections.xlsx`. "Relative to" rows multiply the reference vehicle's base-year cell; trajectory rows multiply the base-year price by the year's cell. The battery replacement workbook is read and never used. All compiled 2024, 2030 and 2050 CapitalCost values with a non-zero price were recomputed exactly (186 rows per year). Findings: Guatemala `TRAUTHG` and `TRAUTPHG` chain a ratio onto a ratio and compile to 0.0694 M US$ per Gvkm (1.33 US$ per vehicle); Costa Rica's values labelled "US$ / vehicle" are about one hundredth of a vehicle price; OperationalLife is 1 year for Dominican Republic automobiles, motorcycles and taxis and for Costa Rica minibuses.

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

(Completed in the Dominican Republic section of Phase 2.)

### 1.6 Sourcing work

Phase 2 sources 352 vehicle pairs (Costa Rica 82, Dominican Republic 82, Guatemala 76, Honduras 60, JAM_TRANSPORT 52) and 301 sector pairs (CR_AFOLU 35, CR_WASTE 2, RD_AFOLU 41, RD_WASTE 5, ECU_AGR 117, ECU_WASTE 2, GUA_WASTE 8, HON_AFOLU 17, HON_WASTE 8, JAM_AFOLU 53, JAM_WASTE 13), plus the vehicle chain inputs (distance per vehicle and OperationalLife, `vehicle_chain_inputs.csv`). Many pairs share one source value (for example a crop's production cost and its import price), so the number of distinct values to find is smaller.

## 2. Phase 2 by country

(Added country by country.)

## 3. Manual downloads

(Added at the end.)

## 4. Gates

(Added at the end.)
