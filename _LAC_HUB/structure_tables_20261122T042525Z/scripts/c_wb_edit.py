"""Phase C workbook edits, through ao_safe_save (openpyxl edit, Excel recalculation, blank-formula guard, then
replace), with a check of every workbook against its state before.

  rename(path, mapping)      cells whose whole text is a scenario name of `mapping` get the new name.
                             Check: every other cell equal by (sheet, cell), formula text and stored value;
                             renamed cells hold the new name; formula count unchanged.
  delete_rows(path, rows)    rows = {sheet: [row numbers]} are deleted by Excel (references are adjusted by
                             Excel), saved to a temporary copy, recalculated, guarded, then replaced.
                             Check by key, never by row number: the multiset of row contents (stored values)
                             of each sheet after = before minus the deleted rows.
Both return a dict summary. The rows to delete are found by find_rows(path, names): rows that hold a cell
whose whole text is one of `names` in a scenario column (a column whose header contains 'Scenario' or is
'Name', or any column when the sheet has no header match).
"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, M.ROOT_S)
import ao_safe_save as S  # noqa: E402
from openpyxl import load_workbook  # noqa: E402


def dump(path):
    wf = load_workbook(path, data_only=False)
    wv = load_workbook(path, data_only=True)
    out = {}
    for ws in wf.worksheets:
        wsv = wv[ws.title]
        for row in ws.iter_rows():
            for c in row:
                v = wsv[c.coordinate].value
                if c.value is not None or v is not None:
                    out[(ws.title, c.coordinate)] = (c.value, v)
    return out


def rename(path, mapping):
    path = Path(path)
    before = dump(path)
    wb = load_workbook(path, data_only=False)
    changed = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.strip() in mapping and not c.value.startswith('='):
                    new = mapping[c.value.strip()]
                    changed.append((ws.title, c.coordinate, c.value, new))
                    c.value = new
    if not changed:
        return {'file': str(path), 'renamed': 0, 'check': 'no change'}
    S.save_ao_safely(wb, path)
    after = dump(path)
    ch = {(s, k): (o, n) for s, k, o, n in changed}
    bad = []
    for key in set(before) | set(after):
        b, a = before.get(key), after.get(key)
        if key in ch:
            if a is None or a[0] != ch[key][1]:
                bad.append((key, b, a))
            continue
        if b != a:
            # a formula's stored value may be recomputed by Excel; it must not change
            bad.append((key, b, a))
    nf_b = sum(1 for v in before.values() if isinstance(v[0], str) and v[0].startswith('='))
    nf_a = sum(1 for v in after.values() if isinstance(v[0], str) and v[0].startswith('='))
    return {'file': str(path), 'renamed': len(changed), 'other_cells_differing': len(bad),
            'formulas_before': nf_b, 'formulas_after': nf_a, 'examples': bad[:5],
            'check': 'PASS' if not bad and nf_b == nf_a else 'FAIL'}


def find_rows(path, names, sheets=None):
    wb = load_workbook(path, read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        if sheets and ws.title not in sheets:
            continue
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        hdr = [str(x) if x is not None else '' for x in rows[0]]
        cols = [j for j, h in enumerate(hdr) if 'scenario' in h.lower() or h.strip() == 'Name']
        hits = []
        for i, r in enumerate(rows[1:], start=2):
            check = [r[j] for j in cols if j < len(r)] if cols else list(r)
            if any(isinstance(v, str) and v.strip() in names for v in check):
                hits.append(i)
        if hits:
            out[ws.title] = hits
    wb.close()
    return out


def row_multiset(path):
    wv = load_workbook(path, data_only=True)
    out = {}
    for ws in wv.worksheets:
        out[ws.title] = Counter(tuple(c for c in r) for r in ws.iter_rows(values_only=True)
                                if any(c is not None for c in r))
    return out


def delete_rows(path, rows):
    import pythoncom
    import win32com.client
    path = Path(path).resolve()
    before = row_multiset(path)
    wvb = load_workbook(path, data_only=True)
    deleted = {s: Counter(tuple(c.value for c in wvb[s][i]) for i in idx) for s, idx in rows.items()}
    tmp = path.with_name(path.stem + '.safesave_tmp' + path.suffix)
    shutil.copy2(path, tmp)
    pythoncom.CoInitialize()
    excel = wb = None
    try:
        excel = win32com.client.DispatchEx('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        excel.AskToUpdateLinks = False
        excel.EnableEvents = False
        wb = excel.Workbooks.Open(str(tmp), 0, False)
        for s, idx in rows.items():
            ws = wb.Worksheets(s)
            for i in sorted(idx, reverse=True):
                ws.Rows(i).Delete()
        excel.CalculateFullRebuild()
        wb.SaveAs(str(tmp), S.XL_OPENXML_WORKBOOK)
        wb.Close(False)
        wb = None
    finally:
        try:
            if wb is not None:
                wb.Close(False)
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
    except Exception:
        os.remove(tmp)
        raise
    after = row_multiset(tmp)
    bad = {}
    for s in before:
        exp = before[s] - deleted.get(s, Counter())
        # a deleted row's content may also occur in rows that stay; remove only as many as were deleted
        if after.get(s, Counter()) != exp:
            bad[s] = (sum((exp - after.get(s, Counter())).values()), sum((after.get(s, Counter()) - exp).values()))
    if bad:
        os.remove(tmp)
        return {'file': str(path), 'deleted': sum(len(v) for v in rows.values()), 'check': 'FAIL', 'sheets': bad}
    os.replace(tmp, path)
    return {'file': str(path), 'deleted': sum(len(v) for v in rows.values()), 'check': 'PASS'}
