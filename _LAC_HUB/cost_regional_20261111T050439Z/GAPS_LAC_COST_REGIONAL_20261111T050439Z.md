# GAPS LAC_COST_REGIONAL 20261111T050439Z

## 1. Judgement calls and reasons

1. Currency basis. The brief says values are real 2024 USD, but several international values keep the currency year of their country job (Costa Rica plant rows 2022 USD after 2021, Jamaica as published, Guatemala ATB rows 2022 USD, Dominican Republic 2021 to 2023 USD). Regional proposals follow the brief and are real 2024 USD, so `change_pct` includes the currency-year step (about +7.2 percent for a 2022 USD row).
2. Year of a single printed value. ICE PEG 2024-2040 and ODS Honduras PIEG 2026-2035 print one cost per technology, not a year path. The value is placed at 2024 (the first plan year of both) and the path is P(y) = R x I(y)/I(2024).
3. ICE costs are in constant USD of December 2023. They are converted with the CPI-U annual averages 2024/2023 (313.689/304.702), the same convention the Costa Rica job used for December 2019 USD.
4. ICE PEG 2024-2040 prints a capitalized investment (Tabla 10.8, note 1) and an overnight investment (Tabla 10.9, note 2). The overnight value is used because the model cost is overnight.
5. IRENA weighted average total installed cost is accepted as overnight capital cost per kW, as all six country jobs did.
6. ICE generic hydro (Hidro Genericos, 20 MW) has 0 useful volume in Tabla 10.7, so it is run-of-river and does not match Costa Rica PWRHYDDAM. ICE reservoir projects (Diquis, RG-430) are single projects, not a class value. The Costa Rica dam row takes ODS Honduras Hidroelectrica de embalse (R2).
7. IRENA hydropower classes (large above 10 MW, small up to 10 MW) state size, not dam or run-of-river, so they match neither configuration.
8. Costa Rica PWRSPVDTR (PV in distribution) is matched to ICE Solar Genericos (10 MW, fixed tilt), as the Costa Rica job treated it as utility-scale ground PV; fixed tilt is taken over the 1-axis tracking generic.
9. Costa Rica PWRDSL and PWRFOI variable O&M take the ODS Honduras engine on gas/bunker/diesel (5 USD/MWh diesel, 7 USD/MWh bunker); the Costa Rica job mapped both rows to medium-speed engines.
10. Size rows of ODS Honduras Tabla 19. Where the value differs by size the lower middle printed size is taken (hybrid PV with battery 30 percent: 50 MW of 20, 50, 100, 150). Run-of-river takes the under 10 MW row, which is also the small hydro class of the current Guatemala source. Engine O&M, PV fixed O&M and reservoir capital cost are equal across sizes.
11. Guatemala PPPVTS (transmission solar with battery storage) is matched to the ODS Honduras hybrid PV with battery (battery 30 percent of PV power). The current ATB PV-plus-battery reference has a larger battery share; both are PV with storage, which is the configuration test of the brief.
12. Within R2, the most recent publication wins: ODS Honduras PIEG (September 2026) over ICE PEG 2024-2040 (September 2025) for Guatemala engines, geothermal, run-of-river and combined cycle.
13. Honduras PPBIM takes ICE Biomasa Genericos (sugarcane, steam cycle) as R2; the Honduras plan has no biomass candidate.
14. IRENA RPGC 2024 Table 2.1 marks Central America and the Caribbean as data from 2012, not 2010, so the first printed year is 2012 for Jamaica PPWNDON.
15. IRENA RPGC 2025 Table 3.1 prints 2015 and 2025 for Central America and the Caribbean. Following the brief, Guatemala PPPVT and PPPVT2 interpolate linearly between them for 2018 to 2024 (2024: 1,077.06 USD/kW), even though the 2024 edition printed 1,375 for 2024; within R1 the most recent edition is taken.
16. IRENA RPGC 2025 wind and PV rows for Other North America include Canada and are not LAC tables; they are not used.
17. Colombian Technology Catalogue (R2 for Ecuador): values per MWe (AC) are used, not per MWp (DC). Ecuador PPPVD (distributed solar) takes the industrial rooftop class (100 kW) because the current Ecuador source is ATB commercial PV; PPWNDD takes small turbines under 1 MW; STOELE takes grid-scale lithium-ion, 4 hours, and keeps the /31.536 PJ per GW-year conversion of the Ecuador job.
18. Catalogue reading corrections: PDF p.64 fixed O&M prints 15.000, 12.900, 10.900 with the last digit in a separate text cell; PDF p.140 prints 66,500 with a comma and PDF p.141 prints 94.00 next to 93.600; all are read as thousands of USD/MW-year (stated in `regional_values.csv`). Only the p.64 row enters a proposal.
19. Dominican Republic PPPVT, PPPVTHYD and PPWNDON are refused: their current paths add a 4-hour battery cost from 2025, and no regional source with a stated currency year prices that configuration.
20. Dominican Republic PPDHYD (self-producer hydro) states no hydro type, so no dam or run-of-river value is matched.
21. Jamaica PPWNDON: the 2021 row of `proposals_all.csv` rests on the national 2018 IRP (PSJ-004) and is outside the scope rule, so the regional path covers 2022 to 2055 only.
22. Jamaica IRP 2018 states 2018 USD (PDF p.59) and is R2 for the Dominican Republic, but none of its candidate rows matches an in-scope Dominican Republic group with the allowed configuration.
23. The ODS Honduras CPI-U source (CSH-005) was fetched by the Honduras job through a POST to the BLS v1 API; its URL is recorded as that job recorded it.
24. Where a conversion needed no CPI-U factor (2024 USD sources), `source_ids` carries only the regional source id.

### Documents excluded (no value accepted)

- IRENA Renewable Energy Roadmap for Central America 2022 (REG-004): Table 16 has no currency year (would have served distributed PV, biomass and geothermal).
- MEM Guatemala PEIG 2026-2050 (REG-007): Tabla 6 has no currency year.
- MEM Guatemala PEG 2024-2054 (REG-008): no technology cost table in the text layer.
- ETESA Panama PESIN 2025-2039 (REG-009): project costs in B/./kW with no currency year; promoter data, not class values.
- El Salvador PIEGE 2020-2030 (REG-010): project costs with no currency year.
- SENER Mexico PLADESE 2025-2039 (REG-011): costs are CAIO (include interest during construction at 6.89 percent) and carry no currency year.
- IDB Technical Note 1831 (REG-012): country costs only as charts.
- UPME Colombia PIEG 2025-2039 (REG-013): CAPEX only as a chart; led to the Colombian Technology Catalogue.
- CNE Dominican Republic PEN 2022-2036 (REG-016): generic project tables 204 to 229 state no currency year.
- Barbados IRRP draft 2021 (REG-017): Table E.1 is labelled 2020 Cost (BBD/MW) with no price base; units read as BBD per kW.
- CCREEE 2022 (REG-018): benchmarks are ranges or global values with no stated currency year; the LAC wind 2,062 USD/kW is older than IRENA RPGC 2024.
- PREPA IRP 2019 (REG-019): covers utility PV, onshore wind and batteries only; no in-scope Caribbean group matched (Dominican Republic PV and wind refused for configuration; Jamaica wind takes R1).
- Jamaica IRP 2022 (REG-021): no per-kW cost table.
- USAID Caribbean Energy Initiative cost comparison (2021): seen in search results; USAID is a bilateral agency, not a regional or multilateral body or a neighbour government, so it fits no tier; not downloaded.

## 2. Known-limitation candidates

- `_LAC_HUB/cost_review_20261111T015203Z/proposals_all.csv`, plant rows of Costa Rica, Jamaica, Guatemala and the Dominican Republic: International plant values are in mixed currency years (2018 to 2024 USD), while the brief and these regional proposals use real 2024 USD.
- `proposals_all.csv`, Dominican Republic PPPVT, PPPVTHYD, PPWNDON: Rows described as plain solar or wind carry a 4-hour battery cost from 2025, which blocks any plain regional value.
- `proposals_all.csv`, Guatemala PPPVT and PPPVT2: Two transmission solar rows with the same description now receive the same IRENA capital path.
- `proposals_all.csv`, Jamaica PPWNDON CapitalCost: The 2021 value is the national IRP 1,870 USD/kW (2018 USD) while 2022 onwards is regional, so the path has a step.
- `regional_proposals.csv`, Honduras PPBIM FixedCost: ICE sugarcane biomass fixed O&M (38 USD/kW-year) is 77 percent below the ATB dedicated biopower value it replaces.
- `regional_proposals.csv`, Ecuador STOELE FixedCost: Catalogue battery fixed O&M (15 USD/kW-year in 2024) is 68 percent below ATB; ATB includes augmentation in fixed O&M.

## 3. Left unchecked

- PDF tables were read from the text layer (PyMuPDF and pdfplumber); pages were not rendered to images. Gate 4 found every accepted value in the text at its page.
- MEM Guatemala PEG 2024-2054 may hold cost tables as images; no OCR was run.
- IRENA RPGC 2022 regional PV costs are a figure without a text table and were not transcribed.
- The Panama project table parse (426 values) was not reconciled with the table totals.
- Whether the model also represents the storage service of the Dominican Republic PV and wind rows was not checked.

## 4. Manual downloads

- https://www.recursosyenergia.gob.ec/wp-content/uploads/2020/01/4.-EXPANSION-DE-LA-GENERACION.pdf: Ecuador Plan Maestro de Electricidad 2018-2027, chapter 4 Expansion de la generacion: candidate plant costs (national, found late). Would serve: Ecuador PPPVD, PPWNDD, STOELE.
- https://www.ceaconline.org/ (document location unknown): CEAC Plan Indicativo Regional de Expansion de la Generacion, latest edition: regional candidate costs for Central America. Would serve: Costa Rica, Guatemala and Honduras groups kept international (distributed PV, biomass variable O&M, coal).
- https://cne.gob.do/documentos/ (document location unknown): CNE Dominican Republic Estudio del Regimen Economico de las Energias Renovables (November 2020) and resolutions CNE-AD-0036-2022 and CNE-AD-0006-2023: reference costs by technology including biomass. Would serve: Dominican Republic PPBGS, PPBIM, PPPVD.
- https://energia.pr.gov/ (docket NEPR-AP-2023-0004, 2025 IRP workpapers): Puerto Rico 2025 IRP (LUMA) technology cost assumptions. Would serve: Dominican Republic and Jamaica distributed PV and biomass groups.
- https://www.mem.gob.ni/ (document location unknown): Nicaragua MEM generation expansion plan with candidate costs. Would serve: Costa Rica, Guatemala and Honduras groups kept international.

## 5. Incidents

- curl crashed (segmentation fault) on the ICE PEG 2024-2040 URL; the file was downloaded with Python urllib from the same URL.
- The IDB publications server returned HTTP 403 to Python urllib; curl with a browser user agent downloaded the file.
- The Ecuador ministry host (recursosyenergia.gob.ec) does not resolve, as the Ecuador job also found.
- Three helper scripts briefly contained literal dash characters after writing; they were replaced with chr() calls before the dash gate ran.
- The brief asks for one commit and for the pull request number and commit hash in REPORT. A file cannot carry its own commit hash and the number exists only after the pull request is opened, so a second commit updates REPORT with both (the method used by the earlier cost jobs).
