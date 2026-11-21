"""A1: sources.csv for every source id used in proposals.csv. Earlier ids are reused from the earlier job's sources.csv (file
path made relative to this job folder); new ids FR2-* are registered here by file and take their metadata from the research
tables (research/*_sources.csv) or from the entries below. Every file is hashed again and must match the recorded SHA-256.
Also writes logs/sources_check.csv."""
import csv, glob, hashlib, os
import pandas as pd

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
EARLIER = 'C:/clw_fix/_LAC_HUB/fix_run_20261111T200825Z'
ARCHIVE = 'C:/Users/luisfernando/Desktop/OSeMOSYS/LAC_sources_archive/'
FIELDS = ['id', 'url', 'title', 'publisher', 'date', 'accessed', 'sha256', 'file', 'page_or_table']
NEW = {  # id -> file (relative to the job folder) as listed in a research table
    'FR2-D12-01': 'downloads/d12_lives/ARCONEL_Regulacion-Nro.-ARCONEL-00424-CODIFICADA.pdf',
    'FR2-D12-02': 'downloads/d12_lives/ARCERNNR_costo_servicio_2021_esmap.pdf',
    'FR2-D12-03': 'downloads/d12_lives/ARCONEL_Regulacion-001-23-Fe-Erratas.pdf',
    'FR2-D12-04': 'downloads/d12_lives/Ley_Hidrocarburos_primicias.pdf',
    'FR2-D12-06': 'downloads/d12_lives/PLANMICC_OperationalLife_BAU_7483e67.csv',
    'FR2-D12-07': 'downloads/d12_lives/PLANMICC_A-O_Parametrization_COMPLETED_7483e67.xlsx',
    'FR2-D12-08': 'downloads/d12_lives/ATB2024_definitions.html',
    'FR2-D12-09': 'downloads/d12_lives/IRENA_Green_hydrogen_cost_reduction_2020.pdf',
    'FR2-D12-10': 'downloads/d12_lives/IRS_p946.pdf',
    'FR2-D12-11': 'downloads/d12_lives/CELEC_EEFF_2020_esmap.pdf',
    'FR2-D12-12': 'downloads/d12_lives/ARCONEL_2.2.-Regulacion-Nro.-005-25-ERNC.pdf',
    'FR2-D12-13': 'downloads/d12_lives/ARCONEL_Regulacion-ARCONEL-006-24-1-3.pdf',
}
MANUAL = {
    'FR2-GUA-01': dict(url='https://www.amm.org.gt/pdfs2/pub_gen_mensual_x_planta/GM20250101.xlsx',
                       title='Despacho de carga ejecutado del Sistema Nacional Interconectado 2025, generacion mensual por planta (GWh)',
                       publisher='Administrador del Mercado Mayorista (AMM), Guatemala', date='2025 (full year)',
                       accessed='2026-11-21', file='downloads/d2_gua/AMM_GM20250101.xlsx',
                       page_or_table='sheet Energia, row 8 PLANTAS HIDROELECTRICAS, column O TOTAL (5,473.52 GWh)'),
}
EXTRA = os.path.join(JOB, 'scripts', 'sources_extra.csv')   # further FR2 ids (D2, D3), same columns as FIELDS minus sha check


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def resolve(f):
    if f.startswith('archive '):
        return ARCHIVE + f[len('archive '):].replace('LAC_sources_archive/', '')
    if f.startswith('../'):
        return os.path.normpath(os.path.join(JOB, f))
    return os.path.join(JOB, f)


research = {}
for t in glob.glob(JOB + '/research/*_sources.csv'):
    for r in csv.DictReader(open(t, encoding='utf-8')):
        research.setdefault(r['file'].strip(), r)
P = pd.read_csv(JOB + '/proposals.csv', dtype=str, keep_default_na=False)
used = sorted({s.strip() for x in P.source_ids for s in x.split(';') if s.strip()})
earlier = {r['id']: r for r in csv.DictReader(open(EARLIER + '/sources.csv', encoding='utf-8'))}
extra = {r['id']: r for r in csv.DictReader(open(EXTRA, encoding='utf-8'))} if os.path.exists(EXTRA) else {}
out, check = [], []
for i in used + [k for k in list(NEW) + list(MANUAL) + list(extra) if k not in used]:
    if i in earlier:
        e = earlier[i]
        rec = dict(id=i, url=e['url'], title=e['title'], publisher=e['publisher'], date=e['date'], accessed=e['accessed'],
                   sha256=e['sha256'], file='../fix_run_20261111T200825Z/' + e['local_file'], page_or_table=e['page_or_table'])
    elif i in NEW:
        r = research[NEW[i]]
        rec = dict(id=i, url=r['url'], title=r['title'], publisher=r['publisher'], date=r['date'], accessed=r['accessed'],
                   sha256=r['sha256'], file=NEW[i], page_or_table=r['page_or_table'])
    elif i in MANUAL:
        rec = dict(id=i, sha256='', **MANUAL[i])
    elif i in extra:
        rec = {k: extra[i].get(k, '') for k in FIELDS}
    else:
        check.append(dict(id=i, status='MISSING: id not registered'))
        continue
    files = [f.strip() for f in rec['file'].split(';')]
    if i in earlier and len(files) > 1:
        files = [files[0]] + ['../fix_run_20261111T200825Z/' + f for f in files[1:]]
    recorded = [s.strip() for s in rec['sha256'].split(';')] if rec['sha256'] else [''] * len(files)
    hs, st = [], 'ok'
    for k, f in enumerate(files):
        p = resolve(f)
        if not os.path.exists(p):      # reused from the read-only archive: copy into downloads/reused/
            hits = glob.glob(ARCHIVE + '**/' + os.path.basename(f), recursive=True)
            if hits:
                os.makedirs(JOB + '/downloads/reused', exist_ok=True)
                dst = JOB + '/downloads/reused/' + os.path.basename(f)
                if not os.path.exists(dst):
                    import shutil
                    shutil.copy2(hits[0], dst)
                f = 'downloads/reused/' + os.path.basename(f)
                files[k] = f
                p = dst
        if not os.path.exists(p):
            st = f'MISSING FILE {f}'
            hs.append('')
            continue
        h = sha(p)
        if recorded[k] and recorded[k] != h:
            st = f'SHA MISMATCH {f} recorded {recorded[k][:12]} file {h[:12]}'
        hs.append(h)
    check.append(dict(id=i, status=st if st != 'ok' else ('ok' if all(recorded) else 'ok (hash computed now)')))
    rec['file'] = '; '.join(files)
    rec['sha256'] = '; '.join(hs)
    out.append(rec)
with open(JOB + '/sources.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(out)
pd.DataFrame(check).to_csv(JOB + '/logs/sources_check.csv', index=False, lineterminator='\n')
bad = [c for c in check if not c['status'].startswith('ok')]
print('sources', len(out), 'used ids', len(used), 'problems', len(bad))
for b in bad:
    print(b)
