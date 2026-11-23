"""Build proposals_DR.csv from cells_DR.csv, the GEN packages and the DR sources.

Run: python -I build_proposals_DR.py (paths are relative to this file).
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

# World Bank WDI PA.NUS.FCRF, Dominican Republic (DR-002)
FX = {2019: 51.2948583333333, 2021: 57.2211166666666}
TAREAS_PER_HA = 15.9  # DR-003 and DR-004: "Una Hectarea equivale a 15.9 tareas"

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
# National anchors (GEN-104, 2020 USD)
CAR_CONV_NAT = 20001 * F20       # PDF p. 72
CAR_ELE_NAT = 30000 * F20        # PDF p. 94, footnote 29
BUS_ELE_NAT = 360000 * F20
TRK_ELE_NAT = 120000 * F20
MOT_ELE_NAT = 3000 * F20


def atb(cls, pt):
    return GV[("price", cls, pt)]


R_C8_DSL_ELE = atb("heavy_freight", "DSL")[0] / atb("heavy_freight", "ELE")[0]
R_C8_HYD_DSL = atb("heavy_freight", "HYD")[0] / atb("heavy_freight", "DSL")[0]
R_C8_HD_DSL = atb("heavy_freight", "HD")[0] / atb("heavy_freight", "DSL")[0]
R_CAR_DSL_GSL = atb("car", "DSL")[0] / atb("car", "GSL")[0]
R_CAR_HG_GSL = atb("car", "HG")[0] / atb("car", "GSL")[0]

BUS_DSL = BUS_ELE_NAT * R_C8_DSL_ELE
TRK_DSL = TRK_ELE_NAT * R_C8_DSL_ELE
CAR_DSL = CAR_CONV_NAT * R_CAR_DSL_GSL
CAR_HG = CAR_CONV_NAT * R_CAR_HG_GSL

NAT_CAR = ("GEN-104;GEN-001", "20001", "US$ per vehicle (average new conventional vehicle, Dominican Republic)", "2020", F20)
KM_NOTE = {
    "Techs_Buses_Pub": " The proposed Ref.km.BY of this group changes from 33,000 to 44,000 km per vehicle per year, so the compiled M US$ per Gvkm changes with it (1000 x price / km).",
    "Techs_Buses_Tur": " The proposed Ref.km.BY of this group changes from 33,000 to 44,000 km per vehicle per year, so the compiled M US$ per Gvkm changes with it (1000 x price / km).",
}
GROUP = {"TRAUT": "Techs_Auto", "TRSUV": "Techs_SUV", "TRTAX": "Techs_Taxi", "TRYLF": "Techs_Li_Freight",
         "TRYTK": "Techs_He_Freight", "TRMBS": "Techs_Buses_Micro", "TRBPU": "Techs_Buses_Pub",
         "TRBTUR": "Techs_Buses_Tur", "TRMOT": "Techs_Motos"}
CLASS = {"TRAUT": "car", "TRSUV": "SUV", "TRTAX": "taxi", "TRYLF": "light_freight", "TRYTK": "heavy_freight",
         "TRMBS": "minibus", "TRBPU": "bus", "TRBTUR": "bus", "TRMOT": "motorcycle"}


def split(tech):
    for p in sorted(GROUP, key=len, reverse=True):
        if tech.startswith(p):
            return p, tech[len(p):]
    raise KeyError(tech)


def r6(x):
    return float("%.6g" % x) if abs(x) < 10 else round(x, 2)


# Base price specs: tech -> dict(kind='price'|'ratio', value, ref, sources, source_value, source_unit, cy, cpi, derivation)
def atb_price_spec(cls, pt, label):
    v20, v24 = atb(cls, pt)
    return dict(kind="price", value=v24, sources="GEN-101;GEN-001", sv=str(v20), su="US$ per vehicle (US purchase price, ATB 2022 Mid, 2024 model year)",
                cy="2020", cpi=F20, der="GEN reference_price %s %s: ATB 2022 Mid %s, %s US$ (2020 USD) x CPI factor %.6f = %.2f US$ (2024 USD). No Dominican price is published for this class and powertrain; US prices exclude Dominican import duties and taxes." % (cls, pt, label, v20, F20, v24))


def ratio_spec(num_val, num_txt, ref_tech, ref_val, ref_txt, sources):
    return dict(kind="ratio", value=num_val / ref_val, sources=sources, sv="%.2f / %.2f" % (num_val, ref_val), su="ratio of prices in 2024 USD",
                cy="", cpi="", der="Ratio the compiler expects: this vehicle's price (%s = %.2f US$) divided by the raw base-year cell of %s (%s = %.2f US$); the compiler multiplies them." % (num_txt, num_val, ref_tech, ref_txt, ref_val))


SPEC = {}
# Cars and taxis: national conventional price (GEN-104) with ATB powertrain ratios
SPEC["TRAUTGSL"] = dict(kind="price", value=CAR_CONV_NAT, sources="GEN-104;GEN-001", sv="20001", su="US$ per vehicle (average new conventional vehicle)", cy="2020", cpi=F20,
                        der="National average price of a new conventional vehicle, USD 20,001 (Plan Estrategico Nacional de Movilidad Electrica, PDF p. 72; plan dated 2020, currency year 2020) x CPI factor %.6f = %.2f US$ (2024 USD)." % (F20, CAR_CONV_NAT))
SPEC["TRAUTDSL"] = dict(kind="price", value=CAR_DSL, sources="GEN-104;GEN-101;GEN-001", sv="20001 x (28600 / 23120)", su="US$ per vehicle", cy="2020", cpi=F20,
                        der="National conventional vehicle price USD 20,001 (GEN-104, PDF p. 72) x CPI factor %.6f = %.2f, times the ATB 2022 Mid compact car diesel to gasoline price ratio 28,600 / 23,120 = %.5f (GEN-101) = %.2f US$ (2024 USD)." % (F20, CAR_CONV_NAT, R_CAR_DSL_GSL, CAR_DSL))
for t in ("TRTAXGSL", "TRTAXLPG"):
    SPEC[t] = dict(SPEC["TRAUTGSL"])
    if t.endswith("LPG"):
        SPEC[t]["der"] = SPEC["TRAUTGSL"]["der"] + " LPG taxis are converted gasoline cars, so they take the gasoline price (GEN proxy rule)."
for t in ("TRAUTELE", "TRTAXELE"):
    SPEC[t] = dict(kind="price", value=CAR_ELE_NAT, sources="GEN-104;GEN-001", sv="30000", su="US$ per vehicle (electric automobile)", cy="2020", cpi=F20,
                   der="Electric automobile price USD 30,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD)." % (F20, CAR_ELE_NAT))
SPEC["TRAUTHG"] = ratio_spec(CAR_HG, "national conventional price %.2f x ATB hybrid to gasoline ratio 25,600 / 23,120" % CAR_CONV_NAT, "TRAUTELE", 30000.0, "current cell, confirmed", "GEN-104;GEN-101;GEN-001")
SPEC["TRAUTLPG"] = ratio_spec(CAR_CONV_NAT, "gasoline car price, GEN proxy for LPG", "TRAUTDSL", CAR_DSL, "proposed cell", "GEN-104;GEN-101;GEN-001")
# SUV
for pt, lab in (("DSL", "Small SUV Conventional CI"), ("GSL", "Small SUV Conventional SI"), ("NGS", "Small SUV CNG")):
    SPEC["TRSUV" + pt] = atb_price_spec("SUV", pt, lab)
SPEC["TRSUVELE"] = ratio_spec(atb("SUV", "ELE")[1], "ATB Small SUV BEV300, 2024 USD", "TRSUVDSL", atb("SUV", "DSL")[1], "proposed cell", "GEN-101;GEN-001")
SPEC["TRSUVLPG"] = ratio_spec(atb("SUV", "LPG")[1], "ATB Small SUV gasoline, GEN proxy for LPG, 2024 USD", "TRSUVDSL", atb("SUV", "DSL")[1], "proposed cell", "GEN-101;GEN-001")
# Light freight (pickup)
SPEC["TRYLFDSL"] = atb_price_spec("light_freight", "DSL", "Pickup Conventional CI")
SPEC["TRYLFGSL"] = atb_price_spec("light_freight", "GSL", "Pickup Conventional SI")
for pt, lab in (("ELE", "Pickup BEV300"), ("HD", "Pickup hybrid, GEN proxy for HD"), ("LPG", "Pickup gasoline, GEN proxy for LPG"), ("NGS", "Pickup CNG")):
    SPEC["TRYLF" + pt] = ratio_spec(atb("light_freight", pt)[1], "ATB %s, 2024 USD" % lab, "TRYLFDSL", atb("light_freight", "DSL")[1], "proposed cell", "GEN-101;GEN-001")
# Minibus (ATB Class 4 step van)
SPEC["TRMBSDSL"] = atb_price_spec("minibus", "DSL", "Class 4 StepVan diesel")
SPEC["TRMBSGSL"] = atb_price_spec("minibus", "GSL", "Class 4 StepVan, diesel proxy for gasoline")
SPEC["TRMBSELE"] = ratio_spec(atb("minibus", "ELE")[1], "ATB Class 4 StepVan BEV, 2024 USD", "TRMBSDSL", atb("minibus", "DSL")[1], "proposed cell", "GEN-101;GEN-001")
SPEC["TRMBSLPG"] = ratio_spec(atb("minibus", "LPG")[1], "ATB Class 4 StepVan, diesel proxy for LPG, 2024 USD", "TRMBSDSL", atb("minibus", "DSL")[1], "proposed cell", "GEN-101;GEN-001")
# Buses: national electric bus price, ATB Class 8 powertrain ratios
for p in ("TRBPU", "TRBTUR"):
    SPEC[p + "ELE"] = dict(kind="price", value=BUS_ELE_NAT, sources="GEN-104;GEN-001", sv="360000", su="US$ per vehicle (electric bus)", cy="2020", cpi=F20,
                           der="Electric bus price USD 360,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD)." % (F20, BUS_ELE_NAT))
    for pt in ("DSL", "GSL"):
        SPEC[p + pt] = dict(kind="price", value=BUS_DSL, sources="GEN-104;GEN-101;GEN-001", sv="360000 x (160750 / 327750)", su="US$ per vehicle", cy="2020", cpi=F20,
                            der="National electric bus price USD 360,000 (GEN-104) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101; ATB has no bus, Class 8 is the GEN heavy-duty proxy) = %.2f US$ (2024 USD).%s" % (F20, BUS_ELE_NAT, R_C8_DSL_ELE, BUS_DSL, " Gasoline buses take the diesel price (GEN proxy rule)." if pt == "GSL" else ""))
    SPEC[p + "HYD"] = ratio_spec(BUS_DSL * R_C8_HYD_DSL, "diesel bus price x ATB Class 8 FCEV to diesel ratio 292,000 / 160,750", p + "DSL", BUS_DSL, "proposed cell", "GEN-104;GEN-101;GEN-001")
    SPEC[p + "LPG"] = ratio_spec(BUS_DSL, "diesel bus price, GEN proxy for LPG", p + "DSL", BUS_DSL, "proposed cell", "GEN-104;GEN-101;GEN-001")
# Heavy freight: national electric cargo vehicle price, ATB Class 8 ratios
SPEC["TRYTKELE"] = dict(kind="price", value=TRK_ELE_NAT, sources="GEN-104;GEN-001", sv="120000", su="US$ per vehicle (electric cargo vehicle)", cy="2020", cpi=F20,
                        der="Electric cargo vehicle price USD 120,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD)." % (F20, TRK_ELE_NAT))
for pt in ("DSL", "GSL"):
    SPEC["TRYTK" + pt] = dict(kind="price", value=TRK_DSL, sources="GEN-104;GEN-101;GEN-001", sv="120000 x (160750 / 327750)", su="US$ per vehicle", cy="2020", cpi=F20,
                              der="National electric cargo vehicle price USD 120,000 (GEN-104) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101) = %.2f US$ (2024 USD).%s" % (F20, TRK_ELE_NAT, R_C8_DSL_ELE, TRK_DSL, " Gasoline trucks take the diesel price (GEN proxy rule)." if pt == "GSL" else ""))
SPEC["TRYTKHD"] = ratio_spec(TRK_DSL * R_C8_HD_DSL, "diesel truck price x ATB Class 8 diesel hybrid to diesel ratio 172,750 / 160,750", "TRYTKDSL", TRK_DSL, "proposed cell", "GEN-104;GEN-101;GEN-001")
SPEC["TRYTKHYD"] = ratio_spec(TRK_DSL * R_C8_HYD_DSL, "diesel truck price x ATB Class 8 FCEV to diesel ratio 292,000 / 160,750", "TRYTKDSL", TRK_DSL, "proposed cell", "GEN-104;GEN-101;GEN-001")
SPEC["TRYTKLPG"] = ratio_spec(TRK_DSL, "diesel truck price, GEN proxy for LPG", "TRYTKDSL", TRK_DSL, "proposed cell", "GEN-104;GEN-101;GEN-001")
# Motorcycles
SPEC["TRMOTELE"] = dict(kind="price", value=MOT_ELE_NAT, sources="GEN-104;GEN-001", sv="3000", su="US$ per vehicle (electric motorcycle)", cy="2020", cpi=F20,
                        der="Electric motorcycle price USD 3,000 (GEN-104, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD)." % (F20, MOT_ELE_NAT))
SPEC["TRMOTGSL"] = dict(kind="assumption", sentence="A new gasoline motorcycle of 100 to 150 cc costs 1,153.47 US$ per vehicle in the Dominican Republic in the base year, the typical commuter and motoconcho model. The national electric mobility plan prices an electric motorcycle at USD 3,000 (2020), so the gasoline model is about 40 percent of the electric one; range 900 to 2,000 US$ per vehicle.")

# Trajectory family per tech
TRAJ_KEY = {"TRAUTELE": ("car", "ELE"), "TRAUTHG": ("car", "HG"), "TRTAXELE": ("taxi", "ELE"), "TRSUVELE": ("SUV", "ELE"),
            "TRYLFELE": ("light_freight", "ELE"), "TRYTKELE": ("heavy_freight", "ELE"), "TRYTKHYD": ("heavy_freight", "HYD"),
            "TRBPUELE": ("bus", "ELE"), "TRBTURELE": ("bus", "ELE"), "TRBPUHYD": ("bus", "HYD"), "TRBTURHYD": ("bus", "HYD"),
            "TRMBSELE": ("minibus", "ELE")}

# Operational life (GEN operational_life mapping)
LIFE = {"car": (15, "GEN-103;GEN-104;DR-001"), "taxi": (15, "GEN-103;GEN-104;DR-001"), "SUV": (15, "GEN-103;GEN-104;DR-001"),
        "light_freight": (15, "GEN-103;GEN-104;DR-001"), "minibus": (15, "GEN-103;GEN-104;DR-001"),
        "bus": (10, "GEN-104;DR-001"), "heavy_freight": (10, "GEN-104;DR-001"), "motorcycle": (10, "GEN-104;DR-001")}
LIFE_DER = {15: "GEN operational_life for this class: 15 years (NREL ATB 2022 light-duty and Class 4 vehicle life, GEN-103). National comparison: the electric mobility plan uses a theoretical 10-year life for the whole fleet (GEN-104, PDF p. 78, footnote 11), while the DGII 2023 fleet register shows 48.4 percent of automobiles and 13.7 percent of jeeps built in 2000 or earlier (DR-001, Cuadro 2.9.1, PDF p. 18), so registered light vehicles stay in use well beyond 10 years; 15 years lies between the two.",
            10: "GEN operational_life for this class: 10 years, the theoretical vehicle life of the national electric mobility plan (GEN-104, PDF p. 78, footnote 11; 2.4 percent of the fleet retired each year). National comparison: the DGII 2023 fleet register shows 41.7 percent of buses, 48.3 percent of cargo vehicles and 35.6 percent of motorcycles built in 2000 or earlier (DR-001, Cuadro 2.9.1, PDF p. 18), which points to longer real service lives; see the report decision on heavy-vehicle lives."}

# Distances
KM = {"Techs_Auto": (7500, "automobiles and jeeps"), "Techs_SUV": (7500, "automobiles and jeeps"), "Techs_Buses_Micro": (44000, "buses"),
      "Techs_Buses_Pub": (44000, "buses"), "Techs_Buses_Tur": (44000, "buses"), "Techs_He_Freight": (9000, "cargo vehicles"),
      "Techs_Li_Freight": (9000, "cargo vehicles"), "Techs_Motos": (10500, "motorcycles")}

ROWS = []
with open(os.path.join(CC_DIR, "cells_DR.csv"), encoding="utf-8") as f:
    CELLS = list(csv.DictReader(f))


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


def out(c, proposed, cls, sources="", sv="", su="", cy="", cpi="", der="", sent=""):
    ROWS.append({
        "country": c["country"], "model": c["model"], "sheet": c["sheet"], "tech": c["tech"], "tech_name": c["tech_name"],
        "parameter": c["parameter"], "unit_introduced": c["unit_introduced"], "unit": c["unit"], "projection_mode": c["projection_mode"],
        "year": c["year"], "current_value": c["current_value"], "proposed_value": proposed if isinstance(proposed, str) else fmt(proposed),
        "change_class": cls, "source_ids": sources, "source_value": sv, "source_unit": su, "source_currency_year": cy,
        "cpi_factor": ("%.6f" % cpi) if isinstance(cpi, float) else cpi, "derivation": der, "assumption_sentence": sent,
        "ao_row_at_b51f24b": c["ao_row_at_b51f24b"]})


def sourced(c, val, spec_like, der, cur=None):
    cur = float(c["current_value"]) if cur is None else cur
    cls = classify(cur, val)
    prop = c["current_value"] if cls == "confirmed" else val
    d = der + (" Sourced value %s against current %s: %s." % (fmt(val), c["current_value"], "within 25 percent, current value kept" if cls == "confirmed" else "differs by more than 25 percent, sourced value proposed"))
    out(c, prop, cls, spec_like["sources"], spec_like["sv"], spec_like["su"], spec_like["cy"], spec_like["cpi"], d)


def vehicle(c):
    tech, par, mode, cm = c["tech"], c["parameter"], c["projection_mode"], c["cell_meaning"]
    if par in ("Ref.km.BY",):
        g = tech
        if g in KM:
            v, lab = KM[g]
            s = dict(sources="GEN-104", sv=str(v), su="km per vehicle per year (%s)" % lab, cy="", cpi="")
            sourced(c, float(v), s, "Use intensity of %s in the national electric mobility plan: %s km per year (GEN-104, PDF p. 78, Tabla 4, from average daily distances by vehicle type)." % (lab, format(v, ",")))
        else:  # taxi
            out(c, c["current_value"], "assumption", der="No national or GEN distance for taxis.",
                sent="A taxi in the Dominican Republic runs 45,000 km per year, about 150 km per working day over 300 days, six times the private-car figure. The national electric mobility plan gives 7,500 km per year for private automobiles and 44,000 km per year for buses, and a taxi in daily service sits near the bus figure; range 30,000 to 60,000 km per year.")
        return
    prefix, pt = split(tech)
    cls_name = CLASS[prefix]
    if par == "OperationalLife":
        v, src = LIFE[cls_name]
        s = dict(sources=src, sv=str(v), su="years", cy="", cpi="")
        sourced(c, float(v), s, LIFE_DER[v])
        return
    if par == "FixedCost":
        if prefix == "TRMOT":
            sent = {"GSL": "Maintenance of a gasoline motorcycle costs 5.41 M US$ per Gvkm (0.0054 US$ per km, about 57 US$ per year at 10,500 km) in every year. No public cost series covers motorcycle maintenance in the region; range 3 to 20 M US$ per Gvkm.",
                    "ELE": "Maintenance of an electric motorcycle costs 1.7853 M US$ per Gvkm (about 19 US$ per year at 10,500 km) in every year, a third of the gasoline motorcycle figure, in line with the lower maintenance of electric drivetrains. Range 1 to 10 M US$ per Gvkm."}[pt]
            out(c, c["current_value"], "assumption", der="No GEN maintenance value for motorcycles; same value every year.", sent=sent)
            return
        gpt = pt if pt in ("DSL", "GSL", "LPG", "NGS", "ELE", "HYD", "HG", "HD") else "DSL"
        mcls = "bus" if cls_name == "bus" else cls_name
        v20, v24 = GV[("maint", mcls, gpt)]
        s = dict(sources="GEN-102;GEN-001", sv=str(v20), su="M US$ per Gvkm (ATB levelized maintenance and repair, US conditions)", cy="2020", cpi=F20)
        der = ("GEN maintenance_cost %s %s: %s M US$ per Gvkm (2020 USD) x CPI factor %.6f = %.3f (2024 USD), same value every year%s. National comparison: the electric mobility plan sets electric vehicle maintenance at 3 percent per year of the vehicle price (GEN-104, PDF p. 94, footnote 31), a rule for electric vehicles only, so one basis (ATB) is used for all powertrains."
               % (mcls, gpt, v20, F20, v24, " (Flat row: base-year cell only, every year takes it)" if mode == "Flat" else ""))
        sourced(c, v24, s, der)
        return
    # CapitalCost
    spec = SPEC[tech]
    km_note = KM_NOTE.get(GROUP[prefix], "")
    is_base = cm.startswith("base-year") or cm.startswith("ratio")
    if is_base:
        if spec["kind"] == "assumption":
            out(c, c["current_value"], "assumption", der="Flat row: base-year cell only, every year takes it. No national or GEN price for gasoline motorcycles.", sent=spec["sentence"])
            return
        flat = " Flat row: base-year cell only, every year takes it." if mode == "Flat" else " Base-year cell of a trajectory row: the cell holds the 2024 price and later year cells hold multipliers on it."
        sourced(c, spec["value"], spec, spec["der"] + flat + km_note)
        return
    # multiplier cell
    y = int(c["year"])
    fam = TRAJ_KEY[tech]
    if y < 2024:
        m = 1.0
        der = "Multiplier for %d: 1.0. The GEN price_trajectory (NREL ATB 2022 Mid, %s %s) is relative to the 2024 price and starts in 2024; the base-year cell holds a 2024 price, so years before 2024 take it unchanged." % (y, fam[0], fam[1])
    else:
        m = TRAJ[(fam[0], fam[1], y)]
        der = "GEN price_trajectory %s %s, year %d: ratio %.6f to the own 2024 price (NREL ATB 2022 Mid, interpolated between published years); applies because the base-year cell holds a 2024 price." % (fam[0], fam[1], y, m)
    s = dict(sources="GEN-101", sv="%.6f" % m, su="ratio to 2024 price", cy="", cpi="")
    sourced(c, m, s, der + km_note)


# ---------------- sector ----------------
def crop_total(name):
    if name == "rice":
        rd_t = 7900.40
        ha = rd_t * TAREAS_PER_HA
        usd = ha / FX[2021]
        v24 = usd * CPI[2021]
        return v24, "DR-003;DR-002;GEN-001", "7900.40", "RD$ per tarea (rice, total variable cost incl. financing, FENARROZ 2021)", "2021", CPI[2021], \
            "Rice production cost 7,900.40 RD$ per tarea (Ministerio de Agricultura, Costo de Produccion 2021, rice table PDF p. 7, source FENARROZ) x 15.9 tareas per ha (same document) = %.1f RD$ per ha / %.4f RD$ per US$ (WDI 2021, DR-002) = %.2f US$ per ha (2021) x CPI factor %.6f = %.2f US$ per ha (2024 USD)." % (ha, FX[2021], usd, CPI[2021], v24)
    if name == "cocoa":
        rd_t = (11112.36 + 7 * 4310.6) / 10
        lab = "cocoa: establishment years 1 to 3 = 11,112.36 RD$ per tarea, maintenance from year 4 = 4,310.6 RD$ per tarea per year (Costos Estimados 2019, PDF p. 131)"
    elif name == "coffee":
        rd_t = (8262.9 + 7 * 1105.98) / 10
        lab = "coffee: establishment years 1 to 3 = 8,262.9 RD$ per tarea, maintenance from year 4 = 1,105.98 RD$ per tarea per year (Costos Estimados 2019, PDF p. 132)"
    elif name == "fruit":
        rd_t = 14567.15
        lab = "banana (guineo) in maintenance, 14,567.15 RD$ per tarea per year (Costos Estimados 2019, summary table PDF p. 162), the largest fruit crop by area"
    ha = rd_t * TAREAS_PER_HA
    usd = ha / FX[2019]
    v24 = usd * CPI[2019]
    if name in ("cocoa", "coffee"):
        form = "Average yearly cost over the 10-year template = (establishment + 7 x maintenance) / 10 = %.2f RD$ per tarea" % rd_t
    else:
        form = "Yearly cost %.2f RD$ per tarea" % rd_t
    return v24, "DR-004;DR-002;GEN-001", "%.2f" % rd_t, "RD$ per tarea per year", "2019", CPI[2019], \
        "Ministerio de Agricultura, %s. %s x 15.9 tareas per ha = %.1f RD$ per ha / %.4f RD$ per US$ (WDI 2019, DR-002) = %.2f US$ per ha (2019) x CPI factor %.6f = %.2f US$ per ha (2024 USD)." % (lab, form, ha, FX[2019], usd, CPI[2019], v24)


CROP = {"AG_RIC": "rice", "AG_COC": "cocoa", "AG_CAF": "coffee", "AG_FRT": "fruit"}

FAO = {}
with open(os.path.join(JOB, "GEN", "faostat_trade_unit_values.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["country"] == "DR" and r["year"] == "avg_2019_2023":
            FAO[r["model_item"]] = (float(r["unit_value_2024usd"]), r["fao_items"])
IMP = {"IMPCAF": "coffee", "IMPCARBOV": "beef", "IMPCOC": "cocoa", "IMPFRT": "fruit", "IMPLEC": "milk", "IMPRIC": "rice", "IMPSGC": "sugar"}

GS = {}
with open(os.path.join(JOB, "GEN", "gen_sector_values.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        GS[(r["tech"], r["parameter"])] = r
CEPAL_COLL = 34.22 * CPI[2010] + 12.01 * CPI[2010]
CEPAL_DISP = 20.43 * CPI[2010]
WAW_OD_HIGH = 10 * CPI[2018]
WW_SEWER = 8.168 * 1000 * CPI[2015]   # M US$ per billion m3 per year, 2024 USD (GEN-207 conversion)
WW_SEPT = 2.117 * 1000 * CPI[2015]

ASSUME = {
    ("AG_RIC", "CapitalCost"): "Rice carries a capital cost of 381.1 M US$ per Mt of annual production capacity (381 US$ per t), covering levelling, irrigation canals and machinery. At the national rice yield of 5.1 t per ha published by FAO this is about 1,950 US$ per ha; range 200 to 600 US$ per t.",
    ("AG_SGC", "CapitalCost"): "Sugar cane carries a capital cost of 0.3735 M US$ per Mt of annual production capacity (0.37 US$ per t), a token value that leaves the cane choice to the yearly costs. With FAO's national cane yield of 45.5 t per ha this is about 17 US$ per ha; range 0 to 50 US$ per t if field establishment is included.",
    ("AG_SGC", "FixedCost"): "Sugar cane has a fixed cost of 892.85 US$ per ha per year (M US$ per Mha) for field upkeep, ratoon management and overheads. The Ministry of Agriculture cost series does not cover cane, which is grown by the sugar mills; at FAO's national cane yield of 45.5 t per ha the fixed and variable costs together equal about 39 US$ per t of cane. Range 600 to 1,300 US$ per ha.",
    ("AG_SGC", "VariableCost"): "Sugar cane has a variable cost of 892.85 US$ per ha per year (M US$ per Mha) for inputs, cutting and haulage. Together with the fixed cost this equals about 39 US$ per t of cane at FAO's national yield of 45.5 t per ha; range 600 to 1,300 US$ per ha.",
    ("AGR_OTP", "FixedCost"): "Other crops (roots, tubers, pulses, vegetables and minor crops) have a fixed cost of 1,752.53 US$ per ha per year. The Ministry of Agriculture 2019 cost summary gives total costs of about 2,450 to 10,100 RD$ per tarea for these field crops, about 760 to 3,140 US$ per ha in 2019 prices, and the fixed and variable costs together (2,262.61 US$ per ha) lie inside that range; range 1,000 to 2,500 US$ per ha.",
    ("AGR_OTP", "VariableCost"): "Other crops have a variable cost of 510.08 US$ per ha per year. Together with the fixed cost (2,262.61 US$ per ha) the total lies inside the 760 to 3,140 US$ per ha range of the Ministry of Agriculture 2019 cost summary for field crops; range 300 to 1,000 US$ per ha.",
    ("GA_CARBOV", "CapitalCost"): "Beef cattle carry a capital cost of 2,690 M US$ per Mt of annual meat capacity (2,690 US$ per t of carcass), covering herd, pasture establishment and installations. FAO's national producer price of beef averages 1,759 US$ per t (2019 to 2023, real 2024 USD), so the capital cost equals about 1.5 years of output value; range 1,500 to 4,000 US$ per t.",
    ("GA_CARBOV", "FixedCost"): "Beef cattle have a fixed cost of 2,843.60 M US$ per Mt converted to a per-hectare basis in every year, for pasture upkeep, labour and veterinary care. No national cost per hectare of beef pasture is published; FAO's national producer price of beef averages 1,759 US$ per t (2019 to 2023, real 2024 USD). Range plus or minus 50 percent.",
    ("GA_CARBOV", "VariableCost"): "Beef cattle have a variable cost of 3,732.88 M US$ per Mt converted to a per-hectare basis in every year, for feed, supplements and animal health. No national cost per hectare of beef pasture is published; range plus or minus 50 percent.",
    ("GA_LEC", "CapitalCost"): "Dairy cattle carry a capital cost of 2,690 M US$ per Mt of annual milk capacity (2,690 US$ per t), covering herd, milking equipment and installations, the same value as beef cattle. FAO's national producer price of raw milk averages 473 US$ per t (2019 to 2023, real 2024 USD); range 1,500 to 4,000 US$ per t.",
    ("GA_LEC", "FixedCost"): "Dairy cattle have a fixed cost of 1,891.76 M US$ per Mt converted to a per-hectare basis in every year. The Ministry of Agriculture estimates the average cost of producing milk at 16.73 RD$ per litre in June 2019 (about 390 US$ per t in 2024 USD), but a per-hectare value needs the milk yield per hectare of pasture, which is not published; range plus or minus 50 percent.",
    ("GA_LEC", "VariableCost"): "Dairy cattle have a variable cost of 3,383.63 M US$ per Mt converted to a per-hectare basis in every year. The Ministry of Agriculture puts feed and inputs at 10.31 of the 16.73 RD$ per litre cost of milk in 2019; range plus or minus 50 percent.",
    ("AERO_PTAR", "VariableCost"): "Operating a centralized aerobic wastewater treatment plant costs 50.65 M US$ per billion m3 treated in 2018, rising to 94.85 in 2050 (0.05 to 0.09 US$ per m3) as treatment standards tighten. Published operating costs of activated-sludge plants in Latin America are about 0.05 to 0.30 US$ per m3; range in that band.",
    ("SEPT_SYST", "VariableCost"): "Operating and emptying septic systems costs 7.37 M US$ per billion m3 in 2018, falling to 2.51 in 2050 (under 0.01 US$ per m3). Faecal sludge emptying is paid by households at intervals of several years, so the yearly cost per m3 is small; range 1 to 20 M US$ per billion m3.",
    ("IMPOTP", "VariableCost"): "Imports of other agricultural products cost 1,796.37 US$ per t (M US$ per Mt). The group has no single FAOSTAT item; the national import unit values of fruit (2,235 US$ per t), vegetables (1,502) and pulses (1,289) for 2019 to 2023 in real 2024 USD bracket it; range 1,300 to 2,300 US$ per t.",
}
PEN = {
    "contam_agua": "The water-contamination externality of uncontrolled waste disposal is 35.76 per unit of waste in 2018, falling to 27.80 in 2030 and 22.40 in 2050, in the model's money unit per unit of waste emission. It values damage to water bodies from open dumps and burning in the Dominican Republic and keeps a fixed proportion to the health (2.43 times) and tourism (3.64 times) externalities; range half to double.",
    "salud_residuos": "The public-health externality of uncontrolled waste disposal is 86.84 per unit of waste in 2018, falling to 67.51 in 2030 and 54.40 in 2050. It values illness linked to open dumps and waste burning in the Dominican Republic, 2.43 times the water-contamination externality; range half to double.",
    "turismo_residuos": "The tourism externality of uncontrolled waste disposal is 130.26 per unit of waste in 2018, falling to 101.26 in 2030 and 81.61 in 2050. It values tourism revenue lost to littered coasts and dumps, which weighs heavily in the Dominican economy, 3.64 times the water-contamination externality; range half to double.",
}


def sector(c):
    tech, par = c["tech"], c["parameter"]
    cur = float(c["current_value"])
    peryear = " Same value every year." if c["projection_mode"] == "User defined" else " Flat row: base-year cell only, every year takes it."
    if par == "EmissionsPenalty":
        out(c, c["current_value"], "assumption", der="Penalty per unit of emission in that year; the published origin cannot be downloaded (listed in manual_downloads_DR.csv).", sent=PEN[tech])
        return
    if (tech, par) in ASSUME:
        out(c, c["current_value"], "assumption", der="No published value for this cell." + peryear, sent=ASSUME[(tech, par)])
        return
    if tech in IMP:
        v, items = FAO[IMP[tech]]
        s = dict(sources="GEN-201;GEN-001", sv="%.2f" % v, su="US$ per t (FAOSTAT import unit value, quantity-weighted mean 2019 to 2023, real 2024 USD)", cy="2019-2023", cpi="1.226992-1.029494")
        note = ""
        if tech == "IMPSGC":
            note = " The model item is sugar cane; cane itself is hardly traded (FAO cane unit value 2,788 US$ per t on 1.3 t per year), so the sugar item (raw plus refined, FAO 162 and 164) is used, per the GEN mapping."
        if tech == "IMPCOC":
            note = " Cocoa bean imports are small (76 t per year), so the unit value is less robust."
        sourced(c, v, s, "FAOSTAT import unit value for the Dominican Republic, item %s, quantity-weighted mean of 2019 to 2023 in real 2024 USD = %.2f US$ per t (GEN-201, GEN/faostat_trade_unit_values.csv; each year deflated with its own CPI factor). Model unit MUSD/Mt equals US$ per t.%s%s" % (items, v, note, peryear))
        return
    if tech in CROP and par in ("FixedCost", "VariableCost"):
        v24, src, sv, su, cy, cpi, der = crop_total(CROP[tech])
        other = "VariableCost" if par == "FixedCost" else "FixedCost"
        oth = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == tech and x["parameter"] == other]
        tot_cur = cur + float(oth[0]["current_value"])
        cls = classify(tot_cur, v24)
        prop = c["current_value"] if cls == "confirmed" else v24 * cur / tot_cur
        d = der + (" The source gives one total cost per ha; it is compared with the model's FixedCost + VariableCost = %.2f US$ per ha (%s) and, if replaced, split in the model's own proportion (this cell's share %.4f)." % (tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur)) + peryear
        out(c, prop, cls, src, sv, su, cy, cpi, d)
        return
    if tech in ("BLEND_NO_DCOLL", "LANDFILL"):
        same = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == tech and x["year"] == c["year"]]
        tot_cur = sum(float(x["current_value"]) for x in same)
        if tech == "BLEND_NO_DCOLL":
            v = CEPAL_COLL
            sv, lab = "34.22 + 12.01", "collection (34.22) plus transfer (12.01) US$ per t, 2010 USD"
        else:
            v = CEPAL_DISP
            sv, lab = "20.43", "final disposal 20.43 US$ per t, 2010 USD"
        cls = classify(tot_cur, v)
        prop = c["current_value"] if cls == "confirmed" else v * cur / tot_cur
        d = ("CEPAL 2016, Cuadro 6 (Latin America and the Caribbean averages): %s x CPI factor %.6f = %.2f US$ per t (2024 USD). Compared with the model's CapitalCost + VariableCost = %.3f US$ per t (%s); if replaced, split in the model's own proportion (this cell's share %.4f). What a Waste 2.0 (GEN-204, Table 5.2) gives %s US$ per t for upper-middle income countries (2024 USD)."
             % (lab, CPI[2010], v, tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur,
                "62 to 125" if tech == "BLEND_NO_DCOLL" else "25 to 81")) + peryear
        out(c, prop, cls, "GEN-206;GEN-204;GEN-001", sv, "US$ per t", "2010", CPI[2010], d)
        return
    if tech == "NO_CONTR_OD":
        s = dict(sources="GEN-204;GEN-001", sv="10", su="US$ per t (open dumping, top of the lower-middle income range 3 to 10)", cy="2018", cpi=CPI[2018])
        sourced(c, WAW_OD_HIGH, s, "What a Waste 2.0, Table 5.2, p. 105: open dumping 3 to 10 US$ per t for lower-middle income countries, not given for upper-middle income; the top of the range is used for the Dominican Republic (upper-middle income): 10 x CPI factor %.6f = %.2f US$ per t (2024 USD)." % (CPI[2018], WAW_OD_HIGH) + peryear)
        return
    if tech in ("SEWERWW", "AERO_PTAR") and par == "CapitalCost":
        sew = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == "SEWERWW" and x["parameter"] == "CapitalCost" and x["year"] == c["year"]]
        aer = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == "AERO_PTAR" and x["parameter"] == "CapitalCost" and x["year"] == c["year"]]
        tot_cur = float(sew[0]["current_value"]) + float(aer[0]["current_value"])
        cls = classify(tot_cur, WW_SEWER)
        prop = c["current_value"] if cls == "confirmed" else WW_SEWER * cur / tot_cur
        d = ("Hutton and Varughese 2016, Table E.1 (GEN-207): urban sewerage with treatment, Dominican Republic, 447.2 US$ per person served (2015 USD) / 54.75 m3 per person per year (150 L per day, GEN conversion) = 8.168 US$ per m3 per year = 8,168 M US$ per billion m3 per year x CPI factor %.6f = %.1f (2024 USD), conveyance and treatment together. Compared with the model's SEWERWW + AERO_PTAR = %.1f (%s); if replaced, split in the model's own proportion (this cell's share %.4f)."
             % (CPI[2015], WW_SEWER, tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur)) + peryear
        out(c, prop, cls, "GEN-207;GEN-001", "447.2", "US$ per person served (urban sewerage with treatment)", "2015", CPI[2015], d)
        return
    if tech == "SEPT_SYST" and par == "CapitalCost":
        s = dict(sources="GEN-207;GEN-001", sv="115.9", su="US$ per person served (urban septic tank with faecal sludge management)", cy="2015", cpi=CPI[2015])
        sourced(c, WW_SEPT, s, "Hutton and Varughese 2016, Table E.1 (GEN-207): urban septic tank with faecal sludge management, Dominican Republic, 115.9 US$ per person (2015 USD) / 54.75 m3 per person per year (150 L per day, GEN conversion) = 2,117 M US$ per billion m3 per year x CPI factor %.6f = %.1f (2024 USD); the source gives no time path, so the same value is proposed every year." % (CPI[2015], WW_SEPT))
        return
    raise KeyError((tech, par))


for c in CELLS:
    if c["model"] == "RD_ENERGY":
        vehicle(c)
    else:
        sector(c)

# Row-level coherence for multiplier series: if any multiplier cell of a trajectory row is replaced,
# every multiplier cell of that row takes the GEN value, so the written path has no jumps.
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
with open(os.path.join(CC_DIR, "proposals_DR.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(ROWS)
print(len(CELLS), len(ROWS))
