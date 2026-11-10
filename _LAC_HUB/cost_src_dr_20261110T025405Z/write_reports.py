"""Write REPORT, GAPS and CHANGES markdown files from the job CSVs, then normalise line endings to LF."""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *

def f(x, n=2):
    try: return f"{float(x):,.{n}f}"
    except (TypeError, ValueError): return str(x)
gates = open(os.path.join(JOB, "gate_results_pre.txt"), encoding="utf-8").read().strip().splitlines()
post = os.path.join(JOB, "gate_results_post.txt")
gates_post = open(post, encoding="utf-8").read().strip().splitlines() if os.path.exists(post) else []
FS = pd.read_csv(os.path.join(JOB, "fuel_summary.csv"))
PS = pd.read_csv(os.path.join(JOB, "plant_summary.csv"))
P = pd.read_csv(os.path.join(JOB, "proposals.csv"))
PT = pd.read_csv(os.path.join(JOB, "paper_trace.csv"))
SRC = pd.read_csv(os.path.join(JOB, "sources.csv"))
SUM = pd.read_csv(os.path.join(JOB, "proposals_summary.csv"))

R = []
R.append(f"# REPORT LAC_COST_SRC_DR {STAMP}\n")
R.append("Sourced cost proposals for the Dominican Republic energy model (`DominicanRepublic/RD_ENERGY`). No model file changed; `proposals.csv` is the file LAC_COST_WRITE reads.\n")
R.append("- Pull request: draft, opened on `luviga/clewise-lac` from branch `job/cost-src-dr` after the commit; its number and URL are given in the pull request list of that branch (they cannot be written inside the single commit the brief allows).")
R.append("- Branch: `job/cost-src-dr`, from `2ddd560`.")
R.append("- Commit: the single commit \"LAC_COST_SRC_DR: sourced cost proposals for Dominican Republic\" on that branch, which adds this folder (a commit cannot hold its own hash).")
R.append("- Brief: `BRIEF_LAC_COST_SRC_DR.md` (copied verbatim).\n")
R.append("## Gate results\n")
R.append("| Gate | Result |\n|---|---|")
for g in gates + gates_post:
    name, rest = g.split(": ", 1)
    R.append(f"| {name} | {rest} |")
if not gates_post:
    R.append("| Gates 2, 3, 7b, 7c (after the commit) | run after the commit with `gates.py post`; results are in `gate_results_post.txt` on the branch working copy and in the pull request body |")
R.append("\nSourcing check script: `gates.py` (gate 4 counts above). Proposals rows: " + f"{len(P)}; basis classes " + ", ".join(f"{k} {v}" for k, v in P.basis_class.value_counts().items()) + "; change classes " + ", ".join(f"{k} {v}" for k, v in P.change_class.value_counts().items()) + ".\n")

R.append("## Fuel supply rows\n")
R.append("Source: `fuel_summary.csv`, `fuel_prices.csv`. USD/GJ, net calorific basis, real 2024 USD. Current = BAU compiled 2024 VariableCost. Step at the join = STEPS 2026 over 2025, in percent (not smoothed).\n")
R.append("| Row | Chosen point | 2024 value | Current 2024 | r | r case | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | Step at join |\n|---|---|---|---|---|---|---|---|---|---|---|")
for r in FS.itertuples():
    case = "multi-year average" if r.r_case.startswith("multi") else "2024 ratio alone"
    R.append(f"| `{r.row}` | {r.chosen_point} | {f(r.value_2024,3)} | {f(r.current_2024,3)} | {f(r.r,4)} | {case} ({r.r_case.split('years ')[-1] if r.r_case.startswith('multi') else 'no history'}) | {f(r.STEPS_2030,3)} | {f(r.STEPS_2050,3)} | {f(r.CPS_2050,3)} | {f(r.NZE_2050,3)} | {f(r.join_step_pct,1)}% |")
R.append("\nBenchmarks: crude and oil products against EIA Brent (RBRTE) with the WEO 2025 IEA crude oil price; natural gas against Henry Hub (RNGWHHD, converted to net with 0.9) with the WEO 2025 United States gas price, because US exports of LNG to the DR in 2024 (90,594 MMcf, EIA) equal about all DR LNG imports (1,842,142 t, about 89,798 MMcf gross, UN Comtrade) and the TotalEnergies supply agreement of April 2025 is indexed to Henry Hub; coal against the World Bank Coal South African series with the WEO 2025 European Union steam coal price, because the DR coal reference is Platts FOB Puerto Bolivar (Colombia), an Atlantic-basin export price (MEM Boletin 2024). WEO 2025 fuel prices are in Table 2.3 on page 109 (not Table 2.32), USD (MER, 2024), years 2024, 2035 and 2050, linearly interpolated and flat after 2050 (the model ends in 2050). WEO 2025 was written before the 2026 Middle East energy crisis.\n")
R.append("`EXTT_CRU`, `EXTT_NGS` and `PRO_COA` get no proposal (country notes): `EXTT_NGS` cannot run (activity upper limit 0 in every year); `EXTT_CRU` (43.2 PJ in 2024) and `PRO_COA` (3.1 PJ in 2024) can run at zero cost, recorded in GAPS as known-limitation candidates.\n")

R.append("## Plants\n")
R.append("Source: `plant_summary.csv`, `plant_costs.csv`. 2024 values; CapitalCost USD/kW, FixedCost USD/kW-yr, VariableCost USD/GJ (non-fuel variable O&M). Class is the P2 class of the 2024 cell; the last column lists every class used over 2018 to 2050.\n")
R.append("| Technology | Capital cur | Capital prop | Fixed cur | Fixed prop | Variable cur | Variable prop | Class 2024 (C / F / V) | Sources 2024 (C / F / V) |\n|---|---|---|---|---|---|---|---|---|")
for t in PLANTS:
    g = PS[PS.technology == t].set_index("parameter")
    R.append(f"| `{t}` | {f(g.cur_2024['CapitalCost'],1)} | {f(g.prop_2024['CapitalCost'],1)} | {f(g.cur_2024['FixedCost'],2)} | {f(g.prop_2024['FixedCost'],2)} | {f(g.cur_2024['VariableCost'],4)} | {f(g.prop_2024['VariableCost'],4)} | "
             f"{g.class_2024['CapitalCost']} / {g.class_2024['FixedCost']} / {g.class_2024['VariableCost']} | {g.source_2024['CapitalCost']} / {g.source_2024['FixedCost']} / {g.source_2024['VariableCost']} |")
R.append("\nSource ids: CSD-008 CNE Plan Energetico Nacional 2022-2036 (Tablas 220, 223, 229); CSD-009 IRENA Renewable Power Generation Costs in 2022; CSD-011 and CSD-012 NREL ATB 2023 and 2024; full records in `sources.csv`.\n")
R.append("## Electricity imports\n")
R.append("`IMP_ELE` has an activity upper limit of 0 in every BAU year (VariableCost 19.05 USD/GJ, CapitalCost 1,642.86, FixedCost 32.86). It never runs, so rule E1 does not apply and nothing is proposed.\n")
R.append("## Country task\n")
R.append("- Gasoline and LPG use the market import cost (decision 2): `DIST_GSL` 19.614 USD/GJ (US export FOB to the DR times the DR CIF/FOB ratio, HS 271012) and `DIST_LPG` 11.042 USD/GJ (DR customs CIF, HS 271112 plus 271113). The MICM parities (19.490 and 15.253) are in `price_points_2024.csv`.")
R.append("- The same rule (market over administrative) is applied to natural gas: `DIST_NGS` uses the DR customs CIF of LNG (8.936 USD/GJ, already net) instead of the MICM PPI (8.666 USD/GJ gross, 9.629 net), which is fixed in pesos. See GAPS.")
R.append("- `DIST_KER` is priced (current 0) at the MICM kerosene import parity, 19.889 USD/GJ in 2024; jet fuel parity (20.015) is recorded beside it.")
R.append("- `PPBIM` CapitalCost 38.46 USD/kW has no external source; proposed 2,162 USD/kW (IRENA 2022 bioenergy). `PPBIM` cannot build more capacity, so the change does not affect investment. Its fixed (35.16) and variable (1.5806) values match the PEN Tabla 229 engine figures by number.")
R.append("- `PPBGS` (can build, activity limit up to 16 PJ) had zero placeholders; proposed capital 2,162 USD/kW (IRENA 2022), fixed 163.67 USD/kW-yr (ATB 2024 Biopower), variable 1.389 USD/GJ (IRENA 2022, 0.005 USD/kWh).")
R.append("- Activity check: `EXTT_NGS` cannot run; `EXTT_CRU` and `PRO_COA` can (see GAPS).\n")
R.append("## ASSUMPTION rows\n")
nA = (P.basis_class == "ASSUMPTION").sum()
nS = (P.assumption_sentence.fillna("") != "").sum()
R.append(f"{nA} rows have basis ASSUMPTION. {nS} rows (`DIST_NGS`, history from ratio and projected years) carry the brief's natural gas gross-to-net ASSUMPTION sentence, because their Henry Hub benchmark is published per MMBtu; the observed LNG customs values are per tonne and already net.\n")
R.append("## Paper trail\n")
R.append("Source: `paper_trace.csv`. Statements per document:\n")
for d, n in PT.document.value_counts().items():
    R.append(f"- {d}: {n}")
R.append("\nWhat changes if the proposals are applied: the Data in Brief section 4.8 text (sources, base year, currency basis, fuel price scenarios), the Table 53 rows for the 9 supply rows and 23 plants (two rows to add, `PPBGS` and `DIST_KER`), references [13] and [14]; the MethodsX energy template sentence on costs; the JCLP results for the DR (DCAPEX/GDP, DOPEX/GDP, accumulated investment, fuel-import exposure, BAU emissions check) after a rerun; `Suplementary.xlsx` sheet Costos_RD (same as Table 53) and `Data_v2.xlsx` sheet 13.RD_Costos (results to recompute).\n")
R.append("## Notes for LAC_COST_WRITE\n")
nfill = (P.change_class == "fill_empty").sum()
nmode = P[P.needs_user_defined_mode == "yes"].groupby(["Tech", "Parameter"]).ngroups
R.append(f"- {nfill} proposal rows fill workbook cells that are empty today (their current value is the BAU compiled value produced by the row's projection mode).")
R.append(f"- {nmode} technology-parameter rows have `needs_user_defined_mode = yes`: their proposal varies by year or fills empty cells while the Projection.Mode is Flat, Percent growth of incomplete years or another non user-defined mode. Writing the cells without changing the mode to User defined would leave the proposals unused.")
R.append("- Fuel rows have three scenario variants (STEPS, CPS, NZE); the base model uses STEPS.\n")
open(os.path.join(JOB, f"REPORT_LAC_COST_SRC_DR_{STAMP}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(R).rstrip("\n") + "\n")

# ---------------- GAPS ----------------
big = []
for r in SUM[SUM.fuel_scenario.isin(["ALL", "STEPS"])].itertuples():
    for y in (2024, 2030, 2050):
        c = getattr(r, f"change_pct_{y}")
        try:
            if abs(float(c)) > 25: big.append((r.Tech, r.Parameter, y, float(c), getattr(r, f"current_{y}"), getattr(r, f"proposed_{y}")))
        except (TypeError, ValueError):
            if getattr(r, f"current_{y}") == 0 and getattr(r, f"proposed_{y}") != 0: big.append((r.Tech, r.Parameter, y, None, 0, getattr(r, f"proposed_{y}")))
CAUSE = {
    "DIST_COA": "current values are about 2.4 times the 2024 customs CIF (3.97 USD/GJ); the current 2024 value tracks the 2022 price spike",
    "DIST_COK": "current values grow by a percent rule; the customs CIF of petroleum coke is 2.62 USD/GJ and the projection follows Brent through WEO",
    "DIST_DSL": "the current row grows by a percent rule to 33.4 USD/GJ in 2050; the WEO 2025 STEPS crude path is flat to falling",
    "DIST_GSL": "same percent growth rule in the current row; the market import cost is 19.61 USD/GJ",
    "DIST_LPG": "current 29.47 USD/GJ is a retail-type value; the DR customs CIF is 11.04 USD/GJ and the MICM parity 15.25",
    "DIST_NGS": "the current row falls to 3.2 USD/GJ by 2050; the WEO 2025 US gas price rises from 2.2 to 4.6 USD/MBtu in STEPS and r is 2.68 (LNG over Henry Hub)",
    "PPBIM": "current 38.46 USD/kW has no external source; IRENA 2022 bioenergy is 2,162",
    "PPBGS": "zero placeholders replaced with sourced values",
    "PPDHYD": "current 1,980 and 20 have no external source; IRENA 2022 hydropower 2,881 USD/kW and 2.5 percent O&M",
    "PPCOA": "PEN Tabla 223 gives fixed 40.58 USD/kW-yr and variable 4.50 USD/MWh against current 82 and 0.71 USD/GJ (2.54 USD/MWh)",
    "PPCCTDSL": "current 3.18 USD/GJ (11.4 USD/MWh) has no source; PEN Tabla 220 combined cycle 2.55 USD/MWh",
    "PPICEFOI": "current 1.04 USD/GJ (3.75 USD/MWh) has no source; PEN Tabla 229 engines 5.69 USD/MWh",
    "PPPVD": "ATB 2024 CommPV fixed O&M falls over time while the current value is flat at 18",
    "PPPVT": "ATB 2024 UtilityPV fixed O&M (21.6 USD/kW-yr in 2024) is above the current 13.5",
    "PPPVTHYD": "same as PPPVT",
}
G = []
G.append(f"# GAPS LAC_COST_SRC_DR {STAMP}\n")
G.append("## Judgement calls\n")
for line in [
    "Natural gas chosen point: the import CIF (DR customs, LNG, 8.936 USD/GJ net) instead of the first point in F2 order (MICM wholesale import parity, 8.666 USD/GJ gross, 9.629 net). Reason: rule F2 says market over administrative, and the MICM natural gas PPI is fixed in pesos and changes twice a year. It is also the option that changes the current value least (+17 percent against +26 percent).",
    "Kerosene chosen point: the MICM kerosene import parity (19.889 USD/GJ), although that row follows a frozen retail price. No market value for kerosene is published; the market-tracking jet fuel parity (20.015) differs by 0.6 percent and is recorded beside it.",
    "Fuel oil: the MICM Fuel Oil No. 6 parity (13.352) is chosen; the FO 1%S grade (14.950) is recorded beside it.",
    "Petroleum coke and LPG are benchmarked to Brent and the WEO crude oil price, as rule F4 says for oil products, although petroleum coke trades against coal and LPG against Mont Belvieu propane. With the multi-year r, petroleum coke rises from 2.62 USD/GJ in 2024 to 3.69 in 2026 (step 35 percent) because the 2024 ratio to Brent (0.19) is below the 2019 to 2025 average (0.26).",
    "Coal: the WEO 2025 European Union steam coal series is used for the projection (DR coal reference Platts FOB Puerto Bolivar, Atlantic basin) and the World Bank Coal South African series (fob Richards Bay NAR 6000) as observed benchmark for r, because the Pink Sheet annual file has no Colombian coal column.",
    "Year 2025: treated as a history year (benchmark observed in 2025) for every row; where the chosen point has no 2025 observation the value is r times the 2025 benchmark. Projected years start in 2026 for all rows.",
    "History before the first observation (2018 for every row, and 2020 and 2021 for some) uses r times the benchmark, per F3. Comtrade weights flagged as estimated (2019, 2022 and 2023 coal; 2022 petroleum coke; 2019 LPG; 2023 crude) are used as published.",
    "Plant costs are left in their source currency year (PEN 2021 USD, IRENA 2022 USD, ATB 2022 or 2023 USD); the brief asks for real 2024 USD only for fuel prices.",
    "IEA WEO 2023 and 2025 technology cost tables cover only the United States, the European Union, China and India and combine O&M with fuel; they were checked for matches and not used as the replacement source. The national plan (PEN) is the first covering source for thermal plants; IRENA for PV, wind, hydropower and bioenergy levels; NREL ATB for paths.",
    "IRENA values are matched only against the year they report (2022). Where no source matches, a replacement takes the IRENA 2022 level (cited edition) and, for PV and wind, the ATB 2024 Moderate trajectory from 2022 on; the newer IRENA 2024 values are written in the derivation, not proposed.",
    "Matched rows whose cited table has a newer edition (ATB 2023 to ATB 2024 for PPHDAM and PPPVD) take the newer value as `matched, newer edition` (change class upgrade), and the cited value is kept in `plant_costs.csv` column cited_edition_value.",
    "Generic thermal plants (12 technologies) share the PEN Tabla 220 combined cycle figures. The capital cost path after 2022 follows the ATB 2024 NG 2-on-1 Combined Cycle (F-Frame) trajectory scaled to 1,084 USD/kW, because the current decline matches no source.",
    "`PPCCTDSL` variable O&M takes PEN Tabla 220 (combined cycle), although its capital and fixed values match Tabla 229 (engines) by number.",
    "PV and wind keep the storage adder the current rows apply from 2025 (the 2025 adder equals ATB 2023 4Hr battery OCC Conservative 2025, 1,836.85 USD/kW, and 35.90 USD/kW-yr fixed O&M). The proposal uses the ATB 2024 4Hr battery CAPEX and fixed O&M (Moderate) for the adder.",
    "`PPBGS` fixed O&M uses ATB 2024 Biopower Dedicated (163.67 USD/kW-yr) because IRENA 2022 gives only a range (2 to 6 percent of capital per year). This avoids an ASSUMPTION row.",
    "`PPDHYD` fixed O&M = 2.5 percent of 2,881 USD/kW (IEA average quoted by IRENA 2022 page 162).",
    "Current values: the A-O workbook fills only the 2018 cell for most rows; the current value in the proposals is the BAU compiled value, and rows writing an empty cell are `fill_empty`.",
    "PR number and commit hash are not written in REPORT because the brief allows one commit; they are in the pull request and the final summary.",
]:
    G.append(f"- {line}")
G.append("\n## ASSUMPTION rows\n")
G.append("None with basis ASSUMPTION. The `DIST_NGS` rows that use Henry Hub carry the brief's gas gross-to-net sentence; leads for `DIST_NGS` are in `search_log.csv` (EIA LNG exports by country, TotalEnergies release, AES 10-K not opened).\n")
G.append("## Proposed changes above 25 percent\n")
G.append("Source: `proposals_summary.csv` (STEPS for fuel rows).\n")
G.append("| Technology | Parameter | Year | Current | Proposed | Change | Likely cause |\n|---|---|---|---|---|---|---|")
for t, p, y, c, cv, pv in big:
    G.append(f"| `{t}` | {p} | {y} | {f(cv,4)} | {f(pv,4)} | {'from 0' if c is None else f(c,0) + '%'} | {CAUSE.get(t, 'PEN Tabla 220 variable O&M 2.55 USD/MWh (0.708 USD/GJ) against current 0.375 USD/GJ')} |")
G.append("\n## Sources blocked or paywalled\n")
for line in ["SIE resolution SIE-064-2022-TF (workbook reference for PV and wind 2018 levels): not found in a short search.",
             "bvearmb.do repository copy of the PEN and the energiaestrategica.com PEN draft: HTTP 403.",
             "totalenergies.com/node/26486: HTTP 410; Business Wire copy of the release: HTTP 403 (the TotalEnergies newsroom page was used).",
             "AES Corporation Form 10-K on sec.gov: not opened, because the SEC asks automated clients for a contact address.",
             "CNE documents page loads its file list through a script; the PEN file was reached in a browser and downloaded through the listed link, which carries a list token that may expire."]:
    G.append(f"- {line}")
G.append("\n## Known-limitation candidates\n")
for line in [
    "`EXTT_CRU` (Primary Techs): domestic crude extraction with VariableCost 0 and an activity upper limit of 43.2 PJ in 2024 (51.5 PJ maximum), producing the same fuel E1CRU as `DIST_CRU`; the DR produces no crude.",
    "`PRO_COA` (Primary Techs): domestic coal production with VariableCost 0 and an activity upper limit of 3.1 PJ in 2024 (3.6 PJ maximum), producing E1COA like `DIST_COA`; the DR produces no coal.",
    "Generic thermal plants: twelve technologies (isolated, self-producer, engines and combined cycle) share the PEN combined cycle cost figures (Secondary Techs).",
    "`PPPVT`, `PPPVTHYD`, `PPWNDON`: a battery storage cost is added to the plant cost from 2025 (Primary Techs); whether the model also represents the storage service is not checked.",
    "Unit labels: plant VariableCost rows are labelled M US$ / GWh for some technologies (for example PPHDAM, PPPVT, PPWNDON) and M US$ / PJ for others; all affected values are 0.",
    "Supply rows use the projection mode Percent growth of incomplete years, with only the 2018 cell filled (Primary Techs).",
    "MICM kerosene, gasoline and LPG parities are residuals of frozen retail prices (from LAC_LOCAL_PRICES notes).",
    "Plant costs mix currency years (2021 to 2024 USD) while fuel prices are real 2024 USD.",
    "PPPVT FixedCost 2024 is 13.5466 (section 5 of the brief shows 13.6).",
]:
    G.append(f"- {line}")
G.append("\n## Left unchecked\n")
for line in ["Whether the PEN 2025-2038 (reported to be in consultation) has newer generic project tables.",
             "The SIE-064-2022-TF resolution text.",
             "Country-level IRENA data for the DR (IRENA charts list the DR for onshore wind and PV installed costs; values not read from charts).",
             "Plant rows outside section 5 (other technologies are listed in `cost_rows_current.csv` only).",
             "Whether LAC_COST_WRITE changes projection modes when it writes year cells."]:
    G.append(f"- {line}")
G.append("\n## Incidents\n")
for line in ["The session was interrupted once at the start of Step 2 (paper file search); the step was restarted with a time limit and completed.",
             "First fuel summary read the workbook 2024 cell (empty for most rows); corrected to the BAU compiled value.",
             "IRENA single-year values were first matched against every year; corrected to match only 2022.",
             "Gate 7a first flagged URLs as machine paths (the pattern matched the scheme separator of https links); the pattern was corrected.",
             "One patch to `gates.py` by text replacement did not apply because of escaping; the line was edited directly."]:
    G.append(f"- {line}")
open(os.path.join(JOB, f"GAPS_LAC_COST_SRC_DR_{STAMP}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(G).rstrip("\n") + "\n")

# ---------------- CHANGES ----------------
C = [f"# CHANGES LAC_COST_SRC_DR {STAMP}\n",
     "Sourced cost proposals for the Dominican Republic energy model. Adds files only inside `_LAC_HUB/cost_src_dr_" + STAMP + "/`. No model file changed (gate 1: the SHA-256 of the A-O workbook and the five BAU CSVs are identical before and after).\n",
     "## Files created (tracked)\n"]
DESC = {
    "BRIEF_LAC_COST_SRC_DR.md": "the brief, copied verbatim",
    f"REPORT_LAC_COST_SRC_DR_{STAMP}.md": "gate results, fuel and plant tables, imports, country task, paper trail",
    f"GAPS_LAC_COST_SRC_DR_{STAMP}.md": "judgement calls, changes above 25 percent, blocked sources, known-limitation candidates",
    f"CHANGES_LAC_COST_SRC_DR_{STAMP}.md": "this file (also the pull request body)",
    "proposals.csv": "one row per workbook cell to write (the only file LAC_COST_WRITE reads)",
    "proposals_summary.csv": "2024, 2030 and 2050 current and proposed values by technology, parameter and scenario",
    "fuel_prices.csv": "supply row prices by year and scenario with r, benchmark, WEO series and derivation",
    "fuel_summary.csv": "one line per supply row for the report",
    "price_points_2024.csv": "every published 2024 price point beside the chosen one, with the difference in percent",
    "plant_costs.csv": "plant cost cells with P2 class, sources and derivations",
    "plant_summary.csv": "one line per plant and parameter for the report",
    "cost_rows_current.csv": "every CapitalCost, FixedCost and VariableCost row of Primary and Secondary Techs with scope",
    "section5_recheck.csv": "recomputation of the brief's section 5 table from the BAU CSVs",
    "sources.csv": "source records (13 new, the rest reused from LAC_LOCAL_PRICES)",
    "constants.csv": "constants with source and locator (CPI-U, benchmarks, WEO 2025 values, conversion factors)",
    "constants_fuel.csv": "constants written by the fuel script (merged into constants.csv)",
    "search_log.csv": "leads tried, with URL or query and result",
    "paper_trace.csv": "statements in the CLEWISE papers that concern DR costs, and what they will need to say",
    "baseline_before.csv": "SHA-256 before", "baseline_after.csv": "SHA-256 after",
    "gate_results_pre.txt": "gate output before the commit", "gate_results_post.txt": "gate output after the commit",
    "common.py": "shared paths and lists", "baseline.py": "hash script", "dump_docx.py": "paper text extraction",
    "step3_cost_rows.py": "Step 3", "step4_fuel_prices.py": "Step 4", "step5_plant_costs.py": "Steps 5 and 6", "step8_proposals.py": "Step 8",
    "build_sources.py": "sources.csv and constants.csv", "build_logs.py": "search_log.csv and paper_trace.csv", "gates.py": "Step 9 gates",
    "write_reports.py": "this report set",
}
for fn in sorted(os.listdir(JOB)):
    if os.path.isfile(os.path.join(JOB, fn)) and fn.endswith((".md", ".csv", ".py", ".txt")):
        C.append(f"- `{fn}`: {DESC.get(fn, 'supporting file')}")
C.append("\n## Downloaded or copied (local only, `downloads/`, not tracked)\n")
for r in SRC[SRC.id.str.startswith("CSD")].itertuples():
    C.append(f"- `{r.downloaded_file}`: {r.url}")
C.append("- `lp/DR/` and `lp/GEN/`: copies of the LAC_LOCAL_PRICES downloads for the reused source ids (DR-001 to DR-152, GEN-001 to GEN-008); URLs in `sources.csv`.")
C.append("- `paper/`: copies of CLEWISE_MethodsX_v02.docx, CLEWISE_DataInBrief.docx, CLEWISE_JCLP_draft_v2.docx, Suplementary.xlsx and Data_v2.xlsx, read only, with text extractions.")
C.append("\n## Model files\n\nNo model file changed.\n")
open(os.path.join(JOB, f"CHANGES_LAC_COST_SRC_DR_{STAMP}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(C).rstrip("\n") + "\n")

# normalise line endings of every tracked-type file to LF
n = 0
for fp in glob.glob(os.path.join(JOB, "*")):
    if fp.endswith((".md", ".csv", ".py", ".txt")):
        b = open(fp, "rb").read()
        nb = b.replace(b"\r\n", b"\n")
        if nb != b: open(fp, "wb").write(nb); n += 1
print("reports written; LF normalised in", n, "files")
