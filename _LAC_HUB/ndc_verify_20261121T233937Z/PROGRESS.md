# LAC_NDC_VERIFY progress

Stamp 20261121T233937Z. Branch `job/ndc-verify` from `origin/main` at `a76ad81`.

| Step | State | Note |
|---|---|---|
| Setup | done | 46 scout downloads present, SHA-256 match (`parts/scout_download_check.csv`). Model worktree at 481a7c0, clean. Text of every page cached with pdftotext (pypdf for GUA-02 and GUA-04). |
| A | done | `values_to_verify.csv`: 733 values (CR 102, DR 66, ECU 114, GUA 126, HON 192, JAM 133). `document_status.csv`: NDC in force and long-term document per country; UNFCCC registry blocked (bot check, CAPTCHA). |
| B | done | Blind readings by two background tasks (`blind_answers_<code>.csv`); 32 values read a third time by the hub (`parts/third_reading.csv`); second places by text search and identities (`parts/check3_<code>.csv`). `verification_<code>.csv`: 559 at 3 of 3, 165 at 2 of 3, 9 conflicts. |
| C | done | `units.csv` (93 rows), `share_definitions.csv` (221), `model_comparison.csv` (733). |
| D | in progress | Two research tasks running (GUA, JAM, CR; HON, DR, ECU). |
| E | done (rerun after D not needed) | `scenario_values.csv` 446 rows; `scenario_values_held_back.csv` 14 rows. |
| F | done | `script_constants.csv` 11,170 rows (1,977 in files Stage 0 to 3 depend on); `script_constants_accepted.csv` 52,301; `scenario_names.csv` 12 names; `structure_map.md`. |
| G | pending | |
| H | pending | |
