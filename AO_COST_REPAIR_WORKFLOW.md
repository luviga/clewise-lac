# AO Cost Repair Workflow

This workflow repairs suspicious or missing energy costs in
`A1_Outputs/A-O_Parametrization.xlsx` through a reversible manifest process.

## Rules Implemented

- Plan first, edit later. `plan` only writes CSV review artifacts.
- Approved changes are stored cell by cell in `manifest.csv`.
- Workbook edits require `apply --apply`; otherwise apply is a dry run.
- Every real apply creates timestamped workbook backups.
- `restore` can copy backups from an apply log back to the original AO paths.
- Fuel `VariableCost` uses `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx`.
- Fuel workbook values are converted from `USD/PJ` to AO-style `MUS$/PJ` when needed.
- Ecuador `CapitalCost` and `FixedCost` use smart local matching first.
- Rows with no safe Ecuador local match are flagged for ATB or manual review.
- Review-required mappings are not applied unless explicitly approved.

## Ecuador Pilot

Create a dry-run plan:

```powershell
py ao_cost_repair_manager.py plan --country Ecuador
```

Review these files in the generated `_COST_REPAIR_OUTPUT/ao_cost_repair_*` folder:

- `summary.csv`: counts by source and decision.
- `manifest.csv`: approved cell-level proposed edits.
- `mapping_candidates.csv`: smart local source matches to review.
- `no_safe_match.csv`: rows held back for ATB/manual review.
- `run_config.json`: source files and options used.

Validate the approved manifest without editing:

```powershell
py ao_cost_repair_manager.py apply --manifest "_COST_REPAIR_OUTPUT\ao_cost_repair_YYYYMMDD_HHMMSS\manifest.csv" --dry-run
py ao_cost_repair_manager.py verify --manifest "_COST_REPAIR_OUTPUT\ao_cost_repair_YYYYMMDD_HHMMSS\manifest.csv" --expect original
```

Apply only after reviewing `manifest.csv`:

```powershell
py ao_cost_repair_manager.py apply --manifest "_COST_REPAIR_OUTPUT\ao_cost_repair_YYYYMMDD_HHMMSS\manifest.csv" --apply
py ao_cost_repair_manager.py verify --manifest "_COST_REPAIR_OUTPUT\ao_cost_repair_YYYYMMDD_HHMMSS\manifest.csv" --expect applied
```

Restore if needed:

```powershell
py ao_cost_repair_manager.py restore --apply-log "_COST_REPAIR_OUTPUT\ao_cost_repair_YYYYMMDD_HHMMSS\apply_YYYYMMDD_HHMMSS_apply_log.csv"
py ao_cost_repair_manager.py restore --apply-log "_COST_REPAIR_OUTPUT\ao_cost_repair_YYYYMMDD_HHMMSS\apply_YYYYMMDD_HHMMSS_apply_log.csv" --apply
```

## Tests

Run:

```powershell
py -m unittest test_ao_cost_repair_manager.py
```

The tests cover fuel workbook conversion, smart Ecuador matching, the charcoal
vs coal guard, and apply/verify behavior on a toy AO workbook.
