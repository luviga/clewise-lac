"""Read Honduras values from CCHAC-SICA weekly fuel price bulletins (2024, hosted by SEN).

Usage: py -I parse_cchac.py <dir_with_pdfs> <out_csv>

For the charts "Precios e Impuesto de las Gasolinas" and "... del Diesel" the Honduras bar
carries three dollar labels stacked vertically: total (top), Impuestos, Precio sin Imp.
For the LPG table "Estructura de Precios del GLP en la Region" the Honduras column is read
row by row. Checks: total = tax + pre-tax within 0.02.
"""
import csv
import re
import sys
from pathlib import Path

import pdfplumber

NUMRE = re.compile(r"^\$?(\d+[.,]\d+)$")


def dollar_words(words):
    out = []
    for i, w in enumerate(words):
        m = NUMRE.match(w["text"])
        if not m:
            continue
        has_dollar = w["text"].startswith("$") or any(
            o["text"] == "$" and abs(o["top"] - w["top"]) < 3 and 0 <= w["x0"] - o["x1"] < 12
            for o in words)
        if has_dollar:
            out.append({"x": (w["x0"] + w["x1"]) / 2, "top": w["top"], "v": float(m.group(1).replace(",", "."))})
    return out


def bars(page, names):
    words = page.extract_words()
    hn = sorted([w for w in words if w["text"] == "HONDURAS"], key=lambda w: w["top"])
    dv = dollar_words(words)
    res = {}
    k = 0
    prev = 0
    for h in hn:
        cx = (h["x0"] + h["x1"]) / 2
        vals = sorted([d for d in dv if abs(d["x"] - cx) < 30 and prev < d["top"] < h["top"]],
                      key=lambda d: d["top"])
        if len(vals) >= 3 and k < len(names):
            total, tax, pre = vals[0]["v"], vals[1]["v"], vals[2]["v"]
            res[names[k]] = (pre, tax, total, abs(pre + tax - total) <= 0.021)
            k += 1
            prev = h["top"] + 5
    return res


def glp(page):
    words = page.extract_words()
    var = [w for w in words if w["text"] == "VARIABLES"]
    if not var:
        return {}
    vy = var[0]["top"]
    hn = [w for w in words if w["text"] == "HONDURAS"]
    if not hn:
        return {}
    h = min(hn, key=lambda w: abs(w["top"] - vy))
    x0, x1 = h["x0"] - 8, h["x1"] + 8
    dv = [d for d in dollar_words(words) if x0 <= d["x"] <= x1 and vy < d["top"] < vy + 300]
    lines = {}
    for w in words:
        if w["x1"] < 170 and vy < w["top"] < vy + 300 and not NUMRE.match(w["text"]) and w["text"] != "$":
            key = round(w["top"])
            near = [kk for kk in lines if abs(kk - key) <= 3]
            if near:
                lines[near[0]].append(w)
            else:
                lines[key] = [w]
    labels = {kk: " ".join(x["text"] for x in sorted(v, key=lambda x: x["x0"])) for kk, v in lines.items()}
    out = {}
    for d in dv:
        if not labels:
            break
        kk = min(labels, key=lambda q: abs(q - d["top"]))
        if abs(kk - d["top"]) <= 6:
            out.setdefault(labels[kk], []).append(d["v"])
    return out


def main():
    d = Path(sys.argv[1])
    rows = []
    for f in sorted(d.glob("*.pdf")):
        pdf = pdfplumber.open(f)
        first = " ".join((pdf.pages[0].extract_text() or "").split())
        m = re.search(r"Semana del (.*?20\d\d)", first)
        week = m.group(1) if m else ""
        for i, pg in enumerate(pdf.pages):
            t = " ".join((pg.extract_text() or "").split()).lower()
            if "precios e impuesto de las gasolinas" in t:
                for name, (pre, tax, tot, ok) in bars(pg, ["GSL_superior", "GSL_regular"]).items():
                    rows.append([f.name, week, i + 1, name, "pre_tax", pre, ok])
                    rows.append([f.name, week, i + 1, name, "tax", tax, ok])
                    rows.append([f.name, week, i + 1, name, "total", tot, ok])
            elif "precios e impuesto del di" in t:
                for name, (pre, tax, tot, ok) in bars(pg, ["DSL"]).items():
                    rows.append([f.name, week, i + 1, name, "pre_tax", pre, ok])
                    rows.append([f.name, week, i + 1, name, "tax", tax, ok])
                    rows.append([f.name, week, i + 1, name, "total", tot, ok])
            if "estructura de precios del glp" in t and "precio fob" in t:
                for lab, vals in glp(pg).items():
                    for v in vals:
                        rows.append([f.name, week, i + 1, "LPG_25lb", lab, v, ""])
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo)
        w.writerow(["file", "week", "page", "series", "component", "value_usd", "check_total"])
        w.writerows(rows)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
