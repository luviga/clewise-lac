"""SHA-256 of the six main A-O energy workbooks and the fuel workbook (read-only gate)."""
import hashlib, sys, os, csv, datetime
ROOT = r"C:\Users\luisfernando\Desktop\OSeMOSYS\MODELS_LAC_5"
FILES = [
 r"CostaRica\CR_ENERGY\t1_confection\A1_Outputs\A-O_Parametrization.xlsx",
 r"DominicanRepublic\RD_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 r"Ecuador\ECU_Energy\A1_Outputs\A-O_Parametrization.xlsx",
 r"Guatemala\GUA_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 r"Honduras\HON_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 r"Jamaica\JAM_ENERGY\A1_Outputs\A-O_Parametrization.xlsx",
 r"LAC_Fuel_Price_Projections_2026_v2_audit.xlsx",
]
out = sys.argv[1]
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["file","bytes","mtime_utc","sha256","hashed_at_utc"])
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        h = hashlib.sha256(open(p,"rb").read()).hexdigest()
        st = os.stat(p)
        w.writerow([rel, st.st_size, datetime.datetime.utcfromtimestamp(st.st_mtime).isoformat(), h,
                    datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")])
print(open(out).read())
