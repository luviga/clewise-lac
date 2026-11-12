# Jamaica hydro: IRP small hydro, schedule, existing hydro and observed data

Prepared 2026-11-11. All local paths are relative to the job folder `C:\clw_fix\_LAC_HUB\fix_run_20261111T200825Z\`. "PDF p" means the page index in the PDF file; "printed p" is the page number printed on the page when it differs. Numbers marked "my arithmetic" are sums or ratios I computed from the cited figures; everything else was read directly in the cited file.

## Sources

- JAMF-01 | https://www.mset.gov.jm/wp-content/uploads/2024/11/2022-Jamaica-Integrated-Resource-Plan.pdf | 2022 Jamaica Integrated Resource Plan, 2018 IRP Review and Update (IRP-2) | Ministry of Science, Energy, Telecommunications and Transport (MSETT) | cover dated August 2023; posted on MSETT site 8 November 2024 (see JAMF-03); PDF created 2024-11-07 | accessed 2026-11-11 | `downloads/jam/JAM_2022_IRP_mset.pdf` | SHA-256 f0ecdcf2fb8dec0185cce30371b8e81c309cb1215ab32a43a67a9edc6a8ff043 | PDF p1 (cover), p11 Table ES-1, p15 Table ES-4, p19 Table ES-6, p20 to 21 Table ES-7, p22 Table ES-8, p26 Dashboard, p30 Table 2-1, p39 to 40 Section 5 and Table 5-1, p43 to 44 Section 6.2, p45 Table 7-1, p52 to 53 Table 9-1, p61 Table 11-1, p62 Table 11-2, p63, p66 Table 11-5, p71 Table 11-9, p73 Table 11-10, p75 Table 11-11, p76 Table 11-12, p77 Table 11-13, p89 (printed page numbers equal PDF page numbers in this file).
- JAMF-02 | https://gpe.gov.jm/wp-content/uploads/2024/11/2022-Jamaica-Integrated-Resource-Plan.pdf | Same document as JAMF-01 (compressed copy) | hosted by the Generation Procurement Entity (GPE) | PDF created 2024-11-07, modified 2024-11-08 | accessed 2026-11-11 | `downloads/jam/JAM_2022_IRP_gpe.pdf` | SHA-256 298dd443b322702de87c85258fad5fb6bbc7bd20e0821bc90dff3b324286788e | Mirror only. Text extracted with `pdftotext -layout` is identical to JAMF-01 (0 differing lines after whitespace normalisation); 93 pages.
- JAMF-03 | https://www.mset.gov.jm/documents/integrated-resource-plan/ | Integrated Resource Plan document listing page | MSETT | page datePublished 2024-11-08 | accessed 2026-11-11 | `downloads/jam/JAM_mset_IRP_documents_page.html` | SHA-256 5a9a2576d2ef8d62ae5da6d527676e2e17e79444a3f8419c74204f019333965e | Lists "2022 Jamaica Integrated Resource Plan" with date "8th November 2024" and links JAMF-01.
- JAMF-04 | https://www.mset.gov.jm/wp-content/uploads/2020/03/2018-Jamaica-Integrated-Resource-Feb-21-2020.pdf | 2018 Jamaica Integrated Resource Plan (IRP-1), revised February 21, 2020 (prepared by DNV GL) | MSET | February 21, 2020 | accessed 2026-11-11 | `downloads/jam/JAM_2018_IRP1_Feb2020_mset.pdf` | SHA-256 4cdb2ff686a5e72dcde0a927be4c8ae2c07b43e9e54c0f5a37ec787cde2574a7 | PDF p90 (printed p92) Section 3.4.4; PDF p91 (printed p93); PDF p100 (printed p102); PDF p105 (printed p107) Figure 46; PDF p182 Appendix C candidate table (no printed number).
- JAMF-05 | https://www.jamstockex.com/wp-content/uploads/2023/04/JPS-AR-22-April-27.pdf | JPS Annual Report 2022 | Jamaica Public Service Company (hosted by Jamaica Stock Exchange) | April 2023 (PDF created 2023-04-30) | accessed 2026-11-11 | `downloads/jam/JPS_AR_2022_jse.pdf` | SHA-256 6a4568974636f77f7e6861d4718f3050ed764fb41e66b8c212cef0e88514e6a9 | PDF p22 (printed p20) "Operational Statistics", Net Generation and Purchases (MWh), 2018 to 2022.
- JAMF-06 | https://www.jpsco.com/wp-content/uploads/2025/04/JPS-AR-2024-MM-FINAL-300425-SPREADS.pdf | JPS Annual Report 2024 | Jamaica Public Service Company | April 2025 (PDF created 2025-04-30) | accessed 2026-11-11 | `downloads/jam/JPS_AR_2024.pdf` | SHA-256 42e02f16df9b6bd6813011af84dd09f3ac515316bc64136815c2b29b650c43c8 | PDF p12 (spread, printed p20) "Operational Statistics", 2020 to 2024.
- JAMF-07 | https://cdn.jamstockex.com/pd/2026/05/JPS-ar-2025-WEB-2.pdf | JPS Annual Report 2025 | Jamaica Public Service Company (hosted by Jamaica Stock Exchange) | 2026 (PDF created 2026-04-30; JSE path 2026/05) | accessed 2026-11-11 | `downloads/jam/JPS_AR_2025_jse.pdf` | SHA-256 5acc57186879de8bb86f2bf433f3c4ae464b855b36adb7067419168f2446e0d6 | PDF p3 (printed p1) company profile; PDF p6 (printed p4) "2025 Year in Review"; PDF p30 (printed p28) "Operational Statistics", 2021 to 2025.
- JAMF-08 | https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2022.pdf | Jamaica Energy Statistics 2022 | Energy Economics and Planning Unit, Energy Division (MSET) | May 2023 | accessed 2026-11-11 | `downloads/jam/MSETT_Jamaica_Energy_Statistics_2022.pdf` | SHA-256 42173d523e4a09baf263df5284a036421e385d2b20709908f3dcc545564caa95 | PDF p15 Table 8 "JPS Electricity Statistics", Electricity Generation (MWh), 2018 to 2022p.
- JAMF-09 | https://www.mset.gov.jm/wp-content/uploads/2021/07/JAMAICA-ENERGY-STATISTICS-2025.pdf | Jamaica Energy Statistics 2025 | Energy Economics and Planning Unit, Energy Division, Ministry of Energy, Transport and Telecommunications | July 2026 | accessed 2026-11-11 | `downloads/jam/MSETT_Jamaica_Energy_Statistics_2025.pdf` | SHA-256 e5c817b1f0236937163badacf28491724a8a07c87e37ae09408871a984a1eb9f | PDF p15 ("Page 15 of 19") Table 8, Electricity Generation (MWh), 2021 to 2025p; PDF p13 Table 5 (labelled "Table 5. Jamaica's Total Energy Consumption"), hydropower 000 MWh.
- JAMF-10 | https://our.org.jm/wp-content/uploads/2023/05/JPS-2023-Annual-Filing_May-5-2023.pdf | JPS 2023 Annual Filing (tariff filing to the regulator) | Jamaica Public Service Company, hosted by the Office of Utilities Regulation (OUR) | May 5, 2023 | accessed 2026-11-11 | `downloads/jam/OUR_JPS_2023_Annual_Filing.pdf` | SHA-256 97a41c774b290d40ca57f1770821502d9272de0fad2bd45063075b327be4ab5d | p81 ("Page 81 of 100") Table 6-6 System Projected Maximum Capacity Rating (MCR); p82 hydro forecast bullets.
- JAMF-11 | https://cekh.ccreee.org/wp-content/uploads/2025/07/2023-Jamaica-Energy-Report-Card.pdf | 2023 Jamaica Energy Report Card | Caribbean Centre for Renewable Energy and Energy Efficiency (CCREEE) | July 2025 (PDF created 2025-07-08) | accessed 2026-11-11 | `downloads/jam/CCREEE_2023_Jamaica_Energy_Report_Card.pdf` | SHA-256 025a30b44fc1046c1a37ca556a55c935ba738a14fa2452fe69df3a403bea26ac | PDF p14 (printed p13) chart "Renewable Energy Resources" (Installed RE vs Potential RE, MW); PDF p3 (printed p2) totals.
- JAMF-12 | https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Mar/IRENA_DAT_RE_Capacity_Statistics_2026.pdf | Renewable Capacity Statistics 2026 | International Renewable Energy Agency (IRENA) | March 2026 (PDF created 2026-03-31) | accessed 2026-11-11 | `downloads/jam/IRENA_RE_Capacity_Statistics_2026.pdf` | SHA-256 fc580bd4f4ee39ef20de6b1ce3926005a4e3e3b8e2c92fd6a16d175a52515921 | PDF p19 (printed p7) "Hydropower" table; PDF p22 (printed p10) "Renewable hydropower" table; PDF p7 data-source flag notes.
- JAMF-13 | https://www.irena.org/IRENADocuments/Statistical_Profiles/Central%20America%20and%20the%20Caribbean/Jamaica_Central%20America%20and%20the%20Caribbean_RE_SP.pdf (redirects to https://www.irena.org/-/media/Files/IRENA/Agency/Statistics/Statistical_Profiles/...) | Energy Profile: Jamaica | IRENA | PDF created 2025-09-24 | accessed 2026-11-11 | `downloads/jam/IRENA_Jamaica_statistical_profile.pdf` | SHA-256 3bf632e1a77e0abacae5ae92555844113941b6fc72291f77bc7fb5629ba6ca16 | PDF p2 "Electricity capacity" (box "Net capacity change in 2024 (MW)"); PDF p3 "Generation in 2023".
- JAMF-14 | https://jamaica-gleaner.com/article/news/20261026/jps-harnesses-power-water-looks-towards-hydroelectricitys-potential-shaping | "JPS harnesses power of water - Looks towards hydroelectricity's potential in shaping Jamaica's energy future" | The Gleaner (Jamaica) | 2026-10-26 | accessed 2026-11-11 | `downloads/jam/Gleaner_20261026_JPS_hydro.html` | SHA-256 0779ff5cce03a6cd13476f975207c237094e987e15672326110eef2e1b600ede | article body (web page, no page numbers).
- JAMF-15 | https://www.jamaicaobserver.com/2026/01/02/maggotty-island-moves-jps-last-mile/ | "'Maggotty Island' moves JPS to 'the last mile'" | Jamaica Observer | 2026-01-02 | accessed 2026-11-11 | `downloads/jam/Observer_20260102_Maggotty_island.html` | SHA-256 1e6e7ef77d3c8d364da7bc0663562f8a4bcb71906f53d2396377ea0c01d17483 | article body.
- JAMF-16 | https://www.jamaicaobserver.com/2025/08/26/holness-commits-hydro-storage-project-clarendon-manchester/ | "Holness commits to hydro storage project for Clarendon, Manchester" | Jamaica Observer | 2025-08-26 | accessed 2026-11-11 | `downloads/jam/Observer_20250826_hydro_storage.html` | SHA-256 ced5ee366a05531a2e65dbe1c3722fce3ee4efcb3a627da9dc886d9aff1b7326 | article lead paragraph.
- JAMF-17 | https://gpe.gov.jm/wp-content/uploads/2024/11/100-MW-Request-for-Proposals-Report-of-Award.pdf | RFP for Supply of up to 100 MW (Net) of Electricity Generation from Renewable Energy Resources (BOO): Report of Award | Generation Procurement Entity (GPE) | November 22, 2024 | accessed 2026-11-11 | `downloads/jam/GPE_100MW_RFP_Report_of_Award.pdf` | SHA-256 1dcbf81e26696b849636cbdbe8af589666c52dfda60057dda18a51f6091af982 | p2 "List of Successful Bidders".

## Small hydro in the IRP

### The document and its status
- JAMF-01 PDF p1 (cover): "2022 Jamaica Integrated Resource Plan, 2018 IRP Review and Update", dated August 2023. The cover note says it is a final document and that the data, conclusions and recommendations are final as the report was presented to and approved by Cabinet. It is called IRP-2 in the text.
- MSETT posted it on 8 November 2024 (JAMF-03 listing date "8th November 2024"; page metadata datePublished 2024-11-08). This matches the "published around November 2024" description. The document itself does not call itself the "2024 IRP".

### The 34.3 MW figure (confirmed)
- JAMF-01 p15, Table ES-4 "IRP-2 Preferred Portfolio Highlights 2022-2041", under "Procurement of": 34.3 MW of hydro power plant capacity, comprising 12 small hydro plants across the country, installed between 2027 and 2033.
- The same wording is repeated in JAMF-01 p62, Table 11-2 "IRP-2 Preferred Portfolio Highlights".
- JAMF-01 p22, Table ES-8 "Key IRP Findings", item 8: the preferred implementation plan (least cost) requires 34.3 MW of hydro plants (with 344 MW wind, 1,143 MW solar PV) over the 20-year planning period. The repeat on p89 (Section 13.1, item 8) rounds this to "34 MW of hydro plants".
- JAMF-01 p71, Table 11-9 "Share of Investments by Technology": New Capacity (MW) Hydro 34.3; % of Investment Hydro 5.8.
- JAMF-01 p21, Table ES-7 "IRP-1 and IRP-2 Summary Comparison", row "New Hydro Plant Installation (MW)": IRP-1 34.3, IRP-2 34.3; change column reads "No capacity [change]"; comment column "Implementation date change".
- Classification: the plan presents the 34.3 MW as part of the recommended "Preferred Portfolio" / "Preferred Implementation Plan", i.e. planned least-cost additions to be procured. It is not a committed project: Section 6.2 (p43 to 44) defines committed projects as those awarded with an executed PPA (or JPS ROFR projects), and the only committed item named there is the 171.5 MW JPS ROFR replacement. No hydro project is described as committed. The IRP never uses the word "indicative" for the hydro.
- Origin in IRP-1: JAMF-01 p11 Table ES-1 and p30 Table 2-1 (IRP-1 highlights) list "34.3 MW of run of river hydro plants comprising of 12 small hydro plants sited throughout the country in 2023". JAMF-01 p31 (Section 2.3) says that as of June 2022 procurement of the IRP-1 resources for 2022 to 2024 had not commenced.
- Inconsistency to note: JAMF-01 p75, Table 11-11 "IRP-1 Preferred Implementation Portfolio Capacity", row "CapExHydro", shows 36.0 MW from 2023 to 2037 (not 34.3).

### Plant list
- IRP-2 (JAMF-01) does not name the 12 plants anywhere (searched all hydro mentions on pages 8, 9, 11, 15, 19, 21, 22, 24, 25, 26, 30, 40, 45, 52, 53, 61, 62, 65, 66, 71, 73, 75, 76, 77, 89, 92, 93). It says IRP-2 is "Not stand alone. To be read in conjunction with IRP-1" (p20, Table ES-7).
- IRP-1 (JAMF-04, PDF p182, Appendix C "Capacity Expansion Generation Modeled") lists 12 run-of-river hydro candidates with nameplate MW (capacity factor; potential net annual energy GWh): Martha Brae 4.4 (43.30%; 16.69), Laughlands 2.0 (60.00%; 10.51), Great River 8.0 (50.20%; 35.18), Negro River 2.3 (34.74%; 7.00), Rio Cobre (Bog Walk) 1.3 (43.20%; 4.92), Spanish River 8.0 (25.60%; 17.94), Green River 2.9 (37.00%; 9.40), Wild Cane River 2.5 (31.90%; 6.99), Rio Grande 1 0.9 (40.58%; 3.20), Rio Grande 2 0.8 (38.52%; 2.70), Swift River 2.9 (32.67%; 8.30), Rio Cobre (NIC Dam) 1.0 (26.25%; 2.30). Same table: lead time 5.5 years, PPA term 20 years, plant life 50 years, capital cost "MSET needs to get from PCJ". Values were checked against a rendered image of the page because `pdftotext -layout` misaligns this table.
- These 12 sum to 37.0 MW and 125.13 GWh (my arithmetic), not 34.3 MW. Neither IRP explains the difference, so the 12-plant list behind 34.3 MW cannot be confirmed from these documents.

### Schedule (yes, the plan gives one, but its tables do not agree exactly)
1. Year-by-year, Table 11-5 "IRP-2 Preferred Implementation Plan Details" (JAMF-01 p66), resource additions text and "Firm Cap Addition" column:
   - 2027: "12.7 MW hydro plan[t]" (firm addition 87.7 MW = 75 MW BESS + 12.7 MW hydro)
   - 2028: 7 MW of hydro plants (firm addition 7.0)
   - 2029: 11 MW hydro plant (firm addition 11.0)
   - 2030: none
   - 2031: 2 MW of hydro (firm addition 2)
   - 2032: 1 MW hydro plant (firm addition 1)
   - 2033 onward: none
   - Sum 33.7 MW (my arithmetic).
   - p63 note: plants are assumed in service at the beginning of the year stated.
2. Cumulative installed hydro, Table 11-12 "IRP-2 Preferred Portfolio Implementation Plan" (JAMF-01 p76), row Hydro (MW, rounded): 2022 29, 2023 29, 2024 29, 2025 29, 2026 29, 2027 41, 2028 49, 2029 60, 2030 60, 2031 62, 2032 63, then 63 every year to 2041. Implied additions (my arithmetic): 2027 +12, 2028 +8, 2029 +11, 2031 +2, 2032 +1, total +34. The same row appears in Table 11-13 (p77).
3. Period totals, Table ES-6 "Capacity Implementation Summary" (JAMF-01 p19) and the IRP-2 Dashboard (p26), Hydro MW: 2023-2025 0; 2026-2030 31.12; 2031-2035 3.18; 2036-2041 0; Total 34 (31.12 + 3.18 = 34.30, my arithmetic).
4. Summary text, Tables ES-4 (p15) and 11-2 (p62): hydro "installed between 2027 to 2033".
5. Hydro capital spending, Table 11-10 "Preferred Implementation Plan PV Investment Cash Flow" (JAMF-01 p73), Capex Hydro Build Cost (US$ '000, present value): 2027 30,764.50; 2028 20,854.55; 2029 18,223.51; 2030 0.00; 2031 2,781.68; 2032 2,229.78; 2033 176.46; total 75,030.48. None before 2027.
6. Earliest date: Table 11-1 "Technology Lead Time to COD" (JAMF-01 p61): Hydroelectric duration 4.0 years, earliest COD 2027.
- Inconsistencies: the year-by-year text sums to 33.7 MW, the cumulative row implies 34 MW, the period table gives 31.12 + 3.18 = 34.3 MW, and the 2033 capex entry (176.46) has no matching MW addition in Table 11-5. For a model, Table 11-5 (p66) is the only table that gives MW by year; Table ES-6 (p19) is the only one that adds to exactly 34.3.

## Existing hydro and assumptions

From IRP-2 (JAMF-01):
- p40, Table 5-1 "Generating System Installed Capacity": JPS Hydro 28.7 MW in 2019, 28.7 MW in 2020, 28.7 MW in 2021 (row read with word coordinates; the layout text of this table is shifted).
- p75, Table 11-11 (IRP-1 portfolio): existing Hydro 28.7 MW in every year 2018 to 2037.
- p76, Table 11-12: Hydro 29 MW (rounded) for 2022 to 2026, before new additions.
- p53, Table 9-1 "2021 Generation Energy Mix": Hydro 3.20% of 2021 net generation (renewables total 12.41%).
- p45, Table 7-1 "Generating Plant Planning Life": Hydroelectric 30 years.
- No hydro capacity factor, no annual hydro energy (GWh) assumption and no hydro cost assumption appear in IRP-2. The phrase "capacity factor" in IRP-2 appears only in the candidate cost discussion on p48 to 49 (wind; a 23% "plant performance capacity factor" sentence that follows the wind price chart) and for offshore wind on p54, never for hydro. IRP-2 says it is to be read with IRP-1.

From IRP-1 (JAMF-04), which IRP-2 builds on:
- PDF p90 (printed p92), Section 3.4.4 "Small Hydro": 28.67 MW of existing hydro plants, modelled as must-run with a maximum generation of 26.7 [MW], annual generation 152,612 MWh and capacity factor 60.7 percent. Small hydro potential "in the order of 6,000 GWh per annum".
- PDF p105 (printed p107), Figure 46 "Existing Hydro units" (MW): C/Spring 0.77; L/White River 4.75; Maggotty-1 3.15; Maggotty-2 3.15; Maggotty-3 6; Rio Bueno A 2.5; Rio Bueno B 1.1; Roaring River 4.05; U/White River 3.2; Total 28.67. Text on the same page says the plants maintain capacity factors above 70 percent (this conflicts with the 60.7% modelling value on printed p92).
- PDF p100 (printed p102): the Maggotty Hydro Plant was commissioned in 2014 (last hydro addition named in the plan).

Regulatory filing (JAMF-10):
- p81, Table 6-6 "System Projected Maximum Capacity Rating (MCR)": "JPS Hydro Subtotal" 29.59 MW for 2022 and 29.59 MW for 2023.
- p82: JPS hydro capacity factor forecast to average 49% for the 2023 to 2024 regulatory period (including a major overhaul on Lower White River and generator overhaul on Maggotty units 1 and 2 for 45 days); hydro energy forecast 126 GWh for 2023/24.

## Observed hydro 2018 onward

Hydro generation is JPS net generation. IRP-1 lists Jamaica's hydroelectric resources as the nine JPS units (JAMF-04 printed p107), IRP-2 Table 5-1 has only a "JPS Hydro" row, and the MSETT Table 8 hydro row (source "Jamaica Public Service and Independent Power Producers") matches the JPS report figures, so these series cover all grid hydro. MW values are from different documents with slightly different definitions (nameplate 28.67 to 28.7, MCR 29.59, rounded 29 or 30).

| Year | Hydro GWh (JPS annual report) | Hydro GWh (MSETT Energy Statistics) | Installed hydro MW | Sources and pages |
|---|---|---|---|---|
| 2018 | 179.153 | 179.154 | 28.7 (IRP-1 base year); IRENA 30 (unofficial) | GWh: JAMF-05 PDF p22 (printed p20); JAMF-08 p15 Table 8. MW: JAMF-01 p75 Table 11-11; JAMF-04 printed p107 Fig. 46 (28.67); JAMF-12 printed p10 |
| 2019 | 155.212 | 155.212 | 28.7; IRENA 30 | GWh: JAMF-05 PDF p22; JAMF-08 p15. MW: JAMF-01 p40 Table 5-1; JAMF-12 printed p10 |
| 2020 | 135.581 | 135.581 | 28.7; IRENA 30 | GWh: JAMF-05 PDF p22; JAMF-08 p15. MW: JAMF-01 p40 Table 5-1; JAMF-12 printed p10 |
| 2021 | 138.431 | 138.432 | 28.7; IRENA 30 | GWh: JAMF-07 PDF p30 (printed p28); JAMF-09 p15. MW: JAMF-01 p40 Table 5-1; JAMF-12 printed p10 |
| 2022 | 119.441 | 119.442 | 29.59 (MCR); 29 (IRP-2 start year, rounded); IRENA 30 | GWh: JAMF-07 PDF p30; JAMF-09 p15. MW: JAMF-10 p81 Table 6-6; JAMF-01 p76 Table 11-12; JAMF-12 printed p10 |
| 2023 | 110.279 | 110.284 | 29.59 (projected MCR); 29 (CCREEE installed RE, hydro); IRENA 30 | GWh: JAMF-07 PDF p30; JAMF-09 p15; IRENA profile gives 110 GWh (JAMF-13 p3). MW: JAMF-10 p81; JAMF-11 printed p13; JAMF-12 printed p10 |
| 2024 | 122.470 | 122.470 | IRENA 30; IRENA profile: net hydro capacity change in 2024 = 0 MW | GWh: JAMF-06 PDF p12 (printed p20); JAMF-07 PDF p30; JAMF-09 p15. MW: JAMF-12 printed p10; JAMF-13 p2 |
| 2025 | 121.033 | 121.231 (preliminary) | IRENA 30 (unofficial) | GWh: JAMF-07 PDF p30 (also "121 GWh ... generated by hydro plants", PDF p6, printed p4); JAMF-09 p15. MW: JAMF-12 printed p10 |
| 2026 | not yet published | not yet published | about 30 MW, nine units at six locations (as of 2026-10-26) | JAMF-14 |

Notes on the table:
- JPS annual report values were read from the "Net Generation and Purchases (MWh)" rows, matched to year columns by word coordinates; row totals reconcile (e.g. 2023: 240,043 + 110,279 + 70,550 + 731,138 + 3,512,849 = 4,664,859, my arithmetic).
- IRENA flags (JAMF-12 PDF p7): "o" official, "u" unofficial, "e" estimated by IRENA. Jamaica renewable hydropower is 30 MW in every year 2016 to 2025, flagged "e" for 2016 and 2017 and "u" for 2018 to 2025 (PDF p22, printed p10). The "Hydropower" table (PDF p19, printed p7) also shows 30 for every year 2016 to 2025. Treat IRENA MW as weak (rounded, unofficial).
- JAMF-13 p2 also contains a text-layer table (not visible on the rendered page, hidden behind the chart) giving Hydro/marine 30 MW and 2019-24 capacity change 0; the visible box "Net capacity change in 2024 (MW)" shows Hydro and marine 0.
- JAMF-07 PDF p3 (printed p1): Jamaica's total installed capacity "currently stands at 1,040.8 MW" (no hydro split).
- Implied fleet capacity factor 2025: 121,033 MWh / (29.59 MW x 8,760 h) = 46.7% (my arithmetic). JAMF-14 states the JPS hydro fleet averaged about 47% capacity factor from 2022 to 2025.

### New hydro plants in 2024, 2025 or 2026: none found
No new hydro plant entered service in Jamaica in 2024 or 2025, and none is reported for 2026 up to 26 October 2026. Evidence:
1. Capacity series flat: IRENA records 30 MW every year 2016 to 2025 (JAMF-12 printed p10) and 0 MW net hydro change in 2024 (JAMF-13 p2). JPS's regulatory MCR was 29.59 MW for 2022 and 2023 (JAMF-10 p81).
2. Same fleet in 2026 as in 2018: JAMF-14 (Gleaner, 2026-10-26) says JPS operates nine hydro units across six locations with combined installed capacity of approximately 30 MW: Upper White River, Lower White River and Roaring River (St Ann), Constant Spring (St Andrew), two units at Rio Bueno (Trelawny) and three at Maggotty (St Elizabeth). This is the same nine-unit list as IRP-1 Figure 46 (28.67 MW, JAMF-04 printed p107). The article says studies show potential for at least another 60 MW but names no project under construction. JAMF-15 (Observer, 2026-01-02) calls Maggotty "one of six hydropower plants operated by JPS", generating up to 12 MW.
3. Generation flat: 110.3 GWh (2023), 122.5 GWh (2024), 121.0 GWh (2025) (JAMF-07 p30), with no step change.
4. Plan timing: IRP-2 holds hydro at 29 MW through 2026 (JAMF-01 p76) and gives 2027 as the earliest COD for new hydro (p61, Table 11-1).
5. Procurement: the GPE 100 MW renewable RFP award (JAMF-17, 22 Nov 2024, p2) went to two solar PV projects (49.83 MW, Clarendon; 50.00 MW, Trelawny); no hydro was awarded.
6. JAMF-16 (Observer, 2025-08-26) reports a hydro storage project for Clarendon and Manchester only as an election pledge, not a built plant.
- The last hydro addition named in the sources is the Maggotty plant commissioned in 2014 (JAMF-04 printed p102).
- Limits: full-year 2026 statistics are not yet published; the 2026 statement rests on JAMF-14 (October 2026) and JAMF-15 (January 2026).

## URLs tried and failed

- https://www.msett.gov.jm/ : DNS failure ("Could not resolve host"). The ministry site is https://www.mset.gov.jm/ (used for JAMF-01, 03, 04, 08, 09).
- https://www.our.org.jm/ via curl (Windows schannel): TLS error SEC_E_UNTRUSTED_ROOT (certificate chain not trusted by the Windows store). The same host worked with Python `urllib` using the certifi CA bundle (normal certificate verification, not disabled), which is how JAMF-10 was downloaded.
- OUR site search (https://our.org.jm/?s=annual+filing, ?s=rate+review+2024, ?s=jps+2025, ?s=maximum+capacity+rating): no 2024, 2025 or 2026 JPS annual filing or 2024-2029 rate review determination found, so no regulator MCR for 2024 or 2025.
- https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Apr/IRENA_DAT_RE_Capacity_Statistics_2026.pdf : returned an HTML page (38,511 bytes), not the PDF. The /2026/Mar/ path worked (JAMF-12).
- https://www.pioj.gov.jm/product/economic-and-social-survey-jamaica-2024/ and .../economic-and-social-survey-jamaica-2025/ : the Economic and Social Survey Jamaica is a paid product ("Add to cart"); not downloaded, energy chapter not checked.
- https://gpe.gov.jm/downloads/ : page loads but does not link the 2022 IRP (it links only the 2018 IRP on gpe.80gigs.com). The 2022 IRP was found by direct URL (JAMF-02) and on the MSETT site (JAMF-01). Page not saved.
- Jamaica Information Service (jis.gov.jm): web searches found no JIS article on the November 2024 publication of the 2022 IRP (only 2017 articles on the first IRP). Nothing downloaded.
- JPS annual report narrative pages: JPS AR 2023 (https://jpsco.com/wp-content/uploads/2024/06/JPS-Annual-Report-2023.pdf) and JPS AR 2021 (https://jpsco.com/wp-content/uploads/2023/05/JPS-2021-Annual-Report-1.pdf) downloaded fine but were deleted as redundant (their hydro rows equal JAMF-05/06/07). None of the JPS annual reports gives hydro installed MW by year.
- MSETT Jamaica Energy Statistics 2021, 2023 (revised August 2024) and 2024 editions downloaded fine but were deleted as redundant (hydro rows identical to JAMF-08/09; no installed capacity table in any edition).
