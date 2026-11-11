import pandas as pd, re
p = pd.read_csv('cost_review_20261111T015203Z/proposals_all.csv', low_memory=False)
key = ['country','Tech','Parameter','fuel_scenario']
sourced = {'replace','projected','observed','history from ratio','matched, newer edition'}
g = p.groupby(key)
rows = []
for k, d in g:
    cls = set(d.basis_class.dropna())
    if 'matched' in cls and (cls & sourced):
        m = d[d.basis_class=='matched']
        for _, r in m.iterrows():
            der = str(r.derivation)
            sv = None
            mm = re.search(r'within 2 percent of the source value ([0-9.eE+-]+)', der)
            if mm: sv = float(mm.group(1).rstrip('.'))
            else:
                mm = re.search(r'gives ([0-9.eE+-]+)', der)
                if mm: sv = float(mm.group(1).rstrip('.'))
            rows.append(dict(zip(key, k), year=r.year, sheet=r.sheet, current=r.current_value, proposed=r.proposed_value, source_value=sv, classes=';'.join(sorted(cls)), der=der[:300]))
o = pd.DataFrame(rows)
print('groups', o.groupby(key).ngroups, 'cells', len(o))
print(o.groupby('country').size())
print('no source value parsed:', o.source_value.isna().sum())
print(o[o.source_value.isna()].der.str[:200].unique()[:10])
o.to_csv('fix_run_20261111T200825Z/scripts/r5_matched_scratch.csv', index=False)
print(o.groupby(key).size().to_string())
