"""Build proposals_JAM.csv from cells_JAM.csv, the GEN packages and the JAM sources.

Run: python -I build_proposals_JAM.py (paths are relative to this file).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse_cop_JAM  # noqa: E402

CC_DIR = os.path.dirname(HERE)
JOB = os.path.dirname(CC_DIR)

CPI = {}
with open(os.path.join(JOB, "cpi_u.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        CPI[int(r["year"])] = float(r["factor_to_2024"])
F20, F21, F22 = CPI[2020], CPI[2021], CPI[2022]

# World Bank WDI PA.NUS.FCRF, Jamaica (JAM-005)
with open(os.path.join(JOB, "downloads", "JAM", "WB_WDI_PA.NUS.FCRF_JAM_2015_2024.json"), encoding="utf-8") as f:
    FX = {int(r["date"]): float(r["value"]) for r in json.load(f)[1] if r["value"] is not None}

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


# ---------------- UN Comtrade, Jamaica imports 2021 (JAM-004), comparison only ----------------
CT = {}
with open(os.path.join(JOB, "downloads", "JAM", "comtrade_JAM_imports_vehicles_2021.json"), encoding="utf-8") as f:
    for r in json.load(f)["data"]:
        CT[r["cmdCode"]] = (r["qty"] or 0.0, r["cifvalue"] or 0.0)


def ct_note(codes, label):
    q = sum(CT[c][0] for c in codes if c in CT)
    v = sum(CT[c][1] for c in codes if c in CT)
    return (" Comparison: UN Comtrade records Jamaica's 2021 imports of %s (HS %s) at %s US$ CIF per unit on %s units (JAM-004; CIF before Jamaican duties, taxes and margins, new and used vehicles together)."
            % (label, ", ".join(codes), format(round(v / q), ","), format(round(q), ",")))


# ---------------- national anchors ----------------
# OUR 2021 consultation document (JAM-002), Figure 6 / Table 11: total acquisition cost, US$, under the 2021 tax and duty regime
OUR_FIT, OUR_NOTE, OUR_LEAF = 34477.76, 33444.24, 48386.50
OUR_ICE = (OUR_FIT + OUR_NOTE) / 2
CAR_GSL = OUR_ICE * F21
CAR_ELE = OUR_LEAF * F21
R_CAR_DSL_GSL = atb("car", "DSL")[0] / atb("car", "GSL")[0]
R_CAR_HG_GSL = atb("car", "HG")[0] / atb("car", "GSL")[0]
CAR_DSL = CAR_GSL * R_CAR_DSL_GSL
CAR_HG = CAR_GSL * R_CAR_HG_GSL
# JUTC contract 2022 (JAM-003): 45 diesel buses US$5.4 million, 5 electric buses US$1.1 million
BUS_DSL = 5.4e6 / 45 * F22
BUS_ELE = 1.1e6 / 5 * F22
R_C8_HYD_DSL = atb("heavy_freight", "HYD")[0] / atb("heavy_freight", "DSL")[0]
R_C8_HD_DSL = atb("heavy_freight", "HD")[0] / atb("heavy_freight", "DSL")[0]
R_C8_DSL_ELE = atb("heavy_freight", "DSL")[0] / atb("heavy_freight", "ELE")[0]
# GEN-104 anchors where no Jamaican price is published
TRK_ELE = 120000 * F20
TRK_DSL = TRK_ELE * R_C8_DSL_ELE
MOT_ELE = 3000 * F20

OUR_TXT = ("Office of Utilities Regulation (OUR), EV consultation document 2021, Figure 6 (PDF p. 82): total acquisition cost under the Jamaican tax and duty regime, Honda Fit 34,477.76 and Nissan Note 33,444.24 US$ (petrol), Nissan Leaf 48,386.50 US$ (electric)")
TAX_NOTE = " The OUR price includes Jamaican import duty and taxes (see report decision on tax-inclusive light-duty prices)."

GROUP = {"TRAUT": "Techs_Auto", "TRSUV": "Techs_SUV", "TRTAX": "Techs_Taxi", "TRYLF": "Techs_Li_Freight",
         "TRYTK": "Techs_He_Freight", "TRMBS": "Techs_Buses_Micro", "TRBPU": "Techs_Buses_Pub", "TRMOT": "Techs_Motos"}
CLASS = {"TRAUT": "car", "TRSUV": "SUV", "TRTAX": "taxi", "TRYLF": "light_freight", "TRYTK": "heavy_freight",
         "TRMBS": "minibus", "TRBPU": "bus", "TRMOT": "motorcycle"}
KM_NOTE = {
    "Techs_Auto": " The proposed Ref.km.BY of this group changes from 12,000 to 20,000 km per vehicle per year, so the compiled M US$ per Gvkm changes with it (1000 x price / km).",
    "Techs_SUV": " The proposed Ref.km.BY of this group changes from 12,000 to 20,000 km per vehicle per year, so the compiled M US$ per Gvkm changes with it (1000 x price / km).",
}


def split(tech):
    for p in sorted(GROUP, key=len, reverse=True):
        if tech.startswith(p):
            return p, tech[len(p):]
    raise KeyError(tech)


with open(os.path.join(CC_DIR, "cells_JAM.csv"), encoding="utf-8") as f:
    CELLS = list(csv.DictReader(f))
CUR = {(c["model"], c["tech"], c["parameter"], c["year"]): c for c in CELLS}


def classify(cur, src, tol=0.25):
    if cur == 0:
        return "replace" if src != 0 else "confirmed"
    return "replace" if abs(src - cur) / abs(cur) > tol + 1e-12 else "confirmed"


def fmt(x):
    if isinstance(x, str):
        return x
    if abs(x) >= 100:
        return "%.2f" % x
    return "%.6g" % x


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
    return cls


# ---------------- base-year price specs ----------------
def price(value, sources, sv, su, cy, cpi, der):
    return dict(kind="price", value=value, sources=sources, sv=sv, su=su, cy=cy, cpi=cpi, der=der)


def atb_price(cls, pt, label, extra=""):
    v20, v24 = atb(cls, pt)
    return price(v24, "GEN-101;GEN-001", str(v20), "US$ per vehicle (US purchase price, ATB 2022 Mid, 2024 model year)", "2020", F20,
                 "GEN reference_price %s %s: NREL ATB 2022 Mid %s, %s US$ (2020 USD) x CPI factor %.6f = %.2f US$ (2024 USD). No Jamaican price is published for this class and powertrain; US prices exclude Jamaican import duties and taxes.%s"
                 % (cls, pt, label, format(v20, ","), F20, v24, extra))


def ratio(num, num_txt, ref, sources, sv, extra=""):
    return dict(kind="ratio", num=num, num_txt=num_txt, ref=ref, sources=sources, sv=sv, extra=extra)


SPEC = {}
SPEC["TRAUTGSL"] = price(CAR_GSL, "JAM-002;GEN-001", "34477.76; 33444.24", "US$ per vehicle (total acquisition cost, petrol compact car, Jamaica)", "2021", F21,
                         "%s. Mean of the two petrol cars = %.2f US$ (2021) x CPI factor %.6f = %.2f US$ (2024 USD).%s" % (OUR_TXT, OUR_ICE, F21, CAR_GSL, TAX_NOTE)
                         + ct_note(["870321", "870322", "870323", "870324"], "gasoline cars"))
SPEC["TRTAXGSL"] = dict(SPEC["TRAUTGSL"])
SPEC["TRAUTDSL"] = price(CAR_DSL, "JAM-002;GEN-101;GEN-001", "34477.76; 33444.24", "US$ per vehicle (total acquisition cost, petrol compact car, Jamaica)", "2021", F21,
                         "%s. Mean petrol price %.2f US$ (2021) x CPI factor %.6f = %.2f, times the ATB 2022 Mid compact car diesel to gasoline price ratio 28,600 / 23,120 = %.5f (GEN-101) = %.2f US$ (2024 USD).%s"
                         % (OUR_TXT, OUR_ICE, F21, CAR_GSL, R_CAR_DSL_GSL, CAR_DSL, TAX_NOTE) + ct_note(["870331", "870332", "870333"], "diesel cars"))
for t in ("TRAUTELE", "TRTAXELE"):
    SPEC[t] = price(CAR_ELE, "JAM-002;GEN-001", "48386.50", "US$ per vehicle (total acquisition cost, Nissan Leaf, Jamaica)", "2021", F21,
                    "%s. Electric car 48,386.50 US$ (2021) x CPI factor %.6f = %.2f US$ (2024 USD).%s" % (OUR_TXT, F21, CAR_ELE, TAX_NOTE) + ct_note(["870380"], "battery electric cars"))
SPEC["TRAUTHG"] = ratio(CAR_HG, "OUR mean petrol car price %.2f US$ (2024 USD) x ATB 2022 Mid compact hybrid to gasoline price ratio 25,600 / 23,120 = %.2f US$" % (CAR_GSL, CAR_HG),
                        "TRAUTELE", "JAM-002;GEN-101;GEN-001", "34477.76; 33444.24; 25600 / 23120", ct_note(["870340"], "gasoline hybrid cars"))
# SUV (ATB small SUV)
SPEC["TRSUVDSL"] = atb_price("SUV", "DSL", "Small SUV Conventional CI")
SPEC["TRSUVGSL"] = atb_price("SUV", "GSL", "Small SUV Conventional SI")
SPEC["TRSUVELE"] = atb_price("SUV", "ELE", "Small SUV BEV300")
# Light freight (ATB pickup)
SPEC["TRYLFDSL"] = atb_price("light_freight", "DSL", "Pickup Conventional CI", ct_note(["870421"], "diesel goods vehicles up to 5 t"))
SPEC["TRYLFGSL"] = atb_price("light_freight", "GSL", "Pickup Conventional SI", ct_note(["870431"], "gasoline goods vehicles up to 5 t"))
SPEC["TRYLFHD"] = atb_price("light_freight", "HD", "Pickup hybrid (GEN proxy for diesel hybrid)")
v20, v24 = atb("light_freight", "ELE")
SPEC["TRYLFELE"] = ratio(v24, "ATB 2022 Mid Pickup BEV300, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (format(v20, ","), F20, v24), "TRYLFDSL", "GEN-101;GEN-001", str(v20))
# Minibus (ATB Class 4 step van)
SPEC["TRMBSDSL"] = atb_price("minibus", "DSL", "Class 4 step van diesel (GEN proxy for minibus)", ct_note(["870210"], "diesel buses and minibuses for 10 or more persons"))
SPEC["TRMBSGSL"] = atb_price("minibus", "GSL", "Class 4 step van, diesel price (GEN proxy for gasoline minibus)")
v20, v24 = atb("minibus", "ELE")
SPEC["TRMBSELE"] = ratio(v24, "ATB 2022 Mid Class 4 step van BEV, %s US$ (2020 USD) x %.6f = %.2f US$ (2024 USD)" % (format(v20, ","), F20, v24), "TRMBSDSL", "GEN-101;GEN-001", str(v20))
# Public buses: national JUTC contract prices
JUTC_TXT = "JUTC fleet contract signed May 2022 (Jamaica Gleaner, 31 May 2022): 45 diesel buses valued at US$5.4 million and 5 electric buses valued at US$1.1 million"
JIS_PER_BUS = 5e9 / 170 / FX[2024]
SPEC["TRBPUDSL"] = price(BUS_DSL, "JAM-003;JAM-007;JAM-005;GEN-001", "5.4 million / 45", "US$ per vehicle (diesel bus, JUTC contract)", "2022", F22,
                         "%s. Diesel: 5,400,000 / 45 = 120,000 US$ (2022) x CPI factor %.6f = %.2f US$ (2024 USD). Comparison: the Jamaica Information Service reports 170 new JUTC buses bought for J$5 billion since 2023 (JAM-007; diesel and CNG units together), J$29.4 million per bus = %.0f US$ at the 2024 WDI rate %.2f J$ per US$ (JAM-005)."
                         % (JUTC_TXT, F22, BUS_DSL, JIS_PER_BUS, FX[2024]))
SPEC["TRBPUGSL"] = dict(SPEC["TRBPUDSL"])
SPEC["TRBPUGSL"]["der"] = SPEC["TRBPUDSL"]["der"] + " Gasoline buses take the diesel price (GEN proxy rule)."
SPEC["TRBPUELE"] = price(BUS_ELE, "JAM-003;GEN-001", "1.1 million / 5", "US$ per vehicle (electric bus, JUTC contract)", "2022", F22,
                         "%s. Electric: 1,100,000 / 5 = 220,000 US$ (2022) x CPI factor %.6f = %.2f US$ (2024 USD). National electric to diesel price ratio 1.83, against 2.04 for ATB Class 8 (GEN-101)." % (JUTC_TXT, F22, BUS_ELE))
SPEC["TRBPUHYD"] = ratio(BUS_DSL * R_C8_HYD_DSL, "JUTC diesel bus price %.2f US$ (2024 USD) x ATB 2022 Mid Class 8 FCEV to diesel price ratio 292,000 / 160,750 = %.2f US$" % (BUS_DSL, BUS_DSL * R_C8_HYD_DSL),
                         "TRBPUDSL", "JAM-003;GEN-101;GEN-001", "5.4 million / 45; 292000 / 160750")
# Heavy freight: GEN-104 electric cargo vehicle anchor with ATB Class 8 ratios
SPEC["TRYTKDSL"] = price(TRK_DSL, "GEN-104;GEN-101;GEN-001", "120000 x (160750 / 327750)", "US$ per vehicle", "2020", F20,
                         "No Jamaican heavy truck price is published. GEN-104 electric cargo vehicle price USD 120,000 (Dominican Republic electric mobility plan, PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f, times the ATB 2022 Mid Class 8 diesel to BEV price ratio 160,750 / 327,750 = %.5f (GEN-101) = %.2f US$ (2024 USD), the same anchor used for the other countries."
                         % (F20, TRK_ELE, R_C8_DSL_ELE, TRK_DSL) + ct_note(["870422", "870423"], "diesel goods vehicles over 5 t"))
SPEC["TRYTKELE"] = ratio(TRK_ELE, "GEN-104 electric cargo vehicle USD 120,000 (2020) x %.6f = %.2f US$ (2024 USD)" % (F20, TRK_ELE), "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "120000")
SPEC["TRYTKHD"] = ratio(TRK_DSL * R_C8_HD_DSL, "diesel truck price %.2f x ATB Class 8 diesel hybrid to diesel ratio 172,750 / 160,750 = %.2f US$" % (TRK_DSL, TRK_DSL * R_C8_HD_DSL), "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "172750 / 160750")
SPEC["TRYTKHYD"] = ratio(TRK_DSL * R_C8_HYD_DSL, "diesel truck price %.2f x ATB Class 8 FCEV to diesel ratio 292,000 / 160,750 = %.2f US$" % (TRK_DSL, TRK_DSL * R_C8_HYD_DSL), "TRYTKDSL", "GEN-104;GEN-101;GEN-001", "292000 / 160750")
# Motorcycles
SPEC["TRMOTELE"] = price(MOT_ELE, "GEN-104;GEN-001", "3000", "US$ per vehicle (electric motorcycle)", "2020", F20,
                         "No Jamaican retail price is published. GEN-104 electric motorcycle price USD 3,000 (PDF p. 94, Tabla 6 footnote 29) x CPI factor %.6f = %.2f US$ (2024 USD), the same anchor used for the other countries." % (F20, MOT_ELE)
                         + ct_note(["871160"], "electric motorcycles"))
SPEC["TRMOTGSL"] = dict(kind="assumption", value=2500.0,
                        sentence="A new gasoline motorcycle of the common commuter size (125 to 250 cc) costs 2,500 US$ per vehicle in Jamaica in the base year, including import duty and taxes. UN Comtrade records Jamaica's 2021 imports of motorcycles of 250 to 500 cc at about 2,390 US$ CIF per unit, and the electric motorcycle reference price of the Dominican Republic electric mobility plan is USD 3,000 (2020); range 1,500 to 4,000 US$ per vehicle.",
                        der="Flat row: base-year cell only, every year takes it. No Jamaican retail price and no GEN price exist for gasoline motorcycles. UN Comtrade 2021 (JAM-004) gives 447 US$ CIF per unit for HS 871120 (50 to 250 cc, 6,600 units) and 2,387 for HS 871130 (250 to 500 cc, 18 units); the 871120 value is too low for a complete new motorcycle (likely includes scooters and kits), so an ASSUMPTION is proposed; the current 6,496.24 is above the electric motorcycle reference.")

TRAJ_KEY = {"TRAUTELE": ("car", "ELE"), "TRAUTHG": ("car", "HG"), "TRTAXELE": ("taxi", "ELE"), "TRSUVELE": ("SUV", "ELE"),
            "TRYLFELE": ("light_freight", "ELE"), "TRYTKELE": ("heavy_freight", "ELE"), "TRYTKHYD": ("heavy_freight", "HYD"),
            "TRBPUELE": ("bus", "ELE"), "TRBPUHYD": ("bus", "HYD"), "TRMBSELE": ("minibus", "ELE")}

# ---------------- OperationalLife ----------------
OUR_LIFE = "National comparison: the Office of Utilities Regulation assumes a 15-year useful life for electric and conventional cars in Jamaica (JAM-002, PDF p. 20 and p. 82)."
LIFE = {"car": (15, "JAM-002;GEN-103", "Office of Utilities Regulation EV consultation document 2021 assumes a 15-year useful life for electric and conventional cars in Jamaica (JAM-002, PDF p. 20 and p. 82); NREL ATB 2022 light-duty vehicle life is also 15 years (GEN-103)."),
        "taxi": (15, "JAM-002;GEN-103", "Office of Utilities Regulation EV consultation document 2021 assumes a 15-year useful life for cars in Jamaica (JAM-002, PDF p. 20 and p. 82); NREL ATB 2022 light-duty life 15 years (GEN-103). Taxis run more kilometres per year, so a shorter life is plausible."),
        "SUV": (15, "GEN-103;JAM-002", "GEN operational_life for light-duty vehicles: 15 years (NREL ATB 2022, GEN-103). " + OUR_LIFE),
        "light_freight": (15, "GEN-103", "GEN operational_life for light-duty vehicles (pickup): 15 years (NREL ATB 2022, GEN-103)."),
        "minibus": (15, "GEN-103", "GEN operational_life for Class 4 vehicles (GEN minibus mapping): 15 years (NREL ATB 2022, GEN-103)."),
        "bus": (10, "GEN-104", "GEN operational_life for buses: 10 years, the theoretical vehicle life of the Dominican Republic electric mobility plan (GEN-104, PDF p. 78, footnote 11), used for the other countries; no Jamaican bus retirement age is published."),
        "heavy_freight": (10, "GEN-104", "GEN operational_life for heavy freight: 10 years (GEN-104, PDF p. 78, footnote 11), used for the other countries; no Jamaican truck retirement age is published. See the report decision on heavy-vehicle lives."),
        "motorcycle": (10, "GEN-104", "GEN operational_life for motorcycles: 10 years (GEN-104, PDF p. 78, footnote 11), used for the other countries; no Jamaican motorcycle retirement age is published.")}

# ---------------- distances ----------------
KM = {"Techs_Auto": (20000, "JAM-002", "km per year (average annual distance of an individual driver, Jamaica)",
                     "Office of Utilities Regulation EV consultation document 2021 (JAM-002, PDF p. 82): 'A distance of 20,000 km represents the annual average distance that an individual travels', used in its car life-cycle cost comparison."),
      "Techs_SUV": (20000, "JAM-002", "km per year (average annual distance of an individual driver, Jamaica)",
                    "Office of Utilities Regulation EV consultation document 2021 (JAM-002, PDF p. 82): 20,000 km per year is the annual average distance an individual travels; applied to pick-ups and jeeps in private use as to cars."),
      "Techs_Buses_Pub": (44000, "GEN-104", "km per year (buses)", "GEN annual_km: buses 44,000 km per year (Dominican Republic electric mobility plan, GEN-104, PDF p. 78, Tabla 4); no Jamaican bus distance is published."),
      "Techs_Buses_Micro": (44000, "GEN-104", "km per year (buses)", "GEN annual_km: buses 44,000 km per year (GEN-104, PDF p. 78, Tabla 4); no Jamaican minibus distance is published."),
      "Techs_Li_Freight": (9000, "GEN-104", "km per year (cargo vehicles)", "GEN annual_km: cargo vehicles 9,000 km per year (GEN-104, PDF p. 78, Tabla 4); no Jamaican light truck distance is published."),
      "Techs_Motos": (10500, "GEN-104", "km per year (motorcycles)", "GEN annual_km: motorcycles 10,500 km per year (GEN-104, PDF p. 78, Tabla 4); no Jamaican motorcycle distance is published.")}

WRITTEN = {}  # tech -> written base-year cell value (after classification)


def base_price_row(c, tech, spec, km_note, mode):
    flat = " Flat row: base-year cell only, every year takes it." if mode == "Flat" else " Base-year cell of a trajectory row: the cell holds the 2024 price and later year cells hold multipliers on it."
    if spec["kind"] == "assumption":
        cls = "assumption"
        out(c, spec["value"], cls, der=spec["der"] + km_note, sent=spec["sentence"])
        WRITTEN[tech] = spec["value"]
        return
    if spec["kind"] == "price":
        cls = sourced(c, spec["value"], spec, spec["der"] + flat + km_note)
        WRITTEN[tech] = float(c["current_value"]) if cls == "confirmed" else spec["value"]
        return
    ref = spec["ref"]
    refval = WRITTEN[ref]
    val = spec["num"] / refval
    s = dict(sources=spec["sources"], sv=spec["sv"], su="ratio of prices in 2024 USD", cy="", cpi="")
    der = ("Ratio the compiler expects: this vehicle's price (%s) divided by the written base-year cell of %s (%.2f US$, as proposed); the compiler multiplies them, giving %.2f US$ per vehicle.%s%s%s"
           % (spec["num_txt"], ref, refval, spec["num"], flat.replace("the cell holds the 2024 price", "the cell holds the 2024 ratio"), spec["extra"], km_note))
    sourced(c, val, s, der)
    WRITTEN[tech] = None


ORDER_FIRST = ["TRAUTGSL", "TRAUTELE", "TRYLFDSL", "TRYTKDSL", "TRMBSDSL", "TRBPUDSL"]


def vehicle(c):
    tech, par, mode, cm = c["tech"], c["parameter"], c["projection_mode"], c["cell_meaning"]
    if par == "Ref.km.BY":
        if tech in KM:
            v, src, su, der = KM[tech]
            sourced(c, float(v), dict(sources=src, sv=str(v), su=su, cy="", cpi=""), der)
        elif tech == "Techs_He_Freight":
            out(c, c["current_value"], "assumption",
                der="No Jamaican heavy truck distance is published. The GEN annual_km values do not fit this class: GEN-104 gives 9,000 km per year for all Dominican cargo vehicles (mostly light), and GEN-103 gives 35,942 km for a US Class 4 truck; the current value lies between them and is kept as an ASSUMPTION (departure from a plain GEN fallback, see report).",
                sent="A heavy truck in Jamaica runs 27,000 km per year, about 90 km per working day over 300 days on an island whose longest road haul is under 250 km. The Dominican Republic electric mobility plan gives 9,000 km per year for its whole cargo fleet, light vehicles included, and the NREL Annual Technology Baseline uses about 36,000 km for a US Class 4 truck; range 15,000 to 40,000 km per year.")
        else:  # taxi
            out(c, c["current_value"], "assumption", der="No Jamaican or GEN distance for taxis.",
                sent="A taxi in Jamaica runs 45,000 km per year, about 150 km per working day over 300 days. The Office of Utilities Regulation finds that electric cars pay back within five years only above about 60,000 km per year and names taxis as the users who reach such distances, while it puts a private driver at 20,000 km; range 30,000 to 60,000 km per year.")
        return
    prefix, pt = split(tech)
    cls_name = CLASS[prefix]
    if par == "OperationalLife":
        v, src, der = LIFE[cls_name]
        sourced(c, float(v), dict(sources=src, sv=str(v), su="years", cy="", cpi=""), der)
        return
    km_note = KM_NOTE.get(GROUP[prefix], "")
    if par == "FixedCost":
        if prefix == "TRMOT":
            sent = {"GSL": "Maintenance of a gasoline motorcycle costs 5.41 M US$ per Gvkm (0.0054 US$ per km, about 65 US$ per year at 12,000 km) in every year. No public cost series covers motorcycle maintenance in the Caribbean; range 3 to 20 M US$ per Gvkm.",
                    "ELE": "Maintenance of an electric motorcycle costs 1.7853 M US$ per Gvkm (about 21 US$ per year at 12,000 km) in every year, a third of the gasoline motorcycle figure, in line with the lower maintenance of electric drivetrains. Range 1 to 10 M US$ per Gvkm."}[pt]
            out(c, c["current_value"], "assumption", der="No GEN maintenance value for motorcycles; same value every year.", sent=sent)
            return
        gpt = pt if pt in ("DSL", "GSL", "LPG", "NGS", "ELE", "HYD", "HG", "HD") else "DSL"
        v20, v24 = GV[("maint", cls_name, gpt)]
        s = dict(sources="GEN-102;GEN-001", sv=str(v20), su="M US$ per Gvkm (ATB levelized maintenance and repair, US conditions)", cy="2020", cpi=F20)
        der = ("GEN maintenance_cost %s %s: %s M US$ per Gvkm (2020 USD) x CPI factor %.6f = %.3f (2024 USD)%s."
               % (cls_name, gpt, v20, F20, v24, " (Flat row: base-year cell only, every year takes it)" if mode == "Flat" else ", same value every year"))
        if cls_name in ("car", "taxi"):
            der += " National comparison: the Office of Utilities Regulation life-cycle comparison (JAM-002, Figure 6, PDF p. 82) shows a 15-year maintenance component of about 6,120 US$ for a petrol car and 1,369 US$ for the Nissan Leaf at 20,000 km per year (about 20 and 5 M US$ per Gvkm, discounted totals as read from the figure), lower than ATB."
        sourced(c, v24, s, der)
        return
    # CapitalCost
    spec = SPEC[tech]
    if cm.startswith("base-year") or cm.startswith("ratio"):
        base_price_row(c, tech, spec, km_note, mode)
        return
    y = int(c["year"])
    fam = TRAJ_KEY[tech]
    if y < 2024:
        m = 1.0
        der = "Multiplier for %d: 1.0. The GEN price_trajectory (NREL ATB 2022 Mid, %s %s) is relative to the 2024 price and starts in 2024; the base-year cell holds a 2024 price, so years before 2024 take it unchanged." % (y, fam[0], fam[1])
    elif y > 2050:
        m = TRAJ[(fam[0], fam[1], 2050)]
        der = "Multiplier for %d: the GEN price_trajectory %s %s value of 2050, %.6f (NREL ATB 2022 Mid publishes to 2050; JAM_TRANSPORT runs to 2055, so 2051 to 2055 hold the 2050 ratio flat)." % (y, fam[0], fam[1], m)
    else:
        m = TRAJ[(fam[0], fam[1], y)]
        der = "GEN price_trajectory %s %s, year %d: ratio %.6f to the own 2024 price (NREL ATB 2022 Mid, interpolated between published years); applies because the base-year cell holds a 2024 price." % (fam[0], fam[1], y, m)
    sourced(c, m, dict(sources="GEN-101", sv="%.6f" % m, su="ratio to 2024 price", cy="", cpi=""), der + km_note)


# ---------------- sector ----------------
FAO = {}
with open(os.path.join(JOB, "GEN", "faostat_trade_unit_values.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["country"] == "JAM" and r["year"] == "avg_2019_2023":
            FAO[r["model_item"]] = (float(r["unit_value_2024usd"]), r["fao_items"], float(r["import_quantity"]))
IMP = {"IMPCARBOV": "beef", "IMPCARPOL": "poultry_meat", "IMPCARPOR": "pigmeat", "IMPCER": "cereals", "IMPCNT": "coconut",
       "IMPCOF": "coffee", "IMPCON": "condiments_spices", "IMPFRT": "fruit", "IMPLEG": "legumes_pulses", "IMPMILK": "milk",
       "IMPPOT": "potatoes", "IMPVEG": "vegetables"}

COP = [r for r in parse_cop_JAM.parse("MOA_COP_2022.txt") if r["ok"]]
COP_MAP = {"AG_YAM": (("YELLOW YAM", "SWEET YAM"), "yams (yellow yam and sweet yam)"),
           "AG_POT": (("IRISH POTATO", "SWEET POTATO"), "potatoes (Irish potato and sweet potato)"),
           "AG_VEG": (("CABBAGE", "CARROT", "TOMATO", "LETTUCE", "ONION", "ESCALLION"), "vegetables (cabbage, carrot, tomato, lettuce, onion, escallion)"),
           "AG_LEG": (("RED PEAS",), "legumes (red peas, the only pulse budget)"),
           "AG_PLA": (("PLANTAIN",), "plantain"),
           "AG_FRT": (("PINEAPPLE",), "fruit (pineapple, the only fruit budget)")}
FX22 = FX[2022]


def cop_value(tech):
    crops, lab = COP_MAP[tech]
    recs = [r for r in COP if r["crop"] in crops]
    per_ha = [r["yield_kg"] * r["cop"] / 0.4 for r in recs]
    jmd = sum(per_ha) / len(per_ha)
    usd = jmd / FX22
    v24 = usd * F22
    cops = sorted(set(int(r["cop"]) for r in recs))
    der = ("Ministry of Agriculture and Fisheries, Cost of Production Estimates 2022 (JAM-006): each crop budget gives a projected marketable yield (kg) and a cost of production (J$ per kg) for 0.4 ha and one crop cycle; total operating cost per ha = yield x cost per kg / 0.4. Mean over %d budgets for %s (cost of production %s to %s J$ per kg) = %.0f J$ per ha per crop cycle / %.4f J$ per US$ (WDI 2022, JAM-005) = %.2f US$ per ha (2022) x CPI factor %.6f = %.2f US$ per ha (2024 USD). The budgets are operating costs per crop cycle (labour, inputs, tools, transport, land charge, supervision) and exclude establishment; the model area is harvested area, so one cycle per ha."
           % (len(recs), lab, format(min(cops), ","), format(max(cops), ","), jmd, FX22, usd, F22, v24))
    return v24, "%.0f" % jmd, der


GS_CEPAL_COLL = (34.22 + 12.01) * CPI[2010]
GS_CEPAL_DISP = 20.43 * CPI[2010]
WAW_OD_HIGH = 10 * CPI[2018]
WW_SEWER = 339.9 / 54.75 * 1000 * CPI[2015]   # M US$ per billion m3 per year, 2024 USD (GEN-207 conversion, Jamaica)
WW_SEPT = 88.1 / 54.75 * 1000 * CPI[2015]

UNIT_NOTE = "The unit is M US$ per Mha, which equals US$ per ha of harvested area (the model activity is area in Mha)."
CAP_SENT = {
    "AG_CER": "Cereals (maize) carry a capital cost of 0.91 US$ per ha (M US$ per Mha), a token value that leaves the crop choice to the yearly costs. The Ministry of Agriculture and Fisheries counts tools at about 30,000 J$ per ha per crop cycle (about 210 US$, 2024 USD) and publishes no establishment cost; range 0 to 1,000 US$ per ha.",
    "AG_CNT": "Coconut carries a capital cost of 8.27 US$ per ha (M US$ per Mha), a token value for a tree crop whose replanting costs several thousand US$ per ha. No Jamaican establishment cost for coconut is published; range 8 to 5,000 US$ per ha, the upper end for full replanting.",
    "AG_COF": "Coffee carries a capital cost of 24.68 US$ per ha (M US$ per Mha), a token value for a perennial crop whose establishment over the first three years costs several thousand US$ per ha. No Jamaican coffee establishment cost is published; range 25 to 8,000 US$ per ha, the upper end for full establishment.",
    "AG_CON": "Condiments and spices (ginger, hot pepper, pimento) carry a capital cost of 8.23 US$ per ha (M US$ per Mha), a token value. The Ministry of Agriculture and Fisheries publishes operating costs of about 26,000 to 51,000 US$ per ha per crop cycle for ginger and hot pepper in 2022 but no establishment cost; range 0 to 1,000 US$ per ha.",
    "AG_FRT": "Fruits carry a capital cost of 6.07 US$ per ha (M US$ per Mha), a token value for orchard and pineapple establishment. No Jamaican fruit establishment cost is published; range 6 to 5,000 US$ per ha.",
    "AG_LEG": "Legumes carry a capital cost of 122.26 US$ per ha (M US$ per Mha) for tools and land preparation equipment. The Ministry of Agriculture and Fisheries counts tools at about 30,000 J$ per ha per crop cycle (about 210 US$, 2024 USD) and publishes no establishment cost; range 0 to 1,000 US$ per ha.",
    "AG_PLA": "Plantains carry a capital cost of 547.98 US$ per ha (M US$ per Mha) for field establishment. No Jamaican establishment cost for plantain is published; the Ministry of Agriculture and Fisheries puts operating costs at about 23,000 US$ per ha per crop cycle in 2022, so establishment is a small share; range 300 to 3,000 US$ per ha.",
    "AG_POT": "Potatoes carry a capital cost of 12.78 US$ per ha (M US$ per Mha), a token value for a short-cycle crop with no establishment phase. The Ministry of Agriculture and Fisheries counts tools at about 30,000 J$ per ha per crop cycle (about 210 US$, 2024 USD); range 0 to 1,000 US$ per ha.",
    "AG_VEG": "Vegetables carry a capital cost of 49.20 US$ per ha (M US$ per Mha), a token value for short-cycle crops with no establishment phase. The Ministry of Agriculture and Fisheries counts tools at about 30,000 J$ per ha per crop cycle (about 210 US$, 2024 USD); range 0 to 1,000 US$ per ha.",
    "AG_YAM": "Yams carry a capital cost of 17.52 US$ per ha (M US$ per Mha), a token value. The Ministry of Agriculture and Fisheries counts tools at about 30,000 J$ per ha per crop cycle (about 210 US$, 2024 USD) and treats trenching and staking as operating costs; range 0 to 1,000 US$ per ha.",
    "GA_CARBOV": "Beef cattle carry a capital cost of 8.25 US$ per ha of pasture (M US$ per Mha), a token value for herd and pasture establishment. No Jamaican cost of beef production per ha is published; FAO's import unit value of beef for Jamaica averages 5,405 US$ per t (2019 to 2023, real 2024 USD). Range 8 to 2,000 US$ per ha.",
    "GA_CARPOL": "Poultry carries a capital cost of 28.67 US$ per ha (M US$ per Mha) of the area assigned to poultry, a token value for housing and equipment. No Jamaican cost of poultry production per ha is published; range plus or minus 50 percent, and up to 100 times higher if housing is counted per ha of built area.",
    "GA_CARPOR": "Pigs carry a capital cost of 16.28 US$ per ha (M US$ per Mha) of the area assigned to pigs, a token value for housing and equipment. No Jamaican cost of pig production per ha is published; range plus or minus 50 percent, and up to 100 times higher if housing is counted per ha of built area.",
    "GA_MILK": "Dairy cattle carry a capital cost of 9.38 US$ per ha of pasture (M US$ per Mha), a token value for herd, milking equipment and installations. No Jamaican cost of milk production per ha is published; range 9 to 3,000 US$ per ha.",
    "GA_OTRCAR": "Other meat animals (goats and sheep) carry a capital cost of 15.24 US$ per ha (M US$ per Mha), a token value for pens and herd. No Jamaican cost per ha is published; range 15 to 1,000 US$ per ha.",
}
OP_SENT = {
    ("AG_CER", "FixedCost"): "Cereals (maize) have a fixed cost of 4.20 US$ per ha per year (M US$ per Mha). Together with the variable cost the total is 14.27 US$ per ha, two orders of magnitude below the 9,000 to 26,000 US$ per ha per crop cycle the Ministry of Agriculture and Fisheries publishes for other field crops in 2022; a commercial maize crop costs roughly 1,000 to 3,000 US$ per ha, which is the range for the total.",
    ("AG_CER", "VariableCost"): "Cereals (maize) have a variable cost of 10.07 US$ per ha per year (M US$ per Mha). The total with the fixed cost (14.27 US$ per ha) is far below the per-ha operating costs the Ministry of Agriculture and Fisheries publishes for field crops; range for the total 1,000 to 3,000 US$ per ha.",
    ("AG_COF", "FixedCost"): "Coffee has a fixed cost of 5.50 US$ per ha per year (M US$ per Mha). Together with the variable cost the total is 23 US$ per ha, far below the yearly upkeep of a coffee farm (pruning, weeding, fertiliser and picking), which costs roughly 2,000 to 6,000 US$ per ha; that is the range for the total.",
    ("AG_COF", "VariableCost"): "Coffee has a variable cost of 17.50 US$ per ha per year (M US$ per Mha). The total with the fixed cost (23 US$ per ha) is far below the yearly cost of tending and picking coffee; range for the total 2,000 to 6,000 US$ per ha.",
}
LIVE = {"GA_CARBOV": "beef cattle", "GA_CARPOL": "poultry", "GA_CARPOR": "pigs", "GA_MILK": "dairy cattle", "GA_OTRCAR": "other meat animals (goats and sheep)"}
FAO_IMP_ITEM = {"GA_CARBOV": "beef", "GA_CARPOL": "poultry_meat", "GA_CARPOR": "pigmeat", "GA_MILK": "milk", "GA_OTRCAR": "sheep_goat_meat"}

PEN_YEARS = {}
for c in CELLS:
    if c["parameter"] == "EmissionsPenalty":
        PEN_YEARS[(c["tech"], int(c["year"]))] = float(c["current_value"])


def pen_sentence(tech):
    v21, v30, v50 = PEN_YEARS[(tech, 2021)], PEN_YEARS[(tech, 2030)], PEN_YEARS[(tech, 2050)]
    what = {"contam_agua": ("water-contamination", "damage to rivers, groundwater and coastal waters from open dumps and waste burning in Jamaica, and keeps a fixed proportion to the health (2.43 times) and tourism (3.64 times) externalities"),
            "salud_residuos": ("public-health", "illness linked to open dumps and waste burning in Jamaica, 2.43 times the water-contamination externality"),
            "turismo_residuos": ("tourism", "tourism revenue lost to littered coasts and dump fires, which weighs heavily in the Jamaican economy, 3.64 times the water-contamination externality")}[tech]
    return ("The %s externality of uncontrolled waste disposal is %.2f per unit of waste in 2021, falling to %.2f in 2030 and %.2f in 2050, in the model's money unit per unit of waste emission. It values %s; range half to double."
            % (what[0], v21, v30, v50, what[1]))


def sector(c):
    tech, par = c["tech"], c["parameter"]
    cur = float(c["current_value"])
    peryear = " Same value every year." if c["projection_mode"] == "User defined" else " Flat row: base-year cell only, every year takes it."
    if par == "EmissionsPenalty":
        out(c, c["current_value"], "assumption", der="Penalty per unit of emission in that year; the published origin (IDB) cannot be downloaded (listed in manual_downloads_JAM.csv).", sent=pen_sentence(tech))
        return
    if c["model"] == "JAM_AFOLU":
        if tech in IMP:
            v, items, q = FAO[IMP[tech]]
            s = dict(sources="GEN-201;GEN-001", sv="%.2f" % v, su="US$ per t (FAOSTAT import unit value, quantity-weighted mean 2019 to 2023, real 2024 USD)", cy="2019-2023", cpi="per year 1.226992 (2019) to 1.029494 (2023), GEN-001")
            note = ""
            if q < 100:
                note = " Imports are small (%.0f t per year), so the unit value is less robust." % q
            if tech == "IMPCER":
                note = " FAO trade aggregate 1944 includes cereal preparations; maize alone averages 315.99 US$ per t (305,456 t per year)."
            sourced(c, v, s, "FAOSTAT import unit value for Jamaica, item %s, quantity-weighted mean of 2019 to 2023 in real 2024 USD = %.2f US$ per t (GEN-201, each year deflated with its own CPI factor). Model unit MUSD/Mton equals US$ per t.%s%s" % (items, v, note, peryear))
            return
        if par == "CapitalCost":
            out(c, c["current_value"], "assumption", der=UNIT_NOTE + " No published establishment cost per ha for this activity in Jamaica." + peryear, sent=CAP_SENT[tech])
            return
        if (tech, par) in OP_SENT:
            out(c, c["current_value"], "assumption", der=UNIT_NOTE + " The Ministry of Agriculture and Fisheries 2022 cost of production estimates (JAM-006) hold no cereal or coffee budget." + peryear, sent=OP_SENT[(tech, par)])
            return
        if tech in COP_MAP:
            v24, sv, der = cop_value(tech)
            other = "VariableCost" if par == "FixedCost" else "FixedCost"
            tot_cur = cur + float(CUR[(c["model"], tech, other, c["year"])]["current_value"])
            cls = classify(tot_cur, v24)
            prop = c["current_value"] if cls == "confirmed" else v24 * cur / tot_cur
            d = (UNIT_NOTE + " " + der + " The source gives one total operating cost per ha; it is compared with the model's FixedCost + VariableCost = %.2f US$ per ha (%s, the model total is %.0f times lower) and, if replaced, split in the model's own proportion (this cell's share %.4f)."
                 % (tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", v24 / tot_cur, cur / tot_cur)) + peryear
            out(c, prop, cls, "JAM-006;JAM-005;GEN-001", sv, "J$ per ha per crop cycle (mean of budgets, computed from yield x cost per kg / 0.4 ha)", "2022", F22, d)
            return
        if tech in LIVE:
            other = "VariableCost" if par == "FixedCost" else "FixedCost"
            tot_cur = cur + float(CUR[(c["model"], tech, other, c["year"])]["current_value"])
            imp = FAO[FAO_IMP_ITEM[tech]][0]
            sent = ("%s have a %s of %s US$ per ha per year (M US$ per Mha) of the area assigned to them, for %s. Together the fixed and variable costs are %.2f US$ per ha. No Jamaican cost of %s production per ha is published (the Ministry of Agriculture and Fisheries cost of production estimates cover crops only); FAO's import unit value of the product averages %s US$ per t (2019 to 2023, real 2024 USD). Range plus or minus 50 percent."
                    % (LIVE[tech][0].upper() + LIVE[tech][1:], "fixed cost" if par == "FixedCost" else "variable cost", fmt(cur),
                       "labour, pasture or housing upkeep and veterinary care" if par == "FixedCost" else "feed, supplements and animal health",
                       tot_cur, LIVE[tech], format(round(imp), ",")))
            out(c, c["current_value"], "assumption", der=UNIT_NOTE + " No published cost per ha for this livestock activity in Jamaica." + peryear, sent=sent)
            return
        raise KeyError((tech, par))
    # JAM_WASTE
    if tech in ("BLEND_NO_DCOLL", "LANDFILL"):
        same = [x for x in CELLS if x["model"] == c["model"] and x["tech"] == tech and x["year"] == c["year"] and x["parameter"] in ("CapitalCost", "VariableCost")]
        tot_cur = sum(float(x["current_value"]) for x in same)
        if tech == "BLEND_NO_DCOLL":
            v, sv, lab = GS_CEPAL_COLL, "34.22 + 12.01", "collection (34.22) plus transfer (12.01) US$ per t, 2010 USD"
        else:
            v, sv, lab = GS_CEPAL_DISP, "20.43", "final disposal 20.43 US$ per t, 2010 USD"
        cls = classify(tot_cur, v)
        prop = c["current_value"] if cls == "confirmed" else v * cur / tot_cur
        d = ("CEPAL 2016, Cuadro 6 (Latin America and the Caribbean averages): %s x CPI factor %.6f = %.2f US$ per t (2024 USD). Compared with the model's CapitalCost + VariableCost = %.3f US$ per t (%s); if replaced, split in the model's own proportion (this cell's share %.4f). What a Waste 2.0 (GEN-204, Table 5.2) gives %s US$ per t for upper-middle income countries (2024 USD)."
             % (lab, CPI[2010], v, tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur,
                "62 to 125" if tech == "BLEND_NO_DCOLL" else "25 to 81")) + peryear
        out(c, prop, cls, "GEN-206;GEN-204;GEN-001", sv, "US$ per t", "2010", CPI[2010], d)
        return
    if tech == "NO_CONTR_OD":
        s = dict(sources="GEN-204;GEN-001", sv="10", su="US$ per t (open dumping, top of the lower-middle income range 3 to 10)", cy="2018", cpi=CPI[2018])
        sourced(c, WAW_OD_HIGH, s, "What a Waste 2.0, Table 5.2, p. 105: open dumping 3 to 10 US$ per t for lower-middle income countries, not given for upper-middle income; the top of the range is used for Jamaica (upper-middle income), as for the other countries: 10 x CPI factor %.6f = %.2f US$ per t (2024 USD)." % (CPI[2018], WAW_OD_HIGH) + peryear)
        return
    if tech in ("SEWERWW", "AERO_PTAR") and par == "CapitalCost":
        tot_cur = float(CUR[(c["model"], "SEWERWW", "CapitalCost", c["year"])]["current_value"]) + float(CUR[(c["model"], "AERO_PTAR", "CapitalCost", c["year"])]["current_value"])
        cls = classify(tot_cur, WW_SEWER)
        prop = c["current_value"] if cls == "confirmed" else WW_SEWER * cur / tot_cur
        d = ("Hutton and Varughese 2016, Table E.1 (GEN-207): urban sewerage with treatment, Jamaica, 339.9 US$ per person served (2015 USD) / 54.75 m3 per person per year (150 L per day, GEN conversion) = 6.208 US$ per m3 per year = 6,208 M US$ per billion m3 per year x CPI factor %.6f = %.1f (2024 USD), conveyance and treatment together. Compared with the model's SEWERWW + AERO_PTAR = %.1f (%s); if replaced, split in the model's own proportion (this cell's share %.4f)."
             % (CPI[2015], WW_SEWER, tot_cur, "within 25 percent, current values kept" if cls == "confirmed" else "differs by more than 25 percent", cur / tot_cur)) + peryear
        out(c, prop, cls, "GEN-207;GEN-001", "339.9", "US$ per person served (urban sewerage with treatment)", "2015", CPI[2015], d)
        return
    if tech == "SEPT_SYST" and par == "CapitalCost":
        s = dict(sources="GEN-207;GEN-001", sv="88.1", su="US$ per person served (urban septic tank with faecal sludge management)", cy="2015", cpi=CPI[2015])
        sourced(c, WW_SEPT, s, "Hutton and Varughese 2016, Table E.1 (GEN-207): urban septic tank with faecal sludge management, Jamaica, 88.1 US$ per person (2015 USD) / 54.75 m3 per person per year (150 L per day, GEN conversion) = 1,609 M US$ per billion m3 per year x CPI factor %.6f = %.1f (2024 USD); the source gives no time path, so the same value is proposed every year." % (CPI[2015], WW_SEPT))
        return
    if tech == "AERO_PTAR" and par == "VariableCost":
        v21, v50 = PEN_SAFE("AERO_PTAR")
        out(c, c["current_value"], "assumption", der="No published operating cost per m3 for Jamaican treatment plants; the row's unit label reads 'No se si aplica' and the value is read as M US$ per billion m3 treated." + peryear.replace("Same value every year.", "Each year keeps its own cell."),
            sent="Operating a centralized aerobic wastewater treatment plant costs %.2f M US$ per billion m3 treated in 2021, rising to %.2f in 2050 (0.05 to 0.09 US$ per m3) as treatment standards tighten. Published operating costs of activated-sludge plants in Latin America and the Caribbean are about 0.05 to 0.30 US$ per m3; range in that band." % (v21, v50))
        return
    if tech == "SEPT_SYST" and par == "VariableCost":
        v21, v50 = PEN_SAFE("SEPT_SYST")
        out(c, c["current_value"], "assumption", der="No published operating cost per m3 for Jamaican septic systems; the row's unit label reads 'No se si aplica' and the value is read as M US$ per billion m3." + peryear.replace("Same value every year.", "Each year keeps its own cell."),
            sent="Operating and emptying septic systems costs %.2f M US$ per billion m3 in 2021, falling to %.2f in 2050 (under 0.01 US$ per m3). Faecal sludge emptying is paid by households at intervals of several years, so the yearly cost per m3 is small; range 1 to 20 M US$ per billion m3." % (v21, v50))
        return
    raise KeyError((tech, par))


def PEN_SAFE(tech):
    v = {int(x["year"]): float(x["current_value"]) for x in CELLS if x["model"] == "JAM_WASTE" and x["tech"] == tech and x["parameter"] == "VariableCost"}
    return v[2021], v[2050]


# vehicles: reference rows first, so ratios use the written reference cells
veh = [c for c in CELLS if c["model"] == "JAM_TRANSPORT"]
first = [c for c in veh if c["tech"] in ORDER_FIRST and c["parameter"] == "CapitalCost" and c["year"] == "2021"]
idx = {id(c): i for i, c in enumerate(CELLS)}
for c in first:
    vehicle(c)
done = {id(c) for c in first}
for c in CELLS:
    if id(c) in done:
        continue
    if c["model"] == "JAM_TRANSPORT":
        vehicle(c)
    else:
        sector(c)
# restore cell-list order
key = lambda r: (r["model"], r["tech"], r["parameter"], r["year"])
pos = {(c["model"], c["tech"], c["parameter"], c["year"]): i for i, c in enumerate(CELLS)}
ROWS.sort(key=lambda r: pos[key(r)])

# Row-level coherence for multiplier series
MULT = "multiplier on the base-year value"
meaning = {(c["model"], c["tech"], c["parameter"], c["year"]): c["cell_meaning"] for c in CELLS}
rows_with_replace = {(r["model"], r["tech"], r["parameter"]) for r in ROWS
                     if meaning[key(r)] == MULT and r["change_class"] == "replace"}
for r in ROWS:
    k = (r["model"], r["tech"], r["parameter"])
    if k in rows_with_replace and meaning[key(r)] == MULT and r["change_class"] == "confirmed":
        r["proposed_value"] = fmt(float(r["source_value"]))
        r["change_class"] = "replace"
        r["derivation"] = r["derivation"].replace(
            "within 25 percent, current value kept",
            "within 25 percent, but other multiplier cells of this row differ by more than 25 percent, so the whole GEN series is proposed for the row to keep the price path coherent (row-level replacement)")

COLS = ["country", "model", "sheet", "tech", "tech_name", "parameter", "unit_introduced", "unit", "projection_mode", "year", "current_value",
        "proposed_value", "change_class", "source_ids", "source_value", "source_unit", "source_currency_year", "cpi_factor", "derivation",
        "assumption_sentence", "ao_row_at_b51f24b"]
with open(os.path.join(CC_DIR, "proposals_JAM.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(ROWS)
print(len(CELLS), len(ROWS))
