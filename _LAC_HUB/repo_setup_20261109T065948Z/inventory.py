"""Inventory every file under MODELS_LAC_5 (excluding this job folder and .git/).
Usage: py -I -B inventory.py <root> <out_csv>
Writes path (relative, forward slashes), size, sha256, mtime (UTC ISO).
"""
import csv, hashlib, os, sys, datetime

root = os.path.abspath(sys.argv[1])
out = sys.argv[2]
JOB = "_LAC_HUB/repo_setup_20261109T065948Z"

rows = []
for dp, dns, fns in os.walk(root):
    rel_dir = os.path.relpath(dp, root).replace("\\", "/")
    if rel_dir == ".":
        rel_dir = ""
    # skip .git at root (created by this job) and job folder
    keep = []
    for d in dns:
        rp = (rel_dir + "/" + d) if rel_dir else d
        if rp == JOB or rp == ".git":
            continue
        keep.append(d)
    dns[:] = keep
    for f in fns:
        rp = (rel_dir + "/" + f) if rel_dir else f
        full = os.path.join(dp, f)
        st = os.stat(full)
        h = hashlib.sha256()
        with open(full, "rb") as fh:
            for chunk in iter(lambda: fh.read(4 * 1024 * 1024), b""):
                h.update(chunk)
        mt = datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        rows.append((rp, st.st_size, h.hexdigest(), mt))

rows.sort()
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["path", "size_bytes", "sha256", "mtime_utc"])
    w.writerows(rows)
print(f"{len(rows)} files, {sum(r[1] for r in rows)} bytes -> {out}")
