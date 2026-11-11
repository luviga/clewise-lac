"""R6: compute the least change in B1_Scenario_Config.xlsx that makes NDCNEW and LTSNEW reproduce
the BAU history (years up to 2024).

Rule: only NDCNEW / LTSNEW rows that write a history year are touched, and only their history
values change. The target for a history year is the value BAU ends up with in B1_Output_Params
for the same parameter and set (or the B1 default when BAU has no entry).
- Year-column sheets (Efficiency, SmartGrid, EmissionsActivityRatio), Method Exact: the history
  year cells take the BAU value.
- Electrical sheet, exact-year lists: the history years get exact values equal to BAU / Security_Multiplier;
  where the row interpolates across 2024 (first exact year in history, next known point after 2025),
  2025 is added as an exact year with the value the row already gives it, so every year from 2025 on
  is unchanged.
Run: py -I scripts/r6_build.py <root> <bau_b1_root> <out_csv>
"""
import os, sys, glob
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

ROOT, BROOT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MODELS = {
    'CostaRica': 'CostaRica/CR_ENERGY/t1_confection',
    'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
    'Ecuador': 'Ecuador/ECU_Energy',
    'Guatemala': 'Guatemala/GUA_ENERGY',
    'Honduras': 'Honduras/HON_ENERGY',
    'Jamaica': 'Jamaica/JAM_ENERGY',
}
SC = ['NDCNEW', 'LTSNEW']
HIST_END = 2024


def load_bau(model):
    frames = []
    for f in glob.glob(os.path.join(BROOT, model, 'B1_Output_Params', 'BAU', '*.csv')):
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        if 'Value' in d.columns and 'PARAMETER' in d.columns:
            for k in ['TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'TIMESLICE']:
                if k not in d.columns: d[k] = ''
            frames.append(d[['PARAMETER', 'TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'TIMESLICE', 'YEAR', 'Value']])
    x = pd.concat(frames, ignore_index=True)
    x['YEAR'] = pd.to_numeric(x.YEAR, errors='coerce')
    x['v'] = pd.to_numeric(x.Value, errors='coerce')
    return x


def defaults(model):
    d = pd.read_excel(os.path.join(ROOT, model, 'B1_Default_Param.xlsx'))
    return dict(zip(d.iloc[:, 0], d.iloc[:, 1]))


def interp(time_range, known_years, known_values):
    """Same as B1 linear_interpolation_time_series: 0 before the first known year, np.interp, flat after the last."""
    min_t = min(known_years)
    xp, fp, fill = [], [], []
    for t, y in enumerate(time_range):
        if y in known_years or y < min_t:
            xp.append(t)
            fp.append(0.0 if y < min_t else float(known_values[known_years.index(y)]))
        else:
            fill.append(t)
    filled = list(np.interp(fill, xp, fp)) if fill else []
    out = []
    for t in range(len(time_range)):
        out.append(fp[xp.index(t)] if t in xp else filled[fill.index(t)])
    return out


def fmt(v):
    s = repr(float(v))
    if s.endswith('.0'): s = s[:-2]
    return s


changes, notes = [], []
for c, model in MODELS.items():
    bau = load_bau(model)
    dflt = defaults(model)
    years_all = sorted(int(y) for y in bau.YEAR.dropna().unique())
    time_range = years_all
    hist = [y for y in time_range if y <= HIST_END]

    def bau_series(par, tech='', fuel='', emis=''):
        s = bau[bau.PARAMETER == par]
        if tech: s = s[s.TECHNOLOGY == tech]
        if fuel: s = s[s.FUEL == fuel]
        if emis: s = s[s.EMISSION == emis]
        if s.TIMESLICE.nunique() > 1 or s.MODE_OF_OPERATION.nunique() > 1:
            return None
        return dict(zip(s.YEAR.astype(int), s.v))

    path = os.path.join(ROOT, model, 'B1_Scenario_Config.xlsx')
    wb = openpyxl.load_workbook(path, data_only=True)
    for ws in wb.worksheets:
        hdr = [ws.cell(1, j).value for j in range(1, ws.max_column + 1)]
        if 'Scenario' not in hdr: continue
        ic = {h: j + 1 for j, h in enumerate(hdr) if h is not None}
        ycols = {int(h): j for h, j in ic.items() if isinstance(h, (int, float)) and 2015 <= int(h) <= 2060}
        seen = set()
        for r in range(2, ws.max_row + 1):
            sc = ws.cell(r, ic['Scenario']).value
            if sc not in SC: continue
            par = ws.cell(r, ic['Parameter']).value if 'Parameter' in ic else None
            if ws.title in ('Distance_Levers', 'Mode_Shift', 'Occupancy_Rate', 'Tech_Adoption', 'T_Elasticity'): continue
            # ---------------- Electrical (exact-year lists) ----------------
            if 'Exact_Years' in ic:
                tech = ws.cell(r, ic['Tech_Set']).value
                key = (ws.title, sc, tech, par)
                if key in seen:
                    notes.append(dict(country=c, sheet=ws.title, row=r, note=f'duplicate row for {sc} {par} {tech}: B1 uses only the first one; not changed'))
                    continue
                seen.add(key)
                ey = str(ws.cell(r, ic['Exact_Years']).value).replace(' ', '')
                ev = str(ws.cell(r, ic['Exact_Values']).value).replace(' ', '')
                meth = str(ws.cell(r, ic['Method']).value).replace(' ', '')
                if ey == 'intact':
                    yini = ws.cell(r, ic['y_ini']).value
                    if yini is not None and float(yini) < HIST_END:
                        notes.append(dict(country=c, sheet=ws.title, row=r, note=f'intact row with y_ini {yini} before 2024 ({sc} {par} {tech}); not changed'))
                    continue
                eys = [int(float(x)) for x in ey.split(';') if x]
                evs = [float(x) for x in ev.split(';') if x]
                if not any(y <= HIST_END for y in eys): continue
                my = [int(float(x)) for x in str(ws.cell(r, ic['Milestone_Years']).value).replace(' ', '').split(';') if x not in ('', 'None', 'nan')]
                mv = [float(x) for x in str(ws.cell(r, ic['Milestone_Value']).value).replace(' ', '').split(';') if x not in ('', 'None', 'nan')]
                sec = ws.cell(r, ic['Security_Multiplier']).value
                sec = 1.0 if sec in (None, '') else float(sec)
                if 'Fix_Indicated' in meth or 'Interpolate_Escalate' in meth:
                    notes.append(dict(country=c, sheet=ws.title, row=r, note=f'method {meth} not handled ({sc} {par} {tech}); not changed'))
                    continue
                if par == 'CapacityFactor':
                    notes.append(dict(country=c, sheet=ws.title, row=r, note=f'CapacityFactor row ({sc} {tech}) has a time-slice dimension; checked separately'))
                    continue
                known_y = [float(y) for y in eys] + [float(y) for y in my]
                known_v = evs + mv
                old = interp(time_range, known_y, known_v)  # before the multiplier
                tgt = bau_series(par, tech=tech)
                newmap = {}
                for y in hist:
                    b = tgt.get(y) if tgt else None
                    if b is None or pd.isna(b):
                        b = float(dflt.get(par, 0.0))
                    newmap[y] = b / sec
                # keep every year after 2024 as it is
                for y, v in zip(eys, evs):
                    if y > HIST_END: newmap[y] = v
                # anchor every year of the segment that crosses 2024 at the value the row already gives it
                later = sorted(y for y in eys + my if y > HIST_END)
                stop = later[0] if later else 2026
                for y in range(HIST_END + 1, stop):
                    if y in time_range and y not in eys and y not in my:
                        newmap[y] = old[time_range.index(y)]
                ny = sorted(newmap)
                nv = [newmap[y] for y in ny]
                new = interp(time_range, [float(y) for y in ny] + [float(y) for y in my], nv + mv)
                # check: no change after 2024, history equals BAU after the multiplier and rounding
                for t, y in enumerate(time_range):
                    if y > HIST_END:
                        assert new[t] == old[t] or abs(round(new[t] * sec, 4) - round(old[t] * sec, 4)) < 1e-9, (c, r, y, new[t], old[t])
                hist_change = any(abs(round(new[time_range.index(y)] * sec, 4) - round(old[time_range.index(y)] * sec, 4)) > 1e-9 for y in hist)
                if not hist_change: continue
                new_ey = ' ; '.join(str(y) for y in ny)
                new_ev = ' ; '.join(fmt(v) for v in nv)
                changes.append(dict(country=c, file=model + '/B1_Scenario_Config.xlsx', sheet=ws.title, row=r,
                                    column=get_column_letter(ic['Exact_Years']), header='Exact_Years', scenario=sc, parameter=par, set=tech,
                                    old=ws.cell(r, ic['Exact_Years']).value, new=new_ey, kind='electrical_list'))
                changes.append(dict(country=c, file=model + '/B1_Scenario_Config.xlsx', sheet=ws.title, row=r,
                                    column=get_column_letter(ic['Exact_Values']), header='Exact_Values', scenario=sc, parameter=par, set=tech,
                                    old=ws.cell(r, ic['Exact_Values']).value, new=new_ev, kind='electrical_list'))
                continue
            # ---------------- year-column sheets ----------------
            if not ycols: continue
            meth = ws.cell(r, ic['Method']).value if 'Method' in ic else None
            st = ws.cell(r, ic.get('Set', ic.get('Tech_Set'))).value
            if meth != 'Exact':
                if any(ws.cell(r, ycols[y]).value is not None for y in ycols if y <= HIST_END):
                    notes.append(dict(country=c, sheet=ws.title, row=r, note=f'method {meth} with history values ({sc} {par} {st}); not changed'))
                continue
            if par == 'EmissionActivityRatio':
                if 'Set2' in ic:
                    tech, emis = st, ws.cell(r, ic['Set2']).value
                else:
                    tech, emis = [s.strip() for s in str(st).split(';')]
                tgt = bau_series(par, tech=tech, emis=emis)
            elif par == 'SpecifiedAnnualDemand':
                tgt = bau_series(par, fuel=st)
            else:
                si = ws.cell(r, ic['Set_Index']).value if 'Set_Index' in ic else 't'
                tgt = bau_series(par, tech=st) if si == 't' else bau_series(par, fuel=st)
            if tgt is None:
                notes.append(dict(country=c, sheet=ws.title, row=r, note=f'{par} {st} has several modes or time slices in BAU; not changed'))
                continue
            for y in sorted(ycols):
                if y > HIST_END: continue
                cell = ws.cell(r, ycols[y])
                if cell.value is None: continue
                b = tgt.get(y)
                if b is None or pd.isna(b):
                    b = float(dflt.get(par, 0.0))
                try:
                    cur = float(cell.value)
                except (TypeError, ValueError):
                    continue
                if abs(round(cur, 4) - round(b, 4)) > 1e-9:
                    changes.append(dict(country=c, file=model + '/B1_Scenario_Config.xlsx', sheet=ws.title, row=r,
                                        column=get_column_letter(ycols[y]), header=y, scenario=sc, parameter=par, set=st,
                                        old=cell.value, new=b, kind='year_column'))
pd.DataFrame(changes).to_csv(OUT, index=False)
pd.DataFrame(notes).to_csv(OUT.replace('.csv', '_notes.csv'), index=False)
ch = pd.DataFrame(changes)
print('cells', len(ch))
if len(ch):
    print(ch.groupby(['country', 'sheet', 'kind']).agg(cells=('row', 'size'), rows=('row', 'nunique')).to_string())
print(pd.DataFrame(notes).to_string() if notes else 'no notes')
