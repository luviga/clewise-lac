# REPORT LAC_COST_SRC_ECU 20261110T025435Z

- Pull request: https://github.com/luviga/clewise-lac/pull/4 (draft, number 4)
- Branch: `job/cost-src-ecu` on top of `2ddd560`. First commit `e4c62fa` (all outputs). A second commit normalizes line endings and adds the pull request number and gate results here; its hash is the head of the branch (see GAPS, incidents).
- Job folder: `_LAC_HUB/cost_src_ecu_20261110T025435Z/`
- No model file changed. All values are in real 2024 USD, and fuel prices are in USD/GJ net (= MUSD/PJ).

## Gate results

- Gate 1 read-only: 6 files hashed; equal to baseline_before: PASS
- Gate 2 diff scope: 24 files changed since 2ddd560; outside job folder: 0: PASS
- Gate 3 tracked types: 24 tracked files; other extensions 0; under downloads/ 0: PASS
- Gate 4a proposals rows: 6090 (4609 non-ASSUMPTION); source ids not in sources.csv: []; rows without source ids: 0: PASS
- Gate 4b sources: 80 records; problems: 0 []: PASS
- Gate 5 ASSUMPTION: 1481 rows, 19 technologies (ADD_GRE, DIST_BGS, DIST_BIM, DIST_CHA, DIST_COA, DIST_COK, DIST_CRU, DIST_DSL, DIST_FIR, DIST_FOI, DIST_GSL, DIST_JET, DIST_KER, DIST_LPG, DIST_NGS, DIST_OID, DIST_OPE, DIST_RDF, IMPELE); without logged leads: []; sentences 26, with forbidden words 0 [], missing Reason/Range 0: PASS
- Gate 6 coverage: 29 plants x 3 parameters, 13 supply rows x 3 scenarios, IMPELE; 30 year columns 2021-2050; gaps []; duplicate cells 0: PASS
- Gate 7 hygiene: git diff --check output 0 chars; em dash or machine path hits 0 []; trailer lines in last 3 commits: False: PASS

Gate 7 failed on the first commit (Windows line endings read as trailing whitespace) and passes after the second commit. All gates were run again on the final tree.

## Fuel supply rows

How to read this table:
- Value 2024 is the chosen published point (USD/GJ net, real 2024).
- Current is the 2024 workbook value.
- r is the anchor ratio of rule F4: USD/GJ per USD/bbl of Brent, or per USD/t of Australian coal for coal.
- The step at the join compares, in STEPS, the first projected year with the last observed year.

| Row | Chosen point (source) | 2024 value | Current | r and case | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join |
|---|---|---|---|---|---|---|---|---|---|
| DIST_COA | import CIF, Comtrade (ECU-017, ECU-018) | 8.913 | 1 | 0.06549, 2024 ratio alone (benchmark World Bank Australian coal; WEO steam coal Japan) | 7.27 | 4.96 | 6.20 | 2.89 | -3.1 percent (2024 to 2025) |
| DIST_COK | import CIF, Comtrade (ECU-018, ECU-023) | 3.794 | 1 | 0.04712, 2024 ratio alone (Brent; WEO crude) | 3.82 | 3.65 | 5.09 | 1.20 | +0.1 percent (2024 to 2025) |
| DIST_CRU | export FOB, EP Petroecuador (ECU-001) | 11.864 | 1 | 0.14725, mean 2018-2025 (BCE history ECU-002) | 11.94 | 11.41 | 15.91 | 3.75 | +20.3 percent (2025 to 2026) |
| DIST_DSL | import CIF, EP Petroecuador (ECU-001) | 17.718 | 1 | 0.23008, mean 2018-2025 | 18.65 | 17.82 | 24.86 | 5.86 | +14.2 percent (2025 to 2026) |
| DIST_FOI | export FOB, EP Petroecuador (ECU-001) | 10.106 | 1 | 0.12779, mean 2018-2025 | 10.36 | 9.90 | 13.81 | 3.26 | +14.9 percent (2025 to 2026) |
| DIST_GSL | import CIF, EP Petroecuador (ECU-001) | 20.133 | 1 | 0.25132, mean 2018-2025 | 20.38 | 19.47 | 27.15 | 6.40 | +19.1 percent (2025 to 2026) |
| DIST_JET | import CIF, EP Petroecuador (ECU-001) | 23.183 | 1 | 0.28792, 2024 ratio alone | 23.34 | 22.30 | 31.11 | 7.34 | +0.1 percent (2024 to 2025) |
| DIST_KER | wholesale import parity, Diesel 1 industrial terminal price excl. VAT (ECU-003 to ECU-015) | 18.324 | 1 | 0.22757, 2024 ratio alone | 18.45 | 17.63 | 24.59 | 5.80 | +0.1 percent (2024 to 2025) |
| DIST_LPG | import CIF, EP Petroecuador (ECU-001) | 11.767 | 1 | 0.15298, mean 2018-2025 | 12.40 | 11.85 | 16.53 | 3.90 | +15.5 percent (2025 to 2026) |
| DIST_NGS | generator delivered, 2.881 gross / 0.9 (ECU-001) | 3.201 | 1 | none: administered domestic price, flat at observed real mean 2018-2025 | 3.44 | 3.44 | 3.44 | 3.44 | -11.1 percent (2025 to 2026) |
| DIST_OPE | none published; ASSUMPTION: fuel oil export series | 10.106 | 1 | as DIST_FOI | 10.36 | 9.90 | 13.81 | 3.26 | as DIST_FOI |
| EXTT_CRU | CCG kit crude extraction cost MINOIL (CCG-002) | 13.936 | 1 | not a price row; CCG path, same in all scenarios | 15.72 | 21.51 | 21.51 | 21.51 | none |
| EXTT_NGS | CCG kit gas extraction cost MINNGS (CCG-002) | 5.908 | 1 | not a price row; CCG path, same in all scenarios | 7.09 | 11.03 | 11.03 | 11.03 | none |

The other published 2024 price points are in price_points_2024.csv, with their difference to the chosen point: terminal, generator-delivered and final-consumer prices. The WEO 2025 values used are in constants.csv (Table 2.3, page 109).

## Power plants, 2024

Units and conversions:
- CapitalCost is in USD/kW, FixedCost in USD/kW-yr and VariableCost in USD/GJ.
- CCG values are in 2020 USD, times 1.212038 (US CPI-U 2024/2020).
- ATB values are overnight costs in 2022 USD, times 1.071874.
- CCG fixed costs include variable O&M, so VariableCost is 0.
- PLANMICC values sit beside each value in plant_costs.csv, with pairs that differ by more than 25 percent flagged.

| Plant | CapitalCost current / proposed | FixedCost current / proposed | VariableCost current / proposed | P2 class | Source |
|---|---|---|---|---|---|
| PPBGS | 1 / 2,308.93 | 1 / 15.76 | 1 / 0.00 | replace | CCG PWRBIO001 |
| PPBIM | 2 / 2,308.93 | 2 / 15.76 | 2 / 0.00 | replace | CCG PWRBIO001 |
| PPIBIM | 1 / 2,308.93 | 1 / 15.76 | 1 / 0.00 | replace | CCG PWRBIO001 |
| PPCRU | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPDDSL | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPDFOI | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPDSL | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPFOI | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPRDSL | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPILPG | 1 / 1,454.45 | 1 / 18.18 | 1 / 0.00 | replace | CCG PWROHC001 |
| PPNGS | 1 / 706.62 | 1 / 12.12 | 1 / 0.00 | replace | CCG PWRNGS002 |
| PPRNGS | 1 / 706.62 | 1 / 12.12 | 1 / 0.00 | replace | CCG PWRNGS002 |
| PPHDAMAB | 5000 / 3,562.18 | 1 / 106.87 | 1 / 0.00 | replace | CCG PWRHYD001 |
| PPHDAMAM | 3500 / 3,500.00 | 1 / 106.87 | 1 / 0.00 | matched;replace | CCG PWRHYD001 |
| PPHDAMAS | 5000 / 3,030.10 | 1 / 90.90 | 1 / 0.00 | replace | CCG PWRHYD002 |
| PPHDAMPM | 3500 / 3,500.00 | 1 / 106.87 | 1 / 0.00 | matched;replace | CCG PWRHYD001 |
| PPHDAMPS | 5000 / 3,030.10 | 1 / 90.90 | 1 / 0.00 | replace | CCG PWRHYD002 |
| PPHRORAB | 3500 / 3,500.00 | 1 / 106.87 | 1 / 0.00 | matched;replace | CCG PWRHYD001 |
| PPHRORAM | 5000 / 3,562.18 | 1 / 106.87 | 1 / 0.00 | replace | CCG PWRHYD001 |
| PPHRORAS | 3500 / 3,030.10 | 1 / 90.90 | 1 / 0.00 | replace | CCG PWRHYD002 |
| PPHRORPM | 5000 / 3,562.18 | 1 / 106.87 | 1 / 0.00 | replace | CCG PWRHYD001 |
| PPHRORPS | 3500 / 3,030.10 | 1 / 90.90 | 1 / 0.00 | replace | CCG PWRHYD002 |
| PPHD | 1 / 4,240.92 | 1 / 127.23 | 1 / 0.00 | replace | CCG PWRHYD003 |
| PPIHD | 1 / 4,240.92 | 1 / 127.23 | 1 / 0.00 | replace | CCG PWRHYD004 |
| PPPVT | 800 / 1,484.89 | 1 / 19.30 | 1 / 0.00 | replace | CCG PWRSOL001 |
| PPPVTS | 1 / 2,101.82 | 1 / 19.50 | 1 / 0.00 | replace | CCG PWRSOL001S |
| PPWNDON | 1300 / 1,430.45 | 1 / 57.22 | 1 / 0.00 | replace | CCG PWRWND001 |
| PPPVD | 100 / 1,855.49 | 1 / 19.71 | 1 / 0.00 | replace | NREL ATB 2024 |
| PPWNDD | 1 / 3,676.44 | 1 / 41.74 | 1 / 0.00 | replace | NREL ATB 2024 |

Renewable capital paths follow the CCG kit workbook:
- Utility PV goes from 1,485 USD/kW (2024) to 941 (2030) and 800 (2050).
- Onshore wind goes from 1,430 to 1,075 and 924.
- ATB distributed wind falls from 3,676 to 1,736 by 2050.

## Other rows, 2024

- **Transmission and distribution** (CCG PWRTRN and PWRDIST, per PJ/yr of capacity): ELE_TRANS capital is 28.67 MUSD per PJ/yr and ELE_DIST 57.30. Fixed and variable costs are 0.
- **Storage** STOELE (NREL ATB 2024 Li-ion 4 hour, per PJ/yr): capital 60.16, fixed 1.50, variable 0.
- **Refineries** REF_DSL, REF_FOI, REF_GSL, REF_JET, REF_LPG and REF_OPE: VariableCost 0.870 USD/GJ (CCG UPSREF001). CapitalCost and FixedCost are empty in the workbook and not proposed.
- **PLANMICC values:**
  - PROCRU: fixed 114.48 per capacity unit (3.63 x 31.536), variable 2.40.
  - PRONGS: capital 1.02, fixed 0.50, variable 2.04.
  - HYD_G_PROD: capital 34.34, fixed 1.27, variable 0.67.
  - HYD_DIST: variable 29.71, falling to 6.60 in 2050; capital and fixed 0.
- **Biomass supply:** DIST_BIM and DIST_FIR 6.79 USD/GJ (CCG MINBIO).
- **ASSUMPTION rows:**
  - DIST_CHA 13.57 USD/GJ.
  - DIST_BGS, DIST_OID and DIST_RDF 0.
  - ADD_GRE 0 for all three costs.
  - All DIST_* capital and fixed costs 0.

## Electricity imports (Step 6)

IMPELE covers imports from Colombia and Peru. Its quantity is fixed by activity limits of 1.675 to 1.759 PJ a year.

| Year | Price paid (USD/MWh) | Notes |
|---|---|---|
| 2021 | 25.5 | nominal |
| 2022 | 59.5 | nominal |
| 2023 | 216.4 | nominal |
| 2024 | 263.5 | 334.50 MUSD for 1,269.6 GWh, equal to 73.19 USD/GJ in real 2024 USD |

- Sources: ARCONEL Estadistica 2024, Tablas 145 to 148 (ECU-020), and CENACE Informe Anual 2024, Tabla 2.4 (ECX-001).
- Observed values are used for 2021 to 2024. From 2025, the 2024 price is held flat as an ASSUMPTION.
- Capital and fixed costs are 0 (ASSUMPTION).
- The current value is 1. PLANMICC uses 11.83 with no source.

## Country task (Step 7)

- **Plants:** CCG Ecuador starter kit v1.0 (Zenodo 5498094; Allington et al. 2022), converted from 2020 USD to 2024 USD. Every value is compared with PLANMICC at commit 7483e67: the compiled BAU costs and the v2 cost sheet source codes. 61 technology-parameter pairs differ by more than 25 percent; GAPS section 3 gives the causes.
- **Hydro mapping:** in mapping_ECU.csv. Dam and run-of-river plants, Amazon and Pacific, big and medium map to CCG large hydro, and small to CCG medium hydro. PLANMICC rows match by basin, kind and size.
- **DIST_* capital and fixed costs:** 0, with an ASSUMPTION sentence.
- **Transmission, distribution, refinery, production and storage rows:** CCG where the kit has them, otherwise PLANMICC, otherwise NREL ATB 2024 (storage).
- **Fuel decisions (decision 6):** applied. Fuel oil and crude are at export FOB. Gas is at the domestic price to generators, held flat. Administered products use market import unit values.
- **DIST_OPE:** the fuel oil export series, as an ASSUMPTION.
- **EXTT_CRU and EXTT_NGS:** CCG extraction costs.

## ASSUMPTION rows

There are 1,481 ASSUMPTION proposal cells in 19 technologies:
- **All three costs:** ADD_GRE and IMPELE.
- **CapitalCost and FixedCost:** DIST_BGS, DIST_BIM, DIST_CHA, DIST_COA, DIST_COK, DIST_CRU, DIST_DSL, DIST_FIR, DIST_FOI, DIST_GSL, DIST_JET, DIST_KER, DIST_LPG, DIST_NGS, DIST_OID, DIST_OPE and DIST_RDF.
- **VariableCost:** DIST_BGS, DIST_CHA, DIST_OID, DIST_OPE and DIST_RDF, plus DIST_NGS for 2026 to 2050.

Every natural gas cell also carries the F5 gross-to-net sentence.

| Basis class | Cells |
|---|---|
| replace | 3,687 |
| ASSUMPTION | 1,481 |
| projected | 687 |
| observed | 106 |
| matched | 93 |
| history from ratio | 36 |

| Change class | Cells |
|---|---|
| fill_placeholder | 5,700 |
| replace | 297 |
| keep | 93 |

## Paper trail

paper_trace.csv holds 53 statements.

| Document | Statements | Needing a change if the proposals are applied |
|---|---|---|
| CLEWISE_DataInBrief.docx | 20 | 14 |
| CLEWISE_JCLP_draft_v2.docx | 12 | 10 |
| CLEWISE_MethodsX_v02.docx | 8 | 6 |
| Data_v2.xlsx | 7 | 6 |
| Suplementary.xlsx | 6 | 1 |

What changes:
- **Data in Brief:** it has no Ecuador cost table. Its section 4.8 says costs are in current USD without deflation and come from IRENA and WEO 2023 learning curves. For Ecuador it would need to name the CCG kit, PLANMICC, EP Petroecuador and WEO 2025, and to state real 2024 USD.
- **MethodsX:** it states no cost or fuel price input. Step 1, section 1.4.1 and the fuel-import exposure indicator of Step 5 would each gain a sentence on the cost and price basis.
- **JCLP draft:** it cites no cost or price source. Sections 2.2.1, 2.4.1 and 2.4.3 would gain the basis. The Ecuador statements and figures in section 3.5 rest on incomplete Data_v2 rows and would need recomputing after a model rerun.
- **Data_v2.xlsx:** its Ecuador cost and fuel import rows are blank or copied from Guatemala.
