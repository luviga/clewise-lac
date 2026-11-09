"""Arithmetic check of image-read PPIs: PPI + round(rate*PPI,2) + L112 + dist + det + transport must equal an
official price present in the OCR text of the same resolution (+-0.02) for one of the 2024 margin sets.
Usage: py -I dr_check_image_reads.py <dr_resolution_image_reads.csv> <micm_res2024_dir>"""
import sys, os, re, csv, pdfplumber
S = {'GSL_PREMIUM': (71.85, .16, [(15.09, 22.57), (16.59, 25.07)]), 'GSL_REGULAR': (63.83, .16, [(15.09, 22.57), (16.59, 25.07)]),
     'DSL_REGULAR': (28.06, .16, [(12.78, 19.25), (14.28, 21.75)]), 'DSL_EGPC': (28.06, .16, [(5.24, 0)]), 'AVTUR': (6.30, .065, [(15.53, 0)]),
     'KER': (17.99, .16, [(9.10, 15.01)]), 'FO6': (17.99, .16, [(1.54, 0)]), 'FO6_EGPC': (17.99, .16, [(1.35, 0)]),
     'FO6_1S': (17.99, .16, [(1.54, 0)]), 'FO6_1S_EGPC': (17.99, .16, [(1.35, 0)]), 'LPG': (0, .16, [(10.21, 14.90), (11.71, 16.90)])}
files = os.listdir(sys.argv[2])
ok = bad = 0
for r in csv.DictReader(open(sys.argv[1], encoding='utf-8')):
    f = [x for x in files if 'NO.' + r['resolution_number'].split('-')[0] + '-' in x][0]
    txt = ' '.join((p.extract_text() or '') for p in pdfplumber.open(os.path.join(sys.argv[2], f)).pages)
    txt = re.sub(r'(\d),(\d{3}\.)', r'\1\2', txt)
    nums = set()
    for tk in re.findall(r'\d{1,3}[.,\-] ?\d{2}(?!\d)', txt):
        try:
            nums.add(round(float(re.sub(r'[,\-] ?', '.', tk)), 2))
        except ValueError:
            pass
    for k, (l112, av, ms) in S.items():
        p = float(r[k])
        offs = [round(p + round(av * p, 2) + l112 + d + e + 5.68, 2) for d, e in ms]
        if any(abs(o - n) <= 0.021 for o in offs for n in nums):
            ok += 1
        else:
            bad += 1
            print('no official match in OCR text', r['week_start'], k, p, offs)
print('ok', ok, 'not matched', bad)
