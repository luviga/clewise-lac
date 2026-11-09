"""Copy a file to backups/<name>.pre_<stamp>, record SHA-256 of original and copy."""
import csv, hashlib, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
STAMP = "20261109T053358Z"
OUT = Path(__file__).resolve().parent
MAN = OUT / "backups" / "backup_manifest.csv"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
args = sys.argv[1:]
prefix = ""
if args and args[0].startswith("--prefix="):
    prefix = args.pop(0).split("=", 1)[1]
for src in args:
    src = Path(src).resolve()
    before = sha(src)
    dst = OUT / "backups" / f"{prefix}{src.name}.pre_{STAMP}"
    if dst.exists(): raise SystemExit(f"backup exists already: {dst}")
    shutil.copyfile(src, dst)
    after = sha(dst)
    new = not MAN.exists()
    with open(MAN, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["utc", "source", "backup", "sha256_source_before_change", "sha256_backup", "equal"])
        w.writerow([datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), str(src), str(dst), before, after, before == after])
    print(src.name, before, after, before == after)
