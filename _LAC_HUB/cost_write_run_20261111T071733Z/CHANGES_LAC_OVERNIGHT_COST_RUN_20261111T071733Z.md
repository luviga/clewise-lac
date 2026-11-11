# CHANGES LAC_OVERNIGHT_COST_RUN 20261111T071733Z

Branch `job/cost-write-run` from `origin/main` at `4124868`. File or folder by file, what changed and why.

## Phase A: safe-save write order

- `ao_safe_save.py`: `save_ao_safely(wb, path)` now saves to `<stem>.safesave_tmp<suffix>` in the target's folder, has Excel recalculate that copy, runs the blank-formula guard on it, and only then replaces the target with `os.replace`. On any error (guard, COM, `PermissionError`) the temporary copy is deleted, the target is left untouched and the error is re-raised. Signature, `None` return and the rest of the module are unchanged; the docstring list describes the new order.
- `test_ao_safe_save.py`: three tests added (Excel failure and guard failure leave the target byte-identical with no temporary file left; a real-Excel save over an existing target stores `=A1*B1+1` with value 7). Five tests, five PASS lines.
- `.gitignore`: `*.safesave_tmp.xlsx` and `/_LAC_HUB/**/backups/` added under "Backups and caches", so a leftover temporary copy and the job backups are never committed.

## Phase C: sourced costs in the A-O workbooks

- `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx`, `DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`, `Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, `Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`, `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`: 13,020 CapitalCost, FixedCost and VariableCost cells written from `write_set.csv` (reviewed proposals, regional overrides, decisions D2, D3, D4, D6, D8) with `ao_cost_repair_manager.py apply`, and 87 Projection.Mode cells switched to "User defined" (D8, D4). Saved through `save_ao_safely`; zero formula cells without a stored value.
- `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Demand.xlsx`: D9, `Demand_Projection!M25` (E5INDCOA, 2021) 0.675 to 0.00667 PJ, saved through `save_ao_safely`.
