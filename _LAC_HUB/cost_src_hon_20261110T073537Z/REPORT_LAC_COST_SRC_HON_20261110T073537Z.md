# REPORT: LAC_COST_SRC_HON 20261110T073537Z

Sourced cost proposals for the Honduras energy model. No model file changed.

- Pull request: luviga/clewise-lac#3 (draft), https://github.com/luviga/clewise-lac/pull/3
- Branch: `job/cost-src-hon`, from `2ddd560`
- Commit: the single commit on the branch, "LAC_COST_SRC_HON: sourced cost proposals for Honduras". A file cannot hold the hash of the commit that adds it; `git log -1 job/cost-src-hon` and the pull request show it.

## Gates

| Gate | Result |
|---|---|
| 1 Read-only | PASS: 6 model files, SHA-256 equal before and after (`baseline_before.csv`, `baseline_after.csv`) |
| 2 Diff scope | PASS: `git diff --name-only 2ddd560 HEAD` lists 39 files, all inside `_LAC_HUB/cost_src_hon_20261110T073537Z/` |
| 3 Tracked file types | PASS: 39 tracked files in the job folder, all `.md`, `.csv`, `.py` or `.txt`; `git ls-files` shows nothing under `downloads/` |
| 4 Sourcing | PASS: 1,990 of 1,990 proposal rows with a basis other than ASSUMPTION cite only ids in `sources.csv`; 81 of 81 sources have an http(s) URL, a page or table locator, a retrieval date and every listed file present in `downloads/`; no local path or internal file in any source field |
| 5 ASSUMPTION rows | PASS: 4 rows, 1 technology (`IMP_ELE` VariableCost 2018 to 2021); leads in `search_log.csv`; the sentence passes the wording check. 103 rows carry a sentence (the 4, plus the natural gas sentence of rule F5 on all 99 `DIST_NGS` rows) |
| 6 Coverage | PASS: 12 plants x 3 parameters x 33 years (2018 to 2050); 8 supply rows x 3 scenarios x 33 years; `IMP_ELE` VariableCost and FixedCost for the 7 years with a positive activity lower limit (2018 to 2024); no duplicate keys |
| 7 Format | PASS: `git diff --check` clean; no em dash and no machine path in any output file (the copied brief excepted); `git log -3 --format=%B` has no Co-Authored-By and no Generated with line |

`proposals.csv` has 1,994 rows. Basis: observed 69, history from ratio 105, projected 621, matched 408, matched newer edition 648, replace 139, ASSUMPTION 4. Change class: keep 342, upgrade 648, replace 938, fill_empty 66.

## Fuel supply rows

USD/GJ (MUSD/PJ), net calorific basis, real 2024 USD. Current = BAU 2024 value. r is the mean ratio of the chosen point (or of import CIF, case 2) to its benchmark, both real 2024 USD. Benchmarks: Brent with the WEO crude oil price for oil products; Henry Hub with the WEO United States gas price for natural gas (ODS LNG chain indexed to Henry Hub); World Bank South African coal with the WEO European Union steam coal price for coal and petroleum coke (Colombian coal origin). WEO 2025 Table 2.3, PDF page 109.

| Supply row | Chosen 2024 point | 2024 proposed | 2024 current | r (case) | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join |
|---|---|---|---|---|---|---|---|---|---|
| `DIST_COA` | import CIF (Comtrade) | 5.194 | 3.448 | 1.194 (history 2019, 2020, 2021, 2023, 2024) | 4.195 | 2.963 | 3.681 | 1.751 | 2024 to 2025: -5.9% |
| `DIST_COK` | import CIF (Comtrade) | 2.509 | 4.921 | 0.687 (history 2018 to 2024) | 2.415 | 1.706 | 2.119 | 1.008 | 2024 to 2025: +12.2% |
| `DIST_DSL` | wholesale import parity, pre-tax | 18.825 | 26.477 | 1.404 (import CIF history 2021 to 2025 x 2024 ratio 1.065) | 19.698 | 18.820 | 26.249 | 6.191 | 2024 to 2025: +4.0% |
| `DIST_FOI` | import CIF (BCH) | 12.510 | 15.064 | 0.869 (history 2021 to 2025) | 12.185 | 11.642 | 16.237 | 3.829 | 2025 to 2026: +11.3% |
| `DIST_GSL` | wholesale import parity, pre-tax | 21.562 | 26.878 | 1.615 (import CIF history 2021 to 2025 x 2024 ratio 1.133) | 22.664 | 21.654 | 30.201 | 7.123 | 2024 to 2025: +4.5% |
| `DIST_KER` | wholesale import parity, pre-tax | 20.206 | 26.493 | 1.475 (import CIF history 2021 to 2025 x 2024 ratio 1.071) | 20.698 | 19.776 | 27.582 | 6.505 | 2024 to 2025: +1.8% |
| `DIST_LPG` | wholesale import parity, pre-tax (CCHAC) | 11.748 | 17.896 | 0.912 (import CIF history 2021 to 2025 x 2024 ratio 0.931) | 12.790 | 12.220 | 17.044 | 4.020 | 2024 to 2025: +8.2% |
| `DIST_NGS` | generator delivered (ODS LNG chain), 5.515 gross / 0.9 | 6.128 | 10.240 | 2.657 (2024 ratio only) | 8.711 | 12.813 | 13.927 | 6.128 | 2024 to 2025: +7.0% |

CPS is above STEPS and NZE below it for every row from 2026. Every other published 2024 point (generator delivered, final consumer pre-tax, second import CIF) is in `price_points_2024.csv` with its difference to the chosen point. History years without an observation of the chosen point use r times the benchmark of that year (GAPS 1.4).

## Power plants

2024 values. CapitalCost USD/kW; FixedCost USD/kW-yr; VariableCost USD/GJ (non-fuel O&M; x 3.6 = USD/MWh). Matched values are the ODS/CND PIEG 2024-2033 Tabla 7 (2023 USD) and its Anexos Tablas B-2 and B-3; upgrades are the PIEG 2026-2035 Tabla 19 (2024 USD), applied from 2024, with NREL ATB 2024 Moderate paths for PV, wind and hybrids. 2018 to 2023 keep the current values wherever they are matched.

| Plant | Cap current | Cap proposed | Fixed current | Fixed proposed | Var current | Var proposed | Class (Cap / Fixed / Var) | Source |
|---|---|---|---|---|---|---|---|---|
| `PPBIM` | 4,851.00 | 2,012.82 | 157.00 | 163.67 | 0.0800 | 1.3889 | replace / replace / replace | IRENA 2022 with ATB 2024 Biopower path / ATB 2024 / IRENA 2022 |
| `PPCOK` | 4,769.52 | 4,769.52 | 45.68 | 45.68 | 1.4056 | 1.4056 | matched (all) | ODS 2024-2033 Tabla 7, Carbon 30 MW |
| `PPFOI` | 984.08 | 1,269.20 | 39.57 | 14.00 | 1.7778 | 1.9444 | matched, newer edition (all) | ODS Tabla 7 bunker engine 100 MW; Tabla 19 dual engine 100 MW |
| `PPGEO` | 5,900.00 | 6,179.24 | 153.98 | 160.66 | 0.3639 | 0.4167 | matched, newer edition (all) | ODS Tabla 7 and Tabla 19, geothermal |
| `PPGTDSL` | 1,204.83 | 1,437.59 | 13.73 | 16.00 | 0.5833 | 0.9722 | matched, newer edition (all) | ODS Tabla 7 and Tabla 19, combined cycle row |
| `PPGTGLP` | 1,204.83 | 1,437.59 | 18.35 | 20.00 | 1.4694 | 1.6667 | matched, newer edition (all) | ODS combined cycle row (capital); LPG row to open-cycle GT 30 MW (O&M) |
| `PPHDAM` | 3,576.00 | 5,100.00 | 47.06 | 37.93 | empty | 0.0000 | matched, newer edition / same / matched (fill) | ODS Tabla 7 and Tabla 19, reservoir hydro >100 MW |
| `PPHROR` | 2,000.00 | 3,786.50 | 47.06 | 40.00 | empty | 0.0000 | matched, newer edition / same / matched (fill) | ODS Tabla 7 and Tabla 19, run-of-river <10 MW |
| `PPICEDSL` | 966.72 | 1,269.20 | 39.57 | 14.00 | 1.7778 | 1.3889 | matched, newer edition (all) | ODS Tabla 7 diesel engine 80 MW; Tabla 19 dual engine 100 MW |
| `PPPVD` | 871.80 | 1,138.48 | 22.74 | 29.53 | 0.0000 | 0.0000 | matched, newer edition / replace / matched | ODS Tabla 7 and Tabla 19 solar FV with ATB UtilityPV path / ATB 2024 ResPV / ODS |
| `PPPVT` | 1,139.23 | 1,434.72 | 25.36 | 40.31 | 0.0000 | 0.0000 | matched, newer edition / same / matched | ODS Tabla 7, Tabla B-2 and Tabla 19 PV-plus-battery 50 MW with ATB PV-Plus-Battery path |
| `PPWNDON` | 1,597.70 | 1,868.76 | 36.27 | 41.14 | 0.0000 | 0.0000 | matched, newer edition / same / matched | ODS Tabla 7, Tabla B-3 and Tabla 19 wind-plus-battery 50 MW with ATB LandbasedWind path |

2030 and 2050 values are in `proposals_summary.csv`. Over all plant cells (12 plants x 3 parameters x 33 years = 1,188): keep 342, upgrade 648, replace 132, fill_empty 66. IRENA 2022 and IEA WEO 2023 give none of the current numbers; the ODS plans give all except bioenergy and the distributed PV fixed O&M path.

## Electricity imports

`IMP_ELE` carries the price in both VariableCost and FixedCost (500 in 2018 to 559.8 in 2024, MUSD/PJ). The proposal moves the price to VariableCost and sets FixedCost to 0 for 2018 to 2024.

| Year | Basis | USD/MWh nominal | USD/GJ, real 2024 | Source |
|---|---|---|---|---|
| 2024 | observed | 114.56 (17,401,336 USD / 151.90 GWh) | 31.82 | CREE tariff reports, MER rows, 12 months |
| 2023 | observed | 130.31 | 37.27 | same |
| 2022 | observed | 114.90 | 34.21 | same |
| 2018 to 2021 | ASSUMPTION | | 31.82 | 2024 price held |

The price is ENEE's contract and spot purchases in the regional market, capacity charges included. CRIE reports 158.80 GWh of Honduras withdrawals in 2024, matching the model's 0.571 PJ. The 99999 years (2025 to 2050) are not proposed and stay as they are (GAPS 1.26).

## Country task

- Section 5 facts recomputed from the BAU CSVs (`section5_check.csv`): all plant and supply values and residual capacities agree with the brief. One difference: `IMP_ELE` VariableCost and FixedCost are 99999 from 2025, not from 2030.
- The ODS Plan Indicativo 2026-2035 (HON-016) was used first for plant costs: it gives the newer edition of every matched row except coal and bioenergy. The matching values themselves come from the earlier edition, PIEG 2024-2033 (HON-018).
- `PPCOK`: only FixedCost and VariableCost matter; both are matched and kept.
- `DIST_NGS`: the ODS LNG chain 5.515 USD/GJ gross, divided by 0.9 (6.128 net), Henry Hub indexed per HON-016 section 5.3.5.
- `IMP_ELE`: priced as above; FixedCost proposed at 0 because both parameters carry the price.

## ASSUMPTION rows

4 rows: `IMP_ELE` VariableCost 2018, 2019, 2020 and 2021 (31.82 USD/GJ). No plant or fuel value is an ASSUMPTION; the natural gas sentence of rule F5 rides on every `DIST_NGS` row as required.

## Paper trail

44 statements in `paper_trace.csv`.

| Document | Statements | What changes if the proposals are applied |
|---|---|---|
| CLEWISE_DataInBrief.docx | 33 | Table 62 (21 Honduras rows in scope): each fuel row, plant cost and the import row needs its new value and source; the caption needs the currency basis. Section 4.8 (and its duplicate in the appendix) needs to name the ODS plans, ATB 2024 and IRENA 2022 for Honduras, and the fuel price basis (pre-tax, real 2024 USD, WEO 2025 scenarios). The data collection line and the reference list need the new sources; [14] (WEO 2023) no longer sources any Honduras value. The PPBIM variable cost label (M USD/GWh) is a unit slip. |
| CLEWISE_MethodsX_v02.docx | 3 | The energy template text needs the supply-row fuel price basis; fuel price sensitivity (CPS, NZE) becomes available; a Honduras worked example would carry the new inputs. |
| CLEWISE_JCLP_draft_v2.docx | 6 | State the cost basis of the least-cost run; after a re-run, re-check the Honduras CAPEX, OPEX, accumulated investment and Fuel-Import Exposure statements. |
| Suplementary.xlsx | 1 | Sheet Costos_HON E1:K38 changes with Table 62. |
| Data_v2.xlsx | 1 | Sheet 11.Honduras_Costos is recomputed from the re-run model. |
