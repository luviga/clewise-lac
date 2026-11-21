"""Check that the scout downloads hold the 46 registered files with matching SHA-256."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SCOUT, read_csv, sha256, write_csv, JOB

rows = []
for r in read_csv(os.path.join(SCOUT, "sources.csv")):
    p = os.path.join(SCOUT, r["file"])
    ok = os.path.exists(p)
    h = sha256(p) if ok else ""
    rows.append({"id": r["id"], "file": r["file"], "exists": ok,
                 "sha_match": ok and h == r["SHA-256"].strip().lower()})
write_csv(os.path.join(JOB, "parts", "scout_download_check.csv"), rows)
print(len(rows), "files;", sum(r["exists"] for r in rows), "exist;", sum(r["sha_match"] for r in rows), "match")
for r in rows:
    if not r["sha_match"]:
        print("PROBLEM", r)
