"""Survey: which models have a Vehicle Techs sheet; dump headers, parameters, Fixed Horizon rows and Demand Ref.km.BY."""
import sys
import openpyxl

ROOT = r"C:\clw_align"
MODELS = ["CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic/RD_ENERGY", "Guatemala/GUA_ENERGY",
          "Honduras/HON_ENERGY", "Jamaica/JAM_TRANSPORT", "Ecuador/ECU_Energy", "Jamaica/JAM_ENERGY"]

for m in MODELS:
    p = f"{ROOT}/{m}/A1_Outputs/A-O_Parametrization.xlsx"
    wb = openpyxl.load_workbook(p, read_only=True, data_only=False)
    print("==", m, wb.sheetnames)
    if "Vehicle Techs" in wb.sheetnames:
        ws = wb["Vehicle Techs"]
        rows = list(ws.iter_rows(values_only=True))
        print("  header:", rows[0][:12], "...", rows[0][-2:], "ncol", len(rows[0]))
        params = {}
        for r in rows[1:]:
            if r[0] is None:
                continue
            params.setdefault(r[4], 0)
            params[r[4]] += 1
        print("  params:", params)
    if "Fixed Horizon Parameters" in wb.sheetnames:
        ws = wb["Fixed Horizon Parameters"]
        rows = list(ws.iter_rows(values_only=True))
        print("  FHP header:", rows[0])
    wb.close()
    d = f"{ROOT}/{m}/A1_Outputs/A-O_Demand.xlsx"
    wb = openpyxl.load_workbook(d, read_only=True, data_only=False)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    print("  Demand sheets:", wb.sheetnames, "header:", rows[0])
    wb.close()
