"""Gate 4: every accepted value is found as printed in its downloaded file at the recorded page.
The page text (PyMuPDF) is normalised by removing whitespace and table separators; the check
finds the row label and then the printed value(s) in order within 220 characters after it."""
import json, re, sys
import fitz
import pandas as pd

RV = pd.read_csv("regional_values.csv").set_index("value_id")
SRC = pd.read_csv("scratch/sources_regional.csv").set_index("source_id")
ACC = json.load(open("scratch/accepted.json"))

def norm(s):
    return re.sub(r"[\s|    ]+", "", s)

# label to anchor the search, per (source, page, technology substring, component)
LABELS = [
    ("REG-005", 153, "Biomasa", "capital", "BiomasaGenéricos"), ("REG-005", 153, "Solar Genericos (10 MW)", "capital", "SolarGenéricos(3)"),
    ("REG-005", 153, "Eolico Genericos", "capital", "EolicoGenéricos"), ("REG-005", 151, "Geotermico", "fixed_om", "GeotérmicoGenéricos(3)"),
    ("REG-005", 151, "Solar Genericos (10 MW)", "fixed_om", "SolarGenéricos(3)"), ("REG-005", 151, "Eolico Genericos", "fixed_om", "EólicoGenéricos(3)"),
    ("REG-005", 151, "Biomasa", "fixed_om", "BiomasaGenéricos(3)"),
    ("REG-006", 46, "bunker/diesel", "variable_om", "Motordecombustióninternaagasnatural/búnker/diésel"),
    ("REG-006", 46, "bunker/diesel", "fixed_om", "Motordecombustióninternaagasnatural/búnker/diésel"),
    ("REG-006", 46, "embalse", "capital", "Hidroeléctricadeembalse"), ("REG-006", 46, "Geotermica", "capital", "Geotérmica"),
    ("REG-006", 46, "pasada", "capital", "Hidroeléctricadepasada"), ("REG-006", 46, "ciclo combinado a gas natural", "capital", "Turbinadegasenciclocombinadoagasnatural"),
    ("REG-006", 46, "Solar fotovoltaica, 50", "fixed_om", "Solarfotovoltaica"), ("REG-006", 46, "con bateria (30%)", "capital", "Solarfotovoltaicaconbatería(30%)"),
    ("REG-006", 46, "con bateria (30%)", "fixed_om", "Solarfotovoltaicaconbatería(30%)"),
    ("REG-003", 62, "Utility-scale solar PV", "capital", "CentralAmericaandtheCaribbean"),
    ("REG-002", 71, "Onshore wind", "capital", "CentralAmericaandtheCaribbean*"),
    ("REG-014", 64, "industrial", "capital", "Inversiónespecífica,sistematotal(MUSD/MWe)"), ("REG-014", 64, "industrial", "fixed_om", "O&Mfijas(USD/MWe/año)"),
    ("REG-014", 92, "Peque", "capital", "Inversiónespecífica,sistematotal(millones"), ("REG-014", 92, "Peque", "fixed_om", "O&Mfijas(USD/MWe/año)"),
    ("REG-014", 316, "Gran escala", "capital", "Inversióntotal(MUSD/MW)"), ("REG-014", 315, "Gran escala", "fixed_om", "O&Mfijas(USD/MWe/año)"),
]
def label_for(r):
    for sid, p, sub, comp, lab in LABELS:
        if r["source_id"] == sid and int(r["pdf_page"]) == p and sub in r["technology_as_printed"] and r["cost_component"] == comp:
            return lab
    raise KeyError(r.name)

rows, cache = [], {}
for key, a in ACC.items():
    country, tech, param = key.split("|")
    for vid in a["picks"]:
        r = RV.loc[vid]
        f = "downloads/" + SRC.loc[r["source_id"], "downloaded_file"]
        p = int(r["pdf_page"])
        if (f, p) not in cache:
            cache[(f, p)] = norm(fitz.open(f)[p - 1].get_text())
        T = cache[(f, p)]
        lab = label_for(r)
        printed = norm(str(r["check_string"]))
        if r["source_id"] == "REG-014" and r["cost_component"] == "fixed_om" and p == 64:
            printed = {"15.00": "15.000", "12.90": "12.900", "10.90": "10.900"}[printed]  # third digit sits in a separate text cell
        if r["source_id"] in ("REG-002", "REG-003"):
            printed = re.sub(r"^[^0-9]*", "", printed)  # row values only; the region name is the label
        found, where = False, ""
        for m in re.finditer(re.escape(lab), T):
            seg = T[m.end(): m.end() + 220]
            if printed in seg:
                found, where = True, f"after '{lab}' at offset {seg.index(printed)}"
                break
        rows.append({"country": country, "technology": tech, "parameter": param, "value_id": vid, "source_id": r["source_id"],
                     "file": SRC.loc[r["source_id"], "downloaded_file"], "pdf_page": p, "locator": r["page_or_table"],
                     "printed_value_searched": printed, "value": r["value"], "unit": r["unit"], "value_year": r["value_year"],
                     "found": "yes" if found else "no", "where": where})
out = pd.DataFrame(rows)
out.to_csv("value_checks.csv", index=False, lineterminator="\n")
print(out.found.value_counts().to_dict())
print(out[out.found == "no"].to_string())
