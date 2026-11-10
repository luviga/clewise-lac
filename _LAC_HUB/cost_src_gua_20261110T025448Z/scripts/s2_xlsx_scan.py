import openpyxl, sys, re
f=sys.argv[1]
wb=openpyxl.load_workbook(f,data_only=True,read_only=True)
for ws in wb.worksheets:
    print('== SHEET',ws.title,ws.max_row,ws.max_column)
    n=0
    for r in ws.iter_rows():
        vals=[(c.coordinate,c.value) for c in r if c.value is not None]
        if not vals: continue
        if n<4: print('  ',vals[:12]); 
        n+=1
        s=' '.join(str(v) for _,v in vals)
        if re.search(r'(?i)cost|price|IRENA|IEA|NREL|OLADE|ATB|USD|outlook|Guatemala|GTM|GUA',s) and n>=4:
            print('  *',str(vals[:14])[:600])
