"""Step 4. For every formula cell in formula_cells.csv, compare what A2 compiled with what A2 would compile
(a) from the intended value and (b) from an empty cell, using a replica of A2's per-row Projection.Mode logic
(A2_Compiler_Jamaica.py:514-602 and write rule at 792; same loop in A2_Compiler_Ecuador.py). Writes formula_vs_compiled.csv.
Read-only on all model files."""
import os, math, glob
import numpy as np, pandas as pd
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.dirname(os.path.abspath(__file__))
ENERGY = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
          "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
          "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
NOT_WRITTEN = ['EMPTY', 'Zero', '', None, 'According to demand']   # A2_Compiler_Jamaica.py:788


def isnan(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


def r4(v):
    """A2 rounds numpy float64 values read by pandas; numpy rounds halves to even (e.g. 0.41705 -> 0.417)."""
    return float(round(np.float64(v), 4))


def a2_row(vals, mode, pp, years):
    """Replica of A2's per-row logic for sheets other than the first. vals: list aligned with years
    (float or nan). Returns compiled values (rounded 4), None if A2 writes no row, 'unsupported' otherwise."""
    if not isinstance(mode, str) or mode in NOT_WRITTEN:
        return None
    n = len(years); raw = list(vals); new = list(vals)
    if mode == 'Flat':
        new = [r4(raw[0]) if not isnan(raw[0]) else float('nan')] * n
    elif mode == 'Percent growth of incomplete years':
        for y in range(n):
            if isnan(raw[y]):
                new[y] = r4(new[y - 1] * (1 + pp / 100))
    elif mode == 'User defined':
        new = [r4(v) if not isnan(v) else float('nan') for v in raw]
    elif mode == 'Interpolate to stated end value from projection parameter':
        df = list(raw); final = pp
        x_fill, xp, yp = [], [], []; fidx = 0; fval = None
        for y in range(n):
            v = df[y]
            if y != 0:
                vp = df[y - 1]
                if y > fidx and fidx != 0:
                    xp.append(y); yp.append(fval)
                if not isnan(v) and isnan(vp) and years[y] > final:
                    fidx = y; fval = df[y]; xp.append(y); yp.append(fval)
                if years[y] <= final and isnan(v):
                    xp.append(y); yp.append(vp); df[y] = vp
                if years[y] <= final and not isnan(v):
                    xp.append(y); yp.append(v)
                if years[y] > final and isnan(v) and fidx == 0:
                    x_fill.append(y)
            else:
                xp.append(y); yp.append(v)
        filled = list(np.interp(x_fill, xp, yp))
        out = []
        for c in range(n):
            if c in xp: out.append(float(yp[xp.index(c)]))
            elif c in x_fill: out.append(float(filled[x_fill.index(c)]))
            else: out.append(float('nan'))
        new = out
    else:
        return 'unsupported'
    return [r4(v) if not isnan(v) else float('nan') for v in new]


def eq4(a, b):
    if isnan(a) and isnan(b): return True
    if isnan(a) or isnan(b): return False
    return abs(float(a) - float(b)) <= 0.00005 + 1e-9 * abs(float(b))


fc = pd.read_csv(os.path.join(OUT, "formula_cells.csv"), dtype={"stored_value": object, "intended_value": object, "own_eval_value": object})
res = []
csv_cache = {}


def compiled_lookup(base, scen, param, tech, year):
    p = os.path.join(base, scen, f"{param}.csv")
    if p not in csv_cache:
        csv_cache[p] = pd.read_csv(p, dtype={"TECHNOLOGY": str}) if os.path.exists(p) else None
    d = csv_cache[p]
    if d is None: return None, "no file"
    m = d[(d["TECHNOLOGY"] == tech) & (pd.to_numeric(d["YEAR"], errors="coerce") == year)]
    return m["Value"].tolist(), f"{len(m)} rows"


KEEP = ["country", "sheet", "cell", "tech", "parameter", "projection_mode", "column_header", "year", "formula",
        "has_stored_value", "intended_value", "intended_method"]
for c, d in ENERGY.items():
    base = os.path.join(ROOT, d)
    x = pd.ExcelFile(os.path.join(base, "A1_Outputs", "A-O_Parametrization.xlsx"))   # what A2 reads
    sheets = {s: x.parse(s) for s in x.sheet_names}
    first_sheet = x.sheet_names[0]
    scen_dirs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(base, "A2_Output_Params", "*")) if os.path.isdir(p))
    g = fc[fc.country == c]
    for sh, gs in g.groupby("sheet"):
        df = sheets[sh]
        years = [col for col in df.columns if isinstance(col, (int, np.integer))]
        for r_idx, gr in gs.groupby("row"):
            n = r_idx - 2
            row = df.loc[n]
            for _, f in gr.iterrows():
                rec0 = {k: f[k] for k in KEEP}
                colh = str(f.column_header)
                if pd.isna(f.year):
                    if colh in ("Tech.ID", "Tech.Type", "Source / Assumption", "NOTAS"):
                        res.append({**rec0, "scenario": "", "class": "not checked",
                                    "detail": f"column {colh} is not read by A2 (no use of it in any energy A2_Compiler_*.py); no compiled counterpart"})
                        continue
                    if colh == "Tech":
                        mode = row.get("Projection.Mode")
                        if sh != first_sheet and (not isinstance(mode, str) or mode in NOT_WRITTEN):
                            res.append({**rec0, "scenario": "", "class": "not checked",
                                        "detail": f"Tech name cell; A2 reads it as {row.get('Tech')!r}, but Projection.Mode={mode!r} so A2 writes no row for it"})
                        else:
                            res.append({**rec0, "scenario": "", "class": "not checked",
                                        "detail": f"Tech name cell on a written row; A2 reads {row.get('Tech')!r}"})
                        continue
                    res.append({**rec0, "scenario": "", "class": "not checked", "detail": f"non-year column {colh}"})
                    continue
                yr = int(f.year); tech = row.get("Tech"); param = row.get("Parameter")
                if sh == first_sheet:
                    res.append({**rec0, "scenario": "", "class": "not checked", "detail": "first sheet holds no years"}); continue
                read_vals = [float(row[y]) if (not isinstance(row[y], str) and not isnan(row[y])) else float('nan') for y in years]
                int_vals = list(read_vals); blank_vals = list(read_vals)
                for _, ff in gr.iterrows():
                    if pd.isna(ff.year): continue
                    k = years.index(int(ff.year))
                    if isnan(read_vals[k]):   # use the stored value A2 saw where one exists (avoids 5th-decimal rounding ties)
                        try: int_vals[k] = float(ff.intended_value)
                        except (TypeError, ValueError): int_vals[k] = float('nan')
                    blank_vals[k] = float('nan')
                mode = row.get("Projection.Mode"); pp = row.get("Projection.Parameter")
                try: pp = float(pp)
                except (TypeError, ValueError): pass
                e_int = a2_row(int_vals, mode, pp, years); e_blank = a2_row(blank_vals, mode, pp, years)
                k = years.index(yr)
                if e_int is None:
                    res.append({**rec0, "scenario": "", "class": "not checked", "detail": f"Projection.Mode={mode!r}: A2 writes no row from this A-O row"}); continue
                if e_int == 'unsupported':
                    res.append({**rec0, "scenario": "", "class": "not checked", "detail": f"Projection.Mode={mode!r} not replicated"}); continue
                vi, vb = e_int[k], e_blank[k]
                for scen in scen_dirs:
                    vals, info = compiled_lookup(os.path.join(base, "A2_Output_Params"), scen, param, tech, yr)
                    rec = {**rec0, "scenario": scen, "a2_from_intended": vi, "a2_from_blank": vb,
                           "compiled_values": "" if vals is None else ";".join("" if isnan(v) else str(v) for v in vals),
                           "compiled_match": info}
                    if not vals:
                        rec.update({"class": "not checked", "detail": f"no matching compiled row ({info})"}); res.append(rec); continue
                    ok = any(eq4(v, vi) for v in vals); bl = any(eq4(v, vb) for v in vals)
                    if ok:
                        cls = "ok"; det = "compiled equals intended (4 dp)" + ("; blank would give the same" if eq4(vi, vb) else "")
                    elif bl:
                        cls = "blank-filled"
                        det = ("A2 wrote the row with an empty Value (round(NaN) stays NaN); B1 skips rows with an empty Value"
                               if isnan(vb) else f"A2 filled the empty cell by its '{mode}' rule")
                    else:
                        cls = "different"; det = "compiled matches neither intended nor blank result"
                        if sh == "Vehicle Techs":
                            cls, det = "not checked", "Vehicle Techs: A2 unit conversion not replicated; compiled differs from replica"
                    rec.update({"class": cls, "detail": det}); res.append(rec)
out = pd.DataFrame(res)
out.to_csv(os.path.join(OUT, "formula_vs_compiled.csv"), index=False)
print(out.groupby(["country", "scenario", "class"]).size().to_string())
