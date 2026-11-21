"""Index of B1_Scenario_Config.xlsx rows for selected scenarios (read-only).

Usage: python -I config_index.py <workbook> <out_txt> [scenario ...]
Writes sheet, Excel row number and the first 14 cells of each row whose first cell is one of the
scenarios (default NDCNEW LTSNEW BAU), plus the header row of each sheet.
"""
import sys

import openpyxl


def main():
    wb_path, out = sys.argv[1], sys.argv[2]
    scen = set(sys.argv[3:]) or {"NDCNEW", "LTSNEW", "BAU"}
    wb = openpyxl.load_workbook(wb_path, read_only=True, data_only=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for ws in wb.worksheets:
            for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                cells = ["" if v is None else str(v) for v in row]
                if i == 1 or (cells and cells[0] in scen):
                    fh.write(f"{ws.title}\t{i}\t" + " | ".join(cells[:14]) + "\n")
    print("done")


if __name__ == "__main__":
    main()
