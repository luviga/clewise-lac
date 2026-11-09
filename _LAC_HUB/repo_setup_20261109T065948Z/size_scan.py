import csv, sys, os, collections
src, out = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding="utf-8")))
big = sorted([r for r in rows if int(r["size_bytes"]) > 10*1024*1024], key=lambda r: -int(r["size_bytes"]))
top = collections.Counter(); ext = collections.Counter(); topn = collections.Counter(); extn = collections.Counter()
for r in rows:
    p = r["path"]; s = int(r["size_bytes"])
    t = p.split("/")[0] if "/" in p else "(root files)"
    e = os.path.splitext(p)[1].lower() or "(none)"
    top[t] += s; topn[t] += 1; ext[e] += s; extn[e] += 1
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["section", "key", "size_bytes", "size_mb", "file_count"])
    for r in big:
        s = int(r["size_bytes"]); w.writerow(["file_over_10MB", r["path"], s, round(s/1048576, 1), 1])
    for k, s in top.most_common():
        w.writerow(["total_by_top_folder", k, s, round(s/1048576, 1), topn[k]])
    for k, s in ext.most_common():
        w.writerow(["total_by_extension", k, s, round(s/1048576, 1), extn[k]])
print(len(big), "files over 10MB;", sum(1 for r in big if int(r["size_bytes"]) > 50*1048576), "over 50MB")
