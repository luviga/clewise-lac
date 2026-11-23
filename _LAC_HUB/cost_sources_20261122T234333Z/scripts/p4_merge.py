"""Phase 4: merge every manual-download list into manual_downloads.csv and print overall counts."""
import os, sys, csv
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import JOB

CCS = ["CR", "DR", "GUA", "HON", "JAM", "ECU"]
lists = [("GEN vehicles", "GEN/manual_downloads_GEN_vehicles.csv"), ("GEN sector", "GEN/manual_downloads_GEN_sector.csv")]
lists += [(cc, "%s/manual_downloads_%s.csv" % (cc, cc)) for cc in CCS]
rows = []
for who, p in lists:
    for r in csv.DictReader(open(os.path.join(JOB, p), newline="", encoding="utf-8")):
        if any(v.strip() for v in r.values() if v):
            rows.append(dict(listed_by=who, url=r.get("url", ""), title=r.get("title", ""),
                             what_it_would_source=r.get("what_it_would_source", ""),
                             proposal_rows_waiting=r.get("proposal_rows_waiting", "")))
with open(os.path.join(JOB, "manual_downloads.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["listed_by", "url", "title", "what_it_would_source", "proposal_rows_waiting"], lineterminator="\n")
    w.writeheader(); w.writerows(rows)
print("manual rows", len(rows))
for r in rows:
    print("-", r["listed_by"], "|", r["title"][:110], "|", r["url"][:90])

tot = Counter()
print("\ncountry cells confirmed replace assumption manual pairs")
for cc in CCS:
    d = list(csv.DictReader(open(os.path.join(JOB, cc, "proposals_%s.csv" % cc), newline="", encoding="utf-8")))
    c = Counter(r["change_class"] for r in d)
    pairs = len({(r["model"], r["tech"], r["parameter"]) for r in d})
    tot.update(c); tot["cells"] += len(d); tot["pairs"] += pairs
    print(cc, len(d), c["confirmed"], c["replace"], c["assumption"], c["manual"], pairs)
print("TOTAL", dict(tot))
