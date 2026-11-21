"""Write sources, pending, targets and projections for Ecuador (ECU) from values read in the documents.

Usage: python -I write_tables_ECU.py <job_folder>
Every value below was read on the cited physical page of the downloaded file (text cache or page image).
"""
import csv
import hashlib
import os
import sys

JOB = sys.argv[1]
ACC = "2026-11-21"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pages(path):
    import pdfplumber
    with pdfplumber.open(path) as p:
        return len(p.pages)


def write(name, cols, rows):
    with open(os.path.join(JOB, name), "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


# ---------------------------------------------------------------- sources
SRC = [
    ("ECU-01", "NDC", "https://unfccc.int/sites/default/files/2025-02/Segunda%20NDC%20de%20Ecuador.pdf",
     "Segunda Contribucion Determinada a Nivel Nacional de la Republica del Ecuador 2026-2035 (second NDC)",
     "Republica del Ecuador, Ministerio del Ambiente, Agua y Transicion Ecologica (MAATE)",
     "2025-02 (document dated February 2025, p.2; delivery to the UNFCCC in February 2025 per the timeline on p.41)",
     "downloads/ECU/ECU_NDC2_2025.pdf", "Spanish (executive summary also in English)"),
    ("ECU-02", "NDC", "https://unfccc.int/sites/default/files/NDC/2022-06/Primera%20NDC%20Ecuador.pdf",
     "Primera Contribucion Determinada a Nivel Nacional para el Acuerdo de Paris bajo la Convencion Marco de Naciones Unidas sobre Cambio Climatico (first NDC, 2020-2025)",
     "Republica del Ecuador, Ministerio del Ambiente", "2019-03 (cover dated March 2019; ECU-01 p.36 says presented in March 2019)",
     "downloads/ECU/ECU_NDC1_2019.pdf", "Spanish"),
    ("ECU-03", "LTS-national-not-submitted",
     "http://certificacionpuntoverde.ambiente.gob.ec/libraries/EAlfresco.php/?doc=674e3cfd-a3c5-497b-8919-32a2791d51ab (link 'Documento PLANMICC completo' on https://planmicc.ambiente.gob.ec/)",
     "Plan Nacional de Mitigacion del Cambio Climatico del Ecuador, PLANMICC (2024-2070); called the long-term strategy in ECU-01 p.10, p.33, p.44; not found on the UNFCCC long-term strategies portal",
     "Ministerio del Ambiente, Agua y Transicion Ecologica (MAATE)", "2024-08 (p.2)",
     "downloads/ECU/ECU_PLANMICC_2024.pdf", "Spanish"),
    ("ECU-04", "BTR", "https://unfccc.int/sites/default/files/resource/a.%205CN1RBT-27dic_final.pdf",
     "Quinta Comunicacion Nacional y Primer Reporte Bienal de Transparencia del Ecuador (5CN-1RBT; fifth national communication and first BTR)",
     "Ministerio del Ambiente, Agua y Transicion Ecologica (MAATE)",
     "2024-12 (file name dated 27 December; ECU-01 p.21 footnote 13 says delivered to the UNFCCC in December 2024)",
     "downloads/ECU/ECU_BTR1_5CN_2024.pdf", "Spanish"),
    ("ECU-05", "NID",
     "https://cdn.climatepolicyradar.org/navigator/ECU/2024/ecuador-national-inventory-report-nir-2024_8c731b52bc1d6e93a107d2251cf6204a.pdf (copy of https://unfccc.int/sites/default/files/resource/e.%202024.12.27_NID_5CN1RBT_v7_final.pdf; earlier register row FR2-D3-ECUNID)",
     "Documento del Inventario Nacional (DIN) de Gases de Efecto Invernadero del ano 2022 del Ecuador",
     "Ministerio del Ambiente, Agua y Transicion Ecologica (MAATE)", "2024 (December 2024 with the 5CN-1RBT)",
     "downloads/ECU/ECU_NID_2024.pdf", "Spanish"),
    ("ECU-06", "BUR",
     "https://unfccc.int/sites/default/files/resource/ECUADOR_%20CN4_%20BUR2.pdf (address from a search result; file reused from the earlier job download ECU_CN4_BUR2_2022.pdf, byte identity with the address not re-checked)",
     "Cuarta Comunicacion Nacional y Segundo Informe Bienal de Actualizacion del Ecuador a la CMNUCC (CN4 and BUR2)",
     "Ministerio del Ambiente, Agua y Transicion Ecologica (MAATE)", "2022-12 (p.3)",
     "downloads/ECU/ECU_CN4_BUR2_2022.pdf", "Spanish"),
    ("ECU-07", "sector plan",
     "https://drive.google.com/file/d/1rcL-T4NVY25jk-5Q5BLi4kvJGyFGHxE3/view (linked as 'Plan Maestro de Electricidad Completo' on https://www.ambienteyenergia.gob.ec/plan-maestro-de-electricidad/; earlier job register d12_lives)",
     "Plan Maestro de Electricidad 2023-2032 (complete document); cited by ECU-01 p.67 as a source for the energy sector target",
     "Ministerio de Energia y Minas, Ecuador", "edition 2023-2032",
     "downloads/ECU/ECU_PME_2023_2032.pdf", "Spanish"),
    ("ECU-08", "sector plan",
     "https://www.undp.org/sites/g/files/zskgke326/files/migration/ec/e0b4e4e6a9d69f45f8e47838439b898bd2c9743b457e43e80333e6ea176e5724.pdf",
     "Plan Nacional de Eficiencia Energetica 2016-2035 (PLANEE); cited by ECU-01 p.67 and ECU-03 p.101 (Tabla 14)",
     "Ministerio de Electricidad y Energia Renovable, Ecuador (edition hosted by UNDP Ecuador)", "2017 (printed in Quito, 2017, p.4)",
     "downloads/ECU/ECU_PLANEE_2016_2035.pdf", "Spanish"),
    ("ECU-09", "sector plan",
     "https://www.ambienteyenergia.gob.ec/wp-content/uploads/2023/11/hoja_de_ruta_hidrogeno_verde_Modificado.pdf (earlier job register d12_lives)",
     "Hoja de Ruta del Hidrogeno Verde en Ecuador (first edition); cited by ECU-03 p.100 for hydrogen in transport",
     "Ministerio de Energia y Minas, Ecuador", "2023-07",
     "downloads/ECU/ECU_H2_roadmap_2023.pdf", "Spanish"),
]

src_rows = []
for sid, kind, url, title, pub, date, fpath, lang in SRC:
    full = os.path.join(JOB, fpath)
    src_rows.append({"id": sid, "country": "Ecuador", "kind": kind, "URL": url, "title": title, "publisher": pub,
                     "date": date, "accessed": ACC, "SHA-256": sha(full), "file": fpath, "pages": pages(full),
                     "language": lang})
write("parts/sources_ECU.csv", ["id", "country", "kind", "URL", "title", "publisher", "date", "accessed", "SHA-256",
                                "file", "pages", "language"], src_rows)

PEND = [
    {"country": "Ecuador", "kind": "sector plan",
     "title": "Politica Nacional de Movilidad Urbana Sostenible (PNMUS), cited by ECU-03 p.101 (Tabla 14) as basis of the transport hypotheses",
     "urls_tried": "https://capacity4dev.europa.eu/media/282471/download/9de7a615-eeac-43e8-b6b7-01137546d565_en ; https://capacity4dev.europa.eu/media/281874/download/d0753420-61c0-4313-be2c-e56645a20c85_en ; https://www.obraspublicas.gob.ec/politica-nacional-de-movilidad-urbana-sostenible/",
     "errors": "HTTP 403 (HTML page); HTTP 403 (HTML page); host name could not be resolved",
     "note": "Three attempts on 2026-11-21. The PLANMICC public transport and modal targets (ECU-03 p.106) are recorded from the PLANMICC itself."},
    {"country": "Ecuador", "kind": "sector plan",
     "title": "Estrategia Nacional de Electromovilidad para Ecuador (ENEM, 2021, IDB), cited by ECU-03 p.101 (Tabla 14)",
     "urls_tried": "web search (two queries) for an official PDF: none found ; https://www.iadb.org/es/proyecto/EC-T1452 ; https://biblioteca.olade.org/opac-tmpl/Documentos/cg00578.pdf",
     "errors": "no PDF address found by search; project page is HTML with no document link; HTTP 404",
     "note": "Three attempts on 2026-11-21. Electric vehicle and freight electrification targets are recorded from ECU-03 p.106 and p.107."},
]
write("parts/sources_pending_ECU.csv", ["country", "kind", "title", "urls_tried", "errors", "note"], PEND)

# ---------------------------------------------------------------- targets
# (source, page, table, kind, sector, description, original term, indicator, value, unit, base, year, cond, gases, image, note)
G4 = "CO2, CH4, N2O, HFC"
T = [
    # ---- ECU-01 second NDC
    ("ECU-01", "p.10;p.14;p.55;p.56", "printed p.8, p.12, p.53, p.54 (sections 4.2.4 and 4.4.1)", "NDC", "economy-wide",
     "Economy-wide GHG reduction in 2035 against the trend scenario (Energy, IPPU, Agriculture, LULUCF, Waste)",
     "escenario incondicional", "percent reduction against BAU", "7", "percent",
     "BAU (trend scenario, base year 2010)", "2035", "unconditional", G4, "no",
     "Single-year target for 2035; implementation period 1 January 2026 to 31 December 2035 (p.56). AR5 GWP (p.60)."),
    ("ECU-01", "p.10;p.55;p.56", "printed p.8, p.53, p.54", "NDC", "economy-wide",
     "Unconditional 2035 reduction expressed in kt CO2eq", "", "emission reduction against BAU", "8800", "kt CO2eq",
     "BAU (trend scenario, base year 2010)", "2035", "unconditional", G4, "no", "Printed as approximately 8,800 kt."),
    ("ECU-01", "p.55;p.56;p.57", "printed p.53, p.54; Figura 6 printed p.55", "NDC", "economy-wide",
     "Additional conditional GHG reduction in 2035 against the trend scenario, subject to international support",
     "escenario condicional", "percent reduction against BAU (additional)", "8", "percent",
     "BAU (trend scenario, base year 2010)", "2035", "conditional", G4, "no",
     "p.55 and p.56 say 8 percent additional; the executive summary (p.10) says the conditional target could reach 8 percent. Read as additional, so 15 percent in total (see notes)."),
    ("ECU-01", "p.55;p.56;p.57", "printed p.53, p.54; Figura 6", "NDC", "economy-wide",
     "Additional conditional 2035 reduction expressed in kt CO2eq", "", "emission reduction against BAU (additional)",
     "10600", "kt CO2eq", "BAU (trend scenario, base year 2010)", "2035", "conditional", G4, "no",
     "Printed as approximately 10,600 kt."),
    ("ECU-01", "p.57", "Figura 6 printed p.55", "NDC", "economy-wide",
     "Updated objective of the first NDC shown in the second NDC figure (four sectors, LULUCF excluded)",
     "Objetivo Primera NDC 5% (actualizado)", "percent reduction against BAU", "5", "percent", "BAU",
     "2025", "unconditional", G4, "yes", "Figure label: approximately 5,200 kt CO2eq. Footnote 31 (p.56) says the first NDC value excludes LULUCF."),
    ("ECU-01", "p.57", "Tabla 3 printed p.55, Energia line 1", "NDC", "Energy",
     "Line of action: promote development and use of renewable energy (no number stated)",
     "Impulsar el desarrollo y consumo de la energia renovable", "line of action", "", "", "", "2035",
     "not stated", "CO2, CH4, N2O", "no", "Initiatives are not listed in the NDC; the target value is built from the PLANMICC model (p.10, p.33)."),
    ("ECU-01", "p.57", "Tabla 3 printed p.55, Energia line 2", "NDC", "Energy",
     "Line of action: energy efficiency and change of consumption behaviour (no number stated)", "eficiencia energetica",
     "line of action", "", "", "", "2035", "not stated", "CO2, CH4, N2O", "no", ""),
    ("ECU-01", "p.57", "Tabla 3 printed p.55, Energia line 3", "NDC", "Transport",
     "Line of action: sustainable mobility for all types of transport (no number stated)", "movilidad sostenible",
     "line of action", "", "", "", "2035", "not stated", "CO2, CH4, N2O", "no", ""),
    ("ECU-01", "p.58", "Tabla 3 printed p.56, Procesos Industriales lines 1 and 2", "NDC", "IPPU",
     "Lines of action: additions in cement production; reduce consumption, recover and dispose of HFC, PFC and SF6 (no number stated)",
     "adiciones en la produccion de cemento", "line of action", "", "", "", "2035", "not stated", "CO2, HFC", "no", ""),
    ("ECU-01", "p.58", "Tabla 3 printed p.56, Agricultura", "NDC", "Agriculture",
     "Lines of action: sustainable low-emission livestock and agro-productive systems (no number stated)", "",
     "line of action", "", "", "", "2035", "not stated", "CH4, N2O", "no", ""),
    ("ECU-01", "p.58;p.59", "Tabla 3 printed p.56, USCUSS lines 1 to 8", "NDC", "LULUCF",
     "Lines of action: conservation, protected areas, sustainable forest management, plantations, forest control, deforestation-free production, fire management (no number stated)",
     "", "line of action", "", "", "", "2035", "not stated", "CO2", "no",
     "Targets of the REDD+ Action Plan update (2025) are to be added later (p.59)."),
    ("ECU-01", "p.58", "Tabla 3 printed p.56, Residuos", "NDC", "Waste",
     "Lines of action: active methane capture at landfills, integrated solid waste management, wastewater treatment (no number stated)",
     "captura activa de metano", "line of action", "", "", "", "2035", "not stated", "CH4, N2O", "no", ""),
    # ---- ECU-02 first NDC
    ("ECU-02", "p.22", "printed p.21", "NDC", "economy-wide",
     "First NDC: GHG reduction in 2025 against the trend scenario for Energy, Agriculture, IPPU and Waste",
     "escenario incondicional", "percent reduction against BAU", "9", "percent", "BAU (trend scenario, base year 2010)",
     "2025", "unconditional", "CO2, CH4, N2O", "no", "Superseded by ECU-01. LULUCF treated separately."),
    ("ECU-02", "p.22", "printed p.21", "NDC", "economy-wide",
     "First NDC: total reduction in 2025 with international support (four sectors)", "escenario condicional",
     "percent reduction against BAU", "20.9", "percent", "BAU (trend scenario, base year 2010)", "2025",
     "conditional", "CO2, CH4, N2O", "no", "11.9 points above the unconditional 9 percent. ECU-04 p.215 says the conditional value was adjusted to 13.5 percent in the implementation plan."),
    ("ECU-02", "p.22;p.23", "printed p.21 to p.22", "NDC", "LULUCF",
     "First NDC: LULUCF reduction in 2025 against the forest reference emission level", "nivel de referencia",
     "percent reduction against reference level", "4", "percent", "forest reference emission level (2000-2008)",
     "2025", "unconditional", "CO2", "no", "Conditional: 16 percent more, 20 percent in total (p.23)."),
    ("ECU-02", "p.18", "Tabla 2 printed p.17", "NDC", "Transport",
     "First NDC efficient public transport: operation of the Quito Metro (22 km); the Cuenca tram (12 km) is in the same initiative",
     "Transporte Publico Eficiente", "length of metro line in operation", "22", "km", "absolute", "2025",
     "unconditional", "CO2", "no", "Cuenca tram 12 km, same initiative. Rail in the model: E5TRXTRAI is fully electric in every scenario."),
    # ---- ECU-03 PLANMICC (long-term plan)
    ("ECU-03", "p.96", "printed p.92, text on Figura 15", "LTS-national-not-submitted", "economy-wide",
     "CC 2070 scenario: national emissions about 70 percent below the trend scenario in 2070",
     "Escenario Compromiso Climatico 2070", "percent reduction against BAU", "70", "percent", "BAU (trend scenario 2070)",
     "2070", "not stated", "CO2, CH4, N2O", "no", "Trend 2070 about 118,000 Gg; CC 2070 about 36,400 Gg."),
    ("ECU-03", "p.5;p.96", "Prologo printed p.1; printed p.92", "LTS-national-not-submitted", "economy-wide",
     "CC 2070 scenario: national emissions about 50 percent below 2018", "", "percent reduction against base year",
     "50", "percent", "base year 2018 (75,326.87 Gg CO2eq)", "2070", "not stated", "CO2, CH4, N2O", "no",
     "The prologue (p.5) says the plan sets intermediate targets for 2035 and 2050."),
    ("ECU-03", "p.96", "printed p.92", "LTS-national-not-submitted", "economy-wide",
     "CC 2070 scenario: national net emissions in 2070", "", "net emissions", "36400", "Gg CO2eq", "absolute", "2070",
     "not stated", "CO2, CH4, N2O", "no", "Approximate value. No national net-zero year is stated."),
    ("ECU-03", "p.102", "Figura 19 printed p.98", "LTS-national-not-submitted", "Energy",
     "Energy sector (including transport) emissions target, phase I", "Metas del sector Energia, Fase I 2024-2035",
     "sector emissions", "39200", "Gg CO2eq", "absolute (2018: 38,400 Gg)", "2035", "not stated", "CO2, CH4, N2O", "no", ""),
    ("ECU-03", "p.102", "Figura 19 printed p.98", "LTS-national-not-submitted", "Energy",
     "Energy sector (including transport) emissions target, phase II", "Fase II 2036-2050", "sector emissions", "35800",
     "Gg CO2eq", "absolute (2018: 38,400 Gg)", "2050", "not stated", "CO2, CH4, N2O", "no", ""),
    ("ECU-03", "p.102", "Figura 19 printed p.98", "LTS-national-not-submitted", "Energy",
     "Energy sector (including transport) emissions target, phase III", "Fase III 2051-2070", "sector emissions",
     "33900", "Gg CO2eq", "absolute (2018: 38,400 Gg)", "2070", "not stated", "CO2, CH4, N2O", "no", ""),
    ("ECU-03", "p.101;p.102", "printed p.97 and p.98", "LTS-national-not-submitted", "Energy",
     "Energy sector reduction potential against the trend scenario in 2070", "", "percent reduction against BAU",
     "49", "percent", "BAU (trend scenario 2070: 66,300 Gg)", "2070", "not stated", "CO2, CH4, N2O", "no",
     "About 32,000 Gg CO2eq (p.101). Emissions stay close to the trend in the first five years (p.101)."),
    ("ECU-03", "p.102", "printed p.98", "LTS-national-not-submitted", "Energy",
     "Share of electricity in the energy matrix (final energy use) in 2050", "participacion de la electricidad en la matriz energetica",
     "electricity share of final energy", "32.0", "percent", "16.4 percent in 2018", "2050", "not stated", "", "no",
     "46.6 percent in 2070 (same page)."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Non-conventional renewable (ERNC: solar, wind and others) share of SNI generation, phase I",
     "ERNC", "share of generation", "24", "percent", "absolute", "2035", "not stated", "CO2", "yes",
     "Printed as about 24 percent (about 240 MW). The 240 MW looks inconsistent with 24 percent of generation; read as printed (see notes). Footnote 20 defines ERNC; p.108 says the indicator also covers biomass."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Hydro share of SNI generation, phase I", "", "share of generation", "64", "percent", "absolute", "2035",
     "not stated", "CO2", "yes", "Printed as about 64 percent (about 10,000 MW)."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Hydro capacity associated with the phase I hydro share", "", "installed capacity", "10000", "MW", "absolute",
     "2035", "not stated", "CO2", "yes", "Printed as about 10,000 MW in brackets after the 64 percent."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Non-conventional renewable share of SNI generation, phase II", "ERNC", "share of generation", "35", "percent",
     "absolute", "2050", "not stated", "CO2", "yes", "Printed as about 35 percent (about 3,800 MW)."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Non-conventional renewable capacity associated with the phase II share", "ERNC", "installed capacity", "3800",
     "MW", "absolute", "2050", "not stated", "CO2", "yes", "Printed as about 3,800 MW."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Hydro share of SNI generation, phase II", "", "share of generation", "54", "percent", "absolute", "2050",
     "not stated", "CO2", "yes", "Phase III (2070) also about 54 percent hydro."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA1", "LTS-national-not-submitted", "Energy",
     "Non-conventional renewable share of SNI generation, phase III", "ERNC", "share of generation", "37", "percent",
     "absolute", "2070", "not stated", "CO2", "yes", "Printed as about 37 percent (about 8,400 MW)."),
    ("ECU-03", "p.100;p.101", "printed p.96; Tabla 14 printed p.97", "LTS-national-not-submitted", "Energy",
     "A share of thermal generation is kept for stability and security of supply (no number stated)",
     "manteniendo un porcentaje de energia termica", "thermal generation kept", "", "", "", "2070", "not stated",
     "CO2", "no", "The phase II and III shares of Tabla 15 (35 plus 54 percent) leave about 11 percent non-renewable; that sum is ours, not printed."),
    ("ECU-03", "p.100", "printed p.96", "LTS-national-not-submitted", "Energy",
     "Oil exports decline and gradual substitution of fossil fuels from 2038, with crude imports for domestic refining",
     "sustitucion gradual del uso de combustibles fosiles a partir del 2038", "start year", "2038", "year", "", "2038",
     "not stated", "CO2", "no", "Scenario hypothesis, not a target. Refining capacity kept at the reference year level (p.101)."),
    ("ECU-03", "p.104", "Tabla 15 printed p.100, LA2", "LTS-national-not-submitted", "Energy",
     "Energy efficiency: national energy consumption (transport excluded) saved against the trend scenario, phase I",
     "Ahorrar aproximadamente 6500 kBEP", "percent saving against BAU", "8.4", "percent",
     "BAU (trend scenario); about 6,500 kBEP", "2035", "not stated", "CO2", "yes", "Footnote 22: transport not included."),
    ("ECU-03", "p.105", "Tabla 15 printed p.101", "LTS-national-not-submitted", "Energy",
     "Residential electricity use share by substitution of LPG, phase II", "", "electricity share of residential energy",
     "66", "percent", "absolute", "2050", "not stated", "CO2", "yes", "About 80 percent in phase III (2070)."),
    ("ECU-03", "p.105", "Tabla 15 printed p.101", "LTS-national-not-submitted", "Energy",
     "Industry electricity use share by substitution of fossil fuels, phase II", "", "electricity share of industrial energy",
     "64", "percent", "absolute (about 13,800 kBEP)", "2050", "not stated", "CO2", "yes",
     "About 72 percent (about 21,900 kBEP) in 2070; industry uses about 4 percent hydrogen in 2070."),
    ("ECU-03", "p.105", "Tabla 15 printed p.101", "LTS-national-not-submitted", "Energy",
     "Share of industry energy generated from waste, phase II", "", "waste share of industrial energy", "6", "percent",
     "absolute (about 1,200 kBEP)", "2050", "not stated", "CO2", "yes", "About 4 percent (about 1,320 kBEP) in 2070."),
    ("ECU-03", "p.106", "Tabla 15 printed p.102", "LTS-national-not-submitted", "Energy",
     "Electricity share of demand in agriculture, forestry, fishing and fish farming, phase II", "",
     "electricity share of sector energy", "19", "percent", "absolute", "2050", "not stated", "CO2", "yes",
     "About 36 percent in 2070. The 'no especificado' sector: about 14 percent (2050) and 20 percent (2070)."),
    ("ECU-03", "p.106", "Tabla 15 printed p.102, LA3", "LTS-national-not-submitted", "Transport",
     "Transport energy consumption saved against the trend scenario, phase I", "Ahorrar el consumo energetico del transporte",
     "percent saving against BAU", "2.8", "percent", "BAU (trend scenario)", "2035", "not stated", "CO2", "yes", ""),
    ("ECU-03", "p.106", "Tabla 15 printed p.102, LA3", "LTS-national-not-submitted", "Transport",
     "Share of passenger-km served by public transport with diesel buses, phase II", "", "share of passenger-km",
     "40", "percent", "absolute", "2050", "not stated", "CO2", "yes", "About 14 percent in 2070."),
    ("ECU-03", "p.106", "Tabla 15 printed p.102, LA3", "LTS-national-not-submitted", "Transport",
     "Share of passenger transport using hybrid vehicles, phase II", "", "share of passenger transport", "13.36",
     "percent", "absolute (about 340,000 vehicles)", "2050", "not stated", "CO2", "yes",
     "Same share in 2070 (about 350,000 vehicles)."),
    ("ECU-03", "p.107", "Tabla 15 printed p.103, LA3", "LTS-national-not-submitted", "Transport",
     "Electric light freight vehicles as share of freight vehicles, phase II", "", "share of freight vehicles", "22",
     "percent", "absolute (about 180,000 vehicles)", "2050", "not stated", "CO2", "yes",
     "About 51 percent (about 600,000 vehicles) in 2070."),
    ("ECU-03", "p.107", "Tabla 15 printed p.103, LA3", "LTS-national-not-submitted", "Transport",
     "Share of the freight fleet using hydrogen, phase III", "", "share of freight fleet", "11", "percent", "absolute",
     "2070", "not stated", "CO2", "yes", "Beyond 2050, following the green hydrogen roadmap (p.100)."),
    ("ECU-03", "p.115;p.117", "Figura 22 printed p.111; Tabla 21 printed p.113", "LTS-national-not-submitted", "Agriculture",
     "Agriculture emissions target, phase I", "", "sector emissions", "16591", "Gg CO2eq", "absolute (2018: 14,334 Gg)",
     "2035", "not stated", "CH4, N2O", "no", "17,257 Gg (2050) and 19,162 Gg (2070). 41.5 percent below the trend in 2070 (p.113)."),
    ("ECU-03", "p.116", "Tabla 21 printed p.112", "LTS-national-not-submitted", "Agriculture",
     "Share of the cattle herd under climate-smart livestock practices (GCI), phase I", "ganaderia climaticamente inteligente",
     "share of herd", "20", "percent", "absolute", "2035", "not stated", "CH4, N2O", "no", "50 percent (2050), 90 percent (2070)."),
    ("ECU-03", "p.116", "Tabla 21 printed p.112", "LTS-national-not-submitted", "Agriculture",
     "Replacement of synthetic nitrogen fertilizer by organic fertilizer, phase I", "", "share replaced", "10", "percent",
     "absolute", "2035", "not stated", "N2O", "no", "20 percent (2050), 30 percent (2070)."),
    ("ECU-03", "p.125", "Figura 26 printed p.121", "LTS-national-not-submitted", "LULUCF",
     "LULUCF net emissions target, phase I (sector becomes a net sink around 2035)", "", "sector net emissions", "-611",
     "Gg CO2eq", "absolute (2018: 14,910 Gg)", "2035", "not stated", "CO2", "no",
     "-20,547 Gg (2050) and -26,970 Gg (2070)."),
    ("ECU-03", "p.126", "Tabla 24 printed p.122", "LTS-national-not-submitted", "LULUCF",
     "Reduction of net deforestation, phase I", "deforestacion neta", "percent reduction", "45.5", "percent",
     "not stated (about 45,983 ha per year in 2035)", "2035", "not stated", "CO2", "no",
     "73.48 percent (about 12,194.5 ha per year) in 2050."),
    ("ECU-03", "p.126", "Tabla 24 printed p.122", "LTS-national-not-submitted", "LULUCF",
     "Forest cover under legal protection, phase I", "", "area under protection", "7.29", "Mha",
     "increase of 17.41 percent", "2035", "not stated", "CO2", "no", "About 9 Mha (2050) and 9.13 Mha (2070)."),
    ("ECU-03", "p.127", "Tabla 24 printed p.123", "LTS-national-not-submitted", "LULUCF",
     "Area restored per year, phase I", "", "restoration rate", "3249", "ha per year", "absolute", "2035", "not stated",
     "CO2", "no", "About 11,956 ha per year (2050) and 12,953 ha per year (2070)."),
    ("ECU-03", "p.127", "Tabla 24 printed p.123", "LTS-national-not-submitted", "LULUCF",
     "Area of commercial forest plantations, phase I", "", "plantation area", "266963", "ha", "increase of 68.79 percent on the base year",
     "2035", "not stated", "CO2", "no", "About 422,901 ha (2050) and 644,405 ha (2070)."),
    ("ECU-03", "p.133", "Figura 30 printed p.129", "LTS-national-not-submitted", "IPPU",
     "IPPU emissions target, phase I", "", "sector emissions", "3050", "Gg CO2eq", "absolute (2018: 2,425 Gg)", "2035",
     "not stated", "CO2", "no", "4,245 Gg (2050), 5,792 Gg (2070); about 30 percent below the trend in 2070 (p.132)."),
    ("ECU-03", "p.134", "Tabla 26 printed p.130", "LTS-national-not-submitted", "IPPU",
     "Clinker factor in cement production, phase I", "factor clinker", "clinker factor", "68", "percent", "absolute",
     "2035", "not stated", "CO2", "no", "60 percent in 2050, kept at 60 percent or less to 2070."),
    ("ECU-03", "p.134", "Tabla 26 printed p.130", "LTS-national-not-submitted", "IPPU",
     "CO2 from cement production used through carbon capture and use projects, phase I", "", "CO2 used", "100", "kt CO2",
     "absolute", "2035", "not stated", "CO2", "no", "300 kt in 2050."),
    ("ECU-03", "p.135", "Tabla 26 printed p.131", "LTS-national-not-submitted", "IPPU",
     "Reduction of HFC and PFC imports, phase I", "", "percent reduction of imports", "30", "percent",
     "not stated", "2035", "not stated", "HFC, PFC", "no", "80 percent (2050) and 100 percent (2070)."),
    ("ECU-03", "p.143", "Figura 36 printed p.139", "LTS-national-not-submitted", "Waste",
     "Waste emissions target, phase I", "", "sector emissions", "2347", "Gg CO2eq", "absolute (2018: 2,541 Gg)", "2035",
     "not stated", "CH4, N2O", "no", "2,785 Gg (2050), 3,650 Gg (2070); about 50 percent below the trend in 2070 (p.143)."),
    ("ECU-03", "p.145", "Tabla 28 printed p.141", "LTS-national-not-submitted", "Waste",
     "Share of solid waste managed in open dumps, phase I", "botaderos a cielo abierto", "share of waste", "47",
     "percent", "absolute", "2035", "not stated", "CH4", "no",
     "30 percent (2050) and 0 percent (2070); 70 percent of disposal sites operated technically in 2035."),
    ("ECU-03", "p.144", "Tabla 28 printed p.140", "LTS-national-not-submitted", "Waste",
     "Share of solid waste managed through recycling, treatment and recovery, phase I", "", "share of waste", "10",
     "percent", "absolute", "2035", "not stated", "CH4", "no", "34 percent (2050), 37 percent (2070)."),
    ("ECU-03", "p.145", "Tabla 28 printed p.141", "LTS-national-not-submitted", "Waste",
     "Share of landfill waste processed in new landfill biogas power plants, phase I", "", "share of landfill waste",
     "10", "percent", "absolute", "2035", "not stated", "CH4", "no",
     "50 percent (2050), 100 percent (2070). Biogas electricity is counted in the energy sector (p.139)."),
    ("ECU-03", "p.147", "Tabla 28 printed p.143", "LTS-national-not-submitted", "Waste",
     "Share of wastewater treated in treatment plants, phase I", "", "share of wastewater", "8", "percent", "absolute",
     "2035", "not stated", "CH4, N2O", "no", "14 percent (2050), 16 percent (2070)."),
    # ---- ECU-04 BTR1 (first NDC tracking)
    ("ECU-04", "p.215", "printed p.63", "BTR", "economy-wide",
     "First NDC conditional target adjusted in the implementation plan (four sectors)", "", "percent reduction against BAU",
     "13.5", "percent", "BAU (trend scenario, base year 2010)", "2025", "conditional", "CO2, CH4, N2O", "no",
     "Superseded NDC; reported for context."),
    ("ECU-04", "p.226", "Tabla 29 printed p.74", "BTR", "economy-wide",
     "Progress of the first NDC in 2023: unconditional reduction reached, against the 9 percent target",
     "% cumplimiento", "percent reduction achieved", "8.61", "percent", "BAU (trend scenario)", "2023",
     "unconditional", "CO2, CH4, N2O", "no", "6,449.96 kt CO2eq reduced in 2023 (Tabla 27, p.226). Status, not a target."),
    ("ECU-04", "p.217;p.222", "Tabla 19 printed p.65; Tabla 23 printed p.70", "BTR", "Energy",
     "First NDC hydropower development: recalculated reduction potential", "Desarrollo de Centrales Hidroelectricas",
     "emission reduction", "4400", "kt CO2eq", "BAU", "2025", "unconditional", "CO2", "no",
     "First NDC value was 6,000 kt (Tabla 18, p.217)."),
    ("ECU-04", "p.217;p.221", "Tabla 19 printed p.65; Tabla 22 printed p.69", "BTR", "Transport",
     "Gasoline with ethanol (Ecopais blend), new initiative of the first NDC", "Preparacion y despacho de gasolinas con etanol",
     "emission reduction", "885.46", "kt CO2eq", "BAU (cumulative 2023 to 2025)", "2025", "unconditional", "CO2", "no",
     "120 kt in 2025 in Tabla 19 (p.217). Biofuel blending measure."),
    ("ECU-04", "p.222", "Tabla 24 printed p.70", "BTR", "Energy",
     "First NDC conditional energy measures: national energy efficiency plan", "Plan Nacional de Eficiencia Energetica",
     "emission reduction", "2300", "kt CO2eq", "BAU", "2025", "conditional", "CO2", "no",
     "Other conditional energy measures: OGE&EE 1,300 kt; renewables 2,700 kt; hydrocarbons efficiency 500 kt."),
    ("ECU-04", "p.222", "Tabla 24 printed p.70", "BTR", "Transport",
     "First NDC conditional NAMA for freight and passenger transport", "NAMA de transporte de carga y pasajeros",
     "emission reduction", "1740", "kt CO2eq", "BAU", "2025", "conditional", "CO2", "no", ""),
    ("ECU-04", "p.222;p.223", "Tabla 23 printed p.70; Tabla 24 printed p.71", "BTR", "IPPU",
     "First NDC clinker substitution in cement (unconditional)", "", "emission reduction", "130", "kt CO2eq", "BAU",
     "2025", "unconditional", "CO2", "no", "Conditional extension 323 kt (p.223)."),
    ("ECU-04", "p.237;p.238", "printed p.85 to p.86", "BTR", "LULUCF",
     "First NDC LULUCF: PROAmazonia reduction potential (4 percent)", "", "emission reduction", "16078.32", "kt CO2eq",
     "forest reference emission level 43,418.13 kt per year", "2025", "unconditional", "CO2", "no",
     "Conditional REDD+ Action Plan: 62,074.31 kt (16 percent more)."),
    # ---- sector plans
    ("ECU-07", "p.159", "Tabla No. 4-6 (printed p.132)", "sector plan", "Energy",
     "Generation expansion plan 2023-2032: new hydro capacity", "Plan de Expansion de Generacion", "new capacity",
     "4034", "MW", "absolute (additions 2023 to 2032)", "2032", "not stated", "CO2", "no",
     "Includes two 1,200 MW stages in 2031 and 2032."),
    ("ECU-07", "p.159", "Tabla No. 4-6 (printed p.132)", "sector plan", "Energy",
     "Generation expansion plan 2023-2032: new non-conventional renewable capacity (hydro excluded)", "ERNC",
     "new capacity", "1683", "MW", "absolute (additions 2023 to 2032)", "2032", "not stated", "CO2", "no", ""),
    ("ECU-07", "p.159", "Tabla No. 4-6 (printed p.132)", "sector plan", "Energy",
     "Generation expansion plan 2023-2032: new thermal capacity", "TERMICO", "new capacity", "587", "MW",
     "absolute (additions 2023 to 2032)", "2032", "not stated", "CO2", "no", "Total expansion 6,304 MW."),
    ("ECU-08", "p.20", "printed p.18", "sector plan", "Energy",
     "Minimum energy avoided by the efficiency plan over 2016 to 2035", "energia evitada", "cumulative energy avoided",
     "543", "Mbep", "BAU (cumulative 2016 to 2035)", "2035", "not stated", "CO2", "no",
     "With an estimated GHG reduction of 65 Mt CO2e (same page)."),
    ("ECU-08", "p.65", "Tabla 4 (printed p.63)", "sector plan", "Transport",
     "Transport cumulative energy saving by 2035", "", "cumulative energy saving", "339.6", "Mbep",
     "BAU (cumulative)", "2035", "not stated", "CO2", "no", ""),
    ("ECU-08", "p.65", "Tabla 4 (printed p.63)", "sector plan", "Transport",
     "Ethanol blending in gasoline by 2025", "10% de etanol", "blend share", "10", "percent", "absolute", "2025",
     "not stated", "CO2", "no", "Biodiesel blend 5 percent by 2025 (same row)."),
    ("ECU-08", "p.67", "printed p.65", "sector plan", "Energy",
     "Electricity distribution losses reduced from 21.4 percent (2007) to 8.3 percent in 2035", "perdidas",
     "distribution losses", "8.3", "percent", "21.4 percent in 2007", "2035", "not stated", "CO2", "no", ""),
    ("ECU-09", "p.6", "summary of the roadmap (capacities)", "sector plan", "Energy",
     "Electrolysis capacity planned for green hydrogen", "capacidad de electrolisis", "installed capacity", "6", "GW",
     "absolute", "2050", "not stated", "CO2", "no", "1 GW in 2030 and 3 GW in 2040 (same sentence)."),
]

TCOLS = ["target_id", "source_id", "page", "table_or_figure", "document_kind", "sector", "description", "original_term",
         "indicator", "value", "unit", "base_or_reference", "target_year", "conditionality", "gases", "read_as_image",
         "note"]
rows = []
for i, t in enumerate(T, start=1):
    rows.append(dict(zip(TCOLS, [f"ECU-T{i:03d}"] + list(t))))
write("targets_ECU.csv", TCOLS, rows)

# ---------------------------------------------------------------- projections
P = []


def add(src, page, tab, scen, sector, year, value, note="", gas="CO2eq (CO2, CH4, N2O)", unit="kt CO2eq"):
    P.append({"source_id": src, "page": page, "table_or_figure": tab, "scenario_as_named": scen, "sector": sector,
              "gas": gas, "unit": unit, "year": year, "value": value, "note": note})


# BTR1 Tabla 31: trend projection by sector (AR2 GWP, IPCC 1996)
t31 = {
    "Energy": [(1994, 14994.92), (2000, 21648.27), (2006, 29541.34), (2010, 35812.52), (2020, 46600), (2025, 51100)],
    "IPPU": [(1994, 2036.81), (2000, 1389.97), (2006, 2762.61), (2010, 2659.25), (2020, 3512), (2025, 3718)],
    "Agriculture": [(1994, 15029.29), (2000, "12307.30"), (2006, 14051.63), (2010, 14420.68), (2015, 15092.57),
                    (2020, 15605.68), (2022, 15656.53), (2025, 15892.95)],
    "LULUCF": [(2000, 43418.13), (2006, 43418.13), (2010, 43418.13), (2015, 43418.13), (2020, 43418.13),
               (2022, 43418.13), (2025, 43418.13)],
    "Waste": [(1994, 1433.51), (2000, 1688.19), (2006, 1845.61), (2010, 3347.00), (2020, 3903.00), (2025, 4168.00)],
    "economy-wide (without LULUCF)": [(2010, 56239.45), (2020, 69620.68), (2025, 74878.95)],
    "economy-wide (with LULUCF)": [(2010, 99657.58), (2020, 113038.81), (2025, 118297.08)],
}
for sec, ser in t31.items():
    for y, v in ser:
        add("ECU-04", "p.234", "Tabla 31 printed p.82", "Tendencial (first NDC trend)", sec, y, v,
            "Years to 2010 are inventory values; 2020 and 2025 projected. AR2 GWP. LULUCF is the constant forest reference level.")
for scen, vals in [("Tendencial", (56038, 71641, 76904)), ("Incondicional", (56038, 62519, 67774)),
                   ("Condicional", (56038, 61135, 60824))]:
    for y, v in zip((2010, 2020, 2025), vals):
        add("ECU-04", "p.214", "Tabla 15 printed p.62", scen + " (first NDC)", "four sectors (Energy, IPPU, Agriculture, Waste)", y, v)
for scen, vals in [("Tendencial", (54028, 69621, 74879)), ("Incondicional", (54028, 62901, 68142)),
                   ("Condicional", (54028, 53738, 58031))]:
    for y, v in zip((2010, 2020, 2025), vals):
        add("ECU-04", "p.215", "Tabla 16 printed p.63", scen + " (first NDC implementation plan)",
            "four sectors (Energy, IPPU, Agriculture, Waste)", y, v, "Values updated in 2020.")
for sec, tend, inc, cond in [("Energy", 51100, 44540, 36000), ("Agriculture", 15893, 15876, 14928),
                             ("IPPU", 3718, 3588, 3265), ("Waste", 4168, 4138, 3838)]:
    add("ECU-04", "p.212", "Tabla 13 printed p.60", "Tendencial (first NDC implementation plan)", sec, 2025, tend)
    add("ECU-04", "p.212", "Tabla 13 printed p.60", "Incondicional (first NDC implementation plan)", sec, 2025, inc)
    add("ECU-04", "p.212", "Tabla 13 printed p.60", "Condicional (first NDC implementation plan)", sec, 2025, cond)
# PLANMICC (Gg CO2eq = kt CO2eq)
G = "Gg CO2eq"
add("ECU-03", "p.96", "printed p.92 (text on Figura 15)", "Tendencial and CC 2070 (common base year)", "economy-wide (net)", 2018, 75326.87, "INGEI 2018 base.", unit=G)
add("ECU-03", "p.95;p.96", "Figura 15 printed p.91; text p.92", "Escenario Tendencial", "economy-wide (net)", 2070, 118000, "Approximate.", unit=G)
add("ECU-03", "p.95;p.96", "Figura 15 printed p.91; text p.92", "Escenario Compromiso Climatico 2070", "economy-wide (net)", 2070, 36400, "Approximate.", unit=G)
fig16 = {
    "Energy (transport)": (19425, 20245, 18982, 14082),
    "Energy (other energy)": (20321, 19039, 16808, 19812),
    "LULUCF (emissions)": (40908, 31838, 21358, 17578),
    "Agriculture (livestock)": (9034, 9921, 9147, 6735),
    "Agriculture (crops)": (5485, 7109, 8654, 12797),
    "IPPU": (2425, 3050, 4245, 5792),
    "Waste": (2667, 2643, 3255, 4120),
    "LULUCF (removals)": (-25998, -32449, -41905, -44549),
}
for sec, vals in fig16.items():
    for y, v in zip((2018, 2035, 2050, 2070), vals):
        add("ECU-03", "p.97", "Figura 16 printed p.93 (read as image)", "Escenario Compromiso Climatico 2070", sec, y, v,
            "Bar labels read from the page image; waste labels differ from Figura 36 (2,541; 2,347; 2,785; 3,650).", unit=G)
for y, v in ((2018, 38400), (2035, 39200), (2050, 35800), (2070, 33900)):
    add("ECU-03", "p.101;p.102", "Figura 17 printed p.97; Figura 19 printed p.98", "Escenario Compromiso Climatico 2070", "Energy (including transport)", y, v, unit=G)
add("ECU-03", "p.101", "Figura 17 printed p.97", "Escenario Tendencial", "Energy (including transport)", 2070, 66300, unit=G)
for y, v in ((2018, 14334), (2035, 16591), (2050, 17257), (2070, 19162)):
    add("ECU-03", "p.115", "Figura 22 printed p.111", "Escenario Compromiso Climatico 2070", "Agriculture", y, v, unit=G)
add("ECU-03", "p.113", "Figura 20 printed p.109", "Escenario Tendencial", "Agriculture", 2070, 32700, unit=G)
for y, v in ((2018, 14910), (2035, -611), (2050, -20547), (2070, -26970)):
    add("ECU-03", "p.125", "Figura 26 printed p.121", "Escenario Compromiso Climatico 2070", "LULUCF (net)", y, v, unit=G)
add("ECU-03", "p.120", "Figura 23 printed p.116 (read as image)", "Escenario Tendencial", "LULUCF (net)", 2070, 3300, "Approximate label.", unit=G)
for y, v in ((2018, 2425), (2035, 3050), (2050, 4245), (2070, 5792)):
    add("ECU-03", "p.133", "Figura 30 printed p.129", "Escenario Compromiso Climatico 2070", "IPPU", y, v, unit=G)
add("ECU-03", "p.131", "Figura 29 printed p.127", "Escenario Tendencial", "IPPU", 2070, 8000, "Approximate label.", unit=G)
for y, v in ((2018, 2541), (2035, 2347), (2050, 2785), (2070, 3650)):
    add("ECU-03", "p.143", "Figura 36 printed p.139", "Escenario Compromiso Climatico 2070", "Waste", y, v, unit=G)
add("ECU-03", "p.142", "Figura 35 printed p.138", "Escenario Tendencial", "Waste", 2070, 7200, "Approximate label.", unit=G)

write("projections_ECU.csv", ["source_id", "page", "table_or_figure", "scenario_as_named", "sector", "gas", "unit",
                              "year", "value", "note"], P)
print(len(src_rows), "sources;", len(PEND), "pending;", len(rows), "targets;", len(P), "projection rows")
