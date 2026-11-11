# PROGRESS LAC_FIX_RUN 20261111T200825Z

Start: base origin/main c42ae07ac81f0f3a28f6275e7ce356f9696c4f77, branch job/fix-run, clone /c/clw_fix, free disk on C: 93 GB, EXCEL.EXE processes before Phase A: 0.

2026-11-11T20:09:00Z | setup | done | clone at c42ae07, job folder made, disk 93 GB free, EXCEL.EXE 0
2026-11-11T20:38:36Z | A1 (part) | in progress | R4 currency years found for all 109 groups (3764 cells, ~3244 change); R5 304 matched cells (14 already regional); R6 dry run 1230 config cells; R7 IRP-2 34.3 MW schedule found; R2 source confirmed; R3 prices sourced; ECU volumes and R1 sources pending (agents)
2026-11-11T20:49:37Z | A2 | done | starter_kit_deviations.csv 36 rows (30 EXTT_CRU MINOIL cells, 3 R5 PV and wind cells, 3 hydro rows)
2026-11-11T20:52:59Z | A1 | done | sources.csv 111 ids; proposals.csv 4471 rows (R1 38, R2 4, R3 155, R4 2558, R4+R5 126, R5 105, R6 1226, R7 59); sources_pending.csv 41 rows
2026-11-11T20:52:59Z | A3 | done | Phase A commit
2026-11-11T21:01:15Z | B1 | done | 13 files backed up with SHA-256 (backups/backup_manifest.csv)
2026-11-11T21:01:15Z | B2 | done | A-O cells via ao_cost_repair_manager apply+verify: DR 1981, ECU 383 (+38 new-row cells), GUA 337 (+1 mode), HON 89, JAM 383 (+1 mode); A-O_Demand 10 cells; T5CRUEXP VariableCost added to Ecuador Demand Techs row 203 (test compile read it)
2026-11-11T21:01:15Z | B3 | done | configs: CR 62 (R2 4, R6 58), DR 292, ECU 364, GUA 176, HON 208, JAM 134 (R6 128, R7 6); Stage 2 Jamaica CSV 12 lines (R7)
2026-11-11T21:01:15Z | B4 | done | write_check.csv: (1) all written cells equal proposals; (2) FAIL strict: 31 dependent formula cells recalculated (DR J233 J253 =J232*0.5%; Jamaica O198:AQ198 PPHROR lower limit formula); (3) 0 blank formulas; (4) no formula in F1 cells; (5) 472 other A-O workbooks identical; (6) CSV only listed lines
