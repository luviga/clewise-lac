# CHANGES LAC_STRUCTURE_TABLES 20261122T042525Z

File by file, what changed and why. Pull request 1 (values and names in external tables) is section 1; pull request 2 (scenarios renamed) is section 2.

## 1. Values and names of the stage pipeline in external tables (pull request 1)

No value that reaches a model changed. Every literal that the scan of LAC_NDC_VERIFY marked as a result dependency now comes from a table through one loader; constants of the mathematics, of a file layout or of presentation stay, each listed with its reason in `script_constants_accepted_job.csv`. Each edited Python file was checked against its version at `b51f24b` by folding every loader read back into the literal it returns and comparing the two syntax trees (`scripts/b2_fold_check.py`): all equal.

### New tables (OSTRAM folder names)

- `config/preparation/Config_country_codes.yaml`: the six countries in processing order, with pipeline name, display name, model region code, country folder, model folder, model file and the names of the A2 compiler and B1 runner. Replaces the country dictionaries typed in eleven scripts.
- `config/scenarios/scenario_catalogue.csv`: every scenario name the code uses, with its role (base, ndc, lts, lts_optimal and one role per older name) and its groups (`in_use`, `policy`, `older`). The stage scripts read their scenario lists from the group `in_use`.
- `config/scenarios/rules/stage_controller.csv`: Stage 0 to 3 controller settings (anchor, cutoff, plateau and hold years, decline rate, security factors, sentinels, tolerances, rounding digits, printed years), one row per setting and stage, with a country column for settings written per country (`share_column`).
- `config/scenarios/technology_types.csv`: technology groups, name tokens and name prefixes (power plant prefixes, hydro, renewable, fossil and solar-wind tokens, Stage 0 bypass plants, transmission and distribution tokens, transport fleet groups, ignore lists, gasoline blend technologies, mode-shift complement shares).
- `config/scenarios/fuel_types.csv` and `config/scenarios/emission_labels.csv`: fuel and emission label groups beside the technology table (electricity token, transport demand fuels; externality labels per country, gasoline blend emissions, CO2 token).
- `inputs/scenarios/scenario_values.csv`: the renewable share targets of F3 with columns `country, scenario, lever, lever_kind, year, value, unit`; `lever_kind` is `share of generation` in every row. General rows carry country `all`; Costa Rica and Ecuador have their own rows, as the code had. The targets were typed three times (Stage 1, Stage 2 and the general curve again in `stage3_results.py`); all three now read this table.
- `config/compilation/Config_MOMF_T1_A.yaml`: numbers of the A2 compilers (rounding digits for all; base year per country).
- `config/execution/Config_MOMF_T1_AB.yaml`: numbers of the B1 runners (rounding digits, security factors, markers in the general section; years, discount values, blend points, mode-shift and region settings per country).

### New code

- `lac_tables.py` (repository root): the loader. Reads the tables above with the standard library and PyYAML; typed values (integer text gives an int, decimal text a float, `|` separates list items); cached lookups for names and numbers; a command `python lac_tables.py solver-runs <S0|FINAL>` that prints the solver run list for the batch and shell files.

### Stage pipeline at the root

- `stage0_run.py`: scenario list, anchor and plateau years, power plant prefixes, bypass plant set, upper limit sentinel, country table, year header minimum, bypass floor and oversize ratio, change tolerance and log rounding read from the tables. It still writes `stage0_run_all.bat` and `.sh` on each run with one command per prepared run.
- `stage0_collect_outputs.py`, `stage0_capacity_check.py`, `stage0_recommend_shares.py`: scenario lists, country tables, prefixes, transmission tokens, history end year, thresholds and rounding digits read from the tables.
- `stage0_clean.py`, `stage2_post_clean.py`: country tables read from the country YAML.
- `stage1_share_analyzer_v16.py`, `stage2_apply_v2.py`: share column per country, scenario roles, controller settings, technology tokens, the Costa Rica name list and the renewable targets read from the tables; output labels that held the base scenario name are built from the catalogue (same text).
- `stage3_apply.py`, `stage3_results.py`: scenario list, prefixes, country table (with region code), patch year, reserve margin, sentinels and factors, uncapped value, fallback years, check thresholds, printed years and the general renewable targets read from the tables.
- `stage0_run_all.bat`, `stage0_run_all.sh`, `stage3_run_all.bat`: rewritten as loops over the run list that `lac_tables.py` prints (countries from the country YAML, scenarios from the catalogue); no country, scenario, path or date is typed in them. Stage 3 runs this batch file as tracked.
- `ao_safe_save.py`: unchanged; its three flagged numbers are an Excel interface constant and message lengths (accepted list).

### Six energy models

- `A2_Compiler_<country>.py` (six files): a loader preamble (finds `lac_tables.py`, reads the compilation numbers of the country); rounding digits, base year and the scenario folder names of the outputs read from the tables. The older scenario folders the compilers write (NDCincond, NDCcond, NDP, NDPAMB, NDCINC) are read from the catalogue by role.
- `B1_Base_Scenarios_Adj_Parallel*.py` (six files): a loader preamble (country of the script, execution numbers of the country); rounding digits, security factors, markers, years, discount values, blend points, region codes, scenario roles, fleet groups, demand fuels, externality lists, ignore lists, gasoline blend technologies and emissions read from the tables. The scripts keep their names, places and logic; the six runners were not merged.

### Job folder

- `_LAC_HUB/structure_tables_20261122T042525Z/`: brief, PROGRESS, REPORT, GAPS, this file, `tables_register.csv`, `script_constants_accepted_job.csv`, `baseline_against_main.csv`, `phaseB_against_baseline.csv` (0 rows), the scans before and after (`scan_before/`, `scan_after/`), working lists (`work/`) and the job scripts (`scripts/`, machine paths in an untracked `machine.json` read by `scripts/machine.py`). Run logs stay out of git (they hold machine paths and solver figures).

## 2. Scenarios renamed BAU, NDC, LTS (pull request 2)

Two commits on `job/structure-rename`, stacked on pull request 1. The first retires the older scenario names; the second renames NDCNEW to NDC and LTSNEW to LTS and carries the outputs of the final run. The plan of every place is in `rename_plan.csv`; names left are in `names_left.csv`.

### Retire older names (commit "retire older scenario names")

- `A2_Compiler_<country>.py` (six files): the compilers no longer write folders under older names (NDCincond, NDCcond, NDP, NDPAMB, NDCINC, LTS). Where such a folder fed a scenario in use (Dominican Republic NDCcond, Guatemala and Honduras NDP, Jamaica LTS), the compiler writes the same data straight into the folders of the scenarios in use, which the pipeline step did before with a copy.
- `CostaRica/.../MOMF_T1_A.yaml`: the empty list of other scenarios and the retired output folder entry removed.
- `B1_Base_Scenarios_Adj_Parallel*.py` (five files): twelve `if` branches that run only for an older scenario removed (Costa Rica 9, Dominican Republic 1, Guatemala 2); blend-share and name lookups of older scenarios point to the scenario in use (the same result for the three scenarios run).
- `B1_Scenario_Config.xlsx` (six files): 1,681 rows of older scenarios deleted (Excel row deletion; the remaining rows checked by content).
- `Ecuador/ECU_Energy/A2_Output_Params/NDCINC/`: removed (written only under the older name, read by nothing in use).

### Rename (NDCNEW to NDC, LTSNEW to LTS)

- `config/scenarios/scenario_catalogue.csv`: the two scenarios in use carry their new names; the rows of older names are gone. Every stage script reads its names from here, so the stage code did not change.
- `A2_Compiler_<country>.py` (Dominican Republic, Guatemala, Honduras, Jamaica): the files written for the policy scenarios take the name of their folder as Scenario label (it was an older name); values unchanged.
- `A2_Extra_Inputs/A-Xtra_Scenarios.xlsx` (five files): the Other_Scenarios row deleted (no code reads it after C2).
- `B1_Scenario_Config.xlsx` (six files) and `_STAGE2_INPUTS/STAGE2_OVERWRITES_*.xlsx`: cells holding NDCNEW or LTSNEW renamed through `ao_safe_save.py`, every other cell and every formula checked equal (`workbook_checks.csv`).
- `_STAGE2_INPUTS/STAGE2_OVERWRITES_*.csv`, `inputs/scenarios/scenario_values.csv`: the scenario column renamed, every other field checked equal.
- `A2_Output_Params/` and `B1_Output_Params/` of the six models: folders NDCNEW and LTSNEW moved to NDC and LTS with `git mv`, then rewritten by the final run.
- `stage1_test_v16.py`, `stage2_test_v2.py`, `stage3_test.py`, `stage2_demand_verify.py`: scenario lists and names read from the catalogue.
- Stage outputs (`_STAGE0_OUTPUT`, `_STAGE1_OUTPUT`, `_STAGE2_OUTPUT`, `_STAGE3_RESULTS`) and the compiled folders: as written by the final run under the new names.
