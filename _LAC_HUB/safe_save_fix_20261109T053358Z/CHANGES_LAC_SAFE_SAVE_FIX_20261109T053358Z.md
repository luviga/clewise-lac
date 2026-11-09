# CHANGES LAC_SAFE_SAVE_FIX 20261109T053358Z

## `ao_safe_save.py` (new, MODELS_LAC_5 root)
Shared save path for A-O workbooks: `recalc_in_excel` (hidden private Excel, full rebuild recalculation, save as xlsx, always quits), `assert_no_blank_formula_cells` (raises `BlankFormulaError` listing sheet and cell of each formula without a stored value) and `save_ao_safely` (openpyxl save, then Excel recalculation, then the guard). Stops a repeat of the 12 May and 14 May losses.

## `test_ao_safe_save.py` (new, MODELS_LAC_5 root)
Builds a one-formula workbook, shows an openpyxl-only save is refused by the guard, then shows `recalc_in_excel` restores the value (7) with zero blanks and the formula text unchanged; also runs `save_ao_safely` end to end. Passes 2 of 2.

## `ao_cost_repair_manager.py` (root)
Apply path: `wb.save(ao_path)` (was line 1533, now 1536) replaced by `save_ao_safely(wb, ao_path)`; one import of the helper added after the openpyxl import. The cost repair tool can no longer write an A-O without stored formula values. Backup: `backups/ao_cost_repair_manager.py.pre_20261109T053358Z`.

## `Jamaica/JAM_ENERGY/apply_ao_edits.py`
`wb.save(args.ao_file)` (was line 286, now 289) replaced by `save_ao_safely(wb, args.ao_file)`; one import of the helper (with a path to the root) added. This is the script that caused the Jamaica loss. Backup: `backups/apply_ao_edits.py.pre_20261109T053358Z`.

## `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py`
`wb.save(ao_path)` (was line 397, now 400) replaced by `save_ao_safely(wb, ao_path)`; one import of the helper (with a path to the root) added. Its "GROUP 4" flattening logic is unchanged. Backup: `backups/patch_ao_ecuador_hydro.py.pre_20261109T053358Z`.

## `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`
Recalculated and saved by Excel through `recalc_in_excel`. Formula cells without stored values went from 1,261 to 0; all 1,261 restored values equal `intended_value`; formula text and all 14,136 plain values unchanged. Backup: `backups/Jamaica_A-O_Parametrization.xlsx.pre_20261109T053358Z`.

## `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`
Recalculated and saved by Excel through `recalc_in_excel`. Formula cells without stored values went from 990 to 0; all 990 restored values equal `intended_value`; formula text and all 14,884 plain values unchanged, including the 451 deliberately flattened year cells. Backup: `backups/Ecuador_A-O_Parametrization.xlsx.pre_20261109T053358Z`.
