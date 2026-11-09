# BRIEF LAC_FUEL_CHECK: fuel price workbook audit and a dry-run plan to price fuels in all six countries

Working copy (the model): `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash: `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens here.
Hub folder (briefs and job outputs): `MODELS_LAC_5/_LAC_HUB/`. This brief lives there. It holds no model input; the pipeline does not read it.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. This job writes no model input.

## 1. Goal

Luis decided on 8 November 2026 that fuel prices in all six country energy models (Costa Rica, Dominican Republic, Ecuador, Guatemala, Honduras, Jamaica) will come from one workbook, `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx`, written into each country's A-O workbook by `ao_cost_repair_manager.py`. That gives the six countries one price base, which the later fuel price scenarios (HIGH and LOW) need. Before anything is written, find out: what the workbook holds and cites; how the tool maps its fuels to each country's technologies and converts units; what a write would change in each country, value by value; and which A-O file the pipeline actually reads. Produce a dry-run plan only.

## 2. The standard

Every value the model uses must have an external, retrievable source (URL, DOI or public document) or a plain ASSUMPTION label. Internal files are never a source. Report only what you read from the files; every claim names the file, sheet, cell range, line or command it came from; mark inferences as inferences.

Scope is frozen. Do only what section 5 lists. Anything else goes to GAPS under "Known-limitation candidates". Do not fix it.

## 3. Facts already checked by values

From an earlier read-only scan of 8 November 2026 (`cost_check_detail.csv`, first stored VariableCost values in each main energy A-O workbook, `<country energy folder>/A1_Outputs/A-O_Parametrization.xlsx`; Costa Rica under `CostaRica/CR_ENERGY/t1_confection/`):

- Fuel supply technologies are named `DIST_<FUEL>` in Dominican Republic, Ecuador, Guatemala, Honduras and Jamaica, and `IMP<FUEL>` or `IMPPUR<FUEL>` in Costa Rica (for example `IMPPURDSL`, `IMPFOI`, `IMPNGS`, `IMPCOK`). Domestic extraction is `EXTT_<FUEL>`; refineries are `REF_<FUEL>`.
- Ecuador: every VariableCost row is the placeholder 1, fuel supply included (`DIST_DSL`, `DIST_FOI`, `DIST_NGS`, `DIST_CRU` and others).
- Current diesel supply prices, first stored year: Dominican Republic `DIST_DSL` 19.948, Guatemala `DIST_DSL` 19.948, Honduras `DIST_DSL` 15.284, Jamaica `DIST_DSL` 18.918, Costa Rica `IMPPURDSL` 11.922. The units are not stated in the files; MUSD/PJ is an inference.
- Gaps among fuel supply rows: Costa Rica `IMPNGS` and `IMPCOK` empty; Guatemala `DIST_COK` and `DIST_KER` 0; Dominican Republic `DIST_KER` 0; Jamaica `DIST_COA` empty.
- `ao_cost_repair_manager.py` ran twice on 11 May 2026 for Ecuador, dry run only (`_COST_REPAIR_OUTPUT/ao_cost_repair_20260511_205736/` and `..._210318/`), scenario `REF`, with 3,210 and 3,180 cells approved. Its default fuel workbook path pointed to Downloads, where the file no longer exists; the copy in the working copy is 220,764 bytes, dated 2026-06-08, SHA-256 `ab32c8a76ddabb54ed5548ad6447ba01f2bb008e991371a023a6bee37d075e6c`.
- Project notes (lead, check it): the v2 workbook is the authoritative one and v1 must not be used; it carries a GJ per unit column, full-precision USD/PJ values and audit trail sheets. openpyxl cannot evaluate formula cells, and some A-O workbooks (Ecuador) contain formula cells.

## 4. Setup

- Environment: Windows, Git Bash and the `py` launcher. Run your own scripts with `py -I`. pandas and openpyxl are installed. Install nothing.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Create `_LAC_HUB/fuel_check_<stamp>/` inside MODELS_LAC_5 and put every file you write there, including helper scripts.
- Write only inside `_LAC_HUB/fuel_check_<stamp>/`. One exception: if `ao_cost_repair_manager.py` has no option to send its dry-run output elsewhere, it may create new timestamped folders under `MODELS_LAC_5/_COST_REPAIR_OUTPUT/`; list each one in CHANGES.
- Read-only, never write, move, rename or delete: every file in MODELS_LAC_5 (above exception aside) and everything else in `_LAC_HUB`.
- Do not open anything outside MODELS_LAC_5, and nothing under `C:\Users\luisfernando\Dropbox\2_WORK\`. The old model copies there are online-only archives, and reading them downloads them.
- Never run the tool in apply mode. Never pass `--yes` or any flag that writes to a workbook. Do not run any model or solver.
- Expected run time: 45 to 90 minutes.

## 5. Work

### Step 1. Baseline for the read-only gate

Record SHA-256, size and modification time of: the fuel workbook; every `A-O_Parametrization*.xlsx` under each country's energy folder `A1_Outputs/` (not the staging folder `models_energy_RE_generation_costs_update`); and `ao_cost_repair_manager.py`. Save as `baseline_before.csv`.

### Step 2. Which A-O file the pipeline reads

Each energy folder holds `A-O_Parametrization.xlsx`, `A-O_Parametrization_COMPLETED.xlsx` and `A-O_Parametrization_Natural_COMPLETED.xlsx`. Read the scripts that build the model inputs (the `A1`/`A2` scripts in each country energy folder, the `B1_Base_Scenarios_Adj_Parallel*.py` runners, and the Stage 0 to Stage 3 scripts at the top level) and find which of the three each one opens and which one writes the others. State, per country: the file a person edits, the file the model build reads, and the step that turns one into the other. Name the script and line for each. Say which file `ao_cost_repair_manager.py` writes, and whether that is the right one.

### Step 3. Fuel workbook audit

Open the workbook read-only and report:

1. Every sheet: name, purpose in one line, size (rows by columns), and whether it holds formula cells (open once with `data_only=False` to count formulas, once with `data_only=True` for values).
2. Units: the unit of each price column, and the GJ per unit factors with their sources.
3. Coverage: a matrix of country by fuel by price scenario by year range. List the scenario names (REF, HIGH, LOW or others). Mark every country and fuel the A-O workbooks need (Step 4) that the workbook lacks.
4. Sources: for every fuel and country, the source the workbook gives (URL, DOI, report title and year). Classify each as external and retrievable, external but not retrievable from the reference given, internal (a file, sheet, chat or note), or none. Count values per class. Do not search the web for missing sources; list them.
5. Diesel, fuel oil and natural gas in 2025 and 2030, REF scenario, all six countries, in the workbook's own units, as a table.

Save the matrix as `fuel_coverage.csv` and the source classification as `fuel_sources.csv`.

### Step 4. How the tool works

Read `ao_cost_repair_manager.py` and report, with line numbers:

1. Its command-line options and defaults, its plan, apply and verify modes, and how it chooses the country, the scenario and the fuel workbook.
2. How it maps workbook fuels to A-O technologies for each country. Say whether it handles Costa Rica's `IMP*` and `IMPPUR*` names, `EXTT_*` and `REF_*` rows, and the Guatemala and Dominican Republic rows that are 0 today.
3. Its unit conversion from the workbook to the A-O values, with the factor, and whether the result matches the inferred MUSD/PJ (diesel near 15 to 20 per PJ in the countries already priced).
4. What it writes: sheet, rows, parameter (VariableCost only, or also other cost parameters), years, the `Projection.Mode` it sets, and how it treats formula cells, backups and existing values (`--replace-existing-fuel-costs`).
5. Anything that would stop it from running for a country other than Ecuador.

### Step 5. Dry-run plan, all six countries

Point the tool at the working copy's fuel workbook (`MODELS_LAC_5/LAC_Fuel_Price_Projections_2026_v2_audit.xlsx`) explicitly, never the Downloads default. For each of the six countries, run its plan or dry-run mode for scenario REF, with existing fuel costs replaced if that is what option B needs (that is, every fuel supply row priced from the workbook). If the tool cannot run for a country, record why and continue with the others.

From its outputs build `fuel_plan.csv`, one row per country, technology and year: current value, planned value, ratio planned to current, and the workbook cell it came from. Then in REPORT:

1. Per country: how many cells would change, which technologies, and diesel, fuel oil and natural gas in 2025 and 2030, current versus planned.
2. Every planned value more than 3 times or less than one third of the current one, where the current value is a real price (not 0, empty or 1). These are unit risks.
3. Every fuel supply row with a gap today (section 3 list, plus any others you find) that the plan leaves empty, 0 or 1.
4. Any row the plan would change that is not a fuel supply row.

### Step 6. Gates

1. Read-only gate: repeat Step 1 into `baseline_after.csv`. Every hash must match. Any difference is a failure: report it at the top of REPORT.
2. Nothing written outside `_LAC_HUB/fuel_check_<stamp>/`, apart from any dry-run folders under `MODELS_LAC_5/_COST_REPAIR_OUTPUT/`, each listed in CHANGES.
3. Every number in REPORT traces to a CSV in the output folder or a command shown in REPORT.

## 6. Outputs

All in `_LAC_HUB/fuel_check_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_FUEL_CHECK_<stamp>.md`: start with the gate results. Then a short answer: whether the workbook can price all six countries as it stands; how many of its values have an external, retrievable source; whether the tool's units match the models; how many cells would change per country; and the list of problems that must be settled before an apply job (unit risks, uncovered rows, unsourced values, the wrong target file). Then sections for Steps 2 to 5.

`GAPS_LAC_FUEL_CHECK_<stamp>.md`: every judgement call and its reason; files you could not read; "Known-limitation candidates"; anything left unchecked.

`CHANGES_LAC_FUEL_CHECK_<stamp>.md`: every file and folder you created, with its purpose in one line. Confirm that no A-O workbook, the fuel workbook or the tool changed.

Supporting files: `baseline_before.csv`, `baseline_after.csv`, `fuel_coverage.csv`, `fuel_sources.csv`, `fuel_plan.csv`, and your helper scripts.
