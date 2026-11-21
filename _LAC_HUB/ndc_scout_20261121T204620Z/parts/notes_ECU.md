# Notes for GAPS: Ecuador (ECU)

## Judgement calls and reasons

- **Long-term strategy.** The UNFCCC long-term strategies portal could not be read by script. WebFetch returned an empty page, and curl returned a 957-byte bot-check page. The Climate Policy Radar geography page lists no long-term strategy for Ecuador. The second NDC calls the PLANMICC 2024-2070 its long-term strategy (ECU-01 p.10, p.33, p.44, p.113). I registered the PLANMICC (ECU-03) as `LTS-national-not-submitted` and read its chapter 6 (scenarios, targets, indicators; physical p.90 to p.147) in full.
- **Current NDC.** ECU-01 was downloaded directly from the UNFCCC file address (February 2025 folder); the NDC registry page itself was not read. The first NDC (ECU-02) was also downloaded from UNFCCC. Both files start with `%PDF`.
- **Conditional target.** ECU-01 p.55 and p.56 say "8% adicional" (about 10,600 kt). The executive summary (p.10) says the conditional target could reach 8 percent. I read it as 8 percent on top of the 7 percent, 15 percent in total, which matches 10,600 kt being additional (8,800 kt is 7 percent). In alignment, 15 percent is used for the conditional comparison.
- **Sector plans (at most five).** Five plans are cited for quantified energy or transport targets. The NDC names the Plan Maestro de Electricidad 2023-2032 and the PLANEE 2016-2035 as sources of the energy target (ECU-01 p.67). The PLANMICC names the PLANEE, the urban mobility policy (PNMUS) and the electromobility strategy as the basis of its energy and transport hypotheses (ECU-03 p.101, Tabla 14), and the green hydrogen roadmap for hydrogen in transport (p.100). PME, PLANEE and the hydrogen roadmap are registered (ECU-07 to ECU-09). PNMUS and the electromobility strategy failed after three attempts each and are in `parts/sources_pending_ECU.csv`. The 2026 PME adjustment (Acuerdo MAE-MAE-2026-0066-AM and annexes) is cited by neither the NDC nor the PLANMICC and would be a sixth plan, so it was not registered. Its copy was removed from `downloads/ECU/`.
- **Reused files.** ECU-05 (NID) is the earlier download with the same SHA-256 and URL as register row FR2-D3-ECUNID. ECU-07 (PME 2023-2032) and ECU-09 (hydrogen roadmap) are earlier downloads; their SHA-256 values equal the rows of `C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\research\d12_lives_sources.csv`, which also gives their URLs (they are not in that job's `sources.csv`). ECU-06 (CN4/BUR2) is the earlier download `ECU_CN4_BUR2_2022.pdf`; its UNFCCC address comes from a search result, and byte identity with that address was not checked.
- **ECU-06 scope.** The CN4/BUR2 is superseded by the BTR1 (ECU-04). Its first NDC chapter (physical p.623 to p.624) repeats the first NDC scenarios that ECU-04 reprints in updated form. It was searched, not read, and no rows come from it.
- **Energy emissions in the model.** Energy-sector total = CO2e_DE + CO2e_FUG + CO2e_REF + CO2_PP, in Mt CO2e (diesel road factor 0.0741 per PJ in `EmissionActivityRatio.csv`). I used CO2_PP instead of CO2e_PP because CO2e_PP carries the known unintended EmissionActivityRatio differences, while CO2_PP is equal across scenarios. CO2e_sources was not used: it counts fuels at the DIST_* technologies and overlaps the other labels. Its BAU value even falls from 2025 to 2030 (33.45 to 32.56).
- **Renewable categories.** For the PLANMICC non-conventional renewable (ERNC) share I counted solar PV, wind, biogas and biomass plant types (p.108 says the indicator also covers biomass). Hydro counts PPHD, PPHDAM*, PPHROR* and PPIHD. The model has no separate SNI; all generation is used.
- **Comparison years.** The PME expansion runs 2023 to 2032. The model increase is taken from 2025 to 2035, the nearest printed years in the levers file.
- **Electricity share of final energy (ECU-T024).** The delivered-fuel rows of the levers file include fuel to power plants and exports. The model value (ELE over all deliveries except CRU and OPE) is indicative only.
- **Proposals.** PLANMICC phase I values are proposed for NDCNEW, because the NDC builds its target on the PLANMICC model and states no sector numbers. The hub decides whether NDCNEW should follow them. LTSNEW follows the hub decision that LTS equals NDC through 2035.

## Ambiguous targets and how I read them

- **ERNC phase I (ECU-03 p.104, Tabla 15).** The table prints "about 24 percent (about 240 MW)" for 2035, against "about 35 percent (about 3,800 MW)" in 2050 and "about 37 percent (about 8,400 MW)" in 2070. 240 MW cannot give 24 percent of generation, so the MW figure looks like a typing error (perhaps 2,400 MW). The percentage is kept as the target; the 240 MW is only mentioned in the note. The 3,800 MW of 2050 also looks low for a 35 percent share at solar and wind capacity factors.
- **Energy sector efficiency (ECU-03 p.104).** "Save about 8.4 percent, about 6,500 kBEP of national energy consumption" against the trend; footnote 22 says transport is excluded. I compared it with all non-road-transport demand rows of the model.
- **PLANMICC Figure 16 (p.97, read as image).** Its waste labels (2,667; 2,643; 3,255; 4,120 Gg) differ from Figura 36 (2,541; 2,347; 2,785; 3,650 Gg). Both are in `projections_ECU.csv` with a note. The energy labels of Figure 16 add up to Figure 17 (for example 20,245 + 19,039 = 39,284, against 39,200).
- **First NDC conditional target.** The first NDC gives 20.9 percent (ECU-02 p.22); the BTR1 says it was adjusted to 13.5 percent in the implementation plan (ECU-04 p.215). Both are kept.
- **BTR1 projections** use AR2 GWP and IPCC 1996 guidelines (ECU-04 p.231); the second NDC uses AR5 (ECU-01 p.60). They are not comparable with each other or with the 2022 inventory.
- **Quito Metro and Cuenca tram (ECU-02 p.18).** Recorded as 22 km of metro; the 12 km tram is in the note (no sum).

## Solved results against compiled inputs (asked by the hub)

The solved results at 481a7c0 are not consistent with the compiled policy inputs in `Ecuador/ECU_Energy/B1_Output_Params`.
- **Floors far above solved generation.** NDCNEW `TotalTechnologyAnnualActivityLowerLimit` rows add up to 231.5 PJ in 2030 and 255.7 PJ in 2035, against 138.1 and 153.3 PJ of solved total generation. Per plant type the solved/floor ratio is 0.40 to 0.70 for most types. Examples for NDCNEW 2035: PPFOI floor 22.854 against solved 9.181 PJ; PPHDAMAB 26.947 against 17.800; PPHRORAB 40.140 against 24.709; PPWNDON 53.524 against 12.292; PPRDSL 18.305 against 7.348. LTSNEW 2050 floors add up to 354.7 PJ against 203.7 PJ solved (PPWNDON 182.072 against 50.832).
- **Solved values above compiled caps.** NDCNEW 2030: PPHRORAS solved 6.378 PJ against an upper limit of 2.685; PPHRORPM 11.578 against 9.504; PPRNGS 4.254 against 2.529. NDCNEW 2035: PPPVD 8.676 against 5.785.
- **Shares.** The compiled NDCNEW floors imply a renewable share of 0.750 in 2035, while the solved share is 0.805. `ShareValidation` control shares (0.800 in NDCNEW 2035, 0.990 in LTSNEW 2050) match the solver.
- **Reading.** The solved results seem to come from the stage-3 target shares, not from the activity limits now in `B1_Output_Params`. The floors look scaled by about 1.67. BAU is consistent: its floors (112 PJ) are below solved generation (155 PJ in 2035).
- **Same pattern as Costa Rica.** The hub should check how stage 3 builds and applies these limits before the solved values are used.
- **Tables affected.** All model values in `alignment_ECU.csv` are solved values.

## Known-limitation candidates

- **Refinery emission factor.** `model_levers_ECU.csv` rows 8 and 9: the PROCRU EmissionActivityRatio is 0.0038 (CO2_REF) and 0.0036 (CO2e_REF) in BAU, against 0.0043 and 0.0039 in NDCNEW and LTSNEW from 2025. This difference is not in the brief's list of known unintended differences. It raises policy-scenario refinery emissions (CO2e_REF in 2035: 1.344 Mt in NDCNEW, 1.245 in BAU) and makes NDCNEW energy emissions in 2025 slightly higher than BAU (44,648 against 44,565 kt).
- **Distribution losses.** The ELE_DIST InputActivityRatio is 1.1393 (12.2 percent losses) and ELE_TRANS is 1.0398, in every scenario. No grid-loss lever exists in `B1_Scenario_Config.xlsx` (SmartGrid and Electrical sheets).
- **No fuel switching in end uses.** Efficiency sheet rows 8 to 33 (LTSNEW) and 63 to 88 (NDCNEW) scale each fuel; the residential electricity share stays at 38.3 percent and the industrial one at 44.6 percent in 2050 in every scenario.
- **Hydro capacity.** Hydro capacity grows only from 6.18 to 6.34 GW between 2025 and 2035 in every scenario, although the PME adds 4,034 MW of hydro by 2032. TotalAnnualMaxCapacity of hydro types is 99 GW (not binding) in the policy scenarios.
- **Geothermal.** PPGEO TotalAnnualMaxCapacity is 0 in BAU and 99 GW in NDCNEW and LTSNEW (Electrical rows 89 and 155), but no geothermal generation is solved.
- **Hydrogen.** E5INDHYD demand is 0 in every scenario (Efficiency rows 21 and 76), although HYD_G_PROD exists.
- **C1 renewable list.** The renewable list in `model_levers_ECU.csv` does not count PPIBIM or PPGEO. Neither has solved generation, so the shares are not affected.

## Left unchecked

- **Sector models.** The sector models (ECU_AGR, ECU_USCUSS, ECU_IPPU, ECU_WASTE) were not read for values; only technology names were read to name the folder.
- **NDC2 (ECU-01).** Read page by page from the text cache. The adaptation, loss and damage and finance chapters (p.72 to p.118) were read for mitigation numbers only.
- **PLANMICC (ECU-03).**
  - Chapter 6 (p.90 to p.147) was read in full; Tabla 15 (p.104 to p.107) and Figures 16 and 23 were also read as page images.
  - Chapters 1 to 5 and 7 to 8 (diagnosis, process, vision, action plan, finance, gender, MRV) were searched by keyword, and only the pages with hits were read. This deviates from "read in full", for time.
- **BTR1 (ECU-04, 1,119 pages).** Only the NDC tracking and projections part was read (physical p.145 to p.148 contents, p.208 to p.238). The inventory, adaptation and support chapters were not read.
- **NID (ECU-05).** Searched for projections and targets; none found.
- **Sector plans.** PME (ECU-07): only the expansion summary table (p.159) and keyword searches. PLANEE (ECU-08): target tables and summary pages (p.20, p.65, p.67). Hydrogen roadmap (ECU-09): summary page p.6 and keyword searches.
- **NDC2 Figure 6 (p.57).** It plots the trend, unconditional and conditional series without printing values, so no series was copied.

## Incidents

- The UNFCCC long-term strategies portal returned an empty page to WebFetch and a bot-check page to curl.
- The 2026 PME adjustment annexes were copied and cached as ECU-08 by mistake before the selection of sector plans. The copy and its cache were deleted, and ECU-08 was rebuilt for the PLANEE.
- pypdf printed fontTools warnings during the spot check; the extraction still worked.
- The self-check of values against the cited page text found two rows not matching. One value was a sum of two printed lengths (34 km), now replaced by the printed 22 km. The other was a decimal form (12,307.30), now written with both decimals. After the fixes, all 197 numeric values were found on their pages.

## Hub corrections (LAC_NDC_SCOUT hub)

- The emission comparisons ECU-T001, ECU-T002, ECU-T003, ECU-T020 and ECU-T021 in `alignment_ECU.csv`, the matching lines of `changes_since_paper_ECU.md` and proposal row 15 were recomputed by the hub from the single label CO2e_sources (`scripts/hub_fix_ecu_emissions.py`), because the brief forbids summing emission labels. The four-label build described above was dropped.
