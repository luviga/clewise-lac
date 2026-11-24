"""Dump every vehicle CapitalCost and FixedCost cell (formula and cached value), OperationalLife rows of vehicle techs,
and Ref.km.BY rows of A-O_Demand.xlsx, for the vehicle models. Output: vr_scripts/cells_dump.csv (scratch input for vr03)."""
import csv
import os
import openpyxl
from openpyxl.utils import get_column_letter

ROOT = r"C:\clw_align"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cells_dump.csv")
MODELS = ["CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic/RD_ENERGY", "Guatemala/GUA_ENERGY",
          "Honduras/HON_ENERGY", "Jamaica/JAM_TRANSPORT", "Ecuador/ECU_Energy", "Jamaica/JAM_ENERGY"]
PARAMS = ("CapitalCost", "FixedCost")

rows_out = []
for m in MODELS:
    p = f"{ROOT}/{m}/A1_Outputs/A-O_Parametrization.xlsx"
    wbf = openpyxl.load_workbook(p, read_only=True, data_only=False)
    wbv = openpyxl.load_workbook(p, read_only=True, data_only=True)
    if "Vehicle Techs" not in wbf.sheetnames:
        continue
    f_rows = list(wbf["Vehicle Techs"].iter_rows())
    v_rows = list(wbv["Vehicle Techs"].iter_rows(values_only=True))
    hdr = [c.value for c in f_rows[0]]
    col = {h: i for i, h in enumerate(hdr) if h is not None}
    techs = set()
    for ri in range(1, len(f_rows)):
        fr = f_rows[ri]
        vr = v_rows[ri]
        tech = vr[col["Tech"]]
        par = vr[col["Parameter"]]
        if tech is None:
            continue
        techs.add(tech)
        if par not in PARAMS:
            continue
        for h, ci in col.items():
            if not isinstance(h, int):
                continue
            fv = fr[ci].value
            cv = vr[ci]
            rows_out.append(dict(model=m, file="A1_Outputs/A-O_Parametrization.xlsx", sheet="Vehicle Techs",
                                 excel_row=ri + 1, coord=f"{get_column_letter(ci + 1)}{ri + 1}", tech=tech, tech_name=vr[col["Tech.Name"]],
                                 parameter=par, unit_introduced=vr[col["Unit.Introduced"]], unit=vr[col["Unit"]],
                                 projection_mode=vr[col["Projection.Mode"]], year=h,
                                 formula=fv if isinstance(fv, str) and fv.startswith("=") else "",
                                 value=cv))
    # Fixed Horizon Parameters: OperationalLife of vehicle techs
    ff = list(wbf["Fixed Horizon Parameters"].iter_rows())
    fv_ = list(wbv["Fixed Horizon Parameters"].iter_rows(values_only=True))
    hdr = [c.value for c in ff[0]]
    col = {h: i for i, h in enumerate(hdr) if h is not None}
    for ri in range(1, len(ff)):
        vr = fv_[ri]
        if vr[col["Tech"]] in techs and vr[col["Parameter"]] == "OperationalLife":
            cell = ff[ri][col["Value"]]
            src = vr[col["Source / Assumption"]] if "Source / Assumption" in col else ""
            rows_out.append(dict(model=m, file="A1_Outputs/A-O_Parametrization.xlsx", sheet="Fixed Horizon Parameters",
                                 excel_row=ri + 1, coord=getattr(cell, "coordinate", ""), tech=vr[col["Tech"]],
                                 tech_name=vr[col["Tech.Name"]], parameter="OperationalLife",
                                 unit_introduced=src, unit=vr[col["Unit"]], projection_mode="", year="",
                                 formula=cell.value if isinstance(cell.value, str) and str(cell.value).startswith("=") else "",
                                 value=vr[col["Value"]]))
    wbf.close()
    wbv.close()
    # Demand Ref.km.BY
    d = f"{ROOT}/{m}/A1_Outputs/A-O_Demand.xlsx"
    wbf = openpyxl.load_workbook(d, read_only=True, data_only=False)
    wbv = openpyxl.load_workbook(d, read_only=True, data_only=True)
    sn = "Demand_Projection"
    ff = list(wbf[sn].iter_rows())
    fv_ = list(wbv[sn].iter_rows(values_only=True))
    hdr = [c.value for c in ff[0]]
    col = {h: i for i, h in enumerate(hdr) if h is not None}
    for ri in range(1, len(ff)):
        vr = fv_[ri]
        km = vr[col["Ref.km.BY"]]
        if km is None or km == "":
            continue
        cell = ff[ri][col["Ref.km.BY"]]
        rows_out.append(dict(model=m, file="A1_Outputs/A-O_Demand.xlsx", sheet=sn, excel_row=ri + 1,
                             coord=getattr(cell, "coordinate", ""), tech=vr[col["Fuel/Tech"]], tech_name=vr[col["Name"]],
                             parameter="Ref.km.BY", unit_introduced="", unit="km per vehicle per year",
                             projection_mode="", year="",
                             formula=cell.value if isinstance(cell.value, str) and str(cell.value).startswith("=") else "",
                             value=km))
    wbf.close()
    wbv.close()

with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()))
    w.writeheader()
    w.writerows(rows_out)
print("rows", len(rows_out), OUT)
