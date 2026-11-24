"""Build value_register_vehicles.csv from the dump of the vehicle cells (vr02_dump.py), the cost-sources proposals (#16),
the vehicle-price proposals (#18) and the GEN vehicle factors. Run vr02_dump.py first."""
import csv
import math
import os
import pickle
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
ROOT = r"C:\clw_align"
HUB = os.path.join(ROOT, "_LAC_HUB")
CS = os.path.join(HUB, "cost_sources_20261122T234333Z")
VP = os.path.join(HUB, "vehicle_prices_20261123T163210Z")
OUT = os.path.join(WORK, "value_register_vehicles.csv")

MODELS = {
    "CostaRica/CR_ENERGY/t1_confection": ("CR", "CR_ENERGY", "Costa Rica"),
    "DominicanRepublic/RD_ENERGY": ("DR", "RD_ENERGY", "the Dominican Republic"),
    "Guatemala/GUA_ENERGY": ("GUA", "GUA_ENERGY", "Guatemala"),
    "Honduras/HON_ENERGY": ("HON", "HON_ENERGY", "Honduras"),
    "Jamaica/JAM_TRANSPORT": ("JAM", "JAM_TRANSPORT", "Jamaica"),
}
CPI = {2020: 1.212039, 2021: 1.157652, 2022: 1.071873, 2023: 1.029494, 2024: 1.0}

# ----------------------------------------------------------------------------- inputs
dump = pd.read_csv(os.path.join(HERE, "cells_dump.csv"), dtype={"year": str})
dump = dump[dump.model.isin(MODELS)].copy()


def num(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


dump["num"] = pd.Series([num(v) for v in dump["value"]], index=dump.index, dtype=object)
dump["formula"] = dump["formula"].fillna("")

p16 = []
for cc in ["CR", "DR", "GUA", "HON", "JAM"]:
    d = pd.read_csv(os.path.join(CS, cc, f"proposals_{cc}.csv"), dtype={"year": str})
    p16.append(d)
p16 = pd.concat(p16)
p16["year"] = p16["year"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
P16 = {(r.model, r.tech, r.parameter, r.year): r for r in p16.itertuples()}
P16_any = {}
for r in p16.itertuples():
    P16_any.setdefault((r.model, r.tech, r.parameter), r)

p18 = {}
for cc in ["DR", "GUA"]:
    d = pd.read_csv(os.path.join(VP, cc, f"proposals_{cc}.csv"), dtype={"year": str})
    for r in d.itertuples():
        p18[(r.model, r.tech, str(r.year))] = r
cls18 = {}
for cc in ["CR", "DR", "GUA", "HON", "JAM"]:
    d = pd.read_csv(os.path.join(VP, cc, f"class_prices_{cc}.csv"))
    for r in d.itertuples():
        cls18[(r.model, r.tech)] = r

gen = pd.read_csv(os.path.join(CS, "GEN", "gen_vehicle_factors.csv"))
REF101 = {(r.vehicle_class, r.powertrain): r.value_2024usd for r in gen[(gen.item == "reference_price") & (gen.source_id == "GEN-101")].itertuples()}
TRAJ = {(r.vehicle_class, r.powertrain, int(r.year)): r.value for r in gen[gen.item == "price_trajectory"].itertuples()}

groups = {}
for m in MODELS:
    g = pickle.load(open(os.path.join(ROOT, m, "A1_Outputs", "A-O_Fleet_Groups.pickle"), "rb"))
    for k, v in g.items():
        for t in v:
            groups[(m, t)] = k

# ----------------------------------------------------------------------------- vocabulary
PT_WORD = {"HYBDSL": "hybrid diesel", "HYBGSL": "hybrid gasoline", "PHD": "plug-in hybrid diesel",
           "PHG": "plug-in hybrid gasoline", "HD": "hybrid diesel", "HG": "hybrid gasoline", "HYD": "fuel cell",
           "ELE": "battery electric", "DSL": "diesel", "GSL": "gasoline", "LPG": "LPG", "NGS": "natural gas",
           "NGV": "natural gas", "Flex_Fuel": "flex-fuel", "FOI": "fuel oil", "KER": "kerosene"}
PT_GEN = {"HYBDSL": "HD", "HYBGSL": "HG", "NGV": "NGS", "FOI": "DSL", "KER": "DSL"}
CLASS_PREFIX = [  # (prefix, class word, gen class, kind)
    ("TRNBUS", "bus", "bus", "bus"), ("TRNMIC", "minibus", "minibus", "road"), ("TRNTAX", "taxi", "taxi", "road"),
    ("TRNMOT", "motorcycle", None, "road"), ("TRNSED", "car", "car", "road"), ("TRNSUV", "SUV", "SUV", "road"),
    ("TRNFREHEA", "heavy truck", "heavy_freight", "road"), ("TRNFRELIG", "light truck", "light_freight", "road"),
    ("TRNPASRAI", "passenger train", None, "other"), ("TRNFRERAI", "freight train", None, "other"),
    ("TRAUT", "car", "car", "road"), ("TRTAX", "taxi", "taxi", "road"), ("TRMOT", "motorcycle", None, "road"),
    ("TRSUV", "SUV", "SUV", "road"), ("TRBPU", "public bus", "bus", "bus"), ("TRBTUR", "tourism bus", "bus", "bus"),
    ("TRBPR", "private bus", "bus", "bus"), ("TRMBS", "minibus", "minibus", "road"),
    ("TRYLF", "light truck", "light_freight", "road"), ("TRYTK", "heavy truck", "heavy_freight", "road"),
    ("TRXTTEL", "cable car", None, "other"), ("TRXTRAIFRE", "freight train", None, "other"),
    ("TRXTRAI", "passenger train", None, "other"), ("TRXBUSEFI", "rapid transit bus", None, "other"),
    ("TRAV", "aircraft", None, "other"), ("TRMAMFRE", "freight vessel", None, "other"),
    ("TRMAR", "passenger vessel", None, "other"),
]


def tech_info(model, tech):
    cc = MODELS[model][0]
    for pre, word, gcls, kind in CLASS_PREFIX:
        if tech.startswith(pre):
            suf = tech[len(pre):]
            break
    else:
        raise ValueError(tech)
    if word == "SUV" and cc in ("HON", "JAM"):
        word = "pick-up or jeep"
    ptw = PT_WORD.get(suf, suf)
    ptg = PT_GEN.get(suf, suf)
    return dict(cls=word, gcls=gcls, kind=kind, suf=suf, ptw=ptw, ptg=ptg)


def fmt(x, nd=0):
    if x is None:
        return ""
    if nd == 0:
        return f"{x:,.0f}"
    return f"{x:,.{nd}f}"


def pct(a, b):
    """how far a sits from b, in words"""
    r = a / b - 1
    if abs(r) < 0.005:
        return "equal to"
    return f"{abs(r) * 100:.0f} percent {'above' if r > 0 else 'below'}"


def outval(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if float(v).is_integer():
        return str(int(v))
    return repr(float(v))


# ----------------------------------------------------------------------------- distances (rule 4)
KM_GROUP_WORD = {"TRNMIC": "minibus", "TRNBUS": "bus", "TRNTAX": "taxi", "TRNPASRAI": "passenger train",
                 "TRNMOT": "motorcycle", "TRNSED": "car", "TRNSUV": "SUV", "TRNFREHEA": "heavy truck",
                 "TRNFRERAI": "freight train", "TRNFRELIG": "light truck", "Techs_Auto": "car",
                 "Techs_Motos": "motorcycle", "Techs_SUV": "SUV", "Techs_Taxi": "taxi", "Techs_Buses_Pub": "public bus",
                 "Techs_Buses_Micro": "minibus", "Techs_Buses_Tur": "tourism bus", "Techs_Buses_Pri": "private bus",
                 "Techs_Telef": "cable car cabin", "Techs_Trains": "passenger train", "Techs_Bus_Efi": "rapid transit bus",
                 "Techs_He_Freight": "heavy truck", "Techs_Li_Freight": "light truck", "Techs_Maritime": "passenger vessel",
                 "Techs_Maritime_Freight": "freight vessel", "Techs_Aviation": "aircraft", "Techs_Rail": "train"}
GEN104_P78 = "PDF p. 78, Tabla 4, column Intensidad de uso (km/ano)"
# decisions: (model short, group) -> (after, source_id, page, derivation)
KM_RULE = {
    ("DR", "Techs_Auto"): (7500, "GEN-104", GEN104_P78, "National figure: automobiles and jeeps 7,500 km per year in the national electric mobility plan; equal to the value, which stays."),
    ("DR", "Techs_SUV"): (7500, "GEN-104", GEN104_P78, "National figure: automobiles and jeeps 7,500 km per year in the national electric mobility plan; equal to the value, which stays."),
    ("DR", "Techs_Motos"): (10500, "GEN-104", GEN104_P78, "National figure: motorcycles 10,500 km per year in the national electric mobility plan; equal to the value, which stays."),
    ("DR", "Techs_Buses_Pub"): (44000, "GEN-104", GEN104_P78, "National figure: buses (autobuses) 44,000 km per year in the national electric mobility plan; replaces 33,000."),
    ("DR", "Techs_Buses_Tur"): (44000, "GEN-104", GEN104_P78, "National figure: buses (autobuses) 44,000 km per year in the national electric mobility plan; replaces 33,000."),
    ("DR", "Techs_Buses_Micro"): (44000, "GEN-104", GEN104_P78, "National figure: buses (autobuses) 44,000 km per year in the national electric mobility plan; equal to the value, which stays."),
    ("DR", "Techs_Li_Freight"): (9000, "GEN-104", GEN104_P78, "National figure: cargo vehicles (carga) 9,000 km per year in the national electric mobility plan; equal to the value, which stays."),
    ("DR", "Techs_He_Freight"): (9000, "GEN-104", GEN104_P78, "National figure: cargo vehicles (carga) 9,000 km per year in the national electric mobility plan; equal to the value, which stays."),
    ("JAM", "Techs_Auto"): (20000, "JAM-002", "printed p. 82", "National figure: the Office of Utilities Regulation consultation document (2021) states 20,000 km as the annual average distance an individual travels; replaces 12,000."),
    ("JAM", "Techs_SUV"): (20000, "JAM-002", "printed p. 82", "National figure for private light vehicles: the Office of Utilities Regulation consultation document (2021) states 20,000 km as the annual average distance an individual travels; applied to pick-ups and jeeps in private use as to cars; replaces 12,000."),
    ("CR", "TRNBUS"): (58999, "CR-002", "PDF p. 83, table of assumptions (60,000 km per year, urban buses); CR-001 Cuadro A18, PDF p. 204 (45,000 km plus 10 percent)", "National figures: CEPAL (2024) uses 60,000 km per year for urban buses; the value 58,999 sits 1.7 percent below it and 19 percent above the 49,500 km of CEPAL (2022) for concession buses, so it stays."),
    ("GUA", "Techs_He_Freight"): (9000, "GEN-104", GEN104_P78, "Class value of a cited source: cargo vehicles (carga) 9,000 km per year in the Dominican Republic national electric mobility plan, the figure behind the heavy-truck distance of the Dominican and Honduran models; replaces 50,400 (equal to the bus distance)."),
    ("HON", "Techs_Buses_Tur"): (44000, "GEN-104", GEN104_P78, "Class value of a cited source: buses (autobuses) 44,000 km per year in the Dominican Republic national electric mobility plan; replaces 7,500 (equal to the car distance)."),
}
KM_CHECK = {  # assumption sentence pieces: class -> comparison text
    "car": "The Dominican Republic national electric mobility plan uses 7,500 km per year for automobiles and jeeps and the NREL Annual Technology Baseline 2022 uses 19,108 km per year for a new light-duty vehicle",
    "SUV": "The Dominican Republic national electric mobility plan uses 7,500 km per year for automobiles and jeeps and the NREL Annual Technology Baseline 2022 uses 19,108 km per year for a new light-duty vehicle",
    "taxi": "A taxi in daily service runs several times the distance of a private car: the Dominican Republic national electric mobility plan uses 7,500 km per year for private automobiles and 44,000 km per year for buses",
    "motorcycle": "The Dominican Republic national electric mobility plan uses 10,500 km per year for motorcycles",
    "bus": "The Dominican Republic national electric mobility plan uses 44,000 km per year for buses and CEPAL (2024) uses 60,000 km per year for urban buses in Costa Rica",
    "minibus": "The Dominican Republic national electric mobility plan uses 44,000 km per year for buses and the NREL Annual Technology Baseline 2022 implies 35,942 km per year for a Class 4 van",
    "light truck": "The Dominican Republic national electric mobility plan uses 9,000 km per year for all cargo vehicles and the NREL Annual Technology Baseline 2022 uses 19,108 km per year for a light-duty pickup",
    "heavy truck": "The Dominican Republic national electric mobility plan uses 9,000 km per year for all cargo vehicles, most of them light",
}
KM_REF = {"car": 7500, "SUV": 7500, "taxi": None, "motorcycle": 10500, "bus": 44000, "minibus": 44000,
          "light truck": 9000, "heavy truck": 9000}


def km_class(word):
    if word in ("public bus", "tourism bus", "private bus", "bus"):
        return "bus"
    return word


rows = []
km_after = {}   # (model, group) -> after km
km_before = {}
for r in dump[dump.parameter == "Ref.km.BY"].itertuples():
    m = r.model
    cc, short, country = MODELS[m]
    if r.num is None:
        continue
    grp = r.tech
    if not any(groups.get((m, t)) == grp for (mm, t) in groups if mm == m):
        continue
    word = KM_GROUP_WORD.get(grp, grp)
    before = r.num
    km_before[(m, grp)] = before
    rule = KM_RULE.get((cc, grp))
    src = page = sent = ""
    if rule:
        after, src, page, der = rule
    else:
        after = before
        kc = km_class(word)
        if before == 1:
            der = "Placeholder distance of 1 km: the activity of this group is not counted in vehicle-km, so the distance enters no price conversion; value stays."
            sent = (f"The {word} group uses a distance of 1 km per vehicle per year in {country}, a unit placeholder, because its "
                    f"activity and costs are counted per passenger-km or tonne-km and no conversion from vehicles applies.")
        elif kc in KM_CHECK:
            der = "No national figure for this class; value stays as an assumption."
            ref = KM_REF.get(kc)
            chk = KM_CHECK[kc]
            if ref:
                chk += f"; the value sits {pct(before, ref)} the plan figure"
            lo = min(before, ref) if ref else None
            hi = max(before, ref) if ref else None
            rng = f" The range is {fmt(lo)} to {fmt(hi)} km per year." if ref and lo != hi else ""
            sent = (f"A {word} in {country} runs {fmt(before)} km per year in the base year, the distance that sets how many "
                    f"vehicles a unit of transport demand needs and so the capital cost per vehicle-km. {chk}.{rng}")
        else:
            der = "Non-road or special group; value stays as an assumption."
            sent = (f"A {word} in {country} runs {fmt(before)} km per year in the base year, a value that converts its "
                    f"capacity between vehicles and vehicle-km; its capital cost is zero or entered per vehicle-km, so the distance "
                    f"does not change a price.")
    km_after[(m, grp)] = after
    rows.append(dict(model=m, file=r.file, sheet=r.sheet, tech=grp, parameter="Ref.km.BY", year="",
                     before=outval(before), after=outval(after), unit="km per vehicle per year (base year)",
                     source_id=src, page=page, derivation=der + f" Cell {r.coord}.", assumption_sentence=sent,
                     range_low="", range_high=""))


def km_of(m, tech, which="after"):
    g = groups[(m, tech)]
    return (km_after if which == "after" else km_before).get((m, g))


# ----------------------------------------------------------------------------- price anchors (rule 1)
JAM003_DSL = 120000 * CPI[2022]
JAM003_ELE = 220000 * CPI[2022]
CR001_ARESEP = 127500 * CPI[2020]
CR001_BYD = 400000 * CPI[2020]
GEN104_EBUS = 360000 * CPI[2020]
ATB8 = {"DSL": 1.0, "GSL": 1.0, "LPG": 1.0, "NGS": 1.0, "HD": 172750 / 160750, "PHD": 254500 / 160750,
        "HYD": 292000 / 160750}

CR001_DSL = [(100000, "Cuadro 7, note e (CAF 2019: diesel bus about USD 100,000), PDF p. 58"),
             (127500, "PDF p. 110 (ARESEP ceiling price of an interurban diesel bus, CRC 74,087,835 = USD 127,500)"),
             (150000, "Cuadro 7 (Grutter Consulting, diesel bus USD 150,000), PDF p. 58"),
             (155000, "Cuadro 7 (CAF; Creara, diesel bus USD 155,000), PDF p. 58")]
CR001_ELE = [(137000, "Cuadro 7 (ARESEP, electric bus USD 137,000), PDF p. 58"),
             (220000, "Cuadro 7 (Grutter Consulting, electric bus USD 220,000), PDF p. 58"),
             (287000, "Cuadro 7 (QEV, electric bus USD 287,000), PDF p. 58"),
             (315500, "Cuadro 7 (BYD, electric bus USD 315,500), PDF p. 58"),
             (400000, "PDF p. 57 (BYD K9G 12 m electric bus USD 400,000)"),
             (432000, "Cuadro 7 (CAF, electric bus USD 432,000), PDF p. 58")]
CR001_HYB = [(290000, "Cuadro 7 (Creara, hybrid bus USD 290,000), PDF p. 58")]


def anchors_for(cc, info):
    """list of (source_id, figure nominal US$, page, words)"""
    k, pt, cls = info["kind"], info["ptg"], info["cls"]
    out = []
    if cc == "CR" and k == "bus":
        lst = {"DSL": CR001_DSL, "LPG": CR001_DSL, "ELE": CR001_ELE, "HD": CR001_HYB}.get(pt, [])
        out = [("CR-001", a, p, "the CEPAL (2022) study of bus fleet renewal in Costa Rica") for a, p in lst]
    if cc in ("DR", "HON", "GUA"):
        p94 = "PDF p. 94, Tabla 6 footnote 29"
        w = "the Dominican Republic national electric mobility plan (2020)"
        if pt == "ELE" and cls in ("car", "taxi"):
            out.append(("GEN-104", 30000, p94, w))
        if pt == "ELE" and k == "bus":
            out.append(("GEN-104", 360000, p94, w))
        if pt == "ELE" and cls == "heavy truck":
            out.append(("GEN-104", 120000, p94, w))
        if pt == "ELE" and cls == "motorcycle":
            out.append(("GEN-104", 3000, p94, w))
        if cls in ("car", "taxi") and pt in ("GSL", "DSL", "LPG", "NGS", "Flex_Fuel"):
            out.append(("GEN-104", 20001, "PDF p. 72 (average price of a new conventional vehicle)", w))
    if cc == "JAM":
        if k == "bus" and pt in ("DSL", "GSL", "LPG"):
            out.append(("JAM-003", 120000, "article body, paragraph 2 (45 diesel buses for US$5.4 million)", "the 2022 JUTC bus contract reported by the Gleaner"))
        if k == "bus" and pt == "ELE":
            out.append(("JAM-003", 220000, "article body, paragraph 2 (5 electric buses for US$1.1 million)", "the 2022 JUTC bus contract reported by the Gleaner"))
        if cls in ("car", "taxi") and pt in ("GSL", "DSL"):
            out.append(("JAM-002", 34477.76, "Figure 6, printed p. 82 (Honda Fit, total acquisition cost with duties and taxes)", "the Office of Utilities Regulation consultation document (2021)"))
            out.append(("JAM-002", 33444.24, "Figure 6, printed p. 82 (Nissan Versa Note, total acquisition cost with duties and taxes)", "the Office of Utilities Regulation consultation document (2021)"))
        if cls in ("car", "taxi") and pt == "ELE":
            out.append(("JAM-002", 48386.50, "Figure 6, printed p. 82 (Nissan Leaf, total acquisition cost with duties and taxes)", "the Office of Utilities Regulation consultation document (2021)"))
    return out


def price_range(m, tech, info):
    """(low, high, low_text, high_text) in 2024 US$ per vehicle"""
    cc = MODELS[m][0]
    k, pt, cls, gcls = info["kind"], info["ptg"], info["cls"], info["gcls"]
    if k == "bus":
        if pt == "ELE":
            hi, hit = (CR001_BYD, "price of a new BYD K9G electric bus in Costa Rica") if cc == "CR" else \
                (GEN104_EBUS, "electric bus price in the Dominican Republic national electric mobility plan")
            return JAM003_ELE, hi, "price of a new electric bus in the 2022 Jamaica Urban Transit Company contract", hit
        f = ATB8.get(pt, 1.0)
        tail = "" if f == 1.0 else f" times the NREL ATB 2022 Class 8 {info['ptw']} to diesel price ratio {f:.4f}"
        return (JAM003_DSL * f, CR001_ARESEP * f,
                "price of a new diesel bus in the 2022 Jamaica Urban Transit Company contract" + tail,
                "ARESEP ceiling price of a new interurban diesel bus in Costa Rica" + tail)
    c18 = cls18.get((MODELS[m][1], tech))
    if tech == "TRYTKFOI":
        c18 = cls18.get((MODELS[m][1], "TRYTKDSL"))
    if c18 is None:
        return None, None, "", ""
    low = float(c18.base_price_usd2024)
    lowt = "average customs value of imported new and used vehicles of the class, 2019 to 2023"
    if cls == "motorcycle":
        return low, 3000 * CPI[2020], lowt, "price of a new electric motorcycle in the Dominican Republic national electric mobility plan"
    hi = REF101.get((gcls, pt)) or REF101.get((gcls, "DSL"))
    return low, hi, lowt, f"NREL ATB 2022 price of a new {info['ptw']} {cls} in the United States"


# ----------------------------------------------------------------------------- CapitalCost (rule 1)
cap = dump[dump.parameter == "CapitalCost"].copy()
cap["yr"] = cap.year.astype(int)
by_year = cap.groupby("model").yr.min().to_dict()
raw_by = {(r.model, r.tech): r.num for r in cap.itertuples() if r.yr == by_year[r.model]}
BROKEN = {("GUA", "TRAUTHG"), ("GUA", "TRAUTPHG"), ("DR", "TRYLFNGS")}
empty_skipped = {"CapitalCost": 0, "FixedCost": 0}
cr_checks = []


def ref_of(unit_intro):
    mm = re.match(r"Relative to (\S+)", str(unit_intro))
    return mm.group(1) if mm else None


def by_price(m, tech, cell_by, unit_intro):
    ref = ref_of(unit_intro)
    if ref:
        rv = raw_by.get((m, ref))
        return None if rv is None or cell_by is None else rv * cell_by
    return cell_by


tech_sent = {}
for (m, tech), g in cap.groupby(["model", "tech"], sort=False):
    cc, short, country = MODELS[m]
    info = tech_info(m, tech)
    g = g.sort_values("yr")
    ui = g.unit_introduced.iloc[0]
    unit_c = g.unit.iloc[0]
    mode = g.projection_mode.iloc[0]
    by = by_year[m]
    vals = {r.yr: r.num for r in g.itertuples()}
    km_b = km_of(m, tech, "before")
    low, high, lowt, hight = price_range(m, tech, info)
    is_cr_price = cc == "CR" and "vehicle" in str(ui) and km_b and km_b > 1
    ref = ref_of(ui)
    # price per vehicle now (base year; 2024 for CR)
    if is_cr_price:
        p_now = (vals.get(2024) or 0) * km_b / 1000
        p_2050 = (vals.get(2050) or 0) * km_b / 1000
    else:
        p_now = by_price(m, tech, vals.get(by), ui)
        p_2050 = None
    # multipliers of trajectory rows
    traj = "relative to BY" in str(mode)
    m2030 = vals.get(2030) if traj else None
    m2050 = vals.get(2050) if traj else None
    broken = (cc, tech) in BROKEN
    # new values for broken rows
    new_ui = None
    if broken:
        p_new_by = None
        r18 = p18.get((short, tech, str(by)))
        new_ui = r18.unit_introduced_proposed
        nref = ref_of(new_ui)
        p_new_by = raw_by.get((m, nref)) * float(r18.proposed_value)
    # citation
    cite = None
    if p_now and p_now > 0 and not broken:
        best = None
        for sid, a, page, words in anchors_for(cc, info):
            d = abs(p_now / a - 1)
            if d <= 0.25 and (best is None or d < best[0]):
                best = (d, sid, a, page, words)
            if d <= 0.25 and "ARESEP ceiling" in page:  # the reference price named for Costa Rica buses wins
                best = (-1, sid, a, page, words)
                break
        cite = best
    # sentence (tech level)
    desc = f"{info['ptw']} {info['cls']}"
    lowshort, highshort = lowt, hight
    rng = ""
    if low and high:
        rng = f" The range is {fmt(low)} to {fmt(high)} US$ per vehicle in 2024 US$, from the {lowt} to the {hight}."
    path = ""
    if traj and m2030 is not None and m2050 is not None:
        gk = (info["gcls"] if info["gcls"] else "car", info["ptg"])
        atb50 = TRAJ.get((gk[0], gk[1], 2050))
        path = (f", falling to {m2030 * 100:.0f} percent of that price by 2030 and {m2050 * 100:.0f} percent by 2050"
                + (f" (NREL ATB 2022 Mid trajectory: {atb50 * 100:.0f} percent of the 2024 price by 2050)" if atb50 else ""))
    elif is_cr_price and p_2050:
        path = f" and {fmt(p_2050)} US$ in 2050"
    sent = ""
    if info["kind"] == "other" or (p_now is not None and p_now == 0 and not low):
        if p_now in (None, 0):
            sent = (f"The {info['cls']} ({info['ptw']}) carries no capital cost per vehicle in {country}, because the mode is "
                    f"represented by its fuel use only and its vehicles are not chosen by cost.")
        else:
            sent = (f"A {desc} costs {fmt(p_now)} US$ per vehicle-km of yearly capacity in {country}, a cost entered per unit "
                    f"of activity rather than per vehicle.")
    elif broken:
        pass
    elif cite:
        sent = ""
    elif p_now is not None:
        chk = []
        if low:
            chk.append(f"{pct(p_now, low)} the {lowshort} ({fmt(low)} US$ of 2024)")
        if high:
            chk.append(f"{pct(p_now, high)} the {highshort} ({fmt(high)} US$ of 2024)")
        anc = anchors_for(cc, info)
        if anc:
            sid, a, page, words = min(anc, key=lambda x: abs(p_now / x[1] - 1))
            if not (high and abs(a * CPI[2020] - high) < 1):
                chk.append(f"{pct(p_now, a)} the {fmt(a)} US$ printed in {words}")
        rel = ""
        if ref and not is_cr_price:
            rel = f" ({vals.get(by):.4g} times the {tech_info(m, ref)['ptw']} {tech_info(m, ref)['cls']})"
        if is_cr_price:
            when = "in 2024"
        elif traj:
            when = "in the base year"
        else:
            when = "in every year"
        reason = ("a pre-tax price between the customs value of imported new and used vehicles and the price of a new one, "
                  "since the fleet is renewed mainly by imports")
        if info["kind"] == "bus":
            reason = "a pre-tax price of a new bus"
        rng_s = f"; range {fmt(low)} to {fmt(high)} US$ per vehicle (2024 US$)" if low and high else ""
        first = f"A {desc} in {country} costs {fmt(p_now)} US$ per vehicle {when}{rel}{path}, {reason}."
        if chk:
            last = ", ".join(chk[:-1]) + (" and " if len(chk) > 1 else "") + chk[-1]
            sent = f"{first} It sits {last}{rng_s}."
        else:
            sent = first + (f" The range is {fmt(low)} to {fmt(high)} US$ per vehicle (2024 US$)." if rng_s else "")
    tech_sent[(m, tech)] = sent
    if is_cr_price:
        cr_checks.append(dict(tech=tech, km=km_b, p2024=p_now, low=low, high=high))
    # rows
    for r in g.itertuples():
        y = r.yr
        if r.num is None and not r.formula:
            empty_skipped["CapitalCost"] += 1
            continue
        before = r.formula if r.formula else r.num
        after = before
        src = page = ""
        cellkind = ("base-year price" if (y == by and not ref) else
                    ("ratio to the base-year price of " + ref if y == by else
                     ("multiplier on the base-year price" if traj else "unused year cell of a Flat row")))
        if is_cr_price:
            cellkind = "price of the year"
        der = ""
        unit = f"cell: {ui} ({cellkind}; compiled to {unit_c}); range: 2024 US$ per vehicle"
        if is_cr_price:
            after = r.num * km_b / 1000
            der = (f"Re-entered as the price per vehicle: {r.num:.6g} x {fmt(km_b)} km per vehicle-year / 1000 = {after:,.2f} US$ "
                   f"per vehicle; the compiler divides by the distance once (1000 x price / km), so the compiled cost stays "
                   f"{r.num:.6g} M US$ per Gvkm, which a double division had cut to {r.num / km_b * 1000:.4g}.")
            if r.formula:
                der += f" The cell held the formula {r.formula} (repeats the previous year); the number is written instead."
            unit = f"cell: US$ / vehicle (price of the year; compiled to {unit_c}); range: 2024 US$ per vehicle"
        elif broken:
            r18 = p18[(short, tech, str(y))]
            after = float(r18.proposed_value)
            if y == by:
                nref = ref_of(new_ui)
                der = (f"Value proposed for this cell by the vehicle-price proposals: ratio {after} = import price of the vehicle "
                       f"({fmt(float(cls18[(short, tech)].base_price_usd2024))} US$) / import price of {nref} "
                       f"({fmt(float(cls18[(short, nref)].base_price_usd2024))} US$), both 2024 US$; the compiler multiplies it by the "
                       f"base-year cell of {nref} as it stands ({fmt(raw_by.get((m, nref)))} US$), giving {fmt(p_new_by)} US$ per vehicle.")
                if new_ui != ui:
                    der += (f" The row label changes from '{ui}' to '{new_ui}' (separate row of this table, column Unit.Introduced); "
                            f"with the old label the compiler would multiply by the ratio held in {ref} and the price would stay near zero.")
                if before and isinstance(before, float) and before > 1000:
                    der += f" The cell held a price ({fmt(before)} US$) where a ratio belongs, so the compiler multiplied two prices."
                src = "COMTRADE-JAM"
                page = (f"Jamaica imports by HS line as reported to UN Comtrade: {tech} {cls18[(short, tech)].detail}; "
                        f"{nref} {cls18[(short, nref)].detail}")
            else:
                der = (f"Proposed value of the vehicle-price proposals for this cell: multiplier {after} on the base-year price "
                       f"(NREL ATB 2022 Mid path relative to 2024; years before 2024 take 1).")
                src, page = "GEN-101", "vehicles.csv, scenario Mid, column vehicle_cost(2020$)"
        else:
            if r.formula:
                der = f"Cell holds the formula {r.formula} (value {r.num:.6g}); formula and value stay."
            else:
                der = "Value stays."
            if cite and (y == by or is_cr_price):
                pass
        if cite and not broken:
            d, sid, a, pg, words = cite
            src, page = sid, pg
            der += (f" Price per vehicle {fmt(p_now)} US$ ({'2024' if is_cr_price else 'base year'}) sits {pct(p_now, a)} the "
                    f"{fmt(a)} US$ in {words}, within 25 percent.")
            if is_cr_price and y != 2024:
                der += " Later years follow the price path of the row."
        rs = tech_sent[(m, tech)]
        if broken:
            pr = p_new_by
            nm = "hybrid gasoline car" if tech == "TRAUTHG" else ("plug-in hybrid gasoline car" if tech == "TRAUTPHG" else "natural gas light truck")
            refw = {"TRAUTDSL": "diesel car", "TRYLFDSL": "diesel light truck"}[ref_of(new_ui)]
            rs = (f"A {nm} costs {fmt(pr)} US$ per vehicle in the base year in {country}, {float(p18[(short, tech, str(by))].proposed_value):.4f} times "
                  f"the {refw}, the ratio of the average customs values of the two classes in Jamaica's imports of 2019 to 2021 "
                  f"(new and used vehicles), with later prices on the NREL ATB 2022 Mid trajectory. The price sits {pct(pr, low)} the "
                  f"average customs value of the class ({fmt(low)} US$ of 2024) and {pct(pr, high)} the NREL ATB 2022 price of a new "
                  f"vehicle of the class ({fmt(high)} US$ of 2024); range {fmt(low)} to {fmt(high)} US$ per vehicle.")
        rows.append(dict(model=m, file=r.file, sheet=r.sheet, tech=tech, parameter="CapitalCost", year=str(y),
                         before=outval(before), after=outval(after), unit=unit, source_id=src, page=page,
                         derivation=(der + f" Cell {r.coord}.").strip(),
                         assumption_sentence=("" if (cite and not broken and not rs) else rs),
                         range_low=fmt(low, 0).replace(",", "") if low else "",
                         range_high=fmt(high, 0).replace(",", "") if high else ""))
    if broken and new_ui != ui:
        r0 = g.iloc[0]
        col = "F"
        rows.append(dict(model=m, file=r0.file, sheet=r0.sheet, tech=tech, parameter="CapitalCost", year="Unit.Introduced",
                         before=ui, after=new_ui, unit="label of the reference vehicle (column Unit.Introduced)",
                         source_id="", page="",
                         derivation=(f"Label change that goes with the new ratio cells: the row is read relative to {ref_of(new_ui)} "
                                     f"(a price per vehicle) instead of {ref} (itself a ratio to TRAUTDSL, which broke the chain). "
                                     f"Cell {col}{r0.excel_row}."),
                         assumption_sentence="", range_low="", range_high=""))

# ----------------------------------------------------------------------------- FixedCost (rule 2)
fix = dump[dump.parameter == "FixedCost"].copy()
fix["yr"] = fix.year.astype(int)
for (m, tech), g in fix.groupby(["model", "tech"], sort=False):
    cc, short, country = MODELS[m]
    info = tech_info(m, tech)
    km = km_of(m, tech, "after")
    desc = f"{info['ptw']} {info['cls']}"
    for r in g.sort_values("yr").itertuples():
        if r.num is None and not r.formula:
            empty_skipped["FixedCost"] += 1
            continue
        before = r.formula if r.formula else r.num
        v = r.num
        p = P16.get((short, tech, "FixedCost", str(r.yr)))
        gfig = None
        if p is not None and num(p.source_value) is not None and num(p.cpi_factor) is not None:
            gfig = num(p.source_value) * num(p.cpi_factor)
        cls16 = p.change_class if p is not None else ""
        src = page = sent = ""
        der = "Value stays."
        if r.formula:
            der = f"Cell holds the formula {r.formula} (value {v:.6g}); formula and value stay."
        if cc == "CR":
            der += " Entered in M US$ per Gvkm and not converted by the compiler (no division by distance)."
        lo = hi = None
        if gfig is not None:
            lo, hi = min(v, gfig), max(v, gfig)
            der += f" NREL ATB 2022 levelized maintenance and repair cost for the class: {gfig:.3f} M US$ per Gvkm (2024 US$); the value sits {pct(v, gfig)} it."
        if cls16 == "confirmed" and gfig is not None:
            src, page = "GEN-102", "vehicles_fuels.csv, scenario Mid, column discounted_maintenance_and_repair_cost"
        elif v is not None and info["kind"] != "other":
            per_year = f", about {fmt(v / 1000 * km)} US$ per year at {fmt(km)} km" if km and km > 1 else ""
            if gfig is not None:
                sent = (f"Maintenance and repair of a {desc} cost {v:.4g} M US$ per Gvkm ({v / 1000:.4f} US$ per km{per_year}) in {country}, "
                        f"the cost of keeping the vehicle in service on local roads. The NREL ATB 2022 levelized maintenance and repair cost "
                        f"of the class is {gfig:.1f} M US$ per Gvkm in 2024 US$ for United States conditions, {pct(gfig, v)} this value; "
                        f"range {lo:.1f} to {hi:.1f} M US$ per Gvkm.")
            else:
                lo, hi = (3, 20) if info["cls"] == "motorcycle" else (None, None)
                sent = (f"Maintenance and repair of a {desc} cost {v:.4g} M US$ per Gvkm ({v / 1000:.4f} US$ per km{per_year}) in {country}, "
                        f"a small share of the running cost of a light two-wheeler"
                        + (f"; range {lo} to {hi} M US$ per Gvkm." if lo else "."))
                if info["cls"] != "motorcycle":
                    sent = (f"Maintenance and repair of a {desc} cost {v:.4g} M US$ per Gvkm ({v / 1000:.4f} US$ per km{per_year}) in {country}, "
                            f"the cost of keeping the vehicle in service.")
        else:
            sent = (f"The {info['cls']} ({info['ptw']}) carries a fixed cost of {v:.4g} M US$ per unit of capacity in {country}; "
                    f"the mode is represented by its fuel use and its vehicles are not chosen by cost.")
        rows.append(dict(model=m, file=r.file, sheet=r.sheet, tech=tech, parameter="FixedCost", year=str(r.yr),
                         before=outval(before), after=outval(before), unit=f"M US$ per Gvkm ({r.unit_introduced}); range: M US$ per Gvkm, 2024 US$",
                         source_id=src, page=page, derivation=der + f" Cell {r.coord}.", assumption_sentence=sent,
                         range_low=f"{lo:.3f}" if lo is not None else "", range_high=f"{hi:.3f}" if hi is not None else ""))

# ----------------------------------------------------------------------------- OperationalLife (rule 3)
ol = dump[dump.parameter == "OperationalLife"].copy()
life = {(r.model, r.tech): r.num for r in ol.itertuples()}
new_life = {}
for r in ol.itertuples():
    m, tech = r.model, r.tech
    cc, short, country = MODELS[m]
    info = tech_info(m, tech)
    v = r.num
    src = page = sent = ""
    after = v
    if cc == "CR" and tech.startswith("TRNBUS"):
        after, src, page = 15, "CR-002", "PDF p. 83, annex table of assumptions (legal service life of a bus, Consejo de Transporte Publico, 15 years)"
        der = f"National figure: legal service life of a bus in Costa Rica, 15 years; {'equal to' if v == 15 else 'replaces'} {v:g}."
    elif cc == "CR" and tech.startswith("TRNMIC") and v == 1:
        after, src, page = 15, "CR-002", "PDF p. 83, annex table of assumptions (legal service life of a bus, Consejo de Transporte Publico, 15 years)"
        der = ("One-year life replaced by the life of the same class in this model: the bus life of CR_ENERGY (TRNBUS*, 15 years, "
               "the national legal service life of a bus); replaces 1.")
    elif cc == "DR" and (tech.startswith("TRAUT") or tech.startswith("TRTAX")) and v == 1:
        suv = "TRSUV" + tech[5:] if tech.startswith("TRAUT") else "TRSUV" + tech[5:]
        if (m, suv) not in life:
            suv = "TRSUVGSL"
        after = life[(m, suv)]
        der = (f"One-year life replaced by the life of the same class in this model: the SUV life of RD_ENERGY "
               f"({suv}, {after:g} years); replaces 1.")
        sent = (f"A {info['ptw']} {'car' if tech.startswith('TRAUT') else 'taxi'} in the Dominican Republic stays in service "
                f"{after:g} years, the life of a sport utility vehicle of the same powertrain, since both are light-duty vehicles. "
                f"The NREL ATB 2022 uses 15 years for light-duty vehicles and the national electric mobility plan 10 years for the "
                f"whole fleet, while 48.4 percent of the automobiles registered at the end of 2023 were built in 2000 or earlier; "
                f"range 10 to 23 years.")
    elif cc == "DR" and tech.startswith("TRMOT") and v == 1:
        after, src, page = 10, "GEN-104", "PDF p. 78, footnote 11 (vida util teorica de 10 anos)"
        der = ("One-year life replaced: no motorcycle in RD_ENERGY has another life, so the national figure applies, the 10-year "
               "theoretical vehicle life of the national electric mobility plan; replaces 1.")
    elif cc == "JAM" and tech.startswith("TRAUT"):
        after, src, page = 15, "JAM-002", "printed p. 20 and p. 82 (15-year useful life of electric and conventional cars)"
        der = f"National figure: 15-year useful life of electric and conventional cars in the Office of Utilities Regulation consultation document; {'equal to' if v == 15 else 'replaces'} {v:g}."
    else:
        der = "Value stays as an assumption."
        k = info["kind"]
        if k == "other":
            sent = f"The {info['cls']} ({info['ptw']}) stays in service {v:g} years in {country}, a life that sets how a capital cost spreads over time; this mode carries no capital cost per vehicle."
        else:
            refs = {"car": ("15 years for light-duty vehicles in the NREL ATB 2022", 15),
                    "taxi": ("15 years for light-duty vehicles in the NREL ATB 2022", 15),
                    "SUV": ("15 years for light-duty vehicles in the NREL ATB 2022", 15),
                    "pick-up or jeep": ("15 years for light-duty vehicles in the NREL ATB 2022", 15),
                    "light truck": ("15 years for light-duty vehicles in the NREL ATB 2022", 15),
                    "minibus": ("15 years for a Class 4 van in the NREL ATB 2022", 15),
                    "motorcycle": ("10 years of theoretical vehicle life in the Dominican Republic national electric mobility plan", 10),
                    "heavy truck": ("10 years of theoretical vehicle life in the Dominican Republic national electric mobility plan", 10)}
            if k == "bus":
                rt, rv = "15 years of legal service life of a bus in Costa Rica (CEPAL 2024)", 15
            else:
                rt, rv = refs.get(info["cls"], ("15 years for light-duty vehicles in the NREL ATB 2022", 15))
            extra = ""
            if cc == "CR":
                extra = ", while vehicles inspected in Costa Rica in 2019 averaged about 16 years of age"
            if cc == "JAM" and info["cls"] in ("taxi", "pick-up or jeep"):
                extra = ", while the Office of Utilities Regulation assumes a 15-year useful life for cars in Jamaica"
            if cc == "DR":
                extra = ", while 41.7 to 48.3 percent of the buses, automobiles and cargo vehicles registered in the Dominican Republic at the end of 2023 were built in 2000 or earlier"
            lo, hi = min(v, rv), max(v, rv)
            sent = (f"A {info['ptw']} {info['cls']} stays in service {v:g} years in {country}, the period over which its price is paid off. "
                    f"The value sits {pct(v, rv)} the {rt}{extra}" + (f"; range {lo:g} to {hi:g} years." if lo != hi else "."))
    if src and after != v:
        pass
    rows.append(dict(model=m, file=r.file, sheet=r.sheet, tech=tech, parameter="OperationalLife", year="",
                     before=outval(v), after=outval(after), unit="years", source_id=src, page=page,
                     derivation=der + f" Cell {r.coord}.", assumption_sentence=sent, range_low="", range_high=""))

# ----------------------------------------------------------------------------- write
cols = ["model", "file", "sheet", "tech", "parameter", "year", "before", "after", "unit", "source_id", "page",
        "derivation", "assumption_sentence", "range_low", "range_high"]
order = {"CapitalCost": 0, "FixedCost": 1, "OperationalLife": 2, "Ref.km.BY": 3}
rows.sort(key=lambda r: (list(MODELS).index(r["model"]), order[r["parameter"]], r["tech"], r["year"]))
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({c: r[c] for c in cols})
pd.DataFrame(cr_checks).to_csv(os.path.join(HERE, "cr_price_check.csv"), index=False)
print("rows", len(rows), "empty cells skipped", empty_skipped)
