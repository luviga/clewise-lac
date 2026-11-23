"""Gate tool of Phase B: prove that an edited Python script holds exactly the values of the untouched one.

For each file: parse the file at the base commit (old) and the working file (new). In the new tree, every read
through the loader (a call LT.<function>(...) with constant arguments, a subscript chain on such a call, or a
module-level alias whose name starts with _T and whose value is such a read) is evaluated with the tables of the
working tree and replaced by the literal it returns. The loader preamble (statements that use names starting
with _LT or import lac_tables) and the _T alias assignments are dropped. Both trees are then normalised (string
concatenations and f-strings made only of constants are joined) and compared with ast.dump.

Equal trees mean the edited script computes with the same literals as before. The script also writes one
register row per literal of the old tree that a loader read replaced (old line, value, loader expression).

Usage: py -I b2_fold_check.py <repo-relative file> [...]   (base commit b51f24b)
A draft copy at work/../draft/<file> is read instead of the working file when it exists (drafts are made while
a pipeline run uses the working files).
Writes work/fold/<file with / replaced by __>.csv and prints OK or the first differences.
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import ast
import csv
import difflib
import importlib.util
import os
import subprocess
import sys

ROOT = M.ROOT_S
JOB = ROOT + '/_LAC_HUB/structure_tables_20261122T042525Z'
BASE = 'b51f24b'
OUT = JOB + '/work/fold'

spec = importlib.util.spec_from_file_location('lac_tables', ROOT + '/lac_tables.py')
LT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LT)


def old_source(rel):
    return subprocess.run(['git', '-C', ROOT, 'show', f'{BASE}:{rel}'], capture_output=True, check=True).stdout.decode(
        'utf-8', errors='replace')


def uses_lt_private(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id.startswith('_LT'):
            return True
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in n.names] + ([n.module] if isinstance(n, ast.ImportFrom) and n.module else [])
            if any(x == 'lac_tables' for x in names):
                return True
            if any((a.asname or '').startswith('_LT') for a in n.names):
                return True
    return False


class Folder:
    def __init__(self, path):
        self.env = {'LT': LT, '__file__': path}
        self.aliases = {}
        self.marks = {}

    def is_root(self, n):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) \
                and n.func.value.id == 'LT':
            return all(self.is_static(a) for a in n.args) and all(self.is_static(k.value) for k in n.keywords)
        if isinstance(n, ast.Name) and n.id in self.aliases:
            return True
        if isinstance(n, ast.Subscript):
            return self.is_root(n.value) and self.is_static(n.slice)
        return False

    def is_static(self, n):
        if isinstance(n, ast.Constant):
            return True
        if isinstance(n, ast.Name) and n.id == '__file__':
            return True
        if isinstance(n, (ast.Tuple, ast.List)):
            return all(self.is_static(e) for e in n.elts)
        if isinstance(n, ast.UnaryOp) and isinstance(n.operand, ast.Constant):
            return True
        return self.is_root(n)

    def value(self, n):
        env = dict(self.env)
        env.update(self.aliases)
        return eval(compile(ast.Expression(body=n), '<fold>', 'eval'), env)

    def literal(self, v, src):
        node = ast.parse(repr(v), mode='eval').body
        self.marks[id(node)] = src
        return node

    def fold(self, node):
        if isinstance(node, ast.expr) and self.is_root(node):
            return self.literal(self.value(node), ast.unparse(node))
        for field, val in ast.iter_fields(node):
            if isinstance(val, list):
                new = []
                for v in val:
                    if isinstance(v, ast.AST):
                        new.append(self.fold(v))
                    else:
                        new.append(v)
                setattr(node, field, new)
            elif isinstance(val, ast.AST):
                setattr(node, field, self.fold(val))
        return node


class Norm(ast.NodeTransformer):
    """Joins constant strings; writes a set literal as set([...]) and a tuple of constants as tuple([...]), so that
    set(LT.techs(...)) and tuple(LT.techs(...)) compare equal to the literal they replace (same order).
    A joined constant keeps the register marks of the loader reads it was built from."""

    def __init__(self, marks=None):
        self.marks = marks if marks is not None else {}

    def _mark(self, node, parts):
        found = [self.marks[id(p)] for p in parts if p is not None and id(p) in self.marks]
        if found:
            self.marks[id(node)] = ' + '.join(found)
        return node

    def visit_List(self, node):
        self.generic_visit(node)
        elts = []
        for e in node.elts:
            if isinstance(e, ast.Starred) and isinstance(e.value, (ast.List, ast.Tuple)):
                elts.extend(e.value.elts)
            else:
                elts.append(e)
        node.elts = elts
        return node

    def visit_Set(self, node):
        self.generic_visit(node)
        return ast.copy_location(ast.Call(func=ast.Name(id='set', ctx=ast.Load()),
                                          args=[ast.List(elts=node.elts, ctx=ast.Load())], keywords=[]), node)

    def visit_Tuple(self, node):
        self.generic_visit(node)
        if isinstance(node.ctx, ast.Load) and node.elts and all(isinstance(e, ast.Constant) for e in node.elts):
            return ast.copy_location(ast.Call(func=ast.Name(id='tuple', ctx=ast.Load()),
                                              args=[ast.List(elts=node.elts, ctx=ast.Load())], keywords=[]), node)
        return node

    def visit_JoinedStr(self, node):
        self.generic_visit(node)
        values, buf, parts = [], None, []
        for v in node.values:
            text = None
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                text = v.value
            elif isinstance(v, ast.FormattedValue) and v.conversion == -1 and v.format_spec is None \
                    and isinstance(v.value, ast.Constant) and isinstance(v.value.value, (str, int)):
                text = str(v.value.value)
            if text is None:
                if buf is not None:
                    values.append(self._mark(ast.Constant(buf), parts))
                    buf, parts = None, []
                values.append(v)
            else:
                buf = text if buf is None else buf + text
                parts += [v, getattr(v, 'value', None)]
        if buf is not None:
            values.append(self._mark(ast.Constant(buf), parts))
        if len(values) == 1 and isinstance(values[0], ast.Constant):
            return ast.copy_location(values[0], node)
        node.values = values
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add) and isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant) \
                and isinstance(node.left.value, str) and isinstance(node.right.value, str):
            return self._mark(ast.copy_location(ast.Constant(node.left.value + node.right.value), node),
                              [node.left, node.right])
        return node


def prepare_new(src, path):
    tree = ast.parse(src)
    f = Folder(path)
    body = []
    for st in tree.body:
        if uses_lt_private(st):
            continue
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) \
                and st.targets[0].id.startswith('_T'):
            if not f.is_root(st.value):
                raise SystemExit(f'alias {st.targets[0].id} is not a loader read: {ast.unparse(st.value)}')
            f.aliases[st.targets[0].id] = f.value(st.value)
            continue
        body.append(st)
    tree.body = body
    tree = f.fold(tree)
    tree = Norm(f.marks).visit(tree)
    return tree, f.marks


def parallel(o, n, marks, rows):
    if id(n) in marks:
        for c in ast.walk(o):
            if isinstance(c, ast.Constant) and not isinstance(c.value, bool) and c.value is not None:
                rows.append({'old_line': getattr(c, 'lineno', getattr(o, 'lineno', '')), 'value': c.value,
                             'loader_read': marks[id(n)]})
        return
    if type(o) is not type(n):
        return
    for (fo, vo), (fn, vn) in zip(ast.iter_fields(o), ast.iter_fields(n)):
        if isinstance(vo, list) and isinstance(vn, list):
            for a, b in zip(vo, vn):
                if isinstance(a, ast.AST) and isinstance(b, ast.AST):
                    parallel(a, b, marks, rows)
        elif isinstance(vo, ast.AST) and isinstance(vn, ast.AST):
            parallel(vo, vn, marks, rows)


def check(rel):
    path = os.path.abspath(os.path.join(ROOT, rel))
    old = Norm().visit(ast.parse(old_source(rel)))
    draft = os.path.join(JOB, 'draft', rel)
    new_src = open(draft if os.path.exists(draft) else path, encoding='utf-8').read()
    new, marks = prepare_new(new_src, path)
    do, dn = ast.dump(old), ast.dump(new)
    rows = []
    if do == dn:
        parallel(old, new, marks, rows)
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, rel.replace('/', '__') + '.csv'), 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['old_line', 'value', 'loader_read'], lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
        print(f'OK {rel}: {len(marks)} loader reads, {len(rows)} literals replaced')
        return True
    ob = [ast.dump(s) for s in old.body]
    nb = [ast.dump(s) for s in new.body]
    print(f'DIFFER {rel}')
    sm = difflib.SequenceMatcher(a=ob, b=nb, autojunk=False)
    shown = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        for st in old.body[i1:i2][:2]:
            print(f'  old line {st.lineno}: {ast.unparse(st)[:300]}')
        for st in new.body[j1:j2][:2]:
            print(f'  new (folded): {ast.unparse(st)[:300]}')
        # descend into differing statement pairs to show the innermost difference
        for a, b in zip(old.body[i1:i2], new.body[j1:j2]):
            if ast.dump(a) != ast.dump(b):
                inner(a, b)
        shown += 1
        if shown >= 4:
            break
    return False


def inner(o, n, depth=0):
    """Print the deepest differing statement inside two differing compound statements."""
    for fo, fn in zip(ast.iter_fields(o), ast.iter_fields(n)):
        vo, vn = fo[1], fn[1]
        if isinstance(vo, list) and isinstance(vn, list) and vo and isinstance(vo[0], ast.stmt):
            for a, b in zip(vo, vn):
                if ast.dump(a) != ast.dump(b):
                    nested = type(a) is type(b) and any(isinstance(x[1], list) and x[1] and isinstance(x[1][0], ast.stmt)
                                                        for x in ast.iter_fields(a))
                    if depth < 12 and nested:
                        inner(a, b, depth + 1)
                    else:
                        print(f'    old line {a.lineno}: {ast.unparse(a)[:400]}')
                        print(f'    new (folded):  {ast.unparse(b)[:400]}')
                    return
            if len(vo) != len(vn):
                print(f'    statement count differs: {len(vo)} against {len(vn)}')
                return


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ok = all([check(f) for f in sys.argv[1:]])
    sys.exit(0 if ok else 1)
