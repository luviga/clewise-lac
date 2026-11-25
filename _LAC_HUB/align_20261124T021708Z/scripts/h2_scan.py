"""List the hydrogen technologies of every model: technologies with a hydrogen fuel (name holds HYD and is not a
hydro fuel) in their InputActivityRatio or OutputActivityRatio, from the compiled B1 inputs of every scenario.
Usage: python -I h2_scan.py   (prints country, model, fuel, technology, side)"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
from pathlib import Path

MODELS = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
          'Ecuador': 'Ecuador/ECU_Energy', 'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY',
          'Jamaica': 'Jamaica/JAM_ENERGY', 'Jamaica_transport': 'Jamaica/JAM_TRANSPORT'}
rows = set()
for c, d in MODELS.items():
    for sc in sorted((M.ROOT / d / 'B1_Output_Params').glob('*')):
        for side, fn in (('input', 'InputActivityRatio.csv'), ('output', 'OutputActivityRatio.csv')):
            p = sc / fn
            if not p.exists():
                continue
            with open(p, encoding='utf-8') as fh:
                for r in csv.DictReader(fh):
                    f = r['FUEL']
                    if 'HYD' in f.upper():
                        rows.add((c, d, f, r['TECHNOLOGY'], side))
out = M.JOB / 'work' / 'h2_scan.csv'
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['country', 'model', 'fuel', 'technology', 'side'])
    for r in sorted(rows):
        w.writerow(r)
print(len(rows), 'rows ->', out)
