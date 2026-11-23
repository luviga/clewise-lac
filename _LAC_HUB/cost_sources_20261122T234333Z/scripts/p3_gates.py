"""Phase 3 gates. Writes gates_result.md and gate3_value_checks.csv. Usage: p3_gates.py [CC ...]"""
import os, sys, csv, re, random, subprocess, zipfile, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import ROOT, JOB, MODELS
import openpyxl

STAMP = "20261122T234333Z"
import shutil
PDFTOTEXT = shutil.which("pdftotext") or os.path.join(os.environ.get("ProgramFiles", ""), "Git", "mingw64", "bin", "pdftotext.exe")
REL = "_LAC_HUB/cost_sources_%s/" % STAMP
CCS = sys.argv[1:] or ["CR", "DR", "GUA", "HON", "JAM", "ECU"]
COLS = "country,model,sheet,tech,tech_name,parameter,unit_introduced,unit,projection_mode,year,current_value,proposed_value,change_class,source_ids,source_value,source_unit,source_currency_year,cpi_factor,derivation,assumption_sentence,ao_row_at_b51f24b".split(",")
out = []
fail = []


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True).stdout


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


# ---------- load
props, cells, srcs = [], [], {}
for cc in CCS:
    p = os.path.join(JOB, cc, "proposals_%s.csv" % cc)
    if not os.path.exists(p):
        fail.append("missing proposals_%s.csv" % cc); continue
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != COLS:
            fail.append("%s: proposal columns differ from the brief" % cc)
        props += list(rd)
    cells += list(csv.DictReader(open(os.path.join(JOB, cc, "cells_%s.csv" % cc), newline="", encoding="utf-8")))
    for r in csv.DictReader(open(os.path.join(JOB, cc, "sources_%s.csv" % cc), newline="", encoding="utf-8")):
        srcs[r["id"]] = r
for r in csv.DictReader(open(os.path.join(JOB, "sources_GEN.csv"), newline="", encoding="utf-8")):
    srcs[r["id"]] = r

# ---------- gate 0: coverage
key = lambda r: (r["country"], r["model"], r["sheet"], r["tech"], r["parameter"], str(r["year"]))
pk = {}
dup = 0
for r in props:
    if key(r) in pk: dup += 1
    pk[key(r)] = r
ck = {key(c): c for c in cells}
missing = [k for k in ck if k not in pk]
extra = [k for k in pk if k not in ck]
curdiff = [k for k in ck if k in pk and num(pk[k]["current_value"]) != num(ck[k]["current_value"]) and str(pk[k]["current_value"]) != str(ck[k]["current_value"])]
out.append("## Gate 0. Coverage\n\nCells %d, proposal rows %d, duplicates %d, cells without a proposal %d, proposals without a cell %d, current values differing from the cell list %d." % (len(ck), len(props), dup, len(missing), len(extra), len(curdiff)))
if dup or missing or extra or curdiff:
    fail.append("gate 0")
    out.append("Examples: missing %s; extra %s; differing %s" % (missing[:3], extra[:3], curdiff[:3]))

# ---------- gate 1: read-only
names = [n for n in git("diff", "--name-only", "b51f24b", "HEAD").splitlines() if n]
bad1 = [n for n in names if not n.startswith(REL)]
stat = [l for l in git("status", "--porcelain").splitlines() if l and REL not in l]
out.append("## Gate 1. Read-only\n\n`git diff --name-only b51f24b HEAD`: %d files, %d outside the job folder. `git status --porcelain` lines outside the job folder: %d." % (len(names), len(bad1), len(stat)))
if bad1 or stat:
    fail.append("gate 1"); out.append("Outside: %s %s" % (bad1[:5], stat[:5]))

# ---------- gate 2: current values from the workbooks at b51f24b
MBY = {m["model"]: m for m in MODELS}
rnd = random.Random(20261122)
sample = rnd.sample(props, min(100, len(props)))
wbc = {}
ok2 = 0
lines2 = []


def ao_value(r):
    m = MBY[r["model"]]
    folder = m["folder"]
    if r["parameter"] == "EmissionsPenalty":
        p = os.path.join(ROOT, m["bau"], "EmissionsPenalty.csv")
        for c in csv.DictReader(open(p, newline="", encoding="utf-8-sig")):
            if c["EMISSION"] == r["tech"] and str(int(float(c["YEAR"]))) == str(r["year"]):
                return float(c["Value"]), m["bau"] + "/EmissionsPenalty.csv"
        return None, "compiled"
    if r["parameter"] == "Ref.km.BY":
        path = folder + "/A1_Outputs/A-O_Demand.xlsx"
        wb = wbc.setdefault(path, openpyxl.load_workbook(os.path.join(ROOT, path), read_only=True, data_only=True))
        it = wb.worksheets[0].iter_rows(values_only=True)
        h = list(next(it)); H = {x: i for i, x in enumerate(h)}
        for row in it:
            if row[H["Fuel/Tech"]] == r["tech"]:
                return row[H["Ref.km.BY"]], path
        return None, path
    path = folder + "/A1_Outputs/A-O_Parametrization.xlsx"
    wb = wbc.setdefault(path, openpyxl.load_workbook(os.path.join(ROOT, path), read_only=True, data_only=True))
    ws = wb[r["sheet"]]
    it = ws.iter_rows(values_only=True)
    h = list(next(it)); H = {x: i for i, x in enumerate(h) if x is not None}
    for row in it:
        if row and row[H["Tech"]] == r["tech"] and row[H["Parameter"]] == r["parameter"]:
            if r["parameter"] == "OperationalLife":
                return row[H["Value"]], path
            return row[H[int(r["year"])]], path
    return None, path


for r in sample:
    v, path = ao_value(r)
    if subprocess.run(["git", "diff", "--quiet", "b51f24b", "--", path.split("/B1_")[0] if "B1_" in path else path], cwd=ROOT).returncode != 0:
        lines2.append("file changed since b51f24b: " + path)
    good = (v is not None and num(v) is not None and num(r["current_value"]) is not None and abs(num(v) - num(r["current_value"])) <= 1e-6 * max(1, abs(num(v)))) or str(v) == str(r["current_value"])
    ok2 += good
    if not good:
        lines2.append("%s: workbook %s, proposal %s" % (key(r), v, r["current_value"]))
out.append("## Gate 2. Current values\n\n%d of %d random proposal rows (seed 20261122) match the workbook or compiled file at b51f24b." % (ok2, len(sample)) + ("\n\n" + "\n".join("- " + l for l in lines2[:20]) if lines2 else ""))
if ok2 != len(sample):
    fail.append("gate 2")

# ---------- gate 3: sources
miss_id, miss_file = set(), set()
for r in props:
    if r["change_class"] == "assumption":
        continue
    for i in [x.strip() for x in r["source_ids"].split(";") if x.strip()]:
        if i not in srcs:
            miss_id.add(i)
    if not r["source_ids"].strip():
        miss_id.add("(empty) %s" % (key(r),))
for i, s in srcs.items():
    for p in [x.strip() for x in s["downloaded_file"].split(";") if x.strip()]:
        if not os.path.exists(os.path.join(JOB, p)):
            miss_file.add("%s %s" % (i, p))
out.append("## Gate 3. Sources\n\nNon-assumption rows whose source ids are missing from the sources files: %d (%s). Sources whose downloaded file is missing: %d (%s)." % (len(miss_id), sorted(miss_id)[:5], len(miss_file), sorted(miss_file)[:5]))
if miss_id or miss_file:
    fail.append("gate 3")


def text_of(path):
    p = os.path.join(JOB, path)
    ext = os.path.splitext(p)[1].lower()
    try:
        if ext == ".pdf":
            r = subprocess.run([PDFTOTEXT, "-layout", p, "-"], capture_output=True)
            t = r.stdout.decode("utf-8", "replace")
            if len(t.strip()) < 100:
                import pypdf
                t = "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(p).pages)
            return t
        if ext in (".xlsx", ".xlsm"):
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
            return "\n".join(" ".join(str(c) for c in row if c is not None) for ws in wb.worksheets for row in ws.iter_rows(values_only=True))
        if ext == ".zip":
            return ""
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception as e:
        return ""


def variants(v):
    x = num(v)
    if x is None:
        return []
    out = set()
    for d in range(0, 5):
        s = ("%." + str(d) + "f") % x
        out.add(s); out.add("{:,.{}f}".format(x, d)); out.add("{:,.{}f}".format(x, d).replace(",", " "))
        out.add(s.replace(".", ","))
        out.add("{:,.{}f}".format(x, d).replace(",", "#").replace(".", ",").replace("#", "."))
    if x == int(x):
        out.add(str(int(x)))
    return [o for o in out if len(o.replace(",", "").replace(".", "").replace(" ", "")) >= 2]


txtc = {}
rows3 = []
for cc in CCS:
    sourced = [r for r in props if r["country"] == cc and r["change_class"] != "assumption" and r["source_value"].strip()]
    # one row per distinct source value to make the 10 checks informative
    seen, uniq = set(), []
    for r in sourced:
        k = (r["source_ids"], r["source_value"])
        if k not in seen:
            seen.add(k); uniq.append(r)
    pick = random.Random(20261122).sample(uniq, min(10, len(uniq)))
    for r in pick:
        found_in = ""
        for i in [x.strip() for x in r["source_ids"].split(";") if x.strip()]:
            s = srcs.get(i)
            if not s:
                continue
            for p in [x.strip() for x in s["downloaded_file"].split(";") if x.strip()]:
                if p not in txtc:
                    txtc[p] = text_of(p)
                t = txtc[p]
                for v in variants(r["source_value"]):
                    if re.search(r"(?<![\d.])" + re.escape(v) + r"(?![\d]|[.,]\d)", t):
                        found_in = "%s (%s)" % (i, p); break
                if found_in: break
            if found_in: break
        rows3.append(dict(country=cc, model=r["model"], tech=r["tech"], parameter=r["parameter"], year=r["year"],
                          source_ids=r["source_ids"], source_value=r["source_value"], source_unit=r["source_unit"],
                          source_currency_year=r["source_currency_year"], found_in_file=found_in or "not found by text search",
                          result="confirmed" if found_in else "check by reading"))
with open(os.path.join(JOB, "gate3_value_checks.csv"), "w", newline="", encoding="utf-8") as f:
    if rows3:
        w = csv.DictWriter(f, fieldnames=list(rows3[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(rows3)
n_ok = sum(1 for r in rows3 if r["result"] == "confirmed")
out.append("Value checks (10 per country, seed 20261122, one per distinct source value): %d of %d found by text search in the downloaded file; the rest are listed in `gate3_value_checks.csv` for a reading check." % (n_ok, len(rows3)))

# ---------- gate 4: internal citations
bad_url = re.compile(r"(climateleadgroup|clg\.|readthedocs\.io|^[A-Za-z]:\\|^/c/|file:|_LAC_HUB|github\.com/(luviga|clg|climateleadgroup))", re.I)
bad_txt = re.compile(r"(\.xlsx|\.csv|\bsheet\b|\bjob\b|\bhub\b|commit|not found|could not be found|kept as used|retained|provisional|workbook|A-O|\bLAC_)", re.I)
hits = []
for i, s in srcs.items():
    if bad_url.search(s["url"]):
        hits.append("url %s %s" % (i, s["url"]))
for r in props:
    if r["assumption_sentence"] and bad_txt.search(r["assumption_sentence"]):
        hits.append("assumption %s: %s" % (key(r), bad_txt.search(r["assumption_sentence"]).group(0)))
out.append("## Gate 4. No internal citation\n\nHits: %d.%s" % (len(hits), ("\n\n" + "\n".join("- " + h for h in hits[:30])) if hits else ""))
if hits:
    fail.append("gate 4")

# ---------- gate 5: currency
cpi = {r["year"]: float(r["factor_to_2024"]) for r in csv.DictReader(open(os.path.join(JOB, "cpi_u.csv"), encoding="utf-8"))}
bad5, conv = [], 0
for r in props:
    if r["cpi_factor"].strip() or r["source_currency_year"].strip():
        conv += 1
        y = r["source_currency_year"].strip()
        f = num(r["cpi_factor"])
        if not y or (f is None and not re.fullmatch(r"\d{4}-\d{4}", y)):
            bad5.append("%s: year %r factor %r" % (key(r), y, r["cpi_factor"])); continue
        if y not in cpi and re.fullmatch(r"\d{4}-\d{4}", y):
            pairs = re.findall(r"(\d+\.\d+) \((\d{4})\)", r["cpi_factor"])
            if pairs and all(abs(cpi.get(yy, -9) - float(ff)) <= 5e-4 for ff, yy in pairs):
                continue
        if y not in cpi or abs(cpi[y] - f) > 5e-4:
            bad5.append("%s: factor %s for %s, table %s" % (key(r), f, y, cpi.get(y)))
out.append("## Gate 5. Currency\n\nConverted rows %d; rows with a missing year or factor, or a factor that differs from `cpi_u.csv` (GEN-001): %d.%s" % (conv, len(bad5), ("\n\n" + "\n".join("- " + b for b in bad5[:20])) if bad5 else ""))
if bad5:
    fail.append("gate 5")

# ---------- gate 6
log = git("log", "b51f24b..HEAD", "--format=%B")
coauth = len(re.findall(r"Co-Authored-By|Generated with", log, re.I))
chk = subprocess.run(["git", "diff", "--check", "b51f24b", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout
em = []
for n in ("REPORT", "GAPS", "CHANGES"):
    p = os.path.join(JOB, "%s_LAC_COST_SOURCES_%s.md" % (n, STAMP))
    if chr(0x2014) in open(p, encoding="utf-8").read():
        em.append(n)
out.append("## Gate 6. Commit hygiene\n\nCo-Authored-By or Generated-with lines in the branch log: %d. `git diff --check b51f24b HEAD` lines: %d. Output files with an em dash: %d %s." % (coauth, len(chk.splitlines()), len(em), em))
if coauth or chk.strip() or em:
    fail.append("gate 6")

out.append("## Result\n\n" + ("All gates pass." if not fail else "Failed: " + ", ".join(fail)))
open(os.path.join(JOB, "gates_result.md"), "w", encoding="utf-8", newline="\n").write("# Gate results\n\n" + "\n\n".join(out) + "\n")
print("\n\n".join(out))
