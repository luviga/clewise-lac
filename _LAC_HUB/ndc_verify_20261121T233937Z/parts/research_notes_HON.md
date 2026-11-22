# Step D research notes: Honduras (HON)

Accessed 2026-11-22. Five sources registered (HON-21 to HON-25): 2 official, 2 external, 1 lead. 50 rows in `analyses_HON.csv`. Pending: 1 of 3 fetched (ENME), 2 still pending.

## The documents

- **HON-21, ENME (official, sector plan, D1).** Secretaria de Energia (SEN), official version 2023, published on sen.hn in May 2024 behind a flipbook viewer. Strategy with five axes and fleet targets: electric vehicles 3 percent of the national fleet in 2030 and 15 percent in 2050 (p.24, p.38). No model results. NDC 3.0 (HON-01 p.27) cites it for 3 percent in 2030 and adds 7.5 percent for 2035, a year the ENME does not state.
- **HON-22, ENDRCH-HON documentation (lead, CLG).** Read the Docs PDF build of the CLG site (author field CLG, built 2025-12-04; Git repository clg-admin/ENDRCH-HON). OSeMOSYS model for energy, transport and LULUCF, built to support the update of the ENDRCH (p.5, p.7). Scenarios Tendencial, ENDRCH and ENDRC Ambicioso. Prints a 67 percent cut against Tendencial in 2050 (p.8), the 2050 generation mix assumptions (p.11), the energy net saving of 4.43 billion USD (p.12) and LULUCF net removals in 2050 (p.21).
- **HON-23, Prospectiva Energetica: adopcion de la electromovilidad 2019-2050 (official, analysis).** SEN, November 2023. MAED demand projection (p.28) with a least-cost generation expansion. Four scenarios (I reference, II high electric vehicles, III renewable power, IV both). Prints CO2 changes against Escenario I (Tabla 11, p.53), average electricity cost (Tabla 12, p.54) and vehicle penetration assumptions (p.31 to p.39). It is the analytical companion of the ENME; neither document cites the other by title.
- **HON-24, UNEP Green Economic Recovery (external, 2024).** EUROCLIMA+ project; Green Economy Model (system dynamics) for SERNA, built on the preliminary ENDRCH decarbonization paths (p.47 to p.49). Scenarios BAU, EA 2045, LA 2045, EA 2050, LA 2050. Prints BAU emissions of 14.7 Mt CO2e in 2022 and 54.8 Mt in 2050 (p.49), 2030 cuts of 14.7 to 19.1 percent against BAU, and GDP and jobs results (p.51).
- **HON-25, World Bank CCDR Honduras (external, 2023).** Staff report. CPAT carbon-price scenarios Low, NDC Energy and Paris Aligned (Box 3.1, p.37 to p.38) measured against the 2021 NDC update. Prints CO2 cuts of 3, 9 and 20 percent in 2030 against BAU.

## Government documents they support

ENDRCH, not submitted (HON-22 p.5, p.7; HON-24 p.47 to p.49); the ENME and the NDC electric vehicle goal (HON-21 p.24; HON-01 p.27); the 2021 NDC update (HON-25 p.13, p.37). ENME p.9 says SEN estimated the NDC 2021 energy target (9 percent) with a LEAP model and BaU and mitigation scenarios. That LEAP study was not found.

## CLG authorship

HON-22 is CLG (class lead). The NDC 3.0 itself (HON-01 p.4) credits Climate Lead Group-Libelula for compilation, drafting, the participatory process, editing and layout. That does not change the class of HON-01, which is a government submission, but the hub should know the same group wrote both the NDC text and the ENDRCH model documentation.

## Not obtained

The ENDRCH itself (not published; the NDC says it is being consolidated). The NDC 3.0 technical annex. The SEN LEAP model study behind the 2021 NDC energy target. The ES&T paper "Pathways to Decarbonize Honduras' Power Sector" (DOI 10.1021/acs.est.4c13433) was seen only as a listing; it is behind the publisher's site and was not fetched. IRENA Renewables Readiness Assessment Honduras 2023 was skipped as qualitative. The AECID country sheet was opened and skipped: it restates the NDC and adds no analysis.

## Judgement calls

- HON-22: the transport chapter (section 1.5) repeats the energy chapter text, input table and references (several references are Dominican Republic sources). The only transport result printed is "almost 50 percent" (p.16), which repeats the energy sentence. It is recorded with a note, and no transport-only value is taken from it.
- HON-24: the text says BAU emissions rise 58 percent between 2022 and 2050, which does not match its own 14.7 and 54.8 Mt. Both levels are recorded as printed. Figure 10 labels above 100 percent below BAU mean net negative emissions.
- HON-25: Box 3.1 gives USD 50 to 93 per tCO2e for Paris Aligned, while footnote 12 on p.13 gives USD 5 to 9 for the same scenario, and p.13 says a carbon price meets the NDC's 23 percent energy cut while the box ties the NDC to a 9 percent CO2 cut. The box values are recorded and both conflicts are noted.
- HON-23 vehicle tables (Tablas 3, 5, 7, 9) extract with shifted columns. Only the shares stated in the running text (p.31, p.34) are recorded.

## What a deeper study would need

The ENDRCH-HON model files (the clg-admin/ENDRCH-HON repository) to read the Tendencial and ENDRCH series by sector and year, because the docs print the series only as figures. The SEN LEAP files for the 2021 NDC energy target and for the NDC 3.0 BAU, to see whether the NDC 3.0 BAU matches the ENDRCH-HON Tendencial. A definition of the electric vehicle share in the ENME (stock of all vehicles or of light vehicles only) to compare it with the model's transport technologies. The PIEG 2026-2035 (HON-08) against the ENDRCH generation mix for 2033. When the ENDRCH is published, its scenario values should replace the CLG documentation as the source.
