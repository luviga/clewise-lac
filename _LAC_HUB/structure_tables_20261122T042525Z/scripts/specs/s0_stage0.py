# Phase B edits: Stage 0 scripts and the two cleaners. Literals -> reads through lac_tables (LT).
IMP_OLD = "from pathlib import Path\n"
CC_COMMENT = "# country -> model folder inside the country folder (config/preparation/Config_country_codes.yaml)\n"

EDITS = [
    # ---------------------------------------------------------------- stage0_clean.py
    ("stage0_clean.py", """from pathlib import Path

MODELS_LAC_ROOT""", """from pathlib import Path

import lac_tables as LT

MODELS_LAC_ROOT"""),
    ("stage0_clean.py", """COUNTRY_CONFIG = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}""", CC_COMMENT + 'COUNTRY_CONFIG = LT.country_map("model_dir")'),
    # ---------------------------------------------------------------- stage2_post_clean.py
    ("stage2_post_clean.py", """from pathlib import Path

COUNTRY_CONFIG = {
    "CostaRica": "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador": "ECU_Energy",
    "Guatemala": "GUA_ENERGY",
    "Honduras": "HON_ENERGY",
    "Jamaica": "JAM_ENERGY",
}""", """from pathlib import Path

import lac_tables as LT

""" + CC_COMMENT + 'COUNTRY_CONFIG = LT.country_map("model_dir")'),
    # ---------------------------------------------------------------- stage0_run.py
    ("stage0_run.py", """import pandas as pd

# =============================================================================
# CONFIGURATION""", """import pandas as pd

import lac_tables as LT

# =============================================================================
# CONFIGURATION (values and names from the tables read by lac_tables.py)"""),
    ("stage0_run.py", 'SOURCE_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]', 'SOURCE_SCENARIOS = LT.scenarios()'),
    ("stage0_run.py", "ANCHOR_YEAR = 2024\nPLATEAU_END = 2024  # 2025+", 'ANCHOR_YEAR = LT.controller("anchor_year")\nPLATEAU_END = LT.controller("plateau_end_year", "0")  # 2025+'),
    ("stage0_run.py", 'PP_PREFIXES = ("PP", "PWR")  # Must match', 'PP_PREFIXES = tuple(LT.techs("power_plant_prefix"))  # Must match'),
    ("stage0_run.py", """BYPASS_TECHS = {
    "PPWNDD", "PPPVD", "PPPVDS",           # distributed gen → E3ELE
    "PPHD", "PPIHD",                         # isolated/distributed hydro → E3ELE
    "PPCRU", "PPDDSL", "PPDFOI", "PPDGSL",  # autoproducers → E3ELE
    "PPDGLP", "PPDNGS", "PPRDSL", "PPRNGS", # refinery/distributed → E3ELE
    "PPILPG", "PPIBIM",                      # isolated → E3ELE
}""", """# Distributed gen, isolated/distributed hydro, autoproducers, refinery/distributed and isolated plants
# (all route to E3ELE): config/scenarios/technology_types.csv, group stage0_bypass.
BYPASS_TECHS = set(LT.techs("stage0_bypass"))"""),
    ("stage0_run.py", "UPPER_LIMIT_SENTINEL = 9999.0", 'UPPER_LIMIT_SENTINEL = LT.controller("upper_limit_sentinel", "0")'),
    ("stage0_run.py", """# Confirmed from Codex scan — model dir relative to country root,
# and path to OSeMOSYS_Model.txt relative to country root.
COUNTRY_CONFIG = {
    "CostaRica": {
        "model_dir": "CR_ENERGY/t1_confection",
        "osemosys":  "CR_ENERGY/t1_confection/OSeMOSYS_Model.txt",
    },
    "DominicanRepublic": {
        "model_dir": "RD_ENERGY",
        "osemosys":  "RD_ENERGY/OSeMOSYS_Model.txt",
    },
    "Ecuador": {
        "model_dir": "ECU_Energy",
        "osemosys":  "ECU_Energy/OSeMOSYS_Model.txt",
    },
    "Guatemala": {
        "model_dir": "GUA_ENERGY",
        "osemosys":  "GUA_ENERGY/OSeMOSYS_Model.txt",
    },
    "Honduras": {
        "model_dir": "HON_ENERGY",
        "osemosys":  "HON_ENERGY/OSeMOSYS_Model.txt",
    },
    "Jamaica": {
        "model_dir": "JAM_ENERGY",
        "osemosys":  "JAM_ENERGY/OSeMOSYS_Model.txt",
    },
}""", """# Model dir relative to country root, and path to OSeMOSYS_Model.txt relative to country root
# (config/preparation/Config_country_codes.yaml).
COUNTRY_CONFIG = LT.country_table("model_dir", "osemosys")"""),
    ("stage0_run.py", "            if years and years[0] >= 2000:", '            if years and years[0] >= LT.controller("year_header_min"):', 2),
    ("stage0_run.py", "                if years and years[0] >= 2000:", '                if years and years[0] >= LT.controller("year_header_min"):'),
    ("stage0_run.py", "        anchor_val = anchor_values.get(tech, 0.01)", '        anchor_val = anchor_values.get(tech, LT.controller("bypass_floor_pj", "0"))'),
    ("stage0_run.py", "            anchor_val = 0.01  # Must be", '            anchor_val = LT.controller("bypass_floor_pj", "0")  # Must be'),
    ("stage0_run.py", '"Relaxed": round(anchor_val, 6),', '"Relaxed": round(anchor_val, LT.controller("change_log_digits", "0")),'),
    ("stage0_run.py", '"Delta": round(anchor_val, 6),', '"Delta": round(anchor_val, LT.controller("change_log_digits", "0")),'),
    ("stage0_run.py", "if abs(new_val - old_val) > 1e-10:", 'if abs(new_val - old_val) > LT.controller("change_tolerance"):'),
    ("stage0_run.py", '"Original": round(old_val, 6),', '"Original": round(old_val, LT.controller("change_log_digits", "0")),'),
    ("stage0_run.py", '"Relaxed": round(new_val, 6),', '"Relaxed": round(new_val, LT.controller("change_log_digits", "0")),'),
    ("stage0_run.py", '"Delta": round(new_val - old_val, 6),', '"Delta": round(new_val - old_val, LT.controller("change_log_digits", "0")),'),
    ("stage0_run.py", "                        bypass_ideal_caps[tech] = 0.01", '                        bypass_ideal_caps[tech] = LT.controller("bypass_floor_pj", "0")'),
    ("stage0_run.py", "ideal = bypass_ideal_caps.get(tech, 0.01)", 'ideal = bypass_ideal_caps.get(tech, LT.controller("bypass_floor_pj", "0"))'),
    ("stage0_run.py", "if ul_anchors[tech] > ideal * 2:", 'if ul_anchors[tech] > ideal * LT.controller("bypass_oversize_ratio", "0"):'),
    # ---------------------------------------------------------------- stage0_collect_outputs.py
    ("stage0_collect_outputs.py", """import numpy as np

MODELS_LAC_ROOT""", """import numpy as np

import lac_tables as LT

MODELS_LAC_ROOT"""),
    ("stage0_collect_outputs.py", """SOURCE_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
PP_PREFIXES = ("PP", "PWR")  # Must match Stage 1's PWR_PREFIXES
ELEC_FUEL_PATTERNS = ["ELE"]
TD_PATTERNS = ["ELE_TRN","ELE_TRANS","ELETTRN","TDELE","TD_ELE","TRANS_ELE",
               "ELE_DTR","ELE_DIST","ELEDTR","ELEDIST","TD_DIST","DIST_ELE"]

COUNTRY_CONFIG = {
    "CostaRica":         {"model_dir": "CR_ENERGY/t1_confection"},
    "DominicanRepublic": {"model_dir": "RD_ENERGY"},
    "Ecuador":           {"model_dir": "ECU_Energy"},
    "Guatemala":         {"model_dir": "GUA_ENERGY"},
    "Honduras":          {"model_dir": "HON_ENERGY"},
    "Jamaica":           {"model_dir": "JAM_ENERGY"},
}""", """SOURCE_SCENARIOS = LT.scenarios()
PP_PREFIXES = tuple(LT.techs("power_plant_prefix"))  # Must match Stage 1's PWR_PREFIXES
ELEC_FUEL_PATTERNS = LT.fuels("electricity_fuel_token")
TD_PATTERNS = LT.techs("transmission_distribution_token")

COUNTRY_CONFIG = LT.country_table("model_dir")"""),
    ("stage0_collect_outputs.py", '"Min_PJ":round(emp_gen.min(),2),"Max_PJ":round(emp_gen.max(),2)})',
     '"Min_PJ":round(emp_gen.min(),LT.controller("status_digits_pj", "0")),"Max_PJ":round(emp_gen.max(),LT.controller("status_digits_pj", "0"))})'),
    ("stage0_collect_outputs.py", "                if yr > 2024:", '                if yr > LT.controller("history_end_year"):'),
    ("stage0_collect_outputs.py", "if gen > 0.0001:", 'if gen > LT.controller("min_share_generation_pj", "0"):'),
    ("stage0_collect_outputs.py", '"Gen_PJ": round(gen, 4),', '"Gen_PJ": round(gen, LT.controller("digits_pj", "0")),'),
    ("stage0_collect_outputs.py", '"Total_Gen_PJ": round(total, 4),', '"Total_Gen_PJ": round(total, LT.controller("digits_pj", "0")),'),
    ("stage0_collect_outputs.py", '"Share_Pct": round(gen / total * 100, 2),', '"Share_Pct": round(gen / total * 100, LT.controller("digits_pct", "0")),'),
    ("stage0_collect_outputs.py", '"Empirical_Gen_PJ":round(empirical,4),', '"Empirical_Gen_PJ":round(empirical,LT.controller("digits_pj", "0")),'),
    ("stage0_collect_outputs.py", '"Analytical_RequiredGen_PJ":round(analytical,4),', '"Analytical_RequiredGen_PJ":round(analytical,LT.controller("digits_pj", "0")),'),
    ("stage0_collect_outputs.py", '"Delta_PJ":round(delta,4),', '"Delta_PJ":round(delta,LT.controller("digits_pj", "0")),'),
    ("stage0_collect_outputs.py", '"Actual_PJ":round(a,4),"Floor_PJ":round(f,4),', '"Actual_PJ":round(a,LT.controller("digits_pj", "0")),"Floor_PJ":round(f,LT.controller("digits_pj", "0")),'),
    ("stage0_collect_outputs.py", '"Headroom_PJ":round(a-f,4)})', '"Headroom_PJ":round(a-f,LT.controller("digits_pj", "0"))})'),
    ("stage0_collect_outputs.py", 'big=dd[abs(dd["Delta_Pct"])>5]', 'big=dd[abs(dd["Delta_Pct"])>LT.controller("report_delta_pct", "0")]'),
    ("stage0_collect_outputs.py", "bad = sums[(sums - 100.0).abs() > 0.1]", 'bad = sums[(sums - 100.0).abs() > LT.controller("share_sum_tolerance_pct", "0")]'),
    # ---------------------------------------------------------------- stage0_capacity_check.py
    ("stage0_capacity_check.py", """import numpy as np

MODELS_LAC_ROOT""", """import numpy as np

import lac_tables as LT

MODELS_LAC_ROOT"""),
    ("stage0_capacity_check.py", """SOURCE_SCENARIOS = ["BAU", "NDCNEW", "LTSNEW"]
PP_PREFIXES = ("PP", "PWR")

COUNTRY_CONFIG = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}""", """SOURCE_SCENARIOS = LT.scenarios()
PP_PREFIXES = tuple(LT.techs("power_plant_prefix"))

""" + CC_COMMENT + 'COUNTRY_CONFIG = LT.country_map("model_dir")'),
    ("stage0_capacity_check.py", '"LowerLimit_PJ": round(lower, 4),', '"LowerLimit_PJ": round(lower, LT.controller("digits_pj", "0")),'),
    ("stage0_capacity_check.py", '"ProdPotential_PJ": round(prod_potential, 4),', '"ProdPotential_PJ": round(prod_potential, LT.controller("digits_pj", "0")),'),
    ("stage0_capacity_check.py", '"Actual_PJ": round(actual, 4),', '"Actual_PJ": round(actual, LT.controller("digits_pj", "0")),'),
    ("stage0_capacity_check.py", '"Total_Gen_PJ": round(total_gen, 4),', '"Total_Gen_PJ": round(total_gen, LT.controller("digits_pj", "0")),'),
    ("stage0_capacity_check.py", '"Share_A_LowerLimit_Pct": round(share_a, 2),', '"Share_A_LowerLimit_Pct": round(share_a, LT.controller("digits_pct", "0")),'),
    ("stage0_capacity_check.py", '"Share_B_Ceiling_Pct": round(share_b, 2),', '"Share_B_Ceiling_Pct": round(share_b, LT.controller("digits_pct", "0")),'),
    ("stage0_capacity_check.py", '"Share_C_Actual_Pct": round(share_c, 2),', '"Share_C_Actual_Pct": round(share_c, LT.controller("digits_pct", "0")),'),
    # ---------------------------------------------------------------- stage0_recommend_shares.py
    ("stage0_recommend_shares.py", """import numpy as np

MODELS_LAC_ROOT""", """import numpy as np

import lac_tables as LT

MODELS_LAC_ROOT"""),
    ("stage0_recommend_shares.py", """MAX_YEAR = 2024  # Only historical years

# Classification thresholds
CLOSE_THRESHOLD = 0.10    # C is "close to" A if |C-A|/max(C,A) < 10%
UNDERUTIL_THRESHOLD = 0.50  # C is "much smaller than" B if C/B < 50%

COUNTRY_CONFIG = {
    "CostaRica":         "CR_ENERGY/t1_confection",
    "DominicanRepublic": "RD_ENERGY",
    "Ecuador":           "ECU_Energy",
    "Guatemala":         "GUA_ENERGY",
    "Honduras":          "HON_ENERGY",
    "Jamaica":           "JAM_ENERGY",
}

PP_PREFIXES = ("PP", "PWR")""", """MAX_YEAR = LT.controller("history_end_year")  # Only historical years

# Classification thresholds
CLOSE_THRESHOLD = LT.controller("close_threshold", "0")    # C is "close to" A if |C-A|/max(C,A) < threshold
UNDERUTIL_THRESHOLD = LT.controller("underutil_threshold", "0")  # C is "much smaller than" B if C/B < threshold

""" + CC_COMMENT + """COUNTRY_CONFIG = LT.country_map("model_dir")

PP_PREFIXES = tuple(LT.techs("power_plant_prefix"))"""),
    ("stage0_recommend_shares.py", '(df_ceil["Scenario"] == "BAU") &', '(df_ceil["Scenario"] == LT.scenario("base")) &'),
    ("stage0_recommend_shares.py", 'df_cf = read_b1_csv(b1_dir, "BAU", "CapacityFactor.csv")', 'df_cf = read_b1_csv(b1_dir, LT.scenario("base"), "CapacityFactor.csv")'),
    ("stage0_recommend_shares.py", 'df_af = read_b1_csv(b1_dir, "BAU", "AvailabilityFactor.csv")', 'df_af = read_b1_csv(b1_dir, LT.scenario("base"), "AvailabilityFactor.csv")'),
    ("stage0_recommend_shares.py", 'accum_cap = get_cumulative_capacity(b1_dir, "BAU")', 'accum_cap = get_cumulative_capacity(b1_dir, LT.scenario("base"))'),
    ("stage0_recommend_shares.py", '"b_full": round(b_full, 2), "c": c,', '"b_full": round(b_full, LT.controller("digits_pct", "0")), "c": c,'),
    ("stage0_recommend_shares.py", '"full_potential_pj": round(full_potential, 4),', '"full_potential_pj": round(full_potential, LT.controller("digits_pj", "0")),'),
    ("stage0_recommend_shares.py", '"accum_cap_gw": round(ac, 4),', '"accum_cap_gw": round(ac, LT.controller("digits_pj", "0")),'),
    ("stage0_recommend_shares.py", "denom = max(c, a, 0.01)", 'denom = max(c, a, LT.controller("min_share_pct", "0"))'),
    ("stage0_recommend_shares.py", "elif b > c and b > a and b > 0.01:", 'elif b > c and b > a and b > LT.controller("min_share_pct", "0"):'),
    ("stage0_recommend_shares.py", "if filler_c_sum > 0.01 and filler_techs:", 'if filler_c_sum > LT.controller("min_share_pct", "0") and filler_techs:'),
    ("stage0_recommend_shares.py", 't["d"] = round(t["c"] * scale, 2)', 't["d"] = round(t["c"] * scale, LT.controller("digits_pct", "0"))'),
    ("stage0_recommend_shares.py", 't["d"] = round(per, 2)', 't["d"] = round(per, LT.controller("digits_pct", "0"))'),
    ("stage0_recommend_shares.py", "if abs(total_d - 100.0) > 0.1:", 'if abs(total_d - 100.0) > LT.controller("share_sum_tolerance_pct", "0"):'),
    ("stage0_recommend_shares.py", 't["d"] = round(t["d"] * scale, 2)', 't["d"] = round(t["d"] * scale, LT.controller("digits_pct", "0"))'),
    ("stage0_recommend_shares.py", "if e_raw_sum > 0.01:", 'if e_raw_sum > LT.controller("min_share_pct", "0"):'),
    ("stage0_recommend_shares.py", 't["e"] = round(t["e_raw"] * e_scale, 2)', 't["e"] = round(t["e_raw"] * e_scale, LT.controller("digits_pct", "0"))'),
    ("stage0_recommend_shares.py", '"Share_D_Recommended_Pct": round(t["d"], 2),', '"Share_D_Recommended_Pct": round(t["d"], LT.controller("digits_pct", "0")),'),
    ("stage0_recommend_shares.py", '"Share_E_Proportional_Pct": round(t["e"], 2),', '"Share_E_Proportional_Pct": round(t["e"], LT.controller("digits_pct", "0")),'),
    ("stage0_recommend_shares.py", '"Total_Gen_PJ": round(total_gen, 4),', '"Total_Gen_PJ": round(total_gen, LT.controller("digits_pj", "0")),'),
    ("stage0_recommend_shares.py", 'd2024 = df[df["Year"] == 2024]', 'd2024 = df[df["Year"] == LT.controller("history_end_year")]'),
]
