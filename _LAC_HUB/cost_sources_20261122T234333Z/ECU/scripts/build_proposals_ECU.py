"""Build the ECU proposal, source, search-log and manual-download files.

Run: python -I build_proposals_ECU.py (from any folder).
Inputs: ../cells_ECU.csv, the GEN FAOSTAT tables (GEN-201 to GEN-203), the
FAOSTAT production subset (via fao_groups_ECU.py) and the values read from the
downloaded Ecuadorian documents (ECU-001 to ECU-004), entered below with page.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fao_groups_ECU as fg  # noqa: E402

CC_DIR = os.path.dirname(HERE)
JOB = os.path.dirname(CC_DIR)
GEN = os.path.join(JOB, "GEN")

CPI = {2010: 1.438571, 2012: 1.366277, 2014: 1.325058, 2022: 1.071873, 2023: 1.029494}
FAO_CPI = "per year 1.226992 (2019) to 1.029494 (2023), GEN-001"
FLAT = "Flat row: base-year cell only, every year takes it."


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def gen_row(fname, item, col):
    for r in read(os.path.join(GEN, fname)):
        if r["country"] == "ECU" and r["model_item"] == item and r["year"] == "avg_2019_2023":
            return float(r[col]), r
    raise KeyError(item)


def pp(item):
    return gen_row("faostat_producer_prices.csv", item, "producer_price_2024usd_per_t")[0]


def yl(item):
    return gen_row("faostat_yields.csv", item, "yield_t_per_ha")[0]


def tuv(item):
    return gen_row("faostat_trade_unit_values.csv", item, "unit_value_2024usd")


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


# Model activity units, read from the compiled BAU parameters (OutputActivityRatio,
# InputActivityRatio, SpecifiedAnnualDemand): crops and livestock use E2_CRO / E2_PAS land
# at ratio 1, so their activity is Mha; imports output E3_* at ratio 1, crops in Mt and
# livestock in million head (E5GAN* demands are herd sizes, e.g. 58.3 million birds).
OAR = {"AG_ARR": 4.420505405826361, "AG_COF": 0.16678538719853467, "AG_SUG": 77.71341443115008,
       "AG_MAI": 4.208932635411925, "AG_SOY": 1.0675280480672091, "AG_PAL": 6.5500556145042585,
       "AG_LEG": 1.4155396702730552, "AG_CER": 1.4921974083264409, "AG_TUB": 9.324991795208403,
       "AG_FRT": 6.667458901665889, "AG_VEG": 14.623969180071411,
       "GA_BOV": 1.638103614705104, "GA_BOVLEC": 1.638103614705104, "GA_OVE": 0.0107,
       "GA_CBR": 0.0107, "GA_CAM": 0.1068, "GA_CAB": 0.5339, "GA_MUL": 0.1068, "GA_POR": 0.0107,
       "GA_AVE": 0.0107}

# Fixed share of the total cost per hectare in the MAG hard-maize budget (ECU-002):
# fixed 304.02 of total 1,762.08 US$ per ha.
F_SHARE = 304.02 / 1762.08

out = {}  # (tech, parameter) -> dict(fields)


def put(tech, par, value, cls, sids="", sval="", sunit="", scy="", cpi="", deriv="", assum=""):
    out[(tech, par)] = dict(proposed_value=value, change_class=cls, source_ids=sids, source_value=sval,
                            source_unit=sunit, source_currency_year=scy, cpi_factor=cpi,
                            derivation=deriv, assumption_sentence=assum)


def fmt(x):
    return "%.2f" % x if abs(x) >= 1 else "%.4f" % x


# ---------------------------------------------------------------- crops (Secondary Techs)
UNIT_CROP = ("Unit assumed: US$ per hectare (M US$ per Mha); the activity of the crop is land in Mha "
             "(InputActivityRatio 1 on E2_CRO) and the model yield is %s t per ha (OutputActivityRatio to E3_%s, Mt).")

# Rice: MAGAP budget for technified rice, 2012 costs (ECU-001, Tabla 3.5, MAGAP column).
r_land, r_cap = 210.00, 56.01
r_nt, r_tr = 961.01, 560.29
r_total = r_nt + r_tr
r_var = (r_total - r_land - r_cap) * CPI[2012]
r_fix = (r_land + r_cap) * CPI[2012]
rice_note = ("MAGAP rice budget for one hectare of technified rice (75 sacks of 205 lb per ha, about 6.97 t per ha), "
             "2012 costs, as reproduced in Castillo (2013) for Rimisp, Tabla 3.5, PDF p. 30: non-tradable factors 961.01 US$ "
             "(labour 377.50, water 40.00, land rent 210.00, capital 56.01, non-tradable machinery 277.50) plus tradable inputs "
             "560.29 US$ (fertiliser and agrochemicals 315.29, seed 60.00, tradable machinery 185.00) = 1,521.30 US$ per ha.")
put("AG_ARR", "VariableCost", r_var, "replace", "ECU-001;GEN-001", "961.01 + 560.29", "US$ per ha (rice, total cost per hectare)",
    "2012", "%.6f" % CPI[2012],
    rice_note + " Variable part = total less land rent and capital = 1,255.29 US$ (2012) x CPI factor 1.366277 = %s US$ per ha (2024 USD). "
    % fmt(r_var) + UNIT_CROP % ("4.42", "ARR") + " FAOSTAT gives 3.60 t per ha for 2019 to 2023 (GEN-203), so the MAGAP budget is for an "
    "above-average yield; the FAOSTAT value of production is 381.2 US$ per t x 3.599 t per ha = 1,372 US$ per ha (GEN-202, GEN-203). "
    + FLAT + " Sourced value %s against current 1: differs by more than 25 percent, sourced value proposed." % fmt(r_var))
put("AG_ARR", "FixedCost", r_fix, "replace", "ECU-001;GEN-001", "210.00 + 56.01", "US$ per ha (rice land rent and capital cost)",
    "2012", "%.6f" % CPI[2012],
    rice_note + " Fixed part = land rent 210.00 + capital 56.01 = 266.01 US$ (2012) x CPI factor 1.366277 = %s US$ per ha (2024 USD); "
    "17.5 percent of the total, close to the 17.3 percent fixed share of the MAG hard-maize budget (ECU-002). " % fmt(r_fix)
    + UNIT_CROP % ("4.42", "ARR") + " " + FLAT + " Sourced value %s against current 1: differs by more than 25 percent, sourced value proposed." % fmt(r_fix))

# Maize: MAG summer 2022 hard yellow maize cost (ECU-002).
m_var = 1458.06 * CPI[2022]
m_fix = 304.02 * CPI[2022]
maize_note = ("MAG cost of production of hard yellow maize, summer 2022 cycle, as reported by Ibarra Velasquez et al. (2023) in Polo del "
              "Conocimiento (section Costos de produccion de maiz duro amarillo and Figura 3, source MAG 2022 balance of supply and demand): "
              "variable cost 1,458.06 US$, fixed cost 304.02 US$, total 1,762.08 US$ per ha at 127 quintals per ha (wet and dirty grain).")
put("AG_MAI", "VariableCost", m_var, "replace", "ECU-002;GEN-001", "1.458,06", "US$ per ha (hard maize, variable cost)", "2022",
    "%.6f" % CPI[2022], maize_note + " 1,458.06 x CPI factor 1.071873 = %s US$ per ha (2024 USD). " % fmt(m_var)
    + UNIT_CROP % ("4.21", "MAI") + " " + FLAT + " Sourced value %s against current 1: differs by more than 25 percent, sourced value proposed." % fmt(m_var))
put("AG_MAI", "FixedCost", m_fix, "replace", "ECU-002;GEN-001", "304,02", "US$ per ha (hard maize, fixed cost)", "2022",
    "%.6f" % CPI[2022], maize_note + " 304.02 x CPI factor 1.071873 = %s US$ per ha (2024 USD). " % fmt(m_fix)
    + UNIT_CROP % ("4.21", "MAI") + " " + FLAT + " Sourced value %s against current 1: differs by more than 25 percent, sourced value proposed." % fmt(m_fix))

# Crops without a national budget: total cost per ha = value of production per ha
# (FAOSTAT producer price x yield, 2019-2023, real 2024 USD), split with the MAG maize fixed share.
oc = fg.group(["15", "44", "71", "75", "79", "83", "92", "108"])
fr = fg.group(["490", "495", "497", "507", "512", "515", "521", "526", "531", "534", "536", "544", "547",
               "558", "560", "567", "568", "569", "571", "572", "574", "600", "603", "619"])
pal_price, pal_yield = 0.33, 5.57  # ECU-004: US$ per kg producer price 2023; t per ha 2023 (ESPAC)
crops = {
    "AG_COF": ("coffee", pp("coffee"), yl("coffee"), "FAOSTAT green coffee producer price (one year with a price) and yield",
               "GEN-202;GEN-203", "coffee (green bean)"),
    "AG_SUG": ("sugarcane", pp("sugar_cane"), yl("sugar_cane"), "FAOSTAT sugar cane producer price and yield", "GEN-202;GEN-203", "sugarcane"),
    "AG_SOY": ("soy", pp("soy"), yl("soy"), "FAOSTAT soya bean producer price and yield", "GEN-202;GEN-203", "soya beans"),
    "AG_LEG": ("legumes", pp("legumes_pulses"), yl("legumes_pulses"), "FAOSTAT pulses (production-weighted) producer price and yield",
               "GEN-202;GEN-203", "pulses"),
    "AG_CER": ("cereals", oc["price"], oc["yield"], "FAOSTAT cereals other than rice and maize (wheat, barley, rye, oats, sorghum, quinoa), "
               "production-weighted producer price and summed yield", "GEN-202;GEN-203", "cereals other than rice and maize"),
    "AG_TUB": ("tubers", pp("tubers"), yl("tubers"), "FAOSTAT roots and tubers (production-weighted) producer price and yield",
               "GEN-202;GEN-203", "roots and tubers"),
    "AG_FRT": ("fruits", fr["price"], fr["yield"], "FAOSTAT fruit other than bananas and plantains (production-weighted) producer price and "
               "summed yield", "GEN-202;GEN-203", "fruit other than bananas and plantains"),
    "AG_VEG": ("vegetables", pp("vegetables"), yl("vegetables"), "FAOSTAT vegetables (production-weighted) producer price and yield",
               "GEN-202;GEN-203", "vegetables"),
    "AG_PAL": ("palm hearts", pal_price * 1000 * CPI[2023], pal_yield, "MAG producer price of palm hearts (about 0.33 US$ per kg in 2023, "
               "national weighted mean) and the 2023 national yield of 5.57 t per ha (INEC ESPAC), both in the MAG palm heart bulletin 2023",
               "ECU-004;GEN-001", "palm hearts (palmito)"),
}
cap = {"AG_COF": (3000, "coffee", "2,000 to 4,000"), "AG_SUG": (2000, "sugarcane", "1,500 to 3,000"),
       "AG_PAL": (3000, "palm hearts", "2,000 to 4,000"), "AG_FRT": (3000, "fruit orchards", "2,000 to 5,000")}
for tech, (lab, price, yld, how, sids, word) in crops.items():
    total = price * yld
    var = total * (1 - F_SHARE)
    fix = total * F_SHARE
    code = tech[3:]
    basis = ("%s: %s US$ per t x %s t per ha = %s US$ per ha (real 2024 USD, 2019 to 2023 unless stated). " %
             (how, fmt(price), "%.3f" % yld, fmt(total)))
    if tech == "AG_PAL":
        basis = ("%s: 330 US$ per t (2023) x CPI factor 1.029494 = %s US$ per t x 5.57 t per ha = %s US$ per ha (2024 USD). "
                 "FAOSTAT has no palm heart producer price. " % (how, fmt(price), fmt(total)))
    common = (basis + "Value of production per ha taken as the total cost per ha (no national cost budget for this crop could be downloaded); "
              "split with the fixed share of the MAG hard-maize budget, 304.02 / 1,762.08 = 0.1725 (ECU-002). " +
              UNIT_CROP % ("%.2f" % OAR[tech], code) + " " + FLAT)
    put(tech, "VariableCost", var, "assumption", sids, "", "", "", "",
        common + " Variable part = total x 0.8275 = %s." % fmt(var),
        "Growing one hectare of %s in Ecuador costs %s US$ a year in variable inputs and labour (2024 USD), taken as 83 percent of the "
        "value of production per hectare (producer price x national yield, FAOSTAT 2019 to 2023 or the Ministry of Agriculture bulletin), "
        "the variable share of the Ministry of Agriculture hard-maize cost budget of 2022. Range 70 to 130 percent of this value."
        % (word, "{:,.0f}".format(var)))
    put(tech, "FixedCost", fix, "assumption", sids, "", "", "", "",
        common + " Fixed part = total x 0.1725 = %s." % fmt(fix),
        "Fixed costs of %s (land rent, administration, interest) are %s US$ per hectare a year (2024 USD), 17 percent of the value of "
        "production per hectare, the fixed share of the Ministry of Agriculture hard-maize cost budget of 2022 (304 of 1,762 US$ per ha). "
        "Range 10 to 25 percent of the value of production." % (word, "{:,.0f}".format(fix)))
    if tech in cap:
        c, w, rng = cap[tech]
        put(tech, "CapitalCost", c, "assumption", "", "", "", "", "",
            "Perennial crop: establishment cost per hectare of new area. " + UNIT_CROP % ("%.2f" % OAR[tech], code) + " " + FLAT,
            "Establishing one hectare of %s costs about %s US$ (2024 USD), covering land preparation, planting material and the upkeep of "
            "the first unproductive years; yearly renovation of existing plantations sits in the yearly costs. Range %s US$ per hectare."
            % (w, "{:,.0f}".format(c), rng))
for tech, word in [("AG_ARR", "rice"), ("AG_MAI", "hard maize"), ("AG_SOY", "soya beans"), ("AG_LEG", "pulses"),
                   ("AG_CER", "cereals"), ("AG_TUB", "roots and tubers"), ("AG_VEG", "vegetables")]:
    put(tech, "CapitalCost", 0, "assumption", "", "", "", "", "",
        "Annual crop. " + UNIT_CROP % ("%.2f" % OAR[tech], tech[3:]) + " " + FLAT,
        "An annual crop of %s carries no capital cost per hectare: machinery is hired by the hour and its cost, like land preparation, "
        "is part of the yearly cost per hectare (as in the Ministry of Agriculture rice and maize budgets). If owned machinery or irrigation "
        "were counted, a range of 0 to 1,500 US$ per hectare applies." % word)

# ---------------------------------------------------------------- livestock (Secondary Techs)
UNIT_LS = ("Unit assumed: US$ per hectare of pasture (M US$ per Mha); the activity is pasture land in Mha (InputActivityRatio 1 on E2_PAS) "
           "and the model stocking rate is %s head per ha (OutputActivityRatio to E3_%s, million head). Cost per ha = cost per head x %s.")
# Beef cattle: Rimisp focal groups of Balzar, Chone and Vinces (ECU-003, Tabla 23).
per_head = mean([159.4, 157.4, 285.5])
b_var = per_head * OAR["GA_BOV"] * CPI[2014]
put("GA_BOV", "VariableCost", b_var, "replace", "ECU-003;GEN-001", "159.4; 157.4; 285.5", "US$ per head per year (beef cattle, total cost)",
    "2014", "%.6f" % CPI[2014],
    "Castillo (2015) for Rimisp, Tabla 23 (PDF p. 48): average yearly cost per head of beef cattle in the focal groups of Balzar, Chone and "
    "Vinces (pasture upkeep, supplementary feed, herding, animal health, other) 159.4, 157.4 and 285.5 US$ (per ha 143.5, 159.4, 555.0 at "
    "0.97 to 2.03 head per ha); mean %.2f US$ per head (2014) x 1.6381 head per ha = %.2f US$ per ha x CPI factor 1.325058 = %s US$ per ha "
    "(2024 USD). Land rent and the value of the herd are not in these costs. " % (per_head, per_head * OAR["GA_BOV"], fmt(b_var))
    + UNIT_LS % ("1.638", "BOV", "1.638") + " " + FLAT + " Sourced value %s against current 1: differs by more than 25 percent, sourced value proposed." % fmt(b_var))
b_fix = b_var * F_SHARE / (1 - F_SHARE)
put("GA_BOV", "FixedCost", b_fix, "assumption", "", "", "", "", "",
    "VariableCost %s x 0.1725 / 0.8275 (fixed share of the MAG hard-maize budget, ECU-002) = %s. " % (fmt(b_var), fmt(b_fix))
    + UNIT_LS % ("1.638", "BOV", "1.638") + " " + FLAT,
    "Fixed costs of beef cattle (land rent, taxes, administration) are %s US$ per hectare of pasture a year (2024 USD), set so that they "
    "are 17 percent of the total cost, the fixed share of the Ministry of Agriculture hard-maize cost budget of 2022. Range 10 to 25 percent "
    "of the total." % "{:,.0f}".format(b_fix))

# Value of output per head of stock (FAOSTAT, real 2024 USD) for dairy, sheep, goats, pigs, poultry.
milk_y = mean(fg.series("882", "Yield/Carcass Weight").values()) / 1000.0  # t per milking animal
milk_p = pp("milk")


def per_stock(meat_code, stock_code, price, carcass_scale=1.0):
    carc = mean(fg.series(meat_code, "Yield/Carcass Weight").values()) * carcass_scale / 1000.0  # t per head
    sl = fg.series(meat_code, "Producing Animals/Slaughtered")
    st = fg.series(stock_code, "Stocks")
    yrs = [y for y in sl if y in st]
    turn = sum(sl[y] for y in yrs) / sum(st[y] for y in yrs)
    return carc * price * turn, carc, turn


sheep_p = pp("sheep_meat_biological")
ls = {}
v, c, t = per_stock("977", "976", sheep_p)
ls["GA_OVE"] = (v, "sheep", "carcass %.1f kg x FAOSTAT sheep meat producer price %s US$ per t x %.3f slaughtered per head of stock" % (c * 1000, fmt(sheep_p), t))
v, c, t = per_stock("1017", "1016", sheep_p)
ls["GA_CBR"] = (v, "goats", "carcass %.1f kg x FAOSTAT sheep meat producer price %s US$ per t (no goat price for Ecuador) x %.3f slaughtered per head of stock" % (c * 1000, fmt(sheep_p), t))
pig_p = pp("pigmeat_biological")
v, c, t = per_stock("1035", "1034", pig_p)
ls["GA_POR"] = (v, "pigs", "carcass %.1f kg x FAOSTAT pig meat producer price %s US$ per t x %.3f slaughtered per head of stock" % (c * 1000, fmt(pig_p), t))
chk_p = pp("poultry_meat_biological")
v, c, t = per_stock("1058", "1057", chk_p, carcass_scale=0.001)  # g per animal; both counts in 1000 An
ls["GA_AVE"] = (v, "poultry", "carcass %.2f kg x FAOSTAT chicken meat producer price %s US$ per t x %.3f slaughtered per bird of stock" % (c * 1000, fmt(chk_p), t))
ls["GA_BOVLEC"] = (milk_y * milk_p, "dairy cattle", "milk %.3f t per milking animal (FAOSTAT 2019 to 2023 mean) x FAOSTAT raw milk producer price %s US$ per t" % (milk_y, fmt(milk_p)))
ls["GA_CAM"] = (30.0, "South American camelids", None)
ls["GA_CAB"] = (100.0, "horses", None)
ls["GA_MUL"] = (100.0, "mules", None)
rng_head = {"GA_CAM": "15 to 60", "GA_CAB": "50 to 250", "GA_MUL": "50 to 250"}
for tech, (vh, word, how) in ls.items():
    o = OAR[tech]
    total = vh * o
    var, fix = total * (1 - F_SHARE), total * F_SHARE
    u = UNIT_LS % (("%.4f" % o).rstrip("0"), tech[3:], ("%.4f" % o).rstrip("0"))
    if how:
        base = ("Value of output per head of stock a year = %s = %s US$ (real 2024 USD, GEN-202, GEN-203), taken as the yearly cost per head; "
                "per ha = %s x %s = %s US$; " % (how, fmt(vh), fmt(vh), ("%.4f" % o).rstrip("0"), fmt(total)))
        sids = "GEN-202;GEN-203"
        what = "the value of output per head (FAOSTAT 2019 to 2023)"
        rng = "70 to 130 percent of this value"
    else:
        base = "Upkeep cost of %s US$ per head a year (ASSUMPTION, no output value); per ha = %s x %s = %s US$; " % (fmt(vh), fmt(vh), ("%.4f" % o).rstrip("0"), fmt(total))
        sids = ""
        what = "an upkeep cost of %s US$ per head a year (feed beyond grazing, health, shoeing or shearing)" % "{:,.0f}".format(vh)
        rng = "%s US$ per head a year" % rng_head[tech]
    base += "split with the MAG hard-maize fixed share 0.1725 (ECU-002). " + u + " " + FLAT
    flag = (" The stocking rate %s head per ha in the model is far below real densities, so the per-hectare value is small; "
            "per head the cost is %s US$." % (("%.4f" % o).rstrip("0"), fmt(vh))) if o < 0.2 else ""
    put(tech, "VariableCost", var, "assumption", sids, "", "", "", "", base + " Variable part = %s." % fmt(var) + flag,
        "Keeping %s costs %s US$ per hectare of pasture a year in variable inputs and labour (2024 USD): 83 percent of %s at the model's "
        "%s head per hectare, the variable share of the Ministry of Agriculture hard-maize cost budget of 2022. Range %s."
        % (word, fmt(var), what, ("%.4f" % o).rstrip("0"), rng))
    put(tech, "FixedCost", fix, "assumption", sids, "", "", "", "", base + " Fixed part = %s." % fmt(fix) + flag,
        "Fixed costs of %s (land rent, administration) are %s US$ per hectare of pasture a year (2024 USD): 17 percent of %s at the "
        "model's %s head per hectare, the fixed share of the Ministry of Agriculture hard-maize cost budget of 2022. Range 10 to 25 percent."
        % (word, fmt(fix), what, ("%.4f" % o).rstrip("0")))
for tech, word in [("GA_BOV", "beef cattle"), ("GA_BOVLEC", "dairy cattle"), ("GA_OVE", "sheep"), ("GA_CBR", "goats"),
                   ("GA_CAM", "South American camelids"), ("GA_CAB", "horses"), ("GA_MUL", "mules"), ("GA_POR", "pigs"), ("GA_AVE", "poultry")]:
    o = ("%.4f" % OAR[tech]).rstrip("0")
    put(tech, "CapitalCost", 0, "assumption", "", "", "", "", "",
        UNIT_LS % (o, tech[3:], o) + " " + FLAT,
        "Raising %s carries no capital cost per hectare of pasture: the herd and existing pasture are in place, and their upkeep is in the "
        "yearly costs. If new pasture, fencing and water points were counted, a range of 300 to 800 US$ per hectare applies." % word)

# ---------------------------------------------------------------- imports (Primary Techs)
UNIT_IMP_T = "Unit assumed: US$ per t (M US$ per Mt); the import activity is product in Mt (OutputActivityRatio 1 to E3_%s, the same fuel the crop makes in Mt)."
UNIT_IMP_H = "Unit assumed: US$ per head (M US$ per million head); the import activity is animals in million head (OutputActivityRatio 1 to E3_%s, the herd fuel whose demand is counted in million head)."
imp_t = {"IMPARR": ("rice", "ARR", ""), "IMPCOF": ("coffee", "COF", ""), "IMPMAI": ("maize", "MAI", ""),
         "IMPLEG": ("legumes_pulses", "LEG", ""), "IMPCER": ("cereals", "CER", " The import activity bounds (1.49 to 1.64 Mt in 2021) match FAOSTAT cereal imports of about 1.5 Mt a year, mostly wheat."),
         "IMPTUB": ("tubers", "TUB", ""), "IMPFRT": ("fruit", "FRT", ""), "IMPVEG": ("vegetables", "VEG", ""),
         "IMPPAL": ("palm_hearts", "PAL", " AG_PAL is palm hearts (palmito, 5.6 to 6.6 t per ha), not oil palm (AG_PAF); FAO item 472 is a broad preserved-vegetables item that holds preserved palm hearts, so the value is a processed-product price."),
         "IMPBOV": ("live_cattle", "BOV", " Live cattle imports are breeding stock (52 head a year on average, two years with imports), so the unit value is far above the value of a slaughter animal."),
         "IMPPOR": ("live_pigs", "POR", " Live pig imports are breeding stock (570 head a year)."),
         "IMPAVE": ("live_chickens", "AVE", " Live chicken imports (2.5 million head a year) are mostly breeding chicks."),
         "IMPCAB": ("live_horses", "CAB", " Live horse imports (116 head a year) are mostly pedigree animals.")}
for tech, (item, code, note) in imp_t.items():
    v, r = tuv(item)
    head = item.startswith("live_")
    unit = UNIT_IMP_H % code if head else UNIT_IMP_T % code
    put(tech, "VariableCost", v, "replace", "GEN-201;GEN-001", "%.2f" % v,
        "US$ per %s (FAOSTAT import unit value, quantity-weighted mean 2019 to 2023, real 2024 USD)" % ("head" if head else "t"),
        "2019-2023", FAO_CPI,
        "FAOSTAT import unit value for Ecuador, item %s (FAO %s), quantity-weighted mean of 2019 to 2023 in real 2024 USD = %s US$ per %s "
        "(GEN-201; each year deflated with its own CPI factor; mean import %s %s a year). %s%s %s Sourced value %s against current 1: differs by "
        "more than 25 percent, sourced value proposed." % (r["fao_items"], r["fao_item_codes"], fmt(v), "head" if head else "t",
                                                           "{:,.0f}".format(float(r["import_quantity"])), r["quantity_unit"], unit, note, FLAT, fmt(v)))
# Sugarcane import: cane-equivalent of the sugar import unit value.
sv, _ = tuv("sugar")
cane = fg.series("156", "Production")
sug = fg.series("162", "Production")
ratio = sum(sug.values()) / sum(cane.values())
cane_v = sv * ratio
put("IMPSUG", "VariableCost", cane_v, "replace", "GEN-201;GEN-203;GEN-001", "%.2f" % sv,
    "US$ per t of sugar (FAOSTAT import unit value raw plus refined sugar, quantity-weighted mean 2019 to 2023, real 2024 USD)", "2019-2023", FAO_CPI,
    "Sugar cane itself is hardly imported (1 t in five years), so the sugar import unit value (FAO 162 + 164) %s US$ per t (GEN-201) is "
    "converted to cane equivalent with the national ratio of raw sugar to sugar cane production 2019 to 2023, %s / %s t = %.4f (GEN-203): "
    "%s x %.4f = %s US$ per t of cane. Comparison: FAOSTAT producer price of sugar cane in Ecuador 35.03 US$ per t (GEN-202). %s %s Sourced value %s "
    "against current 1: differs by more than 25 percent, sourced value proposed." % (fmt(sv), "{:,.0f}".format(sum(sug.values())),
                                                                                    "{:,.0f}".format(sum(cane.values())), ratio, fmt(sv), ratio, fmt(cane_v),
                                                                                    UNIT_IMP_T % "SUG", FLAT, fmt(cane_v)))
soy_pp = pp("soy")
put("IMPSOY", "VariableCost", soy_pp, "assumption", "GEN-202", "", "", "", "",
    "FAOSTAT soya bean imports of Ecuador are 52 t (2019) and 4 t (2020) at 2,737 and 5,483 US$ per t (real 2024), a seed price, so no "
    "usable import unit value exists. " + UNIT_IMP_T % "SOY" + " " + FLAT,
    "Imported soya beans cost %s US$ per t (2024 USD), the FAOSTAT producer price of soya beans in Ecuador for 2019 to 2023, taken as the "
    "import parity price since grain imports are almost nil. Range 450 to 900 US$ per t." % fmt(soy_pp))
sheep_head = ls["GA_OVE"][0]
car_sheep = mean(fg.series("977", "Yield/Carcass Weight").values())
car_goat = mean(fg.series("1017", "Yield/Carcass Weight").values())
imp_ass = {
    "IMPOVE": (car_sheep * sheep_p / 1000, "sheep", "Live sheep are not imported (FAOSTAT 2019 to 2023). ",
               "the carcass value of a sheep in Ecuador (%.1f kg x the FAOSTAT sheep meat producer price %s US$ per t)" % (car_sheep, fmt(sheep_p)), "30 to 150"),
    "IMPCBR": (car_goat * sheep_p / 1000, "goats", "Live goats are not imported (FAOSTAT 2019 to 2023). ",
               "the carcass value of a goat in Ecuador (%.1f kg x the FAOSTAT sheep meat producer price %s US$ per t)" % (car_goat, fmt(sheep_p)), "40 to 200"),
    "IMPCAM": (150.0, "South American camelids (llamas, alpacas)", "Live camelids are not imported (FAOSTAT 2019 to 2023). ",
               "a typical farm price of a llama or alpaca", "80 to 400"),
    "IMPMUL": (600.0, "mules", "Live mules are not imported (FAOSTAT 2019 to 2023). ",
               "a typical farm price of a working mule, well below the FAOSTAT unit value of imported horses (8,182 US$ per head), which are pedigree animals", "300 to 1,200"),
}
for tech, (v, word, why, basis, rng) in imp_ass.items():
    put(tech, "VariableCost", v, "assumption", "GEN-202;GEN-203" if tech in ("IMPOVE", "IMPCBR") else "", "", "", "", "",
        why + UNIT_IMP_H % tech[3:] + " " + FLAT,
        "An imported head of %s costs %s US$ (2024 USD), %s. Range %s US$ per head." % (word, fmt(v), basis, rng))
for r in read(os.path.join(CC_DIR, "cells_ECU.csv")):
    if r["tech"].startswith("IMP") and r["parameter"] in ("CapitalCost", "FixedCost"):
        head = r["tech"] in ("IMPBOV", "IMPOVE", "IMPCBR", "IMPCAM", "IMPCAB", "IMPMUL", "IMPPOR", "IMPAVE")
        put(r["tech"], r["parameter"], 0, "assumption", "", "", "", "", "",
            (UNIT_IMP_H if head else UNIT_IMP_T) % r["tech"][3:] + " " + FLAT,
            "Imports carry no %s: the import price per %s covers the supplier's costs, and port and transport capacity is not modelled "
            "per product. Range 0." % ("capital cost" if r["parameter"] == "CapitalCost" else "fixed cost", "head" if head else "tonne"))

# ---------------------------------------------------------------- waste
w_total = (34.22 + 12.01) * CPI[2010]
for par, cur in (("CapitalCost", 9.0), ("VariableCost", 29.7)):
    share = cur / 38.7
    put("BLEND_NO_DCOLL", par, w_total * share, "replace", "GEN-206;GEN-204;GEN-001", "34.22 + 12.01", "US$ per t", "2010", "%.6f" % CPI[2010],
        "CEPAL 2016, Cuadro 6 (Latin America and the Caribbean averages): collection (34.22) plus transfer (12.01) US$ per t, 2010 USD x CPI "
        "factor 1.438571 = %.2f US$ per t (2024 USD). Unit read as US$ per t (M US$ per Mt). Compared with the model's CapitalCost + "
        "VariableCost = 38.7 US$ per t (differs by more than 25 percent); split in the model's own proportion (this cell's share %.4f) = %s. "
        "What a Waste 2.0 (GEN-204, Table 5.2) gives 62 to 125 US$ per t for collection and transfer in upper-middle income countries such "
        "as Ecuador (2024 USD). No Ecuadorian cost per tonne could be read from a downloadable national document. %s"
        % (w_total, share, fmt(w_total * share), FLAT))

# ---------------------------------------------------------------- write proposals
cols = ["country", "model", "sheet", "tech", "tech_name", "parameter", "unit_introduced", "unit", "projection_mode", "year",
        "current_value", "proposed_value", "change_class", "source_ids", "source_value", "source_unit", "source_currency_year",
        "cpi_factor", "derivation", "assumption_sentence", "ao_row_at_b51f24b"]
rows = []
for c in read(os.path.join(CC_DIR, "cells_ECU.csv")):
    p = out[(c["tech"], c["parameter"])]
    row = {k: c.get(k, "") for k in cols}
    row.update(p)
    v = p["proposed_value"]
    row["proposed_value"] = "0" if v == 0 else ("%.2f" % v if abs(v) >= 1 else "%.6f" % v)
    if p["change_class"] == "confirmed":
        row["proposed_value"] = c["current_value"]
    row["ao_row_at_b51f24b"] = c["ao_row_at_b51f24b"]
    rows.append(row)
with open(os.path.join(CC_DIR, "proposals_ECU.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print("proposals:", len(rows))
