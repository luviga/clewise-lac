# ECUADOR POST-PATCH VALIDATION PROMPT
# =====================================
# Paste this into a fresh Claude chat after running the patched Ecuador pipeline.
# Upload the files listed below alongside this prompt.

"""
CONTEXT — what was patched and why:

Ecuador's OSeMOSYS A-O_Parametrization.xlsx had a counterfactual NDC encoding
where major hydro plants (Coca Codo Sinclair 1,500 MW, Sopladora 487 MW, and
several others totaling ~1,800 MW) had ResidualCapacity = 0 despite being
operational since 2016-2017. The solver was forced to invest endogenously to
meet generation lower limits — incurring phantom capital costs and producing
incorrect capacity trajectories.

PATCH A (patch_ao_ecuador_hydro.py — 13 edits to A-O_Parametrization.xlsx):
  - PPHRORAB RC: 0.000 → 1.500 GW (Coca Codo Sinclair)
  - PPHRORAM RC: 0.000 → 0.487 GW (Sopladora)
  - PPHDAMAB RC: 1.075 → 1.270 GW (+Mazar 170 MW)
  - PPHRORAS RC: 0.024 → 0.062 GW (small southern RoR)
  - PPHRORPM RC: 0.230 → 0.288 GW (+small additions)
  - PPHRORPS RC: 0.055 → 0.150 GW (smaller RoR pre-2021)
  - PPHD RC: 0.813 → 0.648 GW (reduce excess filler)
  - PPHRORAB MCI: zeroed 0.1623 GW at 2026-28 (phantom NDC investment)
  - PPHRORAS MCI: added 0.180 GW at 2022 (Delsitanisagua, COD Dec 2018)
  - PPHRORPM MCI: added 0.270 GW at 2022 (Minas San Francisco, COD Jan 2019)
  - PPWNDON RC: 0.0212 → 0.0165 GW (Villonaco correction)
  Total new hydro RC: 5,305 MW vs real fleet ~5,107 MW (104%).

PATCH B (stage0_run.py — bypass-tech upper limit cap):
  Stage 0's relaxed run was letting the optimizer route generation through
  bypass techs (PPWNDD, PPHD, PPIHD, autoproducers) to avoid 18.5% T&D losses,
  collapsing Empirical_Gen from ~131 PJ to ~112 PJ. Fix: cap bypass-tech upper
  limits at their 2024 activity level instead of 9999.

ADDITIONAL KNOWN ISSUE (not patched, pre-existing):
  - PPWNDD ResidualCapacity = 0.2586 GW (phantom distributed wind) — already
    0.0 in current A-O but persists in old B1_Output_Params. The A2 re-run
    should propagate the 0.0 correctly.
  - PPPVD ResidualCapacity = 0.026 GW (distributed PV) — already correct in A-O.

PIPELINE RUN SEQUENCE (already completed by user):
  1. py patch_ao_ecuador_hydro.py  (applied Patch A)
  2. py A2_compiler.py --countries Ecuador
  3. py B1_scenario_config.py --countries Ecuador
  4. py stage0_run.py --countries Ecuador  (with Patch B)
  5. GLPK solver runs (BAU_S0, NDCNEW_S0, LTSNEW_S0)
  6. py stage0_collect_outputs.py --countries Ecuador
"""

# =====================================================================
# VALIDATION TASK — please check the following
# =====================================================================

"""
PLEASE UPLOAD THESE FILES:
  1. _STAGE0_OUTPUT/STAGE0_DENOMINATORS.xlsx  (new, from step 6)
  2. _STAGE0_OUTPUT/Ecuador/EMPIRICAL_GEN__Ecuador__BAU_S0.csv
  3. _STAGE0_OUTPUT/Ecuador/PRODUCTION_BY_TECH__Ecuador__BAU_S0.csv
  4. _STAGE0_OUTPUT/STAGE0_RUN_STATUS.csv
  5. The patched A-O_Parametrization.xlsx (for cross-reference)
  6. Ecuador/ECU_Energy/B1_Output_Params/BAU/ResidualCapacity.csv (new)

CHECKS TO PERFORM:

CHECK 1 — Solver feasibility:
  All 3 Ecuador scenarios (BAU_S0, NDCNEW_S0, LTSNEW_S0) must show "OK" in
  STAGE0_RUN_STATUS.csv. Any INFEASIBLE is a red flag.

CHECK 2 — Empirical_Gen / Consumer_Demand ratio:
  For years 2025-2050, the ratio should be ~1.14-1.17 (generation-level,
  including T&D losses). Previously it was ~1.01 (consumer-level, bypass gaming).
  - If still ~1.01: bypass cap patch didn't work or wasn't applied
  - If ~1.14-1.17: correct, T&D losses are properly reflected
  - If >1.25: something over-generating
  Consumer demand reference: 2025 = 110.8 PJ, 2030 = 121.9 PJ

CHECK 3 — Hydro generation at normal-year levels:
  Total hydro production (sum of all PPHD* + PPIHD techs) for 2024 should be
  ~75-90 PJ (normal year), NOT ~53 PJ (drought-suppressed).
  CENACE reference: 2022 hydro = 88.2 PJ, 2019 = 88.0 PJ.

CHECK 4 — No phantom wind generation:
  PPWNDD production should be near-zero or zero for all years.
  Previously it had 0.2586 GW RC producing ~1.1 PJ. After fix: ~0 PJ.

CHECK 5 — CCS (PPHRORAB) generation is realistic:
  PPHRORAB should produce ~24-26 PJ (≈7,000-7,200 GWh).
  This matches Coca Codo Sinclair's typical annual output.
  If PPHRORAB produces 0 PJ: the RC fix didn't propagate through A2/B1.

CHECK 6 — Sopladora (PPHRORAM) generation:
  PPHRORAM should produce ~5.5-6.5 PJ (≈1,500-1,800 GWh).
  Sopladora's typical output. If 0 PJ: same propagation issue.

CHECK 7 — ResidualCapacity.csv from B1_Output_Params:
  Verify that the new B1 CSV has:
    PPHRORAB: 1.500 GW for all years
    PPHRORAM: 0.487 GW for all years
    PPWNDD: 0.0 GW (not 0.2586)
  If old values persist, A2 compiler didn't pick up the patched A-O.

CHECK 8 — Capital cost sanity:
  With CCS and Sopladora now in RC (free capacity), the model should NOT be
  investing $5+ billion in new hydro capacity. Check if NewCapacity for
  PPHRORAB or PPHRORAM is zero in the solver output — it should be, since
  the RC already covers the lower limits.

CHECK 9 — Denominator gap:
  STAGE0_DENOMINATORS.xlsx: Delta_Pct for 2025-2050 should be smaller than
  before (was -14.7%). Target: within ±5%. If still -14%: bypass cap not working.

If all 9 checks pass, Ecuador is ready for Stage 1 share analysis.
If any fail, flag the specific check number and the values observed.
"""
