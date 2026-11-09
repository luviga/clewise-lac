"""Convert CRLF line endings to LF and strip trailing spaces and tabs at line ends, in the job's tracked text
files (.csv, .md, .py, .txt outside downloads/), so that `git diff --check` passes. Content is otherwise unchanged.
Also makes baseline.py and consumers.py write LF.
Usage: py -I normalize_eol.py <job_folder>"""
import os
import re
import sys

job = sys.argv[1]
for name in ("baseline.py", "consumers.py"):
    p = os.path.join(job, "scripts", name)
    s = open(p, encoding="utf-8").read()
    s = s.replace("w = csv.writer(fh)", 'w = csv.writer(fh, lineterminator="' + "\\" + 'n")')
    open(p, "w", encoding="utf-8", newline="").write(s)
changed = 0
for root, dirs, files in os.walk(job):
    if "downloads" in os.path.relpath(root, job).split(os.sep):
        continue
    for f in files:
        if not f.endswith((".csv", ".md", ".py", ".txt")):
            continue
        p = os.path.join(root, f)
        raw = open(p, "rb").read()
        new = re.sub(rb"[ \t]+(\r?\n)", rb"\1", raw).replace(b"\r\n", b"\n")
        new = re.sub(rb"[ \t]+$", b"", new)
        if new != raw:
            open(p, "wb").write(new)
            changed += 1
print(changed, "files normalised")
