# PROGRESS LAC_CLEANUP 20261123T031711Z

Start: clone of the main copy, origin set to GitHub, branch job/cleanup from origin/main (merge of pull request 15). The start-point check against the reviewed tree of pull request 15 printed nothing (equal outside `_LAC_HUB/`). Free disk on C: 78 GB.

| time (UTC) | step | status | note |
|---|---|---|---|
| 2026-11-23T03:17Z | setup | done | clone, branch, stamp, job folder; run scripts copied from LAC_STRUCTURE_TABLES and adapted (job path, temp folder, Stage 3 command read from PIPELINE_WORKFLOW.md) |
| 2026-11-23T03:40Z | step 1 tests | done | lock found: openpyxl 3.1.2 keeps a worksheet stream of a normal-mode load open until the next garbage collection; Excel releases files at once. Test setup collects garbage after each load of the modules under test and before temp folder removal. Both files pass three runs in a row; 0 Excel processes and 0 temp folders left. Patch parked in work/ for the baseline run on the start commit |
| 2026-11-23T03:23Z | step 2 baseline | running | full_run.py baseline (A2 and B1 six countries, Stages 0 to 3, tests) |
| 2026-11-23T04:43Z | step 2 baseline | done | 4,750 s; 19 B1, 18 Stage 0 and 18 Stage 3 solves OPTIMAL; Stage 3 objectives equal to F1; baseline against main: 0 differences in 1,259 files (3 run stamps skipped); stage tests 10/10, 13/13 (stage 1), hard 7/7 (stage 2), stage 3 10/11 (T4 7,958 of 7,998); ShareValidation 9 FAIL; unit tests fail on the start-commit tests (file locks), as expected. Stage 2 hole scan: 97 cases (10 Guatemala BAU, 87 Jamaica PPBIM) |
| 2026-11-23T04:50Z | step 3 code fixes | applied | F5 (3 runners, YAML), F6, F7, docs, step 1 test setup; syntax checked |
| 2026-11-23T04:45Z | step 3 gate run | running | full_run.py step3 |
| 2026-11-23T05:00Z | step 4 preview (scratch copy) | done | Stage 2 fix in a scratch copy of the baseline: 10 Guatemala holes filled, 16 values changed (Guatemala BAU 2030-2031 non-hydro renewables), nothing else; Guatemala Stage 3 under the common rule: BAU OPTIMAL, NDC and LTS no feasible solution; one-group relaxation: only the orphan cap binds (work/gua_relax.csv); step 4.5 row orphan_cap_exempt_scenarios prepared |
| 2026-11-23T06:13Z | step 3 gate run | done | 5,299 s; gate against baseline: 0 differences in 1,259 files, 36 data files and 36 objectives (work/step3_gate_*); F6 changes only the RE target lines of the Stage 3 results log (Costa Rica and Ecuador now checked against their own targets, all 24 pass); unit tests pass in the run |
| 2026-11-23T06:20Z | commit 1 | pushed | code and tables |
| 2026-11-23T06:22Z | step 4 applied | running | Stage 2 overflow branch scales frozen and solar and wind plants together; --skip-orphan-cap removed; controller row orphan_cap_exempt_scenarios; docs; full_run.py step4 |
| 2026-11-23T07:37Z | step 4 run | done | 4,823 s; 18 Stage 3 solves OPTIMAL; T4 passes for all six countries (7,998 of 7,998, all stage 3 tests pass); only the Guatemala BAU objective changes; Guatemala NDC and LTS objectives equal the baseline (a few hydro values move between equal-cost solutions); keyed results compare: only Guatemala rows change (work/step4_results_keyed.csv); stage2_holes.csv: 97 cases, 10 Guatemala BAU filled, 87 Jamaica PPBIM unchanged (other cause) |
| 2026-11-23T07:55Z | commit 2 | pushed | Guatemala Stage 2 and Stage 3; tracked result workbooks left as in main (run outputs restored) |
| 2026-11-23T08:05Z | step 5 deletions | running | 36 entries removed with git rm (2,448 files), 6 .gitignore lines that named the removed folder; full_run.py step5 |
| 2026-11-23T09:01Z | step 5 gate run | done | 4,705 s; gate against step 4: 0 differences in compiled inputs, 36 data files and 36 objectives; the one tree difference is the deleted Stage 1 file CONTROLLER_NEW_SCENARIOS_BEFORE.xlsx, which no run writes; all tests pass |
| 2026-11-23T09:10Z | commit 3 | pushed | deletions |
| 2026-11-23T09:30Z | step 6 edits | applied | 13 workbooks, 3 override CSVs, 3 static TotalAnnualMinCapacity files; workbook_checks.csv: 13 of 13 PASS (first check run failed one Costa Rica cell through a fault of the check, fixed: edited cells looked up at their start coordinates); edits staged before the run (A2 restores A1_Outputs from git) |
| 2026-11-23T09:32Z | step 6 gate run | running | full_run.py step6 |
| 2026-11-23T10:22Z | step 6 gate run | done | 4,641 s; gate against step 5: data files and objectives equal; tree differences are labels and notes only; old-label scan of the six energy models: 0 files after (3 before); all tests pass |
| 2026-11-23T10:40Z | commit 4 | pushed | workbooks and labels |
| 2026-11-23T10:45Z | step 7 | done | draft pull request opened (number in the REPORT); REPORT, GAPS and CHANGES written; commit 5 job folder; diff check clean |
