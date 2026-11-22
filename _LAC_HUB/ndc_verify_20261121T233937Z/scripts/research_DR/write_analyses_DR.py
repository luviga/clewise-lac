"""Write JOB/analyses_DR.csv from the readings of the step D sources of the Dominican Republic.

Every value was read from JOB/downloads/DR/text_all/<id>/p<N>.txt (page given in the row).
Check with scripts/research_HON/check_analyses.py DR.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
FIELDS = ["source_id", "class", "model_or_method", "scenario", "scenario_definition", "indicator",
          "sector", "year", "value", "unit", "page", "note"]

MANAGE = "MANAGE computable general equilibrium model with sector models (World Bank)"
EPM = "Electricity Planning Model (EPM, World Bank capacity expansion and dispatch)"
IDB = "OSeMOSYS-type power model with Robust Decision Making, 1,001 futures (CLG for IDB)"
CLG = "OSeMOSYS-RD with Robust Decision Making (202 futures)"
DDP = "Narrative summary of the draft LT-LEDS and of DR-23"
PEN = "Energy prospective of the Plan Energetico Nacional 2025-2038 (summary in a CNE bulletin)"

D_NP = "NP / BAU: least-cost power plan without emission constraint; demand from the 2022-2036 national energy plan; minimal EVs"
D_NDC = "NDC2030: NP plus NDC goals (3.9 Mt CO2e below NP in 2030), 25 percent RE by 2025 and 30 percent by 2030, 9.3 percent EV fleet in 2050"
D_NZP = "NZP2050: NDC2030 plus net zero power sector emissions by 2050, ambitious efficiency, 70 percent EV fleet in 2050"
D_AMB = "Ambitious scenario of the CCDR macro analysis (power, transport and AFOLU measures)"
D_BASE = "Base: trend expansion of the SENI"
D_REF = "Referencia: expansion per the 2022 national energy plan"
D_GAS = "Gas natural: coal plants converted to natural gas"
D_REN = "Renovables: coal plants replaced by wind and solar with storage"
D_TEND = "Tendencial: historical patterns and commitments already in force"
D_LTS = "Estrategia (LTS): deep decarbonization of all sectors to 2050 (generation mix, electrification, modal shift, AFOLU, IPPU, waste)"
D_PTEN = "Escenario tendencial of the PEN 2025-2038 energy prospective"
D_PALT = "Escenario alternativo of the PEN 2025-2038 (the plan proposes moving towards it: infrastructure, efficiency, renewables, storage)"

R = []


def add(sid, cls, model, scen, sdef, ind, sector, year, value, unit, page, note=""):
    R.append(dict(zip(FIELDS, [sid, cls, model, scen, sdef, ind, sector, year, value, unit, page, note])))


# DR-21 World Bank CCDR main report (external)
add("DR-21", "external", MANAGE, "Ambitious", D_AMB, "accumulated emission reductions, combined power and transport",
    "power and transport", "2030", "14", "Mt CO2e", "p.11", "Table ES-1; same table as Table 1 on p.52.")
add("DR-21", "external", MANAGE, "Ambitious", D_AMB, "accumulated emission reductions, combined power and transport",
    "power and transport", "2050", "221", "Mt CO2e", "p.11", "Table ES-1.")
add("DR-21", "external", MANAGE, "Ambitious", D_AMB, "accumulated emission reductions, power", "electricity", "2050", "207",
    "Mt CO2e", "p.11", "Table ES-1. The transport and AFOLU rows extract with shifted columns and are not recorded.")
add("DR-21", "external", MANAGE, "Ambitious", D_AMB, "investment costs, combined power and transport", "power and transport",
    "2050", "38037", "million USD 2022", "p.11", "Table ES-1; present value, 6 percent discount rate.")
add("DR-21", "external", EPM, "NDC2030", D_NDC, "total discounted power system costs", "electricity", "2050", "34.7",
    "billion USD", "p.46", "Cumulative 2023-2050 (Annex 3, DR-22 p.16).")
add("DR-21", "external", EPM, "NZP2050", D_NZP, "total discounted power system costs", "electricity", "2050", "51.0",
    "billion USD", "p.46", "")
add("DR-21", "external", EPM, "NDC2030", D_NDC, "power investment, net present value", "electricity", "2050", "12.0",
    "billion USD", "p.46", "Annex 3 (DR-22 p.16) prints 11.9 for the same quantity.")
add("DR-21", "external", EPM, "NZP2050", D_NZP, "power investment, net present value", "electricity", "2050", "25.5",
    "billion USD", "p.46", "")
add("DR-21", "external", EPM, "NDC2030", D_NDC, "combined solar and wind capacity", "electricity", "2050", "16000", "MW",
    "p.44", "Printed as 16,000 MW (16 GW); 40,000 MW in NZP2050; about 800 MW today.")
add("DR-21", "external", EPM, "NZP2050", D_NZP, "combined solar and wind capacity", "electricity", "2050", "40000", "MW",
    "p.44", "Printed as 40,000 MW (40 GW).")

# DR-22 World Bank CCDR Annex 3 power (external)
for scen, d, page, vals in (("NP", D_NP, "p.15", ("9.9", "12.2", "14.3")),
                            ("NDC2030", D_NDC, "p.16", ("6.0", "7.4", "8.7")),
                            ("NZP2050", D_NZP, "p.17", ("6.9", "3.5", "0.0"))):
    for y, v in zip(("2030", "2040", "2050"), vals):
        add("DR-22", "external", EPM, scen, d, "GHG emissions from grid electricity generation", "electricity", y, v,
            "Mt CO2e", page, "Scenario results table; columns extract out of order. Row identified by demand times "
            "emission factor on the same page and by the 3.9 Mt NDC cut against NP in 2030 (p.14). 2022: 11.1.")
add("DR-22", "external", EPM, "NZP2050", D_NZP, "renewable share of generation", "electricity", "2050", "67", "percent", "p.3",
    "Printed as Renewables share 2050: 67%, up from 16% today. Same on p.4.")
add("DR-22", "external", EPM, "NP", D_NP, "investment needs for new electricity system capex, cumulative 2023-2050",
    "electricity", "2050", "8.8", "billion USD 2022", "p.15", "Scenario results table.")
add("DR-22", "external", EPM, "NDC2030", D_NDC, "investment needs for new electricity system capex, cumulative 2023-2050",
    "electricity", "2050", "11.9", "billion USD 2022", "p.16", "Main report p.46 prints 12.0.")
add("DR-22", "external", EPM, "NZP2050", D_NZP, "investment needs for new electricity system capex, cumulative 2023-2050",
    "electricity", "2050", "25.5", "billion USD 2022", "p.17", "Discounted; headline on p.3.")
add("DR-22", "external", EPM, "NP", D_NP, "battery storage capacity", "electricity", "2050", "1.1", "GW", "p.8", "")
add("DR-22", "external", EPM, "NDC2030", D_NDC, "battery storage capacity", "electricity", "2050", "2.4", "GW", "p.8", "")
add("DR-22", "external", EPM, "NZP2050", D_NZP, "battery storage capacity", "electricity", "2050", "11.9", "GW", "p.8", "")
add("DR-22", "external", EPM, "NZP2050", D_NZP, "offshore wind capacity", "electricity", "2050", "8.5", "GW", "p.7", "")
add("DR-22", "external", EPM, "NP", D_NP, "electric vehicle share of the fleet, scenario assumption", "transport", "2050", "8",
    "percent", "p.14", "Scenario table: 2 percent EV by 2030 and 8 percent by 2050. p.19 says 2.6 percent by 2030 and 8.0 percent by 2050.")
add("DR-22", "external", EPM, "NDC2030", D_NDC, "electric vehicle share of the fleet, scenario assumption", "transport", "2030",
    "7.2", "percent", "p.14", "")
add("DR-22", "external", EPM, "NDC2030", D_NDC, "electric vehicle share of the fleet, scenario assumption", "transport", "2050",
    "9.3", "percent", "p.14", "")
add("DR-22", "external", EPM, "NZP2050", D_NZP, "electric vehicle share of the fleet, scenario assumption", "transport", "2030",
    "15", "percent", "p.14", "")
add("DR-22", "external", EPM, "NZP2050", D_NZP, "electric vehicle share of the fleet, scenario assumption", "transport", "2050",
    "70", "percent", "p.14", "")

# DR-23 IDB monograph by CLG authors (lead)
add("DR-23", "lead", IDB, "Base", D_BASE, "SENI GHG emissions", "electricity", "2050", "23.7", "Mt CO2e", "p.23",
    "Average of futures; 13.6 Mt CO2e in 2021 (same page).")
add("DR-23", "lead", IDB, "Referencia", D_REF, "SENI GHG emissions", "electricity", "2050", "20.5", "Mt CO2e", "p.23", "")
add("DR-23", "lead", IDB, "Renovables", D_REN, "SENI GHG emissions", "electricity", "2050", "11.2", "Mt CO2e", "p.23", "")
add("DR-23", "lead", IDB, "Renovables", D_REN, "non-conventional renewable share of generation", "electricity", "2050", "55",
    "percent", "p.5", "Printed as around 55 percent; p.20 says scenarios with more than 55 percent are technically feasible.")
add("DR-23", "lead", IDB, "Renovables", D_REN, "cumulative avoided emissions against Base", "electricity", "2050", "140",
    "Mt CO2e", "p.22", "Also p.5. Gas natural avoids about three quarters of this, Referencia less than a third.")
add("DR-23", "lead", IDB, "Renovables", D_REN, "avoided emissions against Base", "electricity", "2030", "5", "Mt CO2e", "p.22",
    "Printed as equal to 40 percent of the NDC reduction; Gas natural 25 percent and Referencia 4 percent.")
add("DR-23", "lead", IDB, "Renovables", D_REN, "net benefit against Base, cumulative to mid-century", "electricity", "2050",
    "2700", "million USD", "p.20", "Discounted to 2023 at 5.04 percent.")
add("DR-23", "lead", IDB, "Gas natural", D_GAS, "net benefit against Base, cumulative to mid-century", "electricity", "2050",
    "2300", "million USD", "p.21", "")
add("DR-23", "lead", IDB, "Referencia", D_REF, "net benefit against Base, cumulative to mid-century", "electricity", "2050",
    "1300", "million USD", "p.21", "Printed as US$ 1 300 without the word millones.")
add("DR-23", "lead", IDB, "Renovables", D_REN, "additional generation capex against Base", "electricity", "2050", "3300",
    "million USD", "p.20", "Plus USD 1,000 million storage capex; p.5 gives 4,600 million total renewable investment.")
add("DR-23", "lead", IDB, "Renovables", D_REN, "cumulative additional direct jobs", "electricity", "2050", "160000", "jobs",
    "p.24", "Printed as almost 160 000.")

# DR-24 CLG LTS-RD documentation (lead)
add("DR-24", "lead", CLG, "Tendencial", D_TEND, "national GHG emissions", "all", "2018", "28.2", "Mt CO2e", "p.9", "")
add("DR-24", "lead", CLG, "Tendencial", D_TEND, "national GHG emissions", "all", "2050", "75", "Mt CO2e", "p.9",
    "Printed as close to 75 MtCO2e; range of tendencial futures 60 to 100 Mt (p.10).")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "national GHG emissions", "all", "2050", "17.4", "Mt CO2e", "p.9",
    "Range of strategy futures 2 to 32 Mt (p.10).")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "national GHG emission reduction against Tendencial", "all", "2050", "76",
    "percent", "p.9", "Printed as approximately 76 percent.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "net benefit against Tendencial, upper percentile futures, cumulative 2024-2050",
    "all", "2050", "52", "billion USD", "p.10", "Range 52 to 225 billion current USD; this row is the lower bound.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "wind onshore share of generation, scenario assumption", "electricity",
    "2050", "30", "percent", "p.18", "Mix: wind onshore 30, offshore 7, utility solar 25, distributed solar 15, hydro 3, natural gas 20 percent.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "natural gas share of generation, scenario assumption", "electricity",
    "2050", "20", "percent", "p.18", "")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "technical distribution losses, scenario assumption", "electricity",
    "2050", "8", "percent", "p.18", "")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "electric share of cars, SUVs, motorcycles and buses, scenario assumption",
    "transport", "2050", "70", "percent", "p.19", "Freight 50 percent; 2035: 5 percent motorcycles, 10 percent cars, SUVs, taxis and freight, 30 percent buses.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "public transport modal shift, scenario assumption", "transport", "2050",
    "20", "percent", "p.19", "Active mobility 10 percent; 2035 values 10 and 5 percent.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "emission reduction against Tendencial, energy", "energy", "2050", "22.6",
    "Mt CO2e", "p.19", "")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "emission reduction against Tendencial, transport", "transport", "2050",
    "5.4", "Mt CO2e", "p.19", "")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "net benefit against Tendencial, energy and transport", "energy and transport",
    "2050", "46", "billion USD", "p.19", "Printed as 46 miles de millones de dolares.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "emission reduction against Tendencial, AFOLU", "AFOLU", "2050", "76.2",
    "percent", "p.25", "Removals up 23.6 percent in 2050; saving 6.2 billion USD.")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "emission reduction against Tendencial, IPPU", "IPPU", "2050", "8.25",
    "Mt CO2e", "p.31", "")
add("DR-24", "lead", CLG, "Estrategia (LTS)", D_LTS, "emission reduction against Tendencial, waste", "waste", "2050", "6.8",
    "Mt CO2e", "p.37", "Cost reduction 5,300 million discounted USD 2024-2050.")

# DR-25 DDP 2025 chapter by CLG (lead)
add("DR-25", "lead", DDP, "Draft LT-LEDS", "Draft long-term low-emission development strategy, pending official launch",
    "", "", "", "", "", "p.2", "States the LT-LEDS is drafted with World Bank Group support and CLG technical support and is still pending official launch.")
add("DR-25", "lead", DDP, "Renewable electricity (DR-23)", D_REN, "additional investment by 2050 against a baseline", "electricity",
    "2050", "3.3", "billion USD", "p.2", "DR-23 p.5 gives 4,600 million total renewable investment; 3.3 billion matches its generation capex alone (p.20).")

# DR-26 CNE bulletin with the PEN summary (official)
add("DR-26", "official", PEN, "Escenario tendencial", D_PTEN, "energy demand", "all energy", "2038", "12248", "ktep", "p.28",
    "Infographic; 2022 starting point 7,727 ktep. Year read from the heading two possible paths to 2038.")
add("DR-26", "official", PEN, "Escenario tendencial", D_PTEN, "imports share of total supply", "all energy", "2038", "69.37",
    "percent", "p.28", "Infographic; 82.69 percent in 2022.")
add("DR-26", "official", PEN, "Escenario alternativo", D_PALT, "energy demand", "all energy", "2038", "13540", "ktep", "p.29",
    "Infographic. Higher demand than tendencial with lower energy intensity (2.18 against 2.47 tep per DOP as printed).")
add("DR-26", "official", PEN, "Escenario alternativo", D_PALT, "imports share of total supply", "all energy", "2038", "69.75",
    "percent", "p.29", "Infographic.")
add("DR-26", "official", PEN, "PEN 2025-2038", "Generation expansion of the PEN: meet demand, 25 percent RE by 2025 and 30 percent by 2030, least cost, gas as transition fuel",
    "renewable investment needed to reach at least 30 percent renewables", "electricity", "2030", "5400", "million USD", "p.32",
    "USD 2,900 million more for 2031-2038 to keep that level.")
add("DR-26", "official", PEN, "PEN 2025-2038", "Generation expansion of the PEN: meet demand, 25 percent RE by 2025 and 30 percent by 2030, least cost, gas as transition fuel",
    "maximum electricity demand", "electricity", "2038", "7595", "MW", "p.37", "3,940 MW in 2025 and 5,070 MW in 2030 in the same graphic.")


def main():
    out = os.path.join(JOB, "analyses_DR.csv")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in R:
            w.writerow(r)
    print("wrote", out, len(R))


if __name__ == "__main__":
    main()
