"""FAOSTAT group values for Ecuador used by build_proposals_ECU.py.

Reads the FAOSTAT subsets (GEN-202 prices, GEN-203 production) and returns,
for a list of FAO item codes, the 2019-2023 yield (sum production / sum area
harvested) and the simple mean of the production-weighted producer price in
real 2024 USD (each year deflated with its CPI factor, GEN-001).
"""
import csv
import collections
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(os.path.dirname(HERE))
SUB = os.path.join(JOB, "downloads", "GEN_sector")
CPI = {"2019": 1.226992, "2020": 1.212039, "2021": 1.157652, "2022": 1.071873, "2023": 1.029494}
YEARS = sorted(CPI)

_prod = None
_price = None
_names = {}


def _load():
    global _prod, _price
    if _prod is not None:
        return
    _prod = collections.defaultdict(dict)
    with open(os.path.join(SUB, "subset_production_6countries_2019_2023.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Area"] != "Ecuador":
                continue
            _names[r["Item Code"]] = r["Item"]
            if r["Value"]:
                _prod[(r["Item Code"], r["Element"])][r["Year"]] = float(r["Value"])
    _price = collections.defaultdict(dict)
    with open(os.path.join(SUB, "subset_prices_6countries_2019_2023.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Area"] != "Ecuador" or r["Element"] != "Producer Price (USD/tonne)":
                continue
            _price[r["Item Code"]][r["Year"]] = float(r["Value"])


def group(codes):
    _load()
    prod = sum(_prod[(c, "Production")].get(y, 0) for c in codes for y in YEARS)
    area = sum(_prod[(c, "Area harvested")].get(y, 0) for c in codes for y in YEARS)
    prices = []
    for y in YEARS:
        num = den = 0.0
        for c in codes:
            if y in _price.get(c, {}):
                q = _prod[(c, "Production")].get(y, 0)
                num += q * _price[c][y] * CPI[y]
                den += q
        if den:
            prices.append(num / den)
    price = sum(prices) / len(prices) if prices else None
    items = [(c, _names.get(c)) for c in codes if _prod.get((c, "Area harvested"))]
    return {"yield": prod / area if area else None, "price": price, "n_price_years": len(prices),
            "prod_mean": prod / 5, "area_mean": area / 5, "items": items}


def series(code, element):
    _load()
    return dict(_prod.get((code, element), {}))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oc = ["15", "44", "71", "75", "79", "83", "92", "108"]
    fr = ["490", "495", "497", "507", "512", "515", "521", "526", "531", "534", "536", "544", "547",
          "558", "560", "567", "568", "569", "571", "572", "574", "600", "603", "619"]
    for lab, cs in [("other cereals", oc), ("fruit excl banana plantain", fr)]:
        print(lab, group(cs))
    for c in ["156", "162", "164"]:
        print(c, _names.get(c), series(c, "Production"))
    for c in ["1016", "1017", "1033", "1034", "1057", "1058", "1035", "977", "866", "867"]:
        print(c, _names.get(c), series(c, "Stocks"), series(c, "Producing Animals/Slaughtered"),
              series(c, "Yield/Carcass Weight"))
