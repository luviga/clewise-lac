"""Builds the summary tables quoted in REPORT from formula_cells.csv, formula_vs_compiled.csv,
downstream_follow.csv and affected_rows.csv. Writes step2_summary_*.csv, step4_summary.csv, step5_jamaica_rows.csv."""
import pandas as pd
fc = pd.read_csv("formula_cells.csv")
fc["column_kind"] = fc.column_header.astype(str).where(fc.year.isna(), "year column")
fc.groupby("country").agg(formula_cells=("cell", "size"), without_stored_value=("has_stored_value", lambda s: int((~s).sum())),
                           in_year_columns=("year", lambda s: int(s.notna().sum())),
                           own_eval_ok=("intended_method", lambda s: int(s.str.startswith("own").sum())),
                           own_eval_equals_stored=("own_eval_equals_stored", lambda s: int((s == True).sum()))).to_csv("step2_summary_country.csv")
fc.groupby(["country", "sheet"]).size().rename("formula_cells").to_csv("step2_summary_by_sheet.csv")
fc.groupby(["country", "column_kind", "parameter"], dropna=False).size().rename("formula_cells").to_csv("step2_summary_by_parameter.csv")
v = pd.read_csv("formula_vs_compiled.csv")
v["scenario"] = v.scenario.fillna("(none)")
v.groupby(["country", "scenario", "class"]).size().rename("cells").to_csv("step4_summary.csv")
a = pd.read_csv("affected_rows.csv")
def eq(x, y):
    try: return abs(float(x) - float(y)) <= 6e-5
    except (TypeError, ValueError): return False
a["bau_0_txt_equals_intended"] = [eq(x, y) for x, y in zip(a.bau_0_txt, a.intended_compiled)]
a["bau_final_0_txt_equals_intended"] = [eq(x, y) for x, y in zip(a.bau_final_0_txt, a.intended_compiled)]
s = a.groupby(["parameter", "tech", "projection_mode"]).agg(years=("year", lambda y: f"{y.min()}-{y.max()}"), n_years=("year", "size"),
        formula_cells=("is_formula_cell", "sum"), intended_min=("intended_compiled", "min"), intended_max=("intended_compiled", "max"),
        a2_bau_state=("a2_bau", lambda s: "empty" if s.isna().all() else "mixed"),
        b1_bau_state=("b1_bau", lambda s: "empty" if s.isna().all() else "mixed"),
        bau_0_txt_eq=("bau_0_txt_equals_intended", "sum"), bau_final_eq=("bau_final_0_txt_equals_intended", "sum"),
        bau_final_values=("bau_final_0_txt", lambda s: ";".join(sorted(set(map(str, s)))[:4])))
s.to_csv("step5_jamaica_rows.csv")
print(pd.read_csv("step2_summary_country.csv").to_string()); print(pd.read_csv("step4_summary.csv").to_string())
print(s.to_string())
