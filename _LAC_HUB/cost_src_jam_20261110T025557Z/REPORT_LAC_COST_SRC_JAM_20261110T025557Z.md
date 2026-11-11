# REPORT: LAC_COST_SRC_JAM 20261110T025557Z

Sourced cost proposals for the Jamaica energy model.

- Pull request: luviga/clewise-lac#2 (draft), https://github.com/luviga/clewise-lac/pull/2
- Branch: `job/cost-src-jam`, from `2ddd560`
- Commit: the single commit on the branch, "LAC_COST_SRC_JAM: sourced cost proposals for Jamaica". Its hash is shown by `git log -1 job/cost-src-jam` and in the pull request; a file cannot hold the hash of the commit that adds it.

## Gates

| Gate | Result |
|---|---|
| 1 Read-only | PASS: 6 model files, SHA-256 equal before and after |
| 2 Diff scope | PASS: `git diff --name-only 2ddd560 HEAD` lists 37 files, all inside `_LAC_HUB/cost_src_jam_20261110T025557Z/` |
| 3 Tracked file types | PASS: 37 tracked files, all `.md`, `.csv`, `.py` or `.txt`; none under `downloads/` |
| 4 Sourcing | PASS: 2,234 of 2,234 proposal rows with a basis other than ASSUMPTION cite only ids in `sources.csv`; 37 of 37 sources have an http(s) URL, a page or table locator, a retrieval date and every listed file present in `downloads/`; no local path or internal file in any source field |
| 5 ASSUMPTION rows | PASS: 286 rows over 6 technologies (`DIST_KER`, `DIST_JET`, `PPPVDS`, `PPWNDONS`, `PPHDAM`, `PPGEO`); all have leads in `search_log.csv`; all sentences pass the wording check. 595 rows carry a sentence (the 286 plus the gas sentence on every `DIST_NGS` row and the kerosene and jet sentence on their later rows) |
| 6 Coverage | PASS: 13 plants x 3 parameters and 11 supply rows x 3 scenarios, every year 2021 to 2055 |
| 7 Format | PASS: `git diff --check` clean; no em dash and no machine path in any output file (the copied brief excepted); `git log -3 --format=%B` has no Co-Authored-By and no Generated with line |

## Fuel supply rows

USD/GJ (MUSD/PJ), net calorific basis, real 2024 USD. Current = A-O workbook 2024 value. r is the mean ratio of the chosen point to its benchmark over the years shown (both real 2024 USD). Benchmarks: Brent with the WEO crude oil price for oil products and crude; Henry Hub with the WEO United States gas price for natural gas (US LNG, EIA); Richards Bay coal with the WEO European Union steam coal price for coal, petroleum coke and `DIST_OPE`.

| Supply row | Chosen 2024 point | 2024 proposed | 2024 current | r (case) | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join |
|---|---|---|---|---|---|---|---|---|---|
| `DIST_COA` | import CIF | 5.747 | 1.514 | 0.844 (history 2018, 2019, 2020, 2021, 2022, 2024) | 2.97 | 2.10 | 2.60 | 1.24 | 2024 to 2025: -39.8% |
| `DIST_COK` | import CIF | 3.087 | 4.872 | 1.182 (history 2020, 2022, 2023, 2024, 2025) | 4.16 | 2.93 | 3.65 | 1.73 | 2025 to 2026: +23.3% |
| `DIST_DSL` | generator delivered, excluding SCT | 19.948 | 19.820 | 1.432 (2024 ratio only) | 20.09 | 19.19 | 26.77 | 6.31 | 2024 to 2025: +0.1% |
| `DIST_FOI` | import CIF | 13.262 | 13.488 | 0.815 (history 2018 to 2025) | 11.43 | 10.92 | 15.23 | 3.59 | 2025 to 2026: -0.4% |
| `DIST_GSL` | import CIF | 17.140 | 19.299 | 1.270 (history 2018 to 2025) | 17.82 | 17.03 | 23.75 | 5.60 | 2025 to 2026: +18.3% |
| `DIST_JET` | wholesale import parity, pre-tax (ASSUMPTION) | 18.000 | 13.492 | 1.292 (2024 ratio only) | 18.12 | 17.32 | 24.15 | 5.70 | 2024 to 2025: +0.1% |
| `DIST_KER` | wholesale import parity, pre-tax (ASSUMPTION) | 18.000 | 13.492 | 1.556 (history 2018, 2019) | 21.83 | 20.86 | 29.09 | 6.86 | 2024 to 2025: +20.6% |
| `DIST_LPG` | import CIF | 9.019 | 21.259 | 0.761 (history 2018 to 2025) | 10.67 | 10.20 | 14.22 | 3.35 | 2025 to 2026: +19.5% |
| `DIST_NGS` | import CIF (LNG) | 13.923 | 7.080 | 4.045 (history 2018 to 2024) | 13.26 | 19.51 | 21.20 | 9.33 | 2024 to 2025: -28.3% |
| `DIST_OPE` | import CIF (petroleum coke, same commodity as `DIST_COK`) | 3.087 | 0.000 | 1.182 (history 2020, 2022 to 2025) | 4.16 | 2.93 | 3.65 | 1.73 | 2025 to 2026: +23.3% |
| `EXTT_CRU` | import CIF (MSET crude import value) | 14.006 | 0.000 | 1.024 (history 2018 to 2025) | 14.37 | 13.73 | 19.15 | 4.52 | 2025 to 2026: +18.4% |

Notes. Petrojam weekly prices were parsed (52 weeks of 2024, no gap) and turned out to be the tax-inclusive refinery billing prices, so diesel and gasoline fall back as the brief says. Diesel import CIF (HS 271019) mixes products, so the closest pre-tax diesel point was used (GAPS 1.2). The 2025 Comtrade coal and LNG records are excluded as outliers. The CPS series is above STEPS and NZE below it for every row. Every other published 2024 point is in `price_points_2024.csv`.

## Power plants

2024 values. CapitalCost USD/kW; FixedCost USD/kW-yr; VariableCost USD/GJ (non-fuel O&M). Classes are those of rule P2. Values stay in the currency year of their source (GAPS 1.14).

| Plant | Cap current | Cap proposed | Fixed current | Fixed proposed | Var current | Var proposed | Class (Cap / Fixed / Var) | Source (Cap / Fixed / Var) |
|---|---|---|---|---|---|---|---|---|
| `PPBGS` | 5,391.00 | 2,015.84 | 157.00 | 163.67 | 1.40 | 1.11 | replace / replace / matched, newer edition | IRENA 2022 with ATB path / NREL ATB 2024 / IRENA 2022 and IRENA 2025 |
| `PPBIM` | 5,391.00 | 2,015.84 | 157.00 | 163.67 | 1.40 | 1.11 | replace / replace / matched, newer edition | IRENA 2022 with ATB path / NREL ATB 2024 / IRENA 2022 and IRENA 2025 |
| `PPDSL` | 5,391.00 | 800.00 | 2.99 | 12.00 | 0.90 | 0.28 | replace / replace / replace | 2018 IRP (combustion turbine) |
| `PPFOI` | 5,391.00 | 1,400.00 | 2.99 | 36.00 | 6.34 | 1.81 | replace / matched (unit fix) / replace | 2018 IRP (medium speed diesel, HFO) |
| `PPGEO` | 6,750.07 | 6,471.59 | 113.62 | 128.73 | empty | 0.00 | replace in 2024, matched in 2021 to 2023 / matched, newer edition / ASSUMPTION | NREL ATB 2024 HydroFlash (2021 USD) / IRENA 2022 and IRENA 2025 with ATB path / ATB and IRENA |
| `PPHDAM` | 3,007.71 | 3,007.71 | 85.00 | 85.00 | empty | 0.00 | matched / matched / ASSUMPTION | NREL ATB 2024 NPD1 (2021 USD) / same / ATB and IRP |
| `PPHROR` | 7,436.08 | 7,436.08 | 120.00 | 120.00 | empty | 0.00 | matched / matched / replace (fill) | NREL ATB 2024 NSD3 / 2018 IRP / 2018 IRP |
| `PPNGS` | 1,300.00 | 1,300.00 | 22.77 | 14.40 | 1.15 | 0.72 | matched / replace / replace | OUR GEP 2010 / 2018 IRP / 2018 IRP |
| `PPPVD` | 2,736.31 | 2,600.58 | 29.11 | 29.11 | empty | 0.00 | replace / matched / replace (fill) | NREL ATB 2024 ResPV / same / 2018 IRP |
| `PPPVDS` | 3,824.22 | 3,353.43 | 68.95 | 75.04 | empty | 0.00 | ASSUMPTION | PPPVD plus IRP battery with ATB battery path |
| `PPPVT` | 1,348.64 | 1,348.64 | 31.20 | 31.20 | empty | 0.00 | matched / matched / replace (fill) | 2018 IRP with ATB path / 2018 IRP / 2018 IRP |
| `PPWNDON` | 1,772.59 | 1,772.59 | 36.00 | 36.00 | 0.69 | 0.69 | matched / matched / matched | NREL ATB 2024 Class 9 (2021: 2018 IRP) / 2018 IRP / 2018 IRP |
| `PPWNDONS` | 3,733.29 | 2,525.44 | 82.58 | 81.93 | empty | 0.69 | ASSUMPTION | PPWNDON plus IRP battery with ATB battery path |

Years other than 2024 follow each source's path; `proposals_summary.csv` gives 2024, 2030 and 2050. Over all plant cells (35 years x 39 rows): 310 keep, 105 upgrade, 35 unit fix, 245 fill empty, 670 replace.

## Electricity imports

The Jamaica model has no electricity import technology. Step 6 was skipped.

## Country task

- Petrojam pages: all 10 parsed; 2024 is complete (52 weeks). The 2024 means equal MSET's refinery billing prices, which include SCT, so they were not used as the pre-tax point. They are recorded as price points, and they do not replace the kerosene and jet ASSUMPTION.
- `EXTT_CRU` priced from the MSET crude import value: 80.94 USD/bbl in 2024, 14.006 USD/GJ. History 2018 to 2025 is from MSET Table 1.
- `DIST_OPE` priced as petroleum coke, the same commodity as `DIST_COK`.
- `DIST_COA` priced. The A-O workbook holds 1.514 in Flat mode, not an empty value.
- Geothermal: one academic resource estimate exists (94.8 MWe, low-enthalpy); it is recorded as a known-limitation candidate.
- Section 5 check against the A-O workbook. All plant and supply 2024 values agree with section 5, with three exceptions:
  - `DIST_COA` holds 1.514, not empty.
  - `PPFOI` residual capacity is 0.0765 GW in 2025, 0.0795 GW in 2026 and 0 from 2027, not 0 from 2030.
  - `PPPVDS` residual capacity has no unit.

## ASSUMPTION rows

286 rows over 6 technologies:
- `DIST_KER` and `DIST_JET` 2024: 6 rows (3 scenarios each).
- `PPPVDS` and `PPWNDONS`: 210 rows (3 parameters x 35 years each).
- `PPHDAM` and `PPGEO` VariableCost at 0: 70 rows.

Leads for each are in `search_log.csv` and GAPS section 2.

## Paper trail

61 statements in `paper_trace.csv`:

| Document | Statements | What changes if the proposals are applied |
|---|---|---|
| CLEWISE_DataInBrief.docx | 51 | Table 67 (42 cells): every fuel row and every replaced plant cost needs its 2024 value and a source. The section 4.8 text needs to name the source per cost and the currency basis (fuel in real 2024 USD, pre-tax). The data collection list needs the new sources. Reference [13] is cited for the Jamaica IRP but is IRENA in the list. Rows for crude and other petroleum products need to be added. |
| CLEWISE_MethodsX_v02.docx | 2 | The energy template needs to say that fuel enters through supply rows at pre-tax import parity with WEO 2025 scenarios. Fuel price sensitivity (CPS, NZE) can be mentioned. |
| CLEWISE_JCLP_draft_v2.docx | 6 | State the fuel cost basis of the least-cost model. Re-run, then re-check the Jamaica results for CAPEX, OPEX, accumulated investment and fuel import exposure. |
| Suplementary.xlsx | 1 | Sheet Costos_JAM L1:Q36 changes with Table 67. |
| Data_v2.xlsx | 1 | Sheet 15. Jamaica_Costos is recomputed from the re-run model. |
