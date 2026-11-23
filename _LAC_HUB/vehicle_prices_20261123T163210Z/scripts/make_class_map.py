"""Write vehicle_class_map.csv: one row per model and technology in scope, with vehicle class,
powertrain and the HS 6-digit codes (HS 2017 and HS 2022) that hold it.

Reads the scope cells file (scope_cells.csv in the job folder, the CapitalCost rows of the
ENERGY and TRANSPORT models in the cost-sources proposal files). The HS codes follow the WCO
nomenclature chapter 87 (sources HS-001 for HS 2017, HS-002 for HS 2022).
"""
import csv
import os

JOB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# class by technology prefix
PREFIX = [
    ("TRNSED", "car"), ("TRNTAX", "taxi"), ("TRNSUV", "SUV"), ("TRNFRELIG", "pickup or light truck"),
    ("TRNFREHEA", "heavy truck"), ("TRNMIC", "minibus"), ("TRNBUS", "bus"), ("TRNMOT", "motorcycle"),
    ("TRAUT", "car"), ("TRTAX", "taxi"), ("TRSUV", "SUV"), ("TRYLF", "pickup or light truck"),
    ("TRYTK", "heavy truck"), ("TRMBS", "minibus"), ("TRBPU", "bus"), ("TRBPR", "bus"),
    ("TRBTUR", "bus"), ("TRMOT", "motorcycle"),
]
# powertrain by technology suffix (longest first)
SUFFIX = [
    ("HYBDSL", "hybrid diesel"), ("HYBGSL", "hybrid gasoline"), ("Flex_Fuel", "gasoline (flex fuel)"),
    ("PHG", "plug-in hybrid gasoline"), ("PHD", "plug-in hybrid diesel"), ("NGV", "natural gas"),
    ("NGS", "natural gas"), ("DSL", "diesel"), ("GSL", "gasoline"), ("LPG", "LPG"),
    ("ELE", "battery electric"), ("HYD", "fuel cell"), ("HG", "hybrid gasoline"), ("HD", "hybrid diesel"),
]

SI = ("gasoline", "gasoline (flex fuel)", "LPG", "natural gas")

# HS lines per (class group, powertrain): (hs2017, hs2022, why)
CAR_SI = ("870321;870322;870323", "870321;870322;870323")
SUV_SI = ("870323;870324", "870323;870324")
CAR_CI = ("870331;870332", "870331;870332")
SUV_CI = ("870332;870333", "870332;870333")


def lines(cls, pt, name):
    """Return hs2017, hs2022, priced_by_lines (yes/no), reason."""
    si = pt in SI
    if cls in ("car", "taxi", "SUV"):
        pickup = cls == "SUV" and "pick" in name.lower()
        base = {"car": (CAR_SI, CAR_CI), "taxi": (CAR_SI, CAR_CI), "SUV": (SUV_SI, SUV_CI)}[cls]
        why_cls = ("Taxis take the car lines. " if cls == "taxi" else "")
        if pickup:
            why_cls = ("The group holds pick-ups and jeeps, so it takes the larger passenger-car lines "
                       "(jeeps) and the goods-vehicle lines up to 5 tonnes g.v.w. (pick-ups). ")
        if si:
            h = base[0]
            extra = ";870431" if pickup else ""
            why = (why_cls + ("Spark-ignition engines (gasoline, flex fuel, LPG and natural gas) share the "
                              "lines of vehicles with only a spark-ignition engine; HS has no fuel split. ")
                   + ("Cars take the lines up to 3,000 cc. " if cls != "SUV" else
                      "SUVs and jeeps take the lines above 1,500 cc, where nearly all of them fall. "))
            return h[0] + extra, h[1] + extra, "yes", why.strip()
        if pt == "diesel":
            h = base[1]
            extra = ";870421" if pickup else ""
            why = why_cls + ("Diesel cars take the compression-ignition lines up to 2,500 cc."
                             if cls != "SUV" else "Diesel SUVs and jeeps take the compression-ignition lines above 1,500 cc.")
            return h[0] + extra, h[1] + extra, "yes", why.strip()
        m = {"hybrid gasoline": ("870340", "870451"), "hybrid diesel": ("870350", "870441"),
             "plug-in hybrid gasoline": ("870360", "870451"), "plug-in hybrid diesel": ("870370", "870441"),
             "battery electric": ("870380", "870460"), "fuel cell": ("870380", "870460")}[pt]
        h17, h22 = m[0], m[0]
        if pickup:
            h22 = m[0] + ";" + m[1]
        if pt == "fuel cell":
            return h17, h22, "no", (why_cls + "A fuel cell car has only an electric motor for propulsion and "
                                    "falls in the electric line, where battery electric cars make nearly all "
                                    "imports, so the line gives no fuel cell price.").strip()
        why = why_cls + "Hybrid, plug-in hybrid and electric cars have their own lines, with no engine-size split."
        if pickup:
            why += " Goods vehicles of the same powertrain have their own lines only from HS 2022."
        return h17, h22, "yes", why.strip()
    if cls == "pickup or light truck":
        band = "Light trucks take g.v.w. not exceeding 5 tonnes."
        if si:
            return "870431", "870431", "yes", "Spark-ignition goods vehicles up to 5 tonnes g.v.w. " + band
        if pt == "diesel":
            return "870421", "870421", "yes", "Compression-ignition goods vehicles up to 5 tonnes g.v.w. " + band
        if pt in ("hybrid diesel", "plug-in hybrid diesel"):
            return "", "870441", "yes", ("Diesel-electric goods vehicles up to 5 tonnes have their own line only "
                                         "from HS 2022; in HS 2017 they sit in 8704.90 with other vehicles. " + band)
        if pt in ("hybrid gasoline", "plug-in hybrid gasoline"):
            return "", "870451", "yes", ("Gasoline-electric goods vehicles up to 5 tonnes have their own line only "
                                         "from HS 2022. " + band)
        if pt == "battery electric":
            return "", "870460", "yes", ("Electric goods vehicles have their own line only from HS 2022, with no "
                                         "weight split; light vans and pick-ups make most of it.")
        return "", "870460", "no", ("A fuel cell goods vehicle falls in the electric line, where battery "
                                    "electric vehicles make nearly all imports, so the line gives no fuel cell price.")
    if cls == "heavy truck":
        band = "Heavy trucks take g.v.w. above 5 tonnes (both the 5 to 20 tonne and the above 20 tonne bands)."
        if si:
            return "870432", "870432", "yes", "Spark-ignition goods vehicles above 5 tonnes g.v.w. " + band
        if pt == "diesel":
            return "870422;870423", "870422;870423", "yes", "Compression-ignition goods vehicles above 5 tonnes. " + band
        if pt in ("hybrid diesel", "plug-in hybrid diesel"):
            return "", "870442;870443", "yes", ("Diesel-electric goods vehicles above 5 tonnes have their own lines "
                                                "only from HS 2022. " + band)
        if pt in ("hybrid gasoline", "plug-in hybrid gasoline"):
            return "", "870452", "yes", "Gasoline-electric goods vehicles above 5 tonnes, HS 2022 only. " + band
        why = ("The electric goods-vehicle line (HS 2022 only) has no weight split and holds mostly light vans, "
               "so it gives no heavy-truck price.")
        if pt == "fuel cell":
            why = "A fuel cell truck falls in the electric line, which gives no heavy fuel cell price. " + why
        return "", "870460", "no", why
    if cls in ("bus", "minibus"):
        why_cls = ("HS does not split buses from minibuses; heading 8702 covers every vehicle for ten or more "
                   "persons. ")
        if pt == "diesel":
            return "870210", "870210", "yes", why_cls + "Diesel only."
        if si:
            return "870290", "870290", "yes", why_cls + ("Buses with only a spark-ignition engine have no line of "
                                                         "their own and fall in 8702.90 Other.")
        if pt in ("hybrid diesel", "plug-in hybrid diesel"):
            return "870220", "870220", "yes", why_cls + "Diesel and electric motor, plug-in or not."
        if pt in ("hybrid gasoline", "plug-in hybrid gasoline"):
            return "870230", "870230", "yes", why_cls + "Spark-ignition and electric motor."
        if pt == "battery electric":
            return "870240", "870240", "yes", why_cls + "Only electric motor."
        return "870240", "870240", "no", (why_cls + "A fuel cell bus falls in the electric line, where battery "
                                          "electric buses make nearly all imports, so the line gives no fuel cell price.")
    if cls == "motorcycle":
        if pt == "battery electric":
            return "871160", "871160", "yes", "Motorcycles with electric motor for propulsion."
        return ("871110;871120;871130;871140;871150", "871110;871120;871130;871140;871150", "yes",
                "Motorcycles with a reciprocating piston engine, all cylinder capacities (flex fuel engines included).")
    raise ValueError((cls, pt))


def main():
    rows = {}
    with open(os.path.join(JOB, "scope_cells.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[(r["country"], r["model"], r["tech"])] = r["tech_name"]
    out = []
    for (cc, model, tech), name in sorted(rows.items()):
        if tech == "TRNPASRAIELE":
            out.append([cc, model, tech, name, "rail", "battery electric", "", "", "", "no", "",
                        "Out of scope: the cell is entered in M US$ per GPkm and stays as proposed before."])
            continue
        cls = next(c for p, c in PREFIX if tech.startswith(p))
        pt = next(s for k, s in SUFFIX if tech.endswith(k))
        h17, h22, priced, why = lines(cls, pt, name)
        band = ""
        if cls == "pickup or light truck" or ("pick" in name.lower()):
            band = "g.v.w. not exceeding 5 t"
        elif cls == "heavy truck":
            band = "g.v.w. exceeding 5 t"
        out.append([cc, model, tech, name, cls, pt, h17, h22, band, priced, "HS-001;HS-002", why])
    with open(os.path.join(JOB, "vehicle_class_map.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["country", "model", "tech", "tech_name", "vehicle_class", "powertrain", "hs2017_codes",
                    "hs2022_codes", "truck_weight_band", "own_lines_priced", "hs_source_ids", "why"])
        w.writerows(out)
    print(len(out), "rows")


if __name__ == "__main__":
    main()
