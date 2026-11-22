# BRIEF LAC_STRUCTURE_TABLES: every value and name of the stage pipeline in external tables, scenarios renamed BAU, NDC and LTS, results unchanged

Repository: https://github.com/luviga/clewise-lac, `main` at `b51f24b` (pull request #13 merged on 21 November 2026). No open pull request.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, try it at least three different ways, record the block, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge. Commits and pull requests carry no co-author line and no mention of an AI tool.

This is a long job with three full runs of the pipeline. It is restartable: keep `PROGRESS.md` in the job folder up to date after every step. If you start and the job folder already exists, read `PROGRESS.md` and continue from the first step that is not marked done. Never make a second clone, stamp or job folder.

## 1. Goal

Luis decided on 21 November 2026 that no value of the system may live in a script: every number and every name of a country, scenario, technology, fuel or emission sits in an external table, in the folder layout of https://github.com/Climate-Lead-Group/OSTRAM. He also decided that the scenarios are called BAU, NDC and LTS in every model.

This job does the first half of that work for the six energy models and the stage pipeline. It moves the values and names out of the code into tables, and it renames the scenarios. It changes no value. The compiled inputs and the solved results after the job equal those before it. Moving folders into the OSTRAM layout is the next job and is not part of this one.

## 2. The standard

The models run only on externally sourced values, values a rule computes every run from sourced inputs, and labelled ASSUMPTIONs. This job changes no value and adds no source and no ASSUMPTION sentence. The tables it creates hold the values exactly as the code holds them today. The job that follows (LAC_ALIGN) replaces them with the published values and writes their sources.

Scope is frozen. Do only what section 5 lists. Anything new you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

Do not:
- change any number that reaches a model, in a workbook, a CSV or a table;
- edit any `OSeMOSYS_Model.txt`;
- move, rename or delete a folder other than the scenario folders named in Phase C;
- touch the sector models (`*_AFOLU`, `*_IPPU`, `*_WASTE`, `JAM_TRANSPORT`, `ECU_AGR` and the like), `models_energy_RE_generation_costs_update/`, `_COST_AUDIT_OUTPUT/`, `_COST_REPAIR_OUTPUT/`, or any earlier `_LAC_HUB/` job folder;
- merge the six A2 compilers or the six B1 scripts into one.

## 3. Facts already checked by values (hub 12, at `b51f24b`)

F1. The tree of `b51f24b` equals `a76ad81` plus the folder `_LAC_HUB/ndc_verify_20261121T233937Z/`. Models, scripts, compiled inputs and stage outputs are those of `a76ad81`.

F2. `_LAC_HUB/ndc_verify_20261121T233937Z/script_constants.csv` lists 11,170 values and names written in code. 1,977 rows have `stage0_3_results_depend` = `yes`. They sit in 32 files: the six `B1_Base_Scenarios_Adj_Parallel*.py` (229, 226, 211, 149, 140 and 116 rows), `stage2_apply_v2.py` (115), `stage1_share_analyzer_v16.py` (105), `stage3_run_all.bat` (61), `stage0_run.py` (57), `stage3_results.py` (55), `stage3_apply.py` (50), `stage0_collect_outputs.py` (46), the six `A2_Compiler_*.py` (196 together), `stage0_recommend_shares.py` (36), `stage0_capacity_check.py` (24), `stage2_post_clean.py` (19), `stage0_run_all.bat` and `.sh` (15 each), `stage0_clean.py` (12), `ao_safe_save.py` (3), and the six energy copies of `OSeMOSYS_Model.txt` (97 together). By kind: 1,221 numbers, 248 scenario names, 131 technology names, 110 country codes, 107 country names, 74 fuel names, 64 emission names, 22 name prefixes. Column `move_to` names a target table for each row.

F3. The renewable targets are typed twice with the same content, in `stage1_share_analyzer_v16.py` lines 97 to 110 and `stage2_apply_v2.py` lines 61 to 75: NDCNEW 0.75 in 2035 and 0.75 in 2050; LTSNEW 0.75 and 0.99; Costa Rica NDCNEW 0.90 and 0.90, LTSNEW 0.99 and 0.99; Ecuador NDCNEW 0.80 and 0.80, LTSNEW 0.80 and 0.99; `TARGET_HOLD_YEAR = 2050`.

F4. `_LAC_HUB/ndc_verify_20261121T233937Z/scenario_names.csv` finds 12 scenario names in the repository: BAU, NDCNEW and LTSNEW (the three in use), and NDC, LTS, NDCcond, NDCincond, NDP, NDPAMB, NDCINC, LTSOPT and Default. The names NDC and LTS are therefore already taken by older scenarios. `Honduras/HON_ENERGY/B1_Scenario_Config.xlsx` holds 263 cells with NDCcond. In `_LAC_HUB/cost_write_run_20261111T071733Z/pipeline_commands.csv`, the Dominican Republic A2 step for NDCNEW and LTSNEW copies the files the compiler writes to `A2_Output_Params/NDCcond`. An old name can therefore feed a scenario in use.

F5. The six energy copies of `OSeMOSYS_Model.txt` are two different models. Costa Rica, Honduras, the Dominican Republic, Ecuador and Jamaica hold the same 577 lines (two files that differ only in line endings). Guatemala holds a different file of 743 lines.

F6. The last full run is on `main`: 18 of 18 Stage 3 solves OPTIMAL, with objectives in `_LAC_HUB/fix_run2_20261120T225823Z/stage_logs/solves_stage3.jsonl`; results in `_STAGE3_RESULTS/stage3_results.xlsx`; compiled inputs in each model's `A2_Output_Params/<scenario>/` and `B1_Output_Params/<scenario>/`. Solver run folders (`Executables/`) are ignored by git.

F7. The exact commands of the pipeline are in `_LAC_HUB/cost_write_run_20261111T071733Z/pipeline_commands.csv` and `PIPELINE_WORKFLOW.md`. The rules that earlier runs needed are in section 5 of `_LAC_HUB/fix_run2_20261120T225823Z/BRIEF_LAC_FIX_RUN2_v2.md` and are repeated in section 4 below.

## 4. Setup

- Windows, Git Bash. Anaconda Python (3.12.4, pandas 2.2.2) for the pipeline, as in `pipeline_commands.csv`. python.org Python with `py -I` for your own scripts. Microsoft Excel and pywin32 for workbook saves, always through `ao_safe_save.py`. `glpsol` 4.65 at `C:\glpk-4.65\w64`.
- New clone `/c/clw_struct` from GitHub. Branch `job/structure-tables` from `origin/main` at `b51f24b`.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder `_LAC_HUB/structure_tables_<stamp>/`. Copy this brief into it.
- Write only inside `/c/clw_struct` and `/c/clw_struct_base` (the baseline snapshot, outside the clone).
- Read-only, never write: the main copy `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5`, `C:\clw_fix`, `C:\clw_scout`, `C:\clw_scout_model`, `C:\clw_scout_venv`, `C:\Users\luisfernando\Desktop\OSeMOSYS\LAC_sources_archive`, anything under Dropbox `2_WORK` and OneDrive.
- Background tasks: at most two at a time. Check every value a background task reports in its file before you use it.
- Write scripts and text with the file tool. Never use shell heredocs.
- Record free disk on C: at the start. A full run writes about 27 GB of solver output. Below 80 GB free, delete solver output `.txt` files over 500 MB of a stage whose extraction has finished. Nothing else.
- Record the number of `EXCEL.EXE` processes before work. Never close one you did not start.
- Every full run starts from a clean `git status` for tracked files, so that every run starts from the same inputs. Commit or restore before a run.
- Rules carried from the earlier runs: call batch files by full path (`NoDefaultCurrentDirectoryInExePath=1`); no `glpsol.bat` wrapper on PATH during stage runs; absolute log paths in solve wrappers; Guatemala A2 through `_LAC_HUB/cost_write_run_20261111T071733Z/scripts/run_with_append_shim.py`; Costa Rica B1 with a temporary `A2_Output_Params/LTSOPT` (a copy of the long-term scenario) and an empty `B1_Output_Params/LTSOPT`, removed afterwards; the A2 driver restores `A1_Outputs` with `git checkout`, so stage every workbook change before a recompile; run `test_ao_cost_repair_manager` through `unittest discover` and `test_ao_safe_save.py` with its own runner; workbook write checks compare by key, never by row number.

## 5. Work

### Phase A. Baseline, no change

A1. With the untouched code, recompile A2 and B1 for the six countries and run Stages 0 to 3 with every test, as in `pipeline_commands.csv` and `PIPELINE_WORKFLOW.md`. Keep the logs in the job folder under `stage_logs/baseline/`.

A2. Copy the compiled inputs, the stage outputs, the 18 objectives and the test results of this run to `/c/clw_struct_base`. This snapshot is the baseline of every gate below.

A3. Compare the baseline with what `main` tracks (F6): compiled inputs cell by cell with a key of parameter, technology, fuel, emission, mode and year; stage outputs cell by cell; the 18 objectives. Write every difference to `baseline_against_main.csv` with both values. Zero differences is the expected result. If there are differences, do not chase them: they are reported, and the gates use the baseline snapshot.

A4. Restore the tracked files to `b51f24b` (`git checkout -- .`), so Phase B starts clean.

### Phase B. Values and names into tables (pull request 1)

B1. Create the tables, in the OSTRAM folder names, at the repository root. Use the `move_to` column of `script_constants.csv` as the plan:
- `config/preparation/Config_country_codes.yaml`: country name, code, model folder, name of each country's A2 and B1 script;
- `config/scenarios/scenario_catalogue.csv`: scenario name, role, folder names;
- `config/scenarios/rules/stage_controller.csv`: controller settings (anchor and cutoff years, decline rates, tolerances, hold year);
- `config/scenarios/technology_types.csv`: technology groups and name prefixes;
- `inputs/scenarios/scenario_values.csv`: the targets of F3, with columns `country, scenario, lever, lever_kind, year, value, unit`. `lever_kind` is `share of generation` for every row of this job. The column exists so that a later job can load a capacity target without a code change;
- `config/compilation/` and `config/execution/`: one YAML per stage for the numbers of the A2 and B1 scripts, with a section per country where they differ;
- fuel and emission label tables beside the technology table.
A country value that equals the general value is still written per country only where the code does so today.

B2. Write one small loader module at the repository root that reads these tables. Replace every literal of the 32 files (F2) by a read through it. The scripts keep their names, their places and their logic. Batch and shell files take their country and scenario lists from the loader.

B3. The six `OSeMOSYS_Model.txt` copies stay byte for byte as they are. Their 97 rows remain in the list and are reported.

B4. Write `tables_register.csv` in the job folder: one row per value or name moved, with table, key, value, old file, old line and kind (system value, controller setting, unit conversion, name). The tables themselves carry no source column yet.

B5. Gates of Phase B:
1. Rerun `_LAC_HUB/ndc_verify_20261121T233937Z/scripts/f1_scan_code.py` on the branch (copy it into the job folder first and point it at the clone). Expected: no row with `stage0_3_results_depend` = `yes` outside the six model files. A constant of the mathematics or of presentation may stay only if it is in `script_constants_accepted.csv` or you add it to an accepted list in the job folder with its reason.
2. Recompile A2 and B1. Compiled inputs equal the baseline cell by cell. Allowed differences: none.
3. Run Stages 0 to 3 with every test. 18 of 18 OPTIMAL. Objectives, stage outputs and `stage3_results.xlsx` equal the baseline. Test results equal the baseline list of passes and failures.
4. `git diff --name-only origin/main` lists only: the 26 code files of F2, the new tables, the loader, test files, and the job folder. No workbook differs from `b51f24b`. A compiled input or a stage output differs from `b51f24b` only where `baseline_against_main.csv` already shows that difference.
5. `git diff --check` is clean.
Any other difference is a failure: find its cause and fix it in the branch. If you cannot, report it and do not open the pull request for this phase.

B6. Commit "LAC_STRUCTURE_TABLES: values and names of the stage pipeline in external tables". Push. Open draft pull request 1 with that title, base `main`, body taken from CHANGES.

### Phase C. Scenarios renamed (pull request 2, stacked on 1)

Scope: the six energy model folders and the stage pipeline at the root. Branch `job/structure-rename` from the head of `job/structure-tables`.

C1. Write `rename_plan.csv`: every place in scope where one of the 12 names of F4 occurs (code, tables, folder names, workbook sheets, workbook cells, tracked outputs), with one action:
- `rename`: NDCNEW becomes NDC, LTSNEW becomes LTS;
- `retire`: the older NDC and LTS, NDCcond, NDCincond, NDP, NDPAMB and NDCINC;
- `keep`: BAU, LTSOPT, and generic uses of the word Default.
Where a retired name feeds a scenario in use (F4), re-point the feed to the scenario in use and keep the data. The label goes and the values stay.

C2. Retire first. Remove the retired scenario folders, sheets, rows and code branches in scope. Gate: recompile A2 and B1; the compiled inputs of BAU, NDCNEW and LTSNEW equal the baseline cell by cell. Commit "retire older scenario names".

C3. Then rename, through `config/scenarios/scenario_catalogue.csv`, `git mv` for tracked folders, and `ao_safe_save.py` for workbooks. A workbook change touches only cells that hold a scenario name. Check every changed workbook by key against its state before: every other cell equal, formulas kept.

C4. Gates of Phase C:
1. Recompile A2 and B1, then run Stages 0 to 3 with every test. With the mapping NDCNEW to NDC and LTSNEW to LTS, compiled inputs, the 18 objectives, stage outputs and `stage3_results.xlsx` equal the baseline. Allowed differences: scenario names only.
2. A scan of the scope finds only BAU, NDC, LTS and LTSOPT as scenario names. Occurrences outside the scope are listed in `names_left.csv` with counts and are not changed.
3. Tests give the baseline list of passes and failures. Where a test names a scenario, it reads the catalogue.
4. `git diff --check` is clean.
If a country cannot pass gate 1 after the rename, put that country back to its state after C2, record the cause with values, and finish the others.

C5. Commit the renamed tracked outputs of the final run with the code. Push. Open draft pull request 2 titled "LAC_STRUCTURE_TABLES: scenarios renamed BAU, NDC, LTS", base `job/structure-tables`, body taken from CHANGES.

## 6. Outputs

All three in the job folder, plain English, no em dashes.

`REPORT_LAC_STRUCTURE_TABLES_<stamp>.md`: first, anything failed, blocked or pending. Then pull request numbers and commit hashes; the baseline against `main` (count and size of differences); the tables created, with row counts; the count of rows moved against the 1,977 of F2; every gate with its counts; the 18 objectives at baseline, after Phase B and after Phase C; tests run; run times of each full run.

`GAPS_LAC_STRUCTURE_TABLES_<stamp>.md`: every judgement call and its reason; "Known-limitation candidates"; anything left unchecked; incidents; what the next job (the OSTRAM layout) needs to know, including the two different model files of F5 and every place where the six country scripts differ in logic.

`CHANGES_LAC_STRUCTURE_TABLES_<stamp>.md`: file by file, what changed and why, in two or three lines each.

Tracked files follow the repository's writing rules: no machine paths, no figures from model results, no hash values.
