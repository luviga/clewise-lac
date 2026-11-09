"""Step 5: build fuel_plan.csv from the six plan manifests (tool output), add the workbook cell each
planned value came from, the current A-O value, and the value the model last compiled
(A2_Output_Params/BAU/VariableCost.csv, read-only). Also writes plan_summary.csv, unit_risks.csv,
gap_rows.csv and dsl_hfo_ngs_2025_2030.csv. Read-only on model files."""
import csv, os
import pandas as pd
from openpyxl.utils import get_column_letter
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.join(ROOT, r"_LAC_HUB\fuel_check_20261108T223320Z")
MODEL = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
         "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
         "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
# OSeMOSYS_VarCost: header row 4, 2018 in column F (6) ... 2050 in AL (38)
wbv = pd.read_excel(os.path.join(ROOT, "LAC_Fuel_Price_Projections_2026_v2_audit.xlsx"), sheet_name="OSeMOSYS_VarCost", header=3)
def wb_cell(src_row, year):
    if pd.isna(src_row) or src_row == "": return "", ""
    src_row = int(src_row)
    r = wbv.iloc[src_row - 5]
    avail = [y for y in range(2018, 2051) if isinstance(r[str(y)], (int, float)) and not pd.isna(r[str(y)])]
    note = ""
    y = year
    if year > max(avail): y = max(avail); note = f"held flat from {y}"
    elif year < min(avail): y = min(avail); note = f"held flat back from {y}"
    return f"OSeMOSYS_VarCost!{get_column_letter(6 + y - 2018)}{src_row}", note
def is_fuel_supply(tech):
    t = str(tech).upper(); return t.startswith(("DIST_", "IMP"))
def real(v):
    return pd.notna(v) and abs(v) > 1e-12 and abs(v - 1) > 1e-12
frames = []
for c, mdir in MODEL.items():
    m = pd.read_csv(os.path.join(OUT, f"plan_{c}", "manifest.csv"), encoding="utf-8-sig")
    a2 = pd.read_csv(os.path.join(ROOT, mdir, r"A2_Output_Params\BAU\VariableCost.csv"))
    a2 = a2[a2.MODE_OF_OPERATION == 1].set_index(["TECHNOLOGY", "YEAR"])["Value"]
    a2 = a2[~a2.index.duplicated()]
    for _, r in m.iterrows():
        cell, note = wb_cell(r.source_row_index, int(r.year)) if r.source_kind == "fuel_workbook" else ("", "")
        cur = pd.to_numeric(r.old_value, errors="coerce"); new = float(r.new_value)
        eff = a2.get((r.tech, int(r.year)), float("nan")) if r.parameter == "VariableCost" else float("nan")
        frames.append({
            "country": c, "sheet": r.sheet, "ao_row": r.row_index, "tech": r.tech, "tech_name": r.tech_name,
            "parameter": r.parameter, "row_class": ("fuel_supply" if is_fuel_supply(r.tech) and r.parameter == "VariableCost"
                         else "refinery" if str(r.tech).upper().startswith("REF_") else "extraction" if str(r.tech).upper().startswith("EXTT_")
                         else "other"),
            "year": int(r.year), "current_ao_value": "" if pd.isna(cur) else cur,
            "current_model_value_A2_BAU": "" if pd.isna(eff) else eff, "planned_value": new,
            "ratio_planned_to_current_ao": round(new / cur, 4) if real(cur) else "",
            "ratio_planned_to_model_A2_BAU": round(new / eff, 4) if real(eff) else "",
            "source_kind": r.source_kind, "fuel_code": r.fuel_code if pd.notna(r.fuel_code) else "",
            "workbook_cell": cell, "workbook_cell_note": note,
            "internal_source_if_not_workbook": "" if r.source_kind == "fuel_workbook" else f"{os.path.relpath(r.source_path, ROOT)}!{r.source_sheet} row {r.source_row_index}",
            "unit_conversion": r.unit_conversion, "projection_mode_old": r.projection_mode_old if pd.notna(r.projection_mode_old) else "",
            "projection_mode_new": r.projection_mode_new})
plan = pd.DataFrame(frames)
plan.to_csv(os.path.join(OUT, "fuel_plan.csv"), index=False)
# summary per country
s = plan.groupby(["country", "source_kind", "row_class", "parameter"]).agg(cells=("year", "size"), rows=("tech", lambda x: x.nunique()),
        techs=("tech", lambda x: " ".join(sorted(set(x))))).reset_index()
s.to_csv(os.path.join(OUT, "plan_summary.csv"), index=False)
# unit risks: ratio > 3 or < 1/3 where current is a real price
def risk(df, col):
    v = pd.to_numeric(df[col], errors="coerce")
    return df[(v > 3) | (v < 1/3)]
ur = pd.concat([risk(plan, "ratio_planned_to_current_ao").assign(basis="A-O cell"),
                risk(plan, "ratio_planned_to_model_A2_BAU").assign(basis="A2_Output_Params BAU")])
ur.to_csv(os.path.join(OUT, "unit_risks.csv"), index=False)
# DSL / HFO / NGS 2025 & 2030
want = {"DSL": ("DIST_DSL", "IMPPURDSL"), "HFO": ("DIST_FOI", "IMPFOI"), "NGS": ("DIST_NGS", "IMPNGS")}
ao = pd.read_csv(os.path.join(OUT, "ao_varcost_rows.csv"))
rows = []
for c, mdir in MODEL.items():
    a2 = pd.read_csv(os.path.join(ROOT, mdir, r"A2_Output_Params\BAU\VariableCost.csv"))
    a2 = a2[a2.MODE_OF_OPERATION == 1]
    for fc, techs in want.items():
        t = next((t for t in techs if ((ao.country == c) & (ao.tech == t)).any()), None)
        if t is None:
            rows.append({"country": c, "fuel": fc, "tech": "(no row)"}); continue
        for y in (2025, 2030):
            a = ao[(ao.country == c) & (ao.tech == t)].iloc[0]
            p = plan[(plan.country == c) & (plan.tech == t) & (plan.year == y) & (plan.parameter == "VariableCost")]
            e = a2[(a2.TECHNOLOGY == t) & (a2.YEAR == y)].Value
            rows.append({"country": c, "fuel": fc, "tech": t, "year": y,
                         "current_ao_value": a[f"v{y}"] if pd.notna(a[f"v{y}"]) else "",
                         "current_model_value_A2_BAU": round(float(e.iloc[0]), 4) if len(e) else "",
                         "planned_value": round(float(p.planned_value.iloc[0]), 4) if len(p) else "(no change planned)",
                         "planned_source": p.source_kind.iloc[0] if len(p) else "", "workbook_cell": p.workbook_cell.iloc[0] if len(p) else ""})
pd.DataFrame(rows).to_csv(os.path.join(OUT, "dsl_hfo_ngs_2025_2030.csv"), index=False)
# gap rows: fuel supply rows (DIST_/IMP*) VariableCost that are empty/all-0/all-1 today, and whether the plan fills them
g = ao[(ao.fuel_supply_prefix == "YES") & (ao.tech.str.upper().str.startswith(("DIST_", "IMP"))) &
       ((ao["empty"] == "YES") | (ao["all_zero"] == "YES") | (ao["all_one"] == "YES"))].copy()
g["state_today"] = g.apply(lambda r: "empty" if r["empty"] == "YES" else "all 0" if r["all_zero"] == "YES" else "all 1", axis=1)
def fill(r):
    p = plan[(plan.country == r.country) & (plan.tech == r.tech) & (plan.parameter == "VariableCost")]
    if not len(p): return "NOT FILLED (left as today)"
    return f"filled from {p.source_kind.iloc[0]} ({len(p)} cells)"
g["plan_result"] = g.apply(fill, axis=1)
g[["country", "sheet", "row", "tech", "tech_name", "unit", "state_today", "plan_result"]].to_csv(os.path.join(OUT, "gap_rows.csv"), index=False)
print(len(plan), "plan rows;", len(ur), "unit-risk rows;", len(g), "gap rows")
