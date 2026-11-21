"""Phase B: back up, then write every row of proposals.csv into the working tree of C:/clw_fix. Idempotent: a cell already
holding its target is skipped; a new row already present (same key) is skipped. Logs every write to logs/phaseB_write.log.

Kinds: ao_cell, demand_cell (number), ao_formula (formula text), config_cell (text), config_row (append a row to a sheet,
JSON dict by header), fhp_newrow (insert a row pair at the end of its block in Fixed Horizon Parameters, Tech.ID chain rebuilt),
csv_line (Stage 2 overwrite CSV: append a line; new_value = the full line).
Workbooks are saved with save_ao_safely (Excel recalculation, no formula cell without a value).
Run: py -I scripts/phaseB_write.py [--dry-run] [--only <workbook substring>]
"""
import csv, hashlib, json, os, shutil, sys, datetime
from pathlib import Path
import pandas as pd
import openpyxl

ROOT = Path('C:/clw_fix')
JOB = ROOT / '_LAC_HUB' / 'fix_run2_20261120T225823Z'
sys.path.insert(0, str(ROOT))
from ao_safe_save import save_ao_safely  # noqa: E402

DRY = '--dry-run' in sys.argv
ONLY = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
P = pd.read_csv(JOB / 'proposals.csv', dtype=str, keep_default_na=False)
if ONLY:
    P = P[P.workbook.str.contains(ONLY, regex=False)]
log = open(JOB / 'logs' / 'phaseB_write.log', 'a', encoding='utf-8', newline='\n')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    log.write(s + '\n')
    log.flush()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


say('=== phaseB_write', datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z', 'dry' if DRY else 'apply', ONLY or 'all')
files = sorted(set(P.workbook))
# ---------- backups (first run only per file) ----------
man = JOB / 'backups' / 'backup_manifest.csv'
old = {}
if man.exists():
    old = {r['file']: r for r in csv.DictReader(open(man, encoding='utf-8'))}
for f in files:
    src, dst = ROOT / f, JOB / 'backups' / f
    if f in old:
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not DRY:
        shutil.copy2(src, dst)
        old[f] = dict(file=f, sha256_before=sha(src), backup=str(dst.relative_to(JOB)).replace('\\', '/'), sha256_backup=sha(dst))
if not DRY and old:
    with open(man, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['file', 'sha256_before', 'backup', 'sha256_backup'], lineterminator='\n')
        w.writeheader()
        w.writerows(old.values())
say('backups in manifest:', len(old))


def close(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))


def hdr_of(ws):
    return {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1) if ws.cell(1, j).value is not None}


def last_row(ws):
    r = ws.max_row
    while r > 1 and all(ws.cell(r, j).value in (None, '') for j in range(1, min(ws.max_column, 6) + 1)):
        r -= 1
    return r


for wbpath, g in P[~P.kind.isin(['csv_line', 'd8_target', 'doc'])].groupby('workbook'):
    wb = openpyxl.load_workbook(ROOT / wbpath, data_only=False)
    n = skip = 0
    # cells first (row numbers refer to the base layout), new rows after
    for r in g[g.kind.isin(['ao_cell', 'demand_cell', 'ao_formula', 'config_cell', 'cfg_num'])].itertuples():
        ws = wb[r.sheet]
        rr = int(r.row)
        cell = ws[f'{r.column}{rr}']
        h = hdr_of(ws)
        tcol = 3 if r.kind == 'cfg_num' else h.get('Tech', h.get('Tech_Set', 2 if r.kind != 'config_cell' else 3))
        tech = ws.cell(rr, tcol).value
        assert str(tech).split(';')[0].strip() == r.Tech, (wbpath, r.sheet, rr, tech, r.Tech)
        cur = cell.value
        if r.kind in ('ao_cell', 'demand_cell', 'cfg_num'):
            if close(cur, r.new_value):
                skip += 1
                continue
            if r.current_value not in ('', 'None', 'nan') and not (isinstance(cur, str) and cur.startswith('=')):
                assert cur is None or close(cur, r.current_value), (wbpath, r.sheet, rr, r.column, cur, r.current_value)
            cell.value = float(r.new_value)
        elif r.kind == 'ao_formula':
            if cur == r.new_formula:
                skip += 1
                continue
            cell.value = r.new_formula
        else:
            if str(cur) == r.new_value:
                skip += 1
                continue
            assert str(cur).replace(' ', '') == r.current_value.replace(' ', ''), (wbpath, r.sheet, rr, str(cur)[:60])
            cell.value = r.new_value
        n += 1
        log.write(f'  {wbpath}|{r.sheet}|{r.column}{rr}|{r.Tech}|{r.Parameter}|{r.year}: {cur!r} -> '
                  f'{r.new_formula or r.new_value}\n')
    # appended rows (config sheets)
    for r in g[g.kind == 'config_row'].itertuples():
        ws = wb[r.sheet]
        rec = json.loads(r.new_value)
        h = hdr_of(ws)
        lr = last_row(ws)
        keyc = [k for k in ('Scenario', 'Parameter', 'Tech_Set') if k in h]
        exists = False
        for rr in range(2, lr + 1):
            if all(str(ws.cell(rr, h[k]).value) == str(rec[k]) for k in keyc) and \
                    str(ws.cell(rr, h['Description Parameter-Set'] if 'Description Parameter-Set' in h else 4).value) == \
                    str(rec.get('Description Parameter-Set', rec.get('Description Parameter-Set'))) and r.sheet == 'Electrical':
                exists = True
            if r.sheet == 'SmartGrid' and all(str(ws.cell(rr, h[k]).value) == str(rec[k]) for k in ('Scenario', 'Parameter', 'Tech_Set') if k in h):
                exists = True
        if exists:
            skip += 1
            continue
        nr = lr + 1
        for k, v in rec.items():
            key = int(k) if (k.isdigit() and int(k) in h) else k
            if key not in h:
                raise SystemExit(f'column {k} not in {wbpath} {r.sheet}')
            if isinstance(v, str) and v.replace('.', '', 1).isdigit() and r.sheet == 'SmartGrid':
                v = float(v)
            ws.cell(nr, h[key]).value = v
        n += 1
        log.write(f'  {wbpath}|{r.sheet}|new row {nr}|{rec.get("Scenario")}|{rec.get("Parameter")}|{rec.get("Tech_Set")}\n')
    # Fixed Horizon Parameters new row pairs
    fh = g[g.kind == 'fhp_newrow']
    if len(fh):
        ws = wb['Fixed Horizon Parameters']
        h = hdr_of(ws)
        have = {(ws.cell(rr, h['Tech']).value, ws.cell(rr, h['Parameter']).value) for rr in range(2, ws.max_row + 1)}
        for r in fh.itertuples():
            rec = json.loads(r.new_value)
            if (rec['Tech'], rec['Parameter']) in have:
                skip += 1
                continue
            types = [ws.cell(rr, h['Tech.Type']).value for rr in range(1, ws.max_row + 1)]
            pos = max(i for i, t in enumerate(types, start=1) if t == rec['Tech.Type']) + 1
            ws.insert_rows(pos)
            for k, v in rec.items():
                ws.cell(pos, h[k]).value = v
            have.add((rec['Tech'], rec['Parameter']))
            n += 1
            log.write(f'  {wbpath}|Fixed Horizon Parameters|inserted row {pos}|{rec["Tech"]}|{rec["Parameter"]}|{rec["Value"]}\n')
        # rebuild the Tech.ID chain: first row of a pair =B{r-2}+1, second =B{r-1}; row 2 holds 1
        idc = openpyxl.utils.get_column_letter(h['Tech.ID'])
        lr = last_row(ws)
        for rr in range(2, lr + 1):
            first = ws.cell(rr, h['Parameter.ID']).value in (1, '1')
            if rr == 2:
                v = 1
            elif first:
                v = f'={idc}{rr - 2}+1'
            else:
                v = f'={idc}{rr - 1}'
            ws.cell(rr, h['Tech.ID']).value = v
    say(f'{wbpath}: {n} writes, {skip} already at target')
    if n and not DRY:
        save_ao_safely(wb, ROOT / wbpath)
        say('  saved', wbpath)
    wb.close()

# ---------- Stage 2 overwrite CSV lines (appended, line ending of the file kept) ----------
for f, g in P[P.kind == 'csv_line'].groupby('workbook'):
    raw = open(ROOT / f, 'rb').read().decode('utf-8')
    eol = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.splitlines()
    add = [r.new_value for r in g.itertuples() if r.new_value not in lines]
    if add and not DRY:
        body = raw if raw.endswith(eol) else raw + eol
        open(ROOT / f, 'wb').write((body + eol.join(add) + eol).encode('utf-8'))
    say(f'{f}: {len(add)} lines appended, {len(g) - len(add)} already present')
log.close()
