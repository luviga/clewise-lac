# CHANGES: LAC_NDC_VERIFY 20261121T233937Z

Everything is in `_LAC_HUB/ndc_verify_20261121T233937Z/`. No workbook, CSV, compiled file, script or stage output of the models was changed. Downloaded documents and page text caches are in the ignored `downloads/` folder.

## Outputs

- `REPORT_LAC_NDC_VERIFY_20261121T233937Z.md`: what failed or is pending, check status counts per country, every conflict with its three readings, headline values against the model, supporting analyses, values held in code, gates, pull request.
- `GAPS_LAC_NDC_VERIFY_20261121T233937Z.md`: judgement calls, documents not fetched, values with two checks, shares of a different kind, known-limitation candidates, what was left unchecked, incidents.
- `CHANGES_LAC_NDC_VERIFY_20261121T233937Z.md`: this file.
- `BRIEF_LAC_NDC_VERIFY.md`: copy of the brief. `PROGRESS.md`: step log.

## Step A

- `values_to_verify.csv`: 733 published values taken from the scout tables (CR 102, DR 66, ECU 114, GUA 126, HON 192, JAM 133), with document role and the reason each was included.
- `document_status.csv`: the NDC in force and the long-term document of each country, with title page, date, UNFCCC file folder and the registry check (blocked by a bot check and CAPTCHA).

## Step B

- `blind_<code>.csv`: the blind reading lists (source, page, masked description; no value, unit or year).
- `blind_answers_<code>.csv` and `blind_log_<code>.md`: the second, blind readings from page images by two background tasks, with their notes on printing slips.
- `blind_reading_instructions.md`: the rules the blind readers followed.
- `verification_<code>.csv`: one row per value with check 1 (scout), check 2 (blind), check 3 (second place or identity), the hub's third reading where needed, and the status (556 at 3 of 3, 165 at 2 of 3, 12 conflicts).

## Step C

- `units.csv`: every document and model unit, its standard unit, factor and source, and the GWP set of each main document.
- `share_definitions.csv`: numerator, denominator, renewable definition and conditionality of each share (221 rows).
- `model_comparison.csv`: for each value, the model quantity of the same kind in NDCNEW and LTSNEW for 2030, 2035 and 2050 from the solved results, or `different quantity` with the data needed to convert.

## Step D

- `sources.csv`: 84 documents (46 from the scout, 38 found in this job), with class `official`, `external` or `lead`, URL, SHA-256 and file.
- `sources_pending.csv`: the 12 scout pending documents retried (6 fetched, 6 still pending).
- `analyses_<code>.csv`: printed results of the supporting analyses per scenario, year and page (258 rows; every value checked on its page).
- `analyses_comparison.md`: one paragraph per country on how the analyses' scenarios compare with BAU, NDCNEW and LTSNEW.
- `deep_dive_<code>.md`: half a page per country on what a deeper study would still need.
- `research_instructions.md`: the rules the research tasks followed.

## Step E

- `scenario_values.csv`: 443 rows a later job could load (442 values from the NDCs in force, the plans they cite, the submitted long-term strategies and two plans named by the NDCs, plus one row for Honduras saying there is no published long-term value), in standard units with the printed value, source, page, check status, conditionality and model quantity.
- `scenario_values_held_back.csv`: 17 rows not loadable (12 conflicts, 3 verbal targets with no number, 2 with no stated year), each with its reason.

## Step F

- `script_constants.csv`: 11,170 values and element names written in code outside `_LAC_HUB/` (1,977 in files that Stage 0 to 3 results depend on), with file, line, context, what it controls and the table and column it should move to.
- `script_constants_accepted.csv`: 52,301 constants of the mathematics or presentation (0, 1, indices, unit conversions with their source, plotting and housekeeping scripts), each with the reason.
- `scenario_names.csv`: the 12 scenario names found in code, folder names, workbook sheets and workbook cells, with counts and places.
- `structure_map.md`: the repository's folders and scripts against the OSTRAM layout, and what would move where.

## Working files

- `scripts/`: the hub scripts of each step (`a*` step A, `b*` step B, `c1` step C, `d*` step D checks, `e1` step E, `f*` step F, `g1` gates, `h*` report tables) and the blind and research tasks' scripts.
- `parts/`: intermediate tables (blind keys, comparisons, second-place hits, third readings, self-contradictions, analyses checks, research notes and source lists per country, gate results, headline tables).
- `.gitignore`: keeps `downloads/` out of git.
