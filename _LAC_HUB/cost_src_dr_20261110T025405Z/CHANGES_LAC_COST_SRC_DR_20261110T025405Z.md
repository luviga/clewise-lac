# CHANGES LAC_COST_SRC_DR 20261110T025405Z

Sourced cost proposals for the Dominican Republic energy model. Adds files only inside `_LAC_HUB/cost_src_dr_20261110T025405Z/`. No model file changed (gate 1: the SHA-256 of the A-O workbook and the five BAU CSVs are identical before and after).

## Files created (tracked)

- `BRIEF_LAC_COST_SRC_DR.md`: the brief, copied verbatim
- `CHANGES_LAC_COST_SRC_DR_20261110T025405Z.md`: this file (also the pull request body)
- `GAPS_LAC_COST_SRC_DR_20261110T025405Z.md`: judgement calls, changes above 25 percent, blocked sources, known-limitation candidates
- `REPORT_LAC_COST_SRC_DR_20261110T025405Z.md`: gate results, fuel and plant tables, imports, country task, paper trail
- `baseline.py`: hash script
- `baseline_after.csv`: SHA-256 after
- `baseline_before.csv`: SHA-256 before
- `build_logs.py`: search_log.csv and paper_trace.csv
- `build_sources.py`: sources.csv and constants.csv
- `common.py`: shared paths and lists
- `constants.csv`: constants with source and locator (CPI-U, benchmarks, WEO 2025 values, conversion factors)
- `constants_fuel.csv`: constants written by the fuel script (merged into constants.csv)
- `cost_rows_current.csv`: every CapitalCost, FixedCost and VariableCost row of Primary and Secondary Techs with scope
- `dump_docx.py`: paper text extraction
- `fuel_prices.csv`: supply row prices by year and scenario with r, benchmark, WEO series and derivation
- `fuel_summary.csv`: one line per supply row for the report
- `gate_results_pre.txt`: gate output before the commit
- `gates.py`: Step 9 gates
- `paper_trace.csv`: statements in the CLEWISE papers that concern DR costs, and what they will need to say
- `plant_costs.csv`: plant cost cells with P2 class, sources and derivations
- `plant_summary.csv`: one line per plant and parameter for the report
- `price_points_2024.csv`: every published 2024 price point beside the chosen one, with the difference in percent
- `proposals.csv`: one row per workbook cell to write (the only file LAC_COST_WRITE reads)
- `proposals_summary.csv`: 2024, 2030 and 2050 current and proposed values by technology, parameter and scenario
- `search_log.csv`: leads tried, with URL or query and result
- `section5_recheck.csv`: recomputation of the brief's section 5 table from the BAU CSVs
- `sources.csv`: source records (13 new, the rest reused from LAC_LOCAL_PRICES)
- `step3_cost_rows.py`: Step 3
- `step4_fuel_prices.py`: Step 4
- `step5_plant_costs.py`: Steps 5 and 6
- `step8_proposals.py`: Step 8
- `write_reports.py`: this report set

## Downloaded or copied (local only, `downloads/`, not tracked)

- `bench/bls_CUUR0000SA0_get.json`: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2016&endyear=2025&annualaverage=true
- `bench/RBRTEa.xls`: https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls
- `bench/RNGWHHDa.xls`: https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls
- `bench/CMO-Historical-Data-Annual.xlsx`: https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx
- `weo/WorldEnergyOutlook2025.pdf`: https://www.iea.org/reports/world-energy-outlook-2025
- `gas/te_press.html`: https://totalenergies.com/newsroom/liquefied-natural-gas-totalenergies-will-supply-400000-tons-lng-year-15-years/?lang=eng
- `gas/NG_MOVE_EXPC_S1_A.xls`: https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_A.xls
- `pen/PEN2022-2037.pdf`: https://cne.gob.do/wp-admin/admin-ajax.php?action=outofthebox-download&OutoftheBoxpath=%2Fpen2022-2037.pdf&lastpath=%2F&account_id=dbid:AAAGpYR0ODh0f0jJZRlCsjhWYMYovXEms_Q&listtoken=255346f20b4341ea85f9ebf4917022f4&dl=1
- `irena/IRENA_Renewable_power_generation_costs_in_2022.pdf`: https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf
- `irena/IRENA_TEC_RPGC_in_2024_2025.pdf`: https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_TEC_RPGC_in_2024_2025.pdf
- `atb/ATBe_2023.parquet`: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2023/ATBe.parquet
- `atb/ATBe_2024_v3.0.0.parquet`: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2024/v3.0.0/ATBe.parquet
- `weo/WorldEnergyOutlook2023.pdf`: https://iea.blob.core.windows.net/assets/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf
- `lp/DR/` and `lp/GEN/`: copies of the LAC_LOCAL_PRICES downloads for the reused source ids (DR-001 to DR-152, GEN-001 to GEN-008); URLs in `sources.csv`.
- `paper/`: copies of CLEWISE_MethodsX_v02.docx, CLEWISE_DataInBrief.docx, CLEWISE_JCLP_draft_v2.docx, Suplementary.xlsx and Data_v2.xlsx, read only, with text extractions.

## Model files

No model file changed.
