"""Transcribed regional source register and printed values for LAC_COST_REGIONAL.

Every value below was read from the downloaded file at the stated PDF page (1-based page of the
file, not the printed folio). The Colombian Technology Catalogue rows are extracted by
catalog_extract.py and merged in step3_extract.py.
"""

RETRIEVED_NEW = "2026-11-11"   # downloaded by this job
RETRIEVED_COPY = "2026-11-10"  # file copied from a country job download folder (retrieved that day)

# source_id, url, title, publisher, publication_date, retrieval_date, downloaded_file, region, notes
SOURCES = [
    ("REG-001", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf",
     "Renewable Power Generation Costs in 2022", "International Renewable Energy Agency (IRENA)", "2023-08", RETRIEVED_COPY,
     "irena/IRENA_RPGC_2022.pdf", "LAC regional tables", "values in 2022 USD; copied from the Costa Rica job download folder"),
    ("REG-002", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_TEC_RPGC_in_2024_2025.pdf",
     "Renewable Power Generation Costs in 2024", "International Renewable Energy Agency (IRENA)", "2025-07", RETRIEVED_COPY,
     "irena/IRENA_RPGC_2024.pdf", "LAC regional tables", "values in 2024 USD; copied from the Costa Rica job download folder"),
    ("REG-003", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf",
     "Renewable Power Generation Costs in 2025", "International Renewable Energy Agency (IRENA)", "2026-07-02", RETRIEVED_COPY,
     "irena/IRENA_RPGC_2025.pdf", "LAC regional tables", "values in 2025 USD; copied from the Jamaica job download folder"),
    ("REG-004", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2022/Mar/IRENA_Renewable_Roadmap_Central_America_2022.pdf",
     "Renewable Energy Roadmap for Central America: Towards a Regional Energy Transition", "International Renewable Energy Agency (IRENA)", "2022-03", RETRIEVED_NEW,
     "ca/IRENA_Renewable_Roadmap_Central_America_2022.pdf", "Central America", "Annex B Table 16 prints investment costs without a currency year"),
    ("REG-005", "https://www.grupoice.com/wps/wcm/connect/20b300e4-c4df-4994-b1b1-372726fa4f3b/PLAN+DE+EXPANSION+DE+LA+GENERACION+ELECTRICA+2024-2040.pdf?MOD=AJPERES&CVID=pFal9fj",
     "Plan de Expansion de la Generacion Electrica 2024-2040", "Instituto Costarricense de Electricidad (ICE)", "2025-09", RETRIEVED_NEW,
     "ca/CR_ICE_PEG_2024-2040.pdf", "Costa Rica", "costs in constant USD of December 2023 (PDF p.151 and p.152 text)"),
    ("REG-006", "https://cnd.enee.hn/wp-content/uploads/2026/09/Informe-PIEG-2026-2035.pdf",
     "Plan Indicativo de Expansion de la Generacion 2026-2035, Informe", "Operador del Sistema (ODS) / Centro Nacional de Despacho, Honduras", "2026-09", RETRIEVED_COPY,
     "ca/HON_ODS_Informe_PIEG_2026-2035.pdf", "Honduras", "Tabla 19 costs referenced to the year 2024; copied from the Honduras job download folder"),
    ("REG-007", "https://mem.gob.gt/wp-content/uploads/2026/01/PEIG_2026_2050_MEM.pdf",
     "Plan de Expansion Indicativo del Sistema de Generacion 2026-2050", "Ministerio de Energia y Minas (MEM), Guatemala", "2026-01", RETRIEVED_COPY,
     "ca/GUA_MEM_PEIG_2026-2050.pdf", "Guatemala", "Tabla 6 prints no currency year; copied from the Guatemala job download folder"),
    ("REG-008", "https://www.cnee.gob.gt/PlanesExpansion/2024-2054/PEG%202024-2054.pdf",
     "Plan de Expansion Indicativo del Sistema de Generacion 2024-2054", "Ministerio de Energia y Minas (MEM), Guatemala; hosted by CNEE", "2024-01", RETRIEVED_NEW,
     "ca/GUA_PEG_2024-2054.pdf", "Guatemala", "no technology cost table in the text layer"),
    ("REG-009", "https://asep.gob.pa/wp-content/uploads/electricidad/consultas_publicas/2025/cp_009-2025/tomo_II/tomo_II-plan_Indicativo_generacion_2025-2039.pdf",
     "Plan de Expansion del Sistema Interconectado Nacional 2025-2039, Tomo II Plan Indicativo de Generacion", "Empresa de Transmision Electrica S.A. (ETESA), Panama; hosted by ASEP", "2025-07", RETRIEVED_NEW,
     "ca/PAN_ETESA_PESIN_2025-2039_tomoII_generacion.pdf", "Panama", "project-by-project costs in B/./kW, no currency year stated"),
    ("REG-010", "https://estadisticas.dgehm.gob.sv/wp-content/uploads/2021/06/Plan-indicativo-de-la-generaci%C3%B3n-de-la-expansi%C3%B3n-2020-2030-vf.pdf",
     "Plan Indicativo de la Expansion de la Generacion Electrica de El Salvador 2020-2030", "Consejo Nacional de Energia / DGEHM, El Salvador", "2020-11", RETRIEVED_NEW,
     "ca/SLV_PIEGE_2020-2030.pdf", "El Salvador", "project costs in $/kW, no currency year stated"),
    ("REG-011", "https://dof.gob.mx/nota_detalle_popup.php?codigo=5770297",
     "Plan de Desarrollo del Sector Electrico (PLADESE) 2025-2039, Diario Oficial de la Federacion", "Secretaria de Energia (SENER), Mexico", "2025-10-14", RETRIEVED_NEW,
     "ca/MEX_SENER_PLADESE_2025-2039_DOF.html", "Mexico", "Tabla 3.1 costs are CAIO (include interest during construction) with no currency year"),
    ("REG-012", "https://publications.iadb.org/publications/spanish/document/Evoluci%C3%B3n_futura_de_costos_de_las_energ%C3%ADas_renovables_y_almacenamiento_en_Am%C3%A9rica_Latina_es.pdf",
     "Evolucion futura de costos de las energias renovables y almacenamiento en America Latina (Nota tecnica IDB-TN-1831)", "Banco Interamericano de Desarrollo (BID)", "2019-12", RETRIEVED_NEW,
     "ca/IDB_TN1831_costos_renovables_almacenamiento_AL.pdf", "Latin America", "country costs shown as charts only"),
    ("REG-013", "https://docs.upme.gov.co/SIMEC/Energia%20Electrica/PIEG/2025-2039/PIEG_2025_2039_Version_final.pdf",
     "Plan Indicativo de Expansion de la Generacion 2025-2039, version final", "Unidad de Planeacion Minero Energetica (UPME), Colombia", "2026-07", RETRIEVED_NEW,
     "and/COL_UPME_PIEG_2025-2039.pdf", "Colombia", "CAPEX by technology only as a chart (Grafica 8)"),
    ("REG-014", "https://minenergia.gov.co/documents/13276/Catalogo-Tecnologico-Colombiano-tecnologias-generacion-almacenamiento-energia-ES.pdf",
     "Catalogo Tecnologico Colombiano: Tecnologias de generacion y almacenamiento de energia, primera edicion", "Ministerio de Minas y Energia (MME) and UPME, Colombia, with the Danish Energy Agency", "2025-03", RETRIEVED_NEW,
     "and/COL_MinEnergia_Catalogo_Tecnologico_generacion_almacenamiento.pdf", "Colombia", "all cost data in fixed 2024 USD prices (PDF p.30)"),
    ("REG-015", "https://www.mset.gov.jm/wp-content/uploads/2020/03/2018-Jamaica-Integrated-Resource-Feb-21-2020.pdf",
     "2018 Jamaica Integrated Resource Plan", "Ministry of Science, Energy and Technology (MSET), Jamaica", "2020-02-21", RETRIEVED_COPY,
     "car/JAM_IRP_2018_MSET_Feb2020.pdf", "Jamaica", "all costs in 2018 United States dollars (PDF p.59); copied from the Jamaica job download folder"),
    ("REG-016", "https://cne.gob.do/wp-admin/admin-ajax.php?action=outofthebox-download&OutoftheBoxpath=%2Fpen2022-2037.pdf&lastpath=%2F&account_id=dbid:AAAGpYR0ODh0f0jJZRlCsjhWYMYovXEms_Q&listtoken=255346f20b4341ea85f9ebf4917022f4&dl=1",
     "Plan Energetico Nacional 2022-2036", "Comision Nacional de Energia (CNE), Republica Dominicana", "2022-08", RETRIEVED_COPY,
     "car/DR_CNE_PEN2022-2036.pdf", "Dominican Republic", "generic project tables 204 to 229 print no currency year; copied from the Dominican Republic job download folder"),
    ("REG-017", "https://energy.gov.bb/wp-content/uploads/2024/10/MM_IADB_Draft-IRRP-Report_ActivityB_vB_0-Final-Rev-6-June-22-Revision-FEL-1-1.pdf",
     "Integrated Resource and Resiliency Plan for Barbados, Activity B: Draft Report", "Government of Barbados (Mott MacDonald for the IDB)", "2021-06-22", RETRIEVED_NEW,
     "car/BRB_IRRP_draft_ActivityB.pdf", "Barbados", "Table E.1 labelled 2020 Cost (BBD/MW); no price base stated"),
    ("REG-018", "https://www.ccreee.org/wp-content/uploads/2022/03/Sustainable-Energy-Technology-Considerations-and-Regional-Outlook.pdf",
     "Sustainable Energy Technology Considerations and Regional Outlook", "Caribbean Centre for Renewable Energy and Energy Efficiency (CCREEE)", "2022-03", RETRIEVED_NEW,
     "car/CCREEE_Sustainable_Energy_Technology_Considerations_2022.pdf", "Caribbean", "2020 benchmark ranges"),
    ("REG-019", "https://energia.pr.gov/wp-content/uploads/sites/7/2019/02/PREPA-Ex.-1.0-IRP-2019-PREPA-IRP-Report.pdf",
     "Puerto Rico Integrated Resource Plan 2018-2019, Draft for Review (Exhibit 1.0)", "Puerto Rico Electric Power Authority (PREPA), prepared by Siemens PTI", "2019-02", RETRIEVED_NEW,
     "car/PREPA_IRP_2019_Ex1.0_Report.pdf", "Puerto Rico", "costs in 2018 USD"),
    ("REG-020", "https://cnd.enee.hn/wp-content/uploads/2026/09/Anexos-PIEG-2026-2035.pdf",
     "Plan Indicativo de Expansion de la Generacion 2026-2035, Anexos", "Operador del Sistema (ODS) / Centro Nacional de Despacho, Honduras", "2026-09", RETRIEVED_COPY,
     "ca/HON_ODS_Anexos_PIEG_2026-2035.pdf", "Honduras", "cost breakdowns behind Tabla 19 of the Informe; copied from the Honduras job download folder"),
    ("REG-021", "https://gpe.gov.jm/wp-content/uploads/2024/11/2022-Jamaica-Integrated-Resource-Plan.pdf",
     "2022 Jamaica Integrated Resource Plan (IRP-2)", "Government of Jamaica, Generation Procurement Entity", "2024-11", RETRIEVED_COPY,
     "car/JAM_IRP_2022_gpe.pdf", "Jamaica", "no per-kW cost table; copied from the Jamaica job download folder"),
]

# Values: (source_id, pdf_page, locator, technology_as_printed, component, value, unit, currency_year,
#          value_year, geography, check_string)
# component: capital (total installed / overnight / development cost), capital_capitalized,
#            fixed_om, variable_om
V = []
def add(*row):
    V.append(row)

# REG-001 IRENA RPGC 2022 Table 2.1 (PDF p.75); Central America and the Caribbean data from 2012
for geo, y0, v0, v1, chk in [("Central America and the Caribbean", 2012, 2970, 1694, "andtheCaribbean*|2801|2970|3127|1694|1694|1694"),
                             ("Other South America", 2010, 2739, 1305, "OtherSouthAmerica|2513|2739|2863|892|1305|1504")]:
    add("REG-001", 75, "Table 2.1, weighted average", "Onshore wind total installed cost", "capital", v0, "USD/kW", 2022, y0, geo, chk)
    add("REG-001", 75, "Table 2.1, weighted average", "Onshore wind total installed cost", "capital", v1, "USD/kW", 2022, 2022, geo, chk)
add("REG-001", 159, "Hydropower chapter text", "Small hydropower weighted average total installed cost (2010-2015)", "capital", 3244, "USD/kW", 2022, "2010-2015", "Central America and the Caribbean", "CentralAmericaandtheCaribbeanitwasUSD3244/kW")

# REG-002 IRENA RPGC 2024
for geo, y0, v0, v1, chk in [("Central America and the Caribbean", 2012, 3153, 2108, "andtheCaribbean*|3153|3153|3153|2108|2108|2108"),
                             ("Other South America", 2012, 2521, 1492, "OtherSouthAmerica*|1698|2521|3945|1088|1492|1960")]:
    add("REG-002", 71, "Table 2.1, weighted average", "Onshore wind total installed cost", "capital", v0, "USD/kW", 2024, y0, geo, chk)
    add("REG-002", 71, "Table 2.1, weighted average", "Onshore wind total installed cost", "capital", v1, "USD/kW", 2024, 2024, geo, chk)
for geo, v0, v1, chk in [("Central America and the Caribbean", 2612, 1375, "theCaribbean|2042|2612|3956|939|1375|2288"),
                         ("Other South America", 3202, 1048, "OtherSouthAmerica|2234|3202|5440|596|1048|1634")]:
    add("REG-002", 95, "Table 3.1, weighted average", "Utility-scale solar PV total installed cost", "capital", v0, "USD/kW", 2024, 2015, geo, chk)
    add("REG-002", 95, "Table 3.1, weighted average", "Utility-scale solar PV total installed cost", "capital", v1, "USD/kW", 2024, 2024, geo, chk)
for tech, period, val, geo, chk in [
        ("Large hydropower (>10 MW) weighted average total installed cost", "2010-2017", 3652, "Central America", "CentralAmerica|3652|3058|3444|n.a."),
        ("Large hydropower (>10 MW) weighted average total installed cost", "2018-2024", 3058, "Central America", "CentralAmerica|3652|3058|3444|n.a."),
        ("Small hydropower (<=10 MW) weighted average total installed cost", "2010-2017", 3444, "Central America", "CentralAmerica|3652|3058|3444|n.a."),
        ("Large hydropower (>10 MW) weighted average total installed cost", "2010-2017", 2519, "Other South America", "OtherSouthAmerica|2519|2913|3307|n.a."),
        ("Large hydropower (>10 MW) weighted average total installed cost", "2018-2024", 2913, "Other South America", "OtherSouthAmerica|2519|2913|3307|n.a."),
        ("Small hydropower (<=10 MW) weighted average total installed cost", "2010-2017", 3307, "Other South America", "OtherSouthAmerica|2519|2913|3307|n.a.")]:
    add("REG-002", 149, "Table 6.3", tech, "capital", val, "USD/kW", 2024, period, geo, chk)

# REG-003 IRENA RPGC 2025
for geo, v0, v1, chk in [("Other South America", 2663, 1314, "OtherSouthAmerica|2351|2663|3014|1095|1314|2252"),
                         ("Other North America (Canada and Mexico)", 2958, 1810, "OtherNorthAmerica|1925|2958|4145|1623|1810|2250")]:
    add("REG-003", 46, "Table 2.1, weighted average", "Onshore wind total installed cost", "capital", v0, "USD/kW", 2025, 2015, geo, chk)
    add("REG-003", 46, "Table 2.1, weighted average", "Onshore wind total installed cost", "capital", v1, "USD/kW", 2025, 2025, geo, chk)
for geo, v0, v1, chk in [("Central America and the Caribbean", 2675, 931, "theCaribbean|2091|2675|4052|649|931|1016"),
                         ("Other South America", 3280, 867, "OtherSouthAmerica|2289|3280|5573|488|867|1538"),
                         ("Other North America (Canada and Mexico)", 2706, 887, "OtherNorthAmerica|2035|2706|6153|702|887|1777")]:
    add("REG-003", 62, "Table 3.1, weighted average", "Utility-scale solar PV total installed cost", "capital", v0, "USD/kW", 2025, 2015, geo, chk)
    add("REG-003", 62, "Table 3.1, weighted average", "Utility-scale solar PV total installed cost", "capital", v1, "USD/kW", 2025, 2025, geo, chk)
add("REG-003", 106, "Section 6 text (Figure 6.5)", "Large hydropower (>10 MW) weighted average total installed cost", "capital", 3133, "USD/kW", 2025, "2018-2025", "Central America and the Caribbean", "USD3133/kWinCentralAmericaandtheCaribbean")

# REG-004 IRENA Roadmap Central America, Annex B Table 16 (PDF p.95); no currency year
for tech, vals in [("Hydropower", (1445, 1445, 1430)), ("Solar PV - utility", (1200, 590, 320)),
                   ("Solar PV - distributed generation", (1400, 680, 375)), ("Bioenergy and waste", (1500, 1500, 1500)),
                   ("Geothermal", (4600, 4175, 3860)), ("Wind onshore", (1420, 1300, 1220)), ("Solar CSP", (7350, 5355, 4535)),
                   ("Natural gas (Combined Cycle)", (890, 890, 890))]:
    for y, v in zip((2018, 2030, 2050), vals):
        add("REG-004", 95, "Annex B Table 16", tech, "capital", v, "USD/kW", "not stated", y, "Central America", str(v))

# REG-005 ICE PEG 2024-2040: Tabla 10.9 overnight (PDF p.153) and Tabla 10.8 capitalized and fixed O&M (PDF p.151)
ICE = [  # name, overnight 10.9, capitalized 10.8, fixed O&M 10.8
    ("Hidro Genericos (20 MW, run-of-river: useful volume 0)", 4500, 5710, 41), ("Fourth Cliff", 5276, 6666, 46), ("PCH PAACUME", 3735, 4173, 71),
    ("Toro Amarillo", 3647, 4171, 41), ("Chimirol", 4010, 5357, 41), ("Diquis", 5986, 8670, 20), ("Diquis Minicentral", 0, 0, 106),
    ("RG-430 CM 360", 6317, 7719, 42), ("RG-430 CM 318", 5910, 7293, 37),
    ("Quijote (wind)", 1939, 2120, 50), ("Tejona Repotenciacion (wind)", 1845, 2015, 50), ("Las Pavas (wind)", 1948, 2129, 50),
    ("Montosa (wind)", 1725, 1886, 50), ("San Jorge (wind)", 1722, 1882, 50), ("MOVASA 2 (wind)", 1776, 1942, 50), ("Eolico Genericos (10 MW)", 1900, 2077, 50),
    ("Huacas (solar)", 1227, 1330, 17), ("Abangares (solar)", 1190, 1289, 15), ("Las Delicias (solar)", 939, 1062, 16), ("San Antonio (solar)", 1074, 1164, 15),
    ("Numu (solar)", 999, 1073, 17), ("Los Tecales (solar)", 800, 859, 17), ("Los Mangos (solar)", 892, 958, 17), ("Colorado (solar)", 875, 940, 17),
    ("Las Canas (solar)", 850, 913, 17), ("Solar Genericos (10 MW)", 1100, 1182, 17), ("Solar Tracking 1D Genericos (10 MW)", 1500, 1612, 17),
    ("Borinquen 1 (geothermal, remaining investment)", 5757, 7036, 160), ("Borinquen 2 (geothermal)", 6645, 8202, 90), ("Plazoleta PLB-01 (geothermal)", 6645, 7785, 160),
    ("Geotermico Genericos (55 MW)", 6645, 8202, 160), ("Motores Combustion Interna Alquiler", 0, 0, 201), ("Motores Media Velocidad Bunker (20 MW)", 1800, 2056, 40),
    ("Turbinas de Gas Diesel (20 MW)", 1200, 1371, 18), ("Ciclo Combinado Diesel", 1500, 1813, 14), ("Ciclo Combinado GNL FSRU Alquiler", 1500, 1813, 196.5),
    ("Ciclo Combinado Terminal GNL", 2833, 3662, 14), ("Ciclo Combinado GNL", 1500, 1813, 14), ("Turbina de Gas Diesel Alquiler", 0, 0, 266),
    ("Biomasa Genericos (10 MW, sugarcane)", 1750, 1896, 37), ("Baterias Genericas 30 MW", 1400, 1528, 40), ("Baterias Genericas 60 MW", 1400, 1528, 40),
    ("Turbo-Bombeo Genericos", 5090, 6244, 27)]
for name, on, cap, fom in ICE:
    add("REG-005", 153, "Tabla 10.9, Costo de inversion overnight", name, "capital", on, "USD/kW", 2023, "candidate (Dec-2023 prices)", "Costa Rica", f"{on:,}".replace(",", ""))
    add("REG-005", 151, "Tabla 10.8, Inversion unitaria (capitalizado)", name, "capital_capitalized", cap, "USD/kW", 2023, "candidate (Dec-2023 prices)", "Costa Rica", f"{cap:,}".replace(",", ""))
    add("REG-005", 151, "Tabla 10.8, Costo fijo O&M unitario", name, "fixed_om", fom, "USD/kW-year", 2023, "candidate (Dec-2023 prices)", "Costa Rica", str(fom))

# REG-006 Honduras PIEG 2026-2035 Informe Tabla 19 (PDF p.46), referenced to 2024
HON = [  # technology, size MW, capex, fixed O&M, variable O&M (printed)
    ("Motor de combustion interna a gas natural", "20", "1,586.68", "14.00", "5.00"), ("Motor de combustion interna a gas natural", "50", "1,338.99", "14.00", "5.00"),
    ("Motor de combustion interna a gas natural", "100", "1,168.21", "14.00", "5.00"),
    ("Motor de combustion interna a gas natural/bunker/diesel", "20", "1,695.95", "14.00", "5 gas natural/diesel y 7 bunker"),
    ("Motor de combustion interna a gas natural/bunker/diesel", "50", "1,440.41", "14.00", "5 gas natural/diesel y 7 bunker"),
    ("Motor de combustion interna a gas natural/bunker/diesel", "100", "1,269.20", "14.00", "5 gas natural/diesel y 7 bunker"),
    ("Motor de combustion interna en ciclo combinado a gas natural", "250", "1,346.19", "14.00", "5.00"),
    ("Turbina de gas en ciclo abierto a gas natural/diesel/LPG", "30", "1,496.90", "20.00", "6.00"),
    ("Turbina de gas en ciclo abierto a gas natural/diesel/LPG", "50", "1,345.42", "20.00", "6.00"),
    ("Turbina de gas en ciclo abierto a gas natural/diesel/LPG", "70", "1,234.80", "20.00", "6.00"),
    ("Turbina de gas en ciclo combinado a gas natural", "250", "1,437.59", "16.00", "3.5"),
    ("Eolica", "50", "1,722.64", "34.71", "0.00"), ("Eolica", "100", "1,698.12", "34.91", "0.00"), ("Eolica", "200", "1,557.91", "34.71", "0.00"),
    ("Geotermica", "20", "6,179.24", "160.66", "1.50"),
    ("Hidroelectrica de embalse", "<100", "5,100.00", "37.42", "0.00"), ("Hidroelectrica de embalse", ">100", "5,100.00", "37.93", "0.00"),
    ("Hidroelectrica de pasada", "<10", "3,786.50", "40.00", "0.00"), ("Hidroelectrica de pasada", ">100", "4,387.24", "36.63", "0.00"),
    ("Solar fotovoltaica", "20", "1,227.42", "21.25", "0.00"), ("Solar fotovoltaica", "50", "1,138.48", "21.25", "0.00"), ("Solar fotovoltaica", "150", "889.44", "21.25", "0.00"),
    ("Sistema de almacenamiento de energia en baterias", "15", "1,229.20", "42.00", "0.00"), ("Sistema de almacenamiento de energia en baterias", "50", "1,135.71", "42.00", "0.00"),
    ("Sistema de almacenamiento de energia en baterias", "150", "925.65", "42.00", "0.00"),
    ("Central hibrida: Eolica con bateria (10%)", "50", "1,868.76", "41.14", "0.00"), ("Central hibrida: Eolica con bateria (10%)", "100", "1,829.23", "41.14", "0.00"),
    ("Central hibrida: Eolica con bateria (10%)", "200", "1,704.02", "40.12", "0.00"),
    ("Central hibrida: Solar fotovoltaica con bateria (30%)", "20", "1,516.86", "40.31", "0.00"), ("Central hibrida: Solar fotovoltaica con bateria (30%)", "50", "1,434.72", "40.31", "0.00"),
    ("Central hibrida: Solar fotovoltaica con bateria (30%)", "100", "1,188.98", "40.31", "0.00"), ("Central hibrida: Solar fotovoltaica con bateria (30%)", "150", "1,168.47", "40.31", "0.00"),
    ("Central hibrida: Solar fotovoltaica 25 MW + bateria 25 MW", "25", "2,901.94", "63.25", "0.00"),
    ("Central hibrida: Solar fotovoltaica 50 MW + bateria 75 MW", "50", "2,750.90", "84.25", "0.00"),
    ("Central hibrida: Solar fotovoltaica 125 MW + bateria 100 MW", "125", "1,572.28", "54.85", "0.00"),
    ("Central hibrida: Solar fotovoltaica 150 MW + hidroelectrica de bombeo 150 MW", "150", "4,900.03", "48.04", "2.50"),
    ("Central hibrida: Solar fotovoltaica 1,680.80 MW + bateria 1,000 MW + bombeo 1,200 MW", "1,680.80", "2,790.58", "56.67", "2.50")]
def f(s):
    return float(s.replace(",", ""))
for tech, size, capex, fom, vom in HON:
    t = f"{tech}, {size} MW"
    add("REG-006", 46, "Tabla 19", t, "capital", f(capex), "USD/kW", 2024, "2024 reference", "Honduras", capex)
    add("REG-006", 46, "Tabla 19", t, "fixed_om", f(fom), "USD/kW-year", 2024, "2024 reference", "Honduras", fom)
    if "bunker" in vom:
        add("REG-006", 46, "Tabla 19", t + " (gas natural/diesel)", "variable_om", 5.0, "USD/MWh", 2024, "2024 reference", "Honduras", "5gasnatural/diésely7búnker")
        add("REG-006", 46, "Tabla 19", t + " (bunker)", "variable_om", 7.0, "USD/MWh", 2024, "2024 reference", "Honduras", "5gasnatural/diésely7búnker")
    else:
        add("REG-006", 46, "Tabla 19", t, "variable_om", f(vom), "USD/MWh", 2024, "2024 reference", "Honduras", vom)

# REG-007 Guatemala PEIG 2026-2050 Tabla 6 (PDF p.35); no currency year
for tech, c, fo, vo in [("Cogeneracion", 1929, 77, 10), ("Geotermica", 6500, 151, 5), ("Hidroelectrica de Pasada", 3900, 34, 22.73),
                        ("Hidroelectrica de Embalse", 3500, 50, 60.19), ("Eolica", 1600, 28, 1.5), ("Fotovoltaica", 1190, 20, 1.57),
                        ("Bateria acoplada (200 MWh)", 673, 18, None), ("Combustion Interna (Gas Natural)", 1400, 20, 5),
                        ("Termoelectrica (Gas Natural)", 4091, 7, 2), ("Turbo gas (Gas Natural)", 4392, 10, 7), ("Ciclo Combinado (Gas Natural)", 4256, 12, 5)]:
    add("REG-007", 35, "Tabla 6", tech, "capital", c, "USD/kW", "not stated", "candidate", "Guatemala", f"{c:,}")
    add("REG-007", 35, "Tabla 6", tech, "fixed_om", fo, "USD/kW-year", "not stated", "candidate", "Guatemala", str(fo))
    if vo is not None:
        add("REG-007", 35, "Tabla 6", tech, "variable_om", vo, "USD/MWh", "not stated", "candidate", "Guatemala", str(vo))

# REG-010 El Salvador PIEGE 2020-2030 Tablas 3 and 4 (PDF p.13 and p.14); no currency year
for name, tech, c, fo, p in [("EcoSolar", "Fotovoltaico", 1515, 19, 13), ("Sonsonate Energia", "Fotovoltaico", 1500, 19, 13), ("Chaparral", "Hidroelectrico", 2283, 17, 13),
                             ("Ventus", "Eolico", 2200, 55, 13), ("EDP", "GNL", 2116, 27, 13), ("Berlin U5", "Geotermico", 5000, 115, 14),
                             ("Chinameca", "Geotermico", 4000, 115, 14), ("San Vicente", "Geotermico", 4000, 115, 14), ("Amp. Chinameca", "Geotermico", 4000, 115, 14),
                             ("Amp. San Vicente", "Geotermico", 4000, 115, 14), ("FV1 to FV5 (five rows)", "Fotovoltaico", 1100, 19, 14),
                             ("EO1, EO2, Eolico CEL (three rows)", "Eolico", 2000, 55, 14)]:
    add("REG-010", p, "Tabla 3/4 (project)", f"{name} ({tech})", "capital", c, "$/kW", "not stated", "project", "El Salvador", str(c))
    add("REG-010", p, "Tabla 3/4 (project)", f"{name} ({tech})", "fixed_om", fo, "$/kW-year", "not stated", "project", "El Salvador", str(fo))

# REG-011 Mexico PLADESE Tabla 3.1 (DOF HTML), CAIO average (max, min) and fixed O&M average
for tech, a, mx, mn, fa in [("Turbogas", 727, 1093, 461, 9768), ("Ciclo combinado", 843, 1641, 679, 15037), ("Combustion interna", 1265, 1288, 1242, 13137),
                            ("Carboelectrica", 1895, 2125, 1769, 38506), ("Nuclear", 9760, 10322, 9197, 152321), ("Geotermoelectrica", 3983, 3983, 3983, 176433),
                            ("Hidroelectrica", 3406, 3902, 3012, 82195), ("Eolica", 1820, 2915, 1368, 37058), ("Solar fotovoltaica", 1017, 1017, 1017, 10366),
                            ("Banco de Baterias", 2109, 3057, 1019, 36652)]:
    add("REG-011", 0, "Tabla 3.1 (CAIO 6.89%, average)", tech, "capital_capitalized", a, "USD/kW bruto", "not stated", "2025-2039 plan", "Mexico", f"{a:,}")
    add("REG-011", 0, "Tabla 3.1 (fixed O&M average)", tech, "fixed_om", fa, "USD/MW-year", "not stated", "2025-2039 plan", "Mexico", f"{fa:,}")

# REG-015 Jamaica IRP 2018, Appendix C (PDF p.182) and BESS text (PDF p.107); 2018 USD
for tech, c, fom_m, vom in [("Wind (candidate projects)", "1870", "3.00", "2.5"), ("Solar PV (candidate projects)", "1350", "2.60", "0"),
                            ("Run of River Hydro (candidate projects)", None, "10.00", "0.0"), ("Waste to Energy (Soapberry)", "7200", "16.60", "7.0"),
                            ("Combustion Turbine (GTX), natural gas/ADO", "800.0", "1.0", "1.0"), ("Combined Cycle (NGCC), natural gas/ADO", "1600.0", "1.2", "2.6"),
                            ("Medium Speed Diesel (HFO)", "1400.0", "3.0", "6.5"), ("Medium Speed Diesel (NG)", "1400.0", "2.39", "6.5")]:
    if c is not None:
        add("REG-015", 182, "Appendix C", tech, "capital", float(c), "USD/kW (thermal: incl. IDC)", 2018, "candidate", "Jamaica", c)
    add("REG-015", 182, "Appendix C", tech, "fixed_om", float(fom_m), "USD/kW-month", 2018, "candidate", "Jamaica", fom_m)
    add("REG-015", 182, "Appendix C", tech, "variable_om", float(vom), "USD/MWh", 2018, "candidate", "Jamaica", vom)
add("REG-015", 107, "Planned and potential battery storage", "Transmission-connected BESS 24.5 MW / 6 MWh", "capital", 816, "USD/kW", 2018, "candidate", "Jamaica", "$816/kW")
add("REG-015", 107, "Planned and potential battery storage", "Transmission-connected BESS 24.5 MW / 6 MWh", "fixed_om", 50, "USD/kW-year", 2018, "candidate", "Jamaica", "$50/kWperyear")

# REG-016 DR PEN 2022-2036 generic projects (Tablas 204 to 229); no currency year
for tab, page, tech, c, fo, vo in [(204, 336, "Fotovoltaico angulo fijo 50 MWAC", "1,052", "13,500", None), (206, 337, "Fotovoltaico tracker 1 eje 150 MWAC", "1,248", "15,330", None),
                                   (208, 338, "Fotovoltaico tracker 1 eje + almacenamiento 200 MWh", "1,612", "32,330", None),
                                   (212, 340, "Eolico Onshore 50 MW", "1,742", "35,140", None), (214, 342, "Eolico Offshore 210 MW", "2,600", "67,250", None),
                                   (216, 343, "Hidroelectrica 100 MW (reservoir)", "2,769", "42,010", None), (218, 344, "Incineradora RSU 50 MW", "3,645", "125,720", "13.24"),
                                   (220, 345, "Ciclo combinado gas natural 418 MW", "1084", "14,100", "2.55"), (223, 347, "Turbina de vapor 650 MW", "3,676", "40,580", "4.50"),
                                   (226, 349, "Turbina de gas ciclo simple 105 MW", "1,175", "16,300", "4.70"), (229, 350, "Motores combustion interna 220 MW", "1,100", "35,160", "5.69")]:
    add("REG-016", page, f"Tabla {tab}", tech, "capital", f(c), "US$/kW", "not stated", "generic (2021 study)", "Dominican Republic", c)
    add("REG-016", page, f"Tabla {tab}", tech, "fixed_om", f(fo), "US$/MW-year", "not stated", "generic (2021 study)", "Dominican Republic", fo)
    if vo:
        add("REG-016", page, f"Tabla {tab}", tech, "variable_om", f(vo), "US$/MWh", "not stated", "generic (2021 study)", "Dominican Republic", vo)

# REG-017 Barbados IRRP draft Table E.1 (PDF p.190 and p.191); no price base
for tech, c, p in [("Medium Speed Rec. Engines", "2,904.00", 190), ("Gas Turbines", "2,471.00", 190), ("Woody Biomass", "10,032.00", 190), ("Landfill Gas", "7,075.00", 190),
                   ("Municipal Waste", "24,000.00", 190), ("On-shore Wind", "4,208.57", 191), ("PV (Ground Mounted)", "3,121.31", 191),
                   ("Batteries (4h)", "2631.82", 191)]:
    add("REG-017", p, "Table E.1", tech, "capital", f(c), "BBD per kW (labelled BBD/MW)", "not stated", 2020, "Barbados", c)

# REG-018 CCREEE (PDF p.18), ranges and single benchmarks
for tech, txt, geo in [("Solar PV residential", "658-4,236", "Global benchmark"), ("Solar PV commercial", "651-2974", "Global benchmark"),
                       ("Solar PV utility", "883", "Global benchmark"), ("Solar PV utility", "1,730-3,150", "Jamaica"), ("Wind", "1,355", "Global"),
                       ("Wind", "2,062", "Latin America and the Caribbean"), ("Wind", "1,875-2,489", "Jamaica"), ("Storage lithium 4-hour", "350 / kWh", "Global")]:
    add("REG-018", 18, "Regional Benchmarks table", tech, "capital", txt, "USD/kW", "not stated (2020 benchmark)", 2020, geo, txt.replace(" ", ""))

# REG-019 PREPA IRP 2019, Exhibits 6-33 (PDF p.109) and 6-44 (PDF p.121), base case, 2018 USD
for cod, pv, pvf, wd, wdf in [(2019, 1.58, 11.85, 2.01, 67.58), (2020, 1.48, 10.88, 2.01, 67.08), (2021, 1.41, 10.14, 2.02, 66.58), (2022, 1.39, 10.03, 2.02, 66.08),
                              (2023, 1.38, 9.92, 2.02, 65.59), (2024, 1.36, 9.81, 2.03, 65.09), (2025, 1.34, 9.70, 2.03, 64.59), (2030, 1.26, 9.15, 2.05, 62.11),
                              (2035, 1.21, 8.77, 2.07, 59.63), (2038, 1.18, 8.55, 2.08, 58.13)]:
    add("REG-019", 109, "Exhibit 6-33, Overnight Cost Puerto Rico 100 MW", "Utility-scale solar PV", "capital", pv * 1000, "USD/kWac (printed $2018/Wac)", 2018, cod, "Puerto Rico", f"{pv:.2f}")
    add("REG-019", 109, "Exhibit 6-33, Fixed O&M", "Utility-scale solar PV", "fixed_om", pvf, "USD/kW-year", 2018, cod, "Puerto Rico", f"{pvf:.2f}")
    add("REG-019", 121, "Exhibit 6-44, Overnight Cost Puerto Rico 100 MW", "Onshore wind", "capital", wd * 1000, "USD/kW (printed $2018/Watt)", 2018, cod, "Puerto Rico", f"{wd:.2f}")
    add("REG-019", 121, "Exhibit 6-44, Fixed O&M", "Onshore wind", "fixed_om", wdf, "USD/kW-year", 2018, cod, "Puerto Rico", f"{wdf:.2f}")

# REG-009 Panama PESIN 2025-2039: generic thermal candidates (PDF p.67); project rows summarised in GAPS
for tech, cap, fo, c in [("Motor de Media Velocidad (Diesel), Progreso Energy 1.05 MW", "1.05", "8", "1810"),
                         ("Turbina de Gas Aeroderivada (GNL) 150A", "150", "12.058", "796.935"),
                         ("Turbina de Gas Aeroderivada (GNL) 250A to 250F", "250", "6.768", "567.625")]:
    add("REG-009", 67, "Tabla 4.12", tech, "capital", f(c), "B/./kW", "not stated", "candidate", "Panama", c)
    add("REG-009", 67, "Tabla 4.12", tech, "fixed_om", f(fo), "B/./kW-year", "not stated", "candidate", "Panama", fo)
