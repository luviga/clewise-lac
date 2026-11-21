"""Phase C repair: put listed cells back to their base-snapshot value (4ba69d6) and save with save_ao_safely. Logged.
Usage: py -I scripts/restore_cells.py <workbook rel path> <sheet> <cell> [<cell> ...]"""
import sys
import openpyxl
sys.path.insert(0, 'C:/clw_fix')
from ao_safe_save import save_ao_safely  # noqa: E402

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
wbp, sheet, cells = sys.argv[1], sys.argv[2], sys.argv[3:]
b = openpyxl.load_workbook('C:/clw_base_4ba69d6/' + wbp)[sheet]
wb = openpyxl.load_workbook('C:/clw_fix/' + wbp)
ws = wb[sheet]
with open(JOB + '/logs/restore_cells.log', 'a', encoding='utf-8') as log:
    for c in cells:
        log.write(f'{wbp}|{sheet}|{c}: {str(ws[c].value)[:80]!r} -> base {str(b[c].value)[:80]!r}\n')
        ws[c].value = b[c].value
save_ao_safely(wb, 'C:/clw_fix/' + wbp)
print('restored', cells)
