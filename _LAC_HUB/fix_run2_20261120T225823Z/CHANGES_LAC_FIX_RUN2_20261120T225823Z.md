# CHANGES LAC_FIX_RUN2 20261120T225823Z

Branch `job/fix-run` (draft PR #11), compared with `4ba69d6`. One entry per file or folder: what changed and why. Every written cell is in `proposals.csv` with its decision, sources and derivation; `write_check.csv` checks them.

## Model data files

- `Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx`. Crude chain (D-ECU1, D-ECU2, D7a): `EXTT_CRU` limits from BCE field production 2021-2030 (held after 2030), lower band 0.999; `DIST_CRU` limits 0 and 999,999 every year; `PROCRU` limits 0 and 999,999; `REF_*` limits scaled to BCE processed crude (2021-2025) and MDEP-BCE refinery loads (2026-2030, held after). Fixed Horizon Parameters: OperationalLife of the 36 capital-cost technologies from ARCONEL-004/24, the ARCERNNR 2021 cost-of-service report, the CCG kit, PLANMICC and NREL ATB (D12); new row pairs for `PPHD` (CapacityToActivityUnit 31.536, D1) and `PRONGS`; CapacityToActivityUnit 31.536 for 8 hydro plants at 31.54 (D13).
- `Ecuador/ECU_Energy/A1_Outputs/A-O_Demand.xlsx`. `E5EXPCRU` 2031-2050 hold the 2030 BCE outlook value, 655.88 PJ (D-ECU1).
- `Ecuador/ECU_Energy/B1_Scenario_Config.xlsx`. SmartGrid: `PROCRU` CO2 and CO2e factors of 2022 from the national inventory (D3), in the BAU row and its two copies.
- `DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`. CapacityToActivityUnit 31.536 for 29 plants (D13); the band factor 0.98 becomes 0.999 in 19 lower-limit rows (D7a); `PPDHYD` capacity factor formula gains the 0.0036 conversion (D2f) and its activity upper limit follows UN self-producer hydro statistics (Phase D repair, D2f and D2c); `PPDBGS` capacity factor 2018-2023 from IRENA biogas statistics (Phase C repair, D2c).
- `DominicanRepublic/RD_ENERGY/B1_Scenario_Config.xlsx`. EmissionsActivityRatio: history factors 2018-2022 of coal, gas and fuel-oil plants from the national inventory and CNE generation (D3), in the BAU rows and their copies. Electrical: history elements of the `PPDBGS` and `PPDHYD` lower and upper rows of NDCNEW and LTSNEW set to BAU (D2).
- `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx`. CapacityToActivityUnit 31.536 for 10 plants (D13).
- `CostaRica/CR_ENERGY/t1_confection/B1_Scenario_Config.xlsx`. Electrical: 36 Overwrite rows that give NDCNEW and LTSNEW the BAU transport history (D2e); history-only `PWRSUG` cap rows; 2021 elements of `PWRBMS` and `PWRHYDROR` lower limits set to BAU (D2d).
- `Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`. CapacityToActivityUnit 31.536 for 15 plants (D13); `DIST_FLEXFUEL` VariableCost from the Brazilian hydrated-ethanol to pre-tax gasoline ratio times `DIST_GSL` (D6).
- `Guatemala/GUA_ENERGY/B1_Scenario_Config.xlsx`. Electrical: 54 Overwrite rows with BAU transport history for NDCNEW and LTSNEW (D2e).
- `Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`. CapacityToActivityUnit 31.536 for 20 plants (D13); `PPBGS` CapitalCost 7,269.10 USD/kW in every year (D5).
- `Honduras/HON_ENERGY/B1_Scenario_Config.xlsx`. EmissionsActivityRatio: 2019 factors of five power-plant types from the BEN 2019 efficiencies and the inventory factors (D3). Electrical: 20 transport Overwrite rows and a history-only `TRBPUGSL` cap row per policy scenario (D2e).
- `Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx`. CapacityToActivityUnit 31.536 for 15 plants (12 at 31.356, 3 at 31.4; D13); band factor 0.999 in 7 lower-limit rows (D7a).
- `Jamaica/JAM_ENERGY/B1_Scenario_Config.xlsx`. SmartGrid: `T5DSLTRO` and `T5GSLTRO` multiplier rows for NDCNEW and LTSNEW so their 2021-2024 factors equal BAU (D2a).
- `_STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.csv`. 2025 and 2026 hydro shares per scenario from the AMM 2025 hydro generation and each scenario's Stage 0 denominator (D8, step DS1); the non-hydro plateau shares of those years scaled so each year sums to 100 percent.

## Compiled outputs

- `*/A2_Output_Params/` and `*/B1_Output_Params/` of the six energy models: recompiled with the canonical A2 and B1 commands after the writes (Phase C); differences against `4ba69d6` are classified in `recompile_diff_summary.csv` (none unexplained). Ecuador `A2_Output_Params/NDCINC` is rewritten by the Ecuador A2 compiler as before.
- `_STAGE0_OUTPUT/`, `_STAGE1_OUTPUT/`, `_STAGE2_OUTPUT/`, `_STAGE3_RESULTS/`: Stages 0 to 3 re-run (Phase D, second run after the Dominican repair).

## Job folder `_LAC_HUB/fix_run2_20261120T225823Z/`

- `REPORT_`, `GAPS_`, `CHANGES_LAC_FIX_RUN2_20261120T225823Z.md`: the three outputs of the brief.
- `proposals.csv`, `sources.csv`, `sources_pending.csv`, `source_map.csv`, `starter_kit_deviations.csv`, `history_plan.csv`, `history_builds.csv`, `history_diff_before.csv`, `gua_hydro_trace.md`: Phase A.
- `write_check.csv`, `backups/` (with `backup_manifest.csv`): Phase B. `recompile_diff_summary.csv`: Phase C. `fix_checks.csv`, `fix_checks_detail.csv`, `results_compare.csv`: Phase D. `cross_sector_check.csv` and `.md`: Phase E.
- `scripts/` (proposal builders, writer, checks, drivers, stage runner), `logs/`, `stage_logs/` (run 1 in `stage_logs/run1/`), `research/` (search notes and source tables), `PROGRESS.md`, `BRIEF_LAC_FIX_RUN2.md` and `BRIEF_LAC_FIX_RUN2_v2.md`. `downloads/` is gitignored.
