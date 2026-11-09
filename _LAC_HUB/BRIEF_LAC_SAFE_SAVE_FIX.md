# BRIEF LAC_SAFE_SAVE_FIX: make A-O edits keep formula values, and repair the Jamaica and Ecuador workbooks

Working copy: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (the single keeper copy, not OneDrive synced). This is a local job. There is no GitHub clone and no pull request.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Do not run A2, B1, any stage, or the solver. Do not apply any cost edit.

## 1. Goal

Two things, in order.

First, give every script that writes an A-O workbook a save path that keeps formula results and a guard that refuses to leave a formula cell without a stored value, so a future cost edit cannot repeat the 12 May failure.

Second, repair the two workbooks that already lost their stored values, Jamaica and Ecuador, by recalculating them in Excel so the values come back while the formulas and the deliberate edits stay in place.

Decision taken by Luis on 8 November 2026: A-O edits recalculate through Excel on save, with a post-save guard, and the cost repair tool does not run in apply mode until the guard is in place. See the hub handover, section "Review of LAC_FORMULA_CHECK".

## 2. The standard

This job changes no sourced data value. It restores the results that existing formulas already define and adds a safety check, so it creates no new citation or ASSUMPTION. Keep every formula live: do not replace a formula with a number anywhere. The A-O workbook is the data authoring layer. Leave its structure and its formulas as they are and restore only the cached results.

Scope is frozen. Do only what section 5 lists. Anything new you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

## 3. Facts already checked by values (from LAC_FORMULA_CHECK 20261109T003529Z)

- Jamaica `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`: all 1,261 formulas lost their stored values on the 12 May `apply_ao_edits.py` save; 594 are in year columns. The intended value of every formula cell is in `_LAC_HUB/formula_check_20261109T003529Z/formula_cells.csv`, column `intended_value`. That job's evaluator matched Excel on all 4,453 cells it could cross-check in the four clean countries, so Excel recalculation is the authority here.
- Ecuador `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`: 990 formulas without stored values after the 14 May `patch_ao_ecuador_hydro.py` save; none are in year columns. That same patch deliberately replaced 451 year-column formulas with plain rule values; those are intended and must stay as numbers.
- Costa Rica, Dominican Republic, Guatemala, Honduras: all A-O formulas still hold stored values. Do not open these four workbooks for writing and do not change them.
- The existing backups predate the intended edits. Jamaica's `A-O_Parametrization.bak_20260511_171831.xlsx` is from before the 12 May edits, and Ecuador's `A-O_Parametrization_BACKUP_20260514_111921.xlsx` is from before the hydro patch. Do not restore from either backup; it would lose intended changes. Recalculate the current files instead.
- Microsoft Excel is installed (`C:\Program Files (x86)\Microsoft Office`, Office 15, Excel 2013). LibreOffice is not installed.
- The three scripts that open an A-O with openpyxl and save it: `Jamaica/JAM_ENERGY/apply_ao_edits.py` (load line 246, save line 286); `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py` (load line 132, save line 397); and `ao_cost_repair_manager.py` apply path (load line 1476, save line 1533). The first two are per country; `ao_cost_repair_manager.py` is at the MODELS_LAC_5 root.

## 4. Setup

- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Use it in the output folder and the three output file names. Call it `<stamp>`.
- Output folder: `_LAC_HUB/safe_save_fix_<stamp>/`. Write your scripts, logs and the three output files here.
- Backups folder: `_LAC_HUB/safe_save_fix_<stamp>/backups/`. Before changing any file, copy it here with its own name plus suffix `.pre_<stamp>`, and record its SHA-256.
- Run Python with `-I` for your own scripts. Install `pywin32` if it is not present (needed to drive Excel through COM); `xlwings` is an acceptable equivalent if already present.
- Write only inside: `_LAC_HUB/safe_save_fix_<stamp>/`; the two A-O workbooks named in steps 3 and 4; the three scripts named in step 2; and the new helper and test from step 1 (place them next to `ao_cost_repair_manager.py` at the root).
- Read-only, never write: every other file in MODELS_LAC_5, including the other four A-O workbooks, every `A2_Output_Params`, `B1_Output_Params` and `Executables` folder, and the `formula_check_20261109T003529Z` and `price_sources_20261109T003525Z` folders.

## 5. Work

### Step 1. Shared safe-save helper
Write `ao_safe_save.py` with three functions:
- `recalc_in_excel(path)`: open the workbook in Excel through COM with `Visible=False` and `DisplayAlerts=False`, force a full recalculation (`Application.CalculateFullRebuild`), save in the same xlsx format (FileFormat 51), close the workbook, and quit the Excel application cleanly even if an error is raised. This restores the cached result of every formula without changing the formula text.
- `assert_no_blank_formula_cells(path)`: open the workbook twice with openpyxl, once `data_only=False` and once `data_only=True`; for every cell that holds a formula, check that the data-only value is not None; return the count of blanks and a list of their sheet and cell references; raise `BlankFormulaError` if the count is not zero.
- `save_ao_safely(wb, path)`: save through the caller's normal openpyxl path, then call `recalc_in_excel(path)`, then `assert_no_blank_formula_cells(path)`.

Write `test_ao_safe_save.py`: build a tiny workbook with one arithmetic formula; save it with openpyxl only and assert `assert_no_blank_formula_cells` raises; then `recalc_in_excel` and assert it passes with zero blanks.

### Step 2. Wire the guard into the three writers
In `apply_ao_edits.py`, `patch_ao_ecuador_hydro.py` and `ao_cost_repair_manager.py` (apply path, around line 1533), replace the bare `wb.save(...)` call with `save_ao_safely(wb, path)` imported from `ao_safe_save.py`. Change nothing else in these scripts. Do not run them in this job.

### Step 3. Repair Jamaica
Back up `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` to the backups folder and record its SHA-256. Recalculate it with `recalc_in_excel`. Run `assert_no_blank_formula_cells` and expect zero. Then compare every formula cell's restored value against `intended_value` in `formula_check_20261109T003529Z/formula_cells.csv` for Jamaica, matching A2's rounding (numpy half-to-even at 4 decimals). Expect all 1,261 to agree. Record any cell that differs, with its formula, restored value and intended value. Do not hand-edit any cell.

### Step 4. Repair Ecuador
Same as step 3 for `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`. Expect zero blanks and all 990 formula cells to equal `intended_value`. The 451 deliberately replaced year cells are plain numbers, not formulas, so they are outside this check and must stay as they are.

### Step 5. Gates
1. Backups: the SHA-256 recorded before each change equals the backup copy's SHA-256.
2. Blank-formula guard: zero blank formula cells in the Jamaica and Ecuador workbooks after recalculation.
3. Intended-value check: Jamaica 1,261 of 1,261 and Ecuador 990 of 990 formula cells equal `intended_value`. Any mismatch is a failure: report it, do not declare the job done, and do not hand-edit the cell.
4. Hash gate: among the six A-O workbooks, only Jamaica and Ecuador changed; Costa Rica, Dominican Republic, Guatemala and Honduras keep the same SHA-256 as before. `find MODELS_LAC_5 -newer <first backup file> -type f`, excluding `_LAC_HUB/safe_save_fix_<stamp>/`, lists only the two workbooks and the files from steps 1 and 2.
5. The helper test passes.

Do not run A2, B1, any stage, or the solver. The current Jamaica `A2_Output_Params` and `B1_Output_Params` still carry the 764 empty values from 12 May. Leave them untouched; they are regenerated at the later re-run stage and must not be fed forward before then.

## 6. Outputs

All three in `_LAC_HUB/safe_save_fix_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_SAFE_SAVE_FIX_<stamp>.md`: what changed and why; for Jamaica and Ecuador, the blank count before and after and the intended-value check counts; the four other workbooks' SHA-256 before and after; gate results; the helper test result; whether Excel COM was available and used.

`GAPS_LAC_SAFE_SAVE_FIX_<stamp>.md`: every judgement call and its reason; any cell whose recalculated value differs from `intended_value`; "Known-limitation candidates"; anything left unchecked; incidents. If Excel COM cannot be driven, record it here, do not flatten any formula to a number as a substitute, and leave that workbook unrepaired for the hub to decide.

`CHANGES_LAC_SAFE_SAVE_FIX_<stamp>.md`: file by file, what changed and why, two or three lines each, covering the new helper and test and the three wired scripts and the two repaired workbooks.
