# map_jam: Jamaica documentation source map and commissioning statistics

Prepared 2026-11-20 (UTC). Paths are relative to the job folder `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\`. "Old job" means `C:\clw_fix\_LAC_HUB\fix_run_20261111T200825Z\` (files reused there, with their ids). "PDF p" is the page index of the file; the printed page number is added when it differs. Every number below was read in the cited file; sums marked "my arithmetic" show their inputs. Full source list with SHA-256: `research/map_jam_sources.csv`. Source map: `research/map_jam_map.csv` (43 rows).

## Part 1. Source map

### Where the documentation is
- Read the Docs site `https://jam-lts.readthedocs.io/en/latest/`: 38 pages saved as `downloads/map_jam/rtd_*.html` (index, introduction, methodology, model use, national results, GitHub navigation, authors, and the five pages of each of the five mitigation sectors). The energy model is section 4.1 "Electricity and Buildings Sector"; transport (4.2) and industry (4.3) share the same model.
- GitHub: the organisation `Climate-Lead-Group` has only two public repositories, `OSTRAM-LAC` and `OSTRAM` (`downloads/map_jam/clg_repos.json`). Neither is the Jamaica model; in `OSTRAM-LAC` Jamaica appears only as the country code JAM in a table of the README. The Jamaica repository is `clg-admin/JAM-LTS`, linked from the docs page "Github Navigation" (`downloads/map_jam/clgadmin_JAM-LTS_tree.json`, 2340 paths, last push 2025-12-04). Its `README.md` has no references. Its `docs/1_mitigation/0_electricity_buildings/*.rst` files are the source of the Read the Docs pages (same file names and sizes as the `_sources` copies), so the repository adds no citation beyond the site. Model folder: `Ele_Bld_Ind_Integrated/` (workbooks only; not downloaded).
- The only pages with citations for the energy model are "4.1.2 Input Data" (Table 2) and "4.1.5 References". The scenario page (4.1.3) names the 2018 Integrated Resource Plan without a page.

### What the docs cite for the power sector, and what the cited documents print
(All in `map_jam_map.csv` with page, value, model technology and parameter.)
- Installed capacity: 2018 Jamaica Integrated Resource Plan (IRP-1), "Figs. 64 & 65" = PDF p140 (printed p142), unit lists of IPP and JPS conventional plants; the renewable list is Figure 63, PDF p139. Complement: SieLAC-OLADE (page saved is an empty form).
- Generation: MSET web page "An Overview of Jamaica's Electricity Sector" (`downloads/map_jam/MSET_electricity_investments_page.html`): 2018 net generation and purchases 4,355,535 MWh, of which Steam & Slow Speed Diesel 1,354,599, Hydro 179,152, Gas Turbines 124,818, Combined Cycle 901,834, Purchases 1,795,132.
- Operational life: IRP-1 Table 2, PDF p61 (printed p63): hydro 50; simple cycle combustion turbine 20; combined cycle 30; medium speed diesel 30; biomass 30; wind 20; solar PV 20 years. The model uses 50 for hydro and 20 for every other power plant (the model note says "Jamaica Integrated Resource Plan"); the plan prints 30 for combined cycle, medium speed diesel and biomass.
- Costs: IRP-1 Appendix C, PDF p182 (printed A-8): capital cost US$/kW wind 1870, solar 1350, waste to energy 7200, gas turbine 800, combined cycle 1600, medium speed diesel 1400; hydro cost not given. Battery: PDF p107, "$816/kW", which equals the model `STOELE` CapitalCost (816). The model costs of the other plants are not the plan numbers; the docs name NREL ATB 2023 as complement (no URL; not downloaded here).
- Planned additions and retirements: IRP-1 Table 3, PDF p141 (printed p143), and Appendix D, PDF p185 (printed A-11).
- Fuel prices: IRP-1 Figure 43 (PDF p97) and Figure 44 (PDF p98); MSET petroleum prices 2018 (`downloads/map_jam/MSET_Petroleum_Prices_2018.pdf`, J$/litre); IEA WEO 2023 and Argus (not obtained).
- Emission factors: IPCC 2006, Volume 2, Chapter 2, Table 2.2 (PDF p16): CO2 kg/TJ gas/diesel oil 74 100, residual fuel oil 77 400, natural gas 56 100.
- Transmission and distribution costs: JPS annual filings 2015, 2022, 2023 (all three saved; the cost figure itself was not searched).

### Not downloaded
StatInJa value added (no URL on the site); NREL ATB 2023; IEA WEO 2023 PDF; Argus petroleum coke; SieLAC data; national energy balance PDFs and the PIOJ survey PDF (listing pages saved only); all transport and industry documents (no URL on the site, not power sector). Each has `downloaded=no` or `partly` and a note in the map.

## Part 2. Commissioning 2019 to 2024

### (a) Plants commissioned or retired, 2019 to 2024

Commissioned (source for the dated list: OUR Annual Report 2023-2024, `downloads/map_jam/OUR_Annual_Report_2023-2024.pdf`, PDF p62, "System Developments (2019-2023)"; the same list is in the OUR determination `downloads/map_jam/OUR_JPS_2023_Annual_Tariff_Review_Determination.pdf`, PDF p78 to p79):

| Plant | Technology | Fuel | MW | Date | Other locators |
|---|---|---|---|---|---|
| Eight Rivers Energy Company (EREC), Paradise Park, Westmoreland | Solar PV | solar | 37 | 2019 June | 2022 IRP PDF p39 says "37.5 MW of solar plant in 2019" |
| JPS Hybrid Energy Storage System (HESS) | Li-ion battery 20 MW and flywheel 4.5 MW | storage | 24.5 MW / 16.6 MWh | 2019 December | 2022 IRP PDF p39: 40 minutes, "not considered a generation capacity resource" |
| South Jamaica Power Company (SJPC), Old Harbour | Combined cycle gas turbine | NG/ADO | 194 | 2019 December | 2022 IRP PDF p39 ("194 MW of gas fired combined cycle plant in 2019") |
| NFE-JAMALCO | Combined heat and power | NG/ADO | 94 | 2020 February | JPS Annual Filing 2021, PDF p17, says "March 2020" |
| JPS/CB Hill Run, St Catherine (JPS with Caribbean Broilers and New Fortress Energy) | CHP distributed generation | NG | 10 | 2021 December | JPS Annual Filing 2022, PDF p14 ("commissioned in December 2021"); fuel NG and 10.00 MW in the 2023 determination, PDF p95, Table 7.12; 2022 IRP PDF p39: "10 MW of the 14 MW granted for the replacement of the 14 MW Bogue gas turbine GT 8" |

2022, 2023 and 2024: no generating plant commissioned. Evidence:
- The OUR list above covers 2019 to 2023 and its only 2022 to 2023 item is 40 MVar of capacitor banks (2023).
- The JPS unit capacity tables are identical for 2021, 2022 and 2023, total 1043.25 MW (see b).
- CCREEE 2023 report card (old job JAMF-11), PDF p17 (printed p16): "There were no Renewable Energy Projects reported for 2023"; licences to Wigton Energy (49.83 MW) and Sunterra Energy (50 MW) were awarded in February 2025.
- OUR Annual Report 2024-2025 (`downloads/map_jam/OUR_Annual_Report_2024-2025.pdf`, PDF p48): the 2024 developments listed are lower losses, lower fuel rates, private investment commitments for utility-scale renewables, more distributed generation and the award by the Generation Procurement Entity of 100 MW (50 MW solar, 49.83 MW wind). No commissioning. Its Table 23 (PDF p57) lists the same renewable plants and capacities for 2021 to 2024.
- OUR Annual Report 2022-2023 (`downloads/map_jam/OUR_Annual_Report_2022-2023.pdf`, PDF p68): "JPS still has 4MW of residual capacity to install" from the 14 MW right of first refusal. No document read says these 4 MW were installed by 2024.

Retired:
- JPS steam units (heavy fuel oil), 262 MW, retired in 2020: 2022 IRP PDF p39 ("A total of 262 MW of JPS heavy fuel oil (HFO) burning steam units were retired in 2020") and Table 5-1, PDF p40 (JPS Steam HFO 262.0 MW in 2019, 0.0 in 2020). Units, from IRP-1 Appendix D (PDF p185): Old Harbour 2 60 MW, Old Harbour 3 65 MW, Old Harbour 4 68.5 MW, Hunts Bay B6 68.5 MW; 60 + 65 + 68.5 + 68.5 = 262.0 MW (my arithmetic). Hunts Bay B6 (68.5 MW): "at the end of 2020" (JPS Annual Filing 2021, PDF p17; 2023 determination PDF p108). The exact month for Old Harbour 2 to 4 was not found; IRP-1 PDF p103 says they were extended until after the Old Harbour CCGT became commercial.
- Bogue GT8 (14 MW): out of service since 2011 (IRP-1 PDF p104); replaced by the Hill Run plant.
- JPS Munro wind (3 MW): no retirement statement found, but it stopped producing: 743.04 MWh in 2021, 511.05 in 2022, (1.22) in 2023, none in 2024 (OUR 2024-2025, PDF p57, Table 23).
- No retirement in 2021 to 2024: the 171.5 MW of JPS units due in 2023 (Rockfort 1 and 2, GT5, GT10, GT3, GT6, GT7, GT9) were moved to 2026 (2022 IRP PDF p40, Table 5-2). The 60 MW IPP diesel contract (expiry 2024 in Table 5-3, PDF p41; "retirement of the 60 MW of IPP diesel plant in 2025" in the text of the same page) was not confirmed as retired by any document read.

Meaning for the model's 2021 to 2024 new capacity: the only real addition is 10 MW of natural gas CHP (December 2021), against 0.021 GW built for `PPNGS`. No diesel plant and no hydro plant was commissioned in 2021 to 2024 (`PPDSL` 0.008 GW and `PPHDAM` 0.004 GW have no match). JPS hydro is 28.66 MW nameplate (OUR Table 23) or 29.59 MW maximum capacity rating (JPS filings) in every year; the model residual is 0.0291 GW.

### (b) Installed capacity at year end, as printed

2018. IRP-1 Figure 45, PDF p100 (printed p102): "Installed Capacity, 2018 Expected (MW) 974". 2022 IRP Table 11-4, PDF p65: 2018 system installed capacity 974.3 MW, firm 824.4 MW. No table by technology in MW for 2018 was found; IRP-1 Figure 42 (PDF p93, source OUR) gives shares by fuel: HFO 43%, NG/ADO 31%, ADO 10%, Wind 8%, Solar 4%, Hydro 2%, NG 2%.

2019 to 2021. 2022 IRP Table 5-1 "Generating System Installed Capacity", PDF p40 (Page 40 of 93), MW:

| Technology | 2019 | 2020 | 2021 |
|---|---|---|---|
| JPS Steam HFO | 262.0 | 0.0 | 0 |
| JPS Diesel HFO | 40.0 | 40.0 | 40.0 |
| Gas Turbines NG | 20.0 | 20.0 | 20.0 |
| Gas Turbines ADO | 131.5 | 131.5 | 131.5 |
| Comb. Cycle NG | 114.0 | 114.0 | 114.0 |
| Dist. Generation | 0.0 | 0.0 | 10.0 |
| JPS Thermal | 567.5 | 305.5 | 315.5 |
| IPPs Diesel HFO | 249.9 | 249.9 | 249.9 |
| IPPs NG | 194.0 | 288.0 | 288.0 |
| Total IPP Thermal | 443.9 | 537.9 | 537.9 |
| System Firm Capacity | 1,011.4 | 843.4 | 853.4 |
| JPS Hydro | 28.7 | 28.7 | 28.7 |
| IPP Solar | 20.0 | 57.0 | 57.0 |
| IPP Wind | 101.3 | 101.3 | 101.3 |
| Renewable Generation | 187.0 | 187.0 | 187.0 |
| Total Capacity | 1198.24 | 1030.34 | 1040.4 |

Note: the "Renewable Generation" row prints 187.0 for 2019 although 28.7 + 20.0 + 101.3 = 150.0 (my arithmetic); the solar plant commissioned in June 2019 appears only from 2020.

2021 to 2023. JPS "System Projected Maximum Capacity Rating (MCR)" tables: Annual Filing 2021, PDF p121, Table 7-3 (2021 and 2022); Annual Filing 2022, PDF p92 to p93, Table 6-3 (2022 and 2023); 2023 Annual Filing (old job JAMF-10), PDF p81, Table 6-6 (2022 and 2023). The three tables print the same values, MW:
- JPS: Rockfort 1 and 2 20.00 each (subtotal 40.00); Hunt's Bay GT5 21.50, GT10 32.50 (54.00); Bogue GT3 21.50, GT6 14.00, GT7 18.00, GT9 20.00, GT11 20.00, GT12 40.00, GT13 40.00, ST14 40.00 (213.50); Munro Wind 3.00; JPS Hydro 29.59; JPSCo's total 340.09.
- Others: JEP 74.16; JEP-50 50.20; JPPC 60.00; WKPP 65.50; SJPC 194.00; NFE 94.00; JPS DG 10.00; Wigton I 20.00; Wigton II 18.00; Wigton III 24.00; Blue Mountain Wind 36.30; WRG Solar 20.00; Eight Rivers Solar 37.00; sub total 703.16. Total 1043.25.
- By fuel for 2023, using the fuel column of the OUR 2023 determination, PDF p95, Table 7.12 (my arithmetic on the MCR values printed there): HFO = RF1 20 + RF2 20 + JPPC 60 + JEP 124.36 + WKPP 65.5 = 289.86 MW; ADO = GT5 21.5 + GT10 32.5 + GT3 21.5 + GT6 18 + GT7 18 + GT9 20 = 131.5 MW; NG = GT11 20 + Bogue CCGT 120 + JPS/CB CHP 10 = 150 MW; NG/ADO = SJPC 194 + NFE 94 = 288 MW; thermal total 859.36 MW. Renewables from the filing table: wind 3 + 20 + 18 + 24 + 36.3 = 101.3 MW; solar 20 + 37 = 57 MW; hydro 29.59 MW. (Table 7.12 prints GT6 as 18.00 MW; the filings print 14.00.)

2023. CCREEE 2023 Jamaica Energy Report Card (old job JAMF-11), PDF p12 (printed p11), chart "Installed Capacity (MW)": Electric Utility Diesel 53; Electric Utility HFO 138.9; Electric Utility LNG 120; IPP HFO 249.9; IPP LNG 298; Electric Utility RE 32.2; IPP RE 156; Distributed Generation 25.2; Total Capacity 1,077.7 MW. PDF p3: total installed conventional capacity 859 MW, total installed RE 218.7 MW. The eight chart values add to 1,073.2 (my arithmetic), not 1,077.7.

2024. No table by technology for the end of 2024 was found. OUR Annual Report 2024-2025, PDF p57, Table 23, prints the same renewable plant capacities as for 2021 to 2023: JPS Hydro 28.66; Wigton I 20.7; Wigton II 18; Wigton III 24; BMR 36.3; JPS Munro Wind 3; Content Solar 20; EREC 37 MW. JPS Annual Report 2025 (old job JAMF-07), PDF p3 (printed p1): "Jamaica's total installed capacity currently stands at 1,040.8 MW" (statement of the 2025 report, no breakdown).

### (c) Net generation by fuel, as printed

Ministry series. "Table 8. JPS Electricity Statistics, Electricity Generation (MWh)", source "Jamaica Public Service and Independent Power Producers". 2018 to 2021 from Jamaica Energy Statistics 2022 (old job JAMF-08), PDF p15; 2022 to 2025p from Jamaica Energy Statistics 2025 (old job JAMF-09), PDF p15. The two editions print the same 2021 and 2022 values.

| MWh | Petroleum | Natural Gas | Hydro | Wind | Solar | Total Net Generation | Losses % |
|---|---|---|---|---|---|---|---|
| 2018 | 2,880,413 | 948,092 | 179,154 | 301,950 | 45,893 | 4,355,502 | 26% |
| 2019 | 2,757,259 | 1,150,761 | 155,212 | 272,010 | 89,597 | 4,424,839 | 26% |
| 2020 | 1,206,233 | 2,481,186 | 135,581 | 280,321 | 124,112 | 4,227,433 | 28% |
| 2021 | 1,226,317 | 2,543,490 | 138,432 | 263,808 | 131,908 | 4,303,955 | 28% |
| 2022 | 1,516,217 | 2,385,955 | 119,442 | 271,820 | 131,337 | 4,424,771 | 28% |
| 2023 | 1,378,864 | 2,810,863 | 110,284 | 231,724 | 133,124 | 4,664,859 | 28% |
| 2024 | 1,359,354 | 2,750,150 | 122,470 | 216,815 | 142,147 | 4,590,936 | 27% |
| 2025p | 1,304,545 | 2,662,617 | 121,231 | 219,696 | 104,925 | 4,413,014 | 26% |

Regulator series. OUR Annual Report 2024-2025, PDF p54, "Table 21: System Annual Net Generation Breakdown by Primary Energy Source (2019-2024)", GWh. The pages of this PDF are images; the values were read from the rendered page.

| GWh | NG | HFO | Wind | Hydro | Solar | ADO | Net billing | Other | Total |
|---|---|---|---|---|---|---|---|---|---|
| 2019 | 1,162.36 | 2,647.27 | 274.51 | 152.71 | 89.94 | 103.04 | 3.37 | 0.34 | 4,429.83 |
| 2020 | 2,481.19 | 1,167.55 | 281.42 | 134.48 | 124.48 | 38.31 | 4.18 | 0.37 | 4,227.43 |
| 2021 | 2,689.51 | 1,054.25 | 264.55 | 137.69 | 132.22 | 25.74 | 4.85 | 0.31 | 4,303.96 |
| 2022 | 2,319.18 | 1,297.20 | 272.33 | 118.93 | 126.25 | 285.59 | 5.09 | 0.21 | 4,424.77 |
| 2023 | 2,810.86 | 1,334.96 | 231.72 | 110.28 | 127.49 | 43.44 | 5.63 | 0.44 | 4,664.84 |
| 2024 | 2,738.78 | 1,326.69 | 238.00 | 122.47 | 122.47 | 43.81 | 5.67 | 0.23 | 4,590.94 |

The earlier edition, OUR Annual Report 2023-2024, PDF p50, "Table 20: Annual Net Generation by Primary Energy Source (GWH) [2019-2023]" (text PDF), prints some different values: 2019 solar 86.23, other 0.37, total 4,429.87; 2020 solar 119.93; 2021 NG 2,563.17, ADO 152.09, solar 127.06; 2022 HFO 1,297.63, ADO 285.08, other 0.28; 2023 HFO 1,324.96, ADO 43.46, other 0.46, total 4,664.86. Hydro and wind are the same in both editions.

Checks on 2024 (my arithmetic, inputs from OUR 2024-2025 Table 23, PDF p57, MWh): wind = Wigton I 40,052.01 + Wigton II 42,242.65 + Wigton III 40,513.97 + BMR 115,186.67 = 237,995.30, which agrees with 238.00 GWh. Solar = Content Solar 43,782.23 + EREC 71,515.26 = 115,297.49 MWh, which does not agree with the 122.47 GWh printed in Table 21; 122.47 is also the hydro value (JPS Hydro 122,470.31 MWh), so the solar cell of Table 21 looks like a copy of the hydro cell. The ministry prints 142,147 MWh for solar in 2024.

Renewable plants, net generation MWh (OUR 2024-2025, PDF p57, Table 23; 2021 to 2023 equal OUR 2023-2024, PDF p52, Table 22): JPS Hydro 137,687.56 (2021), 118,929.86 (2022), 110,280.43 (2023), 122,470.31 (2024); Wigton I 51,467.29, 50,140.32, 43,556.10, 40,052.01; Wigton II 51,774.14, 52,634.44, 43,272.08, 42,242.65; Wigton III 43,573.93, 46,068.91, 39,402.84, 40,513.97; BMR 116,994.59, 122,971.70, 105,493.63, 115,186.67; JPS Munro Wind 743.04, 511.05, (1.22), none; Content Solar 44,372.14, 45,798.20, 45,751.92, 43,782.23; EREC 82,687.83, 80,451.63, 81,742.79, 71,515.26; Net Billing 4,845.94, 5,088.25, 5,632.46, 5,272.27. Totals printed in the 2024-2025 edition: 534,146.46; 522,594.36; 475,131.03; 475,763.11 (the 2023-2024 edition prints 534,146.47 and 522,594.35 for 2021 and 2022).

## Not found
- Installed capacity by technology in MW at the end of 2018 and at the end of 2024 (only totals: 974 MW for 2018; 1,040.8 MW "currently" in the JPS 2025 report).
- Retirement month of Old Harbour units 2, 3 and 4 (year 2020 only).
- Whether the last 4 MW of the 14 MW right of first refusal and the 60 MW IPP diesel retirement happened by the end of 2024.
- Net generation by fuel split of petroleum into HFO and ADO for 2018 (the ministry prints "Petroleum" only; the regulator tables start in 2019).
- JPS annual reports 2022, 2024 and 2025 (old job) give "Net generation and purchases" by JPS plant type only; the layout text of those pages is scrambled and was not used.

## Unreachable
- `https://www.argusmedia.com/-/media/Files/sample-reports/argus-latin-markets.ashx` (Argus petroleum coke sample, cited by the docs): HTTP 404 with Git Bash curl, browser user agent and `-L`. A second batch (Wayback Machine copies, `curl.exe`, another Argus sample URL) was refused by the session permission system before it ran, so no further attempt was made.
- IEA World Energy Outlook 2023 PDF: only the landing page `https://www.iea.org/reports/world-energy-outlook-2023` was saved (HTTP 200). The PDF download was part of the refused batch; not attempted again.
- StatInJa value added tables: no URL on the docs site; a try of the STATIN national accounts page was part of the refused batch; not attempted again.
- SieLAC-OLADE report pages (`https://sielac.olade.org/WebForms/Reportes/ReporteDato7.aspx?oc=181&or=392&ss=2&v=1` and `...oc=51&or=30102&ss=2&v=1`): HTTP 200, but the saved HTML is the empty report form (the word Jamaica does not occur); the data needs an interactive query. No other route tried.
- OUR Annual Report 2024-2025: downloaded, but all pages are images (`pdftotext` and PyMuPDF return no text, no OCR tool installed). The tables on PDF p54 and p57 were read from rendered page images.
