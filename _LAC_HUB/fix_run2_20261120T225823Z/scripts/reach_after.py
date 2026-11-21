"""D2b estimate after D13, D7a and D2f, from logs/reach_BAU_before.csv (base B1 BAU): CAU 31.536 for the D13 plants and
Ecuador PPHD, band rows x 0.999 / 0.98, DR PPDHYD capacity factor / 0.0036. Prints the history tech-years still above
reachable output from residual capacity alone. Writes logs/reach_BAU_after_estimate.csv."""
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
d = pd.read_csv(JOB + '/logs/reach_BAU_before.csv')
d13 = pd.read_csv(JOB + '/proposals_parts/d13.csv')
plants = set(zip(d13.country, d13.Tech)) | {('Ecuador', 'PPHD')}
m = d.apply(lambda r: (r.country, r.tech) in plants, axis=1)
d.loc[m, 'cau'] = 31.536
band = pd.read_csv(JOB + '/proposals_parts/d7a.csv')
bset = set(zip(band.country, band.Tech, band.year))
b = d.apply(lambda r: (r.country, r.tech, r.year) in bset, axis=1)
d.loc[b, 'lower_pj'] = d.loc[b, 'lower_pj'] * 0.999 / 0.98
h = (d.country == 'DominicanRepublic') & (d.tech == 'PPDHYD')
d.loc[h, 'cf'] = d.loc[h, 'cf'] / 0.0036
d['reachable_pj'] = d.residual_gw * d.cf * d.af * d.cau
d['excess_pj'] = d.lower_pj - d.reachable_pj
d['need_gw'] = d.excess_pj / (d.cf * d.af * d.cau)
d.to_csv(JOB + '/logs/reach_BAU_after_estimate.csv', index=False, lineterminator='\n')
v = d[d.excess_pj > 1e-6]
g = v.groupby(['country', 'tech']).agg(years=('year', lambda s: ' '.join(map(str, s))), max_excess_pj=('excess_pj', 'max'),
                                      max_need_gw=('need_gw', 'max'), residual=('residual_gw', 'first'), cf=('cf', 'first'))
pd.set_option('display.width', 220)
print(g.round(4).to_string())
print('tech-years above reachable:', len(v), 'before:', int((pd.read_csv(JOB + '/logs/reach_BAU_before.csv').excess_pj > 1e-6).sum()))
