"""Extract fuel tariff lines from Banco de Guatemala 'Importaciones realizadas por partida'
(Comercio General, KF-103_<year>.xlsx). Values in USD (CIF), volumes in kilograms.

Usage: py -I gua_banguat_trade.py <file1.xlsx> [<file2.xlsx> ...]
Prints for each file and each selected SAC line: annual value, annual kg, USD per tonne,
and the monthly value and kg (12 pairs).
"""
import sys
import openpyxl

LINES = {
    '2701120000': 'COA bituminous coal',
    '2701190000': 'COA other coal',
    '2701110000': 'COA anthracite',
    '2713110000': 'COK petroleum coke not calcined',
    '2713120000': 'COK petroleum coke calcined',
    '2710191100': 'JET kerosene-type jet fuel (SAC 2710.19.11)',
    '2710191200': 'KER other kerosenes (SAC 2710.19.12)',
    '2710192100': 'DSL gas oil diesel (SAC 2710.19.21)',
    '2710192200': 'FOI fuel oil No. 6 bunker C (SAC 2710.19.22)',
    '2710123000': 'GSL motor gasoline (SAC 2710.12.30)',
    '2710122000': 'AVG aviation gasoline (SAC 2710.12.20)',
    '2710121000': 'petroleum ether (SAC 2710.12.10)',
    '2711120000': 'LPG propane',
    '2711130000': 'LPG butanes',
    '2711110000': 'NGS liquefied natural gas',
    '2711210000': 'NGS natural gas gaseous',
    '2709000000': 'CRU crude',
    '2709009000': 'CRU crude other',
}


def main(paths):
    for path in paths:
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
        year = None
        for r in ws.iter_rows(values_only=True):
            cells = [c for c in r if c is not None]
            if not cells:
                continue
            first = str(cells[0]).strip()
            if first.startswith('A') and 'o ' in first and year is None and any(ch.isdigit() for ch in first):
                year = first
            code = first.replace(' ', '')
            if code in LINES:
                vals = []
                for c in cells[1:]:
                    try:
                        vals.append(float(c))
                    except (TypeError, ValueError):
                        vals.append(0.0)
                v, kg = vals[0], vals[1]
                upt = v / kg * 1000 if kg else float('nan')
                months = ';'.join('%.0f/%.0f' % (vals[2 + 2 * i], vals[3 + 2 * i]) for i in range(12)
                                  if 3 + 2 * i < len(vals))
                print('%s\t%s\t%s\t%s\tvalue_usd=%.0f\tkg=%.0f\tusd_per_t=%.2f\tmonths=%s' % (
                    path.replace('\\', '/').split('/')[-1], year, code, LINES[code], v, kg, upt, months))


if __name__ == '__main__':
    main(sys.argv[1:])
