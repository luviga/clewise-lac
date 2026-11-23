"""Build the FAOSTAT extracts for the sector agents from the subsets made by faostat_subset.py.

Outputs in GEN/: faostat_trade_unit_values.csv, faostat_producer_prices.csv, faostat_yields.csv,
faostat_item_mapping.csv. Real 2024 USD with cpi_u.csv (factor_to_2024 of the data year).
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
JOB = os.path.dirname(GEN)
DL = os.path.join(JOB, "downloads", "GEN_sector")
CC = {"Costa Rica": "CR", "Dominican Republic": "DR", "Ecuador": "ECU", "Guatemala": "GUA",
      "Honduras": "HON", "Jamaica": "JAM"}
cpi = pd.read_csv(os.path.join(JOB, "cpi_u.csv")).set_index("year")["factor_to_2024"]

CEREALS = [15, 27, 44, 56, 71, 75, 79, 83, 92, 108]
OTHER_GRAINS = [15, 44, 56, 71, 75, 79, 83, 92, 108]
PULSES = [176, 181, 187, 191, 195, 197, 201, 210, 211]
ROOTS = [116, 122, 125, 135, 136, 137, 149]
SPICES = [687, 689, 692, 693, 698, 702, 711, 720, 723]
VEG = [358, 366, 367, 372, 373, 388, 393, 394, 397, 399, 401, 402, 403, 406, 407, 414, 417, 420,
       423, 426, 430, 446, 449, 463]
FRUIT = [486, 489, 490, 495, 497, 507, 512, 515, 521, 526, 531, 534, 536, 544, 547, 558, 560,
         567, 568, 569, 571, 572, 574, 600, 603, 619]

# Trade mapping: model item -> (model techs, FAO item codes summed, label, quantity unit)
TRADE = [
    ("rice", "IMPRIC;IMPARR", [30], "Rice, paddy (rice milled equivalent) [FAO aggregate]", "t"),
    ("banana", "IMPBAN", [486], "Bananas", "t"),
    ("plantain", "(no IMP tech in scope; AG_PLA)", [489], "Plantains and cooking bananas", "t"),
    ("coffee", "IMPCAF;IMPCOF", [656], "Coffee, green", "t"),
    ("sugar", "IMPSUG (CR Import Sugar; ECU Import Sugarcane);IMPSGC", [162, 164],
     "Raw cane or beet sugar (centrifugal only) + Refined sugar", "t"),
    ("sugar_cane", "IMPSGC;IMPSUG (if cane itself is meant)", [156], "Sugar cane", "t"),
    ("molasses", "IMPMOL", [165], "Molasses", "t"),
    ("pineapple", "IMPPIN", [574], "Pineapples", "t"),
    ("oranges", "IMPORG", [490], "Oranges", "t"),
    ("vegetables", "IMPVEG", [1734], "Vegetables [FAO trade aggregate]", "t"),
    ("other_grains", "IMPOTG", OTHER_GRAINS, "Cereals other than rice: wheat, barley, maize, rye, oats, millet, sorghum, quinoa, cereals n.e.c. (sum)", "t"),
    ("cereals", "IMPCER", [1944], "Cereals [FAO trade aggregate, includes preparations]", "t"),
    ("maize", "IMPMAI (HON, ECU)", [56], "Maize (corn)", "t"),
    ("soy", "IMPSOY", [236], "Soya beans", "t"),
    ("palm_oil", "IMPPAL if oil palm is meant", [257], "Palm oil", "t"),
    ("palm_hearts", "IMPPAL if palm hearts (palmito) are meant", [472], "Vegetables preserved nes (o/t vinegar) [FAO item holding preserved palm hearts]", "t"),
    ("legumes_pulses", "IMPLEG;IMPFRI (HON beans: use beans_dry)", [1954], "Pulses [FAO trade aggregate]", "t"),
    ("beans_dry", "IMPFRI (HON frijol)", [176], "Beans, dry", "t"),
    ("melons", "IMPMEL (HON)", [568], "Cantaloupes and other melons", "t"),
    ("tubers", "IMPTUB", [1719], "Roots and Tubers [FAO trade aggregate]", "t"),
    ("potatoes", "IMPPOT", [116], "Potatoes", "t"),
    ("fruit", "IMPFRT", [1802], "Fruit [FAO trade aggregate]", "t"),
    ("cocoa", "IMPCOC", [661], "Cocoa beans", "t"),
    ("coconut", "IMPCNT", [249, 250], "Coconuts, in shell + Coconuts, desiccated", "t"),
    ("condiments_spices", "IMPCON", SPICES, "Spices: pepper, chillies dry, vanilla, cinnamon, cloves, nutmeg, anise group, ginger, other spices (sum)", "t"),
    ("milk", "IMPLEC;IMPMILK", [1881], "Dairy Products, milk equivalent [FAO trade aggregate]", "t"),
    ("beef", "IMPCAR;IMPCARBOV;IMPBOV (meat)", [1806], "Beef and Buffalo Meat, primary [FAO aggregate, carcass weight]", "t"),
    ("pigmeat", "IMPCARPOR;IMPPOR (meat)", [2073], "Pigmeat (meat equivalent) [FAO aggregate]", "t"),
    ("poultry_meat", "IMPCARPOL;IMPAVE (meat)", [1808], "Meat, Poultry [FAO aggregate]", "t"),
    ("sheep_goat_meat", "IMPOVE;IMPCBR (meat)", [1807], "Sheep and Goat Meat [FAO aggregate]", "t"),
    ("other_products", "IMPOTP (DR Other products; no single FAO match)", [1882], "Crops and livestock products [FAO total, indicator only]", "t"),
    # live animals: quantity in heads
    ("live_cattle", "IMPBOV;IMPCARBOV (if live animals)", [866], "Cattle (live)", "head"),
    ("live_sheep", "IMPOVE", [976], "Sheep (live)", "head"),
    ("live_goats", "IMPCBR", [1016], "Goats (live)", "head"),
    ("live_pigs", "IMPPOR;IMPCARPOR (if live)", [1034], "Swine / pigs (live)", "head"),
    ("live_chickens", "IMPAVE", [1057], "Chickens (live)", "head"),
    ("live_horses", "IMPCAB", [1096], "Horses (live)", "head"),
    ("live_mules", "IMPMUL", [1110], "Mules and hinnies (live)", "head"),
    ("live_camelids", "IMPCAM", [1157], "Other camelids (live)", "head"),
]

# Producer prices: model item -> (techs, FAO item codes; >1 code = production-weighted mean)
PRICES = [
    ("rice", "AGRRIC;AG_RIC;AG_ARR", [27], "Rice (paddy)"),
    ("banana", "AGRBAN;AG_BAN", [486], "Bananas"),
    ("plantain", "AG_PLA", [489], "Plantains and cooking bananas"),
    ("coffee", "AGRCAF;AG_CAF;AG_COF", [656], "Coffee, green"),
    ("oil_palm", "AGRPLM;AG_PLM;AG_PAL (if oil palm)", [254], "Oil palm fruit"),
    ("pineapple", "AGRPIN", [574], "Pineapples"),
    ("oranges", "AGRORG", [490], "Oranges"),
    ("vegetables", "AGRVEG;AG_VEG;AG_LEG (HON, if vegetables)", VEG, "Vegetables: production-weighted mean of FAO vegetable items with a price"),
    ("other_grains", "AGROTG", OTHER_GRAINS, "Cereals other than rice: production-weighted mean"),
    ("cereals", "AG_CER", CEREALS, "Cereals: production-weighted mean"),
    ("maize", "AG_MAI", [56], "Maize (corn)"),
    ("sugar_cane", "AG_SGC;AG_SUG", [156], "Sugar cane"),
    ("cocoa", "AG_COC", [661], "Cocoa beans"),
    ("fruit", "AG_FRT", FRUIT, "Fruit: production-weighted mean of FAO fruit items with a price"),
    ("soy", "AG_SOY", [236], "Soya beans"),
    ("legumes_pulses", "AG_LEG", PULSES, "Pulses: production-weighted mean"),
    ("beans_dry", "AG_FRI (HON frijol)", [176], "Beans, dry"),
    ("melons", "AG_MEL", [568], "Cantaloupes and other melons"),
    ("tubers", "AG_TUB", ROOTS, "Roots and tubers: production-weighted mean"),
    ("potatoes", "AG_POT", [116], "Potatoes"),
    ("yams", "AG_YAM", [137], "Yams"),
    ("coconut", "AG_CNT", [249], "Coconuts, in shell"),
    ("condiments_spices", "AG_CON", SPICES, "Spices: production-weighted mean"),
    ("milk", "GA_LEC;GA_BOVLEC;GA_MILK", [882], "Raw milk of cattle"),
    ("beef", "GA_CARBOV;GA_BOV", [867], "Meat of cattle with the bone, fresh or chilled"),
    ("beef_biological", "GA_CARBOV;GA_BOV (FAO '(biological)' series)", [945], "Meat of cattle with the bone, fresh or chilled (biological)"),
    ("pigmeat", "GA_CARPOR;GA_POR", [1035], "Meat of pig with the bone, fresh or chilled"),
    ("poultry_meat", "GA_CARPOL;GA_AVE", [1058], "Meat of chickens, fresh or chilled"),
    ("sheep_meat", "GA_OVE;GA_OTRCAR", [977], "Meat of sheep, fresh or chilled"),
    ("goat_meat", "GA_CBR;GA_OTRCAR", [1017], "Meat of goat, fresh or chilled"),
    ("pigmeat_biological", "GA_CARPOR;GA_POR (FAO '(biological)' series)", [1056], "Meat of pig with the bone, fresh or chilled (biological)"),
    ("poultry_meat_biological", "GA_CARPOL;GA_AVE (FAO '(biological)' series)", [1095], "Meat of chickens, fresh or chilled (biological)"),
    ("sheep_meat_biological", "GA_OVE;GA_OTRCAR (FAO '(biological)' series)", [1013], "Meat of sheep, fresh or chilled (biological)"),
    ("goat_meat_biological", "GA_CBR;GA_OTRCAR (FAO '(biological)' series)", [1033], "Meat of goat, fresh or chilled (biological)"),
    ("horse_meat", "GA_CAB", [1097], "Horse meat, fresh or chilled"),
    ("other_mammal_meat", "GA_CAM;GA_MUL", [1166], "Other meat of mammals, fresh or chilled"),
]

LIVE = {"An": 1.0, "1000 An": 1000.0, "No": 1.0}


def trade():
    t = pd.read_csv(os.path.join(DL, "subset_trade_6countries_2019_2023.csv"))
    t = t[t.Element.isin(["Import quantity", "Import value"])]
    rows, maprows = [], []
    for item, techs, codes, label, qunit in TRADE:
        maprows.append(dict(domain="TCL (trade)", model_item=item, model_techs=techs,
                            fao_item_codes=";".join(map(str, codes)), fao_items=label, unit_basis=qunit))
        s = t[t["Item Code"].isin(codes)]
        for country, cc in CC.items():
            c = s[s.Area == country]
            yrs = []
            for y in range(2019, 2024):
                cy = c[c.Year == y]
                q = cy[cy.Element == "Import quantity"]
                v = cy[cy.Element == "Import value"]
                qty = (q.Value * q.Unit.map(LIVE).fillna(1.0)).sum() if len(q) else float("nan")
                val = v.Value.sum() if len(v) else float("nan")
                uv = val * 1000 / qty if qty and qty > 0 and val == val else float("nan")
                f = cpi[y]
                flags = ";".join(sorted(set(cy.Flag.dropna().astype(str))))
                yrs.append((y, qty, val, uv, f))
                rows.append(dict(country=cc, model_item=item, model_techs=techs,
                                 fao_item_codes=";".join(map(str, codes)), fao_items=label, year=str(y),
                                 import_quantity=round(qty, 2) if qty == qty else "", quantity_unit=qunit,
                                 import_value_kusd=round(val, 2) if val == val else "",
                                 unit_value_usd_per_unit=round(uv, 2) if uv == uv else "",
                                 cpi_factor=f, unit_value_2024usd=round(uv * f, 2) if uv == uv else "",
                                 fao_flags=flags, note=""))
            ok = [(y, q, v, uv, f) for y, q, v, uv, f in yrs if uv == uv and q > 0]
            if ok:
                wq = sum(q for _, q, _, _, _ in ok)
                wv = sum(v * 1000 * f for _, _, v, _, f in ok)
                simple = sum(uv * f for _, _, _, uv, f in ok) / len(ok)
                note = f"{len(ok)} of 5 years with quantity > 0; simple mean of real annual unit values = {simple:.2f}"
                if wq < (100 if qunit == "t" else 10):
                    note += "; small volume, unit value unreliable"
                rows.append(dict(country=cc, model_item=item, model_techs=techs,
                                 fao_item_codes=";".join(map(str, codes)), fao_items=label,
                                 year="avg_2019_2023", import_quantity=round(wq / len(ok), 2), quantity_unit=qunit,
                                 import_value_kusd="", unit_value_usd_per_unit="", cpi_factor="",
                                 unit_value_2024usd=round(wv / wq, 2), fao_flags="",
                                 note="quantity-weighted mean of real 2024 USD unit values (sum of deflated values / sum of quantities); import_quantity is the annual mean; " + note))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(GEN, "faostat_trade_unit_values.csv"), index=False, lineterminator="\n")
    return maprows


def prices():
    p = pd.read_csv(os.path.join(DL, "subset_prices_6countries_2019_2023.csv"))
    p = p[p.Element == "Producer Price (USD/tonne)"]
    pr = pd.read_csv(os.path.join(DL, "subset_production_6countries_2019_2023.csv"))
    prod = pr[(pr.Element == "Production") & (pr.Unit == "t")]
    rows, maprows = [], []
    for item, techs, codes, label in PRICES:
        maprows.append(dict(domain="PP (producer prices)", model_item=item, model_techs=techs,
                            fao_item_codes=";".join(map(str, codes)), fao_items=label, unit_basis="t"))
        for country, cc in CC.items():
            vals = []
            for y in range(2019, 2024):
                pc = p[(p.Area == country) & (p.Year == y) & p["Item Code"].isin(codes)]
                if pc.empty:
                    continue
                if len(codes) == 1:
                    price = float(pc.Value.iloc[0])
                    used = str(codes[0])
                    note = ""
                else:
                    w = prod[(prod.Area == country) & (prod.Year == y)].set_index("Item Code").Value
                    pc = pc.assign(w=pc["Item Code"].map(w)).dropna(subset=["w"])
                    pc = pc[pc.w > 0]
                    if pc.empty:
                        continue
                    price = float((pc.Value * pc.w).sum() / pc.w.sum())
                    used = ";".join(str(int(c)) for c in pc["Item Code"])
                    note = f"production-weighted mean of {len(pc)} items (weights: FAOSTAT QCL production t, same year)"
                f = cpi[y]
                vals.append(price * f)
                rows.append(dict(country=cc, model_item=item, model_techs=techs, fao_item_codes=used,
                                 fao_items=label, year=str(y), producer_price_usd_per_t=round(price, 2),
                                 cpi_factor=f, producer_price_2024usd_per_t=round(price * f, 2), note=note))
            if vals:
                rows.append(dict(country=cc, model_item=item, model_techs=techs,
                                 fao_item_codes=";".join(map(str, codes)), fao_items=label, year="avg_2019_2023",
                                 producer_price_usd_per_t="", cpi_factor="",
                                 producer_price_2024usd_per_t=round(sum(vals) / len(vals), 2),
                                 note=f"simple mean of {len(vals)} real 2024 USD annual prices"))
    pd.DataFrame(rows).to_csv(os.path.join(GEN, "faostat_producer_prices.csv"), index=False, lineterminator="\n")
    return maprows


def yields():
    pr = pd.read_csv(os.path.join(DL, "subset_production_6countries_2019_2023.csv"))
    rows = []
    crops = [(i, t, c, l) for i, t, c, l in PRICES if c[0] < 860]
    for item, techs, codes, label in crops:
        for country, cc in CC.items():
            c = pr[(pr.Area == country) & pr["Item Code"].isin(codes)]
            prod = c[(c.Element == "Production") & (c.Unit == "t")].groupby("Year").Value.sum()
            area = c[c.Element == "Area harvested"].groupby("Year").Value.sum()
            yrs = sorted(set(prod.index) & set(area.index))
            yrs = [y for y in yrs if area[y] > 0]
            if not yrs:
                continue
            for y in yrs:
                rows.append(dict(country=cc, model_item=item, model_techs=techs,
                                 fao_item_codes=";".join(map(str, codes)), fao_items=label, year=str(y),
                                 production_t=round(prod[y], 1), area_harvested_ha=round(area[y], 1),
                                 yield_t_per_ha=round(prod[y] / area[y], 3), note=""))
            rows.append(dict(country=cc, model_item=item, model_techs=techs,
                             fao_item_codes=";".join(map(str, codes)), fao_items=label, year="avg_2019_2023",
                             production_t=round(sum(prod[y] for y in yrs) / len(yrs), 1),
                             area_harvested_ha=round(sum(area[y] for y in yrs) / len(yrs), 1),
                             yield_t_per_ha=round(sum(prod[y] for y in yrs) / sum(area[y] for y in yrs), 3),
                             note=f"{len(yrs)} years; yield = sum production / sum area harvested (group items summed)"))
    pd.DataFrame(rows).to_csv(os.path.join(GEN, "faostat_yields.csv"), index=False, lineterminator="\n")


if __name__ == "__main__":
    m = trade() + prices()
    yields()
    pd.DataFrame(m).to_csv(os.path.join(GEN, "faostat_item_mapping.csv"), index=False, lineterminator="\n")
    print("done")
