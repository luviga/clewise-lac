# CHANGES LAC_COST_REGIONAL 20261111T050439Z

Regional plant cost values where published: 28 of 68 international-only groups get a regional or late national value (880 rows in `regional_proposals.csv`); 40 keep their international value.

## Files created (all in `_LAC_HUB/cost_regional_20261111T050439Z/`)

- `BRIEF_LAC_COST_REGIONAL.md`: copy of the brief
- `REPORT_LAC_COST_REGIONAL_20261111T050439Z.md`: run facts, scope counts, documents, the 68 groups, flags, gates
- `GAPS_LAC_COST_REGIONAL_20261111T050439Z.md`: judgement calls, exclusions, known-limitation candidates, unchecked items, manual downloads, incidents
- `CHANGES_LAC_COST_REGIONAL_20261111T050439Z.md`: this file
- `scope.csv`: 68 groups with technology name, configuration, 2024 value, sources and outcome
- `leads.csv`: lead families and documents with status
- `search_log.csv`: searches and documents opened
- `manual_downloads.csv`: pages that did not open or documents not located
- `regional_values.csv`: every generation cost printed in the opened regional documents
- `match_log.csv`: match or refusal per group
- `regional_proposals.csv`: one row per year column of each accepted group, columns of proposals_all.csv plus tier, international_value, change_pct
- `regional_vs_international.csv`: one row per accepted group, 2024 comparison and flags
- `sources.csv`: external sources with URL, dates, file and locator
- `value_checks.csv`: gate 4 checks of accepted values against the file text
- `baseline_before.csv`: SHA-256 of the six A-O workbooks and BAU A2_Output_Params CSVs at start
- `baseline_after.csv`: the same at the end
- `baseline.py`: hashing script for gate 1
- `step1_scope.py`: scope rule
- `textindex.py`: PDF text extraction helper
- `pages.py`: page search helper
- `catalog_extract.py`: Colombian catalogue data sheet extraction
- `regional_data.py`: transcribed source register and printed values
- `step3_extract.py`: builds regional_values.csv
- `step4_match.py`: matching decisions, scope.csv and match_log.csv
- `step5_proposals.py`: regional proposals and comparison
- `step2_logs.py`: sources, leads, search log and manual downloads
- `gate4_value_checks.py`: gate 4
- `gates.py`: gates 1, 3, 5 and 7 (dashes)
- `report_text.py`: writes REPORT, GAPS and CHANGES

Untracked: `downloads/` (source files) and `scratch/` (working files).

No model file and no existing proposal was changed: the A-O workbooks and BAU parameter CSVs hash the same before and after (gate 1), and `proposals_all.csv` and the country job files were only read. LAC_COST_WRITE reads `regional_proposals.csv` on top of `proposals_all.csv`.
