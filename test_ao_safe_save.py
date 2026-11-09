"""Test for ao_safe_save.py (needs Excel and pywin32).

Run:  py -I test_ao_safe_save.py      or      py -m pytest test_ao_safe_save.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openpyxl import Workbook, load_workbook  # noqa: E402

from ao_safe_save import (  # noqa: E402
    BlankFormulaError,
    assert_no_blank_formula_cells,
    recalc_in_excel,
    save_ao_safely,
)


def _tiny_workbook():
    wb = Workbook()
    ws = wb.active
    ws.title = "Primary Techs"
    ws["A1"] = 2
    ws["B1"] = 3
    ws["C1"] = "=A1*B1+1"
    return wb


def test_openpyxl_only_save_is_refused_then_recalc_passes():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tiny_ao.xlsx"
        _tiny_workbook().save(path)

        try:
            assert_no_blank_formula_cells(path)
        except BlankFormulaError as exc:
            assert exc.blanks == ["Primary Techs!C1"], exc.blanks
        else:
            raise AssertionError("guard did not raise on an openpyxl-only save")

        recalc_in_excel(path)
        count, blanks = assert_no_blank_formula_cells(path)
        assert count == 0 and blanks == []

        wb_f = load_workbook(path, data_only=False)
        wb_v = load_workbook(path, data_only=True)
        assert wb_f["Primary Techs"]["C1"].value == "=A1*B1+1"
        assert wb_v["Primary Techs"]["C1"].value == 7


def test_save_ao_safely_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tiny_ao_safe.xlsx"
        save_ao_safely(_tiny_workbook(), path)
        wb_v = load_workbook(path, data_only=True)
        assert wb_v["Primary Techs"]["C1"].value == 7


if __name__ == "__main__":
    test_openpyxl_only_save_is_refused_then_recalc_passes()
    print("PASS test_openpyxl_only_save_is_refused_then_recalc_passes")
    test_save_ao_safely_end_to_end()
    print("PASS test_save_ao_safely_end_to_end")
