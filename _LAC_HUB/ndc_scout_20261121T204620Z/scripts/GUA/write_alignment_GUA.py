"""Write alignment_GUA.csv and parts/proposals_GUA.csv (LAC_NDC_SCOUT, Guatemala).

Usage (from the job folder): python -I scripts/GUA/write_alignment_GUA.py
Model values come from model_levers_GUA.csv (line numbers given in model_reference) and, for
2032 and cumulative values, from _STAGE3_RESULTS/stage3_results.xlsx as computed by
scripts/GUA/model_numbers.py (printed output recorded in parts/notes_GUA.md).
"""
import csv
import os

import pandas as pd

JOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
lev = pd.read_csv(os.path.join(JOB, "model_levers_GUA.csv"))
lev.index = lev.index + 2  # file line numbers (header is line 1)


def v(line, col):
    return float(lev.loc[line, col])


def red(line, scen, year):
    b = v(line, f"BAU_{year}")
    s = v(line, f"{scen}_{year}")
    return 100 * (1 - s / b)


def r(x, n=4):
    return round(x, n)


def ratio(m, t):
    return "" if (m == "" or t in ("", 0)) else round(float(m) / float(t), 3)


AH = ["target_id", "source_id", "page", "target_description", "target_value", "target_unit", "target_year", "model_quantity",
      "model_reference", "NDCNEW_value", "LTSNEW_value", "model_unit", "ratio_NDCNEW", "ratio_LTSNEW", "status",
      "sector_model_folder", "note"]
A = []
EM = 186  # CO2e_sources line
EMN = ("Model covers energy and transport only. Label CO2e_sources (fossil fuel combustion counted at the DIST_* "
       "technologies, Mt CO2e assumed from emission factors of about 0.074 per PJ of diesel) is used; the overlapping label CO2e "
       "(line 185) gives 20.4 percent in 2035. Labels Accidents, Congestion and Health are not greenhouse gases and are never added.")


def add(tid, sid, page, desc, tval, tunit, tyear, mq, mref, n, l, munit, status, folder="", note="", rn=None, rl=None):
    if rn is None:
        rn = ratio(n, tval) if status not in ("not compared", "in documents, not in the model", "in the model, not in the documents") else ""
    if rl is None:
        rl = ratio(l, tval) if status not in ("not compared", "in documents, not in the model", "in the model, not in the documents") else ""
    A.append([tid, sid, page, desc, tval, tunit, tyear, mq, mref, n, l, munit, rn, rl, status, folder, note])


# Economy-wide and energy emissions
add("GUA-T001", "GUA-01", "p.13;p.25;p.28;p.131", "Economy-wide reduction of net GHG emissions against BAU in 2035", "23.7", "percent", "2035",
    "energy-system emission reduction against the model BAU in 2035", f"model_levers_GUA.csv line {EM} (solved, emissions by label, CO2e_sources): 1 - scenario/BAU",
    r(red(EM, "NDCNEW", 2035)), r(red(EM, "LTSNEW", 2035)), "percent", "same direction, different size", "",
    EMN + " The NDC target is economy-wide and net of LULUCF; 88.4 percent of its 2035 reduction is forest (GUA-T031). The model BAU is not the NDC BAU.")
add("GUA-T005", "GUA-01", "p.26;p.27;p.29", "Emission reduction of the energy and transport measures in 2035", "1184.9", "kt CO2eq", "2035",
    "energy-system emission reduction against the model BAU in 2035", f"model_levers_GUA.csv line {EM}, BAU minus scenario, Mt converted to kt",
    r((v(EM, "BAU_2035") - v(EM, "NDCNEW_2035")) * 1000, 1), r((v(EM, "BAU_2035") - v(EM, "LTSNEW_2035")) * 1000, 1), "kt CO2e",
    "same direction, different size", "", EMN + " The NDC energy reduction comes from 1,000 MW of renewables and E10 only.")
add("GUA-T006", "GUA-01", "p.29", "Energy sector (including transport) net emissions in the mitigation scenario in 2035", "27320.2", "kt CO2eq", "2035",
    "energy-system emissions in 2035", f"model_levers_GUA.csv line {EM}, Mt converted to kt",
    r(v(EM, "NDCNEW_2035") * 1000, 1), r(v(EM, "LTSNEW_2035") * 1000, 1), "kt CO2e", "same direction, different size", "",
    "Level comparison. The NDC energy BAU for 2035 is 28,505.1 kt (p.29); the model BAU is 43,097.1 kt (ratio 1.51). "
    "Model 2025 policy emissions exceed BAU because IMP_ELE is 0 in the policy scenarios (known unintended difference).")
add("GUA-T007", "GUA-01", "p.26;p.27", "Cumulative reduction 2026 to 2035 of the energy and transport measures", "7211.6", "kt CO2eq", "2035",
    "cumulative energy-system emission reduction 2026 to 2035", "_STAGE3_RESULTS/stage3_results.xlsx sheet AnnualEmissions, Guatemala, CO2e_sources, sum of BAU minus scenario 2026-2035 (scripts/GUA/model_numbers.py)",
    40632.0, 36464.0, "kt CO2e", "same direction, different size", "", "Mt converted to kt.")
# Power
add("GUA-T008", "GUA-01", "p.40;p.41;p.102", "At least 80 percent of electricity from renewable sources by 2035", "80", "percent", "2035",
    "renewable share of generation 2035", "model_levers_GUA.csv line 149 (renewable types PPBGS PPBIM PPGEO PPHDAM PPHROR PPPVD PPPVDS PPPVT PPPVT2 PPPVTS PPWNDON)",
    r(100 * v(149, "NDCNEW_2035")), r(100 * v(149, "LTSNEW_2035")), "percent", "matches", "",
    "Within 10 percent by the rule, but the model sits 5 points below a stated floor ('al menos'). The solved share comes from the Stage 1 target curve "
    "(stage1_share_analyzer_v16.py line 98, 0.75 for NDCNEW in 2035 and 2050), not from B1_Scenario_Config.xlsx.")
cap = [150, 151, 155, 156, 157, 159, 160, 161, 162, 163, 164]


def capsum(scen, y):
    return sum(0 if pd.isna(lev.loc[i, f"{scen}_{y}"]) else float(lev.loc[i, f"{scen}_{y}"]) for i in cap)


add("GUA-T009", "GUA-01", "p.40;p.102;p.28", "At least 1,000 MW of additional renewable capacity from 2025 to 2035", "1000", "MW", "2035",
    "increase of renewable installed capacity 2025 to 2035", "model_levers_GUA.csv lines 150, 151, 155, 156, 157, 159 to 164 (installed capacity, renewable types)",
    r((capsum("NDCNEW", 2035) - capsum("NDCNEW", 2025)) * 1000, 1), r((capsum("LTSNEW", 2035) - capsum("LTSNEW", 2025)) * 1000, 1), "MW",
    "same direction, different size", "", "Capacity in GW converted to MW. The target is a floor. The model BAU alone adds 1,514 MW in the same period.")
add("GUA-T042", "GUA-02", "p.72;p.77", "80 percent clean electricity generation by 2030 (NDC 2021, superseded)", "80", "percent", "2030",
    "renewable share of generation 2030", "model_levers_GUA.csv line 149",
    r(100 * v(149, "NDCNEW_2030")), r(100 * v(149, "LTSNEW_2030")), "percent", "same direction, different size", "",
    "NDC 2021 counts natural gas as clean (p.71); with solved gas generation added the model reaches 73.5 percent in NDCNEW 2030. The INDC (GUA-T055) states 80 percent renewable in 2030 as well.")
add("GUA-T072", "GUA-07", "p.68;p.70", "Renewable share of electricity generation 64 percent in 2032 (Plan Nacional de Energia; cited by the LTS, GUA-T060)", "64", "percent", "2032",
    "renewable share of generation 2032", "_STAGE3_RESULTS/stage3_results.xlsx sheet TotalTechnologyAnnualActivity, Guatemala PP techs 2032 (scripts/GUA/model_numbers.py)",
    69.44, 69.44, "percent", "matches", "", "Older plan (2017); the model exceeds this floor.")
add("GUA-T013", "GUA-01", "p.42;p.104", "47,000 additional households with electricity access through sustainable solutions by 2035", "47000", "households", "2035",
    "rural electrification or off-grid supply", "no access or off-grid household technology among GUA_ENERGY levers (model_levers_GUA.csv)", "", "", "",
    "in documents, not in the model", "", "")
# Emissions against BAU, older and long-term documents
add("GUA-T039", "GUA-02", "p.70", "Unconditional 11.2 percent below BAU in 2030 (NDC 2021, superseded)", "11.2", "percent", "2030",
    "energy-system emission reduction against the model BAU in 2030", f"model_levers_GUA.csv line {EM}",
    r(red(EM, "NDCNEW", 2030)), r(red(EM, "LTSNEW", 2030)), "percent", "matches", "",
    EMN + " Status judged on NDCNEW; LTSNEW is at ratio 0.90.")
add("GUA-T056", "GUA-04", "p.58;p.56", "LTS options cut projected emissions by 59 percent in 2050 (203 to 83 Mt CO2e)", "59", "percent", "2050",
    "energy-system emission reduction against the model BAU in 2050", f"model_levers_GUA.csv line {EM}",
    r(red(EM, "NDCNEW", 2050)), r(red(EM, "LTSNEW", 2050)), "percent", "matches", "",
    EMN + " Status judged on LTSNEW. The strategy figure is economy-wide (forest and agriculture options give 81 percent of its cumulative reduction).")
add("GUA-T057", "GUA-04", "p.57;p.58", "LTS options cut projected emissions by 44 percent in 2030", "44", "percent", "2030",
    "energy-system emission reduction against the model BAU in 2030", f"model_levers_GUA.csv line {EM}",
    r(red(EM, "NDCNEW", 2030)), r(red(EM, "LTSNEW", 2030)), "percent", "same direction, different size", "", EMN)
add("GUA-T059", "GUA-04", "p.24;p.30", "Cumulative 2019-2050 reduction of the LTS energy options (374 Mt) and transport options (80 Mt), summed", "454", "Mt CO2e", "2050",
    "cumulative energy-system emission reduction 2019 to 2050", "_STAGE3_RESULTS/stage3_results.xlsx sheet AnnualEmissions, Guatemala, CO2e_sources, sum of BAU minus scenario 2019-2050 (scripts/GUA/model_numbers.py)",
    212.964, 393.253, "Mt CO2e", "same direction, different size", "",
    "Target value is the sum of GUA-T059 and GUA-T062. Industry options (103 Mt, GUA-T063) mix process and energy and are left out.")
add("GUA-T073", "GUA-07", "p.92", "Energy sector GHG 29.2 percent below its BAU in 2032 (Plan Nacional de Energia)", "29.2", "percent", "2032",
    "energy-system emission reduction against the model BAU in 2032", "_STAGE3_RESULTS/stage3_results.xlsx sheet AnnualEmissions, Guatemala, CO2e_sources 2032 (scripts/GUA/model_numbers.py)",
    15.551, 13.92, "percent", "same direction, different size", "",
    "The plan's energy BAU for 2032 is 16.82 Mt; the model BAU is 38.37 Mt.")
# Transport
add("GUA-T014", "GUA-01", "p.46;p.27;p.106", "E10 ethanol blend from 2026, held to 2035", "10", "percent", "2035",
    "ethanol share applied to gasoline emission factors", "Guatemala/GUA_ENERGY/B1_Base_Scenarios_Adj_Parallel_Guatemala.py lines 3616 to 3618 (blend 0 in 2024, 5 in 2025, 10 from 2026); model_levers_GUA.csv lines 3 to 5 (DIST_GSL 0.0568 against 0.063157 in BAU)",
    10, 10, "percent", "matches", "", "The model lowers the gasoline emission factor by 10.1 percent; it starts a 5 percent blend in 2025, one year before the NDC.")
add("GUA-T067", "GUA-05", "p.254", "Ethanol blend rising to 15 percent by 2030 (roadmap reported in BTR1)", "15", "percent", "2030",
    "ethanol share applied to gasoline emission factors", "B1_Base_Scenarios_Adj_Parallel_Guatemala.py lines 3616 to 3618", 10, 10, "percent",
    "same direction, different size", "", "Not restated in NDC 3.0, which keeps E10.")
ev_t = (4451 + 10000) / 5300000 * 100
add("GUA-T016", "GUA-01", "p.47;p.107;p.45", "10,000 additional electric vehicles by 2035 against 4,451 in 2025 (fleet 5.3 million in January 2024)", r(ev_t), "percent of fleet (derived)", "2035",
    "electric share of car output (E5TRAUT) in 2035", "model_levers_GUA.csv line 176; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 27 (NDCNEW) and 49 (LTSNEW)",
    r(100 * v(176, "NDCNEW_2035")), r(100 * v(176, "LTSNEW_2035")), "percent", "same direction, different size", "",
    "Target value derived: (4,451 + 10,000) / 5,300,000. It is an upper bound because the fleet grows after 2024 and covers all vehicle types. "
    "Every road group in NDCNEW has a 20 percent electric share in 2035 (lines 176 to 182).")
hy_t = (15975 + 20000) / 5300000 * 100
hyn = (v(88, "NDCNEW_2035") + v(90, "NDCNEW_2035")) / v(110, "NDCNEW_2035") * 100
hyl = (v(88, "LTSNEW_2035") + v(90, "LTSNEW_2035")) / v(110, "LTSNEW_2035") * 100
add("GUA-T017", "GUA-01", "p.47;p.107;p.45", "20,000 additional hybrid vehicles by 2035 against 15,975 in 2025", r(hy_t), "percent of fleet (derived)", "2035",
    "hybrid and plug-in hybrid share of car output in 2035 (activity lower limits)", "model_levers_GUA.csv lines 88, 90 and 110 (TRAUTHG, TRAUTPHG, Techs_Auto lower limits)",
    r(hyn), r(hyl), "percent", "same direction, different size", "",
    "NDCNEW hybrids equal BAU (6.5 percent), so they are not a policy lever; LTSNEW caps them near 0.22 (lines 130, 131). Target share derived as for GUA-T016.")
add("GUA-T044", "GUA-02", "p.77", "24.3 percent of gasoline vehicles replaced by electric by 2032 (NDC 2021, superseded)", "24.3", "percent", "2032",
    "electric share of car output in 2032", "_STAGE3_RESULTS/stage3_results.xlsx sheet TotalTechnologyAnnualActivity, TRAUTELE over all TRAUT techs, 2032 (scripts/GUA/model_numbers.py)",
    14.01, 18.02, "percent", "same direction, different size", "", "Vehicle share against output share.")
add("GUA-T021", "GUA-01", "p.48;p.109", "25 percent of the Transmetro diesel fleet replaced by electric units by 2035", "25", "percent", "2035",
    "electric share of public bus output (E5TRBPU) in 2035", "model_levers_GUA.csv line 178; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 40 and 62",
    r(100 * v(178, "NDCNEW_2035")), r(100 * v(178, "LTSNEW_2035")), "percent", "same direction, different size", "",
    "Transmetro is one system inside the public bus group; the model applies its share to all public buses.")
add("GUA-T018", "GUA-01", "p.47;p.108", "45 km interconnected bike lane network in the department of Guatemala by 2027", "45", "km", "2027",
    "non-motorised passenger demand (E6TRNOMOT)", "model_levers_GUA.csv line 20; B1_Scenario_Config.xlsx sheet Mode_Shift rows 5 and 7", 0.0205, 0.0205,
    "model input unit (2035)", "not compared", "", "No common unit (km of lanes against passenger demand). BAU holds 0; the model lever exists and is very small.")
add("GUA-T020", "GUA-01", "p.48;p.109", "Aerometro cable car (lines 1 and 2) operating in Guatemala City by 2030", "2", "lines", "2030",
    "cable car passenger demand (E6AERO)", "B1_Scenario_Config.xlsx sheet Efficiency row 13 (NDP only, 0); no NDCNEW or LTSNEW row", "", "", "",
    "in documents, not in the model", "", "")
fir_t = (23704952 - 22777477) / 23704952 * 100
add("GUA-T078", "GUA-07", "p.79;p.80", "Firewood use cut by efficient stoves (2030: 22,777,477 t against 23,704,952 t without stoves)", r(fir_t, 2), "percent (derived)", "2030",
    "residential firewood demand (E5RESFIR) against BAU in 2030", "model_levers_GUA.csv line 16; B1_Scenario_Config.xlsx sheet Efficiency rows 24 and 35",
    r(red(16, "NDCNEW", 2030)), r(red(16, "LTSNEW", 2030)), "percent", "same direction, different size", "",
    "Target derived from Tablas 10 and 11. NDC 3.0 E-3(b) promotes efficient stoves with no number. Model cut is 18.5 percent in 2035.")
# Other sectors
for tid, page, desc, val, unit, yr, folder in [
        ("GUA-T024", "p.56;p.114", "HFC consumption 10 percent below the Kigali baseline from 2029", "10", "percent", "2029", "Guatemala/GUA_IPPU"),
        ("GUA-T025", "p.56;p.114", "HFC consumption 30 percent below the Kigali baseline from 2035", "30", "percent", "2035", "Guatemala/GUA_IPPU"),
        ("GUA-T027", "p.33;p.94", "Net zero deforestation with a net forest gain of 2,161 ha per year by 2035", "2161", "ha per year", "2035", "Guatemala/GUA_AFOLU"),
        ("GUA-T028", "p.33;p.94", "Gross deforestation 0.62 percent per year (20,833 ha) by 2035", "0.62", "percent per year", "2035", "Guatemala/GUA_AFOLU"),
        ("GUA-T030", "p.33;p.94", "LULUCF net emissions 49 percent below BAU in 2035", "49", "percent", "2035", "Guatemala/GUA_AFOLU"),
        ("GUA-T032", "p.35", "12,000 ha of additional agroforestry by 2035", "12000", "ha", "2035", "Guatemala/GUA_AFOLU"),
        ("GUA-T034", "p.52", "Intensive rotational grazing on 900 farms by 2035", "900", "farms", "2035", "Guatemala/GUA_AFOLU"),
        ("GUA-T036", "p.59", "22 organic waste projects by 2035 (methane capture programme R-3(b) without number)", "22", "projects", "2035", "Guatemala/GUA_WASTE")]:
    techs = {"Guatemala/GUA_IPPU": "technologies REFR_AC_HFC32, REFR_AC_HFC125, REFR_AC_HFC134a, REFR_AC_HFC143a",
             "Guatemala/GUA_AFOLU": "technologies Deforestacion, Restauracion, AreaIncendiada, FOLU1 to FOLU4, AG1a to AG4, GAN1 to GAN3",
             "Guatemala/GUA_WASTE": "technologies LANDFILL, CO2_CH4_BURN, COMPOST, AD, OPEN_BURN"}[folder]
    add(tid, "GUA-01", page, desc, val, unit, yr, "sector model quantity", f"{folder} ({techs}); not read for values", "", "", "",
        "not compared", folder, "Energy model does not carry this sector.")
# Model levers without document support
add("", "GUA-04", "p.24;p.58", "No 2050 renewable share of generation in the long-term strategy (energy options are named, not sized as shares)", "", "", "",
    "renewable share of generation 2050", "model_levers_GUA.csv line 149; stage1_share_analyzer_v16.py line 99 (LTSNEW 0.99 in 2050)",
    r(100 * v(149, "NDCNEW_2050")), r(100 * v(149, "LTSNEW_2050")), "percent", "in the model, not in the documents", "",
    "NDC 3.0 stops at 2035 (80 percent floor). The only later sourced share is 64 percent in 2032 (GUA-07).")
add("", "GUA-01", "p.46;p.47", "NDC 3.0 transport measures hold no electric share for freight or minibuses", "", "", "",
    "electric share of heavy freight output (E5TRYTK)", "model_levers_GUA.csv line 182; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 34 and 56",
    r(100 * v(182, "NDCNEW_2035")), r(100 * v(182, "LTSNEW_2035")), "percent (2035)", "in the model, not in the documents", "",
    "NDCNEW sets 10 percent electric in 2030 and 30 percent from 2040 for every road group; LTSNEW 10, 50 and 90 percent in 2030, 2040, 2050.")
add("", "GUA-01", "p.41;p.45", "NDC 3.0 lists energy efficiency as an additional topic without a quantified target", "", "", "",
    "final demand per fuel against BAU (industrial petroleum coke shown)", "model_levers_GUA.csv lines 7 to 17; B1_Scenario_Config.xlsx sheet Efficiency rows 15 to 25 (NDCNEW) and 26 to 36 (LTSNEW)",
    r(red(10, "NDCNEW", 2035)), r(red(10, "LTSNEW", 2035)), "percent below BAU (2035)", "in the model, not in the documents", "",
    "NDCNEW demand in 2035 against BAU: about 9.5 percent lower for industrial fuels and electricity, 10.3 percent lower for commercial fuels, "
    "8.2 percent lower for residential LPG, 18.5 percent lower for residential firewood, and 2.5 percent higher for residential electricity.")
add("", "GUA-01", "p.46", "NDC 3.0 biofuel measure is the E10 blend only; no flex-fuel vehicles", "", "", "",
    "flex-fuel motorcycle activity lower limit", "model_levers_GUA.csv line 102 (TRMOTFlex_Fuel); line 79 (TRAUTFlex_Fuel, LTSNEW only)",
    v(102, "NDCNEW_2035"), v(102, "LTSNEW_2035"), "model input unit (2035)", "in the model, not in the documents", "", "")

with open(os.path.join(JOB, "alignment_GUA.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(AH)
    w.writerows(A)
print("alignment rows", len(A))
cnt = {}
for a in A:
    cnt[a[14]] = cnt.get(a[14], 0) + 1
print(cnt)

# ---------------------------------------------------------------- proposals
PH = ["country", "scenario", "lever", "model_rows", "current_value", "proposed_value", "source_id", "page", "class", "note"]
CFG = "Guatemala/GUA_ENERGY/B1_Scenario_Config.xlsx"
P = [
    ["Guatemala", "NDCNEW", "renewable share of generation from 2035 (plant activity lower limits)",
     f"stage1_share_analyzer_v16.py lines 97 to 110 (RENEWABLE_TARGET_CURVE NDCNEW 0.75; COUNTRY_TARGET_OVERRIDES has no Guatemala entry), carried by _STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx sheet CURRENT_LOWER (Guatemala NDCNEW rows) into Stage 3; {CFG} sheet Electrical rows 59 to 73 and 119 to 133 are replaced for PP techs from 2025 in Stage 3",
     "75 percent in 2035, held to 2050 (solved 0.750)", "at least 80 percent renewable generation in 2035, held after 2035", "GUA-01", "p.40;p.102", "A",
     "A Guatemala override like those for Costa Rica and Ecuador would carry it. LTSNEW rows follow the hub decision that LTS equals NDC through 2035 (LTSNEW 2035 also 0.75 now)."],
    ["Guatemala", "NDCNEW", "new renewable capacity 2025 to 2035",
     f"{CFG} sheet Electrical rows 74 to 88 (TotalAnnualMaxCapacity, NDCNEW); solved capacity in model_levers_GUA.csv lines 150 to 164",
     "solved increase 4,104 MW (NDCNEW), 5,241 MW (LTSNEW)", "at least 1,000 MW new renewable capacity 2025 to 2035 (floor)", "GUA-01", "p.40;p.102;p.28", "A",
     "Floor already exceeded; no change needed unless the hub wants NDCNEW to sit on the stated value. Capacity follows from the share lever."],
    ["Guatemala", "NDCNEW", "electric share of road transport groups",
     f"{CFG} sheet Tech_Adoption rows 24, 27, 31, 34, 37, 40, 43 (NDCNEW electric techs, v_2030 0.1, v_2040 0.3, v_2050 0.3)",
     "10 percent of each group's output in 2030, 20 percent in 2035, 30 percent from 2040",
     "10,000 electric vehicles added 2025 to 2035 (fleet 4,451 in September 2025), all vehicle types", "GUA-01", "p.47;p.107", "A",
     "The document gives vehicles, the lever takes output shares; the hub must convert (fleet 5.3 million in January 2024, p.45, gives at most 0.27 percent). The document is silent after 2035."],
    ["Guatemala", "NDCNEW", "hybrid cars",
     f"{CFG} sheet Electrical rows 151 to 154 exist for LTSNEW only (TRAUTHG, TRAUTPHG); NDCNEW hybrids follow BAU (model_levers_GUA.csv lines 88, 90)",
     "hybrid and plug-in hybrid 6.5 percent of car output in 2035, same as BAU",
     "20,000 hybrid vehicles added 2025 to 2035 (fleet 15,975 in September 2025)", "GUA-01", "p.47;p.107", "A",
     "Needs NDCNEW rows like the LTSNEW ones; vehicle count must be converted to output."],
    ["Guatemala", "NDCNEW", "Transmetro bus electrification",
     f"{CFG} sheet Tech_Adoption row 40 (TRBPUELE, NDCNEW)", "20 percent of public bus output electric in 2035",
     "25 percent of the Transmetro diesel fleet electric by 2035", "GUA-01", "p.48;p.109", "A",
     "Transmetro is a subset of public buses; the group share must be derived from fleet sizes the NDC does not give."],
    ["Guatemala", "NDCNEW", "non-motorised transport (bike lanes)", f"{CFG} sheet Mode_Shift row 5 (E6TRNOMOT, NDCNEW)",
     "non-motorised demand 0.0205 model units in 2035 (BAU 0)", "45 km interconnected bike lane network in the department of Guatemala by 2027",
     "GUA-01", "p.47;p.108", "A", "No trips or passenger-km given; conversion needed."],
    ["Guatemala", "NDCNEW", "cable car (Aerometro)", f"{CFG} sheet Efficiency row 13 (E6AERO demand, NDP only); SmartGrid rows 4 and 5 (T5ELEAERO costs, NDP only)",
     "no cable car demand in NDCNEW or LTSNEW", "Aerometro lines 1 and 2 operating in Guatemala City by 2030", "GUA-01", "p.48;p.109", "B",
     "Needs NDCNEW and LTSNEW rows and a demand derived from capacity or ridership, which the NDC does not give."],
    ["Guatemala", "NDCNEW", "rural electricity access", "none (no access lever in GUA_ENERGY)", "no measure",
     "47,000 additional households with electricity access through sustainable solutions by 2035", "GUA-01", "p.42;p.104", "B",
     "Needs an access or off-grid technology; demand effect likely small."],
    ["Guatemala", "NDCNEW", "economy-wide emission target", f"{CFG} has no Emission_Restriction sheet; AnnualEmissionLimit empty",
     "no emission limit; solved energy-system reduction against model BAU 19.7 percent in 2035",
     "23.7 percent below BAU in net national emissions in 2035 (57,763.7 kt CO2eq); energy and transport 1,184.9 kt below the energy BAU", "GUA-01", "p.28;p.29;p.131", "C",
     "The energy model alone cannot carry a net economy-wide target dominated by forests. Its energy reduction (8,479 kt) is 7.2 times the NDC energy reduction, against a model BAU 51 percent above the NDC energy BAU."],
    ["Guatemala", "NDCNEW", "ethanol blend in gasoline", "B1_Base_Scenarios_Adj_Parallel_Guatemala.py lines 3616 to 3618",
     "5 percent in 2025, 10 percent from 2026", "documents silent", "GUA-01", "p.46", "",
     "NDC 3.0 states E10 from 2026, which the model already holds (2025 at 5 percent is one year early). The BTR1 roadmap figure of 15 percent by 2030 (GUA-05 p.254) is not restated in NDC 3.0, so nothing is proposed."],
    ["Guatemala", "NDCNEW", "final energy demand per fuel (efficiency, firewood)", f"{CFG} sheet Efficiency rows 15 to 25",
     "3.6 to 18.5 percent below BAU in 2035 by fuel", "documents silent", "GUA-01", "p.41;p.42;p.45", "",
     "NDC 3.0 has only an energy information system (E-2) and unquantified efficient stoves (E-3(b)). The older Plan Nacional de Energia (GUA-07 p.79 to p.81) gives 100,000 stoves."],
    ["Guatemala", "NDCNEW", "electric share of freight trucks and minibuses", f"{CFG} sheet Tech_Adoption rows 31, 34, 43",
     "10 percent in 2030, 30 percent from 2040", "documents silent", "GUA-01", "p.46;p.47", "", ""],
    ["Guatemala", "NDCNEW", "electricity imports (IMP_ELE)", f"{CFG} sheet Electrical rows 156 and 157",
     "lower limit 0 from 2025 (BAU 5.70 to 3.80 PJ to 2031)", "documents silent", "GUA-05", "p.253", "",
     "Known unintended difference (brief section 3), not a policy measure. BTR1 reports imports at 9.1 percent of supply 2017-2024, with no target."],
    ["Guatemala", "LTSNEW", "renewable share of generation in 2050", "stage1_share_analyzer_v16.py line 99 (LTSNEW 0.99 in 2050)",
     "99 percent in 2050", "documents silent", "GUA-04", "p.24;p.58", "", "The LTS (2018) names options and an economy-wide 59 percent cut against BAU in 2050; no power share."],
    ["Guatemala", "LTSNEW", "electric share of road transport groups", f"{CFG} sheet Tech_Adoption rows 46, 49, 53, 56, 59, 62, 65",
     "10, 50, 90 percent in 2030, 2040, 2050", "documents silent", "GUA-04", "p.30", "", "The LTS names electric vehicles (option T-5) without a size."],
    ["Guatemala", "LTSNEW", "economy-wide emission level in 2050", "AnnualEmissionLimit empty",
     "solved energy-system reduction against model BAU 57.7 percent in 2050", "59 percent below projected emissions in 2050 with all LTS options (economy-wide)", "GUA-04", "p.58", "C",
     "Energy model cannot carry an economy-wide target; its energy cut already matches the headline percentage (ratio 0.98)."],
]
with open(os.path.join(JOB, "parts/proposals_GUA.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(PH)
    w.writerows(P)
cc = {}
for p in P:
    k = p[8] or "documents silent"
    cc[k] = cc.get(k, 0) + 1
print("proposals", len(P), cc)
