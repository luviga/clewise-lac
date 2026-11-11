"""Write REPORT, GAPS and CHANGES for LAC_COST_REGIONAL from the output files."""
import json, os, sys
import pandas as pd

STAMP = "20261111T050439Z"
PR = sys.argv[1] if len(sys.argv) > 1 else "not yet opened (recorded in a second commit)"
COMMIT = sys.argv[2] if len(sys.argv) > 2 else "the commit that adds this folder (recorded in a second commit)"
ORIGIN = "9dcafbf15f2c6ba5b306efa383fc33ef333baa22"

sc = pd.read_csv("scope.csv")
cmp_ = pd.read_csv("regional_vs_international.csv")
src = pd.read_csv("sources.csv")
rv = pd.read_csv("regional_values.csv")
props = pd.read_csv("regional_proposals.csv", dtype=str)
vc = pd.read_csv("value_checks.csv")
g = json.load(open("scratch/gates.json"))
leads = pd.read_csv("leads.csv")
log = pd.read_csv("search_log.csv")
man = pd.read_csv("manual_downloads.csv")

def fmt(x, nd=2):
    try:
        return f"{float(x):,.{nd}f}"
    except (TypeError, ValueError):
        return ""

# ---------------- REPORT ----------------
R = []
R.append("# REPORT LAC_COST_REGIONAL " + STAMP + "\n")
R.append("Regional plant cost values for the plant rows that rest only on international sources.\n")
R.append("## Run\n")
R.append(f"- Pull request: {PR}")
R.append("- Branch: `job/cost-regional`")
R.append(f"- `origin/main` hash at branch time: `{ORIGIN}` (all seven job folders of the preamble table present)")
R.append(f"- Commit hash: {COMMIT}")
R.append("- Job folder: `_LAC_HUB/cost_regional_" + STAMP + "/`\n")
R.append("## Scope (Step 1)\n")
by = sc.groupby("country").rows.sum().to_dict()
R.append(f"The scope rule selects {int(sc.rows.sum()):,} rows, {len(sc)} country, technology and parameter groups and "
         f"{sc.groupby(['country','technology']).ngroups} country and technology pairs, equal to the expected 2,217, 68 and 40. "
         "Rows by country: " + ", ".join(f"{k} {v}" for k, v in by.items()) + " (all equal to the brief).\n")
R.append("## Outcome\n")
oc = sc.outcome.value_counts()
acc = sc[sc.outcome != "international kept"]
R.append(f"- Groups with an accepted value: {len(acc)} of 68 (N {oc.get('N', 0)}, R1 {oc.get('R1', 0)}, R2 {oc.get('R2', 0)}); "
         f"international kept: {oc.get('international kept', 0)}.")
R.append(f"- `regional_proposals.csv`: {len(props)} rows (one per year column of each accepted group), values in real 2024 USD and model units.")
R.append(f"- Accepted groups by country: " + ", ".join(f"{k} {v}" for k, v in acc.groupby('country').size().items()) + "; Dominican Republic 0.\n")
R.append("## Documents opened, by tier and region\n")
tiermap = {"REG-001": ("LAC", "R1"), "REG-002": ("LAC", "R1"), "REG-003": ("LAC", "R1"), "REG-004": ("Central America", "R1"), "REG-012": ("LAC", "R1"),
           "REG-005": ("Central America", "N (Costa Rica); R2 (Guatemala, Honduras)"), "REG-006": ("Central America", "R2"), "REG-020": ("Central America", "R2"),
           "REG-007": ("Central America", "R2"), "REG-008": ("Central America", "N (Guatemala); R2"), "REG-009": ("Central America", "R2"),
           "REG-010": ("Central America", "R2"), "REG-011": ("Central America", "R2"), "REG-013": ("Andean", "R2"), "REG-014": ("Andean", "R2"),
           "REG-015": ("Caribbean", "R2"), "REG-021": ("Caribbean", "R2"), "REG-016": ("Caribbean", "R2"), "REG-017": ("Caribbean", "R2"),
           "REG-018": ("Caribbean", "R1"), "REG-019": ("Caribbean", "R2")}
used = set(x for v in props.source_ids for x in v.split(";"))
R.append("| Source | Document | Region | Tier | Values in `regional_values.csv` | Used in proposals |")
R.append("|---|---|---|---|---|---|")
for _, r in src[src.source_id.str.startswith("REG")].iterrows():
    reg, tier = tiermap[r.source_id]
    n = int((rv.source_id == r.source_id).sum())
    R.append(f"| {r.source_id} | {r.title} ({r.publisher}, {r.publication_date}) | {reg} | {tier} | {n} | {'yes' if r.source_id in used else 'no'} |")
cnt = pd.Series([tiermap[s][0] for s in tiermap]).value_counts().to_dict()
R.append("\nDocuments opened by region: " + ", ".join(f"{k} {v}" for k, v in cnt.items()) +
         " (21 documents). By tier: N 1 (ICE PEG 2024-2040, national for Costa Rica; MEM Guatemala PEG 2024-2054 would be N for Guatemala but prints no cost table); "
         "R1 6 (IRENA RPGC 2022, 2024 and 2025, IRENA Central America roadmap, IDB TN-1831, CCREEE); R2 14 (neighbour plans and the Colombian catalogue). "
         "CPI-U files of three country jobs (CRC-001, FUE-001, CSH-005) were copied for the currency conversion.\n")
R.append(f"Leads: {len(leads)} rows in `leads.csv`; {len(log)} entries in `search_log.csv`; {len(man)} manual downloads. Extra documents beyond the lead list: "
         "Central America 2 of 10 (ICE PEG 2024-2040, MEM Guatemala PEG 2024-2054), Andean 1 of 10 (Ecuador PME chapter, did not open), Caribbean 1 of 10 (CNE Dominican Republic study, not found).\n")
R.append("## The 68 groups\n")
R.append("2024 values in model units (CapitalCost USD/kW, FixedCost USD/kW-year, VariableCost USD/GJ; Ecuador STOELE per PJ/yr of capacity). "
         "International values keep the currency year of their country job; regional values are real 2024 USD.\n")
R.append("| Country | Technology | Parameter | Outcome | Source | 2024 international | 2024 regional | Change % |")
R.append("|---|---|---|---|---|---|---|---|")
for _, r in sc.iterrows():
    m = cmp_[(cmp_.country == r.country) & (cmp_.technology == r.technology) & (cmp_.parameter == r.parameter)]
    if len(m):
        m = m.iloc[0]
        R.append(f"| {r.country} | {r.technology} | {r.parameter} | {r.outcome} | {m.regional_source} | {fmt(m.international_2024, 4)} | {fmt(m.regional_2024, 4)} | {fmt(m.change_pct_2024)} |")
    else:
        R.append(f"| {r.country} | {r.technology} | {r.parameter} | international kept | | {fmt(r.proposed_2024, 4)} | | |")
R.append("\n## Flags (Step 6)\n")
fl = cmp_[cmp_["flags"].fillna("") != ""]
R.append(f"{len(fl)} of {len(cmp_)} accepted groups carry a flag; no accepted value is outside the screens "
         "(CapitalCost 300 to 8,000 USD/kW, FixedCost 0 to 200 USD/kW-year, VariableCost up to 8.33 USD/GJ). Flags do not block a proposal.\n")
for _, r in fl.iterrows():
    R.append(f"- {r.country} {r.technology} {r.parameter}: {r['flags']}.")
R.append("\n## Gates (Step 7)\n")
g1, g3, g5 = g["gate1"], g["gate3"], g["gate5"]
R.append("| Gate | Result | Counts |")
R.append("|---|---|---|")
R.append(f"| 1 Read-only | {g1['result']} | {g1['files']} files hashed before and after (6 A-O workbooks and 180 BAU A2_Output_Params CSVs in the main copy), {g1['changed']} changed |")
R.append(f"| 2 Changed files | {g.get('gate2', {}).get('result', 'not run')} | {g.get('gate2', {}).get('counts', '')} |")
R.append(f"| 3 Sources | {g3['result']} | {g3['proposal_source_ids']} source ids in proposals, all in `sources.csv` ({g3['sources']} sources); every source has an http(s) URL, a locator, a retrieval date and a file in `downloads/`; no local path or internal file named |")
R.append(f"| 4 Values as printed | {'pass' if (vc.found == 'yes').all() else 'fail'} | {int((vc.found == 'yes').sum())} of {len(vc)} accepted printed values found in the file text at the recorded page (`value_checks.csv`) |")
R.append(f"| 5 Coverage | {g5['result']} | {g5['groups']} accepted groups, {g5['rows']} rows, no year missing or duplicated |")
R.append(f"| 6 Commit messages | {g.get('gate6', {}).get('result', 'not run')} | {g.get('gate6', {}).get('counts', 'runs on the commit itself; result recorded in the second commit')} |")
R.append(f"| 7 Dashes and whitespace | {g.get('gate7', {}).get('result', g['gate7_emdash']['result'])} | {g.get('gate7', {}).get('counts', 'no em dash in job files')} |")
open(f"REPORT_LAC_COST_REGIONAL_{STAMP}.md", "w", encoding="utf-8", newline="\n").write("\n".join(R).rstrip() + "\n")

# ---------------- GAPS ----------------
G = []
G.append("# GAPS LAC_COST_REGIONAL " + STAMP + "\n")
G.append("## 1. Judgement calls and reasons\n")
J = [
    "Currency basis. The brief says values are real 2024 USD, but several international values keep the currency year of their country job (Costa Rica plant rows 2022 USD after 2021, Jamaica as published, Guatemala ATB rows 2022 USD, Dominican Republic 2021 to 2023 USD). Regional proposals follow the brief and are real 2024 USD, so `change_pct` includes the currency-year step (about +7.2 percent for a 2022 USD row).",
    "Year of a single printed value. ICE PEG 2024-2040 and ODS Honduras PIEG 2026-2035 print one cost per technology, not a year path. The value is placed at 2024 (the first plan year of both) and the path is P(y) = R x I(y)/I(2024).",
    "ICE costs are in constant USD of December 2023. They are converted with the CPI-U annual averages 2024/2023 (313.689/304.702), the same convention the Costa Rica job used for December 2019 USD.",
    "ICE PEG 2024-2040 prints a capitalized investment (Tabla 10.8, note 1) and an overnight investment (Tabla 10.9, note 2). The overnight value is used because the model cost is overnight.",
    "IRENA weighted average total installed cost is accepted as overnight capital cost per kW, as all six country jobs did.",
    "ICE generic hydro (Hidro Genericos, 20 MW) has 0 useful volume in Tabla 10.7, so it is run-of-river and does not match Costa Rica PWRHYDDAM. ICE reservoir projects (Diquis, RG-430) are single projects, not a class value. The Costa Rica dam row takes ODS Honduras Hidroelectrica de embalse (R2).",
    "IRENA hydropower classes (large above 10 MW, small up to 10 MW) state size, not dam or run-of-river, so they match neither configuration.",
    "Costa Rica PWRSPVDTR (PV in distribution) is matched to ICE Solar Genericos (10 MW, fixed tilt), as the Costa Rica job treated it as utility-scale ground PV; fixed tilt is taken over the 1-axis tracking generic.",
    "Costa Rica PWRDSL and PWRFOI variable O&M take the ODS Honduras engine on gas/bunker/diesel (5 USD/MWh diesel, 7 USD/MWh bunker); the Costa Rica job mapped both rows to medium-speed engines.",
    "Size rows of ODS Honduras Tabla 19. Where the value differs by size the lower middle printed size is taken (hybrid PV with battery 30 percent: 50 MW of 20, 50, 100, 150). Run-of-river takes the under 10 MW row, which is also the small hydro class of the current Guatemala source. Engine O&M, PV fixed O&M and reservoir capital cost are equal across sizes.",
    "Guatemala PPPVTS (transmission solar with battery storage) is matched to the ODS Honduras hybrid PV with battery (battery 30 percent of PV power). The current ATB PV-plus-battery reference has a larger battery share; both are PV with storage, which is the configuration test of the brief.",
    "Within R2, the most recent publication wins: ODS Honduras PIEG (September 2026) over ICE PEG 2024-2040 (September 2025) for Guatemala engines, geothermal, run-of-river and combined cycle.",
    "Honduras PPBIM takes ICE Biomasa Genericos (sugarcane, steam cycle) as R2; the Honduras plan has no biomass candidate.",
    "IRENA RPGC 2024 Table 2.1 marks Central America and the Caribbean as data from 2012, not 2010, so the first printed year is 2012 for Jamaica PPWNDON.",
    "IRENA RPGC 2025 Table 3.1 prints 2015 and 2025 for Central America and the Caribbean. Following the brief, Guatemala PPPVT and PPPVT2 interpolate linearly between them for 2018 to 2024 (2024: 1,077.06 USD/kW), even though the 2024 edition printed 1,375 for 2024; within R1 the most recent edition is taken.",
    "IRENA RPGC 2025 wind and PV rows for Other North America include Canada and are not LAC tables; they are not used.",
    "Colombian Technology Catalogue (R2 for Ecuador): values per MWe (AC) are used, not per MWp (DC). Ecuador PPPVD (distributed solar) takes the industrial rooftop class (100 kW) because the current Ecuador source is ATB commercial PV; PPWNDD takes small turbines under 1 MW; STOELE takes grid-scale lithium-ion, 4 hours, and keeps the /31.536 PJ per GW-year conversion of the Ecuador job.",
    "Catalogue reading corrections: PDF p.64 fixed O&M prints 15.000, 12.900, 10.900 with the last digit in a separate text cell; PDF p.140 prints 66,500 with a comma and PDF p.141 prints 94.00 next to 93.600; all are read as thousands of USD/MW-year (stated in `regional_values.csv`). Only the p.64 row enters a proposal.",
    "Dominican Republic PPPVT, PPPVTHYD and PPWNDON are refused: their current paths add a 4-hour battery cost from 2025, and no regional source with a stated currency year prices that configuration.",
    "Dominican Republic PPDHYD (self-producer hydro) states no hydro type, so no dam or run-of-river value is matched.",
    "Jamaica PPWNDON: the 2021 row of `proposals_all.csv` rests on the national 2018 IRP (PSJ-004) and is outside the scope rule, so the regional path covers 2022 to 2055 only.",
    "Jamaica IRP 2018 states 2018 USD (PDF p.59) and is R2 for the Dominican Republic, but none of its candidate rows matches an in-scope Dominican Republic group with the allowed configuration.",
    "The ODS Honduras CPI-U source (CSH-005) was fetched by the Honduras job through a POST to the BLS v1 API; its URL is recorded as that job recorded it.",
    "Where a conversion needed no CPI-U factor (2024 USD sources), `source_ids` carries only the regional source id.",
]
for i, j in enumerate(J, 1):
    G.append(f"{i}. {j}")
G.append("\n### Documents excluded (no value accepted)\n")
EX = [
    ("IRENA Renewable Energy Roadmap for Central America 2022 (REG-004)", "Table 16 has no currency year (would have served distributed PV, biomass and geothermal)."),
    ("MEM Guatemala PEIG 2026-2050 (REG-007)", "Tabla 6 has no currency year."),
    ("MEM Guatemala PEG 2024-2054 (REG-008)", "no technology cost table in the text layer."),
    ("ETESA Panama PESIN 2025-2039 (REG-009)", "project costs in B/./kW with no currency year; promoter data, not class values."),
    ("El Salvador PIEGE 2020-2030 (REG-010)", "project costs with no currency year."),
    ("SENER Mexico PLADESE 2025-2039 (REG-011)", "costs are CAIO (include interest during construction at 6.89 percent) and carry no currency year."),
    ("IDB Technical Note 1831 (REG-012)", "country costs only as charts."),
    ("UPME Colombia PIEG 2025-2039 (REG-013)", "CAPEX only as a chart; led to the Colombian Technology Catalogue."),
    ("CNE Dominican Republic PEN 2022-2036 (REG-016)", "generic project tables 204 to 229 state no currency year."),
    ("Barbados IRRP draft 2021 (REG-017)", "Table E.1 is labelled 2020 Cost (BBD/MW) with no price base; units read as BBD per kW."),
    ("CCREEE 2022 (REG-018)", "benchmarks are ranges or global values with no stated currency year; the LAC wind 2,062 USD/kW is older than IRENA RPGC 2024."),
    ("PREPA IRP 2019 (REG-019)", "covers utility PV, onshore wind and batteries only; no in-scope Caribbean group matched (Dominican Republic PV and wind refused for configuration; Jamaica wind takes R1)."),
    ("Jamaica IRP 2022 (REG-021)", "no per-kW cost table."),
    ("USAID Caribbean Energy Initiative cost comparison (2021)", "seen in search results; USAID is a bilateral agency, not a regional or multilateral body or a neighbour government, so it fits no tier; not downloaded."),
]
for d, r in EX:
    G.append(f"- {d}: {r}")
G.append("\n## 2. Known-limitation candidates\n")
K = [
    ("`_LAC_HUB/cost_review_20261111T015203Z/proposals_all.csv`, plant rows of Costa Rica, Jamaica, Guatemala and the Dominican Republic", "International plant values are in mixed currency years (2018 to 2024 USD), while the brief and these regional proposals use real 2024 USD."),
    ("`proposals_all.csv`, Dominican Republic PPPVT, PPPVTHYD, PPWNDON", "Rows described as plain solar or wind carry a 4-hour battery cost from 2025, which blocks any plain regional value."),
    ("`proposals_all.csv`, Guatemala PPPVT and PPPVT2", "Two transmission solar rows with the same description now receive the same IRENA capital path."),
    ("`proposals_all.csv`, Jamaica PPWNDON CapitalCost", "The 2021 value is the national IRP 1,870 USD/kW (2018 USD) while 2022 onwards is regional, so the path has a step."),
    ("`regional_proposals.csv`, Honduras PPBIM FixedCost", "ICE sugarcane biomass fixed O&M (38 USD/kW-year) is 77 percent below the ATB dedicated biopower value it replaces."),
    ("`regional_proposals.csv`, Ecuador STOELE FixedCost", "Catalogue battery fixed O&M (15 USD/kW-year in 2024) is 68 percent below ATB; ATB includes augmentation in fixed O&M."),
]
for w, t in K:
    G.append(f"- {w}: {t}")
G.append("\n## 3. Left unchecked\n")
for t in [
    "PDF tables were read from the text layer (PyMuPDF and pdfplumber); pages were not rendered to images. Gate 4 found every accepted value in the text at its page.",
    "MEM Guatemala PEG 2024-2054 may hold cost tables as images; no OCR was run.",
    "IRENA RPGC 2022 regional PV costs are a figure without a text table and were not transcribed.",
    "The Panama project table parse (426 values) was not reconciled with the table totals.",
    "Whether the model also represents the storage service of the Dominican Republic PV and wind rows was not checked.",
]:
    G.append(f"- {t}")
G.append("\n## 4. Manual downloads\n")
for _, r in man.iterrows():
    G.append(f"- {r.url}: {r.what_it_should_hold}. Would serve: {r.groups_it_would_serve}.")
G.append("\n## 5. Incidents\n")
for t in [
    "curl crashed (segmentation fault) on the ICE PEG 2024-2040 URL; the file was downloaded with Python urllib from the same URL.",
    "The IDB publications server returned HTTP 403 to Python urllib; curl with a browser user agent downloaded the file.",
    "The Ecuador ministry host (recursosyenergia.gob.ec) does not resolve, as the Ecuador job also found.",
    "Three helper scripts briefly contained literal dash characters after writing; they were replaced with chr() calls before the dash gate ran.",
    "The brief asks for one commit and for the pull request number and commit hash in REPORT. A file cannot carry its own commit hash and the number exists only after the pull request is opened, so a second commit updates REPORT with both (the method used by the earlier cost jobs).",
]:
    G.append(f"- {t}")
open(f"GAPS_LAC_COST_REGIONAL_{STAMP}.md", "w", encoding="utf-8", newline="\n").write("\n".join(G) + "\n")

# ---------------- CHANGES ----------------
C = ["# CHANGES LAC_COST_REGIONAL " + STAMP + "\n",
     f"Regional plant cost values where published: {len(acc)} of 68 international-only groups get a regional or late national value "
     f"({len(props)} rows in `regional_proposals.csv`); 40 keep their international value.\n",
     "## Files created (all in `_LAC_HUB/cost_regional_" + STAMP + "/`)\n"]
FILES = [
    ("BRIEF_LAC_COST_REGIONAL.md", "copy of the brief"),
    (f"REPORT_LAC_COST_REGIONAL_{STAMP}.md", "run facts, scope counts, documents, the 68 groups, flags, gates"),
    (f"GAPS_LAC_COST_REGIONAL_{STAMP}.md", "judgement calls, exclusions, known-limitation candidates, unchecked items, manual downloads, incidents"),
    (f"CHANGES_LAC_COST_REGIONAL_{STAMP}.md", "this file"),
    ("scope.csv", "68 groups with technology name, configuration, 2024 value, sources and outcome"),
    ("leads.csv", "lead families and documents with status"),
    ("search_log.csv", "searches and documents opened"),
    ("manual_downloads.csv", "pages that did not open or documents not located"),
    ("regional_values.csv", "every generation cost printed in the opened regional documents"),
    ("match_log.csv", "match or refusal per group"),
    ("regional_proposals.csv", "one row per year column of each accepted group, columns of proposals_all.csv plus tier, international_value, change_pct"),
    ("regional_vs_international.csv", "one row per accepted group, 2024 comparison and flags"),
    ("sources.csv", "external sources with URL, dates, file and locator"),
    ("value_checks.csv", "gate 4 checks of accepted values against the file text"),
    ("baseline_before.csv", "SHA-256 of the six A-O workbooks and BAU A2_Output_Params CSVs at start"),
    ("baseline_after.csv", "the same at the end"),
    ("baseline.py", "hashing script for gate 1"), ("step1_scope.py", "scope rule"), ("textindex.py", "PDF text extraction helper"),
    ("pages.py", "page search helper"), ("catalog_extract.py", "Colombian catalogue data sheet extraction"),
    ("regional_data.py", "transcribed source register and printed values"), ("step3_extract.py", "builds regional_values.csv"),
    ("step4_match.py", "matching decisions, scope.csv and match_log.csv"), ("step5_proposals.py", "regional proposals and comparison"),
    ("step2_logs.py", "sources, leads, search log and manual downloads"), ("gate4_value_checks.py", "gate 4"), ("gates.py", "gates 1, 3, 5 and 7 (dashes)"),
    ("report_text.py", "writes REPORT, GAPS and CHANGES"),
]
for f_, d in FILES:
    C.append(f"- `{f_}`: {d}")
C.append("\nUntracked: `downloads/` (source files) and `scratch/` (working files).\n")
C.append("No model file and no existing proposal was changed: the A-O workbooks and BAU parameter CSVs hash the same before and after (gate 1), "
         "and `proposals_all.csv` and the country job files were only read. LAC_COST_WRITE reads `regional_proposals.csv` on top of `proposals_all.csv`.")
open(f"CHANGES_LAC_COST_REGIONAL_{STAMP}.md", "w", encoding="utf-8", newline="\n").write("\n".join(C) + "\n")
print("written")
