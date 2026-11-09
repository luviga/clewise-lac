"""Build the Guatemala output CSVs of job LAC_LOCAL_PRICES 20261109T085226Z.

Usage: py -I gua_build.py <downloads GUA folder> <country GUA output folder>

Reads the files saved in downloads/GUA (Banguat rates and trade files, UN Comtrade
JSON, parsed MEM price structures, MEM other-fuel prices) and writes:
prices_GUA.csv, history_GUA.csv, sources_GUA.csv, constants_GUA.csv,
calorific_GUA.csv. The search log and manual list are written by gua_logs.py.
All arithmetic is done here so every derivation string matches the value.
"""
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

import openpyxl

RET = '2026-11-09'
NS = '{http://www.banguat.gob.gt/variables/ws/}'

# Shared constants (sourced by the main session; used by name only)
L_PER_USGAL = 3.785411784
GJ_PER_MMBTU = 1.055056
UN_GAL_PER_T = {'GSL': 357, 'DSL': 304, 'JET': 326, 'KER': 326, 'FOI': 278, 'LPG': 489, 'AVG': 362}
IPCC_NCV = {'GSL': 44.3, 'DSL': 43.0, 'JET': 44.1, 'KER': 43.8, 'FOI': 40.4, 'LPG': 47.3, 'AVG': 44.3,
            'CRU': 42.3, 'COK': 32.5, 'COA_OTHER_BITUMINOUS': 25.8, 'NGS': 48.0}

# Country constants read from local publishers (see constants_GUA.csv)
GUA_COA_NAR_MMBTU_PER_T = 23.81   # PEG-5 bases, Colombia 6000 kcal/kg NAR
GUA_COK_NAR_MMBTU_PER_T = 29.76   # PEG-5 bases, USGC petcoke 7500 kcal/kg NAR
GUA_KG_PER_LB = 0.454             # Decreto 74-98 art. 2
GUA_LB_PER_LPG_CYLINDER = 25      # MEM structure slide 'CILINDRO DE 25 LIBRAS'
GUA_IVA_RATE = 0.12               # MEM structure slides 'IMPUESTO AL VALOR AGREGADO 12%'
GUA_IDP_KER = 0.50                # Decreto 74-98 art. 1 (Kerosina Q0.50 per US gallon)
GUA_IDP_FOI = 0.0                 # MEM bunker structure slides 2024 (IDP Q0.000)

MESES = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7,
         'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
MES_EN = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

PRICE_HDR = ['country', 'fuel', 'model_code', 'price_point', 'year', 'fob', 'freight', 'insurance', 'port',
             'importer_terminal_margin', 'wholesale_margin', 'inland_freight', 'retail_margin',
             'price_as_published', 'currency', 'unit', 'period', 'months_covered', 'tax_treatment',
             'calorific_basis', 'exchange_rate', 'exchange_rate_constant', 'conversion_constants',
             'value_usd_per_gj', 'evidence_class', 'source_id', 'page_or_table', 'downloaded_file',
             'derivation', 'notes']


def r4(x):
    return float('%.4f' % x)


def fx_mean(path, year):
    root = ET.parse(path).getroot()
    vals = [float(v.find(NS + 'venta').text) for v in root.iter(NS + 'Var')
            if v.find(NS + 'fecha').text.endswith(str(year))]
    return round(sum(vals) / len(vals), 5), len(vals)


def banguat_lines(path):
    out = {}
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    for r in ws.iter_rows(values_only=True):
        cells = [c for c in r if c is not None]
        if not cells:
            continue
        code = str(cells[0]).strip().replace(' ', '')
        if re.fullmatch(r'27\d{8}', code):
            vals = []
            for c in cells[1:]:
                try:
                    vals.append(float(c))
                except (TypeError, ValueError):
                    vals.append(0.0)
            out[code] = (vals[0], vals[1])
    return out


def comtrade(path):
    d = json.load(open(path, encoding='utf-8'))
    return {str(r['cmdCode']): r for r in d['data']}


def structures(path):
    """Mean of each component per slide over the 2024 weeks (equal weight per week)."""
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    by = defaultdict(lambda: defaultdict(dict))
    files = defaultdict(dict)
    for r in rows:
        if r['component'] == 'ERROR' or r['value'] == '':
            continue
        m = re.search(r'al-(\d{2})-([a-z]+)-(\d{4})', r['file'])
        wk = '%s-%02d-%s' % (m.group(3), MESES[m.group(2)], m.group(1))
        if wk[:4] != '2024':
            continue
        if wk in files[r['fuel']] and files[r['fuel']][wk] != r['file']:
            continue
        files[r['fuel']][wk] = r['file']
        by[r['fuel']][wk][r['component']] = float(r['value'])
    res = {}
    for fuel, wks in by.items():
        weeks = sorted(wks)
        comps = sorted({c for w in weeks for c in wks[w]})
        mean = {c: sum(wks[w].get(c, 0.0) for w in weeks) / len(weeks) for c in comps}
        res[fuel] = dict(weeks=weeks, mean=mean, files=sorted(set(files[fuel].values())))
    return res


def other_fuels(path):
    """MEM 'Precios promedio de combustibles a consumidor final, ciudad capital' sheet X-MES-AS."""
    import warnings
    warnings.filterwarnings('ignore')
    ws = openpyxl.load_workbook(path, data_only=True)['X-MES-AS']
    out = {}
    year = None
    for r in ws.iter_rows(values_only=True):
        c = [x for x in r if x is not None]
        if not c:
            continue
        s = str(c[0])
        m = re.match(r'A.O (\d{4})', s)
        if m:
            year = int(m.group(1))
            out[year] = {}
            continue
        if year and s.strip().upper() in [k.upper() for k in MESES] and len(c) >= 3:
            out[year][MESES[s.strip().lower()]] = {'KER': float(c[1]), 'FOI': float(c[2])}
        if year and s.strip() == 'Promedio' and len(c) >= 3:
            out[year]['avg'] = {'KER': float(c[1]), 'FOI': float(c[2])}
    return out


def main(dl, outdir):
    rel = lambda p: 'GUA/' + p
    # ---------------- exchange rates
    fx = {}
    for y in range(2018, 2026):
        fx[y] = fx_mean(os.path.join(dl, 'banguat_TipoCambioRango_%d.xml' % y), y)
    FX = fx[2024][0]

    # ---------------- sources
    S = []

    def src(url, title, publisher, date, fn, page, supports):
        sid = 'GUA-%03d' % (len(S) + 1)
        S.append(dict(id=sid, url=url, title=title, publisher=publisher, date=date, retrieval_date=RET,
                      downloaded_file=rel(fn), page_or_table=page, rows_and_constants_supported=supports))
        return sid

    SOAP = 'https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx?op=TipoCambioRango'
    s_fx = src(SOAP, 'Tipo de cambio de referencia, web service TipoCambioRango, 01/01/2024 to 31/12/2024',
               'Banco de Guatemala', '2024 daily series', 'banguat_TipoCambioRango_2024.xml',
               'SOAP 1.1 POST to https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx, method TipoCambioRango, '
               'fechainit 01/01/2024, fechafin 31/12/2024; all <Var> elements (moneda 2, US dollar), field venta',
               'GUA_FX_2024; every GTQ row in prices_GUA.csv')
    s_kf24 = src('https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/2024/CG/KF-103_2024.xlsx',
                 'Importaciones realizadas por partida, Comercio General, ano 2024 (valor en US dolares y volumen en kilogramos)',
                 'Banco de Guatemala', '2024 annual (file as published 2026)', 'banguat/CG_KF-103_2024.xlsx',
                 'sheet Impo, rows 2701120000, 2701190000, 2713110000, 2710192200, 2710192100, 2710123000, 2710191200, 2711120000, column Total Anual Valor and Volumen',
                 'COA, COK, FOI, DSL, GSL, KER, LPG import CIF 2024')
    s_c4 = src('https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/CG/2024/ceie04.htm',
               'Cuadro 4 Guatemala: valor (CIF), volumen y precio medio de las importaciones, clasificacion CUODE, comercio general',
               'Banco de Guatemala', 'January 2024 and January 2025', 'banguat/CG_2024_ceie04.htm',
               'title (VALOR (CIF)) and footnote 1/ (hulla bituminosa January 2024 US$5,722.0 thousand, 48,213.4 thousand kg)',
               'confirms that Banguat import values are CIF; the footnote equals the January 2024 value of line 2701120000 in GUA-002')
    s_kf116 = src('https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/2024/CG/Origen/KF-116_2024.xlsx',
                  'Importaciones realizadas por partida y pais origen, Comercio General, ano 2024',
                  'Banco de Guatemala', '2024 annual', 'banguat/CG_Origen_KF-116_2024.xlsx',
                  'sheet Impo, lines 2701120000 (Colombia only), 2701190000 (United States only), 2713110000 (United States, Mexico)',
                  'COA and COK origin (notes)')
    CT_URL = ('https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=320&period=2024&partnerCode=0&flowCode=M'
              '&cmdCode=2701,2713,2709,2710,2711,270112,270119,271311,271312,271012,271019,271111,271112,271113,271119,271121,271020')
    s_ct = src(CT_URL, 'UN Comtrade public preview API, Guatemala imports 2024, HS 2701, 2709, 2710, 2711, 2713 and 6-digit lines',
               'United Nations Statistics Division (UN Comtrade)', '2024 annual', 'comtrade_GUA_2024_M.json',
               'data records cmdCode 270112, 271311 (cifvalue, netWgt); no record for 271111 or 271121',
               'COA, COK import CIF (international customs); NGS no imports')
    s_peg5 = src('https://peg-5-2025.com.gt/static/pdf/3.%20Bases%20de%20Licitaci%C3%B3n%20PEG-5%20CNEE-108-2025.pdf',
                 'Bases de Licitacion PEG-5-2025 (approved by CNEE resolution CNEE-108-2025)',
                 'Distribuidoras EEGSA, DEOCSA, DEORSA; approved by Comision Nacional de Energia Electrica (CNEE)', '2025',
                 'cnee/PEG5_Bases_CNEE-108-2025.pdf',
                 'numeral 5.3.3, pages 28 to 31 (CTUNG considerations: coal 23.81 MMBTU/TM, petroleum coke 29.76 MMBTU/TM; Fo table; FAGN, FGSC; CITT coal 23.33 US$/MWh, petcoke 18.76 US$/MWh)',
                 'GUA_COA_NAR_MMBTU_PER_T; GUA_COK_NAR_MMBTU_PER_T; NGS ASSUMPTION check; calorific_GUA.csv')
    s_cost = src('https://mem.gob.gt/wp-content/uploads/2025/01/COSTO-IMPORTACION-HIDROCARBUROS-2024-12.xlsx',
                 'Costo de la importacion de productos derivados de petroleo, mensual (unidad USD), 2010 to December 2024',
                 'Ministerio de Energia y Minas, Direccion General de Hidrocarburos', 'January 2025',
                 'mem_imports/COSTO-IMPORTACION-HIDROCARBUROS-2024-12.xlsx',
                 'sheet COSTO IMPORTACION, rows 2024-01 to 2024-12, columns Bunker C o fuel oil, Kerosina, Petcoke',
                 'notes only (FOI, KER, COK cross-checks)')
    s_vol = src('https://mem.gob.gt/wp-content/uploads/2025/01/IMPORTACION-HIDROCARBUROS-VOLUMEN-2024-12.xlsx',
                'Importacion de productos derivados de petroleo, mensual (unidad barril de 42 galones), 2001 to December 2024',
                'Ministerio de Energia y Minas, Direccion General de Hidrocarburos', 'January 2025',
                'mem_imports/IMPORTACION-HIDROCARBUROS-VOLUMEN-2024-12.xlsx',
                'sheet IMPORTACION, rows 2024-01 to 2024-12, columns Bunker, Kerosina, Petcoke',
                'notes only (FOI, KER, COK cross-checks)')
    s_oth = src('https://mem.gob.gt/wp-content/uploads/2024/11/PRECIOS-OTROS-COMBUSTIBLES-MENSUALES-OCTUBRE-2024.xlsx',
                'Precios promedio de combustibles a consumidor final, ciudad capital (kerosina, bunker, av gas, av jet, GLP), monthly',
                'Ministerio de Energia y Minas, Direccion General de Hidrocarburos, Depto. de Analisis Economico', 'November 2024',
                'mem_other/PRECIOS-OTROS-COMBUSTIBLES-MENSUALES-OCTUBRE-2024.xlsx',
                'sheet X-MES-AS, tables ANO 2018 to ANO 2024 (2024: January to October), columns KEROSINA and BUNKER, Q./galon',
                'KER and FOI final consumer pre-tax 2024 and history 2018 to 2024')
    s_law = src('https://docs.costa-rica.justia.com/nacionales/modificaciones/decreto-no-74-1998-nov-17-1998.pdf',
                'Decreto numero 74-98 del Congreso de la Republica (reforma articulo 13 del Decreto 38-92, Ley del Impuesto a la Distribucion de Petroleo Crudo y Combustibles Derivados del Petroleo), Diario de Centro America 16 December 1998',
                'Congreso de la Republica de Guatemala (Diario de Centro America, scan hosted by Justia)', '1998-11-17',
                'law/decreto-no-74-1998.pdf',
                'page 1, Articulo 1 (Kerosina Q0.50 per US gallon) and Articulo 2 (libra = 0.454 kg); scanned page read from image',
                'GUA_IDP_KER; GUA_KG_PER_LB')
    s_sac = src('https://www.eaduana.com/aranceles/arancel-centroamericano-de-importacion?page=70',
                'Arancel Centroamericano de Importacion (SAC, seventh amendment), chapter 27 lines 2709 to 2710.19.22',
                'eAduana (reproduction of the SIECA Arancel Centroamericano de Importacion)', 'page updated 2025-10-14',
                'nomenclature/eaduana_arancel_page70.html',
                'lines 2710.12.20 Gasolina de aviacion, 2710.12.30 Las demas gasolinas, 2710.19.11 Keroseno para motores de reaccion, 2710.19.12 Los demas kerosenos, 2710.19.21 Diesel oil (Gas oil), 2710.19.22 Fuel oil No. 6 (Bunker C)',
                'meaning of the 10-digit lines used for FOI, DSL, GSL, KER in GUA-002')
    s_be10 = src('https://www.mem.gob.gt/wp-content/uploads/2012/06/INFORME_BALANCE_ENERGETICO.pdf',
                 'Balance Energetico 2010', 'Ministerio de Energia y Minas, Direccion General de Energia', '2012-06',
                 'balance/INFORME_BALANCE_ENERGETICO_2010.pdf',
                 'page 8, table Abreviaturas utilizadas en el balance / Factores de Conversion a Barriles Equivalentes de Petroleo (BEP)',
                 'calorific_GUA.csv')
    s_be24 = src('https://mem.gob.gt/wp-content/uploads/2025/07/BALANCE-ENERGETICO-2024.pdf',
                 'Balance Energetico 2024', 'Ministerio de Energia y Minas', '2025-07', 'balance/BALANCE-ENERGETICO-2024.pdf',
                 'page 4 (unit kBEP); tables 1 to 7; no conversion factors and no statement of net or gross basis',
                 'calorific_GUA.csv')
    s_kfh = {}
    for y in [2018, 2019, 2020, 2021, 2022, 2023, 2025]:
        s_kfh[y] = src('https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/%d/CG/KF-103_%d.xlsx' % (y, y),
                       'Importaciones realizadas por partida, Comercio General, ano %d' % y, 'Banco de Guatemala',
                       '%d annual' % y, 'banguat/CG_KF-103_%d.xlsx' % y,
                       'sheet Impo, Total Anual Valor and Volumen of the same lines as GUA-002', 'history_GUA.csv %d' % y)
    s_kfh[2024] = s_kf24
    s_fxh = {}
    for y in [2018, 2019, 2020, 2021, 2022, 2023, 2025]:
        s_fxh[y] = src(SOAP, 'Tipo de cambio de referencia, web service TipoCambioRango, %d' % y, 'Banco de Guatemala',
                       '%d daily series' % y, 'banguat_TipoCambioRango_%d.xml' % y,
                       'SOAP 1.1 POST, method TipoCambioRango, fechainit 01/01/%d, fechafin 31/12/%d, field venta' % (y, y),
                       'GUA_FX_%d' % y)
    s_fxh[2024] = s_fx
    st = structures(os.path.join(dl, 'estructuras_parsed.csv'))
    allfiles = sorted({f for v in st.values() for f in v['files']})
    urls = {os.path.basename(u.strip()): u.strip() for u in open(os.path.join(dl, 'estructuras_urls.txt'))}
    s_struct = []
    for f in allfiles:
        m = re.search(r'al-(\d{2})-([a-z]+)-(\d{4})', f)
        d = '%s-%02d-%s' % (m.group(3), MESES[m.group(2)], m.group(1))
        s_struct.append(src(urls[f], 'Estructuras de Precios referenciales al %s (gasolina superior, regular, diesel, GLP cilindro 25 lb, bunker, GLP automotriz)' % d,
                            'Ministerio de Energia y Minas, Direccion General de Hidrocarburos, Depto. de Analisis Economico',
                            d, 'estructuras/' + f, 'slides 1 to 6 (one per product), Quetzales column',
                            'DSL, GSL, LPG, FOI weekly components 2024'))
    struct_ids = ';'.join(s_struct)
    struct_first, struct_last = s_struct[0], s_struct[-1]

    # ---------------- constants
    C = []

    def const(name, value, unit, sid, page, deriv):
        C.append(dict(name=name, value=value, unit=unit, source_id=sid, page_or_table=page, derivation=deriv))

    const('GUA_FX_2024', '%.5f' % FX, 'GTQ per USD', s_fx, S[0]['page_or_table'],
          'mean of %d daily reference rates 01/01/2024 to 31/12/2024 (venta = compra every day), computed by country/GUA/gua_fx.py' % fx[2024][1])
    for y in [2018, 2019, 2020, 2021, 2022, 2023, 2025]:
        const('GUA_FX_%d' % y, '%.5f' % fx[y][0], 'GTQ per USD', s_fxh[y], 'TipoCambioRango %d, field venta' % y,
              'mean of %d daily reference rates of %d, computed by country/GUA/gua_fx.py' % (fx[y][1], y))
    const('GUA_COA_NAR_MMBTU_PER_T', '23.81', 'MMBtu per tonne, net as received (Colombia 6000 kcal/kg NAR)', s_peg5,
          'numeral 5.3.3 page 29 and Fo table page 30', 'published; equals 25.1209 GJ/t with GJ_PER_MMBTU 1.055056')
    const('GUA_COK_NAR_MMBTU_PER_T', '29.76', 'MMBtu per tonne, net as received (USGC petcoke 7500 kcal/kg NAR)', s_peg5,
          'numeral 5.3.3 page 29 and Fo table page 30', 'published; equals 31.3985 GJ/t with GJ_PER_MMBTU 1.055056')
    const('GUA_KG_PER_LB', '0.454', 'kg per libra', s_law, 'Articulo 2 (reforma articulo 48 Decreto 109-97)',
          'published (cuatrocientos cincuenta y cuatro milesimas de kilogramo); read from scanned image')
    const('GUA_LB_PER_LPG_CYLINDER', '25', 'libras per residential LPG cylinder', struct_first,
          'slide 4 title ESTRUCTURA DEL PRECIO DEL GAS LICUADO DE PETROLEO, CILINDRO DE 25 LIBRAS', 'published')
    const('GUA_IVA_RATE', '0.12', 'fraction of price net of IDP', struct_first,
          'every slide, label IMPUESTO AL VALOR AGREGADO 12%',
          'published; checked: superior 3 Jan 2024 IVA 2.76 = 0.12 x (30.47 - 4.70 - 2.76)')
    const('GUA_IDP_KER', '0.50', 'GTQ per US gallon', s_law, 'Articulo 1 (Articulo 13 Tasas de Impuesto: Kerosina Q 0.50)',
          'published 1998 rate; later reforms changed the gasoline and fuel oil rates; no later kerosene rate found')
    const('GUA_IDP_FOI_2024', '0.000', 'GTQ per US gallon', struct_first, 'slide 5 bunker, IMPUESTO A LA DISTRIBUCION Q0.000',
          'published in every 2024 bunker structure')

    # ---------------- prices
    P = []

    def price(**k):
        row = {h: '' for h in PRICE_HDR}
        row.update(country='Guatemala', year=2024)
        row.update(k)
        P.append(row)

    bg = banguat_lines(os.path.join(dl, 'banguat/CG_KF-103_2024.xlsx'))
    ct = comtrade(os.path.join(dl, 'comtrade_GUA_2024_M.json'))
    coa_gj_t = GUA_COA_NAR_MMBTU_PER_T * GJ_PER_MMBTU
    cok_gj_t = GUA_COK_NAR_MMBTU_PER_T * GJ_PER_MMBTU

    def bg_row(fuel, code, model, gj_t, conv, basis, notes, gj_t_text):
        v, kg = bg[code]
        upt = v / kg * 1000
        val = upt / gj_t
        price(fuel=fuel, model_code=model, price_point='import CIF', price_as_published=r4(upt), currency='USD',
              unit='USD/t', period='2024 calendar year', months_covered='1-12', tax_treatment='CIF, before import duties and taxes',
              calorific_basis='not stated', conversion_constants=conv, value_usd_per_gj=r4(val),
              evidence_class='local customs or statistics', source_id='%s;%s;%s' % (s_kf24, s_c4, s_sac) if fuel not in ('COA', 'COK') else '%s;%s;%s' % (s_kf24, s_c4, s_kf116),
              page_or_table='KF-103_2024 sheet Impo line %s, Total Anual' % code, downloaded_file=rel('banguat/CG_KF-103_2024.xlsx'),
              derivation='%.0f USD / %.0f kg x 1000 = %.4f USD/t; / %s = %.4f USD/GJ' % (v, kg, upt, gj_t_text, val),
              notes=notes)
        return upt, val

    # COA
    coa_upt, coa_val = bg_row('COA', '2701120000', 'DIST_COA', coa_gj_t,
                              'GUA_COA_NAR_MMBTU_PER_T;GJ_PER_MMBTU', 'net',
                              'SAC 2701.12 bituminous coal, all from Colombia (GUA-004). Customs gives no calorific value; the factor is the PEG-5 evaluation value for Colombia 6000 kcal/kg NAR (net as received). With IPCC_NCV_COA_OTHER_BITUMINOUS 25.8 GJ/t the value would be %.4f USD/GJ. Line 2701.19 (other coal, from the United States) adds 25945614 USD for 194997532 kg (133.06 USD/t); all 2701 lines together give %.2f USD/t. No published generator-delivered coal price: AMM publishes plant variable costs in US$/MWh only, and PEG-5 publishes local internment and transport for coal as 23.33 US$/MWh of output (not per tonne).' % (
                                  bg['2701120000'][0] / bg['2701120000'][1] * 1000 / 25.8,
                                  sum(bg[c][0] for c in ('2701110000', '2701120000', '2701190000')) / sum(bg[c][1] for c in ('2701110000', '2701120000', '2701190000')) * 1000),
                              '(23.81 MMBtu/t GUA_COA_NAR_MMBTU_PER_T x 1.055056 GJ/MMBtu GJ_PER_MMBTU = 25.1209 GJ/t)')
    P[-1]['calorific_basis'] = 'not stated'
    r = ct['270112']
    upt = r['cifvalue'] / r['netWgt'] * 1000
    price(fuel='COA', model_code='DIST_COA', price_point='import CIF', price_as_published=r4(upt), currency='USD', unit='USD/t',
          period='2024 calendar year', months_covered='1-12', tax_treatment='CIF', calorific_basis='not stated',
          conversion_constants='GUA_COA_NAR_MMBTU_PER_T;GJ_PER_MMBTU', value_usd_per_gj=r4(upt / coa_gj_t),
          evidence_class='international customs (Comtrade)', source_id=s_ct, page_or_table='cmdCode 270112, flowCode M, partnerCode 0',
          downloaded_file=rel('comtrade_GUA_2024_M.json'),
          derivation='cifvalue %.0f USD / netWgt %.0f kg x 1000 = %.4f USD/t; / 25.1209 GJ/t (23.81 MMBtu/t GUA_COA_NAR_MMBTU_PER_T x 1.055056 GJ_PER_MMBTU) = %.4f USD/GJ' % (r['cifvalue'], r['netWgt'], upt, upt / coa_gj_t),
          notes='Second source for the Banguat value; qtyUnitAbbr empty, isQtyEstimated %s, isNetWgtEstimated %s.' % (r['isQtyEstimated'], r['isNetWgtEstimated']))
    # COK
    bg_row('COK', '2713110000', 'DIST_COK', cok_gj_t, 'GUA_COK_NAR_MMBTU_PER_T;GJ_PER_MMBTU', 'net',
           'SAC 2713.11 petroleum coke not calcined, 909983110 kg from the United States and 4184856 kg from Mexico (GUA-004). Factor is the PEG-5 evaluation value for USGC petcoke 7500 kcal/kg NAR (net as received); with IPCC_NCV_COK 32.5 GJ/t the value would be %.4f USD/GJ. MEM DGH monthly import cost and volume tables (GUA-007, GUA-008) give 298199093 USD for 4898556 units labelled barrels in 2024, with monthly unit values from 14.59 to 146.95, inconsistent with customs; not used. No published delivered price to cement or industry.' % (
               bg['2713110000'][0] / bg['2713110000'][1] * 1000 / 32.5),
           '(29.76 MMBtu/t GUA_COK_NAR_MMBTU_PER_T x 1.055056 GJ/MMBtu GJ_PER_MMBTU = 31.3985 GJ/t)')
    r = ct['271311']
    upt = r['cifvalue'] / r['netWgt'] * 1000
    price(fuel='COK', model_code='DIST_COK', price_point='import CIF', price_as_published=r4(upt), currency='USD', unit='USD/t',
          period='2024 calendar year', months_covered='1-12', tax_treatment='CIF', calorific_basis='not stated',
          conversion_constants='GUA_COK_NAR_MMBTU_PER_T;GJ_PER_MMBTU', value_usd_per_gj=r4(upt / cok_gj_t),
          evidence_class='international customs (Comtrade)', source_id=s_ct, page_or_table='cmdCode 271311, flowCode M, partnerCode 0',
          downloaded_file=rel('comtrade_GUA_2024_M.json'),
          derivation='cifvalue %.0f USD / netWgt %.0f kg x 1000 = %.4f USD/t; / 31.3985 GJ/t (29.76 MMBtu/t GUA_COK_NAR_MMBTU_PER_T x 1.055056 GJ_PER_MMBTU) = %.4f USD/GJ' % (r['cifvalue'], r['netWgt'], upt, upt / cok_gj_t),
          notes='Second source for the Banguat value; isQtyEstimated %s, isNetWgtEstimated %s.' % (r['isQtyEstimated'], r['isNetWgtEstimated']))
    # NGS
    price(fuel='NGS', model_code='DIST_NGS', price_point='generator delivered', price_as_published=7.763, currency='USD',
          unit='USD/GJ', period='2024 calendar year', months_covered='1-12', tax_treatment='pre-tax',
          calorific_basis='gross', conversion_constants='', value_usd_per_gj=7.763,
          evidence_class='ASSUMPTION candidate', source_id=s_peg5,
          page_or_table='PEG-5 bases numeral 5.3.3 (gas price = Henry Hub + FAGN + FGSC; CI and regasification separate)',
          downloaded_file=rel('cnee/PEG5_Bases_CNEE-108-2025.pdf'),
          derivation='value kept from the hub row built from published rates: Henry Hub 2024 average 2.079 USD/GJ + 5.684 USD/GJ for liquefaction, shipping and regasification = 7.763 USD/GJ (gross basis)',
          notes='Natural gas delivered to a Guatemalan power plant is taken as 7.76 USD/GJ (gross) for 2024, the Henry Hub average plus about 5.7 USD/GJ for liquefaction, shipping and regasification, because Guatemala imported no natural gas in 2024 and publishes no delivered gas price. The PEG-5 tender bases price contracted gas the same way, as Henry Hub plus a bidder adder (FAGN) for liquefaction and transport plus a supply guarantee factor (FGSC), with regasification paid in the capacity price. Range 6.5 to 10 USD/GJ (gross).')
    # ---------------- liquids from MEM structures
    GJ_GAL = {f: IPCC_NCV[f] / UN_GAL_PER_T[f] for f in ('DSL', 'GSL', 'FOI', 'LPG', 'KER')}
    conv_gal = lambda f: 'IPCC_NCV_%s;UN_GAL_PER_T_%s' % (f, f)
    gjtxt = lambda f: '(IPCC_NCV_%s %.1f GJ/t / UN_GAL_PER_T_%s %d gal/t = %.6f GJ/gal)' % (f, IPCC_NCV[f], f, UN_GAL_PER_T[f], GJ_GAL[f])
    ncyl = GUA_LB_PER_LPG_CYLINDER * GUA_KG_PER_LB / 1000 * IPCC_NCV['LPG']
    weeks = st['DSL']['weeks']
    nweeks = len(weeks)
    months = sorted({int(w[5:7]) for w in weeks})
    mtxt = ','.join(str(m) for m in months)
    weeks_txt = '%d of 52 weekly structures, dated %s' % (nweeks, ' '.join(w[5:] for w in weeks))
    period = '2024, %d weekly structures (no structure published for 26 Feb to 18 Mar, 29 Apr, 29 Jul to 9 Sep, 4 Nov, 18 Nov to 9 Dec, 30 Dec)' % nweeks
    pg = 'Estructuras de Precios referenciales 2024, %d files (%s to %s), Quetzales column' % (nweeks, struct_first, struct_last)
    dlf = ';'.join(rel('estructuras/' + f) for f in allfiles)

    def usd(q, gj):
        return q / FX / gj

    def mean(fuel, c):
        return st[fuel]['mean'].get(c, 0.0)

    def liquid_rows(fuel, slide, model, label, unitpub, gj_unit, conv, gj_text):
        m = st[slide]['mean']
        cif = m['cif']
        fr = m.get('inland_freight', 0.0)
        oc = m.get('other_costs', 0.0)
        im = m.get('importer_margin', 0.0)
        rm = m.get('retail_margin', 0.0)
        idp = m.get('idp', 0.0)
        iva = m.get('iva', 0.0)
        bm = m.get('bottler_margin', 0.0)
        tot = cif + fr + oc + im + rm + idp + iva + bm
        comps_txt = 'means of %d weeks, GTQ per %s: CIF %.4f; inland freight %.4f; other costs %.4f; importer margin %.4f; %sretail margin %.4f; IDP %.4f; IVA %.4f; sum %.4f' % (
            nweeks, unitpub.split('/')[1], cif, fr, oc, im, ('bottler margin %.4f; ' % bm) if bm else '', rm, idp, iva, tot)
        base = dict(fuel=fuel, model_code=model, currency='GTQ', unit=unitpub, period=period, months_covered=mtxt,
                    calorific_basis='not stated', exchange_rate='%.5f' % FX, exchange_rate_constant='GUA_FX_2024',
                    conversion_constants=conv, evidence_class='local regulator or operator', source_id=struct_ids,
                    page_or_table=pg, downloaded_file=dlf)
        v = usd(cif, gj_unit)
        price(price_point='import CIF', price_as_published=r4(cif), tax_treatment='CIF, before taxes', value_usd_per_gj=r4(v),
              derivation='mean of weekly PRECIO CIF %.4f GTQ/%s / %.5f GTQ/USD (GUA_FX_2024) / %s = %.4f USD/GJ' % (cif, unitpub.split('/')[1], FX, gj_text, v),
              notes='%s. MEM publishes CIF as one value (FOB, freight and insurance not separated). %s.' % (label, weeks_txt), **base)
        wh = cif + fr + oc + im
        v = usd(wh, gj_unit)
        price(price_point='wholesale import parity', price_as_published=r4(wh), importer_terminal_margin=r4(im),
              inland_freight=r4(fr), tax_treatment='pre-tax (excludes IDP and IVA)', value_usd_per_gj=r4(v),
              derivation='CIF %.4f + inland freight %.4f + other costs %.4f + importer margin %.4f = %.4f GTQ/%s; / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (
                  cif, fr, oc, im, wh, unitpub.split('/')[1], FX, gj_text, v),
              notes='%s. Price before the retail stage, summed from the published components. Other costs (OTROS GASTOS, %.4f GTQ) have no column and are included in the sum. %s.' % (label, oc, comps_txt), **base)
        pt = tot - idp - iva
        v = usd(pt, gj_unit)
        price(price_point='final consumer pre-tax', price_as_published=r4(tot), importer_terminal_margin=r4(im),
              inland_freight=r4(fr), retail_margin=r4(rm), wholesale_margin=r4(bm) if bm else '',
              tax_treatment='published price includes IDP and IVA; value excludes both', value_usd_per_gj=r4(v),
              derivation='published consumer price mean %.4f - IDP %.4f - IVA %.4f = %.4f GTQ/%s; / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (
                  tot, idp, iva, pt, unitpub.split('/')[1], FX, gj_text, v),
              notes='%s. %s%s.' % (label, comps_txt, '; bottler margin (MARGEN DEL ENVASADOR) recorded as wholesale_margin' if bm else ''), **base)

    liquid_rows('DSL', 'DSL', 'DIST_DSL', 'Diesel, consumer price at service station (MEM structure)', 'GTQ/gal', GJ_GAL['DSL'], conv_gal('DSL'), gjtxt('DSL'))
    liquid_rows('GSL', 'GSL_regular', 'DIST_GSL', 'Gasoline regular (MEM structure)', 'GTQ/gal', GJ_GAL['GSL'], conv_gal('GSL'), gjtxt('GSL'))
    liquid_rows('GSL', 'GSL_superior', 'DIST_GSL', 'Gasoline superior (MEM structure)', 'GTQ/gal', GJ_GAL['GSL'], conv_gal('GSL'), gjtxt('GSL'))
    liquid_rows('LPG', 'LPG_cylinder_25lb', 'DIST_LPG', 'LPG residential cylinder of 25 libras (MEM structure)', 'GTQ/cylinder', ncyl,
                'GUA_LB_PER_LPG_CYLINDER;GUA_KG_PER_LB;IPCC_NCV_LPG',
                '(25 lb GUA_LB_PER_LPG_CYLINDER x 0.454 kg/lb GUA_KG_PER_LB = 11.35 kg x IPCC_NCV_LPG 47.3 GJ/t = %.6f GJ/cylinder)' % ncyl)
    # LPG automotive: subtotal row PRECIO A EXPENDEDOR EN PLANTA includes IDP
    m = st['LPG_automotive_gal']['mean']
    cif, oc, im, idp, rm, iva = m['cif'], m['other_costs'], m['importer_margin'], m['idp'], m['retail_margin'], m['iva']
    tot = cif + oc + im + idp + rm + iva
    base = dict(fuel='LPG', model_code='DIST_LPG', currency='GTQ', unit='GTQ/gal', period=period, months_covered=mtxt,
                calorific_basis='not stated', exchange_rate='%.5f' % FX, exchange_rate_constant='GUA_FX_2024',
                conversion_constants=conv_gal('LPG'), evidence_class='local regulator or operator', source_id=struct_ids,
                page_or_table=pg + ', slide 6 GLP automotriz', downloaded_file=dlf)
    lab = 'Automotive LPG per gallon (MEM structure)'
    ctx = 'means of %d weeks, GTQ/gal: CIF %.4f; other costs %.4f; importer margin %.4f; IDP %.4f; price to retailer at plant %.4f; retail margin %.4f; IVA %.4f; sum %.4f' % (
        nweeks, cif, oc, im, idp, m['subtotal_planta'], rm, iva, tot)
    v = usd(cif, GJ_GAL['LPG'])
    price(price_point='import CIF', price_as_published=r4(cif), tax_treatment='CIF, before taxes', value_usd_per_gj=r4(v),
          derivation='mean PRECIO CIF %.4f GTQ/gal / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (cif, FX, gjtxt('LPG'), v),
          notes='%s. %s. %s.' % (lab, weeks_txt, ctx), **base)
    wh = cif + oc + im
    v = usd(wh, GJ_GAL['LPG'])
    price(price_point='wholesale import parity', price_as_published=r4(m['subtotal_planta']), importer_terminal_margin=r4(im),
          tax_treatment='published plant price includes IDP; value excludes IDP and IVA', value_usd_per_gj=r4(v),
          derivation='CIF %.4f + other costs %.4f + importer margin %.4f = %.4f GTQ/gal (published plant price %.4f minus IDP %.4f); / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (
              cif, oc, im, wh, m['subtotal_planta'], idp, FX, gjtxt('LPG'), v),
          notes='%s. The slide shows MARGEN IMPORTADOR twice; the first line carries no Quetzal value. %s.' % (lab, ctx), **base)
    pt = tot - idp - iva
    v = usd(pt, GJ_GAL['LPG'])
    price(price_point='final consumer pre-tax', price_as_published=r4(tot), importer_terminal_margin=r4(im), retail_margin=r4(rm),
          tax_treatment='published price includes IDP and IVA; value excludes both', value_usd_per_gj=r4(v),
          derivation='consumer price %.4f - IDP %.4f - IVA %.4f = %.4f GTQ/gal; / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (tot, idp, iva, pt, FX, gjtxt('LPG'), v),
          notes='%s. %s.' % (lab, ctx), **base)
    # FOI bunker structure
    m = st['FOI_bunker']['mean']
    cif, term, port, im, idp, iva = m['cif'], m['terminal'], m['port'], m['importer_margin'], m['idp'], m['iva']
    tot = cif + term + port + im + idp + iva
    base = dict(fuel='FOI', model_code='DIST_FOI', currency='GTQ', unit='GTQ/gal', period=period, months_covered=mtxt,
                calorific_basis='not stated', exchange_rate='%.5f' % FX, exchange_rate_constant='GUA_FX_2024',
                conversion_constants=conv_gal('FOI'), evidence_class='local regulator or operator', source_id=struct_ids,
                page_or_table=pg + ', slide 5 bunker', downloaded_file=dlf)
    ctx = 'means of %d weeks, GTQ/gal: CIF %.4f; terminal charges (GASTOS DE TERMINAL) %.4f; port charges (CARGOS PORTUARIOS) %.4f; gross importer margin %.4f; IDP %.4f; IVA %.4f; ex-rack San Jose price %.4f' % (
        nweeks, cif, term, port, im, idp, iva, tot)
    v = usd(cif, GJ_GAL['FOI'])
    price(price_point='import CIF', price_as_published=r4(cif), tax_treatment='CIF, before taxes', value_usd_per_gj=r4(v),
          derivation='mean PRECIO CIF %.4f GTQ/gal / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (cif, FX, gjtxt('FOI'), v),
          notes='Bunker C (fuel oil), MEM structure of the ex-rack price at Puerto San Jose terminal. %s. %s.' % (weeks_txt, ctx), **base)
    pre = tot - idp - iva
    v = usd(pre, GJ_GAL['FOI'])
    price(price_point='wholesale import parity', price_as_published=r4(tot), port=r4(port), importer_terminal_margin=r4(term + im),
          tax_treatment='published ex-rack price includes IVA (IDP is zero); value excludes IVA', value_usd_per_gj=r4(v),
          derivation='ex-rack price %.4f - IDP %.4f - IVA %.4f = %.4f GTQ/gal (= CIF %.4f + terminal %.4f + port %.4f + importer margin %.4f); / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (
              tot, idp, iva, pre, cif, term, port, im, FX, gjtxt('FOI'), v),
          notes='Ex-rack Puerto San Jose, the terminal price at which power plants and industry buy bunker; no generator-delivered price is published. importer_terminal_margin = terminal charges %.4f + gross importer margin %.4f. %s.' % (term, im, ctx), **base)
    # FOI and KER consumer prices, MEM other fuels
    of = other_fuels(os.path.join(dl, 'mem_other/PRECIOS-OTROS-COMBUSTIBLES-MENSUALES-OCTUBRE-2024.xlsx'))
    for fuel, model, idp_v, idp_name in (('FOI', 'DIST_FOI', GUA_IDP_FOI, 'GUA_IDP_FOI_2024'), ('KER', 'DIST_KER', GUA_IDP_KER, 'GUA_IDP_KER')):
        mm = sorted(k for k in of[2024] if isinstance(k, int))
        vals = [of[2024][k][fuel] for k in mm]
        avg = sum(vals) / len(vals)
        pre = (avg - idp_v) / (1 + GUA_IVA_RATE)
        v = usd(pre, GJ_GAL[fuel])
        price(fuel=fuel, model_code=model, price_point='final consumer pre-tax', price_as_published=r4(avg), currency='GTQ',
              unit='GTQ/gal', period='2024, January to October (monthly averages)', months_covered=','.join(str(k) for k in mm),
              tax_treatment='published price includes IDP and IVA; value excludes both', calorific_basis='not stated',
              exchange_rate='%.5f' % FX, exchange_rate_constant='GUA_FX_2024',
              conversion_constants='%s;GUA_IVA_RATE;IPCC_NCV_%s;UN_GAL_PER_T_%s' % (idp_name, fuel, fuel),
              value_usd_per_gj=r4(v), evidence_class='local regulator or operator',
              source_id='%s;%s' % (s_oth, s_law if fuel == 'KER' else struct_first),
              page_or_table='sheet X-MES-AS, table ANO 2024, column %s' % ('KEROSINA' if fuel == 'KER' else 'BUNKER'),
              downloaded_file=rel('mem_other/PRECIOS-OTROS-COMBUSTIBLES-MENSUALES-OCTUBRE-2024.xlsx'),
              derivation='mean of %d monthly prices (%s) = %.4f GTQ/gal; (%.4f - IDP %.2f %s) / (1 + 0.12 GUA_IVA_RATE) = %.4f GTQ/gal; / %.5f (GUA_FX_2024) / %s = %.4f USD/GJ' % (
                  len(mm), ' '.join('%s %.4f' % (MES_EN[k], of[2024][k][fuel]) for k in mm), avg, avg, idp_v, idp_name, pre, FX, gjtxt(fuel), v),
              notes=('Kerosene consumer price, Guatemala City, MEM monitoring; constant at 37.00 GTQ/gal in every month of 2024 (and 30.00 in 2020 and 2021), so it moves little with import costs. MEM publishes no kerosene price structure; imports were 71.43 bbl in August 2024 (MEM DGH, 151.62 USD/bbl) and 14774 kg under SAC 2710.19.12 (Banguat). The IDP rate is the 1998 rate (see constants).'
                     if fuel == 'KER' else
                     'Bunker consumer price, Guatemala City, MEM monitoring (MEM note: Precios Bunker son al consumidor). November and December 2024 not published in this file.'))
    # Banguat CIF for liquids
    for fuel, code, model, lab in (('FOI', '2710192200', 'DIST_FOI', 'SAC 2710.19.22 Fuel oil No. 6 (Bunker C); origins Ecuador, Bahamas, US Virgin Islands, Peru, others (GUA-004)'),
                                   ('DSL', '2710192100', 'DIST_DSL', 'SAC 2710.19.21 Diesel oil (gas oil)'),
                                   ('GSL', '2710123000', 'DIST_GSL', 'SAC 2710.12.30 motor gasoline (las demas gasolinas), regular and superior together'),
                                   ('LPG', '2711120000', 'DIST_LPG', 'SAC 2711.12 propane; butanes (2711.13) add 4987043 USD for 5596472 kg'),
                                   ('KER', '2710191200', 'DIST_KER', 'SAC 2710.19.12 other kerosenes; only 14774 kg imported in 2024, so the unit value is not representative of a fuel price; kerosene-type jet fuel (2710.19.11) was 796.64 USD/t for 134688 t')):
        v, kg = bg[code]
        upt = v / kg * 1000
        gj_t = IPCC_NCV[fuel]
        val = upt / gj_t
        price(fuel=fuel, model_code=model, price_point='import CIF', price_as_published=r4(upt), currency='USD', unit='USD/t',
              period='2024 calendar year', months_covered='1-12', tax_treatment='CIF, before import duties and taxes',
              calorific_basis='not stated', conversion_constants='IPCC_NCV_%s' % fuel, value_usd_per_gj=r4(val),
              evidence_class='local customs or statistics', source_id='%s;%s;%s' % (s_kf24, s_c4, s_sac),
              page_or_table='KF-103_2024 sheet Impo line %s, Total Anual' % code, downloaded_file=rel('banguat/CG_KF-103_2024.xlsx'),
              derivation='%.0f USD / %.0f kg x 1000 = %.4f USD/t; / IPCC_NCV_%s %.1f GJ/t = %.4f USD/GJ' % (v, kg, upt, fuel, gj_t, val),
              notes=lab + '.')
    with open(os.path.join(outdir, 'prices_GUA.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=PRICE_HDR)
        w.writeheader()
        w.writerows(P)

    # ---------------- history (Banguat CIF 2018-2025; MEM consumer prices 2018-2024)
    H = []
    for y in range(2018, 2026):
        b = banguat_lines(os.path.join(dl, 'banguat/CG_KF-103_%d.xlsx' % y))
        for fuel, code, model, gj_t, conv, txt in (
                ('COA', '2701120000', 'DIST_COA', coa_gj_t, 'GUA_COA_NAR_MMBTU_PER_T;GJ_PER_MMBTU', '25.1209 GJ/t (GUA_COA_NAR_MMBTU_PER_T x GJ_PER_MMBTU)'),
                ('COK', '2713110000', 'DIST_COK', cok_gj_t, 'GUA_COK_NAR_MMBTU_PER_T;GJ_PER_MMBTU', '31.3985 GJ/t (GUA_COK_NAR_MMBTU_PER_T x GJ_PER_MMBTU)'),
                ('FOI', '2710192200', 'DIST_FOI', IPCC_NCV['FOI'], 'IPCC_NCV_FOI', 'IPCC_NCV_FOI 40.4 GJ/t'),
                ('DSL', '2710192100', 'DIST_DSL', IPCC_NCV['DSL'], 'IPCC_NCV_DSL', 'IPCC_NCV_DSL 43.0 GJ/t'),
                ('GSL', '2710123000', 'DIST_GSL', IPCC_NCV['GSL'], 'IPCC_NCV_GSL', 'IPCC_NCV_GSL 44.3 GJ/t'),
                ('LPG', '2711120000', 'DIST_LPG', IPCC_NCV['LPG'], 'IPCC_NCV_LPG', 'IPCC_NCV_LPG 47.3 GJ/t')):
            if code not in b:
                continue
            v, kg = b[code]
            upt = v / kg * 1000
            row = {h: '' for h in PRICE_HDR}
            row.update(country='Guatemala', fuel=fuel, model_code=model, price_point='import CIF', year=y,
                       price_as_published=r4(upt), currency='USD', unit='USD/t', period='%d calendar year' % y,
                       months_covered='1-12', tax_treatment='CIF, before import duties and taxes', calorific_basis='not stated',
                       conversion_constants=conv, value_usd_per_gj=r4(upt / gj_t), evidence_class='local customs or statistics',
                       source_id='%s;%s' % (s_kfh[y], s_c4), page_or_table='KF-103_%d sheet Impo line %s, Total Anual' % (y, code),
                       downloaded_file=rel('banguat/CG_KF-103_%d.xlsx' % y),
                       derivation='%.0f USD / %.0f kg x 1000 = %.4f USD/t; / %s = %.4f USD/GJ (nominal)' % (v, kg, upt, txt, upt / gj_t),
                       notes='Nominal USD. Same Banguat series and line every year.')
            H.append(row)
    for y in range(2018, 2025):
        fxy = fx[y][0]
        for fuel, model, idp_v, idp_name in (('FOI', 'DIST_FOI', None, ''), ('KER', 'DIST_KER', GUA_IDP_KER, 'GUA_IDP_KER')):
            mm = sorted(k for k in of[y] if isinstance(k, int))
            if not mm:
                continue
            vals = [of[y][k][fuel] for k in mm]
            avg = sum(vals) / len(vals)
            if fuel == 'FOI':
                # IDP on bunker: 0 in the 2024 structures; earlier years not checked, so pre-tax removes IVA only
                idp_use, idp_txt = 0.0, 'IDP taken as 0 (2024 structure value)'
            else:
                idp_use, idp_txt = idp_v, 'IDP %.2f GUA_IDP_KER' % idp_v
            pre = (avg - idp_use) / 1.12
            v = pre / fxy / GJ_GAL[fuel]
            row = {h: '' for h in PRICE_HDR}
            row.update(country='Guatemala', fuel=fuel, model_code=model, price_point='final consumer pre-tax', year=y,
                       price_as_published=r4(avg), currency='GTQ', unit='GTQ/gal', period='%d monthly averages' % y,
                       months_covered=','.join(str(k) for k in mm),
                       tax_treatment='published price includes IDP and IVA; value excludes both', calorific_basis='not stated',
                       exchange_rate='%.5f' % fxy, exchange_rate_constant='GUA_FX_%d' % y,
                       conversion_constants='GUA_IVA_RATE;IPCC_NCV_%s;UN_GAL_PER_T_%s%s' % (fuel, fuel, ';GUA_IDP_KER' if fuel == 'KER' else ''),
                       value_usd_per_gj=r4(v), evidence_class='local regulator or operator',
                       source_id='%s;%s' % (s_oth, s_fxh[y]), page_or_table='sheet X-MES-AS, table ANO %d, column %s' % (y, 'KEROSINA' if fuel == 'KER' else 'BUNKER'),
                       downloaded_file=rel('mem_other/PRECIOS-OTROS-COMBUSTIBLES-MENSUALES-OCTUBRE-2024.xlsx'),
                       derivation='mean of %d monthly prices = %.4f GTQ/gal; (%.4f - %s) / 1.12 (GUA_IVA_RATE) = %.4f; / %.5f (GUA_FX_%d) / %s = %.4f USD/GJ (nominal)' % (
                           len(mm), avg, avg, idp_txt, pre, fxy, y, gjtxt(fuel), v),
                       notes='Nominal. Guatemala City consumer price, MEM monitoring.')
            H.append(row)
    with open(os.path.join(outdir, 'history_GUA.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=PRICE_HDR)
        w.writeheader()
        w.writerows(H)

    # ---------------- calorific
    CAL = [
        dict(country='Guatemala', balance='Balance Energetico 2024 (national energy balance)', publisher='Ministerio de Energia y Minas',
             url=S[[s['id'] for s in S].index(s_be24)]['url'], net_or_gross='not stated', factor_NGS='', factor_COA='', factor_COK='',
             factor_FOI='', factor_units='kBEP used as common unit; no factors published', page_or_table='page 4 and tables 1 to 7', source_id=s_be24),
        dict(country='Guatemala', balance='Balance Energetico 2010 (latest national balance found with its factor table)', publisher='Ministerio de Energia y Minas, Direccion General de Energia',
             url=S[[s['id'] for s in S].index(s_be10)]['url'], net_or_gross='not stated', factor_NGS='', factor_COA='5.0439',
             factor_COK='4.8998', factor_FOI='1.0685', factor_units='BEP per tonne (COA, COK); BEP per barrel (FOI); no natural gas factor',
             page_or_table='page 8, Factores de Conversion a Barriles Equivalentes de Petroleo (BEP)', source_id=s_be10),
        dict(country='Guatemala', balance='PEG-5-2025 tender bases (evaluation fuel values, not a balance)', publisher='Distribuidoras; approved by CNEE',
             url=S[[s['id'] for s in S].index(s_peg5)]['url'], net_or_gross='net', factor_NGS='', factor_COA='23.81',
             factor_COK='29.76', factor_FOI='', factor_units='MMBtu per tonne, net as received (NAR); natural gas priced in US$/MMBtu at Henry Hub (gross)',
             page_or_table='numeral 5.3.3, pages 29 and 30', source_id=s_peg5),
    ]
    with open(os.path.join(outdir, 'calorific_GUA.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['country', 'balance', 'publisher', 'url', 'net_or_gross', 'factor_NGS', 'factor_COA',
                                          'factor_COK', 'factor_FOI', 'factor_units', 'page_or_table', 'source_id'])
        w.writeheader()
        w.writerows(CAL)
    with open(os.path.join(outdir, 'sources_GUA.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'url', 'title', 'publisher', 'date', 'retrieval_date', 'downloaded_file',
                                          'page_or_table', 'rows_and_constants_supported'])
        w.writeheader()
        w.writerows(S)
    with open(os.path.join(outdir, 'constants_GUA.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['name', 'value', 'unit', 'source_id', 'page_or_table', 'derivation'])
        w.writeheader()
        w.writerows(C)
    print('prices', len(P), 'history', len(H), 'sources', len(S), 'constants', len(C), 'FX', FX)
    for p in P:
        print(p['fuel'], p['price_point'], p['value_usd_per_gj'], p['evidence_class'], p['notes'][:50])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
