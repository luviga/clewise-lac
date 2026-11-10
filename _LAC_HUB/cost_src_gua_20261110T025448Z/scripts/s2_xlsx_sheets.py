import openpyxl, sys
for f in sys.argv[1:]:
    wb=openpyxl.load_workbook(f,data_only=True,read_only=True)
    print('###',f)
    for ws in wb.worksheets: print('  ',ws.title,ws.max_row,ws.max_column)
