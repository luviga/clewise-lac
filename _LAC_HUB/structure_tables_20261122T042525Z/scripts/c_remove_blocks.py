"""Phase C: remove code branches that test a retired scenario name.

For each (file, header text) of the spec, every `if` statement whose header line holds the text is removed
with its body. An `if` with an `else` (and no `elif`) is replaced by the body of its `else`, dedented, because
the tested scenario never runs; an `if` with an `elif` is reported and left for a hand edit.
Works on the AST for the statement extent and on the text for the edit, keeping line endings.

Usage: py -I c_remove_blocks.py <spec.py>   spec defines BLOCKS = [(repo file, header text), ...]
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast
import runpy
import sys
from pathlib import Path

ROOT = M.ROOT
spec = runpy.run_path(sys.argv[1])
total = 0
for f, text in spec['BLOCKS']:
    p = ROOT / f
    raw = p.read_bytes().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    removed = 0
    while True:
        lines = raw.split(nl)
        tree = ast.parse(raw)
        target = None
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and text in lines[node.lineno - 1]:
                target = node
                break
        if target is None:
            break
        orelse = target.orelse
        if orelse and len(orelse) == 1 and isinstance(orelse[0], ast.If) and \
                lines[orelse[0].lineno - 1].lstrip().startswith('elif'):
            print(f'LEFT {f}:{target.lineno}: if with elif, hand edit needed')
            break
        start, end = target.lineno - 1, target.end_lineno
        if orelse:
            ind_if = len(lines[start]) - len(lines[start].lstrip())
            body_start = orelse[0].lineno - 1
            body = lines[body_start:end]
            ind_body = len(lines[body_start]) - len(lines[body_start].lstrip())
            shift = ind_body - ind_if
            new = [ln[shift:] if ln[:shift].strip() == '' else ln for ln in body]
            lines[start:end] = new
        else:
            lines[start:end] = []
        raw = nl.join(lines)
        removed += 1
    ast.parse(raw)
    p.write_bytes(raw.encode('utf-8'))
    print(f'{f}: {removed} branch(es) removed for {text!r}')
    total += removed
print('total', total)
