# BRIEF LAC_OVERNIGHT_COST_RUN: safe-save write order, sourced costs written into the six energy models, A2 and B1 recompiled, Stages 0 to 3 re-run

Repository: https://github.com/luviga/clewise-lac, `main` at `4124868`. No open pull requests. This brief replaces `BRIEF_LAC_W0_SAFE_SAVE_ORDER.md`, which was never launched; its work is Phase A here.

You work alone and to the end, overnight. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge.

## 0. Restartability

Keep `PROGRESS.md` in the job folder. After every numbered step, append one line: UTC time, step number, done or blocked, and the key count. Commit and push at the end of every phase. If your context is compacted or the session restarts, read this brief and `PROGRESS.md` first and continue from the first step not marked done. Never redo a step marked done unless a later gate shows it is wrong.

## 1. Goal

Make the six energy models least-cost on sourced costs, then produce the base results. In order: fix the save order of the A-O writer (Phase A); check that the pipeline scripts reproduce today's compiled inputs before anything changes (Phase B); write the reviewed cost proposals and the decisions below into the A-O workbooks (Phase C); recompile A2 and B1 (Phase D); re-run Stages 0 to 3 for 18 country and scenario pairs and compare with the 16 May results (Phase E). Stage 4 and the paper are later jobs.

## 2. The standard

The model runs only on externally sourced values, values a rule computes every run from sourced inputs, and labelled ASSUMPTIONs. Every value written comes from the reviewed proposal files or from a rule in section 3 whose inputs are named there. Never write a value from memory or from an internal file that is not listed here.

Scope is frozen. Do only what section 6 lists. Anything new you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

Commit messages and the pull request description carry no `Co-Authored-By` line and no "Generated with" line of any kind.

Solver: GLPK (`glpsol`, `C:\glpk-4.65\w64\` on this machine), as the pipeline expects. The parsers read the GLPK `-o` output format, so no other solver is used.

## 3. Decisions in force and facts checked by values (at `4124868`)

Inputs, all tracked on `main`:

- `_LAC_HUB/cost_review_20261111T015203Z/proposals_all.csv`: 17,921 rows, one per cell. Columns include `country, sheet, Tech.ID, Tech, Parameter, fuel_scenario, year, current_value, proposed_value, change_class, basis_class, source_ids, derivation, assumption_sentence, projection_mode, needs_user_defined_mode`. `fuel_scenario` is ALL (12,212 rows), STEPS, CPS or NZE (1,903 each). `sheet` is "Primary Techs" or "Secondary Techs". The column `workbook_cell` is not a cell address; locate cells by sheet, `Tech`, `Parameter` and year column.
- `_LAC_HUB/cost_regional_20261111T050439Z/regional_proposals.csv`: 880 rows, same columns plus `tier, international_value, change_pct`, values in real 2024 USD. They override `proposals_all.csv` for the same country, sheet, Tech, Parameter and year.
- `_LAC_HUB/cost_src_cr_20261110T025401Z/structure_proposals.csv`: the Costa Rica coal fix (row with status "proposed").
- The six country job folders `_LAC_HUB/cost_src_{cr,dr,ecu,gua,hon,jam}_<stamp>/` hold `sources.csv`, `constants.csv`, `proposals.csv` and `paper_trace.csv`. `constants.csv` holds the CPI-U annual averages and the WEO 2025 price series each job used.

A-O layout: each energy model's `A1_Outputs/A-O_Parametrization.xlsx` has sheets "Primary Techs" and "Secondary Techs" with header `Tech.ID, Tech, Tech.Name, Parameter.ID, Parameter, Unit, Projection.Mode, Projection.Parameter`, then one column per year. Projection modes seen include "User defined", "Flat", "Zero", "EMPTY" and "Percent growth of incomplete years"; only "User defined" uses every year column as written.

Writer: `ao_cost_repair_manager.py apply --manifest <csv> --apply` edits only manifest cells, located by `sheet`, `row_index`, `tech`, `parameter` and `year`, checks `old_value`, can set `projection_mode_new`, makes a backup first and saves through `save_ao_safely`. Manifest columns are in `MANIFEST_FIELDS` in that file. Use it for the A-O_Parametrization writes.

Decisions (Luis, 8 to 11 November):

- D1. Base models take fuel rows with `fuel_scenario` STEPS and every row with ALL. CPS and NZE rows are not written; they are for Stage 4.
- D2. Regional overrides apply as in `regional_proposals.csv`, except Costa Rica `PWRHYDDAM` CapitalCost, which uses the national ICE value: R = capacity-weighted mean of ICE PEG 2024-2040 Tabla 10.9 overnight costs, Diquis 5,986 USD/kW (623 MW), RG-430 CM 360 6,317 (162 MW), RG-430 CM 318 5,910 (209 MW) = 6,023.966 USD/kW in December 2023 USD, times CPI-U 2024 over 2023 (313.689/304.702, the `constants.csv` CPI rows of the Costa Rica job, source CRC-001) = 6,201.639 USD/kW real 2024 USD. Write it by multiplying every year of the regional `PWRHYDDAM` CapitalCost path (5,100 at 2024, the Honduras value times the international index) by 6,201.639/5,100. Source ids: REG-005 (ICE PEG 2024-2040, PDF p.153 Tabla 10.9) and CRC-001.
- D3. Currency: every written value is real 2024 USD. Fuel rows already are. For each non-fuel group (country, Tech, Parameter) whose final values do not come from `regional_proposals.csv` or D2: find the currency year stated in its `derivation` or in its source's `sources.csv` entry. If the derivation already shows a CPI-U step to 2024, or the stated year is 2024, leave it. If a year Y before 2024 is stated, multiply every year of the group by CPI-U(2024)/CPI-U(Y), using the CPI-U annual averages in the country job's `constants.csv` (or another country job's, same BLS series CUUR0000SA0). If no year can be established, leave the values and list the group as a known limitation. Zero values stay zero. Record every group in `currency_conversion.csv` (country, Tech, Parameter, stated year, where stated, factor, or "left: reason").
- D4. Dominican Republic `EXTT_CRU` and `PRO_COA` VariableCost: priced at the written `DIST_CRU` and `DIST_COA` VariableCost path for every year (STEPS for projections). Checked by values: their activity upper limits in the A-O ("Estimado de los datos del INGEI 2022", `EXTT_CRU` 51.49 PJ in 2022) carry real flows, so they are not set to zero. Their rows switch to "User defined".
- D5. Ecuador `PPGEO` and `PPPVDS` keep their placeholder 1 (TotalAnnualMaxCapacity 0 every year). Do not touch them.
- D6. Ecuador coal fuel rows use the same WEO 2025 coal series the other five countries use (EU), in place of the Japan series: for each projected year y and WEO scenario, multiply the Ecuador value by [EU(y)/EU(2024)] / [JP(y)/JP(2024)], with both series taken from the `constants.csv` files. History years unchanged.
- D7. The gas sentence "divided by 0.9" is removed from the `assumption_sentence` of Jamaica and Dominican Republic natural gas rows whose value was never divided. This is text only, written into `assumptions_final.csv`.
- D8. A row whose written values vary by year and whose Projection.Mode is not "User defined" is switched to "User defined". A row in mode "Zero" or "EMPTY" that receives a non-zero value is switched to "User defined".
- D9. Costa Rica coal fix: `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Demand.xlsx`, sheet `Demand_Projection`, row 25 (Fuel/Tech `E5INDCOA`), column 2021 (cell M25): 0.675 to 0.00667 PJ (source CRC-006). Check the row label and the current value before writing; save through `save_ao_safely`.
- D10. Honduras `IMP_ELE`: proposals cover 2018 to 2024 only; the 2025 onward values (99999) stay untouched.
- D11. Costa Rica `IMPELE` VariableCost 57.2387 USD/GJ in every year, as in `proposals_all.csv`.

Pipeline facts:

- Energy model folders: `CostaRica/CR_ENERGY/t1_confection`, `DominicanRepublic/RD_ENERGY`, `Ecuador/ECU_Energy`, `Guatemala/GUA_ENERGY`, `Honduras/HON_ENERGY`, `Jamaica/JAM_ENERGY`. Each has several A2 and B1 script variants (for example `A2_Compiler.py` and `A2_Compiler_Jamaica.py`, `B1_Base_Scenarios_Adj_Parallel.py` and `B1_Base_Scenarios_Adj_Parallel_Jamaica.py`). Phase B decides which ones reproduce the tracked outputs.
- A2 writes `A2_Output_Params/<scenario>/*.csv`. B1 reads `B1_Scenario_Config.xlsx`, writes `B1_Output_Params/<scenario>/*.csv` and `Executables/<scenario>_0/<scenario>_0.txt`, solves with `glpsol`, and processes outputs. `Executables/` is gitignored, so the clone has none until B1 runs.
- Jamaica's tracked `A2_Output_Params` (12 May) carry 764 empty values that the safe-save fix of 9 November restored in the workbook, so Jamaica's recompiled A2 output will differ there even before any cost write. Jamaica `A2_Output_Params/NDCNEW` was written on 12 May by a script not yet traced.
- Stage commands, from `PIPELINE_WORKFLOW.md` (run from the clone root, Anaconda Python as `py`):
  - Stage 0: `py stage0_clean.py --confirm`, `py stage0_run.py`, `stage0_run_all.bat`, `py stage0_collect_outputs.py`, `py stage0_capacity_check.py`, `py stage0_recommend_shares.py`, `py stage0_test.py`.
  - Stage 1: `py stage1_share_analyzer_v16.py`, `py stage1_test_v16.py` (13 tests passed on 16 May).
  - Stage 2: `py stage2_apply_v2.py --root . --stage0-denom _STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx`, `py stage2_test_v2.py --stage0-denom _STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx` (7 of 7 hard tests passed).
  - Stage 3: `py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala`, `py stage3_test.py --root .`, `stage3_run_all.bat`, `py stage3_results.py --root .`.
- 16 May baseline: `_STAGE3_RESULTS/stage3_results.xlsx` (sheets TotalTechnologyAnnualActivity, AnnualEmissions, AnnualTechnologyEmission, NewCapacity, TotalCapacityAnnual, ProductionByTechnologyAnnual, ShareValidation): 18 of 18 optimal, RE targets 24 of 24, share validation 7,789 pass, 189 warn, 20 fail. Jamaica's 16 May Stage 3 used data files of 27 January.
- Each Stage 3 solve took 7 to 22 seconds in May. Solver output `.txt` files can exceed 700 MB each.

## 4. Setup

- Windows, Git Bash, Anaconda Python as `py`; run your own scripts with `py -I`. Microsoft Excel and pywin32 are required (A-O saves). Put `C:\glpk-4.65\w64` on PATH for the session if `glpsol` is not found.
- Clone: `git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_overnight`; in it run `git remote set-url origin https://github.com/luviga/clewise-lac.git`, `git fetch origin`, and create branch `job/cost-write-run` from `origin/main`. Check `origin/main` is `4124868`; if newer, branch from it and record the hash.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder: `_LAC_HUB/cost_write_run_<stamp>/` in the clone. Copy this brief into it.
- Check free disk space on C: at the start and record it. If below 80 GB at any point, delete solver output `.txt` files larger than 500 MB of a stage whose extraction step has already finished (they are regenerable and gitignored). Never delete anything else.
- Write only inside `/c/clw_overnight`. Read-only, never write: the main copy `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (you may read its `Executables/` for comparison), every other `C:\clw_*` clone, and anything under Dropbox `2_WORK`.
- Record the number of running `EXCEL.EXE` processes before Phase A. Never close a process you did not start.

## 5. Do and do not

Do: the steps of section 6, in order. Fix a pipeline script only when it cannot run in the clone because of a hard-coded folder path; make the smallest path-only edit, in its own commit, and list it in CHANGES.

Do not: run any A1 script (it rewrites the A-O workbooks); edit `OSeMOSYS_Model.txt`, any A2, B1 or stage script beyond a path-only fix, `B1_Scenario_Config.xlsx`, `_STAGE2_INPUTS/`, or any non-energy model; change controller rules or flags; add sources; run Stage 4; touch the paper files; tune anything to make a run feasible.

## 6. Work

### Phase A. Safe-save write order

A1. In `ao_safe_save.py`, change `save_ao_safely(wb, path)` (signature and `None` return kept): resolve the target; the temporary copy is `<stem>.safesave_tmp<suffix>` in the same folder; delete a leftover of that name if present and print a log line; `wb.save(tmp)`, `recalc_in_excel(tmp)`, `assert_no_blank_formula_cells(tmp)`; only then `os.replace(tmp, target)`. If any of these raises (including `BlankFormulaError`, a COM error, or `PermissionError` because the target is open), delete the temporary copy, leave the target untouched, and re-raise. Call the helpers through their module-level names. Update the docstring list. Nothing else in the module changes.

A2. In `test_ao_safe_save.py` keep the two tests and add three, each in its own temporary folder, each with a PASS line in `__main__`: (a) `test_excel_failure_leaves_target_unchanged` (target with plain values, SHA-256 recorded, `ao_safe_save.recalc_in_excel` replaced in try/finally by a function raising `RuntimeError`; the call raises; hash unchanged; no `*.safesave_tmp*` left); (b) `test_guard_failure_leaves_target_unchanged` (replacement does nothing; `BlankFormulaError`; hash unchanged; no temporary file); (c) `test_replace_existing_target` (real Excel; target exists; after the call `Primary Techs!C1` holds `=A1*B1+1` with stored value 7; no temporary file).

A3. Add two lines to `.gitignore` under "Backups and caches": `*.safesave_tmp.xlsx` and `/_LAC_HUB/**/backups/`.

A4. Gates: `py -I test_ao_safe_save.py` 5 of 5; `py -I -m unittest test_ao_cost_repair_manager -v` 4 of 4; the three writers (`ao_cost_repair_manager.py`, `Jamaica/JAM_ENERGY/apply_ao_edits.py`, `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py`) unchanged and each with one `save_ao_safely(` call. Logs in the job folder.

A5. Commit "Phase A: replace the A-O workbook only after the guard passes on a temporary copy". Push the branch and open one draft pull request titled "LAC_OVERNIGHT_COST_RUN: safe-save order, sourced costs, recompile and base re-runs"; update its body at the end from CHANGES.

### Phase B. Reproduce before changing

B1. For each of the six energy models, find the A2 compiler that reproduces the tracked `A2_Output_Params/{BAU,NDCNEW,LTSNEW}/*.csv` from the unchanged workbooks. Run candidates from the model folder. Compare keyed (parameter file and every index column, value to 1e-9 relative), never by hash or row order. Save each run's output to `baseline/<country>/A2/` in the job folder before trying another candidate, and restore the tracked files with `git checkout` between candidates. Expected: exact match everywhere except Jamaica's 764 restored values and anything you can explain the same way. Record in `pipeline_commands.csv` the chosen script and command per country and scenario, and in `baseline_A2_diff.csv` every differing value.

B2. Same for B1: find the runner that reproduces the tracked `B1_Output_Params/<scenario>/*.csv`, keyed. Where the main copy has `Executables/<scenario>_0/<scenario>_0.txt`, also compare your regenerated data file with it, parsed by parameter and index, not as text. Keep the regenerated `Executables/` (Stage 0 needs them). Record results in `pipeline_commands.csv` and `baseline_B1_diff.csv`.

B3. If no candidate reproduces a country, take the one with the fewest unexplained differences, mark the country "unverified" in PROGRESS and REPORT, and continue.

B4. Restore every tracked file changed during Phase B (`git status` clean outside the job folder). Commit the job folder ("Phase B: pipeline reproduction baseline").

### Phase C. Write the costs

C1. Build `write_set.csv` from section 3: ALL and STEPS rows of `proposals_all.csv`, overridden by `regional_proposals.csv`, then D2, D3, D4, D6 applied, in that order. One row per cell with country, sheet, Tech, Parameter, year, current workbook value, value to write, rule applied, source ids. Rows whose `change_class` is "keep" are written only if D3 changes them. Skip D5 and D10 cells. Count rows by country and rule.

C2. Locate each cell in the A-O workbook (sheet, `Tech`, `Parameter`, year column; record `row_index`). A proposal whose row or year column does not exist goes to `unplaced.csv` with the reason, not written. Build the manifest in the format `ao_cost_repair_manager.py` expects, with `approved` set and `projection_mode_new` per D8.

C3. Back up the six A-O workbooks and `A-O_Demand.xlsx` of Costa Rica into `backups/` in the job folder with a SHA-256 manifest. Run `ao_cost_repair_manager.py apply --manifest <manifest> --apply --output-dir <job folder>` country by country (check the option name in its `--help`), then `verify`. Write D9 with openpyxl and `save_ao_safely`.

C4. Gates: (1) every written cell equals `write_set.csv` to 1e-9 relative; (2) a cell-by-cell comparison of every sheet before and after (values and formula text) shows changes only at manifest cells, the Projection.Mode cells of D8 and cell M25 of D9; (3) zero formula cells without a stored value in every changed workbook; (4) the 20 other A-O workbooks (non-energy, reference copies) byte-identical. Write `write_check.csv`.

C5. Write `assumptions_final.csv` (every written row with an ASSUMPTION sentence, D7 applied) and `currency_conversion.csv`. Commit "Phase C: sourced costs written to the six energy A-O workbooks" (workbooks plus job folder files).

### Phase D. Recompile

D1. For each country run the Phase B commands: A2, then B1 (which also solves the three `_0` scenarios).

D2. Gate: keyed comparison against the Phase B baseline outputs. Allowed differences: CapitalCost, FixedCost and VariableCost of written cells; Costa Rica `SpecifiedAnnualDemand` for `E5INDCOA` in 2021 (and any parameter B1 derives directly from it, listed); Jamaica values explained in Phase B. Any other difference is a failure: find its cause; if it comes from the write, fix the write and redo C3 to D2; if you cannot explain it, record it and continue. Write `recompile_diff_summary.csv` (country, scenario, parameter, values changed, allowed yes or no).

D3. Record each B1 `_0` solve status (optimal, infeasible) and objective value. Commit A2 and B1 outputs ("Phase D: A2 and B1 recompiled with sourced costs"). Ignore `SelectedResults.csv` (last writer wins).

### Phase E. Stages 0 to 3

E1. Run Stage 0, 1, 2 and 3 with the commands of section 3, in order, each test included. A failing test does not stop the pipeline: record it, continue, and flag it. An infeasible solve is recorded, not tuned; continue with the other runs. Disk rule of section 4 applies.

E2. Compare with 16 May, writing `results_compare.csv` and a short table in REPORT, by country and scenario: solve status; objective value; RE share in 2030, 2035 and 2050 against target; share validation pass, warn, fail; new capacity by power technology summed over the horizon; total emissions in 2030 and 2050. List the five largest changes in new capacity per country.

E3. Recheck by values one known-limitation candidate: Guatemala `PPPVT` new capacity before 2025 in NDCNEW and LTSNEW (0.667 GW on 16 May, against 0.08 GW residual).

E4. Commit stage outputs (`_STAGE0_OUTPUT/`, `_STAGE1_OUTPUT/`, `_STAGE2_OUTPUT/`, `_STAGE3_RESULTS/`) and the job folder ("Phase E: base re-runs, Stages 0 to 3").

### Phase F. Final gates and pull request

F1. `git diff --name-only origin/main` shows only: Phase A files; the six energy A-O workbooks and Costa Rica `A-O_Demand.xlsx`; `A2_Output_Params` and `B1_Output_Params` of the six energy models; the four stage output folders; any path-only fix; the job folder. Nothing in non-energy models, `models_energy_RE_generation_costs_update/` or reference folders.
F2. No file larger than 50 MB staged; no `*.safesave_tmp*` file anywhere; `EXCEL.EXE` count equals the count at the start; `git diff --check` clean; no em dash in any tracked file you wrote; `git log origin/main..HEAD` has no `Co-Authored-By` and no "Generated with" line.
F3. Push, update the draft pull request body from CHANGES. A last commit only to write hashes into REPORT is allowed.

## 7. Outputs

All in the job folder, plain English, no em dashes, one UTC stamp.

`REPORT_LAC_OVERNIGHT_COST_RUN_<stamp>.md`: pull request number, base and commit hashes; per phase what ran, gate results with counts, durations; the canonical A2 and B1 commands; cells written by country and rule; the results comparison table; solve statuses; anything marked unverified or failed, first.

`GAPS_LAC_OVERNIGHT_COST_RUN_<stamp>.md`: every judgement call and its reason; "Known-limitation candidates"; anything left unchecked; incidents; groups left in their source currency year.

`CHANGES_LAC_OVERNIGHT_COST_RUN_<stamp>.md`: file or folder by file, what changed and why, two or three lines each.

Also in the job folder: `PROGRESS.md`, `pipeline_commands.csv`, `baseline_A2_diff.csv`, `baseline_B1_diff.csv`, `write_set.csv`, `unplaced.csv`, the manifest and apply logs, `write_check.csv`, `assumptions_final.csv`, `currency_conversion.csv`, `recompile_diff_summary.csv`, `results_compare.csv`, test logs. Backups stay untracked (`backups/` is gitignored from Phase A3).

Tracked files outside the job folder follow the repository's writing rules: no machine paths, no figures from model results in docs.
