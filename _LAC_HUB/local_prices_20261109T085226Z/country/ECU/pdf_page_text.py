"""Print layout text of given PDF pages. Usage: py -I pdf_page_text.py <pdf> <page1> [<page2> ...] (1-based)"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pdfplumber

pdf = sys.argv[1]
with pdfplumber.open(pdf) as d:
    for n in [int(x) for x in sys.argv[2:]]:
        print(f"===== page {n} =====")
        print(d.pages[n - 1].extract_text(layout=False) or "")
