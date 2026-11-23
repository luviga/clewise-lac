"""Build the shared international vehicle cost package (GEN vehicles).

Inputs (downloads/GEN_vehicles): NREL ATB 2022 Transportation vehicles.csv and
vehicles_fuels.csv (GEN-101, GEN-102), ATB 2022 Transportation definitions page
(GEN-103), INTRANT-IDB 2020 national electric mobility plan (GEN-104).
Output: GEN/gen_vehicle_factors.csv
"""
import csv
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
JOB = os.path.dirname(GEN)
DL = os.path.join(JOB, "downloads", "GEN_vehicles")

cpi = pd.read_csv(os.path.join(JOB, "cpi_u.csv")).set_index("year")["factor_to_2024"]
F2020 = float(cpi.loc[2020])
MI_KM = 1.609344

# model class -> ATB class
CLASS_MAP = {
    "car": "Compact",
    "taxi": "Compact",
    "SUV": "Small_SUV",
    "light_freight": "Pickup",
    "minibus": "4",
    "bus": "8",
    "heavy_freight": "8",
}
CLASS_NOTE = {
    "car": "ATB Compact Passenger Car (model AUT, SED)",
    "taxi": "ATB Compact Passenger Car (model TAX)",
    "SUV": "ATB Small SUV (model SUV, pick-up and jeep)",
    "light_freight": "ATB Pickup Truck (model YLF, FRELIG)",
    "minibus": "ATB Class 4 Medium StepVan (model MBS, MIC)",
    "bus": "ATB Class 8 Longhaul Sleeper used as heavy-duty proxy; ATB has no bus (model BPU, BUS, BTUR, BPR)",
    "heavy_freight": "ATB Class 8 Longhaul Sleeper (model YTK, FREHEA)",
}
LDV_PT = {
    "DSL": ("Conventional CI", ""),
    "GSL": ("Conventional SI", ""),
    "Flex_Fuel": ("Conventional SI", "proxy: gasoline spark-ignition vehicle"),
    "LPG": ("Conventional SI", "proxy: ATB has no LPG vehicle; gasoline spark-ignition vehicle"),
    "NGS": ("Conventional CNG", ""),
    "ELE": ("BEV300", "BEV with 300-mile range"),
    "HYD": ("Fuel Cell 300", ""),
    "HG": ("Split HEV", ""),
    "HD": ("Split HEV", "proxy: ATB has no light-duty diesel hybrid; gasoline power-split hybrid"),
    "PHG": ("EREV PHEV50", ""),
    "PHD": ("EREV PHEV50", "proxy: ATB has no light-duty diesel plug-in hybrid; gasoline PHEV50"),
}
HD_PT = {
    "DSL": ("Conv", ""),
    "GSL": ("Conv", "proxy: ATB has no gasoline medium/heavy vehicle; diesel conventional"),
    "LPG": ("Conv", "proxy: ATB has no LPG medium/heavy vehicle; diesel conventional"),
    "NGS": ("Conv", "proxy: ATB 2022 has no natural gas medium/heavy vehicle; diesel conventional"),
    "ELE": ("BEV", ""),
    "HYD": ("FCEV", ""),
    "HD": ("ParHEV", "diesel parallel hybrid"),
    "PHD": ("SeriesPHEV", "diesel series plug-in hybrid"),
}

veh = pd.read_csv(os.path.join(DL, "NREL_ATB_2022_transportation_vehicles.csv"), dtype={"vehicle_class": str})
veh = veh[veh.scenario == "Mid"]
vf = pd.read_csv(
    os.path.join(DL, "NREL_ATB_2022_transportation_vehicles_fuels.csv"),
    usecols=["year", "scenario", "vehicle_class", "vehicle_detail", "discounted_maintenance_and_repair_cost"],
    dtype={"vehicle_class": str},
    low_memory=False,
)
vf = vf[vf.scenario == "Mid"].groupby(["vehicle_class", "vehicle_detail", "year"])[
    "discounted_maintenance_and_repair_cost"].first()


def series(cls, detail):
    s = veh[(veh.vehicle_class == cls) & (veh.vehicle_detail == detail)].groupby("year")["vehicle_cost(2020$)"].first()
    return s.sort_index()


def interp(s, y):
    xs = list(s.index)
    if y in s.index:
        return float(s.loc[y])
    lo = max(x for x in xs if x < y)
    hi = min(x for x in xs if x > y)
    return float(s.loc[lo] + (s.loc[hi] - s.loc[lo]) * (y - lo) / (hi - lo))


rows = []


def add(item, vclass, pt, year, value, unit, cy, v24, cf, sid, page, deriv):
    rows.append(dict(item=item, vehicle_class=vclass, powertrain=pt, year=year, value=value, unit=unit,
                     source_currency_year=cy, value_2024usd=v24, cpi_factor=cf, source_id=sid,
                     page_or_table=page, derivation=deriv))


ATB_PAGE = "vehicles.csv, scenario Mid, column vehicle_cost(2020$)"
for mclass, acls in CLASS_MAP.items():
    ptmap = HD_PT if acls in ("4", "6", "8") else LDV_PT
    for pt, (detail, ptnote) in ptmap.items():
        s = series(acls, detail)
        if s.empty:
            continue
        p24 = interp(s, 2024)
        pub = ", ".join(f"{y}={int(v)}" for y, v in s.items())
        note = f"{CLASS_NOTE[mclass]}; ATB vehicle_detail {detail}" + (f" ({ptnote})" if ptnote else "")
        for y in range(2024, 2051):
            r = interp(s, y) / p24
            add("price_trajectory", mclass, pt, y, round(r, 6), "ratio to own 2024 price", "", "", "",
                "GEN-101", ATB_PAGE,
                f"{note}. Published prices (2020 USD): {pub}. 2024 and the years between published years "
                f"interpolated linearly; ratio = price(year) / price(2024). Published to 2050, so no hold-flat needed.")
        # reference price 2024 (not for buses: the ATB Class 8 tractor is a trajectory proxy only)
        if mclass != "bus":
          add("reference_price", mclass, pt, 2024, round(p24, 1), "US$ per vehicle", 2020, round(p24 * F2020, 1),
            round(F2020, 6), "GEN-101", ATB_PAGE,
            f"{note}. 2024 price interpolated linearly between published years ({pub}); "
            f"value_2024usd = value x CPI-U factor 2020->2024. United States retail price, no import duties or taxes of the five countries.")
        # maintenance
        m = vf.loc[(acls, detail)]
        m24 = interp(m, 2024)
        km = m24 / MI_KM
        km24 = km * F2020
        mpub = ", ".join(f"{y}={v}" for y, v in m.items())
        add("maintenance_cost", mclass, pt, 2024, round(km, 5), "US$ per km", 2020, round(km24, 5), round(F2020, 6),
            "GEN-102", "vehicles_fuels.csv, scenario Mid, column discounted_maintenance_and_repair_cost (US$ per mile)",
            f"{note}. Levelized maintenance and repair cost per mile ({mpub}), 2024 interpolated; "
            f"US$ per km = US$ per mile / 1.609344; value_2024usd = value x CPI-U factor 2020->2024.")
        add("maintenance_cost", mclass, pt, 2024, round(km * 1000, 3), "M US$ per Gvkm", 2020, round(km24 * 1000, 3),
            round(F2020, 6), "GEN-102",
            "vehicles_fuels.csv, scenario Mid, column discounted_maintenance_and_repair_cost (US$ per mile)",
            f"{note}. Same value as the US$ per km row times 1000 (1 US$/km = 1000 M US$/Gvkm), for FixedCost rows.")

# DR national plan reference prices (Latin American data point)
PEN = "GEN-104"
for mclass, pt, v, pg in [
    ("car", "ELE", 30000, "PDF page 94, Tabla 6 footnote 29"),
    ("bus", "ELE", 360000, "PDF page 94, Tabla 6 footnote 29"),
    ("heavy_freight", "ELE", 120000, "PDF page 94, Tabla 6 footnote 29 (vehiculos de carga)"),
    ("motorcycle", "ELE", 3000, "PDF page 94, Tabla 6 footnote 29"),
    ("car", "GSL", 20001, "PDF page 72, average new conventional vehicle in the Dominican Republic"),
]:
    add("reference_price", mclass, pt, 2020, v, "US$ per vehicle", 2020, round(v * F2020, 1), round(F2020, 6), PEN, pg,
        "Dominican Republic national plan (INTRANT with IDB, 2020); currency year taken as the publication year 2020; "
        "value_2024usd = value x CPI-U factor 2020->2024. The conventional car value is for a new conventional vehicle, fuel not stated.")

# operational life
for mclass in ["car", "taxi", "SUV", "light_freight"]:
    add("operational_life", mclass, "all", "", 15, "years", "", "", "", "GEN-103",
        "Levelized Cost of Driving Assumptions for Light-Duty Vehicles: Vehicle life 15 years (Bento et al., 2018)",
        "Light-duty vehicle life used by NREL ATB 2022 Transportation.")
add("operational_life", "minibus", "all", "", 15, "years", "", "", "", "GEN-103",
    "Levelized Cost of Driving Assumptions for Medium- and Heavy-Duty Vehicles: 15 years for Class 4 Van",
    "ATB Class 4 van life used for minibuses. ATB gives 5 years for Class 6 and Class 8 (first owner only), which is not a vehicle lifetime.")
for mclass in ["bus", "heavy_freight", "motorcycle", "all_road"]:
    add("operational_life", mclass, "all", "", 10, "years", "", "", "", PEN,
        "PDF page 78, Tabla 4 footnote 11: vida util teorica de 10 anos",
        "Theoretical fleet life of 10 years used by the Dominican Republic national electric mobility plan for the whole vehicle fleet (not class specific).")

# annual km
ldv_avg_mi = 178102 / 15
add("annual_km", "car_SUV_light_duty", "all", "", round(ldv_avg_mi * MI_KM, 0), "km per vehicle per year", "", "", "",
    "GEN-103", "LCOD methodology text: 14,231 miles/year new, 9,249 at age 15, 178,102 miles over 15 years",
    "United States light-duty average over 15 years = 178,102 mi / 15 x 1.609344 km per mile.")
add("annual_km", "minibus", "all", "", round(335000 / 15 * MI_KM, 0), "km per vehicle per year", "", "", "", "GEN-103",
    "LCOD assumptions MDHD: 335,000 miles not discounted for Class 4 over 15 years",
    "United States Class 4 van average = 335,000 mi / 15 years x 1.609344.")
for mclass, v in [("car_jeep", 7500), ("bus", 44000), ("freight", 9000), ("motorcycle", 10500)]:
    add("annual_km", mclass, "all", "", v, "km per vehicle per year", "", "", "", PEN,
        "PDF page 78, Tabla 4, column Intensidad de uso (km/ano)",
        "Dominican Republic national plan, average use intensity by vehicle type (automoviles y jeeps, autobuses, carga, motocicletas).")

out = os.path.join(GEN, "gen_vehicle_factors.csv")
cols = ["item", "vehicle_class", "powertrain", "year", "value", "unit", "source_currency_year", "value_2024usd",
        "cpi_factor", "source_id", "page_or_table", "derivation"]
with open(out, "w", newline="\n", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows ->", out)
