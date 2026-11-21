"""Fill cause, fix and status of history_builds.csv after the Phase D run (values from fix_checks2 'after' columns and the
research notes). Causes are stated only where traced by values; the rest say so."""
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
h = pd.read_csv(JOB + '/history_builds.csv', dtype=str, keep_default_na=False)
C = {
    ('Ecuador', 'PPHD'): ('no CapacityToActivityUnit row (default 1)', 'D1 row of 31.536; build removed'),
    ('Ecuador', 'PPRDSL'): ('residual 0.2345 GW against a history lower limit of 7.49 PJ at CF 0.306 (needs about 0.78 GW); ARCONEL prints 1,264 MW of non-incorporated engine capacity without a split by fuel',
                            'not fixed: no sourced capacity of isolated diesel plants at oil facilities (GAPS)'),
    ('Ecuador', 'PPHRORPM'): ('TotalAnnualMinCapacityInvestment 0.27 GW in 2022 (A-O Primary Techs row 289); sourced: Sarapullo 48.45 MW (2022) and Alluriquin 204 MW (Dec 2024)',
                              'not fixed: the 2022 ARCONEL statistics have no public download address (sources_pending.csv)'),
    ('Ecuador', 'PPHRORAS'): ('TotalAnnualMinCapacityInvestment 0.18 GW in 2022 (row 279) plus economic builds in 2021 (history years have no cap); sourced: Sabanilla 36 MW (2022), Abanico +15.38 MW (2024)',
                              'not fixed: as PPHRORPM'),
    ('Ecuador', 'PPHDAMPS'): ('TotalAnnualMinCapacityInvestment 0.0163 GW in 2022-2024 (row 249); sourced small hydro additions 9.1 MW, class not printed', 'not fixed'),
    ('Ecuador', 'PPWNDON'): ('build of 0.032 GW in 2021 against Huascachaca 49.98 MW in Dec 2022 and Mar 2023', 'not fixed: timing'),
    ('Ecuador', 'PPFOI'): ('build 0.095 GW in 2021 against the Karpowership 100 MW of Sep 2024', 'not fixed: timing'),
    ('Ecuador', 'PPNGS'): ('build 0.117 GW in 2021; no gas plant entered 2021-2024', 'not fixed'),
    ('Ecuador', 'PPPVD'): ('build 0.115 GW in 2021; no distributed PV listed among new plants', 'not fixed'),
    ('Jamaica', 'PPNGS'): ('build 0.0168 GW in 2023-2024 against the 10 MW Hill Run CHP of Dec 2021', 'not fixed'),
    ('Jamaica', 'PPDSL'): ('history lower limit above residual output; no diesel plant commissioned', 'not fixed'),
    ('Jamaica', 'PPHDAM'): ('history lower limit above residual output (28.66 MW nameplate every year)', 'not fixed'),
    ('DominicanRepublic', 'PPPVT'): ('A-O TotalAnnualMaxCapacity path (Primary Techs row 176) 2021-2024 = 0.366, 0.417, 0.675, 0.675 GW against OC-SENI solar 305.48, 405.48, 675.08, 933.48 MW (Tabla 36): builds 488 MW against 778 MW commissioned',
                                     'not fixed: replacing the path changes BAU capacity in every later year (GAPS)'),
    ('DominicanRepublic', 'PPPVD'): ('capacity path against CNE net metering 177.06 MW (2020) to 424.32 MW (2024): +247 MW against 143 MW built', 'not fixed (GAPS)'),
    ('DominicanRepublic', 'PPWNDON'): ('Los Guzmancito II 46.80 MW (2022) matches the 0.0467 GW build', 'matches'),
    ('DominicanRepublic', 'PPHDAM'): ('+7.56 MW SENI hydro addition is dated 2019, the model builds it in 2024 (policy) or 0.7 MW (BAU)', 'not fixed: timing'),
    ('DominicanRepublic', 'PPICEFOI'): ('fuel-oil engines: Karpowership Azua 188.66 MW (Jan 2024), Pimentel 4 36.26 MW (May 2024), retirements 76.86 and 17.4 MW; net +130.68 MW', 'not fixed'),
    ('DominicanRepublic', 'PPDHYD'): ('capacity factor 0.0152 (formula without 0.0036)', 'D2f formula and UN-sourced activity limit; no build'),
    ('DominicanRepublic', 'PPDBGS'): ('capacity factor 0.08 copied from distributed diesel', 'IRENA-sourced capacity factor (D2c); build within 2 MW of the +2 MW IRENA addition in 2022'),
    ('CostaRica', 'PWRDSL'): ('PTA Moin 105 MW rented diesel blocks entered Mar-Apr 2024 (CENCE Informe 2024 p.25)', '2024 build matches; 2022 build has no source'),
    ('CostaRica', 'PWRSUG'): ('policy transport history added electricity demand', 'D2e transport alignment and BAU PWRSUG history cap; no build'),
    ('CostaRica', 'PWRHYDROR'): ('2023 re-entries 46.84 MW; net hydro +21.7 MW 2020-2024', 'not fixed'),
    ('CostaRica', 'PWRGEO'): ('no geothermal commissioning 2021-2024 (CENCE); residual 0.229 GW against BAU history caps about twice the sourced capacity', 'not fixed'),
    ('CostaRica', 'PWRWNONS'): ('only PE Tilaran 17.4 MW (Nov 2023)', 'not fixed'),
    ('CostaRica', 'PWRFOI'): ('no bunker plant added 2021-2024', 'not fixed'),
    ('CostaRica', 'PWRSPVTRN'): ('Huacas 5.1 MW and Valle Escondido 4.987 MW in 2024 (10.087 MW)', 'policy builds match within 2 MW'),
    ('Guatemala', 'PPNGS'): ('Actun Can 2.586 MW from Aug 2020 not in the residual', 'build below 2 MW after D13'),
}
for i, r in h.iterrows():
    k = (r.country, r.tech)
    if k in C:
        h.at[i, 'cause'], h.at[i, 'fix'] = C[k]
    elif not r.get('cause', ''):
        h.at[i, 'cause'] = 'not traced'
    h.at[i, 'status'] = r.get('status_after', '') or r.status
h.to_csv(JOB + '/history_builds.csv', index=False, lineterminator='\n')
print(h[['country', 'tech', 'after_BAU', 'after_NDCNEW', 'after_LTSNEW', 'sourced_commissioning_gw', 'status']].to_string())
