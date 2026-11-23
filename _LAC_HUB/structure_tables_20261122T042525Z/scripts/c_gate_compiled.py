"""Compiled inputs of two A2 and B1 runs, compared by key: the A2 files installed per scenario, the B1 output
parameters per scenario, and the B1 data files (OSeMOSYS .txt, parsed); plus the B1 solve status and objective.

Usage: py -I c_gate_compiled.py <logs A (a2b1 folder)> <logs B (a2b1 folder)> <out.csv> [--map NEW=OLD,...]
  --map: scenario folder and data file names of run B written back to run A names; with a map the Scenario
         label column of the A2 files is compared apart (kind label) and does not count as a value difference.
Prints counts per country and scenario; exit 1 if any value difference.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import csv  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

from dat_compare import compare_dat  # noqa: E402
from keyed_compare import compare_dirs  # noqa: E402

A, B, OUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
MAP = {}
if '--map' in sys.argv:
    for pair in sys.argv[sys.argv.index('--map') + 1].split(','):
        new, old = pair.split('=')
        MAP[old] = new
COUNTRIES = ['CostaRica', 'DominicanRepublic', 'Ecuador', 'Guatemala', 'Honduras', 'Jamaica']
SCENS = ['BAU', 'NDCNEW', 'LTSNEW']  # names of run A (the baseline)
rows = []
bad = 0


def objectives(p):
    s = json.loads(Path(p).read_text(encoding='utf-8'))
    out = {}
    for x in s.get('solves', []):
        name = Path(x['data'].replace('\\\\', '\\').replace('\\', '/')).stem
        out[name] = (x.get('status'), x.get('objective'))
    return out


for c in COUNTRIES:
    oa = objectives(A / c / 'b1' / 'summary.json')
    ob = objectives(B / c / 'b1' / 'summary.json')
    for s in SCENS:
        sb = MAP.get(s, s)
        n = {}
        ign = ('Scenario',) if MAP else ()
        d1 = compare_dirs(A / c / 'a2' / 'installed' / s, B / c / 'a2' / 'installed' / sb, ignore_cols=ign)
        d2 = compare_dirs(A / c / 'b1' / 'B1_Output_Params' / s, B / c / 'b1' / 'B1_Output_Params' / sb, ignore_cols=ign)
        d3 = compare_dat(A / c / 'b1' / 'data_files' / f'{s}_0.txt', B / c / 'b1' / 'data_files' / f'{sb}_0.txt')
        for part, ds in (('A2 installed', d1), ('B1 output parameters', d2), ('B1 data file', d3)):
            n[part] = len(ds)
            bad += len(ds)
            for d in ds:
                rows.append([c, s, sb, part, d.get('file', d.get('param', '')), d.get('key', ''), d.get('kind', ''),
                             d.get('a', ''), d.get('b', '')])
        if MAP:  # labels apart
            for part, sub in (('A2 installed', 'a2/installed'), ('B1 output parameters', 'b1/B1_Output_Params')):
                la, lb = set(), set()
                for f in (A / c / sub / s).glob('*.csv'):
                    la |= {r.get('Scenario') for r in csv.DictReader(open(f, encoding='utf-8')) if 'Scenario' in r}
                for f in (B / c / sub / sb).glob('*.csv'):
                    lb |= {r.get('Scenario') for r in csv.DictReader(open(f, encoding='utf-8')) if 'Scenario' in r}
                if la != lb:
                    rows.append([c, s, sb, part, '(all files)', 'Scenario', 'label', '|'.join(sorted(x for x in la if x)),
                                 '|'.join(sorted(x for x in lb if x))])
        sa_, sb_ = oa.get(f'{s}_0'), ob.get(f'{sb}_0')
        same = sa_ == sb_
        if not same:
            bad += 1
            rows.append([c, s, sb, 'B1 solve', f'{s}_0', '', 'status or objective', str(sa_), str(sb_)])
        print(c, s, '->', sb, n, 'B1 solve status and objective equal' if same else 'B1 solve DIFFERS',
              sa_[0] if sa_ else None)
with open(OUT, 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['country', 'scenario_a', 'scenario_b', 'part', 'file_or_parameter', 'key', 'kind', 'a', 'b'])
    w.writerows(rows)
print('value differences', bad, 'rows written', len(rows))
sys.exit(1 if bad else 0)
