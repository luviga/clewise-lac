"""Draft D2b and D2c tables from the Phase A logs (read-only). Writes history_plan_draft.csv and history_builds_draft.csv."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB

r = pd.read_csv(f'{JOB}/logs/reach_BAU_before.csv')
r = r[r.excess_pj > 1e-6].copy()
PATH_DR = {'PPPVT', 'PPPVD', 'PPWNDON', 'PPICEGASFOI', 'PPHDAM'}
CF_DR = {'PPDDSL', 'PPDBGS', 'PPDGSL', 'PPDGLP'}


def cause(x):
    c, t, y = x.country, x.tech, x.year
    if x.excess_pj < 0.01 and x.need_gw < 0.002:
        return 'rounding: limit set at full reachable output (no band) and rounded up at 4 decimals'
    if c == 'Ecuador' and t == 'PPHD':
        return 'no CapacityToActivityUnit row: CAU defaults to 1 instead of 31.536 (F2, D1)'
    if c == 'DominicanRepublic' and t in PATH_DR:
        return ('A-O lower limit = TotalAnnualMaxCapacity path x CF x 8760 x 0.0036 x 0.98; ResidualCapacity is the 2018 value only, '
                'so the path increments are built as new capacity')
    if c == 'DominicanRepublic' and t == 'PPDHYD':
        return ('CapacityFactor formula =J227/(J225*8760) omits the 0.0036 PJ/GWh factor (0.0152); '
                'lower = 0.98 x upper from observed generation')
    if c == 'DominicanRepublic' and t in CF_DR:
        return ('CapacityFactor series shared by the distributed fossil and biogas rows (about 0.08); '
                'lower = 0.98 x upper from observed generation')
    if c == 'DominicanRepublic':
        return 'lower = 0.98 x upper from observed generation; residual x CF below it'
    if c == 'CostaRica':
        return ('BAU config history limit from observed generation; A-O ResidualCapacity below the installed capacity '
                'of the BAU TotalAnnualMaxCapacity path')
    if c == 'Ecuador' and t in ('PPHRORAS', 'PPHRORPM', 'PPHRORAM', 'PPHDAMPS', 'PPHDAMPM'):
        return ('2022 CapacityFactor lower than other years while the lower limit is flat; MinCapacityInvestment 2022 '
                'PPHRORAS 0.18, PPHRORPM 0.27, PPHDAMPS 0.0163 GW')
    if c == 'Ecuador' and t in ('PPPVT', 'PPWNDD'):
        return 'residual capacity 0 with a positive history lower limit'
    if c == 'Ecuador':
        return 'residual capacity below observed generation at the row CapacityFactor'
    if c == 'Guatemala':
        return 'residual capacity 0 with a positive history lower limit (first natural gas generation)'
    if c == 'Jamaica' and t == 'PPDSL' and y == 2024:
        return 'residual capacity 0 in 2024 with a positive lower limit'
    return 'residual capacity below observed generation at the row CapacityFactor'


r['cause'] = r.apply(cause, axis=1)
r['note'] = ''
r.loc[r.country.isin(['CostaRica', 'DominicanRepublic', 'Guatemala', 'Jamaica']), 'note'] = \
    'CapacityToActivityUnit in the data is 31.356 (31.4 for some Jamaica techs); workbook band formulas use 8760 x 0.0036 = 31.536'
cols = ['country', 'scenario', 'tech', 'year', 'lower_pj', 'reachable_pj', 'excess_pj', 'need_gw', 'residual_gw', 'cf', 'af', 'cau',
        'maxcap_gw', 'mincapinv_gw', 'cause', 'note']
r[cols].to_csv(f'{JOB}/history_plan_draft.csv', index=False, lineterminator='\n', float_format='%.6g')
print('history_plan_draft rows', len(r)); print(r.groupby('country').size())

b = pd.read_csv(f'{JOB}/logs/stage3_newcap_history_before.csv')
b = b[(b.Year >= 2021) & (b.Year <= 2024)]
g = b.groupby(['Country', 'Technology'])[['BAU', 'NDCNEW', 'LTSNEW']].sum().reset_index()
big = b[b[['BAU', 'NDCNEW', 'LTSNEW']].max(axis=1) > 1e-4]
yrs = big.groupby(['Country', 'Technology']).Year.apply(lambda s: ';'.join(map(str, sorted(set(s))))).to_dict()
g = g[g[['BAU', 'NDCNEW', 'LTSNEW']].max(axis=1) > 1e-4]
J = 'downloads/map_jam'
E = 'downloads/d2_ecu'
M = {
    ('Jamaica', 'PPNGS'): ('CB Hill Run CHP (JPS), natural gas, 10 MW, Dec 2021; no plant commissioned 2022 to 2024',
                           f'OUR Annual Report 2023-2024 PDF p.62; OUR 2023 determination PDF p.78-79 and p.95 ({J})',
                           'year and size differ (model 0.021 GW in 2023-2024)'),
    ('Jamaica', 'PPDSL'): ('none 2021 to 2024', f'OUR Annual Report 2023-2024 PDF p.62; JPS filings 2021-2023 unit tables ({J})', 'no match'),
    ('Jamaica', 'PPHDAM'): ('none; JPS hydro 28.66 MW nameplate in every year', f'JPS filings 2021-2023 ({J})', 'no match'),
    ('Jamaica', 'PPFOI'): ('none (262 MW HFO steam retired in 2020)', '2022 IRP PDF p.39-40 (JAMF-01)', 'no match'),
    ('Jamaica', 'PPPVT'): ('none 2021 to 2024', f'OUR Annual Report 2023-2024 PDF p.62 ({J})', 'no match'),
    ('Jamaica', 'PPWNDON'): ('none 2021 to 2024', f'OUR Annual Report 2023-2024 PDF p.62 ({J})', 'no match'),
    ('Ecuador', 'PPWNDON'): ('Huascachaca wind (Elecaustro): 32.00/28.57 MW Dec 2022 and 49.98 MW Mar 2023 in ARCONEL; CENACE 2 x 18 MW Dec 2022, 50 MW commercial 31 Mar 2023',
                             f'ARCONEL Estadistica 2022 Tabla 27 p.45; 2023 Tabla 27 p.44; CENACE Informe Anual 2022 parte1 p.111; 2023 parte2 p.1 ({E})',
                             'year differs (model 0.032 GW in 2021); size to check'),
    ('Ecuador', 'PPHRORPM'): ('Sarapullo 48.45 MW (Feb 2022 in ARCONEL; commercial 1 Mar 2023 in CENACE); basin and run-of-river type not printed',
                              f'ARCONEL Estadistica 2022 p.45, 2023 p.44; CENACE 2022 parte1 p.111, 2023 parte2 p.1 ({E}); lead P3 report Tabla 5',
                              'model 0.270 GW in 2022 (MinCapacityInvestment); Sarapullo is 0.049 GW'),
    ('Ecuador', 'PPHRORAS'): ('candidates: Chalpi 8.10 MW (Apr 2021), Vindobona 4.85 MW (Feb 2021), Sabanilla 36.00/30.60 MW (Oct 2022), Huayquichuma 6.50 MW (Jan 2024), Abanico increase 15.38 MW (May 2024); basin not printed',
                              f'ARCONEL Estadistica 2021 Tabla 27 p.54, 2022 p.45, 2024 p.44; CENACE 2021 parte2 p.2 ({E})',
                              'model 0.442 GW in 2021-2022 against at most 0.07 GW of candidates'),
    ('Ecuador', 'PPRDSL'): ('candidate: Cuyabeno Crudo Diesel CELEC (Petroecuador, non-incorporated) 25.60/20.74 MW, 2021',
                            f'ARCONEL Estadistica 2021 Tabla 27 p.54 ({E})', 'model 0.618 GW in 2021'),
    ('Ecuador', 'PPNGS'): ('candidate: Shushufindi CG Gas (Petroecuador, non-incorporated) 22.80/15.00 MW, Aug 2021',
                           f'ARCONEL Estadistica 2021 Tabla 27 p.54, Tabla 60 p.75 ({E})', 'model 0.117 GW in 2021'),
    ('Ecuador', 'PPFOI'): ('candidate: Karpowership Emre Bey 105.30/100 MW HFO, leased, Sep 2024 (SNI)',
                           f'ARCONEL Estadistica 2024 p.44 and p.64; CENACE 2024 parte3 p.9 ({E})', 'model 0.095-0.103 GW in 2021'),
    ('Ecuador', 'PPHD'): ('not a commissioning: CapacityToActivityUnit missing (F2)', '', 'removed by D1'),
}
rows = []
for _, x in g.iterrows():
    m = M.get((x.Country, x.Technology), ('', '', 'not yet matched (statistics downloaded, not yet read)'))
    rows.append(dict(country=x.Country, tech=x.Technology, build_years=yrs.get((x.Country, x.Technology), ''),
                     built_gw_2021_2024_BAU=round(x.BAU, 4), built_gw_NDCNEW=round(x.NDCNEW, 4), built_gw_LTSNEW=round(x.LTSNEW, 4),
                     sourced_commissioning=m[0], source_locator=m[1], status=m[2]))
pd.DataFrame(rows).to_csv(f'{JOB}/history_builds_draft.csv', index=False, lineterminator='\n')
print('history_builds_draft rows', len(rows))
