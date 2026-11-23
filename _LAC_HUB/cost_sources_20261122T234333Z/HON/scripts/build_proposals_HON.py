"""Build proposals_HON.csv from cells_HON.csv, the GEN packages and the HON sources.

Run: python -I build_proposals_HON.py (paths are relative to this file).
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CC_DIR = os.path.dirname(HERE)
JOB = os.path.dirname(CC_DIR)

CPI = {}
with open(os.path.join(JOB, "cpi_u.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        CPI[int(r["year"])] = float(r["factor_to_2024"])

# World Bank WDI PA.NUS.FCRF, Honduras, lempiras per US$ (HON-004)
FX = {2016: 22.835018390426, 2023: 24.6016468236818}
MZ_PER_HA = 1.43  # HON-003: "Manzanas a hectareas se dividio entre 1.43" (INE, CAN 2024)
FAO_CPI = "per year 1.226992 (2019) to 1.029494 (2023), GEN-001"

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

F20 = CPI[2020]
# Regional anchors (GEN-104, Dominican Republic plan, 2020 USD)
CAR_CONV = 20001 * F20
CAR_ELE = 30000 * F20
BUS_ELE = 360000 * F20
TRK_ELE = 120000 * F20
MOT_ELE = 3000 * F20


def atb(cls, pt):
    return GV[("price", cls, pt)]


R_C8_DSL_ELE = atb("heavy_freight", "DSL")[0] / atb("heavy_freight", "ELE")[0]
R_C8_HYD_DSL = atb("heavy_freight", "HYD")[0] / atb("heavy_freight", "DSL")[0]
R_C8_HD_DSL = atb("heavy_freight", "HD")[0] / atb("heavy_freight", "DSL")[0]
R_CAR_DSL_GSL = atb("car", "DSL")[0] / atb("car", "GSL")[0]
R_CAR_HG_GSL = atb("car", "HG")[0] / atb("car", "GSL")[0]
BUS_DSL = BUS_ELE * R_C8_DSL_ELE
TRK_DSL = TRK_ELE * R_C8_DSL_ELE
CAR_DSL = CAR_CONV * R_CAR_DSL_GSL
CAR_HG = CAR_CONV * R_CAR_HG_GSL

REGIONAL = ("Honduras publishes no new-vehicle price by class and powertrain (customs data are reported to UN Comtrade only as partner estimates, and the national electric mobility strategy draft could not be downloaded); "
            "the Dominican Republic national electric mobility plan (GEN-104) is used as the nearest published regional price, a Central American and Caribbean import market with similar duties.")

GROUP = {"TRAUT": "Techs_Auto", "TRSUV": "Techs_SUV", "TRTAX": "Techs_Taxi", "TRYLF": "Techs_Li_Freight",
         "TRYTK": "Techs_He_Freight", "TRMBS": "Techs_Buses_Micro", "TRBPU": "Techs_Buses_Pub",
         "TRBTUR": "Techs_Buses_Tur", "TRMOT": "Techs_Motos"}
CLASS = {"TRAUT": "car", "TRSUV": "SUV", "TRTAX": "taxi", "TRYLF": "light_freight", "TRYTK": "heavy_freight",
         "TRMBS": "minibus", "TRBPU": "bus", "TRBTUR": "bus", "TRMOT": "motorcycle"}

# Distances (GEN annual_km, GEN-104 Tabla 4)
KM = {"Techs_Auto": (7500, "automobiles and jeeps"), "Techs_SUV": (7500, "automobiles and jeeps"),
      "Techs_Buses_Micro": (44000, "buses"), "Techs_Buses_Pub": (44000, "buses"), "Techs_Buses_Tur": (44000, "buses"),
      "Techs_He_Freight": (9000, "cargo vehicles"), "Techs_Li_Freight": (9000, "cargo vehicles"),
      "Techs_Motos": (10500, "motorcycles")}
KM_CUR = {"Techs_Buses_Pub": 26000, "Techs_Buses_Micro": 20000, "Techs_Buses_Tur": 7500, "Techs_Motos": 7327}
KM_NOTE = {g: " The proposed Ref.km.BY of this group changes from %s to %s km per vehicle per year, so the compiled M US$ per Gvkm changes with it (1000 x price / km)." % (format(v, ","), format(KM[g][0], ","))
           for g, v in KM_CUR.items()}


def split(tech):
    for p in sorted(GROUP, key=len, reverse=True):
        if tech.startswith(p):
            return p, tech[len(p):]
    raise KeyError(tech)


def fmt(x):
    if isinstance(x, str):
        return x
    if abs(x) >= 100:
        return "%.2f" % x
    return "%.6g" % x


def classify(cur, src, tol=0.25):
    if cur == 0:
        return "replace" if src != 0 else "confirmed"
    return "replace" if abs(src - cur) / abs(cur) > tol else "confirmed"


# ---- base prices (US$ per vehicle rows) ----
def atb_spec(cls, pt, label, proxy=""):
    v20, v24 = atb(cls, pt)
    return dict(value=v24, sources="GEN-101;GEN-001", sv=str(v20), su="US$ per vehicle (US purchase price, ATB 2022 Mid, 2024 model year)", cy="2020", cpi=F20,
                der="GEN reference_price %s %s: ATB 2022 Mid %s, %s US$ (2020 USD) x CPI factor %.6f = %.2f US$ (2024 USD).%s Neither Honduras nor the regional plan (GEN-104) publishes this class; US prices exclude Honduran import duties and taxes." % (cls, pt, label, v20, F20, v24, proxy))


PRICE = {}
PRICE["TRAUTGSL"] = dict(value=CAR_CONV, sources="GEN-104;GEN-001", sv="20001", su="US$ per vehicle (average new conventional vehicle, Dominican Republic)", cy="2020", cpi=F20,
                         der="Average price of a new conventional vehicle, USD 20,001 (GEN-104, PDF p. 72; plan dated 2020, currency year 2020) x CPI factor %.6f = %.2f US$ (2024 USD). %s" % (F20, CAR_CONV, REGIONAL))
PRICE["TRAUTDSL"] = dict(value=CAR_DSL, sources="GEN-104;GEN-101;GEN-001", sv="20001 x (28600 / 23120)", su="US$ per vehicle", cy="2020", cpi=F20,
                         der="Conventional vehicle price USD 20,001 (GEN-104, PDF p. 72) x CPI factor %.6f = %.2f, times the ATB 2022 Mid compact car diesel to gasoline price ratio 28,600 / 23,120 = %.5f (GEN-101) = %.2f US$ (2024 USD). %s" % (F20, CAR_CONV, R_CAR_DSL_GSL, CAR_DSL, REGIONAL))
for t in ("TRTAXGSL", "TRTAXLPG"):
    PRICE[t] = dict(PRICE["TRAUTGSL"])
    if t.endswith("LPG"):
        PRICE[t]["der"] += " LPG taxis are converted gasoline cars, so they take the gasoline price (GEN proxy rule)."
for t in ("TRAUTELE", "TRTAXELE"):
    PRICE[t] = dict(value=CAR_ELE, sources="GEN-104;GEN-001", sv="30000", su="US$ per vehicle (electric automobile)", cy="2020", cpi=F20,
                    der="Electric automobile price USD 30,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD). %s" % (F20, CAR_ELE, REGIONAL))
for pt, lab in (("DSL", "Small SUV Conventional CI"), ("GSL", "Small SUV Conventional SI")):
    PRICE["TRSUV" + pt] = atb_spec("SUV", pt, lab)
PRICE["TRYLFDSL"] = atb_spec("light_freight", "DSL", "Pickup Conventional CI")
PRICE["TRYLFGSL"] = atb_spec("light_freight", "GSL", "Pickup Conventional SI")
PRICE["TRMBSDSL"] = atb_spec("minibus", "DSL", "Class 4 StepVan diesel")
PRICE["TRMBSGSL"] = atb_spec("minibus", "GSL", "Class 4 StepVan", " Gasoline minibuses take the diesel price (GEN proxy rule).")
for p in ("TRBPU", "TRBTUR"):
    for pt in ("DSL", "GSL"):
        PRICE[p + pt] = dict(value=BUS_DSL, sources="GEN-104;GEN-101;GEN-001", sv="360000 x (160750 / 327750)", su="US$ per vehicle", cy="2020", cpi=F20,
                             der="Electric bus price USD 360,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101; ATB has no bus, Class 8 is the GEN heavy-duty proxy) = %.2f US$ (2024 USD).%s %s"
                             % (F20, BUS_ELE, R_C8_DSL_ELE, BUS_DSL, " Gasoline buses take the diesel price (GEN proxy rule)." if pt == "GSL" else "", REGIONAL))
PRICE["TRYTKDSL"] = dict(value=TRK_DSL, sources="GEN-104;GEN-101;GEN-001", sv="120000 x (160750 / 327750)", su="US$ per vehicle", cy="2020", cpi=F20,
                         der="Electric cargo vehicle price USD 120,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101) = %.2f US$ (2024 USD). %s" % (F20, TRK_ELE, R_C8_DSL_ELE, TRK_DSL, REGIONAL))
PRICE["TRMOTELE"] = dict(value=MOT_ELE, sources="GEN-104;GEN-001", sv="3000", su="US$ per vehicle (electric motorcycle)", cy="2020", cpi=F20,
                         der="Electric motorcycle price USD 3,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD). %s" % (F20, MOT_ELE, REGIONAL))
MOT_GSL_SENT = ("A new gasoline motorcycle of 100 to 150 cc costs 1,153.47 US$ per vehicle in Honduras in the base year, the typical commuter and mototaxi model; "
                "motorcycles are 45 percent of the 2.4 million vehicles registered in Honduras in 2021 according to the National Statistics Institute. "
                "The Dominican Republic electric mobility plan prices an electric motorcycle at USD 3,000 (2020), so the gasoline model is about 40 percent of the electric one; range 900 to 2,000 US$ per vehicle.")

# ---- ratio rows: target price (2024 USD) and its text ----
RATIO = {
    "TRAUTHG": (CAR_HG, "conventional vehicle price %.2f (GEN-104) x ATB hybrid to gasoline ratio 25,600 / 23,120" % CAR_CONV, "GEN-104;GEN-101;GEN-001"),
    "TRBPUELE": (BUS_ELE, "electric bus USD 360,000 (GEN-104) x CPI factor", "GEN-104;GEN-001"),
    "TRBTURELE": (BUS_ELE, "electric bus USD 360,000 (GEN-104) x CPI factor", "GEN-104;GEN-001"),
    "TRBPUHYD": (BUS_DSL * R_C8_HYD_DSL, "diesel bus price x ATB Class 8 FCEV to diesel ratio 292,000 / 160,750", "GEN-104;GEN-101;GEN-001"),
    "TRMBSELE": (atb("minibus", "ELE")[1], "ATB Class 4 StepVan BEV, 2024 USD", "GEN-101;GEN-001"),
    "TRSUVELE": (atb("SUV", "ELE")[1], "ATB Small SUV BEV300, 2024 USD", "GEN-101;GEN-001"),
    "TRYLFELE": (atb("light_freight", "ELE")[1], "ATB Pickup BEV300, 2024 USD", "GEN-101;GEN-001"),
    "TRYLFHD": (atb("light_freight", "HD")[1], "ATB Pickup hybrid, GEN proxy for HD, 2024 USD", "GEN-101;GEN-001"),
    "TRYTKELE": (TRK_ELE, "electric cargo vehicle USD 120,000 (GEN-104) x CPI factor", "GEN-104;GEN-001"),
    "TRYTKHD": (TRK_DSL * R_C8_HD_DSL, "diesel truck price x ATB Class 8 diesel hybrid to diesel ratio 172,750 / 160,750", "GEN-104;GEN-101;GEN-001"),
    "TRYTKHYD": (TRK_DSL * R_C8_HYD_DSL, "diesel truck price x ATB Class 8 FCEV to diesel ratio 292,000 / 160,750", "GEN-104;GEN-101;GEN-001"),
}

TRAJ_KEY = {"TRAUTELE": ("car", "ELE"), "TRAUTHG": ("car", "HG"), "TRTAXELE": ("taxi", "ELE"), "TRSUVELE": ("SUV", "ELE"),
            "TRYLFELE": ("light_freight", "ELE"), "TRYTKELE": ("heavy_freight", "ELE"), "TRYTKHYD": ("heavy_freight", "HYD"),
            "TRBPUELE": ("bus", "ELE"), "TRBTURELE": ("bus", "ELE"), "TRBPUHYD": ("bus", "HYD"), "TRMBSELE": ("minibus", "ELE")}

LIFE = {"car": (15, "GEN-103"), "taxi": (15, "GEN-103"), "SUV": (15, "GEN-103"), "light_freight": (15, "GEN-103"), "minibus": (15, "GEN-103"),
        "bus": (10, "GEN-104"), "heavy_freight": (10, "GEN-104"), "motorcycle": (10, "GEN-104")}
LIFE_DER = {15: "GEN operational_life for this class: 15 years (NREL ATB 2022 light-duty and Class 4 vehicle life, GEN-103). Honduras publishes no fleet-age or scrappage series (the INE fleet bulletin 2017-2021, HON-001, gives counts by type only); the Dominican Republic plan uses a theoretical 10-year life for the whole fleet (GEN-104, PDF p. 78, footnote 11).",
            10: "GEN operational_life for this class: 10 years, the theoretical vehicle life of the Dominican Republic electric mobility plan (GEN-104, PDF p. 78, footnote 11). Honduras publishes no fleet-age or scrappage series (the INE fleet bulletin 2017-2021, HON-001, gives counts by type only)."}

ROWS = []
with open(os.path.join(CC_DIR, "cells_HON.csv"), encoding="utf-8") as f:
    CELLS = list(csv.DictReader(f))


def out(c, proposed, cls, sources="", sv="", su="", cy="", cpi="", der="", sent=""):
    ROWS.append({
        "country": c["country"], "model": c["model"], "sheet": c["sheet"], "tech": c["tech"], "tech_name": c["tech_name"],
        "parameter": c["parameter"], "unit_introduced": c["unit_introduced"], "unit": c["unit"], "projection_mode": c["projection_mode"],
        "year": c["year"], "current_value": c["current_value"], "proposed_value": proposed if isinstance(proposed, str) else fmt(proposed),
        "change_class": cls, "source_ids": sources, "source_value": sv, "source_unit": su, "source_currency_year": cy,
        "cpi_factor": ("%.6f" % cpi) if isinstance(cpi, float) else cpi, "derivation": der, "assumption_sentence": sent,
        "ao_row_at_b51f24b": c["ao_row_at_b51f24b"]})


def verdict(cls):
    return "within 25 percent, current value kept" if cls == "confirmed" else "differs by more than 25 percent, sourced value proposed"


def sourced(c, val, s, der):
    cur = float(c["current_value"])
    cls = classify(cur, val)
    prop = c["current_value"] if cls == "confirmed" else val
    out(c, prop, cls, s["sources"], s["sv"], s["su"], s["cy"], s["cpi"], der + " Sourced value %s against current %s: %s." % (fmt(val), c["current_value"], verdict(cls)))
    return cls


def is_base(c):
    return c["cell_meaning"].startswith("base-year") or c["cell_meaning"].startswith("ratio")


# proposed raw base-year cell of every price row (for the ratio rows)
PROP_BASE = {}
for c in CELLS:
    if c["model"] == "HON_ENERGY" and c["parameter"] == "CapitalCost" and is_base(c) and c["tech"] in PRICE:
        v = PRICE[c["tech"]]["value"]
        PROP_BASE[c["tech"]] = (float(c["current_value"]), "current cell, confirmed") if classify(float(c["current_value"]), v) == "confirmed" else (v, "proposed cell")


def vehicle(c):
    tech, par, mode = c["tech"], c["parameter"], c["projection_mode"]
    if par == "Ref.km.BY":
        if tech in KM:
            v, lab = KM[tech]
            s = dict(sources="GEN-104", sv=str(v), su="km per vehicle per year (%s)" % lab, cy="", cpi="")
            sourced(c, float(v), s, "GEN annual_km: use intensity of %s in the Dominican Republic electric mobility plan, %s km per year (GEN-104, PDF p. 78, Tabla 4, from average daily distances by vehicle type). Honduras publishes no distance per vehicle by type (no inspection or odometer series); the plan is the nearest published regional value." % (lab, format(v, ",")))
        else:
            out(c, c["current_value"], "assumption", der="No Honduran or GEN distance for taxis; current value kept as the assumption value.",
                sent="A taxi in Honduras runs 25,000 km per year, about 85 km per working day over 300 days, more than three times the private-car figure. The Dominican Republic electric mobility plan gives 7,500 km per year for private automobiles and 44,000 km per year for buses, and a taxi in daily urban service lies between the two; range 20,000 to 50,000 km per year.")
        return
    prefix, pt = split(tech)
    cls_name = CLASS[prefix]
    if par == "OperationalLife":
        v, src = LIFE[cls_name]
        sourced(c, float(v), dict(sources=src + ";HON-001", sv=str(v), su="years", cy="", cpi=""), LIFE_DER[v])
        return
    if par == "FixedCost":
        if prefix == "TRMOT":
            sent = {"GSL": "Maintenance of a gasoline motorcycle in Honduras costs 5.41 M US$ per Gvkm (0.0054 US$ per km, about 40 to 60 US$ per year at 7,000 to 10,500 km) in every year. No public cost series covers motorcycle maintenance in the region; range 3 to 20 M US$ per Gvkm.",
                    "ELE": "Maintenance of an electric motorcycle in Honduras costs 1.7853 M US$ per Gvkm (about 13 to 19 US$ per year at 7,000 to 10,500 km) in every year, a third of the gasoline motorcycle figure, in line with the lower maintenance of electric drivetrains. Range 1 to 10 M US$ per Gvkm."}[pt]
            out(c, c["current_value"], "assumption", der="No GEN maintenance value for motorcycles; same value every year.", sent=sent)
            return
        gpt = pt if pt in ("DSL", "GSL", "LPG", "NGS", "ELE", "HYD", "HG", "HD") else "DSL"
        v20, v24 = GV[("maint", cls_name, gpt)]
        s = dict(sources="GEN-102;GEN-001", sv=str(v20), su="M US$ per Gvkm (ATB levelized maintenance and repair, US conditions)", cy="2020", cpi=F20)
        der = ("GEN maintenance_cost %s %s: %s M US$ per Gvkm (2020 USD) x CPI factor %.6f = %.3f (2024 USD), same value every year%s. Honduras publishes no vehicle maintenance cost series; the Dominican Republic plan sets electric vehicle maintenance at 3 percent per year of the vehicle price (GEN-104, PDF p. 94, footnote 31), a rule for electric vehicles only, so one basis (ATB) is used for all powertrains."
               % (cls_name, gpt, v20, F20, v24, " (Flat row: base-year cell only, every year takes it)" if mode == "Flat" else ""))
        sourced(c, v24, s, der)
        return
    km_note = KM_NOTE.get(GROUP[prefix], "")
    if is_base(c):
        flat = " Flat row: base-year cell only, every year takes it." if mode == "Flat" else " Base-year cell of a trajectory row: the cell holds the 2024 price and later year cells hold multipliers on it."
        if tech == "TRMOTGSL":
            out(c, c["current_value"], "assumption", der="Flat row: base-year cell only, every year takes it. No Honduran or GEN price for gasoline motorcycles." + km_note, sent=MOT_GSL_SENT)
            return
        if c["unit_introduced"].startswith("Relative to"):
            ref = c["unit_introduced"].replace("Relative to", "").strip()
            target, txt, srcs = RATIO[tech]
            refv, reftxt = PROP_BASE[ref]
            ratio = target / refv
            s = dict(sources=srcs, sv="%.2f / %.2f" % (target, refv), su="ratio of prices in 2024 USD", cy="", cpi="")
            der = "Ratio the compiler expects: this vehicle's price (%s = %.2f US$, 2024 USD) divided by the raw base-year cell of %s (%s = %.2f US$); the compiler multiplies them." % (txt, target, ref, reftxt, refv)
            sourced(c, ratio, s, der + flat + km_note)
            return
        s = PRICE[tech]
        sourced(c, s["value"], s, s["der"] + flat + km_note)
        return
    y = int(c["year"])
    fam = TRAJ_KEY[tech]
    if y < 2024:
        m = 1.0
        der = "Multiplier for %d: 1.0. The GEN price_trajectory (NREL ATB 2022 Mid, %s %s) is relative to the 2024 price and starts in 2024; the base-year cell holds a 2024 price, so years before 2024 take it unchanged." % (y, fam[0], fam[1])
    else:
        m = TRAJ[(fam[0], fam[1], y)]
        der = "GEN price_trajectory %s %s, year %d: ratio %.6f to the own 2024 price (NREL ATB 2022 Mid, interpolated between published years); applies because the base-year cell holds a 2024 price." % (fam[0], fam[1], y, m)
    sourced(c, m, dict(sources="GEN-101", sv="%.6f" % m, su="ratio to 2024 price", cy="", cpi=""), der + km_note)


# ---------------- sector ----------------
FAO = {}
with open(os.path.join(JOB, "GEN", "faostat_trade_unit_values.csv"), encoding="utf-8") as f:
    FAOROWS = [r for r in csv.DictReader(f) if r["country"] == "HON"]
for r in FAOROWS:
    if r["year"] == "avg_2019_2023":
        FAO[r["model_item"]] = (float(r["unit_value_2024usd"]), r["fao_items"])
PP = {}
with open(os.path.join(JOB, "GEN", "faostat_producer_prices.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["country"] == "HON" and r["year"] == "avg_2019_2023":
            PP[r["model_item"]] = float(r["producer_price_2024usd_per_t"])
YLD = {}
with open(os.path.join(JOB, "GEN", "faostat_yields.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["country"] == "HON" and r["year"] == "avg_2019_2023":
            YLD[r["model_item"]] = float(r["yield_t_per_ha"])


def gross(item):
    return PP[item] * YLD[item]


# Banana: A-flag years only (the 2022 value is an FAO estimate, flag X, on 106,044 t at 35.56 US$ per t)
ban = [r for r in FAOROWS if r["model_item"] == "banana" and r["year"] != "avg_2019_2023" and r["fao_flags"] == "A"]
BAN_V = sum(float(r["import_value_kusd"]) * 1000 * float(r["cpi_factor"]) for r in ban) / sum(float(r["import_quantity"]) for r in ban)
BAN_YEARS = ", ".join(r["year"] for r in ban)

IMP = {"IMPMAI": ("maize", ""), "IMPFRI": ("beans_dry", " The model item is frijol (dry beans), FAO item 176."),
       "IMPRIC": ("rice", " Rice in milled equivalent (FAO 30)."),
       "IMPCAF": ("coffee", " Green coffee imports are small (85 t per year on average) and the annual unit values swing from 604 to 7,678 US$ per t, so the value is less robust."),
       "IMPLEG": ("vegetables", " The model item LEG (legumbres) is read as vegetables, the crop whose production cost the model's AG_LEG row matches; the FAO pulses aggregate gives 1,218.55 US$ per t, within 10 percent.")}

CEPAL_COLL = (34.22 + 12.01) * CPI[2010]
CEPAL_DISP = 20.43 * CPI[2010]
WAW_OD_HIGH = 10 * CPI[2018]

COF_L = [26879.80, 25482.52, 27460.48, 31610.23]
COF_MZ = sum(COF_L) / 4
COF_HA = COF_MZ * MZ_PER_HA
COF_USD = COF_HA / FX[2016]
COF_24 = COF_USD * CPI[2016]



def crop_sent(tech, cur):
    if tech == "AG_RIC":
        return ("Rice costs %s US$ per ha per year to grow in Honduras, a national mean of irrigated valley rice (Comayagua, Olancho) and rainfed smallholder rice. "
                "A published budget for traditional low-input rice in Wampusirpi (CIAT 2024) gives L 22,050 per ha (about 920 US$ per ha in 2024 USD), the lower bound for unirrigated rice with little fertiliser; irrigated rice with purchased inputs costs two to three times as much. Range 900 to 3,000 US$ per ha.") % format(cur, ",.1f")
    if tech == "AG_MAI":
        g = gross("maize")
        return ("Maize costs %s US$ per ha per year (M US$ per Mha) to grow in Honduras, covering seed, fertiliser, labour and land preparation of the mostly smallholder rainfed crop. "
                "FAOSTAT's producer price and yield for Honduras (2019 to 2023, real 2024 USD) give a gross output value of about %s US$ per ha, so the cost lies above the average revenue of the crop; range 700 to 2,000 US$ per ha.") % (format(cur, ",.1f"), format(round(g), ","))
    if tech == "AG_BAN":
        g = gross("banana")
        return ("Bananas cost %s US$ per ha per year to grow in Honduras, the field cost of the plantation crop for export. FAOSTAT's producer price and yield for Honduras (2019 to 2023, real 2024 USD) give a gross output value of about %s US$ per ha, so the cost is about one tenth of it; "
                "export plantations spend 5,000 to 12,000 US$ per ha per year on inputs and labour, and range 2,000 to 12,000 US$ per ha.") % (format(cur, ",.2f"), format(round(g), ","))
    if tech == "AG_MEL":
        g = gross("melons")
        return ("Melons cost %s US$ per ha per year to grow in Honduras, the irrigated export crop of the southern coast. FAOSTAT's producer price and yield for Honduras (2019 to 2023, real 2024 USD) give a gross output value of about %s US$ per ha; range 4,000 to 12,000 US$ per ha.") % (format(cur, ",.1f"), format(round(g), ","))
    if tech == "AG_PLM":
        g = gross("oil_palm")
        return ("Oil palm costs %s US$ per ha per year to grow in Honduras, for upkeep, fertiliser and harvest of fresh fruit bunches. FAOSTAT's producer price and yield for Honduras (2019 to 2023, real 2024 USD) give a gross output value of about %s US$ per ha; range 1,000 to 2,500 US$ per ha.") % (format(cur, ",.1f"), format(round(g), ","))
    if tech == "AG_SGC":
        g = gross("sugar_cane")
        return ("Sugar cane costs %s US$ per ha per year to grow in Honduras, for inputs, cutting and haulage to the mill. FAOSTAT's producer price and yield for Honduras (2019 to 2023, real 2024 USD) give a gross output value of about %s US$ per ha; range 1,500 to 2,500 US$ per ha.") % (format(cur, ",.1f"), format(round(g), ","))
    if tech == "AG_LEG":
        g = gross("vegetables")
        return ("Vegetables (legumbres) cost %s US$ per ha per year to grow in Honduras, the input and labour intensive horticultural crops. FAOSTAT's producer prices and yields for Honduras (2019 to 2023, real 2024 USD) give a gross output value of about %s US$ per ha for vegetables; range 3,000 to 12,000 US$ per ha.") % (format(cur, ",.1f"), format(round(g), ","))
    raise KeyError(tech)


PEN_NAME = {"contam_agua": ("water-contamination", "damage to rivers and groundwater from open dumps and waste burning", "", "range half to double"),
            "salud_residuos": ("public-health", "illness linked to open dumps and waste burning", ", 2.43 times the water-contamination externality", "range half to double"),
            "turismo_residuos": ("tourism", "tourism revenue lost to littered coasts, rivers and dumps", ", 3.64 times the water-contamination externality", "range half to double")}


def pen_sent(tech):
    vals = {int(x["year"]): float(x["current_value"]) for x in CELLS if x["tech"] == tech and x["parameter"] == "EmissionsPenalty"}
    nm, what, ratio, rng = PEN_NAME[tech]
    return ("The %s externality of uncontrolled waste disposal in Honduras is %.4f M US$ per kt of waste (%.1f US$ per t) in 2018, falling to %.4f (%.1f US$ per t) in 2030 and %.4f (%.1f US$ per t) in 2050. "
            "It values %s%s; %s.") % (nm, vals[2018], vals[2018] * 1000, vals[2030], vals[2030] * 1000, vals[2050], vals[2050] * 1000, what, ratio, rng)


def sector(c):
    tech, par = c["tech"], c["parameter"]
    cur = float(c["current_value"])
    peryear = " Flat row: base-year cell only, every year takes it." if c["projection_mode"] == "Flat" else " Same value every year."
    if par == "EmissionsPenalty":
        out(c, c["current_value"], "assumption", der="Penalty per unit of emission in that year (M US$ per kt). The published origin (IDB waste-sector guidelines) cannot be downloaded; listed in manual_downloads_HON.csv.", sent=pen_sent(tech))
        return
    if tech == "AG_CAF" and par == "CapitalCost":
        out(c, c["current_value"], "assumption", der="User defined row, zero in every year; same value every year.",
            sent="Coffee carries no capital cost per hectare in Honduras: the plantation exists, and its yearly renovation (pruning, replanting of old bushes) is part of the yearly production cost per hectare. Establishing a new hectare of coffee costs roughly 2,000 to 4,000 US$ over the first two to three years, which is the range if new plantations are to carry a capital cost.")
        return
    if tech == "AG_CAF" and par == "VariableCost":
        der = ("UNDP, HEIFER and IHCAFE coffee value chain study (2018), Tabla 7 (PDF p. 16) and Tabla 15 (PDF p. 30): production cost per manzana by farm size, 26,879.80 (under 2 mz), 25,482.52 (to 5 mz), 27,460.48 (to 20 mz), 31,610.23 (over 20 mz) L per mz; field data of the 2015-2016 harvest (PDF p. 4), currency year 2016. "
               "Mean of the four classes %.2f L per mz x 1.43 mz per ha (INE, CAN 2024, HON-003) = %.1f L per ha / %.4f L per US$ (WDI 2016, HON-004) = %.2f US$ per ha (2016) x CPI factor %.6f = %.2f US$ per ha (2024 USD). "
               "The farm-size classes give %.0f to %.0f US$ per ha (2024 USD). The study notes that the costs exclude farm administration and interest and that most farms do not count family labour, so the value is a lower bound. "
               "Current value 4,318.8 equals FAOSTAT's producer price x yield for Honduras (3,744.53 x 1.154 = 4,321 US$ per ha, GEN-202, GEN-203), a gross output value rather than a cost.") % (
            COF_MZ, COF_HA, FX[2016], COF_USD, CPI[2016], COF_24, min(COF_L) * MZ_PER_HA / FX[2016] * CPI[2016], max(COF_L) * MZ_PER_HA / FX[2016] * CPI[2016])
        s = dict(sources="HON-002;HON-003;HON-004;GEN-001", sv="26879.80; 25482.52; 27460.48; 31610.23", su="L per manzana (coffee production cost by farm size)", cy="2016", cpi=CPI[2016])
        sourced(c, COF_24, s, der + peryear)
        return
    if tech == "AG_FRI":
        lha = 15730
        usd = lha / FX[2023]
        v24 = usd * CPI[2023]
        der = ("CIAT (2024), Perfil del mercado y las cadenas de granos basicos en Wampusirpi, Honduras: production cost of beans (frijol) per hectare, L 15,700 in the text (PDF p. 13) and 15,730 L in the budget of Anexo 2 (PDF p. 24: seed, land preparation, sowing, weeding, insecticide, harvest, land rent; hired and family labour at the local day wage), currency year 2023. "
               "15,730 L per ha / %.4f L per US$ (WDI 2023, HON-004) = %.2f US$ per ha (2023) x CPI factor %.6f = %.2f US$ per ha (2024 USD). "
               "The budget is for one municipality of La Mosquitia under traditional low-input practice; beans in Honduras are mostly a smallholder rainfed crop, and the study puts the local yield in poor years (0.64 to 0.91 t per ha) in the range of the national mean, so it is used as the national cost.") % (FX[2023], usd, CPI[2023], v24)
        s = dict(sources="HON-005;HON-004;GEN-001", sv="15,730", su="L per ha (beans, total production cost)", cy="2023", cpi=CPI[2023])
        sourced(c, v24, s, der + peryear)
        return
    if tech.startswith("AG_"):
        out(c, c["current_value"], "assumption", der="No Honduran crop budget for this crop." + peryear, sent=crop_sent(tech, cur))
        return
    if tech in IMP:
        item, note = IMP[tech]
        v, items = FAO[item]
        s = dict(sources="GEN-201;GEN-001", sv="%.2f" % v, su="US$ per t (FAOSTAT import unit value, quantity-weighted mean 2019 to 2023, real 2024 USD)", cy="2019-2023", cpi=FAO_CPI)
        sourced(c, v, s, "FAOSTAT import unit value for Honduras, item %s, quantity-weighted mean of 2019 to 2023 in real 2024 USD = %.2f US$ per t (GEN-201; each year deflated with its own CPI factor). Model unit MUSD/Mt equals US$ per t.%s%s" % (items, v, note, peryear))
        return
    if tech == "IMPBAN":
        s = dict(sources="GEN-201;GEN-001", sv="422.0; 416.0; 2952.0; 777.0 (1000 US$) on 3353.17; 5031.35; 21501.03; 2679.26 t", su="1000 US$ and t (FAOSTAT import value and quantity, bananas, FAO 486)", cy="2019-2023", cpi=FAO_CPI)
        sourced(c, BAN_V, s, ("FAOSTAT bananas (FAO 486) imports of Honduras, years with official data (flag A: %s): sum of import values deflated with each year's CPI factor / sum of quantities = %.2f US$ per t (2024 USD). "
                               "The 2022 value (106,044 t at 35.56 US$ per t, flag X, an FAO estimate) is left out; with it the quantity-weighted mean is 66.96 US$ per t (GEN file). Model unit MUSD/Mt equals US$ per t.%s") % (BAN_YEARS, BAN_V, peryear))
        return
    if tech == "IMPMEL":
        out(c, "%.2f" % PP["melons"], "assumption", der="FAOSTAT melon imports of Honduras are about 1 t per year except an FAO estimate (flag X) of 4,017 t in 2022, so no import unit value is usable." + peryear,
            sent="Imported melons cost %.2f US$ per t (M US$ per Mt) in Honduras, the FAOSTAT producer price of melons in Honduras for 2019 to 2023 in real 2024 USD, taken as the import parity price since Honduras is a net melon exporter and imports almost none. Range 400 to 1,000 US$ per t." % PP["melons"])
        return
    if tech in ("BLEND_NO_DCOLL", "LANDFILL"):
        same = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == tech and x["year"] == c["year"]]
        tot_cur = sum(float(x["current_value"]) for x in same)
        if tech == "BLEND_NO_DCOLL":
            v, sv, lab, waw = CEPAL_COLL, "34.22 + 12.01", "collection (34.22) plus transfer (12.01) US$ per t, 2010 USD", "37.48 to 93.69"
        else:
            v, sv, lab, waw = CEPAL_DISP, "20.43", "final disposal 20.43 US$ per t, 2010 USD", "18.74 to 49.97"
        vk = v / 1000
        cls = classify(tot_cur, vk)
        prop = c["current_value"] if cls == "confirmed" else vk * cur / tot_cur
        d = ("CEPAL 2016, Cuadro 6 (Latin America and the Caribbean averages): %s x CPI factor %.6f = %.2f US$ per t (2024 USD) = %.5f M US$ per kt (model unit, US$ per t / 1000). Compared with the model's CapitalCost + VariableCost = %.4f M US$ per kt (%s); if replaced, split in the model's own proportion (this cell's share %.4f). "
             "What a Waste 2.0 (GEN-204, Table 5.2, p. 105) gives %s US$ per t for lower-middle income countries such as Honduras (2024 USD).") % (
            lab, CPI[2010], v, vk, tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur, waw)
        out(c, prop, cls, "GEN-206;GEN-204;GEN-001", sv, "US$ per t", "2010", CPI[2010], d + peryear)
        return
    if tech == "NO_CONTR_OD":
        s = dict(sources="GEN-204;GEN-001", sv="10", su="US$ per t (open dumping, top of the lower-middle income range 3 to 10)", cy="2018", cpi=CPI[2018])
        sourced(c, WAW_OD_HIGH / 1000, s, ("What a Waste 2.0, Table 5.2, p. 105: open dumping 3 to 10 US$ per t for lower-middle income countries, the income group of Honduras; the top of the range is used, as for the other countries: 10 x CPI factor %.6f = %.2f US$ per t (2024 USD) = %.5f M US$ per kt (model unit, US$ per t / 1000).") % (CPI[2018], WAW_OD_HIGH, WAW_OD_HIGH / 1000) + peryear)
        return
    raise KeyError((tech, par))


for c in CELLS:
    if c["model"] == "HON_ENERGY":
        vehicle(c)
    else:
        sector(c)

# Row-level coherence for multiplier series (same rule as the other countries)
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
with open(os.path.join(CC_DIR, "proposals_HON.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(ROWS)
print(len(CELLS), len(ROWS))
