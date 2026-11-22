# REPORT LAC_STRUCTURE_TABLES 20261122T042525Z

## Failed, blocked or pending

- Gate 2 of Phase C is met for every scenario field the pipeline matches (folder names, scenario columns, catalogue, code literals of the pipeline scripts, stage output file names), and not met for four kinds of text and label inside pipeline files: description text in the B1 configurations and two Costa Rica variant rows not run, Note and Rationale prose of the Stage 2 overrides, the Scenario label of `TotalAnnualMinCapacity` rows that come from the A1 workbooks (Dominican Republic, Guatemala), and the Costa Rica `Blend_Shares_0.pickle` that no run rewrote. All are listed in `names_left.csv` with a reason; GAPS 1.14 gives the judgement.
- Files in the scope folders that the pipeline neither runs nor reads (older script copies, backup and reference workbooks, plot configurations, the Costa Rica experiment manager keys) keep the older names (GAPS 1.12, 1.13); listed in `names_left.csv`.
- Unit tests `test_ao_cost_repair_manager` (2 errors of 4) and `test_ao_safe_save` (stops at its first test) fail on Windows file locks in the temporary folder in every run of this job, the baseline included (GAPS incidents). Stage 3 test T4 fails as on `main`.
- The pull request numbers below were added in a report-only commit on job/structure-rename (force push is not used). The final REPORT, GAPS and CHANGES are on that branch; pull request 1 holds the job folder as it was after Phase B.

## Pull requests and commits

| Pull request | Branch | Base | Commits |
|---|---|---|---|
| 14 (draft) "LAC_STRUCTURE_TABLES: values and names of the stage pipeline in external tables" | job/structure-tables | main | ff37de0 (one commit; it holds the job folder as it was after Phase B) |
| 15 (draft) "LAC_STRUCTURE_TABLES: scenarios renamed BAU, NDC, LTS" | job/structure-rename | job/structure-tables | f3df640 "retire older scenario names", b6f69a2 (rename with the outputs of the final run), then a report-only commit with the pull request numbers |

## Baseline against main

The baseline run on `b51f24b` (A2 and B1 of six countries, Stages 0 to 3, every test) reproduces what `main` tracks: 0 differences in 1,278 compared files (`baseline_against_main.csv`, header only); 3 run stamps skipped (Stage 0 log, two controller workbooks).

## Tables created

| Table | Rows or keys |
|---|---|
| `config/preparation/Config_country_codes.yaml` | 6 countries, 9 fields each |
| `config/scenarios/scenario_catalogue.csv` | 11 rows in pull request 1; 4 rows after the rename (BAU, NDC, LTS, LTSOPT) |
| `config/scenarios/rules/stage_controller.csv` | 66 |
| `config/scenarios/technology_types.csv` | 136 |
| `config/scenarios/fuel_types.csv` | 7 |
| `config/scenarios/emission_labels.csv` | 57 |
| `inputs/scenarios/scenario_values.csv` | 12 |
| `config/compilation/Config_MOMF_T1_A.yaml` | 1 general key, 5 country keys |
| `config/execution/Config_MOMF_T1_AB.yaml` | 7 general keys, 59 country keys |

Loader: `lac_tables.py`. Register of every moved value: `tables_register.csv` (1,777 rows).

## Rows moved

Of the 1,977 rows of F2 (`script_constants.csv` of LAC_NDC_VERIFY), 97 are in model files and stay. Of the 1,880 others, 1,601 moved to the tables and 279 were already accepted by that scan; 2 further rows (field count of the batch-file loop) were accepted with a reason. After Phase B the scan finds 281 yes-rows outside the model files, all accepted with a reason (`script_constants_accepted_job.csv`), 0 not accepted.

## Gates

Phase B:
1. f1 scan: 281 yes-rows outside the model files, 281 accepted with a reason, 0 not accepted; 97 model-file rows kept.
2. Recompile: A2 installed files, B1 output parameters and B1 data files of 18 scenario runs equal the baseline (part of the full run; 0 differences).
3. Stages 0 to 3: 18 of 18 OPTIMAL in Stage 0 and in Stage 3; objectives equal; stage outputs and `stage3_results.xlsx` equal (`phaseB_against_baseline.csv`: 0 differences in 1,278 files, 3 run stamps skipped); test results equal the baseline list.
4. Paths differing from `origin/main`: 25 code files, 9 tables, the loader, the job folder; 0 other paths, no workbook.
5. `git diff --check` (with `cr-at-eol` for the CRLF files): clean.

Phase C:
- C2: A2 installed files, B1 output parameters and B1 data files of BAU, NDCNEW and LTSNEW equal the baseline by key (`c2_against_baseline.csv`, 0 differences); 18 B1 solves OPTIMAL with equal objectives.
- C3: 3,030 workbook cells renamed, 1,681 rows of older scenarios deleted, 5 A-Xtra rows deleted, 7 CSV tables renamed in their scenario column; every workbook and table check PASS (`workbook_checks.csv`).
- C4 gate 1: with the mapping NDC to NDCNEW and LTS to LTSNEW, compiled values equal the baseline (`phaseC_compiled_against_baseline.csv`: 0 value differences, 19 label rows), the 18 objectives equal, stage outputs and `stage3_results.xlsx` equal (`phaseC_against_baseline.csv`: only Scenario labels of the A2 files, the retired Ecuador NDCINC folder, and older names inside Stage 2 note prose that the mapping turns into old names).
- C4 gate 2: see the first section; `names_left.csv` lists every name left with class and count (36 rows in pipeline files, 55 in other files of the scope, 3 other-tool keys, 4,615 outside the scope).
- C4 gate 3: test results equal the baseline list; `stage1_test_v16.py`, `stage2_test_v2.py`, `stage3_test.py` and `stage2_demand_verify.py` read their scenario names from the catalogue.
- C4 gate 4: `git diff --check` (with `cr-at-eol`): clean.

## Objectives

Stage 3 (FINAL) objective of each model, in the model's cost unit; names after the rename (NDC was NDCNEW, LTS was LTSNEW). All 18 OPTIMAL in every run; Stage 0 objectives are equal across the three runs as well.

| Country | Scenario | Baseline | After Phase B | After Phase C |
|---|---|---|---|---|
| Costa Rica | BAU | 114537.2847 | 114537.2847 | 114537.2847 |
| Costa Rica | NDC | 104231.3004 | 104231.3004 | 104231.3004 |
| Costa Rica | LTS | 95511.03799 | 95511.03799 | 95511.03799 |
| Dominican Republic | BAU | 411688.7579 | 411688.7579 | 411688.7579 |
| Dominican Republic | NDC | 430947.4136 | 430947.4136 | 430947.4136 |
| Dominican Republic | LTS | 455181.1777 | 455181.1777 | 455181.1777 |
| Ecuador | BAU | 268341.2784 | 268341.2784 | 268341.2784 |
| Ecuador | NDC | 257974.9215 | 257974.9215 | 257974.9215 |
| Ecuador | LTS | 250736.464 | 250736.464 | 250736.464 |
| Guatemala | BAU | 360931.9209 | 360931.9209 | 360931.9209 |
| Guatemala | NDC | 347968.8583 | 347968.8583 | 347968.8583 |
| Guatemala | LTS | 346140.4368 | 346140.4368 | 346140.4368 |
| Honduras | BAU | 104917.6359 | 104917.6359 | 104917.6359 |
| Honduras | NDC | 103142.1113 | 103142.1113 | 103142.1113 |
| Honduras | LTS | 100692.3388 | 100692.3388 | 100692.3388 |
| Jamaica | BAU | 65086.6886 | 65086.6886 | 65086.6886 |
| Jamaica | NDC | 61614.69871 | 61614.69871 | 61614.69871 |
| Jamaica | LTS | 59581.54338 | 59581.54338 | 59581.54338 |

## Tests

Run in every full run (baseline, Phase B, Phase C), with the same result each time:
- `stage0_test.py`: 10 of 10 pass.
- `stage1_test_v16.py`: 13 of 13 pass.
- `stage2_test_v2.py`: hard tests 7 of 7 pass.
- `stage3_test.py`: 10 of 11 pass; T4 fails, as on `main`.
- `test_ao_cost_repair_manager.py` (unittest discover): 4 run, 2 errors (file locks in the temporary folder).
- `test_ao_safe_save.py` (own runner): stops at its first test (file lock in the temporary folder).

## Run times

| Run | Content | Seconds |
|---|---|---|
| baseline | A2 and B1 of six countries, Stages 0 to 3, tests | 6,107 |
| phaseB | same | 4,367 |
| c2 | A2 and B1 of six countries | 1,366 |
| phaseC | A2 and B1 of six countries, Stages 0 to 3, tests | 4,126 |
