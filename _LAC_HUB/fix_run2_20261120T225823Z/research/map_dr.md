# map_dr: Dominican Republic documentation source map

Prepared 2026-11-21 (UTC). Paths are relative to the job folder `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\`. Source map: `research/map_dr_map.csv` (44 rows). Document list with SHA-256: `research/map_dr_sources.csv`. "PDF p" is the page index of the file; the printed page is added when it differs. Every value in the map was read in the downloaded file.

## What the documentation covers
- Read the Docs `https://lts-rd.readthedocs.io/en/latest/`: the energy model is section "0_electricity_transport". Only two pages carry citations: "Datos de entrada" (Tabla 2 energy, 12 inputs; Tabla 3 transport, 6 inputs) and "Referencias" (13 entries). Methodology, structure and scenario pages cite nothing.
- GitHub: `Climate-Lead-Group` has only `OSTRAM-LAC` and `OSTRAM` (regional models). The country model is `clg-admin/LTS-RD`. Its A1 inputs readme lists four classifier sheets and no sources; its `README.md` is a copy of the Ecuador (ECU_NDC) README. No citation beyond the docs.
- Citations without a reference entry: "IMF, 2021" (health externalities). "Ministerio de Hacienda de Costa Rica (2023)" has a placeholder entry ("anada titulo y enlace").

## What was downloaded and what it gives (new in this task unless marked)
- OCDO-SENI 2023a "Informe Anual": the 2023 report (OC-GG-03-IAOPTE-20240214-V0), entry 193521. Tabla 36 (PDF p93-95, printed p91-93) gives SENI capacity by technology 2012-2023; Tabla 4 (PDF p26, printed p24) gives 2023 capacity by primary source: coal 1095.00, natural gas 1019.98, fuel oil #6 707.01, gas and fuel oil #6 673.73, gas and fuel oil #2 334.00, fuel oil #2 100.0, hydro 623.28, solar 675.08, wind 417.05, biomass 30.00, total 5675.12 MW.
- OCDO-SENI 2023b "Programa de operacion de largo plazo 2024-2027": found through the OC file API (`apps.oc.org.do/website-api/v1/publicaciones`). Tabla 11 (PDF p77) lists 43 projects, 3,491.77 MW; by source (my sum of the printed rows): solar 1657.77 (31 projects), natural gas 1454 (5), wind 300 (6), biomass 80 (1). Tabla 1 (PDF p9) dates the gas plants. Section 3.4 (PDF p7) says fuel prices follow EIA STEO/AEO and CME futures, with no numbers in the text.
- OCDO-SENI 2023c "Programacion Semanal": one 2023 week (24-30 June) of 104 weekly files. Sheet "COSTO VARIABLE DE PRODUCCION" gives declared fuel prices per plant (for example CESPM natural gas 333.00 RD$/MMBTU at plant, Quisqueya 2 fuel oil #6 99.52 RD$/gal, Punta Catalina coal 7068.11 RD$/ton), non-fuel variable cost (RD$/MWh) and the exchange rate 54.9547 RD$/US$. The weekly programme has no investment cost, fixed O&M or refinery cost; the docs cite it for those, so these four rows have no value.
- Quiros-Tortos et al. 2023 (IDB, earlier attempt): Cuadro 4 (PDF p52) planned capacity 2023-2034 by technology; Cuadro 5 (PDF p53) cost parameters (for example solar FV 1024 $/kW in 2022, 564 in 2050; onshore wind 1688 and 944). The docs cite this study only for planned capacity; the cost rows are marked as such.
- IPCC 2006 Vol. 2 Ch. 2 (earlier attempt): Table 2.2 (PDF p16-17), Table 2.3 (PDF p18), Table 2.4 (PDF p20-21). Ch. 3 Spanish (file in `downloads/map_hon/`): Cuadro 3.2.1 (PDF p16).
- DGII Parque Vehicular 2022: stock by class 2021-2022 (PDF p5), total 5,463,996 in 2022. No split by fuel in the text.
- World Bank CCDR Annex 4 Transport: fleet 2020 4,842,367 (PDF p7), shares by type (PDF p8). No split by fuel.
- Leads only, no values: SieLAC balance page (empty form), BCRD home page, Godinez-Zamora DOI redirect page.

Earlier-attempt files not used in the map: OC Memorias 2018-2023 zips (the companion task d2_dr reads them), CNE DataCNE files, `oc_informe_anual_2018.pdf`, H2LAC strategy, UASD cable study.

## Not found or not usable
- Investment cost, fixed O&M and refinery variable cost: not in the cited weekly programme.
- Population (ONE 2015), GDP (Banco Central 2023), energy balance (SieLAC 2022): not obtained (see below). The transport growth rates and elasticities printed in Tabla 3 of the docs have no traceable source.
- Vehicle stock by fuel for 2019: neither DGII 2022 nor the World Bank annex prints it.

## Unreachable
- `https://www.one.gob.do/datos-y-estadisticas/temas/estadisticas-demograficas/estimaciones-y-proyecciones-demograficas/`: HTTP 403 (Windows curl, browser user agent). A Wayback request was part of a batch the session permission system refused; not retried.
- `https://doi.org/10.1016/j.esr.2020.100545` (Godinez-Zamora 2020): DOI resolves to an Elsevier redirect page (saved). The ScienceDirect PDF and its Wayback copy were in the refused batch; not retried.
- IMF 2021: `https://www.imf.org/-/media/Files/Publications/WP/2021/English/wpiea2021236-print-pdf.ashx` HTTP 403; `https://www.elibrary.imf.org/downloadpdf/journals/001/2021/236/001.2021.issue-236-en.pdf` HTTP 403; the Wayback copy was in the refused batch. The title is my assumption; the docs give none.
- `https://sielac.olade.org/WebForms/Reportes/ReporteBalanceEnergetico.aspx?or=600&ss=2&v=1`: HTTP 200 but only the interactive form (no data).
- `https://www.bancentral.gov.do/`: HTTP 200, home page only; the docs name no table.
- `https://dgii.gov.do/...ParqueVehicular2022.pdf`: Git Bash curl crashed (segmentation fault) twice; Windows curl from PowerShell worked.
- `https://www.oc.do/Informes/Operacion-del-SENI/Planeacion-del-SENI` and `.../Programacion-del-SENI`: the pages only embed a file viewer; files were reached through `https://apps.oc.org.do/website-api/v1/publicaciones/<area>?loggedIn=false` and a POST to `.../download-url`.
