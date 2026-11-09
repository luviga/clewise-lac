"""Step 4: 2024 adders by country and fuel.
adder = (observed pre-tax import cost - 2024 benchmark) + terminal/wholesale margin, in USD/GJ.
Inputs: downloads/<CC>/<CC>_regulator_2024.csv (values extracted from regulator documents, spot-checked),
history_usd_per_gj.csv (benchmarks). Writes adders_2024.csv and adders_working.txt.
Run: py -I adders.py <output_folder>
"""
import sys, os
import numpy as np
import pandas as pd

OUT = sys.argv[1]
DL = os.path.join(OUT, "downloads")
L_PER_GAL = 3.785411784
KG_25LB = 25 * 0.45359237
MMBTU_GJ = 1.055056
# gal per GJ (UNSD gal/t over IPCC NCV) as in history.py
GPG = {"GSL": 357 / 44.3, "DSL": 304 / 43.0, "JET": 326 / 44.1, "KER": 326 / 43.8, "LPG": 489 / 47.3,
       "FOI": 278 / 40.4, "AVG": 362 / 44.3, "CRU": 7.32 * 42 / 42.3}
NCV = {"GSL": 44.3, "DSL": 43.0, "JET": 44.1, "KER": 43.8, "LPG": 47.3, "FOI": 40.4, "AVG": 44.3, "CRU": 42.3, "NGS": 48.0}
# exchange rates, 2024 averages, selling rate where both are published
FX = {"CR": (518.23, "CRC/USD, mean of 366 daily BCCR reference selling rates 2024 (https://sdd.bccr.fi.cr/es/IndicadoresEconomicos/Inicio/Contenedor/6?Cuadro=1)"),
      "DR": (59.5665, "DOP/USD, BCRD 2024 annual average selling rate, sheet PromAnual (https://cdn.bancentral.gov.do/documents/estadisticas/mercado-cambiario/documents/TASA_DOLAR_REFERENCIA_MC.xlsx)"),
      "GUA": (7.75960, "GTQ/USD, mean of 366 daily Banguat reference rates 2024 (https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx, TipoCambioRango)"),
      "JAM": (157.22, "JMD/USD, Bank of Jamaica 2024 annual weighted average selling rate (https://boj.org.jm/market/foreign-exchange/average-exchange-rates/)")}

h = pd.read_csv(os.path.join(OUT, "history_usd_per_gj.csv"))
B = h[h.year == 2024].set_index("benchmark").usd_per_gj
BM = {"GSL": B["GSL_USGC"], "DSL": B["DSL_USGC"], "JET": B["JET_USGC"], "KER": B["JET_USGC"] * 44.1 / 43.8,
      "LPG": B["LPG_MB"], "CRU": B["CRU_Brent"], "NGS": B["NGS_HH"], "COA": B["COA_SAfrica_WB"], "COK": B["COK_US_power"],
      "FOI": B["FOI_proxy"], "AVG": B["AVG_proxy"]}
BMNAME = {"GSL": "EIA USGC conventional regular gasoline", "DSL": "EIA USGC ULSD", "JET": "EIA USGC jet",
          "KER": "EIA USGC jet on kerosene NCV", "LPG": "EIA Mont Belvieu propane", "CRU": "EIA Brent",
          "NGS": "EIA Henry Hub (gross basis)", "COA": "World Bank South African coal (NAR)",
          "COK": "EIA US petcoke delivered to power plants (proxy)", "FOI": "Brent x 0.814 (proxy; ratio from ARESEP 2024 FOB bunker)",
          "AVG": "USGC gasoline x 1.579 (proxy; EIA PADD 3 avgas ratio 2018-2021)"}

def load(cc):
    d = pd.read_csv(os.path.join(DL, cc, f"{cc}_regulator_2024.csv"))
    d["date_or_period"] = d["date_or_period"].astype(str)
    return d[d.date_or_period.str.contains("2024") & ~d.date_or_period.str.startswith("2025")]

def mean(d, fuel_pat, comp, unit, note_pat=None, period="monthly"):
    x = d[d.fuel.astype(str).str.contains(fuel_pat, regex=True) & (d.component == comp) & (d.unit == unit)]
    if note_pat:
        x = x[x.notes.astype(str).str.contains(note_pat, regex=True)]
    if period == "monthly":
        x = x[x.date_or_period.str.len() > 4]
    elif period == "annual":
        x = x[x.date_or_period == "2024"]
    if len(x) == 0:
        raise ValueError(f"no rows {fuel_pat} {comp} {unit} {note_pat}")
    return float(x.value.mean()), len(x), "; ".join(sorted(set(x.source_url.astype(str))))[:600]

rows, work = [], []
def add(country, fuel, code, method, imp, margin, comps, src, note=""):
    bm = BM[fuel]
    imp_add = None if imp is None else imp - bm
    tot = None if imp_add is None else imp_add + (margin or 0.0)
    rows.append(dict(country=country, fuel=fuel, model_code=code, method=method, benchmark=BMNAME[fuel],
                     benchmark_2024_usd_per_gj=round(bm, 3),
                     observed_import_cost_usd_per_gj=None if imp is None else round(imp, 3),
                     import_adder_usd_per_gj=None if imp_add is None else round(imp_add, 3),
                     margin_usd_per_gj=None if margin is None else round(margin, 3),
                     adder_usd_per_gj=None if tot is None else round(tot, 3),
                     pre_tax_price_2024_usd_per_gj=None if tot is None else round(bm + tot, 3),
                     components=comps, sources=src, notes=note))
    work.append(f"{country} {fuel}: {comps} | benchmark {bm:.3f} | import cost {imp if imp is None else round(imp,3)} | "
                f"import adder {imp_add if imp_add is None else round(imp_add,3)} | margin {margin if margin is None else round(margin,3)} | adder {tot if tot is None else round(tot,3)}")

crc_l = lambda v: v / FX["CR"][0] * L_PER_GAL          # CRC/L -> USD/gal
dop_g = lambda v: v / FX["DR"][0]                      # DOP/gal -> USD/gal
gtq_g = lambda v: v / FX["GUA"][0]                     # GTQ/gal -> USD/gal

# ---------------- Costa Rica: ARESEP monthly resolutions (RECOPE purchase cost COA + RECOPE margin K) ----------------
cr = load("CR")
for fuel, code, pat in [("DSL", "IMPPURDSL", "^Diesel"), ("GSL", "IMPPURGSL", "RON 91"), ("JET", "IMPKJF", "^Jet fuel"),
                        ("KER", "IMPKJF", "^Kerosene"), ("LPG", "IMPLPG", "70-30"), ("FOI", "IMPFOI", "Bunker"), ("AVG", "IMPAVG", "Av-Gas")]:
    coa, n, src = mean(cr, pat, "import_cost_cif", "CRC/L")
    k, _, _ = mean(cr, pat, "margin_terminal_wholesale", "CRC/L")
    imp = crc_l(coa) * GPG[fuel]; mg = crc_l(k) * GPG[fuel]
    extra = ""
    if fuel in ("FOI", "LPG"):
        fob, _, _ = mean(cr, pat, "fob_reference", "CRC/L")
        extra = f"; of which ARESEP 'Precio FOB estimado' {crc_l(fob)*GPG[fuel]:.3f} USD/GJ and freight+insurance+port {crc_l(coa-fob)*GPG[fuel]:.3f} USD/GJ"
    add("CostaRica", fuel, code, "observed (regulator price structure)", imp, mg,
        f"COA {coa:.2f} CRC/L ({n} months) and RECOPE margin K {k:.2f} CRC/L at {FX['CR'][0]} CRC/USD{extra}", src,
        "COA = RECOPE purchase cost from invoices (FOB, freight, insurance, trader premium, port); ARESEP method RE-0024-JD-2022; Bunker and LPG pre-tax prices are subsidised below COA+K")
for fuel, code in [("NGS", "IMPNGS"), ("COA", "IMPCOA"), ("COK", "IMPCOK")]:
    add("CostaRica", fuel, code, "ASSUMPTION candidate", None, None, "no regulated price; RECOPE does not handle this fuel", "", "")

# ---------------- Dominican Republic: MICM weekly price structures ----------------
dr = load("DR")
for fuel, code, pat, note in [
        ("DSL", "DIST_DSL", "^diesel_gasoil_regular_power_generators", "gasoil regular for power generators (EGP-C), the market-tracking diesel row"),
        ("GSL", "DIST_GSL", "^gasoline_regular", "retail price frozen in 2024; import parity near constant, administrative"),
        ("LPG", "DIST_LPG", "^lpg_glp", "retail price frozen in 2024; import parity fixed (87.08 then 84.06 DOP/gal), administrative"),
        ("KER", "DIST_KER", "^kerosene", ""), ("JET", "DIST_KER", "^jet_fuel_avtur", "avtur; DR model has no DIST_JET row (shown for reference)"),
        ("FOI", "DIST_FOI", "^fuel_oil_no6$", "fuel oil No. 6 (general)")]:
    ip, n, src = mean(dr, pat, "import_parity", "DOP/gal", period="any")
    mg, _, _ = mean(dr, pat, "margin_terminal_wholesale", "DOP/gal", period="any")
    add("DominicanRepublic", fuel, code, "observed (regulator price structure)", dop_g(ip) * GPG[fuel], dop_g(mg) * GPG[fuel],
        f"MICM paridad de importacion {ip:.2f} DOP/gal and distributor margin {mg:.2f} DOP/gal ({n} weeks) at {FX['DR'][0]} DOP/USD", src, note)
ng, n, src = mean(dr, "^natural_gas$", "price_pre_tax", "DOP/MMBtu", period="any")
add("DominicanRepublic", "NGS", "DIST_NGS", "observed (regulator published importer price)", ng / FX["DR"][0] / MMBTU_GJ, 0.0,
    f"MICM importer selling price to wholesaler {ng:.2f} DOP/MMBtu ({n} weeks) at {FX['DR'][0]} DOP/USD; margin included in the price", src,
    "gross calorific basis like Henry Hub; covers liquefaction, shipping, regasification and importer margin")
add("DominicanRepublic", "COA", "DIST_COA", "ASSUMPTION candidate", None, None, "no published delivered coal price opened (OC-SENI not opened)", "",
    "MEM bulletins quote coal FOB Bolivar 3.58 USD/MMBtu (4 months, Platts) as a benchmark check only")
add("DominicanRepublic", "COK", "DIST_COK", "ASSUMPTION candidate", None, None, "no published price", "", "")
add("DominicanRepublic", "CRU", "DIST_CRU", "ASSUMPTION candidate", None, None, "no published crude import cost opened", "", "")

# ---------------- Guatemala: MEM weekly price structures ----------------
gu = load("GUA")
for fuel, code, pat in [("DSL", "DIST_DSL", "^diesel$"), ("GSL", "DIST_GSL", "^gasoline_regular$")]:
    cif, n, src = mean(gu, pat, "import_parity", "GTQ/gal", period="any")
    fob, nf, _ = mean(gu, pat, "fob_reference", "GTQ/gal", period="any")
    im, _, _ = mean(gu, pat, "margin_terminal_wholesale", "GTQ/gal", "Margen del importador", period="any")
    ot, _, _ = mean(gu, pat, "margin_terminal_wholesale", "GTQ/gal", "Otros gastos", period="any")
    add("Guatemala", fuel, code, "observed (regulator price structure)", gtq_g(cif) * GPG[fuel], gtq_g(im + ot) * GPG[fuel],
        f"MEM Precio CIF {cif:.2f} GTQ/gal ({n} weeks) plus importer margin {im:.2f} and other costs {ot:.2f} GTQ/gal at {FX['GUA'][0]} GTQ/USD; "
        f"MEM FOB US Gulf {fob:.2f} GTQ/gal ({nf} days) so CIF-FOB = {gtq_g(cif-fob)*GPG[fuel]:.3f} USD/GJ", src,
        "inland freight (0.40 GTQ/gal) and retail margin excluded")
cif, n, src = mean(gu, "^fuel_oil_bunker$", "import_parity", "GTQ/gal", period="any")
im, _, _ = mean(gu, "^fuel_oil_bunker$", "margin_terminal_wholesale", "GTQ/gal", "Margen del importador", period="any")
te, _, _ = mean(gu, "^fuel_oil_bunker$", "margin_terminal_wholesale", "GTQ/gal", "Gastos de terminal", period="any")
po, _, _ = mean(gu, "^fuel_oil_bunker$", "margin_terminal_wholesale", "GTQ/gal", "Cargos portuarios", period="any")
uv, nu, _ = mean(gu, "^fuel_oil_bunker$", "import_parity", "USD/bbl", period="any")
add("Guatemala", "FOI", "DIST_FOI", "observed (regulator price structure)", gtq_g(cif) * GPG["FOI"], gtq_g(im + te + po) * GPG["FOI"],
    f"MEM ex-rack Puerto San Jose structure: Precio CIF {cif:.2f} GTQ/gal ({n} weeks), importer margin {im:.2f}, terminal {te:.2f}, port {po:.4f} GTQ/gal at {FX['GUA'][0]} GTQ/USD; "
    f"MEM monthly unit import value {uv:.2f} USD/bbl ({nu} months) = {uv/42*GPG['FOI']:.3f} USD/GJ", src,
    "MEM CIF for bunker is below the MEM daily FOB table (different grades); importer margin in this structure is large")
cyl, n, src = mean(gu, "lpg", "import_parity", "GTQ/cylinder_25lb", period="any")
im, _, _ = mean(gu, "lpg", "margin_terminal_wholesale", "GTQ/cylinder_25lb", "Margen del importador", period="any")
per_gj = lambda v: v / FX["GUA"][0] / KG_25LB * 1000 / NCV["LPG"]
add("Guatemala", "LPG", "DIST_LPG", "observed (regulator price structure)", per_gj(cyl), per_gj(im),
    f"MEM 25 lb cylinder structure: Precio CIF {cyl:.2f} GTQ/cylinder ({n} weeks) plus importer margin {im:.2f} GTQ/cylinder; 25 lb = {KG_25LB:.3f} kg; NCV 47.3 GJ/t", src,
    "bottler and retail margins excluded")
for fuel, code, why in [("KER", "DIST_KER", "kerosene imported in one month only (71 bbl)"), ("NGS", "DIST_NGS", "no natural gas imports or published price"),
                        ("COA", "DIST_COA", "no published coal price"), ("COK", "DIST_COK", "MEM petcoke unit value is reported per barrel; unit doubtful, not used")]:
    add("Guatemala", fuel, code, "ASSUMPTION candidate" if fuel in ("NGS", "COA", "COK") else "built (regional published data)", None, None, why, "", "")

# ---------------- Honduras: SEN import CIF (annual report), CREE bunker price, SEN LPG structure ----------------
ho = load("HON")
for fuel, code, pat in [("DSL", "DIST_DSL", "^diesel$"), ("GSL", "DIST_GSL", "^gasoline_regular$"), ("KER", "DIST_KER", "^kerosene$")]:
    v, n, src = mean(ho, pat, "import_parity", "USD/bbl", period="annual")
    add("Honduras", fuel, code, "observed import cost; margin ASSUMPTION candidate", v / 42 * GPG[fuel], None,
        f"SEN annual report 2024 CIF unit value {v:.2f} USD/bbl (CIF value / volume)", src,
        "SEN monthly reports give a lower volume-weighted CIF; the annual report is used; no published margin")
v, n, src = mean(ho, "^fuel_oil$", "generator_fuel_price", "USD/bbl", "Real", period="monthly")
add("Honduras", "FOI", "DIST_FOI", "observed (regulator published delivered price)", v / 42 * GPG["FOI"], 0.0,
    f"CREE actual monthly bunker price for generation {v:.2f} USD/bbl ({n} months); delivered price, margins included", src,
    "SEN annual CIF unit value for fuel oil 76.46 USD/bbl is a cross-check")
fobc, n, src = mean(ho, "^lpg$", "fob_reference", "USD/cylinder_25lb", period="any")
ipc, _, _ = mean(ho, "^lpg$", "import_parity", "USD/cylinder_25lb", period="any")
mgc, _, _ = mean(ho, "^lpg$", "margin_terminal_wholesale", "USD/cylinder_25lb", period="any")
hgj = lambda v: v / KG_25LB * 1000 / NCV["LPG"]
add("Honduras", "LPG", "DIST_LPG", "observed (regulator price structure)", hgj(ipc), hgj(mgc),
    f"SEN/CCHAC bulletin 25 lb cylinder: FOB {fobc:.3f}, import parity {ipc:.3f}, importer margin {mgc:.3f} USD/cylinder ({n} weeks, Jan-Jul); 25 lb = {KG_25LB:.3f} kg", src,
    f"published FOB = {hgj(fobc):.3f} USD/GJ vs Mont Belvieu {BM['LPG']:.3f}")
for fuel, code in [("NGS", "DIST_NGS"), ("COA", "DIST_COA"), ("COK", "DIST_COK")]:
    add("Honduras", fuel, code, "ASSUMPTION candidate", None, None, "no published 2024 price", "", "")

# ---------------- Jamaica: UN Comtrade CIF unit values, OUR generator fuel prices ----------------
ja = load("JAM")
v, n, src = mean(ja, r"LPG propane \(HS", "import_unit_value_cif", "USD/tonne", period="annual")
add("Jamaica", "LPG", "DIST_LPG", "observed import cost (customs CIF); margin ASSUMPTION candidate", v / NCV["LPG"], None,
    f"UN Comtrade Jamaica imports 2024 HS 271112 propane CIF {v:.2f} USD/t; NCV 47.3 GJ/t", src, "")
v, n, src = mean(ja, "Natural gas", "generator_fuel_price", "USD/MMBtu", period="any")
add("Jamaica", "NGS", "DIST_NGS", "observed (regulator published delivered price)", v / MMBTU_GJ, 0.0,
    f"OUR investigation report Dec 2024: natural gas price to JPS and IPP plants {v:.2f} USD/MMBtu ({n} plant-months, June-July 2024)", src,
    "gross basis; range 8.59-14.23 USD/MMBtu by plant")
v, n, src = mean(ja, "Heavy fuel oil", "generator_fuel_price", "USD/MMBtu", period="any")
add("Jamaica", "FOI", "DIST_FOI", "observed (regulator published delivered price)", v / MMBTU_GJ, 0.0,
    f"OUR investigation report Dec 2024: HFO price to JPS and IPP plants {v:.2f} USD/MMBtu ({n} plant-months, June-July 2024)", src,
    "published in USD/MMBtu on an unstated (probably gross) basis, while the fuel oil benchmark is on net basis; gross basis would understate the adder by about 5-8 percent of the price")
v, n, src = mean(ja, r"Gasoline and light oils \(HS", "import_unit_value_cif", "USD/tonne", period="annual")
for fuel, code in [("DSL", "DIST_DSL"), ("GSL", "DIST_GSL"), ("KER", "DIST_KER"), ("JET", "DIST_JET")]:
    add("Jamaica", fuel, code, "built (regional published data)", None, None,
        "no published pre-tax price; Petrojam site not retrievable" + (f"; Comtrade HS 271012 CIF {v:.2f} USD/t = {v/44.3:.3f} USD/GJ is below the USGC benchmark, so not used" if fuel == "GSL" else ""), src if fuel == "GSL" else "", "")
for fuel, code in [("COA", "DIST_COA"), ("COK", "DIST_COK")]:
    add("Jamaica", fuel, code, "ASSUMPTION candidate", None, None, "no published price (Comtrade coal value has no weight)", "", "")

# ---------------- Ecuador: EP Petroecuador 2024 import unit values (DPU, freight included, insurance excluded) ----------------
ec = load("ECU")
def ecu(pat, unit="USD/bbl"):
    x = ec[ec.fuel.astype(str).str.contains(pat, regex=True) & (ec.component == "import_unit_value") & (ec.unit == unit) & (ec.date_or_period.str.startswith("2024 ("))]
    return float(x.value.iloc[0]), "; ".join(sorted(set(x.source_url.astype(str))))
for fuel, code, pat, lab in [("DSL", "DIST_DSL", r"diesel \(all grades\)", "all diesel (value-weighted Diesel 2 and Premium)"),
                             ("GSL", "DIST_GSL", "all naphtha grades", "all naphtha (value-weighted RON 95 and RON 80)"),
                             ("JET", "DIST_JET", "Jet A-1", "Jet A-1 (7 months with imports)")]:
    try:
        v, src = ecu(pat)
    except Exception:
        v, src = None, ""
    add("Ecuador", fuel, code, "observed import cost; margin ASSUMPTION candidate", None if v is None else v / 42 * GPG[fuel], None,
        f"EP Petroecuador Informe Estadistico 2024 import unit value {lab} {v} USD/bbl (DPU basis: freight included, insurance excluded)", src, "")
try:
    v, src = ecu("LPG", "USD/t")
except Exception:
    v, src = None, ""
add("Ecuador", "LPG", "DIST_LPG", "observed import cost; margin ASSUMPTION candidate", None if v is None else v / NCV["LPG"], None,
    f"EP Petroecuador 2024 LPG import unit value {v} USD/t (DPU basis)", src, "")
add("Ecuador", "FOI", "DIST_FOI", "ASSUMPTION candidate", None, None, "no fuel oil imports in 2024; Ecuador exports fuel oil No. 6 (export FOB 61.68 USD/bbl)", "", "")
for fuel, code in [("KER", "DIST_KER"), ("CRU", "DIST_CRU"), ("NGS", "DIST_NGS"), ("COA", "DIST_COA"), ("COK", "DIST_COK")]:
    add("Ecuador", fuel, code, "ASSUMPTION candidate" if fuel != "KER" else "built (regional published data)", None, None, "no 2024 import cost published", "", "")

a = pd.DataFrame(rows)

# ---------------- built adders and margin assumptions from the observed set ----------------
obs = a[a.method.str.startswith("observed (regulator price structure)")]
stats = {}
for fuel in ["DSL", "GSL", "KER", "JET", "LPG", "FOI"]:
    o = obs[obs.fuel == fuel]
    stats[fuel] = dict(n=len(o), adder_med=o.adder_usd_per_gj.median(), adder_min=o.adder_usd_per_gj.min(), adder_max=o.adder_usd_per_gj.max(),
                       imp_med=o.import_adder_usd_per_gj.median(), mg_med=o.margin_usd_per_gj.median(),
                       mg_min=o.margin_usd_per_gj.min(), mg_max=o.margin_usd_per_gj.max(), who=", ".join(o.country))
stats["KER"] = stats["KER"] if stats["KER"]["n"] >= 2 else stats["KER"]
for i, r in a.iterrows():
    f = r.fuel
    if r.method.startswith("built") and f in stats:
        s = stats[f] if stats[f]["n"] >= 2 else stats["JET"]
        a.at[i, "import_adder_usd_per_gj"] = round(s["imp_med"], 3)
        a.at[i, "margin_usd_per_gj"] = round(s["mg_med"], 3)
        a.at[i, "adder_usd_per_gj"] = round(s["imp_med"] + s["mg_med"], 3)
        a.at[i, "pre_tax_price_2024_usd_per_gj"] = round(r.benchmark_2024_usd_per_gj + s["imp_med"] + s["mg_med"], 3)
        a.at[i, "components"] = (r.components + f"; built as median of observed regulator import adders ({s['imp_med']:.3f}) and margins ({s['mg_med']:.3f}) "
                                 f"for this fuel in {s['who']}; observed total adder range {s['adder_min']:.3f} to {s['adder_max']:.3f}")
    elif "margin ASSUMPTION" in r.method and f in stats:
        a.at[i, "margin_usd_per_gj"] = round(stats[f]["mg_med"], 3)
        a.at[i, "adder_usd_per_gj"] = round(r.import_adder_usd_per_gj + stats[f]["mg_med"], 3)
        a.at[i, "pre_tax_price_2024_usd_per_gj"] = round(r.benchmark_2024_usd_per_gj + r.import_adder_usd_per_gj + stats[f]["mg_med"], 3)
        a.at[i, "components"] = r.components + f"; margin candidate = median published margin for this fuel ({stats[f]['mg_med']:.3f}; range {stats[f]['mg_min']:.3f} to {stats[f]['mg_max']:.3f}) in {stats[f]['who']}"

a.to_csv(os.path.join(OUT, "adders_2024.csv"), index=False)
with open(os.path.join(OUT, "adders_working.txt"), "w", encoding="utf-8") as f:
    f.write("Benchmarks 2024 USD/GJ: " + ", ".join(f"{k}={v:.3f}" for k, v in BM.items()) + "\n")
    f.write("Exchange rates: " + "; ".join(f"{k}: {v[0]} {v[1]}" for k, v in FX.items()) + "\n\n")
    f.write("\n".join(work) + "\n\nObserved-set statistics by fuel (regulator price structures only):\n")
    for k, s in stats.items():
        f.write(f"{k}: " + ", ".join(f"{a_}={b_ if isinstance(b_, str) else round(b_, 3)}" for a_, b_ in s.items()) + "\n")
pd.set_option("display.width", 250)
print(a[["country", "fuel", "method", "benchmark_2024_usd_per_gj", "observed_import_cost_usd_per_gj", "import_adder_usd_per_gj", "margin_usd_per_gj", "adder_usd_per_gj"]].to_string())
