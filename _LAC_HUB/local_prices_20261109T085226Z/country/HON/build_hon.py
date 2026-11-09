"""Assemble the Honduras (HON) outputs of job LAC_LOCAL_PRICES 20261109T085226Z.

Usage: py -I build_hon.py <downloads_HON_dir> <out_dir>
Reads the parsed CCHAC weekly tables in <downloads_HON_dir>/cchac and the Comtrade JSON
responses, and writes prices_HON.csv, history_HON.csv, sources_HON.csv, constants_HON.csv,
search_log_HON.csv, manual_HON.csv and calorific_HON.csv to <out_dir>.
Every other number is typed in below from the cited document (page or table in the rows).
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

DL = Path(sys.argv[1])
OUT = Path(sys.argv[2])
TODAY = "2026-11-09"

# ---------------------------------------------------------------- shared constants
L_PER_USGAL = 3.785411784
USGAL_PER_BBL = 42.0
GJ_PER_MMBTU = 1.055056
UN_GAL = {"GSL": 357, "DSL": 304, "KER": 326, "FOI": 278, "LPG": 489, "JET": 326}
NCV = {"GSL": 44.3, "DSL": 43.0, "KER": 43.8, "FOI": 40.4, "LPG": 47.3, "COK": 32.5,
       "COA_OTHER_BITUMINOUS": 25.8}

# ---------------------------------------------------------------- HON constants
HON_FX_2024 = 24.7950          # BCH daily Compra mean 2024 (fx_bch.py)
HON_KG_PER_LB = 0.4535924      # NIST SP 811 Appendix B.9
HON_KG_PER_CYL25 = 25 * HON_KG_PER_LB
HON_GJ_PER_CYL25 = HON_KG_PER_CYL25 / 1000 * NCV["LPG"]


def per_bbl_to_gj(v, f):
    """USD/bbl -> USD/GJ: x (UN gal/t / 42 gal/bbl) bbl/t / NCV GJ/t."""
    return v * (UN_GAL[f] / USGAL_PER_BBL) / NCV[f]


def per_gal_to_gj(v, f):
    return v * UN_GAL[f] / NCV[f]


HEAD = ["country", "fuel", "model_code", "price_point", "year", "fob", "freight", "insurance", "port",
        "importer_terminal_margin", "wholesale_margin", "inland_freight", "retail_margin",
        "price_as_published", "currency", "unit", "period", "months_covered", "tax_treatment",
        "calorific_basis", "exchange_rate", "exchange_rate_constant", "conversion_constants",
        "value_usd_per_gj", "evidence_class", "source_id", "page_or_table", "downloaded_file",
        "derivation", "notes"]


def row(**k):
    r = {h: "" for h in HEAD}
    r.update({"country": "Honduras", "year": 2024})
    r.update(k)
    for h in HEAD:
        if isinstance(r[h], float):
            r[h] = f"{r[h]:.4f}".rstrip("0").rstrip(".") if h != "value_usd_per_gj" else f"{r[h]:.3f}"
    return r


def fmt(x, n=4):
    return f"{x:.{n}f}"


# ---------------------------------------------------------------- sources
S = {}


def src(sid, url, title, publisher, date, file, page, supports):
    S[sid] = dict(id=sid, url=url, title=title, publisher=publisher, date=date, retrieval_date=TODAY,
                  downloaded_file=file, page_or_table=page, rows_and_constants_supported=supports)


src("HON-001", "https://www.bch.hn/estadisticos/EME/Informe%20Combustibles/Informe%20de%20Combustibles%20a%20diciembre%202024.pdf",
    "Informe de Combustibles a diciembre 2024 (Importacion de Combustibles)", "Banco Central de Honduras (BCH)",
    "2025", "HON/bch/Informe_de_Combustibles_a_diciembre_2024.pdf",
    "Anexo 1 (CIF by importer type) and Anexo 3 (CIF by product, 2022 to 2024)",
    "history 2022 import CIF; cross-check of 2024 CIF by product")
src("HON-002", "https://www.bch.hn/estadisticos/EME/Informe%20Combustibles/Informe%20de%20Combustibles%20a%20diciembre%202025.pdf",
    "Informe de Combustibles a diciembre 2025", "Banco Central de Honduras (BCH)", "2026",
    "HON/bch/Informe_de_Combustibles_a_diciembre_2025.pdf",
    "Anexo 1 (generadoras termicas bunker) and Anexo 3 (CIF by product, 2023 to 2025)",
    "2024 import CIF DSL GSL KER FOI LPG; history 2023 to 2025")
src("HON-003", "https://www.bch.hn/estadisticos/EME/Informe%20Combustibles/Informe%20de%20Combustibles%20a%20diciembre%202023.pdf",
    "Informe de Combustibles a diciembre 2023", "Banco Central de Honduras (BCH)", "2024",
    "HON/bch/Informe_de_Combustibles_a_diciembre_2023.pdf", "Anexo 3 (CIF by product, 2021 to 2023)",
    "history 2021 import CIF")
src("HON-004", "https://www.bch.hn/estadisticos/GIE/_layouts/15/download.aspx?SourceUrl=/estadisticos/GIE/LIBTipo%20de%20cambio/Precio%20Promedio%20Diario%20del%20D%C3%B3lar.xlsx",
    "Precio Promedio del Dolar de los Estados Unidos de America, Serie Diaria 2000-2026 (Lempiras por US$1.00)",
    "Banco Central de Honduras (BCH)", "2026", "HON/bch/BCH_Precio_Promedio_Diario_del_Dolar.xlsx",
    "sheet Tipo de Cambio Diario, column Compra, daily rows of 2024", "HON_FX_2024")
src("HON-005", "https://sen.hn/wp-content/uploads/2025/04/Informe-Estadistico-Anual-de-Comercializacion-de-Hidrocarburos-en-Honduras-2024.pdf",
    "Informe Estadistico Anual de Comercializacion de Hidrocarburos en Honduras 2024",
    "Secretaria de Estado en el Despacho de Energia (SEN), Direccion General de Hidrocarburos y Biocombustibles",
    "2025-04", "HON/sen_monthly/Informe-Estadistico-Anual-de-Comercializacion-de-Hidrocarburos-en-Honduras-2024.pdf",
    "p.8 import table (volumen recibido, CIF; column labelled millones US$ holds thousands of USD)",
    "2024 import CIF DSL GSL KER FOI LPG (second local source)")
src("HON-006", "https://www.laprensa.hn/economia/como-define-precio-consumidor-combustibles-honduras-NK19576193",
    "Como se define el precio al consumidor de los combustibles en Honduras? (structure valid 27 May to 2 June 2024)",
    "La Prensa (Honduras), reporting the SEN/DGHB import parity price structure", "2024-05-29",
    "HON/press/como-define-precio-consumidor-combustibles-honduras-NK19576193.html",
    "article text, section Formula de los combustibles",
    "DSL GSL KER wholesale import parity, wholesale margin, freight, retail margin, tax (one week)")
src("HON-007", "https://www.elheraldo.hn/economia/como-define-precio-consumidor-combustibles-honduras-GK19575298",
    "Como se define el precio al consumidor de los combustibles en Honduras?", "El Heraldo (Honduras)",
    "2024-05-29", "HON/press/como-define-precio-consumidor-combustibles-honduras-GK19575298.html",
    "article text", "same figures as HON-006 (corroboration)")
src("HON-008", "https://blogs.unah.edu.hn/presencia-universitaria/combustibles-al-alza-presionan-la-economia-y-agravan-la-inseguridad-alimentaria-en-honduras/",
    "Combustibles al alza presionan la economia y agravan la inseguridad alimentaria en Honduras",
    "Universidad Nacional Autonoma de Honduras (UNAH), Presencia Universitaria", "2025",
    "HON/press/combustibles-al-alza-presionan-la-economia-y-agravan-la-inseguridad-alimentaria-en-honduras.html",
    "article text (margin ranges)", "cross-check of margin ranges (retail L 6.07 to 8.38, wholesale L 1.55 to 3.21, freight L 1.53 per gallon)")
cree = [
    ("HON-009", "Informe-de-1er-Ajuste-Tarifario-2024_Final.pdf", "Informe de Ajuste Tarifario Primer Trimestre 2024", "p.6 (forecast fuel prices Q1 2024)"),
    ("HON-010", "Informe-de-2do-Ajuste-Tarifario-2024.pdf", "Informe de Ajuste Tarifario Segundo Trimestre 2024", "p.5 and Fig. 1 (real bunker Jan, Feb 2024); forecast fuel prices Q2 2024"),
    ("HON-011", "Informe-de-3er-Ajuste-Tarifario-2024.pdf", "Informe de Ajuste Tarifario Tercer Trimestre 2024", "p.5 (real bunker Mar to May 2024); forecast fuel prices Q3 2024"),
    ("HON-012", "Informe-de-4to-Ajuste-Tarifario-2024_VF.pdf", "Informe de Ajuste Tarifario Cuarto Trimestre 2024", "p.5 (real bunker Jun to Aug 2024); forecast fuel prices Q4 2024"),
    ("HON-013", "Informe-de-1er-Ajuste-Tarifario-2025.pdf", "Informe de Ajuste Tarifario Primer Trimestre 2025", "p.5 and Fig. 1 p.15 (real bunker Sep to Nov 2024)"),
    ("HON-014", "Informe-de-2do-Ajuste-Tarifario-2025.pdf", "Informe de Ajuste Tarifario Segundo Trimestre 2025", "p.5 (real bunker Dec 2024)"),
]
for sid, fn, title, page in cree:
    src(sid, "https://www.cree.gob.hn/wp-content/uploads/2019/02/" + fn, title,
        "Comision Reguladora de Energia Electrica (CREE)", "2024-2025", "HON/cree/" + fn, page,
        "FOI generator delivered 2024; DSL generator forecast 2024")
src("HON-015", "https://www.cree.gob.hn/wp-content/uploads/2019/02/Informe-revisi%C3%B3n-de-los-CBG-2024-versi%C3%B3n-p%C3%A1gina-web_DC-1.pdf",
    "Revision y analisis del Costo Base de Generacion 2024 presentado por la ENEE", "Comision Reguladora de Energia Electrica (CREE)",
    "2023-12", "HON/cree/Informe-revision-CBG-2024.pdf", "section 3.2 p.13 (projected 2024 HFO 76.77 USD/bbl, diesel 266.50 USc/gal)",
    "DSL generator forecast 2024 (annual)")
src("HON-016", "https://cnd.enee.hn/wp-content/uploads/2026/09/Informe-PIEG-2026-2035.pdf",
    "Plan Indicativo de Expansion de la Generacion 2026-2035, Informe", "Operador del Sistema (ODS) / Centro Nacional de Despacho (CND), Honduras",
    "2026-09", "HON/ods/Informe-PIEG-2026-2035.pdf",
    "section 5.3 pp.55-57 (2024 averages: bunker internacion 1.368 USD/MMBtu, diesel 2.29, coal freight 0.549 and 5% local cost, gas chain)",
    "COA generator delivered (local cost); NGS chain; FOI and DSL internacion components")
src("HON-017", "https://cnd.enee.hn/wp-content/uploads/2026/09/Anexos-PIEG-2026-2035.pdf",
    "Plan Indicativo de Expansion de la Generacion 2026-2035, Anexos", "Operador del Sistema (ODS) / CND, Honduras", "2026-09",
    "HON/ods/Anexos-PIEG-2026-2035.pdf", "Anexo D, Tablas D-1 to D-5 pp.40-41; Tabla H-8 p.54 (Becosa coal/petcoke 105 MW)",
    "NGS chain components; inland transport; Becosa as coal and petcoke plant")
src("HON-018", "https://cnd.enee.hn/wp-content/uploads/2024/07/G01-PIEG-2024-2033-Aprobado.pdf",
    "Plan Indicativo de Expansion de la Generacion 2024-2033 (aprobado)", "Operador del Sistema (ODS) / CND, Honduras", "2024-07",
    "HON/ods/G01-PIEG-2024-2033-Aprobado.pdf", "section 5.3 pp.56-58 (fuel chain method, March 2023 update)",
    "cross-check of NGS chain (0.5 USD/MMBtu shipping) and coal method")
CT = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=340&period={y}&partnerCode=0&flowCode=M&cmdCode={c}"
src("HON-019", CT.format(y=2024, c="270111,270112,270119,271311,271312,271320,271390,271012,271019,271020,271111,271112,271113,271119,271121"),
    "UN Comtrade public preview API, Honduras imports 2024, HS 6-digit", "United Nations Statistics Division (UN Comtrade)", "2026",
    "HON/comtrade/HON_2024_M_6digit.json", "records cmdCode 270112 and 271311 (cifvalue, netWgt kg)",
    "COA and COK import CIF 2024; COA generator delivered (CIF part)")
src("HON-020", CT.format(y=2024, c="2701,2713,2709,2710,2711"),
    "UN Comtrade public preview API, Honduras imports 2024, HS 4-digit", "United Nations Statistics Division (UN Comtrade)", "2026",
    "HON/comtrade/HON_2024_M_4digit.json", "records cmdCode 2701, 2710, 2711, 2713", "cross-check (no 2709 crude imports reported)")
hist_ct = {2018: "HON-021", 2019: "HON-022", 2020: "HON-023", 2021: "HON-024", 2022: "HON-025", 2023: "HON-026"}
for y, sid in hist_ct.items():
    src(sid, CT.format(y=y, c="270112,271311"), f"UN Comtrade public preview API, Honduras imports {y}, HS 270112 and 271311",
        "United Nations Statistics Division (UN Comtrade)", "2026", f"HON/comtrade/HON_{y}_M_coal_coke.json",
        "records cmdCode 270112 and 271311", f"history {y} COA and COK import CIF")
src("HON-027", "https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls", "Henry Hub Natural Gas Spot Price, annual (Dollars per Million Btu)",
    "U.S. Energy Information Administration (EIA)", "2026", "HON/eia/RNGWHHDa.xls", "sheet Data 1, row 2024 (2.19)",
    "HON_EIA_HH_2024 used in NGS chain")
src("HON-028", "https://sen.hn/wp-content/uploads/2025/10/BEN2024.pdf", "Balance Energetico Nacional 2024",
    "Secretaria de Estado en el Despacho de Energia (SEN)", "2025-10", "HON/balance/BEN2024.pdf",
    "section 3 Metodologia p.7; section 4.2.2.3 Coque de petroleo pp.102-103; fuel oil imports p.~100",
    "calorific_HON.csv")
src("HON-029", "https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9",
    "NIST Guide to the SI, Appendix B.9 Factors for units listed by kind of quantity (mass)",
    "National Institute of Standards and Technology (NIST)", "2026", "HON/nist/nist_sp811_appB9.html",
    "row pound (avoirdupois) (lb) to kilogram 4.535 924 E-01", "HON_KG_PER_LB")
src("HON-030", "https://sen.hn/wp-content/uploads/2024/07/Decreto-Legislativo-No.-100-2020-ACPV.pdf",
    "Decreto Legislativo No. 100-2020 (La Gaceta No. 35,524, 22 February 2021)", "Congreso Nacional de Honduras, hosted by SEN",
    "2021-02-22", "HON/sen_legal/Decreto-Legislativo-No.-100-2020-ACPV.pdf", "Articulo 1, p.A2",
    "tax treatment of generator fuel (ACPV exemption for SIN generation)")

# CCHAC bulletins, one source per document
urls = [u.strip() for u in (DL / "cchac" / "urls.txt").read_text().splitlines() if u.strip()]
cchac_ids = {}
for i, u in enumerate(urls):
    sid = f"HON-{40 + i:03d}"
    fn = u.rsplit("/", 1)[1]
    cchac_ids[fn] = sid
    src(sid, u, f"CCHAC-SICA Estadisticas Comerciales de Combustibles, weekly bulletin ({fn.split('-')[0]})",
        "Comite de Cooperacion de Hidrocarburos de America Central (CCHAC-SICA), published by SEN Honduras", "2024",
        "HON/cchac/" + fn,
        "p.6 Precios e Impuesto de las Gasolinas, p.7 Precios e Impuesto del Diesel (Honduras bars); LPG table Costos y variables que conforman el precio al publico (Honduras column)",
        "DSL GSL final consumer pre-tax 2024; LPG structure 2024")

# ---------------------------------------------------------------- data
# BCH Anexo 3 (thousand USD, thousand bbl); 2023-2025 from HON-002, 2022 from HON-001, 2021 from HON-003
BCH = {
    2021: dict(GSL_S=(416392.4, 4530.9), GSL_R=(238521.3, 2707.6), KER=(46204.5, 557.6), DSL=(594221.0, 6966.4), FOI=(317093.0, 5038.0), LPG=(173287.6, 2969.1)),
    2022: dict(GSL_S=(549169.5, 4145.9), GSL_R=(407847.0, 3331.2), KER=(86231.5, 610.0), DSL=(1005691.7, 6770.7), FOI=(449728.6, 5180.6), LPG=(215116.0, 3268.6)),
    2023: dict(GSL_S=(497143.0, 4297.6), GSL_R=(388983.5, 3747.4), KER=(74714.6, 616.4), DSL=(920892.6, 7857.4), FOI=(530883.4, 7128.6), LPG=(175897.7, 3474.1)),
    2024: dict(GSL_S=(511192.5, 4906.9), GSL_R=(387653.6, 4151.9), KER=(60502.1, 568.3), DSL=(876107.4, 8343.0), FOI=(542316.4, 7102.3), LPG=(192701.4, 3759.2)),
    2025: dict(GSL_S=(514725.3, 5467.1), GSL_R=(381396.8, 4357.0), KER=(56077.7, 594.7), DSL=(834875.2, 8775.6), FOI=(392505.5, 5751.6), LPG=(200654.7, 4055.2)),
}
BCH_SRC = {2021: "HON-003", 2022: "HON-001", 2023: "HON-002", 2024: "HON-002", 2025: "HON-002"}
BCH_FILE = {"HON-001": "HON/bch/Informe_de_Combustibles_a_diciembre_2024.pdf",
            "HON-002": "HON/bch/Informe_de_Combustibles_a_diciembre_2025.pdf",
            "HON-003": "HON/bch/Informe_de_Combustibles_a_diciembre_2023.pdf"}
# SEN annual 2024 (bbl received, thousand USD)
SEN = dict(GSL_S=(4764889.63, 502773.99), GSL_R=(4081729.04, 385657.98), DSL=(8343045.76, 916315.08),
           KER=(51413.52, 5457.96), FOI=(6783554.34, 518697.62), LPG=(6600705.11, 337425.45))
W_SUP = 4906.9 / (4906.9 + 4151.9)   # BCH 2024 volume share of superior in gasoline imports
W_REG = 1 - W_SUP
# Press structure 27 May to 2 June 2024, L/gal
PS = dict(GSL_S=dict(ppi=70.8245, tax=24.5595, wm=3.1844, fr=1.53, rm=8.3893, pump=108.49),
          GSL_R=dict(ppi=61.0413, tax=20.4296, wm=3.0338, fr=1.53, rm=8.3165, pump=94.35),
          DSL=dict(ppi=66.0216, tax=11.0245, wm=2.1748, fr=1.53, rm=7.1291, pump=87.88),
          KER=dict(ppi=67.3121, tax=3.7028, wm=1.5552, fr=1.53, rm=6.0771, pump=80.18))
CREE_BUNKER = [73.77, 71.45, 70.33, 76.39, 79.07, 77.01, 76.31, 77.06, 73.56, 67.75, 70.94, 69.09]
CREE_DSL_Q = [274.33, 257.00, 264.67, 270.00]
HH_2024 = 2.19
ODS = dict(uplift=1.15, liq=2.0, ship=0.3, regas=1.0, inland=0.1320, coal_local=0.05, coal_freight=0.549,
           foi_int=1.368, foi_fin=0.0163, dsl_int=2.29, dsl_fin=0.024)


def comtrade(fn, code):
    d = json.load(open(DL / "comtrade" / fn))
    for r in d.get("data", []):
        if r["cmdCode"] == code:
            return r
    return None


weekly = pd.read_csv(DL / "cchac" / "cchac_hon_liquids_weekly.csv")
glp = pd.read_csv(DL / "cchac" / "cchac_hon_glp_weekly.csv")
NW = len(weekly)

P = []
FXN = "HON_FX_2024"

# ------------------------------------------------ COA
r = comtrade("HON_2024_M_6digit.json", "270112")
coa_t = r["cifvalue"] / r["netWgt"] * 1000
P.append(row(fuel="COA", model_code="DIST_COA", price_point="import CIF", price_as_published=round(coa_t, 2),
             currency="USD", unit="USD/t", period="2024", months_covered=12, tax_treatment="CIF value before import duties and taxes",
             calorific_basis="not stated", conversion_constants="IPCC_NCV_COA_OTHER_BITUMINOUS",
             value_usd_per_gj=coa_t / NCV["COA_OTHER_BITUMINOUS"], evidence_class="international customs (Comtrade)",
             source_id="HON-019", page_or_table="cmdCode 270112, flowCode M, partner World",
             downloaded_file="HON/comtrade/HON_2024_M_6digit.json",
             derivation=f"cifvalue {r['cifvalue']:.2f} USD / netWgt {r['netWgt']:.0f} kg x 1000 = {coa_t:.2f} USD/t; / 25.8 GJ/t (IPCC_NCV_COA_OTHER_BITUMINOUS, net) = {coa_t/25.8:.3f} USD/GJ",
             notes=f"HS 270112 bituminous coal. qtyUnitCode 8 (kg), isQtyEstimated {r['isQtyEstimated']}, isNetWgtEstimated {r['isNetWgtEstimated']}; classification {r['classificationCode']}. 27.5 kt in 2024; consumer is the Becosa coal/petcoke steam plant (105 MW, ODS PIEG 2026-2035 Tabla H-8)."))
coa_del = coa_t * (1 + ODS["coal_local"])
P.append(row(fuel="COA", model_code="DIST_COA", price_point="generator delivered", fob="", freight="", port=round(coa_t * ODS["coal_local"], 2),
             price_as_published=round(coa_del, 2), currency="USD", unit="USD/t", period="2024", months_covered=12,
             tax_treatment="CIF plus local logistics; excludes taxes", calorific_basis="not stated",
             conversion_constants="IPCC_NCV_COA_OTHER_BITUMINOUS;HON_ODS_COAL_LOCAL_COST_SHARE",
             value_usd_per_gj=coa_del / NCV["COA_OTHER_BITUMINOUS"], evidence_class="built from published components",
             source_id="HON-019;HON-016", page_or_table="HON-019 cmdCode 270112; HON-016 section 5.3.4 p.56",
             downloaded_file="HON/comtrade/HON_2024_M_6digit.json;HON/ods/Informe-PIEG-2026-2035.pdf",
             derivation=f"import CIF {coa_t:.2f} USD/t (HON-019) x (1 + 0.05 local cost share over CIF, HON_ODS_COAL_LOCAL_COST_SHARE, HON-016 5.3.4) = {coa_del:.2f} USD/t; / 25.8 GJ/t (IPCC_NCV_COA_OTHER_BITUMINOUS) = {coa_del/25.8:.3f} USD/GJ",
             notes="The system operator's planning chain for a coal plant adds 5% of the CIF price for local logistics and operation (port column holds that 5%). Ocean freight (0.549 USD/MMBtu in the ODS chain) is already inside the observed CIF."))
# ------------------------------------------------ COK
r = comtrade("HON_2024_M_6digit.json", "271311")
cok_t = r["cifvalue"] / r["netWgt"] * 1000
P.append(row(fuel="COK", model_code="DIST_COK", price_point="import CIF", price_as_published=round(cok_t, 2), currency="USD",
             unit="USD/t", period="2024", months_covered=12, tax_treatment="CIF value before import duties and taxes",
             calorific_basis="not stated", conversion_constants="IPCC_NCV_COK", value_usd_per_gj=cok_t / NCV["COK"],
             evidence_class="international customs (Comtrade)", source_id="HON-019",
             page_or_table="cmdCode 271311, flowCode M, partner World", downloaded_file="HON/comtrade/HON_2024_M_6digit.json",
             derivation=f"cifvalue {r['cifvalue']:.2f} USD / netWgt {r['netWgt']:.2f} kg x 1000 = {cok_t:.2f} USD/t; / 32.5 GJ/t (IPCC_NCV_COK, net) = {cok_t/32.5:.3f} USD/GJ",
             notes=f"HS 271311 petroleum coke not calcined, 185.2 kt in 2024. isQtyEstimated {r['isQtyEstimated']}, isNetWgtEstimated {r['isNetWgtEstimated']}. Same supply row feeds Becosa (PPCOK) and industry (T5COKIND); the SEN balance 2024 reports all 2024 petcoke as autoproduction. No published delivered petcoke price; the ODS 5% local cost is stated for coal plants only and is not applied here."))
# ------------------------------------------------ NGS
fob = HH_2024 * ODS["uplift"] + ODS["liq"]
tot = fob + ODS["ship"] + ODS["regas"]
P.append(row(fuel="NGS", model_code="DIST_NGS", price_point="generator delivered", fob=round(fob, 4), freight=ODS["ship"],
             importer_terminal_margin=ODS["regas"], price_as_published=round(tot, 4), currency="USD", unit="USD/MMBtu",
             period="2024", months_covered=12, tax_treatment="pre-tax", calorific_basis="gross",
             conversion_constants="GJ_PER_MMBTU;HON_EIA_HH_2024;HON_ODS_NGS_BUYER_UPLIFT;HON_ODS_LNG_LIQUEFACTION;HON_ODS_LNG_SHIPPING_INTERNACION;HON_ODS_LNG_REGASIFICATION",
             value_usd_per_gj=tot / GJ_PER_MMBTU, evidence_class="built from published components",
             source_id="HON-016;HON-017;HON-027", page_or_table="HON-016 section 5.3.5 pp.56-57; HON-017 Tabla D-5 p.41; HON-027 row 2024",
             downloaded_file="HON/ods/Informe-PIEG-2026-2035.pdf;HON/ods/Anexos-PIEG-2026-2035.pdf;HON/eia/RNGWHHDa.xls",
             derivation=f"Henry Hub 2024 2.19 USD/MMBtu (HON_EIA_HH_2024) x 1.15 buyer costs (HON_ODS_NGS_BUYER_UPLIFT) = 2.5185; + 2.0 liquefaction (HON_ODS_LNG_LIQUEFACTION) = {fob:.4f} (fob column); + 0.3 shipping and internacion (HON_ODS_LNG_SHIPPING_INTERNACION, freight column) + 1.0 regasification FSRU (HON_ODS_LNG_REGASIFICATION, importer_terminal_margin column) = {tot:.4f} USD/MMBtu; / 1.055056 GJ/MMBtu (GJ_PER_MMBTU) = {tot/GJ_PER_MMBTU:.3f} USD/GJ",
             notes="Honduras imported no natural gas in 2024; this is the system operator's published LNG cost chain to a plant at Puerto Cortes applied to the 2024 Henry Hub average. Inland transport 0.1320 USD/MMBtu (Tabla D-2, HON_ODS_NGS_INLAND) applies only if the plant is away from the port and is not added. Basis recorded as gross because Henry Hub is quoted on gross Btu; the ODS report says it converts fuels to LHV but does not state the basis of the chain components."))
# ------------------------------------------------ FOI
foi_g = sum(CREE_BUNKER) / 12
P.append(row(fuel="FOI", model_code="DIST_FOI", price_point="generator delivered", price_as_published=round(foi_g, 4), currency="USD",
             unit="USD/bbl", period="2024-01 to 2024-12", months_covered=12, tax_treatment="as used for generation; fuel for SIN generation is exempt from ACPV (HON-030)",
             calorific_basis="not stated", conversion_constants="UN_GAL_PER_T_FOI;USGAL_PER_BBL;IPCC_NCV_FOI",
             value_usd_per_gj=per_bbl_to_gj(foi_g, "FOI"), evidence_class="local regulator or operator",
             source_id="HON-010;HON-011;HON-012;HON-013;HON-014;HON-030",
             page_or_table="precio real del bunker by month: HON-010 p.5 (Jan, Feb), HON-011 p.5 (Mar, Apr, May), HON-012 p.5 (Jun, Jul, Aug), HON-013 p.5 (Sep, Oct, Nov), HON-014 p.5 (Dec)",
             downloaded_file="HON/cree/Informe-de-2do-Ajuste-Tarifario-2024.pdf;HON/cree/Informe-de-3er-Ajuste-Tarifario-2024.pdf;HON/cree/Informe-de-4to-Ajuste-Tarifario-2024_VF.pdf;HON/cree/Informe-de-1er-Ajuste-Tarifario-2025.pdf;HON/cree/Informe-de-2do-Ajuste-Tarifario-2025.pdf",
             derivation="mean of Jan 73.77, Feb 71.45, Mar 70.33, Apr 76.39, May 79.07, Jun 77.01, Jul 76.31, Aug 77.06, Sep 73.56, Oct 67.75, Nov 70.94, Dec 69.09 = "
                        f"{foi_g:.4f} USD/bbl; / 42 gal/bbl (USGAL_PER_BBL) x 278 gal/t (UN_GAL_PER_T_FOI) / 40.4 GJ/t (IPCC_NCV_FOI) = {per_bbl_to_gj(foi_g,'FOI'):.3f} USD/GJ",
             notes="CREE precio real of bunker (HFO 3%) used in the SIN, simple mean of 12 months. ODS chain for 2024: internacion 1.368 USD/MMBtu and financial cost 0.0163 USD/MMBtu over the NY No.6 3% reference (HON-016 5.3.2), components not added here because they are inside the real price."))
v, b = BCH[2024]["FOI"]
P.append(row(fuel="FOI", model_code="DIST_FOI", price_point="import CIF", price_as_published=round(v / b, 2), currency="USD", unit="USD/bbl",
             period="2024", months_covered=12, tax_treatment="CIF, before taxes", calorific_basis="not stated",
             conversion_constants="UN_GAL_PER_T_FOI;USGAL_PER_BBL;IPCC_NCV_FOI", value_usd_per_gj=per_bbl_to_gj(v / b, "FOI"),
             evidence_class="local customs or statistics", source_id="HON-002", page_or_table="Anexo 3, BUNKER, 2024 column",
             downloaded_file=BCH_FILE["HON-002"],
             derivation=f"{v:.1f} thousand USD / {b:.1f} thousand bbl = {v/b:.2f} USD/bbl; / 42 x 278 / 40.4 = {per_bbl_to_gj(v/b,'FOI'):.3f} USD/GJ",
             notes="All bunker importers. Direct imports by thermal generators alone: 352,502.5 thousand USD / 4,586.6 thousand bbl = 76.86 USD/bbl (Anexo 1 of HON-002 and HON-001). SEN annual report gives 518,697.62 / 6,783,554.34 bbl = 76.46 USD/bbl."))
# ------------------------------------------------ liquids: import CIF (BCH and SEN)
def gsl_w(d):
    vs, bs = d["GSL_S"]
    vr, br = d["GSL_R"]
    return (vs + vr) / (bs + br)


for f, mc in [("DSL", "DIST_DSL"), ("GSL", "DIST_GSL"), ("KER", "DIST_KER"), ("LPG", "DIST_LPG")]:
    if f == "GSL":
        val = gsl_w(BCH[2024])
        der = f"(511,192.5 + 387,653.6) thousand USD / (4,906.9 + 4,151.9) thousand bbl (superior + regular) = {val:.2f} USD/bbl"
        note = "Superior and regular combined by import value and volume (superior 104.18, regular 93.37 USD/bbl)."
        tab = "Anexo 3, GASOLINA SUPERIOR and GASOLINA REGULAR, 2024 column"
    else:
        v, b = BCH[2024][f]
        val = v / b
        der = f"{v:.1f} thousand USD / {b:.1f} thousand bbl = {val:.2f} USD/bbl"
        note = ""
        tab = f"Anexo 3, {dict(DSL='DIESEL', KER='KEROSENE', LPG='LPG')[f]}, 2024 column"
        if f == "LPG":
            note = "The December 2025 report revises 2024 LPG to 192,701.4 / 3,759.2 (51.26 USD/bbl); the December 2024 report had 177,477.2 / 3,442.1 (51.56)."
    P.append(row(fuel=f, model_code=mc, price_point="import CIF", price_as_published=round(val, 2), currency="USD", unit="USD/bbl",
                 period="2024", months_covered=12, tax_treatment="CIF, before taxes", calorific_basis="not stated",
                 conversion_constants=f"UN_GAL_PER_T_{f};USGAL_PER_BBL;IPCC_NCV_{f}", value_usd_per_gj=per_bbl_to_gj(val, f),
                 evidence_class="local customs or statistics", source_id="HON-002", page_or_table=tab, downloaded_file=BCH_FILE["HON-002"],
                 derivation=der + f"; / 42 gal/bbl x {UN_GAL[f]} gal/t (UN_GAL_PER_T_{f}) / {NCV[f]} GJ/t (IPCC_NCV_{f}) = {per_bbl_to_gj(val,f):.3f} USD/GJ",
                 notes=("BCH data from SARAH customs records and importers. " + note).strip()))
    # SEN annual
    if f == "GSL":
        bs, vs = SEN["GSL_S"]
        br, vr = SEN["GSL_R"]
        sval = (vs + vr) / (bs + br) * 1000
        sder = f"(502,773.99 + 385,657.98) thousand USD / (4,764,889.63 + 4,081,729.04) bbl x 1000 = {sval:.2f} USD/bbl"
    else:
        bb, vv = SEN[f]
        sval = vv / bb * 1000
        sder = f"{vv:,.2f} thousand USD / {bb:,.2f} bbl x 1000 = {sval:.2f} USD/bbl"
    P.append(row(fuel=f, model_code=mc, price_point="import CIF", price_as_published=round(sval, 2), currency="USD", unit="USD/bbl",
                 period="2024", months_covered=12, tax_treatment="CIF, before taxes", calorific_basis="not stated",
                 conversion_constants=f"UN_GAL_PER_T_{f};USGAL_PER_BBL;IPCC_NCV_{f}", value_usd_per_gj=per_bbl_to_gj(sval, f),
                 evidence_class="local regulator or operator", source_id="HON-005",
                 page_or_table="p.8 import table (volumen recibido, CIF)", downloaded_file=S["HON-005"]["downloaded_file"],
                 derivation=sder + f"; / 42 x {UN_GAL[f]} / {NCV[f]} = {per_bbl_to_gj(sval,f):.3f} USD/GJ",
                 notes="Second local source for the same price point. The CIF column is labelled millones US$ but holds thousands of USD. Volumes match BCH for diesel; CIF values differ (diesel 916.3 vs 876.1 million USD)."))
# FOI SEN annual
bb, vv = SEN["FOI"]
P.append(row(fuel="FOI", model_code="DIST_FOI", price_point="import CIF", price_as_published=round(vv / bb * 1000, 2), currency="USD", unit="USD/bbl",
             period="2024", months_covered=12, tax_treatment="CIF, before taxes", calorific_basis="not stated",
             conversion_constants="UN_GAL_PER_T_FOI;USGAL_PER_BBL;IPCC_NCV_FOI", value_usd_per_gj=per_bbl_to_gj(vv / bb * 1000, "FOI"),
             evidence_class="local regulator or operator", source_id="HON-005", page_or_table="p.8 import table (FUEL OIL)",
             downloaded_file=S["HON-005"]["downloaded_file"],
             derivation=f"518,697.62 thousand USD / 6,783,554.34 bbl x 1000 = {vv/bb*1000:.2f} USD/bbl; / 42 x 278 / 40.4 = {per_bbl_to_gj(vv/bb*1000,'FOI'):.3f} USD/GJ",
             notes="Second local source."))
# ------------------------------------------------ liquids: press structure week (wholesale import parity, pre-tax)
for f, mc, keys in [("DSL", "DIST_DSL", ["DSL"]), ("GSL", "DIST_GSL", ["GSL_S", "GSL_R"]), ("KER", "DIST_KER", ["KER"])]:
    if len(keys) == 1:
        d = PS[keys[0]]
        ppi, wm, fr, rm, tax = d["ppi"], d["wm"], d["fr"], d["rm"], d["tax"]
        wd = ""
    else:
        a, c = PS["GSL_S"], PS["GSL_R"]
        ppi = W_SUP * a["ppi"] + W_REG * c["ppi"]
        wm = W_SUP * a["wm"] + W_REG * c["wm"]
        fr = 1.53
        rm = W_SUP * a["rm"] + W_REG * c["rm"]
        tax = W_SUP * a["tax"] + W_REG * c["tax"]
        wd = f"superior and regular weighted by BCH 2024 import volumes (superior share {W_SUP:.4f} = 4,906.9 / 9,058.8 thousand bbl, HON-002): "
    usd = ppi / HON_FX_2024
    P.append(row(fuel=f, model_code=mc, price_point="wholesale import parity", price_as_published=round(ppi, 4), currency="HNL", unit="HNL/USgal",
                 period="2024-05-27 to 2024-06-02", months_covered="0.25", tax_treatment="excludes taxes (precio paridad importacion sin impuestos)",
                 calorific_basis="not stated", exchange_rate=HON_FX_2024, exchange_rate_constant=FXN,
                 conversion_constants=f"UN_GAL_PER_T_{f};IPCC_NCV_{f}", value_usd_per_gj=per_gal_to_gj(usd, f),
                 evidence_class="built from published components", source_id="HON-006;HON-007;HON-004",
                 page_or_table="HON-006 article section Formula de los combustibles", downloaded_file=S["HON-006"]["downloaded_file"],
                 derivation=wd + f"PPI {ppi:.4f} HNL/gal / 24.7950 HNL/USD (HON_FX_2024) = {usd:.4f} USD/gal; x {UN_GAL[f]} gal/t (UN_GAL_PER_T_{f}) / {NCV[f]} GJ/t (IPCC_NCV_{f}) = {per_gal_to_gj(usd,f):.3f} USD/GJ",
                 notes="One weekly SEN/DGHB structure as reported by La Prensa and El Heraldo (29 May 2024). PPI includes FOB, freight, insurance and importer costs to the terminal; the article does not split them. The annual BCH exchange rate is used because the article gives no weekly rate."))
    pre = ppi + wm + fr + rm
    usdp = pre / HON_FX_2024
    P.append(row(fuel=f, model_code=mc, price_point="final consumer pre-tax", wholesale_margin=round(wm, 4), inland_freight=round(fr, 4),
                 retail_margin=round(rm, 4), price_as_published=round(pre, 4), currency="HNL", unit="HNL/USgal",
                 period="2024-05-27 to 2024-06-02", months_covered="0.25", tax_treatment=f"excludes tax ({tax:.4f} HNL/gal ACPV)",
                 calorific_basis="not stated", exchange_rate=HON_FX_2024, exchange_rate_constant=FXN,
                 conversion_constants=f"UN_GAL_PER_T_{f};IPCC_NCV_{f}", value_usd_per_gj=per_gal_to_gj(usdp, f),
                 evidence_class="built from published components", source_id="HON-006;HON-007;HON-008;HON-004",
                 page_or_table="HON-006 article section Formula de los combustibles", downloaded_file=S["HON-006"]["downloaded_file"],
                 derivation=wd + f"PPI {ppi:.4f} + wholesale margin {wm:.4f} + freight {fr:.4f} + retail margin {rm:.4f} = {pre:.4f} HNL/gal (equals pump price minus tax); / 24.7950 (HON_FX_2024) = {usdp:.4f} USD/gal; x {UN_GAL[f]} / {NCV[f]} = {per_gal_to_gj(usdp,f):.3f} USD/GJ",
                 notes=f"Tegucigalpa reference. Margins are fixed HNL amounts per gallon; in USD/GJ: wholesale {per_gal_to_gj(wm/HON_FX_2024,f):.3f}, inland freight {per_gal_to_gj(fr/HON_FX_2024,f):.3f}, retail {per_gal_to_gj(rm/HON_FX_2024,f):.3f}. UNAH (HON-008) gives the same ranges (retail 6.07 to 8.38, wholesale 1.55 to 3.21, freight 1.53 HNL/gal)."))
# ------------------------------------------------ CCHAC weekly pre-tax (DSL, GSL)
cfiles = sorted(set(weekly.file) - {"image"})
cfn = sorted(set(cfiles) | {u.rsplit('/', 1)[1] for u in urls if u.rsplit('/', 1)[1].startswith(('No.1-', 'No.30', 'No.31'))})
cids = ";".join(sorted(cchac_ids[f] for f in cfn))
cdl = ";".join("HON/cchac/" + f for f in cfn)
dsl_pre = weekly["DSL_pre_tax"].mean()
gs = weekly["GSL_superior_pre_tax"].mean()
gr = weekly["GSL_regular_pre_tax"].mean()
gw = W_SUP * gs + W_REG * gr
weeks_note = f"{NW} weekly bulletins from 31 Dec 2023 to 3 Aug 2024 (bulletins 9, 14 and 22 not published by SEN; none after bulletin 31); bulletins 1, 30 and 31 read from page images"
P.append(row(fuel="DSL", model_code="DIST_DSL", price_point="final consumer pre-tax", price_as_published=round(dsl_pre, 4), currency="USD",
             unit="USD/USgal", period="2023-12-31 to 2024-08-03", months_covered=7, tax_treatment="excludes taxes (Precio sin Imp.)",
             calorific_basis="not stated", conversion_constants="UN_GAL_PER_T_DSL;IPCC_NCV_DSL", value_usd_per_gj=per_gal_to_gj(dsl_pre, "DSL"),
             evidence_class="local regulator or operator", source_id=cids, page_or_table="p.7 Precios e Impuesto del Diesel, Honduras bar",
             downloaded_file=cdl,
             derivation=f"mean of {NW} weekly Precio sin Imp. values = {dsl_pre:.4f} USD/gal; x 304 gal/t (UN_GAL_PER_T_DSL) / 43.0 GJ/t (IPCC_NCV_DSL) = {per_gal_to_gj(dsl_pre,'DSL'):.3f} USD/GJ",
             notes=weeks_note + ". Official regulated pump price (Tegucigalpa) less the fixed ACPV tax (0.45 USD/gal); before the 2024 stabilisation subsidy."))
P.append(row(fuel="GSL", model_code="DIST_GSL", price_point="final consumer pre-tax", price_as_published=round(gw, 4), currency="USD",
             unit="USD/USgal", period="2023-12-31 to 2024-08-03", months_covered=7, tax_treatment="excludes taxes (Precio sin Imp.)",
             calorific_basis="not stated", conversion_constants="UN_GAL_PER_T_GSL;IPCC_NCV_GSL", value_usd_per_gj=per_gal_to_gj(gw, "GSL"),
             evidence_class="local regulator or operator", source_id=cids + ";HON-002", page_or_table="p.6 Precios e Impuesto de las Gasolinas, Honduras bars; HON-002 Anexo 3 volumes",
             downloaded_file=cdl,
             derivation=f"mean superior {gs:.4f} and regular {gr:.4f} USD/gal over {NW} weeks; weighted {W_SUP:.4f}/{W_REG:.4f} by BCH 2024 import volumes = {gw:.4f} USD/gal; x 357 gal/t (UN_GAL_PER_T_GSL) / 44.3 GJ/t (IPCC_NCV_GSL) = {per_gal_to_gj(gw,'GSL'):.3f} USD/GJ",
             notes=weeks_note + f". Regular alone {per_gal_to_gj(gr,'GSL'):.3f}, superior alone {per_gal_to_gj(gs,'GSL'):.3f} USD/GJ."))
# ------------------------------------------------ DSL generator forecast (CREE)
dq = sum(CREE_DSL_Q) / 4 / 100
P.append(row(fuel="DSL", model_code="DIST_DSL", price_point="generator delivered", price_as_published=round(dq * 100, 2), currency="USD",
             unit="USc/USgal", period="2024 (quarterly forecasts)", months_covered=12,
             tax_treatment="as used for generation; fuel for SIN generation is exempt from ACPV (HON-030)", calorific_basis="not stated",
             conversion_constants="UN_GAL_PER_T_DSL;IPCC_NCV_DSL", value_usd_per_gj=per_gal_to_gj(dq, "DSL"),
             evidence_class="local regulator or operator", source_id="HON-009;HON-010;HON-011;HON-012;HON-015;HON-030",
             page_or_table="precio promedio de los combustibles utilizados para la generacion: HON-009 p.6 (Q1 274.33), HON-010 (Q2 257.00), HON-011 (Q3 264.67), HON-012 (Q4 270); HON-015 section 3.2 (annual 266.50)",
             downloaded_file="HON/cree/Informe-de-1er-Ajuste-Tarifario-2024_Final.pdf;HON/cree/Informe-de-2do-Ajuste-Tarifario-2024.pdf;HON/cree/Informe-de-3er-Ajuste-Tarifario-2024.pdf;HON/cree/Informe-de-4to-Ajuste-Tarifario-2024_VF.pdf;HON/cree/Informe-revision-CBG-2024.pdf",
             derivation=f"(274.33 + 257.00 + 264.67 + 270.00) / 4 = {dq*100:.2f} USc/gal = {dq:.4f} USD/gal (equal to the CBG 2024 annual 266.50); x 304 / 43.0 = {per_gal_to_gj(dq,'DSL'):.3f} USD/GJ",
             notes="Forecast prices used by the system operator for each quarter (Platts based, internalised with the SEN price structure); CREE publishes no real diesel price for generation, only for bunker. ODS chain for 2024: diesel internacion 2.29 USD/MMBtu plus financial cost 0.024 (HON-016 5.3.3)."))
# ------------------------------------------------ LPG (CCHAC structure)
nl = len(glp)
cif = glp["cif_plus_ppi"].mean()
fobm, frm, term, portm = glp["fob"].mean(), glp["freight"].mean(), glp["terminal"].mean(), glp["port"].mean()
imp, dist, inl, ret, cyl = glp["importer_margin"].mean(), glp["distributor_margin"].mean(), glp["inland_freight"].mean(), glp["retail_margin"].mean(), glp["cylinder_maintenance"].mean()
cif_c = fobm + frm + term + portm
gfiles = sorted(set(glp.file))
gids = ";".join(sorted({cchac_ids[f] for f in gfiles}))
gdl = ";".join("HON/cchac/" + f for f in gfiles)
P.append(row(fuel="LPG", model_code="DIST_LPG", price_point="wholesale import parity", fob=round(fobm, 4), freight=round(frm, 4),
             port=round(term + portm, 4), price_as_published=round(cif_c, 4), currency="USD", unit="USD per 25 lb cylinder",
             period="2023-12-31 to 2024-07-13", months_covered=6.5, tax_treatment="excludes taxes", calorific_basis="not stated",
             conversion_constants="HON_KG_PER_LB;IPCC_NCV_LPG", value_usd_per_gj=cif_c / HON_GJ_PER_CYL25,
             evidence_class="local regulator or operator", source_id=gids,
             page_or_table="table Costos y variables que conforman el precio al publico, column HONDURAS (Precio FOB, Flete Maritimo, Operacion de Terminal, Cargo Portuario, Precio CIF+ (PPI))",
             downloaded_file=gdl,
             derivation=f"means over {nl} weeks: FOB {fobm:.4f} + freight {frm:.4f} + terminal {term:.4f} + port {portm:.4f} = {cif_c:.4f} USD/cyl (published CIF+ mean over the 24 weeks that print it: {cif:.4f}); cylinder 25 lb x 0.4535924 kg/lb (HON_KG_PER_LB) = 11.3398 kg x 47.3 GJ/t (IPCC_NCV_LPG) = {HON_GJ_PER_CYL25:.5f} GJ; {cif_c:.4f} / {HON_GJ_PER_CYL25:.5f} = {cif_c/HON_GJ_PER_CYL25:.3f} USD/GJ",
             notes="Regulated domestic 25 lb cylinder, 100% propane; insurance row blank for Honduras. No LPG structure was found after mid July 2024."))
pre_l = cif_c + imp + dist + inl + ret + cyl
P.append(row(fuel="LPG", model_code="DIST_LPG", price_point="final consumer pre-tax", fob=round(fobm, 4), freight=round(frm, 4), port=round(term + portm, 4),
             importer_terminal_margin=round(imp, 4), wholesale_margin=round(dist, 4), inland_freight=round(inl, 4), retail_margin=round(ret, 4),
             price_as_published=round(pre_l, 4), currency="USD", unit="USD per 25 lb cylinder", period="2023-12-31 to 2024-07-13", months_covered=6.5,
             tax_treatment="excludes ACPV tax 0.88 USD/cyl; before subsidy", calorific_basis="not stated",
             conversion_constants="HON_KG_PER_LB;IPCC_NCV_LPG", value_usd_per_gj=pre_l / HON_GJ_PER_CYL25,
             evidence_class="local regulator or operator", source_id=gids, page_or_table="same table, Margenes and Otros rows",
             downloaded_file=gdl,
             derivation=f"CIF+ {cif_c:.4f} + importer {imp:.4f} + distributor {dist:.4f} + land transport {inl:.4f} + point of sale {ret:.4f} + cylinder maintenance {cyl:.4f} = {pre_l:.4f} USD/cyl; / {HON_GJ_PER_CYL25:.5f} GJ = {pre_l/HON_GJ_PER_CYL25:.3f} USD/GJ",
             notes="Margins of the bottled 25 lb channel. Importer margin alone is 0.31 USD/cyl (0.578 USD/GJ)."))

# ---------------------------------------------------------------- history
H = []
for y in range(2021, 2026):
    sid = BCH_SRC[y]
    for f, mc in [("DSL", "DIST_DSL"), ("GSL", "DIST_GSL"), ("KER", "DIST_KER"), ("FOI", "DIST_FOI"), ("LPG", "DIST_LPG")]:
        if f == "GSL":
            val = gsl_w(BCH[y])
            der = f"(superior {BCH[y]['GSL_S'][0]:,.1f} + regular {BCH[y]['GSL_R'][0]:,.1f}) / ({BCH[y]['GSL_S'][1]:,.1f} + {BCH[y]['GSL_R'][1]:,.1f}) = {val:.2f} USD/bbl"
        else:
            v, b = BCH[y][f]
            val = v / b
            der = f"{v:,.1f} thousand USD / {b:,.1f} thousand bbl = {val:.2f} USD/bbl"
        H.append(row(year=y, fuel=f, model_code=mc, price_point="import CIF", price_as_published=round(val, 2), currency="USD", unit="USD/bbl",
                     period=str(y), months_covered=12, tax_treatment="CIF, before taxes", calorific_basis="not stated",
                     conversion_constants=f"UN_GAL_PER_T_{f};USGAL_PER_BBL;IPCC_NCV_{f}", value_usd_per_gj=per_bbl_to_gj(val, f),
                     evidence_class="local customs or statistics", source_id=sid, page_or_table=f"Anexo 3, {y} column",
                     downloaded_file=BCH_FILE[sid], derivation=der + f"; / 42 x {UN_GAL[f]} / {NCV[f]} = {per_bbl_to_gj(val,f):.3f} USD/GJ",
                     notes="Nominal USD. Latest BCH edition used for each year (2021 from the December 2023 report, 2022 from December 2024, 2023 to 2025 from December 2025)."))
for y in range(2018, 2025):
    fn = "HON_2024_M_6digit.json" if y == 2024 else f"HON_{y}_M_coal_coke.json"
    sid = "HON-019" if y == 2024 else hist_ct[y]
    for code, f, mc, nc, ncv in [("270112", "COA", "DIST_COA", "IPCC_NCV_COA_OTHER_BITUMINOUS", 25.8), ("271311", "COK", "DIST_COK", "IPCC_NCV_COK", 32.5)]:
        r = comtrade(fn, code)
        if not r:
            continue
        t = r["cifvalue"] / r["netWgt"] * 1000
        H.append(row(year=y, fuel=f, model_code=mc, price_point="import CIF", price_as_published=round(t, 2), currency="USD", unit="USD/t",
                     period=str(y), months_covered=12, tax_treatment="CIF value before import duties and taxes", calorific_basis="not stated",
                     conversion_constants=nc, value_usd_per_gj=t / ncv, evidence_class="international customs (Comtrade)", source_id=sid,
                     page_or_table=f"cmdCode {code}", downloaded_file="HON/comtrade/" + fn,
                     derivation=f"cifvalue {r['cifvalue']:.2f} / netWgt {r['netWgt']:.2f} kg x 1000 = {t:.2f} USD/t; / {ncv} GJ/t ({nc}) = {t/ncv:.3f} USD/GJ",
                     notes=f"Nominal USD; classification {r['classificationCode']}; isNetWgtEstimated {r['isNetWgtEstimated']}. Coal not reported for 2018 and 2022; 2025 not yet available in the preview API."))

# ---------------------------------------------------------------- constants
C = [
    ("HON_FX_2024", "24.7950", "HNL/USD", "HON-004", "sheet Tipo de Cambio Diario, column Compra, 247 daily rows of 2024",
     "mean of 247 daily Compra rates in 2024 computed by fx_bch.py (Venta mean 24.9190; file kept in downloads HON/bch/fx_annual_means.csv)"),
    ("HON_KG_PER_LB", "0.4535924", "kg/lb", "HON-029", "row pound (avoirdupois) (lb)", "as printed (4.535 924 E-01)"),
    ("HON_KG_PER_CYL25", f"{HON_KG_PER_CYL25:.5f}", "kg per 25 lb cylinder", "HON-029", "row pound (avoirdupois) (lb)", "25 lb x HON_KG_PER_LB"),
    ("HON_EIA_HH_2024", "2.19", "USD/MMBtu (gross)", "HON-027", "sheet Data 1, 2024", "as published"),
    ("HON_ODS_NGS_BUYER_UPLIFT", "1.15", "factor on Henry Hub", "HON-016", "section 5.3.5 p.56", "as published (15% buyer costs)"),
    ("HON_ODS_LNG_LIQUEFACTION", "2.0", "USD/MMBtu", "HON-017", "Tabla D-5 p.41", "as published"),
    ("HON_ODS_LNG_SHIPPING_INTERNACION", "0.3", "USD/MMBtu", "HON-017", "Tabla D-5 p.41", "as published"),
    ("HON_ODS_LNG_REGASIFICATION", "1.0", "USD/MMBtu", "HON-017", "Tabla D-5 p.41", "as published"),
    ("HON_ODS_NGS_INLAND", "0.1320", "USD/MMBtu", "HON-017", "Tabla D-2 p.40", "as published; not applied"),
    ("HON_ODS_COAL_LOCAL_COST_SHARE", "0.05", "share of CIF", "HON-016", "section 5.3.4 p.56", "as published (5% local cost over CIF)"),
    ("HON_ODS_COAL_FREIGHT", "0.549", "USD/MMBtu", "HON-016", "section 5.3.4 p.56", "as published; already inside observed CIF, not applied"),
    ("HON_ODS_FOI_INTERNACION_2024", "1.368", "USD/MMBtu (LHV)", "HON-016", "section 5.3.2 p.56", "as published, 2024 average; informational"),
    ("HON_ODS_DSL_INTERNACION_2024", "2.29", "USD/MMBtu (LHV)", "HON-016", "section 5.3.3 p.56", "as published, 2024 average; informational"),
    ("HON_GSL_SUPERIOR_SHARE_2024", f"{W_SUP:.4f}", "share of gasoline import volume", "HON-002", "Anexo 3, 2024 barrels",
     "4,906.9 / (4,906.9 + 4,151.9) thousand bbl"),
]
# ---------------------------------------------------------------- calorific
CAL = [dict(country="Honduras", balance="Balance Energetico Nacional 2024", publisher="Secretaria de Estado en el Despacho de Energia (SEN)",
            url=S["HON-028"]["url"], net_or_gross="not stated",
            factor_NGS="", factor_COA="", factor_COK=f"{1426/257:.3f}", factor_FOI=f"{7096.95/6783:.4f}",
            factor_units="COK: kBEP per thousand t (1426 kBEP / 257 kt, implied); FOI: kBEP per thousand bbl (7,096.95 kBEP / 6,783 kbbl, implied); no natural gas or mineral coal in the 2024 balance",
            page_or_table="section 3 Metodologia p.7 (follows UN IRES and OLADE); section 4.2.2.3 p.103 (petcoke); fuel oil imports paragraph p.~100",
            source_id="HON-028"),
       dict(country="Honduras", balance="ODS Plan Indicativo de Expansion de la Generacion 2026-2035 (fuel price chain)",
            publisher="Operador del Sistema (ODS) / CND", url=S["HON-016"]["url"], net_or_gross="net",
            factor_NGS="1034", factor_COA="22.05", factor_COK="", factor_FOI="6.289",
            factor_units="NGS Btu/ft3; COA MMBtu/short ton; FOI MMBtu/bbl (EIA Monthly Energy Review factors, which are gross); ODS states it converts fuel prices to lower heating value",
            page_or_table="section 5.3 p.55", source_id="HON-016")]

# ---------------------------------------------------------------- search log
L = []


def log(fuels, lead, desc, url, result, detail):
    for f in fuels.split(","):
        L.append(dict(country="Honduras", fuel=f, lead_id=lead, lead=desc, url_or_query=url, date=TODAY, result=result, detail=detail))


ALL = "COA,COK,NGS,FOI,DSL,GSL,KER,LPG"
log("DSL,GSL,LPG", "sen_weekly", "SEN-hosted CCHAC weekly bulletins 2024", "https://sen.hn/wp-content/uploads/2024/ (28 bulletin URLs in sources_HON.csv)", "value found",
    "28 weeks 31 Dec 2023 to 3 Aug 2024 for diesel and gasoline pre-tax and tax; LPG structure 25 weeks; bulletins 1, 30, 31 read from images")
log("KER,FOI", "sen_weekly", "SEN-hosted CCHAC weekly bulletins 2024", "https://sen.hn/wp-content/uploads/2024/", "no value", "bulletins cover gasoline, diesel and LPG only")
log("COA,COK,NGS", "sen_weekly", "SEN-hosted CCHAC weekly bulletins 2024", "https://sen.hn/wp-content/uploads/2024/", "no value", "no coal, petcoke or natural gas")
log("DSL,GSL,KER,LPG", "sen_weekly", "SEN media library search for missing and later bulletins", "https://sen.hn/wp-json/wp/v2/media?search=BOLETIN&per_page=100", "not found",
    "media library lists bulletins 1 to 31 only; 9, 14 and 22 absent; nothing after 3 Aug 2024")
log("DSL,GSL,KER,LPG", "sen_weekly", "Guatemala MEM copy of CCHAC bulletins (media search)", "https://mem.gob.gt/wp-json/wp/v2/media?search=CCHAC&per_page=100", "blocked HTTP 403", "not retried; on manual list")
log("DSL,GSL,KER,LPG", "sen_weekly", "SEN weekly maximum price tables by municipality (S1-AGOSTO-2024 etc.)", "https://sen.hn/wp-content/uploads/2024/10/S1-AGOSTO-2024.pdf", "no value",
    "retail prices with tax in HNL by municipality; no PPI or margin split; not used")
log("DSL,GSL,KER", "sen_weekly", "SEN weekly import parity structure (Estructura de Precios de los Combustibles, CAP)", "web search: Estructura de Precios de los Combustibles Honduras; sen.hn resumen-precio pages", "not found",
    "structure referenced by CREE CBG 2024 and ODS PIEG but not posted online; on manual list")
log("DSL,GSL,KER", "other_press_laprensa", "La Prensa 29 May 2024 article with SEN structure", S["HON-006"]["url"], "value found", "PPI, tax, wholesale margin, freight and retail margin for superior, regular, diesel and kerosene, week 27 May to 2 Jun 2024")
log("DSL,GSL,KER", "other_press_elheraldo", "El Heraldo 29 May 2024 article (same structure)", S["HON-007"]["url"], "value found", "same figures as La Prensa")
log("DSL,GSL,KER", "other_unah_blog", "UNAH blog margin ranges", S["HON-008"]["url"], "value found", "ranges only; cross-check")
log("DSL,GSL,KER,FOI,LPG", "sen_annual", "SEN annual hydrocarbon report 2024", S["HON-005"]["url"], "value found", "volume and CIF by product; no margins")
log("COA,COK,NGS", "sen_annual", "SEN annual hydrocarbon report 2024", S["HON-005"]["url"], "no value", "petroleum products only")
log("DSL,GSL,KER,FOI,LPG", "other_sen_monthly", "SEN monthly hydrocarbon reports Jan to Dec 2024 (weekly retail price charts)", "https://sen.hn/wp-content/uploads/2025/02/IEMCHB-12-2024.pdf (and 11 others)", "no value",
    "weekly retail prices with tax only; May to July charts show about twice the pump price (apparently two cities summed); not used")
log("FOI", "cree", "CREE quarterly tariff adjustment reports (real bunker price)", "https://www.cree.gob.hn/wp-content/uploads/2019/02/ (6 reports)", "value found", "12 monthly real bunker prices 2024")
log("DSL", "cree", "CREE quarterly tariff adjustment reports and CBG 2024 (diesel)", S["HON-015"]["url"], "value found", "quarterly forecast diesel for generation; no real diesel price")
log("COA,COK", "cree", "CREE tariff adjustment reports and CBG 2024 review (coal, petcoke)", S["HON-015"]["url"], "no value", "only bunker and diesel prices; Becosa appears only in plant factor tables")
log("NGS,GSL,KER,LPG", "cree", "CREE tariff adjustment reports", "https://www.cree.gob.hn/wp-content/uploads/2019/02/", "no value", "not covered")
log(ALL, "enee_ods_cnd", "CND/ODS market and operation reports (Oracle APEX)", "https://appcnd.enee.hn:3200/odsprd/f?p=110:4:::::p4_id:41", "timeout", "connection to port 3200 failed after 21 s; on manual list")
log("COA,NGS,FOI,DSL", "enee_ods_cnd", "ODS PIEG 2026-2035 fuel price chain", S["HON-016"]["url"], "value found",
    "coal 5% local cost and freight; LNG chain; bunker and diesel internacion 2024")
log("COK,GSL,KER,LPG", "enee_ods_cnd", "ODS PIEG 2026-2035 fuel price chain", S["HON-016"]["url"], "no value", "no petcoke-specific, gasoline or kerosene chain")
log("COA,COK,NGS", "enee_ods_cnd", "ODS PIEG 2024-2033 approved", S["HON-018"]["url"], "value found", "earlier chain (LNG shipping 0.5 USD/MMBtu); cross-check only")
log("COA,COK,FOI,DSL", "enee_ods_cnd", "ENEE statistical bulletin 2024 (api-documentos)", "https://api-documentos.enee.hn/1627/Boletin-estadistico-agosto-2024.pdf", "not found", "HTTP 404 on links listed on enee.hn; on manual list")
log("NGS,COA,COK,FOI,LPG", "gaceta_lng", "La Gaceta official gazette", "https://gaceta.iaip.gob.hn/", "timeout", "connection failed after 21 s; on manual list")
log("DSL,GSL,KER", "gaceta_lng", "La Gaceta (acuerdos fixing distribution margins)", "https://gaceta.iaip.gob.hn/", "timeout", "connection failed")
log("DSL,GSL,KER", "other_tsc_leyes", "Tribunal Superior de Cuentas legal database (SEN margin acuerdos)", "https://www.tsc.gob.hn/web/leyes/", "blocked HTTP 403", "not retried")
log("NGS", "other_honducompras", "ENEE tender LP-100-080-2023 bases (LNG reference price)", "http://h1.honducompras.gob.hn/Docs/Lic33ENEE%20LP-100-080-2023200-PliegooTerminosdeReferencia.pdf", "no value",
    "only Henry Hub indexation reference (2.18 USD/MMBtu, June 2023); no delivered LNG price")
log("NGS", "other_press_lng", "Web search for 2024 LNG supply to Honduras", "web search: Honduras licitacion gas natural licuado GNL ENEE 2024", "no value", "first LNG cargo reported in 2026; no 2024 supply")
log("DSL,GSL,KER,FOI,LPG", "bch", "BCH Informe de Combustibles a diciembre 2024 and 2025", S["HON-002"]["url"], "value found", "CIF value and volume by product 2022 to 2025; generators' bunker")
log("COA,COK,NGS", "bch", "BCH Informe de Combustibles a diciembre 2024", S["HON-001"]["url"], "no value", "petroleum products only; footnote mentions petcoke plants")
log("DSL,GSL,KER,FOI,LPG,COA,COK", "bch", "BCH December fuel reports 2019 to 2022", "https://www.bch.hn/estadisticos/EME/Informe%20Combustibles/Informe%20de%20Combustibles%20a%20diciembre%202022.pdf", "not found", "HTTP 404 for 2019 to 2022")
log("COA,COK", "customs_national", "Aduanas Honduras statistics", "https://www.aduanas.gob.hn/estadisticas/", "blocked HTTP 403", "on manual list")
log("COA,COK", "customs_national", "BCH fuel import report (customs SARAH based)", S["HON-001"]["url"], "no value", "no coal or petcoke lines")
log("NGS", "customs_national", "BCH fuel import report", S["HON-001"]["url"], "no value", "no natural gas imports in 2024")
log("DSL,GSL,KER,FOI,LPG", "customs_national", "BCH fuel import report (SARAH customs data)", S["HON-002"]["url"], "value found", "same as bch lead")
log("COA,COK", "other_sieca", "SIECA regional trade statistics", "https://estadisticas.sieca.int/", "blocked HTTP 403", "on manual list")
log("COA,COK", "comtrade", "UN Comtrade preview 2024 HS 6-digit", S["HON-019"]["url"], "value found", "270112 27.5 kt 134.00 USD/t; 271311 185.2 kt 81.56 USD/t")
log("NGS", "comtrade", "UN Comtrade preview 2024 HS 6-digit", S["HON-019"]["url"], "no value", "no 271111 or 271121 imports")
log("DSL,GSL,KER,FOI", "comtrade", "UN Comtrade preview 2024 HS 6-digit", S["HON-019"]["url"], "no value",
    "271012 and 271019 mix products (gasoline with other light oils; diesel with fuel oil); national data used")
log("LPG", "comtrade", "UN Comtrade preview 2024 HS 271112", S["HON-019"]["url"], "value found", "654.26 USD/t; not used (national data used)")
log("COA,COK", "comtrade", "UN Comtrade preview 2018 to 2023", CT.format(y="2018..2023", c="270112,271311"), "value found", "history; 2025 not available (HTTP 429 then empty)")
log(ALL, "energy_balance", "SEN Balance Energetico Nacional 2024", S["HON-028"]["url"], "no value", "quantities and implied factors only; no prices; basis not stated")
log(ALL, "energy_balance", "OLADE energy statistics manual (calorific basis)", "https://biblioteca.olade.org/opac-tmpl/Documentos/old0381.pdf", "blocked HTTP 403", "on manual list")

# ---------------------------------------------------------------- manual list
M = [
    dict(url="https://appcnd.enee.hn:3200/odsprd/f?p=110:4:::::p4_id:132", title="CND Bases SDDP (operation planning database)", publisher="ODS / CND Honduras",
         should_hold="plant fuel prices and variable costs used in dispatch planning, including Becosa coal and petcoke", rows_it_closes="COA DIST_COA; COK DIST_COK (generator delivered)",
         why_needed="only operator source for delivered coal and petcoke cost", how_failed="timeout (port 3200 connection refused)", save_as="HON_cnd_bases_sddp_2024.zip", weight_rank=1),
    dict(url="https://appcnd.enee.hn:3200/odsprd/f?p=110:4:::::p4_id:41", title="CND Informe anual de operacion del mercado 2024", publisher="ODS / CND Honduras",
         should_hold="declared variable costs and fuel costs by plant 2024", rows_it_closes="COA, COK, FOI, DSL generator delivered", why_needed="actual 2024 delivered fuel costs by plant",
         how_failed="timeout (port 3200)", save_as="HON_cnd_informe_anual_mercado_2024.pdf", weight_rank=1),
    dict(url="https://api-documentos.enee.hn/1627/Boletin-estadistico-agosto-2024.pdf", title="ENEE Boletin estadistico 2024 (monthly, and December 2024 if issued)", publisher="ENEE",
         should_hold="generation and fuel consumption by plant and fuel, possibly fuel cost", rows_it_closes="COA, COK generator delivered (if costs given)", why_needed="local operator data on coal/petcoke plant",
         how_failed="HTTP 404 for links listed on enee.hn", save_as="HON_enee_boletin_estadistico_2024.pdf", weight_rank=1),
    dict(url="https://www.aduanas.gob.hn/estadisticas/", title="Aduanas Honduras import statistics by tariff line 2024", publisher="Administracion Aduanera de Honduras",
         should_hold="CIF value and kg for SAC 2701.12, 2713.11 in 2024", rows_it_closes="COA DIST_COA; COK DIST_COK (national customs CIF)", why_needed="national customs source to replace Comtrade",
         how_failed="HTTP 403", save_as="HON_aduanas_imports_27_2024.xlsx", weight_rank=1),
    dict(url="https://estadisticas.sieca.int/", title="SIECA trade statistics, Honduras imports SAC 2701 and 2713, 2024", publisher="SIECA",
         should_hold="CIF value and weight by SAC line", rows_it_closes="COA, COK import CIF (cross-check)", why_needed="second customs-based source", how_failed="HTTP 403",
         save_as="HON_sieca_imports_27_2024.xlsx", weight_rank=2),
    dict(url="https://gaceta.iaip.gob.hn/", title="La Gaceta: acuerdos on fuel distribution margins and any LNG supply contract", publisher="Empresa Nacional de Artes Graficas (La Gaceta)",
         should_hold="SEN acuerdos fixing wholesale, freight and retail margins; LNG supply or regasification contracts", rows_it_closes="NGS DIST_NGS; DSL, GSL, KER margins",
         why_needed="official legal source for margins and gas supply", how_failed="timeout", save_as="HON_gaceta_margins_lng.pdf", weight_rank=3),
    dict(url="https://biblioteca.olade.org/opac-tmpl/Documentos/old0381.pdf", title="OLADE Energy Statistics Manual", publisher="OLADE",
         should_hold="calorific basis (net) and conversion factors used in SIELAC", rows_it_closes="calorific_HON.csv second source", why_needed="SEN balance does not state basis",
         how_failed="HTTP 403", save_as="OLADE_energy_statistics_manual.pdf", weight_rank=3),
    dict(url="https://sen.hn/resumen-precio/", title="SEN/DGHB weekly Estructura de Precios de los Combustibles (CAP), all weeks of 2024", publisher="SEN, Direccion General de Hidrocarburos y Biocombustibles",
         should_hold="weekly PPI (FOB, freight, insurance, importer costs), wholesale margin, freight, retail margin, tax by fuel", rows_it_closes="DSL, GSL, KER wholesale import parity and margins (full year)",
         why_needed="only one week of the structure is public (via press)", how_failed="not posted online (not found)", save_as="HON_sen_estructura_precios_2024.pdf", weight_rank=5),
    dict(url="https://mem.gob.gt/wp-json/wp/v2/media?search=CCHAC&per_page=100", title="CCHAC-SICA weekly bulletins 9, 14, 22 and 32 to 52 of 2024", publisher="CCHAC-SICA (copies hosted by MEM Guatemala)",
         should_hold="Honduras pre-tax and tax for gasoline and diesel; LPG structure", rows_it_closes="DSL, GSL final consumer pre-tax (full year); LPG",
         why_needed="SEN copy ends on 3 Aug 2024", how_failed="HTTP 403", save_as="CCHAC_2024_bulletins_missing.zip", weight_rank=5),
]

# ---------------------------------------------------------------- write
def wcsv(name, head, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=head)
        w.writeheader()
        for r in rows:
            w.writerow(r)


wcsv("prices_HON.csv", HEAD, P)
wcsv("history_HON.csv", HEAD, H)
wcsv("sources_HON.csv", ["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "rows_and_constants_supported"],
     [S[k] for k in sorted(S)])
wcsv("constants_HON.csv", ["name", "value", "unit", "source_id", "page_or_table", "derivation"],
     [dict(zip(["name", "value", "unit", "source_id", "page_or_table", "derivation"], c)) for c in C])
wcsv("search_log_HON.csv", ["country", "fuel", "lead_id", "lead", "url_or_query", "date", "result", "detail"], L)
wcsv("manual_HON.csv", ["url", "title", "publisher", "should_hold", "rows_it_closes", "why_needed", "how_failed", "save_as", "weight_rank"],
     sorted(M, key=lambda m: m["weight_rank"]))
wcsv("calorific_HON.csv", ["country", "balance", "publisher", "url", "net_or_gross", "factor_NGS", "factor_COA", "factor_COK", "factor_FOI",
                          "factor_units", "page_or_table", "source_id"], CAL)
for r in P:
    print(r["fuel"], r["price_point"], r["price_as_published"], r["unit"], r["value_usd_per_gj"], r["evidence_class"], r["source_id"][:30])
print(len(P), "price rows;", len(H), "history rows;", len(S), "sources;", len(L), "log rows;", len(M), "manual")
