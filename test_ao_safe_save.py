"""Test for ao_safe_save.py (needs Excel and pywin32).

Run:  py -I test_ao_safe_save.py      or      py -m pytest test_ao_safe_save.py
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openpyxl import Workbook, load_workbook  # noqa: E402

import ao_safe_save  # noqa: E402
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


def _plain_values_workbook():
    wb = Workbook()
    ws = wb.active
    ws.title = "Primary Techs"
    ws["A1"] = 10
    ws["B1"] = 20
    ws["C1"] = 30
    return wb


def _sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _temp_leftovers(folder) -> list[str]:
    return sorted(p.name for p in Path(folder).glob("*.safesave_tmp*"))


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


def test_excel_failure_leaves_target_unchanged():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "target_ao.xlsx"
        _plain_values_workbook().save(target)
        before = _sha256(target)

        def _failing_recalc(path):
            raise RuntimeError("simulated Excel failure")

        original = ao_safe_save.recalc_in_excel
        ao_safe_save.recalc_in_excel = _failing_recalc
        try:
            try:
                save_ao_safely(_tiny_workbook(), target)
            except RuntimeError as exc:
                assert "simulated Excel failure" in str(exc), exc
            else:
                raise AssertionError("save_ao_safely did not raise")
        finally:
            ao_safe_save.recalc_in_excel = original

        assert _sha256(target) == before, "target changed after an Excel failure"
        assert _temp_leftovers(tmp) == [], _temp_leftovers(tmp)


def test_guard_failure_leaves_target_unchanged():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "target_ao.xlsx"
        _plain_values_workbook().save(target)
        before = _sha256(target)

        def _noop_recalc(path):
            return None

        original = ao_safe_save.recalc_in_excel
        ao_safe_save.recalc_in_excel = _noop_recalc
        try:
            try:
                save_ao_safely(_tiny_workbook(), target)
            except BlankFormulaError as exc:
                assert exc.blanks == ["Primary Techs!C1"], exc.blanks
            else:
                raise AssertionError("save_ao_safely did not raise BlankFormulaError")
        finally:
            ao_safe_save.recalc_in_excel = original

        assert _sha256(target) == before, "target changed after a guard failure"
        assert _temp_leftovers(tmp) == [], _temp_leftovers(tmp)


def test_replace_existing_target():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "target_ao.xlsx"
        _plain_values_workbook().save(target)

        save_ao_safely(_tiny_workbook(), target)

        wb_f = load_workbook(target, data_only=False)
        wb_v = load_workbook(target, data_only=True)
        assert wb_f["Primary Techs"]["C1"].value == "=A1*B1+1"
        assert wb_v["Primary Techs"]["C1"].value == 7
        wb_f.close()
        wb_v.close()
        assert _temp_leftovers(tmp) == [], _temp_leftovers(tmp)


if __name__ == "__main__":
    test_openpyxl_only_save_is_refused_then_recalc_passes()
    print("PASS test_openpyxl_only_save_is_refused_then_recalc_passes")
    test_save_ao_safely_end_to_end()
    print("PASS test_save_ao_safely_end_to_end")
    test_excel_failure_leaves_target_unchanged()
    print("PASS test_excel_failure_leaves_target_unchanged")
    test_guard_failure_leaves_target_unchanged()
    print("PASS test_guard_failure_leaves_target_unchanged")
    test_replace_existing_target()
    print("PASS test_replace_existing_target")
