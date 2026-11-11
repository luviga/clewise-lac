"""Step 4: shared inputs compared across the six countries (cross_country.csv)."""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa

F5 = ("ASSUMPTION: natural gas prices published per MMBtu are on a gross calorific basis and are converted to the "
      "models' net basis by dividing by 0.9 (net = 0.9 x gross for natural gas, UN Statistics Division), for all six "
      "countries and all years. Reason: natural gas in the Americas, Henry Hub included, is priced on a gross basis, "
      "and the energy balances behind the models follow the UN recommendation to use net values (IRES, UN 2018). "
      "Check: EIA reports US natural gas at 1,037 Btu per cubic foot, a gross value. Range: a source already on a net "
      "basis would be overstated by about 11 percent.")
# Published Table 2.3, WEO 2025 page 109, read from the PDF in this job (scratch/weo_p109.txt)
WEO_PUB = {("crude", "2024"): 79, ("crude", "CPS2035"): 89, ("crude", "CPS2050"): 106, ("crude", "STEPS2035"): 80,
           ("crude", "STEPS2050"): 76, ("crude", "NZE2035"): 33, ("crude", "NZE2050"): 25,
           ("gas_us", "2024"): 2.2, ("gas_us", "CPS2035"): 4.5, ("gas_us", "CPS2050"): 5.0, ("gas_us", "STEPS2035"): 3.9,
           ("gas_us", "STEPS2050"): 4.6, ("gas_us", "NZE2035"): 2.1, ("gas_us", "NZE2050"): 2.2,
           ("coal_eu", "2024"): 112, ("coal_eu", "CPS2035"): 92, ("coal_eu", "CPS2050"): 82, ("coal_eu", "STEPS2035"): 78,
           ("coal_eu", "STEPS2050"): 66, ("coal_eu", "NZE2035"): 47, ("coal_eu", "NZE2050"): 39,
           ("coal_japan", "2024"): 151, ("coal_japan", "CPS2035"): 112, ("coal_japan", "CPS2050"): 105,
           ("coal_japan", "STEPS2035"): 100, ("coal_japan", "STEPS2050"): 84, ("coal_japan", "NZE2035"): 57,
           ("coal_japan", "NZE2050"): 49}


def series_of(name):
    n = name.upper()
    if "CRUDE" in n:
        return "crude"
    if "GAS" in n:
        return "gas_us"
    if "COAL" in n and "JAPAN" in n:
        return "coal_japan"
    if "COAL" in n:
        return "coal_eu"
    return None


def key_of(name):
    n = name.upper()
    y = re.search(r"(20\d\d)$", n).group(1)
    for s in ("STEPS", "CPS", "NZE"):
        if f"_{s}_" in n:
            return y if y == "2024" else s + y
    return y if y == "2024" else None


rows = []
weo = {cc: {} for cc in CCS}
meta = {cc: set() for cc in CCS}
for cc in CCS:
    c = read(cc, "constants.csv")
    k = c.columns[0]
    loc = "page_or_table" if "page_or_table" in c.columns else "locator"
    for _, r in c[c[k].str.contains("WEO", case=False)].iterrows():
        s, key = series_of(r[k]), key_of(r[k])
        if s and key:
            weo[cc][(s, key)] = num(r["value"])
            meta[cc].add(f"{r[loc][:70]} / {r['unit'][:45]}")

for (s, key), pub in WEO_PUB.items():
    vals = {cc: weo[cc].get((s, key), "") for cc in CCS}
    used = {cc: v for cc, v in vals.items() if v != ""}
    if not used:
        continue
    dis = [cc for cc, v in used.items() if abs(v - pub) > 1e-9]
    rows.append({"item": "WEO 2025 Table 2.3", "key": f"{s} {key}", "published_value": pub,
                 **{COUNTRY[cc]: vals[cc] for cc in CCS},
                 "agree": "yes" if not dis else "no",
                 "note": ("differs from published: " + ",".join(COUNTRY[c] for c in dis)) if dis else
                 f"used by {len(used)} of 6"})
rows.append({"item": "WEO 2025 Table 2.3", "key": "table, page, units, currency year", "published_value":
             "Table 2.3 Wholesale fossil fuel prices by scenario, page 109; USD (MER, 2024)",
             **{COUNTRY[cc]: " || ".join(sorted(meta[cc]))[:300] for cc in CCS},
             "agree": "yes" if all(any("2.3" in m and "109" in m for m in meta[cc]) for cc in CCS) else "no",
             "note": "every country cites Table 2.3 page 109 (the briefs said Table 2.32); WEO publishes 2024, 2035 and 2050 only"})
coal_series = {cc: sorted({s for (s, _) in weo[cc] if s.startswith("coal")}) for cc in CCS}
rows.append({"item": "WEO 2025 Table 2.3", "key": "steam coal series chosen", "published_value": "",
             **{COUNTRY[cc]: ";".join(coal_series[cc]) for cc in CCS},
             "agree": "no" if len({tuple(v) for v in coal_series.values()}) > 1 else "yes",
             "note": "Ecuador uses Japan steam coal (Pacific seaborne, Peru origin per its GAPS item 4); the other five use European Union"})


def series_from_constants(cc, pat):
    c = read(cc, "constants.csv")
    k = c.columns[0]
    out = {}
    for _, r in c.iterrows():
        m = re.fullmatch(pat, r[k], re.I)
        if m:
            out[m.group(1)] = num(r["value"])
    return out


SER = {"US CPI-U annual average": r"(?:US_)?CPI_?U_(20\d\d)",
       "Brent USD/bbl (EIA RBRTE)": r"(?:BENCH_)?BRENT_(20\d\d)",
       "Henry Hub USD/MMBtu (EIA RNGWHHD)": r"(?:HENRY_?HUB|HH)_(20\d\d)",
       "Coal South Africa Richards Bay USD/t (World Bank)": r"COAL_(?:SOUTH_AFRICA_|SAFRICA_|SA_)?(20\d\d)",
       "Coal Australia Newcastle USD/t (World Bank)": r"BENCH_COAL_AU_(20\d\d)"}
for item, pat in SER.items():
    per = {cc: series_from_constants(cc, pat) for cc in CCS}
    years = sorted({y for d in per.values() for y in d})
    for y in years:
        vals = {cc: per[cc].get(y, "") for cc in CCS}
        used = [v for v in vals.values() if v != ""]
        agree = "yes" if len(set(used)) <= 1 else "no"
        rows.append({"item": item, "key": y, "published_value": "", **{COUNTRY[cc]: vals[cc] for cc in CCS},
                     "agree": agree, "note": f"used by {len(used)} of 6" + ("" if agree == "yes" else ": values differ")})

# common conversion constants
CONV = ["GJ_PER_MMBTU", "UN_NGS_NET_PER_GROSS", "MMBTU_PER_MCF_EIA", "UN_BBL_PER_T_CRU", "IPCC_NCV_CRU",
        "GJ_PER_T_COAL_6000(?:NAR|KCAL)?", "IPCC_NCV_COK", "IPCC_NCV_FOI", "UN_GAL_PER_T_FOI"]
for cpat in CONV:
    vals = {}
    for cc in CCS:
        c = read(cc, "constants.csv")
        k = c.columns[0]
        q = c[c[k].str.fullmatch(cpat)]
        vals[cc] = num(q["value"].iloc[0]) if len(q) else ""
    used = [v for v in vals.values() if v != ""]
    rows.append({"item": "conversion constant", "key": cpat.replace("(?:NAR|KCAL)?", ""), "published_value": "",
                 **{COUNTRY[cc]: vals[cc] for cc in CCS}, "agree": "yes" if len(set(used)) <= 1 else "no",
                 "note": f"used by {len(used)} of 6"})

# benchmark 2024 annual average in USD/GJ used in r (from fuel_prices r text where stated)
# gas conversion
GAS = {"ecu": "DIST_NGS", "cr": "IMPNGS", "jam": "DIST_NGS", "dr": "DIST_NGS", "gua": "DIST_NGS", "hon": "DIST_NGS"}
for cc in CCS:
    t = GAS[cc]
    pp = read(cc, "price_points_2024.csv")
    ch = pp[(pp["row"] == t) & (pp["chosen"] == "yes")].iloc[0]
    v = num(ch.get("value_usd_per_gj_net") or ch.get("value_usd_per_gj"))
    # gross USD/GJ value before the 0.9 step, as recorded by each job
    gross, basis = None, ""
    if cc == "ecu":
        gross, basis = num(ch["value_usd_per_gj_as_recorded"]), "published USD/MMBtu (gross), VAT removed"
    elif cc == "cr":
        gross, basis = 7.763, "gross 7.763 USD/GJ stated in the row's product_and_scope and fuel_prices derivation"
    elif cc == "gua":
        gross, basis = num(ch["price_as_published"]), f"price_as_published {ch['price_as_published']} {ch['unit_as_published']}"
    elif cc == "hon":
        gross, basis = 5.515, "derivation: 5.8185 USD/MMBtu / 1.055056 = 5.515 USD/GJ gross"
    elif cc == "dr":
        gross, basis = None, f"chosen import CIF, basis_note '{ch['basis_note']}' (Comtrade LNG per tonne, net)"
    elif cc == "jam":
        gross, basis = None, "chosen import CIF per tonne of LNG / IPCC NCV 48.0 GJ/t, already net"
    P = read(cc, "proposals.csv")
    g = P[(P["Tech"] == t) & (P["Parameter"] == "VariableCost")]
    p24 = g[(g["year"] == "2024") & (g["fuel_scenario"] == "STEPS")]["proposed_value"]
    p24 = num(p24.iloc[0]) if len(p24) else None
    if gross:
        ratio = p24 / gross if p24 else None
        once = ratio is not None and abs(ratio - 1 / 0.9) < 0.002
        res = f"2024 proposed {p24} / gross {gross} = {ratio:.4f}; divided by 0.9 once: {'yes' if once else 'NO'}"
    else:
        once = None
        res = f"2024 proposed {p24}; not divided (already net)"
    f5rows = g["assumption_sentence"].str.contains(re.escape(F5)).sum()
    anyf5 = g["assumption_sentence"].str.contains("dividing by 0.9").sum()
    # identical wording: extract the F5 sentence block from the first row that has it
    block = ""
    for s in g["assumption_sentence"]:
        i = s.find("ASSUMPTION: natural gas prices published per MMBtu")
        if i >= 0:
            j = s.find("ASSUMPTION:", i + 5)
            block = s[i:j if j > 0 else None].strip()
            break
    same = block == F5
    note = basis
    if gross is None and anyf5:
        note += f"; the F5 sentence is attached to {anyf5} rows whose value was not divided by 0.9"
    rows.append({"item": "gas conversion", "key": f"{COUNTRY[cc]} {t}", "published_value": "",
                 **{COUNTRY[c]: (res if c == cc else "") for c in CCS},
                 "agree": "yes" if (once is True and same) or (once is None and not anyf5) else "no",
                 "note": f"{note}; VariableCost rows {len(g)}, rows with the brief's F5 sentence verbatim {f5rows}, "
                         f"with any 'dividing by 0.9' text {anyf5}; sentence identical to the brief: {'yes' if same else 'no' if block else 'absent'}"})

# exchange rates
FX = {"cr": ("CRC", "CR_FX_2024 515.1098 CRC/USD (World Bank WDI PA.NUS.FCRF, CR-023)"),
      "jam": ("JMD", "JAM_FX_2024 157.22 JMD/USD (BOJ annual weighted average selling rate, JAM-001)"),
      "dr": ("DOP", "DR_FX_2024 59.5665 DOP/USD (BCRD annual mean of daily selling rate, DR-001)"),
      "hon": ("HNL", "HON_FX_2024 24.7950 HNL/USD (BCH mean of 247 daily buying rates, HON-004)"),
      "gua": ("GTQ", "GUA_FX_2024 7.75960 GTQ/USD (Banco de Guatemala web service, GUA-001)"),
      "ecu": ("USD", "Ecuador uses the US dollar; no exchange rate")}
rows.append({"item": "exchange rate", "key": "currency and rate 2024", "published_value": "",
             **{COUNTRY[cc]: FX[cc][1] for cc in CCS}, "agree": "n/a",
             "note": "each country converts its own currency, so no two countries share a currency source and no comparison applies; Costa Rica uses the World Bank WDI period average, the others their central bank (Honduras the buying rate, the others the selling rate)"})

X = pd.DataFrame(rows)
write(X, "cross_country.csv")
print(X[["item", "key", "agree", "note"]].to_string(max_colwidth=120))
