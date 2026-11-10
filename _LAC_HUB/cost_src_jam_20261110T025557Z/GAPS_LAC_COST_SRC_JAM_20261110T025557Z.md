# GAPS: LAC_COST_SRC_JAM 20261110T025557Z

Jamaica energy model, sourced cost proposals. This file lists every judgement call, each ASSUMPTION row with its leads, changes above 25 percent, blocked sources, known-limitation candidates, what was left unchecked, and incidents.

## 1. Judgement calls

Fuel supply rows

1. Petrojam weekly prices are tax-inclusive. The 52 weekly 2024 prices (pages 4 to 9, no missing week) average exactly the MSET refinery billing prices: Gasolene 87 168.738 against 168.73 J$/L, Gasolene 90 176.494 against 176.49, Auto Diesel 171.059 against 171.05, ULSD 178.284 against 178.28. MSET defines the billing price as including the Special Consumption Tax (SCT) and fees. Per the brief, they are not used as the pre-tax point; they are recorded in `price_points_2024.csv` (30 to 123 percent above the chosen points) and diesel and gasoline fall back to import CIF.
2. Diesel (`DIST_DSL`): the brief's order would take Comtrade HS 271019 import CIF (16.581 USD/GJ). That code mixes diesel with jet, kerosene, heavy fuel oil and lubricants, and it holds the 2.6 million bbl of Bunker C imported by the alumina companies in 2024, so it is not a diesel price. I treated diesel import CIF as not published and took the closest pre-tax diesel point: ADO delivered to JPS net of the specific SCT, 19.948 USD/GJ (OUR, 12 months). This also changes least against the current 19.82. The ad valorem part of the SCT is not removed; the WTO TPR says diesel for public electricity is exempt, so the value is taken as pre-tax. The point has no history, so r is the 2024 ratio alone.
3. Kerosene and jet (`DIST_KER`, `DIST_JET`): no 2024 pre-tax value is published (Petrojam prices include SCT; MSET reports refined product imports only in aggregate; the US Census trade API needs a key). The 18.0 USD/GJ ASSUMPTION of LAC_LOCAL_PRICES is kept, with a new check against the EIA Gulf Coast jet price. Rule F4 takes r for kerosene from its only history (pre-tax ex-refinery kerosene 2018 and 2019, ratios 1.51 and 1.60 to Brent), giving a +20.6 percent step from 2024 to 2025. Jet has no history, so its r is the 2024 ratio (1.29) and its path stays near 18. The two rows are the same distillation cut but now diverge after 2024; this follows the rule and is not smoothed. The 2018 to 2019 Petrojam ex-refinery kerosene ran 25 to 28 percent above the Gulf Coast jet price, which would put 2024 near 21.8 USD/GJ (stated as the upper range in the sentence).
4. Natural gas (`DIST_NGS`): Henry Hub and the WEO United States series are used because EIA publishes US LNG cargoes to Jamaica in every year 2018 to 2025 (CSJ-003). The 2025 Comtrade LNG record (1,378.6 USD/t on half the usual weight, 28.7 USD/GJ) is treated as a reporting error and excluded; 2025 is projected. The chosen point (LNG per tonne with the IPCC net factor) is already net; Henry Hub is divided by 1.055056 and 0.9. r = 4.05 is the mean of 2018 to 2024 ratios; the 2024 ratio is 6.04 because Henry Hub was unusually low in 2024, hence the -28.3 percent step in 2025. Because r multiplies Henry Hub, the WEO doubling of US gas to 2050 (2.2 to 4.6 USD/MBtu) doubles the LNG price (19.5 USD/GJ in 2050); a cost-plus LNG formula would rise less. This follows rule F4.
5. Coal (`DIST_COA`): Jamaica's coal comes by sea mainly from the US export market (Comtrade mirror). WEO 2025 has no US export coal series (its US series is domestic mine mouth plus transport), so the WEO European Union steam coal import price (Atlantic seaborne) drives the projection, and the World Bank South African coal (fob Richards Bay, NAR 6000 kcal/kg) is the observed benchmark for r. The Colombian series is not in the Pink Sheet annual file. The 2025 Comtrade coal value (245.64 USD/t, weight estimated by Comtrade, 2.6 times the benchmark) is excluded as an outlier.
6. Petroleum coke (`DIST_COK`) uses the same coal benchmark and WEO series (no free petcoke benchmark).
7. `DIST_OPE` outputs `E1COK`, the same commodity as `DIST_COK`, and neither row has an activity limit. At 0 it supplied all `E1COK` for free. It is priced exactly as `DIST_COK` (petroleum coke import CIF), which makes the model indifferent between the two rows.
8. Crude (`EXTT_CRU`) uses the MSET import value per barrel (80.94 USD/bbl in 2024), as the brief asks, converted with 7.32 bbl/t (UNSD) and 42.3 GJ/t (IPCC). The MSET value equals the Comtrade 2709 CIF value to the dollar, so its basis is CIF. History 2018 to 2025 comes from the 2022 and 2025 editions of MSET Table 1.
9. WEO 2025 table: the brief says Table 2.32; the PDF has the fuel price table as Table 2.3 on page 109, in USD (MER, 2024), for 2024, 2035 and 2050. Values are interpolated linearly between those years and held flat after 2050. The 2024 value is common to all scenarios.
10. CPI-U 2025 annual average is the mean of 11 months: BLS did not publish October 2025 (value returned as "-"). 2018 to 2024 means reproduce the BLS annual averages (for example 2024 = 313.689).
11. History years with an observed value are 2021 to 2024 (and 2025 where observed). Years before 2021 enter r only. 2025 is projected where no observed 2025 value exists (rule F4), rather than ratio times the 2025 benchmark (rule F3); the brief has both, and F4 is specific to 2025.
12. Fuel proposals for rows in Flat projection mode (`DIST_COA`, `DIST_OPE`, `EXTT_CRU`) give a value for every year; LAC_COST_WRITE has to switch these rows to a year-by-year mode to write them. The same holds for every plant row in Flat mode.

Plant costs

13. Matching is done year by year. ATB years are aligned with model years (model 2021 against ATB 2022, years after 2050 held at 2050). A value is matched if it is within 2 percent of the source as published or after a stated conversion (USD/kW-month x 12; USD/MWh / 3.6; ATB 2022 USD x CPI-U 2021/2022 = 0.92590).
14. Currency years are left as published. Matched values stay in the currency year of the source they match (2018 USD for the IRP, 2021 USD for the deflated ATB hydro and geothermal series, January 2010 prices for the OUR plan); replacement values are as published (2022 USD for IRENA 2022 and ATB 2024). They are not converted to 2024 USD, which keeps the kept values unchanged as Luis decided. Fuel prices are in 2024 USD, so plant costs are, on average, about 8 to 28 percent low against fuel in real terms (CPI-U 2024/2022 = 1.072; 2024/2018 = 1.249). Recorded as a known-limitation candidate.
15. Luis's decision says Jamaica keeps its current plant costs with refined sources; rule P2 also defines a `replace` class where no source gives the number. Where no source gives the current number, the value is proposed as `replace` (P2) and the current value stays in the row. LAC_COST_WRITE can still decide to write only the `keep` rows.
16. Where the level of a row is matched and its path is not, the years off the path are proposed from the matching source's path: `PPPVT` capital (IRP 1350 times the ATB utility PV index after 2024), `PPWNDON` capital (ATB Class 9), `PPHDAM` (ATB NPD1 step moved from 2045 to 2040), `PPGEO` capital (ATB HydroFlash, 2021 USD). The current paths look like ATB values shifted by one year (for example model `PPPVT` 2022 = 1436.17 against ATB OCC 2023 = 1434.8; model `PPGEO` 2025 = 6978 against ATB 2024 = 6989.5).
17. A matched row with a single-value source (IRP fixed O&M for PV, wind and run-of-river; IRP wind variable O&M; OUR combined cycle capital) is kept constant in all years, as the source gives one value.
18. `PPNGS` capital (1300) matches the OUR Generation Expansion Plan 2010 (1317 USD/kW, January 2010 prices). This is the only source that gives the number; IEA WEO 2023 gives 1000 and the 2018 IRP 1600 including IDC. The match is old and may be a coincidence.
19. `PPNGS` fixed and variable O&M take the 2018 IRP NGCC values (first source in P1 order with a number), not the OUR 2010 values that sit beside the matched capital cost.
20. `PPDSL` is mapped to the IRP combustion turbine on natural gas or ADO (Jamaica's ADO-fired units are gas turbines); `PPFOI` to the IRP medium-speed diesel on HFO.
21. `PPFOI` fixed cost 2.99 is the IRP medium-speed diesel 3.0 USD/kW-month written as a yearly value; proposed as `unit_fix` to 36 USD/kW-yr. `PPDSL` carries the same 2.99 (copied), and is replaced by the IRP combustion turbine 12 USD/kW-yr.
22. Bioenergy (`PPBIM`, `PPBGS`): no source gives 5391 (closest NREL ATB 2023 Biopower 5341.3, but 2024 is 5154.5, 4.4 percent off). The first source in P1 order, IRENA 2022 (global weighted average 2162 USD/kW in 2022), is proposed with the ATB Biopower decline. IRENA 2022 gives fixed O&M only as 2 to 6 percent of capital cost, so the fixed cost takes the ATB 163.7. Biogas uses the bioenergy values, as the model does today.
23. Newer editions: IRENA Renewable Power Generation Costs in 2025 (published July 2026) is the newest IRENA edition. Where a value matches IRENA 2022 (geothermal fixed O&M 115; bioenergy variable O&M 0.005 USD/kWh), the newer value is proposed (`upgrade`): geothermal 128 USD/kW-yr in 2025 moved by the ATB fixed O&M path; bioenergy 0.004 USD/kWh = 1.111 USD/GJ. IEA WEO 2025 has the same power cost table as WEO 2023 but covers none of the matched rows.
24. Empty variable cost rows of PV, run-of-river, dam hydro and geothermal are proposed at 0 (`fill_empty`); this changes nothing in the model and documents the source (IRP gives 0 for PV and run-of-river; ASSUMPTION sentences for dam hydro and geothermal). `PPWNDONS` variable cost is filled with the wind value 0.6944, which adds a cost.

## 2. ASSUMPTION rows and the leads tried

| Rows | Value | Leads tried (see `search_log.csv`) |
|---|---|---|
| `DIST_KER`, `DIST_JET` VariableCost 2024 (and the sentence carried on their later rows) | 18.0 USD/GJ | Petrojam weekly prices (tax-inclusive); MSET Table 1 (aggregate refined products only); MSET ex-refinery kerosene (2018 and 2019 only); Comtrade HS 271019 (mixed); US Census API (key required); EIA Gulf Coast jet price (check value) |
| `PPPVDS` CapitalCost, FixedCost, VariableCost, 2021 to 2055 | PV plant plus 1 kW battery per kW | IRENA 2022 and 2025 (no combined system, no battery in 2022); IEA WEO 2023 and 2025 (battery per kWh only); 2018 IRP and IRP-2 (stand-alone BESS only); NREL ATB 2024 (no residential PV-plus-battery) |
| `PPWNDONS` CapitalCost, FixedCost, VariableCost, 2021 to 2055 | wind plant plus 1 kW battery per kW | same leads; ATB 2024 has no wind-plus-battery |
| `PPHDAM`, `PPGEO` VariableCost | 0 | ATB 2024 has no variable O&M rows for hydropower or geothermal; IRP has neither technology; IRENA gives O&M as fixed cost |

The gas sentence of rule F5 is carried on every `DIST_NGS` row (basis observed, history or projected). The IRP battery used in the storage rows is a 15-minute, transmission-sited unit; a 2 to 4 hour battery would cost more, which is inside the stated range only in part.

## 3. Proposed changes above 25 percent (2024) and likely cause

| Row | Current | Proposed | Change | Likely cause |
|---|---|---|---|---|
| `DIST_COA` VariableCost | 1.514 | 5.747 | +280% | Current value (Table 67: 1.51) is far below the 2018 to 2024 import CIF values (1.7 to 5.9 USD/GJ nominal) and no source gives it |
| `DIST_NGS` VariableCost | 7.080 | 13.923 | +97% | Current value is close to a Henry Hub based estimate; LNG import CIF and the OUR price to JPS (12.83 net) are near 13 to 14 |
| `DIST_LPG` VariableCost | 21.259 | 9.019 | -58% | Current value is near a retail or tax-inclusive LPG price; proposed is import CIF without margins (no published LPG margin) |
| `DIST_COK` VariableCost | 4.872 | 3.087 | -37% | Current series was a US delivered proxy plus an adder; 2024 Comtrade petcoke was cheap |
| `DIST_KER`, `DIST_JET` VariableCost | 13.492 | 18.000 | +33% | Current value is below the 2024 Gulf Coast jet cargo price (17.3) |
| `DIST_OPE`, `EXTT_CRU` VariableCost | 0 | 3.087, 14.006 | from 0 | Placeholders |
| `PPBIM`, `PPBGS` CapitalCost | 5391 | 2016 | -63% | IRENA's global weighted average (first source in P1 order) is far below the US-based ATB value (5154 in 2024); no source gives 5391 |
| `PPDSL` CapitalCost, FixedCost, VariableCost | 5391, 2.99, 0.90 | 800, 12, 0.28 | -85%, +301%, -69% | Biomass capital copied to the diesel plant; fixed cost in the wrong time unit |
| `PPFOI` CapitalCost, FixedCost, VariableCost | 5391, 2.99, 6.34 | 1400, 36, 1.81 | -74%, unit fix, -72% | Same copy; the variable cost may include part of the fuel |
| `PPNGS` FixedCost, VariableCost | 22.77, 1.153 | 14.4, 0.722 | -37% | No source gives the current numbers; IRP NGCC values |
| `PPWNDONS` CapitalCost | 3733 | 2525 | -32% | Current gap to wind (1961 USD/kW) suggests about 2 kW of IRP battery per kW of wind; the rule here uses 1 kW |

## 4. Sources blocked or paywalled

- US Census international trade API (HS10 exports to Jamaica): needs a registered key (HTTP 302 to the missing-key page). Not pursued.
- BLS flat file `cu.data.1.AllItems`: HTTP 403. The BLS public API was used instead.
- IEA GEC Model power generation technology costs dataset (WEO cost file): needs an IEA login. Not used.
- IRENA cost data workbooks (2022 and 2025): behind a form asking for personal details. Not submitted; the PDFs were used.
- Royal Society PDF of Koon Koon et al. 2022 (Jamaica geothermal): HTTP 403; only the landing page was saved.
- From LAC_LOCAL_PRICES and not retried: Petrojam site (HTTP 403 to automated requests; pages saved by hand were used), JPS, OLADE library.

## 5. Known-limitation candidates

- Geothermal (`PPGEO`): it can be built at 6,472 USD/kW (2024). The only published resource estimate found is academic: Koon Koon et al. 2022 (Phil. Trans. R. Soc. A 380:20210133), 94.8 MWe in Rio Minho, Dry Harbour Mountains and Blue Mountain South, low-enthalpy (Bath reservoir 83 to 102 C, Wishart 2013). Neither IRP mentions geothermal. A binary plant, the usual choice for low-enthalpy resources, costs about 31 percent more than flash in ATB 2024 (9175 against 6990 USD/kW in 2024, 2022 USD).
- `DIST_OPE` and `DIST_COK` are two supply rows for one commodity (`E1COK`), which also feeds other petroleum products for residential, commercial and transport uses (`T5OPERES`, `T5OPECOM`, `T5OPETRO`). Primary Techs sheet.
- Refinery rows `REF_DSL`, `REF_GSL`, `REF_LPG`, `REF_FOI`, `REF_JET` (Secondary Techs) carry variable costs of 10.4 to 12.0 USD/GJ. With crude priced at 14 USD/GJ, refined products would cost 24 to 26 USD/GJ, above import parity; `REF_OPE` has no cost.
- `PPWNDOFF` (offshore wind) and `PPPVTS` (utility PV with storage) are plants with cost rows outside the section 5 list (Primary Techs).
- Plant costs stay in their source currency years (2010 to 2022 USD) while fuel is in 2024 USD (judgement call 14).
- Single power plant per fuel: IPP gas and HFO plants pay different contract prices from JPS (OUR June and July 2024), which the model cannot show.
- WEO 2025 was written before the 2026 Middle East energy crisis; 2026 projected prices do not reflect it.

## 6. Left unchecked

- MSET Table 4 billing prices for kerosene, LPG and HFO were not compared week by week with Petrojam; only the four products above were checked against MSET.
- Petrojam 2025 weekly dates shift in November 2025 (6, 14 and 20 November instead of a 7-day step); 2025 Petrojam prices are not used.
- The Petrojam 2019 weekly price workbook (MSET) was not parsed (history only).
- The WEO 2023 regional cost values were read by the research step from the PDF annex; I opened and confirmed the 2018 IRP Appendix C rows (PDF p.182) and the BESS paragraph (PDF p.107) myself, and the ATB values from the saved CSV. IRENA page values (p.15, p.173, p.183; IRENA 2025 p.123, p.133) were read by the research step from the saved PDFs and not re-opened by me.
- No sensitivity of the model results to these proposals was run (no model file changed).

## 7. Incidents

- A Write call turned an escaped em dash in `gates.py` into the character itself; caught by gate 7 and replaced with `chr(0x2014)`.
- Scripts first used absolute machine paths; changed to paths relative to the job folder before the gate run.
- The plant research step wrote one temporary HTML file to the session scratch folder outside the job folder and deleted it at once.
- The US Census blocked response was saved as `downloads/census_exports_JAM_2710_HS10_2024.json` (it holds the missing-key HTML page); kept as evidence, not cited.
