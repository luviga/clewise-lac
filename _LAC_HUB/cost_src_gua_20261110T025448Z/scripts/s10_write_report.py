"""Write REPORT_LAC_COST_SRC_GUA_<stamp>.md from the step outputs. Gate 2, 3 and 7 lines and the
pull request number are filled from work/git_gates.txt when present.
Usage: py -I s10_write_report.py <job folder>"""
import os, sys
import pandas as pd

J = sys.argv[1]
STAMP = '20261110T025448Z'
tables = open(os.path.join(J, 'work', 'report_tables.md'), encoding='utf-8').read().split('\n\n')
fuel, plant = tables[0].strip(), tables[1].strip()
g = {}
gp = os.path.join(J, 'work', 'git_gates.txt')
if os.path.isfile(gp):
    for line in open(gp, encoding='utf-8'):
        if '=' in line:
            k, v = line.rstrip('\n').split('=', 1)
            g[k] = v
pr = g.get('PR', 'not yet opened')
pt = pd.read_csv(os.path.join(J, 'paper_trace.csv'))
pt['change'] = ~pt.needed_change.str.startswith('No change')
cnt = pt.groupby('document').agg(n=('change', 'size'), c=('change', 'sum'))
def pc(doc):
    return int(cnt.loc[doc, 'n']), int(cnt.loc[doc, 'c'])

txt = f"""# REPORT LAC_COST_SRC_GUA {STAMP}

Sourced cost proposals for the Guatemala energy model (`Guatemala/GUA_ENERGY`). This job changes no model file; LAC_COST_WRITE reads `proposals.csv`.

- Pull request: {pr} (draft)
- Branch: `job/cost-src-gua`, from `2ddd560`
- Commit: the single commit on the branch, message "LAC_COST_SRC_GUA: sourced cost proposals for Guatemala". Its hash is stated in the pull request description, since a file cannot hold the hash of its own commit.
- Stamp: {STAMP}

## Gates

| Gate | Result |
|---|---|
| 1. Read-only | pass: `baseline_after.csv` equals `baseline_before.csv` (6 files, SHA-256) |
| 2. Diff scope | {g.get('GATE2', 'pending')} |
| 3. Tracked file types | {g.get('GATE3', 'pending')} |
| 4. Sourcing | pass: 2,212 non-ASSUMPTION proposal rows, 0 with a missing or unknown source id; 197 ASSUMPTION rows, 0 citing an unknown id; 112 sources, each with an http(s) URL, a locator, a retrieval date and a file present in `downloads/`, 0 problems; no local path or internal file in any source field |
| 5. ASSUMPTION rows | pass: 197 rows over 3 technologies (`DIST_NGS`, `IMP_ELE`, `PPPVDS`), each with leads in `search_log.csv`; 3 distinct sentences, 0 failing the word check |
| 6. Coverage | pass: 15 plants x 3 parameters x 33 years, 9 supply rows x 3 scenarios x 33 years, and `IMP_ELE` x 33 years; 2,409 cells, 0 gaps, 0 duplicate cells |
| 7. Text and log | {g.get('GATE7', 'pending')} |

Gate script: `scripts/s9_gates.py`; output in `work/gates_output.txt`.

## Fuel supply rows

All values are USD/GJ on a net calorific basis in real 2024 USD (CPI-U). Projections are P(y, s) = r x B(2024) x WEO_s(y) / WEO_s(2024), using WEO 2025 Table 2.3 (page 109, USD MER 2024; the table is 2.3, not 2.32).

Benchmarks:
- `DIST_COA`: World Bank Coal South African, with the WEO European Union steam coal price.
- `DIST_NGS`: EIA Henry Hub, with the WEO United States gas price.
- All other rows: EIA Brent, with the WEO IEA crude oil price.

r cases:
- Case 1: mean over the chosen point's own history.
- Case 2: mean over the import CIF history, times the 2024 ratio of the chosen point to import CIF.
- Case 3: the 2024 ratio alone.

The step is the change from 2025 (the last history year) to 2026 (the first projected year), not smoothed.

{fuel}

Notes:
- `DIST_KER` uses the MEM consumer price net of taxes. The Banguat import CIF of 51.23 USD/GJ covers 14.8 t in the year and was set aside.
- `DIST_NGS` is an ASSUMPTION: 7.763 USD/GJ gross, divided by 0.9.
- `EXTT_CRU` is new: Banguat crude export FOB, 389.85 USD/t in 2024.
- Every other published 2024 point is in `price_points_2024.csv`.

## Power plants (2024)

CapitalCost is in USD/kW (MUSD/GW), FixedCost in USD/kW-yr, and VariableCost in USD/GJ (MUSD/PJ).
- The current plant VariableCost values are in USD/kWh: the workbook unit label reads "M US$ / GWh". The proposals convert them (x277.78, or USD/MWh / 3.6).
- Plant costs are proposed as published, in each source's dollar year.
- Source ids (details in `sources.csv`):
  - NAT-001: MEM PEIG 2026-2050.
  - NAT-002: MEM PEG 2020-2050.
  - NAT-004: MEM PEIG 2022-2052.
  - INT-001 and INT-002: IRENA RPGC 2022 and 2024.
  - INT-003 to INT-008: NREL ATB 2024, 2023 and 2021.
  - INT-009: EIA 2020 capital cost study.
  - INT-010: EIA AEO2019.
  - INT-013: IEA WEO 2025 Annex B.

{plant}

The PV paths (`PPPVT2`, `PPPVTS`, `PPPVD`) match NREL ATB 2023 Moderate (Market case) for 2024 to 2050. ATB 2024 is proposed for 2022 to 2050 as the newer edition. Proposed capital costs in 2050:
- `PPPVT2`: 682.9 USD/kW.
- `PPPVTS`: 1153.9 USD/kW.
- `PPPVD`: 929.2 USD/kW.
- `PPPVDS`: 1570.1 USD/kW (ASSUMPTION).

P2 classes over all 1,485 plant cells, by change class:
- `matched`: 543 keep and 66 unit fix.
- `matched, newer edition`: 306 upgrade.
- `replace`: 504.
- `ASSUMPTION`: 66.

## Electricity imports

`IMP_ELE` VariableCost is 0 today. The proposal is 17.2278 USD/GJ (62.02 USD/MWh, real 2024 USD) in every year:
- 2024 is `observed`; all other years are `ASSUMPTION`.
- The price is the 2024 import price volume-weighted from the AMM monthly market analyses: Mexico 55.75 USD/MWh on 1,623.39 GWh, and the regional market MER 121.68 USD/MWh on 170.57 GWh. The total, 1,793.96 GWh, equals the AMM Informe Estadistico 2024 annual import of 1,793.97 GWh.
- Check: the customs unit value is about 78.6 USD/MWh (UN Comtrade, Mexico exports to Guatemala), the top of the range.
- No published projection exists, so the price is held flat.
- FixedCost stays 0 and CapitalCost stays empty.

## Country task

- Current values confirmed: every section 5 value of the brief was recomputed from the BAU compiled CSVs and matches (`scripts/s3_bau_2024_check.csv`).
- Unit slip: fixed, with the evidence recorded.
  - The workbook's plant VariableCost unit label is "M US$ / GWh".
  - Data in Brief Table 57 prints "M USD/GWh".
  - Every source behind these values gives variable O&M in USD/MWh: PEG 2020-2050 biogas 5 and coal 6; EIA 2020 engines 5.69; IRENA bioenergy 0.005 USD/kWh. So the model values are USD/kWh, and the proposals divide USD/MWh by 3.6.
  - `PPBGS` and `PPFOI` match their sources exactly after the conversion.
- `PPDSL` CapitalCost 448: no source gives this value.
  - Its fixed (31.6) and variable (6 USD/MWh) costs equal the coal candidate of the MEM PEG 2020-2050.
  - Proposed: the MEM PEIG 2026-2050 internal combustion engine values, 1400 USD/kW, 20 USD/kW-yr and 5 USD/MWh.
- `DIST_COK` and `DIST_KER` are priced: 3.1954 and 31.2593 USD/GJ in 2024.
- `DIST_KER` import CIF check: the 51.23 USD/GJ Banguat line is a 14.8 t sample, so the next F2 point was used.
- `DIST_NGS`: ASSUMPTION at 7.763 USD/GJ gross, 8.626 USD/GJ net.
- `IMP_ELE`: priced (see above).
- `EXTT_CRU`: priced from Banguat crude export FOB.

## ASSUMPTION rows

197 rows in total:
- `DIST_NGS` VariableCost: 99 (33 years x 3 scenarios).
- `IMP_ELE` VariableCost: 32 (all years except 2024).
- `PPPVDS` CapitalCost: 33.
- `PPPVDS` FixedCost: 33.

The leads for each are listed in GAPS section 2.

## Paper trail

`paper_trace.csv` holds {len(pt)} statements. All five files opened from read-only copies.

| Document | Statements | Need a change | What changes |
|---|---|---|---|
| CLEWISE_DataInBrief.docx | {pc('CLEWISE_DataInBrief.docx')[0]} | {pc('CLEWISE_DataInBrief.docx')[1]} | Table 57: each value gets a source and dollar year, plant variable costs are relabelled to M USD/PJ after the x277.78 fix, and the new fuel prices go in, plus rows for electricity imports, kerosene, petroleum coke and crude. Section 4.8 and the specifications table: "current USD without deflation" becomes real 2024 USD for fuel prices and the source dollar year for plant costs, and the sources are named. The reference list adds WEO 2025 and IRENA 2024 and cites them by number. |
| Suplementary.xlsx | {pc('Suplementary.xlsx')[0]} | {pc('Suplementary.xlsx')[1]} | Sheet `Costos_GUA` mirrors Table 57 and changes with it, row by row. |
| CLEWISE_JCLP_draft_v2.docx | {pc('CLEWISE_JCLP_draft_v2.docx')[0]} | {pc('CLEWISE_JCLP_draft_v2.docx')[1]} | The cost basis sentence (and the missing discount rate); Guatemala result statements re-checked after a re-run; references added. |
| CLEWISE_MethodsX_v02.docx | {pc('CLEWISE_MethodsX_v02.docx')[0]} | {pc('CLEWISE_MethodsX_v02.docx')[1]} | Step 1 inputs and processing add fuel prices and technology costs; WEO 2025 CPS and NZE become fuel price sensitivities. |
| Data_v2.xlsx | {pc('Data_v2.xlsx')[0]} | {pc('Data_v2.xlsx')[1]} | Guatemala cost results and the fuel import expenditure rows are regenerated after a re-run. |

The papers cite IRENA Renewable Power Generation Costs in 2022 and IEA WEO 2023 only generically, with no technology-level source. Table 57 has no source column. Its diesel, gasoline and LPG prices equal the Dominican Republic values in Table 53.
"""
open(os.path.join(J, f'REPORT_LAC_COST_SRC_GUA_{STAMP}.md'), 'w', encoding='utf-8', newline='\n').write(txt)
print('written')
