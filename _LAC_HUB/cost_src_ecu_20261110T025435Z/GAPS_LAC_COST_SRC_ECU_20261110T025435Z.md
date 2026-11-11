# GAPS LAC_COST_SRC_ECU 20261110T025435Z

Plain list of judgement calls, ASSUMPTION rows, large changes, blocked sources, known-limitation candidates, unchecked items and incidents. Values are real 2024 USD unless stated.

## 1. Judgement calls and reasons

Fuel supply rows
1. WEO 2025 fossil fuel price table is Table 2.3 "Wholesale fossil fuel prices by scenario", page 109, not Table 2.32. Units: USD/barrel crude, USD/MBtu gas (gross), USD/tonne steam coal (6000 kcal/kg), all 2024 USD at market exchange rates. It publishes 2024, 2035 and 2050 only, so WEO_s(y) is linear 2024 to 2035 and 2035 to 2050. WEO 2025 was written before the 2026 Middle East energy crisis.
2. Diesel, gasoline, jet and LPG use EP Petroecuador's 2024 import unit values (import CIF, DAT/DPU basis, ECU-001), not the administered terminal prices (decision 2). The terminal prices are in price_points_2024.csv beside them.
3. Kerosene (DIST_KER): no import CIF or export FOB exists. The closest pre-tax point is the industrial terminal price of Diesel 1, 2.4619 USD/gal excluding VAT (18.32 USD/GJ), which is administered. r is the 2024 ratio alone.
4. Coal (DIST_COA): 95 percent of Ecuador's 2024 anthracite imports came from Peru (FUEL-001). No WEO series covers Peru or anthracite. I chose WEO "Steam coal Japan" with the World Bank Australian (Newcastle) price as observed benchmark, as the Pacific seaborne market. The alternative pair is EU steam coal with South African coal. With no coal history, r is the 2024 ratio, so the choice sets only the path (STEPS 2050 is 56 percent of 2024 under the Japan series; it would be 59 percent under the EU series).
5. Petroleum coke (DIST_COK): 99 percent from the United States (FUEL-001). Treated as an oil product: Brent benchmark and WEO crude path.
6. Rows without an observed 2025 value (COA, COK, JET, KER) are projected from 2025 (rule F4); 2021 to 2023 are history from ratio.
7. Natural gas (DIST_NGS): the 2018 to 2025 unit values of piped gas (EP Petroecuador Informes Estadisticos) were found. Rule F3 uses observed values for 2021 to 2025, and the flat real mean (3.44 USD/GJ net, 2018 to 2025) applies from 2026. The country note says "flat from 2025"; it was written when no 2025 value was known. The observed 2025 value (3.87 USD/GJ net) is used instead, and the step at the join is -11.1 percent.
8. Gas VAT: the published gas dispatch values are treated as VAT-inclusive, as LAC_LOCAL_PRICES did. Whether VAT applies to gas for generation is not confirmed. If it does not, the gas series is about 12 to 15 percent low.
9. Other petroleum products (DIST_OPE): no published OPE price point. ASSUMPTION: the fuel oil export series, because the national energy balance defines these products as made from heavy residues. Check value: industrial residue terminal price 0.894 USD/gal excluding VAT, 6.15 USD/GJ.
10. The joins between the last observed year and the first projected year are reported, not smoothed: CRU +20.3, GSL +19.1, LPG +15.5, FOI +14.9, DSL +14.2 percent (2025 prices were low against the WEO 2024 level), COA -3.1, NGS -11.1, others about 0.

Plant and other technology costs
11. CCG values come from the kit workbook "Ecuador Base SAND.xlsm" (CCG-002), the dataset the kit ships. Its 2020 values equal article Table 10. Article Table 13 (renewable cost path) is 15 to 18 percent higher in 2020 and 39 to 51 percent higher in 2030 for PV and wind. Table 13 was not used.
12. CCG currency year is read as 2020 USD from the column label "Capital Cost ($/kW in 2020)" (article p.16 and p.22). No sentence states it. CPI factor 2024/2020 = 1.212038.
13. CCG fixed costs include variable O&M (article p.17), so plant VariableCost is 0 for every CCG-mapped plant. The kit's 0.0001 values are solver placeholders.
14. Mapping (mapping_ECU.csv):
    - all oil-fired plants (PPCRU, PPDSL, PPFOI, PPDDSL, PPDFOI, PPRDSL, PPILPG) map to CCG "Light Fuel Oil Power Plant", the kit's only liquid-fuel plant above 1 kW;
    - gas plants (PPNGS, PPRNGS) map to CCG SCGT, because Ecuador's gas plant at Machala is open-cycle;
    - biomass and biogas plants map to CCG biomass;
    - hydro "big" (450 MW and above) and "medium" (50 to 450 MW) map to CCG large (above 100 MW), and "small" (below 50 MW) to CCG medium (10 to 100 MW). The medium class straddles the CCG 100 MW line; I took the large class because most of the 50 to 450 MW range is above 100 MW;
    - PPHD maps to CCG small hydro and PPIHD to off-grid hydro.
15. Three current hydro capital costs (PPHDAMAM, PPHDAMPM, PPHRORAB, all 3,500 USD/kW) are within 2 percent of CCG large hydro in 2024 USD (3,562.18). Rule P2 classes them `matched` and keeps 3,500, so they sit 1.7 percent below their CCG siblings at 3,562.18. The 3,500 is likely CCG small hydro (3,499 in 2020 USD) without the currency conversion.
16. PPPVD (distributed PV without storage), PPWNDD (distributed wind) and STOELE (storage) have no CCG counterpart and no sourced PLANMICC row. PLANMICC PP_SPV_DG carries no source code, and its workbook value (1,360) differs from the compiled one (963.33). Under P2 the first source that covers them is NREL ATB 2024: Commercial PV, Distributed Wind Midsize, and Utility-Scale Battery Storage Li-ion 4 hour, Moderate, Market. IRENA 2022 and 2024, IEA WEO 2023 and the Ecuador master plan were tried first (search_log.csv).
17. ATB: overnight capital cost (OCC) is used, not CAPEX with construction financing, because the model discounts investment itself. ATB is in 2022 USD (CPI factor 1.071874). ATB values before 2024 are taken at the 2024 value; years between published points are linear.
18. STOELE capacity is in PJ/yr (CapacityToActivityUnit 1). The ATB battery cost per kW is divided by 31.536 PJ per GW-year, which treats a kW of battery as 31.536 GJ/yr of throughput. A 4-hour battery cycles far less than that, so the per-PJ/yr cost is low against real use.
19. Transmission and distribution (ELE_TRANS, ELE_DIST) also have capacity in PJ/yr. CCG 746 and 1,491 USD/kW are divided by 31.536 (28.67 and 57.30 MUSD per PJ/yr). PLANMICC uses the same 746 and 1,491 with capacity in GW.
20. Refineries: CCG UPSREF001 variable cost 0.71775 USD/GJ (2020 USD) gives 0.870 for every REF_* VariableCost row. REF_* CapitalCost and FixedCost rows are EMPTY in the workbook and are not proposed (the country notes list REF_* for VariableCost only).
21. PROCRU, PRONGS, HYD_G_PROD and HYD_DIST take PLANMICC compiled values: the CCG kit has no crude or gas production step after extraction, and no hydrogen. Notes:
    - the PLANMICC petroleum sheet's own source codes (6, 10, 4) were not traced to documents;
    - PLANMICC states no currency year, so the values are used as published;
    - PROCRU FixedCost is multiplied by 31.536 because our PROCRU has CapacityToActivityUnit 31.536 and PLANMICC's has 1.
22. EXTT_CRU and EXTT_NGS take the CCG extraction costs (MINOIL, MINNGS) with their kit path to 2050, the same in all three fuel scenarios.
23. DIST_BIM and DIST_FIR take the CCG biomass supply cost (MINBIO, 6.79 USD/GJ). PLANMICC has 2.23 (PROSUG and PROBMS) and 0.66 (PROFIR).
24. Electricity imports (IMPELE): 2021 to 2024 use the observed yearly price paid (total USD over MWh imported from Colombia and Peru, ARCONEL Tablas 145 to 148 and CENACE Tabla 2.4). From 2025 on, the 2024 price (263.5 USD/MWh, 73.19 USD/GJ) is held flat as an ASSUMPTION. ARCONEL Tabla 147 misprints the year labels of its second block; the values reconcile with Tablas 145 and 146 when read as 2020 to 2024.
25. Rule P2 class `replace` is used for every CCG-, PLANMICC- or ATB-sourced value that differs from the current one. Where the current value is a placeholder (1 or 2), change_class is `fill_placeholder`.

Brief facts rechecked (Step 3)
26. The section 5 values match the BAU CSVs, except PPBIM: its CapitalCost, FixedCost and VariableCost are 2, not 1. So VariableCost is 1 on 30 of 31 plants, not all.
27. Twelve REF_* CapitalCost and FixedCost rows have projection mode EMPTY and no values.

Reporting
28. REPORT gives the branch, the pull request and the first commit hash. A file in a commit cannot carry that commit's own hash, so the second commit's hash is the branch head.

## 2. ASSUMPTION rows and the leads tried

1,481 proposal cells, 19 technologies. Leads are in search_log.csv under each row.

- **DIST_* CapitalCost and FixedCost** (17 rows): the CCG kit import rows carry only a 0.0001 placeholder, and PLANMICC import rows have no capacity cost. Check: EP Petroecuador price structure (ECU-004).
- **DIST_OPE VariableCost**:
  - LAC_LOCAL_PRICES has no OPE point;
  - EP Petroecuador terminal lists have single administered products with no volume weights;
  - Informe Estadistico dispatch values include VAT;
  - Comtrade covers minor products only;
  - BEN 2024 gives the definition;
  - neither CCG nor PLANMICC has an OPE price.
- **DIST_CHA VariableCost**: none in CCG, PLANMICC or LAC_LOCAL_PRICES. Twice the CCG biomass cost (kiln yield about one half), range 6.8 to 13.6 USD/GJ.
- **DIST_BGS, DIST_OID, DIST_RDF VariableCost** (0): neither CCG nor PLANMICC has a fuel cost for biogas, waste oils or municipal waste.
- **ADD_GRE** (all three costs 0): no separate refinery gas cost in CCG or PLANMICC.
- **DIST_NGS 2026 to 2050**: flat real mean of observed 2018 to 2025 values. Every gas cell also carries the F5 gross-to-net ASSUMPTION sentence.
- **IMPELE VariableCost 2025 to 2050**: flat at 2024. A press report of a CENACE estimate for 2026 to 2028 (8 to 18 cents/kWh) was found, but the CENACE document itself was not, so it was not used. IMPELE CapitalCost and FixedCost are 0.

## 3. Proposed changes above 25 percent and likely cause

Placeholders: 5,700 of 6,090 cells replace a placeholder of 1 or 2, so their percent changes carry no meaning. Changes to real values:
- PPPVD CapitalCost: 100 to 1,855 USD/kW (+1,756 percent). The current 100 is far below any published distributed PV cost, probably a placeholder or a typo.
- PPPVT CapitalCost: 800 to 1,485 USD/kW in 2024 (+86 percent), falling to 941 in 2030. This is CCG utility PV 2024 (1,225 in 2020 USD) converted to 2024 USD. In 2049 and 2050 the CCG value (810, 804) is within 2 percent of the current 800, so rule P2 keeps 800 there. In the same way, PPWNDON keeps the current 1,300 in 2026 only. These single kept years leave small kinks in otherwise smooth paths; LAC_COST_WRITE may prefer the source value there.
- Hydro dam and run-of-river at 5,000: 3,562 (big and medium, -29 percent) or 3,030 (small, -39 percent). The current 5,000 has no source. CCG large hydro is 2,939 in 2020 USD.
- Hydro at 3,500, small class: 3,030 (-13 percent).

Differences of more than 25 percent against PLANMICC (flag in plant_costs.csv; 61 technology-parameter pairs):
- **Hydro capital, run-of-river large:** PLANMICC 1,318.5 against CCG 3,562.
- **Hydro capital, dam large:** PLANMICC 1,572.5 against 3,562.
- **Hydro fixed costs:** CCG 90.9 to 127.2 (VOM included) against PLANMICC 42 to 66.
- **Biomass and thermal fixed costs:** CCG 15.8 and 18.2 against PLANMICC 90 to 95 and 44.3.
- **Gas turbine:** CCG SCGT 707 against PLANMICC 1,000.
- **Fuel oil engines:** 1,454 against 1,070.
- **Plant variable cost:** CCG 0 (VOM inside fixed) against PLANMICC 0.56 to 18.9. PLANMICC's thermal "variable" costs of 9 to 19 USD/GJ look like they include fuel.
- **Refinery variable cost:** CCG 0.87 against PLANMICC 0.69 to 14.5. PLANMICC's 11.5 to 14.5 also look like they include crude.
- **Biomass supply:** CCG 6.79 against PLANMICC 0.66 to 2.23.
- **Electricity imports:** 73.19 (2024 price paid) against PLANMICC 11.83 (no source code).

Checks against Ecuador data:
- EXTT_CRU 2024 is 13.94 USD/GJ (CCG MINOIL, 11.498 in 2020 USD). EP Petroecuador's total cost per barrel of crude in 2024 was 22.81 USD/bbl (ECX-002), about 3.95 USD/GJ at 42.3 GJ/t and 7.32 bbl/t. CCG's extraction cost is set near an import parity level, so it is 3.5 times the reported cost. It is also above the crude export value DIST_CRU (11.86), and EXTT_NGS (5.91) is above the domestic gas price (3.20). Both extraction rows have lower activity limits, so the order of these prices does not change the dispatch, but it does raise the total cost.

## 4. Sources blocked or paywalled

- Allington et al. 2022 article PDF: ScienceDirect 403 and the PMC bot check (not bypassed). Obtained from the PMC Open Access copy on AWS (CCG-014) and cross-checked with the Europe PMC XML (CCG-015).
- PLANMICC reference 4, the ELENA model paper (Villamar et al. 2021, Energy Strategy Reviews): blocked by a CAPTCHA, not bypassed.
- PLANMICC reference 6, Fichter et al. 2017 (Energy 121, Table A5): paywalled.
- PLANMICC references 1 and 2 point to private files of the government data request. They were not opened, and every code 1 or 2 value is cited as the PLANMICC published dataset.
- IEA WEO 2023 and WEO 2025 power generation technology cost datasets: need an IEA login. WEO 2025 Annex B.4 has costs for the United States, European Union, China and India only.
- Ecuador Plan Maestro de Electricidad: the PME 2023-2032 PDF was not located, and the ministry host for PME 2018-2027 did not resolve.
- CENACE import price projection 2026 to 2028: only the press report was found.
- EP Petroecuador's full-year 2024 "costo de produccion por barril" box: not archived (the Jan to Oct average is 26.06 USD/bbl).

## 5. Known-limitation candidates (not fixed)

- `Ecuador/ECU_Energy` BAU, ELE_TRANS and ELE_DIST: residual capacity is 0. With the proposed capital costs, the model must build the whole grid's capacity from 2021, a large early investment that the real system does not make.
- `A-O_Parametrization.xlsx` Secondary Techs, REF_* CapitalCost and FixedCost: projection mode EMPTY, no values. Refinery capacity therefore costs nothing to build.
- CCG kit refinery capital 24.1: labelled "$/kW" in article Table 23 and Table5_ECU.csv, but "$/PJ" in Table5_ECU.xlsx. The two readings differ by a factor of 31.5.
- PPGEO and PPPVDS: CapitalCost, FixedCost and VariableCost are all 1. They are outside the section 5 plant list and get no proposal here.
- PROCRU: CapacityToActivityUnit is 31.536, while every other non-plant row uses 1.
- `A-O_Parametrization.xlsx` Secondary Techs, REF_JET and REF_OPE: their Tech.Name reads "Primary - Import/Distribution", but they are refinery rows.
- Unit labels: DIST_* CapitalCost and FixedCost rows say "MUS$ / PJ", and ELE_TRANS says "M US$ / PJ" for capacity costs.
- Plant rows are mode `Flat`, but CCG and ATB renewable paths and fuel rows change by year. Writing them needs a year-by-year projection mode.
- CLEWISE Data_v2.xlsx sheet 7_Ecuador_Costos:
  - Energy CAPEX and OPEX rows are blank;
  - the LTS CAPEX row and the NDC and LTS CapitalInvestment rows equal the Guatemala sheet cell by cell;
  - the fuel import expenditure rows are empty.
- CLEWISE JCLP draft, section 3.5: says Ecuador's capital needs are negligible, while Data_v2 shows a positive NDC capital cost change to GDP ratio of 0.036 in 2035.
- CLEWISE Data in Brief, section 4.2: citations [8] to [10] point to IPCC and FAOSTAT rather than the energy balance, PLANMICC and ARCONEL.
- PLANMICC: only 79 of 126 v2 cost rows match the compiled values (for example PP_GEO 5,000 against 4,066.5). Most isolated-system rows copy grid values.
- CCG kit v2.0 (Zenodo record 7526340, 2023) exists. This job used v1.0, as named.
- IMPELE: the 2024 import price reflects the drought year. A flat 2024 level may overstate later import costs. The quantity is fixed, so only total cost is affected.

## 6. Left unchecked

- Currency year of the CCG kit (read from a column label) and of PLANMICC (not stated).
- Documents behind the PLANMICC petroleum sheet's source codes (PROCRU code 6, PRONGS code 10, hydrogen code 4).
- What the EP Petroecuador cost per barrel includes (operating cost only, or with depreciation).
- Whether VAT applies to natural gas sold for generation.
- Whether ATB PV costs are per kW AC or DC (the file says "$/kW").

## 7. Incidents

- The first session ended right after the clone and before the remote, branch and job folder were set. On resume the clone was found intact at 2ddd560 and the remaining setup steps ran. No file was lost.
- Sub-tasks:
  - one FRED request hung and was dropped, because BLS data was used instead;
  - one search log had an unquoted URL with commas, which was repaired before merging;
  - some sub-task source records carried local paths or notes in file fields, which were cleaned during assembly.
- The brief asks for one commit. The first commit (e4c62fa) was pushed and the draft pull request opened. Gate 7 then failed: several files were written with Windows line endings, which git reports as trailing whitespace (the repository stores text as-is). Amending the commit and force-pushing was not permitted in this session, so a second commit fixes the line endings and fills in the pull request number and gate results in REPORT. The branch therefore holds two commits. Squash on merge if one commit is required.
