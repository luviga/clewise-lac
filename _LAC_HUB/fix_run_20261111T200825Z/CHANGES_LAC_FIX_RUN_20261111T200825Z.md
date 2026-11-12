# LAC_FIX_RUN: review fixes of PR #10, recompile and base re-runs

Job LAC_FIX_RUN, stamp 20261111T200825Z, base `main` at c42ae07 (PR #10). It applies the seven fixes decided on 11 November 2026 when reviewing PR #10, recompiles A2 and B1 for the six energy models, and re-runs Stages 0 to 3 once. Every value enters through a data file; `OSeMOSYS_Model.txt` is unchanged. The full account is in `_LAC_HUB/fix_run_20261111T200825Z/`: `REPORT_LAC_FIX_RUN_20261111T200825Z.md` (gates, checks, results), `GAPS_LAC_FIX_RUN_20261111T200825Z.md` (judgement calls, corrections, limitation candidates) and `proposals.csv` (one row per written cell, with source ids and derivation).

## What changed

**R1. Three unexplained formulas replaced by sourced values.**
- Guatemala `DIST_FLEXFUEL` VariableCost (Primary Techs row 284, now User defined): the CEPEA/ESALQ hydrated-ethanol indicator (Sao Paulo, ex-mill) per GJ in real 2024 USD for 2018 to 2024, then the 2024 value moved with the `DIST_GSL` path (ASSUMPTION: Brazilian hydrated ethanol as the price of the flex fuel).
- Honduras `PPBGS` CapitalCost 2018 to 2020: IRENA 2012 biogas Case 10, 5,053 USD/kW in 2010 USD, in 2024 USD.
- Dominican Republic `ELE_TRANS` CapitalCost 2018: the ETED 2021-2035 transmission investment (467.89 million USD) per PJ/yr of the 2035 peak demand over 8,760 hours, in 2024 USD (ASSUMPTION: 2019 USD and 8,760 hours).

**R2. Costa Rica 2021 industry coal.** `E5INDCOA` 2021 = 0.00667 PJ in the four config rows that override it (MINAE energy balance 2022, Tabla 3).

**R3. Ecuador crude balance and prices.**
- Exports stay a demand (`E5EXPCRU`): BCE exports 2021 to 2025, BCE outlook 2026 to 2030; later years unchanged (no outlook found, listed in `sources_pending.csv`).
- `EXTT_CRU` activity limits from BCE field production (upper = production, lower = 0.98 x production), never above the 2025 level.
- `DIST_CRU` lower limit 0 in every year; upper limit unchanged except 2021 and 2022, opened to 999,999 because the refinery input lower limit cannot be met without imports in those years (GAPS item 31).
- Prices: `EXTT_CRU` VariableCost = the former `DIST_CRU` path (export value); `T5CRUEXP` VariableCost = minus that path (new Demand Techs row 203); `DIST_CRU` VariableCost = Brent (EIA) on the WEO 2025 STEPS path in real 2024 USD.

**R4. Dollar year of the 109 cost groups PR #10 left unconverted.** Each group takes the dollar year its source states (or, where none is stated, an ASSUMPTION of the year before publication) and is converted to real 2024 USD with CPI-U annual averages. `currency_conversion.csv` is updated.

**R5. Source values over old values kept inside sourced paths.** The 304 matched cells take the source value in 2024 USD (14 cells already held PR #10 regional values and were left); three Ecuador hydro rows take the CCG kit large-hydro value. `starter_kit_deviations.csv` lists every CCG Ecuador kit value the model does not take as published.

**R6. Same history in every scenario.** NDCNEW and LTSNEW take BAU's 2018 to 2024 values in `B1_Scenario_Config.xlsx`: the history part of their activity limits and capacity caps, new history-only rows for limits only BAU had, and BAU's calibrated history emission factors. Values from 2025 on are unchanged, except that the Dominican Republic and Ecuador B1 round the new emission-factor rows to four decimals (at most 0.00005). Exceptions where BAU history would make a policy scenario infeasible against its own caps from 2025 are listed in `r6_not_applied.csv`. Transport adoption history is not aligned (GAPS item 37).

**R7. Jamaica run-of-river hydro.** `PPHROR` minimum investments follow the 2022 IRP's 34.3 MW of small hydro (2027 to 2032), the capacity cap follows the cumulative plan in all three scenarios, the NDCNEW and LTSNEW config rows overwrite the A2 cap, and the Stage 2 history shares of 2025 and 2026 move from `PPHROR` to `PPHDAM`, which holds the existing run-of-river capacity.

## Files

- A-O workbooks: Dominican Republic, Ecuador (and `A-O_Demand.xlsx`), Guatemala, Honduras, Jamaica `A1_Outputs/A-O_Parametrization.xlsx`.
- `B1_Scenario_Config.xlsx` of all six models.
- `_STAGE2_INPUTS/STAGE2_OVERWRITES_Jamaica.csv` (12 lines).
- Recompiled `A2_Output_Params` and `B1_Output_Params` of the six models.
- Stage 0 to 3 outputs.
- The job folder `_LAC_HUB/fix_run_20261111T200825Z/`.

## Checks

- Phase B write gates (`write_check.csv`): every written cell equals `proposals.csv`; no change outside the listed cells except 31 formula cells that follow written cells; no formula left in the R1 cells; the other 472 A-O workbooks unchanged; the Stage 2 file changed only on the listed lines.
- Phase C keyed comparison against c42ae07 (`recompile_diff_summary.csv`): no difference outside the allowed list.
- Phase D checks (`fix_checks.csv`) and the results comparison (`results_compare.csv`): see the REPORT.

Draft pull request; not for merge before review.
