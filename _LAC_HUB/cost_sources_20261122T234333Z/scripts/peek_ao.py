import sys, openpyxl
p = sys.argv[1]
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
for ws in wb.worksheets:
    print("==", ws.title, ws.max_row, ws.max_column)
    n = 0
    for row in ws.iter_rows(values_only=True):
        print("  ", row[:20])
        n += 1
        if n >= int(sys.argv[2] if len(sys.argv) > 2 else 4):
            break
