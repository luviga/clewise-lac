"""Write search_log_DR.csv, manual_DR.csv and calorific_DR.csv for the Dominican Republic sub-task.
Usage: py -I dr_write_logs.py <country_DR_dir>
Each attempt is listed once with the fuels it covered and expanded to one row per fuel."""
import sys, os, csv

OUT = sys.argv[1]
D = '2026-11-09'
LIQ = ['DSL', 'FOI', 'GSL', 'LPG', 'KER', 'JET']
ALLF = ['COA', 'COK', 'NGS', 'FOI', 'DSL', 'GSL', 'LPG', 'KER', 'JET', 'CRU']
A = [
    # lead_id, lead, url_or_query, result, detail, fuels
    ('sie_cne_micm', 'MICM listing of 2024 weekly price resolutions (9 pages)', 'https://www.micm.gob.do/transparencia/base-legal-de-la-institucion/category/resoluciones-precios-combustibles-2024', 'value found',
     'listing pages 1 to 9 give 100 PDF links (50 liquids and LPG, 50 natural gas); weeks 23 Mar and 14 Dec 2024 have no resolution', LIQ + ['NGS']),
    ('sie_cne_micm', 'MICM weekly price resolutions 2024, 100 PDFs re-downloaded', 'https://www.micm.gob.do/transparencia/images/pdf/transparencia/base-legal-de-la-institucion/resoluciones/2024/ (100 files listed in sources_DR.csv)', 'value found',
     'scanned pages with OCR layer; PPI, taxes and margins per product; 23 liquids tables read from rendered images (dr_resolution_image_reads.csv) and checked against the printed ad valorem column', LIQ),
    ('sie_cne_micm', 'MICM natural gas weekly resolutions 2024 (50)', 'https://www.micm.gob.do/transparencia/images/pdf/transparencia/base-legal-de-la-institucion/resoluciones/2024/ (50 natural gas files)', 'value found',
     'PPI in USD/MMBTU (Parrafo I) weekly; PPI fixed in pesos 592.25 then 504.97 DOP/MMBTU from 15 Jun; cost elements ad valorem, GAL, SICOEX, MDGNV, margins; public price 1,187.16 DOP/MMBTU', ['NGS']),
    ('sie_cne_micm', 'MICM weekly fuel price notices (avisos) 2024, 28 digital PDFs re-downloaded', 'https://micm.gob.do/wp-content/uploads/2024/ (28 files listed in sources_DR.csv)', 'value found',
     '28 weeks Jan to Aug 2024 parsed (dr_parse_avisos.py); all 396 product rows add up to the official price; diesel EGP-C gasoil parity, fuel oil No. 6 parity and distributor margins confirmed', LIQ),
    ('sie_cne_micm', 'MICM quarterly weekly price history 2024 (8 xlsx)', 'https://www.micm.gob.do/transparencia/estadisticas-institucionales/estadisticas-combustibles/category/estadisticas-2033', 'value found',
     'weekly price paid by public by product; used to derive PPI for unfrozen rows (EGP-C gasoil, avtur, fuel oil) for weeks without a digital aviso; derived values match the 28 aviso weeks except 20 to 26 Jan, where the xlsx repeats the previous week', ['DSL', 'FOI', 'JET']),
    ('sie_cne_micm', 'MICM open-data workbook precios de combustibles 2010-2025', 'https://micm.gob.do/transparencias/datos-abiertos/precios-de-combustibles/precios-de-combustibles-2010-2025.xlsx', 'blocked HTTP 403',
     'same result as the earlier job; put on manual list', LIQ),
    ('sie_cne_micm', 'MICM open-data file precios de combustibles 2010-2026 (link from datos.gob.do)', 'https://micm.gob.do/transparencias/datos-abiertos/precios-de-combustibles/precios-de-combustibles-2010-2026.csv', 'no value',
     'opens (HTTP 200, csv and xlsx) but holds only weekly prices paid by the public, tax included, rounded to whole pesos; no PPI or margins', LIQ),
    ('sie_cne_micm', 'MICM page of 2024 weekly avisos (digital notices for Sep to Dec)', 'https://micm.gob.do/direcciones/combustibles/avisos-semanales-de-precios/avisos-semanales-de-precios-de-combustibles/avisos-semanales-de-precios-de-combustibles-2024/', 'blocked HTTP 403',
     'scanned resolutions used instead for those weeks; put on manual list', LIQ),
    ('sie_cne_micm', 'Superintendencia de Electricidad home page (fuel costs of generators, tariff studies)', 'https://www.sie.gob.do/', 'blocked HTTP 403', 'put on manual list', ['COA', 'NGS', 'FOI', 'DSL']),
    ('sie_cne_micm', 'CNE document search (wp-json media search for balance)', 'https://cne.gob.do/wp-json/wp/v2/media?search=balance&per_page=100', 'blocked HTTP 403', 'put on manual list', ['COA', 'COK', 'NGS', 'FOI']),
    ('energy_balance', 'CNE SIEN methodology page of the national energy balance', 'https://sien.cne.gob.do/WebForms/Utilidades/contenido.aspx?archivo=contenido3.1.html', 'value found',
     'balance in kTep following OLADE methodology; natural gas factor 0.83 Tep per thousand normal m3; no coal, petroleum coke or fuel oil factor and no net or gross statement on the page', ['NGS', 'COA', 'COK', 'FOI']),
    ('energy_balance', 'MEM WordPress media search for energy balance files', 'https://mem.gob.do/wp-json/wp/v2/media?search=Balance-Energetico&per_page=100', 'not found',
     'only TOMO-I.-BNEU-2018.pdf (useful energy balance 2018) is listed', ['COA', 'COK', 'NGS', 'FOI']),
    ('energy_balance', 'MEM Balance Nacional de Energia Util 2018, Tomo I', 'https://mem.gob.do/wp-content/uploads/2020/07/TOMO-I.-BNEU-2018.pdf', 'no value', 'no calorific factors and no prices', ['COA', 'COK', 'NGS', 'FOI']),
    ('energy_balance', 'OLADE library documents with national balances', 'https://biblioteca.olade.org/opac-tmpl/Documentos/old0445.pdf', 'blocked HTTP 403', 'put on manual list (SIELAC conversion factors)', ['COA', 'COK', 'NGS', 'FOI']),
    ('energy_balance', 'OLADE SIELAC numeric system (conversion factors by country)', 'https://sielac.olade.org/consultas/sistema-numerico.aspx?ss=2', 'no value',
     'home page opens but queries run only through browser scripts; put on manual list', ['COA', 'COK', 'NGS', 'FOI']),
    ('mem_bulletins', 'MEM Boletin anual de Generacion y Gestion de Energia 2024', 'https://mem.gob.do/wp-content/uploads/2025/01/Boletin-Informativo-Generacion-y-Gestion-Energia-2024-V.2.pdf', 'value found',
     'Platts 2024 annual averages USD/MMBTU: LNG TTF 13.46, NYMEX 2.90, coal FOB Bolivar 3.59, FO No.6 10.96, FO No.2 15.55; international FOB references, not delivered prices; recorded in notes only', ['COA', 'NGS', 'FOI', 'DSL']),
    ('mem_bulletins', 'MEM monthly bulletins Generacion y Gestion de Energia Feb, Apr, Sep, Nov, Dec 2024 (re-downloaded)', 'https://mem.gob.do/wp-content/uploads/2024/03/02.-Boletin-Informativo-Generacion-y-Gestion-Energia-Febrero-2024-v2.pdf (and four other months)', 'no value',
     'monthly Platts references only (same series as the annual bulletin) and plant variable costs in USD/MWh; no delivered fuel price; no petroleum coke', ['COA', 'COK', 'NGS', 'FOI', 'DSL']),
    ('mem_bulletins', 'MEM WordPress media list of 2024 bulletins (Platts quotes for gasoline and LPG)', 'https://mem.gob.do/wp-json/wp/v2/media?search=Boletin-Informativo&per_page=100', 'no value',
     'all 2024 generation bulletins listed; they quote LNG, coal, FO No.6 and FO No.2 only; no gasoline or LPG quote', ['GSL', 'LPG']),
    ('ocseni', 'OC-SENI Memoria Anual 2024 (DMX download)', 'https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?Command=Core_Download&EntryId=200289&PortalId=0&TabId=234', 'value found',
     'section 6.2 charts of monthly fuel costs declared by agents: coal (DOP per tonne) and natural gas (DOP/MMBTU) digitised from the vector charts; table 31 gives USGC HSFO 68.58 USD/bbl', ['COA', 'NGS']),
    ('ocseni', 'OC-SENI Memoria Anual 2024, Figura 44 fuel oil No.6 and No.2 declared costs', 'https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?Command=Core_Download&EntryId=200289&PortalId=0&TabId=234', 'no value',
     'series drawn as filled outlines; month alignment of the digitised points is uncertain, so no value recorded (rough 2024 level about 115 DOP/gal for No.6, consistent with MICM EGP-C)', ['FOI', 'DSL']),
    ('ocseni', 'OC-SENI Programacion del SENI, Programacion Semanal folder (weekly programmes with declared fuel prices)', 'https://www.oc.do/Informes-Hist%C3%B3ricos/Operaci%C3%B3n-del-SENI/Programaci%C3%B3n-del-SENI', 'no value',
     'folder (EntryId 115720) contents load only through browser scripts; current reports are in a Dropbox folder; put on manual list', ['COA', 'NGS', 'FOI', 'DSL']),
    ('ocseni', 'OC-SENI Transacciones Economicas y Calculos Comerciales (monthly)', 'https://www.oc.do/Informes/Administraci%C3%B3n-del-MEM/Transacciones-Econ%C3%B3micas-y-C%C3%A1lculos-Comerciales', 'no value',
     'page lists no files without browser scripts; put on manual list', ['COA', 'NGS', 'FOI', 'DSL']),
    ('customs_national', 'BCRD external sector statistics page (petroleum imports by product)', 'https://www.bancentral.gov.do/a/d/2532-sector-externo', 'no value',
     'page opens but lists no downloadable files without browser scripts', ALLF),
    ('customs_national', 'BCRD Informe de la Economia Dominicana enero-diciembre 2024', 'https://cdn.bancentral.gov.do/documents/publicaciones-economicas/informe-de-la-economia-dominicana/documents/infeco_definitivo2024-12.pdf', 'no value',
     'import values only (coal 260.3 million USD, crude 752.5 million USD, petroleum imports 4,734.1 million USD); no volumes or unit prices', ['COA', 'CRU', 'GSL', 'LPG', 'DSL', 'FOI']),
    ('customs_national', 'BCRD economy report URL guesses for 2024', 'https://cdn.bancentral.gov.do/documents/publicaciones-economicas/informe-de-la-economia-dominicana/documents/infeco_2024-12.pdf', 'not found', 'HTTP 404 for five URL patterns', ['COA', 'CRU']),
    ('customs_national', 'Web search for BCRD per-barrel import prices 2024 by product', 'web search: Banco Central Republica Dominicana importaciones petroleras volumen valor precio por barril 2024', 'not found',
     'press quotes of per-barrel prices could not be traced to a BCRD file', ['GSL', 'LPG', 'DSL', 'FOI', 'CRU']),
    ('dga_one_refidomsa', 'DGA statistics, series de tiempo', 'https://www.aduanas.gob.do/estadisticas/series-de-tiempo/', 'no value',
     'values by tariff chapter only (no HS 6-digit, no quantities); tables render through browser scripts', ALLF),
    ('dga_one_refidomsa', 'Oficina Nacional de Estadistica home page (trade statistics)', 'https://www.one.gob.do/', 'blocked HTTP 403', 'put on manual list', ALLF),
    ('dga_one_refidomsa', 'REFIDOMSA website (crude purchases, annual report)', 'https://www.refidomsa.com/', 'blocked HTTP 403', 'also refidomsa.com/transparencia/ and wp-json; put on manual list', ['CRU', 'GSL', 'DSL', 'FOI', 'LPG']),
    ('comtrade', 'UN Comtrade DR imports 2024, HS 4-digit', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711', 'value found',
     '2709 crude CIF and net weight; 2710 and 2711 and 2701 have no weight at 4 digits', ['CRU', 'COK']),
    ('comtrade', 'UN Comtrade DR imports 2024, HS 6-digit', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=2024&partnerCode=0&flowCode=M&cmdCode=270112,271012,271019,271111,271112,271113,271119,271121,271311,271312', 'value found',
     '270112, 271311, 271111, 271112, 271113 with CIF and weight; 271012 and 271019 have no quantity', ['COA', 'COK', 'NGS', 'LPG']),
    ('comtrade', 'UN Comtrade DR imports 2024, HS 271012 and 271019', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=2024&partnerCode=0&flowCode=M&cmdCode=270112,271012,271019,271111,271112,271113,271119,271121,271311,271312', 'no value',
     'CIF value published but quantity 0 and no weight', ['GSL', 'DSL', 'FOI', 'KER', 'JET']),
    ('comtrade', 'UN Comtrade US exports to DR 2024 (mirror)', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2024&partnerCode=214&flowCode=X&cmdCode=271012,271019,271112,271113,271111,270112,271311,2709', 'value found',
     '271012 FOB and barrels (market-tracking gasoline); 2709 FOB and barrels as crude cross-check; US weights are volume based', ['GSL', 'CRU']),
    ('comtrade', 'UN Comtrade DR imports 2018 to 2025 (one year per query)', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=214&period=<year>&partnerCode=0&flowCode=M&cmdCode=270112,271311,271111,271112,271113,2709', 'value found',
     'history_DR.csv; 2018 and 2020 have no CIF value; several weights flagged as estimated', ['COA', 'COK', 'NGS', 'LPG', 'CRU']),
    ('other_cepal', 'CEPAL Centroamerica y la Republica Dominicana: estadisticas de hidrocarburos (2023 data edition; 2024 edition)', 'https://www.cepal.org/es/publicaciones/82024-centroamerica-la-republica-dominicana-estadisticas-hidrocarburos-2023', 'blocked HTTP 403',
     'publication page refused the fetch tool; no 2024 data edition found by search; put on manual list', ['GSL', 'LPG', 'DSL', 'FOI', 'CRU']),
    ('ocseni', 'OC-SENI Memoria Anual 2024, fuels other than coal, gas and fuel oil', 'https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?Command=Core_Download&EntryId=200289&PortalId=0&TabId=234', 'no value',
     'no petroleum coke or crude cost in the SENI fuel cost figures (no SENI plant burns them)', ['COK', 'CRU']),
    ('mem_bulletins', 'MEM Boletin anual de Generacion y Gestion de Energia 2024, other fuels', 'https://mem.gob.do/wp-content/uploads/2025/01/Boletin-Informativo-Generacion-y-Gestion-Energia-2024-V.2.pdf', 'no value',
     'no crude, petroleum coke, gasoline or LPG reference in the commodity chart', ['CRU', 'COK', 'GSL', 'LPG']),
    ('sie_cne_micm', 'MICM weekly resolutions and avisos 2024, solid fuels and crude', 'https://www.micm.gob.do/transparencia/base-legal-de-la-institucion/category/resoluciones-precios-combustibles-2024', 'no value',
     'MICM sets no price for coal, petroleum coke or crude', ['COA', 'COK', 'CRU']),
    ('energy_balance', 'CNE SIEN methodology page, crude oil and refinery section', 'https://sien.cne.gob.do/WebForms/Utilidades/contenido.aspx?archivo=contenido3.1.html', 'no value',
     'crude imports sourced from REFIDOMSA and BCRD in the balance; no price or calorific factor for crude on the page', ['CRU']),
    ('other_bcrd_fx', 'BCRD reference exchange rate file (re-download)', 'https://cdn.bancentral.gov.do/documents/estadisticas/mercado-cambiario/documents/TASA_DOLAR_REFERENCIA_MC.xlsx', 'value found',
     'sheet PromAnual 2024: buying 59.2507, selling 59.5665 DOP/USD; DR_FX_2024 = 59.5665 confirmed', ['ALL']),
]
with open(os.path.join(OUT, 'search_log_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['country', 'fuel', 'lead_id', 'lead', 'url_or_query', 'date', 'result', 'detail'])
    n = 0
    for lid, lead, url, res, det, fuels in A:
        for f in fuels:
            w.writerow(['DominicanRepublic', f, lid, lead, url, D, res, det])
            n += 1
print('search log rows', n)

M = [
    ('https://www.oc.do/Informes-Hist%C3%B3ricos/Operaci%C3%B3n-del-SENI/Programaci%C3%B3n-del-SENI', 'Programacion Semanal 2024 (weekly operation programmes, folder EntryId 115720) and the Dropbox folder linked from https://www.oc.do/Informes/Operaci%C3%B3n-del-SENI/Programaci%C3%B3n-del-SENI',
     'Organismo Coordinador del SENI', 'weekly fuel prices and variable costs declared by each generator (Punta Catalina, Itabo, Barahona, AES Andres, fuel oil and diesel plants) for 2024',
     'COA DIST_COA, NGS DIST_NGS, FOI DIST_FOI, DSL DIST_DSL generator delivered', 'replaces values digitised from charts with tabulated plant prices', 'folder contents load only through browser scripts (DMX module, Dropbox)', 'DR_OC_programacion_semanal_2024.zip', 1),
    ('https://www.oc.do/Informes/Administrativos/Memoria-Anual', 'Memoria Anual folder Tablas (EntryId 176167)', 'Organismo Coordinador del SENI', 'data tables behind the Memoria figures, including monthly fuel costs declared by agents 2001-2024',
     'COA DIST_COA, NGS DIST_NGS, FOI DIST_FOI generator delivered', 'tabulated monthly coal, gas and fuel oil costs instead of digitised chart points', 'folder entry, not a file; contents load only through browser scripts', 'DR_OC_memoria_tablas_2024.xlsx', 1),
    ('https://www.oc.do/Informes/Administraci%C3%B3n-del-MEM/Transacciones-Econ%C3%B3micas-y-C%C3%A1lculos-Comerciales', 'Informes de Transacciones Economicas mensuales 2024', 'Organismo Coordinador del SENI', 'monthly economic transactions with variable costs and fuel prices used for dispatch',
     'COA, NGS, FOI, DSL generator delivered', 'second operator source for generator fuel prices', 'page lists no files without browser scripts', 'DR_OC_transacciones_2024.zip', 1),
    ('https://sielac.olade.org/consultas/sistema-numerico.aspx?ss=2', 'SIELAC conversion factors, Dominican Republic', 'OLADE', 'calorific values (net, per OLADE methodology) for natural gas, coal, petroleum coke and fuel oil used in the DR balance',
     'calorific_DR.csv (COA, COK, NGS, FOI factors)', 'national balance page gives only the natural gas factor and no basis statement', 'query runs only through browser scripts; OLADE library PDFs return HTTP 403', 'DR_OLADE_SIELAC_factores_conversion.xlsx', 1),
    ('https://cne.gob.do/', 'Balance Energetico Nacional (latest year) and its methodology annex', 'Comision Nacional de Energia', 'national balance with conversion factors and calorific basis',
     'calorific_DR.csv', 'the balance behind the model quantities', 'wp-json document search returns HTTP 403; SIEN numeric system needs browser scripts', 'DR_CNE_balance_energetico.pdf', 1),
    ('https://www.one.gob.do/', 'ONE foreign trade statistics 2024 by HS code', 'Oficina Nacional de Estadistica', 'imports of coal (2701) and petroleum coke (2713) with value and weight',
     'COA DIST_COA, COK DIST_COK import CIF (national source)', 'national customs statistics as first source instead of Comtrade', 'HTTP 403', 'DR_ONE_importaciones_2024.xlsx', 2),
    ('https://www.aduanas.gob.do/estadisticas/dashboard/', 'DGA statistics dashboard', 'Direccion General de Aduanas', 'imports 2024 by tariff line with CIF value and weight, if offered',
     'COA, COK, CRU, GSL, LPG import CIF (national source)', 'national customs statistics; DR Comtrade has no quantity for 271012 and 271019', 'series pages give chapter totals only; tables render through browser scripts', 'DR_DGA_importaciones_2024_hs27.xlsx', 2),
    ('https://www.sie.gob.do/', 'SIE publications on generation costs and fuel indexation', 'Superintendencia de Electricidad', 'fuel prices used in contract indexation or tariff studies 2024',
     'COA, NGS, FOI, DSL generator delivered', 'regulator cross-check of operator values', 'HTTP 403', 'DR_SIE_publicaciones_2024.pdf', 3),
    ('https://micm.gob.do/direcciones/combustibles/avisos-semanales-de-precios/avisos-semanales-de-precios-de-combustibles/avisos-semanales-de-precios-de-combustibles-2024/', 'MICM weekly avisos 2024 page (digital notices Sep to Dec 2024)', 'MICM',
     'digital avisos for the 22 weeks covered here only by scanned resolutions', 'FOI, DSL, GSL, LPG, KER, JET (all weeks; confirmation of image reads)', 'typed values instead of scanned pages', 'HTTP 403', 'DR_MICM_avisos_2024_sep_dec.zip', 4),
    ('https://micm.gob.do/transparencias/datos-abiertos/precios-de-combustibles/precios-de-combustibles-2010-2025.xlsx', 'Precios de combustibles 2010-2025 (open data workbook)', 'MICM', 'weekly prices 2010-2025 (the 2010-2026 csv that opens has retail prices only)',
     'history of liquids', 'possible history series', 'HTTP 403 (retried this session)', 'DR_MICM_precios_combustibles_2010_2025.xlsx', 4),
    ('https://www.refidomsa.com/', 'REFIDOMSA annual report or memoria 2024', 'Refineria Dominicana de Petroleo (REFIDOMSA)', 'crude purchase volumes and cost 2024; product import costs',
     'CRU DIST_CRU (import CIF, local source)', 'local source for the crude row now based on Comtrade', 'HTTP 403', 'DR_REFIDOMSA_memoria_2024.pdf', 6),
    ('https://www.cepal.org/es/publicaciones/82024-centroamerica-la-republica-dominicana-estadisticas-hidrocarburos-2023', 'Centroamerica y la Republica Dominicana: estadisticas de hidrocarburos (2024 data edition when published)', 'CEPAL', 'DR import volumes and values by product, prices',
     'GSL, LPG, DSL, FOI, CRU import cost cross-check', 'regional second source for market-tracking import cost', 'HTTP 403 to the fetch tool; 2024 data edition not found', 'DR_CEPAL_hidrocarburos_2024.pdf', 6),
]
with open(os.path.join(OUT, 'manual_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['url', 'title', 'publisher', 'should_hold', 'rows_it_closes', 'why_needed', 'how_failed', 'save_as', 'weight_rank'])
    for r in sorted(M, key=lambda r: r[-1]):
        w.writerow(r)
print('manual rows', len(M))

with open(os.path.join(OUT, 'calorific_DR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['country', 'balance', 'publisher', 'url', 'net_or_gross', 'factor_NGS', 'factor_COA', 'factor_COK', 'factor_FOI', 'factor_units', 'page_or_table', 'source_id'])
    w.writerow(['DominicanRepublic', 'Balance Energetico Nacional (SIEN, kTep, OLADE methodology)', 'Comision Nacional de Energia',
                'https://sien.cne.gob.do/WebForms/Utilidades/contenido.aspx?archivo=contenido3.1.html', 'not stated', '0.83', '', '', '',
                'NGS: toe per thousand normal m3 (equals 34.75 MJ per normal m3, a level typical of net calorific value); COA, COK, FOI factors not published on the page',
                'Metodologia, sections Gas Natural, Carbon Mineral, Coque, Fuel Oil', 'DR-009'])
print('calorific rows 1')
