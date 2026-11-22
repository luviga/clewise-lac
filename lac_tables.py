"""Loader of the external tables that hold the values and names of the stage pipeline.

Every value and every name of a country, scenario, technology, fuel or emission that the stage pipeline
(A2 compilers, B1 runners, Stages 0 to 3) uses is read from the tables below, through this module:

  config/preparation/Config_country_codes.yaml   countries: name, code, model folder, scripts
  config/scenarios/scenario_catalogue.csv        scenarios: name, role, folder names
  config/scenarios/rules/stage_controller.csv    Stage 0 to 3 controller settings
  config/scenarios/technology_types.csv          technology groups, name tokens and prefixes
  config/scenarios/fuel_types.csv                fuel groups
  config/scenarios/emission_labels.csv           emission groups
  inputs/scenarios/scenario_values.csv           scenario targets (country, scenario, lever, year, value)
  config/compilation/Config_MOMF_T1_A.yaml       numbers of the A2 compilers (general and per country)
  config/execution/Config_MOMF_T1_AB.yaml        numbers of the B1 runners (general and per country)

Scripts in a model folder find this file by walking up from their own folder. Lookups that return a name or a
number are cached (the tables are read once per process); lookups that return a list or a dict return a new
object on every call.
Command line (used by the batch and shell files):
  python lac_tables.py solver-runs <S0|FINAL>   one line per solver run: label|model|data|output
"""
import copy
import csv
import os
import sys
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
_ALL = 'all'


def _path(*parts):
    return ROOT.joinpath(*parts)


def _num(text):
    """Value of a table cell, typed as the code held it: int for integer text, float for decimal text,
    a list for items separated by '|', otherwise the text."""
    s = text.strip()
    if '|' in s:
        return [_num(x) for x in s.split('|')]
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


@lru_cache(maxsize=None)
def _csv(*parts):
    with open(_path(*parts), encoding='utf-8', newline='') as fh:
        return tuple(dict(r) for r in csv.DictReader(fh))


@lru_cache(maxsize=None)
def _yaml(*parts):
    with open(_path(*parts), encoding='utf-8') as fh:
        return yaml.safe_load(fh)


# ----------------------------------------------------------------------------- countries
def _countries():
    return _yaml('config', 'preparation', 'Config_country_codes.yaml')['country_data']


def countries():
    """Country names in table order."""
    return [c['name'] for c in _countries()]


def country(name):
    """The full record of one country."""
    for c in _countries():
        if c['name'] == name:
            return dict(c)
    raise KeyError(name)


def country_map(field):
    """{country name: value of field} in table order."""
    return {c['name']: c[field] for c in _countries()}


def country_table(*fields, **renamed):
    """{country name: {field: value, ...}} in table order; renamed=dict(key=field) gives a field under another key."""
    out = {}
    for c in _countries():
        rec = {f: c[f] for f in fields}
        rec.update({k: c[f] for k, f in renamed.items()})
        out[c['name']] = rec
    return out


def country_of(script_path):
    """Name of the country whose model folder holds script_path."""
    p = Path(script_path).resolve()
    for c in _countries():
        d = _path(c['country_folder'], *c['model_dir'].split('/')).resolve()
        if p.parent == d:
            return c['name']
    raise KeyError(f'no country model folder holds {p}')


@lru_cache(maxsize=None)
def country_value(name, field):
    """One field of one country."""
    return country(name)[field]


def model_path(name):
    """Model folder of a country, relative to the repository root, with forward slashes."""
    c = country(name)
    return c['country_folder'] + '/' + c['model_dir']


# ----------------------------------------------------------------------------- scenarios
def _scen_rows():
    return _csv('config', 'scenarios', 'scenario_catalogue.csv')


@lru_cache(maxsize=None)
def scenario(role):
    """Scenario name of a role (base, ndc, lts, or the role of an older name)."""
    for r in _scen_rows():
        if r['role'] == role:
            return r['scenario']
    raise KeyError(role)


def scenarios(group='in_use'):
    """Scenario names of a group, in catalogue order (group 'in_use': the three scenarios the pipeline runs)."""
    return [r['scenario'] for r in _scen_rows() if group in r['groups'].split('|')]


# ----------------------------------------------------------------------------- stage controller
def _ctl_rows():
    return _csv('config', 'scenarios', 'rules', 'stage_controller.csv')


@lru_cache(maxsize=None)
def _controller(name, stage, country):
    for r in _ctl_rows():
        if r['name'] == name and r['stage'] in (stage, _ALL) and r['country'] == country:
            v = _num(r['value'])
            return tuple(v) if isinstance(v, list) else v
    raise KeyError(f'{name} (stage {stage}, country {country})')


def controller(name, stage=_ALL, country=_ALL):
    """A Stage 0 to 3 controller setting (the row of the stage, or of all stages; of the country, or of all)."""
    v = _controller(name, stage, country)
    return list(v) if isinstance(v, tuple) else v


def controller_list(name, stage=_ALL, country=_ALL):
    """A controller setting that holds a list (items separated by '|'), always as a list."""
    v = controller(name, stage, country)
    return v if isinstance(v, list) else [v]


def controller_by_country(name, stage=_ALL):
    """{country: value} of a setting written once per country, in the order of the rows."""
    return {r['country']: _num(r['value']) for r in _ctl_rows()
            if r['name'] == name and r['stage'] in (stage, _ALL) and r['country'] != _ALL}


# ----------------------------------------------------------------------------- scenario values
def _value_rows():
    return _csv('inputs', 'scenarios', 'scenario_values.csv')


def scenario_values(lever, country=_ALL, scenario_role=None):
    """{scenario name: {year: value}} of one lever for one country ('all': the general rows).
    Only the rows written for that country; no fallback to the general rows."""
    out = {}
    roles = {r['scenario']: r['role'] for r in _scen_rows()}
    for r in _value_rows():
        if r['lever'] != lever or r['country'] != country:
            continue
        if scenario_role is not None and roles.get(r['scenario']) != scenario_role:
            continue
        out.setdefault(r['scenario'], {})[int(r['year'])] = _num(r['value'])
    return out


def scenario_value_overrides(lever):
    """{country: {scenario name: {year: value}}} of the countries that have their own rows of a lever."""
    names = []
    for r in _value_rows():
        if r['lever'] == lever and r['country'] != _ALL and r['country'] not in names:
            names.append(r['country'])
    return {c: scenario_values(lever, c) for c in names}


# ----------------------------------------------------------------------------- technologies, fuels, emissions
@lru_cache(maxsize=None)
def _group_cached(table, group, country):
    rows = _csv('config', 'scenarios', table)
    key = {'technology_types.csv': 'technology', 'fuel_types.csv': 'fuel', 'emission_labels.csv': 'emission'}[table]
    out = tuple(r[key] for r in rows if r['group'] == group and r['country'] in (country, _ALL))
    if not out:
        raise KeyError(f'{table}: group {group} for {country}')
    return out


def _group(table, group, country):
    return list(_group_cached(table, group, country))


def techs(group, country=_ALL):
    """Technology names, name tokens or name prefixes of a group, in table order."""
    return _group('technology_types.csv', group, country)


@lru_cache(maxsize=None)
def tech(group, country=_ALL):
    """The single technology name, token or prefix of a group."""
    v = techs(group, country)
    if len(v) != 1:
        raise KeyError(f'technology group {group} holds {len(v)} names')
    return v[0]


def fuels(group, country=_ALL):
    return _group('fuel_types.csv', group, country)


@lru_cache(maxsize=None)
def fuel(group, country=_ALL):
    v = fuels(group, country)
    if len(v) != 1:
        raise KeyError(f'fuel group {group} holds {len(v)} names')
    return v[0]


def emissions(group, country=_ALL):
    return _group('emission_labels.csv', group, country)


@lru_cache(maxsize=None)
def emission(group, country=_ALL):
    v = emissions(group, country)
    if len(v) != 1:
        raise KeyError(f'emission group {group} holds {len(v)} names')
    return v[0]


def tech_map(group, country=_ALL, value_field='value'):
    """{technology: value} of a group whose rows carry a value (number or text)."""
    rows = _csv('config', 'scenarios', 'technology_types.csv')
    return {r['technology']: _num(r[value_field]) for r in rows
            if r['group'] == group and r['country'] in (country, _ALL)}


def emission_map(group, country=_ALL):
    """{technology: [emission, ...]} of a group of the emission label table."""
    out = {}
    for r in _csv('config', 'scenarios', 'emission_labels.csv'):
        if r['group'] == group and r['country'] in (country, _ALL):
            out.setdefault(r['technology'], []).append(r['emission'])
    return out


# ----------------------------------------------------------------------------- stage numbers (A2, B1)
_STAGE_FILES = {'compilation': ('config', 'compilation', 'Config_MOMF_T1_A.yaml'),
                'execution': ('config', 'execution', 'Config_MOMF_T1_AB.yaml')}


def stage_values(stage, country):
    """Numbers of the A2 ('compilation') or B1 ('execution') scripts: the general section, updated by the
    country's section."""
    d = _yaml(*_STAGE_FILES[stage])
    out = copy.deepcopy(d.get('general') or {})
    out.update(copy.deepcopy((d.get('countries') or {}).get(country) or {}))
    return out


# ----------------------------------------------------------------------------- solver runs
def solver_runs(tag):
    """(label, model file, data file, output file) of every solver run of a stage (S0 or FINAL), relative to the
    repository root with the operating system's separator, for the countries and scenarios of the tables whose
    data file exists."""
    runs = []
    for c in countries():
        mdir = Path(*model_path(c).split('/'))
        model = mdir / country(c)['osemosys_file']
        for s in scenarios():
            name = f'{s}_{tag}_0'
            data = mdir / 'Executables' / name / f'{name}.txt'
            if not _path(data).exists() or not _path(model).exists():
                continue
            out = mdir / 'Executables' / name / f'{name}_output.txt'
            runs.append((f'{c} {s}_{tag}', str(model), str(data), str(out)))
    return runs


def _main(argv):
    if len(argv) == 3 and argv[1] == 'solver-runs':
        for r in solver_runs(argv[2]):
            print('|'.join(r))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
