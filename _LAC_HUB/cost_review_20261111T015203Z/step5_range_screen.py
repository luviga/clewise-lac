"""Step 5: range screen of every proposed value (review_flags.csv).

Severity used in this pack (recorded in GAPS):
  high   = value outside a physical screen (CapitalCost, FixedCost, plant VariableCost, fuel against Brent),
           or exactly 0 or 1 on an in-scope row where no brief rule asks for that value;
  medium = change above 25 percent from a real current value (current not 0, 1, 2 or empty), step at the join above 20 percent;
  low    = change above 25 percent from a placeholder (current 0, 1, 2 or empty), or a 0 that a brief rule prescribes.
"""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa

BRENT24_USD_GJ = 80.52 * 7.32 / 42.3  # EIA Brent 2024 80.52 USD/bbl, UN 7.32 bbl/t, IPCC 42.3 GJ/t


def brief_section5(cc):
    t = text(cc, "BRIEF_LAC_COST_SRC_*.md")
    s5 = t.split("## 5.")[1].split("## 6.")[0]
    plants = re.findall(r"^\| `([^`]+)`", s5.split("Power plants in scope")[1].split("Fuel supply rows")[0], re.M)
    fuels = re.findall(r"^\| `([^`]+)`", s5.split("Fuel supply rows")[1].split("Country notes")[0], re.M)
    return plants, fuels


IMPORT = {"ecu": "IMPELE", "gua": "IMP_ELE", "hon": "IMP_ELE"}
R_PER_BBL = {"ecu", "gua"}
SOURCED_ZERO = re.compile(r"(?i)((?<![\d.])0(\.0+)? USD/MWh|gives 0\.0000|variable O&M 0(\.0+)? USD|no variable O&M|has no variable O&M|zero variable O&M|O&M is)")
# zeros a brief rule prescribes
def prescribed_zero(cc, r):
    if cc == "ecu" and r["Parameter"] == "VariableCost" and r["Tech"].startswith("PP") and "CCG" in r["derivation"]:
        return "Ecuador brief: VariableCost 0 for plants taken from CCG (fixed costs include variable O&M)"
    if cc == "ecu" and r["Tech"].startswith("DIST_") and r["Parameter"] in ("CapitalCost", "FixedCost"):
        return "Ecuador brief: CapitalCost and FixedCost 0 for DIST_* rows with an ASSUMPTION sentence"
    if cc == "hon" and r["Tech"] == "IMP_ELE" and r["Parameter"] == "FixedCost":
        return "Honduras brief: propose FixedCost 0 if both parameters carry the import price"
    return ""


def yr_range(ys):
    ys = sorted(int(y) for y in ys)
    return f"{ys[0]}" if len(ys) == 1 else f"{ys[0]}-{ys[-1]} ({len(ys)} years)"


flags = []


def flag(cc, sev, screen, g, detail):
    r = g.iloc[0]
    cur = g["current_value"]
    flags.append({"country": COUNTRY[cc], "cc": cc, "severity": sev, "screen": screen, "technology": r["Tech"],
                  "parameter": r["Parameter"], "fuel_scenario": ";".join(sorted(set(g["fuel_scenario"]))),
                  "years": yr_range(g["year"]),
                  "proposed_min": min(num(x) for x in g["proposed_value"]), "proposed_max": max(num(x) for x in g["proposed_value"]),
                  "current_values": ";".join(sorted(set(cur), key=lambda x: (num(x) is None, num(x) or 0)))[:80],
                  "change_class": ";".join(sorted(set(g["change_class"]))), "basis_class": ";".join(sorted(set(g["basis_class"]))),
                  "source_ids": ";".join(sorted({i for s in g["source_ids"] for i in s.split(";") if i}))[:120],
                  "detail": detail})


for cc in CCS:
    P = read(cc, "proposals.csv")
    P["pv"] = P["proposed_value"].map(num)
    P["cv"] = P["current_value"].map(num)
    plants, fuels = brief_section5(cc)
    scope = set(plants) | set(fuels) | ({IMPORT[cc]} if cc in IMPORT else set())
    pl = P[P["Tech"].isin(plants)]
    # physical screens
    for prm, lo, hi, unit in [("CapitalCost", 300, 8000, "USD/kW"), ("FixedCost", 0, 200, "USD/kW-yr"),
                              ("VariableCost", None, 30 / 3.6, "USD/GJ")]:
        q = pl[pl["Parameter"] == prm]
        bad = q[((q["pv"] < lo) if lo is not None else False) | (q["pv"] > hi)]
        if prm == "FixedCost":
            bad = q[(q["pv"] < 0) | (q["pv"] > hi)]
        for t, g in bad.groupby("Tech"):
            pz = all(prescribed_zero(cc, r) for _, r in g.iterrows()) and (g["pv"] == 0).all()
            flag(cc, "low" if pz else "high", f"plant {prm} outside {lo if lo is not None else '-'} to {hi:.2f} {unit}", g,
                 (prescribed_zero(cc, g.iloc[0]) + "; " if pz else "") + f"derivation: {g.iloc[0]['derivation'][:200]}")
    # fuel 2024 against Brent-implied value (oil products)
    F = read(cc, "fuel_prices.csv")
    vcol = [c for c in F.columns if c.startswith("value_usd_per_gj")][0]
    f24 = F[(F["year"] == "2024") & (F["scenario"] == "STEPS")]
    for _, r in f24.iterrows():
        if "brent" not in r["benchmark"].lower():
            continue
        rv = num(r["r"])
        v = num(r[vcol])
        if rv is None or v is None:
            continue
        # Ecuador and Guatemala state r against Brent in USD/bbl; the other four against Brent in USD/GJ
        if cc in R_PER_BBL:
            implied, unit = rv * 80.52, "USD/bbl 80.52"
        else:
            implied, unit = rv * BRENT24_USD_GJ, f"USD/GJ {BRENT24_USD_GJ:.3f}"
        ratio = v / implied
        if ratio < 0.5 or ratio > 2:
            g = P[(P["Tech"] == r["row"]) & (P["year"] == "2024") & (P["fuel_scenario"] == "STEPS") & (P["Parameter"] == "VariableCost")]
            if len(g):
                flag(cc, "high", "fuel 2024 outside 0.5 to 2 times Brent-implied value", g,
                     f"2024 {v:.3f} USD/GJ; r {rv:.4f} x Brent 2024 {unit} = {implied:.3f}; ratio {ratio:.2f}")
    # exactly 0 or 1 on in-scope rows
    z = P[P["Tech"].isin(scope) & P["pv"].isin([0.0, 1.0])]
    for (t, prm), g in z.groupby(["Tech", "Parameter"]):
        pres = prescribed_zero(cc, g.iloc[0])
        der = g.iloc[0]["derivation"]
        allzero = (g["pv"] == 0).all()
        if allzero and pres:
            sev, why = "low", pres + "; "
        elif allzero and SOURCED_ZERO.search(der):
            sev, why = "low", "a cited source states 0 for this cost; "
        elif allzero and ("ASSUMPTION" in der or g["basis_class"].eq("ASSUMPTION").all()):
            sev, why = "low", "0 set by an ASSUMPTION sentence; "
        elif allzero and "placeholder" in der:
            sev, why = "medium", "0 read from a source placeholder (0.0001 or 0); "
        else:
            sev, why = "high", ""
        flag(cc, sev, "value exactly 0 or 1 on an in-scope row", g,
             why + f"values {sorted(set(g['proposed_value']))[:4]}; derivation: {g.iloc[0]['derivation'][:160]}")
    # change above 25 percent
    c = P[P["cv"].notna() & (P["cv"] != 0) & P["pv"].notna()].copy()
    c["chg"] = (c["pv"] - c["cv"]) / c["cv"].abs()
    big = c[c["chg"].abs() > 0.25]
    for (t, prm), g in big.groupby(["Tech", "Parameter"]):
        ph = g["cv"].isin([1.0, 2.0]).all()
        flag(cc, "low" if ph else "medium", "proposed change above 25 percent from current", g,
             ("current is a placeholder (1 or 2); " if ph else "") +
             f"change {g['chg'].min() * 100:+.0f} to {g['chg'].max() * 100:+.0f} percent over {len(g)} cells; 2024: " +
             "; ".join(f"{r['fuel_scenario']} {r['current_value']} -> {r['proposed_value']}"
                       for _, r in g[g["year"] == "2024"].head(3).iterrows()))
    zc = P[(P["cv"].isna() | (P["cv"] == 0)) & P["pv"].notna() & (P["pv"] != 0)]
    for (t, prm), g in zc.groupby(["Tech", "Parameter"]):
        flag(cc, "low", "proposed change from a current value of 0 or empty (percent undefined)", g,
             f"{len(g)} cells; derivation: {g.iloc[0]['derivation'][:120]}")
    # step at the join
    for (row, sc), g in F.groupby(["row", "scenario"]):
        g = g.assign(y=g["year"].astype(int)).sort_values("y")
        obs = g[g["case"].str.startswith("observed")]
        proj = g[g["case"].str.startswith("projected")]
        if not len(obs) or not len(proj):
            continue
        lo_, fp = obs.iloc[-1], proj[proj["y"] > obs["y"].max()]
        if not len(fp):
            continue
        fp = fp.iloc[0]
        a, b = num(lo_[vcol]), num(fp[vcol])
        if a and b is not None:
            st = b / a - 1
            if abs(st) > 0.20:
                gg = P[(P["Tech"] == row) & (P["fuel_scenario"] == sc) & (P["year"].isin([lo_["year"], fp["year"]]))
                       & (P["Parameter"] == "VariableCost")]
                if len(gg):
                    flag(cc, "medium", "step at the join above 20 percent", gg,
                         f"{lo_['year']} observed {a:.4f} -> {fp['year']} projected {b:.4f} USD/GJ, step {st * 100:+.1f} percent")

R = pd.DataFrame(flags)
order = {"high": 0, "medium": 1, "low": 2}
R = R.sort_values(["cc", "severity", "screen", "technology"], key=lambda s: s.map(order) if s.name == "severity" else s)
write(R, "review_flags.csv")
print(R.groupby(["cc", "severity"]).size().unstack(fill_value=0))
print(R[R.severity != "low"].groupby(["cc", "screen"]).size().to_string())
