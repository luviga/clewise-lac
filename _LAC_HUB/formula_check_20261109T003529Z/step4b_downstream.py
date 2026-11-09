"""Step 4 follow-up. For every blank-filled or different cell in formula_vs_compiled.csv, look up the same
(parameter, technology, year) in B1_Output_Params/<SCEN>/<param>.csv and in the GMPL data files
Executables/<SCEN>_FINAL_0/<SCEN>_FINAL_0.txt (else <SCEN>_0/<SCEN>_0.txt) for BAU, NDCNEW, LTSNEW.
Also records, per country, the modification times of the A-O workbook, A2_Output_Params, B1_Output_Params
and each data file. Writes downstream_follow.csv and timeline.csv. Read-only."""
import os, re, math, datetime
import pandas as pd
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
OUT = os.path.dirname(os.path.abspath(__file__))
ENERGY = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
          "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
          "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
SCENS = ["BAU", "NDCNEW", "LTSNEW"]
ts = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def isnan(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


def parse_gmpl(path, wanted):
    """Return {param: {"default": d, "data": {(tech, year): value}}} for params in wanted.
    Handles the B1 layout: 'param P default d :=', then '[R,*,*]:' or '[R,T,*,*]:' slice headers,
    a year header line ending ':=', and data lines 'label v1 v2 ...'."""
    out = {}
    cur = None; sl = None; years = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            m = re.match(r"param\s+(\w+)\s+default\s+(\S+)\s*:?=?", s)
            if s.startswith("param "):
                p = m.group(1) if m else s.split()[1]
                cur = p if p in wanted else None
                if cur: out[cur] = {"default": float(m.group(2)) if m else None, "data": {}}
                sl = None; years = None; continue
            if cur is None: continue
            if s == ";": cur = None; continue
            if s.startswith("[") and s.endswith(":"):
                sl = [x.strip() for x in s[1:s.index("]")].split(",")]; years = None; continue
            if s.endswith(":="):
                toks = s[:-2].split()
                if toks and all(t.isdigit() for t in toks): years = [int(t) for t in toks]
                continue
            if years and s:
                toks = s.split()
                label, vals = toks[0], toks[1:]
                fixed = [x for x in (sl or []) if x != "*"]
                tech = fixed[1] if len(fixed) >= 2 else label
                for y, v in zip(years, vals):
                    try: out[cur]["data"][(tech, y)] = float(v)
                    except ValueError: pass
    return out


fvc = pd.read_csv(os.path.join(OUT, "formula_vs_compiled.csv"))
bad = fvc[fvc["class"].isin(["blank-filled", "different"]) & fvc.scenario.isin(SCENS)].copy()
rows, tl = [], []
for c, d in ENERGY.items():
    base = os.path.join(ROOT, d)
    ao = os.path.join(base, "A1_Outputs", "A-O_Parametrization.xlsx")
    tl.append({"country": c, "item": "A-O workbook", "path": os.path.relpath(ao, ROOT), "mtime_utc": ts(os.stat(ao).st_mtime)})
    for sub in ["A2_Output_Params", "B1_Output_Params"]:
        for scen in sorted(os.listdir(os.path.join(base, sub))):
            p = os.path.join(base, sub, scen)
            if not os.path.isdir(p): continue
            mt = [os.stat(os.path.join(p, f)).st_mtime for f in os.listdir(p)]
            tl.append({"country": c, "item": f"{sub}/{scen} newest file", "path": os.path.relpath(p, ROOT), "mtime_utc": ts(max(mt)) if mt else ""})
    files = {}
    for scen in SCENS:
        fin = os.path.join(base, "Executables", f"{scen}_FINAL_0", f"{scen}_FINAL_0.txt")
        raw = os.path.join(base, "Executables", f"{scen}_0", f"{scen}_0.txt")
        for lab, p in [("FINAL", fin), ("_0", raw)]:
            if os.path.exists(p): tl.append({"country": c, "item": f"Executables {scen}{'_FINAL' if lab == 'FINAL' else ''}_0.txt", "path": os.path.relpath(p, ROOT), "mtime_utc": ts(os.stat(p).st_mtime)})
        files[scen] = fin if os.path.exists(fin) else raw
    g = bad[bad.country == c]
    if g.empty: continue
    wanted = set(g.parameter)
    gm = {scen: parse_gmpl(files[scen], wanted) for scen in SCENS}
    gm0 = {scen: parse_gmpl(os.path.join(base, "Executables", f"{scen}_0", f"{scen}_0.txt"), wanted) for scen in SCENS}
    b1cache = {}
    for _, r in g.iterrows():
        scen = r.scenario; key = (r.tech, int(r.year))
        bp = os.path.join(base, "B1_Output_Params", scen, f"{r.parameter}.csv")
        if bp not in b1cache: b1cache[bp] = pd.read_csv(bp, dtype={"TECHNOLOGY": str}) if os.path.exists(bp) else None
        b = b1cache[bp]
        if b is None: b1 = "no file"
        else:
            m = b[(b.TECHNOLOGY == r.tech) & (pd.to_numeric(b.YEAR, errors="coerce") == int(r.year))]
            b1 = "no row" if m.empty else ";".join("" if isnan(v) else str(v) for v in m.Value)
        def look(G):
            P = G.get(r.parameter)
            if P is None: return "param absent", None
            v = P["data"].get(key)
            return ("no entry (default %s)" % P["default"], P["default"]) if v is None else (str(v), v)
        tx, txv = look(gm[scen]); t0, t0v = look(gm0[scen])
        try: iv = float(r.intended_value)
        except (TypeError, ValueError): iv = float("nan")
        rows.append({"country": c, "scenario": scen, "parameter": r.parameter, "tech": r.tech, "year": int(r.year), "cell": r.cell,
                     "formula": r.formula, "intended_value": r.intended_value, "a2_compiled": r.compiled_values, "class_A2": r["class"],
                     "b1_output_value": b1, "datafile": os.path.relpath(files[scen], ROOT), "datafile_value": tx,
                     "datafile_equals_intended_4dp": (txv is not None and not isnan(iv) and abs(txv - round(iv, 4)) <= 0.00005 + 1e-9 * abs(iv)),
                     "datafile_is_default": tx.startswith("no entry"),
                     "scen_0_txt_value": t0})
pd.DataFrame(rows).to_csv(os.path.join(OUT, "downstream_follow.csv"), index=False)
pd.DataFrame(tl).to_csv(os.path.join(OUT, "timeline.csv"), index=False)
D = pd.DataFrame(rows)
if not D.empty:
    D["b1_state"] = D.b1_output_value.map(lambda v: v if v in ("no file", "no row") else ("empty" if v == "" else "value"))
    print(D.groupby(["country", "scenario", "b1_state", "datafile_is_default", "datafile_equals_intended_4dp"]).size().to_string())
