"""D7a: lower bands written as 0.98 times a value (F10) use 0.999. Dominican Republic 19 rows and Jamaica 7 rows: the factor
token 0.98 inside each formula cell of the row becomes 0.999 (plain-value cells and formulas without the token stay).
Ecuador EXTT_CRU row 388 is in ecu_crude.csv. Reads the base snapshot; writes proposals_parts/d7a.csv."""
import os, sys, re, collections
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_props import BASEDIR, write_part

TOK = re.compile(r'(?<![\d.])0\.98(?![\d])')
SETS = [
    ('DominicanRepublic', 'DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
     {'Primary Techs': [138, 168, 178, 208, 228],
      'Secondary Techs': [48, 78, 98, 128, 138, 148, 158, 168, 178, 188, 198, 208, 218, 228]}),
    ('Jamaica', 'Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
     {'Primary Techs': [188, 198], 'Secondary Techs': [88, 138, 148, 158, 168]}),
]
BAND_A = ('ASSUMPTION: the lower activity limit is 0.999 times the sourced output, a 0.1 percent band that keeps the solve '
          'feasible against rounding; a band of 2 percent would let output fall up to 2 percent below the sourced value.')
rows = []
for c, path, sheets in SETS:
    wf = openpyxl.load_workbook(f'{BASEDIR}/{path}')
    wv = openpyxl.load_workbook(f'{BASEDIR}/{path}', data_only=True)
    for s, rr in sheets.items():
        ws, vs = wf[s], wv[s]
        hdr = {ws.cell(1, j).value: j for j in range(1, ws.max_column + 1)}
        yc = {int(k): j for k, j in hdr.items() if isinstance(k, (int, float))}
        for r in rr:
            tech, par = ws.cell(r, hdr['Tech']).value, ws.cell(r, hdr['Parameter']).value
            assert par == 'TotalTechnologyAnnualActivityLowerLimit', (c, s, r, par)
            for y, j in sorted(yc.items()):
                f = ws.cell(r, j).value
                if not (isinstance(f, str) and TOK.search(f)):
                    continue
                nf = TOK.sub('0.999', f)
                cur = vs.cell(r, j).value
                simple = f.count('0.98') == 1 and '+' not in f and '-' not in f[1:] and '/' not in f
                est = repr(float(cur) * 0.999 / 0.98) if (simple and isinstance(cur, (int, float))) else ''
                rows.append(dict(country=c, workbook=path, sheet=s, row=r, column=openpyxl.utils.get_column_letter(j), year=y,
                                 Tech=tech, Parameter=par, scenario='ALL', current_value=cur, new_value=est, new_formula=nf,
                                 kind='ao_formula', decision='D7a', source_ids='',
                                 derivation=f'band factor 0.98 -> 0.999 in formula {f}', assumption=BAND_A))
write_part('d7a', rows)
print(collections.Counter((r['country'], r['sheet'][:3], r['row'], r['Tech']) for r in rows))
