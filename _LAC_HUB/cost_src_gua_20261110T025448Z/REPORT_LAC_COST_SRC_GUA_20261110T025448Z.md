# REPORT LAC_COST_SRC_GUA 20261110T025448Z

Sourced cost proposals for the Guatemala energy model (`Guatemala/GUA_ENERGY`). This job changes no model file; LAC_COST_WRITE reads `proposals.csv`.

- Pull request: not yet opened (draft)
- Branch: `job/cost-src-gua`, from `2ddd560`
- Commit: the single commit on the branch, message "LAC_COST_SRC_GUA: sourced cost proposals for Guatemala". Its hash is stated in the pull request description, since a file cannot hold the hash of its own commit.
- Stamp: 20261110T025448Z

## Gates

| Gate | Result |
|---|---|
| 1. Read-only | pass: `baseline_after.csv` equals `baseline_before.csv` (6 files, SHA-256) |
| 2. Diff scope | pending |
| 3. Tracked file types | pending |
| 4. Sourcing | pass: 2,212 non-ASSUMPTION proposal rows, 0 with a missing or unknown source id; 197 ASSUMPTION rows, 0 citing an unknown id; 112 sources, each with an http(s) URL, a locator, a retrieval date and a file present in `downloads/`, 0 problems; no local path or internal file in any source field |
| 5. ASSUMPTION rows | pass: 197 rows over 3 technologies (`DIST_NGS`, `IMP_ELE`, `PPPVDS`), each with leads in `search_log.csv`; 3 distinct sentences, 0 failing the word check |
| 6. Coverage | pass: 15 plants x 3 parameters x 33 years, 9 supply rows x 3 scenarios x 33 years, and `IMP_ELE` x 33 years; 2,409 cells, 0 gaps, 0 duplicate cells |
| 7. Text and log | pending |

Gate script: `scripts/s9_gates.py`; output in `work/gates_output.txt`.

## Fuel supply rows

All values are USD/GJ on a net calorific basis in real 2024 USD (CPI-U). Projections are P(y, s) = r x B(2024) x WEO_s(y) / WEO_s(2024), using WEO 2025 Table 2.3 (page 109, USD MER 2024; the table is 2.3, not 2.32).

Benchmarks:
- `DIST_COA`: World Bank Coal South African, with the WEO European Union steam coal price.
- `DIST_NGS`: EIA Henry Hub, with the WEO United States gas price.
- All other rows: EIA Brent, with the WEO IEA crude oil price.

r cases:
- Case 1: mean over the chosen point's own history.
- Case 2: mean over the import CIF history, times the 2024 ratio of the chosen point to import CIF.
- Case 3: the 2024 ratio alone.

The step is the change from 2025 (the last history year) to 2026 (the first projected year), not smoothed.

| Supply row | Chosen point | 2024 value (USD/GJ net, real 2024) | Current 2024 | r | r case | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | 2025 value (case) | Step 2025 to 2026 STEPS / CPS / NZE (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `DIST_COA` | import CIF | 5.6536 | 3.4478 | 0.050379 | case 1 | 4.4475 | 3.1409 | 3.9024 | 1.8560 | 4.5860 (observed) | 9.81 / 12.45 / 3.96 |
| `DIST_COK` | import CIF | 3.1954 | 0.0 | 0.04819 | case 1 | 3.9071 | 3.7329 | 5.2065 | 1.2279 | 3.1717 (observed) | 22.62 / 25.15 / 9.39 |
| `DIST_DSL` | wholesale import parity | 20.2962 | 20.4935 | 0.258852 | case 2 | 20.9867 | 20.0513 | 27.9662 | 6.5958 | 17.4382 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_FOI` | wholesale import parity | 14.8098 | 13.8373 | 0.17924 | case 2 | 14.5321 | 13.8844 | 19.3650 | 4.5672 | 12.0750 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_GSL` | wholesale import parity | 22.1109 | 25.0577 | 0.282458 | case 2 | 22.9005 | 21.8798 | 30.5166 | 7.1973 | 19.0284 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_KER` | final consumer pre-tax | 31.2593 | 0.0 | 0.402498 | case 1 | 32.6329 | 31.1784 | 43.4857 | 10.2561 | 27.1152 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_LPG` | wholesale import parity | 13.7735 | 29.4676 | 0.189189 | case 2 | 15.3387 | 14.6550 | 20.4399 | 4.8207 | 12.7452 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_NGS` | generator delivered | 8.6256 | 10.2397 | 3.93861 | case 3 | 12.2611 | 18.0353 | 19.6035 | 8.6256 | 13.5085 (history from ratio) | -27.18 / -24.01 / -36.67 |
| `EXTT_CRU` | export FOB | 9.2162 | empty | 0.130483 | case 1 | 10.5791 | 10.1075 | 14.0973 | 3.3248 | 8.4709 (observed) | 24.32 / 26.88 / 10.9 |

Notes:
- `DIST_KER` uses the MEM consumer price net of taxes. The Banguat import CIF of 51.23 USD/GJ covers 14.8 t in the year and was set aside.
- `DIST_NGS` is an ASSUMPTION: 7.763 USD/GJ gross, divided by 0.9.
- `EXTT_CRU` is new: Banguat crude export FOB, 389.85 USD/t in 2024.
- Every other published 2024 point is in `price_points_2024.csv`.

## Power plants (2024)

CapitalCost is in USD/kW (MUSD/GW), FixedCost in USD/kW-yr, and VariableCost in USD/GJ (MUSD/PJ).
- The current plant VariableCost values are in USD/kWh: the workbook unit label reads "M US$ / GWh". The proposals convert them (x277.78, or USD/MWh / 3.6).
- Plant costs are proposed as published, in each source's dollar year.
- Source ids (details in `sources.csv`):
  - NAT-001: MEM PEIG 2026-2050.
  - NAT-002: MEM PEG 2020-2050.
  - NAT-004: MEM PEIG 2022-2052.
  - INT-001 and INT-002: IRENA RPGC 2022 and 2024.
  - INT-003 to INT-008: NREL ATB 2024, 2023 and 2021.
  - INT-009: EIA 2020 capital cost study.
  - INT-010: EIA AEO2019.
  - INT-013: IEA WEO 2025 Annex B.

| Technology | CapitalCost current / proposed (USD/kW) | class | FixedCost current / proposed (USD/kW-yr) | class | VariableCost current / proposed (USD/GJ) | class | Sources |
|---|---|---|---|---|---|---|---|
| `PPBGS` | 5000 / 2600 | matched, newer edition | 7.11 / 7.11 | matched | 0.005 / 1.3889 | matched | INT-001, NAT-002, NAT-004 |
| `PPBIM` | 1929 / 1929 | matched | 77.16 / 77.16 | matched | 0.0096 / 1.1111 | replace | INT-001, INT-002, NAT-001 |
| `PPCOA` | 2562 / 2100 | replace | 61.4 / 31.6 | replace | 0.0064 / 1.6667 | replace | INT-013, NAT-002 |
| `PPDSL` | 448 / 1400 | replace | 31.6 / 20 | replace | 0.006 / 1.3889 | replace | NAT-001 |
| `PPFOI` | 1908 / 1400 | replace | 35.16 / 35.16 | matched | 0.0057 / 1.5806 | matched | INT-009, NAT-001 |
| `PPGEO` | 3900 / 4015 | replace | 150.6 / 150.6 | matched | 0 / 1.3889 | replace | INT-001, INT-002, NAT-001 |
| `PPHDAM` | 2619 / 3500 | matched, newer edition | 33.54 / 50 | replace | 0 / 0 | matched | INT-001, INT-009, NAT-001, NAT-002, NAT-004 |
| `PPHROR` | 1870 / 3444 | replace | 54 / 34 | matched, newer edition | 0 / 0 | matched | INT-001, INT-002, INT-009, NAT-001, NAT-002, NAT-004 |
| `PPNGS` | 1156 / 1000 | replace | 12.12 / 12.12 | matched | 0.0045 / 1.3889 | replace | INT-013, NAT-001 |
| `PPPVD` | 1789.62 / 1794.74 | matched, newer edition | 18.081 / 18.387 | matched, newer edition | 0 / 0 | matched | INT-003, INT-004, INT-005, INT-006, INT-009 |
| `PPPVDS` | 2959.45 / 2841.53 | ASSUMPTION | 33.944 / 52.303 | ASSUMPTION | 0 / 0 | matched | INT-003, INT-004, INT-009 |
| `PPPVT` | 949 / 1375 | replace | 20.23 / 20.23 | matched | 0 / 0 | matched | INT-001, INT-002, INT-009, NAT-001 |
| `PPPVT2` | 1289.51 / 1551.27 | matched, newer edition | 20.988 / 21.609 | matched, newer edition | 0 / 0 | matched | INT-003, INT-004, INT-005, INT-006, INT-009 |
| `PPPVTS` | 2130.08 / 2456.06 | matched, newer edition | 58.635 / 61.468 | matched, newer edition | 0 / 0 | matched | INT-003, INT-004, INT-005, INT-006, INT-009 |
| `PPWNDON` | 1518 / 1600 | matched, newer edition | 28.08 / 28.08 | matched | 0 / 0 | matched | INT-009, INT-010, NAT-001, NAT-002 |

The PV paths (`PPPVT2`, `PPPVTS`, `PPPVD`) match NREL ATB 2023 Moderate (Market case) for 2024 to 2050. ATB 2024 is proposed for 2022 to 2050 as the newer edition. Proposed capital costs in 2050:
- `PPPVT2`: 682.9 USD/kW.
- `PPPVTS`: 1153.9 USD/kW.
- `PPPVD`: 929.2 USD/kW.
- `PPPVDS`: 1570.1 USD/kW (ASSUMPTION).

P2 classes over all 1,485 plant cells, by change class:
- `matched`: 543 keep and 66 unit fix.
- `matched, newer edition`: 306 upgrade.
- `replace`: 504.
- `ASSUMPTION`: 66.

## Electricity imports

`IMP_ELE` VariableCost is 0 today. The proposal is 17.2278 USD/GJ (62.02 USD/MWh, real 2024 USD) in every year:
- 2024 is `observed`; all other years are `ASSUMPTION`.
- The price is the 2024 import price volume-weighted from the AMM monthly market analyses: Mexico 55.75 USD/MWh on 1,623.39 GWh, and the regional market MER 121.68 USD/MWh on 170.57 GWh. The total, 1,793.96 GWh, equals the AMM Informe Estadistico 2024 annual import of 1,793.97 GWh.
- Check: the customs unit value is about 78.6 USD/MWh (UN Comtrade, Mexico exports to Guatemala), the top of the range.
- No published projection exists, so the price is held flat.
- FixedCost stays 0 and CapitalCost stays empty.

## Country task

- Current values confirmed: every section 5 value of the brief was recomputed from the BAU compiled CSVs and matches (`scripts/s3_bau_2024_check.csv`).
- Unit slip: fixed, with the evidence recorded.
  - The workbook's plant VariableCost unit label is "M US$ / GWh".
  - Data in Brief Table 57 prints "M USD/GWh".
  - Every source behind these values gives variable O&M in USD/MWh: PEG 2020-2050 biogas 5 and coal 6; EIA 2020 engines 5.69; IRENA bioenergy 0.005 USD/kWh. So the model values are USD/kWh, and the proposals divide USD/MWh by 3.6.
  - `PPBGS` and `PPFOI` match their sources exactly after the conversion.
- `PPDSL` CapitalCost 448: no source gives this value.
  - Its fixed (31.6) and variable (6 USD/MWh) costs equal the coal candidate of the MEM PEG 2020-2050.
  - Proposed: the MEM PEIG 2026-2050 internal combustion engine values, 1400 USD/kW, 20 USD/kW-yr and 5 USD/MWh.
- `DIST_COK` and `DIST_KER` are priced: 3.1954 and 31.2593 USD/GJ in 2024.
- `DIST_KER` import CIF check: the 51.23 USD/GJ Banguat line is a 14.8 t sample, so the next F2 point was used.
- `DIST_NGS`: ASSUMPTION at 7.763 USD/GJ gross, 8.626 USD/GJ net.
- `IMP_ELE`: priced (see above).
- `EXTT_CRU`: priced from Banguat crude export FOB.

## ASSUMPTION rows

197 rows in total:
- `DIST_NGS` VariableCost: 99 (33 years x 3 scenarios).
- `IMP_ELE` VariableCost: 32 (all years except 2024).
- `PPPVDS` CapitalCost: 33.
- `PPPVDS` FixedCost: 33.

The leads for each are listed in GAPS section 2.

## Paper trail

`paper_trace.csv` holds 84 statements. All five files opened from read-only copies.

| Document | Statements | Need a change | What changes |
|---|---|---|---|
| CLEWISE_DataInBrief.docx | 41 | 35 | Table 57: each value gets a source and dollar year, plant variable costs are relabelled to M USD/PJ after the x277.78 fix, and the new fuel prices go in, plus rows for electricity imports, kerosene, petroleum coke and crude. Section 4.8 and the specifications table: "current USD without deflation" becomes real 2024 USD for fuel prices and the source dollar year for plant costs, and the sources are named. The reference list adds WEO 2025 and IRENA 2024 and cites them by number. |
| Suplementary.xlsx | 27 | 22 | Sheet `Costos_GUA` mirrors Table 57 and changes with it, row by row. |
| CLEWISE_JCLP_draft_v2.docx | 7 | 6 | The cost basis sentence (and the missing discount rate); Guatemala result statements re-checked after a re-run; references added. |
| CLEWISE_MethodsX_v02.docx | 6 | 5 | Step 1 inputs and processing add fuel prices and technology costs; WEO 2025 CPS and NZE become fuel price sensitivities. |
| Data_v2.xlsx | 3 | 2 | Guatemala cost results and the fuel import expenditure rows are regenerated after a re-run. |

The papers cite IRENA Renewable Power Generation Costs in 2022 and IEA WEO 2023 only generically, with no technology-level source. Table 57 has no source column. Its diesel, gasoline and LPG prices equal the Dominican Republic values in Table 53.
