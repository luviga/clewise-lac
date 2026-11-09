"""Step 3.5: diesel, fuel oil, natural gas, 2025 and 2030, REF, six countries, in the workbook's own units
(USD/L or USD/MMBtu on Country_XXX sheets; USD/PJ on OSeMOSYS_VarCost). Read-only."""
import pandas as pd
WB = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5\LAC_Fuel_Price_Projections_2026_v2_audit.xlsx"
v = pd.read_excel(WB, sheet_name="OSeMOSYS_VarCost", header=3); v["xl_row"] = v.index + 5
out = []
for iso in ["CRI", "DOM", "ECU", "GTM", "HND", "JAM"]:
    for code in ["DSL", "HFO", "NGS"]:
        s = v[(v.ISO == iso) & (v["Fuel Code"] == code) & (v.Scenario == "REF")]
        if not len(s):
            out.append({"iso": iso, "fuel_code": code, "note": "not in workbook"}); continue
        r = s.iloc[0]; gj = r["GJ/unit"]
        unit = "USD/MMBtu" if code == "NGS" else "USD/L"
        rec = {"iso": iso, "fuel_code": code, "xl_row": int(r.xl_row), "GJ_per_unit": gj, "price_unit": unit}
        for y, col in ((2025, "M"), (2030, "R")):
            rec[f"{y}_USD_per_PJ"] = round(r[str(y)], 0)
            rec[f"{y}_{unit.replace('/', '_per_')}"] = round(r[str(y)] * gj / 1e6, 4)
            rec[f"{y}_cell"] = f"OSeMOSYS_VarCost!{col}{int(r.xl_row)}"
        out.append(rec)
df = pd.DataFrame(out); df.to_csv("step3_5_dsl_hfo_ngs_REF.csv", index=False); print(df.to_string())
