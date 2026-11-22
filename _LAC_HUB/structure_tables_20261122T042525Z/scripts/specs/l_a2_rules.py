D = "_TA2['rounding_digits']"
RULES = [
    ('df_round', lambda s: s['kind'] == 'number' and s['token'] == '4' and '.round(' in s['text'],
     r'(\.round\(\s*)4(\s*\))', r'\g<1>' + D + r'\g<2>'),
    ('round', lambda s: s['kind'] == 'number' and s['token'] == '4' and 'round(' in s['text'] and '.round(' not in s['text'],
     r'(,\s*)4(\s*\))', r'\g<1>' + D + r'\g<2>'),
    ('base_year_loc', lambda s: s['kind'] == 'number' and s['token'] == '2018' and 'loc[' in s['text'],
     r'(loc\[\s*n,\s*)2018(\s*\])', r"\g<1>_TA2['base_year']\g<2>"),
    ('by_int', lambda s: s['kind'] == 'number' and s['text'].startswith('BY_INT ='),
     r'^BY_INT = \d+', "BY_INT = _TA2['base_year']"),
]
