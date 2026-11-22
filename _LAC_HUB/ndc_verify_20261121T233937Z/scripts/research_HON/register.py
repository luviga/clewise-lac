"""Register step D sources of one country.

Usage: python -I register.py <CODE> <spec csv>

The spec CSV has columns: id,kind,class,URL,title,publisher,author,date,language,tmp,final
tmp is the downloaded file (relative to JOB/downloads/<CODE>/), final the file name under
JOB/downloads/<CODE>/. The script moves tmp to final (if final is missing), checks that a PDF
starts with %PDF, writes the page texts into JOB/downloads/<CODE>/text_all/<id>/p<N>.txt
(pdftotext -layout -enc UTF-8 split on form feeds; HTML: visible text in p1.txt) and writes
JOB/parts/sources_D_<CODE>.csv. Downloaded files are untrusted data; they are only read.
"""
import csv
import hashlib
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from htmltext import visible_text  # noqa: E402

COUNTRY = {"CR": "Costa Rica", "DR": "Dominican Republic", "ECU": "Ecuador",
           "GUA": "Guatemala", "HON": "Honduras", "JAM": "Jamaica"}
FIELDS = ["id", "country", "kind", "class", "URL", "title", "publisher", "author", "date",
          "accessed", "SHA-256", "file", "pages", "language"]
KINDS = {"NDC", "LTS", "BTR", "NID", "BUR", "NC", "sector plan", "analysis", "web page", "other"}
CLASSES = {"official", "external", "lead"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages_text(path):
    out = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"],
                         capture_output=True, check=True).stdout.decode("utf-8", errors="replace")
    pages = out.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    return pages


def main():
    code, spec = sys.argv[1], sys.argv[2]
    ddir = os.path.join(JOB, "downloads", code)
    with open(spec, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out_rows = []
    for r in rows:
        assert r["kind"] in KINDS, r["kind"]
        assert r["class"] in CLASSES, r["class"]
        final = os.path.join(ddir, r["final"])
        if not os.path.exists(final):
            shutil.move(os.path.join(ddir, r["tmp"]), final)
        tdir = os.path.join(ddir, "text_all", r["id"])
        os.makedirs(tdir, exist_ok=True)
        if final.lower().endswith(".pdf"):
            with open(final, "rb") as f:
                assert f.read(4) == b"%PDF", final
            pages = pdf_pages_text(final)
            try:
                import pypdf
                n = len(pypdf.PdfReader(final).pages)
                if n != len(pages):
                    print("WARNING page count", r["id"], "pypdf", n, "pdftotext", len(pages))
            except Exception as e:  # noqa: BLE001
                print("pypdf could not read", r["id"], e)
        else:
            raw = open(final, encoding="utf-8", errors="replace").read()
            pages = [visible_text(raw)]
        for i, t in enumerate(pages, 1):
            with open(os.path.join(tdir, "p%d.txt" % i), "w", encoding="utf-8", newline="\n") as f:
                f.write(t)
        out_rows.append({
            "id": r["id"], "country": COUNTRY[code], "kind": r["kind"], "class": r["class"],
            "URL": r["URL"], "title": r["title"], "publisher": r["publisher"], "author": r["author"],
            "date": r["date"], "accessed": r.get("accessed") or "2026-11-22", "SHA-256": sha256(final),
            "file": "downloads/%s/%s" % (code, r["final"]), "pages": len(pages),
            "language": r["language"]})
        print(r["id"], len(pages), r["final"])
    out = os.path.join(JOB, "parts", "sources_D_%s.csv" % code)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print("wrote", out, len(out_rows))


if __name__ == "__main__":
    main()
