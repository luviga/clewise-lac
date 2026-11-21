"""LAC_NDC_SCOUT hub: merge per-country parts (step D2, D3 counts, sources) and run gates E2 to E4.

Usage: python -I hub_merge_and_gates.py <job_folder> <headline_csv>
<headline_csv> holds the hand-written per-country NDC and LTS fields for cross_country_summary.csv
(columns: country,code,ndc_document,ndc_date,ndc_target_year,ndc_target_type,ndc_headline,lts_document,lts_date,lts_goal).
Writes sources.csv, sources_pending.csv, spot_checks.csv, proposed_scenario_changes.csv,
cross_country_summary.csv and parts/gate_results.csv. Gates E1 and E5 are git checks run by the hub.
"""
import csv
import hashlib
import os
import sys

JOB = sys.argv[1]
HEAD = sys.argv[2]
CODES = ["CR", "DR", "ECU", "GUA", "HON", "JAM"]
STATUSES = ["matches", "same direction, different size", "opposite direction",
            "in documents, not in the model", "in the model, not in the documents", "not compared"]


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def p(*a):
    return os.path.join(JOB, *a)


SRC_F = ["id", "country", "kind", "URL", "title", "publisher", "date", "accessed", "SHA-256", "file", "pages", "language"]
sources, pending, spots, props = [], [], [], []
for c in CODES:
    sources += read(p("parts", f"sources_{c}.csv"))
    pending += read(p("parts", f"sources_pending_{c}.csv"))
    spots += read(p("parts", f"spot_checks_{c}.csv"))
    for r in read(p("parts", f"proposals_{c}.csv")):
        props.append(r)
write(p("sources.csv"), sources, SRC_F)
write(p("sources_pending.csv"), pending, ["country", "kind", "title", "urls_tried", "errors", "note"])
write(p("spot_checks.csv"), spots, ["country", "round", "file", "row_id", "source_id", "page", "value", "unit", "year",
                                    "confirmed", "how_checked", "correction"])
PROP_F = ["country", "scenario", "lever", "model_rows", "current_value", "proposed_value", "source_id", "page", "class", "note"]
write(p("proposed_scenario_changes.csv"), props, PROP_F)

gates = []
ids = {s["id"]: s for s in sources}
# E3: every source file exists with a matching SHA-256
bad = []
for s in sources:
    fp = p(s["file"])
    if not os.path.exists(fp):
        bad.append(f"{s['id']} missing")
    elif sha256(fp) != s["SHA-256"].strip().lower():
        bad.append(f"{s['id']} sha mismatch")
gates.append({"gate": "E3", "check": "every source file exists with matching SHA-256",
              "result": "pass" if not bad else "fail", "detail": f"{len(sources)} sources; " + "; ".join(bad)})
# E2: every row of targets_, projections_, alignment_ has a source id in sources.csv and a page or table
bad = []
nrows = 0
for c in CODES:
    for kind in ["targets", "projections", "alignment"]:
        for i, r in enumerate(read(p(f"{kind}_{c}.csv")), start=2):
            nrows += 1
            sid_field = r.get("source_id", "")
            sids = [x.strip() for x in sid_field.replace(";", ",").split(",") if x.strip()]
            page = (r.get("page", "") or "").strip() or (r.get("table_or_figure", "") or "").strip()
            if not sids or any(x not in ids for x in sids) or not page:
                bad.append(f"{kind}_{c}.csv line {i} ({sid_field or 'no id'}, {page or 'no page'})")
gates.append({"gate": "E2", "check": "rows of targets_, projections_, alignment_ have a known source id and a page or table",
              "result": "pass" if not bad else "fail", "detail": f"{nrows} rows; {len(bad)} failing: " + "; ".join(bad[:40])})
# E4: spot check ends with ten of ten confirmed for every country (last round of each country)
det = []
ok = True
for c_name in sorted(set(r["country"] for r in spots)):
    rows = [r for r in spots if r["country"] == c_name]
    last = max(int(r["round"]) for r in rows)
    lr = [r for r in rows if int(r["round"]) == last]
    conf = sum(1 for r in lr if r["confirmed"].strip().lower() == "yes")
    det.append(f"{c_name} round {last}: {conf} of {len(lr)}")
    ok = ok and conf == 10 and len(lr) == 10
ok = ok and len(det) == 6
gates.append({"gate": "E4", "check": "spot check ends ten of ten for every country", "result": "pass" if ok else "fail",
              "detail": "; ".join(det)})
write(p("parts", "gate_results.csv"), gates, ["gate", "check", "result", "detail"])

# D3 cross-country summary
head = {r["code"]: r for r in read(HEAD)}
out = []
for c in CODES:
    h = head.get(c, {})
    al = read(p(f"alignment_{c}.csv"))
    pr = read(p("parts", f"proposals_{c}.csv"))
    rec = {k: h.get(k, "") for k in ["country", "code", "ndc_document", "ndc_date", "ndc_target_year", "ndc_target_type",
                                      "ndc_headline", "lts_document", "lts_date", "lts_goal"]}
    for s in STATUSES:
        rec["alignment_" + s.replace(", ", "_").replace(" ", "_")] = sum(1 for r in al if r["status"] == s)
    rec["alignment_total"] = len(al)
    for k in ["A", "B", "C"]:
        rec["proposals_class_" + k] = sum(1 for r in pr if r.get("class", "").strip() == k)
    rec["proposals_documents_silent"] = sum(1 for r in pr if not r.get("class", "").strip())
    out.append(rec)
write(p("cross_country_summary.csv"), out, list(out[0].keys()))
for g in gates:
    print(g["gate"], g["result"], g["detail"][:600])
for r in out:
    print({k: v for k, v in r.items() if k.startswith(("code", "alignment_total", "proposals"))})
