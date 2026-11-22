# Phase B edits: stage3_apply.py and stage3_results.py
A = "stage3_apply.py"
R = "stage3_results.py"
UNCAP = 'LT.controller("uncapped_value", "3")'
EDITS = [
    (A, """import pandas as pd

# =====================================================================
# CONFIGURATION
# =====================================================================

SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
PP_PREFIXES = ("PP", "PWR")
FIRST_PATCH_YEAR = 2025
RESERVE_MARGIN = 1.15
UPPER_UNCAPPED = 9999.0  # controller sentinel for "no cap"
LOWER_TO_UPPER_FACTOR = 1.05  # tight cap = lower * 1.05 when controller says uncapped but lower > 0

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY"},
    "Ecuador":           {"model_dir": "ECU_Energy"},
    "Guatemala":         {"model_dir": "GUA_ENERGY"},
    "Honduras":          {"model_dir": "HON_ENERGY"},
    "Jamaica":           {"model_dir": "JAM_ENERGY"},
}""", """import pandas as pd

import lac_tables as LT

# =====================================================================
# CONFIGURATION (values and names from the tables read by lac_tables.py)
# =====================================================================

SCENARIOS = LT.scenarios()
PP_PREFIXES = tuple(LT.techs("power_plant_prefix"))
FIRST_PATCH_YEAR = LT.controller("first_patch_year", "3")
RESERVE_MARGIN = LT.controller("reserve_margin", "3")
UPPER_UNCAPPED = LT.controller("upper_limit_sentinel", "3")  # controller sentinel for "no cap"
LOWER_TO_UPPER_FACTOR = LT.controller("lower_to_upper_factor", "3")  # tight cap = lower * factor when controller says uncapped but lower > 0

COUNTRY_CONFIG = LT.country_table("model_dir")"""),
    (A, "            if 2000 <= y <= 2100:", '            if LT.controller("year_header_min") <= y <= LT.controller("year_header_max", "3"):'),
    (A, "1e-10", 'LT.controller("change_tolerance")', 5),
    (A, "new_v = eff if has_cap else 99999.0", "new_v = eff if has_cap else " + UNCAP),
    (A, "                                new_v = 99999.0", "                                new_v = " + UNCAP),
    (A, "txt_years = list(range(2021, 2051))", 'txt_years = list(range(LT.controller("fallback_years_start", "3"), LT.controller("fallback_years_stop", "3")))', 2),
    (A, "{y: 99999.0 for y in txt_years if y >= FIRST_PATCH_YEAR}", "{y: " + UNCAP + " for y in txt_years if y >= FIRST_PATCH_YEAR}", 2),
    (A, "default_val=99999.0, uncap_sentinel=None", "default_val=" + UNCAP + ", uncap_sentinel=None", 3),
    (A, "zero_lower_upper = 0.0 if not skip_orphans else 99999.0", "zero_lower_upper = 0.0 if not skip_orphans else " + UNCAP),
    (A, 'if up.startswith("E1") and "ELE" in up:', 'if up.startswith("E1") and LT.fuel("electricity_fuel_token") in up:'),
    # ---------------------------------------------------------------- stage3_results.py
    (R, """import pandas as pd

# =====================================================================
# CONFIGURATION
# =====================================================================

SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection", "region": "CR"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY",              "region": "RD"},
    "Ecuador":           {"model_dir": "ECU_Energy",             "region": "ECU"},
    "Guatemala":         {"model_dir": "GUA_ENERGY",             "region": "GUA"},
    "Honduras":          {"model_dir": "HON_ENERGY",             "region": "HON"},
    "Jamaica":           {"model_dir": "JAM_ENERGY",             "region": "JAM"},
}""", """import pandas as pd

import lac_tables as LT

# =====================================================================
# CONFIGURATION (values and names from the tables read by lac_tables.py)
# =====================================================================

SCENARIOS = LT.scenarios()

COUNTRY_CONFIG = LT.country_table("model_dir", region="code")"""),
    (R, "if abs(value) > 1e-10:", 'if abs(value) > LT.controller("change_tolerance"):'),
    (R, 'act[act["Technology"].str.upper().str.startswith(("PP", "PWR"))]', 'act[act["Technology"].str.upper().str.startswith(tuple(LT.techs("power_plant_prefix")))]', 2),
    (R, "max_yr = solver_max_year.get((c, s), 2050)", 'max_yr = solver_max_year.get((c, s), LT.controller("max_year_default", "3"))'),
    (R, "if yi < 2025 or yi > max_yr:", 'if yi < LT.controller("first_patch_year", "3") or yi > max_yr:'),
    (R, "if abs_dev > 0.01:", 'if abs_dev > LT.controller("share_fail_deviation", "3"):', 2),
    (R, "elif abs_dev > 0.003:", 'elif abs_dev > LT.controller("share_warn_deviation", "3"):', 2),
    (R, "for year in [2025, 2030, 2035, 2040, 2050]:", 'for year in LT.controller_list("emission_print_years", "3"):'),
    (R, """            RE_TARGETS = {
                "NDCNEW": {2035: 0.75, 2050: 0.75},
                "LTSNEW": {2035: 0.75, 2050: 0.99},
            }
            RE_TOLERANCE = 0.02  # 2pp tolerance""", """            # (inputs/scenarios/scenario_values.csv, lever renewable_share, general rows)
            RE_TARGETS = LT.scenario_values("renewable_share")
            RE_TOLERANCE = LT.controller("re_target_tolerance", "3")  # share points"""),
    (R, 'bau = merged[(merged["Country"] == country) & (merged["Scenario"] == "BAU")]', 'bau = merged[(merged["Country"] == country) & (merged["Scenario"] == LT.scenario("base"))]'),
    (R, "                for y in [2025, 2030, 2035, 2050]:", '                for y in LT.controller_list("re_print_years", "3"):'),
]
