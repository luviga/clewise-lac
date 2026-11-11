"""Dump paragraphs and tables of the copied paper .docx files to text for reading."""
import sys, zipfile, re
from pathlib import Path
from xml.etree import ElementTree as ET
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
src = Path(sys.argv[1]); out = Path(sys.argv[2])
root = ET.fromstring(zipfile.ZipFile(src).read("word/document.xml"))
body = root.find(W + "body")
lines = []
def ptext(p):
    return "".join(t.text or "" for t in p.iter(W + "t"))
for i, el in enumerate(body):
    if el.tag == W + "p":
        st = el.find(f"{W}pPr/{W}pStyle")
        sty = st.get(W + "val") if st is not None else ""
        t = ptext(el)
        if t.strip(): lines.append(f"[P{i}|{sty}] {t}")
    elif el.tag == W + "tbl":
        lines.append(f"[TABLE {i}]")
        for tr in el.iter(W + "tr"):
            cells = [" ".join(ptext(p) for p in tc.iter(W + "p")) for tc in tr.iter(W + "tc")]
            lines.append(" | ".join(cells))
        lines.append("[END TABLE]")
out.write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
