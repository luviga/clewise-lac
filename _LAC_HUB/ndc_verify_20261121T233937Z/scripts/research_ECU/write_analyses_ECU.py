"""Write JOB/analyses_ECU.csv from the readings of the step D sources of Ecuador.

Every value was read from JOB/downloads/ECU/text_all/<id>/p<N>.txt (page given in the row).
Check with scripts/research_HON/check_analyses.py ECU.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
FIELDS = ["source_id", "class", "model_or_method", "scenario", "scenario_definition", "indicator",
          "sector", "year", "value", "unit", "page", "note"]

PNMUS = "National urban mobility policy (institutional targets, no model)"
ELENA_WB = "ELENA integrated assessment model (MESSAGE platform), run for the World Bank CCDR"
ELENA_IDB = "ELENA integrated assessment model (MESSAGE platform), USFQ for the IDB"
CA = "Downscaled IPCC SR1.5 global cost-effective pathways (Climate Analytics)"
AFD = "Interview on the PLANMICC modelling (OSeMOSYS-Ecuador with Robust Decision Making)"

D_BAU = "BAU: recent sectoral structure kept, Electricity Master Plan (PME) to 2030, then least-cost to 2050"
D_NDCU = "NDCu: unconditional NDC assumptions to 2025, then similar mitigation ambition optimized to 2050"
D_NDCC = "NDCc: conditional NDC assumptions to 2025, then similar mitigation ambition optimized to 2050"
D_NZ = "NZ: unconditional NDC path to 2025, then linear CO2 path to net zero CO2 in 2050 with more ambitious forest trajectories"
D_APS = "Politicas Anunciadas (APS): main announced energy expansion policies (IEA WEO 2021 inspired)"
D_SDS = "Desarrollo Sostenible (SDS): decarbonization driven by a carbon price in ELENA"
D_NZE = "Neto Cero 2050 (NZE): carbon price path to near net zero CO2 in 2050, modal shift, occupancy and distance cuts"
D_15 = "1.5C compatible range for total GHG excluding LULUCF, downscaled from IPCC SR1.5 pathways (BECCS only)"
D_NDC1 = "First NDC target as read by Climate Analytics (conditional on international support)"

R = []


def add(sid, cls, model, scen, sdef, ind, sector, year, value, unit, page, note=""):
    R.append(dict(zip(FIELDS, [sid, cls, model, scen, sdef, ind, sector, year, value, unit, page, note])))


# ECU-21 PNMUS (official policy; D1 document)
add("ECU-21", "official", PNMUS, "PNMUS 2023-2030", "National urban mobility policy with institutional goals for 2030",
    "", "transport", "", "", "", "p.57",
    "Goals are institutional (for example 75 percent of local governments with a sustainable urban mobility plan by 2030, goal B.1.1); no modal share, fleet or emission quantity a model could take.")

# ECU-22 World Bank CCDR Ecuador (external)
add("ECU-22", "external", ELENA_WB, "BAU", D_BAU, "total installed power capacity", "electricity", "2050", "17.7", "GW", "p.52",
    "8.4 GW and 37.4 TWh in 2020 (p.51).")
add("ECU-22", "external", ELENA_WB, "BAU", D_BAU, "renewable share of power generation", "electricity", "2050", "99", "percent",
    "p.52", "Printed as a 99 percent renewables-based power generation system by 2050 if PME and model investments materialize; hydropower 73 percent of installed capacity.")
add("ECU-22", "external", ELENA_WB, "NZ", D_NZ, "electricity generation", "electricity", "2050", "112.9", "TWh", "p.52", "")
add("ECU-22", "external", ELENA_WB, "NZ", D_NZ, "total installed power capacity", "electricity", "2050", "30.3", "GW", "p.52", "")
add("ECU-22", "external", ELENA_WB, "NZ", D_NZ, "solar share of generation", "electricity", "2050", "12.8", "percent", "p.52", "")
add("ECU-22", "external", ELENA_WB, "NDCc", D_NDCC, "solar share of generation", "electricity", "2050", "8", "percent", "p.52", "")
add("ECU-22", "external", ELENA_WB, "NZ", D_NZ, "CO2 emissions of energy and transport", "energy and transport", "2050", "2.6",
    "Mt CO2e", "p.52", "Balanced by forest removals and some BECCS to reach net zero CO2.")
add("ECU-22", "external", ELENA_WB, "NZ", D_NZ, "bus share of passenger travel", "transport", "2050", "63", "percent", "p.53", "")
add("ECU-22", "external", ELENA_WB, "BAU", D_BAU, "electric share of cars", "transport", "2050", "3", "percent", "p.53",
    "Printed as up to 3 percent of cars and 13 percent of buses converted to electricity by 2050 under current trends.")
add("ECU-22", "external", ELENA_WB, "BAU", D_BAU, "electric share of buses", "transport", "2050", "13", "percent", "p.53", "")
add("ECU-22", "external", ELENA_WB, "NDCu", D_NDCU, "", "", "", "", "", "p.88",
    "Scenario defined (p.88); results only in Figure 3.7 (p.47), no printed number.")

# ECU-23 IDB technical note 3000 (external)
add("ECU-23", "external", ELENA_IDB, "Politicas Anunciadas (APS)", D_APS, "CO2 emissions of energy and LULUCF", "energy and LULUCF",
    "2050", "97.2", "Mt CO2", "p.20", "Printed as 97,2 MtCO2/ano; 88.9 Mt in 2015. CO2 only.")
add("ECU-23", "external", ELENA_IDB, "Desarrollo Sostenible (SDS)", D_SDS, "CO2 emissions of energy and LULUCF", "energy and LULUCF",
    "2050", "24", "Mt CO2", "p.20", "Trend reaches net zero in 2070.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "CO2 emissions of energy and LULUCF", "energy and LULUCF",
    "2050", "1.7", "Mt CO2", "p.20", "Printed as 1,7 MtCO2/ano.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "total GHG emissions", "all modelled", "2050", "36", "Mt CO2e",
    "p.19", "Printed as cerca de 36 MtCO2e including other gases.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "electricity generation", "electricity", "2050", "105", "TWh",
    "p.15", "SDS 98 TWh.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "hydropower share of generation", "electricity", "2050", "66",
    "percent", "p.16", "Biomass with CCS 10 percent and non-conventional renewables 18 percent.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "alternative propulsion share of the car fleet", "transport",
    "2050", "69", "percent", "p.16", "APS and SDS: 3 percent.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "alternative propulsion share of the bus fleet", "transport",
    "2050", "71", "percent", "p.17", "Heavy trucks reach only 10 percent even in decarbonization scenarios.")
add("ECU-23", "external", ELENA_IDB, "Neto Cero 2050 (NZE)", D_NZE, "non-motorized share of trips, scenario assumption", "transport",
    "2050", "10", "percent", "p.10", "")

# ECU-24 Climate Analytics (external)
add("ECU-24", "external", CA, "1.5C compatible", D_15, "maximum total GHG emissions excluding LULUCF", "all excl. LULUCF", "2030",
    "37", "Mt CO2e", "html", "Equal to 46 percent below 2015; 53 Mt in 2025.")
add("ECU-24", "external", CA, "1.5C compatible", D_15, "total GHG emissions excluding LULUCF", "all excl. LULUCF", "2050", "13",
    "Mt CO2e", "html", "Printed as around 13 MtCO2e, 81 percent below 2015.")
add("ECU-24", "external", CA, "First NDC", D_NDC1, "emission level excluding LULUCF", "all excl. LULUCF", "2025", "61", "Mt CO2e",
    "html", "Printed as 20.9 percent below BAU, conditional. The same page later says 63 MtCO2e in 2025; it reads the first NDC, not the second NDC in force.")

# ECU-25 AFD interview (lead)
add("ECU-25", "lead", AFD, "PLANMICC scenarios", "OSeMOSYS-Ecuador with Robust Decision Making used to build the PLANMICC",
    "", "", "", "", "", "html", "No numbers. States that the Costa Rican team led by Jairo Quiros built the PLANMICC model in OSeMOSYS.")


def main():
    out = os.path.join(JOB, "analyses_ECU.csv")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in R:
            w.writerow(r)
    print("wrote", out, len(R))


if __name__ == "__main__":
    main()
