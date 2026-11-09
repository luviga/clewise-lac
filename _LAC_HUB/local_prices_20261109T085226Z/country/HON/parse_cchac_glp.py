"""Read the Honduras column of the CCHAC table "Costos y variables que conforman el precio al
publico" (LPG, 25 lb cylinder) from the 2024 CCHAC bulletins hosted by SEN.

Usage: py -I parse_cchac_glp.py <dir_with_pdfs> <out_csv>
The table text is stored as single characters, so characters are rebuilt into tokens by line
and gap, then the Honduras column is selected by the x-range of its header.
"""
import csv
import re
import sys
from pathlib import Path

import pdfplumber

LABELS = ["Precio FOB", "Flete Mar", "Seguro Mar", "Operaci", "Cargo Portuario", "Precio CIF+",
          "Importador", "Envasador", "Margen Distribuidor", "Distribuidor (Minorista)",
          "Transporte Terrestre", "Comercializador", "IVA", "Otros", "Mantenimiento Cilindro",
          "Subsidio 1", "Subsidio 2"]


def lines_of(page):
    rows = {}
    for c in page.chars:
        key = round(c["top"])
        k = next((k for k in rows if abs(k - key) <= 2), key)
        rows.setdefault(k, []).append(c)
    out = []
    for k in sorted(rows):
        cs = sorted(rows[k], key=lambda c: c["x0"])
        toks, cur = [], None
        for c in cs:
            if cur and c["x0"] - cur["x1"] <= 2.5:
                cur["text"] += c["text"]
                cur["x1"] = c["x1"]
            else:
                if cur:
                    toks.append(cur)
                cur = {"text": c["text"], "x0": c["x0"], "x1": c["x1"]}
        if cur:
            toks.append(cur)
        out.append((k, toks))
    return out


def main():
    rows = []
    for f in sorted(Path(sys.argv[1]).glob("*.pdf")):
        pdf = pdfplumber.open(f)
        first = " ".join((pdf.pages[0].extract_text() or "").split())
        m = re.search(r"Semana del (.*?20\d\d)", first)
        week = m.group(1) if m else ""
        for i, pg in enumerate(pdf.pages):
            ls = lines_of(pg)
            hdr = [(k, t) for k, toks in ls for t in toks if t["text"].replace(" ", "") == "HONDURAS"]
            var = [k for k, toks in ls for t in toks if t["text"] == "VARIABLES"]
            if not hdr or not var:
                continue
            vy = var[0]
            hk, ht = min(hdr, key=lambda x: abs(x[0] - vy))
            x0, x1 = ht["x0"] - 10, ht["x1"] + 10
            for k, toks in ls:
                if k <= vy or k > vy + 320:
                    continue
                label = " ".join(t["text"] for t in toks if t["x1"] < 175)
                vals = [t["text"] for t in toks if x0 <= (t["x0"] + t["x1"]) / 2 <= x1 and "$" in t["text"]]
                vals2 = [t["text"] for t in toks if x0 <= (t["x0"] + t["x1"]) / 2 <= x1]
                if vals2:
                    rows.append([f.name, week, i + 1, label, " | ".join(vals2)])
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo)
        w.writerow(["file", "week", "page", "row_label", "honduras_column_text"])
        w.writerows(rows)
    print(len(rows))


if __name__ == "__main__":
    main()
