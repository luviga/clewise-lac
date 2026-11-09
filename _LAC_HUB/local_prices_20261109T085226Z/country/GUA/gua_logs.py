"""Write search_log_GUA.csv and manual_GUA.csv for job LAC_LOCAL_PRICES 20261109T085226Z.

Usage: py -I gua_logs.py <country GUA output folder>
One search-log row per attempt per fuel.
"""
import csv
import os
import sys

D = '2026-11-09'
ALL = ['COA', 'COK', 'NGS', 'FOI', 'DSL', 'GSL', 'LPG', 'KER']
LIQ = ['FOI', 'DSL', 'GSL', 'LPG', 'KER']
STRUCT = ['FOI', 'DSL', 'GSL', 'LPG']

# (fuels or {fuel: (result, detail)}, lead_id, lead, url_or_query, default result, default detail)
A = [
    ({'COA': ('value found', 'line 2701120000 bituminous coal 207199655 USD, 1458913000 kg (142.02 USD/t CIF); 2701190000 other coal 25945614 USD, 194997532 kg'),
      'COK': ('value found', 'line 2713110000 petroleum coke not calcined 91719961 USD, 914167966 kg (100.33 USD/t CIF)'),
      'NGS': ('no value', 'no 2711.11 (LNG) or 2711.21 (natural gas) line in 2024: no natural gas imports'),
      'FOI': ('value found', 'line 2710192200 fuel oil No. 6 bunker C 163931638 USD, 364452218 kg (449.80 USD/t)'),
      'DSL': ('value found', 'line 2710192100 diesel oil 1634735346 USD, 2149528909 kg (760.51 USD/t)'),
      'GSL': ('value found', 'line 2710123000 motor gasoline 1834548119 USD, 2250781418 kg (815.07 USD/t)'),
      'LPG': ('value found', 'line 2711120000 propane 469884502 USD, 708578417 kg (663.14 USD/t)'),
      'KER': ('value found', 'line 2710191200 other kerosenes 33150 USD, 14774 kg (2243.81 USD/t, volume too small to represent a price)')},
     'customs_national', 'Banguat imports by tariff line, Comercio General 2024 (KF-103)',
     'https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/2024/CG/KF-103_2024.xlsx', '', ''),
    ({'COA': ('value found', 'Cuadro 4 title VALOR (CIF); footnote hulla bituminosa January 2024 US$5,722.0 thousand and 48,213.4 thousand kg equals KF-103 line 2701120000 January, so KF-103 values are CIF')},
     'banguat', 'Banguat Cuadro 4 imports CIF by CUODE, Comercio General 2024',
     'https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/CG/2024/ceie04.htm', 'no value',
     'CUODE aggregates only (combustibles y lubricantes); used to confirm that Banguat import values are CIF'),
    ({'COA': ('value found', 'origin of 2701120000: Colombia only; 2701190000: United States only'),
      'COK': ('value found', 'origin of 2713110000: United States 909983110 kg, Mexico 4184856 kg'),
      'FOI': ('value found', 'origin of 2710192200: Ecuador, Bahamas, US Virgin Islands, Peru, Curacao, United States, Belize')},
     'banguat', 'Banguat imports by tariff line and origin country, Comercio General 2024 (KF-116 Origen)',
     'https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/2024/CG/Origen/KF-116_2024.xlsx', 'no value', 'not needed beyond the national totals'),
    (['COA', 'COK', 'FOI', 'DSL', 'GSL', 'LPG'], 'banguat', 'Banguat imports by tariff line, Comercio General 2018 to 2023 and 2025 (KF-103), for history',
     'https://banguat.gob.gt/sites/default/files/banguat/estaeco/ceie/hist/pdfs/<year>/CG/KF-103_<year>.xlsx (years 2018 2019 2020 2021 2022 2023 2025)',
     'value found', 'annual value and kg for the same lines; written to history_GUA.csv'),
    ({'COA': ('value found', 'cmdCode 270112 cifvalue 207127946 USD, netWgt 1458300000 kg (142.03 USD/t); 270119 25945614 USD'),
      'COK': ('value found', 'cmdCode 271311 cifvalue 91719961 USD, netWgt 914168860 kg (100.33 USD/t)'),
      'NGS': ('no value', 'no record for 271111 or 271121: no natural gas imports in 2024'),
      'FOI': ('no value', '271019 mixes diesel and fuel oil (2128302966 USD, 2730613690 kg); no 8-digit split in the preview API'),
      'DSL': ('no value', '271019 mixes diesel and fuel oil (2128302966 USD, 2730613690 kg)'),
      'GSL': ('no value', '271012 mixes motor gasoline, aviation gasoline and other light oils (1840876198 USD, 2259235640 kg)'),
      'LPG': ('value found', '271112 propane 471505109 USD, 710112478 kg (663.98 USD/t); not recorded as a row because the national Banguat line is the same flow'),
      'KER': ('no value', 'kerosene sits inside 271019 with diesel and fuel oil')},
     'comtrade', 'UN Comtrade public preview API, Guatemala imports 2024',
     'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=320&period=2024&partnerCode=0&flowCode=M&cmdCode=2701,2713,2709,2710,2711,270112,270119,271311,271312,271012,271019,271111,271112,271113,271119,271121,271020', '', ''),
    (STRUCT, 'mem_gua', 'MEM weekly Estructuras de Precios referenciales 2024 (direct file URLs)',
     'https://mem.gob.gt/wp-content/uploads/<yyyy>/<mm>/Estructuras-de-Precios-referenciales-al-<dd>-<mes>-2024.pdf (35 files; list in sources_GUA.csv)',
     'value found', '35 of 52 weeks downloaded and parsed (31 known before, 4 new: 30 Sep, 7 Oct, 14 Oct, 21 Oct); components add to the published total in every slide'),
    (STRUCT, 'mem_gua', 'MEM weekly structures, probe of file names for the 17 missing weeks (date Monday to Wednesday, upload folders month to month+2, suffixes none and -1)',
     'https://mem.gob.gt/wp-content/uploads/<yyyy>/<mm>/Estructuras-de-Precios-referenciales-al-<dd>-<mes>-2024[-1].pdf (396 candidate URLs)',
     'not found', 'HTTP 404 for every candidate covering 26 Feb, 4, 11, 18 Mar, 29 Apr, 29 Jul, 5, 12, 19, 26 Aug, 2, 9 Sep, 4, 18, 25 Nov, 2, 9, 30 Dec'),
    (STRUCT, 'mem_gua', 'MEM weekly structures, probe of five alternative file names for the missing weeks',
     'https://mem.gob.gt/wp-content/uploads/<yyyy>/<mm>/{Estructura-de-Precios-referenciales-al,Estructuras-de-precios-referenciales-al,Estructuras-de-Precios-Referenciales-al,Estructuras-de-Precios-referenciales}-<dd>-<mes>-2024[-2].pdf (180 candidate URLs)',
     'not found', 'HTTP 404 for every candidate'),
    (LIQ, 'mem_gua', 'MEM WordPress media index (list of uploaded files)',
     'https://mem.gob.gt/wp-json/wp/v2/media?search=Estructuras-de-Precios&per_page=100&after=2024-01-01T00:00:00&before=2025-12-31T00:00:00',
     'blocked HTTP 403', 'Cloudflare challenge page; put on manual list'),
    (LIQ, 'mem_gua', 'MEM page Historico precios nacionales', 'https://mem.gob.gt/historico-precios-nacionales/', 'blocked HTTP 403', 'Cloudflare challenge page; put on manual list'),
    (LIQ, 'mem_gua', 'MEM page Historico precios nacionales (site host)', 'https://site.mem.gob.gt/historico-precios-nacionales/', 'blocked HTTP 403', 'Cloudflare challenge page'),
    (LIQ, 'mem_gua', 'MEM page Precios combustible nacionales', 'https://mem.gob.gt/que-hacemos/hidrocarburos/comercializacion-downstream/precios-combustible-nacionales/', 'blocked HTTP 403', 'Cloudflare challenge page; put on manual list'),
    ({'KER': ('value found', 'kerosene consumer price Guatemala City 37.00 GTQ/gal every month January to October 2024; series 2002 to 2024'),
      'FOI': ('value found', 'bunker consumer price Guatemala City, January to October 2024, mean 19.0885 GTQ/gal')},
     'mem_gua', 'MEM Precios promedio de combustibles a consumidor final, ciudad capital (otros combustibles), workbook to October 2024',
     'https://mem.gob.gt/wp-content/uploads/2024/11/PRECIOS-OTROS-COMBUSTIBLES-MENSUALES-OCTUBRE-2024.xlsx', '', ''),
    ({'KER': ('value found', 'January to March 2024 kerosene 37.00 GTQ/gal; superseded by the October workbook'),
      'FOI': ('value found', 'January to March 2024 bunker; superseded by the October workbook')},
     'mem_gua', 'MEM Otros combustibles marzo 2024 (PDF)', 'https://mem.gob.gt/wp-content/uploads/2024/04/Otros-Combustibles-marzo-2024.pdf', '', ''),
    (['KER', 'FOI'], 'mem_gua', 'MEM other-fuel monthly prices for November and December 2024 (probe of 80 file names in folders 2024/12 to 2025/04)',
     'https://mem.gob.gt/wp-content/uploads/<yyyy>/<mm>/{PRECIOS-OTROS-COMBUSTIBLES-MENSUALES,REPORTE-OTROS-COMBUSTIBLES,Precios-promedio-MENSUALES-OTROS-COMBUSTIBLES,Otros-Combustibles,PRECIOS-OTROS-COMBUSTIBLES}-<MES>-<yyyy>.{xlsx,pdf}',
     'not found', 'HTTP 404 for every candidate; November and December 2024 missing'),
    ({'FOI': ('value found', 'bunker 2024: 185353689 USD for 2174591 bbl (85.24 USD/bbl), June 204.37 USD/bbl is an outlier; without June 69.6 USD/bbl; not used, MEM does not state CIF or FOB'),
      'DSL': ('value found', 'diesel bajo azufre 2024: 102.01 USD/bbl; not used (basis not stated)'),
      'GSL': ('value found', 'gasolina regular 96.85, superior 102.10 USD/bbl in 2024; not used'),
      'LPG': ('value found', 'GLP 52.82 USD/bbl in 2024; not used'),
      'KER': ('value found', 'kerosina: only August 2024, 10830 USD for 71.43 bbl (151.62 USD/bbl); not representative'),
      'COK': ('value found', 'petcoke 298199093 USD for 4898556 units labelled barrels; monthly unit values 14.59 to 146.95, inconsistent with customs (91.7 million USD); not used'),
      'COA': ('no value', 'tables cover petroleum products and petcoke only, no coal column'),
      'NGS': ('no value', 'no natural gas column')},
     'mem_gua', 'MEM DGH monthly import cost (USD) and import volume (barrels), to December 2024',
     'https://mem.gob.gt/wp-content/uploads/2025/01/COSTO-IMPORTACION-HIDROCARBUROS-2024-12.xlsx ; https://mem.gob.gt/wp-content/uploads/2025/01/IMPORTACION-HIDROCARBUROS-VOLUMEN-2024-12.xlsx', '', ''),
    (['COA', 'COK', 'NGS'], 'mem_gua', 'MEM Revista Hidrocarburos third quarter 2024', 'https://mem.gob.gt/wp-content/uploads/2024/12/Revista-Hidrocarburos-2024-03T.pdf',
     'no value', 'national crude price, international crude and gas benchmarks, import volumes; no coal, petcoke or gas import or delivered price'),
    ({'COA': ('value found', 'factor 1 ton de carbon mineral = 5.0439 BEP (basis not stated)'),
      'COK': ('value found', 'factor 1 ton de coque de petroleo = 4.8998 BEP'),
      'FOI': ('value found', 'factor 1 bbl de fuel oil = 1.0685 BEP'),
      'NGS': ('no value', 'no natural gas factor (no gas in the 2010 balance)')},
     'energy_balance', 'MEM Balance Energetico 2010 (factor table)', 'https://www.mem.gob.gt/wp-content/uploads/2012/06/INFORME_BALANCE_ENERGETICO.pdf', '', ''),
    (['COA', 'COK', 'NGS', 'FOI'], 'energy_balance', 'MEM Balance Energetico 2024', 'https://mem.gob.gt/wp-content/uploads/2025/07/BALANCE-ENERGETICO-2024.pdf',
     'no value', 'kBEP tables only; no conversion factors and no net or gross statement; no prices'),
    (['COA', 'COK', 'NGS', 'FOI'], 'energy_balance', 'MEM Balance Energetico 2023', 'https://mem.gob.gt/wp-content/uploads/2024/08/BALANCE-ENERGETICO-2023.pdf',
     'no value', 'kBEP tables only; no conversion factors'),
    (['COA', 'COK', 'NGS', 'FOI'], 'energy_balance', 'MEM Balance Energetico 2017 and 2018',
     'https://www.mem.gob.gt/wp-content/uploads/2018/08/BALANCE-ENERGETICO-2017.pdf ; https://mem.gob.gt/wp-content/uploads/2020/10/BALANCE-ENERGETICO-2018.pdf',
     'no value', 'kBEP tables only; no conversion factors'),
    (['COA', 'COK', 'NGS', 'FOI'], 'energy_balance', 'MEM balance publication page', 'https://mem.gob.gt/que-hacemos/area-energetica/publicaciones/estadisticas/balance-energetico/',
     'blocked HTTP 403', 'Cloudflare challenge page'),
    (['COA', 'COK', 'NGS', 'FOI'], 'other_olade', 'OLADE Energy Statistics Manual 2017 (SIELAC methodology, net or gross basis)',
     'https://www.olade.org/en/publicaciones/energy-statistics-manual-2017/ (redirects to https://www.olacde.org/en/publicaciones/energy-statistics-manual-2017/)',
     'blocked HTTP 403', 'put on manual list'),
    (['COA', 'FOI', 'DSL', 'NGS', 'COK'], 'amm', 'AMM Programacion de Largo Plazo mayo 2024 a abril 2025 (section 1.7 fuel prices and variable costs)',
     'https://www.amm.org.gt/pdfs2/programas_despacho/03_PROGRAMAS_DE_LARGO_PLAZO/2024-2025/01_PLP20240101_VP.pdf',
     'no value', 'fuel prices shown only as a chart of EIA STEO and Argus-McCloskey API2 projections; declared inventory costs not published; table 16 gives projected variable costs per plant in US$/MWh only (San Jose 68.66, Jaguar Energy 66.20 US$/MWh in May 2024)'),
    (['COA', 'FOI', 'DSL', 'NGS'], 'amm', 'AMM Programacion de despacho trimestral mayo a julio 2024',
     'https://www.amm.org.gt/pdfs2/programacion_trimensual/TRIMENSUAL/2024/01_PROGRAMACION/05EDT2024.pdf',
     'no value', 'section 1.9.1 says declared gas, coal, bunker and diesel prices are used but publishes none; fuel requirement volumes only'),
    (['COA', 'COK', 'FOI', 'DSL', 'NGS'], 'amm', 'AMM weekly dispatch program workbook (structure check with the latest file)',
     'https://www.amm.org.gt/pdfs2/programas_despacho/02_PROGRAMAS_DE_DESPACHO_SEMANAL/2026/01_PROGRAMAS_DE_DESPACHO_SEMANAL/46_PDS20261108.xlsx',
     'no value', 'sheets CVG (variable cost US$/MWh), Exist Comb (fuel stocks, efficiency kWh/TM), Cargas parciales; no fuel prices, so 2024 weekly files would not give them either'),
    (['COA', 'FOI', 'DSL', 'NGS'], 'amm', 'AMM Informe estadistico 2024', 'https://www.amm.org.gt/pdfs2/informes/2024/INFEST20240101_01(FINAL_PDF).pdf',
     'no value', 'generation by fuel and spot prices; no fuel prices'),
    (['COA', 'FOI'], 'amm', 'AMM Revista Digital, Analisis del Mercado Mayorista septiembre 2024', 'https://rd.amm.org.gt/2024/10/18/analisis-mm-septiembre-2024/',
     'no value', 'generation by fuel and spot prices; no fuel prices'),
    (['COA', 'COK', 'FOI', 'DSL', 'NGS'], 'amm', 'AMM private participant site (casillero) with generator declarations', 'https://wl12.amm.org.gt/sitioprivadocasillero/main.jsp',
     'login required', 'declared fuel inventory costs of thermal generators sit behind participant login'),
    (['COA', 'FOI', 'DSL', 'NGS'], 'amm', 'AMM reports site', 'https://reportesbi.amm.org.gt/', 'no value', 'HTTP 200 application shell with dynamic content and no downloadable file'),
    (['COA', 'FOI', 'DSL', 'NGS'], 'amm', 'AMM latest planning publications list', 'https://www.amm.org.gt/ultpub/ultimas_pub_plani.php',
     'no value', 'links to daily and weekly dispatch workbooks, maintenance reports and quarterly program; none carries fuel prices'),
    (['COA', 'FOI', 'NGS'], 'amm', 'web search: AMM Guatemala costos variables de generacion 2024 carbon bunker precio combustible pdf',
     'AMM Guatemala "costos variables de generacion" 2024 carbon bunker precio combustible pdf', 'no value',
     'results were AMM monthly market analyses and the long-term program; no fuel price file'),
    ({'COA': ('value found', 'coal for evaluation 23.81 MMBTU/TM (Colombia 6000 kcal NAR) and local internment plus transport 23.33 US$/MWh of output; no 2024 delivered price per tonne'),
      'COK': ('value found', 'petcoke for evaluation 29.76 MMBTU/TM (USGC 7500 kcal NAR) and 18.76 US$/MWh; no 2024 price'),
      'NGS': ('no value', 'gas energy price = Henry Hub x factor + FAGN (bidder adder for liquefaction and transport) + FGSC; regasification in the capacity price; no number published'),
      'FOI': ('no value', 'bunker indexed to Platts US Gulf No. 6; local costs CI offered by each bidder')},
     'cnee_peg', 'Bases de Licitacion PEG-5-2025 (CNEE-108-2025)',
     'https://peg-5-2025.com.gt/static/pdf/3.%20Bases%20de%20Licitaci%C3%B3n%20PEG-5%20CNEE-108-2025.pdf', '', ''),
    (['NGS', 'COA'], 'cnee_peg', 'PEG-5 Manual de Evaluacion de Ofertas Economicas',
     'https://peg-5-2025.com.gt/static/pdf/4.%20Manual%20de%20Evaluaci%C3%B3n%20de%20Ofertas%20Economicas%20PEG-5%20CNEE-108-2025.pdf',
     'no value', 'procedure only; no fuel prices'),
    (['NGS'], 'cnee_peg', 'web search: PEG-5 adjudication results natural gas price', 'PEG-5 Guatemala adjudicacion resultados 2026 gas natural precio energia ofertado US$/MWh Henry Hub FAGN',
     'no value', 'news items on 57 awarded companies; no published gas adder or delivered gas price'),
    (['COA', 'NGS', 'FOI', 'DSL'], 'cnee_peg', 'CNEE Plan de Expansion Indicativo del Sistema de Generacion 2024-2054',
     'https://www.cnee.gob.gt/PlanesExpansion/2024-2054/PEG%202024-2054.pdf', 'no value',
     'section 4.3.2: fuel price projections shown only as charts built from EIA AEO 2023; no numbers'),
    (['COA', 'NGS', 'FOI'], 'cnee_peg', 'MEM Plan de Expansion Indicativo del Sistema de Generacion 2026-2050',
     'https://mem.gob.gt/wp-content/uploads/2026/01/PEIG_2026_2050_MEM.pdf', 'no value', 'charts 8 and 9 from EIA AEO; no local delivered price'),
    (['NGS', 'COA', 'FOI', 'DSL'], 'other_eor', 'Ente Operador Regional, Informe de Planeamiento Operativo 2024-2025 (update January 2024)',
     'https://www.enteoperador.org/archivos/download/Informe_Planeamiento_Operativo_2024-2025-Actualizacion_ene-2024.pdf', 'no value',
     'regional projections from EIA (Henry Hub, bunker, diesel, coal); not a Guatemalan delivered price'),
    (['FOI', 'DSL', 'GSL', 'KER', 'LPG'], 'other_sac', 'Arancel Centroamericano de Importacion (SAC) chapter 27, reproduction by eAduana',
     'https://www.eaduana.com/aranceles/arancel-centroamericano-de-importacion?page=70', 'value found',
     'meaning of lines 2710.12.30, 2710.19.11, 2710.19.12, 2710.19.21, 2710.19.22 used to read Banguat KF-103'),
    (['KER'], 'other_idp_law', 'Decreto 74-98 (IDP rates), Diario de Centro America 1998, Justia scan',
     'https://docs.costa-rica.justia.com/nacionales/modificaciones/decreto-no-74-1998-nov-17-1998.pdf', 'image only',
     'scanned page read from a PNG render: Kerosina Q0.50 per gallon; later reforms changed gasoline and fuel oil rates, no later kerosene rate found'),
    (['KER'], 'other_idp_law', 'web search: current IDP rate for kerosene', 'SAT Guatemala ley impuesto distribucion petroleo crudo combustibles derivados Kerosina Fuel Oil (Bunker C) tasas por galon',
     'no value', 'news on 2026 temporary IDP suspensions; no consolidated rate table'),
    (['DSL', 'GSL', 'LPG', 'KER'], 'energy_balance', 'MEM Balance Energetico 2024', 'https://mem.gob.gt/wp-content/uploads/2025/07/BALANCE-ENERGETICO-2024.pdf',
     'no value', 'kBEP tables only; no prices and no conversion factors'),
    (['GSL', 'LPG', 'KER'], 'amm', 'AMM Programacion de Largo Plazo mayo 2024 a abril 2025',
     'https://www.amm.org.gt/pdfs2/programas_despacho/03_PROGRAMAS_DE_LARGO_PLAZO/2024-2025/01_PLP20240101_VP.pdf',
     'no value', 'no power plant burns gasoline, LPG or kerosene; AMM files carry no price for these fuels'),
    (['DSL', 'GSL', 'LPG', 'KER'], 'cnee_peg', 'Bases de Licitacion PEG-5-2025 (CNEE-108-2025)',
     'https://peg-5-2025.com.gt/static/pdf/3.%20Bases%20de%20Licitaci%C3%B3n%20PEG-5%20CNEE-108-2025.pdf',
     'no value', 'tender fuels are bunker, coal, petroleum coke and natural gas only'),
]

MANUAL = [
    dict(url='https://wl12.amm.org.gt/sitioprivadocasillero/main.jsp', title='AMM private participant site: weekly declared fuel inventory costs of thermal generators 2024',
         publisher='Administrador del Mercado Mayorista (AMM)', should_hold='declared coal, bunker and diesel inventory costs per plant (San Jose, Jaguar Energy, Las Palmas, Magdalena and others), weeks 1 to 52 of 2024',
         rows_it_closes='DIST_COA generator delivered; DIST_FOI generator delivered; DIST_DSL generator delivered', why_needed='the only source of a delivered fuel price to Guatemalan power plants; AMM public files give variable costs in US$/MWh only',
         how_failed='login required (participant credentials)', save_as='GUA_amm_declared_fuel_costs_2024.xlsx', weight_rank=1),
    dict(url='https://www.olacde.org/en/publicaciones/energy-statistics-manual-2017/', title='OLADE Energy Statistics Manual 2017',
         publisher='OLADE', should_hold='SIELAC convention on net (lower) calorific values and default conversion factors for coal, petroleum coke, natural gas and fuel oil',
         rows_it_closes='calorific_GUA.csv basis for COA, COK, NGS, FOI', why_needed='MEM balances do not state net or gross basis',
         how_failed='blocked HTTP 403 (redirect from www.olade.org)', save_as='OLADE_Energy_Statistics_Manual_2017.pdf', weight_rank=1),
    dict(url='https://mem.gob.gt/historico-precios-nacionales/', title='MEM Historico precios nacionales',
         publisher='Ministerio de Energia y Minas (MEM)', should_hold='links to every 2024 weekly Estructuras de Precios referenciales file and the monthly other-fuel consumer prices for November and December 2024',
         rows_it_closes='DIST_FOI, DIST_DSL, DIST_GSL, DIST_LPG weekly gaps (17 weeks); DIST_KER and DIST_FOI consumer price November and December 2024',
         why_needed='17 of 52 weekly structures could not be found by file name', how_failed='blocked HTTP 403 (Cloudflare challenge)',
         save_as='GUA_mem_historico_precios_nacionales.html', weight_rank=4),
    dict(url='https://mem.gob.gt/wp-json/wp/v2/media?search=Estructuras-de-Precios&per_page=100&after=2024-01-01T00:00:00&before=2025-12-31T00:00:00',
         title='MEM WordPress media index, search Estructuras-de-Precios 2024 to 2025', publisher='Ministerio de Energia y Minas (MEM)',
         should_hold='exact URLs of all weekly price structure files uploaded for 2024', rows_it_closes='DIST_FOI, DIST_DSL, DIST_GSL, DIST_LPG weekly gaps',
         why_needed='file names for the missing weeks are unknown', how_failed='blocked HTTP 403 (Cloudflare challenge)', save_as='GUA_mem_media_estructuras_2024.json', weight_rank=4),
    dict(url='https://mem.gob.gt/que-hacemos/hidrocarburos/comercializacion-downstream/precios-combustible-nacionales/', title='MEM Precios combustible nacionales',
         publisher='Ministerio de Energia y Minas (MEM)', should_hold='current and archived price structures, ex-rack prices and other-fuel monthly prices',
         rows_it_closes='DIST_FOI, DIST_DSL, DIST_GSL, DIST_LPG, DIST_KER', why_needed='index of MEM price files', how_failed='blocked HTTP 403 (Cloudflare challenge)',
         save_as='GUA_mem_precios_combustible_nacionales.html', weight_rank=4),
]


def main(outdir):
    rows = []
    for spec, lead_id, lead, url, res, det in A:
        if isinstance(spec, dict):
            items = [(f, spec[f][0], spec[f][1]) for f in ALL if f in spec]
            if res:
                items += [(f, res, det) for f in ALL if f not in spec and f in ('COK', 'FOI', 'DSL', 'GSL', 'LPG', 'KER', 'NGS') and lead_id == 'banguat' and 'Cuadro 4' in lead]
        else:
            items = [(f, res, det) for f in spec]
        for f, r, d in items:
            rows.append(dict(country='Guatemala', fuel=f, lead_id=lead_id, lead=lead, url_or_query=url, date=D, result=r, detail=d))
    with open(os.path.join(outdir, 'search_log_GUA.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['country', 'fuel', 'lead_id', 'lead', 'url_or_query', 'date', 'result', 'detail'])
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(outdir, 'manual_GUA.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['url', 'title', 'publisher', 'should_hold', 'rows_it_closes', 'why_needed', 'how_failed', 'save_as', 'weight_rank'])
        w.writeheader()
        w.writerows(sorted(MANUAL, key=lambda m: m['weight_rank']))
    print('search_log rows', len(rows), 'manual', len(MANUAL))
    need = {'customs_national', 'comtrade', 'energy_balance', 'mem_gua', 'amm', 'cnee_peg', 'banguat'}
    for f in ALL:
        have = {r['lead_id'] for r in rows if r['fuel'] == f}
        print(f, 'missing leads:', sorted(need - have))


if __name__ == '__main__':
    main(sys.argv[1])
