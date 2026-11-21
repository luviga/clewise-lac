"""Index A-O workbook rows: (country, sheet, tech, parameter) -> rows with mode, projection parameter and year values (values as stored)."""
import openpyxl, pandas as pd, sys, json
AO = {
 'CostaRica': 'CostaRica/CR_ENERGY/t1_confection/A1_Outputs/A-O_Parametrization.xlsx',
 'DominicanRepublic': 'DominicanRepublic/RD_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
 'Ecuador': 'Ecuador/ECU_Energy/A1_Outputs/A-O_Parametrization.xlsx',
 'Guatemala': 'Guatemala/GUA_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
 'Honduras': 'Honduras/HON_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
 'Jamaica': 'Jamaica/JAM_ENERGY/A1_Outputs/A-O_Parametrization.xlsx',
}
def index(root='C:/clw_fix/'):
    out = []
    for c, path in AO.items():
        wbv = openpyxl.load_workbook(root + path, data_only=True)
        wbf = openpyxl.load_workbook(root + path, data_only=False)
        for ws in wbv.worksheets:
            wf = wbf[ws.title]
            hdr = {}
            for col in range(1, ws.max_column + 1):
                v = ws.cell(1, col).value
                if v is not None: hdr[v if not isinstance(v, float) else int(v)] = col
            if 'Tech' not in hdr or 'Parameter' not in hdr: continue
            years = [k for k in hdr if isinstance(k, int)]
            for r in range(2, ws.max_row + 1):
                t = ws.cell(r, hdr['Tech']).value
                if t is None: continue
                rec = dict(country=c, sheet=ws.title, row=r, tech=t, parameter=ws.cell(r, hdr['Parameter']).value,
                           mode=ws.cell(r, hdr.get('Projection.Mode', 1)).value if 'Projection.Mode' in hdr else None,
                           ppar=ws.cell(r, hdr['Projection.Parameter']).value if 'Projection.Parameter' in hdr else None)
                for y in years:
                    rec[y] = ws.cell(r, hdr[y]).value
                    fv = wf.cell(r, hdr[y]).value
                    if isinstance(fv, str) and fv.startswith('='): rec[f'f{y}'] = fv
                out.append(rec)
    return pd.DataFrame(out)
if __name__ == '__main__':
    df = index()
    df.to_pickle(sys.argv[1])
    print(len(df)); print(df.groupby(['country','sheet']).size())
    d = df.groupby(['country','sheet','tech','parameter']).size(); print('dup keys', (d>1).sum()); print(d[d>1].head(20))
