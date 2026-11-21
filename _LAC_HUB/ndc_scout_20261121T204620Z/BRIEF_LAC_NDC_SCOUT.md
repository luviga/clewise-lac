# BRIEF LAC_NDC_SCOUT: published NDC and LTS documents of the six countries, read against the model scenarios

Repository: https://github.com/luviga/clewise-lac. The model state to read is commit `481a7c0` (head of pull request #11, ref `pull/11/head`). That ref exists whether or not pull request #11 has been merged.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, try it at least three different ways, record the block, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge.

This job is read-only for the models. It changes no workbook, no CSV, no compiled file, no script and no stage output. It writes only its own job folder.

## 1. Goal

The CLEWISE paper was designed a year ago with stylized NDC and LTS scenarios, because most of the six countries had not yet published their new documents. They have now. Luis decided on 21 November 2026 to find out what is published, download it, read it, and see how far the model scenarios (BAU, NDCNEW, LTSNEW) agree with it, before any scenario value is changed.

The job delivers, for Costa Rica, the Dominican Republic, Ecuador, Guatemala, Honduras and Jamaica: the documents, every quantified target and measure in them with its page, a comparison with what the models hold, and a list of proposed scenario changes for the hub to decide. It proposes; it does not write.

## 2. The standard

A source is an external document that you downloaded and opened: an http(s) URL, the title, publisher, date, retrieval date, the saved file and its SHA-256. Every value you report carries its document id and page or table. Never write a value from memory or from a search result snippet.

CLG documents are leads, never sources: the Read the Docs sites (endrch-hon, jam-lts, lts-rd), the CLG GitHub country models, CLG reports and workbooks. Follow the external documents they cite.

Quote at most one short phrase per document, and only where the wording of a target matters. Otherwise describe the target in your own words in English, with the original term in parentheses where it helps.

Write in plain English with no em dashes. Commit messages and the pull request description carry no `Co-Authored-By` line and no "Generated with" line of any kind.

Scope is frozen. Do only what section 5 lists. Anything else you notice goes to GAPS under "Known-limitation candidates" with where it is, the values, and one sentence on what it is.

## 3. Facts already checked by values (hub 11, at `481a7c0`)

Model layout:

- Energy models and their compiled inputs: `CostaRica/CR_ENERGY/t1_confection/`, `DominicanRepublic/RD_ENERGY/`, `Ecuador/ECU_Energy/`, `Guatemala/GUA_ENERGY/`, `Honduras/HON_ENERGY/`, `Jamaica/JAM_ENERGY/`, each with `B1_Output_Params/BAU`, `NDCNEW` and `LTSNEW` (one CSV per parameter).
- Solved results: `_STAGE3_RESULTS/stage3_results.xlsx`, sheets `TotalTechnologyAnnualActivity`, `AnnualEmissions`, `AnnualTechnologyEmission`, `NewCapacity`, `TotalCapacityAnnual`, `ProductionByTechnologyAnnual`, `ShareValidation`.
- Power plants start with `PP` (or `PWR` in Costa Rica). Model years start in 2018 (Dominican Republic, Guatemala, Honduras) or 2021 (Costa Rica, Ecuador, Jamaica) and end in 2050.
- The files `AnnualEmissionLimit`, `ModelPeriodEmissionLimit` and `REMinProductionTarget` hold no rows in any scenario. The scenarios are built from plant activity limits (generation shares), transport technology limits and final demand per fuel.
- Solved renewable share of generation, from the last run's report (not recomputed by the hub; recompute it in step C1): NDCNEW in 2035 is 0.750 in the Dominican Republic, Guatemala, Honduras and Jamaica, 0.800 in Ecuador and 0.900 in Costa Rica; LTSNEW in 2050 is 0.990 in all six.
- NDCNEW and LTSNEW inputs differ before 2035 in all six countries (passenger transport demand from 2026 to 2028, plant and transport limits from 2026 or 2027). Luis has decided that LTS will equal NDC through 2035; a later job writes that.

Known unintended differences between BAU and the policy scenarios. A later job removes them. Label them "known unintended difference" in your tables and never read them as policy measures:

- Guatemala `IMP_ELE` lower limit: BAU 5.70, 4.75, 3.80, 4.75, 3.80, 3.80, 3.80 PJ for 2025 to 2031; policy scenarios 0.
- Honduras `IMP_ELE` upper limit: BAU 99,999; policy scenarios 0 from 2025.
- `EmissionActivityRatio` of 18 plant types from 2025: Dominican Republic `PPCOA`, `PPCCTNGS`, `PPCCTNGSDSL`, `PPICEGASFOI`, `PPICEFOI`, `PPCCTDSL`; Ecuador `PPNGS`, `PPRNGS`, `PPDSL`, `PPRDSL`, `PPCRU`, `PPFOI`; Honduras `PPICEDSL`, `PPGTDSL`, `PPCOK`, `PPGTGLP`, `PPBIM`, `PPFOI`.
- History to 2024: Dominican Republic 65 and Jamaica 6 lower-limit cells per policy scenario differ from BAU.

Leads from web search results (hub 11, 21 November 2026). They are leads: open each document and confirm before you use it.

- Costa Rica: NDC 3.0 for 2025 to 2035, submitted 14 November 2025 (record: https://climate-laws.org/document/costa-rica-nationally-determined-contribution-ndc3-0_7b99). Long-term strategy: National Decarbonization Plan 2018-2050, on the UNFCCC long-term strategies portal, 12 December 2019.
- Dominican Republic: NDC 3.0 (record: https://app.climatepolicyradar.org/documents/dominican-republic-s-ndc-3-0-republica-dominicana-ndc-3-0_81dd). Press reports give 28 percent by 2030 and 32 percent by 2035 against the trend scenario.
- Ecuador: second NDC, submitted in early 2025.
- Guatemala: NDC 3.0 (https://unfccc.int/sites/default/files/2026-11/NDC%203.0.pdf), with a table of net emissions by sector in 2035. A long-term strategy is listed on the UNFCCC portal.
- Honduras: NDC 3.0, 2025 (record: https://climate-laws.org/document/honduras-nationally-determined-contribution-ndc3-0_21f1).
- Jamaica: a 2025 NDC; long-term strategy "2050 Long-term Emission Reduction and Climate Resilient Strategy for Jamaica", submitted 29 August 2025 (https://unfccc.int/documents/649405).

In the last job, UNFCCC file addresses returned a bot-check page to scripted downloads. Copies on `cdn.climatepolicyradar.org`, `climate-laws.org` and government sites worked.

## 4. Setup

- Windows, Git Bash. Create a virtual environment with python.org Python (`py -m venv /c/clw_scout_venv`), install `pypdf`, `pdfplumber`, `pandas` and `openpyxl` in it, and run your own scripts with its interpreter. Open workbooks read-only. Read scanned pages as images and say so in the table.
- New clone: `git clone --filter=blob:none https://github.com/luviga/clewise-lac /c/clw_scout`. Branch `job/ndc-scout` from `origin/main`; record the commit it starts from.
- Model state, read-only: in `/c/clw_scout`, run `git fetch origin pull/11/head`, then `git worktree add --detach /c/clw_scout_model FETCH_HEAD`. Check that `git -C /c/clw_scout_model rev-parse --short HEAD` prints `481a7c0`. Read every model file from `/c/clw_scout_model` and never write there.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder: `/c/clw_scout/_LAC_HUB/ndc_scout_<stamp>/`. Create `.gitignore` in it with the line `downloads/`. Copy this brief into the job folder.
- Earlier downloads, read-only, reuse with their SHA-256 where they are the same document: `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\downloads\` (national inventory documents and transparency reports of several countries) and `C:\Users\luisfernando\Desktop\OSeMOSYS\LAC_sources_archive\`.
- Background tasks: at most two at a time. Give each one country (step A to step C for that country) and run the countries in three pairs. Check every value a background task reports against its file before it enters a table.
- Write scripts and text with the file tool. Never use shell heredocs.
- Keep `PROGRESS.md` in the job folder up to date after each step. Commit and push the job folder as work in progress at least every three hours and after each pair of countries.
- Write only inside `/c/clw_scout` and `/c/clw_scout_venv`. Read-only: `/c/clw_scout_model`, `C:\clw_fix`, the main copy `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5`, `LAC_sources_archive`, every other `C:\clw_*` folder, anything under Dropbox and OneDrive.

Expected duration: roughly four to eight hours (estimate; most of it is reading long PDFs).

## 5. Work

### Step A. What is published (per country)

A1. List every document of these kinds, with title, publisher, date of publication or submission, language and URL:

1. Every NDC version on the UNFCCC NDC registry (https://unfccc.int/NDCREG), the newest first.
2. The long-term strategy on the UNFCCC long-term strategies portal (https://unfccc.int/process/the-paris-agreement/long-term-strategies). If none is submitted, the national long-term plan that the newest NDC cites, marked "not submitted to the UNFCCC".
3. The first Biennial Transparency Report and the newest national inventory document, for their mitigation policy tables and emission projections.
4. At most five sector plans per country, and only those the newest NDC or the long-term strategy cites for a quantified energy or transport target (power expansion plan, energy policy, electric mobility plan).

A2. Download each document into `downloads/<country>/`. Write `sources.csv` (id, country, kind, URL, title, publisher, date, accessed, SHA-256, file, pages, language). For a file you cannot fetch after three different attempts, add a row to `sources_pending.csv` with every URL tried and the error, and go on.

A3. Write `published_<country>.md`: half a page saying what exists, what is new since 1 January 2025, and which document is the current NDC and the current long-term strategy.

### Step B. What the documents commit to (per country)

B1. Read the newest NDC and the long-term strategy in full, and the mitigation chapters of the other documents. Write `targets_<country>.csv`, one row per quantified target or measure: source id, page or table, document kind, sector (Energy, Transport, IPPU, Agriculture, LULUCF, Waste, economy-wide), short description, indicator, value, unit, base year or reference (base year, BAU or absolute), target year, conditional or unconditional, gases covered.

Look in particular for: the economy-wide target and its type; sector emission targets; renewable share of generation or of capacity; capacity additions and fossil plant retirements; coal, fuel oil and gas policy; electric vehicle shares or numbers; public transport and modal shift; efficiency; biofuel blending; grid losses; electricity imports, exports and interconnection; forest, agriculture, cement, refrigerant and waste measures.

B2. Where a document prints its own emission projections (BAU and mitigation, total or by sector), copy the series into `projections_<country>.csv` with source id and page.

B3. Spot check: reopen ten values per country, chosen across documents, and confirm value, unit, year and page. Write `spot_checks.csv`. Fix every error the check finds, then check ten more for that country.

### Step C. What the models hold (per country, read-only at `481a7c0`)

C1. Write `model_levers_<country>.csv` from the compiled inputs and the solved results:

- every parameter and technology or fuel whose value differs between BAU and NDCNEW or LTSNEW from 2025 (absolute tolerance 0.00005, relative 0.01 percent), with the values in 2030, 2035 and 2050, grouped as plant limits, transport limits, demand per fuel, grid losses, fuel emission factors, imports, other; mark the known unintended differences of section 3;
- solved per scenario for 2025, 2030, 2035, 2040 and 2050: generation by plant type and the renewable share (state which plant types you count as renewable), installed capacity by plant type, final demand per fuel, the electric share of each transport group, electricity imports, and emissions by label (never sum labels: the sheets hold accidents, congestion and health next to greenhouse gases, and several CO2-equivalent labels overlap).

C2. Write `alignment_<country>.csv`, one row per pair of a document target and the model quantity that corresponds to it: target (source id, page, value, unit, year), model value in the same unit and year for NDCNEW and LTSNEW, ratio, and a status: `matches` (within 10 percent), `same direction, different size`, `opposite direction`, `in documents, not in the model`, `in the model, not in the documents`. Energy and transport targets are compared in numbers. For targets of the other sectors, name the sector model folder that would carry them if its technology names make that clear, and write `not compared` otherwise. Do not run any model.

### Step D. What changed and what to propose

D1. Write `changes_since_paper_<country>.md`, one page: the NDC target year and target type in the current documents against the model design (NDC measures to 2035, then held; LTS to 2050); whether a long-term strategy exists and its headline goal; the five largest disagreements from `alignment_<country>.csv` with their numbers.

D2. Write `proposed_scenario_changes.csv` for all six countries: country, scenario, lever, model rows concerned (workbook, sheet, row at `481a7c0`), current value, proposed value, source id and page, and a class: `A` a value change on a lever the model already has; `B` needs a new lever or a change of model structure; `C` cannot be represented. Propose only what a document states. Where the documents are silent on a lever, write "documents silent" and propose nothing.

D3. Write `cross_country_summary.csv`: per country, the current NDC (date, target year, target type, headline value), the long-term strategy (date, goal), counts of alignment statuses, counts of proposed changes by class.

### Step E. Gates

1. `git diff --name-only origin/main` lists only files under the job folder.
2. Every row of every `targets_`, `projections_` and `alignment_` file has a source id that exists in `sources.csv` and a page or table.
3. Every source file exists with a matching SHA-256.
4. The spot check of B3 ends with ten of ten confirmed for every country.
5. No model file, script or stage output differs from `481a7c0` in `/c/clw_scout_model` (`git -C /c/clw_scout_model status --short` is empty).

### Step F. Pull request

Commit the job folder (without `downloads/`), push `job/ndc-scout`, and open one draft pull request titled "LAC_NDC_SCOUT: published NDC and LTS documents against the model scenarios", body taken from CHANGES.

## 6. Outputs

All three in the job folder, plain English, no em dashes.

`REPORT_LAC_NDC_SCOUT_<stamp>.md`: failed, blocked or pending items first; then one section per country (what is published, the headline targets with pages, the five largest disagreements with the model, the count of proposed changes by class); the cross-country table; gate results; pull request number and commit hashes.

`GAPS_LAC_NDC_SCOUT_<stamp>.md`: every judgement call and its reason; documents not fetched; targets that were ambiguous and how you read them; known-limitation candidates; what was left unchecked; incidents.

`CHANGES_LAC_NDC_SCOUT_<stamp>.md`: the files of the job folder, two or three lines each.
