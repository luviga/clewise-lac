"""Check register_history.csv: B1 token diffs, before equals current cell, and no duplicate keys."""
import csv, re
from collections import Counter
rows = list(csv.DictReader(open(r"C:\clw_align\_LAC_HUB\align_20261124T021708Z\work\register_history.csv", encoding="utf-8")))
keys = Counter((r["model"], r["file"], r["sheet"], r["tech"], r["parameter"], r["year"]) for r in rows)
print("duplicates", [k for k, v in keys.items() if v > 1])
for r in rows:
    if r["file"].startswith("B1"):
        b = [t.strip() for t in r["before"].split(";")]
        a = [t.strip() for t in r["after"].split(";")]
        diff = [(i, x, y) for i, (x, y) in enumerate(zip(b, a)) if x != y]
        print(r["model"], r["tech"], r["parameter"], "len", len(b), len(a), "diffs", diff)
    if r["year"] in ("Projection.Mode",):
        print(r["model"], r["tech"], r["parameter"], r["year"], repr(r["before"]), "->", r["after"])
print(Counter(r["model"] for r in rows))
print("empty derivation", sum(1 for r in rows if not r["derivation"]))
print("em dash", sum(1 for r in rows for v in r.values() if "\u2014" in v))
