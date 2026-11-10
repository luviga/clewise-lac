"""Write CHANGES_LAC_COST_SRC_ECU_<stamp>.md: every file created or downloaded, with purpose or origin.
Usage: py -I step10_changes.py <job_folder> <stamp>
"""
import sys, os
import pandas as pd

job, stamp = sys.argv[1], sys.argv[2]
src = pd.read_csv(os.path.join(job, 'sources.csv'))
f2url = {}
for r in src.itertuples():
    for f in str(r.downloaded_file).split(';'):
        f2url[f.strip().replace('\\', '/')] = f'{r.id}: {r.url}'
PURPOSE = {
    'baseline_before.csv': 'SHA-256 of the Ecuador A-O workbook and five BAU parameter CSVs before the work (Step 1)',
    'baseline_after.csv': 'the same hashes after the work (gate 1)',
    'paper_trace.csv': 'statements on costs and fuel prices in the CLEWISE papers and what each would need to say (Step 2)',
    'cost_rows_current.csv': 'every CapitalCost, FixedCost and VariableCost row of Primary Techs and Secondary Techs with its scope (Step 3)',
    'fuel_prices.csv': 'fuel supply price series by row, year and fuel scenario, with case, r, benchmark and WEO series (Step 4)',
    'price_points_2024.csv': 'every published 2024 price point per supply row beside the chosen one, with the difference in percent (rule F2)',
    'plant_costs.csv': 'plant, other-row and import cost proposals with PLANMICC values beside and the 25 percent flag (Steps 5 to 7)',
    'mapping_ECU.csv': 'mapping of the model plants (hydro by kind, basin and size) to CCG and PLANMICC technologies (country task)',
    'proposals.csv': 'the cell-by-cell proposals that LAC_COST_WRITE reads (Step 8)',
    'proposals_summary.csv': 'one row per technology and parameter: 2024, 2030 and 2050 current and proposed values and change (Step 8)',
    'sources.csv': 'every source record: URL, locator, retrieval date, downloaded file',
    'constants.csv': 'constants used in derivations: CPI, benchmarks, WEO 2025 values, conversion factors',
    'search_log.csv': 'every lead tried, by row',
    'gate_results.txt': 'gate results with counts (Step 9)',
    'BRIEF_LAC_COST_SRC_ECU.md': 'copy of the brief',
    f'REPORT_LAC_COST_SRC_ECU_{stamp}.md': 'report',
    f'GAPS_LAC_COST_SRC_ECU_{stamp}.md': 'judgement calls, ASSUMPTION rows, large changes, blocked sources, known-limitation candidates',
    f'CHANGES_LAC_COST_SRC_ECU_{stamp}.md': 'this file',
    'scripts/step3_cost_rows.py': 'Step 3 script: current cost rows and section 5 recheck',
    'scripts/step4_fuel_prices.py': 'Step 4 script: fuel price series (F1 to F6)',
    'scripts/step5_plant_costs.py': 'Steps 5 to 7 script: plant, other-row and import proposals, mapping',
    'scripts/step8_assemble.py': 'Step 8 script: proposals, summary, sources, constants, search log',
    'scripts/step9_gates.py': 'Step 9 script: gates',
    'scripts/step10_changes.py': 'this inventory script',
}
lines = [f'# CHANGES LAC_COST_SRC_ECU {stamp}', '',
         'No model file changed: the hashes of the Ecuador A-O workbook and of the BAU CapitalCost, FixedCost, VariableCost, InputActivityRatio and OutputActivityRatio CSVs are identical before and after (baseline_before.csv, baseline_after.csv, gate 1). The pull request adds files inside this job folder only.', '',
         '## Tracked files (committed)', '']
for f in sorted(PURPOSE):
    if os.path.exists(os.path.join(job, f)):
        lines.append(f'- `{f}`: {PURPOSE[f]}')
lines += ['', '## Downloaded and working files (local only, under downloads/, not committed)', '',
          'Origin is the source id and URL where the file is a cited source; otherwise the line gives its purpose.', '']
for root, dirs, files in os.walk(os.path.join(job, 'downloads')):
    dirs.sort()
    for f in sorted(files):
        rel = os.path.relpath(os.path.join(root, f), os.path.join(job, 'downloads')).replace('\\', '/')
        if rel.startswith('PLANMICC/repo/'):
            continue
        if rel in f2url:
            what = f2url[rel]
        elif rel.startswith('_extract/scripts_'):
            what = 'helper script of a sub-task'
        elif rel.startswith('_extract/'):
            what = 'working extract or notes of a sub-task'
        elif rel.startswith('paper/'):
            what = 'read-only copy of a CLEWISE paper file (lead only, never cited)'
        elif rel.startswith('LP/'):
            what = 'file copied from the LAC_LOCAL_PRICES downloads (reused source or its saved page)'
        else:
            what = 'saved page, lead or cross-check file (see search_log.csv)'
        lines.append(f'- `downloads/{rel}`: {what}')
lines += ['- `downloads/PLANMICC/repo/`: shallow partial clone of https://github.com/PLANMICC/OSeMOSYS_Ecuador at 7483e67a5a7a733b4a2697a950eda23a27929df7 (no checkout; single files read with git show)', '']
open(os.path.join(job, f'CHANGES_LAC_COST_SRC_ECU_{stamp}.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print(len(lines))
