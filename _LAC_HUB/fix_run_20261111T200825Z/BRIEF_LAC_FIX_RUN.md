# BRIEF LAC_FIX_RUN: review fixes of PR #10 written into the six energy models, A2 and B1 recompiled, Stages 0 to 3 re-run

Repository: https://github.com/luviga/clewise-lac, `main` at `c42ae07` (PR #10 squash-merged). No open pull requests.

You work alone and to the end. This is a long run (several hours: source searches, then about 20 minutes for Stage 0 and 25 minutes for Stage 3 solves, plus recompiles). Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge.

## 0. Restartability

Keep `PROGRESS.md` in the job folder. After every numbered step, append one line: UTC time, step number, done or blocked, and the key count. Commit and push at the end of every phase. If your context is compacted or the session restarts, read this brief and `PROGRESS.md` first and continue from the first step not marked done.

## 1. Goal

Apply the seven fixes Luis decided on 11 November 2026 when reviewing PR #10, then recompile and re-run Stages 0 to 3 once. The fixes: replace three unexplained formulas; correct Costa Rica 2021 industry coal where the scenario config overrides it; rebuild the Ecuador crude balance and prices; resolve the dollar year of 109 cost groups; write source values over old values kept inside sourced paths; make every scenario reproduce the same history; set Jamaica hydro to the planned amount in every scenario. Stage 4 and the paper are later jobs.

## 2. The standard

The model runs only on externally sourced values, values a rule computes every run from sourced inputs, and labelled ASSUMPTIONs. A source is downloaded, retrievable and readable before it enters a model: a URL, DOI or public permalink you opened, with the page or table. Internal files are never a source. An ASSUMPTION sentence states the value and the plain reason for it; it never says "not found", "kept as used" or "retained". Never write a value from memory.

Every number enters through a data file (A-O workbooks, `A-O_Demand.xlsx`, `B1_Scenario_Config.xlsx`, stage input CSVs). Never edit `OSeMOSYS_Model.txt`.

Scope is frozen. Do only what section 6 lists. Anything new you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

Commit messages and the pull request description carry no `Co-Authored-By` line and no "Generated with" line of any kind.

## 3. Facts already checked by values (hub 8, at `c42ae07`)

Inputs from PR #10, all tracked: `_LAC_HUB/cost_write_run_20261111T071733Z/` holds `write_set.csv`, `currency_conversion.csv`, `assumptions_final.csv`, `pipeline_commands.csv`, `results_compare.csv`, the REPORT and GAPS. `_LAC_HUB/cost_review_20261111T015203Z/proposals_all.csv` holds every proposal with `basis_class`, `source_ids` and `derivation`. The six country job folders `_LAC_HUB/cost_src_{cr,dr,ecu,gua,hon,jam}_<stamp>/` hold `sources.csv` and `constants.csv` (CPI-U annual averages BEN-004, Brent annual averages BEN-001, WEO 2025 price series BEN-005).

F1. Formula cells (item 1):
- Guatemala `GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, Primary Techs row 284, `DIST_FLEXFUEL` VariableCost: formula `=I14+(I14*0.8)` on `DIST_GSL` from 2018 (45.31 USD/GJ in 2018, 71.89 in 2050). Flex fuel feeds `T4Flex_Fuel_PRI`, then `TRAUTFlex_Fuel` and `TRMOTFlex_Fuel`: capped at 0 in BAU, forced by activity lower limits in NDCNEW and LTSNEW.
- Honduras `HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, Secondary Techs row 27, `PPBGS` CapitalCost 2018 to 2020: formula `=I17*(5053/5391)` on `PPBIM` (1,813.8 USD/kW); 2021 onward a plain 5,390.58.
- Dominican Republic `RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, Secondary Techs J232, `ELE_TRANS` CapitalCost 2018: `=(26.24+58.85+382.80)/(5.501*8670*0.0036)` = 2.7251.

F2. Costa Rica coal (item 2): `CostaRica/CR_ENERGY/t1_confection/B1_Scenario_Config.xlsx`, sheet Efficiency, rows 47 (BAU), 48 (LTSNEW), 49 (NDCNEW) and 119 (LTSOPT), Parameter `SpecifiedAnnualDemand`, Set `E5INDCOA`, Method "Exact": column M (2021) = 0.675; column N (2022) = 0.00667. The A-O already holds 0.00667 for 2021 (PR #10, D9). Correct value 0.00667 PJ, source CRC-006 (Costa Rica energy balance, in the Costa Rica job `sources.csv`).

F3. Ecuador crude (item 3), `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`, columns from 2021:
- Primary Techs row 384 `EXTT_CRU` VariableCost: CCG kit `MINOIL` value (13.94 USD/GJ in 2024, 21.51 in 2050, the same in every fuel scenario). Rows 387 and 388: activity upper and lower limits (lower 0 in 2021 to 2023, 940.97 PJ in 2024, 741.4 in 2030, 619.3 from 2035; upper about 2 percent above).
- Primary Techs row 134 `DIST_CRU` VariableCost: Ecuador export value, 11.86 USD/GJ in 2024 (WEO STEPS path, 11.41 in 2050). Rows 137 and 138: upper 999,999; lower 49.24 PJ in 2024 rising to 377.4 from 2035.
- `A-O_Demand.xlsx`, sheet Demand_Projection, row 58 `E5EXPCRU`: 657.9 PJ (2021), 629.1 (2024), 414.0 (2035), 342.6 (2037), 0 from 2038.
- Demand Techs rows 95 to 97 `T5CRUEXP`: CapitalCost, FixedCost, ResidualCapacity only, mode "EMPTY"; there is no VariableCost row.
- Refinery `PROCRU` is pinned (lower 329.2, upper 332.6 PJ). `E0CRU` is used only by `PROCRU` (input 1.0) and `T5CRUEXP`.
- Solved balance at `c42ae07`, all scenarios: extraction plus imports minus refinery and exports = 0 in 2021 to 2023, 31.9 PJ in 2024, 169.4 in 2030, 253.5 in 2035, 667.5 PJ a year from 2038 (11,449 PJ in total). OSeMOSYS keeps a surplus (greater-or-equal balance).
- `VariableCost` is declared without a sign restriction in `OSeMOSYS_Model.txt`, so a negative value is valid.
- Sources already in the Ecuador job: ECU-001 (Petroecuador Informe Estadistico 2024), ECU-002 (BCE `SerieCifrasPetroleras.xlsx`, monthly production and exports 2007 to 2025), BEN-001 (Brent annual), BEN-005 (WEO 2025 Table 2.3), CCG-002 (CCG Ecuador kit), CCG-014 (CCG data article).

F4. Currency (item 4): `currency_conversion.csv` rows whose `left` says not stated, mixed, ambiguous, 2025 USD or January 2010: 109 groups (DR 60, Guatemala 16, Honduras 16, Ecuador 9, Jamaica 8). 90 are used in a solve. Honduras PIEG 2024-2033 Tabla 7 states 2023 USD for the capital costs of the same table.

F5. Matched cells (item 5): in `proposals_all.csv`, 53 groups (country, Tech, Parameter, fuel_scenario) mix `basis_class` "matched" with sourced classes; they hold 304 matched cells (DR 42, Ecuador 3, Guatemala 15, Honduras 144, Jamaica 100). Example: Ecuador `PPPVT` CapitalCost 2049 and 2050 = 800 (source 810.43 and 803.58); `PPWNDON` 2026 = 1,300 (source 1,311.99). Ecuador `PPHDAMAM`, `PPHDAMPM` and `PPHRORAB` CapitalCost 3,500 USD/kW were matched to CCG large hydro (3,562.18 in 2024 USD) but are likely CCG small hydro (3,499 in 2020 USD) without conversion (review pack, `REPORT_LAC_COST_REVIEW_PACK_20261111T015203Z.md`, line 808).

F6. History by scenario (item 6), power-plant activity from `_STAGE3_RESULTS/stage3_results.xlsx`: Ecuador NDCNEW and LTSNEW 189.7 PJ in 2021 against 114.5 in BAU (wind 24.5 against 0.22), 215.5 against 127.3 in 2024; Guatemala up to 7.8 PJ more (2023); DR up to 4.0 PJ (2024, `PPICEFOI` 13.59 in BAU, 0 in the policy scenarios); Honduras up to 1.4 PJ; Costa Rica 2023 Stage 0 denominator 45.5 BAU against 49.1 policy. Stage 2 soft test T11a flags 27 years. Same on 16 May.

F7. Jamaica hydro (item 7), `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, Primary Techs rows 192 to 201 (`PPHROR`): row 199 TotalAnnualMinCapacityInvestment (User defined) gives 12.7 MW (2027), 7.0 (2028), 11.0 (2029), 2.0 (2031), 1.0 (2032), 33.7 MW in total, in all three scenarios; row 198 activity lower limit (User defined) rises to 0.5152 PJ in 2030 and 0.5656 in 2050; row 196 TotalAnnualMaxCapacity is "EMPTY". Stage 3 also builds 1.2 MW (2024), 15.3 (2025) and 0.2 (2026) without a minimum. Hydro output 0.39 PJ in 2026, 0.92 in 2030, about 0.97 from 2040, the same in all scenarios. Stage 2 soft test T9 flags all 87 cases in Jamaica. The 2022 Jamaica Integrated Resource Plan (MSETT, Cabinet-approved and published November 2024) lists 34.3 MW of small hydro (12 plants) as indicative capacity; download it and confirm the figure and any schedule before use.

F8. Hydro output is about the same in every scenario in the other five countries, so scenarios differ through solar and wind.

F9. Tests at `c42ae07`: Stage 0 10 of 10; Stage 1 13 of 13; Stage 2 hard 7 of 7, soft T8 65, T9 87, T11a 27; Stage 3 10 of 11 (T4, 40 Guatemala cells, the documented `--skip-orphan-cap Guatemala` effect); share validation pass 7,882, warn 108, fail 8; 18 of 18 optimal; RE targets 24 of 24.

Pipeline commands: `_LAC_HUB/cost_write_run_20261111T071733Z/pipeline_commands.csv` (canonical A2 and B1 runner per country) and the stage commands in `PIPELINE_WORKFLOW.md`. Writer: `ao_cost_repair_manager.py` (manifest apply and verify, saves through `save_ao_safely`).

## 4. Decisions in force (Luis, 11 November 2026)

- R1. Replace each formula of F1 with a sourced value, or a labelled ASSUMPTION with a stated range where no source exists. Guatemala flex-fuel price: the published price of the flex-fuel blend in Guatemala or the region, pre-tax, real 2024 USD, on the gasoline WEO path. Honduras `PPBGS` CapitalCost 2018 to 2020: a sourced biogas plant capital cost, tier order national, regional, international (IRENA Renewable Power Generation Costs), real 2024 USD, consistent with the 2021 onward row. DR `ELE_TRANS` 2018: source each input of the formula or label it; write the result as a plain value.
- R2. Costa Rica: set column M (2021) of rows 47, 48, 49 and 119 of F2 to 0.00667. Nothing else in the config changes.
- R3. Ecuador crude:
  - Exports stay a demand: `E5EXPCRU` takes a sourced export path (history from ECU-002; projection from a published outlook of the Ministerio de Energia y Minas, Petroecuador or the BCE).
  - Extraction follows a sourced production path: lower and upper limits of `EXTT_CRU` from the same sources, never above the latest observed year.
  - Crude imports `DIST_CRU`: lower limit 0 in every year, upper limit as now; OSeMOSYS fills any shortfall.
  - Prices, base model (STEPS): `EXTT_CRU` VariableCost = the current `DIST_CRU` path (Ecuador export value) in every year; `T5CRUEXP` VariableCost = minus that same path; `DIST_CRU` VariableCost = Brent on the WEO 2025 STEPS path in real 2024 USD (BEN-001 history, BEN-005 projection), plus freight only if you find a source for it.
  - Balance check every run: extraction plus imports minus (refinery crude input plus exports) per year and scenario; any year above 0.5 PJ is reported, not solved around.
  - If no source gives a production or export projection, keep the current projection values unchanged, list them in `sources_pending.csv` with every URL you tried and why it failed, and apply everything else in R3.
- R4. Resolve all 109 groups of F4, used ones first: find the currency year in the source document itself (NREL ATB and IRENA documentation state their dollar year; PIEG Tabla 7; PEN 2022-2036; PEIG; PLANMICC). Where the document truly does not state it, write an ASSUMPTION: the currency year is the year before publication, with that reason. Convert to real 2024 USD with CPI-U annual averages (BEN-004). Update `currency_conversion.csv`.
- R5. In every group of F5 that takes sourced values in any year, write the source value in every year (304 cells). Keep "matched" only where a whole row agrees with its source. Check the three Ecuador hydro rows of F5 against the CCG kit (CCG-002) and write the CCG value of the matching technology, converted to 2024 USD.
- R6. Every scenario reproduces the same history as BAU through 2024. Find by values where the policy scenarios' inputs for 2018 to 2024 differ from BAU (A2 scenario folders, `B1_Scenario_Config.xlsx` rows whose years start in history, Stage 0 denominators, Stage 1 and 2 controller values) and make the least change, in data files or stage inputs, that removes the difference. Do not change targets or anything after 2024.
- R7. Jamaica hydro: the IRP-2 planned small hydro, 34.3 MW, in all three scenarios. `PPHROR` new capacity follows the IRP-2 schedule if the plan gives one (otherwise keep the timing of row 199 and scale it to 34.3 MW), with TotalAnnualMaxCapacity capped at the cumulative plan. No hydro build in 2024 to 2026 unless observed generation (JPS or MSETT statistics) shows a new plant; if it does, record the source. Hydro activity lower limits must be reachable with the capped capacity. Hydro output stays identical across the three scenarios.
- R8. Write `starter_kit_deviations.csv`: one row per CCG Ecuador kit value the model does not take as published (kit and DOI, kit file and cell, parameter, technology, kit value, model value, one-sentence reason, model source ids, decision date). It starts with `EXTT_CRU` VariableCost (reason: the kit values domestic crude at the Brent level, while Ecuador crude sells at about 0.85 of Brent and the model values it at its export price) and covers every CCG-sourced Ecuador row R1 to R5 change.
- R9. Environment rules from PR #10: call batch files by full path (`NoDefaultCurrentDirectoryInExePath=1`); no `glpsol.bat` wrapper on PATH during stage runs; absolute log paths in solve wrappers; Guatemala A2 through `_LAC_HUB/cost_write_run_20261111T071733Z/scripts/run_with_append_shim.py`; Costa Rica B1 needs a temporary `A2_Output_Params/LTSOPT` (copy of LTSNEW) and empty `B1_Output_Params/LTSOPT`, removed afterwards; run `test_ao_cost_repair_manager` through `unittest discover`.

## 5. Setup

- Windows, Git Bash, Anaconda Python as `py`; run your own scripts with `py -I`. Microsoft Excel and pywin32 are required for A-O saves. `glpsol` at `C:\glpk-4.65\w64`.
- Clone: `git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_fix`; in it `git remote set-url origin https://github.com/luviga/clewise-lac.git`, `git fetch origin`, branch `job/fix-run` from `origin/main`. Check `origin/main` is `c42ae07`; if newer, branch from it and record the hash.
- One UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder `_LAC_HUB/fix_run_<stamp>/` in the clone. Copy this brief into it. Downloads go to `_LAC_HUB/fix_run_<stamp>/downloads/` (gitignored if larger than 10 MB; record URL, date and SHA-256 in `sources.csv`).
- Free disk on C: recorded at the start; below 80 GB, delete solver output `.txt` files over 500 MB of a stage whose extraction has finished. Nothing else.
- Write only inside `/c/clw_fix`. Read-only: the main copy `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5`, `/c/clw_overnight` and every other `C:\clw_*` clone, anything under Dropbox `2_WORK`. The nine untracked `_LAC_HUB/BRIEF_*.md` files of the main copy stay as they are.
- Record the number of `EXCEL.EXE` processes before Phase A; never close one you did not start.

## 6. Work

### Phase A. Sources

A1. For R1, R3, R4, R5 and R7, search and download each source; open it and record the page or table. Write `sources.csv` (id, URL, title, publisher, date, accessed, SHA-256, page or table) and `proposals.csv` (country, workbook, sheet, row, Tech, Parameter, year, current value, new value, rule R1 to R7, source ids, derivation, ASSUMPTION sentence where used). List unreachable URLs in `sources_pending.csv`.
A2. Write `starter_kit_deviations.csv` (R8).
A3. Commit "Phase A: sources and proposals for the review fixes".

### Phase B. Write

B1. Back up every workbook you will change into `backups/` with a SHA-256 manifest.
B2. Write the A-O and `A-O_Demand.xlsx` cells of `proposals.csv` with `ao_cost_repair_manager.py` (manifest, apply, verify) or openpyxl plus `save_ao_safely` for cells it cannot address. Switch Projection.Mode to "User defined" where values now vary by year. For `T5CRUEXP` VariableCost: add the row to Demand Techs only if the canonical Ecuador A2 compiler reads it (check by a test compile); otherwise write it in `Ecuador/ECU_Energy/B1_Scenario_Config.xlsx` as an Overwrite row for BAU, NDCNEW and LTSNEW. Record which.
B3. Write R2 in the Costa Rica config, and the R6 and R7 changes wherever Phase A found they enter.
B4. Gates: every written cell equals `proposals.csv` to 1e-9 relative; a cell-by-cell comparison of every changed workbook shows changes only at listed cells and their mode cells; zero formula cells without a stored value; no formula left in the three F1 cells; every other A-O workbook byte-identical. Write `write_check.csv`.
B5. Commit "Phase B: review fixes written".

### Phase C. Recompile

C1. Run A2, then B1, per country with the commands of `pipeline_commands.csv`.
C2. Gate: keyed comparison against the tracked outputs at `c42ae07`. Allowed differences: the parameters and technologies of `proposals.csv`; Costa Rica `SpecifiedAnnualDemand` `E5INDCOA` 2021; Ecuador `E5EXPCRU` demand, `EXTT_CRU` and `DIST_CRU` limits and costs, `T5CRUEXP` VariableCost; Jamaica `PPHROR` rows; the R6 history changes in 2018 to 2024 of NDCNEW and LTSNEW. Any other difference: find its cause; fix it if it comes from your write; otherwise record it. Write `recompile_diff_summary.csv`.
C3. Commit "Phase C: A2 and B1 recompiled".

### Phase D. Stages 0 to 3

D1. Run Stages 0, 1, 2 and 3 with every test, as in `PIPELINE_WORKFLOW.md` (Stage 3: `py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala`). A failing test does not stop the pipeline; an infeasible solve is recorded, not tuned.
D2. Gates by values, written to `fix_checks.csv`:
- History: power-plant activity per technology identical in BAU, NDCNEW and LTSNEW for every year through 2024, every country (tolerance 0.05 PJ); T11a reports 0 years.
- Ecuador crude balance (R3): surplus at most 0.5 PJ in every year and scenario; report extraction, imports, refinery and exports for 2024, 2030, 2035, 2040 and 2050.
- Jamaica: `PPHROR` new capacity at most 34.3 MW over the horizon in every scenario, none in 2024 to 2026 unless sourced; hydro output identical across scenarios; T9 reports 0.
- Costa Rica `E5INDCOA` 2021 demand 0.00667 PJ in every scenario.
- Hydro output by country and scenario for 2026, 2030, 2040 and 2050.
D3. Compare with `c42ae07` in `results_compare.csv` (as in PR #10): solve status, objective, RE share 2030, 2035, 2050 against target, share validation, new capacity by power technology, emissions 2030 and 2050; the five largest new-capacity changes per country.
D4. Commit stage outputs and the job folder: "Phase D: base re-runs, Stages 0 to 3".

### Phase E. Final gates and pull request

E1. `git diff --name-only origin/main` shows only the changed workbooks and configs, the A2 and B1 outputs of the six energy models, any stage input you changed for R6, the four stage output folders and the job folder.
E2. No file over 50 MB staged; no `*.safesave_tmp*` file; `EXCEL.EXE` count as at the start; `git diff --check` clean; no em dash in any file you wrote; no `Co-Authored-By` or "Generated with" line in `git log origin/main..HEAD`.
E3. Push and open one draft pull request titled "LAC_FIX_RUN: review fixes of PR #10, recompile and base re-runs", body from CHANGES. A last commit only to write hashes into REPORT is allowed.

## 7. Outputs

All in the job folder, plain English, no em dashes, one UTC stamp.

`REPORT_LAC_FIX_RUN_<stamp>.md`: anything failed, blocked or pending first; pull request number, base and commit hashes; per fix R1 to R7 what changed, with before and after values and sources; gate results with counts; the `fix_checks.csv` results; the results comparison table; tests and solve statuses.

`GAPS_LAC_FIX_RUN_<stamp>.md`: every judgement call and its reason; where R6 and R7 entered and why that was the least change; "Known-limitation candidates"; anything left unchecked; `sources_pending.csv` summarised; incidents.

`CHANGES_LAC_FIX_RUN_<stamp>.md`: file or folder by file, what changed and why, two or three lines each.

Also in the job folder: `PROGRESS.md`, `sources.csv`, `proposals.csv`, `sources_pending.csv`, `starter_kit_deviations.csv`, `currency_conversion.csv` (updated), `write_check.csv`, `recompile_diff_summary.csv`, `fix_checks.csv`, `results_compare.csv`, test and stage logs.

Tracked files outside the job folder follow the repository's writing rules: no machine paths, no figures from model results in docs.
