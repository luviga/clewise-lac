"""Write parts/sources_HON.csv, parts/sources_pending_HON.csv, targets_HON.csv and projections_HON.csv.

Usage: python -I write_tables_HON.py <job_folder>
All values were read on the cited pages of the downloaded files (text cache in downloads/HON/text).
The NDC 3.0 BAU table (HON-01 p.24) is parsed from the text cache of that page.
"""
import csv
import hashlib
import os
import re
import sys

import pdfplumber

JOB = sys.argv[1]
D = os.path.join(JOB, "downloads", "HON")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def npages(path):
    with pdfplumber.open(path) as pdf:
        return len(pdf.pages)


def write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(path, len(rows))


# ------------------------------------------------------------------ sources
SRC = [
    ("HON-01", "NDC",
     "https://unfccc.int/sites/default/files/2026-01/HON%20NDC%203.0%202026%20Oficial.pdf (byte-identical copy: https://cdn.climatepolicyradar.org/navigator/HND/2026/honduras-nationally-determined-contribution-ndc3-0_535c514b136519bd8db14e3a750df08d.pdf; record https://app.climatepolicyradar.org/document/honduras-nationally-determined-contribution-ndc3-0_bd82)",
     "Contribucion Determinada a Nivel Nacional (NDC 3.0) de Honduras, 2021-2035",
     "Secretaria de Recursos Naturales y Ambiente (SERNA), Gobierno de Honduras",
     "2026-01-21 (submission date in the Climate Policy Radar record; citation 'SERNA 2026' on p.4; UNFCCC folder 2026-01)",
     "HON_NDC3_2026.pdf", "Spanish"),
    ("HON-02", "NDC",
     "https://unfccc.int/sites/default/files/2025-09/Honduras%20Segunda%20Actualizacio%CC%81n%20de%20su%20NDC%20(2021-2030)serna_rev_final.pdf (byte-identical copy: https://cdn.climatepolicyradar.org/navigator/HND/2025/honduras-nationally-determined-contribution-ndc3-0_bd3106d9781869c1c9d56c76c52e1b6f.pdf, which is the file behind the brief's lead record climate-laws.org/document/honduras-nationally-determined-contribution-ndc3-0_21f1)",
     "Segunda Actualizacion de la Contribucion Nacional Determinada de Honduras (2021-2030)",
     "Secretaria de Recursos Naturales y Ambiente (SERNA), Direccion Nacional de Cambio Climatico",
     "2025-04-01 (publication date printed on p.20); UNFCCC folder 2025-09; Climate Policy Radar record date 2025-09-22",
     "HON_NDC_2nd_update_2025.pdf", "Spanish"),
    ("HON-03", "NDC",
     "https://unfccc.int/sites/default/files/NDC/2022-06/NDC%20de%20Honduras_%20Primera%20Actualizaci%C3%B3n.pdf (identical bytes also at https://cdn.climatepolicyradar.org/navigator/HND/1900/honduras-first-ndc-updated-submission_89969b2d7a367ab035f8a67d0706a9dd.pdf and https://faolex.fao.org/docs/pdf/hon216315.pdf)",
     "Actualizacion de la Contribucion Nacional Determinada de Honduras (first update, 2021)",
     "Secretaria de Recursos Naturales y Ambiente (MiAmbiente+), Direccion Nacional de Cambio Climatico",
     "2021-05 (submitted in May 2021 per HON-05 p.504 and BUR2; Climate Policy Radar record date 2021-05-19)",
     "HON_NDC_update_2021.pdf", "Spanish"),
    ("HON-04", "NDC",
     "https://cdn.climatepolicyradar.org/navigator/HND/1900/honduras-first-ndc-archived_cda7e68cb9a78ea7cdc3bb809cba453e.pdf (record https://app.climatepolicyradar.org/document/honduras-nationally-determined-contribution-ndc1-archived_c54a; UNFCCC copy https://unfccc.int/sites/default/files/NDC/2022-06/Honduras%20INDC_esp.pdf not fetched)",
     "Contribucion Prevista y Determinada a Nivel Nacional de la Republica de Honduras (INDC; first NDC from 2016, archived)",
     "Gobierno de la Republica de Honduras",
     "2015-09 (header of every page); first NDC from 2016-09-21 (Climate Policy Radar record; HON-03 p.46)",
     "HON_INDC_2015.pdf", "Spanish"),
    ("HON-05", "BTR",
     "https://unfccc.int/sites/default/files/resource/DOC_UNIDO_BTR_HDR_1%2030.12.24.pdf (URL cited in HON-01 p.69; downloaded 2026-11-21 and byte-identical to the earlier copy C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z/downloads/d3_ef/HON_BTR1_2024.pdf)",
     "Primer Informe Bienal de Transparencia de la Republica de Honduras (1990-2022) (BTR1; chapter 2 is the national inventory 1990-2022)",
     "Secretaria de Recursos Naturales y Ambiente (SERNA), Direccion Nacional de Cambio Climatico",
     "2024-12 (cover p.2)", "HON_BTR1_2024.pdf", "Spanish"),
    ("HON-06", "NID",
     "https://unfccc.int/sites/default/files/resource/Document%20NIR%20Hn%202024.pdf (downloaded 2026-11-21 and byte-identical to the earlier copy C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z/downloads/d3_ef/HON_NIR_2024.pdf, register row FR2-D3-HONNIR)",
     "Informe del Inventario Nacional de Gases de Efecto Invernadero 2016-2020 de Honduras (inventory report of the BUR2)",
     "Secretaria de Recursos Naturales y Ambiente (SERNA)", "2024-02 (cover p.1)",
     "HON_NIR_2024.pdf", "Spanish"),
    ("HON-07", "BUR",
     "https://unfccc.int/sites/default/files/resource/Document%20BUR%20Hn%202024.pdf (downloaded 2026-11-21 and byte-identical to the earlier copy C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z/downloads/d3_ef/HON_BUR2_2024.pdf)",
     "Segundo Informe Bienal de Actualizacion de Honduras (BUR-2)",
     "Secretaria de Recursos Naturales y Ambiente (SERNA)", "2024-02 (cover p.1)",
     "HON_BUR2_2024.pdf", "Spanish"),
    ("HON-08", "sector plan",
     "https://cnd.enee.hn/wp-content/uploads/2026/09/Informe-PIEG-2026-2035.pdf (listed on https://cnd.enee.hn/pieg-y-pert-2026-2035/ as the plan of the final approval, Acuerdo CREE 81-2026)",
     "Plan Indicativo de Expansion de la Generacion 2026-2035 (PIEG 2026-2035), final approved version",
     "Centro Nacional de Despacho (CND), operador del sistema; approved by the Comision Reguladora de Energia Electrica (CREE)",
     "2026-09-18 (publication date on the CND page; document control p.2: definitive approval 16/09/2026; draft 05/09/2025)",
     "HON_PIEG_2026-2035_final.pdf", "Spanish"),
]
rows = []
for sid, kind, url, title, pub, date, fname, lang in SRC:
    p = os.path.join(D, fname)
    rows.append([sid, "Honduras", kind, url, title, pub, date, "2026-11-21", sha(p),
                 "downloads/HON/" + fname, npages(p), lang])
write(os.path.join(JOB, "parts", "sources_HON.csv"),
      ["id", "country", "kind", "URL", "title", "publisher", "date", "accessed", "SHA-256", "file", "pages",
       "language"], rows)

PEND = [
    ["Honduras", "LTS-national-not-submitted",
     "Estrategia Nacional de Descarbonizacion y Resiliencia Climatica de Honduras (ENDRCH), the long-term strategy in preparation",
     "https://unfccc.int/process/the-paris-agreement/long-term-strategies (curl and WebFetch); web searches for the ENDRCH title and for a Honduras LT-LEDS; https://app.climatepolicyradar.org/geographies/honduras; https://serna.gob.hn/?s=descarbonizaci%C3%B3n",
     "UNFCCC portal: Incapsula bot-check page to curl (956 bytes) and empty page to WebFetch; no published ENDRCH document found by search; the Climate Policy Radar country page lists no long-term strategy; SERNA site search returned no document",
     "Not a fetch failure of a known file: HON-01 (p.14, p.15) and HON-05 (p.563 to p.565) say the LTS is being consolidated and has not been submitted. No long-term document exists to register."],
    ["Honduras", "sector plan",
     "Estrategia Nacional de Movilidad Electrica de Honduras (ENME), cited by HON-01 p.27 for the electric vehicle targets",
     "https://sen.hn/?s=movilidad+electrica; https://sen.hn/?s=ENME; https://sen.hn/estrategia-nacional-de-movilidad-electrica-en-honduras/; https://sen.hn/electromovilidad/; https://portalunico.iaip.gob.hn/ver_archivo/MTQwMjQ2NQ== (and three other IAIP ids from search results); web search",
     "SEN pages are news items with no PDF link; IAIP transparency portal returned HTTP 403 for all four ids; web search found only a 2022 draft proposal on mobilityportal.lat (not the 2024 strategy, not fetched)",
     "The NDC 3.0 states the 3 and 7.5 percent fleet targets itself; they are taken from HON-01."],
    ["Honduras", "other",
     "Anexo Tecnico de la NDC 3.0 (indicators and measure sheets, 'Fichas Anexas'), referred to in HON-01 p.17, p.26, p.36",
     "web search for the annex title; https://unfccc.int/sites/default/files/2026-01/ folder (only the main NDC file is listed in search results)",
     "no published copy found",
     "The ICTU appendix announced on HON-01 p.68 has only a cover page in the submitted PDF (read as image)."],
]
write(os.path.join(JOB, "parts", "sources_pending_HON.csv"),
      ["country", "kind", "title", "urls_tried", "errors", "note"], PEND)

# ------------------------------------------------------------------ targets
TH = ["target_id", "source_id", "page", "table_or_figure", "document_kind", "sector", "description",
      "original_term", "indicator", "value", "unit", "base_or_reference", "target_year", "conditionality",
      "gases", "read_as_image", "note"]
G3 = "CO2, CH4, N2O, HFC, NMVOC"
G21 = "CO2, CH4, N2O, HFC"
T = []


def t(src, page, tab, kind, sector, desc, orig, ind, val, unit, base, year, cond, gases, img="no", note=""):
    T.append([None, src, page, tab, kind, sector, desc, orig, ind, val, unit, base, year, cond, gases, img, note])


# HON-01 NDC 3.0
C = "conditional"
t("HON-01", "p.23;p.25", "printed p.22, p.24", "NDC", "economy-wide",
  "Economy-wide single-year target: net emissions 12,847.2 Gg CO2e below BAU in 2035 (BAU 65,616.6), all sectors incl. LULUCF",
  "meta de año único: 2035", "emission reduction against BAU", "12847.2", "Gg CO2e",
  "BAU (BAU 2035 printed '65,616,6' Gg CO2e on p.23; 65,617 in Tabla 2 p.24)", "2035", C, G3,
  note="Fully conditional on international climate finance (p.13, p.17, p.23). p.25 prints a different 'national mitigation target' of 7,268 Gg for 2021-2035 (row below); the sector values on p.25 add up to 12,847.2.")
t("HON-01", "p.22", "printed p.21", "NDC", "economy-wide",
  "Reduction of 19.6 percent against BAU 'by 2035', printed as cumulative over 2021-2035 but equal to 12,847.2 / 65,616.6",
  "reducción nacional de emisiones acumulada durante el periodo 2021-2035 de 19.6 %", "percent reduction against BAU",
  "19.6", "percent", "BAU", "2035", C, G3,
  note="Same sentence says it is equivalent to 8,564.8 Gg, which is the 2030 value (p.23). Read as the 2035 single-year percentage (12,847.2 / 65,616.6 = 19.58 percent).")
t("HON-01", "p.22;p.23;p.25", "printed p.21, p.22, p.24", "NDC", "economy-wide",
  "Net emissions 8,564.8 Gg CO2e below BAU in 2030 (BAU 50,381.3), kept from the second NDC update",
  "Las emisiones se reducirán en 8,564.8 Gg CO2e para el año 2030", "emission reduction against BAU", "8564.8",
  "Gg CO2e", "BAU (BAU 2030 50,381.3 Gg CO2e)", "2030", C, G3)
t("HON-01", "p.22", "printed p.21", "NDC", "economy-wide",
  "17 percent reduction of projected emissions in 2030, kept from the second update and extended to the 2035 BAU",
  "reducir en un 17% las emisiones proyectadas", "percent reduction against BAU", "17", "percent", "BAU", "2030", C, G3,
  note="8,564.8 / 50,381.3 = 17.0 percent. The second update itself states 16 percent plus 1 percent for LULUCF (HON-02 p.3).")
t("HON-01", "p.25", "printed p.24", "NDC", "economy-wide", "Maximum expected net emissions in 2030",
  "Nivel máximo de emisiones esperadas", "net emissions", "41816.4", "Gg CO2e", "absolute (BAU 50,381.3)", "2030", C, G3)
t("HON-01", "p.25", "printed p.24", "NDC", "economy-wide", "Maximum expected net emissions in 2035",
  "Nivel máximo de emisiones esperadas", "net emissions", "52769", "Gg CO2e", "absolute (BAU 65,616.6)", "2035", C, G3)
t("HON-01", "p.25", "printed p.24", "NDC", "economy-wide",
  "'National mitigation target' of 7,268 Gg CO2e over 2021-2035 printed in the 2035 column",
  "Meta nacional de mitigación", "emission reduction against BAU", "7268", "Gg CO2e", "BAU", "2035", C, G3,
  note="Inconsistent with the 12,847.2 Gg on p.23 and with the sum of the sector values on the same page. Listed for completeness, not compared.")
for yr, val, pct, pg in [("2030", "2519.1", "5", "printed p.24"), ("2035", "3778.6", "5.8", "printed p.24")]:
    t("HON-01", "p.25", pg, "NDC", "Energy",
      f"Energy sector mitigation of {val} Gg CO2e against BAU in {yr} ({pct} percent of the national BAU)",
      f"ENERGIA {pct}% en reducción de emisiones respecto al BAU", "emission reduction against BAU", val, "Gg CO2e",
      "BAU (percentage is of the national net BAU: 2,519.1 / 50,381.3 = 5.0 percent; energy sector BAU in Tabla 2 is 9,161 in 2030 and 8,963 in 2035)",
      yr, C, G3, note="Text says 'during the implementation period 2021-" + yr + "'; the values add up to the single-year national target, so read as the reduction in " + yr + ". Against the energy sector's own BAU this is " + ("27.5" if yr == "2030" else "42.2") + " percent.")
for sec, v30, v35, p30, p35 in [("Agriculture", "4534.3", "6801.5", "9", "10.4"), ("IPPU", "503.8", "755.7", "1", "1.2"),
                                ("Waste", "503.8", "755.7", "1", "1.2"), ("LULUCF", "503.8", "755.7", "1", "1.2")]:
    for yr, val, pct in [("2030", v30, p30), ("2035", v35, p35)]:
        t("HON-01", "p.25", "printed p.24", "NDC", sec,
          f"{sec} mitigation of {val} Gg CO2e against BAU in {yr} ({pct} percent of the national BAU)",
          f"{pct}% en reducción de emisiones respecto al BAU", "emission reduction against BAU", val, "Gg CO2e",
          "BAU (national net BAU)", yr, C, G3,
          note="The 2035 column for IPPU, Waste and LULUCF prints 'respecto al BAU en 2030'; read as 2035." if yr == "2035" and sec != "Agriculture" else "")
t("HON-01", "p.26", "printed p.25", "NDC", "Energy",
  "Renewable share of the electricity generation mix reaches 70 percent by 2030", "70% de la matriz de generación eléctrica",
  "renewable share of generation", "70", "percent", "absolute", "2030", C, G3,
  note="Coherent with the PIEG 2026-2035 (HON-08), with storage and transmission as enabling conditions.")
t("HON-01", "p.26", "printed p.25", "NDC", "Energy",
  "Renewable share of generation kept above 70 percent towards 2035", "mantenerla por encima de este nivel hacia 2035",
  "renewable share of generation", "70", "percent", "absolute (floor)", "2035", C, G3)
t("HON-01", "p.26", "printed p.25", "NDC", "Energy",
  "Electricity intensity reduced in absolute terms by 3.4 kWh/USD in 2030 against 2022", "intensidad eléctrica",
  "electricity intensity reduction", "3.4", "kWh/USD", "2022", "2030", C, G3,
  note="Unit as printed; a reduction of 3.4 kWh per USD looks implausibly large for an intensity, possibly a different scale.")
t("HON-01", "p.26", "printed p.25", "NDC", "Energy",
  "A further 4 kWh/USD reduction of electricity intensity by 2035 against 2022", "4 kWh/USD adicionales en 2035",
  "electricity intensity reduction", "4", "kWh/USD", "2022", "2035", C, G3)
t("HON-01", "p.26", "printed p.25", "NDC", "Energy",
  "Share of electricity in final energy use of the commercial, industrial and residential sectors up by at least 3 percentage points by 2030",
  "al menos 3 puntos porcentuales (p.p.)", "electricity share of final consumption (com, ind, res)", "3",
  "percentage points", "not stated (the intensity target on the same page uses 2022)", "2030", C, G3)
t("HON-01", "p.26", "printed p.25", "NDC", "Energy",
  "Share of electricity in final energy use of the commercial, industrial and residential sectors up by at least 5 percentage points by 2035",
  "al menos 5 p.p.", "electricity share of final consumption (com, ind, res)", "5", "percentage points",
  "not stated", "2035", C, G3)
t("HON-01", "p.27", "printed p.26", "NDC", "Transport",
  "Biofuels reach 5 percent of final energy consumption of transport by 2030, held to 2035",
  "participación del 5% de los biocombustibles en el consumo final del sector", "biofuel share of transport final energy",
  "5", "percent", "absolute", "2030", C, G3, note="Measure also covers biogas digesters on farms and in wastewater plants and energy plantations, without numbers.")
t("HON-01", "p.27", "printed p.26", "NDC", "Energy",
  "Firewood consumption per household 39 percent below the 2012 level by 2030 (improved stoves)",
  "reducir el consumo de leña por hogar en un 39%", "firewood consumption per household", "39", "percent reduction",
  "2012", "2030", C, G3)
t("HON-01", "p.27", "printed p.26", "NDC", "Transport",
  "Electrification of 3 percent of the national vehicle fleet by 2030 (in line with the ENME)",
  "electrificación del 3% del parque vehicular nacional", "electric share of vehicle fleet", "3", "percent of fleet",
  "absolute", "2030", C, G3)
t("HON-01", "p.27", "printed p.26", "NDC", "Transport",
  "Electrification of 7.5 percent of the national vehicle fleet by 2035", "ampliar la ambición a 7.5% hacia el 2035",
  "electric share of vehicle fleet", "7.5", "percent of fleet", "absolute", "2035", C, G3)
t("HON-01", "p.27", "printed p.26", "NDC", "Transport",
  "20 percent of light vehicles are gasoline hybrids by 2035", "20% de los vehículos livianos sean híbridos de gasolina",
  "hybrid share of light vehicles", "20", "percent", "absolute", "2035", C, G3)
t("HON-01", "p.27", "printed p.26", "NDC", "Transport",
  "15 percent of heavy and light freight vehicles are diesel hybrids by 2035",
  "15% de los vehículos de carga pesada y liviana sean híbridos de diésel", "hybrid share of freight vehicles", "15",
  "percent", "absolute", "2035", C, G3)
t("HON-01", "p.27", "printed p.26", "NDC", "Transport",
  "Sustainable urban mobility plans by 2030 (public transport, walking and cycling infrastructure, mobility management), no number",
  "planes de movilidad urbana sostenible", "plans in place", "", "", "absolute", "2030", C, G3)
t("HON-01", "p.28", "printed p.27", "NDC", "IPPU",
  "Clinker factor of cement 7.4 percentage points below the BTR values by 2030", "disminución del factor Clinker",
  "clinker factor reduction", "7.4", "percentage points", "values reported in the BTR", "2030", C, G3)
t("HON-01", "p.28", "printed p.27", "NDC", "IPPU", "Clinker factor 8.5 percentage points below the BTR values by 2035",
  "disminución de 8.5 puntos porcentuales", "clinker factor reduction", "8.5", "percentage points",
  "values reported in the BTR", "2035", C, G3)
t("HON-01", "p.28", "printed p.27", "NDC", "IPPU", "HFC consumption held at 90 percent of the Kigali baseline in 2029",
  "mantener el consumo de HFCs en un 90% para 2029", "HFC consumption relative to baseline", "90", "percent of baseline",
  "Kigali baseline", "2029", C, "HFC")
t("HON-01", "p.28", "printed p.27", "NDC", "IPPU", "HFC consumption held at 70 percent of the Kigali baseline in 2035",
  "70% para 2035", "HFC consumption relative to baseline", "70", "percent of baseline", "Kigali baseline", "2035", C, "HFC")
t("HON-01", "p.29", "printed p.28", "NDC", "Agriculture",
  "Sustainable livestock model (NAMA Ganaderia) on 20 percent of the country's farms by 2035", "20% de las fincas del país",
  "share of farms", "20", "percent of farms", "absolute", "2035", C, G3)
t("HON-01", "p.29", "printed p.28", "NDC", "Agriculture",
  "Livestock measure cuts 2,100 Gg CO2e cumulative to 2035", "2100 Gg CO2e acumulados al 2035",
  "cumulative emission reduction", "2100", "Gg CO2e", "BAU", "2035", C, G3)
t("HON-01", "p.29", "printed p.28", "NDC", "Agriculture", "Diversified agroforestry in coffee on 3,300 farms by 2035",
  "3,300 fincas para 2035", "farms", "3300", "farms", "absolute", "2035", C, G3)
t("HON-01", "p.29", "printed p.28", "NDC", "Agriculture",
  "Efficient nitrogen fertiliser management (4R, slow release, organic) on 3,300 coffee farms by 2035", "prácticas 4R",
  "farms", "3300", "farms", "absolute", "2035", C, G3)
t("HON-01", "p.29", "printed p.28", "NDC", "Agriculture",
  "Biodigesters, composting or oxidation ponds in 160 coffee processing plants (beneficios) by 2035, with biogas or heat use",
  "160 beneficios", "processing plants", "160", "plants", "absolute", "2035", C, G3)
t("HON-01", "p.29", "printed p.28", "NDC", "Agriculture",
  "80 coffee processing plants with solar dryers replacing electric or mechanical dryers by 2035", "80 instalaciones modernizadas",
  "installations", "80", "installations", "absolute", "2035", C, G3)
t("HON-01", "p.30", "printed p.29", "NDC", "Agriculture",
  "Reduced nitrogen fertiliser use on 12.7 percent of the agricultural area by 2035", "12.7 % del área dedicada a la agricultura",
  "share of agricultural area", "12.7", "percent of area", "absolute", "2035", C, G3)
t("HON-01", "p.30", "printed p.29", "NDC", "Agriculture", "Drip irrigation on 20,000 ha by 2035", "20 mil hectáreas al 2035",
  "area", "20", "thousand ha", "absolute", "2035", C, G3)
t("HON-01", "p.30", "printed p.29", "NDC", "LULUCF", "LULUCF net emissions 1 percent below BAU in 2030",
  "reducir las emisiones netas del sector UTCUTS en un 1%", "percent reduction against BAU", "1", "percent", "BAU",
  "2030", C, "CO2")
t("HON-01", "p.38", "printed p.37 (adaptation component)", "NDC", "LULUCF",
  "Net loss of forest cover in conservation areas 70 percent lower by 2035 (Restoration and Zero Deforestation strategies)",
  "reducir en un 70% la pérdida neta de cobertura forestal en las áreas de conservación", "reduction of net forest loss",
  "70", "percent", "not stated", "2035", C, "CO2", note="Adaptation measure with a direct mitigation effect; listed because it is quantified.")
t("HON-01", "p.31", "printed p.30", "NDC", "Waste",
  "Operating sanitary landfill with gas capture in Tegucigalpa by 2030 and energy use of biogas by 2035 (capacity up to 8 million t)",
  "relleno sanitario operativo en Tegucigalpa", "landfill capacity", "8", "million t of solid waste", "absolute", "2035", C, "CH4")
t("HON-01", "p.31", "printed p.30", "NDC", "Waste", "Annual per capita generation of non-special solid waste 5 percent lower by 2030",
  "reducir en un 5% la generación anual per cápita", "per capita waste generation reduction", "5", "percent", "baseline (not quantified)",
  "2030", C, "CH4")
t("HON-01", "p.31", "printed p.30", "NDC", "Waste", "Per capita waste generation 10 percent lower by 2035",
  "reducción del 10% a 2035", "per capita waste generation reduction", "10", "percent", "baseline (not quantified)", "2035", C, "CH4")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste", "Recovery rate of recyclable waste (incl. organic) 22 percent by 2030",
  "tasa de aprovechamiento de residuos valorizables", "recovery rate", "22", "percent", "absolute", "2030", C, "CH4")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste", "Recovery rate of recyclable waste 30 percent by 2035",
  "al 30% para el 2035", "recovery rate", "30", "percent", "absolute", "2035", C, "CH4")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste", "3 final disposal sites with methane use by 2030",
  "3 sitios de disposición final ... con aprovechamiento de metano", "sites", "3", "sites", "absolute", "2030", C, "CH4")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste", "4 final disposal sites with methane use by 2035", "4 para 2035",
  "sites", "4", "sites", "absolute", "2035", C, "CH4")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste", "Managed final disposal sites in 6 additional municipalities by 2035",
  "6 municipios adicionales", "municipalities", "6", "municipalities", "absolute", "2035", C, "CH4")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste",
  "80 percent of wastewater treatment plants diagnosed (and compliant) by 2030", "80% del total de las Plantas de Tratamiento",
  "share of plants", "80", "percent of plants", "absolute", "2030", C, "CH4, N2O")
t("HON-01", "p.32", "printed p.31", "NDC", "Waste", "90 percent of wastewater treatment plants diagnosed and compliant by 2035",
  "alcanzando el 90% para 2035", "share of plants", "90", "percent of plants", "absolute", "2035", C, "CH4, N2O")
t("HON-01", "p.11", "printed p.10", "NDC", "Energy", "Reference: energy sector emissions in 2022 from the BTR1 inventory (50 percent of the total)",
  "sector Energía fue el mayor emisor", "inventory emissions", "10880", "Gg CO2e", "inventory 2022", "2022", "not stated", G21,
  note="Inventory value used to check the model level; not a target.")
t("HON-01", "p.11", "printed p.10", "NDC", "economy-wide", "Reference: national emissions excluding LULUCF in 2022 (BTR1 inventory)",
  "excluyendo ... (UTCUTS), sumaron", "inventory emissions", "21795", "Gg CO2e", "inventory 2022", "2022", "not stated", G21,
  note="Net emissions including LULUCF were 18,650 Gg CO2e (same page). Not a target.")

# HON-02 second update (April 2025)
t("HON-02", "p.3;p.11", "Cuadro 3 item 3.a (p.11)", "NDC", "economy-wide",
  "16 percent below the 2030 BAU of 28,945 Gg CO2e for energy, IPPU, agriculture and waste (4,631.2 Gg) (superseded by HON-01)",
  "reducir en un 16% las emisiones de 28,945 Gg CO2-eq proyectadas para 2030", "percent reduction against BAU", "16",
  "percent", "BAU (28,945 Gg CO2e excl. LULUCF)", "2030", C, G3,
  note="p.3 prints the absolute value as '4,631.2.20'; p.11 prints 4631.2.")
t("HON-02", "p.3;p.6;p.11", "Cuadro 3 (p.11)", "NDC", "LULUCF",
  "LULUCF target: 1 percent (214.3 Gg CO2e) of the difference between the old and new BAU in 2030 (superseded)",
  "reducir en un 1% ... 214.3 Gg CO2-eq", "emission reduction against BAU", "214.3", "Gg CO2e", "BAU", "2030", C, "CO2")
t("HON-02", "p.4;p.11", "Cuadro 3 (p.11)", "NDC", "economy-wide",
  "Total conditional reduction of 4,845.5 Gg CO2e in 2030 against the new net BAU of 50,381.3 Gg (superseded)",
  "Las emisiones se reducirán en 4845.5 Gg CO2-eq en el año 2030", "emission reduction against BAU", "4845.5",
  "Gg CO2e", "BAU (net, 50,381.3 Gg CO2e)", "2030", C, G3)
t("HON-02", "p.5", "figure on p.5", "NDC", "economy-wide",
  "Conditional mitigation level of 45,535.7 Gg CO2e net in 2030 (superseded)", "Meta de mitigación condicional",
  "net emissions", "45535.7", "Gg CO2e", "absolute (BAU 50,381.3)", "2030", C, G3)
t("HON-02", "p.3", "printed p.3", "NDC", "Energy",
  "Energy share of the 16 percent: 9 percent of the 2030 BAU (superseded)", "energía (9%)", "percent of national BAU",
  "9", "percent", "BAU (28,945 Gg CO2e)", "2030", C, G3,
  note="p.3 gives agriculture 5 and IPPU 1 percent; Cuadro 3 on p.11 swaps them (IPPU 5, agriculture 1). The 2021 update (HON-03 p.30) agrees with p.3.")

# HON-03 first update 2021
t("HON-03", "p.28;p.29", "contribution M1, printed p.20, p.21", "NDC", "economy-wide",
  "16 percent below BAU in 2030 for all sectors except LULUCF (BAU 28,945 Gg CO2e) (superseded)",
  "reducción de un 16% de las emisiones respecto al escenario BaU", "percent reduction against BAU", "16", "percent",
  "BAU (28,945 Gg CO2e)", "2030", C, G21, note="Conditional on international cooperation (p.10, p.26).")
for sec, v in [("Energy", "9"), ("Agriculture", "5"), ("IPPU", "1"), ("Waste", "1")]:
    t("HON-03", "p.30", "printed p.22", "NDC", sec, f"{sec} share of the 16 percent reduction: {v} percent (superseded)",
      f"{v}% sector", "percent of national BAU", v, "percent", "BAU (28,945 Gg CO2e)", "2030", C, G21)
t("HON-03", "p.33", "Tabla 2, printed p.25", "NDC", "Energy",
  "Energy mitigation scenario 1 chosen: energy emissions 20 percent below the energy BAU in 2030 (12,142 to 9,734 kt CO2e) (superseded)",
  "Escenario de mitigación 1", "percent reduction against energy BAU", "20", "percent",
  "energy BAU 2030 12,142 kt CO2e", "2030", C, G21, note="LEAP model (CAEP 2021). Scenarios 2 and 3 reach 23 and 30 percent.")
t("HON-03", "p.35", "contribution S1, printed p.27", "NDC", "LULUCF",
  "1.3 million ha of forest in functional restoration of the rural landscape by 2030", "1.3 millones de hectáreas",
  "area under restoration", "1.3", "million ha", "absolute", "2030", C, "CO2",
  note="1 million ha from the Bonn Challenge and first NDC plus 300,000 ha.")
t("HON-03", "p.42;p.43", "contribution S2, printed p.34, p.35", "NDC", "Energy",
  "Household firewood consumption 39 percent lower by 2030 against 2012 (13,936 kBEP residential in 2012)",
  "reducir en un 39% el consumo de leña en las familias", "firewood consumption of households", "39",
  "percent reduction", "2012 (13,936 kBEP)", "2030", C, "CH4, N2O")

# HON-04 INDC
t("HON-04", "p.2;p.3", "printed p.2, p.3", "NDC", "economy-wide",
  "15 percent below BAU in 2030 for energy, industrial processes, agriculture and waste (BAU 28,922 Gg CO2e) (superseded)",
  "Reducción de un 15% de las emisiones respecto al escenario BAU para el 2030", "percent reduction against BAU",
  "15", "percent", "BAU (28.922 Gg CO2e printed with a dot)", "2030", C, "CO2, CH4, N2O")
t("HON-04", "p.2", "printed p.2", "NDC", "LULUCF", "Afforestation or reforestation of 1 million ha before 2030 (sector goal)",
  "forestación/reforestación de 1 millón de hectáreas", "area", "1", "million ha", "absolute", "2030", "not stated", "CO2")
t("HON-04", "p.2", "printed p.2", "NDC", "Energy", "Household firewood consumption 39 percent lower through the efficient stoves NAMA",
  "reducir en un 39% el consumo de leña en las familias", "firewood consumption of households", "39", "percent reduction",
  "not stated", "2030", "not stated", "CH4, N2O")

# HON-05 BTR1
t("HON-05", "p.524", "printed p.523", "BTR", "Energy",
  "Prospectiva Energetica 2017-2038: renewables above 80 percent of electricity generation by 2038",
  "alcanzando más del 80% de la generación eléctrica para 2038", "renewable share of generation", "80", "percent",
  "absolute", "2038", "not stated", "CO2")
t("HON-05", "p.525", "printed p.524", "BTR", "IPPU", "HCFC consumption cut to 15 percent of its baseline by 2030 (Montreal Protocol)",
  "disminuir su consumo al 15% de su línea base para 2030", "HCFC consumption relative to baseline", "15",
  "percent of baseline", "Montreal baseline", "2030", "not stated", "HCFC",
  note="Table 3-6 (p.551, p.552) lists import maximums of 2.5 percent of baseline in 2030 and 0 in 2040.")
t("HON-05", "p.526", "printed p.525", "BTR", "IPPU", "HCFC fully eliminated from the market by 2040",
  "total eliminación del mercado para 2040", "HCFC consumption", "0", "percent of baseline", "Montreal baseline", "2040",
  "not stated", "HCFC")
t("HON-05", "p.526", "printed p.525", "BTR", "IPPU",
  "Kigali: HFC consumption frozen at the 2024-2026 average, 10 percent lower in 2029", "reducción del 10% en 2029",
  "HFC consumption reduction", "10", "percent", "average 2024-2026", "2029", "not stated", "HFC")
t("HON-05", "p.526", "printed p.525", "BTR", "IPPU", "Kigali: HFC consumption 80 percent lower in 2045",
  "del 80% para 2045", "HFC consumption reduction", "80", "percent", "average 2024-2026", "2045", "not stated", "HFC")
t("HON-05", "p.528", "printed p.527", "BTR", "Energy", "Efficient stoves NAMA: 800,000 stoves installed by 2026",
  "instalar entre 800,000 y 1,100,000 estufas", "stoves installed", "800000", "stoves", "absolute", "2026", "not stated", "CO2, CH4, N2O")
t("HON-05", "p.528", "printed p.527", "BTR", "Energy", "Efficient stoves NAMA: 1,100,000 stoves installed by 2030",
  "1,100,000 estufas", "stoves installed", "1100000", "stoves", "absolute", "2030", "not stated", "CO2, CH4, N2O")
t("HON-05", "p.529", "printed p.528", "BTR", "Transport",
  "NAMA for sustainable urban public transport: mitigation potential of 200,000 t CO2e per year from 2020",
  "200,000 toneladas de CO₂ equivalente por año", "annual emission reduction", "200000", "t CO2e per year", "BAU",
  "2020", "not stated", "CO2", note="Potential, from Ludeña et al. 2015; NAMA not advancing (HON-07 p.88).")
t("HON-05", "p.530", "printed p.529", "BTR", "Transport",
  "NAMA for efficiency of vehicles in operation: 150,000 to 200,000 t CO2e per year", "entre 150,000 y 200,000 toneladas",
  "annual emission reduction", "200000", "t CO2e per year", "BAU", "not stated", "not stated", "CO2",
  note="Upper end of the printed range; lower end 150,000. Fuel savings 60 to 70 million litres per year.")
t("HON-05", "p.532", "printed p.531", "BTR", "Agriculture",
  "Livestock NAMA scenario 1: better management on 30 percent of degraded pastures, 50.6 Mt CO2e cumulative over 14 years",
  "50.6 millones de t CO₂eq para el escenario 1", "cumulative emission reduction", "50.6", "Mt CO2e", "BAU",
  "not stated (14 years from 2023)", "not stated", "CO2, CH4, N2O", note="Scenario 2: 20 percent of degraded pastures, 29.3 Mt.")
t("HON-05", "p.552", "Tabla 3-6, printed p.551", "BTR", "IPPU",
  "Maximum HCFC-22 imports 2.5 percent of the baseline in 2030 (14,819.2 t CO2eq) and 0 in 2040", "Máximos de importación permitidos",
  "HCFC-22 import maximum", "14819.2", "t CO2eq", "baseline (2013 = 100)", "2030", "not stated", "HCFC")
t("HON-05", "p.572", "Tabla 3-8, printed p.571", "BTR", "Waste",
  "Tegucigalpa landfill: recovery of 15 percent of organic waste by 2030", "meta de recuperación del 15 % de los residuos orgánicos a 2030",
  "organic waste recovery", "15", "percent", "absolute", "2030", "not stated", "CH4")

# HON-07 BUR2
t("HON-07", "p.79", "printed p.79", "BUR", "Energy",
  "Industrial energy efficiency: energy consumption 1 to 4 percent below BAU in 2030", "reducción de entre 1% a 4% en el año 2030",
  "energy consumption reduction against BAU", "4", "percent", "BAU", "2030", "not stated", "CO2, CH4, N2O",
  note="Upper end of the range; lower end 1 percent.")
t("HON-07", "p.80", "printed p.80", "BUR", "Transport",
  "Electromobility action: low impact, below 50 kt CO2e per year by 2030, growing after 2030", "Bajo impacto <50 kt CO2-eq anualmente al 2030",
  "annual emission reduction", "50", "kt CO2e per year (upper bound)", "BAU", "2030", "not stated", "CO2, CH4, N2O")
t("HON-07", "p.82", "printed p.82", "BUR", "Waste",
  "Tegucigalpa landfill: average reduction of 110.67 Gg CO2e per year 2022-2030 (885.37 Gg cumulative), biogas power from 2032",
  "reducción promedio anual de 110,67 Gg CO2 eq", "annual emission reduction", "110.67", "Gg CO2e per year", "BAU",
  "2030", "not stated", "CH4, N2O", note="Printed with a decimal comma.")
t("HON-07", "p.83", "printed p.83", "BUR", "IPPU", "F-gas reduction: 4,448.56 Gg CO2e avoided cumulative 2020-2030",
  "emisiones evitadas acumuladas de 4.448,56 Gg de CO2 eq", "cumulative avoided emissions", "4448.56", "Gg CO2e", "BAU",
  "2030", "not stated", "HFC, HCFC", note="Printed with a dot for thousands and a decimal comma.")

# HON-08 PIEG 2026-2035
P = "sector plan"
t("HON-08", "p.83;p.94", "Figura 56 (Escenario de Expansion V = PIEG)", P, "Energy",
  "Renewable share of electricity supply 76 percent in 2030 in the selected expansion plan", "Porcentaje de renovabilidad",
  "renewable share of generation", "76", "percent", "absolute (plan result)", "2030", "not stated", "CO2",
  note="Indicative least-cost plan, not a policy target. 75 percent in 2031; maximum 76 percent (p.94).")
t("HON-08", "p.83", "Figura 56", P, "Energy", "Renewable share of electricity supply 71 percent in 2035 in the selected expansion plan",
  "Porcentaje de renovabilidad", "renewable share of generation", "71", "percent", "absolute (plan result)", "2035",
  "not stated", "CO2")
t("HON-08", "p.12;p.89;p.93", "Tabla 49 (Escenario V)", P, "Energy",
  "New renewable capacity of 1,796.24 MW in 2026-2035 (hybrid solar and wind counted at their renewable rating)",
  "1,796.24 de capacidad renovable", "new renewable capacity", "1796.24", "MW", "absolute", "2035", "not stated", "CO2")
t("HON-08", "p.12;p.89;p.93", "Tabla 49 (Escenario V)", P, "Energy",
  "New thermal capacity of 1,285 MW in 2026-2035 (natural gas, dual fuel, coal or petcoke)", "1,285 MW de capacidad térmica",
  "new thermal capacity", "1285", "MW", "absolute", "2035", "not stated", "CO2")
t("HON-08", "p.12;p.89;p.93", "Tabla 49 (Escenario V)", P, "Energy", "New stand-alone battery storage of 215 MW in 2026-2035",
  "215 MW en sistemas de almacenamiento", "new storage capacity", "215", "MW", "absolute", "2035", "not stated", "")
t("HON-08", "p.9;p.34;p.35", "Tabla 9, Figura 24", P, "Energy",
  "Retirement of about 1,342.62 MW of fossil plants in 2026-2035 (886.06 MW in 2029, 276.52 MW in 2030)",
  "se retiran alrededor de 1,342.62 MW", "retired capacity", "1342.62", "MW", "absolute", "2035", "not stated", "CO2",
  note="All retirements are bunker, diesel or coal/petcoke plants (Tabla 9); the 105 MW Becosa coal/petcoke plant leaves in January 2029.")
t("HON-08", "p.82", "Tabla 43 (Escenario V)", P, "Energy", "250 MW natural gas combined cycle turbine added in 2029",
  "Turbina de gas en ciclo combinado a gas natural", "new capacity", "250", "MW", "absolute", "2029", "not stated", "CO2",
  note="Plus natural gas engines of 100 MW in 2027, 2029, 2030, 2031 and 2032 and a 30 MW gas turbine in 2035.")
t("HON-08", "p.82", "Tabla 43 (Escenario V)", P, "Energy", "105 MW coal or petcoke steam turbine added in 2029",
  "Turbina de vapor a carbón/petcoke", "new capacity", "105", "MW", "absolute", "2029", "not stated", "CO2")
t("HON-08", "p.90;p.94", "Tabla 50 (Escenario V)", P, "Energy",
  "Power sector CO2 emissions 49 percent below the 2025 level in 2030", "reducción máxima del 49% para el 2030",
  "percent reduction against 2025", "49", "percent", "2025", "2030", "not stated", "CO2")
t("HON-08", "p.90;p.94", "Tabla 50 (Escenario V)", P, "Energy", "Power sector CO2 emissions 33 percent below the 2025 level in 2035",
  "disminución del 33% en 2035", "percent reduction against 2025", "33", "percent", "2025", "2035", "not stated", "CO2")
t("HON-08", "p.90", "printed p.90", P, "Energy",
  "SEN estimate: each energy subsector must cut its emissions by 20 percent towards 2030 to meet the NDC (power is 51.2 percent of energy emissions)",
  "debe reducir en un 20% sus emisiones hacia el 2030", "percent reduction", "20", "percent", "not stated (BAU implied)",
  "2030", "not stated", "CO2")
t("HON-08", "p.54", "Tabla 25", P, "Energy", "Projected electricity demand 15,455.28 GWh in 2030 (medium projection)",
  "Demanda anual de energía", "electricity demand", "15455.28", "GWh", "absolute (projection)", "2030", "not stated", "",
  note="Projection used by the plan, not a target. 18,108.55 GWh in 2035 (next row).")
t("HON-08", "p.54", "Tabla 25", P, "Energy", "Projected electricity demand 18,108.55 GWh in 2035 (medium projection)",
  "Demanda anual de energía", "electricity demand", "18108.55", "GWh", "absolute (projection)", "2035", "not stated", "")

for i, r in enumerate(T, start=1):
    r[0] = f"HON-T{i:03d}"
write(os.path.join(JOB, "targets_HON.csv"), TH, T)

# ------------------------------------------------------------------ projections
PH = ["source_id", "page", "table_or_figure", "scenario_as_named", "sector", "gas", "unit", "year", "value", "note"]
PR = []
cols = [("Agriculture", "agriculture"), ("Energy", "energy"), ("IPPU", "IPPU"), ("Waste", "waste"),
        ("LULUCF emissions", "LULUCF"), ("LULUCF removals", "LULUCF"), ("LULUCF net", "LULUCF"),
        ("economy-wide (net)", "total")]
parsed_years = []
with open(os.path.join(D, "text", "HON-01", "p24.txt"), encoding="utf-8") as fh:
    for line in fh:
        m = re.match(r"^(20[23]\d)\s+(.*)$", line.strip())
        if not m:
            continue
        y = int(m.group(1))
        if y < 2021:
            continue
        vals = m.group(2).split()
        if len(vals) != 8:
            continue  # the caption line '2030 y 2035'
        parsed_years.append(y)
        for (sec, _), v in zip(cols, vals):
            neg = v.startswith("(")
            num = float(v.strip("()").replace(",", ""))
            note = "Linear projection of the 2011-2020 inventory; values printed as integers"
            if neg:
                note += "; printed in parentheses (a removal), value given as a positive magnitude"
            PR.append(["HON-01", "p.24", "Tabla 2 (printed p.23)", "Escenario Tendencial (BAU)", sec, "CO2e (AR5)",
                       "Gg CO2e (removal)" if neg else "Gg CO2e", y, f"{num:g}", note])
assert parsed_years == list(range(2021, 2036)), parsed_years
PR.append(["HON-01", "p.25", "printed p.24", "Nivel maximo de emisiones esperadas (mitigation)", "economy-wide (net)",
           "CO2e (AR5)", "Gg CO2e", 2030, "41816.4", ""])
PR.append(["HON-01", "p.25", "printed p.24", "Nivel maximo de emisiones esperadas (mitigation)", "economy-wide (net)",
           "CO2e (AR5)", "Gg CO2e", 2035, "52769", ""])
traj = {2021: "22957.6", 2022: "26004.6", 2023: "29051.7", 2024: "32098.8", 2025: "35145.9", 2026: "38192.9",
        2027: "41240.0", 2028: "44287.1", 2029: "47334.2", 2030: "50381.3"}
for y, v in traj.items():
    PR.append(["HON-02", "p.5", "figure and table on p.5", "Trayectoria indicativa (BAU)", "economy-wide (net)",
               "CO2e (AR5)", "Gg CO2e", y, v, "Superseded by HON-01 Tabla 2 (same values rounded)"])
PR.append(["HON-02", "p.5", "figure on p.5", "Meta de mitigacion condicional", "economy-wide (net)", "CO2e (AR5)",
           "Gg CO2e", 2030, "45535.7", ""])
for name, v in [("BAU", "12142"), ("Escenario de mitigacion 1", "9734"), ("Escenario de mitigacion 2", "9355"),
                ("Escenario de mitigacion 3", "8545")]:
    PR.append(["HON-03", "p.33", "Tabla 2 (printed p.25)", name, "energy", "CO2e (AR5)", "kt CO2e", 2030, v,
               "LEAP model (CAEP 2021); scenario 1 chosen for the NDC"])
for y, v in [(2012, "18915"), (2020, "22027"), (2030, "28922")]:
    PR.append(["HON-04", "p.3", "printed p.3", "Escenario BAU", "economy-wide excl. LULUCF", "CO2, CH4, N2O (SAR GWP)",
               "Gg CO2e", y, v, "Printed with a dot as thousands separator (e.g. 28.922)"])
PR.append(["HON-07", "p.86;p.87", "NAMA ganaderia table", "BAU (NAMA ganaderia)", "agriculture (livestock, net)",
           "CO2, CH4, N2O", "t CO2e per year", 2030, "10100000", "Net emissions of the livestock sector without intervention"])
t50 = {2026: "10", 2027: "18", 2028: "29", 2029: "40", 2030: "49", 2031: "46", 2032: "39", 2033: "28", 2034: "24",
       2035: "33"}
for y, v in t50.items():
    PR.append(["HON-08", "p.90", "Tabla 50", "Escenario de Expansion V (PIEG 2026-2035)", "electricity generation", "CO2",
               "percent reduction against 2025", y, v, "Reduction of power sector CO2 relative to the 2025 simulation year"])
write(os.path.join(JOB, "projections_HON.csv"), PH, PR)
