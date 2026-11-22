"""Register the step D sources of one country.

Usage: python -I register.py <JOB> <code> <meta.csv>

meta.csv columns: id,country,kind,class,URL,title,publisher,author,date,accessed,file,language
(file relative to JOB). For each row: check the file (PDF starts with %PDF), compute SHA-256,
write page texts to JOB/downloads/<code>/text_all/<id>/p<N>.txt (pdftotext -layout split on
form feeds; HTML visible text to p1.txt), count pages, and write JOB/parts/sources_D_<code>.csv.
"""
import csv
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from html2text import visible_text  # noqa: E402

COLS = ["id", "country", "kind", "class", "URL", "title", "publisher", "author", "date",
        "accessed", "SHA-256", "file", "pages", "language"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path, outdir):
    out = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    parts = out.split("\f")
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    for i, t in enumerate(parts, start=1):
        with open(os.path.join(outdir, "p%d.txt" % i), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    return len(parts)


def main():
    job, code, meta = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = []
    with open(meta, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            path = os.path.join(job, r["file"])
            with open(path, "rb") as fh:
                head = fh.read(5)
            outdir = os.path.join(job, "downloads", code, "text_all", r["id"])
            os.makedirs(outdir, exist_ok=True)
            if path.lower().endswith(".pdf"):
                if not head.startswith(b"%PDF"):
                    raise SystemExit("not a PDF: " + path)
                pages = pdf_pages(path, outdir)
            else:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    t = visible_text(fh.read())
                with open(os.path.join(outdir, "p1.txt"), "w", encoding="utf-8", newline="\n") as fo:
                    fo.write(t)
                pages = 1
            r["SHA-256"] = sha256(path)
            r["pages"] = str(pages)
            rows.append(r)
            print(r["id"], pages, r["SHA-256"][:12])
    out = os.path.join(job, "parts", "sources_D_%s.csv" % code)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == "__main__":
    main()
