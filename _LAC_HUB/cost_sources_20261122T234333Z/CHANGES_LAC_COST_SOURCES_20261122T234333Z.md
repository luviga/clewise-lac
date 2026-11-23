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
- `scripts/`: the scripts that wrote the files above (paths are taken relative to the script); `p2_cells.py` writes the cell lists, `p2_paper_extract.py` reads the Data in Brief draft, `p3_gates.py` runs the Phase 3 gates, `hygiene.py` scans tracked files for line endings, em dashes and machine paths.
- `GEN/`: the shared packages every country uses where national data is missing. `gen_vehicle_factors.csv` holds ATB 2022 price trajectories, reference prices, maintenance, lifetimes and annual distances; `faostat_*.csv` hold FAOSTAT import unit values, producer prices, yields and the item mapping; `gen_sector_values.csv` holds waste and wastewater costs; each package has its sources, search log, manual list, notes and scripts. Their sources are merged into `sources_GEN.csv`.
- `<CC>/cells_<CC>.csv`: one row per A-O cell (or chain input) that the country's proposals answer, with the current value and a locator at `b51f24b`.
- `CR/`: Costa Rica proposals (2,489 cells), sources CR-001 to CR-013, search log, manual downloads and the scripts that built and checked them.
- `DR/`: Dominican Republic proposals (2,354 cells), sources DR-001 to DR-004, search log, manual downloads and scripts.
- `GUA/`: Guatemala proposals (705 cells), sources GUA-001 and GUA-002, search log, manual downloads and scripts.
- `HON/`: Honduras proposals (1,532 cells), sources HON-001 to HON-005, search log, manual downloads and scripts.
- `JAM/`: Jamaica proposals (1,784 cells), sources JAM-001 to JAM-007, search log, manual downloads and scripts.
