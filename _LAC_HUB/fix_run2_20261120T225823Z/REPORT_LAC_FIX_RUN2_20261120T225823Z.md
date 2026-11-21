# REPORT LAC_FIX_RUN2 20261120T225823Z

## Failed, blocked or pending

1. **History gate (DS2), power-plant activity through 2024.** Not identical across scenarios in Costa Rica (8 tech-years, largest spread 0.119 PJ), the Dominican Republic (25, 0.421 PJ) and Ecuador (14, 6.953 PJ, `PPHDAMAB` 2022). Causes found by values:
   - Dominican Republic and Jamaica: the NDCNEW and LTSNEW Electrical rows that hold history lower limits as explicit year points ("Stage 3: Recalibrated from TARGET_SHARES" rows) still carry the BAU history from before D7a and D13, while BAU history moved with the 0.999 band (130 Dominican values, up to 0.347 PJ; 12 Jamaica values, up to 0.011 PJ; `logs/history_diff_after_big.csv`). Aligning them needs one more B1 recompile and a third Stage 0 to 3 run, which the brief does not allow (at most one full re-run, used for the Dominican infeasibility).
   - `PPDBIM` (Dominican Republic) keeps its 4ba69d6 policy history by repair C1-1 (GAPS 2.1).
   - Ecuador and part of Costa Rica: inputs are equal; the solver places output differently inside wide history bounds (Ecuador hydro classes have activity upper limits of 9,999 PJ and no capacity caps in history).
2. **History builds gate (DS2).** New capacity in 2021-2024 does not match the sourced commissioning for 5 Costa Rica, 8 Dominican Republic, 12 Ecuador and 3 Jamaica technologies (`history_builds.csv`, with cause and status per technology). Matches or removals: Ecuador `PPHD` (79.1 GW to 0, D1), Ecuador `PPFOI` (Karpowership 100 MW), Costa Rica `PWRDSL` 2024 (PTA Moin 105 MW) and `PWRSUG` (0), Dominican `PPWNDON` (Los Guzmancito II 46.8 MW), `PPDHYD` and `PPDBGS` (below 2 MW), Guatemala (none above 2 MW), Jamaica `PPFOI`, `PPPVT`, `PPWNDON`. The unmatched builds need decisions that change capacity paths into later years, sources without a public address, or plant-class mappings the statistics do not print (GAPS 4).
3. **Guatemala hydro gate (DS2).** Equal in every scenario in 2025 and 2026 (19.705 PJ, D8) and in most later years, but NDCNEW and LTSNEW run up to 0.47 PJ more in 2029 and NDCNEW 1.14 PJ more in 2041 and 2043: Stage 3 sets each plant's upper limit at 1.05 times its pinned lower limit, and the solver uses that band in the policy scenarios. Data cannot remove it without changing the stage scripts.
4. **Not completed under D2c:** Ecuador `PPHRORPM` and `PPHRORAS` minimum investments (the 2022 ARCONEL statistics have no public download address), Ecuador `PPRDSL` residual, Dominican SENI capacity paths (`PPPVT`, `PPPVD`, `PPICEFOI`, `PPHDAM` timing), Jamaica `PPNGS`, `PPDSL`, `PPHDAM`, Guatemala `PPNGS` residual (AMM capacity files without address).
5. **Phase E** used Dominican Stage 3 results from 4ba69d6 for its energy-side link values, because the first Stage 3 run of this job had no Dominican solution when the check ran.
6. Branch `job/fix-run`, base `4ba69d6`. Commits of this job: `ceb7d4d` (Phase A work in progress), `edd2b51` (Phase A), `a399f18` (Phase B), `f0b5485` (Phase C), `fdd6092` (Phase D work in progress), `ad3dc30` (Phase D), `a5ca980` (Phase F: REPORT, GAPS, CHANGES), and a last commit that writes these hashes. PR #11 description has a section "LAC_FIX_RUN2" (taken from CHANGES); the PR stays draft.

## Per decision

**D-ECU1 and D-ECU2 (Ecuador crude).** `EXTT_CRU` upper limit 2026-2030 from BCE field production (Programacion Macroeconomica 2026-2030, Tabla 2) x 5.778689 GJ/bbl: 972.55, 976.60, 989.89, 1,004.91, 1,009.54 PJ (before: 929.41 every year to 2030, then 729.80 and 631.97); held at 1,009.54 from 2031; lower = 0.999 x upper (D7a). `PROCRU` limits 0 and 999,999 every year (before 330.92 / 327.61 in 2021, 332.57 / 329.25 from 2024). `DIST_CRU` limits 0 and 999,999 every year (2023 upper was 0). `REF_*` limits scaled to the target T(y): BCE processed crude 308.99, 325.73, 308.44, 262.75, 228.49 PJ (2021-2025) and MDEP-BCE refinery loads 271.60, 312.05, 340.94, 340.94, 340.94 PJ (2026-2030), held from 2031; recomputed T within 0.5 percent of F1 in every year. `E5EXPCRU` 2031-2050 = 655.88 PJ (before falling to 0 from 2038). Results (BAU): extraction 996.41 (2021), 1,004.22 (2024), 928.48 (2025), 972.55 (2026), 1,008.53 PJ (2030 on); exports 683.75, 733.13, 690.93, 698.07, 663.24 PJ; imports 0 except 5.89 PJ in 2026 (0.6 percent of production); balance within 0.004 PJ in every year and scenario. Refinery crude use runs at the lower band of the `REF_*` rows: 300.84 PJ against T 308.99 (2021), 333.41 against 340.94 (2030 on).

**D1.** `PPHD` CapacityToActivityUnit 31.536 added: new `PPHD` capacity 79.1 GW in 2021-2024 and 576.7 GW over the horizon before, 0 after.

**D2.** Config changes in `history_plan.csv`: 110 Electrical Overwrite rows with BAU transport history (Costa Rica 36, Guatemala 54, Honduras 20) plus 4 history-only cap rows (Costa Rica `PWRSUG`, Honduras `TRBPUGSL`), 4 Costa Rica 2021 elements (`PWRBMS`, `PWRHYDROR`), Dominican `PPDBGS` and `PPDHYD` history elements, 4 Jamaica SmartGrid multiplier rows. Costa Rica NDCNEW and LTSNEW now solve with BAU's `PWRSUG` history cap of 0 and build no `PWRSUG` in 2021-2024 (before 1.24 and 1.79 GW). Final demand per fuel through 2024: equal in every country (largest spread 0.00005 PJ, rounding). Stage 2 T11a: 0 years (before 1). D2f: Dominican `PPDHYD` capacity factor formula now includes 0.0036; the resulting factor of 4.22 made Stage 3 infeasible (repair below). Repairs: Dominican `PPDBGS` capacity factor from IRENA, `PPDHYD` activity limit from UN statistics, `PPDBIM` history kept (GAPS 2).

**D3.** 129 cells written (Honduras 57: 2019 factors of `PPFOI`, `PPGTDSL`, `PPICEDSL`, `PPCOK`, `PPBIM` from BEN 2019 efficiencies and the inventory's IPCC 2006 Table 2.2 factors; Dominican Republic 66: 2018-2022 factors of `PPCOA`, the three natural-gas rows and `PPICEFOI` from the NID 1998-2022 fuel use, AR5 CO2e factors and CNE gross generation; Ecuador 6: `PROCRU` CO2 and CO2e 2022 from the NID, 0.0038237 and 0.0038341 Mt/PJ). Examples: Dominican `PPICEFOI` 2022 0.17028 to 0.246886; `PPCOA` 2022 0.295152 to 0.306249; Honduras `PPCOK` CO2 2019 0.341556 to 0.305161. The other 188 row-years carry an ASSUMPTION sentence with the IPCC 2006 default range (39 sentences). 7 row-years matched their source.

**D4.** Withdrawn (20 November). No Jamaica overwrite line, no stage script change. Jamaica `PPHROR` new capacity is now 34.30 MW in every scenario (12.90, 7.10, 11.10, 2.10, 1.10 MW in 2027-2032; none in 2024-2026), against 34.45 MW before: D13 removed the cause.

**D5.** Honduras `PPBGS` CapitalCost 7,269.10 USD/kW in every year 2018-2050 (before 5,390.58 in 2021 falling to 3,870.85 in 2050). Source R1F-11 (IRENA 2012 biogas) with BEN-004 (US CPI-U).

**D6.** Guatemala `DIST_FLEXFUEL` VariableCost = r(y) x `DIST_GSL`; r = CEPEA hydrated ethanol (R$/L, annual mean of weekly values) / ANP gasoline A realization price without taxes (monthly bulletin values, each found on its cited page), per GJ with ANP heating values (6,300 and 10,400 kcal/kg): 1.4875 (2019), 1.7229, 1.6322, 1.2505, 1.2072, 1.2392 (2024); 2018 takes 1.4875; from 2025 the mean 1.432409. 2024: 20.80 to 27.40 USD/GJ; 2030: 21.54 to 32.80 USD/GJ.

**D7a.** 0.999 written in 353 formula cells of 26 rows (Dominican Republic 19, Jamaica 7) and in Ecuador `EXTT_CRU`. All 27 rows kept at 0.999: B1 and Stage 3 solves OPTIMAL with them (the Dominican Stage 3 infeasibility was traced to `PPDHYD`, and a test solve with every Dominican band back at 0.98 stayed infeasible; `logs/dr_testsolve.jsonl`). Jamaica `REF_FOI` upper limit from 2024 moves with its lower band (upper = lower x 1.01).

**D7b.** No cell change: ETED Plan de Expansion 2021-2035, Tabla 102 and footnote 35 (PDF p.306) states transmission O&M at 0.5 percent of investment, the value of J233. Other published shares in GAPS 3.2.

**D8.** Cause: the Stage 2 overwrite gave the same 2024-2026 hydro shares (40.31 + 2.84 percent) to every scenario, applied to Stage 0 denominators 12 to 14 percent larger in the policy scenarios, then frozen in PJ (`gua_hydro_trace.md`). Fix (step DS1): 2025 and 2026 shares per scenario = AMM 2025 hydro 5,473.52 GWh (19.704670 PJ, held in 2026) / that scenario's Stage 0 denominator (BAU 45.9803 and 48.9790 PJ; NDCNEW 51.6801 and 55.8979; LTSNEW 51.6801 and 55.8861), split 40.31 : 2.84; non-hydro plateau shares scaled to keep 100 percent. Guatemala hydro 2026: BAU 21.13, NDCNEW 24.12, LTSNEW 24.115 PJ before; 19.705 in all three after. 2030: 24.29 / 27.28 / 27.28 before, 22.864 in all three after.

**D9, D10.** No separate change; Costa Rica `E5INDCOA` unchanged.

**D11.** Phase E below.

**D12.** Ecuador OperationalLife for the 36 capital-cost technologies (`research/d12_lives.md`): `ELE_TRANS` 45 and `ELE_DIST` 35 years (ARCONEL-004/24 Anexo 1 Tabla 3); PV and wind 25 (Tabla 2 legend); hydro above 50 MW 50, 5 to 50 MW 40, 0.5 to 5 MW 33 (Tabla 2, civil works); biomass steam 30, industrial gas turbines 20 (Tabla 2, electromechanical); oil, crude, LPG and biogas engines 25 (ARCERNNR cost of service 2021, Cuadro 1); geothermal 20 (CCG kit); electrolysis 30 (PLANMICC, IRENA 2020); storage 15 (NREL ATB 2024); `PRONGS` 25 (Ley de Hidrocarburos, ASSUMPTION). Before: 31.536 or 31.54 years for plants, 1 year for grid, storage and hydrogen. Ecuador grid new capacity 2021-2050 (BAU): `ELE_TRANS` 3,445.5 to 140.3 PJ/yr, undiscounted capital 98,786 to 4,022 MUSD; `ELE_DIST` 3,024.2 to 123.1, 173,299 to 7,056 MUSD. 26 rows added to `starter_kit_deviations.csv`.

**D13.** CapacityToActivityUnit 31.536 for 97 power plants (Costa Rica 10, Dominican Republic 29, Guatemala 15, Honduras 20, Jamaica 15, Ecuador 8). Power-plant new capacity over the horizon (BAU / NDCNEW / LTSNEW, GW): Costa Rica 5.371 / 6.908 / 8.609 to 5.307 / 5.652 / 6.791; Dominican Republic 22.761 / 29.208 / 40.494 to 21.672 / 27.884 / 39.101; Guatemala 7.537 / 10.971 / 26.190 to 7.541 / 11.156 / 26.270; Honduras 7.507 / 9.899 / 16.363 to 7.446 / 9.821 / 16.248; Jamaica 1.348 / 3.503 / 5.517 to 1.332 / 3.474 / 5.478; Ecuador 592.9 / 592.2 / 600.0 to 16.9 / 16.3 / 23.2 (mostly D1). The Costa Rica policy decrease also reflects the transport history alignment.

## Gates and tests

- Gate A: PASS (58 sources, 1,330 proposal rows; every source file present with matching SHA-256).
- B3 write check: PASS (every written cell at target; changes only at listed and dependent cells; no formula without a stored value; every other A-O and config workbook byte-identical; Stage 2 CSVs changed only on listed lines). Writer unit tests: 4 OK, safe-save tests 3 PASS.
- C2 keyed comparison: 0 unexplained differences (`recompile_diff_summary.csv`). B1 solves: 19 of 19 OPTIMAL (after repair C1-1).
- Stage 0: 18 of 18 OPTIMAL, tests 10 of 10. Stage 1: 13 of 13. Stage 2: hard 7 of 7, soft T8 65, T9 87, T11a 0. Stage 3: tests 10 of 11 (T4, 40 Guatemala cells, the documented `--skip-orphan-cap Guatemala` effect), 18 of 18 OPTIMAL, RE targets 24 of 24, share match 7,923 pass, 66 warnings, 9 failures (before 7,906 / 84 / 8).
- First Stage 3 run: Dominican Republic 3 of 3 UNDEFINED; test solves showed the 2025-2050 upper pins insufficient in total because Stage 0 had run `PPDHYD` at 74 to 193 PJ with the 4.22 capacity factor; repair and one full re-run of Stages 0 to 3.

## fix_checks.csv (DS2)

| Check | Result |
|---|---|
| History PP activity through 2024 (0.05 PJ) | pass Guatemala, Honduras, Jamaica; FAIL Costa Rica (8), Dominican Republic (25), Ecuador (14) |
| History final demand per fuel | pass all six (0.00005 PJ) |
| Stage 2 T11a | 0 years |
| History builds against `history_builds.csv` | pass Guatemala; FAIL Costa Rica 5, Dominican Republic 8, Ecuador 12, Jamaica 3 |
| Ecuador `PPHD` new capacity 0 | pass |
| Ecuador crude balance within 0.5 PJ | pass (0.004 PJ) |
| Ecuador imports above 1 percent of production | none |
| Jamaica `PPHROR` at most 34.4 MW, none in 2024-2026 | pass (34.30 MW, three scenarios) |
| Jamaica hydro identical (0.05 PJ) | pass (0.022) |
| Guatemala hydro identical (0.05 PJ) | FAIL in 2029, 2041, 2043 (largest 1.143 PJ) |
| D7a rows | 27 at 0.999, 0 put back |

Hydro output by country (PJ, 2026 / 2030 / 2040 / 2050), BAU: Costa Rica 35.30 / 35.28 / 35.28 / 35.28; Dominican Republic 4.35 every year; Ecuador 91.88 / 93.72 / 93.11 / 93.11; Guatemala 19.71 / 22.86 / 22.86 / 22.86; Honduras 13.77 / 13.77 / 13.61 / 13.61; Jamaica 0.40 / 0.95 / 1.00 / 1.00. Policy values are in `fix_checks_detail.csv` (within 0.2 PJ of BAU except Ecuador, up to 1.0 PJ).

## Results compared with 4ba69d6 (`results_compare.csv`)

| Country | Scenario | Objective before | Objective after | RE 2030 / 2035 / 2050 after | Emissions 2030 / 2050 after (before) |
|---|---|---|---|---|---|
| Costa Rica | BAU | 114,660 | 114,537 | 0.894 / 0.894 / 0.894 | 23.72 / 34.04 (23.72 / 34.04) |
| Costa Rica | NDCNEW | 104,255 | 104,231 | 0.897 / 0.900 / 0.900 | 22.16 / 27.88 (22.16 / 27.88) |
| Costa Rica | LTSNEW | 95,536 | 95,511 | 0.937 / 0.990 / 0.990 | 19.50 / 8.43 (19.50 / 8.43) |
| Dominican Republic | BAU | 413,922 | 411,689 | 0.191 / 0.231 / 0.339 | 72.60 / 112.92 (72.60 / 112.87) |
| Dominican Republic | NDCNEW | 433,128 | 430,947 | 0.421 / 0.750 / 0.750 | 58.88 / 61.60 (59.10 / 61.73) |
| Dominican Republic | LTSNEW | 457,352 | 455,181 | 0.421 / 0.750 / 0.990 | 58.90 / 17.44 (59.10 / 17.44) |
| Ecuador | BAU | 1,765,128 | 268,341 | 0.768 / 0.778 / 0.809 | 128.76 / 180.74 (131.86 / 182.77) |
| Ecuador | NDCNEW | 1,754,223 | 257,975 | 0.776 / 0.800 / 0.809 | 124.06 / 163.90 (127.05 / 165.86) |
| Ecuador | LTSNEW | 1,749,295 | 250,736 | 0.776 / 0.800 / 0.990 | 123.79 / 117.34 (126.69 / 117.70) |
| Guatemala | BAU | 360,672 | 360,932 | 0.513 / 0.555 / 0.626 | 75.92 / 157.79 (75.21 / 156.46) |
| Guatemala | NDCNEW | 347,103 | 347,969 | 0.658 / 0.750 / 0.750 | 66.55 / 125.43 (65.08 / 125.14) |
| Guatemala | LTSNEW | 345,335 | 346,140 | 0.658 / 0.750 / 0.990 | 68.18 / 66.56 (66.72 / 66.55) |
| Honduras | BAU | 104,975 | 104,918 | 0.570 / 0.590 / 0.647 | 39.22 / 59.21 (39.22 / 59.21) |
| Honduras | NDCNEW | 103,198 | 103,142 | 0.648 / 0.750 / 0.750 | 36.34 / 52.68 (36.34 / 52.68) |
| Honduras | LTSNEW | 100,755 | 100,692 | 0.648 / 0.750 / 0.990 | 36.28 / 23.90 (36.28 / 23.90) |
| Jamaica | BAU | 64,972 | 65,087 | 0.139 / 0.183 / 0.294 | 12.60 / 15.31 (12.65 / 15.35) |
| Jamaica | NDCNEW | 61,507 | 61,615 | 0.391 / 0.750 / 0.750 | 11.05 / 11.44 (11.09 / 11.48) |
| Jamaica | LTSNEW | 59,478 | 59,582 | 0.391 / 0.750 / 0.990 | 10.98 / 4.76 (11.02 / 4.80) |

Objective in each model's cost unit (OFL_Cost or cost); emissions are the sum of AnnualEmissions. The Ecuador objective falls by about 1.5 million because `PPHD` (D1) and the one-year grid and plant lives (D12) no longer rebuild capacity. Guatemala's RE share 2030 falls (0.686 to 0.658 in the policy scenarios) because hydro in 2025-2030 now follows the sourced AMM generation instead of a share of a larger denominator. The split of each objective change into cost terms was not computed: Stage 3 results hold no cost by technology, and the 4ba69d6 solver outputs are not kept. The five largest new-capacity changes per country are in `results_compare.csv` (metric "new capacity summed over the horizon").

## Tests and solve statuses

All in `stage_logs/` (second run) and `stage_logs/run1/` (first run): `stage_status.jsonl`, `solves_stage0.jsonl`, `solves_stage3.jsonl`, one log per step.

## Cross-sector check (Phase E, `cross_sector_check.md`)

- 19 sector models: as cloned, the 18 B1-based runners stop because `Executables/` is gitignored; with an empty `Executables/` in a scratch copy, 17 solve OPTIMAL in every activated scenario; `RD_AFOLU` is infeasible in all three scenarios (its tracked output does not come from its current inputs). `GUA_AFOLU` solves as cloned. Ecuador's four sector models give BAU results different from their tracked outputs (for example ECU_WASTE discounted cost 17,138 against 6,094 tracked).
- Scenarios: BAU aligned everywhere; NDCNEW maps to an NDC or NDP scenario in 17 models (often two candidates) and is missing in JAM_WASTE; LTSNEW is missing in 13 models; only JAM_TRANSPORT uses NDCNEW and LTSNEW names. Years match except Costa Rica (sector 2018, energy 2021) and GUA_AFOLU (2016).
- Links: Costa Rica's energy model produces about 41 to 43 PJ of ethanol a year, about 6 to 7.5 times what the cane of CR_AFOLU could supply (indicative conversion); CR_WASTE recovers 15,000 t CH4 a year while the energy model has no biogas; biogas power and landfill recovery do not agree in the Dominican Republic, Guatemala and Ecuador; RD_AFOLU and HON_AFOLU hold their own copy of the energy system (Dominican firewood ratio 0.72 to 0.80; Honduras equal in 2021-2022, different in 2023-2024); land models hold areas only elsewhere, so biomass units cannot be reconciled.
- Costs: IPPU has no capital cost in BAU but non-zero capital cost in all five policy IPPU scenarios (refrigerant and HFC technologies); every ECU_AGR and ECU_USCUSS cost value is exactly 1.0.
