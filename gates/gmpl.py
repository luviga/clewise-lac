"""Reader of the GMPL files the solver reads.

model_dims(model_file)  index sets of every parameter, from the `param NAME{x in SET, ...}` lines of
                        OSeMOSYS_Model.txt (the structure of the model, never a value).
read_data(data_file)    sets, and for every parameter its declared default, its explicit values keyed by index
                        tuple, duplicate keys and repeated blocks, as glpsol would read them.

Supported data forms (the forms the A2 and B1 scripts and stage3_apply.py write): plain lists of index values and
a value, slices `[a,*,b,*]`, tables `: c1 c2 ... :=` with rows, and both combined. `.` in a table is a missing
value (the default applies).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_TOKEN = re.compile(r"\[[^\]]*\]|:=|:|;|[^\s:;\[\]]+")
_PARAM = re.compile(r"param\s+(\w+)\s*\{([^}]*)\}", re.S)


def model_dims(model_file: str) -> dict:
    """{parameter: [set name, ...]} from the model file."""
    text = open(model_file, encoding="utf-8", errors="replace").read()
    text = re.sub(r"#[^\n]*", "", text)
    dims = {}
    for name, body in _PARAM.findall(text):
        sets = re.findall(r"\b\w+\s+in\s+(\w+)", body)
        dims[name] = sets
    return dims


@dataclass
class Param:
    name: str
    default: float | None = None
    values: dict = field(default_factory=dict)
    duplicates: list = field(default_factory=list)
    blocks: int = 0

    def get(self, key, fallback=None):
        v = self.values.get(key)
        if v is not None:
            return v
        return self.default if self.default is not None else fallback


@dataclass
class Data:
    path: str
    sets: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    dims: dict = field(default_factory=dict)
    problems: list = field(default_factory=list)

    def p(self, name) -> Param:
        if name not in self.params:
            self.params[name] = Param(name)
        return self.params[name]


def _num(tok: str):
    try:
        return float(tok)
    except ValueError:
        return tok


def _statements(text: str):
    """Statements of a data section, split on ';' outside comments, with comments removed."""
    text = re.sub(r"#[^\n]*", "", text)
    start = text.find("data;")
    if start >= 0:
        text = text[start + 5:]
    for st in text.split(";"):
        st = st.strip()
        if st:
            yield st


def _parse_param(name, toks, nd, par: Param, problems):
    """Fill par.values from the tokens after the parameter name; nd = number of index positions."""
    i = 0
    if i < len(toks) and toks[i] == "default":
        par.default = float(toks[i + 1])
        i += 2
    if i < len(toks) and toks[i] == ":=":
        i += 1
    slice_ = [None] * nd

    def put(key, val):
        if val == ".":
            return
        try:
            v = float(val)
        except ValueError:
            problems.append(("S5", name, key, f"value {val!r} is not a number"))
            return
        if key in par.values:
            par.duplicates.append((key, par.values[key], v))
        par.values[key] = v

    n = len(toks)
    while i < n:
        t = toks[i]
        if t.startswith("["):
            parts = [x.strip() for x in t[1:-1].split(",")]
            if len(parts) != nd:
                problems.append(("S5", name, tuple(parts), f"slice of {len(parts)} positions for {nd} indices"))
                return
            slice_ = [None if x == "*" else x for x in parts]
            i += 1
            if i < n and toks[i] == ":=":
                i += 1
            continue
        free = [k for k, x in enumerate(slice_) if x is None]
        if t == ":":
            # table: column labels up to ':=', then rows of one row label and one value per column
            i += 1
            cols = []
            while i < n and toks[i] != ":=":
                cols.append(toks[i])
                i += 1
            i += 1
            if len(free) != 2:
                problems.append(("S5", name, tuple(slice_), f"table needs 2 free positions, has {len(free)}"))
                return
            while i < n and not toks[i].startswith("[") and toks[i] != ":":
                row = toks[i]
                vals = toks[i + 1:i + 1 + len(cols)]
                i += 1 + len(cols)
                for c, v in zip(cols, vals):
                    key = list(slice_)
                    key[free[0]], key[free[1]] = row, c
                    put(tuple(key), v)
            continue
        # plain list: one index value per free position, then the value
        k = len(free)
        chunk = toks[i:i + k + 1]
        if len(chunk) < k + 1:
            problems.append(("S5", name, tuple(chunk), "incomplete record"))
            return
        key = list(slice_)
        for pos, v in zip(free, chunk[:k]):
            key[pos] = v
        put(tuple(key), chunk[k])
        i += k + 1


def read_data(data_file: str, dims: dict) -> Data:
    text = open(data_file, encoding="utf-8", errors="replace").read()
    d = Data(path=data_file, dims=dims)
    for st in _statements(text):
        toks = _TOKEN.findall(st)
        if not toks:
            continue
        if toks[0] == "set":
            name = toks[1]
            members = [x for x in toks[2:] if x != ":="]
            if name in d.sets:
                d.problems.append(("S5", name, (), "set given twice"))
            if len(set(members)) != len(members):
                d.problems.append(("S5", name, (), "set lists a member twice"))
            d.sets[name] = members
        elif toks[0] == "param":
            name = toks[1]
            if name not in dims:
                d.problems.append(("S5", name, (), "parameter not declared in the model file"))
                continue
            par = d.p(name)
            par.blocks += 1
            before = dict(par.values)
            _parse_param(name, toks[2:], len(dims[name]), par, d.problems)
            if par.blocks > 1 and before:
                d.problems.append(("S5", name, (), f"parameter block given {par.blocks} times"))
        elif toks[0] == "end":
            break
    # elements missing from their sets
    setidx = {k: set(v) for k, v in d.sets.items()}
    for name, par in d.params.items():
        sets = dims.get(name, [])
        for key in par.values:
            for pos, s in enumerate(sets):
                if s in setidx and key[pos] not in setidx[s]:
                    d.problems.append(("S5", name, key, f"{key[pos]} is not a member of {s}"))
                    break
        for key, old, new in par.duplicates:
            d.problems.append(("S5", name, key, f"key given twice ({old} then {new})"))
    return d
