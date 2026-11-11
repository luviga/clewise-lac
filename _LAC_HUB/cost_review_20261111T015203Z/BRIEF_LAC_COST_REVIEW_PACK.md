# BRIEF LAC_COST_REVIEW_PACK: one checked review pack for the six country cost jobs

Repository: https://github.com/luviga/clewise-lac, `main` at `2ddd560`. Six draft pull requests are open, one per country, each adding only its own job folder:

| PR | Branch | Head | Job folder on the branch |
|---|---|---|---|
| #2 | `job/cost-src-jam` | `789b36a` | `_LAC_HUB/cost_src_jam_<stamp>/` |
| #3 | `job/cost-src-hon` | `79a3665` | `_LAC_HUB/cost_src_hon_<stamp>/` |
| #4 | `job/cost-src-ecu` | `ddd8d31` | `_LAC_HUB/cost_src_ecu_<stamp>/` |
| #5 | `job/cost-src-dr` | `a0c2845` | `_LAC_HUB/cost_src_dr_<stamp>/` |
| #6 | `job/cost-src-gua` | `0703ae2` | `_LAC_HUB/cost_src_gua_<stamp>/` |
| #7 | `job/cost-src-cr` | `7e8dd76` | `_LAC_HUB/cost_src_cr_<stamp>/` |

Each job's downloaded source files are only on this machine, in `C:\clw_cost_<cc>\_LAC_HUB\cost_src_<cc>_<stamp>\downloads\` (`<cc>` = `cr`, `dr`, `ecu`, `gua`, `hon`, `jam`). Each job followed its brief, `BRIEF_LAC_COST_SRC_<CC>.md`, copied into its job folder.
Main copy on this machine: `C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5` (Git Bash `/c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5`). Claude Code opens there and this brief sits in its `_LAC_HUB/` folder.

You work alone and to the end. Never ask Luis anything and never wait for a reply. Where this brief leaves a choice, take the option that changes least and record it in GAPS. If something blocks a step, record it, finish every step you still can, and write the three output files anyway. Never mark a pull request ready, never merge, never push to or change any of the six branches, and never edit any file in the six job folders or the six `C:\clw_cost_<cc>` clones. This job checks and collects. It changes no model file and no proposal.

## 1. Goal

Turn six pull requests into one checked pack the hub can review in one sitting: every gate rerun independently, the six sets of proposals merged into one file, the values checked against their downloaded sources where a file can be searched, the six countries compared on the shared inputs, and every judgement call and open question the six jobs raised listed in one place. The hub then confirms the flagged items by values and takes Luis through the decisions.

## 2. The standard

Report only what you checked, with counts. A check you could not run is recorded as not run, with the reason; it is never reported as passed. Quote values from the files with their file and row. Do not correct, rewrite or re-source any value: where something looks wrong, write a flag with the evidence. Scope is frozen: anything outside section 5 goes to GAPS under "Known-limitation candidates".

Commits and the pull request carry no Co-Authored-By line and no "Generated with" line.

## 3. Setup

- Environment: Windows, Git Bash, the `py` launcher. Run scripts with `py -I`. pandas, openpyxl, pdfplumber, pypdf and PyMuPDF are installed. Install nothing else.
- Take one UTC stamp at the start, format `YYYYMMDDTHHMMSSZ`, for the job folder and the three output file names.
- New clone from the local main copy, then fetch the six branches:

```bash
git clone /c/Users/luisfernando/Desktop/OSeMOSYS/MODELS_LAC_5 /c/clw_cost_review
cd /c/clw_cost_review
git remote set-url origin https://github.com/luviga/clewise-lac.git
git fetch origin job/cost-src-cr job/cost-src-dr job/cost-src-ecu job/cost-src-gua job/cost-src-hon job/cost-src-jam
git checkout -b job/cost-review 2ddd560
```

  Read branch files with `git show origin/job/cost-src-<cc>:<path>` or `git archive` into a scratch folder inside your job folder's `scratch/` (not tracked: add nothing from it). If a branch head differs from the table in the preamble, use the fetched head and record both hashes in REPORT.
- Job folder: `C:\clw_cost_review\_LAC_HUB\cost_review_<stamp>\`. Write only there.
- Read-only: everything else, including `C:\clw_cost_<cc>`, `C:\clw_local_prices`, `MODELS_LAC_5` and OneDrive. Do not open anything under `C:\Users\luisfernando\Dropbox\`.
- Expected run time: 2 to 4 hours. Sleep must be off on the machine.

## 4. Inputs per country

From each branch's job folder: the brief copy, `REPORT_*.md`, `GAPS_*.md`, `CHANGES_*.md`, `proposals.csv`, `proposals_summary.csv`, `fuel_prices.csv`, `price_points_2024.csv`, `plant_costs.csv`, `sources.csv`, `constants.csv`, `search_log.csv`, `paper_trace.csv`, `cost_rows_current.csv`, `baseline_before.csv`, `baseline_after.csv`, and any extra file the country brief asked for (`mapping_ECU.csv`, `structure_proposals.csv` for Costa Rica). From each local clone: the `downloads/` folder. From `main` at `2ddd560`: the six A-O workbooks (`A1_Outputs/A-O_Parametrization.xlsx` in `CostaRica/CR_ENERGY/t1_confection`, `DominicanRepublic/RD_ENERGY`, `Ecuador/ECU_Energy`, `Guatemala/GUA_ENERGY`, `Honduras/HON_ENERGY`, `Jamaica/JAM_ENERGY`).

## 5. Work

### Step 1. Inventory

For each branch: head hash, number of commits since `2ddd560` with their messages, the job folder name, which of the section 4 files exist, and the PR number. Save `inventory.csv`. A missing file is a flag.

### Step 2. Gates, rerun independently

For each branch, rerun and record pass, fail or not run, with counts, in `gates.csv`:

1. `git diff --name-only 2ddd560 origin/job/cost-src-<cc>` lists only files in that branch's job folder.
2. Tracked files there are only `.md`, `.csv`, `.py`, `.txt`; nothing under `downloads/` is tracked.
3. `git log 2ddd560..origin/job/cost-src-<cc> --format=%B` has no "Co-Authored-By" and no "Generated with".
4. The A-O workbook and BAU CSVs listed in the branch's `baseline_before.csv` have the same SHA-256 at `2ddd560` and at the branch head.
5. Sourcing: every `proposals.csv` row whose basis is not `ASSUMPTION` names source ids that exist in `sources.csv`; every source has an http(s) URL, a locator, a retrieval date and a file name; the file exists in the local `downloads/`; no source field holds a local path or names an internal file (workbook, CSV we built, markdown, handover, paper draft).
6. Every `ASSUMPTION` row has at least one `search_log.csv` entry for its technology or fuel, and its sentence contains none of these words or phrases (case-insensitive): job, hub, agent, brief, PR, pull request, commit, workbook, sheet, cell, CSV, not found, could not, unable, no source, unrecovered, retained, kept as, previously, earlier, pending (except the exact marker "(pending correction)").
7. Coverage: every technology in the plant table and every row in the supply table of section 5 of that branch's brief, and the import technology where the brief's Step 6 applied, has proposals for every year column of that country's A-O workbook (read the year columns from the workbook at `2ddd560`), and every fuel row has all three scenarios STEPS, CPS and NZE.
8. No em dash in any tracked output file of the branch.

### Step 3. Values against their sources

For each country, check proposed values against the downloaded files, by searching the file's text (PDF text, CSV, XLSX cell values, HTML text) for the number as published before conversion, using the source row's locator and the derivation's input values:

- every fuel row's 2024 chosen value (`price_points_2024.csv`);
- every plant or other technology row whose `change_class` is not `keep`;
- 20 `keep` rows per country chosen at random with seed 20261110 (fewer if the country has fewer).

Record each in `value_checks.csv`: country, technology, parameter, year, proposed value, number searched for, file, found yes or no, page or location found, note. Then recompute every derivation you can from its stated inputs and constants, and record any difference above 0.5 percent. Images and scanned pages that cannot be searched are `not run`, with the reason.

### Step 4. Shared inputs across the six

Compare across countries and flag any disagreement, in `cross_country.csv`:

- the WEO 2025 values each country used (table number, units, currency year, each scenario and year), from each `constants.csv`;
- the US CPI-U values used for deflation;
- the gas conversion: every natural gas row divided by 0.9 once, and its ASSUMPTION sentence identical across countries;
- the benchmark series and their 2024 annual averages (Brent, Henry Hub, coal);
- the exchange rates used, where two countries use the same currency source.

### Step 5. Range screen

Flag, in `review_flags.csv`, every proposed value outside these screens, with the current value and source beside it: plant CapitalCost below 300 or above 8,000 USD/kW; FixedCost below 0 or above 200 USD/kW-yr; plant VariableCost above 30 USD/MWh (8.33 USD/GJ); a fuel 2024 value below 0.5 or above 2 times the Brent-implied value for oil products (Brent 2024 annual average in USD/GJ times the row's r); any value of exactly 0 or 1 on a row that the brief listed as in scope; any proposed change above 25 percent from the current value; any step at the join above 20 percent.

### Step 6. Country points the hub asked about

Answer each with evidence in REPORT:

- Costa Rica: does the Costa Rica A-O at `2ddd560` contain an electricity import technology (search the Primary and Secondary sheets and the BAU CSVs for any technology outputting electricity from outside the country, for example names containing `IMP` and `ELE`)? What did the job's commit "price electricity imports (IMPELE)" add, and is the technology used in the model (activity limits, residual capacity, max capacity)? What does `structure_proposals.csv` propose for coal and petroleum coke, and what does the balance page it cites show?
- Ecuador: every row that was 1 in `cost_rows_current.csv` has a proposal other than 1; CCG against PLANMICC, the list of pairs differing by more than 25 percent; plants taken from CCG have VariableCost 0.
- Guatemala: the unit evidence behind the plant VariableCost correction, quoted.
- Honduras: the `IMP_ELE` years with VariableCost or FixedCost 99999 are unchanged in `proposals.csv` or absent from it.
- Jamaica: the Petrojam prices used are pre-tax, and how the job showed it; values were read from the A-O workbook (check `cost_rows_current.csv` against the A-O at `2ddd560`).
- Dominican Republic: `DIST_GSL` and `DIST_LPG` use the market values (19.614 and 11.042 USD/GJ in 2024) with the MICM parity beside them.

### Step 7. Merged files

- `proposals_all.csv`: the six `proposals.csv` stacked, with a country column, in the same columns.
- `summary_all.csv`: the six `proposals_summary.csv` stacked.
- `paper_trace_all.csv`: the six `paper_trace.csv` stacked, de-duplicated where two countries record the same passage, sorted by document and section.
- `decisions_raised.csv`: every judgement call, open question, choice left to Luis or the hub, and ASSUMPTION the six GAPS and REPORT files contain: country, file, the text in one or two sentences, the rows it affects, the size of the effect in the model's units where stated.
- `assumptions_all.csv`: every ASSUMPTION row across the six with its sentence.

### Step 8. Pull request

- Copy this brief into the job folder as `BRIEF_LAC_COST_REVIEW_PACK.md`.
- One commit with the job folder's tracked files (`.md`, `.csv`, `.py`, `.txt` only; nothing from `scratch/`), message "LAC_COST_REVIEW_PACK: checked review pack for the six country cost jobs", no trailer lines. Push `job/cost-review` and open one draft pull request with the same title, body from CHANGES.
- If the push or the pull request fails, keep the local commit, record the exact error in REPORT, and finish the outputs.

## 6. Outputs

All in `_LAC_HUB/cost_review_<stamp>/`, plain English, no em dashes.

`REPORT_LAC_COST_REVIEW_PACK_<stamp>.md`, the single document the hub reads first:

1. Pull request number, branch, commit hash.
2. A table, one row per country: PR, head, commits, gates 1 to 8 (pass, fail, not run), proposals rows, ASSUMPTION rows, value checks found and not found, flags by severity.
3. Cross-country: one table of the WEO 2025 values each country used, with disagreements marked; CPI, gas conversion and benchmarks.
4. Per country, in the order Ecuador, Costa Rica, Jamaica, Dominican Republic, Guatemala, Honduras: the fuel table (row, chosen point, 2024 current and proposed, STEPS 2030 and 2050, CPS and NZE 2050, step at the join); the plant changes above 25 percent with their sources; the answers to Step 6; the flags.
5. The decisions raised, grouped by topic, each with the countries and rows it touches.

`GAPS_LAC_COST_REVIEW_PACK_<stamp>.md`: checks not run and why; judgement calls; "Known-limitation candidates"; incidents.

`CHANGES_LAC_COST_REVIEW_PACK_<stamp>.md`: every file created, one line each; confirmation that no model file, no branch and no job folder of the six was changed.

Supporting files: `inventory.csv`, `gates.csv`, `value_checks.csv`, `cross_country.csv`, `review_flags.csv`, `proposals_all.csv`, `summary_all.csv`, `paper_trace_all.csv`, `decisions_raised.csv`, `assumptions_all.csv`, your helper scripts.
