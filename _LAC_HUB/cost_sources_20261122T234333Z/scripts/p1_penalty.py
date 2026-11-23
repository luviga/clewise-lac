"""Phase 1, step 1.4: EmissionsPenalty in every model's compiled BAU, with emitters and whether an
emitter is a free producer in a 2030 choice set. Writes penalty.csv and appends EmissionsPenalty
rows to cost_inventory.csv."""
import os, sys, csv
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS
import openpyxl


def read(folder, names):
    for n in names:
        p = os.path.join(ROOT, folder, n + ".csv")
        if os.path.exists(p):
            with open(p, newline="", encoding="utf-8-sig") as f:
                return list(csv.DictReader(f))
    return []


free = defaultdict(set)
with open(os.path.join(JOB, "choice_sets.csv"), newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["choice"] == "yes":
            for t in r["free_producers"].split(";"):
                free[r["model"]].add(t)

# A-Xtra_Emissions Externalities sheet per model (origin of the penalty in A2)
def xtra(m):
    p = os.path.join(ROOT, m["folder"], "A2_Extra_Inputs", "A-Xtra_Emissions.xlsx")
    if not os.path.exists(p):
        return {}
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        h = next(it, None)
        if not h or "EmissionsPenalty" not in h:
            continue
        H = {k: i for i, k in enumerate(h) if k}
        for r in it:
            if not r or r[0] is None:
                continue
            e = r[H.get("External Cost", 1)]
            out.setdefault(e, []).append(dict(tech=r[H["Tech"]], penalty=r[H["EmissionsPenalty"]],
                                              unit=r[H["Final Unit"]] if "Final Unit" in H and H["Final Unit"] < len(r) else "",
                                              sheet=ws.title))
    return out


prow, invrows = [], []
for m in MODELS:
    pen = read(m["bau"], ["EmissionsPenalty", "EmissionPenalty"])
    ear = read(m["bau"], ["EmissionActivityRatio"])
    X = xtra(m)
    byE = defaultdict(dict)
    for r in pen:
        try:
            byE[r["EMISSION"]][int(float(r["YEAR"]))] = float(r["Value"])
        except ValueError:
            pass
    emit = defaultdict(set)
    for r in ear:
        try:
            if float(r["Value"]) != 0:
                emit[r["EMISSION"]].add(r["TECHNOLOGY"])
        except ValueError:
            pass
    for e, ser in sorted(byE.items()):
        nz = {y: v for y, v in ser.items() if v != 0}
        if not nz:
            continue
        ys = sorted(nz)
        em = sorted(emit.get(e, []))
        fr = [t for t in em if t in free[m["model"]]]
        xo = X.get(e, [])
        origin = ("A-Xtra_Emissions.xlsx sheet %s" % xo[0]["sheet"]) if xo else (
            "ModeloSuelo workbook via 1_Parameters csv" if m["ao"] is None else "B1_Scenario_Config.xlsx rows of EmissionsPenalty (Waste externalities), applied by B1")
        prow.append(dict(country=m["cc"], model=m["model"], emission=e, first_year=ys[0], last_year=ys[-1],
                         value_first=nz[ys[0]], value_2030=ser.get(2030, ""), value_last=nz[ys[-1]],
                         min_value=min(nz.values()), max_value=max(nz.values()),
                         unit_in_input=(xo[0]["unit"] if xo else ""),
                         emitters=";".join(em), n_emitters=len(em),
                         emitters_free_in_choice_set=";".join(fr), can_change_choice="yes" if fr else "no",
                         origin=origin))
        invrows.append(dict(country=m["cc"], model=m["model"], sheet="compiled BAU EmissionsPenalty (%s)" % origin,
                            ao_row="", tech=e, tech_name="emission " + e, parameter="EmissionsPenalty",
                            unit_introduced="", unit=(xo[0]["unit"] if xo else ""), projection_mode="", projection_parameter="",
                            first_nonzero_year=ys[0], last_nonzero_year=ys[-1], entered_base_year="", entered_base_value="",
                            entered_2024="", entered_2030="", entered_2050="",
                            compiled_2024=ser.get(2024, ""), compiled_2030=ser.get(2030, ""), compiled_2050=ser.get(2050, ""),
                            any_nonzero="yes", has_formula="no", note_text="",
                            **{"class": "choice" if fr else ("total_only" if em else "inactive"),
                               "class_reason": ("emitted by free producer(s) " + ";".join(fr)) if fr else ("emitters not free in any 2030 choice set" if em else "no technology emits it")}))

with open(os.path.join(JOB, "penalty.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(prow[0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(prow)
inv = os.path.join(JOB, "cost_inventory.csv")
with open(inv, newline="", encoding="utf-8") as f:
    rows = [r for r in csv.DictReader(f) if r["parameter"] != "EmissionsPenalty"]
fields = list(rows[0].keys())
rows += invrows
with open(inv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader(); w.writerows(rows)
for p in prow:
    print(p["model"], p["emission"], p["first_year"], p["last_year"], p["value_2030"], p["unit_in_input"], p["n_emitters"], p["can_change_choice"], p["emitters_free_in_choice_set"][:60], "|", p["origin"])
