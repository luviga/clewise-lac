"""A2: history_plan.csv (D2a, D2b, D2d, D2e) and history_builds.csv (D2c).
history_plan: one line per config change of proposals_parts/d2_config.csv, per D2b tech still above reachable output after
D13, D7a and D2f (logs/reach_BAU_after_estimate.csv), and per history difference left on purpose (rounding, one-sided keys).
history_builds: per power technology built in 2021-2024 at 4ba69d6 (logs/stage3_newcap_history_before.csv), with the
sourced commissioning gathered so far (COMM below; research notes give the locators). 'after' columns are filled in Phase D."""
import json
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
plan = []
d2 = pd.read_csv(JOB + '/proposals_parts/d2_config.csv', dtype=str, keep_default_na=False)
for _, r in d2.iterrows():
    if r.kind == 'config_row':
        rec = json.loads(r.new_value)
        what = f'{r.Parameter} of {r.Tech} differs from BAU in 2018-2024 (history_diff_before.csv)'
        if 'Write' in str(rec.get('Method', '')) and r.sheet == 'Electrical':
            ch = 'new history-only Write row: BAU values to 2024, B1 default from 2025'
            why = 'the scenario had no row; a history-only row leaves 2025 on at the default the scenario already had'
        elif r.sheet == 'SmartGrid':
            ch = 'new Exact_Multiplier row: BAU multipliers 2021-2024, 1 from 2025'
            why = 'the scenario had no multiplier row; multiplier 1 keeps its values from 2025'
        else:
            ch = 'new Electrical Overwrite row with every year explicit: BAU compiled values to 2024, own 4ba69d6 values from 2025'
            why = 'transport sheets have no year points; Electrical rows run after the transport block, so one row fixes history only'
        plan.append(dict(country=r.country, sheet=r.sheet, row=r.row, scenario=r.scenario, tech=r.Tech, parameter=r.Parameter,
                         what_differs=what, proposed_change=ch, why_least_change=why, decision=r.decision))
    else:
        plan.append(dict(country=r.country, sheet=r.sheet, row=r.row, scenario=r.scenario, tech=r.Tech, parameter=r.Parameter,
                         what_differs=f'history elements {r.year} differ from BAU', proposed_change=r.derivation,
                         why_least_change='only the history elements of an existing row change', decision=r.decision))
hd = pd.read_csv(JOB + '/history_diff_before.csv')
small = hd[hd.absd <= 0.00005].groupby(['country', 'parameter']).size()
for (c, p), n in small.items():
    plan.append(dict(country=c, sheet='', row='', scenario='NDCNEW;LTSNEW', tech='(several)', parameter=p,
                     what_differs=f'{n} history values differ by at most 0.00005 (B1 rounding to 4 decimals)',
                     proposed_change='none', why_least_change='decision D2e: rounding-only differences stay (listed in GAPS)',
                     decision='D2e'))
one = hd[hd.presence == 'right_only'].groupby(['country', 'parameter', 'technology']).size()
for (c, p, t), n in one.items():
    plan.append(dict(country=c, sheet='', row='', scenario='NDCNEW;LTSNEW', tech=t, parameter=p,
                     what_differs=f'{n} key-years present only in the policy scenarios (technology that exists only there)',
                     proposed_change='none', why_least_change='decision D2e: one-sided keys of policy-only technologies stay (GAPS)',
                     decision='D2e'))
ra = pd.read_csv(JOB + '/logs/reach_BAU_after_estimate.csv')
ra = ra[ra.excess_pj > 1e-6]
for (c, t), g in ra.groupby(['country', 'tech']):
    plan.append(dict(country=c, sheet='A-O / B1 BAU', row='', scenario='BAU (all)', tech=t,
                     parameter='TotalTechnologyAnnualActivityLowerLimit',
                     what_differs=f'history lower limit above residual-capacity output in {" ".join(map(str, g.year))} '
                                  f'(max {g.excess_pj.max():.4f} PJ, needs up to {g.need_gw.max():.4f} GW) after D13, D7a, D2f',
                     proposed_change='checked against sourced commissioning in history_builds.csv; fixed at its cause only '
                                     'with a source (D2b, D2c)',
                     why_least_change='residual capacity plus sourced commissioning is the reachability test of D2b',
                     decision='D2b'))
pd.DataFrame(plan).to_csv(JOB + '/history_plan.csv', index=False, lineterminator='\n')
# builds
COMM = {  # (country, tech): (sourced commissioning GW 2021-2024, plants and dates, source locator)
    ('Jamaica', 'PPNGS'): (0.010, 'JPS/CB Hill Run CHP, natural gas, 10 MW, December 2021', 'OUR Annual Report 2023-2024 PDF p.62; JPS Annual Filing 2022 PDF p.14 (research/map_jam.md)'),
    ('Jamaica', 'PPDSL'): (0.0, 'no diesel plant commissioned 2021-2024', 'OUR Annual Report 2023-2024 PDF p.62; JPS MCR tables 2021-2023'),
    ('Jamaica', 'PPFOI'): (0.0, 'no fuel-oil plant commissioned 2021-2024', 'OUR Annual Report 2023-2024 PDF p.62'),
    ('Jamaica', 'PPHDAM'): (0.0, 'no hydro plant commissioned; JPS hydro 28.66 MW nameplate every year', 'OUR Annual Report 2024-2025 PDF p.57 Table 23'),
    ('Jamaica', 'PPPVT'): (0.0, 'no utility PV commissioned 2021-2024', 'OUR Annual Report 2024-2025 PDF p.57 Table 23'),
    ('Jamaica', 'PPWNDON'): (0.0, 'no wind plant commissioned 2021-2024', 'OUR Annual Report 2024-2025 PDF p.57 Table 23'),
    ('Ecuador', 'PPWNDON'): (0.04998, 'Minas de Huascachaca 32.00 MW (Dec 2022) and +17.98 MW (Mar 2023), 49.98 MW', 'ARCONEL Estadistica 2022 Tabla 27 p.45; 2023 Tabla 27 p.44'),
    ('Ecuador', 'PPHRORPM'): (0.25245, 'Sarapullo 48.45 MW (2022, commercial Mar 2023), Alluriquin 204.00 MW (Dec 2024, experimental)', 'ARCONEL Estadistica 2022 Tabla 27 p.45; 2024 Tabla 27 p.44; CENACE 2022 parte1 p.111'),
    ('Ecuador', 'PPHRORAS'): (0.05888, 'Sabanilla 36.00 MW (Oct 2022), Abanico +15.38 MW (May 2024), Huayquichuma 6.50 MW (Jan 2024), Mira 0.99 MW (Apr 2024); Amazon or Pacific basin not printed', 'ARCONEL Estadistica 2022 Tabla 27 p.45; 2024 Tabla 27 p.44'),
    ('Ecuador', 'PPHDAMPS'): (0.0091, 'Chalpi 8.10 MW (Apr 2021), Ulba 1.00 MW (Apr 2023); dam or run-of-river not printed', 'ARCONEL Estadistica 2021 Tabla 27 p.54; 2023 Tabla 27 p.44'),
    ('Ecuador', 'PPFOI'): (0.100, 'Karpowership Emre Bey (Electroguayas), HFO, 100 MW effective, Sep 2024', 'ARCONEL Estadistica 2024 Tabla 27 p.44; CENACE 2024 parte3 p.9 Tabla 3.2'),
    ('Ecuador', 'PPRDSL'): (0.0484, 'Cuyabeno Crudo Diesel 25.60 MW (2021) and Shushufindi CG Gas 22.80 MW (Aug 2021), isolated self-generation of Petroecuador', 'ARCONEL Estadistica 2021 Tabla 27 p.54'),
    ('Ecuador', 'PPPVD'): (0.0, 'no distributed PV listed among plants entering operation 2021-2024', 'ARCONEL Estadistica 2021-2024 Tabla 27'),
    ('Ecuador', 'PPPVT'): (0.001, 'San Cristobal Solar 1.00 MW (Jan 2022, Galapagos, isolated)', 'ARCONEL Estadistica 2022 Tabla 27 p.45'),
    ('Ecuador', 'PPNGS'): (0.0, 'no SNI gas plant entered operation 2021-2024 (Machala Gas unchanged)', 'ARCONEL Estadistica 2020 Annex A.1 p.212; 2024 Tabla 36 p.50'),
    ('Ecuador', 'PPHD'): (0.0, 'no distributed hydro of 79 GW; decision D1 removes the cause (CapacityToActivityUnit)', 'decision D1'),
}
b = pd.read_csv(JOB + '/history_builds_draft.csv', dtype=str, keep_default_na=False)
out = []
for _, r in b.iterrows():
    k = (r.country, r.tech)
    gw, plants, loc = COMM.get(k, ('', '', ''))
    out.append(dict(country=r.country, tech=r.tech, build_years_before=r.build_years,
                    built_gw_2021_2024_before_BAU=r.built_gw_2021_2024_BAU, before_NDCNEW=r.built_gw_NDCNEW,
                    before_LTSNEW=r.built_gw_LTSNEW, after_BAU='', after_NDCNEW='', after_LTSNEW='',
                    sourced_commissioning_gw=gw, plants_and_dates=plants, source_locator=loc, cause='', fix='', status='pending'))
pd.DataFrame(out).to_csv(JOB + '/history_builds.csv', index=False, lineterminator='\n')
print(len(plan), len(out))
