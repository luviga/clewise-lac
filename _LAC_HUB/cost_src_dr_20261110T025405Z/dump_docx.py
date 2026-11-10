"""Dump paragraphs and tables of a .docx (zip XML) to a text file, keeping heading context."""
import zipfile, sys, re
import xml.etree.ElementTree as ET
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
def text_of(el):
    return "".join(t.text or "" for t in el.iter(W + "t"))
def main(src, out):
    z = zipfile.ZipFile(src)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    lines = []; tno = 0
    for child in body:
        if child.tag == W + "p":
            sty = child.find(f"{W}pPr/{W}pStyle")
            s = sty.get(W + "val") if sty is not None else ""
            t = text_of(child).strip()
            if t:
                lines.append(f"[P {s}] {t}")
        elif child.tag == W + "tbl":
            tno += 1
            lines.append(f"[TABLE {tno}]")
            for tr in child.iter(W + "tr"):
                cells = [text_of(tc).strip() for tc in tr.findall(W + "tc")]
                lines.append("  | " + " | ".join(cells))
            lines.append(f"[END TABLE {tno}]")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(src, len(lines), "lines,", tno, "tables")
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
