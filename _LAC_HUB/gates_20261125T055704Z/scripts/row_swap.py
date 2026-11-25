"""Copy chosen rows (technology names) of chosen two-index blocks from an infeasible data file into a feasible one
and solve: python -I row_swap.py <model> <good> <bad> <out> <blocks,comma> <techs,comma> [--whole block,...]"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import subprocess
import sys

sys.path.insert(0, str(M.ROOT))
import scenario_rules as SR  # noqa: E402

model, good, bad, out, blks, techs = sys.argv[1:7]
whole = sys.argv[sys.argv.index('--whole') + 1].split(',') if '--whole' in sys.argv else []
g = open(good, encoding='utf-8').read().replace('\r\n', '\n')
b = open(bad, encoding='utf-8').read().replace('\r\n', '\n')
yrs, reg = SR.years_of(g), SR.region_of(g)
for p in blks.split(','):
    bb = SR.blocks(b)
    rows = {}
    for sl, ys, rw in SR.parse_block(b[bb[p][0]:bb[p][1]]):
        for k, v in rw.items():
            if k in techs.split(','):
                rows[k] = {y: float(x) for y, x in zip(ys, v)}
    g, n = SR.set_rows(g, p, rows, yrs, reg)
    print(p, n, 'values copied')
for p in whole:
    gb, bb = SR.blocks(g), SR.blocks(b)
    g = g[:gb[p][0]] + b[bb[p][0]:bb[p][1]] + g[gb[p][1]:]
    print(p, 'whole block copied')
open(out, 'w', encoding='utf-8').write(g)
o = out.replace('.txt', '_out.txt')
subprocess.run([M.GLPSOL, '-m', model, '-d', out, '-o', o], capture_output=True, timeout=1800)
with open(o, encoding='utf-8', errors='replace') as fh:
    st = next((l.split(':', 1)[1].strip() for l in fh if l.startswith('Status:')), 'NO STATUS')
print('status:', st)
