# PROGRESS LAC_STRUCTURE_TABLES 20261122T042525Z

Start: clone of the repository from GitHub (outside the main copy), branch job/structure-tables from origin/main b51f24b; free disk on C: 76 GB (below the 80 GB line from the start, so the run script prunes solver output over 500 MB after each stage's extraction); EXCEL.EXE processes before work: 0.

| time (UTC) | step | status | note |
|---|---|---|---|
| 2026-11-22T04:25Z | setup | done | clone, branch, stamp, job folder, brief copied, run scripts adapted from LAC_FIX_RUN2 |
| 2026-11-22T04:27Z | A1 baseline run | running (background) | full_run.py baseline: A2+B1 six countries, Stages 0-3, tests; logs stage_logs/baseline |
| 2026-11-22T05:00Z | B1-B3 drafts | done (drafts) | tables at config/ and inputs/, loader lac_tables.py, 26 files edited in draft/ (applied to the tree after A4); fold check OK for all 23 Python files; gate 1 precheck on drafts: 281 yes rows left, all accepted with reason, 97 model file rows kept |
| 2026-11-22T06:09Z | A1 baseline run | done | 18/18 Stage 0 and Stage 3 OPTIMAL; stage tests 10/10, 13/13, 7/7 hard, Stage 3 10/11 (T4 as before); unit tests: manager 2 of 4 errors, safe-save stopped at test 1 (file locks in the temp folder; reruns hung in Excel automation; Excel processes started by the tests stopped); run time 6,107 s |
| 2026-11-22T06:20Z | A2 snapshot | done | baseline snapshot outside the repository (tree + logs; bulky run logs moved there) |
| 2026-11-22T06:21Z | A3 baseline against main | done | 0 differences (3 run stamps skipped); 18 objectives equal to LAC_FIX_RUN2 |
| 2026-11-22T06:22Z | A4 restore | done | git checkout -- . ; clean |
| 2026-11-22T06:25Z | B1-B4 applied | done | drafts applied; fold check 23 OK; gate 1 on branch PASS (281 accepted, 0 not accepted, 97 model rows); register 1,777 rows; local commits (squashed before the push) |
| 2026-11-22T06:30Z | B5 gate run (phaseB) | running | full_run.py phaseB |
| 2026-11-22T07:34Z | B5 gate run (phaseB) | done | 18/18 Stage 0 and Stage 3 OPTIMAL, objectives equal to the baseline; 0 differences in 1,278 output files (3 run stamps skipped); stage and unit tests equal to the baseline list; run time 4,367 s |
| 2026-11-22T07:36Z | B5 gates 4 and 5 | done | tracked outputs restored; gate 4: 25 code files, 9 tables, loader, job folder, 0 other paths; diff --check (cr-at-eol) clean; machine paths of job scripts moved to scripts/machine.py with an untracked machine.json; run logs kept out of git |
| 2026-11-22T07:37Z | B6 commit, push, draft PR 1 | done | one commit on job/structure-tables; draft PR 14, base main |
| 2026-11-22T07:39Z | C1 rename_plan.csv | done | 2,696 rows from the scope scan (c_scan.py scope), action per name |
| 2026-11-22T07:41Z | C2 retire | applied, committed locally | c2 code specs, 12 branches removed, 1,681 rows of older scenarios deleted from the six B1_Scenario_Config.xlsx (checks PASS), Ecuador A2_Output_Params/NDCINC removed |
| 2026-11-22T08:05Z | C2 gate run (c2) | done | A2 and B1 of six countries recompiled (1,366 s); A2 installed files, B1 output parameters and B1 data files of BAU, NDCNEW and LTSNEW equal the baseline by key (0 differences, c2_against_baseline.csv); 18 B1 solves OPTIMAL with equal objectives |
| 2026-11-22T08:08Z | C3 rename | applied, committed locally | catalogue NDCNEW to NDC and LTSNEW to LTS (older rows removed); A2 policy outputs labelled with their folder name; tests and the Stage 2 demand check read the catalogue; 3,030 workbook cells renamed (checks PASS), Stage 2 override CSV and scenario_values renamed, five A-Xtra Other_Scenarios rows deleted; 24 scenario folders moved with git mv |
| 2026-11-22T08:10Z | C4 gate run (phaseC) | running | full_run.py phaseC --phase-c |
| 2026-11-22T09:18Z | C4 gate run (phaseC) | done | 18/18 Stage 0 and Stage 3 OPTIMAL, objectives equal to the baseline under the name mapping; compiled values equal (labels only); stage outputs equal; tests equal to the baseline list; run time 4,126 s |
| 2026-11-22T09:50Z | C4 gates 2 to 4 | done | names_left.csv (gate 2 met for scenario fields, old names left in notes, A1 labels and one pickle: GAPS 1.14); tests read the catalogue; diff --check clean |
| 2026-11-22T09:58Z | C5 commit, push, draft PR 2 | done | commits f3df640 and b6f69a2 on job/structure-rename; draft PR 15, base job/structure-tables |
| 2026-11-22T10:00Z | outputs | done | REPORT, GAPS, CHANGES final; report-only commit with the pull request numbers; EXCEL.EXE processes at the end: 0 |
