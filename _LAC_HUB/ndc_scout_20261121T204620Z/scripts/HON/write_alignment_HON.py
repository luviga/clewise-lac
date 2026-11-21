"""Write alignment_HON.csv and parts/proposals_HON.csv.

Usage: python -I write_alignment_HON.py <job_folder>
Model values were computed with scripts/HON/model_numbers.py and scripts/HON/check_solved_vs_inputs.py
(read-only, model state 481a7c0) or read from model_levers_HON.csv; the line numbers below refer to that file.
Ratio = model / target in the same unit and year.
"""
import csv
import os
import sys

JOB = sys.argv[1]
ML = "model_levers_HON.csv"
EM = ("Label CO2e_sources (fossil fuel at the DIST_* distribution technologies, assumed Mt CO2e from factors of "
      "0.0743 per PJ diesel and 0.0632 per PJ LPG) is the energy-wide total and is used alone; CO2e, CO2e_DE and "
      "CO2e_PP cover parts of the same fuel and are never added. Health is not a greenhouse gas. CO2e_sources also "
      "counts LPG exports (E5EXPLPG), which are higher in NDCNEW and LTSNEW than in BAU (unlisted difference, see notes).")
STG = ("Solved plant generation follows the Stage 2 controller (CONTROLLER_NEW_SCENARIOS.xlsx, CURRENT_LOWER), "
       "which comes from stage1_share_analyzer_v16.py lines 97 to 99 (default curve, no Honduras override); "
       "the compiled B1_Output_Params limits imply 75 percent already in 2030.")

H = ["target_id", "source_id", "page", "target_description", "target_value", "target_unit", "target_year",
     "model_quantity", "model_reference", "NDCNEW_value", "LTSNEW_value", "model_unit", "ratio_NDCNEW",
     "ratio_LTSNEW", "status", "sector_model_folder", "note"]
A = []


def r3(x):
    return "" if x is None else f"{x:.3f}"


def a(tid, sid, page, desc, tv, tu, ty, mq, mref, n, l, mu, status, folder="", note="", ratio=True):
    rn = rl = ""
    if ratio and n is not None and tv not in ("", None) and float(tv) != 0:
        rn = r3(n / float(tv))
        rl = r3(l / float(tv)) if l is not None else ""
    A.append([tid, sid, page, desc, tv, tu, ty, mq, mref, "" if n is None else f"{n:g}",
              "" if l is None else f"{l:g}", mu, rn, rl, status, folder, note])


SD = "same direction, different size"
# ---------------- economy-wide and energy emissions (NDC 3.0)
a("HON-T001", "HON-01", "p.23;p.25", "Net emissions 12,847.2 Gg CO2e below BAU in 2035 (all sectors)", "12847.2",
  "Gg CO2e", "2035", "energy-system emission reduction against the model BAU in 2035",
  f"{ML} line 219 (solved, emissions by label, CO2e_sources): BAU minus scenario, Mt converted to kt",
  2481.5, 2935.4, "kt CO2e", SD, note="Model covers energy and transport only; the NDC target is net of LULUCF and most of it comes from agriculture (6,801.5 Gg). " + EM)
a("HON-T002", "HON-01", "p.22", "19.6 percent below BAU in 2035 (all sectors, net)", "19.6", "percent", "2035",
  "energy-system emission reduction against the model BAU in 2035", f"{ML} line 219, 1 - scenario/BAU",
  17.412, 20.597, "percent", SD, note="Status judged on NDCNEW (ratio 0.89); LTSNEW is within 10 percent. " + EM)
a("HON-T003", "HON-01", "p.22;p.23;p.25", "Net emissions 8,564.8 Gg CO2e below BAU in 2030 (all sectors)", "8564.8",
  "Gg CO2e", "2030", "energy-system emission reduction against the model BAU in 2030",
  f"{ML} line 219, BAU minus scenario, Mt converted to kt", 964.2, 984.8, "kt CO2e", SD,
  note="Model covers energy and transport only. " + EM)
a("HON-T004", "HON-01", "p.22", "17 percent below BAU in 2030 (all sectors, net)", "17", "percent", "2030",
  "energy-system emission reduction against the model BAU in 2030", f"{ML} line 219, 1 - scenario/BAU",
  7.579, 7.741, "percent", SD, note=EM)
a("HON-T008", "HON-01", "p.25", "Energy sector mitigation of 2,519.1 Gg CO2e against BAU in 2030", "2519.1", "Gg CO2e",
  "2030", "energy-system emission reduction against the model BAU in 2030",
  f"{ML} line 219, BAU minus scenario, Mt converted to kt", 964.2, 984.8, "kt CO2e", SD,
  note="The NDC energy BAU is 9,161 Gg in 2030 (Tabla 2, p.24) against a model BAU of 12,722 kt (ratio 1.39); the NDC reduction is 27.5 percent of its own energy BAU, the model's 7.6 percent. If the NDC figure were cumulative 2021-2030, the model gives 2,095 kt (ratio 0.83). " + EM)
a("HON-T009", "HON-01", "p.25", "Energy sector mitigation of 3,778.6 Gg CO2e against BAU in 2035", "3778.6", "Gg CO2e",
  "2035", "energy-system emission reduction against the model BAU in 2035",
  f"{ML} line 219, BAU minus scenario, Mt converted to kt", 2481.5, 2935.4, "kt CO2e", SD,
  note="NDC energy BAU 2035 is 8,963 Gg (declining linear projection); model BAU 14,251 kt (ratio 1.59). Cumulative 2021-2035 model reduction 11,295 kt (NDCNEW). " + EM)
a("HON-T055", "HON-01", "p.11", "Inventory: energy sector emissions 10,880 Gg CO2e in 2022 (level check)", "10880",
  "Gg CO2e", "2022", "energy-system emissions in 2022 (BAU, history)",
  "_STAGE3_RESULTS/stage3_results.xlsx sheet AnnualEmissions, Honduras, CO2e_sources 2022 (scripts/HON/model_numbers.py)",
  9763.3, 9763.3, "kt CO2e", SD,
  note="Level check, not a target. All scenarios share history to 2024. The inventory energy sector includes CH4 and N2O of firewood, which CO2e_sources does not carry. " + EM)
# ---------------- superseded economy-wide targets
a("HON-T057", "HON-02", "p.3;p.11", "16 percent below the 2030 BAU (energy, IPPU, agriculture, waste) (superseded)", "16",
  "percent", "2030", "energy-system emission reduction against the model BAU in 2030", f"{ML} line 219",
  7.579, 7.741, "percent", SD, note="Same target as HON-T062. " + EM)
a("HON-T062", "HON-03", "p.28;p.29", "16 percent below BAU in 2030 excluding LULUCF (superseded)", "16", "percent",
  "2030", "energy-system emission reduction against the model BAU in 2030", f"{ML} line 219", 7.579, 7.741,
  "percent", SD, note=EM)
a("HON-T063", "HON-03", "p.30", "Energy share of the 16 percent: 9 percent of the 2030 BAU of 28,945 Gg (2,605.1 Gg derived) (superseded)",
  "2605.1", "Gg CO2e", "2030", "energy-system emission reduction against the model BAU in 2030",
  f"{ML} line 219, BAU minus scenario, Mt converted to kt", 964.2, 984.8, "kt CO2e", SD,
  note="Target value derived as 0.09 x 28,945. Same split in HON-02 p.3 (HON-T061). " + EM)
a("HON-T067", "HON-03", "p.33", "Energy emissions 20 percent below the energy BAU in 2030 (12,142 to 9,734 kt) (superseded)",
  "20", "percent", "2030", "energy-system emission reduction against the model BAU in 2030", f"{ML} line 219",
  7.579, 7.741, "percent", SD,
  note="BAU levels agree closely: NDC 2021 energy BAU 12,142 kt against model BAU 12,722 kt (ratio 1.05); the 2021 mitigation level 9,734 kt against model NDCNEW 11,758 kt (ratio 1.21). " + EM)
a("HON-T070", "HON-04", "p.2;p.3", "15 percent below BAU in 2030 (INDC, superseded)", "15", "percent", "2030",
  "energy-system emission reduction against the model BAU in 2030", f"{ML} line 219", 7.579, 7.741, "percent", SD,
  note=EM)
# ---------------- power sector
a("HON-T018", "HON-01", "p.26", "Renewable share of generation 70 percent by 2030", "70", "percent", "2030",
  "renewable share of generation 2030",
  f"{ML} line 176 (renewable types PPBIM PPGEO PPHDAM PPHROR PPPVD PPPVT PPWNDON)", 64.766, 64.766, "percent",
  "matches", note="Within 10 percent by the rule (ratio 0.93), but 5.2 points below a stated floor. " + STG)
a("HON-T019", "HON-01", "p.26", "Renewable share of generation above 70 percent towards 2035", "70", "percent", "2035",
  "renewable share of generation 2035", f"{ML} line 176", 75.0, 75.0, "percent", "matches",
  note="Floor met. " + STG)
a("HON-T089", "HON-08", "p.83;p.94", "PIEG 2026-2035: renewable share of supply 76 percent in 2030", "76", "percent",
  "2030", "renewable share of generation 2030", f"{ML} line 176", 64.766, 64.766, "percent", SD,
  note="The PIEG is an indicative least-cost plan; its renewable share counts supply including imports. " + STG)
a("HON-T090", "HON-08", "p.83", "PIEG 2026-2035: renewable share of supply 71 percent in 2035", "71", "percent", "2035",
  "renewable share of generation 2035", f"{ML} line 176", 75.0, 75.0, "percent", "matches", note=STG)
a("HON-T073", "HON-05", "p.524", "Prospectiva Energetica 2017-2038 (reported in BTR1): renewables above 80 percent of generation by 2038",
  "80", "percent", "2038", "renewable share of generation 2038",
  "_STAGE3_RESULTS/stage3_results.xlsx sheet TotalTechnologyAnnualActivity, Honduras PP techs 2038", 75.0, 79.8,
  "percent", "matches", note="Older plan; ratio 0.94 (NDCNEW) and 1.00 (LTSNEW). " + STG)
a("HON-T091", "HON-08", "p.12;p.89;p.93", "PIEG: 1,796.24 MW new renewable capacity 2026-2035", "1796.24", "MW", "2035",
  "new renewable capacity 2026-2035",
  "_STAGE3_RESULTS/stage3_results.xlsx sheet NewCapacity, Honduras renewable PP techs, sum 2026-2035 (scripts/HON/model_numbers.py)",
  3081.7, 3408.8, "MW", SD,
  note="Model BAU alone adds 1,455.6 MW. NDCNEW adds PPPVT 1,690, PPWNDON 799, PPPVD 546 MW. PIEG counts hybrid plants at their renewable rating only.")
a("HON-T092", "HON-08", "p.12;p.89;p.93", "PIEG: 1,285 MW new thermal capacity 2026-2035", "1285", "MW", "2035",
  "new fossil capacity 2026-2035", "stage3_results.xlsx sheet NewCapacity, Honduras fossil PP techs, sum 2026-2035",
  800.3, 920.4, "MW", SD, note="NDCNEW: PPFOI 529 MW, PPNGS 263 MW, PPCOK 7.5 MW. BAU adds 868 MW (PPFOI 830).")
a("HON-T094", "HON-08", "p.9;p.34;p.35", "PIEG: about 1,342.62 MW of fossil plants retired 2026-2035", "1342.62", "MW", "2035",
  "gross fossil capacity leaving 2026-2035 (derived)",
  f"{ML} lines 178 to 182 and 185 to 186 (installed capacity 2025 and 2035) with NewCapacity 2026-2035: new fossil plus net decrease",
  1237.6, 1237.6, "MW", "matches",
  note="Derived: NDCNEW new fossil 800.3 MW plus net fossil decrease 437.3 MW (1,542.4 to 1,105.1 MW); LTSNEW 920.4 plus 317.2.")
a("HON-T093", "HON-08", "p.12;p.89;p.93", "PIEG: 215 MW stand-alone battery storage 2026-2035", "215", "MW", "2035",
  "storage capacity", "stage3_results.xlsx sheet TotalCapacityAnnual: no storage technology with capacity for Honduras",
  None, None, "MW", "in documents, not in the model")
a("HON-T095", "HON-08", "p.82", "PIEG: 250 MW natural gas combined cycle in 2029", "250", "MW", "2029",
  "installed natural gas capacity (PPNGS) 2029", f"{ML} line 186 and stage3_results.xlsx TotalCapacityAnnual",
  0.0, 0.0, "MW", SD,
  note="Model gas capacity starts in 2033 and reaches 262.8 MW (NDCNEW) and 354.7 MW (LTSNEW) in 2035, but PPNGS never generates in any scenario: its controller lower limit is 0, so Stage 3 sets its activity upper limit to 0 while the reserve margin still builds it.", ratio=False)
a("HON-T096", "HON-08", "p.82;p.34", "PIEG: coal or petcoke steam turbine of 105 MW kept (Becosa 105 MW retired and a new 105 MW unit in 2029)",
  "105", "MW", "2029", "installed petroleum coke capacity (PPCOK) 2029",
  "stage3_results.xlsx TotalCapacityAnnual, Honduras PPCOK 2029", 124.1, 124.2, "MW", SD)
a("HON-T097", "HON-08", "p.90;p.94", "PIEG: power sector CO2 49 percent below 2025 in 2030", "49", "percent", "2030",
  "change of power plant CO2 (CO2_PP) from the scenario's own 2025 level",
  f"{ML} line 215 (solved, CO2_PP)", -3.0, -3.0, "percent reduction", "opposite direction",
  note="Model power CO2 rises 3.0 percent from 2025 to 2030 in NDCNEW and LTSNEW (19.3 percent in BAU). Within each scenario the plant emission factors are constant from 2025, so the known unintended factor difference against BAU does not affect this own-trajectory comparison.")
a("HON-T098", "HON-08", "p.90;p.94", "PIEG: power sector CO2 33 percent below 2025 in 2035", "33", "percent", "2035",
  "change of power plant CO2 (CO2_PP) from the scenario's own 2025 level", f"{ML} line 215", 12.46, 8.0,
  "percent reduction", SD)
a("HON-T099", "HON-08", "p.90", "SEN: each energy subsector cuts emissions 20 percent towards 2030", "20", "percent",
  "2030", "power plant emissions (CO2e_PP) against the model BAU in 2030", f"{ML} line 218 (solved, CO2e_PP)",
  13.787, 13.786, "percent", SD,
  note="Base not printed; read as against BAU. Plant emission factors differ between BAU and the policy scenarios from 2025 (known unintended difference), which changes policy CO2e_PP (diesel plant factors 23 percent lower, petroleum coke 38 percent higher). Energy-wide CO2e_sources falls 7.6 percent.")
a("HON-T100", "HON-08", "p.54", "PIEG: electricity demand 15,455.28 GWh in 2030 (55.64 PJ)", "55.639", "PJ", "2030",
  "total generation (no imports in any scenario)", f"{ML} lines 174 and 208", 57.826, 57.826, "PJ", "matches",
  note="Target converted from GWh at 0.0036 PJ/GWh. Model BAU 55.64 PJ.")
a("HON-T101", "HON-08", "p.54", "PIEG: electricity demand 18,108.55 GWh in 2035 (65.19 PJ)", "65.191", "PJ", "2035",
  "total generation", f"{ML} lines 174 and 208", 69.265, 72.795, "PJ", "matches",
  note="Model BAU 65.18 PJ. LTSNEW is 11.7 percent above the plan.")
# ---------------- demand side
a("HON-T022", "HON-01", "p.26", "Electricity share of final use (com, ind, res) up at least 3 points by 2030", "3",
  "percentage points", "2030", "change of the electric share of compiled RES+COM+IND demand from 2022",
  "HON_ENERGY/B1_Output_Params/<scenario>/SpecifiedAnnualDemand.csv, fuels E5RES*, E5COM*, E5IND* (scripts/HON/model_numbers.py)",
  6.14, 6.14, "percentage points", SD,
  note="Base year read as 2022. Electric share 24.71 percent in 2022, 30.85 percent in 2030 in every scenario including BAU; the policy scenarios cut all fuels by the same percentage.")
a("HON-T023", "HON-01", "p.26", "Electricity share of final use up at least 5 points by 2035", "5", "percentage points",
  "2035", "change of the electric share of compiled RES+COM+IND demand from 2022", "as above", 7.04, 7.04,
  "percentage points", SD, note="31.75 percent in 2035 in every scenario including BAU.")
a("HON-T020", "HON-01", "p.26", "Electricity intensity down 3.4 kWh/USD in 2030 against 2022", "3.4", "kWh/USD", "2030",
  "electricity intensity of GDP", "no GDP-linked indicator among HON_ENERGY levers", None, None, "",
  "in documents, not in the model")
a("HON-T085", "HON-07", "p.79", "BUR2: industrial energy consumption 1 to 4 percent below BAU in 2030", "4", "percent",
  "2030", "compiled industrial demand (all E5IND fuels) against BAU in 2030",
  f"{ML} lines 32 to 40 (E5IND*); SpecifiedAnnualDemand.csv", 2.50, 2.50, "percent", "matches",
  note="Model cut 2.50 percent lies inside the printed 1 to 4 percent range; ratio shown against the upper end.")
a("HON-T025", "HON-01", "p.27", "Firewood per household 39 percent below 2012 by 2030", "39", "percent reduction",
  "2030", "change of compiled residential firewood demand (E5RESFIR), 2030 against 2018",
  f"{ML} line 42; B1_Scenario_Config.xlsx sheet Efficiency row 105", 11.80, 11.80, "percent reduction", SD,
  note="Not like for like: 2012 is before the model start and the model has no household count. Against BAU 2030 the cut is 2.5 percent (51.05 against 52.36 PJ).")
a("HON-T069", "HON-03", "p.42;p.43", "Household firewood 39 percent below 2012 by 2030 (13,936 kBEP in 2012) (superseded wording)",
  "39", "percent reduction", "2030", "change of compiled residential firewood demand, 2030 against 2018",
  f"{ML} line 42", 11.80, 11.80, "percent reduction", SD, note="Same target as HON-T025 and HON-T072 (INDC).")
a("HON-T079", "HON-05", "p.528", "Efficient stoves NAMA: 1,100,000 stoves by 2030", "1100000", "stoves", "2030",
  "residential firewood demand", f"{ML} line 42", None, None, "", "not compared",
  note="No stove count in the model; the firewood cut against BAU is 2.5 percent in 2030.")
# ---------------- transport
a("HON-T024", "HON-01", "p.27", "Biofuels 5 percent of transport final energy by 2030", "5", "percent", "2030",
  "ethanol share of transport final energy (blend share times gasoline share of T4 fuel use)",
  f"{ML} lines 2 and 14 to 21 (DIST_GSL and T4GSL_* emission factors 4.95 to 5.05 percent lower); B1_Base_Scenarios_Adj_Parallel_Honduras.py lines 3712 to 3769",
  2.30, 2.32, "percent", SD,
  note="The model blend is ethanol in gasoline only, 4.99 percent in 2030 and 5 percent in 2035; the biodiesel list is empty (line 3714). Gasoline is 46 percent of T4 transport fuel in NDCNEW 2030.")
a("HON-T026", "HON-01", "p.27", "3 percent of the national vehicle fleet electric by 2030", "3", "percent of fleet",
  "2030", "electric share of road group output (all nine groups)", f"{ML} lines 199 to 207", 10.01, 10.01,
  "percent of output", SD, note="Fleet share against output share; electric vehicles may drive more than average, so the true fleet share is below the output share.")
a("HON-T027", "HON-01", "p.27", "7.5 percent of the national vehicle fleet electric by 2035", "7.5", "percent of fleet",
  "2035", "electric share of road group output (all nine groups)", f"{ML} lines 199 to 207", 20.01, 30.0,
  "percent of output", SD)
a("HON-T028", "HON-01", "p.27", "20 percent of light vehicles gasoline hybrids by 2035", "20", "percent", "2035",
  "hybrid share of car output (TRAUTHG)",
  f"stage3_results.xlsx TotalTechnologyAnnualActivity; {ML} lines 71 and 111; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 154 and 184",
  0.0, 0.0, "percent of output", "opposite direction",
  note="NDCNEW caps hybrid cars at 2 percent (Max) and has no lower limit, so the solver builds none; BAU forces 1.0 percent through a lower limit. Pick-ups and SUVs have no hybrid technology.")
a("HON-T029", "HON-01", "p.27", "15 percent of heavy and light freight vehicles diesel hybrids by 2035", "15", "percent",
  "2035", "hybrid share of light freight output (TRYLFHD); heavy trucks (TRYTKHD) 0",
  f"stage3_results.xlsx TotalTechnologyAnnualActivity; {ML} lines 80 and 82; Tech_Adoption rows 177, 181, 207, 211",
  3.33, 0.13, "percent of output", "in documents, not in the model",
  note="NDCNEW light freight hybrids equal BAU (3.33 percent); heavy-truck hybrids are 0 in all scenarios. The levers are upper limits only.")
a("HON-T030", "HON-01", "p.27", "Sustainable urban mobility plans by 2030 (no number)", "", "", "2030",
  "public passenger demand shift and non-motorised demand", f"{ML} lines 47 and 48; B1_Scenario_Config.xlsx sheet Mode_Shift rows 10 and 11",
  None, None, "", "not compared",
  note="No number in the document. NDCNEW adds non-motorised demand of 0.0101 model units in 2035 (BAU 0) and a small public transport shift.")
# ---------------- model levers without document support
a("", "HON-01", "p.14;p.15", "No long-term strategy is published: no 2050 renewable share in any document", "", "", "",
  "renewable share of generation 2050", f"{ML} line 176; stage1_share_analyzer_v16.py line 99 (LTSNEW 0.99 in 2050)",
  75.0, 99.0, "percent", "in the model, not in the documents",
  note="NDC 3.0 says the LTS is being consolidated and has not been submitted. The newest sourced share is 71 percent in 2035 (HON-08).")
a("", "HON-01", "p.14;p.15", "No long-term strategy: no 2050 transport electrification in any document", "", "", "",
  "electric share of car output 2050", f"{ML} line 199; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 155 and 185",
  30.03, 90.09, "percent", "in the model, not in the documents")
a("", "HON-01", "p.14;p.15", "No long-term strategy: no 2050 emission level in any document", "", "", "",
  "energy-system emission reduction against the model BAU in 2050", f"{ML} line 219", 11.099, 60.036, "percent",
  "in the model, not in the documents", note=EM)
a("", "HON-01", "p.26", "NDC 3.0 states efficiency as an electricity-intensity target, not as fuel demand cuts", "", "", "",
  "compiled final demand per fuel against BAU in 2035 (residential firewood shown)",
  f"{ML} lines 25 to 46 except line 31; B1_Scenario_Config.xlsx sheet Efficiency rows 94 to 117 (NDCNEW)", 5.0, 5.0,
  "percent below BAU (2035)", "in the model, not in the documents",
  note="NDCNEW cuts residential, commercial and industrial demand by 2.5 percent in 2030 and about 5 percent in 2035 for every fuel; LTSNEW cuts more after 2035.")
a("", "HON-01", "p.25;p.26;p.27", "No document gives a higher LPG export demand for the policy scenarios", "", "", "",
  "LPG export demand E5EXPLPG in 2035", f"{ML} line 31; B1_Scenario_Config.xlsx sheet Efficiency row 92 (BAU only)",
  21.4808, 21.4808, "PJ", "in the model, not in the documents",
  note="BAU holds LPG exports at 11.41 PJ from 2025 through an override row labelled 'Demand Commecial Electricity'; NDCNEW and LTSNEW have no override and grow to 39.25 PJ in 2050. Through DIST_LPG this adds about 0.64 Mt to CO2e_sources in 2035. Not on the brief's list of known unintended differences.")

# ---------------- other sectors: name the sector model folder, no numbers
FOLDER = {
    "IPPU": ("Honduras/HON_IPPU", "technologies PROD_CLK_TRAD, PROD_CEM, REFR_AC_HFC32, REFR_AC_HFC125, REFR_AC_HFC134a, REFR_AC_HFC143a"),
    "Agriculture": ("Honduras/HON_AFOLU", "technologies GA_CAR, GA_LEC, GA_POR, GA_POUL, AG_CAF, AG_RIC, SOIALL and others"),
    "LULUCF": ("Honduras/HON_AFOLU", "technologies LU_FORLAT, LU_FORCON, LU_FORMIX, LU_FORMAN, LU_FORDEC, LU_PAS, NS_LU_FOR_*"),
    "Waste": ("Honduras/HON_WASTE", "technologies LANDFILL, LANDFILL_ELEC, CO2_CH4_BURN, COMPOST, ORG_SS, DWW_DC, DWW_N, IWW"),
}
with open(os.path.join(JOB, "targets_HON.csv"), encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(fh):
        if r["sector"] in FOLDER:
            fo, techs = FOLDER[r["sector"]]
            A.append([r["target_id"], r["source_id"], r["page"], r["description"], r["value"], r["unit"],
                      r["target_year"], "sector model quantity", f"{fo} ({techs}); not read for values",
                      "", "", "", "", "", "not compared", fo, "Energy model does not carry this sector."])

with open(os.path.join(JOB, "alignment_HON.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(H)
    w.writerows(A)
print("alignment rows", len(A))

# ------------------------------------------------------------------ proposals
PH = ["country", "scenario", "lever", "model_rows", "current_value", "proposed_value", "source_id", "page", "class", "note"]
CFG = "Honduras/HON_ENERGY/B1_Scenario_Config.xlsx"
P = [
    ["Honduras", "NDCNEW", "renewable share of generation 2030 to 2035 (plant activity limits)",
     "stage1_share_analyzer_v16.py lines 97 to 110 (RENEWABLE_TARGET_CURVE NDCNEW {2035: 0.75, 2050: 0.75}; COUNTRY_TARGET_OVERRIDES has no Honduras entry), carried by _STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx sheet CURRENT_LOWER (Honduras NDCNEW rows) into Stage 3; "
     + CFG + " sheet Electrical rows 82 to 101 (lower) and 162 to 181 (upper) are replaced for PP techs from 2025 in Stage 3",
     "solved 64.8 percent in 2030, 75.0 percent in 2035 and after",
     "at least 70 percent renewable generation in 2030, kept at or above 70 percent to 2035", "HON-01", "p.26", "A",
     "A Honduras override with a 2030 point of at least 0.70 would carry it; 2035 already meets the floor. LTSNEW rows follow the hub decision that LTS equals NDC through 2035. The PIEG (HON-08 p.83) reaches 76 percent in 2030."],
    ["Honduras", "NDCNEW", "electric share of road transport groups",
     CFG + " sheet Tech_Adoption rows 155, 158, 160, 163, 166, 170, 173, 175, 180 (NDCNEW electric techs, Min/Max, v_2030 0.1, v_2040 0.3, v_2050 0.3)",
     "10 percent of each group's output in 2030, 20 percent in 2035, 30 percent from 2040",
     "3 percent of the national vehicle fleet electric in 2030 and 7.5 percent in 2035", "HON-01", "p.27", "A",
     "Fleet share must be converted to output shares per group; the document gives no split by vehicle type and is silent after 2035."],
    ["Honduras", "NDCNEW", "hybrid cars", CFG + " sheet Tech_Adoption row 154 (TRAUTHG, Max, v_2030 0.02, v_2040 0.02, v_2050 0.02)",
     "upper limit 2 percent of car output, solved 0 (BAU 1.0 percent through a lower limit)",
     "20 percent of light vehicles gasoline hybrids by 2035", "HON-01", "p.27", "A",
     "Needs a lower limit (Min) instead of a cap. 'Light vehicles' may include pick-ups and SUVs, which have no hybrid technology in the model (class B for that part)."],
    ["Honduras", "NDCNEW", "hybrid freight trucks",
     CFG + " sheet Tech_Adoption rows 177 (TRYTKHD, Max, v_2040 0.08) and 181 (TRYLFHD, Max, v_2040 0.05)",
     "heavy-truck hybrids 0, light-freight hybrids 3.3 percent of output in 2035 (same as BAU)",
     "15 percent of heavy and light freight vehicles diesel hybrids by 2035", "HON-01", "p.27", "A",
     "Needs lower limits; vehicle shares to be converted to output shares."],
    ["Honduras", "NDCNEW", "biofuel share of transport energy",
     "Honduras/HON_ENERGY/B1_Base_Scenarios_Adj_Parallel_Honduras.py lines 3712 to 3769 (Diesel_Techs empty at line 3714; gasoline blend 0 in 2025, 4.99 percent in 2030, 5.00 percent in 2035 at lines 3764 to 3766)",
     "ethanol 5 percent of gasoline, about 2.3 percent of transport final energy in 2030",
     "biofuels 5 percent of transport final energy by 2030, held to 2035", "HON-01", "p.27", "A",
     "The document does not say which fuel. Either a biodiesel blend (the code path exists with an empty list) or a higher ethanol share would reach 5 percent. The blend only changes emission factors, not fuel supply."],
    ["Honduras", "NDCNEW", "residential firewood demand",
     CFG + " sheet Efficiency row 105 (E5RESFIR, NDCNEW)",
     "51.05 PJ in 2030 (11.8 percent below 2018, 2.5 percent below BAU)",
     "firewood use per household 39 percent below the 2012 level by 2030", "HON-01", "p.27", "A",
     "Needs the 2012 level (HON-03 p.43 gives 13,936 kBEP for residential use in 2012) and household numbers to convert; the BTR1 stove goal of 1.1 million stoves (HON-05 p.528) is another basis."],
    ["Honduras", "NDCNEW", "electricity share of final use (commercial, industrial, residential)",
     CFG + " sheet Efficiency rows 94 to 117 (NDCNEW demand per fuel)",
     "plus 6.1 points in 2030 and 7.0 points in 2035 against 2022 (same as BAU)",
     "at least plus 3 points by 2030 and 5 points by 2035", "HON-01", "p.26", "A",
     "Already exceeded; no change needed unless the hub wants the policy scenario to differ from BAU."],
    ["Honduras", "NDCNEW", "energy-sector emission level",
     "no Emission_Restriction sheet in " + CFG + "; AnnualEmissionLimit.csv empty",
     "no emission limit; solved reduction against model BAU 964 kt in 2030 and 2,482 kt in 2035",
     "energy mitigation of 2,519.1 Gg CO2e in 2030 and 3,778.6 Gg in 2035 against BAU", "HON-01", "p.25", "B",
     "Needs an emission lever and an agreed BAU: the NDC energy BAU (9,161 Gg in 2030, 8,963 in 2035, HON-01 p.24) is 28 to 37 percent below the model BAU."],
    ["Honduras", "NDCNEW", "economy-wide net emission target", "AnnualEmissionLimit.csv empty",
     "no emission limit", "12,847.2 Gg CO2e below BAU in 2035 (net, all sectors); 8,564.8 Gg in 2030", "HON-01",
     "p.23;p.25", "C", "The energy model alone cannot carry a net economy-wide target in which agriculture provides more than half of the reduction."],
    ["Honduras", "NDCNEW", "electricity intensity of GDP", "none", "no indicator",
     "minus 3.4 kWh/USD in 2030 and a further 4 kWh/USD in 2035 against 2022", "HON-01", "p.26", "C",
     "Unit as printed looks implausible; it can only be checked ex post against _GDP_Ref.xlsx."],
    ["Honduras", "NDCNEW", "natural gas combined cycle in the generation mix",
     "Honduras/HON_ENERGY/B1_Scenario_Config.xlsx sheet Electrical rows 93 and 173 (PPNGS lower and upper, replaced by the controller in Stage 3); controller CURRENT_LOWER PPNGS 0",
     "capacity from 2033 (262.8 MW in 2035) but zero generation in every scenario",
     "250 MW gas combined cycle from 2029 (PIEG 2026-2035)", "HON-08", "p.82", "A",
     "Sector plan, indicative; applies to BAU as much as to NDCNEW. A controller share for PPNGS is needed for any gas generation."],
    ["Honduras", "NDCNEW", "electricity imports (IMP_ELE)", CFG + " sheet Electrical row 203",
     "upper limit 0 from 2025 (BAU 99,999)", "documents silent", "HON-08", "p.32", "",
     "Known unintended difference (brief section 3), not a policy measure. Solved imports are 0 in every scenario, BAU included. The PIEG reports net imports of about 1 percent of supply (2024) and sets no target."],
    ["Honduras", "NDCNEW", "LPG export demand (E5EXPLPG)", CFG + " sheet Efficiency row 92 (BAU override only)",
     "policy 21.48 PJ in 2035 against BAU 11.41 PJ", "documents silent", "HON-01", "p.25", "",
     "Unlisted BAU-policy difference that raises policy emissions; the hub should decide whether to copy the BAU row to NDCNEW and LTSNEW."],
    ["Honduras", "NDCNEW", "public and non-motorised transport demand",
     CFG + " sheet Mode_Shift rows 10 and 11 (NDCNEW)", "non-motorised demand 0.0101 model units in 2035 (BAU 0)",
     "documents silent", "HON-01", "p.27", "", "The NDC asks for urban mobility plans by 2030 without a number."],
    ["Honduras", "LTSNEW", "renewable share of generation in 2050", "stage1_share_analyzer_v16.py line 99 (LTSNEW 0.99 in 2050)",
     "99 percent in 2050", "documents silent", "HON-01", "p.14;p.15", "",
     "No long-term strategy is published (being consolidated, not submitted)."],
    ["Honduras", "LTSNEW", "electric share of road transport groups after 2035",
     CFG + " sheet Tech_Adoption rows 182 to 211 (LTSNEW block; electric techs v_2030 0.1, v_2040 0.5, v_2050 0.9)",
     "30 percent in 2035, 50 percent in 2040, 90 percent in 2050", "documents silent", "HON-01", "p.14;p.15", "",
     "Hub decision: LTS equals NDC through 2035; nothing sourced after 2035."],
]
with open(os.path.join(JOB, "parts", "proposals_HON.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(PH)
    w.writerows(P)
print("proposal rows", len(P))
