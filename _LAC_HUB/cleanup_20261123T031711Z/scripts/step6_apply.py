"""Step 6: old scenario names at their source, and the check of every edited workbook against the start commit.

Edits
  1. six B1_Scenario_Config.xlsx: NDCNEW and LTSNEW replaced by NDC and LTS in the description column
     (Electrical, 'Description Parameter-Set'); through ao_safe_save.save_ao_safely.
  2. Costa Rica B1_Scenario_Config.xlsx: the variant rows NDCNEW_stage_2 and LTSNEW_stage_2 (Electrical, column
     Scenario) deleted by Excel, which adjusts every reference, in a temporary copy that is recalculated, guarded
     by ao_safe_save.assert_no_blank_formula_cells and only then replaces the file (the order of save_ao_safely).
  3. Stage 2 override workbooks: NDCNEW and LTSNEW replaced in their text (notes, rationale, method, scope);
     override CSVs: the same in the note field (everything after the fifth comma), other fields untouched.
  4. Guatemala A-O_Parametrization.xlsx, Other_Techs A2 and A3: 'NDP scenarios' replaced by 'NDC and LTS
     scenarios' (the rows feed the policy folders; the '<name> scenarios' form of the other A-O workbooks).
  5. Static compiled files that no step writes: Scenario column of DominicanRepublic B1_Output_Params/NDC and
     Guatemala A2_Output_Params/NDC and LTS TotalAnnualMinCapacity.csv set to the folder's scenario name.
Check (workbook_checks.csv): per workbook, by (sheet, cell) against the start commit (git ref given), every cell
equal in formula text and stored value except the cells edited as names or notes; for the deleted rows, every
other row's cells equal after the row map, and every formula equal to the start formula with its row
references moved by the same map (pointing at the same logical cell); formula count before minus the formulas
of the deleted rows equals after.

Usage: python step6_apply.py <start ref> [--check-only]
"""
import csv
import gc
import io
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

ROOT = M.ROOT
sys.path.insert(0, str(ROOT))
import ao_safe_save as S  # noqa: E402
import openpyxl  # noqa: E402

REF = sys.argv[1]
CHECK_ONLY = '--check-only' in sys.argv
_load = openpyxl.load_workbook


def load(*a, **k):
    # openpyxl 3.1.2 keeps a worksheet stream of a normal-mode load open until the next garbage collection;
    # collect at once so the file can be replaced (see GAPS, step 1)
    wb = _load(*a, **k)
    gc.collect()
    return wb


S.load_workbook = load
NEWNAME = [(re.compile(r'(?<![A-Za-z0-9])NDCNEW(?![A-Za-z0-9])'), 'NDC'),
           (re.compile(r'(?<![A-Za-z0-9])LTSNEW(?![A-Za-z0-9])'), 'LTS')]


def rename_text(s):
    for rx, new in NEWNAME:
        s = rx.sub(new, s)
    return s


B1CFG = ['CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic/RD_ENERGY', 'Ecuador/ECU_Energy', 'Guatemala/GUA_ENERGY',
         'Honduras/HON_ENERGY', 'Jamaica/JAM_ENERGY']
B1CFG = [m + '/B1_Scenario_Config.xlsx' for m in B1CFG]
OVR_XLSX = ['_STAGE2_INPUTS/STAGE2_OVERWRITES_CostaRica.xlsx', '_STAGE2_INPUTS/STAGE2_OVERWRITES_DR.xlsx',
            '_STAGE2_INPUTS/STAGE2_OVERWRITES_Ecuador.xlsx', '_STAGE2_INPUTS/STAGE2_OVERWRITES_Guatemala.xlsx',
            '_STAGE2_INPUTS/STAGE2_OVERWRITES_HON.xlsx', '_STAGE2_INPUTS/STAGE2_OVERWRITES_Jamaica.xlsx']
OVR_CSV = sorted(str(p.relative_to(ROOT).as_posix()) for p in (ROOT / '_STAGE2_INPUTS').glob('STAGE2_OVERWRITES*.csv'))
GUA_AO = 'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx'
CR_CFG = B1CFG[0]
VARIANTS = {'NDCNEW_stage_2', 'LTSNEW_stage_2'}
STATIC = [('DominicanRepublic/RD_ENERGY/B1_Output_Params/NDC/TotalAnnualMinCapacity.csv', 'NDC'),
          ('Guatemala/GUA_ENERGY/A2_Output_Params/NDC/TotalAnnualMinCapacity.csv', 'NDC'),
          ('Guatemala/GUA_ENERGY/A2_Output_Params/LTS/TotalAnnualMinCapacity.csv', 'LTS')]
edited = {}   # workbook -> set of (sheet, coordinate) edited as names or notes
deleted = {}  # workbook -> {sheet: [row numbers at the start commit]}


def cell_edit(rel, want):
    """want(ws, cell) -> new text or None. Saves through save_ao_safely when anything changed."""
    p = ROOT / rel
    wb = load(p)
    changed = set()
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and not c.value.startswith('='):
                    new = want(ws, c)
                    if new is not None and new != c.value:
                        c.value = new
                        changed.add((ws.title, c.coordinate))
    if changed:
        S.save_ao_safely(wb, p)
    wb.close()
    edited.setdefault(rel, set()).update(changed)
    print(f'{rel}: {len(changed)} cells')
    return changed


def desc_col(ws):
    for c in ws[1]:
        if isinstance(c.value, str) and c.value.strip().lower().startswith('description'):
            return c.column
    return None


def b1cfg_want(ws, c):
    col = desc_col(ws)
    if col is not None and c.column == col and c.row > 1:
        return rename_text(c.value)
    return None


def delete_variant_rows(rel):
    import pythoncom
    import win32com.client
    p = (ROOT / rel).resolve()
    wb = load(p, read_only=True)
    rows = {}
    for ws in wb.worksheets:
        hdr = [c for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
        cols = [j for j, h in enumerate(hdr) if isinstance(h, str) and h.strip() == 'Scenario']
        for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if any(j < len(r) and isinstance(r[j], str) and r[j].strip() in VARIANTS for j in cols):
                rows.setdefault(ws.title, []).append(i)
    wb.close()
    gc.collect()
    tmp = p.with_name(p.stem + '.safesave_tmp' + p.suffix)
    shutil.copy2(p, tmp)
    pythoncom.CoInitialize()
    excel = xwb = None
    try:
        excel = win32com.client.DispatchEx('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        excel.AskToUpdateLinks = False
        excel.EnableEvents = False
        xwb = excel.Workbooks.Open(str(tmp), 0, False)
        for s, idx in rows.items():
            ws = xwb.Worksheets(s)
            for i in sorted(idx, reverse=True):
                ws.Rows(i).Delete()
        excel.CalculateFullRebuild()
        xwb.SaveAs(str(tmp), S.XL_OPENXML_WORKBOOK)
        xwb.Close(False)
        xwb = None
    finally:
        try:
            if xwb is not None:
                xwb.Close(False)
        except Exception:
            pass
        try:
            if excel is not None:
                excel.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()
    try:
        S.assert_no_blank_formula_cells(tmp)
        gc.collect()
        os.replace(tmp, p)
    except BaseException:
        if tmp.exists():
            tmp.unlink()
        raise
    deleted[rel] = rows
    print(f'{rel}: deleted rows {sum(len(v) for v in rows.values())} in {list(rows)}')


def csv_note_edit(rel):
    p = ROOT / rel
    raw = p.read_bytes().decode('utf-8-sig' if p.read_bytes()[:3] == b'\xef\xbb\xbf' else 'utf-8')
    bom = p.read_bytes()[:3] == b'\xef\xbb\xbf'
    out, n = [], 0
    for line in raw.splitlines(keepends=True):
        body = line.rstrip('\r\n')
        end = line[len(body):]
        parts = body.split(',', 5)
        if len(parts) == 6 and not body.lstrip().startswith('#'):
            new = rename_text(parts[5])
            if new != parts[5]:
                n += 1
                body = ','.join(parts[:5] + [new])
        elif body.lstrip().startswith('#'):
            new = rename_text(body)
            if new != body:
                n += 1
                body = new
        out.append(body + end)
    if n:
        p.write_bytes(((b'\xef\xbb\xbf' if bom else b'') + ''.join(out).encode('utf-8')))
    print(f'{rel}: {n} lines')
    return n


def static_relabel(rel, name):
    p = ROOT / rel
    raw = p.read_bytes().decode('utf-8')
    lines = raw.splitlines(keepends=True)
    out, n = [lines[0]], 0
    hdr = lines[0].rstrip('\r\n').split(',')
    j = hdr.index('Scenario')
    for line in lines[1:]:
        body = line.rstrip('\r\n')
        end = line[len(body):]
        parts = body.split(',')
        if len(parts) > j and parts[j] != name:
            parts[j] = name
            n += 1
        out.append(','.join(parts) + end)
    p.write_bytes(''.join(out).encode('utf-8'))
    print(f'{rel}: {n} rows relabelled')
    return n


# ----------------------------------------------------------------------------- check
def at_ref(rel):
    data = subprocess.run(['git', 'show', f'{REF}:{rel}'], cwd=ROOT, capture_output=True).stdout
    return io.BytesIO(data)


def dump(src):
    wf, wv = load(src, data_only=False), None
    if isinstance(src, io.BytesIO):
        src.seek(0)
    wv = load(src, data_only=True)
    out = {}
    for ws in wf.worksheets:
        wsv = wv[ws.title]
        for row in ws.iter_rows():
            for c in row:
                v = wsv[c.coordinate].value
                if c.value is not None or v is not None:
                    out[(ws.title, c.row, c.column)] = (c.value, v)
    return out


REFRX = re.compile(r"((?:'[^']+'|[A-Za-z_][\w. ]*)!)?(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\d(])")


def move_refs(formula, sheet_here, rowmap_by_sheet):
    def sub(m):
        pre, d1, col, d2, row = m.groups()
        target = sheet_here if not pre else pre[:-1].strip("'")
        rm = rowmap_by_sheet.get(target)
        if rm is None:
            return m.group(0)
        r = int(row)
        if r not in rm:
            return m.group(0)
        nr = rm[r]
        return f'{pre or ""}{d1}{col}{d2}{nr}' if nr is not None else '#REF!'
    return REFRX.sub(sub, formula)


def check(rel):
    before, after = dump(at_ref(rel)), dump(ROOT / rel)
    dels = deleted.get(rel, {})
    rowmap = {}
    for s, idx in dels.items():
        maxrow = max(k[1] for k in before if k[0] == s)
        ds = sorted(idx)
        rowmap[s] = {r: (None if r in ds else r - sum(1 for d in ds if d < r)) for r in range(1, maxrow + 1)}
    ed = edited.get(rel, set())
    bad, compared, nf_b, nf_a, nf_del = [], 0, 0, 0, 0
    for (s, r, c), (fb, vb) in before.items():
        isf = isinstance(fb, str) and fb.startswith('=')
        nf_b += isf
        nr = rowmap.get(s, {}).get(r, r)
        if nr is None:
            nf_del += isf
            continue
        coord = openpyxl.utils.get_column_letter(c) + str(nr)
        fa, va = after.get((s, nr, c), (None, None))
        compared += 1
        # edits are recorded at their start-commit coordinates (names are edited before rows are deleted)
        if (s, openpyxl.utils.get_column_letter(c) + str(r)) in ed:
            continue
        exp = move_refs(fb, s, rowmap) if isf else fb
        if exp != fa or (vb != va and not (isinstance(vb, float) and isinstance(va, float) and abs(vb - va) <= 1e-9 * max(1, abs(vb)))):
            bad.append(f'{s}!{coord}: {fb!r}/{vb!r} -> {fa!r}/{va!r}')
    keys_after = {(s, r, c) for (s, r, c) in after}
    mapped = {(s, rowmap.get(s, {}).get(r, r), c) for (s, r, c) in before if rowmap.get(s, {}).get(r, r) is not None}
    extra = keys_after - mapped
    for k in sorted(extra):
        bad.append(f'{k[0]}!R{k[1]}C{k[2]}: new cell {after[k]!r}')
    nf_a = sum(1 for (fa, _) in after.values() if isinstance(fa, str) and fa.startswith('='))
    ok = not bad and nf_b - nf_del == nf_a
    return dict(file=rel, cells_compared=compared, name_or_note_cells_edited=len(ed),
                rows_deleted=sum(len(v) for v in dels.values()), formulas_before=nf_b, formulas_in_deleted_rows=nf_del,
                formulas_after=nf_a, other_cells_differing=len(bad), examples=' | '.join(bad[:5])[:900],
                check='PASS' if ok else 'FAIL')


if not CHECK_ONLY:
    for rel in B1CFG:
        cell_edit(rel, b1cfg_want)
    delete_variant_rows(CR_CFG)
    for rel in OVR_XLSX:
        cell_edit(rel, lambda ws, c: rename_text(c.value))
    for rel in OVR_CSV:
        csv_note_edit(rel)
    cell_edit(GUA_AO, lambda ws, c: 'NDC and LTS scenarios' if ws.title == 'Other_Techs' and c.column == 1 and c.value.strip() == 'NDP scenarios' else None)
    for rel, name in STATIC:
        static_relabel(rel, name)
    import json
    (M.JOB / 'work' / 'step6_edits.json').write_text(json.dumps(
        {'edited': {k: sorted(v) for k, v in edited.items()}, 'deleted': deleted}, indent=1), encoding='utf-8')
else:
    import json
    d = json.loads((M.JOB / 'work' / 'step6_edits.json').read_text(encoding='utf-8'))
    edited = {k: {tuple(x) for x in v} for k, v in d['edited'].items()}
    deleted = d['deleted']

rows = [check(rel) for rel in B1CFG + OVR_XLSX + [GUA_AO]]
with open(M.JOB / 'workbook_checks.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r['check'], r['file'], r['name_or_note_cells_edited'], r['rows_deleted'], r['other_cells_differing'], r['examples'][:200])
