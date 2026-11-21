"""A4: starter_kit_deviations.csv = the earlier rows plus one row per D12 life that differs from the CCG kit (kit values read
from the kit workbook here, by cell, not copied from the research note)."""
import csv, re
import openpyxl
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
EARLIER = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z'
KIT = EARLIER + '/downloads/ccg/Ecuador_Base_SAND.xlsm'
KITNAME = ('CCG Starter Data Kit: Ecuador v1.0 (Cannone, Allington et al. 2021), doi:10.5281/zenodo.5498094; data article '
           'doi:10.1016/j.dib.2022.108021')
MAP = {  # model tech -> kit tech (research/d12_lives.md Table 2, nearest kit class)
    'ELE_TRANS': 'PWRTRN', 'ELE_DIST': 'PWRDIST', 'PRONGS': 'MINNGS', 'PPBGS': 'PWRBIO001', 'PPBIM': 'PWRBIO001',
    'PPIBIM': 'PWRBIO001', 'PPCRU': 'PWROHC001', 'PPDSL': 'PWROHC001', 'PPRDSL': 'PWROHC001', 'PPDDSL': 'PWROHC003',
    'PPFOI': 'PWROHC001', 'PPDFOI': 'PWROHC001', 'PPILPG': 'PWROHC001', 'PPNGS': 'PWRNGS001', 'PPRNGS': 'PWRNGS002',
    'PPGEO': 'PWRGEO', 'PPHDAMAB': 'PWRHYD001', 'PPHRORAB': 'PWRHYD001', 'PPHDAMAM': 'PWRHYD001', 'PPHDAMPM': 'PWRHYD001',
    'PPHRORAM': 'PWRHYD001', 'PPHRORPM': 'PWRHYD001', 'PPHDAMAS': 'PWRHYD002', 'PPHDAMPS': 'PWRHYD002', 'PPHRORAS': 'PWRHYD002',
    'PPHRORPS': 'PWRHYD002', 'PPHD': 'PWRHYD003', 'PPIHD': 'PWRHYD004', 'PPWNDON': 'PWRWND001', 'PPWNDD': 'PWRWND001',
    'PPPVT': 'PWRSOL001', 'PPPVTS': 'PWRSOL001S', 'PPPVD': 'PWRSOL001', 'PPPVDS': 'PWRSOL002',
}
wb = openpyxl.load_workbook(KIT, read_only=True, data_only=True)
ws = wb['Parameters']
kit = {}
for i, r in enumerate(ws.iter_rows(min_row=31100, max_row=31200, max_col=10, values_only=True), start=31100):
    if r[0] == 'OperationalLife':
        kit[r[2]] = (r[9], f'J{i}')
P = pd.read_csv(JOB + '/proposals.csv', dtype=str, keep_default_na=False) if False else None
props = pd.read_csv(JOB + '/proposals_parts/d12.csv', dtype=str, keep_default_na=False)
props = props[props.Parameter == 'OperationalLife']
rows = list(csv.DictReader(open(EARLIER + '/starter_kit_deviations.csv', encoding='utf-8')))
fields = list(rows[0].keys())
added = 0
for _, p in props.iterrows():
    life = float(p.new_value) if p.kind == 'ao_cell' else float(__import__('json').loads(p.new_value)['Value'])
    if p.Tech not in MAP:
        rows.append(dict(kit=KITNAME, kit_file_cell='no kit technology for this class', parameter='OperationalLife',
                         technology=p.Tech, kit_value='none', model_value=f'{life:g} years',
                         reason='The kit has no technology of this class; the life comes from the next source level (' +
                                p.derivation + ').', model_source_ids=p.source_ids, decision_date='2026-11-20'))
        added += 1
        continue
    kv, cell = kit[MAP[p.Tech]]
    if abs(float(kv) - life) < 1e-9:
        continue
    rows.append(dict(kit=KITNAME, kit_file_cell=f'Ecuador Base SAND.xlsm, sheet Parameters, cell {cell} (OperationalLife, '
                                               f'{MAP[p.Tech]})', parameter='OperationalLife',
                     technology=f'{p.Tech} (kit {MAP[p.Tech]})', kit_value=f'{kv:g} years', model_value=f'{life:g} years',
                     reason='A national Ecuador document of higher rank states the life for this class: ' + p.derivation +
                            ' (decision D12 source order: national documents before the kit).' if 'CCG' not in p.source_ids else p.derivation,
                     model_source_ids=p.source_ids, decision_date='2026-11-20'))
    added += 1
with open(JOB + '/starter_kit_deviations.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print('earlier', len(rows) - added, 'added', added)
