"""Step 8 (and step 3 for this model): scenario labels of JAM_TRANSPORT at their source, B1_Scenario_Config.xlsx.
  old LTS (the national decarbonization plan scenario, built on the A2 policy base labelled NDP) -> NDP
  NDCNEW -> NDC, LTSNEW -> LTS; the new NDC and LTS read the A2 policy base folder LTS (the NDCNEW and LTSNEW
  folders were byte-equal copies of it), so their Reference is LTS.
Hydrogen: the Tech_Adoption rows of the hydrogen technologies of every policy scenario take the BAU form (maximum 0).
Every changed cell is logged in work/register_jam_transport.csv; the workbook is saved through ao_safe_save."""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import io
import sys

import openpyxl

sys.path.insert(0, str(M.ROOT))
import ao_safe_save  # noqa: E402

P = M.ROOT / 'Jamaica' / 'JAM_TRANSPORT' / 'B1_Scenario_Config.xlsx'
RENAME = {'LTS': 'NDP', 'NDCNEW': 'NDC', 'LTSNEW': 'LTS'}
H2 = {'TRBPUHYD', 'TRYTKHYD', 'TRMARHYD', 'TRMAMFREHYD', 'TRAVHYD'}
BAU_FORM = {'Logistic': 'NO', 'Linear': 'YES', 'v_2030': 0, 'v_2040': 0, 'v_2050': 0, 'Restriction_Type': 'Max'}
wb = openpyxl.load_workbook(io.BytesIO(P.read_bytes()))
log = []
for ws in wb.worksheets:
    hdr = [c.value for c in ws[1]]
    for col_name in ('Scenario', 'Name', 'Reference', 'Description'):
        if col_name not in hdr:
            continue
        k = hdr.index(col_name)
        for row in ws.iter_rows(min_row=2):
            v = row[k].value
            if isinstance(v, str) and v.strip() in RENAME and (col_name != 'Description' or ws.title == 'Scenarios'):
                new = RENAME[v.strip()]
                if ws.title == 'Scenarios' and col_name == 'Reference' and v.strip() in ('NDCNEW', 'LTSNEW'):
                    new = 'LTS'
                if ws.title == 'Scenarios' and col_name == 'Reference' and v.strip() == 'LTS':
                    new = 'LTS'     # the plan scenario keeps reading the A2 policy base folder
                if new != v:
                    log.append([ws.title, row[k].coordinate, col_name, v, new])
                    row[k].value = new
ws = wb['Tech_Adoption']
hdr = [c.value for c in ws[1]]
for row in ws.iter_rows(min_row=2):
    d = dict(zip(hdr, row))
    if d['Tech_Set'].value in H2 and d['Scenario'].value not in ('BAU',):
        for col, v in BAU_FORM.items():
            if d[col].value != v:
                log.append([ws.title, d[col].coordinate, col, d[col].value, v])
                d[col].value = v
ao_safe_save.save_ao_safely(wb, P)
with open(M.JOB / 'work' / 'register_jam_transport.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['sheet', 'cell', 'column', 'before', 'after'])
    w.writerows(log)
print(len(log), 'cells changed')
