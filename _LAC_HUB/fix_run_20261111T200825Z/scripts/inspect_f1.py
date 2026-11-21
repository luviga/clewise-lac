import openpyxl, sys
root = r"C:/clw_fix/"
def show(path, sheet, rows, cols=range(1, 50), formulas=True):
    wb = openpyxl.load_workbook(root + path, data_only=not formulas)
    ws = wb[sheet]
    hdr = [ws.cell(1, c).value for c in cols]
    print(path, sheet, 'header:', hdr[:12], '...')
    for r in rows:
        vals = [ws.cell(r, c).value for c in cols]
        print(r, vals)
show("Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx", "Primary Techs", [14, 284])
show("Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx", "Primary Techs", [14, 284], formulas=False)
show("Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx", "Secondary Techs", [1, 17, 27])
show("DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx", "Secondary Techs", [232])
