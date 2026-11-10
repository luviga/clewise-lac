"""Last step: convert CRLF line endings (written by csv and pandas on Windows) to LF in the job folder's tracked file types,
so that git diff --check passes. The copied brief is left as it is."""
from pathlib import Path
HERE = Path(__file__).parent
n = 0
for f in HERE.glob("*"):
    if f.is_file() and f.suffix in (".csv", ".md", ".py", ".txt") and not f.name.startswith("BRIEF_"):
        b = f.read_bytes()
        c = b.replace(b"\r\n", b"\n")
        if c != b:
            f.write_bytes(c); n += 1
print(n, "files converted")
