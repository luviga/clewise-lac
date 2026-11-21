# BRIEF LAC_FIX_RUN2: hub 9 decisions written into the six energy models on job/fix-run, A2 and B1 recompiled, Stages 0 to 3 re-run, cross-sector check

Repository: https://github.com/luviga/clewise-lac, `main` at `c42ae07`. You build on draft PR #11, branch `job/fix-run`, head `4ba69d6`, job folder of the earlier run `_LAC_HUB/fix_run_20261111T200825Z/` (read it, never write it).

You work alone and to the end. This is a long run: expect 8 to 12 hours (source searches in Phase A, about 20 minutes for Stage 0 and 25 minutes for Stage 3 solves, B1 recompiles, possibly a second Stage 0 to 3 run for D7a). Never ask Luis anything and never wait for a reply. Every decided item in section 4 is applied without asking. Every finding that section 4 does not decide goes to GAPS with its values; you never decide it. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If a gate fails and you cannot repair it inside the decided scope, stop advancing past that phase, commit what passed, still run Phase E (read-only), write the three outputs and push. Never mark a pull request ready and never merge.

## 0. Restartability

Keep `PROGRESS.md` in the job folder. After every numbered step append one line: UTC time, step id (for example `B3`), done or blocked, and the key count. Commit and push at the end of every phase. If your context is compacted or the session restarts, read this brief, `PROGRESS.md` and the last commit message first, then continue from the first step not marked done. Every script you write is idempotent: it reads the workbook state, writes only cells whose value differs from the target, and logs what it wrote. Never rebuild `proposals.csv` from workbooks already written (the earlier run's incident 2).

## 1. Goal

Apply every decision Luis took between 11 and 17 November 2026 (hub 9) and on 20 November (hub 10) to the six energy models on `job/fix-run`, recompile A2 and B1, re-run Stages 0 to 3 once, and run a read-only cross-sector check. After this job, PR #11 is reviewed by values once more and merged. Stage 4, the code clean-up and the paper are later jobs.

## 2. The standard

The model runs only on externally sourced values, values a rule computes every run from sourced inputs, and labelled ASSUMPTIONs. A source is downloaded, retrievable and readable before it enters a model: an http(s) URL, DOI or public repository permalink that you opened, with the page or table and the retrieval date, and the file saved in `downloads/` with its SHA-256. Internal documents are never a source: no workbook, sheet or cell of this repository, no CSV we built, no handover, report or chat output. CLG documents (the Read the Docs sites of section 6 Phase A, the CLG GitHub country models, the Ecuador P3 report and the Ecuador NDC II initiatives workbook in `downloads/leads/`) are leads only: you follow the external documents they cite, download those, and cite those. Never write a value from memory.

Every constant inside a formula you write or touch is either a unit conversion (8,760 hours, 0.0036 PJ per GWh, 31.536 PJ per GW-year) or a labelled ASSUMPTION. Every derived value names its inputs and formula in `proposals.csv`.

An ASSUMPTION sentence states the value with unit and years, the plain reason, a check against a public document where one exists, and a range when the value matters. It never mentions our process, history, workbooks, cells, jobs or what was not found ("not found", "kept as used", "retained", "previously" are forbidden). Example of the form: "ASSUMPTION: the lower activity limit is 0.999 times the sourced output, a 0.1 percent band that keeps the solve feasible against rounding; a band of 2 percent would let output fall up to 2 percent below the sourced value."

Every number enters through a data file: A-O workbooks, `A-O_Demand.xlsx`, `B1_Scenario_Config.xlsx`, `_STAGE2_INPUTS/STAGE2_OVERWRITES_*.csv`. Never edit any `OSeMOSYS_Model.txt` or any script that holds model structure.

Scope is frozen. Do only what section 6 lists. Anything new goes to GAPS under "Known-limitation candidates" with where it is, the values, and one sentence on what it is. Do not fix it.

Commit messages and the pull request description carry no `Co-Authored-By` line and no "Generated with" line of any kind.

## 3. Facts already checked by values (hub 9 and hub 10, at `4ba69d6` unless stated)

F1. Ecuador crude chain, `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`, year columns from 2021:
- Primary Techs rows 387 and 388, `EXTT_CRU` activity upper and lower limit: upper 997.41 (2021), 1,005.22 (2024), 929.41 (2025 to 2030), 729.80 (2031), 631.97 (2035 on); lower = 0.98 x upper as plain values. Row 384 VariableCost = export value (11.86 USD/GJ in 2024).
- Primary Techs rows 137 and 138, `DIST_CRU` upper and lower: lower 0 every year; upper 999,999 except 0 in 2023. Row 134 VariableCost = Brent on WEO 2025 STEPS (13.93 in 2024).
- Secondary Techs rows 177 and 178, `PROCRU` upper and lower: 330.92 and 327.61 (2021), 332.57 and 329.25 from 2024. No source. `PROCRU` converts `E0CRU` to `E1CRU` (input 1.0) plus small product own-use.
- Secondary Techs `REF_DSL` rows 197/198, `REF_GSL` 207/208, `REF_LPG` 217/218, `REF_FOI` 227/228, `REF_JET` 237/238 (upper/lower), all User defined, no source; `REF_OPE` 247/248 is 0. Each takes `E1CRU` with InputActivityRatio 1.0. 2024 uppers 76.09, 56.88, 4.53, 133.37, 15.48 (sum 286.35 PJ); lowers 72.47, 55.76, 4.44, 130.76, 15.33 (sum 278.76 PJ); flat from 2024.
- `PPCRU` (Secondary Techs rows 107/108) takes `E1CRU` at 2.6484 per unit of activity, activity 4.06 to 4.50 PJ (about 11.9 PJ of crude).
- `A-O_Demand.xlsx`, Demand_Projection row 58, `E5EXPCRU`: BCE exports 2021 to 2025 and BCE outlook to 2030 (729.92 PJ in 2024, 655.88 in 2030); 2031 onward unchanged old values (falls to 0 from 2038). Demand Techs row 203 `T5CRUEXP` VariableCost = minus the export value.
- Sources already in the earlier job folder `sources.csv` and `downloads/`: ECUF-01 (BCE series, processed crude row 51), ECUF-03 (BCE Programacion Macroeconomica 2026-2030, Tabla 2 field production 168.3, 169.0, 171.3, 173.9, 174.7 million bbl for 2026 to 2030), ECUF-06 (MDEP-BCE Programacion Macroeconomica, Anexo 3, refinery loads 47, 54, 59, 59, 59 million bbl for 2026 to 2030), ECU-002, GEN-001, GEN-002 (net calorific value 5.778689 GJ per bbl).
- Hub 9 computation: BCE processed crude 309.0 (2021), 325.7, 308.4, 262.8 (2024), 228.5 PJ (2025); Anexo 3 loads 271.6, 312.0, 340.9, 340.9, 340.9 PJ (2026 to 2030); 2030 field production 1,009.5 PJ. Expected crude imports after items 1 and 2: about 2.1 PJ (2021) and 8.9, 7.8, 6.8, 1.2 PJ (2026 to 2029), 0 in other years.

F2. Ecuador `PPHD` (Primary Techs rows 332 to 340): residual 0.648 GW, CapacityFactor 0.11, CapitalCost 4,240.92 USD/kW, activity lower limit 2.14 to 2.19 PJ. It has no CapacityToActivityUnit and no OperationalLife row in `Fixed Horizon Parameters`, so the conversion defaults to 1: Stage 3 builds 576.7 GW of new `PPHD` per scenario (79.1 GW in 2021 to 2024), about 2.45 trillion USD undiscounted capital.

F3. Ecuador OperationalLife (`Fixed Horizon Parameters`, Value column): every OperationalLife row equals the CapacityToActivityUnit row above it, in all 111 rows of `B1_Output_Params/BAU/OperationalLife.csv`: 31.536 or 31.54 years for all 32 power plants, 1 year for the 78 other technologies. The other five countries carry plant lives of 15 to 50 years and grid lives of 30 to 60 years. Ecuador technologies with CapitalCost above 0: 36 (`ELE_DIST`, `ELE_TRANS`, `HYD_G_PROD`, `STOELE`, `PRONGS` and 31 `PP*` plants including `PPHD`); `PPHD` and `PRONGS` have no OperationalLife row. With a one-year life, `ELE_TRANS` and `ELE_DIST` are rebuilt every year: new capacity 3,445 and 3,024 PJ/yr summed over 2021 to 2050 in BAU, about 98,800 and 173,300 MUSD undiscounted capital per scenario.

F4. Power-plant new capacity in 2021 to 2024 at `4ba69d6` (Stage 3, GW, BAU / NDCNEW / LTSNEW): Costa Rica `PWRDSL` 0.104 all, `PWRFOI` 0.076 all, `PWRGEO` 0.063 / 0.031 / 0.031, `PWRHYDROR` 0.105 / 0 / 0, `PWRSPVTRN` 0.013 / 0.010 / 0.010, `PWRSUG` 0 / 1.241 / 1.792, `PWRWNONS` 0.086 / 0.029 / 0.029; Dominican Republic `PPPVT` 0.488, `PPPVD` 0.143, `PPICEFOI` 0.080 / 0.067 / 0.075, `PPWNDON` 0.047, `PPANGS` 0.033 to 0.036, `PPAFOI` 0.029, `PPDHYD` 0 / 0.017 / 0.015, `PPDBGS` 0.0004 / 0.017 / 0.017, smaller others; Ecuador `PPHD` 79.1, `PPRDSL` 0.618, `PPHRORAS` 0.442 to 0.444, `PPHRORPM` 0.270, `PPNGS` 0.117, `PPPVD` 0.115, `PPFOI` 0.095 to 0.103, `PPHDAMPS` 0.049, `PPWNDON` 0.032, smaller others; Guatemala `PPNGS` 0.0007; Honduras none; Jamaica `PPNGS` 0.021, `PPDSL` 0.008, `PPHDAM` 0.004, smaller others. Lead for Ecuador: the P3 report (Tabla 5, based on ARCONEL 2022) lists 0.02 GW of small Amazon run-of-river capacity and Toachi Pilaton Sarapullo 49 MW in 2022.

F5. History by scenario at `4ba69d6` (earlier REPORT section 1 and GAPS items 31 to 38): Costa Rica policy scenarios run `PWRSUG` in 2021 to 2024 because their transport history (B1 sheets Tech_Adoption, Mode_Shift, Occupancy_Rate, Distance_Levers, T_Elasticity, rows that start in history) carries more demand; with those rows set to BAU for 2021 to 2024, NDCNEW solves with BAU's `PWRSUG` cap of 0 (earlier test solves). Dominican Republic `PPDHYD`, `PPDBGS`, `PPDBIM` history lower limits kept at PR #10 values (12 cells, `r6_not_applied.csv`) because BAU's force capacity (`PPDHYD` CapacityFactor 0.0152, `PPDBGS` 0.0812) above the policy caps from 2025. Costa Rica 2021 lower limits of `PWRBMS` (BAU 0.4503 PJ) and `PWRHYDROR` (20.742 PJ) need capacity above the residual (1.2301 GW against 1.23). Ecuador LTSNEW 2022: 3.46 PJ shifted from `PPHRORAS` to `PPHRORPM`, same total.

F6. Emission-factor rows added by the earlier run for history alignment (`_LAC_HUB/fix_run_20261111T200825Z/scripts/r6_ear_rows_Honduras_DominicanRepublic_Ecuador_Jamaica.csv`): 78 rows in NDCNEW and LTSNEW together (Dominican Republic 12, Ecuador 20, Honduras 46), copying 39 BAU rows (Dominican Republic 6, Ecuador 10, Honduras 23) of history emission factors for power plants and the refinery.

F7. Jamaica `PPHROR`: Stage 3 builds 34.45 MW against the IRP-2 plan of 34.3 MW (2027 12.96, 2028 7.13, 2029 11.15, 2031 2.11, 2032 1.11 MW). Cause: the Stage 2 controller lower limit from 2032 is 0.5874 PJ against 0.5848 PJ that 34.3 MW produce at capacity factor 0.543, and Stage 3's `--uncap-pp-maxcap` lifts the plan cap from 2025. `_STAGE2_INPUTS/STAGE2_OVERWRITES_Jamaica.csv` columns `Country,Scenario,Tech,Year,New_Share_Pct,Note`; `PPHROR` lines exist for 2018 to 2026 in each scenario.

F8. Honduras `HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, Secondary Techs row 27, `PPBGS` CapitalCost: 7,269.10 USD/kW in 2018 to 2020 (IRENA 2012 biogas Case 10, R1F-11, converted with BEN-004); 5,390.58 in 2021 falling to 3,870.85 in 2050, no source.

F9. Guatemala `GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, Primary Techs row 284, `DIST_FLEXFUEL` VariableCost: CEPEA/ESALQ hydrated-ethanol price per GJ for 2018 to 2024 (20.80 USD/GJ in 2024), then the 2024 value moved with `DIST_GSL` (row 14, 22.11 USD/GJ in 2024). Sources R1F-14, R1F-15, R1F-18 in the earlier job; ANP and CEPEA data give a Brazilian ethanol-to-gasoline ratio of 1.14 to 1.72 per GJ over 2018 to 2024 (earlier GAPS item 1).

F10. Lower bands written as 0.98 times a value: Dominican Republic A-O, 19 TotalTechnologyAnnualActivityLowerLimit rows whose formulas contain the factor 0.98 (Primary Techs 138, 168, 178, 208, 228; Secondary Techs 48, 78, 98, 128, 138, 148, 158, 168, 178, 188, 198, 208, 218, 228); Jamaica A-O, 7 rows (Primary Techs 188, 198; Secondary Techs 88, 138, 148, 158, 168); Ecuador `EXTT_CRU` row 388 (plain values, 0.98 x upper). Not in the set: Dominican Republic Secondary Techs row 100 (`PPCCTNGS` CapacityFactor, a formula dividing by 0.98) and row 116 (`PPICEFOI` max capacity).

F11. Dominican Republic A-O Secondary Techs: J232 `ELE_TRANS` CapitalCost 3.3093 (ETED plan, R1F-01); J233 `ELE_TRANS` FixedCost `=J232*0.5%`; J253 `ELE_DIST` FixedCost `=J232*0.5%` (it references the transmission capital cost); J252 `ELE_DIST` CapitalCost is a formula of constants `=(82.70071105+32.95726026+54.56960634)/(5.501*8760*0.0036)`.

F12. Guatemala hydro output (PJ, 2026 / 2030 / 2040 / 2050): BAU 21.13 / 24.29 / 24.29 / 24.29; NDCNEW 24.12 / 27.28 / 27.28 / 27.28; LTSNEW 24.12 / 27.28 / 27.28 / 27.28. Hydro in the other five countries differs across scenarios by at most 0.17 PJ. Stage 3 pins every power plant's output from 2025 (upper = lower x 1.05) from the Stage 2 controller.

F13. Costa Rica `E5INDCOA` 2021 demand compiles as 0.0067 PJ (sourced 0.00667, MINAE balance 2022, Tabla 3); keep it.

F14. Tests at `4ba69d6`: Stage 0 10 of 10; Stage 1 13 of 13; Stage 2 hard 7 of 7, soft T8 65, T9 87, T11a 1; Stage 3 10 of 11 (T4, 40 Guatemala cells, the documented `--skip-orphan-cap Guatemala` effect); 18 of 18 OPTIMAL; RE targets met.

F15. Sector models beside energy (hub 9): Costa Rica, Dominican Republic, Guatemala, Honduras: AFOLU, IPPU, WASTE; Ecuador: AGR, USCUSS, IPPU, WASTE; Jamaica: AFOLU, TRANSPORT, WASTE. Guatemala AFOLU uses folders `1_Parameters` and `2_Model` and scenarios BAU, NDC, LTS. IPPU has no capital cost in any country. No file links the sector models to the energy models.

Pipeline: canonical A2 and B1 commands per country in `_LAC_HUB/cost_write_run_20261111T071733Z/pipeline_commands.csv`; drivers `_LAC_HUB/fix_run_20261111T200825Z/scripts/a2_driver.py` and `b1_driver.py`; keyed comparison `scripts/keyed_compare.py`; checks `scripts/fix_checks.py`; stage commands in `PIPELINE_WORKFLOW.md` (Stage 3: `py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala`). Writer: `ao_cost_repair_manager.py` (manifest, apply, verify) or openpyxl plus `save_ao_safely`. You may copy the earlier job's scripts into your job folder and adapt them.

## 4. Decisions in force

Luis, 11 to 17 November 2026 (hub 9), and 20 November (hub 10). Apply each one exactly.

D-ECU1. Ecuador crude after 2030: from 2031 to 2050 the `EXTT_CRU` activity limits, the `E5EXPCRU` demand and the refinery crude rows (`REF_*`, after D-ECU2) hold their 2030 values. ASSUMPTION sentence: "ASSUMPTION: crude production, crude exports and refinery runs from 2031 to 2050 hold their 2030 values (field production 174.7 million bbl, 1,009.5 PJ). The BCE Programacion Macroeconomica 2026-2030 ends in 2030 and no national outlook covers later years; holding 2030 keeps the 2030 balance of production, exports and refining."

D-ECU2. Ecuador crude balance:
- (a) `PROCRU` activity lower limit 0 in every year, upper limit 999,999 (not binding) in every year.
- (b) `EXTT_CRU` 2026 to 2030 from BCE field production (ECUF-03 Tabla 2) times 5.778689 GJ per bbl: upper = production, lower = band x upper (band from D7a). The earlier cap at the 2025 level is removed.
- (c) Total refinery crude use: target T(y) = BCE observed processed crude for 2021 to 2025 (ECUF-01 row 51) and MDEP-BCE Anexo 3 loads for 2026 to 2030 (ECUF-06), held at 2030 from 2031. For each year, k(y) = T(y) divided by the sum of the current `REF_*` upper limits; new upper = k(y) x current upper for each product (product shares unchanged); new lower = new upper x the row's current lower-to-upper ratio for that year (band ratios unchanged). Recompute T from the downloaded files and compare with F1; a difference above 0.5 percent goes to GAPS with both numbers.
- (d) `DIST_CRU` lower limit 0 and upper limit 999,999 in every year 2021 to 2050 (this opens 2023), VariableCost unchanged (Brent on WEO 2025 STEPS).
- Imports are not tuned. Report crude imports per year and scenario; any year above 1 percent of production goes to GAPS with values.

D1. Ecuador `PPHD`: add a CapacityToActivityUnit row of 31.536 (PJ per GW-year, a unit conversion) and an OperationalLife row under D12, in `Fixed Horizon Parameters`, matching the layout of the other Ecuador hydro rows.

D2. History, all six countries: every scenario shares BAU history through 2024, transport rows included.
- (a) For every NDCNEW and LTSNEW B1 output value with a year from 2018 to 2024, the value equals BAU's (relative tolerance 1e-4); every value from 2025 on equals its value at `4ba69d6` unless another decided item changes it. Where a config row's method (growth rates, interpolation from a history start) cannot give both, rewrite that row as explicit year points that reproduce BAU history and the `4ba69d6` compiled values from 2025 exactly. This covers the transport rows of F5 and the Costa Rica `PWRSUG` history cap of 0.
- (b) Every history activity lower limit (2018 to 2024) is reachable with existing plants: lower limit at most (residual capacity plus sourced commissioning up to that year) x CapacityFactor x AvailabilityFactor x CapacityToActivityUnit.
- (c) Every power-plant new capacity in 2021 to 2024 (F4) either matches a sourced commissioning (national regulator or operator statistics: ARCONEL, CENACE or CELEC for Ecuador; ICE or CENCE for Costa Rica; OC-SENI or CNE for the Dominican Republic; AMM or MEM for Guatemala; ODS or ENEE for Honduras; JPS, OUR or MSETT for Jamaica) within 5 percent or 2 MW, whichever is larger, or is removed by fixing its cause: the capacity factor, the residual capacity or the history limit, each written from a source. Record every technology in `history_builds.csv` (country, tech, scenario, built GW 2021 to 2024 before and after, sourced commissioning GW with plant names and dates, source ids, cause, fix).
- (d) This covers Costa Rica `PWRSUG` and `PWRHYDROR`, Costa Rica 2021 lower limits of `PWRBMS` and `PWRHYDROR`, Dominican Republic `PPDHYD` (capacity factor 0.0152), `PPDBGS`, `PPDBIM` (the 12 cells of `r6_not_applied.csv` take BAU history once their cause is fixed), Ecuador `PPHRORAS`, `PPHRORPM`, `PPRDSL` and the LTSNEW 2022 run-of-river split. A capacity factor or residual capacity you change from a source applies in every year and every scenario of that country.

D3. The 78 history emission-factor rows of F6 stay, on condition that every BAU history factor they copy (39 BAU rows) has an external source. For each BAU row and year 2018 to 2024: find the source (national GHG inventory or BUR tables with the activity they rest on, or the IPCC 2006 default the inventory states it uses) and record it; a factor computed as inventory emissions divided by inventory activity is a rule from sourced inputs and names both. Where no source exists, write an ASSUMPTION sentence with the value, the reason and the IPCC 2006 default range for that fuel and gas as the check. If the source gives a different value, write the source value into the BAU row and the copies (history years only) and log it. The four-decimal rounding of Dominican Republic and Ecuador B1 stays (decided as cosmetic).

D4. Jamaica `PPHROR`: overwrite lines in `_STAGE2_INPUTS/STAGE2_OVERWRITES_Jamaica.csv` for every year 2027 to the last year of the controller, in all three scenarios, so the Stage 2 lower limit equals the output of the cumulative IRP-2 plan (12.9, 7.1, 11.1, 2.1, 1.1 MW added in 2027, 2028, 2029, 2031, 2032; 34.3 MW) at capacity factor 0.543: share = plan GW x 0.543 x 31.536 / that scenario's Stage 0 denominator for that year, written with at least six significant digits. Note column cites the 2022 IRP (JAMF-01) and the formula.

D5. Honduras `PPBGS` CapitalCost: 7,269.10 USD/kW (sourced, R1F-11) in every year 2018 to 2050; row 27 becomes Flat or User defined with the same value in every year. Luis's standing rule: keep only sourced values; an unsourced value is replaced, never kept.

D6. Guatemala `DIST_FLEXFUEL` VariableCost (row 284): for each year 2018 to 2024, r(y) = Brazilian hydrated-ethanol price per GJ divided by Brazilian pre-tax gasoline price per GJ in the same year (CEPEA/ESALQ ex-mill and ANP producer prices, both pre-tax, both from downloaded files); value(y) = r(y) x Guatemala `DIST_GSL` VariableCost(y). From 2025, value(y) = mean of r over 2018 to 2024 x `DIST_GSL`(y) (the fuel-price anchor rule decided on 9 November). ASSUMPTION sentence with the ratio range and that the blend is valued at the Brazilian hydrated-ethanol to gasoline ratio because no Central American flex-fuel price series is published. If a pre-tax Brazilian gasoline series cannot be downloaded for a year, use the nearest year with both and log it.

D7a. Every lower band of F10 written as 0.98 times a value (DR 19 rows, Jamaica 7 rows, Ecuador `EXTT_CRU` row 388, and any lower limit this job writes as a band) uses 0.999. Keep 0.999 for a row only where all 18 Stage 3 solves (and all 19 B1 solves) stay OPTIMAL; otherwise put that row back to 0.98 and log it. Procedure: write 0.999 everywhere in Phase B; in Phase C, if a country's B1 solve is infeasible, find the rows by test solves (revert halves of that country's rows) and set only those back to 0.98; in Phase D, if a Stage 3 solve is infeasible, revert that country's rows to 0.98 by the same search and run Stages 0 to 3 once more. Each band carries the ASSUMPTION sentence of section 2 with its own value.

D7b. Dominican Republic `ELE_TRANS` FixedCost (J233, 0.5 percent of capital cost): search for a sourced fixed O&M share of transmission capital, in this order: ETED or CNE Dominican documents; a regional study (Central America or Caribbean, SIEPAC, CEPAL, IDB); an international transmission study (IEA, IRENA, NREL, World Bank, national regulators). Write the first share found as `=J232*<share>` with its source. If none states a share, write an ASSUMPTION with the median of the published shares you downloaded (at least two documents, cited) and the range; if fewer than two exist, keep 0.5 percent under an ASSUMPTION citing what you downloaded. Leave J253 and J252 as they are (F11) and list them in GAPS.

D8. Guatemala hydro: find by values why policy hydro is about 3 PJ above BAU from 2026 (F12): trace from Stage 3 limits back through the Stage 2 controller and overwrites, Stage 1, the Stage 0 denominators and the B1 inputs. Then make hydro output identical across the three scenarios from a sourced hydro path (AMM or MEM generation statistics for history, the hydro freeze rule after the last observed year), with the least change at the cause. Gate: Guatemala hydro by scenario within 0.05 PJ in every year.

D9. No separate fix; D2 covers the Ecuador run-of-river split.

D10. Costa Rica `E5INDCOA` stays as it is (F13).

D11. Read-only cross-sector check, Phase E.

D12 (hub 10, 20 November). Ecuador OperationalLife: every Ecuador technology with CapitalCost above 0 in any year (36 technologies of F3, including `PPHD` and `PRONGS`) gets a sourced operational life, by technology class, in this order: Ecuador national documents (Plan Maestro de Electricidad, ARCONEL, CELEC); the CCG Ecuador starter kit (Zenodo record 5498094, file and table cited) or its data article (doi 10.1016/j.dib.2022.108021); the PLANMICC public repository (github.com/PLANMICC/OSeMOSYS_Ecuador, permalink to the file and cell); NREL ATB or IRENA for the same class. Grid technologies (`ELE_TRANS`, `ELE_DIST`) take a published transmission and distribution asset life. Write each in the OperationalLife row of `Fixed Horizon Parameters` (add the row where it is missing). The other 77 Ecuador rows with a one-year life and no capital cost stay as they are and are listed in GAPS. Every CCG kit value not taken as published gets a row in `starter_kit_deviations.csv`.

## 5. Setup

- Windows, Git Bash, Anaconda Python as `py` for the pipeline, python.org Python for your own scripts with `py -I`. Microsoft Excel and pywin32 for A-O saves. `glpsol` 4.65 at `C:\glpk-4.65\w64`.
- Clone: reuse `/c/clw_fix` (it holds the branch and the earlier `downloads/`). Check: `git -C /c/clw_fix status --short` shows no tracked change, `git -C /c/clw_fix fetch origin`, `git -C /c/clw_fix rev-parse HEAD` and `origin/job/fix-run` both equal `4ba69d6cc3e6619bcc7ee6aee968ea0c78372b2f`, and `origin/main` is `c42ae07`. If any check fails: make a new clone `git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_fix2`, set origin to https://github.com/luviga/clewise-lac.git, fetch, `git checkout -b job/fix-run origin/job/fix-run`, copy `/c/clw_fix/_LAC_HUB/fix_run_20261111T200825Z/downloads/` into the new job folder's `downloads/earlier/` (read-only source), work in `/c/clw_fix2`, and record why.
- One UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder `_LAC_HUB/fix_run2_<stamp>/`. Copy this brief into it. Downloads in `downloads/` (gitignored). Copy every file in `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5/_LAC_HUB/leads_hub10/` into `downloads/leads/` (CLG documents: leads only; if the folder is missing, note it and continue).
- Earlier downloads: `_LAC_HUB/fix_run_20261111T200825Z/downloads/` in the clone and the archive `C:\Users\luisfernando\Desktop\OSeMOSYS\LAC_sources_archive\` (read-only) hold every source already cited; reuse them with their source ids and SHA-256; download again only what is missing.
- Free disk on C: recorded at the start; below 80 GB, delete solver output `.txt` files over 500 MB of a stage whose extraction has finished, and your own diagnostic solver outputs. Nothing else.
- Write only inside the clone you work in. Read-only: the main copy `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (its untracked `_LAC_HUB/BRIEF_*.md` files stay as they are), `LAC_sources_archive`, the earlier job folder `_LAC_HUB/fix_run_20261111T200825Z/`, every other `C:\clw_*` folder, anything under Dropbox `2_WORK` and OneDrive.
- Record the number of `EXCEL.EXE` processes before Phase A; never close one you did not start.
- Rules carried from the earlier runs: call batch files by full path (`NoDefaultCurrentDirectoryInExePath=1`); no `glpsol.bat` wrapper on PATH during stage runs; absolute log paths in solve wrappers; Guatemala A2 through `_LAC_HUB/cost_write_run_20261111T071733Z/scripts/run_with_append_shim.py`; Costa Rica B1 with a temporary `A2_Output_Params/LTSOPT` (copy of LTSNEW) and empty `B1_Output_Params/LTSOPT`, removed afterwards; the A2 driver restores `A1_Outputs` with `git checkout`, so stage every workbook change before a recompile; Costa Rica and Honduras B1 multiply only Write rows by the Security_Multiplier, the other four multiply Write and Overwrite rows; B1 writes every year of an Exact row; run `test_ao_cost_repair_manager` through `unittest discover` and `test_ao_safe_save.py` with its own runner.

## 6. Work

### Phase A. Sources and proposals (no model file changes)

A0. Documentation source map. Read the Read the Docs sites https://endrch-hon.readthedocs.io (Honduras), https://jam-lts.readthedocs.io (Jamaica), https://lts-rd.readthedocs.io (Dominican Republic), each with its input data and references pages, and the matching country model repositories of the Climate-Lead-Group GitHub organisation (list them with https://api.github.com/orgs/Climate-Lead-Group/repos). Read the reference lists of the two leads in `downloads/leads/` too (the P3 report cites, among others, ARCONEL 2022 statistics at https://anda.inec.gob.ec/anda/index.php/catalog/ARCERNNR and MEM Balance Energetico Nacional 2023). Write `source_map.csv`: country, documentation page URL (lead), parameter or technology it documents, the external document it cites (title, publisher, year, URL or DOI), downloaded (yes or no, file, SHA-256), page or table, value printed, matching model row (workbook, sheet, row) if any, current model value. Use the map first when sourcing D2, D3, D7b and D12. Values from the map enter the model only through the decided items of section 4; for every other row it is a list for the next decision.

A1. For D-ECU1, D-ECU2, D1, D2, D3, D5, D6, D7b, D8 and D12: download and open each source, record page or table. Write `sources.csv` (id, URL, title, publisher, date, accessed, SHA-256, file, page or table) continuing the earlier ids where a source is reused, and `proposals.csv` (country, workbook, sheet, row, column or year, Tech, Parameter, scenario, current value, new value, decision id, source ids, derivation, ASSUMPTION sentence where used). Unreachable URLs go to `sources_pending.csv` with every URL tried and the error.

A2. D2 analysis before any write: for each country, list by values every NDCNEW and LTSNEW B1 input whose 2018 to 2024 values differ from BAU (config rows of every sheet, transport sheets included), every history lower limit above reachable output (D2b), and every 2021 to 2024 build (F4) with its cause. Write `history_plan.csv` (country, sheet, row, scenario, what differs, proposed change, why least change). Write `history_builds.csv` (D2c) with the sourced commissioning.

A3. D8 analysis: write `gua_hydro_trace.md` with the values at each step from Stage 3 back to the cause, and the proposed change.

A4. Update `starter_kit_deviations.csv` (copy the earlier rows, add D12 and any CCG value D2 changes).

A5. Gate A: every non-ASSUMPTION row of `proposals.csv` has source ids that exist in `sources.csv` with URL, locator, date, file present and SHA-256; no source field holds a local path or an internal file; every ASSUMPTION sentence passes a scan for the forbidden words of section 2. Commit "Phase A: sources and proposals for the hub 9 decisions" and push.

### Phase B. Writes

B1. Back up every workbook and CSV you will change into `backups/` with a SHA-256 manifest.

B2. Write all A-O, `A-O_Demand.xlsx`, `B1_Scenario_Config.xlsx` and Stage 2 overwrite changes of `proposals.csv`. Switch Projection.Mode to "User defined" where values now vary by year. Rows you add go after the last row of their block in the same layout.

B3. Gates (write `write_check.csv`): every written cell equals `proposals.csv` (relative 1e-9); a cell-by-cell comparison of every changed workbook against `4ba69d6` shows changes only at listed cells and at formula cells that depend on them (list those in advance from the formulas); no formula without a stored value; every other A-O workbook byte-identical; the Stage 2 CSV changed only on listed lines. Commit "Phase B: hub 9 decisions written" and push.

### Phase C. Recompile and base solves

C1. Run A2, then B1, per country with the commands of `pipeline_commands.csv`, one country at a time, starting with Ecuador. After each country, check its B1 solves. If a solve is infeasible: find the cause by values and test solves; repair it only inside the decided items (D7a band back to 0.98; a D2 history change that conflicts with a post-2024 cap is fixed at its cause with a source, as D2 says); record each repair in GAPS with the values. Never relax a limit that a decision did not touch.

C2. Gate: keyed comparison of A2 outputs, B1 outputs and B1 data files against `4ba69d6`. Allowed differences: the cells of `proposals.csv` and what follows from them; Ecuador `EXTT_CRU`, `DIST_CRU`, `PROCRU`, `REF_*`, `E5EXPCRU`, `PPHD` and OperationalLife rows; history values 2018 to 2024 of NDCNEW and LTSNEW; capacity factors and residual capacities changed under D2 in every year; emission factors changed under D3 in history years; DR and Jamaica band rows (D7a); Honduras `PPBGS`; Guatemala `DIST_FLEXFUEL` and the D8 rows; Dominican Republic `ELE_TRANS` FixedCost. Any other difference: find its cause, fix it if it comes from your write, otherwise record it. 19 B1 solves OPTIMAL. Write `recompile_diff_summary.csv`. Commit "Phase C: A2 and B1 recompiled" and push.

### Phase D. Stages 0 to 3

D1. Run Stages 0, 1, 2 and 3 with every test, as in `PIPELINE_WORKFLOW.md`. A failing soft test does not stop the pipeline. An infeasible solve is handled as in D7a or C1, with at most one full re-run of Stages 0 to 3.

D2. Gates by values, written to `fix_checks.csv` (detail in `fix_checks_detail.csv`):
- History: power-plant activity per technology identical in BAU, NDCNEW and LTSNEW for every year through 2024, every country (0.05 PJ); total final demand per fuel through 2024 identical (0.05 PJ); Stage 2 T11a reports 0 years.
- History builds: every power-plant new capacity in 2021 to 2024 matches `history_builds.csv` (D2c tolerance); `PPHD` new capacity 0 in every year.
- Ecuador crude: extraction plus imports minus (`PROCRU` input plus exports) at most 0.5 PJ in every year and scenario; `REF_*` total crude use against T(y) per year; imports per year (report; flag above 1 percent of production); values for 2021, 2024, 2025, 2026, 2030, 2031, 2035, 2040, 2050.
- Jamaica: `PPHROR` new capacity over the horizon at most 34.4 MW (34.3 MW plus the 0.1 MW grid of A2) in every scenario, none in 2024 to 2026; hydro output identical across scenarios (0.05 PJ).
- Guatemala: hydro output identical across scenarios (0.05 PJ) in every year.
- Ecuador `ELE_TRANS` and `ELE_DIST` new capacity per year and its undiscounted capital, before and after.
- Hydro output by country and scenario for 2026, 2030, 2040 and 2050.
- D7a: list of rows at 0.999 and rows put back to 0.98, with the solve that failed.

D3. `results_compare.csv` against `4ba69d6` as in the earlier run (status, objective, RE share 2030, 2035, 2050 against target, share validation, new capacity by power technology, emissions 2030 and 2050), plus the five largest new-capacity changes per country and the objective change per country explained by its three largest cost terms where you can compute them.

D4. Commit stage outputs and the job folder: "Phase D: base re-runs, Stages 0 to 3" and push.

### Phase E. Cross-sector check (read-only; runs even if an earlier phase stopped)

E1. For each country and each sector model of F15: folder, scenario names, years, whether its last tracked outputs exist, and whether it solves now (copy it to a scratch folder outside the clone, run its own runner, record status and time; never write in the clone).
E2. Scenario names and years against the energy model's BAU, NDCNEW and LTSNEW: aligned, mapped (for example Guatemala NDC to NDCNEW), or missing.
E3. Links by values: ethanol (energy demand or supply of ethanol against AFOLU sugarcane or land rows), waste methane and power (WASTE methane against energy biogas plants), biomass (AFOLU wood or residues against energy firewood and biomass rows). For each, the rows on both sides and whether the quantities agree in 2021 to 2024.
E4. Costs: per sector model, which cost parameters carry non-zero values.
Write `cross_sector_check.csv` and a short `cross_sector_check.md`. Change nothing.

### Phase F. Outputs and pull request

F1. `git diff --name-only 4ba69d6` shows only the changed workbooks and configs, the Stage 2 CSVs you changed, A2 and B1 outputs of the six energy models, the four stage output folders and the new job folder.
F2. No committed file over 50 MB; no `*.safesave_tmp*` file; `EXCEL.EXE` count as at the start; `git -c core.whitespace=cr-at-eol diff --check 4ba69d6` clean; no em dash in any file you wrote; no `Co-Authored-By` or "Generated with" line in `git log origin/main..HEAD`.
F3. Push to `job/fix-run` so draft PR #11 updates. Add a section "LAC_FIX_RUN2" to the PR #11 description, taken from your CHANGES file, with `gh pr edit 11` if `gh` is available; otherwise record that in GAPS. PR #11 stays draft. A last commit only to write hashes into REPORT is allowed.

## 7. Outputs

All in the job folder, plain English, no em dashes, one UTC stamp.

`REPORT_LAC_FIX_RUN2_<stamp>.md`: first, anything failed, blocked or pending; branch, base `4ba69d6` and commit hashes; per decision (D-ECU1, D-ECU2, D1 to D8, D12) what changed, with before and after values and sources; the D2 history plan and builds as applied; the Guatemala hydro cause; gate results with counts; the `fix_checks.csv` results; the results comparison table; tests and solve statuses; the cross-sector check summary.

`GAPS_LAC_FIX_RUN2_<stamp>.md`: every judgement call and its reason; every repair made at Phase C or D and why it stays inside a decision; "Known-limitation candidates" (include F11 J252 and J253, the 77 one-year Ecuador lives without capital cost, and anything new); undecided findings with values; anything left unchecked; `sources_pending.csv` summarised; incidents.

`CHANGES_LAC_FIX_RUN2_<stamp>.md`: file or folder by file, what changed and why, two or three lines each.

Also in the job folder: `PROGRESS.md`, `source_map.csv`, `sources.csv`, `proposals.csv`, `sources_pending.csv`, `history_plan.csv`, `history_builds.csv`, `gua_hydro_trace.md`, `starter_kit_deviations.csv`, `write_check.csv`, `recompile_diff_summary.csv`, `fix_checks.csv`, `fix_checks_detail.csv`, `results_compare.csv`, `cross_sector_check.csv`, `cross_sector_check.md`, scripts, test and stage logs.

Tracked files outside the job folder follow the repository's writing rules: no machine paths, no figures from model results, no hash values.
