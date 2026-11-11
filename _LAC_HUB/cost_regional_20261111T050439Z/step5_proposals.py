"""Step 5 and 6: regional_proposals.csv (one row per year column of each accepted group) and
regional_vs_international.csv (one row per accepted group, with flags)."""
import glob, json, sys
import pandas as pd
sys.path.insert(0, ".")
from step1_scope import select

RV = pd.read_csv("regional_values.csv").set_index("value_id")
ACC = json.load(open("scratch/accepted.json"))
SHORT = {"REG-002": "IRENA RPGC 2024", "REG-003": "IRENA RPGC 2025", "REG-005": "ICE PEG 2024-2040",
         "REG-006": "ODS Honduras PIEG 2026-2035", "REG-014": "Colombian Technology Catalogue 2025"}
CUR_YEAR = {"REG-002": 2024, "REG-003": 2025, "REG-005": 2023, "REG-006": 2024, "REG-014": 2024}

# CPI-U (BLS CUUR0000SA0 annual average) from each country's own constants.csv
JOB = {"CostaRica": "cr", "DominicanRepublic": "dr", "Ecuador": "ecu", "Guatemala": "gua", "Honduras": "hon", "Jamaica": "jam"}
def cpi_table(country):
    f = glob.glob(f"../cost_src_{JOB[country]}_*/constants.csv")[0]
    c = pd.read_csv(f, dtype=str)
    key = c.columns[0]
    out = {}
    for _, r in c.iterrows():
        n = r[key]
        for pre in ("US_CPIU_", "CPIU_", "CPI_U_"):
            if n.startswith(pre) and n[len(pre):].isdigit():
                out[int(n[len(pre):])] = (float(r["value"]), r["source_id"], n)
    return out

def to_base(val, unit):
    """printed unit -> USD/kW, USD/kW-year or USD/MWh"""
    if unit == "MUSD/MWe":
        return val * 1000.0, "x 1000 (MUSD/MW to USD/kW)"
    if unit == "USD/MWe-year":
        return val / 1000.0, "/ 1000 (USD/MW-year to USD/kW-year)"
    if unit in ("USD/kW", "USD/kW-year", "USD/MWh"):
        return val, ""
    raise ValueError(unit)

d, s = select()
s["year"] = s["year"].astype(int)
props, comp = [], []
for key, a in ACC.items():
    country, tech, param = key.split("|")
    g = s[(s.country == country) & (s.Tech == tech) & (s.Parameter == param)].sort_values("year").copy()
    I = dict(zip(g.year, g.proposed_value.astype(float)))
    cpi = cpi_table(country)
    sid = a["source_id"]; cy = CUR_YEAR[sid]
    f_cpi = cpi[2024][0] / cpi[cy][0]
    cpi_note = "" if cy == 2024 else f" x CPI-U 2024/{cy} {cpi[2024][0]}/{cpi[cy][0]} ({cpi[2024][2]}, {cpi[cy][2]}; {cpi[2024][1]})"
    per_pj = a["extra"].get("per_pj", False)
    anchors, parts = [], []
    for vid in a["picks"]:
        r = RV.loc[vid]
        v = float(r["value"]); base, unote = to_base(v, r["unit"])
        val = base * f_cpi
        mnote = ""
        if param == "VariableCost":
            val = val / 3.6; mnote = " / 3.6 (USD/MWh to USD/GJ)"
        if per_pj:
            val = val / 31.536; mnote = " / 31.536 PJ per GW-year (STOELE capacity is in PJ/yr)"
        yr = int(r["value_year"]) if a["path"] == "multi" else 2024
        anchors.append((yr, val))
        parts.append(f"{r['value']} {r['unit']} ({r['value_year']}){(' ' + unote) if unote else ''}{cpi_note}{mnote} = {val:.6f} at {yr}")
    anchors.sort()
    ys = [y for y, _ in anchors]; vs = [v for _, v in anchors]
    head = (f"{a['tier']}: {SHORT[sid]} {RV.loc[a['picks'][0], 'page_or_table']}, {RV.loc[a['picks'][0], 'technology_as_printed']}, {RV.loc[a['picks'][0], 'geography']}; "
            + "; ".join(parts))
    src_ids = sid + ("" if cy == 2024 else ";" + cpi[2024][1])
    rows_g = []
    for _, r in g.iterrows():
        y = int(r["year"]); Iy = float(r["proposed_value"])
        if len(anchors) == 1:
            P = vs[0] * Iy / I[2024]
            rule = f"one printed value: P(y) = {vs[0]:.6f} x I(y)/I(2024) = {vs[0]:.6f} x {Iy}/{I[2024]}"
        elif ys[0] <= y <= ys[-1]:
            for k in range(len(ys) - 1):
                if ys[k] <= y <= ys[k + 1]:
                    w = (y - ys[k]) / (ys[k + 1] - ys[k])
                    P = vs[k] + w * (vs[k + 1] - vs[k])
                    rule = f"linear between printed years {ys[k]} ({vs[k]:.6f}) and {ys[k + 1]} ({vs[k + 1]:.6f})"
                    break
        elif y > ys[-1]:
            P = vs[-1] * Iy / I[ys[-1]]
            rule = f"after last printed year: P(y) = P({ys[-1]}) x I(y)/I({ys[-1]}) = {vs[-1]:.6f} x {Iy}/{I[ys[-1]]}"
        else:
            P = vs[0] * Iy / I[ys[0]]
            rule = f"before first printed year: P(y) = P({ys[0]}) x I(y)/I({ys[0]}) = {vs[0]:.6f} x {Iy}/{I[ys[0]]}"
        out = r.to_dict()
        out["year"] = str(y)
        out["proposed_value"] = round(P, 6)
        out["change_class"] = "regional"
        out["basis_class"] = "national" if a["tier"] == "N" else "regional"
        out["source_ids"] = src_ids
        out["derivation"] = f"{head}; {rule} = {P:.6f}; I = current proposed path in proposals_all.csv"
        out["assumption_sentence"] = ""
        out["tier"] = a["tier"]
        out["international_value"] = Iy
        out["change_pct"] = round((P - Iy) / Iy * 100.0, 2)
        rows_g.append(out)
    props += rows_g
    r24 = [x for x in rows_g if x["year"] == "2024"][0]
    to_kw = 31.536 if per_pj else 1.0
    vals_kw = [x["proposed_value"] * to_kw for x in rows_g]
    if param == "CapitalCost":
        screen = [v for v in vals_kw if v < 300 or v > 8000]; scr = "CapitalCost 300 to 8,000 USD/kW"
    elif param == "FixedCost":
        screen = [v for v in vals_kw if v < 0 or v > 200]; scr = "FixedCost 0 to 200 USD/kW-year"
    else:
        screen = [v for v in vals_kw if v > 8.33]; scr = "VariableCost up to 8.33 USD/GJ"
    maxchg = max(abs(x["change_pct"]) for x in rows_g)
    flags = []
    if abs(r24["change_pct"]) > 25:
        flags.append("2024 change above 25 percent")
    if maxchg > 25:
        flags.append(f"change above 25 percent in {sum(abs(x['change_pct']) > 25 for x in rows_g)} of {len(rows_g)} years (max {maxchg:.1f})")
    if screen:
        flags.append(f"{len(screen)} years outside {scr}")
    comp.append({"country": country, "technology": tech, "parameter": param, "unit": r24["unit"],
                 "international_2024": r24["international_value"], "international_source_ids": g[g.year == 2024].iloc[0]["source_ids"],
                 "regional_2024": r24["proposed_value"], "regional_source_ids": src_ids, "regional_source": SHORT[sid], "tier": a["tier"],
                 "change_pct_2024": r24["change_pct"], "max_abs_change_pct_all_years": round(maxchg, 2), "rows": len(rows_g),
                 "flags": "; ".join(flags)})

cols = list(d.columns) + ["tier", "international_value", "change_pct"]
P = pd.DataFrame(props)[cols]
P.to_csv("regional_proposals.csv", index=False, lineterminator="\n")
C = pd.DataFrame(comp).sort_values(["country", "technology", "parameter"])
C.to_csv("regional_vs_international.csv", index=False, lineterminator="\n")
print(len(P), "proposal rows;", len(C), "groups")
print(C[["country", "technology", "parameter", "international_2024", "regional_2024", "tier", "change_pct_2024", "flags"]].to_string())
