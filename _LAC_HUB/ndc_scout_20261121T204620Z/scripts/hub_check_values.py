"""Hub check of values reported by country tasks (LAC_NDC_SCOUT).

Usage: python -I hub_check_values.py <job_folder> <code> [<code> ...]
For every row of targets_<code>.csv and projections_<code>.csv:
- the source id must exist in parts/sources_<code>.csv (or sources.csv),
- the page must be given,
- the source file must exist and its SHA-256 must match,
- the value is searched on the cited page(s) in the cached page text
  downloads/<code>/text/<source_id>/p<N>.txt, and if not found there in the
  text extracted afresh from the PDF page with pypdf.
Writes parts/hub_value_check_<code>.csv with one row per checked row and a status:
found, not_found (needs a manual look), no_value (non-numeric target), error.
"""
import csv
import hashlib
import os
import re
import sys

JOB = sys.argv[1]
CODES = sys.argv[2:]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pages_of(s):
    out = []
    for part in re.split(r"[;,]", str(s)):
        part = part.strip()
        m = re.match(r"^p\.?\s*(\d+)\s*(?:-\s*(\d+))?$", part)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            out.extend(range(a, b + 1))
    return out


def variants(v):
    """String forms a number may take in Spanish or English documents."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return []
    forms = set()
    for dec in range(0, 5):
        r = round(x, dec)
        if abs(r - x) > 1e-9 * max(1.0, abs(x)):
            continue
        s = f"{r:.{dec}f}"
        intpart, _, frac = s.partition(".")
        neg = intpart.startswith("-")
        ip = intpart.lstrip("-")
        groups = []
        while len(ip) > 3:
            groups.insert(0, ip[-3:])
            ip = ip[:-3]
        groups.insert(0, ip)
        for tsep in ["", ",", ".", " ", " ", "'"]:
            for dsep in [".", ","]:
                if tsep == dsep:
                    continue
                body = tsep.join(groups)
                f = ("-" if neg else "") + body + (dsep + frac if frac else "")
                forms.add(f)
    return sorted(forms, key=len, reverse=True)


def find_in(text, forms):
    t = text.replace("−", "-")
    for f in forms:
        pat = r"(?<![\d.,])" + re.escape(f) + r"(?![\d]|[.,]\d)"
        if re.search(pat, t):
            return f
    return None


def load_sources(code):
    rows = {}
    for p in [os.path.join(JOB, "parts", f"sources_{code}.csv"), os.path.join(JOB, "sources.csv")]:
        if os.path.exists(p):
            with open(p, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    rows.setdefault(r["id"], r)
    return rows


def pdf_page_text(path, n, cache={}):
    try:
        import pypdf
        if path not in cache:
            cache[path] = pypdf.PdfReader(path)
        return cache[path].pages[n - 1].extract_text() or ""
    except Exception:
        return ""


def main():
    for code in CODES:
        src = load_sources(code)
        sha_ok = {}
        out = []
        for kind in ["targets", "projections"]:
            fn = os.path.join(JOB, f"{kind}_{code}.csv")
            if not os.path.exists(fn):
                continue
            with open(fn, encoding="utf-8", newline="") as f:
                for i, r in enumerate(csv.DictReader(f), start=2):
                    sid = r.get("source_id", "").strip()
                    page = r.get("page", "").strip()
                    rid = r.get("target_id") or f"line{i}"
                    status, how = "", ""
                    if sid not in src:
                        status, how = "error", "source id not in sources"
                    elif not page:
                        status, how = "error", "no page"
                    else:
                        fpath = os.path.join(JOB, src[sid]["file"])
                        if sid not in sha_ok:
                            sha_ok[sid] = os.path.exists(fpath) and sha256(fpath) == src[sid]["SHA-256"].strip().lower()
                        if not sha_ok[sid]:
                            status, how = "error", "file missing or SHA-256 mismatch"
                        else:
                            forms = variants(r.get("value", ""))
                            if not forms:
                                status, how = "no_value", "value not numeric"
                            else:
                                pgs = pages_of(page)
                                hit = None
                                for n in pgs:
                                    tp = os.path.join(JOB, "downloads", code, "text", sid, f"p{n}.txt")
                                    if os.path.exists(tp):
                                        with open(tp, encoding="utf-8", errors="replace") as tf:
                                            hit = find_in(tf.read(), forms)
                                    if not hit and fpath.lower().endswith(".pdf"):
                                        hit = find_in(pdf_page_text(fpath, n), forms)
                                    if hit:
                                        how = f"'{hit}' on p.{n}"
                                        break
                                status = "found" if hit else "not_found"
                                if not pgs:
                                    status, how = "not_found", "page not in p.N form: " + page
                    out.append({"country": code, "file": f"{kind}_{code}.csv", "row_id": rid, "source_id": sid,
                                "page": page, "value": r.get("value", ""), "unit": r.get("unit", ""),
                                "year": r.get("target_year", r.get("year", "")), "status": status, "how": how})
        op = os.path.join(JOB, "parts", f"hub_value_check_{code}.csv")
        with open(op, "w", encoding="utf-8", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ["country"], lineterminator="\n")
            w.writeheader()
            w.writerows(out)
        counts = {}
        for r in out:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(code, counts)


if __name__ == "__main__":
    main()
