# Step D research notes: Ecuador (ECU)

Accessed 2026-11-22. Five sources registered (ECU-21 to ECU-25): 1 official, 3 external, 1 lead. 25 rows in `analyses_ECU.csv`. Pending: 1 of 2 fetched (PNMUS), ENEM still pending.

## The documents

- **ECU-21, PNMUS 2023-2030 (official, sector plan, D1).** Ministry of Transport and Public Works, September 2023, with EUROCLIMA+ and AFD support. This is the copy linked from climate-laws.org. Its 2030 goals are institutional, for example 75 percent of local governments with a sustainable urban mobility plan (goal B.1.1, p.57). It sets no modal share, fleet share or emission number that a model could take. The PLANMICC transport hypotheses (ECU-03 p.101, p.106) remain the usable values.
- **ECU-22, World Bank CCDR Ecuador (external, September 2024).** Staff report. ELENA integrated assessment model on the MESSAGE platform (p.87) with scenarios BAU, NDCu, NDCc and NZ (p.88). It prints 17.7 GW and a 99 percent renewable power system in 2050 under BAU, 112.9 TWh and 30.3 GW under NZ, solar at 12.8 percent of generation (NZ) against 8 percent (NDCc), 2.6 Mt CO2e from energy and transport in 2050 (p.52), a 63 percent bus share under NZ, and 3 and 13 percent electric cars and buses under BAU (p.53). Its NDC scenarios follow the first NDC (assumptions to 2025), not the second NDC in force.
- **ECU-23, IDB technical note 3000 (external, September 2024).** Soria and Villamar (USFQ) and Rochedo (UFRJ). Same ELENA model family. Scenarios Base, Politicas Anunciadas (APS), Desarrollo Sostenible (SDS) and Neto Cero 2050 (NZE), modelled on the IEA WEO 2021 (p.5). It prints CO2 from energy and LULUCF in 2050 of 97.2, 24 and 1.7 Mt (p.20), NZE total GHG of about 36 Mt CO2e (p.19), the NZE generation mix (p.15, p.16) and alternative-propulsion fleet shares (p.16, p.17).
- **ECU-24, Climate Analytics 1.5C pathway explorer (external, web page, 2022).** Downscaled IPCC SR1.5 pathways. It gives 37 Mt CO2e in 2030 and about 13 Mt in 2050, excluding LULUCF, for a 1.5C compatible path. It reads the first NDC, at 61 Mt in 2025, but the same page also says 63 Mt. It does not cover the second NDC.
- **ECU-25, AFD news item (lead, web page, December 2022).** Interview with Jairo Quiros, who says his Costa Rican team built the PLANMICC model in OSeMOSYS with Robust Decision Making. No numbers. It is marked lead because its content is the CLG modeller's own account.

## Government documents they support

The PLANMICC (ECU-03) says it used an OSeMOSYS-Ecuador model with an RDM process (ECU-03 p.93, p.94). The second NDC (ECU-01 p.66, item 11) names OSeMOSYS as the projection tool for every sector. ECU-25 ties that model to the CLG team, so the NDC 2026-2035 and PLANMICC projections probably come from CLG work. No CLG report or model files for Ecuador were found; the CLG GitHub organisation lists only OSTRAM and OSTRAM-LAC. ECU-22 and ECU-23 are independent of CLG and use a different model (ELENA), which makes them a useful cross-check of the PLANMICC.

## Not obtained

The ENEM (2021, IDB): see `pending_D_ECU.csv`. A CLG or MAATE technical report on OSeMOSYS-Ecuador. The background note 4 of the CCDR (ELENA application), named on ECU-22 p.88 but not among the OKR files listed for the record. The Energy Strategy Reviews 2021 ELENA paper on the NDC (search lead only; DOAJ returned HTTP 403). Two Zenodo student reports on Ecuador electricity and mobility (OSeMOSYS) were seen and skipped as thin. Climate Action Tracker does not cover Ecuador.

## Judgement calls

- ECU-22 prints the 99 percent renewable power share in the BAU paragraph. It is recorded as BAU, as printed, although it reads like a PME-plus-model outcome.
- ECU-23 writes decimals with commas (97,2 and 1,7). Values are converted to dot decimals.
- ECU-24 gives two different first-NDC levels for 2025 (61 and 63 Mt). The first is recorded with a note.
- ECU-25 is a news page by AFD, but it is classed `lead` because its substance is the CLG modeller's statement.

## What a deeper study would need

The OSeMOSYS-Ecuador model and its futures (from MAATE or the CLG team) to read the PLANMICC and NDC 2026-2035 series by sector and year, and to compare them with the ELENA results of ECU-22 and ECU-23, which use different BAU assumptions. The CCDR background note 4 for the ELENA inputs. The ENEM targets for buses and light vehicles, to define the fleet shares the PLANMICC uses (ECU-03 p.106, p.107). The Plan Maestro de Electricidad (ECU-07) expansion against the ELENA BAU of 17.7 GW in 2050. A check of how each source counts renewables (large hydro is counted as renewable in ECU-22 and ECU-23).
