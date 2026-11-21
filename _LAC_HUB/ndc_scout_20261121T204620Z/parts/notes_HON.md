# Notes for GAPS: Honduras (HON)

## Judgement calls and reasons

- **Which document is NDC 3.0.** The brief's lead record (`climate-laws.org/document/honduras-nationally-determined-contribution-ndc3-0_21f1`) returned HTTP 404 to WebFetch and curl. Its Climate Policy Radar twin holds the April 2025 second update (HON-02) and a one-page scanned cover letter, which was not kept. The NDC 3.0 itself is the UNFCCC file of January 2026 (HON-01), which is byte-identical to the Climate Policy Radar record `..._bd82`.
- **Long-term strategy.** None is submitted, and none is published. NDC 3.0 says the LTS (ENDRCH) is being consolidated and was consulted only as guidance (HON-01 p.14, p.15). The BTR1 describes the 2024 update work, which used OSeMOSYS for energy, transport and LULUCF, but prints no figures (HON-05 p.563 to p.565). No `LTS-national-not-submitted` source was registered, because the newest NDC cites no published national long-term plan. The CLG endrch-hon site was not used. The pending row records the searches.
- **Older energy plans.** The BTR1 also names the Prospectiva Energetica 2017-2038 (more than 80 percent renewable by 2038) and the Hoja de Ruta 2050 (HON-05 p.524). Neither the newest NDC nor an LTS cites them for a number, so they were not fetched. The Prospectiva figure is listed from the BTR1 (HON-T073).
- **Sector plans.** Only the PIEG 2026-2035 (HON-08) was fetched; NDC 3.0 names it for the 70 percent target (p.26). NDC 3.0 was written when only the September 2025 draft existed. I used the final version approved on 16 September 2026 (document control, HON-08 p.2), which is the current plan. The draft was not compared. The ENME (electric mobility) could not be fetched (pending).
- **Earlier downloads.** The BTR1, NIR 2024 and BUR2 were downloaded again from the UNFCCC addresses on 2026-11-21. All three are byte-identical to the copies in `C:\clw_fix\...\d3_ef`, so their URLs are now proven. The BTR1 URL is the one NDC 3.0 cites (p.69). The draft PIEG 2024-2033 and the approved annex copy named in the leads were not used, because NDC 3.0 cites the 2026-2035 plan.
- **NDC 2021 file.** Every copy (UNFCCC, Climate Policy Radar, FAOLEX) is exactly 31,457,280 bytes, with the same SHA-256 and no `%%EOF` marker. All 68 pages open and the text extracts through p.66; p.67 and p.68 are the back matter. It was used as is.
- **NDC 3.0 arithmetic.** The sector percentages on p.25 are shares of the national net BAU, not of each sector's BAU: 2,519.1 / 50,381.3 = 5.0 percent. The text says the sector values are 'during the implementation period 2021-2030', but they add up to the single-year national target, so they are read as the reduction in the target year. The cumulative reading is given in the alignment note.
- **Emission label.** Every emission comparison uses `CO2e_sources` alone. It is the energy-wide total, since every fossil fuel passes through a DIST_* technology, and is assumed to be in Mt CO2e (diesel 0.0743, LPG 0.0632 per PJ). The other labels cover parts of the same fuel: CO2e and CO2 for T4 transport, CO2e_DE for T5 final use, CO2e_PP for plants. They are never added, and Health is not a greenhouse gas. `CO2e_sources` does not carry firewood CH4 and N2O, which the inventory's energy sector does, and it does count LPG exports (see below).
- **Power-sector comparisons with the PIEG** use CO2_PP over the scenario's own 2025 to 2030 and 2035 path, because the PIEG measures against 2025. Plant emission factors change between BAU and the policy scenarios from 2025 (a known unintended difference), but they are constant within each scenario after 2025.
- **Unlisted emission factor differences.** These are DIST_GSL (0.069543 to 0.0661) and T4GSL_* (CO2 0.0693 to 0.0658) from 2026. They come from the ethanol blend in `B1_Base_Scenarios_Adj_Parallel_Honduras.py` lines 3712 to 3769: 0 in 2025, 4.99 percent in 2030 and 5 percent in 2035, in every scenario except BAU, NDCincond and NDCcond. The biodiesel list `Diesel_Techs` is empty (line 3714), so diesel factors do not change. This lever carries NDC 3.0's 5 percent biofuel target only in part (HON-T024).
- **Vehicle targets.** The documents count vehicles; the model holds output shares by group. Fleet shares were compared directly with output shares, and the note says so.
- **Firewood.** 2012 lies before the model start. The model cut is measured from 2018, and the per-household target was compared with total residential demand.
- **Status rule.** Status is judged on NDCNEW for NDC and plan targets, and the LTSNEW ratio is given too. HON-T018 (70 percent in 2030) is `matches` by the 10 percent rule (ratio 0.93), but the model sits below a stated floor. HON-T094 (retirements) compares a derived gross figure.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW. LTSNEW follows the hub decision that LTS equals NDC through 2035. The PIEG gas item is proposed as class A but marked as an indicative sector plan.

## Ambiguous targets and how I read them

- **Three national totals in NDC 3.0.** The 2035 reduction is 12,847.2 Gg on p.23. On p.22 a '19.6 percent cumulative 2021-2035' is said to equal 8,564.8 Gg, which is the 2030 value. On p.25 a 'national mitigation target' of 7,268 Gg is printed for 2021-2035. I read 12,847.2 Gg and 19.6 percent as the 2035 single-year target (12,847.2 / 65,616.6 = 19.58 percent). The 7,268 is listed but not compared.
- **17 or 16 percent.** NDC 3.0 says it keeps the second update's '17 percent'. The second update states 16 percent plus 1 percent for LULUCF (HON-02 p.3). Both are listed.
- **Sector split in the second update.** p.3 gives energy 9, agriculture 5, IPPU 1 and waste 1 percent; Cuadro 3 on p.11 swaps agriculture and IPPU. The 2021 update (HON-03 p.30) agrees with p.3.
- **IPPU, waste and LULUCF in 2035.** The 2035 column on p.25 says 'respecto al BAU en 2030' for these three; I read it as 2035.
- **Electrification base year.** The +3 and +5 point targets give no base. 2022 is assumed, the base of the intensity target in the same paragraph.
- **Electricity intensity.** '3.4 kWh/USD' and '4 kWh/USD' are recorded as printed. As intensity reductions they look too large, so the unit or scale may be wrong. Not compared.
- **BTR1 HCFC.** The text says 15 percent of baseline by 2030 (p.525), while Table 3-6 lists an import maximum of 2.5 percent in 2030 (p.552). Both are listed.
- **Removals in the BAU table.** In projections, LULUCF removals printed in parentheses are given as positive magnitudes with the unit 'Gg CO2e (removal)'.
- **Word values.** HON-T075 (total HCFC elimination by 2040) has value 0 for a word, so the hub value check will report it not found. HON-T030 (urban mobility plans) has no number.

## Solved results against compiled inputs (requested check)

- **Against the compiled limits.** Solved plant generation (`stage3_results.xlsx`, TotalTechnologyAnnualActivity) does not follow the compiled activity limits in `HON_ENERGY/B1_Output_Params`. Checked 2025 to 2050 with a tolerance of 0.5 percent: 169 BAU, 306 NDCNEW and 281 LTSNEW technology-years are outside the compiled range. Examples in PJ:
  - NDCNEW 2030: PPFOI 16.395 solved against a compiled value of 11.531 (lower equals upper); PPCOK 2.984 against 2.061; PPPVT 10.056 against 14.669; PPWNDON 7.218 against 9.421; PPHDAM 7.818 against 6.682.
  - NDCNEW 2035: PPPVT 17.814 against 18.698; PPWNDON 12.787 against 12.010.
  - NDCNEW 2050: PPWNDON 24.572 against 20.229.
  - LTSNEW 2050: PPPVT 59.198 against 54.694.
  - BAU 2030: PPHDAM 7.818 against a lower limit of 9.086; PPPVT 6.998 against an upper limit of 4.859.
- **Against the Stage 2 controller.** The solved results match `_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` (CURRENT_LOWER, Honduras) exactly: no technology-year is below the controller lower limit or above lower times 1.05. Stage 3 replaces the plant limits from 2025 (`PIPELINE_WORKFLOW.md`, Stage 3). Two consequences follow:
  - The compiled NDCNEW lower limits imply a 75 percent renewable share in 2030, while the controller and solved share is 64.8 percent.
  - The renewable share lever for the solved runs is `stage1_share_analyzer_v16.py` lines 97 to 110, where Honduras has no override. Changes written only to `B1_Scenario_Config.xlsx` Electrical rows 82 to 101 and 162 to 181 will not reach the solved results unless Stages 0 to 3 are re-run.
- **IMP_ELE.** The known unintended difference (BAU 99,999, policy 0) has no effect on the solved results: imports are 0 in every scenario, BAU included.
- **Transport.** Transport limits are not patched by Stage 3. The solved electric shares match the compiled limits; for example, NDCNEW cars in 2035 are solved at 0.1998 against a compiled limit of 0.6175 over 3.0904.

## Known-limitation candidates

- **LPG export demand differs between BAU and the policy scenarios.** This is not on the brief's list. E5EXPLPG is held at 11.41 PJ from 2025 in BAU, through `B1_Scenario_Config.xlsx` sheet Efficiency row 92, a BAU-only override mislabelled 'Demand Commecial Electricity'. NDCNEW and LTSNEW have no such row and grow to 14.37, 17.57, 21.48 and 39.25 PJ in 2025, 2030, 2035 and 2050 (`model_levers_HON.csv` line 31).
  - DIST_LPG carries the `CO2e_sources` factor 0.063155, so the policy scenarios gain about 0.19 Mt in 2025, 0.39 in 2030, 0.64 in 2035 and 1.76 in 2050.
  - This is why NDCNEW `CO2e_sources` in 2025 (11.188) exceeds BAU (11.062), and why `CO2e_DE` is higher in the policy scenarios than in BAU in every year.
- **Gas plants built but never run.** PPNGS capacity reaches 0.74 GW in BAU, 1.30 GW in NDCNEW and 2.26 GW in LTSNEW by 2050 (line 186), with zero generation in every year. The controller lower limit for PPNGS is 0, so Stage 3 sets its activity upper limit to 0, while the 1.15 reserve margin still builds it as firm capacity.
- **Policy has fewer hybrid cars than BAU.** BAU forces TRAUTHG through a lower limit (1.0 percent of car output in 2035, line 111). NDCNEW and LTSNEW only cap it at 2 percent (Tech_Adoption rows 154 and 184), so the solver builds none.
- **Electrification identical in BAU and policy.** The policy demand cuts are a uniform percentage across fuels, so the electric share of residential, commercial and industrial demand is the same in all three scenarios (24.7 percent in 2022, 30.9 in 2030, 31.8 in 2035).
- **Model BAU energy emissions against the documents.** `CO2e_sources` BAU is 9.76 Mt in 2022, against an inventory energy sector of 10.88 Mt (HON-01 p.11), which includes firewood CH4 and N2O. It is 12.72 and 14.25 Mt in 2030 and 2035, against an NDC 3.0 energy BAU of 9.16 and 8.96 Mt, which comes from a linear projection that declines.
- **Fuel oil in NDCNEW after 2035.** PPFOI generation rises again from 13.93 PJ in 2035 to 22.24 PJ in 2050, with 0.88 GW installed (lines 164, 179). The 75 percent renewable share is held flat, so fossil output grows with demand.
- **Battery storage.** The PIEG plans 215 MW of stand-alone batteries and 685 MW of batteries in hybrid solar and wind plants (Tabla 43, HON-08 p.82). No storage technology has capacity in the Honduras results.

## C1 file (`model_levers_HON.csv`)

- No error found in the rows used. I recomputed from `stage3_results.xlsx` the renewable shares of 2030 and 2035, the `CO2e_sources`, `CO2e_PP` and `CO2_PP` values of 2025, 2030, 2035 and 2050, and the installed capacity; all equal the file.
- Two cautions:
  - As for Guatemala, the `input_difference` plant limit rows do not drive the solved results from 2025.
  - The electricity import row (line 208) is empty because imports are zero.

## Left unchecked

- **NDC 3.0** was read in full, every page through the text cache. The pages with little text (p.1, 9, 19, 33, 45, 51, 59, 64, 71, 72) are photographs or section covers. p.66 is the diagram of the monitoring system (caption in the text layer), not viewed as an image. p.25, p.26 and p.68 were also read as images: p.68 is the cover of the ICTU appendix, and no appendix content follows.
- **Second update** (20 pages) and **INDC** (8 pages) were read in full. **NDC 2021 update:** the mitigation chapters (p.9 to p.47) were read in full; adaptation, finance and MRV (p.48 to p.66) were not.
- **BTR1:** chapter 3 (mitigation and NDC tracking, p.494 to p.579) was read in full. The inventory chapters were not read beyond the values that NDC 3.0 quotes from them. Chapters 4 to 6 were not read.
- **BUR2:** the mitigation chapter (p.72 to p.94) was read; p.90 to p.93 (REDD+, carbon markets) were skimmed for numbers. The NIR 2024 (HON-06) was searched for projections and none were found; no value is cited from it.
- **PIEG:** the executive summary, chapter 4.1, the emission factors, the demand projection, chapter 6.3.5 (the selected scenario), 6.3.7 to 6.5 and the conclusions were read. The other scenarios and the cost chapters were not.
- The AFOLU, IPPU and waste models were not read for values; only their technology names were read, to name the folder.

## Incidents

- The lead record `..._21f1` returned 404 on climate-laws.org.
- The UNFCCC long-term strategies portal returned an Incapsula page to curl and an empty page to WebFetch.
- The IAIP transparency portal returned HTTP 403.
- The Article 6 initial report (www4.unfccc.int Submissions Staging, cited by HON-01 p.22) returned an HTML application page, not a PDF. It was not kept; it is not a required kind.
- One empty shell heredoc was run by mistake while checking the table writer. It did nothing and wrote no file. All scripts were written with the file tool.
- No request was refused by the session permission system.
- Helper outputs of the self-checks went to the session scratchpad, not to the job folder. Scripts: `scripts/HON/model_numbers.py`, `check_solved_vs_inputs.py`, `self_check_HON.py`, `config_index.py`.
- The self-check uses the hub rules: 250 of 252 values were found on the cited page. Not found: HON-T075, whose value 0 stands for a word. No value: HON-T030.
