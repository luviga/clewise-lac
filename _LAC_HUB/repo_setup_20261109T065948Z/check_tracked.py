"""Check a tracked list (git add --dry-run output, or plain git ls-files output) against files_before.csv.
Usage: py -I -B check_tracked.py <files_before.csv> <list.txt> <dryrun|lsfiles> <out_excluded.csv>
Prints count, total size, max size, files over 50 MB, and paths not found in the inventory.
Writes every inventory file NOT in the list (excluded set) to out_excluded.csv.
"""
import csv, sys
inv = {r["path"]: int(r["size_bytes"]) for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
mode = sys.argv[3]
paths = []
for line in open(sys.argv[2], encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    if mode == "dryrun":
        assert line.startswith("add '") and line.endswith("'"), line
        line = line[5:-1]
    paths.append(line)
new = {".gitignore", ".gitattributes"}
missing = [p for p in paths if p not in inv and p not in new]
sizes = [inv.get(p, 0) for p in paths]
total = sum(sizes)
over = [p for p in paths if inv.get(p, 0) > 50 * 1048576]
print(f"count={len(paths)} total_bytes={total} total_GB={total/1024**3:.3f} max_bytes={max(sizes)} over50MB={len(over)} not_in_inventory={len(missing)}")
for p in missing[:20]:
    print("  not in inventory:", p)
s = set(paths)
excl = [(p, n) for p, n in sorted(inv.items()) if p not in s]
with open(sys.argv[4], "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["path", "size_bytes"]); w.writerows(excl)
print(f"excluded={len(excl)} excluded_bytes={sum(n for _, n in excl)}")
