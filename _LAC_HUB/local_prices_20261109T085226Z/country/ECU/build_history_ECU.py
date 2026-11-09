"""Build history_ECU.csv (2018-2025, nominal) from the BCE Cifras del Sector Petrolero annual sums.

Usage: py -I build_history_ECU.py <bce_annual_2018_2025.csv> <out_csv>
The input is the output of bce_annual.py (one publisher, one workbook: ECU-002).
"""
import csv
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src, out = sys.argv[1], sys.argv[2]
GAL_T = {"GSL": 357, "DSL": 304, "FOI": 278, "LPG": 489}
NCV = {"GSL": 44.3, "DSL": 43.0, "FOI": 40.4, "LPG": 47.3, "CRU": 42.3}
SPEC = {
    "crude_export_total": ("CRU", "DIST_CRU", "export FOB", "FOB export value, no taxes", "UN_BBL_PER_T_CRU;IPCC_NCV_CRU",
                           "All Ecuadorian crude exports (public, private, Ministry); BCE provisional figures."),
    "fo6_export": ("FOI", "DIST_FOI", "export FOB", "FOB export value, no taxes", "USGAL_PER_BBL;UN_GAL_PER_T_FOI;IPCC_NCV_FOI",
                   "Fuel Oil No. 6 exports of EP Petroecuador; value = monthly volume x monthly price."),
    "diesel_import": ("DSL", "DIST_DSL", "import CIF", "EP Petroecuador import cost (DPU basis), excludes VAT and insurance", "USGAL_PER_BBL;UN_GAL_PER_T_DSL;IPCC_NCV_DSL",
                      "Diesel imports by EP Petroecuador; BCE monthly cost and volume equal EP Petroecuador figures in 2024."),
    "nafta_import": ("GSL", "DIST_GSL", "import CIF", "EP Petroecuador import cost (DPU basis), excludes VAT and insurance", "USGAL_PER_BBL;UN_GAL_PER_T_GSL;IPCC_NCV_GSL",
                     "Nafta de alto octano imports (blendstock for Extra and Ecopais)."),
    "glp_import": ("LPG", "DIST_LPG", "import CIF", "EP Petroecuador import cost (DPU basis), excludes VAT and insurance", "USGAL_PER_BBL;UN_GAL_PER_T_LPG;IPCC_NCV_LPG",
                   "LPG imports by EP Petroecuador, volume in barrels."),
}
HDR = ["country", "fuel", "model_code", "price_point", "year", "fob", "freight", "insurance", "port", "importer_terminal_margin",
       "wholesale_margin", "inland_freight", "retail_margin", "price_as_published", "currency", "unit", "period", "months_covered",
       "tax_treatment", "calorific_basis", "exchange_rate", "exchange_rate_constant", "conversion_constants", "value_usd_per_gj",
       "evidence_class", "source_id", "page_or_table", "downloaded_file", "derivation", "notes"]
rows = []
with open(src, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["series"] not in SPEC:
            continue
        fuel, code, pp, tax, consts, note = SPEC[r["series"]]
        V, X, p = float(r["volume_kbbl"]), float(r["value_kusd"]), float(r["usd_per_bbl"])
        if fuel == "CRU":
            gj = p * 7.32 / NCV["CRU"]
            conv = f"x 7.32 bbl/t (UN_BBL_PER_T_CRU) / 42.3 GJ/t (IPCC_NCV_CRU)"
        else:
            gj = p / 42 * GAL_T[fuel] / NCV[fuel]
            conv = f"/ 42 (USGAL_PER_BBL) x {GAL_T[fuel]} gal/t (UN_GAL_PER_T_{fuel}) / {NCV[fuel]} GJ/t (IPCC_NCV_{fuel})"
        rows.append(dict(country="Ecuador", fuel=fuel, model_code=code, price_point=pp, year=r["year"],
                         fob=(round(p, 4) if pp == "export FOB" else ""), freight="", insurance="", port="", importer_terminal_margin="",
                         wholesale_margin="", inland_freight="", retail_margin="", price_as_published=round(p, 4), currency="USD", unit="USD/bbl",
                         period=f"calendar year {r['year']}", months_covered=r["months"], tax_treatment=tax, calorific_basis="not stated",
                         exchange_rate="", exchange_rate_constant="", conversion_constants=consts, value_usd_per_gj=round(gj, 4),
                         evidence_class="local customs or statistics", source_id="ECU-002",
                         page_or_table=f"sheet Petroleo row {r['volume_row']} ({r['volume_label']}) and row {r['value_row']} ({r['value_label']}), columns {r['year']} ene to dic",
                         downloaded_file="ECU/BCE_SerieCifrasPetroleras.xlsx",
                         derivation=f"sum of monthly values {X:,.3f} thousand USD / sum of monthly volumes {V:,.3f} thousand bbl = {p:.4f} USD/bbl; {conv} = {gj:.4f} USD/GJ; scripts bce_annual.py and build_history_ECU.py",
                         notes=note + " Nominal USD."))
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=HDR)
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["fuel"], r["year"], r["price_as_published"], r["value_usd_per_gj"])
