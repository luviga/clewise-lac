# Cross-sector check (Phase E), fix_run2_20261120T225823Z

Read-only check of the 19 sector models beside the six energy models. Nothing in `C:\clw_fix` was changed except this file and `cross_sector_check.csv` (one row per country, sector model and check item).

## Method

- E1: listed each model folder, runner, scenarios (B1_Scenario_Config.xlsx, Activated = YES), years (YEAR column of `B1_Output_Params/BAU/*.csv`, or `1_Parameters/BAU` for GUA_AFOLU) and tracked outputs with their last commit date (`git log -1 --format=%ci`). Each folder was copied to `C:\clw_base_4ba69d6\_sector_scratch\<Country>_<Sector>\` and its own runner was run unchanged with Anaconda Python and glpsol 4.65, 20 minute limit, two models at a time. The runners solve every activated scenario, not only the base one. Logs: `C:\clw_base_4ba69d6\_sector_scratch\_logs\`.
- The 18 B1 runners all stop at once in the clone because `Executables/` is gitignored and absent. They were run a second time with an empty `Executables/` folder created in the scratch copy (no model file edited). Base status comes from the glpsol solution file header, read before the runner deletes it. The rerun BAU result was then compared with the tracked consolidated output (column sums of activity, production, emissions and discounted cost).
- E2: compared scenario names with the energy BAU, NDCNEW, LTSNEW and the energy years from `B1_Output_Params/BAU`.
- E3: energy values from `_STAGE3_RESULTS/stage3_results.xlsx` (ProductionByTechnologyAnnual, BAU). The file was rewritten at 2026-11-21 06:39 UTC, after the 06:00 UTC cut, and that version is used, except for the Dominican Republic: the current file has no DR rows because all three DR Stage 3 solves were UNDEFINED, so DR uses the previous file (2026-11-12 00:48 UTC). Energy inputs from `B1_Output_Params/BAU`. Sector values from the tracked BAU outputs (Ecuador values checked against the rerun and equal). Years 2021 to 2024. Conversions marked "indicative" use stated assumptions and are not model data.
- E4: counted non-zero rows of CapitalCost, FixedCost, VariableCost and EmissionsPenalty in `B1_Output_Params/<scenario>` (`1_Parameters` for GUA_AFOLU).

## E1. Models and solve status

| Country | Model | Runner | Activated scenarios | Years | Base solve | Seconds |
|---|---|---|---|---|---|---|
| Costa Rica | CR_AFOLU | t1_confection/B1_Base_Scenarios_Adj_Parallel.py | BAU NDCincond NDCcond DCC | 2018-2050 | optimal | 549.6 |
| Costa Rica | CR_IPPU | B1_Base_Scenarios_Adj_Parallel_IPPU.py | BAU NDCincond NDCcond DCC | 2018-2050 | optimal | 61.0 |
| Costa Rica | CR_WASTE | B1_Base_Scenarios_Adj_Parallel_Waste.py | BAU NDCincond NDCcond DCC | 2018-2050 | optimal | 296.0 |
| Dominican Republic | RD_AFOLU | B1_Base_Scenarios_Adj_Parallel.py | BAU NDCcond NDCincond | 2018-2050 | infeasible | 1177.3 |
| Dominican Republic | RD_IPPU | B1_Base_Scenarios_Adj_Parallel_IPPU.py | BAU NDCincond NDCcond | 2018-2050 | optimal | 22.9 |
| Dominican Republic | RD_WASTE | B1_Base_Scenarios_Adj_Parallel_Waste.py | BAU NDCincond NDCcond | 2018-2050 | optimal | 26.9 |
| Ecuador | ECU_AGR | B1_Base_Scenarios_Adj_Parallel_SIMPLE.py | BAU NDC LTS | 2021-2050 | optimal | 261.4 |
| Ecuador | ECU_USCUSS | B1_Base_Scenarios_Adj_Parallel_SIMPLE.py | BAU NDCINC NDCCON NDC | 2021-2050 | optimal | 912.4 |
| Ecuador | ECU_IPPU | B1_Base_Scenarios_Adj_Parallel_IPPU.py | BAU NDCincond NDCcond | 2021-2050 | optimal | 24.7 |
| Ecuador | ECU_WASTE | B1_Base_Scenarios_Adj_Parallel_Waste.py | BAU NDCincond NDCcond | 2021-2050 | optimal | 32.9 |
| Guatemala | GUA_AFOLU | 7_run_model_mathprog.py | BAU NDC LTS | 2016-2050 | optimal | 101.0 |
| Guatemala | GUA_IPPU | B1_Base_Scenarios_Adj_Parallel_IPPU.py | BAU NDP NDPhigh NDPlow | 2018-2050 | optimal | 27.1 |
| Guatemala | GUA_WASTE | B1_Base_Scenarios_Adj_Parallel_Waste.py | BAU NDP NDPhigh NDPlow | 2018-2050 | optimal | 101.9 |
| Honduras | HON_AFOLU | HON_AFOLU/B1_Base_Scenarios_Adj_Parallel.py | BAU NDP NDC | 2018-2050 | optimal | 542.2 |
| Honduras | HON_IPPU | B1_Base_Scenarios_Adj_Parallel_IPPU.py | BAU NDCincond NDCcond | 2018-2050 | optimal | 19.3 |
| Honduras | HON_WASTE | B1_Base_Scenarios_Adj_Parallel_Waste.py | BAU NDCincond NDCcond | 2018-2050 | optimal | 56.7 |
| Jamaica | JAM_AFOLU | B1_Base_Scenarios_Adj_Parallel.py | BAU LTS NDC | 2021-2055 | optimal | 202.9 |
| Jamaica | JAM_TRANSPORT | B1_Base_Scenarios_Adj_Parallel.py | BAU LTS NDCNEW LTSNEW LTSOPT | 2021-2055 | optimal | 202.8 |
| Jamaica | JAM_WASTE | B1_Base_Scenarios_Adj_Parallel.py | BAU LTS | 2021-2055 | optimal | 17.2 |

Seconds are for the whole runner (all activated scenarios, including output processing), with the energy Stage 3 run and another sector model sharing the machine.

- As cloned, all 18 B1 runners fail with `FileNotFoundError ... './Executables/BAU_0'` (JAM_TRANSPORT first fails on missing `B1_Output_Params/NDCNEW`). GUA_AFOLU needs no extra folder and solves as cloned.
- With an empty `Executables/`, 17 of 18 solve OPTIMAL in every activated scenario. RD_AFOLU is infeasible in all three scenarios (glpsol "PROBLEM HAS NO PRIMAL FEASIBLE SOLUTION", Status UNDEFINED, then `KeyError: 'AccumulatedNewCapacity'` in output processing), so its tracked RDOutput.csv does not come from the current inputs.
- JAM_TRANSPORT solves all five scenarios, but cannot write B1 parameter copies for NDCNEW, LTSNEW and LTSOPT because those `B1_Output_Params` folders do not exist.
- Rerun BAU equals the tracked output in 13 models. In the four Ecuador models the rerun differs (discounted cost: AGR 15,095 vs 12,257; USCUSS 948,380 vs 866,439; IPPU 3,556 vs 952; WASTE 17,138 vs 6,094), so the tracked Ecuador outputs predate the current inputs. GUA_AFOLU outputs are byte identical to the tracked files.
- No runner needs files from the energy models. B1 runners need `A2_Output_Params` (tracked) and `Executables/`; CR_AFOLU also reads `../config_main_files`; GUA_AFOLU runs the tracked `2_Model/<scenario>/data_land.txt` files, not `1_Parameters`.
- All tracked outputs (`*Output*.csv`, `*Input.csv`, `SelectedResults.csv`, GUA_AFOLU `2_Model` csv and txt files) exist; their last commit is the baseline commit of 2026-11-09 00:09:13 -0700.

## E2. Scenario and year alignment

| Country | Model | BAU | NDCNEW | LTSNEW | Years vs energy |
|---|---|---|---|---|---|
| Costa Rica | CR_AFOLU | aligned | mapped (NDCincond or NDCcond) | missing | differ (2018-2050) |
| Costa Rica | CR_IPPU | aligned | mapped (NDCincond or NDCcond) | missing | differ (2018-2050) |
| Costa Rica | CR_WASTE | aligned | mapped (NDCincond or NDCcond) | missing | differ (2018-2050) |
| Dominican Republic | RD_AFOLU | aligned | mapped (NDCcond or NDCincond) | mapped (inactive) (LTS or LTSNZ) | match (2018-2050) |
| Dominican Republic | RD_IPPU | aligned | mapped (NDCincond or NDCcond) | missing | match (2018-2050) |
| Dominican Republic | RD_WASTE | aligned | mapped (NDCincond or NDCcond) | missing | match (2018-2050) |
| Ecuador | ECU_AGR | aligned | mapped (NDC) | mapped (LTS) | match (2021-2050) |
| Ecuador | ECU_USCUSS | aligned | mapped (NDCINC or NDCCON or NDC) | missing | match (2021-2050) |
| Ecuador | ECU_IPPU | aligned | mapped (NDCincond or NDCcond) | missing | match (2021-2050) |
| Ecuador | ECU_WASTE | aligned | mapped (NDCincond or NDCcond) | missing | match (2021-2050) |
| Guatemala | GUA_AFOLU | aligned | mapped (NDC) | mapped (LTS) | differ (2016-2050) |
| Guatemala | GUA_IPPU | aligned | mapped (NDP) | missing | match (2018-2050) |
| Guatemala | GUA_WASTE | aligned | mapped (NDP) | missing | match (2018-2050) |
| Honduras | HON_AFOLU | aligned | mapped (NDP or NDC) | missing | match (2018-2050) |
| Honduras | HON_IPPU | aligned | mapped (NDCincond or NDCcond) | missing | match (2018-2050) |
| Honduras | HON_WASTE | aligned | mapped (NDCincond or NDCcond) | missing | match (2018-2050) |
| Jamaica | JAM_AFOLU | aligned | mapped (NDC) | mapped (LTS) | match (2021-2055) |
| Jamaica | JAM_TRANSPORT | aligned | aligned | aligned | match (2021-2055) |
| Jamaica | JAM_WASTE | aligned | missing | mapped (LTS) | match (2021-2055) |

- BAU is aligned everywhere. Only JAM_TRANSPORT uses the names NDCNEW and LTSNEW.
- NDCNEW maps to an NDC or NDP scenario in 17 models (JAM_TRANSPORT is aligned), often with two candidates (NDCincond, NDCcond). JAM_WASTE has no NDC scenario.
- LTSNEW maps to an LTS scenario only in ECU_AGR, GUA_AFOLU, JAM_AFOLU and JAM_WASTE (and RD_AFOLU, where LTS and LTSNZ are not activated). It is missing in the other 13; Costa Rica's DCC and Guatemala's NDPhigh are the nearest higher ambition scenarios.
- On the energy side NDCNEW and LTSNEW are copies of one folder in five countries (BAU in CR and Ecuador, NDCcond in DR, NDP in Guatemala and Honduras), so a mapping does not mean the scenarios differ.
- Years match except Costa Rica (sector 2018-2050, energy 2021-2050) and GUA_AFOLU (2016-2050 vs 2018-2050).

## E3. Links by values (BAU, 2021 to 2024)

Ethanol
- Costa Rica: energy PROETA makes 40.7, 42.6, 42.1, 42.9 PJ of ethanol, because BLEND_GSL takes 1.0 PJ of pure gasoline and 1.0 PJ of ethanol per PJ of blend (InputActivityRatio, mode 1). CR_AFOLU processes 3.91, 3.80, 3.32, 4.04 Mt of cane on 0.058 to 0.061 Mha. Even with all cane going to ethanol (80 L/t, 21.2 MJ/L, indicative) that is 5.6 to 6.9 PJ, so the energy model needs 6.1 to 7.5 times the country's cane. Disagree.
- Guatemala: flex fuel rows exist on the energy side but are 0 PJ in 2021-2024; GUA_AFOLU has no sugarcane row.
- DR, Ecuador, Honduras: no ethanol row on the energy side; AFOLU sugarcane area 0.125, 0.136 to 0.150, 0.061 to 0.070 Mha. Jamaica: no ethanol and no sugarcane row on either side.

Waste methane and biogas power
- Costa Rica: CR_WASTE fixes landfill methane recovery for electricity at 15,000 t CH4 a year (about 0.75 PJ at 50 MJ/kg) and flaring at 41,250; the energy model has no biogas fuel or plant. Missing on the energy side.
- Dominican Republic: energy PPDBGS 0.055 to 0.057 PJ of electricity (biogas input equal); RD_WASTE recovers no landfill methane (0). Disagree, unless the energy biogas is not from landfills. RD_AFOLU's own copy of PPDBGS (0.0554 PJ) agrees within 2%.
- Guatemala: energy PPBGS 0.094, 0.068, 0.080, 0.080 PJ (biogas input 0.33 to 0.46 PJ); GUA_WASTE recovery 0. Disagree.
- Ecuador: ECU_WASTE recovers 0.006 to 0.024 (unit not documented) for electricity; energy PPBGS is 0 (biogas 0.79 to 0.92 PJ goes to E5TROBGS). Disagree.
- Honduras and Jamaica: 0 on both sides. Agree.

Biomass
- Dominican Republic and Honduras: RD_AFOLU and HON_AFOLU each carry their own copy of the energy system, so values compare directly in PJ. DR firewood 13.5 to 15.0 PJ (energy) vs 18.8 to 18.9 (RD_AFOLU), ratio 0.72 to 0.80; DR other biomass 12.2 to 13.7 vs 15.0 to 18.2. Honduras firewood is equal in 2021-2022 (63.31, 61.26) and diverges in 2023-2024 (59.17 vs 62.46, 53.55 vs 63.69); other biomass ratio 0.96 to 1.15. Disagree.
- Guatemala: energy firewood 330 to 362 PJ vs GUA_AFOLU local firewood (Lena) 11.48 to 11.76 and Lena_total 16.16 to 16.43, unit not documented (an emission factor of 1.725 co2e per unit suggests tonnes of wood, probably Mt). At 15 GJ/t (indicative) the energy side is 1.9 times Lena and 1.4 times Lena_total. Cannot confirm.
- Costa Rica: energy cane products to industry 9.6 to 11.0 PJ vs CR_AFOLU bagasse 0.276 to 0.283 Mt (about 2.1 PJ at 7.7 GJ/t, indicative), ratio 4.5 to 5.0. Energy firewood is 0 in 2021-2024; AFOLU has wood plantation area only.
- Ecuador and Jamaica: AFOLU has forest area or burned area only (no harvested wood or residue row), so the energy firewood (Ecuador 8.2 to 9.1 PJ, Jamaica 3.1 PJ plus 0.6 PJ charcoal) cannot be compared. JAM_TRANSPORT biogas and biomass rows are 0, and energy DIST_BIM serves industry, so the scopes differ.

## E4. Cost parameters (non-zero rows in BAU)

| Model | CapitalCost | FixedCost | VariableCost | EmissionsPenalty |
|---|---|---|---|---|
| CR_AFOLU | 396 | 396 | 1217 | 0 |
| CR_IPPU | 0 | 0 | 0 | 0 |
| CR_WASTE | 528 | 165 | 396 | 0 |
| RD_AFOLU | 3234 | 3003 | 2574 | 396 |
| RD_IPPU | 0 | 0 | 0 | 0 |
| RD_WASTE | 495 | 132 | 396 | 0 |
| ECU_AGR | 1860 | 1860 | 3660 | 30 |
| ECU_USCUSS | 5160 | 5160 | 5970 | 30 |
| ECU_IPPU | 0 | 25 | 25 | 0 |
| ECU_WASTE | 270 | 0 | 300 | 120 |
| GUA_AFOLU | 411 | 35 | 481 | 385 |
| GUA_IPPU | 0 | 0 | 0 | 0 |
| GUA_WASTE | 363 | 0 | 396 | 165 |
| HON_AFOLU | 1908 | 1848 | 1320 | 330 |
| HON_IPPU | 0 | 33 | 33 | 0 |
| HON_WASTE | 363 | 0 | 396 | 165 |
| JAM_AFOLU | 595 | 560 | 980 | 140 |
| JAM_TRANSPORT | 910 | 910 | 175 | 35 |
| JAM_WASTE | 525 | 0 | 525 | 210 |

- IPPU has no CapitalCost in BAU in any country, as known, but non-zero CapitalCost in the policy scenarios of all five IPPU models (refrigerant and HFC technologies, for example CR 202 rows, ECU 150 to 175, GUA 52 to 100, HON 185, RD 100). ECU_IPPU and HON_IPPU carry FixedCost and VariableCost for PROD_CLK_TRAD in BAU (25 and 33 rows).
- ECU_AGR and ECU_USCUSS cost rows are all exactly 1.0 (placeholder values): 1,860 and 5,160 CapitalCost rows, for example.
- WASTE models have no FixedCost except CR_WASTE (165) and RD_WASTE (132); JAM_WASTE FixedCost rows are all 0.
- GUA_AFOLU counts are from `1_Parameters`; the runner solves `2_Model/<scenario>/data_land.txt`, which was not parsed for costs.

## What could not be checked

- RD_AFOLU base solve (infeasible), so its E3 values come from a tracked output that does not match current inputs; the cause of infeasibility was not investigated.
- Dominican Republic energy values come from the previous Stage 3 file, because the current Stage 3 DR solves are UNDEFINED.
- Units of several sector rows are not documented (GUA_AFOLU firewood, ECU_WASTE and JAM_WASTE methane recovery, CR_AFOLU bagasse); those comparisons are indicative only.
- No harvested wood or residue flow exists in the Ecuador, Jamaica and Costa Rica land models, and no sugarcane row exists in GUA_AFOLU or JAM_AFOLU, so those links can only be compared by area.
- Policy scenario links were not compared, because the scenario mapping in E2 is not one to one.
