# BRIEF LAC_FORMULA_CHECK: did A-O formula cells without stored values reach the compiled models as blanks

Working copy: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash: `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens here.
Hub folder: `MODELS_LAC_5/_LAC_HUB/`. This brief lives there.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. This job changes no model file.

## 1. Goal

Each country's energy model starts from `A1_Outputs/A-O_Parametrization.xlsx`. The compiler A2 reads it with pandas, which takes the value Excel stored for each formula cell, not the formula. A workbook last saved by openpyxl stores no values for formula cells, so pandas reads them as empty. Find out, for each of the six countries, whether that has already happened: which formula cells reached `A2_Output_Params` (and from there the B1 outputs and the solver data files) as empty or wrong, which parameters and technologies they touch, and how large the effect is. Then list the ways to fix it, without applying any. The answer decides whether the Stage 3 results of 16 May are sound and how cost edits must be written from now on.

Context: Luis decided on 8 November 2026 that MODELS_LAC_5 is the single working copy and that fuel prices will be rebuilt on an import-parity basis. Another read-only job on price sources may run at the same time in its own folder; ignore it.

## 2. The standard

Report only what you read from the files. Every claim in REPORT names the file, sheet, cell, line or command it came from. Mark inferences as inferences.

Scope is frozen. Do only what section 5 lists. Anything else goes to GAPS under "Known-limitation candidates". Do not fix it.

## 3. Facts already checked by values (job LAC_FUEL_CHECK, `_LAC_HUB/fuel_check_20261108T223320Z/`)

- Energy folders, each under its country folder: Costa Rica `CR_ENERGY/t1_confection`, Dominican Republic `RD_ENERGY`, Ecuador `ECU_Energy`, Guatemala `GUA_ENERGY`, Honduras `HON_ENERGY`, Jamaica `JAM_ENERGY`.
- Chain, same in all six: A1 writes `A1_Outputs/A-O_Parametrization.xlsx`; a person edits it; A2 (`A2_Compiler_<Country>.py`, for example `A2_Compiler_Jamaica.py:418`) reads it with `pd.ExcelFile` and writes `A2_Output_Params/<scenario>/*.csv`; B1 (`B1_Base_Scenarios_Adj_Parallel_<Country>.py`) reads those and writes `B1_Output_Params/` and `Executables/*.txt`; Stages 0 to 3 read only `B1_Output_Params/` and `Executables/`. The A2 "User defined" branch copies each year's value rounded to 4 decimals (`A2_Compiler_Jamaica.py:544-547`).
- Formula cells in the main A-O workbook, and whether any has a stored value (`ao_formula_summary.csv` in that folder): Costa Rica 1,508, Dominican Republic 2,109, Guatemala 883, Honduras 480, all with stored values; Ecuador 990 and Jamaica 1,261, none with a stored value.
- Example formulas: Jamaica `=AL4` style for 2051 to 2055 on fuel supply rows, `DIST_COA` 2021 `=53*1000000000/(1000000000*35)`; Ecuador `=J207*0.98` style (project notes).
- A-O workbook dates: Ecuador 2026-05-14, Jamaica 2026-05-12 (scan of 8 November). Stage 3 results `_STAGE3_RESULTS/stage3_results.xlsx`, 16 May.

## 4. Setup

- Environment: Windows, Git Bash and the `py` launcher. Run your own scripts with `py -I`. pandas and openpyxl are installed. Install nothing. If LibreOffice (`soffice`) is installed, you may use it headless to recalculate copies, never originals.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Create `_LAC_HUB/formula_check_<stamp>/` and put every file you write there, including helper scripts and any recalculated copies.
- Write only inside `_LAC_HUB/formula_check_<stamp>/`.
- Read-only, never write, move, rename or delete: every other file in MODELS_LAC_5. Do not open anything outside MODELS_LAC_5, and nothing under `C:\Users\luisfernando\Dropbox\`.
- Do not run A1, A2, B1, any stage script, any solver, or `ao_cost_repair_manager.py` in apply mode.
- Expected run time: 45 to 90 minutes.

## 5. Work

### Step 1. Baseline for the read-only gate

For each country's energy folder, record SHA-256, size and modification time of the main `A1_Outputs/A-O_Parametrization.xlsx`, and the file count, total size and newest modification time of `A2_Output_Params/`, `B1_Output_Params/` and `Executables/`. Save as `baseline_before.csv`.

### Step 2. Formula inventory

For each main A-O workbook, open once with `data_only=False` and once with `data_only=True`. For every formula cell record sheet, cell, technology and parameter of its row, year of its column, formula text, and stored value (or none). Save as `formula_cells.csv`. In REPORT, per country: count, count without stored value, and counts by parameter and by sheet.

### Step 3. What each formula should be

Work out the intended value of every formula cell:

1. If LibreOffice is available, copy each workbook into the job folder, recalculate the copy headless (convert to xlsx with recalculation), and read the values with `data_only=True`. State the command used.
2. Otherwise, evaluate the formulas yourself where they are simple: cell references, numbers, `+ - * /`, parentheses, and same-sheet references. Follow references to other formula cells recursively. Mark anything else (functions, other sheets, circular references) as "not evaluated" with the reason.

Add the intended value to `formula_cells.csv` with its method.

### Step 4. What the model received

For every formula cell, find the matching value in `A2_Output_Params/<scenario>/<parameter>.csv` for each scenario folder present (match on technology, year and the other keys the CSV uses; read A2's code to see how a row's empty years are filled for each `Projection.Mode`). Classify each cell:

- **ok**: the compiled value equals the intended value (to 4 decimals).
- **blank-filled**: the compiled value is what A2 produces when the cell is empty (state what that is: missing row, 0, the previous year, an interpolation).
- **different**: any other mismatch.
- **not checked**: no intended value, or no matching compiled row.

Save as `formula_vs_compiled.csv`. Also record the modification times of the A-O workbook and of `A2_Output_Params/` for each country, and say which came last.

Then follow every **blank-filled** and **different** cell one step further: does the same wrong value appear in `B1_Output_Params/` and in the BAU, NDCNEW and LTSNEW data files in `Executables/` (`<SCEN>_FINAL_0.txt` where present, else `<SCEN>_0.txt`)? Report per country.

### Step 5. Size of the effect

Per country, list the affected parameters and technologies, the years, and the intended versus compiled values. Group them: costs (CapitalCost, FixedCost, VariableCost), capacity and activity bounds, demand, residual capacity, other. For each group say in one or two sentences what the error would do to the solution (for example, a missing upper bound lets a technology grow without limit; a missing cost makes it free). Do not run the model to prove it.

### Step 6. How it happened

Search all `.py` files in MODELS_LAC_5 (outside `_LAC_HUB` and `__pycache__`) for code that opens an `A-O_Parametrization*.xlsx` with openpyxl and saves it. List file, line and what it changes, and the scripts' dates. Say which of them most likely last saved the Ecuador and Jamaica workbooks, with the evidence. Inference is fine if labelled.

### Step 7. Fix options (do not apply)

List the ways to restore stored values or remove the dependency, with what each changes and its risks. At least: recalculating and saving each workbook in Excel or LibreOffice; replacing formulas by their values; making A2 evaluate formulas; writing future edits with a method that keeps stored values. Say which countries need which, and what must be rerun afterwards (A2, B1, Stages 0 to 3).

### Step 8. Gates

1. Read-only gate: repeat Step 1 into `baseline_after.csv`. All must match. Any difference is a failure: report it at the top of REPORT.
2. Nothing written outside `_LAC_HUB/formula_check_<stamp>/`. List the files you created.
3. Every number in REPORT traces to a CSV in the output folder or a command shown in REPORT.

## 6. Outputs

All in `_LAC_HUB/formula_check_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_FORMULA_CHECK_<stamp>.md`: start with the gate results. Then a short answer: per country, whether formula cells reached the compiled model wrongly (yes, no, or partly, with counts), the most serious effects, how it most likely happened, and the fix you would choose and why. Then sections for Steps 2 to 7.

`GAPS_LAC_FORMULA_CHECK_<stamp>.md`: every judgement call and its reason; files you could not read; "Known-limitation candidates"; anything left unchecked.

`CHANGES_LAC_FORMULA_CHECK_<stamp>.md`: every file you created, with its purpose in one line. Confirm that no file outside the output folder changed.

Supporting files: `baseline_before.csv`, `baseline_after.csv`, `formula_cells.csv`, `formula_vs_compiled.csv`, any recalculated copies, and your helper scripts.
