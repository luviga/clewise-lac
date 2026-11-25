import io, openpyxl
p = r"C:\clw_fix\_LAC_HUB\fix_run2_20261120T225823Z\downloads\map_dr\CNE_DataCNE_GeneracionFuenteSENI.xlsx"
wb = openpyxl.load_workbook(io.BytesIO(open(p, "rb").read()), data_only=True)
for ws in wb:
    print("sheet", ws.title, ws.max_row, ws.max_column)
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 25)):
        vals = [(c.coordinate, c.value) for c in row if c.value is not None]
        if vals:
            print(vals)
