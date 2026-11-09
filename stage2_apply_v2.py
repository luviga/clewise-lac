#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stage2_apply_v2.py — Apply research-corrected shares to Stage 1 CONTROLLER.
============================================================================

Takes:  Stage 1 CONTROLLER + per-country overwrite CSVs
Makes:  Stage 2 CONTROLLER with:
         - Corrected historical shares (from CSVs)
         - Freeze propagation (2025=2026=corrected 2024 where CSV ends at 2024)
         - Forward rebase (2027+): Stage 1 rules re-applied from corrected base
         - Recalculated lower/upper limits

Stage 1 rules preserved:
  - Fossil decline: 1%/yr from cutoff (Costa Rica: 0%)
  - Hydro PJ freeze: absolute PJ locked at corrected anchor value
  - NH-Renewable gap-fill: solar+wind absorb freed capacity
  - Policy targets: NDCNEW/LTSNEW milestones respected
  - Shares sum to 1.0 everywhere

Usage (from MODELS_LAC_4):
  py stage2_apply_v2.py
  py stage2_apply_v2.py --stage1 _STAGE1_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx
  py stage2_apply_v2.py --dry-run
"""

import argparse
import csv
import sys
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd

# =============================================================================
# CONFIG — mirrors Stage 1 v15/v16
# =============================================================================
CUTOFF_YEAR         = 2026
ANCHOR_YEAR         = 2024
PLATEAU_YEARS       = [2025, 2026]
FOSSIL_DECLINE_RATE = 0.01       # 1%/yr from 2027
UPPER_SECURITY_FAC  = 1.05
DEFAULT_UPPER       = 9999.0
YEAR_MIN, YEAR_MAX  = 2018, 2055
CAU                 = 31.536     # CapacityToActivityUnit (PJ/GW/yr)

# Country model directories (same as Stage 1)
COUNTRY_MODEL_DIR = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}

# Policy targets (same as Stage 1)
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

COSTA_RICA_NAMES = ["CostaRica"]

# Tech classifier tokens (same as Stage 1)
HYDRO_TOKENS     = ["HYD", "DAM", "ROR", "PPHD", "PPIHD"]
RENEWABLE_TOKENS = ["GEO", "SOL", "SUN", "SPV", "PV", "CSP",
                    "WND", "WIND", "WNO", "WNS",
                    "BMS", "BIM", "BIO", "BGS", "SUG", "REN"]
FOSSIL_TOKENS    = ["DSL", "DIE", "FOI", "HFO", "CRU",
                    "COA", "COK", "NGS", "GAS", "GLP", "LPG",
                    "GSL", "KJF", "OIL", "PET", "FOS"]
SOLAR_WIND_TOKENS = ["SOL", "SUN", "SPV", "PV", "CSP",
                     "WND", "WIND", "WNO", "WNS"]

# All CSVs apply only to years ≤ CUTOFF_YEAR. No exceptions.
# Rules handle 2027+ for every country and scenario.
CSV_FORWARD_EXCEPTIONS = set()  # empty — no exceptions

# Enforce policy RE target exactly at post-cutoff years.
# NDCNEW = exact target (not higher), LTSNEW = exact target.
# RE = max(target, BAU_RE) at each year.
ENFORCE_POLICY_EXACT = True


def classify_tech(tech):
    t = str(tech).upper()
    if any(tok in t for tok in HYDRO_TOKENS):
        return "HYDRO"
    if any(tok in t for tok in RENEWABLE_TOKENS):
        return "NON_HYDRO_RENEWABLE"
    if any(tok in t for tok in FOSSIL_TOKENS):
        return "FOSSIL"
    return "UNKNOWN"


def is_solar_wind(tech):
    return any(tok in str(tech).upper() for tok in SOLAR_WIND_TOKENS)


def is_costa_rica(country):
    return country in COSTA_RICA_NAMES


def get_target_curve(country, scenario):
    if country in COUNTRY_TARGET_OVERRIDES:
        if scenario in COUNTRY_TARGET_OVERRIDES[country]:
            return COUNTRY_TARGET_OVERRIDES[country][scenario]
    return RENEWABLE_TARGET_CURVE.get(scenario, {})


def policy_renewable_target(year, scenario, anchor_share, country):
    if year <= CUTOFF_YEAR:
        return None
    milestones = get_target_curve(country, scenario)
    if not milestones:
        return None
    if year >= TARGET_HOLD_YEAR:
        return milestones.get(TARGET_HOLD_YEAR, None)
    pts = [(CUTOFF_YEAR, anchor_share)] + sorted(milestones.items())
    pts = sorted(set(pts))
    for i in range(len(pts) - 1):
        y1, v1 = pts[i]
        y2, v2 = pts[i + 1]
        if y1 <= year <= y2:
            if y2 == y1:
                return v2
            return v1 + (v2 - v1) * (year - y1) / (y2 - y1)
    return milestones.get(TARGET_HOLD_YEAR, None)


# =============================================================================
# B1 DATA LOADERS (mirrors Stage 1)
# =============================================================================

def read_b1_csv(path):
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


def load_b1_data(b1_dir, scenario):
    """Load MinCapInvest, CF, AF from B1_Output_Params/{scenario}/."""
    sc_dir = b1_dir / scenario
    if not sc_dir.exists():
        return {"mci": pd.DataFrame(), "cf": pd.DataFrame(), "af": pd.DataFrame()}

    df_mci = read_b1_csv(sc_dir / "TotalAnnualMinCapacityInvestment.csv")
    mci_mat = pivot_tech_year(df_mci) if df_mci is not None else pd.DataFrame()

    df_cf = read_b1_csv(sc_dir / "CapacityFactor.csv")
    cf_mat = pivot_tech_year(df_cf) if df_cf is not None else pd.DataFrame()

    df_af = read_b1_csv(sc_dir / "AvailabilityFactor.csv")
    af_mat = pivot_tech_year(df_af) if df_af is not None else pd.DataFrame()

    return {"mci": mci_mat, "cf": cf_mat, "af": af_mat}


def cumulative_mincap(mci_mat, from_year):
    """Cumulative MinCapInvest from from_year+1 onward."""
    if mci_mat.empty:
        return pd.DataFrame()
    out = mci_mat.copy().fillna(0.0)
    years = sorted(out.columns)
    proj = [y for y in years if y > from_year]
    if not proj:
        return pd.DataFrame(0.0, index=out.index, columns=years)
    cum = out[proj].cumsum(axis=1)
    full = pd.DataFrame(0.0, index=out.index, columns=years)
    for y in proj:
        full[y] = cum[y]
    return full


def load_all_b1(root, years):
    """Load B1 data for all countries and scenarios.

    Returns:
      b1_data: dict[(country, scenario)] -> {mci, cf, af}
      cum_mci: dict[(country, scenario)] -> DataFrame (cumulative from CUTOFF_YEAR)
    """
    b1_data = {}
    cum_mci_all = {}
    all_scenarios = ["BAU", "NDCNEW", "LTSNEW"]

    for country, model_dir in COUNTRY_MODEL_DIR.items():
        b1_dir = root / country / model_dir / "B1_Output_Params"
        if not b1_dir.exists():
            print(f"  [WARN] No B1_Output_Params for {country} at {b1_dir}")
            for sc in all_scenarios:
                b1_data[(country, sc)] = {"mci": pd.DataFrame(), "cf": pd.DataFrame(), "af": pd.DataFrame()}
                cum_mci_all[(country, sc)] = pd.DataFrame()
            continue

        n_techs = 0
        for sc in all_scenarios:
            b1 = load_b1_data(b1_dir, sc)
            b1_data[(country, sc)] = b1
            cum = cumulative_mincap(b1["mci"], CUTOFF_YEAR)
            cum_mci_all[(country, sc)] = cum
            if not cum.empty:
                nonzero = (cum > 0).any(axis=1).sum()
                n_techs += nonzero
        if n_techs:
            print(f"  {country}: {n_techs} techs with MinCapInvest across scenarios")

    return b1_data, cum_mci_all


def get_mincap_floor_pj(tech, year, boundary_pj, cum_mci, b1, country, scenario):
    """Compute mincap floor in PJ for a tech at a year.

    = boundary_PJ + cumulative_new_GW × CF × AF × 31.536
    Returns 0 if no committed capacity exists (rule-based share takes precedence).
    """
    cm = cum_mci.get((country, scenario), pd.DataFrame())
    if cm.empty:
        return 0.0  # no B1 data — rules handle it

    cum_gw = 0.0
    if tech in cm.index and year in cm.columns:
        cum_gw = float(cm.loc[tech, year])
    if cum_gw <= 0:
        return 0.0  # no committed capacity for this tech — rules handle it

    # Get CF and AF
    b1_cs = b1.get((country, scenario), {})
    cf = 1.0
    af = 1.0
    cf_mat = b1_cs.get("cf", pd.DataFrame())
    af_mat = b1_cs.get("af", pd.DataFrame())

    if not cf_mat.empty and tech in cf_mat.index:
        if year in cf_mat.columns:
            v = cf_mat.loc[tech, year]
            if pd.notna(v):
                cf = float(v)
    if not af_mat.empty and tech in af_mat.index:
        if year in af_mat.columns:
            v = af_mat.loc[tech, year]
            if pd.notna(v) and v > 0:
                af = float(v)

    return boundary_pj + cum_gw * cf * af * CAU


# =============================================================================
# LOADERS
# =============================================================================

def load_controller(path):
    """Load Stage 1 CONTROLLER into nested dicts.

    Returns:
      data: dict[(country, scenario, tech)] -> {
          'group', 'sub_group', 'is_renewable',
          'shares': {year: float}, 'lower': {year: float}, 'upper': {year: float}
      }
      years: sorted list of year ints
      meta: dict of row metadata (country, model, scenario, tech, ...)
    """
    wb = openpyxl.load_workbook(path, data_only=True)
    ws_s = wb["CURRENT_SHARES"]
    ws_l = wb["CURRENT_LOWER"]
    ws_u = wb["CURRENT_UPPER"]

    headers = [c.value for c in ws_s[1]]
    year_cols = {h: i + 1 for i, h in enumerate(headers) if isinstance(h, int)}
    years = sorted(year_cols.keys())

    data = {}
    meta = {}
    for r in range(2, ws_s.max_row + 1):
        country  = ws_s.cell(r, 1).value
        model    = ws_s.cell(r, 2).value
        scenario = ws_s.cell(r, 3).value
        tech     = ws_s.cell(r, 4).value
        is_ren   = ws_s.cell(r, 5).value
        group    = ws_s.cell(r, 6).value
        sub_grp  = ws_s.cell(r, 7).value
        source   = ws_s.cell(r, 8).value

        if not (country and scenario and tech):
            continue

        key = (country, scenario, tech)
        shares, lowers, uppers = {}, {}, {}
        for y, col in year_cols.items():
            shares[y] = ws_s.cell(r, col).value or 0.0
            lowers[y] = ws_l.cell(r, col).value or 0.0
            uppers[y] = ws_u.cell(r, col).value or 0.0

        data[key] = {
            "group": group, "sub_group": sub_grp, "is_renewable": is_ren,
            "shares": shares, "lower": lowers, "upper": uppers,
        }
        meta[key] = {
            "Country": country, "Model": model, "Scenario": scenario,
            "Tech": tech, "Is_Renewable": is_ren,
            "Group": group, "Sub_Group": sub_grp, "Source": source,
        }

    return data, years, meta


def load_overrides(override_dir):
    """Load and deduplicate all overwrite CSVs.

    Returns:
      overrides: dict[(country, scenario, tech, year)] -> share_fraction
      notes:     dict[(country, scenario, tech, year)] -> note string
    """
    csvs = sorted(Path(override_dir).glob("STAGE2_OVERWRITES*.csv"))
    if not csvs:
        print(f"[WARN] No STAGE2_OVERWRITES*.csv found in {override_dir}")
        return {}, {}

    raw = {}  # (c, s, t, y) -> (share_pct, note, source_file)
    for p in csvs:
        with open(p, encoding="utf-8-sig") as f:
            for line in f:
                if line.lstrip().startswith("#") or not line.strip():
                    continue
                if line.startswith("Country"):
                    continue
                parts = line.split(",", 5)
                if len(parts) < 5:
                    continue
                try:
                    c = parts[0].strip()
                    s = parts[1].strip()
                    t = parts[2].strip()
                    y = int(float(parts[3].strip()))
                    pct = float(parts[4].strip())
                except (ValueError, IndexError):
                    continue
                note = parts[5].strip().strip('"') if len(parts) > 5 else ""
                key = (c, s, t, y)
                if key not in raw:
                    raw[key] = (pct, note, str(p))

    overrides = {k: v[0] / 100.0 for k, v in raw.items()}
    notes = {k: v[1] for k, v in raw.items()}

    # Summary
    countries = sorted(set(k[0] for k in overrides))
    print(f"[Overrides] {len(overrides)} anchor points from {len(csvs)} files")
    for c in countries:
        n = sum(1 for k in overrides if k[0] == c)
        yrs = sorted(set(k[3] for k in overrides if k[0] == c))
        print(f"  {c}: {n} points, years {min(yrs)}-{max(yrs)}")

    return overrides, notes


# =============================================================================
# CORE: Load total generation from Stage 0 empirical data
# =============================================================================

def load_total_gen_from_stage0(stage0_denominators_path):
    """Load real total generation from STAGE0_DENOMINATORS.xlsx.

    This is the unconstrained GLPK production — the correct denominator.
    DO NOT derive from sum(lower limits) — those are ceiling-capped.
    """
    wb = openpyxl.load_workbook(stage0_denominators_path, data_only=True)
    ws = wb["ALL"]

    tg = {}
    for r in range(2, ws.max_row + 1):
        country = ws.cell(r, 1).value
        scenario_raw = ws.cell(r, 2).value
        year = ws.cell(r, 3).value
        gen_pj = ws.cell(r, 4).value
        if not (country and scenario_raw and year and gen_pj):
            continue
        scenario = str(scenario_raw).replace("_S0", "")
        tg[(country, scenario, int(year))] = float(gen_pj)

    # Forward-fill / back-fill to cover full year range
    countries = sorted(set(k[0] for k in tg))
    scenarios = sorted(set(k[1] for k in tg))
    all_years = sorted(set(k[2] for k in tg))

    for c in countries:
        for s in scenarios:
            series = {y: tg.get((c, s, y)) for y in all_years}
            # Forward-fill
            last = None
            for y in all_years:
                if series[y] is not None:
                    last = series[y]
                elif last is not None:
                    tg[(c, s, y)] = last
            # Back-fill
            first = None
            for y in reversed(all_years):
                if (c, s, y) in tg:
                    first = tg[(c, s, y)]
                elif first is not None:
                    tg[(c, s, y)] = first

    return tg


def derive_total_gen_fallback(data, years):
    """FALLBACK: derive total_gen from sum(lower limits) when Stage 0 unavailable.

    WARNING: This underestimates demand when ceiling caps bind.
    """
    tg = defaultdict(float)
    for (c, s, t), rec in data.items():
        for y in years:
            tg[(c, s, y)] += rec["lower"].get(y, 0.0)
    return dict(tg)


# =============================================================================
# CORE: Apply overrides + forward rebase
# =============================================================================

def apply_stage2(s1_data, years, overrides, total_gen, audit_log,
                 b1_data=None, cum_mci=None):
    """Build Stage 2 shares from Stage 1 data + overrides.

    Returns s2_shares: dict[(country, scenario, tech)] -> {year: share}
    """
    # Group data by (country, scenario)
    cs_techs = defaultdict(set)
    for (c, s, t) in s1_data:
        cs_techs[(c, s)].add(t)

    # Classify all techs
    cat = {}
    for (c, s, t) in s1_data:
        if t not in cat:
            cat[t] = classify_tech(t)

    # Build override lookup per (c, s)
    cs_overrides = defaultdict(dict)  # (c, s) -> {(tech, year): share}
    skipped = 0
    for (c, s, t, y), share in overrides.items():
        # Default: skip forward years. Exception: CSV_FORWARD_EXCEPTIONS.
        if y > CUTOFF_YEAR and (c, s) not in CSV_FORWARD_EXCEPTIONS:
            skipped += 1
            continue
        cs_overrides[(c, s)][(t, y)] = share
    if skipped:
        print(f"  [Skip] {skipped} CSV forward-year overrides (rules handle 2027+)")
        for cs in CSV_FORWARD_EXCEPTIONS:
            print(f"  [Exception] {cs[0]} {cs[1]}: CSV forward years kept")

    # Determine override type per (c, s, year):
    # "full" if all techs specified (sum ≈ 1.0), "partial" otherwise
    cs_year_type = {}
    for (c, s), ov in cs_overrides.items():
        all_techs = cs_techs[(c, s)]
        ov_by_year = defaultdict(dict)
        for (t, y), sh in ov.items():
            ov_by_year[y][t] = sh
        for y, techs in ov_by_year.items():
            s_sum = sum(techs.values())
            cs_year_type[(c, s, y)] = "full" if abs(s_sum - 1.0) < 0.02 else "partial"

    s2_shares = {}

    for (c, s), techs in sorted(cs_techs.items()):
        techs = sorted(techs)
        ov = cs_overrides.get((c, s), {})

        # Anchor years from overrides for this (c, s)
        ov_years = sorted(set(y for (t, y) in ov))
        last_ov_year = max(ov_years) if ov_years else None

        # Determine correction boundary: furthest corrected year
        # If CSV ends at 2024 or earlier, propagate freeze to 2026
        if last_ov_year is not None:
            if last_ov_year <= ANCHOR_YEAR:
                correction_boundary = CUTOFF_YEAR  # freeze propagation
            else:
                correction_boundary = last_ov_year
        else:
            correction_boundary = None  # no corrections for this (c, s)

        # Classify techs for this country
        fossil_techs = [t for t in techs if cat.get(t) == "FOSSIL"]
        hydro_techs  = [t for t in techs if cat.get(t) == "HYDRO"]
        nh_ren_techs = [t for t in techs if cat.get(t) == "NON_HYDRO_RENEWABLE"]
        growth_techs = [t for t in nh_ren_techs if is_solar_wind(t)]
        locked_techs = [t for t in nh_ren_techs if not is_solar_wind(t)]

        # ─── Phase 1: Set corrected + frozen years ───
        for t in techs:
            s2_shares[(c, s, t)] = {}

        for y in years:
            if correction_boundary is None:
                # No corrections — pass through Stage 1
                for t in techs:
                    s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][y]
                continue

            if y in ov_years:
                ytype = cs_year_type.get((c, s, y), "partial")
                if ytype == "full":
                    # Full replacement: use CSV values directly
                    for t in techs:
                        s2_shares[(c, s, t)][y] = ov.get((t, y), 0.0)
                else:
                    # Partial: set overridden techs, renormalize rest within group
                    _apply_partial(s1_data, s2_shares, c, s, techs, y, ov, cat)

            elif y in PLATEAU_YEARS and last_ov_year is not None and last_ov_year <= ANCHOR_YEAR:
                # Freeze propagation: 2025/2026 = corrected 2024
                src = ANCHOR_YEAR
                for t in techs:
                    val = ov.get((t, src), None)
                    if val is not None:
                        s2_shares[(c, s, t)][y] = val
                    else:
                        # Tech not in CSV for anchor year — use Stage 1 anchor
                        s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][src]

            elif ov_years and min(ov_years) <= y <= max(ov_years):
                # Between anchors: interpolate per tech
                _interpolate_year(s2_shares, c, s, techs, y, ov, ov_years, s1_data)

            elif y <= correction_boundary:
                # Inside correction zone but no anchor — keep Stage 1
                for t in techs:
                    s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][y]

            else:
                # Forward year — will be filled in Phase 2
                pass

        # ─── Phase 2: Forward rebase (years > correction_boundary) ───
        if correction_boundary is None:
            continue

        # Get corrected shares at boundary
        boundary_shares = {t: s2_shares[(c, s, t)].get(correction_boundary, 0.0)
                           for t in techs}

        # Hydro PJ floor from corrected boundary
        tg_boundary = total_gen.get((c, s, correction_boundary), 0.0)
        hydro_pj_floor = {}
        for t in hydro_techs:
            hydro_pj_floor[t] = boundary_shares[t] * tg_boundary

        # Locked (biomass/geo) PJ floor — same logic as hydro
        locked_pj_floor = {}
        for t in locked_techs:
            locked_pj_floor[t] = boundary_shares[t] * tg_boundary

        # Renewable share at boundary (for policy curve anchor)
        ren_at_boundary = sum(boundary_shares.get(t, 0) for t in techs
                              if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))

        # Boundary PJ per tech (for mincap floor base)
        boundary_pj = {t: boundary_shares[t] * tg_boundary for t in techs}

        is_cr = is_costa_rica(c)
        is_bau = (s == "BAU")

        for y in years:
            if y <= correction_boundary:
                continue  # already set

            tg_y = total_gen.get((c, s, y), 0.0)
            if tg_y <= 0:
                for t in techs:
                    s2_shares[(c, s, t)][y] = boundary_shares[t]
                continue

            decline_exp = y - CUTOFF_YEAR

            # ── Step A: Compute rule-based shares ──

            # Fossils: 1%/yr decline
            rate = 0.0 if is_cr else FOSSIL_DECLINE_RATE
            for t in fossil_techs:
                s2_shares[(c, s, t)][y] = boundary_shares[t] * (1.0 - rate) ** max(0, decline_exp)

            # Hydro: PJ freeze
            for t in hydro_techs:
                s2_shares[(c, s, t)][y] = hydro_pj_floor[t] / tg_y

            # Locked (biomass/geo): PJ freeze
            for t in locked_techs:
                s2_shares[(c, s, t)][y] = locked_pj_floor[t] / tg_y

            # Growth (solar/wind): placeholder at boundary share (gap-fill below)
            for t in growth_techs:
                s2_shares[(c, s, t)][y] = boundary_shares.get(t, 0)

            # UNKNOWN techs: hold boundary
            for t in techs:
                if cat.get(t) == "UNKNOWN":
                    s2_shares[(c, s, t)][y] = boundary_shares.get(t, 0)

            # ── Step B: Apply mincap floors (max of rule vs committed capacity) ──
            if b1_data is not None and cum_mci is not None:
                for t in techs:
                    mf_pj = get_mincap_floor_pj(
                        t, y, boundary_pj.get(t, 0), cum_mci, b1_data, c, s)
                    mf_share = mf_pj / tg_y
                    if mf_share > s2_shares[(c, s, t)][y] + 0.0001:
                        s2_shares[(c, s, t)][y] = mf_share

            # ── Step C: Compute sums and gap-fill ──
            f_sum = sum(s2_shares[(c, s, t)][y] for t in fossil_techs)
            h_sum = sum(s2_shares[(c, s, t)][y] for t in hydro_techs)
            locked_sum = sum(s2_shares[(c, s, t)][y] for t in locked_techs)

            # Policy adjustment
            if not is_bau:
                target = policy_renewable_target(y, s, ren_at_boundary, c)
                if target is not None:
                    bau_ren = h_sum + locked_sum + sum(
                        s2_shares[(c, s, t)][y] for t in growth_techs)
                    T = max(target, bau_ren)
                    F_target = max(0.0, 1.0 - T)
                    if f_sum > 1e-9:
                        f_scale = F_target / f_sum
                        for t in fossil_techs:
                            s2_shares[(c, s, t)][y] *= f_scale
                    f_sum = F_target
                    nh_target = T - h_sum
                else:
                    nh_target = 1.0 - f_sum - h_sum
            else:
                nh_target = 1.0 - f_sum - h_sum

            nh_target = max(0.0, nh_target)

            # Growth techs absorb remainder after locked
            growth_target = max(0.0, nh_target - locked_sum)
            growth_current = sum(s2_shares[(c, s, t)][y] for t in growth_techs)
            if growth_current > 1e-9 and growth_target > 0:
                scale_G = growth_target / growth_current
                for t in growth_techs:
                    s2_shares[(c, s, t)][y] *= scale_G
            elif growth_techs and growth_target > 0:
                per = growth_target / len(growth_techs)
                for t in growth_techs:
                    s2_shares[(c, s, t)][y] = per
            else:
                for t in growth_techs:
                    s2_shares[(c, s, t)][y] = max(s2_shares[(c, s, t)][y], 0.0)

            # If locked > nh_target, scale locked down
            if locked_sum > nh_target > 0:
                factor = nh_target / locked_sum
                for t in locked_techs:
                    s2_shares[(c, s, t)][y] *= factor
                for t in growth_techs:
                    s2_shares[(c, s, t)][y] = 0.0

            # UNKNOWN techs: hold boundary
            for t in techs:
                if cat.get(t) == "UNKNOWN":
                    s2_shares[(c, s, t)][y] = boundary_shares.get(t, 0)

            # ── Renormalize if needed ──
            total = sum(s2_shares[(c, s, t)][y] for t in techs)
            if abs(total - 1.0) > 0.002:
                if total > 1e-9:
                    factor = 1.0 / total
                    for t in techs:
                        s2_shares[(c, s, t)][y] *= factor
                    audit_log.append({
                        "Country": c, "Scenario": s, "Year": y,
                        "Event": "RENORM",
                        "Raw_Sum": round(total, 6),
                    })

        # ── Phase 3: Fill any remaining gaps ──
        for t in techs:
            for y in years:
                if y not in s2_shares[(c, s, t)]:
                    s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][y]

        # ── Phase 4: Universal renormalization ──
        # For any year where shares don't sum to 1.0, renormalize.
        # At anchor years: preserve override values, scale non-overridden.
        # At other years: scale all proportionally.
        for y in years:
            total = sum(s2_shares[(c, s, t)][y] for t in techs)
            if abs(total - 1.0) < 0.001:
                continue

            if total < 1e-9:
                continue

            # Check if this year has overrides
            is_anchor = y in ov_years
            if is_anchor and cs_year_type.get((c, s, y)) == "partial":
                # Preserve overridden techs, scale rest
                ov_techs_y = {t for (t, yr) in ov if yr == y}
                ov_sum = sum(s2_shares[(c, s, t)][y] for t in ov_techs_y)
                rest_techs = [t for t in techs if t not in ov_techs_y]
                rest_sum = sum(s2_shares[(c, s, t)][y] for t in rest_techs)
                target_rest = 1.0 - ov_sum
                if rest_sum > 1e-9 and target_rest > 0:
                    scale = target_rest / rest_sum
                    for t in rest_techs:
                        s2_shares[(c, s, t)][y] *= scale
                elif rest_techs and target_rest > 0:
                    per = target_rest / len(rest_techs)
                    for t in rest_techs:
                        s2_shares[(c, s, t)][y] = per
            else:
                # Scale all proportionally
                scale = 1.0 / total
                for t in techs:
                    s2_shares[(c, s, t)][y] *= scale

            new_total = sum(s2_shares[(c, s, t)][y] for t in techs)
            if abs(new_total - 1.0) > 0.01:
                audit_log.append({
                    "Country": c, "Scenario": s, "Year": y,
                    "Event": "RENORM_PHASE4",
                    "Raw_Sum": round(total, 6),
                    "New_Sum": round(new_total, 6),
                })

    # ── Phase 5: Policy enforcement ──
    # For policy scenarios (NDCNEW/LTSNEW), enforce RE = target at every
    # post-cutoff year. RE = max(target, BAU_RE). Adjust by scaling
    # growth techs (solar/wind) and fossils.
    if ENFORCE_POLICY_EXACT:
        policy_fixes = 0
        for (c, s), techs in sorted(cs_techs.items()):
            if s == "BAU":
                continue
            curve = get_target_curve(c, s)
            if not curve:
                continue

            techs = sorted(techs)
            fossil_techs = [t for t in techs if cat.get(t) == "FOSSIL"]
            hydro_techs  = [t for t in techs if cat.get(t) == "HYDRO"]
            nh_ren_techs = [t for t in techs if cat.get(t) == "NON_HYDRO_RENEWABLE"]
            growth_techs = [t for t in nh_ren_techs if is_solar_wind(t)]
            locked_techs = [t for t in nh_ren_techs if not is_solar_wind(t)]

            # Get BAU RE for floor
            bau_re = {}
            for y in years:
                bau_re[y] = sum(s2_shares.get((c, "BAU", t), {}).get(y, 0)
                                for t in techs
                                if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))

            # Get anchor RE at cutoff
            anchor_re = sum(s2_shares.get((c, s, t), {}).get(CUTOFF_YEAR, 0)
                            for t in techs
                            if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))

            # Get anchor years for this (c, s) to skip (CSV values respected as-is)
            cs_anchor_years = set(y for (t, y) in cs_overrides.get((c, s), {}))

            for y in years:
                if y <= CUTOFF_YEAR:
                    continue
                if y in cs_anchor_years:
                    continue  # CSV anchor — respect per-tech values

                target = policy_renewable_target(y, s, anchor_re, c)
                if target is None:
                    continue

                # RE = max(target, BAU_RE)
                T = max(target, bau_re.get(y, 0))

                current_re = sum(s2_shares[(c, s, t)][y] for t in techs
                                 if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))

                if abs(current_re - T) < 0.002:
                    continue  # close enough

                # Enforce: set fossil = 1 - T, redistribute renewables
                F_target = max(0.0, 1.0 - T)
                H_sum = sum(s2_shares[(c, s, t)][y] for t in hydro_techs)
                NH_target = max(0.0, T - H_sum)

                # Scale fossils
                f_sum = sum(s2_shares[(c, s, t)][y] for t in fossil_techs)
                if f_sum > 1e-9:
                    f_scale = F_target / f_sum
                    for t in fossil_techs:
                        s2_shares[(c, s, t)][y] *= f_scale

                # Locked techs: keep as-is
                locked_sum = sum(s2_shares[(c, s, t)][y] for t in locked_techs)

                # Growth techs: absorb remainder
                growth_target = max(0.0, NH_target - locked_sum)
                growth_sum = sum(s2_shares[(c, s, t)][y] for t in growth_techs)
                if growth_sum > 1e-9 and growth_target > 0:
                    g_scale = growth_target / growth_sum
                    for t in growth_techs:
                        s2_shares[(c, s, t)][y] *= g_scale
                elif growth_techs and growth_target > 0:
                    per = growth_target / len(growth_techs)
                    for t in growth_techs:
                        s2_shares[(c, s, t)][y] = per

                # If locked > NH_target, scale locked down
                if locked_sum > NH_target > 0:
                    factor = NH_target / locked_sum
                    for t in locked_techs:
                        s2_shares[(c, s, t)][y] *= factor
                    for t in growth_techs:
                        s2_shares[(c, s, t)][y] = 0.0

                policy_fixes += 1

        if policy_fixes:
            print(f"  [Policy] Enforced RE targets at {policy_fixes} (c,s,y) tuples")

    return s2_shares


def _apply_partial(s1_data, s2_shares, c, s, techs, y, ov, cat):
    """Apply partial overrides with group renormalization."""
    overridden = {t: ov[(t, y)] for t in techs if (t, y) in ov}
    not_overridden = [t for t in techs if (t, y) not in ov]

    # Set overridden shares
    for t, sh in overridden.items():
        s2_shares[(c, s, t)][y] = sh

    # For each group, figure out how much is left
    for group_label in ["RENEWABLE", "FOSSIL"]:
        grp_techs_ov = [t for t in overridden if
                        (cat[t] in ("HYDRO", "NON_HYDRO_RENEWABLE") and group_label == "RENEWABLE") or
                        (cat[t] == "FOSSIL" and group_label == "FOSSIL")]
        grp_techs_notov = [t for t in not_overridden if
                           (cat[t] in ("HYDRO", "NON_HYDRO_RENEWABLE") and group_label == "RENEWABLE") or
                           (cat[t] == "FOSSIL" and group_label == "FOSSIL")]

        if not grp_techs_notov:
            continue

        # Original group total from Stage 1
        s1_grp = sum(s1_data[(c, s, t)]["shares"][y] for t in grp_techs_ov + grp_techs_notov)
        # New overridden portion
        ov_grp = sum(overridden.get(t, 0) for t in grp_techs_ov)
        # Remaining for non-overridden
        remaining = max(0.0, s1_grp - ov_grp)

        # Original non-overridden total
        orig_notov = sum(s1_data[(c, s, t)]["shares"][y] for t in grp_techs_notov)
        if orig_notov > 1e-9:
            scale = remaining / orig_notov
            for t in grp_techs_notov:
                s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][y] * scale
        else:
            per = remaining / len(grp_techs_notov) if grp_techs_notov else 0
            for t in grp_techs_notov:
                s2_shares[(c, s, t)][y] = per

    # UNKNOWN techs: keep Stage 1
    for t in not_overridden:
        if cat.get(t) == "UNKNOWN" and (c, s, t) not in [(c, s, tt) for tt in not_overridden if cat.get(tt) != "UNKNOWN"]:
            s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][y]


def _interpolate_year(s2_shares, c, s, techs, y, ov, ov_years, s1_data):
    """Linear interpolation between bracketing anchor years."""
    # Find bracketing anchors
    before = [yr for yr in ov_years if yr <= y]
    after  = [yr for yr in ov_years if yr >= y]

    if not before or not after:
        # Outside anchor range — use Stage 1
        for t in techs:
            s2_shares[(c, s, t)][y] = s1_data[(c, s, t)]["shares"][y]
        return

    y1 = max(before)
    y2 = min(after)

    if y1 == y2:
        for t in techs:
            s2_shares[(c, s, t)][y] = ov.get((t, y1), s1_data[(c, s, t)]["shares"][y])
        return

    frac = (y - y1) / (y2 - y1)
    for t in techs:
        v1 = ov.get((t, y1), s1_data[(c, s, t)]["shares"][y1])
        v2 = ov.get((t, y2), s1_data[(c, s, t)]["shares"][y2])
        s2_shares[(c, s, t)][y] = v1 + (v2 - v1) * frac


# =============================================================================
# LOWER / UPPER RECALCULATION
# =============================================================================

def recalc_limits(s2_shares, s1_data, total_gen, years):
    """Recalculate lower = share × total_gen, upper = max(lower×1.05, s1_upper)."""
    s2_lower = {}
    s2_upper = {}

    for key, year_shares in s2_shares.items():
        c, s, t = key
        s2_lower[key] = {}
        s2_upper[key] = {}
        s1_upper = s1_data[key]["upper"]

        for y in years:
            share = year_shares.get(y, 0.0)
            tg = total_gen.get((c, s, y), 0.0)
            lo = share * tg
            s1_up = s1_upper.get(y, DEFAULT_UPPER)

            # Upper: max of (lower × security factor, stage 1 upper)
            up = max(lo * UPPER_SECURITY_FAC, s1_up)
            # But if Stage 1 upper was 9999, keep it
            if s1_up >= 9990:
                up = DEFAULT_UPPER
            # Ensure upper ≥ lower
            if up < lo:
                up = lo * UPPER_SECURITY_FAC

            s2_lower[key][y] = round(lo, 4)
            s2_upper[key][y] = round(up, 4)

    return s2_lower, s2_upper


# =============================================================================
# WRITE STAGE 2 CONTROLLER
# =============================================================================

def write_controller(s2_shares, s2_lower, s2_upper, s1_meta, years, out_path,
                     audit_log, overrides):
    """Write Stage 2 CONTROLLER_NEW_SCENARIOS.xlsx."""

    # Build dataframes
    base_cols = ["Country", "Model", "Scenario", "Tech",
                 "Is_Renewable", "Group", "Sub_Group", "Source"]

    rows_s, rows_l, rows_u = [], [], []
    for key in sorted(s1_meta.keys()):
        m = s1_meta[key]
        m_out = {k: m[k] for k in base_cols}
        m_out["Source"] = "s2v2"

        row_s = dict(m_out)
        row_l = dict(m_out)
        row_u = dict(m_out)

        for y in years:
            row_s[y] = round(s2_shares[key].get(y, 0.0), 6)
            row_l[y] = s2_lower[key].get(y, 0.0)
            row_u[y] = s2_upper[key].get(y, DEFAULT_UPPER)

        rows_s.append(row_s)
        rows_l.append(row_l)
        rows_u.append(row_u)

    # TECH_MAP
    tech_set = sorted(set(k[2] for k in s1_meta))
    tech_map_rows = []
    for t in tech_set:
        c = classify_tech(t)
        is_ren = c in ("HYDRO", "NON_HYDRO_RENEWABLE")
        tech_map_rows.append({
            "Tech": t,
            "Is_Renewable": 1 if is_ren else (0 if c == "FOSSIL" else ""),
            "Group": "RENEWABLE" if is_ren else ("FOSSIL" if c == "FOSSIL" else "UNKNOWN"),
            "Sub_Group": c,
        })

    # README
    countries_touched = sorted(set(k[0] for k in overrides))
    readme_rows = [
        ("Purpose", "Stage 2 CONTROLLER — research-corrected shares + rebased forward projection"),
        ("Generated", datetime.now().isoformat()),
        ("Version", "s2v2 (Stage 2 Apply v2; based on Stage 1 v15)"),
        ("", ""),
        ("STAGE 2 METHOD", ""),
        ("  Corrections", f"Per-country CSVs for {', '.join(countries_touched)}"),
        ("  Historical", "Direct replacement where CSV sums to 100%; group renorm for partial"),
        ("  Freeze", f"2025-2026 = corrected {ANCHOR_YEAR} (where CSV ends at {ANCHOR_YEAR})"),
        ("  Forward", "Stage 1 rules re-applied from corrected boundary:"),
        ("    Fossil", f"{FOSSIL_DECLINE_RATE*100:.1f}%/yr decline from {CUTOFF_YEAR} (CR: 0%)"),
        ("    Hydro", "PJ freeze at corrected anchor value"),
        ("    NH-Renew", "Gap-fill (solar+wind absorb; biomass/geo locked at boundary)"),
        ("    Policy", f"NDCNEW: {RENEWABLE_TARGET_CURVE['NDCNEW']}; LTSNEW: {RENEWABLE_TARGET_CURVE['LTSNEW']}"),
        ("", ""),
        ("INVARIANTS", ""),
        ("  Shares", "Sum to 1.0 for all (country, scenario, year)"),
        ("  Lower", "share × total_gen (total_gen exogenous from Stage 1)"),
        ("  Upper", f"max(lower × {UPPER_SECURITY_FAC}, Stage 1 upper)"),
    ]

    # Write
    import openpyxl as xl
    wb = xl.Workbook()

    # README
    ws = wb.active
    ws.title = "README"
    ws.append(["Item", "Value"])
    for item, val in readme_rows:
        ws.append([item, val])

    # Helper to write a sheet from row dicts
    def write_sheet(name, rows):
        ws = wb.create_sheet(name)
        cols = base_cols + years
        ws.append(cols)
        for row in rows:
            ws.append([row.get(c, "") for c in cols])

    write_sheet("CURRENT_SHARES", rows_s)
    write_sheet("TARGET_SHARES", rows_s)  # same as current in Stage 2
    write_sheet("CURRENT_LOWER", rows_l)
    write_sheet("CURRENT_UPPER", rows_u)

    # TECH_MAP
    ws_tm = wb.create_sheet("TECH_MAP")
    ws_tm.append(["Tech", "Is_Renewable", "Group", "Sub_Group"])
    for row in tech_map_rows:
        ws_tm.append([row["Tech"], row["Is_Renewable"], row["Group"], row["Sub_Group"]])

    # AUDIT
    if audit_log:
        ws_a = wb.create_sheet("AUDIT")
        cols_a = sorted(set().union(*(d.keys() for d in audit_log)))
        ws_a.append(cols_a)
        for d in audit_log:
            ws_a.append([d.get(c, "") for c in cols_a])

    wb.save(out_path)
    print(f"\n[Wrote] {out_path}")
    print(f"  Rows: {len(rows_s)}")
    print(f"  Years: {years[0]}-{years[-1]}")


# =============================================================================
# MAIN
# =============================================================================

def main(argv=None):
    p = argparse.ArgumentParser(description="Stage 2 Apply v2")
    p.add_argument("--stage1", type=Path,
                   default=Path("_STAGE1_OUTPUT") / "CONTROLLER_NEW_SCENARIOS.xlsx")
    p.add_argument("--overrides-dir", type=Path, default=Path("_STAGE2_INPUTS"))
    p.add_argument("--out", type=Path,
                   default=Path("_STAGE2_OUTPUT") / "CONTROLLER_NEW_SCENARIOS.xlsx")
    p.add_argument("--root", type=Path, default=Path("."),
                   help="MODELS_LAC_4 root (for B1_Output_Params)")
    p.add_argument("--stage0-denom", type=Path,
                   default=Path("_STAGE0_OUTPUT") / "STAGE0_DENOMINATORS.xlsx",
                   help="Stage 0 empirical generation (real demand)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    print("=" * 70)
    print("STAGE 2 APPLY v2")
    print(f"  Stage 1: {args.stage1}")
    print(f"  Overrides: {args.overrides_dir}")
    print(f"  Root: {args.root}")
    print(f"  Output: {args.out}")
    print("=" * 70)

    # Load
    print("\n[1/6] Loading Stage 1 CONTROLLER...")
    s1_data, years, meta = load_controller(args.stage1)
    print(f"  {len(s1_data)} rows, years {years[0]}-{years[-1]}")

    print("\n[2/6] Loading overrides...")
    overrides, notes = load_overrides(args.overrides_dir)
    if not overrides:
        print("[DONE] No overrides — Stage 2 = Stage 1 (copy).")
        return

    print("\n[3/6] Loading total generation (Stage 0 empirical)...")
    if args.stage0_denom.exists():
        total_gen = load_total_gen_from_stage0(args.stage0_denom)
        print(f"  Loaded {len(total_gen)} (c,s,y) entries from {args.stage0_denom.name}")
    else:
        print(f"  [WARN] {args.stage0_denom} not found — falling back to sum(lower limits)")
        print(f"  [WARN] This underestimates demand when ceiling caps bind!")
        total_gen = derive_total_gen_fallback(s1_data, years)
    for c in sorted(set(k[0] for k in s1_data)):
        tg = total_gen.get((c, "BAU", 2024), 0)
        tg50 = total_gen.get((c, "BAU", 2050), 0)
        trend = ((tg50 - tg) / tg * 100) if tg > 0 else 0
        print(f"  {c} BAU: {tg:.1f} PJ (2024) → {tg50:.1f} PJ (2050) [{trend:+.0f}%]")

    print("\n[4/6] Loading B1 data (MinCapInvest, CF, AF)...")
    b1_data, cum_mci = load_all_b1(args.root.resolve(), years)

    print("\n[5/6] Applying corrections + forward rebase...")
    audit_log = []
    s2_shares = apply_stage2(s1_data, years, overrides, total_gen, audit_log,
                             b1_data, cum_mci)

    # Verify completeness
    missing = 0
    for key in s1_data:
        if key not in s2_shares:
            missing += 1
    if missing:
        print(f"  [WARN] {missing} (c,s,t) keys missing from Stage 2 — copying Stage 1")
        for key in s1_data:
            if key not in s2_shares:
                s2_shares[key] = dict(s1_data[key]["shares"])

    # Share sum check
    print("\n  Share sum check (sample):")
    for c in sorted(set(k[0] for k in s2_shares))[:3]:
        for s in ["BAU", "NDCNEW", "LTSNEW"]:
            for y in [2024, 2026, 2030, 2050]:
                total = sum(s2_shares.get((c, s, t), {}).get(y, 0)
                            for t in set(k[2] for k in s2_shares if k[0] == c and k[1] == s))
                flag = "OK" if abs(total - 1.0) < 0.01 else "!!!"
                if y in [2024, 2050]:
                    ren = sum(s2_shares.get((c, s, t), {}).get(y, 0)
                              for t in set(k[2] for k in s2_shares if k[0] == c and k[1] == s)
                              if classify_tech(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))
                    print(f"  {c:20s} {s:8s} {y}: sum={total:.4f} [{flag}] RE={ren:.4f}")

    if args.dry_run:
        print("\n[DRY RUN] Skipping write.")
        return

    print("\n[6/6] Recalculating limits + writing...")
    s2_lower, s2_upper = recalc_limits(s2_shares, s1_data, total_gen, years)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_controller(s2_shares, s2_lower, s2_upper, meta, years, args.out,
                     audit_log, overrides)

    print(f"\n[DONE] Stage 2 CONTROLLER at {args.out}")
    if audit_log:
        print(f"  {len(audit_log)} audit entries (renormalizations)")


if __name__ == "__main__":
    main()
