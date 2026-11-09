# MODELS_LAC_4 Pipeline Workflow

**Updated**: 2026-05-16
**Status**: Stage 0 ✓ → Stage 1 v15 ✓ → Stage 2 v7 ✓ → Stage 3 ✓ → Stage 4 (next)

---

## Pipeline Overview

```
Stage 0 (done)     Relaxed OSeMOSYS runs → empirical generation denominators + recommended shares
    ↓
Stage 1 v15 (done) Controller: shares (100%), lower/upper limits, policy curves
    ↓
Stage 2 v7 (done)  Research-corrected historical shares + rules-based forward rebase → final controller
    ↓
Stage 3 (done)     Patch .txt files + orphan capping + ReserveMargin + GLPK runs + results extraction
    ↓
Stage 4 (next)     LTSOPT variants (fuel price / hydro drought) + B1 data_processor + final reporting
```

---

## Stage 0 — Empirical Denominators (DONE)

**Purpose**: Run each country's OSeMOSYS model with relaxed electricity constraints to measure actual generation totals and historical shares.

**Scripts** (run from `MODELS_LAC_4/`):
```
py stage0_clean.py --confirm
py stage0_run.py
stage0_run_all.bat
py stage0_collect_outputs.py
py stage0_capacity_check.py
py stage0_recommend_shares.py
```

**Key outputs** (`_STAGE0_OUTPUT/`):
- `STAGE0_RECOMMENDED_SHARES_EDITED.csv` — per-tech/year shares (column E), summing to 100%
- `EMPIRICAL_GEN__{Country}__{Scenario}_S0.csv` — total generation per year (the denominator)
- `STAGE0_CAPACITY_CEILING.csv` — production potential ceiling per tech/year
- `STAGE0_DENOMINATORS.xlsx` — empirical vs analytical comparison; **this is the authoritative demand source for Stage 2** (not sum of lower limits, which are ceiling-capped)

**Key decisions**:
- Column E (proportional capacity-based) used for all 6 countries
- Anchor year = 2024, cutoff year = 2026
- Mode = zero (lower limits zeroed 2025+, upper limits set to 9999)
- All 18 runs feasible
- Demand grows for every country (e.g., Honduras +132%, Guatemala +212% by 2050)

**Known issue**: Stage 0 NDCNEW/LTSNEW unconstrained runs produce inflated generation denominators due to orphan tech overproduction (e.g., Guatemala NDCNEW 71 PJ in 2030 vs BAU 59 PJ). This is handled in Stage 3 via `--skip-orphan-cap Guatemala`.

---

## Stage 1 v15 — Controller (DONE)

**Purpose**: Compute shares, lower limits, and upper limits for all (country, scenario, tech, year) from Stage 0 data. Single unified script.

**Scripts**:
```
py stage1_share_analyzer_v16.py
py stage1_test_v16.py
py stage1_test_v16.py --skip-run
```

**Output** (`_STAGE1_OUTPUT/`):
- `CONTROLLER_NEW_SCENARIOS.xlsx` — 7 sheets: README, CURRENT_SHARES, TARGET_SHARES, CURRENT_LOWER, CURRENT_UPPER, TECH_MAP, AUDIT

**Rules**:
- Historical (2018–2024): actual per-year recommended shares from Stage 0
- Plateau (2025–2026): frozen at 2024 anchor
- BAU 2027+: fossil 1%/yr decline (CR: 0%), hydro PJ freeze, NH-renewable gap-fill
- Policy: `T = max(target, BAU_RE)`, solar/wind absorb increment, biomass/geo locked at BAU
- Mincap floor: MinCapInvest × CF × AF × 31.536 from B1_Output_Params
- Country overrides: CR NDCNEW 90%/LTSNEW 99%, Ecuador NDCNEW 80%/LTSNEW 80→99%

**13 tests all passing.**

---

## Stage 2 v7 — Research Corrections + Forward Rebase (DONE)

**Purpose**: Apply research-corrected historical shares from per-country CSVs, then re-derive forward projections using Stage 1 rules from the corrected base. Produces the **authoritative final controller**.

### How it works

**Historical (≤2026):**
- Per-country CSVs correct shares where provided (full replacement if all techs sum to 100%, group renormalization if partial)
- Freeze propagation: if CSV ends at ≤2024, copy corrected 2024 to 2025–2026
- Years without CSV data: keep Stage 1 values

**Forward (2027+) — all from rules, all countries identical:**

| Category | Rule | Behavior |
|----------|------|----------|
| Fossil | 1%/yr decline (CR: 0%) | Share shrinks, freeing capacity |
| Hydro | PJ freeze | Absolute PJ locked at boundary; share declines as demand grows |
| Biomass/geo/biogas | PJ freeze | Same as hydro — no new plants assumed |
| Solar/wind | Gap-fill | Absorb all remaining capacity after fossil + hydro + biomass |
| Mincap floor | MinCapInvest × CF × AF × 31.536 | Per-tech minimum from B1 committed capacity; overrides rule if higher |
| Policy (NDCNEW/LTSNEW) | RE = max(target, BAU_RE) | Fossil compressed, solar/wind expanded to hit exact target |

**Solar/wind split**: determined by mincap floors (B1 committed capacity) where available; falls back to proportional from boundary (2026) shares where MinCapInvest = 0.

**Total generation**: read from `STAGE0_DENOMINATORS.xlsx` (Empirical_Gen_PJ). NOT from sum of lower limits (those are ceiling-capped and underestimate demand).

### Scripts

```
py stage2_apply_v2.py --root . --stage0-denom _STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx
py stage2_test_v2.py --stage0-denom _STAGE0_OUTPUT\STAGE0_DENOMINATORS.xlsx
```

### Output

`_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx` — same 7-sheet format as Stage 1, source column = "s2v2"

### Test results (7/7 hard PASS)

### RE trajectory (final — matches Stage 3 solver output)

```
             Country Scenario   2024   2030   2035   2050
           CostaRica      BAU  89.4%  89.4%  89.4%  89.4%
           CostaRica   NDCNEW  89.4%  89.7%  90.0%  90.0%
           CostaRica   LTSNEW  89.4%  93.7%  99.0%  99.0%
   DominicanRepublic      BAU  15.9%  19.2%  23.1%  33.9%
   DominicanRepublic   NDCNEW  15.9%  42.1%  75.0%  75.0%
   DominicanRepublic   LTSNEW  15.9%  42.1%  75.0%  99.0%
             Ecuador      BAU  75.7%  76.6%  77.8%  80.9%
             Ecuador   NDCNEW  75.7%  77.6%  80.0%  80.9%
             Ecuador   LTSNEW  75.7%  77.6%  80.0%  99.0%
           Guatemala      BAU  63.4%  52.3%  57.1%  64.0%
           Guatemala   NDCNEW  63.4%  68.6%  75.0%  75.0%
           Guatemala   LTSNEW  63.4%  68.6%  75.0%  99.0%
            Honduras      BAU  59.6%  56.9%  59.0%  64.7%
            Honduras   NDCNEW  59.6%  64.7%  75.0%  75.0%
            Honduras   LTSNEW  59.6%  64.7%  75.0%  99.0%
             Jamaica      BAU  10.0%  13.5%  17.8%  29.3%
             Jamaica   NDCNEW  10.0%  38.9%  75.0%  75.0%
             Jamaica   LTSNEW  10.0%  38.9%  75.0%  99.0%
```

---

## Stage 3 — Patch .txt + GLPK Runs + Results Extraction (DONE)

**Purpose**: Patch GLPK .txt data files with Stage 2 controller values (lower/upper activity limits, ReserveMargin), solve all 18 scenarios, extract and validate results.

### Exact reproduction command

```batch
REM From MODELS_LAC_4/ in Anaconda prompt:
py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala
py stage3_test.py --root .
stage3_run_all.bat
py stage3_results.py --root .
```

### What stage3_apply.py does

For each (country, scenario): copies `{scenario}_0/` → `{scenario}_FINAL_0/`, renames .txt, then patches:

1. **LowerLimit**: PP/PWR techs from 2025+ replaced with controller CURRENT_LOWER values
2. **UpperLimit**: always lower × 1.05 (controller uppers ignored as stale Stage 1 values); zero-lower techs get upper=0 (except Guatemala: upper=99999 via `--skip-orphan-cap`)
3. **Orphan PP techs** (in model but not in controller): detected via comprehensive scan of all param blocks; lower=0, upper=0 from 2025+. Skipped for Guatemala.
4. **TotalAnnualMaxCapacity**: PP techs set to 99999 (`--uncap-pp-maxcap`)
5. **ReserveMargin**: 1.15 flat, plain tuple format
6. **ReserveMarginTagFuel**: generation electricity fuel tagged=1
7. **ReserveMarginTagTechnology**: all firm generators tagged=1; solar/wind excluded

Preserves CRLF line endings, historical years (≤2024), non-PP techs.

### Key flags

| Flag | Effect | Why |
|------|--------|-----|
| `--clean` | Deletes and recreates _FINAL_0 folders from untouched _0 originals | Fresh slate on re-runs |
| `--uncap-pp-maxcap` | Sets TotalAnnualMaxCapacity to 99999 for PP techs | Prevents capacity ceilings conflicting with new activity limits |
| `--skip-orphan-cap Guatemala` | Guatemala: orphans left uncapped, zero-lower techs get 99999 | Guatemala NDCNEW/LTSNEW have inflated Stage 0 denominators (orphan overproduction); tight capping causes infeasibility |

### Guatemala exception — root cause

Stage 0 unconstrained NDCNEW/LTSNEW runs for Guatemala produced inflated generation (orphan distributed techs overproduced), yielding denominators 20–47% above BAU:

| Year | BAU gen (PJ) | NDCNEW gen (PJ) | LTSNEW gen (PJ) |
|------|------|------|------|
| 2030 | 59.0 | 71.1 (+20%) | 71.0 |
| 2040 | 92.4 | 135.5 (+47%) | 168.9 |
| 2050 | 135.7 | 171.9 | 281.3 (+107%) |

Stage 2 used these inflated denominators for NDCNEW/LTSNEW lower limits, so lower_sum > BAU generation capacity → infeasible when orphans are capped. The `--skip-orphan-cap` flag restores Guatemala's freedom. Share validation for Guatemala is slightly looser (~1pp) as a result.

### Orphan techs detected per country

| Country | Orphans | Notes |
|---------|---------|-------|
| CostaRica | PP_SPV_DG, PP_SPV_US_H2, PP_WNDOFS, PP_WND_OF_H2, PP_WND_US_H2, PWRSPVDTR (6) | All capped to 0 |
| DominicanRepublic | PPBGS, PPGEO, PPHROR, PPPVTHYD, PPPVTS, PPWNDOFF (6) | All capped to 0 |
| Ecuador | PPWNDOFF, PPWNDONS (2) | PPPVDS was 40% overproducer; caught by zero-lower→zero-upper rule |
| Guatemala | PPPVT2 (1) | **SKIPPED** — left free to produce |
| Honduras | PPPVDS, PPPVT2, PPPVTS, PPWNDS (4) | All capped to 0 |
| Jamaica | PPBGS, PPGEO, PPPVD, PPPVDS, PPPVTS, PPWNDOFF, PPWNDONS (7) | PPPVD was 3.5% late-year leaker |

### Solver results: 18/18 OPTIMAL

| Country | BAU | NDCNEW | LTSNEW |
|---|---|---|---|
| CostaRica | ✓ 13.7s | ✓ 14.6s | ✓ 13.3s |
| DominicanRepublic | ✓ 21.2s | ✓ 22.4s | ✓ 22.4s |
| Ecuador | ✓ 12.9s | ✓ 11.7s | ✓ 11.5s |
| Guatemala | ✓ 7.5s | ✓ 10.7s | ✓ 9.2s |
| Honduras | ✓ 15.7s | ✓ 21.4s | ✓ 18.9s |
| Jamaica | ✓ 11.1s | ✓ 8.5s | ✓ 8.5s |

### Emissions divergence (MtCO2e) — confirmed working

| Country | 2050 BAU | 2050 NDCNEW | 2050 LTSNEW | LTSNEW reduction |
|---------|----------|-------------|-------------|------------------|
| CostaRica | 34.0 | 27.9 | 8.4 | -75% |
| DominicanRepublic | 112.5 | 60.9 | 17.4 | -85% |
| Ecuador | 182.6 | 165.3 | 117.7 | -36% |
| Guatemala | 156.4 | 125.2 | 66.5 | -57% |
| Honduras | 59.0 | 52.5 | 23.7 | -60% |
| Jamaica | 15.3 | 11.4 | 4.7 | -69% |

### RE target validation: 24/24 PASS

| Milestone | Target | Result |
|-----------|--------|--------|
| NDCNEW 2035 | ≥75% RE | ✓ All 6 countries (CR exceeds at 90%) |
| NDCNEW 2050 | ≥75% RE | ✓ All 6 countries |
| LTSNEW 2035 | ≥75% RE | ✓ All 6 countries (CR exceeds at 99%) |
| LTSNEW 2050 | ≥99% RE | ✓ All 6 countries at exactly 99.0% |

### Share validation: 7789 pass, 189 warn, 20 fail

Thresholds: PASS ≤0.3pp, WARN 0.3–1pp, FAIL >1pp. All 20 failures are 1.0–1.2pp — Jamaica PPPVT mid-years (solver favoring cheap solar within 5% headroom) and Guatemala PPHDAM/PPPVD (orphan-skip tradeoff). Acceptable for publication — total RE share hits targets exactly.

### Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `stage3_apply.py` | Patch .txt files with controller values | `py stage3_apply.py --root . --clean --uncap-pp-maxcap --skip-orphan-cap Guatemala` |
| `stage3_test.py` | 11-test validation suite (lower/upper/RM/orphans) | `py stage3_test.py --root .` |
| `stage3_run_all.bat` | GLPK batch solver for all 18 scenarios | `stage3_run_all.bat` |
| `stage3_results.py` | Parse GLPK output, extract variables, validate shares + RE targets | `py stage3_results.py --root .` |

### Output

- `_STAGE3_RESULTS/stage3_results.xlsx` — 7 sheets: TotalTechnologyAnnualActivity, AnnualEmissions, AnnualTechnologyEmission, NewCapacity, TotalCapacityAnnual, ProductionByTechnologyAnnual, ShareValidation
- `{Country}/{ModelDir}/Executables/{Scenario}_FINAL_0/` — patched .txt + GLPK output

---

## Stage 4 — LTSOPT Variants + Final Reporting (NEXT)

**Purpose**: Generate LTSOPT scenario variants (hydro drought, fuel price sensitivity), run B1 data_processor for full output CSVs, produce final emission trajectory plots.

**See**: `HANDOFF_STAGE4.md` for full specification.

---

## Directory Structure

```
MODELS_LAC_4/
├── _STAGE0_OUTPUT/              # Stage 0 artifacts (read-only)
│   ├── STAGE0_RECOMMENDED_SHARES_EDITED.csv
│   ├── STAGE0_CAPACITY_CEILING.csv
│   ├── STAGE0_DENOMINATORS.xlsx       ← authoritative demand source
│   └── {Country}/EMPIRICAL_GEN__*.csv
├── _STAGE1_OUTPUT/              # Stage 1 artifacts (read-only after Stage 2)
│   └── CONTROLLER_NEW_SCENARIOS.xlsx
├── _STAGE2_INPUTS/              # Per-country correction CSVs
│   └── STAGE2_OVERWRITES_*.csv
├── _STAGE2_OUTPUT/              # Stage 2 artifacts
│   └── CONTROLLER_NEW_SCENARIOS.xlsx  ← authoritative final controller
├── _STAGE3_RESULTS/             # Stage 3 results
│   └── stage3_results.xlsx            ← extracted variables + share validation
├── stage0_*.py                  # Stage 0 scripts
├── stage1_share_analyzer_v16.py # Stage 1 main script
├── stage1_test_v16.py           # Stage 1 test harness
├── stage2_apply_v2.py           # Stage 2 apply script
├── stage2_test_v2.py            # Stage 2 test suite
├── stage3_apply.py              # Stage 3 patching script
├── stage3_test.py               # Stage 3 test suite (11 tests)
├── stage3_results.py            # Stage 3 results extractor + validator
├── stage3_run_all.bat           # GLPK batch runner
├── PIPELINE_WORKFLOW.md         # This file
├── {Country}/                   # Country model directories
│   └── {MODEL_DIR}/
│       ├── B1_Output_Params/{Scenario}/   # Protected input CSVs
│       ├── Executables/{Scenario}_0/      # Original solver input (never modified)
│       ├── Executables/{Scenario}_FINAL_0/ # Patched solver input + GLPK output
│       └── OSeMOSYS_Model.txt
└── ...
```

---

## Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| ANCHOR_YEAR | 2024 | Starting composition for all scenarios |
| CUTOFF_YEAR | 2026 | Forward rules begin at 2027 |
| FOSSIL_DECLINE_RATE | 0.01 | 1%/yr from 2027 (BAU); CR = 0% |
| CAU | 31.536 | CapacityToActivityUnit (PJ/GW/yr) |
| UPPER_FACTOR | 1.05 | Upper = lower × 1.05 (Stage 3) |
| RESERVE_MARGIN | 1.15 | 15% reserve margin |
| PP_PREFIXES | PP, PWR | Electricity-sector tech filter |
| VARIABLE_RE_KEYS | SPV, PVD, PVT, PVS, WND, WNO | Solar/wind excluded from RM tags |

| Scenario | Target | Milestones |
|----------|--------|------------|
| BAU | organic | 1%/yr fossil decline, gap-fill with solar/wind |
| NDCNEW | 75% RE by 2035 | CR: 90%, Ecuador: 80% |
| LTSNEW | 99% RE by 2050 | CR: 99% by 2035, Ecuador: 80% by 2035 → 99% by 2050 |

---

## Country Model Directories

| Country | Model Dir | Region | Notes |
|---------|-----------|--------|-------|
| Costa Rica | `CR_ENERGY/t1_confection` | CR | One level deeper |
| Dominican Republic | `RD_ENERGY` | RD | |
| Ecuador | `ECU_Energy` | ECU | Lowercase 'e' |
| Guatemala | `GUA_ENERGY` | GUA | skip-orphan-cap required |
| Honduras | `HON_ENERGY` | HON | |
| Jamaica | `JAM_ENERGY` | JAM | Model horizon to 2055 |
