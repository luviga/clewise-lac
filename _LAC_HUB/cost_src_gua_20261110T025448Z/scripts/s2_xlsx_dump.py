import openpyxl, sys
f=sys.argv[1]; sheets=sys.argv[2:]
wb=openpyxl.load_workbook(f,data_only=True,read_only=True)
for s in sheets:
    ws=wb[s]; print('== SHEET',s)
    for r in ws.iter_rows():
        vals=[(c.coordinate,c.value) for c in r if c.value not in (None,'')]
        if vals: print(' | '.join(f'{k}={v}' for k,v in vals))
