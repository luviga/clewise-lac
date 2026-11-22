# Step D research notes: Dominican Republic (DR)

Accessed 2026-11-22. Six sources registered (DR-21 to DR-26): 1 official, 2 external, 3 lead. 67 rows in `analyses_DR.csv`. Pending: 0 of 2 fetched. Neither document is published yet. The LT-LEDS is a draft awaiting launch, and the PEN is in its final publication stage.

## The documents

- **DR-21, World Bank CCDR Dominican Republic (external, November 2023).** Staff report. It has two layers. The first is the MANAGE general equilibrium model with BAU, Intermediate and Ambitious scenarios (Figure ES-2, p.10; Table ES-1, p.11). The second is the Electricity Planning Model with BAU or NP, NDC2030 and NZP2050 (p.43 to p.46). It prints accumulated emission reductions and investment needs (p.11), power system costs and investments (p.46) and solar and wind capacity in 2050 (p.44).
- **DR-22, CCDR Annex 3, power sector (external, November 2023).** A slide deck on the EPM runs from the Decarbonizing Energy Pathways project. Scenario table on p.14, one results table per scenario on p.15 to p.17, and key messages on p.3 to p.11: 67 percent renewables in 2050 under NZP2050, grid emissions by year, and EV fleet shares of 2 and 8, 7.2 and 9.3, and 15 and 70 percent.
- **DR-23, IDB monograph 1138 (lead, 2023).** Written by CLG (Quiros-Tortos, Victor-Gallardo and others; contact clg-cr.com, p.4) for the IDB and the Ministry of Energy and Mines. Power-sector model with Robust Decision Making over 1,001 futures. Scenarios Base, Referencia (PEN 2022), Gas natural and Renovables. Prints SENI emissions in 2050 (p.23), about 55 percent non-conventional renewables (p.5), 140 Mt avoided and net benefits (p.20 to p.22).
- **DR-24, LTS-RD documentation (lead, CLG).** Read the Docs PDF build, December 2025 (contributors Victor-Gallardo, Quiros-Tortos, Salazar-Vargas). OSeMOSYS-RD with RDM over 202 futures, built with World Bank support for the long-term strategy (ELP; p.7). Scenarios Tendencial and Estrategia (LTS). Prints national emissions of 28.2 Mt in 2018, about 75 Mt (Tendencial) and 17.4 Mt (Estrategia) in 2050, and a cut of about 76 percent (p.9). It also gives the 2050 generation mix and transport assumptions (p.18, p.19) and sector reductions (p.19, p.25, p.31, p.37).
- **DR-25, DDP Report 2025 chapter (lead).** Written by CLG authors, November 2025. Narrative on the draft LT-LEDS, drafted with World Bank Group support and CLG technical support and pending official launch (p.2). It restates DR-23 results.
- **DR-26, CNE Bulletin No. 9 (official, July 2026).** Summary of the PEN 2025-2038: Escenario tendencial and Escenario alternativo for 2038 (p.28, p.29, infographics checked as page images), USD 5,400 million to reach at least 30 percent renewables by 2030 (p.32), and peak demand of 7,595 MW in 2038 (p.37).

## Government documents they support

DR-23 serves the Ministry of Energy and Mines (foreword, p.7 and p.8) and compares its 2030 avoided emissions with the NDC cut (p.22). DR-24 and DR-25 support the draft LT-LEDS, which NDC 3.0 names as an instrument (scout: DR-01 p.120). DR-21 and DR-22 use the NDC 2020 targets (3.9 Mt below NP in 2030) and the MEM renewable resolution of 25 percent by 2025 and 30 percent by 2030 (DR-21 p.43, p.45). NDC 3.0 itself credits IDB funding (DR-01 p.3). Its BAU is a statistical projection by gas (regression and CAGR methods, annex p.188 and p.189), not one of these models.

## CLG authorship

DR-23, DR-24 and DR-25 are CLG (class lead). Only DR-21, DR-22 (World Bank) and DR-26 (CNE) can back a value for the models.

## Not obtained

The LT-LEDS itself and the full PEN 2025-2038 (see `pending_D_DR.csv`). CCDR Annex 4 (transport deep dive) was downloaded to check it but not registered, because it adds no scenario numbers beyond Annex 3. No IRENA, Climate Analytics or Climate Action Tracker country analysis covers the Dominican Republic with scenario results. The Climate Analytics 1.5 pathway explorer page returned HTTP 404.

## Judgement calls

- DR-22 results tables extract with columns out of order. Only the grid emission rows were kept. They were identified by two checks: demand times emission factor on the same page (for example 29.4 TWh at 337 g per kWh gives 9.9 Mt), and the 3.9 Mt NDC cut against NP in 2030 (9.9 minus 6.0). The renewable share rows are not used, because the NZP2050 row reads 41, 19 and 7 percent, which conflicts with the 67 percent headline on p.3.
- DR-22 p.14 gives 2 percent EVs in 2030 for NP, while p.19 gives 2.6 percent. DR-21 p.46 prints NDC2030 investment of 12.0 billion, while DR-22 p.16 prints 11.9. Both are recorded with notes.
- DR-21 Table ES-1: the transport and AFOLU rows extract with shifted columns. Only the combined and power rows are kept.
- DR-23 Referencia net benefit is printed as "US$ 1 300" without the word millones (p.21). It is recorded as million USD, following the other scenarios on the same page.
- DR-26 gives no year beside the scenario values. 2038 comes from the heading "dos caminos posibles hacia el 2038".
- DR-25 gives USD 3.3 billion of additional investment, while DR-23 gives USD 4,600 million in total, of which 3,300 is generation capex.

## What a deeper study would need

The OSeMOSYS-RD model files and the 202 futures (the CLG repository behind lts-rd) to read the Tendencial and Estrategia series by sector, because the docs print most of them only as figures. When the LT-LEDS is launched, its official values must replace DR-24 and DR-25. The full PEN 2025-2038 compendia (5 compendia per DR-26 p.24) for the generation expansion and renewable shares by year, and a definition of the 25 and 30 percent targets (energy or capacity, with or without large hydro). The statistical NDC 3.0 BAU should be compared with the OSeMOSYS-RD Tendencial, since they come from different methods. The World Bank EPM input book (DR-22 p.18 onward) gives plant costs and limits that could be checked against the model's.
