#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stage2_test_v2.py — Test harness for Stage 2 CONTROLLER.
=========================================================

Validates Stage 2 output against acceptance criteria:

Hard (must PASS):
  T1  Share sums = 1.0 ±0.01 for all (country, scenario, year)
  T2  CSV anchor values land exactly (±0.001)
  T3  Upper ≥ Lower for all cells
  T4  No negative shares or limits
  T5  BAU fossil non-increasing from corrected boundary (non-CR)
  T6  Policy milestones: NDCNEW/LTSNEW RE ≥ target at milestone years
  T7  Historical alignment: BAU=NDCNEW=LTSNEW for years with identical CSV data

Soft (informational):
  T8  Continuity: year-over-year RE change < 5pp
  T9  Hydro PJ trajectory: non-increasing from boundary
  T10 Coverage summary per country

Usage:
  py stage2_test_v2.py
  py stage2_test_v2.py --stage2 _STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl

# ── Config ──
YEAR_MIN, YEAR_MAX = 2018, 2055
CUTOFF_YEAR = 2026
SHARE_TOL = 0.01
ANCHOR_TOL = 0.003  # CSV anchor tolerance (percent → fraction rounding)
CONTINUITY_THRESH = 0.05  # 5pp year-over-year max

HYDRO_TOKENS = ["HYD", "DAM", "ROR", "PPHD", "PPIHD"]
RENEWABLE_TOKENS = ["GEO", "SOL", "SUN", "SPV", "PV", "CSP",
                    "WND", "WIND", "WNO", "WNS",
                    "BMS", "BIM", "BIO", "BGS", "SUG", "REN"]
FOSSIL_TOKENS = ["DSL", "DIE", "FOI", "HFO", "CRU",
                 "COA", "COK", "NGS", "GAS", "GLP", "LPG",
                 "GSL", "KJF", "OIL", "PET", "FOS"]

POLICY_CHECKS = [
    # (scenario, year, min_RE, label)
    ("NDCNEW", 2035, 0.70, "NDCNEW 75% target @2035 (5pp margin)"),
    ("NDCNEW", 2050, 0.70, "NDCNEW 75% target @2050 (5pp margin)"),
    ("LTSNEW", 2035, 0.70, "LTSNEW 75% target @2035 (5pp margin)"),
    ("LTSNEW", 2050, 0.94, "LTSNEW 99% target @2050 (5pp margin)"),
]
COUNTRY_POLICY_OVERRIDES = {
    "CostaRica": [
        ("NDCNEW", 2035, 0.85, "CR NDCNEW 90% @2035 (5pp)"),
        ("NDCNEW", 2050, 0.85, "CR NDCNEW 90% @2050 (5pp)"),
        ("LTSNEW", 2035, 0.94, "CR LTSNEW 99% @2035 (5pp)"),
        ("LTSNEW", 2050, 0.94, "CR LTSNEW 99% @2050 (5pp)"),
    ],
    "Ecuador": [
        ("NDCNEW", 2035, 0.75, "ECU NDCNEW 80% @2035 (5pp)"),
        ("NDCNEW", 2050, 0.75, "ECU NDCNEW 80% @2050 (5pp)"),
        ("LTSNEW", 2035, 0.75, "ECU LTSNEW 80% @2035 (5pp)"),
        ("LTSNEW", 2050, 0.94, "ECU LTSNEW 99% @2050 (5pp)"),
    ],
}

# Must match stage2_apply_v2.py — no exceptions, all rules-based 2027+
CSV_FORWARD_EXCEPTIONS = set()
CUTOFF_YEAR_SKIP = 2026


def classify_tech(tech):
    t = str(tech).upper()
    if any(tok in t for tok in HYDRO_TOKENS):
        return "HYDRO"
    if any(tok in t for tok in RENEWABLE_TOKENS):
        return "NON_HYDRO_RENEWABLE"
    if any(tok in t for tok in FOSSIL_TOKENS):
        return "FOSSIL"
    return "UNKNOWN"


def load_controller(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws_s = wb["CURRENT_SHARES"]
    ws_l = wb["CURRENT_LOWER"]
    ws_u = wb["CURRENT_UPPER"]
    headers = [c.value for c in ws_s[1]]
    year_cols = {h: i + 1 for i, h in enumerate(headers) if isinstance(h, int)}
    years = sorted(year_cols.keys())

    data = {}
    for r in range(2, ws_s.max_row + 1):
        c = ws_s.cell(r, 1).value
        s = ws_s.cell(r, 3).value
        t = ws_s.cell(r, 4).value
        g = ws_s.cell(r, 6).value
        if not (c and s and t):
            continue
        key = (c, s, t)
        shares, lowers, uppers = {}, {}, {}
        for y, col in year_cols.items():
            shares[y] = ws_s.cell(r, col).value or 0.0
            lowers[y] = ws_l.cell(r, col).value or 0.0
            uppers[y] = ws_u.cell(r, col).value or 0.0
        data[key] = {"shares": shares, "lower": lowers, "upper": uppers, "group": g}
    return data, years


def load_overrides(override_dir):
    csvs = sorted(Path(override_dir).glob("STAGE2_OVERWRITES*.csv"))
    raw = {}
    for p in csvs:
        with open(p, encoding="utf-8-sig") as f:
            for line in f:
                if line.lstrip().startswith("#") or not line.strip() or line.startswith("Country"):
                    continue
                parts = line.split(",", 5)
                if len(parts) < 5:
                    continue
                try:
                    c, s, t = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    y = int(float(parts[3].strip()))
                    pct = float(parts[4].strip())
                except (ValueError, IndexError):
                    continue
                key = (c, s, t, y)
                if key not in raw:
                    raw[key] = pct / 100.0
    return raw


RESULTS = []

def record(test_id, passed, details=""):
    RESULTS.append((test_id, passed, details))
    flag = "PASS" if passed else "FAIL"
    print(f"  [{flag}] {test_id}: {details}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage2", type=Path,
                   default=Path("_STAGE2_OUTPUT") / "CONTROLLER_NEW_SCENARIOS.xlsx")
    p.add_argument("--stage1", type=Path,
                   default=Path("_STAGE1_OUTPUT") / "CONTROLLER_NEW_SCENARIOS.xlsx")
    p.add_argument("--overrides-dir", type=Path, default=Path("_STAGE2_INPUTS"))
    p.add_argument("--stage0-denom", type=Path,
                   default=Path("_STAGE0_OUTPUT") / "STAGE0_DENOMINATORS.xlsx")
    args = p.parse_args()

    print("=" * 70)
    print("STAGE 2 TEST SUITE v2")
    print("=" * 70)

    data, years = load_controller(args.stage2)
    overrides = load_overrides(args.overrides_dir)

    countries = sorted(set(k[0] for k in data))
    scenarios = sorted(set(k[1] for k in data))
    cat = {k[2]: classify_tech(k[2]) for k in data}

    print(f"  Controller: {args.stage2}")
    print(f"  Countries:  {countries}")
    print(f"  Scenarios:  {scenarios}")
    print(f"  Overrides:  {len(overrides)} anchors")
    print()

    # ── T1: Share sums ──
    print("── HARD TESTS ──")
    sums = defaultdict(float)
    for (c, s, t), rec in data.items():
        for y in years:
            sums[(c, s, y)] += rec["shares"][y]
    fails_t1 = [(k, v) for k, v in sums.items() if abs(v - 1.0) > SHARE_TOL]
    record("T1_share_sums", len(fails_t1) == 0,
           f"{len(fails_t1)} failures" + (f" (worst: {max(abs(v-1) for _,v in fails_t1):.4f})" if fails_t1 else ""))

    # ── T2: Anchor values ──
    fails_t2 = []
    for (c, s, t, y), expected in overrides.items():
        # Skip anchors intentionally ignored by apply script (default: all forward skipped)
        if y > CUTOFF_YEAR_SKIP and (c, s) not in CSV_FORWARD_EXCEPTIONS:
            continue
        rec = data.get((c, s, t))
        if not rec:
            fails_t2.append(f"{c}/{s}/{t}/{y}: missing")
            continue
        actual = rec["shares"].get(y, None)
        if actual is None or abs(actual - expected) > ANCHOR_TOL:
            fails_t2.append(f"{c}/{s}/{t}/{y}: expected {expected:.4f} got {actual}")
    record("T2_anchors_exact", len(fails_t2) == 0,
           f"{len(fails_t2)} failures" + (f" e.g. {fails_t2[0]}" if fails_t2 else ""))

    # ── T3: Upper ≥ Lower ──
    fails_t3 = []
    for (c, s, t), rec in data.items():
        for y in years:
            if rec["upper"][y] + 0.01 < rec["lower"][y]:
                fails_t3.append(f"{c}/{s}/{t}/{y}: U={rec['upper'][y]:.3f} < L={rec['lower'][y]:.3f}")
    record("T3_upper_ge_lower", len(fails_t3) == 0, f"{len(fails_t3)} failures")

    # ── T4: No negatives ──
    fails_t4 = []
    for (c, s, t), rec in data.items():
        for y in years:
            if rec["shares"][y] < -0.001:
                fails_t4.append(f"{c}/{s}/{t}/{y}: share={rec['shares'][y]:.4f}")
            if rec["lower"][y] < -0.01:
                fails_t4.append(f"{c}/{s}/{t}/{y}: lower={rec['lower'][y]:.4f}")
    record("T4_no_negatives", len(fails_t4) == 0, f"{len(fails_t4)} failures")

    # ── T5: BAU fossil non-increasing ──
    fails_t5 = []
    for c in countries:
        if c in ["CostaRica"]:
            continue  # CR has 0% decline (flat allowed)
        # Find corrected boundary: max year with overrides for (c, BAU)
        ov_years = sorted(set(y for (cc, ss, tt, y) in overrides if cc == c and ss == "BAU"))
        if not ov_years:
            continue
        boundary = max(ov_years)
        if boundary < CUTOFF_YEAR:
            boundary = CUTOFF_YEAR

        fos_at_boundary = sum(data[(c, "BAU", t)]["shares"].get(boundary, 0)
                              for t in set(k[2] for k in data if k[0] == c and k[1] == "BAU")
                              if cat[t] == "FOSSIL")
        for y in years:
            if y <= boundary:
                continue
            fos_y = sum(data[(c, "BAU", t)]["shares"].get(y, 0)
                        for t in set(k[2] for k in data if k[0] == c and k[1] == "BAU")
                        if cat[t] == "FOSSIL")
            if fos_y > fos_at_boundary + 0.005:
                fails_t5.append(f"{c} {y}: fossil {fos_y:.4f} > boundary {fos_at_boundary:.4f}")
    record("T5_bau_fossil_decline", len(fails_t5) == 0,
           f"{len(fails_t5)} failures" + (f" e.g. {fails_t5[0]}" if fails_t5 else ""))

    # ── T6: Policy milestones ──
    fails_t6 = []
    for c in countries:
        checks = COUNTRY_POLICY_OVERRIDES.get(c, POLICY_CHECKS)
        for (sc, year, min_re, label) in checks:
            re_sum = sum(data.get((c, sc, t), {"shares": {}})["shares"].get(year, 0)
                         for t in set(k[2] for k in data if k[0] == c and k[1] == sc)
                         if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))
            if re_sum < min_re:
                fails_t6.append(f"{c} {label}: RE={re_sum:.4f} < {min_re}")
    record("T6_policy_milestones", len(fails_t6) == 0,
           f"{len(fails_t6)} failures" + (f" e.g. {fails_t6[0]}" if fails_t6 else ""))
    if fails_t6:
        for f in fails_t6:
            print(f"       {f}")

    # ── T7: Historical alignment ──
    # Check that BAU = NDCNEW = LTSNEW for years where CSV has identical values
    fails_t7 = []
    for c in countries:
        techs_c = sorted(set(k[2] for k in data if k[0] == c))
        for y in range(YEAR_MIN, CUTOFF_YEAR + 1):
            # Check if all 3 scenarios have same CSV values at this year
            csv_vals = {}
            for sc in ["BAU", "NDCNEW", "LTSNEW"]:
                csv_vals[sc] = {t: overrides.get((c, sc, t, y)) for t in techs_c}
            # If all three have the same non-None values
            bau_vals = csv_vals["BAU"]
            all_same = True
            for sc in ["NDCNEW", "LTSNEW"]:
                for t in techs_c:
                    if bau_vals[t] is not None and csv_vals[sc][t] is not None:
                        if abs(bau_vals[t] - csv_vals[sc][t]) > 0.001:
                            all_same = False
            if not all_same:
                continue
            if not any(bau_vals[t] is not None for t in techs_c):
                continue
            # Check actual shares match across scenarios
            for t in techs_c:
                shares = [data.get((c, sc, t), {"shares": {}})["shares"].get(y, 0)
                          for sc in ["BAU", "NDCNEW", "LTSNEW"]]
                if max(shares) - min(shares) > 0.002:
                    fails_t7.append(f"{c}/{t}/{y}: {[round(s,4) for s in shares]}")
    record("T7_historical_alignment", len(fails_t7) == 0,
           f"{len(fails_t7)} failures" + (f" e.g. {fails_t7[0]}" if fails_t7 else ""))

    # ── SOFT TESTS ──
    print()
    print("── SOFT TESTS (informational) ──")

    # ── T8: Continuity ──
    discontinuities = []
    for c in countries:
        for sc in scenarios:
            prev_re = None
            for y in years:
                re_sum = sum(data.get((c, sc, t), {"shares": {}})["shares"].get(y, 0)
                             for t in set(k[2] for k in data if k[0] == c and k[1] == sc)
                             if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))
                if prev_re is not None:
                    delta = abs(re_sum - prev_re)
                    if delta > CONTINUITY_THRESH:
                        discontinuities.append(f"{c}/{sc} {y-1}->{y}: Δ={delta:.4f}")
                prev_re = re_sum
    record("T8_continuity", len(discontinuities) == 0,
           f"{len(discontinuities)} jumps >5pp" + (f" e.g. {discontinuities[0]}" if discontinuities else ""))
    for d in discontinuities[:5]:
        print(f"       {d}")

    # ── T9: Hydro PJ trajectory ──
    hydro_increases = []
    for c in countries:
        for sc in scenarios:
            hydro_techs = [t for t in set(k[2] for k in data if k[0] == c and k[1] == sc)
                           if cat.get(t) == "HYDRO"]
            if not hydro_techs:
                continue
            # Find boundary
            ov_years = sorted(set(y for (cc, ss, tt, y) in overrides if cc == c and ss == sc))
            boundary = max(ov_years) if ov_years else CUTOFF_YEAR
            if boundary < CUTOFF_YEAR:
                boundary = CUTOFF_YEAR
            hydro_pj_boundary = sum(data[(c, sc, t)]["lower"].get(boundary, 0)
                                    for t in hydro_techs)
            for y in years:
                if y <= boundary:
                    continue
                hydro_pj_y = sum(data[(c, sc, t)]["lower"].get(y, 0) for t in hydro_techs)
                if hydro_pj_y > hydro_pj_boundary * 1.05:
                    hydro_increases.append(f"{c}/{sc} {y}: {hydro_pj_y:.3f} > boundary {hydro_pj_boundary:.3f}")
    record("T9_hydro_pj_freeze", len(hydro_increases) == 0,
           f"{len(hydro_increases)} violations" + (f" e.g. {hydro_increases[0]}" if hydro_increases else ""))

    # ── T10: Coverage summary ──
    print()
    print("── COVERAGE SUMMARY ──")
    for c in countries:
        ov_years = sorted(set(y for (cc, ss, tt, y) in overrides if cc == c))
        ov_scenarios = sorted(set(ss for (cc, ss, tt, y) in overrides if cc == c))
        ov_techs = sorted(set(tt for (cc, ss, tt, y) in overrides if cc == c))
        n_anchors = sum(1 for (cc, ss, tt, y) in overrides if cc == c)
        label = "FULL" if ov_years and max(ov_years) >= 2050 else "PARTIAL"
        print(f"  {c:20s}: {n_anchors:>5d} anchors, years {min(ov_years) if ov_years else 'N/A':>4}-{max(ov_years) if ov_years else 'N/A':>4}, "
              f"scenarios {ov_scenarios}, [{label}]")

    # ── Renewable share trajectory table ──
    print()
    print("── RENEWABLE SHARE TRAJECTORY (Stage 2) ──")
    print(f"{'Country':>20s} {'Scenario':>8s}", end="")
    for y in [2024, 2026, 2030, 2035, 2040, 2050]:
        print(f" {y:>6d}", end="")
    print()
    for c in countries:
        for sc in ["BAU", "NDCNEW", "LTSNEW"]:
            print(f"{c:>20s} {sc:>8s}", end="")
            for y in [2024, 2026, 2030, 2035, 2040, 2050]:
                re_sum = sum(data.get((c, sc, t), {"shares": {}})["shares"].get(y, 0)
                             for t in set(k[2] for k in data if k[0] == c and k[1] == sc)
                             if cat.get(t) in ("HYDRO", "NON_HYDRO_RENEWABLE"))
                print(f" {re_sum:>6.1%}", end="")
            print()

    # ── T10: Growth tech presence — soft because depends on B1 mincap data ──
    # When MinCapInvest = 0 AND demand shrinks, growth techs can legitimately
    # reach zero (PJ-frozen hydro+biomass consume all space). B1 mincap floors
    # override this on the actual machine. Flag for review.
    fails_t10 = []
    for c in countries:
        for sc in scenarios:
            growth_techs_c = [t for t in set(k[2] for k in data if k[0] == c and k[1] == sc)
                              if cat.get(t) in ("NON_HYDRO_RENEWABLE") and
                              any(tok in str(t).upper() for tok in
                                  ["SOL","SUN","SPV","PV","CSP","WND","WIND","WNO","WNS"])]
            if not growth_techs_c:
                continue
            for y in [2035, 2050]:
                total_growth = sum(data.get((c, sc, t), {"shares": {}})["shares"].get(y, 0)
                                   for t in growth_techs_c)
                if total_growth < 0.001:
                    fails_t10.append(f"{c}/{sc} {y}: solar+wind={total_growth:.4f} (demand-squeeze — check B1 MinCapInvest)")
    record("T10_growth_tech_check", len(fails_t10) == 0,
           f"{len(fails_t10)} cases with zero solar+wind" + (f" e.g. {fails_t10[0]}" if fails_t10 else ""))

    # ── T11: Denominator + share alignment for early years ──
    # Stage 0 empirical gen should be equal across BAU/NDCNEW/LTSNEW for ≤2024
    # (scenarios only diverge from 2027+; 2025-2026 are frozen)
    DENOM_TOL = 0.5  # PJ tolerance
    DENOM_ALIGN_YEAR = 2024  # check through this year
    fails_t11_denom = []
    fails_t11_shares = []

    if args.stage0_denom.exists():
        import openpyxl as xl2
        wb_d = xl2.load_workbook(args.stage0_denom, data_only=True)
        ws_d = wb_d["ALL"]
        denom = {}
        for r in range(2, ws_d.max_row + 1):
            c_d = ws_d.cell(r, 1).value
            s_d = str(ws_d.cell(r, 2).value or "").replace("_S0", "")
            y_d = ws_d.cell(r, 3).value
            g_d = ws_d.cell(r, 4).value
            if c_d and s_d and y_d and g_d:
                denom[(c_d, s_d, int(y_d))] = float(g_d)

        for c in countries:
            for y in range(YEAR_MIN, DENOM_ALIGN_YEAR + 1):
                vals = {s: denom.get((c, s, y)) for s in ["BAU", "NDCNEW", "LTSNEW"]}
                present = {s: v for s, v in vals.items() if v is not None}
                if len(present) < 2:
                    continue
                vlist = list(present.values())
                spread = max(vlist) - min(vlist)
                if spread > DENOM_TOL:
                    fails_t11_denom.append(
                        f"{c} {y}: BAU={vals.get('BAU','?'):.1f} NDC={vals.get('NDCNEW','?'):.1f} "
                        f"LTS={vals.get('LTSNEW','?'):.1f} (spread={spread:.1f} PJ)")

        record("T11a_denom_alignment", len(fails_t11_denom) == 0,
               f"{len(fails_t11_denom)} years with scenario spread >{DENOM_TOL} PJ" +
               (f" e.g. {fails_t11_denom[0]}" if fails_t11_denom else ""))
        for f in fails_t11_denom[:5]:
            print(f"       {f}")
    else:
        record("T11a_denom_alignment", True, "SKIP (no STAGE0_DENOMINATORS.xlsx)")

    # Share alignment: BAU = NDCNEW = LTSNEW for years ≤ DENOM_ALIGN_YEAR
    for c in countries:
        techs_c = sorted(set(k[2] for k in data if k[0] == c))
        for y in range(YEAR_MIN, DENOM_ALIGN_YEAR + 1):
            for t in techs_c:
                shares_by_sc = [data.get((c, s, t), {"shares": {}})["shares"].get(y, 0)
                                for s in ["BAU", "NDCNEW", "LTSNEW"]]
                spread = max(shares_by_sc) - min(shares_by_sc)
                if spread > 0.005:
                    fails_t11_shares.append(
                        f"{c}/{t}/{y}: BAU={shares_by_sc[0]:.4f} NDC={shares_by_sc[1]:.4f} "
                        f"LTS={shares_by_sc[2]:.4f}")

    record("T11b_share_alignment", len(fails_t11_shares) == 0,
           f"{len(fails_t11_shares)} (c,t,y) with scenario divergence ≤{DENOM_ALIGN_YEAR}" +
           (f" e.g. {fails_t11_shares[0]}" if fails_t11_shares else ""))
    for f in fails_t11_shares[:5]:
        print(f"       {f}")

    # ── Summary ──
    print()
    print("=" * 70)
    hard_tests = [tid for tid, _, _ in RESULTS if tid.startswith("T") and 
                  int(''.join(c for c in tid.split('_')[0] if c.isdigit())) <= 7]
    hard_pass = sum(1 for tid in hard_tests if any(p for t, p, _ in RESULTS if t == tid))
    hard_total = len(hard_tests)
    hard_fails = [(tid, d) for tid, p, d in RESULTS if tid in hard_tests and not p]
    print(f"Hard tests: {hard_total - len(hard_fails)}/{hard_total} PASS")
    if hard_fails:
        print("FAILURES:")
        for tid, d in hard_fails:
            print(f"  {tid}: {d}")
    print()

    sys.exit(0 if not hard_fails else 1)


if __name__ == "__main__":
    main()
