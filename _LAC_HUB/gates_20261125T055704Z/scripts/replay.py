"""Step 6: put back, on copies of the compiled data files in the temporary folder (gates_tmp of machine.json), each defect of the brief that
main no longer carries (values from LAC_ALIGN's registers and write logs), run the suite on the copy and record
whether the expected check flags it. Writes replay_check.csv in the job folder.
Usage: py -I replay.py [case ...]"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import re
import shutil
import sys
from pathlib import Path

ROOT, JOB = M.ROOT, M.JOB
TMP = M.GATES_TMP
PRISTINE = TMP / "pristine_b1"
REPLAY = TMP / "replay"
ALIGN = ROOT / "_LAC_HUB" / "align_20261124T021708Z"
sys.path.insert(0, str(ROOT))
_Mos.chdir(ROOT)
import scenario_rules as SR  # noqa: E402
import lac_tables as LT  # noqa: E402
from gates import run as GR  # noqa: E402

MODEL = {r["model"]: r for r in csv.DictReader(open(ROOT / "config" / "gates" / "models.csv", encoding="utf-8"))}


def src_file(model, scen, point):
    path = MODEL[model]["path"]
    if point == "b1":
        return PRISTINE / path / "Executables" / f"{scen}_0" / f"{scen}_0.txt"
    return ROOT / path / "Executables" / f"{scen}_FINAL_0" / f"{scen}_FINAL_0.txt"


def case_file(case, model, scen, point):
    path = MODEL[model]["path"]
    sub = f"{scen}_0" if point == "b1" else f"{scen}_FINAL_0"
    return REPLAY / case / path / "Executables" / sub / f"{sub}.txt"


def load(case, model, scen, point):
    dst = case_file(case, model, scen, point)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file(model, scen, point), dst)
    with open(dst, encoding="utf-8", errors="replace", newline="") as fh:
        content = fh.read()
    return dst, content.replace("\r\n", "\n")


def save(dst, content):
    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)


def set_rows(content, param, rows):
    yrs = SR.years_of(content)
    content, n = SR.set_rows(content, param, rows, yrs, SR.region_of(content))
    return content, n


def exact_values(text, years):
    vals = [float(x) for x in str(text).split(";") if x.strip()]
    ys = [int(y) for y in years]
    return dict(zip(ys[-len(vals):], vals)) if len(vals) <= len(ys) else {}


def run_suite(case, model, scen, point):
    out = REPLAY / case / "out"
    GR.main(["--point", point, "--models", model, "--scenarios", scen, "--data-dir", str(REPLAY / case),
             "--b1-data-dir", str(PRISTINE), "--out", str(out), "--jobs", "1"])
    return list(csv.DictReader(open(out / "gate_results.csv", encoding="utf-8")))


def first(rows, check, **match):
    for r in rows:
        if r["check"] != check or r["class"] not in ("FAIL",):
            continue
        if all(v in r.get(k, "") for k, v in match.items()):
            return r
    return None


def line(r):
    return ",".join(r[k] for k in ("check", "class", "model", "scenario", "point", "parameter", "technology", "fuel",
                                   "emission", "year", "timeslice", "values", "message")) if r else ""


RESULTS = []


def record(defect, model, scen, how, expected, rows, **match):
    hit = None
    for chk in expected.split("|"):
        hit = first(rows, chk, **match)
        if hit:
            break
    RESULTS.append(dict(defect=defect, model=model, scenario=scen, how_put_back=how, expected_check=expected,
                        flagged="yes" if hit else "no", gate_results_line=line(hit)))
    print(defect, "->", "FLAGGED" if hit else "NOT FLAGGED", line(hit)[:200], flush=True)


# ------------------------------------------------------------------------------------------------ cases
def dr_ppicefoi():
    case, model, scen, point = "dr_ppicefoi", "RD_ENERGY", "BAU", "b1"
    dst, c = load(case, model, scen, point)
    c, n = set_rows(c, "TotalAnnualMaxCapacity", {"PPICEFOI": {2023: 0.583419, 2024: 0.472}})
    save(dst, c)
    record("Dominican PPICEFOI BAU maximum capacity below its history generation lower limit", model, scen,
           f"TotalAnnualMaxCapacity PPICEFOI 2023 0.583419 and 2024 0.472 written into the compiled BAU file ({n} cells)",
           "B8|B5|P1", run_suite(case, model, scen, point), technology="PPICEFOI")


def ecu_maxcap():
    case, model, scen, point = "ecu_maxcap", "ECU_Energy", "BAU", "b1"
    dst, c = load(case, model, scen, point)
    rows = {}
    for r in csv.DictReader(open(ALIGN / "work" / "register_history_fix3.csv", encoding="utf-8")):
        if r["parameter"] == "TotalAnnualMaxCapacity":
            rows.setdefault(r["tech"], {})[int(float(r["year"]))] = float(r["before"])
    c, n = set_rows(c, "TotalAnnualMaxCapacity", rows)
    save(dst, c)
    record("Ecuador maximum capacity 0.1 MW below residual capacity plus committed builds", model, scen,
           f"register_history_fix3.csv before values of {', '.join(sorted(rows))} ({n} cells)", "B6|B5|B8|P1",
           run_suite(case, model, scen, point))


def ecu_pphdamps_dup():
    case, model, scen, point = "ecu_pphdamps_dup", "ECU_Energy", "NDC", "b1"
    dst, c = load(case, model, scen, point)
    start = c.find("param TotalAnnualMaxCapacity")
    end = c.find(";", start)
    block = c[start:end]
    m = re.search(r"\nPPHDAMPS [^\n]*", block)
    if m is None:
        rows = {"PPHDAMPS": {int(y): 9999.0 for y in SR.years_of(c)}}
        c, _ = set_rows(c, "TotalAnnualMaxCapacity", rows)
        start = c.find("param TotalAnnualMaxCapacity")
        end = c.find(";", start)
        block = c[start:end]
        m = re.search(r"\nPPHDAMPS [^\n]*", block)
    dup = m.group(0)
    c = c[:start] + block + dup + "\n" + c[end:]
    save(dst, c)
    record("Ecuador NDC PPHDAMPS second maximum capacity row", model, scen,
           "the PPHDAMPS row of TotalAnnualMaxCapacity written twice in the compiled NDC file", "S5",
           run_suite(case, model, scen, point), parameter="TotalAnnualMaxCapacity")


def cr_policy_history():
    case, model, scen, point = "cr_policy_history", "CR_ENERGY", "NDC", "b1"
    dst, c = load(case, model, scen, point)
    yrs = SR.years_of(c)
    per = {}
    for r in csv.DictReader(open(ALIGN / "work" / "register_policy_history_cr.csv", encoding="utf-8")):
        sc, tech = r["tech"].split("|")
        if sc != scen:
            continue
        vals = exact_values(r["before"], yrs)
        if vals:
            per.setdefault(r["parameter"], {})[tech] = vals
    n = 0
    for p, rows in per.items():
        c, k = set_rows(c, p, rows)
        n += k
    save(dst, c)
    record("Costa Rica policy plant limits below history capacity", model, scen,
           f"register_policy_history_cr.csv before values ({n} cells of {', '.join(sorted(per))})", "B8|B5|B3|P1",
           run_suite(case, model, scen, point))


def dr_policy_history():
    case, model, scen, point = "dr_policy_history", "RD_ENERGY", "LTS", "b1"
    dst, c = load(case, model, scen, point)
    yrs = SR.years_of(c)
    per = {}
    for f in sorted((ALIGN / "work").glob("register_policy_history_dr*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if "|" not in r["tech"]:
                continue
            sc, tech = r["tech"].split("|", 1)
            if sc != scen:
                continue
            vals = exact_values(r["before"], yrs)
            if vals:
                per.setdefault(r["parameter"], {})[tech] = vals
    n = 0
    for p, rows in per.items():
        c, k = set_rows(c, p, rows)
        n += k
    save(dst, c)
    record("Dominican policy plant limits below history capacity", model, scen,
           f"register_policy_history_dr1-4.csv before values ({n} cells of {', '.join(sorted(per))})", "B8|B5|B3|P1",
           run_suite(case, model, scen, point))


def gua_hydrogen():
    case, model, scen, point = "gua_hydrogen", "GUA_ENERGY", "NDC", "final"
    dst, c = load(case, model, scen, point)
    lo = {"TRYTKHYD": 0.0101, "TRBPUHYD": 0.0032, "TRBPRHYD": 0.0027}
    yrs = [y for y in SR.years_of(c) if 2040 <= y <= 2050]
    c, n1 = set_rows(c, "TotalTechnologyAnnualActivityLowerLimit", {t: {y: v for y in yrs} for t, v in lo.items()})
    c, n2 = set_rows(c, "TotalTechnologyAnnualActivityUpperLimit", {t: {y: 99999.0 for y in yrs} for t in lo})
    c, n3 = set_rows(c, "TotalAnnualMaxCapacity", {t: {y: 99999.0 for y in yrs} for t in lo})
    save(dst, c)
    record("Guatemala forced hydrogen vehicles with no hydrogen supply", model, scen,
           "lower limits TRYTKHYD 0.0101, TRBPUHYD 0.0032, TRBPRHYD 0.0027 PJ in 2040-2050 put back in the NDC FINAL "
           f"file with the vehicles' own limits open; the supply chain keeps the hydrogen rule's limits ({n1 + n2 + n3} cells)",
           "S4|P1|S2", run_suite(case, model, scen, point))


def ecu_share_135():
    case, model, scen, point = "ecu_share_135", "ECU_Energy", "NDC", "final"
    dst, c = load(case, model, scen, point)
    # REMinProductionTarget is a one-index block: write the year with the value 1.35 as a plain record
    start = c.find("param REMinProductionTarget")
    hdr_end = c.find(":=", start) + 2
    region = SR.region_of(c)
    c = c[:hdr_end] + f"\n{region} 2032 1.35" + c[hdr_end:]
    save(dst, c)
    rows = run_suite(case, model, scen, point)
    rt = REPLAY / case / "_STAGE1_OUTPUT"
    rt.mkdir(parents=True, exist_ok=True)
    src = ROOT / "_STAGE1_OUTPUT" / "RENEWABLE_TARGETS.csv"
    lines = open(src, encoding="utf-8").read().splitlines()
    lines.append("Ecuador,NDC,2032,1.35,capacity rule,ECU-T069|ECU-T070,share computed from the capacity target before the cap at 1.0")
    (rt / "RENEWABLE_TARGETS.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    from gates.standard import renewable_rule_outputs
    from gates import config as C
    extra = list(renewable_rule_outputs(REPLAY / case, dict(point="final", thr=C.thresholds(ROOT), root=ROOT)))
    record("Ecuador capacity-based target computing a share of 1.35", model, scen,
           "REMinProductionTarget 1.35 in 2032 in the NDC FINAL file, and a RENEWABLE_TARGETS.csv copy with the 1.35 row",
           "R3", rows + extra, year="2032")


def hon_cap(case, minimum_only):
    model, scen, point = "HON_ENERGY", "LTS", "final"
    dst, c = load(case, model, scen, point)
    res = {(r["scenario"], int(r["year"])): r for r in csv.DictReader(open(ALIGN / "results_summary.csv", encoding="utf-8"))
           if r["country"] == "Honduras"}
    y_from, y_start, y_to = (LT.controller(k, "3") for k in ("cap_from_year", "cap_start_year", "cap_target_year"))
    e1 = float(res[("NDC", y_from)]["energy_emissions_kt"]) / 1000.0
    e2 = float(res[("BAU", y_to)]["energy_emissions_kt"]) / 1000.0 * 0.53
    labels = LT.emissions("energy_cap", "Honduras")
    caps = {e: {y: round(e1 + (e2 - e1) * (y - y_from) / (y_to - y_from), 6) for y in range(y_start, y_to + 1)}
            for e in labels}
    c, n = set_rows(c, "AnnualEmissionLimit", caps)
    how = (f"cap at r 0.47 written into the LTS FINAL file: straight line from the solved NDC {y_from} level "
           f"{e1:.4f} Mt to 0.53 x solved BAU {y_to} {e2 / 0.53:.4f} Mt = {e2:.4f} Mt, {y_start}-{y_to} ({n} cells)")
    if minimum_only:
        vehicles = ["TRAUTELE", "TRTAXELE", "TRMOTELE", "TRSUVELE", "TRBPUELE", "TRBTURELE", "TRMBSELE", "TRYTKELE",
                    "TRYLFELE"]
        yrs = SR.years_of(c)
        c, k = set_rows(c, "TotalAnnualMaxCapacity", {t: {y: 99999.0 for y in yrs if y > 2024} for t in vehicles})
        how += (f"; every published vehicle share kept as a minimum only (the maximum capacity rows the Min/Max "
                f"restriction writes for the nine classes opened from 2025, {k} cells; their lower limits stay)")
    save(dst, c)
    rows = run_suite(case, model, scen, point)
    if minimum_only:
        hit = first(rows, "P2")
        RESULTS.append(dict(defect="Honduras LTS cap at r 0.47 with vehicle shares as minimum only (control case)",
                            model=model, scenario=scen, how_put_back=how, expected_check="P2 not flagged",
                            flagged="yes" if hit else "no", gate_results_line=line(hit)))
        print("hon min only ->", "P2 FLAGGED" if hit else "not flagged (expected)", flush=True)
    else:
        record("Honduras LTS infeasible at r 0.47 with the vehicle ceilings", model, scen, how, "P2|P1", rows)


def jam_transport_rename():
    """The JAM_TRANSPORT case: two scenarios that read one input folder. A copy where the NDC data file is absent
    (the runner wrote one folder for two names)."""
    case, model, point = "jam_transport_rename", "JAM_TRANSPORT", "b1"
    d = REPLAY / case / MODEL[model]["path"] / "Executables"
    if d.exists():
        shutil.rmtree(d)
    src = ROOT / MODEL[model]["path"] / "Executables"
    for s in MODEL[model]["scenarios"].split("|"):
        f = src / f"{s}_0" / f"{s}_0.txt"
        if f.exists() and s != "NDC":
            (d / f"{s}_0").mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d / f"{s}_0" / f.name)
    out = REPLAY / case / "out"
    GR.main(["--point", point, "--models", model, "--data-dir", str(REPLAY / case), "--out", str(out), "--jobs", "1"])
    rows = list(csv.DictReader(open(out / "gate_results.csv", encoding="utf-8")))
    record("JAM_TRANSPORT scenarios sharing one input folder after the rename", model, "NDC",
           "copy of the model's compiled files with the NDC data file missing (the runner wrote one folder for two "
           "scenario names)", "S7", rows, scenario="NDC", message="no data file")


CASES = dict(dr_ppicefoi=dr_ppicefoi, ecu_maxcap=ecu_maxcap, ecu_pphdamps_dup=ecu_pphdamps_dup,
             cr_policy_history=cr_policy_history, dr_policy_history=dr_policy_history, gua_hydrogen=gua_hydrogen,
             ecu_share_135=ecu_share_135, hon_ceilings=lambda: hon_cap("hon_ceilings", False),
             hon_minimum_only=lambda: hon_cap("hon_minimum_only", True), jam_transport_rename=jam_transport_rename)

if __name__ == "__main__":
    want = sys.argv[1:] or list(CASES)
    for k in want:
        try:
            CASES[k]()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            RESULTS.append(dict(defect=k, model="", scenario="", how_put_back=f"replay failed: {exc}",
                                expected_check="", flagged="no", gate_results_line=""))
    out = JOB / ("replay_check.csv" if not sys.argv[1:] else f"replay_partial_{'_'.join(want)}.csv")
    if out.exists() and not sys.argv[1:]:  # keep the row replay_gua_distance.py appended
        RESULTS += [r for r in csv.DictReader(open(out, encoding="utf-8")) if r["defect"].startswith("Guatemala NDC and LTS")]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["defect", "model", "scenario", "how_put_back", "expected_check", "flagged",
                                           "gate_results_line"], lineterminator="\n")
        w.writeheader()
        w.writerows(RESULTS)
