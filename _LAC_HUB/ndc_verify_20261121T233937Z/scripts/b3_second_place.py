"""Step B, check 3: find each value in a second place.

For every row of values_to_verify.csv:
1. text search: the value's printed forms on every page of every registered document of the
   same country (downloads/<code>/text_all), except the pages cited by check 1 in the cited
   document. A hit is 'strong' when the number has at least four significant digits, or when
   the matched line also holds the target year or a keyword of the value's kind; otherwise 'weak'.
2. identities: a percent reduction against BAU checked against a BAU level and a target level
   (or a reduction amount) of the same document and year; a reduction amount checked against
   BAU minus target level.
Writes parts/check3_<code>.csv (all hits, one row per value with the best hit and up to five others).
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, SCOUT, CODES, read_csv, write_csv, variants, find_all, pages_of

src = read_csv(os.path.join(SCOUT, "sources.csv"))
extra = os.path.join(JOB, "sources.csv")
if os.path.exists(extra):
    ids = {r["id"] for r in src}
    src += [r for r in read_csv(extra) if r["id"] not in ids and r.get("class", "official") != "lead"]

KW = {
    "emission": r"emisi|gei|ghg|co2|gg|kt|mt|bau|tendencial|reducci|reduction|neutral|absorci|remoci",
    "share": r"renovab|renewab|%|por ?ciento|percent|participaci|share|cuota|matriz|generaci",
    "capacity": r"mw|gw|capacidad|capacity|potencia",
    "vehicle": r"veh[ií]c|flota|fleet|bus|el[eé]ctric|taxi|moto",
    "blend": r"etanol|ethanol|biodi|mezcla|blend|e10|b5|biocomb",
    "loss": r"p[eé]rdida|loss|t&d",
    "efficiency": r"eficien|efficien|ahorro|saving|intensi",
}


def sig_digits(v):
    s = str(v).replace(",", "").replace("-", "").lstrip("0").replace(".", "")
    return len(s.rstrip("0")) if "." not in str(v) else len(s)


def load_pages(code):
    pages = {}
    base = os.path.join(JOB, "downloads", code, "text_all")
    for r in src:
        if not r["id"].startswith(code + "-"):
            continue
        d = os.path.join(base, r["id"])
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            m = re.match(r"p(\d+)\.txt$", fn)
            if m:
                with open(os.path.join(d, fn), encoding="utf-8", errors="replace") as f:
                    pages[(r["id"], int(m.group(1)))] = f.read()
    return pages


def kind_kw(v):
    t = (v["indicator"] + " " + v["description"] + " " + v["unit"]).lower()
    kws = []
    for k, pat in KW.items():
        if re.search(pat, t):
            kws.append(KW[k])
    return "|".join(kws) if kws else KW["emission"]


def fnum(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def identities(vals):
    """Return {value_id: description} for values that satisfy a printed identity."""
    out = {}
    by_doc_year = {}
    for v in vals:
        by_doc_year.setdefault((v["source_id"], v["year"]), []).append(v)
    for (sid, yr), group in by_doc_year.items():
        lv = [g for g in group if re.search(r"kt|gg|mt", g["unit"].lower()) and fnum(g["value"]) is not None]
        pc = [g for g in group if "percent" in g["unit"].lower() and re.search(r"bau|tendencial|against", (g["indicator"] + g["description"]).lower())]
        bau = [g for g in lv if re.search(r"bau|tendencial|base case|baseline|sin cnd|without|no measures|business", (g["scenario_as_named"] + g["description"]).lower()) and not re.search(r"reduction|reducci", g["indicator"].lower())]
        mit = [g for g in lv if g not in bau and not re.search(r"reduction|reducci|cumulative|acumulad", (g["indicator"] + g["description"]).lower())]
        red = [g for g in lv if re.search(r"reduction against bau|emission reduction", g["indicator"].lower()) and not re.search(r"cumulative|per year|annual", g["indicator"].lower())]
        for b in bau:
            B = fnum(b["value"])
            if not B:
                continue
            for p in pc:
                P = fnum(p["value"])
                for m in mit:
                    M = fnum(m["value"])
                    if M is None or b["unit"].split()[0].lower() != m["unit"].split()[0].lower():
                        continue
                    calc = 100 * (1 - M / B)
                    if abs(calc - P) <= 0.051 + 0.005 * abs(P):
                        d = f"identity: 1 - {m['value_id']} ({M}) / {b['value_id']} ({B}) = {calc:.2f} percent"
                        out.setdefault(p["value_id"], d)
                        out.setdefault(m["value_id"], d.replace("identity:", "identity (level):"))
                        out.setdefault(b["value_id"], d.replace("identity:", "identity (BAU):"))
                for r in red:
                    R = fnum(r["value"])
                    if R is None:
                        continue
                    calc = 100 * R / B
                    if abs(calc - P) <= 0.051 + 0.005 * abs(P):
                        d = f"identity: {r['value_id']} ({R}) / {b['value_id']} ({B}) = {calc:.2f} percent"
                        out.setdefault(p["value_id"], d)
                        out.setdefault(r["value_id"], d.replace("identity:", "identity (reduction):"))
            for m in mit:
                M = fnum(m["value"])
                for r in red:
                    R = fnum(r["value"])
                    if M is None or R is None:
                        continue
                    if abs((B - M) - R) <= 0.06 + 0.0005 * abs(R):
                        d = f"identity: {b['value_id']} ({B}) - {m['value_id']} ({M}) = {B - M:.1f}"
                        out.setdefault(r["value_id"], d)
                        out.setdefault(m["value_id"], d.replace("identity:", "identity (level):"))
    # sums: sector rows of a projected series against the printed total of the same scenario and year,
    # and a sector against two of its parts (for example LULUCF net = emissions + removals)
    grp = {}
    for v in vals:
        if v["origin"].startswith("projections") and fnum(v["value"]) is not None:
            grp.setdefault((v["source_id"], v["scenario_as_named"], v["year"]), []).append(v)
    for k, g in grp.items():
        tot = [x for x in g if "economy-wide" in x["sector"].lower()]
        main = [x for x in g if "economy-wide" not in x["sector"].lower() and "(" not in x["sector"]
                and not re.search(r"emissions$|removals$|emisiones$|absorc", x["sector"].lower())]
        for t in tot:
            T = fnum(t["value"])
            S = sum(fnum(x["value"]) for x in main)
            if len(main) >= 3 and abs(S - T) <= 0.15 + 0.0005 * abs(T):
                d = f"identity: sum of {len(main)} sector rows of the same scenario and year = {S:.1f} against total {T}"
                out.setdefault(t["value_id"], d)
                for x in main:
                    out.setdefault(x["value_id"], d.replace("identity:", "identity (part of sum):"))
        for r in g:
            R = fnum(r["value"])
            w = set(re.findall(r"[a-z]+", r["sector"].lower().split("(")[0]))
            others = [x for x in g if x is not r]
            for i, a in enumerate(others):
                for b in others[i + 1:]:
                    wa = set(re.findall(r"[a-z]+", a["sector"].lower()))
                    wb = set(re.findall(r"[a-z]+", b["sector"].lower()))
                    if not (w & wa and w & wb):
                        continue
                    A, B = fnum(a["value"]), fnum(b["value"])
                    for s, lab in [(A + B, "+"), (A - B, "-"), (B - A, "-r")]:
                        if abs(s - R) <= 0.06 + 0.0005 * abs(R) and abs(R) > 0:
                            d = f"identity: {a['sector']} {lab} {b['sector']} = {s:.1f} against {r['sector']} {R}"
                            out.setdefault(r["value_id"], d)
                            out.setdefault(a["value_id"], d.replace("identity:", "identity (part):"))
                            out.setdefault(b["value_id"], d.replace("identity:", "identity (part):"))
    return out


TOK = re.compile(r"(?<![\d.,])-?\d{1,3}(?:[ ,. ']\d{3})+(?:[.,]\d+)?(?![\d])|(?<![\d.,])-?\d+(?:[.,]\d+)?(?![\d])")


def token_values(tok):
    """All numbers a printed token can mean (dot or comma decimal, any thousands separator)."""
    t = tok.replace(" ", " ")
    out = set()
    for dec in [".", ","]:
        s = t
        if dec == ".":
            s2 = re.sub(r"[ ,']", "", s)
        else:
            s2 = re.sub(r"[ .']", "", s).replace(",", ".")
        try:
            out.add(round(float(s2), 6))
        except ValueError:
            pass
    return out


def build_index(pages):
    idx = {}
    for (sid, n), txt in pages.items():
        for line in txt.replace("−", "-").splitlines():
            for m in TOK.finditer(line):
                for x in token_values(m.group(0)):
                    idx.setdefault(x, []).append((sid, n, line))
    return idx


def main():
    vals = read_csv(os.path.join(JOB, "values_to_verify.csv"))
    for code in CODES:
        pages = load_pages(code)
        idx = build_index(pages)
        cv = [v for v in vals if v["country"] == code]
        ids_ = identities(cv)
        rows = []
        for v in cv:
            x = fnum(v["value"])
            hits = []
            if x is not None:
                own = set(pages_of(v["page"])[:1])
                kw = kind_kw(v)
                strong_num = sig_digits(v["value"]) >= 4 and not (x.is_integer() and 1990 <= x <= 2100)
                seen = set()
                for sid, n, line in idx.get(round(x, 6), []):
                    if (sid == v["source_id"] and n in own) or (sid, n) in seen:
                        continue
                    seen.add((sid, n))
                    yr = v["year"][:4] if v["year"] else ""
                    ctx_ok = bool(re.search(kw, line.lower())) or bool(yr and yr in line)
                    strength = "strong" if strong_num or (ctx_ok and yr and yr in line) else ("medium" if ctx_ok else "weak")
                    hits.append((strength, sid, n, ""))
            order = {"strong": 0, "medium": 1, "weak": 2}
            hits.sort(key=lambda h: (order[h[0]], h[1] != v["source_id"], h[2]))
            best = hits[0] if hits else None
            rows.append({"value_id": v["value_id"], "source_id": v["source_id"], "page": v["page"], "value": v["value"],
                         "identity": ids_.get(v["value_id"], ""),
                         "best_strength": best[0] if best else "",
                         "best_place": f"{best[1]} p.{best[2]}" if best else "",
                         "n_hits": len(hits), "n_strong": sum(h[0] == "strong" for h in hits),
                         "other_places": "; ".join(f"{h[1]} p.{h[2]} ({h[0]})" for h in hits[1:6])})
        write_csv(os.path.join(JOB, "parts", f"check3_{code}.csv"), rows)
        n = len(rows)
        print(code, n, "identity", sum(bool(r["identity"]) for r in rows),
              "strong", sum(r["best_strength"] == "strong" for r in rows),
              "medium", sum(r["best_strength"] == "medium" for r in rows),
              "weak", sum(r["best_strength"] == "weak" for r in rows),
              "none", sum(not r["best_strength"] and not r["identity"] for r in rows))


if __name__ == "__main__":
    main()
