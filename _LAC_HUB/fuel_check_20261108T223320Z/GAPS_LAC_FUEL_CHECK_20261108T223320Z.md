# GAPS LAC_FUEL_CHECK 20261108T223320Z

## Judgement calls and reasons

1. **Baseline scope.** "Every `A-O_Parametrization*.xlsx` under each country's energy folder `A1_Outputs/`" was read as recursive, so the 32 files include the `reference_*`, `SinNGSCOM` and backup copies. `Ecuador/ECU_Energy/_DISTANCE_RERUNNER/A1_Outputs/` was left out because it is not the energy folder's own `A1_Outputs/`.
2. **Where dry-run output went.** The tool has `plan --output-dir` (`ao_cost_repair_manager.py:1700`), so each plan was written to `plan_<Country>/` in this folder and nothing to `_COST_REPAIR_OUTPUT/`. This is the option that changes least.
3. **One run per country.** I did not use `--country all`, so each country's output stands alone, as the brief asks per country.
4. **Option B flags.** "Every fuel supply row priced from the workbook" was taken to mean `--replace-existing-fuel-costs`. `--include-review-manifest` was not used because it adds review rows and is not needed for option B. Scenario REF only; HIGH and LOW were not planned.
5. **Python flags.** The tool was run with `py -I`, the same as my own scripts. `build_coverage_sources.py` imports the tool's functions to reuse its own fuel-code mapping; it was run with `-B` and the existing `__pycache__/ao_cost_repair_manager.cpython-312.pyc` kept its 2026-05-11 timestamp.
6. **What counts as a fuel supply row.** `DIST_*` and `IMP*` VariableCost rows. `REF_*` (refinery) and `EXTT_*` (extraction) are reported separately, following the brief's own naming in section 3. The `IMP_R*` and `IMP_SUB*` refrigerant rows, `IMP_STOR` (clinker), `IMP_ELE`/`IMPELE` (electricity) and the ETD biomass rows match the prefix and are listed, but they are not fuels the workbook should be expected to price.
7. **Extra "current" column.** Many A-O fuel rows hold only the first year with "Percent growth of incomplete years" or "Flat", and A2 fills in the rest. So I added `current_model_value_A2_BAU` from `A2_Output_Params/BAU/VariableCost.csv` (mode 1, read-only) next to the A-O cell value. Unit risks are reported on the A-O cell basis the brief asks for. The A2 basis is given as well and finds the same fuel cells.
8. **Source classification rules** (no web page was opened):
   - R: a dated article or document whose description in `Sources` states the value used.
   - NR: a landing page whose content changes (GlobalPetrolPrices, MEM Guatemala, EIA STEO landing page), or a value marked "est", or a value derived in a way the source does not state.
   - NONE: no source and no ASSUMPTION label.
   - Interpolated years take the weaker class of the two anchors around them.
   - For a whole formula chain, the class is its weakest input.
   - Energy contents (S026, IPCC) were classed R because IPCC is a fixed public document, although the densities used to reach per-litre values have no source.
   - S029 (Energy Institute) was classed R for 2018-2023 Brent because it is a stable historical series, although its URL is a landing page.
   - These calls set the counts in `fuel_sources.csv`. A different rule for landing pages would move Honduras super gasoline and Guatemala gasoline and diesel from NR to R.
9. **"Workbook's own units" in Step 3.5.** Both USD/PJ (`OSeMOSYS_VarCost`) and USD/L or USD/MMBtu (Country sheets) are shown. The USD/L figure is USD/PJ x GJ/L ÷ 1e6, which reproduces the Country sheet value.
10. **Coverage "needed".** "Needed" means an A-O `DIST_*`/`IMP*` row exists. The fuel code was assigned with the tool's own `detect_fuel_code`, not my own mapping, so the coverage matrix shows what the tool would look for.

## Files that could not be read

None. All 32 baseline A-O workbooks were hashed. The six main energy A-O workbooks, the fuel workbook, the tool, the A1/A2/B1 scripts named in REPORT Step 2, the top-level stage scripts (by grep) and the six `A2_Output_Params/BAU/VariableCost.csv` files were read.

## Process slip

While checking for new `_COST_REPAIR_OUTPUT` folders, one command wrote a directory listing to Git Bash `/tmp/x`, which is outside MODELS_LAC_5 and outside this folder. The next command deleted it (`rm -f /tmp/x`). It held only folder names from `_COST_REPAIR_OUTPUT/`. No model file was involved.

## Known-limitation candidates (recorded, not fixed)

1. The tool's default fuel workbook path is `~/Downloads/...` (`ao_cost_repair_manager.py:41-43`), and that file no longer exists. Every run must pass `--fuel-workbook`.
2. `--root` help text says MODELS_LAC_4 (1692). `source_projection_mode` is hard-coded "REF trajectory" (1248) whatever `--fuel-scenario` is.
3. `is_fuel_cost_target` matches "distributed" (682), so Ecuador's distributed power plants `PPDDSL` and `PPDFOI` get fuel prices as VariableCost.
4. `REF_JET` in Ecuador and Jamaica has Tech.Name "Primary - Import/Distribution - Jet" in the A-O workbook, so it is treated as an import row.
5. Costa Rica `IMPKJF` (kerosene and jet fuel) maps to KRS. The tool never requests JTA for it, and never requests GSP (premium gasoline) for any country.
6. No COK code, no country NGS for CRI/ECU/GTM/HND, and no delivered coal or crude series. The tool falls back to WORLD FOB coal and Brent for every country (953-956).
7. In Ecuador, local reference rows from internal A-O files are AUTO_HIGH_CONFIDENCE and approved=YES. A fuel-only apply would have to filter the manifest to `source_kind = fuel_workbook`. The Ecuador `DIST_NGS` reference values equal Jamaica's current `DIST_NGS` values (inference: copied across models).
8. Apply on formula cells: the old-value check raises on the first formula cell (1511-1515), and `--ignore-old-value-mismatch` replaces formulas with numbers.
9. openpyxl save (1533) leaves formula cells without cached values (inference from openpyxl behaviour, not tested). A2 reads through pandas.
10. Ecuador (990) and Jamaica (1,261) A-O workbooks already have no cached values on any formula cell (`ao_formula_summary.csv`). Inference: A2 already reads these cells as empty today. This affects Jamaica `DIST_COA` 2021 and the Jamaica 2051-2055 fuel price years, plus whatever the Ecuador formula cells feed. Not checked further.
11. A rerun of A1 regenerates `A-O_Parametrization.xlsx` (REPORT Step 2 table) and would undo any applied fuel prices.
12. The Dominican Republic energy folder has no A1 script, so it is unknown how its A-O workbook is regenerated.
13. Jamaica has three A1 variants (`A1_Model_Structure_JAM.py`, `_ECU.py`, `_HON.py`), and Guatemala and Dominican Republic have several B1 variants. Which one is canonical was not established.
14. Workbook 2018-2025 country prices are back-cast from the May 2026 anchor with the Brent ratio, not observed prices. S028 is listed but unused.
15. Workbook prices are retail or ex-refinery including taxes and subsidies (Anchors_Countries notes; README!B29-B31). Inference: these are not import-parity supply costs, and this explains planned diesel at 1.3 to 2.3 times current in Costa Rica and Jamaica.
16. Jamaica's A-O years run to 2055 but the workbook ends in 2050. The tool holds 2050 flat.
17. Plan run time is long. The six runs together took more than 10 minutes, most of it in Jamaica (inference: per-cell reads in read-only mode, 904-945).
18. The HIGH and LOW scenarios exist in the workbook, but the A-O file holds one value per row. How HIGH and LOW would reach the model (separate A-O copies, or B1 scenario settings) is not defined by the tool.
19. The `current_model_value_A2_BAU` column assumes each country's `A2_Output_Params/BAU/VariableCost.csv` was compiled from the present A-O workbook. That was not checked. Where the A-O cell holds a value, the two columns agree to 4 decimals in `dsl_hfo_ngs_2025_2030.csv`.

## Left unchecked

- Whether any source URL resolves, and whether it states the value. This is by design: no web search.
- Whether the IPCC Table 1.2 values match the workbook's MJ/kg figures.
- HIGH and LOW dry runs.
- The tool's `apply --dry-run` and `verify` were not run. They read the manifest and the A-O workbooks and do not write to them (1549-1596, 1599-1660), but an `apply --dry-run` writes an apply log next to the manifest, and the brief did not ask for it.
- The A2 behaviour for the B1 scenarios (NDCNEW, LTSNEW) beyond BAU.
- Whether the Ecuador A-O formula cells feed any VariableCost the model uses.
- The tool's unit tests (`test_ao_cost_repair_manager.py`) were not run.
