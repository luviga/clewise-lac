"""Build the Costa Rica output CSVs for job LAC_LOCAL_PRICES 20261109T085226Z.

Usage: py -I build_cr.py <downloads_CR_dir> <out_dir>
Reads (all inside downloads/CR):
  aresep_monthly_2024_parsed.csv           (written by parse_aresep_cr.py from the 12 ARESEP resolutions)
  aresep_od_ObtenerComprasCombustibleRecope.json   (ARESEP open data, RECOPE purchase invoices)
  vuce_pt_tiempo.json, vuce_od_import_2701.json, vuce_od_import_2713.json  (PROCOMER / VUCE open data)
  comtrade_CR_2024_M_6digit.json           (UN Comtrade preview API)
  wb_wdi_PA.NUS.FCRF_CRI_2018_2025.json    (World Bank WDI official exchange rate)
Writes prices_CR.csv, history_CR.csv, constants_CR.csv in <out_dir>.
"""
import csv, json, os, sys, collections

DL, OUT = sys.argv[1], sys.argv[2]
P = lambda f: os.path.join(DL, f)

HEAD = ['country', 'fuel', 'model_code', 'price_point', 'year', 'fob', 'freight', 'insurance', 'port',
        'importer_terminal_margin', 'wholesale_margin', 'inland_freight', 'retail_margin', 'price_as_published',
        'currency', 'unit', 'period', 'months_covered', 'tax_treatment', 'calorific_basis', 'exchange_rate',
        'exchange_rate_constant', 'conversion_constants', 'value_usd_per_gj', 'evidence_class', 'source_id',
        'page_or_table', 'downloaded_file', 'derivation', 'notes']

RES_SRC = ['CR-%03d' % i for i in range(1, 13)]           # Jan..Dec 2024 resolutions
RES_FILES = ['CR/RE-0002-IE-2024.pdf', 'CR/RE-0013-IE-2024.pdf', 'CR/RE-0021-IE-2024.pdf', 'CR/RE-0034-IE-2024.pdf',
             'CR/RE-0040-IE-2024.pdf', 'CR/ALCA108_10_06_2024.pdf', 'CR/RE-0050-IE-2024.pdf', 'CR/RE-0059-IE-2024.pdf',
             'CR/RE-0062-IE-2024.pdf', 'CR/RE-0068-IE-2024.pdf', 'CR/RE-0076-IE-2024.pdf', 'CR/RE-0083-IE-2024.pdf']
RES_NAMES = 'RE-0002, RE-0013, RE-0021, RE-0034, RE-0040, RE-0043 (with rectification RE-0044), RE-0050, RE-0059, RE-0062, RE-0068, RE-0076, RE-0083 (all -IE-2024)'
MONTHS = 'prices in force Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec 2024 (one resolution per month)'
SRC_RES = ';'.join(RES_SRC)
FILES_RES = ';'.join(RES_FILES)
SRC_PURCH, SRC_CVG24, SRC_CVG25 = 'CR-013', 'CR-014', 'CR-015'
SRC_VUCE_2713, SRC_VUCE_2701, SRC_VUCE_T = 'CR-016', 'CR-017', 'CR-018'
SRC_VUCE_LNG, SRC_VUCE_NG = 'CR-019', 'CR-020'
SRC_CT4, SRC_CT6, SRC_WDI, SRC_IPCC = 'CR-021', 'CR-022', 'CR-023', 'CR-024'

NCV = {'DSL': 43.0, 'GSL': 44.3, 'JET': 44.1, 'KER': 43.8, 'FOI': 40.4, 'LPG': 47.3, 'AVG': 44.3}


def r4(x):
    return '' if x is None else ('%.4f' % x).rstrip('0').rstrip('.')


def r3(x):
    return '' if x is None else '%.3f' % x


# ---------------- exchange rate (WDI) ----------------
wdi = json.load(open(P('wb_wdi_PA.NUS.FCRF_CRI_2018_2025.json'), encoding='utf-8'))[1]
FX = {int(r['date']): r['value'] for r in wdi}
FX24 = FX[2024]

# ---------------- ARESEP monthly parsed values ----------------
mon = collections.defaultdict(dict)
for r in csv.DictReader(open(P('aresep_monthly_2024_parsed.csv'), encoding='utf-8')):
    if r['period'].startswith('2024'):
        mon[(r['product'], r['component'])][r['period']] = float(r['value'])


def mean12(prod, comp):
    d = mon[(prod, comp)]
    assert len(d) == 12, (prod, comp, len(d))
    return sum(d.values()) / 12.0


# LPG plantel pre-tax: subsidised terminal price without taxes (subsidy table); for months where that table
# was not text-readable (Jun, Jul) use the Por Tanto I.b price with tax per litre minus impuesto unico,
# which equals it in every other month.
lpg_pre = {}
for per in ['2024-%02d' % m for m in range(1, 13)]:
    ts = mon[('LPG', 'term_sub')].get(per)
    mc = mon[('LPG', 'masa_con_l')].get(per)
    alt = None if mc is None else mc - mon[('LPG', 'tax')][per]
    if ts is not None:
        assert alt is None or abs(ts - alt) < 0.02, (per, ts, alt)
        lpg_pre[per] = ts
    else:
        lpg_pre[per] = alt
LPG_PRE = sum(lpg_pre.values()) / 12.0

# ---------------- ARESEP open data purchases ----------------
pur = json.load(open(P('aresep_od_ObtenerComprasCombustibleRecope.json'), encoding='utf-8'))['value']
PMAP = {'Gasolina RON 91': 'GSL91', 'Gasolina RON 95': 'GSL95', 'Jet fuel A-1': 'JET', 'Jet Fuel A': 'JET', 'Av-Gas': 'AVG',
        'Bunker': 'FOI', 'LPG (70-30)': 'LPG'}


def pkey(name):
    if name.startswith('Di') and 'automotriz' in name:
        return 'DSL'
    if name.startswith('Bunker T') and name.endswith('ICE 2'):
        return 'FOI_ICE2'
    return PMAP.get(name)


agg = collections.defaultdict(lambda: collections.Counter())
for r in pur:
    k = pkey(r['producto'])
    if not k:
        continue
    a = agg[(r['anho'], k)]
    a['n'] += 1
    for f in ['litros', 'masa', 'costoFOB', 'costoFlete', 'costoSeguro', 'costoCIF', 'costoTrader', 'costoPortuario']:
        a[f] += (r[f] or 0)

DENS = {k: agg[(2024, k)]['masa'] / agg[(2024, k)]['litros'] for k in ['DSL', 'GSL91', 'GSL95', 'JET', 'AVG', 'FOI', 'FOI_ICE2', 'LPG']}
DNAME = {k: 'CR_DENS_%s_2024' % k for k in DENS}
FUEL_OF = {'DSL': 'DSL', 'GSL91': 'GSL', 'GSL95': 'GSL', 'JET': 'JET', 'KER': 'KER', 'AVG': 'AVG', 'FOI': 'FOI',
           'FOI_ICE2': 'FOI', 'FOI_ICE': 'FOI', 'LPG': 'LPG'}
CODE = {'DSL': 'IMPPURDSL', 'GSL': 'IMPPURGSL', 'JET': 'IMPKJF', 'KER': 'IMPKJF', 'AVG': 'IMPAVG', 'FOI': 'IMPFOI',
        'LPG': 'IMPLPG', 'COA': 'IMPCOA', 'COK': 'IMPCOK', 'NGS': 'IMPNGS'}
LABEL = {'DSL': 'diesel 50 ppm (Diesel para uso automotriz de 50 ppm de azufre)', 'GSL91': 'gasoline RON 91 (regular)',
         'GSL95': 'gasoline RON 95 (super)', 'JET': 'jet fuel (Jet fuel A-1, and Jet Fuel A which replaced it from late 2024)', 'KER': 'kerosene', 'AVG': 'Av-Gas',
         'FOI': 'Bunker (fuel oil)', 'FOI_ICE2': 'Bunker Termico ICE 2 (low-sulphur fuel oil for ICE power plants)',
         'FOI_ICE': 'Bunker Termico ICE (blend for ICE power plants)', 'LPG': 'LPG mix 70-30 propane-butane'}


def dens_for(k):
    return {'KER': 'JET', 'FOI_ICE': 'FOI_ICE2'}.get(k, k)


def gj_per_l(k):
    d = DENS[dens_for(k)]
    return d * NCV[FUEL_OF[k]] / 1000.0


def conv_text(k, usd_per_l):
    dk = dens_for(k)
    f = FUEL_OF[k]
    return ('%s USD/L / (%s kg/L (%s) x %s GJ/t (IPCC_NCV_%s) / 1000) = %s USD/GJ' %
            (r4(usd_per_l), r4(DENS[dk]), DNAME[dk], NCV[f], f, r3(usd_per_l / gj_per_l(k))))


rows, hist = [], []
MESN = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']


def row(**kw):
    d = {h: '' for h in HEAD}
    d.update(country='CostaRica', year='2024', calorific_basis='not stated')
    d.update(kw)
    return d


# ---------------- 1. import CIF, liquids (ARESEP open data) ----------------
for k in ['DSL', 'GSL91', 'GSL95', 'JET', 'AVG', 'FOI', 'FOI_ICE2', 'LPG']:
    a = agg[(2024, k)]
    L = a['litros']
    fob, fr, ins, cif = a['costoFOB'] / L, a['costoFlete'] / L, a['costoSeguro'] / L, a['costoCIF'] / L
    tr, port = a['costoTrader'] / L, a['costoPortuario'] / L
    f = FUEL_OF[k]
    usd_gj = cif / gj_per_l(k)
    rows.append(row(
        fuel=f, model_code=CODE[f], price_point='import CIF', fob=r4(fob), freight=r4(fr), insurance=r4(ins),
        price_as_published=r4(cif), currency='USD', unit='USD/L', period='2024 (ARESEP reference months with purchases: %s; vessels discharged 18 Dec 2023 to 1 Jan 2025)' % ', '.join(sorted({r['mes'].strip() for r in pur if r['anho'] == 2024 and pkey(r['producto']) == k}, key=MESN.index)),
        months_covered=str(len({r['mes'] for r in pur if r['anho'] == 2024 and pkey(r['producto']) == k})), tax_treatment='pre-tax (CIF invoice cost)',
        conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f), value_usd_per_gj=r3(usd_gj),
        evidence_class='local regulator or operator', source_id=SRC_PURCH,
        page_or_table='ARESEP open data service ObtenerComprasCombustibleRecope, records anho=2024, producto=%s' % LABEL[k],
        downloaded_file='CR/aresep_od_ObtenerComprasCombustibleRecope.json',
        derivation=('sum over %d 2024 RECOPE purchase records: costoFOB %.2f, costoFlete %.2f, costoSeguro %.2f, costoCIF %.2f USD over %.0f litros; '
                    'CIF/L = %.2f / %.0f = %s USD/L; %s' % (a['n'], a['costoFOB'], a['costoFlete'], a['costoSeguro'], a['costoCIF'], L,
                                                           a['costoCIF'], L, r4(cif), conv_text(k, cif))),
        notes=('%s. Volume-weighted over all 2024 cargoes. Outside CIF the same records give trader cost %s USD/L and port cost %s USD/L '
               '(landed cost CIF + trader + port = %s USD/L), which ARESEP adds to form the COA. Density is the 2024 invoice mass over litres from the same records.'
               % (LABEL[k], r4(tr), r4(port), r4(cif + tr + port)))))

# ---------------- 2. wholesale import parity: COA + K (ARESEP resolutions) ----------------
PRODS = [('DSL', 'DSL'), ('GSL91', 'GSL91'), ('GSL95', 'GSL95'), ('JET', 'JET'), ('KER', 'KER'), ('AVG', 'AVG'),
         ('FOI', 'FOI'), ('FOI_ICE2', 'FOI_ICE2'), ('LPG', 'LPG')]
for k, pk in PRODS:
    coa, mo, rs = mean12(pk, 'coa'), mean12(pk, 'mo'), mean12(pk, 'rsbt')
    K = mo + rs
    tot = coa + K
    f = FUEL_OF[k]
    usd_l = tot / FX24
    rows.append(row(
        fuel=f, model_code=CODE[f], price_point='wholesale import parity', importer_terminal_margin=r4(K),
        price_as_published=r4(tot), currency='CRC', unit='CRC/L', period=MONTHS, months_covered='12',
        tax_treatment='excludes impuesto unico and VAT; before subsidy allocations and price differentials',
        exchange_rate=r4(FX24), exchange_rate_constant='CR_FX_2024',
        conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f), value_usd_per_gj=r3(usd_l / gj_per_l(k)),
        evidence_class='local regulator or operator', source_id=SRC_RES,
        page_or_table='each resolution: Cuadro Determinacion del Costo de Adquisicion (COA) por producto, column costo de adquisicion por litro; Cuadro Calculo de componentes de margen de operacion y redito sobre base tarifaria (MO, RSBT)',
        downloaded_file=FILES_RES,
        derivation=('mean of 12 monthly COA %s CRC/L + MO %s + RSBT %s (K = %s CRC/L) = %s CRC/L; %s CRC/L / %s CRC/USD (CR_FX_2024) = %s USD/L; %s'
                    % (r4(coa), r4(mo), r4(rs), r4(K), r4(tot), r4(tot), r4(FX24), r4(usd_l), conv_text(k, usd_l))),
        notes=('%s. COA is RECOPE\'s landed acquisition cost per litre from its purchase invoices (CIF, trader cost and port cost) converted by ARESEP at the BCCR selling rate of the 15 days before each cutoff (monthly rates 503.97 to 532.99 CRC/USD). '
               'FOB, freight and insurance are not split in the resolutions; see the import CIF row. K = MO + RSBT is the RECOPE operating margin and return on rate base.'
               % LABEL[k]) + (' Kerosene has no own purchases; ARESEP sets its COA equal to the Jet fuel A-1 COA (blend rule).' if k == 'KER' else '')))

# ---------------- 3. final consumer pre-tax at RECOPE plantel ----------------
for k, pk in [('DSL', 'DSL'), ('GSL91', 'GSL91'), ('GSL95', 'GSL95'), ('JET', 'JET'), ('KER', 'KER'), ('AVG', 'AVG'), ('FOI', 'FOI'), ('LPG', 'LPG')]:
    f = FUEL_OF[k]
    if k == 'LPG':
        pre = LPG_PRE
        pt = 'each resolution: subsidy table (Precio terminal subsidiado, sin impuestos); Jun and Jul from Por Tanto I.b price with tax per litre minus impuesto unico'
        der = ('mean of 12 monthly subsidised terminal prices without tax %s CRC/L (months: %s)'
               % (r4(pre), ', '.join('%s %s' % (p[5:], r4(v)) for p, v in sorted(lpg_pre.items()))))
        note = ('LPG 70-30 price RECOPE charges bottlers at the terminal after the cross-subsidy (decree 39437-MINAE); bottler, distributor and retailer margins and cylinder prices are set separately and not included.')
    else:
        pre = mean12(pk, 'plantel_sin')
        pt = 'each resolution: Por Tanto I.a Precios en planteles de abasto, column precio sin impuesto'
        der = 'mean of 12 monthly plantel prices without tax = %s CRC/L' % r4(pre)
        note = ('%s plantel (terminal) price without impuesto unico, paid by distributors and by large consumers that lift at RECOPE terminals; '
                'it includes COA, K, the price differential, the extraordinary settlement, the regulatory canon and subsidy allocations; the client pays freight from the terminal.' % LABEL[k])
    usd_l = pre / FX24
    rows.append(row(
        fuel=f, model_code=CODE[f], price_point='final consumer pre-tax', price_as_published=r4(pre), currency='CRC', unit='CRC/L',
        period=MONTHS, months_covered='12', tax_treatment='excludes impuesto unico (Ley 8114) and VAT',
        exchange_rate=r4(FX24), exchange_rate_constant='CR_FX_2024',
        conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f), value_usd_per_gj=r3(usd_l / gj_per_l(k)),
        evidence_class='local regulator or operator', source_id=SRC_RES, page_or_table=pt, downloaded_file=FILES_RES,
        derivation='%s; %s CRC/L / %s CRC/USD (CR_FX_2024) = %s USD/L; %s' % (der, r4(pre), r4(FX24), r4(usd_l), conv_text(k, usd_l)),
        notes='Price point: RECOPE plantel (terminal). ' + note))

# ---------------- 4. final consumer pre-tax at service stations (road and airport) ----------------
for k in ['DSL', 'GSL91', 'GSL95', 'KER', 'JET', 'AVG']:
    f = FUEL_OF[k]
    st, tax, pl = mean12(k, 'station_sin_iva'), mean12(k, 'tax'), mean12(k, 'plantel_sin')
    pre = st - tax
    usd_l = pre / FX24
    if k in ('JET', 'AVG'):
        comp = dict(retail_margin='17.265')
        cn = 'airport service station: total marketing margin including transport 17.265 CRC/L (RE-0124-IE-2020), no VAT on transport'
    else:
        comp = dict(retail_margin='56.681', inland_freight='12.773')
        cn = 'road service station: marketing margin 56.681 CRC/L (RE-0038-IE-2021) and average freight 12.773 CRC/L (RE-0124-IE-2020); 13 percent VAT on freight (1.66 CRC/L) excluded'
    rows.append(row(
        fuel=f, model_code=CODE[f], price_point='final consumer pre-tax', price_as_published=r4(pre), currency='CRC', unit='CRC/L',
        period=MONTHS, months_covered='12', tax_treatment='excludes impuesto unico and VAT on transport',
        exchange_rate=r4(FX24), exchange_rate_constant='CR_FX_2024',
        conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f), value_usd_per_gj=r3(usd_l / gj_per_l(k)),
        evidence_class='local regulator or operator', source_id=SRC_RES,
        page_or_table='each resolution: Por Tanto I.d Precios al consumidor final en estacion de servicio con punto fijo (column precio sin IVA/transporte) and Cuadro Impuesto unico a los combustibles; June Av-Gas and Jet A-1 from the rectification RE-0044-IE-2024',
        downloaded_file=FILES_RES, **comp,
        derivation=('mean of 12 monthly station prices without VAT on transport %s CRC/L minus mean impuesto unico %s CRC/L = %s CRC/L; check: plantel price without tax %s + margins = station price without tax and VAT each month; %s CRC/L / %s CRC/USD (CR_FX_2024) = %s USD/L; %s'
                    % (r4(st), r4(tax), r4(pre), r4(pl), r4(pre), r4(FX24), r4(usd_l), conv_text(k, usd_l))),
        notes='%s; %s.' % (LABEL[k], cn)))

# ---------------- 5. generator delivered (ICE thermal plants) ----------------
FLETE = {'FOI_ICE2': 7.045, 'DSL': 6.20}
for k in ['FOI_ICE2', 'DSL']:
    f = FUEL_OF[k]
    pl = mean12(k, 'plantel_sin')
    tot = pl + FLETE[k]
    usd_l = tot / FX24
    rows.append(row(
        fuel=f, model_code=CODE[f], price_point='generator delivered', inland_freight=r4(FLETE[k]), price_as_published=r4(tot),
        currency='CRC', unit='CRC/L', period=MONTHS, months_covered='12', tax_treatment='excludes impuesto unico and VAT',
        exchange_rate=r4(FX24), exchange_rate_constant='CR_FX_2024',
        conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f), value_usd_per_gj=r3(usd_l / gj_per_l(k)),
        evidence_class='built from published components', source_id='%s;%s;%s' % (SRC_RES, SRC_CVG24, SRC_CVG25),
        page_or_table='plantel price: each resolution Por Tanto I.a (precio sin impuesto); freight to ICE: RE-0164-IE-2023 Cuadro 3 (PDF p.9) and RE-0097-IE-2024 Cuadro 3 (PDF p.9)',
        downloaded_file=FILES_RES + ';CR/aresep_RE-0164-IE-2023_CVG2024.pdf;CR/aresep_RE-0097-IE-2024_CVG2025.pdf',
        derivation=('mean of 12 monthly %s plantel prices without tax %s CRC/L (%s; RES ids %s) + freight to the ICE plant %s CRC/L (%s, Cuadro 3) = %s CRC/L; %s CRC/L / %s CRC/USD (CR_FX_2024) = %s USD/L; %s'
                    % (LABEL[k], r4(pl), 'ARESEP monthly resolutions', SRC_RES.replace(';', ' '), r4(FLETE[k]), SRC_CVG24, r4(tot), r4(tot), r4(FX24), r4(usd_l), conv_text(k, usd_l))),
        notes=('ARESEP values ICE thermal fuel in the CVG as the RECOPE plantel price with tax plus the freight ICE pays (basic-zone freight from Barranca terminal to Garabito, RE-0097-IE-2023 for bunker, RE-0124-IE-2020 for diesel). '
               'This row removes the impuesto unico (2024 mean %s CRC/L) to give the pre-tax delivered price. '
               % r4(mean12(k, 'tax'))) + ('ICE buys the same diesel 50 ppm as road transport; there is no separate ICE diesel tariff.' if k == 'DSL' else
                                          'Bunker Termico ICE 2 is the fuel oil RECOPE imports for ICE plants (193 million litres in 2024); the separate blend Bunker Termico ICE had no 2024 purchases.')))
# published CVG 2024 values (with tax, prices in force December 2023)
for k, pl, tot in [('FOI_ICE2', 322.70, 329.74), ('DSL', 619.58, 625.78)]:
    f = FUEL_OF[k]
    usd_l = tot / FX24
    rows.append(row(
        fuel=f, model_code=CODE[f], price_point='generator delivered', inland_freight=r4(FLETE[k]), price_as_published=r4(tot),
        currency='CRC', unit='CRC/L', period='prices in force December 2023 (RE-0154-IE-2023), used by ARESEP to value 2024 thermal generation', months_covered='1',
        tax_treatment='includes impuesto unico', exchange_rate=r4(FX24), exchange_rate_constant='CR_FX_2024',
        conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f), value_usd_per_gj=r3(usd_l / gj_per_l(k)),
        evidence_class='local regulator or operator', source_id=SRC_CVG24,
        page_or_table='RE-0164-IE-2023 Cuadro 3 Precios de combustibles para generacion termica, colones por litro, ano 2024 (PDF p.9)',
        downloaded_file='CR/aresep_RE-0164-IE-2023_CVG2024.pdf',
        derivation='published: plantel price with tax %s + freight %s = %s CRC/L; %s CRC/L / %s CRC/USD (CR_FX_2024) = %s USD/L; %s'
                   % (r4(pl), r4(FLETE[k]), r4(tot), r4(tot), r4(FX24), r4(usd_l), conv_text(k, usd_l)),
        notes='%s. Tax-inclusive regulator value for the 2024 CVG (costo variable de generacion) tariff; a one-month price, kept for reference next to the 12-month pre-tax build.' % LABEL[k]))

# ---------------- 6. petroleum coke and coal: PROCOMER (VUCE open data) and Comtrade ----------------
tt = json.load(open(P('vuce_pt_tiempo.json'), encoding='utf-8'))['d']
tt = tt['results'] if isinstance(tt, dict) else tt
YR = {r['id_tiempo']: int(r['anno'].strip('*')) for r in tt}
MO = {r['id_tiempo']: int(r['num_mes']) for r in tt}


def vuce(fname, hs6):
    d = json.load(open(P(fname), encoding='utf-8'))['d']
    d = d['results'] if isinstance(d, dict) else d
    out = collections.defaultdict(lambda: [0.0, 0.0, set()])
    for r in d:
        if r['partida'].startswith(hs6):
            y = YR[r['id_tiempo']]
            out[y][0] += float(r['valor_tot'])
            out[y][1] += float(r['peso_tot'])
            out[y][2].add(MO[r['id_tiempo']])
    return out


MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ct = {r['cmdCode']: r for r in json.load(open(P('comtrade_CR_2024_M_6digit.json'), encoding='utf-8'))['data']}
SOLID = [('COK', '271311', 'vuce_od_import_2713.json', SRC_VUCE_2713, 32.5, 'IPCC_NCV_COK', 'petroleum coke, not calcined (HS 271311)'),
         ('COA', '270111', 'vuce_od_import_2701.json', SRC_VUCE_2701, 26.7, 'CR_IPCC_NCV_COA_ANTHRACITE', 'anthracite (HS 270111)')]
for f, hs, fn, sid, ncv, ncvname, lab in SOLID:
    v = vuce(fn, hs)
    for y in sorted(v):
        if y < 2018 or y > 2025:
            continue
        val, kg, ms = v[y]
        upt = val / kg * 1000
        mlist = ', '.join(MN[m - 1] for m in sorted(ms))
        d = row(fuel=f, model_code=CODE[f], price_point='import CIF', year=str(y), price_as_published='%.2f' % upt, currency='USD', unit='USD/t',
                period='%d, months with imports: %s' % (y, mlist), months_covered=str(len(ms)),
                tax_treatment='customs value, before import duties (DAI 0 percent on HS 271311) and VAT',
                conversion_constants=ncvname, value_usd_per_gj=r3(upt / ncv),
                evidence_class='local customs or statistics', source_id='%s;%s' % (sid, SRC_VUCE_T),
                page_or_table='PROCOMER open data (VUCE OData) od_import, partida %s*, all records with id_tiempo in %d (months from pt_tiempo)' % (hs, y),
                downloaded_file='CR/%s;CR/vuce_pt_tiempo.json' % fn,
                derivation='sum valor_tot %.2f USD / sum peso_tot %.0f kg x 1000 = %.2f USD/t; %.2f USD/t / %s GJ/t (%s) = %s USD/GJ' % (val, kg, upt, upt, ncv, ncvname, r3(upt / ncv)),
                notes=('%s, %.0f t. PROCOMER publishes the value in US dollars without naming the valuation basis in the OData service; UN Comtrade carries the same 2024 figure as the CIF value (cifvalue). ' % (lab, kg / 1000)) +
                ('Imported by the cement plants (Holcim, CEMEX), the only petcoke users.' if f == 'COK' else
                 'Small specialty anthracite lots, not steam coal: no cement or power plant burned coal in 2024; unit values swing from 378 to 2993 USD/t across 2018 to 2025.'))
        if y == 2024:
            rows.append(d)
        hist.append(d)
    c = ct[hs]
    upt = c['cifvalue'] / c['netWgt'] * 1000
    rows.append(row(fuel=f, model_code=CODE[f], price_point='import CIF', price_as_published='%.2f' % upt, currency='USD', unit='USD/t', period='2024 (annual)', months_covered='12',
                    tax_treatment='CIF, before duties and VAT', conversion_constants=ncvname, value_usd_per_gj=r3(upt / ncv),
                    evidence_class='international customs (Comtrade)', source_id=SRC_CT6,
                    page_or_table='UN Comtrade preview API, reporter 188, 2024, flow M, partner World, cmdCode %s' % hs,
                    downloaded_file='CR/comtrade_CR_2024_M_6digit.json',
                    derivation='cifvalue %.2f USD / netWgt %.3f kg x 1000 = %.2f USD/t (qtyUnitCode 8 kg, isQtyEstimated %s, isNetWgtEstimated %s); / %s GJ/t (%s) = %s USD/GJ'
                               % (c['cifvalue'], c['netWgt'], upt, c['isQtyEstimated'], c['isNetWgtEstimated'], ncv, ncvname, r3(upt / ncv)),
                    notes='Same underlying national customs record as the PROCOMER row; kept as the second source.'))

# ---------------- 7. natural gas ----------------
rows.append(row(fuel='NGS', model_code='IMPNGS', price_point='import CIF', price_as_published='7.763', currency='USD', unit='USD/GJ', period='2024', months_covered='0',
                tax_treatment='pre-tax', calorific_basis='gross', value_usd_per_gj='7.763', evidence_class='ASSUMPTION candidate',
                source_id='%s;%s;%s' % (SRC_VUCE_LNG, SRC_VUCE_NG, SRC_CT6),
                page_or_table='PROCOMER od_import partida 271111* and 271121*; UN Comtrade 2024 cmdCode 271111 (no record) and 271121',
                downloaded_file='CR/vuce_od_import_271111.json;CR/vuce_od_import_271121.json;CR/comtrade_CR_2024_M_6digit.json',
                derivation='no 2024 natural gas import price exists: PROCOMER shows no LNG (271111) imports in 2024 and 3 kg of gaseous natural gas (271121) worth 22.25 USD; Comtrade 2024 has no 271111 record and 271121 3.0 kg, 22.25 USD',
                notes=('Costa Rica imported no natural gas in 2024 and has no LNG terminal or gas network; a delivered small-scale LNG cost of 7.76 USD/GJ (gross) for 2024, '
                       'equal to the 2024 Henry Hub average of 2.08 USD/GJ plus 4.26 USD/GJ for US LNG liquefaction and export and 1.42 USD/GJ for small-scale shipping and regasification, '
                       'is a plausible cost for a first import project; no Costa Rican public document gives an LNG import price to check it against; range 6 to 12 USD/GJ.')))

# ---------------- 8. history: liquids import CIF from ARESEP open data, 2022 to 2025 ----------------
for y in [2022, 2023, 2024, 2025]:
    for k in ['DSL', 'GSL91', 'GSL95', 'JET', 'AVG', 'FOI', 'FOI_ICE2', 'LPG']:
        a = agg[(y, k)]
        if not a['litros']:
            continue
        L = a['litros']
        fob, fr, ins, cif = a['costoFOB'] / L, a['costoFlete'] / L, a['costoSeguro'] / L, a['costoCIF'] / L
        f = FUEL_OF[k]
        hist.append(row(fuel=f, model_code=CODE[f], price_point='import CIF', year=str(y), fob=r4(fob), freight=r4(fr), insurance=r4(ins),
                        price_as_published=r4(cif), currency='USD', unit='USD/L', period='%d (ARESEP reference months)' % y,
                        months_covered=str(len({r['mes'] for r in pur if r['anho'] == y and pkey(r['producto']) == k})),
                        tax_treatment='pre-tax (CIF invoice cost)', conversion_constants='%s;IPCC_NCV_%s' % (DNAME[dens_for(k)], f),
                        value_usd_per_gj=r3(cif / gj_per_l(k)), evidence_class='local regulator or operator', source_id=SRC_PURCH,
                        page_or_table='ARESEP open data service ObtenerComprasCombustibleRecope, records anho=%d, producto=%s' % (y, LABEL[k]),
                        downloaded_file='CR/aresep_od_ObtenerComprasCombustibleRecope.json',
                        derivation='sum costoCIF %.2f USD / sum litros %.0f = %s USD/L over %d records; %s' % (a['costoCIF'], L, r4(cif), a['n'], conv_text(k, cif)),
                        notes='%s. Converted with the 2024 density from the same service for every year (mass field is incomplete in some 2022 and 2023 records). The service starts in December 2021.' % LABEL[k]))

# ---------------- write ----------------
def write(name, rs):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEAD)
        w.writeheader()
        for r_ in rs:
            w.writerow(r_)
    print(name, len(rs))


write('prices_CR.csv', rows)
write('history_CR.csv', sorted(hist, key=lambda r_: (r_['fuel'], r_['notes'][:20], r_['year'])))

with open(os.path.join(OUT, 'constants_CR.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['name', 'value', 'unit', 'source_id', 'page_or_table', 'derivation'])
    w.writerow(['CR_FX_2024', r4(FX24), 'CRC/USD', SRC_WDI, 'World Bank WDI indicator PA.NUS.FCRF (Official exchange rate, LCU per US$, period average), Costa Rica, 2024',
                'published annual average %s; it equals the mean of the BCCR daily reference buying and selling rates over 2024 to within 0.01 CRC; the BCCR daily file itself could not be downloaded (see manual list)' % FX24])
    for y in sorted(FX):
        if y != 2024:
            w.writerow(['CR_FX_%d' % y, r4(FX[y]), 'CRC/USD', SRC_WDI, 'World Bank WDI indicator PA.NUS.FCRF, Costa Rica, %d' % y, 'published annual average'])
    for k, dv in DENS.items():
        a = agg[(2024, k)]
        w.writerow([DNAME[k], r4(dv), 'kg/L', SRC_PURCH, 'ARESEP open data ObtenerComprasCombustibleRecope, anho=2024, producto=%s' % LABEL[k],
                    'sum masa %.0f kg / sum litros %.0f L over %d 2024 cargoes' % (a['masa'], a['litros'], a['n'])])
    w.writerow(['CR_IPCC_NCV_COA_ANTHRACITE', '26.7', 'GJ/t', SRC_IPCC, '2006 IPCC Guidelines Vol. 2 Ch. 1 Table 1.2 (PDF p.18), Anthracite, net calorific value default', 'published default (lower 21.6, upper 32.2)'])
print('FX24', FX24, 'DENS', {k: round(v, 4) for k, v in DENS.items()}, 'LPG_PRE', round(LPG_PRE, 2))
