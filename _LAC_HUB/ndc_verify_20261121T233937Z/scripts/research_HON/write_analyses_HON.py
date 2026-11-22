"""Write JOB/analyses_HON.csv from the readings of the step D sources of Honduras.

Every value was read from JOB/downloads/HON/text_all/<id>/p<N>.txt (page given in the row).
Run check_analyses.py afterwards.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
FIELDS = ["source_id", "class", "model_or_method", "scenario", "scenario_definition", "indicator",
          "sector", "year", "value", "unit", "page", "note"]

ENME = "National electric mobility strategy targets (no model printed)"
CLG = "OSeMOSYS (ENDRCH-HON model; energy, transport and LULUCF)"
SEN = "MAED demand projection with least-cost generation expansion (SEN)"
GEM = "Green Economy Model (system dynamics, UNEP)"
CPAT = "Carbon Pricing Assessment Tool (CPAT, IMF and World Bank)"

D_TEND = "Tendencial: historical GDP per capita trends; power plants per PIEG 2024-2033 then cost-optimal; no extra mitigation"
D_ENDR = "ENDRCH: decarbonization measures (renewables, electrification, efficiency, firewood cut, storage, forest restoration)"
D_AMB = "ENDRC Ambicioso: variant of ENDRCH with a higher renewable generation share in 2050"
D_S1 = "Escenario I (reference): trend growth of transport and least-cost generation without structural change"
D_S2 = "Escenario II: high electric vehicle adoption with trend generation expansion"
D_S3 = "Escenario III: trend transport with structural change to renewable generation"
D_S4 = "Escenario IV: high electric vehicle adoption plus structural change to renewable generation"
D_BAU = "BAU: historical trends, no additional low-carbon or adaptation policy; includes COVID-19 and 2020 hurricane impacts"
D_EA45 = "EA 2045: net zero early action, 2030 goals agreed with government, net zero in 2045"
D_LA45 = "LA 2045: net zero late action, 2030 targets delayed 5 years, net zero in 2045"
D_EA50 = "EA 2050: same as EA 2045 to 2030, net zero in 2050"
D_LA50 = "LA 2050: 2030 targets delayed 5 years, net zero in 2050"
D_LOW = "Low: economy-wide upstream carbon charge from USD 5 per tCO2e in 2020 rising to USD 9 by 2030"
D_NDCE = "NDC Energy: carbon charge from USD 18 per tCO2e in 2020 rising to USD 33 by 2030"
D_PA = "Paris Aligned: carbon charge from USD 50 per tCO2e in 2020 rising to USD 93 by 2030 (Box 3.1 wording)"

R = []


def add(sid, cls, model, scen, sdef, ind, sector, year, value, unit, page, note=""):
    R.append(dict(zip(FIELDS, [sid, cls, model, scen, sdef, ind, sector, year, value, unit, page, note])))


# HON-21 ENME (official strategy, targets only)
add("HON-21", "official", ENME, "ENME target", "Electric vehicle targets of the national electric mobility strategy",
    "electric vehicle share of the national vehicle fleet", "transport", "2030", "3", "percent", "p.24",
    "Also on p.38 (Anexo III). HON-01 p.27 cites the ENME for 3 percent in 2030 and states 7.5 percent for 2035, a year the ENME does not state.")
add("HON-21", "official", ENME, "ENME target", "Electric vehicle targets of the national electric mobility strategy",
    "electric vehicle share of the national vehicle fleet", "transport", "2050", "15", "percent", "p.24",
    "Also on p.38. Share of the fleet (parque vehicular), not of sales.")

# HON-22 CLG ENDRCH-HON documentation (lead)
add("HON-22", "lead", CLG, "Tendencial", D_TEND, "", "all", "", "", "", "p.11",
    "Reference scenario; no number printed for it in the text, only figures.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "GHG emission reduction against Tendencial", "all modelled sectors (energy, transport, LULUCF)",
    "2050", "67", "percent", "p.8", "National result of the model; the absolute series is only in Figure 2 (p.9).")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "energy sector emission reduction against the peak projected in Tendencial",
    "energy", "2050", "47", "percent", "p.12", "Printed as approximately 47 percent.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "energy sector emission reduction against Tendencial (transport chapter text)",
    "energy (transport chapter)", "2050", "50", "percent", "p.16",
    "Printed as almost 50 percent. The transport chapter repeats the energy chapter text and tables; no transport-only result is printed.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "net saving against Tendencial (CAPEX, OPEX and externalities, cumulative to 2050)",
    "energy", "2050", "4.43", "billion USD", "p.12", "Printed as 4.43 mil millones de USD; repeated on p.17. Price year not stated.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "renewable share of generation (solar, wind, hydro), scenario assumption",
    "electricity", "2050", "70", "percent", "p.11", "Input assumption. Same text on p.16. Bioenergy is counted apart (10 percent).")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "natural gas share of generation, scenario assumption",
    "electricity", "2050", "20", "percent", "p.11", "Input assumption.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "bioenergy share of generation, scenario assumption",
    "electricity", "2050", "10", "percent", "p.11", "Input assumption; diesel, fuel oil and petroleum coke generation removed.")
add("HON-22", "lead", CLG, "ENDRC Ambicioso", D_AMB, "renewable share of generation (solar, wind, hydro), scenario assumption",
    "electricity", "2050", "75", "percent", "p.11", "Input assumption; natural gas 15 percent and bioenergy 10 percent in the same line.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "battery storage capacity added, scenario assumption",
    "electricity", "2033", "150", "MW", "p.11", "Printed as up to 2033: 150 MW in batteries.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "battery share of installed capacity, scenario assumption",
    "electricity", "2050", "5", "percent", "p.11", "")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "firewood consumption reduction against Tendencial, scenario assumption",
    "residential", "2030", "39", "percent", "p.12", "Same as the NDC firewood goal; full switch to electricity and LPG for cooking by 2040.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "electrification of end uses against Tendencial, scenario assumption",
    "residential", "2050", "60", "percent", "p.12", "Commercial also 60 percent in the same list.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "electrification of end uses against Tendencial, scenario assumption",
    "industry", "2050", "40", "percent", "p.12", "Agriculture 25 percent in the same list.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "net LULUCF removals", "LULUCF", "2050", "6617", "Gg CO2e", "p.21",
    "Printed as captura neta de 6,617 Gg CO2e.")
add("HON-22", "lead", CLG, "Tendencial", D_TEND, "net LULUCF removals", "LULUCF", "2050", "3494", "Gg CO2e", "p.21",
    "Printed as 3,494 Gg CO2e.")
add("HON-22", "lead", CLG, "ENDRCH", D_ENDR, "forest cover restored, scenario assumption", "LULUCF", "2030", "1", "million ha", "p.20",
    "Reforestation of 0.06 Mha per year between 2025 and 2030 in the same section.")

# HON-23 SEN Prospectiva electromovilidad (official)
add("HON-23", "official", SEN, "Escenario I", D_S1, "electric motorcycle share", "transport", "2030", "3", "percent", "p.31",
    "Text on p.31: 3 percent of motorcycles, 0.5 percent of light vehicles and 0.1 percent of large buses electric by 2030.")
add("HON-23", "official", SEN, "Escenario I", D_S1, "electric motorcycle share", "transport", "2050", "5", "percent", "p.31",
    "Text on p.31: 5 percent of motorcycles and 2 percent of light vehicles by 2050. Base of share (stock or sales) not stated in the text.")
add("HON-23", "official", SEN, "Escenario II", D_S2, "electric motorcycle share", "transport", "2030", "15", "percent", "p.34",
    "Text on p.34: 15 percent of motorcycles, 10 percent of light vehicles, 10 percent of large buses by 2030.")
add("HON-23", "official", SEN, "Escenario II", D_S2, "electric motorcycle share", "transport", "2050", "40", "percent", "p.34",
    "Text on p.34: 40 percent of motorcycles and of cars (turismos), 30 percent of pick ups and jeeps, 40 percent of large buses by 2050. Escenario IV uses the Escenario II transport assumptions (p.39).")
add("HON-23", "official", SEN, "Escenario II", D_S2, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2030", "-6", "percent", "p.53", "Tabla 11.")
add("HON-23", "official", SEN, "Escenario II", D_S2, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2050", "-19", "percent", "p.53", "Tabla 11.")
add("HON-23", "official", SEN, "Escenario III", D_S3, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2030", "-17", "percent", "p.53", "Tabla 11.")
add("HON-23", "official", SEN, "Escenario III", D_S3, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2050", "-40", "percent", "p.53", "Tabla 11.")
add("HON-23", "official", SEN, "Escenario IV", D_S4, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2030", "-24", "percent", "p.53", "Tabla 11.")
add("HON-23", "official", SEN, "Escenario IV", D_S4, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2035", "-44", "percent", "p.53", "Tabla 11.")
add("HON-23", "official", SEN, "Escenario IV", D_S4, "CO2 emission change against Escenario I (transformation and transport)",
    "transformation and transport", "2050", "-56", "percent", "p.53", "Tabla 11. Absolute series only in Grafica 37 (p.53).")
add("HON-23", "official", SEN, "Escenario I", D_S1, "average cost of electricity production 2019-2050",
    "electricity", "2019-2050", "132.5", "USD 2018 per MWh", "p.54", "Tabla 12.")
add("HON-23", "official", SEN, "Escenario IV", D_S4, "average cost of electricity production 2019-2050",
    "electricity", "2019-2050", "140.2", "USD 2018 per MWh", "p.54", "Tabla 12; 5.8 percent above Escenario I.")
add("HON-23", "official", SEN, "Escenario I", D_S1, "cumulative generation expansion investment to 2030",
    "electricity", "2030", "3600", "million USD 2018", "p.53", "Printed as approximately 3,600 millones de USD 2018.")
add("HON-23", "official", SEN, "Escenario IV", D_S4, "additional cumulative generation investment against Escenario I",
    "electricity", "2050", "1300", "million USD 2018", "p.53", "Printed as approximately 1,300 millones (30 percent) above Escenario I; 177 million (5 percent) above in 2030.")

# HON-24 UNEP Green Economic Recovery (external)
add("HON-24", "external", GEM, "BAU", D_BAU, "total GHG emissions", "all", "2022", "14.7", "Mt CO2e", "p.49",
    "Text says emissions rise 58 percent to 2050, which does not match 14.7 to 54.8; recorded as printed.")
add("HON-24", "external", GEM, "BAU", D_BAU, "total GHG emissions", "all", "2050", "54.8", "Mt CO2e", "p.49", "")
add("HON-24", "external", GEM, "EA 2045", D_EA45, "emission reduction against BAU", "all", "2030", "19.1", "percent", "p.49",
    "Printed as the maximum decrease to 2030, shared by EA 2045 and LA 2045.")
add("HON-24", "external", GEM, "LA 2045", D_LA45, "emission reduction against BAU", "all", "2030", "19.1", "percent", "p.49",
    "Same sentence as the EA 2045 row.")
add("HON-24", "external", GEM, "LA 2050", D_LA50, "emission reduction against BAU", "all", "2030", "14.7", "percent", "p.49",
    "Printed as the minimum decrease to 2030.")
add("HON-24", "external", GEM, "EA 2045", D_EA45, "emissions below BAU", "all", "2050", "111.4", "percent", "p.50",
    "Figure 10 label; also -39.79 million t CO2. Above 100 percent means net negative emissions.")
add("HON-24", "external", GEM, "EA 2050", D_EA50, "emissions below BAU", "all", "2050", "101.1", "percent", "p.50", "Figure 10 label.")
add("HON-24", "external", GEM, "LA 2045", D_LA45, "emissions below BAU", "all", "2050", "116.0", "percent", "p.50", "Figure 10 label.")
add("HON-24", "external", GEM, "LA 2050", D_LA50, "emissions below BAU", "all", "2050", "101.5", "percent", "p.50",
    "Figure 10 label; also -36.10 million t CO2.")
add("HON-24", "external", GEM, "EA 2050", D_EA50, "real GDP", "economy", "2050", "26.95", "billion USD", "p.51",
    "14.8 percent above BAU; BAU 23.4 billion USD in 2050 (same page). Price year not stated.")
add("HON-24", "external", GEM, "EA 2045", D_EA45, "additional jobs against BAU", "economy", "2050", "179194", "jobs", "p.51",
    "EA 2050: 178,840 additional jobs (same page).")

# HON-25 World Bank CCDR (external)
add("HON-25", "external", CPAT, "Low", D_LOW, "CO2 emission reduction against BAU", "energy (fossil fuel CO2)", "2030", "3", "percent",
    "p.38", "Box 3.1; 0.8 metric ton as printed (unit evidently Mt).")
add("HON-25", "external", CPAT, "NDC Energy", D_NDCE, "CO2 emission reduction against BAU", "energy (fossil fuel CO2)", "2030", "9",
    "percent", "p.38", "Box 3.1; 2.6 metric tons as printed. Box says consistent with the NDC; p.13 instead says an ambitious carbon price achieves the NDC 23 percent energy cut.")
add("HON-25", "external", CPAT, "Paris Aligned", D_PA, "CO2 emission reduction against BAU", "energy (fossil fuel CO2)", "2030", "20",
    "percent", "p.38", "Box 3.1; 5.7 metric tons as printed. Footnote 12 on p.13 gives USD 5 to 9 per ton for this scenario, which contradicts the box.")
add("HON-25", "external", CPAT, "NDC Energy", D_NDCE, "carbon charge", "economy", "2030", "33", "USD per tCO2e", "p.38", "Real terms.")
add("HON-25", "external", CPAT, "Paris Aligned", D_PA, "additional revenue", "economy", "2030", "2.69", "percent of GDP", "p.38",
    "USD 1 billion per annum.")


def main():
    out = os.path.join(JOB, "analyses_HON.csv")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in R:
            w.writerow(r)
    print("wrote", out, len(R))


if __name__ == "__main__":
    main()
