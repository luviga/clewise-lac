"""REPORT helper: values written per step and country (value_register.csv rows whose after value differs from the
before value), with three example rows per step (before, after, source). Prints Markdown.
Usage: python -I report_counts.py"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402

import pandas as pd

v = pd.read_csv(M.JOB / 'value_register.csv', dtype=str, keep_default_na=False)
v['country'] = v['model'].str.split('/').str[0].replace({'config': 'all (configuration)'})
w = v[v['before'].str.strip() != v['after'].str.strip()]
t = w.pivot_table(index='step', columns='country', values='model', aggfunc='count', fill_value=0)
t['total'] = t.sum(axis=1)
print('| step | ' + ' | '.join(t.columns) + ' |')
print('|' + '---|' * (len(t.columns) + 1))
for step, r in t.iterrows():
    print(f'| {step} | ' + ' | '.join(str(int(x)) for x in r) + ' |')
print()
for step, g in w.groupby('step', sort=True):
    print(f'**{step}**')
    print()
    print('| model | sheet | tech | parameter | year | before | after | source |')
    print('|---|---|---|---|---|---|---|---|')
    ex = g.drop_duplicates(['model']).head(3)
    if len(ex) < 3:
        ex = pd.concat([ex, g.drop(ex.index).head(3 - len(ex))])
    for _, r in ex.iterrows():
        src = r['source_id'].replace('|', ', ') or ('ASSUMPTION' if r['assumption_sentence'] else r['derivation'][:60])
        b, a = str(r['before'])[:40].replace('|', '/'), str(r['after'])[:40].replace('|', '/')
        print(f"| {r['model']} | {r['sheet']} | {r['tech'][:40].replace('|', ' / ')} | {r['parameter']} | {r['year']} | {b} | {a} | {src} |")
    print()
