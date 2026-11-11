# REPORT LAC_COST_SRC_DR 20261110T025405Z

Sourced cost proposals for the Dominican Republic energy model (`DominicanRepublic/RD_ENERGY`). No model file changed; `proposals.csv` is the file LAC_COST_WRITE reads.

- Pull request: draft, opened on `luviga/clewise-lac` from branch `job/cost-src-dr` after the commit; its number and URL are given in the pull request list of that branch (they cannot be written inside the single commit the brief allows).
- Branch: `job/cost-src-dr`, from `2ddd560`.
- Commit: the single commit "LAC_COST_SRC_DR: sourced cost proposals for Dominican Republic" on that branch, which adds this folder (a commit cannot hold its own hash).
- Brief: `BRIEF_LAC_COST_SRC_DR.md` (copied verbatim).

## Gate results

| Gate | Result |
|---|---|
| Gate 1 read-only | PASS - 6 files, hashes equal: True |
| Gate 4a proposals cite existing sources | PASS - 3168 rows, 0 rows with a missing or unknown source id; 82 distinct ids cited |
| Gate 4b source records complete | PASS - 135 sources; 0 problems |
| Gate 5 ASSUMPTION rows | PASS - 0 rows with basis ASSUMPTION; 81 rows carry an ASSUMPTION sentence (DIST_NGS), 1 distinct sentences; leads missing for []; sentences with banned words 0 |
| Gate 6 coverage | PASS - 23 plants x 3 parameters x 33 years; 9 supply rows x 3 scenarios x 33 years; EXTT_CRU, EXTT_NGS, PRO_COA and IMP_ELE exempt by the country notes; gaps: [] |
| Gate 7a no em dash, no machine path | PASS - files with em dash: []; files with a machine path: [] |
| Gates 2, 3, 7b, 7c (after the commit) | run after the commit with `gates.py post`; results are in `gate_results_post.txt` on the branch working copy and in the pull request body |

Sourcing check script: `gates.py` (gate 4 counts above). Proposals rows: 3168; basis classes replace 1323, matched 867, projected 675, history from ratio 123, observed 93, matched, newer edition 87; change classes fill_empty 1623, replace 1287, keep 189, upgrade 63, fill_placeholder 6.

## Fuel supply rows

Source: `fuel_summary.csv`, `fuel_prices.csv`. USD/GJ, net calorific basis, real 2024 USD. Current = BAU compiled 2024 VariableCost. Step at the join = STEPS 2026 over 2025, in percent (not smoothed).

| Row | Chosen point | 2024 value | Current 2024 | r | r case | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join |
|---|---|---|---|---|---|---|---|---|---|---|
| `DIST_COA` | import CIF | 3.975 | 9.605 | 1.1042 | multi-year average (2019,2022,2023,2024,2025) | 3.880 | 2.740 | 3.405 | 1.619 | 14.1% |
| `DIST_COK` | import CIF | 2.622 | 4.945 | 0.2642 | multi-year average (2019,2021,2022,2023,2024,2025) | 3.707 | 3.542 | 4.940 | 1.165 | 35.2% |
| `DIST_CRU` | import CIF | 15.299 | 14.940 | 1.0982 | multi-year average (2019,2022,2023,2024,2025) | 15.408 | 14.722 | 20.533 | 4.843 | 19.6% |
| `DIST_DSL` | wholesale import parity | 17.907 | 20.494 | 1.2852 | 2024 ratio alone (no history) | 18.031 | 17.227 | 24.028 | 5.667 | 19.8% |
| `DIST_FOI` | wholesale import parity | 13.352 | 13.626 | 0.9582 | 2024 ratio alone (no history) | 13.444 | 12.845 | 17.916 | 4.225 | 19.8% |
| `DIST_GSL` | import CIF | 19.614 | 25.058 | 1.4076 | 2024 ratio alone (no history) | 19.749 | 18.869 | 26.317 | 6.207 | 19.8% |
| `DIST_KER` | wholesale import parity | 19.889 | 0.000 | 1.4274 | 2024 ratio alone (no history) | 20.026 | 19.134 | 26.686 | 6.294 | 19.8% |
| `DIST_LPG` | import CIF | 11.041 | 29.468 | 0.7946 | multi-year average (2019,2022,2023,2024,2025) | 11.148 | 10.652 | 14.856 | 3.504 | 4.2% |
| `DIST_NGS` | import CIF | 8.936 | 7.646 | 2.6819 | multi-year average (2019,2021,2022,2023,2024,2025) | 8.793 | 12.933 | 14.058 | 6.186 | -30.0% |

Benchmarks: crude and oil products against EIA Brent (RBRTE) with the WEO 2025 IEA crude oil price; natural gas against Henry Hub (RNGWHHD, converted to net with 0.9) with the WEO 2025 United States gas price, because US exports of LNG to the DR in 2024 (90,594 MMcf, EIA) equal about all DR LNG imports (1,842,142 t, about 89,798 MMcf gross, UN Comtrade) and the TotalEnergies supply agreement of April 2025 is indexed to Henry Hub; coal against the World Bank Coal South African series with the WEO 2025 European Union steam coal price, because the DR coal reference is Platts FOB Puerto Bolivar (Colombia), an Atlantic-basin export price (MEM Boletin 2024). WEO 2025 fuel prices are in Table 2.3 on page 109 (not Table 2.32), USD (MER, 2024), years 2024, 2035 and 2050, linearly interpolated and flat after 2050 (the model ends in 2050). WEO 2025 was written before the 2026 Middle East energy crisis.

`EXTT_CRU`, `EXTT_NGS` and `PRO_COA` get no proposal (country notes): `EXTT_NGS` cannot run (activity upper limit 0 in every year); `EXTT_CRU` (43.2 PJ in 2024) and `PRO_COA` (3.1 PJ in 2024) can run at zero cost, recorded in GAPS as known-limitation candidates.

## Plants

Source: `plant_summary.csv`, `plant_costs.csv`. 2024 values; CapitalCost USD/kW, FixedCost USD/kW-yr, VariableCost USD/GJ (non-fuel variable O&M). Class is the P2 class of the 2024 cell; the last column lists every class used over 2018 to 2050.

| Technology | Capital cur | Capital prop | Fixed cur | Fixed prop | Variable cur | Variable prop | Class 2024 (C / F / V) | Sources 2024 (C / F / V) |
|---|---|---|---|---|---|---|---|---|
| `PPADSL` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPAFOI` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPANGS` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPBGS` | 0.0 | 2,162.0 | 0.00 | 163.67 | 0.0000 | 1.3889 | replace / replace / replace | CSD-009 / CSD-012 / CSD-009 |
| `PPBIM` | 38.5 | 2,162.0 | 35.16 | 35.16 | 1.5806 | 1.5806 | replace / matched / matched | CSD-009 / CSD-008 / CSD-008 |
| `PPCCTDSL` | 1,100.0 | 1,100.0 | 35.16 | 35.16 | 3.1767 | 0.7083 | matched / matched / replace | CSD-008 / CSD-008 / CSD-008 |
| `PPCCTNGS` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPCOA` | 3,676.0 | 3,676.0 | 82.00 | 40.58 | 0.7056 | 1.2500 | matched / replace / replace | CSD-008 / CSD-008 / CSD-008 |
| `PPDBGS` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPDBIM` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPDDSL` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPDFOI` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPDGLP` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPDGSL` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPDHYD` | 1,980.0 | 2,881.0 | 20.00 | 72.03 | 0.0000 | 0.0000 | replace / replace / matched | CSD-009 / CSD-009 / CSD-009 |
| `PPDNGS` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPHDAM` | 3,007.7 | 3,241.3 | 85.00 | 92.00 | 0.0000 | 0.0000 | matched, newer edition / matched, newer edition / matched | CSD-011;CSD-012 / CSD-011;CSD-012 / CSD-011 |
| `PPICEFOI` | 1,100.0 | 1,100.0 | 35.16 | 35.16 | 1.0410 | 1.5806 | matched / matched / replace | CSD-008 / CSD-008 / CSD-008 |
| `PPICEGASFOI` | 982.1 | 1,066.7 | 14.10 | 14.10 | 0.3751 | 0.7083 | replace / matched / replace | CSD-008;CSD-012 / CSD-008 / CSD-008 |
| `PPPVD` | 1,789.6 | 1,789.6 | 18.00 | 18.00 | 0.0000 | 0.0000 | matched / matched / matched | CSD-011 / CSD-011 / CSD-011 |
| `PPPVT` | 861.8 | 916.5 | 13.55 | 21.61 | 0.0000 | 0.0000 | replace / replace / matched | CSD-009;CSD-012 / CSD-012 / CSD-012 |
| `PPPVTHYD` | 861.8 | 916.5 | 13.55 | 21.61 | 0.0000 | 0.0000 | replace / replace / matched | CSD-009;CSD-012 / CSD-012 / CSD-012 |
| `PPWNDON` | 1,443.0 | 1,281.9 | 25.46 | 31.65 | 0.0000 | 0.0000 | replace / replace / matched | CSD-009;CSD-012 / CSD-012 / CSD-012 |

Source ids: CSD-008 CNE Plan Energetico Nacional 2022-2036 (Tablas 220, 223, 229); CSD-009 IRENA Renewable Power Generation Costs in 2022; CSD-011 and CSD-012 NREL ATB 2023 and 2024; full records in `sources.csv`.

## Electricity imports

`IMP_ELE` has an activity upper limit of 0 in every BAU year (VariableCost 19.05 USD/GJ, CapitalCost 1,642.86, FixedCost 32.86). It never runs, so rule E1 does not apply and nothing is proposed.

## Country task

- Gasoline and LPG use the market import cost (decision 2): `DIST_GSL` 19.614 USD/GJ (US export FOB to the DR times the DR CIF/FOB ratio, HS 271012) and `DIST_LPG` 11.042 USD/GJ (DR customs CIF, HS 271112 plus 271113). The MICM parities (19.490 and 15.253) are in `price_points_2024.csv`.
- The same rule (market over administrative) is applied to natural gas: `DIST_NGS` uses the DR customs CIF of LNG (8.936 USD/GJ, already net) instead of the MICM PPI (8.666 USD/GJ gross, 9.629 net), which is fixed in pesos. See GAPS.
- `DIST_KER` is priced (current 0) at the MICM kerosene import parity, 19.889 USD/GJ in 2024; jet fuel parity (20.015) is recorded beside it.
- `PPBIM` CapitalCost 38.46 USD/kW has no external source; proposed 2,162 USD/kW (IRENA 2022 bioenergy). `PPBIM` cannot build more capacity, so the change does not affect investment. Its fixed (35.16) and variable (1.5806) values match the PEN Tabla 229 engine figures by number.
- `PPBGS` (can build, activity limit up to 16 PJ) had zero placeholders; proposed capital 2,162 USD/kW (IRENA 2022), fixed 163.67 USD/kW-yr (ATB 2024 Biopower), variable 1.389 USD/GJ (IRENA 2022, 0.005 USD/kWh).
- Activity check: `EXTT_NGS` cannot run; `EXTT_CRU` and `PRO_COA` can (see GAPS).

## ASSUMPTION rows

0 rows have basis ASSUMPTION. 81 rows (`DIST_NGS`, history from ratio and projected years) carry the brief's natural gas gross-to-net ASSUMPTION sentence, because their Henry Hub benchmark is published per MMBtu; the observed LNG customs values are per tonne and already net.

## Paper trail

Source: `paper_trace.csv`. Statements per document:

- CLEWISE_DataInBrief.docx: 54
- CLEWISE_JCLP_draft_v2.docx: 7
- Data_v2.xlsx: 5
- CLEWISE_MethodsX_v02.docx: 3
- Suplementary.xlsx: 1

What changes if the proposals are applied: the Data in Brief section 4.8 text (sources, base year, currency basis, fuel price scenarios), the Table 53 rows for the 9 supply rows and 23 plants (two rows to add, `PPBGS` and `DIST_KER`), references [13] and [14]; the MethodsX energy template sentence on costs; the JCLP results for the DR (DCAPEX/GDP, DOPEX/GDP, accumulated investment, fuel-import exposure, BAU emissions check) after a rerun; `Suplementary.xlsx` sheet Costos_RD (same as Table 53) and `Data_v2.xlsx` sheet 13.RD_Costos (results to recompute).

## Notes for LAC_COST_WRITE

- 1623 proposal rows fill workbook cells that are empty today (their current value is the BAU compiled value produced by the row's projection mode).
- 41 technology-parameter rows have `needs_user_defined_mode = yes`: their proposal varies by year or fills empty cells while the Projection.Mode is Flat, Percent growth of incomplete years or another non user-defined mode. Writing the cells without changing the mode to User defined would leave the proposals unused.
- Fuel rows have three scenario variants (STEPS, CPS, NZE); the base model uses STEPS.
