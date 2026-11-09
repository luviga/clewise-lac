"""Build prices_DR.csv, history_DR.csv, sources_DR.csv, constants_DR.csv and dr_weekly_ppi_2024.csv for the
Dominican Republic from the files saved in downloads/DR.

Usage: py -I dr_build_outputs.py <downloads_dir> <country_DR_dir>
  <downloads_dir> is the job's downloads folder (contains DR/...), <country_DR_dir> is where CSVs are written.
Inputs produced earlier by dr_parse_avisos.py, dr_weekly_liquids.py, dr_merge_weekly.py, dr_digitise_oc_chart.py.
"""
import sys, os, re, csv, json, subprocess, datetime as dt
import pdfplumber

DL, OUT = sys.argv[1], sys.argv[2]
DR = os.path.join(DL, 'DR')
RET = '2026-11-09'

# shared constants (names from the job brief; values as given there)
L_PER_USGAL = 3.785411784
USGAL_PER_BBL = 42
GJ_PER_MMBTU = 1.055056
UN_GAL = dict(GSL=357, DSL=304, JET=326, KER=326, FOI=278, LPG=489)
NCV = dict(GSL=44.3, DSL=43.0, JET=44.1, KER=43.8, FOI=40.4, LPG=47.3, CRU=42.3, COK=32.5, COA=25.8, NGS=48.0)
NCV_NAME = dict(COA='IPCC_NCV_COA_OTHER_BITUMINOUS')

# ---------------------------------------------------------------- sources
sources = []


def add_source(url, title, publisher, date, dfile, page, supports):
    sid = 'DR-%03d' % (len(sources) + 1)
    sources.append(dict(id=sid, url=url, title=title, publisher=publisher, date=date, retrieval_date=RET,
                        downloaded_file=dfile, page_or_table=page, rows_and_constants_supported=supports))
    return sid


S = {}
S['fx'] = add_source('https://cdn.bancentral.gov.do/documents/estadisticas/mercado-cambiario/documents/TASA_DOLAR_REFERENCIA_MC.xlsx',
                     'Tasas de Cambio del dolar de Referencia del Mercado Spot', 'Banco Central de la Republica Dominicana', 'series to 2025',
                     'DR/bcrd_TASA_DOLAR_REFERENCIA_MC.xlsx', 'sheet PromAnual, row 2024, column Venta', 'DR_FX_2024 and every DOP row')
S['ct4'] = add_source('https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711',
                      'UN Comtrade public preview API: Dominican Republic imports 2024, HS 2701, 2709, 2710, 2711, 2713, partner World', 'United Nations Statistics Division (UN Comtrade)', '2024 annual',
                      'DR/comtrade_214_2024_M_4digit.json', 'records cmdCode 2709 and 2713 (cifvalue, netWgt)', 'CRU import CIF; COK cross-check')
S['ct6'] = add_source('https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=2024&partnerCode=0&flowCode=M&cmdCode=270112,271012,271019,271111,271112,271113,271119,271121,271311,271312',
                      'UN Comtrade public preview API: Dominican Republic imports 2024, HS 6-digit coal, petroleum products, LNG, LPG, petroleum coke', 'United Nations Statistics Division (UN Comtrade)', '2024 annual',
                      'DR/comtrade_214_2024_M_6digit.json', 'records cmdCode 270112, 271311, 271111, 271112, 271113, 271012 (cifvalue, fobvalue, netWgt)', 'COA, COK, NGS, LPG import CIF; GSL CIF/FOB ratio')
S['ctus'] = add_source('https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2024&partnerCode=214&flowCode=X&cmdCode=271012,271019,271112,271113,271111,270112,271311,2709',
                       'UN Comtrade public preview API: United States exports to the Dominican Republic 2024 (mirror data)', 'United Nations Statistics Division (UN Comtrade)', '2024 annual',
                       'DR/comtrade_842_X_to214_2024.json', 'record cmdCode 271012 (fobvalue, altQty in barrels, altQtyUnitCode 19); 2709 for crude cross-check', 'GSL import CIF built (market-tracking); CRU cross-check')
S['ctref'] = add_source('https://comtradeapi.un.org/files/v1/app/reference/QuantityUnits.json', 'UN Comtrade reference table of quantity units',
                        'United Nations Statistics Division (UN Comtrade)', 'current', 'DR/comtrade_ref_QuantityUnits.json', 'qtyCode 7 (l), 8 (kg), 12 (m3), 19 (BBL), 21 (1000 kg)', 'unit codes of the Comtrade records')
S['memann'] = add_source('https://mem.gob.do/wp-content/uploads/2025/01/Boletin-Informativo-Generacion-y-Gestion-Energia-2024-V.2.pdf',
                         'Boletin anual de Generacion y Gestion de Energia 2024', 'Ministerio de Energia y Minas, Viceministerio de Energia', '2025-01',
                         'DR/mem/Boletin-Informativo-Generacion-y-Gestion-Energia-2024-V.2.pdf', 'page 2, section 4, chart Comparacion del promedio anual de los precios de los commodities (Platts, USD/MMBTU, data labels)', 'COA, FOI, NGS international reference cross-checks')
S['ocmem'] = add_source('https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?Command=Core_Download&EntryId=200289&PortalId=0&TabId=234',
                        'Memoria Anual OC 2024 (zip containing Memoria Anual 2024.pdf)', 'Organismo Coordinador del Sistema Electrico Nacional Interconectado (OC-SENI)', '2025-04-22',
                        'DR/ocseni/memoria_anual_oc_2024.zip', 'section 6.2, Figura 45 (carbon, page 129) and Figura 46 (gas natural, page 130); costs declared by agents', 'COA and NGS generator delivered')
S['bcrd_ie'] = add_source('https://cdn.bancentral.gov.do/documents/publicaciones-economicas/informe-de-la-economia-dominicana/documents/infeco_definitivo2024-12.pdf',
                          'Informe de la Economia Dominicana enero-diciembre 2024', 'Banco Central de la Republica Dominicana', '2025',
                          'DR/bcrd/infeco_definitivo2024-12.pdf', 'Anexo No. 6 (continuacion), Importaciones totales por uso o destino economico: Carbon mineral 2024, Petroleo crudo y reconstituido 2024', 'COA and CRU import value cross-check (no volumes)')
S['sien'] = add_source('https://sien.cne.gob.do/WebForms/Utilidades/contenido.aspx?archivo=contenido3.1.html',
                       'SIEN Metodologia (Sistema de Informacion Energetica Nacional)', 'Comision Nacional de Energia', 'undated web page',
                       'DR/cne/sien_e7269c.html', 'section Gas Natural: 0.83 Tep per thousand normal m3; 600 Nm3 per m3 LNG', 'calorific_DR.csv')
S['cthist'] = {}
for y in (2018, 2019, 2020, 2021, 2022, 2023, 2025):
    S['cthist'][y] = add_source('https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=%d&partnerCode=0&flowCode=M&cmdCode=270112,271311,271111,271112,271113,2709' % y,
                                'UN Comtrade public preview API: Dominican Republic imports %d, coal, petroleum coke, LNG, LPG, crude' % y, 'United Nations Statistics Division (UN Comtrade)', '%d annual' % y,
                                'DR/comtrade_214_%d_M_hist.json' % y, 'records cmdCode 270112, 271311, 271111, 271112, 271113, 2709', 'history_DR.csv %d' % y)

# avisos
aviso_ids = {}
for u in open(os.path.join(DR, 'micm_avisos2024', 'aviso_urls.txt')).read().split():
    f = os.path.basename(u)
    aviso_ids[f] = add_source(u, f.replace('.pdf', '').replace('-', ' '), 'Ministerio de Industria, Comercio y Mipymes (MICM)', '2024 weekly',
                              'DR/micm_avisos2024/' + f, 'price table page 1 (PPI, taxes, margins, official price, exchange rate, LPG gal per tonne)', 'weekly PPI and margins, liquids and LPG')
# resolutions
res_links = open(os.path.join(DR, 'micm_listing', 'res_links.txt')).read().split()
liq_ids, ng_ids = {}, {}
res_links.sort(key=lambda p: int(re.search(r'NO\.(\d{3})', p).group(1)))
for p in res_links:
    f = os.path.basename(p)
    ng = 'NATURAL' in f.upper()
    sid = add_source('https://www.micm.gob.do' + p, f.replace('.pdf', '').replace('_', ' '), 'Ministerio de Industria, Comercio y Mipymes (MICM)', '2024 weekly',
                     'DR/micm_res2024/' + f,
                     'Articulo Segundo cost elements and Parrafo I (PPI in USD/MMBTU), Parrafo III exchange rate' if ng else 'Articulo Primero price table (scanned page with OCR text layer)',
                     'NGS weekly PPI' if ng else 'weekly PPI and margins, liquids and LPG')
    (ng_ids if ng else liq_ids)[f] = sid
# history xlsx
est = open(os.path.join(DR, 'micm_listing', 'est_2024.html'), encoding='utf-8', errors='replace').read()
hist_ids = {}
for p in sorted(set(re.findall(r'href="([^"]*HISTORICO[^"]*\.xlsx)"', est))):
    f = os.path.basename(p)
    hist_ids[f] = add_source('https://www.micm.gob.do' + p, f.replace('.xlsx', '').replace('_', ' '), 'Ministerio de Industria, Comercio y Mipymes (MICM), Direccion de Hidrocarburos', '2024 quarterly',
                             'DR/micm_hist2024/' + f, 'weekly price paid by the public by product (columns EGP-C gasoil, Avtur, Fuel Oil, Fuel Oil EGP-C, FO 1%S)', 'weekly PPI derivation for unfrozen products')

# ---------------------------------------------------------------- constants
FX = None
import openpyxl
ws = openpyxl.load_workbook(os.path.join(DR, 'bcrd_TASA_DOLAR_REFERENCIA_MC.xlsx'), read_only=True, data_only=True)['PromAnual']
for r in ws.iter_rows(values_only=True):
    if r and r[0] == 2024:
        FX = round(float(r[2]), 4)
assert FX == 59.5665, FX
avis = list(csv.DictReader(open(os.path.join(DR, 'avisos_parsed.csv'), encoding='utf-8')))
lpgf = {}
for r in avis:
    lpgf[r['file']] = float(r['lpg_gal_per_t'])
LPG_GPT = round(sum(lpgf.values()) / len(lpgf), 4)
constants = [
    dict(name='DR_FX_2024', value=FX, unit='DOP per USD', source_id=S['fx'], page_or_table='sheet PromAnual, 2024, Venta',
         derivation='BCRD 2024 annual average of the daily reference selling rate (simple daily average as stated in the sheet note); buying rate 59.2507'),
    dict(name='DR_LPG_GAL_PER_T_MICM', value=LPG_GPT, unit='US gallons per tonne', source_id=';'.join(aviso_ids[f] for f in sorted(lpgf)),
         page_or_table='each aviso, line Factor de Conversion correspondiente (Gls / Ton. Metric.)',
         derivation='mean of the %d weekly factors published in the digital avisos Jan to Aug 2024 (min %.2f, max %.2f); the scanned resolutions read for Sep to Dec show 502.94 to 504.86, inside the same range' % (len(lpgf), min(lpgf.values()), max(lpgf.values()))),
    dict(name='DR_NG_TEP_PER_THOUSAND_NM3', value=0.83, unit='toe per thousand normal m3', source_id=S['sien'], page_or_table='Metodologia, Gas Natural',
         derivation='as published; equals 0.83 x 41.868 = 34.75 MJ per normal m3 (KCAL_TO_KJ basis of the toe), used only in calorific_DR.csv'),
]

# ---------------------------------------------------------------- weekly liquids (final merged)
wk = list(csv.DictReader(open(os.path.join(DR, 'weekly_liquids_2024_final.csv'), encoding='utf-8')))
CHANGE = '2024-05-25'
MSET = {'GSL_PREMIUM': ((15.09, 22.57), (16.59, 25.07)), 'GSL_REGULAR': ((15.09, 22.57), (16.59, 25.07)),
        'DSL_REGULAR': ((12.78, 19.25), (14.28, 21.75)), 'LPG': ((10.21, 14.90), (11.71, 16.90))}
FIXED = {'AVTUR': (15.53, 0.0), 'DSL_EGPC': (5.24, 0.0), 'KER': (9.10, 15.01), 'FO6': (1.54, 0.0), 'FO6_EGPC': (1.35, 0.0),
         'FO6_1S': (1.54, 0.0), 'FO6_1S_EGPC': (1.35, 0.0)}  # constant in all 28 avisos and in the resolution tables read
for r in wk:
    if r['product'] in MSET:
        a, b = MSET[r['product']]
        r['dist'], r['det'] = (a if r['week_start'] < CHANGE else b)
    elif r['product'] in FIXED:
        r['dist'], r['det'] = FIXED[r['product']]
    r['source_doc_id'] = (aviso_ids.get(r['aviso_file']) if r['source'] == 'aviso' else liq_ids.get(r['resolution_file'], '')) or ''
    if r['source'].startswith('xlsx_derived'):
        r['source_doc_id'] = ';'.join(x for x in [hist_ids.get(r['hist_file'], ''), liq_ids.get(r['resolution_file'], '')] if x)
with open(os.path.join(OUT, 'dr_weekly_ppi_2024.csv'), 'w', newline='', encoding='utf-8') as fh:
    cols = ['week_start', 'product', 'ppi', 'dist', 'det', 'transp', 'l112', 'adval_rate', 'price_public_xlsx', 'fx_micm', 'source', 'source_doc_id', 'aviso_file', 'resolution_file', 'hist_file', 'hist_period', 'check']
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    w.writerows(wk)


def stats(prod):
    rows = [r for r in wk if r['product'] == prod and r['ppi'] not in ('', None)]
    n = len(rows)
    m = lambda k: sum(float(r[k]) for r in rows) / n
    ids = sorted({x for r in rows for x in r['source_doc_id'].split(';') if x}, key=lambda s: int(s[3:]))
    missing = sorted({r['week_start'] for r in wk if r['product'] == prod} - {r['week_start'] for r in rows})
    srcs = {}
    for r in rows:
        srcs[r['source']] = srcs.get(r['source'], 0) + 1
    return dict(n=n, ppi=m('ppi'), dist=m('dist'), det=m('det'), tr=m('transp'), ids=ids, missing=missing, srcs=srcs,
                first=rows[0]['week_start'], last=rows[-1]['week_start'])


def gj_per_gal(f, gpt=None, gpt_name=None):
    g = gpt or UN_GAL[f]
    return NCV[f] / g, (gpt_name or 'UN_GAL_PER_T_%s' % f)


prices = []
HDR = ['country', 'fuel', 'model_code', 'price_point', 'year', 'fob', 'freight', 'insurance', 'port', 'importer_terminal_margin', 'wholesale_margin', 'inland_freight',
       'retail_margin', 'price_as_published', 'currency', 'unit', 'period', 'months_covered', 'tax_treatment', 'calorific_basis', 'exchange_rate', 'exchange_rate_constant',
       'conversion_constants', 'value_usd_per_gj', 'evidence_class', 'source_id', 'page_or_table', 'downloaded_file', 'derivation', 'notes']


def row(**k):
    r = {h: '' for h in HDR}
    r.update(country='DominicanRepublic', year=2024)
    r.update(k)
    prices.append(r)


MICM_FILES = 'DR/micm_avisos2024/ (digital weekly avisos); DR/micm_res2024/ (weekly resolutions); DR/micm_hist2024/ (quarterly weekly price history)'
WEEKS_TXT = 'weekly MICM periods starting Saturday 6 Jan 2024 to Saturday 28 Dec 2024 (last week ends 3 Jan 2025); simple mean of weekly values'
MONTHS = 'Jan;Feb;Mar;Apr;May;Jun;Jul;Aug;Sep;Oct;Nov;Dec'


def liquid_rows(fuel, model, prod, point_sets, gpt=None, gpt_name=None, extra_note=''):
    s = stats(prod)
    gjg, gname = gj_per_gal(fuel, gpt, gpt_name)
    for point, comps in point_sets:
        val = s['ppi'] + sum(s[c] for c in comps)
        usd = val / FX / gjg
        comp_txt = ' + '.join(['PPI %.4f' % s['ppi']] + ['%s %.4f' % ({'dist': 'distributor margin', 'det': 'retailer margin', 'tr': 'transport commission'}[c], s[c]) for c in comps])
        der = ('%s = %.4f DOP/gal (means of %d weeks); %.4f DOP/gal / %.4f DOP/USD (DR_FX_2024) = %.6f USD/gal; GJ per gal = %.1f GJ/t (IPCC_NCV_%s) / %s gal/t (%s) = %.6f; %.6f / %.6f = %.4f USD/GJ' %
               (comp_txt, val, s['n'], val, FX, val / FX, NCV[fuel], fuel, ('%.4f' % (gpt or UN_GAL[fuel])), gname, gjg, val / FX, gjg, usd))
        miss = ('; weeks without a value: %s' % ','.join(s['missing'])) if s['missing'] else ''
        src_txt = ', '.join('%s %d' % kv for kv in sorted(s['srcs'].items()))
        row(fuel=fuel, model_code=model, price_point=point,
            wholesale_margin=('%.4f' % s['dist']) if 'dist' in comps else '',
            inland_freight=('%.4f' % s['tr']) if 'tr' in comps else '',
            retail_margin=('%.4f' % s['det']) if 'det' in comps else '',
            price_as_published='%.4f' % val, currency='DOP', unit='DOP per US gallon', period='2024', months_covered=MONTHS,
            tax_treatment='pre-tax (excludes Ley 112-00 specific tax and Ley 495-06 ad valorem tax shown in the same tables)',
            calorific_basis='not stated', exchange_rate=FX, exchange_rate_constant='DR_FX_2024',
            conversion_constants='IPCC_NCV_%s;%s' % (fuel, gname), value_usd_per_gj='%.4f' % usd,
            evidence_class='local regulator or operator', source_id=';'.join(s['ids']),
            page_or_table='MICM weekly price tables, row %s; columns Precio Paridad Importacion%s' % (prod, (', ' + ', '.join({'dist': 'Distribuidor', 'det': 'Detallista', 'tr': 'Comision Transporte'}[c] for c in comps)) if comps else ''),
            downloaded_file=MICM_FILES, derivation=der,
            notes=('MICM import parity (PPI) is published as one figure without FOB, freight, insurance or terminal split. ' + WEEKS_TXT + '; %d weeks (%s)%s. ' % (s['n'], src_txt, miss) + extra_note).strip())


# DSL: generator delivered (EGP-C), wholesale import parity (EGP-C PPI), final consumer pre-tax (public gasoil regular, frozen)
liquid_rows('DSL', 'DIST_DSL', 'DSL_EGPC', [('generator delivered', ['dist', 'tr']), ('wholesale import parity', [])],
            extra_note='Row Gasoil Regular EGP-C (generators, interconnected and not interconnected), the only market-tracking diesel parity in 2024; generator price = PPI + distributor margin 5.24 + transport commission 5.68 (EGP-T rows exclude transport).')
liquid_rows('DSL', 'DIST_DSL', 'DSL_REGULAR', [('final consumer pre-tax', ['dist', 'det', 'tr'])],
            extra_note='Public Gasoil Regular: retail price frozen at 221.60 DOP/gal all year with a weekly government adjustment; its PPI (mean 134.46) is below the EGP-C PPI for the same product (150.88), so this PPI is administrative. Margins rose from 12.78/19.25 to 14.28/21.75 from the week of 25 May 2024.')
# FOI
liquid_rows('FOI', 'DIST_FOI', 'FO6_EGPC', [('generator delivered', ['dist', 'tr'])], extra_note='Row Fuel Oil EGP-C (No. 6, generators): PPI + distributor margin 1.35 + transport 5.68.')
liquid_rows('FOI', 'DIST_FOI', 'FO6', [('wholesale import parity', []), ('final consumer pre-tax', ['dist', 'tr'])], extra_note='Row Fuel Oil (No. 6) to other buyers: distributor margin 1.54, no retailer margin, transport 5.68.')
liquid_rows('FOI', 'DIST_FOI', 'FO6_1S_EGPC', [('generator delivered', ['dist', 'tr'])], extra_note='Grade Fuel Oil 1% sulphur (FO6 1%S) EGP-C; the model has one fuel oil row; kept as a separate published point.')
liquid_rows('FOI', 'DIST_FOI', 'FO6_1S', [('wholesale import parity', [])], extra_note='Grade Fuel Oil 1% sulphur (FO6 1%S); separate published point.')
# GSL (admin)
liquid_rows('GSL', 'DIST_GSL', 'GSL_REGULAR', [('wholesale import parity', []), ('final consumer pre-tax', ['dist', 'det', 'tr'])],
            extra_note='OPEN QUESTION side A: retail price frozen at 272.50 DOP/gal (regular) all 2024; the weekly PPI moved only between 142.27 and 146.23 and fell by about 3 DOP/gal in the week of 25 May 2024 when margins rose by 4.00, so the published parity behaves as a residual of the frozen price. Premium PPI mean 152.26 DOP/gal (51 weeks) is in dr_weekly_ppi_2024.csv.')
# LPG (admin)
liquid_rows('LPG', 'DIST_LPG', 'LPG', [('wholesale import parity', []), ('final consumer pre-tax', ['dist', 'det', 'tr'])], gpt=LPG_GPT, gpt_name='DR_LPG_GAL_PER_T_MICM',
            extra_note='OPEN QUESTION side A: official LPG price fixed at 131.80 DOP/gal (132.60 paid by public) all year; PPI was 87.08 until 18 May and 84.06 from 25 May, when margins rose by 3.50 and PPI plus ad valorem fell by exactly 3.50, so the PPI is a residual (administrative). Conversion uses the MICM published gallons per tonne; with UN_GAL_PER_T_LPG 489 the value would be %.4f USD/GJ.' % (stats('LPG')['ppi'] / FX / (47.3 / 489)))
# KER, JET
liquid_rows('KER', 'DIST_KER', 'KER', [('wholesale import parity', []), ('final consumer pre-tax', ['dist', 'det', 'tr'])],
            extra_note='Kerosene received a small weekly government adjustment (2.2 to 3.3 DOP/gal) on the retail price; the PPI itself moves with the market.')
liquid_rows('JET', 'DIST_KER', 'AVTUR', [('wholesale import parity', []), ('final consumer pre-tax', ['dist', 'tr'])],
            extra_note='Avtur (jet fuel); ad valorem 6.5% not 16%; no retailer margin.')

# ---------------------------------------------------------------- natural gas MICM weekly PPI
ng_rows = []
for f, sid in sorted(ng_ids.items(), key=lambda kv: int(kv[1][3:])):
    txt = subprocess.run(['pdftotext', os.path.join(DR, 'micm_res2024', f), '-'], capture_output=True).stdout.decode('latin-1').replace('\n', ' ')
    m = re.search(r'ser\S{0,3}\s*de\s*US\$\s*([0-9]+[.,][0-9]+)\s*/\s*Mmbtu', txt, flags=re.I)
    fx = re.search(r'RD\$\s*([0-9]{2}[.,][0-9]{2}),\s*correspondiente', txt)
    v = float(m.group(1).replace(',', '.'))
    fxv = float(fx.group(1).replace(',', '.')) if fx else None
    dop = None
    for cand in (592.25, 504.97):
        if fxv and abs(v * fxv - cand) < 1.5:
            dop = cand
    if abs(v - 10.1761) < 1e-6:  # OCR inserts a digit; 592.25 / 58.20 = 10.176
        v = 10.176
    ng_rows.append(dict(file=f, sid=sid, ppi_usd=v, fx=fxv, ppi_dop=dop))
assert len(ng_rows) == 50
ng_mean = sum(r['ppi_usd'] for r in ng_rows) / 50
ng_dop_mean = sum(r['ppi_dop'] for r in ng_rows) / 50
with open(os.path.join(OUT, 'dr_weekly_ngs_ppi_2024.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['file', 'sid', 'ppi_usd', 'fx', 'ppi_dop'])
    w.writeheader()
    w.writerows(ng_rows)
ng_ids_txt = ';'.join(r['sid'] for r in ng_rows)
row(fuel='NGS', model_code='DIST_NGS', price_point='wholesale import parity', price_as_published='%.4f' % ng_mean, currency='USD', unit='USD per MMBTU',
    period='2024', months_covered=MONTHS, tax_treatment='pre-tax (PPI line; ad valorem 16% and GAL Ley 112 listed separately)', calorific_basis='not stated',
    exchange_rate='', exchange_rate_constant='', conversion_constants='GJ_PER_MMBTU', value_usd_per_gj='%.4f' % (ng_mean / GJ_PER_MMBTU),
    evidence_class='local regulator or operator', source_id=ng_ids_txt, page_or_table='each NG resolution, Articulo Segundo Parrafo I (PPI in USD/MMBTU) and cost-element table',
    downloaded_file='DR/micm_res2024/ (50 natural gas resolutions)',
    derivation='mean of 50 weekly PPI values (weeks 6 Jan to 28 Dec 2024; no resolution in the listing for weeks 23 Mar and 14 Dec) = %.4f USD/MMBTU; / 1.055056 GJ/MMBTU (GJ_PER_MMBTU) = %.4f USD/GJ' % (ng_mean, ng_mean / GJ_PER_MMBTU),
    notes='Basis not stated in the resolution; per-MMBTU prices are taken as gross by convention and are not converted. The PPI is fixed in pesos (592.25 DOP/MMBTU until 14 Jun, 504.97 from 15 Jun 2024; mean %.2f DOP/MMBTU) and converted weekly at the BCRD rate, so it is an administrative value, not a market quote. Importer selling price to wholesaler (671.26 / 772.51 DOP/MMBTU) adds ad valorem 16%%, GAL 21.72, SICOEX 9.78 and MDGNV 54.00. Applies to industrial, commercial and vehicle gas; power plants buy under private contracts.' % ng_dop_mean)
# final consumer pre-tax: public price 1187.16 minus ad valorem and GAL
pre = []
for r in ng_rows:
    adv = 94.76 if r['ppi_dop'] == 592.25 else 80.79
    pre.append(1187.16 - adv - 21.72)
pre_mean = sum(pre) / len(pre)
fx_ng = sum(r['fx'] for r in ng_rows) / 50
row(fuel='NGS', model_code='DIST_NGS', price_point='final consumer pre-tax', wholesale_margin='', retail_margin='', price_as_published='%.4f' % pre_mean, currency='DOP', unit='DOP per MMBTU',
    period='2024', months_covered=MONTHS, tax_treatment='pre-tax (public price 1,187.16 DOP/MMBTU minus Ad-valorem 16% PPI and GAL - Gastos Administrativos Ley 112)', calorific_basis='not stated',
    exchange_rate=FX, exchange_rate_constant='DR_FX_2024', conversion_constants='GJ_PER_MMBTU', value_usd_per_gj='%.4f' % (pre_mean / FX / GJ_PER_MMBTU),
    evidence_class='local regulator or operator', source_id=ng_ids_txt, page_or_table='each NG resolution, cost-element table, column GNL (Precio de Venta al Publico, Ad-valorem 16% PPI, GAL)',
    downloaded_file='DR/micm_res2024/ (50 natural gas resolutions)',
    derivation='weekly: 1187.16 - 94.76 - 21.72 = 1070.68 DOP/MMBTU (weeks to 8 Jun) and 1187.16 - 80.79 - 21.72 = 1084.65 (from 15 Jun); mean of 50 weeks = %.4f DOP/MMBTU; / %.4f DOP/USD (DR_FX_2024) / 1.055056 (GJ_PER_MMBTU) = %.4f USD/GJ' % (pre_mean, FX, pre_mean / FX / GJ_PER_MMBTU),
    notes='Station price to the public for vehicle natural gas (the only consumer price in the resolution); includes PPI, SICOEX, MDGNV, wholesaler processing, distribution, transport, station repayment and retailer margins. Basis not stated (per MMBTU, gross by convention).')

# ---------------------------------------------------------------- OC-SENI declared costs (digitised)
def oc_mean(fname, series):
    rows = [r for r in csv.DictReader(open(os.path.join(DR, 'ocseni', fname), encoding='utf-8')) if int(r['series']) == series]
    last = rows[-12:]
    return sum(float(r['value']) for r in last) / 12, [round(float(r['value']), 1) for r in last]


coal_dop, coal_m = oc_mean('oc_mem2024_chart_p129.csv', 0)
ng_dop, ng_m = oc_mean('oc_mem2024_chart_p130.csv', 1)
row(fuel='COA', model_code='DIST_COA', price_point='generator delivered', price_as_published='%.2f' % coal_dop, currency='DOP', unit='DOP per tonne', period='2024', months_covered=MONTHS,
    tax_treatment='not stated', calorific_basis='not stated', exchange_rate=FX, exchange_rate_constant='DR_FX_2024', conversion_constants=NCV_NAME['COA'],
    value_usd_per_gj='%.4f' % (coal_dop / FX / NCV['COA']), evidence_class='local regulator or operator', source_id=S['ocmem'],
    page_or_table='Memoria Anual 2024, section 6.2, Figura 45 Costo promedio mensual del carbon mineral 2001-2024 (page 129), last 12 monthly points',
    downloaded_file='DR/ocseni/memoria_anual_oc_2024.zip',
    derivation='monthly values digitised from the vector chart (dr_digitise_oc_chart.py; y axis fitted to 17 tick labels, max residual 0.03 pt): %s; mean = %.2f DOP/t; / %.4f DOP/USD (DR_FX_2024) = %.4f USD/t; / 25.8 GJ/t (IPCC_NCV_COA_OTHER_BITUMINOUS) = %.4f USD/GJ' % (', '.join(str(x) for x in coal_m), coal_dop, FX, coal_dop / FX, coal_dop / FX / NCV['COA']),
    notes='Average coal cost declared by generating agents to OC-SENI for economic dispatch (Itabo 1 and 2, Barahona Carbon, Punta Catalina). Value read from a chart, not a table: the figure title says RD$/LB but the axis says RD$/TM and the level (about 5,900) only fits per tonne. Coal calorific value of the plants is not published here, so the IPCC factor is used.')
row(fuel='NGS', model_code='DIST_NGS', price_point='generator delivered', price_as_published='%.2f' % ng_dop, currency='DOP', unit='DOP per MMBTU', period='2024', months_covered=MONTHS,
    tax_treatment='not stated', calorific_basis='not stated', exchange_rate=FX, exchange_rate_constant='DR_FX_2024', conversion_constants='GJ_PER_MMBTU',
    value_usd_per_gj='%.4f' % (ng_dop / FX / GJ_PER_MMBTU), evidence_class='local regulator or operator', source_id=S['ocmem'],
    page_or_table='Memoria Anual 2024, section 6.2, Figura 46 Costo promedio mensual del gas natural 2003-2024 (page 130), last 12 monthly points',
    downloaded_file='DR/ocseni/memoria_anual_oc_2024.zip',
    derivation='monthly values digitised from the vector chart (dr_digitise_oc_chart.py; y axis fitted to 8 tick labels, max residual 0.03 pt): %s; mean = %.2f DOP/MMBTU; / %.4f (DR_FX_2024) = %.4f USD/MMBTU; / 1.055056 (GJ_PER_MMBTU) = %.4f USD/GJ' % (', '.join(str(x) for x in ng_m), ng_dop, FX, ng_dop / FX, ng_dop / FX / GJ_PER_MMBTU),
    notes='Average natural gas cost declared by generating agents to OC-SENI. Value read from a chart, not a table. Basis not stated (per MMBTU, gross by convention; not converted).')

# ---------------------------------------------------------------- Comtrade 2024
ct6 = {r['cmdCode']: r for r in json.load(open(os.path.join(DR, 'comtrade_214_2024_M_6digit.json')))['data']}
ct4 = {r['cmdCode']: r for r in json.load(open(os.path.join(DR, 'comtrade_214_2024_M_4digit.json')))['data']}
ctus = {r['cmdCode']: r for r in json.load(open(os.path.join(DR, 'comtrade_842_X_to214_2024.json')))['data']}


def ct_row(fuel, model, rec, sid, ncv_name, ncv, extra, cmd_label, basis='net'):
    usd_t = rec['cifvalue'] / (rec['netWgt'] / 1000.0)
    row(fuel=fuel, model_code=model, price_point='import CIF', price_as_published='%.4f' % usd_t, currency='USD', unit='USD per tonne', period='2024', months_covered=MONTHS,
        tax_treatment='CIF customs value, excludes duties and taxes', calorific_basis='not stated', exchange_rate='', exchange_rate_constant='', conversion_constants=ncv_name,
        value_usd_per_gj='%.4f' % (usd_t / ncv), evidence_class='international customs (Comtrade)', source_id=sid,
        page_or_table='record reporterCode 214, flowCode M, partnerCode 0, cmdCode %s, classification %s' % (rec['cmdCode'], rec['classificationCode']),
        downloaded_file=sources[int(sid[3:]) - 1]['downloaded_file'],
        derivation='cifvalue %.3f USD / netWgt %.1f kg x 1000 = %.4f USD/t; / %.1f GJ/t (%s) = %.4f USD/GJ (%s calorific basis of the factor)' % (rec['cifvalue'], rec['netWgt'], usd_t, ncv, ncv_name, usd_t / ncv, basis),
        notes='%s. qtyUnitCode %s, isQtyEstimated %s, isNetWgtEstimated %s. %s' % (cmd_label, rec['qtyUnitCode'], rec['isQtyEstimated'], rec['isNetWgtEstimated'], extra))
    return usd_t


coa_t = ct_row('COA', 'DIST_COA', ct6['270112'], S['ct6'], 'IPCC_NCV_COA_OTHER_BITUMINOUS', NCV['COA'],
               'Mostly power plant coal (Punta Catalina, Itabo, Barahona) plus cement. BCRD reports 2024 coal imports of 260.3 million USD (balance of payments basis, no volume). MEM annual bulletin 2024 gives the Platts coal FOB Puerto Bolivar reference at 3.59 USD/MMBTU (3.40 USD/GJ).',
               'HS 270112 bituminous coal')
cok_t = ct_row('COK', 'DIST_COK', ct6['271311'], S['ct6'], 'IPCC_NCV_COK', NCV['COK'],
               'Non-calcined petroleum coke, used by cement. HS 2713 total: 32.26 million USD for 346,650.51 t (93.05 USD/t) including calcined coke and bitumen residues.',
               'HS 271311 petroleum coke not calcined')
cru = ct4['2709']
usd_t = cru['cifvalue'] / (cru['netWgt'] / 1000.0)
row(fuel='CRU', model_code='DIST_CRU', price_point='import CIF', price_as_published='%.4f' % usd_t, currency='USD', unit='USD per tonne', period='2024', months_covered=MONTHS,
    tax_treatment='CIF customs value, excludes duties and taxes', calorific_basis='not stated', conversion_constants='IPCC_NCV_CRU;UN_BBL_PER_T_CRU',
    value_usd_per_gj='%.4f' % (usd_t / NCV['CRU']), evidence_class='international customs (Comtrade)', source_id=S['ct4'],
    page_or_table='record reporterCode 214, flowCode M, partnerCode 0, cmdCode 2709', downloaded_file='DR/comtrade_214_2024_M_4digit.json',
    derivation='cifvalue %.3f USD / netWgt %.1f kg x 1000 = %.4f USD/t; / 42.3 GJ/t (IPCC_NCV_CRU) = %.4f USD/GJ; for reference %.4f USD/t / 7.32 bbl/t (UN_BBL_PER_T_CRU) = %.2f USD/bbl' % (cru['cifvalue'], cru['netWgt'], usd_t, usd_t / NCV['CRU'], usd_t, usd_t / 7.32),
    notes='Crude for the REFIDOMSA refinery. isNetWgtEstimated %s. Cross-checks: DR-reported 2025 record gives both mass and barrels (7.64 bbl/t), which would put 2024 at %.2f USD/bbl; US-reported exports of crude to the Dominican Republic in 2024 were %.0f USD FOB for %.0f bbl (%.2f USD/bbl, record 2709 in the US mirror query), lower than the DR CIF; BCRD lists 2024 crude imports at 752.5 million USD.' % (cru['isNetWgtEstimated'], usd_t / 7.64, ctus['2709']['fobvalue'], ctus['2709']['altQty'], ctus['2709']['fobvalue'] / ctus['2709']['altQty']))
lng = ct6['271111']
lng_t = ct_row('NGS', 'DIST_NGS', lng, S['ct6'], 'IPCC_NCV_NGS', NCV['NGS'],
               'LNG imported through the AES Andres terminal. Alternative quantity %.1f m3 of LNG (altQtyUnitCode 12) gives %.2f USD per m3 LNG. The value is on a net basis because the IPCC factor is net; per coordinator steer it is not converted to gross.' % (lng['altQty'], lng['cifvalue'] / lng['altQty']),
               'HS 271111 natural gas liquefied')
# LPG: 271112 + 271113 combined
p, b = ct6['271112'], ct6['271113']
val = p['cifvalue'] + b['cifvalue']
wt = p['netWgt'] + b['netWgt']
lpg_t = val / (wt / 1000.0)
row(fuel='LPG', model_code='DIST_LPG', price_point='import CIF', price_as_published='%.4f' % lpg_t, currency='USD', unit='USD per tonne', period='2024', months_covered=MONTHS,
    tax_treatment='CIF customs value, excludes duties and taxes', calorific_basis='not stated', conversion_constants='IPCC_NCV_LPG', value_usd_per_gj='%.4f' % (lpg_t / NCV['LPG']),
    evidence_class='international customs (Comtrade)', source_id=S['ct6'], page_or_table='records cmdCode 271112 (propane) and 271113 (butanes), reporter 214, flow M, partner World',
    downloaded_file='DR/comtrade_214_2024_M_6digit.json',
    derivation='(cifvalue 271112 %.3f + 271113 %.3f) USD / (netWgt %.2f + %.2f) kg x 1000 = %.4f USD/t; / 47.3 GJ/t (IPCC_NCV_LPG) = %.4f USD/GJ' % (p['cifvalue'], b['cifvalue'], p['netWgt'], b['netWgt'], lpg_t, lpg_t / NCV['LPG']),
    notes='OPEN QUESTION side B (market-tracking 2024 import cost). Propane alone: %.2f USD/t (%.4f USD/GJ). DR also reports %.0f litres of propane (altQtyUnitCode 7), i.e. %.4f USD per litre or %.4f USD per US gallon CIF, against the MICM PPI of %.4f USD/gal. HS 271119 (other LPG) has value 138,824.91 USD and no quantity and is excluded. isNetWgtEstimated False for both records.' % (
        p['cifvalue'] / (p['netWgt'] / 1000), p['cifvalue'] / (p['netWgt'] / 1000) / NCV['LPG'], p['altQty'], p['cifvalue'] / p['altQty'], p['cifvalue'] / p['altQty'] * L_PER_USGAL, stats('LPG')['ppi'] / FX))
# GSL built: US FOB per bbl x DR CIF/FOB ratio for 271012
us = ctus['271012']
dr = ct6['271012']
fob_bbl = us['fobvalue'] / us['altQty']
ratio = dr['cifvalue'] / dr['fobvalue']
cif_bbl = fob_bbl * ratio
gjg = NCV['GSL'] / UN_GAL['GSL']
gsl_usd = cif_bbl / USGAL_PER_BBL / gjg
row(fuel='GSL', model_code='DIST_GSL', price_point='import CIF', fob='%.4f' % fob_bbl, freight='', insurance='', price_as_published='%.4f' % cif_bbl, currency='USD', unit='USD per barrel',
    period='2024', months_covered=MONTHS, tax_treatment='CIF customs value, excludes duties and taxes', calorific_basis='not stated',
    conversion_constants='USGAL_PER_BBL;IPCC_NCV_GSL;UN_GAL_PER_T_GSL', value_usd_per_gj='%.4f' % gsl_usd, evidence_class='built from published components',
    source_id='%s;%s' % (S['ctus'], S['ct6']), page_or_table='US exports to DR record cmdCode 271012 (fobvalue, altQty BBL); DR imports record cmdCode 271012 (cifvalue, fobvalue)',
    downloaded_file='DR/comtrade_842_X_to214_2024.json;DR/comtrade_214_2024_M_6digit.json',
    derivation='FOB component (%s): fobvalue %.0f USD / altQty %.0f bbl (altQtyUnitCode 19, BBL per %s) = %.4f USD/bbl; CIF/FOB ratio (%s): DR 271012 cifvalue %.3f / fobvalue %.3f = %.6f; %.4f x %.6f = %.4f USD/bbl CIF; / 42 gal/bbl (USGAL_PER_BBL) = %.6f USD/gal; GJ per gal = 44.3 (IPCC_NCV_GSL) / 357 (UN_GAL_PER_T_GSL) = %.6f; = %.4f USD/GJ' % (
        S['ctus'], us['fobvalue'], us['altQty'], S['ctref'], fob_bbl, S['ct6'], dr['cifvalue'], dr['fobvalue'], ratio, fob_bbl, ratio, cif_bbl, cif_bbl / 42, gjg, gsl_usd),
    notes='OPEN QUESTION side B (market-tracking 2024 import cost). The DR record for 271012 has no quantity, so the unit value comes from the US-reported exports to the Dominican Republic (the US supplies most DR gasoline) and DR freight and insurance enter only through the DR CIF/FOB ratio of the same HS code. HS 271012 also holds naphtha and aviation gasoline. FOB alone: %.4f USD/GJ. US weights for petroleum are volume-derived (about 1 kg per litre) and are not used.' % (fob_bbl / 42 / gjg))

# ---------------------------------------------------------------- write prices
with open(os.path.join(OUT, 'prices_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=HDR)
    w.writeheader()
    w.writerows(prices)

# ---------------------------------------------------------------- history (Comtrade DR-reported unit values 2018-2025)
hist = []
codes = [('COA', 'DIST_COA', ['270112'], 'IPCC_NCV_COA_OTHER_BITUMINOUS', 25.8), ('COK', 'DIST_COK', ['271311'], 'IPCC_NCV_COK', 32.5),
         ('NGS', 'DIST_NGS', ['271111'], 'IPCC_NCV_NGS', 48.0), ('LPG', 'DIST_LPG', ['271112', '271113'], 'IPCC_NCV_LPG', 47.3), ('CRU', 'DIST_CRU', ['2709'], 'IPCC_NCV_CRU', 42.3)]
years = {y: (S['cthist'][y], 'DR/comtrade_214_%d_M_hist.json' % y) for y in S['cthist']}
years[2024] = None
for y in sorted(years):
    if y == 2024:
        data = {**ct6, '2709': ct4['2709']}
        sid = '%s;%s' % (S['ct6'], S['ct4'])
        dfile = 'DR/comtrade_214_2024_M_6digit.json;DR/comtrade_214_2024_M_4digit.json'
    else:
        sid, dfile = years[y]
        data = {r['cmdCode']: r for r in json.load(open(os.path.join(DL, dfile.replace('/', os.sep))))['data']}
    for fuel, model, cmds, ncvn, ncv in codes:
        recs = [data.get(c) for c in cmds]
        if any(r is None or not r.get('cifvalue') or not r.get('netWgt') for r in recs):
            continue
        v = sum(r['cifvalue'] for r in recs)
        kg = sum(r['netWgt'] for r in recs)
        ut = v / (kg / 1000)
        est = any(r['isNetWgtEstimated'] for r in recs)
        r0 = {h: '' for h in HDR}
        r0.update(country='DominicanRepublic', fuel=fuel, model_code=model, price_point='import CIF', year=y, price_as_published='%.4f' % ut, currency='USD', unit='USD per tonne',
                  period=str(y), months_covered=MONTHS, tax_treatment='CIF customs value, excludes duties and taxes', calorific_basis='not stated', conversion_constants=ncvn,
                  value_usd_per_gj='%.4f' % (ut / ncv), evidence_class='international customs (Comtrade)', source_id=sid,
                  page_or_table='reporter 214, flow M, partner World, cmdCode %s, classification %s' % ('+'.join(cmds), recs[0]['classificationCode']), downloaded_file=dfile,
                  derivation='cifvalue %.3f USD / netWgt %.1f kg x 1000 = %.4f USD/t; / %.1f GJ/t (%s) = %.4f USD/GJ' % (v, kg, ut, ncv, ncvn, ut / ncv),
                  notes='nominal USD; isNetWgtEstimated %s%s' % (est, '; weight estimated by UN Comtrade, treat with care' if est else ''))
        hist.append(r0)
with open(os.path.join(OUT, 'history_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=HDR)
    w.writeheader()
    w.writerows(hist)

# ---------------------------------------------------------------- sources and constants
with open(os.path.join(OUT, 'sources_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['id', 'url', 'title', 'publisher', 'date', 'retrieval_date', 'downloaded_file', 'page_or_table', 'rows_and_constants_supported'])
    w.writeheader()
    w.writerows(sources)
with open(os.path.join(OUT, 'constants_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['name', 'value', 'unit', 'source_id', 'page_or_table', 'derivation'])
    w.writeheader()
    w.writerows(constants)
print('prices', len(prices), 'history', len(hist), 'sources', len(sources), 'constants', len(constants))
for r in prices:
    print(r['fuel'], r['price_point'], r['price_as_published'], r['unit'], r['value_usd_per_gj'], r['evidence_class'])
for r in hist:
    print('H', r['year'], r['fuel'], r['value_usd_per_gj'], r['notes'][-40:])
