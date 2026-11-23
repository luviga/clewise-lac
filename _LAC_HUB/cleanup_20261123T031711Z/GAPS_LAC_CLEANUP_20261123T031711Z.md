# GAPS LAC_CLEANUP 20261123T031711Z

Judgement calls, known-limitation candidates, candidates kept, unchecked items, and incidents. Figures of model results are in the REPORT only.

## Decision for Luis

**Guatemala NDC and LTS orphan cap.** With the Stage 2 fix and the common Stage 3 rule, Guatemala BAU solves, and NDC and LTS have no feasible solution. Relaxing one limit group at a time on a copy (orphan cap, zero-lower upper, the 1.05 band, and the former exception as a whole) showed that only freeing the orphan cap restores a solution, at the baseline objective of each scenario. The other single relaxations leave both scenarios without a solution. Per step 4.5 the exception is restored for these two scenarios only, and for the orphan cap only, as the row `orphan_cap_exempt_scenarios` of `config/scenarios/rules/stage_controller.csv`. The zero-lower rule now applies to Guatemala NDC and LTS as well. Options for Luis: keep the row; cap the orphan plant through its own controller row so it becomes a controlled plant; or rerun Stage 0 with the orphan cap so the NDC and LTS denominators no longer carry the orphan output (the fix that HANDOFF_STAGE4.md names).

## Judgement calls

- **Step 1 lock.** openpyxl 3.1.2 keeps a worksheet stream of a normal-mode load open until the next garbage collection, so Windows refuses the replace or removal of the file. The fix is in the test setup only (garbage collection after each load and before temp folder removal); `ao_safe_save.py` is unchanged because the brief changes no module for this step. The baseline ran on the start commit with its original tests, so its unit test lines fail as expected; every later run passes them.
- **F5.** The three B1 runners that read `appended_region_code` now read the country code of the country table; the codes are the same, so the compiled files are equal.
- **F6.** The RE target check is printed in the Stage 3 results log and is not written to `stage3_results.xlsx`, so the gate sees no change; the change is in the log lines of Costa Rica and Ecuador.
- **Stage 2 fix.** Of two ways to fix the overflow branch (scale the frozen plants and the solar and wind plants together, or drop the branch and renormalize every plant), the first changes least: fossil and hydro keep their values and only the non-hydro renewables of the overflow years move. It is the gap-fill rule of Stage 1.
- **Hole scan.** 97 cases match the pattern of the brief. Ten are Guatemala BAU solar and wind in 2030 and 2031, the F2 cause, all filled. 87 are Jamaica PPBIM 2027 to 2055 in all three scenarios with a different cause: the sourced overrides set biomass to 0 for 2018 to 2026 and the frozen PJ value carries the 0 forward. Changing that is a value decision, so it is left as it is and listed below.
- **stage3_test.py.** It held no Guatemala special case; T4 failed only because `stage3_apply.py` wrote the open upper limit for Guatemala zero-lower plants. With the common rule T4 passes for all six countries and the file is unchanged.
- **HANDOFF_STAGE4.md** also held the `--skip-orphan-cap` command, so it is edited with PIPELINE_WORKFLOW.md ("every command"). The history paragraphs of PIPELINE_WORKFLOW.md keep the old explanation under a heading that marks it as history.
- **Tracked run outputs.** Each full run rewrites tracked result files (B1 output parameters, Stage 0 to 3 outputs, `stage0_run_all.bat` and `.sh` with machine paths, two `SelectedResults.csv`). They are restored to the committed state after each run, so the commits hold code, tables and workbooks only, and the tracked Stage 2 controller and Stage 3 results workbooks still hold the Guatemala BAU values from before the fix until the next run. The brief keeps model result figures out of tracked files other than the REPORT, and leaving these files as they were is the smaller change.
- **Job folder contents.** The run logs (`stage_logs/`), the gate objective tables and the generation and relaxation tables hold machine paths or result figures, so they stay out of the commit; their content is summarised in the REPORT. `machine.json` (paths of this machine) and `scripts/glpsol_wrap/glpsol.bat` (written by each run with those paths) are not committed either. The step 1 test patch was committed with the job folder and removed in the next commit: as a patch its blank context lines hold one space each, which the whitespace check of step 7 flags, and the fix it holds is in commit 1.
- **Deletions count.** The candidate list counted 2,392 files in `models_energy_RE_generation_costs_update/`; `git ls-files` counts 2,393 with the same bytes. `deletions.csv` holds the counts of git at deletion time.
- **.gitignore.** The section "no tracked file may exceed 50 MB" held only a line of the removed folder, so its heading and blank line went with it.
- **Guatemala A-O Other_Techs A2 and A3.** "NDP scenarios" becomes "NDC and LTS scenarios": the rows feed the policy folders (NDC and LTS), and the other A-O workbooks use the form "<name> scenarios".
- **TotalAnnualMinCapacity labels.** The Dominican `B1_Output_Params/NDC` file and the Guatemala `A2_Output_Params/NDC` and `LTS` files are not written by any step (their modification time does not change in a run), so the source of the old label is the file itself; its Scenario column is set to the folder's name. A recompile copies the corrected label.
- **Experiment-manager keys** (F9) are left as they are, as the brief says.
- **Costa Rica variant rows.** NDCNEW_stage_2 and LTSNEW_stage_2 are deleted by Excel in a temporary copy, so every reference moves with the rows; the copy is recalculated and guarded by `ao_safe_save.assert_no_blank_formula_cells` before it replaces the file, the order of `save_ao_safely`.
- **Commit order.** PROGRESS.md and the job files go in commit 5 as the brief lists them, so they reach the remote with the last push.

## Known-limitation candidates

- `ao_safe_save.py` carries the same openpyxl lock risk in production: `find_blank_formula_cells` loads the temporary copy in normal mode, then the file is replaced or removed.
- `stage0_run.py` rewrites the tracked `stage0_run_all.bat` and `stage0_run_all.sh` with machine paths on every run.
- `stage3_test.py`, `stage1_test_v16.py` and `stage2_demand_verify.py` hold the six country names in their own COUNTRY_CONFIG.
- Jamaica PPBIM: Stage 2 share 0 from 2027 to 2055 in all scenarios where Stage 1 has a share above 0 (87 cases in `stage2_holes.csv`), from the sourced overrides of 2018 to 2026 and the PJ freeze.
- Stage 2 test T10 ("zero solar and wind") passed on the baseline although Guatemala BAU solar and wind plants had share 0 in 2030 and 2031; it does not see a plant-level hole.
- Honduras A-O `Other_Techs` holds "NDP scenarios" as well; it is outside the brief's list and unchanged.
- Costa Rica `A-Xtra_Scenarios.xlsx` holds an NDCincond cell, read by the Costa Rica A2 compiler; outside the brief's list and unchanged.
- Ecuador `_DISTANCE_RERUNNER` is a separate tool folder with its own copies; not a candidate under the brief's wording and unchanged.
- Guatemala NDC and LTS depend on the orphan plant to be feasible; see the decision above.

## Candidates kept

Each is named by a kept script or configuration (`deletions.csv`, decision keep):

- Jamaica `JAM_AO_BAU_edits.xlsx`: read by Jamaica `apply_ao_edits.py`.
- Costa Rica `config_plots/test_inputs.py`: named by `MOMF_B1_exp_manager.yaml`, which the Costa Rica B1 runner loads.
- Dominican `B1_Base_Scenarios_Adj_Parallel_ADJ_TESTEOS.py`: in the keep list of `clean_repo_apply.py` and `clean_repo_identify.py`.
- Costa Rica `A2_Extra_Inputs/A-Xtra_Scenarios.xlsx`: read by the Costa Rica A2 compiler through `MOMF_T1_A.yaml`.
- Costa Rica, Honduras and Jamaica `plots_config.yaml`: read by their `plot_csvs.py`.
- Ecuador `A-O_Parametrization_PLANMICC.xlsx`, `reference_PLANMICC/` and `reference_edited/`: in the source list of `ao_cost_repair_manager.py`.
- Guatemala and Honduras `A-O_Parametrization_COMPLETED.xlsx` and `A-O_Parametrization_Natural_COMPLETED.xlsx`: written by their A2 compilers.
- Guatemala `A2_Compiler.py` and `B1_Energy_Base_Scenarios_Adj_Parallel_mac_DR.py`: run by kept Guatemala wrappers.
- Guatemala `B1_Base_Scenarios.py`: the live Guatemala B1 runner finds its folder through this name.
- Honduras `A1_Outputs/A-O_Parametrization.xlsx`: the A-O workbook that the Honduras A2 compiler reads.

## Unchecked

- Why the band relaxation alone (no 1.05 band on plants with a positive lower limit) leaves Guatemala NDC and LTS without a solution while freeing the orphan cap restores one was not traced further.
- "Guatemala's separate model file" was not identified with certainty. No Guatemala file outside the energy model's pipeline files was edited or deleted except the F9 rows cleared by the search, and the Guatemala wrappers that run other models are kept.
- Guatemala NDC and LTS objectives equal the baseline after step 4, but a few hydro values move between solutions of equal cost because zero-lower plants now get upper 0 there; the solutions were not compared further.

## Incidents and restarts

- The first scratch run of the Stage 2 fix stopped on a console encoding error, so its first "equal" result compared nothing; it was rerun with UTF-8 output and reproduced the baseline before the fix was applied.
- The first draft of the step 4 script placed one edit in the wrong block and held a result figure in the table reason; it was rewritten before it touched the clone.
- The step 6 workbook check first failed one Costa Rica cell. The cause was in the check: edited cells were looked up at their positions after the row deletion. With the start positions the check passes; the workbook was not changed again.
