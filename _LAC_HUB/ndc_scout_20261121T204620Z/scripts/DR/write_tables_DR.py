"""Write the DR source register, pending list, targets and projections tables.

All values were read by hand from the page text cache (downloads/DR/text/<id>/p<N>.txt)
or, for p.44 to p.61 of DR-01, from page images. Run from the job folder:
    python -I scripts/DR/write_tables_DR.py
"""
import csv
import os

JOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def write(path, header, rows):
    full = os.path.join(JOB, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            if len(r) != len(header):
                raise ValueError(f"{path}: row has {len(r)} fields, header {len(header)}: {r[:3]}")
            w.writerow(r)
    print(path, len(rows))


# ---------------------------------------------------------------- sources
SRC_H = ["id", "country", "kind", "URL", "title", "publisher", "date", "accessed", "SHA-256", "file", "pages", "language"]
SRC = [
    ["DR-01", "Dominican Republic", "NDC",
     "https://cdn.climatepolicyradar.org/navigator/DOM/2026/dominican-republic-nationally-determined-contribution-ndc3-0_e78f1541b0c38f4dd92dca4e986bb508.pdf (copy of https://unfccc.int/sites/default/files/2026-06/NDC_3.0_Versio%CC%81n%20Final_1303_conAnexos_REV_2.pdf)",
     "Contribucion Nacionalmente Determinada de Republica Dominicana (2025), NDC 3.0 RD-2025, with annexes",
     "Gobierno de la Republica Dominicana (CNCCMC, MMARN, Ministerio de Hacienda y Economia)",
     "2026-06-09 (UNFCCC upload date per Climate Policy Radar record; document titled 2025)", "2026-11-21",
     "2636efb7ca69e74a99fb849e4d4dd1f061fce27499e5150ed3ffbc8ecac5cfab", "downloads/DR/DR_NDC3_2026.pdf", "222", "Spanish"],
    ["DR-02", "Dominican Republic", "NDC",
     "https://cdn.climatepolicyradar.org/navigator/DOM/1900/dominican-republic-first-ndc-updated-submission_a6f888949eb58d908f8617b998863eae.pdf (copy of https://unfccc.int/sites/default/files/NDC/2022-06/Dominican%20Republic%20First%20NDC%20%28Updated%20Submission%29.pdf)",
     "Contribucion Nacionalmente Determinada 2020, NDC-RD 2020 (first NDC, updated submission)",
     "Gobierno de la Republica Dominicana",
     "2020-12-29 (Climate Policy Radar record; the BTR1 says published 28 December 2020)", "2026-11-21",
     "affe7f74c2416b6fa22c1aac83d5bf59bc8c7542ac3748e403b4aeb7b92b1f66", "downloads/DR/DR_NDC_2020_update.pdf", "167", "Spanish"],
    ["DR-03", "Dominican Republic", "NDC",
     "https://cdn.climatepolicyradar.org/navigator/DOM/1900/dominican-republic-first-ndc-archived_a6453c69d76feda510e0851036557792.pdf (copy of https://unfccc.int/sites/default/files/NDC/2022-06/INDC-DR%20August%202015%20%28unofficial%20translation%29.pdf)",
     "Intended Nationally Determined Contribution INDC-DR, August 2015 (first NDC, archived; unofficial English translation)",
     "Government of the Dominican Republic",
     "2015-08 (INDC); 2017-09-21 first NDC per Climate Policy Radar record", "2026-11-21",
     "8fa0deec0547936673a17e05ab3617b0847e2a79f0c1773c6530e8ff98b716f7", "downloads/DR/DR_NDC1_2017_INDC2015_en.pdf", "4", "English (unofficial translation)"],
    ["DR-04", "Dominican Republic", "BTR",
     "https://cdn.climatepolicyradar.org/navigator/DOM/2025/dominican-republic-biennial-transparency-report-btr1-national-communications-nc4_ad701aa446e577b1ca883f43e7312490.pdf (copy of https://unfccc.int/sites/default/files/resource/Informe%20Final%20BTR1_CN4_30.12.25vf.pdf)",
     "Primer Informe Bienal de Transparencia y Cuarta Comunicacion Nacional de la Republica Dominicana (BTR1/NC4)",
     "Ministerio de Medio Ambiente y Recursos Naturales and CNCCMC, Republica Dominicana",
     "2025-12-30", "2026-11-21",
     "2c51cc229f1b7e594b92470387f2705b6fa9491820824480f619ab262eea39ad", "downloads/DR/DR_BTR1_CN4_2025.pdf", "530", "Spanish"],
    ["DR-05", "Dominican Republic", "NID",
     "https://cdn.climatepolicyradar.org/navigator/DOM/2025/dominican-republic-national-inventory-report-nir-2024_3d5dea7cdecc42592886495a62f9b66e.pdf (copy of https://unfccc.int/sites/default/files/resource/2024_25NID_RD%20con%20ANEXOS%20vFINAL.pdf)",
     "Informe del Inventario Nacional de Gases de Efecto Invernadero Republica Dominicana, Serie 1998-2022 (2024_IIN_RD, NID with annexes)",
     "Ministerio de Medio Ambiente y Recursos Naturales (MMARN)",
     "2025", "2026-11-21",
     "40577e4c8836791b3b51408357f8229bf450e59e1d237c858ff0fc6437db7950", "downloads/DR/DR_NID_2025.pdf", "465", "Spanish"],
    ["DR-06", "Dominican Republic", "LTS-national-not-submitted",
     "https://rise.esmap.org/data/files/library/dominican-republic/Renewable%20Energy/Dominican%20Republic_National%20Development%20Strategy%20law%201-12.pdf",
     "Ley No. 1-12 de Estrategia Nacional de Desarrollo 2030 (END 2030); not submitted to the UNFCCC",
     "Ministerio de Economia, Planificacion y Desarrollo (edition hosted by the ESMAP RISE library)",
     "2012-01-25 (promulgation)", "2026-11-21",
     "464e9ac683e5a71a873c6dc2332d4f587d8a200d202f3ddc338a78b0dd09ea6e", "downloads/DR/DR_END2030_Ley1-12.pdf", "94", "Spanish"],
]

# ---------------------------------------------------------------- pending
PEND_H = ["country", "kind", "title", "urls_tried", "errors", "note"]
PEND = [
    ["Dominican Republic", "LTS",
     "Estrategia de Desarrollo Bajo en Emisiones a Largo Plazo (LT-LEDS) of the Dominican Republic",
     "https://unfccc.int/process/the-paris-agreement/long-term-strategies (WebFetch and curl); https://unfccc.int/LTS (WebFetch); https://unfccc.int/documents?f%5B0%5D=document_type%3A4296&f%5B1%5D=country%3A2148 (curl); https://app.climatepolicyradar.org/search?l=dominican-republic&c=UNFCCC&cfn=long-term (curl); web searches for the strategy PDF; https://ddpinitiative.org/wp-content/uploads/pdf/ddp2025_dom.pdf (curl, lead from search)",
     "UNFCCC pages: empty page to WebFetch and a bot-check page (845 bytes) to curl; Climate Policy Radar: no long-term strategy document listed for the Dominican Republic; searches: no strategy document found, only 2022 press notes on its preparation; DDP URL: page not found (HTML)",
     "No submission found. NDC 3.0 (DR-01 p.120) names the strategy as an instrument the NDC must be coherent with but gives no date or link; NDC 2020 (DR-02 p.26) and BTR1 (DR-04 p.111) state a carbon neutrality aspiration for 2050. Treated as not submitted; END 2030 (DR-06) registered as the national long-term plan the NDC cites."],
    ["Dominican Republic", "sector plan",
     "Plan Energetico Nacional 2025-2038 (PEN), cited by NDC 3.0 as Compendio del Plan Energetico Nacional 2025 a 2038",
     "https://cne.gob.do/plan-energetico-nacional/ (curl); https://cne.gob.do/documentos/tecnicos/pen/ (curl); https://www.cne.gob.do/documentos/plan-energetico-nacional/ (curl); https://cne.gob.do/?s=plan+energetico+nacional (curl); two web searches for the PDF",
     "First URL: HTTP 404; PEN page: a JavaScript file browser (Dropbox plugin) with no direct file link in the HTML; a scripted listing request to the site's file-browser endpoint was refused by the session permission system and not retried; web searches: news items only, no PDF",
     "Cited in DR-01 p.36 (demand and planning assumptions of the BAU) and p.129 (ICTU list of plans). Not cited for a stated quantified target in the NDC text, so its absence does not remove a target row."],
]

# ---------------------------------------------------------------- targets
T_H = ["target_id", "source_id", "page", "table_or_figure", "document_kind", "sector", "description", "original_term",
       "indicator", "value", "unit", "base_or_reference", "target_year", "conditionality", "gases", "read_as_image", "note"]
G4 = "CO2, CH4, N2O, HFC"
T = [
    # NDC 3.0 (DR-01): headline
    ["DR-T001", "DR-01", "p.14;p.62;p.129", "printed p.14, p.62; Tabla 8 (ICTU) printed p.129", "NDC", "economy-wide",
     "Economy-wide GHG reduction against the trend (BAU) scenario in 2030", "escenario de tendencia (BAU)",
     "percent reduction against BAU", "28", "percent", "BAU (2022 base year; BAU 2030 51,949.62 kt CO2eq)", "2030",
     "mixed: 8.5 points unconditional, 19.5 points conditional", G4, "no", "Single-year target type: relative to a projected baseline."],
    ["DR-T002", "DR-01", "p.14;p.62", "printed p.14, p.62", "NDC", "economy-wide",
     "Economy-wide GHG reduction in 2030 expressed in kt CO2eq", "", "emission reduction against BAU", "14732.1", "kt CO2eq",
     "BAU 2030 51,949.62 kt CO2eq", "2030", "mixed", G4, "no", "14,732.1 equals 4,734.7 kt from NDC 2.0 measures plus 9,997.4 kt from new NDC 3.0 measures (p.62 to p.63)."],
    ["DR-T003", "DR-01", "p.14;p.62;p.129", "printed p.14, p.62; Tabla 8 printed p.129", "NDC", "economy-wide",
     "Economy-wide GHG reduction against BAU in 2035", "", "percent reduction against BAU", "32", "percent",
     "BAU (2022 base year; BAU 2035 57,292.65 kt CO2eq)", "2035", "not stated", G4, "no",
     "The 8.5/19.5 split is stated for the 2030 target only; no split is printed for 2035."],
    ["DR-T004", "DR-01", "p.14;p.62", "printed p.14, p.62", "NDC", "economy-wide",
     "Economy-wide GHG reduction in 2035 expressed in kt CO2eq", "", "emission reduction against BAU", "18349.32", "kt CO2eq",
     "BAU 2035 57,292.65 kt CO2eq", "2035", "not stated", G4, "no", "8,351.95 kt from NDC 2.0 actions plus 9,997.4 kt from NDC 3.0 measures (p.63)."],
    ["DR-T005", "DR-01", "p.14;p.62", "printed p.14; Tabla 1 printed p.16", "NDC", "economy-wide",
     "Unconditional part of the 2030 reduction (national resources)", "no-condicionado", "percent reduction against BAU", "8.5", "percent",
     "BAU", "2030", "unconditional", G4, "no", "Table 7 (p.122) repeats 8.5 percent by 2030 as indicator 2."],
    ["DR-T006", "DR-01", "p.14;p.62", "printed p.14; Tabla 1 printed p.16", "NDC", "economy-wide",
     "Conditional part of the 2030 reduction (external finance, technology, capacity)", "condicionado", "percent reduction against BAU", "19.5", "percent",
     "BAU", "2030", "conditional", G4, "no", "Table 7 (p.122) repeats 19.5 percent by 2030 as indicator 3."],
    ["DR-T007", "DR-01", "p.64", "printed p.64; text describing Figura 9", "NDC", "economy-wide",
     "Emission level of the new ambition pathway in 2030", "nueva ambicion", "total gross emissions", "37217", "kt CO2eq",
     "absolute", "2030", "mixed", G4, "no", "Pathway falls from 42,842 kt CO2eq in 2025 (p.64). Gross emissions, removals not netted."],
    ["DR-T008", "DR-01", "p.122", "Tabla 7 printed p.122, indicator 4", "NDC", "economy-wide",
     "Number of enabling frameworks for NDC implementation to be established", "marcos habilitantes", "count of frameworks", "25", "number",
     "absolute", "2035", "not stated", "", "no", "Target year not printed; the NDC period is 2026 to 2035, read as 2035."],
    # NDC 3.0 energy
    ["DR-T009", "DR-01", "p.41;p.45", "Tabla 5 TOTAL row printed p.41; infographic printed p.45", "NDC", "Energy",
     "Emission reduction of the 12 energy PAMs (generation, efficiency, road transport, domestic aviation)", "", "emission reduction", "7477.22", "kt CO2eq",
     "BAU", "2030", "mixed", "CO2, CH4, N2O", "yes", "Additional to NDC 2.0 measures."],
    ["DR-T010", "DR-01", "p.40;p.46", "Tabla 5 printed p.40; infographic printed p.46", "NDC", "Energy",
     "Emission reduction of electricity generation PAMs 1 to 4", "Generacion de Electricidad", "emission reduction", "7204.56", "kt CO2eq",
     "BAU", "2030", "mixed", "CO2, CH4, N2O", "yes", ""],
    ["DR-T011", "DR-01", "p.148", "Anexo 1 printed p.2 (PAM 1)", "NDC", "Energy",
     "Four new natural gas combined cycle units entering the SENI before the end of 2030 (Estrella del Mar IV 150 MW, Manzanillo blocks 1 and 2 812 MW, San Felipe Andres 1 467 MW)",
     "Nuevas unidades de generacion a gas natural", "new natural gas combined cycle capacity", "1429", "MW", "absolute (new capacity)", "2030", "not stated",
     "CO2, CH4, N2O", "no", "Natural gas framed as transition fuel replacing fuel oil plants (p.147)."],
    ["DR-T012", "DR-01", "p.148", "Anexo 1 printed p.2 (PAM 1)", "NDC", "Energy",
     "Emission reduction from the new natural gas combined cycle units", "", "emission reduction per year", "2764734.31", "t CO2eq per year",
     "BAU", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2026 to 2030."],
    ["DR-T013", "DR-01", "p.149", "Anexo 1 printed p.3 (PAM 2)", "NDC", "Energy",
     "New solar, wind and hydro capacity by 2030", "Incremento en un 109% FRE", "new renewable capacity", "1529", "MW (nominal)",
     "absolute (new capacity); equals +109.5 percent of 2024 renewable capacity", "2030", "not stated", "CO2, CH4, N2O", "no",
     "Objective line says 109 percent, description says 109.5 percent of installed renewable capacity of base year 2024."],
    ["DR-T014", "DR-01", "p.149", "Anexo 1 printed p.3 (PAM 2)", "NDC", "Energy",
     "New solar parks (30 parks), of which 170 MW in battery storage", "", "new solar PV capacity", "1267.15", "MW (nominal)",
     "absolute (new capacity)", "2030", "not stated", "CO2", "no", "170 MW of the 1,267.15 MW is battery storage (BESS)."],
    ["DR-T015", "DR-01", "p.149", "Anexo 1 printed p.3 (PAM 2)", "NDC", "Energy",
     "New wind parks (5 parks)", "", "new wind capacity", "250", "MW (nominal)", "absolute (new capacity)", "2030", "not stated", "CO2", "no", ""],
    ["DR-T016", "DR-01", "p.149", "Anexo 1 printed p.3 (PAM 2)", "NDC", "Energy",
     "One new hydro plant", "", "new hydro capacity", "12", "MW (nominal)", "absolute (new capacity)", "2030", "not stated", "CO2", "no", ""],
    ["DR-T017", "DR-01", "p.149", "Anexo 1 printed p.3 (PAM 2)", "NDC", "Energy",
     "Emission reduction from new renewable capacity", "", "emission reduction per year", "2179636.64", "t CO2 per year",
     "BAU", "2030", "not stated", "CO2, CH4, N2O", "no", ""],
    ["DR-T018", "DR-01", "p.150", "Anexo 1 printed p.4 (PAM 3)", "NDC", "Energy",
     "Distribution loss reduction plan: energy saved per year", "Plan Integral de Reduccion de Perdidas", "electricity saved per year", "1005400", "MWh per year",
     "BAU", "2029", "not stated", "CO2, CH4, N2O", "no", "Execution 2025 to 2029; World Bank loan 9624-DO and IDB DR-L1128 programmes."],
    ["DR-T019", "DR-01", "p.150", "Anexo 1 printed p.4 (PAM 3)", "NDC", "Energy",
     "Emission reduction from distribution loss reduction", "", "emission reduction per year", "648885.16", "t CO2eq per year", "BAU", "2029", "not stated", "CO2, CH4, N2O", "no", ""],
    ["DR-T020", "DR-01", "p.151", "Anexo 1 printed p.5 (PAM 4)", "NDC", "Energy",
     "Enabling framework, studies and first small modular nuclear reactor of up to 300 MW", "pequeno reactor modular (SMR)", "nuclear capacity", "300", "MW",
     "absolute", "2035", "not stated", "CO2, CH4, N2O", "no", "Execution 2026 to 2035; capacity is an upper bound (hasta 300 MW)."],
    ["DR-T021", "DR-01", "p.151", "Anexo 1 printed p.5 (PAM 4)", "NDC", "Energy",
     "Emission reduction from the small modular reactor", "", "emission reduction", "1611305.64", "t CO2eq", "BAU", "2035", "not stated", "CO2, CH4, N2O", "no", "Per-year basis not stated."],
    ["DR-T022", "DR-01", "p.153;p.154", "Anexo 1 printed p.7 and p.8 (PAM 6)", "NDC", "Energy",
     "Public lighting and government demand management: electricity saved (over 247,300 LED lamps)", "", "electricity saved per year", "194838", "MWh per year",
     "BAU", "2030", "not stated", "CO2", "no", "Execution 2026 to 2030. GHG reduction 125,748.45 t CO2eq per year (p.153)."],
    ["DR-T023", "DR-01", "p.40;p.47", "Tabla 5 printed p.40; infographic printed p.47", "NDC", "Energy",
     "Emission reduction of energy efficiency PAMs 5 and 6 (RAC standards and labelling, public lighting)", "Eficiencia Energetica", "emission reduction", "125.75", "kt CO2eq",
     "BAU", "2030", "mixed", "CO2, HFC", "yes", "PAM 5 (MEPS and labelling for refrigeration and air conditioning) has no own quantified GHG target in Annex 1 (p.152)."],
    # NDC 3.0 transport
    ["DR-T024", "DR-01", "p.40;p.48", "Tabla 5 printed p.40; infographic printed p.48", "NDC", "Transport",
     "Emission reduction of road transport PAMs 7 to 11", "Transporte Carretero", "emission reduction", "145.91", "kt CO2eq",
     "BAU", "2030", "mixed", "CO2, CH4, N2O", "yes", ""],
    ["DR-T025", "DR-01", "p.155", "Anexo 1 printed p.9 (PAM 7)", "NDC", "Transport",
     "Two new bus corridors in Santo Domingo (Independencia 31 km, 27 de Febrero 36.6 km) with 174 more efficient buses", "", "emission reduction per year", "22925.66", "t CO2eq per year",
     "BAU", "2030", "not stated", "CO2, CH4, N2O", "no", "The buses are diesel (64 plus 110); the measure is fleet efficiency, not electrification."],
    ["DR-T026", "DR-01", "p.156", "Anexo 1 printed p.10 (PAM 8)", "NDC", "Transport",
     "Monorail lines: Santiago (13.2 km, 2026) and Santo Domingo phase I (10.5 km, 2035)", "Monorriel", "emission reduction per year", "111642", "t CO2eq per year",
     "BAU", "2035", "not stated", "CO2, CH4, N2O", "no", "58,993.65 t per year Santo Domingo plus 52,648.56 t per year Santiago."],
    ["DR-T027", "DR-01", "p.157", "Anexo 1 printed p.11 (PAM 9)", "NDC", "Transport",
     "New cable car line (Santo Domingo Oeste), up to 4,500 passengers per hour per direction", "teleferico", "emission reduction per year", "11343", "t CO2eq per year",
     "BAU", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2026 to 2030."],
    ["DR-T028", "DR-01", "p.159;p.160", "Anexo 1 printed p.13 and p.14 (PAM 12)", "NDC", "Transport",
     "Sustainable and lower-carbon aviation fuel in domestic aviation, 500,000 litres per year", "SAF y LCAF", "fuel volume per year", "500000", "litres per year",
     "absolute", "2035", "not stated", "CO2, CH4, N2O", "no", "GHG target 1,000 t CO2eq (p.160); execution 2028 to 2035."],
    # NDC 3.0 IPPU
    ["DR-T029", "DR-01", "p.162;p.163", "Anexo 1 printed p.16 and p.17 (PAM 14)", "NDC", "IPPU",
     "Cut imported HFC substances by 5 percent against BAU in 2030 (Kigali Amendment)", "Disminuir la importacion de las sustancias HFC en 5%", "HFC imports against BAU", "5", "percent",
     "BAU", "2030", "not stated", "HFC", "no", "Equals 191,710 t CO2eq (p.163); observation expects up to 10 percent before 2035."],
    ["DR-T030", "DR-01", "p.162", "Anexo 1 printed p.16 (PAM 13)", "NDC", "IPPU",
     "Enabling frameworks and studies for cement decarbonisation (clinker reduction)", "", "enabling framework", "", "",
     "", "2030", "not stated", "CO2", "no", "No quantified GHG target (N/A in Tabla 5, p.41)."],
    # NDC 3.0 agriculture
    ["DR-T031", "DR-01", "p.164", "Anexo 1 printed p.18 (PAM 15)", "NDC", "Agriculture",
     "Cut cattle mortality to 8 percent (dairy) and 10 percent (beef), with feed inhibitors", "", "cattle mortality rate (dairy)", "8", "percent",
     "absolute", "2030", "not stated", "CH4", "no", "Beef cattle 10 percent. GHG 1,622 t CO2eq per year."],
    ["DR-T032", "DR-01", "p.165", "Anexo 1 printed p.19 (PAM 16)", "NDC", "Agriculture",
     "Half of the manure sludge of mixed and intensive systems treated in biodigesters", "", "share of sludge in biodigesters", "50", "percent",
     "absolute", "2030", "not stated", "CH4", "no", "GHG 14,439.82 t CO2eq per year."],
    ["DR-T033", "DR-01", "p.166", "Anexo 1 printed p.20 (PAM 17)", "NDC", "Agriculture",
     "Half of the solid manure of mixed and intensive systems composted", "", "share of solid manure composted", "50", "percent",
     "absolute", "2030", "not stated", "CH4", "no", "GHG 9,073.37 t CO2eq per year."],
    ["DR-T034", "DR-01", "p.167", "Anexo 1 printed p.21 (PAM 18)", "NDC", "Agriculture",
     "Cut the permanently flooded rice area by 10 percent (alternate wetting and drying)", "", "permanently flooded rice area", "10", "percent reduction",
     "current area", "2030", "not stated", "CH4", "no", "Agriculture PAMs together 29.24 kt CO2eq (Tabla 5, p.42)."],
    # NDC 3.0 LULUCF
    ["DR-T035", "DR-01", "p.169", "Anexo 1 printed p.23 (PAM 19)", "NDC", "LULUCF",
     "Restore 4,500 km2 of degraded forest inside protected areas", "Republica Dominicana 30 x 30", "area reforested", "4500", "km2",
     "absolute", "2030", "not stated", "CO2", "no", "Removals +1.35 Mt CO2 per year at 3 t CO2 per ha per year."],
    ["DR-T036", "DR-01", "p.169;p.171", "Anexo 1 printed p.23 and p.25 (PAMs 19, 20)", "NDC", "LULUCF",
     "Effective conservation of 30 percent of national territory", "conservacion efectiva del 30 % del territorio nacional", "share of territory conserved", "30", "percent",
     "absolute", "2030", "not stated", "CO2", "no", ""],
    ["DR-T037", "DR-01", "p.171", "Anexo 1 printed p.25 (PAM 20)", "NDC", "LULUCF",
     "Zero net mangrove loss inside protected areas", "", "net mangrove loss", "0", "percent",
     "baseline net loss about 10 km2 2015 to 2022", "2030", "not stated", "CO2", "no", "GHG 660,000 t CO2eq."],
    ["DR-T038", "DR-01", "p.42;p.57", "Tabla 5 printed p.42; infographic printed p.57", "NDC", "LULUCF",
     "Emission reduction or removal of the two forest land PAMs", "", "emission reduction", "2010", "kt CO2eq",
     "BAU", "2030", "mixed", "CO2", "yes", "Table 5 prints the LULUCF total as 2,010,000 on p.42 (in a kt column); the PAM rows and the infographic give 2,010; read as 2,010 kt."],
    ["DR-T039", "DR-01", "p.79", "printed p.79", "NDC", "LULUCF",
     "Conservation, restoration and sustainable management of priority ecosystems (adaptation)", "", "share of priority ecosystems", "50", "percent",
     "absolute", "2030", "not stated", "", "no", "70 percent by 2035. Adaptation measure; indicator base not defined in the text."],
    # NDC 3.0 waste
    ["DR-T040", "DR-01", "p.175", "Anexo 1 printed p.29 (PAM 22)", "NDC", "Waste",
     "Methane capture and flaring at Duquesa landfill closure", "cierre tecnico de Duquesa", "emission reduction per year", "138546.23", "t CO2 per year",
     "BAU", "2030", "not stated", "CH4", "no", "Includes closure of about 120 ha of open dumps and valorisation plants of 36,000 t per year."],
    ["DR-T041", "DR-01", "p.176", "Anexo 1 printed p.30 (PAM 23)", "NDC", "Waste",
     "Raise waste valorisation above 7 percent by 2035", "valorizacion de residuos al 7%", "waste valorisation rate", "7", "percent",
     "absolute", "2035", "not stated", "CH4", "no", "Aligned with PLANGIRS, which aims at 15 percent valorisation and closing 100 percent of open dumps (p.177)."],
    ["DR-T042", "DR-01", "p.42;p.60", "Tabla 5 printed p.42; infographic printed p.60", "NDC", "Waste",
     "Wastewater PAMs 24 and 25 (Boca Chica, Higuey, La Romana, Moca, Gaspar Hernandez)", "", "emission reduction", "150.65", "kt CO2eq",
     "BAU", "2030", "mixed", "CH4, N2O", "yes", ""],
    # NDC 2020 (DR-02)
    ["DR-T043", "DR-02", "p.5;p.7;p.11", "printed p.5, p.7, p.11", "NDC", "economy-wide",
     "Economy-wide GHG reduction against BAU in 2030 (previous NDC)", "", "percent reduction against BAU", "27", "percent",
     "BAU 2030 51,000 Gg CO2eq (Plan DECCC 2011); reference year 2010", "2030", "mixed: 20 points conditional, 7 points unconditional (5 private, 2 public)",
     "CO2, CH4, N2O, HFC, PFC, SF6, NF3", "no", "Superseded by DR-01."],
    ["DR-T044", "DR-02", "p.5;p.9", "printed p.5, p.9", "NDC", "economy-wide",
     "Economy-wide reduction from 46 mitigation options (previous NDC)", "", "emission reduction against BAU", "13853.71", "Gg CO2eq",
     "BAU 2030 51,000 Gg CO2eq", "2030", "mixed", "CO2, CH4, N2O, HFC", "no", "Equals 27.16 percent of BAU 2030."],
    ["DR-T045", "DR-02", "p.26", "printed p.26", "NDC", "economy-wide",
     "Aspiration to carbon neutrality by 2050", "aspiracion de carbono neutralidad al 2050", "net emissions", "0", "kt CO2eq",
     "absolute", "2050", "not stated", "not stated", "no", "Aspiration, not a committed target."],
    ["DR-T046", "DR-02", "p.140", "Anexo VIII printed p.140", "NDC", "Energy",
     "Conversion of fuel oil No. 6 units to natural gas", "", "capacity converted", "951", "MWp",
     "absolute", "2025", "not stated", "CO2, CH4, N2O", "no", "Execution 2013 to 2025; description sums stages to 911 MWp; BTR1 (DR-04 p.154) reports 800 MW."],
    ["DR-T047", "DR-02", "p.141", "Anexo VIII printed p.141", "NDC", "Energy",
     "New wind parks", "", "new wind capacity", "477", "MWp", "absolute (new capacity)", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2022 to 2030; capacity factor 34 percent."],
    ["DR-T048", "DR-02", "p.142", "Anexo VIII printed p.142", "NDC", "Energy",
     "New solar PV installations", "", "new solar PV capacity", "479", "MWp", "absolute (new capacity)", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2022 to 2030; capacity factor 18 percent."],
    ["DR-T049", "DR-02", "p.142", "Anexo VIII printed p.142", "NDC", "Energy",
     "Small biomass and solid waste plants (5 MWp units)", "", "new biomass capacity", "93", "MWp", "absolute (new capacity)", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2022 to 2030."],
    ["DR-T050", "DR-02", "p.143", "Anexo VIII printed p.143", "NDC", "Energy",
     "Small and medium hydro plants", "", "new hydro capacity", "21", "MWp", "absolute (new capacity)", "2025", "not stated", "CO2, CH4, N2O", "no", "Execution 2023 to 2025."],
    ["DR-T051", "DR-02", "p.144", "Anexo VIII printed p.144", "NDC", "Energy",
     "Combined cycle expansion (Los Mina gas turbines)", "", "new combined cycle capacity", "100", "MWp", "absolute (new capacity)", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2022 to 2030."],
    ["DR-T052", "DR-02", "p.145", "Anexo VIII printed p.145", "NDC", "Energy",
     "New natural gas plant (mobile unit) in Santo Domingo", "", "new natural gas capacity", "140", "MWp", "absolute (new capacity)", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2021 to 2030."],
    ["DR-T053", "DR-02", "p.101", "Anexo I printed p.101", "NDC", "Energy",
     "Renewable share of electricity generation set by Law 57-07", "cuota de renovables", "renewable share of generation", "25", "percent",
     "absolute", "2025", "not stated", "", "no", "Law 57-07 also set 10 percent for 2015."],
    ["DR-T054", "DR-02", "p.156", "Anexo VIII printed p.156", "NDC", "Transport",
     "Replace 300 diesel buses carrying workers with 100 percent electric buses", "", "electric buses", "300", "vehicles",
     "absolute", "2030", "not stated", "CO2, CH4, N2O", "no", "Execution 2023 to 2030."],
    ["DR-T055", "DR-02", "p.158", "Anexo VIII printed p.157 to p.158", "NDC", "Transport",
     "Taxi and concho fleet: replace 25 percent of the current fleet, 15 percent electric and 10 percent hybrid", "", "electric share of taxi fleet", "15", "percent",
     "current fleet", "2030", "not stated", "CO2, CH4, N2O", "no", "GHG 1,516.94 Gg CO2eq (p.157)."],
    ["DR-T056", "DR-02", "p.158", "Anexo VIII printed p.158", "NDC", "Transport",
     "Pilot feeder bus network with 130 natural gas buses", "", "natural gas buses", "130", "vehicles",
     "absolute", "2030", "not stated", "CO2, CH4, N2O", "no", "GHG 175.83 Gg CO2eq; execution from 2023."],
    ["DR-T057", "DR-02", "p.159", "Anexo VIII printed p.159", "NDC", "Transport",
     "Pilot of 80 electric school buses", "", "electric buses", "80", "vehicles",
     "absolute", "2030", "not stated", "CO2, CH4, N2O", "no", "GHG 31.44 Gg CO2eq; execution 2023 to 2030."],
    ["DR-T058", "DR-02", "p.160", "Anexo VIII printed p.160", "NDC", "Transport",
     "Enabling frameworks to replace up to 240,000 private cars with electric and hybrid cars (75 percent electric, 25 percent hybrid)", "", "electric and hybrid cars", "240000", "vehicles",
     "absolute", "2030", "not stated", "CO2, CH4, N2O", "no", "Phases of 100,000 and 120,000 units are printed (sum 220,000) next to up to 240,000; GHG 3,444.73 Gg CO2eq."],
    # INDC (DR-03)
    ["DR-T059", "DR-03", "p.2", "table, row Quantifiable emissions reduction target", "NDC", "economy-wide",
     "Reduce emissions 25 percent below base-year per capita emissions by 2030 (first NDC)", "", "per capita emissions against base year", "25", "percent",
     "base year 2010 (3.6 t CO2e per capita)", "2030", "conditional", "CO2, CH4, N2O", "no", "Superseded by DR-02 and DR-01."],
    # BTR1 (DR-04)
    ["DR-T060", "DR-04", "p.111", "printed p.111, section 3.2.1", "BTR", "economy-wide",
     "Long-term objective of carbon neutrality by 2050", "carbono neutralidad al 2050", "net emissions", "0", "kt CO2eq",
     "absolute", "2050", "not stated", "not stated", "no", "Stated as the long-term objective the NDC 2020 is aligned with; no strategy document attached."],
    ["DR-T061", "DR-04", "p.174", "printed p.174, section 3.6.2.2 b", "BTR", "Energy",
     "Ministry of Energy and Mines renewable target: 25 percent of generation by 2025", "meta de energia renovable del MEM", "renewable share of generation", "25", "percent",
     "absolute", "2025", "not stated", "", "no", "Reported as an assumption of the World Bank NDC-RD 2030 scenario."],
    ["DR-T062", "DR-04", "p.174", "printed p.174, section 3.6.2.2 b", "BTR", "Energy",
     "Ministry of Energy and Mines renewable target: 30 percent of generation by 2030", "meta de energia renovable del MEM", "renewable share of generation", "30", "percent",
     "absolute", "2030", "not stated", "", "no", "Same scenario assumes 9.3 percent of the vehicle fleet electric by 2050 (a scenario assumption, not a target)."],
    ["DR-T063", "DR-04", "p.179", "printed p.179", "BTR", "IPPU",
     "Reduce HFC by 35 percent by 2030 (Kigali Amendment)", "reduccion de un 35% de los HFC al 2030", "HFC consumption", "35", "percent reduction",
     "not stated", "2030", "not stated", "HFC", "no", "Differs from DR-01 (5 percent of imports against BAU by 2030); base not printed."],
    ["DR-T064", "DR-04", "p.181;p.164", "printed p.181; progress table printed p.164", "BTR", "LULUCF",
     "Raise the reforestation rate from 11,300 to 15,000 ha per year", "", "reforestation rate", "15000", "ha per year",
     "current rate 11,300 ha per year", "2030", "not stated", "CO2", "no", "Target year not printed with the rate; NDC 2020 horizon 2030 assumed."],
    # END 2030 (DR-06)
    ["DR-T065", "DR-06", "p.78", "Articulo 28, indicator 4.1, printed p.76", "LTS-national-not-submitted", "economy-wide",
     "Carbon dioxide emissions per capita (END 2030 indicator 4.1)", "Emisiones de dioxido de carbono", "CO2 emissions per capita", "2.8", "t CO2 per capita",
     "base year 2010 3.6 t per capita", "2030", "not stated", "CO2", "no", "Five-year milestones 3.4 (2015), 3.2 (2020), 3.0 (2025)."],
    ["DR-T066", "DR-06", "p.78", "Articulo 28, indicator 4.3, printed p.76", "LTS-national-not-submitted", "LULUCF",
     "Average annual deforestation rate (negative means forest gain)", "Tasa de deforestacion anual promedio", "deforestation rate", "-0.2", "percent of forest area per year",
     "base year 2005 0.1", "2030", "not stated", "CO2", "no", "Protected areas held at 24.4 percent of territory (indicator 4.2)."],
]

# ---------------------------------------------------------------- projections
P_H = ["source_id", "page", "table_or_figure", "scenario_as_named", "sector", "gas", "unit", "year", "value", "note"]
P = []
tab4 = [
    ("CO2", "kt CO2", ["28589", "34025.67", "37936.85"], "CO2 emissions"),
    ("CH4", "kt CH4", ["415", "391.68", "377.70"], "kt of gas; GWP AR6 29.8 applied in the total"),
    ("N2O", "kt N2O", ["7.367", "13.54", "19.83"], "kt of gas; GWP AR6 273 applied in the total"),
    ("HFC", "kt CO2eq", ["2360", "2555.65", "2686.01"], "printed GWP 1950; the totals only add up if HFC is already in kt CO2eq"),
    ("removals CO2", "kt CO2", ["10247.78", "9545.04", "9130.52"], "removals, printed as positive"),
    ("all (gross emissions)", "kt CO2eq", ["45327.19", "51949.62", "57292.65"], "gross emissions without removals"),
]
for gas, unit, vals, note in tab4:
    for yr, v in zip(["2022", "2030", "2035"], vals):
        scen = "historic (inventory 2022)" if yr == "2022" else "BAU (escenario tendencial, proyeccion media)"
        P.append(["DR-01", "p.32;p.195", "Tabla 4 printed p.32; Anexo 4 Tabla No.4 printed p.8 of 8", scen, "economy-wide", gas, unit, yr, v, note])
P.append(["DR-01", "p.64", "text describing Figura 9", "nueva ambicion (NDC 3.0 pathway)", "economy-wide", "all (gross emissions)", "kt CO2eq", "2025", "42842", ""])
P.append(["DR-01", "p.64", "text describing Figura 9", "nueva ambicion (NDC 3.0 pathway)", "economy-wide", "all (gross emissions)", "kt CO2eq", "2030", "37217", ""])
P.append(["DR-02", "p.7", "printed p.7", "BAU (Plan DECCC 2011)", "economy-wide", "all", "Gg CO2eq", "2030", "51000", "previous NDC baseline"])
P.append(["DR-04", "p.173", "printed p.173, Figura 3.17", "sin medidas (without measures)", "Energy", "all", "kt CO2eq", "2035", "38200", "electricity generation and road transport categories"])
P.append(["DR-04", "p.177", "printed p.177, Figura 3.19", "sin medidas (without measures)", "IPPU", "all", "kt CO2eq", "2035", "5014", ""])
P.append(["DR-04", "p.182", "printed p.182, Figura 3.22", "sin medidas (without measures)", "Agriculture", "all", "kt CO2eq", "2035", "5800", "enteric fermentation and rice cultivation only"])
P.append(["DR-04", "p.183", "printed p.183", "sin medidas (without measures)", "Agriculture", "all", "kt CO2eq", "2035", "7114", "agriculture and land uses total, incl. 1,314 kt from forest land and other land uses"])
P.append(["DR-04", "p.184", "printed p.184, Figura 3.23", "sin medidas (without measures)", "Waste", "all", "kt CO2eq", "2035", "6914", "5,700 kt solid waste disposal plus 1,614 kt wastewater"])
tab314 = [
    ("HFC", ["2360", "2555.65", "2686.01"], "RAC HFC"),
    ("CH4", ["12367", "11672.06", "11255.46"], "kt CO2eq"),
    ("N2O", ["2011.19", "3696.42", "5413.59"], "kt CO2eq"),
    ("removals CO2", ["-10247.78", "-9545.04", "-9130.52"], "removals, printed as negative"),
    ("all (gross emissions)", ["45327.19", "51949.62", "57291.91"], "2035 total differs from DR-01 (57,292.65) by 0.74 kt"),
]
for gas, vals, note in tab314:
    for yr, v in zip(["2022", "2030", "2035"], vals):
        scen = "historic (inventory 2022)" if yr == "2022" else "projection for key indicators (BAU of NDC)"
        P.append(["DR-04", "p.189", "Tabla 3.14 printed p.189", scen, "economy-wide", gas, "kt CO2eq", yr, v, note + "; 2040 not estimated (NE)"])

if __name__ == "__main__":
    write("parts/sources_DR.csv", SRC_H, SRC)
    write("parts/sources_pending_DR.csv", PEND_H, PEND)
    write("targets_DR.csv", T_H, T)
    write("projections_DR.csv", P_H, P)
