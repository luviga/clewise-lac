"""Step 5 (read-only): read diesel and fuel oil supply VariableCost rows from the six A-O workbooks.
Opens each workbook with openpyxl read_only=True, data_only=True (cached values). Never saves.
Writes ao_dsl_foi_2025.csv. Run: py -I read_ao_2025.py <output_folder>
"""
import sys, os, csv
import openpyxl

OUT = sys.argv[1]
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
WB = {
 "CostaRica": r"CostaRica\CR_ENERGY\t1_confection\A1_Outputs\A-O_Parametrization.xlsx",
 "DominicanRepublic": r"DominicanRepublic\RD_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 "Ecuador": r"Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization.xlsx",
 "Guatemala": r"Guatemala\GUA_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 "Honduras": r"Honduras\HON_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 "Jamaica": r"Jamaica\JAM_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
}
TECHS = {"IMPPURDSL": "DSL", "IMPFOI": "FOI", "DIST_DSL": "DSL", "DIST_FOI": "FOI"}

rows_out = []
for country, rel in WB.items():
    wb = openpyxl.load_workbook(os.path.join(ROOT, rel), read_only=True, data_only=True)
    ws = wb["Primary Techs"]
    rows = list(ws.iter_rows(values_only=True))
    # find header row with years
    hdr_i = None
    for i, r in enumerate(rows[:10]):
        if r and any(isinstance(v, (int, float)) and 2015 <= v <= 2060 for v in r if v is not None):
            hdr_i = i
            break
    hdr = rows[hdr_i]
    ycols = {int(v): j for j, v in enumerate(hdr) if isinstance(v, (int, float)) and 2015 <= v <= 2060}
    labels = [str(v) for v in hdr]
    for i, r in enumerate(rows):
        if r is None:
            continue
        tech = next((str(v).strip() for v in r[:6] if v is not None and str(v).strip() in TECHS), None)
        if tech is None:
            continue
        # only the VariableCost parameter block: find parameter label in the row
        param = next((str(v) for v in r[:12] if v is not None and "Variable" in str(v)), None)
        if param is None:
            continue
        mode = next((str(v) for v in r[:12] if v is not None and str(v) in ("User defined", "Flat", "Percent growth of incomplete years", "Interpolate", "EMPTY")), "")
        unit = next((str(v) for v in r[:12] if v is not None and "PJ" in str(v)), "")
        vals = {y: r[j] for y, j in ycols.items() if j < len(r)}
        given = {y: v for y, v in vals.items() if isinstance(v, (int, float))}
        v2025 = vals.get(2025)
        how = "stored value"
        if not isinstance(v2025, (int, float)):
            ys = sorted(given)
            if mode == "Flat" and ys:
                v2025, how = given[ys[0]], f"Flat mode: value of {ys[0]} held"
            elif len(ys) >= 2:
                lo = max([y for y in ys if y <= 2025], default=None)
                hi = min([y for y in ys if y >= 2025], default=None)
                if lo is not None and hi is not None and hi != lo:
                    g = (given[hi] / given[lo]) ** (1 / (hi - lo))
                    v2025, how = given[lo] * g ** (2025 - lo), f"{mode}: geometric interpolation between {lo} and {hi}"
                elif lo is not None:
                    v2025, how = given[lo], f"{mode}: only earlier value {lo}; held (tool may extrapolate differently)"
        rows_out.append(dict(country=country, workbook=rel, sheet="Primary Techs", excel_row=i + 1, tech=tech,
                             fuel=TECHS[tech], parameter=param, unit=unit, projection_mode=mode,
                             given_years=" ".join(f"{y}:{round(v, 4)}" for y, v in sorted(given.items())[:4]) + (" ..." if len(given) > 4 else ""),
                             v2025=None if v2025 is None else round(float(v2025), 4), v2025_basis=how))
    wb.close()

with open(os.path.join(OUT, "ao_dsl_foi_2025.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    w.writeheader()
    w.writerows(rows_out)
for r in rows_out:
    print(r["country"], r["tech"], r["parameter"], r["unit"], r["projection_mode"], r["v2025"], "|", r["v2025_basis"], "|", r["given_years"])
