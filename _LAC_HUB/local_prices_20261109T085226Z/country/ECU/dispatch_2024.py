"""Unit values of EP Petroecuador 2024 dispatches to the electric sector, excluding VAT.

Source: EP Petroecuador, Informe Estadistico Mensual enero - diciembre 2024 (ECU source in sources_ECU.csv),
PDF p.51 (printed p.50) "Despachos por sectores de la abastecedora" (barrels; natural gas in MMBTU) and
PDF p.53 (printed p.52) "Despachos valorados de la abastecedora" (USD).
Monthly figures below are copied from the text layer of those two pages (checked against the page render).

VAT: the dispatch values match the VAT-inclusive terminal prices of the EP Petroecuador price structures
(for example Diesel 2 electric January 5,714,009.62 USD / (150,777 bbl x 42) = 0.9023 USD/gal against
0.900704 USD/gal including 12 percent VAT). VAT rate 12 percent January to March 2024 and 15 percent
from April 2024 (Decreto Ejecutivo 198, cited in Registro Oficial 529 Segundo Suplemento, and stated in each
monthly structure file). Values excluding VAT = value / 1.12 (Jan-Mar) or / 1.15 (Apr-Dec).

Usage: py -I dispatch_2024.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
VAT = [0.12] * 3 + [0.15] * 9

# Natural gas: value row "GAS NATURAL (MMBTU)" (all sectors) p.53; volume electric p.51; industrial total 17,881 MMBTU
gas_val = [1501458.31, 1471118.60, 1468041.08, 1533434.03, 1515884.55, 1453511.01, 1475841.13, 1430612.89,
           1683826.04, 1958905.59, 2216296.15, 2352095.18]
gas_vol_elec = [462022, 452686, 451739, 459552, 451656, 433196, 438343, 425619, 502181, 584558, 553596, 540760]
gas_vol_total_annual = 5773789  # 5,755,908 electric + 17,881 industrial (p.51); equals Despachos total in p.47 table
# Fuel oil No. 4 to electric sector: value row FUEL OIL # 4 Electrico p.53; volume ELECTRICO Fuel Oil # 4 p.51
fo4_val = [9253336.79, 6778288.11, 8419643.22, 8676066.55, 8847666.27, 2640376.06, 6780435.06, 9181769.04,
           9063992.15, 11464509.39, 11319948.73, 8355832.80]
fo4_vol = [409087, 299666, 372229, 374678, 380966, 113690, 291954, 395352, 390281, 493643, 487418, 359788]
# Residuo to electric sector
res_val = [3515636.31, 3451934.05, 4225292.05, 4771008.30, 5318323.86, 1838574.33, 3000208.52, 4230725.79,
           6201613.91, 4609981.80, 7532743.11, 6243167.58]
res_vol = [220062, 214374, 267445, 294527, 323842, 109795, 177277, 254183, 366009, 274763, 440793, 367354]
# Diesel 2 to electric sector (value row Diesel 2 Electrico; volume Diesel 2 electric)
d2_val = [5714009.62, 5073972.94, 6519613.15, 11720998.96, 7977047.47, 918817.51, 2330331.31, 8919589.17,
          9389393.29, 15254056.81, 15888632.42, 12047553.96]
d2_vol = [150777, 133888, 172035, 301908, 205011, 23614, 59890, 229234, 241308, 392030, 408339, 309623]


def ex(vals):
    return [v / (1 + t) for v, t in zip(vals, VAT)]


def report(name, vals, vols, unit, vol_override=None):
    tot_in = sum(vals)
    tot_ex = sum(ex(vals))
    vol = vol_override if vol_override else sum(vols)
    print(f"{name}: value incl VAT {tot_in:,.2f} USD; value excl VAT {tot_ex:,.2f} USD; volume {vol:,} {unit}; "
          f"unit incl VAT {tot_in/vol:.4f}; unit excl VAT {tot_ex/vol:.4f} USD/{unit}")
    for m, (a, b, t) in enumerate(zip(vals, vols, VAT), start=1):
        print(f"   month {m:2d}: {a/b:.4f} incl VAT, {a/b/(1+t):.4f} excl VAT USD/{unit} (electric volume basis)")
    return tot_ex / vol


g = report("Natural gas (all sectors value / all sectors volume)", gas_val, gas_vol_elec, "MMBTU", gas_vol_total_annual)
f = report("Fuel oil No. 4 electric", fo4_val, fo4_vol, "bbl")
r = report("Residuo electric", res_val, res_vol, "bbl")
d = report("Diesel 2 electric", d2_val, d2_vol, "bbl")
print(f"FO4 electric excl VAT per gallon: {f/42:.6f}; residuo: {r/42:.6f}; diesel 2: {d/42:.6f}")
gas_ex_janoct = sum(ex(gas_val)[:10]) / sum(gas_vol_elec[:10])
print(f"Natural gas Jan-Oct excl VAT (electric volume basis): {gas_ex_janoct:.4f} USD/MMBTU; Nov-Dec: "
      f"{sum(ex(gas_val)[10:]) / sum(gas_vol_elec[10:]):.4f}")
