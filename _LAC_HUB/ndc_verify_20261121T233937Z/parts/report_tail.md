
## 5. Supporting analyses found and what they add

38 documents were added (`sources.csv`): 7 official, 15 external, 16 lead (CLG). 258 printed results are in `analyses_<code>.csv`, every one found on its cited page (253 by text search, 5 by the hub on the rendered page or saved HTML). The comparison with BAU, NDCNEW and LTSNEW is in `analyses_comparison.md`.

| Country | Analyses (class) | What they add |
|---|---|---|
| Costa Rica | ICE PEG 2022-2040 (official, cited by NDC 3.0); RAND and IDB cost-benefit of the NDP (external); Climate Action Tracker (external); DDP chapter and `ndc_cr` repository (lead) | The PEG gives yearly generation by source (fuel oil 17 GWh of 13,814 GWh in 2030) behind the 95 percent target; RAND gives the NDP against no decarbonization (net zero against 18.8 Mt in 2050, 41 billion USD net benefit). NDC 3.0 was built on CLEW-CR-3.0, which the CLG repository holds. |
| Dominican Republic | World Bank CCDR and power annex (external); CNE bulletin on the PEN (official); IDB monograph 1138, LTS-RD documentation, DDP chapter (lead) | An independent power model with NP, NDC2030 and NZP2050 (grid emissions 14.3, 8.7 and 0 Mt in 2050; 67 percent renewables in NZP2050). The long-term strategy is still a draft. |
| Ecuador | World Bank CCDR and IDB note 3000 (external, ELENA model); Climate Analytics 1.5 C page (external); PNMUS (official); AFD interview (lead) | The only model family independent of the PLANMICC's OSeMOSYS model; it counts large hydro as renewable and follows the first NDC. The PNMUS sets no number a model could take. |
| Guatemala | ENDBE UNFCCC file (official); IRENA Central America roadmap and IDB project page (external); DDP chapter, RDM guide, `GUA_LTS` repository (lead) | No Guatemala scenario results published. The NDC 3.0 credits the IDB, 2050 Pathways, UNDP and CLG; its BAU rests on two unpublished MARN reports. |
| Honduras | ENME and SEN Prospectiva (official); UNEP green economy study and World Bank CCDR (external); ENDRCH documentation (lead) | The Prospectiva compares four power and transport scenarios (CO2 19 to 56 percent below its reference in 2050); the ENME confirms 3 percent electric vehicles in 2030 but not the NDC's 7.5 percent for 2035. NDC 3.0 credits CLG-Libelula with its drafting. |
| Jamaica | World Bank and Vivid Economics 2020 (external); Climate Analytics project page (external); jam-lts documentation, six pages (lead) | The LEAP study behind the 2020 NDC update (25.4 and 28.5 percent below BAU in 2030). The LTS numbers rest on 2021 Vivid Economics reports that were not found. The jam-lts cost-benefit (preliminary) is CLG work. |

## 6. Values and names held in code

`script_constants.csv` lists 11,170 values and names written in code outside `_LAC_HUB/` (7,027 numbers, 1,282 scenario names, 660 country names and codes, 1,165 technology names and prefixes, 567 fuel names, 469 emission names). 1,977 of them sit in the 32 files that Stage 0 to 3 results depend on; 2,934 sit in the duplicate folder `models_energy_RE_generation_costs_update/`. `script_constants_accepted.csv` holds 52,301 constants of the mathematics or presentation with the reason. `scenario_names.csv` finds 12 scenario names; `structure_map.md` maps the layout against OSTRAM.

| File (Stage 0 to 3 depend on it) | Rows | of which numbers |
|---|---|---|
| Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel_Honduras.py | 229 | 140 |
| DominicanRepublic/RD_ENERGY/B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py | 226 | 133 |
| Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py | 211 | 139 |
| Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel_Jamaica.py | 149 | 108 |
| Ecuador/ECU_Energy/B1_Base_Scenarios_Adj_Parallel.py | 140 | 93 |
| CostaRica/CR_ENERGY/t1_confection/B1_Base_Scenarios_Adj_Parallel_CostaRica.py | 116 | 53 |
| stage2_apply_v2.py | 115 | 75 |
| stage1_share_analyzer_v16.py | 105 | 58 |
| stage3_run_all.bat | 61 | 1 |
| stage0_run.py | 57 | 20 |
| stage3_results.py | 55 | 29 |
| stage3_apply.py | 50 | 30 |
| stage0_collect_outputs.py | 46 | 25 |
| A2 compilers (six files) | 196 | 173 |
| stage0_recommend_shares.py | 36 | 19 |
| stage0_capacity_check.py | 24 | 8 |
| OSeMOSYS_Model.txt (six energy copies) | 97 | 97 |
| stage2_post_clean.py, stage0_run_all.bat and .sh, stage0_clean.py, ao_safe_save.py | 64 | 20 |
| All 32 files | 1,977 | 1,221 |

The other 221 files hold 9,193 rows (sector models, plotting, tests, audits and the duplicate folder). The renewable targets typed twice (`stage1_share_analyzer_v16.py` lines 97 to 110, `stage2_apply_v2.py` lines 61 to 75) are rows of this list and are the proposed home of `scenario_values.csv`.

## 7. Gates

| Gate | Result |
|---|---|
| 1. `git diff --name-only origin/main` lists only files under the job folder | pass |
| 2. Every row of `verification_`, `analyses_` and `scenario_values.csv` has a source id in `sources.csv` and a page; no `scenario_values.csv` row cites a `lead` source | pass |
| 3. Every value of `values_to_verify.csv` has a verification row | pass (733 of 733) |
| 4. Every standard unit of `scenario_values.csv` is listed in `units.csv` | pass |
| 5. Every source file exists with a matching SHA-256 | pass (84 sources) |
| 6. `git -C /c/clw_scout_model status --short` is empty | pass |

## 8. Pull request and commits

