"""Write sources_JAM.csv, search_log_JAM.csv and manual_downloads_JAM.csv."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CC_DIR = os.path.dirname(HERE)
D = "2026-11-22"

SOURCES = [
    ("JAM-001", "https://japarliament.gov.jm/attachments/article/2548/Electronic-Vechile-Policy.pdf", "Electric Vehicle Policy",
     "Government of Jamaica, Ministry of Science, Energy and Technology (copy hosted by the Houses of Parliament)", "2023-06", D,
     "downloads/JAM/Jamaica_Electric_Vehicle_Policy_2023.pdf", "whole document (110 PDF pages) read by text search",
     "No vehicle prices, annual distances or vehicle lives. Context only (concessionary import duty for EVs, charging rules); not cited in proposals."),
    ("JAM-002", "https://our.org.jm/wp-content/uploads/2021/05/OURs-EV-Stakeholders-Consultation-Document-2021-May-12.pdf",
     "Proposals for a Regulatory Framework to Facilitate the Penetration of EV in Jamaica, Consultation Document 2021|ELE|003|CON.001",
     "Office of Utilities Regulation (OUR), Jamaica", "2021-04", D,
     "downloads/JAM/OUR_EV_Stakeholders_Consultation_2021.pdf",
     "Table 10, Table 11 and Figures 5 to 7, printed pp. 81 to 83; 15-year useful life, printed p. 20 and p. 82",
     "Total acquisition cost under the Jamaican tax and duty regime (Figure 6): Nissan Leaf 48,386.50 US$, Honda Fit 34,477.76, Nissan Versa Note 33,444.24. "
     "Total life-cycle cost (Table 11): 63,313; 59,173; 58,139 US$. 20,000 km per year is the annual average distance an individual travels (p. 82). "
     "15-year useful life of EVs and ICEs. Maintenance components read from Figure 6: about 1,369 (Leaf) and 6,120 (Fit, Note) US$ over 15 years. Currency year taken as 2021."),
    ("JAM-003", "https://jamaica-gleaner.com/article/news/20220531/us6-million-contract-signed-50-jutc-buses",
     "US$6-million contract signed for 50 JUTC buses", "The Gleaner (Jamaica)", "2022-05-31", D,
     "downloads/JAM/Gleaner_20220531_US6m_contract_50_JUTC_buses.html", "article body, paragraph 2",
     "45 diesel buses valued at US$5.4 million and five electric buses valuing US$1.1 million for the Jamaica Urban Transit Company: 120,000 and 220,000 US$ per bus."),
    ("JAM-004", "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2021&partnerCode=0&flowCode=M&cmdCode=870210,870220,870230,870240,870290,870321,870322,870323,870324,870331,870332,870333,870340,870350,870360,870370,870380,870390,870421,870422,870423,870431,870432,870441,870442,870443,870451,870452,870460,870490,871110,871120,871130,871140,871150,871160,871190",
     "UN Comtrade, Jamaica imports by HS 8702, 8703, 8704 and 8711 subheading, 2021 (public preview API)", "United Nations Statistics Division",
     "data as published to 2026-11", D, "downloads/JAM/comtrade_JAM_imports_vehicles_2021.json", "JSON records by cmdCode (qty, cifvalue)",
     "CIF values before Jamaican duties and taxes; new and used vehicles together. Examples: 870322 12,793 units 79,761,598 US$; 870323 16,237 units 130,021,624 US$; "
     "870380 29 units 440,641 US$; 871120 6,600 units 2,948,431 US$; 871130 18 units 42,966 US$; 871160 99 units 119,172 US$. Comparison only."),
    ("JAM-005", "https://api.worldbank.org/v2/country/JAM/indicator/PA.NUS.FCRF?format=json&date=2015:2024&per_page=100",
     "World Development Indicators: Official exchange rate (LCU per US$, period average), PA.NUS.FCRF, Jamaica", "World Bank", "data as published to 2026-11", D,
     "downloads/JAM/WB_WDI_PA.NUS.FCRF_JAM_2015_2024.json", "JSON records date 2022 and 2024", "2022 = 153.426816 J$ per US$; 2024 = 156.439540 J$ per US$."),
    ("JAM-006", "https://moa.gov.jm/sites/default/files/pdfs/COP_2022.pdf", "Cost of Production Estimates 2022", "Ministry of Agriculture and Fisheries, Jamaica", "2022", D,
     "downloads/JAM/MOA_COP_2022.pdf",
     "one budget per parish and crop (0.4 ha, one crop cycle): lines 'Projected Marketable Yield (Kg)' and 'Cost of Production $/Kg'; e.g. Clarendon yellow yam, PDF p. 1: 7,794 kg, J$128 per kg, total operating expenditure J$996,375",
     "Estimates stated per kg, area 0.4 hectare, J$; not to be construed as establishment costs. 61 budgets parsed from the pdftotext layout text (two carrot budgets with a shifted layout skipped). "
     "Crops: yams, Irish and sweet potato, dasheen, cassava, cabbage, carrot, tomato, lettuce, onion, escallion, hot pepper, ginger, red peas, plantain, pineapple. No cereals, coffee or livestock."),
    ("JAM-007", "https://jis.gov.jm/jutc-provided-with-170-new-buses-valued-5b-since-2023/", "JUTC Provided with 170 New Buses Valued $5b Since 2023",
     "Jamaica Information Service", "2024 (reports September 2024 data and FY 2024/25 payments)", D,
     "downloads/JAM/JIS_JUTC_170_new_buses_valued_5b.html", "article body, paragraph 1",
     "170 new buses at a cost of J$5 billion since 2023; 100 further units (70 CNG, 30 diesel coach) to be procured. Comparison only."),
]
with open(os.path.join(CC_DIR, "sources_JAM.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "notes"])
    w.writerows(SOURCES)

LOG = [
    ("vehicles CapitalCost base prices", "Electric Vehicle Policy 2023 (Ministry of Science, Energy and Technology)", "https://japarliament.gov.jm/attachments/article/2548/Electronic-Vechile-Policy.pdf", "Downloaded (JAM-001); text search: no vehicle prices, distances or lives."),
    ("vehicles CapitalCost base prices", "Office of Utilities Regulation EV consultation 2021", "https://our.org.jm/wp-content/uploads/2021/05/OURs-EV-Stakeholders-Consultation-Document-2021-May-12.pdf", "Downloaded (JAM-002); acquisition costs of petrol and electric cars, 20,000 km per year, 15-year life. Used."),
    ("TRBPU CapitalCost", "Web search: JUTC electric bus price", "JUTC electric buses cost each price BYD Jamaica", "Found Gleaner 31 May 2022 and JIS articles."),
    ("TRBPU CapitalCost", "Gleaner JUTC contract article", "https://jamaica-gleaner.com/article/news/20220531/us6-million-contract-signed-50-jutc-buses", "Downloaded (JAM-003). Used for diesel and electric bus prices."),
    ("TRBPU CapitalCost", "JIS JUTC fleet articles", "https://jis.gov.jm/jutc-provided-with-170-new-buses-valued-5b-since-2023/ ; https://jis.gov.jm/govt-adding-electric-buses-to-jutc-fleet/", "Downloaded both; the first (JAM-007) gives J$5 billion for 170 buses (comparison); the second has no prices (file kept, not cited)."),
    ("vehicles CapitalCost base prices", "UN Comtrade public API, Jamaica imports 2021 to 2023", "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2021&partnerCode=0&flowCode=M", "2021 downloaded (JAM-004); 2022 downloaded and discarded; 2023 rate-limited (HTTP 429). CIF unit values used as comparison only (used imports dominate)."),
    ("vehicles CapitalCost base prices", "Jamaica Customs Agency duty valuation and STATIN external trade by vehicle type", "jacustoms.gov.jm ; statinja.gov.jm", "Not searched in depth within the time; Comtrade used as the trade source."),
    ("Ref.km.BY", "OUR 2021 (JAM-002) and GEN-104", "downloads/JAM/OUR_EV_Stakeholders_Consultation_2021.pdf", "20,000 km per year for private cars (used for cars and SUVs); other groups GEN-104; taxi ASSUMPTION."),
    ("OperationalLife", "OUR 2021 (JAM-002), GEN-103, GEN-104; Island Traffic Authority fleet age", "downloads/JAM/OUR_EV_Stakeholders_Consultation_2021.pdf", "15-year car life used; no Island Traffic Authority fleet-age table searched within the time."),
    ("exchange rate", "World Bank WDI API", "https://api.worldbank.org/v2/country/JAM/indicator/PA.NUS.FCRF?format=json&date=2015:2024&per_page=100", "Downloaded (JAM-005)."),
    ("AG_* FixedCost VariableCost", "Web search: RADA and Ministry of Agriculture crop budgets", "RADA Jamaica crop budget cost of production per hectare pdf yam sweet potato Irish potato", "Found Ministry of Agriculture Cost of Production Estimates 2019, 2022, 2023, 2024, 2025."),
    ("AG_* FixedCost VariableCost", "MOA COP 2022 and 2023 on restore.moa.gov.jm", "https://restore.moa.gov.jm/sites/default/files/pdfs/COP_2022.pdf", "HTTP 503 page (host under maintenance); not used."),
    ("AG_* FixedCost VariableCost", "MOA COP 2022 on moa.gov.jm", "https://moa.gov.jm/sites/default/files/pdfs/COP_2022.pdf", "Downloaded (JAM-006); 61 budgets parsed. Used. COP 2024 also downloaded and discarded (2022 is closer to the 2021 base year)."),
    ("AG_CER AG_COF GA_*", "MOA COP 2022", "downloads/JAM/MOA_COP_2022.pdf", "No cereal, coffee or livestock budgets; rows are ASSUMPTION. Coffee Industry Regulation Division and Jamaica Agricultural Society not searched within the time."),
    ("IMP* VariableCost", "GEN-201 FAOSTAT trade unit values", "GEN/faostat_trade_unit_values.csv", "Jamaica avg_2019_2023 rows used."),
    ("waste and wastewater", "GEN-204 GEN-206 GEN-207", "GEN/gen_sector_values.csv", "Used (Jamaica row of Hutton and Varughese Table E.1)."),
    ("EmissionsPenalty contam_agua salud_residuos turismo_residuos", "GEN sector notes (IDB publications)", "https://publications.iadb.org/es/lineamientos-sectoriales-para-la-gestion-de-residuos-solidos-y-el-avance-hacia-la-economia-circular", "Not retried: GEN reports bot-verification pages for every IDB PDF. ASSUMPTION; listed as manual."),
]
with open(os.path.join(CC_DIR, "search_log_JAM.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["row", "lead", "url_or_query", "date", "result"])
    for r in LOG:
        w.writerow([r[0], r[1], r[2], D, r[3]])

MAN = [
    ("https://publications.iadb.org/es/lineamientos-sectoriales-para-la-gestion-de-residuos-solidos-y-el-avance-hacia-la-economia-circular",
     "Correal, Rihm et al. (2023). Lineamientos sectoriales para la gestion de residuos solidos y el avance hacia la economia circular. IDB",
     "Public health, water contamination and tourism externalities of waste disposal (origin of contam_agua, salud_residuos, turismo_residuos)",
     "JAM_WASTE EmissionsPenalty contam_agua, salud_residuos, turismo_residuos, 2021 to 2055 (105 cells, class assumption meanwhile)"),
    ("https://publications.iadb.org/es/sostenibilidad-financiera-de-la-gestion-de-residuos-solidos-en-america-latina-y-el-caribe",
     "Correal, Faleiro, Piamonte, Rihm, Zambrano (2023). Sostenibilidad financiera de la gestion de residuos solidos en America Latina y el Caribe. IDB-TN-2663",
     "Waste facility costs (collection, landfill, open dump) that may be the origin of the model values",
     "JAM_WASTE BLEND_NO_DCOLL, LANDFILL, NO_CONTR_OD (sourced meanwhile from CEPAL 2016 and What a Waste 2.0)"),
    ("https://publications.iadb.org/", "IDB (2022). Strategic Framework for Electric Mobility in Jamaica (no public PDF located)",
     "Jamaican vehicle prices by class and powertrain, distances and fleet data",
     "JAM_TRANSPORT Vehicle Techs CapitalCost base-year cells (sourced meanwhile from OUR 2021, JUTC 2022, GEN-101 and GEN-104)"),
]
with open(os.path.join(CC_DIR, "manual_downloads_JAM.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["url", "title", "what_it_would_source", "proposal_rows_waiting"])
    w.writerows(MAN)
print("ok")
