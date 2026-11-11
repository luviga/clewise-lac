"""Extract searchable text from downloaded source files (cached under scratch/text) and search for numbers.

Each cached text has location markers: '@@ page N' for PDFs, '@@ sheet NAME' for workbooks
(each cell line is 'A1<TAB>value'), and plain lines otherwise (location = line number).
"""
import hashlib
import html
import json
import re
import zipfile
from array import array

from common import *  # noqa

TEXTDIR = os.path.join(SCRATCH, "text")
NOTSEARCHABLE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".pack", ".idx", ".rev", ".promisor"}


def _cache_path(cc, path):
    h = hashlib.md5(path.encode("utf-8")).hexdigest()[:12]
    return os.path.join(TEXTDIR, cc, h + "_" + re.sub(r"[^\w.-]", "_", os.path.basename(path))[:60] + ".txt")


def _pdf(path):
    import fitz
    out = []
    doc = fitz.open(path)
    chars = 0
    for i, pg in enumerate(doc, 1):
        t = pg.get_text()
        chars += len(t.strip())
        out.append(f"@@ page {i}\n{t}")
    status = "ok" if chars > 50 * max(1, len(doc)) / 10 else "no text layer"
    return "\n".join(out), status, len(doc)


def _xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        out.append(f"@@ sheet {ws.title}")
        for row in ws.iter_rows():
            for c in row:
                v = getattr(c, "value", None)
                if v is not None and v != "":
                    out.append(f"{c.coordinate}\t{v!r}" if isinstance(v, float) else f"{c.coordinate}\t{v}")
    return "\n".join(out), "ok", None


def _xls(path):
    raw = open(path, "rb").read(2048)
    if raw.lstrip()[:1] == b"<":
        return _htmlish(path)
    import xlrd
    wb = xlrd.open_workbook(path)
    out = []
    for sh in wb.sheets():
        out.append(f"@@ sheet {sh.name}")
        for r in range(sh.nrows):
            for c in range(sh.ncols):
                v = sh.cell_value(r, c)
                if v not in ("", None):
                    out.append(f"{xlrd.formula.cellname(r, c)}\t{v!r}" if isinstance(v, float) else f"{xlrd.formula.cellname(r, c)}\t{v}")
    return "\n".join(out), "ok", None


def _htmlish(path):
    t = open(path, "rb").read().decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|tr|div|li|h\d)>", "\n", t)
    t = re.sub(r"(?i)</t[dh]>", "\t", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t), "ok", None


def _docx(path):
    with zipfile.ZipFile(path) as z:
        x = z.read("word/document.xml").decode("utf-8", "replace")
    x = re.sub(r"</w:p>", "\n", x)
    x = re.sub(r"</w:tc>", "\t", x)
    return html.unescape(re.sub(r"<[^>]+>", "", x)), "ok", None


def _parquet(path):
    df = pd.read_parquet(path)
    return df.to_csv(index=False), "ok", None


def extract(cc, path):
    """Return (text, status). status: ok | not searchable: reason."""
    cp = _cache_path(cc, path)
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as f:
            first = f.readline().rstrip("\n")
            return f.read(), first
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in NOTSEARCHABLE:
            text, status = "", f"not searchable: {ext} file (image or archive)"
        elif ext == ".pdf":
            text, status, n = _pdf(path)
            if status != "ok":
                status = f"not searchable: PDF has no text layer ({n} pages, scanned)"
        elif ext in (".xlsx", ".xlsm"):
            text, status, _ = _xlsx(path)
        elif ext == ".xls":
            text, status, _ = _xls(path)
        elif ext in (".html", ".htm", ".xml"):
            text, status, _ = _htmlish(path)
        elif ext == ".docx":
            text, status, _ = _docx(path)
        elif ext == ".parquet":
            text, status, _ = _parquet(path)
        else:
            text, status = open(path, "rb").read().decode("utf-8", "replace"), "ok"
            if ext == ".json":
                try:
                    text = json.dumps(json.loads(text), indent=0, ensure_ascii=False)
                except Exception:
                    pass
    except Exception as e:  # noqa
        text, status = "", f"not searchable: extraction error {type(e).__name__}: {str(e)[:120]}"
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    with open(cp, "w", encoding="utf-8") as f:
        f.write(status + "\n" + text)
    return text, status


def _decimals(s):
    return len(s.split(".")[1]) if "." in s else 0


def number_regex(s):
    """Regex that finds a printed number whose leading digits match s, in English or Spanish notation."""
    s = s.replace(",", "")
    neg = s.startswith("-")
    s = s.lstrip("-")
    ip, _, dp = s.partition(".")
    ip = ip.lstrip("0") or "0"
    # integer part with optional thousand separators
    groups = []
    while len(ip) > 3:
        groups.insert(0, ip[-3:])
        ip = ip[:-3]
    groups.insert(0, ip)
    sep = r"[,.   ]?"
    ipat = sep.join(groups)
    pat = r"(?<![\d.,])" + ("-?" if neg else "") + ipat + r"(?:[.,]\d+)?(?![\d])"
    return re.compile(pat)


def _parse_variants(tok):
    vals = set()
    t = tok.replace(" ", "").replace(" ", "").replace(" ", "")
    for cand in (t.replace(",", ""), t.replace(".", "").replace(",", ".")):
        try:
            vals.add(float(cand))
        except ValueError:
            pass
    if t.count(",") == 1 and "." not in t:
        try:
            vals.add(float(t.replace(",", ".")))
        except ValueError:
            pass
    return vals


def matches(tok, target_str):
    t = float(target_str.replace(",", ""))
    d = _decimals(target_str.replace(",", ""))
    tol = 0.5 * 10 ** (-d) + 1e-9
    for v in _parse_variants(tok):
        if abs(v - t) <= tol or abs(abs(v) - abs(t)) <= tol:
            return True
    return False


TOKEN = re.compile(r"(?<![\d.,])-?\d[\d,.]*\d(?![\d])|(?<![\d.,])-?\d(?![\d])")
TOKEN_SP = re.compile(r"(?<![\d.,])\d{1,3}(?:[   ]\d{3})+(?:[.,]\d+)?(?![\d])")
TOKEN_PLAIN = re.compile(r"(?<![\d.])-?\d+(?:\.\d+)?(?![\d.])")  # plain decimals, also after a CSV comma
_IDX = {}


def _index(text):
    """One pass over the text: integer part -> list of (value, position) for every printed number."""
    key = id(text)
    if key in _IDX and _IDX[key][0] is text:
        return _IDX[key][1], _IDX[key][2]
    idx = {}
    for rx in (TOKEN, TOKEN_SP, TOKEN_PLAIN):
        for m in rx.finditer(text):
            tok = m.group(0)
            if len(tok) > 30:
                continue
            for v in _parse_variants(tok):
                if v != v or abs(v) > 1e15:
                    continue
                k = int(abs(v))
                a = idx.get(k)
                if a is None:
                    a = idx[k] = (array("d"), array("q"))
                a[0].append(abs(v))
                a[1].append(m.start())
    marks = [(m.start(), m.group(1), m.group(2)) for m in re.finditer(r"@@ (page|sheet) ([^\n]+)", text)]
    _IDX[key] = (text, idx, marks)
    return idx, marks


def locate(text, pos, marks=None):
    """Location label for a character position in cached text."""
    import bisect
    if marks is None:
        _, marks = _index(text)
    i = bisect.bisect_right([m[0] for m in marks], pos) - 1 if marks else -1
    ls = text.rfind("\n", 0, pos) + 1
    le = text.find("\n", pos)
    line = text[ls:le if le >= 0 else None]
    if i >= 0 and marks[i][1] == "page":
        return f"page {marks[i][2]}"
    if i >= 0 and marks[i][1] == "sheet":
        cell = line.split("\t")[0] if "\t" in line else "?"
        return f"sheet {marks[i][2]} cell {cell}"
    return f"line {text.count(chr(10), 0, pos) + 1}"


def search(text, target_str, limit=3):
    """Return list of location labels where the number appears (rounded to the target's decimals)."""
    idx, marks = _index(text)
    ts = target_str.replace(",", "")
    t = abs(float(ts))
    d = _decimals(ts)
    tol = 0.5 * 10 ** (-d) + 1e-9
    out = []
    for k in {int(t), int(t - tol) if t - tol >= 0 else 0, int(t + tol)}:
        vs, ps = idx.get(k, ((), ()))
        for v, pos in zip(vs, ps):
            if abs(v - t) <= tol:
                loc = locate(text, pos, marks)
                if loc not in out:
                    out.append(loc)
                if len(out) >= limit:
                    return out
    return out
