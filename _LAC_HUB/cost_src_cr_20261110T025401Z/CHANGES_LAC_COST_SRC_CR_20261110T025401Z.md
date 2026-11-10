# CHANGES LAC_COST_SRC_CR 20261110T025401Z

This job adds sourced cost proposals for the Costa Rica energy model in `_LAC_HUB/cost_src_cr_20261110T025401Z/`. **No model file changed**: the SHA-256 hashes of `A-O_Parametrization.xlsx` and of the BAU `CapitalCost`, `FixedCost`, `VariableCost`, `InputActivityRatio` and `OutputActivityRatio` CSVs are identical before and after (`baseline_before.csv`, `baseline_after.csv`). Files outside the job folder are untouched.

## Files created (tracked)

- `BRIEF_LAC_COST_SRC_CR.md`: copy of the brief.
- `REPORT_LAC_COST_SRC_CR_20261110T025401Z.md`: results, gates, tables.
- `GAPS_LAC_COST_SRC_CR_20261110T025401Z.md`: judgement calls, ASSUMPTION rows, large changes, blocked sources, known-limitation candidates.
- `CHANGES_LAC_COST_SRC_CR_20261110T025401Z.md`: this file.
- `proposals.csv`: the file LAC_COST_WRITE reads. 1,740 rows:
  - 9 supply rows x 3 fuel scenarios x 30 years;
  - 10 plants x 3 parameters x 30 years;
  - the electricity import technology `IMPELE` x 30 years (added after the first push on Luis's instruction).
- `proposals_summary.csv`: one row per technology and parameter, 2024, 2030 and 2050 current and proposed values with the change in percent.
- `structure_proposals.csv`: Step 7, industry coal against petroleum coke (2021 `E5INDCOA` cell in `A-O_Demand.xlsx`).
- `fuel_prices.csv`: fuel series by row, year and scenario, with case, r, benchmark, WEO series and derivation.
- `price_points_2024.csv`: every published 2024 price point per supply row, with the chosen point and the difference in percent.
- `plant_costs.csv`: plant cost classification (P2), proposed values by year and derivations, plus the `IMPELE` import price rows (E1).
- `cost_rows_current.csv`: every CapitalCost, FixedCost and VariableCost row of Primary Techs and Secondary Techs, with scope.
- `paper_trace.csv`: 39 statements in the CLEWISE papers about costs and fuel prices, and what each will need to say.
- `sources.csv`: 41 sources (12 new, 29 reused from LAC_LOCAL_PRICES).
- `constants.csv`: CPI-U, Brent, Henry Hub, coal, WEO 2025 values, plant source values and conversion constants.
- `search_log.csv`: leads tried for fuel, plant and Step 7 rows.
- `baseline_before.csv`, `baseline_after.csv`: model file hashes.
- `gate_results_pre.txt`, `gate_results_post.txt`: gate output.
- `scripts/`:
  - `extract_paper.py`: docx text extraction.
  - `step2_paper_trace.py`: writes `paper_trace.csv`.
  - `step3_cost_rows.py`: writes `cost_rows_current.csv` and recomputes the section 5 table (`section5_recomputed.txt`).
  - `step4_fuel_prices.py`: fuel series (F1 to F6).
  - `atb_extract.py` and `atb_extract.csv`: NREL ATB 2024 rows used.
  - `step5_plant_costs.py`: plant costs (P1 to P3).
  - `step7_structure.py`: Step 7.
  - `step8_build_outputs.py`: proposals, summary, sources, constants, search log.
  - `step9_gates.py`: gates.
  - `sources_fuel.csv`, `sources_plants.csv`, `search_log_fuel.csv`, `search_log_plants.csv`, `fuel_constants_part.csv`, `plant_constants_part.csv`: parts merged by step 8.
  - `fuel_summary.csv`: fuel summary table.

## Files downloaded or copied (local only, `downloads/`, not tracked)

- `bls_CUUR0000SA0_2017_2025_annualaverage.json`: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2017&endyear=2025&annualaverage=true
- `eia_PET_PRI_SPT_S1_A.xls`: https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_A.xls
- `eia_NG_PRI_FUT_S1_A.xls`: https://www.eia.gov/dnav/ng/xls/NG_PRI_FUT_S1_A.xls
- `WB_CMO_Historical_Data_Annual.xlsx`: https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx
- `WorldEnergyOutlook2025.pdf`: copy of the LAC_LOCAL_PRICES manual download (origin https://www.iea.org/reports/world-energy-outlook-2025).
- `Informe Balance de Energia 2022.pdf`: copy of the LAC_LOCAL_PRICES manual download (origin https://www.minae.go.cr/energia/ben/Informe%20Balance%20de%20Energia%202022.pdf).
- `plants/IRENA_RPGC_2022.pdf`: https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf
- `plants/IRENA_RPGC_2024.pdf`: https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_TEC_RPGC_in_2024_2025.pdf
- `plants/IEA_WEO2023.pdf`: https://iea.blob.core.windows.net/assets/86ede39e-4436-42d7-ba2a-edf61467e070/WorldEnergyOutlook2023.pdf (lead only, not cited).
- `plants/ICE_PEG_2020-2035_mirror_vvalner.pdf`: https://vvalner.com/wp-content/uploads/2021/11/SGCR006-536.pdf
- `plants/NREL_ATB2024_v4.0.0_ATBe.csv`: https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2024/v4.0.0/ATBe.csv
- `plants/EIA_AEO2023_elec_cost_perf.pdf`: https://www.eia.gov/outlooks/aeo/assumptions/pdf/elec_cost_perf.pdf
- `plants/ElFinanciero_ICE_redirige_solar_eolica.html`: https://www.elfinancierocr.com/economia-y-politica/ice-redirige-su-mira-hacia-la-energia-solar-y/X65VM5IS2RDANG4SVXMZWYLI6E/story/ (lead only, not cited).
- `imports/ICE_CENCE_Informe_Anual_2024.pdf`: https://apps.grupoice.com/CenceWeb/documentos/3/3008/24/Informe%20Anual%202024.pdf
- `imports/CEPAL_Estadisticas_subsector_electrico_SICA_2024.pdf`: https://repositorio.cepal.org/server/api/core/bitstreams/0bbc262b-0653-4db6-b643-0f64a8eea6e8/content (lead only, not cited).
- `reused/`: 30 files copied from the LAC_LOCAL_PRICES downloads for the reused source ids (CR-001 to CR-020, CR-022, CR-023, GEN-001 to GEN-003, GEN-005, GEN-006, GEN-008, HON-016; the CR-024 copy of the IPCC chapter duplicates GEN-002). Origins are in `sources.csv`.
- `paper/`: read-only copies of `CLEWISE_MethodsX_v02.docx`, `CLEWISE_DataInBrief.docx`, `CLEWISE_JCLP_draft_v2.docx`, `Suplementary.xlsx` and `Data_v2.xlsx` from the OneDrive paper folder, plus their text extracts. Nothing in OneDrive was written, renamed or moved.
