"""Safe save path for A-O_Parametrization workbooks.

openpyxl writes formulas but never computes their results, so a workbook
loaded with data_only=False and saved by openpyxl loses every cached formula
value. Downstream readers (A2) that open the workbook with data_only=True then
see None for every formula cell. That is the 12 May 2026 Jamaica failure.

This module gives every A-O writer one save path:

    save_ao_safely(wb, path)
        1. wb.save(tmp)                       (openpyxl save to <stem>.safesave_tmp<suffix>
                                               in the target's folder, never to path)
        2. recalc_in_excel(tmp)               (Excel recomputes and stores results)
        3. assert_no_blank_formula_cells(tmp) (refuses a formula cell with no value)
        4. os.replace(tmp, path)              (the target is replaced only now)

If any step raises (a BlankFormulaError, a COM error, a PermissionError
because the target is open), the temporary copy is deleted, the target is
left untouched and the error is re-raised.

Formula text is never replaced by a number.
Requires Microsoft Excel and pywin32 (win32com) on Windows.
"""

from __future__ import annotations

import os
from pathlib import Path

from openpyxl import load_workbook

XL_OPENXML_WORKBOOK = 51  # xlsx, FileFormat 51


class BlankFormulaError(RuntimeError):
    """A formula cell has no stored (cached) value after save."""

    def __init__(self, path, blanks):
        self.path = str(path)
        self.blanks = list(blanks)
        preview = ", ".join(self.blanks[:10])
        more = "" if len(self.blanks) <= 10 else f" (+{len(self.blanks) - 10} more)"
        super().__init__(
            f"{len(self.blanks)} formula cell(s) without a stored value in "
            f"{self.path}: {preview}{more}"
        )


def recalc_in_excel(path) -> None:
    """Open `path` in a private hidden Excel instance, run a full rebuild
    recalculation, save it as xlsx (FileFormat 51) in place, close it and quit
    Excel, also when an error is raised."""
    import pythoncom
    import win32com.client

    full_path = str(Path(path).resolve())
    pythoncom.CoInitialize()
    excel = None
    wb = None
    try:
        # DispatchEx starts a separate Excel process, so a workbook the user
        # has open in their own Excel session is never touched.
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        excel.AskToUpdateLinks = False
        excel.EnableEvents = False
        # UpdateLinks=0: do not refresh external links; ReadOnly=False.
        wb = excel.Workbooks.Open(full_path, 0, False)
        excel.CalculateFullRebuild()
        wb.SaveAs(full_path, XL_OPENXML_WORKBOOK)
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
        wb = None
        excel = None
        pythoncom.CoUninitialize()


def find_blank_formula_cells(path) -> list[str]:
    """Return 'Sheet!A1' references of every formula cell whose cached value
    is None."""
    wb_f = load_workbook(path, data_only=False)
    wb_v = load_workbook(path, data_only=True)
    blanks: list[str] = []
    try:
        for ws_f in wb_f.worksheets:
            ws_v = wb_v[ws_f.title]
            for row in ws_f.iter_rows():
                for cell in row:
                    if cell.data_type != "f":
                        continue
                    if ws_v[cell.coordinate].value is None:
                        blanks.append(f"{ws_f.title}!{cell.coordinate}")
    finally:
        wb_f.close()
        wb_v.close()
    return blanks


def assert_no_blank_formula_cells(path) -> tuple[int, list[str]]:
    """Check that every formula cell in `path` has a stored value.

    Returns (count, references). Raises BlankFormulaError if count != 0.
    """
    blanks = find_blank_formula_cells(path)
    if blanks:
        raise BlankFormulaError(path, blanks)
    return 0, blanks


def save_ao_safely(wb, path) -> None:
    """Save an openpyxl workbook to a temporary copy next to `path`, have
    Excel restore every formula result in that copy, refuse it if any formula
    cell is still without a value, and only then replace `path` with it.

    On any error the temporary copy is deleted, `path` is left untouched and
    the error is re-raised."""
    target = Path(path).resolve()
    tmp = target.with_name(f"{target.stem}.safesave_tmp{target.suffix}")
    if tmp.exists():
        print(f"[ao_safe_save] deleting leftover temporary copy {tmp}")
        tmp.unlink()
    try:
        wb.save(tmp)
        recalc_in_excel(tmp)
        assert_no_blank_formula_cells(tmp)
        os.replace(tmp, target)
    except BaseException:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise
