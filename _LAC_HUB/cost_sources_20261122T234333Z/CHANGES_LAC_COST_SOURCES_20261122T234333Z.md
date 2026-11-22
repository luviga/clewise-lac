# CHANGES LAC_COST_SOURCES 20261122T234333Z

All files are new and sit in `_LAC_HUB/cost_sources_20261122T234333Z/`. No model file, workbook, CSV or script outside this folder was changed.

- `PROGRESS.md`: stamp, phase, what is done and what is next, for a restart.
- `REPORT_LAC_COST_SOURCES_20261122T234333Z.md`: Phase 1 summary, country sections, manual downloads and gate results.
- `GAPS_LAC_COST_SOURCES_20261122T234333Z.md`: judgement calls, known-limitation candidates, costs left for Luis, unchecked items and incidents.
- `cost_inventory.csv`: every CapitalCost, FixedCost, VariableCost and EmissionsPenalty row of the 19 sector models and of the energy models' Vehicle Techs, with values, projection mode, formula flag, note text, class (`choice`, `total_only`, `inactive`) and Phase 2 scope.
- `fixed_horizon_sources.csv`: the source text of every Fixed Horizon Parameters and growth_formula row that has one.
- `choice_sets.csv`: every 2030 output fuel with two or more producers, its free producers, whether a choice exists, and which free producers carry each cost.
- `tech_status.csv`: class and reason per technology and model, used to class the inventory rows.
- `vehicle_cost_chain.md`, `vehicle_chain_check.csv`, `vehicle_chain_inputs.csv`: how a price per vehicle becomes M US$ per Gvkm, the recompute of every vehicle CapitalCost against the compiled BAU, and the chain inputs (distance, OperationalLife, battery rows) Phase 2 sources.
- `penalty.csv`: each penalised emission per model with years, values, emitters and whether it can change a choice.
- `sources_GEN.csv`, `cpi_u.csv`: the US CPI-U annual averages (BLS) and the factors to real 2024 USD used for every conversion.
- `scripts/`: the scripts that wrote the files above (paths are taken relative to the script).
