# GAPS of LAC_INPUT_GATES (stamp 20261125T055704Z)

## Judgement calls and their reasons

1. **Command form.** The brief names `py -I -m gates`. Isolated mode (`-I`) leaves the working folder off the import
   path, so `-m gates` cannot find a package that is not installed, and this job may not install anything outside
   its clone. The package runs as a folder in isolated mode: `py -I gates --point ...` (its `__main__.py`
   puts the repository root on the path); `py -m gates ...` also works. FEASIBILITY_PROTOCOL.md and
   PIPELINE_WORKFLOW.md name `py -I gates`. This is the form that changes least.
2. **Check-mode wrapper writes a stub output.** Several B1 runners (the waste and IPPU runners, for example) read
   the solver output file in a loop until they meet the Karush-Kuhn-Tucker line, so without an output file they
   never return. In check mode the wrapper writes a two-line stub (`Status: NOT SOLVED`) to the `-o` path; the
   runner then stops with an error after all its data files are written and translated. The stubs sit in the
   gitignored `Executables/` folders and hold no solution.
3. **FAIL means beyond the solver's tolerance.** CR_AFOLU E5DEGDRY 2022 has a demand of 0.00170808 and a single
   producer with an activity upper limit of 0.0017; it is short by 8e-6, yet #19 solved CR_AFOLU OPTIMAL because
   GLPK accepts that within its feasibility tolerance. A bound violation larger than `abs_tol` but no larger than
   `solver_abs_tol` (1e-5, `config/gates/thresholds.csv`) is a WARN; a FAIL exceeds it. The Ecuador 0.1 MW case
   (1e-4 GW) stays a FAIL.
4. **S2 and minimum capacity.** The brief makes S2 a FAIL when the consumer is forced by a lower limit or a minimum
   capacity. A minimum capacity does not force activity in OSeMOSYS (capacity may stand idle), so a FAIL there
   would not be sound; S2 is a FAIL only for an activity lower limit with the fuel needed in every mode, and a
   WARN that names the minimum capacity otherwise.
5. **S6 and declared defaults.** A technology without an explicit OperationalLife or CapacityToActivityUnit takes
   the default the data file declares; translation works and nothing is infeasible. That case is a WARN; a missing
   value with no declared default is a FAIL. Factor ranges and split sums are FAILs as the brief says.
6. **P2 bound.** The brief describes the least emissions as least activity times the smallest positive ratio. That
   bound misses emissions that sit upstream of the limited technologies (the Honduras case: emissions on fuel
   supply, ceilings on electric vehicles). P2 uses a weak-duality bound instead: the least embodied emission per
   unit of each fuel along the chain, plus reduced costs filled against the producers' tightened limits. It is
   sound for any sign of the ratios (negative ratios count at the largest activity) and reduces to the brief's
   bound when emissions sit on the limited technology itself.
7. **R1 is a staleness test.** A register value is compared with the compiled file only through its before and
   after values: a compiled cell that still holds `before` (with before different from after) is a FAIL; `after`
   passes; any other value is counted as unchecked. Comparing `after` directly gave false alarms where the
   compiler converts units (the register says so: vehicle capital costs entered per vehicle and compiled to
   M US$ per Gvkm). Rows whose unit column holds the marker `compiled to` and rows that name something that is
   not a set member of the model (a group, a label) are unchecked. R1 reads every `_LAC_HUB/*/value_register.csv`;
   the per-step registers under `work/` that those rows summarise are not read a second time.
8. **R4 at the b1 point for energy models.** `scenario_rules.py` equalises the history of the six energy models
   after the compile and before Stage 0 and Stage 3. At the b1 point R4 is a WARN for those models (the rule fixes
   it later) and a FAIL at the final point; for the 18 other models, which no rule touches, R4 is a FAIL at b1.
9. **Stage 3 build order.** `stage3_apply.py` copies the `_0` files after `scenario_rules.py` has rewritten them, as
   PIPELINE_WORKFLOW.md runs the pipeline. The build therefore ran `scenario_rules.py` first, then
   `stage3_apply.py`, then the tracked caps. The compiled `_0` files were kept in the temporary folder before the
   rules ran and put back after, so the b1 point reads what the compile wrote (S0 compares them with
   B1_Output_Params).
10. **Caps through the pipeline's function.** `stage3_emission_cap.py` has no entry point for writing tracked caps
    without its solves, so the build imports `scenario_rules.set_rows`, the function `stage3_emission_cap.py`
    calls, and writes the rows of `_STAGE3_RESULTS/EMISSION_CAPS.csv` with it.
11. **Costa Rica LTSOPT.** The Costa Rica B1 configuration activates LTSOPT, which has no A2 folder in the tree.
    The compile followed LAC_ALIGN: a temporary `A2_Output_Params/LTSOPT` copied from LTS for the run, removed
    after with its B1 folder. The data file stays in the gitignored `Executables/LTSOPT_0` so the suite reads it;
    S7 reports the missing `B1_Output_Params/LTSOPT`.
12. **R7 origins.** A value is traced when it matches a register row, a row of the scenario's A2 compiled table
    (written by the model's A2 compiler from its A1 workbooks), a sheet row of `B1_Scenario_Config.xlsx` that
    names the technology, or a stage rule (FINAL values that differ from the `_0` file). The workbook origin names
    the sheet and row, not the exact cell, and the A2 origin stops at the compiled table rather than following the
    compiler into the A1 workbook cell.
13. **R6 tracing.** R6 follows the loaded rows of `published_values_loaded.csv` whose model input is a
    Tech_Adoption row. Published values loaded through `inputs/scenarios/scenario_values.csv` (renewable shares,
    capacity targets, emission reductions) reach the data files through stage rules that write minimums
    (`REMinProductionTarget`, lower limits) and the cap; no maximum built from them could be traced to a row, so
    they are not checked by R6.
14. **X2 scope.** X2 checks the renewable share levers (held after their year) and the energy emission reduction
    levers of `scenario_values.csv` against `results_summary.csv`. The capacity levers (new solar, wind, hydro
    capacity) are not checked: the results table holds yearly new capacity by group and the start year of the
    cumulative count is not in the lever rows.

15. **Label-only differences are stale.** ECU_IPPU's policy A2 tables and 17 of ECU_USCUSS's regenerated policy
    tables differ from their tracked copies only in the Scenario column (tracked "BAU", the compiler writes the
    folder's own name); every value is identical. They no longer match what their compiler writes, so they were
    committed with that cause in `stale_compiled.csv`; restoring them was the alternative and would have left
    ECU_USCUSS folders with mixed labels.
16. **ECU_AGR not fixed.** ECU_AGR has the same compiler code and the same `A-Xtra_Scenarios.xlsx` as ECU_USCUSS
    (`Other_Scenarios` NDCINC, a scenario ECU_AGR does not have): its compile writes an untracked
    `A2_Output_Params/NDCINC` and never writes its NDC and LTS folders. Applying the ECU_USCUSS fix would replace
    ECU_AGR's NDC and LTS tables (tracked copies equal to BAU) with the policy tables, a change of AFOLU policy
    inputs the brief does not name; the folder was removed and the case is listed below.
17. **No-limit sentinels.** R4 and R5 treat two values that are both at or above `no_limit_at_or_above` as equal
    (RD_ENERGY FINAL files carry 1e+11 in NDC where BAU carries 99999; neither binds).
18. **P1 per time slice uses demand only.** The users' use of a fuel within a time slice has no least value from
    annual limits, so the time slice test compares the demand with the most supply only.
19. **JAM_TRANSPORT replay.** Main already lacks `B1_Output_Params` for NDP, NDC and LTSOPT, so S7 fires on main;
    the replay copy removed the NDC data file and the replay counts only the S7 row about the missing data file.
20. **PR number.** REPORT and CHANGES name the pull request #20, the next number after #19, written before the
    pull request was opened and checked after.

## Known-limitation candidates

- ECU_AGR: compiler writes `A2_Output_Params/NDCINC` for a scenario the model does not have; its NDC and LTS
  compiled folders have no compile that writes them; all three scenarios carry an EXT_REGAIR emission penalty of 1
  (R2).
- RD_AFOLU: `B1_Output_Params/LTS` and `LTSNZ` (scenarios deactivated in `B1_Scenario_Config.xlsx`, still tracked)
  keep non-zero penalties and old costs; no compile writes them and the suite does not read them.
- JAM_TRANSPORT: the B1 runner writes data files for NDP, NDC and LTSOPT but no `B1_Output_Params` folder for them
  (S7 on main).
- Costa Rica: `B1_Default_Param.xlsx` holds the sourced DiscountRate 0.0831 but the data files declare 0.05 (R1):
  the runner takes the default from elsewhere.
- Costa Rica LTSOPT: activated in the B1 configuration with no A2 folder in the tree (S7).
- JAM_ENERGY: TRXTRAIELE takes fuel E4ELE_HEA, which no technology produces (S2 WARN).
- RD_AFOLU NDCcond and NDCincond: 2018 variable costs of AG_RIC, AG_COC and AG_CAF still at the values LAC_ALIGN's
  register replaced (R1).
- Stage 3 plant limits differ between BAU and the policy scenarios from 2025 without a register row (R5 at the
  final point, 104 rows).
- `PIPELINE_WORKFLOW.md` carries em dashes in its older text; this job added three lines without any.

## Left unchecked

- T0 (translation) is checked by the compile wrapper, not by the suite package, and so has no case in
  `test_gates.py`; every data file's translation is in `check_log.jsonl`.
- `Guatemala/GUA_AFOLU` holds model inputs without an `OSeMOSYS_Model.txt`: `Long_Model.txt`, `0_Ref/` and
  `2_Model/{BAU,LTS,NDC}` (data files of its own pipeline, `7_run_model_mathprog.py`). It has no row in
  `config/gates/models.csv` and the suite does not read it.

## Incidents

- The clean-up step could not delete the temporary folder: the session's safety check refuses to remove a folder
  at the root of the drive without a person approving it. The folder holds only copies (compiled data files,
  replay copies, run logs) and is left for Luis to delete. PROGRESS and this note were corrected in a fourth
  commit, since rewriting the third commit would have needed a force push.

- The background compile started ECU_USCUSS's A2 seconds before its compiler was fixed; ECU_USCUSS was compiled
  again after the fix and the files of that second compile are the committed ones.
- The first trial compile of HON_WASTE hung: the runner waited forever for the solution file. The hung processes
  were stopped and the wrapper's stub output (item 2) added; the compile then ran to the end.
