"""Scan tracked job files (not downloads) for CR line endings, em dashes and machine paths."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import JOB

pat = re.compile(r"((?<![A-Za-z])[A-Za-z]:[\/][A-Za-z_]|/c/Users|clw_costsrc|AppData)")
n = 0
for d, _, fs in os.walk(JOB):
    if "downloads" in d.replace(JOB, "") or "__pycache__" in d:
        continue
    for fn in fs:
        p = os.path.join(d, fn)
        b = open(p, "rb").read()
        t = b.decode("utf-8", "replace")
        iss = []
        if b"\r" in b: iss.append("CR")
        if chr(0x2014) in t: iss.append("EMDASH")
        m = pat.search(t)
        if m: iss.append("PATH:" + t[max(0, m.start() - 30):m.end() + 30].replace("\n", " "))
        if iss:
            n += 1
            print(os.path.relpath(p, JOB), iss)
print("files with issues:", n)
