"""Structural checks of the CR output files and spot-check helper.
Usage: python -I check_files.py <JOB folder>
Checks column sets, status vocabulary, source ids and pages, no em dash, then prints, for each spot-check
needle, the page text lines that contain it."""
import csv
import os
import sys

JOB = sys.argv[1]
EM = chr(0x2014)
STATUS = {"matches", "same direction, different size", "opposite direction",
          "in documents, not in the model", "in the model, not in the documents", "not compared"}
COLS = {
    "parts/sources_CR.csv": "id,country,kind,URL,title,publisher,date,accessed,SHA-256,file,pages,language",
    "parts/sources_pending_CR.csv": "country,kind,title,urls_tried,errors,note",
    "targets_CR.csv": "target_id,source_id,page,table_or_figure,document_kind,sector,description,original_term,indicator,value,unit,base_or_reference,target_year,conditionality,gases,read_as_image,note",
    "projections_CR.csv": "source_id,page,table_or_figure,scenario_as_named,sector,gas,unit,year,value,note",
    "alignment_CR.csv": "target_id,source_id,page,target_description,target_value,target_unit,target_year,model_quantity,model_reference,NDCNEW_value,LTSNEW_value,model_unit,ratio_NDCNEW,ratio_LTSNEW,status,sector_model_folder,note",
    "parts/proposals_CR.csv": "country,scenario,lever,model_rows,current_value,proposed_value,source_id,page,class,note",
    "parts/spot_checks_CR.csv": "country,round,file,row_id,source_id,page,value,unit,year,confirmed,how_checked,correction",
}


def rows(rel):
    path = os.path.join(JOB, rel)
    if not os.path.exists(path):
        return None, None
    raw = open(path, "rb").read()
    if b"\r\n" in raw:
        print("CRLF in", rel)
    text = raw.decode("utf-8")
    if EM in text:
        print("EM DASH in", rel)
    r = list(csv.reader(text.splitlines()))
    return r[0], r[1:]


src = {}
h, b = rows("parts/sources_CR.csv")
for r in b:
    src[r[0]] = int(r[10])
for rel, cols in COLS.items():
    h, b = rows(rel)
    if h is None:
        print("missing", rel)
        continue
    if ",".join(h) != cols:
        print("HEADER MISMATCH", rel, h)
    n = len(h)
    for i, r in enumerate(b, start=2):
        if len(r) != n:
            print(rel, "line", i, "has", len(r), "fields, expected", n)
            continue
        d = dict(zip(h, r))
        if "source_id" in d:
            sids = [s for s in d.get("source_id", "").split(";") if s]
            if rel == "parts/proposals_CR.csv" and not sids:
                sids = []
            elif not sids:
                print(rel, "line", i, "missing source")
            for sid in sids:
                if sid not in src:
                    print(rel, "line", i, "unknown source", sid)
            pg = d.get("page", "")
            if sids and not pg.startswith("p."):
                print(rel, "line", i, "bad page", pg)
            elif sids:
                maxp = max(src.get(s, 0) for s in sids)
                for p in pg.split(";"):
                    num = int(p.strip()[2:])
                    if not 1 <= num <= maxp:
                        print(rel, "line", i, "page out of range", p)
        if rel == "alignment_CR.csv" and d["status"] not in STATUS:
            print(rel, "line", i, "bad status", d["status"])
        if rel == "parts/proposals_CR.csv" and d["class"] not in {"A", "B", "C", ""}:
            print(rel, "line", i, "bad class", d["class"])
    print(rel, "rows", len(b))
for rel in ["published_CR.md", "changes_since_paper_CR.md", "parts/notes_CR.md"]:
    p = os.path.join(JOB, rel)
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        print(rel, "em dash" if EM in t else "ok", len(t.split()), "words")
    else:
        print("missing", rel)
