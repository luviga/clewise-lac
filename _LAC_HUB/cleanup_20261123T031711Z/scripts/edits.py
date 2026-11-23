"""Exact text replacement in a tracked file, keeping its line endings (CRLF or LF)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as M  # noqa: E402


def edit(rel, pairs):
    """pairs: (old, new, expected count). Stops if a count differs; writes nothing in that case."""
    p = M.ROOT / rel
    raw = p.read_bytes().decode('utf-8')
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    for old, new, n in pairs:
        got = s.count(old)
        if got != n:
            raise SystemExit(f'{rel}: expected {n} of {old!r}, found {got}')
        s = s.replace(old, new)
    if crlf:
        s = s.replace('\n', '\r\n')
    p.write_bytes(s.encode('utf-8'))
    print('edited', rel)
