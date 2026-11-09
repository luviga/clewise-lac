"""Dump words with coordinates from page 1 of a PDF (inspection helper). Usage: py -I dr_dump_words.py <pdf> [page]"""
import sys, pdfplumber
pdf = pdfplumber.open(sys.argv[1])
pg = int(sys.argv[2]) if len(sys.argv) > 2 else 0
for w in pdf.pages[pg].extract_words():
    print(round(w['x0'], 1), round(w['x1'], 1), round(w['top'], 1), w['text'])
