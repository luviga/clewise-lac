"""Assemble GAPS_LAC_NDC_SCOUT_<stamp>.md from parts/gaps_hub.md and parts/notes_<code>.md.
Usage: python -I hub_build_gaps.py <job_folder>
Country note headings are pushed down two levels so they sit under Part 2.
"""
import os
import re
import sys

JOB = sys.argv[1]
out = [open(os.path.join(JOB, "parts", "gaps_hub.md"), encoding="utf-8").read().rstrip("\n"), ""]
for code in ["CR", "DR", "ECU", "GUA", "HON", "JAM"]:
    txt = open(os.path.join(JOB, "parts", f"notes_{code}.md"), encoding="utf-8").read().replace("\r", "")
    txt = re.sub(r"^(#+) ", lambda m: "#" * min(len(m.group(1)) + 2, 6) + " ", txt, flags=re.M)
    out.append(txt.rstrip("\n"))
    out.append("")
text = "\n".join(out) + "\n"
if chr(0x2014) in text:
    text = text.replace(chr(0x2014), ", ")
with open(os.path.join(JOB, "GAPS_LAC_NDC_SCOUT_20261121T204620Z.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print(len(text.split()), "words")
