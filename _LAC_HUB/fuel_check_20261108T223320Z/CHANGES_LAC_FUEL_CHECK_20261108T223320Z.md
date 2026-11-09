# CHANGES LAC_FUEL_CHECK 20261108T223320Z

## Confirmation

- No A-O workbook, the fuel workbook or `ao_cost_repair_manager.py` changed. All 34 entries in `baseline_before.csv` and `baseline_after.csv` match on SHA-256, size and modification time. The gate was run twice; the second run came after all other work (`diff baseline_before.csv baseline_after.csv`, no output).
- The tool ran in `plan` mode only, six times, always with `--output-dir` inside this folder. It never ran in `apply`, `verify` or `restore` mode, and never with `--apply`, `--ignore-old-value-mismatch` or any write flag. No model or solver was run.
- No folder was created under `MODELS_LAC_5/_COST_REPAIR_OUTPUT/`. The listing before (`_cost_repair_output_listing_before.txt`) and after are identical.
- `find MODELS_LAC_5 -newer _LAC_HUB/BRIEF_LAC_FUEL_CHECK.md`, excluding this folder, returns only the directories `MODELS_LAC_5` (mtime 15:32:45 local, before this job's start at 15:33:20 local) and `_LAC_HUB` (15:33:20, the creation of this folder).
- `MODELS_LAC_5/__pycache__/ao_cost_repair_manager.cpython-312.pyc` still has its 2026-05-11 timestamp.
- One write outside the allowed area: the Git Bash file `/tmp/x`, a listing of `_COST_REPAIR_OUTPUT/` folder names, written by mistake and deleted in the next command. Details in GAPS.

## Created: folder

- `_LAC_HUB/fuel_check_20261108T223320Z/`: the only place this job wrote, apart from the `/tmp/x` slip above.

## Created: output documents

- `REPORT_LAC_FUEL_CHECK_20261108T223320Z.md`: gate results, short answer, and Steps 2 to 5.
- `GAPS_LAC_FUEL_CHECK_20261108T223320Z.md`: judgement calls, unread files, known-limitation candidates, and what was left unchecked.
- `CHANGES_LAC_FUEL_CHECK_20261108T223320Z.md`: this file.

## Created: required CSVs

- `baseline_before.csv`: Step 1 SHA-256, size and mtime of 34 files.
- `baseline_after.csv`: Step 6 repeat of Step 1.
- `fuel_coverage.csv`: country by fuel code by scenario year ranges, with the A-O rows that need each code and a status.
- `fuel_sources.csv`: source class and reason per anchor and parameter, with value counts per class.
- `fuel_plan.csv`: one row per country, A-O row, technology, parameter and year. Holds current, A2-compiled and planned values, ratios, and the workbook cell or internal source.

## Created: supporting CSVs and text

- `fuel_wb_sheets.csv`: fuel workbook sheets with size and formula counts.
- `fuel_wb_dump.txt`: text dump of every fuel workbook cell (value plus formula text).
- `ao_varcost_rows.csv`: every VariableCost row in the six main energy A-O workbooks with key values and gap flags.
- `ao_formula_cells.csv`: formula cell counts per A-O sheet.
- `ao_formula_summary.csv`: per A-O workbook, formula cells, formula cells without cached values, and planned cells that are formulas.
- `planned_formula_cells.csv`: the 26 Jamaica planned cells that hold formulas.
- `ao_fuel_supply_mapping.csv`: the fuel code the tool assigns to each `DIST_*`/`IMP*` row, and whether it targets the row.
- `fuel_values_classified.csv`: the class of each of the 4,524 `OSeMOSYS_VarCost` values, by its anchor and by its whole chain.
- `step3_5_dsl_hfo_ngs_REF.csv`: Step 3.5 table.
- `plan_summary.csv`: planned cells and rows by country, source kind, row class and parameter.
- `dsl_hfo_ngs_2025_2030.csv`: diesel, fuel oil and natural gas, 2025 and 2030, current versus planned.
- `unit_risks.csv`: planned to current ratio above 3 or below 1/3.
- `gap_rows.csv`: fuel supply rows that are empty, 0 or 1 today, and what the plan does with them.
- `_cost_repair_output_listing_before.txt`: listing of `_COST_REPAIR_OUTPUT/` before the dry runs.
- `plan_runs_console.txt`: the six plan commands and their console output.

## Created: tool dry-run output

- `plan_<Country>/` for CostaRica, DominicanRepublic, Ecuador, Guatemala, Honduras and Jamaica: `manifest.csv`, `mapping_candidates.csv`, `no_safe_match.csv`, `summary.csv` and `run_config.json`, written by `ao_cost_repair_manager.py plan`.

## Created: helper scripts (all read-only on model files)

- `baseline.py`: Steps 1 and 6 hashing.
- `fuel_wb_inspect.py`: first attempt at the sheet listing. It stopped on a console encoding error and was replaced by `fuel_wb_dump.py`. Kept for the record.
- `fuel_wb_dump.py`: Step 3.1 sheet sizes, formula counts and text dump.
- `ao_fuel_rows.py`: reads A-O VariableCost rows and formula counts.
- `build_fuel_plan.py`: Step 5 tables from the manifests.
- `formula_check.py`: formula cells and cached values in the A-O workbooks and planned cells.
- `build_coverage_sources.py`: Steps 3.3 and 3.4.
- `step3_5_table.py`: Step 3.5.
