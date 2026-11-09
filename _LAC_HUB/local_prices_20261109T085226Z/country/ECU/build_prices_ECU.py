"""Build prices_ECU.csv (2024) for Ecuador.

Usage: py -I build_prices_ECU.py <structures_2024_means.csv> <out_prices_csv>

Inputs other than the structure means are typed below with their source id and page; each was read in
this session from the downloaded file named in the row. Shared constants are the hub values named in
AGENT_BRIEF.md; ECU_ constants are in constants_ECU.csv.
"""
import csv
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
means_csv, out = sys.argv[1], sys.argv[2]

# Shared constants (hub)
GAL_T = {"GSL": 357, "DSL": 304, "JET": 326, "KER": 326, "FOI": 278, "LPG": 489}
NCV = {"GSL": 44.3, "DSL": 43.0, "JET": 44.1, "KER": 43.8, "FOI": 40.4, "LPG": 47.3, "CRU": 42.3, "COK": 32.5,
       "COA_OTHER_BITUMINOUS": 25.8}
USGAL_PER_BBL = 42
UN_BBL_PER_T_CRU = 7.32
GJ_PER_MMBTU = 1.055056
# Ecuador constants
NCV_ANTHRACITE = 26.7

means = {}
with open(means_csv, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        means[r["product"]] = r

STRUCT_IDS = "ECU-003;ECU-004;ECU-005;ECU-006;ECU-007;ECU-008;ECU-009;ECU-010;ECU-011;ECU-012;ECU-013;ECU-014;ECU-015"
STRUCT_FILE = ";".join("ECU/estructuras/EPP_ESTRUCTURA-DE-PRECIOS-%s.pdf" % m for m in ["DICIEMBRE-2023", "ENERO-2024", "FEBRERO-2024", "MARZO-2024", "ABRIL-2024", "MAYO-2024", "JUNIO-2024", "JULIO-2024", "AGOSTO-2024", "SEPTIEMBRE-2024", "OCTUBRE-2024", "NOVIEMBRE-2024", "DICIEMBRE-2024"])
STRUCT_PERIOD = "1 Jan 2024 to 31 Dec 2024, day-weighted over 366 days (structures in force 12 Dec 2023 to 11 Jan 2025)"
STRUCT_MONTHS = "Jan;Feb;Mar;Apr;May;Jun;Jul;Aug;Sep;Oct;Nov;Dec"

rows = []


def add(**k):
    base = dict(country="Ecuador", year=2024, fob="", freight="", insurance="", port="", importer_terminal_margin="",
                wholesale_margin="", inland_freight="", retail_margin="", currency="USD", exchange_rate="",
                exchange_rate_constant="", notes="")
    base.update(k)
    rows.append(base)


def gal_to_gj(x, fuel):
    return x * GAL_T[fuel] / NCV[fuel]


def bbl_to_gj(x, fuel):
    return x / USGAL_PER_BBL * GAL_T[fuel] / NCV[fuel]


def m(product):
    return float(means[product]["mean_excl_vat"])


def mi(product):
    return float(means[product]["mean_incl_vat"])


def struct_deriv(product, fuel, extra=""):
    v = m(product)
    return (f"mean of {means[product]['days_2024']} daily terminal prices of '{product}' in 2024 = {mi(product):.6f} USD/gal incl VAT; "
            f"each day divided by (1 + VAT) with VAT 12 percent (ECU_VAT_2024_JAN_MAR) or 15 percent (ECU_VAT_2024_APR_DEC) as printed in the file in force "
            f"= {v:.6f} USD/gal excl VAT{extra}; x {GAL_T[fuel]} gal/t (UN_GAL_PER_T_{fuel}) / {NCV[fuel]} GJ/t (IPCC_NCV_{fuel})")


# ---------------- COA ----------------
cif, kg, fob = 3506260.772, 14734330.0, 2772874.243
ut, uf = cif / kg * 1000, fob / kg * 1000
add(fuel="COA", model_code="DIST_COA", price_point="import CIF", fob=round(uf, 4),
    price_as_published=round(ut, 4), unit="USD/t", period="calendar year 2024", months_covered="12",
    tax_treatment="customs value, excludes duties and VAT", calorific_basis="not stated",
    conversion_constants="ECU_IPCC_NCV_ANTHRACITE", value_usd_per_gj=round(ut / NCV_ANTHRACITE, 4),
    evidence_class="international customs (Comtrade)", source_id="ECU-017;ECU-018",
    page_or_table="Comtrade record reporter 218, flow M, cmdCode 2701, partner World, 2024 (cifvalue, fobvalue, netWgt); 6-digit split from cmdCode 270111 and 270112",
    downloaded_file="ECU/comtrade_ECU_2024_M_4digit.json",
    derivation=(f"cifvalue {cif:,.3f} USD / netWgt {kg:,.0f} kg x 1000 = {ut:.4f} USD/t CIF; fobvalue {fob:,.3f} USD / netWgt = {uf:.4f} USD/t FOB; "
                f"{ut:.4f} USD/t / {NCV_ANTHRACITE} GJ/t (ECU_IPCC_NCV_ANTHRACITE, net) = {ut/NCV_ANTHRACITE:.4f} USD/GJ"),
    notes=("isQtyEstimated and isNetWgtEstimated False; qtyUnitCode 8 (kg). HS 270111 anthracite is 14,681,298 kg (99.6 percent) at 3,472,414.222 USD CIF; "
           "270112 bituminous 49,000 kg; Comtrade CIF minus FOB = 49.77 USD/t (freight and insurance, not split). "
           f"With IPCC_NCV_COA_OTHER_BITUMINOUS 25.8 GJ/t the value would be {ut/25.8:.4f} USD/GJ. Coal does not appear in the BEN 2024 import table (ECU-021 p.115). "
           "National customs (SENAE) quantity data were not retrievable as files; see search log."))

# ---------------- COK ----------------
cif, kg, qty = 30287760.08, 245618130.0, 315051290.0
ut = cif / kg * 1000
add(fuel="COK", model_code="DIST_COK", price_point="import CIF", price_as_published=round(ut, 4), unit="USD/t",
    period="calendar year 2024", months_covered="12", tax_treatment="customs value, excludes duties and VAT",
    calorific_basis="not stated", conversion_constants="IPCC_NCV_COK", value_usd_per_gj=round(ut / NCV["COK"], 4),
    evidence_class="international customs (Comtrade)", source_id="ECU-018;ECU-023",
    page_or_table="Comtrade record reporter 218, flow M, cmdCode 271311 (petroleum coke, not calcined), partner World, 2024; BCE ResultCE IV-2024 p.38 Anexo 1 subpartida 2713110000",
    downloaded_file="ECU/comtrade_ECU_2024_M_6digit.json",
    derivation=(f"cifvalue {cif:,.2f} USD / netWgt {kg:,.0f} kg x 1000 = {ut:.4f} USD/t CIF; / {NCV['COK']} GJ/t (IPCC_NCV_COK, net) = {ut/NCV['COK']:.4f} USD/GJ"),
    notes=(f"Comtrade qty field is {qty:,.0f} kg (qtyUnitCode 8) against netWgt {kg:,.0f} kg; on qty the unit value would be {cif/qty*1000:.4f} USD/t ({cif/qty*1000/NCV['COK']:.4f} USD/GJ); estimate flags False for both. "
           "BCE publishes 2024 FOB imports of subpartida 2713110000 as 8.6 + 2.4 + 7.3 + 3.3 = 21.6 million USD (quarters I to IV, ECU-023 p.38) but no quantity. "
           "BEN 2024 records petroleum coke imports of 1,081 kBEP (ECU-021 p.115). Calcined coke 271312: 45,189 kg only."))

# ---------------- NGS ----------------
gas_ex, gas_in, gas_vol = 17547799.73, 20061024.56, 5773789
g = gas_ex / gas_vol
add(fuel="NGS", model_code="DIST_NGS", price_point="generator delivered", price_as_published=round(gas_in / gas_vol, 4),
    unit="USD/MMBTU", period="calendar year 2024", months_covered="12",
    tax_treatment="published value includes VAT; value_usd_per_gj excludes VAT (derived)", calorific_basis="not stated",
    conversion_constants="GJ_PER_MMBTU;ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC", value_usd_per_gj=round(g / GJ_PER_MMBTU, 4),
    evidence_class="local regulator or operator", source_id="ECU-001",
    page_or_table="PDF p.53 Despachos valorados, row GAS NATURAL (MMBTU), months Jan-Dec 2024; PDF p.51 Despachos por sectores, ELECTRICO and INDUSTRIAL rows GAS NATURAL (MMBTU)",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=(f"sum of monthly dispatch values {gas_in:,.2f} USD incl VAT; each month divided by 1.12 (Jan-Mar, ECU_VAT_2024_JAN_MAR) or 1.15 (Apr-Dec, ECU_VAT_2024_APR_DEC) = {gas_ex:,.2f} USD excl VAT; "
                f"/ {gas_vol:,} MMBTU dispatched (5,755,908 electric + 17,881 industrial) = {g:.4f} USD/MMBTU excl VAT; / {GJ_PER_MMBTU} GJ/MMBTU (GJ_PER_MMBTU) = {g/GJ_PER_MMBTU:.4f} USD/GJ; script dispatch_2024.py"),
    notes=("Domestic gas from the Amistad field sold by EP Petroecuador; 99.7 percent of dispatched volume went to the electric sector (CELEC Termogas Machala). "
           "Monthly unit value excl VAT about 2.90-2.92 USD/MMBTU January to October and 3.63 USD/MMBTU November-December, when it reached the industrial terminal price of 3.7705 USD/MMBTU excl VAT. "
           "VAT inclusion inferred from the diesel and fuel oil electric rows of the same table, which match the VAT-inclusive structure prices. "
           "Per coordinator rule the MMBTU price is kept on its published basis (not stated; per-MMBTU prices treated as gross) and not converted to net. "
           "EP Petroecuador's 2024 cost of natural gas sales was 22,287 thousand USD (ECU-024 p.61 Nota 28)."))
v = m("GAS NATURAL")
add(fuel="NGS", model_code="DIST_NGS", price_point="final consumer pre-tax", price_as_published=round(mi("GAS NATURAL"), 6),
    unit="USD/MMBTU", period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS,
    tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT", calorific_basis="not stated",
    conversion_constants="GJ_PER_MMBTU;ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC", value_usd_per_gj=round(v / GJ_PER_MMBTU, 4),
    evidence_class="local regulator or operator", source_id=STRUCT_IDS,
    page_or_table="p.1 SECTOR INDUSTRIAL, row GAS NATURAL (Millon de BTUs)", downloaded_file=STRUCT_FILE,
    derivation=(f"terminal price 4.222960 USD/MMBTU incl 12 percent VAT (Jan-Mar files) and 4.336075 incl 15 percent VAT (Apr-Dec files) = {v:.6f} USD/MMBTU excl VAT in every file; "
                f"/ {GJ_PER_MMBTU} (GJ_PER_MMBTU) = {v/GJ_PER_MMBTU:.4f} USD/GJ; script structures_2024.py"),
    notes="Piped natural gas sold at the EP Petroecuador terminal to industrial users (17,881 MMBTU dispatched to industry in 2024, ECU-001 p.51). Basis per MMBTU not stated; kept as published.")
v = m("GAS NATURAL LICUADO")
add(fuel="NGS", model_code="DIST_NGS", price_point="final consumer pre-tax", price_as_published=round(mi("GAS NATURAL LICUADO"), 6),
    unit="USD/MMBTU", period="2024, day-weighted over 336 days with a positive price (12 Sep to 11 Oct 2024 structure shows 0.000000)",
    months_covered="Jan;Feb;Mar;Apr;May;Jun;Jul;Aug;Sep;Oct;Nov;Dec (11 Sep to 11 Oct excluded)",
    tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT", calorific_basis="not stated",
    conversion_constants="GJ_PER_MMBTU;ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC", value_usd_per_gj=round(v / GJ_PER_MMBTU, 4),
    evidence_class="local regulator or operator", source_id=STRUCT_IDS,
    page_or_table="p.1 SECTOR INDUSTRIAL, row GAS NATURAL LICUADO (Millon de BTUs)", downloaded_file=STRUCT_FILE,
    derivation=(f"day-weighted mean of 336 daily terminal prices = {mi('GAS NATURAL LICUADO'):.6f} incl VAT, {v:.6f} USD/MMBTU excl VAT (range {means['GAS NATURAL LICUADO']['min_excl_vat']} to {means['GAS NATURAL LICUADO']['max_excl_vat']}); "
                f"/ {GJ_PER_MMBTU} (GJ_PER_MMBTU) = {v/GJ_PER_MMBTU:.4f} USD/GJ; script structures_2024.py"),
    notes="LNG from the Bajo Alto plant sold to industry (1,151,820 MMBTU dispatched in 2024, ECU-001 p.51). Basis per MMBTU not stated; kept as published.")

# ---------------- FOI ----------------
fo6_vol, fo6_val = 6253273, 385717277.14
p = fo6_val / fo6_vol
add(fuel="FOI", model_code="DIST_FOI", price_point="export FOB", price_as_published=61.68, fob=61.68, unit="USD/bbl",
    period="calendar year 2024 (no exports in December)", months_covered="Jan;Feb;Mar;Apr;May;Jun;Jul;Aug;Sep;Oct;Nov",
    tax_treatment="FOB export value, no taxes", calorific_basis="not stated",
    conversion_constants="USGAL_PER_BBL;UN_GAL_PER_T_FOI;IPCC_NCV_FOI", value_usd_per_gj=round(bbl_to_gj(p, "FOI"), 4),
    evidence_class="local regulator or operator", source_id="ECU-001",
    page_or_table="PDF p.57 (printed p.56) Exportacion de Fuel Oil No. 6 realizada por EP Petroecuador, Ano 2024, row TOTAL",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=(f"{fo6_val:,.2f} USD FOB / {fo6_vol:,} bbl = {p:.4f} USD/bbl (published 61.68); / 42 (USGAL_PER_BBL) x 278 (UN_GAL_PER_T_FOI) / 40.4 (IPCC_NCV_FOI) = {bbl_to_gj(p,'FOI'):.4f} USD/GJ"),
    notes="Fuel Oil No. 6 exported by EP Petroecuador; Ecuador imported no fuel oil in 2024 (ECU-001 p.63; BEN 2024 Tabla 5.4 shows fuel oil imports of zero). BCE gives the same 61.68 USD/bbl (ECU-002 rows 120-121).")
add(fuel="FOI", model_code="DIST_FOI", price_point="generator delivered", price_as_published=0.48, unit="USD/gal",
    period="calendar year 2024 (same terminal price excl VAT all year)", months_covered=STRUCT_MONTHS,
    tax_treatment="excludes VAT", calorific_basis="not stated", conversion_constants="UN_GAL_PER_T_FOI;IPCC_NCV_FOI",
    value_usd_per_gj=round(gal_to_gj(0.48, "FOI"), 4), evidence_class="local regulator or operator",
    source_id="ECU-016;" + STRUCT_IDS,
    page_or_table="ECU-016 PDF p.37 Art. 1 Fuel Oil 4 Sector Electrico (Ref. Libertad) 0,480000 USD/galon sin IVA; structures p.1 SECTORES ELECTRICO Y OTROS row FUEL OIL 4 ELECTRICO LIBERTAD (0.537600 incl 12 percent VAT, 0.552000 incl 15 percent VAT)",
    downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=f"0.48 USD/gal x 278 (UN_GAL_PER_T_FOI) / 40.4 (IPCC_NCV_FOI) = {gal_to_gj(0.48,'FOI'):.4f} USD/GJ",
    notes="Regulated terminal price for fuel oil No. 4 from La Libertad refinery to thermal plants of majority state-owned companies; administered price far below export parity.")
add(fuel="FOI", model_code="DIST_FOI", price_point="generator delivered", price_as_published=0.62, unit="USD/gal",
    period="from 1 April 2024 (Decreto 215); same value in the Decreto 308 regime", months_covered="Apr;May;Jun;Jul;Aug;Sep;Oct;Nov;Dec",
    tax_treatment="excludes VAT", calorific_basis="not stated", conversion_constants="UN_GAL_PER_T_FOI;IPCC_NCV_FOI",
    value_usd_per_gj=round(gal_to_gj(0.62, "FOI"), 4), evidence_class="local regulator or operator", source_id="ECU-016",
    page_or_table="PDF p.37 Art. 1 Fuel Oil 4 Sector Electrico 0,620000 USD/galon sin IVA", downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=f"0.62 USD/gal x 278 (UN_GAL_PER_T_FOI) / 40.4 (IPCC_NCV_FOI) = {gal_to_gj(0.62,'FOI'):.4f} USD/GJ",
    notes="Regulated terminal price for fuel oil No. 4 at other dispatch points; not listed in the monthly structures. Months before April 2024 not checked against the earlier decree text (on manual list).")
fo4_ex, fo4_vol = 88205920.74, 4368752
pb = fo4_ex / fo4_vol
add(fuel="FOI", model_code="DIST_FOI", price_point="generator delivered", price_as_published=round(100781864.17 / fo4_vol, 4), unit="USD/bbl",
    period="calendar year 2024", months_covered="12",
    tax_treatment="published value includes VAT; value_usd_per_gj excludes VAT (derived)", calorific_basis="not stated",
    conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;USGAL_PER_BBL;UN_GAL_PER_T_FOI;IPCC_NCV_FOI",
    value_usd_per_gj=round(bbl_to_gj(pb, "FOI"), 4), evidence_class="local regulator or operator", source_id="ECU-001",
    page_or_table="PDF p.53 Despachos valorados row FUEL OIL # 4 Electrico; PDF p.51 ELECTRICO row Fuel Oil # 4",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=(f"100,781,864.17 USD incl VAT; monthly / 1.12 (Jan-Mar) or / 1.15 (Apr-Dec) = {fo4_ex:,.2f} USD excl VAT; / {fo4_vol:,} bbl = {pb:.4f} USD/bbl ({pb/42:.6f} USD/gal); "
                f"/ 42 x 278 / 40.4 = {bbl_to_gj(pb,'FOI'):.4f} USD/GJ; script dispatch_2024.py"),
    notes="Actual average paid for fuel oil No. 4 dispatched to the electric sector; consistent with the regulated 0.48 USD/gal. Residuo to the electric sector averaged 14.51 USD/bbl excl VAT (0.3455 USD/gal) on the same basis.")
v = m("FUEL OIL 6 ELECTRICO")
add(fuel="FOI", model_code="DIST_FOI", price_point="generator delivered", price_as_published=0.417879, unit="USD/gal",
    period="12 Jul 2024 to 31 Dec 2024 (173 days in structures)", months_covered="Jul;Aug;Sep;Oct;Nov;Dec",
    tax_treatment="published price includes 15 percent VAT; value_usd_per_gj excludes VAT", calorific_basis="not stated",
    conversion_constants="ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_FOI;IPCC_NCV_FOI", value_usd_per_gj=round(gal_to_gj(v, "FOI"), 4),
    evidence_class="local regulator or operator", source_id="ECU-010;ECU-011;ECU-012;ECU-013;ECU-014;ECU-015",
    page_or_table="p.1 SECTORES ELECTRICO Y OTROS row FUEL OIL 6 ELECTRICO", downloaded_file=";".join("ECU/estructuras/EPP_ESTRUCTURA-DE-PRECIOS-%s-2024.pdf" % m for m in ["JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]),
    derivation=f"0.417879 USD/gal incl VAT / 1.15 (ECU_VAT_2024_APR_DEC) = {v:.6f} USD/gal; x 278 / 40.4 = {gal_to_gj(v,'FOI'):.4f} USD/GJ",
    notes="Fuel oil No. 6 for electric generation appears only in the July to December 2024 structures.")
for prod, lab in (("FUEL OIL No. 6 INDUSTRIAL", "fuel oil No. 6 industrial"), ("RESIDUO INDUSTRIAL", "residuo industrial")):
    v = m(prod)
    add(fuel="FOI", model_code="DIST_FOI", price_point="final consumer pre-tax", price_as_published=round(mi(prod), 6), unit="USD/gal",
        period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT",
        calorific_basis="not stated", conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_FOI;IPCC_NCV_FOI",
        value_usd_per_gj=round(gal_to_gj(v, "FOI"), 4), evidence_class="local regulator or operator", source_id=STRUCT_IDS,
        page_or_table=f"p.1 SECTOR INDUSTRIAL row {prod}", downloaded_file=STRUCT_FILE,
        derivation=struct_deriv(prod, "FOI", f" (range {means[prod]['min_excl_vat']} to {means[prod]['max_excl_vat']})") + f" = {gal_to_gj(v,'FOI'):.4f} USD/GJ; script structures_2024.py",
        notes=f"EP Petroecuador terminal price to industrial users ({lab}); unsubsidised segment, set monthly. Distributor margin not regulated and not published.")

# ---------------- DSL ----------------
d_val, d_vol = 983330632.39 + 2551055619.48, 9347912 + 24229424
p = d_val / d_vol
add(fuel="DSL", model_code="DIST_DSL", price_point="import CIF", price_as_published=round(p, 4), unit="USD/bbl",
    period="calendar year 2024", months_covered="12 (December provisional)",
    tax_treatment="DAT/DPU value; excludes VAT, operating costs, customs taxes, CORPEI fee and insurance (table note b)",
    calorific_basis="not stated", conversion_constants="USGAL_PER_BBL;UN_GAL_PER_T_DSL;IPCC_NCV_DSL", value_usd_per_gj=round(bbl_to_gj(p, "DSL"), 4),
    evidence_class="local regulator or operator", source_id="ECU-001", page_or_table="PDF p.61 Importacion de diesel (Diesel Oil and Diesel Premium, Ano 2024 totals); p.63 Resumen de importaciones",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=(f"(983,330,632.39 + 2,551,055,619.48) USD / (9,347,912 + 24,229,424) bbl = {p:.4f} USD/bbl; / 42 x 304 (UN_GAL_PER_T_DSL) / 43.0 (IPCC_NCV_DSL) = {bbl_to_gj(p,'DSL'):.4f} USD/GJ"),
    notes="Delivered at place unloaded in Ecuador (ocean freight included, insurance excluded); FOB, freight and insurance not published separately. BCE gives the same 105.2611 USD/bbl (ECU-002 rows 148-150).")
for prod in ("DIESEL PREMIUM INDUSTRIAL", "DIESEL 2 INDUSTRIAL"):
    v = m(prod)
    add(fuel="DSL", model_code="DIST_DSL", price_point="wholesale import parity", price_as_published=round(mi(prod), 6), unit="USD/gal",
        period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT",
        calorific_basis="not stated", conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_DSL;IPCC_NCV_DSL",
        value_usd_per_gj=round(gal_to_gj(v, "DSL"), 4), evidence_class="local regulator or operator", source_id=STRUCT_IDS,
        page_or_table=f"p.1 SECTOR INDUSTRIAL row {prod}", downloaded_file=STRUCT_FILE,
        derivation=struct_deriv(prod, "DSL", f" (range {means[prod]['min_excl_vat']} to {means[prod]['max_excl_vat']})") + f" = {gal_to_gj(v,'DSL'):.4f} USD/GJ; script structures_2024.py",
        notes=("EP Petroecuador terminal price for the unsubsidised industrial segment, revised monthly; the structures do not split it into import cost and terminal margin. "
               f"Against the 2024 import DPU value of 2.5062 USD/gal the implied difference is {v - d_val/d_vol/42:.4f} USD/gal (not a published margin)."))
v = m("DIESEL PREMIUM (AUTOMOTRIZ)")
fc = v + 0.128438
add(fuel="DSL", model_code="DIST_DSL", price_point="final consumer pre-tax", retail_margin=0.128438, price_as_published=round(fc, 6), unit="USD/gal",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="excludes VAT", calorific_basis="not stated",
    conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_DSL;IPCC_NCV_DSL", value_usd_per_gj=round(gal_to_gj(fc, "DSL"), 4),
    evidence_class="built from published components", source_id="ECU-016;" + STRUCT_IDS,
    page_or_table="ECU-016 PDF p.36 Art. 1 Diesel automotriz terminal 1,434171 USD/galon sin IVA and p.37 Art. 4 margen de comercializacion Diesel 0,128438 USD/galon sin IVA; structures p.1 SECTOR AUTOMOTRIZ row DIESEL PREMIUM (AUTOMOTRIZ)",
    downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=(f"terminal price {v:.6f} USD/gal excl VAT (day-weighted mean of structures, ECU-003 to ECU-015; 1.434171 in ECU-016) + retail margin 0.128438 USD/gal (ECU-016 Art. 4) = {fc:.6f} USD/gal; "
                f"x 304 (UN_GAL_PER_T_DSL) / 43.0 (IPCC_NCV_DSL) = {gal_to_gj(fc,'DSL'):.4f} USD/GJ"),
    notes=("Regulated (subsidised) automotive diesel; maximum retail price = terminal + margin + VAT (ECU-016 p.37). The 0.128438 margin is the April 2024 text; the Decreto 308 text in force from 28 June 2024 is on the manual list. "
           "Inland freight not published separately (inside the margin)."))
add(fuel="DSL", model_code="DIST_DSL", price_point="generator delivered", price_as_published=0.8042, unit="USD/gal",
    period="calendar year 2024 (same terminal price excl VAT all year)", months_covered=STRUCT_MONTHS, tax_treatment="excludes VAT",
    calorific_basis="not stated", conversion_constants="UN_GAL_PER_T_DSL;IPCC_NCV_DSL", value_usd_per_gj=round(gal_to_gj(0.8042, "DSL"), 4),
    evidence_class="local regulator or operator", source_id="ECU-016;" + STRUCT_IDS,
    page_or_table="ECU-016 PDF p.36 Art. 1 Industrial, Diesel Sector Electrico 0,804200 USD/galon sin IVA; structures p.1 row DIESEL 2 / PREMIUM ELECTRICO (0.900704 incl 12 percent VAT; 0.924830 incl 15 percent VAT)",
    downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=f"0.8042 USD/gal x 304 (UN_GAL_PER_T_DSL) / 43.0 (IPCC_NCV_DSL) = {gal_to_gj(0.8042,'DSL'):.4f} USD/GJ",
    notes="Regulated terminal price for diesel to the electric sector. EP Petroecuador 2024 dispatch value to the electric sector gives 33.8267 USD/bbl excl VAT = 0.8054 USD/gal (ECU-001 p.51 and p.53; dispatch_2024.py).")

# ---------------- GSL ----------------
g_val, g_vol = 1422954107 + 846964971, 12895620 + 8737704
p = g_val / g_vol
add(fuel="GSL", model_code="DIST_GSL", price_point="import CIF", price_as_published=round(p, 4), unit="USD/bbl",
    period="calendar year 2024", months_covered="12 (December provisional)",
    tax_treatment="DAT/DPU value; excludes VAT, operating costs, customs taxes, CORPEI fee and insurance", calorific_basis="not stated",
    conversion_constants="USGAL_PER_BBL;UN_GAL_PER_T_GSL;IPCC_NCV_GSL", value_usd_per_gj=round(bbl_to_gj(p, "GSL"), 4),
    evidence_class="local regulator or operator", source_id="ECU-001", page_or_table="PDF p.63 Resumen de importaciones de derivados, rows Nafta Ron 95 and Nafta Ron 80, Enero-Diciembre 2024",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=f"(1,422,954,107 + 846,964,971) USD / (12,895,620 + 8,737,704) bbl = {p:.4f} USD/bbl; / 42 x 357 (UN_GAL_PER_T_GSL) / 44.3 (IPCC_NCV_GSL) = {bbl_to_gj(p,'GSL'):.4f} USD/GJ",
    notes="Imports are high and low octane naphtha blendstocks (RON 95 and RON 80), not finished gasoline; no Nafta RON 93 imports in 2024. BCE gives the same 104.927 USD/bbl (ECU-002 rows 141-143).")
for prod in ("EXTRA INDUSTRIAL", "SUPER PREMIUM 95 PREMIUM INDUSTRIAL", "GASOLINA SUPER PREMIUM 95 AUTOMOTRIZ"):
    v = m(prod)
    note = ("EP Petroecuador terminal price for the unsubsidised industrial segment, revised monthly; no split into import cost and terminal margin."
            if "INDUSTRIAL" in prod else
            "Terminal price of Super Premium 95 for automotive distributors (freely set monthly); the retail margin for this product is not regulated and not published (ECU-016 p.38).")
    add(fuel="GSL", model_code="DIST_GSL", price_point="wholesale import parity", price_as_published=round(mi(prod), 6), unit="USD/gal",
        period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT",
        calorific_basis="not stated", conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_GSL;IPCC_NCV_GSL",
        value_usd_per_gj=round(gal_to_gj(v, "GSL"), 4), evidence_class="local regulator or operator", source_id=STRUCT_IDS,
        page_or_table=f"p.1 row {prod}", downloaded_file=STRUCT_FILE,
        derivation=struct_deriv(prod, "GSL", f" (range {means[prod]['min_excl_vat']} to {means[prod]['max_excl_vat']})") + f" = {gal_to_gj(v,'GSL'):.4f} USD/GJ; script structures_2024.py",
        notes=note)
v = m("GASOLINA EXTRA AUTOMOTRIZ")
fc = v + 0.160313
add(fuel="GSL", model_code="DIST_GSL", price_point="final consumer pre-tax", retail_margin=0.160313, price_as_published=round(fc, 6), unit="USD/gal",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="excludes VAT", calorific_basis="not stated",
    conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_GSL;IPCC_NCV_GSL", value_usd_per_gj=round(gal_to_gj(fc, "GSL"), 4),
    evidence_class="built from published components", source_id="ECU-016;" + STRUCT_IDS,
    page_or_table="ECU-016 PDF p.37 Art. 4 margen de comercializacion Gasolina Extra 0,160313 USD/galon sin IVA; structures p.1 SECTOR AUTOMOTRIZ row GASOLINA EXTRA AUTOMOTRIZ",
    downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=(f"terminal price {v:.6f} USD/gal excl VAT (day-weighted mean of structures, range {means['GASOLINA EXTRA AUTOMOTRIZ']['min_excl_vat']} to {means['GASOLINA EXTRA AUTOMOTRIZ']['max_excl_vat']}) "
                f"+ retail margin 0.160313 USD/gal (ECU-016 Art. 4) = {fc:.6f} USD/gal; x 357 (UN_GAL_PER_T_GSL) / 44.3 (IPCC_NCV_GSL) = {gal_to_gj(fc,'GSL'):.4f} USD/GJ"),
    notes=("Extra and Ecopais (ethanol blend) share the same price. Subsidised until 27 June 2024, then a price band (Decreto 308). "
           "The structure in force 12 June to 11 July 2024 shows the pre-28 June price, so 14 days carry the old price (small downward bias). "
           "Margin text for the Decreto 308 period is on the manual list."))

# ---------------- LPG ----------------
add(fuel="LPG", model_code="DIST_LPG", price_point="import CIF", price_as_published=556.59, unit="USD/t", period="calendar year 2024",
    months_covered="12 (December provisional)", tax_treatment="DAT/DPU value; excludes VAT, operating costs, customs taxes, CORPEI fee and insurance",
    calorific_basis="not stated", conversion_constants="IPCC_NCV_LPG", value_usd_per_gj=round(556.59 / NCV["LPG"], 4),
    evidence_class="local regulator or operator", source_id="ECU-001", page_or_table="PDF p.59 Importacion de GLP, Ano 2024, rows TOTAL (15,171,599 bbl, 724,834,072.57 USD) and TOTAL TM (1,302,283 t, 556.59 USD/t)",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=f"724,834,072.57 USD / 1,302,283 t = 556.59 USD/t (published); / 47.3 GJ/t (IPCC_NCV_LPG) = {556.59/NCV['LPG']:.4f} USD/GJ")
v = m("GAS LICUADO DE PETROLEO (GLP) INDUSTRIAL")
add(fuel="LPG", model_code="DIST_LPG", price_point="wholesale import parity", price_as_published=round(mi("GAS LICUADO DE PETROLEO (GLP) INDUSTRIAL"), 6), unit="USD/kg",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT",
    calorific_basis="not stated", conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;IPCC_NCV_LPG", value_usd_per_gj=round(v * 1000 / NCV["LPG"], 4),
    evidence_class="local regulator or operator", source_id=STRUCT_IDS, page_or_table="p.1 SECTOR INDUSTRIAL row GAS LICUADO DE PETROLEO (GLP) INDUSTRIAL (Kilogramos)", downloaded_file=STRUCT_FILE,
    derivation=(f"day-weighted mean {mi('GAS LICUADO DE PETROLEO (GLP) INDUSTRIAL'):.6f} USD/kg incl VAT; each day / (1 + VAT) = {v:.6f} USD/kg excl VAT "
                f"(range {means['GAS LICUADO DE PETROLEO (GLP) INDUSTRIAL']['min_excl_vat']} to {means['GAS LICUADO DE PETROLEO (GLP) INDUSTRIAL']['max_excl_vat']}); x 1000 / 47.3 (IPCC_NCV_LPG) = {v*1000/NCV['LPG']:.4f} USD/GJ; script structures_2024.py"),
    notes="EP Petroecuador terminal price of LPG for industrial users (unsubsidised); no split into import cost and terminal margin.")
v = m("GAS LICUADO DE PETROLEO (G.L.P.) DOMÉSTICO")
add(fuel="LPG", model_code="DIST_LPG", price_point="final consumer pre-tax", price_as_published=0.095652, unit="USD/kg",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="excludes VAT", calorific_basis="not stated",
    conversion_constants="IPCC_NCV_LPG", value_usd_per_gj=round(v * 1000 / NCV["LPG"], 4), evidence_class="local regulator or operator",
    source_id="ECU-016;" + STRUCT_IDS,
    page_or_table="ECU-016 PDF p.38 Art. 8 GLP uso domestico 0,095652 USD/kg sin IVA, cylinder of 15 kg not above 1,65 USD; structures row GAS LICUADO DE PETROLEO (G.L.P.) DOMESTICO",
    downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=f"day-weighted mean of structures {v:.6f} USD/kg excl VAT (0.095652 in ECU-016); x 1000 / 47.3 (IPCC_NCV_LPG) = {v*1000/NCV['LPG']:.4f} USD/GJ",
    notes="Regulated subsidised household LPG; the decree sets the cylinder retail price at 1.65 USD per 15 kg with VAT (0.11 USD/kg), so no separate distribution margin is published for this segment.")
v = m("GAS LICUADO DE PETROLEO (G.L.P.) TAXIS")
fc = v + 0.13
add(fuel="LPG", model_code="DIST_LPG", price_point="final consumer pre-tax", retail_margin=0.13, price_as_published=round(fc, 6), unit="USD/kg",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="excludes VAT", calorific_basis="not stated",
    conversion_constants="IPCC_NCV_LPG", value_usd_per_gj=round(fc * 1000 / NCV["LPG"], 4), evidence_class="built from published components",
    source_id="ECU-016;" + STRUCT_IDS,
    page_or_table="ECU-016 PDF p.38 Art. 10 GLP taxis and agricultural drying 0,168261 USD/kg sin IVA, margen maximo 0,130000 USD/kg; structures rows G.L.P. TAXIS and G.L.P. AGRICOLA",
    downloaded_file="ECU/RO_529_2024_Decreto215.pdf",
    derivation=f"terminal {v:.6f} USD/kg excl VAT (structures mean; 0.168261 in ECU-016) + margin 0.13 USD/kg = {fc:.6f} USD/kg; x 1000 / 47.3 (IPCC_NCV_LPG) = {fc*1000/NCV['LPG']:.4f} USD/GJ",
    notes="Regulated LPG for registered taxis and grain drying; maximum consumer price 0.343 USD/kg with VAT (ECU-016 p.38).")

# ---------------- JET ----------------
p = 59736284.43 / 453513
add(fuel="JET", model_code="DIST_JET", price_point="import CIF", price_as_published=131.72, unit="USD/bbl",
    period="2024, months with imports: May, Jun, Jul, Aug, Sep, Oct, Dec", months_covered="May;Jun;Jul;Aug;Sep;Oct;Dec",
    tax_treatment="DAT/DPU value; excludes VAT, operating costs, customs taxes, CORPEI fee and insurance", calorific_basis="not stated",
    conversion_constants="USGAL_PER_BBL;UN_GAL_PER_T_JET;IPCC_NCV_JET", value_usd_per_gj=round(bbl_to_gj(p, "JET"), 4),
    evidence_class="local regulator or operator", source_id="ECU-001", page_or_table="PDF p.62 Importacion otros productos, JET A-1 Ano 2024 total",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=f"59,736,284.43 USD / 453,513 bbl = {p:.4f} USD/bbl; / 42 x 326 (UN_GAL_PER_T_JET) / 44.1 (IPCC_NCV_JET) = {bbl_to_gj(p,'JET'):.4f} USD/GJ",
    notes="Small cargoes (45 to 140 thousand bbl); domestic refineries supplied most jet fuel in 2024.")
v = m("JET FUEL TPCO")
add(fuel="JET", model_code="DIST_JET", price_point="wholesale import parity", price_as_published=round(mi("JET FUEL TPCO"), 6), unit="USD/gal",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT", calorific_basis="not stated",
    conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_JET;IPCC_NCV_JET", value_usd_per_gj=round(gal_to_gj(v, "JET"), 4),
    evidence_class="local regulator or operator", source_id=STRUCT_IDS, page_or_table="p.1 SECTOR AEREO row JET FUEL TPCO", downloaded_file=STRUCT_FILE,
    derivation=struct_deriv("JET FUEL TPCO", "JET", f" (range {means['JET FUEL TPCO']['min_excl_vat']} to {means['JET FUEL TPCO']['max_excl_vat']})") + f" = {gal_to_gj(v,'JET'):.4f} USD/GJ; script structures_2024.py",
    notes="EP Petroecuador terminal price of jet fuel to distributors, revised monthly; not split into import cost and margin.")

# ---------------- KER ----------------
v = m("DIESEL 1 INDUSTRIAL")
add(fuel="KER", model_code="DIST_KER", price_point="wholesale import parity", price_as_published=round(mi("DIESEL 1 INDUSTRIAL"), 6), unit="USD/gal",
    period=STRUCT_PERIOD, months_covered=STRUCT_MONTHS, tax_treatment="published price includes VAT; value_usd_per_gj excludes VAT", calorific_basis="not stated",
    conversion_constants="ECU_VAT_2024_JAN_MAR;ECU_VAT_2024_APR_DEC;UN_GAL_PER_T_KER;IPCC_NCV_KER", value_usd_per_gj=round(gal_to_gj(v, "KER"), 4),
    evidence_class="local regulator or operator", source_id=STRUCT_IDS + ";ECU-021", page_or_table="structures p.1 SECTOR INDUSTRIAL row DIESEL 1 INDUSTRIAL; ECU-021 PDF p.37 note (1) Diesel 1 (kerosene)",
    downloaded_file=STRUCT_FILE,
    derivation=struct_deriv("DIESEL 1 INDUSTRIAL", "KER", f" (range {means['DIESEL 1 INDUSTRIAL']['min_excl_vat']} to {means['DIESEL 1 INDUSTRIAL']['max_excl_vat']})") + f" = {gal_to_gj(v,'KER'):.4f} USD/GJ; script structures_2024.py",
    notes=("Ecuador sells kerosene as Diesel 1 (the national energy balance labels Diesel 1 as kerosene, ECU-021 p.37). Diesel 1 has the same terminal price as Diesel 2 industrial in every 2024 structure. "
           "Dispatches of Diesel 1 were 8,856 bbl in 2024, valued at 1,033,502.16 USD incl VAT (ECU-001 p.51 and p.53). No separate household kerosene price is published."))

# ---------------- CRU ----------------
c_val, c_vol = 7778608486.21, 113458936
p = c_val / c_vol
add(fuel="CRU", model_code="DIST_CRU", price_point="export FOB", fob=round(p, 4), price_as_published=68.56, unit="USD/bbl", period="calendar year 2024",
    months_covered="12 (December provisional)", tax_treatment="FOB export value, no taxes", calorific_basis="not stated",
    conversion_constants="UN_BBL_PER_T_CRU;IPCC_NCV_CRU", value_usd_per_gj=round(p * UN_BBL_PER_T_CRU / NCV["CRU"], 4),
    evidence_class="local regulator or operator", source_id="ECU-001", page_or_table="PDF p.55 (printed p.54) Exportacion total (crudo Oriente y Napo) realizado por EP Petroecuador, Ano 2024, row TOTAL",
    downloaded_file="ECU/EPP_Informe_Estadistico_2024.pdf",
    derivation=f"{c_val:,.2f} USD FOB / {c_vol:,} bbl = {p:.4f} USD/bbl (published 68.56); x 7.32 bbl/t (UN_BBL_PER_T_CRU) / 42.3 GJ/t (IPCC_NCV_CRU) = {p*UN_BBL_PER_T_CRU/NCV['CRU']:.4f} USD/GJ",
    notes=("Crude Oriente 71.10 USD/bbl (67,253,026 bbl) and Napo 64.85 USD/bbl (46,205,911 bbl). Values on bill of lading basis. "
           "No refinery transfer price for crude delivered to Esmeraldas, La Libertad or Shushufindi is published (see search log); export FOB is the opportunity value. "
           "Ecuador's crudes are heavier than the UN default (Oriente above 20 API, Napo below 20 API, ECU-002 notes 11-12), so 7.32 bbl/t overstates bbl per tonne slightly."))
c_val, c_vol = 8646543.479, 126312.805
p = c_val / c_vol
add(fuel="CRU", model_code="DIST_CRU", price_point="export FOB", fob=round(p, 4), price_as_published=round(p, 4), unit="USD/bbl", period="calendar year 2024",
    months_covered="12", tax_treatment="FOB export value, no taxes", calorific_basis="not stated",
    conversion_constants="UN_BBL_PER_T_CRU;IPCC_NCV_CRU", value_usd_per_gj=round(p * UN_BBL_PER_T_CRU / NCV["CRU"], 4),
    evidence_class="local customs or statistics", source_id="ECU-002", page_or_table="sheet Petroleo rows 94 (total exports, thousand bbl) and 96 (income, thousand USD), columns 2024 ene to dic",
    downloaded_file="ECU/BCE_SerieCifrasPetroleras.xlsx",
    derivation=f"sum of monthly income {c_val:,.3f} thousand USD / sum of monthly exports {c_vol:,.3f} thousand bbl = {p:.4f} USD/bbl; x 7.32 (UN_BBL_PER_T_CRU) / 42.3 (IPCC_NCV_CRU) = {p*UN_BBL_PER_T_CRU/NCV['CRU']:.4f} USD/GJ; script bce_annual.py",
    notes="All Ecuadorian crude exports (public companies, private companies and the Ministry), BCE provisional figures.")
fobv, kg = 7834790006.4, 17091526369.0
ut = fobv / kg * 1000
add(fuel="CRU", model_code="DIST_CRU", price_point="export FOB", fob=round(ut, 4), price_as_published=round(ut, 4), unit="USD/t", period="calendar year 2024",
    months_covered="12", tax_treatment="FOB export value, no taxes", calorific_basis="not stated", conversion_constants="IPCC_NCV_CRU",
    value_usd_per_gj=round(ut / NCV["CRU"], 4), evidence_class="international customs (Comtrade)", source_id="ECU-019",
    page_or_table="Comtrade record reporter 218, flow X, cmdCode 2709, partner World, 2024 (fobvalue, netWgt)", downloaded_file="ECU/comtrade_ECU_2024_X.json",
    derivation=f"fobvalue {fobv:,.1f} USD / netWgt {kg:,.0f} kg x 1000 = {ut:.4f} USD/t; / 42.3 GJ/t (IPCC_NCV_CRU) = {ut/NCV['CRU']:.4f} USD/GJ",
    notes="Comtrade value (7,834.8 million USD) is below the BCE income figure (8,646.5 million USD) for the same year; per-tonne basis avoids the barrel-density question.")

HDR = ["country", "fuel", "model_code", "price_point", "year", "fob", "freight", "insurance", "port", "importer_terminal_margin",
       "wholesale_margin", "inland_freight", "retail_margin", "price_as_published", "currency", "unit", "period", "months_covered",
       "tax_treatment", "calorific_basis", "exchange_rate", "exchange_rate_constant", "conversion_constants", "value_usd_per_gj",
       "evidence_class", "source_id", "page_or_table", "downloaded_file", "derivation", "notes"]
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=HDR)
    w.writeheader()
    for r in rows:
        w.writerow(r)
for r in rows:
    print(r["fuel"], r["price_point"], r["price_as_published"], r["unit"], r["value_usd_per_gj"], r["evidence_class"])
print(len(rows), "rows")
