"""Write parts/proposals_JAM.csv (D2 draft). Rows refer to the model state at 481a7c0 (read-only).

Usage: python -I write_proposals_JAM.py <job_dir>
"""
import csv
import os
import sys

JOB = sys.argv[1]
CFG = "Jamaica/JAM_ENERGY/B1_Scenario_Config.xlsx"
TCFG = "Jamaica/JAM_TRANSPORT/B1_Scenario_Config.xlsx"
CTL = "_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx sheet CURRENT_LOWER"
CURVE = "stage2_apply_v2.py lines 61 to 75 and stage1_share_analyzer_v16.py lines 97 to 110 (RENEWABLE_TARGET_CURVE; COUNTRY_TARGET_OVERRIDES has no Jamaica entry)"

P = [
    ("NDCNEW", "renewable share of generation (plant activity limits)",
     CURVE + ", carried by " + CTL + " rows 297 to 304 (Jamaica NDCNEW) into Stage 3; " + CFG + " sheet Electrical rows 8 to 22, 68 to 70, 74 to 77, 82 and 83 are replaced for PP techs from 2025 in Stage 3",
     "39.1 percent in 2030, 75.0 percent from 2035 to 2050 (solved)", "50 percent of net generation in 2030 and 63 percent in 2035", "JAM-01", "p.14", "A",
     "A Jamaica override with milestones {2030: 0.50, 2035: 0.63} would carry it (the interpolation function accepts several milestones). After 2035 NDC 3.0 is silent; IRP-2 gives 63.4 percent in 2035 (JAM-07 p.77)."),
    ("LTSNEW", "renewable share of generation (plant activity limits)",
     CURVE + ", carried by " + CTL + " rows 289 to 296 (Jamaica LTSNEW)",
     "39.1 percent (2030), 75.0 (2035), 83.0 (2040), 91.0 (2045), 99.0 (2050), solved", "at least 50 percent (2030), 65 (2035), 90 (2040), 95 (2045), 100 (2050)", "JAM-02", "p.14;p.15;p.55", "A",
     "Under the hub decision (LTS equals NDC through 2035) the 2030 and 2035 values would follow NDC 3.0 (50 and 63 percent); the LTS states 65 percent for 2035. LTSNEW is capped at 99 percent by design."),
    ("NDCNEW", "electricity system losses",
     CFG + " sheet SmartGrid row 2 (InputActivityRatio ELE_DIST, label LTS only, inactive); compiled Jamaica/JAM_ENERGY/B1_Output_Params/NDCNEW/InputActivityRatio.csv rows ELE_DIST (1.27 every year)",
     "ELE_DIST input 1.27 per unit, 21.3 percent of electricity entering distribution, same as BAU", "losses 17.7 percent of generation in 2030 and 16.45 percent in 2035 (ELE_DIST input about 1.215 and 1.197)", "JAM-01", "p.14", "A",
     "Needs NDCNEW rows for the existing SmartGrid InputActivityRatio lever. The model places all losses in distribution (ELE_TRANS 1.0); the conversion 1/(1 - loss share) assumes the NDC share is of electricity entering the grid."),
    ("LTSNEW", "electricity system losses",
     CFG + " sheet SmartGrid row 2 (label LTS); compiled B1_Output_Params/LTSNEW/InputActivityRatio.csv ELE_DIST",
     "21.3 percent every year", "no more than 21 percent (2030), 17 (2035), 14 (2040), 11 (2045), 8 (2050)", "JAM-02", "p.14;p.15;p.55", "A",
     "Table 1 (p.15) gives 11 percent for 2050, Table 4 (p.55) 8 percent. ELE_DIST input about 1.266, 1.205, 1.163, 1.124 and 1.087."),
    ("NDCNEW", "solar PV capacity build (IRP-2)",
     CFG + " sheet Electrical row 86 (TotalAnnualMinCapacityInvestment PPPVT, NDCNEW); row 88 for LTSNEW",
     "0 MW in 2025 and 2026, 99.83 MW (2027), 133 MW (2028), 90 MW per year 2029 to 2032; installed 470 MW in 2030 (solved)",
     "IRP-2 schedule: 90 MW per year 2025 to 2032, 34 MW in 2033, 84 MW in 2036, 90 MW in 2037 (installed 597 MW in 2030 and 811 MW in 2035)", "JAM-07", "p.66;p.77", "A",
     "NDC 3.0 cites IRP-2 as a data source (JAM-01 p.5). MinCapInvest is not patched by Stage 3, so this row reaches the solved capacity; generation still follows the share lever. 2025 and 2026 are past or committed years."),
    ("NDCNEW", "wind capacity build (IRP-2)",
     CFG + " sheet Electrical row 87 (MinCapInvest PPWNDON, NDCNEW); row 89 for LTSNEW",
     "60 MW per year 2027 to 2029, 21 MW in 2030; installed 303 MW in 2030 (solved)",
     "IRP-2 schedule: 60 MW per year 2025 to 2027, 21 MW in 2028, 57 MW in 2032, 25 MW in 2035 (installed 300 MW in 2030, 381 MW in 2035)", "JAM-07", "p.66;p.77", "A",
     "Installed wind 2030 already matches; the IRP timing is two years earlier and adds 82 MW after 2030."),
    ("NDCNEW", "battery storage capacity (IRP-2)",
     CFG + " sheet Electrical row 6 (MinCapInvest STOELE, label LTS only); no NDCNEW or LTSNEW row",
     "STOELE 40 MW to 2028, 102.5 MW (2030), 415 MW (2035), same in BAU", "264 MW of 2-hour storage by 2027, 328 MW by 2035, 493 MW by 2041", "JAM-07", "p.15;p.62;p.77", "A",
     "New NDCNEW and LTSNEW rows of an existing parameter."),
    ("LTSNEW", "heavy fuel oil plants",
     CTL + " row 291 (LTSNEW PPFOI) through the Stage 2 fossil rule (stage2_apply_v2.py, FOSSIL_DECLINE_RATE line 44); " + CFG + " sheet Electrical rows 41 and 84 (already 0 from 2027 but replaced by Stage 3)",
     "PPFOI generation 1.66 PJ and capacity 162 MW in 2035 (solved)", "100 percent of HFO capacity phased out by 2035", "JAM-02", "p.15;p.55", "A",
     "Falls on the hub boundary year: under the rule LTS equals NDC through 2035, the phase-out would start in 2036. NDC 3.0 is silent on HFO. The compiled inputs already phase HFO out from 2027 in all scenarios, so the conflict is between the B1 workbook and the controller."),
    ("LTSNEW", "fossil generation",
     CTL + " rows 290, 291 and 294 (LTSNEW PPDSL, PPFOI, PPNGS)",
     "fossil share 17.0 percent in 2040, 9.0 percent in 2045, 1.0 percent in 2050 (solved)", "100 percent of fossil fuel generation phased out by 2040", "JAM-02", "p.15;p.55", "A",
     "The same tables set 90 percent renewable for 2040 and 100 percent only for 2050; the hub must choose which milestone governs. The renewable share row above follows the percentages."),
    ("LTSNEW", "road vehicle fuel efficiency (emission-factor multiplier)",
     CFG + " sheet SmartGrid rows 16 and 18 (EmissionActivityRatio T5DSLTRO and T5GSLTRO, LTSNEW, Exact_Multiplier)",
     "multiplier 1 from 2025 (no improvement); BAU rows 13 and 14 have 0.952 in 2030 and 0.769 in 2050", "fleet fuel efficiency 15 percent better than 2020 by 2030 (multiplier 0.870) and truck fuel use 40 percent lower by 2050 (0.714)", "JAM-02", "p.14;p.15;p.61;p.62", "A",
     "The inactive LTS rows 11 and 12 (efficiency row 22) already hold these values. The lever changes only label CO2e_DETRN; a fuel-demand cut in Efficiency rows 256 to 264 would represent it fully (class B if the hub wants that)."),
    ("NDCNEW", "road vehicle fuel efficiency (emission-factor multiplier)",
     CFG + " sheet SmartGrid rows 15 and 17 (NDCNEW)", "multiplier 1 from 2025, below the BAU improvement (0.952 in 2030)", "documents silent", "JAM-01", "p.6;p.14", "",
     "NDC 3.0 names energy use and transport but gives no efficiency number. The policy scenario is less efficient than BAU from 2025 (known-limitation candidate, see notes)."),
    ("LTSNEW", "electric share of road transport",
     TCFG + " sheet Tech_Adoption rows 109, 112, 115 (private) and 117, 120, 123 (public), LTSNEW; carried into " + CFG + " sheet Efficiency rows 256 to 264 (E5TRO demand)",
     "10 percent of each group's activity in 2030, 50 percent in 2040, 90 percent in 2050", "private fleet 12 percent electric and public fleet 16 percent in 2030; at least 2,000 electric buses by 2040; 67 percent of the passenger fleet in 2050", "JAM-02", "p.14;p.15;p.62", "A",
     "Fleet shares must be converted to activity shares. The inactive LTS rows 37 to 72 hold 12, 39.5 and 67 percent. The energy model only sees the resulting E5TRO fuel demand, so the transport model must be re-run and the Efficiency rows refreshed. The 2025 milestones (8 and 10 percent) are history for the model."),
    ("NDCNEW", "electric share of road transport",
     TCFG + " sheet Tech_Adoption rows 74 to 97 (NDCNEW); " + CFG + " sheet Efficiency rows 240 to 248", "10 percent of each group in 2030, 30 percent from 2040 (heavy trucks 5, 15, 20 percent)", "documents silent", "JAM-01", "p.6;p.14", "",
     "NDC 3.0 covers transport emissions but states no electrification figure."),
    ("LTSNEW", "public transport and modal shift",
     TCFG + " sheet Mode_Shift row 6 (E6TDPASPUB, LTSNEW) and row 7 (E6TRNOMOT)", "shift 0.001 in 2030, 0.0011 in 2040 and 2050", "public transport 35 percent of urban passenger trips by 2030", "JAM-02", "p.61", "A",
     "The LTS presents it as an NDC goal that JAM-03 does not contain; pre-2035 value under the hub rule. The shift parameter must be derived from a modal share the model does not report."),
    ("LTSNEW", "alternative fuels and biofuel blending in transport",
     "Jamaica/JAM_ENERGY/B1_Base_Scenarios_Adj_Parallel_Jamaica.py lines 3702 to 3770 (BLOCK 10, Diesel_Techs and Gasoline_Techs lists empty)", "no biofuel or natural gas road fuel (E5TROBGS, E5TRONGS 0)", "alternative fuels 20 percent of transport by 2030", "JAM-02", "p.61", "B",
     "Needs the blend block filled (script change) or road gas and biofuel demand rows; the LTS does not split biofuels from natural gas vehicles."),
    ("LTSNEW", "residential wood, kerosene and charcoal stoves",
     CFG + " sheet Efficiency rows 172 (E5RESCHA), 175 (E5RESFIR), 177 (E5RESKER) and 174 (E5RESELE), LTSNEW", "firewood, charcoal and kerosene 5 percent below BAU in 2035", "all wood, kerosene and charcoal stoves replaced, with electric stoves, by 2035", "JAM-02", "p.15;p.67;p.69", "A",
     "Set the three fuels to 0 from 2035 and add the equivalent useful energy to residential electricity."),
    ("LTSNEW", "LPG use in buildings",
     CFG + " sheet Efficiency rows 178 (E5RESLPG) and 133 (E5COMLPG), LTSNEW", "5.669 PJ in 2050, 121 percent of the 2021 level", "10 percent of 2020 LPG use by 2050; LPG cookers halved by 2035", "JAM-02", "p.15;p.67;p.69", "A",
     "The text speaks of cookers, the tables of LPG use; the hub must decide whether commercial LPG is included."),
    ("LTSNEW", "solar water heating and efficient lighting",
     "none (no solar water heater or lighting technology in JAM_ENERGY)", "generic cuts in residential and commercial electricity demand (Efficiency rows 128 to 180)", "solar water heating in 60 percent of households by 2030 and 85 percent by 2050; 100 percent LED and T8 lighting by 2030", "JAM-02", "p.14;p.15;p.69", "B",
     "Could be approximated as demand cuts (class A) if the hub accepts a conversion from households to PJ."),
    ("NDCNEW", "cement clinker (process emissions)",
     "Jamaica/JAM_ENERGY technology PROD_CLK_TRAD, label CO2e_CEM (no alternative clinker technology; no B1_Scenario_Config.xlsx row)", "CO2e_CEM 0.325 Mt in 2035, equal in all scenarios", "cement measures cutting 40 ktCO2 in 2035 (growth of cement emissions limited to 11 percent)", "JAM-01", "p.2", "B",
     "The LTS sets clinker-to-cement ratios of 82 percent (2025) and 70 percent (2030) (JAM-02 p.14, p.74) for LTSNEW."),
    ("NDCNEW", "economy-wide emission target",
     "Jamaica/JAM_ENERGY/B1_Output_Params/NDCNEW/AnnualEmissionLimit.csv (empty); no Emission_Restriction sheet in " + CFG,
     "no limit; solved CO2e_sources 5.11 Mt (2030) and 4.19 Mt (2035), 14.2 and 33.1 percent below the model BAU",
     "16.3 percent (2030) and 16.9 percent (2035) below 2012, unconditional, energy and cement, forestry excluded; energy sector 5.8 Mt (2030) and 5.7 Mt (2035)", "JAM-01", "p.2;p.4;p.21", "C",
     "The energy model alone cannot carry a target that includes cement process emissions and, in its headline form, forestry. Its energy emissions already sit below the NDC energy levels (ratio 0.88 in 2030, 0.73 in 2035), so no energy limit is needed."),
    ("NDCNEW", "final demand per fuel (end-use efficiency)",
     CFG + " sheet Efficiency rows 75 to 127 (NDCNEW)", "about 2.5 percent below BAU in 2030 and 5 percent in 2035 for most fuels", "documents silent", "JAM-01", "p.6", "",
     "NDC 3.0 names energy use sub-sectors but gives no number."),
    ("NDCNEW", "renewable share after 2035",
     CURVE, "75 percent held 2035 to 2050", "documents silent", "JAM-01", "p.14", "", "NDC 3.0 runs to 2035."),
    ("LTSNEW", "electric share of freight trucks",
     TCFG + " sheet Tech_Adoption rows 127 (heavy trucks) and 132 (light freight), LTSNEW", "heavy trucks 5, 25, 50 percent and light freight 10, 50, 90 percent in 2030, 2040, 2050", "documents silent", "JAM-02", "p.15;p.61;p.62", "",
     "The LTS sets a 40 percent truck fuel-efficiency gain, not an electric share."),
]

COLS = ["country", "scenario", "lever", "model_rows", "current_value", "proposed_value", "source_id", "page", "class", "note"]


def main():
    with open(os.path.join(JOB, "parts", "proposals_JAM.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLS)
        counts = {}
        for p in P:
            w.writerow(["Jamaica"] + list(p))
            k = p[7] if p[7] else "documents silent"
            counts[k] = counts.get(k, 0) + 1
    print(len(P), counts)


if __name__ == "__main__":
    main()
