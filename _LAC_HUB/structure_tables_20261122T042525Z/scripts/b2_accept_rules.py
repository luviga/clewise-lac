"""Constants of the mathematics, of a file layout or of presentation that stay in the 26 code files, with the
reason. Used by b2_remaining.py (what is left to move) and by b4_register.py (the accepted list of the job)."""
import re

RULES = [
    (lambda s: s['kind'] == 'number' and s['token'] in ('11', '30', '43') and 'range(1,' in s['text'].replace(' ', ''),
     'layout of the B1 structure workbook: number of set, parameter and variable columns read (no effect on values)'),
    (lambda s: s['kind'] == 'number' and s['token'] == '2' and ('iat[2+n' in s['text'].replace(' ', '') or 'n+2' in s['text'].replace(' ', '')),
     'layout of the B1 structure workbook: first data row below the header rows (no effect on values)'),
    (lambda s: s['kind'] == 'number' and s['token'] in ('10', '9', '6') and '10**' in s['text'],
     'unit conversion written as a power of ten (10**9 giga, 10**6 mega prefix)'),
    (lambda s: 'gc.collect' in s['text'],
     'garbage collector generation (memory housekeeping, no effect on results)'),
    (lambda s: s['kind'] == 'number' and 'len(this_param_keys)' in s['text'],
     'number of index sets of a model parameter (mathematical structure of the OSeMOSYS data file)'),
    (lambda s: s['kind'] == 'number' and 'str(10)' in s['text'],
     'fixed leading digits of an internal row code (no effect on values)'),
    (lambda s: 'max_x_per_iter' in s['text'],
     'number of scenarios solved in parallel per batch (no effect on results)'),
    (lambda s: s['kind'] == 'scenario' and s['token'] == 'Default',
     'generic word Default in a file or column name (Default parameter values), not a scenario name'),
    (lambda s: s['file'] == 'ao_safe_save.py' and s['token'] == '51',
     'Excel file format code of the xlsx format in the Excel automation interface (an interface constant)'),
    (lambda s: s['file'] == 'ao_safe_save.py' and s['token'] == '10',
     'number of cell names shown in an error message (presentation)'),
    (lambda s: s['file'] == 'stage2_post_clean.py' and s['token'] in ('1073741824', '1048576', '1024'),
     'bytes per gigabyte, megabyte and kilobyte for a size message (unit conversion, presentation)'),
    (lambda s: s['file'] == 'stage2_post_clean.py' and s['token'] == '3',
     'number of file names printed (presentation)'),
    (lambda s: s['kind'] == 'number' and re.search(r'len\((parts|parts2|data_parts|indices)\)', s['text']) is not None,
     'number of fields of a parsed text line (format of the solver output or data file)'),
    (lambda s: s['kind'] == 'number' and s['token'] == '2' and re.search(r'(i \+= 2|col_start = i \+ 2|semicolon_pos \+ 2|semi \+ 2)', s['text']) is not None,
     'line or character offset in the solver output or data file format'),
    (lambda s: s['kind'] == 'number' and 'bm.group(' in s['text'],
     'group number of a regular expression match'),
    (lambda s: s['kind'] == 'number' and 'f.read(5000)' in s['text'],
     'number of characters read from a solver output header (input and output)'),
    (lambda s: s['kind'] == 'number' and 'bounds[0]+500' in s['text'].replace(' ', ''),
     'number of characters read from a data file block header (input and output)'),
    (lambda s: s['kind'] == 'number' and s['token'] in ('8', '5', '10', '20') and re.search(r'\.(head|nlargest)\(|len\(fails\) > 20', s['text']) is not None,
     'number of rows printed (presentation)'),
    (lambda s: s['kind'] == 'number' and re.search(r'ws(_s)?\.cell\(r, \d\)', s['text']) is not None,
     'column position in a workbook sheet read by the script (file layout)'),
    (lambda s: s['file'].endswith('.bat') and s['kind'] == 'number' and 'tokens=1-4' in s['text'],
     'number of fields of each line of the run list that lac_tables.py prints (format of the batch loop)'),
    (lambda s: s['kind'] == 'number' and s['token'] == '5' and re.search(r'len\(parts\) [<>] 5', s['text']) is not None,
     'number of fields of a parsed text line (file layout)'),
    (lambda s: s['file'] == 'stage3_apply.py' and s['kind'] == 'emission' and s['token'] == 'RM',
     'abbreviation RM (reserve margin) inside a log message, not an emission name'),
    (lambda s: s['file'] == 'stage3_apply.py' and s['kind'] == 'country' and 'help=' in s['text'],
     'example in the help text of a command-line option (presentation)'),
]


def reason(site):
    for pred, why in RULES:
        if pred(site):
            return why
    return None
