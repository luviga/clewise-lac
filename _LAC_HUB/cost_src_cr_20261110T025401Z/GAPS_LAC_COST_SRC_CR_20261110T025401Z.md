# GAPS LAC_COST_SRC_CR 20261110T025401Z

Costa Rica energy model, sourced cost proposals. This file lists every judgement call, each ASSUMPTION row with its leads, changes above 25 percent, blocked sources, known-limitation candidates, items left unchecked and incidents.

## 1. Judgement calls

Fuel supply rows

1. Product per supply row. `local_prices_2024.csv` carries several products for some rows. I followed the brief's section 5 values: `IMPFOI` uses Bunker (fuel oil), 15.458 USD/GJ, not Bunker Termico ICE 2 (the low-sulphur grade for ICE engines, 14.869, minus 3.8 percent). `IMPKJF` uses jet fuel (22.690), not kerosene (21.023, minus 7.3 percent). `IMPPURGSL` uses RON 91 (20.266), not RON 95 (21.406, plus 5.6 percent). All alternatives are in `price_points_2024.csv`.
2. 2025 is treated as a history year, because EIA publishes full-year 2025 averages for Brent and Henry Hub and the World Bank does the same for coal. Projections start in 2026, and the join step is reported between 2025 and 2026.
3. Rule F3 applied as written for case B rows (chosen point is wholesale import parity, with history only for import CIF). History years other than 2024 use r x benchmark(y), even where an import CIF observation exists for that year (2022, 2023, 2025).
4. Petroleum coke benchmark. F4 names no benchmark for petroleum coke, so I used Brent with the WEO crude oil price, because petroleum coke is an oil product. Over 2018 to 2025 the ratio of the coke price to Brent has a coefficient of variation of 16 percent, against 13 percent for South African coal. With coal instead (r = 0.8116 against World Bank South African coal, WEO European Union steam coal), 2024 r x B would be 3.42 USD/GJ and STEPS 2050 would be 2.01 USD/GJ. The Brent version gives 3.76 USD/GJ in STEPS 2050. The effect is small: industry coke demand is about 4 to 6 PJ, so 1.7 USD/GJ is under 10 MUSD a year.
5. Coal benchmark. Costa Rica's 2024 coal imports are 233 t of anthracite from Peru (149.6 t) and the United States (83.9 t), and 2025 imports are from the United States. WEO 2025 Table 2.3's United States steam coal series is a mine-mouth price plus transport, not an import price. I used the European Union series, an Atlantic-basin import price at 6000 kcal/kg, for the projection, and World Bank Pink Sheet South African coal (fob Richards Bay, 6000 kcal/kg) as the observed benchmark for r.
6. Natural gas benchmark. Costa Rica has no LNG supply, so there is no contract or regulator document for its gas. I used Henry Hub and the WEO United States gas price because the 2024 ASSUMPTION price is built on Henry Hub (US Gulf LNG). The regional check is the Honduras system operator expansion plan 2026-2035 (HON-016, pp.56 to 57), which builds delivered LNG on Henry Hub. r is case C (2024 ratio alone).
7. WEO table. The fuel price table in WEO 2025 is Table 2.3 "Wholesale fossil fuel prices by scenario", PDF page 109, not 2.32. Units: USD/barrel for crude, USD/MBtu (gross) for gas, USD/tonne at 6000 kcal/kg for coal. Currency: USD (MER, 2024). Years published: 2024, 2035 and 2050, interpolated linearly. Caveat for the method notes: WEO 2025 was written before the 2026 Middle East energy crisis.
8. `IMPCOA` r = 8.93 rests on anthracite lots of 2 to 316 t a year, with unit values of 13 to 112 USD/GJ. The rules give a 2026 STEPS price of 35.5 USD/GJ. The row only matters if the model keeps industry coal demand. Step 7 proposes 0.00667 PJ for 2021, as for every later year.
9. Only the VariableCost of supply rows is proposed (F2: one price per row). The FixedCost of `IMPPURDSL`, `IMPPURGSL`, `IMPFOI` and `IMPLPG` and the CapitalCost of `IMPLPG` (234.55) are listed in `cost_rows_current.csv` with scope `supply row` and left unchanged (see known-limitation candidates).

Plant rows

10. Matching test (P2). A source matches when it is within 2 percent after a stated conversion, at either of two points:
    - the 2021 column, using sources whose cost year is 2021 or earlier, converted to 2021 USD with CPI-U;
    - the 2024 column, using any source, converted to 2022 USD.

    The 2024 column is in 2022 USD because the workbook applies a 1.0800 step from 2021 to 2022 (CPI-U 2022/2021 = 292.655 / 270.970), so its 2022 to 2050 values are 2022 USD.
11. Currency basis kept as in the workbook. Proposed plant values use 2021 USD in the 2021 column and 2022 USD after, the least change. Fuel prices are in real 2024 USD as Luis decided. The mismatch is a known-limitation candidate.
12. Replacement value. The first point value in P1 order. A range alone (for example IRENA's 20 to 60 USD/kW-yr for hydro O&M, or 2 to 6 percent of installed cost for bioenergy O&M) is not counted as a value. Where IRENA supplies the replacement, I used the newest edition (RPGC 2024) as the minor upgrade and kept the 2022 edition value in the derivation.
13. IRENA region choice. Capital costs use the Central America and the Caribbean region. O&M uses IRENA's "Other OECD" (wind) or "OECD" (PV) assumption, because Costa Rica has been an OECD member since 2021.
14. Paths. Replacement rows keep the ATB 2024 shape the workbook already uses, applied to the new 2024 level. Two exceptions:
    - `PWRSPVDTR` capital moves to the ATB UtilityPV Class5 shape. The old rule, a decline of 10.95 USD/kW a year to 2030 then flat, has no source.
    - `PP_SPV_DG` moves to ATB ResPV Class5.
15. `PWRHYDDAM` FixedCost is the mean of the two reservoir candidates in ICE PEG 2020-2035 Tabla 10.7: Hidro 2 con regulacion at 16 and Hidro 3 con regulacion at 48 USD/kW-yr.
16. `PWRDSL` FixedCost keeps the workbook's path shape (ATB NG 2-on-1 Combined Cycle F-Frame 95% CCS), the least change, although that shape does not describe engines.
17. `PWRFOI` and `PWRDSL` both use the ICE medium-speed engine candidate (MMV), the only engine cost in the plan. The ICE plan lists the MMV fuel as bunker.

Electricity imports (added after the first push, on Luis's instruction of 10 November 2026)

20. The brief said Costa Rica has no electricity import technology and that Step 6 should be skipped. `IMPELE` exists with a positive activity upper limit (2.245 to 3.846 PJ) and no cost, so it was priced under rule E1.
21. Price point: ICE DOCSE Informe Anual 2024, page 17, total cost of 2024 regional market imports divided by energy: 206.06 USD/MWh (57.239 USD/GJ). It includes the CMORC transmission charge paid on contract imports (20.63 MUSD), because that is part of the delivered cost. Without CMORC the price is 149.35 USD/MWh.
22. Years other than 2024 hold the 2024 value flat, as an ASSUMPTION. ARESEP's 2025 tariff resolution quotes an ICE projection of 152.66 USD/MWh for 2025 only. It is a one-year tariff estimate, not a multi-year projection, so it is used as the check and not applied. Earlier ICE annual reports (2021 to 2023) were not retrieved for observed history years.

Country task

18. The brief's premise of "0.675 PJ a year" holds for 2021 only. From 2022, `E5INDCOA` is 0.00667 PJ and `E5INDCOK` is 3.713 PJ, both equal to the 2022 balance. Moving the 2021 0.675 PJ into petroleum coke would put 2021 coke 18 percent above customs, so I propose setting 2021 coal to 0.00667 PJ and keeping coke unchanged. The literal move is recorded as an alternative row in `structure_proposals.csv`.
19. The balance's own implied coke factor (3,713.16 TJ / 138.6 kt = 26.79 GJ/t) is lower than IPCC's 32.5 GJ/t. With it, 2021 coke imports give 3.331 PJ against the workbook's 4.091 PJ. Under either factor, the 0.675 PJ of coal is not supported.

## 2. ASSUMPTION rows (179)

- `IMPNGS` VariableCost, 90 rows (3 scenarios x 30 years). Sentences: the 2024 price ASSUMPTION plus the F5 gross-to-net ASSUMPTION. Leads tried:
  - PROCOMER HS 271111 and 271121 (no LNG in 2024; 3 kg of gaseous natural gas);
  - UN Comtrade 2024 (same);
  - a web search for a Costa Rican LNG import price or study (none);
  - the Honduras system operator plan (Henry Hub based delivered LNG, used as the check).
- `PWRDSL` VariableCost, 30 rows, value unchanged at 1.3056 USD/GJ (4.70 USD/MWh). Leads tried: ICE PEG 2020-2035 (fixed O&M only), IRENA 2022 and 2024 (no engines), WEO 2023 and 2025 (no engines), NREL ATB 2024 (no engines). Check: EIA AEO2023 Table 1, internal combustion engine variable O&M 6.40 USD/MWh (2022 USD).
- `PWRFOI` VariableCost, 30 rows, same as `PWRDSL`.
- `IMPELE` VariableCost, 29 rows (every year except the observed 2024), held at 206.06 USD/MWh. Leads tried:
  - a web search for the 2024 regional market import price;
  - CEPAL SICA electricity statistics 2024 (spot prices for other countries only; exchanges in MWh);
  - the EOR transaction reports page (links load by script);
  - ARESEP CVG 2025 resolution (2025 projection 152.66 USD/MWh; 2024 net import cost in colones without volumes);
  - a web search for ARESEP 2024 CVG adjustments;
  - ICE DOCSE Informe Anual 2024 (the 2024 observed price).

## 3. Proposed changes above 25 percent and likely cause

| Row | Parameter | 2024 change | Likely cause |
|---|---|---|---|
| IMPCOA | VariableCost | +345% | Workbook carries a steam coal price; Costa Rica's only coal imports are specialty anthracite lots |
| IMPFOI | VariableCost | +60% | Workbook value is the 2021 level (Table 49: 9.15) grown slowly; 2024 wholesale import parity includes RECOPE landed costs |
| IMPPURDSL | VariableCost | +58% | Same; workbook 12.61 against wholesale import parity 19.97 |
| IMPLPG | VariableCost | +56% | Same |
| IMPPURGSL | VariableCost | +46% | Same |
| IMPAVG | VariableCost | +24% (2030 +48%, 2050 +59%) | Workbook path declines to 26 USD/GJ by 2050; new path follows WEO STEPS crude, nearly flat |
| PWRFOI | CapitalCost | -68% | No source near 4,650.33 USD/kW; 3.3 to 3.6 times the ICE engine cost; 4,650.33 = 13,951 / 3 suggests a mean or sum slip |
| PWRDSL | FixedCost | -56% | Workbook 53 USD/kW-yr has no source; ICE engine candidate is 21 (Dec-2019 USD) |
| PWRFOI | FixedCost | +48% | Workbook 16.3 has no source; same ICE engine value |
| PP_SPV_DG | FixedCost | +48% | ATB 2024 US residential PV O&M (29.53) is the only source |
| PP_SPV_DG, PWRSPVDTR | CapitalCost 2050 | -46%, -47% | ATB declining paths replace the workbook's flat-after-2030 rules |
| PWRBMS | CapitalCost | +40% | Newer edition: IRENA 2024 global bioenergy average 3,242 USD/kW against 2,162 in IRENA 2022 (project mix) |
| PWRSPVTRN | FixedCost | +36% | IRENA OECD PV O&M 20.7 (2024 USD) against workbook 14.24 |
| PWRWNONS | FixedCost | -29% | IRENA Other OECD wind O&M 45 (2024 USD) against workbook 59 |
| PWRHYDROR | FixedCost | +27% | ICE generic small hydro 48 (Dec-2019 USD) against workbook 43.2 |

## 4. Sources blocked or paywalled (not bypassed)

- ICE Plan de Expansion de la Generacion 2024-2040 and 2022-2040 on grupoice.com: HTTP 500. The archived copy at web.archive.org returned HTTP 429. The 2020-2035 plan was read from a public third-party copy (vvalner.com) of the ICE document (CRC-012). Newer plans may carry different unit costs.
- ARESEP tariff-band resolutions: the search page is behind a reCAPTCHA check, so it was not used.
- IEA WEO 2023 power generation cost dataset: needs a login and licence.
- MINAE Balance Energetico Nacional 2021 and the BEN folder: HTTP 403 with a Cloudflare browser check.

## 5. Known-limitation candidates (not fixed)

- `A-O_Parametrization.xlsx`, Primary Techs: `IMPELE` and `PROINDWAS` share Tech.ID 9, so LAC_COST_WRITE should match rows on Tech, not Tech.ID.
- `CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx`, Primary and Secondary Techs: plant costs carry an 8 percent step from 2021 to 2022 (2021 USD to 2022 USD), while fuel prices will be in real 2024 USD.
- Same workbook, `PWRDSL` CapitalCost and FixedCost: the path follows ATB's gas combined cycle with 95% CCS, a poor proxy for diesel engines.
- Same workbook, supply rows: FixedCost on `IMPPURDSL`, `IMPPURGSL`, `IMPFOI`, `IMPLPG` and CapitalCost 234.55 on `IMPLPG`. With a wholesale import parity price that already includes landed costs, these may double count.
- Same workbook, `PWRHYDDAM` CapitalCost: it matches a US ATB new stream-reach class. IRENA's Central America large hydro averages (3,058 to 3,826 USD/kW) are less than half of it.
- `A2_Extra_Inputs/A-Xtra_Emissions.xlsx`, sheet GHGs, `T5COAIND` rows: they cite "InventarioGEI1990-2021". The 2021 inventory may be where the 2021 coal value of 0.675 PJ comes from.
- PROCOMER shows 87,970 t of petroleum bitumen (HS 271320) imported in 2024. Its representation in the model (non-energy use) was not checked.
- `IMPKJF` carries one price for jet fuel and kerosene; kerosene is 7.3 percent lower.
- CLEWISE Data in Brief: the 4.8 technology cost paragraph appears twice, once truncated before the Ecuador emission factor tables.

## 6. Left unchecked

- A newer NREL ATB edition (2025) was not checked for an update of the series used.
- The news report of PEG 2022-2040 costs (wind 1,874, solar 1,200 USD/kW, currency year not stated) was not used.
- The fit of the workbook paths to ATB 2024 was checked for capital and fixed costs. `PWRGEO` FixedCost matches the HydroFlash shape only approximately (ratio spread 0.4 percent).

## 7. Incidents

- The session was interrupted during the first OneDrive file search. The search was rerun with a timeout and all five paper files copied.
- During plant research, Git Bash curl crashed on an ICE redirect; the ICE DOCSE report was later downloaded with the Windows curl. A cookie-based retry against the ICE site was refused by the session's permission settings and not pursued.
- The repository's `.gitattributes` sets `* -text`, so CSV and Markdown files written on Windows were first committed with CRLF line endings and `git diff --check` failed. All tracked job files were converted to LF and the commit amended before the push.
- The brief asks for one commit. The pull request number is only known after the pull request is opened. Amending the pushed commit would need a force push, which the session's permission settings refused. The report update (pull request number, final gate results, LF fixes in two scripts) is therefore a second commit on the branch, `LAC_COST_SRC_CR: report pull request number`.
- `elec_cost_perf.pdf` at the EIA AEO assumptions address is the AEO2023 edition (March 2023), so the local file is named for that edition.
