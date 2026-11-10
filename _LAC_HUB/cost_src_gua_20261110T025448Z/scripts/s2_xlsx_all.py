import openpyxl, sys
f,out=sys.argv[1],sys.argv[2]
wb=openpyxl.load_workbook(f,data_only=True,read_only=True)
with open(out,'w',encoding='utf-8') as o:
    for ws in wb.worksheets:
        for r in ws.iter_rows():
            for c in r:
                if isinstance(c.value,str) and c.value.strip():
                    o.write(f'{ws.title}!{c.coordinate}\t{c.value}\n'.replace('\n ','  '))
