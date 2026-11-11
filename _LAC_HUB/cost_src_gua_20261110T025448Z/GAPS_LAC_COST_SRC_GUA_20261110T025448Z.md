# GAPS LAC_COST_SRC_GUA 20261110T025448Z

Guatemala energy model, sourced cost proposals. This file lists every judgement call, each ASSUMPTION with its leads, changes above 25 percent, blocked sources, known-limitation candidates, items left unchecked and incidents.

## 1. Judgement calls and reasons

### Fuel supply rows

1. WEO 2025 table number. The fuel price table is Table 2.3 "Wholesale fossil fuel prices by scenario" on page 109, not Table 2.32. Units USD (MER, 2024); columns 2024, then 2035 and 2050 for CPS, STEPS and NZE. Values were interpolated linearly 2024 to 2035 to 2050. The model ends in 2050, so the "flat after the last year" rule never applies.
2. Projected years start in 2026 for every row. All three benchmarks (Brent, Henry Hub, South African coal) have an observed 2025 annual value, so 2025 is a history year for every row. Where the chosen local point has no 2025 value, 2025 is "history from ratio" (r times the observed 2025 benchmark). Rule F4's "2025 where no observed 2025 value exists" was read as the benchmark value.
3. Large joins at 2025 to 2026, not smoothed (rule F4). Brent fell from 80.52 (2024) to 69.14 (2025), while the projection starts from B(2024) times the WEO ratio. For Brent-based rows the step is plus 19.8 percent (STEPS), 22.3 (CPS) and 6.9 (NZE). For `DIST_COK` it is plus 22.6 percent and for `EXTT_CRU` plus 24.3 percent. For `DIST_NGS` it is minus 27.2 percent because Henry Hub rose to 3.52 in 2025. For `DIST_COA` it is plus 9.8 percent.
4. Projections anchor on r times B(2024), not on the observed local 2024 value (rule F4). For case 1 rows the projected level therefore differs from the 2024 observation. Example: `DIST_COA` 2024 observed 5.65, while r x B(2024) = 0.050379 x 105.8 = 5.33 USD/GJ.
5. Coal benchmark. The World Bank Pink Sheet carries no Colombian coal series. Guatemala's coal is all Colombian (Banguat KF-116 origin file, GUA-004), and Colombian coal trades in the Atlantic basin. The observed benchmark is therefore Pink Sheet "Coal, South African" (fob Richards Bay, 6,000 kcal/kg NAR). The WEO series is "Steam coal, European Union", the import market that Colombian and South African coal serve, adjusted to 6,000 kcal/kg.
6. Petroleum coke benchmark. Rule F4 assigns oil products to Brent, and petroleum coke is an oil product (HS 2713), so Brent is used. Over 2018 to 2025 the import CIF tracks Atlantic coal more closely: the coefficient of variation of the ratio is 0.104 against coal and 0.165 against Brent. With the coal benchmark, `DIST_COK` STEPS 2050 would be about 0.03195 x 105.8 x 66 / 112 = 1.99 USD/GJ, against 3.73 with Brent. This is a candidate for Luis to revisit.
7. Natural gas series. US-sourced and Henry Hub-indexed gas is confirmed by the PEG-5 tender bases (GUA-006, numeral 5.3.3: gas price = Henry Hub plus bidder adder plus guarantee factor). So the row uses EIA Henry Hub and the WEO United States gas price.
8. Gasoline. Two wholesale import parity rows are published, regular (22.11 USD/GJ) and superior (23.36). Regular is used: it is the first published row, it has the larger import volume, and section 5 of the brief lists 22.1. A volume-weighted mix would be about 2.5 percent higher. The MEM import volumes for that weighting were not re-sourced in this job.
9. LPG. The 25 lb residential cylinder wholesale import parity (13.77 USD/GJ) is used, as in section 5 of the brief. The automotive LPG wholesale point is 18.24 USD/GJ (plus 32.4 percent), recorded in `price_points_2024.csv`.
10. Kerosene. The Banguat import CIF (51.23 USD/GJ) covers 14,774 kg in the whole year, a sample volume and not a market price. No wholesale or export point exists. The MEM Guatemala City consumer price net of IDP and IVA (31.26 USD/GJ) is used as the closest pre-tax point, with its own 2018 to 2024 history (case 1). It is a retail price, so it includes retail margin.
11. Case 2 rows (diesel, fuel oil, gasoline, LPG). r = mean of Banguat import CIF / Brent over 2018 to 2025, times the 2024 ratio of the chosen point to the Banguat import CIF. The Banguat CIF is used for the ratio, not the MEM structure CIF, because it is the series with the history.
12. `EXTT_CRU`. The brief allows a crude export price "if easy to source". Banguat's exports-by-tariff-line files (KG-103, 2018 to 2025, line 2709001000) give it directly, and their FOB basis is confirmed by Banguat Cuadro 1. The value is 389.85 USD/t in 2024, or 9.216 USD/GJ at 42.3 GJ/t (IPCC). Proposing it fills an empty cell; see the known-limitation note in section 5 on pricing an export row as a cost.
13. `DIST_NGS` level. 7.763 USD/GJ gross is kept from LAC_LOCAL_PRICES as an ASSUMPTION and divided by 0.9 to 8.626 net. Because r is the 2024 ratio alone (case 3), the ratio method also scales the liquefaction, shipping and regasification adder with Henry Hub. The STEPS 2050 value (18.04 USD/GJ net) is therefore likely high. This row feeds only `PPNGS`, which has no residual capacity.
14. Supply-row FixedCost and CapitalCost stay 0 or empty, and no proposals were written for them. A supply row carries its whole price in VariableCost.

### Plants and imports

15. P2 against Luis's "keep" decision. The decision of 10 November keeps current plant values "and each value gets a refined source", while rule P2 says `replace` where no source gives the number. P2 was applied as written: matched values are kept, and unmatched values are replaced by the first source in P1 order. Every `replace` row keeps the current value in `current_value`, so LAC_COST_WRITE can still choose to keep it.
16. Dollar years. Plant costs are proposed as published, in each source's dollar year, without deflation, so that a kept value and its source show the same number. The dollar year is recorded in `plant_costs.csv` (`source_dollar_year`). Fuel prices and the import price are real 2024 USD.
17. Newer editions. The Guatemalan generation plans are one MEM series: PEGT 2018-2032, PEGT 2020-2034, PEG 2020-2050, PEIG 2022-2052, and PEIG 2026-2050 (newest). Where a value matched an older edition, the newest edition that covers the technology is proposed (class `matched, newer edition`). PPBGS capital: 5000 (PEG 2020-2050) becomes 2600 (PEIG 2022-2052), because PEIG 2026-2050 has no biogas candidate. PPHDAM capital: 2600 becomes 3500 (PEIG 2026 Hidro de embalse). PPHROR fixed: 54 (small hydro GDR row) becomes 34 (PEIG 2026 Hidro de pasada). PPWNDON capital: 1500 becomes 1600.
18. Order of sources for `replace`. For each value the first source in P1 order covering the technology was used:
    - IRENA (newest 2024 edition proposed, 2022 value in the derivation).
    - WEO: the WEO 2023 cost table needs an IEA sign-in, so WEO 2025 Annex B Tables B.4a and B.4b are used. They cover only the United States, EU, China and India and give no separate O&M, so the United States values are used, for capital only.
    - The MEM national plan.
    - NREL ATB.
    Where IRENA gives a Central America and Caribbean value, it is preferred to the global average (PPPVT 1375, PPHROR 3444).
19. Hydro fixed O&M (PPHDAM). IRENA gives hydro O&M only as 2 to 2.5 percent of capital cost (20 to 60 USD/kW-yr), not one value, so the national plan value of 50 was used. It lies inside the IRENA range.
20. PPDSL and PPFOI capital. No source covers oil-fired engines in the P1 list before the national plan. PEIG 2026-2050 "Combustion interna" (1400 USD/kW, listed as gas-fired) is used for both diesel and fuel oil engines. PPFOI fixed and variable O&M match the EIA 2020 cost study internal combustion engine case exactly (35.16 USD/kW-yr, 5.69 USD/MWh).
21. PPDSL fixed 31.6 and variable 6.0 (USD/MWh) equal the coal candidate of PEG 2020-2050, not a diesel source. They were treated as not matched.
22. Geothermal variable O&M. The current value is 0, and the sources give EIA 1.16 and PEIG 5 USD/MWh. IRENA states geothermal O&M as a fixed amount only. The PEIG value (5 USD/MWh, 1.389 USD/GJ) is proposed, from the same table that matches the fixed O&M (151).
23. Zero variable O&M for PV, wind and hydro is matched to the EIA 2020 cost study Table 2 (0 USD/MWh). ATB publishes no variable O&M row for these technologies.
24. PV paths.
    - The 2024 to 2050 values of PPPVT2, PPPVTS and PPPVD equal ATB 2023 Moderate, Market (UtilityPV, PV-Plus-Battery, CommPV), so ATB 2024 is proposed as the newer edition for 2022 to 2050.
    - ATB 2024 starts in 2022. For 2018 to 2021 the current value is kept where it matches ATB 2021 or 2023 within 2 percent; otherwise the ATB 2021 value is used, with 2018 held at 2019.
    - PPPVD 2018 to 2020 current values match ATB 2021 ResPV, not CommPV. They were replaced with CommPV to keep one technology per path.
    - The path changes dollar year at the join, from 2019 USD (ATB 2021) to 2022 USD (ATB 2024).
25. ATB class. Class 5 was used for UtilityPV, PV-Plus-Battery and CommPV. In ATB 2023, CAPEX and FOM are identical across classes for these products.
26. PPPVDS. No distributed PV-plus-storage product exists in IRENA, WEO, the MEM plans or ATB, so it is an ASSUMPTION. The value is the PPPVD proposed cost times the ATB PV-Plus-Battery / UtilityPV ratio of the same year.
27. Electricity imports (rule E1). The proposed value is 62.02 USD/MWh (17.228 USD/GJ). It is volume-weighted from the AMM monthly market analyses of 2024: Mexico 55.75 USD/MWh on 1,623.39 GWh, MER 121.68 USD/MWh on 170.57 GWh, total 1,793.96 GWh, which equals the AMM annual 1,793.97 GWh.
    - The AMM annual MER average (158.35) was not used: Mexico supplies about 90 percent of imports.
    - The customs value (UN Comtrade: Mexico exports 78.66 USD/MWh FOB; Guatemala imports CIF value / AMM volume 78.58) is about 27 percent higher. It probably includes the unpublished firm contract price (Energia del Caribe, 56 percent of imports). It is kept as the check and the top of the range.
    - The value is held flat in all years (ASSUMPTION for every year except 2024). The 2024 model activity (6.175 PJ = 1,715 GWh) differs from the AMM 1,794 GWh; the quantity is outside this job.
28. Proposals format. `proposals.csv` carries one extra trailing column, `current_effective_bau`, with the value the BAU compile uses. Most workbook rows hold only a 2018 value with a projection mode such as Flat or "Percent growth of incomplete years", so `current_value` (the workbook cell) is empty for later years.
    - LAC_COST_WRITE will need to switch those rows to a year-by-year projection mode (for example User defined) to write a path.
    - LAC_COST_WRITE will also need to change the plant VariableCost unit label from "M US$ / GWh" to "M US$ / PJ".

## 2. ASSUMPTION rows and the leads tried

| Technology | Rows | Leads tried (search_log.csv) |
|---|---|---|
| `DIST_NGS` (all years, three scenarios) | 99 | Banguat KF-103 2024 (no 2711.11 or 2711.21 line); UN Comtrade 2024 (no gas record); MEM import cost tables (no gas); PEG-5 bases (formula only); AMM and EOR documents (2.6 MW plant on associated gas, no price; AMM fuel declarations behind a login); EIA LNG export prices (check value only) |
| `IMP_ELE` (all years except 2024) | 32 | AMM Informe Estadistico 2024; AMM monthly analyses; EOR annual and statistical reports (2021 only); EOR operational plan (marginal costs, not import prices); CNEE Compendio 2025 (volume only); CNEE Tableau (blocked); web searches for CRIE/EOR prices and the Mexico contract price; national plans (no import price projection); UN Comtrade both directions |
| `PPPVDS` (CapitalCost and FixedCost, all years) | 66 | ATB 2020 to 2024 all PV and storage rows; IRENA 2022 and 2024; WEO 2025 Annex B; MEM plans 2018 to 2026 (PEIG battery add-on is utility-scale); EIA 2020 cost study (utility PV plus battery, used as check) |

The three ASSUMPTION sentences sit in `proposals.csv` and pass the gate 5 word check.

## 3. Proposed changes above 25 percent (2024) and likely cause

| Row | Current | Proposed | Change | Likely cause |
|---|---|---|---|---|
| `DIST_COA` | 3.448 | 5.654 | +64 % | the current value grew 1.9 percent a year from a 2018 value of 2.49; the observed 2024 Banguat CIF at the PEG-5 calorific value is higher |
| `DIST_LPG` | 29.47 | 13.77 | -53 % | the current value equals a Dominican Republic proxy (28.64 in 2018), not a Guatemalan wholesale price |
| `DIST_COK`, `DIST_KER`, `EXTT_CRU`, `IMP_ELE` | 0 or empty | 3.20, 31.26, 9.22, 17.23 | new | placeholders or empty cells filled |
| plant VariableCost (PPBGS, PPBIM, PPCOA, PPDSL, PPFOI, PPNGS) | 0.0045 to 0.0097 | 1.11 to 1.67 | about x277.78 | unit slip, USD/kWh entered as USD/GJ; after the unit conversion the changes are 0 percent (PPBGS, PPFOI), -6 (PPCOA), -17 (PPDSL), +10 (PPNGS) and -59 (PPBIM, IRENA bioenergy 4 USD/MWh against the current 9.65) |
| `PPGEO` VariableCost | 0 | 1.389 | new | PEIG geothermal variable O&M 5 USD/MWh |
| `PPBGS` CapitalCost | 5000 | 2600 | -48 % | newer MEM plan edition (PEIG 2022-2052) halved the biogas candidate cost |
| `PPCOA` FixedCost | 61.4 | 31.6 | -49 % | no source gives 61.4; MEM plan coal candidate 31.6 |
| `PPDSL` CapitalCost | 448 | 1400 | +212 % | 448 matches no source and is low for a diesel plant (brief note); PEIG internal combustion engine 1400 |
| `PPDSL` FixedCost | 31.6 | 20 | -37 % | the current value is the coal row of PEG 2020-2050 |
| `PPFOI` CapitalCost | 1908 | 1400 | -27 % | no source gives 1908 (EIA engines 1810); PEIG engine 1400 |
| `PPHDAM` CapitalCost | 2619 | 3500 | +34 % | newest MEM plan edition |
| `PPHDAM` FixedCost | 33.54 | 50 | +49 % | no reservoir hydro source gives 33.54; PEIG 50 |
| `PPHROR` CapitalCost | 1870 | 3444 | +84 % | no source gives 1870; IRENA Central America small hydro 3444 |
| `PPHROR` FixedCost | 54 | 34 | -37 % | newest MEM plan edition |
| `PPPVT` CapitalCost | 949 | 1375 | +45 % | no source gives 949; IRENA 2024 Central America and Caribbean utility PV 1375 (global 691) |
| `PPPVDS` FixedCost | 33.94 | 52.30 | +54 % | ASSUMPTION ratio from ATB PV-Plus-Battery fixed O&M |
| `PPPVDS` CapitalCost 2050 | 1036 | 1570 | +51 % | ATB 2024 battery ratio stays high to 2050 (1.69) |
| `DIST_NGS` STEPS 2050 | 16.70 | 18.04 | +8 % | see judgement 13 |
| PV paths 2022 and 2023 | | | up to +21 % | ATB 2024 has higher 2022 to 2023 PV costs than ATB 2023 |

## 4. Sources blocked or paywalled

- The IEA WEO 2023 power generation technology cost dataset (xlsx) needs an IEA account sign-in. It was not downloaded, and WEO 2025 Annex B was used instead.
- The IRENA publication HTML page returned HTTP 403; the PDFs downloaded directly.
- atb.nrel.gov no longer resolves. The ATB pages were saved from atb.nlr.gov, and the data files from the OEDI S3 bucket.
- The CNEE Tableau "Informe Estadistico TI 2021-2025" is behind an AWS WAF captcha.
- The AMM participant area (fuel declarations) needs a login.
- No EOR or CRIE 2024 annual MER price report was found online.

## 5. Known-limitation candidates

- `EXTT_CRU` is an export row. A VariableCost equal to the export FOB price adds the export value to total cost without matching revenue (proposals for the Guatemala workbook, Primary Techs, `EXTT_CRU`).
- Plant costs mix dollar years from 2018 USD to 2024 USD (see judgement 16). A later step could deflate all plant costs to 2024 USD with CPI-U.
- `DIST_FLEXFUEL` VariableCost 47.1 USD/GJ (Primary Techs) has no source in the papers. It is outside this job's scope.
- Data in Brief Table 53 (Dominican Republic) shows the same diesel, gasoline and LPG values as Guatemala's Table 57, so these were regional proxies. Other countries' workbooks may carry the same proxies.
- `IMP_ELE` activity in 2024 (6.175 PJ = 1,715 GWh) is below the AMM 2024 import volume of 1,793.97 GWh (and the CNEE Compendio's 1,815.6 GWh).
- PEIG 2026-2050 hydro variable O&M values (22.73 run-of-river, 60.19 reservoir USD/MWh) look like a different quantity, perhaps water charges. They were not used.
- The AMM weekly dispatch workbooks give plant variable costs in USD/MWh. These could cross-check the plant variable O&M plus fuel.
- The CNEE Compendio Estadistico 2025 gives a 2024 spot price of 116.5 USD/MWh, a possible check for import and plant economics.
- The ELE_TRANS, ELE_DIST, HYD_G_PROD and HYD_DIST cost rows (Secondary Techs) have no source in Table 57. They are outside this job.

## 6. Left unchecked

- The newest EIA capital cost study (AEO2025 edition) was not checked as a newer edition for the PPFOI fixed and variable O&M match (EIA 2020 study, 2019 USD).
- Lazard and OLADE cost tables were not searched.
- The WEO 2025 dollar year for Annex B capital costs is not printed in Table B.4. It is taken as 2024 USD, the report's convention.
- The gasoline regular and superior volume mix (judgement 8).
- Pre-2024 electricity import prices. The 2024 price is used for all years.
- The 2025 CPI-U annual average (321.943) is computed by BLS with October 2025 missing (lapse in appropriations). It affects only the 2025 deflation (about 0.1 percent).
- Data in Brief Table 57 and Suplementary `Costos_GUA` carry no source column, so no paper lead pointed to a specific document for any plant value.

## 7. Incidents

- The first setup command was interrupted when the session dropped. The clone had completed; the remote, branch and job folder were then created and checked.
- The national-plan sub-task wrote its search log with row numbers instead of model codes. They were mapped to model codes before assembly.
- The paper text extracts were first written under `work/`. They were moved to `downloads/paper/` (not tracked) so that no draft paper text is committed.
- Sub-tasks deleted downloads they opened but did not cite: ATB 2020 and 2022, AEO2018, AEO2022, the current EMM assumptions, and the CNEE Compendio 2025 (64 MB). Each is logged in `search_log.csv`.
- Two commits instead of one.
  - After the first commit, `git diff --check` flagged trailing whitespace. Python on Windows had written CRLF line endings; they were converted to LF and the commit was amended before the push.
  - After the push, the check still flagged two lines with real trailing spaces (one script line and one pandas printout).
  - Amending the pushed commit would have needed a force push, and that history rewrite was refused by the session's permission guard. The fix therefore went into a second commit on the same branch, together with the final gate results and the pull request number in REPORT.
  - Neither commit carries a Co-Authored-By or "Generated with" line.
- The first pass of the paper trail was written before the plant results. Its `needed_change` column was regenerated from the final proposals (`scripts/s2b_update_paper_trace.py`).
