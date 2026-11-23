# REPORT LAC_CLEANUP 20261123T031711Z

Pull request: luviga/clewise-lac#17 (draft), branch `job/cleanup`, five commits in the order of the brief. Clone `C:\clw_clean`, snapshots `C:\clw_clean_base`, temporary folder `C:\clw_clean_tmp`.

## Failed, blocked or pending

- **Decision for Luis (step 4.5).** Under the common Stage 3 rule, Guatemala NDC and LTS have no feasible solution. Relaxing one limit group at a time showed that only the orphan cap binds, so the exception stays for these two scenarios and for the orphan cap only, as the row `orphan_cap_exempt_scenarios` of `config/scenarios/rules/stage_controller.csv`. Guatemala BAU follows the common rule. Options are in GAPS.
- **Pending by design.** Jamaica PPBIM: 87 cases match the hole pattern with another cause (sourced overrides and the PJ freeze); left unchanged as a value decision (GAPS).
- **Soft tests that failed before the job and still fail:** Stage 2 T8 continuity (65 jumps) and T9 hydro PJ freeze (87, the Jamaica PPBIM cases); Stage 3 share match FAIL, which improves from 9 failures and 66 warnings to 8 and 64.
- Nothing is blocked. The pull request is a draft and is not merged.

## Baseline against main

The baseline run on the start commit compared with the files that main holds: 0 differences in 1,259 files, with 3 run-stamp cells or lines skipped (`baseline_against_main.csv` holds the header only). All 19 B1 solves (with Costa Rica LTSOPT), 18 Stage 0 solves and 18 Stage 3 solves were OPTIMAL, and the Stage 3 objectives equal F1.

## Steps and gates

| step | run time | gate | result |
|---|---:|---|---|
| 1 tests | | both unit test files pass three runs in a row; 0 Excel processes and 0 temp folders left | pass |
| 2 baseline | 4,750 s | against main | 0 differences in 1,259 files |
| 3 code fixes | 5,299 s | against baseline | 0 differences in 1,259 files, 36 data files and 36 objectives; F6 changes only the RE target lines of the Stage 3 results log |
| 4 Guatemala | 4,823 s | expected changes only | only Guatemala rows change (keyed results compare); Stage 2: 16 values in each of CURRENT_SHARES, CURRENT_LOWER and TARGET_SHARES (Guatemala BAU non-hydro renewables 2030 and 2031); Stage 3 inputs: 68 rows of Guatemala BAU, 10 each of NDC and LTS (zero-lower plants PPPVDS and PPPVTS 2025 to 2029 get upper 0 in place of 99999) |
| 5 deletions | 4,705 s | against step 4 | 0 differences in compiled inputs, 36 data files and 36 objectives; the one tree difference is the deleted `CONTROLLER_NEW_SCENARIOS_BEFORE.xlsx` |
| 6 labels | 4,641 s | against step 5 | 36 data files and 36 objectives equal; every tree difference is a label or note: the three TotalAnnualMinCapacity files (33 rows each, equal without the Scenario column), the three override CSVs (first five fields of every line equal) and the note cells of five override workbooks (cell counts equal the edit counts); `workbook_checks.csv` 13 of 13 PASS; old-label scan of the six energy models: 3 files with an old label before, 0 of 1,065 after |
| 7 pull request | | `git diff --check` with `core.whitespace=cr-at-eol` | clean after the step 1 test patch left the commit (its blank context lines were flagged; see GAPS) |

## Stage 3 objectives

All 18 OPTIMAL in every run. Stage 0 objectives are equal in every run.

| country | scenario | baseline | step3 | step4 | step5 | step6 |
|---|---|---:|---:|---:|---:|---:|
| CostaRica | BAU | 114537.2847 | 114537.2847 | 114537.2847 | 114537.2847 | 114537.2847 |
| CostaRica | NDC | 104231.3004 | 104231.3004 | 104231.3004 | 104231.3004 | 104231.3004 |
| CostaRica | LTS | 95511.03799 | 95511.03799 | 95511.03799 | 95511.03799 | 95511.03799 |
| DominicanRepublic | BAU | 411688.7579 | 411688.7579 | 411688.7579 | 411688.7579 | 411688.7579 |
| DominicanRepublic | NDC | 430947.4136 | 430947.4136 | 430947.4136 | 430947.4136 | 430947.4136 |
| DominicanRepublic | LTS | 455181.1777 | 455181.1777 | 455181.1777 | 455181.1777 | 455181.1777 |
| Ecuador | BAU | 268341.2784 | 268341.2784 | 268341.2784 | 268341.2784 | 268341.2784 |
| Ecuador | NDC | 257974.9215 | 257974.9215 | 257974.9215 | 257974.9215 | 257974.9215 |
| Ecuador | LTS | 250736.464 | 250736.464 | 250736.464 | 250736.464 | 250736.464 |
| Guatemala | BAU | 360931.9209 | 360931.9209 | 360932.3291 | 360932.3291 | 360932.3291 |
| Guatemala | NDC | 347968.8583 | 347968.8583 | 347968.8583 | 347968.8583 | 347968.8583 |
| Guatemala | LTS | 346140.4368 | 346140.4368 | 346140.4368 | 346140.4368 | 346140.4368 |
| Honduras | BAU | 104917.6359 | 104917.6359 | 104917.6359 | 104917.6359 | 104917.6359 |
| Honduras | NDC | 103142.1113 | 103142.1113 | 103142.1113 | 103142.1113 | 103142.1113 |
| Honduras | LTS | 100692.3388 | 100692.3388 | 100692.3388 | 100692.3388 | 100692.3388 |
| Jamaica | BAU | 65086.6886 | 65086.6886 | 65086.6886 | 65086.6886 | 65086.6886 |
| Jamaica | NDC | 61614.69871 | 61614.69871 | 61614.69871 | 61614.69871 | 61614.69871 |
| Jamaica | LTS | 59581.54338 | 59581.54338 | 59581.54338 | 59581.54338 | 59581.54338 |

### Changed objectives

| objective | before | after | cause |
|---|---:|---:|---|
| Guatemala BAU, Stage 3 | 360931.9209 | 360932.3291 | Stage 2 fix: solar and wind keep their share in 2030 and 2031, so their lower limits are no longer 0 (+0.408) |

Guatemala NDC and LTS keep their objectives. Their Stage 3 inputs change in the 10 zero-lower rows each, and a few hydro values move between solutions of equal cost (PPHDAM and PPHROR in 2025, 2029, 2044 and 2045).

## Guatemala generation, 2030 and 2031 (PJ)

Solar is the power plants with a solar token (PPPVD, PPPVDS, PPPVT, PPPVTS, PPPVT2), wind those with a wind token (PPWNDON); total is every power plant. Before is the baseline; after is step 4, equal in steps 5 and 6.

| scenario | year | solar before | solar after | wind before | wind after | total before | total after |
|---|---|---:|---:|---:|---:|---:|---:|
| BAU | 2030 | 0.9172 | 2.1435 | 0.0 | 0.928 | 59.9493 | 59.0455 |
| BAU | 2031 | 0.9172 | 2.7175 | 0.0 | 1.1717 | 62.4623 | 61.5627 |
| NDC | 2030 | 10.0826 | 10.0826 | 4.6683 | 4.6683 | 74.9816 | 74.9816 |
| NDC | 2031 | 13.536 | 13.536 | 6.2501 | 6.2501 | 80.4063 | 80.4063 |
| LTS | 2030 | 10.0544 | 10.0544 | 4.6551 | 4.6551 | 74.9109 | 74.9109 |
| LTS | 2031 | 14.8472 | 14.8472 | 6.8247 | 6.8247 | 83.189 | 83.189 |

In BAU the solar and wind gains come from the frozen non-hydro renewables, which now share the room with them: PPBIM 4.5277 to 2.5407 and PPGEO 2.2733 to 1.2757 in 2030. Total power plant generation falls by about 0.90 PJ in each year.

## Step 4.5 relaxation (Guatemala NDC and LTS, common rule)

| variant | NDC | LTS |
|---|---|---|
| common rule | no feasible solution | no feasible solution |
| orphan cap freed | OPTIMAL 347968.8583 | OPTIMAL 346140.4368 |
| zero-lower plants open | no feasible solution | no feasible solution |
| 1.05 band open | no feasible solution | no feasible solution |
| former exception (both) | OPTIMAL 347968.8583 | OPTIMAL 346140.4368 |

Freeing the orphan cap restores both scenarios at the baseline objective. The one orphan plant, PPPVT2, then produces 0.366 PJ over 2043 to 2050 in each scenario (0.004 to 0.072 PJ a year).

## stage2_holes.csv

97 cases of the pattern (Stage 2 share 0 where Stage 1 and every override are above 0):

- Guatemala BAU, 10 cases: PPPVD, PPPVDS, PPPVT, PPPVTS and PPWNDON in 2030 and 2031. All filled; for example PPPVT lower limit 0 to 1.39 PJ (2030) and 1.755 PJ (2031), PPWNDON 0 to 0.928 and 1.1717.
- Jamaica PPBIM 2027 to 2055, 29 cases in each scenario (87): another cause; unchanged.

## Deletions

36 entries removed with `git rm`: 2,448 files, 630,070,723 bytes (about 630 MB). 18 candidates kept because a script or configuration names them. Four `.gitignore` lines named files of the removed folder and went with it, together with the heading and blank line of the section that held only one of them.

## Tests

| test | baseline | step 3 | step 4 | step 5 | step 6 |
|---|---|---|---|---|---|
| unit tests (`test_ao_safe_save`, `test_ao_cost_repair_manager`) | fail (start-commit tests, file locks) | pass | pass | pass | pass |
| Stage 0 tests | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| Stage 1 tests | all pass | all pass | all pass | all pass | all pass |
| Stage 2 hard tests | 7/7 | 7/7 | 7/7 | 7/7 | 7/7 |
| Stage 2 soft T8, T9 | fail, fail | fail, fail | fail, fail | fail, fail | fail, fail |
| Stage 3 tests | 10/11 | 10/11 | 11/11 | 11/11 | 11/11 |
| Stage 3 T4 upper match | 7,958 of 7,998 | 7,958 of 7,998 | 7,998 of 7,998 | 7,998 of 7,998 | 7,998 of 7,998 |
| RE targets | 24 pass | 24 pass | 24 pass | 24 pass | 24 pass |
| Share match (failures, warnings) | 9, 66 | 9, 66 | 8, 64 | 8, 64 | 8, 64 |

Step 1 test runs outside the pipeline: both files pass three runs in a row with the fixed setup, and fail on the start commit with WinError 32.
