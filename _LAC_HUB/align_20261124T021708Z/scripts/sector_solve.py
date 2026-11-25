"""Status and objective of every scenario of the sector models and JAM_TRANSPORT: each data file the model's own B1
runner wrote (Executables/<scenario>_0/<scenario>_0.txt) is solved with the model's OSeMOSYS_Model.txt; the solver
output is deleted after its status and objective are read (the runners delete theirs too).
Usage: python -I sector_solve.py <root> <out.csv>"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import subprocess
import sys
import time
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
MODELS = ['CostaRica/CR_AFOLU/t1_confection', 'CostaRica/CR_WASTE', 'DominicanRepublic/RD_AFOLU', 'DominicanRepublic/RD_WASTE',
          'Ecuador/ECU_WASTE', 'Ecuador/ECU_USCUSS', 'Guatemala/GUA_WASTE', 'Honduras/HON_AFOLU/HON_AFOLU',
          'Honduras/HON_WASTE', 'Jamaica/JAM_AFOLU', 'Jamaica/JAM_WASTE', 'Jamaica/JAM_TRANSPORT']
rows = []
for m in MODELS:
    d = root / m
    for dat in sorted((d / 'Executables').glob('*_0/*_0.txt')) if (d / 'Executables').exists() else []:
        o = dat.with_name(dat.stem + '_check_output.txt')
        t0 = time.time()
        subprocess.run([M.GLPSOL, '-m', str(d / 'OSeMOSYS_Model.txt'), '-d', str(dat), '-o', str(o)], capture_output=True, cwd=d)
        st, obj = 'NO OUTPUT', ''
        if o.exists():
            with open(o, encoding='utf-8', errors='replace') as fh:
                for line in fh:
                    if line.startswith('Status:'):
                        st = line.split(':', 1)[1].strip()
                    elif line.startswith('Objective:'):
                        obj = line.split('=', 1)[1].split('(')[0].strip()
                        break
            o.unlink()
        rows.append([m, dat.parent.name[:-2], st, obj, round(time.time() - t0, 1)])
        print(rows[-1], flush=True)
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['model', 'scenario', 'status', 'objective', 'seconds'])
    w.writerows(rows)
