"""Write search_log_ECU.csv: one row per attempt per fuel.

Usage: py -I build_search_log_ECU.py <out_csv>
"""
import csv
import sys

out = sys.argv[1]
D = "2026-11-09"
ALL = ["COA", "COK", "NGS", "FOI", "DSL", "GSL", "LPG", "KER", "JET", "CRU"]
EPP_IE = "https://www.eppetroecuador.ec/wp-content/uploads/downloads/2025/01/INFORME-ESTADISTICO-MENSUAL-DICIEMBRE-2024-Act..pdf"
STRUCT = "https://www.eppetroecuador.ec/wp-content/uploads/downloads/2024/<MM>/ESTRUCTURA-DE-PRECIOS-<MES>-2024.pdf (13 files Dec 2023 to Dec 2024; Dec 2024 under /wp-content/uploads/2024/12/)"
rows = []


def log(fuels, lead_id, lead, url, result, detail):
    if isinstance(fuels, dict):
        for f, (res, det) in fuels.items():
            rows.append(["Ecuador", f, lead_id, lead, url, D, res, det])
    else:
        for f in fuels:
            rows.append(["Ecuador", f, lead_id, lead, url, D, result, detail])


# petroecuador
log({"CRU": ("value found", "p.55 crude export FOB 2024 total 68.56 USD/bbl (Oriente 71.10, Napo 64.85); no refinery transfer price in the report"),
     "NGS": ("value found", "p.51 and p.53 natural gas dispatches 5,773,789 MMBTU valued at 20,061,024.56 USD incl VAT (electric sector 99.7 percent); LNG to industry 1,151,820 MMBTU"),
     "FOI": ("value found", "p.57 Fuel Oil No. 6 export 6,253,273 bbl at 61.68 USD/bbl FOB; p.51/p.53 fuel oil No. 4 and residuo dispatched to the electric sector with values; p.63 no fuel oil imports"),
     "DSL": ("value found", "p.61 and p.63 Diesel 2 and Diesel Premium imports, DPU basis, 105.19 and 105.29 USD/bbl; margins not in this report"),
     "GSL": ("value found", "p.63 Nafta RON 95 and RON 80 imports, DPU basis, 110.34 and 96.93 USD/bbl"),
     "LPG": ("value found", "p.59 GLP imports 1,302,283 t at 556.59 USD/t, DPU basis"),
     "JET": ("value found", "p.62 Jet A-1 imports 453,513 bbl at 131.72 USD/bbl (7 months)"),
     "KER": ("value found", "p.51/p.53 Diesel 1 (kerosene) dispatches 8,856 bbl valued 1,033,502.16 USD incl VAT; used as check only"),
     "COA": ("no value", "EP Petroecuador does not trade coal"),
     "COK": ("no value", "EP Petroecuador does not import petroleum coke; no coke figures")},
    "petroecuador", "EP Petroecuador Informe Estadistico enero-diciembre 2024", EPP_IE, "", "")
log({f: ("value found", "monthly terminal prices incl VAT by sector (industrial, automotive, electric, aviation); day-weighted 2024 means in structures_2024.py") for f in ["DSL", "GSL", "LPG", "JET", "KER", "FOI", "NGS"]} |
    {"COA": ("no value", "coal not in the price structures"), "COK": ("no value", "petroleum coke not in the price structures"),
     "CRU": ("no value", "crude not sold at terminal; no transfer price")},
    "petroecuador", "EP Petroecuador monthly price structures (precios de venta en terminal para comercializadoras) 2024", STRUCT, "", "")
log(ALL, "petroecuador", "EP Petroecuador Precios de venta combustibles page", "https://www.eppetroecuador.ec/?p=8062", "no value",
    "page shows only the current (July 2026) structure; 2024 files found by their upload paths instead")
log({"NGS": ("no value", "Nota 28 cost of natural gas sales 22,287 thousand USD (cost, not a price)"),
     "CRU": ("no value", "no valuation of crude delivered to refineries; Nota 27 export revenue only")},
    "petroecuador", "EP Petroecuador financial statements 2024", "https://www.eppetroecuador.ec/wp-content/uploads/2026/08/EEFF-2024-signed-signed-signed-signed-signed-signed-signed.pdf", "", "")
log(["CRU"], "petroecuador", "Web search for a published refinery crude transfer price", "query: EP Petroecuador precio crudo entregado a refinerias valoracion carga refineria Esmeraldas 2024", "not found",
    "no published transfer or refinery acquisition price; press items only")
# arcernnr
log(ALL, "arcernnr", "ARCERNNR website (controlrecursosyenergia.gob.ec)", "https://www.controlrecursosyenergia.gob.ec/", "not found",
    "https: TLS certificate name mismatch (curl error 60); http: returns a hosting control panel default page; agency functions split into ARCONEL (electricity) and ARCH (hydrocarbons)")
log({"DSL": ("value found", "Art. 1 diesel automotive terminal 1.434171 and electric 0.804200 USD/gal excl VAT; Art. 4 margin 0.128438 USD/gal"),
     "GSL": ("value found", "Art. 1 Extra terminal 1.983166 USD/gal; Art. 4 margin 0.160313 USD/gal (April-June 2024 text)"),
     "LPG": ("value found", "Art. 8 domestic 0.095652 USD/kg; Art. 10 taxis and drying 0.168261 USD/kg plus margin 0.13 USD/kg"),
     "FOI": ("value found", "Art. 1 fuel oil 4 electric 0.48 (La Libertad) and 0.62 USD/gal excl VAT"),
     "NGS": ("no value", "Art. 12-13 amend Art. 11-A gas prices (1.786087 USD/MMBTU excl VAT for literal a; 0.50 for household pipeline gas from Amistad); the base article naming the use of literal a was not retrievable, so not used"),
     "JET": ("no value", "Art. 7 only a floor of 1.25 USD/gal on the jet fuel terminal price"),
     "KER": ("no value", "no Diesel 1 or kerosene price in the decree"),
     "COA": ("no value", "not covered"), "COK": ("no value", "not covered"), "CRU": ("no value", "not covered")},
    "arcernnr", "Decreto Ejecutivo 215 (Registro Oficial Segundo Suplemento 529, 1 April 2024), reforms to the fuel price regulation drafted with ARCERNNR",
    "https://www.congope.gob.ec/wp-content/uploads/2024/12/Reforma-regulacion-precios-hidrocarburos.pdf", "", "")
log(["DSL", "GSL", "LPG", "FOI", "NGS", "JET", "KER"], "arcernnr", "Decreto Ejecutivo 308 Reglamento Codificado de Regulacion de Precios de Derivados de Hidrocarburos (Registro Oficial Segundo Suplemento 589, 28 June 2024)",
    "https://www.registroficial.gob.ec/segundo-suplemento-al-registro-oficial-no-589/", "not found",
    "index page lists Decreto 308 but has no PDF link; registroficial wp-json search returns HTTP 401; on manual list")
log(["NGS", "FOI", "DSL"], "arcernnr", "Reglamento sustitutivo de regulacion de precios de derivados (Decreto 338 codified) on gob.ec",
    "https://www.gob.ec/sites/default/files/regulations/2018-10/Documento_REGLAMENTO-REGULACI%C3%93N-PRECIOS-DERIVADOS-PETR%C3%93LEO.pdf", "blocked HTTP 000",
    "connection reset by server (curl error 56) on three attempts; on manual list")
log(["NGS", "FOI", "DSL"], "arcernnr", "ARCONEL Estadistica Anual y Multianual del Sector Electrico 2024", "https://arconel.gob.ec/wp-content/uploads/downloads/2025/04/Estadistica2024_abr.pdf", "no value",
    "fuel consumption for generation in physical units and kTEP only (Tablas 55-57); no fuel prices")
log(["NGS", "FOI", "DSL"], "arcernnr", "ARCONEL Informe INF-DTRET-2024-043 costo del servicio publico 2025", "http://arconel.gob.ec/wp-content/uploads/downloads/2024/12/2.-Informe-Nro.-INF-DTRET-2024-043_Certificada.pdf", "no value",
    "states that thermal variable costs use fuel prices fixed by executive decree; no unit prices tabulated")
log(["DSL", "GSL", "LPG", "KER", "JET"], "arcernnr", "Web search for ARCH/ARCERNNR monthly price notices with terminal prices and margins", "query: Agencia de Regulacion y Control de Hidrocarburos ARCH precios de combustibles terminal venta al publico 2024", "not found",
    "no official ARCH site or file located; press reports only")
# mem_cenace
log(ALL, "mem_cenace", "CENACE Informe Anual 2024 parts 1-3", "https://www.cenace.gob.ec/wp-content/plugins/download-monitor/download.php?id=4755&force=1 (also id=4754, 4756)", "no value",
    "generation by fuel and aggregate fuel payments to Petroecuador (14.33 percent of prelaciones, part 2 p.30); no fuel prices or unit variable costs")
log(["NGS", "FOI", "DSL"], "mem_cenace", "CENACE SIMEM portal (consulta CVP, variable costs and fuel cost by unit)", "https://simem.cenace.gob.ec/pmis-web", "login required",
    "requires a market participant digital certificate")
log(["NGS", "FOI", "DSL"], "mem_cenace", "CENACE informacion operativa and informacion comercial pages", "http://www.cenace.gob.ec/info-operativa/InformacionOperativa.htm", "no value",
    "dashboard pages without fuel prices or downloadable cost files")
log(["NGS"], "mem_cenace", "Web search for the natural gas price to Termogas Machala (Ministerio, CELEC, Petroecuador)", "query: precio gas natural Termogas Machala CELEC Petroecuador 2024 USD millon BTU", "no value",
    "press only (subsidised 3.2 USD/MMBTU cited for 2023); not citable; the EP Petroecuador dispatch value was used instead")
log(ALL, "mem_cenace", "Ministerio de Ambiente y Energia, Balance Energetico Nacional 2024 (prices)", "https://www.ambienteyenergia.gob.ec/wp-content/uploads/2025/09/BEN_24_compressed-comprimido-1.pdf", "no value",
    "no fuel prices; used for conversion factors and for Diesel 1 = kerosene")
# energy_balance
log(ALL, "energy_balance", "Balance Energetico Nacional 2024 and its conversion factors", "https://www.ambienteyenergia.gob.ec/wp-content/uploads/2025/09/BEN_24_compressed-comprimido-1.pdf", "no value",
    "p.158 factors in BEP (OLADE 2017 manual cited); net or gross not stated; p.115 imports in kBEP (petroleum coke 1,081 kBEP; no coal); no prices")
log(["NGS", "COA", "COK", "FOI"], "energy_balance", "OLADE Energy Statistics Manual 2017 (basis of BEN factors)", "https://biblioteca.olade.org/opac-tmpl/Documentos/old0381.pdf", "blocked HTTP 403",
    "also old0382.pdf HTTP 403; on manual list")
# bce_senae
log({"CRU": ("value found", "rows 94-96 total crude exports 2024: 68.4534 USD/bbl; series 2018-2025"),
     "FOI": ("value found", "rows 120-121 Fuel oil No. 6 export 61.68 USD/bbl; series 2018-2025"),
     "DSL": ("value found", "rows 148-150 diesel imports 105.2611 USD/bbl (same as EP Petroecuador); series 2018-2025"),
     "GSL": ("value found", "rows 141-143 nafta imports 104.927 USD/bbl; series 2018-2025"),
     "LPG": ("value found", "rows 155-157 GLP imports 47.7757 USD/bbl; series 2018-2025"),
     "JET": ("no value", "row 80 other imports (Avgas, Jet, Cutter Stock) in volume only"),
     "KER": ("no value", "no kerosene or Diesel 1 series"), "NGS": ("no value", "no natural gas series"),
     "COA": ("no value", "no coal series"), "COK": ("no value", "no petroleum coke series")},
    "bce_senae", "BCE Cifras del Sector Petrolero (SerieCifrasPetroleras.xlsx)", "https://contenido.bce.fin.ec/documentos/Estadisticas/Hidrocarburos/SerieCifrasPetroleras.xlsx", "", "")
log({"COK": ("no value", "Anexo 1 subpartida 2713110000 petroleum coke FOB 21.6 million USD in 2024 (8.6, 2.4, 7.3, 3.3 by quarter); no quantity"),
     "FOI": ("no value", "Anexo 1 subpartida 2710192200 fueloils FOB 61.7 million USD in 2024 (private importers); no quantity"),
     "DSL": ("no value", "Anexo 1 subpartida 2710192131 diesel FOB values by quarter; no quantity"),
     "KER": ("no value", "Anexo 1 subpartida 2710192120 diesel 1 FOB 3.9 million USD in Q4 2024; no quantity"),
     "JET": ("no value", "not listed separately"), "GSL": ("no value", "FOB values by subpartida only"), "LPG": ("no value", "propane and butane FOB values only"),
     "COA": ("no value", "coal not in the petroleum annex"), "NGS": ("no value", "not listed"), "CRU": ("no value", "imports only")},
    "bce_senae", "BCE Boletin analitico trimestral de comercio exterior IV-2024, Anexo 1 importaciones petroleras por subpartida", "https://contenido.bce.fin.ec/documentos/Estadisticas/SectorExterno/ComercioExterior/informes/ResultCE_042024.pdf", "", "")
log(ALL, "bce_senae", "SENAE estadisticas page", "https://www.aduana.gob.ec/estadisticas/", "no value",
    "page has no downloadable statistics; customs data sit in the interactive portal (portal.aduana.gob.ec); on manual list for coal and petroleum coke")
# customs_national
log(["COA", "COK", "FOI", "DSL", "GSL", "LPG", "JET", "KER", "NGS", "CRU"], "customs_national", "National import statistics by HS (SENAE portal, BCE annexes)", "https://www.aduana.gob.ec/estadisticas/ ; https://contenido.bce.fin.ec/documentos/Estadisticas/SectorExterno/ComercioExterior/informes/ResultCE_042024.pdf", "no value",
    "no file with CIF value and quantity by HS code located; BCE annex gives FOB values without quantities")
# comtrade
log({"COA": ("value found", "2701 CIF 3,506,260.772 USD, netWgt 14,734,330 kg; 270111 anthracite 14,681,298 kg"),
     "COK": ("value found", "271311 CIF 30,287,760.08 USD, netWgt 245,618,130 kg, qty 315,051,290 kg"),
     "NGS": ("no value", "271111 LNG 92,171 kg only; 271121 no record; Ecuador gas is domestic"),
     "FOI": ("no value", "271019 mixes diesel, fuel oil and other medium and heavy oils (4,705,627,808 kg); no fuel oil split"),
     "DSL": ("no value", "271019 mixed code; EP Petroecuador figures used"),
     "GSL": ("no value", "271012 light oils 105,735,721 kg (private imports); EP Petroecuador naphtha figures used"),
     "LPG": ("no value", "271112 propane has no net weight; 271113 butanes 393,990,275 kg; mixed, EP Petroecuador figures used"),
     "JET": ("no value", "jet inside 271019 mixed code"), "KER": ("no value", "kerosene inside 271019 mixed code"),
     "CRU": ("no value", "2709 imports 959.58 kg only")},
    "comtrade", "UN Comtrade preview API, Ecuador imports 2024, 4 and 6 digit",
    "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=218&period=2024&partnerCode=0&flowCode=M&cmdCode=270111,270112,270119,270120,271311,271312,271320,271390,271012,271019,271111,271112,271113,271119,271121", "", "")
log({"CRU": ("value found", "2709 exports FOB 7,834,790,006.4 USD, netWgt 17,091,526,369 kg"),
     "FOI": ("no value", "271019 exports 1,895,447,783 kg FOB 835,078,833 USD mixes fuel oil No. 6 and other heavy oils")},
    "comtrade", "UN Comtrade preview API, Ecuador exports 2024", "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=218&period=2024&partnerCode=0&flowCode=X&cmdCode=2709,2710,271019,271012,2711,2713", "", "")
# others
log(["COA"], "other_ipcc", "IPCC 2006 Vol. 2 Table 1.2 anthracite NCV (Ecuador imports are anthracite)", "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf", "value found",
    "Anthracite 26.7 TJ/Gg net; recorded as ECU_IPCC_NCV_ANTHRACITE")
log(["DSL", "GSL", "FOI"], "other_lexis", "Lexis summary of Decreto 308 (secondary)", "https://www.lexis.com.ec/noticias/decreto-ejecutivo-no-308-se-emite-el-reglamento-codificado-de-regulacion-de-precios-de-derivados-de-hidrocarburos", "no value",
    "secondary summary repeating diesel margin 0.128438 and electric prices 0.8042, 0.48, 0.62 USD/gal; not cited; decree PDF linked only on a cloud drive")

with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["country", "fuel", "lead_id", "lead", "url_or_query", "date", "result", "detail"])
    w.writerows(rows)
print(len(rows), "rows")
