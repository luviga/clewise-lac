"""Markdown table of the Stage 3 objectives of each full run, from stage_logs/<run>/solves_stage3.jsonl.
Usage: python objectives_table.py <run> [<run> ...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402

runs = sys.argv[1:]
data, order = {}, []
for run in runs:
    for ln in (M.JOB / 'stage_logs' / run / 'solves_stage3.jsonl').read_text(encoding='utf-8').splitlines():
        r = json.loads(ln)
        k = (r['country'], r['scenario'])
        if k not in order:
            order.append(k)
        obj = r['objective'].split('=')[1].split('(')[0].strip() if '=' in r['objective'] else ''
        data[(run, k)] = obj if r['status'] == 'OPTIMAL' else r['status']
print('| country | scenario | ' + ' | '.join(runs) + ' |')
print('|---|---|' + '---:|' * len(runs))
for k in order:
    cells = [data.get((run, k), '') for run in runs]
    mark = [c if i == 0 or c == cells[0] else f'{c} (changed)' for i, c in enumerate(cells)]
    print(f'| {k[0]} | {k[1]} | ' + ' | '.join(mark) + ' |')
