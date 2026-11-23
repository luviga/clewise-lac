"""Proposals for the vehicle CapitalCost cells in scope, from the class prices of build_prices.py.

Reads scope_cells.csv (cells, current values, units, projection modes and the later-year price
path of the cost-sources proposals), <CC>/class_prices_<CC>.csv, <CC>/unit_values_<CC>.csv and
parameters.csv. Writes <CC>/proposals_<CC>.csv: the columns of the cost-sources proposal files
plus unit_introduced_proposed, one row per cell.

    python -I scripts/build_proposals.py
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.dirname(HERE)
CCS = ["CR", "DR", "GUA", "HON", "JAM"]
TRAJ = "User defined trajectory relative to BY"

S_OTHER = ("No vehicles of this class were imported in sufficient number; the average customs value of the "
           "same tariff lines in the other four countries is used.")
S_RULE3 = ("No vehicles of this class and powertrain were imported in sufficient number in any of the five "
           "countries; the average customs value of the diesel vehicle of the same class is multiplied by the "
           "ratio of the two powertrains' prices in the NREL Annual Technology Baseline 2022.")
S_PATH = ("Prices after the base year follow the NREL Annual Technology Baseline 2022 Mid price path of the "
          "same class and powertrain, because no government statistic gives future prices.")
S_FLAT = ("The price is held at the base-year price in every year, because no published price path covers "
          "this vehicle class.")

COUNTRY = {"CR": "Costa Rica", "DR": "the Dominican Republic", "GUA": "Guatemala", "HON": "Honduras",
           "JAM": "Jamaica"}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def params():
    return {r["parameter"]: r["value"] for r in read_csv(os.path.join(JOB, "parameters.csv"))}


def fmt(x, nd=2):
    return f"{x:.{nd}f}"


def stat_text(cp, uv_all):
    """Recomputable description of a class price: per line and year the units, the customs value as
    published, the exchange rate and the CPI factor."""
    used = []
    for part in cp["detail"].split("; "):
        if not part:
            continue
        c, key = part.split(" ")[0], part.split(" ")[1]
        used.append((c, key))
    items = []
    srcs = set()
    for c, key in used:
        for x in uv_all[c]:
            if x["used_in_average"] != "yes":
                continue
            if (x["hs6"] and x["hs6"] == key) or (not x["hs6"] and x["type_label"] and x["type_label"].startswith(key)):
                lab = x["hs6"] or ("DGA type " + x["type_label"])
                items.append(f"{c} {lab} {x['year']}: {float(x['units']):.0f} units, {x['value_basis']} "
                             f"{float(x['customs_value']):.2f} {x['currency']}, rate {float(x['exchange_rate']):g}, "
                             f"CPI factor {float(x['cpi_factor']):.6f}")
                srcs.add(x["source_id"])
    return "; ".join(items), sorted(srcs)


def main():
    p = params()
    band = float(p["confirm_band"])
    cells = read_csv(os.path.join(JOB, "scope_cells.csv"))
    cps, uv_all = {}, {}
    for cc in CCS:
        uv_all[cc] = read_csv(os.path.join(JOB, cc, f"unit_values_{cc}.csv"))
        for r in read_csv(os.path.join(JOB, cc, f"class_prices_{cc}.csv")):
            cps[(cc, r["tech"])] = r
    # row-level info: unit, mode, base year, #16 values by year
    rows = {}
    for c in cells:
        k = (c["country"], c["tech"])
        rows.setdefault(k, {"unit": c["unit_introduced"], "mode": c["projection_mode"], "years": {}})
        rows[k]["years"][int(c["year"])] = c
    for k, v in rows.items():
        v["by"] = min(v["years"])

    def ref_of(unit):
        return unit.replace("Relative to", "").strip() if unit.startswith("Relative to") else None

    def base(cc, tech):
        cp = cps[(cc, tech)]
        price = float(cp["base_price_usd2024"])
        own = cp["method"] in ("own lines", "own customs statistics by vehicle type")
        sentences = []
        if "x ATB ratio" in cp["method"]:
            sentences.append(S_RULE3)
            if "other four countries" in cp["method"]:
                sentences.insert(0, S_OTHER)
        elif cp["method"] == "other four countries":
            sentences.append(S_OTHER)
        return price, own and not sentences, sentences, cp

    out = {cc: [] for cc in CCS}
    for c in cells:
        cc, tech, y = c["country"], c["tech"], int(c["year"])
        info = rows[(cc, tech)]
        unit, mode, by = info["unit"], info["mode"], info["by"]
        cur = float(c["current_value"]) if c["current_value"] not in ("", None) else 0.0
        rec = dict(c)
        rec["unit_introduced_proposed"] = unit
        ref0 = ref_of(unit)
        if ref0 and rows[(cc, ref0)]["unit"].startswith("Relative to"):
            rec["unit_introduced_proposed"] = "Relative to " + ref_of(rows[(cc, ref0)]["unit"])
        if tech == "TRNPASRAIELE":  # out of scope: rail entered in M US$ per GPkm, kept as before
            out[cc].append(rec)
            continue
        price, sourced, sents, cp = base(cc, tech)
        st, srcs = stat_text(cp, uv_all)
        ratio_atb = (f" Then times the ATB powertrain ratio {cp['atb_ratio']} (GEN-101)." if cp["atb_ratio"] else "")
        basis = (f"Base price {tech}: {cp['method']}, lines {cp['lines']}; {st}. Values converted to US$ at the "
                 f"WDI official rate of the same year (WDI-001; 1 for values published in US$) and to 2024 US$ with "
                 f"the CPI-U factor of the year (GEN-001); unit-weighted average {float(cp['value_usd2024']):.2f} "
                 f"US$2024 / {float(cp['units']):.0f} units.{ratio_atb} = {fmt(price)} US$ per vehicle (2024 US$).")
        src_ids = list(srcs) + (["GEN-101"] if cp["atb_ratio"] else [])
        assumption = list(sents)
        value = None
        src_value = fmt(price)
        src_unit = "US$ per vehicle (2024 US$), unit-weighted average of customs values 2019-2023"
        deriv = ""
        if cc == "CR":
            p16 = {yy: float(r["proposed_value"]) for yy, r in info["years"].items()}
            r_y = p16[y] / p16[2024]
            flat = all(abs(p16[yy] / p16[2024] - 1) < 1e-12 for yy in p16)
            value = round(price * r_y, 2)
            if flat:
                assumption.append(S_FLAT)
                path = "held flat in every year"
            else:
                if abs(r_y - 1) > 1e-12:
                    assumption.append(S_PATH)
                    src_ids.append("GEN-101")
                path = f"times the ATB 2022 Mid price ratio to 2024 of {r_y:.6f} for {y} (GEN-101)"
            deriv = (f"{basis} Costa Rica cell entered as a price per vehicle in every year: {fmt(price)} {path} = "
                     f"{fmt(value)} US$ per vehicle. The current cell is in another unit (it behaves like M US$ per "
                     f"Gvkm), so it is never counted as confirmed.")
        elif mode == TRAJ and y != by:
            m16 = float(c["proposed_value"])
            value = m16
            src_ids = ["GEN-101"]
            st_sources = []
            assumption = [S_PATH]
            src_value = c["proposed_value"]
            src_unit = "ratio to the 2024 price"
            deriv = (f"Multiplier for {y}: {m16:g}, the NREL ATB 2022 Mid price of this vehicle's class and powertrain "
                     f"relative to its 2024 price (GEN-101), unchanged; years before 2024 take 1. The base-year cell "
                     f"holds the 2024 price, so the compiled price is base-year price times this multiplier.")
        else:
            ref = ref_of(unit)
            if ref is None:
                value = round(price, 2)
                deriv = basis + (" Flat row: every year takes the base-year cell." if mode == "Flat" else
                                 " Base-year cell of a trajectory row: it holds the 2024 price and later cells hold "
                                 "multipliers on it.")
            else:
                ref_unit = rows[(cc, ref)]["unit"]
                final_ref = ref
                if ref_unit.startswith("Relative to"):
                    final_ref = ref_of(ref_unit)
                pr, sourced_r, sents_r, cp_r = base(cc, final_ref)
                st_r, srcs_r = stat_text(cp_r, uv_all)
                value = round(price / pr, 6)
                for s_ in sents_r:
                    if s_ not in assumption:
                        assumption.append(s_)
                src_ids = sorted(set(src_ids) | set(srcs_r) | ({"GEN-101"} if cp_r["atb_ratio"] else set()))
                src_unit = "ratio of two prices per vehicle (2024 US$)"
                src_value = fmt(value, 6)
                chain = ""
                if final_ref != ref:
                    chain = (f" The reference is changed from {ref} to {final_ref}: {ref} is itself a ratio, so the "
                             f"compiler would multiply two ratios.")
                deriv = (f"{basis} Reference {final_ref}: {cp_r['method']}, lines {cp_r['lines']}; {st_r}; "
                         f"= {fmt(pr)} US$ per vehicle (2024 US$). Ratio {fmt(price)} / {fmt(pr)} = {fmt(value, 6)}; "
                         f"the compiler multiplies it by the base-year cell of {final_ref}.{chain}")
        # change class
        if cc == "CR":
            within = False
        else:
            within = cur != 0 and abs(value - cur) <= band * abs(cur)
        cls = "confirmed" if within else ("assumption" if assumption else "replace")
        rec.update({
            "proposed_value": f"{value:.6f}".rstrip("0").rstrip(".") if isinstance(value, float) else value,
            "change_class": cls,
            "source_ids": ";".join(dict.fromkeys(src_ids)),
            "source_value": src_value, "source_unit": src_unit,
            "source_currency_year": "2019-2023 converted to 2024" if src_unit.startswith("US$") or "ratio of two" in src_unit else "",
            "cpi_factor": "per line-year in derivation" if src_unit.startswith("US$") or "ratio of two" in src_unit else "",
            "derivation": deriv + (f" Proposed {value:g} against current {cur:g}: "
                                   f"{'within' if within else 'differs by more than'} {band * 100:.0f} percent."),
            "assumption_sentence": " ".join(dict.fromkeys(assumption)),
        })
        out[cc].append(rec)
    cols = list(cells[0].keys()) + ["unit_introduced_proposed"]
    for cc in CCS:
        with open(os.path.join(JOB, cc, f"proposals_{cc}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(out[cc])
        n = len(out[cc])
        by_cls = {}
        for r in out[cc]:
            by_cls[r["change_class"]] = by_cls.get(r["change_class"], 0) + 1
        print(cc, n, by_cls)


if __name__ == "__main__":
    sys.exit(main())
