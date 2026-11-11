# REPORT LAC_OVERNIGHT_COST_RUN 20261111T071733Z

Pull request: luviga/clewise-lac#10 (draft), branch `job/cost-write-run`. Base: `origin/main` at `4124868`. Commits: Phase A `c6bb119`, Phase B `059f095`, Phase C `8151460`, Phase D `5673714`, Phase E `4c4d9a1`, Phase F (this report) in the commit that adds it.

## Failed, flagged or unverified, first

No country is unverified: every A2 and B1 reproduction matched the tracked files or differed only in explained places. Items that failed or need attention:

1. **C4(2) fails on a strict reading.** Besides the 13,020 manifest cells, 87 Projection.Mode cells and D9's M25, six cells changed: five formula cells that reference written cells and recalculated (Guatemala Primary Techs I284:J284, DIST_FLEXFUEL VariableCost 2018 and 2019 = DIST_GSL x 1.8; Honduras Secondary Techs I27:K27, PPBGS CapitalCost 2018 to 2020 = PPBIM x 5053/5391) and one formula whose text Excel normalised (DR Secondary Techs J232, same value). Not fixed: the formulas belong to rows the proposals do not cover.
2. **D2 gate: 324 differences outside the allowed list**, all from those two formula chains (Guatemala DIST_FLEXFUEL VariableCost, whose whole 2018 to 2050 path grows from the two formula cells, about 2 percent lower; Honduras PPBGS CapitalCost 2018 to 2020, 5,053 to 1,813.8 USD/kW), in A2, B1 and the data files of all three scenarios. Cause found, not fixed (GAPS section 2).
3. **D9 does not reach B1 or the solves.** Costa Rica `B1_Scenario_Config.xlsx`, sheet Efficiency, sets E5INDCOA demand by "Exact" values with 2021 = 0.675 in every scenario. The workbook and A2 hold 0.00667; B1 writes 0.675. Editing the config is outside the brief.
4. **`git diff --check` is not clean by the plain command**: it reports the CR at the end of every changed line of the A2, B1 and Stage 0 CSV files, which are CRLF like the tracked files they replace. `git -c core.whitespace=cr-at-eol diff --check origin/main` is clean, and the plain check is clean on every other file.
5. **Pipeline tests**: Stage 2 soft tests T8, T9 and T11a fail (hard tests 7 of 7 pass); Stage 3 test T4 fails on 40 Guatemala cells, the documented effect of `--skip-orphan-cap Guatemala`. Stage 0 (10 of 10) and Stage 1 (13 of 13) pass.
6. **Gate A4 command**: the literal `py -I -m unittest test_ao_cost_repair_manager -v` cannot import the module under `-I`; the same four tests pass through `unittest discover`.
7. **Stage 0 needed three attempts** (the batch file was first not found under this session's `NoDefaultCurrentDirectoryInExePath=1`, then ended after one solve because of my `glpsol.bat` wrapper); the third ran all 18 solves. Logs of both failed attempts are kept.
8. **Ecuador's objective rises about eighteen-fold**: its fuel, extraction and import costs were placeholders of 1 USD/GJ and are now sourced prices. Not tuned (GAPS section 2).

## Phase A. Safe-save write order (07:19 to 07:20 UTC)

`save_ao_safely` now writes `<stem>.safesave_tmp<suffix>` next to the target, recalculates it in Excel, runs the blank-formula guard on it and only then replaces the target (`os.replace`); on any error the temporary copy is deleted and the target is left untouched. Three tests added.

| Gate | Result |
|---|---|
| `py -I test_ao_safe_save.py` | 5 of 5 PASS (`test_ao_safe_save.log`) |
| `test_ao_cost_repair_manager` | 4 of 4 OK through `unittest discover`; the literal `py -I -m unittest test_ao_cost_repair_manager -v` cannot import the module under `-I` (both logs kept) |
| three writers unchanged, one `save_ao_safely(` call each | yes (SHA-256 equal to the base commit; 1, 1, 1) |
| `.gitignore` | `*.safesave_tmp.xlsx` and `/_LAC_HUB/**/backups/` added |

## Phase B. Reproduce before changing (07:21 to 08:25 UTC)

Every country reproduces; no country is unverified. Differences from the tracked files are all explained (`baseline_A2_diff.csv`, `baseline_B1_diff.csv`).

| Country | A2 compiler | A2 differing values (BAU / NDCNEW / LTSNEW) | B1 differing values vs tracked (BAU / NDCNEW / LTSNEW) | B1 data files vs main copy | Explanation |
|---|---|---|---|---|---|
| Costa Rica | A2_Compiler_CostaRica.py, NDCNEW and LTSNEW from BAU | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | exact (B1 needs a temporary LTSOPT input) |
| Dominican Republic | A2_Compiler_DominicanRepublic.py, from NDCcond | 393 / 393 / 393 | 444 / 587 / 579 | 444 / 587 / 579 | workbook transport edit after the tracked compile (efficient bus input electricity, not diesel) |
| Ecuador | A2_Compiler_Ecuador.py, from BAU | 0 / 1229 / 1229 | 0 / 464 / 464 | 0 / 435 / 435 | tracked NDCNEW and LTSNEW predate the 13 and 14 May hydro patch |
| Guatemala | A2_Compiler_Guatemala.py through the pandas shim, from NDP | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | exact |
| Honduras | A2_Compiler_Honduras.py, from NDP | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | exact |
| Jamaica | A2_Compiler_Jamaica.py, LTSNEW written by the compiler, NDCNEW copied from it | 764 / 764 / 764 | 904 / 3308 / 25 | 23 / 25 / 25 (27 January files) | 764 blanks restored on 9 November; tracked B1 NDCNEW is a BAU copy labelled LTS; 12 May planned-capacity edits |

Canonical commands (`pipeline_commands.csv`, run from the model folder with Anaconda Python 3.12.4, pandas 2.2.2):

- A2: `python A2_Compiler_<Country>.py` (Guatemala: `python run_with_append_shim.py A2_Compiler_Guatemala.py`), then copy the files the compiler wrote to the source folder over `A2_Output_Params/NDCNEW` and `LTSNEW` (Costa Rica BAU, DR NDCcond, Ecuador BAU, Guatemala NDP, Honduras NDP, Jamaica LTSNEW), then restore the A2 side files. Driver: `scripts/a2_driver.py`.
- B1: `python B1_Base_Scenarios_Adj_Parallel_<Country>.py` (Ecuador: `B1_Base_Scenarios_Adj_Parallel.py`), with an empty `Executables/` and glpsol 4.65 on PATH; Costa Rica also needs a temporary LTSOPT input. Driver: `scripts/b1_driver.py`.

All 19 B1 solves of Phase B were OPTIMAL (four for Costa Rica including the temporary LTSOPT).

## Phase C. Write the costs (08:29 to 08:43 UTC)

Cells written by country and rule (`write_set.csv`, `write_set_counts.csv`):

| Country | proposals_all | regional | D2 | D3 converted | D4 | D6 | D8 fill | Total |
|---|---|---|---|---|---|---|---|---|
| Costa Rica | 300 | 240 | 30 | 420 | 0 | 0 | 0 | 990 |
| Dominican Republic | 2,301 | 0 | 0 | 99 | 66 | 0 | 0 | 2,466 |
| Ecuador | 5,011 | 180 | 0 | 0 | 0 | 26 | 3 | 5,220 |
| Guatemala | 660 | 330 | 0 | 363 | 0 | 0 | 0 | 1,353 |
| Honduras | 992 | 66 | 0 | 159 | 0 | 0 | 60 | 1,277 |
| Jamaica | 839 | 34 | 0 | 841 | 0 | 0 | 0 | 1,714 |
| Total | 10,103 | 850 | 30 | 1,882 | 66 | 26 | 63 | 13,020 |

Not written: 210 Costa Rica proposals with no value (cells stay empty) and 951 keep cells that D3 and D6 did not change; no proposal falls on a D5 or D10 cell. Unplaced: 0. Projection modes switched to "User defined": 87 (D8 83, D8 EMPTY with a non-zero value 2, D4 2). D2: R = 6,201.6390 USD/kW (2024), factor 1.2160076 on the regional path. D3: 66 groups converted, 109 groups left in their source currency year (GAPS section 3). D7: the gas sentence removed from 62 written rows. D9: `A-O_Demand.xlsx` M25 0.675 to 0.00667.

| C4 gate | Result |
|---|---|
| (1) written cells equal `write_set.csv` to 1e-9 relative | pass, 13,020 of 13,020 |
| (2) changes only at manifest cells, D8 mode cells and M25 | **FAIL on a strict reading**: 13,020 manifest cells, 87 mode cells and M25 changed as intended, plus 5 formula cells that reference written cells and recalculated (Guatemala DIST_FLEXFUEL VariableCost 2018 and 2019, Honduras PPBGS CapitalCost 2018 to 2020) and 1 formula whose text Excel normalised (DR ELE_TRANS CapitalCost 2018, value unchanged). Not fixed: out of scope (GAPS section 2) |
| (3) formula cells without a stored value | pass, 0 in 7 workbooks |
| (4) other A-O workbooks byte-identical | pass, 469 of 469 other tracked `A-O_*.xlsx` (41 other `A-O_Parametrization.xlsx`) |

`ao_cost_repair_manager.py verify` passed for all six manifests.

## Phase D. Recompile (08:45 to 09:18 UTC)

A2 then B1 per country with the Phase B commands; every exit code 0.

| Gate | Result |
|---|---|
| D2 keyed comparison with the Phase B outputs (`recompile_diff_summary.csv`) | 107,247 differing values in A2, B1 and data files; 106,923 allowed (written cost cells; Costa Rica E5INDCOA 2021 in A2); 324 not allowed (item 2 above) |
| Written cells reach the compiled A2 output (`compiled_check.csv`) | 39,060 cell and scenario checks: 39,033 equal at A2's 4-decimal rounding, 27 differ by 0.0001 at rounding ties |
| D3 solve status of the B1 `_0` runs | 19 of 19 OPTIMAL (Costa Rica 4 with the temporary LTSOPT) |

B1 `_0` objective values (model units, `recompile/<Country>/B1/solve_log.jsonl`), Phase B baseline then recompiled:

| Country | BAU | NDCNEW | LTSNEW |
|---|---|---|---|
| Costa Rica | 105,635 to 116,178 | 92,329 to 102,698 | 87,655 to 97,724 |
| Dominican Republic | 428,270 to 407,131 | 444,471 to 428,532 | 464,584 to 452,813 |
| Ecuador | 107,499 to 1,978,795 | 128,531 to 2,669,127 | 130,674 to 2,670,548 |
| Guatemala | 379,489 to 358,872 | 367,367 to 350,349 | 362,054 to 348,141 |
| Honduras | 132,862 to 107,335 | 124,708 to 103,516 | 118,739 to 100,975 |
| Jamaica | 52,253 to 62,713 | 50,796 to 61,367 | 48,593 to 59,083 |

## Phase E. Stages 0 to 3 (09:18 to 10:08 UTC)

| Stage | Commands and results | Duration |
|---|---|---|
| 0 | clean, run (529 values patched), batch (18 of 18 OPTIMAL), collect (18 OK, 0 infeasible), capacity check, recommend shares, test 10 of 10 | 21 min (third attempt) |
| 1 | share analyzer, test 13 of 13 | 12 s |
| 2 | apply, test: 7 of 7 hard PASS; soft T8, T9, T11a FAIL | 5 s |
| 3 | apply, test 10 of 11 (T4), batch 18 of 18 OPTIMAL, results: RE targets 24 of 24, share validation 7,882 pass, 108 warn, 8 fail | 24 min |

Solve status by country and scenario: all 18 Stage 3 runs OPTIMAL, as on 16 May (the 16 May data files solved again: 18 of 18 OPTIMAL).

### Results compared with 16 May

Objective in model units; RE share of power-sector activity as `stage3_results.py` computes it (16 May > new); emissions are AnnualEmissions summed over every emission, as `stage3_results.py` prints them; new capacity is NewCapacity of PP/PWR technologies summed over the horizon, in model capacity units. Full detail in `results_compare.csv`.

| Country | Scenario | Status 16 May / new | Objective 16 May | Objective new | RE 2030 | RE 2035 | RE 2050 | Shares pass/warn/fail 16 May | new | Emissions 2030 | Emissions 2050 | PP new capacity, sum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CostaRica | BAU | OPTIMAL / OPTIMAL | 103,588 | 114,697 | 89.4 > 89.4% | 89.4 > 89.4% | 89.4 > 89.4% | 234/0/0 | 234/0/0 | 23.72 > 23.72 | 34.04 > 34.04 | 5.37 > 5.37 |
| CostaRica | NDCNEW | OPTIMAL / OPTIMAL | 94,047 | 104,293 | 89.7 > 89.7% | 90.0 > 90.0% | 90.0 > 90.0% | 231/3/0 | 233/1/0 | 22.16 > 22.16 | 27.87 > 27.87 | 7.16 > 6.96 |
| CostaRica | LTSNEW | OPTIMAL / OPTIMAL | 85,988 | 95,575 | 93.7 > 93.7% | 99.0 > 99.0% | 99.0 > 99.0% | 232/2/0 | 234/0/0 | 19.50 > 19.50 | 8.43 > 8.43 | 8.46 > 8.11 |
| DominicanRepublic | BAU | OPTIMAL / OPTIMAL | 425,608 | 411,651 | 19.2 > 19.2% | 23.1 > 23.1% | 33.9 > 33.9% | 598/0/0 | 598/0/0 | 72.29 > 72.60 | 112.51 > 112.87 | 23.05 > 22.76 |
| DominicanRepublic | NDCNEW | OPTIMAL / OPTIMAL | 439,827 | 430,752 | 41.8 > 42.1% | 75.0 > 75.0% | 75.0 > 75.0% | 593/5/0 | 598/0/0 | 58.55 > 59.06 | 60.90 > 61.71 | 30.19 > 30.65 |
| DominicanRepublic | LTSNEW | OPTIMAL / OPTIMAL | 459,310 | 454,800 | 41.8 > 42.1% | 75.0 > 75.0% | 99.0 > 99.0% | 592/6/0 | 598/0/0 | 58.54 > 59.06 | 17.37 > 17.44 | 40.90 > 42.01 |
| Ecuador | BAU | OPTIMAL / OPTIMAL | 107,054 | 1,933,690 | 76.6 > 76.3% | 77.7 > 77.4% | 80.9 > 80.6% | 794/12/0 | 794/12/0 | 130.84 > 130.95 | 182.56 > 182.77 | 602.30 > 592.85 |
| Ecuador | NDCNEW | OPTIMAL / OPTIMAL | 128,481 | 2,086,399 | 77.9 > 77.7% | 80.1 > 80.2% | 80.9 > 80.6% | 784/22/0 | 795/11/0 | 125.65 > 125.79 | 165.33 > 165.35 | 629.72 > 617.64 |
| Ecuador | LTSNEW | OPTIMAL / OPTIMAL | 127,291 | 2,080,590 | 77.9 > 77.7% | 80.1 > 80.2% | 99.0 > 99.0% | 779/27/0 | 782/24/0 | 125.30 > 125.42 | 117.68 > 117.68 | 636.55 > 624.95 |
| Guatemala | BAU | OPTIMAL / OPTIMAL | 381,734 | 360,741 | 53.0 > 53.1% | 57.2 > 57.2% | 64.0 > 64.1% | 356/5/3 | 356/6/2 | 75.21 > 75.21 | 156.41 > 156.46 | 7.52 > 7.54 |
| Guatemala | NDCNEW | OPTIMAL / OPTIMAL | 367,236 | 350,275 | 68.6 > 68.6% | 75.0 > 75.0% | 75.0 > 75.0% | 353/9/2 | 362/2/0 | 64.31 > 65.08 | 125.15 > 125.13 | 11.94 > 11.72 |
| Guatemala | LTSNEW | OPTIMAL / OPTIMAL | 361,792 | 348,264 | 68.6 > 68.6% | 75.0 > 75.0% | 99.0 > 99.0% | 354/8/2 | 363/1/0 | 65.94 > 66.71 | 66.53 > 66.55 | 27.16 > 26.94 |
| Honduras | BAU | OPTIMAL / OPTIMAL | 128,297 | 104,950 | 56.9 > 56.9% | 59.0 > 59.0% | 64.7 > 64.7% | 416/0/0 | 416/0/0 | 39.20 > 39.22 | 58.98 > 59.20 | 7.51 > 7.51 |
| Honduras | NDCNEW | OPTIMAL / OPTIMAL | 124,904 | 103,910 | 64.8 > 64.8% | 75.0 > 75.0% | 75.0 > 75.0% | 407/9/0 | 407/9/0 | 36.28 > 36.31 | 52.50 > 52.66 | 10.53 > 10.62 |
| Honduras | LTSNEW | OPTIMAL / OPTIMAL | 118,837 | 101,468 | 64.8 > 64.8% | 75.0 > 75.0% | 99.0 > 99.0% | 407/9/0 | 407/9/0 | 36.22 > 36.24 | 23.69 > 23.90 | 16.98 > 17.08 |
| Jamaica | BAU | OPTIMAL / OPTIMAL | 56,688 | 65,081 | 13.8 > 13.8% | 18.2 > 18.2% | 29.3 > 29.3% | 228/20/0 | 231/17/0 | 12.57 > 12.65 | 15.27 > 15.35 | 2.17 > 1.36 |
| Jamaica | NDCNEW | OPTIMAL / OPTIMAL | 52,752 | 61,693 | 39.1 > 39.1% | 75.0 > 75.0% | 75.3 > 75.0% | 203/34/11 | 228/14/6 | 11.01 > 11.09 | 11.38 > 11.48 | 3.63 > 3.54 |
| Jamaica | LTSNEW | OPTIMAL / OPTIMAL | 50,476 | 59,668 | 39.6 > 39.1% | 75.0 > 75.0% | 99.0 > 99.0% | 228/18/2 | 246/2/0 | 10.94 > 11.02 | 4.72 > 4.80 | 5.55 > 5.54 |

RE targets met (2 pp tolerance): 24 of 24 on 16 May and 24 of 24 now.

Five largest changes in new capacity per country (summed over the horizon, model capacity units; `results_compare_top_newcap.csv`):

| Country | Scenario | Technology | 16 May | New | Change |
|---|---|---|---|---|---|
| CostaRica | LTSNEW | PWRSUG | 2.721 | 2.375 | -0.346 |
| CostaRica | NDCNEW | PWRSUG | 1.490 | 1.293 | -0.197 |
| CostaRica | BAU | PWRWNONS | 2.255 | 2.260 | +0.006 |
| CostaRica | BAU | PWRHYDDAM | 0.193 | 0.193 | -0.000 |
| CostaRica | BAU | PWRHYDROR | 0.105 | 0.105 | -0.000 |
| DominicanRepublic | LTSNEW | PPDBGS | 0.042 | 0.543 | +0.501 |
| DominicanRepublic | LTSNEW | PPPVT | 17.284 | 17.716 | +0.432 |
| DominicanRepublic | LTSNEW | PPBIM | 0.320 | 0.002 | -0.318 |
| DominicanRepublic | BAU | PPBGS | 0.268 | 0.000 | -0.268 |
| DominicanRepublic | LTSNEW | PPWNDON | 10.433 | 10.700 | +0.267 |
| Ecuador | LTSNEW | PPHD | 607.372 | 597.076 | -10.296 |
| Ecuador | NDCNEW | PPHD | 607.372 | 597.076 | -10.296 |
| Ecuador | BAU | PPHD | 585.225 | 576.736 | -8.488 |
| Ecuador | NDCNEW | PPHRORAB | 2.615 | 0.652 | -1.963 |
| Ecuador | LTSNEW | PPHRORAB | 2.615 | 0.652 | -1.963 |
| Guatemala | LTSNEW | PPDSL | 3.486 | 0.082 | -3.404 |
| Guatemala | LTSNEW | PPFOI | 0.330 | 3.719 | +3.389 |
| Guatemala | LTSNEW | PPWNDON | 7.955 | 7.850 | -0.105 |
| Guatemala | LTSNEW | PPPVT | 7.360 | 7.264 | -0.096 |
| Guatemala | NDCNEW | PPWNDON | 2.544 | 2.458 | -0.086 |
| Honduras | LTSNEW | PPNGS | 0.132 | 2.275 | +2.143 |
| Honduras | LTSNEW | PPGTDSL | 2.135 | 0.001 | -2.134 |
| Honduras | NDCNEW | PPNGS | 0.112 | 1.312 | +1.200 |
| Honduras | NDCNEW | PPGTDSL | 1.192 | 0.001 | -1.191 |
| Honduras | BAU | PPGTDSL | 0.280 | 0.001 | -0.279 |
| Jamaica | BAU | PPPVT | 1.179 | 0.658 | -0.522 |
| Jamaica | LTSNEW | PPNGS | 0.522 | 0.039 | -0.484 |
| Jamaica | LTSNEW | PPDSL | 0.090 | 0.573 | +0.483 |
| Jamaica | BAU | PPWNDON | 0.358 | 0.076 | -0.283 |
| Jamaica | NDCNEW | PPWNDON | 0.797 | 0.682 | -0.115 |

### E3. Guatemala PPPVT before 2025

Rechecked by values: new capacity 0.386 GW in 2018 and 0.280 GW in 2022 in NDCNEW and LTSNEW (0.667 GW in total, unchanged from 16 May), none in BAU, against a residual capacity of 0.08 GW. The B1 NDCNEW and LTSNEW activity lower limits of PPPVT for 2018 to 2024 (3.81 PJ in 2018, 6.46 PJ in 2022) are five to ten times BAU's (0.54 and 0.63 PJ); at the 2018 capacity factor 0.2607, 3.81 PJ needs 0.466 GW. Stage 3 patches only 2025 onward. Known-limitation candidate (GAPS).

## Phase F. Final gates

| Gate | Result |
|---|---|
| F1 changed paths | only Phase A files (`ao_safe_save.py`, `test_ao_safe_save.py`, `.gitignore`), the six energy A-O workbooks and Costa Rica `A-O_Demand.xlsx`, A2 and B1 outputs of the six energy models, the four stage output folders and the job folder; no path-only fix was needed |
| F2 no staged file above 50 MB | pass (0) |
| F2 no `*.safesave_tmp*` file | pass (0) |
| F2 `EXCEL.EXE` count | 0, equal to the count at the start (0) |
| F2 `git diff --check` | flagged: CR at end of changed lines in the CRLF pipeline CSVs only; clean with `core.whitespace=cr-at-eol` and clean on all other files |
| F2 no em dash in files I wrote | pass |
| F2 no `Co-Authored-By` or "Generated with" in `git log origin/main..HEAD` | pass |

Setup: clone `/c/clw_overnight` from the main copy, origin set to GitHub, branch from `origin/main` (`4124868`, unchanged). Free disk on C: 129 GB at the start, lowest 94 GB (rule not triggered). `EXCEL.EXE` running at the start: 0.
