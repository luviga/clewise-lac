# BRIEF LAC_COST_REGIONAL: regional plant cost values for the plant rows that rest only on international sources

Repository: https://github.com/luviga/clewise-lac. Luis merges pull requests #2 to #8 before launch, so `origin/main` should contain these job folders:

| Country | Job folder on `main` | Downloads on this machine |
|---|---|---|
| Costa Rica | `_LAC_HUB/cost_src_cr_20261110T025401Z/` | `C:\clw_cost_cr\_LAC_HUB\cost_src_cr_20261110T025401Z\downloads\` |
| Dominican Republic | `_LAC_HUB/cost_src_dr_20261110T025405Z/` | `C:\clw_cost_dr\_LAC_HUB\cost_src_dr_20261110T025405Z\downloads\` |
| Ecuador | `_LAC_HUB/cost_src_ecu_20261110T025435Z/` | `C:\clw_cost_ecu\_LAC_HUB\cost_src_ecu_20261110T025435Z\downloads\` |
| Guatemala | `_LAC_HUB/cost_src_gua_20261110T025448Z/` | `C:\clw_cost_gua\_LAC_HUB\cost_src_gua_20261110T025448Z\downloads\` |
| Honduras | `_LAC_HUB/cost_src_hon_20261110T073537Z/` | `C:\clw_cost_hon\_LAC_HUB\cost_src_hon_20261110T073537Z\downloads\` |
| Jamaica | `_LAC_HUB/cost_src_jam_20261110T025557Z/` | `C:\clw_cost_jam\_LAC_HUB\cost_src_jam_20261110T025557Z\downloads\` |
| Review pack | `_LAC_HUB/cost_review_20261111T015203Z/` | none |

Main copy on this machine: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens there and this brief sits in its `_LAC_HUB/` folder.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark a pull request ready and never merge. This job searches, extracts and proposes. It changes no model file and no existing proposal.

## 1. Goal

Luis decided on 11 November 2026 that plant costs use the most local source that can be cited: a national source first, then a regional one, then an international one. The six country jobs found national sources for most plant cost cells. 2,217 cells (68 country, technology and parameter groups, 40 country and technology pairs) rest only on IRENA, NREL ATB, US EIA or IEA. This job looks for a regional value for those groups and proposes it where one meets section 2. Where none does, the international value stays and nothing is proposed. LAC_COST_WRITE later reads your `regional_proposals.csv` on top of the review pack's `proposals_all.csv`.

## 2. The standard

Cite only external, retrievable sources: a URL, DOI or public repository permalink with commit hash. Never cite internal files (workbooks, sheets, cells, markdown, handovers, CSVs we built, local paths). Every source is downloaded, retrievable and readable, and kept in your `downloads/` folder, before any value from it enters `regional_proposals.csv`. Every source row records the http(s) URL that returns the file, the title, the publisher, the publication date, the retrieval date, the downloaded file name and the page or table.

A regional value is accepted only if all of these hold:

1. It is the same technology class and the same cost component as the model row: overnight capital cost per kW, fixed O&M per kW-year, or non-fuel variable O&M per MWh. Configuration matches: utility-scale against distributed, with storage against without, dam against run-of-river.
2. It was published in 2019 or later.
3. Its currency year is stated in the document. A value without a stated currency year is not accepted.
4. You found the number in the downloaded file at the locator you record.

Do not write new ASSUMPTION rows. A group whose only regional evidence fails a condition above keeps its international value, and you record why in `scope.csv`.

Tiers, best first:

- N (national, found late): a source from the country's own government, regulator, system operator or utility that its country job did not use.
- R1 (regional body): a value published for Central America, the Caribbean, or Latin America and the Caribbean by a regional or multilateral body, for example CEAC or SICA, CRIE or EOR, OLADE, CEPAL (ECLAC), IDB, CAF, CDB, CARICOM or CCREEE, World Bank regional reports, or IRENA regional reports and IRENA country or regional tables for Latin America and the Caribbean.
- R2 (neighbour): a value published by the government, regulator, system operator or utility of a neighbouring country. Neighbours: for Costa Rica, Guatemala and Honduras, the other SICA members and Mexico; for the Dominican Republic and Jamaica, other Caribbean states and territories, including Puerto Rico; for Ecuador, Colombia and Peru.

Within a tier, take the most recent publication, then the most specific geography (Central America for Costa Rica, Guatemala and Honduras; the Caribbean for the Dominican Republic and Jamaica; the Andean countries or South America for Ecuador).

Scope is frozen. Do only what section 5 lists. Anything new you find goes to GAPS under "Known-limitation candidates", with where it is and one sentence on what it is. Do not fix it.

Commits and the pull request carry no Co-Authored-By line and no "Generated with" line.

## 3. Facts already checked by values

- `_LAC_HUB/cost_review_20261111T015203Z/proposals_all.csv` has 17,921 rows, country names without spaces (`CostaRica`, `DominicanRepublic`, `Ecuador`, `Guatemala`, `Honduras`, `Jamaica`), years 2018 to 2055.
- The scope rule in Step 1 selects 2,217 rows, 68 country, technology and parameter groups and 40 country and technology pairs. Rows by country: Costa Rica 360, Dominican Republic 528, Ecuador 180, Guatemala 528, Honduras 132, Jamaica 489.
- The groups, by country:
  - Costa Rica: `PP_SPV_DG` (CapitalCost, FixedCost); `PWRBMS` (CapitalCost, VariableCost); `PWRDSL` (VariableCost); `PWRFOI` (VariableCost); `PWRGEO` (FixedCost); `PWRHYDDAM` (CapitalCost); `PWRSPVDTR` (CapitalCost); `PWRSPVTRN` (FixedCost); `PWRWNONS` (CapitalCost, FixedCost).
  - Dominican Republic: `PPBGS` (CapitalCost, FixedCost, VariableCost); `PPBIM` (CapitalCost); `PPDHYD`, `PPHDAM`, `PPPVD`, `PPPVT`, `PPPVTHYD`, `PPWNDON` (CapitalCost, FixedCost each).
  - Ecuador: `PPPVD`, `PPWNDD`, `STOELE` (CapitalCost, FixedCost each).
  - Guatemala: `PPBIM` (VariableCost); `PPCOA` (CapitalCost); `PPFOI` (FixedCost, VariableCost); `PPGEO` (CapitalCost); `PPHROR` (CapitalCost); `PPNGS` (CapitalCost); `PPPVD`, `PPPVDS`, `PPPVT2`, `PPPVTS` (CapitalCost, FixedCost each); `PPPVT` (CapitalCost).
  - Honduras: `PPBIM` (CapitalCost, FixedCost, VariableCost); `PPPVD` (FixedCost).
  - Jamaica: `PPBGS`, `PPBIM` (CapitalCost, FixedCost, VariableCost each); `PPGEO`, `PPHDAM`, `PPPVD` (CapitalCost, FixedCost each); `PPHROR`, `PPWNDON` (CapitalCost).
- Units in the model and in `proposals_all.csv`: CapitalCost in MUSD per GW (equal to USD/kW), FixedCost in USD/kW-year, VariableCost in MUSD per PJ (equal to USD/GJ; USD/MWh divided by 3.6). Values in real 2024 USD.
- The six country jobs used the same US CPI-U values for deflation (review pack `cross_country.csv`). Use the CPI-U rows from the country's own `constants.csv`.

## 4. Setup

- Environment: Windows, Git Bash, the `py` launcher. Run scripts with `py -I`. pandas, openpyxl, pdfplumber, pypdf and PyMuPDF are installed. Install nothing else.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`, for the job folder and the three output file names.
- New clone from the local main copy, branch from GitHub's `main`:

```bash
git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_cost_regional
cd /c/clw_cost_regional
git remote set-url origin https://github.com/luviga/clewise-lac.git
git fetch origin main
git checkout -b job/cost-regional origin/main
```

  Record the `origin/main` hash in REPORT. If `origin/main` lacks any job folder in the preamble table, fetch `pull/2/head` to `pull/8/head` (`git fetch origin pull/<n>/head:pr<n>`), read the missing files with `git show pr<n>:<path>`, keep the branch on `origin/main`, and record this in GAPS.
- Job folder: `C:\clw_cost_regional\_LAC_HUB\cost_regional_<stamp>\`, with an untracked `downloads\` and `scratch\` inside. Write only there.
- You may copy files from the six country `downloads\` folders into your `downloads\` when a regional document is already there. Cite its original URL, never the local path.
- Read-only: everything else, including the six `C:\clw_cost_<cc>` clones, `C:\clw_cost_review`, `C:\clw_local_prices`, `MODELS_LAC_5` and OneDrive. Do not open anything under `C:\Users\luisfernando\Dropbox\`.
- Expected run time: 4 to 8 hours. Sleep must be off on the machine.

## 5. Work

### Step 1. Scope

From `proposals_all.csv`, select rows with `fuel_scenario` = `ALL`, a proposed value that is not empty and not 0, and every id in `source_ids` within this list for the row's country:

- CostaRica: CRC-001, CRC-010, CRC-011, CRC-013, CRC-014
- DominicanRepublic: CSD-009, CSD-011, CSD-012
- Ecuador: ATB-001, BEN-004
- Guatemala: INT-001 to INT-009, INT-013
- Honduras: CSH-011, CSH-013
- Jamaica: CSJ-006, PSJ-001, PSJ-002, PSJ-006

Expected: 2,217 rows, 68 groups, 40 pairs. A different count is recorded in REPORT with the difference listed; continue with what the rule selects. Write `scope.csv`, one row per group: country, technology, parameter, technology description from the country's A-O workbook (`Tech.Name`), configuration (utility or distributed, storage, hydro type), 2024 proposed value and its source ids, and later the outcome (tier found, or "international kept" with the reason).

### Step 2. Leads

Build `leads.csv` before searching widely. Start from these document families and confirm each one opens. Each is a lead until you open it and find the values:

- CEAC (Consejo de Electrificación de América Central), the regional indicative generation expansion plan, latest edition.
- IRENA Renewable Power Generation Costs 2022, 2024 and 2025 (already in some country downloads): country and regional tables for Latin America and the Caribbean.
- IRENA regional market analyses for Latin America and for the Caribbean or small island developing states.
- IDB, CAF, OLADE and CEPAL publications with generation technology cost tables for Central America, the Caribbean or Latin America.
- CDB, CARICOM or CCREEE studies with Caribbean generation costs.
- Neighbour national plans with technology cost tables: Panama, El Salvador, Nicaragua and Mexico for the Central American countries; Puerto Rico's integrated resource plan and other Caribbean utility plans for the Dominican Republic and Jamaica; Colombia (UPME) and Peru for Ecuador.

Log every search and every document opened in `search_log.csv`: date and time, query or URL, what it held, outcome. Pages that do not open go to `manual_downloads.csv`: URL, what it should hold, which groups it would serve. Do not stop for them.

Stop rule: work through the lead list, plus at most 10 further documents per region (Central America, Caribbean, Andean) found along the way. Then stop searching. The remaining groups keep their international values.

### Step 3. Extraction

Open each regional document once and extract every generation technology cost it prints, for all technologies, into `regional_values.csv`: source id, document, page or table, technology as printed, cost component, value, unit, currency year, geography covered, publication year, tier (N, R1 or R2). This avoids reopening documents per cell.

### Step 4. Match

For each group in `scope.csv`, choose the best value in `regional_values.csv` by the section 2 tiers and acceptance rules. Record the match, or the reason no value was accepted, in `scope.csv` and `match_log.csv`. A technology description that differs from the model row (for example a battery hybrid against plain PV) is not a match.

### Step 5. Regional proposals

For each accepted group, write one row per year column in `proposals_all.csv` for that group to `regional_proposals.csv`, with the same columns as `proposals_all.csv` plus `tier`, `international_value` (the value being replaced) and `change_pct`. Set `change_class` to `regional`, `basis_class` to `national` (tier N) or `regional` (tiers R1, R2), and `source_ids` to the new source plus the CPI-U id used.

Values by year:

- Convert the published value to real 2024 USD with the country's CPI-U values (published currency year to 2024) and to model units. Write every input and constant in `derivation`.
- If the document prints values for two or more years, use them, interpolate linearly between printed years, and after the last printed year follow the shape of the current proposed path: P(y) = P(last printed year) x I(y) / I(last printed year), where I is the current proposed value of that row.
- If it prints one year, use it for that year and scale the current proposed path through it: P(y) = R x I(y) / I(year of R).
- Years before the first printed year use the same scaling.

### Step 6. Comparison

Write `regional_vs_international.csv`, one row per accepted group: 2024 international value and source, 2024 regional value and source, tier, change in percent. Flag every change above 25 percent and every value outside these screens: CapitalCost below 300 or above 8,000 USD/kW; FixedCost below 0 or above 200 USD/kW-year; VariableCost above 8.33 USD/GJ. Flags do not block a proposal.

### Step 7. Gates

Record each as pass, fail or not run, with counts, in REPORT:

1. Read-only: SHA-256 of the six A-O workbooks (`A1_Outputs/A-O_Parametrization.xlsx` under `CostaRica/CR_ENERGY/t1_confection`, `DominicanRepublic/RD_ENERGY`, `Ecuador/ECU_Energy`, `Guatemala/GUA_ENERGY`, `Honduras/HON_ENERGY`, `Jamaica/JAM_ENERGY`) and of every BAU `A2_Output_Params` CSV in those six folders, taken at the start and the end, are equal (`baseline_before.csv`, `baseline_after.csv`).
2. `git diff --name-only origin/main` lists only files in your job folder; tracked files are only `.md`, `.csv`, `.py`, `.txt`; nothing under `downloads/` or `scratch/` is tracked.
3. Every `regional_proposals.csv` row has source ids present in your `sources.csv`; every source has an http(s) URL, a locator, a retrieval date and a file present in `downloads/`; no source field holds a local path or names an internal file.
4. Every accepted value was found as printed in its downloaded file at the recorded locator (search the file text); list each with file and page in `value_checks.csv`.
5. Coverage: each accepted group has a row for every year column that group has in `proposals_all.csv`.
6. `git log origin/main..HEAD --format=%B` has no "Co-Authored-By" and no "Generated with".
7. No em dash in any tracked file; `git diff --check` is clean.

### Step 8. Pull request

- Copy this brief into the job folder as `BRIEF_LAC_COST_REGIONAL.md`.
- One commit with the job folder's tracked files, message "LAC_COST_REGIONAL: regional plant cost values where published", no trailer lines. Push `job/cost-regional` and open one draft pull request with the same title, body taken from CHANGES.
- If the push or the pull request fails, keep the local commit, record the exact error in REPORT, and finish the outputs.

## 6. Outputs

All in `_LAC_HUB/cost_regional_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_COST_REGIONAL_<stamp>.md`: pull request number, branch, `origin/main` hash and commit hash; scope counts against the expected 2,217, 68 and 40; documents opened by tier and region; a table of the 68 groups with outcome (N, R1, R2 or international kept) and, where accepted, 2024 international and regional values with change in percent; flags; gate results with counts.

`GAPS_LAC_COST_REGIONAL_<stamp>.md`: every judgement call and its reason (matches made or refused, configuration calls, documents excluded); "Known-limitation candidates"; anything left unchecked; manual downloads; incidents.

`CHANGES_LAC_COST_REGIONAL_<stamp>.md`: every file created, one line each, and confirmation that no model file and no existing proposal was changed.

Supporting files: `scope.csv`, `leads.csv`, `search_log.csv`, `manual_downloads.csv`, `regional_values.csv`, `match_log.csv`, `regional_proposals.csv`, `regional_vs_international.csv`, `sources.csv`, `value_checks.csv`, `baseline_before.csv`, `baseline_after.csv`, your helper scripts.

Output files other than the brief copy carry no machine paths, and no hash values outside REPORT and the baseline files.
