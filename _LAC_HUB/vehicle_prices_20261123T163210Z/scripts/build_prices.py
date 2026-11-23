"""Unit values and class prices of imported vehicles, from government import statistics.

Reads only files under downloads/ (including downloads/manual/), parameters.csv and the job's
own definitions (vehicle_class_map.csv for the lines of each class). Writes, per country:
  <CC>/unit_values_<CC>.csv   per tariff line and year: customs value, units, unit value,
                               currency, exchange rate, CPI factor, value in 2024 US$
  <CC>/class_prices_<CC>.csv  per technology: base price in 2024 US$ per vehicle and how it
                               was formed (own lines, other four countries, or the diesel
                               vehicle of the class times the ATB powertrain ratio)

Run again unchanged after files are added to downloads/manual/:
    python -I scripts/build_prices.py
"""
import csv
import glob
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import national_parsers  # noqa: E402
csv.field_size_limit(10_000_000)

CCS = ["CR", "DR", "GUA", "HON", "JAM"]
ISO3 = {"CR": "CRI", "DR": "DOM", "GUA": "GTM", "HON": "HND", "JAM": "JAM"}
COMTRADE_ID = "COMTRADE-{cc}"


# ---------------------------------------------------------------- parameters and conversions
def read_parameters():
    p = {}
    with open(os.path.join(JOB, "parameters.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            p[r["parameter"]] = r["value"]
    return p


def cpi_factors(price_year):
    """CPI-U annual averages (period M13) from the BLS JSON files; factor = CPI(price_year)/CPI(y)."""
    cpi = {}
    for fn in sorted(glob.glob(os.path.join(JOB, "downloads", "GEN", "bls_CUUR0000SA0_*.json"))):
        with open(fn, encoding="utf-8") as f:
            d = json.load(f)
        for rec in d["Results"]["series"][0]["data"]:
            if rec["period"] == "M13":
                cpi[int(rec["year"])] = float(rec["value"])
    base = cpi[price_year]
    return {y: base / v for y, v in cpi.items()}, cpi


def exchange_rates():
    """WDI PA.NUS.FCRF, local currency per US$, period average, from the WDI bulk CSV zip."""
    fn = glob.glob(os.path.join(JOB, "downloads", "wdi", "WDI_PA.NUS.FCRF_csv.zip"))[0]
    z = zipfile.ZipFile(fn)
    name = [n for n in z.namelist() if n.startswith("API_")][0]
    lines = z.read(name).decode("utf-8-sig").splitlines()
    rows = list(csv.reader(lines[4:]))
    head = rows[0]
    fx = {}
    for row in rows[1:]:
        if len(row) < 2:
            continue
        for cc, iso in ISO3.items():
            if row[1] == iso:
                for i, h in enumerate(head):
                    if h.isdigit() and row[i]:
                        fx[(cc, int(h))] = float(row[i])
    return fx


# ---------------------------------------------------------------- UN Comtrade (reporter data)
def comtrade_records(cc, rejected=()):
    """Country-reported imports from UN Comtrade (reporter = the country, partner = World).

    Quantities estimated by the UN (isQtyEstimated) are not counts of the government and are
    returned with units None, so they never enter an average.
    """
    out = []
    for fn in sorted(glob.glob(os.path.join(JOB, "downloads", "comtrade", f"comtrade_{cc}_imports_*.json"))):
        with open(fn, encoding="utf-8") as f:
            d = json.load(f)
        for r in d.get("data", []):
            if r.get("partnerCode") != 0 or r.get("flowCode") != "M":
                continue
            reported_units = (r.get("qtyUnitCode") == 5 and not r.get("isQtyEstimated") and r.get("qty"))
            note = ("units reported by the country" if reported_units else
                    "units not reported (estimated by the UN from weight); not used")
            if reported_units and cc in rejected:
                reported_units = False
                note = ("units reported by the country are not vehicle counts (far below the vehicles counted "
                        "by the national customs in its own bulletins); not used")
            value = r.get("cifvalue") or r.get("primaryValue")
            basis = "CIF" if r.get("cifvalue") else "primary value"
            out.append({
                "country": cc, "source_id": COMTRADE_ID.format(cc=cc),
                "file": os.path.relpath(fn, JOB).replace("\\", "/"),
                "year": int(r["period"]), "line": r["cmdCode"], "hs6": r["cmdCode"],
                "line_description": f"HS {r['cmdCode']} ({r.get('classificationCode')})",
                "value": float(value or 0), "currency": "USD", "value_basis": basis,
                "units": float(r["qty"]) if reported_units else None,
                "new_used": "all",
                "note": note,
            })
    return out


# ---------------------------------------------------------------- unit values
def build_unit_values(cc, params, cpi, fx):
    recs = national_parsers.records(cc, JOB)
    rejected = [c for c in params["comtrade_units_rejected"].split(";") if c]
    # Comtrade only for years with no national tariff-line file that gives units
    line_years = {r["year"] for r in recs if r["units"] and r.get("hs6")}
    recs += [r for r in comtrade_records(cc, rejected) if r["year"] not in line_years]
    y0, y1 = int(params["first_year"]), int(params["last_year"])
    minu = float(params["min_units_per_line_year"])
    rows = []
    for r in recs:
        if not (y0 <= r["year"] <= y1):
            continue
        if r["currency"] == "USD":
            rate = 1.0
        else:
            rate = fx[(cc, r["year"])]
        usd = r["value"] / rate
        f = cpi[r["year"]]
        usd24 = usd * f
        units = r["units"]
        uv = usd24 / units if units else None
        if units is None:
            used, why = "no", r["note"]
        elif r["new_used"] == "used":
            used, why = "no", "used vehicles; the tariff separates new from used and only new vehicles are averaged"
        elif units < minu:
            used, why = "no", f"fewer than {int(minu)} units"
        else:
            used, why = "yes", r["note"]
        rows.append({
            "country": cc, "year": r["year"], "line": r["line"], "hs6": r["hs6"],
            "type_label": r.get("type_label", ""),
            "line_description": r["line_description"], "new_used": r["new_used"],
            "customs_value": round(r["value"], 2), "currency": r["currency"], "currency_year": r["year"],
            "value_basis": r["value_basis"], "exchange_rate": rate,
            "value_usd": round(usd, 2), "cpi_factor": round(f, 6), "value_usd2024": round(usd24, 2),
            "units": units if units is None else round(units, 3),
            "unit_value_usd2024": None if uv is None else round(uv, 2),
            "used_in_average": used, "reason": why, "source_id": r["source_id"], "file": r["file"],
        })
    rows.sort(key=lambda x: (x["hs6"], x["line"], x["year"]))
    return rows


# ---------------------------------------------------------------- class prices
def read_class_map():
    with open(os.path.join(JOB, "vehicle_class_map.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def class_lines(r):
    return sorted({c for col in ("hs2017_codes", "hs2022_codes") for c in r[col].split(";") if c})


def read_type_map():
    with open(os.path.join(JOB, "national_type_map.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pool(uv_rows, lines, types=()):
    sel = [x for x in uv_rows if x["used_in_average"] == "yes" and
           ((x["hs6"] and x["hs6"] in lines) or (x["type_label"] and x["type_label"] in types))]
    v = sum(x["value_usd2024"] for x in sel)
    u = sum(x["units"] for x in sel)
    return (v / u if u else None), v, u, sel


ATB_MAP = {  # vehicle class -> ATB class (as in the cost-sources vehicle package)
    "car": "Compact", "taxi": "Compact", "SUV": "Small_SUV", "pickup or light truck": "Pickup",
    "minibus": "4", "heavy truck": "8", "bus": "8",
}
ATB_DETAIL_LD = {  # light duty; proxies as in the cost-sources vehicle package
    "diesel": "Conventional CI", "gasoline": "Conventional SI", "gasoline (flex fuel)": "Conventional SI",
    "LPG": "Conventional SI", "natural gas": "Conventional CNG", "hybrid gasoline": "Split HEV",
    "hybrid diesel": "Split HEV", "plug-in hybrid gasoline": "EREV PHEV50",
    "plug-in hybrid diesel": "EREV PHEV50", "battery electric": "BEV300", "fuel cell": "Fuel Cell 300"}
ATB_DETAIL_HD = {  # medium and heavy duty
    "diesel": "Conv", "gasoline": "Conv", "gasoline (flex fuel)": "Conv", "LPG": "Conv", "natural gas": "Conv",
    "hybrid diesel": "ParHEV", "hybrid gasoline": "ParHEV", "plug-in hybrid diesel": "SeriesPHEV",
    "plug-in hybrid gasoline": "SeriesPHEV", "battery electric": "BEV", "fuel cell": "FCEV"}


def atb_ratio(vclass, powertrain):
    """ATB 2022 Mid price of the powertrain over the diesel vehicle of the same ATB class, 2024
    (interpolated linearly between the published years, as in the cost-sources package)."""
    fn = os.path.join(JOB, "downloads", "GEN", "NREL_ATB_2022_transportation_vehicles.csv")
    atb_class = ATB_MAP[vclass]
    det = ATB_DETAIL_HD if atb_class in ("4", "8") else ATB_DETAIL_LD
    pts = {}
    with open(fn, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["scenario"] != "Mid" or r["vehicle_class"] != atb_class:
                continue
            for pt in ("diesel", powertrain):
                if r["vehicle_detail"] == det[pt]:
                    pts.setdefault(pt, {})[int(r["year"])] = float(r["vehicle_cost(2020$)"])

    def at2024(s):
        lo = max(y for y in s if y <= 2024)
        hi = min(y for y in s if y >= 2024)
        if lo == hi:
            return s[lo]
        return s[lo] + (s[hi] - s[lo]) * (2024 - lo) / (hi - lo)

    a, b = at2024(pts[powertrain]), at2024(pts["diesel"])
    return a / b, a, b, f"ATB 2022 Mid class {atb_class}, {det[powertrain]} {a:.1f} / {det['diesel']} {b:.1f} (2020 US$, 2024 interpolated)"


def describe(sel):
    by = {}
    for x in sel:
        k = (x["country"], x["hs6"] or x["type_label"])
        by.setdefault(k, []).append(x)
    parts = []
    for (c, h), xs in sorted(by.items()):
        yrs = sorted({x["year"] for x in xs})
        parts.append(f"{c} {h} {min(yrs)}-{max(yrs)} ({len(yrs)} yr): {sum(x['units'] for x in xs):.0f} units, "
                     f"{sum(x['value_usd2024'] for x in xs):.0f} US$2024")
    return "; ".join(parts)


def build_class_prices(uv, cmap, tmap):
    out = []
    # first pass: own lines and other-country pools
    res = {}
    for r in cmap:
        cc = r["country"]
        if r["vehicle_class"] == "rail":
            continue
        lines = class_lines(r)
        price, v, u, sel = (None, 0, 0, [])
        method = ""
        if r["own_lines_priced"] == "yes":
            price, v, u, sel = pool(uv[cc], lines)
            method = "own lines"
            if price is None:
                types = [t["source_label"] for t in tmap if t["country"] == cc
                         and r["vehicle_class"] in t["vehicle_class"].split(";")
                         and r["powertrain"] in t["powertrains"].split(";")]
                if types:
                    price, v, u, sel = pool(uv[cc], [], types)
                    method = "own customs statistics by vehicle type"
            if price is None:
                others = [x for c2 in CCS if c2 != cc for x in uv[c2]]
                price, v, u, sel = pool(others, lines)
                method = "other four countries" if price is not None else ""
        res[(cc, r["tech"])] = (price, v, u, sel, method)
    # second pass: rule 3, diesel vehicle of the class times the ATB powertrain ratio
    for r in cmap:
        cc = r["country"]
        if r["vehicle_class"] == "rail":
            continue
        price, v, u, sel, method = res[(cc, r["tech"])]
        detail = describe(sel) if sel else ""
        ratio_note = ""
        if price is None:
            dsl = [m for m in cmap if m["country"] == cc and m["vehicle_class"] == r["vehicle_class"]
                   and m["powertrain"] == "diesel"]
            if dsl:
                p0, v0, u0, sel0, m0 = res[(cc, dsl[0]["tech"])]
                lines0 = class_lines(dsl[0])
            else:  # no diesel vehicle of this class in the model: use the class's diesel lines
                proto = next(m for m in cmap if m["vehicle_class"] == r["vehicle_class"] and m["powertrain"] == "diesel")
                lines0 = class_lines(proto)
                p0, v0, u0, sel0 = pool(uv[cc], lines0)
                m0 = "own lines"
                if p0 is None:
                    types0 = [t["source_label"] for t in tmap if t["country"] == cc
                              and r["vehicle_class"] in t["vehicle_class"].split(";")
                              and "diesel" in t["powertrains"].split(";")]
                    if types0:
                        p0, v0, u0, sel0 = pool(uv[cc], [], types0)
                        m0 = "own customs statistics by vehicle type"
                if p0 is None:
                    p0, v0, u0, sel0 = pool([x for c2 in CCS if c2 != cc for x in uv[c2]], lines0)
                    m0 = "other four countries"
            k, a, b, txt = atb_ratio(r["vehicle_class"], r["powertrain"])
            price = p0 * k
            v, u = v0, u0
            method = f"diesel {r['vehicle_class']} ({m0}) x ATB ratio"
            detail = describe(sel0)
            ratio_note = f"{k:.6f} = {txt}"
        out.append({
            "country": cc, "model": r["model"], "tech": r["tech"], "vehicle_class": r["vehicle_class"],
            "powertrain": r["powertrain"], "lines": ";".join(class_lines(r)), "method": method,
            "base_price_usd2024": None if price is None else round(price, 2),
            "value_usd2024": round(v, 2), "units": round(u, 3), "atb_ratio": ratio_note,
            "detail": detail,
        })
    return out


def write(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    params = read_parameters()
    cpi, _ = cpi_factors(int(params["price_year"]))
    fx = exchange_rates()
    uv = {}
    for cc in CCS:
        uv[cc] = build_unit_values(cc, params, cpi, fx)
        write(os.path.join(JOB, cc, f"unit_values_{cc}.csv"), uv[cc])
    cp = build_class_prices(uv, read_class_map(), read_type_map())
    for cc in CCS:
        write(os.path.join(JOB, cc, f"class_prices_{cc}.csv"), [x for x in cp if x["country"] == cc])
        n = sum(1 for x in uv[cc] if x["used_in_average"] == "yes")
        print(cc, len(uv[cc]), "line-years,", n, "used")


if __name__ == "__main__":
    main()
