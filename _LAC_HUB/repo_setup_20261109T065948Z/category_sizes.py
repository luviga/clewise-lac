import csv, sys, collections, re
inv = {r["path"]: int(r["size_bytes"]) for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
paths = [l.rstrip("\n")[5:-1] for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
cats = collections.Counter(); n = collections.Counter(); ex = collections.Counter()
for p in paths:
    s = inv.get(p, 0)
    if "/Executables/" in p:
        k = "Executables"
        if p.lower().endswith((".py", ".bat", ".sh")): ex["Executables scripts"] += 1
    elif "/B1_Output_Params/" in p: k = "B1_Output_Params"
    elif "/A2_Output_Params/" in p: k = "A2_Output_Params"
    else: k = "other"
    cats[k] += s; n[k] += 1
for k, s in cats.most_common(): print(f"{k:20s} {s/1e6:8.1f} MB {n[k]:6d} files")
print(ex)
total = sum(cats.values()); print("total", total, "need to drop", total - 2_000_000_000)
