"""Shared helpers for the proposal builders of LAC_FIX_RUN2 (draft, not yet run).
Proposal builders read only the base snapshot (scripts/make_base_snapshot.sh), never the working tree."""
import os, csv
from openpyxl.utils import get_column_letter
from common import JOB

BASEDIR = os.environ.get('LAC_BASE', 'C:/clw_base_4ba69d6')
PROP_FIELDS = ['country', 'workbook', 'sheet', 'row', 'column', 'year', 'Tech', 'Parameter', 'scenario', 'current_value',
               'new_value', 'new_formula', 'kind', 'decision', 'source_ids', 'derivation', 'assumption']


def write_part(name, rows):
    os.makedirs(f'{JOB}/proposals_parts', exist_ok=True)
    p = f'{JOB}/proposals_parts/{name}.csv'
    with open(p, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=PROP_FIELDS, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in PROP_FIELDS})
    print('wrote', len(rows), 'rows to', p)


def col_letter(n):
    return get_column_letter(n)
