"""Write sources_HON.csv, search_log_HON.csv and manual_downloads_HON.csv (run: python -I write_meta_HON.py)."""
import csv
import os

CC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = "2026-11-22"

S = [
    ["HON-001", "https://www.ine.gob.hn/wp-content/uploads/2025/05/Parque-Vehicular-2017-2021.pdf", "El Parque Vehicular de Honduras 2017-2021",
     "Instituto Nacional de Estadistica (INE), Secretaria del Despacho Presidencial, with records of the Instituto de la Propiedad", "2025-05 (upload date)", D,
     "downloads/HON/INE_Parque-Vehicular-2017-2021.pdf", "Cuadro 1 (fleet by type 2020 and 2021) and section 3.1, PDF p. 4 to 5; section II (vehicle imports from SARAH customs records)",
     "Registered fleet 2,415,192 vehicles at end 2021: motorcycles 1,084,706 (45 percent), pick up and jeep 436,860, turismo 405,075, buses and similar 50,085, heavy vehicles 82,365. Vehicle imports about 880 million US$ in 2021 (454 million in 2020). Counts only: no fleet age, distance or price by type. Used as national comparison for OperationalLife and the motorcycle price assumption."],
    ["HON-002", "https://www.undp.org/sites/g/files/zskgke326/files/migration/hn/cadena-valor-cafe-2018-HEIFER-IHCAFE-PNUD.pdf", "Analisis de la cadena de valor de cafe en Honduras",
     "PNUD Honduras, HEIFER and Instituto Hondureno del Cafe (IHCAFE)", "2018-05", D, "downloads/HON/cadena-valor-cafe-2018-HEIFER-IHCAFE-PNUD.pdf",
     "Tabla 7 Costos de produccion por tamano de la finca, PDF p. 16; Tabla 15 costos y retornos, PDF p. 30; field data of the 2015-2016 harvest, PDF p. 4",
     "Production cost per manzana: under 2 mz 26,879.80 L, to 5 mz 25,482.52, to 20 mz 27,460.48, over 20 mz 31,610.23 (administration and financing interest excluded; family labour often not counted). Yields 15.9 to 18.3 qq per mz."],
    ["HON-003", "https://ine.gob.hn/wp-content/uploads/2026/01/Informe-resultados-preliminares-CAN-2024-1.pdf", "Censo Agropecuario Nacional 2024: informe de resultados preliminares",
     "Instituto Nacional de Estadistica (INE) Honduras", "2026-01", D, "downloads/HON/INE_Informe-resultados-preliminares-CAN-2024.pdf",
     "Notes under the crop tables, PDF p. 29, 32, 34 to 36, 38, 40: Manzanas a hectareas se dividio entre 1.43",
     "Official national conversion: 1 manzana = 1 / 1.43 = 0.6993 ha (10,000 square varas give 0.6987 ha, 0.1 percent apart). Used to convert L per manzana to L per hectare."],
    ["HON-004", "https://api.worldbank.org/v2/country/HND/indicator/PA.NUS.FCRF?format=json&date=2015:2024&per_page=100",
     "World Development Indicators: Official exchange rate (LCU per US$, period average), PA.NUS.FCRF, Honduras", "World Bank", "data as published to 2026-11", D,
     "downloads/HON/WB_WDI_PA.NUS.FCRF_HND_2015_2024.json", "JSON records date 2016 and 2023", "2016 = 22.835018390426 L per US$; 2023 = 24.6016468236818 L per US$."],
    ["HON-005", "https://programs.wcs.org/Portals/234/Newsletter/Boletin7EUDeSIRA/Perfil%20del%20mercado%20y%20las%20cadenas%20de%20granos%20basicos_Honduras.pdf",
     "Perfil del mercado y las cadenas de granos basicos en Wampusirpi, Honduras (Publicacion CIAT No. 561)",
     "Bucardo E M, Charry A, Claros L, Wiegel J; Centro Internacional de Agricultura Tropical (CIAT), Alliance of Bioversity International and CIAT", "2024", D,
     "downloads/HON/Perfil_mercado_cadenas_granos_basicos_Honduras.pdf",
     "Text PDF p. 13 (cost per hectare of beans L 15,700, 666 USD; rice L 22,050, USD 890.90); Anexo 2 Estimaciones de costos de produccion en la zona, PDF p. 23 (ARROZ) and p. 24 (FRIJOL)",
     "Bean budget total costs 15,730 L; rice 22,050 L; traditional low-input practice in one municipality of La Mosquitia, all labour (family and hired) valued at the local day wage. Beans used for AG_FRI; rice cited as a lower-bound comparison only."],
]

L = [
    ["vehicles CapitalCost base prices", "UN Comtrade public API (Honduras imports, HS 8702 8703 8704 8711)",
     "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=340&period=2019&partnerCode=0&flowCode=M&cmdCode=870210 to 871160 (6-digit list)", D,
     "Downloaded 2019, 2022, 2023, 2024 (downloads/HON/comtrade_HON_imports_vehicles_*.json). Not used: Honduras does not report (isReported false), quantities are estimated (isQtyEstimated true, fractional units such as 5153.187 for HS 870323), and 2022 to 2024 return no rows."],
    ["vehicles CapitalCost base prices", "Web search: SAR or Aduanas vehicle valuation table", "SAR Honduras tabla de valores vehiculos importacion pdf", D,
     "No SAR or Aduanas valuation table online; results are press notes on import taxes and a Guatemalan SAT table (not Honduran). Not used."],
    ["vehicles CapitalCost base prices", "Web search: average CIF value per imported vehicle by type", "Honduras valor CIF promedio vehiculos importados turismos pick up motocicletas", D,
     "Only totals (INE: about 880 million US$ of vehicle imports in 2021) and press notes; most imports are used vehicles. No unit value by class. Not used."],
    ["vehicles CapitalCost, Ref.km.BY", "Honduras national electric mobility strategy (draft, Secretaria de Energia)",
     "https://mobilityportal.lat/wp-content/uploads/2022/08/Propuesta-de-Estrategia-de-Movilidad-Electrica-en-Honduras.pdf", D,
     "HTTP 403 for scripts (also the mobilityportal.eu redirect, and WebFetch). Listed as manual."],
    ["vehicles CapitalCost electric bus", "GCF concept note, Fostering Sustainable Urban Mobility in Tegucigalpa (CABEI, 2020)",
     "https://www.greenclimate.fund/sites/default/files/document/25320-fostering-sustainable-urban-mobility-efficient-and-low-emission-transport-tegucigalpa.pdf", D,
     "Downloaded (downloads/HON/GCF_25320_concept_note_Tegucigalpa_urban_mobility.pdf). Pilot of 8 electric buses; the component budget mixes buses and infrastructure, no price per bus, no km. Not used."],
    ["vehicles all", "Read the Docs lead (endrch-hon, transport inputs and references)", "https://endrch-hon.readthedocs.io/en/latest/1_transport/4_referencias.html", D,
     "Lead only. Transport references are Dominican Republic documents (DGII fleet, DR CCDR, Godinez-Zamora 2020), which confirms the Honduras vehicle sheet was built from the Dominican template. No Honduran vehicle source listed."],
    ["vehicles Ref.km.BY and OperationalLife", "Honduras NDC, BUR, BTR and NIR copies (read-only scout folder)", "text search for km per year, kilometres travelled, vehicle life", D,
     "No distance per vehicle or vehicle life by type. Not used."],
    ["vehicles OperationalLife", "INE fleet bulletin 2017-2021", "https://www.ine.gob.hn/wp-content/uploads/2025/05/Parque-Vehicular-2017-2021.pdf", D,
     "Downloaded with Windows curl (the temp.ine.gob.hn host in search results does not resolve). Counts by type only, no age distribution. Cited as HON-001 for context."],
    ["vehicles Ref.km.BY taxi", "GEN-104 and Honduran sources", "downloads/GEN_vehicles/Plan_Estrategico_Nacional_Movilidad_Electrica_2020.pdf", D,
     "No taxi distance in GEN or Honduran sources. Taxi row is an ASSUMPTION."],
    ["AG_* crop costs", "Web search: SAG, DICTA, UPEG costos de produccion por manzana", "DICTA SAG Honduras costos de produccion por manzana maiz frijol arroz pdf", D,
     "No SAG or DICTA cost table online; press notes only (La Prensa: maize about L 24,200 per manzana, year unclear). Not used."],
    ["AG_RIC AG_FRI", "CIAT 2024, granos basicos en Wampusirpi",
     "https://programs.wcs.org/Portals/234/Newsletter/Boletin7EUDeSIRA/Perfil%20del%20mercado%20y%20las%20cadenas%20de%20granos%20basicos_Honduras.pdf", D,
     "Downloaded (HON-005). Cost per ha for beans (used, confirmed) and rice (low-input upland rice; cited as lower bound in the rice ASSUMPTION)."],
    ["AG_CAF VariableCost", "IHCAFE / UNDP coffee value chain 2018",
     "https://www.undp.org/sites/g/files/zskgke326/files/migration/hn/cadena-valor-cafe-2018-HEIFER-IHCAFE-PNUD.pdf", D, "Downloaded (HON-002). Cost per manzana by farm size used."],
    ["manzana to hectare", "FAO documents and INE census report", "https://ine.gob.hn/wp-content/uploads/2026/01/Informe-resultados-preliminares-CAN-2024-1.pdf", D,
     "INE CAN 2024 states the factor 1.43 manzanas per hectare (HON-003). Two FAO Honduras documents checked (ar886s, cc4289es) give no explicit factor; deleted after reading."],
    ["AG_MAI AG_BAN AG_MEL AG_PLM AG_SGC AG_LEG", "Web search: FHIA, DICTA crop budgets per hectare or manzana",
     "FHIA OR DICTA costo de produccion por hectarea OR por manzana arroz Honduras 2019 2020", D,
     "Only a Zamorano thesis on one experimental plot and the FHIA annual report (no crop budget table). ASSUMPTION with FAOSTAT gross output value as comparison."],
    ["exchange rate", "World Bank WDI API", "https://api.worldbank.org/v2/country/HND/indicator/PA.NUS.FCRF?format=json&date=2015:2024&per_page=100", D, "Downloaded (HON-004)."],
    ["IMP* VariableCost", "GEN-201 FAOSTAT trade unit values", "GEN/faostat_trade_unit_values.csv", D,
     "Honduras rows avg_2019_2023 used; bananas recomputed without the flag X year 2022; melons unusable (about 1 t per year), ASSUMPTION at the FAO producer price."],
    ["waste", "GEN-204 GEN-206", "GEN/gen_sector_values.csv", D, "Used (lower-middle income ranges of What a Waste 2.0 for Honduras)."],
    ["EmissionsPenalty contam_agua salud_residuos turismo_residuos", "GEN sector notes and GEN manual list (IDB publications)",
     "https://publications.iadb.org/es/lineamientos-sectoriales-para-la-gestion-de-residuos-solidos-y-el-avance-hacia-la-economia-circular", D,
     "Not retried: GEN reports bot-verification pages for every IDB PDF. Rows are ASSUMPTION, listed as manual."],
]

M = [
    ["https://publications.iadb.org/es/lineamientos-sectoriales-para-la-gestion-de-residuos-solidos-y-el-avance-hacia-la-economia-circular",
     "Correal, Rihm et al. (2023). Lineamientos sectoriales para la gestion de residuos solidos y el avance hacia la economia circular. IDB",
     "Public health, water contamination and tourism externalities of waste disposal (origin of contam_agua, salud_residuos, turismo_residuos)",
     "HON_WASTE EmissionsPenalty contam_agua, salud_residuos, turismo_residuos, 2018 to 2050 (99 cells, class assumption meanwhile)"],
    ["https://publications.iadb.org/es/sostenibilidad-financiera-de-la-gestion-de-residuos-solidos-en-america-latina-y-el-caribe",
     "Correal, Faleiro, Piamonte, Rihm, Zambrano (2023). Sostenibilidad financiera de la gestion de residuos solidos en America Latina y el Caribe. IDB-TN-2663",
     "Waste facility costs (collection, landfill, open dump) that may be the origin of the model values",
     "HON_WASTE BLEND_NO_DCOLL, LANDFILL, NO_CONTR_OD (sourced meanwhile from CEPAL 2016 and What a Waste 2.0)"],
    ["https://www.mobilityportal.eu/wp-content/uploads/2022/08/Propuesta-de-Estrategia-de-Movilidad-Electrica-en-Honduras.pdf",
     "Propuesta de Estrategia Nacional de Movilidad Electrica en Honduras (draft, Secretaria de Energia)",
     "Honduran vehicle prices, electric vehicle prices, distances per vehicle type and vehicle life, if the draft holds them",
     "HON_ENERGY Vehicle Techs CapitalCost base-year cells, Ref.km.BY per group, OperationalLife (sourced meanwhile from GEN-104, GEN-101, GEN-103)"],
]

for name, header, rows in (("sources_HON.csv", "id,url,title,publisher,date,retrieval_date,downloaded_file,page_or_table,notes", S),
                           ("search_log_HON.csv", "row,lead,url_or_query,date,result", L),
                           ("manual_downloads_HON.csv", "url,title,what_it_would_source,proposal_rows_waiting", M)):
    with open(os.path.join(CC_DIR, name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header.split(","))
        w.writerows(rows)
print("written")
