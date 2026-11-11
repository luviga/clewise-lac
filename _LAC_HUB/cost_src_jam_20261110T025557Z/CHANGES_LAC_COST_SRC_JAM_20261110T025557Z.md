# CHANGES: LAC_COST_SRC_JAM 20261110T025557Z

Sourced cost proposals for the Jamaica energy model (`Jamaica/JAM_ENERGY`). This job adds files in `_LAC_HUB/cost_src_jam_20261110T025557Z/` only. No model file changed: the SHA-256 of the A-O workbook and of the five BAU parameter CSVs are the same before and after (`baseline_before.csv`, `baseline_after.csv`).

## What the pull request carries

- `proposals.csv`: 2,520 rows, the only file LAC_COST_WRITE reads. One row per cell, every year 2021 to 2055: 11 fuel supply rows (VariableCost, STEPS, CPS and NZE) and 13 power plants (CapitalCost, FixedCost, VariableCost).
- Fuel prices are pre-tax import or wholesale prices from Jamaica's own published data (UN Comtrade, MSET Energy Statistics, OUR), in USD/GJ net, real 2024 USD (US CPI-U). Projections follow IEA WEO 2025 Table 2.3 by scenario through an average local-to-benchmark ratio (Brent, Henry Hub, Richards Bay coal).
- Plant costs: the current values are kept wherever a source gives the same number within 2 percent: the 2018 Jamaica IRP, NREL ATB 2024, IRENA 2022 and the OUR 2010 expansion plan. Otherwise the first source in the brief's order is proposed. Fixes include the diesel and fuel-oil plants, which carried the biomass capital cost, and a monthly-for-yearly fixed cost slip on the fuel-oil plant.
- Four technologies rest on ASSUMPTION sentences: kerosene and jet in 2024, the two storage-paired plants, and zero variable O&M for dam hydro and geothermal.

## Files created (tracked)

| File | Purpose |
|---|---|
| `BRIEF_LAC_COST_SRC_JAM.md` | Copy of the brief |
| `REPORT_LAC_COST_SRC_JAM_20261110T025557Z.md` | Results, gates, tables |
| `GAPS_LAC_COST_SRC_JAM_20261110T025557Z.md` | Judgement calls, ASSUMPTION leads, large changes, blocked sources, known-limitation candidates |
| `CHANGES_LAC_COST_SRC_JAM_20261110T025557Z.md` | This file |
| `baseline_before.csv`, `baseline_after.csv` | SHA-256 of the six Jamaica model files before and after |
| `cost_rows_current.csv` | Step 3: every CapitalCost, FixedCost and VariableCost row of Primary Techs and Secondary Techs (A-O cached values) with scope |
| `capacity_rows_current.csv` | Residual and maximum capacity rows of the plants in scope (check of section 5) |
| `paper_trace.csv` | Step 2: 61 statements in the CLEWISE papers on costs and fuel prices, and what each will need to say |
| `petrojam_weekly.csv` | 200 parsed weekly Petrojam prices (J$/L), 2023 to 2026 |
| `fuel_prices.csv` | Step 4: price per supply row, year and scenario, with case, r and derivation |
| `fuel_summary.csv` | One line per supply row: 2024 value, r, 2030 and 2050 values, step at the join |
| `price_points_2024.csv` | Rule F2: every published 2024 point per supply row with its difference from the chosen point |
| `fuel_constants.csv` | Constants used by the fuel step (merged into `constants.csv`) |
| `fuel_assumptions.txt` | ASSUMPTION sentences for kerosene, jet and gas (JSON text) |
| `atb2024_series.csv` | Extract of the NREL ATB 2024 rows used (Moderate, Market, 30-year) |
| `plant_costs.csv` | Step 5: plant value per technology, parameter and year with class, sources and derivation |
| `plant_sources.csv` | Plant sources before merging into `sources.csv` |
| `proposals.csv`, `proposals_summary.csv` | Step 8 |
| `sources.csv` | 37 sources cited, each with URL, locator, retrieval date and downloaded file |
| `constants.csv` | 87 constants with source and locator |
| `search_log.csv`, `search_log_fuel.csv` | Leads tried (81 rows), fuel and plant |
| `gates_output.txt` | Output of the gate script |
| `baseline.py`, `extract_cost_rows.py`, `paper_dump.py`, `parse_petrojam.py`, `build_fuel.py`, `extract_atb.py`, `build_plant.py`, `build_logs.py`, `assemble.py`, `build_sources.py`, `build_paper_trace.py`, `gates.py` | Helper scripts, run with `py -I` in this order |

## Files downloaded or copied (local only, `downloads/`, not tracked)

| File | Origin |
|---|---|
| `RBRTEa.xls` | https://www.eia.gov/dnav/pet/hist_xls/RBRTEa.xls |
| `RNGWHHDa.xls` | https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls |
| `NG_MOVE_EXPC_S1_A.xls` | https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_A.xls |
| `PET_PRI_SPT_S1_A.xls` | https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_A.xls |
| `CMO-Historical-Data-Annual.xlsx` | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx |
| `bls_cpiu_v1_post_2016_2025.json` | https://api.bls.gov/publicAPI/v1/timeseries/data/ (POST, series CUUR0000SA0, 2016 to 2025) |
| `census_exports_JAM_2710_HS10_2024.json` | US Census API missing-key page (blocked attempt, kept as evidence) |
| `WorldEnergyOutlook2025.pdf` | copy of the LAC_LOCAL_PRICES manual download (origin https://www.iea.org/reports/world-energy-outlook-2025) |
| `petrojam/` | copies of the 10 Petrojam listing pages saved by hand for LAC_LOCAL_PRICES and their log (origin https://www.petrojam.com/price/?wpv_view_count=1537-TCPID11733&wpcf_price_date=&wpv_paged=N) |
| `JAM/`, `GEN/` | copies of the LAC_LOCAL_PRICES downloads for the reused sources JAM-001 to JAM-023 and GEN-001 to GEN-008 |
| `plant/` | IRENA Renewable Power Generation Costs in 2022 and in 2025 (with annex), IEA WEO 2023 and 2025, IEA GEC documentation 2023, publication pages, leads and search log of the IRENA and IEA research step |
| `plant2/` | 2018 Jamaica IRP (MSET and ESMAP copies), IRP-2 (2023), OUR Generation Expansion Plan 2010 and avoided cost parameters 2008, NREL ATB 2024 `ATBe.csv` v4.0.0, ATB pages, EIA capital cost reports (AEO2020, AEO2023, AEO2025), geothermal sources, leads and search log of the ATB and Jamaica research step |
| `paper/` | read copies of `CLEWISE_MethodsX_v02.docx`, `CLEWISE_DataInBrief.docx`, `CLEWISE_JCLP_draft_v2.docx`, `Suplementary.xlsx`, `Data_v2.xlsx` (OneDrive left untouched) |

## Confirmation

No model file changed. Gate 1 recomputed the six hashes after all steps and they equal the baseline. The commit touches only files inside `_LAC_HUB/cost_src_jam_20261110T025557Z/`.
