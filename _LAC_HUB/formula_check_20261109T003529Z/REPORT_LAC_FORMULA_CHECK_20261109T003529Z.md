# REPORT LAC_FORMULA_CHECK 20261109T003529Z

Job folder: `_LAC_HUB/formula_check_20261109T003529Z/` (all paths below are relative to `MODELS_LAC_5/` unless they are file names in this folder). Stamp taken at start with `date -u +%Y%m%dT%H%M%SZ`.

## Gate results

1. **Read-only gate: PASS.** `baseline_before.csv` and `baseline_after.csv` (both written by `baseline.py`) have 24 rows each: six A-O workbooks (SHA-256, size, mtime) plus file count, total size and newest mtime of `A2_Output_Params/`, `B1_Output_Params/` and `Executables/` for six countries. A row-by-row comparison found 0 differences (command shown in the run log: merge on country and item, compare file_count, size_bytes, mtime_utc_newest, sha256).
2. **Nothing written outside the job folder: PASS for MODELS_LAC_5, with two exceptions outside it, both reported in GAPS.** Inside MODELS_LAC_5, every file I created is in this folder (listed in CHANGES). Outside MODELS_LAC_5: (a) a mistyped command created an empty file `C:\Users\luisfernando\AppData\Local\Temp\x.py`, which I deleted at once; (b) two helper text files went into the Claude session scratchpad and were then moved into this folder (`scratch_a2_loop_jamaica.txt`, `scratch_py_files_naming_ao.txt`). No model file was touched (gate 1).
3. **Traceability: PASS.** Every number below comes from a CSV in this folder or from a file, line or command named next to it.

## Short answer

| Country | Formula cells (none stored) | Reached the compiled model wrongly? | Reached the Stage 3 data files of 16 May? |
|---|---|---|---|
| Costa Rica | 1,508 (0) | No. 530 year cells ok in each of BAU, NDCNEW and LTSNEW; 115 Vehicle Techs cells not checked; 863 Tech.ID cells not read by A2 | No |
| Dominican Republic | 2,109 (0) | No. 1,484 year cells ok per scenario; 1 not checked; 624 Tech.ID cells not read by A2 | No |
| Ecuador | 990 (990) | No. None of the 990 sits in a year column: 958 are Tech.ID cells, which A2 never reads, and 32 are Tech-name cells on rows with `Projection.Mode = EMPTY`, which A2 does not write | No |
| Guatemala | 883 (0) | No. 586 year cells ok per scenario; 283 Vehicle Techs cells not checked; 14 notes cells | No |
| Honduras | 480 (0) | No. 179 year cells ok per scenario; 250 cells on the `growth_formula` sheet, which A2 drops (`A2_Compiler_Honduras.py:408`); 2 on Zero rows; 49 Tech.ID | No |
| **Jamaica** | **1,261 (1,261)** | **Yes.** All 594 year-column formula cells were blank-filled in `A2_Output_Params/BAU`, `NDCNEW` and `LTSNEW` (12 May). Five of the 40 rows are Flat with a formula in the base year, which blanks all 35 years: **764 compiled year values are empty** in each scenario, and the same 764 are empty in `B1_Output_Params/BAU` and `NDCNEW` | **No.** The data files that Stage 3 copied were written on 27 January, before the bad save. They hold the intended value in 763 of 764 BAU cases. |

**Most serious effects (in the 12 May A2/B1 outputs for Jamaica, not yet in any solver run):** the refinery activity bounds for REF_DSL, REF_GSL, REF_LPG, REF_FOI and REF_JET (lower bound 2021-2055, upper bound 2024-2055) and the run-of-river lower bound PPHROR would fall to the data-file defaults (lower 0, upper 99999); STOELE CapitalCost (816), the ELE_TRANS and ELE_DIST FixedCost (4.5085) and DIST_COA VariableCost (1.5143) would become free in all 35 years; ResidualCapacity for TM_HOU, PPFOI and PPDSL would become 0; PPWNDON CapacityFactor 2023-2055 would default to 1 instead of 0.3042. The default values are from `Jamaica/JAM_ENERGY/Executables/BAU_FINAL_0/BAU_FINAL_0.txt` (`param ... default` lines 64, 186, 561, 1421, 1839, 1873, 1916).

**How it happened:** `Jamaica/JAM_ENERGY/apply_ao_edits.py` opened the workbook with `load_workbook(args.ao_file)` (line 246) and saved it with `wb.save(args.ao_file)` (line 286) at 2026-05-12 00:18:31Z. Its own backup, `A-O_Parametrization.bak_20260511_171831.xlsx`, still has all 1,261 formulas with stored values; the saved file has none (`step6_backups.csv`). Ecuador's workbook was last saved by `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py` (`load_workbook` line 132, `wb.save` line 397) at 2026-05-14 18:19:22Z. Its backup `A-O_Parametrization_BACKUP_20260514_111921.xlsx` has 1,441 formulas, all with stored values. That script replaced the 451 year-column formulas with plain numbers on purpose (its "GROUP 4", lines 241-308) and left 990 formulas without stored values.

**Is the 16 May Stage 3 sound with respect to this defect?** Yes, for all six countries: no blank formula cell reached a `*_FINAL_0.txt` file. This is not a clean bill for Jamaica, though. Its Stage 3 data files come from `*_0.txt` files dated 27 January (`timeline.csv`), so they cannot contain anything edited in the A-O since then, including the 12 May `apply_ao_edits.py` changes. One cell shows the gap: PPPVT 2025 lower bound is 0.5468 by today's formula but 1.4103 in `BAU_0.txt`. This is outside the frozen scope and is listed in GAPS as a known-limitation candidate.

**Fix I would choose:** for Jamaica, recalculate and save the workbook in Excel (option A in Step 7). Then check every recalculated value against `intended_value` in `formula_cells.csv`. My evaluator agreed with Excel's own stored values on all 4,453 cells it could check in the other four countries. Then rerun A2, B1 and Stages 0 to 3 for Jamaica. Ecuador needs no rerun for this defect, but a recalculate-and-save removes the latent risk. For every country, add a guard to every script that saves an A-O workbook (option D) before `ao_cost_repair_manager.py` is run in apply mode. Its apply path (`ao_cost_repair_manager.py:1476` load, `:1533` save) would strip the stored values from all 4,980 formula cells in Costa Rica, the Dominican Republic, Guatemala and Honduras. That is the same failure as Jamaica's, at four times the size.

## Step 2. Formula inventory

Method: `step2_3_inventory_eval.py` opens each main `A1_Outputs/A-O_Parametrization.xlsx` with openpyxl twice (`data_only=False` and `data_only=True`, read-only mode) and writes one line per formula cell to `formula_cells.csv`: sheet, cell, row, column header, year, Tech, Parameter, Projection.Mode, formula, stored value, plus Step 3 fields. Summary tables: `step2_summary_country.csv`, `step2_summary_by_sheet.csv`, `step2_summary_by_parameter.csv` (built by `summaries.py`).

| Country | Formula cells | Without stored value | In year columns | In other columns |
|---|---|---|---|---|
| Costa Rica | 1,508 | 0 | 645 | 863 Tech.ID |
| Dominican Republic | 2,109 | 0 | 1,485 | 624 Tech.ID |
| Ecuador | 990 | 990 | 0 | 958 Tech.ID, 32 Tech |
| Guatemala | 883 | 0 | 869 | 14 "Source / Assumption" |
| Honduras | 480 | 0 | 431 (250 of them on `growth_formula`) | 49 Tech.ID |
| Jamaica | 1,261 | 1,261 | 594 | 667 Tech.ID |

The totals and the no-stored-value counts agree with `fuel_check_20261108T223320Z/ao_formula_summary.csv`.

By sheet (`step2_summary_by_sheet.csv`):
- Costa Rica: Primary Techs 434, Vehicle Techs 341, Secondary Techs 334, Fixed Horizon Parameters 296, Demand Techs 99, Transport Fuel Distribution 3, Other_Techs 1.
- Dominican Republic: Secondary Techs 1,264, Primary Techs 529, Fixed Horizon Parameters 314, Vehicle Techs 2.
- Ecuador: Primary Techs 390, Demand Techs 230, Fixed Horizon Parameters 220, Secondary Techs 150.
- Guatemala: Primary Techs 598, Vehicle Techs 285.
- Honduras: growth_formula 250, Secondary Techs 117, Primary Techs 113.
- Jamaica: Secondary Techs 411, Demand Techs 323, Fixed Horizon Parameters 314, Primary Techs 213.

By parameter, year columns only (`step2_summary_by_parameter.csv`):
- Costa Rica: CapacityFactor 159, ResidualCapacity 145, CapitalCost 109, TotalTechnologyAnnualActivityLowerLimit 102, FixedCost 56, TotalAnnualMaxCapacity 48, TotalTechnologyAnnualActivityUpperLimit 26.
- Dominican Republic: TotalTechnologyAnnualActivityLowerLimit 550, CapacityFactor 354, TotalTechnologyAnnualActivityUpperLimit 331, TotalAnnualMaxCapacity 213, ResidualCapacity 28, FixedCost 5, CapitalCost 4.
- Ecuador: none.
- Guatemala: ResidualCapacity 522, CapacityFactor 314, TotalAnnualMaxCapacity 26, CapitalCost 3, FixedCost 2, VariableCost 2.
- Honduras: ResidualCapacity 91, CapacityFactor 53, TotalAnnualMaxCapacity 24, VariableCost 10, CapitalCost 3, and 250 on growth_formula (no Parameter column).
- Jamaica: TotalTechnologyAnnualActivityLowerLimit 249, TotalTechnologyAnnualActivityUpperLimit 183, CapitalCost 44, ResidualCapacity 39, CapacityFactor 33, VariableCost 26, FixedCost 12, TotalAnnualMinCapacityInvestment 8.

The brief's examples are confirmed for Jamaica: `=AL4` on DIST_DSL VariableCost 2051-2055, and DIST_COA 2021 `=53*1000000000/(1000000000*35)` (`formula_cells.csv`). The Ecuador example `=J207*0.98` does not exist in today's workbook, which has no year-column formulas. It may have been among the 451 year formulas that the hydro patch removed (see Step 6).

## Step 3. Intended values

LibreOffice is not installed (`which soffice` found nothing, and there is no LibreOffice folder under Program Files). So I used route 2: a small evaluator in `step2_3_inventory_eval.py` that handles numbers, `+ - * / ^ %`, parentheses and same-sheet cell references, followed recursively. A formula that is a single reference to a text cell returns the text, which covers Ecuador's `=+B155` tech names. Anything else is "not evaluated" with a reason. Where the evaluator fails but Excel left a stored value, `intended_value` is the stored value, with method "stored value". Columns in `formula_cells.csv`: `own_eval_value`, `own_eval_equals_stored`, `intended_value`, `intended_method`, `not_evaluated_reason`.

| Country | Own evaluator | Stored value used (functions such as AVERAGE, SUM, MAX) | Not evaluated |
|---|---|---|---|
| Costa Rica | 1,294 | 214 | 0 |
| Dominican Republic | 2,053 | 56 | 0 |
| Ecuador | 990 | 0 | 0 |
| Guatemala | 626 | 257 | 0 |
| Honduras | 480 | 0 | 0 |
| Jamaica | 1,261 | 0 | 0 |

**Validation:** wherever both exist (4,453 cells in Costa Rica, the Dominican Republic, Guatemala and Honduras), the evaluator's result equals Excel's stored value in every case (`step2_summary_country.csv`, column `own_eval_equals_stored`). All Ecuador and Jamaica formulas fall inside the evaluator's grammar, so every formula cell has an intended value.

## Step 4. What the model received

Method (`step4_compare.py`): for each formula cell, the script rebuilds the A-O row as A2 reads it (`pd.ExcelFile(...).parse(sheet)`, the same call as `A2_Compiler_Jamaica.py:418`). It then runs a replica of A2's per-row logic twice, once with the intended values and once with the formula cells empty. The replica follows `A2_Compiler_Jamaica.py:514-602` and the write rule at line 792, whose loop matches `A2_Compiler_Ecuador.py` (diffed with `diff -w`). It covers Flat (base-year value for all years), Percent growth of incomplete years, User defined (round each year to 4 decimals), Interpolate to stated end value, and the modes A2 does not write (`EMPTY`, `Zero`, `According to demand`, blank; `A2_Compiler_Jamaica.py:792`). The compiled value is matched in `A2_Output_Params/<scenario>/<Parameter>.csv` on TECHNOLOGY and YEAR. Rounding is numpy's, as in A2, because pandas hands A2 `numpy.float64` values: for example, 0.41705 rounds to 0.417.

What A2 produces for an empty cell: in User defined mode, `round(NaN, 4)` stays NaN and A2 writes the row with an empty Value. In Flat mode an empty base-year cell blanks every year of the row. Interpolate and Percent-growth rows would be filled from neighbours. No Jamaica or Ecuador formula sits on such a row; elsewhere only 2 Guatemala cells do, and they have stored values. Jamaica's 594 year formulas are on 589 User defined cells and 5 Flat cells. B1 then skips any input row whose Value is empty (`B1_Base_Scenarios_Adj_Parallel_Jamaica.py`, line 2174: `if row[header_row[-1]] != None and row[header_row[-1]] != ''`). The data file therefore falls back to the parameter's `default`.

Results (`formula_vs_compiled.csv`, `step4_summary.csv`):

| Country | ok (per scenario BAU / NDCNEW / LTSNEW) | blank-filled | different | not checked |
|---|---|---|---|---|
| Costa Rica | 530 / 530 / 530 | 0 | 0 | 863 Tech.ID; 114 Vehicle Techs (A2 unit conversion not replicated); 1 Other_Techs row with no compiled match |
| Dominican Republic | 1,484 / 1,484 / 1,484 | 0 | 0 | 624 Tech.ID; 1 Vehicle Techs row in mode "User defined trajectory relative to BY" |
| Ecuador | none in year columns | 0 | 0 | 958 Tech.ID; 32 Tech cells on EMPTY rows (A2 reads them as NaN and writes no row) |
| Guatemala | 586 / 586 / 586 | 0 | 0 | 283 Vehicle Techs; 14 notes cells |
| Honduras | 179 / 179 / 179 | 0 | 0 | 250 growth_formula; 2 Zero rows; 49 Tech.ID |
| Jamaica | 0 | **594 / 594 / 594** | 0 | 667 Tech.ID |

A first pass showed 83 Dominican Republic cells as "different" by 0.0001. These were rounding ties (0.41705), which A2 rounds half-to-even through numpy. After matching A2's rounding they are ok. The `Default` scenario folders hold header-only CSVs for these parameters, and Guatemala's Default folder has no such files, so every Default comparison is "not checked: no matching compiled row".

Supporting scan (`empty_values_scan.py`, `empty_values_scan.csv`): Jamaica has 764 empty-Value rows in each of `A2_Output_Params/BAU`, `NDCNEW` and `LTSNEW`, and in `B1_Output_Params/BAU` and `NDCNEW`; 594 of them are formula cells. The other 170 come from the five Flat rows whose base-year cell is a formula (5 rows × 34 extra years). No compiled CSV in any country has an empty TECHNOLOGY. Empty values that have nothing to do with formulas exist in the Dominican Republic (365 per scenario), Guatemala (66 per scenario) and Ecuador NDCINC (30); see GAPS.

**Timing** (`timeline.csv`, `baseline_before.csv`):

| Country | A-O workbook mtime | Newest A2_Output_Params file | Which came last |
|---|---|---|---|
| Costa Rica | 2025-09-23T22:54:20Z | 2025-09-25T07:38:02Z | A2 |
| Dominican Republic | 2025-12-10T17:23:53Z | 2025-12-10T17:24:25Z | A2 |
| Ecuador | 2026-05-14T18:19:22Z | 2026-05-14T18:19:57Z (BAU, NDCINC) | A2, 35 s after the save without stored values |
| Guatemala | 2025-12-26T23:22:53Z | 2025-12-26T23:27:54Z | A2 |
| Honduras | 2025-12-10T17:22:20Z | 2025-12-10T17:22:46Z | A2 |
| Jamaica | 2026-05-12T00:18:32Z | 2026-05-12T00:20:28Z (BAU, NDCNEW, LTSNEW) | A2, 2 min after the save without stored values |

**One step further, Jamaica** (`step4b_downstream.py` → `downstream_follow.csv`; `step5_effect.py` → `affected_rows.csv`). Data files read: `Executables/<SCEN>_FINAL_0/<SCEN>_FINAL_0.txt`, which exists for all three scenarios, with `<SCEN>_0.txt` read alongside.

| | BAU | NDCNEW | LTSNEW |
|---|---|---|---|
| B1_Output_Params value for the 594 formula cells | empty in 594 (written 2026-05-12T00:20:28Z) | empty in 594 (same time) | present in 594 (written 2026-01-27T08:23:33Z); equals intended in 503 |
| `<SCEN>_0.txt` (written 2026-01-27) equals intended | 593 of 594 | 503 of 594 | 503 of 594 |
| `<SCEN>_FINAL_0.txt` (2026-05-16) equals intended | 511 of 594 | 501 of 594 | 501 of 594 |
| Data-file entry missing (default applied) | 0 | 0 | 0 |

All FINAL-file mismatches are TotalTechnologyAnnualActivityLower/UpperLimit on PP technologies (PPBIM, PPDSL, PPFOI, PPHDAM, PPHROR, PPNGS, PPPVT). In BAU they are all years 2025 and later. That is exactly what `stage3_apply.py` patches (docstring lines 3-10: PP-prefix techs, years ≥ 2025), so they are not caused by the formulas. In NDCNEW and LTSNEW, a further 91 cells already differ in `_0.txt`, all on the same PP limit rows. Inference: these are B1's scenario-specific adjustments, not formula effects. The single BAU cell that differs in `_0.txt` is PPPVT 2025 lower bound: intended 0.5468 today, 1.4103 in `BAU_0.txt`. Its formula's inputs changed after January.

So in Jamaica the blanks reached `A2_Output_Params` and `B1_Output_Params` but **not** `Executables`. Stage 3 copied `<SCEN>_0` to `<SCEN>_FINAL_0` (`stage3_apply.py:559-588`), and those `_0.txt` files predate the bad save. Ecuador's data files were rebuilt after its save (`BAU_0.txt` 2026-05-14T18:20:32Z) but carry no formula effect, because no formula feeds a compiled value. The other four countries had no blank-filled or different cells, so there was nothing to follow.

## Step 5. Size of the effect

Only Jamaica is affected, and only in the 12 May `A2_Output_Params` and `B1_Output_Params` (BAU and NDCNEW; LTSNEW in A2 only). Per row (`step5_jamaica_rows.csv`, one line per parameter and technology; years 2021-2055, values are the intended compiled values; every listed year is empty in A2 BAU and B1 BAU):

**Costs** (CapitalCost, FixedCost, VariableCost; 218 empty year values)
- CapitalCost: LCM_HOUSE 2023-2055, 70,986.6393; STOELE 2021-2055 (Flat), 816; PPWNDONS 2051-2055, 3,158.4785; PPPVDS 2051-2055, 2,068.0329.
- FixedCost: ELE_TRANS and ELE_DIST 2021-2055 (Flat), 4.5085 each; PPWNDONS 2051-2055, 68.2120; PPPVDS 2051-2055, 40.4796.
- VariableCost: DIST_COA 2021-2055 (Flat), 1.5143; DIST_DSL 22.4135, DIST_GSL 19.3404, DIST_LPG 21.5598, DIST_FOI 14.6004, DIST_KER 13.8175, all 2051-2055.
- Effect: with the value missing, the data-file default applies, which is 0 for CapitalCost, FixedCost and VariableCost in `BAU_FINAL_0.txt`. Storage capacity, transmission and distribution, coal supply in every year, and the main liquid fuels after 2050 would cost nothing. The solver would favour them, and system cost would be understated (inference).

**Capacity and activity bounds** (TotalTechnologyAnnualActivityLower/UpperLimit, TotalAnnualMinCapacityInvestment; 474 empty year values)
- Lower limits: REF_DSL, REF_GSL, REF_LPG, REF_FOI, REF_JET 2021-2055; PPHROR 2021-2055; PPHDAM 2021-2055 (Flat, 0.4884); PPBIM 2024-2055; PPDSL 2021-2024; PPFOI 2025; PPPVT 2025.
- Upper limits: REF_DSL, REF_GSL, REF_LPG, REF_FOI, REF_JET 2024-2055; PPBIM 2021-2040; PPFOI 2025; PPNGS 2027; PPPVT 2027.
- STOELE TotalAnnualMinCapacityInvestment 2030-2037, 0.0625.
- Effect: a missing lower limit defaults to 0, so refinery output, hydro and biomass generation are no longer forced. A missing upper limit defaults to 99999, so refineries and PPBIM can grow without limit. The planned storage build of 0.0625 a year from 2030 to 2037 disappears.

**Residual capacity** (39 empty year values): TM_HOU 2022-2055 (0.88 to 1.7714), PPFOI 2022-2026 (0.0765 to 0.1395), PPDSL 2023 (0.055). Effect: the default of 0 removes existing capacity. The model must build it new, or meet the demand some other way.

**Other** (33 empty year values; CapacityFactor): PPWNDON 2023-2055, 0.3042, would default to 1. Onshore wind would look more than three times as productive.

**Demand:** no formula cell touches demand.

Because none of these 764 values reached a data file, the 16 May Stage 3 solution is unaffected. They would all reach the solver the next time B1 is rerun for Jamaica from the current A2 outputs. Inference: B1 would then write the data file without these entries, as described in Step 4.

## Step 6. How it happened

Search: of the 73 `.py` files outside `_LAC_HUB` and `__pycache__` that name `A-O_Parametrization` (list in `scratch_py_files_naming_ao.txt`), four both call `load_workbook` and call `.save(`:

| File | Lines | What it changes | File date (UTC) |
|---|---|---|---|
| `Jamaica/JAM_ENERGY/apply_ao_edits.py` | 246 `load_workbook(args.ao_file)`; 207 writes cells; 286 `wb.save(args.ao_file)`; 74-78 backup `*.bak_<stamp>.xlsx` | Year-column values of matching (Tech, Parameter) rows in "Primary Techs", from an edits workbook (default `JAM_AO_BAU_edits.xlsx`) | 2026-05-12T00:01:47Z |
| `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py` | 132 `openpyxl.load_workbook(ao_path)`; 397 `wb.save(ao_path)`; 127 backup `*_BACKUP_<stamp>.xlsx` | Hydro ResidualCapacity and MinCapacityInvestment; "GROUP 4" (241-308) replaces every year-column formula in "Primary Techs": lower limits flattened to the first numeric value, upper limits and MaxCapacity set to 9999, other formula cells set to the first numeric value | 2026-05-14T18:18:00Z |
| `ao_cost_repair_manager.py` | 1476 `load_workbook(ao_path, data_only=False)`; 1533 `wb.save(ao_path)` | Cost cells and Projection.Mode from an approved manifest, in apply mode only | 2026-05-12T04:03:02Z |
| `test_ao_cost_repair_manager.py` | 29, 41 save test workbooks it builds itself | Test fixtures only, not A-O files | 2026-05-12T04:03:09Z |

A1 scripts write the A-O with xlsxwriter (for example `Ecuador/ECU_Energy/A1_Model_Structure_Energy.py:1498`). That produces values only, with no formulas, so it cannot cause this defect.

Evidence for the last saves (`step6_backups.py` → `step6_backups.csv`):
- **Jamaica:** `apply_ao_edits.py` most likely did it. Its backup `A-O_Parametrization.bak_20260511_171831.xlsx` is stamped 2026-05-11 17:18:31 local, which is 2026-05-12 00:18:31Z. The workbook's mtime is 00:18:32Z and its document property `modified` is 00:18:31. The backup has 1,261 formulas, all with stored values; the current file has the same 1,261, none with a stored value. The current file's `creator` is "openpyxl" while the backup's is empty: openpyxl fills an empty creator on save. A2 ran two minutes later (00:20:28Z).
- **Ecuador:** `patch_ao_ecuador_hydro.py` most likely did it. Its backup `A-O_Parametrization_BACKUP_20260514_111921.xlsx` is stamped 11:19:21 local, which is 18:19:21Z, one second before the workbook's mtime of 18:19:22Z. The backup has 1,441 formulas with stored values, 451 of them in year columns; the current file has 990, none stored, none in year columns. Cell by cell (`step6_ecuador_451.py` → `step6_ecuador_451.csv`), all 451 former year formulas are now plain numbers. Only 29 equal the formula's last stored value. The other 422 were changed by the patch's rule: CapacityFactor 143, lower limits 138, upper limits 132, TotalAnnualMaxCapacity 9. An earlier backup `..._BACKUP_20260513_215823.xlsx`, identical in size and mtime, shows a first run on 13 May. Inference: that run was undone with `patch_ao_ecuador_hydro_UNDO.py` before the second one.
- `ao_cost_repair_manager.py` did not save any A-O. Both apply logs in `_COST_REPAIR_OUTPUT/` (`apply_20260511_210105_apply_log.csv`, `apply_20260511_210630_apply_log.csv`) are Ecuador runs with `dry_run=YES`.

The mechanism is general: openpyxl keeps formula text but writes no stored results, and pandas reads stored results only. Any `load_workbook(path)` followed by `save` on a workbook that contains formulas leaves every formula blank for A2.

## Step 7. Fix options (none applied)

**A. Recalculate and save each workbook in Excel or LibreOffice.**
- What it changes: stored values come back for every formula cell; the formulas stay.
- Risks: Excel recalculates against today's inputs, so a formula whose inputs were edited gives a new result. That is the intended behaviour, and it is what `intended_value` already shows. Excel may also touch formatting and document properties. LibreOffice is not installed. Microsoft Office is (`C:\Program Files (x86)\Microsoft Office\`, "Microsoft Office 15"; inference: Excel 2013).
- Check afterwards: re-run `step2_3_inventory_eval.py`, expect 0 cells without a stored value, and expect `own_eval_equals_stored` to be True everywhere.
- Needed for: Jamaica (1,261 cells, 594 that matter). Advisable for Ecuador (990 cells, none that matter today).

**B. Replace formulas by their values.**
- What it changes: each formula becomes a number, for example `intended_value` from `formula_cells.csv`, written into a copy that is then checked and swapped in.
- Risks: the logic is lost, for example REF_FOI lower bound = 0.98 × another row, or DIST_* 2051-2055 = the 2050 value. Later edits to the source row no longer propagate. Needs care with numpy-style rounding ties. Ecuador's hydro patch already did this for 451 cells, but with its own rule values instead of the formula results.
- Needed for: an alternative to A for Jamaica.

**C. Make A2 evaluate formulas, or at least refuse empty formula cells.**
- (C1) Guard: before parsing, A2 opens the A-O with openpyxl in both modes and stops if any formula cell in a column it reads has no stored value. The change is small, carries no risk to results, and would have stopped the 12 May Jamaica run.
- (C2) Evaluate: compute formulas inside A2 with an evaluator like `step2_3_inventory_eval.py` (covers 100% of the Ecuador and Jamaica formulas) or a library such as `formulas` or `pycel`, which would have to be installed. The risk is that the evaluator's grammar falls short: it would miss AVERAGE, SUM and MAX in Costa Rica (214), the Dominican Republic (56) and Guatemala (257). Every A2 compiler (six variants) would need the change.

**D. Write future edits with a method that keeps stored values.**
- Options: edit through Excel itself (xlwings or COM, which recalculates on save); or after any openpyxl save, run a headless recalculation of the file; or write values only into rows that hold no formulas and refuse to save a workbook with formulas.
- Minimum: add a post-save check (count formula cells without a stored value; must be 0) to `apply_ao_edits.py`, `patch_ao_ecuador_hydro.py` and `ao_cost_repair_manager.py` (apply path, lines 1469-1537).
- Needed for: all six countries before the next cost edit. This matters most for the four countries that are clean today and would lose stored values on their first openpyxl save: Costa Rica 1,508 cells, the Dominican Republic 2,109, Guatemala 883, Honduras 480.

**What to rerun afterwards:**
- Jamaica: after A or B, run A2, then B1, then Stages 0 to 3. The current `A2_Output_Params` and `B1_Output_Params` (BAU, NDCNEW) carry 764 empty values each and must not be fed to B1's data-file writer as they are. Separately, the Stage 3 data files lack every A-O change since 27 January (see GAPS).
- Ecuador: nothing has to be rerun for this defect. Inference: a recalculate-and-save that changes no value leaves A2 output unchanged.
- Costa Rica, Dominican Republic, Guatemala, Honduras: nothing to rerun. Put D in place before any edit.
