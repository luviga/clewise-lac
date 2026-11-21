"""Shared paths and helpers of LAC_FIX_RUN2."""
import os, glob
import pandas as pd

ROOT = 'C:/clw_fix'
JOB = ROOT + '/_LAC_HUB/fix_run2_20261120T225823Z'
EARLIER = ROOT + '/_LAC_HUB/fix_run_20261111T200825Z'
BASE = '4ba69d6cc3e6619bcc7ee6aee968ea0c78372b2f'
MODELS = {
    'CostaRica': 'CostaRica/CR_ENERGY/t1_confection',
    'DominicanRepublic': 'DominicanRepublic/RD_ENERGY',
    'Ecuador': 'Ecuador/ECU_Energy',
    'Guatemala': 'Guatemala/GUA_ENERGY',
    'Honduras': 'Honduras/HON_ENERGY',
    'Jamaica': 'Jamaica/JAM_ENERGY',
}
SCENS = ['BAU', 'NDCNEW', 'LTSNEW']
KEYS = ['PARAMETER', 'REGION', 'TECHNOLOGY', 'FUEL', 'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE', 'SEASON',
        'DAYTYPE', 'DAILYTIMEBRACKET', 'STORAGE']


def load_params(folder):
    frames = []
    for f in sorted(glob.glob(os.path.join(folder, '*.csv'))):
        try:
            d = pd.read_csv(f, dtype=str, keep_default_na=False)
        except Exception:
            continue
        if 'Value' not in d.columns or 'PARAMETER' not in d.columns or len(d) == 0:
            continue
        for k in KEYS:
            if k not in d.columns:
                d[k] = ''
        d['file'] = os.path.basename(f)
        frames.append(d[KEYS + ['Value', 'file']])
    if not frames:
        return pd.DataFrame(columns=KEYS + ['Value', 'file', 'v'])
    x = pd.concat(frames, ignore_index=True)
    x['v'] = pd.to_numeric(x.Value, errors='coerce')
    return x


def defaults(model, root=ROOT):
    d = pd.read_excel(os.path.join(root, model, 'B1_Default_Param.xlsx'))
    return dict(zip(d.iloc[:, 0], d.iloc[:, 1]))
