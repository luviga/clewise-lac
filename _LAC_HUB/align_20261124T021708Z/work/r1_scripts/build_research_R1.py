"""Builds work/research_R1.csv from values read in the downloaded files (R1 research job)."""
import csv, hashlib, os

ROOT = r"C:\clw_align\_LAC_HUB\align_20261124T021708Z"
DL = os.path.join(ROOT, "downloads", "R1")
OUT = os.path.join(ROOT, "work", "research_R1.csv")
RD = "2026-11-23"
COLS = ["topic", "country", "item", "value_printed", "unit_printed", "value_standard", "unit_standard", "year",
        "source_title", "publisher", "url", "retrieval_date", "local_file", "sha256", "page_or_table", "note"]


def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(DL, rel), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


rows = []


def add(**k):
    r = {c: "" for c in COLS}
    r.update(k)
    r["retrieval_date"] = RD
    if r["local_file"] and not r["sha256"]:
        r["sha256"] = sha(r["local_file"])
    rows.append(r)


# ---------------- A. social discount rates ----------------
THESIS = dict(source_title="Estimacion de la tasa de descuento empleada para la evaluacion costo-beneficio de proyectos con efectos medioambientales en Costa Rica (MSc thesis, J. Rivera Ugarte, Nov 2024)",
              publisher="Universidad Nacional (UNA), Costa Rica, CINPE",
              url="https://repositorio.una.ac.cr/bitstreams/19e556ba-0009-4d22-8f1b-9a7f9c1a0bd2/download",
              local_file="A_discount/CRI_UNA_thesis.pdf")
add(topic="A", country="CRI", item="Social discount rate (TSD) set by MIDEPLAN for public investment projects", value_printed="8,31%",
    unit_printed="%", value_standard="8.31", unit_standard="percent per year", year="2019", **THESIS,
    page_or_table="PDF p10 (Resumen ejecutivo, printed p. x); PDF p18 (printed p. 4): 'el valor de la TSD se actualizo en 2019, estableciendose un valor de 8,31% (Mideplan, ND)'",
    note="Secondary source citing MIDEPLAN (Ramsey method). Real vs nominal not stated in the source; treated as real. Primary MIDEPLAN (2019) 'Precios sociales: Guia para su aplicacion' not found online.")
add(topic="A", country="CRI", item="Social discount rate used by MIDEPLAN 2010 to 2019 (superseded)", value_printed="12%",
    unit_printed="%", value_standard="12", unit_standard="percent per year", year="2010-2019", **THESIS,
    page_or_table="PDF p17 (printed p. 3)", note="Historical value, cites Mideplan (2010) p. 53.")
add(topic="A", country="CRI", item="MIDEPLAN general methodology guide: TSD defined but no value printed", value_printed="", unit_printed="",
    value_standard="", unit_standard="", year="2024",
    source_title="Guia Metodologica General para la Identificacion, Formulacion y Evaluacion de Proyectos de Inversion Publica: Perfil del Proyecto (Julio 2024)",
    publisher="MIDEPLAN (copy hosted by PANI)",
    url="https://pani.go.cr/wp-content/uploads/2026/01/Guia-Metodologica-General-para-la-identificacion-formulacion-y-Evaluacion-de-proyectos-de-Inversion-Publica-Perfil-del-Proyecto.pdf",
    local_file="A_discount/CRI_guia_perfil_mideplan_pani.pdf", page_or_table="Section 3.3.1 (printed p. 100), footnote 38",
    note="Refers to MIDEPLAN 'Precios sociales: Guia para su aplicacion' (2019) for the TSD value; official primary value not retrieved.")
add(topic="A", country="HND", item="Social discount rate, DGIP Guia Metodologica General (2015), status 'Vigente'", value_printed="12%",
    unit_printed="%", value_standard="12", unit_standard="percent per year", year="2015", **THESIS,
    page_or_table="PDF p18 (printed p. 4), Tabla 1.1 (countries using 12%): 'Honduras, Direccion General de Inversiones Publicas (2015), 2015, Vigente'",
    note="Secondary source. Primary DGIP 2015 guide link on observatorioplanificacion.cepal.org returned 404. SEFIN Acuerdo 345-2025 (Normas Tecnicas de Inversion Publica) downloaded and checked: no discount rate value; it defers to the Guia Metodologica.")
add(topic="A", country="HND", item="Normas Tecnicas de Inversion Publica 2025: no discount rate printed", value_printed="", unit_printed="",
    value_standard="", unit_standard="", year="2025", source_title="Acuerdo 345-2025 Normas Tecnicas de Inversion Publica",
    publisher="Secretaria de Finanzas (SEFIN), Honduras",
    url="https://www.sefin.gob.hn/wp-content/uploads/2026/05/ACUERDO-345-2025-NORMAS-TECNICAS-DE-INVERSION-PUBLICA.pdf",
    local_file="A_discount/HND_Acuerdo_345_2025_Normas_Tecnicas.pdf", page_or_table="whole document searched (descuento, discount)",
    note="No value; refers to the Guia Metodologica de formulacion y evaluacion.")
add(topic="A", country="GTM", item="Social discount rate, SEGEPLAN, updated in 2022 (previously 12%, SEGEPLAN 2019)", value_printed="7%",
    unit_printed="%", value_standard="7", unit_standard="percent per year", year="2022", **THESIS,
    page_or_table="PDF p18 (printed p. 4), Tabla 1.1: 'Guatemala, Secretaria de Planificacion y Programacion de la Presidencia (2019), 2019, Se actualizo su valor en 2022 a 7%'",
    note="Secondary source only; SEGEPLAN primary not found. Conflict: IMF PIMA technical assistance report 2024 (TARSA2024021) reportedly says the social discount rate is not determined; that PDF could only be opened in a browser on imf.org (sha256 of PDF e50808c862a9f950ca10b36ad3013ddc5caae3a06ee421e598ac0a1600ea5491), text not checked.")
add(topic="A", country="GTM", item="Social discount rate, SEGEPLAN 2019 (superseded 2022 per same source)", value_printed="12%",
    unit_printed="%", value_standard="12", unit_standard="percent per year", year="2019", **THESIS,
    page_or_table="PDF p18 (printed p. 4), Tabla 1.1", note="Secondary source.")
add(topic="A", country="DOM", item="Social discount rate, MEPyD (2017), status 'Vigente'", value_printed="12%",
    unit_printed="%", value_standard="12", unit_standard="percent per year", year="2017", **THESIS,
    page_or_table="PDF p18 (printed p. 4), Tabla 1.1: 'Republica Dominicana, Ministerio de Economia, Planificacion y Desarrollo (2017), 2017, Vigente'",
    note="Secondary source. MEPyD 'Precios sociales Republica Dominicana 2022' (mepyd.gob.do) returned HTTP 403 / Cloudflare error 1009; it may hold an updated TSD. Check by hand.")
ECU = dict(source_title="The social discount rate in the evaluation of investment projects: an application for Ecuador (Zhangallimbay and Castillo), CEPAL Review No. 134, August 2021",
           publisher="ECLAC (CEPAL)", url="https://repositorio.cepal.org/server/api/core/bitstreams/f31ddfbe-bccb-49db-aa04-00f3d663314c/content",
           local_file="A_discount/ECU_CEPAL_tasa_social_descuento.pdf")
add(topic="A", country="ECU", item="Standard social discount rate applied by planning institutions (Ecuador)", value_printed="12%",
    unit_printed="%", value_standard="12", unit_standard="percent per year", year="2021", **ECU,
    page_or_table="PDF p1 (abstract) and PDF p2 (printed p. 76): 'In Ecuador, as in other Latin American countries, a fixed discount rate, usually of 12%, is used'",
    note="Secondary (peer-reviewed); official Secretaria Nacional de Planificacion document not retrieved. Real vs nominal not stated.")
add(topic="A", country="JAM", item="Social discount rate in Jamaica PIMS documents: none published", value_printed="", unit_printed="",
    value_standard="", unit_standard="", year="2016-2024", source_title="PIMS Guidelines 2016; Extract of PIMS Handbook with revised CRA methodology (15 Oct 2024); The Public Investment Management System (2022-10-28)",
    publisher="Ministry of Finance and the Public Service, Jamaica",
    url="https://www.mof.gov.jm/wp-content/uploads/PIMS-Guidelines-2016.pdf ; https://www.mof.gov.jm/wp-content/uploads/Extract-of-PIMS-Handbook-with-revised-CRA-Methodology-Oct.-15-2024.pdf ; https://www.mof.gov.jm/wp-content/uploads/PIMS-The-Public-Investment-Management-System-20221028.pdf",
    local_file="A_discount/JAM_PIMS_Guidelines_2016.pdf", page_or_table="whole documents searched for 'discount'",
    note="No discount rate in any of the three MoF documents (sha256 of handbook extract and 2022 PIMS file in the summary). Use the mean of the other countries.")

# ---------------- B. IMF fossil fuel subsidies 2023 ----------------
IMF = dict(source_title="IMF Energy Subsidy Template (This Version: January 2024), companion to 'IMF Fossil Fuel Subsidies Data: 2023 Update' (Black, Liu, Parry, Vernon), file externalfuelsubsidiestemplate2023new.xlsx",
           publisher="International Monetary Fund, Fiscal Affairs Department",
           url="https://www.imf.org/-/media/files/topics/energy-subsidies/externalfuelsubsidiestemplate2023new.xlsx",
           local_file="B_imf/extract_externalfuelsubsidiestemplate2023new_data_sheet.csv",
           sha256="13ab93f4a034d816106712e6eabb487d32f8dad732a177acc46a5b4432cdfcb3")
labels = {
    "mit.airpol.cost.gso.all.1": ("Gasoline, local air pollution, average", "real 2021 USD/liter"),
    "mit.acc.cost.gso.all.1": ("Gasoline accident damage", "real 2021 USD/liter"),
    "mit.con.cost.gso.all.1": ("Gasoline, congestion, average", "real 2021 USD/liter"),
    "mit.rdm.cost.gso.all.1": ("Gasoline, road damage, average", "real 2021 USD/liter"),
    "mit.scc.cost.gso.all.1": ("Gasoline, global warming cost, average", "real 2021 USD/liter"),
    "mit.airpol.cost.die.all.1": ("Diesel, local air pollution, average", "real 2021 USD/liter"),
    "mit.acc.cost.die.all.1": ("Diesel accident damage", "real 2021 USD/liter"),
    "mit.con.cost.die.all.1": ("Diesel, congestion, average", "real 2021 USD/liter"),
    "mit.rdm.cost.die.all.1": ("Diesel, road damage, average", "real 2021 USD/liter"),
    "mit.scc.cost.die.all.1": ("Diesel, global warming cost, average", "real 2021 USD/liter"),
    "mit.airpol.cost.lpg.all.1": ("LPG, local air pollution, average", "real 2021 USD/liter"),
    "mit.scc.cost.lpg.all.1": ("LPG, global warming cost, average", "real 2021 USD/liter"),
    "mit.airpol.cost.ker.all.1": ("Kerosene, local air pollution, average", "real 2021 USD/liter"),
    "mit.scc.cost.ker.all.1": ("Kerosene, global warming cost, average", "real 2021 USD/liter"),
    "mit.airpol.cost.coa.pow.1": ("Coal, local air pollution, electricity", "real 2021 USD/GJ"),
    "mit.scc.cost.coa.pow.1": ("Coal, global warming cost, electricity", "real 2021 USD/GJ"),
    "mit.airpol.cost.coa.tot.1": ("Coal, local air pollution, average", "real 2021 USD/GJ"),
    "mit.airpol.cost.nga.pow.1": ("Natural gas, local air pollution, electricity", "real 2021 USD/GJ"),
    "mit.scc.cost.nga.pow.1": ("Natural gas, global warming cost, electricity", "real 2021 USD/GJ"),
    "mit.airpol.cost.nga.ind.1": ("Natural gas, local air pollution, industry", "real 2021 USD/GJ"),
    "mit.airpol.cost.nga.tot.1": ("Natural gas, local air pollution, average", "real 2021 USD/GJ"),
}
with open(os.path.join(DL, IMF["local_file"]), encoding="utf-8") as f:
    lines = f.read().splitlines()
hi = next(i for i, l in enumerate(lines) if l.startswith("cc,year,row,"))
hdr = lines[hi].split(",")
for l in lines[hi + 1:]:
    if not l.strip():
        continue
    v = l.split(",")
    cc, yr, rown = v[0], v[1], v[2]
    for j, h in enumerate(hdr[3:], start=3):
        var, colL = h.split("[")
        colL = colL.rstrip("]")
        if var not in labels:
            continue
        lab, unit = labels[var]
        std = f"{float(v[j]):.6g}"
        note = "Scenario U1 (U5 identical). 2022 is the latest estimate year; 2030 is the latest (projected) year in the file." if yr == "2030" else "Scenario U1 (U5 identical). 2022: latest non-projected year (file runs 2015-2030)."
        note += " sha256 is of the original 16,305,319-byte xlsx (computed in a browser on imf.org; scripted download gets HTTP 403); local_file is a row extract of that xlsx."
        if cc == "HND" and var in ("mit.acc.cost.die.all.1", "mit.con.cost.die.all.1", "mit.rdm.cost.die.all.1"):
            note += " Value is 0 in the file for Honduras diesel driving externalities."
        add(topic="B", country={"CRI": "CRI", "DOM": "DOM", "ECU": "ECU", "GTM": "GTM", "HND": "HND", "JAM": "JAM"}[cc],
            item=f"{lab} ({var})", value_printed=v[j], unit_printed=unit, value_standard=std,
            unit_standard=unit.replace("real 2021 USD/liter", "USD2021 per litre").replace("real 2021 USD/GJ", "USD2021 per GJ"),
            year=yr, page_or_table=f"sheet 'data', cell {colL}{rown}", note=note, **IMF)

# ---------------- C. IPCC 2006 Table 2.2 ----------------
IPCC = dict(source_title="2006 IPCC Guidelines for National Greenhouse Gas Inventories, Vol. 2 Energy, Ch. 2 Stationary Combustion, Table 2.2 Default emission factors for stationary combustion in the energy industries (kg of greenhouse gas per TJ on a Net Calorific Basis)",
            publisher="IPCC / IGES", url="https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_2_Ch2_Stationary_Combustion.pdf",
            local_file="C_ipcc/V2_2_Ch2_Stationary_Combustion.pdf")
ef = [  # fuel, CO2, CH4, N2O, pdf page
    ("Crude Oil", "73 300", "r 3", "0.6", 16), ("Gas/Diesel Oil", "74 100", "r 3", "0.6", 16),
    ("Residual Fuel Oil", "77 400", "r 3", "0.6", 16), ("Liquefied Petroleum Gases", "63 100", "r 1", "0.1", 16),
    ("Petroleum Coke", "r 97 500", "r 3", "0.6", 16), ("Other Bituminous Coal", "94 600", "1", "r 1. 5", 16),
    ("Sub-Bituminous Coal", "96 100", "1", "r 1.5", 16), ("Natural Gas", "56 100", "1", "0.1", 16),
    ("Other Primary Solid Biomass", "n 100 000", "30", "4", 17), ("Landfill Gas", "n 54 600", "r 1", "0.1", 17),
    ("Sludge Gas", "n 54 600", "r 1", "0.1", 17), ("Other Biogas", "n 54 600", "r 1", "0.1", 17),
]
for fuel, co2, ch4, n2o, pg in ef:
    for gas, val in (("CO2", co2), ("CH4", ch4), ("N2O", n2o)):
        std = val.replace("r ", "").replace("n ", "").replace(" ", "")
        note = "Default value; 'r' = revised since 1996 Guidelines, 'n' = new. "
        if fuel in ("Other Primary Solid Biomass", "Landfill Gas", "Sludge Gas", "Other Biogas") and gas == "CO2":
            note += "Biomass CO2 is reported as an information item, not in national totals. "
        if fuel == "Other Primary Solid Biomass":
            note += "Bagasse is not listed separately in Table 2.2; it falls under Other Primary Solid Biomass. "
        add(topic="C", country="ALL", item=f"{fuel}, {gas} default emission factor, energy industries", value_printed=val,
            unit_printed="kg of greenhouse gas per TJ on a Net Calorific Basis", value_standard=std, unit_standard="kg/TJ (NCV)",
            year="2006", page_or_table=f"Table 2.2, PDF page {pg} of chapter file (printed p. 2.{pg})", note=note.strip(), **IPCC)

# ---------------- D. interconnections and trade ----------------
EORMX = dict(source_title="Estudio de seguridad operativa: Limites de transferencia de potencia desde el Sistema Electrico de Mexico hacia el Sistema Electrico Regional, epoca humeda (junio a noviembre de 2021), 28 May 2021",
             publisher="Ente Operador Regional (EOR), published by CND Panama", url="https://www.cnd.com.pa/images/avisos/083-Anexo_I-.pdf",
             local_file="D_interconnect/CND_083_Anexo_I.pdf")
add(topic="D", country="GTM", item="Mexico-SER (Tapachula-Los Brillantes 400 kV) transfer limit, max, medium and min demand", value_printed="240",
    unit_printed="Limite de Transferencia (MW)", value_standard="240", unit_standard="MW", year="2021", **EORMX,
    page_or_table="PDF p20, section 4.0 and 5.0.A table", note="Import direction Mexico to SER. Wet season Jun-Nov 2021.")
add(topic="D", country="GTM", item="Los Brillantes 400/230 kV transformers: continuous thermal limit per bank (two banks in parallel)", value_printed="247.5",
    unit_printed="MVA", value_standard="247.5", unit_standard="MVA", year="2019", **EORMX,
    page_or_table="PDF p3", note="Per AMM note GMEI-038-2019; replaced 225 MVA.")
add(topic="D", country="GTM", item="Mexico-SER under-voltage transfer trip scheme threshold", value_printed="300 MW",
    unit_printed="MW", value_standard="300", unit_standard="MW", year="2021", **EORMX,
    page_or_table="PDF p4", note="Trip when Mexico-SER transfer exceeds 300 MW and Tapachula voltage <= 0.97 p.u.")
EOR = dict(source_title="Estudio de Maximas Capacidades de Transferencia de Potencia entre areas de control del SER, Noviembre 2025, Resultados finales (30 Oct 2025)",
           publisher="Ente Operador Regional (EOR), published by CND Panama",
           url="https://cnd.com.pa/images/doc/doc_mer/153-Anexo_I_Informe_Estudio_MCTP_Noviembre_2025.pdf",
           local_file="D_interconnect/EOR_MCTP_Noviembre_2025_Anexo_I.pdf")
mctp = [("GTM", "GUA 02 Guatemala export to Honduras", "300 300 300 300", "300", 29),
        ("GTM", "GUA 03 Guatemala simultaneous export to El Salvador + Honduras", "300 300 300 300", "300", 29),
        ("GTM", "GUA 04 Guatemala import from Honduras", "300 300 300 300", "300", 29),
        ("GTM", "GUA 06 Guatemala import from El Salvador", "300 300 300 300", "300", 29),
        ("GTM", "GUA 01 Guatemala export to El Salvador", "300 300 300 300", "300", 29),
        ("HND", "HON 15 Honduras import South-North", "260 140 250 140", "140", 30),
        ("HND", "HON 18 Honduras export North-South", "250 290 260 250", "250", 30),
        ("HND", "HON 19 Honduras import from El Salvador", "300 280 300 280", "280", 30),
        ("HND", "HON 20 Honduras export to El Salvador", "300 300 300 300", "300", 30),
        ("HND", "HON 21 Honduras import from Guatemala", "300 280 300 280", "280", 30),
        ("HND", "HON 22 Honduras export to Guatemala", "300 300 300 300", "300", 30)]
for cc, it, vp, vs, pg in mctp:
    add(topic="D", country=cc, item=f"SIEPAC maximum transfer capacity (MCTP), {it}; most restrictive value", value_printed=vp,
        unit_printed="MW (MAX MED MIN, most restrictive)", value_standard=vs, unit_standard="MW", year="2025", **EOR,
        page_or_table=f"Tabla 12, PDF p{pg} (raw text order)", note="Values for transmission rights for November 2025; N-1 criterion.")
CNEE = dict(source_title="Compendio Estadistico 2024 (data 2019-2023, based on AMM reports)",
            publisher="Comision Nacional de Energia Electrica (CNEE), Guatemala",
            url="https://cnee.gob.gt/xhtml/informacion/Docs/Compendio_Estadistico_2024.pdf",
            local_file="D_interconnect/GTM_CNEE_Compendio_Estadistico_2024.pdf")
imp = {"2019": "1,113", "2020": "1,008", "2021": "1,141", "2022": "1,413", "2023": "1,900"}
exp = {"2019": "2,169", "2020": "1,063", "2021": "1,116", "2022": "1,035", "2023": "1,053"}
for y in imp:
    add(topic="D", country="GTM", item="Electricity imported, total (Energia importada total)", value_printed=imp[y], unit_printed="GWh",
        value_standard=imp[y].replace(",", ""), unit_standard="GWh", year=y, **CNEE,
        page_or_table="PDF p12, section 1.2.1 Datos Generales y Resumen de Indicadores", note="Mexico + MER combined. CNEE table built from AMM reports.")
    add(topic="D", country="GTM", item="Electricity exported, total (Energia exportada total)", value_printed=exp[y], unit_printed="GWh",
        value_standard=exp[y].replace(",", ""), unit_standard="GWh", year=y, **CNEE,
        page_or_table="PDF p12, section 1.2.1 Datos Generales y Resumen de Indicadores", note="Mexico + MER combined.")
add(topic="D", country="GTM", item="Electricity exported 2023 (text figure)", value_printed="1,052.93", unit_printed="GWh", value_standard="1052.93",
    unit_standard="GWh", year="2023", **CNEE, page_or_table="PDF p13", note="Same quantity as table on p12, more decimals.")
add(topic="D", country="GTM", item="Spot (oportunidad) imports from Mexico", value_printed="726", unit_printed="GWh", value_standard="726",
    unit_standard="GWh", year="2023", **CNEE, page_or_table="PDF p22, section 1.3.2", note="2019 value printed as 'aproximadamente 6 GWh'. 2023 spot exports to Mexico: 6 GWh. 2019 exports to Mexico: 414.5 GWh.")
add(topic="D", country="GTM", item="Firm contract import from Mexico (Energia del Caribe, S.A.)", value_printed="120 MW", unit_printed="MW", value_standard="120",
    unit_standard="MW", year="2023", **CNEE, page_or_table="PDF p22, section 1.3.2", note="Only firm contract on the Mexico link.")

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows ->", OUT)
for rel in ["A_discount/JAM_PIMS_Handbook_extract_2024.pdf", "A_discount/JAM_PIMS_20221028.pdf", "B_imf/dsd_ffs.json"]:
    print(rel, sha(rel))
