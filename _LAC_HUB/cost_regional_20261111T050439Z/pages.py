"""Print pages of an extracted text file whose text matches a regex (scratch helper)."""
import sys, re, unicodedata
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
txt = open(sys.argv[1], encoding="utf-8").read()
pages = re.split(r"\n=====PAGE (\d+)=====\n", txt)
pat = re.compile(sys.argv[2], re.I)
only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else None
for i in range(1, len(pages), 2):
    no, body = pages[i], pages[i + 1]
    if (only is None and pat.search(body)) or (only and no in only):
        print(f"=====PAGE {no}=====\n" + body.replace("\n", "|")[:6000])
