import csv, sys, collections
inv = {r["path"]: int(r["size_bytes"]) for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
paths = [l.rstrip("\n")[5:-1] for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
c = collections.Counter(); n = collections.Counter()
for p in paths:
    parts = p.split("/")
    for i in range(1, len(parts)):
        d = "/".join(parts[:i])
        if any(k in d for k in ("Executables", "B1_Output_Params", "A2_Output_Params", "Output", "output", "Results", "results")):
            c[d] += inv.get(p, 0); n[d] += 1
for d, s in c.most_common(60):
    print(f"{s/1e6:9.1f} MB {n[d]:5d}  {d}")
