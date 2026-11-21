"""Self check: is each numeric value of targets_ECU.csv and projections_ECU.csv printed on a cited page?

Usage: python -I self_check_ECU.py <job_folder> <out_csv>
Searches the text cache downloads/ECU/text/<source>/p<N>.txt for printed forms of the value
(Spanish and English thousands and decimal separators). Prints the rows not found.
"""
import csv
import os
import re
import sys

JOB, OUT = sys.argv[1], sys.argv[2]


def forms(v):
    s = str(v).strip()
    if not s:
        return []
    try:
        x = float(s)
    except ValueError:
        return [s]
    out = set()
    neg = x < 0
    x = abs(x)
    if x == int(x):
        i = int(x)
        out.update({str(i), f"{i:,}".replace(",", "."), f"{i:,}", f"{i:,}".replace(",", " ")})
    else:
        txt = s.lstrip("-")
        ip, dp = txt.split(".")
        ipi = int(ip)
        for th in (".", ",", " ", ""):
            for dec in (",", "."):
                if th == dec:
                    continue
                g = f"{ipi:,}".replace(",", th) if th else str(ipi)
                out.add(g + dec + dp)
    if neg:
        out = {"-" + f for f in out} | out
    return sorted(out, key=len, reverse=True)


def text_of(src, pages):
    t = ""
    for p in pages:
        f = os.path.join(JOB, "downloads", "ECU", "text", src, f"p{p}.txt")
        if os.path.exists(f):
            with open(f, encoding="utf-8") as h:
                t += h.read() + "\n"
    return t


res = []
for name, idcol in (("targets_ECU.csv", "target_id"), ("projections_ECU.csv", None)):
    with open(os.path.join(JOB, name), encoding="utf-8") as f:
        for k, r in enumerate(csv.DictReader(f), start=2):
            pages = re.findall(r"p\.(\d+)", r["page"])
            t = text_of(r["source_id"], pages)
            fs = forms(r["value"])
            if not fs:
                st = "no_value"
            else:
                tt = re.sub(r"\s+", " ", t)
                st = "found" if any(re.search(r"(?<![0-9])" + re.escape(x) + r"(?![0-9])", tt) for x in fs) else "not_found"
            rid = r[idcol] if idcol else f"row{k}"
            res.append({"file": name, "row": rid, "source_id": r["source_id"], "page": r["page"], "value": r["value"], "status": st})
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    w = csv.DictWriter(f, fieldnames=list(res[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(res)
from collections import Counter
print(Counter(r["status"] for r in res))
for r in res:
    if r["status"] == "not_found":
        print(r)
