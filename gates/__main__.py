"""Entry point. `py -I gates --point ...` runs this folder in isolated mode (isolated mode leaves the working folder
off the import path, so `-I -m gates` cannot find the package); `py -m gates --point ...` works as well."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from gates.run import main
else:
    from .run import main

sys.exit(main())
