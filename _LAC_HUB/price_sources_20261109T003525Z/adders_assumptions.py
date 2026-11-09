"""Step 4 (part 2): fill built LNG adders and ASSUMPTION candidates in adders_2024.csv. Run after adders.py.
Run: py -I adders_assumptions.py <output_folder>"""
import sys, os, pandas as pd
OUT = sys.argv[1]
a = pd.read_csv(os.path.join(OUT, "adders_2024.csv"))
h = pd.read_csv(os.path.join(OUT, "history_usd_per_gj.csv"))
B = h[h.year == 2024].set_index("benchmark").usd_per_gj
MM = 1.055056
fob_spread = B["LNG_FOB_US_to_DR"] - B["NGS_HH"]          # EIA 2024: FOB price of US LNG to DR minus Henry Hub
ship_lo, ship_mid, ship_hi = 0.5 / MM, 1.5 / MM, 4.5 / MM  # LNG Industry 2017: 0.5-2.5 USD/MMBtu at 90% use; 1.0-4.5 at 50%
LNG_SRC = "https://www.eia.gov/dnav/ng/xls/NG_MOVE_EXPC_S1_M.xls; https://www.eia.gov/dnav/ng/xls/NG_PRI_FUT_S1_M.xls; https://www.lngindustry.com/liquefaction/29112017/will-a-gas-market-develop-in-the-caribbean-part-two"
obs_ngs = a[(a.fuel == "NGS") & a.method.str.startswith("observed")].set_index("country").adder_usd_per_gj
foi_obs = a[(a.fuel == "FOI") & (a.method == "observed (regulator price structure)")]
foi_med_imp, foi_med_mg = foi_obs.import_adder_usd_per_gj.median(), foi_obs.margin_usd_per_gj.median()

ASSUME = {
 "COA": dict(adder=1.0, lo=0.6, hi=1.6, s=("Imported steam coal delivered to the plant or industrial user costs about 1.0 USD/GJ (range 0.6 to 1.6 USD/GJ, "
      "equal to 15 to 40 USD/t at 25.1 GJ/t) above the World Bank South African fob Richards Bay benchmark, covering ocean freight from Colombia or the "
      "US Gulf, insurance, port handling and inland transport, held constant in real terms. Applies to all six countries for 2024 onward."),
      check="Check: the Dominican Ministry of Energy and Mines bulletins quote coal fob Puerto Bolivar (Colombia) at 3.58 USD/MMBtu (3.39 USD/GJ) for 2024 months, below the South African benchmark of 4.21 USD/GJ, so the benchmark already sits about 0.8 USD/GJ above the Colombian origin price and the central adder is at the low end of a full freight leg."),
 "COK": dict(adder=0.8, lo=0.5, hi=1.2, s=("Imported petroleum coke delivered to the cement or power plant costs about 0.8 USD/GJ (range 0.5 to 1.2 USD/GJ, "
      "equal to 15 to 40 USD/t at 32.5 GJ/t) above the EIA US delivered petroleum coke proxy, covering ocean freight from the US Gulf, insurance and port handling, "
      "held constant in real terms. Applies to all six countries for 2024 onward."),
      check="Check: no published delivered petcoke price was retrieved for the six countries; the per-tonne freight range is the same as for coal."),
 "CRU": dict(adder=0.35, lo=0.17, hi=0.52, s=("Imported crude oil delivered to the refinery costs about 0.35 USD/GJ (range 0.17 to 0.52 USD/GJ, equal to 1 to 3 USD/bbl) "
      "above Brent, covering tanker freight in the Caribbean basin and insurance, held constant in real terms. Applies to the Dominican Republic and Ecuador."),
      check="Check: UN Comtrade reports Jamaica's 2024 crude imports (HS 2709) at 586.37 USD/t CIF, 13.86 USD/GJ, close to the 2024 Brent benchmark of 13.94 USD/GJ, so grade discounts can offset freight."),
}
for i, r in a.iterrows():
    f = r.fuel
    if f == "NGS" and r.method.startswith("ASSUMPTION"):
        a.at[i, "method"] = "built (published rates)"
        a.at[i, "import_adder_usd_per_gj"] = round(fob_spread + ship_mid, 3)
        a.at[i, "margin_usd_per_gj"] = 0.0
        a.at[i, "adder_usd_per_gj"] = round(fob_spread + ship_mid, 3)
        a.at[i, "pre_tax_price_2024_usd_per_gj"] = round(r.benchmark_2024_usd_per_gj + fob_spread + ship_mid, 3)
        a.at[i, "components"] = (f"EIA 2024 FOB price of US LNG exports to the Dominican Republic minus Henry Hub = {fob_spread:.3f} USD/GJ (liquefaction spread), "
                                 f"plus small-scale shipping and regasification 1.5 USD/MMBtu = {ship_mid:.3f} USD/GJ (mid of 0.5-2.5 USD/MMBtu at 90% utilisation, LNG Industry 2017); "
                                 f"range {fob_spread+ship_lo:.2f} to {fob_spread+ship_hi:.2f} USD/GJ (4.5 USD/MMBtu at 50% utilisation); "
                                 f"observed totals: Dominican Republic {obs_ngs.get('DominicanRepublic')}, Jamaica {obs_ngs.get('Jamaica')} USD/GJ; gross calorific basis")
        a.at[i, "sources"] = LNG_SRC
    elif f in ASSUME and r.method.startswith("ASSUMPTION"):
        s = ASSUME[f]
        a.at[i, "adder_usd_per_gj"] = s["adder"]
        a.at[i, "pre_tax_price_2024_usd_per_gj"] = round(r.benchmark_2024_usd_per_gj + s["adder"], 3)
        a.at[i, "components"] = f"ASSUMPTION candidate {s['adder']} USD/GJ (range {s['lo']} to {s['hi']}): " + s["s"] + " " + s["check"]
        a.at[i, "sources"] = "check source: " + ("https://mem.gob.do (Boletin de Generacion y Gestion de Energia 2024, see sources.csv)" if f == "COA" else
                                                 "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=388&period=2024&partnerCode=0&flowCode=M&cmdCode=271012,271019,271111,271112,271113,271121,270112,270119,2709,271020" if f == "CRU" else "")
    elif f == "FOI" and r.country == "Ecuador":
        a.at[i, "method"] = "built (regional published data)"
        a.at[i, "import_adder_usd_per_gj"] = round(foi_med_imp, 3)
        a.at[i, "margin_usd_per_gj"] = round(foi_med_mg, 3)
        a.at[i, "adder_usd_per_gj"] = round(foi_med_imp + foi_med_mg, 3)
        a.at[i, "pre_tax_price_2024_usd_per_gj"] = round(r.benchmark_2024_usd_per_gj + foi_med_imp + foi_med_mg, 3)
        a.at[i, "components"] = (r.components + f"; built as median of observed regulator fuel oil import adders ({foi_med_imp:.3f}) and margins ({foi_med_mg:.3f}) "
                                 f"in {', '.join(foi_obs.country)}; an export-parity alternative would use the EP Petroecuador 2024 fuel oil No. 6 export FOB of 61.68 USD/bbl "
                                 f"= {61.68*6.62/40.4:.3f} USD/GJ, {61.68*6.62/40.4 - r.benchmark_2024_usd_per_gj:.3f} USD/GJ against the benchmark")
a.to_csv(os.path.join(OUT, "adders_2024.csv"), index=False)
print(a[a.method.str.contains("ASSUMPTION|built")][["country", "fuel", "method", "adder_usd_per_gj"]].to_string())
