# CHANGES LAC_PRICE_SOURCES 20261109T003525Z

No model file changed. The SHA-256 of the six A-O energy workbooks and of `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx` is identical before and after (`baseline_before.csv`, `baseline_after.csv`). Model workbooks were opened read-only (openpyxl, read_only=True, never saved).

All files below are in `_LAC_HUB/price_sources_20261109T003525Z/`. The complete list of every file with its origin URL or purpose, including the 500+ downloaded regulator documents, is in `file_inventory.csv`.

## Outputs and scripts

- `CHANGES_LAC_PRICE_SOURCES_20261109T003525Z.md`: this file
- `GAPS_LAC_PRICE_SOURCES_20261109T003525Z.md`: judgement calls, blocked sources, assumptions, limitations
- `REPORT_LAC_PRICE_SOURCES_20261109T003525Z.md`: main report (gates, short answer, Steps 1-5)
- `adders.py`: Step 4 script: observed and built adders
- `adders_2024.csv`: Step 4 output: adders by country and fuel
- `adders_assumptions.py`: Step 4 script: built LNG adders and ASSUMPTION candidates
- `adders_working.txt`: Step 4 working lines
- `ao_dsl_foi_2025.csv`: Step 5 extract of model values
- `baseline.py`: SHA-256 read-only gate script
- `baseline_after.csv`: hashes after Step 5
- `baseline_before.csv`: hashes before Step 1
- `benchmarks.csv`: Step 1 benchmark list
- `build_sources.py`: script that builds sources.csv
- `file_inventory.csv`: every file in the folder with origin URL or purpose
- `history.py`: Step 2 script: annual averages and USD/GJ conversion
- `history_ratios.csv`: Step 2 output: product-to-driver ratios
- `history_usd_per_gj.csv`: Step 2 output: annual benchmark values 2018-2025 with sources
- `list_files.py`: script that builds file_inventory.csv
- `monthly_benchmarks.csv`: Step 2 output: monthly benchmark values 2017-2026 as published
- `projection_method.md`: Step 3 rule for each fuel
- `projections.csv`: Step 3 output: driver projections as published
- `projections.py`: Step 3 script: AEO2025 extraction
- `projections_usd_per_gj.csv`: Step 3 output: Brent and Henry Hub in 2024 USD/GJ
- `projections_wb_cmo.py`: Step 3 script: appends World Bank CMO Oct 2026 forecasts
- `read_ao_2025.py`: Step 5 script: read-only extract of model diesel and fuel oil rows
- `sanity.py`: Step 5 script: ratio of model to parity
- `sanity_check_2025.csv`: Step 5 output
- `sources.csv`: all sources with URL, title, publisher, date, retrieval date
- `sources_core.csv`: sources opened in the main session

## Downloaded public data (main session)

- `downloads/CMO-Historical-Data-Annual.xlsx`: downloaded from https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx
- `downloads/CMO-Historical-Data-Monthly.xlsx`: downloaded from https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx
- `downloads/CMO-October-2026-Forecasts.pdf`: downloaded from https://thedocs.worldbank.org/en/doc/2ac43f46629cf90c2ea5b8929a343593-0050012026/related/CMO-October-2026-Forecasts.pdf
- `downloads/CMO-Pink-Sheet-November-2026.pdf`: downloaded from https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-November-2026.pdf
- `downloads/PET_PRI_REFOTH_A_EPPR_PWG_DPGAL_M.xls`: downloaded from https://www.eia.gov/dnav/pet/xls/PET_PRI_REFOTH_A_EPPR_PWG_DPGAL_M.xls
- `downloads/PET_PRI_REFOTH_A_EPPV_PWG_DPGAL_M.xls`: downloaded from https://www.eia.gov/dnav/pet/xls/PET_PRI_REFOTH_A_EPPV_PWG_DPGAL_M.xls
- `downloads/PET_PRI_SPT_S1_A.xls`: downloaded from https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_A.xls
- `downloads/PET_PRI_SPT_S1_M.xls`: downloaded from https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_M.xls
- `downloads/aeo2025/highprice_aeotab12.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/highprice/aeotab12.xlsx
- `downloads/aeo2025/highprice_aeotab13.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/highprice/aeotab13.xlsx
- `downloads/aeo2025/highprice_aeotab15.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/highprice/aeotab15.xlsx
- `downloads/aeo2025/lowprice_aeotab12.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/lowprice/aeotab12.xlsx
- `downloads/aeo2025/lowprice_aeotab13.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/lowprice/aeotab13.xlsx
- `downloads/aeo2025/lowprice_aeotab15.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/sidecases/lowprice/aeotab15.xlsx
- `downloads/aeo2025/ref_aeotab12.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/aeotab12.xlsx
- `downloads/aeo2025/ref_aeotab13.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/aeotab13.xlsx
- `downloads/aeo2025/ref_aeotab15.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/aeotab15.xlsx
- `downloads/aeo2026/ref_aeotab12.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/aeotab12.xlsx
- `downloads/aeo2026/ref_aeotab13.xlsx`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/excel/aeotab13.xlsx
- `downloads/conversion/IPCC2006_V2_1_Ch1_Introduction.pdf`: downloaded from https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf
- `downloads/conversion/UNSD_EnergyYearbook2023_09ii.pdf`: downloaded from https://unstats.un.org/unsd/energystats/pubs/yearbook/2023/09ii.pdf
- `downloads/conversion/eia_faq_heat_content_ng.html`: downloaded from https://www.eia.gov/tools/faqs/faq.php?id=45&t=8
- `downloads/eia_aeo25_ref.html`: downloaded public file (origin listed in the folder's notes file or sources.csv)
- `downloads/eia_aeo25_side.html`: downloaded from https://www.eia.gov/outlooks/archive/aeo25/tables_side_xls.php
- `downloads/eia_aeo_index.html`: downloaded public file (origin listed in the folder's notes file or sources.csv)
- `downloads/eia_aeo_side.html`: downloaded from https://www.eia.gov/outlooks/aeo/tables_side_xls.php
- `downloads/eia_epm/epm_index.html`: downloaded public file (origin listed in the folder's notes file or sources.csv)
- `downloads/eia_epm/table_4_01.xlsx`: downloaded from https://www.eia.gov/electricity/monthly/xls/table_4_01.xlsx
- `downloads/eia_epm/table_4_01continued.xlsx`: downloaded from https://www.eia.gov/electricity/monthly/xls/table_4_01continued.xlsx
- `downloads/eia_ng/NG_MOVE_EXPC_S1_M.xls`: downloaded from https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_M.xls
- `downloads/eia_ng/NG_PRI_FUT_S1_M.xls`: downloaded from https://www.eia.gov/dnav/ng/xls/NG_PRI_FUT_S1_M.xls
- `downloads/eia_ng/NG_PRI_SUM_DCU_NUS_M.xls`: downloaded from https://www.eia.gov/dnav/ng/xls/NG_PRI_SUM_DCU_NUS_M.xls
- `downloads/lng/CRS_R45006_2017.html`: downloaded from https://www.everycrsreport.com/files/20171101_R45006_df0760946ebf24c3b677c09eacc757679458e113.html
- `downloads/lng/lngindustry_caribbean_part2.html`: downloaded from https://www.lngindustry.com/liquefaction/29112017/will-a-gas-market-develop-in-the-caribbean-part-two
- `downloads/wb_commodity_markets.html`: downloaded from https://www.worldbank.org/en/research/commodity-markets

## Country folders (regulator documents downloaded by the country sub-tasks)

- `downloads/CR/`: 40 files (16 downloaded documents, plus helper scripts, text extracts, page renders, `CR_regulator_2024.csv` and `CR_notes.md`); each file and its origin is in `file_inventory.csv`.
- `downloads/DR/`: 191 files (167 downloaded documents, plus helper scripts, text extracts, page renders, `DR_regulator_2024.csv` and `DR_notes.md`); each file and its origin is in `file_inventory.csv`.
- `downloads/GUA/`: 94 files (86 downloaded documents, plus helper scripts, text extracts, page renders, `GUA_regulator_2024.csv` and `GUA_notes.md`); each file and its origin is in `file_inventory.csv`.
- `downloads/HON/`: 75 files (55 downloaded documents, plus helper scripts, text extracts, page renders, `HON_regulator_2024.csv` and `HON_notes.md`); each file and its origin is in `file_inventory.csv`.
- `downloads/JAM/`: 82 files (72 downloaded documents, plus helper scripts, text extracts, page renders, `JAM_regulator_2024.csv` and `JAM_notes.md`); each file and its origin is in `file_inventory.csv`.
- `downloads/ECU/`: 20 files (3 downloaded documents, plus helper scripts, text extracts, page renders, `ECU_regulator_2024.csv` and `ECU_notes.md`); each file and its origin is in `file_inventory.csv`.

## Files written outside the output folder

- Seven scratch files (HTML pages and PNG page renders) in Claude's session temp scratchpad, written by the country sub-tasks; one PDF cached by a fetch tool in its own temp folder. Nothing outside the output folder inside MODELS_LAC_5.
- Deleted in this session: empty files from failed EIA downloads (HTTP 404 and wrong file names); EIA files downloaded and found not relevant (PET_PRI_RESID_A_EPPR_PTA_DPGAL_M.xls retail residual ending 2011, PET_PRI_REFOTH_A_EPPV_PTG_DPGAL_M.xls avgas retail, Electric Power Monthly state tables 4.10, 4.12 and tables 4.2 to 4.4); the AMM 2024 annual report and Imprenta Nacional Alcances 104-107, opened and deleted by sub-tasks as not relevant.
