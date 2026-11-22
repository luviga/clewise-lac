"""Step B: write verification_<code>.csv, one row per value of values_to_verify.csv.

Status rule (recorded in GAPS):
- check 1 counts when the hub's third reading (where one was needed) does not overturn it;
- check 2 counts when the blind reading has the same value for the same year, or when the third
  reading finds that both readings state the same verbal target (check 1 encoded a word as a number);
- check 3 counts when an identity holds, or the value is printed on another page or document in a
  line that also holds the year or a keyword of the value's kind ('strong' or 'medium' hit); for a
  verbal target, when the blind reader found the statement on a second page;
- a value listed in parts/self_conflicts.csv (the document gives two values for the same quantity and year,
  or a printed value that its own label contradicts) is a conflict whatever its counts;
- 3 counts give '3 of 3', 2 give '2 of 3' naming the missing check, fewer give 'conflict';
  a third reading that supports check 2 or neither reading also gives 'conflict'.
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, read_csv, write_csv

third = {r["value_id"]: r for r in read_csv(os.path.join(JOB, "parts", "third_reading.csv"))}
selfc = {r["value_id"]: r["note"] for r in read_csv(os.path.join(JOB, "parts", "self_conflicts.csv"))}
vals = read_csv(os.path.join(JOB, "values_to_verify.csv"))
total = {}
for code in CODES:
    comp = {r["value_id"]: r for r in read_csv(os.path.join(JOB, "parts", f"compare_{code}.csv"))}
    c3 = {r["value_id"]: r for r in read_csv(os.path.join(JOB, "parts", f"check3_{code}.csv"))}
    answers = {}
    for r in read_csv(os.path.join(JOB, f"blind_answers_{code}.csv")):
        answers.setdefault(r["blind_id"], []).append(r)
    rows = []
    for v in vals:
        if v["country"] != code:
            continue
        vid = v["value_id"]
        cp, k3, t = comp[vid], c3[vid], third.get(vid)
        verbal = (t is not None and t["supports"] == "verbal") or v["numeric"] == "False"
        c1 = not (t and t["supports"] in ("check2", "neither"))
        c2 = cp["check2_status"] == "agree" or (t is not None and t["check2_reading"] == "agree")
        if v["numeric"] == "False":
            c2 = bool([a for a in answers.get(cp["blind_id"], []) if "not found" not in a["note"].lower()])
        if verbal:
            pages = {a["page_read"] for a in answers.get(cp["blind_id"], []) if "not found" not in a["note"].lower()}
            c3ok = len(pages) >= 2
            place = f"statement repeated on {', '.join(sorted(pages))} of {v['source_id']} (blind reading)" if c3ok else "no second place found"
            how = "verbal target: statement found on more than one page" if c3ok else ""
        else:
            c3ok = bool(k3["identity"]) or k3["best_strength"] in ("strong", "medium")
            if k3["identity"]:
                place, how = f"{v['source_id']} (printed numbers)", k3["identity"]
            elif c3ok:
                place = k3["best_place"]
                how = f"same figure printed in a line with the {'year' if k3['best_strength'] == 'strong' else 'kind keyword'} (text search; {k3['n_hits']} places in all)"
            else:
                place = "no second place found"
                how = f"only weak text matches: {k3['best_place']}" if k3["best_strength"] == "weak" else ""
        if t and t["supports"] in ("check2", "neither"):
            c3ok = False
        n = c1 + c2 + c3ok
        if t and t["supports"] in ("check2", "neither"):
            status = "conflict"
            snote = f"check 1 {v['value']} {v['unit']} {v['year']} against check 2 {cp['check2_value']} {cp['check2_unit']} {cp['check2_year']}; " + \
                    ("the document supports check 2: " if t["supports"] == "check2" else "the document supports neither reading in full: ") + t["note"]
        elif n == 3:
            status, snote = "3 of 3", ""
        elif n == 2:
            miss = [name for name, ok in [("check 1", c1), ("check 2", c2), ("check 3", c3ok)] if not ok][0]
            status = "2 of 3"
            why = {"check 2": f"check 2 {cp['check2_status']}" + (f" ({t['check2_reading']}); hub third reading supports check 1" if t else ""),
                   "check 3": "no second place found", "check 1": "check 1 overturned"}[miss]
            snote = f"missing {miss}: {why}"
        else:
            status = "conflict"
            snote = f"only {n} of 3 checks; check 2 {cp['check2_status']}" + (f"; hub third reading: {t['note']}" if t else "")
        if vid in selfc:
            status, snote = "conflict", selfc[vid]
        settled_v = (t["third_value"] if t and t["supports"] in ("check1", "check2", "neither") else v["value"])
        rows.append({
            "value_id": vid, "country": code, "source_id": v["source_id"], "document_role": v["document_role"],
            "description": v["description"],
            "check1_value": v["value"], "check1_unit": v["unit"], "check1_year": v["year"], "check1_page": v["page"],
            "check2_value": cp["check2_value"], "check2_unit": cp["check2_unit"], "check2_year": cp["check2_year"],
            "check2_page": cp["check2_page"], "check2_result": cp["check2_status"],
            "check3_place": place, "check3_how": how,
            "third_reading_page": t["third_page"] if t else "", "third_reading_value": t["third_value"] if t else "",
            "third_reading_year": t["third_year"] if t else "", "third_reading_note": t["note"] if t else "",
            "settled_value": settled_v, "verbal_target": "yes" if verbal else "no",
            "status": status, "status_note": snote})
    write_csv(os.path.join(JOB, f"verification_{code}.csv"), rows)
    cnt = {}
    for r in rows:
        cnt[r["status"]] = cnt.get(r["status"], 0) + 1
    total[code] = cnt
    print(code, len(rows), cnt)
write_csv(os.path.join(JOB, "parts", "status_counts.csv"),
          [{"country": c, "3 of 3": d.get("3 of 3", 0), "2 of 3": d.get("2 of 3", 0), "conflict": d.get("conflict", 0)} for c, d in total.items()])
