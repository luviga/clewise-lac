import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook

import ao_cost_repair_manager as mgr


def make_ao(path: Path, rows: list[list[object]], years: list[int]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Primary Techs"
    ws.append(
        [
            "Tech.ID",
            "Tech",
            "Tech.Name",
            "Parameter.ID",
            "Parameter",
            "Unit",
            "Projection.Mode",
            "Projection.Parameter",
            *years,
        ]
    )
    for row in rows:
        ws.append(row)
    wb.save(path)


def make_fuel_workbook(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "OSeMOSYS_VarCost"
    ws.append(["OSeMOSYS VariableCost USD/PJ"])
    ws.append([])
    ws.append([])
    ws.append(["ISO", "Fuel", "Fuel Code", "Scenario", "GJ/unit", "2021", "2022"])
    ws.append(["ECU", "Diesel", "DSL", "REF", 0.0358, 30_000_000, 31_000_000])
    wb.save(path)


class AoCostRepairManagerTests(unittest.TestCase):
    def test_fuel_series_reads_and_converts_to_musd_per_pj(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fuel_path = Path(tmp) / "fuel.xlsx"
            make_fuel_workbook(fuel_path)
            series, meta = mgr.read_fuel_series(fuel_path, "ECU", "DSL", "REF")
            self.assertEqual(meta["source_sheet"], "OSeMOSYS_VarCost")
            self.assertEqual(series[2021], 30_000_000)
            converted, note = mgr.fuel_unit_conversion(series[2021], "MUS$ / PJ")
            self.assertEqual(converted, 30)
            self.assertEqual(note, "usd_per_pj_to_musd_per_pj")

    def test_smart_mapping_matches_same_name_different_tech_id(self) -> None:
        target = mgr.AoCostRow(
            country="Ecuador",
            model_label="ECU_Energy",
            workbook_path=Path("target.xlsx"),
            source_label="target",
            source_kind="target",
            sheet="Primary Techs",
            row_index=2,
            tech="PPGEO",
            tech_name="Primary - Transformation - Geothermal",
            parameter="CapitalCost",
            unit="MUS$ / PJ",
            projection_mode="Flat",
            year_values={2021: 1, 2022: None},
            header_years=(2021, 2022),
        )
        source = mgr.AoCostRow(
            country="Ecuador",
            model_label="ECU_Energy",
            workbook_path=Path("source.xlsx"),
            source_label="source",
            source_kind="ecuador_local_reference",
            sheet="Primary Techs",
            row_index=7,
            tech="PP_GEO",
            tech_name="Primary - Transformation - Geothermal",
            parameter="CapitalCost",
            unit="MUS$ / PJ",
            projection_mode="User defined",
            year_values={2021: 5000, 2022: 4900},
            header_years=(2021, 2022),
        )
        score = mgr.score_local_match(target, source)
        self.assertEqual(score.decision, "AUTO_HIGH_CONFIDENCE")
        self.assertGreaterEqual(score.score, 95)

    def test_charcoal_does_not_match_steam_coal_fuel_code(self) -> None:
        row = mgr.AoCostRow(
            country="Ecuador",
            model_label="ECU_Energy",
            workbook_path=Path("target.xlsx"),
            source_label="target",
            source_kind="target",
            sheet="Primary Techs",
            row_index=2,
            tech="DIST_CHA",
            tech_name="Primary - ETD - Charcoal",
            parameter="VariableCost",
            unit="MUS$ / PJ",
            projection_mode="Flat",
            year_values={2021: 1},
            header_years=(2021,),
        )
        self.assertEqual(mgr.detect_fuel_code(row), "")
        self.assertEqual(mgr.detect_family(row), "charcoal")

    def test_apply_verify_and_restore_on_tiny_workbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ao_path = root / "A-O_Parametrization.xlsx"
            make_ao(
                ao_path,
                [
                    [
                        1,
                        "DIST_DSL",
                        "Primary - Import/Distribution - Diesel",
                        1,
                        "VariableCost",
                        "MUS$ / PJ",
                        "Flat",
                        0,
                        1,
                        None,
                    ]
                ],
                [2021, 2022],
            )
            manifest = [
                {
                    "manifest_id": "m1",
                    "approved": "YES",
                    "decision": "AUTO_HIGH_CONFIDENCE",
                    "country": "Ecuador",
                    "model_label": "ECU_Energy",
                    "ao_path": str(ao_path),
                    "sheet": "Primary Techs",
                    "row_index": "2",
                    "tech": "DIST_DSL",
                    "tech_name": "Primary - Import/Distribution - Diesel",
                    "parameter": "VariableCost",
                    "unit": "MUS$ / PJ",
                    "year": "2021",
                    "old_value": "1",
                    "new_value": "30",
                    "source_kind": "fuel_workbook",
                    "source_path": "fuel.xlsx",
                    "source_sheet": "OSeMOSYS_VarCost",
                    "source_row_index": "5",
                    "source_tech": "",
                    "source_tech_name": "Fuel code DSL",
                    "source_unit": "USD/PJ",
                    "source_projection_mode": "REF trajectory",
                    "fuel_code": "DSL",
                    "scenario": "REF",
                    "score": "100",
                    "reason": "test",
                    "row_fingerprint": "abc",
                    "projection_mode_old": "Flat",
                    "projection_mode_new": "User defined",
                    "unit_conversion": "usd_per_pj_to_musd_per_pj",
                    "generated_at": "test",
                },
                {
                    "manifest_id": "m2",
                    "approved": "YES",
                    "decision": "AUTO_HIGH_CONFIDENCE",
                    "country": "Ecuador",
                    "model_label": "ECU_Energy",
                    "ao_path": str(ao_path),
                    "sheet": "Primary Techs",
                    "row_index": "2",
                    "tech": "DIST_DSL",
                    "tech_name": "Primary - Import/Distribution - Diesel",
                    "parameter": "VariableCost",
                    "unit": "MUS$ / PJ",
                    "year": "2022",
                    "old_value": "",
                    "new_value": "31",
                    "source_kind": "fuel_workbook",
                    "source_path": "fuel.xlsx",
                    "source_sheet": "OSeMOSYS_VarCost",
                    "source_row_index": "5",
                    "source_tech": "",
                    "source_tech_name": "Fuel code DSL",
                    "source_unit": "USD/PJ",
                    "source_projection_mode": "REF trajectory",
                    "fuel_code": "DSL",
                    "scenario": "REF",
                    "score": "100",
                    "reason": "test",
                    "row_fingerprint": "abc",
                    "projection_mode_old": "Flat",
                    "projection_mode_new": "User defined",
                    "unit_conversion": "usd_per_pj_to_musd_per_pj",
                    "generated_at": "test",
                },
            ]
            cells, modes = mgr.apply_rows_to_workbook(
                ao_path=ao_path,
                rows=manifest,
                dry_run=False,
                ignore_old_value_mismatch=False,
            )
            self.assertEqual(cells, 2)
            self.assertEqual(modes, 1)
            checked, errors = mgr.verify_manifest_rows(
                root=root,
                rows=manifest,
                expect="applied",
                include_review=False,
            )
            self.assertEqual(checked, 2)
            self.assertEqual(errors, [])
            wb = load_workbook(ao_path, data_only=True)
            ws = wb["Primary Techs"]
            self.assertEqual(ws["G2"].value, "User defined")
            self.assertEqual(ws["I2"].value, 30)
            self.assertEqual(ws["J2"].value, 31)
            wb.close()


if __name__ == "__main__":
    unittest.main()
