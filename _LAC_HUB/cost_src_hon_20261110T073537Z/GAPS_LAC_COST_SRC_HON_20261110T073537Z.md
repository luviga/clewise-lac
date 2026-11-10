# GAPS: LAC_COST_SRC_HON 20261110T073537Z

Honduras energy model, sourced cost proposals. This file lists every judgement call, each ASSUMPTION row with its leads, the changes above 25 percent, blocked sources, known-limitation candidates, what was left unchecked, and incidents.

## 1. Judgement calls

Fuel supply rows

1. Chosen points follow rule F2 and section 5: wholesale import parity, pre-tax, for diesel, gasoline, kerosene and LPG; import CIF for coal, petroleum coke and fuel oil; generator delivered (the ODS LNG chain) for natural gas. For fuel oil the BCH import CIF (HON-002, 12.510 USD/GJ) is used, not the SEN value (12.528), because the history series is BCH.
2. The diesel, gasoline and kerosene import parity values cover one published week (27 May to 2 June 2024). They are used as published (the only pre-tax wholesale point). LPG import parity covers 25 CCHAC weeks (January to July 2024).
3. Rule F4 case 2 applies to diesel, gasoline, kerosene and LPG: r is the mean 2021 to 2025 ratio of the BCH import CIF to Brent, times the 2024 ratio of the chosen point to the BCH import CIF. Case 1 (history of the chosen point) applies to coal, petroleum coke and fuel oil. Case 3 (2024 ratio only) applies to natural gas.
4. History years: only years with an observed value of the chosen point are `observed`. Diesel, gasoline, kerosene and LPG therefore have 2018 to 2023 from the ratio (r x Brent of that year), even though import CIF values exist for 2021 to 2025; this follows F3 literally. 2025 is projected wherever the chosen point has no 2025 observation (F4), so only fuel oil starts projecting in 2026.
5. Coal: Honduras' coal comes from Colombia (Comtrade mirror: Colombia reports 27.5 kt to Honduras in 2024, the same tonnage Honduras reports), and the ODS indexes coal to FOB Colombia (HON-016, 5.3.4). No free Colombian coal series exists in the World Bank Pink Sheet (annual or monthly). The observed benchmark is the Pink Sheet South African coal (fob Richards Bay, NAR 6000), an Atlantic seaborne price; the projection series is the WEO European Union steam coal price (imports, Atlantic), which matches a Colombian export origin better than the WEO US series (mine mouth plus transport).
6. Petroleum coke uses the same coal benchmark and WEO series. There is no free petroleum coke benchmark.
7. Natural gas: the ODS LNG chain is Henry Hub indexed (HON-016, 5.3.5), so Henry Hub and the WEO United States gas series apply. The chain value 5.515 USD/GJ is gross; divided by 0.9 it is 6.128 USD/GJ net. r = 2.657 multiplies the Henry Hub path; the chain's fixed adders (liquefaction 2.0, shipping 0.3, regasification 1.0 USD/MMBtu) do not scale with Henry Hub, so the proposed 2050 STEPS price (12.81 USD/GJ) is about 42 percent above the chain recomputed at the WEO 2050 Henry Hub price (4.6 x 1.15 + 3.3 = 8.59 USD/MMBtu gross, 9.05 USD/GJ net). This follows rule F4.
8. WEO 2025 table: the brief says Table 2.32; the PDF has the fuel price table as Table 2.3 on PDF page 109, in USD (MER, 2024), for 2024, 2035 and 2050. Values are interpolated linearly between those years and held flat after 2050 (the model ends in 2050). The 2024 value is common to all scenarios.
9. CPI-U 2025 is the mean of 11 months; BLS did not publish October 2025. 2024 = 313.689.
10. Fuel rows are in "Percent growth of incomplete years" mode in the workbook; LAC_COST_WRITE has to switch them to a year-by-year mode to write the proposals.

Plant costs

11. Every current plant value except bioenergy and the distributed PV fixed O&M path is printed in the ODS/CND Plan Indicativo de Expansion de la Generacion 2024-2033, Tabla 7 (2023 USD), and the PV and wind paths in its Anexos Tablas B-2 and B-3. These are classified `matched` (the document states the numbers and names IRENA 2021, EIA AEO 2023, PNNL and K&M Advisors as its own origins). IRENA 2022 and IEA WEO 2023 give none of the current numbers.
12. Matching is done on the level and, where the row has a path, year by year: PPPVT and PPWNDON capital equal Tablas B-2 and B-3 in every year 2023 to 2042; their fixed O&M is within 2 percent (the model applies the B-2 fixed O&M one year later). PPPVD capital is held flat at the 2023 value (Flat mode) although the plan projects a decline; the level is matched and the path is the stated rule (Flat).
13. Newer edition: the ODS/CND PIEG 2026-2035 Tabla 19 (2024 USD) is the newer edition of the same table. For every matched row it has a value for, the newer value is proposed from 2024 (`upgrade`, basis `matched, newer edition`); 2018 to 2023 keep the current value (`keep`, basis `matched`), since the cited edition is referenced to 2023 and the newer one to 2024. This keeps the history years unchanged.
14. The newer value is taken from the row of the same technology and size class as the cited row, even where the cited row is a different technology from the model's (see section 5): PPPVT keeps the PV-plus-battery row (50 MW: 1,434.72 USD/kW, 40.31 USD/kW-yr), PPWNDON the wind-plus-battery row (50 MW: 1,868.76, 41.14), PPGTDSL and PPGTGLP capital the combined cycle row (1,437.59). PPGTGLP fixed and variable O&M follow the cited LPG row to its newer edition, the open-cycle gas turbine 30 MW (20.00 USD/kW-yr, 6 USD/MWh). PPFOI and PPICEDSL take the 100 MW dual-fuel engine row (1,269.20 USD/kW, 14 USD/kW-yr; 7 USD/MWh for bunker, 5 for diesel); the cited diesel row was 80 MW and the 2026-2035 plan has no 80 MW row. This changes least and keeps the model's technology mapping; the technology-correct alternatives are listed in section 5.
15. Paths of the newer edition: the ODS states (Anexos A.2) that wind, PV and hybrid costs follow NREL ATB 2024 Moderate rates from 2024 but shows them only as figures. The proposals rebuild them as the 2024 Tabla 19 value times the ATB 2024 Moderate index (year / 2024): OCC and Fixed O&M of Utility-Scale PV-Plus-Battery Class 1 for PPPVT, LandbasedWind Class 4 for PPWNDON (the wind-plus-battery hybrid has only 10 percent battery), UtilityPV Class 1 for PPPVD capital. The ATB index is the same for all PV classes; wind classes 4 and 7 give OCC indices within 4 percent. Other technologies are held constant, as the ODS does.
16. PPCOK keeps all its values: the 2026-2035 plan has no new coal candidate. Its Tabla 20 lists a 105 MW coal and petroleum coke steam unit modelled on Becosa at 1,537.12 USD/kW, but that value is the capacity reference price times firm capacity and remaining life, not a cost estimate, so it is not a newer edition of the coal row.
17. Hydro variable cost: the model holds it empty (Zero mode, with 0.4361 USD/GJ stored in 2018). The 2026-2035 Tabla 19 gives 0.00 USD/MWh, so it is proposed at 0 for every year (`fill_empty`, basis `matched`); the 2024-2033 edition gave 1.57 USD/MWh.
18. Bioenergy (PPBIM): no source gives 5,391 to 3,871 USD/kW, 157 USD/kW-yr or 0.08. Rule P2 `replace` applies with the first source in P1 order that covers bioenergy: IRENA 2022 capital (global weighted average 2,162 USD/kW in 2022) with the ATB 2024 Biopower Moderate OCC decline from 2022, and IRENA 2022 variable O&M 0.005 USD/kWh (1.3889 USD/GJ). IRENA 2022 gives fixed O&M only as 2 to 6 percent of capital per year; WEO 2023 Annex B and both ODS plans have no bioenergy row, so the fixed O&M is ATB 2024 Biopower 163.67 USD/kW-yr. The newest IRENA edition (2025) gives 3,606 USD/kW in 2025 and 0.004 USD/kWh; recorded here, not proposed, since the row is a replacement and not a match to IRENA 2022. Honduras biomass plants are sugar mill cogenerators; the IRENA global average includes them.
19. Distributed PV fixed O&M (PPPVD): no source gives the current path (25.85 in 2018, 22.74 in 2024, 11.40 in 2050). IRENA 2022 and 2025, WEO 2023 and the ODS plans publish no distributed or residential PV O&M; NREL ATB 2024 ResPV Moderate fixed O&M (29.53 USD/kW-yr in 2024, 2022 USD) is proposed, held at the 2022 value for 2018 to 2021.
20. Currency years are left as published: ODS values in 2023 USD (to 2023) and 2024 USD (from 2024), IRENA 2022 and ATB 2024 in 2022 USD. Fuel prices are real 2024 USD. Plant costs from 2022 USD sources are about 7 percent low against fuel in real terms (CPI-U 2024 / 2022 = 1.072).
21. Plant rows in Flat mode (most of them) receive a value per year from 2024; LAC_COST_WRITE has to switch them to a year-by-year mode.
22. Luis's decision keeps current plant costs with a refined source. Where a newer edition exists, rule P2 adds the newer value; where no source gives the number, P2 proposes a replacement and the current value stays in the row. LAC_COST_WRITE can still write only the `keep` rows.

Electricity imports

23. Both VariableCost and FixedCost of IMP_ELE carry the import price (500 to 559.8 MUSD/PJ, identical by year). The price goes to VariableCost and FixedCost is proposed at 0 for 2018 to 2024.
24. The price is the cost of ENEE's purchases in the regional market (MER), contract and spot, energy plus capacity charges, divided by the energy, summed over 12 months from the CREE quarterly tariff reports. No annual document publishes a single Honduras import price (EOR and CRIE publish volumes and nodal prices only). 2024: 17,401,336 USD for 151.90 GWh, 114.56 USD/MWh, 31.82 USD/GJ. Energy only would be 106.60 USD/MWh.
25. Rule E1 names the 2024 price. 2022 and 2023 are also published by the same reports, so those years use their own observed price in real 2024 USD (34.21 and 37.27 USD/GJ), as rule F3 does for fuels. 2018 to 2021 have no full-year published price and carry the 2024 price as an ASSUMPTION.
26. The brief says the 99999 price starts in 2030; the workbook and the BAU CSVs have 99999 from 2025 for both VariableCost and FixedCost, with activity lower limit 0 and upper limit 99999 from 2025. Rule E1 applies to 2018 to 2024 (positive lower limit); 2025 to 2050 are not proposed and stay at 99999.
27. Volume check: CRIE reports Honduras MER withdrawals of 158.80 GWh in 2024 and 381.34 GWh in 2018, against the model's 0.571 PJ (158.7 GWh) and 1.339 PJ (372 GWh). The CREE purchases (151.90 GWh in 2024) cover ENEE only.
28. The 2023 total from the parsed CREE rows is 148.63 GWh and 19,368,599 USD (130.31 USD/MWh nominal); the import research step had read September and October 2023 from page images and reported 144.04 GWh and 131.49 USD/MWh. The parsed figure agrees with CRIE (148.64 GWh) and is used.

## 2. ASSUMPTION rows and the leads tried

| Rows | Value | Leads tried (see `search_log.csv`) |
|---|---|---|
| `IMP_ELE` VariableCost 2018 to 2021 (4 rows) | 31.82 USD/GJ (the 2024 price) | EOR site, transaction reports and memorias; CRIE annual and statistical reports 2018 to 2024 (volumes and nodal prices only); ODS market operation page (no documents); CREE tariff reports (complete only from December 2021; 2021 quarterly reports not parsed; none for 2018 to 2020); web searches (press only) |

The natural gas sentence of rule F5 is carried on every `DIST_NGS` row (99 rows; basis observed or projected), with GEN-008, GEN-006 and GEN-005 cited.

## 3. Proposed changes above 25 percent (2024) and likely cause

| Row | Current | Proposed | Change | Likely cause |
|---|---|---|---|---|
| `DIST_COA` VariableCost | 3.448 | 5.194 | +51% | Current value grows 1.9 percent a year from the 2021 workbook value (3.26); 2024 coal import CIF was 134 USD/t |
| `DIST_COK` VariableCost | 4.921 | 2.509 | -49% | Current value is the 2022 workbook value (4.74) grown at 1.9 percent a year; 2024 petcoke CIF was 81.56 USD/t |
| `DIST_DSL` VariableCost | 26.477 | 18.825 | -29% | Current value is the 2022 import price spike (25.5) grown at 1.9 percent a year |
| `DIST_LPG` VariableCost | 17.896 | 11.748 | -34% | Current value is the 2022 workbook value (17.23) grown at 1.9 percent a year; LPG import prices fell in 2023 and 2024 |
| `DIST_NGS` VariableCost | 10.240 | 6.128 | -40% | Current value is 9.15 in 2018 grown at 1.9 percent; the ODS chain at the 2024 Henry Hub (2.19) is lower |
| `PPBIM` CapitalCost | 4,851 | 2,013 | -59% | IRENA global weighted average (first source in P1 order) is far below the US-based ATB value; no source gives the current path |
| `PPBIM` VariableCost | 0.08 | 1.389 | x17 | Current value has a M US$/GWh label and no source; IRENA 2022 gives 0.005 USD/kWh |
| `PPFOI`, `PPICEDSL` CapitalCost | 984.08, 966.72 | 1,269.20 | +29%, +31% | Newer ODS edition prices a 100 MW dual-fuel engine plant |
| `PPFOI`, `PPICEDSL` FixedCost | 39.57 | 14.00 | -65% | Newer ODS edition uses developer O&M quotes instead of the EIA AEO value |
| `PPGTDSL` VariableCost | 0.583 | 0.972 | +67% | Newer ODS edition of the combined cycle row (3.5 against 2.10 USD/MWh) |
| `PPHDAM` CapitalCost | 3,576 | 5,100 | +43% | Newer ODS edition uses the IRENA Central America and Caribbean reservoir value |
| `PPHROR` CapitalCost | 2,000 | 3,786.50 | +89% | Newer ODS edition estimates small run-of-river at 3,786.50 (below 10 MW) |
| `PPPVD` CapitalCost, FixedCost | 871.80, 22.74 | 1,138.48, 29.53 | +31%, +30% | Newer ODS edition for 50 MW utility PV; ATB residential PV O&M |
| `PPPVT` CapitalCost, FixedCost | 1,139.23, 25.36 | 1,434.72, 40.31 | +26%, +59% | Newer ODS edition of the PV-plus-battery row, now with 30 percent battery |
| `IMP_ELE` VariableCost, FixedCost | 559.8, 559.8 | 31.82, 0 | -94%, -100% | Current value is not a price (500 grown at 1.9 percent, 1,800 USD/MWh in each of two parameters) |

## 4. Sources blocked or paywalled

- S&P Global Platts (the ODS fuel price reference) is a subscription; not used.
- IEA GEC power generation cost data file (WEO cost assumptions) needs an IEA login; not used. WEO 2023 and 2025 Annex B tables were used as leads.
- IRENA cost data workbooks are behind a contact-details form; the PDFs were used.
- BLS flat files are blocked to automated requests; the BLS public API was used.
- CREE media search page 2 returned HTTP 400.
- From LAC_LOCAL_PRICES and not retried: Aduanas and SIECA (HTTP 403), appcnd.enee.hn (refuses connections), OLADE library (HTTP 403).

## 5. Known-limitation candidates

- `PPPVT` (Primary Techs) carries the ODS PV-plus-battery cost and `PPWNDON` the wind-plus-battery cost, while the model has separate storage rows (`PPPVTS`, `PPWNDS`). Plain-technology values, 2023-2024 plan: solar FV 871.80 USD/kW and 17.16 USD/kW-yr; wind 1,583.00 and 29.64. 2026-2035 plan (50 MW): solar 1,138.48 and 21.25; wind 1,722.64 and 34.71.
- `PPGTDSL` (Secondary Techs) carries the ODS combined cycle (CCGN 250 MW) costs; `PPGTGLP` carries the combined cycle capital cost. The open-cycle gas turbine row of the 2026-2035 plan (30 MW: 1,496.90 USD/kW, 20 USD/kW-yr, 6 USD/MWh) and the 2023-2024 LPG row (1,024.63 USD/kW) fit these units. Neither can be built in BAU.
- `PPPVD` (distributed PV) capital equals the ODS utility-scale PV row; distributed systems usually cost more (ATB 2024 ResPV OCC 2,600 USD/kW in 2024).
- Variable cost unit labels in the A-O workbook read "M US$ / GWh" for `PPBIM`, `PPPVT` and `PPPVD` while the values are used per PJ; Data in Brief Table 62 prints the same label, and "M USD/GWh" for the coal plant row.
- Hydro variable cost rows (`PPHDAM`, `PPHROR`) are in Zero mode with 0.4361 stored in 2018.
- `IMP_ELE` FixedCost and VariableCost are 99999 from 2025 with an upper activity limit of 99999; the price works as a block on imports after 2024 (Primary Techs).
- `IMP_ELE` CapacityToActivityUnit is 31.356 in the BAU CSV; the usual value for GW to PJ per year is 31.536.
- Rows with cost parameters outside the section 5 list (listed in `cost_rows_current.csv` as `other`): `PPWNDS`, `PPPVT2`, `PPPVTS`, `PPPVDS`, `PPBGS`, `PPCOA`, `PPNUC`, `PPNGS`, `STOELE`, `ELE_TRANS`, `ELE_TRANS2`, `ELE_DIST`, `HYD_G_PROD`, `HYD_DIST`, `DIST_URA`, and the `EXTT_` and `DIST_` rows in EMPTY mode.
- Comtrade mirror data show 530 kt of petroleum coke exported by the USA to Honduras in 2024 against 185 kt reported by Honduras (HS 271311).
- Plant costs stay in the currency years of their sources (2022 to 2024 USD) while fuel is in 2024 USD (judgement call 20).
- WEO 2025 was written before the 2026 Middle East energy crisis; 2026 projected fuel prices do not reflect it. The first LNG cargo reached Puerto Cortes in 2026 (press, from LAC_LOCAL_PRICES), outside the 2024 scope.
- Becosa (`PPCOK`, 105 MW) burns coal and petroleum coke; `DIST_COK` also feeds industry.

## 6. Left unchecked

- CREE 2021 quarterly tariff reports were not parsed (only December 2021, from the April-June 2022 report).
- Tabla 19 of PIEG 2026-2035 was read from the PDF text layer (clean); Tabla 7 of PIEG 2024-2033 and Tabla B-3 were checked on rendered page images. The ODS Anexos A.2 figures were not digitised; the ATB index is used instead (judgement call 15).
- IRENA 2025 values (page 14 and the bioenergy chapter) were read from the text layer only.
- The 2018 and 2022 coal history and the 2018 to 2023 oil product history come from the ratio rule; the BCH import CIF series for 2021 to 2025 was used only for r.
- No model run was made (no model file changed), so the effect on total cost and capacity built is not measured.

## 7. Incidents

- The first session of this job ended on its first command before anything was created; the job restarted on 2026-11-10 with stamp 20261110T073537Z.
- The first version of the CREE parser read quarterly summary tables as monthly rows (2023 and 2024 totals off by a factor of about 300); it was rewritten to assign rows by section totals, and every parsed row was checked against its printed USD/MWh.
- The gate script first matched its own path patterns as machine paths; the patterns are now built from pieces.
- A `.json` summary from the import step was removed so that only `.md`, `.csv`, `.py` and `.txt` files are tracked.
- The import research step (a delegated sub-task) saved its files in `downloads/imp/` only; every value used was re-parsed in `parse_cree_mer.py`.
