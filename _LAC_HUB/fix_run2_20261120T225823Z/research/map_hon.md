# map_hon: Honduras documentation source map

Prepared 2026-11-21 (UTC). Paths are relative to the job folder `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\`. Source map: `research/map_hon_map.csv` (29 rows). Document list with SHA-256: `research/map_hon_sources.csv`. "PDF p" is the page index of the file. Every value in the map was read in the downloaded file.

## What the documentation covers
- Read the Docs `https://endrch-hon.readthedocs.io/en/latest/`: "4.2 Datos de entrada" (Tabla 2, 8 inputs) cites SieHonduras (2022), Banco Central de Honduras (2023), Naciones Unidas (2022), Centro Nacional de Despacho (2023), IPCC (2006) Vol. 2 Cap. 2 and IMF (Coady et al., 2019). The transport input page (5.2) repeats the same energy table.
- The reference pages (4.5 and 5.5) are the Dominican Republic list copied (Banco Central de Republica Dominicana, DGII, OCDO-SENI, ONE, IDB study on the Dominican Republic, and others). Except IPCC, no Honduras citation of Tabla 2 has a reference entry, title or URL. I identified the documents by name and year: CND 2023 = PIEG 2024-2033 draft of 4 August 2023 (the scenario page names this plan); SieHonduras 2022 = SEN Balance Energetico Nacional 2022; Naciones Unidas 2022 = World Population Prospects 2022.
- GitHub: `Climate-Lead-Group` has only `OSTRAM-LAC` and `OSTRAM`. The country model is `clg-admin/ENDRCH-HON`; its README holds only the title, and the A1 inputs readme lists classifier sheets with no sources. `OSTRAM-LAC` documents its own data sources (for example PIEG 2024-2033 for Honduras minimum investments), but it is the regional model, not this one.

## What was downloaded and what it gives (all files from the earlier attempt except WPP 2022 and the BCH page)
- PIEG 2024-2033 draft (CND): Figura 1 (PDF p11) capacity 2022 by resource: hydro 909.4, bunker and diesel 949.9, coal/petcoke 105, biomass 221.3, geothermal 39, wind 235, solar 510.8, total 2,970.4 MW (labels matched to legend colours on the rendered page). Tabla 7 (PDF p45) investment, fixed and variable O&M costs by technology, 2023 USD. Tabla 8: El Tornillito hydro 198 MW, January 2026. Tabla 9 (PDF p46) thermal retirements 2027 and 2030. Tabla 17 (PDF p53) electricity demand 11,191.62 GWh (2022) to 18,409.30 GWh (2035). Tabla 20 (PDF p62) inland fuel transport costs. Fuel price projections (Figura 32) are drawn only as a chart.
- PIEG annexes: Tabla B-1 (PDF p18) solar and wind cost projection 2023-2042; Tabla C-5 (PDF p24) LNG chain (liquefaction 2, shipping 0.5, regasification 1 USD/MMBtu over Henry Hub + 15%); Tabla D-1 (PDF p26) life and capacity factor per technology (for example coal 30 years and 80%, large hydro 40 years and 50%, solar 25 years and 25%).
- SEN BEN 2022: installed capacity about 3173 MW (PDF p61); 2022 imports and average import prices: gasoline 6,520 kBEP and US$127.99/bbl (PDF p85), diesel 6,824.5 kBEP and US$148.54/bbl (PDF p93), fuel oil 5,295.7 kBEP and US$86.81/bbl (PDF p97), LPG 3,852.8 kBEP (PDF p80), petroleum coke 1888 kBEP (PDF p100).
- IPCC 2006 Vol. 2 Ch. 2 Table 2.2 (PDF p16-17): fuel oil 77 400, diesel 74 100, natural gas 56 100, LPG 63 100, petroleum coke 97 500 kg CO2/TJ.
- UN WPP 2022 (new, Wayback copy): Honduras population 9792.85 thousand (2018), 10432.86 (2022), 11724.522 (2030), 14258.514 (2050).
- IMF Coady et al. 2019 (WP/19/89): downloaded, but it prints no Honduras value; the country estimates are in an IMF spreadsheet not obtained.
- Complement not cited by the docs: ENEE Boletin Estadistico December 2021, Cuadro No.1 (PDF p3), capacity by plant type 2020 and 2021 (total 2,829.8 MW in Dec 2021).
- The approved PIEG 2024-2033 (July 2024) and its annexes are in the earlier job as R1F-04 and R1F-05 (`downloads/r1/HN_G01-PIEG-2024-2033-Aprobado.pdf`); not read here because the docs cite the 2023 version.

Earlier-attempt files not used in the map: BEN 2018-2021 and 2023, ENEE bulletins 2018-2020, approved-plan listings, BTR1, UN IRES 2018, IPCC Ch. 2 Spanish and Ch. 3, OSTRAM-LAC docs.

## Not found
- GDP from Banco Central de Honduras: the docs name no document; only the home page was saved.
- Fuel price projections as numbers: only the chart of Figura 32.
- Health externality per unit of fuel for Honduras: not printed in Coady et al. 2019.

## Unreachable
- `https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_General/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx`: HTTP 404 (Git Bash curl, browser user agent). The Wayback copy `https://web.archive.org/web/2023id_/<same URL>` worked (25,237,501 bytes, real xlsx).
- `https://www.imf.org/-/media/Files/Publications/WP/2019/WPIEA2019089.ashx`: HTTP 403 (HEAD check); the earlier attempt's copy is used and its source URL was not recorded.
- ENEE December 2021 bulletin at `http://www.enee.hn/Subgerencia%20planificacion/2021/Boletin%20Estadistico%20Diciembre%202021.pdf` and `...DICIEMBRE%202021.pdf`: 308 then 404; the saved copy is the one linked from the Wayback copy of the ENEE bulletin page.
- SieHonduras pages (`downloads/map_hon/siehonduras_*.html`): HTTP 200 but an ASP.NET application with no data in the static HTML.
- `https://www.bch.hn/`: HTTP 200, home page only.
