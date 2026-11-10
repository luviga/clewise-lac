# CHANGES: LAC_COST_SRC_HON 20261110T073537Z

Sourced cost proposals for the Honduras energy model: fuel supply rows, power plants and electricity imports, with the paper trail. This job adds files in `_LAC_HUB/cost_src_hon_20261110T073537Z/` only. No model file changed: the SHA-256 of the Honduras A-O workbook and the BAU CapitalCost, FixedCost, VariableCost, InputActivityRatio and OutputActivityRatio CSVs are equal before and after (`baseline_before.csv`, `baseline_after.csv`).

## Output files (tracked)

- `REPORT_LAC_COST_SRC_HON_20261110T073537Z.md`: gates, fuel, plant and import tables, paper trail summary.
- `GAPS_LAC_COST_SRC_HON_20261110T073537Z.md`: judgement calls, ASSUMPTION rows and leads, changes above 25 percent, blocked sources, known-limitation candidates.
- `CHANGES_LAC_COST_SRC_HON_20261110T073537Z.md`: this file.
- `BRIEF_LAC_COST_SRC_HON.md`: copy of the brief.
- `proposals.csv`: one row per cell to write (1,994 rows); the file LAC_COST_WRITE reads.
- `proposals_summary.csv`: 2024, 2030 and 2050 current and proposed values per technology and parameter.
- `fuel_prices.csv`: fuel series by row, year and scenario, with case, r, benchmark, WEO series, sources and derivation.
- `fuel_summary.csv`: one line per supply row (r, 2030 and 2050 values, step at the join).
- `price_points_2024.csv`: every published 2024 price point per supply row, the chosen one marked, with the difference in percent.
- `plant_costs.csv`: plant and import rows by year with current and proposed values, P2 class, sources and derivation.
- `cost_rows_current.csv`: every CapitalCost, FixedCost and VariableCost row of Primary Techs and Secondary Techs with its scope.
- `capacity_rows_current.csv`: residual capacity, capacity limits and activity limits of the rows in scope.
- `section5_check.csv`: section 5 values recomputed from the BAU CSVs.
- `atb2024_series.csv`: the NREL ATB 2024 rows used (Moderate, Market, 30 years).
- `cree_mer_monthly.csv`: monthly MER import rows (contract and spot) parsed from the CREE tariff reports.
- `paper_trace.csv`: 44 statements in the CLEWISE papers and what they will need to say.
- `sources.csv`: 81 sources (reused LAC_LOCAL_PRICES ids GEN-, HON- and new CSH- ids).
- `constants.csv`, `fuel_constants.csv`: conversion constants, CPI-U, benchmarks and the WEO 2025 values used, with page and table.
- `search_log.csv`, `imp_leads.csv`: every lead tried.
- `fuel_assumptions.txt`: the natural gas sentence of rule F5.
- `gates_output.txt`: output of the gate script.
- `baseline_before.csv`, `baseline_after.csv`: model file hashes.
- Scripts: `baseline.py` (hashes), `extract_cost_rows.py` (Step 3), `paper_dump.py` and `build_paper_trace.py` (Step 2), `build_fuel.py` (Step 4), `extract_atb.py` and `build_plant.py` (Step 5), `parse_cree_mer.py` and `build_import.py` (Step 6), `assemble.py` (Step 8), `build_logs.py`, `build_sources.py`, `gates.py` (Step 9), `normalize_eol.py` (LF line endings). Run order: extract_cost_rows, build_fuel, extract_atb, build_plant, parse_cree_mer, build_import, assemble, build_paper_trace, build_logs, build_sources, baseline after, gates, normalize_eol (line endings).

## Downloaded files (local only, `downloads/`, not tracked)

- `RBRTEa.xls`: https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls (Brent annual).
- `RNGWHHDa.xls`: https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls (Henry Hub annual).
- `CMO-Historical-Data-Annual.xlsx`, `CMO-Historical-Data-Monthly.xlsx`: World Bank Pink Sheet, https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/ (annual used; monthly opened to look for a Colombian coal series).
- `bls_cpiu_v1_2016_2025.json`: BLS public API, series CUUR0000SA0.
- `WorldEnergyOutlook2025.pdf`: copied from the LAC_LOCAL_PRICES manual downloads; origin https://www.iea.org/reports/world-energy-outlook-2025.
- `HON/`, `GEN/`: files of the reused LAC_LOCAL_PRICES sources, copied from that job's downloads.
- `HON_extra/comtrade_mirror_exports_to_HON_2024_coal_coke.json`, `HON_extra/comtrade_HON_2025_M_coal_coke.json`: UN Comtrade preview API (mirror exports to Honduras 2024; Honduras imports 2025, no data).
- `plant/IRENA_Renewable_power_generation_costs_in_2022.pdf`, `plant/IRENA_TEC_RPGC_in_2025_2026.pdf`: IRENA, URLs in `sources.csv` (CSH-011, CSH-012); `plant/irena2022.txt`, `plant/irena2025.txt` text dumps.
- `plant/WorldEnergyOutlook2023.pdf`: https://www.iea.org/files/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf.
- `plant/ATBe_2024_v4.0.0.csv`: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2024/v4.0.0/ATBe.csv.
- `plant/G02-Anexos-PIEG-2024-2033-Aprobado.pdf`: https://cnd.enee.hn/wp-content/uploads/2024/07/G02-Anexos-PIEG-2024-2033-Aprobado.pdf.
- `plant/png/`: page images of Tabla 7 (PIEG 2024-2033) and Tabla B-3 used to confirm the values.
- `imp/`: CREE quarterly tariff reports 2022 to 2025 (https://www.cree.gob.hn/wp-content/uploads/2019/02/...), CRIE annual and statistical MER reports 2018 to 2024 (https://crie.org.gt/wp-content/uploads/...), EOR pages and memoria, CREE media search results, page images.
- `paper/`: copies of the five CLEWISE paper files from the OneDrive folder (read-only source) and their text dumps in `paper/txt/`.
