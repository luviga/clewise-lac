"""Self check of targets_JAM.csv and projections_JAM.csv: is each value printed on the cited pages?

Usage: python -I self_check_JAM.py <job_dir> <out_txt>
Searches several printed forms of the number (with thousands separators, trailing zeros,
spaced digits) in the text cache; reports rows not found. Writes only <out_txt>.
"""
import csv
import os
import re
import sys

JOB, OUT = sys.argv[1], sys.argv[2]


def pages_of(s):
    out = []
    for part in re.split(r"[;,]", s):
        m = re.match(r"^\s*p\.(\d+)\s*$", part)
        if m:
            out.append(int(m.group(1)))
    return out


def forms(v):
    v = v.strip()
    if not v:
        return []
    try:
        f = float(v)
    except ValueError:
        return []
    out = {v}
    if f == int(f):
        i = int(f)
        out |= {str(i), "{:,}".format(i), "{:,}".format(i).replace(",", " "), "%d.0" % i}
    else:
        s = ("%f" % f).rstrip("0")
        out |= {s, s.lstrip("0") if s.startswith("0.") else s, ("%.2f" % f), ("%.1f" % f)}
        if abs(f) >= 1000:
            ip, dp = s.split(".")
            out.add("{:,}".format(int(ip)) + "." + dp)
    return [x for x in out if x]


def norm(t):
    return re.sub(r"\s+", " ", t)


def found(text, v):
    t = norm(text)
    t2 = t.replace(" ", "")
    for f in forms(v):
        pat = r"(?<![\d.])" + re.escape(f) + r"(?![\d])"
        if re.search(pat, t) or re.search(pat, t2):
            return True
    return False


lines = []
for fname, idcol, valcol in [("targets_JAM.csv", "target_id", "value"), ("projections_JAM.csv", None, "value")]:
    with open(os.path.join(JOB, fname), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    nf = 0
    for i, r in enumerate(rows, start=2):
        v = r[valcol]
        rid = r[idcol] if idcol else "%s line %d" % (fname, i)
        if not v.strip():
            lines.append("NOVALUE %s" % rid)
            continue
        ok = False
        for p in pages_of(r["page"]):
            path = os.path.join(JOB, "downloads", "JAM", "text", r["source_id"], "p%d.txt" % p)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as fh:
                    if found(fh.read(), v):
                        ok = True
                        break
        if not ok:
            nf += 1
            lines.append("NOTFOUND %s %s %s value=%s" % (rid, r["source_id"], r["page"], v))
    lines.append("%s rows %d not found %d" % (fname, len(rows), nf))

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
