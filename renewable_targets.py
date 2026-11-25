"""Renewable share targets of the policy scenarios, built each run from inputs/scenarios/scenario_values.csv.

Two kinds of published rows give a target:
  renewable_share          a share of generation (fraction) in a year, written as published;
  new_renewable_capacity   capacity (MW) of one plant kind added after the anchor year by a year; the rule
                           below turns the rows of one (country, scenario, year) into a share.

Capacity rule (one rule for every country; its constants are rows of config/scenarios/rules/stage_controller.csv):
  share(y) = (G_ren + sum over rows of MW / capacity_mw_per_gw * CF_kind * capacity_pj_per_gw_year) / D(y)
  G_ren    model generation of the renewable plants (hydro and non-hydro renewable classes) in the anchor year
           (Stage 0 recommended share of the anchor year times the Stage 0 generation of that year), PJ
  (a share above max_target_share is capped at it)
  CF_kind  capacity factor times availability factor of the plant kind in the anchor year: the mean over the
           plants of the kind (technology_types.csv group capacity_kind_<kind>, plants of group stage0_bypass
           left out), weighted by their anchor-year generation, or the plain mean when none generates
  D(y)     Stage 0 total generation of the scenario in the target year, PJ
A share of a year with both kinds of rows comes from the renewable_share row.

Curve: no target in or before the cutoff year; straight line from the scenario's renewable share in the cutoff
year to the first target year and between target years; the last target held after its year. A country and
scenario without rows has no curve (the policy scenario takes the BAU shares).

Stage 1 builds the curves and writes them to _STAGE1_OUTPUT/RENEWABLE_TARGETS.csv; Stage 2, the Stage 3
results and the tests read that file through load().
"""
import csv
from pathlib import Path

import lac_tables as LT

SHARE_LEVER = 'renewable_share'
CAPACITY_LEVER = 'new_renewable_capacity'
FILE_NAME = 'RENEWABLE_TARGETS.csv'
FIELDS = ['country', 'scenario', 'year', 'value', 'basis', 'value_ids', 'derivation']


def _rows(lever):
    return [r for r in LT._value_rows() if r['lever'] == lever]


def capacity_kind_techs(kind, techs):
    """Plants of a capacity kind (name tokens of group capacity_kind_<kind>), bypass plants left out when others
    exist."""
    toks = LT.techs('capacity_kind_' + kind)
    found = [t for t in techs if any(tok in str(t).upper() for tok in toks)]
    bypass = set(LT.techs('stage0_bypass'))
    main = [t for t in found if t not in bypass]
    return main or found


def build(country, scenarios, techs, renewable_techs, anchor_gen, cf_af, denominator):
    """Targets of one country.
    techs: power plants of the country; renewable_techs: those of the hydro and non-hydro renewable classes;
    anchor_gen(tech, scenario) -> PJ in the anchor year; cf_af(tech, scenario) -> CF x AF in the anchor year;
    denominator(scenario, year) -> PJ. Returns {scenario: {year: (value, basis, value_ids, derivation)}}."""
    mw_per_gw = LT.controller('capacity_mw_per_gw', '1')
    pj_per_gw = LT.controller('capacity_pj_per_gw_year', '1')
    digits = LT.controller('share_digits', '1')
    out = {}
    for sc in scenarios:
        cur = {}
        for r in _rows(SHARE_LEVER):
            if r['country'] == country and r['scenario'] == sc:
                cur[int(r['year'])] = (float(r['value']), 'published share', r.get('value_id', ''),
                                       f"{r['value']} as published ({r.get('source_id', '')})")
        cap = {}
        for r in _rows(CAPACITY_LEVER):
            if r['country'] == country and r['scenario'] == sc:
                cap.setdefault(int(r['year']), []).append(r)
        for y, rows in sorted(cap.items()):
            if y in cur:
                continue
            g_ren = sum(anchor_gen(t, sc) for t in renewable_techs)
            parts, add, ids = [], 0.0, []
            for r in rows:
                kind = r['lever_kind']
                kt = capacity_kind_techs(kind, techs)
                w = [(t, anchor_gen(t, sc)) for t in kt]
                wsum = sum(g for _, g in w)
                if wsum > 0:
                    cf = sum(cf_af(t, sc) * g for t, g in w) / wsum
                else:
                    cf = sum(cf_af(t, sc) for t in kt) / len(kt) if kt else 0.0
                pj = float(r['value']) / mw_per_gw * cf * pj_per_gw
                add += pj
                ids.append(r.get('value_id', ''))
                parts.append(f"{r['value']} MW {kind} x CF {cf:.4f} = {pj:.4f} PJ")
            d = denominator(sc, y)
            if d <= 0:
                continue
            raw = (g_ren + add) / d
            cap = LT.controller('max_target_share', '1')
            val = round(min(raw, cap), digits)
            cur[y] = (val, 'capacity rule', '|'.join(ids),
                      f"({g_ren:.4f} PJ renewable generation {LT.controller('anchor_year')} + "
                      + ' + '.join(parts) + f") / {d:.4f} PJ total generation {y}"
                      + (f" = {raw:.4f}, capped at {cap}" if raw > cap else ''))
        if cur:
            out[sc] = cur
    # LTS equals NDC through lts_equals_ndc_until: the LTS curve takes the NDC points up to that year and the NDC
    # value of that year, then its own points after it
    ndc, lts, until = LT.scenario('ndc'), LT.scenario('lts'), LT.controller('lts_equals_ndc_until', '1')
    if ndc in out and (lts in scenarios):
        npts = {y: v[0] for y, v in out[ndc].items()}
        held = curve_value(npts, until, min(npts) - 1, 0.0) if npts else None
        new = {y: v for y, v in out[ndc].items() if y <= until}
        if held is not None and until not in new:
            new[until] = (held, 'NDC value held', '', f'NDC curve value of {until}')
        new.update({y: v for y, v in out.get(lts, {}).items() if y > until})
        out[lts] = new
    return out


def write(all_targets, out_dir):
    """all_targets: {country: {scenario: {year: (value, basis, ids, derivation)}}}"""
    p = Path(out_dir) / FILE_NAME
    with open(p, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(FIELDS)
        for c in sorted(all_targets):
            for sc in all_targets[c]:
                for y in sorted(all_targets[c][sc]):
                    v, basis, ids, der = all_targets[c][sc][y]
                    w.writerow([c, sc, y, v, basis, ids, der])
    return p


def load(root):
    """{country: {scenario: {year: value}}} from the Stage 1 output file."""
    p = Path(root) / '_STAGE1_OUTPUT' / FILE_NAME
    out = {}
    if not p.exists():
        return out
    with open(p, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r['country'], {}).setdefault(r['scenario'], {})[int(r['year'])] = float(r['value'])
    return out


def curve_value(milestones, year, cutoff, anchor_share):
    """Target of a year: None in or before the cutoff year or without milestones; straight line from the cutoff
    year (anchor share) through the milestones; the last milestone held after its year."""
    if year <= cutoff or not milestones:
        return None
    pts = sorted(milestones.items())
    if year >= pts[-1][0]:
        return pts[-1][1]
    pts = [(cutoff, anchor_share)] + [p for p in pts if p[0] > cutoff]
    for (y1, v1), (y2, v2) in zip(pts, pts[1:]):
        if y1 <= year <= y2:
            return v2 if y2 == y1 else v1 + (v2 - v1) * (year - y1) / (y2 - y1)
    return pts[-1][1]
