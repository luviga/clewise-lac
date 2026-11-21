"""Print the NDCNEW and LTSNEW rows of B1_Scenario_Config.xlsx (read-only) with Excel row numbers.

Usage: python -I config_index.py <xlsx> [sheet ...]
"""
import sys

import openpyxl


def main():
    path = sys.argv[1]
    sheets = sys.argv[2:]
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        if sheets and ws.title not in sheets:
            continue
        header = None
        for r, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if r == 1:
                header = list(row)
                continue
            if row and row[0] in ("NDCNEW", "LTSNEW", "BAU"):
                d = {str(h): v for h, v in zip(header, row) if h is not None}
                keep = {k: d[k] for k in d if k not in ("Description Parameter-Set",)}
                txt = "; ".join(f"{k}={str(v)[:140]}" for k, v in keep.items() if v not in (None, ""))
                print(f"{ws.title} row {r}: {txt[:900]}")


if __name__ == "__main__":
    main()
