"""Step B, check 2: write blind_<code>.csv (no value, unit or year) and the key that maps
blind items back to value ids (parts/blind_key_<code>.csv, not given to the blind reader).

A blind item is one source, one page list and one description with numbers and years removed.
Target rows that share source, pages and scrubbed description become one item; the reader
reports every year and value printed for it, and the hub matches by year.
Projection rows become one item per series (source, page, scenario, sector, gas).
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, SCOUT, CODES, read_csv, write_csv

src = {r["id"]: r for r in read_csv(os.path.join(SCOUT, "sources.csv"))}


def scrub(s):
    s = re.sub(r"\b(19|20)\d\d\b", "[year]", s)
    s = re.sub(r"\d[\d.,]*", "[n]", s)
    s = re.sub(r"\b(kt|Gg|Mt|MtCO2e|ktCO2e|GWh|TWh|MWh|MW|GW|PJ|TJ|percent|%)\b", "[unit]", s, flags=re.I)
    return s.strip()


vals = read_csv(os.path.join(JOB, "values_to_verify.csv"))
for code in CODES:
    items, key = {}, []
    for v in vals:
        if v["country"] != code:
            continue
        if v["origin"].startswith("projections"):
            sc, sec = v["scenario_as_named"], v["sector"]
            desc = f"Projected GHG emissions series, scenario '{scrub(sc)}', sector '{scrub(sec)}': report every year printed and its value"
        else:
            desc = scrub(v["description"])
        k = (v["source_id"], v["page"], desc)
        if k not in items:
            items[k] = f"{code}-B{len(items) + 1:03d}"
        key.append({"value_id": v["value_id"], "blind_id": items[k]})
    rows = []
    for (sid, page, desc), bid in items.items():
        rows.append({"blind_id": bid, "source_id": sid, "pdf_file": "C:/clw_scout/_LAC_HUB/ndc_scout_20261121T204620Z/" + src[sid]["file"],
                     "pages": page, "what_to_read": desc})
    write_csv(os.path.join(JOB, f"blind_{code}.csv"), rows)
    write_csv(os.path.join(JOB, "parts", f"blind_key_{code}.csv"), key)
    print(code, len(rows), "blind items for", len(key), "values")
