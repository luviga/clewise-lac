"""Steps 2 and 3. For each main A-O workbook: open with data_only=False and data_only=True, list every
formula cell with sheet, cell, Tech, Parameter, Projection.Mode, column header (year), formula text and
stored value. Then evaluate each formula with a small evaluator limited to numbers, + - * / ^ %, parentheses
and same-sheet cell references (recursively). Anything else is 'not evaluated' with a reason.
Writes formula_cells.csv. Read-only on the workbooks."""
import os, re, csv, sys
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.dirname(os.path.abspath(__file__))
ENERGY = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
          "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
          "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
TOK = re.compile(r"\s*(?:(?P<ref>\$?[A-Za-z]{1,3}\$?\d+)(?![\w(!:])|(?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|(?P<op>[-+*/^()%]))")

class NotEval(Exception): pass

def evaluate(sheet, coord, F, V, stack):
    """F: {(sheet,coord): formula}, V: {(sheet,coord): value} (non-formula values)."""
    key = (sheet, coord)
    if key in stack: raise NotEval("circular reference")
    if key not in F:
        v = V.get(key)
        if v is None: return 0.0                     # Excel treats an empty cell as 0
        if isinstance(v, bool): return float(v)
        if isinstance(v, (int, float)): return float(v)
        raise NotEval(f"reference to text cell {coord}={v!r}")
    f = str(F[key])
    body = f[1:] if f.startswith("=") else f
    if "!" in body: raise NotEval("reference to another sheet")
    if re.search(r"[A-Za-z_][A-Za-z0-9_.]*\(", body): raise NotEval("uses a function")
    if ":" in body: raise NotEval("uses a range")
    if '"' in body: raise NotEval("uses a text literal")
    single = re.fullmatch(r"\s*\+?\s*(\$?[A-Za-z]{1,3}\$?\d+)\s*", body)
    if single:                                       # a pure reference may carry text (e.g. a tech name)
        c = single.group(1).replace("$", "").upper(); k2 = (sheet, c)
        if k2 not in F and isinstance(V.get(k2), str): return V[k2]
        if k2 in F: return evaluate(sheet, c, F, V, stack | {key})
    pos, expr = 0, []
    while pos < len(body):
        if body[pos:].strip() == "": break
        m = TOK.match(body, pos)
        if not m or m.end() == pos: raise NotEval(f"unsupported token at {body[pos:pos+10]!r}")
        pos = m.end()
        if m.group("ref"):
            c = m.group("ref").replace("$", "").upper()
            expr.append(repr(evaluate(sheet, c, F, V, stack | {key})))
        elif m.group("num"): expr.append(m.group("num"))
        else:
            o = m.group("op"); expr.append({"^": "**", "%": "/100"}.get(o, o))
    try:
        return float(eval("".join(expr), {"__builtins__": {}}, {}))
    except ZeroDivisionError: raise NotEval("division by zero (#DIV/0!)")
    except Exception as e: raise NotEval(f"expression error {e}")

rows = []
for c, d in ENERGY.items():
    p = os.path.join(ROOT, d, "A1_Outputs", "A-O_Parametrization.xlsx")
    wf = load_workbook(p, data_only=False, read_only=True); wv = load_workbook(p, data_only=True, read_only=True)
    F, V, meta = {}, {}, []
    for ws in wf.worksheets:
        sv = {}
        for r in wv[ws.title].iter_rows():
            for cell in r:
                if cell.value is not None and hasattr(cell, "coordinate"): sv[cell.coordinate] = cell.value
        hdr, rowinfo = {}, {}
        for r in ws.iter_rows():
            for cell in r:
                if not hasattr(cell, "coordinate") or cell.value is None: continue
                k = (ws.title, cell.coordinate)
                if cell.row == 1: hdr[cell.column] = cell.value
                if cell.data_type == "f": F[k] = cell.value; meta.append((ws.title, cell.coordinate, cell.row, cell.column, sv.get(cell.coordinate)))
                else: V[k] = cell.value
        cols = {str(v).strip(): k for k, v in hdr.items()}
        def rv(row, name):
            k = cols.get(name)
            if k is None: return None
            from openpyxl.utils import get_column_letter
            key = (ws.title, f"{get_column_letter(k)}{row}")
            return V.get(key, F.get(key))
        for (sh, coord, row, col, stored) in [m for m in meta if m[0] == ws.title]:
            h = hdr.get(col)
            year = int(h) if isinstance(h, (int, float)) or (isinstance(h, str) and h.strip().isdigit()) else ""
            own, reason = "", ""
            try:
                own = evaluate(sh, coord, F, V, frozenset())
            except NotEval as e:
                reason = str(e)
            if own != "": val, method = own, "own evaluator (numbers, + - * / ^, same-sheet refs)"
            elif stored is not None: val, method = stored, "stored value (own evaluator could not evaluate)"
            else: val, method = "", "not evaluated"
            if own != "" and stored is not None:
                try: agree = abs(float(own) - float(stored)) <= 1e-9 * max(1.0, abs(float(stored)))
                except (TypeError, ValueError): agree = str(own) == str(stored)
            else: agree = ""
            rows.append({"country": c, "sheet": sh, "cell": coord, "row": row, "column_header": h, "year": year,
                         "tech": rv(row, "Tech"), "parameter": rv(row, "Parameter"), "projection_mode": rv(row, "Projection.Mode"),
                         "formula": F[(sh, coord)], "stored_value": "" if stored is None else stored,
                         "has_stored_value": stored is not None, "own_eval_value": own, "own_eval_equals_stored": agree, "intended_value": val, "intended_method": method,
                         "not_evaluated_reason": reason})
    print(c, "formula cells:", sum(1 for r in rows if r["country"] == c), flush=True)
keys = list(rows[0].keys())
with open(os.path.join(OUT, "formula_cells.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
