"""Print the A-O rows and B1 config rows of one technology (read-only helper).
Run: py -I scripts/show_tech.py <country> <tech> [param-substring]"""
import sys, os
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, MODELS
c, tech = sys.argv[1], sys.argv[2]
sub = sys.argv[3] if len(sys.argv) > 3 else ''
m = MODELS[c]
p = f'{ROOT}/{m}/A1_Outputs/A-O_Parametrization.xlsx'
wv = openpyxl.load_workbook(p, data_only=True); wf = openpyxl.load_workbook(p)
for ws in wv.worksheets:
    hdr = {ws.cell(1, k).value: k for k in range(1, ws.max_column + 1)}
    if 'Tech' not in hdr: continue
    ycols = sorted((int(h), k) for h, k in hdr.items() if isinstance(h, (int, float)) and 2015 <= h <= 2060)
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, hdr['Tech']).value != tech: continue
        par = ws.cell(r, hdr['Parameter']).value
        if sub and sub.lower() not in str(par).lower(): continue
        if 'Value' in hdr:
            print(f'{ws.title[:6]} r{r} {par}: Value={ws.cell(r, hdr["Value"]).value}')
            continue
        vals = [ws.cell(r, k).value for y, k in ycols if y <= 2026 or y in (2030, 2050)]
        f = [wf[ws.title].cell(r, k).value for y, k in ycols if y <= 2026]
        nf = sum(1 for x in f if isinstance(x, str) and x.startswith('='))
        ex = next((x for x in f if isinstance(x, str) and x.startswith('=')), '')
        if all(v is None for v in vals): continue
        mode = ws.cell(r, hdr.get('Projection.Mode', 1)).value
        print(f'{ws.title[:6]} r{r} {par} [{mode}|{ws.cell(r, hdr.get("Projection.Parameter", 1)).value}]:',
              [round(v, 5) if isinstance(v, float) else v for v in vals], f'nform={nf} {str(ex)[:70]}' if nf else '')
cfg = openpyxl.load_workbook(f'{ROOT}/{m}/B1_Scenario_Config.xlsx', data_only=True)
for ws in cfg.worksheets:
    hdr = [ws.cell(1, k).value for k in range(1, ws.max_column + 1)]
    if 'Scenario' not in hdr: continue
    for r in range(2, ws.max_row + 1):
        row = [ws.cell(r, k).value for k in range(1, ws.max_column + 1)]
        if row[0] not in ('BAU', 'NDCNEW', 'LTSNEW', 'All'): continue
        if not any(isinstance(x, str) and (x == tech or x.replace(' ', '').startswith(tech + ';')) for x in row[:6]): continue
        if sub and sub.lower() not in str(row[1]).lower(): continue
        print(f'cfg {ws.title[:10]} r{r}:', [str(x)[:120] for x in row if x is not None][:14])
