import zipfile, sys, os
import xml.etree.ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def ptext(p):
    return ''.join(t.text or '' for t in p.iter() if t.tag in (W+'t',W+'tab') and (t.text if t.tag==W+'t' else True) ) if False else ''.join((t.text or '') if t.tag==W+'t' else '\t' for t in p.iter() if t.tag in (W+'t',W+'tab'))
def style(p):
    pp=p.find(W+'pPr')
    if pp is not None:
        s=pp.find(W+'pStyle')
        if s is not None: return s.get(W+'val')
    return ''
src,out=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(src)
root=ET.fromstring(z.read('word/document.xml'))
body=root.find(W+'body')
lines=[];ti=0
for el in body:
    if el.tag==W+'p':
        t=ptext(el)
        if t.strip(): lines.append(f'[P|{style(el)}] {t}')
    elif el.tag==W+'tbl':
        ti+=1; lines.append(f'[TABLE {ti}]')
        for tr in el.iter(W+'tr'):
            cells=[]
            for tc in tr.findall(W+'tc'):
                cells.append(' / '.join(ptext(p) for p in tc.iter(W+'p') if ptext(p).strip()))
            lines.append('  | '+' | '.join(cells))
        lines.append(f'[/TABLE {ti}]')
open(out,'w',encoding='utf-8').write('\n'.join(lines))
print(src, len(lines), ti)
