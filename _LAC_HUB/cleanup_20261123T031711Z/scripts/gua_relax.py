"""Step 4.5: find the binding limit group of an infeasible Guatemala scenario under the common Stage 3 rule.

Works on a scratch copy that holds lac_tables.py, config/, inputs/, the Stage 2 controller, the Guatemala model file
and its B1 data files, and stage3_apply.py with the common rule. For each variant, one group of Stage 3 limits is
relaxed by changing one line of a copy of stage3_apply.py, the Guatemala NDC and LTS files are patched and solved
with glpsol, and status, objective and the activity of the relaxed plants (2025 onward) are recorded:
  common            the common rule (no relaxation)
  orphans_free      orphan plants (in the model, not in the controller) not capped
  zero_lower_open   plants with a zero lower limit get the open upper limit instead of 0
  band_open         plants with a positive lower limit get an open upper limit instead of 1.05 x lower
  former_exception  orphans_free and zero_lower_open together (the removed exception)
Usage: python gua_relax.py <scratch root> <glpsol> <out.csv>
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

root, glpsol, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
base = (root / 'stage3_apply.py').read_text(encoding='utf-8')
ORPH = "            orphan_techs = [t for t in all_pp_in_txt if t not in ctrl_pp_techs]"
ZERO = "                zero_lower_upper = 0.0"
BAND = 'LOWER_TO_UPPER_FACTOR = LT.controller("lower_to_upper_factor", "3")'
for s in (ORPH, ZERO, BAND):
    assert base.count(s) == 1, s
VARIANTS = {
    'common': [],
    'orphans_free': [(ORPH, "            orphan_techs = []")],
    'zero_lower_open': [(ZERO, '                zero_lower_upper = LT.controller("uncapped_value", "3")')],
    'band_open': [(BAND, 'LOWER_TO_UPPER_FACTOR = 1e9')],
}
VARIANTS['former_exception'] = VARIANTS['orphans_free'] + VARIANTS['zero_lower_open']
G = root / 'Guatemala' / 'GUA_ENERGY'


def activity(output, years_from=2025):
    """Sum of TotalTechnologyAnnualActivity by plant over 2025+ from the glpsol -o file (column listing)."""
    acts = {}
    rx = re.compile(r'^\s*\d+\s+TotalTechnologyAnnualActivity\[([^,\]]+),([^,\]]+),(\d{4})\]')
    lines = output.read_text(errors='replace').splitlines()
    for i, ln in enumerate(lines):
        m = rx.match(ln)
        if m and int(m.group(3)) >= years_from and m.group(2).startswith('PP'):
            parts = ln.split()
            vals = parts[2:] if len(parts) > 2 else lines[i + 1].split()
            try:
                v = float(vals[1]) if vals[0] in ('B', 'NL', 'NU', 'NF', 'NS') else float(vals[0])
            except (ValueError, IndexError):
                continue
            acts[m.group(2)] = acts.get(m.group(2), 0.0) + v
    return acts


rows = []
for name, subs in VARIANTS.items():
    src = base
    for a, b in subs:
        src = src.replace(a, b)
    (root / 'stage3_apply_variant.py').write_text(src, encoding='utf-8')
    subprocess.run([sys.executable, 'stage3_apply_variant.py', '--root', '.', '--clean', '--uncap-pp-maxcap',
                    '--countries', 'Guatemala', '--scenarios', 'NDC', 'LTS'], cwd=root, capture_output=True,
                   env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'})
    log = (root / 'variant_apply.log')
    for scen in ('NDC', 'LTS'):
        d = G / 'Executables' / f'{scen}_FINAL_0'
        o = d / f'{scen}_FINAL_0_output.txt'
        subprocess.run([glpsol, '-m', 'OSeMOSYS_Model.txt', '-d', str(d / f'{scen}_FINAL_0.txt'), '-o', str(o)],
                       cwd=G, capture_output=True)
        status = obj = ''
        with open(o, errors='replace') as fh:
            for _ in range(15):
                ln = fh.readline()
                if ln.startswith('Status:'):
                    status = ln.split(':', 1)[1].strip()
                if ln.startswith('Objective:'):
                    obj = ln.split('=', 1)[1].split('(')[0].strip() if '=' in ln else ''
        acts = activity(o) if status == 'OPTIMAL' else {}
        rows.append(dict(variant=name, scenario=scen, status=status, objective=obj,
                         pp_activity_2025_on_pj=';'.join(f'{k}={v:.3f}' for k, v in sorted(acts.items()) if abs(v) > 1e-6)))
        print(name, scen, status, obj, flush=True)
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
