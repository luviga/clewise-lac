"""Print sheet names, dimensions and header row of each main A-O workbook (read-only)."""
import os
from openpyxl import load_workbook
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
ENERGY = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
          "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
          "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
for c, d in ENERGY.items():
    wb = load_workbook(os.path.join(ROOT, d, "A1_Outputs", "A-O_Parametrization.xlsx"), read_only=True)
    print("==", c, "lastModifiedBy=", wb.properties.lastModifiedBy, "modified=", wb.properties.modified, "creator=", wb.properties.creator)
    for ws in wb.worksheets:
        hdr = [h for h in next(ws.iter_rows(min_row=1, max_row=1, values_only=True)) if h is not None]
        print("  ", ws.title, "| dims", ws.calculate_dimension(), "|", hdr[:12], "...", hdr[-2:])
