# Phase B edits: stage1_share_analyzer_v16.py
F = "stage1_share_analyzer_v16.py"
CR = 'LT.controller_list("own_rule_country_names", "1")[0]'
EDITS = [
    (F, """import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================""", """import pandas as pd

import lac_tables as LT

# =============================================================================
# CONFIG (values and names from the tables read by lac_tables.py)
# ============================================================================="""),
    (F, """# Per-country share column selection (from Stage 0 analysis)
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
                    "GSL", "KJF", "OIL", "PET", "FOS"]""", """# Per-country share column selection (from Stage 0 analysis)
SHARE_COLUMN = LT.controller_by_country("share_column", "1")

# Country model directories
COUNTRY_MODEL_DIR = LT.country_map("model_dir")

# Scenarios (config/scenarios/scenario_catalogue.csv)
BAU_SCENARIO      = LT.scenario("base")
POLICY_SCENARIOS  = LT.scenarios("policy")
ALL_SCENARIOS     = [BAU_SCENARIO] + POLICY_SCENARIOS

# BAU rule parameters (config/scenarios/rules/stage_controller.csv)
ANCHOR_YEAR         = LT.controller("anchor_year")
CUTOFF_YEAR         = LT.controller("cutoff_year", "1")
PLATEAU_YEARS       = LT.controller_list("plateau_years", "1")
FOSSIL_DECLINE_RATE = LT.controller("fossil_decline_rate", "1")     # per year after the cutoff year
HYDRO_DECLINE_RATE  = 0.0      # deprecated in v15: hydro uses PJ freeze instead
CAU                 = 31.536   # CapacityToActivityUnit (PJ/GW/yr)
PP_PREFIXES         = tuple(LT.techs("power_plant_prefix"))

# Policy renewable target curves (inputs/scenarios/scenario_values.csv, lever renewable_share)
RENEWABLE_TARGET_CURVE = LT.scenario_values("renewable_share")
COUNTRY_TARGET_OVERRIDES = LT.scenario_value_overrides("renewable_share")
TARGET_HOLD_YEAR = LT.controller("target_hold_year", "1")

# Upper limits
DEFAULT_UPPER_LIMIT     = LT.controller("upper_limit_sentinel", "1")
UPPER_SECURITY_FACTOR   = LT.controller("upper_security_factor", "1")   # upper ≥ lower × this

# Names of the country with its own rule set (Costa Rica)
COSTA_RICA_NAMES = LT.controller_list("own_rule_country_names", "1")

# Policy tech allocation: solar+wind tokens grow; biomass/biogas/geo locked at BAU
# (config/scenarios/technology_types.csv)
SOLAR_WIND_TOKENS = LT.techs("solar_wind_token")

# Tech classifier tokens
HYDRO_TOKENS     = LT.techs("hydro_token")
RENEWABLE_TOKENS = LT.techs("renewable_token")
FOSSIL_TOKENS    = LT.techs("fossil_token")"""),
    (F, "        if nh_anchor_sum > 1e-9 and nh_target > 0:", '        if nh_anchor_sum > LT.controller("zero_tolerance") and nh_target > 0:'),
    (F, "        if total > 1.001:", '        if total > LT.controller("renorm_trigger", "1"):'),
    (F, "            if scalable_sum > 1e-9:", '            if scalable_sum > LT.controller("zero_tolerance"):'),
    (F, '"Event": "RENORM", "Raw_Sum": round(total, 4),', '"Event": "RENORM", "Raw_Sum": round(total, LT.controller("audit_digits", "1")),'),
    (F, '"Adjusted_Sum": round(sum(bau_shares.get((t, year), 0) for t in all_techs), 4),', '"Adjusted_Sum": round(sum(bau_shares.get((t, year), 0) for t in all_techs), LT.controller("audit_digits", "1")),'),
    (F, "if growth_bau_sum > 1e-9 and growth_target > 0:", 'if growth_bau_sum > LT.controller("zero_tolerance") and growth_target > 0:'),
    (F, "if F_BAU > 1e-9:", 'if F_BAU > LT.controller("zero_tolerance"):'),
    (F, "if pol_total > 1.001:", 'if pol_total > LT.controller("renorm_trigger", "1"):'),
    (F, "                if scalable_sum > 1e-9:", '                if scalable_sum > LT.controller("zero_tolerance"):'),
    (F, '''                "Target_Renewable": round(target_renew, 4),
                "BAU_Renewable": round(BAU_renewable, 4),
                "H_BAU": round(H_BAU, 4),
                "H_Policy": round(H_policy, 4),
                "N_BAU": round(N_BAU, 4),
                "F_BAU": round(F_BAU, 4),
                "T_Final": round(T, 4),
                "N_Target": round(N_target, 4),
                "F_Target": round(F_target, 4),
                "Locked_Sum": round(locked_sum, 4),
                "Growth_Target": round(max(0.0, N_target - locked_sum), 4),''', '''                "Target_Renewable": round(target_renew, LT.controller("audit_digits", "1")),
                f"{LT.scenario('base')}_Renewable": round(BAU_renewable, LT.controller("audit_digits", "1")),
                f"H_{LT.scenario('base')}": round(H_BAU, LT.controller("audit_digits", "1")),
                "H_Policy": round(H_policy, LT.controller("audit_digits", "1")),
                f"N_{LT.scenario('base')}": round(N_BAU, LT.controller("audit_digits", "1")),
                f"F_{LT.scenario('base')}": round(F_BAU, LT.controller("audit_digits", "1")),
                "T_Final": round(T, LT.controller("audit_digits", "1")),
                "N_Target": round(N_target, LT.controller("audit_digits", "1")),
                "F_Target": round(F_target, LT.controller("audit_digits", "1")),
                "Locked_Sum": round(locked_sum, LT.controller("audit_digits", "1")),
                "Growth_Target": round(max(0.0, N_target - locked_sum), LT.controller("audit_digits", "1")),'''),
    (F, '''                row[f"Share_{year}"] = round(share, 6)
                row[f"Lower_{year}"] = round(lower, 4)
                row[f"Upper_{year}"] = round(upper, 4)''', '''                row[f"Share_{year}"] = round(share, LT.controller("share_digits", "1"))
                row[f"Lower_{year}"] = round(lower, LT.controller("limit_digits", "1"))
                row[f"Upper_{year}"] = round(upper, LT.controller("limit_digits", "1"))'''),
    (F, "        for year in [ANCHOR_YEAR, 2030, 2040, 2050]:", '        for year in [ANCHOR_YEAR, *LT.controller_list("summary_years", "1")]:'),
    (F, '{"Item": "BAU RULE", "Value": ""},', '''{"Item": f"{LT.scenario('base')} RULE", "Value": ""},'''),
    (F, '{"Item": "  Costa Rica", "Value": "same rules as other countries (BAU); managed per COUNTRY_TARGET_OVERRIDES (policy)"},',
     '''{"Item": f"  {LT.country_value(''' + CR + ''', 'display_name')}", "Value": f"same rules as other countries ({LT.scenario('base')}); managed per COUNTRY_TARGET_OVERRIDES (policy)"},'''),
    (F, '''        {"Item": "  NDCNEW", "Value": str(RENEWABLE_TARGET_CURVE.get("NDCNEW", {}))},
        {"Item": "  LTSNEW", "Value": str(RENEWABLE_TARGET_CURVE.get("LTSNEW", {}))},
        {"Item": "  CR overrides", "Value": str(COUNTRY_TARGET_OVERRIDES.get("CostaRica", {}))},''', '''        {"Item": f"  {LT.scenario('ndc')}", "Value": str(RENEWABLE_TARGET_CURVE.get(LT.scenario('ndc'), {}))},
        {"Item": f"  {LT.scenario('lts')}", "Value": str(RENEWABLE_TARGET_CURVE.get(LT.scenario('lts'), {}))},
        {"Item": f"  {LT.country_value(''' + CR + ''', 'code')} overrides", "Value": str(COUNTRY_TARGET_OVERRIDES.get(''' + CR + ''', {}))},'''),
]
