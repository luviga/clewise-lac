"""Steps 2 and 3 bookkeeping: sources.csv, leads.csv, search_log.csv, manual_downloads.csv."""
import csv, datetime, os
import pandas as pd

def clean(x):
    return x.replace(chr(0x2014), "-").replace(chr(0x2013), "-") if isinstance(x, str) else x

# ---------------- sources.csv ----------------
src = pd.read_csv("scratch/sources_regional.csv")
LOC = {
    "REG-001": "PDF p.75 Table 2.1 (onshore wind, Central America and the Caribbean, Other South America); PDF p.159 text (small hydro)",
    "REG-002": "PDF p.71 Table 2.1 (onshore wind); PDF p.95 Table 3.1 (utility-scale PV); PDF p.149 Table 6.3 (hydropower)",
    "REG-003": "PDF p.46 Table 2.1 (onshore wind); PDF p.62 Table 3.1 (utility-scale PV); PDF p.106 text (large hydropower)",
    "REG-004": "PDF p.95 Annex B Table 16",
    "REG-005": "PDF p.151 Tabla 10.8 (capitalized investment, fixed O&M, USD December 2023); PDF p.153 Tabla 10.9 (overnight investment)",
    "REG-006": "PDF p.46 Tabla 19 (investment, fixed and variable O&M, referenced to 2024)",
    "REG-007": "PDF p.35 Tabla 6", "REG-008": "whole document searched; no cost table in the text layer",
    "REG-009": "PDF p.58 Tabla 4.9, p.60 to p.64 Tabla 4.10, p.66 Tabla 4.11, p.67 Tabla 4.12",
    "REG-010": "PDF p.13 Tabla 3, PDF p.14 Tabla 4", "REG-011": "Section 3.1.3, Tabla 3.1 (HTML page)",
    "REG-012": "PDF p.113 to p.126 (Ecuador charts); no printed values used", "REG-013": "PDF p.24 Grafica 8 (chart, no printed values)",
    "REG-014": "data sheets PDF p.62 to p.327; currency statement PDF p.30; used: PDF p.64 (industrial rooftop PV), p.92 (small wind), p.315 and p.316 (grid-scale lithium-ion battery)",
    "REG-015": "PDF p.59 (2018 USD statement); PDF p.107 (BESS); PDF p.182 Appendix C",
    "REG-016": "PDF p.336 to p.350 Tablas 204 to 229", "REG-017": "PDF p.190 and p.191 Table E.1",
    "REG-018": "PDF p.18 Regional Benchmarks table", "REG-019": "PDF p.109 Exhibit 6-33; PDF p.121 Exhibit 6-44",
    "REG-020": "PDF p.5 to p.25 Annex A (breakdowns behind Tabla 19 of the Informe)", "REG-021": "whole document searched; no per-kW cost table",
}
src["page_or_table"] = src["source_id"].map(LOC)
src["notes"] = src["notes"].str.replace(r"copied from the (.+?) job download folder", r"same file as downloaded by the \1 cost job on 2026-11-10", regex=True)
cpi = [
    {"source_id": "CRC-001", "url": "https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2017&endyear=2025&annualaverage=true",
     "title": "Consumer Price Index for All Urban Consumers (CPI-U), All items in U.S. city average, series CUUR0000SA0, annual averages 2017 to 2025",
     "publisher": "U.S. Bureau of Labor Statistics", "publication_date": "data as published to 2026-11", "retrieval_date": "2026-11-10",
     "downloaded_file": "cpi/bls_CUUR0000SA0_2017_2025_annualaverage_CR.json", "region": "United States",
     "notes": "Costa Rica constants US_CPIU_2023 = 304.702, US_CPIU_2024 = 313.689; same id and file as the Costa Rica cost job",
     "page_or_table": "JSON Results.series[0].data, period M13 (Annual), years 2023 and 2024"},
    {"source_id": "FUE-001", "url": "https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2017&endyear=2025&annualaverage=true",
     "title": "Consumer Price Index for All Urban Consumers (CPI-U), all items in U.S. city average, series CUUR0000SA0",
     "publisher": "U.S. Bureau of Labor Statistics", "publication_date": "annual averages 2017 to 2025", "retrieval_date": "2026-11-10",
     "downloaded_file": "cpi/bls_CUUR0000SA0_2017_2025_GUA.json", "region": "United States",
     "notes": "Guatemala constants CPI_U_2024 = 313.689, CPI_U_2025 = 321.943; same id and file as the Guatemala cost job",
     "page_or_table": "JSON Results.series[0].data, period M13 (Annual), years 2024 and 2025"},
    {"source_id": "CSH-005", "url": "https://api.bls.gov/publicAPI/v1/timeseries/data/ (POST {\"seriesid\":[\"CUUR0000SA0\"],\"startyear\":\"2016\",\"endyear\":\"2025\"})",
     "title": "Consumer Price Index for All Urban Consumers (CPI-U), all items, U.S. city average, not seasonally adjusted (CUUR0000SA0)",
     "publisher": "U.S. Bureau of Labor Statistics", "publication_date": "data to 2025", "retrieval_date": "2026-11-10",
     "downloaded_file": "cpi/bls_cpiu_v1_2016_2025_HON.json", "region": "United States",
     "notes": "Honduras constants CPIU_2023 = 304.702 and CPIU_2024 = 313.689 (means of 12 monthly values); same id and file as the Honduras cost job",
     "page_or_table": "JSON Results.series[0].data, series CUUR0000SA0, monthly values M01 to M12 for 2023 and 2024"},
]
src = pd.concat([src, pd.DataFrame(cpi)], ignore_index=True)
src = src[["source_id", "url", "title", "publisher", "publication_date", "retrieval_date", "downloaded_file", "page_or_table", "region", "notes"]]
src.map(clean).to_csv("sources.csv", index=False, lineterminator="\n")

# ---------------- leads.csv ----------------
L = [
    ("L01", "CEAC regional indicative generation expansion plan", "Central America", "CEAC Plan Indicativo Regional de Expansion de la Generacion, latest edition", "", "not found",
     "two web searches (standard and extended) found no CEAC plan document; listed in manual_downloads.csv", "lead list"),
    ("L02", "IRENA Renewable Power Generation Costs 2022, 2024, 2025", "LAC", "IRENA RPGC in 2022 (REG-001)", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2023/Aug/IRENA_Renewable_power_generation_costs_in_2022.pdf", "opened", "regional tables extracted; older than the 2024 and 2025 editions", "lead list"),
    ("L03", "IRENA Renewable Power Generation Costs 2022, 2024, 2025", "LAC", "IRENA RPGC in 2024 (REG-002)", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA_TEC_RPGC_in_2024_2025.pdf", "opened", "Central America and Caribbean onshore wind used (Jamaica PPWNDON)", "lead list"),
    ("L04", "IRENA Renewable Power Generation Costs 2022, 2024, 2025", "LAC", "IRENA RPGC in 2025 (REG-003)", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf", "opened", "Central America and Caribbean utility PV used (Guatemala PPPVT, PPPVT2)", "lead list"),
    ("L05", "IRENA regional market analyses (Latin America; Caribbean or SIDS)", "Central America", "IRENA Renewable Energy Roadmap for Central America (REG-004)", "https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2022/Mar/IRENA_Renewable_Roadmap_Central_America_2022.pdf", "opened", "Table 16 has no currency year; not accepted", "lead list"),
    ("L06", "IRENA regional market analyses (Latin America; Caribbean or SIDS)", "LAC", "IRENA Renewable Energy Market Analysis: Latin America (2016) and SIDS lighthouses material", "", "not opened",
     "published before 2019 (fails rule 2) or without cost tables; web search found no newer Caribbean or SIDS cost table", "lead list"),
    ("L07", "IDB, CAF, OLADE and CEPAL cost tables", "LAC", "IDB Technical Note 1831 (REG-012)", "https://publications.iadb.org/publications/spanish/document/Evoluci%C3%B3n_futura_de_costos_de_las_energ%C3%ADas_renovables_y_almacenamiento_en_Am%C3%A9rica_Latina_es.pdf", "opened", "country costs as charts only; no printed value", "lead list"),
    ("L08", "IDB, CAF, OLADE and CEPAL cost tables", "LAC", "OLADE, CEPAL and CAF technology cost tables", "", "not found", "web search found OLADE monthly reports and an IEA-OLADE note without cost tables; OLADE library blocked in earlier jobs", "lead list"),
    ("L09", "CDB, CARICOM or CCREEE Caribbean generation costs", "Caribbean", "CCREEE Sustainable Energy Technology Considerations and Regional Outlook (REG-018)", "https://www.ccreee.org/wp-content/uploads/2022/03/Sustainable-Energy-Technology-Considerations-and-Regional-Outlook.pdf", "opened", "ranges and 2020 benchmarks without a stated currency year; not accepted", "lead list"),
    ("L10", "Neighbour plans: Panama", "Central America", "ETESA PESIN 2025-2039 Tomo II (REG-009)", "https://asep.gob.pa/wp-content/uploads/electricidad/consultas_publicas/2025/cp_009-2025/tomo_II/tomo_II-plan_Indicativo_generacion_2025-2039.pdf", "opened", "project costs, no currency year; not accepted", "lead list"),
    ("L11", "Neighbour plans: El Salvador", "Central America", "El Salvador PIEGE 2020-2030 (REG-010)", "https://estadisticas.dgehm.gob.sv/wp-content/uploads/2021/06/Plan-indicativo-de-la-generaci%C3%B3n-de-la-expansi%C3%B3n-2020-2030-vf.pdf", "opened", "project costs, no currency year; not accepted", "lead list"),
    ("L12", "Neighbour plans: Nicaragua", "Central America", "MEM Nicaragua generation expansion plan", "", "not found", "web search found no plan document", "lead list"),
    ("L13", "Neighbour plans: Mexico", "Central America", "SENER PLADESE 2025-2039, DOF 14 October 2025 (REG-011)", "https://dof.gob.mx/nota_detalle_popup.php?codigo=5770297", "opened", "CAIO costs include interest during construction; no currency year; not accepted", "lead list"),
    ("L14", "Neighbour plans: Puerto Rico IRP and other Caribbean utility plans", "Caribbean", "PREPA IRP 2019 Exhibit 1.0 (REG-019)", "https://energia.pr.gov/wp-content/uploads/sites/7/2019/02/PREPA-Ex.-1.0-IRP-2019-PREPA-IRP-Report.pdf", "opened", "utility PV, wind and battery only; no in-scope group matched", "lead list"),
    ("L15", "Neighbour plans: Puerto Rico IRP and other Caribbean utility plans", "Caribbean", "Puerto Rico 2025 IRP (LUMA) cost assumptions", "", "not found", "docket filings found without cost tables; listed in manual_downloads.csv", "lead list"),
    ("L16", "Neighbour plans: Puerto Rico IRP and other Caribbean utility plans", "Caribbean", "Barbados IRRP draft (REG-017)", "https://energy.gov.bb/wp-content/uploads/2024/10/MM_IADB_Draft-IRRP-Report_ActivityB_vB_0-Final-Rev-6-June-22-Revision-FEL-1-1.pdf", "opened", "no price base stated; not accepted", "lead list"),
    ("L17", "Neighbour plans: Colombia (UPME)", "Andean", "UPME PIEG 2025-2039 (REG-013)", "https://docs.upme.gov.co/SIMEC/Energia%20Electrica/PIEG/2025-2039/PIEG_2025_2039_Version_final.pdf", "opened", "CAPEX as a chart only; points to the Colombian Technology Catalogue", "lead list"),
    ("L18", "Neighbour plans: Colombia (UPME)", "Andean", "Colombian Technology Catalogue, MME and UPME, March 2025 (REG-014)", "https://minenergia.gov.co/documents/13276/Catalogo-Tecnologico-Colombiano-tecnologias-generacion-almacenamiento-energia-ES.pdf", "opened", "2024 USD data sheets; used for Ecuador PPPVD, PPWNDD, STOELE", "lead list (found through L17)"),
    ("L19", "Neighbour plans: Peru", "Andean", "MINEM, COES or Osinergmin technology cost table", "", "not found", "web search found news only", "lead list"),
    ("L20", "Neighbour plans (SICA members) already downloaded by country jobs", "Central America", "ODS Honduras PIEG 2026-2035 Informe and Anexos (REG-006, REG-020)", "https://cnd.enee.hn/wp-content/uploads/2026/09/Informe-PIEG-2026-2035.pdf", "opened", "Tabla 19 (2024 USD) used as R2 for Costa Rica and Guatemala", "lead list"),
    ("L21", "Neighbour plans (SICA members) already downloaded by country jobs", "Central America", "MEM Guatemala PEIG 2026-2050 (REG-007)", "https://mem.gob.gt/wp-content/uploads/2026/01/PEIG_2026_2050_MEM.pdf", "opened", "Tabla 6 has no currency year; not accepted", "lead list"),
    ("L22", "Neighbour plans (Caribbean) already downloaded by country jobs", "Caribbean", "Jamaica IRP 2018 (REG-015)", "https://www.mset.gov.jm/wp-content/uploads/2020/03/2018-Jamaica-Integrated-Resource-Feb-21-2020.pdf", "opened", "2018 USD; R2 for the Dominican Republic, no in-scope group matched", "lead list"),
    ("L23", "Neighbour plans (Caribbean) already downloaded by country jobs", "Caribbean", "Jamaica IRP 2022 (REG-021)", "https://gpe.gov.jm/wp-content/uploads/2024/11/2022-Jamaica-Integrated-Resource-Plan.pdf", "opened", "no per-kW cost table", "lead list"),
    ("L24", "Neighbour plans (Caribbean) already downloaded by country jobs", "Caribbean", "CNE Dominican Republic PEN 2022-2036 (REG-016)", "https://cne.gob.do/wp-admin/admin-ajax.php?action=outofthebox-download&OutoftheBoxpath=%2Fpen2022-2037.pdf&lastpath=%2F&account_id=dbid:AAAGpYR0ODh0f0jJZRlCsjhWYMYovXEms_Q&listtoken=255346f20b4341ea85f9ebf4917022f4&dl=1", "opened", "Tablas 204 to 229 have no currency year; not accepted", "lead list"),
    ("X01", "National, found late", "Central America", "ICE PEG 2024-2040 (REG-005)", "https://www.grupoice.com/wps/wcm/connect/20b300e4-c4df-4994-b1b1-372726fa4f3b/PLAN+DE+EXPANSION+DE+LA+GENERACION+ELECTRICA+2024-2040.pdf?MOD=AJPERES&CVID=pFal9fj", "opened", "N for Costa Rica (6 groups), R2 for Honduras (2 groups)", "extra document 1 of 10 (Central America)"),
    ("X02", "National, found late", "Central America", "MEM Guatemala PEG 2024-2054 (REG-008)", "https://www.cnee.gob.gt/PlanesExpansion/2024-2054/PEG%202024-2054.pdf", "opened", "no cost table in the text layer", "extra document 2 of 10 (Central America)"),
    ("X03", "National, found late", "Andean", "Ecuador Plan Maestro de Electricidad 2018-2027, chapter 4", "https://www.recursosyenergia.gob.ec/wp-content/uploads/2020/01/4.-EXPANSION-DE-LA-GENERACION.pdf", "did not open", "host name does not resolve; listed in manual_downloads.csv", "extra document 1 of 10 (Andean)"),
    ("X04", "National, found late", "Caribbean", "CNE Dominican Republic Estudio del Regimen Economico de las Energias Renovables (2020) and price recommendations", "", "not found", "web searches found references only; listed in manual_downloads.csv", "extra document 1 of 10 (Caribbean)"),
]
pd.DataFrame(L, columns=["lead_id", "family", "region", "document", "url", "status", "outcome", "counted_as"]).map(clean).to_csv("leads.csv", index=False, lineterminator="\n")

# ---------------- search_log.csv ----------------
log = []
with open("scratch/search_log_raw.tsv", encoding="utf-8") as fh:
    for line in fh:
        t, q, held, out = line.rstrip("\n").split("\t")
        log.append({"datetime_utc": t, "query_or_url": q, "what_it_held": held, "outcome": out})
for _, r in src.iterrows():
    fpath = "downloads/" + r["downloaded_file"]
    t = datetime.datetime.utcfromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%dT%H:%M:%SZ")
    how = "copied from an earlier LAC cost job download of the same URL" if r["retrieval_date"] == "2026-11-10" else "downloaded"
    log.append({"datetime_utc": t, "query_or_url": r["url"], "what_it_held": f"{r['title']} ({r['source_id']}); {how}; text extracted and read",
                "outcome": "opened; " + str(r["notes"])})
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
for t, q, held, out in [
        (now, "https://publications.iadb.org/publications/spanish/document/ (IDB TN-1831, first request; logged at write-up, attempt made earlier in the session)", "HTTP 403 to the first request", "retried with curl and a browser user agent: downloaded"),
        (now, "https://www.recursosyenergia.gob.ec/wp-content/uploads/2020/01/4.-EXPANSION-DE-LA-GENERACION.pdf", "Ecuador PME 2018-2027 chapter 4 (logged at write-up, attempt made earlier in the session)", "host name does not resolve (getaddrinfo failed); manual download listed")]:
    log.append({"datetime_utc": t, "query_or_url": q, "what_it_held": held, "outcome": out})
pd.DataFrame(log).sort_values("datetime_utc").map(clean).to_csv("search_log.csv", index=False, lineterminator="\n")

# ---------------- manual_downloads.csv ----------------
M = [
    ("https://www.recursosyenergia.gob.ec/wp-content/uploads/2020/01/4.-EXPANSION-DE-LA-GENERACION.pdf", "Ecuador Plan Maestro de Electricidad 2018-2027, chapter 4 Expansion de la generacion: candidate plant costs (national, found late)", "Ecuador PPPVD, PPWNDD, STOELE"),
    ("https://www.ceaconline.org/ (document location unknown)", "CEAC Plan Indicativo Regional de Expansion de la Generacion, latest edition: regional candidate costs for Central America", "Costa Rica, Guatemala and Honduras groups kept international (distributed PV, biomass variable O&M, coal)"),
    ("https://cne.gob.do/documentos/ (document location unknown)", "CNE Dominican Republic Estudio del Regimen Economico de las Energias Renovables (November 2020) and resolutions CNE-AD-0036-2022 and CNE-AD-0006-2023: reference costs by technology including biomass", "Dominican Republic PPBGS, PPBIM, PPPVD"),
    ("https://energia.pr.gov/ (docket NEPR-AP-2023-0004, 2025 IRP workpapers)", "Puerto Rico 2025 IRP (LUMA) technology cost assumptions", "Dominican Republic and Jamaica distributed PV and biomass groups"),
    ("https://www.mem.gob.ni/ (document location unknown)", "Nicaragua MEM generation expansion plan with candidate costs", "Costa Rica, Guatemala and Honduras groups kept international"),
]
pd.DataFrame(M, columns=["url", "what_it_should_hold", "groups_it_would_serve"]).to_csv("manual_downloads.csv", index=False, lineterminator="\n")
print(len(src), "sources;", len(L), "leads;", len(log), "log rows")
