"""Shared helpers for LAC_NDC_VERIFY scripts. Run with /c/clw_scout_venv/Scripts/python.exe -I."""
import csv
import hashlib
import os
import re

JOB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOUT = os.path.join(os.path.dirname(JOB), "ndc_scout_20261121T204620Z")
MODEL = "C:/clw_scout_model"
CODES = ["CR", "DR", "ECU", "GUA", "HON", "JAM"]
COUNTRY = {"CR": "Costa Rica", "DR": "Dominican Republic", "ECU": "Ecuador",
           "GUA": "Guatemala", "HON": "Honduras", "JAM": "Jamaica"}
CODE_OF = {v: k for k, v in COUNTRY.items()}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def pages_of(s):
    out = []
    for part in re.split(r"[;,]", str(s)):
        part = part.strip()
        m = re.match(r"^p\.?\s*(\d+)\s*(?:-\s*(\d+))?$", part)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            out.extend(range(a, b + 1))
    return out


def variants(v):
    """String forms a number may take in Spanish or English documents."""
    try:
        x = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return []
    forms = set()
    for dec in range(0, 8):
        r = round(x, dec)
        if abs(r - x) > 1e-9 * max(1.0, abs(x)):
            continue
        s = f"{r:.{dec}f}"
        intpart, _, frac = s.partition(".")
        neg = intpart.startswith("-")
        ip = intpart.lstrip("-")
        groups = []
        while len(ip) > 3:
            groups.insert(0, ip[-3:])
            ip = ip[:-3]
        groups.insert(0, ip)
        for tsep in ["", ",", ".", " ", "\u00a0", "'"]:
            for dsep in [".", ","]:
                if tsep == dsep:
                    continue
                body = tsep.join(groups)
                forms.add(("-" if neg else "") + body + (dsep + frac if frac else ""))
    return sorted(forms, key=len, reverse=True)


def find_all(text, forms):
    """Return list of (form, line) where a form appears as a whole number."""
    t = text.replace("\u2212", "-")
    hits = []
    for line in t.splitlines():
        for f in forms:
            pat = r"(?<![\d.,])" + re.escape(f) + r"(?![\d]|[.,]\d)"
            if re.search(pat, line):
                hits.append((f, line))
                break
    return hits


def text_path(code, sid, n):
    return os.path.join(JOB, "downloads", code, "text_all", sid, f"p{n}.txt")


def page_text(code, sid, n):
    p = text_path(code, sid, n)
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    p2 = os.path.join(SCOUT, "downloads", code, "text", sid, f"p{n}.txt")
    if os.path.exists(p2):
        with open(p2, encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""
