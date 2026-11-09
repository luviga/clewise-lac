"""Gate 7 scan: em dashes and machine paths (outside URLs) in the job's tracked text files.
Usage: py -I scan_text.py <list_of_files_txt> <out_txt>
The scan skips its own output file. Pattern pieces are built from parts so that this script does not match itself."""
import os
import sys
import re

BS = "\\"
EM = chr(0x2014)
PATH = re.compile(
    r"((?:^|[\s`'\"(=,;\[])[A-Za-z]:[/" + BS + BS + r"]"
    r"|(?:^|[\s`'\"(=,;\[])/c/[A-Za-z]"
    r"|" + BS + BS + "Us" + "ers" + BS + BS +
    r"|/" + "Us" + "ers/|App" + "Data|clw_" + "local_prices|Desk" + "top[/" + BS + BS + r"]OSeMOSYS)")
URL = re.compile(r"https?://\S+")
out = []
n_em = n_path = 0
skip = os.path.basename(sys.argv[2])
for f in open(sys.argv[1], encoding="utf-8").read().split():
    if os.path.basename(f) == skip:
        continue
    for i, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        if EM in line:
            n_em += 1
            out.append(f"EMDASH {f}:{i}")
        if PATH.search(URL.sub("", line)):
            n_path += 1
            out.append(f"PATH {f}:{i}: {line.strip()[:160]}")
out.append(f"em dash lines: {n_em}; machine path lines: {n_path}")
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print(out[-1])
for f in sorted(set(x.split(" ")[1].split(":")[0] for x in out[:-1])):
    print(" ", f)
