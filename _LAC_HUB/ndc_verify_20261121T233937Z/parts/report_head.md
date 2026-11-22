# REPORT: LAC_NDC_VERIFY 20261121T233937Z

Branch `job/ndc-verify`, started from `origin/main` at `a76ad81`. Model state read from `/c/clw_scout_model` at `481a7c0` (unchanged). Nothing in a model was changed; this job proposes and lists.

## 1. Failed, blocked or pending

- **UNFCCC NDC registry and long-term strategies portal: blocked.** Three addresses gave an Incapsula bot check to curl and an Imperva CAPTCHA in the browser; not passed. Versions were confirmed from title pages and UNFCCC file folders (`document_status.csv`). No table mixes versions: Honduras rows use NDC 3.0 (HON-01) only; the second update (HON-02) gives no NDC row.
- **Documents still pending (6 of 12):** Dominican Republic LT-LEDS (draft awaiting launch) and PEN 2025-2038; Ecuador ENEM; Honduras ENDRCH (not published) and NDC 3.0 technical annex; Jamaica BTR1 and NID. Fetched: ICE PEG 2022-2040 (CR-22), Costa Rica INDC Spanish (CR-21), PNMUS (ECU-21), ENDBE UNFCCC file (GUA-21), ENME (HON-21); the Jamaica LTS UNFCCC file is byte-identical to JAM-02.
- **12 conflicts held back** (section 3) and **5 rows with no number or no stated year** held back (`scenario_values_held_back.csv`).
- **165 values with two checks**, most for want of a second place (section 2).
- **Unconfirmed lead:** the UNFCCC case study naming CLG, UWI and CIRED for Jamaica's long-term strategy gave a bot check; not confirmed.
- **Values found in step D not yet given three checks**, among them the ICE PEG 2022-2040 that Costa Rica's NDC 3.0 relies on; they are not in `scenario_values.csv`.
- **Background tasks:** three ran at once for some minutes (the brief allows two) when a foreground search was moved to the background by the harness while both blind readers ran (GAPS, incidents).
- **Pull request number:** added in a second, report-only commit (a force push to amend is not used).

## 2. Values by check status

733 values checked: 556 at 3 of 3, 165 at 2 of 3, 12 conflicts. Check 2 agreed with check 1 on 698 values at the first comparison; the hub read 32 pages a third time (`parts/third_reading.csv`).
