# Research notes, Costa Rica (step D)

Accessed 2026-11-22. Eight new sources: two official documents from D1 (the INDC 2015 Spanish original and the ICE PEG 2022-2040), one external report, three Climate Action Tracker pages (external) and two CLG items (lead). Analyses file: `analyses_CR.csv`, 47 rows.

## How the NDC 3.0 says it was modelled

CR-01 p.34 and p.147 say the NDC 3.0 used a multisector, economy-wide model on the CLEW framework, extended to all IPCC sectors and named CLEW-CR-3.0. It follows TIMES-CR and OSeMOSYS-CR (p.147, "desde 2016") and is aligned with the 1.5 C path of the 2020 headline target. The NDC names no modelling team. CR-24 (CLG authors) states the same lineage: TIMES-CR in 2017 informed the NDP (p.3), and OSeMOSYS-CR and then CLEW-CR were used, with CLEW serving the NDC 3.0 (p.4). The CLG repository `clg-admin/ndc_cr` (CR-28, folder `ndc_cr_30`) holds OSeMOSYS-based Energy, IPPU, AFOLU and Waste models with the scenarios BAU, NDCcond and NDCincond. This links CLG to the NDC 3.0 modelling, but no government document names CLG.

## The analyses

- **CR-22, ICE Plan de Expansion de la Generacion Electrica 2022-2040, official.** It is the plan that NDC 3.0 contribution EN-10 relies on (CR-01 p.36 and p.46). It uses least-cost expansion under medium, high and low demand. The Plan Recomendado is the base plan at medium demand (p.22 footnote). It adds 460, 525 and 650 MW of wind and solar in 2024 to 2027, 2028 to 2032 and 2033 to 2035 (p.22) and reaches 5,637 MW in 2040 (p.196). Tabla 15.4 (p.202) gives yearly generation by source and emissions, about 0.4 Mt CO2eq a year, most of it from hydro reservoirs and geothermal rather than fuel oil.
- **CR-23, RAND for the IDB (2020), external.** "The Benefits and Costs of Decarbonizing Costa Rica's Economy". Authors are from RAND, the University of Costa Rica (EPERLab: Victor-Gallardo, Godinez-Zamora, Quiros-Tortos), the MINAE Climate Change Directorate and the IDB. It uses Robust Decision Making over 3,003 futures with sector emissions and cost-benefit models. Scenarios: Without decarbonization and the National Decarbonization Plan (NDP, the LTS CR-02 and CR-03). Results: net emissions 11.7 MtCO2e in 2018, 18.8 in 2050 without the plan and 0 with it (p.49), and net benefits of 41 billion USD discounted to 2015 at 5 percent (p.50). It informs the implementation of the LTS (title). GUA-23 p.7 cites it as a notable example of an RDM cost-benefit analysis behind an LTS.
- **CR-24, DDP Report 2025 chapter, lead (CLG authorship).** It is a narrative. It gives the model lineage (above), the 41 billion USD headline (p.6, the same figure as CR-23) and AFD (2022) jobs estimates.
- **CR-25 to CR-27, Climate Action Tracker, external.** The page says its ratings and data are from the 2023 evaluation and that the NDC 3.0 is not yet assessed. Overall rating Almost sufficient. Current policies give 13.2 to 15.8 MtCO2e in 2030 excluding LULUCF (CR-26). The 1.5 C domestic benchmark is 11 MtCO2e excluding LULUCF in 2030 (CR-25). The LTS gives 2.9 to 5.5 MtCO2e in 2050 excluding LULUCF (CR-27). CAT converts the SAR-based NDC to AR4 (CR-27). CR-26 cites the PEG recommended scenario as 2,125 MW of additional renewable capacity by 2040 compared to 2021, which is a second reading of CR-22.
- **CR-28, CLG GitHub `ndc_cr`, lead.** Scenario folder names only. No values were read.
- **CR-21, INDC 2015 Spanish original (FAOLEX copy), official.** This is the D1 document. It is not an analysis.

## What could not be obtained

- The IDB publication page for CR-23 (publications.iadb.org) returned HTTP 403. The RAND copy carries the IDB copyright and was used instead.
- The PEG 2024-2040 (newer ICE edition) was found by search but not fetched. Scope covers the edition the NDC cites.
- Godinez-Zamora et al. (2020) on transport costs and benefits and Rodriguez et al. (2022) on the fiscal effects of transport decarbonization (both cited by CR-23 and GUA-23) were not searched, to stay within the time budget.
- No World Bank CCDR for Costa Rica was searched. IRENA's Central America roadmap covers Costa Rica but prints country results only in figures. It is registered as GUA-26.

## Judgement calls

- CR-23 is classed external. Three authors were then at the University of Costa Rica and later wrote CLG documents (CR-24, GUA-23), but the report credits UCR and not CLG.
- In CR-22 Tabla 15.4 the year column is printed apart from the data rows in the text layout. The years 2030, 2035 and 2040 were assigned by row order (19 rows, 2022 to 2040). The rows say so, and the hub should check them on the rendered page.
- CR-23 prints two sets of totals: 78 and 37 billion USD in the summary (p.16), and 75 and 34 billion USD in chapter 3 (p.50). Both give 41 billion USD net. The chapter 3 values are used and the summary values are noted.
- The CR-23 Figure S.2 labels for electricity (-0.7) and buildings (-0.6) were read from the text layout of a bar chart.

## Scenarios against the models

The NDP scenario of CR-23 is the LTS reference for LTSNEW: net zero by 2050, with the largest cuts in transport (7.4 MtCO2e by 2050, p.16). Its electricity sector is already near 100 percent renewable. The model uses 0.90 for NDCNEW and 0.99 for LTSNEW in 2035 and 2050 (hub 11). The NDC 3.0 power target of 95 percent renewable generation (scout finding on CR-01) relies on the PEG. The PEG Tabla 15.4 implies very small fossil generation (bunker 17 GWh of 13,814 GWh in 2030), but the share was not computed here (one value per row as printed). The scout found that the model counts PWRSUG (sugarcane) as non-renewable. The PEG lists biomass separately (78 GWh a year), and its renewable definition would count it.

## What a deeper study would need

The CLEW-CR-3.0 scenario outputs behind the NDC 3.0, either published by the DCC or read from `clg-admin/ndc_cr` (Energy `SelectedResults.csv`) with permission, to compare NDCcond and NDCincond with NDCNEW. The EPERLab `osemosys-cr-v2` model cited in GUA-23 p.28. The PEG 2022-2040 scenario tables by demand case (chapter 14) and the PEG 2024-2040 update. The CR-23 result database (RAND visualization), to get yearly sector paths rather than 2050 points only. A CAT reassessment once it covers the NDC 3.0.
