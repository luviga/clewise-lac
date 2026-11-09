# GAPS LAC_FORMULA_CHECK 20261109T003529Z

## Judgement calls and their reasons

1. **No LibreOffice, so I wrote my own evaluator (Step 3, route 2).** Microsoft Office is installed (`C:\Program Files (x86)\Microsoft Office\`), but the brief names only LibreOffice for recalculation. Driving Excel would have gone beyond the brief, so I did not use it. To show the evaluator is sound, I compared it with Excel's stored values on 4,453 cells in four countries: all agree (`step2_summary_country.csv`).
2. **Intended value for formulas with functions.** Where my evaluator does not cover a formula (AVERAGE, SUM, MAX: 214 in Costa Rica, 56 in the Dominican Republic, 257 in Guatemala), I took Excel's stored value as the intended value. I labelled these "stored value (own evaluator could not evaluate)". None of these countries lacks stored values.
3. **Text references.** In Ecuador, formulas such as `=+B155` copy a technology name. I let a single reference return text, so these cells get an intended value (the tech name) instead of "not evaluated".
4. **Rounding.** A2 rounds the `numpy.float64` values pandas gives it, and numpy rounds halves to even. My first pass used Python floats and flagged 83 Dominican Republic cells as "different" by 0.0001 (stored value 0.41705). I changed the replica to numpy rounding and, where a stored value exists, used the stored value exactly as A2 read it. After that the 83 cells are ok. Both choices are in `step4_compare.py` (function `r4`, and the comment at the intended-row build).
5. **Classes for cells A2 never reads.** Tech.ID, Tech.Type, "Source / Assumption" and NOTAS columns have no compiled counterpart. No energy `A2_Compiler_*.py` uses them (grep for `Tech.ID`, `Tech.Type` and `'Source` found nothing). I filed them as "not checked" and gave the reason in the `detail` column instead of inventing a fifth class.
6. **Vehicle Techs.** A2 converts units on this sheet (`A2_Compiler_Jamaica.py`, the "Vehicle Techs" block after line 602). I did not replicate that, so a mismatch there is "not checked", not "different": Costa Rica 114 cells, Guatemala 283. These countries have stored values, so A2 read numbers in these cells. Inference: they are not blank-filled.
7. **Downstream file choice.** The brief says to use `<SCEN>_FINAL_0.txt` where present. It is present for all three scenarios in every country, so I used it, and I also read `<SCEN>_0.txt` to tell formula effects apart from Stage 3 patches.
8. **Effect beyond formula cells.** I added a row-level pass (`step5_effect.py`) because a Flat row with a formula in its base year blanks 35 years, not one. This brought Jamaica's count from 594 formula cells to 764 empty compiled values. I classed the 170 extra years under Step 5, not Step 4, because Step 4 asks about formula cells.
9. **Timestamps.** Times in REPORT are UTC. Some `ls` listings during the run showed local time (UTC-7 in May); I converted them with the matching UTC mtimes from `timeline.csv`.

## Breaches and incidents during the run

1. **Empty file outside MODELS_LAC_5.** A mistyped command (`cat > /tmp/x.py`) created the empty file `C:\Users\luisfernando\AppData\Local\Temp\x.py` at 2026-11-09 00:36Z (17:36 local, 8 November). The command then hung waiting for input. I stopped it, checked that the file was empty (0 bytes), and deleted it. No content was written, and nothing inside MODELS_LAC_5 was affected.
2. **Helper files in the session scratchpad.** Two helper text files were first written to the Claude session scratchpad (`C:\Users\luisfernando\AppData\Local\Temp\claude\...\scratchpad\`): an extract of the A2 loop used for the `diff`, and the list of `.py` files naming the A-O. I moved both into this folder as `scratch_a2_loop_jamaica.txt` and `scratch_py_files_naming_ao.txt`. The scratchpad is now empty of my files.

## Files I could not read

None. Every A-O workbook, backup, A2 and B1 CSV, data file and script I needed opened without error.

## Known-limitation candidates (outside the frozen scope, not fixed)

1. **Jamaica's Stage 3 data files predate every A-O change made since 27 January 2026.** `Jamaica/JAM_ENERGY/Executables/<SCEN>_0/<SCEN>_0.txt` are dated 2026-01-27T08:23Z (`timeline.csv`). `stage3_apply.py:559-588` copies them to `_FINAL_0`. So the 12 May `apply_ao_edits.py` edits to "Primary Techs", and any other A-O change since January, are absent from the 16 May Stage 3 run. One visible case: PPPVT 2025 lower bound is 0.5468 by today's formula but 1.4103 in `BAU_0.txt` (`downstream_follow.csv`). Inference: B1 on 12 May wrote `B1_Output_Params/BAU` and `NDCNEW` but not `Executables`, or its data files were later replaced. I did not check which. Jamaica's `B1_Output_Params/LTSNEW` is also still from 27 January.
2. **Ecuador's hydro patch replaced 451 year-column formulas with rule values.** 422 of the new values differ from the formulas' last stored values (`step6_ecuador_451.csv`): CapacityFactor 143 cells set to the first numeric value of the row; lower limits flattened (138); upper limits and MaxCapacity set to 9999 (141). These are deliberate modelling changes (`patch_ao_ecuador_hydro.py` lines 241-308). They did reach Ecuador's data files, which A2 and B1 rebuilt on 14 May. Whether they are right is outside this job.
3. **The Ecuador example `=J207*0.98` from project notes is not in today's workbook.** Inference: it may have been among the 451 cells the patch removed. I did not search the backup for it specifically.
4. **Empty values in compiled CSVs that are not formula-related** (`empty_values_scan.csv`): Dominican Republic 365 per scenario in A2 BAU, NDCNEW and LTSNEW (CapacityToActivityUnit, CapitalCost, FixedCost, OperationalLife, ResidualCapacity, TotalTechnologyAnnualActivityLowerLimit; technologies such as TRXTRAIELE, TRXTRAIFREELE, TRXTTELELE and T5* demand techs); Guatemala 66 per scenario (AvailabilityFactor, CapacityFactor); Ecuador NDCINC 30 (OutputActivityRatio). B1 drops these rows, so the data-file default applies.
5. **Ecuador's 32 Tech-name formulas sit on EMPTY rows.** They are harmless today. If someone gives one of those Demand Techs rows a written Projection.Mode (FixedCost or ResidualCapacity of T5COMGSL, T5TAEGSL and so on) without recalculating first, A2 would write the row with TECHNOLOGY = NaN.
6. **`ao_cost_repair_manager.py` apply mode has the same hazard** (`load_workbook(ao_path, data_only=False)` at line 1476, `wb.save` at 1533). Run on Costa Rica, the Dominican Republic, Guatemala or Honduras, it would strip the stored values of 1,508, 2,109, 883 and 480 formula cells. Earlier job LAC_FUEL_CHECK found that 26 of Jamaica's planned cost cells are formula cells (`fuel_check_20261108T223320Z/planned_formula_cells.csv`); the tool would overwrite those formulas with numbers.
7. **Who wrote Jamaica's `A2_Output_Params/NDCNEW` on 12 May.** `A2_Compiler_Jamaica.py` writes `BAU/` and the `LTS_STR` folder (`LTSNEW`, line 20) only, yet `NDCNEW/` has the same date and the same empty values. I did not trace which script copied it.
8. **Directory mtimes.** All `A2_Output_Params/*`, `Executables/*` and similar directories show a modification time of 2026-11-08 15:02 local, while their files keep older dates. Inference: this comes from copying the tree into MODELS_LAC_5 on 8 November. Gate 1 compares files, not directory mtimes, and found no change.

## Left unchecked

- `Default` scenario folders: they hold header-only CSVs (Guatemala has no matching files), so all Default comparisons are "not checked".
- Vehicle Techs formula cells in Costa Rica (114) and Guatemala (283), and 1 Dominican Republic Vehicle Techs cell in mode "User defined trajectory relative to BY": the replica does not cover them (see judgement 6).
- One Costa Rica Other_Techs formula cell: no matching compiled row (A2 skips Other_Techs rows, `A2_Compiler_Jamaica.py:792`).
- NDCNEW and LTSNEW data files: 91 cells that already differ from the intended value in `_0.txt` on PP activity limits. I attributed them to B1 scenario adjustments by inference, without reading B1's adjustment code.
- I did not check Stage 0 `*_S0_0.txt` files, since the brief names `_FINAL_0` and `_0` only.
- I did not run A2, B1, any stage or any solver (as the brief requires), so all statements about what the solver would do are inference.
