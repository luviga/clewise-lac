# CHANGES LAC_FORMULA_CHECK 20261109T003529Z

All files below were created by this job in `_LAC_HUB/formula_check_20261109T003529Z/`. No file was edited, moved, renamed or deleted anywhere else in MODELS_LAC_5.

## Reports
- `REPORT_LAC_FORMULA_CHECK_20261109T003529Z.md`: gate results, short answer, and Steps 2 to 7.
- `GAPS_LAC_FORMULA_CHECK_20261109T003529Z.md`: judgement calls, incidents, known-limitation candidates, items left unchecked.
- `CHANGES_LAC_FORMULA_CHECK_20261109T003529Z.md`: this file.

## Data files
- `baseline_before.csv`: Step 1 read-only baseline (A-O hash, size, mtime; file count, size, newest mtime of A2_Output_Params, B1_Output_Params, Executables).
- `baseline_after.csv`: the same, taken at the end; identical to the before file in all 24 rows.
- `formula_cells.csv`: every formula cell in the six main A-O workbooks, with formula, stored value, own evaluation and intended value (Steps 2 and 3).
- `formula_vs_compiled.csv`: each formula cell against the A2 output per scenario, classified ok, blank-filled, different or not checked (Step 4).
- `downstream_follow.csv`: blank-filled Jamaica cells traced into B1_Output_Params and the BAU, NDCNEW and LTSNEW data files (Step 4).
- `timeline.csv`: modification times of the A-O workbook, A2 and B1 scenario folders and data files, per country (Step 4).
- `empty_values_scan.csv`: empty Value and empty TECHNOLOGY counts in every A2 and B1 output CSV (supports Steps 4 and 5).
- `affected_rows.csv`: row-level mismatches between intended and compiled values, by year, with B1 and data-file values (Step 5).
- `affected_rows_summary.csv`: per A-O row, the number of formula cells and of years compiled wrongly (Step 5).
- `step5_jamaica_rows.csv`: Jamaica affected rows grouped by parameter and technology, used for the Step 5 lists.
- `step2_summary_country.csv`, `step2_summary_by_sheet.csv`, `step2_summary_by_parameter.csv`: Step 2 count tables.
- `step4_summary.csv`: Step 4 class counts per country and scenario.
- `step6_backups.csv`: formula and stored-value counts and document properties of the Jamaica and Ecuador A-O workbooks and their backups (Step 6).
- `step6_ecuador_451.csv`: what became of each of the 451 year-column formulas in Ecuador's pre-patch backup (Step 6).
- `scratch_a2_loop_jamaica.txt`: extract of the A2 parametrization loop, used to diff the six compilers (first written to the session scratchpad, then moved here).
- `scratch_py_files_naming_ao.txt`: list of the 73 `.py` files naming `A-O_Parametrization` (first written to the session scratchpad, then moved here).

## Helper scripts (all read-only on model files; run with `py -I`)
- `baseline.py`: writes a baseline CSV (Step 1 and gate 1).
- `inspect_headers.py`: prints sheet names, dimensions, header rows and document properties of each A-O.
- `step2_3_inventory_eval.py`: formula inventory and evaluator; writes `formula_cells.csv`.
- `step4_compare.py`: A2 replica and comparison with A2 outputs; writes `formula_vs_compiled.csv`.
- `step4b_downstream.py`: B1 and data-file follow-up and timeline; writes `downstream_follow.csv` and `timeline.csv`.
- `empty_values_scan.py`: writes `empty_values_scan.csv`.
- `step5_effect.py`: row-level effect; writes `affected_rows.csv` and `affected_rows_summary.csv`.
- `summaries.py`: builds the Step 2, Step 4 and Step 5 summary tables.
- `step6_backups.py`: writes `step6_backups.csv`.
- `step6_ecuador_451.py`: writes `step6_ecuador_451.csv`.

No recalculated workbook copies were made, because LibreOffice is not installed.

## Confirmation that nothing outside the output folder changed
- Gate 1: `baseline_after.csv` equals `baseline_before.csv` in all 24 rows: the A-O SHA-256 for all six countries, and file counts, sizes and newest mtimes of A2_Output_Params, B1_Output_Params and Executables.
- `find MODELS_LAC_5 -newer baseline_before.csv -type f`, leaving out this folder and the concurrent job's `price_sources_*` folder, returned no files.
- Outside MODELS_LAC_5: one empty file, `C:\Users\luisfernando\AppData\Local\Temp\x.py`, was created by mistake and deleted at once. Two helper files were written to the Claude session scratchpad and moved into this folder. Details are in GAPS under "Breaches and incidents during the run".
