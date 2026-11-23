"""Build the Costa Rica proposal, source, search-log and manual files (LAC_COST_SOURCES Phase 2).

Run: python -I build_proposals_CR.py  (paths are built from this file's location)
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CC_DIR = os.path.dirname(HERE)
JOB = os.path.dirname(CC_DIR)
GEN = os.path.join(JOB, "GEN")

CPI = {}
with open(os.path.join(JOB, "cpi_u.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        CPI[int(r["year"])] = float(r["factor_to_2024"])

RETR = "2026-11-22"

# ---------------------------------------------------------------- GEN vehicle package
gen = list(csv.DictReader(open(os.path.join(GEN, "gen_vehicle_factors.csv"), encoding="utf-8")))
REF = {}      # (class, pt, source) -> (value, value_2024)
MAINT = {}    # (class, pt) -> (value_src M US$/Gvkm, value_2024)
TRAJ_PUB = {}  # (class, pt) -> {year: price}
TRAJ = {}     # (class, pt) -> {year: ratio}
for r in gen:
    key = (r["vehicle_class"], r["powertrain"])
    if r["item"] == "reference_price":
        REF[key + (r["source_id"],)] = (float(r["value"]), float(r["value_2024usd"]))
    elif r["item"] == "maintenance_cost" and r["unit"] == "M US$ per Gvkm":
        MAINT[key] = (float(r["value"]), float(r["value_2024usd"]))
    elif r["item"] == "price_trajectory":
        TRAJ.setdefault(key, {})[int(float(r["year"]))] = float(r["value"])
        m = re.search(r"Published prices \(2020 USD\): ([^.]+)\.", r["derivation"])
        if m and key not in TRAJ_PUB:
            TRAJ_PUB[key] = {int(a): float(b) for a, b in re.findall(r"(\d{4})=(\d+(?:\.\d+)?)", m.group(1))}


def interp(pub, y):
    ys = sorted(pub)
    if y <= ys[0]:
        return pub[ys[0]]
    for a, b in zip(ys, ys[1:]):
        if a <= y <= b:
            return pub[a] + (pub[b] - pub[a]) * (y - a) / (b - a)
    return pub[ys[-1]]


def ratio(cls, pt, y):
    if y >= 2024:
        return TRAJ[(cls, pt)][y]
    pub = TRAJ_PUB[(cls, pt)]
    return interp(pub, y) / interp(pub, 2024)


# ---------------------------------------------------------------- cells
cells = list(csv.DictReader(open(os.path.join(CC_DIR, "cells_CR.csv"), encoding="utf-8")))

KM = {"TRNMIC": 32843, "TRNBUS": 58999, "TRNTAX": 46880, "TRNPASRAI": 1, "TRNMOT": 7413,
      "TRNSED": 12095, "TRNSUV": 12095, "TRNFREHEA": 26979, "TRNFRELIG": 15455}
GROUP_CLASS = {"TRNMIC": "minibus", "TRNBUS": "bus", "TRNTAX": "taxi", "TRNSED": "car", "TRNSUV": "SUV",
               "TRNFRELIG": "light_freight", "TRNFREHEA": "heavy_freight", "TRNMOT": "motorcycle"}
PT_MAP = {"DSL": "DSL", "GSL": "GSL", "LPG": "LPG", "ELE": "ELE", "HYD": "HYD", "NGV": "NGS",
          "HYBDSL": "HD", "HYBGSL": "HG"}
PT_WORD = {"DSL": "diesel", "GSL": "gasoline", "LPG": "LPG", "ELE": "battery electric", "HYD": "fuel cell",
           "NGS": "CNG", "HD": "diesel hybrid", "HG": "gasoline hybrid"}


def split_tech(t):
    for g in sorted(KM, key=len, reverse=True):
        if t.startswith(g):
            return g, t[len(g):]
    raise ValueError(t)


# National bus prices: CEPAL (2022), CR-001, PDF p. 110 (diesel, ARESEP tope) and p. 57 (BYD K9G e-bus)
BUS_DSL_SRC = 127500.0   # USD, from 74,087,835 CRC at 581.02 CRC/USD as stated in the source
BUS_ELE_SRC = 400000.0   # USD, BYD K9G, battery included, charger apart
BUS_CY = 2020
ATB8 = {"DSL": 160750.0, "HD": 172750.0, "HYD": 292000.0}  # ATB 2022 Class 8 Mid, 2021 published price (2020 USD)


def base_price(cls, pt):
    """Return (price_2024, source_ids, source_value, source_unit, cy, cpi, text)."""
    if cls == "bus":
        if pt == "ELE":
            v = BUS_ELE_SRC * CPI[BUS_CY]
            return (v, "CR-001", BUS_ELE_SRC, "US$ per vehicle", BUS_CY, CPI[BUS_CY],
                    "Costa Rica 12 m battery electric bus (BYD K9G, battery included, price reported by the national distributor) USD 400,000 (CR-001, p. 57), 2020 USD x %.6f = %.0f real 2024 US$" % (CPI[BUS_CY], v))
        d = BUS_DSL_SRC * CPI[BUS_CY]
        txt = ("Costa Rica diesel interurban bus, ARESEP-approved ceiling price CRC 74,087,835 = USD 127,500 at 581.02 CRC per USD (CR-001, p. 110), 2020 USD x %.6f = %.0f real 2024 US$" % (CPI[BUS_CY], d))
        if pt in ("DSL", "LPG", "GSL", "NGS"):
            if pt != "DSL":
                txt += "; LPG bus takes the diesel bus price (GEN proxy rule for heavy duty)"
            return (d, "CR-001", BUS_DSL_SRC, "US$ per vehicle", BUS_CY, CPI[BUS_CY], txt)
        f = ATB8[pt] / ATB8["DSL"]
        v = d * f
        return (v, "CR-001;GEN-101", BUS_DSL_SRC, "US$ per vehicle", BUS_CY, CPI[BUS_CY],
                txt + "; times ATB 2022 Class 8 %s / diesel price ratio %.0f / %.0f = %.4f (GEN-101) = %.0f" % (PT_WORD[pt], ATB8[pt], ATB8["DSL"], f, v))
    src = "GEN-101"
    if (cls, pt, src) not in REF:
        raise KeyError((cls, pt))
    sv, v = REF[(cls, pt, src)]
    return (v, src, sv, "US$ per vehicle", 2020, CPI[2020],
            "GEN reference price %s %s (NREL ATB 2022 Mid, United States price, excludes Costa Rica import taxes) %.0f 2020 USD x %.6f = %.1f real 2024 US$" % (cls.replace("_", " "), PT_WORD[pt], sv, CPI[2020], v))


rows = []


def cls_of(src_val, cur):
    if cur is None or cur == 0:
        return "replace"
    return "confirmed" if abs(src_val / cur - 1.0) <= 0.25 + 1e-9 else "replace"


def emit(c, proposed, cclass, sids="", sval="", sunit="", cy="", cpi="", deriv="", assum=""):
    def fmt(x):
        if x == "" or x is None:
            return ""
        if isinstance(x, float):
            return ("%.6f" % x).rstrip("0").rstrip(".")
        return str(x)
    rows.append({
        "country": c["country"], "model": c["model"], "sheet": c["sheet"], "tech": c["tech"],
        "tech_name": c["tech_name"], "parameter": c["parameter"], "unit_introduced": c["unit_introduced"],
        "unit": c["unit"], "projection_mode": c["projection_mode"], "year": c["year"],
        "current_value": c["current_value"], "proposed_value": fmt(proposed), "change_class": cclass,
        "source_ids": sids, "source_value": fmt(sval), "source_unit": sunit, "source_currency_year": fmt(cy),
        "cpi_factor": fmt(cpi), "derivation": deriv, "assumption_sentence": assum,
        "ao_row_at_b51f24b": c["ao_row_at_b51f24b"]})


MOTO_GSL_PRICE = 2000.0
MOTO_MAINT = {"GSL": 25.0, "ELE": 15.0}

for c in cells:
    if c["phase2_scope"] != "vehicle":
        continue
    cur = float(c["current_value"])
    g, sfx = split_tech(c["tech"])
    # ---------------- rail rows (M US$ per GPkm, distance 1 km)
    if g == "TRNPASRAI":
        if c["parameter"] == "CapitalCost":
            emit(c, cur, "assumption", deriv="Flat row: base-year cell only, every year takes it. Cell holds the formula 1956.73947317362 / 0.7315286784 (M US$ per GPkm); entered in the row's own unit, not converted by distance.",
                 assum="The electric passenger train capital cost is 2,674.9 M US$ per billion passenger-km of annual capacity (2.67 US$ per passenger-km of yearly service), covering rolling stock and electrification of the Greater Metropolitan Area train. Published estimates for light and suburban rail investment per annual passenger-km vary widely with corridor load, so the value carries a range of 1,500 to 5,000 M US$ per GPkm.")
        else:
            emit(c, cur, "assumption", deriv="Flat row: base-year cell only, every year takes it. Cell holds the formula 26.1 / 0.7315286784 (M US$ per GPkm); entered in the row's own unit, not converted by distance.",
                 assum="The electric passenger train fixed operation and maintenance cost is 35.7 M US$ per billion passenger-km of annual capacity (0.036 US$ per passenger-km), about 1.3 percent of its capital cost per year. The value carries a range of 20 to 70 M US$ per GPkm, in line with yearly maintenance shares of 1 to 3 percent of rail investment.")
        continue
    cls = GROUP_CLASS[g]
    pt = PT_MAP[sfx]
    y = int(c["year"])
    km = KM[g]
    if c["parameter"] == "CapitalCost":
        if cls == "motorcycle":
            if pt == "ELE":
                sv, v = REF[("motorcycle", "ELE", "GEN-104")]
                compiled = 1000 * v / km
                emit(c, v, cls_of(v, cur), "GEN-104", sv, "US$ per vehicle", 2020, CPI[2020],
                     "Electric motorcycle price USD 3,000 from the Dominican Republic national electric mobility plan (GEN-104, p. 94), 2020 USD x %.6f = %.1f real 2024 US$ per vehicle; held flat in every year because no published trajectory covers motorcycles. Compiles to 1000 x %.1f / %d km = %.2f M US$ per Gvkm (current cell %.4f compiles to %.4f)." % (CPI[2020], v, v, km, compiled, cur, 1000 * cur / km))
            else:
                v = MOTO_GSL_PRICE
                emit(c, v, "assumption", deriv="ASSUMPTION price 2,000 US$ per vehicle held flat in every year (no published motorcycle trajectory). Compiles to 1000 x 2000 / %d km = %.2f M US$ per Gvkm (current cell %.4f compiles to %.4f)." % (km, 1000 * v / km, cur, 1000 * cur / km),
                     assum="A new gasoline motorcycle of the commuter class (125 to 200 cc) that dominates the Costa Rica fleet costs 2,000 US$ per vehicle in real 2024 terms, held flat to 2050. The Dominican Republic national electric mobility plan prices an electric motorcycle at 3,000 US$, and the value carries a range of 1,200 to 3,500 US$.")
            continue
        p24, sids, sv, sunit, cy, cpi, txt = base_price(cls, pt)
        r = ratio(cls, pt, y)
        v = p24 * r
        compiled = 1000 * v / km
        traj_note = ("ATB 2022 Mid trajectory ratio to the 2024 price %.4f for %d (GEN-101, price_trajectory %s %s)" % (r, y, cls, pt) if y >= 2024 else
                     "ATB 2022 Mid published prices interpolated linearly, ratio to 2024 %.4f for %d (GEN-101)" % (r, y))
        sids2 = sids if "GEN-101" in sids else sids + ";GEN-101"
        deriv = ("%s; times %s = %.1f US$ per vehicle. The compiler turns it into 1000 x %.1f / %d km (Ref.km.BY of %s, constant) = %.2f M US$ per Gvkm; the current cell %.4f compiles to %.4f. Unit question raised as a decision: the current cells behave like prices already divided by distance." % (txt, traj_note, v, v, km, g, compiled, cur, 1000 * cur / km))
        emit(c, v, cls_of(v, cur), sids2, sv, sunit, cy, cpi, deriv)
        continue
    # FixedCost (M US$ per Gvkm), flat
    if cls == "motorcycle":
        v = MOTO_MAINT[pt]
        emit(c, v, "assumption", deriv="ASSUMPTION %.0f M US$ per Gvkm (%.3f US$ per km), flat in every year." % (v, v / 1000),
             assum=("Maintenance and repair of a %s motorcycle costs %.0f M US$ per Gvkm (%.3f US$ per km) in real 2024 terms, flat to 2050. No published motorcycle maintenance series exists in the NREL Annual Technology Baseline, whose compact car value is 93 M US$ per Gvkm; motorcycles have far fewer parts and tyres, and the value carries a range of %d to %d M US$ per Gvkm." %
                    ("gasoline" if pt == "GSL" else "battery electric", v, v / 1000, 10 if pt == "GSL" else 5, 40 if pt == "GSL" else 25)))
        continue
    sv, v = MAINT[(cls, pt)]
    cc = cls_of(v, cur)
    deriv = ("Flat in every year. GEN maintenance_cost %s %s: ATB 2022 levelized maintenance and repair %.3f M US$ per Gvkm in 2020 USD x %.6f = %.3f real 2024 (GEN-102). Entered directly in M US$ per Gvkm (no distance conversion)." % (cls, pt, sv, CPI[2020], v))
    emit(c, cur if cc == "confirmed" else v, cc, "GEN-102", sv, "M US$ per Gvkm", 2020, CPI[2020], deriv)

# ---------------------------------------------------------------- chain inputs
OL = {}
for c in cells:
    if c["phase2_scope"] != "vehicle_chain":
        continue
    cur = float(c["current_value"])
    if c["parameter"] == "Ref.km.BY":
        g = c["tech"]
        if g == "TRNBUS":
            src = 49500.0
            emit(c, cur, cls_of(src, cur), "CR-001", "45000 km + 10% unproductive", "km per bus per year", "", "",
                 "Costa Rica concession bus: 45,000 km per year plus 10 percent unproductive km = 49,500 km (CR-001, Cuadro A18, PDF p. 204); 49,500 / 58,999 = 0.839, within 25 percent, so the current value stays. The CEPAL (2024) TCO annex uses 60,000 km per year for urban buses (CR-002, p. 83).")
        elif g == "TRNMIC":
            emit(c, cur, cls_of(35942.0, cur), "GEN-103", 35942, "km per vehicle per year", "", "",
                 "GEN annual_km minibus: ATB Class 4 step van 335,000 miles over 15 years = 35,942 km per year (GEN-103); 35,942 / 32,843 = 1.094, within 25 percent, so the current value stays.")
        elif g == "TRNPASRAI":
            emit(c, cur, "assumption", deriv="Placeholder distance: the rail group is entered in GPkm and its cost rows are in M US$ per GPkm, so the distance enters no conversion.",
                 assum="The rail group uses a distance of 1 km per vehicle per year because its activity and costs are entered per passenger-km, so no conversion from vehicles applies. The value is a unit placeholder with no range.")
        else:
            txt = {
                "TRNSED": ("12,095 km per sedan per year", "the Dominican Republic national electric mobility plan uses 7,500 km per year for cars and the NREL Annual Technology Baseline uses 19,108 km per year for a new United States light-duty vehicle", "7,500 to 19,108"),
                "TRNSUV": ("12,095 km per SUV per year", "the Dominican Republic national electric mobility plan uses 7,500 km per year for cars and jeeps and the NREL Annual Technology Baseline uses 19,108 km per year for a new United States light-duty vehicle", "7,500 to 19,108"),
                "TRNTAX": ("46,880 km per taxi per year (about 130 km per day)", "taxis run several times the distance of private cars; the NREL Annual Technology Baseline gives 19,108 km per year for a private light-duty vehicle", "35,000 to 60,000"),
                "TRNMOT": ("7,413 km per motorcycle per year", "the Dominican Republic national electric mobility plan uses 10,500 km per year", "5,000 to 10,500"),
                "TRNFRELIG": ("15,455 km per light freight vehicle per year", "the Dominican Republic national electric mobility plan uses 9,000 km per year for all cargo vehicles and the NREL Annual Technology Baseline uses 19,108 km per year for light-duty vehicles", "9,000 to 19,108"),
                "TRNFREHEA": ("26,979 km per heavy freight vehicle per year", "the Dominican Republic national electric mobility plan uses 9,000 km per year for all cargo vehicles, while long-haul tractors elsewhere exceed 50,000 km per year", "15,000 to 50,000"),
            }[g]
            emit(c, cur, "assumption", deriv="Base-year distance, constant to 2050 (A-Xtra_Projections change zero). Every price row of the group compiles as 1000 x price / this distance.",
                 assum="The distance is %s in the base year and stays constant to 2050, as measured for the Costa Rica fleet before 2020. For comparison, %s; the value carries a range of %s km." % txt)
    else:  # OperationalLife
        t = c["tech"]
        g, sfx = split_tech(t)
        if g == "TRNBUS":
            emit(c, cur, cls_of(15.0, cur), "CR-002", 15, "years", "", "",
                 "Legal service life of a bus in Costa Rica set by the Consejo de Transporte Publico: 15 years (CR-002, PDF p. 83, annex table of assumptions). 15 / %d = %.3f, within 25 percent, so the current value stays." % (cur, 15 / cur))
        elif g == "TRNMIC":
            emit(c, 15.0, "replace", "CR-002;GEN-103", 15, "years", "", "",
                 "Current 1 year makes the full price fall every year. Proposed 15 years: GEN operational_life minibus, ATB 2022 Class 4 van life 15 years (GEN-103), equal to the 15-year legal service life of public transport buses in Costa Rica (CR-002, PDF p. 83).")
        elif g in ("TRNSED", "TRNSUV", "TRNTAX", "TRNFRELIG"):
            cc = cls_of(15.0, cur)
            emit(c, cur if cc == "confirmed" else 15.0, cc, "GEN-103", 15, "years", "", "",
                 "GEN operational_life light duty: ATB 2022 vehicle life 15 years (GEN-103); 15 / %d = %.3f." % (cur, 15 / cur))
        elif g == "TRNMOT":
            cc = cls_of(10.0, cur)
            emit(c, cur if cc == "confirmed" else 10.0, cc, "GEN-104", 10, "years", "", "",
                 "GEN operational_life motorcycle: 10-year theoretical vehicle life of the Dominican Republic national electric mobility plan (GEN-104, p. 78 footnote 11); 10 / %d = %.3f." % (cur, 10 / cur))
        elif g == "TRNFREHEA":
            emit(c, cur, "assumption", deriv="Same life for every heavy freight powertrain.",
                 assum="A heavy freight vehicle stays in service 20 years in Costa Rica. Vehicles inspected in 2019 averaged about 16 years of age and trailers 27 years according to the inspection operator, while the Dominican Republic national electric mobility plan uses a 10-year theoretical life; the value carries a range of 15 to 25 years.")
        elif g == "TRNPASRAI":
            emit(c, cur, "assumption", deriv="Rail rolling stock life.",
                 assum="Electric passenger trains stay in service 20 years. Rolling stock and electrification assets commonly last 25 to 40 years, so the value carries a range of 20 to 35 years.")

# ---------------------------------------------------------------- sector rows
fao = {}
for r in csv.DictReader(open(os.path.join(GEN, "faostat_trade_unit_values.csv"), encoding="utf-8")):
    if r["country"] == "CR" and r["year"] == "avg_2019_2023":
        fao[r["model_item"]] = r

IMP_ITEM = {"IMPRIC": "rice", "IMPBAN": "banana", "IMPCAF": "coffee", "IMPSUG": "sugar", "IMPMOL": "molasses",
            "IMPPIN": "pineapple", "IMPORG": "oranges", "IMPVEG": "vegetables", "IMPOTG": "other_grains",
            "IMPLEC": "milk", "IMPCAR": "beef"}

# SEPSA crop cost models (US$ per ha, currency year 2025 except banana 2026)
CAFE = [6277.2, 1970.4, 3112.0, 4048.1, 4327.3, 4571.9, 4409.3, 4896.9] + [4268.0] * 13
PALM = [3570.3, 989.3, 1609.3, 1493.4, 1685.9, 1808.7, 1990.7, 2129.0, 2139.4, 2162.6, 2011.5, 2137.0, 2204.1,
        2333.7, 2169.7, 2325.9, 2303.8, 2206.4, 2342.9, 2382.0, 2300.5]
ORANGE = [6505.3, 2527.6, 2973.2, 3122.6, 3831.2, 3839.8, 3855.4, 4190.6, 4206.2, 4190.6, 4206.2]
assert len(CAFE) == 21 and len(PALM) == 21 and len(ORANGE) == 11
avg = lambda xs: sum(xs) / len(xs)
F25 = CPI[2025]
CROP = {
    # tech: (capital source tuple or None, annual source tuple)
    "AGRCAF": (("CR-004", CAFE[0], "year 0 (renovation of one hectare) US$ 6,277.2 per ha, PDF p. 4 to 5"),
               ("CR-004", avg(CAFE[1:]), "mean of the yearly totals of years 1 to 20 (PDF pp. 6 to 25)")),
    "AGRPLM": (("CR-009", PALM[0], "year 0 (renovation) US$ 3,570.3 per ha, resumen PDF p. 25"),
               ("CR-009", avg(PALM[1:]), "mean of the yearly totals of years 1 to 20 (resumen PDF pp. 25 to 27)")),
    "AGRORG": (("CR-008", ORANGE[0], "year 0 (establishment) US$ 6,505.3 per ha, resumen PDF p. 14"),
               ("CR-008", avg(ORANGE[1:]), "mean of the yearly totals of years 1 to 10 (resumen PDF pp. 14 to 15)")),
    "AGRRIC": (None, ("CR-005;CR-006", (3413.5 + 3239.6) / 2, "mean of rainfed (secano) US$ 3,413.5 and irrigated (riego) US$ 3,239.6 per ha per cycle (resumen PDF p. 5 and p. 6)")),
    "AGRPIN": (None, ("CR-007", 19344.3, "annual mean of years 1 and 2, US$ 19,344.3 per ha (resumen PDF p. 6)")),
    "AGROTG": (None, ("CR-010", 1682.8, "maize, Chorotega, US$ 1,682.8 per ha per cycle (resumen PDF p. 4)")),
    "AGRVEG": (None, ("CR-011;CR-013", 2959.7 + 15563.4, "onion, Central Oriental: seedbed US$ 2,959.7 plus field US$ 15,563.4 = 18,523.1 per ha (CR-011, resumen PDF p. 6); field tomato at US$ 46,327.3 per ha (CR-013) marks the upper end of the vegetable group")),
}
cur_by = {}
for c in cells:
    if c["model"] == "CR_AFOLU":
        cur_by[(c["tech"], c["parameter"])] = float(c["current_value"])

for c in cells:
    if c["phase2_scope"] != "sector_choice":
        continue
    cur = float(c["current_value"])
    t, p = c["tech"], c["parameter"]
    flat = "Flat row: base-year cell only, every year takes it. "
    if c["model"] == "CR_WASTE":
        src = 34.22 * CPI[2010]
        tot = cur_by_w = None
        tot = 0.009 + 0.0297
        f = (src / 1000) / tot
        v = cur * f
        emit(c, v, "replace", "GEN-206", 34.22, "US$ per t (collection, LAC average)", 2010, CPI[2010],
             flat + "Unit inferred as M US$ per kt (activity in Gg, CapitalCost 0.009 + VariableCost 0.0297 = 0.0387 M US$ per kt = 38.7 US$ per t). CEPAL 2016 Cuadro 6 collection 34.22 US$ per t (2010 USD) x %.6f = %.2f real 2024 US$ per t = %.5f M US$ per kt; ratio to current total %.3f; proposed value keeps the model's capital/variable split: %s x %.4f = %.6f. What a Waste 2.0 (GEN-204) gives 62 to 125 real 2024 US$ per t for collection and transfer in upper-middle income countries." % (CPI[2010], src, src / 1000, f, c["current_value"], f, v))
        continue
    if t.startswith("IMP"):
        item = IMP_ITEM[t]
        r = fao[item]
        src = float(r["unit_value_2024usd"])
        if t == "IMPPIN":
            emit(c, cur, "assumption", deriv=flat + "Unit inferred as M US$ per Mt = US$ per t (activity in Mt). FAOSTAT import unit value 8,701 US$ per t rests on 8 t per year and is not usable.",
                 assum="Imported pineapple costs 470.8 US$ per tonne. Costa Rica hardly imports pineapple (about 8 tonnes a year in FAOSTAT trade data), and the FAOSTAT producer price is about 285 US$ per tonne (real 2024, 2022 to 2023), so the value carries a range of 285 to 700 US$ per tonne.")
            continue
        cc = cls_of(src, cur)
        emit(c, cur if cc == "confirmed" else src, cc, "GEN-201", src,
             "US$ per t (real 2024, quantity-weighted mean 2019-2023)", "2019-2023", "per year 1.226992 (2019) to 1.029494 (2023), GEN-001",
             flat + "Unit inferred as M US$ per Mt = US$ per t (import activity in Mt). FAOSTAT import unit value for Costa Rica, %s (FAO %s), import value / import quantity per year deflated to 2024 and averaged by quantity over 2019-2023 = %.2f US$ per t; ratio to current %.3f." % (r["fao_items"], r["fao_item_codes"], src, src / cur))
        continue
    # crop production rows, unit M US$ per Mha = US$ per ha
    unit_txt = "Unit inferred as M US$ per Mha = US$ per ha per year (activity in Mha, OutputActivityRatio in t per ha). "
    if t == "AGRBAN":
        sentences = {
            "CapitalCost": "Establishing one hectare of export banana costs 4,460.2 US$ of capacity investment in Costa Rica. The national cost model for smallholder (criollo) banana in the Huetar Caribe region gives an initial investment of 3,709 US$ per ha (2026 USD), and export plantations with cable and drainage systems cost more, so the value carries a range of 3,700 to 9,000 US$ per ha.",
            "FixedCost": "The fixed yearly cost of one hectare of export banana is 245.3 US$ per ha, and together with the variable cost the yearly production cost is 8,178 US$ per ha. The national smallholder (criollo) banana cost model gives 4,788 US$ per ha per year (2026 USD), while the FAOSTAT gross output value is about 19,400 US$ per ha (51.9 t per ha at 373 US$ per t), so the total carries a range of 4,800 to 19,000 US$ per ha.",
            "VariableCost": "The variable yearly cost of one hectare of export banana is 7,932.7 US$ per ha, and together with the fixed cost the yearly production cost is 8,178 US$ per ha. The national smallholder (criollo) banana cost model gives 4,788 US$ per ha per year (2026 USD), while the FAOSTAT gross output value is about 19,400 US$ per ha (51.9 t per ha at 373 US$ per t), so the total carries a range of 4,800 to 19,000 US$ per ha.",
        }
        emit(c, cur, "assumption", deriv=flat + unit_txt + "Compared with CR-012 (criollo banana, 2026 USD) and FAOSTAT yield and producer price (GEN-202, GEN-203).", assum=sentences[p])
        continue
    capsrc, annsrc = CROP[t]
    if p == "CapitalCost":
        if capsrc is None:
            name = {"AGRRIC": "rice", "AGRPIN": "pineapple", "AGROTG": "other grains (maize)", "AGRVEG": "other vegetables"}[t]
            extra = {"AGRRIC": "The national rice cost models count land preparation inside each cycle's cost",
                     "AGRPIN": "The national pineapple cost model counts planting inside the first-year cost of 27,259 US$ per ha (2025 USD)",
                     "AGROTG": "The national maize cost model counts land preparation inside each cycle's cost",
                     "AGRVEG": "The national onion and tomato cost models count land preparation inside each cycle's cost"}[t]
            emit(c, cur, "assumption", deriv=flat + unit_txt + "No separate establishment cost in the national crop cost model.",
                 assum="Expanding %s area costs %s US$ per hectare of capacity in Costa Rica, for land clearing, levelling, drainage and farm equipment. %s, so the value carries a range of %s to %s US$ per ha." %
                       (name, "{:,.1f}".format(cur), extra, "{:,.0f}".format(cur * 0.5), "{:,.0f}".format(cur * 1.5)))
            continue
        sid, sv, note = capsrc
        s24 = sv * F25
        cc = cls_of(s24, cur)
        emit(c, cur if cc == "confirmed" else s24, cc, sid, sv, "US$ per ha (establishment)", 2025, F25,
             flat + unit_txt + "SEPSA/MAG national cost model, %s; 2025 USD x %.6f = %.1f real 2024; ratio to current %.3f." % (note, F25, s24, s24 / cur))
        continue
    # Fixed and Variable: compare sum
    sid, sv, note = annsrc
    s24 = sv * F25
    fixed = cur_by[(t, "FixedCost")]
    var = cur_by[(t, "VariableCost")]
    tot = fixed + var
    f = s24 / tot
    cc = "confirmed" if abs(f - 1) <= 0.25 else "replace"
    v = cur if cc == "confirmed" else cur * f
    emit(c, v, cc, sid, round(sv, 2), "US$ per ha per year (total production cost)", 2025, F25,
         flat + unit_txt + "SEPSA/MAG national cost model, %s; 2025 USD x %.6f = %.1f real 2024 US$ per ha per year, compared with FixedCost + VariableCost = %.1f + %.1f = %.1f (ratio %.3f). The source gives no fixed/variable split; %s" %
         (note, F25, s24, fixed, var, tot, f, "both rows keep their current values." if cc == "confirmed" else "both rows are scaled by %.4f, keeping the model's split." % f))

# ---------------------------------------------------------------- checks and write
assert len(rows) == len(cells), (len(rows), len(cells))
COLS = ["country", "model", "sheet", "tech", "tech_name", "parameter", "unit_introduced", "unit", "projection_mode",
        "year", "current_value", "proposed_value", "change_class", "source_ids", "source_value", "source_unit",
        "source_currency_year", "cpi_factor", "derivation", "assumption_sentence", "ao_row_at_b51f24b"]
with open(os.path.join(CC_DIR, "proposals_CR.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)

S = "downloads/CR/"
SOURCES = [
    ("CR-001", "https://repositorio.cepal.org/server/api/core/bitstreams/7cd64039-a9c3-443d-a4f7-dbbae16756b8/content (record https://hdl.handle.net/11362/48538)",
     "Estudio de impacto economico de las inversiones y el financiamiento para el recambio de flota de autobuses sostenibles en Costa Rica (Adamson and Cipoletta Tomassian), LC/TS.2022/183",
     "Comision Economica para America Latina y el Caribe (CEPAL)", "2022-12", S + "S2200597_es.pdf",
     "PDF p. 57 (BYD K9G e-bus USD 400,000) and Cuadro 7 p. 58; PDF p. 110 (diesel interurban bus ARESEP ceiling CRC 74,087,835 = USD 127,500 at 581.02 CRC/USD); Cuadro A18 PDF p. 204 (45,000 km per year plus 10 percent unproductive)",
     "National data: prices used in the ARESEP-based tariff and TCO analysis for Costa Rica concession buses. Currency year taken as 2020 (data year of the study; exchange rate as stated)."),
    ("CR-002", "https://repositorio.cepal.org/server/api/core/bitstreams/d502fce1-3c41-43f7-8bc8-c6b007fc6f11/content",
     "Transicion hacia la electromovilidad publica en Costa Rica: insumos y propuestas, LC/TS.2024/70",
     "Comision Economica para America Latina y el Caribe (CEPAL)", "2024-09", S + "CEPAL_2024_LCTS2024-70_electromovilidad_publica_CR.pdf",
     "PDF p. 83, table of assumptions: legal service life of a bus 15 years (Consejo de Transporte Publico); 60,000 km per year urban buses",
     "Also Cuadro 42 (PDF p. 111): compiled e-bus and diesel bus prices, context only."),
    ("CR-003", "https://observador.cr/vehiculos-revisados-en-costa-rica-tienen-antiguedad-de-16-anos-en-promedio/",
     "Vehiculos revisados en Costa Rica tienen antiguedad de 16 anos en promedio", "El Observador CR (data from Riteve SyC)", "2020-06-18",
     S + "observador_vehiculos_revisados_antiguedad_16_anos.html", "article text",
     "Average age of vehicles inspected in 2019 about 16 years; trailers and semi-trailers 27 years; route and tourism buses about 8 years; newly registered vehicles 2.5 years (used imports about 8 years). Comparison for OperationalLife."),
    ("CR-004", "https://infoagro.go.cr/wp-content/uploads/2025/08/CAFE_MaduracionMedia_2025.pdf", "Modelo de costos para el cultivo de cafe, zonas de maduracion media, Costa Rica (update June 2025)",
     "Secretaria Ejecutiva de Planificacion Sectorial Agropecuaria (SEPSA), MAG, with ICAFE", "2025-06", S + "CAFE_MaduracionMedia_2025.pdf",
     "COSTO TOTAL DE PRODUCCION per year, years 0 to 20 (PDF pp. 4 to 25)", "US$ at 508.28 CRC/USD (30 June 2025). Year 0 6,277.2; years 1 to 20 1,970.4 to 4,896.9 US$ per ha."),
    ("CR-005", "https://infoagro.go.cr/wp-content/uploads/2025/08/ARROZ_SECANO_NACIONAL_2025.pdf", "Modelo de costos arroz secano, nacional (update June 2025)",
     "SEPSA, MAG", "2025-06", S + "ARROZ_SECANO_NACIONAL_2025.pdf", "Resumen de costos por hectarea, PDF p. 5", "Costos totales por hectarea US$ 3,413.5 (CRC 1,735,026.8) at 508.28 CRC/USD."),
    ("CR-006", "https://infoagro.go.cr/wp-content/uploads/2025/08/ARROZ_RIEGO_NACIONAL_2025.pdf", "Modelo de costos arroz riego, nacional (update June 2025)",
     "SEPSA, MAG, with INTA", "2025-06", S + "ARROZ_RIEGO_NACIONAL_2025.pdf", "Resumen de costos por hectarea, PDF p. 6", "Costos totales por hectarea US$ 3,239.6 (CRC 1,646,639.6) at 508.28 CRC/USD."),
    ("CR-007", "https://infoagro.go.cr/wp-content/uploads/2025/06/PINA_HuetarNorte_2025.pdf", "Modelo de costos de produccion de pina, Region Huetar Norte 2025",
     "SEPSA, MAG", "2025-06", S + "PINA_HuetarNorte_2025.pdf", "Resumen, PDF p. 6", "Year 1 US$ 27,259; year 2 US$ 11,429.5; annual mean US$ 19,344.3 per ha at 505.28 CRC/USD."),
    ("CR-008", "https://infoagro.go.cr/wp-content/uploads/2025/06/NARANJA_Chorotega_2025.pdf", "Modelo de costos de produccion de naranja dulce, Region Chorotega (update June 2025)",
     "SEPSA, MAG", "2025-06", S + "NARANJA_Chorotega_2025.pdf", "COSTO TOTAL per year and resumen, PDF pp. 2 to 15", "Year 0 US$ 6,505.3; years 1 to 10 US$ 2,527.6 to 4,206.2 per ha at 512.02 CRC/USD."),
    ("CR-009", "https://infoagro.go.cr/wp-content/uploads/2025/10/Palma_Aceitera_BruncaPacificoCentral_2025.pdf", "Modelo de costos para el cultivo de palma aceitera, Regiones Brunca y Pacifico Central (update April 2025)",
     "SEPSA, MAG", "2025-04", S + "Palma_Aceitera_BruncaPacificoCentral_2025.pdf", "Resumen de costos por hectarea anos 0 al 20, PDF pp. 25 to 27", "Year 0 US$ 3,570.3; years 1 to 20 US$ 989.3 to 2,382.0 per ha at 508.21 CRC/USD."),
    ("CR-010", "https://infoagro.go.cr/wp-content/uploads/2025/05/MAIZ_Chorotega_2025.pdf", "Modelo de costos de produccion de maiz, Region Chorotega (update May 2025)",
     "SEPSA, MAG", "2025-05", S + "MAIZ_Chorotega_2025.pdf", "COSTO TOTAL DE PRODUCCION and resumen, PDF p. 4", "US$ 1,682.8 per ha per cycle (CRC 856,618.2) at 509.05 CRC/USD; yield 3.0 t per ha."),
    ("CR-011", "https://infoagro.go.cr/wp-content/uploads/2025/07/CEBOLLA_CentralOriental_2025.pdf", "Modelo de costos de produccion de cebolla, Region Central Oriental 2025",
     "SEPSA, MAG", "2025-06", S + "CEBOLLA_CentralOriental_2025.pdf", "Resumen costos produccion cebolla, PDF p. 6", "Seedbed US$ 2,959.7 plus field US$ 15,563.4 per ha at 508.28 CRC/USD."),
    ("CR-012", "https://infoagro.go.cr/wp-content/uploads/2026/05/BANANO_CRIOLLO_HuetarCaribe_2026.pdf", "Modelo de costos de produccion de banano criollo, Region Huetar Caribe 2026",
     "SEPSA, MAG", "2026-05", S + "BANANO_CRIOLLO_HuetarCaribe_2026.pdf", "Resumen, PDF p. 7", "Initial investment US$ 3,709.1; annual mean years 1 and 2 US$ 4,787.7 per ha at 457.64 CRC/USD (2026 USD). Smallholder banana, comparison only."),
    ("CR-013", "https://infoagro.go.cr/wp-content/uploads/2025/03/TOMATE_CentralOccidental_veranera_2025.pdf", "Modelo de costos de produccion de tomate en campo, siembra veranera, Region Central Occidental 2025",
     "SEPSA, MAG", "2025-01", S + "TOMATE_CentralOccidental_veranera_2025.pdf", "Resumen costos tomate, PDF p. 6", "US$ 46,327.3 per ha at 504.27 CRC/USD; yield 51.2 t per ha. Upper end for other vegetables, comparison only."),
]
with open(os.path.join(CC_DIR, "sources_CR.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "url", "title", "publisher", "date", "retrieval_date", "downloaded_file", "page_or_table", "notes"])
    for s in SOURCES:
        w.writerow([s[0], s[1], s[2], s[3], s[4], RETR, s[5], s[6], s[7]])

print("rows", len(rows))
from collections import Counter
print(Counter(r["change_class"] for r in rows))
