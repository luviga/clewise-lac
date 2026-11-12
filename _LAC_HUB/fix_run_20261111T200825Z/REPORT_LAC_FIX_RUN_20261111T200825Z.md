# REPORT LAC_FIX_RUN 20261111T200825Z

Job LAC_FIX_RUN: the seven review fixes of PR #10, recompile of A2 and B1, one re-run of Stages 0 to 3. Clone `/c/clw_fix`, branch `job/fix-run`, base `main` at c42ae07ac81f0f3a28f6275e7ce356f9696c4f77 (PR #10). Judgement calls, the corrections made at the recompile and the limitation candidates are in `GAPS_LAC_FIX_RUN_20261111T200825Z.md`; the pull request text is `CHANGES_LAC_FIX_RUN_20261111T200825Z.md`.

## 1. Failed, blocked or pending

1. **Jamaica `PPHROR` gate failed by 0.15 MW.** Stage 3 builds 34.45 MW in every scenario (2027 12.96, 2028 7.13, 2029 11.15, 2031 2.11, 2032 1.11 MW) against the plan's 34.3 MW; nothing is built in 2024 to 2026. Cause: the Stage 2 controller sets the `PPHROR` activity lower limit from 2032 at 0.5874 PJ (`CURRENT_LOWER`), 0.44 percent above what 34.3 MW produce at the capacity factor of 0.543 (0.5848 PJ), and Stage 3's documented `--uncap-pp-maxcap` lifts the cumulative-plan cap from 2025, so the model builds the extra 0.15 MW. The brief asks for one run and no tuning, so it was not corrected. A least-change correction for a later run: Stage 2 overwrite lines for Jamaica `PPHROR` 2027 to 2055 with the share that 34.3 MW give, or a lower limit taken from the A-O row (98 percent of the plan's output).
2. **History check (power-plant activity through 2024, 0.05 PJ) failed in three countries.**
   - Costa Rica, 17 technology-years: NDCNEW and LTSNEW run `PWRSUG` in 2021 to 2024 (up to 6.1 PJ in 2023), which BAU caps at 0, because their transport history carries more demand than BAU's. Test solves: the BAU cap alone makes NDCNEW infeasible; with the transport rows of 2021 to 2024 set to BAU it solves (GAPS items 36 and 37). Hydro, wind and geothermal move with it; total generation differs by up to 3.6 PJ (2023).
   - Dominican Republic, 18 technology-years: `PPDHYD`, `PPDBGS` and `PPDBIM` keep their PR #10 history lower limits, because BAU's would force capacity the policy scenarios cap from 2025 (GAPS item 33); coal and fuel-oil plants move within their history bands (largest 0.43 PJ).
   - Ecuador, 2 technology-years: in LTSNEW 2022 run-of-river output is split differently between `PPHRORPM` and `PPHRORAS` (3.46 PJ); their total is the same (total power-plant activity differs by 0.0002 PJ).
   - Guatemala, Honduras and Jamaica pass (largest spread 0.008 PJ).
3. **Stage 2 soft tests.** T11a fails in one year (Costa Rica 2023, 3.6 PJ, same cause as item 2; PR #10 had 27 years). T9 fails (87 hydro-freeze cases; Jamaica's planned hydro rises after 2026, expected under R7). T8 fails (65 share jumps over 5 points, as in PR #10). All seven hard tests pass.
4. **Stage 3 test T4** (paired upper rule) fails 40 of 7,998 cases, Guatemala `PPPVD` and `PPPVDS` with zero lower limit and an upper of 99,999; PR #10 had the same count.
5. **Decision for review: emission factors after 2024.** To give NDCNEW and LTSNEW BAU's calibrated history emission factors (they differed by up to 64 percent), whole rows were added, because B1 writes every year of an Exact row. The Dominican Republic and Ecuador B1 round these rows to four decimals, so the scenarios' own factors from 2025 change by at most 0.00005 (power plants at most 0.03 percent; Ecuador refinery CO2 and CO2e up to 0.6 percent; refinery CH4 and N2O factors of about 1e-7 become 0). This departs from "nothing after 2024"; removing the 32 Dominican Republic and Ecuador rows reverses it (GAPS item 38).
6. **R6 exceptions** (`r6_not_applied.csv`, 18 rows): Dominican Republic distributed generation (12 cells), Costa Rica 2021 lower limits of `PWRBMS` and `PWRHYDROR` (4 cells), Costa Rica `PWRSUG` history cap (2 rows not added). Transport history is not aligned (GAPS item 37).
7. **R3 deviation:** crude imports opened in 2021 and 2022 (0 to 999,999 PJ); without it every Ecuador scenario is infeasible, because the refinery input lower limit is above sourced production minus sourced exports (GAPS item 31).
8. **R3 pending:** no published production or export outlook after 2030; the 2031 to 2050 values are unchanged (`sources_pending.csv`). The kept export demand falls to 0 from 2038, and the kept extraction lower limit makes the model export about 290 PJ a year through `T5CRUEXP` without a demand.
9. **Phase B write gate (2), strict:** 31 formula cells outside the list changed because they depend on written cells (Dominican Republic `J233` and `J253` = `J232` x 0.5 percent; Jamaica `PPHROR` lower-limit formula row 198). Expected; listed in `write_check_diffs.csv`.

## 2. Pull request and commits

- Pull request: https://github.com/luviga/clewise-lac/pull/11 (draft)
- Base: `main` c42ae07ac81f0f3a28f6275e7ce356f9696c4f77
- Phase A, sources and proposals: f997ff4
- Phase B, review fixes written: cfaa90e
- Phase C, A2 and B1 recompiled: bb89b9d
- Phase D, Stages 0 to 3: c0cd76c
- Phase E, report, gaps and changes: f9b816d
- Last commit: writes this section (pull request number and hashes) only

## 3. Fixes, before and after

Every written cell is a row of `proposals.csv` (7,755 rows: source ids, derivation and ASSUMPTION sentence where used); sources in `sources.csv` (111 ids, SHA-256 of each download); unreachable ones in `sources_pending.csv` (41 rows).

| Fix | What changed | Before (c42ae07) | After | Sources |
|---|---|---|---|---|
| R1 Guatemala `DIST_FLEXFUEL` VariableCost | formula `=I14+(I14*0.8)` replaced; row User defined | 45.31 (2018), 44.07 (2024), 71.89 (2050) USD/GJ | 26.94 (2018), 20.80 (2024), 20.58 (2050) | R1F-14, R1F-15, R1F-18, BEN-004 |
| R1 Honduras `PPBGS` CapitalCost 2018 to 2020 | formula replaced | 1,813.82 USD/kW | 7,269.10 | R1F-11, BEN-004 |
| R1 Dominican Republic `ELE_TRANS` CapitalCost | formula (8,670 h) replaced; Flat row | 2.7251 MUSD per PJ/yr | 3.3093 | R1F-01, BEN-004 |
| R2 Costa Rica `E5INDCOA` 2021 | four config rows (BAU, NDCNEW, LTSNEW, LTSOPT) | 0.675 PJ | 0.00667 PJ (0.0067 after B1 rounding) | CRC-006 |
| R3 `DIST_CRU` VariableCost | Brent on the WEO 2025 STEPS path, real 2024 USD | 11.86 (2024), 11.41 (2050) USD/GJ | 13.93 (2024), 13.40 (2050) | BEN-001, BEN-004, BEN-005, GEN-001, GEN-002 |
| R3 `EXTT_CRU` VariableCost | former `DIST_CRU` path (export value) | 13.94 (2024), 21.51 (2050) | 11.86 (2024), 11.41 (2050) | ECU-002, BEN-001, BEN-004, BEN-005 |
| R3 `T5CRUEXP` VariableCost | new Demand Techs row 203 | none | minus the export value (-11.86 in 2024) | as above |
| R3 `EXTT_CRU` activity limits | BCE field production, capped at 2025 | upper 960.2 (2024), 756.5 (2030) PJ | upper 1,005.2 (2024), 929.4 (2030); lower 0.98 x upper | ECUF-01, ECU-002, ECUF-03, GEN-001, GEN-002 |
| R3 `E5EXPCRU` demand | BCE exports and outlook to 2030 | 629.1 (2024), 495.7 (2030) PJ | 729.9 (2024), 655.9 (2030) | ECUF-01, ECU-002, ECUF-03, GEN-001, GEN-002 |
| R3 `DIST_CRU` limits | lower 0 every year; upper 999,999 in 2021 and 2022 | lower 49.2 (2024) to 377.4 PJ (2035); upper 0 in 2021 to 2023 | lower 0; upper 0 only in 2023 | brief R3 |
| R4 109 cost groups | dollar year from the source, else ASSUMPTION year before publication; CPI-U to 2024 USD | e.g. Dominican Republic `PPADSL` CapitalCost 1,084; Jamaica `PPNGS` 1,300 | 1,254.89 (PEN, 2021 USD ASSUMPTION); 1,894.60 (OUR 2010 prices) | `currency_conversion.csv`; 2,884 cells (Dominican Republic 1,980, Guatemala 302, Ecuador 270, Jamaica 246, Honduras 86) |
| R5 matched cells | source value in 2024 USD over old values kept within 2 percent | old value | source value | 105 R5 cells and 126 R4+R5 cells; 14 regional cells left |
| R5 Ecuador hydro | `PPHDAMAM`, `PPHDAMPM`, `PPHRORAB` CapitalCost | old values | 3,562.18 USD/kW (CCG `PWRHYD001`, 2,939 in 2020 USD) | CCG-001, CCG-002, BEN-004 |
| R6 history | see the table below | policy history differed from BAU | BAU history except the exceptions in section 1 | B1_Output_Params of BAU |
| R7 Jamaica `PPHROR` | minimum investments, cumulative cap, config rows 29 and 59 (Overwrite), Stage 2 lines 2025 and 2026 | 50.5 MW built (c42ae07, Stage 3), some in 2024 to 2026 | plan 34.3 MW from 2027 (Stage 3 builds 34.45 MW, section 1) | JAMF-01 (2022 IRP) |
| R8 | `starter_kit_deviations.csv` | none | 36 rows | CCG Ecuador kit |

R6 changes in `B1_Scenario_Config.xlsx` (NDCNEW and LTSNEW; cells / rows):

| Country | History values of existing rows | New history-only rows | New emission-factor rows |
|---|---|---|---|
| Costa Rica | 58 / 28 | 28 / 2 (`PWRHYDDAM` upper limit) | none |
| Dominican Republic | 280 / 140 | none | 516 / 12 |
| Ecuador | 364 / 182 | none | 740 / 20 |
| Guatemala | 176 / 88 | 28 / 2 (`IMP_ELE` lower limit) | none |
| Honduras | 208 / 104 | none | 1,978 / 46 |
| Jamaica | 128 / 62 | none | none |

## 4. Gates

**Phase B (`write_check.csv`).** (1) every written cell equals `proposals.csv`: pass in all 12 workbooks. (2) changes only at listed cells: pass except the 31 dependent formula cells (section 1, item 9). (3) no formula without a stored value: pass. (4) no formula left in the R1 cells: pass. (5) the other 472 tracked A-O workbooks identical to c42ae07: pass. (6) Stage 2 Jamaica file changed only on the 12 listed lines: pass.

**Phase C (`recompile_diff_summary.csv`).** A2 and B1 exit 0 for all six models; 19 B1 solves OPTIMAL (Costa Rica 4 with the temporary LTSOPT, five models 3 each). Keyed comparison of A2 outputs, B1 outputs and B1 data files against c42ae07: 42,488 differing values, 0 outside the allowed list. Allowed reasons: proposal cost cells 31,428; R6 history changes 7,640; R6 emission-factor rows rounded by B1 from 2025 1,664 (at most 0.00005); dependent R1 formula cells 594; R3 Ecuador crude 531; R7 Jamaica `PPHROR` 521; R6 history-only rows at the B1 default from 2025 104; R2 6. The first recompile found nine infeasible solves and two unreadable data files caused by this job's writes; GAPS items 31 to 38 give each cause and correction.

**Phase E.** See section 8.

## 5. Phase D checks (`fix_checks.csv`, details in `fix_checks_detail.csv`)

| Check | Country | Result | Count | Note |
|---|---|---|---|---|
| history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ | CostaRica | FAIL | 17 | max spread 6.1082 PJ; total PP activity spread max 3.6038 PJ |
| history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ | DominicanRepublic | FAIL | 18 | max spread 0.4338 PJ; total PP activity spread max 0.4629 PJ |
| history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ | Ecuador | FAIL | 2 | max spread 3.4566 PJ; total PP activity spread max 0.0002 PJ |
| history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ | Guatemala | pass | 0 | max spread 0.0080 PJ; total PP activity spread max 0.0104 PJ |
| history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ | Honduras | pass | 0 | max spread 0.0001 PJ; total PP activity spread max 0.0001 PJ |
| history: PP activity per technology, years <= 2024, spread across scenarios > 0.05 PJ | Jamaica | pass | 0 | max spread 0.0000 PJ; total PP activity spread max 0.0000 PJ |
| Stage 2 test T9_hydro_pj_freeze | all | FAIL |  | T9_hydro_pj_freeze: 87 violations e.g. Jamaica/BAU 2027: 0.615 > boundary 0.394 |
| Stage 2 test T11a_denom_alignment | all | FAIL |  | T11a_denom_alignment: 1 years with scenario spread >0.5 PJ e.g. CostaRica 2023: BAU=45.5 NDC=49.1 LTS=49.1 (spread=3.6 PJ) |
| Stage 2 T9 violations printed for Jamaica (first lines of the log only) | Jamaica | info | 1 |  |
| Ecuador crude surplus (extraction + imports - refinery - exports) at most 0.5 PJ, every year and scenario | Ecuador | pass | 0 | largest surplus 0.000 PJ |
| Jamaica PPHROR new capacity over the horizon at most 0.0343 GW, none in 2024 to 2026 | Jamaica BAU | FAIL |  | total 34.45 MW; 2024-2026 0.00 MW; by year 2027 12.96, 2028 7.13, 2029 11.15, 2031 2.11, 2032 1.11 |
| Jamaica PPHROR new capacity over the horizon at most 0.0343 GW, none in 2024 to 2026 | Jamaica NDCNEW | FAIL |  | total 34.45 MW; 2024-2026 0.00 MW; by year 2027 12.96, 2028 7.13, 2029 11.15, 2031 2.11, 2032 1.11 |
| Jamaica PPHROR new capacity over the horizon at most 0.0343 GW, none in 2024 to 2026 | Jamaica LTSNEW | FAIL |  | total 34.45 MW; 2024-2026 0.00 MW; by year 2027 12.96, 2028 7.13, 2029 11.15, 2031 2.11, 2032 1.11 |
| Jamaica hydro output identical across scenarios (0.05 PJ) | Jamaica | pass |  | max spread 0.0222 PJ |
| Costa Rica E5INDCOA 2021 demand 0.00667 PJ (config; B1 rounds to 4 decimals) | CostaRica BAU | pass |  | Stage 3 data file value 0.0067 |
| Costa Rica E5INDCOA 2021 demand 0.00667 PJ (config; B1 rounds to 4 decimals) | CostaRica NDCNEW | pass |  | Stage 3 data file value 0.0067 |
| Costa Rica E5INDCOA 2021 demand 0.00667 PJ (config; B1 rounds to 4 decimals) | CostaRica LTSNEW | pass |  | Stage 3 data file value 0.0067 |

Ecuador crude balance (PJ; every scenario identical; the balance is 0.000 to -0.005 in every year):

| Year | Extraction | Imports | Refinery | Exports | Export demand |
|---|---|---|---|---|---|
| 2021 | 997.41 | 8.89 | 327.61 | 678.69 | 678.69 |
| 2024 | 1,005.22 | 53.95 | 329.25 | 729.92 | 729.92 |
| 2030 | 929.41 | 55.72 | 329.25 | 655.88 | 655.88 |
| 2035 | 631.97 | 111.33 | 329.25 | 414.05 | 414.05 |
| 2040 | 619.33 | 0.00 | 329.25 | 290.08 | 0.00 |
| 2050 | 619.33 | 0.00 | 329.25 | 290.08 | 0.00 |

Hydro output (PJ, technologies in the controller's HYDRO sub-group), 2026 / 2030 / 2040 / 2050:

| Country | Scenario | 2026 / 2030 / 2040 / 2050 |
|---|---|---|
| CostaRica | BAU | 35.279 / 35.297 / 35.279 / 35.279 |
| CostaRica | LTSNEW | 35.442 / 35.443 / 35.442 / 35.442 |
| CostaRica | NDCNEW | 35.442 / 35.442 / 35.442 / 35.442 |
| DominicanRepublic | BAU | 4.531 / 4.531 / 4.531 / 4.531 |
| DominicanRepublic | LTSNEW | 4.524 / 4.524 / 4.524 / 4.524 |
| DominicanRepublic | NDCNEW | 4.524 / 4.524 / 4.524 / 4.524 |
| Ecuador | BAU | 91.394 / 91.756 / 91.579 / 91.579 |
| Ecuador | LTSNEW | 91.421 / 91.881 / 91.577 / 91.577 |
| Ecuador | NDCNEW | 91.423 / 91.896 / 91.577 / 91.577 |
| Guatemala | BAU | 21.134 / 24.294 / 24.294 / 24.294 |
| Guatemala | LTSNEW | 24.115 / 27.275 / 27.275 / 27.275 |
| Guatemala | NDCNEW | 24.120 / 27.280 / 27.280 / 27.280 |
| Honduras | BAU | 13.727 / 13.727 / 13.609 / 13.609 |
| Honduras | LTSNEW | 13.748 / 13.748 / 13.658 / 13.658 |
| Honduras | NDCNEW | 13.747 / 13.747 / 13.657 / 13.657 |
| Jamaica | BAU | 0.413 / 0.938 / 1.001 / 0.984 |
| Jamaica | LTSNEW | 0.397 / 0.929 / 1.003 / 0.989 |
| Jamaica | NDCNEW | 0.416 / 0.949 / 1.003 / 0.989 |

## 6. Results compared with c42ae07 (`results_compare.csv`)

Status, objective, RE share of power-plant activity (percent, c42ae07 / new) and emissions (sum of AnnualEmissions, c42ae07 / new):

| Country | Scenario | Status (c42ae07 / new) | Objective c42ae07 | Objective new | RE share 2030 | RE share 2035 | RE share 2050 | Emissions 2030 | Emissions 2050 |
|---|---|---|---|---|---|---|---|---|---|
| CostaRica | BAU | OPTIMAL / OPTIMAL | 114,696.9 | 114,660.2 | 89.4 / 89.4 | 89.4 / 89.4 | 89.4 / 89.4 | 23.72 / 23.72 | 34.04 / 34.04 |
| CostaRica | NDCNEW | OPTIMAL / OPTIMAL | 104,293.5 | 104,254.9 | 89.7 / 89.7 | 90.0 / 90.0 | 90.0 / 90.0 | 22.16 / 22.16 | 27.87 / 27.87 |
| CostaRica | LTSNEW | OPTIMAL / OPTIMAL | 95,574.7 | 95,536.1 | 93.7 / 93.7 | 99.0 / 99.0 | 99.0 / 99.0 | 19.50 / 19.50 | 8.43 / 8.43 |
| DominicanRepublic | BAU | OPTIMAL / OPTIMAL | 411,650.9 | 413,922.5 | 19.2 / 19.2 | 23.1 / 23.1 | 33.9 / 33.9 | 72.60 / 72.60 | 112.87 / 112.87 |
| DominicanRepublic | NDCNEW | OPTIMAL / OPTIMAL | 430,751.9 | 433,127.8 | 42.1 / 42.1 | 75.0 / 75.0 | 75.0 / 75.0 | 59.06 / 59.10 | 61.71 / 61.73 |
| DominicanRepublic | LTSNEW | OPTIMAL / OPTIMAL | 454,799.8 | 457,351.8 | 42.1 / 42.1 | 75.0 / 75.0 | 99.0 / 99.0 | 59.06 / 59.10 | 17.44 / 17.44 |
| Ecuador | BAU | OPTIMAL / OPTIMAL | 1,933,690.5 | 1,765,127.7 | 76.3 / 76.3 | 77.4 / 77.4 | 80.6 / 80.6 | 130.95 / 131.86 | 182.77 / 182.77 |
| Ecuador | NDCNEW | OPTIMAL / OPTIMAL | 2,086,398.9 | 1,754,223.3 | 77.7 / 77.3 | 80.2 / 79.7 | 80.6 / 80.6 | 125.79 / 127.05 | 165.35 / 165.86 |
| Ecuador | LTSNEW | OPTIMAL / OPTIMAL | 2,080,589.6 | 1,749,295.5 | 77.7 / 77.3 | 80.2 / 79.7 | 99.0 / 99.0 | 125.42 / 126.69 | 117.68 / 117.70 |
| Guatemala | BAU | OPTIMAL / OPTIMAL | 360,741.1 | 360,672.2 | 53.1 / 53.1 | 57.2 / 57.2 | 64.1 / 64.1 | 75.21 / 75.21 | 156.46 / 156.46 |
| Guatemala | NDCNEW | OPTIMAL / OPTIMAL | 350,274.6 | 347,103.0 | 68.6 / 68.6 | 75.0 / 75.0 | 75.0 / 75.0 | 65.08 / 65.08 | 125.13 / 125.14 |
| Guatemala | LTSNEW | OPTIMAL / OPTIMAL | 348,264.3 | 345,334.8 | 68.6 / 68.6 | 75.0 / 75.0 | 99.0 / 99.0 | 66.71 / 66.72 | 66.55 / 66.55 |
| Honduras | BAU | OPTIMAL / OPTIMAL | 104,949.9 | 104,974.8 | 56.9 / 56.9 | 59.0 / 59.0 | 64.7 / 64.7 | 39.22 / 39.22 | 59.20 / 59.20 |
| Honduras | NDCNEW | OPTIMAL / OPTIMAL | 103,910.2 | 103,198.3 | 64.8 / 64.7 | 75.0 / 75.0 | 75.0 / 75.0 | 36.31 / 36.34 | 52.66 / 52.68 |
| Honduras | LTSNEW | OPTIMAL / OPTIMAL | 101,467.8 | 100,754.8 | 64.8 / 64.7 | 75.0 / 75.0 | 99.0 / 99.0 | 36.24 / 36.28 | 23.90 / 23.90 |
| Jamaica | BAU | OPTIMAL / OPTIMAL | 65,080.5 | 64,972.1 | 13.8 / 13.9 | 18.2 / 18.3 | 29.3 / 29.3 | 12.65 / 12.65 | 15.35 / 15.35 |
| Jamaica | NDCNEW | OPTIMAL / OPTIMAL | 61,693.2 | 61,507.3 | 39.1 / 39.1 | 75.0 / 75.0 | 75.0 / 75.0 | 11.09 / 11.09 | 11.48 / 11.48 |
| Jamaica | LTSNEW | OPTIMAL / OPTIMAL | 59,668.1 | 59,477.8 | 39.1 / 39.1 | 75.0 / 75.0 | 99.0 / 99.0 | 11.02 / 11.02 | 4.80 / 4.80 |

RE targets (2 point tolerance) and share validation:

| Country | Scenario | RE target met 2035 (c42ae07 / new) | RE target met 2050 | Share validation PASS / WARN / FAIL (c42ae07) | (new) |
|---|---|---|---|---|---|
| CostaRica | BAU | n/a / n/a | n/a / n/a | 234 / 0 / 0 | 234 / 0 / 0 |
| CostaRica | NDCNEW | yes / yes | yes / yes | 233 / 1 / 0 | 234 / 0 / 0 |
| CostaRica | LTSNEW | yes / yes | yes / yes | 234 / 0 / 0 | 234 / 0 / 0 |
| DominicanRepublic | BAU | n/a / n/a | n/a / n/a | 598 / 0 / 0 | 598 / 0 / 0 |
| DominicanRepublic | NDCNEW | yes / yes | yes / yes | 598 / 0 / 0 | 598 / 0 / 0 |
| DominicanRepublic | LTSNEW | yes / yes | yes / yes | 598 / 0 / 0 | 598 / 0 / 0 |
| Ecuador | BAU | n/a / n/a | n/a / n/a | 794 / 12 / 0 | 795 / 11 / 0 |
| Ecuador | NDCNEW | yes / yes | yes / yes | 795 / 11 / 0 | 794 / 12 / 0 |
| Ecuador | LTSNEW | yes / yes | yes / yes | 782 / 24 / 0 | 791 / 15 / 0 |
| Guatemala | BAU | n/a / n/a | n/a / n/a | 356 / 6 / 2 | 356 / 6 / 2 |
| Guatemala | NDCNEW | yes / yes | yes / yes | 362 / 2 / 0 | 363 / 1 / 0 |
| Guatemala | LTSNEW | yes / yes | yes / yes | 363 / 1 / 0 | 363 / 1 / 0 |
| Honduras | BAU | n/a / n/a | n/a / n/a | 416 / 0 / 0 | 416 / 0 / 0 |
| Honduras | NDCNEW | yes / yes | yes / yes | 407 / 9 / 0 | 416 / 0 / 0 |
| Honduras | LTSNEW | yes / yes | yes / yes | 407 / 9 / 0 | 416 / 0 / 0 |
| Jamaica | BAU | n/a / n/a | n/a / n/a | 231 / 17 / 0 | 228 / 20 / 0 |
| Jamaica | NDCNEW | yes / yes | yes / yes | 228 / 14 / 6 | 228 / 14 / 6 |
| Jamaica | LTSNEW | yes / yes | yes / yes | 246 / 2 / 0 | 244 / 4 / 0 |

Largest changes in new power-plant capacity summed over the horizon, five per country (`results_compare_top_newcap.csv`):

| Country | Scenario | Technology | New capacity c42ae07 (GW) | New (GW) | Change (GW) |
|---|---|---|---|---|---|
| CostaRica | LTSNEW | PWRSUG | 2.3749 | 2.8733 | +0.4984 |
| CostaRica | NDCNEW | PWRSUG | 1.2933 | 1.2411 | -0.0521 |
| CostaRica | NDCNEW | PWRWNONS | 2.5483 | 2.5472 | -0.0011 |
| CostaRica | LTSNEW | PWRWNONS | 4.2394 | 4.2383 | -0.0011 |
| CostaRica | LTSNEW | PWRSPVTRN | 0.2266 | 0.2266 | +0.0000 |
| DominicanRepublic | LTSNEW | PPDBGS | 0.5427 | 0.0423 | -0.5004 |
| DominicanRepublic | NDCNEW | PPPVT | 12.1498 | 11.6508 | -0.4990 |
| DominicanRepublic | LTSNEW | PPPVT | 17.7157 | 17.2194 | -0.4963 |
| DominicanRepublic | LTSNEW | PPCCTNGSDSL | 0.0000 | 0.3997 | +0.3997 |
| DominicanRepublic | NDCNEW | PPWNDON | 7.2573 | 6.9487 | -0.3086 |
| Ecuador | NDCNEW | PPHD | 597.0758 | 576.7127 | -20.3631 |
| Ecuador | LTSNEW | PPHD | 597.0758 | 576.7127 | -20.3631 |
| Ecuador | LTSNEW | PPFOI | 0.9683 | 0.0950 | -0.8732 |
| Ecuador | LTSNEW | PPRDSL | 1.3252 | 0.6177 | -0.7076 |
| Ecuador | NDCNEW | PPFOI | 0.9683 | 0.2629 | -0.7054 |
| Guatemala | NDCNEW | PPPVT | 3.3803 | 2.9941 | -0.3862 |
| Guatemala | LTSNEW | PPPVT | 7.2639 | 6.8779 | -0.3860 |
| Guatemala | NDCNEW | PPWNDON | 2.4579 | 2.1036 | -0.3542 |
| Guatemala | LTSNEW | PPWNDON | 7.8500 | 7.4960 | -0.3540 |
| Guatemala | NDCNEW | PPPVD | 2.0903 | 2.0767 | -0.0136 |
| Honduras | NDCNEW | PPPVT | 4.3371 | 3.8148 | -0.5223 |
| Honduras | LTSNEW | PPPVT | 7.5196 | 6.9997 | -0.5198 |
| Honduras | NDCNEW | PPWNDON | 2.1214 | 1.9605 | -0.1608 |
| Honduras | LTSNEW | PPWNDON | 3.6745 | 3.5149 | -0.1596 |
| Honduras | LTSNEW | PPHROR | 0.0788 | 0.0411 | -0.0378 |
| Jamaica | NDCNEW | PPNGS | 0.0387 | 0.0209 | -0.0178 |
| Jamaica | LTSNEW | PPNGS | 0.0387 | 0.0209 | -0.0178 |
| Jamaica | NDCNEW | PPHROR | 0.0506 | 0.0345 | -0.0161 |
| Jamaica | LTSNEW | PPHROR | 0.0506 | 0.0345 | -0.0161 |
| Jamaica | BAU | PPHROR | 0.0505 | 0.0345 | -0.0160 |

## 7. Tests and solve statuses

- `test_ao_cost_repair_manager` through `unittest discover`: 4 of 4 OK (`logs/test_ao_cost_repair_manager.log`). `test_ao_safe_save.py`: unittest discover finds no unittest cases; its own runner: 5 of 5 PASS (`logs/test_ao_safe_save.log`).
- Stage 0: 7 steps exit 0; `stage0_test` 10 of 10; 18 relaxed solves OPTIMAL (`stage_logs/solves_stage0.jsonl`).
- Stage 1: `stage1_test_v16` 13 of 13.
- Stage 2: `stage2_test_v2` hard 7 of 7; soft T8, T9, T11a fail (section 1).
- Stage 3: `stage3_test` 10 of 11 (T4 fails as in PR #10); 18 FINAL solves OPTIMAL (`stage_logs/solves_stage3.jsonl`); `stage3_results` exit 0.
- B1 base solves at the final recompile: 19 of 19 OPTIMAL (`recompile/<country>/B1/solve_log.jsonl`).

## 8. Phase E checks

- E1, changed paths against `origin/main`: the five A-O_Parametrization workbooks and Ecuador's A-O_Demand, the six `B1_Scenario_Config.xlsx`, the A2 and B1 outputs of the six models, `_STAGE2_INPUTS/STAGE2_OVERWRITES_Jamaica.csv` (R7), the four stage output folders and this job folder. Pass.
- E2: no committed file over 50 MB; no `*.safesave_tmp*` file; EXCEL.EXE count 0, as at the start; `git -c core.whitespace=cr-at-eol diff --check origin/main` clean after the job's logs were normalised (LF, no trailing blanks, script-printed em dashes as hyphens, as in PR #10; `stage_logs/README.txt`); no em dash in any added line; no Co-Authored-By or "Generated with" line in `git log origin/main..HEAD`. Pass.
- E3: branch pushed and one draft pull request opened (section 2).

## 9. Environment

Git Bash; python.org Python 3.12 for the job scripts (`py -I`) and Anaconda Python for the pipeline scripts; glpsol 4.65 on PATH, without a wrapper during stage runs; batch files called by full path; Guatemala A2 through PR #10's append shim; Costa Rica B1 with a temporary `LTSOPT` copied from LTSNEW and removed afterwards. EXCEL.EXE count 0 at the start and at the end. Free disk 93 GB at the start; below 80 GB after Stage 0, so the 18 Stage 0 solver outputs over 500 MB were deleted after their extraction (`logs/phaseD_deleted_S0_outputs.txt`).
