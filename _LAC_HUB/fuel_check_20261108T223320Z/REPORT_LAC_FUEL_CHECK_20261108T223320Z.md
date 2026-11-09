# REPORT LAC_FUEL_CHECK 20261108T223320Z

Fuel price workbook audit and dry-run plan to price fuels in all six country energy models. Dry run only: no workbook was written.

Folder: `MODELS_LAC_5/_LAC_HUB/fuel_check_20261108T223320Z/` (called "this folder" below). Every CSV named here is in this folder.

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| 1. Read-only gate | PASS. All 34 files (fuel workbook, `ao_cost_repair_manager.py`, 32 A-O workbooks under the six energy `A1_Outputs/` folders) have the same SHA-256, size and modification time before and after. | `baseline_before.csv`, `baseline_after.csv`; command `diff baseline_before.csv baseline_after.csv` printed no difference. |
| 2. Nothing written outside this folder | PASS for the model, with one process slip. The tool's `plan --output-dir` option sent all dry-run output into this folder, so no folder was created under `_COST_REPAIR_OUTPUT/` (listing before and after identical). `find MODELS_LAC_5 -newer _LAC_HUB/BRIEF_LAC_FUEL_CHECK.md -type f` outside this folder returned nothing. One stray file was written outside MODELS_LAC_5 (a directory listing to Git Bash `/tmp/x`) and deleted in the next command; see CHANGES. | `_cost_repair_output_listing_before.txt`; commands in CHANGES. |
| 3. Every number traces to a CSV or a command | PASS. Each section names its CSV or command. | |

The fuel workbook SHA-256 is `ab32c8a76ddabb54ed5548ad6447ba01f2bb008e991371a023a6bee37d075e6c`, size 220,764 bytes, as stated in the brief (`baseline_before.csv` row 2).

## Short answer

1. **Can the workbook price all six countries as it stands? No.** (`fuel_coverage.csv`)
   - Natural gas exists only for the Dominican Republic and Jamaica. Costa Rica (`IMPNGS`), Ecuador, Guatemala and Honduras (`DIST_NGS`) have no natural gas series.
   - There is no petroleum coke series. `DIST_COK` (Dominican Republic, Ecuador, Guatemala, Honduras, Jamaica) and `IMPCOK` (Costa Rica) cannot be priced.
   - Coal and crude are only world benchmarks: Newcastle steam coal FOB (USD/t ÷ 24 GJ/t) and Brent. No freight or delivery cost to any country is included. The tool falls back to them for every `DIST_COA`/`IMPCOA` and `DIST_CRU` row.
   - There is no series for Costa Rica aviation gasoline (`IMPAVG`), Guatemala flex fuel (`DIST_FLEXFUEL`) or Honduras uranium (`DIST_URA`).
2. **External, retrievable sources:** 28 of the 4,524 numeric values in `OSeMOSYS_VarCost` have an external, retrievable source when every input in their formula chain is counted (all are Brent benchmark values). Counted by each value's own country or benchmark anchor only, 1,711 of 4,524 are retrievable, 2,790 are external but not retrievable from the reference given, and 23 have no source. Every country value goes through the pass-through factors α and fuel factor. Both cite S034, whose description ("Goldman Sachs / industry consensus") does not match its URL (a World Bank subsidy-reform page), so no country value has a fully retrievable chain. Of the 44 country anchors, 17 are retrievable and 27 are not. Honduras and Guatemala have none retrievable. (`fuel_sources.csv`, `fuel_values_classified.csv`)
3. **Do the tool's units match the models? Yes in unit, no in level.** The workbook gives USD/PJ. The tool divides by 1,000,000 to MUSD/PJ (`ao_cost_repair_manager.py:888-896`), and the A-O unit labels read `M US$ / PJ`, `MUS$ / PJ`, `MUS$/PJ` and `MUSD/PJ` (Costa Rica has no unit text). Planned diesel in 2025 is 18.9 to 29.7 MUSD/PJ against current 12.9 to 27.0 (`dsl_hfo_ngs_2025_2030.csv`), the same order of magnitude. Inference: the level is higher because the workbook anchors are retail pump or ex-refinery prices including taxes (Anchors_Countries column K notes). Costa Rica gasoline, LPG and diesel come out at a median 2.0 to 2.3 times the current values (`fuel_plan.csv`, ratio to A2 BAU).
4. **Cells that would change per country** (`plan_summary.csv`, `fuel_plan.csv`): Costa Rica 180, Dominican Republic 264, Ecuador 3,180 (330 from the fuel workbook plus 2,850 copied from internal Ecuador reference workbooks), Guatemala 198, Honduras 198, Jamaica 315.
5. **Problems to settle before any apply job:**
   - **Missing fuels:** no natural gas for 4 countries, no coke anywhere, coal and crude only as world FOB benchmarks, and no series for `IMPAVG`, `DIST_FLEXFUEL` or `DIST_URA`.
   - **Unsourced values:**
     - α and the fuel factors (S034).
     - The natural gas formula coefficients 0.4 and 0.6.
     - The 30% price floor.
     - Brent 2030 for all scenarios, LOW 2026 and HIGH 2027.
     - The Henry Hub 2026 adjustments.
     - 27 country anchors that are estimates or sit on landing pages.
     - 2018 to 2025 country prices, which are back-cast from the May 2026 anchor through the Brent ratio. S028 (World Bank pump prices) is listed but no cell cites it.
   - **Wrong rows priced** (`fuel_plan.csv`):
     - Ecuador `PPDDSL` and `PPDFOI` are distributed power plants. They get the diesel and fuel oil import price as their VariableCost because "distributed" in their name matches `ao_cost_repair_manager.py:682`.
     - `REF_JET` in Ecuador and Jamaica is a refinery row whose Tech.Name reads "Primary - Import/Distribution - Jet", so it gets the jet import price.
     - Costa Rica `IMPKJF` (kerosene and jet fuel) is priced as kerosene (KRS), not jet.
   - **Internal sources:** in Ecuador, 2,850 cells, including CapitalCost and FixedCost for power plants and refineries, would be copied from internal A-O files (`A-O_Parametrization_PLANMICC.xlsx` and two `reference_*` files). They are marked approved=YES in the manifest. Ecuador `DIST_NGS` 2025 and 2030 planned values (6.9971, 7.4710) equal Jamaica's current `DIST_NGS` values exactly (inference: the Ecuador reference holds Jamaica's gas price).
   - **Unit risks:** 28 cells with ratio above 3 or below 1/3 against a real current price (section Step 5.2).
   - **Uncovered gap rows:** 35 fuel supply rows that are empty, 0 or 1 today stay as they are, including Costa Rica `IMPNGS` and `IMPCOK` and Guatemala `DIST_COK` (Step 5.3).
   - **Formula cells:**
     - 26 of Jamaica's planned cells are formulas (`=AL4` style for 2051 to 2055, and `DIST_COA` 2021). The tool's old-value check (`ao_cost_repair_manager.py:1511-1515`) would stop an apply on them unless `--ignore-old-value-mismatch` is passed, and that option overwrites the formula with a constant.
     - Saving with openpyxl (`:1533`) stores no cached values for formula cells (inference from openpyxl behaviour, not tested here), and A2 reads the A-O file with pandas. Costa Rica (1,508), Dominican Republic (2,109), Guatemala (883) and Honduras (480) formula cells would read as empty after an apply.
     - Ecuador (990) and Jamaica (1,261) A-O workbooks already have no cached values on any formula cell today (`ao_formula_summary.csv`).
   - **Target file:** the tool writes `A-O_Parametrization.xlsx`, which is the right file. The change only reaches the model after A2 and B1 are rerun, and a rerun of A1 regenerates `A-O_Parametrization.xlsx` and would overwrite it (Step 2).

## Step 2. Which A-O file the pipeline reads

Commands: `grep -n "A-O_Parametrization"` over each energy folder's `*.py` and the top-level scripts, plus `grep -n "Print_Paramet\|A2_Output_Params"` in Costa Rica's scripts and YAML files.

The chain is the same in all six countries:

1. The A1 script writes `A1_Outputs/A-O_Parametrization.xlsx` (the structure workbook).
2. A person edits `A-O_Parametrization.xlsx`.
3. A2 reads it with `pd.ExcelFile` and writes two outputs:
   - `A2_Output_Params/<scenario>/*.csv`, which B1 reads.
   - `A-O_Parametrization_COMPLETED.xlsx` and `A-O_Parametrization_Natural_COMPLETED.xlsx`, which are print-outs for the user. No script in the pipeline reads them back. The only `.py` that opens a COMPLETED file is `ecuador_non_energy_cost_repair_manager.py:221-261`, which uses non-energy COMPLETED files as references.
4. B1 reads `A2_Output_Params/` and writes `B1_Output_Params/` and `Executables/*.txt`.
5. Stages 0 to 3 read `B1_Output_Params/` and `Executables/*.txt` only. Examples: `stage0_run.py:8-10, 439`, `stage0_capacity_check.py:121`, `stage1_share_analyzer_v16.py:313`, `stage2_apply_v2.py:218`, `stage3_apply.py:5-6`. None of them opens an A-O file.

The A1 scripts write `A-O_Parametrization.xlsx` from scratch with `pd.ExcelWriter`, so a rerun of A1 replaces any edit.

In each country folder, `A2_Compiler.py` and `A2_Compiler_<Country>.py` are byte-identical (`diff -q`, exit 0). Costa Rica's `A2_Compiler_CostaRica.py` and `A2_Compiler_FPT.py` are also byte-identical (`diff -q`, exit 0).

| Country | File a person edits | Written by (A1) | Read by (A2) | A2 writes COMPLETED | A2 writes CSV for B1 | B1 reads |
|---|---|---|---|---|---|---|
| Costa Rica | `CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx` | `A1_Model_Structure.py:1449` (name from `MOMF_T1_A.yaml:87`) | `A2_Compiler_CostaRica.py:421` | `:1013`, `:1022` (`MOMF_T1_A.yaml:141,144`) | `:1044`, `:1051` | `B1_Base_Scenarios_Adj_Parallel_CostaRica.py:2225, 2253` (`MOMF_T1_B1.yaml:7`) |
| Dominican Republic | `RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | no A1 script in `RD_ENERGY/` (not found) | `A2_Compiler_DominicanRepublic.py:412` | `:986`, `:995` | `:1017` (BAU), `:1027`, `:1029` | `B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py:2203, 2230` |
| Ecuador | `ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx` | `A1_Model_Structure_Energy.py:1498` | `A2_Compiler_Ecuador.py:425` | `:1001`, `:1010` | `:1033`, `:1040` | `B1_Base_Scenarios_Adj_Parallel_Ecuador.py:2149, 2176` |
| Guatemala | `GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | `A1_Model_Structure.py:1273` | `A2_Compiler_Guatemala.py:340` | `:802`, `:811` | `:833`, `:840` | `B1_Base_Scenarios_Adj_Parallel_Guatemala.py:2018, 2045` |
| Honduras | `HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | `A1_Model_Structure_HON.py:1295` | `A2_Compiler_Honduras.py:406` (drops sheet `growth_formula` at `:408`) | `:977`, `:986` | `:1008` | `B1_Base_Scenarios_Adj_Parallel_Honduras.py:2126, 2153` |
| Jamaica | `JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx` | `A1_Model_Structure_JAM.py:1498` (also `_ECU.py:1346`, `_HON.py:1272` in the same folder) | `A2_Compiler_Jamaica.py:418` (drops `growth_formula` at `:420`) | `:989`, `:998` | `:1020`, `:1026` | `B1_Base_Scenarios_Adj_Parallel_Jamaica.py:2128, 2155` |

The step that turns the edited file into model input is A2. `ao_cost_repair_manager.py` writes `A-O_Parametrization.xlsx` (`COUNTRY_MODELS[...]["ao_path"]`, lines 47-78), which is the right file to edit. Conditions:

- A2 then B1 must be rerun before the model sees the change.
- A1 must not be rerun afterwards, or the edit is lost.
- A2 reads cached cell values through pandas, so the openpyxl save issue in Step 4.4 applies.

The A2 "User defined" branch copies each year's value, rounded to 4 decimals (`A2_Compiler_Jamaica.py:544-547`). That is the mode the tool sets.

## Step 3. Fuel workbook audit

### 3.1 Sheets

Script `fuel_wb_dump.py`. Output: `fuel_wb_sheets.csv` and the full text dump `fuel_wb_dump.txt`. Values come from `data_only=True` and formula text from `data_only=False`. All 9,427 formula cells carry cached values ("formula_cells_without_cached_value" is 0 on every sheet).

| Sheet | Purpose | Rows x cols | Formula cells |
|---|---|---|---|
| README | Method, scenarios, colour code, sheet map | 57 x 4 | 0 |
| Sources | Source list S001 to S035 with URL and access date | 39 x 5 | 0 |
| Anchors_International | Brent (USD/bbl), Henry Hub (USD/MMBtu), Newcastle coal (USD/t) anchor years by REF/HIGH/LOW with source IDs | 51 x 7 | 0 |
| Anchors_Countries | May 2026 country anchors (USD/L; NG in USD/MMBtu) with published value, unit, FX, date, source ID, note | 51 x 11 | 0 |
| Anchors_Parameters | Pass-through α by country, fuel factors, energy contents, Brent REF 2026 denominator | 40 x 5 | 1 |
| Scenarios | 2018-2050 Brent, WTI, HH, coal by scenario (anchors plus linear interpolation) | 40 x 13 | 378 |
| Current_Snapshot | May 2026 anchors pulled through, USD/L | 10 x 10 | 42 |
| Country_HND, _CRI, _ECU, _GTM | Projected USD/L, 7 fuels x 3 scenarios, 2018-2050 | 38 x 22 each | 693 each |
| Country_JAM, _DOM | Same, plus natural gas USD/MMBtu block (rows 42-74) | 74 x 22 each | 786 each |
| OSeMOSYS_VarCost | Long form ISO x fuel x scenario, USD/PJ, 2018-2050; the sheet the tool reads | 142 x 38 | 4,662 |

### 3.2 Units

- Country sheets: USD/L (natural gas USD/MMBtu). Anchors_International: Brent USD/bbl, HH USD/MMBtu, coal USD/t.
- `OSeMOSYS_VarCost`: USD/PJ = price ÷ GJ per unit × 1,000,000 (README!B27; formula example `OSeMOSYS_VarCost!F5 = Country_HND!B6/Anchors_Parameters!$C$27*1000000`). Column E repeats the GJ per unit factor.
- GJ per unit factors (Anchors_Parameters!C27:C36), all cited to S026 (IPCC 2006 Guidelines Vol 2, Table 1.2):

| Fuel | Factor | Unit | Note in workbook |
|---|---|---|---|
| Gasoline regular and super | 0.0322 | GJ/L | 44.0 MJ/kg, density about 0.74 kg/L |
| Diesel | 0.0358 | GJ/L | 43.0 MJ/kg, about 0.832 kg/L |
| LPG | 0.0259 | GJ/L | 47.3 MJ/kg, about 0.55 kg/L |
| Kerosene, Jet A-1 | 0.0344 | GJ/L | 43.8 MJ/kg, about 0.80 kg/L |
| Fuel oil | 0.0395 | GJ/L | 40.0 MJ/kg, about 0.99 kg/L |
| Natural gas | 1.055 | GJ/MMBtu | |
| Crude | 6.119 | GJ/bbl | 38.5 MJ/L x 158.987 L/bbl |
| Steam coal | 24 | GJ/t | |

IPCC gives calorific values per mass, so the per-litre factors also rest on the densities shown, and those densities have no cited source (`fuel_sources.csv`).

### 3.3 Coverage

`fuel_coverage.csv` holds one row per country and fuel code, with year range and Excel row for REF, HIGH and LOW. It also lists the A-O fuel supply rows that need each code (mapped with the tool's own `detect_fuel_code`) and a status. The scenarios in the workbook are REF, HIGH and LOW only.

- Every country has GSL, GSP, DSL, LPG, KRS, JTA and HFO for REF/HIGH/LOW, 2018-2050.
- NGS: DOM and JAM only, 2020-2050 (2018 and 2019 are "n/a").
- WORLD: CRD (Brent) 2018-2050, COA (coal) 2024-2050.

Needed but missing:

| Country | Missing |
|---|---|
| Costa Rica | NGS (`IMPNGS`); no code for `IMPCOK`, `IMPAVG`, `IMPELE` |
| Dominican Republic | no code for `DIST_COK`, `IMP_ELE`, `DIST_FIR`, `DIST_BIM`, `DIST_BGS` |
| Ecuador | NGS (`DIST_NGS`); no code for `DIST_COK`, `DIST_BGS`, `DIST_BIM`, `DIST_CHA`, `DIST_FIR`, `DIST_OPE`, `DIST_RDF`, `DIST_OID`, `IMPELE` |
| Guatemala | NGS (`DIST_NGS`); no code for `DIST_COK`, `DIST_FLEXFUEL`, `IMP_ELE`, `DIST_FIR`, `DIST_BIM`, `DIST_BGS` |
| Honduras | NGS (`DIST_NGS`); no code for `DIST_COK`, `DIST_URA`, `IMP_ELE`, `DIST_FIR`, `DIST_BIM`, `DIST_BGS` |
| Jamaica | no code for `DIST_COK`, `DIST_FIR`, `DIST_CHA`, `DIST_BIM`, `DIST_BGS`, `DIST_OPE`, `DIST_PV`, `IMP_STOR`, `IMP_R*`, `IMP_SUB*` |
| All six | COA and CRD only through WORLD FOB/Brent benchmarks |

Some of these rows are not liquid or gas fuels (electricity imports, biomass, refrigerants). They are listed because they carry the `DIST_`/`IMP` prefix. GSP (premium gasoline) is in the workbook for all six but no A-O row uses it.

### 3.4 Sources

`fuel_sources.csv` gives one row per anchor or parameter, with source ID, class and reason, and count rows at the end. `fuel_values_classified.csv` gives the class of each of the 4,524 numeric `OSeMOSYS_VarCost` values. No web page was opened; classification is from the workbook's own descriptions and URL form. The rule is in GAPS.

Country anchors, retrievable out of total (natural gas included where present):

| Country | Retrievable / total | Retrievable fuels |
|---|---|---|
| Dominican Republic | 7 / 8 | all but NGS |
| Jamaica | 5 / 8 | GSL, GSP, DSL, KRS, HFO |
| Ecuador | 3 / 7 | GSL, GSP, DSL |
| Costa Rica | 2 / 7 | GSL, GSP |
| Honduras | 0 / 7 | none |
| Guatemala | 0 / 7 | none |

The other anchors are estimates ("est" in the pricing date, 16 anchors), derivations the source does not state, or values on landing pages that change (GlobalPetrolPrices S013 to S015, Guatemala MEM S024, EIA STEO S006/S007).

Value counts (4,524 values):

| Basis | External, retrievable | External, not retrievable | Internal | None |
|---|---|---|---|---|
| Own anchor | 1,711 | 2,790 | 0 | 23 |
| Weakest link of whole chain | 28 | 3,321 | 0 | 1,175 |

Sources with no ASSUMPTION label and no source:

- Natural gas formula `Anchors_Countries!D50 or D51 x (0.4 + 0.6 x HH(y)/HH REF 2026)` (Country_DOM and Country_JAM rows 44-74).
- 30% floor (README!B26).
- Brent 2030 for all scenarios, LOW 2026 and HIGH 2027.
- HH 2026 adjustments, and HH 2027 HIGH and LOW.

S028 (World Bank pump prices) is cited for 2018-2024 history, but no cell outside `Sources` cites it. The 2018-2025 country prices are computed from the May 2026 anchor and the Brent ratio (Country_XXX formulas, e.g. `Country_HND!B6`), not taken from observed prices.

### 3.5 Diesel, fuel oil and natural gas, REF, 2025 and 2030

Workbook units. From `step3_5_dsl_hfo_ngs_REF.csv` (script `step3_5_table.py`). USD/PJ values are `OSeMOSYS_VarCost!M<row>` (2025) and `R<row>` (2030). USD/L and USD/MMBtu are those values x GJ per unit ÷ 1e6.

| Country | Fuel | 2025 USD/PJ | 2025 USD/L (USD/MMBtu) | 2030 USD/PJ | 2030 USD/L (USD/MMBtu) | Row |
|---|---|---|---|---|---|---|
| CRI | Diesel | 29,712,967 | 1.0637 | 31,633,598 | 1.1325 | 32 |
| CRI | Fuel oil | 13,401,108 | 0.5293 | 14,419,304 | 0.5696 | 44 |
| CRI | Natural gas | not in workbook | | | | |
| DOM | Diesel | 25,741,620 | 0.9216 | 27,589,385 | 0.9877 | 74 |
| DOM | Fuel oil | 17,565,190 | 0.6938 | 19,051,899 | 0.7525 | 86 |
| DOM | Natural gas | 10,052,954 | (10.6059) | 11,563,981 | (12.2000) | 131 |
| ECU | Diesel | 18,892,327 | 0.6763 | 19,857,455 | 0.7109 | 95 |
| ECU | Fuel oil | 13,956,487 | 0.5513 | 14,789,557 | 0.5842 | 107 |
| ECU | Natural gas | not in workbook | | | | |
| GTM | Diesel | 27,762,504 | 0.9939 | 29,960,850 | 1.0726 | 116 |
| GTM | Fuel oil | 12,252,848 | 0.4840 | 13,400,633 | 0.5293 | 128 |
| GTM | Natural gas | not in workbook | | | | |
| HND | Diesel | 24,376,833 | 0.8727 | 26,307,088 | 0.9418 | 11 |
| HND | Fuel oil | 12,252,848 | 0.4840 | 13,400,633 | 0.5293 | 23 |
| HND | Natural gas | not in workbook | | | | |
| JAM | Diesel | 27,919,955 | 0.9995 | 30,345,147 | 1.0864 | 53 |
| JAM | Fuel oil | 16,821,835 | 0.6645 | 18,556,329 | 0.7330 | 65 |
| JAM | Natural gas | 10,300,158 | (10.8667) | 11,848,341 | (12.5000) | 134 |

Guatemala and Honduras fuel oil are identical in every year shown. Their anchors are 0.62 USD/L and their α values are both 0.65 (Anchors_Countries!D11, D46; Anchors_Parameters!C6, C11).

## Step 4. How the tool works (`ao_cost_repair_manager.py`, SHA-256 `55e6dfe2...c371`)

### 4.1 Options, modes, selection

- Global `--root` (default `.`, lines 1688-1693; the help text still says MODELS_LAC_4).
- `plan` (1696-1712):
  - `--country`: default `Ecuador` (45). Accepts a name, a comma list or `all` (1144-1151), against the fixed `COUNTRY_MODELS` table of ISO code and A-O path (47-78).
  - `--fuel-workbook`: default `~/Downloads/LAC_Fuel_Price_Projections_2026_v2_audit.xlsx` (41-43).
  - `--fuel-scenario`: default `REF` (44), matched case-insensitively against the `Scenario` column (940).
  - `--output-dir`: default `_COST_REPAIR_OUTPUT/ao_cost_repair_<local stamp>` (1367-1371). The folder must not exist (358-360).
  - `--top-candidates`: default 5.
  - `--include-review-manifest`.
  - `--replace-existing-fuel-costs`.
- Plan opens A-O workbooks with `read_only=True, data_only=True` (433) and the fuel workbook the same way (904). It writes `manifest.csv`, `mapping_candidates.csv`, `no_safe_match.csv`, `summary.csv` and `run_config.json` (1395-1412).
- `apply` (1714-1721): `--manifest`, `--output-dir`, `--dry-run`, `--apply`, `--include-review`, `--ignore-old-value-mismatch`. It refuses to run without `--dry-run` or `--apply` (1549-1550). There is no `--yes` option.
- `verify` (1723-1727): `--expect applied|original`. Reads with `data_only=True` (1611).
- `restore` (1729-1732): preview, or copy back with `--apply`.
- The fuel workbook must have a sheet `OSeMOSYS_VarCost` (906-907) with a header row in the first 12 rows containing `ISO`, `Fuel Code` and `Scenario`, plus 4-digit year columns (911-927).

### 4.2 Mapping workbook fuels to A-O technologies

A row is a fuel target when all of these hold (`is_fuel_cost_target`, 673-686):

- Its parameter is VariableCost.
- `detect_fuel_code` (634-670) returns a code.
- The tech, Tech.Name or sheet text contains "import", "distribution", "distributed" or "dist ", or the tech starts with `DIST_`, `IMP` or `T4`.

Codes: NGS, LPG, DSL, GSL, HFO (from FOI, HFO or "fuel oil"), KRS (from KER, KRS, KJF or "kerosene"), JTA (from JET or JTA), COA, CRD (from CRU or "crude"). Matching uses whole tokens or the end of the tech code (650). The workbook's GSP is never requested. If a country series is missing, only COA and CRD fall back to `WORLD` (953-956). The output per row is in `ao_fuel_supply_mapping.csv`.

- **Costa Rica `IMP*` and `IMPPUR*`:** handled through the `IMP` prefix and the code suffix: `IMPPURDSL`→DSL, `IMPPURGSL`→GSL, `IMPFOI`→HFO, `IMPLPG`→LPG, `IMPCOA`→COA (WORLD) and `IMPKJF`→KRS. `IMPKJF` is kerosene and jet fuel, but it is priced as kerosene. `IMPNGS`→NGS has no CRI series, so it goes to `no_safe_match.csv`. `IMPCOK`, `IMPAVG` and `IMPELE` get no code and are skipped.
- **`EXTT_*`:** never fuel targets, because they have no import or distribution context. In Ecuador only, `EXTT_CRU` and `EXTT_NGS` VariableCost get values from the internal Ecuador references (1273-1320). In other countries, an `EXTT_*` row that looks suspicious is listed in `no_safe_match.csv` and left alone.
- **`REF_*`:** not fuel targets, unless the Tech.Name contains import or distribution text. `REF_JET` in Ecuador and Jamaica has Tech.Name "Primary - Import/Distribution - Jet" (`ao_varcost_rows.csv`), so it is priced with the jet import price. In Ecuador, the other `REF_*` rows get CapitalCost, FixedCost and VariableCost from the internal references.
- **Rows that are 0 today:**
  - Guatemala `DIST_KER` (0) gets KRS.
  - Dominican Republic `DIST_KER` (0) gets KRS.
  - Guatemala `DIST_COK` (0) has no code and stays 0.
  - Rows are flagged suspicious when all years are empty, at least half are 1, at least 90% are 0 for VariableCost, any are non-numeric, or only one year is filled (550-562). With `--replace-existing-fuel-costs`, every fuel target is planned whether or not it looks suspicious (1213, 1233-1237).
- **Side effect of "distributed":** Ecuador `PPDDSL` and `PPDFOI` ("Distributed Power Plant ...") are power plants, but they pass the test at 682 and receive fuel import prices as VariableCost.

### 4.3 Unit conversion

`fuel_unit_conversion` (888-896) works from the target row's unit text:

- If the text has "pj" and "mus", "m us" or a leading "m", the value is divided by 1,000,000.
- If the text is blank, the value is also divided by 1,000,000 ("default", the Costa Rica case).
- If the text says USD/PJ without M, there is no scaling.

The source unit is hard-coded as "USD/PJ" (1247). The result is MUSD/PJ, which is numerically equal to USD/GJ.

The manifests show `usd_per_pj_to_musd_per_pj` for DOM, ECU, GTM, HND and JAM and `usd_per_pj_to_musd_per_pj_default` for Costa Rica (`plan_*/manifest.csv`, column `unit_conversion`).

Planned diesel compared with current values:

| Country | Planned 2025 (MUSD/PJ) | Current 2025 (MUSD/PJ) | Current value from |
|---|---|---|---|
| Costa Rica | 29.71 | 12.85 | A-O |
| Dominican Republic | 25.74 | 20.88 | A2 BAU |
| Ecuador | 18.89 | 1 | placeholder |
| Guatemala | 27.76 | 20.88 | A2 BAU |
| Honduras | 24.38 | 26.98 | A2 BAU |
| Jamaica | 27.92 | 19.90 | A-O |

Source: `dsl_hfo_ngs_2025_2030.csv`. The magnitude matches the inferred MUSD/PJ (diesel near 15 to 20 in the priced countries). The planned level is 0.9 to 2.3 times the current one.

### 4.4 What it writes

- **Sheet and rows:** the sheet and row of each target in the country's `A-O_Parametrization.xlsx`, one manifest line per changed cell (1002-1063). Cells whose value would not change are skipped (1012).
- **Parameter:** from the fuel workbook, VariableCost only. In Ecuador only (1154-1157), the local references also supply CapitalCost, FixedCost and VariableCost (80-84, 1273-1320). Those references are the internal files `A-O_Parametrization_PLANMICC.xlsx`, `reference_PLANMICC/A-O_Parametrization_ref_planmicc.xlsx` and `reference_edited/A-O_Parametrization_ref.xlsx`.
- **Years:** every year column in the A-O sheet (2021-2050 for CR and ECU, 2018-2050 for DOM, GTM and HND, 2021-2055 for JAM). Years after the last workbook year are held at the last year, and years before the first at the first (962-979). As a result:
  - Jamaica 2051-2055 repeat 2050.
  - NGS 2018-2019 repeat 2020.
  - COA 2018-2023 repeat 2024.
- **Projection.Mode:** set to "User defined" on every changed row (1006, 1523-1531). A2 handles this mode. Rows whose mode would change: DOM 4, ECU 106, GTM 6, HND 6, JAM 2, CRI 0 (from `fuel_plan.csv`, rows with `projection_mode_old` other than "User defined").
- **Approval:** AUTO_HIGH_CONFIDENCE rows are written with `approved=YES` (1003-1004). Every row in all six manifests is AUTO_HIGH_CONFIDENCE and approved=YES (`plan_*/summary.csv`).
- **Apply:**
  - Loads with `data_only=False` (1476).
  - Checks the tech and parameter in each target row (1503-1506).
  - Checks the old value (1511-1515).
  - Writes the value (1522) and the mode (1531).
  - Saves in place (1533).
  - Before editing, it copies each workbook to `<output>/backups/apply_<stamp>/` (1439-1444, 1559-1560).
- **Formula cells:**
  - Plan reads cached values. Apply compares the cell's formula text with the manifest's old value, so any formula target stops the apply with a RuntimeError (1512). With `--ignore-old-value-mismatch`, the formula is overwritten with a number.
  - 26 of Jamaica's 315 planned cells are formulas: `DIST_DSL`, `GSL`, `LPG`, `KER` and `FOI` for 2051-2055 (`=AL4` style), and `DIST_COA` 2021 (`=53*1000000000/(1000000000*35)`). The other five countries have 0 (`planned_formula_cells.csv`, `ao_formula_summary.csv`).
  - Inference, not tested: when openpyxl saves a workbook, it stores no cached value for any formula cell, so pandas in A2 reads those cells as empty until the file is opened and saved in Excel. Ecuador (990 formula cells) and Jamaica (1,261) already have no cached values on any formula cell today, which suggests both were last saved by openpyxl.
- **`--replace-existing-fuel-costs`:** replaces fuel target values that look valid, not only placeholders (1213).

### 4.5 What would stop it for a country other than Ecuador

Nothing at plan time. All six plans ran with exit code 0 and no warnings (`plan_runs_console.txt`, `plan_*/run_config.json`). Issues for an apply job:

- Jamaica's 26 formula targets (4.4).
- The Downloads default path for the fuel workbook, which no longer exists, so `--fuel-workbook` must always be passed.
- The Ecuador-only local references do not exist for other countries, so non-fuel cost rows elsewhere fall to `no_safe_match.csv`. This is expected, not a blocker.
- Run time: the six plan runs together took more than 10 minutes (the command passed the 600 s foreground limit while Jamaica was running). Inference: `read_fuel_series` reopens the workbook for each fuel code and reads cells one at a time in read-only mode (904-945).

## Step 5. Dry-run plan, all six countries

Command, once per country, run from `MODELS_LAC_5` (console log in `plan_runs_console.txt`):

```
py -I ao_cost_repair_manager.py --root . plan --country <Country> --fuel-workbook LAC_Fuel_Price_Projections_2026_v2_audit.xlsx --fuel-scenario REF --replace-existing-fuel-costs --output-dir _LAC_HUB/fuel_check_20261108T223320Z/plan_<Country>
```

`run_config.json` in each `plan_<Country>/` confirms the working-copy fuel workbook path.

`fuel_plan.csv` holds one row per country, sheet, A-O row, technology, parameter and year (4,335 rows). Its columns:

- `current_ao_value`: the A-O cell's value.
- `current_model_value_A2_BAU`: the value the model last compiled, from `A2_Output_Params/BAU/VariableCost.csv`, mode 1. Many A-O rows store only the first year and A2 extends them.
- `planned_value`.
- Both ratios.
- `workbook_cell`: the `OSeMOSYS_VarCost` cell, with a note where a year is held flat.
- `internal_source_if_not_workbook`: for the Ecuador local rows.

Script: `build_fuel_plan.py`.

### 5.1 Per country

| Country | Cells | Rows | Technologies changed |
|---|---|---|---|
| Costa Rica | 180 | 6 | `IMPCOA IMPFOI IMPKJF IMPLPG IMPPURDSL IMPPURGSL` |
| Dominican Republic | 264 | 8 | `DIST_COA DIST_CRU DIST_DSL DIST_FOI DIST_GSL DIST_KER DIST_LPG DIST_NGS` |
| Ecuador | 3,180 | 106 | 330 workbook cells: `DIST_COA DIST_CRU DIST_DSL DIST_FOI DIST_GSL DIST_JET DIST_KER DIST_LPG PPDDSL PPDFOI REF_JET`. 2,850 internal-reference cells on 95 rows (see 5.4). |
| Guatemala | 198 | 6 | `DIST_COA DIST_DSL DIST_FOI DIST_GSL DIST_KER DIST_LPG` |
| Honduras | 198 | 6 | `DIST_COA DIST_DSL DIST_FOI DIST_GSL DIST_KER DIST_LPG` |
| Jamaica | 315 | 9 | `DIST_COA DIST_DSL DIST_FOI DIST_GSL DIST_JET DIST_KER DIST_LPG DIST_NGS REF_JET` |

Sources: `plan_summary.csv` and `plan_*/summary.csv`. The Ecuador total of 3,180 equals the 11 May 2026 dry run `ao_cost_repair_20260511_210318` cited in the brief.

Diesel, fuel oil and natural gas, current versus planned, MUSD/PJ (`dsl_hfo_ngs_2025_2030.csv`). "Current" is the A-O cell, or the A2 BAU value in brackets where the A-O cell is blank because of a growth mode.

| Country | Tech | 2025 current | 2025 planned | 2030 current | 2030 planned |
|---|---|---|---|---|---|
| Costa Rica | IMPPURDSL | 12.8544 | 29.7130 | 14.1228 | 31.6336 |
| Costa Rica | IMPFOI | 9.8646 | 13.4011 | 10.8380 | 14.4193 |
| Costa Rica | IMPNGS | empty | no change (not in workbook) | empty | no change |
| Dominican Republic | DIST_DSL | (20.8829) | 25.7416 | (22.9436) | 27.5894 |
| Dominican Republic | DIST_FOI | 12.9492 | 17.5652 | 14.0210 | 19.0519 |
| Dominican Republic | DIST_NGS | 6.1208 | 10.0530 | 2.9863 | 11.5640 |
| Ecuador | DIST_DSL | (1.0000) | 18.8923 | (1.0000) | 19.8575 |
| Ecuador | DIST_FOI | (1.0000) | 13.9565 | (1.0000) | 14.7896 |
| Ecuador | DIST_NGS | (1.0000) | 6.9971 (internal reference) | (1.0000) | 7.4710 (internal reference) |
| Guatemala | DIST_DSL | (20.8829) | 27.7625 | (22.9436) | 29.9609 |
| Guatemala | DIST_FOI | (14.1002) | 12.2528 | (15.4917) | 13.4006 |
| Guatemala | DIST_NGS | (10.4343) | no change (not in workbook) | (11.4641) | no change |
| Honduras | DIST_DSL | (26.9804) | 24.3768 | (29.6428) | 26.3071 |
| Honduras | DIST_FOI | (15.3504) | 12.2528 | (16.8652) | 13.4006 |
| Honduras | DIST_NGS | (10.4343) | no change (not in workbook) | (11.4641) | no change |
| Jamaica | DIST_DSL | 19.9044 | 27.9200 | 20.6603 | 30.3451 |
| Jamaica | DIST_FOI | 12.8949 | 16.8218 | 13.3896 | 18.5563 |
| Jamaica | DIST_NGS | 6.9971 | 10.3002 | 7.4710 | 11.8483 |

### 5.2 Unit risks: planned more than 3 times or less than 1/3 of a real current price

The current price is the A-O cell, not 0, empty or 1. There are 28 cells, listed in `unit_risks.csv` (basis "A-O cell"). The A2 BAU basis finds the same fuel cells.

| Country | Tech | Parameter | Years | Ratio |
|---|---|---|---|---|
| Costa Rica | IMPPURGSL | VariableCost | 2022 | 3.27 |
| Costa Rica | IMPLPG | VariableCost | 2022 | 3.05 |
| Dominican Republic | DIST_NGS | VariableCost | 2029-2050 (22 cells) | 3.16 to 3.87 (current falls from 3.68 to 2.99 and stays near 3.0-3.2; planned 11.6-12.3) |
| Dominican Republic | DIST_COA | VariableCost | 2023 | 0.29 (19.63 to 5.625; the planned value is FOB Newcastle coal ÷ 24 GJ/t) |
| Ecuador (internal reference) | PPPVD | CapitalCost | 2021 | 10.9 (100 to 1,090) |
| Ecuador (internal reference) | PPBIM | CapitalCost | 2021 | 2,695.5 (2 to 5,391) |
| Ecuador (internal reference) | PPBIM | FixedCost | 2021 | 78.5 (2 to 157) |

### 5.3 Fuel supply rows with a gap today that the plan leaves empty, 0 or 1

`gap_rows.csv` lists every `DIST_*`/`IMP*` VariableCost row that is empty, all 0 or all 1 today: 53 rows. The plan fills 11 from the fuel workbook and 7 from internal Ecuador references, and leaves 35 as they are.

Brief section 3 list:

| Row | Today | Plan |
|---|---|---|
| Costa Rica `IMPNGS` | empty | left empty (no CRI natural gas) |
| Costa Rica `IMPCOK` | empty | left empty (no coke code) |
| Guatemala `DIST_COK` | 0 | left 0 |
| Guatemala `DIST_KER` | 0 | filled (KRS) |
| Dominican Republic `DIST_KER` | 0 | filled (KRS) |
| Jamaica `DIST_COA` | empty (one formula cell without a cached value) | filled from WORLD coal |
| Ecuador, 17 `DIST_*` plus `IMPELE`, all 1 | 1 | 8 filled from the workbook (`COA CRU DSL FOI GSL JET KER LPG`); 7 filled from internal references (`NGS COK OPE BGS BIM CHA FIR`); `DIST_RDF`, `DIST_OID`, `IMPELE` left at 1 |

Others left as they are:

| Country | Rows |
|---|---|
| Costa Rica | `IMPELE` (empty) |
| Dominican Republic | `DIST_FIR`, `DIST_BGS` (0) |
| Guatemala | `IMP_ELE` (0); `DIST_FIR`, `DIST_BIM`, `DIST_BGS` (empty) |
| Honduras | `DIST_FIR`, `DIST_BIM`, `DIST_BGS` (empty) |
| Jamaica | `DIST_FIR`, `DIST_CHA`, `DIST_BIM`, `DIST_BGS`, `DIST_OPE`, `DIST_PV` (0); `IMP_STOR`, 6 `IMP_R*` (empty); 6 `IMP_SUB*` (0) |

Also not priced from the workbook, although they are not empty today:

- `DIST_COK` in DOM, HND and JAM (keep current values).
- `DIST_NGS` in GTM and HND (one year plus a growth mode; keep current).
- Costa Rica `IMPAVG`.
- Guatemala `DIST_FLEXFUEL`.
- Honduras `DIST_URA`.

### 5.4 Rows the plan would change that are not fuel supply rows

Fuel supply means `DIST_*`/`IMP*` VariableCost. There are 2,765 such cells, all in Ecuador and Jamaica (`plan_summary.csv`, column `row_class`).

From the fuel workbook:

| Country | Rows | Cells | Kind |
|---|---|---|---|
| Ecuador | `PPDDSL`, `PPDFOI` | 60 | power plants |
| Ecuador | `REF_JET` | 30 | refinery |
| Jamaica | `REF_JET` | 35 | refinery |

From the internal Ecuador references (Ecuador only), 2,640 cells:

- CapitalCost on 32 rows (960 cells), including `PPBIM`, `PPPVD`, `PPNGS`, `ELE_DIST`, `HYD_G_PROD`, `T5LPG*` and `DIST_COA`/`DIST_CRU`.
- FixedCost on 23 rows (690).
- VariableCost on 18 power-plant and grid rows (540).
- `REF_DSL`, `REF_FOI`, `REF_GSL`, `REF_LPG`: CapitalCost 120, FixedCost 120.
- `REF_*` VariableCost 150 (including `REF_OPE`).
- `EXTT_CRU` and `EXTT_NGS` VariableCost 60.

A further 210 cells on 7 Ecuador fuel supply rows also come from these internal references. Together that makes the 2,850.
