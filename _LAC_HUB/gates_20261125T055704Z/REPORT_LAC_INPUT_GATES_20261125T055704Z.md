# REPORT LAC_INPUT_GATES (stamp 20261125T055704Z)

Pull request: #20 (draft), branch `job/gates`, from `main` at #19. Nothing was solved in this job; `glpsol --check`
(translation and generation, no solve) was the only solver call.

## 1. Outcome

- A check suite `gates/` reads the exact GMPL data files the solver reads, with the defaults they declare, and
  reports by model, scenario, parameter, technology, fuel, emission, year and time slice. It runs at three points:
  `py -I gates --point b1|final|results` (see GAPS item 1 on the command form). 32 checks in five layers, each with a
  row in `config/gates/checks.csv`; every tolerance and threshold is a row of `config/gates/thresholds.csv`; the
  model list is `config/gates/models.csv` (24 models discovered from the tree).
- Every data file of every model and scenario was written by the model's own A2 compiler and B1 runner and
  translated by `glpsol --check`: 80 compiled data files at the `_0` point and 18 FINAL files, 0 translation errors.
- Two compiled folders were stale because their compilers never wrote them: RD_AFOLU `A2_Output_Params/BAU` and
  ECU_USCUSS `A2_Output_Params/NDC` and `NDCCON`. Both compilers were fixed, the models recompiled and the
  regenerated files committed (80 files).
- Replay: all 11 defects of the brief that main no longer carries were put back on copies and every one was flagged;
  the Honduras control case (vehicle shares as minimums only) was correctly not flagged.
- Run on main: the b1 point finds 3,581 FAIL and 7,493 WARN rows, the final point 104 FAIL and 1,714 WARN rows, the
  results point 156 WARN rows (rows are grouped by parameter and index over years). The final point finds no FAIL of
  layers S, B or P in the 18 energy scenarios that #19 solved; its FAILs are all R5.
- Run time of the suite over all models: b1 44.0 s, final 13.1 s, results 0.1 s (target 15 minutes).

## 2. Start check

`origin/main` tree equals the tree the brief names; the head is #19. The two unit-test files passed with the
temporary folder set to the job's temporary folder before any work (step 0) and again at the end.

## 3. Check catalogue

| id | class | proves |
|---|---|---|
| T0 | FAIL | `glpsol --check` translates the model with the data file (compile wrapper, check mode) |
| S0 | FAIL | at b1 the parsed data file holds exactly the runner's own tables `B1_Output_Params/<scenario>` |
| S1 | FAIL/WARN | every fuel with a demand is reachable from a technology mode without input fuel |
| S2 | FAIL/WARN | every input fuel has a producer (FAIL when the consumer has an activity lower limit and needs the fuel in every mode) |
| S3 | WARN | fuel produced but neither demanded, used nor tagged |
| S4 | FAIL/WARN | a forced technology whose whole input chain has largest activity 0 |
| S5 | FAIL | no duplicate key, repeated block, unknown element or undeclared parameter |
| S6 | FAIL/WARN | OperationalLife and CapacityToActivityUnit present; factors in [0, 1]; YearSplit and demand profiles sum to 1 |
| S7 | FAIL | every scenario the model configuration lists has its compiled folder and data file |
| B1 | FAIL | minimum capacity at most maximum capacity |
| B2 | FAIL | minimum investment at most maximum investment |
| B3 | FAIL | activity lower limit at most activity upper limit |
| B4 | FAIL | model period lower at most upper; sum of annual lower limits at most model period upper |
| B5 | FAIL | residual capacity at most maximum capacity |
| B6 | FAIL | residual capacity plus minimum investments within their life at most maximum capacity |
| B7 | FAIL | minimum capacity at most residual capacity plus maximum investments within their life |
| B8 | FAIL | activity lower limit at most what the reachable capacity allows (capacity factor, year split, availability, unit) |
| P1 | FAIL/WARN | after pushing limits along the chain both ways, a fuel's least requirement exceeds its most supply (year or time slice) |
| P2 | FAIL | the least emissions (a weak-duality bound along the chain) exceed `AnnualEmissionLimit` |
| P3 | FAIL | the largest tagged production cannot reach `REMinProductionTarget` of the least tagged-fuel production |
| P4 | FAIL | the largest tagged capacity cannot cover the reserve margin on the least tagged production rate |
| R1 | FAIL | a value a merged job registered (before to after) is still at its before value in the compiled file |
| R2 | FAIL | every EmissionsPenalty is 0 (no model is listed as an exception) |
| R3 | FAIL | rule outputs the pipeline reads, and `REMinProductionTarget`, lie in [0, 1] |
| R4 | FAIL/WARN | inputs up to the history cut-off identical across scenarios (WARN at b1 for the energy models, which `scenario_rules.py` equalises later) |
| R5 | FAIL | every input that differs between BAU and a policy scenario has a row in the scenario difference register |
| R6 | FAIL | a published target loaded into Tech_Adoption is written only as a minimum |
| R7 | WARN | every limit value different from its default has an origin; `provenance.csv` |
| R8 | WARN | free unlimited source: no input fuel, no limit, zero capital and variable cost |
| X1 | WARN | year-to-year jump in energy emissions, generation or new capacity |
| X2 | FAIL | loaded renewable share and emission reduction targets met |
| X3 | WARN | solved history identical across scenarios |

A FAIL uses only bounds the model's constraints imply and counts only beyond the solver's feasibility tolerance
(GAPS item 3). Multi-mode technologies take the smallest ratio over the mode set for a requirement and the largest
for an availability.

## 4. Compile and translation per model and scenario

Compile: A2 and B1 of every model with the glpsol wrapper first on the path in check mode (`scripts/compile_check.py`;
the six energy models through LAC_ALIGN's `phaseC_run_c.py`). Stage 3: `scenario_rules.py`, `stage3_apply.py` on
the tracked Stage 2 controller and the tracked caps of `_STAGE3_RESULTS/EMISSION_CAPS.csv` written through
`scenario_rules.set_rows` (`scripts/stage3_build.py`); `stage3_apply.py` needed no Stage 0 output. Rows and seconds
are those of `glpsol --check` (`check_log.jsonl`). RD_AFOLU and ECU_USCUSS show their recompile after the fix.

| model | scenario | written | translation_0 | rows_0 | seconds_0 | final | translation_final | seconds_final |
|---|---|---|---|---|---|---|---|---|
| CR_AFOLU | BAU | yes | translated | 4197834 | 69.6 |  |  |  |
| CR_AFOLU | NDCincond | yes | translated | 4197834 | 60.6 |  |  |  |
| CR_AFOLU | NDCcond | yes | translated | 4197828 | 70.7 |  |  |  |
| CR_AFOLU | DCC | yes | translated | 4197828 | 70.4 |  |  |  |
| CR_ENERGY | BAU | yes | translated | 2825297 | 49.4 | yes | translated | 44.7 |
| CR_ENERGY | NDC | yes | translated | 2825317 | 49.9 | yes | translated | 48.4 |
| CR_ENERGY | LTS | yes | translated | 2825402 | 50.2 | yes | translated | 43.5 |
| CR_ENERGY | LTSOPT | yes | translated | 2825241 | 50.7 |  |  |  |
| CR_IPPU | BAU | yes | translated | 427298 | 7.4 |  |  |  |
| CR_IPPU | NDCincond | yes | translated | 427298 | 6.7 |  |  |  |
| CR_IPPU | NDCcond | yes | translated | 427298 | 7.4 |  |  |  |
| CR_IPPU | DCC | yes | translated | 427298 | 7.5 |  |  |  |
| CR_WASTE | BAU | yes | translated | 459381 | 6.6 |  |  |  |
| CR_WASTE | NDCincond | yes | translated | 459381 | 5.9 |  |  |  |
| CR_WASTE | NDCcond | yes | translated | 459433 | 6.5 |  |  |  |
| CR_WASTE | DCC | yes | translated | 459433 | 6.2 |  |  |  |
| RD_AFOLU | BAU | yes | translated | 11789033 | 271.3 |  |  |  |
| RD_AFOLU | NDCcond | yes | translated | 11789125 | 269.7 |  |  |  |
| RD_AFOLU | NDCincond | yes | translated | 11789125 | 223.1 |  |  |  |
| RD_ENERGY | BAU | yes | translated | 3631526 | 61.0 | yes | translated | 47.8 |
| RD_ENERGY | NDC | yes | translated | 3631734 | 61.1 | yes | translated | 50.5 |
| RD_ENERGY | LTS | yes | translated | 3631734 | 60.9 | yes | translated | 48.4 |
| RD_IPPU | BAU | yes | translated | 209746 | 3.0 |  |  |  |
| RD_IPPU | NDCincond | yes | translated | 209746 | 3.0 |  |  |  |
| RD_IPPU | NDCcond | yes | translated | 209746 | 3.0 |  |  |  |
| RD_WASTE | BAU | yes | translated | 398424 | 6.8 |  |  |  |
| RD_WASTE | NDCincond | yes | translated | 398369 | 6.8 |  |  |  |
| RD_WASTE | NDCcond | yes | translated | 398369 | 6.7 |  |  |  |
| ECU_AGR | BAU | yes | translated | 2731881 | 63.5 |  |  |  |
| ECU_AGR | NDC | yes | translated | 2731881 | 63.7 |  |  |  |
| ECU_AGR | LTS | yes | translated | 2731881 | 64.2 |  |  |  |
| ECU_Energy | BAU | yes | translated | 3106397 | 51.5 | yes | translated | 45.8 |
| ECU_Energy | NDC | yes | translated | 3106422 | 52.1 | yes | translated | 52.8 |
| ECU_Energy | LTS | yes | translated | 3106422 | 52.3 | yes | translated | 66.3 |
| ECU_IPPU | BAU | yes | translated | 340892 | 5.7 |  |  |  |
| ECU_IPPU | NDCincond | yes | translated | 340892 | 5.9 |  |  |  |
| ECU_IPPU | NDCcond | yes | translated | 340892 | 6.2 |  |  |  |
| ECU_USCUSS | BAU | yes | translated | 7663672 | 228.4 |  |  |  |
| ECU_USCUSS | NDCINC | yes | translated | 7663702 | 229.0 |  |  |  |
| ECU_USCUSS | NDCCON | yes | translated | 7663702 | 230.1 |  |  |  |
| ECU_USCUSS | NDC | yes | translated | 7663702 | 148.6 |  |  |  |
| ECU_WASTE | BAU | yes | translated | 164093 | 1.8 |  |  |  |
| ECU_WASTE | NDCincond | yes | translated | 164092 | 1.9 |  |  |  |
| ECU_WASTE | NDCcond | yes | translated | 164113 | 1.9 |  |  |  |
| GUA_ENERGY | BAU | yes | translated | 2333377 | 37.3 | yes | translated | 57.9 |
| GUA_ENERGY | NDC | yes | translated | 2333418 | 37.4 | yes | translated | 46.2 |
| GUA_ENERGY | LTS | yes | translated | 2333483 | 37.8 | yes | translated | 41.2 |
| GUA_IPPU | BAU | yes | translated | 236447 | 3.1 |  |  |  |
| GUA_IPPU | NDP | yes | translated | 236447 | 2.4 |  |  |  |
| GUA_IPPU | NDPhigh | yes | translated | 236399 | 3.2 |  |  |  |
| GUA_IPPU | NDPlow | yes | translated | 236447 | 3.1 |  |  |  |
| GUA_WASTE | BAU | yes | translated | 300497 | 4.9 |  |  |  |
| GUA_WASTE | NDP | yes | translated | 300696 | 3.5 |  |  |  |
| GUA_WASTE | NDPhigh | yes | translated | 300693 | 4.9 |  |  |  |
| GUA_WASTE | NDPlow | yes | translated | 300697 | 5.2 |  |  |  |
| HON_AFOLU | BAU | yes | translated | 7825395 | 215.2 |  |  |  |
| HON_AFOLU | NDP | yes | translated | 7825483 | 213.8 |  |  |  |
| HON_AFOLU | NDC | yes | translated | 7825483 | 214.8 |  |  |  |
| HON_ENERGY | BAU | yes | translated | 2986376 | 59.4 | yes | translated | 54.3 |
| HON_ENERGY | NDC | yes | translated | 2986764 | 59.4 | yes | translated | 65.2 |
| HON_ENERGY | LTS | yes | translated | 2986757 | 59.2 | yes | translated | 60.0 |
| HON_IPPU | BAU | yes | translated | 182327 | 2.9 |  |  |  |
| HON_IPPU | NDCincond | yes | translated | 182327 | 2.8 |  |  |  |
| HON_IPPU | NDCcond | yes | translated | 182327 | 2.9 |  |  |  |
| HON_WASTE | BAU | yes | translated | 270468 | 4.3 |  |  |  |
| HON_WASTE | NDCincond | yes | translated | 270468 | 4.6 |  |  |  |
| HON_WASTE | NDCcond | yes | translated | 270468 | 4.4 |  |  |  |
| JAM_AFOLU | BAU | yes | translated | 1680631 | 25.4 |  |  |  |
| JAM_AFOLU | LTS | yes | translated | 1680631 | 25.2 |  |  |  |
| JAM_AFOLU | NDC | yes | translated | 1680631 | 23.2 |  |  |  |
| JAM_ENERGY | BAU | yes | translated | 4859687 | 115.4 | yes | translated | 97.5 |
| JAM_ENERGY | NDC | yes | translated | 4859710 | 115.0 | yes | translated | 94.8 |
| JAM_ENERGY | LTS | yes | translated | 4859710 | 115.2 | yes | translated | 71.7 |
| JAM_TRANSPORT | BAU | yes | translated | 1366575 | 23.7 |  |  |  |
| JAM_TRANSPORT | NDP | yes | translated | 1366501 | 17.1 |  |  |  |
| JAM_TRANSPORT | NDC | yes | translated | 1366713 | 17.1 |  |  |  |
| JAM_TRANSPORT | LTS | yes | translated | 1366689 | 22.7 |  |  |  |
| JAM_TRANSPORT | LTSOPT | yes | translated | 1366689 | 23.2 |  |  |  |
| JAM_WASTE | BAU | yes | translated | 207743 | 2.0 |  |  |  |
| JAM_WASTE | LTS | yes | translated | 207917 | 2.0 |  |  |  |

Translations logged: 105; T0 failures: 0

## 5. Stale compiled files

`stale_compare.csv` compares every regenerated file with its tracked copy keyed by all index columns (the scenario
label compared on its own); `stale_compiled.csv` lists the 99 stale files, `stale_nondeterminism.csv` the 37 files
that differed only in row order (restored, not committed).

| model | folder | files | cells | example | cause |
|---|---|---|---|---|---|
| RD_AFOLU | A2_Output_Params/BAU and B1_Output_Params/BAU | 6 + 6 | 925 per folder (231 EmissionsPenalty to 0, 396 VariableCost, 165 CapitalCost, 99 FixedCost, 33 rows of EmissionActivityRatio added, 1 ResidualCapacity) | VariableCost IMPRIC 2030 1,445.56 to 743.63; IMPCARBOV 3,810.56 to 10,995.21; EmissionsPenalty Health 2025 1000 to 0 | `A2_Compiler.py` wrote LTS, LTSNZ, NDCincond and NDCcond and never BAU. Fixed: the base tables are written as in JAM_AFOLU's compiler (same code base). |
| ECU_USCUSS | A2_Output_Params/NDC and NDCCON | 19 + 19 | 30 EmissionsPenalty and 30 OutputActivityRatio rows per folder; the other 17 files carry the scenario label only | EmissionsPenalty EXT_REGAIR -3.38 to 0; a non-motorised transport output row (TRANE6NOMOT) added | `A2_Compiler.py` wrote BAU and the single `Other_Scenarios` name (NDCINC). Fixed: every policy scenario the B1 configuration activates is written. |
| ECU_USCUSS | B1_Output_Params/NDC and NDCCON | 2 + 2 | 30 + 30 per folder | same | B1 reads the stale A2 folders |
| ECU_IPPU | A2_Output_Params/NDCcond and NDCincond | 13 + 13 | scenario label only (BAU to the folder's own name); every value identical | | the tracked tables predate the compiler, which writes the folder's own label |
| ECU_AGR | A2_Output_Params/NDCINC (new, untracked) | 19 | | | the compiler writes `Other_Scenarios` NDCINC, a scenario ECU_AGR does not have; not committed, removed; see GAPS |

After the regeneration, RD_AFOLU BAU holds the values #19 wrote (743.63, 10,995.21) and no non-zero penalty;
ECU_USCUSS has no non-zero penalty in any scenario. The other three tracked RD_AFOLU folders that no compile writes
(`B1_Output_Params/LTS` and `LTSNZ`, scenarios not activated) keep their old content; see GAPS.

## 6. Replay of the known defects

`replay_check.csv` (scripts `replay.py`, `replay_gua_distance.py`). Copies in the temporary folder; values from
LAC_ALIGN's registers.

| defect | put back | expected | flagged | first row |
|---|---|---|---|---|
| Dominican PPICEFOI BAU maximum capacity | TotalAnnualMaxCapacity 2023 0.583419 and 2024 0.472 in the compiled BAU file | B8, B5, P1 | yes | B5: residual 0.4956 above maximum 0.472 in 2024 (the 2023 lower limit 9.10 stays within 10.93 the capacity allows) |
| Ecuador maximum capacity 0.1 MW below residual plus committed builds | before values of `register_history_fix3.csv` | B6 | yes | B6 PPPVD 2021 0.0296 > 0.02955 |
| Ecuador NDC PPHDAMPS second maximum capacity row | the row written twice | S5 | yes | S5 key given twice |
| Costa Rica policy plant limits below history capacity | before values of `register_policy_history_cr.csv` (NDC) | B8 | yes | B8 PWRGEO 2026 5.524 > 5.468 |
| Dominican policy plant limits below history capacity | before values of `register_policy_history_dr1-4.csv` (LTS) | B8 | yes | B8 PPHDAM 2018 6.334 > 6.038 |
| Four vehicle distances (Guatemala NDC and LTS infeasible) | Guatemala heavy freight Ref.km.BY 50400 to 9000 in a copy of the model, recompiled (A2, B1 in check mode, Excel recalculation through `ao_safe_save`), rules and Stage 3 run there | P1, B8 | yes | B8 TRYTKDSL NDC FINAL 2025 lower 12.52 > 2.29 the heavy trucks can deliver |
| JAM_TRANSPORT scenarios sharing one input folder | NDC data file absent from a copy | S7 | yes | S7 no data file NDC_0 |
| Guatemala forced hydrogen with no supply | lower limits TRYTKHYD 0.0101, TRBPUHYD 0.0032, TRBPRHYD 0.0027 in 2040-2050 in the NDC FINAL file, vehicles' own limits open, supply chain under the hydrogen rule | S4 | yes | S4 TRBPRHYD 2040-2050, chain dead upstream of E4HYD_PRI |
| Ecuador capacity-based target share 1.35 | REMinProductionTarget 1.35 in 2032 in the NDC FINAL file and a RENEWABLE_TARGETS.csv copy | R3 | yes | R3 2032 1.35 |
| Honduras LTS at r 0.47 with the vehicle ceilings | cap 2036-2050, straight line from the solved NDC 2035 level to 0.53 times the solved BAU 2050 level (results_summary.csv), through `scenario_rules.set_rows`, in the LTS FINAL file | P2 | yes | P2 CO2e_sources 2046 least 11.17 > limit 10.88 Mt (2046 to 2050) |
| Honduras LTS at r 0.47, vehicle shares as minimums only (control) | same cap; the maximum capacity rows that Min/Max writes for the nine electric classes opened from 2025 | P2 not flagged | not flagged | (none) |

The two Honduras runs separate the cause: with the ceilings, every way of meeting transport demand emits more than
the cap from 2046; with the shares as minimums only, the bound no longer proves infeasibility. P2 needed a stronger
bound than the brief's "least activity times smallest ratio" (GAPS item 6): emissions sit on fuel supply, the
ceilings act one level down, so the bound carries least embodied emissions along the chain (weak LP duality).

Defects still on main, proven by the run of section 7: RD_AFOLU B5 (TRAUTELE 2018-2027 residual 0.1322 above
maximum 0, TRMOTELE 2018-2025 0.2518 above 0, in all three scenarios); Honduras R6 (all nine electric classes in NDC
and LTS: 18 rows, with the maximum capacity rows they create); Costa Rica R6 (vehicle and rail classes in NDC and LTS:
18 rows); the cost cells R5 (table below); the stale RD_AFOLU and ECU_USCUSS folders (regenerated in this job, section 5; on the regenerated
files R2 finds no non-zero penalty in either model, and only ECU_AGR still carries one). Results checks on the tracked #19 results: X1
flags the 2036 drops (Dominican LTS 36,111.5 to 23,932.2 kt, minus 33.7 percent; Honduras LTS 12,630 to 10,009 kt),
X3 flags the solved history differences (Ecuador, Costa Rica, Dominican Republic).

Cost cells with BAU 0 and a policy value (`cost_cells.csv`, b1 point): CR_IPPU 202 per policy scenario, RD_IPPU 100,
ECU_IPPU 175 and 150, GUA_IPPU 100, 52 and 100, HON_IPPU 185, HON_WASTE 50, ECU_WASTE 50, HON_AFOLU 60 and 60,
RD_AFOLU 75 and 75. R5 flags every one of them. The counts differ slightly from the brief where it counted per
parameter (HON_AFOLU 30 and 30 per parameter, two parameters); GUA_ENERGY's 33 non-motorised capital cost cells are in
the difference register and pass.

## 7. Run on main

`gate_results.csv` (all rows), `gate_summary.csv` (counts by check, class, model and point), `provenance.csv`.

b1 point (80 data files of 24 models):

| check | class | rows | models |
|---|---|---|---|
| B5 | FAIL | 14 | CR_ENERGY 8 (NDC and LTS history: PWRGEO, PWRSPVTRN, PWRWNONS, PWRFOI residual above the policy maximum in 2021-2024); RD_AFOLU 6 |
| B8 | FAIL | 8 | CR_ENERGY 8 (NDC and LTS PWRSPVTRN history lower limit above its capacity) |
| R1 | FAIL | 16 | CR_ENERGY 4 (DiscountRate: the data file declares 0.05; the register wrote 0.0831 into `B1_Default_Param.xlsx`, which no runner passes on); ECU_Energy 6 (NDC and LTS PROCRU 2021-2024 emission factors still at their before values); RD_AFOLU 6 (NDCcond and NDCincond 2018 variable cost of AG_RIC, AG_COC, AG_CAF) |
| R2 | FAIL | 3 | ECU_AGR 3 (EXT_REGAIR penalty 1 in every scenario) |
| R4 | FAIL | 814 | 11 sector models (CR_AFOLU 187, RD_AFOLU 348, HON_AFOLU 164, ECU_AGR 59, ECU_WASTE 19, JAM_AFOLU 14, JAM_TRANSPORT 11, ECU_IPPU 6, ECU_USCUSS 3, RD_WASTE 2, JAM_WASTE 1) |
| R4 | WARN | 464 | the six energy models (equalised later by `scenario_rules.py`) |
| R5 | FAIL | 2,698 | all 18 sector models and CR_ENERGY (LTSOPT, not in the register) |
| R6 | FAIL | 42 | CR_ENERGY 18, HON_ENERGY 24 |
| S7 | FAIL | 4 | CR_ENERGY LTSOPT (no B1 folder); JAM_TRANSPORT NDP, NDC, LTSOPT (data files written, B1 folders missing) |
| P1 | WARN | 116 | CR_AFOLU (E5DEGDRY short by 8e-6, inside the solver tolerance) |
| R7 | WARN | 2,604 | 14 models (UNTRACED values) |
| R8 | WARN | 268 | 22 models |
| S2 | WARN | 3 | JAM_ENERGY TRXTRAIELE takes E4ELE_HEA, which nothing produces |
| S3 | WARN | 1,144 | 22 models |
| S6 | WARN | 2,894 | 12 models (OperationalLife or CapacityToActivityUnit only by default) |

final point (18 FINAL files of the six energy models):

| check | class | rows | models |
|---|---|---|---|
| R5 | FAIL | 104 | RD_ENERGY 59, CR_ENERGY 32, JAM_ENERGY 8, ECU_Energy 2, GUA_ENERGY 2, HON_ENERGY 1 (Stage 3 plant limits that differ from BAU from 2025 with no register row) |
| R7 | WARN | 747 | six models |
| R8 | WARN | 73 | five models |
| S2 | WARN | 3 | JAM_ENERGY |
| S3 | WARN | 381 | six models |
| S6 | WARN | 510 | five models |

results point (tracked #19 `results_summary.csv`): X1 WARN 129 (all six countries), X3 WARN 27 (Costa Rica 4,
Dominican Republic 13, Ecuador 10), X2 none.

First lines of each kind:

| point | check | class | model | scenario | parameter | item | year | values | message |
|---|---|---|---|---|---|---|---|---|---|
| b1 | B5 | FAIL | CR_ENERGY | NDC | ResidualCapacity | PWRGEO | 2021 | 0.2588 > 0.2562 | residual capacity above maximum capacity in 2021-2024 (4 years) |
| b1 | B5 | FAIL | CR_ENERGY | NDC | ResidualCapacity | PWRSPVTRN | 2021 | 0.0054 > 0.0053 | residual capacity above maximum capacity in 2021-2023 (3 years) |
| b1 | B8 | FAIL | CR_ENERGY | NDC | TotalTechnologyAnnualActivityLowerLimit | PWRSPVTRN | 2021 | 0.0328 > 0.0323718 | activity lower limit above the most activity the reachable capacity allows (capacity 0.0053 x CF.YearSplit 0.2 |
| b1 | B8 | FAIL | CR_ENERGY | NDC | TotalTechnologyAnnualActivityLowerLimit | PWRSPVTRN | 2022 | 0.0307 > 0.030657 | activity lower limit above the most activity the reachable capacity allows (capacity 0.0053 x CF.YearSplit 0.2 |
| b1 | P1 | WARN | CR_AFOLU | BAU |  | E5DEGDRY | 2022 | least 0.00170808 > most 0.0017 | least requirement of the fuel exceeds the most supply its producers can give in the year |
| b1 | P1 | WARN | CR_AFOLU | BAU |  | E5DEGDRY | 2023 | least 0.00170808 > most 0.0017 | least requirement of the fuel exceeds the most supply its producers can give in the year |
| b1 | R1 | FAIL | CR_ENERGY | BAU | DiscountRate |  | 2021 | compiled 0.05 = register before; register after 0.0831 | compiled file still holds the value the register replaced, in 2021-2050 (30 years) (align_20261124T021708Z/val |
| b1 | R1 | FAIL | CR_ENERGY | NDC | DiscountRate |  | 2021 | compiled 0.05 = register before; register after 0.0831 | compiled file still holds the value the register replaced, in 2021-2050 (30 years) (align_20261124T021708Z/val |
| b1 | R2 | FAIL | ECU_AGR | BAU | EmissionsPenalty | EXT_REGAIR | 2021 | 30 non-zero cells, first 1 | non-zero emission penalty in 2021-2050 (30 years) |
| b1 | R2 | FAIL | ECU_AGR | NDC | EmissionsPenalty | EXT_REGAIR | 2021 | 30 non-zero cells, first 1 | non-zero emission penalty in 2021-2050 (30 years) |
| b1 | R4 | FAIL | CR_AFOLU | NDCcond | EmissionActivityRatio | LNDAGR | 2018 | BAU 0.0002 vs NDCcond 0 [MODE_OF_OPERATION=1] | history input differs from BAU in 2018-2024 (7 years) |
| b1 | R4 | FAIL | CR_AFOLU | NDCcond | EmissionActivityRatio | LNDGAN | 2018 | BAU 0.0161 vs NDCcond 0 [MODE_OF_OPERATION=1] | history input differs from BAU in 2018-2024 (7 years) |
| b1 | R4 | WARN | CR_ENERGY | NDC | SpecifiedAnnualDemand | DEMTRNFREHEA | 2021 | BAU 19.5769 vs NDC 19.5769 | history input differs from BAU in 2021 (the pipeline equalises history later with the scenario_rules.py histor |
| b1 | R4 | WARN | CR_ENERGY | NDC | SpecifiedAnnualDemand | DEMTRNFRELIG | 2021 | BAU 7.84137 vs NDC 7.8414 | history input differs from BAU in 2021 (the pipeline equalises history later with the scenario_rules.py histor |
| b1 | R5 | FAIL | CR_AFOLU | NDCincond | EmissionActivityRatio | AGRRIC | 2026 | BAU 0.4202 vs NDCincond 0.4097 [MODE_OF_OPERATION=1] | input differs from BAU with no row in the scenario difference register (25 cells, 2026-2050 (25 years)) |
| b1 | R5 | FAIL | CR_AFOLU | NDCcond | EmissionActivityRatio | AGRCAF | 2029 | BAU 0.002 vs NDCcond 0.0019 [MODE_OF_OPERATION=1] | input differs from BAU with no row in the scenario difference register (22 cells, 2029-2050 (22 years)) |
| b1 | R6 | FAIL | CR_ENERGY | LTS | Tech_Adoption Restriction_Type | TRNBUSELE |  | Restriction_Type Min/Max | published target (CR-T012, CR-T015) is written with a maximum (B1_Scenario_Config.xlsx Tech_Adoption, row 154) |
| b1 | R6 | FAIL | CR_ENERGY | LTS | Tech_Adoption Restriction_Type | TRNFREHEAELE |  | Restriction_Type Min/Max | published target (CR-T027) is written with a maximum (B1_Scenario_Config.xlsx Tech_Adoption, row 164); the dat |
| b1 | R7 | WARN | CR_AFOLU | BAU | TotalTechnologyAnnualActivityUpperLimit | IMPCAR | 2018 | 0.0226 | UNTRACED: 31 cells in 2018-2050 (31 years) with no workbook, rule or register origin |
| b1 | R7 | WARN | CR_AFOLU | BAU | TotalTechnologyAnnualActivityUpperLimit | DEFANTWETPRI | 2033 | 0.2474 | UNTRACED: 14 cells in 2033-2050 (14 years) with no workbook, rule or register origin |
| b1 | R8 | WARN | CR_AFOLU | BAU |  | LNDRSC |  |  | technology without input fuel, without a limit on activity or capacity, and with zero capital and variable cos |
| b1 | R8 | WARN | CR_AFOLU | BAU |  | IMPWOD |  |  | technology without input fuel, without a limit on activity or capacity, and with zero capital and variable cos |
| b1 | S2 | WARN | JAM_ENERGY | BAU | InputActivityRatio | TRXTRAIELE | 2021 |  | input fuel has no producer in 2021-2055 (35 years); consumer not forced |
| b1 | S2 | WARN | JAM_ENERGY | NDC | InputActivityRatio | TRXTRAIELE | 2021 |  | input fuel has no producer in 2021-2055 (35 years); consumer not forced |
| b1 | S3 | WARN | CR_AFOLU | BAU | OutputActivityRatio | E3_PLM | 2018 |  | fuel produced but neither demanded, used nor tagged in 2018-2050 (33 years) |
| b1 | S3 | WARN | CR_AFOLU | BAU | OutputActivityRatio | E3_BAG | 2018 |  | fuel produced but neither demanded, used nor tagged in 2018-2050 (33 years) |
| b1 | S6 | WARN | CR_AFOLU | BAU | OperationalLife | T5DRYSECFORCOV |  | default 1 | no explicit value; the declared default applies |
| b1 | S6 | WARN | CR_AFOLU | BAU | CapacityToActivityUnit | T5DRYSECFORCOV |  | default 1 | no explicit value; the declared default applies |
| b1 | S7 | FAIL | CR_ENERGY | LTSOPT |  |  |  |  | scenario listed by the model configuration has no compiled folder B1_Output_Params/LTSOPT |
| b1 | S7 | FAIL | JAM_TRANSPORT | NDP |  |  |  |  | scenario listed by the model configuration has no compiled folder B1_Output_Params/NDP |
| final | R5 | FAIL | CR_ENERGY | NDC | TotalTechnologyAnnualActivityLowerLimit | PWRSPVTRN | 2025 | BAU 0.1077 vs NDC 0.1084 | input differs from BAU with no row in the scenario difference register (25 cells, 2025-2049 (25 years)) |
| final | R5 | FAIL | CR_ENERGY | NDC | TotalTechnologyAnnualActivityLowerLimit | PWRBMS | 2025 | BAU 0.2462 vs NDC 0.2479 | input differs from BAU with no row in the scenario difference register (25 cells, 2025-2049 (25 years)) |
| final | R7 | WARN | CR_ENERGY | BAU | TotalAnnualMaxCapacity | TRNMIC | 2021 | 0.1818 | UNTRACED: 30 cells in 2021-2050 (30 years) with no workbook, rule or register origin |
| final | R7 | WARN | CR_ENERGY | BAU | TotalAnnualMaxCapacity | TRNBUS | 2021 | 0.2622 | UNTRACED: 30 cells in 2021-2050 (30 years) with no workbook, rule or register origin |
| final | R8 | WARN | CR_ENERGY | BAU |  | PROFIR |  |  | technology without input fuel, without a limit on activity or capacity, and with zero capital and variable cos |
| final | R8 | WARN | CR_ENERGY | BAU |  | PROINDWAS |  |  | technology without input fuel, without a limit on activity or capacity, and with zero capital and variable cos |
| final | S2 | WARN | JAM_ENERGY | BAU | InputActivityRatio | TRXTRAIELE | 2021 |  | input fuel has no producer in 2021-2055 (35 years); consumer not forced |
| final | S2 | WARN | JAM_ENERGY | NDC | InputActivityRatio | TRXTRAIELE | 2021 |  | input fuel has no producer in 2021-2055 (35 years); consumer not forced |
| final | S3 | WARN | CR_ENERGY | BAU | OutputActivityRatio | E5AGRDSL | 2021 |  | fuel produced but neither demanded, used nor tagged in 2021-2050 (30 years) |
| final | S3 | WARN | CR_ENERGY | BAU | OutputActivityRatio | E5AGRELE | 2021 |  | fuel produced but neither demanded, used nor tagged in 2021-2050 (30 years) |
| final | S6 | WARN | RD_ENERGY | BAU | OperationalLife | T5DSLCOM |  | default 1 | no explicit value; the declared default applies |
| final | S6 | WARN | RD_ENERGY | BAU | OperationalLife | T5GSLCOM |  | default 1 | no explicit value; the declared default applies |
| results | X1 | WARN | CostaRica | BAU | gen_pj_oil products |  | 2023 | 2022 0.3302 -> 2023 2.4881 | generation of the group changes by more than the threshold in one year |
| results | X1 | WARN | CostaRica | BAU | energy_emissions_kt |  | 2024 | 2023 9177 -> 2024 10900.8 | energy emissions change by 18.8 percent in one year |
| results | X3 | WARN | CostaRica | LTS | energy_emissions_kt |  | 2023 | BAU 9177 vs LTS 9162.5 | solved history differs from BAU although history inputs are identical |
| results | X3 | WARN | CostaRica | LTS | energy_emissions_kt |  | 2024 | BAU 10900.8 vs LTS 10886.3 | solved history differs from BAU although history inputs are identical |

## 8. Share of limit values traced (R7)

| point | cells | A2 compiled table | workbook cell | register row | stage rule | UNTRACED | traced share |
|---|---|---|---|---|---|---|---|
| b1 | 237,818 | 118,136 | 51,730 | 588 | | 67,364 | 71.7 percent |
| final | 82,934 | 35,366 | 6,515 | 523 | 20,676 | 19,854 | 76.1 percent |

A workbook origin needs the value itself in a row of `B1_Scenario_Config.xlsx` that names the technology (the cell
is reported). Most UNTRACED values are computed by the B1 runners (adoption curves, interpolations) from workbook
parameters; they need a named rule or a register row before R7 can become a FAIL.

## 9. Run times

| step | seconds |
|---|---|
| A2 and B1 compile with translation, six energy models | 1,121 (CR 106, RD 117, ECU 106, GUA 504, HON 113, JAM 175) |
| A2 and B1 compile with translation, 18 other models | 2,919 (AFOLU models 288 to 608 each) |
| recompile after the fixes (RD_AFOLU, ECU_USCUSS) | 1,242 |
| `scenario_rules.py` | 0.8 |
| `stage3_apply.py` | 1.8 |
| cap write | 0.0 |
| translation of the 18 FINAL files | 1,039 |
| suite, b1 point, all models | 44.0 |
| suite, final point | 13.1 |
| suite, results point | 0.1 |
| `test_gates.py` | about 2 |

Summed `glpsol --check` time over the 105 translations: 6,633 s (the largest problem has 11.8 million rows).

## 10. What only a solve can reveal

The suite proves infeasibility only through bounds the constraints imply one at a time or pushed along one chain.
These interactions stay invisible to it:

- several technologies that can each take a demand, whose combined limits cannot (P1 tightens a producer only when
  all the others are at their largest; it does not solve the joint allocation);
- emission limits met only by a combination of substitutions on several branches at once beyond the embodied
  emission bound of P2 (the bound is the LP dual of one fuel balance per fuel with the producers' limits on one
  level; capacity limits further upstream are not in it);
- limits that link years: model period limits against investment paths and operational lives, and capacity built
  in one year needed in another;
- storage: shifting supply between time slices (P1 gives a WARN there);
- results-level problems (an OPTIMAL solve with jumps or unmet targets), which the results point checks after the
  solve.

When a solve fails with every check passing, `FEASIBILITY_PROTOCOL.md` prescribes bisection by blocks with
`bisect_blocks.py` and a new check for the interaction found.

## 11. Gates of this job

1. Tracked changes only in `gates/`, `config/gates/`, `test_gates.py`, `FEASIBILITY_PROTOCOL.md`,
   `PIPELINE_WORKFLOW.md`, the 80 stale compiled files with the two compiler fixes, and the job folder.
2. `test_gates.py` (33 tests), `test_ao_safe_save.py` and `test_ao_cost_repair_manager.py` pass; `git diff --check`
   is clean; no em dash in any file this job wrote.
3. Every data file of every model and scenario was translated by `glpsol --check` at the `_0` point (80) and the
   FINAL point (18).
4. No `OSeMOSYS_Model.txt`, workbook, `inputs/` or `config/scenarios/` file changed.
