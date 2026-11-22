"""Hub check of analyses_<code>.csv: every numeric value is searched on its cited page in the text
cache (downloads/<code>/text_all/<id>/p<N>.txt; p1 for an HTML source). Writes
parts/analyses_check_<code>.csv with status found / not_found / no_value / error.
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, read_csv, write_csv, pages_of
from b3_second_place import TOK, token_values

src = {r["id"]: r for r in read_csv(os.path.join(JOB, "sources.csv"))}
for code in CODES:
    p = os.path.join(JOB, f"analyses_{code}.csv")
    if not os.path.exists(p):
        print(code, "no analyses file")
        continue
    out = []
    for i, r in enumerate(read_csv(p), 2):
        sid = r["source_id"]
        st, how = "", ""
        if sid not in src:
            st, how = "error", "source id not in sources.csv"
        elif not r["value"].strip():
            st = "no_value"
        else:
            try:
                x = round(float(r["value"]), 6)
            except ValueError:
                x = None
            pgs = pages_of(r["page"]) or ([1] if "html" in r["page"].lower() else [])
            if x is None or not pgs:
                st, how = "error", "value or page not parseable"
            else:
                st = "not_found"
                for n in pgs:
                    tp = os.path.join(JOB, "downloads", code, "text_all", sid, f"p{n}.txt")
                    if not os.path.exists(tp):
                        continue
                    t = open(tp, encoding="utf-8", errors="replace").read().replace("−", "-")
                    vals = set()
                    for m in TOK.finditer(t):
                        vals |= token_values(m.group(0))
                    if x in vals or -x in vals:
                        st, how = "found", f"p.{n}"
                        break
        out.append({"line": i, "source_id": sid, "scenario": r["scenario"], "indicator": r["indicator"], "year": r["year"],
                    "value": r["value"], "unit": r["unit"], "page": r["page"], "status": st, "how": how})
    write_csv(os.path.join(JOB, "parts", f"analyses_check_{code}.csv"), out)
    c = {}
    for r in out:
        c[r["status"]] = c.get(r["status"], 0) + 1
    print(code, len(out), c)
