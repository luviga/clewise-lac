"""Write sources_CR.csv, search_log_CR.csv, manual_CR.csv and calorific_CR.csv for job LAC_LOCAL_PRICES 20261109T085226Z.

Usage: py -I make_meta_cr.py <downloads_CR_dir> <out_dir>
Page numbers of the ARESEP resolutions are read from downloads/CR/aresep_monthly_2024_parsed.csv.
"""
import csv, os, sys, collections

DL, OUT = sys.argv[1], sys.argv[2]
RET = '2026-11-09'

pages = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(DL, 'aresep_monthly_2024_parsed.csv'), encoding='utf-8')):
    pages[r['resolution']].setdefault(r['component'], set()).add(r['pdf_page'])


def pg(res):
    p = pages[res]
    g = lambda c: ','.join(sorted(p.get(c, {'n/a'}), key=lambda x: int(x) if x.isdigit() else 0))
    return ('PDF pages: exchange rate p.%s; Cuadro COA p.%s; Cuadro MO and RSBT p.%s; subsidy table (Precio FOB estimado, precio terminal subsidiado) p.%s; '
            'Cuadro Impuesto unico p.%s; Por Tanto I.a plantel prices p.%s; I.b prices by mass p.%s; I.d station prices p.%s'
            % (g('fx'), g('coa'), g('mo'), g('fob_est'), g('tax'), g('plantel_sin'), g('masa_con_l'), g('station_sin_iva')))


RES = [
    ('CR-001', 'RE-0002-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/01/Alcance-No1-Gaceta-No1-08-01-24-Estudio-extraordinario.pdf', 'Alcance 1 a La Gaceta 1', '2024-01-08', 'RE-0002-IE-2024.pdf', 'January 2024'),
    ('CR-002', 'RE-0013-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/02/Alcance-N20-a-La-Gaceta-N22-ARESEP-RE-0013-IE-2024-Estudio-ajuste-extraordinario-mes-enero-2024.pdf', 'Alcance 20 a La Gaceta 22', '2024-02', 'RE-0013-IE-2024.pdf', 'February 2024'),
    ('CR-003', 'RE-0021-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/03/Alcance-N-46-La-Gaceta-N42-05-03-2024.pdf', 'Alcance 46 a La Gaceta 42', '2024-03-05', 'RE-0021-IE-2024.pdf', 'March 2024'),
    ('CR-004', 'RE-0034-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/04/Alcance-N71-La-Gaceta-N64-11-04-2024-RE-0034-IE-2024.pdf', 'Alcance 71 a La Gaceta 64', '2024-04-11', 'RE-0034-IE-2024.pdf', 'April 2024'),
    ('CR-005', 'RE-0040-IE-2024', 'https://recope.go.cr/wp-content/uploads/2024/05/Alcance-N88-a-La-Gaceta-N80-RE-0040-IE-2024.pdf', 'Alcance 88 a La Gaceta 80', '2024-05', 'RE-0040-IE-2024.pdf', 'May 2024'),
    ('CR-006', 'RE-0043-IE-2024', 'https://www.imprentanacional.go.cr/pub/2024/06/10/ALCA108_10_06_2024.pdf', 'Alcance 108 a La Gaceta 104 (also holds the rectification RE-0044-IE-2024, PDF pp.119 to 121)', '2024-06-10', 'ALCA108_10_06_2024.pdf', 'June 2024'),
    ('CR-007', 'RE-0050-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/07/Alcance-N-125-La-Gaceta-N128-12-07-2024-RE-0050-IE-junio-2024.pdf', 'Alcance 125 a La Gaceta 128', '2024-07-12', 'RE-0050-IE-2024.pdf', 'July 2024'),
    ('CR-008', 'RE-0059-IE-2024', 'https://recope.go.cr/wp-content/uploads/2024/08/Alcance-N137-La-Gaceta-N144.pdf', 'Alcance 137 a La Gaceta 144', '2024-08', 'RE-0059-IE-2024.pdf', 'August 2024'),
    ('CR-009', 'RE-0062-IE-2024', 'https://recope.go.cr/wp-content/uploads/2024/09/Alcance-N149-La-Gaceta-N160-RE-0062-IE-2024.pdf', 'Alcance 149 a La Gaceta 160', '2024-09', 'RE-0062-IE-2024.pdf', 'September 2024'),
    ('CR-010', 'RE-0068-IE-2024', 'https://recope.go.cr/wp-content/uploads/2024/10/Alcance-N170-La-Gaceta-N188-09-10-2024-RE-0068-IE-2024.pdf', 'Alcance 170 a La Gaceta 188', '2024-10-09', 'RE-0068-IE-2024.pdf', 'October 2024'),
    ('CR-011', 'RE-0076-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/11/Alcance-N180-La-Gaceta-N209-07-11-2024.pdf', 'Alcance 180 a La Gaceta 209', '2024-11-07', 'RE-0076-IE-2024.pdf', 'November 2024'),
    ('CR-012', 'RE-0083-IE-2024', 'https://www.recope.go.cr/wp-content/uploads/2024/12/Alcance-a-La-Gaceta-N199-a-La-Gaceta-N231-ARESEP-RE-0083-IE-2024.pdf', 'Alcance 199 a La Gaceta 231', '2024-12', 'RE-0083-IE-2024.pdf', 'December 2024'),
]
ROWS_RES = 'prices_CR: DSL, GSL (RON 91 and RON 95), JET, KER, AVG, FOI (Bunker and Bunker Termico ICE 2), LPG wholesale import parity, final consumer pre-tax (plantel and station) and generator delivered rows'

sources = []
for sid, res, url, alc, date, f, month in RES:
    sources.append([sid, url, 'ARESEP Intendencia de Energia %s, ajuste extraordinario de precios de los combustibles que expende RECOPE (prices in force %s), %s' % (res, month, alc),
                    'ARESEP (Autoridad Reguladora de los Servicios Publicos); published in La Gaceta' + ('; copy hosted by RECOPE' if 'recope' in url else ', Imprenta Nacional'),
                    date, RET, 'CR/' + f, pg(res), ROWS_RES])
B = 'https://datos.vuce.cr/OpenData/EstadisticasOData.svc'
SP = 'https://aresep-my.sharepoint.com/:b:/g/personal/multimedia_aresep_go_cr/'
sources += [
    ['CR-013', 'https://datos.aresep.go.cr/ws.datosabiertos/Services/IE/TarifaCombustible.svc/ObtenerComprasCombustibleRecope',
     'Compras de combustible de RECOPE (open data web service, one record per invoice: litres, mass, FOB, freight, insurance, CIF, trader and port cost)', 'ARESEP datos abiertos',
     'service metadata date 2023-11-09; records to 2026', RET, 'CR/aresep_od_ObtenerComprasCombustibleRecope.json', 'JSON array value, records with anho = reference year; fields litros, masa, costoFOB, costoFlete, costoSeguro, costoCIF, costoTrader, costoPortuario',
     'prices_CR import CIF rows for DSL, GSL, JET, AVG, FOI, LPG; history_CR liquids 2022 to 2025; constants CR_DENS_*_2024'],
    ['CR-014', SP + 'EUPUKhxzK4pGnhkF1XL0AnQBgrgE0M7oPssJA8wEfeGInA?e=8QSDkD&download=1',
     'ARESEP Intendencia de Energia RE-0164-IE-2023, fijacion anual del costo variable de generacion (CVG) 2024, ET-103-2023', 'ARESEP', '2023-12-19', RET,
     'CR/aresep_RE-0164-IE-2023_CVG2024.pdf', 'Cuadro 3 Precios de combustibles para generacion termica, colones por litro, ano 2024 (PDF p.9); method text PDF pp.8 to 9',
     'prices_CR generator delivered rows for FOI and DSL (freight to ICE plants; published CVG 2024 prices)'],
    ['CR-015', SP + 'ETCmrAeIUblKiAGnFG-nwLkBxpxTD2n_5NmVatQW-qe_6w?e=jniOEO&download=1',
     'ARESEP Intendencia de Energia RE-0097-IE-2024, fijacion anual del costo variable de generacion (CVG) 2025, ET-100-2024', 'ARESEP', '2024-12-16', RET,
     'CR/aresep_RE-0097-IE-2024_CVG2025.pdf', 'Cuadro 3 (PDF p.9): freight 7.0450 CRC/L bunker termico ICE 2 and 6.20 CRC/L diesel; method text PDF pp.8 to 9 (plantel price with tax plus freight)',
     'prices_CR generator delivered rows for FOI and DSL (freight confirmation)'],
    ['CR-016', B + "/od_import?$filter=startswith(partida,'2713') eq true", 'Estadisticas de comercio exterior, importaciones, partida 2713 (OData od_import)',
     'PROCOMER (Promotora del Comercio Exterior de Costa Rica), VUCE open data', 'data to September 2026', RET, 'CR/vuce_od_import_2713.json',
     'records with partida 271311*, fields id_tiempo, valor_tot (USD), peso_tot (kg)', 'prices_CR and history_CR COK rows'],
    ['CR-017', B + "/od_import?$filter=startswith(partida,'2701') eq true", 'Estadisticas de comercio exterior, importaciones, partida 2701 (OData od_import)',
     'PROCOMER, VUCE open data', 'data to September 2026', RET, 'CR/vuce_od_import_2701.json', 'records with partida 270111*, fields id_tiempo, valor_tot (USD), peso_tot (kg)',
     'prices_CR and history_CR COA rows'],
    ['CR-018', B + '/pt_tiempo', 'Estadisticas de comercio exterior, time dimension (id_tiempo to year and month)', 'PROCOMER, VUCE open data', 'data to September 2026', RET,
     'CR/vuce_pt_tiempo.json', 'fields id_tiempo, anno, num_mes', 'prices_CR and history_CR COA, COK and NGS rows (year and month mapping)'],
    ['CR-019', B + "/od_import?$filter=startswith(partida,'271111') eq true", 'Estadisticas de comercio exterior, importaciones, subpartida 271111 liquefied natural gas',
     'PROCOMER, VUCE open data', 'data to September 2026', RET, 'CR/vuce_od_import_271111.json', 'all records (none in 2024; last 612 kg in 2019)', 'prices_CR NGS row'],
    ['CR-020', B + "/od_import?$filter=startswith(partida,'271121') eq true", 'Estadisticas de comercio exterior, importaciones, subpartida 271121 natural gas in gaseous state',
     'PROCOMER, VUCE open data', 'data to September 2026', RET, 'CR/vuce_od_import_271121.json', 'records in 2024: 3 kg, 22.25 USD', 'prices_CR NGS row'],
    ['CR-021', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=188&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711',
     'UN Comtrade, Costa Rica imports 2024 by HS heading (preview API)', 'United Nations Statistics Division', '2024 annual data', RET, 'CR/comtrade_CR_2024_M_chapter.json',
     'records cmdCode 2701, 2709, 2710, 2711, 2713: cifvalue, netWgt', 'search log context (heading totals)'],
    ['CR-022', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=188&period=2024&partnerCode=0&flowCode=M&cmdCode=270111,270112,270119,270120,271311,271312,271320,271390,270900,271012,271019,271111,271112,271113,271119,271121,271129',
     'UN Comtrade, Costa Rica imports 2024 by HS subheading (preview API)', 'United Nations Statistics Division', '2024 annual data', RET, 'CR/comtrade_CR_2024_M_6digit.json',
     'records cmdCode 270111 and 271311 (cifvalue, netWgt, qtyUnitCode 8 = kg); 271111 absent; 271121 3.0 kg', 'prices_CR COA and COK Comtrade rows; NGS row'],
    ['CR-023', 'https://api.worldbank.org/v2/country/CRI/indicator/PA.NUS.FCRF?date=2018:2025&format=json',
     'World Development Indicators: Official exchange rate (LCU per US$, period average), Costa Rica 2018 to 2025', 'World Bank (from IMF International Financial Statistics)',
     'last updated 2026-10-08', RET, 'CR/wb_wdi_PA.NUS.FCRF_CRI_2018_2025.json', 'records date 2018 to 2025, field value', 'constants CR_FX_2018 to CR_FX_2025; every CRC row in prices_CR'],
    ['CR-024', 'https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf',
     '2006 IPCC Guidelines for National Greenhouse Gas Inventories, Volume 2 Energy, Chapter 1 Introduction', 'IPCC National Greenhouse Gas Inventories Programme (IGES)', '2006', RET,
     'CR/IPCC_2006_V2_1_Ch1_Introduction.pdf', 'Table 1.2, Anthracite NCV 26.7 GJ/t (PDF p.18)', 'constant CR_IPCC_NCV_COA_ANTHRACITE; COA rows'],
]
SH = ['id', 'url', 'title', 'publisher', 'date', 'retrieval_date', 'downloaded_file', 'page_or_table', 'rows_and_constants_supported']
with open(os.path.join(OUT, 'sources_CR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(SH); w.writerows(sources)

# ---------------- search log ----------------
L = []
FUELS_LIQ = ['DSL', 'GSL', 'JET', 'KER', 'LPG', 'FOI', 'AVG']
ALLF = ['COA', 'COK', 'NGS'] + FUELS_LIQ
RECOPE_PAGE = 'https://www.recope.go.cr/productos/precios-nacionales/publicaciones-de-variacion-de-precios/'


def lg(fuels, lead, url, result, detail):
    for f in fuels:
        L.append(['CostaRica', f, lead, {'aresep_recope': 'ARESEP fuel price resolutions and RECOPE price structures',
                                          'procomer_bccr_hacienda': 'PROCOMER, BCCR or Ministerio de Hacienda customs data',
                                          'ice_aresep_generation': 'ICE or ARESEP generation cost filings',
                                          'minae_balance': 'MINAE/SEPSE energy balance', 'customs_national': 'national customs or central bank import statistics by HS',
                                          'comtrade': 'UN Comtrade', 'energy_balance': 'national energy balance and methodology'}.get(lead, lead),
                  url, RET, result, detail])


# aresep_recope
lg(FUELS_LIQ, 'aresep_recope', RECOPE_PAGE + ' (12 monthly resolutions RE-0002 to RE-0083-IE-2024, re-downloaded)', 'value found',
   'COA, MO, RSBT, impuesto unico, plantel prices and station prices for all 12 months; FOB, freight and insurance not split in the resolutions (COA is a landed cost); KER and JET share one COA')
lg(['DSL', 'GSL', 'JET', 'KER', 'AVG'], 'aresep_recope', RECOPE_PAGE, 'no value',
   'no FOB, freight or insurance component and no separate wholesale margin published; distributor-without-fixed-point margin 3.746 CRC/L only as a with-tax price')
lg(['FOI', 'LPG'], 'aresep_recope', RECOPE_PAGE, 'no value',
   'Precio FOB estimado in the subsidy table is a fixed share (84.88 to 89.17 percent) of the terminal price used for the subsidy decree, not an invoice FOB; not used')
lg(['COA', 'COK', 'NGS'], 'aresep_recope', RECOPE_PAGE, 'no value', 'RECOPE does not import or sell coal, petroleum coke or natural gas; no ARESEP price exists')
lg(FUELS_LIQ, 'other_aresep_open_data', 'https://datos.aresep.go.cr/ws.datosabiertos/Services/IE/TarifaCombustible.svc/ObtenerComprasCombustibleRecope', 'value found',
   'invoice-level FOB, freight, insurance, CIF, trader and port cost, litres and mass for every RECOPE cargo 2022 to 2026 (no kerosene cargoes; kerosene is blended from jet)')
lg(['COA', 'COK', 'NGS'], 'other_aresep_open_data', 'https://datos.aresep.go.cr/ws.datosabiertos/Services/IE/TarifaCombustible.svc/ObtenerComprasCombustibleRecope', 'no value', 'RECOPE purchases only')
lg(FUELS_LIQ, 'other_aresep_open_data', 'https://datos.aresep.go.cr/ws.datosabiertos/Services/IE/TarifaCombustible.svc/ObtenerDensidadReferenciaCombustibles', 'no value',
   'reference densities only for 2026; 2024 densities taken from the purchase records instead')
lg(['DSL', 'GSL', 'KER'], 'other_aresep_open_data', 'https://datos.aresep.go.cr/ws.datosabiertos/Services/IE/TarifaCombustible.svc/ObtenerMargenComercializacionEstaciones', 'no value',
   'station margin and freight by station only for 2021 to 2023; 2024 margins taken from the resolutions (56.681 and 12.773 CRC/L)')
# ice_aresep_generation
lg(['FOI', 'DSL'], 'ice_aresep_generation', SP + 'EUPUKhxzK4pGnhkF1XL0AnQBgrgE0M7oPssJA8wEfeGInA?e=8QSDkD&download=1 (RE-0164-IE-2023 CVG 2024)', 'value found',
   'Cuadro 3: bunker termico ICE 2 322.70 + 7.045 = 329.74 CRC/L, diesel 619.58 + 6.20 = 625.78 CRC/L, plantel price with tax plus freight, December 2023 prices')
lg(['FOI', 'DSL'], 'ice_aresep_generation', SP + 'ETCmrAeIUblKiAGnFG-nwLkBxpxTD2n_5NmVatQW-qe_6w?e=jniOEO&download=1 (RE-0097-IE-2024 CVG 2025)', 'value found',
   'same freight; liquidation Jan to Oct 2024 gives real thermal fuel spending 59,197.30 million CRC but no litres, so no actual unit cost')
lg(['FOI', 'DSL'], 'ice_aresep_generation', 'https://aresep.go.cr/resoluciones-intendencia-energia-2024/re-0090-ie-2024-electricidad-publico-ice-estudio-tarifario-generacion-et-075-2024/', 'no value',
   'ICE generation tariff study 2025 downloaded (CR/aresep_RE-0090-IE-2024_ICE_generacion.pdf); fuel is handled through the CVG, no fuel unit price')
lg(['FOI', 'DSL'], 'ice_aresep_generation', 'web search: ICE Plan de Expansion de la Generacion 2024-2040 fuel prices', 'not found', 'only press items on the executive report; no document with fuel prices located')
lg(['COA', 'COK', 'NGS', 'GSL', 'JET', 'KER', 'LPG', 'AVG'], 'ice_aresep_generation', 'RE-0164-IE-2023 and RE-0097-IE-2024 (CVG)', 'no value', 'ICE thermal plants burn only diesel and bunker')
# customs
VU = 'https://datos.vuce.cr/OpenData/EstadisticasOData.svc/od_import'
lg(['COK'], 'procomer_bccr_hacienda', VU + "?$filter=startswith(partida,'2713') eq true", 'value found', '2024 HS 271311: 98,974,100 kg, 10,063,119.59 USD (3 months); series 2017 to 2026')
lg(['COA'], 'procomer_bccr_hacienda', VU + "?$filter=startswith(partida,'2701') eq true", 'value found', '2024 HS 270111 anthracite: 233,468 kg, 131,404.79 USD (3 months); no bituminous or sub-bituminous coal')
lg(['NGS'], 'procomer_bccr_hacienda', VU + "?$filter=startswith(partida,'271111') eq true", 'no value', 'no LNG imports in 2024 (last 612 kg in 2019)')
lg(['NGS'], 'procomer_bccr_hacienda', VU + "?$filter=startswith(partida,'271121') eq true", 'no value', '2024: 3 kg, 22.25 USD (samples, not a price)')
for f in ['COA', 'COK', 'NGS']:
    lg([f], 'procomer_bccr_hacienda', 'https://sdd.bccr.fi.cr/es/IndicadoresEconomicos/Inicio/ (BCCR indicators site)', 'no value', 'BCCR site has no import statistics by tariff line; its data API answers HTTP 500 to non-browser requests')
    lg([f], 'procomer_bccr_hacienda', 'https://www.hacienda.go.cr/', 'no value', 'Ministerio de Hacienda site has fiscal statistics only; customs trade data are published through PROCOMER')
lg(FUELS_LIQ, 'procomer_bccr_hacienda', VU, 'no value', 'not queried for liquids: RECOPE invoice data (ARESEP) give product-level CIF with components; HS 2710 mixes products')
lg(['COA', 'COK'], 'customs_national', VU + ' (PROCOMER OData, same as procomer_bccr_hacienda)', 'value found', 'see procomer_bccr_hacienda rows; national customs data are published by PROCOMER/VUCE')
lg(['NGS'], 'customs_national', VU + ' (PROCOMER OData, 271111 and 271121)', 'no value', 'no natural gas imports in 2024 apart from 3 kg of samples')
lg(FUELS_LIQ, 'customs_national', VU, 'no value', 'not used for liquids: HS 2710 lines mix products; RECOPE invoice data (ARESEP open data) give product-level CIF with FOB, freight and insurance')
# comtrade
CT = 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=188&period=2024&partnerCode=0&flowCode=M&cmdCode=270111,270112,270119,270120,271311,271312,271320,271390,270900,271012,271019,271111,271112,271113,271119,271121,271129'
lg(['COK'], 'comtrade', CT, 'value found', '271311 cifvalue 10,063,119.59 USD, netWgt 98,974,100 kg, flags not estimated')
lg(['COA'], 'comtrade', CT, 'value found', '270111 cifvalue 131,404.79 USD, netWgt 233,467.791 kg, flags not estimated')
lg(['NGS'], 'comtrade', CT, 'no value', '271111 no record; 271121 3.0 kg, 22.25 USD')
lg(['DSL', 'FOI'], 'comtrade', CT, 'no value', '271019 mixes diesel, fuel oil and other medium and heavy oils (1,534,813 t, 1,194.6 million USD); not product specific; RECOPE invoices used')
lg(['GSL', 'JET', 'KER', 'AVG'], 'comtrade', CT, 'no value', '271012 light oils mixes gasoline, avgas and others; jet and kerosene fall under 271019; not product specific')
lg(['LPG'], 'comtrade', CT, 'no value', '271112 propane 251,463 t, 145.75 million USD (579.6 USD/t); RECOPE invoices for the 70-30 mix used instead')
# balance
for f in ALLF:
    lg([f], 'minae_balance', 'https://www.minae.go.cr/energia/ben/Informe%20Balance%20de%20Energia%202022.pdf (and 2023, 2024 file names)', 'blocked HTTP 403', 'Cloudflare challenge page; not retried with other clients')
    lg([f], 'minae_balance', 'https://energia.minae.go.cr/?p=9516 (Balance Energetico Nacional page)', 'not found', 'host name does not resolve (DNS) from this machine')
    lg([f], 'energy_balance', 'https://sepse.go.cr/ (SEPSE)', 'not found', 'host name does not resolve (DNS)')
    lg([f], 'energy_balance', 'https://biblioteca.olade.org/opac-tmpl/Documentos/old0381.pdf (OLADE Manual de Estadisticas Energeticas 2017)', 'blocked HTTP 403', 'second-source calorific factors not retrievable')
# NGS study price
lg(['NGS'], 'other_lng_study', 'web search: Costa Rica estudio gas natural licuado importacion precio US$/MMBtu RECOPE ICE', 'not found', 'only press on RECOPE Terminal Pacifico (LPG terminal, LNG mentioned as an option); no price')
lg(['NGS'], 'other_lng_study', 'web search: ICE Plan de Expansion de la Generacion 2024 gas natural precio', 'not found', 'no ICE or MINAE document with an LNG price assumption located')
# exchange rate
for f in FUELS_LIQ:
    lg([f], 'other_bccr_fx', 'https://apim.bccr.fi.cr/SDDE/api/Bccr.GE.SDDE.IndicadoresSitioExterno.GrupoVariables.API/CuadroGrupoVariables/ObtenerDatosCuadro?IdGrupoVariable=1&FechaInicio=2024-01-01T00:00:00&FechaFin=2024-12-31&CantidadSeriesAMostrar=3',
       'blocked HTTP 500', 'BCCR daily reference rate service behind the Cuadro 1 page; answers 500 to direct requests; World Bank WDI 2024 annual average used for CR_FX_2024')
with open(os.path.join(OUT, 'search_log_CR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['country', 'fuel', 'lead_id', 'lead', 'url_or_query', 'date', 'result', 'detail']); w.writerows(L)

# ---------------- manual list ----------------
M = [
    ['https://www.minae.go.cr/energia/ben/Informe%20Balance%20de%20Energia%202022.pdf', 'Balance Energetico Nacional de Costa Rica, Informe 2022 (and the 2023 and 2024 editions if published)',
     'MINAE Direccion de Energia / SEPSE', 'national energy balance with conversion factors (net or gross basis, factors for natural gas, coal, petroleum coke, fuel oil) and coal, petcoke and natural gas supply',
     'calorific_CR (national balance row); confirms NGS zero supply and COA, COK industry use', 'calorific basis of the model fuel quantities is needed to match prices', 'HTTP 403 Cloudflare challenge', 'CR_MINAE_BEN_2022.pdf', '2'],
    ['https://energia.minae.go.cr/?p=9516', 'Balance Energetico Nacional (BEN) page, Direccion de Energia', 'MINAE', 'links to BEN 2023 and 2024 editions and methodology',
     'calorific_CR', 'locates the 2024 balance', 'host does not resolve (DNS)', 'CR_MINAE_BEN_page.html', '2'],
    ['https://biblioteca.olade.org/opac-tmpl/Documentos/old0381.pdf', 'OLADE Manual de Estadisticas Energeticas 2017', 'OLADE', 'OLADE (SIELAC) calorific basis (net) and default conversion factors',
     'calorific_CR (OLADE row)', 'second source for calorific basis', 'HTTP 403', 'OLADE_manual_estadisticas_2017.pdf', '2'],
    ['https://sdd.bccr.fi.cr/es/IndicadoresEconomicos/Inicio/Contenedor/6?Cuadro=1', 'Tipo cambio de compra y de venta del dolar, referencia del BCCR (daily, 2024, use the Descargar button for 01/01/2024 to 31/12/2024)',
     'Banco Central de Costa Rica', 'daily buying (317) and selling (318) reference rates for 2024', 'constant CR_FX_2024 (all CRC rows)', 'brief asks for the BCCR daily file and a computed mean',
     'page needs JavaScript; its data API answers HTTP 500 to direct requests', 'CR_BCCR_tipo_cambio_2024.xlsx', '4'],
]
with open(os.path.join(OUT, 'manual_CR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['url', 'title', 'publisher', 'should_hold', 'rows_it_closes', 'why_needed', 'how_failed', 'save_as', 'weight_rank']); w.writerows(M)

# ---------------- calorific ----------------
C = [['CostaRica', 'Balance Energetico Nacional (MINAE/SEPSE)', 'MINAE Direccion de Energia / SEPSE', 'https://www.minae.go.cr/energia/ben/Informe%20Balance%20de%20Energia%202022.pdf',
      'not stated', '', '', '', '', '', 'not retrieved: HTTP 403 Cloudflare challenge (on manual list)', ''],
     ['CostaRica', 'OLADE SIELAC energy balance (second source)', 'OLADE', 'https://biblioteca.olade.org/opac-tmpl/Documentos/old0381.pdf',
      'not stated', '', '', '', '', '', 'not retrieved: HTTP 403 (on manual list)', '']]
with open(os.path.join(OUT, 'calorific_CR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['country', 'balance', 'publisher', 'url', 'net_or_gross', 'factor_NGS', 'factor_COA', 'factor_COK', 'factor_FOI', 'factor_units', 'page_or_table', 'source_id']); w.writerows(C)
print('sources', len(sources), 'log', len(L), 'manual', len(M))
