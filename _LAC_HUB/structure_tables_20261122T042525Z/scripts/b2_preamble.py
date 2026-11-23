"""Insert the loader preamble into draft model-folder scripts (A2 compilers, B1 runners), before the first
statement after the module docstring. The preamble finds lac_tables.py by walking up from the script's folder,
imports it as LT, and reads the script's stage numbers into a _T alias (general section plus the country's
section of the stage YAML).

Usage: py -I b2_preamble.py <compilation|execution> <alias> <file> [...]
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast
import sys
from pathlib import Path

JOB = M.JOB
stage, alias = sys.argv[1], sys.argv[2]
PRE = [
    "# Values and names of this script come from the tables read by lac_tables.py (repository root).",
    "import sys as _LTsys",
    "from pathlib import Path as _LTPath",
    "_LTsys.path.insert(0, str(next(p for p in _LTPath(__file__).resolve().parents if (p / 'lac_tables.py').exists())))",
    "import lac_tables as LT",
    "_TC = LT.country_of(__file__)",
    f"{alias} = LT.stage_values('{stage}', _TC)",
    "",
]
if stage == 'compilation':
    PRE[5:7] = [f"{alias} = LT.stage_values('{stage}', LT.country_of(__file__))"]
for f in sys.argv[3:]:
    p = JOB / 'draft' / f
    raw = p.read_bytes().decode('utf-8')
    if 'import lac_tables as LT' in raw:
        print('already', f)
        continue
    nl = '\r\n' if '\r\n' in raw else '\n'
    tree = ast.parse(raw)
    body = tree.body
    first = body[1] if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)) else body[0]
    lines = raw.split(nl)
    at = first.lineno - 1
    lines[at:at] = PRE
    p.write_bytes(nl.join(lines).encode('utf-8'))
    print('inserted', f, 'before line', first.lineno)
