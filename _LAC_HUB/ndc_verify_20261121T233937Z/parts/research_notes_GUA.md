# Research notes, Guatemala (step D)

Accessed 2026-11-22. Six new sources: the ENDBE portal copy (official, from D1), three CLG documents (lead) and two external sources. Analyses file: `analyses_GUA.csv`, 15 rows. Few rows carry numbers, because none of the sources found prints Guatemala scenario results.

## Confirmed leads from the NDC 3.0

GUA-01 p.4 (Reconocimiento) credits technical and financial support from the IDB, the 2050 Pathways Platform and UNDP through the Promesa Climatica (Climate Promise) initiative. GUA-01 p.5 (Creditos) thanks the Climate Lead Group (CLG), the OES and CEAB of the Universidad del Valle de Guatemala and Universidad Galileo for technical support. GUA-01 p.87 cites the CLG and 2050 Pathways guide (GUA-23). The NDC method (p.28 and p.29) rests on two documents that are not public: MARN (2026a), the UVG LULUCF emissions tool and user guide (reference on p.85), and MARN (2026b), Producto 5 of a Climate Promise advisory on emissions accounting for the NDC 3.0 (reference on p.86). The energy, transport and IPPU mitigation scenario is an adjustment to an extrapolated BAU (1,000 MW of renewables entering 2030 to 2033, E10 from 2027, an HFC freeze). The NDC names no energy system model.

## The analyses

- **GUA-21, ENDBE, UNFCCC portal copy, official.** This is the D1 document, not a supporting analysis. It was prepared with USAID support through the LEDS Guatemala project (p.4). A comparison of the numbers in GUA-21 and GUA-04 (the FAOLEX copy) found the same content figures. The differences are page numbers, the 2021 reprint marks and a figure of more than 200 participants in the GUA-21 front matter. The two copies are not byte-identical.
- **GUA-22, DDP Report 2025 chapter, lead (CLG authorship: Angulo, Madrigal, Quiros-Tortos).** It describes the ENDBE update now under way: OSeMOSYS models, Robust Decision Making and a cost-benefit analysis, more than 150 stakeholders, investment scenarios for several ambition levels, and an ENDBE financial dashboard for MINFIN (p.3, p.4). It prints no scenario results. It says the ENDBE update is expected to inform the next NDC and the PANCC (p.3). It cites an 80 percent renewable target for 2027 from the MEM generation expansion plan 2024-2054 (p.4).
- **GUA-23, RDM practical guide (2050 Pathways and CLG, 2024), lead.** It is a method guide and is cited by GUA-01 p.87. Guatemala appears as an ongoing LTS project (p.7) with OSeMOSYS CLEW tools (p.28), preceded by capacity building in which the University of Costa Rica trained two Guatemalan universities (p.54).
- **GUA-24, CLG GitHub repository `clg-admin/GUA_LTS`, lead.** OSeMOSYS energy and transport models in three scenario folders (Escenario_alto, Escenario_medio, Escenario_bajo), plus PIUP, waste and AFOLU models. The GitHub API tree, which was not saved as a source, also shows AFOLU folders named BAU and NDP with Alta, Media and Baja variants, and result files (SelectedResults.csv, GUAOutput.csv). No values were taken from the repository.
- **GUA-25, IDB GU-T1328 project page, external.** Technical cooperation approved on 2022-09-08 (USD 550,000, French Climate Fund for LAC, now closed) to build a net-zero LTS based on the DDPLAC initiative. It is the IDB support that GUA-01 p.4 acknowledges. No output document is linked.
- **GUA-26, IRENA Renewable Energy Roadmap for Central America (2022), external.** REmap scenarios BES, PES, TES and DES for seven countries. The printed values are regional (renewable share of generation 70 percent in 2018, 59 percent in PES 2050 and 97 percent in DES 2050, p.34). Guatemala appears only in figures. The rows are labelled as regional and must not be read as Guatemala values.

## What could not be obtained

- The MEM Plan de Expansion Indicativo del Sistema de Generacion 2024-2054: mem.gob.gt returned a Cloudflare page (HTTP 403), which was not passed, and the CNEE copy returned "Sitio en mantenimiento" (HTTP 503).
- The Deloitte and Enel Hoja de Ruta de Transicion Energetica de Guatemala 2050 (November 2022): cop.impulsouth.org returned a bot check ("Making sure you're not a bot") and enel.com.co returned "Pardon Our Interruption". Neither was passed.
- The UNDP page on the NDC 3.0 process (https://www.undp.org/es/node/564501): HTTP 403.
- MARN 2026a and 2026b: one search found no public copy.
- No World Bank CCDR for Guatemala was found. Climate Action Tracker does not cover Guatemala.

## Judgement calls

- GUA-22 and GUA-23 are classed lead because CLG staff wrote them, even though DDP/IDDRI and 2050 Pathways host them.
- The GitHub folder names (GUA-24) are recorded as scenario names with no definition. The repository has no documentation page.
- IRENA (GUA-26) is registered under Guatemala only. It covers Costa Rica too (see the Costa Rica notes) and Honduras, so the hub may want to cross-reference it rather than register it again.

## Scenarios against the models

None of these analyses prints a Guatemala renewable share, emissions path or fleet share that could stand beside BAU, NDCNEW and LTSNEW. The NDC 3.0 itself sets 80 percent renewable generation by 2035 (GUA-01 p.40 and p.102), above the 0.75 that the model uses for NDCNEW in 2035 (hub 11). The CLG ENDBE update (GUA-22, GUA-24) is the closest relative of LTSNEW. Its results are not published.

## What a deeper study would need

The ENDBE update results (the CLG OSeMOSYS high, medium and low scenarios, with their cost-benefit tables and the MINFIN dashboard), either published by MARN or read from `clg-admin/GUA_LTS` with the government's agreement. The MARN 2026b Climate Promise report holding the NDC 3.0 measure sheets and the BAU extrapolation. The MEM PEG 2024-2054 and the 2040 roadmap behind the 80 percent and 1,000 MW targets. AMM generation statistics, to recompute the renewable share as the NDC defines it.
