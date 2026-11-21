# Notes for GAPS: Guatemala (GUA)

## Judgement calls and reasons

- **Long-term strategy.** The ENDBE (GUA-04) is registered with kind `LTS`. The BTR1 calls it the country's long-term mitigation strategy (GUA-05 p.260, Tabla 4.6), and the brief's lead says it is on the UNFCCC portal. I could not open the portal to confirm the listing or its date. WebFetch returned an empty page, curl returned an Incapsula bot-check page, and three guessed UNFCCC file names returned 404. The copy used is the FAOLEX file linked from the UNEP LEAP record, whose date of text is 2018. Whether it is byte-identical to the portal file is unknown (`parts/sources_pending_GUA.csv`).
- **Newest NID.** The BTR1 (GUA-05) contains the National Inventory Document (1990 to 2022) as its Section I, so no separate 2024 or 2025 NID was sought. GUA-06 is the older inventory report (1990 to 2018, version 2 of 14 August 2023). It is listed for completeness; no value is cited from it.
- **First NDC.** GUA-03 is the INDC dated 29 September 2015, which the BTR1 counts as the first NDC from 2017 (GUA-05 p.251).
- **NDC 2021 copy.** The UNFCCC NDC folder also holds `Contribucion Nacionalmente Determinada Guatemala.pdf`. Its server sends exactly 62,914,560 bytes with no end-of-file marker, and the first pages show it is the same 2021 update. I deleted it and used the complete 230 MB file from the 2022-06 folder (GUA-02, 94 pages).
- **Sector plans.** Only the Plan Nacional de Energia 2017-2032 (GUA-07) was fetched. The LTS cites it for a quantified energy target (64 percent renewable in 2032, GUA-04 p.24), and the BTR1 lists it (p.264).
  - Not fetched because no quantified energy or transport target is cited from them: the Politica Energetica 2013-2027 and the Politica Nacional de Eficiencia Energetica 2023-2050 (named in GUA-01 p.39, p.41, p.45); the Politica Energetica 2019-2050 and the Plan de Expansion Indicativo del Sistema de Generacion 2020-2050 (BTR1 Tablas 4.13 and 4.16); and the electric mobility law (Decreto 40-2022).
  - NDC 3.0 does not cite a source for its 1,000 MW and 80 percent figures. The documents behind them, MARN 2026a and 2026b and the measure sheets, are "available at MARN" (GUA-01 p.134) and not published.
- **Scope of targets.** Mitigation targets and joint mitigation and adaptation targets are listed. Adaptation-only targets in NDC 3.0 are not listed: health, water, irrigation, coast and reef, roads, information systems. Superseded NDC 2021 and INDC targets are listed and marked superseded.
- **Emission label.** Emission targets are compared through `CO2e_sources`, the DIST_* fuel distribution technologies. I assume Mt CO2e, because the emission factors are 0.0743 per PJ for diesel and 0.0632 per PJ for gasoline. `CO2e` overlaps it: plants, T4 transport and T5 demand techs, about 1 point higher. `Accidents`, `Congestion` and `Health` are not greenhouse gases. No labels were summed.
- **Status rule.** Status is judged on NDCNEW for NDC and sector-plan targets and on LTSNEW for LTS targets; the other ratio is given. The 80 percent renewable floor for 2035 is `matches` by the 10 percent rule (75 against 80, ratio 0.94), but the model is below a stated minimum. The hub may prefer `same direction, different size`.
- **Vehicle targets.** The documents count vehicles; the model holds output shares. For GUA-T016 and GUA-T017 I derived an upper-bound fleet share from the January 2024 fleet of 5.3 million (GUA-01 p.45) and the September 2025 baselines (p.107). The model value is the electric share of car output and the hybrid share of car output respectively.
- **Capacity base year.** The annex gives base year 2025 for the 1,000 MW target, so the model increase is measured from 2025 to 2035.
- **Firewood.** The model value for GUA-T078 is the cut in residential firewood demand. The plan's 2030 figure is derived from Tablas 10 and 11 (GUA-07 p.79, p.80).
- **ENDBE energy and transport.** For GUA-T059, the energy (374 Mt) and transport (80 Mt) cumulative reductions were summed to 454 Mt to match the model's energy-system label. Industry (103 Mt) mixes process and energy emissions and was left out.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW; LTSNEW follows the hub decision that LTS equals NDC through 2035. For the renewable share, the lever that the solver actually sees is the Stage 1 target curve and the Stage 2 controller, not `B1_Scenario_Config.xlsx` (see below). No proposals are written for the AFOLU, IPPU and waste models.

## Ambiguous targets and how I read them

- **Conditionality of the 23.7 percent target.** The NDC says it will be met with national resources, complemented in forests by results-based payments and cooperation (p.28), and with "national and international resources" (p.132). It never labels the target conditional or unconditional. Recorded as `not stated`.
- **NDC 2021 clean generation.** Cuadro 3 (p.72) says 80 percent of generation from clean energy by 2030. p.77 says renewables are 80 percent of the "energy matrix". ENE-1 counts natural gas as clean (p.71). Read as a generation share that may include gas.
- **NDC 2021 ethanol.** No year is printed for the 10 percent blend (p.77); I read it as 2030. The BTR1 roadmap expected 15 percent by 2030 (p.254); NDC 3.0 keeps E10.
- **Plan Nacional de Energia.** The renewable mix is said to save 10.82 Mt in 2032 (p.70). Yet the whole plan cuts energy emissions from 16.82 to 11.91 Mt, only 4.91 Mt (p.92). Both are listed. The 2016 renewable share is 58 percent in GUA-07 (Grafica 22, p.68) and 54 percent in GUA-04 (p.24).
- **ENDBE stoves.** "100,00 hogares" on p.26 is read as a misprint, either 10,000 or 100,000. The value recorded is the 11 Mt CO2e reduction in 2050.
- **ENDBE p.30 and p.17.** These pages carry text in a broken font. p.30 was read as an image for the options list; the 80 Mt figure is also in the text layer.
- **PRE 10.5 Mt (GUA-05 p.254).** No period is printed. The target year is set to 2025 as the likely end of the ERPA period; this is uncertain.
- **UTC-2 value 0.12933 (GUA-T047).** It has five decimals, so the hub value check, which tries at most four, will report `no_value`. It is printed on GUA-02 p.71. GUA-T012 (five indicators) is printed as the word "cinco", and GUA-T011 has no number.

## Solved results against compiled inputs (requested check)

- **Against the compiled limits.** The solved plant generation (`stage3_results.xlsx`, TotalTechnologyAnnualActivity) does not respect the compiled activity limits in `GUA_ENERGY/B1_Output_Params` in any scenario. Checked 2025 to 2050 with a tolerance of 0.5 percent: 790 technology-years are outside the compiled range. Examples in PJ:
  - NDCNEW 2030: PPCOA solved 17.218, compiled lower 12.597 and upper 13.856. PPNGS 5.830 against 4.115 to 4.526. PPPVT 6.446 against a lower limit of 13.133. PPWNDON 4.668 against a lower limit of 7.173. PPHDAM 21.317 against an upper limit of 19.867.
  - NDCNEW 2035: PPNGS 4.725 against a lower limit of 7.363. PPCOA 18.224 against an upper limit of 17.330.
  - LTSNEW 2035: PPCOA 21.579 against an upper limit of 19.937. PPPVT 18.104 against a lower limit of 23.414.
  - LTSNEW 2050: PPWNDON 119.254 against an upper limit of 81.858.
  - BAU 2030: PPPVT and PPWNDON solved 0 against lower limits of 3.636 and 1.888.
- **Against the Stage 2 controller.** The solved results match `_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` (sheet CURRENT_LOWER, Guatemala) exactly: 0 technology-years below the controller lower limit or above lower times 1.05. The reason is that Stage 3 replaces the plant lower and upper limits from 2025 with controller values (`PIPELINE_WORKFLOW.md`, Stage 3). Two consequences follow:
  - The compiled NDCNEW limits imply a 75 percent renewable share already in 2030 (share of lower limits 0.7500), while the solved 2030 share is 0.658.
  - The renewable share lever for the solved runs is `stage1_share_analyzer_v16.py` lines 97 to 110, where Guatemala has no override.
- **For the hub.** Any change written only to `B1_Scenario_Config.xlsx` for plant activity will not reach the solved results unless Stages 0 to 3 are re-run. Unlike Costa Rica, the solved fossil generation here is not below the controller floors.
- **Transport.** Transport limits are not patched by Stage 3, and the solved electric shares match the compiled limits. For example, cars in NDCNEW 2035 are 0.2002 solved against 0.1998 compiled.

## Known-limitation candidates

- **Model BAU energy emissions are high against the documents.** `CO2e_sources` in BAU is 25.90 Mt in 2025 and 43.10 Mt in 2035 (`model_levers_GUA.csv` line 186). The 2022 energy inventory is 21.32 Mt (GUA-05 p.274), and the NDC 3.0 energy BAU for 2035 is 28.51 Mt (GUA-01 p.29). Model BAU coal generation alone is 22.3 PJ in 2035, at an emission factor of 0.369 per PJ.
- **Policy emissions exceed BAU in 2025.** `CO2e_sources` is 26.78 in NDCNEW and LTSNEW against 25.90 in BAU. The cause is the IMP_ELE lower limit of 0 in the policy scenarios (known unintended difference), which pushes domestic generation up.
- **Fuel oil capacity in LTSNEW 2050.** PPFOI installed capacity is 4.269 GW with 0.335 PJ of generation (line 154), against 0.85 GW in 2040. This looks like a reserve-margin artefact of Stage 3, which tags firm generators.
- **Hybrids.** LTSNEW caps hybrid cars at an activity of about 0.22 (lines 130, 131) against 5.03 in BAU in 2050 (line 88). The LTS scenario has fewer hybrids than BAU.
- **Cable car.** E6AERO demand and T5ELEAERO costs exist only for the NDP scenario (`B1_Scenario_Config.xlsx` sheet Efficiency row 13, SmartGrid rows 4 and 5). NDCNEW and LTSNEW cannot represent the Aerometro.
- **E10 timing.** The blend starts at 5 percent in 2025 in the policy scenarios (B1 script line 3617), one year before the NDC date and before the BTR1's reported start of January 2026.

## C1 file (`model_levers_GUA.csv`)

- No error found in the rows used. One caution: the `input_difference` rows for plant limits (TotalTechnologyAnnualActivityLower and UpperLimit, PP techs) do not drive the solved results from 2025; the Stage 2 controller does (see above). The `solved` rows are correct against `stage3_results.xlsx`: I recomputed the renewable shares for 2030 and 2035 and the emissions for 2030, 2035 and 2050.

## Left unchecked

- The AFOLU, IPPU and waste sector models were not read for values. Only their technology names were read, to name the folder.
- BTR1 Section I (inventory chapters) was searched, not read page by page; it holds no projections. BTR1 Section II (NDC tracking, policies) was read in full. GUA-06 was searched for projections; none were found.
- NDC 3.0 was read in full. The annex matrices for the adaptation-only sectors (p.110 to p.130) were skimmed for numbers only.
- ENDBE figures and MAC curves (p.25, p.31, p.36, p.42, p.47, p.51, p.54) were not read as images. The option names in the annex (p.61 to p.66) were checked as images on p.61 only; they carry names, not numbers.
- Plan Nacional de Energia: chapters 8.1 to 8.3 were read; the context chapters (p.1 to p.59) were not.

## Incidents

- First attempt at the alternative NDC 2021 URL: truncated file (no end-of-file marker), deleted.
- OLADE copy of the ENDBE: HTTP 404 HTML page, not kept.
- UNFCCC LTS portal and an unfccc.int documents page: bot-check or empty page.
- Climate Policy Radar API search: HTTP 404 JSON.
- No request was refused by the session permission system.
- Helper outputs of the solved-versus-input checks were written to the session scratchpad, not to the job folder. Scripts: `scripts/GUA/check_solved_vs_inputs.py` and `scripts/GUA/controller_check.py`.
