"""Content scan for LAC_REPO_SETUP.
Usage: py -I -B content_scan.py <root> <files_before.csv> <out_dir>
Writes content_scan.csv (secret hits, secret-like file names, licensed docs, backups/caches)
and personal_paths.csv (per-file count of personal path hits).
"""
import csv, os, re, sys, fnmatch, collections

root, inv, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
LIMIT = 50 * 1024 * 1024
BINARY_EXT = {".xlsx", ".xls", ".xlsm", ".pdf", ".zip", ".7z", ".png", ".jpg", ".jpeg", ".gif",
              ".pickle", ".pkl", ".pyc", ".twbx", ".twbr", ".msg", ".docx", ".doc", ".pptx",
              ".parquet", ".h5", ".npy", ".npz", ".exe", ".dll"}

LITERALS = ["sk-ant-", "ghp_", "gho_", "github_pat_", "AKIA", "xox", "-----BEGIN"]
STRONG = {
    "sk-ant-": re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    "ghp_": re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    "gho_": re.compile(r"gho_[A-Za-z0-9]{30,}"),
    "github_pat_": re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    "AKIA": re.compile(r"AKIA[0-9A-Z]{16}"),
    "xox": re.compile(r"xox[abposr]-[A-Za-z0-9\-]{10,}"),
    "-----BEGIN": re.compile(r"-----BEGIN [A-Z ]*(PRIVATE KEY|CERTIFICATE)"),
}
ASSIGN = re.compile(
    r"""(?i)([A-Za-z0-9_.\-]*(?:api_key|apikey|token|secret|password)[A-Za-z0-9_.\-]*)["']?\s*(?:=|:)\s*(?:(["'])(.*?)\2|([^\s,;#)\]}]+))""")
PERSONAL = [b"C:\\Users\\luisfernando", b"C:/Users/luisfernando", b"/c/Users/luisfernando",
            b"C:\\\\Users\\\\luisfernando"]
SECRET_NAMES = [".env", "*.pem", "*.key", "credentials*", "secrets*"]

def mask(s):
    return s[:4] + "****" if len(s) > 4 else s

rows = list(csv.DictReader(open(inv, encoding="utf-8")))
hits = []
personal = collections.Counter()
scanned = 0
skipped_binary = 0
for r in rows:
    p = r["path"]; size = int(r["size_bytes"])
    base = p.rsplit("/", 1)[-1]
    low = base.lower()
    # secret-like file names
    for pat in SECRET_NAMES:
        if fnmatch.fnmatch(low, pat):
            hits.append([p, "", "secret_filename", pat, base])
    ext = os.path.splitext(low)[1]
    if size > LIMIT or ext in BINARY_EXT:
        skipped_binary += 1
        continue
    full = os.path.join(root, p)
    with open(full, "rb") as fh:
        data = fh.read()
    if b"\x00" in data[:8192]:
        skipped_binary += 1
        continue
    scanned += 1
    n = sum(data.count(x) for x in PERSONAL) + data.lower().count(b"c:\\users\\luisfernando".lower()) * 0
    if n:
        personal[p] = n
    text = data.decode("utf-8", errors="replace")
    has_lit = any(l in text for l in LITERALS)
    low_text = text.lower()
    has_name = any(k in low_text for k in ("api_key", "apikey", "token", "secret", "password"))
    if not (has_lit or has_name):
        continue
    for i, line in enumerate(text.splitlines(), 1):
        for lit in LITERALS:
            if lit in line:
                m = STRONG[lit].search(line)
                if m:
                    hits.append([p, i, "secret_literal_strong:" + lit, mask(m.group(0)), "CANDIDATE"])
                else:
                    idx = line.index(lit)
                    ctx = line[max(0, idx - 20): idx + len(lit) + 20].strip()
                    hits.append([p, i, "secret_literal:" + lit, ctx[:80], "weak (no key-shaped value)"])
        ll = line.lower()
        if any(k in ll for k in ("api_key", "apikey", "token", "secret", "password")):
            for m in ASSIGN.finditer(line):
                name = m.group(1)
                val = m.group(3) if m.group(2) else m.group(4)
                if val is None:
                    continue
                hits.append([p, i, "secret_assignment", f"{name} = {mask(val)}", ""])

with open(os.path.join(outdir, "content_scan_raw.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["path", "line", "rule", "matched_masked", "note"])
    w.writerows(hits)
with open(os.path.join(outdir, "personal_paths.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["path", "hits"])
    for k, v in personal.most_common():
        w.writerow([k, v])
print(f"scanned text files: {scanned}; skipped binary/large: {skipped_binary}; secret-rule hits: {len(hits)}; files with personal paths: {len(personal)}")
