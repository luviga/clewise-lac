"""Write alignment_DR.csv (step C2) from targets_DR.csv and model_levers_DR.csv (read-only inputs).

Model quantities are taken from model_levers_DR.csv (hub step C1, model state 481a7c0).
Run from the job folder: python -I scripts/DR/write_alignment_DR.py
"""
import csv
import os

JOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PJ_TO_GWH = 1e6 / 3600.0  # 1 PJ = 277.78 GWh

lev = list(csv.DictReader(open(os.path.join(JOB, "model_levers_DR.csv"), encoding="utf-8")))
tg = {r["target_id"]: r for r in csv.DictReader(open(os.path.join(JOB, "targets_DR.csv"), encoding="utf-8"))}


def row_no(part, quantity, tech):
    for i, r in enumerate(lev, start=2):
        if r["part"] == part and r["quantity"] == quantity and (r["technology"] == tech or r["fuel"] == tech or r["emission"] == tech):
            return i, r
    raise KeyError((part, quantity, tech))


def v(part, quantity, tech, scen, year):
    _, r = row_no(part, quantity, tech)
    x = r[f"{scen}_{year}"]
    return float(x) if x not in ("", None) else 0.0


def cap(techs, scen, year):
    return sum(v("solved", "installed capacity by plant type", t, scen, year) for t in techs)


def ref_rows(part, quantity, techs):
    return ", ".join(str(row_no(part, quantity, t)[0]) for t in techs)


def fmt(x, nd=4):
    if x is None:
        return ""
    return f"{x:.{nd}f}".rstrip("0").rstrip(".")


def ratio(m, t):
    if m is None or t in (None, 0):
        return ""
    return fmt(m / t, 3)


def status_of(m, t):
    if m is None or t in (None, 0):
        return ""
    r = m / t
    if r < 0:
        return "opposite direction"
    if 0.9 <= r <= 1.1:
        return "matches"
    return "same direction, different size"


H = ["target_id", "source_id", "page", "target_description", "target_value", "target_unit", "target_year", "model_quantity",
     "model_reference", "NDCNEW_value", "LTSNEW_value", "model_unit", "ratio_NDCNEW", "ratio_LTSNEW", "status", "sector_model_folder", "note"]
rows = []


def add_t(tid, mq, mref, n, l, munit, status=None, folder="", note="", tval=None, tunit=None, tyear=None, rn=None, rl=None):
    t = tg[tid]
    tv = float(t["value"]) if (tval is None and t["value"] not in ("",)) else tval
    st = status if status else status_of(n, tv)
    rows.append([tid, t["source_id"], t["page"], t["description"], t["value"] if tval is None else fmt(tval),
                 t["unit"] if tunit is None else tunit, t["target_year"] if tyear is None else tyear, mq, mref,
                 fmt(n) if n is not None else "", fmt(l) if l is not None else "", munit,
                 rn if rn is not None else ratio(n, tv), rl if rl is not None else ratio(l, tv), st, folder, note])


EM = "emissions by label"
SRC_ROW = row_no("solved", EM, "CO2e_sources")[0]
red = {}
for s in ("NDCNEW", "LTSNEW"):
    for y in ("2030", "2035", "2050"):
        b = v("solved", EM, "CO2e_sources", "BAU", y)
        red[(s, y)] = (b - v("solved", EM, "CO2e_sources", s, y), b)

EMNOTE = ("Model covers energy and transport only; label CO2e_sources (fossil fuel combustion counted at the DIST_* technologies, "
          "Mt CO2e assumed from emission factors of about 0.074 per PJ of diesel) is used because it is the energy-wide label and is not "
          "touched by the known unintended EmissionActivityRatio differences of PP technologies. The NDC target is economy-wide against the NDC's own BAU.")
for tid, y in (("DR-T001", "2030"), ("DR-T003", "2035")):
    n = 100 * red[("NDCNEW", y)][0] / red[("NDCNEW", y)][1]
    l = 100 * red[("LTSNEW", y)][0] / red[("LTSNEW", y)][1]
    add_t(tid, f"energy-sector emission reduction against model BAU in {y}",
          f"model_levers_DR.csv row {SRC_ROW} (solved, emissions by label, CO2e_sources): 1 - scenario/BAU", n, l, "percent", note=EMNOTE)

n = 1000 * red[("NDCNEW", "2030")][0]
l = 1000 * red[("LTSNEW", "2030")][0]
add_t("DR-T009", "energy-sector emission reduction against model BAU in 2030",
      f"model_levers_DR.csv row {SRC_ROW} (CO2e_sources), BAU minus scenario, Mt converted to kt", n, l, "kt CO2e",
      note="The NDC figure covers only the new NDC 3.0 energy PAMs; NDC 2.0 measures already achieved (4,734.73 kt economy-wide by 2025, p.43) are outside it. Model BAU is not the NDC BAU.")

RE = ["PPPVD", "PPPVT", "PPWNDON", "PPHDAM", "PPDHYD", "PPBIM", "PPDBGS", "PPDBIM"]
CAPQ = "installed capacity by plant type"
CAPNOTE = "Target base year is 2024; model levers start in 2025, so the model increase is 2025 to 2030. Capacity in GW converted to MW."


def inc(techs, s):
    return 1000 * (cap(techs, s, "2030") - cap(techs, s, "2025"))


add_t("DR-T013", "increase of renewable installed capacity 2025 to 2030 (PV utility and distributed, wind, hydro, biomass, biogas)",
      f"model_levers_DR.csv rows {ref_rows('solved', CAPQ, RE)}", inc(RE, "NDCNEW"), inc(RE, "LTSNEW"), "MW", note=CAPNOTE)
add_t("DR-T014", "increase of solar PV capacity 2025 to 2030 (PPPVT plus PPPVD)",
      f"model_levers_DR.csv rows {ref_rows('solved', CAPQ, ['PPPVT', 'PPPVD'])}", inc(["PPPVT", "PPPVD"], "NDCNEW"), inc(["PPPVT", "PPPVD"], "LTSNEW"), "MW",
      note=CAPNOTE + " The document's 1,267.15 MW includes 170 MW of battery storage.")
add_t("DR-T015", "increase of onshore wind capacity 2025 to 2030 (PPWNDON)",
      f"model_levers_DR.csv row {ref_rows('solved', CAPQ, ['PPWNDON'])}", inc(["PPWNDON"], "NDCNEW"), inc(["PPWNDON"], "LTSNEW"), "MW", note=CAPNOTE)
add_t("DR-T016", "increase of hydro capacity 2025 to 2030 (PPHDAM plus PPDHYD)",
      f"model_levers_DR.csv rows {ref_rows('solved', CAPQ, ['PPHDAM', 'PPDHYD'])}", inc(["PPHDAM", "PPDHYD"], "NDCNEW"), inc(["PPHDAM", "PPDHYD"], "LTSNEW"), "MW", note=CAPNOTE)
NG = ["PPCCTNGS", "PPCCTNGSDSL"]
add_t("DR-T011", "increase of natural gas combined cycle capacity 2025 to 2030 (PPCCTNGS plus new-gas PPCCTNGSDSL)",
      f"model_levers_DR.csv rows {ref_rows('solved', CAPQ, NG)}; B1_Scenario_Config.xlsx sheet Electrical rows 127, 128 (NDCNEW) and 69, 70 (LTSNEW) TotalAnnualMaxCapacity",
      inc(NG, "NDCNEW"), inc(NG, "LTSNEW"), "MW", status="in documents, not in the model",
      note=CAPNOTE + " PPCCTNGSDSL (new natural gas) has no solved capacity in NDCNEW to 2050 and none in LTSNEW before 2050; BAU adds 153 MW of PPCCTNGS by 2030.")

i8, r8 = row_no("input_difference", "InputActivityRatio", "ELE_DIST")
ie, _ = row_no("solved", "final energy delivered per fuel", "ELE")
sav = {}
for s in ("NDCNEW", "LTSNEW"):
    sav[s] = PJ_TO_GWH * 1000 * v("solved", "final energy delivered per fuel", "ELE", s, "2030") * (float(r8["BAU_2030"]) - float(r8[f"{s}_2030"]))
add_t("DR-T018", "distribution losses avoided in 2030: ELE delivered times (BAU minus scenario InputActivityRatio of ELE_DIST)",
      f"model_levers_DR.csv row {i8} (InputActivityRatio ELE_DIST) and row {ie} (final energy delivered ELE)", sav["NDCNEW"], sav["LTSNEW"], "MWh per year",
      note="Assumes all delivered electricity passes ELE_DIST. Model ratio 1.0826 in 2030 against 1.1189 in BAU, then rising to 1.1005 by 2050 (B1_Scenario_Config.xlsx sheet SmartGrid rows 4 and 5).")

add_t("DR-T020", "nuclear plant capacity", "no nuclear plant type among PP technologies in model_levers_DR.csv or RD_ENERGY compiled inputs", None, None, "MW",
      status="in documents, not in the model", rn="", rl="", note="Small modular reactor up to 300 MW by 2035 has no technology in the model.")

ish, _ = row_no("solved", "renewable share of generation", "RENEWABLE/ALL")
for tid, y in (("DR-T062", "2030"), ("DR-T061", "2025"), ("DR-T053", "2025")):
    n = 100 * v("solved", "renewable share of generation", "RENEWABLE/ALL", "NDCNEW", y)
    l = 100 * v("solved", "renewable share of generation", "RENEWABLE/ALL", "LTSNEW", y)
    add_t(tid, f"renewable share of generation in {y}", f"model_levers_DR.csv row {ish} (renewable types PPBIM PPDBGS PPDBIM PPDHYD PPHDAM PPPVD PPPVT PPWNDON)",
          n, l, "percent", note="Model 2025 share is a calibrated history value (both scenarios equal BAU)." if y == "2025" else "")

el, _ = row_no("solved", "electric share of transport group", "E5TRTAX")
add_t("DR-T055", "electric share of taxi group output in 2030 (E5TRTAX)", f"model_levers_DR.csv row {el}; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 130 (NDCNEW) and 168 (LTSNEW)",
      100 * v("solved", "electric share of transport group", "E5TRTAX", "NDCNEW", "2030"), 100 * v("solved", "electric share of transport group", "E5TRTAX", "LTSNEW", "2030"), "percent",
      note="Document share is of the taxi fleet (vehicles), model share is of group output (vehicle-km or passenger-km); read as comparable shares. Superseded NDC 2020 option.")
for tid, grp, cfg in (("DR-T054", "E5TRBPU", "134 and 172"), ("DR-T058", "E5TRAUT", "119 and 157")):
    rr, _ = row_no("solved", "electric share of transport group", grp)
    add_t(tid, f"electric share of {grp} group output in 2030", f"model_levers_DR.csv row {rr}; B1_Scenario_Config.xlsx sheet Tech_Adoption rows {cfg}",
          100 * v("solved", "electric share of transport group", grp, "NDCNEW", "2030"), 100 * v("solved", "electric share of transport group", grp, "LTSNEW", "2030"), "percent",
          status="not compared", rn="", rl="", note="Document counts vehicles; the levers file holds no fleet numbers, so no ratio. Same direction (the model raises the electric share). Superseded NDC 2020 option.")

for tid, mq, mref in (
    ("DR-T025", "bus corridor fleet efficiency", "no corridor or bus efficiency lever; Techs_Buses_Pub limits differ from BAU by under 1.1 percent (model_levers_DR.csv rows 62, 63, 121, 122)"),
    ("DR-T026", "rail mass transit (monorail)", "B1_Scenario_Config.xlsx sheet Mode_Shift rows 14 and 18 (Techs_Trains, value 0); TRANRAILINF TotalAnnualMaxCapacity and TotalAnnualMinCapacity 0 (model_levers_DR.csv rows 55 and 64)"),
    ("DR-T027", "cable car", "B1_Scenario_Config.xlsx sheet Mode_Shift rows 13 and 17 (Techs_Telef, value 0)"),
    ("DR-T028", "sustainable aviation fuel", "no aviation fuel blending technology in RD_ENERGY levers"),
):
    add_t(tid, mq, mref, None, None, "", status="in documents, not in the model", rn="", rl="",
          note="The model holds no positive value for this measure in NDCNEW or LTSNEW.")

# efficiency: public lighting vs model electricity demand cut
ELE_D = ["E5COMELE", "E5INDELE", "E5RESELE"]
cut = {}
for s in ("NDCNEW", "LTSNEW"):
    cut[s] = PJ_TO_GWH * 1000 * sum(v("input_difference", "SpecifiedAnnualDemand", f, "BAU", "2030") - v("input_difference", "SpecifiedAnnualDemand", f, s, "2030") for f in ELE_D)
add_t("DR-T022", "electricity demand cut against BAU in 2030 (commercial, industrial, residential SpecifiedAnnualDemand)",
      f"model_levers_DR.csv rows {ref_rows('input_difference', 'SpecifiedAnnualDemand', ELE_D)}", cut["NDCNEW"], cut["LTSNEW"], "MWh per year",
      note="The model cuts all final demand per fuel by about 2.5 percent in 2030 and 5 percent in 2035 against BAU; the document's only quantified electricity saving outside losses is public lighting and government demand.")

# carbon neutrality
for tid in ("DR-T060", "DR-T045"):
    add_t(tid, "energy-sector emissions in 2050 (CO2e_sources)", f"model_levers_DR.csv row {SRC_ROW}",
          1000 * v("solved", EM, "CO2e_sources", "NDCNEW", "2050"), 1000 * v("solved", EM, "CO2e_sources", "LTSNEW", "2050"), "kt CO2e",
          status="same direction, different size", rn="", rl="",
          note="Target is net zero for the whole economy, so no ratio. LTSNEW cuts energy emissions 87 percent against model BAU (54,157 kt) but keeps 6,893 kt; removals sit outside the energy model.")

# other sectors
for tid, folder, why in (
    ("DR-T029", "DominicanRepublic/RD_IPPU", "technologies REFR_AC_HFC32, REFR_AC_HFC125, REFR_AC_HFC134a, REFR_AC_HFC143a"),
    ("DR-T063", "DominicanRepublic/RD_IPPU", "technologies REFR_AC_HFC*"),
    ("DR-T030", "DominicanRepublic/RD_IPPU", "technologies PROD_CLK_TRAD, PROD_CEM"),
    ("DR-T031", "DominicanRepublic/RD_AFOLU", "technology GA_CARBOV (cattle)"),
    ("DR-T034", "DominicanRepublic/RD_AFOLU", "technology AG_RIC (rice)"),
    ("DR-T035", "DominicanRepublic/RD_AFOLU", "technologies LU_FOR, CAMFOR (forest land, land use change to forest)"),
    ("DR-T064", "DominicanRepublic/RD_AFOLU", "technologies LU_FOR, CAMFOR"),
    ("DR-T040", "DominicanRepublic/RD_WASTE", "technologies CO2_CH4_BURN, LANDFILL"),
    ("DR-T041", "DominicanRepublic/RD_WASTE", "technologies INORG_RCY_OS, COMPOST, ORG_SS"),
    ("DR-T042", "DominicanRepublic/RD_WASTE", "technologies PTAR_NEW, PTAR_OLD, SEWERWW"),
    ("DR-T032", "", "no manure management technology name found in the sector folders"),
    ("DR-T033", "", "no manure management technology name found in the sector folders"),
    ("DR-T037", "", "no mangrove or wetland technology name found in RD_AFOLU"),
):
    add_t(tid, "", f"sector folder technology names (B1_Output_Params/BAU/OutputActivityRatio.csv): {why}", None, None, "", status="not compared",
          folder=folder, rn="", rl="", note="Not a sector of the energy model; sector model not read for values in this job.")

# in the model, not in the documents
def add_m(src, page, desc, mq, mref, n, l, unit, note):
    rows.append(["", src, page, desc, "", "", "", mq, mref, n, l, unit, "", "", "in the model, not in the documents", "", note])


rsh = v("solved", "renewable share of generation", "RENEWABLE/ALL", "NDCNEW", "2035")
add_m("DR-01", "p.40;p.148;p.149", "No renewable share target for 2035 in NDC 3.0 (energy PAMs are capacity additions to 2030)",
      "renewable share of generation 2035", f"model_levers_DR.csv row {ish}; B1_Scenario_Config.xlsx sheet Electrical rows 79 to 107 (NDCNEW) and 21 to 49 (LTSNEW) activity lower limits",
      fmt(100 * rsh), fmt(100 * v("solved", "renewable share of generation", "RENEWABLE/ALL", "LTSNEW", "2035")), "percent",
      "NDCNEW holds 75 percent from 2035 to 2050. The documents' only share targets are 25 percent (2025) and 30 percent (2030).")
add_m("DR-04", "p.111", "No published long-term strategy; only a 2050 carbon neutrality objective",
      "renewable share of generation 2050", f"model_levers_DR.csv row {ish}", fmt(100 * v("solved", "renewable share of generation", "RENEWABLE/ALL", "NDCNEW", "2050")),
      fmt(100 * v("solved", "renewable share of generation", "RENEWABLE/ALL", "LTSNEW", "2050")), "percent",
      "LTSNEW reaches 99 percent renewable generation in 2050; no document states a 2050 power-sector target.")
rr, _ = row_no("solved", "electric share of transport group", "E5TRAUT")
add_m("DR-01", "p.40;p.41", "NDC 3.0 transport PAMs hold no electric vehicle share or number",
      "electric share of transport groups (automobiles shown)", f"model_levers_DR.csv rows 210 to 220; B1_Scenario_Config.xlsx sheet Tech_Adoption rows 119 to 151 (NDCNEW) and 157 to 189 (LTSNEW)",
      fmt(100 * v("solved", "electric share of transport group", "E5TRAUT", "NDCNEW", "2035")), fmt(100 * v("solved", "electric share of transport group", "E5TRAUT", "LTSNEW", "2035")), "percent (2035)",
      "NDCNEW sets 10 percent electric in 2030 and 30 percent from 2040 for every road group; LTSNEW 10, 50 and 90 percent in 2030, 2040, 2050. NDC 2020 vehicle-count options (DR-T054 to DR-T058) are superseded.")
add_m("DR-01", "p.40;p.47", "NDC 3.0 holds no economy-wide final demand reduction target",
      "final demand per fuel against BAU 2035 (residential electricity shown)", "model_levers_DR.csv rows 10 to 30 (SpecifiedAnnualDemand)",
      fmt(100 * (1 - v("input_difference", "SpecifiedAnnualDemand", "E5RESELE", "NDCNEW", "2035") / v("input_difference", "SpecifiedAnnualDemand", "E5RESELE", "BAU", "2035"))),
      fmt(100 * (1 - v("input_difference", "SpecifiedAnnualDemand", "E5RESELE", "LTSNEW", "2035") / v("input_difference", "SpecifiedAnnualDemand", "E5RESELE", "BAU", "2035"))),
      "percent below BAU", "All fuels and sectors cut by the same factor (about 2.5 percent in 2030, 5 percent in 2035; LTSNEW about 10 percent in 2050).")
add_m("DR-04", "p.173", "No coal phase-out date or coal limit in the documents (BTR1 calls the move away from coal essential, without a number)",
      "coal plant generation 2030 (PPCOA)", f"model_levers_DR.csv row {row_no('solved', 'generation by plant type', 'PPCOA')[0]}",
      fmt(v("solved", "generation by plant type", "PPCOA", "NDCNEW", "2030")), fmt(v("solved", "generation by plant type", "PPCOA", "LTSNEW", "2030")), "PJ",
      "BAU 30.38 PJ in 2030; NDCNEW holds coal capacity at 1.12 GW to 2050; LTSNEW coal generation 0.84 PJ in 2050.")

if __name__ == "__main__":
    with open(os.path.join(JOB, "alignment_DR.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(H)
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r[14] for r in rows))
    for r in rows:
        print(r[0], r[4], r[6], r[9], r[10], r[12], r[13], r[14])
