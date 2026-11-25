"""Usage: python -I findpage.py file.pdf "regex" [context_lines] [raw]
Runs pdftotext (layout or raw) and prints PDF page number and matching lines with context."""
import re, subprocess, sys
pdf, pat = sys.argv[1], sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
mode = "-raw" if (len(sys.argv) > 4 and sys.argv[4] == "raw") else "-layout"
exe = r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"
txt = subprocess.run([exe, mode, "-enc", "UTF-8", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
sys.stdout.reconfigure(encoding="utf-8")
rx = re.compile(pat, re.I)
for pno, page in enumerate(txt.split("\f"), start=1):
    lines = page.splitlines()
    for i, l in enumerate(lines):
        if rx.search(l):
            print(f"--- p{pno} line {i}")
            for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
                print(("> " if j == i else "  ") + lines[j])
