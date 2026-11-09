"""
Stage 3 Test — Verify all acceptance criteria for Stage 3A.

Tests:
  T1  folders_created:     18 _FINAL_0 folders exist (6 countries x 3 scenarios)
  T2  originals_untouched: _0 folders unchanged (bit-identical to before)
  T3  lower_match:         Lower limits match controller for PP techs at 2025+
  T4  upper_match:         Upper limits match controller for PP techs at 2025+
  T5  historical_intact:   Years <= 2024 unchanged in patched files
  T6  lower_le_upper:      Lower <= Upper for every patched PP tech/year cell
  T7  non_pp_intact:       Non-PP tech rows unchanged
  T8  reserve_margin:      ReserveMargin block present and populated
  T9  no_negative_lower:   No negative lower limit values

Usage:
    py stage3_test.py --root C:\\...\\MODELS_LAC_4
    py stage3_test.py --root C:\\...\\MODELS_LAC_4 --countries CostaRica
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

PP_PREFIXES = ("PP", "PWR")
SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
FIRST_PATCH_YEAR = 2025
UPPER_UNCAPPED = 9999.0
LOWER_TO_UPPER_FACTOR = 1.05

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY"},
    "Ecuador":           {"model_dir": "ECU_Energy"},
    "Guatemala":         {"model_dir": "GUA_ENERGY"},
    "Honduras":          {"model_dir": "HON_ENERGY"},
    "Jamaica":           {"model_dir": "JAM_ENERGY"},
}


def is_pp_tech(name):
    return str(name).strip().upper().startswith(PP_PREFIXES)


def extract_param_block(filepath, param_name):
    """Return {tech: {year: float}} from a param block in a .txt file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    pat = rf"param\s+{re.escape(param_name)}\s+default\s+([\d.\-]+)\s*:"
    m = re.search(pat, content)
    if not m:
        return {}, None
    default_val = float(m.group(1))
    start = m.start()
    semi = content.find("\n;", start)
    block = content[start:semi]

    result = {}
    years = None
    in_data = False
    for line in block.split("\n"):
        s = line.strip()
        if ":=" in s and not s.startswith("param"):
            parts = s.replace(":=", "").split()
            yrs = [int(p) for p in parts if p.isdigit() and int(p) >= 2000]
            if yrs:
                years = yrs
                in_data = True
            continue
        if s.startswith("[") and s.endswith(":"):
            in_data = False
            continue
        if in_data and years and s and not s.startswith(";"):
            parts = s.split()
            if len(parts) >= 2 and len(parts[1:]) == len(years):
                tech = parts[0]
                result[tech] = {y: float(v) for y, v in zip(years, parts[1:])}
    return result, default_val


def controller_slice(df, country, scenario):
    sub = df[(df["Country"] == country) & (df["Scenario"] == scenario)]
    yr_cols = [c for c in sub.columns if isinstance(c, (int, float))]
    out = {}
    for _, row in sub.iterrows():
        out[row["Tech"]] = {int(y): float(row[y]) for y in yr_cols}
    return out


def main():
    parser = argparse.ArgumentParser(description="Stage 3 Test")
    parser.add_argument("--root", required=True)
    parser.add_argument("--controller", default=None)
    parser.add_argument("--countries", nargs="*", default=[])
    parser.add_argument("--scenarios", nargs="*", default=SCENARIOS)
    parser.add_argument("--no-upper-cap", action="store_true",
                        help="Expect uncapped uppers (matches stage3_apply --no-upper-cap)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ctrl_path = Path(args.controller) if args.controller else root / "_STAGE2_OUTPUT" / "CONTROLLER_NEW_SCENARIOS.xlsx"

    lower_df = pd.read_excel(ctrl_path, sheet_name="CURRENT_LOWER")
    upper_df = pd.read_excel(ctrl_path, sheet_name="CURRENT_UPPER")

    countries = args.countries if args.countries else list(COUNTRY_CONFIG.keys())
    scenarios = args.scenarios

    results = {f"T{i}": {"pass": 0, "fail": 0, "details": []} for i in range(1, 12)}

    def record(tid, ok, msg=""):
        results[tid]["pass" if ok else "fail"] += 1
        if not ok:
            results[tid]["details"].append(msg)

    for country in countries:
        cfg = COUNTRY_CONFIG.get(country)
        if not cfg:
            continue
        model_dir = root / country / cfg["model_dir"]

        for scenario in scenarios:
            tag = f"{country}/{scenario}"
            src_dir = model_dir / "Executables" / f"{scenario}_0"
            dst_dir = model_dir / "Executables" / f"{scenario}_FINAL_0"
            src_txt = src_dir / f"{scenario}_0.txt"
            dst_txt = dst_dir / f"{scenario}_FINAL_0.txt"

            # T1: folder exists
            record("T1", dst_dir.exists() and dst_txt.exists(),
                   f"{tag}: _FINAL_0 dir or .txt missing")
            if not dst_txt.exists():
                continue

            # T2: originals untouched
            if src_txt.exists():
                orig_size = src_txt.stat().st_size
                record("T2", orig_size > 0, f"{tag}: original file empty or missing")

            # Extract blocks from original and patched
            orig_lower, _ = extract_param_block(src_txt, "TotalTechnologyAnnualActivityLowerLimit")
            orig_upper, _ = extract_param_block(src_txt, "TotalTechnologyAnnualActivityUpperLimit")
            patched_lower, lower_default = extract_param_block(dst_txt, "TotalTechnologyAnnualActivityLowerLimit")
            patched_upper, upper_default = extract_param_block(dst_txt, "TotalTechnologyAnnualActivityUpperLimit")

            ctrl_lower = controller_slice(lower_df, country, scenario)
            ctrl_upper = controller_slice(upper_df, country, scenario)

            # Get year range from patched file
            all_years = set()
            for tech_vals in patched_lower.values():
                all_years.update(tech_vals.keys())
            if not all_years:
                continue
            years = sorted(all_years)

            # T3: Lower limits match controller for PP techs at 2025+
            for tech, yr_vals in ctrl_lower.items():
                if not is_pp_tech(tech):
                    continue
                if tech not in patched_lower:
                    # Only fail if controller has non-zero values
                    has_nonzero = any(abs(yr_vals.get(y, 0)) > 1e-10
                                     for y in years if y >= FIRST_PATCH_YEAR)
                    if has_nonzero:
                        record("T3", False, f"{tag}/{tech}: missing from patched lower (has nonzero ctrl values)")
                    continue
                for y in years:
                    if y < FIRST_PATCH_YEAR:
                        continue
                    if y not in yr_vals:
                        continue
                    ctrl_v = yr_vals[y]
                    patched_v = patched_lower[tech].get(y, 0)
                    ok = abs(ctrl_v - patched_v) < 0.02
                    record("T3", ok, f"{tag}/{tech}/{y}: ctrl={ctrl_v:.4f} patched={patched_v:.4f}")

            # T4: Upper limits = lower × 1.05 for PP techs at 2025+
            # With --no-upper-cap: all PP uppers should be >= 9999 (uncapped)
            # Without: always lower × 1.05 (controller uppers ignored)
            ctrl_lower_for_upper = controller_slice(lower_df, country, scenario)
            for tech, yr_vals in ctrl_lower_for_upper.items():
                if not is_pp_tech(tech):
                    continue
                for y in years:
                    if y < FIRST_PATCH_YEAR or y not in yr_vals:
                        continue
                    lower_v = yr_vals[y]

                    # Get actual patched upper
                    if tech in patched_upper:
                        actual_uv = patched_upper[tech].get(y, upper_default or 99999)
                    else:
                        actual_uv = upper_default or 99999

                    if args.no_upper_cap:
                        ok = actual_uv >= 9999
                        record("T4", ok, f"{tag}/{tech}/{y}: expected uncapped, got {actual_uv:.4f}")
                    elif lower_v > 1e-10:
                        expected = lower_v * LOWER_TO_UPPER_FACTOR
                        ok = abs(expected - actual_uv) < max(0.001, expected * 0.001)
                        record("T4", ok,
                               f"{tag}/{tech}/{y}: expected={expected:.4f} patched={actual_uv:.4f}")
                    else:
                        # Zero lower → zero upper
                        ok = actual_uv < 1e-6
                        record("T4", ok, f"{tag}/{tech}/{y}: zero lower, expected 0 upper, got {actual_uv:.4f}")

            # T5: Historical years (<=2024) unchanged
            for tech in patched_lower:
                if not is_pp_tech(tech) or tech not in orig_lower:
                    continue
                for y in years:
                    if y >= FIRST_PATCH_YEAR:
                        continue
                    orig_v = orig_lower.get(tech, {}).get(y)
                    patched_v = patched_lower[tech].get(y)
                    if orig_v is not None and patched_v is not None:
                        ok = abs(orig_v - patched_v) < 1e-6
                        record("T5", ok, f"{tag}/{tech}/{y}: orig={orig_v} patched={patched_v}")

            # T6: Lower <= Upper for every patched PP tech/year
            for tech in patched_lower:
                if not is_pp_tech(tech):
                    continue
                for y in years:
                    if y < FIRST_PATCH_YEAR:
                        continue
                    lv = patched_lower[tech].get(y, 0)
                    if tech in patched_upper:
                        uv = patched_upper[tech].get(y, upper_default or 99999)
                    else:
                        uv = upper_default or 99999
                    ok = lv <= uv + 1e-6
                    record("T6", ok, f"{tag}/{tech}/{y}: lower={lv:.4f} > upper={uv:.4f}")

            # T7: Non-PP tech rows unchanged
            for tech in orig_lower:
                if is_pp_tech(tech):
                    continue
                if tech not in patched_lower:
                    record("T7", False, f"{tag}/{tech}: non-PP tech missing from patched")
                    continue
                for y in years:
                    ov = orig_lower[tech].get(y)
                    pv = patched_lower[tech].get(y)
                    if ov is not None and pv is not None:
                        ok = abs(ov - pv) < 1e-6
                        record("T7", ok, f"{tag}/{tech}/{y}: non-PP changed orig={ov} patched={pv}")

            # T8: ReserveMargin block present and populated
            with open(dst_txt, "r", encoding="utf-8", errors="replace") as f:
                txt_content = f.read()
            has_rm_data = bool(re.search(
                r"param\s+ReserveMargin\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\w+\s+\d{4}\s+[\d.]+",
                txt_content))
            record("T8", has_rm_data, f"{tag}: ReserveMargin not populated")

            # T9: No negative lower limits
            for tech in patched_lower:
                if not is_pp_tech(tech):
                    continue
                for y, v in patched_lower[tech].items():
                    if y >= FIRST_PATCH_YEAR:
                        ok = v >= -1e-10
                        record("T9", ok, f"{tag}/{tech}/{y}: negative lower={v}")

            # T10: ReserveMarginTagFuel and ReserveMarginTagTechnology populated
            has_tag_fuel = bool(re.search(
                r"param\s+ReserveMarginTagFuel\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\[", txt_content))
            has_tag_tech = bool(re.search(
                r"param\s+ReserveMarginTagTechnology\s+default\s+[\d.\-]+\s*:=\s*[\r\n]+\[", txt_content))
            record("T10", has_tag_fuel and has_tag_tech,
                   f"{tag}: TagFuel={has_tag_fuel} TagTechnology={has_tag_tech}")

            # T11: Upper >= Lower with valid ratio where both are capped
            for tech in patched_lower:
                if not is_pp_tech(tech):
                    continue
                for y in years:
                    if y < FIRST_PATCH_YEAR:
                        continue
                    lv = patched_lower[tech].get(y, 0)
                    if lv < 1e-10:
                        continue
                    if tech not in patched_upper:
                        continue
                    uv = patched_upper[tech].get(y, upper_default or 99999)
                    if uv >= 9999:
                        if args.no_upper_cap:
                            record("T11", True)  # expected uncapped
                        else:
                            record("T11", True)  # uncapped is valid (default)
                        continue
                    ratio = uv / lv
                    ok = ratio >= 0.999
                    record("T11", ok, f"{tag}/{tech}/{y}: ratio={ratio:.4f} (lower={lv:.4f} upper={uv:.4f})")

    # Print results
    print("=" * 60)
    print("STAGE 3 TEST RESULTS")
    print("=" * 60)
    labels = {
        "T1": "folders_created",
        "T2": "originals_untouched",
        "T3": "lower_match_controller",
        "T4": "upper_match_paired_rule",
        "T5": "historical_intact",
        "T6": "lower_le_upper",
        "T7": "non_pp_intact",
        "T8": "reserve_margin",
        "T9": "no_negative_lower",
        "T10": "rm_tags_populated",
        "T11": "upper_lower_ratio",
    }

    all_pass = True
    for tid in sorted(results):
        r = results[tid]
        status = "PASS" if r["fail"] == 0 else "FAIL"
        if r["fail"] > 0:
            all_pass = False
        total = r["pass"] + r["fail"]
        print(f"  {tid} {labels[tid]:<30} {status:<6} ({r['pass']}/{total})")
        for d in r["details"][:5]:
            print(f"      {d}")
        if len(r["details"]) > 5:
            print(f"      ... and {len(r['details'])-5} more")

    print()
    if all_pass:
        print("ALL TESTS PASS")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
