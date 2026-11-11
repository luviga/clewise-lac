"""Step 3: proposed values against their downloaded sources, and recomputation of derivations."""
import re
import sys
from functools import lru_cache

sys.path.insert(0, ".")
from common import *  # noqa
import textindex as ti

SEED = 20261110
LP = pd.read_csv(glob.glob(os.path.join(REPO, "_LAC_HUB", "local_prices_*", "local_prices_2024.csv"))[0],
                 dtype=str, keep_default_na=False)
LPC = {"cr": "CostaRica", "dr": "DominicanRepublic", "ecu": "Ecuador", "gua": "Guatemala",
       "hon": "Honduras", "jam": "Jamaica"}

NUM = re.compile(r"(?<![A-Za-z0-9_.])-?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\d])|(?<![A-Za-z0-9_.,])-?\d+(?:\.\d+)?(?![\d])")
IDENT = re.compile(
    r"(?i)\b(?:Table|Tabla|Tables|Cuadro|Figure|Figura|Annex|Anexo|Appendix|Ap[eé]ndice|pages?|PDF|printed|p\.|pp\.|row|rows|"
    r"cell|cells|column|col\.|Class|Case|crpyears|edition|v|version|line|lines|section|step|cmdCode|HS|record|Q|Ley|"
    r"No\.|number|chapter|Chapter|sheet)\s*[A-Z]?[\d][\w.\-]*")
UNITQ = re.compile(r"(?i)\b\d+(?:\.\d+)?\s*(?:MW|GW|kW\b|Hr\b|hr\b|-hour|hours?|kV|years?|yr\b|percent|%|months?|weeks?|files|days|bbl/d|t\b|tonnes|kg\b|"
                   r"MWh\b|kcal/kg|Btu|plants?|units?)")
YEAR = re.compile(r"^(19[5-9]\d|20[0-6]\d)$")


@lru_cache(maxsize=None)
def constants_values(cc):
    c = read(cc, "constants.csv")
    k = c.columns[0]
    # only deflators and conversion factors are left out; source values stored as constants stay searchable
    c = c[c[k].str.contains(r"CPI|_PER_|NCV|GAL|BBL|MMBTU|MCF|FX|KCAL|KJ|MWH|GJ_|NET_PER|FACTOR|PJ_PER|L_PER|MONTHS", case=False, regex=True)]
    vals = set()
    for v in c["value"]:
        x = num(v)
        if x is not None:
            vals.add(round(x, 6))
    return vals


def candidates(deriv, cc, exclude=()):
    """Input numbers of a derivation, in order, without identifiers, years, constants or the result."""
    d = re.sub(r"https?://\S+", " ", deriv)
    d = IDENT.sub(" ", d)
    # our own values quoted beside the source (current value, model value) are not published numbers
    d = re.sub(r"(?i)\b(?:current(?: value)?|model(?: value)?(?: \d{4})?|vs model(?: \d{4})?(?: to \d{4})?|proposed(?: \w+)?(?: \d{4})?)\s*(?:is|=|of)?\s*-?[\d,]+(?:\.\d+)?", " ", d)
    d = UNITQ.sub(lambda m: " " if not re.search(r"(?i)MWh|kcal", m.group(0)) else m.group(0), d)
    out = []
    consts = constants_values(cc)
    for m in NUM.finditer(d):
        s = m.group(0)
        if YEAR.match(s):
            continue
        x = num(s)
        if x is None or x in (0, 1):
            continue
        if round(x, 6) in consts and len(s.replace(",", "").replace(".", "").lstrip("-0")) >= 4:
            continue  # a stated constant (CPI, conversion factor) is checked in Step 4, not here
        if any(abs(x - e) < 1e-9 for e in exclude):
            continue
        if s not in out:
            out.append(s)
    return out


@lru_cache(maxsize=None)
def source_files(cc):
    S = read(cc, "sources.csv")
    idc = S.columns[0]
    m = {}
    for _, r in S.iterrows():
        fs = [p.strip().replace("downloads/", "", 1) for p in r["downloaded_file"].split(";") if p.strip()]
        m[r[idc]] = [os.path.join(downloads(cc), f) for f in fs]
    return m


def locator_of(cc, ids):
    S = read(cc, "sources.csv")
    idc = S.columns[0]
    loccol = "page_or_table" if "page_or_table" in S.columns else "locator"
    return " | ".join(S.loc[S[idc] == i, loccol].iloc[0][:80] for i in ids if (S[idc] == i).any())


_text = {}


def get_text(cc, path):
    k = (cc, path)
    if k not in _text:
        _text[k] = ti.extract(cc, path)
    return _text[k]


_hits = {}


def find(cc, files, target):
    """Search target in files. Returns (found_file, locations, not_searchable_list)."""
    ns = []
    for f in files:
        if not os.path.exists(f):
            ns.append(f"{os.path.basename(f)}: file absent")
            continue
        key = (f, target)
        if key not in _hits:
            text, status = get_text(cc, f)
            if status != "ok":
                _hits[key] = (None, status)
            else:
                _hits[key] = (ti.search(text, target), "ok")
        locs, status = _hits[key]
        if status != "ok":
            ns.append(f"{os.path.basename(f)}: {status}")
            continue
        if locs:
            return f, locs, ns
    return None, [], ns


def rel(cc, f):
    return os.path.relpath(f, downloads(cc)).replace("\\", "/") if f else ""


ROWS = []


def check(cc, tech, prm, year, proposed, searched, others, ids, kind, extra_note="", fallback=False):
    files = []
    for i in ids:
        files += source_files(cc).get(i, [])
    files = list(dict.fromkeys(files))
    pv = num(proposed)
    if not searched and pv not in (None, 0.0, 1.0):
        # the derivation names the source but states no number: the proposed value is the published one
        searched = str(proposed)
        extra_note = ("the derivation states no number; the proposed value itself was searched. " + extra_note).strip()
    if not searched:
        ROWS.append({"country": COUNTRY[cc], "cc": cc, "check_set": kind, "technology": tech, "parameter": prm,
                     "year": year, "proposed_value": proposed, "number_searched": "", "file": "",
                     "found": "not run", "location": "",
                     "note": ("no number to search: the derivation states none and the proposed value is 0, 1 or empty; " + extra_note).strip("; ")})
        return
    f, locs, ns = find(cc, files, searched)
    if not f and fallback:
        # the published figures may be the derivation's inputs (for example customs value and weight)
        for o in others:
            if len(o.replace(",", "").replace(".", "").replace("-", "").lstrip("0")) < 3:
                continue
            g, l2, _ = find(cc, files, o)
            if g:
                extra_note = (f"{searched} itself is not printed; derivation input {o} is. " + extra_note).strip()
                searched, f, locs = o, g, l2
                others = [x for x in others if x != o]
                break
    other_found = []
    for o in others[:6]:
        g, l2, _ = find(cc, files, o)
        other_found.append(f"{o}:{'yes' if g else 'no'}")
    searchable = [x for x in files if os.path.exists(x) and get_text(cc, x)[1] == "ok"]
    if f:
        found = "yes"
    elif not searchable:
        found = "not run"
    else:
        found = "no"
    note = []
    if found == "not run":
        note.append("no searchable file among the row's sources: " + "; ".join(ns[:4]))
    elif ns:
        note.append("not searchable: " + "; ".join(ns[:3]))
    if other_found:
        note.append("other inputs found: " + ", ".join(other_found))
    sig = len(searched.replace(",", "").replace(".", "").replace("-", "").lstrip("0"))
    if found == "yes" and sig <= 2:
        note.append("short number (2 significant digits or fewer); a match may be coincidental, check the location")
    if extra_note:
        note.append(extra_note)
    ROWS.append({"country": COUNTRY[cc], "cc": cc, "check_set": kind, "technology": tech, "parameter": prm,
                 "year": year, "proposed_value": proposed, "number_searched": searched,
                 "file": rel(cc, f) if f else ";".join(rel(cc, x) for x in files[:3]) + (" ..." if len(files) > 3 else ""),
                 "found": found, "location": "; ".join(locs), "note": " | ".join(note)})


def ids_of(s):
    return [i.strip() for i in re.split(r"[;,]", s) if i.strip()]


for cc in CCS:
    _text.clear()
    _hits.clear()
    ti._IDX.clear()
    print("==", cc, flush=True)
    P = read(cc, "proposals.csv")
    PP = read(cc, "price_points_2024.csv")
    F = read(cc, "fuel_prices.csv")
    ch = PP[PP["chosen"].str.lower() == "yes"]
    sidcol = "source_ids" if "source_ids" in PP.columns else "source_id"
    # --- fuel rows, 2024 chosen value
    for _, r in ch.iterrows():
        val = r.get("value_usd_per_gj_net") or r.get("value_usd_per_gj")
        note = f"chosen point {r['price_point']}"
        searched, others = "", []
        if r.get("price_as_published", ""):
            searched = r["price_as_published"]
            lp = LP[(LP["country"] == LPC[cc]) & (LP["model_code"] == r["row"]) & (LP["price_point"] == r["price_point"])]
            if len(lp):
                others = candidates(lp.iloc[0]["derivation"], cc, exclude=[])
            note += f"; published unit {r.get('unit_as_published', '')}"
        elif r.get("derivation", ""):
            c = candidates(r["derivation"], cc, exclude=[])
            searched, others = (c[0], c[1:]) if c else ("", [])
            note += f"; derivation: {r['derivation'][:160]}"
        else:
            lp = LP[(LP["country"] == LPC[cc]) & (LP["model_code"] == r["row"]) & (LP["price_point"] == r["price_point"])]
            if len(lp) > 1:
                lp2 = lp[[abs((num(x) or 0) - (num(val) or 0)) < 0.01 for x in lp["value_usd_per_gj"]]]
                lp = lp2 if len(lp2) else lp
            if len(lp):
                searched = lp.iloc[0]["price_as_published"]
                others = candidates(lp.iloc[0]["derivation"], cc, exclude=[])
                note += (f"; published value and unit from LAC_LOCAL_PRICES local_prices_2024.csv "
                         f"({lp.iloc[0]['price_as_published']} {lp.iloc[0]['unit']}, period {lp.iloc[0]['period']})")
                if ";" in lp.iloc[0]["months_covered"] or len(ids_of(r[sidcol])) > 5:
                    note += "; value is a mean over several published files"
        frow = F[(F["row"] == r["row"]) & (F["year"] == "2024")]
        check(cc, r["row"], "VariableCost", "2024", val, searched, others, ids_of(r[sidcol]), "fuel 2024 chosen", note, fallback=True)
    # --- plant and other technology rows not keep
    A = P[P["fuel_scenario"] == "ALL"].copy()
    nk = A[A["change_class"] != "keep"]
    grp = nk.groupby(["Tech", "Parameter", "derivation", "source_ids", "proposed_value"], sort=False)
    for (t, prm, der, sids, pv), g in grp:
        yrs = sorted(g["year"], key=int)
        yl = yrs[0] if len(yrs) == 1 else f"{yrs[0]}-{yrs[-1]} ({len(yrs)} rows)"
        c = candidates(der, cc, exclude=[])
        check(cc, t, prm, yl, pv, c[0] if c else "", c[1:], ids_of(sids), f"not keep ({g['change_class'].iloc[0]})",
              f"basis {g['basis_class'].iloc[0]}", fallback=True)
    # --- 20 keep rows at random
    keep = A[A["change_class"] == "keep"]
    smp = keep.sample(n=min(20, len(keep)), random_state=SEED) if len(keep) else keep
    for _, r in smp.iterrows():
        c = candidates(r["derivation"], cc, exclude=[])
        check(cc, r["Tech"], r["Parameter"], r["year"], r["proposed_value"], c[0] if c else "", c[1:],
              ids_of(r["source_ids"]), "keep sample", f"basis {r['basis_class']}", fallback=True)

V = pd.DataFrame(ROWS)
write(V, "value_checks.csv")
print(V.groupby(["cc", "check_set", "found"]).size().to_string())
