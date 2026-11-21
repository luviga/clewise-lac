"""Dump every sheet of a workbook (read-only) to a text file with sheet and Excel row numbers.

Usage: python -I config_dump.py <workbook> <out_txt>
"""
import sys

import openpyxl


def main():
    wb_path, out_path = sys.argv[1], sys.argv[2]
    wb = openpyxl.load_workbook(wb_path, read_only=True, data_only=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        for ws in wb.worksheets:
            fh.write("##SHEET %s\n" % ws.title)
            for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                vals = ["" if v is None else str(v) for v in row]
                while vals and vals[-1] == "":
                    vals.pop()
                if vals:
                    fh.write("%s!%d\t%s\n" % (ws.title, i, "\t".join(vals)))
    print("written", out_path)


if __name__ == "__main__":
    main()
