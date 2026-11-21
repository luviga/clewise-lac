# PROGRESS LAC_FIX_RUN2 20261120T225823Z

Start: base job/fix-run 4ba69d6cc3e6619bcc7ee6aee968ea0c78372b2f, origin/main c42ae07, clone /c/clw_fix (all setup checks passed), free disk on C: 113 GB, EXCEL.EXE processes before Phase A: 0. Leads folder held one file (P3 report docx); the Ecuador NDC II initiatives workbook was not in it.

2026-11-20T22:58:51Z | setup | done | clone checks passed, job folder made, 1 lead file copied
2026-11-20T23:19:01Z | A1 (D7b) | done | level 1 share found: ETED plan Tabla 102 p.306, 0.5 percent; J233 unchanged, source recorded; 18 documents downloaded
2026-11-21T03:39:28Z | search map_dr | partial (stopped on the spend limit before its report) | downloads/map_dr: 56 files (Read the Docs lts-rd pages, LTS-RD repo README and tree, OC-SENI memorias 2018-2023 zips, OC informe anual 2018, CNE DataCNE generation by source xlsx, net-metering pages, IDB 2023 decarbonisation study, IPCC V2 Ch2); research: none | left: research/map_dr.md and map_dr_map.csv; questions (a) emission factors, (b) distributed generation, (c) transmission O&M (answered by d7b), (d) lives and capacity factors
2026-11-21T03:39:28Z | search map_hon | partial (stopped before its report) | downloads/map_hon: 89 files (Read the Docs endrch-hon pages and repo docs, OSTRAM-LAC data-source docs, SEN BEN 2018-2023, ENEE boletines 2018-2021, PIEG 2024-2033 draft and annexes, BTR1, IPCC V2 Ch2 and Ch3); research: none | left: research/map_hon.md and map_hon_map.csv; emission-factor reproduction (PPFOI, PPCOK) from BEN fuel use
2026-11-21T03:39:28Z | search map_jam | finished | downloads/map_jam: 64 files; research/map_jam.md, map_jam_map.csv (43 rows), map_jam_sources.csv (25 rows) | left: capacity by technology end 2018 and end 2024; values not yet checked by me in the files
2026-11-21T03:39:28Z | search d12_lives | partial (stopped before its report) | downloads/d12_lives: 64 files (PLANMICC A-O and OperationalLife CSV at commit 7483e67 with API listings, PME 2018-2027 annexes and chapter 4, PME 2026 adjustment, ARCONEL regulations and resolutions, ARCERNNR cost of service 2021, CELEC statements 2020, IRENA green hydrogen 2020, ATB 2024 definitions, IRS p946); research/d12_lives_sources.csv (24 lines) | left: research/d12_lives.md with the life per class, the CCG kit OperationalLife list, the choice by source rank
2026-11-21T03:39:28Z | search d2_cr | partial (stopped before its report) | downloads/d2_cr: 63 files (CENCE Boletin or Informe Anual 2017-2025, CENCE renewable generation reports 2021-2024, ARESEP open data on plants and installed capacity 2018-2024 and generation by source 2019-2026); research: none | left: research/d2_cr.md (commissionings 2019-2024, capacity and generation by source)
2026-11-21T03:39:28Z | search d2_dr | partial (stopped before its report) | downloads/d2_dr: 49 files (OC-SENI memorias 2018-2023 and 2025 with extracted folders, CNE memorias 2021-2025, CNE net-metering xlsx 2012-2024 and 2012-2025, datos.gob API); research: none | left: research/d2_dr.md (commissionings, capacity, generation, net metering by technology)
2026-11-21T03:39:28Z | search d2_ecu | partial (stopped while reading CENACE; report written in part) | downloads/d2_ecu: 40 files (ARCONEL Estadistica 2018-2023 and 2025, Atlas 2024, multiannual balance 2015-2024 xlsx, BNEE Aug 2026, CENACE Informe Anual 2021-2025 parts, CENACE operating report 2023); research/d2_ecu.md (section (a) commissionings 2018-2025 written; (b) to (d) to check); d2_ecu_sources.csv not written | left: capacity by class and basin, generation, distributed generation, sources csv
2026-11-21T03:39:28Z | search CENACE index | done inside d2_ecu | CENACE Informe Anual 2021 parts 1-2, 2022 part 1, 2023 parts 1-2, 2024 parts 1 and 3, 2025 parts 1-2 in downloads/d2_ecu | left: 2022 part 2 and 2024 part 2 not downloaded
2026-11-21T03:39:28Z | search d2_gua | partial (stopped before its report) | downloads/d2_gua: 95 files (AMM installed capacity 2015-2026, monthly generation GM 2015-2026, INFEST annual reports 2015-2025 with additional tables); research: none | left: research/d2_gua.md (hydro GWh 2015-2025, last observed month, gross or net basis, commissionings, PEIG hydro additions)
2026-11-21T03:39:28Z | search d3_ef | partial (stopped while downloading SEN balances) | downloads/d3_ef: 19 files (IPCC 2006 V2 Ch2 and Ch4, AR4 WG1 Ch2, AR5 WG1 Ch8, DR BUR1 2020 and BTR1 2025, Ecuador CN4/BUR2 2022 and NID 2024, Honduras BEN 2018-2023, BUR1, BUR2, BTR1, NIR 2024); research: none | left: research/d3_ef.md (IPCC defaults and ranges, inventory factor statements, Honduras comparison)
2026-11-21T03:39:28Z | search d7b_trans_om | finished | downloads/d7b_trans_om: 30 files; research/d7b_trans_om.md, d7b_trans_om_sources.csv (18 documents) | left: nothing; result checked by me (ETED Tabla 102 p.306, 0.5 percent)
2026-11-21T03:39:28Z | A2 (draft) | in progress | history_plan_draft.csv 133 tech-years (CR 13, DR 69, ECU 30, GUA 4, JAM 17); history_builds_draft.csv 41 techs (Jamaica and part of Ecuador matched); history_diff_before.csv 1128 rows
2026-11-21T03:39:28Z | A3 (draft) | done | gua_hydro_trace.md: cause = the same 2024-2026 overwrite share applied to different Stage 0 denominators, then the PJ freeze; proposed change written
2026-11-21T03:39:28Z | stop | blocked | spend limit reached; state saved in NOTES_WORKING.md (handover section), PROGRESS.md and the drafts; no model file changed; next: first step not done is A0 (finish searches, build source_map.csv)

Restart (session 2, brief v2): 2026-11-21T04:13:53Z, clone at ac903a2 = origin/job/fix-run, git status shows only the job folder, free disk on C: 104 GB, EXCEL.EXE processes 0, base snapshot /c/clw_base_4ba69d6 made from 4ba69d6, brief v2 copied into the job folder.
2026-11-21T04:13:53Z | restart setup | done | base snapshot made; LAC_BASE=C:/clw_base_4ba69d6
2026-11-21T04:13:53Z | A1 D-ECU1/D-ECU2 proposals | done | 440 rows (proposals_parts/ecu_crude.csv); T within 0.5 percent of F1 for every year
2026-11-21T04:13:53Z | A1 D13 proposals | done | 97 rows (CR 10, DR 29, GUA 15, HON 20, JAM 15, ECU 8); 9 non-plant rows at 31.356 left (logs/d13_not_plants.csv)
2026-11-21T04:13:53Z | A1 D7a proposals | done | 353 formula cells in 26 rows (DR 19, JAM 7); EXTT_CRU band in ecu_crude
2026-11-21T04:13:53Z | A1 D6 proposals | done | 33 cells; r 2019-2024 1.4875 1.7229 1.6322 1.2505 1.2072 1.2392, r(2018)=r(2019), mean 1.432409; 69 monthly values found on cited pages
2026-11-21T04:13:53Z | A1 D5, D2f proposals | done | 30 cells PPBGS, 1 formula PPDHYD CF
2026-11-21T04:13:53Z | A2 D2 config proposals | done | 128 (transport Overwrite rows CR 38, GUA 54, HON 20; PWRSUG and TRBPUGSL Write rows 4; CR 4 and DR 6 cell edits; JAM 4 SmartGrid rows)
2026-11-21T04:13:53Z | searches d12_lives, d3_ef | running (background) | -
2026-11-21T04:32:53Z | search d12_lives | finished | 36 lives; values checked in ARCONEL-004/24 p.40, ARCERNNR 2021 p.18, ATB 2024, kit J31144, PLANMICC L152
2026-11-21T04:32:53Z | A1 D1/D12 proposals | done | 38 rows (34 OperationalLife cells, 4 new FHP rows for PPHD and PRONGS)
2026-11-21T04:32:53Z | A4 starter_kit_deviations.csv | done | 36 earlier + 26 D12 rows
2026-11-21T04:32:53Z | search d3_ef | finished | 243 row-years: 7 match, 48 differ, 188 no source; Ecuador NID URL resolved (CDN copy, byte-identical)
2026-11-21T04:32:53Z | A1 D3 proposals | done | 63 cells (Honduras 2019, Ecuador PROCRU 2022) + 39 ASSUMPTION rows; Dominican values wait for a public URL of the CNE generation file
2026-11-21T04:32:53Z | A3 D8 target | done | AMM 2025 hydro 5,473.52 GWh = 19.7047 PJ (2025, held 2026); URL checked, hash equal
2026-11-21T04:32:53Z | A0 source_map.csv | partial | Jamaica 43 rows; DR and HON maps pending
2026-11-21T04:32:53Z | A2 history_plan.csv, history_builds.csv | done (builds partial) | 180 plan lines, 41 techs; DR and CR commissioning searches running
2026-11-21T04:32:53Z | A5 Gate A | done | PASS (sources 55, proposals 1224)
2026-11-21T04:49:34Z | search d2_dr | finished | DR commissioning, net metering, self-producers; CNE file URL found (hash equal)
2026-11-21T04:49:34Z | search d2_cr | finished | CR capacity 2020-2024, commissioning, generation; Guatemala gas (Actun Can 2020, Ocultun 2024)
2026-11-21T04:49:34Z | B1 backups | done | 14 files, backups/backup_manifest.csv
2026-11-21T04:49:34Z | B2 writes | done | 1,254 writes in 14 workbooks (incl. D3 DR values after URL found)
2026-11-21T04:49:34Z | B3 write_check | done | PASS; unittest manager 4 OK, safe-save 3 PASS; EXCEL.EXE 0
2026-11-21T05:30:02Z | search map_dr, map_hon | finished | source_map.csv 116 rows (DR 44, HON 29, JAM 43)
2026-11-21T05:30:02Z | C1 A2+B1 Ecuador, CR, GUA, HON, JAM | done | all OPTIMAL (CR 4 incl. LTSOPT)
2026-11-21T05:30:02Z | C1 DR first run | NDCNEW, LTSNEW UNDEFINED | cause by values: PPDBGS CF 0.08 (needs 22 MW vs 12 MW cap from 2025) and PPDBIM BAU history (10.8 MW vs 10.1 MW cap)
2026-11-21T05:30:02Z | C1 repair DR | done | PPDBGS CF from IRENA 2025 (D2c), PPDBIM history rows 24 and 82 back to 4ba69d6; rerun OPTIMAL x3
2026-11-21T05:30:02Z | C2 keyed comparison | done | 0 unexplained (recompile_diff_summary.csv); 19 of 19 B1 solves OPTIMAL; write_check PASS
2026-11-21T06:40:00Z | DS1 + Stages 0-3 run 1 | done | Stage 0 18/18 OPTIMAL, tests 10/10; DS1 12 hydro lines + 60 non-hydro plateau lines scaled (T1); Stage 1 13/13; Stage 2 hard 7/7, T8 65, T9 87, T11a 0; Stage 3 tests 10/11 (T4 40 cells, as base); Stage 3 15/18 OPTIMAL, DR BAU/NDCNEW/LTSNEW UNDEFINED
2026-11-21T07:00:51Z | Phase E (agent) | done | cross_sector_check.csv 296 rows, .md; 17 of 18 sector B1 models solve, RD_AFOLU infeasible
2026-11-21T07:00:51Z | D repair DR | done | test solves (logs/dr_testsolve.jsonl): D7a bands at 0.98 still infeasible; upper pins from 2025 cause it; Stage 0 ran PPDHYD at 74-193 PJ (CF 4.22 after D2f); PPDHYD activity limit written from UN statistics (7-10 GWh), policy history rows aligned; DR A2+B1 rerun OPTIMAL x3; C2 0 unexplained
2026-11-21T07:00:51Z | DS1-DS4 run 2 (one full rerun of Stages 0-3) | started | run 1 logs moved to stage_logs/run1
2026-11-21T07:52:21Z | DS1-DS3 run 2 | done | Stage 0 18/18 OPTIMAL, tests 10/10; DS1 0 lines changed (Guatemala denominators unchanged); Stage 1 13/13; Stage 2 hard 7/7, T8 65, T9 87, T11a 0; Stage 3 tests 10/11 (T4 40 cells); Stage 3 18/18 OPTIMAL; RE targets 24/24; share match 7923 pass, 66 warn, 9 fail
2026-11-21T07:52:21Z | DS2 gates | done | pass: Ecuador crude (max 0.004 PJ), PPHD 0, Jamaica PPHROR 34.30 MW, Jamaica hydro, final demand history; FAIL: PP history activity CR/DR/ECU, builds CR/DR/ECU/JAM, Guatemala hydro 2029/2041/2043 (Stage 3 5 percent band)
2026-11-21T07:52:21Z | DS3 results_compare.csv | done | 453 rows
2026-11-21T08:17:07Z | E (agent) | done | see cross_sector_check.md
2026-11-21T08:17:07Z | F outputs | done | REPORT, GAPS, CHANGES written; NOTES_WORKING.md folded and deleted; Guatemala overwrite notes reworded without model figures (shares unchanged); write_check PASS on final state
2026-11-21T08:17:07Z | FS1, FS2 | done | changed paths: six models' A-O/config workbooks and A2/B1 outputs, Guatemala Stage 2 CSV, four stage output folders, job folder; no file over 50 MB; no safesave_tmp; EXCEL.EXE 0; diff --check (cr-at-eol) clean after text normalisation; no em dash in written files; no Co-Authored-By or Generated-with lines
2026-11-21T08:17:53Z | FS3 | done | pushed to job/fix-run; PR #11 description section LAC_FIX_RUN2 added with gh pr edit; PR stays draft
