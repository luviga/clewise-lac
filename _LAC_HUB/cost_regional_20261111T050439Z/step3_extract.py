"""Step 3: write regional_values.csv (every generation cost printed in the opened regional documents)
and sources.csv. Inputs: regional_data.py (transcribed values), scratch/col_catalog_rows.csv
(catalog_extract.py) and the Panama PESIN text (project tables)."""
import csv, re, sys
import pandas as pd
sys.path.insert(0, ".")
import regional_data as RD

PUB_YEAR = {s[0]: s[4][:4] for s in RD.SOURCES}
DOC = {s[0]: s[2] for s in RD.SOURCES}

TIER = {
    "REG-001": "R1 for all six countries", "REG-002": "R1 for all six countries", "REG-003": "R1 for all six countries",
    "REG-004": "R1 for CostaRica, Guatemala, Honduras", "REG-012": "R1 for all six countries", "REG-018": "R1 for DominicanRepublic, Jamaica",
    "REG-005": "N for CostaRica; R2 for Guatemala, Honduras",
    "REG-006": "national source already used by the Honduras job; R2 for CostaRica, Guatemala",
    "REG-020": "national source already used by the Honduras job; R2 for CostaRica, Guatemala",
    "REG-007": "national source already used by the Guatemala job; R2 for CostaRica, Honduras",
    "REG-008": "N for Guatemala; R2 for CostaRica, Honduras",
    "REG-009": "R2 for CostaRica, Guatemala, Honduras", "REG-010": "R2 for CostaRica, Guatemala, Honduras", "REG-011": "R2 for CostaRica, Guatemala, Honduras",
    "REG-013": "R2 for Ecuador", "REG-014": "R2 for Ecuador",
    "REG-015": "national source already used by the Jamaica job; R2 for DominicanRepublic",
    "REG-021": "national source already used by the Jamaica job; R2 for DominicanRepublic",
    "REG-016": "national source already used by the Dominican Republic job; R2 for Jamaica",
    "REG-017": "R2 for DominicanRepublic, Jamaica", "REG-019": "R2 for DominicanRepublic, Jamaica",
}

rows = []
def push(sid, page, loc, tech, comp, val, unit, cur, vyear, geo, chk):
    rows.append({"value_id": f"V{len(rows) + 1:04d}", "source_id": sid, "document": DOC[sid],
                 "page_or_table": (f"PDF p.{page}, " if page else "") + loc, "pdf_page": page,
                 "technology_as_printed": tech, "cost_component": comp, "value": val, "unit": unit,
                 "currency_year": cur, "value_year": vyear, "geography": geo, "publication_year": PUB_YEAR[sid],
                 "tier": TIER[sid], "check_string": chk})

for r in RD.V:
    push(*r)

# Colombian catalogue rows (2024, 2030, 2050 columns), with two corrections for split cells
cat = pd.read_csv("scratch/col_catalog_rows.csv")
for _, r in cat.iterrows():
    lab = str(r["label"]); tech = str(r["technology"]); p = int(r["pdf_page"])
    if lab.lower().startswith("inversión nominal (%)") or pd.isna(r["v2024"]) and pd.isna(r["v2030"]):
        continue
    if p == 68 and ("DC" in lab or "MWp" in lab or "relacionados" in lab):
        continue  # DC-basis rows on p.68 are misaligned in the table layer; AC rows kept
    printed = str(r["printed"]).split(" | ")
    vals = [r["v2024"], r["v2030"], r["v2050"]]
    note = ""
    if lab.startswith("O&M fij") and "MWe" in lab and all(isinstance(v, float) and v < 1000 for v in vals if pd.notna(v)) and p in (64, 140, 141):
        vals = [v * 1000 if pd.notna(v) and v < 1000 else v for v in vals]
        note = " (thousands separator split or printed as comma in the PDF; read as thousands)"
    if p == 141 and lab.startswith("O&M fij"):
        vals = [94000.0, 93600.0, 93100.0]
        note = " (first cell printed 94.00 next to 93.600 and 93.100; read as 94,000)"
    if lab.startswith("Inversi") or lab.startswith("Costo total"):
        comp = "capital"
        unit = "MUSD/MWh" if "MWh" in lab or (p in (315, 317) and lab.startswith("Costo total")) else ("MUSD/MWp (DC)" if "DC" in lab or "MWp" in lab else "MUSD/MWe")
    elif "fij" in lab:
        comp, unit = "fixed_om", ("USD/MWp(DC)-year" if "DC" in lab else "USD/MWe-year")
    else:
        comp, unit = "variable_om", "USD/MWh"
    for y, v, pr in zip((2024, 2030, 2050), vals, printed):
        if pd.isna(v):
            continue
        push("REG-014", p, f"data sheet row '{lab}'{note}", tech, comp, float(v), unit, 2024, y, "Colombia", pr.strip())

# Panama PESIN 2025-2039 project tables (wind p.58, solar p.60 to p.64, hydro p.66)
t = open("scratch/PAN_ETESA_PESIN_2025-2039_tomoII_generacion.txt", encoding="utf-8").read()
pages = re.split(r"\n=====PAGE (\d+)=====\n", t)
pat = {
    "wind": re.compile(r"\|([^|]+)\|Aerogeneradores de \|Eje Horizontal\|[^|]+\|[^|]+\|[^|]+\|([^|]+)\|([^|]+)\|"),
    "solar": re.compile(r"\|([^|]+)\|Solar Fotovoltaica\|[^|]+\|[^|]+\|[^|]+\|([^|]+)\|([^|]+)\|"),
    "hydro": re.compile(r"\|([^|]+)\|Hidroel.ctrica \|de Pasada\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|([^|]+)\|([^|]+)\|"),
}
for i in range(1, len(pages), 2):
    no = int(pages[i]); b = "|" + pages[i + 1].replace("\n", "|")
    if not 57 <= no <= 67:
        continue
    for kind, rx in pat.items():
        for name, fom, cap in rx.findall(b):
            name = name.strip()
            try:
                capv, fomv = float(cap.replace(",", "")), float(fom.replace(",", ""))
            except ValueError:
                continue
            tech = {"wind": "wind project", "solar": "solar PV project", "hydro": "run-of-river hydro project"}[kind]
            push("REG-009", no, "Tabla 4.9/4.10/4.11 (project)", f"{name} ({tech})", "capital", capv, "B/./kW", "not stated", "project", "Panama", cap.strip())
            push("REG-009", no, "Tabla 4.9/4.10/4.11 (project)", f"{name} ({tech})", "fixed_om", fomv, "B/./kW-year", "not stated", "project", "Panama", fom.strip())

out = pd.DataFrame(rows)
out.to_csv("regional_values.csv", index=False, lineterminator="\n")

src = pd.DataFrame([{"source_id": s[0], "url": s[1], "title": s[2], "publisher": s[3], "publication_date": s[4], "retrieval_date": s[5],
                     "downloaded_file": s[6], "region": s[7], "notes": s[8]} for s in RD.SOURCES])
loc = out.groupby("source_id")["page_or_table"].apply(lambda x: "; ".join(sorted(set(x)))[:400])
src["page_or_table"] = src["source_id"].map(loc).fillna("opened; no value transcribed (see GAPS)")
src.to_csv("scratch/sources_regional.csv", index=False, lineterminator="\n")
print(len(out), "values;", out.groupby("source_id").size().to_dict())
