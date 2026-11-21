# CHANGES LAC_NDC_SCOUT 20261121T204620Z

Job folder `_LAC_HUB/ndc_scout_20261121T204620Z/` only; no model file changed. Model state read at `481a7c0`. Downloads (`downloads/`, about 200 MB, with page text caches and page images) stay local and are ignored by `.gitignore`. `<code>` is CR, DR, ECU, GUA, HON or JAM.

## Outputs

- `REPORT_LAC_NDC_SCOUT_20261121T204620Z.md`: blocked and pending items first, then one section per country (documents, headline targets with pages, five largest disagreements, proposals by class), the cross-country table, gates, pull request and commits.
- `GAPS_LAC_NDC_SCOUT_20261121T204620Z.md`: hub judgement calls, blocks, hub-confirmed known-limitation candidates and incidents, followed by the notes of the six country tasks.
- `CHANGES_LAC_NDC_SCOUT_20261121T204620Z.md`: this file.

## Step A

- `sources.csv`: the 46 documents downloaded and opened (id, country, kind, URL, title, publisher, date, accessed, SHA-256, file, pages, language). Merged from `parts/sources_<code>.csv`.
- `sources_pending.csv`: 12 documents not fetched, with the URLs tried and the errors.
- `published_<code>.md`: half a page per country on what is published, what is new since 1 January 2025, and the current NDC and long-term strategy.

## Step B

- `targets_<code>.csv`: 549 quantified targets and measures in all, one row each, with source id, PDF page, table, sector, indicator, value, unit, reference, target year, conditionality and gases.
- `projections_<code>.csv`: 505 rows of emission projections printed in the documents (BAU and mitigation, total or by sector), with source id and page.
- `spot_checks.csv`: ten values per country reopened and confirmed (round 1, 10 of 10 in all six). Merged from `parts/spot_checks_<code>.csv`.

## Step C

- `model_levers_<code>.csv`: part `input_difference`, every compiled input differing between BAU and NDCNEW or LTSNEW from 2025, grouped, with known unintended differences marked; part `solved`, generation, capacity, renewable share, final energy per fuel, electric share of transport groups, electricity imports and exports, and emissions by label, per scenario for 2025, 2030, 2035, 2040 and 2050.
- `alignment_<code>.csv`: 352 rows pairing a document target with the model quantity, NDCNEW and LTSNEW values, ratios and a status.

## Step D

- `changes_since_paper_<code>.md`: one page per country: target year and type against the model design, the long-term strategy, and the five largest disagreements.
- `proposed_scenario_changes.csv`: 122 rows for the hub to decide (60 class A, 22 class B, 8 class C, 32 levers where the documents are silent), with the workbook, sheet and row at `481a7c0`. Merged from `parts/proposals_<code>.csv`.
- `cross_country_summary.csv`: per country the current NDC and long-term strategy, alignment status counts and proposal counts by class.

## Working files

- `BRIEF_LAC_NDC_SCOUT.md`: the brief, copied unchanged.
- `PROGRESS.md`: the step log kept during the job.
- `country_task_conventions.md`: file names, columns and rules given to the six country tasks.
- `.gitignore`: keeps `downloads/` out of git.
- `parts/`: per-country sources, pending lists, spot checks, proposal drafts and notes; `headlines.csv` (hand-written NDC and LTS fields for the summary); `hub_value_check_<code>.csv` (the hub's search of every value on its cited page); `gate_results.csv` (gates E2 to E4); `gaps_hub.md` (Part 1 of GAPS).
- `scripts/c1_model_levers.py`: step C1 for all six countries.
- `scripts/hub_check_values.py`: checks every target and projection value against the text of the cited PDF page and every file against its SHA-256.
- `scripts/hub_fix_ecu_emissions.py`: recomputes five Ecuador emission alignment rows from the single label CO2e_sources.
- `scripts/hub_merge_and_gates.py`: merges the parts into the step D tables and `sources.csv`, and runs gates E2 to E4.
- `scripts/hub_build_gaps.py`: assembles GAPS from Part 1 and the country notes.
- `scripts/<code>/`: the scripts each country task used (text cache, page rendering, workbook reading, table writing, spot checks).
