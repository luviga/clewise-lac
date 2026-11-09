"""Step 5. Row-level effect: for every A-O row (any country) that has a formula cell in a year column, compute
with the A2 replica from step4_compare.py the full compiled row from intended values and compare it, year by year,
with A2_Output_Params/BAU (and B1_Output_Params/BAU and the BAU data file used by Stage 3).
A Flat row whose base-year cell is a formula loses every year, so the effect can exceed the formula count.
Writes affected_rows.csv (one line per row and year with a mismatch) and affected_rows_summary.csv. Read-only."""
import os, re, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "step4_compare.py"), encoding="utf-8").read()
exec(src[:src.index("fc = pd.read_csv")])          # ROOT, ENERGY, NOT_WRITTEN, isnan, r4, a2_row, eq4
d4b = open(os.path.join(HERE, "step4b_downstream.py"), encoding="utf-8").read()
exec(d4b[d4b.index("def parse_gmpl"):d4b.index("fvc = pd.read_csv")])   # parse_gmpl

fc = pd.read_csv(os.path.join(HERE, "formula_cells.csv"), dtype={"intended_value": object})
fc = fc[fc.year.notna()]
detail, summ = [], []
for c, d in ENERGY.items():
    g = fc[fc.country == c]
    if g.empty: continue
    base = os.path.join(ROOT, d)
    x = pd.ExcelFile(os.path.join(base, "A1_Outputs", "A-O_Parametrization.xlsx"))
    a2 = {}; b1 = {}
    datafile = os.path.join(base, "Executables", "BAU_FINAL_0", "BAU_FINAL_0.txt")
    gm = parse_gmpl(datafile, set(g.parameter.dropna()))
    gm0 = parse_gmpl(os.path.join(base, "Executables", "BAU_0", "BAU_0.txt"), set(g.parameter.dropna()))
    for sh, gs in g.groupby("sheet"):
        df = x.parse(sh)
        if sh == x.sheet_names[0] or "Tech" not in df.columns: continue
        years = [col for col in df.columns if isinstance(col, (int, np.integer))]
        for r_idx, gr in gs.groupby("row"):
            row = df.loc[r_idx - 2]
            tech, param, mode = row.get("Tech"), row.get("Parameter"), row.get("Projection.Mode")
            pp = row.get("Projection.Parameter")
            try: pp = float(pp)
            except (TypeError, ValueError): pass
            read_vals = [float(row[y]) if (not isinstance(row[y], str) and not isnan(row[y])) else float('nan') for y in years]
            int_vals = list(read_vals)
            for _, ff in gr.iterrows():
                k = years.index(int(ff.year))
                if isnan(read_vals[k]):
                    try: int_vals[k] = float(ff.intended_value)
                    except (TypeError, ValueError): pass
            e_int = a2_row(int_vals, mode, pp, years)
            if e_int is None or e_int == 'unsupported' or sh == "Vehicle Techs": continue
            for folder, cache in (("A2_Output_Params", a2), ("B1_Output_Params", b1)):
                p = os.path.join(base, folder, "BAU", f"{param}.csv")
                if p not in cache: cache[p] = pd.read_csv(p, dtype={"TECHNOLOGY": str}) if os.path.exists(p) else None
            A = a2[os.path.join(base, "A2_Output_Params", "BAU", f"{param}.csv")]
            B = b1[os.path.join(base, "B1_Output_Params", "BAU", f"{param}.csv")]
            A = A[A.TECHNOLOGY == tech] if A is not None else None
            B = B[B.TECHNOLOGY == tech] if B is not None else None
            n_mis = n_empty = 0
            for k, y in enumerate(years):
                av = A[pd.to_numeric(A.YEAR) == y].Value.tolist() if A is not None else []
                if not av: continue
                if not any(eq4(v, e_int[k]) for v in av):
                    n_mis += 1; n_empty += all(isnan(v) for v in av)
                    bv = B[pd.to_numeric(B.YEAR) == y].Value.tolist() if B is not None else []
                    P = gm.get(param, {"data": {}, "default": None}); P0 = gm0.get(param, {"data": {}, "default": None})
                    dv = P["data"].get((tech, y)); dv0 = P0["data"].get((tech, y))
                    detail.append({"country": c, "sheet": sh, "tech": tech, "parameter": param, "projection_mode": mode, "year": y,
                                   "is_formula_cell": any(int(v) == y for v in gr.year), "intended_compiled": e_int[k],
                                   "a2_bau": ";".join("" if isnan(v) else str(v) for v in av),
                                   "b1_bau": ";".join("" if isnan(v) else str(v) for v in bv) if bv else "no row",
                                   "bau_0_txt": dv0 if dv0 is not None else f"default {P0['default']}",
                                   "bau_final_0_txt": dv if dv is not None else f"default {P['default']}"})
            summ.append({"country": c, "sheet": sh, "tech": tech, "parameter": param, "projection_mode": mode,
                         "formula_cells_in_row": len(gr), "years_compiled_wrong_in_A2_BAU": n_mis, "of_which_empty": n_empty})
D = pd.DataFrame(detail); S = pd.DataFrame(summ)
D.to_csv(os.path.join(HERE, "affected_rows.csv"), index=False); S.to_csv(os.path.join(HERE, "affected_rows_summary.csv"), index=False)
print(S[S.years_compiled_wrong_in_A2_BAU > 0].to_string())
print(S.groupby("country")[["formula_cells_in_row", "years_compiled_wrong_in_A2_BAU", "of_which_empty"]].sum())
