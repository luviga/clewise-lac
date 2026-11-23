"""Build proposals_GUA.csv from cells_GUA.csv, the GEN packages and the GUA sources.

Run: python -I build_proposals_GUA.py (paths are relative to this file).
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CC_DIR = os.path.dirname(HERE)
JOB = os.path.dirname(CC_DIR)

CPI = {}
with open(os.path.join(JOB, "cpi_u.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        CPI[int(r["year"])] = float(r["factor_to_2024"])
F20 = CPI[2020]

# ---------------- GEN vehicle package ----------------
GV = {}
TRAJ = {}
with open(os.path.join(JOB, "GEN", "gen_vehicle_factors.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["item"] == "price_trajectory":
            TRAJ[(r["vehicle_class"], r["powertrain"], int(float(r["year"])))] = float(r["value"])
        elif r["item"] == "reference_price" and r["source_id"] == "GEN-101":
            GV[("price", r["vehicle_class"], r["powertrain"])] = (float(r["value"]), float(r["value_2024usd"]))
        elif r["item"] == "maintenance_cost" and r["unit"] == "M US$ per Gvkm":
            GV[("maint", r["vehicle_class"], r["powertrain"])] = (float(r["value"]), float(r["value_2024usd"]))


def atb(cls, pt):
    return GV[("price", cls, pt)]


# ---------------- UN Comtrade, Guatemala imports (GUA-001 for 2024) ----------------
CT = {}
with open(os.path.join(JOB, "downloads", "GUA", "comtrade_GUA_imports_vehicles_2024.json"), encoding="utf-8") as f:
    for r in json.load(f)["data"]:
        CT[r["cmdCode"]] = (r["qty"] or 0.0, r["cifvalue"] or 0.0)


def ct_unit(codes):
    q = sum(CT[c][0] for c in codes if c in CT and CT[c][0] > 0)
    v = sum(CT[c][1] for c in codes if c in CT and CT[c][0] > 0)
    return v / q, q


def ct_note(codes, label):
    uv, q = ct_unit(codes)
    return (" Comparison: UN Comtrade puts Guatemala's 2024 imports of %s (HS %s) at %s US$ CIF per unit on %s units (GUA-001; partner-based estimate, CIF before Guatemalan duties, taxes and margins, new and used vehicles together)."
            % (label, ", ".join(codes), format(round(uv), ","), format(round(q), ",")))


# National anchors published for the region (GEN-104, 2020 USD)
BUS_ELE = 360000 * F20
TRK_ELE = 120000 * F20
MOT_ELE = 3000 * F20
R_C8_DSL_ELE = atb("heavy_freight", "DSL")[0] / atb("heavy_freight", "ELE")[0]
BUS_DSL = BUS_ELE * R_C8_DSL_ELE
TRK_DSL = TRK_ELE * R_C8_DSL_ELE

GROUP = {"TRAUT": "Techs_Auto", "TRBPR": "Techs_Buses_Pri", "TRBPU": "Techs_Buses_Pub", "TRMBS": "Techs_Buses_Micro",
         "TRMOT": "Techs_Motos", "TRYLF": "Techs_Li_Freight", "TRYTK": "Techs_He_Freight"}
CLASS = {"TRAUT": "car", "TRBPR": "bus", "TRBPU": "bus", "TRMBS": "minibus", "TRMOT": "motorcycle",
         "TRYLF": "light_freight", "TRYTK": "heavy_freight"}
KM_CUR = {"Techs_Auto": 19220, "Techs_Buses_Pri": 50400, "Techs_Buses_Pub": 50400, "Techs_Buses_Micro": 50400,
          "Techs_Motos": 9390, "Techs_Li_Freight": 20600, "Techs_He_Freight": 50400}


def split(tech):
    for p in sorted(GROUP, key=len, reverse=True):
        if tech.startswith(p):
            return p, tech[len(p):]
    raise KeyError(tech)


with open(os.path.join(CC_DIR, "cells_GUA.csv"), encoding="utf-8") as f:
    CELLS = list(csv.DictReader(f))
CUR = {(c["model"], c["tech"], c["parameter"], c["year"]): c for c in CELLS}


def base_cell(tech):
    """Base-year CapitalCost cell of a vehicle (2018)."""
    return CUR[("GUA_ENERGY", tech, "CapitalCost", "2018")]


def classify(cur, src, tol=0.25):
    if cur == 0:
        return "replace" if src != 0 else "confirmed"
    return "replace" if abs(src - cur) / abs(cur) > tol else "confirmed"


def fmt(x):
    if isinstance(x, str):
        return x
    if abs(x) >= 100:
        return "%.2f" % x
    return "%.6g" % x


# ---------------- base-year price specs ----------------
# kind 'price': value in US$ per vehicle (2024 USD); kind 'ratio': price of this vehicle (num) over the written
# base-year cell of ref (resolved after the reference row is classified).
def atb_price(cls, pt, label, extra=""):
    v20, v24 = atb(cls, pt)
    return dict(kind="price", value=v24, sources="GEN-101;GEN-001", sv=str(v20),
                su="US$ per vehicle (US purchase price, ATB 2022 Mid, 2024 model year)", cy="2020", cpi=F20,
                der="GEN reference_price %s %s: NREL ATB 2022 Mid %s, %s US$ (2020 USD) x CPI factor %.6f = %.2f US$ (2024 USD). No published Guatemalan price for this class and powertrain could be downloaded; US prices exclude Guatemalan import duties and taxes.%s"
                    % (cls, pt, label, format(v20, ","), F20, v24, extra))


def ratio(num, num_txt, ref, sources, sv, extra=""):
    return dict(kind="ratio", num=num, num_txt=num_txt, ref=ref, sources=sources, sv=sv, extra=extra)


SPEC = {}
SPEC["TRAUTDSL"] = atb_price("car", "DSL", "Compact car Conventional CI", ct_note(["870331", "870332", "870333"], "diesel cars"))
SPEC["TRAUTGSL"] = atb_price("car", "GSL", "Compact car Conventional SI", ct_note(["870321", "870322", "870323", "870324"], "gasoline cars"))
SPEC["TRAUTFlex_Fuel"] = atb_price("car", "Flex_Fuel", "Compact car Conventional SI (GEN proxy for flex fuel)")
SPEC["TRAUTELE"] = ratio(atb("car", "ELE")[1], "ATB 2022 Mid compact car BEV300, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (format(atb("car", "ELE")[0], ","), F20, atb("car", "ELE")[1]),
                         "TRAUTDSL", "GEN-101;GEN-001;GUA-001", "%s" % atb("car", "ELE")[0], ct_note(["870380"], "battery electric cars"))
SPEC["TRAUTLPG"] = ratio(atb("car", "LPG")[1], "ATB 2022 Mid compact car gasoline (GEN proxy for LPG), %.2f US$ (2024 USD)" % atb("car", "LPG")[1],
                         "TRAUTDSL", "GEN-101;GEN-001", "%s" % atb("car", "LPG")[0])
SPEC["TRAUTHG"] = ratio(atb("car", "HG")[1], "ATB 2022 Mid compact car power-split hybrid, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (format(atb("car", "HG")[0], ","), F20, atb("car", "HG")[1]),
                        "TRAUTELE", "GEN-101;GEN-001;GUA-001", "%s" % atb("car", "HG")[0], ct_note(["870340"], "gasoline hybrid cars"))
SPEC["TRAUTPHG"] = ratio(atb("car", "PHG")[1], "ATB 2022 Mid compact car PHEV50, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (format(atb("car", "PHG")[0], ","), F20, atb("car", "PHG")[1]),
                         "TRAUTELE", "GEN-101;GEN-001;GUA-001", "%s" % atb("car", "PHG")[0], ct_note(["870360"], "gasoline plug-in hybrid cars"))
# Light freight (ATB pickup)
SPEC["TRYLFDSL"] = atb_price("light_freight", "DSL", "Pickup Conventional CI", ct_note(["870421"], "diesel goods vehicles up to 5 t"))
SPEC["TRYLFGSL"] = atb_price("light_freight", "GSL", "Pickup Conventional SI", ct_note(["870431"], "gasoline goods vehicles up to 5 t"))
for pt, lab in (("ELE", "Pickup BEV300"), ("HD", "Pickup hybrid (GEN proxy for diesel hybrid)"), ("LPG", "Pickup gasoline (GEN proxy for LPG)"), ("PHD", "Pickup PHEV50 (GEN proxy for diesel plug-in hybrid)")):
    v20, v24 = atb("light_freight", pt)
    SPEC["TRYLF" + pt] = ratio(v24, "ATB 2022 Mid %s, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (lab, format(v20, ","), F20, v24), "TRYLFDSL", "GEN-101;GEN-001", "%s" % v20)
# Microbuses (ATB Class 4 step van, GEN mapping)
SPEC["TRMBSDSL"] = atb_price("minibus", "DSL", "Class 4 step van diesel (GEN proxy for microbus)")
SPEC["TRMBSGSL"] = atb_price("minibus", "GSL", "Class 4 step van, diesel price (GEN proxy for gasoline microbus)")
for pt, lab in (("ELE", "Class 4 step van BEV"), ("HYD", "Class 4 step van fuel cell"), ("LPG", "Class 4 step van diesel (GEN proxy for LPG)"), ("PHD", "Class 4 step van diesel plug-in hybrid")):
    v20, v24 = atb("minibus", pt)
    SPEC["TRMBS" + pt] = ratio(v24, "ATB 2022 Mid %s, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (lab, format(v20, ","), F20, v24), "TRMBSDSL", "GEN-101;GEN-001", "%s" % v20)
# Buses: regional electric bus price (GEN-104) with ATB Class 8 powertrain ratios
for p in ("TRBPU", "TRBPR"):
    SPEC[p + "DSL"] = dict(kind="price", value=BUS_DSL, sources="GEN-104;GEN-101;GEN-001;GUA-001", sv="360000 x (160750 / 327750)", su="US$ per vehicle", cy="2020", cpi=F20,
                           der="Electric bus price USD 360,000 in the Dominican Republic national electric mobility plan (GEN-104, PDF p. 94, Tabla 6 footnote 29; the only published Central American and Caribbean bus price in the GEN package) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101; ATB has no bus, Class 8 is the GEN heavy-duty proxy) = %.2f US$ (2024 USD).%s"
                               % (F20, BUS_ELE, R_C8_DSL_ELE, BUS_DSL, ct_note(["870210"], "diesel buses for ten or more persons")))
    SPEC[p + "ELE"] = ratio(BUS_ELE, "electric bus USD 360,000 (GEN-104) x %.6f = %.2f US$ (2024 USD)" % (F20, BUS_ELE), p + "DSL", "GEN-104;GEN-101;GEN-001;GUA-001", "360000", ct_note(["870240"], "electric buses"))
    SPEC[p + "HYD"] = ratio(BUS_DSL * atb("heavy_freight", "HYD")[0] / atb("heavy_freight", "DSL")[0], "diesel bus price %.2f x ATB Class 8 fuel cell to diesel ratio 292,000 / 160,750" % BUS_DSL, p + "DSL", "GEN-104;GEN-101;GEN-001", "292000 / 160750")
    SPEC[p + "PHD"] = ratio(BUS_DSL * atb("heavy_freight", "PHD")[0] / atb("heavy_freight", "DSL")[0], "diesel bus price %.2f x ATB Class 8 diesel plug-in hybrid to diesel ratio 254,500 / 160,750" % BUS_DSL, p + "DSL", "GEN-104;GEN-101;GEN-001", "254500 / 160750")
    SPEC[p + "LPG"] = ratio(BUS_DSL, "diesel bus price %.2f (GEN proxy for LPG)" % BUS_DSL, p + "DSL", "GEN-104;GEN-101;GEN-001", "160750 / 160750")
# Heavy freight: regional electric cargo vehicle price (GEN-104) with ATB Class 8 ratios
SPEC["TRYTKDSL"] = dict(kind="price", value=TRK_DSL, sources="GEN-104;GEN-101;GEN-001;GUA-001", sv="120000 x (160750 / 327750)", su="US$ per vehicle", cy="2020", cpi=F20,
                        der="Electric cargo vehicle price USD 120,000 in the Dominican Republic national electric mobility plan (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101) = %.2f US$ (2024 USD). The ATB Class 8 diesel itself (194,835 US$, a US long-haul tractor) is not used as the price, because it sits far above the trucks sold in Central America.%s"
                            % (F20, TRK_ELE, R_C8_DSL_ELE, TRK_DSL, ct_note(["870422", "870423"], "diesel goods vehicles above 5 t")))
SPEC["TRYTKELE"] = ratio(TRK_ELE, "electric cargo vehicle USD 120,000 (GEN-104) x %.6f = %.2f US$ (2024 USD)" % (F20, TRK_ELE), "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "120000")
SPEC["TRYTKHD"] = ratio(TRK_DSL * atb("heavy_freight", "HD")[0] / atb("heavy_freight", "DSL")[0], "diesel truck price %.2f x ATB Class 8 diesel hybrid to diesel ratio 172,750 / 160,750" % TRK_DSL, "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "172750 / 160750")
SPEC["TRYTKHYD"] = ratio(TRK_DSL * atb("heavy_freight", "HYD")[0] / atb("heavy_freight", "DSL")[0], "diesel truck price %.2f x ATB Class 8 fuel cell to diesel ratio 292,000 / 160,750" % TRK_DSL, "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "292000 / 160750")
SPEC["TRYTKPHD"] = ratio(TRK_DSL * atb("heavy_freight", "PHD")[0] / atb("heavy_freight", "DSL")[0], "diesel truck price %.2f x ATB Class 8 diesel plug-in hybrid to diesel ratio 254,500 / 160,750" % TRK_DSL, "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "254500 / 160750")
SPEC["TRYTKLPG"] = ratio(TRK_DSL, "diesel truck price %.2f (GEN proxy for LPG)" % TRK_DSL, "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "160750 / 160750")
# Motorcycles
MOT_UV, MOT_Q = ct_unit(["871120"])
SPEC["TRMOTGSL"] = dict(kind="price", value=MOT_UV, sources="GUA-001;GEN-001", sv="406827868.0 / 165857.41", su="US$ CIF per unit (imports of motorcycles 50 to 250 cc, HS 871120)", cy="2024", cpi=1.0,
                        der="UN Comtrade, Guatemala imports 2024, HS 871120 (motorcycles with engines of 50 to 250 cc, the commuter class that dominates the fleet): CIF value 406,827,868 US$ / 165,857.41 units = %.2f US$ per unit (2024 USD, CPI factor 1.000000). A partner-based estimate, CIF before duties, taxes and dealer margin, so the retail price is somewhat higher; the 2018 figure was 2,354 US$ (GUA-002, 169,493,597 / 72,013.015, 2,940 US$ in 2024 USD)." % MOT_UV)
SPEC["TRMOTELE"] = dict(kind="price", value=MOT_ELE, sources="GEN-104;GEN-001;GUA-001", sv="3000", su="US$ per vehicle (electric motorcycle)", cy="2020", cpi=F20,
                        der="Electric motorcycle price USD 3,000 in the Dominican Republic national electric mobility plan (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD); no Guatemalan price is published.%s The HS 871160 line also holds low-power electric scooters, so it sits below a full electric motorcycle." % (F20, MOT_ELE, ct_note(["871160"], "electric motorcycles")))
SPEC["TRMOTFlex_Fuel"] = dict(kind="assumption", sentence="A flex-fuel motorcycle costs 3,666.21 US$ per vehicle in Guatemala in every year, about 30 percent above the gasoline motorcycle for an engine and fuel system that accept ethanol blends. UN Comtrade data put Guatemala's 2024 imports of 50 to 250 cc motorcycles at about 2,450 US$ CIF per unit before duties and margins; range 2,500 to 4,500 US$ per vehicle.")

TRAJ_KEY = {"TRAUTELE": ("car", "ELE"), "TRAUTHG": ("car", "HG"), "TRAUTPHG": ("car", "PHG"),
            "TRBPRELE": ("bus", "ELE"), "TRBPUELE": ("bus", "ELE"), "TRBPRHYD": ("bus", "HYD"), "TRBPUHYD": ("bus", "HYD"),
            "TRBPRPHD": ("bus", "PHD"), "TRBPUPHD": ("bus", "PHD"), "TRMBSELE": ("minibus", "ELE"), "TRMBSHYD": ("minibus", "HYD"),
            "TRMBSPHD": ("minibus", "PHD"), "TRYLFELE": ("light_freight", "ELE"), "TRYTKELE": ("heavy_freight", "ELE"),
            "TRYTKHYD": ("heavy_freight", "HYD")}

# ---------------- resolve base-year cells (prices first, then ratios in chain order) ----------------
WRITTEN = {}   # tech -> written base-year cell
BASE = {}      # tech -> dict(proposed, cls, sources, sv, su, cy, cpi, der, sourced_price)


def resolve(tech):
    if tech in BASE:
        return
    spec = SPEC[tech]
    c = base_cell(tech)
    cur = float(c["current_value"])
    if spec["kind"] == "assumption":
        BASE[tech] = dict(cls="assumption", proposed=cur)
        WRITTEN[tech] = cur
        return
    if spec["kind"] == "price":
        val = spec["value"]
        cls = classify(cur, val)
        BASE[tech] = dict(cls=cls, val=val, sources=spec["sources"], sv=spec["sv"], su=spec["su"], cy=spec["cy"], cpi=spec["cpi"],
                          der=spec["der"], price=val)
        WRITTEN[tech] = cur if cls == "confirmed" else val
        return
    ref = spec["ref"]
    resolve(ref)
    ref_raw = WRITTEN[ref]
    val = spec["num"] / ref_raw
    cls = classify(cur, val)
    ref_is_ratio = SPEC[ref]["kind"] == "ratio"
    if ref_is_ratio:
        der = ("Chained reference: this row is 'Relative to %s' and %s is itself 'Relative to %s', so the compiler multiplies this cell by the RAW base-year cell of %s, which holds a ratio (%s), not a price. "
               "The cell is therefore set so that the compiled base-year price equals the sourced price: sourced price %.2f US$ (%s) / raw %s cell %s = %s. "
               "If the %s cell is written with another value, this cell must be recomputed; the chain is raised as a decision (make the row relative to %s or enter it in US$ per vehicle)."
               % (ref, ref, SPEC[ref]["ref"], ref, fmt(ref_raw), spec["num"], spec["num_txt"], ref, fmt(ref_raw), fmt(val), ref, SPEC[ref]["ref"]))
    else:
        der = ("Ratio the compiler expects: this vehicle's price (%s) divided by the raw base-year cell of %s as written (%s US$, %s) = %.2f / %s = %s; the compiler multiplies them."
               % (spec["num_txt"], ref, fmt(ref_raw), "its proposed value" if BASE[ref]["cls"] == "replace" else "its current value, confirmed", spec["num"], fmt(ref_raw), fmt(val)))
        if cls == "confirmed" and BASE[ref]["cls"] == "replace":
            der += (" The ratio is confirmed, but the compiled base-year price moves from %.2f to %.2f US$ because the reference price changes."
                    % (cur * float(base_cell(ref)["current_value"]), cur * ref_raw))
    BASE[tech] = dict(cls=cls, val=val, sources=spec["sources"], sv=spec["sv"], su="ratio of prices in 2024 USD" if not ref_is_ratio else "price / raw reference cell",
                      cy="2020" if "GEN-001" in spec["sources"] else "", cpi=F20 if "GEN-001" in spec["sources"] else "", der=der + spec.get("extra", ""), price=spec["num"])
    WRITTEN[tech] = cur if cls == "confirmed" else val


for t in SPEC:
    resolve(t)

ROWS = []


def out(c, proposed, cls, sources="", sv="", su="", cy="", cpi="", der="", sent=""):
    ROWS.append({
        "country": c["country"], "model": c["model"], "sheet": c["sheet"], "tech": c["tech"], "tech_name": c["tech_name"],
        "parameter": c["parameter"], "unit_introduced": c["unit_introduced"], "unit": c["unit"], "projection_mode": c["projection_mode"],
        "year": c["year"], "current_value": c["current_value"], "proposed_value": proposed if isinstance(proposed, str) else fmt(proposed),
        "change_class": cls, "source_ids": sources, "source_value": sv, "source_unit": su, "source_currency_year": cy,
        "cpi_factor": ("%.6f" % cpi) if isinstance(cpi, float) else cpi, "derivation": der, "assumption_sentence": sent,
        "ao_row_at_b51f24b": c["ao_row_at_b51f24b"]})


def sourced(c, val, s, der, cur=None):
    cur = float(c["current_value"]) if cur is None else cur
    cls = classify(cur, val)
    prop = c["current_value"] if cls == "confirmed" else val
    d = der + (" Sourced value %s against current %s: %s." % (fmt(val), c["current_value"], "within 25 percent, current value kept" if cls == "confirmed" else "differs by more than 25 percent, sourced value proposed"))
    out(c, prop, cls, s["sources"], s["sv"], s["su"], s["cy"], s["cpi"], d)


LIFE = {"car": (15, "GEN-103"), "light_freight": (15, "GEN-103"), "minibus": (15, "GEN-103"),
        "bus": (10, "GEN-104"), "heavy_freight": (10, "GEN-104"), "motorcycle": (10, "GEN-104")}
LIFE_DER = {15: "GEN operational_life for this class: 15 years (NREL ATB 2022 light-duty and Class 4 vehicle life, GEN-103). No Guatemalan scrappage or fleet-age series is published in a downloadable form.",
            10: "GEN operational_life for this class: 10 years, the theoretical vehicle life of the Dominican Republic national electric mobility plan (GEN-104, PDF p. 78, footnote 11), the only regional published value in the GEN package. No Guatemalan scrappage or fleet-age series is published in a downloadable form; Guatemalan buses and trucks are often imported used and run longer (see the report decision on heavy-vehicle lives)."}
KM = {"Techs_Auto": (19108, "GEN-103", "km per vehicle per year (US light-duty vehicles, ATB)", "NREL ATB 2022 light-duty annual distance, 19,108 km (GEN-103, LCOD methodology text)"),
      "Techs_Li_Freight": (19108, "GEN-103", "km per vehicle per year (US light-duty vehicles incl. pickups, ATB)", "NREL ATB 2022 light-duty annual distance (pickups are light duty in ATB), 19,108 km (GEN-103)"),
      "Techs_Buses_Pub": (44000, "GEN-104", "km per vehicle per year (buses)", "Bus use intensity in the Dominican Republic national electric mobility plan, 44,000 km per year (GEN-104, PDF p. 78, Tabla 4)"),
      "Techs_Buses_Pri": (44000, "GEN-104", "km per vehicle per year (buses)", "Bus use intensity in the Dominican Republic national electric mobility plan, 44,000 km per year (GEN-104, PDF p. 78, Tabla 4)"),
      "Techs_Buses_Micro": (44000, "GEN-104", "km per vehicle per year (buses)", "Bus use intensity in the Dominican Republic national electric mobility plan, 44,000 km per year (GEN-104, PDF p. 78, Tabla 4); Guatemalan microbuses run collective routes like buses, so the bus figure is used rather than the ATB Class 4 delivery van (35,942 km)"),
      "Techs_Motos": (10500, "GEN-104", "km per vehicle per year (motorcycles)", "Motorcycle use intensity in the Dominican Republic national electric mobility plan, 10,500 km per year (GEN-104, PDF p. 78, Tabla 4)")}


def vehicle(c):
    tech, par, mode, cm = c["tech"], c["parameter"], c["projection_mode"], c["cell_meaning"]
    if par == "Ref.km.BY":
        if tech in KM:
            v, src, su, txt = KM[tech]
            s = dict(sources=src, sv=str(v), su=su, cy="", cpi="")
            sourced(c, float(v), s, txt + ". No Guatemalan odometer or inspection survey with distance per vehicle is published.")
        else:
            out(c, c["current_value"], "assumption", der="No published distance for heavy trucks in Guatemala or in the GEN package.",
                sent="A heavy truck in Guatemala runs 50,400 km per year in every year, about 170 km per working day over 300 days on regional and port freight routes. The Dominican Republic national electric mobility plan gives 9,000 km per year for all cargo vehicles, mostly light ones, and 44,000 km per year for buses; range 30,000 to 80,000 km per year.")
        return
    prefix, pt = split(tech)
    cls_name = CLASS[prefix]
    if par == "OperationalLife":
        v, src = LIFE[cls_name]
        sourced(c, float(v), dict(sources=src, sv=str(v), su="years", cy="", cpi=""), LIFE_DER[v])
        return
    if par == "FixedCost":
        if prefix == "TRMOT":
            sent = {"GSL": "Maintenance of a gasoline motorcycle costs 5.41 M US$ per Gvkm (0.0054 US$ per km, about 51 US$ per year at 9,390 km) in every year. No public cost series covers motorcycle maintenance in Central America; range 3 to 20 M US$ per Gvkm.",
                    "ELE": "Maintenance of an electric motorcycle costs 1.7853 M US$ per Gvkm (about 17 US$ per year at 9,390 km) in every year, a third of the gasoline motorcycle figure, in line with the lower maintenance of electric drivetrains; range 1 to 10 M US$ per Gvkm.",
                    "Flex_Fuel": "Maintenance of a flex-fuel motorcycle costs 7.033 M US$ per Gvkm (about 66 US$ per year at 9,390 km) in every year, 30 percent above the gasoline motorcycle for fuel-system upkeep with ethanol blends; range 4 to 25 M US$ per Gvkm."}[pt]
            out(c, c["current_value"], "assumption", der="No GEN maintenance value for motorcycles. Flat row: base-year cell only, every year takes it.", sent=sent)
            return
        v20, v24 = GV[("maint", cls_name, pt)]
        s = dict(sources="GEN-102;GEN-001", sv=str(v20), su="M US$ per Gvkm (ATB levelized maintenance and repair, US conditions)", cy="2020", cpi=F20)
        der = ("GEN maintenance_cost %s %s: %s M US$ per Gvkm (2020 USD) x CPI factor %.6f = %.3f (2024 USD). Flat row: base-year cell only, every year takes it.%s"
               % (cls_name, pt, v20, F20, v24, " Buses take the ATB Class 8 value (GEN heavy-duty proxy)." if cls_name == "bus" else ""))
        sourced(c, v24, s, der)
        return
    # CapitalCost
    if cm.startswith("base-year") or cm.startswith("ratio"):
        b = BASE[tech]
        if b["cls"] == "assumption":
            out(c, c["current_value"], "assumption", der="Flat row: base-year cell only, every year takes it. No published price for flex-fuel motorcycles.", sent=SPEC[tech]["sentence"])
            return
        tail = " Flat row: base-year cell only, every year takes it." if mode == "Flat" else " Base-year cell of a trajectory row: the compiled base-year price is a 2024 price and later year cells hold multipliers on it."
        tail += " Ref.km.BY of the group is unchanged, so the compiled M US$ per Gvkm moves with this cell only (1000 x price / km)."
        d = b["der"] + tail + (" Sourced value %s against current %s: %s." % (fmt(b["val"]), c["current_value"], "within 25 percent, current value kept" if b["cls"] == "confirmed" else "differs by more than 25 percent, sourced value proposed"))
        out(c, c["current_value"] if b["cls"] == "confirmed" else b["val"], b["cls"], b["sources"], b["sv"], b["su"], b["cy"], b["cpi"], d)
        return
    y = int(c["year"])
    fam = TRAJ_KEY[tech]
    if y < 2024:
        m = 1.0
        der = "Multiplier for %d: 1.0. The GEN price_trajectory (NREL ATB 2022 Mid, %s %s) is relative to the 2024 price and starts in 2024; the base-year cell gives a 2024 price, so years before 2024 take it unchanged." % (y, fam[0], fam[1])
    else:
        m = TRAJ[(fam[0], fam[1], y)]
        der = "GEN price_trajectory %s %s, year %d: ratio %.6f to the own 2024 price (NREL ATB 2022 Mid, interpolated between published years); applies because the base-year cell gives a 2024 price." % (fam[0], fam[1], y, m)
    if fam[0] == "bus":
        der += " ATB has no bus; Class 8 is the GEN heavy-duty proxy."
    if fam[0] == "minibus":
        der += " ATB Class 4 step van is the GEN proxy for microbuses."
    sourced(c, m, dict(sources="GEN-101", sv="%.6f" % m, su="ratio to 2024 price", cy="", cpi=""), der)


# ---------------- sector (GUA_WASTE) ----------------
CEPAL_COLL = 34.22 * CPI[2010] + 12.01 * CPI[2010]
CEPAL_DISP = 20.43 * CPI[2010]
WAW_OD_HIGH = 10 * CPI[2018]
PEN = {
    "contam_agua": "The water-contamination externality of uncontrolled waste disposal is 79.00 per unit of waste in 2018, falling to 57.82 in 2030 and 32.43 in 2050, in the model's money unit per unit of waste emission. It values damage to rivers, lakes and groundwater from open dumps in Guatemala and keeps a fixed proportion to the health (2.43 times) and tourism (3.64 times) externalities; range half to double.",
    "salud_residuos": "The public-health externality of uncontrolled waste disposal is 191.85 per unit of waste in 2018, falling to 140.43 in 2030 and 78.76 in 2050. It values illness linked to open dumps and waste burning in Guatemala, 2.43 times the water-contamination externality; range half to double.",
    "turismo_residuos": "The tourism externality of uncontrolled waste disposal is 287.77 per unit of waste in 2018, falling to 210.65 in 2030 and 118.13 in 2050. It values tourism revenue lost to littered lakes, rivers and dumps in Guatemala, 3.64 times the water-contamination externality; range half to double.",
}


def sector(c):
    tech, par = c["tech"], c["parameter"]
    cur = float(c["current_value"])
    if par == "EmissionsPenalty":
        out(c, c["current_value"], "assumption", der="Penalty per unit of emission in that year; the published origin cannot be downloaded (listed in manual_downloads_GUA.csv).", sent=PEN[tech])
        return
    flat = " Flat row: base-year cell only, every year takes it."
    if tech in ("BLEND_NO_DCOLL", "LANDFILL"):
        same = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == tech and x["year"] == c["year"]]
        tot_cur = sum(float(x["current_value"]) for x in same)
        if tech == "BLEND_NO_DCOLL":
            v, sv, lab, waw = CEPAL_COLL, "34.22 + 12.01", "collection (34.22) plus transfer (12.01) US$ per t, 2010 USD", "62 to 125"
        else:
            v, sv, lab, waw = CEPAL_DISP, "20.43", "final disposal 20.43 US$ per t, 2010 USD", "25 to 81"
        cls = classify(tot_cur, v)
        prop = c["current_value"] if cls == "confirmed" else v * cur / tot_cur
        d = ("CEPAL 2016, Cuadro 6 (Latin America and the Caribbean averages): %s x CPI factor %.6f = %.2f US$ per t (2024 USD). Compared with the model's CapitalCost + VariableCost = %.3f US$ per t (%s); if replaced, split in the model's own proportion (this cell's share %.4f). What a Waste 2.0 (GEN-204, Table 5.2) gives %s US$ per t for upper-middle income countries such as Guatemala (2024 USD)."
             % (lab, CPI[2010], v, tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur, waw)) + flat
        out(c, prop, cls, "GEN-206;GEN-204;GEN-001", sv, "US$ per t", "2010", CPI[2010], d)
        return
    if tech == "NO_CONTR_OD":
        s = dict(sources="GEN-204;GEN-001", sv="10", su="US$ per t (open dumping, top of the lower-middle income range 3 to 10)", cy="2018", cpi=CPI[2018])
        sourced(c, WAW_OD_HIGH, s, "What a Waste 2.0, Table 5.2, p. 105: open dumping 3 to 10 US$ per t for lower-middle income countries, not given for upper-middle income; the top of the range is used for Guatemala (upper-middle income): 10 x CPI factor %.6f = %.2f US$ per t (2024 USD)." % (CPI[2018], WAW_OD_HIGH) + flat)
        return
    raise KeyError((tech, par))


for c in CELLS:
    if c["model"] == "GUA_ENERGY":
        vehicle(c)
    else:
        sector(c)

# Row-level coherence: if any multiplier cell of a trajectory row is replaced, the whole GEN series is proposed.
MULT = "multiplier on the base-year value"
meaning = {(c["model"], c["tech"], c["parameter"], c["year"]): c["cell_meaning"] for c in CELLS}
rows_with_replace = {(r["model"], r["tech"], r["parameter"]) for r in ROWS
                     if meaning[(r["model"], r["tech"], r["parameter"], r["year"])] == MULT and r["change_class"] == "replace"}
for r in ROWS:
    key = (r["model"], r["tech"], r["parameter"])
    if key in rows_with_replace and meaning[key + (r["year"],)] == MULT and r["change_class"] == "confirmed":
        r["proposed_value"] = fmt(float(r["source_value"]))
        r["change_class"] = "replace"
        r["derivation"] = r["derivation"].replace(
            "within 25 percent, current value kept",
            "within 25 percent, but other multiplier cells of this row differ by more than 25 percent, so the whole GEN series is proposed for the row to keep the price path coherent (row-level replacement)")

COLS = ["country", "model", "sheet", "tech", "tech_name", "parameter", "unit_introduced", "unit", "projection_mode", "year", "current_value",
        "proposed_value", "change_class", "source_ids", "source_value", "source_unit", "source_currency_year", "cpi_factor", "derivation",
        "assumption_sentence", "ao_row_at_b51f24b"]
with open(os.path.join(CC_DIR, "proposals_GUA.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(ROWS)
print(len(CELLS), len(ROWS))

# ---------------- summary for the report (printed only) ----------------
from collections import Counter
print("cells by class", Counter(r["change_class"] for r in ROWS))
print("pairs by class", Counter(v for v in {(r["model"], r["tech"], r["parameter"]): r["change_class"] for r in ROWS if r["change_class"] != "replace"}.values()),
      "replace pairs", len({(r["model"], r["tech"], r["parameter"]) for r in ROWS if r["change_class"] == "replace"}))


def eff_price(tech, cells):
    unit = base_cell(tech)["unit_introduced"]
    v = cells[tech]
    if unit.startswith("Relative to "):
        ref = unit[len("Relative to "):]
        return v * cells[ref]
    return v


cur_cells = {t: float(base_cell(t)["current_value"]) for t in SPEC}
new_cells = {t: WRITTEN[t] for t in SPEC}
chg = []
for t in SPEC:
    prefix, _ = split(t)
    km = KM_CUR[GROUP[prefix]]
    pc, pn = eff_price(t, cur_cells), eff_price(t, new_cells)
    chg.append((abs(1000 * (pn - pc) / km), t, pc, pn, 1000 * pc / km, 1000 * pn / km, BASE[t]["cls"]))
for x in sorted(chg, reverse=True):
    print("%-16s %-10s price %12.2f -> %12.2f  M US$/Gvkm %10.4f -> %10.4f" % (x[1], x[6], x[2], x[3], x[4], x[5]))
fc = [(abs(float(r["proposed_value"]) - float(r["current_value"])), r["tech"], r["current_value"], r["proposed_value"]) for r in ROWS
      if r["parameter"] == "FixedCost" and r["change_class"] == "replace"]
for x in sorted(fc, reverse=True)[:8]:
    print("FixedCost", x)
