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
