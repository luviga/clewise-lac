# PROGRESS LAC_OVERNIGHT_COST_RUN 20261111T071733Z

UTC time | step | status | key count
2026-11-11T07:19:10Z | setup | done | clone at 4124868, branch job/cost-write-run, C: free 129G, EXCEL.EXE running 0, glpsol at C:/glpk-4.65/w64 on PATH, py = Python 3.12.0 (not Anaconda)
2026-11-11T07:20:02Z | A1 | done | save_ao_safely writes <stem>.safesave_tmp<suffix>, recalc, guard, then os.replace; cleanup and re-raise on error
2026-11-11T07:20:02Z | A2 | done | 3 tests added, 5 tests in test_ao_safe_save.py
2026-11-11T07:20:02Z | A3 | done | 2 .gitignore lines added
2026-11-11T07:20:02Z | A4 | done | test_ao_safe_save 5 of 5 PASS; test_ao_cost_repair_manager 4 of 4 OK (via unittest discover, literal -m command cannot import under -I); 3 writers unchanged (SHA-256), 1 save_ao_safely( call each
2026-11-11T08:25:20Z | B1 | done | A2 compiler per country found (one distinct file each); Anaconda Python + pandas 2.2.2 (Guatemala via pandas shim); CR, GUA, HON exact (0 differing values); DR 393 per scenario (transport edit), ECU NDCNEW/LTSNEW 1229 each (pre-patch hydro), JAM 764 per scenario (restored blanks)
2026-11-11T08:25:20Z | B2 | done | B1 runner per country; CR, ECU BAU, GUA, HON exact incl. data files vs main copy; DR 444/587/579 (transport, follows A2); ECU NDCNEW/LTSNEW 464 (pre-patch hydro); JAM vs 12 May tracked 904/3308/25, data files vs 27 Jan 23/25/25 (12 May planned-capacity edits); all 19 B1 solves OPTIMAL
2026-11-11T08:25:20Z | B3 | done | no country unverified; every difference explained (baseline_A2_diff.csv, baseline_B1_diff.csv)
2026-11-11T08:25:20Z | B4 | done | tracked files restored (git status clean outside the job folder); Executables kept (gitignored)
2026-11-11T08:29:43Z | C1 | done | write_set.csv 13020 cells (proposals_all 10103, regional 850, D2 30, D3 1882, D4 66, D6 26, D8 fill 63); skipped 210 empty proposals and 951 unchanged keep cells; D5 and D10 cells none in the proposals
2026-11-11T08:29:43Z | C2 | done | 13020 cells located (row_index recorded), unplaced 0; 6 manifests; 87 rows switched to User defined (D8 83, D8 EMPTY 2, D4 2)
2026-11-11T08:43:28Z | C3 | done | 7 workbooks backed up (SHA-256 in backup_manifest.csv); ao_cost_repair_manager apply + verify per country: 13020 cells changed, 87 projection modes changed, verify passed 6 of 6; D9 written (M25 0.675 to 0.00667)
2026-11-11T08:43:28Z | C4 | done | (1) 13020 of 13020 pass; (2) FAIL strict: 13020 manifest + 87 mode + 1 D9, plus 5 dependent formulas recalculated and 1 formula text normalised (see write_check.csv); (3) 0 blank formula cells; (4) 469 of 469 other A-O workbooks identical
2026-11-11T08:43:28Z | C5 | done | assumptions_final.csv 2015 rows (62 D7 removals); currency_conversion.csv 388 groups (359 D3 groups, 29 regional or D2 groups)
2026-11-11T09:17:45Z | D1 | done | A2 and B1 recompiled for 6 countries with the Phase B commands (all exits 0)
2026-11-11T09:17:45Z | D2 | done | recompile_diff_summary.csv: 107247 differing values, 106923 allowed (written cost cells; CR E5INDCOA 2021 in A2 only), 324 not allowed: Guatemala DIST_FLEXFUEL VariableCost 33 per scenario and Honduras PPBGS CapitalCost 2018-2020 3 per scenario, in A2, B1 and data files, caused by workbook formulas on written cells (recorded, not fixed); compiled_check 39060 cell-scenario checks, 27 differ by 0.0001 at rounding ties
2026-11-11T09:17:45Z | D3 | done | 19 B1 _0 solves OPTIMAL (CR 4 incl. temporary LTSOPT); objectives in recompile/<country>/B1/solve_log.jsonl; 16 May FINAL data files re-solved: 18 of 18 OPTIMAL (resolve_16may.jsonl)
2026-11-11T10:07:47Z | E1 | done | Stage 0: 18 of 18 OK (all OPTIMAL), stage0_test 10 of 10 (third attempt; attempts 1 and 2 failed, see GAPS); Stage 1: 13 of 13; Stage 2: 7 of 7 hard, soft T8, T9, T11a fail; Stage 3: stage3_test 10 of 11 (T4 40 Guatemala cells from --skip-orphan-cap), 18 of 18 OPTIMAL, RE targets 24 of 24, share validation 7882 pass, 108 warn, 8 fail
2026-11-11T10:07:47Z | E2 | done | results_compare.csv 463 rows, results_compare_top_newcap.csv; 16 May objectives from resolve_16may.jsonl
2026-11-11T10:07:47Z | E3 | done | Guatemala PPPVT new capacity before 2025 unchanged: 0.667 GW in NDCNEW and LTSNEW (0.386 GW 2018, 0.280 GW 2022), 0 in BAU; driven by B1 NDCNEW/LTSNEW activity lower limits 2018-2024 (3.81 PJ in 2018, 6.46 PJ in 2022 against 0.54 and 0.63 PJ in BAU)
2026-11-11T10:11:58Z | F1 | done | changed paths only in the allowed set (Phase A files, 7 workbooks, A2/B1 outputs of 6 models, 4 stage folders, job folder)
2026-11-11T10:11:58Z | F2 | done | no file above 50 MB, 0 safesave_tmp files, EXCEL.EXE 0 = start, no em dash, no trailers; git diff --check flags only CR line endings of the CRLF pipeline CSVs (clean with cr-at-eol)
2026-11-11T10:11:58Z | F3 | done | REPORT, GAPS, CHANGES written; pushed; draft PR body updated from CHANGES
