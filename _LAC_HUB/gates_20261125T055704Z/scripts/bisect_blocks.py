"""Find which parameter blocks of a data file make it infeasible: start from a feasible data file (good) and copy
the blocks that differ from the infeasible one (bad) half at a time. Usage:
  python -I bisect_blocks.py <model.txt> <good.txt> <bad.txt> <workdir> [--list | --try p1,p2,...]
Prints the blocks that differ and, step by step, the status of each trial. Writes trials to <workdir>."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import re
import subprocess
import sys
from pathlib import Path

model, good, bad, wd = sys.argv[1:5]
wd = Path(wd)
wd.mkdir(parents=True, exist_ok=True)


def blocks(t):
    out = {}
    for m in re.finditer(r'^param\s+(\w+)\s+default[^\n]*\n', t, flags=re.M):
        e = t.find('\n;', m.end())
        out[m.group(1)] = (m.start(), e + 2)
    return out


g = Path(good).read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
b = Path(bad).read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
gb, bb = blocks(g), blocks(b)
diff = [p for p in bb if p in gb and g[gb[p][0]:gb[p][1]] != b[bb[p][0]:bb[p][1]]]
print('differing blocks:', diff, flush=True)
if '--list' in sys.argv:
    sys.exit(0)


def build(ps, name):
    t = g
    for p in sorted(ps, key=lambda p: -gb[p][0]):
        s, e = gb[p]
        bs, be = bb[p]
        t = t[:s] + b[bs:be] + t[e:]
    f = wd / f'{name}.txt'
    f.write_text(t, encoding='utf-8')
    return f


def solve(f):
    o = f.with_name(f.stem + '_out.txt')
    subprocess.run([M.GLPSOL, '-m', model, '-d', str(f), '-o', str(o)], capture_output=True, timeout=1800)
    st = 'NO STATUS'
    with open(o, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            if line.startswith('Status:'):
                st = line.split(':', 1)[1].strip()
                break
    o.unlink()
    return st


if '--try' in sys.argv:
    ps = sys.argv[sys.argv.index('--try') + 1].split(',')
    print('trial', ps, '->', solve(build(ps, 'single')), flush=True)
    sys.exit(0)
cand = list(diff)
k = 0
while len(cand) > 1:
    half = cand[:len(cand) // 2]
    k += 1
    st = solve(build(half, f'trial{k}'))
    print(f'trial {k}: blocks {half} from the infeasible file -> {st}', flush=True)
    if st != 'OPTIMAL':
        cand = half
    else:
        cand = cand[len(cand) // 2:]
print('binding block:', cand, flush=True)
