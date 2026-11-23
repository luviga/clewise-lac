"""Gate 3 second pass: for sampled source values that a text search cannot find because they are
derived (ATB values interpolated between published years, ratios of two ATB prices, FAOSTAT multi-year
averages), recompute them from the downloaded files and confirm. Updates gate3_value_checks.csv."""
import os, sys, csv, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from models import JOB

ATB = os.path.join(JOB, "downloads", "GEN_vehicles", "NREL_ATB_2022_transportation_vehicles.csv")
atb = list(csv.DictReader(open(ATB, newline="", encoding="utf-8")))
gvf = list(csv.DictReader(open(os.path.join(JOB, "GEN", "gen_vehicle_factors.csv"), newline="", encoding="utf-8")))
fao = list(csv.DictReader(open(os.path.join(JOB, "GEN", "faostat_trade_unit_values.csv"), newline="", encoding="utf-8")))


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def published(der):
    m = re.search(r"Published prices \(20\d\d USD\): ([0-9=, ]+)", der) or re.search(r"published years \(([0-9=, ]+)\)", der)
    if not m:
        return None
    return {int(a): float(b) for a, b in re.findall(r"(\d{4})=(\d+(?:\.\d+)?)", m.group(1))}


def atb_has(price, der):
    """True if the published price exists in the ATB file in a Mid row of the class named in the derivation."""
    cls = re.search(r"ATB (.+?) (?:\(|used)", der)
    det = re.search(r"vehicle_detail ([^.(;]+)", der)
    for r in atb:
        if r["scenario"] != "Mid" or num(r["vehicle_cost(2020$)"]) != price:
            continue
        if cls and cls.group(1).strip() not in r["vehicle_class_display"]:
            continue
        if det and det.group(1).strip().strip(";,.").strip() != r["vehicle_detail"]:
            continue
        return True
    return False


def interp(pub, y):
    ys = sorted(pub)
    if y in pub:
        return pub[y]
    for a, b in zip(ys, ys[1:]):
        if a < y < b:
            return pub[a] + (pub[b] - pub[a]) * (y - a) / (b - a)
    return None


def check_gen_vehicle(value):
    """Find a GEN vehicle factor equal to value, recompute it from ATB published prices found in the file."""
    for g in gvf:
        for col in ("value", "value_2024usd"):
            if num(g[col]) is not None and abs(num(g[col]) - value) <= max(1e-6, 1e-6 * abs(value)):
                pub = published(g["derivation"])
                if not pub:
                    continue
                if not all(atb_has(p, g["derivation"]) for p in pub.values()):
                    return "ATB published prices not all found in file (%s)" % g["derivation"][:60]
                y = int(g["year"])
                if g["item"] == "price_trajectory":
                    calc = interp(pub, y) / interp(pub, 2024)
                elif col == "value":
                    calc = interp(pub, y)
                else:
                    calc = interp(pub, y) * num(g["cpi_factor"])
                if calc is not None and abs(calc - value) <= 5e-4 * max(1, abs(value)):
                    return "confirmed by recompute: %s %s %s %s from ATB published prices %s" % (g["item"], g["vehicle_class"], g["powertrain"], y, pub)
                return "recompute differs: %s vs %s" % (calc, value)
    return None


def check_fao(value):
    for f in fao:
        for k, v in f.items():
            if num(v) is not None and abs(num(v) - value) <= 0.006:
                return "confirmed against FAOSTAT extract row %s %s (%s)" % (f.get("country", ""), f.get("model_item", f.get("item", "")), k)
    return None


# value checks done by reading the downloaded file (country, tech, parameter, year) -> what was read
READ = {
    ("CR", "TRNBUS", "Ref.km.BY", "BY"): "confirmed by reading CR-001 (downloads/CR/S2200597_es.pdf): note to the bus cost table, initial assumption 45.000 km per year plus 10 percent unproductive mileage (ARESEP)",
    ("JAM", "AG_PLA", "FixedCost", "2021"): "confirmed by reading JAM-006 (downloads/JAM/MOA_COP_2022.pdf): plantain budgets St. Mary 8,603 kg at J$63 per kg and Trelawny 8,097 kg at J$79 per kg for 0.4 ha; (8,603 x 63 + 8,097 x 79) / 2 / 0.4 = J$1,477,065 per ha",
    ("ECU", "GA_BOV", "VariableCost", "2021"): "confirmed by reading ECU-003 (downloads/ECU/Rimisp_GanaderiaCarne_DocResultados.pdf): Tabla 23, row Total, cost per head 159.4, 157.4 and 285.5 US$ by producer type",
    ("ECU", "AG_MAI", "FixedCost", "2021"): "confirmed by reading ECU-002 (downloads/ECU/PoloConocimiento_5170_cadena_maiz_Ecuador.html): variable cost $ 1.458,06 and fixed cost $ 304,02 per ha (MAG)",
    ("ECU", "AG_ARR", "FixedCost", "2021"): "confirmed by reading ECU-001 (downloads/ECU/Rimisp_DocEcuador_productividad.pdf): Tabla 3.5, MAGAP column, Tierra $ 210.00 and Capital $ 56.01 per ha",
    ("CR", "TRNMIC", "Ref.km.BY", "BY"): "confirmed by reading GEN-103 (ATB definitions page): Class 4 van 335,000 miles undiscounted over a 15-year first-owner life; 335,000 / 15 x 1.609344 = 35,942 km per year",
}
p = os.path.join(JOB, "gate3_value_checks.csv")
rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
for r in rows:
    if r["result"] == "confirmed":
        continue
    sv = r["source_value"]
    res = READ.get((r["country"], r["tech"], r["parameter"], r["year"]))
    m = re.fullmatch(r"\s*([\d.]+)\s*/\s*([\d.]+)\s*", sv)
    if res:
        pass
    elif "GEN-101" in r["source_ids"] and m:
        a, b = check_gen_vehicle(float(m.group(1))), check_gen_vehicle(float(m.group(2)))
        if a and b and a.startswith("confirmed") and b.startswith("confirmed"):
            res = "confirmed by recompute of both prices"
    elif "GEN-101" in r["source_ids"] and num(sv) is not None:
        res = check_gen_vehicle(num(sv))
    elif "GEN-201" in r["source_ids"] and num(sv) is not None:
        res = check_fao(num(sv))
    if res:
        r["found_in_file"] = res
        r["result"] = "confirmed" if res.startswith("confirmed") else "check by reading"
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(rows)
for r in rows:
    if r["result"] != "confirmed":
        print("OPEN", r["country"], r["tech"], r["parameter"], r["year"], r["source_ids"], r["source_value"], "|", r["found_in_file"])
print(sum(r["result"] == "confirmed" for r in rows), "of", len(rows), "confirmed")
