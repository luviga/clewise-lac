# CHANGES LAC_ALIGN 20261124T021708Z

## Code and configuration

`renewable_targets.py` (new)
: Builds the renewable share targets of the policy scenarios each run from `inputs/scenarios/scenario_values.csv`: published shares as published, and published new capacity turned into a share by one capacity rule (capacity x anchor-year capacity factor x 31.536, added to the anchor-year renewable generation, over the Stage 0 generation of the target year; at most `max_target_share`). Holds the last target after its year and makes the LTS curve equal the NDC curve through 2035.

`scenario_rules.py` (new)
: Pipeline step after the B1 runs and before Stage 0. Every solver data file gets the hydrogen rule (technologies of group `hydrogen` at activity upper limit 0, no lower limit) and the history rule (policy values up to `history_end_year` equal BAU).

`stage3_emission_cap.py` (new)
: Pipeline step after `stage3_run_all.bat`. For a scenario with an `energy_emission_reduction_vs_bau` row, writes yearly AnnualEmissionLimit values on a straight line from the solved NDC energy emissions of 2035 to BAU 2050 x (1 - r) on the `energy_cap` labels, then solves that scenario again.

`stage1_share_analyzer_v16.py`
: Reads its targets through `renewable_targets.build` instead of the stylised curves; a country and scenario without a target takes the BAU shares; writes `_STAGE1_OUTPUT/RENEWABLE_TARGETS.csv`.

`stage2_apply_v2.py`
: Reads the built targets; frozen output and committed builds are kept and the non-committed fossil part gives way when they overflow the total (solar and wind keep their boundary output); renormalisation keeps frozen plants; new sheets FROZEN and FLOOR_LOWER.

`stage3_apply.py`
: The orphan cap applies in every country and scenario (`orphan_cap_exempt_scenarios` removed); in a scenario with an energy emission cap the power plant share pins are released from `cap_start_year` (upper limits open, except the locked plants of Stage 1, biomass, biogas, bagasse and geothermal, which keep the controller upper; lower limits from FLOOR_LOWER).

`stage3_results.py`
: RE target check against each country's own built targets (released cap years not checked); extracts TotalDiscountedCost.

`stage1_test_v16.py`, `stage2_test_v2.py`, `stage3_test.py`
: Policy milestones from the built targets; Stage 2 T2 accepts an anchor of 0 for a plant absent from the controller; T8 skips recorded history years, target ramps and years after the model horizon, and its yearly step allows the share the committed renewable builds of the year add; T9 adds committed builds; new T12 hole scan (sourced zeros skipped); Stage 3 T3 and T4 expect the released limits of a capped scenario.

`ao_safe_save.py`
: The final replace is retried after garbage collection for up to 30 seconds; openpyxl and Excel held the temporary copy of large workbooks for a moment (WinError 32).

`config/scenarios/rules/stage_controller.csv`
: Rows `capacity_mw_per_gw`, `capacity_pj_per_gw_year`, `max_target_share`, `lts_equals_ndc_until`, `cap_start_year`, `cap_from_year`, `cap_target_year`; rows `orphan_cap_exempt_scenarios` and `target_hold_year` removed.

`config/scenarios/technology_types.csv`
: Group `hydrogen` (technologies with a hydrogen fuel in their input or output, six energy models) and groups `capacity_kind_solar`, `_wind`, `_hydro`, `_nonhydro_renewable`.

`config/scenarios/emission_labels.csv`
: Groups `energy_cap` (Dominican Republic and Honduras, `CO2e_sources`) and `energy_report` (label set reported against published energy emission levels).

`config/execution/Config_MOMF_T1_AB.yaml`
: Output discount rates equal to each country's social discount rate (Dominican Republic and Ecuador 0.12, Guatemala 0.07, Honduras 0.12, Jamaica 0.10262).

`Jamaica/JAM_TRANSPORT/A2_Compiler.py`
: Writes the policy base to the reference folder of every activated policy scenario of the Scenarios sheet (the B1 runner reads one folder per scenario); before, only `LTS` was written and the other scenarios read stale copies.

`PIPELINE_WORKFLOW.md`, `HANDOFF_STAGE4.md`
: The removed orphan exemption, the target rule, the scenario rules step and the emission cap step.

## Model inputs

`inputs/scenarios/scenario_values.csv`
: The 12 stylised rows are replaced by 33 published rows (renewable shares, new renewable capacity, and the two LTS emission reduction assumptions) with source, value id and note.

`*/B1_Scenario_Config.xlsx` (CR, DR, ECU, GUA, HON energy; sector waste and land-use models; JAM_TRANSPORT)
: Guatemala and Honduras IMP_ELE rows (same limits in every scenario); policy emission factor rows (DR, HON: BAU value; ECU: IPCC 2006 x fuel input); transport adoption rows of the published targets (CR, HON); Guatemala hydrogen adoption rows in the BAU form; waste and land-use EmissionsPenalty rows 0; history cells of step 5.1; Costa Rica and Dominican NDC and LTS plant capacity and activity limit rows (Electrical) at the BAU values (stylised recalibration rows, not published measures); Jamaica SmartGrid road emission factor rows of the policy scenarios at the BAU values; JAM_TRANSPORT scenario labels.

`*/A1_Outputs/A-O_Parametrization.xlsx`, `*/A1_Outputs/A-O_Demand.xlsx`
: Vehicle prices, fixed costs and lives (step 7.1 to 7.4; the four sourced distances are not written, see GAPS); sector cost proposals (step 7.5); history residual capacity, caps, builds and generation of step 5.1; Honduras IMP_ELE upper limit from 2025; Jamaica PPBIM residual capacity 0.

`*/A2_Extra_Inputs/A-Xtra_Emissions.xlsx`
: EmissionsPenalty 0 (externalities out of the objective).

`*/B1_Default_Param.xlsx`
: DiscountRate: each country's social discount rate.

`Jamaica/JAM_TRANSPORT`
: Old LTS renamed NDP, NDCNEW to NDC, LTSNEW to LTS, each with its own reference folder (A2 folders NDP and NDC added, NDCNEW and LTSNEW removed); the dated JAMInput and JAMOutput copies removed; JAMInput.csv and JAMOutput.csv regenerated by its runner.

## Compiled inputs and stage outputs

`*/A2_Output_Params`, `*/B1_Output_Params`, `_STAGE0_OUTPUT`, `_STAGE1_OUTPUT`, `_STAGE2_OUTPUT`, `_STAGE3_RESULTS`
: Regenerated by the full run of this job, as the repository tracks them.

## Job folder

`_LAC_HUB/align_20261124T021708Z/`
: Brief, progress, the three output files, gate tables, registers, sources and scripts.
