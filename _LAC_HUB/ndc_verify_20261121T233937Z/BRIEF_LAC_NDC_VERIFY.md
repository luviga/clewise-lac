# BRIEF LAC_NDC_VERIFY: check every published value three times, put all of them in one unit system, and list every value held in code

Repository: https://github.com/luviga/clewise-lac, `main` at `a76ad81` (pull request #12 merged on 21 November 2026).

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, try it at least three different ways, record the block, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge.

This job is read-only for the models. It changes no workbook, no CSV, no compiled file, no script and no stage output. It writes only its own job folder.

## 1. Goal

Luis decided on 21 November 2026 that the NDC and LTS scenarios of the six models will use the values the countries have published, in place of the stylized values the models hold now. Before any value enters a model it is checked three times, expressed in one unit system so that document and model can be compared, and written to one table. He also decided that no value of the system may live in code: every number and every name of a country, scenario, technology or fuel will sit in an external table, and the repository will follow the layout of https://github.com/Climate-Lead-Group/OSTRAM.

This job prepares both. It delivers:

1. `scenario_values.csv`, the checked list of published values that a later job will load;
2. the supporting analyses behind each NDC and long-term strategy, and a note per country on what a deeper study would need;
3. `script_constants.csv`, the list of every value and element name that is written in code today.

It proposes and lists. It writes nothing into a model.

## 2. The standard

A source is an external document that you downloaded and opened: an http(s) URL, the title, publisher, date, retrieval date, the saved file and its SHA-256. Every value carries its document id and page or table. Never write a value from memory or from a search result snippet.

CLG documents are leads, never sources: the Read the Docs sites (endrch-hon, jam-lts, lts-rd), the CLG GitHub country models, CLG reports and workbooks. In this job you read them, because they describe the analysis behind several official documents. Record what they say and mark every such row `lead`. A row of `scenario_values.csv` always cites a document published by a government, the UNFCCC or another external body.

Quote at most one short phrase per document, and only where the wording of a target matters. Write in plain English with no em dashes. Commit messages and the pull request description carry no `Co-Authored-By` line and no "Generated with" line of any kind.

Scope is frozen. Do only what section 5 lists. Anything else you notice goes to GAPS under "Known-limitation candidates" with where it is, the values, and one sentence on what it is.

## 3. Facts already checked by values (hub 11)

The scout job, now on `main`: `_LAC_HUB/ndc_scout_20261121T204620Z/`. Its files use the country codes CR, DR, ECU, GUA, HON, JAM. It holds `sources.csv` (46 documents), `sources_pending.csv` (12), `targets_<code>.csv` (549 rows), `projections_<code>.csv` (505), `model_levers_<code>.csv`, `alignment_<code>.csv` (352), `proposed_scenario_changes.csv` (122 rows: 60 class A, 22 class B, 8 class C, 32 with the documents silent) and `published_<code>.md`. The downloaded documents are not in git; they are on this machine in `C:\clw_scout\_LAC_HUB\ndc_scout_20261121T204620Z\downloads\<code>\`. In its tables `page` is the physical PDF page, counted from 1.

Hub checks of that job:

- The hub opened the Guatemala NDC 3.0 itself and found the scout's values: 23.7 percent below BAU in 2035, BAU 75,738.0 and mitigation 57,763.7 kt CO2 eq, energy and transport cut 1,184.9 kt in 2035. The values of the other five countries have had one reading only.
- Solved plant output from 2025 follows the stage controller and not the compiled B1 limits. Guatemala NDCNEW 2030 `PPCOA`: compiled 12.5965 to 13.8562 PJ, solved 17.2176.
- The renewable targets are constants typed twice, in `stage1_share_analyzer_v16.py` (lines 97 to 110) and `stage2_apply_v2.py` (lines 61 to 75): NDCNEW 0.75 in 2035 and 2050; LTSNEW 0.75 in 2035 and 0.99 in 2050; Costa Rica 0.90 and 0.90 (LTSNEW 0.99 and 0.99); Ecuador 0.80 and 0.80 (LTSNEW 0.80 and 0.99).
- The scout counted renewable plant types by name pattern. Costa Rica `PWRSUG` (sugarcane) was counted as non-renewable.
- Scenario names in the energy models: `BAU`, `NDCNEW`, `LTSNEW`. Other names appear in folders and logs: `NDCcond`, `NDCincond`, `NDP`, `NDPAMB`, `NDCINC`, `LTSOPT`, `Default`. Luis decided the final names are `BAU`, `NDC` and `LTS`.

Known unintended differences between BAU and the policy scenarios, which a later job removes. Never read them as policy measures: Guatemala `IMP_ELE` lower limit (BAU 5.70, 4.75, 3.80, 4.75, 3.80, 3.80, 3.80 PJ for 2025 to 2031, policy 0); Honduras `IMP_ELE` upper limit (BAU 99,999, policy 0 from 2025); `EmissionActivityRatio` of 18 plant types from 2025 in the Dominican Republic, Ecuador and Honduras; history rows to 2024 in the Dominican Republic and Jamaica.

Leads for step D, to be opened and confirmed: the Guatemala NDC 3.0 credits the IDB, the 2050 Pathways Platform and UNDP for support and the Climate Lead Group, Universidad del Valle de Guatemala and Universidad Galileo for technical support (GUA-01, credits pages). A UNFCCC case study says a team including the Climate Lead Group, the University of the West Indies and CIRED did the analysis for Jamaica's long-term strategy with 2050 Pathways Platform support (https://unfccc.int/about-us/regional-collaboration-centres/rcc-events/building-a-long-term-vision-for-climate-resilience-in-jamaica). Sites: http://www.2050pathways.org/, https://ndcpartnership.org, https://jam-lts.readthedocs.io, https://lts-rd.readthedocs.io, https://endrch-hon.readthedocs.io, https://api.github.com/orgs/Climate-Lead-Group/repos.

Scripted downloads from unfccc.int file addresses worked in the scout job; the long-term strategies portal page showed a bot check.

## 4. Setup

- Windows, Git Bash. Reuse the clone `C:\clw_scout` (`/c/clw_scout`): `git fetch origin`, then `git switch -c job/ndc-verify origin/main`. Record the commit it starts from. The ignored `downloads/` folder of the scout job stays on disk; check that it holds the 46 files with their SHA-256 before you start, and download again any that is missing.
- Model state, read-only: the worktree `/c/clw_scout_model` at `481a7c0`, whose model files are identical to `main`. If it is missing, run `git fetch origin pull/11/head` and `git worktree add --detach /c/clw_scout_model FETCH_HEAD`. Never write there.
- Python: the virtual environment `/c/clw_scout_venv` (pypdf, pdfplumber, pandas, openpyxl). Create it again if it is missing. Open workbooks read-only.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`. Job folder: `/c/clw_scout/_LAC_HUB/ndc_verify_<stamp>/`, with a `.gitignore` holding the line `downloads/`. Copy this brief into it. New downloads go to `downloads/<code>/` of this job folder.
- Background tasks: at most two at a time. Check every value a background task reports against its file before it enters a table.
- Write scripts and text with the file tool. Never use shell heredocs.
- Keep `PROGRESS.md` up to date after each step. Commit and push the job folder as work in progress after each step.
- Write only inside the job folder and `/c/clw_scout_venv`. Read-only: the scout job folder, `/c/clw_scout_model`, `C:\clw_fix`, the main copy `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5`, `LAC_sources_archive`, every other `C:\clw_*` folder, anything under Dropbox and OneDrive.

Expected duration: roughly three to five hours (estimate).

## 5. Work

### Step A. The list of values to verify

Write `values_to_verify.csv` from the scout tables. Include every `targets_` row that is cited by a class A or class B row of `proposed_scenario_changes.csv`, and every row that states: an economy-wide or sector emission target; a renewable share or a generation, capacity or retirement target; a vehicle share or number; a fuel blend; a grid loss target; an efficiency target. Include the BAU and mitigation series of the current NDC and of the long-term strategy from `projections_`. Give the count per country.

For each country, confirm which document is the NDC in force and which is the long-term strategy: title page, date, and the entry on the UNFCCC NDC registry or portal. The scout found that one registry record named in its brief was Honduras's second update and not NDC 3.0; make sure no table mixes versions.

### Step B. Three checks per value

- Check 1 is the scout's reading. Copy its value, unit, year and page.
- Check 2 is a second, blind reading. Prepare `blind_<code>.csv` with the source id, page and description of each value and without the value, unit or year. A background task that has not seen the scout tables renders each page as an image, reads the value, unit, year and reference from it, and writes its answer. Compare. Where the two readings differ, read the page a third time yourself, settle it, and record all three.
- Check 3 is a second place. Find the same value somewhere else: another page or annex table of the same document (for example the ICTU annex), another official document (transparency report, national communication, ministry publication, UNFCCC registry page), or an identity that the printed numbers must satisfy (a percentage against a printed BAU and a printed target level). Record where. If there is none, write `no second place found`.

Write `verification_<code>.csv`: one row per value with the three readings, their pages, and a status: `3 of 3`, `2 of 3` (say which check is missing) or `conflict` (say what differs and which reading the document supports). Never drop a row.

### Step C. One unit system

Write `units.csv`: every unit that appears in the documents and in the models, its standard unit, the factor, and a source for the factor. Standard units: emissions kt CO2 eq (record the global warming potential set the document uses and never convert between sets); energy PJ; capacity MW; shares as a fraction between 0 and 1; money in USD of the stated year.

A share is only comparable with another share of the same thing. For every share, record its numerator and denominator exactly as the document defines them: share of gross or net generation, of installed capacity, of the vehicle fleet, of vehicle sales, of energy use. Record how the document defines "renewable" (large hydro, biomass, bagasse, waste, imports, self-generation) and whether the target is conditional on support.

Then, for each verified value, give the model quantity of the same kind in the same unit for 2030, 2035 and 2050 in NDCNEW and LTSNEW, taken from the solved results. Recompute the model's renewable share under each country's own definition. Where the model has no quantity of the same kind (for example a fleet share against a share of transport output), write `different quantity` and say which data would be needed to convert. Do not convert by assumption.

### Step D. Supporting analyses and pending documents

D1. Try again to fetch the 12 documents of the scout's `sources_pending.csv`.

D2. Find at most eight supporting analyses per country: the technical, modelling or cost-benefit reports behind the NDC and the long-term strategy, and independent analyses of them. Look at what the 2050 Pathways Platform, the NDC Partnership, UNDP Climate Promise, the IDB, the World Bank, IRENA and Climate Analytics have published for the country, and at the CLG documentation site and country model where one exists. Download each, add it to `sources.csv` of this job (id, country, kind, class `official`, `external` or `lead`, URL, title, publisher, author, date, accessed, SHA-256, file, pages, language), and save web pages as HTML files.

D3. Write `analyses_<code>.csv`: for each analysis its class, the model or method, each scenario it defines (name and one-line definition), and its printed results per scenario and year (emissions total and by sector, renewable share, vehicle shares, costs and benefits), each with its page. Say in one paragraph per country how those scenarios compare with BAU, NDCNEW and LTSNEW.

D4. Write `deep_dive_<code>.md`, half a page: what a deeper study of this country would still need.

### Step E. The table of values to load

Write `scenario_values.csv`, one row per value that a model could take: country; scenario (`NDC` or `LTS`); lever; kind of quantity; year; value and unit in the standard system; value and unit as printed; source id and page; check status from step B; conditional, unconditional or not stated; the model quantity it corresponds to and whether it is the same kind; and a note.

Rules:

- Use only rows with status `3 of 3` or `2 of 3`. List `conflict` rows in `scenario_values_held_back.csv` with the reason.
- Where a document gives a conditional and an unconditional value, write both rows.
- `NDC` rows come from the NDC in force and the plans it cites. `LTS` rows come from the long-term strategy submitted to the UNFCCC. Where none is submitted and the NDC names a national long-term plan, use that plan and mark the row `plan named by the NDC`. Where neither exists, write one row per country saying `no published long-term value`.
- Write no value for a year the documents do not state. A later job decides how a value is held or joined between years.
- Where a target is a capacity or an amount of energy and not a share (the Dominican Republic's new renewable and gas capacity, for example), keep it in its own kind. Do not turn it into a share.

### Step F. Values and names held in code

Scan every script and model file of the repository outside `_LAC_HUB/`: the stage scripts at the root, the per-country pipeline scripts, shell and batch files, and the OSeMOSYS model files. Write `script_constants.csv`, one row per value of the system that is written in code: file, line, name, value, what it controls, whether the Stage 0 to 3 results depend on it, and the external table and column it should move to. A value of the system is a number such as a share, a bound, a rate, a year or a tolerance that changes results, or a name of a country, scenario, technology, fuel or emission written as a literal. Constants of the mathematics (0, 1, unit conversions with a source) go in a separate file `script_constants_accepted.csv` with the reason.

Write `scenario_names.csv`: every scenario name found in code, folder names, workbook sheets and workbook cells, with the count and the places.

Write `structure_map.md`, at most two pages: the current folders and scripts of the repository against the folders of https://github.com/Climate-Lead-Group/OSTRAM (clone it read-only into `/c/clw_scout_ostram`), with what would move where. Describe only; change nothing.

### Step G. Gates

1. `git diff --name-only origin/main` lists only files under this job folder.
2. Every row of `verification_`, `analyses_` and `scenario_values.csv` has a source id that exists in a `sources.csv` and a page, table or file. No row of `scenario_values.csv` cites a source of class `lead`.
3. Every value of `values_to_verify.csv` has a row in `verification_<code>.csv`.
4. Every row of `scenario_values.csv` has a standard unit that is listed in `units.csv`.
5. Every source file exists with a matching SHA-256.
6. `git -C /c/clw_scout_model status --short` is empty.

### Step H. Pull request

Commit the job folder (without `downloads/`), push `job/ndc-verify`, and open one draft pull request titled "LAC_NDC_VERIFY: published values checked three times, one unit system, values held in code", body taken from CHANGES.

## 6. Outputs

All three in the job folder, plain English, no em dashes.

`REPORT_LAC_NDC_VERIFY_<stamp>.md`: failed, blocked or pending items first; the count of values by check status per country, and every conflict with its three readings; one table per country of the headline values in standard units, document against model; the supporting analyses found and what they add; the count of values and names held in code, by script; gate results; pull request number and commit hashes.

`GAPS_LAC_NDC_VERIFY_<stamp>.md`: every judgement call and its reason; documents not fetched; values with only two checks; shares that are not the same kind as the model's; known-limitation candidates; what was left unchecked; incidents.

`CHANGES_LAC_NDC_VERIFY_<stamp>.md`: the files of the job folder, two or three lines each.
