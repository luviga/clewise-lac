"""Survey workbooks for old scenario names: per file and sheet, the cells holding NDCNEW, LTSNEW or 'NDP scenarios',
with their column header, and the formula count. Reads the files as a git ref holds them.
Usage: python wb_survey.py <ref> <path> [<path> ...]"""
import io
import re
import subprocess
import sys
import warnings

import openpyxl

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')
ref = sys.argv[1]
RX = re.compile(r'NDCNEW|LTSNEW|NDP scenarios')
for p in sys.argv[2:]:
    data = subprocess.run(['git', 'show', f'{ref}:{p}'], capture_output=True).stdout
    wb = openpyxl.load_workbook(io.BytesIO(data))
    nf = 0
    print('==', p)
    for ws in wb.worksheets:
        hdr = {c.column: c.value for c in ws[1]}
        by_col = {}
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    if c.value.startswith('='):
                        nf += 1
                    elif RX.search(c.value):
                        by_col.setdefault((c.column_letter, hdr.get(c.column)), []).append((c.coordinate, c.value))
        for (col, h), cells in by_col.items():
            whole = sum(1 for _, v in cells if v.strip() in ('NDCNEW', 'LTSNEW') or re.fullmatch(r'(NDCNEW|LTSNEW)_\w+', v.strip()))
            print(f'   {ws.title}!{col} [{h}] cells {len(cells)} (whole-name {whole}) e.g. {cells[0][0]}: {cells[0][1][:90]!r}')
    print('   formulas', nf)
