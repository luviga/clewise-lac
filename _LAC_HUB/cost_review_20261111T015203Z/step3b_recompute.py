"""Step 3, second part: recompute derivations from their stated inputs.

(a) Arithmetic chains written in the derivation text ("a x b / c = d"): the expression left of each '=' is
    evaluated when, after removing words, units, years and descriptive brackets, it is a plain arithmetic
    expression with at least one operator; the result is compared with the number right of '='.
(b) Fuel projections: for projected years P(y, s) / WEO_s(y) must be constant for a row and scenario
    (rule F4, P = r x B(2024) x WEO_s(y) / WEO_s(2024)), with WEO 2025 Table 2.3 linear between 2024, 2035
    and 2050 and flat after 2050.
Differences above 0.5 percent are written to derivation_recompute.csv.
"""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa

URL = re.compile(r"https?://\S+")
BRACKET_WORDS = re.compile(r"\([^()]*[A-Za-z][^()]*\)")
CPI_LABEL = re.compile(r"(?i)\b(?:US_)?CPI(?:[-_ ]?U)?(?:_?(?:19|20)\d\d)?(?:\s*(?:19|20)\d\d(?:\s*/\s*(?:19|20)\d\d)?)?")
UNITS = re.compile(r"(?i)[A-Za-z$%][A-Za-z0-9$%\-]*(?:/[A-Za-z0-9\-]+)+")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-.]*")
NUMTOK = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def tokens(s):
    s = URL.sub(" ", s)
    s = CPI_LABEL.sub(" ", s)
    s = re.sub(r"[A-Za-z_]*\(\s*(?:19|20)\d\d\s*\)", " ", s)  # B(2024), WEO_s(2024): labels
    s = s.replace("&", "")
    s = re.sub(r",(?!\d{3})", " ", s)  # text commas; thousands separators stay
    for _ in range(3):
        s = BRACKET_WORDS.sub(" ", s)
    s = UNITS.sub(" ", s)
    s = re.sub(r"(?<=\s)x(?=\s)|×", "*", " " + s + " ")
    s = re.sub(r"(?<![\w.])\d+(?:\.\d+)?(?=[A-Za-z])", " ", s)  # numbers glued to words (4Hr, 20MW)
    s = WORD.sub(" ", s)  # words are transparent; two numbers side by side still break the expression
    s = s.replace(";", " ").replace(":", " ")
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        m = NUMTOK.match(s, i)
        if m:
            out.append(("n", m.group(0).replace(",", "")))
            i = m.end()
            continue
        if c in "*/+-()":
            out.append(("o", c))
        else:
            out.append(("b", c))
        i += 1
    # a year label next to another number (no operator between) is a label, not an operand
    keep = []
    for j, t in enumerate(out):
        if t[0] == "n" and re.fullmatch(r"(19[5-9]\d|20[0-6]\d)", t[1]):
            nb = (j > 0 and out[j - 1][0] == "n") or (j + 1 < len(out) and out[j + 1][0] == "n")
            if nb:
                continue
        keep.append(t)
    return keep


def last_expression(toks, target=None):
    """Valid suffix expressions (number (op number)+, balanced brackets); the one matching target if any, else the longest."""
    best = None
    for start in range(len(toks) - 1, -1, -1):
        seg = toks[start:]
        if any(t[0] == "b" for t in seg):
            break
        expr = "".join(t[1] if t[0] == "o" else f" {t[1]} " for t in seg)
        if not any(t[0] == "o" and t[1] in "*/+-" for t in seg) or seg[0][0] == "o" and seg[0][1] != "(":
            continue
        if expr.count("(") != expr.count(")"):
            continue
        try:
            # no two numbers side by side
            if re.search(r"\d\s+\d", expr):
                continue
            v = eval(expr, {"__builtins__": {}}, {})
            best = (expr.strip(), v)
            if target and abs(v - target) <= 0.005 * abs(target):
                return best
        except Exception:  # noqa
            continue
    return best


def check_text(der):
    res = []
    d = URL.sub(" ", der)
    for clause in [d]:
        parts = clause.split("=")
        for i in range(1, len(parts)):
            lhs, rhs = parts[i - 1], parts[i]
            m = NUMTOK.search(rhs)
            if not m or rhs[:m.start()].strip():
                continue
            rv = float(m.group(0).replace(",", ""))
            e = last_expression(tokens(lhs), rv)
            if not e or rv == 0:
                continue
            expr, v = e
            diff = (v - rv) / abs(rv)
            res.append((expr, v, rv, diff))
    return res


rows = []
summary = []
for cc in CCS:
    n_der = n_expr = n_bad = n_scale = 0
    seen = set()
    srcs = [("proposals.csv", "derivation", ["Tech", "Parameter", "fuel_scenario", "year"]),
            ("price_points_2024.csv", "derivation", ["row", "price_point"]),
            ("fuel_prices.csv", "derivation", ["row", "scenario", "year"]),
            ("fuel_prices.csv", "r_detail", ["row", "scenario", "year"]),
            ("fuel_prices.csv", "r_method", ["row", "scenario", "year"]),
            ("plant_costs.csv", "derivation", ["technology", "parameter", "year"])]
    for fn, col, keys in srcs:
        D = read(cc, fn)
        if D is None or col not in D.columns:
            continue
        for _, r in D.iterrows():
            der = r[col]
            if not der or der in seen:
                continue
            seen.add(der)
            n_der += 1
            for expr, v, rv, diff in check_text(der):
                n_expr += 1
                scale = any(abs(v / rv - f) <= 0.005 * f for f in (1e3, 1e6, 1e-3, 1e-6)) if v else False
                if scale:
                    n_scale += 1
                elif abs(diff) > 0.005:
                    n_bad += 1
                    rows.append({"country": COUNTRY[cc], "cc": cc, "check": "arithmetic in derivation", "file": fn,
                                 "row": " ".join(r[k] for k in keys if k in r), "expression": expr,
                                 "recomputed": round(v, 6), "stated": rv, "diff_pct": round(diff * 100, 3),
                                 "derivation": der[:400]})
    summary.append({"cc": cc, "distinct_derivations": n_der, "expressions_recomputed": n_expr,
                    "equal_after_unit_scale_1000": n_scale, "over_0_5pct": n_bad})

# (b) projection path against WEO 2025
WEO = {"crude": {"2024": 79, "STEPS": (80, 76), "CPS": (89, 106), "NZE": (33, 25)},
       "gas": {"2024": 2.2, "STEPS": (3.9, 4.6), "CPS": (4.5, 5.0), "NZE": (2.1, 2.2)},
       "coal_eu": {"2024": 112, "STEPS": (78, 66), "CPS": (92, 82), "NZE": (47, 39)},
       "coal_japan": {"2024": 151, "STEPS": (100, 84), "CPS": (112, 105), "NZE": (57, 49)}}


def weo(series, s, y):
    w = WEO[series]
    a, b, c = w["2024"], w[s][0], w[s][1]
    if y <= 2024:
        return a
    if y <= 2035:
        return a + (b - a) * (y - 2024) / 11
    if y <= 2050:
        return b + (c - b) * (y - 2035) / 15
    return c


def series_of(t):
    t = t.lower()
    if "crude" in t or "oil" in t:
        return "crude"
    if "gas" in t:
        return "gas"
    if "coal" in t and "japan" in t:
        return "coal_japan"
    if "coal" in t:
        return "coal_eu"
    return None


proj_sum = []
for cc in CCS:
    F = read(cc, "fuel_prices.csv")
    vcol = [c for c in F.columns if c.startswith("value_usd_per_gj")][0]
    n_series = n_bad = n_skip = 0
    for (row, sc), g in F.groupby(["row", "scenario"]):
        ser = series_of(g["weo_series"].iloc[0])
        pr = g[g["case"].str.startswith("projected")]
        if not ser or not len(pr) or sc not in ("STEPS", "CPS", "NZE"):
            n_skip += 1
            continue
        n_series += 1
        ks = [(int(r["year"]), num(r[vcol]) / weo(ser, sc, int(r["year"]))) for _, r in pr.iterrows() if num(r[vcol])]
        k0 = sorted(k for _, k in ks)[len(ks) // 2]
        worst = max(ks, key=lambda t: abs(t[1] / k0 - 1))
        if abs(worst[1] / k0 - 1) > 0.005:
            n_bad += 1
            rows.append({"country": COUNTRY[cc], "cc": cc, "check": "projection follows WEO path", "file": "fuel_prices.csv",
                         "row": f"{row} {sc}", "expression": f"P(y)/WEO_{sc}({ser}, y) constant over {len(ks)} projected years",
                         "recomputed": round(k0, 6), "stated": round(worst[1], 6),
                         "diff_pct": round((worst[1] / k0 - 1) * 100, 3),
                         "derivation": f"largest deviation in {worst[0]}; weo_series {g['weo_series'].iloc[0][:80]}"})
    proj_sum.append({"cc": cc, "projected_series_checked": n_series, "series_off_path": n_bad, "series_not_checked": n_skip})

R = pd.DataFrame(rows, columns=["country", "cc", "check", "file", "row", "expression", "recomputed", "stated", "diff_pct", "derivation"])
write(R, "derivation_recompute.csv")
S = pd.DataFrame(summary).merge(pd.DataFrame(proj_sum), on="cc")
write(S, "derivation_recompute_summary.csv")
print(S.to_string())
print(R.groupby(["cc", "check"]).size().to_string())
