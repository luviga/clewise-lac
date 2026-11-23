"""Step 2.4: extract paragraphs and table cells of the Data in Brief draft (copied into
downloads/paper/) that mention vehicle or sector-model costs. Writes downloads/paper/dib_cost_mentions.csv
(untracked working file) for building paper_trace.csv."""
import os, sys, csv, re, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import JOB

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
src = os.path.join(JOB, "downloads", "paper", "CLEWISE_DataInBrief.docx")
z = zipfile.ZipFile(src)
root = ET.fromstring(z.read("word/document.xml"))
body = root.find(W + "body")
items = []
n_par = 0
n_tab = 0
for el in body:
    if el.tag == W + "p":
        n_par += 1
        t = "".join(x.text or "" for x in el.iter(W + "t"))
        items.append(("paragraph %d" % n_par, t))
    elif el.tag == W + "tbl":
        n_tab += 1
        for ri, tr in enumerate(el.iter(W + "tr"), start=1):
            cells = ["".join(x.text or "" for x in tc.iter(W + "t")) for tc in tr.iter(W + "tc")]
            items.append(("table %d row %d" % (n_tab, ri), " | ".join(cells)))
pat = re.compile(r"(cost|capex|capital|O&M|fixed|variable|US\$|USD|price|vehic|bus|truck|car\b|motorcycl|electric|landfill|compost|crop|import|livestock|cattle|penalt|externalit|lifetime|operational life|km)", re.I)
out = os.path.join(JOB, "downloads", "paper", "dib_cost_mentions.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["location", "text"])
    k = 0
    for loc, t in items:
        if t.strip() and pat.search(t):
            w.writerow([loc, t.strip()])
            k += 1
print(n_par, "paragraphs,", n_tab, "tables,", k, "matching items")
