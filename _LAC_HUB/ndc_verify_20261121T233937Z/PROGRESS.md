# LAC_NDC_VERIFY progress

Stamp 20261121T233937Z. Branch `job/ndc-verify` from `origin/main` at `a76ad81`.

| Step | State | Note |
|---|---|---|
| Setup | done | 46 scout downloads present, SHA-256 match. Model worktree at 481a7c0, clean. Page text cached with pdftotext (pypdf for GUA-02 and GUA-04). |
| A | done | `values_to_verify.csv` 733 values; `document_status.csv`; UNFCCC registry blocked (bot check, CAPTCHA). |
| B | done | `verification_<code>.csv`: 556 at 3 of 3, 165 at 2 of 3, 12 conflicts. |
| C | done | `units.csv`, `share_definitions.csv`, `model_comparison.csv`. |
| D | done | 38 new sources (7 official, 15 external, 16 lead); 6 of 12 pending fetched; 258 analysis rows, all found on their pages; `analyses_comparison.md`; `deep_dive_<code>.md`. |
| E | done | `scenario_values.csv` 443 rows; `scenario_values_held_back.csv` 17 rows. |
| F | done | `script_constants.csv` 11,170 rows; `script_constants_accepted.csv` 52,301; `scenario_names.csv` 12 names; `structure_map.md`. |
| G | done | All six gates pass (`parts/gate_results.csv`). |
| H | done | Draft pull request luviga/clewise-lac#13; job commit 2265146, then a report-only commit. |
