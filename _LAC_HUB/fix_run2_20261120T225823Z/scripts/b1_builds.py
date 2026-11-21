"""Power-plant NewCapacity 2018-2024 from the B1 solve outputs (Executables/<scen>_0/<scen>_0_Output.csv) of one country.
Copies the three output CSVs to logs/phaseC/<Country>/outputs/ (Executables is overwritten by later runs) and prints builds.
Usage: py -I scripts/b1_builds.py <Country> [--from-logs]"""
import os, shutil, sys
import pandas as pd

M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
     'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
     'Jamaica': 'Jamaica/JAM_ENERGY'}
JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
c = sys.argv[1]
od = f'{JOB}/logs/phaseC/{c}/outputs'
os.makedirs(od, exist_ok=True)
rows = []
for s in ['BAU', 'NDCNEW', 'LTSNEW']:
    src = f'C:/clw_fix/{M[c]}/Executables/{s}_0/{s}_0_Output.csv'
    dst = f'{od}/{s}_0_Output.csv'
    if '--from-logs' not in sys.argv:
        shutil.copy2(src, dst)
    d = pd.read_csv(dst, usecols=['Technology', 'Year', 'NewCapacity'], low_memory=False)
    d = d[d.Technology.astype(str).str.match(r'^(PP|PWR)') & (d.Year <= 2024) & (d.NewCapacity.fillna(0) > 1e-6)]
    for _, r in d.iterrows():
        rows.append(dict(scenario=s, tech=r.Technology, year=int(r.Year), gw=r.NewCapacity))
o = pd.DataFrame(rows)
o.to_csv(f'{od}/builds_2018_2024.csv', index=False, lineterminator='\n')
if len(o):
    p = o.pivot_table(index=['tech', 'year'], columns='scenario', values='gw', aggfunc='sum').fillna(0)
    print(p.round(4).to_string())
else:
    print('no builds')
