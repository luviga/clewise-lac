"""Extract capital and O&M rows (2024, 2030, 2050 columns) from every data sheet of the
Colombian Technology Catalogue (MinEnergia/UPME, March 2025). Output: scratch/col_catalog_rows.csv."""
import re, csv, sys, pdfplumber
PDF = "downloads/and/COL_MinEnergia_Catalogo_Tecnologico_generacion_almacenamiento.pdf"
PAGES = range(60, 330)
LABEL = re.compile(r"^(Inversi[oó]n|Costo total de la inversi[oó]n|O&M fij|O&M [Vv]ariab|Variable O&M)", re.I)
def num(s):
    s = s.strip().replace(" ", "")
    if s in ("", "-"):
        return None
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):      # thousands separator
        return float(s.replace(".", ""))
    if re.fullmatch(r"\d+,\d+", s):                # decimal comma
        return float(s.replace(",", "."))
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return float(s)
    if re.fullmatch(r"\d{1,3}(,\d{3})+", s):       # stray English thousands
        return float(s.replace(",", ""))
    return "BAD:" + s
rows, tech = [], None
pdf = pdfplumber.open(PDF)
for p in PAGES:
    for t in pdf.pages[p - 1].extract_tables():
        for r in t:
            cells = [(c or "").replace("\n", " ").strip() for c in r]
            nonempty = [c for c in cells if c]
            if not nonempty:
                continue
            if nonempty[0].lower().startswith("tecnolog") and len(nonempty) > 1:
                tech = nonempty[1]
                continue
            lab = nonempty[0]
            if LABEL.match(lab):
                vals = [num(c) for c in nonempty[1:4]]
                rows.append([p, tech, lab, *vals, " | ".join(nonempty[1:4])])
with open("scratch/col_catalog_rows.csv", "w", newline="\n", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["pdf_page", "technology", "label", "v2024", "v2030", "v2050", "printed"])
    w.writerows(rows)
print(len(rows), "rows")
