"""D6: Guatemala DIST_FLEXFUEL VariableCost (Primary Techs row 284).
r(y) = Brazilian hydrated-ethanol price per GJ / Brazilian pre-tax gasoline A price per GJ (2019-2024 from downloaded files);
2018 has no downloaded pre-tax gasoline series -> nearest year with both (2019), logged.
value(y) = r(y) x DIST_GSL VariableCost(y) for 2018-2024; from 2025 mean(r 2018-2024) x DIST_GSL(y).
Every monthly gasoline value is checked as printed on its cited bulletin page (pdftotext). Reads the base snapshot."""
import os, sys, re, subprocess, collections, datetime
import openpyxl, xlrd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EARLIER, JOB
from common_props import BASEDIR, write_part

DL = EARLIER + '/downloads/r1/'
B = {  # source id -> file
    'R1F-19': 'BR_ANP_bt_2021_boletim-trimestral-1.pdf', 'R1F-20': 'BR_ANP_bt_2021_boletim-trimestral-2.pdf',
    'R1F-21': 'BR_ANP_bt_2021_boletim-trimestral-3.pdf', 'R1F-22': 'BR_ANP_bt_2021_boletim-trimestral-4.pdf',
    'R1F-23': 'BR_ANP_bt_2020_boletim-trimestral-sdc-5-1t20-novo.pdf', 'R1F-24': 'BR_ANP_bt_2020_boletim-trimestral-sdc-6-2t20-novo.pdf',
    'R1F-25': 'BR_ANP_bt_2020_boletim-trimestral-sdc-7-3t20.pdf', 'R1F-26': 'BR_ANP_bt_2020_boletim-trimestral-sdc-8-4t20-novo.pdf',
    'R1F-27': 'BR_ANP_bt_2021_boletim-trimestral-sdc-9-1t21-novo.pdf', 'R1F-28': 'BR_ANP_bt_2021_boletim-trimestral-sdc-10-2t21.pdf',
    'R1F-29': 'BR_ANP_bt_2021_boletim-trimestral-sdc-11-3t21_vf.pdf', 'R1F-30': 'BR_ANP_bt_2021_boletim-trimestral-sdc-12-4t21_vf.pdf',
    'R1F-31': 'BR_ANP_bt_2022_boletim-trimestral-sdc-13-1t22.pdf', 'R1F-32': 'BR_ANP_bt_2022_boletim-trimestral-sdc-14-2t22.pdf',
    'R1F-33': 'BR_ANP_bt_2022_boletim-trimestral-sdc-15-3t22.pdf', 'R1F-34': 'BR_ANP_bt_2022_boletim-trimestral-sdc-16-4t22.pdf',
    'R1F-35': 'BR_ANP_bt_2023_boletim-trim-precos-17-1t23.pdf', 'R1F-36': 'BR_ANP_boletim_trim_precos_18_2t23.pdf',
    'R1F-37': 'BR_ANP_bt_2023_boletim-trim-precos-19-3t23.pdf', 'R1F-38': 'BR_ANP_bt_2023_boletim-trim-precos-20-4t23.pdf',
    'R1F-39': 'BR_ANP_boletim-trim-precos-21-1t24.pdf', 'R1F-40': 'BR_ANP_boletim-trim-precos-22-2t24.pdf',
    'R1F-41': 'BR_ANP_boletim-trim-precos-23-3t24.pdf', 'R1F-42': 'BR_ANP_boletim-trim-precos-24-4t24.pdf',
}
# (year, value R$/L, source, PDF page) for the monthly gasoline A realization price sem tributos; None page = search all pages
G = [
    (2019, 1.50, 'R1F-19', 14), (2019, 1.59, 'R1F-19', 14), (2019, 1.80, 'R1F-19', 14),
    (2019, 1.96, 'R1F-20', 11), (2019, 2.01, 'R1F-20', 11), (2019, 1.793, 'R1F-21', 18),
    (2019, 1.709, 'R1F-21', 18), (2019, 1.680, 'R1F-21', 18), (2019, 1.752, 'R1F-21', 18),
    (2019, 1.806, 'R1F-22', 20), (2019, 1.840, 'R1F-22', 20), (2019, 1.933, 'R1F-22', 20),
    (2020, 1.890, 'R1F-23', 21), (2020, 1.757, 'R1F-23', 21), (2020, 1.431, 'R1F-23', 21),
    (2020, 1.013, 'R1F-24', 14), (2020, 1.144, 'R1F-24', 14), (2020, 1.480, 'R1F-24', 14),
    (2020, 1.704, 'R1F-25', 17), (2020, 1.779, 'R1F-25', 17), (2020, 1.664, 'R1F-26', 22),
    (2020, 1.754, 'R1F-26', 22), (2020, 1.674, 'R1F-26', 22), (2020, 1.765, 'R1F-26', 22),
    (2021, 1.933, 'R1F-27', 21), (2021, 2.288, 'R1F-27', 21), (2021, 2.805, 'R1F-28', 24),
    (2021, 2.800, 'R1F-28', 24), (2021, 2.621, 'R1F-28', 24), (2021, 2.600, 'R1F-28', 24),
    (2021, 2.768, 'R1F-29', 15), (2021, 2.844, 'R1F-29', 15), (2021, 2.865, 'R1F-29', 15),
    (2021, 3.052, 'R1F-30', 17), (2021, 3.238, 'R1F-30', 17), (2021, 3.197, 'R1F-30', 17),
    (2022, 3.291, 'R1F-31', 15), (2022, 3.337, 'R1F-31', 15), (2022, 3.808, 'R1F-31', 15),
    (2022, 3.888, 'R1F-32', 17), (2022, 3.946, 'R1F-32', 17), (2022, 3.773, 'R1F-32', 17),
    (2022, 4.078, 'R1F-33', 6), (2022, 3.638, 'R1F-33', 6), (2022, 3.349, 'R1F-33', 6),
    (2022, 3.384, 'R1F-34', 6), (2022, 3.358, 'R1F-34', 6), (2022, 3.196, 'R1F-35', 6),
    (2023, 3.209, 'R1F-35', 6), (2023, 3.434, 'R1F-35', 6), (2023, 3.179, 'R1F-35', 6),
    (2023, 3.174, 'R1F-36', 7), (2023, 2.992, 'R1F-36', 7), (2023, 2.867, 'R1F-37', 6),
    (2023, 2.624, 'R1F-37', 6), (2023, 2.986, 'R1F-37', 6), (2023, 3.083, 'R1F-37', 6),
    (2023, 2.957, 'R1F-38', 6), (2023, 2.871, 'R1F-38', 6), (2023, 2.805, 'R1F-38', 6),
    (2024, 2.833, 'R1F-39', 6), (2024, 2.887, 'R1F-39', 6), (2024, 2.827, 'R1F-39', 6),
    (2024, 2.914, 'R1F-40', 11), (2024, 2.850, 'R1F-40', 11), (2024, 2.824, 'R1F-40', 11),
    (2024, 2.972, 'R1F-41', 13), (2024, 3.006, 'R1F-41', 13), (2024, 2.991, 'R1F-41', 13),
]
Q4_2024 = (3.88, 0.89, 'R1F-42', 15)   # Producao Gasolina A 3.88 less federal taxes 0.89 R$/L, months Oct-Dec 2024


def page_text(sid, p):
    out = subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), DL + B[sid], '-'], capture_output=True)
    return out.stdout.decode('utf-8', 'replace')


def fmt_variants(v):
    s3 = f'{v:.3f}'.replace('.', ',')
    s2 = f'{v:.2f}'.replace('.', ',')
    return {s3, s2, s3.rstrip('0')}


log = []
miss = 0
cache = {}
for y, v, sid, p in G:
    t = cache.setdefault((sid, p), page_text(sid, p))
    ok = any(re.search(r'(?<![\d,])' + re.escape(s) + r'(?!\d)', t) for s in fmt_variants(v))
    if not ok:
        miss += 1
    log.append(f'{y} {v} {sid} p.{p} {"found" if ok else "NOT FOUND"}')
t = page_text(*Q4_2024[2:])
q4ok = ('3,88' in t) and ('0,89' in t)
log.append(f'Q4 2024 3.88 and 0.89 on R1F-42 p.15: text layer {q4ok}; values are chart labels, checked on the rendered page image (Producao Gasolina A R$ 3,88 and PIS/COFINS R$ 0,89, 4o Trim 2024)')
# heating values R1F-18 p.1
hv = subprocess.run(['pdftotext', '-raw', '-f', '1', '-l', '1', DL + 'BR_ANP_anuario2026_fatores-de-conversao-2026.pdf', '-'],
                    capture_output=True).stdout.decode('utf-8', 'replace')
hvl = [ln for ln in hv.splitlines() if re.search(r'(?i)etanol hidratado|gasolina a\b', ln)]
log.append('R1F-18 p.1 lines: ' + ' || '.join(' '.join(l.split()) for l in hvl))
DENS_E, PCI_E, DENS_G, PCI_G = 0.809, 6300.0, 0.742, 10400.0
MJL_E = DENS_E * PCI_E * 4.1868 / 1000.0       # t/m3 = kg/L; kcal/kg x 4.1868 kJ/kcal -> MJ/L
MJL_G = DENS_G * PCI_G * 4.1868 / 1000.0
# CEPEA weekly ethanol R$/L, annual means by year of week date
bk = xlrd.open_workbook(DL + 'BR_CEPEA_etanol_hidratado_semanal_SP_id103.xls', ignore_workbook_corruption=True)
sh = bk.sheet_by_index(0)
eth = collections.defaultdict(list)
for i in range(sh.nrows):
    a, b = sh.cell_value(i, 0), sh.cell_value(i, 1)
    d = None
    if isinstance(a, str) and re.match(r'\d\d/\d\d/\d{4}', a.strip()):
        d = datetime.datetime.strptime(a.strip(), '%d/%m/%Y')
    elif isinstance(a, float) and a > 30000:
        d = xlrd.xldate_as_datetime(a, bk.datemode)
    if d is None:
        continue
    try:
        bv = float(str(b).replace(',', '.'))
    except ValueError:
        continue
    eth[d.year].append(bv)
gas = collections.defaultdict(list)
for y, v, sid, p in G:
    gas[y].append(v)
gas[2024] += [Q4_2024[0] - Q4_2024[1]] * 3
r = {}
for y in range(2019, 2025):
    assert len(gas[y]) == 12, (y, len(gas[y]))
    e = sum(eth[y]) / len(eth[y])
    g = sum(gas[y]) / 12
    r[y] = (e / MJL_E) / (g / MJL_G)
    log.append(f'{y}: ethanol {e:.4f} R$/L ({len(eth[y])} weeks), gasoline A {g:.4f} R$/L (12 months), r = {r[y]:.4f}')
r[2018] = r[2019]
log.append(f'2018: no downloaded pre-tax gasoline A series; nearest year with both is 2019, r(2018) = r(2019) = {r[2018]:.4f}')
rbar = sum(r[y] for y in range(2018, 2025)) / 7
log.append(f'mean r 2018-2024 = {rbar:.6f}; range {min(r.values()):.4f} to {max(r.values()):.4f}; misses {miss}')
open(JOB + '/logs/d6_values.log', 'w').write('\n'.join(log) + '\n')
print('\n'.join(log[-12:]))

AO = 'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx'
wf = openpyxl.load_workbook(f'{BASEDIR}/{AO}')
ws = wf['Primary Techs']
hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
assert ws.cell(284, 2).value == 'DIST_FLEXFUEL' and ws.cell(284, 5).value == 'VariableCost'
assert ws.cell(14, 2).value == 'DIST_GSL' and ws.cell(14, 5).value == 'VariableCost'
SRC = 'R1F-14;R1F-15;R1F-18;' + ';'.join(f'R1F-{i}' for i in range(19, 43))
A = (f'ASSUMPTION: the flex-fuel blend is valued at the Brazilian ratio of hydrated-ethanol to pre-tax gasoline A prices per GJ '
     f'(ratio {min(r.values()):.2f} to {max(r.values()):.2f} over 2019-2024; 2018 takes the 2019 ratio, the nearest year with both '
     f'pre-tax prices) times the Guatemala gasoline price, because no Central American flex-fuel price series is published; from '
     f'2025 the 2018-2024 mean ratio {rbar:.3f} applies.')
rows = []
for y in range(2018, 2051):
    j = hdr[y]
    gsl = ws.cell(14, j).value
    assert isinstance(gsl, (int, float)), (y, gsl)
    if y <= 2024:
        new = r[y] * gsl
        der = f'r({y}) = {r[y]:.6f} x DIST_GSL VariableCost {gsl} = {new:.6f} USD/GJ'
    else:
        new = rbar * gsl
        der = f'mean r 2018-2024 = {rbar:.6f} x DIST_GSL VariableCost {gsl} = {new:.6f} USD/GJ'
    rows.append(dict(country='Guatemala', workbook=AO, sheet='Primary Techs', row=284, column=openpyxl.utils.get_column_letter(j),
                     year=y, Tech='DIST_FLEXFUEL', Parameter='VariableCost', scenario='ALL', current_value=ws.cell(284, j).value,
                     new_value=repr(new), kind='ao_cell', decision='D6', source_ids=SRC, derivation=der, assumption=A))
write_part('d6', rows)
print('2024', rows[6]['current_value'], '->', rows[6]['new_value'], '| 2030', rows[12]['current_value'], '->', rows[12]['new_value'])
