#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STAGE 1: Share Analyzer (v16) — Unified with Empirical Denominators
=====================================================================
Replaces stage1_share_analyzer_v9.py + stage1b_policy_share_rule_v1.py.
Deprecates Stages 2 and 3.

What's new in v10 vs v9 + 1B
-----------------------------
  * Denominators come from Stage 0 empirical runs (not demand × loss_multiplier)
  * Starting shares come from Stage 0 recommended column (E or D), summing to 100%
  * Policy rule (formerly Stage 1B) is integrated — all 3 scenarios in one pass
  * Real lower limits computed directly: share × empirical_gen (no soft factor)
  * Capacity ceiling enforced: lower_limit ≤ production_potential
  * Share sums = 100% for every (country, scenario, year) by construction

Pipeline position
-----------------
  Stage 0 (done) → STAGE 1 v10 (this) → patch .txt → run glpsol → collect results

Inputs (from Stage 0):
  _STAGE0_OUTPUT/STAGE0_RECOMMENDED_SHARES_EDITED.csv  (or _SHARES.csv fallback)
  _STAGE0_OUTPUT/{Country}/EMPIRICAL_GEN__{Country}__{Scenario}_S0.csv
  _STAGE0_OUTPUT/STAGE0_CAPACITY_CEILING.csv

Inputs (from B1):
  B1_Output_Params/{Scenario}/TotalAnnualMinCapacityInvestment.csv
  B1_Output_Params/{Scenario}/CapacityFactor.csv
  B1_Output_Params/{Scenario}/AvailabilityFactor.csv
  B1_Output_Params/{Scenario}/TotalTechnologyAnnualActivityUpperLimit.csv

Outputs:
  _STAGE1_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx

Usage (from MODELS_LAC_4):
  py stage1_share_analyzer_v15.py
  py stage1_share_analyzer_v15.py --countries Honduras Jamaica
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================
MODELS_LAC_ROOT = "./"
STAGE0_DIR      = "./_STAGE0_OUTPUT"
OUTPUT_DIR      = "./_STAGE1_OUTPUT"

# Stage 0 filenames
RECOMMENDED_SHARES_FILES = [
    "STAGE0_RECOMMENDED_SHARES_EDITED.csv",
    "STAGE0_RECOMMENDED_SHARES.csv",
]
CEILING_FILE = "STAGE0_CAPACITY_CEILING.csv"

# Per-country share column selection (from Stage 0 analysis)
SHARE_COLUMN = {
    "CostaRica":         "Share_E_Proportional_Pct",
    "DominicanRepublic": "Share_E_Proportional_Pct",
    "Ecuador":           "Share_E_Proportional_Pct",
    "Guatemala":         "Share_E_Proportional_Pct",
    "Honduras":          "Share_E_Proportional_Pct",
    "Jamaica":           "Share_E_Proportional_Pct",
}

# Country model directories
COUNTRY_MODEL_DIR = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}

# Scenarios
BAU_SCENARIO      = "BAU"
POLICY_SCENARIOS  = ["NDCNEW", "LTSNEW"]
ALL_SCENARIOS     = [BAU_SCENARIO] + POLICY_SCENARIOS

# BAU rule parameters
ANCHOR_YEAR         = 2024
CUTOFF_YEAR         = 2026
PLATEAU_YEARS       = [2025, 2026]
FOSSIL_DECLINE_RATE = 0.01     # 1%/yr from 2027
HYDRO_DECLINE_RATE  = 0.0      # deprecated in v15: hydro uses PJ freeze instead
CAU                 = 31.536   # CapacityToActivityUnit (PJ/GW/yr)
PP_PREFIXES         = ("PP", "PWR")

# Policy renewable target curves
RENEWABLE_TARGET_CURVE = {
    "NDCNEW": {2035: 0.75, 2050: 0.75},
    "LTSNEW": {2035: 0.75, 2050: 0.99},
}
COUNTRY_TARGET_OVERRIDES = {
    "CostaRica": {
        "NDCNEW": {2035: 0.90, 2050: 0.90},
        "LTSNEW": {2035: 0.99, 2050: 0.99},
    },
    "Ecuador": {
        "NDCNEW": {2035: 0.80, 2050: 0.80},
        "LTSNEW": {2035: 0.80, 2050: 0.99},
    },
}
TARGET_HOLD_YEAR = 2050

# Upper limits
DEFAULT_UPPER_LIMIT     = 9999.0
UPPER_SECURITY_FACTOR   = 1.05   # upper ≥ lower × this

# Costa Rica names
COSTA_RICA_NAMES = ["CostaRica", "COSTARICA", "Costa Rica", "Costa_Rica"]

# Policy tech allocation: solar+wind tokens grow; biomass/biogas/geo locked at BAU
SOLAR_WIND_TOKENS = ["SOL", "SUN", "SPV", "PV", "CSP",    # solar
                     "WND", "WIND", "WNO", "WNS"]           # wind

# Tech classifier tokens
HYDRO_TOKENS     = ["HYD", "DAM", "ROR", "PPHD", "PPIHD"]
RENEWABLE_TOKENS = ["GEO", "SOL", "SUN", "SPV", "PV", "CSP",
                    "WND", "WIND", "WNO", "WNS",
                    "BMS", "BIM", "BIO", "BGS", "SUG", "REN"]
FOSSIL_TOKENS    = ["DSL", "DIE", "FOI", "HFO", "CRU",
                    "COA", "COK", "NGS", "GAS", "GLP", "LPG",
                    "GSL", "KJF", "OIL", "PET", "FOS"]


# =============================================================================
# HELPERS
# =============================================================================

def is_costa_rica(country):
    return country in COSTA_RICA_NAMES


def classify_tech(tech):
    """FOSSIL / HYDRO / NON_HYDRO_RENEWABLE / UNKNOWN."""
    t = str(tech).upper()
    if any(tok in t for tok in HYDRO_TOKENS):
        return "HYDRO"
    if any(tok in t for tok in RENEWABLE_TOKENS):
        return "NON_HYDRO_RENEWABLE"
    if any(tok in t for tok in FOSSIL_TOKENS):
        return "FOSSIL"
    return "UNKNOWN"


def is_pp(tech):
    return str(tech).upper().startswith(PP_PREFIXES)


def read_csv(path):
    if path.exists():
        return pd.read_csv(path)
    return None


def pivot_tech_year(df, default=0.0):
    if df is None or df.empty:
        return pd.DataFrame()
    d = df.copy()
    d["YEAR"] = pd.to_numeric(d["YEAR"], errors="coerce")
    d = d.dropna(subset=["YEAR"])
    d["YEAR"] = d["YEAR"].astype(int)
    if "TIMESLICE" in d.columns:
        d = d.groupby(["TECHNOLOGY", "YEAR"])["Value"].sum().reset_index()
    mat = d.pivot_table(index="TECHNOLOGY", columns="YEAR",
                        values="Value", aggfunc="sum")
    if default is not None:
        mat = mat.fillna(default)
    return mat


# =============================================================================
# STAGE 0 DATA LOADERS
# =============================================================================

def load_recommended_shares(s0_dir):
    """Load recommended shares CSV. Returns DataFrame."""
    for fname in RECOMMENDED_SHARES_FILES:
        p = s0_dir / fname
        if p.exists():
            df = pd.read_csv(p)
            print(f"  [Loaded] {fname} ({len(df)} rows)")
            return df
    print("[ERROR] No recommended shares file found in", s0_dir)
    sys.exit(1)


def load_empirical_gen(s0_dir, country, scenario):
    """Load empirical generation Series (year -> PJ) for a country/scenario."""
    s0_scen = f"{scenario}_S0"
    p = s0_dir / country / f"EMPIRICAL_GEN__{country}__{s0_scen}.csv"
    if not p.exists():
        return pd.Series(dtype=float)
    df = pd.read_csv(p)
    return pd.Series(df["Empirical_Gen_PJ"].values, index=df["Year"].astype(int).values)


def load_ceiling(s0_dir):
    """Load capacity ceiling. Returns dict: (country, scenario, tech, year) -> PJ."""
    p = s0_dir / CEILING_FILE
    if not p.exists():
        print(f"  [WARN] {CEILING_FILE} not found — no ceiling enforcement")
        return {}
    df = pd.read_csv(p)
    ceiling = {}
    for _, row in df.iterrows():
        key = (row["Country"], row["Scenario"], row["Technology"], int(row["Year"]))
        ceiling[key] = float(row["ProdPotential_PJ"])
    print(f"  [Loaded] {CEILING_FILE} ({len(ceiling)} entries)")
    return ceiling


# =============================================================================
# B1 DATA LOADERS
# =============================================================================

def load_b1_data(b1_dir, scenario):
    """Load MinCapInvest, CF, AF, upper limits from B1_Output_Params."""
    sc_dir = b1_dir / scenario
    if not sc_dir.exists():
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # MinCapacityInvestment
    df_mci = read_csv(sc_dir / "TotalAnnualMinCapacityInvestment.csv")
    mci_mat = pivot_tech_year(df_mci) if df_mci is not None else pd.DataFrame()

    # CF (simple pivot — no yearsplit weighting for simplicity)
    df_cf = read_csv(sc_dir / "CapacityFactor.csv")
    cf_mat = pivot_tech_year(df_cf) if df_cf is not None else pd.DataFrame()

    # AF
    df_af = read_csv(sc_dir / "AvailabilityFactor.csv")
    af_mat = pivot_tech_year(df_af) if df_af is not None else pd.DataFrame()

    # Upper limits
    df_ul = read_csv(sc_dir / "TotalTechnologyAnnualActivityUpperLimit.csv")
    ul_mat = pivot_tech_year(df_ul, default=None) if df_ul is not None else pd.DataFrame()

    return {"mci": mci_mat, "cf": cf_mat, "af": af_mat, "upper": ul_mat}


def cumulative_mincap(mci_mat, anchor_year):
    """Cumulative MinCapInvest from anchor_year+1 onward."""
    if mci_mat.empty:
        return pd.DataFrame()
    out = mci_mat.copy().fillna(0.0)
    years = sorted(out.columns)
    proj = [y for y in years if y > anchor_year]
    if not proj:
        return pd.DataFrame(0.0, index=out.index, columns=years)
    cum = out[proj].cumsum(axis=1)
    full = pd.DataFrame(0.0, index=out.index, columns=years)
    for y in proj:
        full[y] = cum[y]
    return full


# =============================================================================
# POLICY CURVE
# =============================================================================

def get_target_curve(country, scenario):
    if country in COUNTRY_TARGET_OVERRIDES:
        if scenario in COUNTRY_TARGET_OVERRIDES[country]:
            return COUNTRY_TARGET_OVERRIDES[country][scenario]
    return RENEWABLE_TARGET_CURVE[scenario]


def policy_renewable_target(year, scenario, anchor_share_2026, country):
    """Piecewise linear renewable target for (year, scenario, country)."""
    if year <= CUTOFF_YEAR:
        return None
    milestones = get_target_curve(country, scenario)
    if year >= TARGET_HOLD_YEAR:
        return milestones[TARGET_HOLD_YEAR]
    pts = [(CUTOFF_YEAR, anchor_share_2026)] + sorted(milestones.items())
    pts = sorted(set(pts))
    for i in range(len(pts) - 1):
        y1, v1 = pts[i]
        y2, v2 = pts[i + 1]
        if y1 <= year <= y2:
            if y2 == y1:
                return v2
            return v1 + (v2 - v1) * (year - y1) / (y2 - y1)
    return milestones[TARGET_HOLD_YEAR]


# =============================================================================
# CORE: Compute shares and limits for one country
# =============================================================================

def process_country(country, rec_shares, s0_dir, ceiling, root, audit_log,
                    global_years):
    """
    Returns list of row dicts for the controller, one per (scenario, tech, year).
    """
    print(f"\n{'='*60}")
    print(f"[Country] {country}")

    model_dir = COUNTRY_MODEL_DIR.get(country)
    if model_dir is None:
        print(f"  [SKIP] No model directory configured")
        return []

    b1_dir = root / country / model_dir / "B1_Output_Params"
    is_cr = is_costa_rica(country)
    col = SHARE_COLUMN.get(country, "Share_E_Proportional_Pct")

    # --- Load recommended shares: per-year for history, 2024 for projection ---
    country_rec = rec_shares[rec_shares["Country"] == country]
    if country_rec.empty:
        print(f"  [SKIP] No recommended shares for {country}")
        return []

    available_hist_years = sorted(country_rec["Year"].unique())

    # Build historical_shares: (tech, year) -> fraction for all available years
    historical_shares = {}  # (tech, year) -> fraction
    for _, row in country_rec.iterrows():
        tech = row["Technology"]
        yr = int(row["Year"])
        if is_pp(tech):
            historical_shares[(tech, yr)] = max(0.0, row[col] / 100.0)

    # Anchor shares at 2024 (used for 2025-2026 plateau and 2027+ rules)
    anchor_rec = country_rec[country_rec["Year"] == ANCHOR_YEAR]
    if anchor_rec.empty:
        print(f"  [SKIP] No recommended shares at {ANCHOR_YEAR}")
        return []

    anchor_shares = {}
    for _, row in anchor_rec.iterrows():
        tech = row["Technology"]
        if is_pp(tech):
            anchor_shares[tech] = max(0.0, row[col] / 100.0)

    # Earliest available year (for bfill of pre-history years)
    earliest_hist_year = min(available_hist_years)

    print(f"  [Shares] {len(anchor_shares)} PP techs from {col}, "
          f"history {earliest_hist_year}-{ANCHOR_YEAR}, "
          f"anchor sum={sum(anchor_shares.values()):.4f}")

    # --- Load empirical gen for all scenarios ---
    emp_gen = {}
    for sc in ALL_SCENARIOS:
        emp_gen[sc] = load_empirical_gen(s0_dir, country, sc)
        if emp_gen[sc].empty:
            print(f"  [WARN] No empirical gen for {sc}")

    # Determine year range from BAU empirical gen
    if emp_gen[BAU_SCENARIO].empty:
        print(f"  [SKIP] No BAU empirical gen")
        return []

    # --- Load B1 data (MinCapInvest, CF, AF, upper limits) ---
    b1 = {}
    cum_mci = {}
    for sc in ALL_SCENARIOS:
        if b1_dir.exists():
            b1[sc] = load_b1_data(b1_dir, sc)
            cum_mci[sc] = cumulative_mincap(b1[sc]["mci"], ANCHOR_YEAR)
        else:
            b1[sc] = {"mci": pd.DataFrame(), "cf": pd.DataFrame(),
                      "af": pd.DataFrame(), "upper": pd.DataFrame()}
            cum_mci[sc] = pd.DataFrame()

    # Determine full year range from B1 + global
    # Use global_years so all countries output the same year columns
    years = global_years

    # Extend empirical gen to cover full year range (ffill/bfill)
    for sc in ALL_SCENARIOS:
        if emp_gen[sc].empty:
            continue
        eg = emp_gen[sc]
        full = pd.Series(index=years, dtype=float)
        for y in years:
            if y in eg.index:
                full[y] = eg[y]
        full = full.ffill().bfill()
        emp_gen[sc] = full
    print(f"  [Years] {years[0]}-{years[-1]} ({len(years)} years)")

    # --- Gather all PP techs (from all historical years + MinCapInvest) ---
    all_techs = set(anchor_shares.keys())
    # Include techs from all historical years (some appear/disappear)
    all_techs.update(t for (t, y) in historical_shares.keys())
    for sc in ALL_SCENARIOS:
        if not b1[sc]["mci"].empty:
            all_techs.update(t for t in b1[sc]["mci"].index if is_pp(t))
    all_techs = sorted(all_techs)

    # Ensure techs not in anchor get share=0
    for t in all_techs:
        if t not in anchor_shares:
            anchor_shares[t] = 0.0

    # Classify techs
    cat = {t: classify_tech(t) for t in all_techs}
    fossil_techs = [t for t in all_techs if cat[t] == "FOSSIL"]
    hydro_techs = [t for t in all_techs if cat[t] == "HYDRO"]
    nh_renew_techs = [t for t in all_techs if cat[t] == "NON_HYDRO_RENEWABLE"]

    # --- Helper: mincap floor for a tech/year ---
    def mincap_floor(tech, year, sc):
        if cum_mci[sc].empty:
            return 0.0
        cm = 0.0
        if tech in cum_mci[sc].index and year in cum_mci[sc].columns:
            cm = float(cum_mci[sc].loc[tech, year])
        if cm <= 0:
            return 0.0
        # CF × AF
        cf = 1.0
        af = 1.0
        if not b1[sc]["cf"].empty and tech in b1[sc]["cf"].index:
            if year in b1[sc]["cf"].columns:
                v = b1[sc]["cf"].loc[tech, year]
                if pd.notna(v):
                    cf = float(v)
        if not b1[sc]["af"].empty and tech in b1[sc]["af"].index:
            if year in b1[sc]["af"].columns:
                v = b1[sc]["af"].loc[tech, year]
                if pd.notna(v) and v > 0:
                    af = float(v)
        return anchor_lower_pj(tech, sc) + cm * cf * af * CAU

    def anchor_lower_pj(tech, sc):
        """Anchor-year lower limit in PJ = anchor_share × empirical_gen[2024]."""
        eg = emp_gen[sc].get(ANCHOR_YEAR, 0.0)
        return anchor_shares.get(tech, 0.0) * eg

    # --- Ceiling lookup ---
    def get_ceiling(tech, year, sc):
        key = (country, sc, tech, year)
        return ceiling.get(key, None)

    # --- Upstream upper limit ---
    def upstream_upper(tech, year, sc):
        ul = b1[sc]["upper"]
        if ul.empty:
            return DEFAULT_UPPER_LIMIT
        if tech in ul.index and year in ul.columns:
            v = ul.loc[tech, year]
            if pd.notna(v):
                return float(v)
        return DEFAULT_UPPER_LIMIT

    # =================================================================
    # STEP 1: Compute BAU shares for all years
    # =================================================================
    bau_shares = {}  # (tech, year) -> fraction

    # Compute hydro PJ floor: freeze at anchor-year absolute generation
    # Share will decline naturally as total generation grows
    anchor_eg = emp_gen[BAU_SCENARIO].get(ANCHOR_YEAR, 0.0)
    hydro_pj_floor = {}  # tech -> PJ (frozen absolute value)
    for t in hydro_techs:
        hydro_pj_floor[t] = anchor_shares[t] * anchor_eg

    for year in years:
        # Historical: use actual per-year recommended shares
        if year <= ANCHOR_YEAR:
            # Find the best matching year from available history
            if year >= earliest_hist_year:
                src_year = year
            else:
                src_year = earliest_hist_year  # bfill for pre-history years

            for t in all_techs:
                bau_shares[(t, year)] = historical_shares.get((t, src_year), 0.0)
            continue

        # Plateau (2025-2026): frozen at 2024 anchor
        if year in PLATEAU_YEARS:
            for t in all_techs:
                bau_shares[(t, year)] = anchor_shares[t]
            continue

        # Projection (2027+)
        decline_exp = year - CUTOFF_YEAR

        # Fossils: 1%/yr decline, but respect MinCapInvest floor
        eg = emp_gen[BAU_SCENARIO].get(year, 0.0)
        for t in fossil_techs:
            base = anchor_shares[t] * (1.0 - FOSSIL_DECLINE_RATE) ** decline_exp
            if eg > 0:
                mf = mincap_floor(t, year, BAU_SCENARIO)
                mf_share = mf / eg
                base = max(base, mf_share)
            bau_shares[(t, year)] = base

        # Hydro: PJ freeze (share declines as demand grows) + mincap floor
        for t in hydro_techs:
            if eg > 0:
                base = hydro_pj_floor[t] / eg  # declining share
                mf = mincap_floor(t, year, BAU_SCENARIO)
                mf_share = mf / eg
                base = max(base, mf_share)
                bau_shares[(t, year)] = base
            else:
                bau_shares[(t, year)] = anchor_shares[t]

        # Non-hydro renewables: gap-fill to 100%
        fossil_sum = sum(bau_shares.get((t, year), 0) for t in fossil_techs)
        hydro_sum = sum(bau_shares.get((t, year), 0) for t in hydro_techs)
        unknown_sum = sum(anchor_shares.get(t, 0) for t in all_techs if cat[t] == "UNKNOWN")
        nh_target = 1.0 - fossil_sum - hydro_sum - unknown_sum

        nh_anchor_sum = sum(anchor_shares.get(t, 0) for t in nh_renew_techs)
        if nh_anchor_sum > 1e-9 and nh_target > 0:
            scale = nh_target / nh_anchor_sum
            for t in nh_renew_techs:
                raw = anchor_shares[t] * scale
                # Mincap floor check
                eg = emp_gen[BAU_SCENARIO].get(year, 0.0)
                if eg > 0:
                    mf = mincap_floor(t, year, BAU_SCENARIO)
                    mf_share = mf / eg
                    raw = max(raw, mf_share)
                bau_shares[(t, year)] = raw
        else:
            for t in nh_renew_techs:
                bau_shares[(t, year)] = anchor_shares.get(t, 0.0)

        # UNKNOWN techs: hold at anchor
        for t in all_techs:
            if cat[t] == "UNKNOWN":
                bau_shares[(t, year)] = anchor_shares[t]

        # Step 2: renormalize if total exceeds 1.0
        # (can happen when hydro/NH-renewable mincap floors inflate shares)
        total = sum(bau_shares.get((t, year), 0) for t in all_techs)
        if total > 1.001:
            # Scale ALL non-UNKNOWN shares proportionally to hit 1.0
            scalable = [t for t in all_techs if cat[t] != "UNKNOWN"]
            scalable_sum = sum(bau_shares.get((t, year), 0) for t in scalable)
            target_sum = 1.0 - unknown_sum
            if scalable_sum > 1e-9:
                factor = target_sum / scalable_sum
                for t in scalable:
                    bau_shares[(t, year)] = bau_shares.get((t, year), 0) * factor
            audit_log.append({
                "Country": country, "Scenario": BAU_SCENARIO, "Year": year,
                "Event": "RENORM", "Raw_Sum": round(total, 4),
                "Adjusted_Sum": round(sum(bau_shares.get((t, year), 0) for t in all_techs), 4),
            })

    # =================================================================
    # STEP 2: Compute policy scenario shares (2027+)
    # =================================================================
    policy_shares = {}  # {scenario: {(tech, year): fraction}}

    for sc in POLICY_SCENARIOS:
        policy_shares[sc] = {}

        # Historical + plateau: copy from BAU
        for year in years:
            if year <= CUTOFF_YEAR:
                for t in all_techs:
                    policy_shares[sc][(t, year)] = bau_shares[(t, year)]

        if is_cr and country not in COUNTRY_TARGET_OVERRIDES:
            # Costa Rica with no override: passthrough BAU for all years
            for year in years:
                if year > CUTOFF_YEAR:
                    for t in all_techs:
                        policy_shares[sc][(t, year)] = bau_shares[(t, year)]
            continue

        # Anchor renewable share at 2026 from BAU
        anchor_renew_2026 = sum(
            bau_shares.get((t, CUTOFF_YEAR), 0)
            for t in all_techs if cat[t] in ("HYDRO", "NON_HYDRO_RENEWABLE")
        )
        anchor_renew_2026 = min(1.0, max(0.0, anchor_renew_2026))

        for year in years:
            if year <= CUTOFF_YEAR:
                continue  # already set above

            target_renew = policy_renewable_target(
                year, sc, anchor_renew_2026, country)
            if target_renew is None:
                for t in all_techs:
                    policy_shares[sc][(t, year)] = bau_shares[(t, year)]
                continue

            # BAU category sums at this year (for BAU floor comparison)
            H_BAU = sum(bau_shares.get((t, year), 0) for t in hydro_techs)
            N_BAU = sum(bau_shares.get((t, year), 0) for t in nh_renew_techs)
            F_BAU = sum(bau_shares.get((t, year), 0) for t in fossil_techs)
            BAU_renewable = H_BAU + N_BAU

            # Hydro: PJ freeze using scenario-specific denominator
            eg_policy = emp_gen[sc].get(year, 0.0)
            for t in hydro_techs:
                if eg_policy > 0:
                    base = hydro_pj_floor[t] / eg_policy
                    mf = mincap_floor(t, year, sc)
                    mf_share = mf / eg_policy
                    policy_shares[sc][(t, year)] = max(base, mf_share)
                else:
                    policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0)

            H_policy = sum(policy_shares[sc].get((t, year), 0) for t in hydro_techs)

            # BAU floor: never suppress renewables below BAU
            T = max(target_renew, BAU_renewable)
            N_target = T - H_policy  # use policy hydro (lower than BAU due to bigger denominator)
            F_target = max(0.0, 1.0 - T)

            # NH-renewables: split into growth (solar/wind) and locked (biomass etc.)
            def is_solar_wind(tech):
                return any(tok in str(tech).upper() for tok in SOLAR_WIND_TOKENS)

            growth_techs = [t for t in nh_renew_techs if is_solar_wind(t)]
            locked_techs = [t for t in nh_renew_techs if not is_solar_wind(t)]

            # Lock biomass/biogas/geo at BAU share
            locked_sum = sum(bau_shares.get((t, year), 0) for t in locked_techs)
            for t in locked_techs:
                policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0)

            # Growth techs (solar/wind) absorb the remainder
            growth_target = max(0.0, N_target - locked_sum)
            growth_bau_sum = sum(bau_shares.get((t, year), 0) for t in growth_techs)

            if growth_bau_sum > 1e-9 and growth_target > 0:
                scale_G = growth_target / growth_bau_sum
                for t in growth_techs:
                    policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0) * scale_G
            elif growth_techs and growth_target > 0:
                # Fallback: equal split among growth techs
                per = growth_target / len(growth_techs)
                for t in growth_techs:
                    policy_shares[sc][(t, year)] = per
            else:
                # No growth needed or no growth techs
                for t in growth_techs:
                    policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0)

            # If locked_sum > N_target (locked techs alone exceed allocation),
            # scale locked techs down and zero growth techs
            if locked_sum > N_target and N_target > 0:
                factor = N_target / locked_sum
                for t in locked_techs:
                    policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0) * factor
                for t in growth_techs:
                    policy_shares[sc][(t, year)] = 0.0

            # Fossils: scale proportionally
            if F_BAU > 1e-9:
                scale_F = F_target / F_BAU
                for t in fossil_techs:
                    policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0) * scale_F
            elif fossil_techs:
                per = F_target / len(fossil_techs)
                for t in fossil_techs:
                    policy_shares[sc][(t, year)] = per

            # UNKNOWN: hold at BAU
            for t in all_techs:
                if cat[t] == "UNKNOWN":
                    policy_shares[sc][(t, year)] = bau_shares.get((t, year), 0)

            # Renormalize if total exceeds 1.0
            # (happens when H_policy << H_BAU and growth scaling overflows)
            pol_total = sum(policy_shares[sc].get((t, year), 0) for t in all_techs)
            if pol_total > 1.001:
                unknown_sum_p = sum(policy_shares[sc].get((t, year), 0)
                                    for t in all_techs if cat[t] == "UNKNOWN")
                scalable = [t for t in all_techs if cat[t] != "UNKNOWN"]
                scalable_sum = sum(policy_shares[sc].get((t, year), 0) for t in scalable)
                target_sum = 1.0 - unknown_sum_p
                if scalable_sum > 1e-9:
                    factor = target_sum / scalable_sum
                    for t in scalable:
                        policy_shares[sc][(t, year)] = policy_shares[sc].get((t, year), 0) * factor

            audit_log.append({
                "Country": country, "Scenario": sc, "Year": year,
                "Event": "POLICY",
                "Target_Renewable": round(target_renew, 4),
                "BAU_Renewable": round(BAU_renewable, 4),
                "H_BAU": round(H_BAU, 4),
                "H_Policy": round(H_policy, 4),
                "N_BAU": round(N_BAU, 4),
                "F_BAU": round(F_BAU, 4),
                "T_Final": round(T, 4),
                "N_Target": round(N_target, 4),
                "F_Target": round(F_target, 4),
                "Locked_Sum": round(locked_sum, 4),
                "Growth_Target": round(max(0.0, N_target - locked_sum), 4),
            })

    # =================================================================
    # STEP 3: Compute lower/upper limits and build controller rows
    # =================================================================
    all_scenario_shares = {BAU_SCENARIO: bau_shares}
    all_scenario_shares.update(policy_shares)

    rows = []
    for sc in ALL_SCENARIOS:
        sc_shares = all_scenario_shares.get(sc, {})
        eg = emp_gen.get(sc, pd.Series(dtype=float))

        for tech in all_techs:
            is_ren = cat[tech] in ("HYDRO", "NON_HYDRO_RENEWABLE")
            group = "RENEWABLE" if is_ren else ("FOSSIL" if cat[tech] == "FOSSIL" else "UNKNOWN")

            row = {
                "Country": country,
                "Model": COUNTRY_MODEL_DIR[country].split("/")[-1],
                "Scenario": sc,
                "Tech": tech,
                "Is_Renewable": 1 if is_ren else (0 if cat[tech] == "FOSSIL" else ""),
                "Group": group,
                "Sub_Group": cat[tech],
                "Source": "v10",
            }

            for year in years:
                share = sc_shares.get((tech, year), 0.0)
                total_gen = eg.get(year, 0.0)

                # Lower limit
                lower = share * total_gen

                # Ceiling cap
                ceil = get_ceiling(tech, year, sc)
                if ceil is not None and ceil > 0 and lower > ceil:
                    lower = ceil

                # Upper limit: ensure ≥ lower
                ups_upper = upstream_upper(tech, year, sc)
                upper = max(lower * UPPER_SECURITY_FACTOR, ups_upper)
                if upper < lower:
                    upper = lower * UPPER_SECURITY_FACTOR

                row[f"Share_{year}"] = round(share, 6)
                row[f"Lower_{year}"] = round(lower, 4)
                row[f"Upper_{year}"] = round(upper, 4)

            rows.append(row)

    # Summary
    for sc in ALL_SCENARIOS:
        for year in [ANCHOR_YEAR, 2030, 2040, 2050]:
            if year not in years:
                continue
            s = sum(all_scenario_shares.get(sc, {}).get((t, year), 0) for t in all_techs)
            renew = sum(
                all_scenario_shares.get(sc, {}).get((t, year), 0)
                for t in all_techs if cat[t] in ("HYDRO", "NON_HYDRO_RENEWABLE")
            )
            print(f"  [{sc:8s} {year}] shares={s:.4f}  renewable={renew:.4f}")

    return rows


# =============================================================================
# WRITE CONTROLLER
# =============================================================================

def write_controller(all_rows, audit_log, output_dir):
    if not all_rows:
        print("[ERROR] No rows to write.")
        return

    df = pd.DataFrame(all_rows)
    base_cols = ["Country", "Model", "Scenario", "Tech",
                 "Is_Renewable", "Group", "Sub_Group", "Source"]

    share_cols = sorted([c for c in df.columns if c.startswith("Share_")],
                        key=lambda c: int(c.replace("Share_", "")))
    lower_cols = sorted([c for c in df.columns if c.startswith("Lower_")],
                        key=lambda c: int(c.replace("Lower_", "")))
    upper_cols = sorted([c for c in df.columns if c.startswith("Upper_")],
                        key=lambda c: int(c.replace("Upper_", "")))

    # CURRENT_SHARES
    df_cs = df[base_cols + share_cols].copy()
    df_cs.columns = base_cols + [int(c.replace("Share_", "")) for c in share_cols]

    # TARGET_SHARES (same as current in v10 — all are final)
    df_ts = df_cs.copy()

    # CURRENT_LOWER
    df_cl = df[base_cols + lower_cols].copy()
    df_cl.columns = base_cols + [int(c.replace("Lower_", "")) for c in lower_cols]

    # CURRENT_UPPER
    df_cu = df[base_cols + upper_cols].copy()
    df_cu.columns = base_cols + [int(c.replace("Upper_", "")) for c in upper_cols]

    # TECH_MAP
    tech_rows = []
    for tech in sorted(df["Tech"].unique()):
        c = classify_tech(tech)
        is_ren = c in ("HYDRO", "NON_HYDRO_RENEWABLE")
        tech_rows.append({
            "Tech": tech,
            "Is_Renewable": 1 if is_ren else (0 if c == "FOSSIL" else ""),
            "Group": "RENEWABLE" if is_ren else ("FOSSIL" if c == "FOSSIL" else "UNKNOWN"),
            "Sub_Group": c,
        })
    df_tm = pd.DataFrame(tech_rows)

    # README
    readme = pd.DataFrame([
        {"Item": "Purpose", "Value": "Controller workbook (v10): empirical denominators + integrated policy rule"},
        {"Item": "Generated", "Value": datetime.now().isoformat()},
        {"Item": "Version", "Value": "v15 (replaces v9 + Stage 1B; deprecates Stages 2/3)"},
        {"Item": "", "Value": ""},
        {"Item": "STAGE 0 INPUTS", "Value": ""},
        {"Item": "  Shares", "Value": f"Column per country: {SHARE_COLUMN}"},
        {"Item": "  Denominator", "Value": "Empirical gen from Stage 0 relaxed runs"},
        {"Item": "  Ceiling", "Value": "STAGE0_CAPACITY_CEILING.csv"},
        {"Item": "", "Value": ""},
        {"Item": "BAU RULE", "Value": ""},
        {"Item": "  Anchor", "Value": str(ANCHOR_YEAR)},
        {"Item": "  Cutoff", "Value": str(CUTOFF_YEAR)},
        {"Item": "  Fossils", "Value": f"{FOSSIL_DECLINE_RATE*100:.1f}%/yr decline from 2027"},
        {"Item": "  Hydro", "Value": f"freeze + MinCapInvest"},
        {"Item": "  NH-Renewable", "Value": "gap-fill to 100%"},
        {"Item": "  Costa Rica", "Value": "same rules as other countries (BAU); managed per COUNTRY_TARGET_OVERRIDES (policy)"},
        {"Item": "", "Value": ""},
        {"Item": "POLICY RULE", "Value": ""},
        {"Item": "  NDCNEW", "Value": str(RENEWABLE_TARGET_CURVE.get("NDCNEW", {}))},
        {"Item": "  LTSNEW", "Value": str(RENEWABLE_TARGET_CURVE.get("LTSNEW", {}))},
        {"Item": "  CR overrides", "Value": str(COUNTRY_TARGET_OVERRIDES.get("CostaRica", {}))},
        {"Item": "", "Value": ""},
        {"Item": "SHARES", "Value": "Sum to 100% for all (country, scenario, year) by construction"},
        {"Item": "LOWER LIMITS", "Value": "share × empirical_gen, capped at production potential"},
        {"Item": "UPPER LIMITS", "Value": f"max(lower × {UPPER_SECURITY_FACTOR}, upstream)"},
    ])

    # AUDIT
    df_audit = pd.DataFrame(audit_log) if audit_log else pd.DataFrame()

    # Write
    ctrl_path = Path(output_dir) / "CONTROLLER_NEW_SCENARIOS.xlsx"
    with pd.ExcelWriter(ctrl_path, engine="openpyxl") as writer:
        readme.to_excel(writer, sheet_name="README", index=False)
        df_cs.to_excel(writer, sheet_name="CURRENT_SHARES", index=False)
        df_ts.to_excel(writer, sheet_name="TARGET_SHARES", index=False)
        df_cl.to_excel(writer, sheet_name="CURRENT_LOWER", index=False)
        df_cu.to_excel(writer, sheet_name="CURRENT_UPPER", index=False)
        df_tm.to_excel(writer, sheet_name="TECH_MAP", index=False)
        if not df_audit.empty:
            df_audit.to_excel(writer, sheet_name="AUDIT", index=False)

    print(f"\n[Wrote] {ctrl_path}")
    print(f"  Countries: {df['Country'].nunique()}")
    print(f"  Scenarios: {df['Scenario'].nunique()}")
    print(f"  Techs:     {df['Tech'].nunique()}")
    years_out = sorted({int(c.replace("Share_", "")) for c in share_cols})
    print(f"  Years:     {years_out[0]}-{years_out[-1]}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Stage 1 v10: Unified Share Analyzer")
    parser.add_argument("--countries", nargs="*", default=[])
    parser.add_argument("--output-dir", default=OUTPUT_DIR)
    parser.add_argument("--stage0-dir", default=STAGE0_DIR)
    args = parser.parse_args()

    root = Path(MODELS_LAC_ROOT).resolve()
    s0_dir = Path(args.stage0_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("STAGE 1: Share Analyzer (v15)")
    print("  Empirical denominators + integrated policy rule")
    print("  Deprecates v9 + Stage 1B + Stages 2/3")
    print("=" * 70)
    print(f"Timestamp:   {datetime.now().isoformat()}")
    print(f"Stage 0 dir: {s0_dir}")
    print(f"Output dir:  {out_dir}")
    print(f"Anchor:      {ANCHOR_YEAR} | Cutoff: {CUTOFF_YEAR}")
    print(f"Fossil decline: {FOSSIL_DECLINE_RATE*100:.1f}%/yr")
    print()

    # Load Stage 0 data
    print("Loading Stage 0 outputs...")
    rec_shares = load_recommended_shares(s0_dir)
    ceiling = load_ceiling(s0_dir)

    # Process each country
    countries = sorted(COUNTRY_MODEL_DIR.keys())
    if args.countries:
        countries = [c for c in countries if c in args.countries]
    print(f"\nCountries to process: {countries}")

    # Pre-scan: determine global year range across all countries
    global_years = set()
    for country in countries:
        model_dir = COUNTRY_MODEL_DIR.get(country)
        if model_dir is None:
            continue
        b1_dir = root / country / model_dir / "B1_Output_Params"
        # Empirical gen years
        eg = load_empirical_gen(s0_dir, country, BAU_SCENARIO)
        if not eg.empty:
            global_years.update(int(y) for y in eg.index)
        # B1 years
        if b1_dir.exists():
            for sc in ALL_SCENARIOS:
                sc_dir = b1_dir / sc
                if not sc_dir.exists():
                    continue
                for fname in ["TotalAnnualMinCapacityInvestment.csv",
                              "TotalTechnologyAnnualActivityUpperLimit.csv"]:
                    p = sc_dir / fname
                    if p.exists():
                        try:
                            df = pd.read_csv(p)
                            if "YEAR" in df.columns:
                                global_years.update(
                                    int(y) for y in pd.to_numeric(
                                        df["YEAR"], errors="coerce").dropna())
                        except Exception:
                            pass
    global_years = sorted(global_years)
    print(f"Global year range: {global_years[0]}-{global_years[-1]} "
          f"({len(global_years)} years)")

    all_rows = []
    audit_log = []

    for country in countries:
        rows = process_country(country, rec_shares, s0_dir, ceiling,
                               root, audit_log, global_years)
        all_rows.extend(rows)

    # Write controller
    write_controller(all_rows, audit_log, out_dir)

    print(f"\n{'='*70}")
    print("STAGE 1 v15 COMPLETE")
    print("=" * 70)
    print(f"Next: run stage1_test_v15.py to validate")
    print(f"Then: stage1_patch_final.py to prepare real OSeMOSYS runs")


if __name__ == "__main__":
    main()
