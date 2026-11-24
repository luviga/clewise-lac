"""Pipeline step after the B1 runs and before Stage 0: rules that every solver data file of the stage pipeline
receives. It rewrites Executables/{scenario}_0/{scenario}_0.txt of each country; Stage 0 and Stage 3 copy these
files, so every Stage 0 and Stage 3 solve carries the rules. The rules hold no values: names and years come from
the tables read by lac_tables.py.

  hydrogen   every technology of group `hydrogen` of config/scenarios/technology_types.csv (production,
             distribution, vehicles and end uses that take or give a hydrogen fuel) gets an activity upper limit
             of 0 in every year, and every activity lower limit it has is set to 0 (removed).
  history    every value of a policy scenario in a year up to history_end_year (stage_controller.csv) equals the
             BAU value of the same parameter, indices and year (history is the same in every scenario). A row
             that BAU lacks takes the parameter default in those years; a BAU row that the policy file lacks is
             added with the BAU history and the default in later years.

Usage:  py scenario_rules.py --root .   [--countries ...]
Writes _STAGE0_OUTPUT/SCENARIO_RULES_LOG.csv (country, scenario, rule, parameter, values changed).
"""
import argparse
import csv
import re
from pathlib import Path

import lac_tables as LT

YEAR_RE = re.compile(r'^\d{4}$')


def _fmt(v):
    if float(v) == int(v) and abs(v) < 1e12:
        return str(int(v))
    return f"{v:.6f}".rstrip("0").rstrip(".")


def region_of(content):
    m = re.search(r"set REGION\s*:=\s*(\S+)\s*;", content)
    return m.group(1) if m else None


def years_of(content):
    m = re.search(r"set YEAR\s*:=\s*([^;]+);", content)
    return [int(y) for y in m.group(1).split()] if m else []


def techs_in_file(content):
    m = re.search(r"set TECHNOLOGY\s*:=\s*([^;]+);", content)
    return set(m.group(1).split()) if m else set()


def _bounds(content, param):
    m = re.search(rf"param\s+{re.escape(param)}\s+default\s+\S+\s*:=?", content)
    if not m:
        return None
    end = content.find("\n;", m.end())
    if end == -1:
        return None
    return m.start(), end + 2


def blocks(content):
    """{param: (start, end, default)} of every parameter block."""
    out = {}
    for m in re.finditer(r"param\s+(\w+)\s+default\s+(\S+)\s*:=?", content):
        end = content.find("\n;", m.end())
        if end != -1:
            out[m.group(1)] = (m.start(), end + 2, float(m.group(2)))
    return out


def parse_block(text):
    """[(slice, years, {key: [values]})] of a block whose column headers are years (else [])."""
    out, cur_slice, years, rows = [], '', None, None
    for ln in text.split("\n")[1:]:
        s = ln.strip()
        if not s or s == ';':
            continue
        if s.startswith('[') and s.endswith(':'):
            cur_slice, years = s, None
            continue
        if s.endswith(':='):
            toks = s[:-2].split()
            if toks and all(YEAR_RE.match(t) for t in toks):
                years, rows = [int(t) for t in toks], {}
                out.append((cur_slice, years, rows))
            else:
                years = None
            continue
        if years is not None:
            parts = s.split()
            if len(parts) == len(years) + 1:
                rows[parts[0]] = parts[1:]
    return out


def set_rows(content, param, rows, years, region, only_existing=False):
    """rows: {name: {year: value}} of a two-index block ([R,*,*]: rows by name, columns by year). Existing rows get
    the given years replaced; missing rows are added (years not given take the block default) unless
    only_existing; an empty block gets its header. Returns (content, values changed)."""
    b = _bounds(content, param)
    if b is None or not rows:
        return content, 0
    start, end = b
    block = content[start:end]
    default = float(re.match(rf"param\s+{re.escape(param)}\s+default\s+(\S+)", block).group(1))
    lines = block.split("\n")
    hdr_i = next((i for i, ln in enumerate(lines)
                  if ln.strip().endswith(":=") and not ln.strip().startswith("param")), None)
    changed = 0
    if hdr_i is None:
        if only_existing:
            return content, 0
        new = [lines[0].rstrip(), f"[{region},*,*]:", " ".join(str(y) for y in years) + " :="]
        for name in sorted(rows):
            changed += sum(1 for y in years if y in rows[name])
            new.append(name + " " + " ".join(_fmt(rows[name].get(y, default)) for y in years) + " ")
        new.append(";")
        return content[:start] + "\n".join(new) + "\n" + content[end:], changed
    yrs = [int(x) for x in lines[hdr_i].replace(":=", "").split()]
    seen, out = set(), []
    for i, ln in enumerate(lines):
        parts = ln.split()
        if i > hdr_i and len(parts) == len(yrs) + 1 and parts[0] in rows:
            name = parts[0]
            seen.add(name)
            vals = parts[1:]
            for j, y in enumerate(yrs):
                if y in rows[name] and abs(float(vals[j]) - rows[name][y]) > 1e-12:
                    vals[j] = _fmt(rows[name][y])
                    changed += 1
            out.append(name + " " + " ".join(vals) + " ")
            continue
        if ln.strip() == ";" and not only_existing:
            for name in sorted(set(rows) - seen):
                changed += sum(1 for y in yrs if y in rows[name] and abs(rows[name][y] - default) > 1e-12)
                out.append(name + " " + " ".join(_fmt(rows[name].get(y, default)) for y in yrs) + " ")
        out.append(ln)
    return content[:start] + "\n".join(out) + content[end:], changed


def apply_hydrogen(content, country):
    """Hydrogen technologies: activity upper limit 0 in every year, activity lower limits set to 0."""
    try:
        h2 = set(LT.techs('hydrogen', country))
    except KeyError:
        return content, []
    h2 &= techs_in_file(content)
    if not h2:
        return content, []
    yrs, reg = years_of(content), region_of(content)
    zero = {t: {y: 0.0 for y in yrs} for t in sorted(h2)}
    content, nu = set_rows(content, 'TotalTechnologyAnnualActivityUpperLimit', zero, yrs, reg)
    content, nl = set_rows(content, 'TotalTechnologyAnnualActivityLowerLimit', zero, yrs, reg, only_existing=True)
    return content, [('hydrogen', 'TotalTechnologyAnnualActivityUpperLimit', nu),
                     ('hydrogen', 'TotalTechnologyAnnualActivityLowerLimit', nl)]


def apply_history(content, base_content, last_year):
    """Policy values of years up to last_year take the BAU values (see the module text)."""
    log = []
    pb, bb = blocks(content), blocks(base_content)
    for param in sorted(pb, key=lambda p: -pb[p][0]):   # from the end, so earlier offsets stay valid
        if param not in bb:
            continue
        ps, pe, default = pb[param]
        bs, be, _ = bb[param]
        ptext, btext = content[ps:pe], base_content[bs:be]
        pslices, bslices = parse_block(ptext), parse_block(btext)
        if not pslices and not bslices:
            continue
        bmap = {}
        for sl, yrs, rows in bslices:
            for k, vals in rows.items():
                bmap[(sl, k)] = dict(zip(yrs, vals))
        dflt = _fmt(default)
        changed = 0
        seen = set()
        lines = ptext.split("\n")
        out, cur_slice, years = [], '', None
        pslice_names = {sl for sl, _, _ in pslices}
        pending = {}   # slice -> rows of BAU missing in the policy file
        prow_keys = {(sl, k) for sl, _, rows in pslices for k in rows}
        for (sl, k), bv in bmap.items():
            if (sl, k) not in prow_keys and any(y <= last_year and abs(float(v) - default) > 1e-12
                                                for y, v in bv.items()):
                pending.setdefault(sl, []).append(k)

        def flush(sl, yrs):
            nonlocal changed
            rows = []
            for k in sorted(pending.pop(sl, [])):
                bv = bmap[(sl, k)]
                vals = [bv.get(y, dflt) if y <= last_year else dflt for y in yrs]
                changed += sum(1 for y in yrs if y <= last_year and abs(float(bv.get(y, dflt)) - default) > 1e-12)
                rows.append(k + " " + " ".join(vals) + " ")
            return rows

        for i, ln in enumerate(lines):
            s = ln.strip()
            if i > 0 and ((s.startswith('[') and s.endswith(':')) or s == ';'):
                if years is not None and cur_slice in pending:
                    out.extend(flush(cur_slice, years))
                if s.startswith('['):
                    cur_slice, years = s, None
                out.append(ln)
                continue
            if i > 0 and s.endswith(':='):
                toks = s[:-2].split()
                years = [int(t) for t in toks] if toks and all(YEAR_RE.match(t) for t in toks) else None
                out.append(ln)
                continue
            parts = s.split()
            if i > 0 and years is not None and len(parts) == len(years) + 1:
                k, vals = parts[0], parts[1:]
                bv = bmap.get((cur_slice, k))
                for j, y in enumerate(years):
                    if y > last_year:
                        continue
                    want = bv.get(y, dflt) if bv is not None else dflt
                    if abs(float(vals[j]) - float(want)) > 1e-12:
                        vals[j] = want
                        changed += 1
                out.append(k + " " + " ".join(vals) + " ")
                continue
            out.append(ln)
        # BAU slices that the policy file lacks: added at the block end
        extra = []
        for sl in sorted(set(pending) - pslice_names):
            yrs = sorted({y for (s2, k) in bmap for y in bmap[(s2, k)] if s2 == sl})
            rows = flush(sl, yrs)
            if rows:
                extra += ([sl] if sl else []) + [" ".join(str(y) for y in yrs) + " :="] + rows
        if extra:
            j = len(out) - 1
            while j >= 0 and out[j].strip() != ';':
                j -= 1
            out = out[:j] + extra + out[j:]
        if changed:
            content = content[:ps] + "\n".join(out) + content[pe:]
            log.append(('history', param, changed))
    return content, log


def _read(p):
    with open(p, 'r', encoding='utf-8', errors='replace', newline='') as fh:
        c = fh.read()
    return c.replace('\r\n', '\n'), '\r\n' in c


def _write(p, content, crlf):
    if crlf:
        content = content.replace('\n', '\r\n')
    with open(p, 'w', encoding='utf-8', newline='') as fh:
        fh.write(content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--countries', nargs='*', default=[])
    a = ap.parse_args()
    root = Path(a.root).resolve()
    last = LT.controller('history_end_year')
    base = LT.scenario('base')
    rows = []
    for c in LT.countries():
        if a.countries and c not in a.countries:
            continue
        ex = root / Path(*LT.model_path(c).split('/')) / 'Executables'
        bpath = ex / f'{base}_0' / f'{base}_0.txt'
        if not bpath.exists():
            print(f'[SKIP] {c}: no {bpath.name}')
            continue
        bcontent, bcrlf = _read(bpath)
        bcontent, lg = apply_hydrogen(bcontent, c)
        _write(bpath, bcontent, bcrlf)
        rows += [(c, base) + r for r in lg]
        for sc in LT.scenarios('policy'):
            p = ex / f'{sc}_0' / f'{sc}_0.txt'
            if not p.exists():
                continue
            content, crlf = _read(p)
            content, lg1 = apply_hydrogen(content, c)
            content, lg2 = apply_history(content, bcontent, last)
            _write(p, content, crlf)
            rows += [(c, sc) + r for r in lg1 + lg2]
        print(c, 'done:', sum(r[4] for r in rows if r[0] == c), 'values changed')
    out = root / '_STAGE0_OUTPUT' / 'SCENARIO_RULES_LOG.csv'
    out.parent.mkdir(exist_ok=True)
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['country', 'scenario', 'rule', 'parameter', 'values_changed'])
        w.writerows(rows)
    print('[Wrote]', out)


if __name__ == '__main__':
    main()
