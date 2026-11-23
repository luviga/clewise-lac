D = "_TB1['rounding_digits']"
RULES = [
    ('round', lambda s: s['kind'] == 'number' and s['token'] == '4' and 'round(' in s['text'],
     r'(,\s*)4(\s*\))', r'\g<1>' + D + r'\g<2>'),
]
