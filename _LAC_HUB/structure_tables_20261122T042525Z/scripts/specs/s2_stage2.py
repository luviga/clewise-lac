# Phase B edits: stage2_apply_v2.py
F = "stage2_apply_v2.py"
CR = 'LT.controller_list("own_rule_country_names", "2")[0]'
EDITS = [
    (F, """import pandas as pd

# =============================================================================
# CONFIG — mirrors Stage 1 v15/v16
# =============================================================================
CUTOFF_YEAR         = 2026
ANCHOR_YEAR         = 2024
PLATEAU_YEARS       = [2025, 2026]
FOSSIL_DECLINE_RATE = 0.01       # 1%/yr from 2027
UPPER_SECURITY_FAC  = 1.05
DEFAULT_UPPER       = 9999.0
YEAR_MIN, YEAR_MAX  = 2018, 2055""", """import pandas as pd

import lac_tables as LT

# =============================================================================
# CONFIG — mirrors Stage 1 v15/v16 (values and names from the tables read by lac_tables.py)
# =============================================================================
CUTOFF_YEAR         = LT.controller("cutoff_year", "2")
ANCHOR_YEAR         = LT.controller("anchor_year")
PLATEAU_YEARS       = LT.controller_list("plateau_years", "2")
FOSSIL_DECLINE_RATE = LT.controller("fossil_decline_rate", "2")       # per year after the cutoff year
UPPER_SECURITY_FAC  = LT.controller("upper_security_factor", "2")
DEFAULT_UPPER       = LT.controller("upper_limit_sentinel", "2")
YEAR_MIN, YEAR_MAX  = LT.controller("year_min", "2"), LT.controller("year_max", "2")"""),
    (F, """# Country model directories (same as Stage 1)
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
                     "WND", "WIND", "WNO", "WNS"]""", """# Country model directories (same as Stage 1)
COUNTRY_MODEL_DIR = LT.country_map("model_dir")

# Policy targets (same table as Stage 1: inputs/scenarios/scenario_values.csv)
RENEWABLE_TARGET_CURVE = LT.scenario_values("renewable_share")
COUNTRY_TARGET_OVERRIDES = LT.scenario_value_overrides("renewable_share")
TARGET_HOLD_YEAR = LT.controller("target_hold_year", "2")

COSTA_RICA_NAMES = LT.controller_list("own_rule_country_names", "2")

# Tech classifier tokens (same as Stage 1: config/scenarios/technology_types.csv)
HYDRO_TOKENS     = LT.techs("hydro_token")
RENEWABLE_TOKENS = LT.techs("renewable_token")
FOSSIL_TOKENS    = LT.techs("fossil_token")
SOLAR_WIND_TOKENS = LT.techs("solar_wind_token")"""),
    (F, '    all_scenarios = ["BAU", "NDCNEW", "LTSNEW"]', '    all_scenarios = LT.scenarios()'),
    (F, 'cs_year_type[(c, s, y)] = "full" if abs(s_sum - 1.0) < 0.02 else "partial"',
     'cs_year_type[(c, s, y)] = "full" if abs(s_sum - 1.0) < LT.controller("full_override_tolerance", "2") else "partial"'),
    (F, '        is_bau = (s == "BAU")', '        is_bau = (s == LT.scenario("base"))'),
    (F, 'if mf_share > s2_shares[(c, s, t)][y] + 0.0001:', 'if mf_share > s2_shares[(c, s, t)][y] + LT.controller("mincap_share_tolerance", "2"):'),
    (F, '1e-9', 'LT.controller("zero_tolerance")', 8),
    (F, '            if abs(total - 1.0) > 0.002:', '            if abs(total - 1.0) > LT.controller("renorm_tolerance", "2"):'),
    (F, '"Raw_Sum": round(total, 6),', '"Raw_Sum": round(total, LT.controller("audit_digits", "2")),', 2),
    (F, '"New_Sum": round(new_total, 6),', '"New_Sum": round(new_total, LT.controller("audit_digits", "2")),'),
    (F, '            if abs(new_total - 1.0) > 0.01:', '            if abs(new_total - 1.0) > LT.controller("renorm_check_tolerance", "2"):'),
    (F, '            if s == "BAU":', '            if s == LT.scenario("base"):'),
    (F, 'bau_re[y] = sum(s2_shares.get((c, "BAU", t), {}).get(y, 0)', 'bau_re[y] = sum(s2_shares.get((c, LT.scenario("base"), t), {}).get(y, 0)'),
    (F, '                if abs(current_re - T) < 0.002:', '                if abs(current_re - T) < LT.controller("target_match_tolerance", "2"):'),
    (F, '            if s1_up >= 9990:', '            if s1_up >= LT.controller("sentinel_detect_threshold", "2"):'),
    (F, '            s2_lower[key][y] = round(lo, 4)\n            s2_upper[key][y] = round(up, 4)',
     '            s2_lower[key][y] = round(lo, LT.controller("limit_digits", "2"))\n            s2_upper[key][y] = round(up, LT.controller("limit_digits", "2"))'),
    (F, 'row_s[y] = round(s2_shares[key].get(y, 0.0), 6)', 'row_s[y] = round(s2_shares[key].get(y, 0.0), LT.controller("share_digits", "2"))'),
    (F, '("    Fossil", f"{FOSSIL_DECLINE_RATE*100:.1f}%/yr decline from {CUTOFF_YEAR} (CR: 0%)"),',
     '''("    Fossil", f"{FOSSIL_DECLINE_RATE*100:.1f}%/yr decline from {CUTOFF_YEAR} ({LT.country_value(''' + CR + ''', 'code')}: 0%)"),'''),
    (F, '''("    Policy", f"NDCNEW: {RENEWABLE_TARGET_CURVE['NDCNEW']}; LTSNEW: {RENEWABLE_TARGET_CURVE['LTSNEW']}"),''',
     '''("    Policy", f"{LT.scenario('ndc')}: {RENEWABLE_TARGET_CURVE[LT.scenario('ndc')]}; {LT.scenario('lts')}: {RENEWABLE_TARGET_CURVE[LT.scenario('lts')]}"),'''),
    (F, '        tg = total_gen.get((c, "BAU", 2024), 0)\n        tg50 = total_gen.get((c, "BAU", 2050), 0)',
     '        tg = total_gen.get((c, LT.scenario("base"), LT.controller("trend_start_year", "2")), 0)\n        tg50 = total_gen.get((c, LT.scenario("base"), LT.controller("trend_end_year", "2")), 0)'),
    (F, '        for s in ["BAU", "NDCNEW", "LTSNEW"]:\n            for y in [2024, 2026, 2030, 2050]:',
     '        for s in LT.scenarios():\n            for y in LT.controller_list("check_years", "2"):'),
    (F, '                flag = "OK" if abs(total - 1.0) < 0.01 else "!!!"\n                if y in [2024, 2050]:',
     '                flag = "OK" if abs(total - 1.0) < LT.controller("share_check_tolerance", "2") else "!!!"\n                if y in LT.controller_list("check_renewable_years", "2"):'),
]
