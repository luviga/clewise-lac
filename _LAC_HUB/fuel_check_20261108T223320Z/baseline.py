"""Step 1 / Step 6 baseline: SHA-256, size, mtime of the fuel workbook, the tool,
and every A-O_Parametrization*.xlsx under each country's energy A1_Outputs/."""
import hashlib, os, sys, csv, datetime, glob
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
ENERGY = {
    "CostaRica": r"CostaRica\CR_ENERGY\t1_confection\A1_Outputs",
    "DominicanRepublic": r"DominicanRepublic\RD_ENERGY\A1_Outputs",
    "Ecuador": r"Ecuador\ECU_Energy\A1_Outputs",
    "Guatemala": r"Guatemala\GUA_ENERGY\A1_Outputs",
    "Honduras": r"Honduras\HON_ENERGY\A1_Outputs",
    "Jamaica": r"Jamaica\JAM_ENERGY\A1_Outputs",
}
files = [("fuel_workbook", "LAC_Fuel_Price_Projections_2026_v2_audit.xlsx"),
         ("tool", "ao_cost_repair_manager.py")]
for c, d in ENERGY.items():
    for p in sorted(glob.glob(os.path.join(ROOT, d, "**", "A-O_Parametrization*.xlsx"), recursive=True)):
        files.append((c, os.path.relpath(p, ROOT)))
out = sys.argv[1]
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["role", "relpath", "size_bytes", "mtime_utc", "sha256"])
    for role, rel in files:
        p = os.path.join(ROOT, rel); h = hashlib.sha256()
        with open(p, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
        st = os.stat(p)
        w.writerow([role, rel, st.st_size,
                    datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    h.hexdigest()])
print(len(files), "files ->", out)
