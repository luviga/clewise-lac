"""Write GEN/gen_sector_values.csv (waste and wastewater cost values, externality rows)."""
import os
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
JOB = os.path.dirname(GEN)
cpi = {}
with open(os.path.join(JOB, "cpi_u.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        cpi[int(r["year"])] = float(r["factor_to_2024"])

COLS = ["item", "tech", "parameter", "value", "unit", "source_currency_year", "value_2024usd", "cpi_factor",
        "source_id", "page_or_table", "derivation"]
rows = []


def add(item, tech, par, value, unit, year, sid, loc, der):
    f = cpi[year] if year else ""
    v24 = round(value * f, 2) if (year and value != "") else ""
    rows.append(dict(item=item, tech=tech, parameter=par, value=value, unit=unit, source_currency_year=year or "",
                     value_2024usd=v24, cpi_factor=f, source_id=sid, page_or_table=loc, derivation=der))


WAW = "GEN-204"
WAWT = "Table 5.2 Typical Waste Management Costs by Disposal Type, p. 105"
WDER = ("Typical total cost per tonne (no capital/operating split) for {inc} countries, as printed; "
        "currency year taken as the publication year 2018 (the table states none); value_2024usd = value x CPI factor 2018. "
        "Income group (World Bank): CR, DR, ECU, GUA, JAM upper-middle; HON lower-middle.")
for tech, cat, vals in [
    ("BLEND_NO_DCOLL", "Collection and transfer", {"upper-middle": (50, 100), "lower-middle": (30, 75)}),
    ("LANDFILL", "Controlled landfill to sanitary landfill", {"upper-middle": (20, 65), "lower-middle": (15, 40)}),
    ("NO_CONTR_OD", "Open dumping", {"lower-middle": (3, 10)}),
    ("COMPOST", "Composting", {"upper-middle": (20, 75), "lower-middle": (10, 40)}),
]:
    for inc, (lo, hi) in vals.items():
        for par, v in [("total_cost_low", lo), ("total_cost_high", hi)]:
            add("waste_cost", tech, f"{par} ({inc} income)", v, "US$/t", 2018, WAW, f"{WAWT}, row '{cat}'",
                WDER.format(inc=inc))
add("waste_cost", "NO_CONTR_OD", "total_cost (upper-middle income)", "", "US$/t", None, WAW,
    f"{WAWT}, row 'Open dumping'", "Printed as '--' (not available) for upper-middle income countries.")

CEP = "GEN-206"
CEPT = "Cuadro 6 'Paises de America Latina y el Caribe: costo de los servicios por tamano de poblacion', p. 29 (source line: OPS/OMS-AIDIS-BID, 2010)"
CDER = ("LAC regional average cost of the service, column 'Grupo' (all municipality sizes), from the 2010 regional "
        "evaluation reproduced by CEPAL; currency year 2010; value_2024usd = value x CPI factor 2010.")
add("waste_cost", "BLEND_NO_DCOLL", "collection cost (Recoleccion, LAC average)", 34.22, "US$/t", 2010, CEP, CEPT, CDER)
add("waste_cost", "BLEND_NO_DCOLL", "transfer cost (Transferencia, LAC average)", 12.01, "US$/t", 2010, CEP, CEPT, CDER)
add("waste_cost", "LANDFILL", "final disposal cost (Disposicion final, LAC average)", 20.43, "US$/t", 2010, CEP, CEPT, CDER)
add("waste_cost", "BLEND_NO_DCOLL;LANDFILL", "collection, transfer and treatment cost (LAC average)", 67, "US$/t",
    2010, CEP, "Text above Cuadro 6, p. 29: 'casi 67 dolares por tonelada (Martinez Arce et al, 2010)'",
    "Regional average total cost of collection, transfer and treatment; currency year 2010.")

HUT = "GEN-207"
HT = "Appendix E, Table E.1 Capital Costs per Person Served in 2015, Including Hardware and Software (pdf p. 57; Jamaica on pdf p. 58), columns 'Advanced: full excreta management (incremental off-site)', Urban"
HDER = ("Capital cost per person served (2015 USD), incremental off-site cost over basic sanitation. "
        "To convert to the model unit (M US$ per billion m3 per year = US$ per m3 per year): value / annual wastewater per person; "
        "with 150 L per person per day (ASSUMPTION, range 100 to 200) the divisor is 54.75 m3 per person per year. "
        "Row read from the table by column position; the sewerage figure covers conveyance and treatment together.")
for cc, sew, sep in [("DR", 447.2, 115.9), ("ECU", 660.4, 247.2), ("GUA", 384.9, 94.7), ("JAM", 339.9, 88.1)]:
    add("wastewater_cost", "SEWERWW;AERO_PTAR", f"capital per person, urban sewerage with treatment ({cc})", sew,
        "US$/person served", 2015, HUT, HT, HDER)
    add("wastewater_cost", "SEPT_SYST", f"capital per person, urban septic tank with faecal sludge management ({cc})", sep,
        "US$/person served", 2015, HUT, HT, HDER)
    # illustrative conversion
    for tech, v in [("SEWERWW;AERO_PTAR", sew), ("SEPT_SYST", sep)]:
        conv = round(v / 54.75, 3)
        rows.append(dict(item="wastewater_cost", tech=tech,
                         parameter=f"capital per annual volume, converted ({cc})", value=conv,
                         unit="US$ per m3/yr = M US$ per billion m3/yr x 1/1000", source_currency_year=2015,
                         value_2024usd=round(conv * cpi[2015], 3), cpi_factor=cpi[2015], source_id=HUT,
                         page_or_table=HT,
                         derivation=f"{v} US$/person / 54.75 m3/person/yr (150 L/person/day, ASSUMPTION). "
                                    f"In model units: {round(conv*1000,1)} M US$ per billion m3/yr (2015 USD)."))

for pen, techs in [("contam_agua", "NO_CONTR_OD;SIT_CLAN"), ("salud_residuos", "NO_CONTR_OD;OPEN_BURN;SIT_CLAN"),
                   ("turismo_residuos", "NO_CONTR_OD;SIT_CLAN"), ("FERT_ORG", "AD;COMPOST"),
                   ("RM", "INORG_RCY_OS"), ("water_reuse", "AERO_PTAR_RU")]:
    rows.append(dict(item="waste_externality", tech=techs, parameter=pen, value="", unit="US$/t",
                     source_currency_year="", value_2024usd="", cpi_factor="", source_id="",
                     page_or_table="",
                     derivation="No downloaded source gives this value. Origin documents named by the model documentation "
                                "are Inter-American Development Bank publications that refuse scripted and browser downloads "
                                "(bot verification); listed in manual_downloads_GEN_sector.csv."))

with open(os.path.join(GEN, "gen_sector_values.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(len(rows))
