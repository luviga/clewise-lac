"""Step 1 / Step 8.1 read-only gate: SHA-256, size, mtime of each main A-O workbook, and
file count, total size, newest mtime of A2_Output_Params, B1_Output_Params, Executables."""
import hashlib, os, sys, csv, datetime
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
ENERGY = {"CostaRica": r"CostaRica\CR_ENERGY\t1_confection", "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
          "Ecuador": r"Ecuador\ECU_Energy", "Guatemala": r"Guatemala\GUA_ENERGY",
          "Honduras": r"Honduras\HON_ENERGY", "Jamaica": r"Jamaica\JAM_ENERGY"}
ts = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rows = []
for c, d in ENERGY.items():
    p = os.path.join(ROOT, d, "A1_Outputs", "A-O_Parametrization.xlsx")
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    st = os.stat(p)
    rows.append([c, "ao_workbook", os.path.relpath(p, ROOT), 1, st.st_size, ts(st.st_mtime), h.hexdigest()])
    for sub in ["A2_Output_Params", "B1_Output_Params", "Executables"]:
        q = os.path.join(ROOT, d, sub); n = s = 0; newest = 0.0
        if os.path.isdir(q):
            for dp, dn, fn in os.walk(q):
                for f in fn:
                    st = os.stat(os.path.join(dp, f)); n += 1; s += st.st_size; newest = max(newest, st.st_mtime)
            rows.append([c, sub, os.path.relpath(q, ROOT), n, s, ts(newest) if n else "", ""])
        else:
            rows.append([c, sub, os.path.relpath(q, ROOT), "MISSING", "", "", ""])
with open(sys.argv[1], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["country", "item", "relpath", "file_count", "size_bytes", "mtime_utc_newest", "sha256"]); w.writerows(rows)
for r in rows: print(r)
