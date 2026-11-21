# Notes for GAPS: Jamaica (JAM)

## Judgement calls and reasons

- **LTS copy and date.** JAM-02 is the Climate Policy Radar copy. Its cover says November 2023, its PDF was created on 18 August 2025 and last modified on 27 August 2025, and NDC 3.0 says the strategy was approved in 2024 (JAM-01 p.3, p.22). The UNFCCC record (documents/649405, submission 29 August 2025 per the brief) returned a 212-byte Incapsula page to curl and an empty page to WebFetch. Whether the copy is byte-identical to the UNFCCC file is unknown (`parts/sources_pending_JAM.csv`). The PDF dates make it very likely to be the submitted version.
- **NDC 3.0 file.** The UNFCCC file `2025-09/Jamaica ICTU Final Report Sep19.pdf` and the Climate Policy Radar NDC 3.0 file are byte-identical (same SHA-256); the UNFCCC address is registered as the URL. The same holds for the 2020 update (UNFCCC NDC/2022-06 file and the Climate Policy Radar copy).
- **No BTR1 found.** Three search routes, the UNFCCC listing (bot-check) and four guessed UNFCCC file names (HTTP 404) gave nothing. NDC 3.0 (September 2025) says the BTR will be prepared (p.18). The TNC (JAM-06, 2018) and BUR1 (JAM-05, inventory 2006-2012) are registered as the newest inventory documents. BUR1 has no date on its cover; it is registered as 2016 from a web-search lead (UNFCCC submission 18 November 2016), which no opened document confirms. The BUR1 and TNC inventory totals for 2006-2012 disagree (BUR1 Table ES1 CO2 2012 14,296 Gg, JAM-05 p.3; TNC Table 2 CO2 2012 7,387 Gg, JAM-06 p.11). No value from either inventory is used in the comparison.
- **Sector plans.** Only IRP-2 (JAM-07) qualifies under the brief: NDC 3.0 lists it as a data source (p.5) and its 63.4 percent for 2035 equals the NDC figure. IRP-1 (JAM-08, superseded) was reused from `LAC_sources_archive` (same SHA-256) because NDC 2.0 cites it and it records the earlier 30 percent target; a fresh download of IRP-2 from gpe.gov.jm had the same SHA-256 as the archive copy. Not fetched, because the LTS and NDC take no number from them: National Energy Policy 2009-2030 (its targets are quoted in JAM-08 p.16 and JAM-04 p.2), Electric Vehicle Policy 2023 (JAM-02 p.150), Strategic Framework for Electric Mobility 2022 (JAM-02 p.57), National Biofuels Policy 2010-2030 (JAM-02 p.93), Energy-from-Waste Policy (p.88). No IRP newer than IRP-2 was found in one search (the archive search log of 10 November 2026 found none either).
- **Scope of targets.** Mitigation and mixed targets are listed, including mangrove and seagrass items that NDC 3.0 says were not evaluated quantitatively. Adaptation-only items of the LTS (tourism, health costs, coastal works) are not listed. LTS figures that are scenario results (98 percent power cut, 60 percent industry cut, transport 0.79 Mt) are listed with a note.
- **Emission label.** Emission targets are compared through `CO2e_sources`, the DIST_* fuel distribution technologies (diesel 0.0742758 per PJ, so Mt CO2e). `CO2e_PP` (plants), `CO2e_DE` (end-use demand techs) and `CO2e_DETRN` (road, maritime, jet) are subsets of it, computed with technology-level factors; `CO2e_CEM` (clinker), `CO2e_LIME`, `CO2e_HFC` and `CO2e_LUBRI` are non-energy. No labels were summed. NDC targets that cover energy plus cement are compared on the energy label only, and rows that need both labels are `not compared`.
- **Base year.** The model starts in 2021. 2021 stands in for 2020 in the LTS comparisons (JAM-T045, JAM-T063); targets against 2012 are `not compared`.
- **Status rule.** NDC and sector-plan targets are judged on NDCNEW, LTS targets on LTSNEW; the other ratio is given. Floors met within 10 percent (90 percent renewable in 2040, ratio 0.92) are `matches` by the 10 percent rule although the model is below a stated minimum.
- **Transport units.** The LTS gives fleet shares; the JAM_TRANSPORT Tech_Adoption rows give shares of group activity, which feed the energy model only as E5TRO fuel demand. The model value in the transport rows is the transport-model input share; the energy-model electric share of road energy is in the note.
- **Losses.** The model puts all losses in distribution (ELE_DIST input 1.27, ELE_TRANS 1.0); 1 - 1/1.27 = 21.26 percent is compared with losses as a share of generation. The LTS 2030 milestone (21 percent) matches only by coincidence, so that row is `matches` while the NDC rows are `in documents, not in the model` because no scenario changes the factor.
- **Proposals.** NDC 3.0 items are proposed for NDCNEW; LTS milestones for LTSNEW, with a note where a pre-2035 LTS value conflicts with the hub decision that LTS equals NDC through 2035. For the renewable share the lever that the solver sees is the Stage 1 and Stage 2 curve, not `B1_Scenario_Config.xlsx`. No proposals for AFOLU and waste.

## Ambiguous targets and how I read them

- **LTS 73 percent and 7.25 Mt (JAM-02 p.13).** The parenthesis follows "2020 levels", so 7.25 MtCO2e is read as the 2020 level. The LTS also gives 10.15 Mt for 2019 (p.33), from another source (ClimateWatch), so the two are not on the same basis.
- **LTS 2050 losses.** Table 1 (p.15) says 11 percent, Table 4 and the text (p.54, p.55) say 8 percent. Both rows are listed; the 8 percent row is compared.
- **LTS fuel efficiency year.** Table 1 and the text (p.14, p.61) give 2030; Table 6 (p.62) lists it under 2025. Read as 2030.
- **LTS transport goals attributed to the NDC.** The LTS says the updated NDC set 35 percent urban public transport, 15 percent fuel efficiency and 20 percent alternative fuels by 2030 (p.61), and that forestry targets come from the NDC (p.80). The 2020 NDC (JAM-03) contains none of these numbers. They are listed as LTS targets.
- **LTS fossil phase-out against renewable milestones.** 100 percent fossil phase-out in 2040 conflicts with 90 percent renewable in 2040 in the same tables (p.15, p.55).
- **LTS afforestation.** Table 13 gives 150 ha per year; the text gives 100 ha per year (p.80, p.81).
- **Forest cover baseline.** NDC 3.0 uses 47.9 percent (p.16); the LTS says 30 percent citing Vision 2030 (p.75); the TNC says 40 percent (p.9).
- **IRP-2 internal inconsistencies.** 2035 renewable share 63.4 percent in Tables 11-6 and 11-13 (p.67, p.77) but 56.3 percent in Table 11-7 (p.68); 2030 power emissions 1.29 Mt (p.15, p.62) or 1.26 Mt (p.90); the 65.5 MW IPP retirement in 2033 (p.15) or 2032 (p.62). Table 11-6 shows HFO at 0.0 percent in every year including 2022, which conflicts with Table 11-7 (12.9 percent in 2022); not used.
- **NDC 3.0 renewable and loss targets: conditionality.** They are listed under the Global Stocktake response, and the next sentence says enhanced ambition is contingent on international support (p.14). Recorded as `not stated`.
- **NDC 3.0 target years read from durations.** Three million trees in five years (read as 2030); non-revenue water over 11 years (read as 2036); 200 electric buses in three years from 2023 (read as 2026).
- **Values the hub check will not find as digits.** JAM-T037 (printed "three million"), JAM-T060 and JAM-T061 (value 0 from "phase out 100%"), JAM-T046 (net zero, value 0). JAM-T002 is found by pypdf but not in the pdfplumber cache, because the two-column table interleaves the text.

## Solved results against compiled inputs (requested check)

- **Against the compiled limits.** Solved plant generation (`stage3_results.xlsx`, TotalTechnologyAnnualActivity) breaks the compiled `B1_Output_Params` activity limits in every scenario, 2025 to 2050, 0.5 percent tolerance: BAU 106 technology-years below the lower and 29 above the upper limit, NDCNEW 82 and 52, LTSNEW 86 and 56 (`scripts/JAM/model_numbers.py`). Examples in PJ:
  - Fuel oil: compiled upper limit 0 from 2027 in all scenarios (model_levers lines 57 and 70); solved PPFOI 4.73 (BAU 2030), 3.45 (NDCNEW 2030), 1.56 (NDCNEW 2035), 1.66 (LTSNEW 2035).
  - NDCNEW 2030: PPPVT solved 3.61 against a compiled lower limit of 8.02; PPWNDON 2.11 against 4.32; PPHDAM 0.40 against an upper limit of 0.24.
  - BAU 2030: PPPVT 1.07 against a lower limit of 5.30; PPWNDON 0.28 against 2.85.
  - LTSNEW 2050: PPPVT 23.54 against an upper limit of 22.29; PPWNDON 7.88 against a lower limit of 10.33.
- **Implied shares.** The compiled lower limits imply a renewable share of 75 percent already in 2030 in NDCNEW and LTSNEW and 52.9 percent in BAU (66.0 in 2035, 78.1 in 2050). The solved shares are 39.1 percent (policy) and 13.9 percent (BAU) in 2030. The compiled BAU therefore carries a far greener power plan than the solved BAU.
- **Against the Stage 2 controller.** Solved values stay within the controller lower limit and lower times 1.05 (`_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` sheet CURRENT_LOWER, rows 281 to 304) in every technology-year of all three scenarios. Stage 3 replaces the plant limits from 2025 with controller values (`PIPELINE_WORKFLOW.md`, Stage 3).
- **What does reach the solver from B1.** TotalAnnualMinCapacityInvestment (Electrical rows 86 to 89) is not patched by Stage 3. Solved solar capacity in 2030 equals 57 + 99.83 + 133 + 90 + 90 = 469.8 MW and wind 102 + 3 x 60 + 21 = 303 MW. Demand per fuel, the road emission factors and transport demand also reach the solver unchanged.
- **For the hub.** A renewable share change written only to `B1_Scenario_Config.xlsx` will not reach the solved results unless Stages 0 to 3 are re-run. The renewable share lever is `stage2_apply_v2.py` lines 61 to 75 (and `stage1_share_analyzer_v16.py` lines 97 to 110).

## Model lever not on the brief's known list: road emission factors (T5DSLTRO, T5GSLTRO on CO2e_DETRN)

- **What it is.** `B1_Scenario_Config.xlsx` sheet SmartGrid rows 11 to 18 apply an `Exact_Multiplier` to the EmissionActivityRatio of the road diesel and gasoline demand technologies. The multipliers are the inverse of fuel-efficiency factors in rows 22 (label LTS: 1.15 in 2030, 1.40 in 2050) and 23 (BAU: 1.05 in 2030, 1.30 in 2050). BAU (rows 13 and 14) therefore lowers the factor by 4.8 percent in 2030 and 23 percent in 2050. NDCNEW and LTSNEW (rows 15 to 18) use 1 from 2025, so the factors return to 0.0743 (diesel) and 0.0695 (gasoline). It is a vehicle fuel-efficiency proxy. It is not biofuel blending: the blend block of the B1 script (lines 3702 to 3770) has empty technology lists and is inactive for Jamaica.
- **Effect.** The inactive LTS rows match the LTS targets exactly (15 percent by 2030, 40 percent by 2050), so the policy scenarios appear to have lost the efficiency gain that BAU keeps. `CO2e_DETRN` in 2025 is 2.636 Mt in both policy scenarios against 2.581 in BAU. The lever changes only this label: fuel demand and `CO2e_sources` (computed at DIST_DSL and DIST_GSL with fixed factors) are unchanged. In 2025 `CO2e_sources` is 5.470 in all three scenarios.
- **`model_levers_JAM.csv`.** Lines 2 and 3 are correct but unlabelled. They are better read as a likely unintended inversion than as a policy measure.

## Known-limitation candidates

- **Policy road emission factors above BAU** (SmartGrid rows 15 to 18; model_levers lines 2 and 3): see above. BAU 2050 diesel factor 0.0571 against 0.0743 in NDCNEW and LTSNEW.
- **Road diesel above BAU in NDCNEW** (model_levers line 35; Efficiency row 240): 17.61 PJ against 13.91 in 2040 and 22.83 against 17.87 in 2050, while gasoline falls to 17.57 against 37.42. The diesel and gasoline paths come from the transport model and may reflect a fleet-split error.
- **Grid losses fixed at 21.3 percent in all scenarios** (InputActivityRatio ELE_DIST 1.27); the only loss lever is on the inactive LTS label (SmartGrid row 2).
- **Fuel oil in compiled inputs against the controller.** The compiled inputs phase out PPFOI from 2027 in all scenarios; the controller keeps it (BAU 4.73 PJ in 2030). The B1 workbook and the solved runs describe different power systems.
- **Diesel capacity in LTSNEW 2050.** PPDSL capacity 413 MW (77 MW in 2040, 181 MW in 2045) with 0.007 PJ of generation; likely a reserve-margin artefact of Stage 3, which tags firm generators.
- **Biomass plant.** PPBIM has 5 MW capacity and compiled lower limits (0.15 PJ in BAU) but solved generation 0 in all scenarios; the Stage 3 controller gives it 0.
- **Cement process emissions** (`CO2e_CEM`) identical in all scenarios; no clinker substitution technology.
- **History cells.** The brief's six known history lower-limit cells to 2024 per policy scenario are PPDSL 2022 (BAU 0.5754, policy 0.5645), PPDSL 2024 (0.0348, 0.0342) and PPHDAM 2021 to 2024 (0.4979, 0.4884). Policy scenarios also carry 28 zero-valued lower-limit rows to 2024 for techs absent from BAU (PPBGS, PPGEO, PPPVD, PPPVDS, PPPVTS, PPWNDOFF, PPWNDONS), with no value difference.
- **Storage** (STOELE) is the same in all scenarios: 102.5 MW in 2030 against 264 MW in IRP-2.

## C1 file (`model_levers_JAM.csv`)

- No error found in the rows used. Recomputed from `stage3_results.xlsx`: renewable share 2030 and 2035, capacity of PPPVT, PPWNDON, PPFOI, and emissions `CO2e_sources`, `CO2e_PP`, `CO2e_DETRN`, `CO2e_CEM` for 2025 to 2050 agree.
- Two cautions. The plant-limit rows (lines 39 to 77) do not drive the solved results from 2025; the controller does. The renewable plant list in line 88 (PPBIM PPHDAM PPHROR PPPVT PPWNDON) is right for the solved results, since the other renewable PP techs are capped at 0 by Stage 3.

## Left unchecked

- LTS read page by page via the text cache (194 pages). Figures with data only in graphics were not read as images: Figure 1 (p.33), Figures 2, 4, 6, 7, 9 (p.50, p.52, p.58, p.71, p.77), Figure 5 (p.53), Figure 10 (p.84). p.14 and p.172 were viewed as images (Table 1 check; p.172 is a photo).
- NDC 3.0 (23 pages), NDC 2020 (12 pages) and INDC (9 pages) read in full.
- IRP-2: executive summary, chapters 4, 5, 9, 11 (p.61 to p.77) and 13 read; transmission chapters (p.79 to p.88) and cost tables skipped. IRP-1: only the target pages p.16 and p.143.
- TNC: summary (p.7 to p.13) and mitigation chapter pages p.327 to p.329, p.345 to p.347, p.354 to p.356, p.364 to p.365. BUR1: executive summary and mitigation tables (p.2 to p.6, p.105 to p.110). Neither was read in full.
- The JAM_AFOLU and JAM_WASTE models were not read for values; only technology names, to name the folder. JAM_TRANSPORT was read only for the Tech_Adoption and Mode_Shift rows of `B1_Scenario_Config.xlsx`; its compiled outputs exist only for BAU and LTS.

## Incidents

- UNFCCC record pages (documents/649405, first-biennial-transparency-reports) returned bot-check or empty pages. UNFCCC resource files (BUR1, TNC, NDC files) downloaded normally with curl.
- A search lead `resource/Fourth National GHG Inventory rev Aug42020.pdf` turned out to be Belize's inventory; deleted. The `www4.unfccc.int` TNC address returned an HTML page; deleted.
- No request was refused by the session permission system.
- Helper outputs of the model checks were written to the session scratchpad, not to the job folder. Scripts: `scripts/JAM/model_numbers.py`, `config_dump.py`, `config_rows.py`, `self_check_JAM.py`, `spot_check_JAM.py`, `render_pages.py`, `text_cache.py`, and the four `write_*_JAM.py` writers.
