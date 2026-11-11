"""R6, emission factors: NDCNEW and LTSNEW rows for EmissionActivityRatio pairs that only BAU calibrates in history.

For every (technology, emission) whose B1 EmissionActivityRatio differs between BAU and NDCNEW or LTSNEW in 2018 to
2024 (r6_history_after.csv), and where the config has an 'Exact' BAU row but no row for that scenario, a copy of
the BAU row is appended to the same sheet for the scenario. Its year cells: the BAU value of B1_Output_Params up to
2024, and the scenario's current value of B1_Output_Params from 2025 (B1 writes every year of an Exact row, so the
values from 2025 on must be the ones the scenario already has; nothing after 2024 changes).
Writes scripts/r6_ear_rows.csv (one row per cell) and r6_ear_rows_notes.csv; --apply writes the configs.
Run: py -I scripts/r6_ear_rows.py <countries...> [--apply]
"""
import glob, os, sys
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

ROOT = r'C:\clw_fix'
JOB = os.path.join(ROOT, '_LAC_HUB', 'fix_run_20261111T200825Z')
sys.path.insert(0, ROOT)
M = {'CostaRica': 'CostaRica/CR_ENERGY/t1_confection', 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY', 'Ecuador': 'Ecuador/ECU_Energy',
     'Guatemala': 'Guatemala/GUA_ENERGY', 'Honduras': 'Honduras/HON_ENERGY', 'Jamaica': 'Jamaica/JAM_ENERGY'}
APPLY = '--apply' in sys.argv
COUNTRIES = [a for a in sys.argv[1:] if a in M]
H = pd.read_csv(os.path.join(JOB, 'r6_history_after.csv'), dtype=str, keep_default_na=False)
H = H[(H.parameter == 'EmissionActivityRatio') & (H.stage == 'B1_Output_Params') & (H.presence == 'both')]


def b1(model, scen):
    d = pd.read_csv(os.path.join(ROOT, model, 'B1_Output_Params', scen, 'EmissionActivityRatio.csv'), dtype=str, keep_default_na=False)
    d['y'] = d.YEAR.astype(int)
    return d


cells, notes = [], []
for c in COUNTRIES:
    model = M[c]
    h = H[H.country == c]
    pairs = sorted({(r.technology, r.emission, r.scenario) for r in h.itertuples()
                    if abs(float(r.bau) - float(r.scen)) > 1e-9 * max(1.0, abs(float(r.bau)))})
    if not pairs:
        continue
    out = {s: b1(model, s) for s in ('BAU', 'NDCNEW', 'LTSNEW')}
    path = os.path.join(ROOT, model, 'B1_Scenario_Config.xlsx')
    wb = openpyxl.load_workbook(path, data_only=False)
    # index every EmissionActivityRatio row: (sheet, scenario, tech, emission) -> row
    idx, layout = {}, {}
    for ws in wb.worksheets:
        hdr = [ws.cell(1, j).value for j in range(1, ws.max_column + 1)]
        if 'Scenario' not in hdr or 'Parameter' not in hdr:
            continue
        ic = {v: j + 1 for j, v in enumerate(hdr) if v is not None}
        ycols = {int(v): j + 1 for j, v in enumerate(hdr) if isinstance(v, (int, float)) and 2015 <= int(v) <= 2060}
        if not ycols:
            continue
        layout[ws.title] = (ic, ycols)
        for r in range(2, ws.max_row + 1):
            if ws.cell(r, ic['Parameter']).value != 'EmissionActivityRatio':
                continue
            sc = ws.cell(r, ic['Scenario']).value
            st = str(ws.cell(r, ic['Set'] if 'Set' in ic else ic['Tech_Set']).value)
            if 'Set2' in ic:
                tech, em = st.strip(), str(ws.cell(r, ic['Set2']).value).strip()
            else:
                parts = [x.strip() for x in st.split(';')]
                if len(parts) != 2:
                    continue  # a row of another layout (one set only); not an emission-factor pair
                tech, em = parts
            idx.setdefault((ws.title, sc, tech, em), r)
    next_row = {ws.title: ws.max_row for ws in wb.worksheets}
    for tech, em, scen in pairs:
        bau_rows = [(sh, r) for (sh, sc, t, e), r in idx.items() if sc == 'BAU' and t == tech and e == em]
        own = [(sh, r) for (sh, sc, t, e), r in idx.items() if sc == scen and t == tech and e == em]
        if not bau_rows:
            notes.append(dict(country=c, scenario=scen, tech=tech, emission=em, note='no BAU EmissionActivityRatio row in the config; not changed'))
            continue
        if own:
            notes.append(dict(country=c, scenario=scen, tech=tech, emission=em, note=f'{scen} already has a row {own}; not changed'))
            continue
        sh, br = bau_rows[0]
        ws = wb[sh]
        ic, ycols = layout[sh]
        if ws.cell(br, ic['Method']).value != 'Exact':
            notes.append(dict(country=c, scenario=scen, tech=tech, emission=em, note=f'BAU row {sh} {br} method {ws.cell(br, ic["Method"]).value}; not changed'))
            continue
        ob = out['BAU'][(out['BAU'].TECHNOLOGY == tech) & (out['BAU'].EMISSION == em)]
        osn = out[scen][(out[scen].TECHNOLOGY == tech) & (out[scen].EMISSION == em)]
        if ob.MODE_OF_OPERATION.nunique() > 1 or osn.MODE_OF_OPERATION.nunique() > 1:
            notes.append(dict(country=c, scenario=scen, tech=tech, emission=em, note='several modes of operation; not changed'))
            continue
        vb = dict(zip(ob.y, ob.Value)); vs = dict(zip(osn.y, osn.Value))
        next_row[sh] += 1
        nr = next_row[sh]
        for j in range(1, ws.max_column + 1):
            src = ws.cell(br, j).value
            hdrv = ws.cell(1, j).value
            if j == ic['Scenario']:
                v = scen
            elif j in ycols.values():
                y = [k for k, jj in ycols.items() if jj == j][0]
                if y <= 2024:
                    v = float(vb[y]) if y in vb else src
                else:
                    v = float(vs[y]) if y in vs else src
            else:
                v = src
            if v is None:
                continue
            cells.append(dict(country=c, workbook=f'{model}/B1_Scenario_Config.xlsx', sheet=sh, row=nr, column=get_column_letter(j),
                              header=hdrv, scenario=scen, tech=tech, emission=em, bau_row=br, value=v))
            if APPLY:
                assert ws.cell(nr, j).value is None
                ws.cell(nr, j).value = v
    if APPLY and any(x['country'] == c for x in cells):
        from ao_safe_save import save_ao_safely
        save_ao_safely(wb, path)
    wb.close()
cd = pd.DataFrame(cells)
suffix = '_'.join(COUNTRIES)
cd.to_csv(os.path.join(JOB, 'scripts', f'r6_ear_rows_{suffix}.csv'), index=False, lineterminator='\n')
pd.DataFrame(notes).to_csv(os.path.join(JOB, 'scripts', f'r6_ear_rows_{suffix}_notes.csv'), index=False, lineterminator='\n')
if len(cd):
    print(cd.groupby(['country', 'sheet', 'scenario']).agg(rows=('row', 'nunique'), cells=('row', 'size')).to_string())
print(pd.DataFrame(notes).to_string() if notes else 'no notes')
