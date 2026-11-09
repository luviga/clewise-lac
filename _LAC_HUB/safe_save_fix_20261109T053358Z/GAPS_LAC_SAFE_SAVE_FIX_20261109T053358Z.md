# GAPS LAC_SAFE_SAVE_FIX 20261109T053358Z

## Judgement calls

1. **Backup names carry a country prefix.** Both repaired workbooks are called `A-O_Parametrization.xlsx`, so "own name plus suffix" would collide. Backups are `Jamaica_A-O_Parametrization.xlsx.pre_20261109T053358Z` and `Ecuador_A-O_Parametrization.xlsx.pre_20261109T053358Z`. The three script backups use their plain names.
2. **Import line added in each wired script.** The brief says change only the save call, but the helper has to be imported. Each script gets one `sys.path.insert` pointing at the MODELS_LAC_5 root and one `from ao_safe_save import save_ao_safely`. The path insert is also added in `ao_cost_repair_manager.py`, which sits at the root, so the import still works when Python runs in isolated mode (`-I` drops the script folder from the path). Nothing else in the scripts changed (diffs against the backups show only these lines).
3. **Separate Excel instance.** `recalc_in_excel` uses `DispatchEx`, which starts its own Excel process, so it never attaches to or closes an Excel session Luis may have open. It also sets `AskToUpdateLinks=False`, `EnableEvents=False`, `ScreenUpdating=False` and opens with `UpdateLinks=0` so no external link refresh or macro event can alter values. These are additions to the brief's minimum (`Visible=False`, `DisplayAlerts=False`).
4. **What the guard counts as blank.** As specified, only a data-only value of `None`. A formula that evaluates to an Excel error (for example `#DIV/0!`) passes the guard. The repair check counted Excel errors separately: 0 in both workbooks.
5. **Comparison rule for intended values.** Both sides rounded with `numpy.round(x, 4)` (half-to-even) and compared for equality; non-numeric values compared as stripped text. All 2,251 cells were numeric and agreed.
6. **Extra preservation checks.** Beyond the brief, `repair_workbook.py` compared every non-empty cell before and after: same sheet list, same formula cells, same formula text, same plain values (exact, int and float treated as equal when numerically equal). All zero differences. It also confirmed the 451 Ecuador cells in `step6_ecuador_451.csv` are still plain numbers equal to their prior values.
7. **Two "find -newer" lists.** I wrote `ao_safe_save.py` and `test_ao_safe_save.py` and ran the helper test before taking the first backup (the backups of the three scripts, taken just before wiring them). So `find -newer <first backup>` lists the two workbooks and the three scripts but not the helper and test. To cover all files changed by this job I also ran `find -newer start_reference.marker`, a marker whose mtime is set to the stamp time (2026-11-09T05:33:58Z). That list has exactly the 7 expected files.
8. **Ran the existing cost repair unit test.** The brief says not to run the three writer scripts. I did not. I did run `test_ao_cost_repair_manager.py`, which only builds and edits a workbook in a temporary folder, to confirm the wired apply path still works. It passed 4 of 4. It ran with `-B` and without `-I` because it imports its module from the script folder.

## Cells whose recalculated value differs from intended_value

None. Jamaica 0 of 1,261, Ecuador 0 of 990 (`jamaica_mismatches.csv`, `ecuador_mismatches.csv`, header only).

## Known-limitation candidates

- `ao_safe_save.py`, `save_ao_safely`: the openpyxl save happens before the Excel step, so if Excel is missing or fails, the file on disk is already in the no-values state; the call raises, so the writer stops loudly, but the workbook needs a recalculation or restore from the writer's own backup afterwards.
- `ao_safe_save.py`: works only on Windows with Excel and pywin32. Any A-O writer run on another machine will fail at save time.
- `test_ao_cost_repair_manager.py`: now needs Excel and takes about 94 seconds instead of under a second, because its apply and restore steps go through Excel.
- `Ecuador/ECU_Energy/A1_Outputs/patch_ao_ecuador_hydro.py`: still contains "GROUP 4" (lines about 244 to 311 after the edit), which flattens year-column formulas to numbers; the guard does not stop that, because a plain number is not a blank formula.
- Other A-O copies (`reference_*` folders, `models_energy_RE_generation_costs_update/*`, non-energy sector workbooks) were not checked for missing stored values; out of scope.

## Left unchecked

- The Jamaica `A2_Output_Params` and `B1_Output_Params` with the 764 empty values from 12 May: left untouched by design, to be regenerated later.
- Whether Excel 2013 changed any formatting, column widths, defined names, data validation or other workbook metadata on save. Cell values and formula text were checked; formatting was not.
- The Excel recalculation used the workbook's own formulas only; nothing was run downstream (no A2, B1, stage or solver).

## Incidents

- The first helper test run (before I switched to `-B`) wrote `__pycache__/ao_safe_save.cpython-312.pyc` at the root. I deleted that one file, which this job had created; nothing else in `__pycache__` was touched. All later Python runs used `-B`.
- After the first helper test, two `EXCEL.EXE` processes were still listed for a few seconds; they exited on their own once the Python process released them. No Excel process remained after any later step.
- A first attempt at the cost repair test under `-I` failed at import (module not on path) before running anything; rerun without `-I` as noted above.
- A first attempt at the `find -newer <first backup>` command failed because a shell alias appended `*` to the file name; rerun with plain `ls`.
