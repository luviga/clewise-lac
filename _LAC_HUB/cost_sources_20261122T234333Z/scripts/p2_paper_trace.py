"""Step 2.4: paper_trace.csv. For every row of the Data in Brief cost tables for transport, AFOLU and
waste (section 4.8), find the technologies it prints by name in the country's proposals and say whether
the proposals would change the printed numbers."""
import os, sys, csv, re, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import JOB

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
z = zipfile.ZipFile(os.path.join(JOB, "downloads", "paper", "CLEWISE_DataInBrief.docx"))
body = ET.fromstring(z.read("word/document.xml")).find(W + "body")
caption, tables = "", []
for el in body:
    if el.tag == W + "p":
        t = "".join(x.text or "" for x in el.iter(W + "t")).strip()
        if t:
            caption = t
    elif el.tag == W + "tbl":
        rows = [["".join(x.text or "" for x in tc.iter(W + "t")).strip() for tc in tr.iter(W + "tc")] for tr in el.iter(W + "tr")]
        tables.append((caption, rows))

CC = {"Costa Rica": "CR", "Dominican Republic": "DR", "Guatemala": "GUA", "Honduras": "HON", "Jamaica": "JAM", "Ecuador": "ECU"}
props = {}
for cc in CC.values():
    p = os.path.join(JOB, cc, "proposals_%s.csv" % cc)
    if os.path.exists(p):
        props[cc] = list(csv.DictReader(open(p, newline="", encoding="utf-8")))


CODE = {"BAN": "banana", "CAF": "coffee", "RIC": "rice", "MAI": "maize", "SGC": "sugarcane", "PLM": "palm",
        "LEG": "legumes", "MEL": "melon", "FRI": "beans", "COF": "coffee", "CNT": "coconut", "VEG": "vegetables",
        "CON": "condiments", "FRT": "fruits", "CER": "cereals", "PLA": "plantains", "POT": "potatoes", "YAM": "yams",
        "BOV": "cattle", "POR": "pigs", "POL": "poultry", "ILK": "milk", "CAR": "othermeats"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


out = []
for ti, (cap, rows) in enumerate(tables, start=1):
    m = re.match(r"Table (\d+)\. Costs of (Transport|AFOLU|Waste) Sector technologies for (.+)$", cap)
    if not m:
        continue
    sector, country = m.group(2), m.group(3).strip()
    cc = CC.get(country)
    hdr = rows[0]
    for ri, row in enumerate(rows[1:], start=2):
        name = row[0]
        if not name:
            continue
        P = props.get(cc, [])
        core = norm(re.sub(r"(Production|Processing)", "", name))
        hits = [p for p in P if norm(p["tech_name"]) == norm(name) or norm(p["tech"]) == norm(name)]
        if not hits and sector == "AFOLU" and core:
            def nm(p):
                n = norm(p["tech_name"]) or norm(CODE.get(p["tech"].split("_")[-1][-3:], ""))
                return n
            hits = [p for p in P if not p["tech"].startswith("IMP") and nm(p) and (nm(p) == core or nm(p).startswith(core) or core.startswith(nm(p)))]
        params = sorted({p["parameter"] for p in hits})
        if not hits:
            out.append(dict(paper_table="Table %s" % m.group(1), docx_table=ti, row=ri, country=country, sector=sector,
                            printed_row=" | ".join(row), matched_techs="", proposal_classes="",
                            base_year_current="", base_year_proposed="", text_would_change="no proposal row (technology not in Phase 2 scope or name not matched)"))
            continue
        techs = sorted({p["tech"] for p in hits})
        by = {}
        for p in hits:
            k = (p["tech"], p["parameter"])
            if k not in by or str(p["year"]) < str(by[k]["year"]):
                by[k] = p
        classes = sorted({p["change_class"] for p in hits})
        changed = any(p["change_class"] == "replace" for p in hits)
        out.append(dict(paper_table="Table %s" % m.group(1), docx_table=ti, row=ri, country=country, sector=sector,
                        printed_row=" | ".join(row), matched_techs=";".join(techs), proposal_classes=";".join(classes),
                        base_year_current="; ".join("%s %s %s=%s" % (k[0], k[1], v["year"], v["current_value"]) for k, v in sorted(by.items())),
                        base_year_proposed="; ".join("%s %s %s=%s" % (k[0], k[1], v["year"], v["proposed_value"]) for k, v in sorted(by.items())),
                        text_would_change=("yes: at least one printed cost of this row has a replace proposal" if changed else "no: confirmed or assumption only")))
with open(os.path.join(JOB, "paper_trace.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), Counter((r["country"], r["sector"], r["text_would_change"][:3]) for r in out))
