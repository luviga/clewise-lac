"""Gates of LAC_VEHICLE_PRICES. Writes gates_result.md in the job folder.

    python -I scripts/gates.py <scope count expected, 2892>
Gate 4 copies the job's inputs into a clean folder under the system temporary directory and runs
build_prices.py there.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(JOB))
JOBREL = os.path.relpath(JOB, REPO).replace("\\", "/")
CCS = ["CR", "DR", "GUA", "HON", "JAM"]
ALLOWED = {"customs", "trade_statistics_reported_by_country", "fiscal_valuation_table"}
csv.field_size_limit(10_000_000)


def rd(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(a, b, rel=1e-9):
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def gate1(expected):
    scope = rd(os.path.join(JOB, "scope_cells.csv"))
    keys = {(r["country"], r["model"], r["tech"], r["year"]) for r in scope}
    seen, dup, extra = {}, 0, 0
    for cc in CCS:
        for r in rd(os.path.join(JOB, cc, f"proposals_{cc}.csv")):
            k = (r["country"], r["model"], r["tech"], r["year"])
            if k in seen:
                dup += 1
            seen[k] = 1
            if k not in keys:
                extra += 1
    missing = len(keys - set(seen))
    ok = len(keys) == expected and dup == 0 and extra == 0 and missing == 0
    return ok, f"{len(seen)} proposal rows for {len(keys)} cells in scope (expected {expected}); missing {missing}, duplicate {dup}, extra {extra}"


def gate2():
    import openpyxl
    books, bad, n = {}, [], 0
    for cc in CCS:
        for r in rd(os.path.join(JOB, cc, f"proposals_{cc}.csv")):
            m = re.match(r"(.+?), sheet (.+?), row (\d+), column (\d+)", r["ao_row_at_b51f24b"])
            path, sheet, row, col = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            if path not in books:
                books[path] = openpyxl.load_workbook(os.path.join(REPO, path), data_only=True, read_only=True)
            ws = books[path][sheet]
            if (path, sheet) not in books:
                hdr = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
                books[(path, sheet)] = {str(h).strip(): j for j, h in enumerate(hdr) if h is not None}
                books[(path, sheet, "rows")] = list(ws.iter_rows(values_only=True))
            j = books[(path, sheet)][col]
            v = books[(path, sheet, "rows")][row - 1][j]
            n += 1
            try:
                same = close(float(v), float(r["current_value"]))
            except (TypeError, ValueError):
                same = str(v) == r["current_value"]
            if not same:
                bad.append(f"{cc} {r['tech']} {r['year']}: workbook {v}, file {r['current_value']}")
    return not bad, f"{n} cells read from the workbooks of the checked-out tree; {len(bad)} differ" + (
        ": " + "; ".join(bad[:5]) if bad else "")


def gate3():
    bad, n = [], 0
    for cc in CCS:
        types = {r["id"]: r["source_type"] for r in rd(os.path.join(JOB, cc, f"sources_{cc}.csv"))}
        for r in rd(os.path.join(JOB, cc, f"proposals_{cc}.csv")):
            if r["assumption_sentence"].strip():
                continue
            n += 1
            for s in [x for x in r["source_ids"].split(";") if x]:
                if types.get(s) not in ALLOWED:
                    bad.append(f"{cc} {r['tech']} {r['year']} cites {s} ({types.get(s)})")
    return not bad, f"{n} non-ASSUMPTION rows; {len(bad)} cite a source of another type" + (
        ": " + "; ".join(bad[:5]) if bad else "")


def gate4():
    tmp = tempfile.mkdtemp(prefix="vehprice_gate4_")
    dst = os.path.join(tmp, "job")
    os.makedirs(dst)
    for name in ["scripts", "downloads"]:
        shutil.copytree(os.path.join(JOB, name), os.path.join(dst, name),
                        ignore=shutil.ignore_patterns("__pycache__"))
    for name in ["parameters.csv", "vehicle_class_map.csv", "national_type_map.csv"]:
        shutil.copy(os.path.join(JOB, name), dst)
    for cc in CCS:
        os.makedirs(os.path.join(dst, cc))
    res = subprocess.run([sys.executable, "-I", os.path.join(dst, "scripts", "build_prices.py")],
                         capture_output=True, text=True)
    if res.returncode:
        return False, "build_prices.py failed in the clean folder: " + res.stderr[-300:]
    bad, n = [], 0
    for cc in CCS:
        clean = {r["tech"]: r for r in rd(os.path.join(dst, cc, f"class_prices_{cc}.csv"))}
        mine = {r["tech"]: r for r in rd(os.path.join(JOB, cc, f"class_prices_{cc}.csv"))}
        if clean != mine:
            bad.append(f"{cc} class prices differ")
        props = rd(os.path.join(JOB, cc, f"proposals_{cc}.csv"))
        by = {}
        for r in props:
            by.setdefault(r["tech"], []).append(r)
        for tech, rs in by.items():
            if tech == "TRNPASRAIELE":
                continue
            rs.sort(key=lambda r: int(r["year"]))
            unit = rs[0]["unit_introduced_proposed"]
            price = float(clean[tech]["base_price_usd2024"])
            if cc == "CR":
                r24 = [r for r in rs if r["year"] == "2024"][0]
                n += 1
                if not close(float(r24["proposed_value"]), round(price, 2)):
                    bad.append(f"{cc} {tech} 2024 {r24['proposed_value']} vs {price}")
                continue
            r0 = rs[0]
            n += 1
            if unit.startswith("Relative to"):
                ref = unit.replace("Relative to", "").strip()
                want = round(price / float(clean[ref]["base_price_usd2024"]), 6)
            else:
                want = round(price, 2)
            if not close(float(r0["proposed_value"]), want):
                bad.append(f"{cc} {tech} {r0['year']} {r0['proposed_value']} vs {want}")
    shutil.rmtree(tmp, ignore_errors=True)
    return not bad, f"clean run reproduces the class prices of all five countries; {n} base-year cells checked; {len(bad)} differ" + (
        ": " + "; ".join(bad[:5]) if bad else "")


def opens(path):
    p = path.lower()
    if p.endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return len(pdf.pages) > 0
    if p.endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True)
        ok = len(wb.sheetnames) > 0
        wb.close()
        return ok
    if p.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            json.load(f)
        return True
    if p.endswith(".zip"):
        return zipfile.ZipFile(path).testzip() is None
    if p.endswith(".csv"):
        with open(path, encoding="utf-8-sig", errors="strict") as f:
            return len(f.readline()) > 0
    return os.path.getsize(path) > 0


def gate5():
    bad, n = [], 0
    seen = set()
    for cc in CCS:
        for r in rd(os.path.join(JOB, cc, f"sources_{cc}.csv")):
            for fpath in [x.strip() for x in r["downloaded_file"].split(";") if x.strip()]:
                if fpath in seen:
                    continue
                seen.add(fpath)
                n += 1
                full = os.path.join(JOB, fpath)
                try:
                    if not (os.path.exists(full) and opens(full)):
                        bad.append(fpath)
                except Exception as e:  # noqa: BLE001
                    bad.append(f"{fpath} ({type(e).__name__})")
    return not bad, f"{n} downloaded files named in the sources files; {len(bad)} missing or unreadable" + (
        ": " + "; ".join(bad) if bad else "")


def gate6():
    sys.path.insert(0, HERE)
    import build_prices as bp
    cpi, _ = bp.cpi_factors(2024)
    fx = bp.exchange_rates()
    bad, n = [], 0
    for cc in CCS:
        for r in rd(os.path.join(JOB, cc, f"unit_values_{cc}.csv")):
            n += 1
            y = int(r["year"])
            if int(r["currency_year"]) != y:
                bad.append(f"{cc} {r['line']} {y} currency year")
            rate = 1.0 if r["currency"] == "USD" else fx[(cc, y)]
            if not close(float(r["exchange_rate"]), rate):
                bad.append(f"{cc} {r['line']} {y} rate")
            if abs(float(r["cpi_factor"]) - round(cpi[y], 6)) > 1e-9:
                bad.append(f"{cc} {r['line']} {y} cpi")
            if abs(float(r["value_usd2024"]) - float(r["customs_value"]) / rate * cpi[y]) > 0.011:  # stored to the cent
                bad.append(f"{cc} {r['line']} {y} value")
    return not bad, f"{n} line-year rows: year, exchange rate (WDI PA.NUS.FCRF, 1 for US$ values) and CPI factor (BLS CPI-U) equal the downloaded tables; {len(bad)} differ" + (
        ": " + "; ".join(bad[:5]) if bad else "")


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True).stdout


def gate7():
    files = [f for f in git("diff", "--name-only", "origin/main", "HEAD").splitlines() if f]
    out = [f for f in files if not f.startswith(JOBREL + "/")]
    return not out, f"{len(files)} files differ from origin/main; {len(out)} outside the job folder" + (
        ": " + "; ".join(out[:5]) if out else "")


PAT = [(re.compile(r"[A-Za-z]:[\\/][A-Za-z_]"), "machine path"), (re.compile(r"/c/Users|\\Users\\|/Users/"), "machine path"),
       (re.compile("—"), "em dash"), (re.compile(r"Co-Authored-By", re.I), "co-author line"),
       (re.compile(r"Generated with", re.I), "generated-with line")]


def gate8():
    bad = []
    files = [f for f in git("ls-files", JOBREL).splitlines() if f]
    for f in files:
        with open(os.path.join(REPO, f), encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                for rx, what in PAT:
                    if rx.search(line):
                        bad.append(f"{f}:{i} {what}")
    msgs = git("log", "--format=%B", "origin/main..HEAD")
    for rx, what in PAT:
        if rx.search(msgs):
            bad.append(f"commit messages: {what}")
    return not bad, f"{len(files)} tracked job files and the branch's commit messages scanned; {len(bad)} hits" + (
        ": " + "; ".join(bad[:8]) if bad else "")


def main():
    expected = int(sys.argv[1]) if len(sys.argv) > 1 else 2892
    gates = [("1 Coverage", lambda: gate1(expected)), ("2 Current values", gate2), ("3 Source type", gate3),
             ("4 Recompute", gate4), ("5 Files", gate5), ("6 Currency", gate6), ("7 Read-only", gate7),
             ("8 Hygiene", gate8)]
    lines = ["# Gates LAC_VEHICLE_PRICES", "", "| Gate | Result | Detail |", "| --- | --- | --- |"]
    for name, fn in gates:
        ok, det = fn()
        print(name, "PASS" if ok else "FAIL", det)
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {det} |")
    lines.append("")
    lines.append("Gate 8 on the pull request body is checked when the pull request is opened (see the REPORT).")
    with open(os.path.join(JOB, "gates_result.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
