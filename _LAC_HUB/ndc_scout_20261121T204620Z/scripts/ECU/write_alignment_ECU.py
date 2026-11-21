"""Write alignment_ECU.csv: document targets (targets_ECU.csv) against model quantities (model_levers_ECU.csv).

Usage: python -I write_alignment_ECU.py <job_folder>
Model values are computed from model_levers_ECU.csv (rows cited by file row number, header = row 1).
"""
import csv
import os
import sys

import pandas as pd

JOB = sys.argv[1]
L = pd.read_csv(os.path.join(JOB, "model_levers_ECU.csv"))
L.index = L.index + 2  # file row numbers
TG = {r["target_id"]: r for r in csv.DictReader(open(os.path.join(JOB, "targets_ECU.csv"), encoding="utf-8"))}


def row(q, t):
    r = L[(L.quantity == q) & (L.technology == t)]
    assert len(r) == 1, (q, t, len(r))
    return r.index[0]


def val(q, t, s, y):
    v = L.loc[row(q, t), f"{s}_{y}"]
    return 0.0 if pd.isna(v) else float(v)


def rows_of(q, techs):
    return " ".join(str(row(q, t)) for t in techs)


GEN, CAP = "generation by plant type", "installed capacity by plant type"
HYDRO = ["PPHD", "PPHDAMAB", "PPHDAMAM", "PPHDAMAS", "PPHDAMPM", "PPHDAMPS", "PPHRORAB", "PPHRORAM", "PPHRORAS",
         "PPHRORPM", "PPHRORPS", "PPIHD"]
ERNC = ["PPPVD", "PPPVT", "PPPVTS", "PPWNDD", "PPWNDON", "PPBGS", "PPBIM"]
PVW = ["PPPVD", "PPPVT", "PPPVTS", "PPWNDD", "PPWNDON"]
CAP_HYDRO = HYDRO
CAP_PVW = ["PPPVD", "PPPVT", "PPPVTS", "PPWNDD", "PPWNDON"]
EML = ["CO2e_DE", "CO2e_FUG", "CO2e_REF", "CO2_PP"]


def share(techs, s, y):
    tot = val("generation total (all PP/PWR)", "ALL", s, y)
    return 100 * sum(val(GEN, t, s, y) for t in techs) / tot


def capsum(techs, s, y):
    return 1000 * sum(val(CAP, t, s, y) for t in techs if row_exists(CAP, t))


def row_exists(q, t):
    return len(L[(L.quantity == q) & (L.technology == t)]) == 1


def energy_em(s, y):  # Mt CO2e -> kt
    return 1000 * sum(val("emissions by label", l, s, y) for l in EML)


def demand(fuels, s, y):
    return sum(val("SpecifiedAnnualDemand", "", s, y) for _ in [])  # placeholder (not used)


def dem(fuel, s, y):
    r = L[(L.quantity == "SpecifiedAnnualDemand") & (L.fuel == fuel)]
    v = r[f"{s}_{y}"].iloc[0]
    return float(v)


def dem_row(fuel):
    return L[(L.quantity == "SpecifiedAnnualDemand") & (L.fuel == fuel)].index[0]


NONTRO = [f for f in L[L.quantity == "SpecifiedAnnualDemand"].fuel if not str(f).startswith("E5TRO")]
TRO = ["E5TRODSL", "E5TROELE", "E5TROGSL"]
RES = ["E5RESELE", "E5RESFIR", "E5RESLPG", "E5RESNGS"]
IND = [f for f in NONTRO if str(f).startswith("E5IND")]

out = []


def add(tid, quantity, ref, nv, lv, unit, status, folder="", note="", tv=None):
    t = TG[tid]
    tval = float(t["value"]) if (tv is None and t["value"] not in ("",)) else tv

    def ratio(m):
        if m is None or m == "" or tval in (None, "", 0):
            return ""
        return round(m / tval, 3)

    out.append({"target_id": tid, "source_id": t["source_id"], "page": t["page"],
                "target_description": t["description"], "target_value": t["value"], "target_unit": t["unit"],
                "target_year": t["target_year"], "model_quantity": quantity, "model_reference": ref,
                "NDCNEW_value": "" if nv is None else round(nv, 4), "LTSNEW_value": "" if lv is None else round(lv, 4),
                "model_unit": unit, "ratio_NDCNEW": ratio(nv) if status != "not compared" else "",
                "ratio_LTSNEW": ratio(lv) if status != "not compared" else "", "status": status,
                "sector_model_folder": folder, "note": note})


EMREF = "model_levers_ECU.csv rows " + " ".join(str(row("emissions by label", l)) for l in EML) + " (CO2e_DE + CO2e_FUG + CO2e_REF + CO2_PP)"
EMNOTE = ("Energy-sector total built from the labels CO2e_DE (demand), CO2e_FUG (fugitive), CO2e_REF (refinery) and CO2_PP "
          "(power plants, CO2 only). CO2_PP is used instead of CO2e_PP because CO2e_PP carries the known unintended "
          "EmissionActivityRatio differences of PPNGS, PPRNGS, PPDSL, PPRDSL, PPCRU and PPFOI from 2025; CO2_PP is equal "
          "across scenarios. Unit Mt CO2e assumed (diesel road factor 0.0741 per PJ), converted to kt. CO2e_sources is not "
          "used: it counts fuel at the DIST_* technologies and overlaps the other labels.")

# ---- economy-wide targets against the model's own BAU (energy only)
for tid, tv in (("ECU-T001", None),):
    red = {s: 100 * (1 - energy_em(s, 2035) / energy_em("BAU", 2035)) for s in ("NDCNEW", "LTSNEW")}
    add(tid, "energy-sector emission reduction against model BAU in 2035", EMREF, red["NDCNEW"], red["LTSNEW"],
        "percent", "same direction, different size", "",
        "Model covers energy and transport only; the NDC target is economy-wide against the NDC trend scenario (2010 base). "
        f"Model BAU 2035 {energy_em('BAU', 2035):.0f} kt. " + EMNOTE)
red = {s: 100 * (1 - energy_em(s, 2035) / energy_em("BAU", 2035)) for s in ("NDCNEW", "LTSNEW")}
add("ECU-T003", "energy-sector emission reduction against model BAU in 2035, compared with the total conditional reduction (7 plus 8 percent)",
    EMREF, red["NDCNEW"], red["LTSNEW"], "percent", "same direction, different size", "",
    "Target value used for the ratio is 15 percent (7 percent unconditional plus 8 percent additional), our reading of p.55 and p.56.",
    tv=15.0)
add("ECU-T002", "energy-sector emission reduction against model BAU in 2035", EMREF,
    energy_em("BAU", 2035) - energy_em("NDCNEW", 2035), energy_em("BAU", 2035) - energy_em("LTSNEW", 2035), "kt CO2e",
    "same direction, different size", "",
    "The NDC 8,800 kt covers all five sectors including LULUCF. " + EMNOTE)
# ---- PLANMICC energy-sector levels
for tid, y in (("ECU-T020", 2035), ("ECU-T021", 2050)):
    add(tid, f"energy-sector emissions (including transport) in {y}", EMREF, energy_em("NDCNEW", y), energy_em("LTSNEW", y),
        "kt CO2e", "same direction, different size", "",
        f"Model BAU {y}: {energy_em('BAU', y):.0f} kt. PLANMICC 2018 base 38,400 Gg; model 2025 BAU {energy_em('BAU', 2025):.0f} kt. " + EMNOTE)
# ---- renewable shares
add("ECU-T025", "non-conventional renewable share of generation in 2035 (solar PV, wind, biogas, biomass plants)",
    "model_levers_ECU.csv rows " + rows_of(GEN, ERNC) + " over row " + str(row("generation total (all PP/PWR)", "ALL")),
    share(ERNC, "NDCNEW", 2035), share(ERNC, "LTSNEW", 2035), "percent", "same direction, different size", "",
    "Model counts all generation (no separate SNI). Solar and wind alone: NDCNEW %.2f percent. PPPVTS has no 2025 value." % share(PVW, "NDCNEW", 2035))
add("ECU-T026", "hydro share of generation in 2035",
    "model_levers_ECU.csv rows " + rows_of(GEN, HYDRO), share(HYDRO, "NDCNEW", 2035), share(HYDRO, "LTSNEW", 2035),
    "percent", "matches", "", "Hydro plant types PPHD, PPHDAM*, PPHROR*, PPIHD.")
add("ECU-T027", "installed hydro capacity in 2035", "model_levers_ECU.csv rows " + rows_of(CAP, CAP_HYDRO),
    capsum(CAP_HYDRO, "NDCNEW", 2035), capsum(CAP_HYDRO, "LTSNEW", 2035), "MW", "same direction, different size", "",
    "Model hydro capacity grows from %.0f MW (2025) only; GW converted to MW." % capsum(CAP_HYDRO, "NDCNEW", 2025))
add("ECU-T028", "non-conventional renewable share of generation in 2050 (solar PV, wind, biogas, biomass plants)",
    "model_levers_ECU.csv rows " + rows_of(GEN, ERNC), share(ERNC, "NDCNEW", 2050), share(ERNC, "LTSNEW", 2050),
    "percent", "same direction, different size", "", "LTSNEW is the long-term scenario; NDCNEW holds 2035 measures.")
add("ECU-T029", "installed solar PV and wind capacity in 2050", "model_levers_ECU.csv rows " + rows_of(CAP, CAP_PVW),
    capsum(CAP_PVW, "NDCNEW", 2050), capsum(CAP_PVW, "LTSNEW", 2050), "MW", "same direction, different size", "",
    "Biogas and biomass plants excluded (128.5 and 86.6 MW in every scenario). GW converted to MW.")
add("ECU-T030", "hydro share of generation in 2050", "model_levers_ECU.csv rows " + rows_of(GEN, HYDRO),
    share(HYDRO, "NDCNEW", 2050), share(HYDRO, "LTSNEW", 2050), "percent", "same direction, different size", "",
    "LTSNEW renewable share 2050 is 99.0 percent (row %d) against about 89 percent implied by the PLANMICC phase II shares." % row("renewable share of generation", "RENEWABLE/ALL"))
add("ECU-T032", "non-renewable share of generation in 2050",
    "model_levers_ECU.csv row " + str(row("renewable share of generation", "RENEWABLE/ALL")),
    100 * (1 - val("renewable share of generation", "RENEWABLE/ALL", "NDCNEW", 2050)),
    100 * (1 - val("renewable share of generation", "RENEWABLE/ALL", "LTSNEW", 2050)), "percent", "opposite direction", "",
    "No number in the document; it keeps thermal generation for security of supply. LTSNEW nearly phases it out (1 percent in 2050). Ratios not computed.",
    tv=0)
# ---- PME expansion 2023-2032 against model increase 2025 to 2035
inc_h = {s: capsum(CAP_HYDRO, s, 2035) - capsum(CAP_HYDRO, s, 2025) for s in ("NDCNEW", "LTSNEW")}
inc_r = {s: capsum(CAP_PVW, s, 2035) - capsum(CAP_PVW, s, 2025) for s in ("NDCNEW", "LTSNEW")}
add("ECU-T069", "increase of hydro capacity 2025 to 2035", "model_levers_ECU.csv rows " + rows_of(CAP, CAP_HYDRO),
    inc_h["NDCNEW"], inc_h["LTSNEW"], "MW", "same direction, different size", "",
    "Plan additions are 2023 to 2032; model levers start in 2025 and the nearest printed year after 2032 is 2035. Model BAU adds %.0f MW." % (capsum(CAP_HYDRO, "BAU", 2035) - capsum(CAP_HYDRO, "BAU", 2025)))
add("ECU-T070", "increase of solar PV and wind capacity 2025 to 2035", "model_levers_ECU.csv rows " + rows_of(CAP, CAP_PVW),
    inc_r["NDCNEW"], inc_r["LTSNEW"], "MW", "same direction, different size", "",
    "Plan additions 2023 to 2032 (hydro excluded); model 2025 to 2035.")
# ---- efficiency and transport
def nontro(s, y):
    return sum(dem(f, s, y) for f in NONTRO)


eff = {s: 100 * (1 - nontro(s, 2035) / nontro("BAU", 2035)) for s in ("NDCNEW", "LTSNEW")}
add("ECU-T034", "reduction of non-transport final demand against model BAU in 2035 (all SpecifiedAnnualDemand fuels except E5TRO*)",
    "model_levers_ECU.csv rows %d to %d" % (min(dem_row(f) for f in NONTRO), max(dem_row(f) for f in NONTRO)),
    eff["NDCNEW"], eff["LTSNEW"], "percent", "matches" if abs(eff["NDCNEW"] / 8.4 - 1) <= 0.1 else "same direction, different size", "",
    "Model BAU is not the PLANMICC trend scenario. The model scales every fuel down; it does not switch fuels.")
tro = {s: 100 * (1 - sum(dem(f, s, 2035) for f in TRO) / sum(dem(f, "BAU", 2035) for f in TRO)) for s in ("NDCNEW", "LTSNEW")}
add("ECU-T039", "reduction of road transport energy demand (E5TRODSL, E5TROGSL, E5TROELE) against model BAU in 2035",
    "model_levers_ECU.csv rows " + " ".join(str(dem_row(f)) for f in TRO), tro["NDCNEW"], tro["LTSNEW"], "percent",
    "same direction, different size", "",
    "Gasoline demand falls from %.1f to %.1f PJ in NDCNEW 2035. Model transport is fuel-based (E5TRO*), road only." % (dem("E5TROGSL", "BAU", 2035), dem("E5TROGSL", "NDCNEW", 2035)))
res = {s: 100 * dem("E5RESELE", s, 2050) / sum(dem(f, s, 2050) for f in RES) for s in ("BAU", "NDCNEW", "LTSNEW")}
add("ECU-T035", "electricity share of residential final demand in 2050",
    "model_levers_ECU.csv rows " + " ".join(str(dem_row(f)) for f in RES), res["NDCNEW"], res["LTSNEW"], "percent",
    "in documents, not in the model", "",
    "Same share as BAU (%.1f percent): the policy scenarios scale each residential fuel down and do not replace LPG by electricity." % res["BAU"])
ind = {s: 100 * dem("E5INDELE", s, 2050) / sum(dem(f, s, 2050) for f in IND) for s in ("BAU", "NDCNEW", "LTSNEW")}
add("ECU-T036", "electricity share of industrial final demand in 2050",
    "model_levers_ECU.csv rows " + " ".join(str(dem_row(f)) for f in IND), ind["NDCNEW"], ind["LTSNEW"], "percent",
    "in documents, not in the model", "", "Same share as BAU (%.1f percent): no fuel switching in industry." % ind["BAU"])
# electricity share of final energy: ELE over all delivered fuels except crude (CRU) and other petroleum energy (OPE)
FIN = [t for t in L[L.quantity == "final energy delivered per fuel"].technology if t not in ("CRU", "OPE")]
fe = {s: 100 * val("final energy delivered per fuel", "ELE", s, 2050) / sum(val("final energy delivered per fuel", t, s, 2050) for t in FIN) for s in ("BAU", "NDCNEW", "LTSNEW")}
add("ECU-T024", "electricity share of fuels delivered in 2050 (all E4/E5 deliveries except crude and OPE)",
    "model_levers_ECU.csv rows " + rows_of("final energy delivered per fuel", FIN), fe["NDCNEW"], fe["LTSNEW"], "percent",
    "same direction, different size", "",
    "Indicative only: the delivered-fuel rows include fuel to power plants and exports, so they are not final consumption. BAU %.1f percent." % fe["BAU"])
eshare_row = row("electric share of transport group (fuel-based)", "E5TRO*")
for tid, q in (("ECU-T040", "passenger-km by public transport"), ("ECU-T041", "hybrid vehicle share"),
               ("ECU-T042", "electric light freight vehicle share")):
    add(tid, q, "no vehicle, passenger-km or freight split in ECU_Energy (road transport is fuel-based, E5TRO*)", None, None,
        "", "in documents, not in the model", "",
        "Closest model quantity: electric share of road transport energy (row %d), NDCNEW 2050 %.3f, LTSNEW 2050 %.3f." % (
            eshare_row, val("electric share of transport group (fuel-based)", "E5TRO*", "NDCNEW", 2050),
            val("electric share of transport group (fuel-based)", "E5TRO*", "LTSNEW", 2050)))
add("ECU-T043", "hydrogen share of freight fleet", "", None, None, "", "not compared", "",
    "Target year 2070 is beyond the model horizon (2050).")
add("ECU-T074", "ethanol share in gasoline", "no blending technology or ethanol fuel among the model levers", None, None, "",
    "in documents, not in the model", "", "Also the first NDC ethanol initiative (ECU-T064).")
add("ECU-T075", "electricity distribution losses (1 minus 1 over the ELE_DIST InputActivityRatio)",
    "B1_Output_Params/NDCNEW and LTSNEW InputActivityRatio.csv, ELE_DIST E2ELE 2035 = 1.1393 (equal to BAU)",
    100 * (1 - 1 / 1.1393), 100 * (1 - 1 / 1.1393), "percent", "in documents, not in the model", "",
    "Losses are constant and equal to BAU; no grid-loss lever differs (model_levers_ECU.csv has no grid losses rows). Transmission ELE_TRANS 1.0398 in addition.")
add("ECU-T076", "hydrogen production or demand", "E5INDHYD demand is 0 (B1_Scenario_Config.xlsx Efficiency rows 21 and 76); HYD_G_PROD exists",
    None, None, "", "in documents, not in the model", "", "The PLANMICC uses hydrogen only after 2050 (ECU-03 p.100).")
# ---- other sectors
for tid, folder, techs in (("ECU-T044", "Ecuador/ECU_AGR", "livestock GA_BOV*"), ("ECU-T045", "Ecuador/ECU_AGR", "livestock GA_BOV*"),
                           ("ECU-T047", "Ecuador/ECU_USCUSS", "land use LU_FOR, LU_PLA"), ("ECU-T049", "Ecuador/ECU_USCUSS", "land use LU_N*"),
                           ("ECU-T051", "Ecuador/ECU_USCUSS", "plantations LU_PLA"), ("ECU-T052", "Ecuador/ECU_IPPU", "PROD_CLK_TRAD, PROD_CEM"),
                           ("ECU-T053", "Ecuador/ECU_IPPU", "clinker PROD_CLK_TRAD"), ("ECU-T055", "Ecuador/ECU_IPPU", "IMP_HFC*"),
                           ("ECU-T056", "Ecuador/ECU_WASTE", "LANDFILL, NO_CONTR_OD, DWW_*"), ("ECU-T057", "Ecuador/ECU_WASTE", "open dump NO_CONTR_OD"),
                           ("ECU-T060", "Ecuador/ECU_WASTE", "wastewater DWW_DC, DWW_N, IWW")):
    add(tid, "sector model quantity", "technology names in " + folder + " (" + techs + ")", None, None, "", "not compared", folder,
        "Sector model not read for values (task scope: energy model).")
# ---- levers without document support
add("ECU-T001", "NDCNEW renewable share of generation 80 percent from 2035 (target shares)",
    "model_levers_ECU.csv row %d; ShareValidation control share 0.800" % row("renewable share of generation", "RENEWABLE/ALL"),
    100 * val("renewable share of generation", "RENEWABLE/ALL", "NDCNEW", 2035), 100 * val("renewable share of generation", "RENEWABLE/ALL", "LTSNEW", 2035),
    "percent", "in the model, not in the documents", "",
    "The NDC states no generation share; the PLANMICC phase I shares (ECU-T025, ECU-T026) sum to about 88 percent. Ratios not computed.", tv=0)
add("ECU-T001", "electric share of road transport energy (E5TRO*): NDCNEW 2035 and LTSNEW 2050",
    "model_levers_ECU.csv row %d; demand rows %d (E5TROELE)" % (eshare_row, dem_row("E5TROELE")),
    100 * val("electric share of transport group (fuel-based)", "E5TRO*", "NDCNEW", 2035),
    100 * val("electric share of transport group (fuel-based)", "E5TRO*", "LTSNEW", 2050), "percent",
    "in the model, not in the documents", "",
    "NDCNEW value is 2035, LTSNEW value is 2050 (34 percent). The documents give vehicle shares for 2050 (ECU-T041, ECU-T042), not an energy share; nothing for 2035. Ratios not computed.", tv=0)
add("ECU-T001", "EmissionActivityRatio of PROCRU (refinery) for CO2_REF and CO2e_REF from 2025: BAU 0.0038 and 0.0036, policy 0.0043 and 0.0039",
    "model_levers_ECU.csv rows 8 and 9", None, None, "", "in the model, not in the documents", "",
    "Not in the brief's list of known unintended differences; raises refinery emissions in the policy scenarios (CO2e_REF NDCNEW 2035 1.344 against BAU 1.245 Mt). Ratios not computed.", tv=0)
add("ECU-T001", "EmissionActivityRatio of PPNGS, PPRNGS, PPDSL, PPRDSL, PPCRU, PPFOI (CO2e_PP) from 2025",
    "model_levers_ECU.csv rows 2 to 7", None, None, "", "in the model, not in the documents", "",
    "Known unintended difference (brief section 3), not a policy measure. Ratios not computed.", tv=0)

COLS = ["target_id", "source_id", "page", "target_description", "target_value", "target_unit", "target_year",
        "model_quantity", "model_reference", "NDCNEW_value", "LTSNEW_value", "model_unit", "ratio_NDCNEW", "ratio_LTSNEW",
        "status", "sector_model_folder", "note"]
for r in out:
    if r["status"] == "in the model, not in the documents" or r["target_id"] == "ECU-T032":
        r["ratio_NDCNEW"] = r["ratio_LTSNEW"] = ""
    if r["status"] == "in the model, not in the documents":
        r.update({"target_id": "", "source_id": "ECU-01", "page": "p.56",
                  "target_description": "no matching document target (the second NDC states only the economy-wide target, section 4.4.1)",
                  "target_value": "", "target_unit": "", "target_year": ""})
with open(os.path.join(JOB, "alignment_ECU.csv"), "w", encoding="utf-8", newline="\n") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(out)
from collections import Counter
print(len(out), Counter(r["status"] for r in out))
for r in out:
    print(r["target_id"], r["model_quantity"][:60], r["NDCNEW_value"], r["LTSNEW_value"], r["ratio_NDCNEW"], r["ratio_LTSNEW"], r["status"])
