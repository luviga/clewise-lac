# REPORT LAC_ALIGN 20261124T021708Z

Pull request: [luviga/clewise-lac#19](https://github.com/luviga/clewise-lac/pull/19) (draft, branch `job/align`).

Every Stage 3 solve of the six energy models is OPTIMAL in the final run (BAU, NDC and LTS of Costa Rica, the Dominican Republic, Ecuador, Guatemala, Honduras and Jamaica), including the two LTS solves with an energy emission cap. JAM_TRANSPORT and every sector model are OPTIMAL except RD_AFOLU, which was infeasible before this job and stays so for a cause in its own adoption rows (input for LAC_STAGE4). Judgement calls, limitations and incidents are in `GAPS_LAC_ALIGN_20261124T021708Z.md`; file by file changes in `CHANGES_LAC_ALIGN_20261124T021708Z.md`.

## What changed and why, step by step

**Step 0. Baseline.** A clean clone of `origin/main` was compiled and solved with the pipeline (7,935 s): all 18 Stage 3 solves OPTIMAL, objectives equal to the LAC_CLEANUP column. Sector models and JAM_TRANSPORT were solved with their own runners (`sector_baseline.csv`): all OPTIMAL except RD_AFOLU (three scenarios infeasible).

**Step 1. Sources.** `sources.csv` lists 49 sources with URL, retrieval date, local copy and SHA-256. Reopen gate (`reopen_check.csv`): 44 values confirmed in the archived copy (38 by text search, 6 by hand), 4 cost tables found with the number split across columns, 1 not confirmed. Leads (`leads_checked.csv`, 200 entries): 179 not relevant, 2 used (GEN-104, IPCC 2006), 8 opened and not used, 11 not reachable or landing pages only (`manual_downloads.csv`).

**Step 2. Published NDC and LTS values.** The 12 stylised rows of `inputs/scenarios/scenario_values.csv` are replaced by 33 published rows: renewable shares (Costa Rica 0.95 to 2035 and 1.0 from 2036 in LTS, Guatemala 0.80, Honduras 0.70, Jamaica 0.50 and 0.63, Jamaica LTS 0.90 to 1.0, Ecuador LTS 0.89 in 2050), new renewable capacity turned into a share by one capacity rule (Dominican 2030, Ecuador 2032, Jamaica 2041), and the two LTS emission assumptions (Dominican r = 0.56, Honduras r = 0.37). `renewable_targets.py` builds the targets each run; LTS equals NDC through 2035; a target is held after its last year. Transport targets go to the Tech_Adoption rows of Costa Rica and Honduras. The Dominican and Honduras LTS get a yearly energy emission cap from 2036 (`stage3_emission_cap.py`). `published_values_loaded.csv`: 155 rows loaded (34 value ids), 426 not loaded, each with its reason. Third readings: DR-T014 and DR-T015 agree.

**Step 3. Hydrogen and the orphan rule.** 70 hydrogen technologies of the six models form group `hydrogen`; the scenario rules step sets their activity to 0 in every scenario (solved activity 0, `hydrogen_check.csv`). The orphan cap applies in every country and scenario (the last exemption row is removed).

**Step 4. Stage 2.** Frozen output and committed builds are kept, and the non-committed fossil part gives way when they overflow the total; solar and wind keep their boundary output. Tests: hard 7/7, T8 continuity, T9 hydro freeze and the new T12 hole scan pass.

**Step 5. History.** History builds from regulator records (cells in the table below; 43 cases in `history_builds_after.csv`: 18 match the sourced commissioning, 11 do not, 14 have no record). Jamaica PPBIM residual capacity 0. The history identity rule makes every policy value up to 2024 equal to BAU in every solved data file (gate: 33,903 cells, 0 differences). The Dominican and Costa Rica policy plant rows, which carried caps from an earlier stylised target, take the BAU values.

**Step 6. Imports and emission factors.** Guatemala and Honduras import limits from 2025 (540 MW and 420 MW). Dominican and Honduras policy emission factors take the BAU rows (equal to IPCC 2006 within 6 percent); Ecuador's plant factors take IPCC 2006 x fuel input with the AR5 GWP of its inventory; Jamaica's SmartGrid road fuel rows of the policy scenarios take BAU.

**Step 7. Costs.** Vehicle prices, fixed costs and lives (1,289 cells: Costa Rica prices per vehicle, Guatemala TRAUTHG and TRAUTPHG, Dominican TRYLFNGS, 1-year lives); the four sourced distances are not written (Decisions for Luis). Sector cost proposals of 10 sector models (609 cells). Every EmissionsPenalty is 0; external costs are reported after the solve (`external_costs.csv`, 4,346 rows). Discount rates: Costa Rica 0.0831, Dominican Republic 0.12, Ecuador 0.12, Guatemala 0.07, Honduras 0.12, Jamaica 0.10262 (mean), in `B1_Default_Param.xlsx` and the output discounting.

**Step 8. Jamaica transport.** Old LTS renamed NDP, NDCNEW to NDC, LTSNEW to LTS; each scenario has its own A2 reference folder, which the A2 compiler now writes for every activated policy scenario. No NDCNEW or LTSNEW is left in tracked files of JAM_TRANSPORT. The dated JAMInput and JAMOutput copies are removed; JAMInput.csv and JAMOutput.csv are regenerated.

**Step 9. Recompile and full solve.** Final full run (align6) and a Stage 3 repeat (align7) after the locked-plant change; gates below.

### Values written per step and country

Cells of `value_register.csv` (16,188 rows) whose value changed, by step and country, with three example rows per step.

| step | CostaRica | DominicanRepublic | Ecuador | Guatemala | Honduras | Jamaica | all (configuration) | total |
|---|---|---|---|---|---|---|---|---|
| 2.5 transport targets | 44 | 0 | 0 | 0 | 72 | 0 | 0 | 116 |
| 3 hydrogen adoption rows | 0 | 0 | 0 | 108 | 0 | 0 | 0 | 108 |
| 5.1 history | 70 | 51 | 52 | 0 | 0 | 2 | 0 | 175 |
| 5.1 history, after the solves (fix 1) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 5.1 history, after the solves (fix 2) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 5.1 history, after the solves (fix 3) | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 16 |
| 5.1 history, after the solves (fix 4) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 5.1 history, after the solves (fix 5) | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 16 |
| 5.1 history, after the solves (fix 6) | 0 | 0 | 0 | 0 | 0 | 31 | 0 | 31 |
| 5.3 policy history rows (DR), pass 1 | 0 | 52 | 0 | 0 | 0 | 0 | 0 | 52 |
| 5.3 policy plant caps (DR), pass 2 | 0 | 22 | 0 | 0 | 0 | 0 | 0 | 22 |
| 5.3 policy plant limits (CR) | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 40 |
| 5.3 policy plant limits (DR), pass 3 | 0 | 62 | 0 | 0 | 0 | 0 | 0 | 62 |
| 5.3 policy-only plant caps opened (DR), pass 4 | 0 | 26 | 0 | 0 | 0 | 0 | 0 | 26 |
| 6.1-6.2 imports | 0 | 0 | 0 | 35 | 32 | 0 | 0 | 67 |
| 6.3 emission factors | 0 | 352 | 2396 | 0 | 1196 | 0 | 0 | 3944 |
| 6.3 emission factors (Jamaica road fuels) | 0 | 0 | 0 | 0 | 0 | 124 | 0 | 124 |
| 7.1-7.4 vehicles | 1210 | 11 | 0 | 68 | 0 | 0 | 0 | 1289 |
| 7.4 distances reverted | 0 | 2 | 0 | 1 | 1 | 2 | 0 | 6 |
| 7.5 sector costs | 11 | 281 | 2 | 5 | 12 | 298 | 0 | 609 |
| 7.6 penalties and 5.2 PPBIM | 0 | 539 | 361 | 683 | 528 | 432 | 0 | 2543 |
| 7.7 discount rate | 1 | 1 | 1 | 1 | 1 | 1 | 5 | 11 |
| 8 labels | 0 | 0 | 0 | 0 | 0 | 307 | 0 | 307 |

**2.5 transport targets**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| CostaRica/CR_ENERGY/t1_confection | Tech_Adoption | NDC / TRNBUSELE |  | v_2030 | 0.1 | 0.035 | CR-01 |
| Honduras/HON_ENERGY | Tech_Adoption | NDC / TRAUTELE |  | v_2030 | 0.1 | 0.03 | HON-01 |
| CostaRica/CR_ENERGY/t1_confection | Tech_Adoption | NDC / TRNBUSELE |  | v_2035 | 0.3 | 0.1 | CR-01 |

**3 hydrogen adoption rows**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Guatemala/GUA_ENERGY | Tech_Adoption | NDC / TRYTKHYD |  | Logistic | YES | NO | hydrogen technology: no adoption path; maximum 0 as in the B |
| Guatemala/GUA_ENERGY | Tech_Adoption | NDC / TRYTKHYD |  | Linear | NO | YES | hydrogen technology: no adoption path; maximum 0 as in the B |
| Guatemala/GUA_ENERGY | Tech_Adoption | NDC / TRYTKHYD |  | R2021 | 0.001 | n.a. | hydrogen technology: no adoption path; maximum 0 as in the B |

**5.1 history**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| CostaRica/CR_ENERGY/t1_confection | Secondary Techs | PWRFOI | ResidualCapacity | 2021 | 0.227242 | 0.227661 | HB-CENCE-2021, HB-CENCE-2022, HB-CENCE-2023, HB-CENCE-2024 |
| DominicanRepublic/RD_ENERGY | Primary Techs | PPPVT | TotalAnnualMaxCapacity | 2021 | 0.3657959 | 0.33746 | HB-OC-2021, HB-OC-2022, HB-OC-2023, HB-OC-2024 |
| Ecuador/ECU_Energy | Primary Techs | PPHRORPM | TotalAnnualMinCapacityInvestment | 2022 | 0.27 | 0.04845 | HB-ARCONEL-2022, HB-ARCONEL-2023 |

**5.1 history, after the solves (fix 1)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Electrical | BAU / PPICEFOI | TotalAnnualMaxCapacity | Exact_Values | 9999 ; 9999 ; 9999 ; 0.583419 ; 0.471952 | 9999 ; 9999 ; 9999 ; 0.583419 ; 0.472 ;  | HB-OC-2023, HB-OC-2024 |

**5.1 history, after the solves (fix 2)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Electrical | BAU / PPICEFOI | TotalAnnualMaxCapacity | Exact_Values | 9999 ; 9999 ; 9999 ; 0.583419 ; 0.472 ;  | 9999 ; 9999 ; 9999 ; 9999 ; 9999 ; 9999  | HB-OC-2023, HB-OC-2024 |

**5.1 history, after the solves (fix 3)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Ecuador/ECU_Energy | Primary Techs | PPHRORPM | TotalAnnualMaxCapacity | 2021 | 0.288 | 0.2881 | HB-ARCONEL-2021, HB-ARCONEL-2022, HB-ARCONEL-2023, HB-ARCONEL-2024 |
| Ecuador/ECU_Energy | Primary Techs | PPHRORPM | TotalAnnualMaxCapacity | 2022 | 0.33645 | 0.33655 | HB-ARCONEL-2021, HB-ARCONEL-2022, HB-ARCONEL-2023, HB-ARCONEL-2024 |
| Ecuador/ECU_Energy | Primary Techs | PPHRORPM | TotalAnnualMaxCapacity | 2023 | 0.33645 | 0.33655 | HB-ARCONEL-2021, HB-ARCONEL-2022, HB-ARCONEL-2023, HB-ARCONEL-2024 |

**5.1 history, after the solves (fix 4)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Primary Techs | PPPVT | CapacityFactor | 2025 | =P180 | 0.1873615249523615 | the years after 2024 keep the capacity factor they had (0.18 |

**5.1 history, after the solves (fix 5)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Ecuador/ECU_Energy | Electrical | NDC / PPHDAMPS | TotalAnnualMaxCapacity | Built-in Parameter-Set | NO | YES | the compiled inputs now carry a maximum capacity row of this |
| Ecuador/ECU_Energy | Electrical | NDC / PPHDAMPS | TotalAnnualMaxCapacity | Method | Write ; Interpolate ; Fix_Last | Overwrite ; Interpolate ; Fix_Last | the compiled inputs now carry a maximum capacity row of this |
| Ecuador/ECU_Energy | Electrical | NDC / PPHRORAS | TotalAnnualMaxCapacity | Built-in Parameter-Set | NO | YES | the compiled inputs now carry a maximum capacity row of this |

**5.1 history, after the solves (fix 6)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Jamaica/JAM_ENERGY | Primary Techs | PPHDAM | TotalTechnologyAnnualActivityLowerLimit | Projection.Mode | User defined | Flat | HB-OUR-AR2425 |
| Jamaica/JAM_ENERGY | Primary Techs | PPHDAM | TotalTechnologyAnnualActivityLowerLimit | 2021 | 0.49518 | =($I$185)*$I$190*8760*0.0036*0.999 | HB-OUR-AR2425 |
| Jamaica/JAM_ENERGY | Primary Techs | PPHDAM | TotalTechnologyAnnualActivityLowerLimit | 2022 | 0.427719 |  | HB-OUR-AR2425 |

**5.3 policy history rows (DR), pass 1**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPDBIM | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.0495561 ; 0.0491506 ; 0.0484814 ; 0.05 | 0.2326 ; 0.2485 ; 0.2167 ; 0.2336 ; 0.25 | history years up to 2024 take the compiled BAU value divided |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPHDAM | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 6.2139 ; 3.4668 ; 4.5335 ; 5.2779 ; 5.14 | 6.3343 ; 3.534 ; 4.6214 ; 5.3802 ; 5.24  | history years up to 2024 take the compiled BAU value divided |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPPVD | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.6181 ; 0.8716 ; 1.1765 ; 1.4598 ; 1.87 | 0.6181 ; 0.8716 ; 1.1765 ; 1.4598 ; 1.87 | history years up to 2024 take the compiled BAU value divided |

**5.3 policy plant caps (DR), pass 2**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPBIM | TotalAnnualMaxCapacity | Exact_Values | 0.028571 ; 0.028571 ; 0.028571 ; 0.02857 | 0.028571 ; 0.028571 ; 0.028571 ; 0.02857 | every year takes the compiled BAU value divided by the Secur |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPHDAM | TotalAnnualMaxCapacity | Exact_Values | 0.586381 ; 0.593619 ; 0.593619 ; 0.59361 | 0.586381 ; 0.593619 ; 0.593619 ; 0.59361 | every year takes the compiled BAU value divided by the Secur |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPPVD | TotalAnnualMaxCapacity | Exact_Values | 0.088571 ; 0.124952 ; 0.168667 ; 0.20923 | 0.088571 ; 0.124952 ; 0.168667 ; 0.20923 | every year takes the compiled BAU value divided by the Secur |

**5.3 policy plant limits (CR)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| CostaRica/CR_ENERGY/t1_confection | Electrical | NDC / PWRBMS | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.4503 ; 0.1987 ; 0.1985 ; 0.2151 ; 0.22 | 0.4503 ; 0.1987 ; 0.1985 ; 0.2151 ; 0.22 | every year takes the compiled BAU value divided by the Secur |
| CostaRica/CR_ENERGY/t1_confection | Electrical | NDC / PWRDSL | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.00269422 ; 0.00318348 ; 0.350421 ; 1.5 | 0.0027 ; 0.0032 ; 0.3504 ; 1.5763 ; 1.65 | every year takes the compiled BAU value divided by the Secur |
| CostaRica/CR_ENERGY/t1_confection | Electrical | NDC / PWRFOI | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.00735203 ; 0.327043 ; 1.84498 ; 3.2007 | 0.0074 ; 0.327 ; 1.845 ; 2.9829 ; 3.3692 | every year takes the compiled BAU value divided by the Secur |

**5.3 policy plant limits (DR), pass 3**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPBIM | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.7116 ; 0.7286 ; 0.5915 ; 0.7867 ; 0.74 | 0.7116 ; 0.7286 ; 0.5915 ; 0.7867 ; 0.74 | every year takes the compiled BAU value divided by the Secur |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPDBGS | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.0565 ; 0.0565 ; 0.0565 ; 0.0565 ; 0.05 | 0.0565 ; 0.0565 ; 0.0565 ; 0.0565 ; 0.05 | every year takes the compiled BAU value divided by the Secur |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPDBIM | TotalTechnologyAnnualActivityLowerLimit | Exact_Values | 0.2326 ; 0.2485 ; 0.2167 ; 0.2336 ; 0.25 | 0.2326 ; 0.2485 ; 0.2167 ; 0.2336 ; 0.25 | every year takes the compiled BAU value divided by the Secur |

**5.3 policy-only plant caps opened (DR), pass 4**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPBGS | TotalAnnualMaxCapacity | Exact_Values | 95238095237.14285 ; 95238095237.14285 ;  | 9522.857143 ; 9522.857143 ; 9522.857143  | every year takes the compiled BAU value divided by the Secur |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPDBGS | TotalAnnualMaxCapacity | Exact_Values | 95238095237.14285 ; 95238095237.14285 ;  | 9522.857143 ; 9522.857143 ; 9522.857143  | every year takes the compiled BAU value divided by the Secur |
| DominicanRepublic/RD_ENERGY | Electrical | LTS / PPDBIM | TotalAnnualMaxCapacity | Exact_Values | 95238095237.14285 ; 95238095237.14285 ;  | 9522.857143 ; 9522.857143 ; 9522.857143  | every year takes the compiled BAU value divided by the Secur |

**6.1-6.2 imports**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Guatemala/GUA_ENERGY | Electrical | BAU / IMP_ELE | TotalTechnologyAnnualActivityUpperLimit | Description Parameter-Set | Primary - Import - Electricity | Electricity imports: sourced history; fr | ALN-CNEE-2024, ALN-EOR-MEX-2021, ALN-EOR-MCTP-2025 |
| Honduras/HON_ENERGY | Primary Techs | IMP_ELE | TotalTechnologyAnnualActivityUpperLimit | 2025 | 99999 | 13.2451 | ALN-EOR-MCTP-2025 |
| Guatemala/GUA_ENERGY | Electrical | BAU / IMP_ELE | TotalTechnologyAnnualActivityUpperLimit | Linear | YES | NO | ALN-CNEE-2024, ALN-EOR-MEX-2021, ALN-EOR-MCTP-2025 |

**6.3 emission factors**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | EmissionsActivityRatio | LTS / PPCCTDSL / CO2e_PP | EmissionActivityRatio | 2018 | 0.1767 | 0.176666652 | ALN-IPCC2006-V2C2 |
| Honduras/HON_ENERGY | EmissionsActivityRatio | LTS / PPBIM / CH4_PP | EmissionActivityRatio | 2025 | 0.0001949634302167979 | 0.0001691556994072527 | ALN-IPCC2006-V2C2 |
| Ecuador/ECU_Energy | SmartGrid | BAU / PPDSL ; CO2e_PP | EmissionActivityRatio | 2021 | 0.1547483303114855 | 0.2148587043 | ALN-IPCC2006-V2C2, ECU-05 |

**6.3 emission factors (Jamaica road fuels)**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Jamaica/JAM_ENERGY | SmartGrid | NDC / T5DSLTRO | EmissionActivityRatio | 2025 | 1 | 0.9782608695652175 | value of the BAU row of the same technology: one emission fa |
| Jamaica/JAM_ENERGY | SmartGrid | NDC / T5DSLTRO | EmissionActivityRatio | 2026 | 1 | 0.972972972972973 | value of the BAU row of the same technology: one emission fa |
| Jamaica/JAM_ENERGY | SmartGrid | NDC / T5DSLTRO | EmissionActivityRatio | 2027 | 1 | 0.9677419354838711 | value of the BAU row of the same technology: one emission fa |

**7.1-7.4 vehicles**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| CostaRica/CR_ENERGY/t1_confection | Vehicle Techs | TRNBUSDSL | CapitalCost | 2021 | 1628.2624 | 96065.85333760001 | CR-001 |
| DominicanRepublic/RD_ENERGY | Vehicle Techs | TRYLFNGS | CapitalCost | 2018 | 17466.62 | 0.525215 | COMTRADE-JAM |
| Guatemala/GUA_ENERGY | Vehicle Techs | TRAUTHG | CapitalCost | 2018 | 1.021213590136161 | 0.507942 | COMTRADE-JAM |

**7.4 distances reverted**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_ENERGY | Demand_Projection | Techs_Buses_Pub | Ref.km.BY |  | 44000 | 33000 | GEN-104 |
| Guatemala/GUA_ENERGY | Demand_Projection | Techs_He_Freight | Ref.km.BY |  | 9000 | 50400 | GEN-104 |
| Honduras/HON_ENERGY | Demand_Projection | Techs_Buses_Tur | Ref.km.BY |  | 44000 | 7500 | GEN-104 |

**7.5 sector costs**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| CostaRica/CR_AFOLU/t1_confection | Primary Techs | IMPBAN | VariableCost | 2018 | 52.3 | 77.5 | GEN-201 |
| CostaRica/CR_WASTE | Secondary Techs | BLEND_NO_DCOLL | CapitalCost | 2018 | 0.009 | 0.011448 | GEN-206 |
| DominicanRepublic/RD_AFOLU | Primary Techs | IMPRIC | VariableCost | 2018 | 1445.56 | 743.63 | GEN-201;GEN-001 |

**7.6 penalties and 5.2 PPBIM**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| DominicanRepublic/RD_AFOLU | Externalities | PPCCTNGS / Health | EmissionsPenalty |  | 1000 | 0 | externalities out of the objective: penalty 0; external cost |
| DominicanRepublic/RD_ENERGY | Externalities | PPCCTNGS / Health | EmissionsPenalty |  | 1000 | 0 | externalities out of the objective: penalty 0; external cost |
| Ecuador/ECU_USCUSS | Externalities | T5NPRAND / EXT_REGAIR | EmissionsPenalty |  | -3.3825202 | 0 | externalities out of the objective: penalty 0; external cost |

**7.7 discount rate**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| CostaRica/CR_ENERGY/t1_confection | Default_Values |  | DiscountRate |  | 0.05 | 0.0831 | ALN-UNA-2024 |
| DominicanRepublic/RD_ENERGY | Default_Values |  | DiscountRate |  | 0.05 | 0.12 | ALN-UNA-2024 |
| Ecuador/ECU_Energy | Default_Values |  | DiscountRate |  | 0.05 | 0.12 | ALN-CEPAL-ECU-2021 |

**8 labels**

| model | sheet | tech | parameter | year | before | after | source |
|---|---|---|---|---|---|---|---|
| Jamaica/JAM_TRANSPORT | Scenarios | A3 | Name |  | LTS | NDP | scenario label (step 8) |
| Jamaica/JAM_TRANSPORT | Scenarios | A4 | Name |  | NDCNEW | NDC | scenario label (step 8) |
| Jamaica/JAM_TRANSPORT | Scenarios | A5 | Name |  | LTSNEW | LTS | scenario label (step 8) |

## Gate results

| gate | result |
|---|---|
| 9.1 compile diff against the baseline | 20,489 differences, 0 unexplained (`compile_diff.csv`, `compile_diff_unexplained.csv` empty) |
| 6.4 scenario differences | 2,011 groups, 0 without a policy measure (`scenario_difference_register.csv`) |
| 9.2 model files | `git diff --stat origin/main -- "*OSeMOSYS_Model.txt"` empty |
| 5.4 history identity | 33,903 history cells, 0 differences; 119 open upper bounds written as 99999 in BAU and as the block default in NDC and LTS (both no limit) |
| frozen output | 2,784 plant-years, 0 below the frozen value |
| hydrogen | 0 non-zero activity values |
| 9.3 energy models | B1: every solve OPTIMAL; Stage 0: 18/18 OPTIMAL; Stage 3: 18/18 OPTIMAL; cap step: Dominican LTS and Honduras LTS OPTIMAL, every capped year at or below its cap |
| 9.3 JAM_TRANSPORT | BAU, NDP, NDC, LTS, LTSOPT OPTIMAL |
| 9.3 sector models | 33 solves OPTIMAL; RD_AFOLU BAU, NDCcond, NDCincond infeasible (as in the baseline) |
| 9.4 Stage 0 tests | 10/10 |
| 9.4 Stage 1 tests | 13/13 |
| 9.4 Stage 2 tests | hard 7/7; T8 continuity, T9 hydro freeze, T12 hole scan pass |
| 9.4 Stage 3 tests | 11/11, T4 with no special case |
| 9.4 renewable targets | every milestone of each country's loaded targets met within tolerance (Stage 3 results, released cap years not checked) |
| 9.4 unit tests | `test_ao_cost_repair_manager`, `test_ao_safe_save` pass |
| Stage 3 share check | 244 cells more than 1 point from the controller: 238 in the released cap years of Dominican and Honduras LTS, 6 Jamaica PPPVT cells about 1.1 points above inside the 1.05 band (8 of this kind in the baseline) |
| 9.6 whitespace | `git diff --check` with `core.whitespace=cr-at-eol` clean; no em dash and no attribution line in the files written |

RD_AFOLU: its data files hold residual capacity above the maximum capacity of TRAUTELE (2018 to 2027) and TRMOTELE (2018 to 2025), from its own Tech_Adoption rows; dropping those two caps from the BAU data file makes it OPTIMAL. No value of this job enters these rows, so it is recorded for LAC_STAGE4.

## Objectives before and after

Stage 3 objective of every energy model solve and the objective of every sector model solve, baseline and after (`objectives.csv`). The energy objectives fall mostly from the national discount rates (all models used 0.05 before) and the zero emission penalties; Costa Rica rises with the vehicle prices re-entered per vehicle. JAM_TRANSPORT baseline LTS, NDCNEW, LTSNEW are matched to NDP, NDC, LTS.

| model | scenario | baseline | after | change % |
|---|---|---|---|---|
| CostaRica/CR_ENERGY/t1_confection | BAU | 114537.2847 | 131926.2883 | 15.18 |
| CostaRica/CR_ENERGY/t1_confection | NDC | 104231.3004 | 124520.8229 | 19.47 |
| CostaRica/CR_ENERGY/t1_confection | LTS | 95511.03799 | 121279.5019 | 26.98 |
| DominicanRepublic/RD_ENERGY | BAU | 411688.7579 | 112599.2212 | -72.65 |
| DominicanRepublic/RD_ENERGY | NDC | 430947.4136 | 112258.9043 | -73.95 |
| DominicanRepublic/RD_ENERGY | LTS | 455181.1777 | 110242.2479 | -75.78 |
| Ecuador/ECU_Energy | BAU | 268341.2784 | 144098.5268 | -46.30 |
| Ecuador/ECU_Energy | NDC | 257974.9215 | 140097.361 | -45.69 |
| Ecuador/ECU_Energy | LTS | 250736.464 | 138841.0049 | -44.63 |
| Guatemala/GUA_ENERGY | BAU | 360932.3291 | 368017.5832 | 1.96 |
| Guatemala/GUA_ENERGY | NDC | 347968.8583 | 353978.2166 | 1.73 |
| Guatemala/GUA_ENERGY | LTS | 346140.4368 | 351933.4809 | 1.67 |
| Honduras/HON_ENERGY | BAU | 104917.6359 | 47496.32223 | -54.73 |
| Honduras/HON_ENERGY | NDC | 103142.1113 | 47694.13754 | -53.76 |
| Honduras/HON_ENERGY | LTS | 100692.3388 | 47136.22967 | -53.19 |
| Jamaica/JAM_ENERGY | BAU | 65086.6886 | 35344.16603 | -45.70 |
| Jamaica/JAM_ENERGY | NDC | 61614.69871 | 34277.51185 | -44.37 |
| Jamaica/JAM_ENERGY | LTS | 59581.54338 | 33739.81495 | -43.37 |
| CostaRica/CR_AFOLU/t1_confection | BAU | 1238647.715 | 1225126.161 | -1.09 |
| CostaRica/CR_AFOLU/t1_confection | DCC | 1238925.1 | 1225341.703 | -1.10 |
| CostaRica/CR_AFOLU/t1_confection | NDCcond | 1238925.1 | 1225341.703 | -1.10 |
| CostaRica/CR_AFOLU/t1_confection | NDCincond | 1238647.715 | 1225126.161 | -1.09 |
| CostaRica/CR_WASTE | BAU | 5895.018545 | 6288.456425 | 6.67 |
| CostaRica/CR_WASTE | DCC | 7465.557518 | 7699.947422 | 3.14 |
| CostaRica/CR_WASTE | NDCcond | 7070.154726 | 7322.27939 | 3.57 |
| CostaRica/CR_WASTE | NDCincond | 5077.736658 | 5357.5427 | 5.51 |
| DominicanRepublic/RD_AFOLU | BAU | UNDEFINED | UNDEFINED |  |
| DominicanRepublic/RD_AFOLU | NDCcond | UNDEFINED | UNDEFINED |  |
| DominicanRepublic/RD_AFOLU | NDCincond | UNDEFINED | UNDEFINED |  |
| DominicanRepublic/RD_WASTE | BAU | 6329.862829 | 6216.041079 | -1.80 |
| DominicanRepublic/RD_WASTE | NDCcond | 7126.849159 | 6759.723846 | -5.15 |
| DominicanRepublic/RD_WASTE | NDCincond | 7126.849159 | 6759.723846 | -5.15 |
| Ecuador/ECU_WASTE | BAU | 17138.43361 | 17044.4785 | -0.55 |
| Ecuador/ECU_WASTE | NDCcond | 18112.34189 | 18026.7148 | -0.47 |
| Ecuador/ECU_WASTE | NDCincond | 17832.07863 | 17743.10098 | -0.50 |
| Ecuador/ECU_USCUSS | BAU | 948379.766 | 949103.5557 | 0.08 |
| Ecuador/ECU_USCUSS | NDC | 948379.766 | 948379.766 | 0.00 |
| Ecuador/ECU_USCUSS | NDCCON | 947037.5018 | 947037.5018 | 0.00 |
| Ecuador/ECU_USCUSS | NDCINC | 948379.766 | 949103.5557 | 0.08 |
| Guatemala/GUA_WASTE | BAU | 20926.61596 | 4408.015882 | -78.94 |
| Guatemala/GUA_WASTE | NDP | 12660.417 | 4770.768715 | -62.32 |
| Guatemala/GUA_WASTE | NDPhigh | 12466.26151 | 5557.717089 | -55.42 |
| Guatemala/GUA_WASTE | NDPlow | 16040.78487 | 4373.131948 | -72.74 |
| Honduras/HON_AFOLU/HON_AFOLU | BAU | 408335.3298 | 440208.1872 | 7.81 |
| Honduras/HON_AFOLU/HON_AFOLU | NDC | 392418.6089 | 431932.8307 | 10.07 |
| Honduras/HON_AFOLU/HON_AFOLU | NDP | 397264.4611 | 436301.0532 | 9.83 |
| Honduras/HON_WASTE | BAU | 19005.2584 | 4080.797577 | -78.53 |
| Honduras/HON_WASTE | NDCcond | 15494.94356 | 6403.609385 | -58.67 |
| Honduras/HON_WASTE | NDCincond | 15494.94356 | 6403.609385 | -58.67 |
| Jamaica/JAM_AFOLU | BAU | 8642.084056 | 18534.72677 | 114.47 |
| Jamaica/JAM_AFOLU | LTS | 8503.868992 | 18534.72677 | 117.96 |
| Jamaica/JAM_AFOLU | NDC | 8503.868992 | 18534.72677 | 117.96 |
| Jamaica/JAM_WASTE | BAU | 3156.931071 | 1318.499141 | -58.23 |
| Jamaica/JAM_WASTE | LTS | 2677.211371 | 1630.541287 | -39.10 |
| Jamaica/JAM_TRANSPORT | BAU | 60139.90118 | 57519.33497 | -4.36 |
| Jamaica/JAM_TRANSPORT | NDP | 49828.60175 | 47767.26099 | -4.14 |
| Jamaica/JAM_TRANSPORT | LTS | 49761.11207 | 47808.00158 | -3.92 |
| Jamaica/JAM_TRANSPORT | LTSOPT | 49761.11207 | 47808.00158 | -3.92 |
| Jamaica/JAM_TRANSPORT | NDC | 54331.58008 | 51632.75309 | -4.97 |

## Renewable share and energy emissions

Renewable share of power plant generation and energy emissions (kt CO2 eq, labels of group energy_report) from the final run (`results_summary.csv`).

| country | scenario | RE share 2030 | RE share 2035 | RE share 2050 | energy kt CO2 eq 2030 | 2035 | 2050 |
|---|---|---|---|---|---|---|---|
| CostaRica | BAU | 0.894 | 0.894 | 0.894 | 11,973 | 12,946 | 17,184 |
| CostaRica | LTS | 0.950 | 0.950 | 1.000 | 9,715 | 9,507 | 6,872 |
| CostaRica | NDC | 0.950 | 0.950 | 0.950 | 9,867 | 9,658 | 12,698 |
| DominicanRepublic | BAU | 0.208 | 0.247 | 0.353 | 33,682 | 38,366 | 53,400 |
| DominicanRepublic | LTS | 0.231 | 0.247 | 0.852 | 31,724 | 36,112 | 16,566 |
| DominicanRepublic | NDC | 0.231 | 0.247 | 0.353 | 31,724 | 36,140 | 50,126 |
| Ecuador | BAU | 0.771 | 0.781 | 0.812 | 32,739 | 37,724 | 49,307 |
| Ecuador | LTS | 0.920 | 1.000 | 0.889 | 28,536 | 28,549 | 33,361 |
| Ecuador | NDC | 0.920 | 1.000 | 1.000 | 28,662 | 28,704 | 38,730 |
| Guatemala | BAU | 0.656 | 0.614 | 0.623 | 32,240 | 41,577 | 72,916 |
| Guatemala | LTS | 0.680 | 0.800 | 0.800 | 30,693 | 32,796 | 48,786 |
| Guatemala | NDC | 0.680 | 0.802 | 0.800 | 30,623 | 33,495 | 57,528 |
| Honduras | BAU | 0.570 | 0.590 | 0.647 | 12,727 | 14,261 | 19,238 |
| Honduras | LTS | 0.701 | 0.701 | 1.000 | 11,274 | 12,630 | 12,120 |
| Honduras | NDC | 0.701 | 0.700 | 0.700 | 11,326 | 12,757 | 18,772 |
| Jamaica | BAU | 0.242 | 0.231 | 0.294 | 5,706 | 6,134 | 7,698 |
| Jamaica | LTS | 0.501 | 0.632 | 1.000 | 4,790 | 4,298 | 1,916 |
| Jamaica | NDC | 0.501 | 0.638 | 0.775 | 4,827 | 4,523 | 5,217 |

## Published emission levels against the model

Not imposed; reported after the solve (`emission_targets_check.csv`). Rows without a model value (Ecuador 2070 targets and the 2018 reference) fall in years the solved results do not hold.

| value id | country | scenario | year | target kt | model kt | result |
|---|---|---|---|---|---|---|
| ECU-T020 | Ecuador | LTS | 2035 | 39200.0 | 28549.2 | met |
| ECU-T021 | Ecuador | LTS | 2050 | 35800.0 | 33360.9 | met |
| ECU-T022 | Ecuador | LTS | 2070 | 33900.0 | no model year | not checked |
| ECU-P105 | Ecuador | LTS | 2018 | 38400.0 | no model year | not checked |
| ECU-P106 | Ecuador | LTS | 2035 | 39200.0 | 28549.2 | met |
| ECU-P107 | Ecuador | LTS | 2050 | 35800.0 | 33360.9 | met |
| ECU-P108 | Ecuador | LTS | 2070 | 33900.0 | no model year | not checked |
| GUA-T006 | Guatemala | NDC | 2035 | 27320.2 | 33495.0 | missed |
| GUA-P028 | Guatemala | NDC | 2035 | 27320.2 | 33495.0 | missed |
| HON-T055 | Honduras | NDC | 2022 | 10880.0 | 9763.8 | met |
| JAM-T017 | Jamaica | NDC | 2030 | 5800.0 | 4826.8 | met |
| JAM-T018 | Jamaica | NDC | 2035 | 5700.0 | 4522.7 | met |
| JAM-T019 | Jamaica | NDC | 2030 | 5500.0 | 4826.8 | met |
| JAM-T020 | Jamaica | NDC | 2035 | 4900.0 | 4522.7 | met |
| JAM-P004 | Jamaica | NDC | 2030 | 5800.0 | 4826.8 | met |
| JAM-P005 | Jamaica | NDC | 2035 | 5700.0 | 4522.7 | met |
| JAM-P006 | Jamaica | NDC | 2030 | 5500.0 | 4826.8 | met |
| JAM-P007 | Jamaica | NDC | 2035 | 4900.0 | 4522.7 | met |

## Decisions for Luis

1. **Honduras r = 0.37 instead of 0.47.** With r = 0.47 the Honduras LTS solve has no feasible solution. Relaxing one limit group at a time, only the capacity caps of the electric vehicle classes (Tech_Adoption rows of the published fleet targets HON-T026 to T029) restore it; emissions are counted at fuel supply, so the cap falls on road transport and industry. In 0.005 steps 0.37 is OPTIMAL and 0.375 is not. Loaded: r = 0.37 (2050 cap 12.12 Mt against BAU 2050 19.24 Mt; NDC 2035 12.76 Mt). Options: keep 0.37, let electric vehicles exceed the published fleet shares in LTS after 2035, or count a lower r.
2. **Locked plants keep their upper limit after the release.** The brief opens every upper limit from 2036 in the capped LTS scenarios. Opened, the Dominican LTS moved all fossil generation to the biomass plant in one year (PPBIM 1.1 PJ in 2035, 114 PJ in 2036, 235 PJ in 2050; emissions 10.5 Mt in 2036 against a cap of 35.3 Mt): the model has no biomass supply limit and biomass power is the cheapest plant at zero penalties. Biomass, biogas, bagasse and geothermal now keep the controller upper limit (Stage 1 holds them at their BAU share); solar, wind, hydro and fossil plants stay open. Result: Dominican LTS 23.9 Mt in 2036 and 16.6 Mt in 2050 (cap 23.5 Mt), solar 20 PJ in 2035, 57 PJ in 2036, 191 PJ in 2050; the oil plants stop in 2036, as the model holds no build rate limit for solar.
3. **Ecuador capacity rule above 1.** PME 2023-2032 adds 4,034 MW of hydro and 1,683 MW of other renewables by 2032; with the model's own capacity factors the rule gives a share of 1.35 of the model's 2032 generation. The rule writes at most `max_target_share` = 1.0, so Ecuador NDC holds 1.0 from 2032 and Ecuador LTS falls to PLANMICC's 0.89 by 2050 (below the NDC's held 1.0).
4. **Distances not written.** Sourced distances: Dominican public and tourism buses 44,000 km (GEN-104; model 33,000), Guatemala heavy freight 9,000 km (GEN-104; model 50,400), Honduras tourism buses 44,000 km (GEN-104; model 7,500), Jamaica cars and SUVs 20,000 km (JAM-002; model 12,000). Written, they rescale the transport demand the compilers derive from fleet x distance (Guatemala heavy freight demand fell from 97 to 17 in compiled units) against fixed policy limits, and the Guatemala policy scenarios had no feasible solution. All four are reverted; the values stay in the register as the range.
5. **Discount rates.** Guatemala: the source tabulates SEGEPLAN's move from 12 to 7 percent in 2022, and 7 percent is loaded; Jamaica publishes none and takes the mean of the five (0.10262). No source says real or nominal.
6. **Policy plant rows at BAU values.** Costa Rica and Dominican NDC and LTS plant caps and lower limits from an earlier stylised target (Costa Rica PWRGEO 0.267 GW in 2025 against BAU 0.525 GW) made the policy solves infeasible with the common history. They take the BAU values; Stage 3 sets the plant limits from 2025 from the published targets.
7. **Unsettled history cases.** Dominican PPICEFOI (recorded 0.4956 GW after the 2022 retirement cannot produce the model's 2022 generation of 12.1 PJ; the cap stays as before), Jamaica PPHDAM (yearly OUR values broke the runner; the flat row stays), and 9 other cases listed in GAPS keep their earlier values.
8. **RD_AFOLU** stays infeasible for the TRAUTELE and TRMOTELE rows of its own adoption sheet (input for LAC_STAGE4).

## Manual downloads

| URL | what waits for it |
|---|---|
| https://dgii.gov.do/estadisticas/parqueVehicular/Paginas/default.aspx | Dominican vehicle fleet |
| https://agricultura.gob.do/category/estadisticas-agropecuarias/costos-de-produccion-productos-agropecuarios/costos-de-produccion-por-productos-agropecuarios-2021/ | Dominican crop costs |
| http://documents.worldbank.org/curated/en/099112823121518054/P1793550846dd10c09d6806829ab581992 | Dominican vehicle prices, lives, distances (World Bank CCDR transport annex) |
| https://www.oc.do/Informes/Administrativos/Informe-Anual | Dominican capacity history (OC-SENI annual report 2023) |
| https://bioelectricidad.org/uploads/library/10.pdf | Dominican emission factors (inventory base year 2010) |
| https://www.cne.gob.do/wp-content/uploads/2022/08/Plan-Energetico-Nacional-WEB-2022.pdf | Dominican capacity history (national energy plan 2022) |
| https://www.oc.do/Informes/Operación-del-SENI/Planeación-del-SENI | Dominican capacity history (long-term operation programme 2024-2027) |
| https://www.rtv.co.cr/wp-content/uploads/AnuarioRiteve2018.pdf | Costa Rica vehicle distances and fleet age |
| https://www.recursosyenergia.gob.ec/wp-content/uploads/2024/08/BEN_2023-cap_7.pdf | Ecuador capacity history (energy balance 2023) |
| https://www.imf.org/en/Publications/WP/Issues/2019/05/02/Global-Fossil-Fuel-Subsidies-Remain-Large-An-Update-Based-on-Country-Level-Estimates-46509 | externality factors (IMF working paper) |
| https://ine.gob.hn/v4/docs/transporte/parque-vehicular-por-tipo-de-vehiculo-2018-2022-2/ | Honduras vehicle fleet 2018-2022 |

The values these bear on stay as ASSUMPTION or cited to another source of the register.

## Run times

| run | seconds |
|---|---|
| baseline full run (A2, B1, Stages 0 to 3, unit tests) | 7,935 |
| final full run align6: A2 and B1 of six countries | 1,902 |
| align6 Stage 0 | 1,856 |
| align6 Stages 1 and 2 | 23 |
| align6 Stage 3 with the cap step | 1,849 |
| align6 total | 5,639 |
| align7 Stage 3 repeat (solves 1,217, cap step 182) | 1,647 |
| sector models and JAM_TRANSPORT, compile and solve with their own runners | 23,875 (shared the machine with the energy runs) |
| JAM_TRANSPORT final compile and solve | 148 |
