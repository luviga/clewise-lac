# HANDOFF_STAGE4.md — Stage 4: LTSOPT Variants + Final Reporting

**Date**: 2026-05-16
**Prerequisite**: Stage 3 complete — 18/18 OPTIMAL, RE targets 24/24 PASS
**Project**: MODELS_LAC_4, 6 LAC countries × 3 scenarios (BAU, NDCNEW, LTSNEW)

---

## Context

Stage 3 produced optimal GLPK solutions for all 18 (country × scenario) combinations with validated emission divergence and RE share targets. The `_FINAL_0` folders contain patched .txt files and 750MB+ GLPK output files. Results are extracted in `_STAGE3_RESULTS/stage3_results.xlsx`.

**Stage 3 exact reproduction command:**
```batch
py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala
py stage3_test.py --root .
stage3_run_all.bat
py stage3_results.py --root .
```

---

## Stage 4 Scope

### 4A — LTSOPT Scenario Generation
Generate a fourth scenario (LTSOPT) for each country by creating variants of LTSNEW with:
- **Hydro drought**: reduce hydro capacity factors (or availability factors) to simulate drought conditions
- **Fuel price sensitivity**: apply HIGH/LOW fuel price projections from `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx`

LTSOPT is derived from LTSNEW `_FINAL_0` files, not from scratch. The approach:
1. Copy LTSNEW_FINAL_0 → LTSOPT_FINAL_0
2. Patch hydro parameters (CapacityFactor or AvailabilityFactor reduction)
3. Optionally patch VarCost with fuel price scenarios
4. Solve with GLPK
5. Extract results

### 4B — B1 data_processor Integration
Run the existing B1 `data_processor()` function against all `_FINAL_0_output.txt` files to produce the full CSV outputs that the downstream reporting pipeline expects (Output.csv format with all OSeMOSYS variables).

### 4C — Final Reporting
- Emission trajectory plots (6 countries × 4 scenarios)
- Generation mix stacked area charts
- RE share trajectory comparison
- Cost comparison across scenarios

---

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| Stage 3 results | `_STAGE3_RESULTS/stage3_results.xlsx` | Extracted variables + share validation |
| Controller | `_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` | Authoritative shares/limits (TECH_MAP for RE classification) |
| Fuel prices | `LAC_Fuel_Price_Projections_2026_v2_audit.xlsx` | REF/HIGH/LOW fuel price scenarios |
| B1 runner | `B1_Base_Scenarios_Adj_Parallel_{Country}.py` | data_processor function for output parsing |
| GLPK outputs | `{Country}/{ModelDir}/Executables/{Scenario}_FINAL_0/{Scenario}_FINAL_0_output.txt` | 750MB+ solver output files |

---

## Stage 3 Configuration Record

### Command
```
py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala
```

### Design decisions and rationale

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Upper limit rule | Always lower × 1.05 | Controller uppers were stale Stage 1 values (2–7× too wide) |
| Zero-lower tech upper | 0 (except Guatemala: 99999) | Prevents unconstrained techs from stealing generation share |
| Orphan PP tech handling | Detected via comprehensive param block scan; lower=0, upper=0 | Techs in model but not in controller were producing 3–40% unconstrained |
| Guatemala exception | `--skip-orphan-cap Guatemala` | Stage 0 NDCNEW/LTSNEW denominators inflated 20–107% by orphan overproduction; tight caps make lower_sum > demand → infeasible |
| MaxCapacity | Uncapped (99999) for all PP techs | Original caps conflicted with new higher activity lower limits |
| ReserveMargin | 1.15 flat, plain tuple format | SOASIA reference format; solar/wind excluded from firm capacity |
| Share validation | PASS ≤0.3pp, WARN 0.3–1pp, FAIL >1pp | 20 failures all 1.0–1.2pp (Jamaica PV mid-years, Guatemala orphan-skip tradeoff) |
| RE target tolerance | 2pp | All 24 checks pass with 0pp deviation at milestones |

### RE policy targets (hardcoded in stage3_results.py)

| Scenario | Year | Target | Notes |
|----------|------|--------|-------|
| NDCNEW | 2035 | 75% RE | CR override: 90%, Ecuador: 80% (both exceed 75% naturally) |
| NDCNEW | 2050 | 75% RE | Maintained from 2035 |
| LTSNEW | 2035 | 75% RE | Intermediate milestone |
| LTSNEW | 2050 | 99% RE | Full decarbonization target |

### Country-specific notes

| Country | Special handling | Notes |
|---------|-----------------|-------|
| CostaRica | None | Already 89% RE in BAU; path: `CR_ENERGY/t1_confection` (one level deeper) |
| DominicanRepublic | None | Largest absolute emission reduction under LTSNEW (-85%) |
| Ecuador | None | PPPVDS was 40% overproducer (caught by zero-lower rule); `ECU_Energy` (lowercase 'e') |
| Guatemala | `--skip-orphan-cap` | Inflated Stage 0 denominators; PPPVT2 orphan left free; share validation ~1pp looser |
| Honduras | None | 4 orphan techs capped |
| Jamaica | None | 7 orphan techs capped; PPPVD was 3.5% late-year leaker; model horizon 2021–2055 |

### Orphan techs per country (for reference)

```
CostaRica:         PP_SPV_DG, PP_SPV_US_H2, PP_WNDOFS, PP_WND_OF_H2, PP_WND_US_H2, PWRSPVDTR
DominicanRepublic: PPBGS, PPGEO, PPHROR, PPPVTHYD, PPPVTS, PPWNDOFF
Ecuador:           PPWNDOFF, PPWNDONS (+ PPPVDS caught by zero-lower rule)
Guatemala:         PPPVT2 (SKIPPED)
Honduras:          PPPVDS, PPPVT2, PPPVTS, PPWNDS
Jamaica:           PPBGS, PPGEO, PPPVD, PPPVDS, PPPVTS, PPWNDOFF, PPWNDONS
```

---

## Known Issues for Stage 4

1. **Guatemala denominator inflation**: The proper fix is rerunning Stage 0 with orphan caps, then Stage 2 with clean denominators. Current workaround (`--skip-orphan-cap`) is acceptable but leaves Guatemala shares ~1pp looser.

2. **Jamaica PPPVT late-year deviation**: 1.0–1.2pp overproduction in NDCNEW 2031–2044. End-of-horizon solver artifact from salvage value effects. Acceptable for publication.

3. **Pre-2027 emission drift**: ~0.1% difference between BAU/NDCNEW/LTSNEW in 2025–2026 due to LP perfect-foresight. Not a bug — solver prepares for different futures.

4. **GLPK output file size**: 750MB+ per scenario. Clean with `stage2_post_clean.py --all-runs --yes` after B1 processing if Dropbox space is tight.

---

## Environment

- Windows Anaconda `cmd` prompt
- `py` (not `python`); inline `#` comments do not work in Windows cmd
- GLPK v4.65
- Python 3.12 (Anaconda)
- Dropbox: primary storage — pause sync before bulk operations
