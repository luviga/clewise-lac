"""DS1 (D8): Guatemala hydro overwrite shares for 2025 and 2026 per scenario, from the new Stage 0 denominators.
share(s, y) = sourced hydro PJ / Stage 0 Empirical_Gen_PJ(s, y); hydro PJ = AMM 2025 hydro block 5,473.519306 GWh x 0.0036 =
19.704670 PJ (2025, held in 2026); split PPHDAM : PPHROR by the 2024 overwrite shares 40.31 : 2.84.
Edits the 12 existing lines (Country, Scenario, Tech, Year) of _STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.csv in place
(line ending kept), logs to logs/ds1_gua_hydro.csv. Idempotent."""
import csv, io
import openpyxl
import pandas as pd

ROOT = 'C:/clw_fix/'
JOB = ROOT + '_LAC_HUB/fix_run2_20261120T225823Z'
F = ROOT + '_STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.csv'
P = pd.read_csv(JOB + '/proposals_parts/d8.csv')
PJ = float(P.new_value.iloc[0])
W = {'PPHDAM': 40.31 / 43.15, 'PPHROR': 2.84 / 43.15}
wb = openpyxl.load_workbook(ROOT + '_STAGE0_OUTPUT/STAGE0_DENOMINATORS.xlsx', read_only=True, data_only=True)
den = {}
for sh in ('BAU_S0', 'NDCNEW_S0', 'LTSNEW_S0'):
    for r in wb[sh].iter_rows(min_row=2, values_only=True):
        if r[0] == 'Guatemala' and r[2] in (2025, 2026):
            den[(sh[:-3], r[2])] = float(r[3])
raw = open(F, 'rb').read().decode('utf-8')
eol = '\r\n' if '\r\n' in raw else '\n'
lines = raw.split(eol)
hdr = next(csv.reader([lines[0]]))
log, n = [], 0
for i, line in enumerate(lines[1:], start=1):
    if not line:
        continue
    f = next(csv.reader([line]))
    rec = dict(zip(hdr, f))
    if rec['Country'] != 'Guatemala' or rec['Tech'] not in W or rec['Year'] not in ('2025', '2026'):
        continue
    s, y, t = rec['Scenario'], int(rec['Year']), rec['Tech']
    d = den[(s, y)]
    share = PJ * W[t] / d * 100.0
    rec['New_Share_Pct'] = f'{share:.6f}'
    rec['Note'] = (f'AMM hydro {PJ:.6f} PJ (2025 observed{", held in 2026" if y == 2026 else ""}) x {W[t]:.6f} ({t} part 40.31:2.84) '
                   f'/ Stage 0 denominator {d:.4f} PJ ({s} {y})')
    rec['Rationale'] = ('Decision D8: one sourced hydro path in every scenario; share = sourced hydro PJ / this scenario Stage 0 '
                        'denominator')
    rec['Reference'] = 'AMM Generacion Mensual por Planta 2025 (GM20250101.xlsx), sheet Energia, row 8 PLANTAS HIDROELECTRICAS'
    buf = io.StringIO()
    csv.writer(buf, lineterminator='').writerow([rec[h] for h in hdr])
    if lines[i] != buf.getvalue():
        log.append(dict(line=i + 1, scenario=s, tech=t, year=y, denominator_pj=d, old=line, new=buf.getvalue(), share_pct=share))
        lines[i] = buf.getvalue()
        n += 1
# Keep each (scenario, year) at 100 percent: every Guatemala technology has a plateau line in 2025 and 2026, so the share the
# sourced hydro frees (or takes) is spread over the non-hydro plateau lines in proportion to their written shares
# (their mutual proportions unchanged). Base non-hydro shares are read from the base snapshot so reruns stay idempotent.
base = pd.read_csv('C:/clw_base_4ba69d6/_STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.csv')
hyd = {}
for i, line in enumerate(lines[1:], start=1):
    if not line:
        continue
    rec = dict(zip(hdr, next(csv.reader([line]))))
    if rec['Country'] == 'Guatemala' and rec['Tech'] in W and rec['Year'] in ('2025', '2026'):
        hyd[(rec['Scenario'], int(rec['Year']))] = hyd.get((rec['Scenario'], int(rec['Year'])), 0.0) + float(rec['New_Share_Pct'])
for i, line in enumerate(lines[1:], start=1):
    if not line:
        continue
    rec = dict(zip(hdr, next(csv.reader([line]))))
    if rec['Country'] != 'Guatemala' or rec['Tech'] in W or rec['Year'] not in ('2025', '2026'):
        continue
    s, y = rec['Scenario'], int(rec['Year'])
    b = base[(base.Country == 'Guatemala') & (base.Scenario == s) & (base.Year == y)]
    bnon = b[~b.Tech.isin(list(W))]
    k = (100.0 - hyd[(s, y)]) / bnon.New_Share_Pct.sum()
    b0 = float(bnon[bnon.Tech == rec['Tech']].New_Share_Pct.iloc[0])
    rec['New_Share_Pct'] = f'{b0 * k:.6f}'
    rec['Note'] = (f'Plateau 2024 anchor {b0:g} percent x {k:.6f} (non-hydro plateau shares scaled so that the year sums to 100 '
                   f'percent with the sourced hydro share, decision D8)')
    buf = io.StringIO()
    csv.writer(buf, lineterminator='').writerow([rec[h] for h in hdr])
    if lines[i] != buf.getvalue():
        log.append(dict(line=i + 1, scenario=s, tech=rec['Tech'], year=y, denominator_pj='', old=line, new=buf.getvalue(),
                        share_pct=b0 * k))
        lines[i] = buf.getvalue()
        n += 1
open(F, 'wb').write(eol.join(lines).encode('utf-8'))
pd.DataFrame(log).to_csv(JOB + '/logs/ds1_gua_hydro.csv', index=False, lineterminator='\n')
print('lines changed', n, {k: round(v, 4) for k, v in den.items()})
