# Guatemala hydro trace (D8), draft

Values read at the base commit 4ba69d6 from the tracked stage outputs (`scripts/gua_trace_values.py`, output in `logs/gua_trace_values.log`). Hydro here is `PPHDAM` plus `PPHROR`, the two technologies of the controller's HYDRO sub-group for Guatemala. PJ unless stated.

## Step by step, from Stage 3 back to the cause

**Stage 3 output** (`_STAGE3_RESULTS/stage3_results.xlsx`, TotalTechnologyAnnualActivity):

| Year | BAU | NDCNEW | LTSNEW |
|---|---|---|---|
| 2024 | 19.344 | 19.344 | 19.344 |
| 2025 | 19.841 | 22.300 | 22.300 |
| 2026 | 21.134 | 24.120 | 24.115 |
| 2030 | 24.294 | 27.280 | 27.275 |
| 2050 | 24.294 | 27.280 | 27.275 |

Stage 3 pins every power plant from 2025 at the Stage 2 controller lower limit (upper = lower x 1.05) and leaves history years as B1 wrote them, so 2024 is equal in all scenarios and the split starts in 2025.

**Stage 2 controller** (`_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx`), hydro shares and lower limits:

| Year | Share, all scenarios | Lower BAU | Lower NDCNEW | Lower LTSNEW |
|---|---|---|---|---|
| 2024 | 0.4315 (PPHDAM 0.4031 + PPHROR 0.0284) | 18.787 | 18.787 | 18.787 |
| 2025 | 0.4315 | 19.841 | 22.300 | 22.300 |
| 2026 | 0.4315 | 21.134 | 24.120 | 24.115 |
| 2027 | BAU 0.4059, NDCNEW 0.4005, LTSNEW 0.4006 | 21.134 | 24.120 | 24.115 |
| 2030 | BAU 0.4115, NDCNEW 0.3641, LTSNEW 0.3644 | 24.294 | 27.280 | 27.275 |

The shares of 2024, 2025 and 2026 come from `_STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.csv`: PPHDAM 40.31 percent and PPHROR 2.84 percent in 2024 (note "AMM=40.31%"), repeated in 2025 and 2026 as "Plateau=corrected 2024 anchor", identical lines for BAU, NDCNEW and LTSNEW. Lower limit = share x total generation of that scenario and year. From 2027 Stage 2 freezes hydro PJ at the 2026 boundary (`stage2_apply_v2.py`, hydro PJ freeze), then raises it from 2028 by the mincap floor (boundary PJ + cumulative TotalAnnualMinCapacityInvestment x CF x AF x 31.536): B1 MinCapInvest PPHDAM 0.052 GW (2028) and 0.13 GW (2030), PPHROR 0.02 GW (2030), the same in the three scenarios, adding 3.16 PJ by 2030 in every scenario.

**Stage 0 denominators** (`_STAGE0_OUTPUT/STAGE0_DENOMINATORS.xlsx`, Empirical_Gen_PJ):

| Year | BAU | NDCNEW | LTSNEW |
|---|---|---|---|
| 2024 | 43.538 | 43.538 | 43.538 |
| 2025 | 45.980 | 51.680 | 51.680 |
| 2026 | 48.979 | 55.898 | 55.886 |
| 2030 | 59.032 | 74.922 | 74.852 |

Check: 0.4315 x 48.979 = 21.134; 0.4315 x 55.898 = 24.120; 0.4315 x 55.886 = 24.115. These are the Stage 3 hydro values of 2026 exactly.

**Stage 1** (`_STAGE1_OUTPUT`): hydro share 0.4187 in 2024 to 2026 in all scenarios; Stage 2 replaces it with the overwrite shares, so Stage 1 is not the cause.

**B1 inputs**: hydro capacity, capacity factors and MinCapInvest are the same in the three scenarios (MinCapInvest above); the B1 history of PPHDAM and PPHROR is aligned. The policy scenarios' Stage 0 runs (relaxed limits, lower limits zeroed from 2025) generate more electricity from 2025 because of orphan distributed technologies (documented in `PIPELINE_WORKFLOW.md`, Guatemala exception) and the policy demand (transport electrification), so their denominators are 12 to 14 percent above BAU in 2025 and 2026.

## Cause

The hydro path is set as a share of total generation in 2025 and 2026 and then frozen in PJ at 2026. The same share applied to a larger policy denominator gives about 3 PJ more hydro in NDCNEW and LTSNEW (2.98 to 2.99 PJ in 2026 and every later year). No source supports more hydro in the policy scenarios: the hydro fleet, capacity factors and committed additions are identical.

## Proposed least change (not yet written)

- Keep the 2024 overwrite share (AMM observed). Replace the 2025 and 2026 overwrite lines of PPHDAM and PPHROR per scenario by the share that gives one sourced hydro PJ path: share(s, y) = sourced hydro PJ(y) / Stage 0 denominator(s, y), at least six significant digits, Note citing the AMM statistics and the formula.
- Sourced hydro PJ: AMM observed hydro generation for every observed year (2025 is fully observed in `downloads/d2_gua/AMM_GM20260101.xlsx` and the AMM INFEST 2025 files, to be read); after the last observed year, the hydro freeze rule holds that PJ. If 2025 is the last full observed year, 2025 and 2026 both take the 2025 observed PJ split between PPHDAM and PPHROR by the 2024 overwrite proportions (40.31 : 2.84) unless AMM prints the split.
- Because the denominators come from Stage 0, the shares must be recomputed after the Phase D Stage 0 run (denominators change with this job's writes), before Stage 2. The 2028 and 2030 mincap additions stay and apply equally to all scenarios.
- Gate: Guatemala hydro by scenario within 0.05 PJ in every year.
- Open point for the new session: the AMM files in `downloads/d2_gua/` were downloaded by a search that stopped before writing its report; their values and the gross or net basis (and whether distributed renewable generators are included) still have to be read and recorded with locators.
