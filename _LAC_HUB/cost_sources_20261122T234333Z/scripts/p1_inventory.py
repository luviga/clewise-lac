"""Phase 1, step 1.1: cost inventory of every live A-O workbook (all sheets with cost rows)
and of the GUA_AFOLU compiled CSVs. Writes cost_inventory.csv and fixed_horizon_sources.csv.
EmissionsPenalty is not held in any A-O sheet; it is inventoried from the compiled BAU files
in p1_penalty.py and appended to the inventory there."""
import os, sys, csv, re
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS
import openpyxl

COST = ["CapitalCost", "FixedCost", "VariableCost", "EmissionsPenalty"]
STD = {"Tech.ID", "Tech", "Tech.Name", "Parameter.ID", "Parameter", "Unit", "Unit.Introduced",
       "Projection.Mode", "Projection.Parameter", "Application", "Fuel", "Tech.Type", "Value"}


def load_compiled(folder, param):
    """dict tech -> {year: value} from a compiled BAU csv."""
    out = defaultdict(dict)
    for name in (param, param.replace("Emissions", "Emission")):
        p = os.path.join(ROOT, folder, name + ".csv")
        if os.path.exists(p):
            with open(p, newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    key = r["TECHNOLOGY"] or r["EMISSION"]
                    try:
                        out[key][int(float(r["YEAR"]))] = float(r["Value"])
                    except ValueError:
                        pass
            break
    return out


def fmt(v):
    if v is None or v == "":
        return ""
    if isinstance(v, float):
        return repr(round(v, 10))
    return str(v)


def nz_span(series):
    ys = sorted(y for y, v in series.items() if v not in (None, 0, 0.0))
    return (ys[0], ys[-1]) if ys else ("", "")


rows = []
fh_rows = []
modes = defaultdict(int)
for m in MODELS:
    comp = {p: load_compiled(m["bau"], p) for p in COST[:3]}
    if m["ao"] is None:
        # GUA_AFOLU: compiled CSVs are the inputs
        for prm in COST[:3]:
            for tech, ser in sorted(comp[prm].items()):
                a, b = nz_span(ser)
                rows.append(dict(country=m["cc"], model=m["model"], sheet="1_Parameters/BAU/%s.csv" % prm,
                                 ao_row="", tech=tech, tech_name="", parameter=prm, unit_introduced="", unit="",
                                 projection_mode="(csv values)", projection_parameter="",
                                 first_nonzero_year=a, last_nonzero_year=b,
                                 entered_base_year="", entered_base_value="",
                                 entered_2024=fmt(ser.get(2024)), entered_2030=fmt(ser.get(2030)), entered_2050=fmt(ser.get(2050)),
                                 compiled_2024=fmt(ser.get(2024)), compiled_2030=fmt(ser.get(2030)), compiled_2050=fmt(ser.get(2050)),
                                 any_nonzero=("yes" if a != "" else "no"), has_formula="no", note_text=""))
        continue
    p = os.path.join(ROOT, m["ao"])
    wbv = openpyxl.load_workbook(p, read_only=True, data_only=True)
    wbf = openpyxl.load_workbook(p, read_only=True, data_only=False)
    for ws in wbv.worksheets:
        wsf = wbf[ws.title]
        vit = ws.iter_rows(values_only=True)
        fit = wsf.iter_rows(values_only=True)
        hdr = next(vit, None)
        next(fit, None)
        if not hdr:
            continue
        hdr = [h.strip() if isinstance(h, str) else h for h in hdr]
        title = ws.title
        # Fixed Horizon / growth_formula source text
        is_fh = "fixed horizon" in title.lower() or title.lower().startswith("growth_formula")
        src_cols = [i for i, h in enumerate(hdr) if isinstance(h, str) and re.search(r"source|assumption|fuente|note|nota|comment", h, re.I)]
        if is_fh:
            for rn, r in enumerate(vit, start=2):
                if not r:
                    continue
                txt = [str(r[i]) for i in src_cols if i < len(r) and r[i] not in (None, "")]
                if src_cols and txt:
                    d = {h: r[i] for i, h in enumerate(hdr) if i < len(r) and isinstance(h, str)}
                    fh_rows.append(dict(country=m["cc"], model=m["model"], sheet=title, ao_row=rn,
                                        tech=d.get("Tech", d.get("Transpose growth", "")),
                                        parameter=d.get("Parameter", d.get("DESC", "")), unit=d.get("Unit", ""),
                                        value=fmt(d.get("Value", "")), source_text=" | ".join(txt)))
            continue
        if "Parameter" not in hdr:
            continue
        if m["kind"] == "energy" and title != "Vehicle Techs":
            continue  # energy models: only the vehicles are in scope
        pi = hdr.index("Parameter")
        ycols = [(i, h) for i, h in enumerate(hdr) if isinstance(h, int) or (isinstance(h, float) and h.is_integer())]
        ycols = [(i, int(h)) for i, h in ycols]
        notec = [i for i, h in enumerate(hdr) if isinstance(h, str) and h not in STD]
        H = {h: i for i, h in enumerate(hdr) if isinstance(h, str)}
        for rn, (r, rf) in enumerate(zip(vit, fit), start=2):
            if not r or len(r) <= pi or r[pi] not in COST:
                continue
            g = lambda k: r[H[k]] if k in H and H[k] < len(r) else None
            ent = {y: r[i] for i, y in ycols if i < len(r)}
            vcols = [i for i, _ in ycols] + [H[k] for k in ("Projection.Parameter",) if k in H]
            has_f = any(i < len(rf) and isinstance(rf[i], str) and str(rf[i]).startswith("=") for i in vcols)
            prm = r[pi]
            tech = g("Tech")
            cser = comp.get(prm, {}).get(tech, {})
            entered_nz = {y: v for y, v in ent.items() if isinstance(v, (int, float)) and v != 0}
            src = cser if cser else entered_nz
            a, b = nz_span(src)
            base_y = min(entered_nz) if entered_nz else ""
            modes[str(g("Projection.Mode"))] += 1
            rows.append(dict(country=m["cc"], model=m["model"], sheet=title, ao_row=rn, tech=tech,
                             tech_name=g("Tech.Name") or "", parameter=prm,
                             unit_introduced=g("Unit.Introduced") or "", unit=g("Unit") or "",
                             projection_mode=g("Projection.Mode") or "", projection_parameter=fmt(g("Projection.Parameter")),
                             first_nonzero_year=a, last_nonzero_year=b,
                             entered_base_year=base_y, entered_base_value=fmt(ent.get(base_y)) if base_y != "" else "",
                             entered_2024=fmt(ent.get(2024)), entered_2030=fmt(ent.get(2030)), entered_2050=fmt(ent.get(2050)),
                             compiled_2024=fmt(cser.get(2024)), compiled_2030=fmt(cser.get(2030)), compiled_2050=fmt(cser.get(2050)),
                             any_nonzero=("yes" if (entered_nz or any(v for v in cser.values())) else "no"),
                             has_formula="yes" if has_f else "no",
                             note_text=" | ".join(str(r[i]) for i in notec if i < len(r) and r[i] not in (None, ""))))

out = os.path.join(JOB, "cost_inventory.csv")
fields = list(rows[0].keys())
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
with open(os.path.join(JOB, "fixed_horizon_sources.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(fh_rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(fh_rows)
print(len(rows), "inventory rows;", len(fh_rows), "fixed-horizon source rows")
for k, v in sorted(modes.items(), key=lambda x: -x[1]):
    print("  mode", repr(k), v)
