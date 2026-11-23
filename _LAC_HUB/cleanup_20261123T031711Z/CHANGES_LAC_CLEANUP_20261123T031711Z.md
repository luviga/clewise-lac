# CHANGES LAC_CLEANUP 20261123T031711Z

File by file, what changed and why. Commits in the order of the brief: code and tables; Guatemala Stage 2 and Stage 3; deletions; workbooks and labels; job folder. Results of each run are in the REPORT.

## Commit 1: code and tables

`CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py`, `DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py`, `Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py`
: F5. The region code appended to compiled rows is read from the country table (`LT.country_value(country, 'code')`) in place of the YAML key `appended_region_code`. The code of each country is unchanged, so every compiled file is equal.

`config/execution/Config_MOMF_T1_AB.yaml`
: F5. The three `appended_region_code` keys are removed; the country table holds the code once.

`stage3_results.py`
: F6. The RE target check reads each country's own `renewable_share` rows of `inputs/scenarios/scenario_values.csv` where it has them, else the general rows, the lookup that Stages 1 and 2 use. Costa Rica and Ecuador are now checked against their own targets; only the check lines of the log change.

`stage0_run.py`
: F7. The two loops over the bypass plants walk them in sorted order, so the order of the written rows no longer depends on set order. Membership is unchanged.

`PIPELINE_WORKFLOW.md`, `HANDOFF_STAGE4.md`
: NDCNEW and LTSNEW renamed NDC and LTS in text, commands and folder names, to match the scenario catalogue.

`test_ao_safe_save.py`, `test_ao_cost_repair_manager.py`
: Step 1. openpyxl 3.1.2 keeps a worksheet stream of a normal-mode load open until the next garbage collection, so on Windows the tests failed with a file lock when they replaced or removed a workbook. The test setup collects garbage after each load of the module under test and before a temp folder is removed. The modules under test are unchanged.

## Commit 2: Guatemala Stage 2 and Stage 3

`stage2_apply_v2.py`
: F2. When the frozen non-hydro renewables alone exceed the room that fossil and hydro leave, the branch scaled them down and set solar and wind to 0, which wrote share 0 and lower limit 0 for Guatemala BAU solar and wind in 2030 and 2031. The frozen plants and the solar and wind plants are now scaled together into that room, the Stage 1 gap-fill. The forward rebase and the policy enforcement held the same branch and get the same change. The 87 Jamaica PPBIM cases of the hole scan have another cause and are unchanged (GAPS).

`stage3_apply.py`
: The `--skip-orphan-cap` option is removed. Every country caps orphan plants at 0 from 2025 and gives zero-lower plants upper 0. A scenario listed for a country under `orphan_cap_exempt_scenarios` in the controller table keeps its orphan plants uncapped; the script names no country.

`config/scenarios/rules/stage_controller.csv`
: Step 4.5. New row `orphan_cap_exempt_scenarios` for Guatemala, NDC and LTS, with its reason: under the common rule these two scenarios have no feasible solution, and relaxing one limit group at a time showed that only the orphan cap binds. It stays until Luis decides.

`PIPELINE_WORKFLOW.md`, `HANDOFF_STAGE4.md`
: The Stage 3 command loses `--skip-orphan-cap Guatemala` in both files. The text that described the exception now states the common rule and the one table row, and the history section keeps its earlier explanation under a heading that says so.

## Commit 3: deletions

36 entries removed with `git rm`, 2,448 files, about 630 MB; each with its search result in `deletions.csv`. They are the Costa Rica `Blend_Shares_0.pickle` (F8), the F9 rows that no pipeline script reads, `models_energy_RE_generation_costs_update/` (F10), five `reference_*` folders and older script copies in the energy model folders. Eighteen candidates are kept because a script names them (GAPS).

`.gitignore`
: The four lines that named files inside `models_energy_RE_generation_costs_update/` are removed, with the heading and blank line of the section that held only one of them.

## Commit 4: workbooks and labels

All workbook writes go through `ao_safe_save.py`; `workbook_checks.csv` compares each edited workbook by key with the start commit and passes for all 13.

`CostaRica/CR_ENERGY/t1_confection/B1_Scenario_Config.xlsx`
: NDCNEW and LTSNEW renamed NDC and LTS in the description column of `Electrical`. The variant rows NDCNEW_stage_2 and LTSNEW_stage_2 are deleted by Excel, so every reference moves with the rows; the formula count is unchanged and every other cell is equal after the row map.

`Ecuador/ECU_Energy/B1_Scenario_Config.xlsx`, `Guatemala/GUA_ENERGY/B1_Scenario_Config.xlsx`, `Honduras/HON_ENERGY/B1_Scenario_Config.xlsx`, `Jamaica/JAM_ENERGY/B1_Scenario_Config.xlsx`
: NDCNEW and LTSNEW renamed NDC and LTS in the description column. The Dominican workbook held no old name and is unchanged.

`_STAGE2_INPUTS/STAGE2_OVERWRITES_CostaRica.xlsx`, `_DR.xlsx`, `_Ecuador.xlsx`, `_Guatemala.xlsx`, `_HON.xlsx`
: NDCNEW and LTSNEW renamed in note, rationale, method and scope text. Value cells unchanged. The Jamaica workbook held no old name.

`_STAGE2_INPUTS/STAGE2_OVERWRITES_CostaRica.csv`, `_Guatemala.csv`, `_HONDURAS.csv`
: The same renames in the note field (after the fifth comma); the first five fields of every line are unchanged.

`Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`
: `Other_Techs` A2 and A3: "NDP scenarios" renamed "NDC and LTS scenarios", the form of the other labels; these rows feed the policy folders.

`DominicanRepublic/RD_ENERGY/B1_Output_Params/NDC/TotalAnnualMinCapacity.csv`, `Guatemala/GUA_ENERGY/A2_Output_Params/NDC/TotalAnnualMinCapacity.csv`, `Guatemala/GUA_ENERGY/A2_Output_Params/LTS/TotalAnnualMinCapacity.csv`
: The Scenario column held NDCcond and NDP. No step writes these files, so they are the source of the label; the column now holds the folder's name and a recompile carries it. Every other field is unchanged.

The experiment-manager keys (F9) are left as they are.

## Commit 5: job folder

`_LAC_HUB/cleanup_20261123T031711Z/`
: PROGRESS, REPORT, GAPS and CHANGES; `baseline_against_main.csv`, `stage2_holes.csv`, `deletions.csv`, `workbook_checks.csv`; the job scripts (run, snapshot, gate, step edits, hole scan, relaxation, label scan) without the machine file and the solver wrapper that a run writes with machine paths; the step 1 test patch and the step 5 search tables. Run logs and tables of result figures stay local (GAPS).
