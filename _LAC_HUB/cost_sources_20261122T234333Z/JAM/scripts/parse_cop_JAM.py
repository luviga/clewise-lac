"""Parse the Ministry of Agriculture (Jamaica) Cost of Production Estimates text (pdftotext -layout).

Returns one record per crop budget: parish, crop, area, yield kg, cost J$ per kg.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))


def num(s):
    s = s.replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse(name="MOA_COP_2022.txt"):
    path = os.path.join(JOB, "downloads", "JAM", name)
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")
    recs, cur = [], None
    for ln in lines:
        m = re.match(r"^\s*(Parish|Crop|Area|Projected Marketable Yield \(Kg\)|Cost of Production \$/Kg)\s{2,}(\S.*?)\s*$", ln)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        if key == "Parish":
            if cur:
                recs.append(cur)
            cur = {"parish": val}
        elif cur is not None:
            cur[key] = val
    if cur:
        recs.append(cur)
    out = []
    for r in recs:
        y = num(r.get("Projected Marketable Yield (Kg)", ""))
        c = num(r.get("Cost of Production $/Kg", ""))
        ok = r.get("Area", "").startswith("0.4") and y is not None and c is not None
        out.append(dict(parish=r["parish"], crop=r.get("Crop", "").strip().upper(), area=r.get("Area", ""), yield_kg=y, cop=c, ok=ok))
    return out


if __name__ == "__main__":
    import sys
    for r in parse(sys.argv[1] if len(sys.argv) > 1 else "MOA_COP_2022.txt"):
        tot = r["yield_kg"] * r["cop"] / 0.4 if r["ok"] else None
        print(r["ok"], r["parish"], r["crop"], r["area"], r["yield_kg"], r["cop"], tot)
