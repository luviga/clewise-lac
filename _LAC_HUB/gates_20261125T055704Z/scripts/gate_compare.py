"""Gate comparison of two full runs held as snapshots (a2_snapshot.py):

  1. tracked outputs (compiled A2 and B1 parameters, stage outputs) with a3_compare.py (no tolerance);
  2. B1 data files (<scen>_0.txt) and Stage 3 input data files (<scen>_FINAL_0.txt), by parameter and index
     (dat_compare.py);
  3. Stage 0 and Stage 3 objectives and statuses (solves_stage0.jsonl, solves_stage3.jsonl).
Writes <out>_tree.csv (a3_compare rows), <out>_data.csv (data-file differences) and <out>_objectives.csv.

Usage: python gate_compare.py <snapshot A> <snapshot B> <out prefix> [--map NEW=OLD,...]
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dat_compare import compare_dat  # noqa: E402

A, B, OUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
extra = sys.argv[4:]
S = Path(__file__).resolve().parent
r = subprocess.run([sys.executable, '-I', str(S / 'a3_compare.py'), str(A / 'tree'), str(B / 'tree'), OUT + '_tree.csv'] + extra,
                   capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode:
    print(r.stderr[-2000:])

rows = []


def data_pairs(snap):
    out = {}
    for f in (snap / 'logs' / 'a2b1').glob('*/b1/data_files/*.txt'):
        out[('B1 data file', f.parts[-4], f.name)] = f
    for f in (snap / 'final_data').rglob('*_FINAL_0.txt'):
        out[('Stage 3 input', f.parent.relative_to(snap / 'final_data').as_posix(), f.name)] = f
    return out


da, db = data_pairs(A), data_pairs(B)
counts = {}
for k in sorted(set(da) | set(db)):
    if k not in da or k not in db:
        rows.append(dict(kind=k[0], model=k[1], file=k[2], param='', key='', diff='file only in ' + ('B' if k not in da else 'A'), a='', b=''))
        continue
    diffs = compare_dat(da[k], db[k])
    counts[k] = len(diffs)
    for d in diffs:
        rows.append(dict(kind=k[0], model=k[1], file=k[2], param=d.get('param', ''), key=d.get('key', ''),
                         diff=d.get('kind', ''), a=d.get('a', ''), b=d.get('b', '')))
with open(OUT + '_data.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['kind', 'model', 'file', 'param', 'key', 'diff', 'a', 'b'], lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(f'data files A {len(da)}, B {len(db)}; files with differences {sum(1 for v in counts.values() if v)}; rows {len(rows)}')
for k, v in counts.items():
    if v:
        print('  ', k, v)


def objectives(snap):
    out = {}
    for stage, name in (('S0', 'solves_stage0.jsonl'), ('S3', 'solves_stage3.jsonl')):
        f = snap / 'logs' / name
        if f.exists():
            for line in f.read_text(encoding='utf-8').splitlines():
                d = json.loads(line)
                obj = d.get('objective') or ''
                val = obj.split('=')[1].split('(')[0].strip() if '=' in obj else obj
                out[(stage, d['country'], d['scenario'])] = (d.get('status'), val)
    return out


oa, ob = objectives(A), objectives(B)
orows = []
for k in sorted(set(oa) | set(ob)):
    sa, va = oa.get(k, ('', ''))
    sb, vb = ob.get(k, ('', ''))
    orows.append(dict(stage=k[0], country=k[1], scenario=k[2], status_a=sa, objective_a=va, status_b=sb, objective_b=vb,
                      equal='yes' if (sa, va) == (sb, vb) else 'no'))
with open(OUT + '_objectives.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(orows[0].keys()) if orows else ['stage'], lineterminator='\n')
    w.writeheader()
    w.writerows(orows)
print(f'objectives: {len(orows)} rows, {sum(1 for x in orows if x["equal"] == "no")} differ')
for x in orows:
    if x['equal'] == 'no':
        print('  ', x)
