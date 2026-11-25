"""Dump, for every history-build case, the A-O rows, B1 Electrical BAU rows and compiled BAU values.
Read only. Output: printed text and work/hb_scripts/hb_dump.json (scratch for later scripts)."""
import io, csv, json, os, sys
import openpyxl

ROOT = r"C:\clw_align"
MODELS = {
    "CostaRica": r"CostaRica\CR_ENERGY\t1_confection",
    "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
    "Ecuador": r"Ecuador\ECU_Energy",
    "Guatemala": r"Guatemala\GUA_ENERGY",
    "Honduras": r"Honduras\HON_ENERGY",
    "Jamaica": r"Jamaica\JAM_ENERGY",
}
HB = r"C:\clw_align\_LAC_HUB\fix_run2_20261120T225823Z\history_builds.csv"
OUT = r"C:\clw_align\_LAC_HUB\align_20261124T021708Z\work\hb_scripts\hb_dump.json"


def load(p, data_only=False):
    return openpyxl.load_workbook(io.BytesIO(open(p, "rb").read()), data_only=data_only)


cases = list(csv.DictReader(open(HB, encoding="utf-8")))
techs = {}
for c in cases:
    techs.setdefault(c["country"], set()).add(c["tech"])

dump = {}
for country, rel in MODELS.items():
    if country not in techs:
        continue
    mdir = os.path.join(ROOT, rel)
    ao = os.path.join(mdir, "A1_Outputs", "A-O_Parametrization.xlsx")
    wb = load(ao)
    wbv = load(ao, data_only=True)
    res = {}
    for sh in ("Primary Techs", "Secondary Techs"):
        if sh not in wb.sheetnames:
            continue
        ws = wb[sh]
        wsv = wbv[sh]
        hdr = [c.value for c in ws[1]]
        # locate Tech and Parameter columns
        try:
            ti = hdr.index("Tech")
            pi = hdr.index("Parameter")
        except ValueError:
            print(country, sh, "header", hdr[:15])
            continue
        for r in range(2, ws.max_row + 1):
            t = ws.cell(r, ti + 1).value
            if t in techs[country]:
                row = {}
                for ci, h in enumerate(hdr):
                    v = ws.cell(r, ci + 1).value
                    vv = wsv.cell(r, ci + 1).value
                    row[str(h)] = [v if not hasattr(v, "text") else str(v), vv]
                res.setdefault(t, []).append({"sheet": sh, "row": r, "param": ws.cell(r, pi + 1).value, "cells": row})
    # B1 Electrical
    b1 = os.path.join(mdir, "B1_Scenario_Config.xlsx")
    wb1 = load(b1)
    ws = wb1["Electrical"]
    hdr = [c.value for c in ws[1]]
    b1rows = []
    for r in range(2, ws.max_row + 1):
        vals = {str(h): ws.cell(r, i + 1).value for i, h in enumerate(hdr)}
        ts = str(vals.get("Tech_Set") or "")
        hit = [t for t in techs[country] if t in [x.strip() for x in ts.replace(";", ",").split(",")]]
        if hit:
            b1rows.append({"row": r, "vals": {k: (str(v) if v is not None else None) for k, v in vals.items()}})
    # compiled BAU
    comp = {}
    for folder in ("A2_Output_Params", "B1_Output_Params"):
        for prm in ("ResidualCapacity", "TotalTechnologyAnnualActivityLowerLimit", "TotalTechnologyAnnualActivityUpperLimit",
                    "TotalAnnualMinCapacityInvestment", "TotalAnnualMaxCapacityInvestment", "TotalAnnualMaxCapacity",
                    "TotalAnnualMinCapacity", "CapacityFactor", "AvailabilityFactor", "CapacityToActivityUnit", "OperationalLife"):
            p = os.path.join(mdir, folder, "BAU", prm + ".csv")
            if not os.path.exists(p):
                continue
            for d in csv.DictReader(open(p, encoding="utf-8")):
                t = d.get("TECHNOLOGY")
                if t in techs[country]:
                    y = d.get("YEAR")
                    if y and (int(y) > 2030):
                        continue
                    key = "|".join([folder[:2], prm, t] + ([d.get("TIMESLICE")] if d.get("TIMESLICE") else []))
                    comp.setdefault(key, {})[y or "-"] = d["Value"]
    dump[country] = {"ao": res, "b1hdr": [str(h) for h in hdr], "b1": b1rows, "comp": comp}

json.dump(dump, open(OUT, "w", encoding="utf-8"), indent=0, default=str)
print("written", OUT)
