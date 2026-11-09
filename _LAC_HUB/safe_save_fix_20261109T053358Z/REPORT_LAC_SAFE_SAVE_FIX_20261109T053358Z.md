# REPORT LAC_SAFE_SAVE_FIX 20261109T053358Z

Brief: `_LAC_HUB/BRIEF_LAC_SAFE_SAVE_FIX.md`. Stamp taken at start: `20261109T053358Z`. Output folder: `_LAC_HUB/safe_save_fix_20261109T053358Z/`.

## Result

All five gates pass. The Jamaica and Ecuador energy A-O workbooks have their formula results back, every formula is still live, and no plain value moved. The three A-O writers now save through Excel and refuse to finish if any formula cell is left without a stored value. No A2, B1, stage or solver was run, and no cost edit was applied.

## What changed and why

openpyxl writes formula text but never computes results. A workbook loaded with `data_only=False` and saved by openpyxl therefore loses every cached formula value, and A2 (which reads with `data_only=True`) sees empty cells. That is what happened to Jamaica on 12 May (`apply_ao_edits.py`) and to Ecuador on 14 May (`patch_ao_ecuador_hydro.py`).

1. New helper `ao_safe_save.py` at the MODELS_LAC_5 root, with `recalc_in_excel`, `assert_no_blank_formula_cells` (raises `BlankFormulaError`) and `save_ao_safely`. New test `test_ao_safe_save.py` beside it.
2. The bare `wb.save(...)` in `Jamaica/JAM_ENERGY/apply_ao_edits.py`, `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py` and `ao_cost_repair_manager.py` (apply path) is now `save_ao_safely(wb, path)`. The only other change in each is the import of the helper.
3. Jamaica and Ecuador workbooks recalculated in place by Excel. No cell was edited by hand. Neither backup from May was used.

## Excel COM

Available and used. Microsoft Excel 2013 was driven through pywin32 (already installed, Python 3.12) using a private hidden instance (`DispatchEx`, `Visible=False`, `DisplayAlerts=False`), `Application.CalculateFullRebuild`, `SaveAs` FileFormat 51, close, quit. No Excel process was left running after any step.

## Jamaica: `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`

| Check | Before | After |
|---|---|---|
| Formula cells | 1,261 | 1,261 (same cells, same formula text: 0 changed) |
| Formula cells without stored value | 1,261 | 0 |
| Plain (non-formula) cells | 14,136 | 14,136, 0 values changed |
| Formula cells showing an Excel error | n/a | 0 |
| Intended-value check (4 dp, half-to-even) | n/a | 1,261 of 1,261 agree, 0 mismatches |
| SHA-256 | `18f92a48b2bd41522a3dc5e7f3ad49e71194b008e0ac7bdd44871a0c2603e17f` | `592ceda73c6df758684a8a2fea20ac152db70f44ce6a4d65888274bfada16695` |

Recalculated at 2026-11-09T05:39:03Z. Detail: `jamaica_result.json`, `jamaica_intended_check.csv`, `jamaica_mismatches.csv` (header only), `jamaica_preservation_diffs.csv` (header only), `jamaica_run.log`.

## Ecuador: `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`

| Check | Before | After |
|---|---|---|
| Formula cells | 990 | 990 (same cells, same formula text: 0 changed) |
| Formula cells without stored value | 990 | 0 |
| Plain (non-formula) cells | 14,884 | 14,884, 0 values changed |
| The 451 deliberately flattened year cells (`step6_ecuador_451.csv`) | plain numbers | 451 of 451 still plain numbers, equal to their prior values |
| Formula cells showing an Excel error | n/a | 0 |
| Intended-value check (4 dp, half-to-even) | n/a | 990 of 990 agree, 0 mismatches |
| SHA-256 | `1d38bdefeb065c3369138240c7f6680e4042861b21306a5506abf82bc605315c` | `f1fb407a78848aaf7a9cffd6d771f2f3b507f0bc105366195e89089f03f6ff68` |

Recalculated at 2026-11-09T05:40:05Z. Detail: `ecuador_result.json`, `ecuador_intended_check.csv`, `ecuador_mismatches.csv` (header only), `ecuador_preservation_diffs.csv` (header only), `ecuador_run.log`.

## The four other energy A-O workbooks

Not opened for writing. Hashes from `ao_hashes_before.csv` and `gates_result.json`:

| Workbook | SHA-256 before | SHA-256 after |
|---|---|---|
| `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx` | `522d438ea7c27d4ceb3614267adff0503d059ecfe1a22d5d926bf7432dc9c8b7` | same |
| `DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | `f396abf1b587d337040735f945d0b7b2c7b4a47bf2c11e121753d8b5b7e4af7c` | same |
| `Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | `e2f9aad05f2b96c35392fb523e9bf056a9c71e067e564951b7770ac2e661e7f1` | same |
| `Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | `d20f4aa8d4c55aa384a8bd0f7a6c93fd5e635427eba8e9e705651b8638b40458` | same |

## Gates

| # | Gate | Result |
|---|---|---|
| 1 | Backups: SHA-256 before change equals backup copy | PASS, 5 of 5 (`backups/backup_manifest.csv`, rechecked in `gates_result.json`) |
| 2 | Zero blank formula cells after recalculation | PASS, Jamaica 0, Ecuador 0 |
| 3 | Intended-value check | PASS, Jamaica 1,261 of 1,261, Ecuador 990 of 990 |
| 4 | Hash gate | PASS. Of the six A-O workbooks only Jamaica and Ecuador changed. `find . -newer <first backup> -type f` (excluding this folder) lists only the two workbooks and the three wired scripts (`find_newer_first_backup.txt`); `find . -newer start_reference.marker` adds the new helper and test, 7 files in all (`find_newer_start.txt`). See GAPS for why two lists. |
| 5 | Helper test passes | PASS, 2 of 2 tests (`test_ao_safe_save.log`, rerun at the end in `test_ao_safe_save_final.log`) |

Extra check, not a gate: the existing `test_ao_cost_repair_manager.py` (works only in a temporary folder) passes 4 of 4 through the new save path (`test_ao_cost_repair_manager_after_wiring.log`).

## Backups

In `backups/`, each with suffix `.pre_20261109T053358Z`: `ao_cost_repair_manager.py`, `apply_ao_edits.py`, `patch_ao_ecuador_hydro.py`, `Jamaica_A-O_Parametrization.xlsx`, `Ecuador_A-O_Parametrization.xlsx`.

## Still open (unchanged by this job)

Jamaica `A2_Output_Params` and `B1_Output_Params` still carry the 764 empty values from 12 May. They were not touched and must be regenerated at the later re-run stage from the repaired workbook before anything is fed forward.

## Scripts in this folder

`backup.py` (copy plus SHA-256 manifest), `repair_workbook.py` (steps 3 and 4), `gates.py` (step 5), `start_reference.marker` (mtime set to the stamp time).
