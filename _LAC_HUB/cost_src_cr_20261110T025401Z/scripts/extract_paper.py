"""Extract paragraphs and tables from the copied CLEWISE docx files to text (scratch)."""
import sys, zipfile, re
from xml.etree import ElementTree as ET
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def text(el):
    return ''.join(t.text or '' for t in el.iter(W+'t'))
src, out = sys.argv[1], sys.argv[2]
root = ET.fromstring(zipfile.ZipFile(src).read('word/document.xml'))
body = root.find(W+'body')
lines = []; ti = 0
for el in body:
    if el.tag == W+'p':
        s = text(el).strip()
        sty = el.find(f'{W}pPr/{W}pStyle')
        st = sty.get(W+'val') if sty is not None else ''
        if s: lines.append(f'[P {st}] {s}')
    elif el.tag == W+'tbl':
        ti += 1; lines.append(f'[TABLE {ti}]')
        for tr in el.iter(W+'tr'):
            lines.append(' | '.join(text(tc).strip() for tc in tr.findall(W+'tc')))
        lines.append('[END TABLE]')
open(out, 'w', encoding='utf-8').write('\n'.join(lines))
print(src, len(lines))
