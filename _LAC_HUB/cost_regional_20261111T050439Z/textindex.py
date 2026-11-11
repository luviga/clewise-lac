"""Extract page text of a PDF to a text file with page markers (scratch only)."""
import sys, fitz
src, out = sys.argv[1], sys.argv[2]
doc = fitz.open(src)
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    for i, p in enumerate(doc, 1):
        fh.write(f"\n=====PAGE {i}=====\n")
        fh.write(p.get_text())
print(src, len(doc), "pages")
