"""List every VariableCost row in each main energy A-O_Parametrization.xlsx (read-only),
flag fuel supply rows (DIST_*, IMP*, EXTT_*, REF_*), count formula cells per sheet.
Writes ao_varcost_rows.csv and ao_formula_cells.csv."""
import csv, re, sys
from openpyxl import load_workbook
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
AO = {
 "CostaRica": r"CostaRica\CR_ENERGY\t1_confection\A1_Outputs\A-O_Parametrization.xlsx",
 "DominicanRepublic": r"DominicanRepublic\RD_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 "Ecuador": r"Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization.xlsx",
 "Guatemala": r"Guatemala\GUA_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 "Honduras": r"Honduras\HON_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 "Jamaica": r"Jamaica\JAM_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
}
out = sys.argv[1]
rows_out, form_out = [], []
def fuel_supply(tech):
    t = tech.upper()
    return t.startswith(("DIST_", "IMP", "EXTT_", "REF_"))
for c, rel in AO.items():
    p = ROOT + "\\" + rel
    wf = load_workbook(p, data_only=False)
    wv = load_workbook(p, data_only=True)
    for ws in wf.worksheets:
        vs = wv[ws.title]
        nform = 0; vc_form = 0
        hdr = None
        for r in range(1, 9):
            vals = [ws.cell(r, k).value for k in range(1, min(ws.max_column, 300) + 1)]
            norm = {str(v).strip().lower().replace("_", ".") for v in vals if v is not None}
            if "tech" in norm and "parameter" in norm:
                hdr = r; break
        cols = {}
        if hdr:
            for k in range(1, min(ws.max_column, 300) + 1):
                v = ws.cell(hdr, k).value
                if v is None: continue
                s = str(v).strip()
                cols[int(s) if re.fullmatch(r"\d{4}", s) else s] = k
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == 'f': nform += 1
        if hdr and "Tech" in cols and "Parameter" in cols:
            years = sorted(k for k in cols if isinstance(k, int))
            for r in range(hdr + 1, ws.max_row + 1):
                tech = vs.cell(r, cols["Tech"]).value
                par = vs.cell(r, cols["Parameter"]).value
                if not tech or str(par).strip() != "VariableCost": continue
                tech = str(tech).strip()
                rowform = sum(1 for y in years if ws.cell(r, cols[y]).data_type == 'f')
                vc_form += rowform
                vals = {y: vs.cell(r, cols[y]).value for y in years}
                num = [v for v in vals.values() if isinstance(v, (int, float))]
                first_y = next((y for y in years if isinstance(vals[y], (int, float))), "")
                rows_out.append({
                    "country": c, "sheet": ws.title, "row": r, "tech": tech,
                    "tech_name": vs.cell(r, cols.get("Tech.Name", cols["Tech"])).value,
                    "unit": vs.cell(r, cols["Unit"]).value if "Unit" in cols else "",
                    "projection_mode": vs.cell(r, cols["Projection.Mode"]).value if "Projection.Mode" in cols else "",
                    "fuel_supply_prefix": "YES" if fuel_supply(tech) else "",
                    "first_year": years[0] if years else "", "last_year": years[-1] if years else "",
                    "n_year_cols": len(years), "n_numeric": len(num), "formula_cells_in_row": rowform,
                    "first_numeric_year": first_y, "first_numeric_value": vals.get(first_y, "") if first_y != "" else "",
                    "v2025": vals.get(2025, ""), "v2030": vals.get(2030, ""), "v2050": vals.get(2050, ""),
                    "all_zero": "YES" if num and all(abs(v) < 1e-12 for v in num) else "",
                    "all_one": "YES" if num and all(abs(v - 1) < 1e-12 for v in num) else "",
                    "empty": "YES" if not num else "",
                })
        form_out.append({"country": c, "sheet": ws.title, "max_row": ws.max_row, "max_col": ws.max_column,
                         "header_row": hdr or "", "formula_cells_sheet": nform, "formula_cells_in_VariableCost_rows": vc_form})
with open(out + "/ao_varcost_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0])); w.writeheader(); w.writerows(rows_out)
with open(out + "/ao_formula_cells.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(form_out[0])); w.writeheader(); w.writerows(form_out)
print(len(rows_out), "VariableCost rows")
