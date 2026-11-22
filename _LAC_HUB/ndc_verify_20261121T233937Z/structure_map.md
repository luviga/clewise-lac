# Structure map: clewise-lac against OSTRAM

Describes only. Nothing was moved or changed. Current state: `main` at `a76ad81`. OSTRAM: https://github.com/Climate-Lead-Group/OSTRAM, cloned read-only to `/c/clw_scout_ostram` at `73d045a`.

## What OSTRAM looks like

- `config/`: one YAML or CSV per stage. `compilation/Config_MOMF_T1_A.yaml`, `execution/Config_MOMF_T1_AB.yaml`, `preparation/Config_country_codes.yaml` (country codes and names, the single source of truth) and `Config_region_consolidation.yaml`, `scenarios/<scenario>/` (one folder per scenario with its rule files, for example `bau_calibration.yaml`, `set_vre_targets.yaml`), `scenarios/rules/` (shared CSV rules), `scenarios/technology_types.csv` (technology groups), `setups/` (registry and setup files).
- `inputs/`: data tables. `osemosys_global/` (one CSV per OSeMOSYS set and parameter), `preparation/`, `execution/`, `scenarios/` (root workbooks).
- `model/`: one shared model file (`osemosys_fast_preprocessed.txt`).
- `ostram/`: the Python package. `pipeline/preparation`, `pipeline/compilation`, `pipeline/execution`, `pipeline/scenarios`, `reporting/`, `validation/`; run as `python -m ostram`.
- `areas/<area>/config`, `areas/<area>/inputs`, `areas/<area>/model`: a second study area with the same layout (there is already an `areas/lac`).
- `docs/`, `examples/`, `tests/`, `tools/` at the root.

## What clewise-lac looks like

- Six country folders (`CostaRica`, `DominicanRepublic`, `Ecuador`, `Guatemala`, `Honduras`, `Jamaica`), each with sector models: `*_ENERGY` (Costa Rica nests it under `t1_confection/`), `*_AFOLU`, `*_IPPU`, `*_WASTE`, and in Jamaica `JAM_TRANSPORT`. Each model folder holds its own scripts (`A1_Model_Structure.py`, `A2_Compiler_<country>.py`, `B1_Base_Scenarios_Adj_Parallel*.py`, `B2_Results_Creator_f0.py`, plotting scripts), its own copy of `OSeMOSYS_Model.txt` (30 copies in the repository), input workbooks (`A1_Inputs/`, `A2_Extra_Inputs/`, `B1_Scenario_Config.xlsx`, `B1_Default_Param.xlsx`, `B1_Model_Structure.xlsx`), compiled CSV folders per scenario (`A2_Output_Params/<scenario>/`, `B1_Output_Params/<scenario>/`) and `Executables/`.
- Root scripts for the stage controller: `stage0_*.py`, `stage1_share_analyzer_v16.py`, `stage2_apply_v2.py`, `stage3_apply.py`, `stage3_results.py`, `stage*_run_all.bat` and `.sh`, cost-repair and audit scripts, cleaning scripts, tests (`test_*.py`, `stage*_test*.py`).
- Root output folders: `_STAGE0_OUTPUT`, `_STAGE1_OUTPUT`, `_STAGE2_INPUTS`, `_STAGE2_OUTPUT`, `_STAGE3_RESULTS`, `_COST_AUDIT_OUTPUT`, `_COST_REPAIR_OUTPUT`.
- `models_energy_RE_generation_costs_update/`: a second copy of the six energy models (2,392 files), not used by the stage run (see `script_constants.csv`, column `stage0_3_results_depend` = `no`).
- `_LAC_HUB/`: job folders and briefs.

## What would move where

| Now | In an OSTRAM layout | Note |
|---|---|---|
| Country names and folder names typed in `stage1_share_analyzer_v16.py` (lines 64 to 79), `stage2_apply_v2.py` (lines 52 to 57), `stage3_apply.py` (lines 39 to 44) and the batch files | `config/preparation/Config_country_codes.yaml` (name, code, model folder) | 660 country names and codes in `script_constants.csv` |
| Scenario names in code (1,282 literals), folders `A2_Output_Params/<scenario>`, `B1_Output_Params/<scenario>`, `Executables/<scenario>_FINAL_0` and workbook sheets | `config/scenarios/<scenario>/` with `BAU`, `NDC`, `LTS` (Luis, 21 November 2026); old names retired | `scenario_names.csv` counts 12 names |
| Renewable targets typed twice (`stage1_share_analyzer_v16.py` lines 97 to 110, `stage2_apply_v2.py` lines 61 to 75) and other controller numbers (anchor and cutoff years, decline rate, tolerances) | `inputs/scenarios/scenario_values.csv` (published targets) and `config/scenarios/rules/stage_controller.csv` (controller settings) | `scenario_values.csv` of this job is the proposed content of the first |
| Technology prefixes and names in code (`PWR`, `PP`, plant lists) | `config/scenarios/technology_types.csv` (group, technology) | 1,165 rows of kind technology or prefix |
| Fuel and emission names in code | set tables (`FUEL.csv`, `EMISSION.csv`) with a group or label table | 1,036 rows |
| Numbers in `A2_Compiler_*.py` and `B1_*.py` | `config/compilation/Config_MOMF_T1_A.yaml` and `config/execution/Config_MOMF_T1_AB.yaml` | names in column `move_to` |
| `A1_Inputs/`, `A2_Extra_Inputs/`, `B1_Scenario_Config.xlsx`, `B1_Default_Param.xlsx` per model | `inputs/preparation/` and `inputs/scenarios/` (per country inside a file, or `areas/<country>/inputs/`) | |
| `A2_Output_Params/`, `B1_Output_Params/`, `Executables/` | generated outputs outside git, under a run folder | OSTRAM keeps data under DVC (`dvc.yaml`) |
| 30 copies of `OSeMOSYS_Model.txt` | one file in `model/` | numbers in the model file are listed in `script_constants.csv` (bounds of -99999 on cost and emission variables, the 0.5 mid-year factor); whether the 30 copies are identical was not checked |
| Root `stage*.py` scripts, A2 and B1 scripts per model | a package like `ostram/pipeline/{preparation,compilation,execution,scenarios}` with one entry command | A2 and B1 differ per country today; one shared compiler would read the country tables |
| `stage3_results.py`, `B2_Results_Creator_f0.py`, plotting scripts in `config_plots/` | `ostram/reporting/` | |
| `test_*.py`, `stage*_test*.py` | `tests/` | |
| `_STAGE*`, `_COST_*` output folders | run output folders outside git | |
| `models_energy_RE_generation_costs_update/` | retired or archived | duplicate of the energy models |
| `PIPELINE_WORKFLOW.md`, `HANDOFF_STAGE4.md`, `AO_COST_REPAIR_WORKFLOW.md` | `docs/` | |
| Sector models (`*_AFOLU`, `*_IPPU`, `*_WASTE`, `JAM_TRANSPORT`) | `areas/<country>/<sector>/` with the same config, inputs, model split, or separate repositories | they are not part of Stage 0 to 3 |

## Differences that a move would have to settle

- OSTRAM is one power-system model with many regions; clewise-lac is six whole-energy models with sector models beside them. The `areas/` pattern fits one area per country better than one shared `inputs/osemosys_global/`.
- OSTRAM scenarios are folders of rule files that act on a base; clewise-lac scenarios are built by B1 from the scenario workbook and then rewritten by the stage controller from 2025. The controller logic is the part that would become `config/scenarios/<scenario>/` rule files plus `inputs/scenarios/scenario_values.csv`.
- Costa Rica nests its energy model one level deeper (`CR_ENERGY/t1_confection/`) and uses `PWR` technology names, the other five use `PP`. Ecuador names its folder `ECU_Energy`. A move would make these uniform.
