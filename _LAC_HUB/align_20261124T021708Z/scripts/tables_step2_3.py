"""Add the rows of steps 2 and 3 to the configuration tables (run once; checks it is not run twice).
technology_types.csv: group hydrogen (from work/h2_scan.csv, the six energy models; technologies with a hydrogen
fuel in their input or output), groups capacity_kind_solar, _wind, _hydro, _nonhydro_renewable (name tokens).
stage_controller.csv: constants of the capacity rule and of the emission cap step; orphan_cap_exempt_scenarios
and target_hold_year rows removed."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv

TT = M.ROOT / 'config' / 'scenarios' / 'technology_types.csv'
SC = M.ROOT / 'config' / 'scenarios' / 'rules' / 'stage_controller.csv'

lines = TT.read_text(encoding='utf-8').splitlines()
assert not any(l.startswith('hydrogen,') for l in lines), 'already applied'
scan = list(csv.DictReader(open(M.JOB / 'work' / 'h2_scan.csv', encoding='utf-8')))
fuels = {}
for r in scan:
    if r['country'] == 'Jamaica_transport':
        continue
    fuels.setdefault((r['country'], r['technology']), set()).add(r['fuel'])
new = []
for (c, t), fs in sorted(fuels.items()):
    new.append(f"hydrogen,{t},name,{c},,scenario_rules.py,hydrogen technology (input or output fuel {' '.join(sorted(fs))}): activity upper limit 0 and no lower limit in every scenario")
KIND = {'solar': ['SOL', 'SUN', 'SPV', 'PV', 'CSP'], 'wind': ['WND', 'WIND', 'WNO', 'WNS'],
        'hydro': ['HYD', 'DAM', 'ROR', 'PPHD', 'PPIHD'],
        'nonhydro_renewable': ['GEO', 'SOL', 'SUN', 'SPV', 'PV', 'CSP', 'WND', 'WIND', 'WNO', 'WNS', 'BMS', 'BIM', 'BIO', 'BGS', 'SUG']}
for k, toks in KIND.items():
    for tok in toks:
        new.append(f"capacity_kind_{k},{tok},token,all,,renewable_targets.py,name token of the plants whose capacity factor turns published {k.replace('_', ' ')} capacity into generation (capacity rule)")
with open(TT, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(lines + new) + '\n')

rows = SC.read_text(encoding='utf-8').splitlines()
rows = [r for r in rows if not r.startswith('3,orphan_cap_exempt_scenarios,') and not r.startswith('all,target_hold_year,')]
add = [
    '1,capacity_mw_per_gw,all,1000,MW per GW,renewable_targets.py,unit change of published capacity (capacity rule)',
    '1,capacity_pj_per_gw_year,all,31.536,PJ per GW and year,renewable_targets.py,generation of 1 GW running a whole year (8760 hours times 3.6 TJ per MWh); capacity rule',
    '3,cap_start_year,all,2036,year,stage3_apply.py; stage3_emission_cap.py,first year of the energy emission cap of a scenario with an energy_emission_reduction_vs_bau row; from this year its power plant share pins are released (upper limits open; frozen output and committed builds keep their lower limits)',
    '3,cap_from_year,all,2035,year,stage3_emission_cap.py,year whose solved energy emissions of the NDC scenario start the straight line of the cap',
    '3,cap_target_year,all,2050,year,stage3_emission_cap.py,year whose cap is BAU energy emissions times (1 minus r)',
]
i = max(k for k, r in enumerate(rows) if r.startswith('3,'))
rows = rows[:i + 1] + add[2:] + rows[i + 1:]
j = max(k for k, r in enumerate(rows) if r.startswith('1,'))
rows = rows[:j + 1] + add[:2] + rows[j + 1:]
with open(SC, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(rows) + '\n')
print('technology_types rows added:', len(new), '; controller rows now', len(rows))
