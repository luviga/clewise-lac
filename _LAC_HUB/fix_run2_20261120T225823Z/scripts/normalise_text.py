"""FS2: normalise text files of the job folder for `git diff --check` (trailing blanks removed, no blank lines at the end,
LF endings). Skips downloads/ and backups/ (byte copies) and binary files. Logs the files changed."""
import os

JOB = 'C:/clw_fix/_LAC_HUB/fix_run2_20261120T225823Z'
EXT = {'.txt', '.log', '.csv', '.md', '.py', '.sh', '.json', '.jsonl', '.bat', '.html', '.rst'}
changed = []
for d, dirs, files in os.walk(JOB):
    rel = os.path.relpath(d, JOB).replace('\\', '/')
    if rel.split('/')[0] in ('downloads', 'backups'):
        continue
    for f in files:
        p = os.path.join(d, f)
        if os.path.splitext(f)[1].lower() not in EXT:
            continue
        raw = open(p, 'rb').read()
        try:
            t = raw.decode('utf-8')
        except UnicodeDecodeError:
            t = raw.decode('latin-1')
        lines = [l.rstrip() for l in t.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
        while lines and lines[-1] == '':
            lines.pop()
        new = ('\n'.join(lines) + '\n').encode('utf-8')
        if new != raw:
            open(p, 'wb').write(new)
            changed.append(os.path.relpath(p, JOB))
open(JOB + '/logs/normalise_text.log', 'w').write('\n'.join(changed) + '\n')
print(len(changed))
